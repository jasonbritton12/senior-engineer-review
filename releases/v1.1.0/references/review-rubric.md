# Review Rubric

Scoring detail for the Senior Engineer Review skill. Loaded on demand so `SKILL.md`
stays lean. Reference this file when you need severity definitions, the verdict
mapping, or the finding schema.

## Severity definitions

| Severity | Scope | Examples |
|---|---|---|
| **Critical** | Bugs and security defects that can cause data loss, corruption, outage, privilege escalation, or exploited trust boundaries. | Injection, missing authz, unhandled null on a primary path, secret in source, prompt-injection on an agent. |
| **Major** | Logic or performance defects that produce wrong results, meaningful slowness, or fragile behavior under realistic load. | Race condition under contention, O(n²) on a hot path, incorrect edge-case result, missing error handling on a fallible call. |
| **Minor** | Style, readability, and maintainability issues with no functional impact. | Naming, dead code, inconsistent formatting, missing doc comment, thin tests. |

## Severity → verdict mapping (the anchor)

| Finding state | Verdict |
|---|---|
| Any unresolved **Critical** | **Request Changes** (never Merge) |
| **Major**-only, fixes are low-risk and well-understood | **Conditional Merge** (merge after the listed fixes) |
| **Major** present but fixes are risky or unclear | **Request Changes** |
| Only **Minor** findings, or none | **Merge** |

A verdict that contradicts its own findings (e.g. "Merge" with an open Critical)
is invalid. Re-derive the verdict from the highest unresolved severity.

## Per-finding schema

Report each finding on one line using this schema:

```
[SER-###] [Severity] [path:line] [Issue] [Evidence: Observed|Inferred|Assumed + confidence] [Why it matters in production] [Fix]
```

- IDs are stable within a review (`SER-001`, `SER-002`, …) so they can be
  referenced in follow-up/progress-delta reviews.
- Every Critical and Major finding must quote the offending `path:line` as proof.
- A finding whose evidence is `Assumed` or `unverified` may not be ranked Critical
  unless corroborated by independent `Observed` evidence.

## Mapping to the sibling skills' scale

The sibling skills (`senior-security-review`, `greenlight-review-board`) use a
four-tier Critical/High/Medium/Low scale. This skill keeps the engineering-native
Critical/Major/Minor three-tier scale. When cross-referencing across a suite review,
use this mapping:

| This skill | Sibling scale |
|---|---|
| Critical | Critical |
| Major | High (or Medium when impact is contained) |
| Minor | Low |

## Evidence confidence

- **High** — directly observed in code you read this session.
- **Medium** — inferred from strong surrounding evidence.
- **Low** — assumed or based on incomplete context; state what would raise confidence.

State residual risk and missing tests explicitly even when recommending Merge.
