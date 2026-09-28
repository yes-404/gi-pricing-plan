---
id: FD-9020
family: finding
title: Check 32 reads two disclosed specimen rows in open-questions.md as failures as soon as the file cites an unresolved id
status: active
created: 2026-09-28
owner: auditor
tree: 9fa2b833e00281a36109183a12efc9d7152225e9
corrected_by: []
relates: [WK-1178]
---

# FD-9020 — Check 32 reads two disclosed specimen rows in open-questions.md as failures as soon as the file cites an unresolved id

**Severity: low.** The auditor filed this finding on 2026-09-28, on the lead's instruction. It comes
from executor-s2's T4b report, relayed in the lead's `to-deputy.md` entry of 21:42:18 BST
("Candidate finding (for auditor-b's next records PR)"), and the auditor reproduced it. It is low
because a workaround exists (S3 respelled the row) and no check passes wrongly. It misleads a
reader, because the DISCLOSED count moves for a reason that has nothing to do with the change.

## Finding

At `origin/main`, two rows of `python3 scripts/audit-docs.py` sit in the DISCLOSED set. They are
check 32's readings of `docs/open-questions.md:47`, OQ-555's own text, which spells a padded plan id
as a specimen. When the same file gains any other reference to an id that does
not resolve in `docs/INDEX.md` (for example an open question that cites a working id), those two
rows become **FAILED** and the DISCLOSED count falls by two. So an unrelated edit to the file
turns two standing, disclosed rows into two failures the author did not cause.

## Evidence

Reproduced on detached copies of `origin/main` `9fa2b833`, at `nice -n 10`, each edit committed
locally and never pushed. The command was `python3 scripts/audit-docs.py` in every case:

| Edit to `docs/open-questions.md` | rc | DISCLOSED | FAILED rows |
|---|---|---|---|
| none (base) | 0 | 851 | none |
| a blank line appended | 0 | 851 | none |
| an HTML comment appended | 0 | 851 | none |
| a comment inserted above line 47 (the rows move to line 48) | 0 | 851 | none |
| OQ-555's row text edited, `docs/INDEX.md` regenerated | 0 | 851 | none |
| **a row citing an open-question id in the working range, which `docs/INDEX.md` does not carry** | **1** | **849** | check 4 (the OQ is raised in no spec), check 32 at `:188` (the id "does not resolve in docs/INDEX.md"), check 39 (INDEX stale), and **two** check-32 rows at `:47` ("short-padded id … outside a link target") |

The two `:47` rows are the two that fall out of DISCLOSED. The check 4, check 32 (`:188`) and
check 39 rows are the expected ones for an unresolved id.

**The same happened in S3's tree.** At `98424cc5^` (the parent of S3's respelling commit) the same
audit prints `DISCLOSED (849…)`, `FAILED (23)`, and lists the two `open-questions.md:47` rows next
to `open-questions.md:131` (a working-range open-question id that does not resolve). At `98424cc5` (the respelling) it prints
`FAILED (21)`, so the respelling removed exactly those two rows. Commit `98424cc5`'s own message
reads *"Editing docs/open-questions.md ([its three working-range open-question rows]) made check 32 read line 47's two [padded plan-id] specimen spellings as violations."* Bracketed: the commit names three working ids and one padded id form; they resolve to nothing, so this record does not repeat them, and the brackets mark the substitution.

**Not explained:** why the specimen rows leave DISCLOSED when another unresolved id appears. The
`_docverify` docstrings say a token that resolves to nothing is *"a specimen of the form, not a
citation"* (`scripts/_docverify.py:1944`), and the `row_e` guard refuses to excuse every token when
`docs/INDEX.md` resolves no id (`:2024`). Neither states the interaction seen here, and this record
did not trace `audit-docs.py`'s DISCLOSED accounting. The table above is the observation.

## Disposition

**Deferred with an owner — WK-1178**, docs hygiene, with the lead acting on it. Event: `audit-docs.py`
classifies OQ-555's specimen rows the same whether or not the file cites another unresolved id, or
OQ-555's specimen is rewritten as a phrase on `main` (S3's `98424cc5` does the latter on its branch,
and that change lands with S3). Until then a PR that adds an open question with a working id to
`open-questions.md` sees the DISCLOSED count fall by two, and its author should read that as this
finding and not as a regression.
