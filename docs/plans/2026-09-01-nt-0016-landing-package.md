# NT-0016 landing package — the reconciliation update, the Work-row draft, and the acceptance batch (2026-09-01)

| | |
|---|---|
| **What this is** | A **proposal package** collecting what the maintainer's next acceptance pass signs: the appended 2026-09-01 update to the frozen [`2026-08-30-nt-0014-0017-reconciliation.md`](2026-08-30-nt-0014-0017-reconciliation.md) (its new §8), the draft Work row for NT-0016's Stages 2–5 (§2 here), and the one-page acceptance-batch summary (§1 here). **Nothing here is in force**: a proposal binds only when the maintainer dates its acceptance line |
| **Tree** | `43fd277` (confirmed equal to `origin/main` when this was written). Every claim below was checked at that tree; every landing is cited from the tree's own history, not from any relay |
| **Who does what** | The planner drafts; the maintainer signs; the lead applies — roadmap rows and the §7 clause are edits to `docs/roadmap.md`, which a planner does not make (`.claude/roles/planner.md`) |
| **What changes** | Exactly two files in this PR: the appended §8 on the reconciliation (additive only — its frozen body is untouched) and this new file. No roadmap edit, no other `docs/` change |

## Acceptance Standard

Each item checkable by a command a fresh reviewer can run at `43fd277`.

1. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this package — run before
   the PR was opened, and check 28's pass is part of that run (the acceptance-standard field
   this file declares is the one check 28 reads).
2. `git diff --stat 43fd277..<branch> -- docs/` names exactly two files:
   `docs/plans/2026-08-30-nt-0014-0017-reconciliation.md` and
   `docs/plans/2026-09-01-nt-0016-landing-package.md`; and `git diff` on the reconciliation
   shows only inserted lines after its original foot — nothing above the appended §8 changes.
3. Every PR number and merge SHA named in the reconciliation's §8 and in §2 below appears in
   `git log --format='%h %s' 43fd277~30..43fd277` with the matching subject — the landing
   record is the tree's own history.
4. No `FR-`/`NFR-`/`OQ-`/`ADR-` identifier is minted or claimed by this package. The ids it
   cites — `FR-DATA-32` and `NFR-RATE-12` — are already defined in
   [`../specs/01-data-management.md`](../specs/01-data-management.md) and
   [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md), and the audit's own
   undefined-id check passes.
5. `git diff --stat 43fd277..<branch> -- docs/roadmap.md` is empty — the Work row below is a
   proposal in this package, applied by the lead only after the maintainer signs.
6. Ruling 58 is honoured by both changed files: notes are cited by `NT-00NN` id or by
   `docs/notes/` path, never by the vacated home's path (checked at write time with the
   concatenation idiom the tombstone test uses, so the probe cannot match itself).

---

## 1. The acceptance batch — three instruments, one pass

The maintainer is asked for three signatures, each a single dated line. For each: what the
line signs, the verified state behind it, and who applies what once it is dated.

### 1.1 The reconciliation — four dispositions

**Sign:** the single acceptance line at the foot of
[`2026-08-30-nt-0014-0017-reconciliation.md`](2026-08-30-nt-0014-0017-reconciliation.md),
which carries all four dispositions: NT-0014 — ADOPT the remainder (Slices E, F, G) as one
Work row; NT-0015 — ADOPT as one Work row (P1–P5); NT-0016 — **ADOPT Stages 2–5 as one Work
row**, the revision appended 2026-09-01 (§8.2 of that file); NT-0017 — ADOPT and close on its
residue (impact rows 6 and 9).

**Verified state at `43fd277`.** NT-0014 and NT-0015 both show *"Landed"* in the roadmap's
pending-proposals table — all eight slices and P1–P5 respectively are merged, and the table
records it — while the reconciliation's acceptance line is still `_pending._`: the work is in,
and none of the four dispositions binds until the signature. NT-0016's four investigation
slices and all eleven rulings are merged (§8.1 of the appended update, one row per item). The
investigation plan's own close — its §4a eight-item standard — is a separate act at the
plan's close, not part of this batch; the team reports seven of the eight items verified at
this tree, with the eighth (the frontend half of the gate) being re-run by the team's
gate-runner as this package is written.

**After the signature:** the lead converts each adopted note to its Work row in
`docs/roadmap.md` §7 (clause 2) — using the row drafted in §2 below for NT-0016 and the
reconciliation's own row shapes (§2–§5 of its frozen body) for the other three. NT-0017's
impact-row-6 line (the repository settings) is the maintainer's to write; nobody else can
supply it. NT-0016's row then opens on the maintainer's direction — the gate ruling's closing
section records that the maintainer intends to read the taxonomy draft and direct next steps
themselves.

### 1.2 The three plan reviews

**Sign:** date the three pending acceptance lines of plan reviews 9, 10 and 11 in
[`../audit/plan-reviews.md`](../audit/plan-reviews.md) together, as review 11's proposal 11.1
recommends. The lead has accepted that recommendation and will carry it, and review 10's
proposal 5.2 had already asked for 9 and 10 as two acceptances on one occasion.

**Verified state at `43fd277`.** All three lines read `_pending._`; reviews 9 and 10 have
been pending since 2026-08-30. Per the lead's relay, the hold is the maintainer's own:
release once NT-0016 has landed with a solid solution and implementation. The landings cited
in the reconciliation's §8.1 are that landing — four slices merged, a taxonomy draft
clustered from a byte-reproducible census, eleven rulings — so the trigger is met, and the
"solid" half can now be judged on the cited evidence rather than on promise.

**After the signature:** the reviews' proposals bind from that date. The four unnumbered rule
candidates (A, B, the third, and P12) are numbered into
[`../process/delivery-process.md`](../process/delivery-process.md) §15 in the same pass —
numbering happens at acceptance, per the reviews' own rule. The eleven register rows behind
review 11 then receive their final dispositions from their named owners; several are
themselves decisions the signature hands over rather than makes: F48's placement and F63's
reading are the maintainer's (F63 alone, per `CLAUDE.md` §13 — reopening a Work close is
theirs alone); F62's ruling is the decision-maker's; DP-1's placement is the lead's and
maintainer's; `NFR-RATE-12`'s branch is the maintainer's to place; the F26, F58 and F61 owner
assignments are the lead's (review 11's table lists F26 as maintainer-or-lead); F31's charter
correction follows review 9's proposal 5.3, carried forward by review 11, once accepted.

### 1.3 The clause-2 exception

**Sign:** accept the reconciliation §7 recommendation verbatim — clause 2 of
`docs/roadmap.md` §7 gains one clause: *a note may land work ahead of its reconciliation
under a dated maintainer delegation or a light-path ruling, and the reconciliation then
records what landed rather than authorising it.*

**Verified state.** The clause-2 rule and the practice already diverge in three recorded
instances: NT-0014's Slices A–D under a dated delegation, NT-0017's S1/S2 under the note's
§7 light path, and now NT-0016's four slices and rulings under the 2026-09-01 acceptance.
None was irregular in itself; clause 2 as written states an absolute with a documented
exception, so a reader following the rule literally concludes merged bodies of work were
unauthorised — which they were not. The reconciliation's own §7 makes exactly this argument.

**After the signature:** the lead applies the one clause to `docs/roadmap.md` §7 clause 2 — a
clause addition, not a rewrite (the reconciliation's own §7 wording). NT-0016's §8.1 record
then stands as the second recorded instance of the exception, which is the point of it: the
reconciliation records what landed rather than authorising it.

---

## 2. The draft Work row — NT-0016 Stages 2–5

Proposed as a workstream row in the roadmap's `| # | Workstream | Notes |` shape. The id is
assigned at placement, not here — see the placement note below. The row's scope is
[`NT-0016`](../notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md) §4–§7
(Stages 2–5) — Stage 0's census and Stage 1's draft, plus the §3a notes move, have already
landed as the investigation plan's four slices, and are not re-scoped.

| # | Workstream | Notes |
|---|---|---|
| **W— (id assigned at placement)** | **File taxonomy, reference coding and custody — NT-0016 Stages 2–5** | [`NT-0016`](../notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md) §4–§7, built against the ruled inputs (Rulings 55–65). **Stage 2 — the reference-coding standard:** filename grammar and header block per category, over the twelve-category set as amended by Ruling 62 (the closure/audit record's three homes documented; the map/leaf and rulings-record grammar splits resolved here as the named items Ruling 62 hands over); one home per category per Ruling 63 (rulings and ledgers stay in `docs/plans/` under filename grammar; closure/audit records keep their three homes; register + findings keep their two); citation forms per Ruling 65's mixed grammar — spec, ADR, note, register/findings and workflow journey cite by their existing id, while plan, rulings record, ledger, closure/audit record, contract and process/charter/skill cite by dated filename — prospective only, no frozen retrofit (Ruling 65 §2a, matching Ruling 58 for the notes family); `docs/INDEX.md` as the legacy mapping so the standard covers every file without moving one (C1); `scripts/file-lint.py` wired into the gate warn-then-red with a dated flag-day; the five creating skills (`writing-plans`, `close-workstream`, `phase-review`, `adr-write`, `spec-change`) updated to emit the standard. **Stage 3 — the ownership map:** the category × role matrix (creates/amends/retires) as a living file in `docs/process/` (Ruling 55), every cell citing the charter line that grants it, empty rows and columns filed as findings per NT-0015's grammar. **Stage 4 — the workflow-loop audit:** the lifecycle triple per category (which step creates, reads, retires), the four verdicts, and the unreferenced population — 39 files at `4f95fb3`, 40 at `052afe3` — decomposed into verdict-2 findings or declared verdict-4; verdict-4 status is **derived** from an existing closure record wherever one covers the file, and an explicit declaration is required only for the residual — the 3 verdict-2 files plus any future file with no covering closure record — in whichever of the two forms the implementing slice chooses (Ruling 64). **Stage 5 — migration and enforcement:** the prospective standard live from the flag-day; legacy migrates opportunistically-on-amendment only, never a bulk rename (C1); the census re-runs at every phase close, with growth in uncategorised or verdict-2 files a red flag in the phase review. **Dependencies:** Stage 4 needs the committed census (`docs/audit/file-census-5ef559d.csv`) and Stage 3's matrix; Stage 5 needs Stage 2; Stages 2 and 3 are independent now that Stage 1 and the gate ruling have landed (the note's §8 dependency chain). **Acceptance:** the note's §11 items (a)–(g). The notes move (the note's former S0) already landed as the investigation plan's Slice 4 (`1ec453b`, PR #544) |

**Placement — recommended, not decided.** Phase 2's workstream table, beside W12. Three
reasons: Phase 2 is the phase currently open, and a row placed anywhere else would sit in a
table whose phase has closed; the pending-proposals table already sits under Phase 2, so the
NT-0014 and NT-0015 conversion rows land beside this one on the same signature — one pass
over one table; and the work has no `RATE`-requirement dependency, so it can sit beside the
phase's work without blocking or being blocked by it. The decision is the maintainer's — the
reconciliation's own §2 states the pattern (*"the roadmap row is the maintainer's to place"*)
— and this package supplies the row's text, not its position. Wherever it lands it is a
process/documentation row of the same class as the NT-0014 and NT-0015 rows it lands beside.

---

## 3. What this package does not do

- **It does not edit `docs/roadmap.md`.** The row above and the §7 clause are proposals,
  applied by the lead after the maintainer signs — the same division the reconciliation's own
  §7 records.
- **It does not date any acceptance line.** Only the maintainer can; the three lines in
  §1.1–§1.3 stay `_pending._` until then.
- **It does not slice the Work.** Sizing, sequencing and slicing Stages 2–5 is a future
  plan's work — the gate ruling's *What this record's ruling now permits* says so in its own
  words, and this package does not pre-empt it.
- **It does not close the investigation plan.** The plan's §4a eight-item standard is a
  separate acceptance act at the plan's close.
- **It does not decide any register-row disposition.** Each of the eleven rows behind review
  11 goes to its named owner (§1.2); this package names the owners and stops.
