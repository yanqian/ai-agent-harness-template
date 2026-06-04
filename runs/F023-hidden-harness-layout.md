# Run Record: F023 - Add hidden harness installation layout

## Summary

- Date: 2026-06-04
- Agent role: Coding Agent
- Feature: F023
- Result: Passed

## Repository State

- Starting commit: f704527
- Ending commit: pending
- Working tree status: modified

## Commands Run

```bash
./init.sh
python3 -m unittest test.unit.test_scripts test.harness.test_skill_initializer
tmpdir=$(mktemp -d); python3 skills/ai-agent-harness/scripts/init_harness.py --root "$tmpdir" --template-root . --mode new; "$tmpdir/init.sh"
rg -n "0\.2\.2|0\.2\.1" . -S
```

## Evidence

- Tests: `./init.sh` passed with 23 validated features, 18 contract tests, 5 harness tests, 8 unit tests, and 1 smoke test.
- Logs: A real temporary hidden-layout project initialized with `layout=hidden` and its root `./init.sh` passed all layers.
- Screenshots or traces: Not applicable.
- External behavior verification: Verified real local initializer behavior and root shell entrypoint behavior with a temporary project.
- Capability gaps: none

## Failure Analysis

- Failure domain: n/a
- Failure summary: none
- Harness improvement: Added hidden and visible installation layout profiles, hidden root entrypoints, layout-aware check/repair/manifest behavior, documentation, bundled template sync, and tests.
- Follow-up feature: none

## Files Changed

- `.agent-harness-template.json`
- `README.md`
- `SPEC.md`
- `feature_list.json`
- `progress.md`
- `runs/F023-hidden-harness-layout.md`
- `scripts/validate-state.py`
- `skills/ai-agent-harness/SKILL.md`
- `skills/ai-agent-harness/references/workflows.md`
- `skills/ai-agent-harness/scripts/init_harness.py`
- `test/unit/test_scripts.py`
- `test/harness/test_skill_initializer.py`
- `test/contract/test_repository_contract.py`
- `skills/ai-agent-harness/assets/template/`

## Evaluator Result

```text
EVAL_PASS: F023
```

## Follow-Up

- Consider a future explicit migration command from visible layout to hidden layout for already-installed projects.
