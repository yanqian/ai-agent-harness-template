#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = ROOT / "feature_list.json"
SCHEMA_PATH = ROOT / "schemas" / "feature_list.schema.json"
VALID_STATUSES = {"todo", "in_progress", "done", "blocked"}
FEATURE_ID_RE = re.compile(r"^F[0-9]{3,}$")


def fail(message: str) -> None:
    print(f"state validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is invalid JSON: {exc}")


def require_string(feature: dict, key: str) -> str:
    value = feature.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"feature {feature.get('id', '<unknown>')} must have non-empty string {key}")
    return value


def main() -> int:
    if not SCHEMA_PATH.exists():
        fail("schemas/feature_list.schema.json is missing")

    data = load_json(FEATURES_PATH)
    if not isinstance(data, dict):
        fail("feature_list.json must be a JSON object")
    features = data.get("features")
    if not isinstance(features, list):
        fail("feature_list.json must contain a features array")

    seen_ids = set()
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            fail(f"feature at index {index} must be an object")
        feature_id = require_string(feature, "id")
        if not FEATURE_ID_RE.match(feature_id):
            fail(f"feature id must match F###: {feature_id}")
        if feature_id in seen_ids:
            fail(f"duplicate feature id: {feature_id}")
        seen_ids.add(feature_id)

        require_string(feature, "title")
        require_string(feature, "description")
        acceptance = feature.get("acceptance")
        if not isinstance(acceptance, list) or not acceptance or not all(isinstance(item, str) and item.strip() for item in acceptance):
            fail(f"feature {feature_id} must have non-empty acceptance strings")
        if not isinstance(feature.get("passes"), bool):
            fail(f"feature {feature_id} must have boolean passes")
        status = feature.get("status")
        if status not in VALID_STATUSES:
            fail(f"feature {feature_id} has invalid status: {status}")
        attempts = feature.get("attempts")
        if not isinstance(attempts, int) or attempts < 0:
            fail(f"feature {feature_id} must have non-negative integer attempts")
        if not isinstance(feature.get("last_error"), str):
            fail(f"feature {feature_id} must have string last_error")
        if feature["passes"] is True and status != "done":
            fail(f"feature {feature_id} has passes=true but status is not done")
        if status == "done" and feature["passes"] is not True:
            fail(f"feature {feature_id} has status=done but passes is not true")

    print(f"validated {len(features)} features")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

