#!/usr/bin/env python3
"""Assert a release snapshot matches the canonical root files.

Prevents the released copy of the skill from silently drifting from root.
Stdlib only. Exit 0 if in sync, 1 on any drift.

Usage:
    python3 scripts/check_release_drift.py            # checks newest releases/vN
    python3 scripts/check_release_drift.py v1.1.0     # checks a specific release
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Canonical files that must be identical between root and a release snapshot.
CANONICAL = [
    "SKILL.md",
    "README.md",
    "agents/openai.yaml",
    "references/review-rubric.md",
    "examples/canonical-review-template.md",
]


def newest_release():
    rel = ROOT / "releases"
    versions = sorted(
        (p for p in rel.glob("v*") if p.is_dir()),
        key=lambda p: [int(x) for x in p.name.lstrip("v").split(".") if x.isdigit()],
    )
    return versions[-1] if versions else None


def main():
    if len(sys.argv) > 1:
        release = ROOT / "releases" / sys.argv[1]
    else:
        release = newest_release()
    if not release or not release.exists():
        print("FAIL: no release directory found")
        return 1

    drift = []
    for rel_path in CANONICAL:
        root_file = ROOT / rel_path
        snap_file = release / rel_path
        if not root_file.exists():
            continue  # canonical file not present at root; skip
        if not snap_file.exists():
            drift.append(f"{rel_path}: missing in {release.name}")
            continue
        if root_file.read_bytes() != snap_file.read_bytes():
            drift.append(f"{rel_path}: differs between root and {release.name}")

    if drift:
        print(f"FAIL: drift detected against {release.name}")
        for d in drift:
            print(f"  - {d}")
        return 1
    print(f"OK: {release.name} matches root canonical files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
