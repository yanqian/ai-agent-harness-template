import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_command(args):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True)


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


if __name__ == "__main__":
    unittest.main()
