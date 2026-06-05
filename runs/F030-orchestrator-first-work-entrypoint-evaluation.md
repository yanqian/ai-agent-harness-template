# Run Record: F030 - orchestrator-first work entrypoint

## Summary

- Date: 2026-06-05
- Agent role: Evaluator Agent
- Feature: F030
- Result: pass

## Repository State

- Starting commit: 8093bf9
- Ending commit: uncommitted working tree
- Working tree status: F030 implementation changes present

## Commands Run

```bash
./init.sh
python3 -m unittest discover -s test/contract -p 'test_*.py'
make work
scripts/validate-feature.sh F030
```

## Evidence

- `Makefile` now includes `work`, which runs `python3 orchestrator.py --max-rounds 1`.
- `AGENTS.md`, `README.md`, `docs/agent-workflow.md`, prompts, SKILL.md, workflow references, and bundled template files document orchestrator-first work and explicit manual fallback.
- `orchestrator.py` checks adapters before entering feature state transitions and fails closed when adapters are missing, not executable, or still templates.
- `scripts/run-coding-agent.sh` and `scripts/run-evaluator-agent.sh` now explain the adapter setup gap and warn against bypassing evaluator gating or final `./init.sh` verification.
- Contract tests verify orchestrator-first entrypoint documentation, `make work`, adapter fail-closed checks, prompts, skill docs, and bundled template synchronization.
- `make work` was run with template adapters and failed closed after startup verification, before mutating F030 state.

## Failure Analysis

- Failure domain:
- Failure summary:
- Harness improvement: F030 itself is the harness improvement that makes orchestrator-first work explicit and fail-closed.
- Follow-up feature: F031 will make the orchestrator-first agent provider configurable.

## Files Changed

- `AGENTS.md`
- `Makefile`
- `README.md`
- `docs/agent-workflow.md`
- `feature_list.json`
- `orchestrator.py`
- `progress.md`
- `prompts/continue.md`
- `prompts/evaluate.md`
- `prompts/work.md`
- `scripts/run-coding-agent.sh`
- `scripts/run-evaluator-agent.sh`
- `skills/ai-agent-harness/`
- `test/contract/test_repository_contract.py`

## Evaluator Result

```text
EVAL_PASS: F030
```

## Follow-Up

- Implement F031 so configured Codex, Claude Code, Cursor Agent, or custom providers can back the orchestrator role adapters without implicit guessing.
