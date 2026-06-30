# Canonical Review Template

The exact output shape a Senior Engineer Review should produce. Every report:

- opens with a single `Verdict:` line — **no title heading or preamble above it**;
- uses ATX `## ` (H2) headings for every section, in the order shown;
- never uses bold text (`**Findings**`) as a section header.

The per-finding schema is:

```
SER-### · <Severity> · path:line · <Issue> · Evidence: <Observed|Inferred|Assumed>, <confidence> · Fix: <minimal fix>
```

> The examples below are shown inside blockquotes only to set them apart on this
> page. A real review is the same text **without** the leading `> `.

---

## Example A — Compact report (default)

> Verdict: Conditional Merge — one Major issue with a low-risk fix.
>
> ## Required Actions
>
> - [ ] Fix SER-001 before merge (guard null address).
> - [ ] Optional: remove dead branch SER-002.
>
> ## Findings
>
> - SER-001 · Major · `api/orders.py:88` · Unhandled `None` when
>   `customer.address` is absent; checkout 500s for guest carts. Evidence:
>   Observed, High. Fix: guard and fall back to billing address.
> - SER-002 · Minor · `api/orders.py:140` · Dead branch after early `return`.
>   Evidence: Observed, High. Fix: delete lines 140–146.

---

## Example B — Full report (Critical/Major present, on request, or follow-up)

> Verdict: Request Changes — one Critical (SQL injection) blocks merge.
>
> ## Required Actions
>
> - [ ] Fix SER-001 (SQL injection) before merge — Critical.
> - [ ] Fix SER-002 (race on balance update) — Major.
> - [ ] Add tests for both paths.
>
> ## Severity Ranking
>
> | ID | Severity | Location | Issue |
> |---|---|---|---|
> | SER-001 | Critical | `db/users.py:54` | Raw f-string SQL with user input |
> | SER-002 | Major | `wallet/ledger.py:120` | Read-modify-write on balance without a lock |
> | SER-003 | Minor | `wallet/ledger.py:12` | Unused import |
>
> ## Findings
>
> - SER-001 · Critical · `db/users.py:54` · `query = f"SELECT * FROM users WHERE
>   name = '{name}'"` — user-controlled `name` is interpolated directly. Evidence:
>   Observed, High. Fix: parameterized query (diff below).
> - SER-002 · Major · `wallet/ledger.py:120` · Balance is read, adjusted, then
>   written without a transaction or lock; concurrent debits can double-spend.
>   Evidence: Observed, High. Fix: `SELECT … FOR UPDATE` or an atomic update.
> - SER-003 · Minor · `wallet/ledger.py:12` · `import os` unused. Evidence:
>   Observed, High. Fix: remove.
>
> ## Edge Case Analysis
>
> - Null/empty: `name=""` still injects; covered by SER-001 fix.
> - Concurrency: SER-002 is the race; no other shared mutable state found.
> - Error handling: DB errors propagate uncaught to the handler — acceptable here
>   (framework returns 500 + logs), but no test asserts it.
>
> ## Concrete Fixes
>
> ```diff
> - query = f"SELECT * FROM users WHERE name = '{name}'"
> - cur.execute(query)
> + cur.execute("SELECT * FROM users WHERE name = %s", (name,))
> ```
>
> ```diff
> - bal = read_balance(uid)
> - write_balance(uid, bal - amount)
> + with db.transaction():
> +     bal = read_balance(uid, for_update=True)
> +     if bal < amount:
> +         raise InsufficientFunds(uid)
> +     write_balance(uid, bal - amount)
> ```
>
> ## Assumptions & Residual Risk
>
> - Assumed PostgreSQL (Observed in `requirements.txt`). If another DB, the
>   `FOR UPDATE` syntax may differ — verify.
> - No tests exist for either path; both fixes need regression coverage.
> - *AI-generated advisory review, not an authoritative production sign-off.*
