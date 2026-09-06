"""Explicit real-provider smoke; not invoked by init or dependency-free CI tests."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import completion

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    # The selected provider and argv are explicit; only its workspace is moved to
    # the isolated fixture. Never mutate user's actual provider configuration.
    config = json.loads(args.config.read_text())
    provider = config['provider']
    config['providers'][provider]['cwd'] = '.'
    with tempfile.TemporaryDirectory(prefix='harness-provider-smoke-') as tmp:
        project = Path(tmp)
        for name in ('scripts', 'schemas', 'prompts'):
            shutil.copytree(ROOT / name, project / name)
        shutil.copy2(ROOT / 'orchestrator.py', project)
        (project / 'agent-provider.json').write_text(json.dumps(config))
        (project / 'AGENTS.md').write_text('Read progress.md and feature_list.json; run ./init.sh. Do not edit files during evaluation. Return only the requested assessment JSON.\n')
        (project / 'progress.md').write_text('Current System Status: provider smoke fixture. Next Feature: F001. Known Issues: none.\n')
        feature = {'id': 'F001', 'title': 'Smoke recovery', 'description': 'Verify the existing fixture marker through init.sh.', 'acceptance': ['Project-root ./init.sh exits zero and prints FIXTURE_OK by verifying marker.txt equals ready.'], 'passes': False, 'status': 'todo', 'attempts': 0, 'last_error': ''}
        (project / 'feature_list.json').write_text(json.dumps({'features': [feature]}))
        completion.freeze_policy(project, {'features': []})
        (project / 'marker.txt').write_text('ready\n')
        init = project / 'init.sh'
        init.write_text('#!/bin/sh\nset -eu\ntest "$(cat marker.txt)" = ready\necho FIXTURE_OK\n')
        init.chmod(0o755)
        def run(argv, label):
            result = subprocess.run(argv, cwd=project, text=True, capture_output=True)
            (output / (label + '.stdout')).write_text(result.stdout)
            (output / (label + '.stderr')).write_text(result.stderr)
            if result.returncode:
                raise RuntimeError(f'{label} exited {result.returncode}; see {output}')
        try:
            run(['git', 'init', '-q'], 'git-init')
            run(['git', '-c', 'user.name=Smoke', '-c', 'user.email=smoke@example.test', 'commit', '--allow-empty', '-qm', 'fixture'], 'git-commit')
            run([sys.executable, 'orchestrator.py', '--work-fast'], 'handoff')
            feature = json.loads((project / 'feature_list.json').read_text())['features'][0]
            note = project / 'runs/coding.md'
            note.write_text('FAST_CODING_EVIDENCE: F001\nCODING_PASS: F001\n')
            run([sys.executable, 'orchestrator.py', '--record-coding', 'F001', '--run-id', feature['active_run'], '--evidence-file', str(note)], 'coding')
            run([sys.executable, 'orchestrator.py', '--work-fast'], 'evaluation')
            completion.verify_history(project, json.loads((project / 'feature_list.json').read_text()))
            print(f'Real configured provider receipt verified; artifacts: {output}')
        finally:
            if (project / 'runs').exists():
                shutil.copytree(project / 'runs', output / 'runs')
            shutil.copy2(project / 'feature_list.json', output)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
