# AI Agent Harness Template

[![CI](https://github.com/yanqian/ai-agent-harness-template/actions/workflows/ci.yml/badge.svg)](https://github.com/yanqian/ai-agent-harness-template/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Make AI coding projects resumable.

AI agents are powerful, but long-running coding work breaks when:

- the session is interrupted;
- context becomes too long;
- the weekly quota is exhausted;
- tomorrow's agent forgets yesterday's decisions;
- the agent changes unrelated files;
- the agent marks work done too early.

This is not a prompt collection. It is a repository-state protocol for making AI coding work resumable, auditable, and evaluator-gated.

This template keeps durable project state inside the repository:

- `SPEC.md` for requirements
- `feature_list.json` for executable feature state
- `progress.md` for recovery notes
- `AGENTS.md` for agent rules
- `QUALITY.md` for evaluator criteria
- `runs/` for evidence and handoff records

It is designed for Codex, Claude Code, Cursor Agent, and similar coding agents without binding the harness to one vendor.

The repository also includes a distributable [AI Agent Harness skill](skills/ai-agent-harness/SKILL.md). The skill is a convenience layer for initialization and day-to-day harness use: install or repair the harness, plan requirements, work one feature, evaluate completion, and commit approved progress. It does not replace repository state; `AGENTS.md`, `SPEC.md`, `feature_list.json`, `progress.md`, `docs/`, `QUALITY.md`, `runs/`, and git history remain the source of truth.

## Announcement

Read the project announcement: [I Built a Small Harness to Stop AI Coding Projects From Forgetting State](https://yanqian.github.io/posts/publish/i-built-a-small-harness-to-stop-ai-coding-projects-from-forgetting-state/).

## Sources

This template is informed by:

- OpenAI, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
- Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- Geoff Huntley, [everything is a ralph loop](https://ghuntley.com/loop/)

## Why This Exists

AI coding breaks down less because models cannot write code, and more because long-running work loses project state.

This harness keeps the durable state in files that agents, humans, and CI can all inspect. The template dogfoods its own state model: every change is tracked as a feature with acceptance criteria, validation status, attempts, and recovery notes.

The workflow was extracted from real agent projects such as [home-guard-tg](https://github.com/yanqian/home-guard-tg) and [agent-remote-tg](https://github.com/yanqian/agent-remote-tg). See [docs/real-world-usage.md](docs/real-world-usage.md).

## Control Boundary

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

### Use This Template

1. Copy this template into your project root.
2. Run `make clean` to reset template state.
3. Replace `SPEC.md` with your project goal.
4. Add your first feature to `feature_list.json`.
5. Run `make init`.
6. Ask Codex, Claude Code, Cursor Agent, or another coding agent to follow `AGENTS.md`.
7. Validate one feature with `make validate FEATURE=F001`.

### Use The Skill

The skill lives in `skills/ai-agent-harness/` and is designed to remain vendor-neutral even when loaded by Codex as `SKILL.md`.

Initialize or inspect a project:

```bash
python3 skills/ai-agent-harness/scripts/init_harness.py --root /path/to/project --mode adopt
python3 skills/ai-agent-harness/scripts/init_harness.py --root /path/to/project --mode check
```

The initializer supports `new`, `adopt`, `repair`, and `check` modes. It does not overwrite conflicting files unless `--force` is used after explicit approval.

The skill also defines a finalize-and-commit workflow. It stages and commits only after the user explicitly says they are satisfied or asks to commit.

### Verify This Repository

Run the same command used by CI:

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
- `make clean` resets project-specific state after copying the template.
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

The orchestrator is intentionally boring: it does not make agents smarter. It only selects one feature, enforces the startup protocol, dispatches role prompts, and records state transitions.

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
