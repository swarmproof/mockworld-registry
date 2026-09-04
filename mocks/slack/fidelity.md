# fidelity — mock:slack

**Fidelity level:** `partial` — Slack-shaped, realistic enough to break agents, not
a full clone of the Slack Web API.

## Models
- Channels with membership (`is_member`) and privacy flags.
- Messages with `ts` ids, threading (`thread_ts`), and accumulating `reactions`.
- Slack's response envelope: success is `{ok: true, ...}`; errors are
  `{ok: false, error: "channel_not_found"}` etc.

## Invariants
- You can only `post_message` to a channel you are a member of (`not_in_channel`).
- Messages persist and are returned newest-first by `get_channel_history`.
- Reactions accumulate per emoji name.

## Faults
- `channel_not_found` / `not_in_channel` / `message_not_found` (stateful).
- `msg_too_long` when `text` exceeds 4000 characters (conditional).
- `rate_limited` (429 + `Retry-After`), elevated under the `hostile` profile.

## Does NOT model
- Blocks/attachments, Block Kit, slash commands, users/presence, or scopes/OAuth.
- Pagination cursors (uses a simple `limit`).
- Edits/deletes, pins, or per-user reaction identity (reactions are counts).
