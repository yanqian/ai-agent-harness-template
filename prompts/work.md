# Coding Agent Prompt

Act as Coding Agent for one selected feature.

This prompt must be rendered with the provider-workspace path contract before provider execution.

Feature ID: `Fxxx`

Default invocation: the Coding Agent prompt is normally dispatched by the orchestrator through baseline `make work`, not the fast `make work-fast` handoff. In hidden-layout installs, run the equivalent command from the project root with `make -C .agent-harness work`, or run `make work` after changing into `.agent-harness/`. If you are running this prompt manually, treat that as an explicit fallback because role adapters are unavailable or the user requested interactive/manual work. A missing root `Makefile` in hidden layout is not a valid manual-fallback reason. Record the fallback in `progress.md` or `runs/`, and do not bypass evaluator gating, evaluator evidence, attempts, failure records, or final `./init.sh` verification.

You must:

1. Read `AGENTS.md`.
2. Read `progress.md`.
3. Read `feature_list.json`.
4. Check recent work with `git log --oneline -20`.
5. Run `./init.sh` before changing files.
6. Implement only the selected feature.
7. Preserve unrelated user changes.
8. Update `progress.md`.
9. Update only the selected feature in `feature_list.json`.
10. Run `./init.sh` after changes.
11. Record run evidence in `runs/` for non-trivial work, external behavior verification, failures, or evaluator handoff.
12. When work fails or is blocked, classify the failure using `docs/failure-domains.md` and assess whether it requires a harness improvement.
13. When a required capability is missing, follow `docs/capability-gaps.md` before using any workaround.
14. When implementation touches `examples/`, follow `docs/example-boundaries.md`.

Do not mark unrelated features done.
Do not overwrite `feature_list.json`.
Do not reset existing feature state.
Preserve existing feature IDs, ordering, `passes`, `status`, `attempts`, `last_error`, and unknown fields.
Do not stage or commit during orchestrated runs.
When relying on external CLI, API, runtime, or structured tool output behavior, verify it with a primary source or real-shaped fixture before depending on it.
Do not bypass missing tools, permissions, generators, dependencies, services, credentials, runtime settings, CI resources, or verification fixtures with hand-written generated artifacts, weakened scope, skipped verification, or local-only environment changes.
If a workaround is temporary, record it and keep the feature incomplete, blocked, or linked to a follow-up feature until the capability is durable or explicitly scoped out.
Do not implement project-level requirements by repurposing default examples such as `examples/tiny-cli` or `examples/go-server`; use project-owned source and tests unless the feature explicitly targets examples.
Do not leave repeated failures as retries only; convert harness weaknesses into docs, prompts, scripts, schemas, tests, or a new feature entry.

Return:

- Feature implemented.
- Files changed.
- Verification commands run.
- Remaining issues.
- Failure domain and harness improvement assessment when applicable.
- Capability gaps and durable capability changes or follow-up feature when applicable.
- Example-boundary assessment when `examples/` changed.
- Suggested commit message.

End with exactly one structured coding verdict line:

```text
CODING_PASS: Fxxx
CODING_FAIL: Fxxx: <reason>
```


## Run-scoped completion

New orchestrator runs use the receipt contract in `docs/run-evidence.md`.
Use only the active run printed in the handoff. Old PASS text cannot complete a
Feature. Work-fast must use `orchestrator.py --record-coding` with that run ID after
coding, then rerun work-fast. Only the runner records command outcomes and links a
validated receipt before marking done. Receipt evaluator prompts explicitly replace
the legacy final text verdict with strict per-criterion JSON; follow the rendered
current-run prompt. Do not copy old receipts or mutate the completion policy.


## Role boundary recovery

New runs freeze protected state and initial dirty paths before coding. Use
`--adopt-dirty PATH` and optional `--allow-path PATH` only when starting a new run;
paths are project-relative, including in hidden layout. Roles must not edit
feature_list.json, SPEC.md, QUALITY.md or completion-policy.json during a run.
Read `docs/run-evidence.md` for changes.json, mandatory evaluator scope relevance,
violation reports and explicit `--restart-run FEATURE --run-id RUN` recovery.
Preserve the tree after violations; never auto-stash, reset, delete or force commit.
Restart the coordinator after upgrading to template 0.4.0.
