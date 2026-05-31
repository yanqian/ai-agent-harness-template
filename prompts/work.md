# Coding Agent Prompt

Act as Coding Agent for one selected feature.

Feature ID: `Fxxx`

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

Do not mark unrelated features done.
Do not overwrite `feature_list.json`.
Do not reset existing feature state.
Preserve existing feature IDs, ordering, `passes`, `status`, `attempts`, `last_error`, and unknown fields.
Do not stage or commit during orchestrated runs.
When relying on external CLI, API, runtime, or structured tool output behavior, verify it with a primary source or real-shaped fixture before depending on it.

Return:

- Feature implemented.
- Files changed.
- Verification commands run.
- Remaining issues.
- Suggested commit message.
