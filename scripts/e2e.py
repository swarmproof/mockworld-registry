"""E2E scenario checks for registry mocks — guards behavior, not just schema.

Run in CI after scripts/check.py. Each mock's load-bearing invariants are
exercised through the engine; any failure exits non-zero. Requires
`pip install mockworld-mcp`.
"""

from __future__ import annotations

import sys
from pathlib import Path

from mockworld import Engine

ROOT = Path(__file__).resolve().parents[1]


def _eng(name: str) -> Engine:
    # Local path → trusted, so the scenario runs in-process (fast, CI-friendly).
    return Engine.from_source(str(ROOT / "mocks" / name), seed=7, faults="none")


def check_slack() -> list[str]:
    fails: list[str] = []
    e = _eng("slack")
    chans = e.call("list_channels", {}).data["channels"]
    member = next(c for c in chans if c["is_member"])
    nonmember = next(c for c in chans if not c["is_member"])

    if not e.call("post_message", {"channel": member["id"], "text": "hi"}).success:
        fails.append("slack: post to a member channel should succeed")
    if e.call("post_message", {"channel": nonmember["id"], "text": "x"}).err.body["error"] != "not_in_channel":
        fails.append("slack: posting to a non-member channel must return not_in_channel")
    if e.call("post_message", {"channel": "C_MISSING", "text": "x"}).err.body["error"] != "channel_not_found":
        fails.append("slack: posting to a missing channel must return channel_not_found")
    if e.call("post_message", {"channel": member["id"], "text": "a" * 4001}).err.body["error"] != "msg_too_long":
        fails.append("slack: text over 4000 chars must return msg_too_long")

    parent = e.call("post_message", {"channel": member["id"], "text": "root"}).data
    reply = e.call("post_message", {"channel": member["id"], "text": "re", "thread_ts": parent["ts"]}).data
    if reply["message"]["thread_ts"] != parent["ts"]:
        fails.append("slack: a threaded reply must carry the parent thread_ts")

    e.call("add_reaction", {"channel": member["id"], "timestamp": reply["ts"], "name": "thumbsup"})
    hist = e.call("get_channel_history", {"channel": member["id"]}).data["messages"]
    if not hist or hist[0]["ts"] < parent["ts"]:
        fails.append("slack: history must be newest-first")
    reacted = next((m for m in hist if m["ts"] == reply["ts"]), None)
    if not reacted or reacted["reactions"].get("thumbsup") != 1:
        fails.append("slack: reactions must accumulate on the message")
    return fails


def check_twilio() -> list[str]:
    fails: list[str] = []
    e = _eng("twilio")
    bal0 = e.call("get_balance", {}).data["balance_micro_usd"]
    msg = e.call("send_sms", {"to": "+14155559999", "from": "+14155550100", "body": "a" * 200}).data  # 2 segments
    if msg["num_segments"] != 2:
        fails.append("twilio: a 200-char body must be 2 segments")
    bal1 = e.call("get_balance", {}).data["balance_micro_usd"]
    if bal0 - bal1 != msg["price_micro_usd"]:
        fails.append("twilio: balance must be debited by exactly the message price (conservation)")
    if e.call("get_message_status", {"sid": msg["sid"]}).data["status"] != "delivered":
        fails.append("twilio: a queued message must advance to delivered on status fetch")
    if e.call("send_sms", {"to": "5551234", "from": "+1", "body": "x"}).err.body["code"] != 21211:
        fails.append("twilio: a non-E.164 number must return 21211 invalid_number")
    if e.call("send_sms", {"to": "+14155550001", "from": "+1", "body": "x"}).err.body["code"] != 21610:
        fails.append("twilio: a seeded opted-out number must return 21610 blocked")

    for _ in range(800):  # drain the balance
        e.call("send_sms", {"to": "+14155559999", "from": "+1", "body": "x"})
    if e.call("send_sms", {"to": "+14155559999", "from": "+1", "body": "x"}).err.body["code"] != 20003:
        fails.append("twilio: an overdrawing send must return 20003 insufficient_balance")
    if e.call("get_balance", {}).data["balance_micro_usd"] < 0:
        fails.append("twilio: balance must never go negative")
    return fails


def main() -> int:
    fails: list[str] = []
    for name, fn in [("slack", check_slack), ("twilio", check_twilio)]:
        result = fn()
        fails += result
        print(f"  {'✗' if result else '✓'} {name}: {len(result)} failure(s)")
    if fails:
        print("\nE2E FAILURES:")
        for f in fails:
            print(f"  ✗ {f}")
        return 1
    print("✓ all registry-mock E2E scenarios passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
