# Progress

## Current System Status

The minimal AI agent harness template is runnable.

Implemented components:

- Durable agent rules in `AGENTS.md`.
- Practiced AGENTS guardrails for state safety, external behavior verification, tool schema handling, and anti-pattern prevention.
- Requirements in `SPEC.md`.
- Feature state in `feature_list.json`.
- Feature schema in `schemas/feature_list.schema.json`.
- Prompt templates in `prompts/`.
- Validation scripts in `scripts/`.
- Layered test coverage under `test/unit`, `test/contract`, and `test/smoke`.
- Contract tests that lock AI agent obligations and harness boundaries.
- Verification planning in `test_plan.md`.
- Root verification wrapper at `./init.sh`.
- Vendor-neutral lightweight orchestrator in `orchestrator.py`.
- Explicit Coding Agent and Evaluator Agent adapters under `scripts/`.
- Tiny dependency-free Python CLI example in `examples/tiny-cli/`.

## Last Completed Feature

`F006` - Replace generic agent command with role adapters.

## Next Feature

No unfinished feature remains in the template.

## Known Issues

- The template orchestrator is intentionally lightweight and vendor-neutral.
- Vendor-specific command wrappers for Codex, Claude Code, and Cursor Agent are intentionally left to downstream projects.
