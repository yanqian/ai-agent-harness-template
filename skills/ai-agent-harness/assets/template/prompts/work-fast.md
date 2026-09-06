# Work-Fast Coding Handoff

Act as the provider-native coding phase for one selected feature.

This handoff must be rendered with the provider-workspace path contract before the current provider-native session acts on it.

Feature ID: `Fxxx`

This prompt is emitted by `make work-fast`, the fast A/B alternative to the baseline `make work` flow. In this mode the orchestrator does not invoke the Coding Agent role adapter. The current provider surface performs the implementation, records durable coding evidence, and leaves completion to a separate cold-start Evaluator Agent child process.

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
11. Record coding evidence in `runs/` containing `FAST_CODING_EVIDENCE: Fxxx` and `CODING_PASS: Fxxx`, or `CODING_FAIL: Fxxx: <reason>` when coding cannot complete.

Strict rules:

- Do not invoke `scripts/run-coding-agent.sh` or otherwise spawn the Coding Agent role adapter during the fast coding phase.
- Do not write `EVAL_PASS: Fxxx` in coding evidence.
- Do not mark the selected feature `passes=true` or `status=done`.
- Do not mark unrelated features done.
- Do not stage or commit.
- Do not treat local tests or coding evidence as evaluator evidence.

After coding evidence is recorded, rerun `make work-fast`. The orchestrator must invoke the Evaluator Agent adapter as a separate cold-start child process before any fast-flow feature can become done.

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
