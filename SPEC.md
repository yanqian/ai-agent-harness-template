# AI Agent Harness Template SPEC

## 1. Goal

Provide a minimal, copyable repository harness for controlled AI-assisted development with Codex, Claude Code, Cursor Agent, or similar coding agents.

The harness makes project state recoverable by storing requirements, feature state, progress, prompts, and validation scripts in files.

## 2. Scope

### Included

- Durable project instructions in `AGENTS.md`.
- Proven agent guardrails for state safety, external behavior verification, and anti-patterns in `AGENTS.md`.
- Human-readable requirements in `SPEC.md`.
- Machine-readable feature state in `feature_list.json`.
- Human-readable recovery state in `progress.md`.
- A JSON Schema for feature state.
- Prompt templates for planning, work, continuation, and evaluation.
- Deterministic validation scripts.
- A test plan and dependency-free unit, contract, and smoke tests.
- A vendor-neutral lightweight `orchestrator.py`.
- A tiny runnable example proving the harness loop works.

### Excluded

- Vendor-specific automation for Codex, Claude Code, Cursor, or other tools.
- Cloud deployment.
- CI provider configuration.
- Automatic commits.
- Vendor-specific orchestration adapters.

## 3. Core Concepts

### Spec First

New work is first written into `SPEC.md` so agents share a stable requirement source.

### Feature Tracked

Every executable unit of work is represented in `feature_list.json` with explicit state and acceptance criteria.

### Evaluator Gated

A feature is complete only when validation passes and an evaluator can justify the result against the acceptance criteria.

### Orchestrated When Needed

`orchestrator.py` can preview or run the coding/evaluation loop for one unfinished feature at a time. It is intentionally vendor-neutral: `--dry-run` prints prompts, while `HARNESS_AGENT_COMMAND` lets downstream projects connect Codex, Claude Code, Cursor Agent, or another command.

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
- `python3 orchestrator.py --dry-run` runs the startup protocol and previews agent prompts without mutating feature state.
- `feature_list.json` conforms to `schemas/feature_list.schema.json`.
- `prompts/plan.md`, `prompts/work.md`, `prompts/continue.md`, and `prompts/evaluate.md` define the standard agent roles.
- The tiny example can be tested without installing third-party dependencies.
- `AGENTS.md` includes external behavior verification and external tool schema guardrails.
- `./init.sh` runs unit, contract, smoke, and optional harness tests.

## 5. Verification Plan

Run:

```bash
./init.sh
scripts/validate-feature.sh F001
scripts/summarize-progress.sh
python3 orchestrator.py --dry-run
```
