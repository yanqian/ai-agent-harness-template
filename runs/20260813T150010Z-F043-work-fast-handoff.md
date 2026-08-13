# Run Record: F043 - work-fast coding handoff

## Summary

- Date: 20260813T150010Z
- Agent role: Orchestrator fast handoff
- Feature: F043
- Result: in_progress

## Repository State

- Starting commit: 61d3804
- Ending commit: 61d3804
- Working tree status: M AGENTS.md
 M README.md
 M SPEC.md
 M agent-provider.example.json
 M docs/agent-provider-configuration.md
 M docs/agent-workflow.md
 M docs/architecture.md
 M docs/testing.md
 M feature_list.json
 M orchestrator.py
 M progress.md
 M prompts/continue.md
 M prompts/evaluate.md
 M prompts/plan.md
 M prompts/work-fast.md
 M prompts/work.md
 M scripts/run-agent-provider.py
 M skills/ai-agent-harness/SKILL.md
 M skills/ai-agent-harness/assets/template/AGENTS.md
 M skills/ai-agent-harness/assets/template/README.md
 M skills/ai-agent-harness/assets/template/SPEC.md
 M skills/ai-agent-harness/assets/template/agent-provider.example.json
 M skills/ai-agent-harness/assets/template/docs/agent-provider-configuration.md
 M skills/ai-agent-harness/assets/template/docs/agent-workflow.md
 M skills/ai-agent-harness/assets/template/docs/architecture.md
 M skills/ai-agent-harness/assets/template/docs/testing.md
 M skills/ai-agent-harness/assets/template/feature_list.json
 M skills/ai-agent-harness/assets/template/orchestrator.py
 M skills/ai-agent-harness/assets/template/progress.md
 M skills/ai-agent-harness/assets/template/prompts/continue.md
 M skills/ai-agent-harness/assets/template/prompts/evaluate.md
 M skills/ai-agent-harness/assets/template/prompts/plan.md
 M skills/ai-agent-harness/assets/template/prompts/work-fast.md
 M skills/ai-agent-harness/assets/template/prompts/work.md
 M skills/ai-agent-harness/assets/template/scripts/run-agent-provider.py
 M skills/ai-agent-harness/assets/template/skills/ai-agent-harness/SKILL.md
 M skills/ai-agent-harness/assets/template/skills/ai-agent-harness/references/workflows.md
 M skills/ai-agent-harness/assets/template/skills/ai-agent-harness/scripts/init_harness.py
 M skills/ai-agent-harness/assets/template/test/contract/test_repository_contract.py
 M skills/ai-agent-harness/assets/template/test/harness/test_skill_initializer.py
 M skills/ai-agent-harness/assets/template/test/unit/test_scripts.py
 M skills/ai-agent-harness/references/workflows.md
 M skills/ai-agent-harness/scripts/init_harness.py
 M test/contract/test_repository_contract.py
 M test/harness/test_skill_initializer.py
 M test/unit/test_scripts.py
?? agent-provider.json
?? runs/20260813T144746Z-F042-work-fast-handoff.md
?? runs/20260813T145400Z-F042-work-fast-coding.md
?? runs/20260813T145756Z-F042-evaluation.md
?? runs/20260813T145836Z-F042-evaluation.md

## Commands Run

```bash
python3 orchestrator.py --work-fast
```

## Evidence

- Fast handoff: FAST_CODING_HANDOFF: F043
- Coding evidence required: write a separate run record containing the fast coding evidence marker and matching coding pass verdict after implementation.
- Evaluator pass prohibited in coding evidence: do not write evaluator pass evidence during the fast coding phase.
