# fidelity — mock:twilio

**Fidelity level:** `partial` — Twilio-SMS-shaped, realistic enough to break agents,
not a full clone of the Twilio API.

## Models
- One account with a balance and a per-segment price (micro-USD, integer money).
- Messages with a `sid`, `num_segments`, `price`, and a status lifecycle.
- A sticky opt-out (STOP) list of numbers that can never be messaged.

## Invariants
- **Balance conservation:** each send debits `segments × price`; a send that would
  overdraw is rejected (`insufficient_balance`) and the balance is untouched.
- **Status lifecycle:** a message is `queued` on send and advances to `delivered`
  when its status is fetched (the delivery callback).
- **Sticky opt-out:** seeded opted-out numbers always return `blocked` (21610).

## Faults / errors
- `invalid_number` (21211) for non-E.164 `to`.
- `blocked` (21610) for opted-out recipients.
- `insufficient_balance` (20003) when the balance can't cover the segments.
- `rate_limited` (429), elevated under `hostile`.

## Does NOT model
- MMS/media, messaging services/pools, number provisioning, or webhooks.
- Carrier-specific segment encoding (uses a flat 160-char GSM segment).
- Real pricing by destination country (flat per-segment price).
