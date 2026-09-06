"""Post-role accidental-write detection. Not a same-account security sandbox."""
import base64
import difflib
import os
import re
import uuid

import run_evidence as e


def read(path):
    if path.is_symlink():
        raise e.EvidenceError(f'symlink boundary artifact: {path}')
    return e.decode_json(path.read_bytes())


def selection(workspace, values):
    if not isinstance(values, list) or len(set(values)) != len(values):
        raise e.EvidenceError('boundary paths must be a unique list')
    for value in values:
        e._relative(value)
        if value == '.git' or value.startswith('.git/') or any(c in value for c in '*?['):
            raise e.EvidenceError(f'boundary paths must be literal project-relative paths: {value}')
        e._safe(workspace, value)
    return values


def matches(path, values):
    return any(path == v or path.startswith(v + '/') for v in values)


def content(workspace, entry):
    path = e._safe(workspace, entry['path'])
    if entry['kind'] == 'deleted':
        return b''
    if entry['kind'] == 'symlink':
        return os.fsencode(os.readlink(path))
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        return stream.read()


def capture(harness, workspace, layout, run_id, adopt, allowed):
    selection(workspace, adopt)
    if allowed is not None:
        selection(workspace, allowed)
    snap = e.snapshot(workspace, layout)
    dirty = set()
    for args in [('diff', '--cached', '--name-only', '-z'), ('diff', '--name-only', '-z'), ('ls-files', '--others', '-z')]:
        dirty.update(os.fsdecode(p) for p in e._git(workspace, *args).split(b'\0') if p)
    prefix = '' if layout == 'visible' else '.agent-harness/'
    value = {'version': 1, 'run_id': run_id, 'state': read(harness / 'feature_list.json'),
             'snapshot': snap, 'dirty': sorted(dirty), 'adopt': adopt, 'allowed': allowed,
             'contracts': [prefix + p for p in ('SPEC.md', 'QUALITY.md', 'completion-policy.json')],
             'contents': {v['path']: base64.b64encode(content(workspace, v)).decode('ascii') for v in snap['entries']}}
    if snap != e.snapshot(workspace, layout):
        raise e.EvidenceError('source changed during boundary capture')
    directory = harness / 'runs' / run_id
    e._write_new(directory / 'boundary-required.json', {'run_id': run_id, 'feature_id': next(f['id'] for f in value['state']['features'] if f.get('active_run') == run_id)})
    e._write_new(directory / 'boundary.json', value)


def reject(directory, phase, reasons):
    report = {'phase': phase, 'violations': reasons, 'recovery': 'Preserve files; inspect violation and restore unauthorized edits manually, then --restart-run FEATURE --run-id RUN. Declare --adopt-dirty and --allow-path before the new coding handoff.'}
    e._write_new(directory / ('violation-' + uuid.uuid4().hex + '.json'), report)
    if not (directory / 'failure.json').exists():
        e._write_new(directory / 'failure.json', report)
    raise e.EvidenceError('role boundary violation: ' + '; '.join(reasons) + '; explicit --restart-run required')


def check(harness, workspace, layout, run_id, phase='coding'):
    if not isinstance(run_id, str) or not re.fullmatch(r'[0-9a-f]{32}', run_id):
        raise e.EvidenceError('invalid boundary run ID')
    directory = e._safe(harness, 'runs/' + run_id)
    if directory.is_symlink():
        raise e.EvidenceError('symlink boundary run directory')
    try:
        boundary = read(directory / 'boundary.json')
        if boundary['version'] != 1 or boundary['run_id'] != run_id:
            raise e.EvidenceError('invalid boundary identity')
        selection(workspace, boundary['adopt'])
        if boundary['allowed'] is not None:
            selection(workspace, boundary['allowed'])
        now_state = read(harness / 'feature_list.json')
        current = e.snapshot(workspace, layout)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        reject(directory, phase, ['missing/invalid boundary: ' + str(exc)])
    reasons = []
    if now_state != boundary['state']:
        before = boundary['state']
        for key in set(before) | set(now_state):
            if before.get(key) != now_state.get(key):
                if key == 'features':
                    old = {v['id']: v for v in before[key]}
                    new = {v['id']: v for v in now_state.get(key, [])}
                    reasons.extend('feature_list.json:' + fid for fid in sorted(set(old) | set(new)) if old.get(fid) != new.get(fid))
                    if list(old) != list(new):
                        reasons.append('feature_list.json: feature order/IDs')
                else:
                    reasons.append('feature_list.json:' + key)
    old = {v['path']: v for v in boundary['snapshot']['entries']}
    new = {v['path']: v for v in current['entries']}
    changed = sorted(p for p in set(old) | set(new) if old.get(p) != new.get(p))
    for p in changed:
        if p in boundary['contracts']:
            reasons.append('protected contract: ' + p)
        if p in boundary['dirty'] and not matches(p, boundary['adopt']):
            reasons.append('pre-existing dirty path: ' + p)
        if boundary['allowed'] is not None and not matches(p, boundary['allowed']):
            reasons.append('outside allowed paths: ' + p)
    if phase == 'evaluation':
        candidate = read(directory / 'run.json')['snapshot']
        expected = {v['path']: v for v in candidate['entries']}
        reasons.extend('evaluation source edit: ' + p for p in sorted(set(expected) | set(new)) if expected.get(p) != new.get(p))
    if reasons:
        reject(directory, phase, reasons)
    return boundary, current, changed


def diff(harness, workspace, layout, run_id):
    boundary, current, changed = check(harness, workspace, layout, run_id)
    entries = {v['path']: v for v in current['entries']}
    previous = {v['path']: v for v in boundary['snapshot']['entries']}
    result = []
    for p in changed:
        before = base64.b64decode(boundary['contents'].get(p, ''))
        after = content(workspace, entries[p]) if p in entries else b''
        result.append({'path': p, 'before_base64': base64.b64encode(before).decode('ascii'),
                       'after_base64': base64.b64encode(after).decode('ascii'),
                       'before_entry': previous.get(p), 'after_entry': entries.get(p),
                       'diff': ''.join(difflib.unified_diff(before.decode('utf-8', 'replace').splitlines(True), after.decode('utf-8', 'replace').splitlines(True), fromfile='before/' + p, tofile='after/' + p))})
    e._write_new(harness / 'runs' / run_id / 'changes.json', {'run_id': run_id, 'changes': result})


def scope(assessment, directory):
    """The new bridge requires a scope assessment, then emits legacy criterion JSON.

    Separate runner artifact binds the actual captured provider response and diff.
    Historical receipts retain their original evaluation schema.
    """
    judgment = assessment.pop('scope', None)
    if (not isinstance(judgment, dict) or set(judgment) != {'status', 'reason'} or
            judgment['status'] != 'pass' or not isinstance(judgment['reason'], str) or not judgment['reason'].strip()):
        raise e.EvidenceError('missing or rejected evaluator scope relevance assessment')
    e._write_new(directory / 'scope.json', {'scope': judgment, 'provider_sha256': e.file_digest(directory / 'provider.stdout'),
                                         'changes_sha256': e.file_digest(directory / 'changes.json')})


def verify_scope(directory):
    value = read(directory / 'scope.json')
    raw = read(directory / 'provider.stdout')
    changes = read(directory / 'changes.json')
    if changes.get('run_id') != directory.name:
        raise e.EvidenceError('scope diff run identity mismatch')
    if (value != {'scope': raw.get('scope'), 'provider_sha256': e.file_digest(directory / 'provider.stdout'),
                 'changes_sha256': e.file_digest(directory / 'changes.json')} or
            value['scope']['status'] != 'pass' or not value['scope']['reason'].strip()):
        raise e.EvidenceError('invalid scope relevance evidence')


def receipt_binding(directory):
    """Receipt-hashed enrollment survives missing sidecars without legacy fallback."""
    verify_scope(directory)
    boundary = read(directory / 'boundary.json')
    enrollment = read(directory / 'boundary-required.json')
    if boundary['run_id'] != directory.name or enrollment['run_id'] != directory.name:
        raise e.EvidenceError('boundary enrollment mismatch')
    return {'version': 1, **{name.replace('.', '_').replace('-', '_'): e.file_digest(directory / name)
            for name in ('boundary-required.json', 'boundary.json', 'changes.json', 'scope.json')}}
