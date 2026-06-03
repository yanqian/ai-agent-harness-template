# AI Agent Harness Workflows

These workflows operate the repository-local harness. They are intentionally vendor-neutral; Codex, Claude Code, Cursor Agent, and other coding agents can follow the same file protocol.

If the skill is installed in an agent surface, invoke it by name, for example `Use $ai-agent-harness to initialize this project.` Manual `python3 skills/ai-agent-harness/scripts/init_harness.py` usage is for repository checkouts and tools without a skill loader.

## Initialize Harness

Use when the target project lacks harness files or the user asks to install, adopt, repair, or check the harness.

1. Run `scripts/init_harness.py --mode check --root <project>` when the user only wants inspection.
2. Run `scripts/init_harness.py --mode adopt --root <project>` for an existing project.
3. Run `scripts/init_harness.py --mode new --root <project>` for a new project.
4. Run `scripts/init_harness.py --mode repair --root <project>` for an existing harness with missing files.
5. Do not use `--force` unless the user explicitly approved overwriting conflicts.
6. After initialization, run `<project>/init.sh` if present.

`new` and `adopt` reset project feature state to an empty `feature_list.json` and fresh `progress.md`. `repair` preserves existing project state.

Installed projects record `.agent-harness/manifest.json`. The template records `.agent-harness-template.json`. Use `check` before repair or upgrade decisions: it reports installed version, template version, missing files, merge-sensitive conflicts, harness-owned drift, project-owned state changes, semantic validity, runnable status, and next action guidance.

A project is an installed harness when `./init.sh` succeeds, `feature_list.json` is valid, `progress.md` contains recovery sections, `AGENTS.md` contains the startup and safety rules, prompts and scripts are present, run templates are available, and `check` reports `runnable_harness=true`.

## Plan Requirement

Use when the user describes new work before implementation.

1. Follow the repository startup protocol.
2. Read `AGENTS.md`, `SPEC.md`, `feature_list.json`, and `progress.md`.
3. Append the requirement to `SPEC.md`.
4. Append new feature entries to `feature_list.json`.
5. Preserve feature IDs, ordering, status, attempts, errors, and unknown fields.
6. Do not implement business logic during planning.
7. Run `./init.sh`.

## Work One Feature

Use when the user asks to implement, continue, or work on a harness feature.

1. Follow the repository startup protocol.
2. Select exactly one feature unless the user explicitly names one.
3. Implement only that feature.
4. Preserve unrelated working-tree changes.
5. Update `progress.md`.
6. Update only the selected feature in `feature_list.json`.
7. Record a run note in `runs/` for non-trivial work, external behavior verification, failures, or evaluator handoff.
8. Run `./init.sh` after changes.
9. Do not stage or commit during orchestrated Coding Agent work.

## Evaluate Feature

Use when the user asks whether a feature is complete or asks for evaluation.

1. Follow the repository startup protocol.
2. Inspect the selected feature's implementation.
3. Verify acceptance criteria in `feature_list.json`.
4. Apply `QUALITY.md`.
5. Check relevant run evidence in `runs/`.
6. Do not implement new features.
7. Output exactly `EVAL_PASS: Fxxx` or `EVAL_FAIL: Fxxx: <reason>` when acting as an Evaluator Agent.

## Continue Harness Work

Use after interruption or when the user asks to resume.

1. Reconstruct context from repository files and git history only.
2. Read `progress.md`, `feature_list.json`, `AGENTS.md`, and recent commits.
3. Run `./init.sh`.
4. Identify the next safe action from repository state.
5. Stop and report exact conflicts if state is unsafe.

## Finalize And Commit

Use only when the user explicitly says they are satisfied or asks to commit.

1. Follow the repository startup protocol.
2. Run relevant verification, normally `./init.sh`.
3. Inspect `git status --short`.
4. Identify files changed by the approved work.
5. If unrelated changes are present, ask the user before staging.
6. Stage only approved files.
7. Commit with a concise message. Prefer `Implement Fxxx <feature title>` or `Add Fxxx <feature title>`.
8. Default to no push. Push or pull request creation requires a separate explicit request.

Never commit merely because implementation finished. The commit boundary is user satisfaction.
