#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== Required files =="
for path in \
  AGENTS.md \
  SPEC.md \
  feature_list.json \
  progress.md \
  README.md \
  schemas/feature_list.schema.json \
  prompts/plan.md \
  prompts/work.md \
  prompts/continue.md \
  prompts/evaluate.md \
  scripts/validate-state.py \
  scripts/validate-feature.sh \
  scripts/summarize-progress.sh
do
  test -f "$path"
done

echo "== Harness state =="
python3 scripts/validate-state.py

echo "== Tiny example =="
python3 - <<'PY'
from pathlib import Path

for path in [Path("examples/tiny-cli/tiny_cli.py"), Path("examples/tiny-cli/test_tiny_cli.py")]:
    compile(path.read_text(), str(path), "exec")
PY
python3 examples/tiny-cli/test_tiny_cli.py

echo "init verification passed"
