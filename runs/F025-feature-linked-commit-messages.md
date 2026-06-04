# Run Record: F025 - Add feature-linked commit message rules

## Summary

- Date: 2026-06-04
- Agent role: Coding Agent
- Feature: F025
- Result: Passed

## Repository State

- Starting commit: 32c4edd
- Ending commit: pending
- Working tree status: modified

## Commands Run

```bash
./init.sh
python3 -m unittest test.contract.test_repository_contract
```

## Evidence

- `docs/commit-messages.md` defines the required feature-linked subject format.
- `AGENTS.md`, `skills/ai-agent-harness/SKILL.md`, and `skills/ai-agent-harness/references/workflows.md` require approved feature commits to include feature IDs.
- Contract tests verify commit-message governance across docs, prompts, skill files, initializer file lists, and bundled template files.
- Capability gaps: none

## Failure Analysis

- Failure domain: n/a
- Failure summary: none
- Harness improvement: Added feature-linked commit message governance.
- Follow-up feature: none

## Evaluator Result

```text
EVAL_PASS: F025
```

## Follow-Up

- Consider a future optional commit-msg hook if users want local Git enforcement.
