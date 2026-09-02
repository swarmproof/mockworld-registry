# Contributing a mock

1. **Author it** (needs `pip install mockworld-mcp`):
   ```bash
   mockworld new mymock          # scaffolds ./mymock (lints clean, runs)
   # edit mock.yaml + handlers.py to model your service; declare faults
   mockworld validate ./mymock   # must be clean
   ```

2. **Add it to this repo** under `mocks/mymock/` (the four files: `mock.yaml`,
   optional `handlers.py`/`seed.py`, and `fidelity.md`).

3. **Get your index entry**:
   ```bash
   mockworld pack ./mymock
   ```
   Copy the printed JSON into `registry.json`'s `mocks` array, and set:
   ```json
   "source": "github:swarmproof/mockworld-registry@main/mocks/mymock"
   ```

4. **Open a PR.** CI validates the mock and re-verifies the checksum.

## Rules
- **Determinism is required.** No `time`/`random`/`uuid` in handlers — draw all
  entropy from `ctx` (the validator enforces this).
- **No network/filesystem/subprocess** in handler code — the safety gate refuses it.
- Ship a `fidelity.md` documenting what your mock does and does *not* model.
- Business-logic faults only (declines, 429s, latency…); transport chaos is out of scope.
