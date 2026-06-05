# Run Record: F032 - new project flow guide

## Summary

- Date: 2026-06-05
- Agent role: Evaluator Agent
- Feature: F032
- Result: pass

## Repository State

- Starting commit: f822ac7
- Ending commit: uncommitted working tree
- Working tree status: F032 documentation changes present; local `agent-provider.json` remains untracked

## Commands Run

```bash
./init.sh
python3 -m unittest discover -s test/contract -p 'test_*.py'
scripts/validate-feature.sh F032
```

## Evidence

- `docs/new-project-flow.md` documents the end-to-end new project flow from skill invocation through approved commit.
- The guide includes a Mermaid `flowchart TD` diagram showing skill initialization, minspec input, SPEC normalization, feature decomposition, runnable skeleton, provider choice, `make work`, Coding Agent work, Evaluator Agent verification, `EVAL_PASS: Fxxx`, root `./init.sh`, and human commit approval.
- The guide lists required human inputs: project/install choice, conflict decisions, minspec, clarifications, runtime choices, provider choice, execution approval, and commit approval.
- `README.md` links to the guide near Quick Start.
- `docs/README.md`, `SPEC.md`, `scripts/init.sh`, contract tests, and bundled template files were updated consistently.
- Contract tests verify the README link, docs index entry, Mermaid diagram, key flow nodes, SPEC mention, init check, and bundled template synchronization.

## Failure Analysis

- Failure domain:
- Failure summary:
- Harness improvement: F032 improves onboarding by making the skill-assisted flow visible as a single diagram and short guide.
- Follow-up feature:

## Files Changed

- `README.md`
- `SPEC.md`
- `docs/README.md`
- `docs/new-project-flow.md`
- `feature_list.json`
- `progress.md`
- `scripts/init.sh`
- `skills/ai-agent-harness/assets/template/`
- `skills/ai-agent-harness/scripts/init_harness.py`
- `test/contract/test_repository_contract.py`

## Evaluator Result

```text
EVAL_PASS: F032
```

## Follow-Up

- Consider linking the guide from external project docs once this template is released.
