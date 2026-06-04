# Run Record: F021 - Add capability gap governance

## Summary

- Date: 2026-06-04
- Agent role: Coding Agent
- Feature: F021
- Result: Passed

## Repository State

- Starting commit: ae3175d
- Ending commit: pending
- Working tree status: modified

## Commands Run

```bash
./init.sh
rg -n "0\.2\.0" . -S
rg -n "capability-gaps|Capability Gap|capability_gap|generated bindings|local-only environment" AGENTS.md SPEC.md QUALITY.md docs prompts runs scripts skills test -S
```

## Evidence

- Tests: `./init.sh` passed with 21 validated features, 17 contract tests, 4 harness tests, 8 unit tests, and 1 smoke test.
- Logs: Verification output showed `init verification passed`.
- Screenshots or traces: Not applicable.
- External behavior verification: Not applicable; this change codifies harness behavior rather than depending on a new external tool schema.
- Capability gaps: The original observed gaps were missing code generation/tooling and Go build cache setup. The new rules require those to become durable project capabilities, blocked work, or follow-up features instead of local-only bypasses.

## Failure Analysis

- Failure domain: n/a
- Failure summary: none
- Harness improvement: Added capability-gap governance in `AGENTS.md`, `docs/capability-gaps.md`, prompts, `QUALITY.md`, failure domains, run template, skill workflows, initializer checks, bundled template, and contract tests.
- Follow-up feature: none

## Files Changed

- `AGENTS.md`
- `SPEC.md`
- `QUALITY.md`
- `docs/capability-gaps.md`
- `docs/README.md`
- `docs/agent-workflow.md`
- `docs/failure-domains.md`
- `prompts/plan.md`
- `prompts/work.md`
- `prompts/evaluate.md`
- `prompts/continue.md`
- `runs/RUN_TEMPLATE.md`
- `scripts/init.sh`
- `skills/ai-agent-harness/`
- `test/contract/test_repository_contract.py`
- `test/harness/test_skill_initializer.py`
- `feature_list.json`
- `progress.md`

## Evaluator Result

```text
EVAL_PASS: F021
```

## Follow-Up

- Continue collecting real manual-acceptance failures and convert repeated classes into durable harness rules or tests.
