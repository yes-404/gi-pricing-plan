---
id: RL-8221
family: ruling
title: §14 review E6 — OQ-8206 decided (ii) — GET /api/v1/rating-versions stays unpaginated with a cap of 500 Rating Versions per workspace, measured at each §14 review, with two reopen triggers
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; working id until minted in the §14 review PR, after OQ-8206 mints in SL-1552's PR
created: 2026-10-25
owner: decision-maker
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [OQ-8206, SL-1552, WK-675, RL-1765, NFR-526, NFR-457]   # CR 8219, RL 8163 and FR 8209 added at the mint, once minted
---

# RL-8221 — §14 review E6: OQ 8206 decided, (ii) unpaginated with a cap of 500

*(Working id 8221, reserved by lead 28 in `handover/eta.md` at 2026-10-25 11:35:25 GMT. It
mints in the §14 review's PR, **after OQ 8206 mints in SL-1552's PR** (WK-675 S10), and its
citations of OQ 8206, RL 8163 and FR 8209 are re-pointed to their minted ids then. Working ids
in prose are in space form and are not minted.)*

## How this was ruled

- **The decision is not this record's.** It is the maintainer's, in
  `~/gi-pricing-plan.local/channel/to-lead.md` (a local file, cited by entry header), entry
  *"2026-10-25 11:32:17 GMT — Maintainer: §14 note r5 — the six owed rulings, decided now
  (dated lines for the review's rows)"*, line 4, verbatim:

  > **E6 — decided (ii): unpaginated with a cap.** The named figure: **500 rating versions in
  > one workspace**, measured as the row count of `rating_versions` per workspace on any real
  > or demo workspace at each §14 review; a workspace above 500, or a measured `GET
  > /api/v1/rating-versions` p95 above the platform's list budget, reopens the OQ as a slice
  > under option (i). Record: the **RL** (decision-maker) closing OQ 8206, minted in the
  > review's PR after OQ 8206 mints in S10's. **Gate-row form: JOIN the existing "Before the
  > P2 exit demo" row (count +1)**; the S10 branch's new "…§14 plan review" row is folded into
  > the existing row by the lead in SL-1552's PR before its gate (the branch is unmerged, so
  > this is not a plan edit).

  This line is the dated acceptance line of review item E6. It is decided, so this record
  carries no DRAFT banner.
- **The question it closes.** OQ 8206 is recorded on the S10 branch only, not on `main`:
  `origin/sl-1552-wk675-s10` @`4a4efdd181e7d85d64a1fa9a4560e707d3661f44`,
  `docs/open-questions.md:163`, with its `03` §10 mirror at
  `docs/specs/03-rating-engine.md:1617` and its gate row at `docs/roadmap.md:3519`. The
  question, verbatim from `open-questions.md:163`:

  > **When does `GET /api/v1/rating-versions` need server-side pagination and filtering
  > (status, slug), and at what workspace size?**

  Its options, verbatim: *"(i) Paginate the route with a cursor and `?status=` / `?slug=`
  filters: a backend change, the contract regenerated, the S7 picker (`RL-1765`) updated in
  the same commit. (ii) Keep it unpaginated and state a cap in the §5.1 row, with a named
  figure beyond which (i) is taken."* Its recommendation, verbatim: *"(ii) until a measured
  workspace exceeds a figure this question's owner names (none is set here); decided at the
  `CLAUDE.md` §14 plan review before the P2 exit demo. A decision-maker recommends here and
  does not decide."* Owner WK-675; status `open`.
- **Facts checked at `ff976406`** (`origin/main`):
  - `docs/specs/03-rating-engine.md:1092`, the §5.1 row for `GET /api/v1/rating-versions`,
    says *"**200** with a `RatingVersion[]` (§4.3), unpaginated"* and states no cap.
  - The table the measure counts exists: `backend/src/app/db/models.py:2301`,
    `__tablename__ = "rating_versions"`.
  - **"The platform's list budget"** names no NFR by that phrase: `grep -rn -i "list budget"
    docs/specs` prints nothing. The platform's read budget is `07` **NFR-526** (`07-platform.md:515`,
    *"API metadata reads p95 < 300 ms (NFR-457)"*) after `00` **NFR-457**
    (`00-overview.md:580`, *"Interactive UI: p95 < 300 ms for metadata reads"*). This record
    reads "the platform's list budget" as NFR-526, p95 < 300 ms. **This is a reading, not
    the maintainer's text**: the lead confirms it, or the maintainer corrects it, before the
    mint.

## Ruled

**OQ 8206 is decided (ii): `GET /api/v1/rating-versions` stays unpaginated, with a cap.**

1. **The cap.** 500 Rating Versions in one workspace.
2. **The measure.** The row count of `rating_versions` per workspace, on any real or demo
   workspace, taken at each `CLAUDE.md` §14 review. The measuring predicate is
   `select workspace_id, count(*) from rating_versions group by workspace_id order by 2 desc`,
   and its largest value is read against 500. The review that takes it quotes the database,
   the tree and the output.
3. **Reopen trigger 1.** A workspace with more than 500 Rating Versions reopens OQ 8206 as a
   slice under option (i).
4. **Reopen trigger 2.** A measured `GET /api/v1/rating-versions` p95 above the platform's list
   budget (read here as NFR-526, p95 < 300 ms; see above) reopens OQ 8206 as a slice under
   option (i).

## What it obliges

All of these edits are made on the tree where OQ 8206 is minted, so **they are applied when
this record is folded into the review's PR after SL-1552 merges**. They cannot be made on
this record's branch, which is cut from `ff976406`, where OQ 8206 does not exist.

1. **`docs/open-questions.md`, the OQ 8206 row (its minted id).** The decision edit, as
   `.claude/skills/spec-change` gives it: strike the question and prefix it with *"**DECIDED
   2026-10-25: (ii), unpaginated with a cap of 500 Rating Versions per workspace, by
   `RL-8221`.**"* Leave the options column as it is. Rewrite the recommendation column as the
   decision: the cap, the measure and the two reopen triggers (Ruled 1–4). Set the status to
   *"decided 2026-10-25 (`RL-8221`; the maintainer's entry 2026-10-25 11:32:17 GMT, line 4)"*.
   The decision-maker sets `closed` citing the resolver (`document-ids.md` §1.6 OQ row).
2. **`docs/specs/03-rating-engine.md` §10, the OQ 8206 mirror.** The same strike, and a
   one-line pointer: *"Decided 2026-10-25 by `RL-8221`: (ii), the cap and its reopen triggers
   are in §5.1's `GET /api/v1/rating-versions` row."*
3. **`docs/specs/03-rating-engine.md` §5.1, the `GET /api/v1/rating-versions` row.** It gets a
   dated clause after its existing text (and after S10's FR 8209 clause). The row text is not
   rewritten: *"(**Cap added 2026-10-25, `RL-8221`, OQ 8206 (ii):** unpaginated up to 500
   Rating Versions in one workspace. The count of `rating_versions` per workspace is measured
   at each §14 review. A workspace above 500, or a measured p95 of this route above NFR-526,
   reopens OQ 8206 as a slice under option (i): a cursor and `?status=` / `?slug=` filters.)"*
   **No new FR is appended.** Option (ii) puts the cap in the §5.1 row, and the row is where
   it is read. The route's behaviour does not change, so there is no code or contract delta
   and no test.
4. **`docs/roadmap.md` §10, the "Before the P2 exit demo" row.** By the time this record is
   folded, the lead has folded the S10 branch's separate row into that row, in SL-1552's PR
   (11:32:17 line 4), and that row then shows OQ 8206 bold with its count increased by one.
   This record's edit: strike the id, `~~OQ-<minted>~~ ✔`, with the note *"decided
   2026-10-25 by `RL-8221`: (ii), unpaginated with a cap of 500 Rating Versions per
   workspace, measured at each §14 review; it keeps this row for its revisit"*. Then recount
   the row from its ids: one fewer open, the same total. At `ff976406` the row reads "11 (11
   open)" (`docs/roadmap.md:3523`; the row counts findings and questions together). So,
   with nothing else changed, the row goes to 12 (12 open) at S10's merge and to 12 (11 open)
   at this record's fold. The review decides other ids in the same row, so recount it at the
   end.

## Acceptance — the violation that must become detectable

- *Violation: the cap is decided, but the route still states no cap.* `grep -n "RL-8221"
  docs/specs/03-rating-engine.md` at the review's merged tree prints the §5.1 row and the §10
  mirror. Fewer than two hits means the decision was not applied.
- *Violation: a workspace passes 500 and nobody notices.* Each §14 review quotes the measuring
  predicate's output (Ruled 2). A review without it is missing an item, which its auditor
  can see.
- *Violation: OQ 8206 is closed in one mirror and open in the other.* `audit-docs.py`'s
  open-question mirror check compares the two at the review's merged tree.
