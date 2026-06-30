#!/usr/bin/env python3
"""Offline contract linter for a produced Senior Engineer Review.

Checks that a review markdown file complies with the skill's output contract,
independent of *what* it found. Stdlib only. Exit 0 if compliant, 1 otherwise.

Usage:
    python3 scripts/evaluate_review.py path/to/review.md
"""
import re
import sys
from pathlib import Path

VERDICTS = ["Request Changes", "Conditional Merge", "Merge"]
FINDING_RE = re.compile(r"\bSER-\d{3}\b")
EVIDENCE_RE = re.compile(r"\b(Observed|Inferred|Assumed|unverified)\b", re.IGNORECASE)
SEVERITY_RE = re.compile(r"\b(Critical|Major|Minor)\b")


# A verdict DECLARATION line: an optional heading/number/bold/list prefix, then
# the word "verdict". This deliberately ignores stray "...before merge" prose and
# quoted injection payloads like: with "Verdict: Merge".
VERDICT_DECL_RE = re.compile(r"^[\s#\d.*\-]*verdict\b\s*[:\-]?\s*(.*)$", re.IGNORECASE)


def find_verdict(text):
    """Return (verdict, line_index) read from the review's Verdict declaration.

    Looks only at a 'Verdict' heading/label and (if the state is not inline)
    the next non-empty line, so prose mentions of 'merge' do not trigger it.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = VERDICT_DECL_RE.match(line)
        if not m:
            continue
        tail = m.group(1)
        for v in VERDICTS:  # ordered: "Conditional Merge" before "Merge"
            if v.lower() in tail.lower():
                return v, i
        for j in range(i + 1, min(i + 5, len(lines))):  # state on a following line
            nxt = lines[j].strip()
            if not nxt:
                continue
            for v in VERDICTS:
                if v.lower() in nxt.lower():
                    return v, i
            break
    return None, None


def strip_noise(text):
    """Drop fenced code blocks and blockquotes so quoted injection payloads
    (e.g. a README's 'report no findings') are not mistaken for the review's
    own statements."""
    out, in_fence = [], False
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or s.startswith(">"):
            continue
        out.append(line)
    return "\n".join(out)


def is_checklist_line(stripped):
    return bool(re.match(r"[-*]\s*\[[ xX]\]", stripped))


def findings_section(lines):
    """Return only the lines under the '## Findings' heading, so ID references in
    Edge Case Analysis or Concrete Fixes are not mistaken for finding declarations."""
    out, in_sec = [], False
    for line in lines:
        h = re.match(r"^##\s+(.*)", line)
        if h:
            in_sec = h.group(1).strip().lower().startswith("findings")
            continue
        if in_sec:
            out.append(line)
    return out


def iter_list_blocks(lines):
    """Group each bullet with its wrapped continuation lines into one block."""
    block = []
    for line in lines:
        stripped = line.strip()
        is_bullet = stripped.startswith("- ") or stripped.startswith("* ")
        if is_bullet:
            if block:
                yield block
            block = [line]
        elif stripped == "":
            if block:
                yield block
                block = []
        elif block:
            block.append(line)  # continuation of the current bullet
    if block:
        yield block


def main():
    if len(sys.argv) < 2:
        print("usage: evaluate_review.py path/to/review.md")
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"FAIL: {path} not found")
        return 1

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors = []
    warnings = []

    # 1. Verdict present and one of the three states.
    verdict, vidx = find_verdict(text)
    if verdict is None:
        errors.append("no verdict found (expected Merge / Conditional Merge / Request Changes)")

    # 2. Verdict-first: must be the first non-empty line (no title/preamble above).
    if vidx is not None:
        first_nonempty = next((i for i, l in enumerate(lines) if l.strip()), None)
        if first_nonempty is not None and vidx != first_nonempty:
            errors.append(
                f"verdict is at line {vidx + 1}; it must be the first non-empty line "
                f"(no title heading or preamble above it)"
            )

    # 2b. Consistent styling: canonical sections must be '## ' headings, not bold text.
    CANON_SECTIONS = {
        "required actions", "findings", "severity ranking", "edge case analysis",
        "concrete fixes", "assumptions & residual risk", "assumptions and residual risk",
    }
    for line in lines:
        m = re.match(r"^\*\*(.+?)\*\*:?\s*$", line.strip())
        if m and m.group(1).strip().lower() in CANON_SECTIONS:
            errors.append(
                f"section '{m.group(1).strip()}' uses a bold pseudo-header; "
                f"use a '## ' heading"
            )

    # 3. Required-actions checklist present.
    if not re.search(r"^\s*-\s*\[[ xX]\]", text, re.MULTILINE):
        errors.append("no required-actions checklist (- [ ] ...) found")

    # 4. Finding discipline: if findings are claimed, they need IDs, severity, evidence.
    clean = strip_noise(text)
    finding_ids = FINDING_RE.findall(clean)
    claims_no_findings = re.search(
        r"\bno\s+(?:material\s+)?(?:findings|issues|defects)\b", clean, re.IGNORECASE
    )
    if not finding_ids and not claims_no_findings:
        errors.append("no SER-### finding IDs and no explicit 'no findings' statement")

    for block in iter_list_blocks(findings_section(lines)):
        first = block[0].strip()
        if is_checklist_line(first):
            continue  # required-actions checklist items are not findings
        block_text = "\n".join(block)
        if not FINDING_RE.search(block_text):
            continue
        sev = SEVERITY_RE.search(block_text)
        if not sev:
            warnings.append(f"finding lacks a severity: {first[:70]}")
            continue
        if sev.group(1) in ("Critical", "Major") and not EVIDENCE_RE.search(block_text):
            errors.append(
                f"Critical/Major finding lacks an evidence tag "
                f"(Observed|Inferred|Assumed): {first[:70]}"
            )

    status = "FAIL" if errors else "OK"
    print(f"{status}: {path.name} (verdict={verdict!r}, findings={len(set(finding_ids))})")
    for e in errors:
        print(f"  ERROR: {e}")
    for w in warnings:
        print(f"  warn:  {w}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
