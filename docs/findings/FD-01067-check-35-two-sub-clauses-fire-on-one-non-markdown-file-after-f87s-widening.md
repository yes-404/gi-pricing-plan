---
id: FD-1067
family: finding
title: check 35's two sub-clauses both fire on one non-markdown file after F87's widening
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-18
owner: lead
tree: 4d9fe1d62328285ac0483b047c3959e39e0f5bd6
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
---

# FD-1067 — Check 35's two sub-clauses fire on one non-markdown file after F87's widening

## Finding

`docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md:1168-1170` (finding 8, quoted):
"Check 35's second clause is inert corpus-wide. Zero `Permitted owners:` lines exist
anywhere." That was true before F87's widening landed. After it (this checkpoint,
`docs/findings/register.md`'s F87 row), it is no longer true: check 35's owner clause and its
second (`Permitted owners:`) clause both now fire on one real non-markdown file — an
output-shape question about what a non-markdown owner-clause reader should do, not previously
exercised because the population was empty until F87's widening reached it.

## Evidence

`CR-1063` §4 (`docs/closures/CR-01063-w37-6-run-2-the-closure-g-record.md`), the squash
commit's own "Disclosed to W37-11" section, quoted in full: *"check 35: two sub-clauses both
fire on one non-markdown file after F87's widening — output-shape question, owner lead."* Live
`audit-docs.py` check 35 output at `4d9fe1d`: "395 owner(s) checked in scope; 50 owner
check(s) deferred (owner: W37-10, RL-1046 §B — F92's stamp-deferred population); 66
exemption(s) reconciled against 568 file(s) in RFC-937's stamp set; 93 unstamped file(s) in
the enforced checks-30-39 scope." The `W37-10` owner-tag literal named in that deferral is
itself a stamp-deferral population label, not a fourth owner of this or F92's row — the leaf
plan that owns aligning that label to a real owner is **W37-7's**, which owns the code path
(the lead's correction to this finding, checkpoint 3).

## Disposition

**Carry forward with an owner (lead), decaying to W37-11.** An output-shape question, not a
correctness defect: what a reader of check 35's second clause should do when it fires on a
non-markdown file is not yet specified. Not filed as a register row before this checkpoint;
filed here so it is not lost between `CR-1063`'s disclosure prose and the next place a
planner would look.
