---
id: RL-941
family: ruling
title: Q1: the category set is ruled **amended**, not drafted-as-is and not rebuilt
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

# RFC-897's Q1, Q2, Q3 and Q7's general half, ruled (2026-09-01)

**What this is.** The decision gate
[`../plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md`](../plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md) §4 places after
Slice 3 (PR #545, merged as `9e70469`), against
[`../research/RS-00953-file-taxonomy-draft-rfc-897-stage-1.md`](../research/RS-00953-file-taxonomy-draft-rfc-897-stage-1.md). That plan's §2 found
four of RFC-897's seven questions not rulable at `b551060` because they presuppose a closed
category set the census had not yet produced: Q1, Q2, Q3 and Q7's general half. Slice 3's
draft now exists and states each as a choice between named options, deliberately with no
recommendation. This record rules all four. Q4, Q5, Q6 and Q7's notes half are already ruled
(Rulings 55–58, `2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`) and are not reopened.

**Numbering continues at 62.** Verified rather than relayed: `git grep -n "^# Ruling \|^##
Ruling " docs/plans/` at this session's tree (`052afe3`, `origin/main`, fetched immediately
before this record was written) yields a maximum of 61, in
[`RL-00951-rl-947-s-tombstone-gains-per-file-stubs-watched-by-a-new-check-not-left.md`](RL-00951-rl-947-s-tombstone-gains-per-file-stubs-watched-by-a-new-check-not-left.md).

**Evidence tree.** The draft states its own tree as `4f95fb3` and its corpus as `git
ls-files`, 1328 tracked files. This record's own checks were run at `052afe3` — two commits
later, both additive: the draft's own file (`9e70469`) and RL-951 (`052afe3`), each one
new file under `docs/`, bringing the corpus to 1330. Every figure below states which tree it
was read at; where a figure could have moved, it was re-measured rather than assumed. No
finding below depends on the two-commit drift changing in substance — see each ruling's §1.

**On `referenced_by` and the census-of-a-census correction (draft §0.1).** Independently
reproduced at `052afe3`, not merely re-read: regenerating `scripts/file-census.py` fresh and
checking `docs/plans/`'s 125 files at this tree, the script's own `referenced_by` column
reports exactly **one** file with a raw count of zero
(`2026-09-01-ruling-61-notes-tombstone-stubs-watched.md` — genuinely too new to be cited by
anything, including the committed census, which does not enumerate the future). Recomputing
by hand with the two census-artifact files excluded as spurious referrers — the correction
the draft's §0.1 describes — raises the zero-count set to **40**: the same 39 files the
draft's §4 names at `4f95fb3`, plus this one additional, genuinely-new file. The two
independent counts (draft's 39 at `4f95fb3`; this record's 40 at `052afe3`) agree exactly on
every file they share, which is the check that says the correction reproduces rather than
drifts. **RL-943 (Q3) is the only ruling below whose evidentiary weight depends on a
`referenced_by`-derived figure** — the corrected 39/40-file population — and it says so
there, with both trees named.

## Acceptance Standard

1. `git grep -c "^## RL-872[2-5] —" docs/rulings/INDEX.md#2026-09-01-nt-0016-q1-q2-q3-q7-general-rulingsmd`
   returns `4`, and `git grep -n "^## Ruling " docs/plans/` shows 62–65 filling the gap
   immediately after RL-951 with no duplicate and no skip.
2. Each of the four `### 2. Ruled` subsections names both the chosen option and every
   rejected option in its opening sentence, with the evidence that separated them.
3. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
4. `git grep -nE '\bFR-[A-Z]+-[0-9]|\bNFR-[A-Z]+-[0-9]|\bOQ-[A-Z]+-[0-9]|\bADR-[0-9]'
   docs/rulings/INDEX.md#2026-09-01-nt-0016-q1-q2-q3-q7-general-rulingsmd` returns no matches — no
   requirement or ADR identifier is minted, per RFC-897 C2.
5. `git diff --stat <merge-base>..<branch> -- docs/` names exactly this one new file — no
   frozen plan is edited, and neither `2026-08-31-nt-0016-investigation.md`,
   `2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md` nor
   `../research/RS-00953-file-taxonomy-draft-rfc-897-stage-1.md` is touched.
6. RL-943 (Q3) names both trees (`4f95fb3` and `052afe3`) for its `referenced_by`-derived
   figures, per `CLAUDE.md` §13's tree-carrying rule.

---

## RL-941 — Q1: the category set is ruled **amended**, not drafted-as-is and not rebuilt

### 1. Verified first, independently, at `052afe3`

| Claim | Verdict |
|---|---|
| The draft's §1 confirms all twelve of RFC-897 §3's hypothesised categories exist as real, coherent, non-empty clusters | **Confirmed by reading §1.1–1.12 in full** — every one of the twelve rows has a named home, a measured file count, and (where relevant) an id family; none reads as empty or as a cluster the census failed to find |
| Closure/audit records occupy three homes, not the two RFC-897 §3 states | **Confirmed, independently counted** — `docs/audit/work/` holds 15 `README.md` closure files (one fewer than the draft's 16 at `4f95fb3`; ordinary drift, not disputed), `docs/closures/INDEX.md#closure-recordsmd` is one 4782-line file (byte-identical line count to the draft's own citation), and `ls docs/plans/ \| grep -i closure` returns exactly three non-ledger matches: `2026-08-22-w5-closure.md`, `2026-08-23-w32-closure-proposal.md`, `2026-08-27-closure-audit-standard.md` |
| "plan (map / leaf)" has two live filename grammars for its map sub-kind | **Confirmed** — `slice-map` (4 files: `w6b-slice-map.md` and three `-revised-N` siblings) and `map-plan` (1 file: `2026-08-31-w12-map-plan.md`), no shared `name_pattern` |
| "rulings record" has two live filename grammars | **Confirmed, and grown since the draft** — 23 files match a suffix form (`-ruling.md`/`-rulings.md`/`-rulings-`); 2 files now match a prefix form (`ruling-NN-slug.md`: RL-950 and, landed since the draft, RL-951 itself) |
| Neither grammar split corresponds to a category the twelve-row hypothesis is missing, or to a hypothesised category that turns out not to exist | **Confirmed by re-reading §1.2 and §1.3 in full** — in both cases the draft's own text states the underlying object is the same one category ("Both name the same underlying object," §1.2; "every file in the 24 is the same object," §1.3's rejected-reading paragraph). Neither section proposes splitting the category, adding a new one, or retiring one |
| No section of the draft (§1, §2, or §3) identifies a category present in the census but absent from the twelve-row hypothesis, or a hypothesised category the census shows does not correspond to real files | **Confirmed by reading §1 through §3 end to end** — §3's "categories no charter creates" (ledger, research note, workflow journey, note, role charter) is an ownership-coverage finding against the same twelve categories, not a claim that any of them is miscategorised or spurious |

### 2. Ruled

**Chosen: Option B — amended.** Keep RFC-897 §3's twelve rows as the base, and apply the
draft's three §2 findings directly: closure/audit record gets a corrected third home; the
map/leaf and rulings-record naming splits are carried forward as Stage 2 grammar items, not
as new or split categories. **Rejected: Option A — drafted as written**, because the closure
third-home finding is a verified factual gap in §3's own table, not a drafting nicety, and
leaving it unamended would carry a known-wrong row forward. **Rejected: Option C — rebuilt
from the census.**

**The draft's own argument for Option C is examined and not adopted.** §5's Q1 section
states that the two independently-found filename-grammar splits (map/leaf, rulings record)
are "the sharpest evidence for this option specifically," on the reasoning that two
instances of the same defect shape are stronger evidence than one. Two instances of the same
shape are indeed stronger evidence *of that shape* — the finding itself is real and is
adopted below. But the question is not whether the finding is real; it is what it is
evidence *for*. In both cases the draft's own text records that the category itself was
correctly identified — one purpose, one home, one governing charter clause — and that only
the *filename spelling underneath* the category disagrees with itself. That is a defect in
the reference-coding grammar a category uses, which RFC-897 §1 (Design constraints) and §4
(Stage 2 — Reference coding standard) already scope as separate, later work; it is not
evidence that the categories a Stage 1 taxonomy exercise is meant to produce are the wrong
ones, missing one, or contain one that should not exist. A defect one level below the
category boundary does not impeach the boundary. Discarding a twelve-row structure that the
census independently confirms in full, in favour of building a fresh set from scratch, is a
much larger and riskier action than the finding that would motivate it — it is the remedy
for "the categories are wrong," applied to a finding that says "two categories are spelled
two ways." The draft's own §5 Option B text already states the correct-sized remedy for this
specific finding: carry the grammar items forward to Stage 2. This ruling adopts that
remedy under the amended option and declines to extend it into a justification for
rebuilding the set the finding does not touch.

The one finding in §2 that *is* a genuine correction to §3's stated content — the
closure/audit record's third home — is exactly what "amended" is for: the category survives
unchanged, one factual detail about it is corrected. Nothing else in §1, §2 or §3 rises to
that bar; §1.6's register/findings home-split detail and §1.10's process/charter/skill
sub-kind split are both recorded by the draft itself as informative for other questions (Q2
and the charter-ownership findings in §3, respectively), not as corrections to §3's table
that Q1 must carry.

### 3. What it obliges

The taxonomy, once written up by whichever future slice does so (Stage 1's deliverable,
unscoped by this plan), states twelve categories matching RFC-897 §3's names, with
"closure / audit record" documenting three homes rather than two. The map/leaf and
rulings-record filename-grammar inconsistencies are handed to Stage 2 (reference coding
standard) as named items to resolve, not treated as a taxonomy defect requiring a rebuild.

**Overridden if** a future slice's own read of the census surfaces a category the twelve
rows do not name, or shows one of the twelve does not correspond to a real, coherent
cluster of files — neither of which this record found in the draft's evidence.

---
