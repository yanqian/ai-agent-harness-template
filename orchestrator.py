#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

FEATURES_PATH = Path("feature_list.json")
PROGRESS_PATH = Path("progress.md")
PROMPTS_DIR = Path("prompts")
MAX_ROUNDS = 1
MAX_ATTEMPTS = 3


class OrchestratorError(Exception):
    pass


def sh(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, text=True, check=check)


def run_capture(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def load_state() -> dict:
    data = json.loads(FEATURES_PATH.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        raise OrchestratorError("feature_list.json must contain a top-level features array.")
    return data


def save_state(data: dict) -> None:
    FEATURES_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


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
    priority = {"P0": 0, "P1": 1, "P2": 2}
    candidates = []
    ordered_features = features(data)
    for feature in ordered_features:
        attempts = int(feature.get("attempts", 0))
        status = normalize_status(feature)
        if feature.get("passes") is False and status in {"todo", "in_progress"} and attempts < max_attempts:
            candidates.append(feature)
    candidates.sort(key=lambda item: (priority.get(item.get("priority", "P2"), 9), ordered_features.index(item)))
    return candidates[0] if candidates else None


def mark_in_progress(feature_id: str) -> None:
    data = load_state()
    feature = feature_by_id(data, feature_id)
    feature["status"] = "in_progress"
    feature["attempts"] = int(feature.get("attempts", 0)) + 1
    feature["last_error"] = ""
    save_state(data)


def mark_done(feature_id: str) -> None:
    data = load_state()
    feature = feature_by_id(data, feature_id)
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


def prompt_template(name: str) -> str:
    path = PROMPTS_DIR / name
    if not path.exists():
        raise OrchestratorError(f"Missing prompt template: {path}")
    return path.read_text()


def coding_prompt(feature_id: str) -> str:
    return f"{prompt_template('work.md')}\n\nSelected feature ID: `{feature_id}`\n"


def evaluator_prompt(feature_id: str) -> str:
    return f"{prompt_template('evaluate.md')}\n\nSelected feature ID: `{feature_id}`\n"


def agent_command(prompt: str) -> list[str]:
    raw = os.environ.get("HARNESS_AGENT_COMMAND", "").strip()
    if not raw:
        raise OrchestratorError(
            "HARNESS_AGENT_COMMAND is not set. Use --dry-run to preview prompts, "
            "or set it to a command that accepts the prompt as its final argv."
        )
    return raw.split() + [prompt]


def run_agent(prompt: str, dry_run: bool, label: str) -> subprocess.CompletedProcess[str]:
    if dry_run:
        print(f"\n== {label} prompt ==")
        print(prompt)
        return subprocess.CompletedProcess(["dry-run"], 0, stdout="", stderr="")
    command = agent_command(prompt)
    result = subprocess.run(command, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="", flush=True)
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr, flush=True)
    return result


def evaluator_result(feature_id: str, result: subprocess.CompletedProcess[str]) -> tuple[bool, str]:
    output = "\n".join(part for part in [result.stdout, result.stderr] if part)
    pass_line = f"EVAL_PASS: {feature_id}"
    fail_prefix = f"EVAL_FAIL: {feature_id}:"
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith(fail_prefix):
            return False, stripped[len(fail_prefix):].strip() or "Evaluator reported failure."
    for line in output.splitlines():
        if line.strip() == pass_line:
            return True, ""
    return False, f"Evaluator did not emit required pass line: {pass_line}"


def evaluate_feature(feature_id: str, dry_run: bool) -> bool:
    print(f"\n== Evaluate: {feature_id} ==", flush=True)
    result = run_agent(evaluator_prompt(feature_id), dry_run, "Evaluator Agent")
    if dry_run:
        return True
    if result.returncode != 0:
        print(f"EVAL_FAIL: {feature_id}: evaluator exited with code {result.returncode}", flush=True)
        return False
    passed, reason = evaluator_result(feature_id, result)
    if passed:
        print(f"Evaluator accepted {feature_id}.", flush=True)
        return True
    print(f"EVAL_FAIL: {feature_id}: {reason}", flush=True)
    return False


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
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    startup_protocol()

    if args.eval_only:
        results = [evaluate_feature(feature_id, args.dry_run) for feature_id in feature_ids_for_eval(args.eval_only)]
        return 0 if all(results) else 1

    for round_no in range(1, args.max_rounds + 1):
        data = load_state()
        feature = pick_feature(data, args.max_attempts)
        if not feature:
            print("No runnable unfinished feature left.", flush=True)
            return 0
        feature_id = str(feature["id"])
        print(f"\n== Round {round_no}: {feature_id} ==", flush=True)

        if args.dry_run:
            run_agent(coding_prompt(feature_id), dry_run=True, label="Coding Agent")
            run_agent(evaluator_prompt(feature_id), dry_run=True, label="Evaluator Agent")
            continue

        mark_in_progress(feature_id)
        coding_result = run_agent(coding_prompt(feature_id), dry_run=False, label="Coding Agent")
        if coding_result.returncode != 0:
            mark_failed(feature_id, f"coding agent exited with code {coding_result.returncode}", args.max_attempts)
            continue

        evaluator = run_agent(evaluator_prompt(feature_id), dry_run=False, label="Evaluator Agent")
        if evaluator.returncode != 0:
            mark_failed(feature_id, f"evaluator exited with code {evaluator.returncode}", args.max_attempts)
            continue

        passed, reason = evaluator_result(feature_id, evaluator)
        if passed:
            mark_done(feature_id)
            print(f"Done: {feature_id}", flush=True)
        else:
            mark_failed(feature_id, reason or "Evaluator rejected the feature.", args.max_attempts)
            print(f"Evaluation failed: {feature_id}: {reason}", flush=True)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OrchestratorError as exc:
        print(f"orchestrator error: {exc}", file=sys.stderr)
        raise SystemExit(1)

