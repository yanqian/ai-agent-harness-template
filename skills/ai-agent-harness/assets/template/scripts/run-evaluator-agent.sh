#!/usr/bin/env bash
set -euo pipefail

cat >/dev/null
cat >&2 <<'MSG'
scripts/run-evaluator-agent.sh is a template adapter.

The default work entrypoint is orchestrator-first, but this adapter is not configured.
Replace this file with the project-specific Evaluator Agent invocation before running `make work`.
The orchestrator sends the full Evaluator Agent prompt on stdin.
The evaluator output must contain exactly one EVAL_PASS or EVAL_FAIL line.

If you use the documented manual fallback, record that it was a fallback and do not bypass
evaluator gating, evaluator evidence, or final ./init.sh verification.

Examples:
  codex exec "$(cat)"
  claude "$(cat)"
MSG
exit 2
