# External Behavior Verification

Agents must verify behavior outside repository code before relying on it.

Examples:

- CLI argument shapes, stdin/stdout/stderr, exit codes, signals, cwd, env, timeout, and shell behavior.
- API payloads, SDK return values, webhooks, and callbacks.
- Runtime/platform behavior such as filesystem permissions, process handling, network behavior, and deployment semantics.
- Structured model/tool output such as JSONL, JSON, logs, and approval events.

Preferred evidence:

- Official documentation.
- Official `--help` output.
- Real minimal commands.
- Captured logs.
- Real-shaped fixtures committed to tests.

If behavior cannot be verified directly, document the uncertainty in `SPEC.md`, `progress.md`, `runs/`, or implementation notes and choose the safer default.

