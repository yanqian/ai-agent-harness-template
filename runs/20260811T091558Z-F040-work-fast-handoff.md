# Run Record: F040 - work-fast coding handoff

## Summary

- Date: 20260811T091558Z
- Agent role: Orchestrator fast handoff
- Feature: F040
- Result: in_progress

## Repository State

- Starting commit: 1b0bfed
- Ending commit: 1b0bfed
- Working tree status: M .agent-harness-template.json
 M AGENTS.md
 M Makefile
 M README.md
 M SPEC.md
 M agent-provider.example.json
 M docs/agent-provider-configuration.md
 M docs/agent-workflow.md
 M feature_list.json
 M orchestrator.py
 M progress.md
 M prompts/continue.md
 M prompts/evaluate.md
 M prompts/plan.md
 M schemas/feature_list.schema.json
 M scripts/init.sh
 M skills/ai-agent-harness/assets/template/AGENTS.md
 M skills/ai-agent-harness/assets/template/Makefile
 M skills/ai-agent-harness/assets/template/README.md
 M skills/ai-agent-harness/assets/template/agent-provider.example.json
 M skills/ai-agent-harness/assets/template/docs/agent-provider-configuration.md
 M skills/ai-agent-harness/assets/template/docs/agent-workflow.md
 M skills/ai-agent-harness/assets/template/orchestrator.py
 M skills/ai-agent-harness/assets/template/prompts/continue.md
 M skills/ai-agent-harness/assets/template/prompts/evaluate.md
 M skills/ai-agent-harness/assets/template/prompts/plan.md
 M skills/ai-agent-harness/assets/template/schemas/feature_list.schema.json
 M skills/ai-agent-harness/assets/template/scripts/init.sh
 M skills/ai-agent-harness/assets/template/test/contract/test_repository_contract.py
 M test/contract/test_repository_contract.py
 M test/unit/test_scripts.py
?? agent-provider.json
?? runs/20260811T080638Z-F039-work-fast-handoff.md
?? runs/20260811T081020Z-F039-work-fast-coding.md
?? runs/20260811T081318Z-F039-evaluation.md
?? runs/20260811T081342Z-F039-failure.md
?? runs/20260811T081610Z-F039-failure.md
?? runs/20260811T082002Z-F039-evaluation.md
?? scripts/human-eval.py
?? skills/ai-agent-harness/assets/template/scripts/human-eval.py

## Commands Run

```bash
python3 orchestrator.py --work-fast
```

## Evidence

- Fast handoff: FAST_CODING_HANDOFF: F040
- Coding evidence required: write a separate run record containing the fast coding evidence marker and matching coding pass verdict after implementation.
- Evaluator pass prohibited in coding evidence: do not write evaluator pass evidence during the fast coding phase.
