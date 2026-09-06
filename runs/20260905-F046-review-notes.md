# F046 concurrent implementation review

## Summary
- Agent role: coordinating implementation reviewer
- Feature: F046
- Result: review input; not an evaluator verdict

## Evidence
The actual F045 baseline log /tmp/harness-F045-work.log contains exact `EVAL_PASS: Fxxx` template lines in the CODING child stderr before that child exits (lines 1513 and 3351), because the child reads AGENTS/prompts. Its actual coding verdict is CODING_PASS: F045. The current F046 draft completion.record_coding rejects ANY output line beginning EVAL_PASS:, including unrelated/template historical text, while run_current_round passes role_output(coding), combining stdout and stderr. This will reject ordinary real baseline coding despite successful coding and despite the new independent evaluator gate.

## Requested regression
Before accepting F046, ensure baseline coding evidence accepts real-shaped captured diagnostic/template/history output while deriving only the actual coding verdict from the documented role channel. Preserve strict run binding and do not use coding output as evaluator evidence. Provider-native hand-authored evidence may retain its anti-spoofing rule. Add regression using the real-shaped separation of stdout final CODING_PASS and stderr echoed EVAL_PASS: Fxxx/template text; document the channel contract instead of weakening independent evaluation.

## Failure Analysis
- Failure domain: external_behavior_gap
- Failure summary: combined provider diagnostics can contain evaluator marker examples and are not a pure coding-evidence document.
- Harness improvement: cover the real captured diagnostic shape in F046 tests and separate trusted coding verdict handling from independent evaluator provenance.

This note does not mark F046 complete or change acceptance criteria.

## Self-hosting rollout boundary
The outer make work process for F046 was launched before F046 changed orchestrator.py; it is still executing the old in-memory mark_done(feature_id) path. The frozen root policy currently lists only completed F001–F045 (excluding unfinished F011). When that old parent marks F046 done after legacy evaluation, current init will require a F046 receipt. Do not fabricate a legacy entry or prospective completion. Ensure the selected F046 receives a real independent current-snapshot receipt, or explicitly hand off a recovery/re-evaluation through the new coordinator before the outer task proceeds to F047. Preserve all other Feature state. This is a rollout concern, not permission to skip the new gate.

## Pending explicit permission: real provider smoke
The coordinating task requested escalated execution of scripts/smoke-completion-provider.py twice. Automatic approval review rejected it, including after inspecting copied source/config scope. Its stated reason is that repository-derived scripts, schemas, prompts and orchestrator may be transmitted to the configured external OpenAI/Codex evaluator without sufficiently explicit payload/destination authorization. A concise explicit user question is pending in the coordinating task. DO NOT retry this smoke via another command, normal sandbox, child process, or other indirect route until that approval arrives. Continue local fake-role/Git/installation tests. This is not evaluator evidence and must not be treated as a successful real-provider smoke.

## Authorized real-provider result

The user confirmed the explicitly scoped fixture payload/destination request. The escalated real configured-provider smoke completed with exit 0. Artifact root: runs/20260905-F046-coordinator-provider-smoke. The synthetic Feature F001 completed on run 3071ac1cfa4c4571b8701b20182fb85c; the runner created receipt.json and verify_history succeeded before the temporary fixture was removed. This proves the configured Codex evaluator can return the harness JSON assessment protocol. It does not accept actual Feature F046.

Starting actual repository make work-fast was then rejected by automatic approval review because its broader repository context was outside the narrowly authorized fixture payload. No process was launched and no attempt was consumed. A follow-up authorization request explicitly covers actual repository code/docs/tests/state/run evidence for F046-F048. Do not execute equivalent external calls while that request is pending.
