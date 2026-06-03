---
name: ai-agent-harness
description: Use when initializing, adopting, repairing, or operating an AI Agent Harness repository; when the user mentions AGENTS.md, feature_list.json, progress.md, resumable AI coding, Planning Agent, Coding Agent, Evaluator Agent, harness workflow, or committing approved harness work. Supports project initialization, new requirement planning, one-feature implementation, evaluation, and explicit finalize-and-commit workflows while keeping repository files as the durable source of truth.
metadata:
  short-description: Initialize and operate an AI agent harness
---

# AI Agent Harness

Use this skill as the convenience layer for the repository-local AI Agent Harness protocol.

The repository remains the source of durable state. Do not store durable project state in the skill, in chat history, or in hidden local memory.

When this skill is installed, prefer natural invocation such as `Use $ai-agent-harness to initialize this project.` Manual `python3 .../init_harness.py` commands are for repository checkouts, direct script testing, or agent tools without a skill loader.

## Core Rule

Before planning, coding, evaluating, continuing, or committing harness work in a repository that already has `AGENTS.md`, follow that repository's startup protocol. For this harness, that means:

1. Read `progress.md`.
2. Read `feature_list.json`.
3. Run `git log --oneline -20`.
4. Run `./init.sh`.

If the repository does not have the harness yet, use the initializer script below.

## Initialize Or Repair

Use `scripts/init_harness.py` from this skill.

Modes:

- `new`: install the harness into a new or empty project and reset project state.
- `adopt`: install missing harness files into an existing project and reset project state; default mode.
- `repair`: add missing harness files but preserve existing `feature_list.json` and `progress.md`.
- `check`: report missing files, merge-sensitive conflicts, harness-owned drift, project state changes, installed/template versions, semantic validity, runnable status, and next action guidance without writing.

Default behavior never overwrites conflicting files. Use `--force` only after the user explicitly approves overwriting conflicts.

The initializer writes `.agent-harness/manifest.json` into installed projects and reads `.agent-harness-template.json` from the template. File categories matter:

- harness-owned static files are hash checked;
- project-owned state is validated semantically after initialization;
- merge-sensitive files are not overwritten by default;
- optional integrations are reported separately from core harness validity.

Examples:

```bash
python3 /path/to/skill/scripts/init_harness.py --root /path/to/project --mode adopt
python3 /path/to/skill/scripts/init_harness.py --root /path/to/project --mode check
python3 /path/to/skill/scripts/init_harness.py --root /path/to/project --mode repair
```

## Workflows

For planning, one-feature work, evaluation, continuation, and final commit rules, read `references/workflows.md`.

Use the workflow names as intent detectors:

- Initialize Harness
- Plan Requirement
- Work One Feature
- Evaluate Feature
- Continue Harness Work
- Finalize And Commit

## Commit Boundary

Only commit after the user explicitly says they are satisfied or asks to commit.

Before committing:

1. Run the harness startup protocol.
2. Run the relevant verification command, normally `./init.sh`.
3. Inspect `git status --short`.
4. Stage only files related to the approved work.
5. Stop and ask if unrelated changes are present.
6. Commit with a message derived from the feature ID and title when available.

Default to commit only. Push or pull request creation requires a separate explicit request.
