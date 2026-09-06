"""Run the configured independent evaluator adapter with the frozen receipt prompt.

Raw provider stdout/stderr are retained. stdout must be our evaluation JSON schema;
no values are recovered from prose, file paths, log tails or provider event guesses.
"""
from pathlib import Path
import subprocess
import sys

import completion
import role_boundary as b
import run_evidence as e


def main():
    harness = Path(sys.argv[1]).resolve()
    directory = completion.directory(harness, sys.argv[2])
    prompt = (directory / 'evaluator-prompt.txt').read_text()
    with (directory / 'provider.stdout').open('xb') as out, (directory / 'provider.stderr').open('xb') as err:
        result = subprocess.run([str(harness / 'scripts/run-evaluator-agent.sh')], cwd=harness,
                                input=prompt.encode(), stdout=out, stderr=err, shell=False)
    if result.returncode:
        print(f'evaluator adapter exit {result.returncode}; see {directory}/provider.stderr', file=sys.stderr)
        return 1
    assessment = e.decode_json((directory / 'provider.stdout').read_bytes())
    if (directory / 'boundary-required.json').exists() or (directory / 'boundary.json').exists():
        b.read(directory / 'boundary.json')
        b.scope(assessment, directory)
    e.validate_evaluation(assessment, completion.read(directory / 'run.json'))
    print(e.canonical(assessment).decode('ascii'))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (e.EvidenceError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
