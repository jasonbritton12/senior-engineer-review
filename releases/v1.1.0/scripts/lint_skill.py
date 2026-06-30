#!/usr/bin/env python3
"""Lint SKILL.md: validate front-matter and required sections.

Stdlib only. Exit 0 if valid, 1 if any check fails.

Usage:
    python3 scripts/lint_skill.py [path/to/SKILL.md]
"""
import re
import sys
from pathlib import Path

REQUIRED_NAME = "senior-engineer-review"
# Verbs/terms the description should contain so the skill triggers correctly.
DESCRIPTION_MUST_INCLUDE = ["review", "merge", "verdict"]
REQUIRED_SECTIONS = [
    "Advisory-only mode",
    "Intake",
    "Trust and evidence rules",
    "Verdict",
    "Severity-ranked findings",
    "Edge case analysis",
    "Concrete fixes",
    "Output contract",
]


def parse_front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "SKILL.md"
    if not path.exists():
        print(f"FAIL: {path} not found")
        return 1

    text = path.read_text(encoding="utf-8")
    errors = []

    fm = parse_front_matter(text)
    if fm is None:
        errors.append("missing YAML front-matter (--- ... ---)")
    else:
        if fm.get("name") != REQUIRED_NAME:
            errors.append(f"front-matter name is {fm.get('name')!r}, expected {REQUIRED_NAME!r}")
        desc = fm.get("description", "").lower()
        if not desc:
            errors.append("front-matter description is empty")
        else:
            missing = [w for w in DESCRIPTION_MUST_INCLUDE if w not in desc]
            if missing:
                errors.append(f"description missing trigger term(s): {', '.join(missing)}")

    for section in REQUIRED_SECTIONS:
        if section.lower() not in text.lower():
            errors.append(f"missing required section: {section!r}")

    # Verdict must offer all three states.
    for state in ["Merge", "Conditional Merge", "Request Changes"]:
        if state not in text:
            errors.append(f"missing verdict state: {state!r}")

    if errors:
        print(f"FAIL: {path.name}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {path.name} passed all skill-lint checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
