"""Real POSIX process tests: locks, atomic visibility, interruption and stale writes."""
import importlib.util
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import state_store as store


def feature(fid='F001', **fields):
    return dict(id=fid, title='test', description='test', acceptance=['works'],
                passes=False, status='todo', attempts=0, last_error='', **fields)


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'feature_list.json'
        self.write({'custom': {'keep': 1}, 'features': [feature(custom=['keep'])]})

    def write(self, data):
        self.path.write_text(json.dumps(data))

    def child(self, code, *args):
        env = dict(os.environ, PYTHONPATH=str(ROOT / 'scripts'))
        return subprocess.Popen([sys.executable, '-u', '-c', code, str(self.path), *args],
                                env=env, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def finish(self, child):
        out, err = child.communicate(timeout=15)
        self.assertEqual(child.returncode, 0, err)
        return out

    def test_dependency_graph_validation_and_no_mutation(self):
        for deps in ('F002', [1], ['F002', 'F002'], ['F001'], ['F999']):
            with self.subTest(deps=deps):
                self.write({'features': [feature(depends_on=deps), feature('F002')]})
                original = self.path.read_bytes()
                with self.assertRaises(store.StateError):
                    store.load(self.path)
                self.assertEqual(self.path.read_bytes(), original)
        self.write({'features': [feature(depends_on=['F002']), feature('F002', depends_on=['F001'])]})
        with self.assertRaisesRegex(store.StateError, 'cycle'):
            store.load(self.path)

    def test_readiness_including_fast_resume(self):
        spec = importlib.util.spec_from_file_location('orch_state_test', ROOT / 'orchestrator.py')
        orch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orch)
        first, second = feature(), feature('F002', depends_on=['F001'])
        second.update(status='in_progress', active_run='old', priority='P0')
        data = {'features': [first, second]}
        self.assertEqual(orch.pick_fast_feature(data, 3)['id'], 'F001')
        first.update(passes=True, status='done')
        self.assertEqual(orch.pick_fast_feature(data, 3)['id'], 'F002')
        first['human_acceptance'] = {'reopen_pending': True, 'status': 'rejected'}
        self.assertFalse(store.ready(data, second))
        with self.assertRaises(ValueError):
            orch.pick_fast_feature(data, 3)

    def test_real_competing_owners_and_readers(self):
        holder = self.child("import state_store as s,sys; from pathlib import Path\np=Path(sys.argv[1])\nwith s.ownership(p):\n print('locked',flush=True)\n sys.stdin.readline()")
        try:
            self.assertEqual(holder.stdout.readline().strip(), 'locked')
            contender = self.child("import state_store as s,sys; from pathlib import Path\nwith s.ownership(Path(sys.argv[1])): pass")
            _, err = contender.communicate(timeout=15)
            self.assertNotEqual(contender.returncode, 0)
            self.assertIn('lock contention', err)
            self.assertEqual(store.load(self.path)['custom'], {'keep': 1})
            env = dict(os.environ, HARNESS_FEATURE_LIST=str(self.path), HARNESS_RUNS_DIR=str(self.path.parent / 'runs'))
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/human-eval.py'), 'F001', '--result', 'fail', '--classification', 'current_feature', '--feedback', 'retry'], env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('owner lock contention', result.stderr)
            self.assertEqual(store.load(self.path)['features'][0]['attempts'], 0)
        finally:
            self.finish(holder)
        with store.ownership(self.path):
            pass

    def test_real_stale_writer_preserves_unknown_fields(self):
        stale = self.child("import state_store as s,sys; from pathlib import Path\np=Path(sys.argv[1]); d=s.load(p); print('loaded',flush=True); sys.stdin.readline(); d['features'][0]['attempts']=99; s.save(p,d)")
        try:
            self.assertEqual(stale.stdout.readline().strip(), 'loaded')
            data = store.load(self.path)
            data['features'][0]['attempts'] = 1
            store.save(self.path, data)
            _, err = stale.communicate('\n', timeout=15)
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn('stale-state write', err)
            fresh = store.load(self.path)
            self.assertEqual(fresh['features'][0]['attempts'], 1)
            self.assertEqual(fresh['features'][0]['custom'], ['keep'])
            self.assertEqual(list(fresh), ['custom', 'features'])
        finally:
            if stale.poll() is None:
                stale.kill(); stale.communicate()

    def test_kill_before_atomic_replace_keeps_original_and_releases_lock(self):
        original = self.path.read_bytes()
        child = self.child("import state_store as s,sys; from pathlib import Path\np=Path(sys.argv[1]); d=s.load(p); d['custom']={'large':'x'*1000000}\ndef stop(*args):\n print('before replace',flush=True); sys.stdin.readline()\ns.os.replace=stop\ns.save(p,d)")
        try:
            self.assertEqual(child.stdout.readline().strip(), 'before replace')
            child.kill(); child.communicate(timeout=15)
            self.assertEqual(self.path.read_bytes(), original)
            data = store.load(self.path)
            data['custom']['after'] = True
            store.save(self.path, data)
            self.assertTrue(store.load(self.path)['custom']['after'])
        finally:
            if child.poll() is None:
                child.kill(); child.communicate()

    def test_short_write_lock_contention_and_atomic_reader_visibility(self):
        data = store.load(self.path)
        holder = self.child("import state_store as s,sys; from pathlib import Path\nwith s.lock(Path(sys.argv[1])):\n print('locked',flush=True); sys.stdin.readline()")
        try:
            self.assertEqual(holder.stdout.readline().strip(), 'locked')
            with self.assertRaisesRegex(store.StateError, 'state lock contention'):
                store.save(self.path, data)
        finally:
            self.finish(holder)
        writer = self.child("import state_store as s,sys; from pathlib import Path\np=Path(sys.argv[1])\nfor i in range(40):\n d=s.load(p); d['payload']=str(i)*100000; s.save(p,d)\n")
        try:
            while writer.poll() is None:
                observed = json.loads(self.path.read_bytes())
                self.assertEqual(observed['custom'], {'keep': 1})
            self.finish(writer)
        finally:
            if writer.poll() is None:
                writer.kill(); writer.communicate()

    def test_reopen_archives_evidence_and_retry_keeps_history(self):
        f = feature()
        f.update(passes=True, status='done', attempts=4, active_run='a'*32, completion_receipt='runs/old/receipt.json')
        self.write({'features': [f]})
        env = dict(os.environ, HARNESS_FEATURE_LIST=str(self.path), HARNESS_RUNS_DIR=str(self.path.parent / 'runs'))
        args = [sys.executable, str(ROOT / 'scripts/human-eval.py'), 'F001', '--result', 'fail', '--classification', 'current_feature', '--feedback', 'unmet']
        for _ in range(2):
            result = subprocess.run(args, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        reopened = store.load(self.path)['features'][0]
        self.assertNotIn('active_run', reopened)
        self.assertNotIn('completion_receipt', reopened)
        self.assertEqual(len(reopened['completion_history']), 1)
        self.assertEqual(len(reopened['human_acceptance']['history']), 2)
        self.assertEqual(len(list((self.path.parent / 'runs').glob('*human-eval.md'))), 2)
        spec = importlib.util.spec_from_file_location('orch_reopen', ROOT / 'orchestrator.py')
        orch = importlib.util.module_from_spec(spec); spec.loader.exec_module(orch)
        with patch.object(orch, 'FEATURES_PATH', self.path):
            orch.mark_in_progress('F001')
        retry = store.load(self.path)['features'][0]
        self.assertEqual(retry['attempts'], 5)
        self.assertEqual(retry['human_acceptance']['status'], 'unreviewed')
        self.assertFalse(retry['human_acceptance']['reopen_pending'])
        self.assertEqual(retry['completion_history'], reopened['completion_history'])
        import completion
        with self.assertRaises(ValueError):
            completion.active(self.path.parent, retry)

    def test_new_done_reopen_contradiction_fails_save(self):
        data = store.load(self.path)
        data['features'][0].update(passes=True, status='done', human_acceptance={'status':'rejected'})
        with self.assertRaisesRegex(store.StateError, 'done with rejected'):
            store.save(self.path, data)
        self.assertFalse(store.load(self.path)['features'][0]['passes'])

    def test_legacy_feedback_preserves_frozen_policy_and_history_validity(self):
        import completion
        for hidden in (False, True):
            with self.subTest(hidden=hidden), tempfile.TemporaryDirectory() as tmp:
                h = Path(tmp) / '.agent-harness' if hidden else Path(tmp)
                h.mkdir(exist_ok=True)
                p = h / 'feature_list.json'
                f = feature()
                f.update(passes=True, status='done', attempts=1,
                         human_acceptance={'status': 'accepted', 'history': [{'legacy': 'keep'}], 'custom': 42})
                original = copy.deepcopy(f)
                state = {'features': [f]}
                p.write_text(json.dumps(state))
                completion.freeze_policy(h, state)
                policy = (h / completion.POLICY).read_bytes()
                env = dict(os.environ, HARNESS_FEATURE_LIST=str(p), HARNESS_RUNS_DIR=str(h / 'runs'))
                for result, classification in [('pass', 'current_feature'), ('fail', 'new_requirement'), ('pass', 'current_feature')]:
                    command = [sys.executable, str(ROOT / 'scripts/human-eval.py'), 'F001', '--result', result,
                               '--classification', classification, '--feedback', 'observational feedback']
                    r = subprocess.run(command, env=env, capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, r.stderr)
                    state = store.load(p)
                    self.assertTrue(completion.verify_history(h, state))
                    self.assertEqual((h / completion.POLICY).read_bytes(), policy)
                    self.assertTrue(state['features'][0]['passes'])
                updated = state['features'][0]
                self.assertEqual(len(updated['human_acceptance']['history']), 4)
                self.assertEqual(updated['human_acceptance']['custom'], 42)
                frozen = completion.legacy_identity(original)
                for mutation in ('history', 'criteria', 'attempt', 'reopen'):
                    bad = copy.deepcopy(updated)
                    if mutation == 'history':
                        bad['human_acceptance']['history'][0] = {'legacy': 'edited'}
                    elif mutation == 'criteria':
                        bad['acceptance'] = ['relaxed']
                    elif mutation == 'attempt':
                        bad['attempts'] += 1
                    else:
                        bad['human_acceptance']['history'][-1].update(result='fail', classification='current_feature')
                    self.assertFalse(completion.legacy_matches(bad, frozen), mutation)

    def test_feedback_rejects_invalid_legacy_transition_before_publication(self):
        import completion
        f = feature()
        f.update(passes=True, status='done', human_acceptance={'status': 'rejected', 'reopen_pending': True})
        state = {'features': [f]}
        self.write(state)
        completion.freeze_policy(self.path.parent, state)
        original = self.path.read_bytes()
        env = dict(os.environ, HARNESS_FEATURE_LIST=str(self.path), HARNESS_RUNS_DIR=str(self.path.parent / 'runs'))
        command = [sys.executable, str(ROOT / 'scripts/human-eval.py'), 'F001', '--result', 'pass',
                   '--classification', 'current_feature', '--feedback', 'cannot erase legacy contradiction']
        r = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('No feedback/state was published', r.stderr)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse(list((self.path.parent / 'runs').glob('*human-eval.md')))
        command[command.index('pass')] = 'fail'
        r = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(completion.verify_history(self.path.parent, store.load(self.path)))

    def test_first_legacy_feedback_batch_and_reopen_cannot_reuse_exemption(self):
        import completion
        f = feature()
        f.update(passes=True, status='done')
        state = {'features': [f]}
        self.write(state)
        completion.freeze_policy(self.path.parent, state)
        frozen = completion.legacy_identity(f)
        batch = self.path.parent / 'feedback.json'
        batch.write_text(json.dumps([
            {'feature_id': 'F001', 'result': 'fail', 'classification': 'new_requirement', 'feedback': 'new value'},
            {'feature_id': 'F001', 'result': 'pass', 'classification': 'current_feature', 'feedback': 'existing value works'}]))
        env = dict(os.environ, HARNESS_FEATURE_LIST=str(self.path), HARNESS_RUNS_DIR=str(self.path.parent / 'runs'))
        r = subprocess.run([sys.executable, str(ROOT / 'scripts/human-eval.py'), '--batch-file', str(batch)],
                           env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(completion.verify_history(self.path.parent, store.load(self.path)))
        r = subprocess.run([sys.executable, str(ROOT / 'scripts/human-eval.py'), 'F001', '--result', 'fail',
                            '--classification', 'current_feature', '--feedback', 'actually unmet'],
                           env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        reopened = store.load(self.path)['features'][0]
        self.assertFalse(reopened['passes'])
        reopened.update(passes=True, status='done')
        self.assertFalse(completion.legacy_matches(reopened, frozen))


if __name__ == '__main__':
    unittest.main()
