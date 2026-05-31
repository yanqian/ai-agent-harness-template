# Quality Rubric

Evaluator Agents use this rubric when deciding whether a feature is complete.

The feature must satisfy its `feature_list.json` acceptance criteria and preserve the repository harness contracts. Tests passing is necessary but not always sufficient.

## Criteria

### Correctness

- The implementation satisfies the feature description and acceptance criteria.
- The implementation handles expected success and failure paths.
- The implementation does not depend on unverified external behavior.

### Completeness

- The implemented surface matches the requested scope.
- Documentation, prompts, scripts, examples, and tests are updated when affected.
- No required follow-up is hidden as "future work" unless explicitly accepted.

### Maintainability

- The change follows existing repository structure and naming.
- The change avoids unnecessary abstractions.
- Durable knowledge is stored in repository files, not chat history.

### Test Coverage

- Unit, contract, smoke, and relevant harness tests cover the behavior.
- Tests assert meaningful outcomes, not only file existence.
- Real-shaped fixtures or primary-source verification support external tool assumptions.

### Recoverability

- A future agent can resume from `AGENTS.md`, `SPEC.md`, `feature_list.json`, `progress.md`, `docs/`, `QUALITY.md`, `runs/`, and git history.
- State files remain valid and internally consistent.
- Run evidence is recorded when the work involves non-trivial verification or failure analysis.

### Safety

- The change preserves unrelated user work.
- The change does not broaden execution authority accidentally.
- The evaluator rejects premature completion.

## Pass Guidance

Return `EVAL_PASS: Fxxx` only when:

- All relevant verification commands pass.
- Acceptance criteria are met.
- The rubric above has no unresolved critical issue.

Return `EVAL_FAIL: Fxxx: <reason>` when:

- A required behavior is missing.
- State is inconsistent.
- Verification was skipped or inconclusive.
- External behavior was assumed without evidence.

