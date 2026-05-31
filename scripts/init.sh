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
  test_plan.md \
  README.md \
  QUALITY.md \
  orchestrator.py \
  docs/README.md \
  docs/architecture.md \
  docs/testing.md \
  docs/external-behavior.md \
  docs/agent-workflow.md \
  docs/decisions/README.md \
  runs/RUN_TEMPLATE.md \
  schemas/feature_list.schema.json \
  prompts/plan.md \
  prompts/work.md \
  prompts/continue.md \
  prompts/evaluate.md \
  scripts/validate-state.py \
  scripts/validate-feature.sh \
  scripts/summarize-progress.sh \
  scripts/summarize-runs.sh \
  scripts/run-coding-agent.sh \
  scripts/run-evaluator-agent.sh
do
  test -f "$path"
done

echo "== Harness state =="
python3 scripts/validate-state.py

echo "== Orchestrator syntax =="
python3 - <<'PY'
from pathlib import Path

compile(Path("orchestrator.py").read_text(), "orchestrator.py", "exec")
PY

echo "== Tiny example =="
python3 - <<'PY'
from pathlib import Path

for path in [Path("examples/tiny-cli/tiny_cli.py"), Path("examples/tiny-cli/test_tiny_cli.py")]:
    compile(path.read_text(), str(path), "exec")
PY
python3 examples/tiny-cli/test_tiny_cli.py

if [[ "${HARNESS_SKIP_TEST_LAYERS:-}" == "1" ]]; then
  echo "skip layered tests: HARNESS_SKIP_TEST_LAYERS=1"
  echo "init verification passed"
  exit 0
fi

run_unittest_layer() {
  local name="$1"
  local path="$2"
  if [[ -d "$path" ]]; then
    echo "== ${name} tests =="
    python3 -m unittest discover -s "$path" -p 'test_*.py'
  else
    echo "skip ${name} tests: ${path} not present"
  fi
}

run_unittest_layer "Unit" "test/unit"
run_unittest_layer "Contract" "test/contract"
run_unittest_layer "Harness" "test/harness"
run_unittest_layer "Smoke" "test/smoke"

echo "init verification passed"
