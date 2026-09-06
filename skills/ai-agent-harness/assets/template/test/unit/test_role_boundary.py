"""Adversarial real Git and real role subprocess coverage for F048."""
import json
from pathlib import Path
import sys
import tempfile

from test_completion import CompletionTests


class RoleBoundaryTests(CompletionTests):
    # Reuse fixtures, not the parent's tests (filtered below).
    def commit_fixture(self):
        self.command(['git', 'add', '.'], self.root)
        result = self.command(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-qm', 'source'], self.root)
        self.assertEqual(result.returncode, 0, result.stderr)

    def mutate_adapter(self, code):
        self.script(self.h / 'scripts/run-coding-agent.sh', '#!' + sys.executable + '\nimport json,sys\nfrom pathlib import Path\nsys.stdin.read()\n' + code + '\nprint("CODING_PASS: F001")\n')

    def test_role_writes_rejected_in_both_modes_and_layouts(self):
        for hidden in (False, True):
            for fast in (False, True):
                for change in ('dirty', 'delete', 'criteria', 'early-done', 'unrelated', 'contract', 'outside'):
                    with self.subTest(hidden=hidden, fast=fast, change=change), tempfile.TemporaryDirectory() as tmp:
                        self.root = Path(tmp)
                        self.setup_repo(hidden)
                        (self.h / 'prior.txt').write_text('prior accepted uncommitted implementation')
                        other = dict(self.f, id='F002', title='Other')
                        (self.h / 'feature_list.json').write_text(json.dumps({'features': [self.f, other]}))
                        code = {
                            'dirty': 'Path("prior.txt").write_text("overwritten")',
                            'delete': 'Path("prior.txt").unlink()',
                            'criteria': 'p=Path("feature_list.json"); s=json.loads(p.read_text()); s["features"][0]["acceptance"]=["relaxed"]; p.write_text(json.dumps(s))',
                            'early-done': 'p=Path("feature_list.json"); s=json.loads(p.read_text()); s["features"][0].update(passes=True,status="done"); p.write_text(json.dumps(s))',
                            'unrelated': 'p=Path("feature_list.json"); s=json.loads(p.read_text()); s["features"][1]["title"]="unauthorized"; p.write_text(json.dumps(s))',
                            'contract': 'Path("QUALITY.md").write_text("relaxed checks")',
                            'outside': 'Path("outside.txt").write_text("unrelated")',
                        }[change]
                        args = ['--allow-path', ('.agent-harness/' if hidden else '') + 'allowed'] if change == 'outside' else []
                        if fast:
                            begin = self.run_cli('--work-fast', *args)
                            self.assertEqual(begin.returncode, 0, begin.stderr)
                            self.command([sys.executable, '-c', 'import json\nfrom pathlib import Path\n' + code])
                            result = self.record()
                        else:
                            self.mutate_adapter(code)
                            result = self.run_cli(*args)
                        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                        state = self.state()
                        directory = self.h / 'runs' / state['active_run']
                        self.assertTrue(list(directory.glob('violation-*.json')), result.stderr)
                        self.assertFalse((directory / 'receipt.json').exists())
                        self.assertFalse(state['passes'])
                        if change == 'dirty':
                            self.assertEqual((self.h / 'prior.txt').read_text(), 'overwritten')
                        if change == 'delete':
                            self.assertFalse((self.h / 'prior.txt').exists())

    def test_authorized_dirty_new_deleted_paths_and_full_diff(self):
        for hidden in (False, True):
            for fast in (False, True):
                with self.subTest(hidden=hidden, fast=fast), tempfile.TemporaryDirectory() as tmp:
                    self.root = Path(tmp)
                    self.setup_repo(hidden)
                    (self.h / 'source').mkdir()
                    (self.h / 'source/old').write_text('committed content\n')
                    self.commit_fixture()
                    (self.h / 'source/old').write_text('planning edits\n')
                    prefix = '.agent-harness/' if hidden else ''
                    args = ['--adopt-dirty', prefix + 'source/old', '--allow-path', prefix + 'source']
                    code = 'Path("source/old").unlink(); Path("source/new\\nname").write_text("new implementation\\n")'
                    if fast:
                        result = self.run_cli('--work-fast', *args)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.command([sys.executable, '-c', 'from pathlib import Path\n' + code])
                        result = self.record()
                        self.assertEqual(result.returncode, 0, result.stderr)
                        result = self.run_cli('--work-fast')
                    else:
                        self.mutate_adapter(code)
                        result = self.run_cli(*args)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assert_done()
                    directory = self.h / 'runs' / self.state()['active_run']
                    diff = json.loads((directory / 'changes.json').read_text())
                    self.assertEqual(len(diff['changes']), 2)
                    self.assertIn('planning edits', (directory / 'changes.json').read_text())
                    self.assertTrue((directory / 'scope.json').exists())

    def test_missing_boundary_and_late_adoption_fail_closed_then_explicit_restart(self):
        self.setup_repo()
        (self.h / 'old').write_text('prior work')
        f = self.begin_fast()
        result = self.run_cli('--work-fast', '--adopt-dirty', 'old')
        self.assertNotEqual(result.returncode, 0)
        # A new run requires explicit restart; no old evidence is reused.
        result = self.run_cli('--restart-run', 'F001', '--run-id', f['active_run'])
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli('--work-fast', '--adopt-dirty', 'old')
        self.assertEqual(result.returncode, 0, result.stderr)
        fresh = self.state()
        self.assertNotEqual(fresh['active_run'], f['active_run'])
        (self.h / 'runs' / fresh['active_run'] / 'boundary.json').unlink()
        self.assertNotEqual(self.record().returncode, 0)
        self.assertFalse(self.state()['passes'])

    def test_evaluator_scope_and_unrelated_state_edits(self):
        for hidden in (False, True):
            for fast in (False, True):
                for behavior in ('missing-scope', 'unrelated-state', 'delete-source'):
                    with self.subTest(hidden=hidden, fast=fast, behavior=behavior), tempfile.TemporaryDirectory() as tmp:
                        self.root = Path(tmp)
                        self.setup_repo(hidden)
                        (self.h / 'source.txt').write_text('must survive evaluator')
                        p = self.h / 'scripts/run-evaluator-agent.sh'
                        script = p.read_text()
                        if behavior == 'missing-scope':
                            script = script.replace('print(json.dumps(result))', 'result.pop("scope", None); print(json.dumps(result))')
                        elif behavior == 'unrelated-state':
                            script += '\np=Path("feature_list.json"); s=json.loads(p.read_text()); s["unknown"]="unauthorized"; p.write_text(json.dumps(s))\n'
                        else:
                            script += '\nPath("source.txt").unlink()\n'
                        p.write_text(script)
                        if fast:
                            self.begin_fast()
                            self.assertEqual(self.record().returncode, 0)
                        result = self.run_cli(*(['--work-fast'] if fast else []))
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertFalse(self.state()['passes'])
                        directory = self.h / 'runs' / self.state()['active_run']
                        self.assertTrue((directory / 'failure.json').exists())
                        if behavior != 'missing-scope':
                            self.assertTrue(list(directory.glob('violation-*.json')))

    def test_removed_active_run_and_staged_dirty_are_detected(self):
        self.setup_repo()
        (self.h / 'staged.txt').write_text('original')
        self.commit_fixture()
        (self.h / 'staged.txt').write_text('staged user edit')
        self.command(['git', 'add', 'staged.txt'])
        # Cancellation: index differs from HEAD while worktree matches HEAD.
        (self.h / 'staged.txt').write_text('original')
        self.assertEqual(self.command(['git', 'diff', '--name-only', 'HEAD']).stdout, '')
        f = self.begin_fast()
        (self.h / 'staged.txt').write_text('role overwrite')
        state = self.state()
        del state['active_run']
        self.save(state)
        result = self.run_cli('--work-fast')
        self.assertNotEqual(result.returncode, 0)
        directory = self.h / 'runs' / f['active_run']
        report = next(directory.glob('violation-*.json')).read_text()
        self.assertIn('staged.txt', report)
        self.assertIn('feature_list.json:F001', report)
        self.assertEqual((self.h / 'staged.txt').read_text(), 'role overwrite')

    def test_receipt_enrollment_rejects_missing_sidecars(self):
        import completion
        import run_evidence
        for name in ('boundary.json', 'boundary-required.json', 'scope.json', 'changes.json', 'all'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                self.root = Path(tmp)
                self.setup_repo()
                result = self.run_cli()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assert_done()
                directory = self.h / 'runs' / self.state()['active_run']
                for victim in (('boundary.json', 'boundary-required.json', 'scope.json', 'changes.json') if name == 'all' else (name,)):
                    (directory / victim).unlink()
                with self.assertRaises((run_evidence.EvidenceError, OSError)):
                    completion.verify_history(self.h, {'features': [self.state()]})

    def test_path_validation_before_lifecycle_mutation(self):
        self.setup_repo()
        for path in ('../escape', '/absolute', '.', 'src/../x', 'src//x', '.git/config', 'src/*'):
            before = (self.h / 'feature_list.json').read_bytes()
            result = self.run_cli('--work-fast', '--allow-path', path)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((self.h / 'feature_list.json').read_bytes(), before)


# Parent integration suite runs once in its own module.
for name in list(vars(CompletionTests)):
    if name.startswith('test_') and name not in vars(RoleBoundaryTests):
        setattr(RoleBoundaryTests, name, None)
del CompletionTests
