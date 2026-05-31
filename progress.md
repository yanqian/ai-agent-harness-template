# Progress

## Current System Status

The minimal AI agent harness template is runnable.

Implemented components:

- Durable agent rules in `AGENTS.md`.
- Requirements in `SPEC.md`.
- Feature state in `feature_list.json`.
- Feature schema in `schemas/feature_list.schema.json`.
- Prompt templates in `prompts/`.
- Validation scripts in `scripts/`.
- Root verification wrapper at `./init.sh`.
- Vendor-neutral lightweight orchestrator in `orchestrator.py`.
- Tiny dependency-free Python CLI example in `examples/tiny-cli/`.

## Last Completed Feature

`F002` - Add vendor-neutral lightweight orchestrator.

## Next Feature

No unfinished feature remains in the template.

## Known Issues

- This template intentionally does not include a full orchestrator.
- Vendor-specific command wrappers for Codex, Claude Code, and Cursor Agent are intentionally left to downstream projects.
