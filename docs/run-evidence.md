# Run-scoped evidence primitives

F045 provides `scripts/run_evidence.py` and strict JSON schemas for run manifests,
criterion assessments and receipts. F046 enrolls orchestration in this contract;
these primitives alone do not change the existing PASS-line completion policy.
No primitive writes Feature lifecycle state or launches another orchestrator.

## Runner API

The coordinating runner calls these functions in order:

1. `create_run(workspace, feature, attempt, layout, additional_commands=())`
   freezes the candidate source snapshot, Feature ID/title/description/acceptance,
   attempt and required argv checks. It generates a UUID run ID and writes an
   exclusive `runs/<run_id>/run.json`. In hidden layout these files live under
   `.agent-harness/runs/`. Workspace must be the real Git repository root.
   Call this at the candidate verification boundary; initial coding handoff and
   resume enrollment are F046 responsibilities.
2. `execute_required(workspace, run)` runs root `./init.sh` first, then each
   additional command in declared order. Each command specifies nonempty `argv`
   and positive integer `timeout_seconds`; no shell parses argv. Commands run
   from the project root, inherit the runner environment, and receive EOF stdin.
   The runner writes exclusive stdout/stderr files and an outcome JSON, including
   exit code, timeout flag, launch error and SHA-256 log hashes. Failed checks
   retain evidence and cannot form a successful receipt. Timeouts terminate the
   immediate child; this primitive does not promise descendant process isolation.
3. `evaluate(workspace, run, configured_adapter_command)` launches a separate
   process. Its stdout must contain exactly one `evaluation.schema.json` object,
   not Markdown, provider-native events or a PASS line. The caller configures an
   adapter that reads the manifest and maps its provider to this harness-owned
   protocol. No external provider schema is assumed. Every zero-based acceptance
   index must appear once with pass/fail, a nonblank reason and nonblank evidence
   references. Binding includes Feature/run/attempt/contract/source fingerprints.
   The runner captures output directly; the agent cannot supply command outcomes.
4. `build_receipt(workspace, run, checks, evaluator_command, evaluation, feature)`
   checks persisted runner records, log hashes, exact required-command coverage,
   actual captured evaluator JSON, complete passing criteria and unchanged live
   source/contract. It writes `receipt.json` exclusively, with a checksum. It does
   not mark anything done. Interrupted or rejected work remains inspectable;
   existing evidence is never overwritten. Start a new run to retry execution.

`validate_run`, `validate_evaluation` and `validate_receipt` reject unknown/missing
fields, wrong types (including booleans as integers), malformed fingerprints,
cross-run bindings and incomplete criterion coverage. `decode_json` additionally
rejects duplicate keys and nonfinite JSON constants. The standard-library schema
validator implements precisely the keywords used by the shipped schemas; changing
schemas requires updating that validator and tests together.

## Source identity

`git-source-v1` uses real `git ls-files --stage -z` and `--others -z`, supplemented by a non-following directory walk because Git
omits untracked FIFOs. Each entry
records its path, index mode/blob object ID/stage, worktree kind/permission mode
and SHA-256 of file bytes or symlink target bytes. Tracked deletion has an explicit
marker; index deletion also changes the snapshot. Index and worktree differences
remain distinct even when the worktree is restored to HEAD. No commit is needed.
NUL-delimited Git output supports spaces, tabs, newlines, leading dashes, Unicode
and, on filesystems permitting them, undecodable filename bytes (JSON escapes
preserve filesystem surrogate bytes). macOS rejected the invalid-UTF-8 fixture
with EPERM; its separate regression runs on supporting platforms, while all other
unusual-path cases run on macOS too.
Lists are sorted and canonical JSON is SHA-256 hashed. Git internals are not source.

Only these canonical harness metadata paths are excluded, using the selected
layout prefix: `feature_list.json`, `progress.md`, `manifest.json`, and `runs/**`
except `runs/RUN_TEMPLATE.md`. They are reserved runtime namespaces, not product
implementation locations. The Feature contract is separately fingerprinted;
protection of other lifecycle fields and role mutations belongs to F047/F048.
Same-named root files are ordinary source under hidden layout. SPEC, prompts,
schemas, provider configuration and bundled template code are source.

Ignored untracked `__pycache__` contents and `.pyc`/`.pyo` files are excluded.
Other ignored files, including ignored source/build paths, are included; tracked
cache/build/product files are always included outside the reserved metadata paths.
There is no broad `.gitignore` bypass and no user-controlled exclusion list.

Symlink targets are hashed without dereferencing, including dangling/external
links. Symlink ancestors are rejected, regular file reads use `O_NOFOLLOW`, and
nonregular files/submodules/nested Git repositories fail closed rather than silently omitting content.
Snapshotting is detection, not an atomic filesystem transaction: callers must keep
other writers idle; before/after equality detects persistent changes but cannot
prove that transient edits never occurred. Full process sandboxing and malicious
concurrent filesystem races are outside this contract.

## Trust and history

A receipt is an accidental-error integrity boundary, not authentication against a
process with arbitrary same-account filesystem access. The runner owns IDs,
commands, execution results and receipt assembly. Agent input is limited to the
captured assessment; the configured adapter must actually be an independent
Evaluator. Fake evaluator subprocesses test this protocol, not evaluator quality
or an external provider's behavior. Hashes do not establish semantic correctness.

`validate_receipt(receipt, workspace)` verifies historical internal integrity and
persisted artifacts without comparing an old snapshot to today's source. Later
Features may legitimately change code. `current=True` additionally requires the
live snapshot; pass the current `feature` to check its contract and `expected_run`
to bind finalization to a particular attempt. `build_receipt` always applies these
current checks. Old receipts must never stand in for a reopened Feature's new run.
Missing logs, run files or outcomes invalidate historical evidence. No historical
receipts are fabricated by F045 and no legacy completion state is migrated here.

## Current-run completion (F046)

Every newly started `work` or `work-fast` attempt requires receipts. Both modes use
`completion.finalize` and the same `mark_done(feature_id, receipt_path)` gate.
`--eval-only` remains an advisory review command; it cannot complete a Feature.
The orchestrator must itself be restarted after upgrading its runtime. An already
running older orchestrator cannot provide the new completion contract.

The runner creates `runs/<uuid>/handoff.json` before coding and links `active_run`
from the selected Feature. The handoff freezes the contract, attempt, required
commands and starting snapshot. Coding may change source. After coding, the runner
writes `coding.json` bound to the candidate snapshot and exclusive `run.json` with
the same UUID. Baseline uses the actual coding child stdout and successful exit;
stderr remains diagnostics in `coding.stderr`. Real Codex diagnostic output can
contain quoted `EVAL_PASS: Fxxx` templates and past verdicts (captured in the F045
run); those are never evaluator evidence. Provider-native notes still reject
EVAL_PASS markers. No global Markdown scan participates in completion.

For work-fast, use the command printed in the handoff, from the harness directory:

```bash
python3 orchestrator.py --record-coding F001 --run-id <active-uuid> --evidence-file runs/my-coding-note.md
make work-fast
```

The note contains `FAST_CODING_EVIDENCE: F001` and `CODING_PASS: F001` after the
implementation is ready. The CLI records the current source fingerprint; changing
source afterwards requires a new attempt. Old notes alone never trigger evaluation.
Additional checks are declared on the Feature as `required_commands`, an array of
`{"argv": ["python3", "test.py"], "timeout_seconds": 60}` objects. The first required
command is always project-root `./init.sh`. Commands are frozen at handoff, executed
without a shell, and captured by the runner, separately from evaluator assertions.

The evaluator bridge launches the configured independent evaluator adapter and
retains raw `provider.stdout` and `provider.stderr`. Its prompt requests exactly
`evaluation.schema.json` on stdout, with the supplied binding and one assessment
per zero-based acceptance index. This harness-owned adapter contract overrides the
legacy final EVAL_PASS text format **for receipt evaluation only**. No provider
JSONL fields, log tails or prose are parsed. Nonzero exits, prose-only PASS, missing
criteria, stale bindings, changed source or changed criteria reject the run.

A validated `receipt.json` is fsynced before the Feature links `completion_receipt`
and becomes done. Historical validation verifies the receipt, manifests and log
hashes without comparing every old source snapshot to today's repository. Resuming
an interrupted state write can reuse the persisted receipt only if the candidate
and live contract/source are still unchanged. Interrupted check/evaluator execution
without a receipt fails closed, keeps all files, and returns nonzero. The next
attempt gets a new UUID; inspect `failure.json` and `last_error` first. Human reopen
also requires a new run. No automatic rollback, deletion or commit occurs.

## Frozen compatibility policy

`completion-policy.json` is project-owned migration evidence. The template's own
legacy list is never installed in a project. Fresh installs get an empty list and
therefore enforce receipts from F001. The first installation/upgrade into a legacy
project freezes the exact identities of its existing done Features; later lifecycle
operations preserve this list byte-for-byte. Checks never create or expand it.
Do not delete it to attempt to re-enroll newer completions as legacy. Missing or
malformed policy fails validation; restore the original policy from durable history.

Unchanged frozen legacy identities retain their old evaluator-evidence policy.
Changed attempts or criteria cannot use that exemption. F047 permits only exact replay of appended observational Human Eval events over a consistent frozen human-acceptance history; edited/deleted history and current-scope rejection cannot use it. F043's
historical done plus rejected/reopen metadata is visibly reported as a legacy
contradiction, preserved without mutation, and cannot authorize a new completion.
This is an accidental-error integrity boundary, not protection against malicious
same-account writers who can forge both source and evidence. Lifecycle locking and
protected role write sets are separately scoped to F047 and F048.

Configured-provider smoke (requires the chosen provider's normal runtime access):

```bash
python3 scripts/smoke-completion-provider.py --config agent-provider.json --output runs/provider-smoke
```

This creates a real isolated Git fixture and runs work-fast through the configured
evaluator adapter, preserving its output for inspection. Fake-role tests prove our
state machine, not the provider's output contract. Do not claim provider verification
when runtime preflight fails.

## Dependency and lifecycle transactions (F047)

`depends_on` is an optional array of unique existing Feature IDs. Self edges,
non-string IDs, missing IDs and cycles fail state validation before lifecycle
mutation. Both baseline scheduling and work-fast resume require every dependency
to be done/passing, without rejected or pending-reopen metadata. A frozen legacy
contradiction is historical evidence only and is never a ready dependency.
Finalization rechecks readiness; changing dependencies cannot bypass the gate.

`state_store.py` is the shared lifecycle storage API for orchestrator and Human
Eval. `load` captures the exact file revision; `save` validates, compares that
revision, fsyncs a same-directory temporary file, atomically replaces the target,
and fsyncs its directory. Unknown fields, array order and history survive. A stale
revision fails rather than merging or overwriting another writer. Readers need no
lock and observe either complete old JSON or complete new JSON.

There are two permanent POSIX advisory lock inodes under `runs/`: an ownership
lock for a whole orchestrator round (or Human Eval command / record-coding command),
and a short replacement lock for compare-and-swap. Competing lifecycle commands
exit nonzero with `owner lock contention`; retry after the owner exits. Subprocess
verification and read-only state checks still work during ownership. Work-fast
releases ownership at handoff; recording coding and resuming reacquire it. Kernel
locks are released on process exit, including termination. Do not unlink a lock
file to recover: its presence does not mean it is locked. Network filesystems with
unverified flock/rename durability semantics are outside the tested platform
contract; tests exercise real local POSIX subprocesses on macOS/Linux.

A process interrupted before replacement leaves the old valid state and may leave
a dot-prefixed temporary file beside it. Preserve it for inspection; it is never
read as state or automatically promoted. Interruption after replacement may leave
the new valid state. Run/receipt validation decides whether a run can resume; it
never invents evidence. Human Eval writes a uniquely named feedback record before
state replacement, so an interrupted command can leave an unlinked record. Such a
record is not applied feedback until reflected in `human_acceptance.history`.

Only harness lifecycle commands change attempts, status, passes, active evidence
and human metadata. Human current-scope failure archives active run/receipt links
in `completion_history`, removes those live links and sets todo/reopen_pending.
Retry increments attempts, clears pending reopen and changes rejected to unreviewed
while retaining all feedback history. Independent new-requirement feedback cannot
cancel a pending reopen. New done plus rejected/reopen states fail validation and
completion; the exact frozen legacy identity remains diagnosed and untouched.
Old archived evidence cannot authorize the new run. Arbitrary direct role edits
and source write-set enforcement are the separate F048 boundary, not a claimed
security property of advisory locks.

Restart the coordinator after upgrading. The already-running F047 parent loaded
F046 code, so its own first round is not evidence of the new ownership guard.
Fresh-process regression fixtures exercise the guard; subsequent real rounds use
the new runtime. No completion-policy mutation or legacy metadata rewrite is part
of this change.

### Legacy observational feedback

The compatibility policy remains immutable. `legacy_matches` compares the frozen
completion identity and replays only newly appended `pass/current_feature` or
`fail/new_requirement` feedback over the original human metadata. Existing history
and unknown metadata must remain identical; the resulting status, feedback and
timestamp must exactly match that replay. A current-scope rejection, changed
criteria/attempt, edited history, or repaired-in-place contradictory legacy state
cannot pass this check. F043 therefore remains an exact historical exception.
Human Eval validates the proposed completion history before publishing state or
feedback records. Invalid transitions fail with recovery guidance and leave both
unchanged. A real current-scope rejection still reopens the original Feature and
requires a new independent evaluation. Receipt-era feedback continues to use its
original receipt integrity rules. This detects accidental lifecycle errors; it is
not authentication against a same-account writer who can forge all artifacts.

## Role change boundaries (F048, template 0.4.0)

New coordinators capture `runs/<run>/boundary.json` after their lifecycle update
and before coding. It freezes the entire Feature document (including unknown
fields, ordering, every contract and lifecycle field), the source snapshot, initial
dirty paths, and explicit path authorization. Coding may update canonical progress
and run notes, but must not edit feature_list.json, SPEC.md, QUALITY.md or the frozen
completion policy. Plan contract changes separately before starting a run.
Evaluator implementation edits are rejected, including new/deleted files and index
or mode changes. Both work modes and record-coding use the same checks. Required
checks do not authorize source changes. Missing boundaries fail closed on resume.

Pre-existing staged, unstaged, deleted and untracked source paths are protected by
default. Before a NEW run, repeat literal project-relative declarations as needed:

```bash
python3 orchestrator.py --work-fast --adopt-dirty src/worker.py --allow-path src --allow-path test
```

`--adopt-dirty PATH` explicitly permits further changes to initial dirty paths at
or beneath PATH; it does not erase or commit prior work. `--allow-path PATH` is an
optional additional restriction on all source changes, including clean, new and
deleted paths. An empty allowlist permits no source changes. No globs, absolute
paths, dot/traversal components or Git-internal paths are allowed. In hidden layout
run the command from `.agent-harness`, but paths still start at the project root:
use `src` for product source and `.agent-harness/scripts` for harness source.
Adoption cannot override protected contracts/state. Declarations are immutable on
resume and cannot be supplied after a violation. For this template's intentionally
uncommitted hardening batch, adopt only the prior dirty implementation paths needed
by the next Feature; retain unrelated prior work unchanged. No forced commit.

`changes.json` contains the full attributable before/after bytes (base64), textual
diff and snapshot/index/mode metadata, including untracked additions and deletions.
The baseline is the handoff, not HEAD, so adopted planning edits remain visible as
the starting content. Evaluators must read it and provide an explicit scope
relevance judgment even without an allowlist. The rendered JSON adds
`"scope":{"status":"pass|fail","reason":"concrete relevance assessment"}`.
The bridge retains raw provider output, records its hash and the changes hash in
`scope.json`, and emits the historical per-criterion evaluation shape to the receipt
runner. Missing/failed scope judgments reject completion. Historical receipts keep
their existing schema; boundary-era receipts carry an explicit hashed role_boundary enrollment binding for boundary-required.json, boundary.json, changes.json and scope.json. Missing sidecars cannot downgrade them to legacy validation.

Violations write exact paths/Feature IDs and reasons to `violation-<id>.json` and
reject the run. The tree is preserved: never auto-stash, rollback, delete user files,
or force a commit. Inspect the report and manually restore unauthorized state or
contract edits. Malformed Feature JSON may require manual repair before any command
can validate it; it is never silently replaced from the captured copy. A rejected
run cannot complete or resume. Explicitly archive it before a new coding round:

```bash
python3 orchestrator.py --restart-run F001 --run-id <rejected-run-id>
python3 orchestrator.py --work-fast --adopt-dirty src/worker.py
```

Restart preserves attempts/history and files, removes live completion reuse and
records the operator action. A blocked Feature can be explicitly restarted;
existing retry limits still apply (use the documented `--max-attempts` deliberately
if exhausted). A new UUID and boundary are captured before the next coding handoff.
No authorization can retroactively make a rejected run pass.

Trust exclusions remain Git internals, canonical progress/manifest, canonical run
artifacts except RUN_TEMPLATE.md, and ignored untracked Python bytecode caches.
Canonical Feature state is excluded from source hashing but now independently
compared in full. Source guards do not protect their own evidence from a malicious
same-account writer. This is post-role error detection, not a filesystem sandbox.
Restart the coordinator after upgrading: the parent already executing the first
F048 implementation loaded F047 code and cannot retrospectively enforce F048.
Fresh-process adversarial tests establish new guard behavior; subsequent real runs
must start with the upgraded coordinator, not reuse a pre-boundary handoff.
