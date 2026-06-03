#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).resolve().parents[1]
BUNDLED_TEMPLATE = SKILL_DIR / "assets" / "template"
TEMPLATE_MANIFEST = ".agent-harness-template.json"
INSTALL_MANIFEST = ".agent-harness/manifest.json"
TEMPLATE_VERSION = "0.2.0"
MODE_CHOICES = {"new", "adopt", "repair", "check"}

REQUIRED_TEMPLATE_FILES = [
    TEMPLATE_MANIFEST,
    "AGENTS.md",
    "SPEC.md",
    "feature_list.json",
    "progress.md",
    "init.sh",
    "Makefile",
    "QUALITY.md",
    "orchestrator.py",
    "scripts/init.sh",
    "scripts/validate-state.py",
    "scripts/validate-feature.sh",
    "prompts/work.md",
    "prompts/evaluate.md",
    "docs/README.md",
    "runs/RUN_TEMPLATE.md",
]

PROJECT_OWNED_STATE = {"SPEC.md", "feature_list.json", "progress.md"}
MERGE_SENSITIVE = {"AGENTS.md", "README.md", "Makefile"}
OPTIONAL_PREFIXES = (".github/", "examples/")
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}

FRESH_FEATURE_LIST = {"features": []}
FRESH_PROGRESS = """# Progress

## Current System Status

Harness state has been reset for a new project.

## Last Completed Feature

None.

## Next Feature

Add the first feature to `feature_list.json`.

## Known Issues

- Project-specific requirements and verification are not defined yet.
"""


class HarnessInitError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize or repair an AI Agent Harness project.")
    parser.add_argument("--root", default=".", help="Target project root. Defaults to the current directory.")
    parser.add_argument("--mode", choices=sorted(MODE_CHOICES), default="adopt")
    parser.add_argument("--template-root", help="Override the template root used for copying harness files.")
    parser.add_argument("--force", action="store_true", help="Overwrite conflicting files. Requires explicit user approval.")
    parser.add_argument("--dry-run", action="store_true", help="Report planned changes without writing files.")
    return parser.parse_args()


def find_template_root(explicit: Optional[str]) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.append(BUNDLED_TEMPLATE)

    # When this skill is copied inside a harness repository without bundled assets,
    # the repository root itself can serve as the template source.
    candidates.append(SKILL_DIR.parents[1])

    for candidate in candidates:
        root = candidate.resolve()
        if all((root / path).exists() for path in REQUIRED_TEMPLATE_FILES):
            return root
    checked = ", ".join(str(path.resolve()) for path in candidates)
    raise HarnessInitError(f"no usable harness template found; checked: {checked}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def category_for(rel: Path) -> str:
    text = rel.as_posix()
    if text in PROJECT_OWNED_STATE:
        return "project-owned state"
    if text in MERGE_SENSITIVE:
        return "merge-sensitive"
    if text == TEMPLATE_MANIFEST:
        return "template manifest"
    if text.startswith(INSTALL_MANIFEST):
        return "installation manifest"
    if text.startswith(OPTIONAL_PREFIXES):
        return "optional integration"
    return "harness-owned static"


def iter_template_files(template_root: Path):
    for path in sorted(template_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(template_root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.parts and rel.parts[0] == "runs" and rel.name not in {"RUN_TEMPLATE.md", ".gitkeep"}:
            continue
        if rel.parts[:3] == ("skills", "ai-agent-harness", "assets"):
            continue
        if rel.as_posix().startswith(".agent-harness/"):
            continue
        yield rel


def build_template_manifest(template_root: Path) -> dict:
    files = {}
    for rel in iter_template_files(template_root):
        files[rel.as_posix()] = {
            "category": category_for(rel),
            "sha256": sha256(template_root / rel),
        }
    return {
        "schema_version": 1,
        "template_version": TEMPLATE_VERSION,
        "file_categories": {
            "harness-owned static": "Copied and drift-checked by content hash.",
            "project-owned state": "Copied or reset during initialization, then validated semantically instead of byte-compared.",
            "merge-sensitive": "Never overwritten by default because the target project may already own this file.",
            "optional integration": "Copied when missing and reported when changed, but not required for core harness validity.",
            "template manifest": "Template metadata used for future drift checks.",
        },
        "files": files,
    }


def read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def installed_manifest(root: Path) -> Optional[dict]:
    return read_json(root / INSTALL_MANIFEST)


def ensure_parent(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path, dry_run: bool) -> None:
    ensure_parent(dst, dry_run)
    if not dry_run:
        shutil.copy2(src, dst)


def reset_project_state(root: Path, dry_run: bool) -> list[str]:
    changed = []
    feature_path = root / "feature_list.json"
    progress_path = root / "progress.md"
    if not dry_run:
        feature_path.write_text(json.dumps(FRESH_FEATURE_LIST, indent=2) + "\n")
        progress_path.write_text(FRESH_PROGRESS)
    changed.extend(["feature_list.json", "progress.md"])
    return changed


def validate_feature_list(path: Path) -> tuple[bool, str]:
    data = read_json(path)
    if data is None:
        return False, "feature_list.json is missing or invalid JSON"
    features = data.get("features")
    if not isinstance(features, list):
        return False, "feature_list.json must contain a features array"
    seen = set()
    for feature in features:
        if not isinstance(feature, dict):
            return False, "each feature must be an object"
        feature_id = feature.get("id")
        if not isinstance(feature_id, str) or not feature_id:
            return False, "each feature must have an id"
        if feature_id in seen:
            return False, f"duplicate feature id: {feature_id}"
        seen.add(feature_id)
        for key in ["title", "description", "last_error", "status"]:
            if key not in feature:
                return False, f"feature {feature_id} is missing {key}"
        if not isinstance(feature.get("acceptance"), list):
            return False, f"feature {feature_id} must have acceptance list"
        if not isinstance(feature.get("passes"), bool):
            return False, f"feature {feature_id} must have boolean passes"
        if not isinstance(feature.get("attempts"), int):
            return False, f"feature {feature_id} must have integer attempts"
    return True, "ok"


def semantic_validation(root: Path) -> dict:
    required = [
        "AGENTS.md",
        "SPEC.md",
        "feature_list.json",
        "progress.md",
        "init.sh",
        "QUALITY.md",
        "orchestrator.py",
        "scripts/validate-state.py",
        "scripts/check-failure-domains.sh",
        "prompts/work.md",
        "prompts/evaluate.md",
        "docs/README.md",
        "runs/RUN_TEMPLATE.md",
    ]
    missing = [path for path in required if not (root / path).exists()]
    checks = []
    if missing:
        checks.append("missing required semantic files: " + ",".join(missing))

    agents = root / "AGENTS.md"
    if agents.exists():
        text = agents.read_text(errors="replace")
        for phrase in ["Required Startup Protocol", "State Safety Rules", "External Behavior Verification"]:
            if phrase not in text:
                checks.append(f"AGENTS.md missing {phrase}")

    progress = root / "progress.md"
    if progress.exists():
        text = progress.read_text(errors="replace")
        for phrase in ["Current System Status", "Next Feature", "Known Issues"]:
            if phrase not in text:
                checks.append(f"progress.md missing {phrase}")

    feature_ok, feature_reason = validate_feature_list(root / "feature_list.json")
    if not feature_ok:
        checks.append(feature_reason)

    for script in ["init.sh", "scripts/validate-state.py", "scripts/check-failure-domains.sh"]:
        if not (root / script).exists():
            continue
        if script.endswith(".sh") and not is_executable(root / script):
            checks.append(f"{script} is not executable")

    init_ok = run_quick_init(root)
    if not init_ok:
        checks.append("HARNESS_SKIP_TEST_LAYERS=1 ./init.sh failed")

    return {
        "state_valid": "false" if checks else "true",
        "runnable_harness": "false" if checks else "true",
        "state_errors": checks,
    }


def is_executable(path: Path) -> bool:
    return bool(path.stat().st_mode & 0o111)


def run_quick_init(root: Path) -> bool:
    init = root / "init.sh"
    if not init.exists():
        return False
    try:
        result = subprocess.run(
            [str(init)],
            cwd=str(root),
            text=True,
            capture_output=True,
            env={**os.environ, "HARNESS_SKIP_TEST_LAYERS": "1"},
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def classify_files(template_root: Path, target_root: Path):
    missing = []
    unchanged = []
    conflicts = []
    drift = []
    project_state_changed = []
    optional_changed = []
    for rel in iter_template_files(template_root):
        src = template_root / rel
        dst = target_root / rel
        category = category_for(rel)
        if not dst.exists():
            missing.append(rel)
            continue
        if sha256(src) == sha256(dst):
            unchanged.append(rel)
            continue
        if category == "project-owned state":
            project_state_changed.append(rel)
        elif category == "merge-sensitive":
            conflicts.append(rel)
        elif category == "optional integration":
            optional_changed.append(rel)
        elif category == "template manifest":
            drift.append(rel)
        else:
            drift.append(rel)
    return {
        "missing": missing,
        "unchanged": unchanged,
        "conflicts": conflicts,
        "drift": drift,
        "project_state_changed": project_state_changed,
        "optional_changed": optional_changed,
    }


def write_install_manifest(root: Path, template_root: Path, mode: str, dry_run: bool) -> None:
    if dry_run:
        return
    manifest = {
        "schema_version": 1,
        "template_version": TEMPLATE_VERSION,
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": mode,
        "files": {},
    }
    for rel in iter_template_files(template_root):
        dst = root / rel
        if dst.exists():
            manifest["files"][rel.as_posix()] = {
                "category": category_for(rel),
                "sha256": sha256(dst),
            }
    path = root / INSTALL_MANIFEST
    ensure_parent(path, dry_run=False)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def ensure_runs_gitkeep(root: Path, dry_run: bool) -> None:
    gitkeep = root / "runs" / ".gitkeep"
    if gitkeep.exists() or dry_run:
        return
    gitkeep.parent.mkdir(parents=True, exist_ok=True)
    gitkeep.write_text("")


def should_copy_missing(mode: str, rel: Path) -> bool:
    category = category_for(rel)
    if mode == "repair":
        return category in {
            "harness-owned static",
            "template manifest",
            "optional integration",
            "project-owned state",
            "merge-sensitive",
        }
    return True


def initialize(args: argparse.Namespace) -> int:
    target_root = Path(args.root).resolve()
    template_root = find_template_root(args.template_root)
    target_root.mkdir(parents=True, exist_ok=True)

    classification = classify_files(template_root, target_root)
    missing = classification["missing"]
    conflicts = classification["conflicts"]
    drift = classification["drift"]

    installed = installed_manifest(target_root)
    semantic = semantic_validation(target_root)
    if args.mode == "check":
        print_summary(args.mode, template_root, target_root, classification, semantic, installed, [], [], [], [])
        return 0 if check_is_clean(classification, semantic, installed) else 1

    created = []
    overwritten = []
    reset = []
    blocking_conflicts = [] if args.force else conflicts
    if blocking_conflicts:
        print_summary(args.mode, template_root, target_root, classification, semantic, installed, [], blocking_conflicts, [], [])
        return 1

    for rel in missing:
        if should_copy_missing(args.mode, rel):
            copy_file(template_root / rel, target_root / rel, args.dry_run)
            created.append(rel)

    writable_conflicts = conflicts + drift if args.force else []
    for rel in writable_conflicts:
        copy_file(template_root / rel, target_root / rel, args.dry_run)
        overwritten.append(rel)

    if args.mode in {"new", "adopt"}:
        reset = reset_project_state(target_root, args.dry_run)
    elif args.mode == "repair":
        for rel in sorted(PROJECT_OWNED_STATE):
            if rel in {path.as_posix() for path in missing}:
                reset.append(rel)

    ensure_runs_gitkeep(target_root, args.dry_run)
    if not blocking_conflicts:
        write_install_manifest(target_root, template_root, args.mode, args.dry_run)

    classification_after = classify_files(template_root, target_root) if not args.dry_run else classification
    semantic_after = semantic_validation(target_root) if not args.dry_run else semantic
    installed_after = installed_manifest(target_root) if not args.dry_run else installed
    print_summary(
        args.mode,
        template_root,
        target_root,
        classification_after,
        semantic_after,
        installed_after,
        created,
        blocking_conflicts,
        overwritten,
        reset,
    )
    return 1 if blocking_conflicts else 0


def check_is_clean(classification: dict, semantic: dict, installed: Optional[dict]) -> bool:
    return (
        not classification["missing"]
        and not classification["conflicts"]
        and not classification["drift"]
        and semantic["state_valid"] == "true"
        and installed is not None
        and installed.get("template_version") == TEMPLATE_VERSION
    )


def next_action(classification: dict, semantic: dict, installed: Optional[dict]) -> str:
    if classification["conflicts"]:
        return "review merge-sensitive conflicts; rerun with --force only after explicit approval"
    if classification["missing"]:
        return "run repair to restore missing harness files"
    if classification["drift"]:
        return "review harness-owned drift; repair missing files or use explicit force/upgrade when appropriate"
    if installed is None:
        return "run repair to write an installation manifest"
    if installed.get("template_version") != TEMPLATE_VERSION:
        return "template version drift detected; review changes before upgrade"
    if semantic["state_valid"] != "true":
        return "fix semantic harness validation errors"
    return "harness is installed and runnable"


def print_list(name: str, paths: list[Path]) -> None:
    print(f"{name}={len(paths)}")
    if paths:
        print(f"{name}_files:")
        for rel in paths:
            print(f"- {rel.as_posix()}")


def print_summary(
    mode: str,
    template_root: Path,
    target_root: Path,
    classification: dict,
    semantic: dict,
    installed: Optional[dict],
    created: list[Path],
    blocking_conflicts: list[Path],
    overwritten: list[Path],
    reset: list[str],
) -> None:
    print(f"mode={mode}")
    print(f"template_root={template_root}")
    print(f"target_root={target_root}")
    print(f"template_version={TEMPLATE_VERSION}")
    print(f"installed_version={installed.get('template_version') if installed else 'none'}")
    print(f"state_valid={semantic['state_valid']}")
    print(f"runnable_harness={semantic['runnable_harness']}")
    print_list("missing", classification["missing"])
    print(f"unchanged={len(classification['unchanged'])}")
    print_list("conflicts", classification["conflicts"])
    print_list("drift", classification["drift"])
    print_list("project_state_changed", classification["project_state_changed"])
    print_list("optional_changed", classification["optional_changed"])
    print_list("created", created)
    print_list("overwritten", overwritten)
    print(f"state_reset={','.join(reset) if reset else 'none'}")
    if semantic["state_errors"]:
        print("state_errors:")
        for error in semantic["state_errors"]:
            print(f"- {error}")
    if blocking_conflicts:
        print("blocking_conflicts:")
        for rel in blocking_conflicts:
            print(f"- {rel.as_posix()}")
        print("Use --force only after explicit approval to overwrite conflicts.")
    print(f"next_action={next_action(classification, semantic, installed)}")


def main() -> int:
    try:
        return initialize(parse_args())
    except HarnessInitError as exc:
        print(f"init_harness error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
