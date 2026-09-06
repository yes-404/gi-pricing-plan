---
id: RL-943
family: ruling
title: Q3: verdict-4 status is derived from an existing closure record wherever one covers the file; declared only for the residual
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

## RL-943 — Q3: verdict-4 status is derived from an existing closure record wherever one covers the file; declared only for the residual

### 1. Verified first, independently, at `052afe3` and `4f95fb3`

**This ruling is the one in this record whose weight rests on a `referenced_by`-derived
figure — stated at both trees per the preamble's disclosure.**

| Claim | Verdict |
|---|---|
| At `4f95fb3` (the draft's own tree), 39 `docs/plans/` files carry no genuine reference after the census-of-a-census correction, and 36 of the 39 are shown, by manually reading each file against `docs/closures/INDEX.md#closure-recordsmd` and `docs/roadmap.md`, to be fully covered by an existing closure narrative's discussion of the same requirement/slice/Work id | **Confirmed by reading the draft's §4 table in full**, all 39 rows, not sampled — spot-checked independently below rather than accepted on the draft's word |
| At `052afe3`, this record's own tree, the corrected zero-`referenced_by` population is 40 — the same 39 files by path, plus one new file (RL-951's own record, filed after the draft) that is unreferenced for the same "too new" reason the draft's own #38/#39 rows state, not for lack of eventual coverage | **Confirmed, independently regenerated** — see this record's preamble; the population grows by exactly the files that landed between the two trees, with no other change |
| Three spot-checked verdict-4 rows resolve against `docs/closures/INDEX.md#closure-recordsmd` exactly as the draft states: `W6b-10 browser auth` (#28), `W6b-15 _minor rename` (#30), and `FR-199` (#5) | **Confirmed** — `grep -n "W6b-10 browser auth\|FR-199\|W6b-15" docs/closures/INDEX.md#closure-recordsmd` returns the exact citing lines the draft's table quotes, at `052afe3` |
| §0.2's methodology point — a closure record cites the requirement/slice/Work id or PR number, never the plan's own filename, so `referenced_by`'s basename-substring rule structurally cannot see this relationship | **Confirmed by the same spot-check** — none of the three matched lines contains the plan's own filename; each cites only the id, slug, or PR number |
| The 3 verdict-2 files (#13, #36, #38 in the draft's numbering) are each flagged on a stated gap in the file's own text (an unresolved forward reference, an unowned follow-up, or genuine newness), not asserted from silence | **Confirmed by reading rows 13, 36 and 38 in full** — each carries the specific textual evidence the draft's "Reason" column states |

### 2. Ruled

**Chosen: Option C — derived from the existing closure record, as the primary mechanism,
for the population it actually covers.** Where a `docs/plans/` file names a requirement id,
slice id, Work id or PR number that an existing closure record (`docs/closures/INDEX.md#closure-recordsmd`,
a `docs/audit/work/<id>/README.md`, or a Ruling's own text amending a prior Ruling) already
discusses, verdict-4 status is *read off* that closure record rather than declared a second
time on the file. **Rejected, as a universal mechanism: Option A — a separate index
marker**, and **Option B — a category attribute on the file itself.** Neither is rejected
outright — see below — but neither is adopted as the default.

92% of the population this ruling governs (36 of 39 at the draft's tree; the same 36 of 40
at this record's tree, since the one added file is verdict-2-shaped by the same "too new"
reasoning, not verdict-4) already carries the information a verdict-4 declaration would
restate. Declaring it a second time — on an index, or on the file's own header — creates
exactly the failure this repository has already named and fixed four separate times:
`CLAUDE.md` §0's own rule ("counts and status that change are not written in this file")
and its citation, `.claude/rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md`, record four prior
incidents of a second copy of a status going stale independently of the record that is
actually authoritative. RL-945 above (Q4, this same investigation) already applied this
exact reasoning to the ownership matrix, for the same reason: a second place recording a
status that another document already carries authoritatively is the shape that goes stale,
not a convenience. A verdict-4 declaration duplicating a closure record's own coverage is
the identical shape at file scope rather than document scope.

This is not adopted without qualification, and the draft's own text is right to flag the
residual: the 3 verdict-2 files, and any future file with no closure record covering it,
have nothing to derive the verdict *from* — Option C is silent about them by construction,
since there is no source document to read the status off of. For that residual population,
an explicit declaration is still required, under either Option A or Option B. This record
does not choose between A and B for the residual: which is lighter to build and maintain is
an implementation question for whichever future slice actually files Stage 4's verdict
declarations (unscoped by this plan, per the Constraints below), not a property the four
gate questions require this record to fix in advance.

### 3. What it obliges

Whichever future slice implements Stage 4's verdict-declaration mechanism (unscoped by this
plan) checks, for each `docs/plans/` file with no genuine `referenced_by` hit, whether a
closure record already covers its id before creating any new declaration for it. Only the
residual — files with no covering closure record — gets an explicit declaration, in a form
that slice chooses between Option A and Option B.

**Overridden if** a future slice finds the 92% figure does not generalise as new files enter
the unreferenced population, or if a closure record's own citation practice changes such that
`§0.2`'s id-not-filename pattern no longer holds.

---
