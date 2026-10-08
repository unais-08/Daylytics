"""Compare the captured OpenAPI schema with the current application schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalize(item)
            for key, item in sorted(value.items())
            if key != "operationId"
        }
    if isinstance(value, list):
        return sorted((normalize(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True))
    return value


def main() -> int:
    baseline_path = Path(__file__).resolve().parents[1] / "docs" / "openapi.before.json"
    if not baseline_path.exists():
        print(f"Missing baseline: {baseline_path}", file=sys.stderr)
        return 2
    before = json.loads(baseline_path.read_text(encoding="utf-8"))
    after = app.openapi()
    if normalize(before) == normalize(after):
        print("OpenAPI schemas match after normalization.")
        return 0
    print("OpenAPI schemas differ.")
    print(json.dumps({"before": normalize(before), "after": normalize(after)}, indent=2, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
