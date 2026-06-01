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
        for phrase in ["architecture.md", "testing.md", "external-behavior.md", "agent-workflow.md", "failure-domains.md", "real-world-usage.md", "decisions/"]:
            self.assertIn(phrase, docs)

        quality = (ROOT / "QUALITY.md").read_text()
        for phrase in ["Correctness", "Completeness", "Maintainability", "Test Coverage", "Recoverability", "Safety", "failure domain", "harness improvement"]:
            self.assertIn(phrase, quality)

        run_template = (ROOT / "runs" / "RUN_TEMPLATE.md").read_text()
        for phrase in ["Commands Run", "Evidence", "Failure Analysis", "Failure domain", "Harness improvement", "Evaluator Result", "Follow-Up"]:
            self.assertIn(phrase, run_template)

        failure_domains = (ROOT / "docs" / "failure-domains.md").read_text()
        for phrase in ["requirement_gap", "implementation_gap", "test_gap", "contract_gap", "external_behavior_gap", "state_recovery_gap", "agent_workflow_gap", "environment_gap", "Improvement Loop"]:
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
            ],
            "evaluate.md": [
                "Act as Evaluator Agent",
                "Do not implement new features.",
                "Do not accept incomplete work.",
                "Prevent premature completion.",
                "Apply the rubric in `QUALITY.md`.",
                "record or update run evidence using `runs/RUN_TEMPLATE.md`.",
                "classify the failure using `docs/failure-domains.md`",
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
