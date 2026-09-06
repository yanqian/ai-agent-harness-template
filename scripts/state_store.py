"""Shared lifecycle validation and POSIX single-writer state transactions.

Readers never lock. Ownership spans a command/round; replacement locks are short.
Lock files are permanent inodes in runs/, not lock-existence sentinels.
"""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import sys
import tempfile


class StateError(ValueError):
    pass


@contextmanager
def lock(path, name='state'):
    path = Path(path).resolve()
    directory = path.parent / 'runs'
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ('.' + path.name + '.' + name + '.lock')).open('a+b') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise StateError(f'{name} lock contention for {path}; retry after the current writer exits') from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def ownership(path):
    return lock(path, 'owner')


def validate(data, harness=None):
    if not isinstance(data, dict) or not isinstance(data.get('features'), list):
        raise StateError('feature_list.json must contain a features array')
    by_id = {}
    for f in data['features']:
        if not isinstance(f, dict) or not isinstance(f.get('id'), str) or f['id'] in by_id:
            raise StateError('invalid or duplicate feature ID')
        by_id[f['id']] = f
    for fid, f in by_id.items():
        deps = f.get('depends_on', [])
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
            raise StateError(f'{fid}: depends_on must be an array of feature IDs')
        if len(set(deps)) != len(deps) or fid in deps or any(d not in by_id for d in deps):
            raise StateError(f'{fid}: duplicate, self or missing dependency')
    visited, visiting = set(), set()
    def visit(fid):
        if fid in visiting:
            raise StateError(f'dependency cycle at {fid}')
        if fid in visited:
            return
        visiting.add(fid)
        for dep in by_id[fid].get('depends_on', []):
            visit(dep)
        visiting.remove(fid)
        visited.add(fid)
    for fid in by_id:
        visit(fid)
    for fid, f in by_id.items():
        if type(f.get('passes')) is not bool or f.get('status') not in {'todo', 'in_progress', 'done', 'blocked'} or (f['status'] == 'done') != f['passes']:
            raise StateError(f'{fid}: contradictory passes/status')
        if type(f.get('attempts')) is not int or f['attempts'] < 0:
            raise StateError(f'{fid}: attempts must be a non-negative integer')
        if 'completion_history' in f and not isinstance(f['completion_history'], list):
            raise StateError(f'{fid}: completion_history must be an array')
        human = f.get('human_acceptance', {})
        if not isinstance(human, dict) or ('reopen_pending' in human and type(human['reopen_pending']) is not bool):
            raise StateError(f'{fid}: invalid human acceptance')
        contradiction = f['passes'] and (human.get('reopen_pending') or human.get('status') == 'rejected')
        if contradiction:
            import completion
            old = completion.read_policy(Path(harness))['legacy'].get(fid) if harness and (Path(harness) / completion.POLICY).exists() else None
            if old == completion.legacy_identity(f) and not f.get('active_run') and not f.get('completion_receipt'):
                print(f'legacy metadata contradiction: {fid}; frozen history only', file=sys.stderr)
            else:
                raise StateError(f'{fid}: done with rejected/reopen metadata')
        if human.get('reopen_pending') and not f['passes'] and (f['status'] != 'todo' or f.get('active_run') or f.get('completion_receipt')):
            raise StateError(f'{fid}: pending reopen must be todo without active completion evidence')


def ready(data, feature):
    by_id = {f['id']: f for f in data['features']}
    return all(by_id[d].get('passes') is True and by_id[d].get('status') == 'done'
               and not by_id[d].get('human_acceptance', {}).get('reopen_pending')
               and by_id[d].get('human_acceptance', {}).get('status') != 'rejected'
               for d in feature.get('depends_on', []))


class State(dict):
    """JSON-compatible mapping with an out-of-band compare-and-swap token."""
    pass


def load(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    data = State(json.loads(raw))
    validate(data, path.parent)
    data.original = raw
    data.path = path
    return data


def save(path, data):
    path = Path(path).resolve()
    if not isinstance(data, State) or data.path != path:
        raise StateError('state write requires a loaded revision')
    with lock(path):
        if path.read_bytes() != data.original:
            raise StateError('stale-state write rejected; reload before retry')
        validate(data, path.parent)
        raw = (json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode()
        fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as handle:
                os.fchmod(handle.fileno(), path.stat().st_mode & 0o777)
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            directory = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
            data.original = raw
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def invalidate_completion(feature, reason):
    evidence = {k: feature.pop(k) for k in ('active_run', 'completion_receipt') if k in feature}
    if evidence:
        feature.setdefault('completion_history', []).append(dict(evidence, reason=reason, attempt=feature['attempts']))
