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
Do not stage or commit unless explicitly instructed.

Return:

- Feature implemented.
- Files changed.
- Verification commands run.
- Remaining issues.
- Suggested commit message.

