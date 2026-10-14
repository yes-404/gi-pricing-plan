---
id: PL-1665
family: plan
kind: map
title: WK-690 — Slices 4 and 5 acceptance brought to RL-1615 and RL-1616, and the fix row's F.1 restated: Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1268, PL-1621, RL-1265, RL-1410, RL-1445, RL-1615, RL-1616, FD-1349, FD-1619, OQ-1617, SL-1274, SL-1275, SL-1622]
---

# PL-1665 — WK-690 Slices 4 and 5 brought to their rulings: Work-plan delta

*(Minted 2026-10-12 as PL-1665 from working id 9864, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

> **For agentic workers:** the executor of each slice binds `subagent-driven-development` or
> `executing-plans`, and `spec-change` for every `docs/specs/` edit. Under L5 the steps are
> written in the slice's own `LG-`.

## Goal

Make `PL-1621`'s acceptance for S4 (`SL-1274`) and S5 (`SL-1275`) say what `RL-1615` and
`RL-1616` ruled, and restate the fix row's (`SL-1622`) item F.1 against main. This delta is done
when every slice it names has closed on its own `LG-` (Acceptance Standard item 2), or has been
moved to Phase 3 by a dated move line. The Work's own goal is still `PL-1268`'s.

**Architecture:** an additive delta. It replaces named items of `PL-1621` and adds new ones.
Every item it does not name stands as `PL-1621` wrote it. `PL-1621` is frozen and is not edited.

**Spec:** `docs/specs/02-modelling.md` §3.1, §3.7, §3.10, §4.1, §4.2, §5.1, §5.3;
`docs/workflows/WF-00702-custom-objective-lifecycle.md` Route B. The rulings are the binding text where this delta and a ruling
differ. A difference is a defect in this delta, and the executor reports it to the lead.

## Authority

- **The form and the id.** The lead's entry "2026-10-12 02:53:18 BST — readiness results: WK-690
  S4/S5 NOT READY (PL-1621 acceptance predates RL-1615/RL-1616; 5.3 CONTRADICTS RL-1616) → delta
  PL 9864 form (a) …" (`~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md:2437`). Form (a)
  is an additive dated Work-plan delta that relates `PL-1268` and `PL-1621` (Lean P2 L5,
  `docs/plans/README.md:16-20`). The maintainer's entry "2026-10-12 02:53:52 BST — Readiness
  rulings: …; PL 9864 + PL 9865 deltas OK; …" (`to-lead.md:22817`), item 3, verbatim: *"WK-690:
  PL-1665, an additive Work-plan delta. 5.3 follows RL-1616 (200 ok:false), because a ruling
  outranks an earlier plan line. The delta strikes the plan line and cites RL-1616. The S5 timing
  window needs a TRUE ALONE."*
- **The rulings it applies.** `RL-1615` (DP-S4-1 (a2), DP-S4-2, need 4.5) and `RL-1616` (DP-S5-1
  (a), conditions 3a–3d). Both were minted in D11 (#1275, `b1cdefb5`). Each was minted after
  `PL-1621`'s acceptance was written at `d699a561`. `PL-1621` took only their ids into its
  Resolved-by cells (`PL-1621:295-296`, `:309`).
- **Their obligations on this plan.** `RL-1615:117-120`: "PL-1621's planner cites this record on
  DP-S4-1 and DP-S4-2. Its S4 row's write set adds `backend/src/app/platform/transformations.py`
  and the banding routes in `backend/src/app/api/models.py`." `RL-1616:95-96`: "S5's estimate
  gains about 0.3 of a slice (accepted), plus whatever conditions 3a to 3c add, and the plan says
  so."
- **The ALONE window for 3c and 3d.** A timing measurement on the shared box needs a true
  ALONE window. The precedent is the maintainer's entry "2026-10-12 00:16:39 BST — SL-1455 T0
  rerun (asyncio debug OFF, ~12 min ALONE) …" (`to-lead.md:22637`). The entry "2026-10-12
  02:47:50 BST" item 1 (`to-lead.md:22799`) separates a functional window from a timing window.

## What changes, item by item

| `PL-1621` item | This delta | Why |
|---|---|---|
| 4.1 (`:90`) | **Replaced** by 4.1′ | `RL-1615:100-113`: six spec and schema dispositions, not two |
| 4.2 (`:95`) | Stands | — |
| 4.3 (`:98`) | **Replaced** by 4.3′ | `RL-1615:75-77`, `:125-132`: two refusal points, plus three limbs missing from 4.3 |
| 4.4 (`:105`) | **Replaced** by 4.4′ | `RL-1615:78` (ii), `:133`: `banding.created` too |
| 4.5, 4.6 | Stand | — |
| — | **New** 4.7 | `RL-1615:95-97`: need 4.5 (c), interim evidence |
| R4.2 (`:223`) | **Replaced** by R4.2′ | `RL-1615:75`: creation refusal when certainly numeric |
| R4.3 (`:229`) | **Replaced** by R4.3′ | `RL-1615:86-97`: FD-1619 and OQ-1617, not "maintainer, P2 closure" |
| S4 row write set and size (`:210`) | **Widened** (§S4 row) | `RL-1615:117-120` |
| 5.1 (`:116`) | **Replaced** by 5.1′ | `RL-1616:67`, `:80-89`: FR clauses 3a–3d, the audit sentence, WF-702 B1.4 |
| 5.2 (`:122`) | Stands | — |
| 5.3 (`:130`) | **Replaced** by 5.3′ | **5.3 contradicts `RL-1616:66`**: a bad loss answers 200 `ok: false`, not 422 |
| 5.4–5.6 | Stand | — |
| — | **New** 5.7 | `RL-1616:72-73`: conditions 3c and 3d, measured in an ALONE window |
| S5 row size (`:211`) | **Raised** (§S5 row) | `RL-1616:95-96` |
| F.1 (`:149`) | **Replaced** by F.1′ | FD-1349's guard is on main already (§F.1′) |
| F.2–F.6, R-F.1, R-F.2 | Stand | — |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root.

**This delta**

1. **The delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` exit 0 at the
   branch head. The one exception is check 31's line naming this file's working id, which clears
   at the mint.
2. **Each slice's `LG-` quotes both plans.** The `LG-` quotes its `PL-1621` row and every item
   this delta replaces or adds for that slice. `git grep -l 'PL-<this delta's minted id>' --
   docs/ledgers` prints the `LG-` of each slice in scope here that was not moved to P3.

**S4 — `SL-1274` (replaces 4.1, 4.3 and 4.4; adds 4.7)**

- **4.1′ Spec first, in the code's commit.** All six dispositions of `RL-1615:100-113` land with
  the code, each with a dated line citing `RL-1615`, through `spec-change`:
  - `02` §4.1: `expression` exists on `Factor`, and `banding_id` is allowed on `banding` and
    `expression`. The current "still does not exist on the type" text gets a dated line and is
    not deleted.
  - `02` §4.2: `source_expression`, with the rule that exactly one of `column` and
    `source_expression` is set.
  - `02` FR-95: the result-type rule (DP-S4-2's creation row and resolution row).
  - `02` FR-97: a Banding maps a column or an `expression` Factor's result.
  - `02` FR-208: the `expression` arm resolves.
  - The `model-schema` shapes `Factor`, `Banding`, `BandingProposal` and `BandingEvaluation`.

  `git log -1 --format=%H -- docs/specs/02-modelling.md` on the slice branch names a commit that
  also touches `packages/model-schema/src/model_schema/modelling.py`.
  `uv run python scripts/generate-contracts.py --check` exits 0.
- **4.3′ Every limb of `RL-1615`'s Ruled table was seen failing first.** The `LG-` quotes each
  test red before the implementation and green after. The tests are these.
  - **Creation, 422 at the edge** (`RL-1615:75`), four refusals:
    - (i) a parse error, with its position;
    - (ii) an undeclared column (FR-95);
    - (iii) a pinned Banding whose `source_expression` differs from the expression;
    - (iv) a certainly numeric expression with no `banding_id`, whose message names FR-210.

    "Certainly numeric" is the ruling's definition: the root is `+ - * / **`, unary `-`, a
    numeric literal, or one of `log exp sqrt abs clip log1p expm1`. A guard test shows that a
    bare symbol, and `where`, `min` or `max` at the root, are **not** refused at creation.
  - **Resolution** (`RL-1615:76`). `resolve_factors`
    (`packages/pricing-core/src/pricing_core/modelling/factors.py:112`) raises
    `FactorResolutionError` in two cases: numeric and unbanded, naming FR-210; and string and
    banded. A `source_expression` mismatch is also refused at resolution (`RL-1615:74`, `:130`).
    The match is a normalised parse (an AST dump), not a raw string. A test shows that two
    spellings of one expression that differ only in white space match.
  - **The resolving arms** (`RL-1615:77`). Numeric and banded uses `apply_banding`. String and
    unbanded is categorical. Each arm has one passing fit in a GLM and one in a GBM, and each fit
    yields FR-113's relativity table with its base level marked.
  - **Versioning** (`RL-1615:79`, `:130`). A Factor v2 with a changed expression that pins the
    v1 Banding is refused at creation and at resolution.
  - **The grammar refusals of `PL-1621` 4.3.** `%`, a bare comparison and an unknown function in
    the `factor` profile are each refused with 422 and the position. Under
    `uv run pytest packages/pricing-core/tests/test_glm.py -q` the existing FR-208 and FR-209
    refusal tests for `spline`, `polynomial` and `offset` still pass.
- **4.4′ Audited.** Two tests, from `RL-1615:78` (ii) and `:133`:
  - `factor.created`'s after-state
    (`action="factor.created"`, `backend/src/app/platform/modelling.py:261`) carries
    `expression`;
  - `banding.created`'s after-state (`action="banding.created"`,
    `backend/src/app/platform/transformations.py:299`) carries `source_expression`.

  Both are NFR-484.
- **4.7 The interim parity evidence** (`RL-1615:95-97`, need 4.5 (c)). A test shows that the
  fitted Model's factor record carries the `expression` text of each `expression` Factor, so
  that a reviewer can compare it with a ZEN restatement. The `LG-` cites FD-1619 and OQ-1617 as
  the owners of the parity check itself (R4.3′). The `LG-` does not build that check.

**S5 — `SL-1275` (replaces 5.1 and 5.3; adds 5.7)**

- **5.1′ Spec first, in the slice's first commit, before any code that calls the route.** All
  five dispositions of `RL-1616:80-89` land through `spec-change`, each citing `RL-1616`:
  - `02` §3.7: a new FR, appended from the global sequence. It has numbered clauses for
    conditions 3a, 3b, 3c and 3d, and each clause is quoted from `RL-1616:70-73` with its value
    filled in. The FR names the grid's maximum point count (3a), the executor's fixed worker
    count and the wall-clock timeout (3b), and the preview's own latency budget (3d). The FR
    also has the audit sentence of `RL-1616:69`: NFR-484's "objective derivation" is the one
    stored by `/derive`, and create refuses `derived`.
  - `02` §5.1: the row for `POST /api/v1/custom-objectives/preview`.
  - `02` §5.3: a dated "built" line on the Custom objective library row's 2026-08-27 "not
    rendered" note.
  - `WF-702` B1.4: a citation of the route.
  - The `model-schema` request and response shapes. The request reuses `ObjectiveParameter`.

  The values in 3a, 3b and 3d are the slice's choice, made in the FR. The `LG-` records the
  reason for each value. `uv run python scripts/generate-contracts.py --check` exits 0, and
  `pnpm --dir frontend generate:api` leaves `git status --short frontend/src/api/generated`
  empty.
- **5.3′ The preview route answers as ruled, persists nothing and is governed.** Each test was
  seen failing first in the `LG-`. The tests are these.
  - **Parse only** (`RL-1616:66`). With no `grid`, a loss that does not parse, for example
    `numpy.where(…)` (B1.5), answers **200 with `ok: false`** and `RL-1362` DP-S3-3's
    positioned error, as `POST /model-specs/validate` does (`backend/src/app/api/models.py:684`).
    A malformed request body answers 422. **Struck from `PL-1621` 5.3 (`:130-132`), because it
    contradicts `RL-1616:66` and a ruling outranks an earlier plan line (the maintainer,
    02:53:52 item 3):** ~~"The route answers 422 `OBJECTIVE_GRAMMAR_VIOLATION` with the
    position for `numpy.where(…)` (B1.5)."~~ The frozen file is not edited. The strike lives
    here.
  - **Derive and evaluate** (`RL-1616:66`, `:109`). With a `grid`, the curve equals the output
    of `compile_kernel`
    (`packages/pricing-core/src/pricing_core/modelling/expression_objective.py:217`) for the same
    loss, parameters and grid. The derivation goes through the same `derive` (`:100`). No
    preview copy of either function exists. The 5.5 grep and a reviewer's read of the route
    module confirm this.
  - **3a, input bounds** (`RL-1616:70`, `:107`). A grid over the FR's maximum, and an expression
    over an FR-145 profile limit, each answer 422 `VALIDATION_FAILED`. A test shows that SymPy
    was not called, for example with a patched `derive` that fails if it is called.
  - **3b, time bound** (`RL-1616:71`, `:107-108`). A derivation made slow in the test (a
    patched kernel) answers `ok: false` with a timeout reason, not a 500. After the timeout the
    executor has no worker left running.
  - **Permission and flag order** (`RL-1616:68`, `:112`). Without `model:fit` or without
    `custom_objective:author` the answer is 403. With both permissions and the flag off it is 409
    `OBJECTIVE_KIND_NOT_ENABLED`. The permission check runs first.
  - **Nothing persisted, nothing audited** (`RL-1616:69`, `:101`, `:111`). Rows in the
    custom-objective tables and Audit Events are counted before and after a successful preview,
    and the counts are equal.
- **5.7 Conditions 3c and 3d are measured, in a true ALONE window** (`RL-1616:72-73`; Authority,
  last bullet). They are diagnostic on the shared box, so neither result fails the gate on its
  own. Each is a measurement, never an estimate.
  - 3c: `/score`'s p99 at a moderate rate, alone and then with previews saturating their
    executor.
  - 3d: the preview's own latency against the FR's budget.

  The `LG-` records the rate, the sample count, the box load before and after each run, and the
  command verbatim. **This is S5's activation need (§Tasks, S5 row): a TRUE ALONE window, booked by the lead and quoted at S5's GO.** A run on a shared box is a
  functional run only and does not discharge 5.7. A test that shows `/score` is never queued
  behind the preview executor (separate executors) is also required. It discharges 3c's "never
  queue ahead" clause apart from the timing.

**Fix row — `SL-1622` (replaces F.1)**

- **F.1′ FD-1349: the guard exists; prove it, then discharge it.** FD-1349's comparison is on
  main: `test_the_certificate_check_name_enum_is_the_code_vocabulary`
  (`backend/tests/test_contracts.py:2995-3013`). It was added by `36a9f483` ("SL-1273: WK-690
  Slice 3 — the expression kind through the platform behind the flag …", #1122, 2026-10-05), by
  the predicate `git log --format='%h %aI %s' origin/main
  -S'test_the_certificate_check_name_enum_is_the_code_vocabulary' --
  backend/tests/test_contracts.py`. `git show d699a561:backend/tests/test_contracts.py | grep -c
  test_the_certificate_check_name_enum_is_the_code_vocabulary` prints `1`, so the guard was
  already there at `PL-1621`'s own tree. The fix row writes no new guard. The `LG-` proves the
  guard red on the finding's own broken input:
  1. In the slice worktree, replace five names in the
     `result.properties.checks.items.properties.name.enum` of
     `docs/contracts/schemas/objective-certificate.schema.json` with `"BOGUS"`.
  2. Run `uv run pytest backend/tests/test_contracts.py -q -k
     certificate_check_name_enum_is_the_code_vocabulary`. It must fail.
  3. Restore the file. `git diff --stat` on the file prints nothing, and the same command
     passes.

  The `LG-` quotes both runs. At the close the auditor writes FD-1349's dated discharge line in
  the register (`docs/findings/register.md:281`): "Resolved by SL-1273 (#1122, `36a9f483`)",
  citing `test_contracts.py:2995-3013` and the red-on-BOGUS run. `python3
  scripts/register-lint.py` exits 0 after it. F.5's "closed by the slice" for FD-1349 means this
  line.

## Global Constraints

`PL-1621`'s Global Constraints (`:177-194`) and `PL-1268`'s apply unchanged. That includes
these rules:

- **One PR per slice.**
- **S4 and S5 never at once.**
- **`RL-1445`'s concurrency.**
- **The custom-objective governance rules.**
- **The flag stays off** (`RL-1265` DP-3).
- **No `eval`, `exec` or `lambdify`.**
- **One parser.**

Two more come from the rulings:

- **The single implementation** (`RL-1616:66`). The preview route calls the fit's own `derive`
  and `compile_kernel`. It never calls a copy of either.
- **No formula parity check is built in S4.** `RL-1615:86-97` routes it to FD-1619 (owner
  WK-1178) and OQ-1617.

## Tasks

The order and lanes of `PL-1621:196-211` stand: the fix row, then S4, then S5, each with its lane
assigned at GO. This delta changes the rows as follows.

**S4 row (`PL-1621:210`).**
- **Write set** (`RL-1615:117-118`). Add `backend/src/app/platform/transformations.py`
  (`banding.created` at `:299`; banding propose and evaluate) and the banding routes in
  `backend/src/app/api/models.py`: `propose_banding` `:330`, `evaluate_banding` `:361` and
  `create_banding` `:389`. Read them at S4's base, because the file gained a route at `:1253`
  after `d699a561`.
- **Size.** About 1.5 slices (`RL-1615:118-120`, the memo's estimate, not a measurement),
  against `PL-1621`'s 1.
- **Requirements.** Add `02` FR-97 and §4.2 `source_expression`.

**S5 row (`PL-1621:211`).**
- **Size.** 1 plus about 0.3 (`RL-1616:95-96`, accepted), plus whatever conditions 3a–3c add.
- **Activation need (new): a TRUE ALONE window for 5.7**, of the class of the maintainer's
  "2026-10-12 00:16:39 BST" entry (`to-lead.md:22637`): no other gate, test, check or sweep on
  the box. It is required by the maintainer's "2026-10-12 02:53:52 BST" item 3 (`to-lead.md:22817`).
  A FUNCTIONAL window does not meet this need. The lead books the window, and S5's GO quotes the
  booking. S5's code may be built before the window. 5.7 is measured inside it, and S5 does not
  close until 5.7 is measured.
- **Requirements.** Add the new §3.7 FR (5.1′).

**Fix row (`PL-1621:209`).** The write set loses the new guard (F.1′). It keeps
`backend/src/app/platform/metrics.py` and `packages/pricing-core/src/pricing_core/modelling/objectives.py`
with their tests (F.2, F.3). It touches `backend/tests/test_contracts.py` not at all, unless
the red-on-BOGUS proof needs a scratch copy, which is never committed.

### Rationale changes

- **R4.2′ — Where the numeric refusal fires** (replaces `PL-1621:223-228`). It fires at **two**
  points (`RL-1615:75-76`). At creation, 422, only when the expression is certainly numeric and
  has no `banding_id`. At resolution, as a `FactorResolutionError` naming FR-210, by the result's
  dtype on the Dataset Version. A non-bare expression can be a string, so creation alone cannot
  decide every case. The undeclared-column refusal and the `source_expression` mismatch also
  fire at creation.
- **R4.3′ — A rated model's expression input** (replaces `PL-1621:229-234`). S4 still builds the
  modelling side only. The rating limb, a ZEN restatement of the formula, is not S4's. **Its
  owner is FD-1619** (`docs/findings/register.md:343`, owner WK-1178), with the parity check's
  design at **OQ-1617** (`docs/open-questions.md:152`; `docs/specs/03-rating-engine.md:1554`).
  This replaces `PL-1621`'s "not started, owner the maintainer, event the P2 phase closure
  record". The interim is 4.7. Option (d), routing numeric results through `01` FR-36's
  `derive_expression`, is the named fallback **only if rung 6 is applied to S4**, and is decided
  then with figures (`RL-1615:74`).
- **R5.1′ — The route is ruled** (adds to `PL-1621:235-244`). `POST
  /api/v1/custom-objectives/preview` is fixed by `RL-1616:66`. `PL-1621`'s "illustrative" path
  is now the ruled one. The editor is create-only (`RL-1616:75`), which confirms R5.4.

## Decision points

None open. This delta applies decisions already made: DP-S4-1 and DP-S4-2 (`RL-1615`), DP-S5-1
(`RL-1616`), and the delta's form (a) (the lead, from-lead "2026-10-12 02:53:18 BST"). The values
of conditions 3a, 3b and 3d are not decision points for this plan. `RL-1616` puts them in the
slice's FR (5.1′), and the S5 executor writes them under `spec-change`. If the executor finds a
value it cannot choose without a ruling, it raises the question to the lead and does not pick
silently (`CLAUDE.md` §10).

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| — | none | — | — | — | — | — |

## Self-review

- **Ruling coverage.** Each row of `RL-1615`'s Ruled table (`:74-79`) maps to an item:
  - DP-S4-1 → 4.1′ and 4.3′;
  - DP-S4-2 creation → 4.3′;
  - DP-S4-2 resolution → 4.3′;
  - Red first → 4.3′;
  - extra costs (i) → 4.1′ and the write set;
  - extra costs (ii) → 4.4′;
  - Versioning → 4.3′.

  Each of `RL-1615`'s four Acceptance violations (`:128-133`) has a test in 4.3′ or 4.4′. Need
  4.5 (a), (b) and (c) map to R4.3′ and 4.7. Each row of `RL-1616`'s Ruled table (`:66-76`) maps
  to an item:
  - DP-S5-1 → 5.3′;
  - Spec first → 5.1′;
  - Permission and flag → 5.3′;
  - Audit → 5.1′ and 5.3′;
  - 3a and 3b → 5.1′ and 5.3′;
  - 3c and 3d → 5.1′ and 5.7;
  - R4 → unchanged;
  - Editing → R5.1′.

  Each of `RL-1616`'s four Acceptance violations (`:107-112`) has a test in 5.3′. `RL-1616:97-100`
  lists the timeout's `ok: false` and the curve agreement, and both are in 5.3′.
- **Literals verified at `fc4401dc`.** These were read in the tree, not recalled:
  - `def derive` (`expression_objective.py:100`) and `def compile_kernel` (`:217`);
  - `resolve_factors` (`factors.py:112`) and `_column_matches` (`:320`);
  - `FactorResolutionError` (`pricing_core/modelling/errors.py:42`);
  - `action="factor.created"` (`platform/modelling.py:261`) and `action="banding.created"`
    (`platform/transformations.py:299`);
  - the banding routes (`api/models.py:330`, `:361`, `:389`) and `/model-specs/validate`
    (`:684`);
  - `AUTHORED` (`backend/tests/test_contracts.py:30`) and the guard (`:2995-3013`);
  - FD-1619 (`register.md:343`) and OQ-1617 (`open-questions.md:152`).
- **Placeholders.** None. The numeric values of 3a, 3b and 3d are deliberately left to the
  slice's FR, because `RL-1616` says "named in the FR" and does not name them. This plan does
  not pick them.
- **Collisions** (convention 4, at 2026-10-12 02:5x BST). `gh pr list --state open` prints one
  PR, #1289 (SL-1527), which touches `docs/roadmap.md` only and none of the WK-690 rows. No
  `origin/*` branch has a diff against `origin/main` in `model_schema/modelling.py`,
  `factors.py`, `transformations.py`, `api/custom_objectives.py` or `02-modelling.md`. No ruling
  after D11 rules on WK-690. The per-branch check is re-run at each slice's GO, as
  `PL-1621:331-333` says.
- **Not this plan's writes.** The lead lists this delta on WK-690's roadmap row and adds its
  minted id to the `relates` field of `SL-1274`, `SL-1275` and `SL-1622` at each GO. This
  branch edits no `SL-` row.
