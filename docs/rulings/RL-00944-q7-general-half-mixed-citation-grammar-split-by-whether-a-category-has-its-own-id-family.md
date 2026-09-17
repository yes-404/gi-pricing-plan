---
id: RL-944
family: ruling
title: Q7, general half: mixed citation grammar, split by whether a category has its own id family
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

## RL-944 — Q7, general half: mixed citation grammar, split by whether a category has its own id family

### 1. Verified first, independently, at `052afe3`

| Claim | Verdict |
|---|---|
| Categories with an existing, independent id family: spec (`FR-`/`NFR-`/`OQ-`), ADR (`ADR-NNNN`), note (`NT-00NN`, already ruled — RL-948), register + findings (`F`-number), workflow journey (`wf-NN`) | **Confirmed** — five of the twelve categories from RL-941's table carry a minted id family, per the draft's §1.1, 1.8, 1.6, 1.11, 1.12 |
| Categories with no id family of their own: plan (map/leaf), rulings record, ledger, closure/audit record, contract (identified by artifact slug, not a numeric id), process/charter/skill (none of the three sub-kinds mints an id) | **Confirmed** — six categories, per §1.2–1.5, 1.9, 1.10 |
| RFC-897 C2 forbids minting a new id family | **Confirmed, re-read** — `.claude/rfcs/0016-…md` §1, restated in the investigation plan's Global Constraints and this session's own dispatch constraints |
| Option A (id-only, universally) would require minting a new id family for at least four of the six id-less categories to be citable by id at all | **Confirmed by construction** — a plan, a rulings record, a ledger and a closure/audit record are today identified only by dated filename (RL-941 §1, RL-942 §1); an id-only citation rule for them has no id to cite unless one is minted |
| The draft's own §4 finding — 36 of 39 (40 of 41 at this record's tree, RL-943 §1) "unreferenced" plans are in fact covered, but by a requirement, slice, Work or Ruling number rather than a path | **Confirmed, RL-943 §1** — re-verified independently there, not merely re-read |
| `docs/findings/register.md`'s own citation practice already cites `NT-00NN` ids 8 times without an accompanying path | **Confirmed** — matches RL-948 §1's own independently-verified figure, re-checked: `git grep -c "NT-00[0-9][0-9]" docs/findings/register.md` returns 8 |
| RL-948 already rules the notes family — one of the five id-bearing categories — to cite by id, not path | **Confirmed**, `2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md:226-260`, not reopened here |

### 2. Ruled

**Chosen: Option C — mixed, split by whether the category has an independent id family.**
**Rejected: Option A — id-only, universally.** **Rejected: Option B — path-only, as the
status quo.**

Option A is disqualified mechanically, the same shape RL-947 used to disqualify a
symlink for Q6: it is not merely undesirable, it cannot be executed as stated without
violating RFC-897 C2 and this session's own constraint against minting an id. Six of the
twelve categories have no id to cite. Option B is not actually the status quo it names
itself: id-based citation already dominates working practice for every category that has an
id to cite — the register's own 8 unaccompanied `NT-00NN` citations, the universal practice
of citing a spec requirement by `FR-`/`NFR-`/`OQ-` id rather than `docs/specs/NN-module.md`,
and RL-948's own ruling for notes are all standing, working precedent, not a proposal.
Declaring "path-only" the rule would reverse practice that is already succeeding for five of
the twelve categories, on no evidence that it is failing.

Option C is what the evidence independently converges on from two directions at once: RFC-897
C2 forces it from above (no new id may be minted, so an id-less category cannot be cited by
id without first creating one — out of scope here), and the draft's own §4/RL-943 finding
confirms it from below (citation practice for the id-bearing categories already runs almost
entirely by id, id-less categories are cited by dated filename because that is the only
handle they have). This ruling states as a rule what RL-948 already established for one
category and the register's own practice already demonstrates for others: it is not a new
policy invented here so much as a generalisation, named once, of behaviour already present
and not previously written down as a rule.

### 2a. Where this ruling narrows itself, matching RL-948's own precedent

As RL-948 states for the notes family specifically: this governs **new and living**
citations going forward, not a retrofit of the frozen corpus. No frozen `docs/plans/` file
is edited to convert a path citation to an id citation, or the reverse, by this ruling.

### 3. What it obliges

Whichever future slice implements Stage 2's reference-coding standard states the citation
grammar per category as: spec, ADR, note, register/findings and workflow journey cite by
their existing id; plan, rulings record, ledger, closure/audit record, contract and
process/charter/skill cite by dated filename or path, since none has an id to cite and
minting one is out of scope for this investigation. A future ruling that assigns an id
family to one of the six id-less categories would move that category from the second list
to the first — this ruling does not itself do so.

**Overridden if** a future ruling mints an id family for one of the six id-less categories
(which would require its own decision point, since RFC-897 C2 forbids doing so here), or if
citation practice for an id-bearing category is found, on fresh evidence, to run
predominantly by path rather than id.

---

## What this record's ruling now permits

**§4a item 7 of the investigation plan is discharged: all four questions it names — Q1, Q2,
Q3 and Q7's general half — are ruled above, not carried forward.** Combined with Rulings
55–58, all seven of RFC-897 §10's open questions are now ruled.

Per the investigation plan §4's own words, this ruling **is** the trigger the plan names for
RFC-897's Stages 2–5, which that plan "deliberately" leaves unscoped. What it now permits,
stated without scoping it: a future plan may cut Stages 2 (reference coding standard), 3
(ownership map), 4 (workflow-loop audit / verdict decomposition) and 5 (migration and
enforcement) into slices, using the twelve-category set as amended by RL-941, the
per-category home rule from RL-942, the verdict-4 mechanism from RL-943, and the
citation grammar from RL-944 (together with Rulings 55–58) as fixed inputs it does not
need to re-derive. Sizing, sequencing and slicing those four stages is that future plan's
work, not this record's — the maintainer has said they intend to read the draft and direct
next steps themselves, and nothing above pre-empts that.

## What this record found, beyond what was asked

- **The draft's §5 Q1 write-up over-reaches on its own strongest evidence.** The two
  independently-found filename-grammar splits are real and are adopted (RL-941), but they
  support the amended option, not — as the draft's own text argues — the rebuild option. See
  RL-941 §2 for the reasoning; this is a rejection of the draft's own stated argument, not
  merely of the option it argues for.
- **RFC-897 §3's "known tension" undercounts by one home, confirmed independently** at both
  the draft's tree and this record's own — RL-941 §1.
- **The census-of-a-census correction (draft §0.1) reproduces cleanly one commit-pair later**,
  gaining exactly one new file (RL-951's own record) for exactly the reason the draft's
  own methodology predicts (too new to be cited yet) — stated in this record's preamble and
  relied on directly by RL-943.
- **Nothing else in the draft's evidentiary claims failed independent re-verification.** No
  correction is filed against the draft itself; §6 of the draft ("rules none of §5's four
  questions... mints no id... edits no frozen file") is confirmed true by this record's own
  read.

## Constraints observed

Mints no `FR-`, `NFR-`, `OQ-` or `ADR-` id (RFC-897 C2). Edits no file under `docs/plans/`
other than this new record. Does not scope Stages 2–5. Not merged by this role — opened as a
PR and reported by number, per `.claude/roles/decision-maker.md`.
