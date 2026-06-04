# Continue Agent Prompt

Act as a recovery agent for this repository.

You must reconstruct context from repository state only:

1. Read `AGENTS.md`.
2. Read `progress.md`.
3. Read `feature_list.json`.
4. Check recent work with `git log --oneline -20`.
5. Run `./init.sh`.
6. Inspect `git status --short`.
7. Determine whether work is complete, incomplete, or blocked.
8. If prior work failed, inspect `runs/` and `docs/failure-domains.md` before deciding the next action.
9. If prior work used a workaround for a missing tool, dependency, generator, permission, service, credential, runtime setting, CI resource, or verification fixture, inspect `docs/capability-gaps.md` before continuing.

Do not rely on prior chat history.
Do not reset or discard user changes.
Do not overwrite `feature_list.json`.
Do not reset existing feature state.
Stop and report exact conflicts when repository state is unsafe.
Use `orchestrator.py` according to `AGENTS.md` when implementation or evaluation is required.
Do not continue repeated failures without either implementing a harness improvement or adding an explicit follow-up feature.
Do not continue local-only capability workarounds as if they were durable completion.

Return:

- Current feature state.
- Working tree state.
- Verification status.
- Failure domain and harness improvement status when prior work failed.
- Capability gap status and durable capability or follow-up when prior work used a workaround.
- Recommended next action.
