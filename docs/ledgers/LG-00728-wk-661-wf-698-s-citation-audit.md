---
id: LG-728
family: ledger
title: WK-661 — `WF-698`'s citation audit
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-17
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — `WF-698`'s citation audit, 2026-08-17 *(in progress, not closed)*

The eighth slice, and the smallest: FR-19(i), `audit-docs.py`'s **check 21**. The roadmap
put it before `WF-698`'s journey test, and that ordering was right — the audit is what gives the
journey test something to stand on, because a journey citing an interface no spec declares is
drift no other check in this repository can see. `audit-docs.py` check 14's "workflow coverage"
measures whether a journey *mentions* a requirement id, which is the weaker question plan
review 2 found it was answering.

| Delivered | Evidence |
|---|---|
| Check 21 | Every `` `METHOD /path` `` and `` `name()` `` in `WF-698…05` must be declared in a spec's §5.1 or §5.2. Current run: **30 endpoint citations, 7 function citations, all declared** |
| It runs in CI already | `docs.yml` triggers on `docs/**` and runs the script; no workflow change was needed, which is what FR-19's "on every docs change" asked for |
| The enforcement is **visible** | `tests/test_repository_invariants.py` marks it `FR-19`, so `req-coverage.py` can see it. Re-auditing WK-657 reported half its scope missing while the enforcement worked perfectly in CI; this is the fix for that class of blindness, applied at the time rather than later |
| A citation **form**, in `docs/workflows/README.md` | An endpoint is `` `METHOD /path` ``; a `pricing-core` function is `` `name()` `` — the parentheses are what distinguish a citation from a column name, a parameter or prose in the same cell. Without them the check is a heuristic over every backticked token in a row, and `control`, `_rejected`, `f`, `where` and `Piecewise` all appear in exactly those rows |
| Both halves proved by injection | An undeclared endpoint and an undeclared function each failed, and the summary line reports the count rather than saying "all declared" above a `FAILED` block |

**It found real drift on its first run.** WF-698 A8 cited `profile_version()`; `01` §5.2 was
corrected to `profile_frame` / `profile_parquet` on 2026-08-15 and the journey was not updated,
so the journey named a function that never existed. The spec was right and the journey wrong —
resolved by correcting the journey to `profile_frame()`, which is what the profiling handler
actually calls.

**One deliberate looseness, counted and printed.** A journey writes
`POST /environments/prod/deployments` where `03` §5.1 declares `/environments/{env}/deployments`
— and the journey is *right* to be concrete, since which environment is deployed to is the
step's content. So a declared `{}` segment matches a literal one, after an exact match is tried
first. The cost is that a citation of `/models/nonsense` would match a declared `/models/{}`;
the audit prints how many citations used the fallback (currently 4, all of them environments)
so the looseness is visible rather than assumed away. Refusing it instead would report four
declared, working endpoints as missing, and a check that cries wolf is one everybody learns to
skip.

**One thing worth a plan-review question rather than a unilateral change.** The *number* of
checks is stated in six places — `CLAUDE.md` three times, `docs.yml`'s comment,
`.claude/skills/README.md`, and the `docs-audit` skill's frontmatter — and adding one check
meant editing all six. `CLAUDE.md` §0's own rule is that counts which change do not belong in
it, and this is a count that changes. Updated everywhere for now; whether the number should be
stated at all is the maintainer's call.

**Not delivered:** FR-19(ii), one end-to-end test per journey. Still WK-661's for `WF-698`, and
now writable — both arms of that journey run, selection (E1/E2) since the comparison slice and
approval (E6–E10) since the lifecycle slice. The requirement's own text refuses the cheap
version: marking an existing test with a journey id claims a journey where one slice is
covered.
