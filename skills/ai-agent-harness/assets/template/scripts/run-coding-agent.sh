#!/usr/bin/env bash
set -euo pipefail

cat >/dev/null
cat >&2 <<'MSG'
scripts/run-coding-agent.sh is a template adapter.

Replace this file with the project-specific Coding Agent invocation.
The orchestrator sends the full Coding Agent prompt on stdin.

Examples:
  codex exec "$(cat)"
  claude "$(cat)"
MSG
exit 2

