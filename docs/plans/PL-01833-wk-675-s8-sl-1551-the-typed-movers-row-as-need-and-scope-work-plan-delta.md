---
id: PL-1833
family: plan
kind: map
title: WK-675 — Slice 8 (SL-1551), the dislocation views: the typed /movers row as its need and its scope, and where it is built: a dated Work-plan delta to PL-1546
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-17
owner: planner
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1546, PL-1286, PL-1501, PL-1267, SL-1551, SL-1388, RL-1504, RL-1473, FD-1796]
---

# PL-1833 — WK-675 Slice 8 (SL-1551): the typed `/movers` row as S8's need and scope (delta to PL-1546)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5. It follows
> `document-ids.md` §1.6, PL row: *"a change is one dated Work-plan delta, a new `PL-` that
> `relates:` the Work's plan"*. It changes **one row** of
> [`PL-1546`](PL-01546-wk-675-slices-5-to-11-work-plan-delta.md): row 5, `SL-1551`.
> `PL-1546`'s body is frozen and is not edited. **Read `PL-1286`'s S8 row (`:311`) and its
> dependency row (`:363`), then `PL-1546` row 5 (`:150`), its order paragraph (`:130-142`) and
> R8.1 (`:193-194`), then this file. Where they differ, this file is the later statement.** The
> executor binds what `PL-1546`'s header names: `vue-frontend`, `vue-best-practices`,
> `vue-testing-best-practices`, `python-test` (S8 now has a backend route change),
> `test-driven-development`, `dev-commands` and `git-hygiene`; a chart also has
> `accessibility-tester` verify it. This delta adds **`python-package`** and
> **`contract-schema`** for the `model-schema` row (Task 1). The executor is spawned from
> `.claude/roles/executor.md`. Its `LG-` quotes `PL-1546` row 5 and this file's §"Tasks" as its
> scope. REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans.

Filed under **working id 8095** (minted as `PL-1833`, 2026-10-21), reserved by the lead (`~/gi-pricing-plan.local/handover/eta.md`,
"2026-10-17 19:34:39 BST: **8095 PL** reserved (WK-675 S8 plan delta: PL-1546 row 5 → SL-1551,
the typed /movers row as need + scope + a DP in-slice vs separate backend slice …)"). Written
2026-10-17 by the planner (seat planner-s8) on the lead's brief
`brief-planner-s8-2026-10-17.md`. **Tree read:** `origin/main`
`9469721db3d26480824cc1d715da2ec4ca9044d0` (#1326, 2026-10-17T16:56:51+01:00). Every
`file:line` below was read at that tree unless a branch is named. **No test was run at planning
time.** **`status: draft`**: DP-S8-1 blocks (§"Decision points"). *(Amended 2026-10-17 by the
planner (seat planner-s8b), pre-merge: both DPs are ruled (a), §"Decision points"; the plan
stays `draft` until it is minted, in order, and then goes `active`.)* *(Amended 2026-10-21, executor exec-d28, on the maintainer's (by delegation) GO D28, `to-lead.md` "2026-10-21 15:10:53 BST": minted as `PL-1833` and set `active`, in that order.)*

## Authority

- **The GO**, the maintainer's entry in `~/gi-pricing-plan.local/channel/to-lead.md`,
  "2026-10-17 19:34:26 BST — Maintainer: GO planner for the WK-675 S8 plan delta (PL 8095); lane
  C read noted", verbatim: *"GO: one planner seat writes the S8 plan delta (working PL 8095) on
  PL-1546 row 5 → SL-1551: the typed /movers row as S8's need + scope (the route is given to S8
  by PL-1501:429 DP-S4-3; my 2026-10-16 10:21:56 Q5), plus a DP stating in-slice vs a separate
  backend slice, with options + a recommendation. Writing only (no DB/gate/tests). Fixes mismatch
  M1. The delta rides the next docs batch, minted in order."* Same entry: *"The recommendation
  that none of S9–S11 starts before the Mon 19 Oct 12:00 cut checkpoint is AGREED. The cut
  decisions at that checkpoint are the USER's (it goes in the morning summary)."*
- **The owner**, the maintainer's entry "2026-10-16 10:21:56 BST — Maintainer: CUT CHECKPOINT
  questions Q1–Q7", Q5, verbatim: *"the typed movers row SL-1551 needs: no slice carries it at
  0877e6e7, so it is an UNOWNED need, which is not a permitted state. Owner = SL-1551 itself
  (WK-675), via its own plan delta (the row is a model-schema shape, generated). The lane C
  planner confirms by Mon 19 12:00 that no other Work's surface owns it; otherwise it brings a
  DP."* That confirmation is filed in `~/gi-pricing-plan.local/handover/lanec-next-2026-10-17.md`
  §3 (planner-lanec, 2026-10-17 19:31 BST, at `9469721d`); this delta re-checked its two
  predicates at the same tree (Context 4).
- **The typed shape and the hard gate**, the `to-lead.md` entry "2026-10-10 01:54:02 BST —
  RULINGS on S4 @04eaed4a: (1) red-first on parent commits ACCEPTED; (2) untyped movers ACCEPTED
  FOR S4 ONLY as an owned gap with a hard gate. Not an OQ: it is decided", item (2), verbatim:
  *"The typed shape: a row model in model-schema with the known fields typed (the policy/quote
  identifier; before/after/change in integer minor units; change_pct as the repo's decimal
  form), plus ONE named open field for the portfolio's own columns (e.g. `columns: dict[str,
  JsonScalar]`), never a bare open object."* *"HARD GATE: the typed row is an ACTIVATION NEED of
  the first slice that consumes /movers (WK-675's movers view). Its plan gets a dated need line
  (via D3's or its own delta), and no frontend code may read /movers before the typed row is
  merged. Owner WK-675. If no consumer exists by WK-673's Work close, it is carried by name at
  P2's close."* *"The ACK of the slice that adds the typed row checks the response shape and the
  regenerated client."* *"Cost: none now; ~1 h later in the consumer slice."* The roadmap carries
  this as `SL-1551`'s added need, `docs/roadmap.md:1546`, headed "(draft, for the lead's batch)".
- **The route is S8's**, `PL-1501:429`, DP-S4-3 (a): *"the read route is owned by WK-675 Slice 8,
  the view that needs it"*; ruled (d) by `RL-1504` item 5 (the blob holds the frame's own columns
  only; `/movers` joins the portfolio columns at read).

## Why a delta, and not the slice's ledger

The `LG-` is the executor's file (`document-ids.md` §1.6, LG row). A change to what a Work-plan
row says is a new `PL-` that `relates:` the Work's plan. The precedents are `PL-1668` (row 1) and
`PL-1764` (row 4).

## Context — what is open at `9469721d`

1. **The route is untyped.** `docs/contracts/openapi/generated.json`, path
   `/api/v1/dislocation-runs/{run_id}/movers`, `get` → `responses` → `200` → `application/json`
   → `schema`, verbatim: `{"items": {"additionalProperties": true, "type": "object"}, "title":
   "Response Get Dislocation Run Movers Api V1 Dislocation Runs  Run Id  Movers Get", "type":
   "array"}`. Read with: `python3 -c "import json;print(json.load(open('docs/contracts/openapi/generated.json'))['paths']['/api/v1/dislocation-runs/{run_id}/movers']['get']['responses']['200']['content']['application/json']['schema'])"`.
   The handler, `backend/src/app/api/dislocation_runs.py:157-161`, returns `list[dict[str, Any]]`
   with no `response_model`, and builds each row as `{k: _json_value(v) for k, v in
   r.items()}` (`:197`).
2. **No mover class exists in `model-schema`.** `git grep -n -iE 'class .*Mover' -- packages/model-schema`
   prints nothing (rc 1). `packages/model-schema/src/model_schema/dislocation.py` (279 lines)
   holds `DislocationRun` with `largest_movers_blob: str | None` (`:208`) and no row type.
   `JsonScalar` is not defined anywhere in `packages/model-schema/src` (`git grep -n JsonScalar
   -- packages/model-schema/src`, no hit).
3. **What a stored mover row holds.** The blob holds `MOVERS_COLUMNS = ("quote_id",
   *_FRAME_COLUMNS)` (`backend/src/app/worker/dislocation_handlers.py:89`), where
   `_FRAME_COLUMNS` (`packages/pricing-core/src/pricing_core/rating/analysis.py:77-86`) is
   `baseline_outcome`, `candidate_outcome`, `baseline_minor`, `candidate_minor`, `change_minor`,
   `baseline_error_code`, `candidate_error_code`, `origin_rung`. **There is no `change_pct`
   column**: `select_movers` (`analysis.py:293-309`) decides and orders on
   `Fraction(abs(change_minor), baseline_minor)` and stores the frame's own schema. The ruling's
   `change_pct` is therefore **computed at read**, and its decimal form and rounding are not
   stated in `03` §4.6 (`03:705` defines the mover and its order, and rounds only
   `abs_change_pct_quantiles`: "rounded once to 6 places toward +∞"). Every mover is in the
   banded set (`03:705`), so `baseline_minor > 0` and its percentage is always defined.
4. **No other Work owns the row** (Q5's confirmation, re-checked here): `git grep -l -iE 'typed
   movers|movers row|MoverRow|DislocationMover' -- docs` prints `PL-1501` and `roadmap.md` only;
   no `frontend/src` file mentions `movers` (`git grep -n -i movers -- frontend/src`, no hit).
5. **The repo's two decimal forms.** `DecimalStr` and `PositionalDecimalStr`
   (`packages/model-schema/src/model_schema/money.py:127-145`); the second always serialises
   positionally, because `DecimalStr`'s `str()` can emit an exponent outside its own JSON Schema
   pattern (`RL-1329` §3, B2, quoted at `money.py:134-139`). *Observation, not this delta's
   scope:* `DislocationTotals.change_pct`, `DislocationBand.mean_change_pct`,
   `SegmentSlice.mean_change_pct` and `AttributionItem.mean_change_pct` are `float | None`
   (`dislocation.py:84`, `:105`, `:113`, `:163`); the lead may route that to an owner. The new
   row does not copy it. *(Routed 2026-10-17 by the maintainer's 19:41:48 BST entry: a LOW FD,
   working id FD 8096, owner WK-1178, in batch D21. S8's scope is not widened.)*
6. **Three in-flight slices regenerate `generated.json`.** `git diff --name-only
   origin/main...origin/<branch> -- docs/contracts packages/model-schema/src`, at the heads read
   2026-10-17: `sl-1547-wk675-s5` @`4c45b8f2` (generated.json, `rating.py`, `regression.py`, two
   regression/algorithm schemas), `sl-1341-wk1250-s3-purpose-mount` @`f269c5ca` (generated.json,
   `rating.py`, `scoring.py`, `rating-algorithm.schema.json`), `sl-1274-wk690-s4-factor-expression`
   @`bba2e0ae` (generated.json, `diagnostics.py`, `modelling.py`, two banding/diagnostics
   schemas). **None touches `dislocation.py` or `api/dislocation_runs.py`**; each touches
   `generated.json`, so whichever of them and S8's typed row merges later re-merges main and
   re-runs `generate-contracts.py` (the maintainer's "2026-10-16 09:35:13 BST — GO SL-1341 …"
   rule, as lanec-next §1 quotes it).

## M1 — row 5's needs, corrected

`PL-1546:139-140` states *"S8 needs S1 and `SL-1388` only"*, and row 5 (`:150`) lists *"S1 (met);
**`SL-1388`** (WK-673 S4) closed"*. Both predate the 2026-10-10 01:54:02 hard gate. **Dated need
line, 2026-10-17 (this delta):** S8's needs are **S1 closed (met); `SL-1388` closed (met); the
typed movers row of Task 1 in `model-schema`, its route typed and its contract regenerated** —
met either by S8's own Task 1 before any frontend read of `/movers` (DP-S8-1 (a)), or by a
separate slice merged before S8 activates (DP-S8-1 (b)). Which, is DP-S8-1's ruling. `PL-1546`
`:139-140`'s conclusion stands in its other half: S8 still has no dependency on S10 or S11.

## Goal

S8 ships `PL-1286`'s S8 row (`:311`) — change histogram (FR-263), segment grid (FR-264),
attribution waterfall (FR-266), largest movers with drill-down to individual quotes (FR-263),
the run cited by id (FR-265), each chart with its table (NFR-463) — **with the movers read
through a generated, typed row**, never a hand-written frontend type. Done when `SL-1551` closes
on its `LG-` (or a moved line puts it in Phase 3) and Acceptance 1–9 hold.

## Requirements, each id

`03` §3.9: FR-263, FR-264, FR-265, FR-266 (unchanged from row 5); NFR-463 (unchanged). §3.9 also
holds FR-1397, FR-1398 and FR-1399; they are the attribution's backend rules, delivered by
WK-673, and **not** S8's scope (S8 renders their output). `03` §5.1's `/movers` row (`03:1067`)
and §4.6's mover definition (`03:705`) are amended by Task 1 (spec first).

## Tasks

The slice's steps are written in its `LG-` by its executor (L5). This delta fixes what the
tasks must contain and their order.

### Task 1 — the typed movers row (backend, spec first)

1. **Spec, `03-rating-engine.md`.** §4.6 (`:705`) gains one sentence: a mover row's `change_pct`
   is (candidate − baseline) ÷ baseline × 100 computed exactly on the integers and written as a
   positional decimal string rounded once to 6 places **away from zero**, so a mover never reads
   below `mover_threshold_pct` (the rule `abs_change_pct_quantiles` uses for the same reason,
   `:705`). *This rounding is a design choice: DP-S8-2, ruled (a) — 6 places, `ROUND_UP`,
   `PositionalDecimalStr`.* The amendment lands in `docs/specs/03-rating-engine.md` §4.6
   (heading "4.6 `DislocationRun`", the "Bands and movers" paragraph at `:705`) **in S8's own
   commit**, per `.claude/skills/spec-change`, citing the maintainer's 2026-10-17 19:41:48 BST
   entry; this plan does not edit the spec. §5.1's `/movers` row (`:1067`) names the
   response as an array of `DislocationMover`. Dated *(Amended 2026-10-…, WK-675 Slice 8,
   PL-1833)* at each site.
2. **`model-schema`.** In `dislocation.py`, a `DislocationMover` with every stored column typed:
   `quote_id: str`; `baseline_outcome`, `candidate_outcome`: the frame's outcome strings;
   `baseline_minor`, `candidate_minor`, `change_minor`: `MoneyMinor`; `baseline_error_code`,
   `candidate_error_code`: `str | None`; `origin_rung: str | None`; `change_pct:
   PositionalDecimalStr`; and the ONE open field `columns: dict[str, JsonScalar]`, the portfolio
   columns joined at read. `JsonScalar` is added to `model-schema` as `str | int | float | bool |
   None` (a portfolio column is not money; the rating path's money never enters `columns`).
   Exported from `model_schema/__init__.py`.
3. **The route.** `get_dislocation_run_movers` returns `list[DislocationMover]`: the stored
   columns into their fields, `change_pct` computed per step 1, every other joined column into
   `columns`. `_json_value` already turns a `Decimal` into a string (`:147-149`); a date or
   datetime column becomes its ISO string; **any other non-scalar dtype is a stop-and-report**,
   not a widened type.
4. **Contracts.** `uv run python scripts/generate-contracts.py` regenerates `generated.json`;
   `pnpm --dir frontend generate:api` regenerates the client. No hand-authored schema under
   `docs/contracts/schemas/` changes: the row is an API response, not a persisted artifact (the
   blob's columns are unchanged).
5. **Tests, red first.** A route test, `@pytest.mark.req("FR-263")`, asserts each typed field on
   a mover from a seeded run, `change_pct`'s string for a value that rounds (red on a
   half-even or toward-zero implementation), an **edge-of-threshold case** (a mover whose
   exact percentage equals `mover_threshold_pct`, and one just above it whose exact value is
   not a 6-place decimal: each is selected and each `change_pct` reads ≥ the threshold after
   `ROUND_UP`; red on a toward-zero implementation; DP-S8-2 (a)), and that a portfolio column arrives under `columns`
   and not at the top level. A `model-schema` test refuses a float `change_pct` and a bare extra
   top-level key (`extra="forbid"`). Broken-input run of each recorded in the `LG-`.

### Task 2 — the views (frontend), after Task 1

`PL-1286`'s S8 row, under `PL-1546` R8.1 (the slug route form, `RL-1473:200`), mounted at
`03:1416`'s `/rating/:slug/v/:version/dislocation`. The histogram, segment grid and attribution
waterfall read `GET /api/v1/dislocation-runs/{run_id}` only; the largest-movers table reads
`/movers` through the generated `DislocationMover`. **No frontend file reads `/movers` in a
commit older than Task 1's** (Acceptance 5). Each chart has its `RL-1307` accessible table.

## Decision points

Planner does not rule these (`delivery-process.md` §3). **DP-S8-1 blocks** (it decides whether
this slice is one PR or two, and which record carries Task 1); this plan is `draft` until it is
ruled. DP-S8-2 blocks Task 1 only. *(Both ruled (a), 2026-10-17; the dated lines are below the
table.)*

| DP | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| **DP-S8-1** | Is the typed movers row built **inside S8** or in **a separate small backend slice first**? | **(a) In-slice.** Task 1 is S8's first task, in S8's one PR (L1 (a')). Paths: `03` §4.6/§5.1, `dislocation.py`, `__init__.py`, `api/dislocation_runs.py`, its test, `generated.json`, plus S8's frontend. Gate cost: **one** two-half gate (the maintainer's 2026-10-17 18:56:17 entry measured a re-gate at 60.9 min; the 01:54:02 entry priced the row at "~1 h later in the consumer slice"). Ids: none new. Order: S8's single PR merges after S5 (`SL-1547`) and S7 (`SL-1550`) by item D, so it is likely the later of any `generated.json` pair and re-merges + re-runs both generators once, on a larger PR. Ruling text: matches Q5's *"Owner = SL-1551 itself"*; does **not** match the letter of 01:54:02's *"ACTIVATION NEED … no frontend code may read /movers before the typed row is merged"* — an activation need cannot be met inside the slice it gates — so that line is re-read as an in-slice order gate (Acceptance 5), which only its author can confirm. **(b) A separate backend slice ahead of S8** (cut by this delta's batch: one new `SL-` + its `LG-`, WK-675, rung 7 with S8). Paths: Task 1's backend paths only. Gate cost: **two** two-half gates (the backend slice needs the frontend half too, because `generate:api` changes the client S8 type-checks against), plus a second PR, ACK and merge. Ids: one `SL-`, one `LG-` in a mint batch. Order: ready as soon as minted and GO'd (needs: `SL-1388`, met), so it could run while S5/S7 finish; its small PR re-merges cheaply against `SL-1547`/`SL-1341`/`SL-1274`. Ruling text: matches 01:54:02's letter exactly; moves Q5's owner from `SL-1551` to a sibling WK-675 slice, which Q5's author confirms. **(c) WK-673 builds it** (the route's original slice's Work). Excluded: Q5 rules the owner is WK-675, and lanec-next §3 confirms no other Work's surface holds it. | **(a), with Acceptance 5 as the order gate.** The scarce resource this week is gate time (to-lead 19:32:51: SOLO gates queued SL-1543 → the SL-1740 + SL-1547 pair → SL-1258); (b) spends a second full gate and two ids to land ~1 h of backend work alone. (a) holds the hard gate's purpose — no hand-written type, money typed — by command (Acceptance 4, 5), and the 01:54:02 entry already priced the work "in the consumer slice". The 10-16 Q5 is the later statement and names `SL-1551` itself. **Fallback: (b)**, if the maintainer holds 01:54:02's letter. | decision point | yes | **RULED (a)**, 2026-10-17 19:41:48 BST, the maintainer (see the dated line below the table) |
| **DP-S8-2** | How is a mover's `change_pct` rounded and written? `03` §4.6 is silent (Context 3) | **(a)** Exact fraction, rounded once to 6 places **away from zero**, `PositionalDecimalStr`: a mover never reads below its threshold; mirrors `abs_change_pct_quantiles`' "toward +∞" on the absolute value. **(b)** 6 places, `ROUND_HALF_EVEN`, `PositionalDecimalStr`: the usual display rounding; a mover at exactly the threshold after rounding down can read under it. **(c)** `DecimalStr` with no rounding (a terminating decimal only when `baseline_minor`'s prime factors allow; otherwise a cut is still needed, so this is (a) or (b) in disguise) | **(a).** It keeps the displayed value consistent with the membership test FR-263's threshold made, the property §4.6 already chose for the quantiles. (c) is not a real option. | decision point | yes — Task 1 | **RULED (a)**, 2026-10-17 19:41:48 BST, the maintainer (see the dated line below the table) |

**Rulings, dated 2026-10-17** (recorded pre-merge by the planner, seat planner-s8b). Source:
the maintainer's `to-lead.md` entry "2026-10-17 19:41:48 BST — Maintainer: PL 8095 (S8) DPs —
DP-S8-1 (a), DP-S8-2 (a) + a spec line; dislocation floats → a LOW FD".

- **DP-S8-1 → (a)**: S8 builds the typed `/movers` row itself (Task 1). The entry reads the
  2026-10-10 01:54:02 BST hard gate (*"no frontend code may read /movers before the typed row is
  merged"*) by its purpose, verbatim: *"no frontend code is ever written against, or lands on
  main reading, an untyped /movers."* Acceptance 5's ancestor check plus the single squash merge
  meets it; (b) is not needed.
- **DP-S8-2 → (a)**: `change_pct` is computed at read to 6 places, `ROUND_UP` (away from zero),
  `PositionalDecimalStr` — the quantiles' rule — so a selected mover never displays below its
  threshold. A one-line dated amendment to `docs/specs/03-rating-engine.md` §4.6 lands in S8's
  commit (Task 1.1), and a test pins a value at the threshold edge (Task 1.5, Acceptance 7).
- **Not S8's scope:** the `float | None` pct fields in `dislocation.py` (Context 5) go to a LOW
  FD, working id FD 8096, owner WK-1178, in batch D21. S8 is not widened.

## Cut-ladder note

`SL-1551` keeps `PL-1546` row 5's ladder entry: **rung 7, conditional on #1164's served page**
(void if exit demo (b)'s served page is this view). Under DP-S8-1 (b), the backend slice shares
rung 7: if S8 is cut, the row has no consumer and 01:54:02's last limb applies (*"carried by name
at P2's close"*). **S9, S10 and S11 do not start before the Mon 19 Oct 12:00 cut checkpoint**,
and **the cut decisions there are the USER's** (the maintainer's 2026-10-17 19:34:26 entry, quoted
in §"Authority"). This delta cuts nothing and applies no rung. S8 is not named in that hold; it
takes its item-D turn after S7 once this delta is active and the maintainer's GO is given.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` exit 0 at the
   branch head, except check 31's line naming this file's working id, which clears at the mint.
2. **The route is typed.** This prints a schema whose `items` is `{'$ref':
   '#/components/schemas/DislocationMover'}`:
   `python3 -c "import json;print(json.load(open('docs/contracts/openapi/generated.json'))['paths']['/api/v1/dislocation-runs/{run_id}/movers']['get']['responses']['200']['content']['application/json']['schema'])"`.
   Broken input: at `9469721d` it prints `'items': {'additionalProperties': True, 'type':
   'object'}` (Context 1).
3. **One row class, and no bare open object in it.** `git grep -nE '^class DislocationMover\b' --
   packages/model-schema/src` prints one line; in `generated.json`'s
   `components.schemas.DislocationMover`, `additionalProperties` is `false` or absent, and
   `columns` is the only property whose schema has `additionalProperties`.
4. **No hand-written API shape** (`PL-1546` item 4): `uv run python scripts/generate-contracts.py
   --check` exits 0; `pnpm --dir frontend generate:api` leaves `git status --short
   frontend/src/api/generated` empty; `git grep -nE "^(export )?(interface|type) DislocationMover\b"
   frontend/src` prints at most one `components[...]` alias.
5. **The order gate (DP-S8-1 (a)).** With `A=$(git log --reverse --format=%H -S DislocationMover
   origin/main..HEAD -- packages/model-schema/src | head -1)` and `B=$(git log --reverse
   --format=%H -G 'movers' origin/main..HEAD -- frontend/src | head -1)`, `git merge-base
   --is-ancestor "$A" "$B"` exits 0. Broken input: a branch whose first frontend `movers` commit
   precedes `A` exits 1. *(Under DP-S8-1 (b) this item is replaced by: the backend slice's `SL-`
   reads `closed` on `origin/main` at S8's activation commit.)*
6. **Each FR has a test naming it** (`PL-1546` item 3): `grep -rlE 'FR-26[3-6][^0-9]' frontend/src
   --include=*.test.ts` prints a file for each of FR-263, FR-264, FR-265 and FR-266 (checked per
   id), and the route test carries `@pytest.mark.req("FR-263")`.
7. **`change_pct` is held by test at its rounding edge** (DP-S8-2): the route test's rounding case
   is listed in the `LG-` with its red on the broken implementation; so is its
   edge-of-threshold case (Task 1.5: a mover exactly at `mover_threshold_pct`, and one just above
   it, each reading ≥ the threshold after `ROUND_UP`), red on a toward-zero implementation; and
   `git diff origin/main...HEAD -- docs/specs/03-rating-engine.md` shows §4.6's dated
   `change_pct` line (DP-S8-2 (a), 2026-10-17 19:41:48 BST).
8. **Every chart has its accessible table** (`PL-1546` item 5, NFR-463), and
   `accessibility-tester`'s report is quoted in the `LG-`.
9. **The gate is green on the slice's merge tree** (`PL-1546` item 8): the `CLAUDE.md` §11
   commands, both halves, each rc 0, against `origin/main...<slice branch>`, in a slot the lead
   grants; the ACK checks the response shape and the regenerated client (01:54:02, last limb).

## Global Constraints

`PL-1546`'s Global Constraints apply unchanged (Vue 3 `<script setup lang="ts">` only; no
hand-written API type; money never a float; WCAG 2.2 AA; one PR per slice carrying code, tests,
the `SL-1551` status line and its one `LG-`). Added here:

- **Money in the row is `MoneyMinor`** (`CLAUDE.md` §7); `change_pct` is a decimal string, never a
  float (Context 5).
- **The movers blob is unchanged**: no portfolio column is stored (`RL-1504` item 5, NFR-499);
  `columns` is filled at read only.
- **Spec and code in one commit at the squash** (`CLAUDE.md` §2); `audit-docs.py` exits 0 on it.
- **The `generated.json` re-merge rule** (Context 6): if `SL-1547`, `SL-1341` or `SL-1274` merges
  first, S8 re-merges main and re-runs both generators before its ACK request; the ACK checks the
  contract diff.
- **No new route, no new dependency.**

## Self-review

- **Brief coverage.** (1) need + scope with the untyped evidence: Context 1–3, Task 1. (2) M1:
  §"M1". (3) DP in-slice vs separate, with paths, gate cost, the shared `generated.json`, order,
  and a recommendation: DP-S8-1. (4) the cut-ladder note: §"Cut-ladder note".
- **Spec coverage.** FR-263 (histogram, movers, drill-down), FR-264 (segment grid), FR-265 (run by
  id), FR-266 (waterfall): Task 2; NFR-463: Acceptance 8; the mover row's spec text: Task 1.1.
- **Placeholder scan.** The amendment date in Task 1.1 is the executor's commit date, left as
  "2026-10-…" by design; nothing else is open but the two DPs.
- **Literals verified at `9469721d`:** `generated.json` movers 200 schema; `api/dislocation_runs.py:147-197`;
  `dislocation_handlers.py:87-89`; `analysis.py:77-86`, `:293-309`; `dislocation.py:84`, `:105`,
  `:113`, `:163`, `:208`; `money.py:127-145`; `03:705`, `:1067`, `:1416`; `PL-1546:130-150`,
  `:193-194`; `PL-1286:311`, `:363`; `PL-1501:429`; `roadmap.md:1546`.
