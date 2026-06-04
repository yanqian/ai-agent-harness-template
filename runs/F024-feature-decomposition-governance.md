# Run Record: F024 Feature Decomposition Governance

## Feature

- ID: F024
- Title: Add feature decomposition governance
- Status: done

## Summary

Added durable planning and evaluation rules so broad user requirements are split into independently verifiable feature entries. The rule is now documented in `docs/feature-decomposition.md`, referenced from core repository docs, enforced by Planning and Evaluator prompts, included in the distributable skill workflow, and locked by contract tests.

## Commands Run

- `./init.sh`
- `python3 -m unittest test.contract.test_repository_contract`

## Evidence

- `docs/feature-decomposition.md` defines the core feature-granularity rule, split triggers, allowed merges, required planning output, and evaluator rejection criteria.
- `prompts/plan.md` requires Planning Agent to use the decomposition rules before appending features.
- `prompts/evaluate.md` requires Evaluator Agent to reject over-bundled feature entries with `feature_decomposition_gap`.
- `test/contract/test_repository_contract.py` verifies the governance remains present across docs, prompts, skill guidance, initializer files, and bundled template expectations.

## Failure Analysis

- Failure domain: n/a
- Failure summary: none
- Harness improvement: implemented directly as F024
- Follow-up feature: none

## Evaluator Result

EVAL_PASS: F024

## Follow-Up

- None.
