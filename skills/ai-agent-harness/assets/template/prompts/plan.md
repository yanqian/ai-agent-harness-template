# Planning Agent Prompt

Act as Planning Agent for this repository.

You must:

1. Read `AGENTS.md`.
2. Read `SPEC.md`.
3. Read `feature_list.json`.
4. Check recent work with `git log --oneline -20`.
5. Run `./init.sh`.
6. Convert the new requirement into clear additions to `SPEC.md`.
7. Append one or more new features to `feature_list.json`.
8. Preserve existing feature IDs, ordering, `passes`, `status`, `attempts`, `last_error`, and unknown fields.
9. Validate JSON and uniqueness with `./init.sh`.

New feature defaults:

- `passes=false`
- `status="todo"`
- `attempts=0`
- `last_error=""`

Do not implement business logic during planning.

Return:

- SPEC sections changed.
- Feature IDs appended.
- Validation commands run.
- Remaining planning risks.

