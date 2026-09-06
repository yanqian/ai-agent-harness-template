"""Current-run completion coordinator. Called by the orchestrator, never by roles.

Policy and receipt checks detect accidental stale evidence, not malicious writers.
Lifecycle storage and ownership use state_store; role_boundary compares protected
state and attributable source changes before current-run completion.
"""
import copy
import json
from pathlib import Path
import re
import sys
import uuid

import run_evidence as e
import state_store
import role_boundary as b

POLICY = 'completion-policy.json'


def read(path):
    if path.is_symlink():
        raise e.EvidenceError(f'symlink evidence: {path}')
    return e.decode_json(path.read_bytes())


def contract(feature):
    return {k: feature[k] for k in ('id', 'title', 'description', 'acceptance')}


def legacy_identity(feature):
    return {k: feature.get(k) for k in ('id', 'title', 'description', 'acceptance', 'passes', 'status', 'attempts', 'human_acceptance')}


def legacy_matches(feature, frozen):
    """Replay only append-only observational feedback over a frozen completion.

    The policy never grows or changes. Reopening, edited history, changed criteria
    and attempts cannot become observational feedback. Contradictory legacy state
    remains an exact-match exception, never an authorization for a new transition.
    """
    current = legacy_identity(feature)
    if frozen == current:
        return True
    if not isinstance(frozen, dict):
        return False
    if {k: v for k, v in current.items() if k != 'human_acceptance'} != {k: v for k, v in frozen.items() if k != 'human_acceptance'}:
        return False
    original = frozen.get('human_acceptance')
    expected = copy.deepcopy(original) if isinstance(original, dict) else {'status': 'unreviewed', 'history': []}
    if original is not None and not isinstance(original, dict):
        return False
    if expected.get('status') == 'rejected' or expected.get('reopen_pending'):
        return False
    actual = current.get('human_acceptance')
    history = expected.setdefault('history', [])
    if not isinstance(actual, dict) or not isinstance(history, list) or not isinstance(actual.get('history'), list):
        return False
    events = actual['history']
    if len(events) <= len(history) or events[:len(history)] != history:
        return False
    for event in events[len(history):]:
        if (not isinstance(event, dict) or set(event) != {'at', 'result', 'classification', 'feedback'} or
                any(not isinstance(event[k], str) or not event[k].strip() for k in event)):
            return False
        pair = (event['result'], event['classification'])
        if pair not in {('pass', 'current_feature'), ('fail', 'new_requirement')}:
            return False
        history.append(copy.deepcopy(event))
        expected['last_feedback'] = event['feedback']
        expected['last_recorded_at'] = event['at']
        expected['status'] = 'accepted' if event['result'] == 'pass' else 'new_requirement'
        if event['result'] == 'pass':
            expected['reopen_pending'] = False
        else:
            expected.setdefault('reopen_pending', False)
    return expected == actual


def freeze_policy(harness, state):
    """One-time explicit migration. Never expand an existing compatibility list."""
    path = harness / POLICY
    if not path.exists():
        legacy = {f['id']: legacy_identity(f) for f in state['features']
                  if f.get('passes') is True and f.get('status') == 'done' and not f.get('active_run') and not f.get('completion_receipt')}
        e._write_new(path, {'schema_version': 1, 'legacy': legacy})
    return read_policy(harness)


def read_policy(harness):
    value = read(harness / POLICY)
    if set(value) != {'schema_version', 'legacy'} or type(value['schema_version']) is not int or value['schema_version'] != 1 or not isinstance(value['legacy'], dict):
        raise e.EvidenceError('invalid completion policy')
    for key, feature in value['legacy'].items():
        if not re.fullmatch(r'F[0-9]{3,}', key) or not isinstance(feature, dict) or feature != legacy_identity(feature) or feature['id'] != key or feature['passes'] is not True or feature['status'] != 'done':
            raise e.EvidenceError('invalid frozen legacy entry')
    return value


def paths(harness):
    harness = Path(harness).resolve()
    layout = 'hidden' if harness.name == '.agent-harness' else 'visible'
    return (harness.parent if layout == 'hidden' else harness), layout


def directory(harness, run_id):
    if not isinstance(run_id, str) or not re.fullmatch(r'[0-9a-f]{32}', run_id):
        raise e.EvidenceError('invalid active run ID')
    path = e._safe(harness, 'runs/' + run_id)
    if path.is_symlink():
        raise e.EvidenceError('symlink active run')
    return path


def start(harness, feature, mode):
    read_policy(harness)
    workspace, layout = paths(harness)
    # Validate the command declaration through the existing strict run schema.
    commands = [{'argv': ['./init.sh'], 'timeout_seconds': 600}, *feature.get('required_commands', [])]
    value = {'schema_version': 1, 'run_id': uuid.uuid4().hex, 'feature_id': feature['id'],
             'attempt': feature['attempts'], 'contract': contract(feature), 'criteria_sha256': e.digest(contract(feature)),
             'snapshot': e.snapshot(workspace, layout), 'required_commands': commands}
    e.validate_run(value)
    path = directory(harness, value['run_id'])
    path.mkdir(parents=True, exist_ok=False)
    e._write_new(path / 'handoff.json', {'mode': mode, 'run': value})
    return value['run_id']


def active(harness, feature, mode=None):
    path = directory(harness, feature.get('active_run'))
    value = read(path / 'handoff.json')
    if set(value) != {'mode', 'run'} or value['mode'] not in ('work', 'work-fast'):
        raise e.EvidenceError('invalid run handoff')
    run = value['run']
    e.validate_run(run)
    if (run['run_id'] != feature['active_run'] or run['feature_id'] != feature['id'] or
            run['attempt'] != feature['attempts'] or run['criteria_sha256'] != e.digest(contract(feature)) or
            run['required_commands'][1:] != feature.get('required_commands', []) or
            run['snapshot']['layout'] != paths(harness)[1] or
            feature.get('human_acceptance', {}).get('reopen_pending') is True or
            (mode is not None and mode != value['mode'])):
        raise e.EvidenceError('active run identity, criteria, commands or reopen state changed')
    if (path / 'failure.json').exists():
        raise e.EvidenceError('rejected run cannot resume; start a new attempt')
    return path, run


def validate_coding_output(feature_id, source, output):
    if not isinstance(output, str):
        raise e.EvidenceError('coding output must be text')
    pass_line = f"CODING_PASS: {feature_id}"
    verdicts = [line.strip() for line in output.splitlines() if line.strip() == pass_line or line.strip().startswith(f"CODING_FAIL: {feature_id}:")]
    if not verdicts or verdicts[-1] != pass_line:
        raise e.EvidenceError('coding evidence missing final pass')
    if source == 'provider-native-v1':
        if f"FAST_CODING_EVIDENCE: {feature_id}" not in [line.strip() for line in output.splitlines()]:
            raise e.EvidenceError('provider-native evidence missing fast coding marker')
        if any(line.strip().startswith('EVAL_PASS:') for line in output.splitlines()):
            raise e.EvidenceError('coding evidence contains evaluator approval')


def record_coding(harness, feature, run_id, source, output):
    b.check(harness, *paths(harness), run_id)
    path, run = active(harness, feature)
    if run_id != run['run_id'] or source not in ('runner-coding-child-v1', 'provider-native-v1'):
        raise e.EvidenceError('stale coding run or invalid source')
    mode = read(path / 'handoff.json')['mode']
    if source != ('provider-native-v1' if mode == 'work-fast' else 'runner-coding-child-v1'):
        raise e.EvidenceError('coding source does not match work mode')
    validate_coding_output(feature["id"], source, output)
    b.diff(harness, *paths(harness), run_id)
    candidate = dict(run, snapshot=e.snapshot(*paths(harness)))
    e.validate_run(candidate)
    value = {'binding': e.binding(candidate), 'source': source, 'output': output, 'sha256': e.digest(output)}
    e._write_new(path / 'coding.json', value)
    # Candidate manifest is immutable; interruption between these writes fails closed.
    e._write_new(path / 'run.json', candidate)
    return candidate


def candidate(harness, feature):
    b.check(harness, *paths(harness), feature.get('active_run'))
    path, handoff = active(harness, feature)
    run = read(path / 'run.json')
    e.validate_run(run)
    if {k: v for k, v in run.items() if k != 'snapshot'} != {k: v for k, v in handoff.items() if k != 'snapshot'}:
        raise e.EvidenceError('candidate does not match handoff')
    coding = read(path / 'coding.json')
    mode = read(path / 'handoff.json')['mode']
    if (set(coding) != {'binding', 'source', 'output', 'sha256'} or coding['binding'] != e.binding(run) or
            coding['sha256'] != e.digest(coding['output']) or
            coding['source'] != ('provider-native-v1' if mode == 'work-fast' else 'runner-coding-child-v1')):
        raise e.EvidenceError('invalid or cross-run coding receipt')
    validate_coding_output(feature['id'], coding['source'], coding['output'])
    e.assert_unchanged(run, paths(harness)[0], feature)
    return path, run


def finalize(harness, feature, evaluator_prompt):
    """Shared gate; persist validated receipt first. Caller then links and marks done."""
    state = state_store.load(harness / "feature_list.json")
    if not state_store.ready(state, feature):
        raise e.EvidenceError("feature dependencies are not ready")
    path, run = candidate(harness, feature)
    workspace, layout = paths(harness)
    if (path / 'receipt.json').exists():
        b.verify_scope(path)
        receipt = read(path / 'receipt.json')
        e.validate_receipt(receipt, workspace, expected_run=run, current=True, feature=feature)
        return path / 'receipt.json'
    if any(path.glob('check-*')) or any(path.glob('evaluator-*')):
        raise e.EvidenceError('interrupted verification without receipt; restart with a new run')
    try:
        checks = e.execute_required(workspace, run)
    finally:
        b.check(harness, workspace, layout, run['run_id'], 'evaluation')
    for check in checks:
        e._successful(check)
    b.check(harness, workspace, layout, run['run_id'], 'evaluation')
    e.assert_unchanged(run, workspace, feature)
    # The bridge handles only our documented adapter stdout contract, no provider JSONL guesses.
    assessment = {'scope': {'status': 'pass', 'reason': '<assess full attributable changes.json for relevance to this Feature>'}, 'binding': e.binding(run), 'criteria': [
        {'index': i, 'status': 'pass', 'reason': '<your assessment>', 'evidence': ['<actual evidence>']}
        for i in range(len(run['contract']['acceptance']))]}
    prompt = (evaluator_prompt + '\n\n# Current-run receipt evaluation (overrides final text verdict format)\n'
              'Inspect the candidate and required check logs at ' + str(path) + '.\n'
              'Read changes.json: full before/after bytes, index/mode metadata and diff attributable to this run. Report scope relevance in scope even without an allowlist. Do not modify source, lifecycle state, or contracts. Return ONLY one JSON object, no Markdown or PASS lines. '
              'Use this exact binding and assess every zero-based acceptance index with pass/fail, a concrete reason and evidence. '
              'A sample shape follows; replace the placeholder assessments:\n' + json.dumps(assessment) + '\n'
              'Frozen acceptance criteria:\n' + json.dumps(run['contract']['acceptance']) + '\n')
    (path / 'evaluator-prompt.txt').write_text(prompt)
    command = {'argv': [sys.executable, str(harness / 'scripts/completion_evaluator.py'), str(harness), run['run_id']], 'timeout_seconds': 3600}
    try:
        outcome, evaluation = e.evaluate(workspace, run, command)
    finally:
        b.check(harness, workspace, layout, run['run_id'], 'evaluation')
    b.verify_scope(path)
    # Reload state after evaluator: criteria changes are not excluded by snapshot checks.
    current = next(f for f in read(harness / 'feature_list.json')['features'] if f['id'] == feature['id'])
    active(harness, current)
    e.build_receipt(workspace, run, checks, outcome, evaluation, current)
    return path / 'receipt.json'


def verify_history(harness, state):
    try:
        state_store.validate(state, harness)
    except state_store.StateError as exc:
        raise e.EvidenceError(str(exc)) from exc
    policy = read_policy(harness)
    workspace, _ = paths(harness)
    for feature in state['features']:
        if feature.get('passes') is not True or feature.get('status') != 'done':
            continue
        old = policy['legacy'].get(feature['id'])
        if legacy_matches(feature, old) and not feature.get('completion_receipt') and not feature.get('active_run'):
            if feature.get('human_acceptance', {}).get('reopen_pending') or feature.get('human_acceptance', {}).get('status') == 'rejected':
                print(f"legacy metadata contradiction: {feature['id']} done with rejected/reopen metadata; frozen history only", file=sys.stderr)
            continue
        link = feature.get('completion_receipt')
        if not isinstance(link, str) or not re.fullmatch(r'runs/[0-9a-f]{32}/receipt.json', link):
            raise e.EvidenceError(f"{feature['id']}: missing current-run completion receipt")
        receipt = read(e._safe(harness, link))
        e.validate_receipt(receipt, workspace)
        run = receipt['run']
        if (run['run_id'] != feature.get('active_run') or run['feature_id'] != feature['id'] or
                run['attempt'] != feature['attempts'] or run['criteria_sha256'] != e.digest(contract(feature)) or
                link != f"runs/{run['run_id']}/receipt.json"):
            raise e.EvidenceError(f"{feature['id']}: completion receipt identity mismatch")
    return True
