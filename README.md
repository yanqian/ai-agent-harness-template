# AI Agent Harness Template

A minimal repository template for controlled AI-agent development.

The harness is designed for Codex, Claude Code, Cursor Agent, and similar coding agents. It does not depend on a specific vendor. The control boundary is the repository state:

- `SPEC.md` records requirements.
- `feature_list.json` records executable feature state.
- `progress.md` records human-readable recovery status.
- `AGENTS.md` defines agent rules.
- `prompts/` contains role prompts.
- `scripts/` validates state and examples.

## Quick Start

Run:

```bash
./init.sh
scripts/validate-feature.sh F001
scripts/summarize-progress.sh
```

Expected result:

- required files are present;
- `feature_list.json` is valid;
- feature IDs are unique;
- status and `passes` fields are consistent;
- the tiny example tests pass.

## Development Flow

1. Add new requirements to `SPEC.md`.
2. Append new features to `feature_list.json`.
3. Implement one feature at a time.
4. Run `./init.sh`.
5. Run `scripts/validate-feature.sh Fxxx`.
6. Update `progress.md`.
7. Commit only after verification passes.

## Agent Prompt Files

- `prompts/plan.md` converts new requirements into spec and feature entries.
- `prompts/work.md` implements one selected feature.
- `prompts/continue.md` resumes from repository state.
- `prompts/evaluate.md` verifies one selected feature.

## Copying The Template

For a new project, copy the template files into the project root, then replace the tiny example with project-specific code and tests. Keep `./init.sh` as the single verification entry point.

## Tiny Example

The included example lives in `examples/tiny-cli/`. It exposes a small Python function and test suite so the harness can prove validation works without third-party dependencies.

