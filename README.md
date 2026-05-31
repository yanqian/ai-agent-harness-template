# AI Agent Harness Template

A minimal repository template for controlled AI-agent development.

The harness is designed for Codex, Claude Code, Cursor Agent, and similar coding agents. It does not depend on a specific vendor. The control boundary is the repository state:

- `SPEC.md` records requirements.
- `feature_list.json` records executable feature state.
- `progress.md` records human-readable recovery status.
- `AGENTS.md` defines agent rules.
- `prompts/` contains role prompts.
- `scripts/` validates state and examples.
- `test/` contains unit, contract, and smoke tests.
- `orchestrator.py` previews or runs one-feature coding/evaluation loops.

## Quick Start

Run:

```bash
./init.sh
scripts/validate-feature.sh F001
scripts/summarize-progress.sh
python3 orchestrator.py --dry-run
```

Expected result:

- required files are present;
- `feature_list.json` is valid;
- feature IDs are unique;
- status and `passes` fields are consistent;
- the tiny example tests pass.
- the orchestrator can run the startup protocol and preview prompts.
- the unit, contract, and smoke layers pass.

## Development Flow

1. Add new requirements to `SPEC.md`.
2. Append new features to `feature_list.json`.
3. Implement one feature at a time.
4. Run `./init.sh`.
5. Run `scripts/validate-feature.sh Fxxx`.
6. Update `progress.md`.
7. Commit only after verification passes.

## Orchestrator

Preview the next one-feature round:

```bash
python3 orchestrator.py --dry-run
```

Run evaluator prompt preview only:

```bash
python3 orchestrator.py --eval-only F001 --dry-run
```

The template does not assume a specific AI coding tool. To execute a real agent instead of previewing prompts, set `HARNESS_AGENT_COMMAND` to a command that accepts the prompt as its final argv.

Examples:

```bash
HARNESS_AGENT_COMMAND="codex exec" python3 orchestrator.py --max-rounds 1
HARNESS_AGENT_COMMAND="claude" python3 orchestrator.py --max-rounds 1
```

## Agent Prompt Files

- `prompts/plan.md` converts new requirements into spec and feature entries.
- `prompts/work.md` implements one selected feature.
- `prompts/continue.md` resumes from repository state.
- `prompts/evaluate.md` verifies one selected feature.

## Test Layers

- `test/unit/` covers deterministic helper behavior.
- `test/contract/` locks repository rules, schema, prompts, and orchestrator contracts.
- `test/harness/` is optional and intended for downstream workflow tests.
- `test/smoke/` runs the main verification commands end to end.

All default layers are run by:

```bash
./init.sh
```

## Copying The Template

For a new project, copy the template files into the project root, then replace the tiny example with project-specific code and tests. Keep `./init.sh` as the single verification entry point.

## Tiny Example

The included example lives in `examples/tiny-cli/`. It exposes a small Python function and test suite so the harness can prove validation works without third-party dependencies.
