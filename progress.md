# Progress

## Current System Status

The minimal AI agent harness template is runnable.

Implemented components:

- Durable agent rules in `AGENTS.md`.
- Repository knowledge map under `docs/`.
- Real-world usage notes in `docs/real-world-usage.md`.
- Evaluator rubric in `QUALITY.md`.
- Run artifact template under `runs/`.
- Failure-domain improvement loop in `docs/failure-domains.md` and `scripts/check-failure-domains.sh`.
- Practiced AGENTS guardrails for state safety, external behavior verification, tool schema handling, and anti-pattern prevention.
- Requirements in `SPEC.md`.
- Feature state in `feature_list.json`.
- Feature schema in `schemas/feature_list.schema.json`.
- Prompt templates in `prompts/`.
- Validation scripts in `scripts/`.
- Clean-state reset command in `scripts/clean-state.py` and `make clean`.
- Layered test coverage under `test/unit`, `test/contract`, and `test/smoke`.
- Contract tests that lock AI agent obligations and harness boundaries.
- Verification planning in `test_plan.md`.
- Root verification wrapper at `./init.sh`.
- Make targets in `Makefile`.
- GitHub Actions workflow in `.github/workflows/ci.yml`.
- OSS readiness files: `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, and issue templates.
- Vendor-neutral lightweight orchestrator in `orchestrator.py`.
- Explicit Coding Agent and Evaluator Agent adapters under `scripts/`.
- Distributable AI Agent Harness skill under `skills/ai-agent-harness/` with initializer, workflow guidance, and explicit finalize-and-commit rules.
- Manifest-aware skill initializer checks for new, adopt, repair, and check modes, including drift diagnostics and runnable installed-harness validation.
- README guidance that separates installing the AI Agent Harness skill, invoking the installed skill, and manually running the fallback initializer script.
- Portable Codex, Claude Code, and Cursor installation guidance for the AI Agent Harness skill without machine-specific absolute paths.
- Capability-gap governance that requires missing tools, permissions, generators, dependencies, services, credentials, runtime settings, CI resources, and verification fixtures to become durable project capabilities or tracked blocked/follow-up work.
- Example-boundary governance that keeps default examples as harness demonstrations instead of project implementation shortcuts.
- Installation layout profiles, with hidden layout as the default for user projects and visible layout retained for template maintenance.
- Feature-decomposition governance that requires broad requirements to become independently verifiable feature entries instead of over-bundled features.
- Feature-linked commit message governance that ties approved feature commits back to `feature_list.json`.
- Installer executable-bit repair that makes generated shell entrypoints executable even when source template modes are lost.
- Project recovery init governance so installed projects distinguish harness verification from the root project recovery contract.
- Minspec-to-SPEC normalization governance so planners must clarify goal, scope, flows, constraints, ambiguities, capabilities, implementation paths, and verification before appending features.
- Evaluator-evidence guardrail so features cannot be marked done without durable `EVAL_PASS: Fxxx` run evidence.
- Orchestrator-first work entrypoint so implementation and evaluation default to `make work` instead of manual state edits, with adapter-unavailable flows failing closed.
- Explicit agent-provider configuration so orchestrator adapters can use Codex, Claude Code, Cursor Agent, or a custom provider without unsafe guessing.
- New-project flow guide with a one-screen Mermaid diagram linking skill initialization, minspec planning, runnable skeleton, provider setup, orchestrator work, evaluator evidence, init verification, and commit approval.
- Final role verdict normalization so historical run evidence echoed by agents cannot override final Coding Agent or Evaluator Agent pass/fail lines, and structured pass verdicts can recover provider exit-code contradictions.
- Provider runtime preflight checks so configured agent providers can report permission gaps before feature state is mutated and outer agents can request user-approved escalation.
- Hidden-layout work-directory guidance so agents run `make -C .agent-harness work` from installed project roots instead of treating a missing root `Makefile` as orchestrator unavailability.
- Evaluator-gated `make work-fast`, including fast handoff/evidence parsing, mandatory evaluator-child gating, documentation, tests, bundled template sync, and evaluator pass evidence.
- Preferred interactive work-fast guidance in AGENTS instructions, including visible-layout and generated hidden-layout command choices.
- Installed-harness upgrade workflow so global skill/template updates can be safely propagated into already installed hidden-layout projects.
- Tiny dependency-free Python CLI example in `examples/tiny-cli/`.
- Dependency-free Go server example in `examples/go-server/`.

## Last Completed Feature

`F048` - Reject completion after unauthorized role changes. Accepted through the new guarded coordinator on attempt 2; receipt: runs/5770fe94333346629908d706d81e9aea/receipt.json. The authorized F045-F048 completion-hardening batch is complete at template version 0.4.0.

## Next Feature

No remaining work in the authorized hardening batch. `F011` remains the unchanged P2 backlog item and was not included. The user approved committing and pushing the F045-F048 batch on 2026-09-06; earlier uncommitted checkpoints below are historical. New rounds use the guarded workflow documented in docs/run-evidence.md, with explicit pre-coding dirty-path adoption only when needed.

## Known Issues

- The template orchestrator is intentionally lightweight and vendor-neutral.
- `agent-provider.json` is intentionally absent by default; copy `agent-provider.example.json` and select an explicit provider before real `make work` execution.
- `F011` remains a P2 backlog item and should not preempt the new P0 orchestrator-first work.
- `F036` is a P0 A/B workflow experiment: keep `make work` as the two-child-process baseline and add `make work-fast` with provider-native coding plus mandatory cold-start evaluator child gating.
- The former `0.3.8`/`0.3.9` template-version source inconsistency was resolved independently in F043.

## Recovery Notes

- F030 used explicit manual fallback because role adapters are still template adapters until F031.
- `make work` was verified to run the startup protocol and fail closed before mutating F030 state when adapters are unconfigured.
- F031 verified Codex command shape with `codex exec --help`; Claude Code and Cursor Agent command shapes remain intentionally unconfigured until verified on a machine that has those CLIs.
- F032 added `docs/new-project-flow.md` and README onboarding link so new users can see the full skill-assisted path at a glance.
- F033 fixed final role verdict parsing and synchronized the fix into the bundled skill template; downstream installed projects should receive the same harness file update.
- F034 added provider runtime preflight commands and a machine-readable `PROVIDER_RUNTIME_PERMISSION_REQUIRED` marker so outer agents can ask users to approve escalated provider runtime execution.
- F035 used explicit manual fallback because provider adapters are intentionally unconfigured in this template checkout. It clarified that hidden-layout installs should use `make -C .agent-harness work` from the project root or `make work` inside `.agent-harness/`, synchronized the bundled skill template, bumped the template version to 0.3.4, and added contract plus initializer coverage.
- F036 planning was added on branch `codex-work-fast-flow`. The first orchestrated `make work` attempt received approved escalated runtime execution but failed before implementation because the local Codex provider command started outside a trusted repository root: `Not inside a trusted directory and --skip-git-repo-check was not specified.` The failure is recorded in `runs/20260707T095608Z-F036-failure.md`; retry requires correcting local provider working directory/trust configuration rather than manual feature implementation.
- F036 was completed through the orchestrator after the local provider command was corrected. Coding evidence is recorded in `runs/20260707T152121Z-F036-work-fast-coding.md`, evaluator approval is recorded as `EVAL_PASS: F036` in `runs/20260707T152614Z-F036-evaluation.md`, and final `./init.sh` plus `scripts/validate-feature.sh F036` passed.
- F037 completed through work-fast provider-native implementation. Root and bundled template AGENTS now tell agents to default to evaluator-gated `work-fast` for interactive user-led development while preserving baseline `make work` for explicit full two-child-process, unattended, or batch runs. A first evaluator rerun exposed a work-fast handoff/evidence parser false positive and recorded `runs/20260709T035347Z-F037-failure.md`; the coding pass fixed that parser edge case and updated the coding evidence at `runs/20260709T035143Z-F037-work-fast-coding.md`. Evaluator approval is recorded as `EVAL_PASS: F037` in `runs/20260709T040001Z-F037-evaluation.md`, and final `./init.sh` plus `scripts/validate-feature.sh F037` passed.
- F038 was planned after a real hidden-layout project repair showed a lifecycle gap: the global skill had `work-fast`, but the installed project-local `.agent-harness` remained on an older template without the target. The planned fix adds an explicit upgrade workflow and reduces nested template vendoring in installed projects.
- F038 completed through work-fast provider-native implementation. The initializer now has explicit `upgrade` mode, hidden-layout harness runtime files are upgradeable without overwriting root project recovery entrypoints, obsolete nested template assets are removed during upgrade, and the template version was bumped to 0.3.7. Coding evidence is recorded in `runs/20260709T061705Z-F038-work-fast-coding.md`, evaluator approval is recorded as `EVAL_PASS: F038` in `runs/20260709T062151Z-F038-evaluation.md`, and final `./init.sh` plus `scripts/validate-feature.sh F038` passed.
- A follow-up 0.3.8 repair fixed installed-project contract tests so hidden-layout installs no longer require the removed nested `skills/ai-agent-harness/assets/template` tree.
- F039/F040 planning adds an optional Human Eval layer that can happen after multiple Features are automatically complete. Unmet original scope must reopen the original Feature; genuinely new requirements remain planning inputs and are not auto-appended. F040 depends on F039.
- F039 coding added optional Human Eval recording, current-scope reopen behavior, non-blocking new-requirement recording, orchestrator reopen selection, evidence-parser hardening, contract coverage, and bundled template synchronization. Coding evidence is recorded in `runs/20260811T081020Z-F039-work-fast-coding.md`; evaluator approval is recorded in `runs/20260811T082002Z-F039-evaluation.md`.
- F039 had two evaluator-gated failures before passing: missing contract coverage and a work-fast evidence-parser false positive. Both are recorded in `runs/` and fixed with regression coverage. F040 remains the next independent feature for deferred batch Human Eval.
- F040 coding added JSON batch Human Eval input, mixed-outcome routing, batch run evidence, Make targets, tests, and bundled template synchronization. Coding evidence is recorded in `runs/20260811T092000Z-F040-work-fast-coding.md`; F040 remains incomplete until a separate Evaluator Agent records `EVAL_PASS: F040`.
- F040 evaluator feedback identified missing smoke coverage; subprocess smoke coverage and explicit batch pass tests now pass. Rerun the separate Evaluator Agent for F040.
- F040 passed after adding the required subprocess smoke coverage. Evaluator approval is recorded in `runs/20260811T092600Z-F040-evaluation.md`.
- F041 synchronized Human Eval lifecycle rules into the distributable skill and bundled template, with contract parity coverage. Coding evidence is recorded in `runs/20260811T093600Z-F041-work-fast-coding.md`; evaluator approval is recorded in `runs/20260811T093820Z-F041-evaluation.md`. F011 remains the next unfinished feature.
- F042 planning defined provider paths relative to the adapter-selected provider workspace and split template-version parity into F043. Work-fast coding added layout-aware prompt rendering for Planning, Coding, Evaluator, Continue, and Work-fast; resolved provider `cwd` relative to `agent-provider.json` for both preflight and real execution; generated hidden examples with `cwd: ".."`; synchronized the distributable/bundled template surfaces; and added fake-provider plus stale-root-sentinel regressions. The coding phase correctly left F042 incomplete pending independent evaluation.
- F042 passed independent evaluation. Evaluator approval is recorded in `runs/20260813T145836Z-F042-evaluation.md`; the evaluator reran unit, contract, harness, full init, and selected-feature validation before the orchestrator marked F042 done.
- F043 coding aligned the distributable and bundled initializer with manifest version `0.3.9`, changed initializer fixtures to derive their expected version from `.agent-harness-template.json`, and added a contract test that rejects drift between manifest, initializer, bundled initializer, and bundled tests. The coding phase correctly left F043 incomplete pending independent evaluation.
- F043 passed independent evaluation. Evaluator approval is recorded in `runs/20260813T150520Z-F043-evaluation.md`; the orchestrator marked the Feature done only after the durable pass record existed.
- F043 was reopened after global skill installation exposed a stale bundled `.agent-harness-template.json` at `0.3.8`. The cold-start evaluator rejected the old implementation and required the bundled manifest plus version-parity contract coverage to be repaired before reevaluation.

- F044 planned from downstream F044 numbering contamination: initializer resets feature/progress state but copies the template product SPEC. Failure domain: agent_workflow_gap. The durable fix is fresh project scaffolding and preservation regressions; existing downstream IDs will not be rewritten.

- F044 uses adapter-unavailable manual fallback after normal and escalated work-fast runtime preflights failed before dispatch. See runs/20260905T033800Z-F044-manual-fallback.md. Attempts=1; separate cold-start evaluation is required.

- F044 coding completed: fresh SPEC scaffolds, project-local numbering guidance, preservation across lifecycle modes, dry-run safety, and bundled regression coverage. Full ./init.sh passed (30 unit, 32 contract, 11 harness, 2 smoke); independent evaluator approval is pending. See runs/20260905T034300Z-F044-coding.md.

- F044 passed independent cold-start evaluation in runs/20260905T034449Z-F044-evaluation.md, including full init, selected-feature validation, all-mode dry-run probes, and bundle parity. Manual fallback completion is backed by this evaluator evidence. Existing downstream projects and the globally installed skill were not modified.

- F044 final post-completion ./init.sh passed with evaluator evidence present; all 43 pre-existing feature entries were verified unchanged. The evaluator run metadata labels were corrected to the check-failure-domains contract before final verification. No commit performed.

## Completion hardening plan — 2026-09-05

- User approved planning and implementing the discussed completion and post-run hard constraints, with a pre-change tag first. Annotated tag `pre-completion-hardening-20260905` targets clean commit `7929e0f`. No implementation commits or pushes are authorized by this request.
- Appended normalized SPEC and F045–F048 without changing existing Feature state. Each coding round must implement only its selected Feature and receive separate evaluator approval.
- Provider preflight initially failed under the sandbox on the Codex local state database/app-server; escalated preflight reached the provider but failed with the old configured gpt-5.4. Investigating real command output before changing project-local configuration.
- Historical F043 still has done plus rejected/reopen_pending metadata. Preserve its record; the new compatibility policy must surface the discrepancy and prevent it being accepted as current-run evidence.

- Provider recovery verified: the installed desktop CLI 0.153.3 with the existing global model gpt-6-astra returned PROVIDER_OK; project-local Codex config now uses that executable/model. Evidence: runs/20260905-provider-runtime-recovery.md. No global settings changed.

### F045 coding handoff (2026-09-05)

- Implemented independently testable run manifests, Git source snapshots, strict
  receipt/evaluation schemas, non-shell runner command capture and per-criterion
  evaluator validation in `scripts/run_evidence.py`.
- Root and bundled runtime, schemas, docs, init requirements and tests are synced.
- This session is the selected F045 Coding Agent at attempt 1; it does not invoke
  a nested orchestrator or write evaluator approval. F045 remains in progress.
- Evidence and verification: `runs/20260905-F045-coding.md`. Existing planning,
  provider configuration and recovery-note changes were preserved.
- F046 owns actual completion-gate enrollment/migration; F047/F048 remain untouched.


### F046 coding handoff (2026-09-05)

- This is the selected baseline Coding Agent at attempt 1, not a nested orchestrator
  run. Implemented only F046. Existing F045, planning and provider changes remain.
- Both work modes now use UUID handoffs, snapshot-bound coding receipts, runner
  recovery/declared checks, a configured independent JSON evaluator bridge and one
  receipt-before-done gate. Resume, failure and frozen legacy migration are covered
  by real Git and child-process tests. No global PASS scan completes new runs.
- Fresh installations receive an empty completion policy; older installations freeze
  only their own previous completions. F043's contradictory historical metadata is
  surfaced without changing it. The distributable and bundled surfaces are synced.
- Full init passed during implementation. Final selected-feature validation and
  exact test counts are recorded in `runs/20260905-F046-coding.md`.
- Capability gap: real configured Codex evaluator runtime preflight fails in this
  Coding Agent sandbox with readonly state DB and app-server Operation not permitted.
  The durable smoke script reproduced this; raw output is retained under
  `runs/20260905-F046-provider-smoke/`. Do not replace it with fake-role evidence.
- F046 remains incomplete. The coordinating process must run the documented real
  provider smoke with its already-authorized runtime access, then dispatch a separate
  Evaluator Agent. It must restart into the new orchestrator to enroll completion;
  an older already-running orchestrator's plain PASS cannot create a valid receipt.
- Failure domain: capability_gap. Harness improvement: added reproducible provider
  smoke and retained logs; no weakened criteria or local-only provider workaround.
  No examples, global configuration, commit, stage, or F047/F048 implementation.

## Recovery checkpoint — completion hardening paused for explicit provider approval

- F045 is independently accepted and done. F046 attempt 1 returned CODING_FAIL on a capability gap; the legacy coordinator kept it todo/false. F047/F048 have not started. All original 44 Feature entries remain byte-equivalent as parsed JSON to the pre-change tag.
- The user allowed Codex/config upgrades. Project-local configuration uses the already installed verified desktop CLI 0.153.3 and gpt-6-astra; no global upgrade was needed.
- Automatic approval review separately rejected the isolated real-provider smoke twice, even after inspecting its copied scripts/schemas/prompts/orchestrator and credential-free config. It requires explicit user permission for that source payload to the current OpenAI/Codex evaluator. The coordinating task asked this exact question via the async input tool; no reply has been received at this checkpoint. Do not retry the rejected smoke indirectly.
- After explicit approval, run scripts/smoke-completion-provider.py with agent-provider.json and a new output directory under runs/, using approved runtime access. Then resume F046 through the NEW coordinator (prefer work-fast to record existing completed coding without rerunning implementation), record active-run coding evidence, and obtain an independent current-snapshot receipt. The old F046 parent has exited; do not use legacy PASS text to mark done.
- Follow with one-feature F047 and F048 rounds. Keep all prior uncommitted implementation/planning changes; do not commit or push unless requested.
- Post-failure ./init.sh passed (log /tmp/harness-F046-post-failure-init.log), git diff --check passed, tag still targets 7929e0f. F046 coding/local evidence: runs/20260905-F046-coding.md. Recovery/permission review: runs/20260905-F046-review-notes.md and runs/20260905T113237Z-F046-failure.md.

- Resume authorization (2026-09-05): user replied continue to the explicit payload/destination request; automatic approval accepted the isolated configured-provider smoke. Startup verification passed at /tmp/harness-resume-approved-init.log. No feature completion inferred from authorization.

- Explicit repository-context authorization confirmed: user answered 确认 to sending this repository code, docs, tests, task state and run evidence to the configured OpenAI/Codex Coding/Evaluator subprocesses for F046-F048. Automatic review accepted make work-fast. Preserve this scope through subsequent rounds; no commit or push authorization was requested.

- F046 independent evaluator accepted every criterion; the new coordinator persisted the receipt then marked done. Actual provider JSON and review/check evidence are under runs/0a849903224541bb910486c1eaba3236/. No legacy PASS scan or manual done edit was used.

## F047 coding handoff — run d8f37ba8e15843889367969a7e56a907

- Implemented dependency graph validation/readiness in baseline and fast resume,
  shared POSIX ownership plus short atomic compare-and-swap state writes, and
  Human Eval evidence archival/reopen/retry lifecycle consistency. Unknown fields,
  ordering, attempts and feedback history are preserved; frozen F043 is diagnosed
  without rewriting its history or completion policy.
- Runtime, schema, tests, installer requirement and bundled copies are synchronized.
  Actual competing orchestrator/Human Eval subprocesses cover visible and hidden
  layouts; real writer interruption and stale-writer tests cover storage behavior.
- This is the dispatched baseline Coding Agent, not manual fallback. F047 lifecycle
  fields remain runner-owned and unchanged by this coding session. Independent
  evaluation/current-run receipt is still required before F047 completion.
- The current parent loaded F046 runtime before this edit; restart the coordinator
  for F048 so the new ownership behavior applies to that round. F048 still owns
  arbitrary role edits/write-set enforcement and final template version sync.
- Failure domain: contract_gap (the targeted pre-existing lifecycle/dependency gap).
  Harness improvement: durable state API, graph checks, recovery documentation and
  real subprocess regression coverage. No missing required capability, example
  modification, commit, staging, global configuration change or policy mutation.

- F047 coordinating review found supported Human Eval pass on a frozen legacy completion exits 0 but then fails completion history validation. Reproducer and required cases: runs/d8f37ba8e15843889367969a7e56a907/coordinator-review.md. Resolve this before coding acceptance; keep frozen policy/original state intact.
- Final verification: scripts/validate-feature.sh F047 exited 0, including full
  ./init.sh (59 unit tests with one existing optional skip; contract, harness and
  smoke layers passed). Coding evidence: runs/d8f37ba8e15843889367969a7e56a907/F047-coding.md.

- F047 attempt 1 was independently rejected for legacy Human Eval feedback invalidating history. Attempt 2 uses provider-native work-fast on run bf46e6a2b8014c02bc6cdaa3feda1835. Implemented strict replay of appended observational feedback over immutable frozen legacy identity and pre-publication history validation; unsupported transitions leave state/records unchanged. Added real subprocess regressions, synchronized bundle, and retained prior rejection evidence. Final validation and independent reevaluation pending.

- F047 attempt 2 independently accepted all criteria after legacy feedback repair. Runner persisted receipt before done. Start F048 from a new coordinator process to activate shared ownership/state transactions; preserve all previous uncommitted work and original 44 entries.

- F048 coordinating review: real Git proves diff HEAD misses pre-existing staged/unstaged cancellation. See runs/3211a673a7e04b68a8a7f7c2ad93eb0f/coordinator-review.md before coding completion; union staged and unstaged paths, add regression. Also account for old parent/new scope-protocol self-hosting.

- F048 coding implements protected full Feature state and contract checks, initial
  dirty staged/unstaged/untracked union, pre-handoff --adopt-dirty and --allow-path,
  attributable full changes, mandatory evaluator scope relevance, receipt-hashed
  boundary enrollment, durable violations and explicit --restart-run recovery.
  All lifecycle fields and prior uncommitted Feature work remain runner-owned.
  Runtime/docs/prompts/skill/tests/bundled copies and version sources now use 0.4.0.
  Real Git/subprocess adversarial tests pass (7 groups, both modes/layouts).
  Coordinating review's staged/worktree cancellation and missing-sidecar cases are
  covered. The first full init overlapped continued template edits and its installer
  check detected real template drift; rerunning after source stabilization.
  Failure domain: test_gap (verification overlapped edits); harness improvement:
  perform final distribution verification only after source stabilization. No
  missing runtime capability or example-boundary changes. Final full selected
  validation and independent evaluator are pending; old loaded parent cannot claim
  F048 guard enrollment for its own already-started run. See coordinator-response.md
  under runs/3211a673a7e04b68a8a7f7c2ad93eb0f for provider scope smoke handoff.
- F048 final coding validation passed: scripts/validate-feature.sh F048 exited 0,
  including full ./init.sh (69 unit tests with one existing optional skip, 33
  contract, 12 installer/harness, 2 smoke tests, Python/Go examples). Coding evidence:
  runs/3211a673a7e04b68a8a7f7c2ad93eb0f/F048-coding.md. No lifecycle fields changed;
  separate evaluator and coordinated provider scope smoke remain pending.

- F048 new-runtime real configured Codex smoke passed, including explicit scope assessment and role_boundary-hashed receipt: runs/20260905-F048-provider-smoke. Actual Feature independent evaluation is still pending.

- F048 attempt 1 independent Evaluator passed all five criteria, but the pre-upgrade parent used the old exact-property schema validator and could not validate the newly optional role_boundary property at final receipt assembly ($: missing or unknown fields). No receipt/done was produced. This is the documented self-hosted runtime upgrade boundary; next action is a fresh work-fast round with the new coordinator, review existing implementation without further source changes, and fresh guarded independent evaluation. Do not reuse the old verdict as a new receipt. New-runtime real Provider scope smoke already passed.

- Final explicit authorization resolved: user selected “我授权上述 F048 仓库数据发送至 OpenAI/Codex，完成最终验收”; automatic approval accepted the exact make work-fast command. Current run remains 5770fe94333346629908d706d81e9aea with unchanged source and no dirty adoption.

## Completion-hardening batch accepted

- F045 independently accepted primitive run evidence (runs/20260905-F045-evaluation.md).
- F046 accepted current-run completion receipt (runs/0a849903224541bb910486c1eaba3236/receipt.json).
- F047 accepted dependency/lifecycle transactions and legacy feedback repair (runs/bf46e6a2b8014c02bc6cdaa3feda1835/receipt.json).
- F048 accepted protected writes and scope-bound evidence using the new coordinator (runs/5770fe94333346629908d706d81e9aea/receipt.json).
- Template and initializer version sources are 0.4.0. Original 44 Feature entries remain unchanged. F043's frozen historical contradiction remains visible without mutation.
- Real configured-provider smokes passed for receipt JSON and the new scope/boundary protocol. Project-local Codex configuration was repaired using the installed desktop CLI; no global upgrade was needed.
- Pre-change annotated tag pre-completion-hardening-20260905 still targets 7929e0fe9d654dc6f0ae87d048979a4c305ce117. No staging, commit, push, reset, stash or rollback.
- Final post-completion ./init.sh passed (exit 0); durable log: runs/20260905-completion-hardening-final-init.log. Final diff check passed; 33 changed root/bundle pairs are byte-identical; index remains unchanged.

- 2026-09-06 finalize: user approved committing and pushing the F045-F048 batch. Pre-commit ./init.sh passed; log: runs/20260906-precommit-init.log. origin/main matched local HEAD before commit. Runtime lock files are excluded from staging; source, distribution and durable evaluator receipts are included.
