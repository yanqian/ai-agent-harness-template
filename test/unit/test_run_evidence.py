import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('run_evidence', ROOT / 'scripts/run_evidence.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


class RunEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.test')
        self.git('config', 'user.name', 'Fixture')
        self.write('init.sh', '#!/bin/sh\nprintf "recovery ok\\n"\n')
        (self.root / 'init.sh').chmod(0o755)
        self.write('source.py', 'original\n')
        self.write('.gitignore', '__pycache__/\n*.pyc\nbuild/\nignored.py\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        self.feature = {'id': 'F001', 'title': 'Fixture', 'description': 'Evidence fixture', 'acceptance': ['Recovery succeeds', 'Source unchanged']}

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def run_record(self, layout='visible', **kwargs):
        return e.create_run(self.root, self.feature, 1, layout, **kwargs)

    def evaluator(self, run, mutation='', assessment=None):
        value = assessment or {'binding': e.binding(run), 'criteria': [
            {'index': i, 'status': 'pass', 'reason': 'checked fixture', 'evidence': ['actual fixture process']} for i in range(2)]}
        code = mutation + '\nprint(' + repr(json.dumps(value)) + ')'
        return e.evaluate(self.root, run, {'argv': [sys.executable, '-c', code], 'timeout_seconds': 5})

    def receipt(self, layout='visible'):
        run = self.run_record(layout)
        checks = e.execute_required(self.root, run)
        outcome, assessment = self.evaluator(run)
        return e.build_receipt(self.root, run, checks, outcome, assessment, self.feature)

    def test_real_git_snapshot_tracks_index_worktree_deleted_untracked_and_modes(self):
        original = e.snapshot(self.root)
        self.write('source.py', 'staged\n')
        self.git('add', 'source.py')
        staged = e.snapshot(self.root)
        self.write('source.py', 'original\n')
        self.assertNotEqual(original['sha256'], e.snapshot(self.root)['sha256'])
        self.assertNotEqual(staged['sha256'], e.snapshot(self.root)['sha256'])
        (self.root / 'source.py').unlink()
        deleted = next(x for x in e.snapshot(self.root)['entries'] if x['path'] == 'source.py')
        self.assertEqual(deleted['kind'], 'deleted')
        self.assertTrue(deleted['index'])
        self.write('new.py', 'new')
        before = e.snapshot(self.root)
        (self.root / 'new.py').chmod(0o755)
        self.assertNotEqual(before, e.snapshot(self.root))
        self.git('rm', '--cached', '-f', 'source.py')
        self.assertNotEqual(before, e.snapshot(self.root))

    def test_unusual_paths_and_symlink_targets_are_hashed_without_following(self):
        for path in ['-dash', 'line\nbreak', 'tab\tname', 'quote"slash\\', '中文']:
            self.write(path, path)
        self.git('add', '.')
        os.symlink('/outside/never-read', self.root / 'link')
        first = e.snapshot(self.root)
        self.assertEqual(first, e.snapshot(self.root))
        link = next(x for x in first['entries'] if x['path'] == 'link')
        self.assertEqual(link['kind'], 'symlink')
        self.assertEqual(link['sha256'], e.hashlib.sha256(b'/outside/never-read').hexdigest())
        (self.root / 'link').unlink()
        os.symlink('/different', self.root / 'link')
        self.assertNotEqual(first, e.snapshot(self.root))
        self.write('dir/file', 'inside')
        self.git('add', 'dir/file')
        (self.root / 'dir/file').unlink()
        (self.root / 'dir').rmdir()
        os.symlink('/tmp', self.root / 'dir')
        with self.assertRaises(e.EvidenceError):
            e.snapshot(self.root)

    @unittest.skipIf(sys.platform == 'darwin', 'macOS filesystem rejects invalid UTF-8 names (real EPERM observed)')
    def test_undecodable_filename_on_supporting_filesystems(self):
        raw = os.fsencode(self.root) + b'/invalid-\xff'
        with open(raw, 'wb') as stream:
            stream.write(b'invalid utf8 filename')
        self.git('add', '.')
        run = self.run_record()
        e.validate_run(e.decode_json(e.canonical(run)))
        self.assertIn(os.fsdecode(b'invalid-\xff'), [x['path'] for x in run['snapshot']['entries']])

    def test_additional_checks_are_fixed_and_all_required(self):
        command = {'argv': [sys.executable, '-c', 'print("extra check")'], 'timeout_seconds': 5}
        run = self.run_record(additional_commands=[command])
        command['argv'].append('changed caller input')
        checks = e.execute_required(self.root, run)
        self.assertEqual(len(checks), 2)
        outcome, assessment = self.evaluator(run)
        with self.assertRaises(e.EvidenceError):
            e.build_receipt(self.root, run, checks[:1], outcome, assessment, self.feature)
        e.build_receipt(self.root, run, checks, outcome, assessment, self.feature)

    def test_submodules_and_nonregular_source_fail_closed(self):
        oid = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('update-index', '--add', '--cacheinfo', '160000,' + oid + ',submodule')
        with self.assertRaises(e.EvidenceError): e.snapshot(self.root)
        self.git('update-index', '--force-remove', 'submodule')
        os.mkfifo(self.root / 'pipe')
        with self.assertRaises(e.EvidenceError): e.snapshot(self.root)

    def test_narrow_exclusions_and_hidden_layout(self):
        for layout, prefix in [('visible', ''), ('hidden', '.agent-harness/')]:
            with self.subTest(layout=layout):
                before = e.snapshot(self.root, layout)
                self.write(prefix + 'runs/result.json', 'metadata')
                self.write(prefix + 'progress.md', 'metadata')
                self.write(prefix + 'feature_list.json', 'metadata')
                self.write('__pycache__/a.pyc', 'cache')
                self.assertEqual(before, e.snapshot(self.root, layout))
                self.write(prefix + 'runs/RUN_TEMPLATE.md', 'contract')
                self.assertNotEqual(before, e.snapshot(self.root, layout))
        baseline = e.snapshot(self.root)
        self.write('ignored.py', 'ignored source still included')
        self.write('build/product.py', 'ignored build source still included')
        self.assertNotEqual(baseline, e.snapshot(self.root))
        self.git('add', '-f', '__pycache__/a.pyc')
        self.assertIn('__pycache__/a.pyc', [x['path'] for x in e.snapshot(self.root)['entries']])

    def test_visible_hidden_receipts_and_historical_current_semantics(self):
        for layout in ('visible', 'hidden'):
            with self.subTest(layout=layout):
                receipt = self.receipt(layout)
                e.validate_receipt(receipt, self.root, current=True, feature=self.feature)
                self.write('source.py', layout)
                e.validate_receipt(receipt, self.root)
                with self.assertRaises(e.EvidenceError):
                    e.validate_receipt(receipt, self.root, current=True)

    def test_unique_runs_deep_copy_contract_and_cross_run_rejection(self):
        run = self.run_record()
        other = self.run_record()
        self.assertNotEqual(run['run_id'], other['run_id'])
        self.feature['acceptance'][0] = 'changed'
        self.assertEqual(run['contract']['acceptance'][0], 'Recovery succeeds')
        with self.assertRaises(e.EvidenceError):
            e.assert_unchanged(run, self.root, self.feature)
        value = {'binding': e.binding(other), 'criteria': [{'index': i, 'status': 'pass', 'reason': 'yes', 'evidence': ['test']} for i in range(2)]}
        with self.assertRaises(e.EvidenceError):
            e.validate_evaluation(value, run)

    def test_strict_schemas_checksums_and_criterion_coverage(self):
        run = self.run_record()
        for field, value in [('attempt', True), ('attempt', 0), ('run_id', 'old'), ('extra', 1)]:
            bad = copy.deepcopy(run)
            bad[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(e.EvidenceError):
                e.validate_run(bad)
        bad = copy.deepcopy(run)
        bad['snapshot']['entries'][0]['mode'] += 1
        with self.assertRaises(e.EvidenceError):
            e.validate_run(bad)
        _, assessment = self.evaluator(run)
        for change in ('missing', 'duplicate', 'failure', 'empty', 'unknown'):
            bad = copy.deepcopy(assessment)
            if change == 'missing': bad['criteria'].pop()
            if change == 'duplicate': bad['criteria'][1]['index'] = 0
            if change == 'failure': bad['criteria'][0]['status'] = 'fail'
            if change == 'empty': bad['criteria'][0]['evidence'] = [' ']
            if change == 'unknown': bad['criteria'][0]['exit_code'] = 0
            with self.subTest(change=change), self.assertRaises(e.EvidenceError):
                e.validate_evaluation(bad, run)
        with self.assertRaises(e.EvidenceError):
            e.decode_json('{"a":1,"a":2}')

    def test_real_process_failure_timeout_launch_error_and_literal_argv(self):
        run = self.run_record()
        literal = '$(touch SHOULD_NOT_EXIST); `false`'
        commands = [
            {'argv': [sys.executable, '-c', 'import sys; print(sys.argv[1]); print("err",file=sys.stderr); sys.exit(7)', literal], 'timeout_seconds': 5},
            {'argv': [sys.executable, '-c', 'import time; time.sleep(5)'], 'timeout_seconds': 1},
            {'argv': ['./missing-executable'], 'timeout_seconds': 1}]
        for i, command in enumerate(commands):
            outcome = e.execute(self.root, run, command, 'check', i)
            with self.assertRaises(e.EvidenceError): e._successful(outcome)
            if i == 0:
                self.assertEqual(outcome['exit_code'], 7)
                self.assertIn(literal, (e._run_dir(self.root, run) / outcome['stdout']['path']).read_text())
            if i == 1: self.assertTrue(outcome['timed_out'])
            if i == 2: self.assertTrue(outcome['launch_error'])
        self.assertFalse((self.root / 'SHOULD_NOT_EXIST').exists())

    def test_evaluator_changes_source_are_rejected_with_logs_retained(self):
        run = self.run_record()
        with self.assertRaises(e.EvidenceError):
            self.evaluator(run, 'from pathlib import Path; Path("source.py").write_text("modified")')
        self.assertTrue((e._run_dir(self.root, run) / 'evaluator-0.json').exists())
        self.assertEqual((self.root / 'source.py').read_text(), 'modified')

    def test_required_check_source_change_and_failure_cannot_form_receipt(self):
        for content in ['#!/bin/sh\nexit 9\n', '#!/bin/sh\necho changed > source.py\n']:
            self.write('init.sh', content)
            run = self.run_record()
            checks = e.execute_required(self.root, run)
            if checks[0]['exit_code']:
                outcome, assessment = self.evaluator(run)
                with self.assertRaises(e.EvidenceError):
                    e.build_receipt(self.root, run, checks, outcome, assessment, self.feature)
            else:
                with self.assertRaises(e.EvidenceError): self.evaluator(run)

    def test_receipt_rejects_tampering_missing_checks_and_cross_run(self):
        receipt = self.receipt()
        for kind in ('checks', 'binding', 'assessment', 'extra'):
            bad = copy.deepcopy(receipt)
            if kind == 'checks': bad['checks'] = []
            if kind == 'binding': bad['checks'][0]['binding']['attempt'] = 2
            if kind == 'assessment': bad['evaluation']['criteria'][0]['reason'] = 'invented'
            if kind == 'extra': bad['agent_claim'] = True
            bad['sha256'] = e.digest({k: v for k, v in bad.items() if k != 'sha256'})
            with self.subTest(kind=kind), self.assertRaises(e.EvidenceError):
                e.validate_receipt(bad, self.root)
        with self.assertRaises(e.EvidenceError):
            e.validate_receipt(receipt, self.root, expected_run=self.run_record())
        directory = e._run_dir(self.root, receipt['run'])
        (directory / 'check-0.stdout').write_text('forged')
        with self.assertRaises(e.EvidenceError): e.validate_receipt(receipt, self.root)

    def test_symlink_evidence_and_no_overwrite(self):
        receipt = self.receipt()
        run = receipt['run']
        with self.assertRaises(FileExistsError):
            e.execute_required(self.root, run)
        log = e._run_dir(self.root, run) / 'check-0.stdout'
        log.unlink()
        os.symlink(self.root / 'source.py', log)
        with self.assertRaises(e.EvidenceError): e.validate_receipt(receipt, self.root)

    def test_schema_distribution_and_runtime_parity(self):
        bundle = ROOT / 'skills/ai-agent-harness/assets/template'
        # Installed harnesses do not vendor another nested template.
        if not bundle.exists():
            return
        for path in ['scripts/run_evidence.py', 'schemas/run.schema.json', 'schemas/evaluation.schema.json', 'schemas/receipt.schema.json', 'docs/run-evidence.md', 'test/unit/test_run_evidence.py']:
            self.assertEqual((ROOT / path).read_bytes(), (bundle / path).read_bytes(), path)


if __name__ == '__main__':
    unittest.main()
