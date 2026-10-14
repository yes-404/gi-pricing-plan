---
id: PL-8002
family: plan
kind: map
title: WK-673 — RL-9996's DP-P1 fix, FR-242's drafted change summary pairs a rate table's versions through the table step that names them and refuses no pin set, and SL-1678's guard is removed (SL-8003): a dated delta to PL-1267
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: 36e2610ab8135bc3b3563464e7f5f719713b168b
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1267, RL-9996, FD-1679, PL-1677, SL-1678, LG-1681, RL-1498, RL-1538, PL-1502, SL-1503, PL-1542, SL-1543]
---

# PL-8002 — WK-673, DP-P1's fix: the drafted change summary pairs rate tables through the `table` step, and the FD-1679 guard goes (delta to PL-1267)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). It adds
> **one slice row**, SL-8003 (working id), under `### WK-673` in [`../roadmap.md`](../roadmap.md),
> to WK-673's Work plan [`PL-1267`](PL-01267-wk-673-dislocation-with-attribution-map-plan.md),
> whose body is frozen and not edited. It records `PL-1677`'s DP-P1 as **ruled** by RL-9996
> (working id), and cuts the fix slice that ruling obliges.
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds, as RL-9996 "What it
> obliges" lists them: `test-driven-development` (every red is seen red **by its cause** on
> `main` before the code that turns it green), `python-test` (the `req` marker; negative tests),
> `spec-change` (Task 1), `contract-schema` (Task 4; `contract-guard` is **not** bound, because
> the regenerated contract is not guarded: premise k), `dev-commands` (`uv sync --all-packages`;
> both gate halves) and `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions
> before the first step. The executor is spawned from `.claude/roles/executor.md`.

Filed under **working id 8002**; its slice row is **SL-8003** (`draft`, working id 8003). Both ids
were reserved by the lead, `~/gi-pricing-plan.local/handover/eta.md`, line "2026-10-14 09:42:42
BST lead: RESERVED working ids PL 8002 (PL-1267 dated delta: the RL 9996 / DP-P1 fix slice,
WK-673; write set exactly RL 9996 "What it obliges") and SL 8003 (its slice). Free-check own call:
8002/8003 id-form 0, eta 0, INDEX 0, branches 0, git grep origin/main docs+.claude 0. Seat
planner-dpp1fix." Written 2026-10-14 from 09:47 BST (by `TZ=Europe/London date`) by the planner
(seat planner-dpp1fix). **Tree read:** `origin/main` `36e2610ab8135bc3b3563464e7f5f719713b168b`
(#1296, SL-1678). Every `file:line` below was read at that tree unless a branch is named. The
branch is cut from RL-9996's branch `origin/rl-9996-dpp1-2026-10-14`
@`0d8f1288bfe974af064e9284b3b4cc27c6c91607`, so the ruling is citable; it re-merges `origin/main`
after the ruling is minted.

## Context — the entries this delta records

Each entry is quoted from the record or channel file named, with its author.

1. **The ruling** — RL-9996 (working id; the decision-maker, seat dm-dpp1), file
   `docs/rulings/RL-09996-dp-p1-decided-the-change-summary-pairs-a-rate-table-s-versions-through-the-table-step-that-names-them-and-refuses-no-pin-set.md`
   on `origin/rl-9996-dpp1-2026-10-14` @`0d8f1288`. Its §"Ruled" table, row DP-P1, verbatim:
   *"(a′): pair a rate table's versions through the `table` step that names them, by `step_id`; a
   pin difference no step entry names is paired by slug only when it is the one such ref on each
   side, else listed alone; no pin set refused; `RateTableChange` gains `step_id`"*. Row "The
   guard": *"removed by the fix slice, no residual case kept; SL-1678's three tests flip to C3b
   and C3c"*. Its §"What it obliges", first bullet, verbatim — **this is the write set** (§Write set
   copies it and adds nothing):

   ```text
   The planner cuts the fix slice as one dated Work-plan delta to PL-1267 (Lean P2 L5), with this record as its decision. Its write set: backend/src/app/platform/rating_versions.py (draft_change_summary_for :1329-1402, _pins_by_slug deleted); backend/src/app/platform/change_summary.py (the pure pairing, per RL-1498 DP-E1-4's placement, the sort and _table_line); packages/model-schema/src/model_schema/rating.py (RateTableChange.step_id); docs/contracts/openapi/generated.json (regenerated); the two test files; 03 (T1, T2); the slice's LG-. The executor binds test-driven-development, python-test, spec-change, contract-schema/contract-guard if the regenerated contract is guarded, dev-commands and git-hygiene.
   ```

   (Backticks around paths are dropped in this block; the record has them.) Its second bullet:
   *"The fix slice applies T1 and T2 verbatim, shows R1 to R7 and U1 and U2 red by the causes
   above before the code, keeps G1 and G2 green unedited, and runs the broken-input proof."*
2. **The confirmation** — the maintainer's (by delegation) entry "2026-10-14 09:42:05 BST — RL
   9996 (DP-P1) CONFIRMED as drafted; fix slice to be cut now; G2 conditional; SL-[…] fact
   corrected (re lead 09:41:01)" (the elided id is an unminted slice id in the entry header, elided so check 32 does not read it as a citation) (`channel/to-lead.md`), items 1 to 3 in their operative lines:

   ```text
   1. **RL 9996 @0d8f1288 (tree 591cee55): CONFIRMED, no amendment.** [...] Mint it in the next docs batch.
   2. **Fix slice: cut it NOW.** The planner writes the PL-1267 dated delta (Lean P2 L5), with ids from 8000–8299. The write set is exactly RL 9996 "What it obliges". At its ACK I check generated.json request AND response shapes (step_id nullable, optional).
   3. **G2 sequencing (yours, conditioned on the sl1543-prep read):** if E1's version pins two versions of one slug against an approved baseline, the fix slice JOINS the G2 path and merges before SL-1543. SL-1543 must not change E1's `expect=200`, re-order the journey to dodge the guard, or skip E1 (no faked step, as in my 12 Oct rulings). If E1 is not affected, the fix slice runs in parallel and is off the G2 path. Report the read and the decision to me, with the version and pins E1 drafts.
   ```

3. **The lead's dispatch of this plan** — the lead's from-lead entry "2026-10-14 09:42:42 BST"
   (`channel/from-lead-2026-10-09.md`), item (1): *"cut the fix slice NOW (PL 8002 + SL 8003
   reserved; planner-dpp1fix); G2 rule: if E1 pins two versions of one slug vs an approved
   baseline, the fix slice joins G2 and merges before SL-1543 (no edit to E1 expect=200, no
   re-order, no skip) — sl1543-prep's E1 read pending."*
4. **The E1 read, and the sequencing it decides** — the lead's from-lead entry "2026-10-14
   09:44:28 BST" (`channel/from-lead-2026-10-09.md`), item (1), verbatim:

   ```text
   (1) E1 READ (executor-sl1543-prep, read-only, at main 36e2610a): TODAY E1 passes the SL-1678 guard — RV3 pins built at examples/fremtpl2/journey.py:653-658 from `table_refs` (dict keyed by factor; edits REPLACE the ref at :373 and :401; :728 asserts len(pins.rate_tables) == len(factors)); baseline = seed approved rating_version:fremtpl2-demo@1 (journey.py:1038), one seed @1 ref per slug. UNDER PL-1542 Task 3 B1 (a second `table` step on each seeded table's seed-origin version; check_step_refs_pinned requires every referenced table pinned) RV3 pins e.g. region@1 AND region@2 → `_pins_by_slug` (rating_versions.py:1405) raises 409 at the change-summary draft (:1335-1378) because a baseline exists → E1 expect=200 FAILS. Per the maintainer's 09:42:05 (3): the RL 9996 fix slice (SL 8003) JOINS G2 and merges BEFORE SL-1543. Open sub-question: whether Pins/create_rating_version dedupes IDENTICAL refs (else the seed baseline under B1 could trip it too) → to planner-dpp1fix as a red.
   ```

   and the maintainer's (by delegation) entry "2026-10-14 09:45:05 BST — PL 9997 DP-1..5 RULED;
   SL-1543 severity response RULED (amended: no `_minor` name); E1 → SL 8003 on the G2 path
   CONFIRMED (re lead 09:43:40, 09:44:28)" (`channel/to-lead.md`), its item (C), verbatim:

   ```text
   **(C) E1:** my 09:42:05 (3) condition is MET by your read (B1 → RV3 pins region@1 + region@2 against approved fremtpl2-demo@1 → `_pins_by_slug` 409 → E1 expect=200 fails). SL 8003 is ON the G2 path and merges BEFORE SL-1543. Identical-ref dedupe: a red in SL 8003, as you said. **Send a revised G2 ETA** with SL 8003 in series (it was about 1 executor-day per PL-1677 :157), together with the #1297 ETA.
   ```

   The gate-1 order, the maintainer's (by delegation) entry "2026-10-14 09:46:40 BST — ETA
   received: train timings accepted as working figures; G2 and exit figures NOT adopted as stated;
   three orders (re lead 09:46:06)", item 1: *"the gate-1 series SL-[…] → SL-[…] → SL 8003 →
   SL-1543 → SL-[…]"*, accepted there as a working estimate (the three elided ids are slice ids
   not yet minted on `origin/main`, elided so check 32 does not read them as citations: the
   WK-1178 import-route slice of #1297, and WK-673's FD-1660 guard and fix slices).

## Goal

`GET /api/v1/rating-versions/{id}/change-summary-draft` answers every pin set on a version with an
algorithm and pins, and its rate-table entries name every version one side pins and the other does
not, paired as RL-9996's two passes pair them: through the `table` step that names them, by
`step_id`; then a pin difference no step entry names, by slug only where it is the one such ref on
each side. Each entry carries a new optional `step_id`. SL-1678's 409 guard is gone, its three
tests flipped to the cases RL-9996 names C3b and C3c. FR-242 carries T1 and the §5.1 row carries
T2. `FD-1679`'s remaining limb, DP-P1, is discharged at the slice's merge.

## Status

The status is the `status:` field in the header, and nothing else. The plan is filed `draft`: DP-1 to DP-5 are all ruled (the maintainer (by delegation), "2026-10-14 10:00:17 BST" (B); the Decision points table's "Ruled" column); DP-3 (G2 membership) is decided: SL-8003 joins G2 (Context entry 4). None changes the write set. The slice PR's first commit sets the plan `active`, as for `PL-1677`.

## Activation needs, each with its state at `36e2610a`

1. **RL-9996 minted.** **OPEN**: the ruling is on `origin/rl-9996-dpp1-2026-10-14` under a working
   id; the maintainer's (by delegation) 09:42:05 item 1: *"Mint it in the next docs batch."* The
   slice applies T1 and T2 with the minted id in place of `<RL>`.
2. **This delta ACKed and minted** (PL-8002 and SL-8003 under minted ids), with the ACK's
   `generated.json` request-and-response check (Context entry 2, item 2) run on the slice's PR, not
   on this plan, since this plan changes no contract (Acceptance 6 is the command). **OPEN.**
3. **DP-3 decided by the lead** on the sl1543-prep read of E1 (Context entry 2, item 3). **MET**:
   joins G2, the lead's from-lead "2026-10-14 09:44:28 BST" item (1), confirmed by the maintainer's
   (by delegation) "2026-10-14 09:45:05 BST" item (C) (Context entry 4; §Sequencing).
4. **No in-flight writer on the write set, or the dispatch record names the definitions.**
   Re-checked by the lead at the GO. At 2026-10-14 09:46 BST (`gh pr list --state open` and
   three-dot `git diff --name-only origin/main...<head>` per branch) the shared paths were:
   `docs/contracts/openapi/generated.json` on #1300, #1301, `origin/sl-1683-wk1178-import-200-typing`
   @`e0a5726e` and `origin/sl-1543-prep-on-1300` @`c5bc231d`; `docs/specs/03-rating-engine.md` on
   #1298, #1301, `origin/sl-1683-wk1178-import-200-typing` and `origin/sl-1695-wk673-fd1660-guard`
   @`b6b13eee`. None of them touches `rating_versions.py`, `change_summary.py`,
   `model_schema/rating.py` or either test file. `generated.json` is regenerated after the slice's
   last re-merge of `origin/main`, never hand-merged; `03` is re-anchored by content. **OPEN until
   the GO.**
5. **A build slot and the single gate** (`RL-1445` item 1). **OPEN.**
6. **DP-5 ruled** (an identical duplicate ref). **MET**: set semantics, (a), the maintainer (by delegation), "2026-10-14 10:00:17 BST" (B). It decides R8's post-fix assert and two
   lines of `pair_rate_tables` (Task 3 Step 2); E8 (Task 2) runs whatever the ruling.

## Sequencing — G2

**SL-8003 is on the G2 path and merges before `SL-1543`.** The rule, the maintainer's (by
delegation) 09:42:05 item 3, verbatim: *"if E1's version pins two versions of one slug against an
approved baseline, the fix slice JOINS the G2 path and merges before SL-1543. SL-1543 must not
change E1's `expect=200`, re-order the journey to dodge the guard, or skip E1 (no faked step, as in
my 12 Oct rulings). If E1 is not affected, the fix slice runs in parallel and is off the G2 path."*
Its condition is met: the lead's from-lead 09:44:28 item (1), *"UNDER PL-1542 Task 3 B1 […] RV3
pins e.g. region@1 AND region@2 → `_pins_by_slug` (rating_versions.py:1405) raises 409 at the
change-summary draft (:1335-1378) because a baseline exists → E1 expect=200 FAILS. Per the
maintainer's 09:42:05 (3): the RL 9996 fix slice (SL 8003) JOINS G2 and merges BEFORE SL-1543"*;
confirmed by the maintainer's (by delegation) 09:45:05 item (C): *"SL 8003 is ON the G2 path and
merges BEFORE SL-1543."* Gate-1 order as a working estimate (09:46:40 item 1, Context entry 4):
SL-8003 is third of five, after the WK-1178 import-route slice and WK-673's FD-1660 guard slice, and
before `SL-1543`. This plan reads none of the journey itself; the E1 facts are the
lead's read, quoted.

## Scope and requirements, each id individually

- `03` **FR-242** (the change summary, drafted from the structural and rate-table diffs): its
  drafting limb gains RL-9996's pairing rule (T1) and loses SL-1678's refusal (T2). FR-242 carries
  no dated amendment at `36e2610a` (`03-rating-engine.md:142`).
- `03` **FR-219** (the structural diff): read only. Its step pairing by `step_id` (`_diff_steps`,
  `packages/model-schema/src/model_schema/rating.py:896`) is the pairing pass 1 reuses.
- `03` **FR-231** (the unweighted cell diff) and **FR-232** (`pending` for a parquet side): read
  only; each paired entry still carries one or the other, as today.
- `03` **FR-237** (exact pins): read only; whether a step's ref is pinned stays compile's to
  refuse (RL-9996 §"The rule", last paragraph).
- `03` **FR-1399** (pin accounting): read only; T1 applies its pin clause to the draft.
- `FD-1679` (HIGH, owner WK-673): its remaining limb, DP-P1, is discharged at the slice's merge.

## Premises, read at `36e2610a`

| # | Premise | Locator | What it says |
|---|---|---|---|
| a | The guard | `backend/src/app/platform/rating_versions.py:1405-1426` `_pins_by_slug` | `if ref.slug in by_slug:` (`:1416`) raises `PlatformError("VALIDATION_FAILED", …, 409, …)`, the detail ending `(FD-1679).` |
| b | Its two callers, the only pin reads | `rating_versions.py:1378-1379` | `before = _pins_by_slug(baseline_row.pins)`, `after = _pins_by_slug(row.pins)`, inside `async with database.session()` |
| c | The slug pairing and the diff calls | `rating_versions.py:1380-1402` | `for slug in sorted(before.keys() \| after.keys())`; `rate_tables_service.diff_needs_job(database, workspace_id, slug, new.version, old.version)` → `pending=True`; else `rate_tables_service.diff(database, workspace_id, slug, new.version, old.version, blob_store=blob_store, cache=None)` |
| d | The algorithms | `rating_versions.py:1354`, `:1374-1377` | `candidate = await _algorithm_of(…)` (404 if `None`); `previous = await _algorithm_of(…, rating_version=baseline_row)`; `structural = None if previous is None else diff_algorithms(previous, candidate)`. `_algorithm_of` returns `RatingAlgorithm \| None` (`:1192-1194`) |
| e | No baseline | `rating_versions.py:1368-1369` | `if found is None: return draft_change_summary(None, None, [])` |
| f | The docstring sentence to remove | `rating_versions.py:1336-1337` | *"Rate tables are paired by slug across the two versions' pins; two versions of one slug on either side: 409 `VALIDATION_FAILED` (FD-1679)."* |
| g | The sort and the text | `backend/src/app/platform/change_summary.py:30`, `:86-104` | `tables = sorted(rate_tables, key=lambda entry: entry.slug)`; `_table_line` renders `- {slug}: added, …`, `- {slug}: removed, …`, `- {slug}: version {from} -> {to}…`, and the pending line naming `GET /api/v1/rate-tables/{slug}@{to}/diff?against={from}` |
| h | The shape | `packages/model-schema/src/model_schema/rating.py:1174-1190` `RateTableChange` | `frozen=True, extra="forbid"`; `slug`, `from_ref`, `to_ref`, `diff`, `pending`; no `step_id` |
| i | A `table` step | `rating.py:368-373` `RatingTableStep` | `type: Literal["table"]`, `rate_table_ref: ArtifactRef` |
| j | `ArtifactRef` is hashable | `packages/model-schema/src/model_schema/refs.py:78` | `class ArtifactRef(BaseModel, frozen=True)` |
| k | The contract | `docs/contracts/openapi/generated.json` | `RateTableChange` is one schema (no `-Input`/`-Output` split), `required: ["slug"]`; its one referrer is `ChangeSummaryDraft.properties.rate_tables.items`, whose one referrer is `paths./api/v1/rating-versions/{rating_version_id}/change-summary-draft.get.responses.200`; no `requestBody` reaches either. `git grep -n 'RateTableChange\|ChangeSummaryDraft' origin/main -- backend/tests/test_contracts.py docs/contracts ':!docs/contracts/openapi/generated.json'` prints nothing, so no drift guard compares it |
| l | The frontend | `frontend/src` | `git grep -n -E 'change-summary-draft\|ChangeSummaryDraft\|RateTableChange' origin/main -- frontend/src`, outside `frontend/src/api/generated/`, prints nothing; `frontend/src/api/generated/` is VCS-ignored (`.gitignore:38`); `generate:api` is `openapi-typescript ../docs/contracts/openapi/generated.json …` (`frontend/package.json:13`) |
| m | The route tests | `backend/tests/test_rating_version_change_summary_route.py` | `pytestmark = pytest.mark.req("FR-242")` (`:37`); helpers `_run`, `_algorithm`, `_seed_table_version`, `_pins`, `_insert`, `_url`, `_save_algorithms` (`:42-147`); `_SOFTENED` (`:38`); E1 `test_wf699_e1_the_draft_is_built_from_the_approved_baseline` (`:150-204`); SL-1678's block `:387-496` (`_create_over_http`, `_approve`, `_two_versions_of_one_table`, `_assert_refused`, `test_a_candidate_pinning_two_versions_of_one_table_is_refused` parametrized `two_then_one`/`one_then_two`, `test_a_baseline_pinning_two_versions_of_one_table_is_refused`); first-version test `:498-515` |
| n | A table-step fixture exists | `backend/tests/test_rating_pin_membership_api.py:43-49` | inserts `{"step_id": "s_tbl", "type": "table", "label": "Factor", "rate_table_ref": "rate_table:unpinned-tbl@1", "key_expr": ["premium_in"], "on_miss": "error", "consumes": ["premium_in"], "produces": "factor"}` at index 1 of `_minimal_algorithm()`, and `POST /api/v1/rating-algorithms` answers 201 with `factor` consumed by nothing and the ref not existing |
| o | The unit tests | `backend/tests/test_change_summary_draft.py` | `_rv`, `_table(slug, version)`, `_changed(slug, before, after, **diff)` (`:27-41`); `RateTableDiff(changed_cells=…)`, the other fields default `None` (`rating.py:1143-1147`) |
| p | The spec texts | `docs/specs/03-rating-engine.md:142` (FR-242), `:1052` (the §5.1 row) | `:1052` ends with SL-1678's clause from `**409** \`VALIDATION_FAILED\` when the version's pins` through `(**added 2026-10-12, SL-1678, FR-242**)` |
| q | The journey's E1 | `examples/fremtpl2/journey.py:953-959` (cited by RL-9996; not re-traced here) | E1 calls the draft route with `expect=200` |
| r | No dedupe of identical refs, by reading | `packages/model-schema/src/model_schema/rating.py:70-85` `Pins`; `backend/src/app/platform/rating_versions.py:307` | `Pins.rate_tables: list[ArtifactRef] = Field(default_factory=list)`, `frozen=True, extra="forbid"`, no validator; create stores `pins=pins.model_dump(mode="json")`. Read only: E8 (Task 2) establishes it by a run |

## Decision points

| DP | Question | Options | Recommendation | Blocking | Who | Ruled |
|---|---|---|---|---|---|---|
| DP-P1 | (PL-1677's) How the summary pairs versions when a slug carries two | (a′) and the rest, in RL-9996 | — | — | **Ruled (a′)** by RL-9996 (working id), confirmed by the maintainer (by delegation), 09:42:05 item 1 | Ruled as stated in its Who cell. |
| DP-1 | What the pure pairing in `change_summary.py` returns | (a) `list[RateTableChange]` with `diff` `None` and `pending` `False`; the I/O caller in `rating_versions.py` fills `diff` or `pending` on each entry with both refs by `model_copy(update=…)`; (b) a new internal pair type (step id, slug, two refs) that the caller turns into `RateTableChange` | **(a).** `CLAUDE.md` §2: *"Nobody hand-writes a shape that already exists in `model-schema`"*; (b) is a second shape of the same entry. (a) keeps the pairing pure and testable without a database, as `RL-1498` DP-E1-4 places it, and the caller's loop stays the one place that does I/O | no | the planner (design choice; the lead may overrule) | **Ruled (a)**, the maintainer (by delegation), "2026-10-14 10:00:17 BST" (B): the pairing returns `RateTableChange` without `diff`, the caller fills it via `model_copy`; one shape. |
| DP-2 | SL-1678's three test functions after the flip | (a) keep the functions and their fixtures, replace the asserts, and **rename** them to what they now assert; the `LG-` records old name → new name and the old asserts; (b) keep the names, replace the asserts | **(a).** A name saying "is refused" over a 200 assert is a false label; RL-9996 asks for *"same fixtures, new asserts"* and *"recorded in the fix slice's `LG-`"*, which (a) does. `_assert_refused` loses its last caller and is deleted, recorded in the same `LG-` line | no | the planner (design choice; the lead may overrule) | **Ruled (a)**, the maintainer (by delegation), "2026-10-14 10:00:17 BST" (B): rename the flipped tests, old → new recorded in the `LG-`. |
| DP-3 | **G2 membership.** Does the fix slice join the G2 path and merge before `SL-1543`? | (a) joins G2 and merges before `SL-1543`; (b) runs in parallel, off the G2 path — the maintainer's (by delegation) 09:42:05 item 3 picks between them on the E1 read (§Sequencing, verbatim) | — (not the planner's) | — | **Decided (a)** by the lead, from-lead "2026-10-14 09:44:28 BST" item (1), on the 09:42:05 rule; confirmed by the maintainer (by delegation), "2026-10-14 09:45:05 BST" item (C) | Ruled as stated in its Who cell. |
| DP-4 | The sort position of a null `from_ref` or `to_ref` (RL-9996 rule 4 sorts *"by the `from_ref` and `to_ref` strings"* and is silent on null) | (a) null sorts as the empty string, so before any ref; (b) null sorts after every ref | **(a).** It is total and needs no sentinel, and a one-sided entry is already marked by its text (*"added"* / *"removed"*). R4 asserts its three entries as a set, so neither option makes a red depend on it; U2 fixes only what RL-9996 fixes (step entry before pin entry) | no | the planner (design choice; the lead may overrule) | **Ruled (a)**, the maintainer (by delegation), "2026-10-14 10:00:17 BST" (B): a null ref sorts as `""`, first (consistent with RL 9996 rule 4). |
| DP-5 | **An identical duplicate ref:** one side's `pins.rate_tables` lists the same `slug@version` twice (premise r). What does the draft do? RL-9996 is silent: pass 2 defines a pin difference as *"a ref in `pins.rate_tables` on one side and not on the other"* and rule 2 counts *"exactly one ref removed and exactly one added"*, but neither says whether a ref listed twice is one pin or two, and its cases C1–C5 never list one twice. On main the guard refuses it (premise a: `:1416` compares the slug only, so the second, identical ref raises 409) | (a) **one pin**: the draft reads each side's pins as a set; a ref listed twice is the ref once, and duplication alone makes no entry; create unchanged. (b) **a multiset**: a ref listed twice on one side and once on the other is a pin difference, and gets a pin entry of its own (`step_id` null, no diff). (c) **refuse at create**: `POST /api/v1/rating-versions` refuses a pin list carrying one ref twice (a new 422 on create; a `Pins` validator would refuse it at every read of stored rows too). (d) **normalise at create**: create stores each ref once; rows already stored keep their duplicates, so the draft still needs (a) or (b) for them | **None: the lead's instruction is not to pick.** Trade-offs for the ruler: (a) matches FR-1399's exact-ref comparison and is what Task 3 Step 2's sketch does (its two `set(…)` lines, marked); it is silent towards an author who listed a ref twice. (b) names a difference that changes nothing an approver acts on. (c) narrows create, which `RL-1538` kept permissive for two **versions**, and may refuse the B1 baseline (Context entry 4) if the journey builds pins per step; it is a spec change outside RL-9996's T1/T2. (d) changes stored data and leaves the old rows to (a) or (b) | **yes** (activation need 6) | **the decision-maker**, as an `RL-` against WK-673's plan, extending RL-9996 (the lead's instruction, 2026-10-14 09:44:28 BST item (1): *"Open sub-question: whether Pins/create_rating_version dedupes IDENTICAL refs"*; the maintainer's (by delegation) 09:45:05 item (C): *"Identical-ref dedupe: a red in SL 8003"*) | **Ruled (a), set semantics**, the maintainer (by delegation), "2026-10-14 10:00:17 BST" (B), as a READING of RL 9996 pass 2, not an extension; no sibling `RL-`. RL 9996 pass 2 defines a pin difference as *"a ref in `pins.rate_tables` on one side and not on the other (exact `slug@version`, as FR-1399 compares)"*, a set-membership predicate; "exactly one ref removed and one added" counts DISTINCT refs. So `[X@1, X@1]` against `[X@1]` is no difference, and `[X@1, X@1]` → `[X@2]` is one entry X 1 → 2 with the cell diff. Added red: R9 (Task 2). Create and storage are NOT changed (no dedupe-on-write, no refusal): that is a spec change for another slice. If the reds show another consumer mishandles duplicates, file it then. |

## Write set

Copied from RL-9996 "What it obliges" (Context entry 1). Nothing is added.

| Path | What changes | Task |
|---|---|---|
| `backend/src/app/platform/rating_versions.py` `draft_change_summary_for` (`:1329-1402`) | reads the two pin lists, calls the pure pairing, fills each paired entry's `diff` or `pending`; the docstring sentence at `:1336-1337` replaced | 3 |
| `backend/src/app/platform/rating_versions.py` `_pins_by_slug` (`:1405-1426`) | **deleted**, with its refusal | 3 |
| `backend/src/app/platform/change_summary.py` | the pure pairing `pair_rate_tables` (RL-9996 rules 1–3), the sort (rule 4, replacing `:30`), `_table_line` (rule 5) | 3 |
| `packages/model-schema/src/model_schema/rating.py` `RateTableChange` (`:1174-1190`) | gains `step_id: str \| None = None`; the docstring says what null means (T3) | 3 |
| `docs/contracts/openapi/generated.json` | regenerated by `scripts/generate-contracts.py`, never hand-edited (T3) | 4 |
| `backend/tests/test_rating_version_change_summary_route.py` | R1–R9, E8, the flipped SL-1678 tests (R3), a table-step fixture; E1 (G1) and the first-version test (G2) unedited | 2 |
| `backend/tests/test_change_summary_draft.py` | U1, U2 | 2 |
| `docs/specs/03-rating-engine.md` FR-242 (`:142`) and the §5.1 change-summary-draft row (`:1052`) | T1 appended; T2 strikes SL-1678's clause and appends the struck note | 1 |
| `docs/roadmap.md` SL-8003 row; `docs/ledgers/LG-<working id>` | status lines and the slice ledger (L1 (a′)) | 0, 5 |

**Not written:** `backend/src/app/api/models.py` (the route keeps `problems(401, 403, 404, 409,
422)`: 409 stays declared for `RATING_VERSION_UNPINNED`, so the route's response list does not
move); `examples/fremtpl2/journey.py`; any file under `frontend/` (premise l: the frontend change is
the VCS-ignored regenerated client only); `packages/pricing-core/`; `docs/findings/` (FD-1679's
register line is the lead's or the minter's, RL-9996 "What it obliges", third bullet).

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch, cut from
  `origin/main` **after RL-9996 is minted** (activation need 1). `uv sync --all-packages`.
- [ ] Re-read premises a–p at the slice base and record each in the `LG-` with its locator. If
  `_pins_by_slug` or the loop at premise c no longer reads as stated, STOP to the lead.
- [ ] Record the minted ids that replace `<RL>` (RL-9996's) and `<SL>` (this slice's), and the
  date that replaces `<date>`.
- [ ] `gh pr list --state open`, and grep `to-lead.md` for entries since 2026-10-14 09:42:05 BST
  that rule on `RL 9996`, `DP-P1`, `FD-1679`, `change summary`, `step_id`, an identical duplicate ref, DP-1 to DP-5 or G2.
  Name the SHA and the entries read; use the ruled answer where one exists.
- [ ] Commit the `LG-` scaffold, the SL row's `active` line and this plan's `active` status (L1
  (a′)).

### Task 1: Spec — T1 and T2, verbatim

**Files:** Modify `docs/specs/03-rating-engine.md:142` (FR-242) and `:1052` (§5.1 row).

- [ ] **T1.** Append to FR-242's requirement cell, after `edited by the actuary.`, this text from
  RL-9996 §"DP-T", with `<date>`, `<RL>` filled (one cell, no line break):

  ```text
  *(Amended <date>, WK-673, <RL>, `FD-1679`.)* **How the draft pairs rate tables.** The drafted summary has one entry per rate-table change. For each `step_id` that is a `table` step in the baseline's algorithm or the version's, where its rate-table reference differs between the two: if both references name the same rate table, one entry carries the `step_id`, both references and their cell diff (FR-231). Otherwise each named table is its own entry with the `step_id` and its one reference. Steps are paired by `step_id` only, as FR-219 pairs them. A rate-table pin on one side only that no such entry names is an entry without a `step_id`. Where a rate table has exactly one such pin removed and one added, they are one entry with their cell diff; otherwise each pin is its own entry, without a cell diff. Without the baseline's algorithm, every entry is of the second kind. Two versions of one rate table pinned on either side are valid (`RL-1538`): every version is named, none is dropped, and the draft is never refused for its pins.
  ```

- [ ] **T2.** In the row at `:1052`, wrap SL-1678's clause in `~~…~~`, from `**409**
  \`VALIDATION_FAILED\` when the version's pins` through `(**added 2026-10-12, SL-1678,
  FR-242**)`, and append after it, with `<date>`, `<SL>`, `<RL>` filled:

  ```text
  (**struck <date>, <SL>, <RL>, `FD-1679`:** the draft pairs rate tables through the `table` step that names them, FR-242's <date> amendment, and is refused for no pin set. Each rate-table entry carries a `step_id`, null for a pin no step entry names.)
  ```

- [ ] Diff the two applied texts against RL-9996's T1 and T2 at the minted ruling (not this plan's
  copy): `diff` of the quoted blocks prints nothing but the filled placeholders. Record it in the
  `LG-`.
- [ ] Commit `docs(specs): FR-242's pairing rule and the struck FD-1679 refusal — <SL> (<RL>)`.

### Task 2: The reds — R1 to R9, U1, U2, each red by its cause, and E8

**Files:** Test `backend/tests/test_rating_version_change_summary_route.py`,
`backend/tests/test_change_summary_draft.py`.

**Interfaces:**
- Consumes: the route test file's helpers (premise m); `_minimal_algorithm` (imported at `:20`).
- Produces: `RateTableChange.step_id: str | None` (Task 3 adds it) and the text form
  `- <slug> (step <step_id>): …` (Task 3).

- [ ] **Step 1: The fixture.** Add, beside `_algorithm`, without editing `_minimal_algorithm`
  (RL-9996 §"Red tests"), modelled on premise n:

  ```python
  def _table_algorithm(version: int, tables: dict[str, ArtifactRef]) -> dict[str, Any]:
      """`_minimal_algorithm` with one `table` step per `step_id -> rate table ref`, inserted as
      `test_rating_pin_membership_api.py` inserts one; nothing consumes their outputs."""
      body = _minimal_algorithm()
      body["version"] = version
      for offset, (step_id, ref) in enumerate(sorted(tables.items())):
          body["steps"].insert(
              1 + offset,
              {
                  "step_id": step_id, "type": "table", "label": step_id,
                  "rate_table_ref": str(ref), "key_expr": ["premium_in"], "on_miss": "error",
                  "consumes": ["premium_in"], "produces": f"factor_{step_id}",
              },
          )
      return body


  def _entries(body: dict[str, Any]) -> list[tuple[Any, ...]]:
      """Each entry as (step_id, from_ref, to_ref, has a diff); `.get` so main reads None."""
      return [
          (e.get("step_id"), e["from_ref"], e["to_ref"], e["diff"] is not None)
          for e in body["rate_tables"]
      ]
  ```

  Premise n proves one unconsumed table step saves (201); two (C1, C2) are not proven. If
  `_save_algorithms` answers anything but 201 for a `_table_algorithm` body, that is a fixture
  fault, not a red: fix the fixture (for example consume the factor) before Step 3.

  Each route test below: `_run(grant("analyst"))`; `headers = _headers(principal, workspace_id)`;
  `slug = _table_slug()`; seed versions with `_seed_table_version` (`one` from `_LEVELS`, `two` from
  `_SOFTENED`, and where a third is needed `three` from a new module constant
  `_RAISED = {"driver_age_band": [("17-20", 1.92), ("21-24", 1.50), ("25-29", 1.12)]}`); refs
  `X1`, `X2`, `X3` are `ArtifactRef(type="rate_table", slug=slug, version=one|two|three)`; save the
  two algorithms with `_save_algorithms`; insert the baseline with `_insert(…, version=1,
  algorithm_version=1, pins=…, approved=True)` and the candidate with `_insert(…, version=2,
  algorithm_version=2, pins=…)`; `body = api_client.get(_url(candidate), headers=headers)`.
  Every route test first asserts `response.status_code == 200, response.text`.

- [ ] **Step 2: Write the reds.** Names are the executor's; the case, the asserts and the cause
  on main are RL-9996's (§"Red tests"; §"The cases").

  | Test | Case | Algorithms (1 → 2) and pins (baseline → candidate) | Asserts after the fix | Red on main by — expected failure text |
  |---|---|---|---|---|
  | R1 | C1 | `{t: X1}` → `{t: X2, t_seed: X1}`; `[X1]` → `[X2, X1]` | `_entries(body) == [("t", str(X1), str(X2), True), ("t_seed", None, str(X1), False)]`; the `t` entry's `diff == _diff_ready(api_client, f"/api/v1/rate-tables/{slug}@{two}/diff", {"against": str(one)}, headers).json()` | the guard: `AssertionError` on the status line, `assert 409 == 200`, the response text carrying `"code":"VALIDATION_FAILED"` and `FD-1679` |
  | R2 | C2 | `{t: X2, t_seed: X1}` → `{t: X3, t_seed: X1}`; `[X2, X1]` → `[X3, X1]` | `_entries(body) == [("t", str(X2), str(X3), True)]`; its `diff` equals the diff route's for `{slug}@{three}` against `two` | the guard: `assert 409 == 200`, text as R1 |
  | R3 (flip) | C3b, both orders; C3c | SL-1678's fixtures unchanged (`_algorithm(1)`, `_algorithm(2, extra_step=True)`, no `table` step): C3b `[X1]` → `[X2, X1]` and `[X1, X2]`; C3c `[X1, X2]` → `[X2]` | C3b: `_entries(body) == [(None, None, str(X2), False)]`; C3c: `_entries(body) == [(None, str(X1), None, False)]` | the guard: `assert 409 == 200`, text as R1 |
  | R4 | C3d | `_algorithm(1)` → `_algorithm(2, extra_step=True)`; `[X1, X2]` → `[X3]` | `sorted(_entries(body), key=str) == sorted([(None, str(X1), None, False), (None, str(X2), None, False), (None, None, str(X3), False)], key=str)` | the guard: `assert 409 == 200`, text as R1 |
  | R5 | C3e | `{t: X1}` → `{t: X2}`; `[X1]` → `[X2, X3]` | `_entries(body) == [("t", str(X1), str(X2), True), (None, None, str(X3), False)]` | the guard: `assert 409 == 200`, text as R1 |
  | R6 | C4b | `{t: X1}` → `{u: X2}`; `[X1]` → `[X2]` | `len(body["rate_tables"]) == 2`, then `_entries(body) == [("t", str(X1), None, False), ("u", None, str(X2), False)]` | slug pairing: `assert 1 == 2` on the length (main's one entry `X one → two` with a cell diff) |
  | R7 | C4a | a second slug `Y = _table_slug()` seeded once (`y1`); `{t: X1}` → `{t: Y1}`; `[X1]` → `[Y1]` | `len(body["rate_tables"]) == 2`, then `[e.get("step_id") for e in body["rate_tables"]] == ["t", "t"]`, then the two entries by slug: X `(str(X1) → None)`, Y `(None → str(Y1))` | **red only by the new field**: `assert [None, None] == ['t', 't']`; the length assert passes on main |

  In `backend/tests/test_change_summary_draft.py`:

  - **U1** — `entry = RateTableChange(slug="age", step_id="t", from_ref=_table("age", 1),
    to_ref=_table("age", 2), diff=RateTableDiff(changed_cells=1))`;
    `draft = draft_change_summary(_rv(1), AlgorithmDiff(), [entry])`; assert
    `"- age (step t): version 1 -> 2, 1 cell(s) changed." in draft.text.splitlines()`; and
    `_changed("age", 1, 2, changed_cells=1)` (no `step_id`) renders
    `"- age: version 1 -> 2, 1 cell(s) changed."` as today. **Red on main by:**
    `pydantic_core._pydantic_core.ValidationError: 1 validation error for RateTableChange` /
    `step_id` / `Extra inputs are not permitted` at the constructor.
  - **U2** — `step = RateTableChange(slug="age", step_id="t", from_ref=_table("age", 1),
    to_ref=_table("age", 2), diff=RateTableDiff(changed_cells=1))`;
    `pin = RateTableChange(slug="age", from_ref=None, to_ref=_table("age", 5))`;
    `draft = draft_change_summary(_rv(1), AlgorithmDiff(), [pin, step])`; assert
    `draft.rate_tables == [step, pin]`. **Red on main by:** the same `ValidationError` (the step
    entry cannot be built on main).

  The identical duplicate ref (DP-5; the lead's 09:44:28 item (1), the maintainer's 09:45:05 item
  (C)), in the route test file, through `_two_versions_of_one_table`'s fixtures:

  - **E8 — establishes whether `Pins` or create dedupe an identical ref (not a red).**
    `first = _create_over_http(api_client, headers, algorithm_version=1, pins=_pins(one, one))`
    (the helper asserts the 201); then, in `database.session()`,
    `row = await session.get(RatingVersionRow, first)` and assert
    `row.pins["rate_tables"] == [str(one), str(one)]`. **Expected on main, by reading (premise r):
    PASSES** — nothing dedupes. If it fails with `[str(one)]`, something dedupes: STOP to the
    lead, because DP-5 and R8 then change. Keep E8 after the fix; it pins the stored form.
  - **R8 — a baseline listing one ref twice, as the B1 baseline may.** Algorithms
    `_table_algorithm(1, {"t": X1, "t_seed": X1})` → `_table_algorithm(2, {"t": X2, "t_seed": X1})`;
    baseline pins `_pins(X1, X1)` (approved, via `_insert`), candidate pins `_pins(X2, X1)`.
    **Red on main by the guard on an identical ref:** `assert 409 == 200`, the response text naming
    `FD-1679` and `at versions {one} and {one}` (the detail's two version numbers equal). **After
    the fix, under DP-5 (a):** `_entries(body) == [("t", str(X1), str(X2), True)]`. Under any other
    ruling the ruling states the assert; the red's cause on main is the same. Not counted in the
    broken-input proof.
  - **R9 — an identical duplicate ref on the candidate side only (DP-5 (a), set semantics; added by the
    maintainer's (by delegation) "2026-10-14 10:00:17 BST" (B)).** The same algorithm on both sides
    (no step change); baseline pins `_pins(X1)` (approved, via `_insert`), candidate pins `_pins(X1, X1)`.
    **Red on main by the guard on an identical ref:** `assert 409 == 200`, the detail naming `FD-1679`.
    **After the fix:** 200 and `_entries(body) == []` (no rate-table entry: a ref listed twice is the
    ref once). Create and storage are unchanged, so E8 still passes. Not counted in the broken-input
    proof.

  Delete `_assert_refused` (no caller after the flip, DP-2 (a)); rewrite the block comment at
  `:387-389` to say the summary pairs by step and by unique slug (RL-9996), and that create still
  accepts such pins.

- [ ] **Step 3: Run them on the base, before any code change:**
  `uv run pytest -q backend/tests/test_rating_version_change_summary_route.py backend/tests/test_change_summary_draft.py`.
  Expected: R1–R9 and U1–U2 FAIL, each with the failure text in the table (R8: as stated under it),
  and **every other test in both files PASSES**, including E8, E1 (G1) and the first-version test
  (G2). Paste each failure
  line into the `LG-`. A red that fails for another reason (a fixture, 401, 404, a save refusal of
  a `_table_algorithm` body, a status of 409 whose text does not name `FD-1679`) is not a red: fix
  the test first (`README.md` convention 2).
- [ ] **Step 4: Commit** `test(rating): RL-9996's pairing cases, red on main by their causes — <SL>`.

### Task 3: The pairing, the shape and the guard's removal

**Files:** Modify `packages/model-schema/src/model_schema/rating.py:1174-1190`,
`backend/src/app/platform/change_summary.py`, `backend/src/app/platform/rating_versions.py:1329-1426`.

**Interfaces:**
- Produces: `RateTableChange.step_id: str | None = None`;
  `change_summary.pair_rate_tables(previous: RatingAlgorithm | None, candidate: RatingAlgorithm, before: Sequence[ArtifactRef], after: Sequence[ArtifactRef]) -> list[RateTableChange]`
  (entries carry no `diff`, `pending` `False`; DP-1 (a)).

- [ ] **Step 1: The shape (T3).** In `RateTableChange`, after `slug: str`, add
  `step_id: str | None = None`, and extend the docstring: *"`step_id` is the `table` step whose
  rate-table reference this entry pairs (FR-219's pairing by `step_id`); `None` for a pin no step
  entry names, paired by slug only when it is the one such ref on each side (RL-9996)."*
- [ ] **Step 2: The pure pairing**, in `change_summary.py`, exported in `__all__`:

  ```python
  def pair_rate_tables(
      previous: RatingAlgorithm | None,
      candidate: RatingAlgorithm,
      before: Sequence[ArtifactRef],
      after: Sequence[ArtifactRef],
  ) -> list[RateTableChange]:
      """RL-9996's two passes over the baseline's and the version's rate-table pins.

      Pass 1 pairs each `table` step by `step_id`, as FR-219 does; pass 2 pairs a pin
      difference no step entry names by slug only where it is the one such ref on each side.
      Without the baseline's algorithm there is no step entry. No entry carries a diff.
      """
      entries: list[RateTableChange] = []
      named: set[ArtifactRef] = set()
      if previous is not None:
          old_steps, new_steps = _table_refs(previous), _table_refs(candidate)
          for step_id in sorted(old_steps.keys() | new_steps.keys()):
              old, new = old_steps.get(step_id), new_steps.get(step_id)
              if old == new:
                  continue
              if old is not None and new is not None and old.slug == new.slug:
                  entries.append(
                      RateTableChange(slug=old.slug, step_id=step_id, from_ref=old, to_ref=new)
                  )
              else:
                  if old is not None:
                      entries.append(RateTableChange(slug=old.slug, step_id=step_id, from_ref=old))
                  if new is not None:
                      entries.append(RateTableChange(slug=new.slug, step_id=step_id, to_ref=new))
              named.update(ref for ref in (old, new) if ref is not None)
      # The two set(…) reads are DP-5 (a): a ref listed twice is one pin. Change them, and R8's
      # assert, if the decision-maker rules otherwise.
      removed = (set(before) - set(after)) - named
      added = (set(after) - set(before)) - named
      for slug in sorted({ref.slug for ref in removed | added}):
          gone = [ref for ref in removed if ref.slug == slug]
          came = [ref for ref in added if ref.slug == slug]
          if len(gone) == 1 and len(came) == 1:
              entries.append(RateTableChange(slug=slug, from_ref=gone[0], to_ref=came[0]))
          else:
              entries += [RateTableChange(slug=slug, from_ref=ref) for ref in gone]
              entries += [RateTableChange(slug=slug, to_ref=ref) for ref in came]
      return entries


  def _table_refs(algorithm: RatingAlgorithm) -> dict[str, ArtifactRef]:
      """Each top-level `table` step's rate-table ref by `step_id`; the draft never inlines."""
      return {
          step.step_id: step.rate_table_ref
          for step in algorithm.steps
          if isinstance(step, RatingTableStep)
      }
  ```

  Import `RatingAlgorithm` (`rating.py:555`) and `RatingTableStep` (`rating.py:368`) from
  `model_schema.rating`; the route test file already imports `RatingAlgorithm` from there (`:35`).
- [ ] **Step 3: The sort and the text.** Replace `:30` with
  `tables = sorted(rate_tables, key=_entry_order)` and add:

  ```python
  def _entry_order(entry: RateTableChange) -> tuple[str, int, str, str, str]:
      """RL-9996 rule 4: slug, step entries before pin entries, step_id, from_ref, to_ref;
      a null ref sorts as the empty string (DP-4 (a))."""
      return (
          entry.slug,
          0 if entry.step_id is not None else 1,
          entry.step_id or "",
          "" if entry.from_ref is None else str(entry.from_ref),
          "" if entry.to_ref is None else str(entry.to_ref),
      )
  ```

  In `_table_line`, render the label `slug if entry.step_id is None else f"{slug} (step {entry.step_id})"`
  in the three `- {…}:` prefixes (rule 5); the pending line's
  `GET /api/v1/rate-tables/{slug}@…` keeps the bare `slug`. Update `draft_change_summary`'s
  docstring sentence *"The rate-table entries are those whose pinned version differs, one side only
  included."* to name the two passes.
- [ ] **Step 4: The caller.** In `draft_change_summary_for`, replace `:1378-1402` so that, inside
  the session, it reads `before = _rate_table_pins(baseline_row.pins)` and
  `after = _rate_table_pins(row.pins)`, and after it:

  ```python
  changes: list[RateTableChange] = []
  for entry in pair_rate_tables(previous, candidate, before, after):
      old, new = entry.from_ref, entry.to_ref
      if old is None or new is None:
          changes.append(entry)
      elif await rate_tables_service.diff_needs_job(
          database, workspace_id, new.slug, new.version, old.version
      ):
          changes.append(entry.model_copy(update={"pending": True}))
      else:
          diff = await rate_tables_service.diff(
              database, workspace_id, new.slug, new.version, old.version,
              blob_store=blob_store, cache=None,
          )
          changes.append(entry.model_copy(update={"diff": diff}))
  return draft_change_summary(baseline_ref, structural, changes)
  ```

  Replace `_pins_by_slug` (`:1405-1426`) by:

  ```python
  def _rate_table_pins(pins: dict[str, Any] | None) -> list[ArtifactRef]:
      """A version's pinned rate tables, in stored order; a version without pins pins none."""
      return [] if pins is None else list(Pins.model_validate(pins).rate_tables)
  ```

  Replace the docstring sentence at `:1336-1337` with *"Rate tables are paired by
  `change_summary.pair_rate_tables` (RL-9996): through the `table` step that names them, then a
  pin no step entry names by slug where it is the one such ref on each side. No pin set is
  refused."* Import `pair_rate_tables` beside `draft_change_summary` (`:45`).
- [ ] **Step 5: Run both files:** the Task 2 Step 3 command. Expected: all pass, E1 and the
  first-version test unedited (`git diff origin/main...HEAD` shows no hunk inside `:150-204` or
  `:498-515` of the route test file).
- [ ] **Step 6: The broken-input proof** (RL-9996 §"Red tests"). Locally replace `if previous is
  not None:` in `pair_rate_tables` with `if False:` (every difference sent to pass 2); run the two
  files: R1, R2, R5 and R6 FAIL and E1 (G1) PASSES; restore, and run again green. Record both runs
  in the `LG-`.
- [ ] **Step 7:** `git grep -n 'FD-1679' -- backend/src` prints nothing; `uv run ruff check .`,
  `uv run mypy`, `uv run lint-imports` exit 0.
- [ ] **Step 8: Commit** `fix(rating): the drafted change summary pairs rate tables through the table step and refuses no pin set — <SL> (<RL>, FD-1679)`.

### Task 4: The generated contract and the frontend client

**Files:** Modify `docs/contracts/openapi/generated.json` (regenerated only).

- [ ] `uv run python scripts/generate-contracts.py`, then `--check` exits 0;
  `git diff --name-only origin/main...HEAD -- docs/contracts` prints exactly
  `docs/contracts/openapi/generated.json`.
- [ ] The request-and-response shape check (Acceptance 6) prints the expected lines; paste its
  output into the `LG-` for the maintainer's (by delegation) ACK (Context entry 2, item 2).
- [ ] `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api`, then
  `pnpm --dir frontend type-check` exits 0 and `git status --porcelain -- frontend` prints nothing
  (premise l: the client is VCS-ignored, and no frontend file reads the draft).
- [ ] Commit `chore(contracts): regenerate for RateTableChange.step_id — <SL>`.

### Task 5: The gate and the closing acts

- [ ] `python3 scripts/audit-docs.py` once in a gate-2 docs check; the full gate, both halves
  (`CLAUDE.md` §11), in the single gate slot, on `origin/main...<branch>`; the rc table in the
  `LG-`.
- [ ] Closing acts in the slice PR's last commit (L1 (a′)): SL-8003 `closed` line; the `LG-`'s
  Audit section after the auditor's verdict. FD-1679's closure and register line are the lead's or
  the minter's (RL-9996 "What it obliges", third bullet).

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root of the slice
branch.

1. **Every case answered, every version named:** R1–R9 and E8 pass:
   `uv run pytest -q backend/tests/test_rating_version_change_summary_route.py` exits 0, and the
   `LG-` shows E8 passing on the base (no dedupe; else the STOP of Task 2), DP-5's ruling quoted
   beside R8, and each of R1–R9 failing on the base with the failure text of Task 2's table (Step 3)
   and R1, R2, R5, R6 failing again on the broken-input proof (Task 3 Step 6) while E1 passes.
2. **The text and the order:** U1 and U2 pass:
   `uv run pytest -q backend/tests/test_change_summary_draft.py` exits 0; the `LG-` shows both red
   on the base by `ValidationError` (`step_id`, `Extra inputs are not permitted`).
3. **The guard is gone:** `git grep -n '_pins_by_slug\|FD-1679' -- backend/src` prints nothing;
   `git grep -n 'VALIDATION_FAILED' -- backend/src/app/platform/rating_versions.py` prints no line
   inside `draft_change_summary_for`.
4. **G1 and G2 unedited:** `git diff origin/main...HEAD -- backend/tests/test_rating_version_change_summary_route.py`
   has no hunk touching E1's body (`:150-204` at the base) or the first-version test (`:498-515`).
5. **The flip is recorded:** the `LG-` names each of SL-1678's three test functions, old name →
   new name, with its old and new asserts (DP-2).
6. **The contract, request and response:** `uv run python scripts/generate-contracts.py --check`
   exits 0; `git diff --name-only origin/main...HEAD -- docs/contracts` prints only
   `docs/contracts/openapi/generated.json`; and this prints `changed: ['RateTableChange']`,
   `required: ['slug']`, a `step_id` of `anyOf` string and null with `default` `None`,
   `split: []`, `paths unchanged: True`, `request bodies naming the draft: []`:

   ```bash
   base=$(mktemp) && git show origin/main:docs/contracts/openapi/generated.json > "$base" && python3 -c '
   import json, sys
   a = json.load(open(sys.argv[1])); b = json.load(open("docs/contracts/openapi/generated.json"))
   sa, sb = a["components"]["schemas"], b["components"]["schemas"]
   print("changed:", sorted(k for k in sa.keys() | sb.keys() if sa.get(k) != sb.get(k)))
   r = sb["RateTableChange"]; print("required:", r["required"]); print("step_id:", r["properties"]["step_id"])
   print("split:", [k for k in sb if k.startswith("RateTableChange-") or k.startswith("ChangeSummaryDraft-")])
   print("paths unchanged:", a["paths"] == b["paths"])
   def refs(o):
       if isinstance(o, dict):
           for k, v in o.items():
               yield from ([v] if k == "$ref" else refs(v))
       elif isinstance(o, list):
           for v in o: yield from refs(v)
   bodies = {x for p in b["paths"].values() for op in p.values() if isinstance(op, dict) for x in refs(op.get("requestBody", {}))}
   print("request bodies naming the draft:", sorted(x for x in bodies if "RateTableChange" in x or "ChangeSummaryDraft" in x))
   ' "$base"
   ```

7. **The frontend:** `git grep -n -E 'change-summary-draft|ChangeSummaryDraft|RateTableChange' -- frontend/src ':!frontend/src/api/generated'`
   prints nothing; `git diff --name-only origin/main...HEAD -- frontend` prints nothing;
   `pnpm --dir frontend generate:api && pnpm --dir frontend type-check` exits 0.
8. **The spec says it:** `grep -n 'How the draft pairs rate tables' docs/specs/03-rating-engine.md`
   prints FR-242's line; `grep -c '~~\*\*409\*\* `VALIDATION_FAILED` when the version' docs/specs/03-rating-engine.md`
   prints `1`; `python3 scripts/audit-docs.py` exits 0 with the slice's `LG-` minted.
9. **The gate is green on the merge tree:** the `CLAUDE.md` §11 commands, both halves, each exit 0
   against `origin/main...<slice branch>`.

## Global Constraints

- `CLAUDE.md` §2: no shape written twice (DP-1 (a)); `docs/contracts/` generated, never
  hand-edited.
- `RL-1538`: two versions of one slug are valid pins; create is not narrowed, and now the draft is
  not refused either.
- `RL-1498` DP-E1-5: `RateTableChange` keeps `from_ref` and `to_ref` by name; `step_id` is one
  optional field more, not a supersession (RL-9996 T3).
- `pricing-core` stays free of FastAPI/SQLAlchemy; no pandas. This slice does not touch it.
- One PR per slice (L1 (a′)): code, tests, spec texts, regenerated contract, SL status line, one
  `LG-`.
- `RL-1445` item 1: one full gate at a time; targeted single-file runs only outside it.
- G2: SL-8003 merges before `SL-1543` (§Sequencing; the maintainer's (by delegation) 09:42:05 item 3
  and 09:45:05 item (C)).

## Hand-off (not this plan's writes)

- **The WK-673 roadmap row** lists this delta as a Work-plan delta; the planner's charter limits
  its roadmap writes to the `SL-` rows it cuts, so that line is the lead's, as for `PL-1677`.
- **PL-1677's status.** RL-9996 "What it obliges", fourth bullet: *"PL-1677 stays `active` until
  the fix slice's plan delta records DP-P1 as ruled here. It is not edited."* This delta records it
  (§Decision points, row DP-P1). Whether `PL-1677` then moves to `closed`, and in which PR, is
  outside this plan's write set: options (a) the mint PR of this delta sets it, (b) SL-8003's
  closing PR sets it after FD-1679 closes. **Recommendation (b):** the guard `PL-1677` planned is
  removed only by SL-8003, so its purpose completes at that merge. The lead's.
- **FD-1679**: discharged at SL-8003's merge (RL-9996 "What it obliges", third bullet); its
  closure and register line are the lead's or the minter's.
- **DP-3 / G2**: decided (§Sequencing). The revised G2 ETA with SL-8003 in series is the lead's
  (09:45:05 item (C)).
- **DP-5** is ruled (the maintainer (by delegation), "2026-10-14 10:00:17 BST" (B), a reading of RL 9996 pass 2); the ruling is quoted into the slice's `LG-` at Task 0.

## Self-review

- **Ruling coverage.** RL-9996's rules 1–5 → Task 3 Steps 2–4; T1, T2 → Task 1; T3 → Task 3
  Step 1 and Task 4; R1–R9, E8, U1, U2 → Task 2; G1, G2 → Task 2 Step 3, Task 3 Step 5, Acceptance 4;
  the broken-input proof → Task 3 Step 6; the guard's removal and the flip → Task 2 Step 2, Task 3
  Step 4, Acceptance 3 and 5; `git grep FD-1679 backend/src` empty → Acceptance 3. Each of
  RL-9996's three Acceptance items → R1–R6 (item 1), R3–R5 and G1 (item 2), R1–R5 (item 3).
- **Write set.** Every path in §Write set is in RL-9996 "What it obliges"; the roadmap row and the
  `LG-` are the slice's own paperwork, named in that bullet as *"the slice's `LG-`"*. No path was
  added. `backend/src/app/api/models.py` is deliberately not in it (409 stays declared).
- **Placeholders.** `<date>`, `<RL>`, `<SL>` and the `LG-` working id are filled at execution;
  R-test names are the executor's. No other placeholder.
- **Type consistency.** `pair_rate_tables`, `_table_refs`, `_entry_order`, `_rate_table_pins` and
  `step_id` are named the same in Tasks 2–4 and Acceptance. `PlatformError` is no longer raised
  by the draft for pins.
- **Literals.** Every `file:line` was read at `36e2610a`. Not verified by a run: two table steps
  in one saved algorithm (Task 2 Step 1 says what to do if it is refused).
- **Convention 4.** `gh pr list --state open` and three-dot diffs read at 2026-10-14 09:46 BST
  (activation need 4). The to-lead entries read up to "2026-10-14 09:54:22 BST" and the from-lead
  entries up to "2026-10-14 09:54:12 BST", both read at 09:55 BST; the ones on this plan's subject
  are 09:42:05, 09:45:05 (C) and 09:46:40 item 1 (to-lead) and 09:42:42, 09:44:28 (1) and 09:53:28
  (from-lead). Task 0 re-reads both.
