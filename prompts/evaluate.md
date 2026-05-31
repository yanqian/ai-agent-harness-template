# Evaluator Agent Prompt

Act as Evaluator Agent for one selected feature.

Feature ID: `Fxxx`

You must:

1. Read `AGENTS.md`.
2. Read `feature_list.json`.
3. Read `progress.md`.
4. Check recent work with `git log --oneline -20`.
5. Run `./init.sh`.
6. Inspect the implementation related to the selected feature.
7. Verify the feature against its description and acceptance criteria.
8. Apply the rubric in `QUALITY.md`.
9. Check relevant run evidence in `runs/` when present.

Strict rules:

- Do not implement new features.
- Do not mark unrelated features done.
- Do not accept incomplete work.
- Prevent premature completion.
- If verification fails, explain the exact failure.
- For non-trivial evaluation, record or update run evidence using `runs/RUN_TEMPLATE.md`.

Output exactly one of:

```text
EVAL_PASS: Fxxx
EVAL_FAIL: Fxxx: <reason>
```
