# AI Agent Harness Template SPEC

## 1. Goal

Provide a minimal, copyable repository harness for controlled AI-assisted development with Codex, Claude Code, Cursor Agent, or similar coding agents.

The harness makes project state recoverable by storing requirements, feature state, progress, prompts, and validation scripts in files.

## 2. Scope

### Included

- Durable project instructions in `AGENTS.md`.
- Durable repository knowledge in `docs/`.
- Evaluator quality criteria in `QUALITY.md`.
- Per-run evidence and handoff records in `runs/`.
- Failure-domain classification and harness improvement checks.
- Proven agent guardrails for state safety, external behavior verification, and anti-patterns in `AGENTS.md`.
- Human-readable requirements in `SPEC.md`.
- Machine-readable feature state in `feature_list.json`.
- Human-readable recovery state in `progress.md`.
- A JSON Schema for feature state.
- Prompt templates for planning, work, continuation, and evaluation.
- Deterministic validation scripts.
- A clean-state command for resetting template project state after copying.
- A `Makefile` with common local and CI verification targets.
- A GitHub Actions workflow that runs harness verification on push and pull request.
- Public-facing README positioning for resumable AI coding projects.
- OSS readiness files for licensing, contribution, security reporting, changelog, and issue triage.
- A test plan and dependency-free unit, contract, and smoke tests.
- Contract tests for AI agent obligations and harness boundaries.
- A vendor-neutral lightweight `orchestrator.py`.
- A tiny runnable example proving the harness loop works.
- A dependency-free Go server example for service-style projects.

### Excluded

- Vendor-specific automation for Codex, Claude Code, Cursor, or other tools.
- Cloud deployment.
- CI provider configuration.
- Automatic commits.
- Vendor-specific orchestration adapters.

## 3. Core Concepts

### Spec First

New work is first written into `SPEC.md` so agents share a stable requirement source.

### Repository Knowledge Map

`AGENTS.md` acts as an entry point. Durable knowledge belongs in `docs/`, quality criteria belong in `QUALITY.md`, and run evidence belongs in `runs/`.

### Failure Improvement Loop

Failures are classified by domain and assessed for harness improvement. Failed or blocked run records must state the failure domain and whether the harness should be improved through docs, prompts, scripts, schemas, tests, or a follow-up feature.

The orchestrator writes a failed run record when unattended coding or evaluation fails. Unknown failure-domain fields intentionally fail validation until the failure is classified and the harness improvement assessment is recorded.

### Feature Tracked

Every executable unit of work is represented in `feature_list.json` with explicit state and acceptance criteria.

### Evaluator Gated

A feature is complete only when validation passes and an evaluator can justify the result against the acceptance criteria.

### Orchestrated When Needed

`orchestrator.py` can preview or run the coding/evaluation loop for one unfinished feature at a time. It is intentionally vendor-neutral: `--dry-run` prints prompts, while `scripts/run-coding-agent.sh` and `scripts/run-evaluator-agent.sh` are the explicit role adapters downstream projects replace to connect Codex, Claude Code, Cursor Agent, or another tool.

### Recoverable

Any session can resume by reading repository files and git history. Chat history is not required.

### Verified External Assumptions

When implementation relies on behavior outside repository code, agents verify that behavior through primary sources, real commands, official documentation, captured logs, or real-shaped fixtures before depending on it.

### Layered Verification

The template keeps automated checks in explicit layers:

- Unit tests cover small deterministic helper behavior.
- Contract tests lock repository rules, schema shape, prompt requirements, and orchestrator command guarantees.
- Harness tests are reserved for project-level workflow behavior and are optional in the minimal template.
- Smoke tests run the template's main user-facing verification commands end to end.

## 4. Acceptance Criteria

- `./init.sh` validates harness state and runs the tiny example tests.
- `scripts/validate-feature.sh F001` validates a feature by ID and runs the default verification entry point.
- `scripts/summarize-progress.sh` prints a concise status summary.
- Contract tests statically verify the orchestrator CLI and startup contract.
- Contract tests verify AI-facing obligations for state safety, external behavior verification, prompt restrictions, and evaluator gating.
- `feature_list.json` conforms to `schemas/feature_list.schema.json`.
- `prompts/plan.md`, `prompts/work.md`, `prompts/continue.md`, and `prompts/evaluate.md` define the standard agent roles.
- The tiny example can be tested without installing third-party dependencies.
- The Go server example can be tested with `go test ./...` when Go is installed.
- `AGENTS.md` includes external behavior verification and external tool schema guardrails.
- `./init.sh` runs unit, contract, smoke, and optional harness tests.
- `docs/README.md`, `QUALITY.md`, and `runs/RUN_TEMPLATE.md` are present and validated.
- `scripts/check-failure-domains.sh` verifies failed run records include failure-domain and harness-improvement fields.
- `make ci` runs the CI verification path.
- `.github/workflows/ci.yml` runs `make ci` on GitHub Actions.
- `make clean` resets `feature_list.json`, `progress.md`, and recorded run artifacts for a fresh project.
- README explains the project as a repository-level harness for resumable AI coding, not a prompt collection.
- `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, and GitHub issue templates are present.

## 5. Verification Plan

Run:

```bash
./init.sh
scripts/validate-feature.sh F001
scripts/summarize-progress.sh
python3 orchestrator.py --dry-run
make ci
```

Run `python3 orchestrator.py --dry-run` and `scripts/validate-feature.sh F001` outside `./init.sh`; both commands call `./init.sh` and should not be nested inside tests run by `./init.sh`.
