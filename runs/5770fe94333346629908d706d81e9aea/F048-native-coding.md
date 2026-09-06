# F048 current-runtime verification handoff

FAST_CODING_EVIDENCE: F048

Existing F048 implementation has been reviewed and retained unchanged. Attempt 1's independent Evaluator passed all criteria, but the parent loaded the previous schema validator and failed final receipt construction after the upgrade. No receipt was created, and that old verdict is not reused for completion. The exact failure is retained in runs/3211a673a7e04b68a8a7f7c2ad93eb0f/ and runs/20260905T145932Z-F048-failure.md.

This new work-fast round is enrolled by the new coordinator before this review. No source or Feature state was edited by the native coding session, and no dirty paths were adopted. Every prior uncommitted path remains protected. The original implementation diff and review are available in the previous run's coding-changed-paths.json, handoff/run snapshots, F048-coding.md and independent-evaluation.md; this round's attributable diff is correctly empty.

Implementation: full protected Feature state/contracts, staged+unstaged+untracked dirty union, pre-coding adoption and optional literal allowlist, post-role violation reports preserving the tree, explicit restart, attributable before/after diff, mandatory independent scope judgment, and hashed boundary enrollment sidecars in new receipts. Missing evidence cannot downgrade a new receipt to historical compatibility. Bundled runtime/docs/prompts/skill/tests and version sources are synchronized at 0.4.0.

Verification: full independent and coding init plus selected F048 validation passed in the previous run; this new coordinator startup also passed. 69 unit tests (one existing platform skip), 33 contract, 12 installation/harness, 2 smoke tests and example checks. Coordinating review reproduced and corrected staged/worktree cancellation and missing-sidecar downgrade cases; real Git/subprocess regressions cover both modes and layouts.

The new coordinator and actual configured Codex evaluator also passed an isolated real-provider scope-protocol smoke: runs/20260905-F048-provider-smoke/runs/7d73c00531d0497996a014a2ba4dfa55/receipt.json includes role_boundary hashes and passing raw provider scope evidence. It verifies actual protocol behavior, not this Feature's completion.

User explicitly authorized current OpenAI/Codex repository contexts for F046-F048. No staging, commit, push, rollback or global configuration changes. Fresh independent current-run assessment, required checks and guard-bearing receipt are still required.

CODING_PASS: F048
