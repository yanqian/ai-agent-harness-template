import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INIT_SCRIPT = ROOT / "skills" / "ai-agent-harness" / "scripts" / "init_harness.py"


def run_initializer(project: Path, mode: str, *extra: str):
    return subprocess.run(
        [
            sys.executable,
            str(INIT_SCRIPT),
            "--root",
            str(project),
            "--template-root",
            str(ROOT),
            "--mode",
            mode,
            *extra,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def run_project_init(project: Path):
    return subprocess.run(
        [str(project / "init.sh")],
        cwd=project,
        text=True,
        capture_output=True,
        env={**os.environ, "HARNESS_SKIP_TEST_LAYERS": "1"},
    )


class SkillInitializerHarnessTests(unittest.TestCase):
    def test_new_mode_creates_runnable_harness_and_clean_check(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            result = run_initializer(project, "new")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("mode=new", result.stdout)
            self.assertIn("state_valid=true", result.stdout)
            self.assertIn("runnable_harness=true", result.stdout)
            self.assertIn("state_reset=feature_list.json,progress.md", result.stdout)

            data = json.loads((project / "feature_list.json").read_text())
            self.assertEqual(data, {"features": []})
            manifest = json.loads((project / ".agent-harness" / "manifest.json").read_text())
            self.assertEqual(manifest["template_version"], "0.2.1")
            self.assertIn("category", manifest["files"]["scripts/validate-state.py"])

            init = run_project_init(project)
            self.assertEqual(init.returncode, 0, init.stderr)

            check = run_initializer(project, "check")
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertIn("template_version=0.2.1", check.stdout)
            self.assertIn("installed_version=0.2.1", check.stdout)
            self.assertIn("state_valid=true", check.stdout)
            self.assertIn("runnable_harness=true", check.stdout)
            self.assertIn("project_state_changed=", check.stdout)
            self.assertIn("next_action=harness is installed and runnable", check.stdout)

    def test_adopt_mode_does_not_overwrite_merge_sensitive_files_by_default(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            (project / "README.md").write_text("existing readme\n")
            (project / "AGENTS.md").write_text("existing agent rules\n")

            result = run_initializer(project, "adopt")
            self.assertEqual(result.returncode, 1)
            self.assertIn("blocking_conflicts:", result.stdout)
            self.assertIn("README.md", result.stdout)
            self.assertIn("AGENTS.md", result.stdout)
            self.assertEqual((project / "README.md").read_text(), "existing readme\n")
            self.assertEqual((project / "AGENTS.md").read_text(), "existing agent rules\n")
            self.assertFalse((project / ".agent-harness" / "manifest.json").exists())
            self.assertFalse((project / "feature_list.json").exists())

            forced = run_initializer(project, "adopt", "--force")
            self.assertEqual(forced.returncode, 0, forced.stderr)
            self.assertIn("overwritten=2", forced.stdout)
            self.assertNotEqual((project / "README.md").read_text(), "existing readme\n")

    def test_repair_restores_missing_harness_files_and_preserves_project_state(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            initial = run_initializer(project, "new")
            self.assertEqual(initial.returncode, 0, initial.stderr)

            custom_features = {
                "features": [
                    {
                        "id": "F999",
                        "title": "Custom project feature",
                        "description": "Project-owned feature state must survive repair.",
                        "acceptance": ["state remains intact"],
                        "passes": False,
                        "status": "todo",
                        "attempts": 7,
                        "last_error": "keep me",
                    }
                ]
            }
            (project / "feature_list.json").write_text(json.dumps(custom_features, indent=2) + "\n")
            (project / "progress.md").write_text(
                "# Progress\n\n"
                "## Current System Status\n\ncustom\n\n"
                "## Last Completed Feature\n\nNone.\n\n"
                "## Next Feature\n\nF999\n\n"
                "## Known Issues\n\nNone.\n"
            )
            (project / "scripts" / "validate-state.py").unlink()
            (project / "prompts" / "work.md").unlink()

            repaired = run_initializer(project, "repair")
            self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
            self.assertIn("mode=repair", repaired.stdout)
            self.assertIn("created=2", repaired.stdout)
            self.assertTrue((project / "scripts" / "validate-state.py").exists())
            self.assertTrue((project / "prompts" / "work.md").exists())
            self.assertEqual(json.loads((project / "feature_list.json").read_text()), custom_features)
            self.assertIn("F999", (project / "progress.md").read_text())

    def test_check_reports_complete_diagnostics_and_version_drift(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            initial = run_initializer(project, "new")
            self.assertEqual(initial.returncode, 0, initial.stderr)

            manifest_path = project / ".agent-harness" / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["template_version"] = "0.0.0"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            (project / "scripts" / "validate-state.py").write_text("local static drift\n")
            (project / "README.md").write_text("local merge-sensitive change\n")

            check = run_initializer(project, "check")
            self.assertEqual(check.returncode, 1)
            for phrase in [
                "mode=check",
                "template_version=0.2.1",
                "installed_version=0.0.0",
                "state_valid=false",
                "runnable_harness=false",
                "missing=0",
                "conflicts=1",
                "drift=1",
                "project_state_changed=",
                "optional_changed=0",
                "state_errors:",
                "next_action=review merge-sensitive conflicts",
            ]:
                self.assertIn(phrase, check.stdout)


if __name__ == "__main__":
    unittest.main()
