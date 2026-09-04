"""Deterministic base dataset for mock:slack."""

from __future__ import annotations

_CHANNEL_NAMES = ["general", "random", "engineering", "design", "support",
                  "sales", "incidents", "watercooler"]


def generate(ctx, definition) -> dict:
    channels: dict[str, dict] = {}
    for i in range(definition.seed.volume.get("channels", 0)):
        cid = ctx.ids.next("C")
        name = _CHANNEL_NAMES[i % len(_CHANNEL_NAMES)]
        channels[cid] = {
            "id": cid,
            "name": name,
            "is_member": ctx.rng.random() < 0.7,   # member of ~70% of channels
            "is_private": ctx.rng.random() < 0.2,
        }

    channel_ids = list(channels)
    messages: dict[str, dict] = {}
    for i in range(definition.seed.volume.get("messages", 0)):
        ts = f"{1_700_000_000 + i}.000{i:03d}"
        messages[ts] = {
            "ts": ts,
            "channel": ctx.rng.choice(channel_ids) if channel_ids else "C000",
            "user": f"U{ctx.rng.randint(100, 999)}",
            "text": ctx.fake.sentence(),
            "thread_ts": None,
            "reactions": {},
        }
    return {"channels": channels, "messages": messages}
