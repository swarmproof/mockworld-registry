"""Deterministic base dataset for mock:twilio.

Seeds one account with a balance, some prior messages, and a few sticky opt-outs
so blocked-recipient behavior is demonstrable out of the box.
"""

from __future__ import annotations

_OPT_OUTS = ["+14155550001", "+14155550002", "+442071230003"]


def generate(ctx, definition) -> dict:
    account = {
        "AC_default": {
            "id": "AC_default",
            "balance_micro_usd": 5_000_000,        # $5.00
            "price_per_segment_micro_usd": 7_900,  # ≈ $0.0079 / segment
        }
    }

    messages: dict[str, dict] = {}
    for i in range(definition.seed.volume.get("messages", 0)):
        sid = ctx.ids.next("SM")
        messages[sid] = {
            "sid": sid,
            "to": f"+1415555{ctx.rng.randint(1000, 9999)}",
            "from": "+14155550100",
            "body": ctx.fake.sentence(),
            "status": ctx.rng.choice(["delivered", "delivered", "delivered", "sent", "failed"]),
            "num_segments": 1,
            "price_micro_usd": 7_900,
            "error_code": None,
            "created": 1_700_000_000 + i,
        }

    opt_outs = {n: {"number": n} for n in _OPT_OUTS}
    return {"account": account, "messages": messages, "opt_outs": opt_outs}
