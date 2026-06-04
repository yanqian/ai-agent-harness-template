# Repository Knowledge Map

This directory is the expandable knowledge base for agents.

`AGENTS.md` should stay short and act as a map. Put durable, detailed knowledge here so future sessions can recover context without relying on chat history.

## Index

- `architecture.md` - repository structure, boundaries, and extension points.
- `testing.md` - verification layers and how to add project-specific tests.
- `external-behavior.md` - rules for validating CLIs, APIs, runtimes, and structured tool output.
- `feature-decomposition.md` - rules for splitting broad requirements into independently verifiable feature entries.
- `commit-messages.md` - rules for linking commits back to feature IDs.
- `capability-gaps.md` - rules for turning missing tools, permissions, generators, dependencies, and environment setup into durable project capabilities.
- `example-boundaries.md` - rules for keeping default examples as harness demonstrations rather than project implementation shortcuts.
- `agent-workflow.md` - planning, coding, evaluation, orchestration, and recovery loop.
- `failure-domains.md` - failure classification and rules for turning failures into harness improvements.
- `real-world-usage.md` - real projects that informed the harness design.
- `decisions/` - dated decision records for durable design choices.

## Maintenance Rules

- Update docs when behavior, structure, or workflow changes.
- Prefer concise documents with clear ownership over one large manual.
- Promote repeated review feedback or recurring failure classes into docs, tests, prompts, or scripts.
