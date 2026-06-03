#!/usr/bin/env python3
import argparse
import filecmp
import json
import shutil
import sys
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).resolve().parents[1]
BUNDLED_TEMPLATE = SKILL_DIR / "assets" / "template"
MODE_CHOICES = {"new", "adopt", "repair", "check"}

REQUIRED_TEMPLATE_FILES = [
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

STATE_FILES = {"feature_list.json", "progress.md"}
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


def iter_template_files(template_root: Path):
    for path in sorted(template_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(template_root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.parts[:3] == ("skills", "ai-agent-harness", "assets"):
            continue
        yield rel


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


def classify_files(template_root: Path, target_root: Path):
    missing = []
    unchanged = []
    conflicts = []
    for rel in iter_template_files(template_root):
        src = template_root / rel
        dst = target_root / rel
        if not dst.exists():
            missing.append(rel)
        elif filecmp.cmp(src, dst, shallow=False):
            unchanged.append(rel)
        else:
            conflicts.append(rel)
    return missing, unchanged, conflicts


def initialize(args: argparse.Namespace) -> int:
    target_root = Path(args.root).resolve()
    template_root = find_template_root(args.template_root)
    target_root.mkdir(parents=True, exist_ok=True)

    missing, unchanged, conflicts = classify_files(template_root, target_root)
    writable_conflicts = conflicts if args.force else []
    blocking_conflicts = [] if args.force else conflicts

    if args.mode == "check":
        print_summary(args.mode, template_root, target_root, missing, unchanged, conflicts, [], blocking_conflicts)
        return 1 if missing or conflicts else 0

    created = []
    overwritten = []
    for rel in missing:
        copy_file(template_root / rel, target_root / rel, args.dry_run)
        created.append(rel)

    for rel in writable_conflicts:
        copy_file(template_root / rel, target_root / rel, args.dry_run)
        overwritten.append(rel)

    reset = []
    if args.mode in {"new", "adopt"}:
        reset = reset_project_state(target_root, args.dry_run)
    elif args.mode == "repair":
        for rel in STATE_FILES:
            if rel in {str(path) for path in missing}:
                reset.append(rel)

    ensure_runs_gitkeep(target_root, args.dry_run)
    print_summary(args.mode, template_root, target_root, missing, unchanged, conflicts, created, blocking_conflicts, overwritten, reset)
    return 1 if blocking_conflicts else 0


def ensure_runs_gitkeep(root: Path, dry_run: bool) -> None:
    gitkeep = root / "runs" / ".gitkeep"
    if gitkeep.exists() or dry_run:
        return
    gitkeep.parent.mkdir(parents=True, exist_ok=True)
    gitkeep.write_text("")


def print_summary(
    mode: str,
    template_root: Path,
    target_root: Path,
    missing: list[Path],
    unchanged: list[Path],
    conflicts: list[Path],
    created: list[Path],
    blocking_conflicts: list[Path],
    overwritten: Optional[list[Path]] = None,
    reset: Optional[list[str]] = None,
) -> None:
    overwritten = overwritten or []
    reset = reset or []
    print(f"mode={mode}")
    print(f"template_root={template_root}")
    print(f"target_root={target_root}")
    print(f"missing={len(missing)}")
    print(f"unchanged={len(unchanged)}")
    print(f"conflicts={len(conflicts)}")
    print(f"created={len(created)}")
    print(f"overwritten={len(overwritten)}")
    print(f"state_reset={','.join(reset) if reset else 'none'}")
    if blocking_conflicts:
        print("blocking_conflicts:")
        for rel in blocking_conflicts:
            print(f"- {rel}")
        print("Use --force only after explicit approval to overwrite conflicts.")


def main() -> int:
    try:
        return initialize(parse_args())
    except HarnessInitError as exc:
        print(f"init_harness error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
