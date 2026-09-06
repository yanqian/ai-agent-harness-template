# F046 native coding handoff

FAST_CODING_EVIDENCE: F046

The existing F046 implementation was produced by the prior independent Coding Agent, then reviewed by the coordinating native session. The prior coding failure was a runtime capability gap, not a successful evaluation. Current code uses one receipt-gated path for work and work-fast, immutable active-run coding/candidate binding, runner-owned recovery checks, strict independent evaluator JSON, historical receipt verification, and frozen explicit migration policy.

Review correction retained: baseline coding consumes actual stdout, while diagnostic stderr containing quoted historical verdict templates is not treated as coding or evaluator approval. Native notes reject evaluator markers. Bundled code and installer regressions cover fresh and legacy visible/hidden layouts.

Validation:
- ./init.sh passed: /tmp/harness-resume-approved-init.log.
- scripts/validate-feature.sh F046 passed: /tmp/harness-F046-coordinator-validation.log.
- git diff --check passed.
- Real configured Codex smoke completed successfully through work-fast and verified its runner-generated receipt. Evidence: runs/20260905-F046-coordinator-provider-smoke/runs/3071ac1cfa4c4571b8701b20182fb85c/receipt.json plus raw provider output/check logs. This synthetic result proves provider protocol support; it does not complete F046.

User explicitly confirmed actual repository context authorization for F046-F048 Coding/Evaluator subprocesses. No commit, staging, rollback, or unrelated Feature mutation was performed. F047/F048 implementation is deferred until F046 independent acceptance. Existing original 44 Feature entries and all prior implementation/planning edits are preserved.

CODING_PASS: F046
