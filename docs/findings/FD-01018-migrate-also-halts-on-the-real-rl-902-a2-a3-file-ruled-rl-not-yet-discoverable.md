---
id: FD-1018
family: finding
title: `migrate()` also halts on the real RL-902/A2/A3 file: ruled `RL-`, not yet discoverable
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F81.md
---

# F81 — `migrate()` also halts on the real RL-902/A2/A3 file: ruled `RL-`, not yet discoverable

Evidence essay for the register row self-named `(F81)` in `docs/findings/register.md`. Same
class as F80 (a ruling has decided a document's family; discovery code that would emit
that family's draft has not been written yet), found the same way — running the code
against the real tree rather than reading a PR body's account of it — and filed separately
because the defect, the file and the remedy are distinct from F80's.

## The defect, verified directly at `3f41d60`

Rulings 86/87 (`docs/rulings/INDEX.md#2026-09-02-w37-ruling-a-series-and-standalone-ruling-filesmd`,
PR #598) rule that the three headings `### RL-902`, `### RL-903`, `### RL-904` in
`docs/plans/INDEX.md#2026-08-30-nt-0012-0013-0014-adoptionmd` become three standalone `RL-`
records. No discovery code yet turns them into `RL-` drafts, and `_discover_multi_ruling_
files` still treats the file as one multi-ruling plan whose sub-headings are un-splittable
letter-suffixed units. Running the guard `d7c9b08` built for exactly this class of gap
(row 31) against the real tree:

```
_check_multi_ruling_files_not_silently_unrecognised(ROOT)
→ NotImplementedError: migrate: docs/plans/INDEX.md#2026-08-30-nt-0012-0013-0014-adoptionmd
  (multi-ruling headings) -- 3 unit(s) an independent census found are neither a
  produced record, a derived body line, nor a declared exception (RL-985):
    docs/rulings/RL-00902-rfc-842-s-credential-lifetime-rule-lands-in-claude-skills-secret-hygiene.md:16: ### RL-902 -- ...
    docs/rulings/RL-00903-rfc-842-s-search-by-shape-rule-lands-in-claude-skills-close-workstream.md:16: ### RL-903 -- ...
    docs/rulings/RL-00904-rfc-843-s-remove-the-relay-lands-in-delivery-process-md-15.md:16: ### RL-904 -- ...
```

The call is unconditional inside `migrate()` (`scripts/doc-id.py:2984`, immediately after
`_discover_multi_ruling_files` runs), earlier in the pipeline than F80's plan-reviews call
— a real run would halt here first, before ever reaching the Pending-proposals gap.

Not a false positive from testing the guard out of context: `_discover_multi_ruling_files`
and this guard were confirmed to correctly exempt every genuine single-ruling h1 file on
the real tree (three, not four — an earlier pass of this audit mis-flagged
`2026-09-02-w37-ruling-88-acceptance-amendment.md` as a fourth because its own h1 title
happens to start with the words "RL-979's", which is a description of the ruling it
amends, not a new standalone `# Ruling <n>` heading in the canonical form; corrected here
after re-running `_discover_multi_ruling_files(ROOT)` and reading its own file list).

## Scope of this finding

- **Not fix-before-close for W37-5b.** Row 6's discharge criterion was the derivation and
  the ruling (Rulings 86/87), not the discovery code — the obligations list's own text says
  "OWED BY THE PLANNER, then the decision-maker", never "and coded here." Both landed.
- **It blocks W37-6's go-ahead as things stand, the same way F80 does**, and earlier in the
  pipeline. Acceptance item 13's reasoning for W37-5b's own existence applies here too,
  discovered the same way F80 was: by running the code, not by reading a report about it.
- **Proposed disposition** (a proposal; the verdict is the lead's): **not started** —
  discovery code that splits the three letter-suffixed sub-headings into three `RL-`
  drafts, symmetric to `_discover_multi_ruling_files`'s existing digit-suffixed splitting.
  Owner not named here, for the same reason as F80: W37-6's executor or a narrow follow-up
  slice are both live options.
- **Falsifiable**: discharged when the discovery code lands and
  `_check_multi_ruling_files_not_silently_unrecognised(ROOT)` returns cleanly against the
  real tree, or by a corrected reading showing another call path resolves these headings
  first.

## Amendment, 2026-09-02 — the guard is fixture-tested only, and one commit body understates it

Two adjacent facts, surfaced by a read-only census sweep after this finding was filed and
verified independently by the lead at `b7abf3b` before being recorded here. Neither changes
the finding's disposition; both change what a reader should assume about it.

**The guard has no test against the real file.** Every test of
`_check_multi_ruling_files_not_silently_unrecognised` builds its input under `tmp_path`
(`tests/test_doc_id_migrate.py:1645`, `:1662`, `:1686`). `_A_SERIES_SOURCE` — the constant
naming the real `docs/plans/INDEX.md#2026-08-30-nt-0012-0013-0014-adoptionmd` — is used only by the
`_ruling_file_owner` and discovery tests (`:1309`, `:1330`), never by a test of this guard.
So the guard's behaviour on the corpus it will actually abort against is **proven by
execution and not pinned by a regression test**: running it directly against the tree today
raises `NotImplementedError` naming **3** units, which is the behaviour this finding
describes, but nothing in the suite would notice if that stopped being true.

The distinction is worth keeping sharp, because a looser version of this claim — *"no test
covers A3 or the real file"* — is **false**: `:1298` runs `_ruling_file_owner` directly
against the real A1–A3 source. It is this guard specifically that is fixture-only.

**`d7c9b08`'s commit body understates its own guard by one unit.** It says the guard *"names
A1 and A2 as unaccounted"*. Run live it names **three** — A1, A2 and A3, at
`docs/plans/INDEX.md#2026-08-30-nt-0012-0013-0014-adoptionmd`, `:81` and `:96`. That file is
unchanged since `97965be`, so the guard named three at `d7c9b08` too; the body was wrong when
written, not overtaken. The fixtures use A1/A2 only, which is the likely source of the
miscount — the body describes the fixture's output rather than the real file's.

This is the **second** commit body in W37-5b to misdescribe what it landed, after `614c92c`
(recorded in this slice's closure record §3). A squash body cannot be amended, so both
corrections live in amendable documents that cite the hash — and two instances in one slice
is a pattern worth naming rather than two coincidences: **a body written from the fixture
run, or from a branch state the executor had already moved past, reads as a report of the
delivered code and is not checked against it.**

**Not a new finding and not a change of disposition.** The disposition above stands
unchanged: not started, owner unnamed. What is added is that whoever takes it should land a
test binding the guard to the real file at the same time, so the discharge condition above
becomes checkable by the suite rather than only by hand.
