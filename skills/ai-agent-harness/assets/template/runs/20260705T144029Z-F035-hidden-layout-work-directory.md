# Run Record: F035 - hidden-layout work directory

## Summary

- Date: 20260705T144029Z
- Agent role: Coding Agent and Evaluator Agent manual fallback
- Feature: F035
- Result: pass

## Repository State

- Starting commit: 91b5c78
- Ending commit: pending
- Working tree status: modified

## Commands Run

```bash
python3 -m unittest discover -s test/contract -p 'test_*.py'
python3 -m unittest discover -s test/harness -p 'test_*.py'
./init.sh
scripts/validate-feature.sh F035
```

## Evidence

- Tests: contract tests passed, harness initializer tests passed, full `./init.sh` passed, and `scripts/validate-feature.sh F035` passed.
- Logs: `./init.sh` validated 35 features and completed unit, contract, harness, and smoke layers.
- Screenshots or traces:
- External behavior verification: Not applicable; this feature documents repository-local hidden-layout command routing.

## Failure Analysis

- Failure domain: none
- Failure summary: No failure. Manual fallback was used because provider adapters are intentionally unconfigured in this template checkout.
- Harness improvement: Hidden-layout root instructions, workflow docs, prompts, skill references, bundled template files, and tests now make `make -C .agent-harness work` explicit.
- Follow-up feature:

## Files Changed

- `AGENTS.md`
- `README.md`
- `SPEC.md`
- `docs/agent-workflow.md`
- `docs/agent-provider-configuration.md`
- `docs/new-project-flow.md`
- `prompts/continue.md`
- `prompts/evaluate.md`
- `prompts/work.md`
- `skills/ai-agent-harness/`
- `.agent-harness-template.json`
- `feature_list.json`
- `progress.md`
- `test/contract/test_repository_contract.py`
- `test/harness/test_skill_initializer.py`

## Evaluator Result

```text
EVAL_PASS: F035
```

## Follow-Up

- None.
