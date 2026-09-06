# F047 coding evidence

- Active run: d8f37ba8e15843889367969a7e56a907, baseline work coding child.
- Selected feature: F047 only. No manual fallback and no lifecycle-state edits.

## Implementation and files

- Added scripts/state_store.py: validated dependency DAG/readiness, lifecycle
  consistency, permanent ownership/write lock inodes, revision compare-and-swap,
  fsynced temporary write/atomic replacement/directory sync and evidence archival.
- orchestrator.py uses shared load/save and round ownership, checks dependencies
  in baseline/fast selection and completion, resets rejected metadata on retry
  without losing history, and locks record-coding independently.
- scripts/human-eval.py uses the same ownership/storage, archives active completion
  on reopen, retains history, keeps pending reopen across independent feedback,
  and uses unique feedback record names. State publication follows record creation.
- scripts/completion.py and scripts/validate-state.py enforce lifecycle validation;
  completion also checks dependency readiness. Schema declares depends_on and
  completion_history; scripts/init.sh and the initializer require the state module.
- docs/run-evidence.md and test_plan.md document invariants, interruption behavior,
  POSIX contract, legacy boundary and coordinator restart requirement.
- test/unit/test_state_store.py covers real subprocess owners, stale writers,
  short-write contention, atomic reader visibility, killed pre-replace writer,
  graph validation, fast dependency resume and reopen/retry evidence/history.
- test/unit/test_completion.py adds real competing orchestrators and Human Eval
  under visible and hidden layouts, invalid-graph command behavior, and exercises
  actual Human Eval for reopening completed receipt-backed fixtures.
- Corresponding bundled distribution files are byte-identical; progress.md records
  the handoff. No examples changed. No stage, commit, push or global config edits.

## Verification and external behavior

- Startup ./init.sh passed: /tmp/F047-startup.log.
- Initial unit regression found old tests directly constructing a newly forbidden
  reopen state and an inconsistent exception type at the completion API. Updated
  the fixture to use actual Human Eval and retained EvidenceError at that API.
- Unit suite passed; subsequent added atomic-reader/short-lock test also passed.
- ./init.sh passed: F047-init.log in this run directory.
- Selected-feature validation result is in F047-validation.log in this run.
- git diff --check passed. Original 44 feature entries match git 7929e0f as parsed
  JSON. Completion policy and provider configuration match the active handoff
  hashes. All modified bundled copies match their root counterparts.
- OS behavior is verified with actual POSIX child processes and local filesystem
  writes. The killed writer test pauses inside a child immediately before real
  replacement and kills it; the reader test reads during repeated real replaces.
  Fake coding/evaluator adapters exercise only harness state-machine integration;
  no new external provider output semantics are introduced or claimed verified.

## Failure analysis and remaining boundary

- Failure domain: contract_gap (pre-existing missing transaction/dependency guard).
- Harness improvement: shared state API, graph/lifecycle validation, documented
  recovery and real subprocess regression tests durably address that gap.
- Capability gaps: none for F047 local POSIX behavior. No workaround or follow-up
  capability feature required. No example-boundary issue.
- Independent evaluator acceptance and the runner's receipt/finalization remain
  pending. This note does not approve evaluation or complete the Feature.
- The existing coordinator loaded F046 runtime before this coding child; restart
  before F048 to use the new ownership implementation. F048 retains direct role
  write-set protection and final version synchronization; not implemented here.
- Suggested commit: F047 Enforce dependency and lifecycle state transactions

Final selected-feature validation exited 0: 59 unit tests (one existing optional
skip), 33 contract tests, 12 harness tests and 2 smoke tests passed, plus example
checks. Its final ./init.sh printed `init verification passed`, followed by
`feature validation passed: F047`.

CODING_PASS: F047
