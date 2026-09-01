# NT-0016's Q1, Q2, Q3 and Q7's general half, ruled (2026-09-01)

**What this is.** The decision gate
[`2026-08-31-nt-0016-investigation.md`](2026-08-31-nt-0016-investigation.md) §4 places after
Slice 3 (PR #545, merged as `9e70469`), against
[`../audit/file-taxonomy-draft.md`](../audit/file-taxonomy-draft.md). That plan's §2 found
four of NT-0016's seven questions not rulable at `b551060` because they presuppose a closed
category set the census had not yet produced: Q1, Q2, Q3 and Q7's general half. Slice 3's
draft now exists and states each as a choice between named options, deliberately with no
recommendation. This record rules all four. Q4, Q5, Q6 and Q7's notes half are already ruled
(Rulings 55–58, `2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`) and are not reopened.

**Numbering continues at 62.** Verified rather than relayed: `git grep -n "^# Ruling \|^##
Ruling " docs/plans/` at this session's tree (`052afe3`, `origin/main`, fetched immediately
before this record was written) yields a maximum of 61, in
[`2026-09-01-ruling-61-notes-tombstone-stubs-watched.md`](2026-09-01-ruling-61-notes-tombstone-stubs-watched.md).

**Evidence tree.** The draft states its own tree as `4f95fb3` and its corpus as `git
ls-files`, 1328 tracked files. This record's own checks were run at `052afe3` — two commits
later, both additive: the draft's own file (`9e70469`) and Ruling 61 (`052afe3`), each one
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
drifts. **Ruling 64 (Q3) is the only ruling below whose evidentiary weight depends on a
`referenced_by`-derived figure** — the corrected 39/40-file population — and it says so
there, with both trees named.

## Acceptance Standard

1. `git grep -c "^## Ruling 6[2-5] —" docs/plans/2026-09-01-nt-0016-q1-q2-q3-q7-general-rulings.md`
   returns `4`, and `git grep -n "^## Ruling " docs/plans/` shows 62–65 filling the gap
   immediately after Ruling 61 with no duplicate and no skip.
2. Each of the four `### 2. Ruled` subsections names both the chosen option and every
   rejected option in its opening sentence, with the evidence that separated them.
3. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
4. `git grep -nE '\bFR-[A-Z]+-[0-9]|\bNFR-[A-Z]+-[0-9]|\bOQ-[A-Z]+-[0-9]|\bADR-[0-9]'
   docs/plans/2026-09-01-nt-0016-q1-q2-q3-q7-general-rulings.md` returns no matches — no
   requirement or ADR identifier is minted, per NT-0016 C2.
5. `git diff --stat <merge-base>..<branch> -- docs/` names exactly this one new file — no
   frozen plan is edited, and neither `2026-08-31-nt-0016-investigation.md`,
   `2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md` nor
   `../audit/file-taxonomy-draft.md` is touched.
6. Ruling 64 (Q3) names both trees (`4f95fb3` and `052afe3`) for its `referenced_by`-derived
   figures, per `CLAUDE.md` §13's tree-carrying rule.

---

## Ruling 62 — Q1: the category set is ruled **amended**, not drafted-as-is and not rebuilt

### 1. Verified first, independently, at `052afe3`

| Claim | Verdict |
|---|---|
| The draft's §1 confirms all twelve of NT-0016 §3's hypothesised categories exist as real, coherent, non-empty clusters | **Confirmed by reading §1.1–1.12 in full** — every one of the twelve rows has a named home, a measured file count, and (where relevant) an id family; none reads as empty or as a cluster the census failed to find |
| Closure/audit records occupy three homes, not the two NT-0016 §3 states | **Confirmed, independently counted** — `docs/audit/work/` holds 15 `README.md` closure files (one fewer than the draft's 16 at `4f95fb3`; ordinary drift, not disputed), `docs/audit/closure-records.md` is one 4782-line file (byte-identical line count to the draft's own citation), and `ls docs/plans/ \| grep -i closure` returns exactly three non-ledger matches: `2026-08-22-w5-closure.md`, `2026-08-23-w32-closure-proposal.md`, `2026-08-27-closure-audit-standard.md` |
| "plan (map / leaf)" has two live filename grammars for its map sub-kind | **Confirmed** — `slice-map` (4 files: `w6b-slice-map.md` and three `-revised-N` siblings) and `map-plan` (1 file: `2026-08-31-w12-map-plan.md`), no shared `name_pattern` |
| "rulings record" has two live filename grammars | **Confirmed, and grown since the draft** — 23 files match a suffix form (`-ruling.md`/`-rulings.md`/`-rulings-`); 2 files now match a prefix form (`ruling-NN-slug.md`: Ruling 60 and, landed since the draft, Ruling 61 itself) |
| Neither grammar split corresponds to a category the twelve-row hypothesis is missing, or to a hypothesised category that turns out not to exist | **Confirmed by re-reading §1.2 and §1.3 in full** — in both cases the draft's own text states the underlying object is the same one category ("Both name the same underlying object," §1.2; "every file in the 24 is the same object," §1.3's rejected-reading paragraph). Neither section proposes splitting the category, adding a new one, or retiring one |
| No section of the draft (§1, §2, or §3) identifies a category present in the census but absent from the twelve-row hypothesis, or a hypothesised category the census shows does not correspond to real files | **Confirmed by reading §1 through §3 end to end** — §3's "categories no charter creates" (ledger, research note, workflow journey, note, role charter) is an ownership-coverage finding against the same twelve categories, not a claim that any of them is miscategorised or spurious |

### 2. Ruled

**Chosen: Option B — amended.** Keep NT-0016 §3's twelve rows as the base, and apply the
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
the reference-coding grammar a category uses, which NT-0016 §1 (Design constraints) and §4
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
unscoped by this plan), states twelve categories matching NT-0016 §3's names, with
"closure / audit record" documenting three homes rather than two. The map/leaf and
rulings-record filename-grammar inconsistencies are handed to Stage 2 (reference coding
standard) as named items to resolve, not treated as a taxonomy defect requiring a rebuild.

**Overridden if** a future slice's own read of the census surfaces a category the twelve
rows do not name, or shows one of the twelve does not correspond to a real, coherent
cluster of files — neither of which this record found in the draft's evidence.

---

## Ruling 63 — Q2: partial split, evidenced by what the census shows has already happened

### 1. Verified first, independently, at `052afe3`

| Claim | Verdict |
|---|---|
| Ledgers: 16 files, all in `docs/plans/`, zero growth across three tree readings (`7db62ca`, `b551060`, `4f95fb3`) | **Confirmed unchanged at `052afe3`** — `ls docs/plans/*-ledger.md \| wc -l` returns 16, matching the draft's figure exactly; no ledger has ever appeared outside `docs/plans/` |
| Rulings records: all 25 files (23 suffix + 2 prefix, Ruling 62 above) sit in `docs/plans/`, none elsewhere | **Confirmed** — `ls docs/plans/` glob for both grammars returns 25 files, zero outside the directory |
| Closure/audit records already occupy three homes without any rule forcing the split | **Confirmed, Ruling 62 §1** — `docs/audit/work/`, `docs/audit/closure-records.md`, and `docs/plans/*-closure*.md` predate this investigation and were never consolidated |
| Register and findings already occupy two home directories (`docs/audit/register.md`, `docs/audit/findings/`) | **Confirmed** — `docs/audit/register.md` is one file; `docs/audit/findings/` holds 4 `FN.md` files plus a `README.md`, per the draft's §1.6, re-verified by directory listing |
| NT-0016 §10's own recommendation for Q2 was grammar-in-place, on the ground that "splitting multiplies C1 exposure for no reader gain" | **Confirmed as stated** — `.claude/notes/0016-…md:224-225` |

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
exposure (NT-0016 C1: no retro-rename of a cited artifact) that nothing in the evidence
motivates. NT-0016 §10's own reasoning against splitting — "no reader gain" — is sound for
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

## Ruling 64 — Q3: verdict-4 status is derived from an existing closure record wherever one covers the file; declared only for the residual

### 1. Verified first, independently, at `052afe3` and `4f95fb3`

**This ruling is the one in this record whose weight rests on a `referenced_by`-derived
figure — stated at both trees per the preamble's disclosure.**

| Claim | Verdict |
|---|---|
| At `4f95fb3` (the draft's own tree), 39 `docs/plans/` files carry no genuine reference after the census-of-a-census correction, and 36 of the 39 are shown, by manually reading each file against `docs/audit/closure-records.md` and `docs/roadmap.md`, to be fully covered by an existing closure narrative's discussion of the same requirement/slice/Work id | **Confirmed by reading the draft's §4 table in full**, all 39 rows, not sampled — spot-checked independently below rather than accepted on the draft's word |
| At `052afe3`, this record's own tree, the corrected zero-`referenced_by` population is 40 — the same 39 files by path, plus one new file (Ruling 61's own record, filed after the draft) that is unreferenced for the same "too new" reason the draft's own #38/#39 rows state, not for lack of eventual coverage | **Confirmed, independently regenerated** — see this record's preamble; the population grows by exactly the files that landed between the two trees, with no other change |
| Three spot-checked verdict-4 rows resolve against `docs/audit/closure-records.md` exactly as the draft states: `W6b-10 browser auth` (#28), `W6b-15 _minor rename` (#30), and `FR-MODEL-78` (#5) | **Confirmed** — `grep -n "W6b-10 browser auth\|FR-MODEL-78\|W6b-15" docs/audit/closure-records.md` returns the exact citing lines the draft's table quotes, at `052afe3` |
| §0.2's methodology point — a closure record cites the requirement/slice/Work id or PR number, never the plan's own filename, so `referenced_by`'s basename-substring rule structurally cannot see this relationship | **Confirmed by the same spot-check** — none of the three matched lines contains the plan's own filename; each cites only the id, slug, or PR number |
| The 3 verdict-2 files (#13, #36, #38 in the draft's numbering) are each flagged on a stated gap in the file's own text (an unresolved forward reference, an unowned follow-up, or genuine newness), not asserted from silence | **Confirmed by reading rows 13, 36 and 38 in full** — each carries the specific textual evidence the draft's "Reason" column states |

### 2. Ruled

**Chosen: Option C — derived from the existing closure record, as the primary mechanism,
for the population it actually covers.** Where a `docs/plans/` file names a requirement id,
slice id, Work id or PR number that an existing closure record (`docs/audit/closure-records.md`,
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
and its citation, `.claude/notes/0003-duplicated-status-goes-stale.md`, record four prior
incidents of a second copy of a status going stale independently of the record that is
actually authoritative. Ruling 55 above (Q4, this same investigation) already applied this
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

## Ruling 65 — Q7, general half: mixed citation grammar, split by whether a category has its own id family

### 1. Verified first, independently, at `052afe3`

| Claim | Verdict |
|---|---|
| Categories with an existing, independent id family: spec (`FR-`/`NFR-`/`OQ-`), ADR (`ADR-NNNN`), note (`NT-00NN`, already ruled — Ruling 58), register + findings (`F`-number), workflow journey (`wf-NN`) | **Confirmed** — five of the twelve categories from Ruling 62's table carry a minted id family, per the draft's §1.1, 1.8, 1.6, 1.11, 1.12 |
| Categories with no id family of their own: plan (map/leaf), rulings record, ledger, closure/audit record, contract (identified by artifact slug, not a numeric id), process/charter/skill (none of the three sub-kinds mints an id) | **Confirmed** — six categories, per §1.2–1.5, 1.9, 1.10 |
| NT-0016 C2 forbids minting a new id family | **Confirmed, re-read** — `.claude/notes/0016-…md` §1, restated in the investigation plan's Global Constraints and this session's own dispatch constraints |
| Option A (id-only, universally) would require minting a new id family for at least four of the six id-less categories to be citable by id at all | **Confirmed by construction** — a plan, a rulings record, a ledger and a closure/audit record are today identified only by dated filename (Ruling 62 §1, Ruling 63 §1); an id-only citation rule for them has no id to cite unless one is minted |
| The draft's own §4 finding — 36 of 39 (40 of 41 at this record's tree, Ruling 64 §1) "unreferenced" plans are in fact covered, but by a requirement, slice, Work or Ruling number rather than a path | **Confirmed, Ruling 64 §1** — re-verified independently there, not merely re-read |
| `docs/audit/register.md`'s own citation practice already cites `NT-00NN` ids 8 times without an accompanying path | **Confirmed** — matches Ruling 58 §1's own independently-verified figure, re-checked: `git grep -c "NT-00[0-9][0-9]" docs/audit/register.md` returns 8 |
| Ruling 58 already rules the notes family — one of the five id-bearing categories — to cite by id, not path | **Confirmed**, `2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md:226-260`, not reopened here |

### 2. Ruled

**Chosen: Option C — mixed, split by whether the category has an independent id family.**
**Rejected: Option A — id-only, universally.** **Rejected: Option B — path-only, as the
status quo.**

Option A is disqualified mechanically, the same shape Ruling 57 used to disqualify a
symlink for Q6: it is not merely undesirable, it cannot be executed as stated without
violating NT-0016 C2 and this session's own constraint against minting an id. Six of the
twelve categories have no id to cite. Option B is not actually the status quo it names
itself: id-based citation already dominates working practice for every category that has an
id to cite — the register's own 8 unaccompanied `NT-00NN` citations, the universal practice
of citing a spec requirement by `FR-`/`NFR-`/`OQ-` id rather than `docs/specs/NN-module.md`,
and Ruling 58's own ruling for notes are all standing, working precedent, not a proposal.
Declaring "path-only" the rule would reverse practice that is already succeeding for five of
the twelve categories, on no evidence that it is failing.

Option C is what the evidence independently converges on from two directions at once: NT-0016
C2 forces it from above (no new id may be minted, so an id-less category cannot be cited by
id without first creating one — out of scope here), and the draft's own §4/Ruling 64 finding
confirms it from below (citation practice for the id-bearing categories already runs almost
entirely by id, id-less categories are cited by dated filename because that is the only
handle they have). This ruling states as a rule what Ruling 58 already established for one
category and the register's own practice already demonstrates for others: it is not a new
policy invented here so much as a generalisation, named once, of behaviour already present
and not previously written down as a rule.

### 2a. Where this ruling narrows itself, matching Ruling 58's own precedent

As Ruling 58 states for the notes family specifically: this governs **new and living**
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
(which would require its own decision point, since NT-0016 C2 forbids doing so here), or if
citation practice for an id-bearing category is found, on fresh evidence, to run
predominantly by path rather than id.

---

## What this record's ruling now permits

**§4a item 7 of the investigation plan is discharged: all four questions it names — Q1, Q2,
Q3 and Q7's general half — are ruled above, not carried forward.** Combined with Rulings
55–58, all seven of NT-0016 §10's open questions are now ruled.

Per the investigation plan §4's own words, this ruling **is** the trigger the plan names for
NT-0016's Stages 2–5, which that plan "deliberately" leaves unscoped. What it now permits,
stated without scoping it: a future plan may cut Stages 2 (reference coding standard), 3
(ownership map), 4 (workflow-loop audit / verdict decomposition) and 5 (migration and
enforcement) into slices, using the twelve-category set as amended by Ruling 62, the
per-category home rule from Ruling 63, the verdict-4 mechanism from Ruling 64, and the
citation grammar from Ruling 65 (together with Rulings 55–58) as fixed inputs it does not
need to re-derive. Sizing, sequencing and slicing those four stages is that future plan's
work, not this record's — the maintainer has said they intend to read the draft and direct
next steps themselves, and nothing above pre-empts that.

## What this record found, beyond what was asked

- **The draft's §5 Q1 write-up over-reaches on its own strongest evidence.** The two
  independently-found filename-grammar splits are real and are adopted (Ruling 62), but they
  support the amended option, not — as the draft's own text argues — the rebuild option. See
  Ruling 62 §2 for the reasoning; this is a rejection of the draft's own stated argument, not
  merely of the option it argues for.
- **NT-0016 §3's "known tension" undercounts by one home, confirmed independently** at both
  the draft's tree and this record's own — Ruling 62 §1.
- **The census-of-a-census correction (draft §0.1) reproduces cleanly one commit-pair later**,
  gaining exactly one new file (Ruling 61's own record) for exactly the reason the draft's
  own methodology predicts (too new to be cited yet) — stated in this record's preamble and
  relied on directly by Ruling 64.
- **Nothing else in the draft's evidentiary claims failed independent re-verification.** No
  correction is filed against the draft itself; §6 of the draft ("rules none of §5's four
  questions... mints no id... edits no frozen file") is confirmed true by this record's own
  read.

## Constraints observed

Mints no `FR-`, `NFR-`, `OQ-` or `ADR-` id (NT-0016 C2). Edits no file under `docs/plans/`
other than this new record. Does not scope Stages 2–5. Not merged by this role — opened as a
PR and reported by number, per `.claude/roles/decision-maker.md`.
