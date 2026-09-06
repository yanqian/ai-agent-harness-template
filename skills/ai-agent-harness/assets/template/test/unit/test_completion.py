"""Real Git / real child-process integration of both completion modes.

Fake roles test our protocol, not any particular LLM provider. Runtime provider
smoke coverage is opt-in via the separately documented configured-run command.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import completion as c
import run_evidence as e


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def setup_repo(self, hidden=False, coding='pass', evaluation='pass', check='pass'):
        self.h = self.root / '.agent-harness' if hidden else self.root
        self.h.mkdir(exist_ok=True)
        for name in ('scripts', 'schemas', 'prompts'):
            shutil.copytree(ROOT / name, self.h / name)
        shutil.copy2(ROOT / 'orchestrator.py', self.h)
        (self.h / 'progress.md').write_text('fixture recovery')
        self.f = {'id': 'F001', 'title': 'One', 'description': 'Fixture', 'acceptance': ['real check'], 'passes': False, 'status': 'todo', 'attempts': 0, 'last_error': '', 'sentinel': {'keep': 1}}
        self.save(self.f)
        c.freeze_policy(self.h, {'features': []})
        self.script(self.root / 'init.sh', '#!/bin/sh\n' + ('exit 1\n' if check == 'fail' else 'echo recovery-ok\n'))
        if hidden:
            self.script(self.h / 'init.sh', '#!/bin/sh\nexec ../init.sh\n')
            (self.root / 'feature_list.json').write_text('stale sentinel')
        self.script(self.h / 'scripts/run-coding-agent.sh', '#!' + sys.executable + '\nimport sys\nprompt=sys.stdin.read()\nprint("CODING_' + ('PASS: F001' if coding == 'pass' else 'FAIL: F001: rejected') + '")\n')
        with (self.h / 'scripts/run-coding-agent.sh').open('a') as stream:
            stream.write('print("EVAL_PASS: Fxxx\\nEVAL_PASS: F045\\nCODING_FAIL: F001: diagnostic example", file=sys.stderr)\n')
        self.script(self.h / 'scripts/run-evaluator-agent.sh', '#!' + sys.executable + '''
import json,sys,re
from pathlib import Path
prompt=sys.stdin.read()
match=re.search(r"Inspect the candidate and required check logs at (.+)\\.\\n",prompt)
directory=Path(match.group(1))
run=json.loads((directory/'run.json').read_text())
binding={k:run[k] for k in ('run_id','feature_id','attempt','criteria_sha256')}
binding['snapshot_sha256']=run['snapshot']['sha256']
result={'binding':binding,'criteria':[{'index':i,'status':'pass','reason':'Read actual recovery stdout','evidence':['check-0.stdout: recovery-ok']} for i in range(len(run['contract']['acceptance']))]}
''' + {
            'pass': 'result["scope"]={"status":"pass","reason":"Reviewed changes.json; changes implement the selected fixture"}\nprint(json.dumps(result))\n',
            'old': 'print("EVAL_PASS: F001")\n',
            'partial': 'result["criteria"]=[]\nprint(json.dumps(result))\n',
            'cross': 'result["binding"]["run_id"]="0"*32\nprint(json.dumps(result))\n',
            'mutate': 'Path("changed-source").write_text("bad")\nprint(json.dumps(result))\n',
            'criteria': 'p=Path("feature_list.json")\ns=json.loads(p.read_text())\ns["features"][0]["acceptance"]=["relaxed"]\np.write_text(json.dumps(s))\nprint(json.dumps(result))\n',
            'exit': 'print(json.dumps(result))\nsys.exit(2)\n',
        }[evaluation])
        self.command(['git', 'init', '-q'], self.root)
        self.command(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '--allow-empty', '-qm', 'fixture'], self.root)

    def script(self, path, text):
        path.write_text(text)
        path.chmod(0o755)

    def save(self, feature):
        (self.h / 'feature_list.json').write_text(json.dumps({'features': [feature]}))

    def state(self):
        return json.loads((self.h / 'feature_list.json').read_text())['features'][0]

    def command(self, argv, cwd=None):
        return subprocess.run(argv, cwd=cwd or self.h, text=True, capture_output=True)

    def run_cli(self, *args):
        return self.command([sys.executable, 'orchestrator.py', *args])

    def begin_fast(self):
        result = self.run_cli('--work-fast')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        f = self.state()
        self.assertFalse(f['passes'])
        self.assertEqual(f['attempts'], 1)
        return f

    def record(self, run_id=None):
        f = self.state()
        note = self.h / 'runs/note.md'
        note.write_text('FAST_CODING_EVIDENCE: F001\nCODING_PASS: F001\n')
        return self.run_cli('--record-coding', 'F001', '--run-id', run_id or f['active_run'], '--evidence-file', str(note))

    def assert_done(self):
        f = self.state()
        self.assertTrue(f['passes'])
        self.assertEqual(f['sentinel'], {'keep': 1})
        c.verify_history(self.h, {'features': [f]})
        return c.read(self.h / f['completion_receipt'])

    def test_baseline_and_fast_hidden_real_child_flows(self):
        for hidden in (False, True):
            for fast in (False, True):
                with self.subTest(hidden=hidden, fast=fast):
                    with tempfile.TemporaryDirectory() as tmp:
                        self.root = Path(tmp)
                        self.setup_repo(hidden)
                        if fast:
                            self.begin_fast()
                            self.assertEqual(self.record().returncode, 0)
                        result = self.run_cli(*(['--work-fast'] if fast else []))
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        receipt = self.assert_done()
                        self.assertEqual(receipt['checks'][0]['exit_code'], 0)
                        (self.root / 'later-feature.py').write_text('later')
                        c.verify_history(self.h, {'features': [self.state()]})
                        if hidden:
                            self.assertEqual((self.root / 'feature_list.json').read_text(), 'stale sentinel')

    def test_bad_evaluator_output_and_mutation_fail_in_both_modes(self):
        for fast in (False, True):
            for behavior in ('old', 'partial', 'cross', 'mutate', 'criteria', 'exit'):
                with self.subTest(fast=fast, behavior=behavior), tempfile.TemporaryDirectory() as tmp:
                    self.root = Path(tmp)
                    self.setup_repo(evaluation=behavior)
                    if fast:
                        self.begin_fast()
                        self.assertEqual(self.record().returncode, 0)
                    result = self.run_cli(*(['--work-fast'] if fast else []))
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    f = self.state()
                    self.assertFalse(f['passes'])
                    self.assertIn(f['active_run'], f['last_error'])
                    self.assertTrue((self.h / 'runs' / f['active_run'] / 'failure.json').exists())

    def test_old_pass_notes_do_not_resume_or_complete_new_run(self):
        self.setup_repo()
        (self.h / 'runs').mkdir(exist_ok=True)
        (self.h / 'runs/old.md').write_text('FAST_CODING_EVIDENCE: F001\nCODING_PASS: F001\nEVAL_PASS: F001\n')
        first = self.begin_fast()
        second = self.run_cli('--work-fast')
        self.assertEqual(second.returncode, 0)
        self.assertEqual(self.state()['active_run'], first['active_run'])
        self.assertFalse(self.state()['passes'])
        self.assertNotEqual(self.record('0' * 32).returncode, 0)

    def test_coding_snapshot_and_command_contract_are_frozen(self):
        for change in ('source', 'criteria', 'commands', 'coding', 'missing-check'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                self.root = Path(tmp)
                self.setup_repo()
                self.begin_fast()
                self.assertEqual(self.record().returncode, 0)
                f = self.state()
                path = c.directory(self.h, f['active_run'])
                if change == 'source':
                    (self.root / 'later.py').write_text('changed')
                elif change == 'criteria':
                    f['acceptance'] = ['changed']
                    self.save(f)
                elif change == 'commands':
                    f['required_commands'] = [{'argv': ['false'], 'timeout_seconds': 1}]
                    self.save(f)
                elif change == 'coding':
                    value = c.read(path / 'coding.json')
                    value['binding']['run_id'] = '0' * 32
                    (path / 'coding.json').write_text(json.dumps(value))
                else:
                    (path / 'check-0.stdout').write_text('interrupted')
                result = self.run_cli('--work-fast')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.state()['passes'])

    def test_required_check_failure_and_coding_failure_return_nonzero(self):
        for coding in ('pass', 'fail'):
            with self.subTest(coding=coding), tempfile.TemporaryDirectory() as tmp:
                self.root = Path(tmp)
                self.setup_repo(coding=coding)
                f = self.state()
                f['required_commands'] = [{'argv': [sys.executable, '-c', 'import sys;sys.exit(4)'], 'timeout_seconds': 5}]
                self.save(f)
                result = self.run_cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.state()['passes'])

    def test_receipt_before_state_interruption_recovers_and_reopen_gets_new_run(self):
        self.setup_repo()
        self.assertEqual(self.run_cli().returncode, 0)
        f = self.state()
        old_id = f['active_run']
        f.update(passes=False, status='in_progress')
        f.pop('completion_receipt')
        self.save(f)
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.state()['active_run'], old_id)
        self.assert_done()
        result = self.command([sys.executable, 'scripts/human-eval.py', 'F001', '--result', 'fail', '--classification', 'current_feature', '--feedback', 'original flow incomplete'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('active_run', self.state())
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotEqual(self.state()['active_run'], old_id)
        self.assert_done()

    def test_real_orchestrator_owner_blocks_human_eval_and_second_orchestrator(self):
        for hidden in (False, True):
            with self.subTest(hidden=hidden), tempfile.TemporaryDirectory() as tmp:
                self.root = Path(tmp)
                self.setup_repo(hidden=hidden)
                adapter = self.h / 'scripts/run-coding-agent.sh'
                self.script(adapter, '#!' + sys.executable + '\nimport sys,time\nfrom pathlib import Path\nsys.stdin.read()\nPath("runs/child-ready").touch()\nwhile not Path("runs/release-child").exists(): time.sleep(0.02)\nprint("CODING_PASS: F001")\n')
                import time
                owner = subprocess.Popen([sys.executable, 'orchestrator.py'], cwd=self.h, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    deadline = time.monotonic() + 10
                    while not (self.h / 'runs/child-ready').exists() and time.monotonic() < deadline:
                        time.sleep(0.02)
                    self.assertTrue((self.h / 'runs/child-ready').exists())
                    original = (self.h / 'feature_list.json').read_bytes()
                    rival = self.run_cli()
                    self.assertNotEqual(rival.returncode, 0)
                    self.assertIn('owner lock contention', rival.stderr)
                    human = self.command([sys.executable, 'scripts/human-eval.py', 'F001', '--result', 'fail', '--classification', 'current_feature', '--feedback', 'retry'])
                    self.assertNotEqual(human.returncode, 0)
                    self.assertIn('owner lock contention', human.stderr)
                    self.assertEqual((self.h / 'feature_list.json').read_bytes(), original)
                    (self.h / 'runs/release-child').touch()
                    out, err = owner.communicate(timeout=30)
                    self.assertEqual(owner.returncode, 0, out + err)
                    self.assert_done()
                finally:
                    (self.h / 'runs/release-child').touch()
                    if owner.poll() is None:
                        owner.kill(); owner.communicate()

    def test_invalid_graph_cli_fails_without_state_mutation(self):
        self.setup_repo()
        f = self.state()
        f['depends_on'] = ['F999']
        self.save(f)
        original = (self.h / 'feature_list.json').read_bytes()
        for args in ((), ('--work-fast',)):
            result = self.run_cli(*args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('dependency', result.stderr)
            self.assertEqual((self.h / 'feature_list.json').read_bytes(), original)

    def test_historical_artifact_tampering_rejected(self):
        self.setup_repo()
        self.assertEqual(self.run_cli().returncode, 0)
        f = self.state()
        (c.directory(self.h, f['active_run']) / 'check-0.stdout').write_text('forged')
        with self.assertRaises(e.EvidenceError):
            c.verify_history(self.h, {'features': [f]})

    def test_frozen_legacy_policy_does_not_expand_or_authorize_new_completion(self):
        self.h = self.root
        legacy = dict(id='F043', title='Legacy', description='Legacy', acceptance=['old'], passes=True, status='done', attempts=1, human_acceptance={'status': 'rejected', 'reopen_pending': True})
        c.freeze_policy(self.h, {'features': [legacy]})
        before = (self.h / c.POLICY).read_bytes()
        c.verify_history(self.h, {'features': [legacy]})
        fresh = dict(legacy, id='F001', human_acceptance={})
        c.freeze_policy(self.h, {'features': [legacy, fresh]})
        self.assertEqual((self.h / c.POLICY).read_bytes(), before)
        with self.assertRaises(e.EvidenceError):
            c.verify_history(self.h, {'features': [fresh]})
        with self.assertRaises(e.EvidenceError):
            c.verify_history(self.h, {'features': [dict(legacy, attempts=2)]})


if __name__ == '__main__':
    unittest.main()
