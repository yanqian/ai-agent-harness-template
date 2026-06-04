import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RepositoryContractTests(unittest.TestCase):
    def test_readme_records_reference_sources(self):
        text = (ROOT / "README.md").read_text()
        for phrase in [
            "## Sources",
            "Harness engineering: leveraging Codex in an agent-first world",
            "https://openai.com/index/harness-engineering/",
            "Harness design for long-running application development",
            "https://www.anthropic.com/engineering/harness-design-long-running-apps",
            "everything is a ralph loop",
            "https://ghuntley.com/loop/",
        ]:
            self.assertIn(phrase, text)

    def test_readme_positions_resumable_ai_coding_harness(self):
        text = (ROOT / "README.md").read_text()
        for phrase in [
            "Make AI coding projects resumable.",
            "the session is interrupted",
            "context becomes too long",
            "the weekly quota is exhausted",
            "tomorrow's agent forgets yesterday's decisions",
            "the agent changes unrelated files",
            "the agent marks work done too early",
            "This is not a prompt collection.",
            "repository-state protocol",
            "## Why This Exists",
            "The template dogfoods its own state model",
            "### Use This Template",
            "### Verify This Repository",
            "make validate FEATURE=F001",
            "The orchestrator is intentionally boring",
            "## Announcement",
            "I Built a Small Harness to Stop AI Coding Projects From Forgetting State",
            "https://yanqian.github.io/posts/publish/i-built-a-small-harness-to-stop-ai-coding-projects-from-forgetting-state/",
        ]:
            self.assertIn(phrase, text)

    def test_oss_readiness_files_are_present(self):
        required_files = [
            "LICENSE",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CHANGELOG.md",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
            ".github/ISSUE_TEMPLATE/config.yml",
        ]
        for path in required_files:
            self.assertTrue((ROOT / path).exists(), f"{path} should exist")

        license_text = (ROOT / "LICENSE").read_text()
        contributing = (ROOT / "CONTRIBUTING.md").read_text()
        security = (ROOT / "SECURITY.md").read_text()
        changelog = (ROOT / "CHANGELOG.md").read_text()
        bug = (ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").read_text()
        feature = (ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()

        self.assertIn("MIT License", license_text)
        self.assertIn("make ci", contributing)
        self.assertIn("Reporting Security Issues", security)
        self.assertIn("## 0.1.0", changelog)
        self.assertIn("Failure Domain", bug)
        self.assertIn("Acceptance Criteria", feature)
        for path in required_files:
            self.assertIn(path, init)

    def test_agents_external_behavior_verification_preserves_core_requirements(self):
        text = (ROOT / "AGENTS.md").read_text()
        for phrase in [
            "## External Behavior Verification",
            "### External Tool Schema Rules",
            "must verify that behavior before relying on it",
            "Do not infer unknown external behavior from intuition or local mocks.",
            "mocks and fake children as tests of this repository's state machine only",
            "do not prove the external tool or platform behaves that way",
            "argv, stdio, cwd, env, timeout, signal handling, or shell mode",
            "real command behavior or document why direct verification is not possible",
            "real-shaped output from the source",
            "regression tests using those captured shapes",
            "If the schema is unknown, fail closed",
        ]:
            self.assertIn(phrase, text)

    def test_capability_gap_governance_is_documented_and_enforced(self):
        agents = (ROOT / "AGENTS.md").read_text()
        docs_index = (ROOT / "docs" / "README.md").read_text()
        capability = (ROOT / "docs" / "capability-gaps.md").read_text()
        workflow = (ROOT / "docs" / "agent-workflow.md").read_text()
        quality = (ROOT / "QUALITY.md").read_text()
        failure_domains = (ROOT / "docs" / "failure-domains.md").read_text()
        run_template = (ROOT / "runs" / "RUN_TEMPLATE.md").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()
        skill = (ROOT / "skills" / "ai-agent-harness" / "SKILL.md").read_text()
        workflows = (ROOT / "skills" / "ai-agent-harness" / "references" / "workflows.md").read_text()
        initializer = (ROOT / "skills" / "ai-agent-harness" / "scripts" / "init_harness.py").read_text()

        for phrase in [
            "## Capability Gap Handling",
            "A missing tool, permission, generator, dependency, service, credential, runtime setting, CI resource, or verification fixture is a capability gap",
            "Do not bypass a capability gap by hand-writing generated artifacts",
            "local-only environment changes",
            "mark the feature blocked or append a follow-up feature",
        ]:
            self.assertIn(phrase, agents)

        for phrase in [
            "# Capability Gaps",
            "Hand-writing generated bindings or generated artifacts only because the generator is missing.",
            "setting `GOCACHE` under a temporary directory is acceptable for local verification only",
            "Use `capability_gap` as the primary failure domain",
        ]:
            self.assertIn(phrase, capability)

        checks = {
            docs_index: ["capability-gaps.md", "missing tools, permissions, generators, dependencies"],
            workflow: ["follow `docs/capability-gaps.md`", "Evaluation rejects features that bypass required capability gaps"],
            quality: ["Required capabilities are provided, documented, automated", "required capability gap was bypassed"],
            failure_domains: ["capability_gap", "required tool, permission, generator, dependency"],
            run_template: ["Capability gaps:"],
            init: ["docs/capability-gaps.md"],
            skill: ["docs/capability-gaps.md", "local-only workarounds"],
            workflows: ["Identify required capabilities", "Check `docs/capability-gaps.md`"],
            initializer: ["docs/capability-gaps.md", "Capability Gap Handling", "TEMPLATE_VERSION = \"0.3.3\""],
        }
        for text, phrases in checks.items():
            for phrase in phrases:
                self.assertIn(phrase, text)

    def test_feature_decomposition_governance_is_documented_and_enforced(self):
        agents = (ROOT / "AGENTS.md").read_text()
        spec = (ROOT / "SPEC.md").read_text()
        docs_index = (ROOT / "docs" / "README.md").read_text()
        decomposition = (ROOT / "docs" / "feature-decomposition.md").read_text()
        workflow = (ROOT / "docs" / "agent-workflow.md").read_text()
        quality = (ROOT / "QUALITY.md").read_text()
        failure_domains = (ROOT / "docs" / "failure-domains.md").read_text()
        plan = (ROOT / "prompts" / "plan.md").read_text()
        evaluate = (ROOT / "prompts" / "evaluate.md").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()
        skill = (ROOT / "skills" / "ai-agent-harness" / "SKILL.md").read_text()
        workflows = (ROOT / "skills" / "ai-agent-harness" / "references" / "workflows.md").read_text()
        initializer = (ROOT / "skills" / "ai-agent-harness" / "scripts" / "init_harness.py").read_text()

        for phrase in [
            "Decompose broad requirements into independently verifiable feature entries.",
            "Do not collapse unrelated or independently verifiable work into one feature.",
            "Use `docs/feature-decomposition.md`",
            "Feature entries must be independently verifiable units of work.",
        ]:
            self.assertIn(phrase, agents)

        for phrase in [
            "# Feature Decomposition",
            "A feature is the smallest valuable behavior or capability",
            "Split Triggers",
            "Allowed Merges",
            "more than five acceptance criteria",
            "Use `feature_decomposition_gap`",
        ]:
            self.assertIn(phrase, decomposition)

        checks = {
            spec: ["Feature count is determined by independently verifiable behavior"],
            docs_index: ["feature-decomposition.md", "independently verifiable feature entries"],
            workflow: ["Planning follows `docs/feature-decomposition.md`", "Evaluation rejects over-bundled features"],
            quality: ["not over-bundled", "should have been decomposed"],
            failure_domains: ["feature_decomposition_gap", "over-bundled feature"],
            plan: ["Use `docs/feature-decomposition.md`", "Do not append a generic \"implement all requirements\" feature"],
            evaluate: ["Check `docs/feature-decomposition.md`", "Use `feature_decomposition_gap`"],
            init: ["docs/feature-decomposition.md"],
            skill: ["docs/feature-decomposition.md", "Split independently verifiable behavior"],
            workflows: ["Use `docs/feature-decomposition.md`", "reject over-bundled features"],
            initializer: ["docs/feature-decomposition.md", "TEMPLATE_VERSION = \"0.3.3\""],
        }
        for text, phrases in checks.items():
            for phrase in phrases:
                self.assertIn(phrase, text)

    def test_commit_message_governance_is_documented_and_enforced(self):
        agents = (ROOT / "AGENTS.md").read_text()
        spec = (ROOT / "SPEC.md").read_text()
        docs_index = (ROOT / "docs" / "README.md").read_text()
        commit_messages = (ROOT / "docs" / "commit-messages.md").read_text()
        workflow = (ROOT / "docs" / "agent-workflow.md").read_text()
        quality = (ROOT / "QUALITY.md").read_text()
        readme = (ROOT / "README.md").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()
        skill = (ROOT / "skills" / "ai-agent-harness" / "SKILL.md").read_text()
        workflows = (ROOT / "skills" / "ai-agent-harness" / "references" / "workflows.md").read_text()
        initializer = (ROOT / "skills" / "ai-agent-harness" / "scripts" / "init_harness.py").read_text()

        for phrase in [
            "## Commit Message Rules",
            "Follow `docs/commit-messages.md`.",
            "Include the selected feature ID first in the commit subject",
            "Use `No-feature: <summary>` only for explicitly non-feature work.",
            "Committing approved feature work without the feature ID in the commit subject.",
        ]:
            self.assertIn(phrase, agents)

        for phrase in [
            "# Commit Messages",
            "Fxxx <Action> <concise summary>",
            "Put the feature ID first",
            "F025 Add feature-linked commit messages",
            "Multiple Features",
            "No-feature:",
            "Verify each referenced ID exists",
        ]:
            self.assertIn(phrase, commit_messages)

        checks = {
            spec: ["Feature-Linked Commits", "Fxxx <Action> <concise summary>", "No-feature:"],
            docs_index: ["commit-messages.md", "linking commits back to feature IDs"],
            workflow: ["Use `docs/commit-messages.md`", "include the feature ID in the commit subject"],
            quality: ["Feature commits can be traced back to `feature_list.json`"],
            readme: ["F025 Add feature-linked commit messages", "docs/commit-messages.md"],
            init: ["docs/commit-messages.md"],
            skill: ["docs/commit-messages.md", "Fxxx <Action> <concise summary>"],
            workflows: ["Read `docs/commit-messages.md`", "starts with the feature ID", "Verify every feature ID referenced"],
            initializer: ["docs/commit-messages.md", "TEMPLATE_VERSION = \"0.3.3\""],
        }
        for text, phrases in checks.items():
            for phrase in phrases:
                self.assertIn(phrase, text)

    def test_example_boundaries_are_documented_and_enforced(self):
        agents = (ROOT / "AGENTS.md").read_text()
        docs_index = (ROOT / "docs" / "README.md").read_text()
        architecture = (ROOT / "docs" / "architecture.md").read_text()
        workflow = (ROOT / "docs" / "agent-workflow.md").read_text()
        examples = (ROOT / "docs" / "example-boundaries.md").read_text()
        quality = (ROOT / "QUALITY.md").read_text()
        failure_domains = (ROOT / "docs" / "failure-domains.md").read_text()
        readme = (ROOT / "README.md").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()
        skill = (ROOT / "skills" / "ai-agent-harness" / "SKILL.md").read_text()
        workflows = (ROOT / "skills" / "ai-agent-harness" / "references" / "workflows.md").read_text()
        initializer = (ROOT / "skills" / "ai-agent-harness" / "scripts" / "init_harness.py").read_text()

        for phrase in [
            "## Example Boundaries",
            "Default examples are harness fixtures and teaching references.",
            "Do not satisfy a project feature by modifying `examples/tiny-cli`, `examples/go-server`, or another default example",
            "Put project requirements in project-owned source, contract, documentation, and test paths",
            "Evaluators must reject project-level work that passes only because an example was repurposed.",
        ]:
            self.assertIn(phrase, agents)

        for phrase in [
            "# Example Boundaries",
            "`examples/` directory exists to prove and explain the harness",
            "Do not implement a project-level feature by repurposing `examples/tiny-cli/`, `examples/go-server/`, or another default example.",
            "project-level protobuf or gRPC behavior",
            "Use `example_scope_gap` as the primary failure domain",
        ]:
            self.assertIn(phrase, examples)

        checks = {
            docs_index: ["example-boundaries.md", "project implementation shortcuts"],
            architecture: ["Default examples under `examples/` are demonstration fixtures"],
            workflow: ["follow `docs/example-boundaries.md`", "Evaluation rejects project-level features that pass only by repurposing default examples."],
            quality: ["Project-level requirements are implemented in project-owned paths", "does not repurpose default examples as project product code"],
            failure_domains: ["example_scope_gap", "product work was implemented in default examples"],
            readme: ["Default examples under `examples/` are harness demonstrations", "do not implement project-level requirements by repurposing them"],
            init: ["docs/example-boundaries.md"],
            skill: ["docs/example-boundaries.md", "Default examples are references"],
            workflows: ["Identify project-owned implementation and verification paths", "do not use default examples as the product implementation surface"],
            initializer: ["docs/example-boundaries.md", "TEMPLATE_VERSION = \"0.3.3\""],
        }
        for text, phrases in checks.items():
            for phrase in phrases:
                self.assertIn(phrase, text)

    def test_agents_preserves_role_and_state_safety_contracts(self):
        text = (ROOT / "AGENTS.md").read_text()
        for phrase in [
            "### Initializer",
            "### Planning Agent",
            "### Coding Agent",
            "### Evaluator Agent",
            "### Orchestrator",
            "## State Safety Rules",
            "Do not overwrite the entire `feature_list.json` unnecessarily.",
            "Update only the current feature during Coding Agent work.",
            "Preserve feature ordering and existing fields.",
            "Do not reset existing fields such as `passes`, `status`, `attempts`, or `last_error` unless explicitly instructed.",
            "The Evaluator Agent verifies without implementation changes.",
            "Marking a feature done without evaluator pass.",
            "Never rely on chat history. Always rely on project state.",
            "`docs/README.md` for the repository knowledge index.",
            "`QUALITY.md` for evaluator criteria.",
            "`runs/` for per-run evidence and handoff records.",
            "## Failure Improvement Loop",
            "Assign one primary failure domain from `docs/failure-domains.md`.",
            "Repeated failures in the same domain must not remain only retries.",
        ]:
            self.assertIn(phrase, text)

    def test_repository_knowledge_and_quality_contracts_are_indexed(self):
        docs = (ROOT / "docs" / "README.md").read_text()
        for phrase in ["architecture.md", "testing.md", "external-behavior.md", "feature-decomposition.md", "commit-messages.md", "capability-gaps.md", "example-boundaries.md", "agent-workflow.md", "failure-domains.md", "real-world-usage.md", "decisions/"]:
            self.assertIn(phrase, docs)

        quality = (ROOT / "QUALITY.md").read_text()
        for phrase in ["Correctness", "Completeness", "Maintainability", "Test Coverage", "Recoverability", "Safety", "failure domain", "harness improvement"]:
            self.assertIn(phrase, quality)

        run_template = (ROOT / "runs" / "RUN_TEMPLATE.md").read_text()
        for phrase in ["Commands Run", "Evidence", "Failure Analysis", "Failure domain", "Harness improvement", "Evaluator Result", "Follow-Up"]:
            self.assertIn(phrase, run_template)

        failure_domains = (ROOT / "docs" / "failure-domains.md").read_text()
        for phrase in ["requirement_gap", "feature_decomposition_gap", "implementation_gap", "test_gap", "contract_gap", "external_behavior_gap", "capability_gap", "example_scope_gap", "state_recovery_gap", "agent_workflow_gap", "environment_gap", "Improvement Loop"]:
            self.assertIn(phrase, failure_domains)

    def test_go_server_example_contract_is_documented_and_verified(self):
        readme = (ROOT / "README.md").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()
        server = (ROOT / "examples" / "go-server" / "server.go").read_text()
        tests = (ROOT / "examples" / "go-server" / "server_test.go").read_text()
        for path in [
            ROOT / "examples" / "go-server" / "go.mod",
            ROOT / "examples" / "go-server" / "main.go",
            ROOT / "examples" / "go-server" / "server.go",
            ROOT / "examples" / "go-server" / "server_test.go",
            ROOT / "examples" / "go-server" / "README.md",
        ]:
            self.assertTrue(path.exists(), f"{path} should exist")
        for phrase in ["examples/go-server", "GET /healthz", "GET /greet?name=Codex", "go test ./..."]:
            self.assertIn(phrase, readme)
        for phrase in ["examples/go-server", "go test ./..."]:
            self.assertIn(phrase, init)
        for phrase in ["/healthz", "/greet", "http.MethodGet", "hello, "]:
            self.assertIn(phrase, server)
        for phrase in ["TestHealthz", "TestGreetUsesName", "TestGreetDefaultsBlankName", "TestPostIsRejected"]:
            self.assertIn(phrase, tests)

    def test_makefile_and_github_actions_ci_contract(self):
        makefile = (ROOT / "Makefile").read_text()
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
        readme = (ROOT / "README.md").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()

        for target in ["init:", "test:", "validate:", "unit:", "contract:", "smoke:", "go-example:", "dry-run:", "summarize:", "clean:", "ci:"]:
            self.assertIn(target, makefile)
        for phrase in ["./init.sh", "scripts/validate-feature.sh $(FEATURE)", "python3 orchestrator.py --dry-run", "python3 scripts/clean-state.py", "$(MAKE) validate FEATURE=F001"]:
            self.assertIn(phrase, makefile)
        for phrase in ["push:", "pull_request:", "workflow_dispatch:", "actions/checkout@v4", "actions/setup-go@v5", "make ci"]:
            self.assertIn(phrase, workflow)
        for phrase in ["Make Targets", "make ci", "make validate FEATURE=Fxxx"]:
            self.assertIn(phrase, readme)
        for phrase in ["Makefile", ".github/workflows/ci.yml"]:
            self.assertIn(phrase, init)

    def test_real_world_usage_references_are_documented(self):
        readme = (ROOT / "README.md").read_text()
        docs_index = (ROOT / "docs" / "README.md").read_text()
        real_world = (ROOT / "docs" / "real-world-usage.md").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()

        for phrase in [
            "home-guard-tg",
            "agent-remote-tg",
            "docs/real-world-usage.md",
            "https://github.com/yanqian/home-guard-tg",
            "https://github.com/yanqian/agent-remote-tg",
        ]:
            self.assertIn(phrase, readme)
        self.assertIn("real-world-usage.md", docs_index)
        for phrase in [
            "home-guard-tg",
            "agent-remote-tg",
            "Durable state belongs in repository files",
            "not vendored examples",
        ]:
            self.assertIn(phrase, real_world)
        self.assertIn("docs/real-world-usage.md", init)

    def test_clean_state_contract_is_documented_and_verified(self):
        readme = (ROOT / "README.md").read_text()
        script = (ROOT / "scripts" / "clean-state.py").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()

        for phrase in ["make clean", "reset template state", "resets project-specific state"]:
            self.assertIn(phrase, readme)
        for phrase in ["feature_list.write_text", "{\"features\": []}", "PROGRESS_TEMPLATE", "RUN_TEMPLATE.md", ".gitkeep"]:
            self.assertIn(phrase, script)
        self.assertIn("scripts/clean-state.py", init)

    def test_ai_agent_harness_skill_contract_is_documented_and_verified(self):
        skill = (ROOT / "skills" / "ai-agent-harness" / "SKILL.md").read_text()
        workflows = (ROOT / "skills" / "ai-agent-harness" / "references" / "workflows.md").read_text()
        initializer = (ROOT / "skills" / "ai-agent-harness" / "scripts" / "init_harness.py").read_text()
        template_manifest = json.loads((ROOT / ".agent-harness-template.json").read_text())
        openai = (ROOT / "skills" / "ai-agent-harness" / "agents" / "openai.yaml").read_text()
        readme = (ROOT / "README.md").read_text()
        spec = (ROOT / "SPEC.md").read_text()
        init = (ROOT / "scripts" / "init.sh").read_text()

        for phrase in [
            "repository files as the durable source of truth",
            "Initialize Harness",
            "Plan Requirement",
            "Work One Feature",
            "Evaluate Feature",
            "Finalize And Commit",
            "Only commit after the user explicitly says they are satisfied",
            "Default behavior never overwrites conflicting files.",
        ]:
            self.assertIn(phrase, skill)
        for phrase in [
            "vendor-neutral",
            "new",
            "adopt",
            "repair",
            "check",
            "Never commit merely because implementation finished.",
            "The commit boundary is user satisfaction.",
        ]:
            self.assertIn(phrase, workflows)
        for phrase in [
            "MODE_CHOICES",
            "LAYOUT_CHOICES",
            "DEFAULT_LAYOUT",
            "new",
            "adopt",
            "repair",
            "check",
            "--layout",
            "hidden_agents_text",
            "hidden_init_text",
            "resolve_layout",
            "layout_harness_root",
            "Use --force only after explicit approval",
            "FRESH_FEATURE_LIST",
            "blocking_conflicts",
            "TEMPLATE_VERSION",
            "PROJECT_OWNED_STATE",
            "MERGE_SENSITIVE",
            "OPTIONAL_PREFIXES",
            "EXECUTABLE_TEMPLATE_PATHS",
            "ensure_executable_mode",
            "item_should_be_executable",
            "semantic_validation",
            "write_install_manifest",
            "project_state_changed",
            "next_action",
        ]:
            self.assertIn(phrase, initializer)
        self.assertEqual(template_manifest["template_version"], "0.3.3")
        self.assertEqual(template_manifest["default_layout"], "hidden")
        self.assertIn("hidden", template_manifest["layouts"])
        self.assertIn("visible", template_manifest["layouts"])
        for category in [
            "harness-owned static",
            "project-owned state",
            "merge-sensitive",
            "optional integration",
            "template manifest",
        ]:
            self.assertIn(category, template_manifest["file_categories"])
        self.assertIn(".agent-harness-template.json", init)
        for phrase in ["AI Agent Harness", "$ai-agent-harness", "allow_implicit_invocation: true"]:
            self.assertIn(phrase, openai)
        for phrase in [
            "AI Agent Harness skill",
            "skills/ai-agent-harness/SKILL.md",
            "does not replace repository state",
            "does not overwrite conflicting files unless `--force` is used",
            ".agent-harness/manifest.json",
            "--layout hidden",
            "--layout visible",
            "Root keeps thin `AGENTS.md` and `init.sh` entry points",
            "project-owned state",
            "runnable_harness=true",
            "version drift",
            "### Install The Skill",
            "### Use The Installed Skill",
            "### Manual Script Usage",
            "#### Codex",
            "#### Claude Code",
            "#### Cursor",
            "python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py",
            "install-skill-from-github.py",
            "Restart Codex to pick up the skill",
            "~/.claude/skills/ai-agent-harness",
            ".claude/skills/ai-agent-harness",
            ".cursor/rules/ai-agent-harness.mdc",
            "Cursor users can still run the manual initializer script",
            "Use $ai-agent-harness to initialize this project.",
            "repository-checkout or vendor-neutral fallback usage",
            "not the primary installed-skill experience",
        ]:
            self.assertIn(phrase, readme)
        self.assertNotIn("/Users/", readme)
        for phrase in [
            "Use $ai-agent-harness to initialize this project.",
            "Manual `python3 .../init_harness.py` commands are for repository checkouts",
            "~/.codex/skills",
            "~/.claude/skills/",
            ".claude/skills/",
            ".cursor/rules",
        ]:
            self.assertIn(phrase, skill)
        self.assertNotIn("/Users/", skill)
        for phrase in [
            "Skill Assisted Workflow",
            "convenience layer",
            "preserve the template's vendor-neutral boundary",
            "skills/ai-agent-harness/",
            "new`, `adopt`, `repair`, and `check` modes",
            "installation layouts",
            "default `hidden` layout",
            "root `AGENTS.md` and `init.sh` as thin entry points",
            "`visible` layout",
            "version drift handling",
            "semantically valid",
            "installed skill usage",
            "Manual `python3 skills/.../init_harness.py` commands",
        ]:
            self.assertIn(phrase, spec)
        for path in [
            "skills/ai-agent-harness/SKILL.md",
            "skills/ai-agent-harness/agents/openai.yaml",
            "skills/ai-agent-harness/references/workflows.md",
            "skills/ai-agent-harness/scripts/init_harness.py",
        ]:
            self.assertIn(path, init)

    def test_feature_schema_requires_acceptance_and_state(self):
        schema = json.loads((ROOT / "schemas/feature_list.schema.json").read_text())
        feature_required = schema["properties"]["features"]["items"]["required"]
        for key in ["id", "title", "description", "acceptance", "passes", "status", "attempts", "last_error"]:
            self.assertIn(key, feature_required)
        self.assertTrue(schema["properties"]["features"]["items"]["additionalProperties"])

    def test_feature_list_state_contract_is_consistent(self):
        data = json.loads((ROOT / "feature_list.json").read_text())
        ids = [feature["id"] for feature in data["features"]]
        self.assertEqual(len(ids), len(set(ids)))
        for feature in data["features"]:
            self.assertIsInstance(feature["acceptance"], list)
            self.assertGreater(len(feature["acceptance"]), 0)
            self.assertIn(feature["status"], ["todo", "in_progress", "done", "blocked"])
            if feature["passes"] is True:
                self.assertEqual(feature["status"], "done")
            if feature["status"] == "done":
                self.assertIs(feature["passes"], True)

    def test_prompt_templates_contain_role_contracts(self):
        expectations = {
            "plan.md": [
                "Act as Planning Agent",
                "Use `docs/feature-decomposition.md`",
                "Do not append a generic \"implement all requirements\" feature",
                "Identify required capabilities",
                "Identify project-owned implementation and verification paths",
                "Preserve existing feature IDs, ordering, `passes`, `status`, `attempts`, `last_error`, and unknown fields.",
                "Do not implement business logic during planning",
            ],
            "work.md": [
                "Act as Coding Agent",
                "Implement only the selected feature",
                "Do not overwrite `feature_list.json`.",
                "Do not reset existing feature state.",
                "Preserve existing feature IDs, ordering, `passes`, `status`, `attempts`, `last_error`, and unknown fields.",
                "Do not stage or commit during orchestrated runs.",
                "verify it with a primary source or real-shaped fixture before depending on it.",
                "follow `docs/capability-gaps.md` before using any workaround",
                "follow `docs/example-boundaries.md`",
                "Do not bypass missing tools, permissions, generators, dependencies",
                "local-only environment changes",
                "Do not implement project-level requirements by repurposing default examples",
                "Record run evidence in `runs/` for non-trivial work",
                "classify the failure using `docs/failure-domains.md`",
                "convert harness weaknesses into docs, prompts, scripts, schemas, tests, or a new feature entry",
            ],
            "continue.md": [
                "reconstruct context from repository state only",
                "Do not rely on prior chat history",
                "Do not overwrite `feature_list.json`.",
                "Do not reset existing feature state.",
                "Stop and report exact conflicts when repository state is unsafe.",
                "Use `orchestrator.py` according to `AGENTS.md` when implementation or evaluation is required.",
                "Do not continue repeated failures without either implementing a harness improvement or adding an explicit follow-up feature.",
                "inspect `docs/capability-gaps.md` before continuing",
                "inspect `docs/example-boundaries.md` before continuing",
            ],
            "evaluate.md": [
                "Act as Evaluator Agent",
                "Check `docs/feature-decomposition.md`",
                "Do not implement new features.",
                "Do not accept incomplete work.",
                "Prevent premature completion.",
                "Apply the rubric in `QUALITY.md`.",
                "record or update run evidence using `runs/RUN_TEMPLATE.md`.",
                "classify the failure using `docs/failure-domains.md`",
                "Check `docs/capability-gaps.md`",
                "Check `docs/example-boundaries.md`",
                "Use `capability_gap`",
                "Use `example_scope_gap`",
                "Use `feature_decomposition_gap`",
                "require a durable harness improvement or a follow-up feature",
                "EVAL_PASS: Fxxx",
                "EVAL_FAIL: Fxxx: <reason>",
            ],
        }
        for filename, phrases in expectations.items():
            text = (ROOT / "prompts" / filename).read_text()
            for phrase in phrases:
                self.assertIn(phrase, text)

    def test_orchestrator_cli_contract_is_documented_statically(self):
        text = (ROOT / "orchestrator.py").read_text()
        for phrase in [
            "--dry-run",
            "--eval-only",
            "--max-rounds",
            "CODING_AGENT_ADAPTER",
            "EVALUATOR_AGENT_ADAPTER",
            "RUNS_DIR",
            "startup_protocol()",
            "write_failure_run_record(feature_id, error)",
            "run_agent(coding_prompt",
            "run_agent(evaluator_prompt",
            "mark_in_progress(feature_id)",
            "mark_done(feature_id)",
            "mark_failed(feature_id",
            "if args.eval_only:",
        ]:
            self.assertIn(phrase, text)
        self.assertNotIn("HARNESS_AGENT_COMMAND", text)

    def test_orchestrator_uses_explicit_role_adapters(self):
        coding = (ROOT / "scripts/run-coding-agent.sh").read_text()
        evaluator = (ROOT / "scripts/run-evaluator-agent.sh").read_text()
        self.assertIn("Coding Agent prompt on stdin", coding)
        self.assertIn("Evaluator Agent prompt on stdin", evaluator)
        self.assertIn("EVAL_PASS", evaluator)
        self.assertIn("EVAL_FAIL", evaluator)


if __name__ == "__main__":
    unittest.main()
