import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RepositoryContractTests(unittest.TestCase):
    def test_agents_contains_core_guardrails(self):
        text = (ROOT / "AGENTS.md").read_text()
        for phrase in [
            "### Initializer",
            "## State Safety Rules",
            "## External Behavior Verification",
            "### External Tool Schema Rules",
            "## Work Rules",
            "## Anti-Patterns",
            "Never rely on chat history. Always rely on project state.",
        ]:
            self.assertIn(phrase, text)

    def test_feature_schema_requires_acceptance_and_state(self):
        schema = json.loads((ROOT / "schemas/feature_list.schema.json").read_text())
        feature_required = schema["properties"]["features"]["items"]["required"]
        for key in ["id", "title", "description", "acceptance", "passes", "status", "attempts", "last_error"]:
            self.assertIn(key, feature_required)

    def test_prompt_templates_contain_role_contracts(self):
        expectations = {
            "plan.md": ["Act as Planning Agent", "Do not implement business logic during planning"],
            "work.md": ["Act as Coding Agent", "Implement only the selected feature"],
            "continue.md": ["reconstruct context from repository state only", "Do not rely on prior chat history"],
            "evaluate.md": ["Act as Evaluator Agent", "EVAL_PASS: Fxxx", "EVAL_FAIL: Fxxx: <reason>"],
        }
        for filename, phrases in expectations.items():
            text = (ROOT / "prompts" / filename).read_text()
            for phrase in phrases:
                self.assertIn(phrase, text)

    def test_orchestrator_dry_run_does_not_mutate_feature_state(self):
        before = (ROOT / "feature_list.json").read_text()
        env = os.environ.copy()
        env["HARNESS_SKIP_TEST_LAYERS"] = "1"
        result = subprocess.run(
            [sys.executable, "orchestrator.py", "--dry-run"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        after = (ROOT / "feature_list.json").read_text()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
