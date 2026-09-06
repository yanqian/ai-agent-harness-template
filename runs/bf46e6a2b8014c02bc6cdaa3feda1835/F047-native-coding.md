# F047 repair coding evidence

FAST_CODING_EVIDENCE: F047

Attempt 1 was rejected by the independent Evaluator: supported legacy feedback broke historical validation. This attempt preserves that evidence and repairs the same Feature. Shared lock/atomic state/dependency implementation from attempt 1 remains; no F048 implementation is included.

Added completion.legacy_matches: exact completion identity plus strict replay of appended observational human feedback over frozen human metadata. Reopening, edited history, changed criteria/attempts and contradictory legacy repairs cannot reuse the exemption. The frozen policy is never mutated. Human Eval now checks proposed completion history before publishing state or feedback records.

Regressions use actual Human Eval subprocesses for pass/new_requirement/batch/reopen, with visible and hidden layouts; verify immutable policy, valid resulting history, preserved metadata, rejected spoofed history/criteria/attempt/reopen, and no publication on unsupported legacy transitions. All original 44 Features remain unchanged. Bundled files are synchronized.

Validation: selected-feature validation (including full ./init.sh) passed, as did focused state tests and git diff --check. Logs are F047-repair-validation.log and F047-repair-unit.log in this run directory. Earlier F047 tests include real competing orchestrator/Human Eval subprocesses, atomic visibility, killed writers and stale-state checks. No external provider process semantics changed.

The user has authorized real repository context for the configured independent evaluator. No lifecycle edits, evaluator approval, stage, commit, push or rollback were performed by coding. Independent assessment and runner receipt remain required.

CODING_PASS: F047
