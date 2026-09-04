"""slack handlers — channel membership, threading, reactions.

Invariants: you can only post to a channel you're a member of; messages persist
and thread replies carry their parent's `thread_ts`; reactions accumulate.
All entropy comes from ctx (deterministic ts ids and clock).
"""

from __future__ import annotations

from mockworld import Result


def list_channels(ctx, params) -> Result:
    return Result.ok({"ok": True, "channels": ctx.state.channels.all()})


def post_message(ctx, params) -> Result:
    if len(params["text"]) > 4000:
        return Result.error("msg_too_long")
    channel = ctx.state.channels.get(params["channel"])
    if channel is None:
        return Result.error("channel_not_found")
    if not channel["is_member"]:
        return Result.error("not_in_channel")

    ts = f"{ctx.now()}.000100"  # Slack-style monotonic timestamp id (virtual clock)
    message = {
        "ts": ts,
        "channel": channel["id"],
        "user": "U_AGENT",
        "text": params["text"],
        "thread_ts": params.get("thread_ts"),
        "reactions": {},
    }
    ctx.state.messages.put(ts, message)
    return Result.ok({"ok": True, "channel": channel["id"], "ts": ts, "message": message})


def get_channel_history(ctx, params) -> Result:
    channel = ctx.state.channels.get(params["channel"])
    if channel is None:
        return Result.error("channel_not_found")
    msgs = ctx.state.messages.filter(channel=channel["id"])
    msgs.sort(key=lambda m: m["ts"], reverse=True)  # newest first
    limit = params.get("limit", 20)
    return Result.ok({"ok": True, "messages": msgs[:limit], "has_more": len(msgs) > limit})


def add_reaction(ctx, params) -> Result:
    message = ctx.state.messages.get(params["timestamp"])
    if message is None or message["channel"] != params["channel"]:
        return Result.error("message_not_found")
    reactions = dict(message.get("reactions") or {})
    reactions[params["name"]] = reactions.get(params["name"], 0) + 1
    message["reactions"] = reactions
    ctx.state.messages.put(message["ts"], message)
    return Result.ok({"ok": True, "ts": message["ts"], "reactions": reactions})
