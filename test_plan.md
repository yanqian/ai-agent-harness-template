# Test Plan

## Verification Entry Point

All automated verification must run through:

```bash
./init.sh
```

`init.sh` must exit non-zero on failure.

## Baseline Checks

The initialization baseline verifies:

- Required state files exist.
- `feature_list.json` is valid and internally consistent.
- Feature IDs are unique.
- `AGENTS.md` contains the core guardrails.
- `orchestrator.py` compiles.
- The tiny example tests pass.
- Unit tests pass.
- Contract tests pass.
- Optional harness tests pass when `test/harness/` exists.
- Smoke tests pass.

## Test Layers

### Unit

Unit tests cover deterministic helper behavior and should not call external services.

Current command:

```bash
python3 -m unittest discover -s test/unit -p 'test_*.py'
```

### Contract

Contract tests lock repository-level promises that should not drift accidentally:

- AGENTS guardrail sections.
- Feature schema expectations.
- Prompt role requirements.
- Orchestrator CLI preview behavior.

Current command:

```bash
python3 -m unittest discover -s test/contract -p 'test_*.py'
```

### Harness

Harness tests are optional in the minimal template. Downstream projects should add them when they have real workflows that require multiple modules or processes.

When `test/harness/` exists, `./init.sh` runs:

```bash
python3 -m unittest discover -s test/harness -p 'test_*.py'
```

### Smoke

Smoke tests run the primary user-facing commands end to end.

Current command:

```bash
python3 -m unittest discover -s test/smoke -p 'test_*.py'
```

## Feature Verification Matrix

| Feature | Verification Requirement |
| --- | --- |
| F001 | State validation, feature validation, progress summary, and tiny example tests pass. |
| F002 | Orchestrator dry-run and eval-only dry-run complete without mutating feature state. |
| F003 | Contract validation proves AGENTS guardrails remain present. |
| F004 | `./init.sh` runs unit, contract, smoke, and optional harness layers. |

