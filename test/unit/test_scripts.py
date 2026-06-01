import json
import os
import shutil
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
        features = data["features"]
        unfinished = [
            feature
            for feature in features
            if not (feature.get("passes") is True and feature.get("status") == "done")
        ]
        self.assertIn(f"features_total={len(features)}", result.stdout)
        self.assertIn(f"features_unfinished={len(unfinished)}", result.stdout)
        if unfinished:
            next_feature = unfinished[0]
            self.assertIn(f"next_feature={next_feature['id']} {next_feature['title']}", result.stdout)
        else:
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

    def test_clean_state_resets_project_state_only(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            shutil.copy(ROOT / "feature_list.json", project / "feature_list.json")
            (project / "progress.md").write_text("# Progress\n\nold state\n")
            runs = project / "runs"
            runs.mkdir()
            (runs / "RUN_TEMPLATE.md").write_text((ROOT / "runs" / "RUN_TEMPLATE.md").read_text())
            (runs / ".gitkeep").write_text("")
            (runs / "20260101T000000Z-F001.md").write_text("old run")

            result = run_command([sys.executable, "scripts/clean-state.py", "--root", str(project)])
            self.assertEqual(result.returncode, 0, result.stderr)

            data = json.loads((project / "feature_list.json").read_text())
            self.assertEqual(data, {"features": []})
            progress = (project / "progress.md").read_text()
            self.assertIn("Harness state has been reset for a new project.", progress)
            self.assertIn("Add the first feature to `feature_list.json`.", progress)
            self.assertTrue((runs / "RUN_TEMPLATE.md").exists())
            self.assertTrue((runs / ".gitkeep").exists())
            self.assertFalse((runs / "20260101T000000Z-F001.md").exists())


if __name__ == "__main__":
    unittest.main()
