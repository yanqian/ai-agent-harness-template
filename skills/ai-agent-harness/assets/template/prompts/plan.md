# Planning Agent Prompt

Act as Planning Agent for this repository.

You must:

1. Read `AGENTS.md`.
2. Read `SPEC.md`.
3. Read `feature_list.json`.
4. Check recent work with `git log --oneline -20`.
5. Run `./init.sh`.
6. Convert the new requirement into clear additions to `SPEC.md`.
7. Identify required capabilities such as tools, permissions, generators, dependencies, services, credentials, runtime settings, CI resources, and verification fixtures.
8. Identify project-owned implementation and verification paths; use `examples/` only when the requirement explicitly targets example maintenance.
9. Append one or more new features to `feature_list.json`, including explicit capability features when the requirement depends on missing or unclear capabilities.
10. Preserve existing feature IDs, ordering, `passes`, `status`, `attempts`, `last_error`, and unknown fields.
11. Validate JSON and uniqueness with `./init.sh`.

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
