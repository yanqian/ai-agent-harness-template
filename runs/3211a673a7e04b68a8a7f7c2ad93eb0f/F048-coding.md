# F048 coding evidence

Active run: 3211a673a7e04b68a8a7f7c2ad93eb0f (baseline Coding Agent child).
No manual fallback or work-fast record-coding call. No lifecycle/state mutation,
evaluator approval, staging, commit, push, policy change or example changes.

## Implementation

- scripts/role_boundary.py freezes the full Feature document and selected contract
  files before coding; protects staged/unstaged/untracked initial dirty paths by
  default; validates literal project-relative pre-coding adoption/allowed paths.
- Both orchestrator modes check coding boundaries and source/state immutability
  around verification/evaluation. Enrollment markers permit startup checks even
  after a role deletes its active_run link or writes early done.
- Durable violations preserve files, reject completion and require explicit
  --restart-run. Restart archives live evidence without resetting attempts or
  discarding the working tree. Malformed state is preserved for manual recovery.
- Full changes.json includes before/after bytes, textual diff, index/mode metadata
  and new/deleted/unusual paths. Independent evaluator must report scope relevance;
  bridge retains raw provider stdout and records bound scope evidence.
- Optional receipt role_boundary field explicitly hashes enrollment and all
  boundary/scope/change sidecars. Existing historical receipts keep their exact
  schema behavior; enrolled receipts cannot silently downgrade when sidecars vanish.
- Runtime/schema/docs/prompts/skill/tests bundled distribution synchronized; version
  sources and version contracts now use 0.4.0. No project state imported to bundle.

Changed source inventory: coding-changed-paths.json (relative to the initial handoff,
not HEAD, so prior uncommitted F045-F047 work is not attributed to F048). Progress and
this run evidence are excluded metadata and were also updated.

## Verification

- Startup ./init.sh: passed before editing (62 unit tests, existing optional skip;
  33 contract, 12 harness, 2 smoke tests).
- python3 -m unittest discover -s test/unit -p test_completion.py: 10 tests passed.
- python3 -m unittest discover -s test/unit -p test_role_boundary.py: 7 test groups
  passed, covering both modes/layouts with real Git and role subprocesses.
- Git cancellation case now uses staged plus unstaged union; test demonstrates
  git diff HEAD alone returns empty while initial dirty protection remains active.
- Final scripts/validate-feature.sh F048 (includes full ./init.sh): see
  coding-validation.log; final outcome will be appended after command completion.
- git diff --check: passed.

Failure domain: contract_gap (the original missing post-role boundary).
Harness improvement: runtime enforcement, receipt enrollment, explicit recovery,
full attributable diff/scope contract and adversarial regression coverage.
One intermediate full init overlapped ongoing template synchronization and correctly
reported installer drift; final validation runs against stable source. This is a
verification scheduling issue, not a bypass or accepted failure.

Capability gaps: no new process flags or external provider event schemas assumed.
The new scope JSON is our own adapter contract, exercised by real subprocess fixtures.
Configured provider scope smoke is delegated to the coordinating runner's authorized
runtime in coordinator-response.md. The current parent loaded F047 before coding:
its genuinely unenrolled handoff uses the previous criterion-only protocol and is
not evidence that F048 protected its own initial implementation. New coordinators
fail closed without boundary and scope enrollment. Do not fabricate retrospective
adoption or weaken the new protocol to accommodate this loaded parent.

Example-boundary assessment: examples/ untouched.
Suggested commit: F048 Reject unauthorized role changes before completion

## Final outcome

scripts/validate-feature.sh F048 exited 0. Its full ./init.sh passed: 69 unit
 tests (one existing optional skip), 33 contract tests, 12 installer/harness tests,
2 smoke tests, Python tiny example and Go example. All source remained stable
during this final verification. Final git diff --check passed. F048 remains
in_progress/passes=false with attempt 1 and the original active run ID unchanged.
Independent evaluator approval and configured new-protocol provider smoke remain
coordinator responsibilities; no evaluator approval is claimed here.

CODING_PASS: F048
