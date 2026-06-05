# Run Record: F031 - configurable orchestrator agent provider

## Summary

- Date: 2026-06-05
- Agent role: Evaluator Agent
- Feature: F031
- Result: pass

## Repository State

- Starting commit: c57938d
- Ending commit: uncommitted working tree
- Working tree status: F031 implementation changes present

## Commands Run

```bash
codex exec --help
command -v codex
command -v claude
command -v cursor-agent
python3 -m unittest discover -s test/unit -p 'test_*.py'
python3 -m unittest discover -s test/contract -p 'test_*.py'
make work
./init.sh
scripts/validate-feature.sh F031
```

## Evidence

- `agent-provider.example.json` defines an explicit provider contract with Codex, Claude Code, Cursor Agent, and custom provider slots.
- `scripts/run-agent-provider.py` loads `agent-provider.json`, requires an explicit provider, validates configured command arrays, fails closed for missing config, missing commands, invalid JSON, and ambiguous detected providers, and dispatches prompts on stdin without a shell.
- `scripts/run-coding-agent.sh` and `scripts/run-evaluator-agent.sh` delegate to the provider dispatcher and support preflight via `HARNESS_AGENT_PROVIDER_CHECK=1`.
- `orchestrator.py` preflights provider-backed adapters before marking a feature `in_progress`, so missing provider setup does not silently mutate feature state.
- Unit tests cover unconfigured provider failure, ambiguous candidate failure, missing configured command failure, and successful configured dispatch.
- Contract tests cover provider documentation, explicit no-guessing behavior, provider dispatcher semantics, adapters, init checks, and bundled template synchronization.
- `make work` with no `agent-provider.json` failed closed after startup verification with a clear message that Codex was detected but still requires explicit configuration.

## External Behavior Verification

- `codex exec --help` was run locally on 2026-06-05. The help output states that if the prompt is omitted or `-` is used, instructions are read from stdin. This verifies the sample Codex command `["codex", "exec", "-"]`.
- `command -v codex` returned `/opt/homebrew/bin/codex`.
- `command -v claude` returned no executable on this machine.
- `command -v cursor-agent` returned no executable on this machine.
- Claude Code and Cursor Agent command shapes are intentionally not hard-coded; docs require local help output, official documentation, or captured logs before configuring those commands.

## Failure Analysis

- Failure domain:
- Failure summary:
- Harness improvement: F031 adds the durable provider configuration capability required by F030.
- Follow-up feature:

## Files Changed

- `AGENTS.md`
- `README.md`
- `agent-provider.example.json`
- `docs/README.md`
- `docs/agent-provider-configuration.md`
- `docs/external-behavior.md`
- `docs/capability-gaps.md`
- `docs/agent-workflow.md`
- `feature_list.json`
- `orchestrator.py`
- `progress.md`
- `scripts/init.sh`
- `scripts/run-agent-provider.py`
- `scripts/run-coding-agent.sh`
- `scripts/run-evaluator-agent.sh`
- `skills/ai-agent-harness/`
- `test/unit/test_scripts.py`
- `test/contract/test_repository_contract.py`

## Evaluator Result

```text
EVAL_PASS: F031
```

## Follow-Up

- Configure a project-specific `agent-provider.json` only when a team wants real unattended provider execution.
