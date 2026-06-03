#!/usr/bin/env bash
set -euo pipefail

cat >/dev/null
cat >&2 <<'MSG'
scripts/run-evaluator-agent.sh is a template adapter.

Replace this file with the project-specific Evaluator Agent invocation.
The orchestrator sends the full Evaluator Agent prompt on stdin.
The evaluator output must contain exactly one EVAL_PASS or EVAL_FAIL line.

Examples:
  codex exec "$(cat)"
  claude "$(cat)"
MSG
exit 2

