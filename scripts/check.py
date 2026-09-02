"""Validate every registry entry: the mock lints clean and its checksum matches.

Run in CI on every PR. Requires `pip install mockworld-mcp`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from mockworld.registry import dir_checksum
from mockworld.validate import validate_mock

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    index = json.loads((ROOT / "registry.json").read_text())
    entries = index["mocks"] if isinstance(index, dict) else index
    failures: list[str] = []

    for entry in entries:
        name, source = entry["name"], entry["source"]
        # source: github:owner/repo@ref/<subdir> — the subdir is a path in THIS repo.
        subdir = source.split("@", 1)[1].split("/", 1)[1] if "@" in source else source
        mock_dir = ROOT / subdir
        if not (mock_dir / "mock.yaml").exists():
            failures.append(f"{name}: no mock.yaml at {subdir}")
            continue

        errors = [f.message for f in validate_mock(str(mock_dir)) if f.level == "error"]
        if errors:
            failures.append(f"{name}: validation errors {errors}")

        actual = dir_checksum(mock_dir)
        if entry.get("sha256") != actual:
            failures.append(f"{name}: checksum mismatch (entry {entry.get('sha256', '')[:12]}…, "
                            f"actual {actual[:12]}…)")

    if failures:
        print("REGISTRY CHECK FAILED:")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(f"✓ {len(entries)} mock(s) valid and checksum-matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
