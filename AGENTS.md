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

### Planning Agent

Use this role for new requirements before implementation begins.

Responsibilities:

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
- Do not stage or commit unless the user explicitly asks.

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
- If verification fails, explain the exact failure.

The Evaluator Agent must output exactly one of:

```text
EVAL_PASS: Fxxx
EVAL_FAIL: Fxxx: <reason>
```

## State Files

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
- `status=done` must not conflict with `passes=false`.
- Agents must not delete unknown fields.

### `progress.md`

`progress.md` must include:

- Current system status.
- Last completed feature.
- Next feature.
- Known issues.
- Recovery notes when useful.

## Verification

`./init.sh` is the default verification entry point. It must be deterministic and fail with a non-zero exit code when the repository is not in a usable state.

Feature-level validation uses:

```bash
scripts/validate-feature.sh F001
```

