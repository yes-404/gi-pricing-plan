---
id: PL-9931
family: plan
kind: map
title: WK-690 — Slices 4 and 5 (expression Factors; the authoring view and WF-702 Route B) as rows: Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-11
owner: planner
tree: d699a561d6a93f33b74beb9c07023f8e655bb8c7
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1268, PL-1371, RL-1263, RL-1265, RL-1307, RL-1410, RL-1445, RL-1474, FD-1294, FD-1349, FD-1492, FD-1512, SL-1274, SL-1275, SL-9936]
---

# PL-9931 — WK-690 Slices 4 and 5 as rows: Work-plan delta

> **For agentic workers:** this is a **Work-plan delta** under Lean P2 L5. It does not replace
> [`PL-1268`](PL-01268-wk-690-expression-custom-objectives-map-plan.md) (WK-690's map plan,
> `active`). It `relates:` that plan and states every change to Slices 4 and 5 since it was
> written. **Read `PL-1268`'s Acceptance Standard, Global Constraints, Core scope table and
> its Slice 4 and Slice 5 tasks (`:517-554`) first, then this file.** Where they differ, this
> file is the later statement. No per-slice leaf plan is written. Each slice is one PR under
> L1 (a'), and its `LG-` quotes its row below as its scope. REQUIRED SUB-SKILL for each
> slice's executor: subagent-driven-development (recommended) or executing-plans. Each
> executor also binds `test-driven-development`, `python-test`, `spec-change` (each slice
> changes `02` first), `contract-schema`, `dev-commands` (the two-half gate) and `git-hygiene`.
> S4 also binds `python-package`. S5 also binds `fastapi-service`, `vue-frontend`,
> `vue-best-practices` and `vue-testing-best-practices`, and has `accessibility-tester`
> verify its chart. Each executor reads [`README.md`](README.md)'s five unchecked conventions
> and is spawned from `.claude/roles/executor.md`.

Filed under working id 9931, reserved by the lead (brief `brief-planner-wk690-2026-10-11.md`,
eta "2026-10-11 11:14:34 BST: RESERVED PL 9931"). Written 2026-10-11 by the planner
(planner-wk690). Evidence was read at `origin/main` `d699a561` (#1272,
2026-10-11T11:12:28+01:00). The readiness memo behind it is
`handover/readiness-wk690-s4s5-2026-10-11.md` (local). The sweep is by full class: every
`docs/` file that names either slice, by the predicate `git grep -ln 'SL-1274\|SL-1275'
origin/main -- docs .claude/skills`; every register row naming the Work, by `grep -n 'WK-690'
docs/findings/register.md`; and every `to-lead.md` entry naming WK-690, by `grep -n 'WK-690'`.
**No earlier WK-690 delta exists.** The lead's entry "2026-10-08 14:27:05 BST" item 2 names
`draft/pl-9470 @ced887f7` as the WK-690 delta, but that commit's subject reads "WK-1178's
single-row Work plan: the FD-1374 fix slice".

## Authority

- **Lean P2 L5**, the maintainer's entry "2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items
  1, 3 and 5 APPROVED; IN PRACTICE NOW; the files are amended through RFC 9479 P6 (the
  maintainer's amendment, by delegation)", as `docs/plans/README.md:16-20` and
  `.claude/skills/writing-plans` state it: slices are rows, no leaf plan is written, and a change
  is one dated Work-plan delta that `relates:` the Work's plan.
- **The P2 re-plan**, "2026-10-08 12:55:22 BST — P2 RE-PLAN RULED …", F-5 (b): "WK-690 just in
  time". This is that delta. The seat is from "2026-10-11 10:47:28 BST", item 3 (the non-build
  planner queue), and "2026-10-11 11:14:26 BST" (the seat).
- **The cut ladder**, "2026-10-08 13:21:00 BST — CUT LADDER (handover/cut-ladder-2026-10-08.md)
  RULED …", item (1): **WK-690 S5 is rung 3, and WK-690 S4 is rung 6.** This delta does not
  pre-cut either rung. It marks both.
- **The resolver of S4's result rule**: `RL-1265` DP-4 (b), `:78` and `:108-109`.
- `kind: map`, because the PL template admits only `map | leaf | review | handover` (the lead's
  decision (b), 2026-10-08, as `PL-1546` used it).

## Goal

Plan WK-690's last two P2 build slices, and its fix row, as L5 rows so that each can be GO'd
without a leaf plan. This delta is done when S4 and S5 have each closed on their own `LG-`, or
have been moved to Phase 3 by a dated move line, and the fix row (SL 9936) has closed on its
own `LG-`. The fix row is never moved by a ladder rung. The Work's own goal is still `PL-1268`'s.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root. Items 1–3
bind the delta; items 4.x bind S4, 5.x bind S5 and F.x bind the fix row. `PL-1268`'s Acceptance
items 1, 2, 9 and 10 still bind all three.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` exit 0 at the
   branch head. The one exception is check 31's line naming this file's working id, which
   clears at the mint.
2. **Each slice closes on its own L1 (a') ledger, and that ledger's scope section quotes the
   slice's row below verbatim.** By the Work's close, `git grep -l 'PL-<this delta's minted id>'
   -- docs/ledgers` prints one `LG-` per slice that was not moved to P3, and each names its
   `SL-` id.
3. **No slice starts while a decision point that blocks it is open.** For S4, DP-S4-1 below
   carries a `Resolved by` id on the slice's base tree. For S5, DP-S5-1 does.

**S4 — SL-1274**

- **4.1 Spec first, in the code's commit.** `02` §4.1 prints the expression field as live, and
  FR-208 carries a dated amendment that says `expression` resolves and states DP-S4-1's
  banding rule. `git log -1 --format=%H -- docs/specs/02-modelling.md` on the slice branch names
  a commit that also touches `packages/model-schema/src/model_schema/modelling.py`.
  `uv run python scripts/generate-contracts.py --check` exits 0.
- **4.2 The requirement is tested, by name.** `git grep -n 'req("FR-95")' -- packages backend`
  prints at least one test. A GLM fit and a GBM fit each run on a banded `expression` Factor,
  and each yields that Factor's FR-113 relativity table with its base level marked.
- **4.3 Every refusal was seen failing first.** The `LG-` quotes each refusal failing before the
  implementation and passing after: a numeric result with no banding, refused by name with
  `FR-210` in the message (`RL-1265` DP-4); a name that is not a declared column, refused at
  creation with 422; and `%`, a bare comparison and an unknown function in the `factor`
  profile, each refused with 422 and the position. Under
  `uv run pytest packages/pricing-core/tests/test_glm.py -q`, the existing FR-208 and FR-209
  refusal tests for `spline`, `polynomial` and `offset` (`test_glm.py:202-268`) still pass.
- **4.4 Audited.** A test shows that `factor.created`'s after-state
  (`backend/src/app/platform/modelling.py:261`) carries the expression text (NFR-484).
- **4.5 Never `eval`.** The compiled form is the `factor` profile's own
  `compile_expression` (`pricing_core/data/expressions.py:323`). The slice's diff adds no call
  to `eval`, `exec` or `lambdify`: `git diff origin/main...<branch> -- packages backend | grep
  '^+' | grep -cE '\b(eval|exec|lambdify)\('` prints `0` (NFR-483).
- **4.6 Both gate halves pass on the merge tree** (`CLAUDE.md` §11), against
  `origin/main...<slice branch>`.

**S5 — SL-1275**

- **5.1 Spec first, in the slice's first commit.** DP-S5-1's route has its `02` §5.1 row and
  its FR, and `02` §5.3's Custom objective library row loses its 2026-08-27 "not rendered" note
  for a dated "built" note. Both land before any code that calls the route.
  `uv run python scripts/generate-contracts.py --check` exits 0.
  `pnpm --dir frontend generate:api` leaves `git status --short frontend/src/api/generated`
  empty.
- **5.2 `WF-702` Route B runs over HTTP in one file**,
  `backend/tests/test_wf702_route_b.py`, which `uv run pytest
  backend/tests/test_wf702_route_b.py -q` passes. With the flag on in one workspace,
  `asymmetric-burning-cost` (§4.6's example) goes from create through derive, certify
  (`certified_with_findings`, convexity `violated`) and submit, to `approved` by two
  non-author Approvers. With the flag at its default in a second workspace, `POST
  /api/v1/custom-objectives` with `kind: expression` answers 409 `OBJECTIVE_KIND_NOT_ENABLED`.
  This is `PL-1268` Acceptance item 7, unchanged. B4.4–B4.5 are carried (R5.3).
- **5.3 The preview route persists nothing and is governed.** Tests show four things. The
  route answers 422 `OBJECTIVE_GRAMMAR_VIOLATION` with the position for `numpy.where(…)`
  (B1.5). It answers 403 without `custom_objective:author`. It answers 409
  `OBJECTIVE_KIND_NOT_ENABLED` with the flag off. Its success writes no row and no audit
  event, counted before and after. Each refusal was seen failing first in the `LG-`.
- **5.4 The view.** Frontend tests show three things. The editor renders the route's parse
  error at its position. The editor is hidden or disabled while the flag is off. A rendering
  test fails if `certified_with_findings` is styled as a failure (`PL-1268` S5 gate). The
  loss-curve preview is a `ChartFigure` in `RL-1307`'s column-descriptor form with its
  accessible table (NFR-463), and `accessibility-tester`'s report is quoted in the `LG-`.
- **5.5 One parser.** No frontend file evaluates or parses the grammar.
  `git diff --name-only origin/main...<branch> -- frontend/src | grep -ciE 'pars|grammar|evaluat'`
  prints `0`, and the editor's only source of parse errors, derivatives and curve points is
  the API (`PL-1268` Global Constraints, `:174`).
- **5.6 Both gate halves pass on the merge tree**, including `generate:api` and `type-check`
  run under `env -C`.

**Fix row — SL 9936** (FD-1349, FD-1492, FD-1512; FD-1294's discharge line)

- **F.1 FD-1349: the contract guard compares the check-name enum.** `backend/tests/test_contracts.py`
  gains a comparison between the authored `result.checks[].name` enum in
  `docs/contracts/schemas/objective-certificate.schema.json` and `OBJECTIVE_CERTIFICATE_CHECKS` /
  `OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC` (`packages/model-schema/src/model_schema/objectives.py`),
  written per `.claude/skills/contract-guard`. The `LG-` quotes it red on the finding's broken
  input (five names replaced by `"BOGUS"`), then green on the tree, under
  `uv run pytest backend/tests/test_contracts.py -q`.
- **F.2 FD-1492: a dangling metric certificate is refused.** A test through `submit` shows that
  a custom metric whose `certificate_id` names no `metric_certificate` row (same workspace,
  same metric) is refused 409 `VALIDATION_FAILED`. That is the stored-state code the objective
  twin uses (`02` §5.1 submit row, `RL-1410`). The test is red first at the base, where
  `backend/src/app/platform/metrics.py:794` tests only `is not None`, and green after.
- **F.3 FD-1512: `pseudo_huber` certifies on the default grid.** The template's loss is
  evaluated in the finding's cancellation-free form (register `:327`'s event). A test certifies
  `pseudo_huber` over `default_sampling` at delta 1, 63, 100, 1000 and 100000, and none is
  `failed`. It is red first at the base for 63, 100, 1000 and 100000. A second test shows that
  the template's gradient and hessian are unchanged to 1e-12 at the finding's worst points, so
  no fitted model's objective changes.
- **F.4 FD-1294's dated line.** The register row (`docs/findings/register.md:218`) gains the
  dated line "Resolved by SL-1271 (#981, `bd67fb51`)", citing
  `packages/pricing-core/tests/test_expression_profiles.py:181-204` (R-F.1). This is the
  auditor's write at the slice's close, not the executor's (`.claude/roles/planner.md` Tools).
  `python3 scripts/register-lint.py` exits 0 after it.
- **F.5 Each register row is closed by the slice.** The `LG-` names FD-1349, FD-1492 and
  FD-1512 with their red and green commands, and the auditor's close moves each row to
  resolved. `python3 scripts/register-lint.py` exits 0.
- **F.6 Both gate halves pass on the merge tree** (`CLAUDE.md` §11).

## Global Constraints

`PL-1268`'s Global Constraints apply unchanged. That covers: `pricing-core` stays standalone;
definitions are JSON, never pickles; no hand-written shape; never `eval` or `lambdify`; one
parser; no pandas; `<script setup lang="ts">` only; spec changes in the code's commit; and the
flag stays off. Added since:

- **One PR per slice** (L1 (a')): the code, the tests, the spec change, the slice's `SL-` row
  status line and one `LG-`. There is no leaf plan, no dispatch `RL-` and no activation PR.
- **Concurrency is `RL-1445`'s** (`RL-1263` as amended: at most three build slices, one full
  gate at a time, and same-Work concurrency only with resolved file sets and no plan
  dependency). **S4 and S5 do not run at once.** Both edit `docs/specs/02-modelling.md` and
  `docs/contracts/`, so their file sets are not disjoint (`PL-1371:210` already says "never
  beside another WK-690 slice").
- **The custom-objective governance rules** (`CLAUDE.md` §3; `.claude/skills/spec-change`
  §"Specifying a custom objective": declared, validated, versioned, audited) bind both slices.
  S4's `expression` Factor is user text evaluated over data and is governed alike. Each row's
  "Governance" cell says how the slice meets them.

## Tasks

Under L5 a Work plan's tasks are its slice rows, and each slice's steps are written in its `LG-`
by its executor. The size is `PL-1371` §3.4's estimate. **The lane is assigned at GO.**
**The fix row goes first**, as soon as a lane frees: it has no decision point and no unmet
dependency, so it is the one WK-690 row GO-able today. **Then S4, then S5**, in reverse ladder order (S4 is rung 6 and S5 is rung 3), so that a cut
discards no finished work. This is the principle the maintainer ruled for WK-675 ("2026-10-08
14:32:33 BST — DELTAS AUDIT …", item D). It is a recommendation for this Work, not a ruling.
No dependency forbids it, because S4 needs S1 and S5 needs S3, and both have closed. If one
slice's decision point is still open when a lane frees, the other takes its turn.

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Governance | Depends on | Lane | Size | Ladder |
|---|---|---|---|---|---|---|---|---|
| 0 | SL 9936 — WK-690 fix row: the three fix-before-close findings | FD-1349 (register `:281`), FD-1492 (`:318`) and FD-1512 (`:327`), each as its register row's Event states it; plus FD-1294's dated discharge line (R-F.1) | `02` §3.7: FR-146 (the certificate a `failed` `pseudo_huber` blocks), FR-157 (the metric evidence kind FD-1492 bypasses); `docs/contracts/schemas/objective-certificate.schema.json` (FD-1349, the guard's comparison) | Declared and versioned: unchanged (no new objective form; `pseudo_huber`'s declared loss is the same function, re-evaluated). Validated: FD-1512 removes a false `failed`; FD-1492 restores the submission evidence check. Audited: unchanged | nothing open: S1–S3 are closed and every cited line is on main at `d699a561` | at GO | 1 | **off the ladder** (DP-W-1 (a), ruled) |
| 1 | SL-1274 — S4: `expression` Factors | `PL-1268` Slice 4 (`:517-530`), plus R4.1–R4.3 | `02` §3.1: FR-95; §3.10: FR-208 (the expression arm); §4.1 `Factor`'s expression field; `RL-1265` DP-4's refusal naming FR-210; §9: NFR-483, NFR-484 | Declared: the `factor` profile (`02:940`), with the text stored on the Factor. Validated: parsed at create (422 with the position), undeclared columns refused at create, numeric-unbanded refused (DP-S4-1). Versioned: `Factor.version`, pinned by id (FR-96). Audited: `factor.created` | S1 (closed, met); DP-4 (`RL-1265`, met); **DP-S4-1 ruled** | at GO | 1 | **rung 6** |
| 2 | SL-1275 — S5: the authoring view and `WF-702` Route B | `PL-1268` Slice 5 (`:532-554`), plus R5.1–R5.4 | `02` §5.3 Custom objective library (editor, derived gradient and hessian display, loss-curve preview); §5.1: DP-S5-1's route and its new FR (spec first); §3.7: FR-145 (position-accurate parse through the route), FR-150 (editor gated), FR-152 (`violated` rendered as a finding); `06` §3.3: FR-367 (the route's permission); `WF-702` Route B B1.1–B4.3 and B4.6, and §7's failure rows; NFR-463; NFR-483 | Declared: text sent to the API only. Validated: the preview route, `/derive` and certify (FR-146). Versioned: create gives `draft`, and `derived` is stored with its tool version (B2.3). Audited: derive, certify and approve (NFR-484, built in S3); the preview route records nothing because it persists nothing | S3 (closed, met); OQ-550 (decided, met); DP-3 (`RL-1265`, met); **DP-S5-1 ruled** | at GO | 1 | **rung 3** |

### Changes since `PL-1268`, per slice

- **R4.1 — How a numeric result is banded (DP-S4-1).** `RL-1265` DP-4 (b) allows "only
  categorical or banded results". The `factor` profile has arithmetic operators only, and its
  EBNF `primary` has no string literal (`02:970`). Any result except a bare column symbol is
  therefore numeric, so **every useful `expression` Factor must be banded**. Nothing can band
  one at `d699a561`. `Factor` refuses a `banding_id` on any type except `banding`
  (`modelling.py:184-193`). `Banding.column` names one dataset column, and `_column_matches`
  (`factors.py:320-326`) checks it against `source_columns[0]`. S4 does not start until
  DP-S4-1 is ruled.
- **R4.2 — Where the numeric refusal fires.** It fires at resolution, as a
  `FactorResolutionError` naming FR-210, because the result type is known only once the
  expression is compiled against a frame. That is FR-208's own site and FR-87's
  "fails loudly" point. The undeclared-column refusal fires at creation, as `PL-1268:528` says.
  If DP-S4-1 (a) is ruled, a Factor declared with a `banding_id` is checked again at creation,
  so that the banding names the factor's own slug.
- **R4.3 — A rated model's expression input is not S4's.** `required_model_inputs`
  (`factors.py:338-349`; FR-240, `SL-1541` #1272) makes a model's inputs its factor slugs, so
  a rating algorithm must supply an expression Factor's value. Doing that means re-expressing
  the formula in ZEN, which is another grammar (`03` FR-244; `RL-1265` DP-5). S4 builds the
  modelling side only. Its `LG-` records the rating limb as "not started", owner the
  maintainer, event the P2 phase closure record, unless DP-S4-1's ruling places it elsewhere.
- **R5.1 — Live parse and preview through one stateless route (DP-S5-1).** `PL-1268:534-535`
  asks for "live parse errors (through the API, never a client-side parser)" and a loss-curve
  preview at chosen parameter values. B1.4 says "Parses on every keystroke". No route does
  either. The eight routes (`backend/src/app/api/custom_objectives.py:170-434`; `02` §5.1
  `:1843-1850`) are list, create, get, derive, certify, certificate, submit and usage. There is
  no edit route, and `/derive` refuses an already derived objective (`RL-1410` R4). **The
  precedent is `03` FR-1607** (`RL-1474`): the designer's
  `POST /api/v1/rating-algorithms/validate` "writes nothing, persists nothing and records no
  audit event", and the frontend re-implements none of its rules. S5 does not start until
  DP-S5-1 is ruled.
- **R5.2 — OQ-550 is decided, and S5 consumes it.** `docs/open-questions.md:41`: "DECIDED
  2026-09-30: (c), column descriptors `{ key, label, value }` … by `RL-1307`". `PL-1268:544`'s
  "otherwise records its `ChartFigure` caller in OQ-550's call-site count" branch no longer
  applies. The loss curve uses `RL-1307`'s form.
- **R5.3 — B4.4 and B4.5 are carried, not built.** These are the Approver's question and the
  Commentary Block resubmission (`06` FR-377, `06:168`; route `POST
  /api/v1/dossiers/{id}/commentary`, `06:607`). `git grep -il commentary -- backend/src` prints
  nothing at `d699a561`. `PL-1268` Acceptance item 7 already runs create → submit → two
  approvals without them. S5's `LG-` records B4.4–B4.5 as "not started", owner FR-377's Work,
  and the Route B file's docstring says the same.
- **R5.4 — The convexity heat map and draft editing are out of S5.** B4.3 names "the
  convexity heat map". `ObjectiveCertificateView.vue:19-22` records that under OQ-587's floor
  rule a heat map would be "a new requirement plus a contract change", and `PL-1268` S5 does not
  list it. There is no edit route either, so a wrong loss is corrected by creating a new
  objective. The editor creates and does not edit, unless DP-S5-1's ruling adds an edit limb.

- **R-F.1 — FD-1294 is discharged at main; only its dated line is owed.** The register row's
  event (`:218`) reads: "SL-1271 merges with the rule, and its acceptance proves `round(x, 2)`
  refused through each of the three callers (a `derive_expression` step, a `filter_rows` step
  and an `expression` check)". At `d699a561`,
  `packages/pricing-core/tests/test_expression_profiles.py:181-204` refuses `round(y, 2)`
  through each of the three, matching `round\(\) takes exactly 1 argument`. Those lines were
  added by `bd67fb51` ("feat(modelling): WK-690 Slice 1 — parser profiles, limits and the sympy
  pin; LG-1304 (#981)"), by the predicate `git log --format='%h %aI %s'
  -L181,205:packages/pricing-core/tests/test_expression_profiles.py origin/main`. The
  arity rule is `_ARITY` at `pricing_core/data/expressions.py:74` and is enforced at `:204-207`.
  The tests were read, not run, by this delta. The fix row's auditor runs them once at the
  close, before the line is written.
- **R-F.2 — The fix row's file set.** It is `backend/tests/test_contracts.py`,
  `backend/src/app/platform/metrics.py` with its tests, and
  `packages/pricing-core/src/pricing_core/modelling/objectives.py` (the `pseudo_huber`
  template) with its tests. It is disjoint from S4's. It overlaps S5 only if DP-S5-1's route
  reuses the template code, so the lead resolves that file set at S5's GO (`RL-1445`). No spec
  text changes: `02` §4.5 (`:880`) gives `pseudo_huber`'s parameter and purpose, not its
  arithmetic form.

### The cut-ladder rows (marked, not cut)

**S5 is rung 3** and is the first WK-690 slice a missed Friday line cuts. Cutting it leaves `02`
§5.3's editor, display and preview, and `WF-702` Route B over HTTP, to P3. That reaches
`PL-1268` Acceptance item 7, the Work's own close condition, which then needs the same dated
move line. **S4 is rung 6.** Cutting it leaves FR-95 and FR-208's expression arm to P3, with
FR-210, the gate its result rule waits on. Until a dated move line applies a rung, both rows
stand. **The fix row is off the ladder** (DP-W-1 (a), ruled): no rung cuts it, so a cut of S5 or S4
never carries a fix-before-close finding with it.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S4-1 | How is an `expression` Factor's numeric result banded, so that `RL-1265` DP-4 (b)'s "banded" case exists? (R4.1) | **(a)** `Factor` admits `banding_id` on `expression`: the result is banded by the pinned Banding, whose `column` names the factor's own slug. `02` §4.1 and FR-208 are amended, and the validator gains an arm. **(b)** An `expression` Factor is never fitted directly: it is a derived input that a `banding` Factor names. This is a new chain between Factors, and FR-92's operand pattern widens to `banding`. **(c)** No banding mechanism: S4 ships the field, the validator and the numeric refusal, so only a bare categorical column resolves, and FR-95 is delivered only nominally | **(a).** It is the smallest change. It reuses `apply_banding` and the FR-98–FR-103 boundary standard unchanged, and every such Factor gets FR-113's relativity table, which is what DP-4 (b) asked for. (b) adds a second resolution pass beside FR-92's for one case. (c) satisfies DP-4 by refusing everything, and the maintainer's rung 6 is the honest form of that outcome | decision point | **yes, for S4** | — (the decision-maker, by `RL-`) |
| DP-S5-1 | How does the editor get live parse errors and a loss-curve preview without persisting a draft per keystroke? (R5.1) | **(a)** One stateless route, e.g. `POST /api/v1/custom-objectives/preview`, takes the loss text, the parameters and a grid. It parses in the `objective` profile, derives, and evaluates the loss on the grid. It is flag-gated and needs `custom_objective:author`. It writes nothing and audits nothing (FR-1607's pattern). It lands spec first: a `02` §5.1 row and an FR. **(b)** Create a draft per debounce, then call `/derive`. That persists noise, and `RL-1410` R4 refuses re-derive. **(c)** Parse only on an explicit "Derive". That drops B1.4 and §5.3's "live parse errors", which is a spec change the other way | **(a).** FR-1607 is the same need, already ruled, for the designer. One route serves the parse, the display and the preview, so the frontend never holds a parser (`PL-1268:174`). It persists nothing, so there is no versioning or audit question, and the permission is FR-367's own | decision point | **yes, for S5** | — (the decision-maker, by `RL-`) |
| DP-W-1 | WK-690's four open findings have no slice: FD-1294 (register `:218`, carry; very likely discharged by `SL-1271`'s arity rule, so only its dated line is owed), FD-1349 (`:281`, carry, "a follow-up slice"), FD-1492 (`:318`, fix before close) and FD-1512 (`:327`, fix before close). Where are they built? | **(a)** A third WK-690 row, a fix slice that is not on the cut ladder, cut by a later delta. **(b)** Fold them into S5. That puts two fix-before-close findings behind rung 3. **(c)** Re-own them to WK-1178, the P2 maintenance Work | **(a).** Two of the four carry the verdict "fix before close", so the Work cannot close while they are open, and a ladder cut must not take a defect fix with it. The three fixes touch `platform/metrics.py`, `pricing_core/modelling/objectives.py` and `backend/tests/test_contracts.py`, which are disjoint from S4 and S5 | scope | no, for S4 and S5. **Yes, for the Work's close** | **RULED (a).** Adopted by the lead, from-lead "2026-10-11 11:20:43 BST — Lead: WK-1250 S3 and WK-690 S4/S5 readiness — both NOT READY; DP-F asked (yours); DP-W-1"; confirmed by the maintainer, to-lead "2026-10-11 11:21:02 BST — DP-F (WK-1250 S3 plan form): (a); DP-W-1 (a): confirmed; dm-wk690 seated: OK", item 2. The fix row is cut above (order 0) |

## Hand-off (not this plan's writes)

- The lead lists this delta on WK-690's roadmap row (L5). `SL-1274` and `SL-1275` already exist
  (`docs/roadmap.md:1528`, `:1547`, `draft`), so no `SL-` row is cut for them. **The fix row's
  `SL 9936` row is cut `draft` under `### WK-690` in `docs/roadmap.md` on this branch** (the
  planner's write, `document-ids.md` §1.6 SL row), with the working id the lead reserved. Each row's
  "relates" gains this delta's minted id at its GO.
- The decision-maker rules DP-S4-1 and DP-S5-1. When both carry a `Resolved by` id, the plan
  goes `active` by its status line (`document-ids.md` §1.6, the PL row).
- `PL-1371:210-211`'s "leaf plan" prep state for S4 and S5 is superseded by L5. The frozen plan
  is not edited.

## Self-review

- **Spec coverage.** Every id `PL-1268`'s Core scope assigns to Slices 4 and 5 is in a row:
  FR-95, FR-208 (the expression arm), `02` §5.3 Custom objective library, and `WF-702` Route B.
  The rows add the ids each slice's acceptance exercises: FR-145, FR-150, FR-152, FR-367,
  NFR-463, NFR-483 and NFR-484. Every open register row owned by WK-690 is placed: FD-1349,
  FD-1492 and FD-1512 in the fix row, and FD-1294's discharge line (R-F.1). The predicate is
  `grep -n 'WK-690' docs/findings/register.md`, which prints six rows: `:182` (FD-1195, resolved,
  WK-1178's), `:326` (FD-1511, resolved by SL-1273), and these four. B4.4–B4.5 are carried (R5.3), not dropped.
- **Placeholders.** None. The route path in DP-S5-1 (a) is illustrative, and the ruling names
  it. The Route B file name is fixed here (`backend/tests/test_wf702_route_b.py`), as
  `PL-1268` Acceptance item 7 asked the slice plan to do.
- **Consistency.** The order is reverse ladder order, the same principle as `PL-1546`.
  `PL-1268:376-391` makes S4 depend on S1 only and S5 on S3 only, so no dependency is reversed.
  The DP ids are new and do not reuse `PL-1268`'s DP-1 to DP-5.
- **Collisions.** Of the 2 open PRs (one `gh pr list --state open --json files` call,
  2026-10-11 ~10:20Z), #1273 (`sl-1600-input-free-error` @71d578ae) touches
  `model_schema/modelling.py` from `:385` on. That is past `Factor` (`:122-250`), so there is
  no overlap, and it merges well before S4's ETA (`eta-p2-2026-10-11.md:54`: Fri 23 Oct). The
  per-branch check over the open build branches is re-run at each slice's GO, because a
  branch's file set at 23 Oct is not today's.
