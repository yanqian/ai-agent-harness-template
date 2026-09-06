# Real configured provider verification

The coordinating process ran scripts/smoke-completion-provider.py with agent-provider.json under the user-authorized Codex runtime. Exit 0; isolated fixture history verification passed. Artifacts: runs/20260905-F048-provider-smoke.

New coordinator fixture run 7d73c00531d0497996a014a2ba4dfa55 produced a done synthetic F001 and receipt with role_boundary enrollment hashes. Raw provider output includes explicit passing scope judgment: changes.json contains no attributable changes, consistent with F001 verifying the existing fixture. Snapshot file contents and modes match. Referenced SPEC.md, QUALITY.md and docs are absent, so their additional checks could not be applied.

This validates the new real configured provider scope protocol, not actual F048 acceptance. The actual F048 parent was started before guard implementation and remains honestly unenrolled. No retrospective boundary/adoption was synthesized; the new-code fixture is the explicit current-runtime verification.
