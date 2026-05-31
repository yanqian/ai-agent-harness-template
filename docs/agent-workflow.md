# Agent Workflow

## Planning

Use `prompts/plan.md` for new requirements.

Planning appends to `SPEC.md` and `feature_list.json`. It does not implement business logic.

## Coding

Use `prompts/work.md` for one selected feature.

The Coding Agent runs `./init.sh` before and after changes, updates only the selected feature state, and records progress.

## Evaluation

Use `prompts/evaluate.md`.

The Evaluator Agent checks the feature against acceptance criteria and `QUALITY.md`. It must output exactly one pass or fail line.

## Continuation

Use `prompts/continue.md` after interruptions.

Continuation reconstructs context from repository files and git history only.

## Run Artifacts

For non-trivial work, create a run note from `runs/RUN_TEMPLATE.md`.

Run notes capture commands, evidence, decisions, failures, and next actions.

