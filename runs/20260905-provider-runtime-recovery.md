# Provider runtime recovery before F045

## Summary
- Agent role: Planning / runtime capability recovery
- Feature: F045–F048 prerequisites
- Result: recovered

## Evidence
- Clean baseline 7929e0f tagged pre-completion-hardening-20260905 before planning edits.
- Startup and post-planning ./init.sh passed; post-planning log: /tmp/harness-hardening-plan-init.log.
- Sandbox preflight failed on ~/.codex/state_5.sqlite and app-server access; automatic approval review allowed escalated runtime checks.
- /opt/homebrew/bin/codex 0.146.1 with gpt-5.4 returned: model is not supported when using Codex with a ChatGPT account.
- The user's existing global model is gpt-6-astra. Old CLI returned: model requires a newer version of Codex.
- /Applications/ChatGPT.app/Contents/Resources/codex --version returned 0.153.3; exec --help confirms stdin -, --model and --ephemeral. A real minimal stdin prompt with gpt-6-astra returned PROVIDER_OK and exit 0.
- Updated only the existing project-local provider configuration to that verified binary/model; provider remains Codex and cwd remains '.'. Original local config backed up at /tmp/harness-provider-before-completion-hardening.json. No global config or executable changed.

## Failure Analysis
- Failure domain: environment_gap
- Failure summary: project-local provider referred to obsolete model and older PATH CLI.
- Harness improvement: durable recovery evidence documents how to verify command version/model and explicitly select an installed compatible executable; project-local verified field records the exact tested configuration. No model or CLI behavior was guessed and evaluator gating is retained.

## Recovery
On another machine, select its installed compatible CLI path explicitly after checking --version, exec --help, and a minimal real prompt; keep configuration local and run provider preflight before work. The absolute binary path is local configuration, not a distributed default.
