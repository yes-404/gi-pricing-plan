---
id: RL-942
family: ruling
title: Q2: partial split, evidenced by what the census shows has already happened
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-01
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-01-nt-0016-q1-q2-q3-q7-general-rulings.md
---

## RL-942 — Q2: partial split, evidenced by what the census shows has already happened

### 1. Verified first, independently, at `052afe3`

| Claim | Verdict |
|---|---|
| Ledgers: 16 files, all in `docs/plans/`, zero growth across three tree readings (`7db62ca`, `b551060`, `4f95fb3`) | **Confirmed unchanged at `052afe3`** — `ls docs/plans/*-ledger.md \| wc -l` returns 16, matching the draft's figure exactly; no ledger has ever appeared outside `docs/plans/` |
| Rulings records: all 25 files (23 suffix + 2 prefix, RL-941 above) sit in `docs/plans/`, none elsewhere | **Confirmed** — `ls docs/plans/` glob for both grammars returns 25 files, zero outside the directory |
| Closure/audit records already occupy three homes without any rule forcing the split | **Confirmed, RL-941 §1** — `docs/audit/work/`, `docs/closures/INDEX.md#closure-recordsmd`, and `docs/plans/*-closure*.md` predate this investigation and were never consolidated |
| Register and findings already occupy two home directories (`docs/findings/register.md`, `docs/audit/findings/`) | **Confirmed** — `docs/findings/register.md` is one file; `docs/audit/findings/` holds 4 `FN.md` files plus a `README.md`, per the draft's §1.6, re-verified by directory listing |
| RFC-897 §10's own recommendation for Q2 was grammar-in-place, on the ground that "splitting multiplies C1 exposure for no reader gain" | **Confirmed as stated** — `.claude/rfcs/0016-…md:224-225` |

### 2. Ruled

**Chosen: Option C — partial split, evidenced by what the census already shows.** Categories
the census shows have *already* organically split into more than one home
(closure / audit record: three; register + findings: two) keep that reality recognised
rather than reversed. Categories the census shows have stayed uniformly in `docs/plans/`
across every measurement taken (rulings records, ledgers — zero drift, zero organic move)
keep the grammar-in-place answer. **Rejected: Option A — grammar-in-place, applied
uniformly.** **Rejected: Option B — split directories, applied uniformly.**

Option A, applied without exception, is not actually available: it would require either
mischaracterising closure/audit records as one home when the census shows three, or actively
*consolidating* three pre-existing homes into one — a bulk-move exercise with real C1
exposure (RFC-897 C1: no retro-rename of a cited artifact) that nothing in the evidence
motivates. RFC-897 §10's own reasoning against splitting — "no reader gain" — is sound for
rulings and ledgers, where the census shows zero organic tendency to split and no gap a
reader has been observed to hit. It does not extend to closure records, where the split
already exists and already serves a distinction the draft's §1.5 states plainly: one
directory is per-item and structurally uniform, one is a single running document, and one
predates the other two mechanisms entirely. Option B, applied without exception, would
impose the same C1-costly move in the other direction — forcing rulings and ledgers into new
subdirectories the evidence gives no reason to create, since neither category has shown any
organic tendency to leave `docs/plans/` across three separate measurements spanning the
whole investigation.

### 3. What it obliges

Whichever future slice implements Stage 2's reference-coding standard treats
"one home per category" as: rulings records and ledgers keep their current single home
(`docs/plans/`), distinguished by filename grammar; closure/audit records keep their current
three homes, each documented rather than merged or split further; register and findings keep
their current two homes. No slice is obliged to move a rulings record or a ledger out of
`docs/plans/`, and no slice is obliged to consolidate the three closure-record homes into
one.

**Overridden if** a future slice finds a reader-facing cost from the current arrangement
this record's evidence did not surface, or if a category not checked here (contract,
process/charter/skill) is found to need a different answer when Stage 2 reaches it — this
ruling covers the four categories the census evidence above actually speaks to.

---
