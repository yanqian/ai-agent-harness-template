import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_command(args):
    env = os.environ.copy()
    env["HARNESS_SKIP_TEST_LAYERS"] = "1"
    return subprocess.run(args, cwd=ROOT, env=env, text=True, capture_output=True)


class SmokeTests(unittest.TestCase):
    def test_primary_template_commands(self):
        commands = [
            ["scripts/validate-feature.sh", "F001"],
            ["scripts/summarize-progress.sh"],
            [sys.executable, "orchestrator.py", "--dry-run"],
            [sys.executable, "orchestrator.py", "--eval-only", "F001", "--dry-run"],
        ]
        for command in commands:
            with self.subTest(command=command):
                result = run_command(command)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
