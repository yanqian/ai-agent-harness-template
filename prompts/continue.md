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

Do not rely on prior chat history.
Do not reset or discard user changes.

Return:

- Current feature state.
- Working tree state.
- Verification status.
- Recommended next action.

