# Agent Workflow

## Planning

Use `prompts/plan.md` for new requirements.

Planning appends to `SPEC.md` and `feature_list.json`. It does not implement business logic.

## Coding

Use `prompts/work.md` for one selected feature.

The Coding Agent runs `./init.sh` before and after changes, updates only the selected feature state, and records progress.

When a required tool, dependency, generator, permission, service, credential, runtime setting, CI resource, or verification fixture is missing, follow `docs/capability-gaps.md`. Do not convert the missing capability into an untracked local workaround.

When implementing project requirements, follow `docs/example-boundaries.md`. Use default examples as references only unless the selected feature explicitly targets example maintenance.

## Evaluation

Use `prompts/evaluate.md`.

The Evaluator Agent checks the feature against acceptance criteria and `QUALITY.md`. It must output exactly one pass or fail line.

Evaluation rejects features that bypass required capability gaps instead of making them durable or tracking them as blocked or follow-up work.

Evaluation rejects project-level features that pass only by repurposing default examples.

## Continuation

Use `prompts/continue.md` after interruptions.

Continuation reconstructs context from repository files and git history only.

## Run Artifacts

For non-trivial work, create a run note from `runs/RUN_TEMPLATE.md`.

Run notes capture commands, evidence, decisions, failures, and next actions.

## Failure Improvement

When work fails, classify the failure using `docs/failure-domains.md`.

Every failed or blocked run should record:

- Failure domain.
- Failure summary.
- Harness improvement assessment.
- Follow-up feature ID if the improvement is deferred.

Use `scripts/check-failure-domains.sh` to verify failed run records include the classification and improvement assessment.
