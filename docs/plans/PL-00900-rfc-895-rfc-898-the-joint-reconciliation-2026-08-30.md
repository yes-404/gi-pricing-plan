---
id: PL-900
family: plan
kind: leaf
title: RFC-895 … RFC-898 — the joint reconciliation (2026-08-30)
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-30
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-30-nt-0014-0017-reconciliation.md
---

# RFC-895 … RFC-898 — the joint reconciliation (2026-08-30)

| | |
|---|---|
| **What this is** | The reconciliation [`../roadmap.md`](../roadmap.md) §7 fixes to WK-671's close: each of the four filed working notes carried to a **recommended disposition** — adopt, reject or defer — with its reasoning. It is a **proposal**. Nothing here is in force |
| **Tree** | `b749acb`, confirmed equal to `origin/main` when this was written. Every claim below was checked at that tree |
| **Trigger** | Shared with `CLAUDE.md` §14's plan review 10, filed the same day as a separate document — [`../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md`](../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md). Separate because the two instruments carry different acceptance: a §14 review outputs one acceptance line over five answers, a reconciliation outputs a disposition **per note**, and one line cannot carry four |
| **Acceptance** | **The maintainer's**, and left undated below. Adoption schedules work, and scheduling is not a lead's or a planner's to decide (`../roadmap.md` §7 clause 2; the same rule `CLAUDE.md` §12 applies to a Work close) |
| **Implements nothing** | Per the maintainer's instruction of 2026-08-30 — *"do everything you can before implementation, and give me a chance to refine the plan"*. No file outside this document is changed by it, no roadmap row is added, and no adoption begins on the strength of a recommendation |

---

## 1. What this reconciliation actually has to decide

Less than the roadmap table anticipated, and the difference is worth stating before the
per-note sections, because it changes what the maintainer is being asked for.

**Three of the four notes have had their open questions ruled already.** The decision-maker
settled RFC-895's Q1/Q3/Q4 ([`../rulings/RL-00908-impact-matrix-row-4-does-not-sit-forever-it-inverts-and-part-c-row-5-closes-here.md`](../rulings/RL-00908-impact-matrix-row-4-does-not-sit-forever-it-inverts-and-part-c-row-5-closes-here.md),
Rulings 40 and 45–48), RFC-896's Q1–Q5 ([`../rulings/RL-00913-q5-file-by-the-f-id-verbatim-the-requirement-id-cannot-name-a-file-and-is-cross-linked-from-inside-it.md`](../rulings/RL-00913-q5-file-by-the-f-id-verbatim-the-requirement-id-cannot-name-a-file-and-is-cross-linked-from-inside-it.md),
Rulings 49–53), and RFC-898's three policy questions went to the maintainer directly
([`../rulings/RL-00914-rfc-898-the-maintainer-s-three-policy-decisions-recorded-2026-08-30.md`](../rulings/RL-00914-rfc-898-the-maintainer-s-three-policy-decisions-recorded-2026-08-30.md)).
**Only RFC-897's seven remain unruled**, which is the same note the maintainer has already
identified as the one needing full research.

**And two of the four have already landed work.** RFC-895's Slices A–D are merged; RFC-898's
S1 and S2 both landed on 2026-08-30, so `README.md`, `SECURITY.md`, `CONTRIBUTING.md` and
`.github/`'s templates exist at this tree. So for those two the question is not *whether* to
adopt — it is what remains, and under what row.

**That is itself a finding, and §7 below takes it up rather than leaving it implicit.** The
roadmap's clause 2 says *"until that row exists, nothing is scheduled"*, and work was done on
two notes before any row existed. The rule and the practice have diverged, and the
reconciliation is the moment to say which one is wrong.

---

## 2. RFC-895 — machine-readable process core

**State at `b749acb`.** `Status: accepted` (corrected the same day from `open`, which had gone
false in both halves). Slices **A–D merged** — `33b5ef1` (#448) files the core extract and the
`§12`→`§15` fix, `0be9c3c` (#451) adds `audit-docs.py` check 26's drift check, `97965be` (#456)
lands RFC-842's two rules and RFC-843's unlanded half. **Slices E, F and G are not started**:
E is the runtime state file plus the watcher, F is the plan validator C1 with the
acceptance-standard field in `writing-plans`, G is hooks C2 and C3 — re-cut by RL-920 to its
hook alone and left blocked on E.

**Recommended disposition: ADOPT the remainder, as one Work row covering E, F and G.**

**Reasoning.**

- **The decision work is finished.** All four of the note's own open questions are ruled, and
  the rulings are specific enough to build against — RL-920 fixes E's shipped fields
  (`position` and `in_flight_expensive_verifications` only, the roster-state claim carried only
  if E can name its source), and re-cuts G rather than leaving it as filed.
- **The mechanism is proven, not speculative.** Check 26 exists, runs in the gate, and was
  landed with a six-mutation proof and a silent negative control. The part of this note that
  could have failed on contact with the repository has already made contact.
- **The remainder is small and sequenced.** E → F are independent; G is blocked on E. There is
  no research left to do.

**What the Work row should say, if accepted.** Scope: RFC-895 Slices E, F, G. Dependencies: E
before G; F independent. Phase: whichever phase the maintainer places process work in — this
note takes no view, and the roadmap row is the maintainer's to place. Owner of the close: the
maintainer (`CLAUDE.md` §12).

**One thing the row must not silently inherit.** The adoption record names **F27(c), F29 and
F33** — the gate-coverage cluster — as findings the §14 review was to have bundled, and
records that the adoption *"must either pick them up deliberately or record that it left
them"*. This reconciliation records that **it leaves them**, and plan review 10 carries them as
an open decision point rather than resolving them here. F33 was materially advanced by
`c8d3c81`; F27(c) and F29 remain open.

---

## 3. RFC-896 — the register is a ledger, evidence is a file

**State at `b749acb`.** `Status: open`. All five open questions are ruled (Rulings 49–53). **No
part of it has landed** — the register's three most recent commits are the F53, F54 and F55
filings, none of them the RL-909 ride-ahead.

**Recommended disposition: ADOPT, as one Work row, and treat RL-909's ride-ahead as owed
now rather than as the Work's first slice.**

**Reasoning.**

- **The maintainer's steer is that this is quick, and the rulings make it quicker.** RL-911
  rejected the "worst offenders" migration as a class that does not exist; RL-910 removed
  the legacy/flag-day machinery entirely. Both rulings *shrank* the note.
- **RL-909 already authorised the ride-ahead PR, dated 2026-08-30, and assigned it to the
  auditor.** It has not landed at this tree. That is a standing obligation from a ruling, not
  a proposal this reconciliation is making — the recommendation is only that the
  reconciliation not silently re-absorb it into a Work that has no start date yet.
- **RL-910 is the load-bearing one and it makes P1 a precondition rather than a nicety.**
  It ruled: no legacy class, no exemption, no warn phase, no flag day — the corpus is conformed
  and `register-lint.py` is red on day one, on every row. That converts P1 from documentation
  into the thing P3 is checked against, and it means the ten non-conforming rows must be fixed
  **before** the linter lands, not after.

**What the Work row should say, if accepted.** Scope: P1–P5. Slices: the RL-909 ride-ahead
(P1 + P2 + the ten-row conformance) → P3 `register-lint.py` red on day one → P4 the
ledger/evidence split, incremental per RL-911 → P5 `register-owed.py`, whose output lands
verbatim per RL-912 and is filed by F-id per RL-913. Acceptance: the note's own §8, which
already names three deliberately broken fixture inputs.

---

## 4. RFC-897 — file taxonomy, reference coding, custody

**State at `b749acb`.** `Status: open`. **Seven open questions, none ruled** — the only note of
the four in that position. Its own §8 sizes it at one Work of roughly five slices plus an audit
slice, after two read-only investigation stages.

**Recommended disposition: ADOPT STAGES 0–1 ONLY, as an investigation, and defer Stages 2–5
until its census exists.** Not a deferral of the note — a deferral of everything that cannot
honestly be scoped yet.

**Reasoning, and it is the note's own.**

- **Its seven questions cannot be ruled on the evidence that exists.** Q1 asks whether the
  taxonomy's closed set is ruled as drafted, amended, or **rebuilt from the census** — and the
  census has not been run. The note's own recommendation is *"rule on the census-clustered set,
  not the hypothesis."* Ruling Q1 today would rule on the hypothesis.
- **This matches the maintainer's steer exactly**, that RFC-897 needs full research, a plan, and
  a cut into slices, proposed rather than implemented. Stage 0 is the census script; Stage 1 is
  the taxonomy draft. Both are read-only, both are one session each, and together they produce
  precisely the evidence the decision-maker needs for Q1–Q7.
- **Its largest single act should not ride ahead of that.** §3a moves `.claude/notes/` to
  `docs/notes/` — the note itself measures the path-citation cost at 28 files, and the notes
  being moved include the other three under reconciliation here. Sequencing that before the
  taxonomy is ruled would be the tail moving the dog.
- **One dependency to record rather than resolve.** RFC-898's `README.md` has already landed and
  cites the pre-move notes path. The note anticipates this and makes it a living-citation update
  inside S0, so the two compose in either order. Nothing is blocked; it is a fact the S0 slice
  must carry.

**What the row should say, if accepted.** A **research/investigation row**, not a delivery row:
scope is Stages 0 and 1 and stops there, output is a committed census and a taxonomy draft, and
its exit is the decision-maker being able to rule Q1–Q7 against measured data. Stages 2–5 get a
row when that ruling exists — deliberately not scoped here, because scoping them now is the
thing this recommendation says cannot yet be done honestly.

---

## 5. RFC-898 — a public face for a public repository

**State at `b749acb`.** `Status: open` — but **the content has landed**. `README.md`,
`SECURITY.md`, `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`
all exist at this tree, filed as S1 then S2 on 2026-08-30 under the note's own §7 light path,
after the maintainer ruled its three policy questions. `docs/process/security-posture.md` carries
its pointer.

**Recommended disposition: ADOPT, and close it fast — what remains is a short residue, not a
Work.**

**Reasoning.** The exposure the note was written about is discharged: the repository went public
with none of these files and now has all of them. The maintainer ruled the one real decision
(the contribution posture) before `CONTRIBUTING.md` was written, which is the ordering the note
itself demanded.

**The residue, measured at this tree rather than assumed.** Two of the note's nine
impact-matrix rows are not discharged:

| Impact row | State at `b749acb` |
|---|---|
| 6 — the two repository settings (private vulnerability reporting; issues with templates) | **Not verifiable from the tree.** Settings-side, so per the note's own §8(b) it is evidenced by a dated maintainer line, which does not exist yet |
| 9 — `docs/roadmap.md` gains this Work's row | **Not present** — the note is still listed only as a pending proposal |

Impact row 7 **is** discharged: `docs/process/checklists/work-item-close.md:21-23` carries the
pointer-freshness check. This section first reported it as missing; the first search looked for
`SECURITY.md` and a hyphenated *pointer-freshness*, and the line says *"pointer freshness"* of
the root `README.md`. Corrected before filing and recorded rather than silently fixed, because
the mistake is the reusable part — a two-token search answered a narrower question than the one
asked, and a null result read as an absence.

**What the row should say, if accepted.** A single small row whose scope is those two items and
whose acceptance is the note's §8 (a) and (c)–(e) — the link check, a test issue filed through
each form, and the auditor's outsider read of the `README`. The settings line is the
maintainer's to write and nobody else can supply it.

---

## 6. Summary of recommendations

| Note | Recommended disposition | Row shape | What is already true |
|---|---|---|---|
| RFC-895 | **Adopt the remainder** | One Work: Slices E, F, G | A–D merged; all four questions ruled |
| RFC-896 | **Adopt** | One Work: P1–P5 | Five questions ruled; RL-909's ride-ahead authorised and not yet landed |
| RFC-897 | **Adopt Stages 0–1 only; defer 2–5** | One investigation row | Nothing ruled, nothing built — by design |
| RFC-898 | **Adopt, and close on a short residue** | One small row: impact rows 6 and 9 | Content landed; exposure discharged |

**No note is recommended for rejection**, so `../roadmap.md` §7 clause 3's retirement path is
not exercised here. Every note above either converts to a row or keeps a named next trigger:
RFC-897's Stages 2–5 are the only deferred item, and its trigger is the decision-maker ruling
Q1–Q7 against the Stage 0 census.

---

## 7. The finding the four raise together, which no single note raises

**Work landed on two of these notes before any Work row existed, and the roadmap's own rule
says that cannot happen.** Clause 2 reads *"until that row exists, nothing is scheduled"* and
*"no adoption is implemented before that signature"*. Yet RFC-895's Slices A–D are merged and
RFC-898's S1 and S2 are merged, both on 2026-08-30, both before this reconciliation was written
and therefore before any acceptance line could have been dated.

**Neither was irregular in itself.** A–D landed under a dated maintainer delegation; S1 and S2
landed under the note's §7 light path after the maintainer ruled its three policy questions, and
the roadmap table records both facts openly rather than hiding them. The problem is narrower and
worth fixing precisely: **clause 2 states an absolute where the practice has a documented
exception**, so a reader following the rule literally would conclude that two merged bodies of
work were unauthorised, which they were not.

**Recommendation — one clause, not a rewrite.** Clause 2 gains an explicit exception: *a note
may land work ahead of its reconciliation under a dated maintainer delegation or a light-path
ruling, and the reconciliation then records what landed rather than authorising it.* That is
what both cases actually were. **Recorded as a proposal against the roadmap, applied by the lead
or decision-maker if accepted** — a planner does not edit `docs/roadmap.md`
(`.claude/roles/planner.md`).

**Why this belongs here and not in plan review 10.** It is a rule about how notes are adopted,
which is this document's instrument, not the plan's shape. Review 10 carries the findings about
how *plans* are written; this one is about how *notes* become work.

---

**Maintainer acceptance:** _pending._ Four dispositions are proposed above and none binds until
this line carries a date and a signature. Per the maintainer's instruction of 2026-08-30, no
adoption is implemented before that signature, and no roadmap row is added on the strength of a
recommendation alone.

---

## 8. Appended 2026-09-01 — what landed under the maintainer's delegation, and the revised RFC-897 disposition

**The body above is frozen as filed at 2026-08-30 (`b749acb`) and is not edited.** This
section is appended after its original foot — the same append-only pattern
[`PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md`](PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md) uses for its own
*Corrections after filing* — so a reader sees both what was believed at the freeze date and
what happened after. **The acceptance line above this section is still `_pending._`**: nothing
here dates it, and none of the four dispositions binds until the maintainer dates it.

### 8.1 The delegation, and what landed under it

On 2026-09-01 the maintainer accepted the investigation plan *"as filed"* — recorded verbatim
in that plan's own acceptance line (`f57d335`, PR #532). That acceptance is the dated
maintainer delegation under which the four slices and the rulings below landed. One row per
item, never a range; every merge is cited from `origin/main`'s own history at `43fd277`.

| Item | PR | Merge | What landed |
|---|---|---|---|
| The plan | #532 | `f57d335` | The investigation plan, accepted by the maintainer as filed on 2026-09-01 — the delegation itself |
| Slice 1 | #540 | `cbf1365` | `scripts/audit-docs.py`'s notes scan roots fail loudly when absent — the live silent-skip defect the plan's §1b proved, fixed |
| Slice 2 — Stage 0 | #537 | `4f95fb3` | `scripts/file-census.py` plus tests, the committed census `docs/research/file-census-5ef559d.csv`, and its companion `docs/research/RS-00952-file-census-rfc-897-stage-0.md` |
| Slice 3 — Stage 1 | #545 | `9e70469` | `docs/research/RS-00953-file-taxonomy-draft-rfc-897-stage-1.md` — the taxonomy draft clustered from the census; rules nothing |
| Slice 4 — Stage 3a | #544 | `1ec453b` | The notes move to `docs/notes/` (18 notes + README), living citations updated, and a watched tombstone left at the vacated home |
| RL-945 — Q4 | #535 | `c0d1712` | The ownership matrix lands as a living file in `docs/process/`; a frozen note appendix is rejected |
| RL-946 — Q5 | #535 | `c0d1712` | Notes destination is `docs/notes/`, keeping the family's name and README; folding into an existing `docs/` family is rejected |
| RL-947 — Q6 | #535 | `c0d1712` | Tombstone form is a README mapping; a symlink is rejected |
| RL-948 — Q7, notes half | #535 | `c0d1712` | Notes are cited by `NT-00NN` id, resolved via the notes index; new path citations are rejected for this category |
| RL-949 | #539 | `7f1e3c6` | The census CSV is outside FR-72's scope; the test gains a second carve-out bought by provable reproducibility — implemented in PR #541 (`15eb633`) |
| RL-950 | #542 | `df0a430` | RL-949's fetch path is broken against github.com; resolved by `fetch-depth: 0` — implemented in PR #543 (`4251501`) |
| RL-951 | #546 | `052afe3` | RL-947's tombstone gains 18 per-file stubs, watched by a new check 30 |
| RL-941 — Q1 | #547 | `43fd277` | The twelve-category set is ruled **amended**: closure/audit record gains its third home; the two filename-grammar splits go to Stage 2 as named items |
| RL-942 — Q2 | #547 | `43fd277` | Partial split: rulings and ledgers stay in `docs/plans/` under filename grammar; closure/audit records keep their three homes; register + findings keep their two |
| RL-943 — Q3 | #547 | `43fd277` | Verdict-4 status is **derived** from an existing closure record wherever one covers the file; an explicit declaration is required only for the residual |
| RL-944 — Q7, general half | #547 | `43fd277` | Mixed citation grammar: categories with an id family cite by id; the six id-less categories cite by dated filename — prospective only, no frozen retrofit |

### 8.2 The revised RFC-897 disposition

§4 above recommended **ADOPT STAGES 0–1 ONLY, and defer Stages 2–5**, with the trigger §6
names in its own words: *"RFC-897's Stages 2–5 are the only deferred item, and its trigger is
the decision-maker ruling Q1–Q7 against the Stage 0 census."* **That trigger has now fired,
and the revised recommendation is: ADOPT Stages 2–5 as one Work row.** The reasoning:

- **The named trigger is ruled.** Rulings 62–65
  ([`../rulings/RL-00944-q7-general-half-mixed-citation-grammar-split-by-whether-a-category-has-its-own-id-family.md`](../rulings/RL-00944-q7-general-half-mixed-citation-grammar-split-by-whether-a-category-has-its-own-id-family.md),
  PR #547) are the decision gate the investigation plan places after Slice 3, and that record
  states it in its own words: *"Per the investigation plan §4's own words, this ruling is the
  trigger the plan names for RFC-897's Stages 2–5."* Combined with Rulings 55–58, all seven of
  RFC-897's §10 questions are now ruled — the gate record's *What this record's ruling now
  permits* discharges the plan's §4a item 7 on exactly this point.
- **The evidence the deferral was waiting for exists.** The census is committed and
  byte-reproducible (`docs/research/file-census-5ef559d.csv`, corpus rule and row count stated in
  `docs/research/RS-00952-file-census-rfc-897-stage-0.md`), and the taxonomy draft (`docs/research/RS-00953-file-taxonomy-draft-rfc-897-stage-1.md`) is
  what Rulings 62–65 rule against.
- **Nothing remains to research.** Stages 2–5 are build work whose inputs are all fixed: the
  twelve-category set as amended (RL-941), the per-category home rule (RL-942), the
  verdict-4 derivation mechanism (RL-943), the mixed citation grammar (RL-944), and the
  notes-family rulings (55–58). The investigation plan's §4 left these stages unscoped only
  until this gate fired; scoping them now is exactly what it said could not be done honestly
  before.
- **The maintainer's direction is not pre-empted.** The gate ruling's closing section records
  that the maintainer intends to read the draft and direct next steps themselves. This revision
  proposes the row; the row opens on the signature, and nothing above schedules it.

The row's scope, dependencies, acceptance and placement are drafted in
[`PL-00938-rfc-897-landing-package-the-reconciliation-update-the-work-row-draft-and-the-acceptance-batch-2026-09-01.md`](PL-00938-rfc-897-landing-package-the-reconciliation-update-the-work-row-draft-and-the-acceptance-batch-2026-09-01.md) §2 — kept out
of this frozen file's body for the same reason the reconciliation itself was written as a
proposal rather than edited into the roadmap.

**What this revision does not touch.** The other three dispositions (§2, §3, §5) stand as
filed. Their *state* has moved since `b749acb`: RFC-895's remainder (Slices E, F, G) and
RFC-896's P1–P5 have since landed — `docs/roadmap.md`'s pending-proposals table records both
("Landed 2026-08-31 — all eight slices merged" / "Landed 2026-08-31 — P1–P5 all merged") — so
for those two the signature now converts landed work into Work rows rather than authorising
new work. RFC-898's residue (impact rows 6 and 9) is unchanged: no Work row exists and the
settings line is unwritten. The plan's own acceptance line already records the one narrow
change it made to this file's §4 — separating the notes move (§3a) from the deferred stages,
*"for the purposes of this plan's four slices"* — and this section records the remainder of
that change here rather than leaving it implicit.

### 8.3 The §7 clause-2 exception, carried forward unchanged

§7's recommendation stands exactly as filed and is not amended by this append: *clause 2 gains
an explicit exception — a note may land work ahead of its reconciliation under a dated
maintainer delegation or a light-path ruling, and the reconciliation then records what landed
rather than authorising it.* RFC-897 is now precisely that shape: the four slices and eleven
rulings above landed under the dated 2026-09-01 delegation, and §8.1 records them rather than
authorising them. That is the second instance of the exception's delegation limb (RFC-895's
Slices A–D being the first; RFC-898's S1/S2 the light-path limb), which is the strongest
evidence yet that the clause should be written down rather than left as an unwritten practice.
Applied by the lead to `docs/roadmap.md` §7 if accepted — a planner does not edit the roadmap
(`.claude/roles/planner.md`).

---

**Appended 2026-09-01 — the dated acceptance block.** The `_pending._` paragraph kept in place
above (immediately after §7) is the record of the pre-signature state and is not edited. The
maintainer's signature, recorded verbatim:

**Maintainer acceptance: accepted as proposed, 2026-09-01 — all four dispositions (RFC-895
remainder E/F/G, RFC-896 P1–P5, RFC-897 Stages 2–5 as one Work row, RFC-898 residue) and §7's
clause-2 exception. RFC-897's Work row is placed in Phase 2 beside WK-672. Plan reviews 9, 10 and
11 are dated together under proposal 11.1, this same date.**

**Who applies what, from this date.** The lead converts the four adopted notes to their Work
rows in `docs/roadmap.md` §7 (clause 2) — RFC-897's row is the landing package's §2 draft at
its ruled placement (Phase 2, beside WK-672) — and applies the clause-2 exception as one clause
addition. RFC-898's impact-row-6 settings line remains the maintainer's to write. The four
unnumbered rule candidates (Candidate A, Candidate B, review 9's third, and P12) are numbered
into `docs/process/delivery-process.md` §15 by the lead in the same pass.
