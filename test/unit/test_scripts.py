import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_command(args, env=None):
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, env=merged_env)


class ScriptUnitTests(unittest.TestCase):
    def test_validate_state_accepts_current_feature_list(self):
        result = run_command([sys.executable, "scripts/validate-state.py"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("validated", result.stdout)

    def test_validate_feature_rejects_unknown_feature(self):
        result = run_command(["scripts/validate-feature.sh", "F999"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown feature id: F999", result.stderr)

    def test_summarize_progress_reports_counts(self):
        result = run_command(["scripts/summarize-progress.sh"])
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((ROOT / "feature_list.json").read_text())
        self.assertIn(f"features_total={len(data['features'])}", result.stdout)
        self.assertIn("next_feature=none", result.stdout)

    def test_summarize_runs_reports_empty_records(self):
        result = run_command(["scripts/summarize-runs.sh"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("run_records=0", result.stdout)
        self.assertIn("latest_run=none", result.stdout)

    def test_check_failure_domains_requires_improvement_assessment(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_dir = Path(tmp_dir)
            record = runs_dir / "_unit_failure.md"
            record.write_text(
                "# Run Record: F999 - unit failure\n\n"
                "## Summary\n\n"
                "- Result: fail\n\n"
                "## Failure Analysis\n\n"
                "- Failure domain: test_gap\n"
                "- Failure summary: synthetic failure\n"
                "- Harness improvement:\n"
                "- Follow-up feature:\n"
            )
            env = {"HARNESS_RUNS_DIR": str(runs_dir)}
            result = run_command(["scripts/check-failure-domains.sh"], env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing_harness_improvement=1", result.stdout)

            record.write_text(
                "# Run Record: F999 - unit failure\n\n"
                "## Summary\n\n"
                "- Result: fail\n\n"
                "## Failure Analysis\n\n"
                "- Failure domain: test_gap\n"
                "- Failure summary: synthetic failure\n"
                "- Harness improvement: add a regression test for this failure class\n"
                "- Follow-up feature: F999\n"
            )
            result = run_command(["scripts/check-failure-domains.sh"], env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("failure_records=1", result.stdout)
            self.assertIn("domain[test_gap]=1", result.stdout)


if __name__ == "__main__":
    unittest.main()
