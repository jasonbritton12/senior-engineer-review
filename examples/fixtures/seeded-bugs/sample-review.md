Verdict: Request Changes — one Critical (SQL injection) blocks merge.

## Required Actions

- [ ] Fix SER-001 (SQL injection) before merge — Critical.
- [ ] Fix SER-002 (null address on guest checkout) — Major.
- [ ] Fix SER-003 (non-atomic counter) — Major.
- [ ] Remove SER-004 (unused import) — Minor.

## Findings

- SER-001 · Critical · `app.py:6` · User input is interpolated into SQL via an
  f-string. Evidence: Observed, High. Fix: use a parameterized query (`?` placeholder).
- SER-002 · Major · `app.py:12` · `customer.address.line1` dereferences a
  possibly-None address; guest checkout raises AttributeError. Evidence: Observed,
  High. Fix: guard None and fall back to billing address.
- SER-003 · Major · `utils.py:9` · Non-atomic read-modify-write on `counter`
  races under threads. Evidence: Observed, High. Fix: use a lock or atomic increment.
- SER-004 · Minor · `utils.py:1` · Unused `import os`. Evidence: Observed, High.
  Fix: remove the import.

## Assumptions & Residual Risk

- No tests cover any path; all four fixes need regression coverage.
- AI-generated advisory review, not an authoritative production sign-off.
