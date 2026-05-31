# AGENTS.md

This repository uses a long-running AI agent harness.

Agents must behave like stateless workers:

- No durable memory between sessions.
- All durable state lives in repository files.
- Every session reconstructs context from files and git history.

## Core Principle

Never rely on chat history. Always rely on project state.

## Required Startup Protocol

Before planning, coding, evaluating, or resuming work, agents must:

1. Read `progress.md`.
2. Read `feature_list.json`.
3. Check recent work:

   ```bash
   git log --oneline -20
   ```

4. Run:

   ```bash
   ./init.sh
   ```

## Roles

### Initializer

Use this role when bootstrapping a new repository from the template.

Responsibilities:

- Create or adapt `SPEC.md`.
- Create or adapt `feature_list.json`.
- Create or adapt `progress.md`.
- Create or adapt `init.sh`.
- Initialize git when the repository has no git history.
- Do not implement business logic during initialization.

### Planning Agent

Use this role for new requirements before implementation begins.

Responsibilities:

- Read `AGENTS.md`.
- Read `SPEC.md`.
- Read `feature_list.json`.
- Append the new requirement to `SPEC.md`.
- Append new feature entries to `feature_list.json`.
- Preserve all existing feature IDs, order, status fields, attempts, errors, and unknown fields.

Strict rules:

- Do not modify existing feature IDs.
- Do not reorder existing features.
- Do not reset existing feature state.
- Only append new feature entries unless explicitly instructed otherwise.
- Ensure `feature_list.json` remains valid JSON.
- Ensure feature IDs remain unique.

### Coding Agent

Use this role to implement exactly one feature.

Responsibilities:

- Follow the startup protocol.
- Implement only the selected feature.
- Keep the system runnable.
- Update `progress.md`.
- Update only the selected feature in `feature_list.json`.
- Preserve unknown feature fields and feature ordering.
- Do not stage or commit during orchestrated runs.
- Do not modify unrelated pre-existing working-tree changes.

The Coding Agent must not mark unrelated features as done.

### Evaluator Agent

Use this role to verify one feature.

Responsibilities:

- Follow the startup protocol.
- Inspect the implementation for the selected feature.
- Run relevant tests or harness checks.
- Verify the feature against its description and acceptance criteria.

Strict rules:

- Do not implement new features.
- Do not mark unrelated features done.
- Do not accept incomplete work.
- Prevent premature completion.
- If verification fails, explain the exact failure.

The Evaluator Agent must output exactly one of:

```text
EVAL_PASS: Fxxx
EVAL_FAIL: Fxxx: <reason>
```

### Orchestrator

`orchestrator.py` owns optional unattended feature execution.

Responsibilities:

- Follow the startup protocol before doing anything else.
- Pick one unfinished feature per round.
- Mark the selected feature `status="in_progress"`.
- Increment the selected feature's `attempts`.
- Run a Coding Agent prompt for that feature.
- Run an Evaluator Agent prompt for that feature.
- Mark the feature done only after evaluator pass.
- Mark the feature failed or blocked after coding or evaluation failure.

The template orchestrator is vendor-neutral. By default it supports `--dry-run` prompt preview. To execute real agents, replace the role adapters:

- `scripts/run-coding-agent.sh`
- `scripts/run-evaluator-agent.sh`

The orchestrator sends each role prompt to the corresponding adapter on stdin.

## State Files

## Repository Knowledge Map

`AGENTS.md` is the entry point, not the whole manual.

Use these durable knowledge files:

- `docs/README.md` for the repository knowledge index.
- `docs/architecture.md` for structure and boundaries.
- `docs/testing.md` for verification layers.
- `docs/external-behavior.md` for CLI, API, runtime, and tool-output verification rules.
- `docs/agent-workflow.md` for planning, coding, evaluation, continuation, and run artifacts.
- `QUALITY.md` for evaluator criteria.
- `runs/` for per-run evidence and handoff records.

### `feature_list.json`

`feature_list.json` is the machine-readable feature scope and state.

Each feature must include:

- `id` string, such as `F001`
- `title` string
- `description` string
- `acceptance` array of strings
- `passes` boolean
- `status` string: `todo`, `in_progress`, `done`, or `blocked`
- `attempts` integer
- `last_error` string
- optional metadata such as `priority`

Rules:

- `passes=true` means complete.
- `passes=false` means incomplete.
- `status` is orchestration state and must not conflict with `passes`.
- `status=blocked` means temporarily skipped after repeated failures.
- `attempts` is incremented when the orchestrator starts a round for that feature.
- Agents must not delete unknown fields.
- Agents must preserve unknown fields.

## State Safety Rules

- Do not overwrite the entire `feature_list.json` unnecessarily.
- Update only the current feature during Coding Agent work.
- Preserve feature ordering and existing fields.
- Do not remove metadata fields.
- Do not reset existing fields such as `passes`, `status`, `attempts`, or `last_error` unless explicitly instructed.

### `progress.md`

`progress.md` must include:

- Current system status.
- Last completed feature.
- Next feature.
- Known issues.
- Recovery notes when useful.

The Coding Agent updates `progress.md` after implementation work.

## External Behavior Verification

When implementation depends on behavior outside this repository's own code, agents must verify that behavior before relying on it.

Examples include:

- CLI tools and their flags, stdin/stdout/stderr behavior, exit codes, signals, working directory, environment variables, and timeout behavior.
- Third-party APIs, webhooks, SDKs, protocol payloads, callback formats, and version-specific fields.
- Runtime and platform behavior such as process management, filesystem semantics, shell behavior, permissions, networking, deployment platforms, and operating-system differences.
- Model or tool output schemas, streamed event formats, JSONL event fields, and approval or permission protocols.

Rules:

- Do not infer unknown external behavior from intuition or local mocks.
- Prefer primary sources: official help output, official documentation, real minimal commands, real sample payloads, or captured logs from the target tool.
- Treat mocks and fake children as tests of this repository's state machine only; they do not prove the external tool or platform behaves that way.
- When changing process semantics such as argv, stdio, cwd, env, timeout, signal handling, or shell mode, verify the real command behavior or document why direct verification is not possible.
- When depending on structured output fields, verify with real-shaped output from the source and add regression tests using those captured shapes.
- If behavior remains uncertain, state the uncertainty explicitly in `SPEC.md`, `progress.md`, or implementation notes, and choose the safer default.

### External Tool Schema Rules

When implementing behavior that parses output from external tools such as Codex CLI JSONL, Claude JSON, Cursor logs, deployment CLIs, test runners, or webhook payloads:

- Do not invent or assume field names from naming convention alone.
- Prefer real captured local output or official documentation as fixtures.
- Add regression tests using real-shaped output for every trusted schema field.
- If the schema is unknown, fail closed instead of extracting identifiers from assistant prose, command output, source files, documentation, or log tails.

## Work Rules

- Only one feature per Coding Agent run.
- Always keep the system runnable.
- Always run `./init.sh` before declaring success.
- The Coding Agent updates state and progress for its target feature.
- The Evaluator Agent verifies without implementation changes.
- The orchestrator owns unattended feature state transitions.

## Anti-Patterns

- Doing multiple features in one Coding Agent run.
- Relying on previous chat instead of repository files.
- Skipping `./init.sh`.
- Leaving broken code.
- Coding Agent committing during orchestrated runs.
- Evaluator Agent accepting incomplete work.
- Marking a feature done without evaluator pass.

## Goal

Make the system:

- Recoverable at any time.
- Runnable at any time.
- Continuously improvable.
- Resistant to premature completion.

## Verification

`./init.sh` is the default verification entry point. It must be deterministic and fail with a non-zero exit code when the repository is not in a usable state.

Feature-level validation uses:

```bash
scripts/validate-feature.sh F001
```

Optional orchestration preview uses:

```bash
python3 orchestrator.py --dry-run
```
