#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
import completion
import state_store
import run_evidence
import role_boundary

FEATURES_PATH = Path("feature_list.json")
PROGRESS_PATH = Path("progress.md")
PROMPTS_DIR = Path("prompts")
RUNS_DIR = Path("runs")
CODING_AGENT_ADAPTER = Path("scripts/run-coding-agent.sh")
EVALUATOR_AGENT_ADAPTER = Path("scripts/run-evaluator-agent.sh")
INSTALL_MANIFEST_PATH = Path("manifest.json")
MAX_ROUNDS = 1
MAX_ATTEMPTS = 3
BOUNDARY_ADOPT = []
BOUNDARY_ALLOWED = None
FAST_CODING_HANDOFF_PREFIX = "FAST_CODING_HANDOFF:"


class OrchestratorError(Exception):
    pass


def sh(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, text=True, check=check)


def run_capture(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def load_state() -> dict:
    return state_store.load(FEATURES_PATH)


def save_state(data: dict) -> None:
    state_store.save(FEATURES_PATH, data)


def features(data: dict) -> list[dict]:
    return data["features"]


def feature_by_id(data: dict, feature_id: str) -> dict:
    for feature in features(data):
        if feature.get("id") == feature_id:
            return feature
    raise OrchestratorError(f"Feature not found: {feature_id}")


def normalize_status(feature: dict) -> str:
    status = feature.get("status", "todo")
    if feature.get("passes") is True:
        return "done"
    if status == "done":
        return "todo"
    return status


def pick_feature(data: dict, max_attempts: int) -> Optional[dict]:
    state_store.validate(data, FEATURES_PATH.resolve().parent)
    priority = {"P0": 0, "P1": 1, "P2": 2}
    candidates = []
    ordered_features = features(data)
    for feature in ordered_features:
        attempts = int(feature.get("attempts", 0))
        status = normalize_status(feature)
        acceptance = feature.get("human_acceptance", {})
        reopened = isinstance(acceptance, dict) and acceptance.get("reopen_pending") is True
        if state_store.ready(data, feature) and feature.get("passes") is False and status in {"todo", "in_progress"} and (attempts < max_attempts or reopened):
            candidates.append(feature)
    candidates.sort(key=lambda item: (priority.get(item.get("priority", "P2"), 9), ordered_features.index(item)))
    return candidates[0] if candidates else None


def pick_fast_feature(data: dict, max_attempts: int) -> Optional[dict]:
    state_store.validate(data, FEATURES_PATH.resolve().parent)
    priority = {"P0": 0, "P1": 1, "P2": 2}
    ordered_features = features(data)
    in_progress = [
        feature
        for feature in ordered_features
        if state_store.ready(data, feature) and feature.get("passes") is False and normalize_status(feature) == "in_progress"
    ]
    if in_progress:
        in_progress.sort(key=lambda item: (priority.get(item.get("priority", "P2"), 9), ordered_features.index(item)))
        return in_progress[0]
    return pick_feature(data, max_attempts)


def mark_in_progress(feature_id: str) -> None:
    data = load_state()
    feature = feature_by_id(data, feature_id)
    if not state_store.ready(data, feature):
        raise state_store.StateError("feature dependencies are not ready")
    state_store.invalidate_completion(feature, "new attempt")
    feature["status"] = "in_progress"
    feature["attempts"] = int(feature.get("attempts", 0)) + 1
    feature["last_error"] = ""
    acceptance = feature.get("human_acceptance")
    if isinstance(acceptance, dict):
        acceptance["reopen_pending"] = False
        if acceptance.get("status") == "rejected":
            acceptance["status"] = "unreviewed"
    save_state(data)


def mark_done(feature_id: str, receipt_path: Path) -> None:
    data = load_state()
    feature = feature_by_id(data, feature_id)
    if not state_store.ready(data, feature):
        raise state_store.StateError("feature dependencies are not ready")
    harness = Path.cwd()
    _, run = completion.candidate(harness, feature)
    receipt = completion.read(receipt_path)
    run_evidence.validate_receipt(receipt, completion.paths(harness)[0], expected_run=run,
                                  current=True, feature=feature)
    feature["completion_receipt"] = receipt_path.relative_to(harness).as_posix()
    feature["passes"] = True
    feature["status"] = "done"
    feature["last_error"] = ""
    save_state(data)


def mark_failed(feature_id: str, error: str, max_attempts: int) -> None:
    data = load_state()
    feature = feature_by_id(data, feature_id)
    attempts = int(feature.get("attempts", 0))
    feature["passes"] = False
    feature["status"] = "blocked" if attempts >= max_attempts else "todo"
    feature["last_error"] = error.strip()[:2000]
    save_state(data)


def write_failure_run_record(
    feature_id: str,
    failure_summary: str,
    *,
    command: str = "python3 orchestrator.py",
    failure_domain: str = "agent_workflow_gap",
    harness_improvement: str = "No new harness improvement required; the orchestrator recorded this failure and kept the feature non-done.",
) -> None:
    RUNS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_feature = re.sub(r"[^A-Za-z0-9_-]+", "-", feature_id)
    path = RUNS_DIR / f"{timestamp}-{safe_feature}-failure.md"
    current_commit = run_capture(["git", "rev-parse", "--short", "HEAD"], check=False).stdout.strip() or "unknown"
    status = run_capture(["git", "status", "--short"], check=False).stdout.strip() or "clean"
    path.write_text(
        f"# Run Record: {feature_id} - orchestrator failure\n\n"
        "## Summary\n\n"
        f"- Date: {timestamp}\n"
        "- Agent role: Orchestrator\n"
        f"- Feature: {feature_id}\n"
        "- Result: fail\n\n"
        "## Repository State\n\n"
        f"- Starting commit: {current_commit}\n"
        f"- Ending commit: {current_commit}\n"
        f"- Working tree status: {status}\n\n"
        "## Commands Run\n\n"
        "```bash\n"
        f"{command}\n"
        "```\n\n"
        "## Evidence\n\n"
        "- Tests:\n"
        f"- Logs: {failure_summary.strip()[:1000]}\n"
        "- Screenshots or traces:\n"
        "- External behavior verification:\n\n"
        "## Failure Analysis\n\n"
        f"- Failure domain: {failure_domain}\n"
        f"- Failure summary: {failure_summary.strip()[:1000]}\n"
        f"- Harness improvement: {harness_improvement}\n"
        "- Follow-up feature:\n\n"
        "## Files Changed\n\n"
        "- `feature_list.json`\n\n"
        "## Evaluator Result\n\n"
        "```text\n"
        f"EVAL_FAIL: {feature_id}: {failure_summary.strip()[:1000]}\n"
        "```\n\n"
        "## Follow-Up\n\n"
        "- Classify the failure domain and assess harness improvement before the next retry.\n"
    )
    print(f"Wrote failure run record: {path}", flush=True)


def startup_protocol() -> None:
    if not PROGRESS_PATH.exists():
        raise OrchestratorError("progress.md is missing.")
    if not FEATURES_PATH.exists():
        raise OrchestratorError("feature_list.json is missing.")
    print("Reading progress.md and feature_list.json.", flush=True)
    PROGRESS_PATH.read_text()
    load_state()
    sh(["git", "log", "--oneline", "-20"])
    sh(["./init.sh"])


def harness_layout() -> str:
    if INSTALL_MANIFEST_PATH.exists():
        try:
            manifest = json.loads(INSTALL_MANIFEST_PATH.read_text())
        except json.JSONDecodeError:
            manifest = {}
        if manifest.get("layout") in {"hidden", "visible"}:
            return str(manifest["layout"])
    if Path.cwd().name == ".agent-harness":
        return "hidden"
    return "visible"


def provider_workspace_path_contract(layout: Optional[str] = None) -> str:
    selected_layout = layout or harness_layout()
    if selected_layout not in {"hidden", "visible"}:
        raise OrchestratorError(f"Unsupported harness layout: {selected_layout}")
    prefix = ".agent-harness/" if selected_layout == "hidden" else ""
    mappings = [
        ("SPEC.md", f"{prefix}SPEC.md"),
        ("feature_list.json", f"{prefix}feature_list.json"),
        ("progress.md", f"{prefix}progress.md"),
        ("QUALITY.md", f"{prefix}QUALITY.md"),
        ("test_plan.md", f"{prefix}test_plan.md"),
        ("runs/", f"{prefix}runs/"),
        ("docs/", f"{prefix}docs/"),
        ("prompts/", f"{prefix}prompts/"),
        ("scripts/", f"{prefix}scripts/"),
        ("test/", f"{prefix}test/"),
    ]
    lines = [
        "# Provider Workspace Path Contract",
        "",
        f"Harness layout: `{selected_layout}`.",
        "All paths below are relative to the provider workspace selected by `agent-provider.json` `cwd`.",
    ]
    if selected_layout == "hidden":
        lines.extend([
            "The provider workspace is the project root; provider `cwd` is normally `..` relative to `.agent-harness/`.",
            "Root files with the same names as harness state are legacy/non-canonical and must not be read or modified.",
        ])
    else:
        lines.append("The provider workspace and harness root are the repository root; provider `cwd` is normally `.`.")
    lines.extend(["", "Canonical harness paths:"])
    lines.extend(f"- `{logical}` -> `{canonical}`" for logical, canonical in mappings)
    lines.extend([
        "",
        "Project-owned source, root `AGENTS.md`, and root `./init.sh` remain relative to the provider workspace.",
        "Treat later bare harness paths in this role prompt as logical names resolved through this mapping.",
    ])
    return "\n".join(lines)


def prompt_template(name: str, layout: Optional[str] = None) -> str:
    path = PROMPTS_DIR / name
    if not path.exists():
        raise OrchestratorError(f"Missing prompt template: {path}")
    return f"{provider_workspace_path_contract(layout)}\n\n{path.read_text()}"


def coding_prompt(feature_id: str) -> str:
    return f"{prompt_template('work.md')}\n\nSelected feature ID: `{feature_id}`\n"


def fast_coding_prompt(feature_id: str) -> str:
    return f"{prompt_template('work-fast.md')}\n\nSelected feature ID: `{feature_id}`\n"


def evaluator_prompt(feature_id: str) -> str:
    return f"{prompt_template('evaluate.md')}\n\nSelected feature ID: `{feature_id}`\n"


def ensure_adapter_configured(label: str, adapter_path: Path) -> None:
    if not adapter_path.exists():
        raise OrchestratorError(
            f"{label} adapter is missing: {adapter_path}. "
            "Configure the role adapter before running orchestrator work, or explicitly use the documented manual fallback."
        )
    if not adapter_path.is_file():
        raise OrchestratorError(f"{label} adapter is not a file: {adapter_path}")
    if (adapter_path.stat().st_mode & 0o111) == 0:
        raise OrchestratorError(
            f"{label} adapter is not executable: {adapter_path}. "
            "Run chmod +x after configuring the adapter."
        )
    marker = "is a template adapter."
    try:
        adapter_text = adapter_path.read_text()
    except UnicodeDecodeError:
        adapter_text = ""
    if marker in adapter_text:
        raise OrchestratorError(
            f"{label} adapter is still the template adapter: {adapter_path}. "
            "The default work entrypoint is orchestrator-first, but real work requires configured Coding Agent "
            "and Evaluator Agent adapters. Configure an agent provider, or explicitly use the manual fallback "
            "without bypassing evaluator pass evidence or final ./init.sh verification."
        )
    if "run-agent-provider.py" in adapter_text:
        env = os.environ.copy()
        env["HARNESS_AGENT_PROVIDER_CHECK"] = "1"
        result = subprocess.run([str(adapter_path)], text=True, capture_output=True, env=env)
        if result.returncode != 0:
            detail = "\n".join(part.strip() for part in [result.stdout, result.stderr] if part.strip())
            raise OrchestratorError(
                f"{label} provider is not configured for orchestrator-first work. "
                f"{detail or f'{adapter_path} exited with code {result.returncode}'}"
            )


def run_agent(prompt: str, dry_run: bool, label: str, adapter_path: Path) -> subprocess.CompletedProcess[str]:
    if dry_run:
        print(f"\n== {label} prompt ==")
        print(prompt)
        return subprocess.CompletedProcess(["dry-run"], 0, stdout="", stderr="")
    ensure_adapter_configured(label, adapter_path)
    result = subprocess.run([str(adapter_path)], input=prompt, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="", flush=True)
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr, flush=True)
    return result


def role_output(result: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(part for part in [result.stdout, result.stderr] if part)


def final_role_verdict(output: str, pass_line: str, fail_prefix: str) -> tuple[Optional[bool], str]:
    verdict: tuple[Optional[bool], str] = (None, "")
    for line in output.splitlines():
        stripped = line.strip()
        if stripped == pass_line:
            verdict = (True, "")
        elif stripped.startswith(fail_prefix):
            verdict = (False, stripped[len(fail_prefix):].strip() or "Role reported failure.")
    return verdict


def evaluator_result(feature_id: str, result: subprocess.CompletedProcess[str]) -> tuple[bool, str]:
    output = role_output(result)
    pass_line = f"EVAL_PASS: {feature_id}"
    fail_prefix = f"EVAL_FAIL: {feature_id}:"
    passed, reason = final_role_verdict(output, pass_line, fail_prefix)
    if passed is not None:
        if passed:
            return True, ""
        return False, reason or "Evaluator reported failure."
    return False, f"Evaluator did not emit required pass line: {pass_line}"


def coding_result(feature_id: str, result: subprocess.CompletedProcess[str]) -> tuple[Optional[bool], str]:
    output = role_output(result)
    pass_line = f"CODING_PASS: {feature_id}"
    fail_prefix = f"CODING_FAIL: {feature_id}:"
    return final_role_verdict(output, pass_line, fail_prefix)


def evaluate_feature(feature_id: str, dry_run: bool) -> bool:
    print(f"\n== Evaluate: {feature_id} ==", flush=True)
    result = run_agent(evaluator_prompt(feature_id), dry_run, "Evaluator Agent", EVALUATOR_AGENT_ADAPTER)
    if dry_run:
        return True
    passed, reason = evaluator_result(feature_id, result)
    if passed:
        if result.returncode != 0:
            print(
                f"Evaluator emitted EVAL_PASS despite provider exit code {result.returncode}; accepting final verdict.",
                flush=True,
            )
        print(f"Evaluator accepted {feature_id}.", flush=True)
        return True
    if result.returncode != 0:
        print(f"EVAL_FAIL: {feature_id}: evaluator exited with code {result.returncode}: {reason}", flush=True)
        return False
    print(f"EVAL_FAIL: {feature_id}: {reason}", flush=True)
    return False


def run_verified_round(round_no: int, max_attempts: int, dry_run: bool, mode: str) -> bool:
    with state_store.ownership(FEATURES_PATH):
        return _run_verified_round(round_no, max_attempts, dry_run, mode)


def _run_verified_round(round_no: int, max_attempts: int, dry_run: bool, mode: str) -> bool:
    data = load_state()
    feature = pick_fast_feature(data, max_attempts) if mode == "work-fast" else pick_feature(data, max_attempts)
    if not feature:
        print("No runnable unfinished feature left.", flush=True)
        return True
    feature_id = feature["id"]
    if dry_run:
        print(fast_coding_prompt(feature_id) if mode == "work-fast" else coding_prompt(feature_id))
        print(evaluator_prompt(feature_id))
        return True
    try:
        ensure_adapter_configured("Evaluator Agent", EVALUATOR_AGENT_ADAPTER)
        if mode == "work":
            ensure_adapter_configured("Coding Agent", CODING_AGENT_ADAPTER)
    except OrchestratorError as exc:
        # Preflight must not increment attempts or mutate lifecycle state.
        write_failure_run_record(feature_id, f"Provider preflight rejected; active run {feature.get('active_run')}: {exc}",
                                 failure_domain="capability_gap")
        print(str(exc), file=sys.stderr)
        return False
    harness = Path.cwd()
    role_boundary.selection(completion.paths(harness)[0], BOUNDARY_ADOPT)
    if BOUNDARY_ALLOWED is not None:
        role_boundary.selection(completion.paths(harness)[0], BOUNDARY_ALLOWED)
    run_id = None
    try:
        completion.read_policy(harness)
        resume = feature.get("status") == "in_progress" and feature.get("active_run") and not feature.get("human_acceptance", {}).get("reopen_pending")
        if resume:
            if BOUNDARY_ADOPT or BOUNDARY_ALLOWED is not None:
                raise run_evidence.EvidenceError('boundary authorization is fixed before coding; use --restart-run')
            role_boundary.check(harness, *completion.paths(harness), feature['active_run'])
            run_id = feature["active_run"]
            directory, _ = completion.active(harness, feature, mode)
        else:
            if feature.get('active_run'):
                old_directory = completion.directory(harness, feature['active_run'])
                if list(old_directory.glob('violation-*.json')):
                    raise run_evidence.EvidenceError('boundary violation requires explicit --restart-run')
            role_boundary.selection(completion.paths(harness)[0], BOUNDARY_ADOPT)
            if BOUNDARY_ALLOWED is not None:
                role_boundary.selection(completion.paths(harness)[0], BOUNDARY_ALLOWED)
            mark_in_progress(feature_id)
            data = load_state()
            feature = feature_by_id(data, feature_id)
            run_id = completion.start(harness, feature, mode)
            feature["active_run"] = run_id
            save_state(data)
            role_boundary.capture(harness, *completion.paths(harness), run_id, BOUNDARY_ADOPT, BOUNDARY_ALLOWED)
            directory = completion.directory(harness, run_id)
            handoff = (fast_coding_prompt(feature_id) if mode == "work-fast" else coding_prompt(feature_id))
            handoff += (f"\nActive run ID: {run_id}\nRun handoff: {directory}/handoff.json\n"
                        "Do not change lifecycle fields or write evaluator approval. "
                        "For work-fast only, after coding record evidence with "
                        f"python3 orchestrator.py --record-coding {feature_id} --run-id {run_id} --evidence-file <run-note-path>.\n")
            (directory / 'coding-prompt.txt').write_text(handoff)
            if mode == "work":
                coding = run_agent(handoff, False, "Coding Agent", CODING_AGENT_ADAPTER)
                (directory / 'coding.stdout').write_text(coding.stdout or '')
                (directory / 'coding.stderr').write_text(coding.stderr or '')
                role_boundary.check(harness, *completion.paths(harness), run_id)
                if coding.returncode != 0:
                    raise run_evidence.EvidenceError(f"coding adapter exited {coding.returncode}")
                current = feature_by_id(load_state(), feature_id)
                completion.record_coding(harness, current, run_id, 'runner-coding-child-v1', coding.stdout or '')
        if mode == "work-fast" and not (directory / 'coding.json').exists():
            print(f"{FAST_CODING_HANDOFF_PREFIX} {feature_id}; run_id={run_id}")
            print((directory / 'coding-prompt.txt').read_text())
            return True
        receipt_path = completion.finalize(harness, feature_by_id(load_state(), feature_id), evaluator_prompt(feature_id))
        mark_done(feature_id, receipt_path)
        print(f"Done: {feature_id}; receipt={receipt_path}", flush=True)
        return True
    except (run_evidence.EvidenceError, OSError, ValueError, KeyError, StopIteration) as exc:
        error = f"run {run_id or 'not-created'}: {exc}"
        if run_id:
            try:
                directory = completion.directory(harness, run_id)
                if directory.exists() and not (directory / 'failure.json').exists():
                    run_evidence._write_new(directory / 'failure.json', {'run_id': run_id, 'reason': str(exc)})
            except (run_evidence.EvidenceError, OSError):
                pass  # Unsafe/missing run paths are diagnosed in the top-level failure record below.
        mark_failed(feature_id, error, max_attempts)
        write_failure_run_record(feature_id, error, command=f"python3 orchestrator.py --{mode}")
        print(error, file=sys.stderr)
        return False


def run_work_fast_round(round_no: int, max_attempts: int, dry_run: bool) -> bool:
    return run_verified_round(round_no, max_attempts, dry_run, "work-fast")


def feature_ids_for_eval(target: str) -> list[str]:
    data = load_state()
    if target == "all":
        return [str(feature["id"]) for feature in features(data)]
    feature_by_id(data, target)
    return [target]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AI agent harness orchestration.")
    parser.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    parser.add_argument("--max-attempts", type=int, default=MAX_ATTEMPTS)
    parser.add_argument("--eval-only", metavar="FEATURE_ID|all")
    parser.add_argument("--adopt-dirty", action="append", default=[], metavar="PATH")
    parser.add_argument("--allow-path", action="append", default=None, metavar="PATH")
    parser.add_argument("--restart-run", metavar="FEATURE_ID")
    parser.add_argument("--record-coding", metavar="FEATURE_ID")
    parser.add_argument("--run-id")
    parser.add_argument("--evidence-file", type=Path)
    parser.add_argument("--work-fast", action="store_true", help="run evaluator-gated fast work mode")
    parser.add_argument(
        "--render-prompt",
        choices=["plan", "work", "evaluate", "continue", "work-fast"],
        help="render one role prompt with the detected provider-workspace path contract",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    global BOUNDARY_ADOPT, BOUNDARY_ALLOWED
    args = parse_args()
    BOUNDARY_ADOPT, BOUNDARY_ALLOWED = args.adopt_dirty, args.allow_path
    if args.restart_run:
        if not args.run_id:
            raise OrchestratorError('--restart-run requires --run-id')
        with state_store.ownership(FEATURES_PATH):
            data = load_state()
            feature = feature_by_id(data, args.restart_run)
            if feature.get('active_run') != args.run_id or feature.get('passes'):
                raise OrchestratorError('restart requires matching incomplete active run; restore unauthorized state edits first')
            directory = completion.directory(Path.cwd(), args.run_id)
            run_evidence._write_new(directory / ('restart-' + __import__('uuid').uuid4().hex + '.json'),
                                    {'run_id': args.run_id, 'action': 'explicit restart; working tree preserved'})
            state_store.invalidate_completion(feature, 'explicit boundary recovery')
            feature['status'] = 'todo'
            feature['last_error'] = ''
            save_state(data)
        print('Run archived; inspect preserved edits and start a new round with any required --adopt-dirty/--allow-path declarations.')
        return 0
    # Check roles before startup can fail on their state edits or selection can skip early done.
    with state_store.ownership(FEATURES_PATH):
        for marker in sorted(RUNS_DIR.glob('*/boundary-required.json')):
            directory = marker.parent
            if (directory / 'receipt.json').exists() or (directory / 'failure.json').exists() or list(directory.glob('restart-*.json')):
                continue
            enrolled = completion.read(marker)
            rid = directory.name
            try:
                role_boundary.check(Path.cwd(), *completion.paths(Path.cwd()), rid)
            except run_evidence.EvidenceError:
                try:
                    mark_failed(enrolled['feature_id'], f'run {rid}: role boundary violation; inspect reports and --restart-run', args.max_attempts)
                except (ValueError, OSError, OrchestratorError):
                    pass  # Preserve malformed state for explicit recovery; never overwrite other Features.
                raise
    startup_protocol()

    if args.record_coding:
        if not args.run_id or not args.evidence_file:
            raise OrchestratorError("--record-coding requires --run-id and --evidence-file")
        feature = feature_by_id(load_state(), args.record_coding)
        try:
            with state_store.ownership(FEATURES_PATH):
                feature = feature_by_id(load_state(), args.record_coding)
                if not state_store.ready(load_state(), feature):
                    raise state_store.StateError('feature dependencies are not ready')
                completion.record_coding(Path.cwd(), feature, args.run_id, 'provider-native-v1', args.evidence_file.read_text())
        except (run_evidence.EvidenceError, OSError, ValueError) as exc:
            write_failure_run_record(feature['id'], f"Coding receipt rejected for requested run {args.run_id}; active run {feature.get('active_run')}: {exc}")
            raise

        print(f"Coding receipt recorded for {args.record_coding}, run {args.run_id}")
        return 0

    if args.render_prompt:
        prompt_names = {
            "plan": "plan.md",
            "work": "work.md",
            "evaluate": "evaluate.md",
            "continue": "continue.md",
            "work-fast": "work-fast.md",
        }
        print(prompt_template(prompt_names[args.render_prompt]))
        return 0

    if args.eval_only:
        results = [evaluate_feature(feature_id, args.dry_run) for feature_id in feature_ids_for_eval(args.eval_only)]
        return 0 if all(results) else 1

    if args.work_fast:
        results = [run_work_fast_round(round_no, args.max_attempts, args.dry_run) for round_no in range(1, args.max_rounds + 1)]
        return 0 if all(results) else 1

    results = [run_verified_round(round_no, args.max_attempts, args.dry_run, "work")
               for round_no in range(1, args.max_rounds + 1)]
    return 0 if all(results) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OrchestratorError, run_evidence.EvidenceError, OSError, ValueError) as exc:
        print(f"orchestrator error: {exc}", file=sys.stderr)
        raise SystemExit(1)
