# Run Record: F026 - Preserve executable script modes during installation

## Summary

- Date: 2026-06-04
- Agent role: Coding Agent
- Feature: F026
- Result: Passed

## Repository State

- Starting commit: 707c1dd
- Ending commit: pending
- Working tree status: modified

## Commands Run

```bash
./init.sh
python3 -m unittest test.harness.test_skill_initializer
python3 -m unittest test.contract.test_repository_contract
scripts/validate-feature.sh F026
git diff --check
```

## Evidence

- Reproduced the issue using the installed skill template: source shell scripts under `~/.codex/skills/ai-agent-harness/assets/template` were not executable after GitHub download installation.
- Added `EXECUTABLE_TEMPLATE_PATHS` and chmod handling in `skills/ai-agent-harness/scripts/init_harness.py`.
- Added a regression test that removes executable bits from a copied template source and verifies hidden-layout install still produces executable entrypoints and runnable `./init.sh`.
- Capability gaps: none

## Failure Analysis

- Failure domain: environment_gap
- Failure summary: GitHub zip/download installation can strip executable bits from skill template shell scripts, causing hidden-layout semantic validation to fail after install.
- Harness improvement: Initializer now enforces executable bits for required harness shell entrypoints after writing files, independent of source template modes.
- Follow-up feature: none

## Evaluator Result

```text
EVAL_PASS: F026
```

## Follow-Up

- Update the installed local skill after release so future user projects receive the executable-bit fix.
