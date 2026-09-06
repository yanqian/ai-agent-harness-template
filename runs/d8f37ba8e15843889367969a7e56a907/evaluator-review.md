# Run Record: F047 - independent lifecycle evaluation

## Summary
- Date: 2026-09-05
- Agent role: independent receipt Evaluator
- Feature: F047, attempt 1, run d8f37ba8e15843889367969a7e56a907
- Result: rejected; criteria 2 and 3 fail due to legacy Human Eval compatibility.

## Repository State
- Starting/ending commit: 7929e0f; no source or lifecycle changes by evaluator.
- Candidate snapshot and criteria verified unchanged through run_evidence.assert_unchanged.
- Nine affected bundled runtime/schema/document/test files independently compared equal.

## Commands Run
- ./init.sh (independent run, exit 0; evaluator-init.log)
- scripts/validate-feature.sh F047 (independent run, exit 0; evaluator-validation.log)
- Real isolated temporary fixtures: freeze legacy done F001, verify history, invoke actual Human Eval subprocess for pass/current_feature and fail/new_requirement, verify resulting history.

## Evidence
- Runner check-0.json records ./init.sh exit 0 and bound log hashes.
- evaluator-legacy-feedback-repro.json records both actual subprocess outcomes.
- Both feedback commands exit 0, preserve frozen policy and keep F001 done, but verify_history raises F001: missing current-run completion receipt.
- Root cause: completion.legacy_identity includes human_acceptance; supported feedback mutates this identity without providing a valid migration/evidence path. human-eval.py validates only state invariants before publication, not completion-history integrity.
- Tests cover real competing orchestrators and Human Eval in both layouts, stale writers, interrupted replacement, atomic reader visibility, dependency readiness and receipt-era reopen/retry. Existing tests omit feedback on frozen legacy completions.
- Normalized SPEC fields and decomposition present; no requirement, example-scope or capability gap.

## Failure Analysis
- Failure domain: implementation_gap
- Failure summary: successful supported Human Eval leaves historical completion invalid.
- Harness improvement: required in F047. Provide durable legacy-feedback handling without weakening receipt-era reopen or mutating frozen policy; alternatively fail unsupported transitions before state publication with recovery guidance. Add regression tests for both feedback paths and resulting completion-history validity.
- Follow-up feature: none; unmet current F047 lifecycle compatibility scope.

## Files Changed
- Evaluation evidence only in this run directory.

## Evaluator Result
Receipt JSON returned to the runner; no legacy PASS line and no completion-state mutation.

## Follow-Up
Repair F047, rerun checks and obtain a fresh bound independent evaluation.
