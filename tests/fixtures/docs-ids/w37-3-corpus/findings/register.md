# Findings register (fixture)

Per Ruling 71 (`docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md`), this table —
not any `FD-` essay's header — is what `doc-index.py --phase` reads for the findings
element. Shape reused from `docs/audit/register.md`'s own convention (`register-lint.py`
already parses it), not invented: the header row is found by *position*, immediately
before the `|---|` delimiter row.

| Finding id | Concerns | Work item | Phase | Decision |
|---|---|---|---|---|
| FD-1450 | Alpha gap, no owner yet | WK-1200 | P9 | unowned |
| FD-1451 | Alpha gap, fixed | WK-1200 | P9 | fix before close — Resolved 2026-01-18, PR #1 |
| FD-1452 | Alpha gap, accepted as-is | WK-1200 | P9 | accept — noted 2026-01-19 |
| FD-1453 | Gamma gap, carried forward | WK-1220 | P8 | unowned by design |
