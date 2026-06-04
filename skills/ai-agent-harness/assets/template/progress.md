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
- Tiny dependency-free Python CLI example in `examples/tiny-cli/`.
- Dependency-free Go server example in `examples/go-server/`.

## Last Completed Feature

`F021` - Add capability gap governance.

## Next Feature

`F011` - Explore concurrent agent execution. This is a future/backlog item only; implement it only if the harness needs parallel agent throughput.

## Known Issues

- The template orchestrator is intentionally lightweight and vendor-neutral.
- Vendor-specific command wrappers for Codex, Claude Code, and Cursor Agent are intentionally left to downstream projects.
