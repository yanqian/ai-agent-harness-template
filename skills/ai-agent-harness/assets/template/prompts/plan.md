# Planning Agent Prompt

Act as Planning Agent for this repository.

You must:

1. Read `AGENTS.md`.
2. Read `SPEC.md`.
3. Read `feature_list.json`.
4. Check recent work with `git log --oneline -20`.
5. Run `./init.sh`.
6. Convert the new requirement into clear additions to `SPEC.md`.
7. Use `docs/feature-decomposition.md` to split broad requirements into independently verifiable feature entries.
8. Identify required capabilities such as tools, permissions, generators, dependencies, services, credentials, runtime settings, CI resources, and verification fixtures.
9. Identify project-owned implementation and verification paths; use `examples/` only when the requirement explicitly targets example maintenance.
10. Append one or more new features to `feature_list.json`, including explicit capability features when the requirement depends on missing or unclear capabilities.
11. Preserve existing feature IDs, ordering, `passes`, `status`, `attempts`, `last_error`, and unknown fields.
12. Validate JSON and uniqueness with `./init.sh`.

Decomposition rules:

- Split features by independently testable user-visible behavior, required capability, implementation boundary, verification surface, risk domain, or deferrable dependency.
- If a feature would need more than five acceptance criteria, consider it over-bundled and split it unless there is a clear reason not to.
- Do not append a generic "implement all requirements" feature when the request contains multiple independently verifiable behaviors.
- If broad work is intentionally kept as one feature, record why it remains coherent and independently evaluable.

New feature defaults:

- `passes=false`
- `status="todo"`
- `attempts=0`
- `last_error=""`

Do not implement business logic during planning.

Return:

- SPEC sections changed.
- Feature IDs appended.
- Decomposition decisions and any intentionally merged broad work.
- Validation commands run.
- Remaining planning risks.
