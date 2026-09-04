"""twilio handlers — segment billing, balance conservation, delivery lifecycle.

Invariants: balance is debited by (segments × price) and never goes negative;
a message moves queued → delivered; opted-out numbers stay blocked (sticky).
"""

from __future__ import annotations

from mockworld import Result

_ACCOUNT_ID = "AC_default"


def _valid_e164(number: str) -> bool:
    return number.startswith("+") and number[1:].isdigit() and 8 <= len(number) <= 16


def _segments(body: str) -> int:
    return max(1, (len(body) + 159) // 160)


def send_sms(ctx, params) -> Result:
    to, body = params["to"], params["body"]
    if not _valid_e164(to):
        return Result.error("invalid_number")
    if ctx.state.opt_outs.exists(to):
        return Result.error("blocked")

    account = ctx.state.account.get(_ACCOUNT_ID)
    segments = _segments(body)
    cost = segments * account["price_per_segment_micro_usd"]
    if account["balance_micro_usd"] < cost:
        return Result.error("insufficient_balance")

    account["balance_micro_usd"] -= cost  # conservation: never below zero (guarded above)
    ctx.state.account.put(account["id"], account)

    message = {
        "sid": ctx.ids.next("SM"),
        "to": to,
        "from": params["from"],
        "body": body,
        "status": "queued",
        "num_segments": segments,
        "price_micro_usd": cost,
        "error_code": None,
        "created": ctx.now(),
    }
    ctx.state.messages.put(message["sid"], message)
    return Result.ok(message)


def get_message_status(ctx, params) -> Result:
    message = ctx.state.messages.get(params["sid"])
    if message is None:
        return Result.error("message_not_found")
    if message["status"] == "queued":  # the delivery callback advances the lifecycle
        message["status"] = "delivered"
        ctx.state.messages.put(message["sid"], message)
    return Result.ok(message)


def list_messages(ctx, params) -> Result:
    msgs = ctx.state.messages.all()
    msgs.sort(key=lambda m: m["created"], reverse=True)
    return Result.ok({"messages": msgs, "count": len(msgs)})


def get_balance(ctx, params) -> Result:
    account = ctx.state.account.get(_ACCOUNT_ID)
    return Result.ok({"balance_micro_usd": account["balance_micro_usd"]})
