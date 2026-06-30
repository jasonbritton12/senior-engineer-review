# Senior Engineer Review

A strict, advisory-only senior-engineer review skill that gives a final
production-grade gate on merge readiness — severity-ranked findings, explicit
edge-case hunting, concrete code-level fixes, and a clear **Merge / Conditional
Merge / Request Changes** verdict. It never modifies your code or docs.

- **Version:** v1.1.0 · **Last reviewed:** 2026-06-29

## What it is (and isn't)

This is an engineering-quality and merge-readiness gate. It is **not** a security
or UX sign-off:

- For a security gate, use **`senior-security-review`**.
- For a UX/product gate, use **`senior-ux-design-review`**.
- For a go/no-go ship board, use **`greenlight-review-board`**.

All findings are advisory and AI-generated — a human retains merge authority.

## Usage

Invoke the skill and point it at what you want reviewed:

```
/senior-engineer-review review the pending diff on this branch for merge readiness
```

It will (a) confirm scope if unclear, (b) review for correctness, security,
performance, and maintainability, and (c) return a verdict-first report.

### Example output (compact)

```
Verdict: Conditional Merge — one Major issue with a low-risk fix.

SER-001 Major · api/orders.py:88 · Unhandled None on guest checkout (500s).
        Evidence: Observed, High. Fix: guard + fall back to billing address.

Required actions:
- [ ] Fix SER-001 before merge.
```

See `examples/canonical-review-template.md` for the full output shape, including
the expanded report used when a Critical or Major finding is present.

## How it works

| File | Purpose |
|---|---|
| `SKILL.md` | Core instruction set: intake, trust/evidence rules, review steps, output contract. |
| `references/review-rubric.md` | Severity definitions, severity→verdict mapping, finding schema. |
| `examples/canonical-review-template.md` | Compact and full sample reports. |
| `scripts/` | Eval harness: contract linter, fixture scorer, release-drift and skill-lint checks. See `scripts/README.md`. |

## Quality

The skill ships with an eval harness so its quality is verifiable, not asserted.
Run `python3 scripts/lint_skill.py` to validate the skill file, and see
`scripts/README.md` for the fixture-based catch-rate, prompt-injection, and
fabricated-citation checks.
