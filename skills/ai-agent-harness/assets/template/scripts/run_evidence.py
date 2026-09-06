"""Run-scoped evidence primitives; orchestration enrollment is a separate layer.

Only the coordinating runner calls create_run/execute/evaluate/build_receipt.
Agent JSON is accepted solely as the criterion assessment captured by evaluate.
See docs/run-evidence.md for exclusions and the same-account trust boundary.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import uuid


class EvidenceError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate(value, rule, defs, where='$'):
    if '$ref' in rule:
        return _validate(value, defs[rule['$ref'].split('/')[-1]], defs, where)
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
    if 'type' in rule and type(value) is not types[rule['type']]:
        raise EvidenceError(f'{where}: expected {rule["type"]}')
    if 'const' in rule and (type(value) is not type(rule['const']) or value != rule['const']):
        raise EvidenceError(f'{where}: invalid constant')
    if 'enum' in rule and value not in rule['enum']:
        raise EvidenceError(f'{where}: invalid enum')
    if isinstance(value, dict):
        props = rule['properties']
        if not set(rule.get('required', props)).issubset(value) or set(value) - set(props):
            raise EvidenceError(f'{where}: missing or unknown fields')
        for key, child in value.items():
            _validate(child, props[key], defs, f'{where}.{key}')
    elif isinstance(value, list):
        if len(value) < rule.get('minItems', 0):
            raise EvidenceError(f'{where}: empty list')
        for i, child in enumerate(value):
            _validate(child, rule['items'], defs, f'{where}[{i}]')
    elif isinstance(value, str):
        if len(value) < rule.get('minLength', 0) or ('pattern' in rule and not re.fullmatch(rule['pattern'], value)):
            raise EvidenceError(f'{where}: invalid string')
    elif type(value) is int:
        if value < rule.get('minimum', value) or value > rule.get('maximum', value):
            raise EvidenceError(f'{where}: integer outside range')


def validate_schema(value, name):
    schema = json.loads((Path(__file__).resolve().parent.parent / 'schemas' / f'{name}.schema.json').read_text())
    _validate(value, {'$ref': schema['$ref']}, schema['$defs'])


def decode_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise EvidenceError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda s: (_ for _ in ()).throw(EvidenceError(s)))
    except (ValueError, UnicodeError) as exc:
        raise EvidenceError(f'invalid JSON: {exc}') from exc


def _relative(path):
    if not isinstance(path, str) or not path or path.startswith('/') or '\x00' in path or any(p in ('', '.', '..') for p in path.split('/')):
        raise EvidenceError(f'unsafe relative path: {path!r}')
    return path


def _safe(root, relative):
    path = root
    parts = _relative(relative).split('/')
    for part in parts[:-1]:
        path = path / part
        if path.is_symlink():
            raise EvidenceError(f'symlink ancestor: {relative!r}')
    return path / parts[-1]


def _git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise EvidenceError(f'git failed: {os.fsdecode(result.stderr)}')
    return result.stdout


def _excluded(path, layout):
    prefix = '' if layout == 'visible' else '.agent-harness/'
    # Canonical mutable harness metadata only, including index versions.
    if path in {prefix + p for p in ('feature_list.json', 'progress.md', 'manifest.json')}:
        return True
    if path.startswith(prefix + 'runs/') and path != prefix + 'runs/RUN_TEMPLATE.md':
        return True
    # Only ignored *untracked* Python cache files are excluded below by snapshot.
    return False


def snapshot(workspace, layout='visible'):
    if layout not in ('visible', 'hidden'):
        raise EvidenceError('invalid layout')
    root = Path(workspace).resolve()
    if Path(os.fsdecode(_git(root, 'rev-parse', '--show-toplevel')).rstrip('\n')).resolve() != root:
        raise EvidenceError('workspace must be the Git root')
    index = {}
    for record in _git(root, 'ls-files', '--stage', '-z').split(b'\x00'):
        if not record:
            continue
        meta, raw_path = record.split(b'\t', 1)
        mode, oid, stage = meta.decode('ascii').split()
        path = os.fsdecode(raw_path)
        if mode == '160000':
            raise EvidenceError(f'submodules require explicit snapshot support: {path}')
        index.setdefault(path, []).append({'mode': mode, 'oid': oid, 'stage': int(stage)})
    others = {os.fsdecode(p) for p in _git(root, 'ls-files', '--others', '-z').split(b'\x00') if p}
    ignored = {os.fsdecode(p) for p in _git(root, 'ls-files', '--others', '--ignored', '--exclude-standard', '-z').split(b'\x00') if p}
    # Git omits untracked FIFOs and can summarize nested repositories. Inspect
    # filesystem entries as well so unsupported types never disappear silently.
    def walk_error(error):
        raise EvidenceError(f'cannot enumerate source: {error}')
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        for name in list(dirs):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if relative == '.git':
                dirs.remove(name)
            elif name == '.git':
                raise EvidenceError(f'nested Git repository requires explicit support: {relative}')
            elif _excluded(relative + '/child', layout):
                dirs.remove(name)
                template = path / 'RUN_TEMPLATE.md'
                if template.exists() or template.is_symlink():
                    others.add(template.relative_to(root).as_posix())
            elif path.is_symlink():
                dirs.remove(name)
                others.add(relative)
        for name in files:
            relative = (base / name).relative_to(root).as_posix()
            if relative != '.git':
                others.add(relative)
    entries = []
    for relative in sorted(set(index) | others):
        if _excluded(relative, layout):
            continue
        if relative not in index and relative in ignored and ('__pycache__' in relative.split('/') or relative.endswith(('.pyc', '.pyo'))):
            continue
        path = _safe(root, relative)
        try:
            info = path.lstat()
        except FileNotFoundError:
            kind, mode, content = 'deleted', 0, b''
        else:
            mode = stat.S_IMODE(info.st_mode)
            if stat.S_ISLNK(info.st_mode):
                kind, content = 'symlink', os.fsencode(os.readlink(path))
            elif stat.S_ISREG(info.st_mode):
                kind = 'file'
                # O_NOFOLLOW prevents following a last-component symlink swap.
                fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
                with os.fdopen(fd, 'rb') as stream:
                    content = stream.read()
            else:
                raise EvidenceError(f'unsupported source file type: {relative!r}')
        entries.append({'path': relative, 'kind': kind, 'mode': mode, 'sha256': hashlib.sha256(content).hexdigest(), 'index': index.get(relative, [])})
    result = {'policy': 'git-source-v1', 'layout': layout, 'entries': entries}
    result['sha256'] = digest(result)
    return result


def _snapshot_valid(value):
    expected = digest({k: v for k, v in value.items() if k != 'sha256'})
    if value['sha256'] != expected:
        raise EvidenceError('snapshot checksum mismatch')
    paths = [entry['path'] for entry in value['entries']]
    if paths != sorted(set(paths)):
        raise EvidenceError('snapshot paths must be unique and sorted')
    for entry in value['entries']:
        _relative(entry['path'])
        stages = [v['stage'] for v in entry['index']]
        if stages != sorted(set(stages)):
            raise EvidenceError('duplicate or unordered index stages')


def validate_run(run):
    validate_schema(run, 'run')
    if run['feature_id'] != run['contract']['id'] or digest(run['contract']) != run['criteria_sha256']:
        raise EvidenceError('contract identity mismatch')
    _snapshot_valid(run['snapshot'])
    for command in run['required_commands']:
        _command_valid(command)
    if run['required_commands'][0]['argv'] != ['./init.sh']:
        raise EvidenceError('project recovery command must be first')


def binding(run):
    return {k: run[k] for k in ('run_id', 'feature_id', 'attempt', 'criteria_sha256')} | {'snapshot_sha256': run['snapshot']['sha256']}


def assert_unchanged(run, workspace, feature=None):
    validate_run(run)
    if feature is not None:
        contract = {k: feature[k] for k in ('id', 'title', 'description', 'acceptance')}
        if digest(contract) != run['criteria_sha256']:
            raise EvidenceError('criteria changed')
    if snapshot(workspace, run['snapshot']['layout']) != run['snapshot']:
        raise EvidenceError('source snapshot changed')


def _run_dir(workspace, run):
    prefix = '' if run['snapshot']['layout'] == 'visible' else '.agent-harness/'
    path = _safe(Path(workspace).resolve(), prefix + 'runs/' + run['run_id'])
    if path.is_symlink():
        raise EvidenceError('symlink run directory')
    return path


def _write_new(path, value):
    with path.open('x', encoding='ascii') as stream:
        stream.write(canonical(value).decode('ascii') + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def create_run(workspace, feature, attempt, layout='visible', additional_commands=(), recovery_timeout=600):
    contract = {k: feature[k] for k in ('id', 'title', 'description', 'acceptance')}
    # Copy all mutable input so later agent/state edits cannot change this contract.
    run = decode_json(canonical({'schema_version': 1, 'run_id': uuid.uuid4().hex, 'feature_id': feature['id'], 'attempt': attempt,
           'contract': contract, 'criteria_sha256': digest(contract), 'snapshot': snapshot(workspace, layout),
           'required_commands': [{'argv': ['./init.sh'], 'timeout_seconds': recovery_timeout}, *additional_commands]}))
    validate_run(run)
    directory = _run_dir(workspace, run)
    directory.mkdir(parents=True, exist_ok=False)
    _write_new(directory / 'run.json', run)
    return run


def _command_valid(command):
    if any('\x00' in arg or not arg for arg in command['argv']):
        raise EvidenceError('invalid argv')


def _bound(value, run):
    if value['binding'] != binding(run):
        raise EvidenceError('cross-run or stale evidence')


def execute(workspace, run, command, label, index):
    """Runner-only process capture; never import outcomes supplied by a role."""
    validate_run(run)
    if label not in ('check', 'evaluator') or type(index) is not int or index < 0:
        raise EvidenceError('invalid command log identity')
    schema = json.loads((Path(__file__).resolve().parent.parent / 'schemas/run.schema.json').read_text())
    _validate(command, {'$ref': '#/$defs/command'}, schema['$defs'])
    _command_valid(command)
    assert_unchanged(run, workspace)
    directory = _run_dir(workspace, run)
    if (directory / 'run.json').is_symlink():
        raise EvidenceError('symlink run manifest')
    if decode_json((directory / 'run.json').read_bytes()) != run:
        raise EvidenceError('persisted run mismatch')
    out = directory / f'{label}-{index}.stdout'
    err = directory / f'{label}-{index}.stderr'
    timed_out, launch_error = False, ''
    with out.open('xb') as stdout, err.open('xb') as stderr:
        try:
            result = subprocess.run(command['argv'], cwd=Path(workspace).resolve(), stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, timeout=command['timeout_seconds'], shell=False)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code, timed_out = -1, True
        except OSError as exc:
            code, launch_error = -1, str(exc)
        for stream in (stdout, stderr):
            stream.flush()
            os.fsync(stream.fileno())
    outcome = {'binding': binding(run), 'source': 'runner-subprocess-v1', 'command': command,
               'exit_code': code, 'timed_out': timed_out, 'launch_error': launch_error,
               'stdout': {'path': out.name, 'sha256': file_digest(out)}, 'stderr': {'path': err.name, 'sha256': file_digest(err)}}
    _write_new(directory / f'{label}-{index}.json', outcome)
    return outcome


def execute_required(workspace, run):
    return [execute(workspace, run, command, 'check', i) for i, command in enumerate(run['required_commands'])]


def validate_evaluation(evaluation, run, require_pass=True):
    validate_run(run)
    validate_schema(evaluation, 'evaluation')
    _bound(evaluation, run)
    rows = evaluation['criteria']
    if sorted(row['index'] for row in rows) != list(range(len(run['contract']['acceptance']))):
        raise EvidenceError('incomplete or duplicate evaluator criteria')
    if any(not row['reason'].strip() or any(not e.strip() for e in row['evidence']) for row in rows):
        raise EvidenceError('empty evaluator evidence')
    if require_pass and any(row['status'] != 'pass' for row in rows):
        raise EvidenceError('evaluator rejected a criterion')


def evaluate(workspace, run, command):
    """Invoke independent evaluator; stdout must be exactly evaluation schema JSON.

    The caller supplies a configured role adapter argv. The adapter can read run.json;
    this primitive does not infer a provider or parse provider-specific output.
    """
    outcome = execute(workspace, run, command, 'evaluator', 0)
    _successful(outcome)
    evaluation = decode_json((_run_dir(workspace, run) / outcome['stdout']['path']).read_bytes())
    validate_evaluation(evaluation, run)
    assert_unchanged(run, workspace)
    return outcome, evaluation


def _successful(outcome):
    if outcome['exit_code'] != 0 or outcome['timed_out'] or outcome['launch_error']:
        raise EvidenceError('runner command did not succeed')


def validate_receipt(receipt, workspace, expected_run=None, current=False, feature=None):
    """Historical integrity by default; current=True additionally checks live source."""
    validate_schema(receipt, 'receipt')
    run = receipt['run']
    validate_run(run)
    if expected_run is not None and run != expected_run:
        raise EvidenceError('receipt belongs to another run')
    if receipt['sha256'] != digest({k: v for k, v in receipt.items() if k != 'sha256'}):
        raise EvidenceError('receipt checksum mismatch')
    directory = _run_dir(workspace, run)
    def read_artifact(name):
        path = _safe(directory, name)
        if path.is_symlink() or not path.is_file():
            raise EvidenceError('missing or symlink evidence artifact')
        return path.read_bytes()
    if decode_json(read_artifact('run.json')) != run:
        raise EvidenceError('persisted run mismatch')
    if [c['command'] for c in receipt['checks']] != run['required_commands']:
        raise EvidenceError('required command coverage mismatch')
    outcomes = [('check', i, c) for i, c in enumerate(receipt['checks'])] + [('evaluator', 0, receipt['evaluator_command'])]
    for label, i, outcome in outcomes:
        _bound(outcome, run)
        _successful(outcome)
        if decode_json(read_artifact(f'{label}-{i}.json')) != outcome:
            raise EvidenceError('runner outcome mismatch')
        for channel in ('stdout', 'stderr'):
            log = outcome[channel]
            if log['path'] != f'{label}-{i}.{channel}' or hashlib.sha256(read_artifact(log['path'])).hexdigest() != log['sha256']:
                raise EvidenceError('runner log mismatch')
    captured = decode_json(read_artifact(receipt['evaluator_command']['stdout']['path']))
    if captured != receipt['evaluation']:
        raise EvidenceError('evaluation differs from captured child output')
    validate_evaluation(receipt['evaluation'], run)
    if 'role_boundary' in receipt or (directory / 'boundary-required.json').exists() or (directory / 'boundary.json').exists():
        import role_boundary
        if receipt.get('role_boundary') != role_boundary.receipt_binding(directory):
            raise EvidenceError('missing or changed role boundary receipt binding')
    if current:
        assert_unchanged(run, workspace, feature)


def build_receipt(workspace, run, checks, evaluator_command, evaluation, feature):
    receipt = decode_json(canonical({'schema_version': 1, 'run': run, 'checks': checks,
               'evaluator_command': evaluator_command, 'evaluation': evaluation}))
    directory = _run_dir(workspace, run)
    if (directory / 'boundary-required.json').exists() or (directory / 'boundary.json').exists():
        import role_boundary
        receipt['role_boundary'] = role_boundary.receipt_binding(directory)
    receipt['sha256'] = digest(receipt)
    validate_receipt(receipt, workspace, expected_run=run, current=True, feature=feature)
    _write_new(_run_dir(workspace, run) / 'receipt.json', receipt)
    return receipt
