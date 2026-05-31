# AI Agent Harness Template

A minimal repository template for controlled AI-agent development.

## Sources

This template is informed by:

- OpenAI, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
- Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- Geoff Huntley, [everything is a ralph loop](https://ghuntley.com/loop/)

The harness is designed for Codex, Claude Code, Cursor Agent, and similar coding agents. It does not depend on a specific vendor. The control boundary is the repository state:

- `SPEC.md` records requirements.
- `feature_list.json` records executable feature state.
- `progress.md` records human-readable recovery status.
- `AGENTS.md` defines agent rules.
- `docs/` stores durable repository knowledge.
- `QUALITY.md` defines the evaluator rubric.
- `runs/` stores run evidence and handoff records.
- `docs/failure-domains.md` and `scripts/check-failure-domains.sh` turn failures into harness improvement pressure.
- `prompts/` contains role prompts.
- `scripts/` validates state and examples.
- `test/` contains unit, contract, and smoke tests.
- `orchestrator.py` previews or runs one-feature coding/evaluation loops.

## Quick Start

Run:

```bash
make ci
```

Expected result:

- required files are present;
- `feature_list.json` is valid;
- feature IDs are unique;
- status and `passes` fields are consistent;
- the tiny example tests pass.
- the Go server example tests pass when Go is installed.
- the orchestrator can run the startup protocol and preview prompts.
- the unit, contract, and smoke layers pass.

## Development Flow

1. Add new requirements to `SPEC.md`.
2. Append new features to `feature_list.json`.
3. Implement one feature at a time.
4. Run `make init`.
5. Run `make validate FEATURE=Fxxx`.
6. Update `progress.md`.
7. Commit only after verification passes.

## Make Targets

- `make init` runs `./init.sh`.
- `make validate FEATURE=Fxxx` validates one feature.
- `make unit`, `make contract`, and `make smoke` run individual test layers.
- `make go-example` runs the Go server example tests.
- `make dry-run` previews the next orchestrator round.
- `make summarize` prints progress and run summaries.
- `make ci` runs the same commands used by GitHub Actions.

## Orchestrator

Preview the next one-feature round:

```bash
python3 orchestrator.py --dry-run
```

Run evaluator prompt preview only:

```bash
python3 orchestrator.py --eval-only F001 --dry-run
```

The template does not assume a specific AI coding tool. To execute a real agent instead of previewing prompts, replace `scripts/run-coding-agent.sh` and `scripts/run-evaluator-agent.sh` with project-specific adapters. The orchestrator sends the selected role prompt to the adapter on stdin. Orchestrator dry-run and `scripts/validate-feature.sh` are manual checks outside `./init.sh` because they run `./init.sh` as part of their own protocol.

Adapter examples:

```bash
codex exec "$(cat)"
claude "$(cat)"
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
make init
```

## Knowledge, Quality, And Runs

Keep `AGENTS.md` short enough to be a map. Put durable detail in `docs/`.

Use `QUALITY.md` when evaluating features. It defines correctness, completeness, maintainability, test coverage, recoverability, and safety criteria.

Use `runs/RUN_TEMPLATE.md` for non-trivial work, failures, external behavior verification, and evaluator handoff.

Failed or blocked run records must include a failure domain and harness improvement assessment. Check that with:

```bash
scripts/check-failure-domains.sh
```

Summarize run records with:

```bash
scripts/summarize-runs.sh
```

## Copying The Template

For a new project, copy the template files into the project root, then replace the tiny example with project-specific code and tests. Keep `./init.sh` as the single verification entry point.

## Tiny Example

The included example lives in `examples/tiny-cli/`. It exposes a small Python function and test suite so the harness can prove validation works without third-party dependencies.

## Go Server Example

The included Go service example lives in `examples/go-server/`. It is a dependency-free HTTP server with:

- `GET /healthz`
- `GET /greet?name=Codex`

Run it with:

```bash
cd examples/go-server
go test ./...
PORT=8080 go run .
```
