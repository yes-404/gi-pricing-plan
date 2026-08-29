# W11 Slice 1 — Evaluator Core, its Prerequisites, and the Latency Harness

> **For agentic workers:** REQUIRED SUB-SKILL: use `subagent-driven-development`
> (recommended) or `executing-plans` to implement this plan task-by-task, plus
> `test-driven-development` and `git-hygiene` — the three skills
> [`.claude/roles/executor.md`](../../.claude/roles/executor.md) makes mandatory for this
> role. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `score_one` — the single evaluator that FR-RATE-37 requires real-time and
batch to share — together with the four prerequisites that do not exist without which it
cannot be written, and the bare-metal latency harness `../roadmap.md` requires be built
"alongside the evaluator, not after".

**Architecture:** Five tasks, strictly sequential, each an independently reviewable PR.
1.1 wires the rating-version write routes so a test can create a real Rating Version;
1.2 makes the compile resolver return real content and persists the `Bundle` behind a
`RATING_COMPILE` Job; 1.3 adds `CompiledBundle` and `load_bundle`, including the
`JdmGraph` → JDM wire-format translation that does not exist today; 1.4 builds `score_one`
on the engine's `async_evaluate()`; 1.5 measures it. Each task's output is the next task's
input, so none of them can be reordered or run in parallel.

**Tech Stack:** `pricing-core` (standalone, zero FastAPI/SQLAlchemy/Redis deps — ADR-0001,
enforced by `.importlinter`'s `core-has-no-infrastructure` contract); `zen-engine==0.53.0`
via `import zen` (declared in `packages/pricing-core/pyproject.toml:53`, the only
declaration in the workspace); FastAPI async routes; the Celery/Redis Job machinery of
[`../specs/07-platform.md`](../specs/07-platform.md); the content-addressed blob store
(`backend/src/app/platform/blobs.py`); XGBoost/glum boosters via
`pricing_core.modelling.gbm.predict_gbm` and `pricing_core.modelling.predict.predict_glm`.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) — §2 (Quote
Context glossary, `:63`), §3.7 real-time scoring, §3.8 batch scoring, §3.11 numeric
precision at the engine boundary (`:200`), §4.3–§4.5 the data contracts, §5.1 the
endpoint table, §5.2 the function signatures, §9 the non-functional budgets.
**Contract:** [`../contracts/schemas/scoring.schema.json`](../contracts/schemas/scoring.schema.json)
— the hand-authored tier, which already defines `QuoteContext`, `LadderRung`,
`ScoringResult` and `Trace`. Read
[`.claude/skills/contract-guard`](../../.claude/skills/contract-guard/SKILL.md) before
citing it: `docs/contracts/schemas/*.schema.json` is *specified* and hand-authored,
`docs/contracts/schemas/generated/*` is *generated* and enforced, and the two are
different obligations.

**Slice source:** [`2026-08-29-w11-scoring.md`](2026-08-29-w11-scoring.md), the frozen W11
sequencing plan — Slice 1, tasks 1.1–1.5. **That file is frozen and is not edited by this
one.** Where this plan's evidence contradicts it, the contradiction is recorded in
*Corrections to the frozen map* below and the map is left standing as the record of what
was believed, per [`README.md`](README.md)'s "a filed plan is a record, not an
instruction".

**Rulings this plan rests on, cited by number and not re-argued:**
[`2026-08-29-w11-prework-rulings.md`](2026-08-29-w11-prework-rulings.md) Rulings 1–5.
**Decision points recovered but not ruled:**
[`2026-08-29-w11-decision-points-recovery.md`](2026-08-29-w11-decision-points-recovery.md)
items 1, 4 and 5 bear on Tasks 1.3 and 1.4.

**Process:** [`../process/delivery-process.md`](../process/delivery-process.md) §6 (the
Slice TDD cycle), §7 (the ≤ 2 re-audit guard, whose instrumentation starts with this
slice — it is the pilot), §8 (no two slices at once; read-only fan-out permitted).

**Rulings 6–11, filed in PR #368 (`docs/plans/2026-08-29-w11-slice1-rulings.md`) while
this plan was being written.** They land after this plan's own evidence sweep and they
change five things in it; each is applied below and named where it applies. Ruling 6 rules
DP3 and **unblocks Task 1.5**. Ruling 7 fixes `load_bundle`'s signature and appends it to
`03` §5.2. Ruling 8 opens the loaded-booster seam. Ruling 9 rules the decline
representation. Ruling 10 gives Task 1.3 two properties it owes W14. Ruling 11 confirms
`MODEL_CALL_FAILED` and corrects this plan's error-raising convention. **PR #368 also edits
`03-rating-engine.md` §3, §5.1 and §5.2**, so every `03:NNN` line number below — all
verified at `7b8473a`, before that PR — shifts once it merges. Re-derive rather than trust
them: `git grep -n 'FR-RATE-39' docs/specs/03-rating-engine.md`. The requirement ids are
permanent; only the line numbers move.

**Highest ids in use, verified at `7b8473a` by scanning
[`../specs/03-rating-engine.md`](../specs/03-rating-engine.md):** FR-RATE-65,
NFR-RATE-14. Next free: `FR-RATE-66`, `NFR-RATE-15`. **This plan mints none of them.** It
cites ids that already exist and proposes no new one. The line is republished because
[`2026-08-29-w11-scoring.md`](2026-08-29-w11-scoring.md)'s own copy was verified at
`d708be3` and this plan is written against a later tree; a stale allocation aid is what
mints a colliding id. Four error codes are registered in Task 1.4 — all four are already
owned by `03` §5.1, `MODEL_CALL_FAILED` as of Ruling 11 — and error codes are a separate
namespace from `FR-`/`NFR-`/`OQ-` ids, so this marker does not cover them.

---

## Acceptance standard for the slice as a whole

`delivery-process.md` §3 requires every plan to state one explicitly and testably. Slice 1
is accepted when **all five** hold, each by a command a fresh reviewer can run:

1. **A real Rating Version can be created, submitted and compiled entirely over HTTP**, and
   the compiled `Bundle` — graph *and* resolved payloads, not only its metadata — is
   retrievable afterwards from the blob store by its content hash.
2. **`score_one` prices that Bundle.** `await score_one(load_bundle(bundle), ctx)` returns a
   `ScoringResult` whose `premium_ladder` reconciles to `payable_premium_minor` to the
   penny, on generated contexts rather than one example (NFR-RATE-8).
3. **Every invariant introduced has a negative test that has been seen to fail**, marked
   `@pytest.mark.req("<id>")`. `CLAUDE.md` §13 rule 4: a check that has never printed a
   failure has not been tested. Each task below names its own broken input.
4. **The full local gate passes, both halves** — the Python/docs half and the frontend half.
   A Python-only gate has been green in this repository while the frontend was red.
5. **NFR-RATE-1 (component), 2, 3, 4, 7, 8 and 14 are measured and written down** in a dated
   note under [`../research/`](../research/), not left as terminal output.

**Not in this slice, and not a gap:** the HTTP scoring endpoint, the sustained-200 rps
measurement, the default-live version resolution and the approval gate are Slice 2's;
`score_batch` is Slice 3's; trace *sampling and persistence* is Slice 4's (Task 1.4
captures a `Trace`, it does not sample or store one).

## Global Constraints

Every task's requirements implicitly include this section.

- **Money is integer minor units or `Decimal`, never `float`** —
  [`../../CLAUDE.md`](../../CLAUDE.md) §7, FR-RATE-29/56.
  `pricing_core.money.apply_factor(amount_minor: int, factor: Decimal, mode: RoundingMode)
  -> int` and `pricing_core.money.reconcile_ladder(risk_premium_minor: int, steps:
  list[tuple[str, int]]) -> bool` are the only ladder-arithmetic primitives. `apply_factor`
  raises `TypeError` on a non-`Decimal` factor and `mode` has **no default** — FR-RATE-12
  requires rounding be declared per step. Do not reimplement either.
- **FR-RATE-56 — money crosses the engine boundary only as integer minor units.** The
  binding rejects `Decimal` outright and returns `float` for everything. Verified live at
  `7b8473a`: a three-step expression graph seeded with `{"base": 1000}` returns
  `{'v0': 1002, 'v1': 1004.002, 'v2': 1006.006002}` — Python floats. Fractional
  relativities may be *held* in rate tables and applied *inside* the engine; anything
  returning to Python for further arithmetic is an integer minor unit or a string.
- **FR-RATE-57 — division by zero returns `null` silently and raises only where the null is
  *used*.** Every division in a rateable path carries an explicit zero guard, and a `null`
  reaching an `output` step is a hard error. `validate_algorithm` already enforces this at
  compile time (`_check_division_guards`, `compile.py:165`); Task 1.4 must not let a `null`
  through at *run* time either.
- **FR-RATE-37 — real-time and batch share the identical compiled bundle and code path.**
  Slice 3 proves this by byte-identical comparison against Task 1.4's `score_one`. Task 1.4
  must therefore keep per-step evaluation in a function `score_batch` can call directly,
  not inline it inside `score_one`'s own body.
- **NFR-RATE-3 — a compiled bundle scores with zero database or network access.** Proven,
  not asserted: Task 1.4's gate blocks DB and network during `score_one` *and* shows the
  test fails when a deliberate DB call is inserted.
- **A negative test for every invariant introduced**, marked `@pytest.mark.req("<id>")`.
- **Spec-vs-code disagreement is a finding, stopped and resolved, never silently matched**
  ([`../../CLAUDE.md`](../../CLAUDE.md) §0). Three are already open below; a fourth is
  raised, not fixed in passing.
- **Worktree hygiene:** your own worktree, never `git checkout`/`git switch` outside it,
  `pwd` + `git branch --show-current` before every git write.
- **The gate, both halves, run locally before every push:**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
```

There is no frontend work in this slice — W15 owns the scoring UI — but new `model-schema`
types regenerate the OpenAPI client, so `generate:api` and `type-check` must still pass.

---

## Verified facts at `7b8473a`

Everything in this section was checked against shipped source or a live call at the pinned
commit, not taken from the map plan's prose. `docs/plans/README.md`'s rule 1 — verify every
repository literal against the shipped source before it enters sample code — is why this
section exists at all: the map plan is a *record*, and three of its literals turned out to
be wrong (see *Corrections* below).

### The ZEN binding, measured live

`import zen` (not `zen_engine`). `zen-engine==0.53.0`, declared only in
`packages/pricing-core/pyproject.toml:53`. The API surface, from the installed stub
`.venv/lib/python3.13/site-packages/zen/__init__.pyi`:

```python
class DecisionEvaluateOptions(TypedDict, total=False):
    max_depth: int
    trace: bool

class EvaluateResponse(TypedDict):
    performance: str
    result: dict
    trace: dict

ZenContext: TypeAlias = Union[str, bytes, dict]
ZenDecisionContentInput: TypeAlias = Union[str, ZenDecisionContent]

class ZenEngine:
    def __init__(self, options: Optional[dict] = None) -> None: ...
    def create_decision(self, content: ZenDecisionContentInput) -> ZenDecision: ...

class ZenDecision:
    def evaluate(self, context: ZenContext, options: Optional[DecisionEvaluateOptions] = None) -> EvaluateResponse: ...
    def async_evaluate(self, context: ZenContext, options: Optional[DecisionEvaluateOptions] = None) -> Awaitable[EvaluateResponse]: ...
    def validate(self) -> None: ...
```

Five facts follow, each verified by running it at `7b8473a`, and each load-bearing on a
task below.

1. **`create_decision` takes a JSON *string*** (or a `ZenDecisionContent` wrapping one) —
   not a dict. `json.dumps(graph)` is the call.
2. **The real JDM wire format is a `{"nodes": [...], "edges": [...]}` pair**, where nodes
   are a **list** of `{"id", "type", "name", "position", "content"}` and edges are explicit
   `{"id", "type": "edge", "sourceId", "targetId"}`. This is *not* the shape `to_jdm`
   produces — see Task 1.3.
3. **`passThrough` decides whether intermediate values survive.** With the default, the same
   graph returns only the final key: `{'v2': 1006.006002}`. With
   `"passThrough": true` on each expression node it returns
   `{'base': 1000, 'v0': 1002, 'v1': 1004.002, 'v2': 1006.006002}`. **The premium ladder
   needs every rung**, so the translation in Task 1.3 must set it. Getting this wrong
   produces a `ScoringResult` with a correct `payable_premium_minor` and an empty ladder —
   which passes a naive golden test and fails NFR-RATE-8.
4. **`options={"trace": True}` is the engine-native trace**, and it is exactly the shape
   FR-RATE-41 wants. The response gains a `trace` key holding one entry per node:
   `{"id", "input", "name", "order", "output", "performance", "traceData"}`. Note
   `performance` is a **string** (`'4.2µs'`), while
   `scoring.schema.json`'s `Trace.steps[].elapsed_us` is `{"type": "integer", "minimum": 0}`
   — parsing, not passing through.
5. **Custom nodes are how `model_call` is built, and the option key is `customHandler`.**
   A node of `"type": "customNode"` validates, and evaluating one without a handler raises
   `RuntimeError: {"type":"NodeError","source":"Custom node handler not provided","nodeId":"c"}`.
   Supplying `zen.ZenEngine({"customHandler": fn})` makes it work: `fn` receives a
   `builtins.PyNodeRequest` and returns `{"output": {...}}`.
   **Trap: `ZenEngine.__init__` accepts any options key without complaint** — `custom_handler`,
   `customNodeHandler`, `function_handler` and `handler` were all accepted by the
   constructor and all failed at *evaluate* time with the same "handler not provided"
   error. A wrong key is silent until the node runs. Verify the handler is invoked, never
   that the constructor accepted the option.

A minimal, verified-runnable graph, for use as the Task 1.3 fixture:

```python
import json, zen

graph = {
    "nodes": [
        {"id": "input", "type": "inputNode", "name": "Request", "position": {"x": 0, "y": 0}},
        {"id": "step0", "type": "expressionNode", "name": "step0", "position": {"x": 50, "y": 0},
         "content": {"expressions": [{"id": "e0", "key": "v0", "value": "base * 1.001 + 1"}],
                     "passThrough": True}},
        {"id": "output", "type": "outputNode", "name": "Response", "position": {"x": 100, "y": 0}},
    ],
    "edges": [
        {"id": "ed0", "type": "edge", "sourceId": "input", "targetId": "step0"},
        {"id": "ed1", "type": "edge", "sourceId": "step0", "targetId": "output"},
    ],
}
decision = zen.ZenEngine().create_decision(json.dumps(graph))
decision.validate()
decision.evaluate({"base": 1000})
# -> {'performance': '...', 'result': {'base': 1000, 'v0': 1002}}
```

A `decisionTableNode`'s `content` is
`{"hitPolicy", "rules", "inputs", "outputs", "passThrough", "inputField", "outputPath",
"executionMode"}`, where `inputs`/`outputs` are lists of `{"id", "name", "field"}` and each
rule is `{"_id": "r1-1", "<input id>": "<condition>", "<output id>": "<expression>"}` — the
rule keys are the input/output **ids**, and the values are expression strings. This is the
node type a `table`/`lookup` step maps to.

### What exists, and what does not

| Thing | State at `7b8473a` |
|---|---|
| `Bundle` | Exists — `pricing_core/rating/compile.py:350`, frozen `BaseModel`: `algorithm_ref`, `graph`, `resolved_payloads`, `pins`, `content_hash`, `compiled_at` |
| `JdmGraph` | Exists — `compile.py:308`: `slug`, `version`, `input_contract`, `outputs`, `nodes: dict[str, dict[str, Any]]` |
| `to_jdm` | Exists — `compile.py:325`. Produces a **dict keyed by `step_id`**, not the engine's node list |
| `compile_bundle` | Exists, **`async def`** — `compile.py:387` |
| `bundle_hash` | Exists — `compile.py:367`, returns `"sha256:" + hexdigest`, matching the contract's `^sha256:[a-f0-9]{64}$` |
| `assert_integer_minor_round_trip` | Exists — `compile.py:67`. **Called from one place, a test.** See finding F-W11-1-3 |
| `CompiledBundle` | **Does not exist in any `.py` file.** 57 hits repo-wide, every one in a `.md` |
| `load_bundle` | Does not exist |
| `score_one` / `score.py` | Does not exist. `pricing_core/rating/` holds `__init__.py` and `compile.py` only |
| `QuoteContext` / `ScoringResult` / `Trace` | No Python class. **They do exist as `$defs` in the hand-authored `docs/contracts/schemas/scoring.schema.json`** |
| `pricing_core/rating/__init__.py` | A docstring and nothing else — no re-exports. Import from `pricing_core.rating.compile`, never `from pricing_core.rating import Bundle` |
| `POST /api/v1/rating-versions` | No route. `grep -rn '"/rating-versions"' backend/src/app/api/` returns one hit, the `GET` list route |
| `POST /api/v1/rating-versions/{id}/submit` | No route. `Permission.RATING_SUBMIT` appears exactly once in `backend/src/app/`, inside `submit_for_review`'s own body |
| `POST /rating-versions/{id}/compile` | Exists at `backend/src/app/api/models.py:1139`, returns **200**, docstring says so explicitly |
| `JobKind.RATING_COMPILE` | Exists (`model_schema/jobs.py:53`), routed to `JobQueue.DEFAULT` (`platform/jobs.py:72`), **no registered handler** |
| `MODEL_CALL_FAILED` | Not in `backend/src/app/errors.py` |
| `INPUT_CONTRACT_VIOLATION`, `REFERENCE_LOOKUP_MISS` | Named in `03` §5.1 (`:530-531`); **not registered in `errors.py`** |
| `RATE_TABLE_MISS`, `EVIDENCE_INCOMPLETE` | Registered — `errors.py:290`, `:254` |
| `nthread` / `n_jobs` anywhere in `pricing_core` | Zero hits. See finding F-W11-1-2 |

### The register rows this slice must honour

`delivery-process.md` §9 requires every slice plan to read the relevant rows of
[`../audit/register.md`](../audit/register.md) before it is finalised.

The register holds 23 rows; seven concern rating. All seven are listed, because a row
skipped silently is indistinguishable from a row that does not exist.

| Row | Bearing on Slice 1 |
|---|---|
| `NFR-RATE-13/14 (F-W9-1)` | **This slice's obligation.** Carried forward with an owner — "the W11 scoring workstream". Task 1.4's `nthread=1` measurement and Task 1.5's harness discharge the NFR-RATE-14 half; the NFR-RATE-13 half needs the HTTP path and is Slice 2's. The row already records W8's figures — NFR-RATE-13 p99 0.070 ms, NFR-RATE-14 p99 1.626 ms — so the measurement here is a re-measurement on the real path, not a first one |
| `03 rating surface (F8)` | The phase-boundary row that covers "compile, score, rate tables, deployment". W11 discharges its scoring quarter |
| `FR-RATE-61 (F-W9-2)` | Carried forward to **W13**, but its own decision text says the check "specialises FR-RATE-40's general approval-evidence gate, **which W11 builds**". FR-RATE-40 is Slice 2's, not this slice's — recorded so the dependency is visible when Slice 2 is planned |
| `FR-RATE-17 (F-W10-2)` | Carried forward with an owner (portfolio-dataset integration). **Not this slice's** |
| `FR-RATE-17/18/19/20 (F-W10-1)` | W10's, half resolved by PR #302. Not this slice's |
| `FR-RATE-16 (F-W10-1-1)` | Resolved 2026-08-28 (PR #302). Closed |
| `03 §5.1 POST /rate-tables/{slug}/versions (F-W10-3)` | Carried forward to the W15 rate-table editor slice. Not this slice's |

**Nothing in the register blocks Slice 1.** One row (`F-W9-1`) is discharged in part by it;
the rest are recorded as not-this-slice's so a later audit can see they were read rather
than missed.

---

## Corrections to the frozen map

The map plan is left standing. These are recorded so an executor reading both is not
misled, and so the next map revision has them.

**C1 — `_Resolver` has two branches, not four.** The map describes the `model` branch plus
"every other ref type (`rate_table`, `reference_table`, `custom_objective`) raises
`NOT_FOUND`". In fact `_Resolver.resolve()` (`rating_versions.py:241-271`) has explicit
branches for `rating_algorithm` (which resolves *for real*, returning `algo.content`) and
`model` (which returns the placeholder `{"status": model.status}`), and then a **single
catch-all `raise`** covering everything else. The map's omission of the working
`rating_algorithm` branch matters: Task 1.2 adds three new branches *before* an existing
catch-all, it does not repair three broken ones.

**C2 — `predict_gbm` is not in `predict.py`.** The map pairs
"`predict_gbm`/`predict_glm`" as though they were siblings. `predict_glm` is
`pricing_core/modelling/predict.py:230`; `predict_gbm` is
`pricing_core/modelling/gbm.py:1185`, and `predict.py`'s own `__all__` does not list it.

**C3 — neither predictor takes `nthread`.** The map's Task 1.4 says `model_call` delegates
"to `predict_gbm`/`predict_glm` with `nthread=1`", which reads as passing an argument.
Neither function has such a parameter and `grep -rn "nthread\|n_jobs\|num_thread"
packages/pricing-core/src/` returns nothing. NFR-RATE-14 therefore requires a *change* to
how the booster is constructed, not a keyword at the call site. See finding F-W11-1-2.

**C4 — `DislocationRun.largest_movers_blob` does not exist.** The map cites it as the
precedent for Task 1.2's blob write. `grep -rn "largest_movers" --include="*.py"` returns
nothing, and `JobKind.DISLOCATION_RUN` has no handler. The real precedent is
`backend/src/app/worker/rate_table_handlers.py:38-54`, quoted verbatim in Task 1.2.

**C5 — the map's Slice 1 requirement list omits FR-RATE-65.** FR-RATE-65
(`03-rating-engine.md:139`) is the requirement that *defines* `CompiledBundle` as a
distinct runtime type; Task 1.3 is what discharges it. It is added to the coverage table
below.

---

## Findings raised by this plan

Each is verified at `7b8473a` by a full-class sweep, per `delivery-process.md` §11. None is
fixed in passing; each carries a recommendation and a named owner.

**F-W11-1-1 — `QuoteContext.purpose` disagrees between the spec and its own contract.
Blocks Task 1.4.**
`03-rating-engine.md:63` defines five values — `new_business | renewal |
mid_term_adjustment | cancellation | what_if` — and carries a dated note: *"`cancellation`
was added 2026-08-18 with FR-RATE-63: OQ-RATE-4's answer mounts the refund sub-graph on
`purpose`, and the value it keys on has to exist."*
`docs/contracts/schemas/scoring.schema.json:13` defines four:
`["new_business", "renewal", "mid_term_adjustment", "what_if"]`. The hand-authored contract
was never updated when §2 gained the value.
This is not cosmetic. FR-RATE-63's refusal guard fires on
`purpose ∈ {mid_term_adjustment, cancellation}`; if `QuoteContext` cannot express
`cancellation`, one limb of that disjunction has no test that can even be written, and the
guard would ship half-proven while looking complete.
**Owner: the decision-maker** — `delivery-process.md` §3 makes spec-vs-code conflicts
theirs, never the planner's. **Recommended resolution:** the spec is right and the contract
is stale; add `"cancellation"` to `scoring.schema.json`'s enum. Task 1.4 does not start its
`purpose` handling until this is ruled. Raised to the lead and the decision-maker
2026-08-29, against task #34.

**F-W11-1-2 — NFR-RATE-14's `nthread=1` has no implementation surface.**
`03-rating-engine.md` states GBM `model_call` steps execute with `nthread=1` per request.
No thread-count control exists anywhere in `pricing_core` (zero grep hits for
`nthread`/`n_jobs`/`num_thread`/`thread_count`), and `predict_gbm` builds its booster with
`xgb.Booster()` / `load_model` / `DMatrix` / `predict` and sets no thread parameter.
**Owner: Task 1.4** — it is the first caller that has to satisfy the requirement.
**Recommended resolution:** add an explicit, keyword-only `nthread: int | None = None`
to `predict_gbm`, applied via the booster's own parameter, rather than setting a process-wide
environment variable — a global would silently change every other caller's behaviour,
including the fit path. The measurement is a Task 1.4 exit criterion regardless.
**Superseded in scope by Ruling 8 (PR #368)**, which found the larger defect in the same
function: `predict_gbm` re-loads the booster on *every* call, so a thread setting alone
would tune a path that should not be running at all. Task 1.3 builds the loaded-booster
seam; this finding's `nthread` half rides on it.

**F-W11-1-3 — FR-RATE-56's startup self-check exists as a function and is wired to
nothing.**
FR-RATE-56 (`03-rating-engine.md:220`) ends: *"A startup self-check asserts the round-trip;
failing it prevents the service starting."* `assert_integer_minor_round_trip`
(`compile.py:67`) exists and its own docstring says it *is* that check. Its only caller in
the repository is `packages/pricing-core/tests/test_rating_compile.py:70`. The backend's
`lifespan` (`backend/src/app/main.py:70-81`) registers two health probes and ensures the
blob bucket; it does not call it. The W9-2 audit record booked FR-RATE-56 "delivered" on
the strength of the function and its test.
**A validator with no production caller is not enforcement.** The full-class sweep behind
this: `git grep -n "assert_integer_minor_round_trip"` returns four hits — the definition,
the `__all__` entry, one test import, one test call — and `git grep -nE "\b(zen|ZenEngine)\b"
-- backend/src packages/*/src` returns three hits, all in `compile.py`, so no engine handle
is constructed anywhere in shipped source today.
**Owner: Task 1.4**, which is where the binding first enters the service's runtime path.
**Recommended resolution:** call it from `lifespan`, and add the negative test that a
failing self-check prevents startup. It is two lines and one test; carrying it as a
deferral would cost more to track than to close.

---

## Requirement coverage

Every id listed individually. A bare numeric range silently drops an append-only id landed
inside it — `../audit/plan-reviews.md` review 8 Q4 found that mechanism twice.

| Requirement | Where in `03` | Discharged by | How it is proven |
|---|---|---|---|
| FR-RATE-34 | §3.7 | Task 1.4 | Golden test: a known Bundle + QuoteContext gives an exact pre-computed ScoringResult. **Excludes** the default-live resolution, which is Slice 2's |
| FR-RATE-38 | §3.7 | Task 1.4 | One typed-error test per category, each fired by a deliberately malformed context |
| FR-RATE-39 | §3.7 | Task 1.4 | A constraint decline returns `outcome: "declined"` with a populated ladder and a non-empty `decline_reasons` — never an HTTP error |
| FR-RATE-41 | §3.7 | Task 1.4 | `trace=True` returns a `Trace` matching `scoring.schema.json`'s `$defs/Trace`; `trace=False` returns `None` |
| FR-RATE-63 | §3.1 (`:87`) | Task 1.4 | Refusal-guard test on broken input — **blocked by F-W11-1-1 for the `cancellation` limb** |
| FR-RATE-64 | §3.7 | Task 1.4 | The `instalment_loading` rung appears in the ladder and reconciles |
| FR-RATE-65 | §3.4 (`:139`) | Task 1.3 | `CompiledBundle` exists as a distinct type from `Bundle` and refuses serialisation |
| FR-RATE-22 citation | §5.1 (`:512`) | Task 1.1 | `audit-docs.py` clean with the citation added |
| FR-RATE-24/25 | §3.4 | Task 1.2 | Round-trip: compile, fetch the persisted Bundle, confirm graph and payloads survive |
| FR-RATE-56 (runtime half) | §3.11 (`:220`) | Task 1.4 | See F-W11-1-3 — the startup call and its negative test |
| NFR-RATE-1 (component) | §9 | Tasks 1.4, 1.5 | Bare-metal p99 against the budget. The **full-path and sustained-load** halves are Slice 2's |
| NFR-RATE-2 | §9 | Task 1.5 | Traced vs untraced p99 delta against the budget |
| NFR-RATE-3 | §9 | Task 1.4 | DB and network blocked during `score_one`, and the test shown to fail with a deliberate DB call inserted |
| NFR-RATE-4 | §9 | Task 1.3 | Compile time and Bundle size for a real large structure |
| NFR-RATE-7 | §9 | Task 1.4 | Same hash + same context, twice, in-process and in a subprocess, byte-identical |
| NFR-RATE-8 | §9 | Task 1.4 | `reconcile_ladder` over generated contexts, not one example |
| NFR-RATE-14 | §9 | Task 1.4 | `nthread=1` on the real `model_call` path, p99 over ≥ 1000 calls. See F-W11-1-2 |

**Deliberately excluded, each with its owner:** FR-RATE-35, 40 and the default-live half of
34 → Slice 2. FR-RATE-36, 37 → Slice 3. FR-RATE-42 → Slice 4. FR-RATE-43, 44, 45 → W12.
FR-RATE-46, 47, 48, 49 → W13. FR-RATE-50 and FR-PLAT-28 → W14. NFR-RATE-5 → Slice 3.
NFR-RATE-9, 11, 13 → Slice 2. NFR-RATE-12 → Slice 4.

---

## Sequencing and blockers

| Task | Depends on | Blocked by | Why it cannot move |
|---|---|---|---|
| 1.1 Route wiring | — | — | Everything downstream needs a real, non-seed Rating Version to test against |
| 1.2 Resolver, persistence, Job | 1.1 | — | Nothing compiles to a useful Bundle today, so 1.3 has nothing to load |
| 1.3 `CompiledBundle` + `load_bundle` | 1.2 | — | `score_one`'s first parameter does not exist until this lands |
| 1.4 `score_one` | 1.3 | **F-W11-1-1** (the `purpose` enum only) | The evaluator |
| 1.5 Latency harness | 1.4 | — (**DP3 ruled**, Ruling 6) | Measures 1.4 |

Strictly sequential — `delivery-process.md` §8's "no two children of a layer at once" is
satisfied by the dependency chain itself, not only by the rule. Read-only evidence fan-out
inside a task is permitted by the same section.

**F-W11-1-1 blocks only the `purpose` handling inside Task 1.4**, not the task. An executor
can build and gate the ladder, the step types, the error typing and the trace before it is
ruled, then add the guard. Do not guess the enum.

**DP3 (load-generation tooling) is ruled** — Ruling 6, PR #368: `scripts/bench-rating.py`
is stdlib-only and follows `bench-model.py`'s shape; no new dependency, no `03` §8 row and
no `skills-map.md` row is owed. **Task 1.5 is not blocked.** The ruling states its own
acceptance test as a violation: if a later PR adds `locust`, `k6`, `hey` or `wrk` to any
`pyproject.toml`, `uv.lock`, CI workflow or setup instruction for this measurement, the
ruling has been overridden and needs a successor record.

**F-W11-1-4 — FR-RATE-64 carries a second refusal that the map plan does not mention.**
The map's Task 1.4 takes FR-RATE-64 as "the `instalment_loading` ladder rung". Its full
text (`03-rating-engine.md:163`) also says the platform *"never emits a payment schedule, an
APR figure, or a credit agreement term. **A Quote Context asking for one is refused** rather
than answered approximately, because an APR that is nearly right is a compliance defect and
not a rounding one."* That is a second guard, with its own broken-input test, and reading
the row's first sentence only would ship the rung and miss it.
**Owner: Task 1.4.** Both halves are exit criteria there.

**F-W11-1-5 — `03` §5.2 puts the money primitives in a module the code does not have, and
names a parameter the code does not use.**
§5.2 (`:615-617`) declares `pricing_core/rating/money.py` with
`apply_factor(amount_minor: int, factor: Decimal, rounding: Rounding) -> int`. The shipped
code has `pricing_core/money.py` with
`apply_factor(amount_minor: int, factor: Decimal, mode: RoundingMode) -> int`. Both the
module path and the third parameter's name differ.
This matters here only because an executor implementing Task 1.4 from §5.2 would import
from a path that does not exist and pass a keyword that is not accepted.
**Owner: the decision-maker** — it is a spec-vs-code conflict, which
`delivery-process.md` §3 makes theirs. **Recommended resolution:** the code is right and the
spec is stale — `pricing_core/money.py` is imported by the shipped rating path and moving it
would break `pricing_core`'s public surface for a naming preference. The correction is a
dated amendment to §5.2, not a code move. **Not a blocker:** Task 1.4 imports from the real
path regardless, and this plan states it (Global Constraints) so the executor never reads
§5.2 for it.

---

## Task 1.1 — Wire `POST /rating-versions` and `POST /rating-versions/{id}/submit`

**Ruling 1.** The defect: `create_rating_version` (`rating_versions.py:93`) and
`submit_for_review` (`:141`) are built, RBAC-checked, audited and tested, and reachable over
HTTP from nowhere. Their only non-test caller in the repository is the demo seed
(`examples/fremtpl2/model.py:326,333`), an in-process call. `Permission.RATING_SUBMIT`
appears exactly once in all of `backend/src/app/` — inside `submit_for_review`'s own body.
`03` §5.1 has specified both routes since it was written (`:513`, `:515`).

**Why it runs first:** every later task in this slice needs a real, non-seed Rating Version
to compile and score against, and today one can only be made from inside a test process.

**Files**
- Create: `backend/src/app/api/rating_versions.py` — a new router module, matching
  `backend/src/app/api/rating_algorithms.py`'s shape (module docstring citing the spec
  section and the slice, `__all__ = ["router"]`, `router = APIRouter(tags=["rating"])`, and
  `Annotated[Caller, Depends(requires(Permission.X))]` aliases).
- Modify: `backend/src/app/main.py` — add `app.include_router(rating_versions.router,
  prefix=API_PREFIX)` to the block at `:110-129`, beside `rating_algorithms`.
- Create: request bodies in `packages/model-schema/src/model_schema/rating.py`.
- Modify: `docs/specs/03-rating-engine.md:513` — add the `(FR-RATE-22)` citation Ruling 1
  names. `docs/workflows/wf-02-model-to-rating-version.md:56` already relies on it.
- Test: `backend/tests/test_rating_versions.py`.

**Interfaces**
- *Consumes* (all exist — do not change their bodies):
  - `rating_versions_service.create_rating_version(session, *, workspace_id: UUID, actor: Principal, slug: str, dataset_version_id: UUID, model_ref: ArtifactRef) -> RatingVersionRow`
  - `rating_versions_service.submit_for_review(session, *, workspace_id: UUID, actor: Principal, rating_version_id: UUID, change_summary: str) -> tuple[RatingVersionRow, ApprovalRequestRow]`
  - `rating_versions_service.to_schema(row: RatingVersionRow) -> RatingVersion`
- *Produces* (Tasks 1.2–1.5 rely on these):
  - `POST /api/v1/rating-versions` → **201** with a `RatingVersion` body
  - `POST /api/v1/rating-versions/{rating_version_id}/submit` → **200** with a `RatingVersion` body

**Type the request bodies; do not take `dict[str, Any]`.** `rating_algorithms.py:34` takes
an untyped body, and that is the pattern this task should *not* copy: register finding
`F-W10-2-2` was raised against exactly that shape ("the ADR-0002 divergence class, invisible
to the drift check") and was resolved by typing it. An untyped body publishes an empty
schema into the OpenAPI contract, which is what FR-PLAT-48's drift check cannot see.

- [ ] **Step 1: add the two request models to `model-schema`**

```python
# packages/model-schema/src/model_schema/rating.py — beside RatingVersion
class RatingVersionCreate(BaseModel):
    """The body of `POST /api/v1/rating-versions` (03 §5.1, FR-RATE-22)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Slug
    dataset_version_id: UUID
    model_ref: ArtifactRef


class RatingVersionSubmit(BaseModel):
    """The body of `POST /api/v1/rating-versions/{id}/submit` (03 §5.1, FR-RATE-40)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    change_summary: str = Field(min_length=1)
```

Add both to the module's `__all__`. `Slug` and `ArtifactRef` are already imported in this
module — check, do not re-import.

- [ ] **Step 2: write the failing tests**

```python
# backend/tests/test_rating_versions.py
@pytest.mark.req("FR-RATE-22")
def test_a_rating_version_is_created_over_http(api_client, workspace_id, principal, grant) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}
    created = api_client.post(
        "/api/v1/rating-versions",
        headers=headers,
        json={
            "slug": "fremtpl2-demo",
            "dataset_version_id": str(uuid7()),
            "model_ref": {"type": "model", "slug": "fremtpl2-glm", "version": 1},
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["status"] == "draft"
```

Mirror the file's existing HTTP tests (`test_the_rating_version_routes_read_over_http`,
`:148-178`) for the fixture and header pattern rather than the sample above where they
differ — `api_client` (`backend/tests/conftest.py:56`), `DEV_PRINCIPAL_HEADER` from
`app.api.deps`, and the `grant("analyst")` bridge are the shapes that already work in this
file. Do not reinvent the module's fixtures.

Write the submit test the same way, against a version created by the `_draft` helper
(`:54-62`), asserting `200` and `"status": "review"`.

- [ ] **Step 3: run them and confirm the predicted failure, by cause**

Run: `uv run pytest backend/tests/test_rating_versions.py -k http -v`

Expected — **two different failures, and they must differ**:
- `POST /api/v1/rating-versions` returns **405 Method Not Allowed**, not 404. The path is
  already registered for `GET` (`models.py:1092`), so Starlette matches the route and
  rejects the method. **A 404 here is a plan defect**: it would mean the `GET` list route is
  not registered at all, which is a different fault and would make the rest of this task's
  premise wrong.
- `POST /api/v1/rating-versions/{id}/submit` returns **404**. No route matches that path at
  any method.

If both return the same status, stop and find out why before implementing.

- [ ] **Step 4: implement the router**

Follow `rating_algorithms.py`'s module shape. Both routes take
`Annotated[Caller, Depends(requires(Permission.RATING_WRITE))]` and
`Annotated[Caller, Depends(requires(Permission.RATING_SUBMIT))]` respectively, and use
`database.unit_of_work()` — the two service functions call `session.flush()` but not
`commit()`, so a plain `database.session()` would create a row that vanishes.

The service functions keep their own in-body `rbac.require_permission` call. That is
deliberate double-checking, not redundancy to remove: the demo seed calls them directly,
with no route dependency in front, and the in-body check is what protects that path.

- [ ] **Step 5: register the router** in `main.py`, beside `rating_algorithms`.

- [ ] **Step 6: run the tests to green, then the full gate**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
uv run python scripts/generate-contracts.py --check
```

`generate-contracts.py --check` **will fail** the first time — the two new `model-schema`
models change the OpenAPI output. Regenerate (`uv run python scripts/generate-contracts.py`)
and commit the regenerated `docs/contracts/` in the same commit; CI fails on drift
(FR-PLAT-48). Then the frontend half: `pnpm --dir frontend generate:api && pnpm --dir
frontend type-check`.

- [ ] **Step 7: add the spec citation and re-run the docs audit**

Add `(FR-RATE-22)` to `docs/specs/03-rating-engine.md:513`. Run
`python3 scripts/audit-docs.py`.

- [ ] **Step 8: commit**

```bash
git add backend/src/app/api/rating_versions.py backend/src/app/main.py \
  packages/model-schema/src/model_schema/rating.py backend/tests/test_rating_versions.py \
  docs/specs/03-rating-engine.md docs/contracts
git commit -m "feat(rating): wire the rating-version create and submit routes (FR-RATE-22)"
```

**Acceptance**
- Both routes answer over HTTP, gated on their existing permissions.
- A test creates a Rating Version and submits it **through the routes**, not the service
  functions — the gap this task closes is precisely that nothing did.
- An RBAC test: a principal without `RATING_WRITE` gets 403 from `POST /rating-versions`.
- `audit-docs.py` clean; the contract regenerated and committed.

**Must NOT touch.** `create_rating_version` and `submit_for_review`'s bodies. They are
correct and tested; this task gives them a caller.

---

## Task 1.2 — Real resolver content, `Bundle` persistence, and the `RATING_COMPILE` Job

**Ruling 2 and its related finding, which the rulings record is explicit are one
prerequisite and not two** (`...prework-rulings.md:339-345`).

**The defect, in three parts that land together.**

(a) `_Resolver.resolve()` (`rating_versions.py:241-271`) has two branches:
`rating_algorithm`, which resolves for real (`ResolvedArtifact(status="approved",
payload=algo.content)`), and `model`, which returns the placeholder
`ResolvedArtifact(status=model.status, payload={"status": model.status})` — no coefficients,
no booster bytes. Everything else falls through to one catch-all:

```python
raise PlatformError(
    "NOT_FOUND",
    "Pinned artifact cannot be resolved yet",
    404,
    f"{ref} has no backend table yet (Phase 2); a compile cannot embed it.",
)
```

That detail string is now false for three ref types. `RateTableRow` (`db/models.py:1951`),
`RateTableVersionRow` (`:1978`), `ReferenceTableRow`/`ReferenceTableVersionRow`/
`ReferenceRowRow` (`:900`/`:920`/`:947`) and `CustomObjectiveRow` (`:1620`) all exist.

(b) `compile_rating_version` (`:226-288`) computes the full `Bundle` and then persists
`{content_hash, bytes, compiled_at}` only. Nothing durable holds `graph` or
`resolved_payloads`, and nothing loads a bundle back — so Task 1.3 has nothing to hydrate.

(c) The route (`api/models.py:1139`) answers **200**, and its own docstring says so. `03`
§5.1:514 specifies **202**, and `wf-02:57` agrees. `JobKind.RATING_COMPILE` exists
(`model_schema/jobs.py:53`) and routes to `JobQueue.DEFAULT` (`platform/jobs.py:72`), but
**has no registered handler** — it is one of ten unregistered kinds, and submitting one
today fails with `JOB_HANDLER_NOT_REGISTERED` (`worker/tasks.py:123`).

**Files**
- Modify: `backend/src/app/platform/rating_versions.py`'s `_Resolver` — add `rate_table`,
  `reference_table` and `custom_objective` branches **before** the catch-all, and replace
  the `model` branch's placeholder with real content. Leave the catch-all in place: it is
  still correct for any ref type that genuinely has no table.
- Create: `backend/src/app/worker/rating_handlers.py`, matching
  `rate_table_handlers.py`'s shape exactly (see the verbatim quotation below).
- Modify: `backend/src/app/worker/entrypoint.py:41-50` — add
  `from app.worker.rating_handlers import register_rating_handlers` and the call, beside
  the three that are already there.
- Modify: `backend/src/app/api/models.py:1139-1161` — submit a Job and answer 202.
- Test: `backend/tests/test_rating_version_compile.py` (exists; `:94-97` currently asserts
  the 200 this task changes — that assertion moves, it is not deleted).

**No spec change.** `03` §5.1 already says 202 and Ruling 2 already ruled the code wrong.
Do not "fix" the spec to say 200.

**Interfaces**
- *Consumes:* Task 1.1's routes (to create the version under test);
  `compile_bundle(version: RatingVersion, resolver: ArtifactResolver) -> Bundle`
  (`compile.py:387`, `async def`); `BlobStore.put(session, content: bytes | Iterable[bytes],
  media_type: str) -> BlobRef` (`platform/blobs.py:130`).
- *Produces:* a persisted, retrievable `Bundle`. Task 1.3's `load_bundle` takes exactly
  what comes back out of the blob store here.

The house pattern for a Job handler, verbatim from
`backend/src/app/worker/rate_table_handlers.py:38-54` and `:57-67` — mirror it, do not
invent a second shape:

```python
    async def work() -> str:
        ...
        payload = diff.model_dump_json().encode()
        async with progress.database.unit_of_work() as session:
            ref = await progress.blob_store.put(session, payload, "application/json")
            return ref.sha256

    sha256 = progress.run_on_loop(work())
    progress.update(1.0, "done")
    return JobResult(kind="blob", ref=sha256)


def register_rate_table_handlers() -> None:
    for kind, handler in ((JobKind.RATE_TABLE_DIFF, _rate_table_diff),):
        if kind not in HANDLERS:
            register_handler(kind, handler)
```

A handler is **synchronous** and takes `(parameters: dict[str, Any], callback:
ProgressCallback) -> JobResult` (`worker/handlers.py:25`); it reaches async work through
`progress.run_on_loop(...)`. `register_handler` refuses a duplicate outright
(`handlers.py:37-38`), which is why registration is a function called from
`entrypoint.py` rather than an import-time side effect.

And the 202 pattern, from `api/rate_tables.py:304-364`:

```python
        async with database.unit_of_work() as session:
            job = await job_service.submit(
                session,
                JobKind.RATE_TABLE_DIFF,
                {**job_identity(caller), "slug": slug, ...},
                caller.principal,
                workspace_id=caller.workspace_id,
            )
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["Location"] = f"/api/v1/jobs/{job.id}"
        return job
```

Note that route is a *conditional* 200-or-202 (`response_model=None`, a union return type,
`responses={200: ..., 202: ...}`). The compile route is **unconditionally** 202, so it is
simpler: declare `status_code=status.HTTP_202_ACCEPTED` and return `Job`.

- [ ] **Step 1: write the failing resolver test**

```python
@pytest.mark.req("FR-RATE-25")
def test_a_version_pinning_a_rate_table_compiles(api_client, ...) -> None:
    """A Rating Version pinning a real W10 rate table resolves and compiles."""
```

Seed a rate table with the W10 fixtures — read `backend/tests/` for the existing rate-table
fixture rather than constructing rows by hand; W10 shipped them and reusing one is the only
way this test proves the resolver reaches *real* stored content.

- [ ] **Step 2: run it and confirm the predicted failure, by cause**

Run: `uv run pytest backend/tests/test_rating_version_compile.py -k rate_table -v`

Expected: HTTP **404**, `"code": "NOT_FOUND"`, and the response `detail` **containing the
literal string** `has no backend table yet (Phase 2)`. The detail is the discriminator: a
404 without it means the rate table itself was not found — the fixture is wrong, not the
resolver — and fixing the resolver would not make that test pass.

- [ ] **Step 3: add the three resolver branches**

Each mirrors the `rating_algorithm` branch: select the row scoped by `workspace_id`, slug
and version; raise `PlatformError("NOT_FOUND", ...)` when absent; return a
`ResolvedArtifact(status=..., payload=...)` carrying the real content. For `rate_table`,
the payload must carry the cells a scoring call will need — a `storage="rows"` version
holds them in `rate_table_cells`, a `storage="parquet"` version in a blob (`RateTableVersionRow`
docstring, `db/models.py:1978-1985`). Read `backend/src/app/platform/rate_tables.py` for the
function that already materialises cells and call it; do not write a second materialiser.

`status` matters: `compile_bundle` refuses any pin whose `status` is not approved-or-better
(`PIN_NOT_APPROVED`, FR-OVR-14). Return the row's real status, as the `model` branch already
does — never a hardcoded `"approved"`.

- [ ] **Step 4: replace the `model` branch's placeholder**

Return the model's real content — coefficients for a GLM, the booster blob reference for a
GBM — not `{"status": model.status}`. `ModelRow` is selected already; read what it stores
and carry the fields `predict_glm`/`predict_gbm` need. Task 1.4 is the consumer; if a field
it needs is missing here, that is this task's defect, not Task 1.4's.

- [ ] **Step 5: write the persistence round-trip test, then make it pass**

```python
@pytest.mark.req("FR-RATE-24")
def test_the_compiled_bundle_survives_persistence(...) -> None:
    """Compile, fetch the Bundle back from the blob store, and confirm nothing was dropped."""
    # ... compile via the route, poll the Job, read the blob by its ref
    restored = Bundle.model_validate_json(blob_bytes)
    assert restored.graph.nodes, "the persisted Bundle has an empty graph"
    assert restored.resolved_payloads, "the persisted Bundle has no resolved payloads"
    assert restored.content_hash == in_process_bundle.content_hash
```

The two `assert ... , "..."` messages are the point: a Bundle that persists its metadata and
silently drops its graph is exactly the failure this task exists to prevent, and a bare
`assert restored` would not catch it.

- [ ] **Step 6: create the handler module and register it.**
- [ ] **Step 7: change the route to 202**, and move the existing `assert response.status_code
      == 200` at `test_rating_version_compile.py:97` to `== 202` plus a Job-body assertion.
- [ ] **Step 8: full gate, both halves, then commit.** The route's response type changes, so
      `generate-contracts.py --check` will fail until regenerated.

**Acceptance**
- A Rating Version pinning a real W10 rate table compiles — it does not today.
- `POST /rating-versions/{id}/compile` answers 202 with a `Job` body and a `Location`
  header; polling the Job to completion yields a `JobResult(kind="blob", ...)`.
- The persisted `Bundle` round-trips with a non-empty `graph` and `resolved_payloads`, and
  a `content_hash` equal to what `compile_bundle()` produced in-process.
- The "before" failure was observed with its documented detail string, per Step 2.

**Must NOT touch.** `compile_bundle()` itself (`compile.py:387`). Ruling 3 already settled
its signature; this task changes what calls it and what happens to its result.

---

## Task 1.3 — `CompiledBundle`, `load_bundle`, and the JDM wire translation

**Ruling 4** settles the type: `CompiledBundle` is a distinct *loaded* runtime wrapper,
never itself serialised. FR-RATE-65 (`03:139`) states it as a requirement. Neither settles
the harder half — that **`to_jdm()` does not produce what the engine consumes**, and the
translation that closes the gap does not exist.

**The two parts.**
(a) `CompiledBundle` has zero code definitions: 57 hits repo-wide, every one in a `.md`.
(b) `to_jdm` (`compile.py:325`) returns a `JdmGraph` whose `nodes` is a
`dict[str, dict[str, Any]]` keyed by `step_id`, with `produces`/`consumes` lists standing in
for edges. The engine consumes a **list** of nodes plus an explicit **edges** list — see
*Verified facts* above, where the real shape is measured rather than described.
`docs/research/zen-evaluate-concurrency.md:147-153` found this while building a graph by
hand for the S2 spike and recorded that "that further translation does not exist yet". This
needs no ruling: the target shape is fixed externally by the engine's own wire format.

**Files**
- Create: `packages/pricing-core/src/pricing_core/rating/runtime.py`.
- Modify: `docs/specs/02-modelling.md` §5.2 — append the loaded-booster seam's signature in
  the same commit that adds it (Ruling 8's standing obligation, not optional).
- Modify: `compile.py`'s `to_jdm` and `JdmGraph` docstrings, both of which currently claim
  unqualified to produce "the engine's graph shape". Correct them to say what `to_jdm`
  actually produces *relative to* the engine's input, so the next reader does not repeat
  this gap's own root cause by trusting a docstring over a live call.
- Test: `packages/pricing-core/tests/test_rating_runtime.py`.

**Interfaces**
- *Consumes:* `Bundle` (`compile.py:350`) as Task 1.2 persists it; `zen.ZenEngine`,
  `zen.ZenDecision`.
- *Produces*, and Task 1.4 depends on these exact names:
  - `def to_wire(graph: JdmGraph) -> dict[str, Any]` — the JDM `{"nodes": [...], "edges": [...]}`
  - `def load_bundle(bundle: Bundle) -> CompiledBundle` — **exactly this signature**, ruled
    and appended to `03` §5.2 by Ruling 7 (PR #368). It takes no resolver, no handler and no
    keyword arguments, and performs no I/O: everything it needs is inside the `Bundle`.
    Plain `def`, per `.claude/skills/spec-change`'s rule — it awaits nothing.
  - `CompiledBundle`, with at minimum `content_hash: str`, `decision: zen.ZenDecision`,
    `algorithm: RatingAlgorithm`, `boosters: Mapping[str, object]`

**Three obligations from Rulings 7, 8 and 10, all landing in this task.**

1. **Ruling 7 — a `model_call`'s payload travels *inside* the `Bundle`, never as a
   reference, and must survive a JSON round trip.** `Bundle` is persisted and cached as
   JSON and `resolved_payloads` is typed `dict[str, Any]` (`compile.py:361`), so raw booster
   bytes cannot sit there unencoded. This is what Task 1.2's `model` branch must produce and
   what `load_bundle` hydrates from — the two tasks meet exactly here.
2. **Ruling 8 — the loaded-booster seam does not exist: `predict_gbm` re-loads the booster
   on every call.** The seam's function names, the loaded type's name, and whether the loader
   lives in `pricing_core/modelling/gbm.py` beside `predict_gbm` or in `rating/runtime.py`
   beside `CompiledBundle` are **this task's design**, deliberately not pre-written by the
   ruling — naming a function before it is designed is how a spec acquires a signature
   nothing implements, which is the failure `CompiledBundle` itself was. **The PR that adds
   the loader appends its signature to `../specs/02-modelling.md` §5.2 in the same commit.**
   *Acceptance, stated as the violation that must become impossible:* a test asserting that
   scoring N quotes against one `CompiledBundle` performs exactly **one** booster load.
3. **Ruling 10 — two properties Slice 1 owes W14, so the deployment-switch mechanism still
   has a choice left.** (i) `CompiledBundle` exposes the `content_hash` of the `Bundle` it
   was loaded from — every candidate switch mechanism compares a held hash against a current
   one, and a `CompiledBundle` that has forgotten its provenance makes FR-RATE-51's "either
   the old or the new bundle, never a mix" unverifiable at runtime. (ii) `load_bundle` is
   **pure with respect to the cache**: it consults no cache, registers itself in no global,
   and starts no background task. `.importlinter` forbids `pricing_core` from importing
   `redis` at all, so any cache tier lives above it in `backend/`. The warm-worker refresh
   trigger itself is **W14's**, not this slice's.

`import zen` is permitted here: `.importlinter`'s `core-has-no-infrastructure` contract
forbids only web, database, queue and cloud clients, and `compile.py:24` already imports it.

- [ ] **Step 1: write the failing round-trip test**

```python
@pytest.mark.req("FR-RATE-65")
async def test_a_real_bundle_loads_and_evaluates() -> None:
    """The Bundle today's compile path produces evaluates through a real engine handle."""
    bundle = await compile_bundle(version, resolver)      # the real path, not a hand-built fixture
    compiled = load_bundle(bundle)
    out = await compiled.decision.async_evaluate({"driver_age": 34})
    assert out["result"], "the engine returned no outputs"
```

**The `Bundle` going in must come from the real `compile_bundle()` path.** A hand-edited
fixture standing in for one would leave the translation gap untested, which is half of what
this task exists to close.

- [ ] **Step 2: run it and confirm the predicted failure, by cause**

Run: `uv run pytest packages/pricing-core/tests/test_rating_runtime.py -v`

Expected on the first run: `ImportError`/`AttributeError` — `load_bundle` does not exist.
After a naive first implementation that hands `JdmGraph.model_dump()` straight to
`create_decision`, expect a **`RuntimeError` from the binding naming a malformed graph**, not
a wrong number. A wrong *number* would mean the translation ran and computed something —
a different fault, and one that would make this task's premise wrong.

- [ ] **Step 3: implement `to_wire`**

The mapping, from the measured format:

```python
def to_wire(graph: JdmGraph) -> dict[str, Any]:
    """Translate pricing-core's JdmGraph into the JDM shape zen's binding consumes.

    `JdmGraph` is pricing-core's own intermediate form: a dict keyed by step_id with
    produces/consumes lists. The engine wants a node *list* plus an explicit edge list.
    Verified against a live `ZenEngine().create_decision(...)` call, never a docstring.
    """
```

Rules the translation must obey, each verified live:
1. Every node is `{"id", "type", "name", "position", "content"}`. `position` is required by
   the parser even though nothing reads it; `{"x": 0, "y": 0}` is fine.
2. The graph needs exactly one `inputNode` and one `outputNode`, derived from
   `graph.input_contract` and `graph.outputs`. Neither needs a `content` key.
3. **Every `expressionNode` sets `"passThrough": True`.** Without it the engine returns only
   the terminal key and the premium ladder is empty. This is the single most consequential
   line in the translation — see *Verified facts* item 3.
4. Edges are explicit: `{"id", "type": "edge", "sourceId", "targetId"}`, derived from the
   `produces`/`consumes` relation `JdmGraph` already carries.
5. A `table`/`lookup` step becomes a `decisionTableNode`, whose `content` is
   `{"hitPolicy", "rules", "inputs", "outputs", "passThrough", "inputField", "outputPath",
   "executionMode"}`; `inputs`/`outputs` are lists of `{"id", "name", "field"}` and each rule
   keys on those ids.
6. A `model_call` step becomes `{"type": "customNode"}`. The handler is supplied when the
   engine is constructed, not when the graph is translated — `load_bundle` takes no handler
   argument (Ruling 7), so whichever object owns the `ZenEngine` owns the handler.

- [ ] **Step 4: implement `CompiledBundle` and `load_bundle`**

```python
@dataclass(frozen=True)
class CompiledBundle:
    """A loaded, executable bundle — FR-RATE-65. Never serialised (Ruling 4).

    `Bundle` is the record: hashable, distributable, cacheable. This is what a warm worker
    holds after loading one, and it owns an engine handle and live booster objects that
    have no serialised form at all.
    """

    content_hash: str
    decision: Any          # zen.ZenDecision — the binding exports no importable type
    algorithm: RatingAlgorithm
    boosters: Mapping[str, object]
```

A `dataclass`, deliberately not a `BaseModel`: making it a Pydantic model would give it a
`model_dump_json()` that appears to work and silently drops the engine handle — the
boundary confusion Ruling 4's option (c) was rejected for.

- [ ] **Step 5: write the negative test that the boundary is real**

```python
@pytest.mark.req("FR-RATE-65")
def test_a_compiled_bundle_cannot_be_serialised(compiled: CompiledBundle) -> None:
    """FR-RATE-65: never itself serialised. Assert the boundary rather than assume it."""
    with pytest.raises(TypeError):
        json.dumps(dataclasses.asdict(compiled))
    assert not isinstance(compiled, BaseModel)
```

**This test proves part (a) only.** It would still pass with part (b) silently broken. Step 1's
round-trip is the only criterion here that proves the translation; do not treat either as
covering both.

- [ ] **Step 6: measure NFR-RATE-4** — compile a real large motor structure once 1.1 and 1.2
      make one compilable, and record the wall time against the **< 60 s** budget and the
      resulting `Bundle` size against **< 500 MB** (`03:780`).

- [ ] **Step 7: correct the two docstrings, run the full gate, commit.**

**Acceptance**
- `load_bundle` on a `Bundle` from the real compile path yields a `CompiledBundle` whose
  handle evaluates the graph to a known expected result.
- `CompiledBundle` is provably not serialisable, and is not a `BaseModel`.
- NFR-RATE-4 measured and written down, both halves.
- `to_jdm`/`JdmGraph` docstrings no longer claim to produce the engine's shape.

**Must NOT touch.** `Bundle` itself. W9's DP1 settled what it is; this task builds the
loaded type on top of it.

---

## Task 1.4 — `score_one` on `async_evaluate()`

**Ruling 5**, not open: the real-time path is built on `async_evaluate()`, never `evaluate()`
plus a thread-pool offload. Measured twice on this machine
(`docs/research/zen-evaluate-concurrency.md`): sync `evaluate()` blocks the event loop
completely; thread-offloaded `evaluate()` is *worse than sequential* (0.90–0.93x);
`async_evaluate()` is non-blocking and gives 2.10–2.25x on 4 cores. `03:599` already declares
`async def score_one`.

**Files**
- Create: `packages/model-schema/src/model_schema/scoring.py` — `QuoteContext`,
  `LadderRung`, `ScoringResult`, `Trace`, `TraceStep`.
- Create: `packages/pricing-core/src/pricing_core/rating/score.py`.
- Modify: `backend/src/app/errors.py` — add `MODEL_CALL_FAILED`, `INPUT_CONTRACT_VIOLATION`
  and `REFERENCE_LOOKUP_MISS` to `RATING_ERROR_CODES` (`:275-307`).
- Modify: `packages/pricing-core/src/pricing_core/modelling/gbm.py:1185` — `predict_gbm`
  gains a thread control (F-W11-1-2).
- Modify: `backend/src/app/main.py:70` — call `assert_integer_minor_round_trip()` in
  `lifespan` (F-W11-1-3).
- Test: `packages/pricing-core/tests/test_rating_score.py`, and a backend test for the
  startup check.

**Build the model-schema types from the contract, not from the §4.4 example.**
`docs/contracts/schemas/scoring.schema.json` already defines all four shapes, and
`CLAUDE.md` §2 forbids hand-writing a shape that exists. Two traps in the §4.4 example that
the contract does not have:
- The example's numeric literals are written `24_150`, which is **not valid JSON**. It is
  illustrative, not a fixture. Copying it into a test file produces a parse error whose
  cause is the plan, not the code.
- The example's ladder shows nine rungs and omits `instalment_loading`; the contract's
  `LadderRung.rung` enum has ten and includes it (FR-RATE-64 postdates the example). **The
  contract's enum is the authority.**

**Interfaces**
- *Consumes:* `load_bundle`/`CompiledBundle`/`to_wire` (Task 1.3);
  `pricing_core.money.apply_factor` and `reconcile_ladder`;
  `pricing_core.modelling.gbm.predict_gbm`; `pricing_core.modelling.predict.predict_glm`.
- *Produces*, and Slice 2 and Slice 3 both depend on this exact shape:
  - `async def score_one(bundle: CompiledBundle, ctx: QuoteContext, *, trace: bool = False) -> ScoringResult`
  - a per-step evaluator `score_batch` can call directly (FR-RATE-37 — Slice 3 proves
    byte-identity against this, so it must be reachable without going through `score_one`)

- [ ] **Step 1: generate the model-schema types from the contract and check both directions**

Write the five Pydantic models against `scoring.schema.json`'s `$defs`, then regenerate and
compare. `backend/tests/test_contracts.py` is where a generated-vs-hand-authored comparison
belongs; read `.claude/skills/contract-guard` before adding one — it records four defects
that were in the guards rather than in the schemas, and why `required` is compared in one
direction only.

**`purpose` is blocked by F-W11-1-1.** The spec says five values, the contract says four.
Do not pick one. Build every other field, leave `purpose` until it is ruled, and do not
write the FR-RATE-63 guard against a guess.

- [ ] **Step 2: write the golden test, and run it red**

```python
@pytest.mark.req("FR-RATE-34")
async def test_a_known_quote_prices_to_a_known_premium(compiled: CompiledBundle) -> None:
    result = await score_one(compiled, ctx)
    assert result.outcome == "quoted"
    assert result.outputs["payable_premium_minor"] == 36_120
    assert [r.rung for r in result.premium_ladder][-1] == "payable_premium"
```

Expected first failure: `ImportError` — `pricing_core.rating.score` does not exist. Not a
wrong number.

- [ ] **Step 3: implement the step evaluator and the ladder**

Every step type: `table`/`lookup` (decision-table node), `expression`, `model_call`
(custom node, below), `constraint`, `output`. The ladder is built with
`apply_factor(amount_minor, factor, mode)` per rung — `mode` has no default and FR-RATE-12
requires it be declared per step, so read it from the step's `RoundSpec`
(`model_schema/rating.py:216`) rather than defaulting it.

- [ ] **Step 4: implement `model_call` as a custom node**

`zen.ZenEngine({"customHandler": fn})` — **the key is `customHandler`**, verified live. The
constructor accepts any other key silently and fails only at evaluate time with
`{"type":"NodeError","source":"Custom node handler not provided"}`. Write a test that
asserts the handler was *invoked*, never that the constructor accepted the option.

The handler receives a `PyNodeRequest` and returns `{"output": {...}}`. Inside it, dispatch
to `predict_gbm` or `predict_glm` on the booster hydrated by Task 1.3, with `nthread=1`.

- [ ] **Step 5: give `predict_gbm` a thread control (F-W11-1-2)**

It has none today, and neither does `predict_glm`. Add a keyword-only
`nthread: int | None = None` to `predict_gbm` and apply it to the booster it constructs —
**not** a process-wide environment variable, which would silently change the fit path's
behaviour too. Then measure: p99 over ≥ 1000 calls, against NFR-RATE-14's amended figure of
**p99 1.626 ms** on the verification machine (the row's 2026-08-27 W8 amendment; the
original S2 figure of 1.09 ms is superseded and citing it would be citing a struck number).

- [ ] **Step 6: the typed per-quote errors (FR-RATE-38)**

Five categories, four dispositions:
- contract violation → `INPUT_CONTRACT_VIOLATION`
- reference miss → `REFERENCE_LOOKUP_MISS`
- table miss → `RATE_TABLE_MISS` (already registered, `errors.py:290`)
- model failure → `MODEL_CALL_FAILED`
- constraint decline → **not an error.** FR-RATE-39: `outcome: "declined"` with reason
  codes, a *successful* response, never an HTTP error.

**`MODEL_CALL_FAILED` is ruled and already in the spec** — Ruling 11 (PR #368) confirmed it
and appended it to §5.1's owned-code block, refusing the alternative of reusing
`BUNDLE_COMPILE_FAILED` because that names a compile-time failure and would blur the audit
trail between a bundle that would not build and a booster that would not answer. Do not
re-add it to the spec; it is there.

**Two corrections this plan owes to Ruling 11, both of which change what Step 6 does.**

*First: it is four codes, not three.* `RATING_ERROR_CODES` (`errors.py:275-307`) is missing
`MODEL_CALL_FAILED`, `INPUT_CONTRACT_VIOLATION`, `REFERENCE_LOOKUP_MISS` **and
`LADDER_RECONCILIATION_FAILED`** — the last is already listed as owned in §5.1 and is named
by NFR-RATE-8's reconciliation work, and an earlier draft of this plan missed it. All four
must reach `RATING_ERROR_CODES` before anything raises them: `PlatformError.__init__`
(`errors.py:344-348`) raises `ValueError("unknown error code ...")` for any code outside
`_KNOWN_CODES`, so raising one before registering it fails at construction rather than at
the client.

*Second, and more important: `score_one` does not raise `PlatformError` at all.* It lives in
`pricing-core`, which `.importlinter`'s `core-has-no-infrastructure` contract forbids from
importing `app`. The established convention inside `pricing-core` is a **code-named
`ValueError`** — `compile.py`'s `_raise_named` produces `ValueError(f"{code}: {message}")`,
and `compile_rating_version` (`rating_versions.py:275-282`) already parses that shape back
into a `PlatformError` at the boundary. `score_one`'s refusals follow `_raise_named`; the
mapping to `PlatformError` happens at the backend boundary in **Slice 2**. An earlier draft
of this step said "add all three to `RATING_ERROR_CODES`" as though `score_one` raised them
directly, which would have sent an executor into a `lint-imports` failure. Registering the
four codes is still this task's work — Slice 2's boundary mapping needs them to exist — but
it is a backend change beside a `pricing-core` change, not the same change.

- [ ] **Step 7: the decline representation**

**Ruled — Ruling 9 (PR #368), and FR-RATE-39 carries a dated amendment saying so.**
Collect-all: the full DAG always evaluates, `outcome` flips to `declined` if any constraint
step fires, `decline_reasons` collects **every** firing step's code, and the ladder stays
fully populated ("what it would have cost"). This matches `scoring.schema.json`'s
`decline_reasons` being an array and `premium_ladder` being required unconditionally. The
amendment appends no new `FR-` because it adds no obligation FR-RATE-39 did not already
carry — it makes precise which of two readings of "reason codes" was meant.

**Acceptance, stated as the ruling states it — the test needs *two* declines, not one.** A
`QuoteContext` firing two constraint declines returns `outcome: "declined"`,
`len(decline_reasons) == 2`, and a `premium_ladder` that reconciles to
`payable_premium_minor` under NFR-RATE-8's check. A single-decline test passes under
short-circuit and collect-all alike and would prove nothing.

- [ ] **Step 8: the trace (FR-RATE-41)**

Use the engine's own: `decision.async_evaluate(ctx, {"trace": True})` returns a `trace` dict
keyed by node id, each `{id, input, name, order, output, performance, traceData}`. Map it to
the contract's `Trace`. `performance` is a **string** (`'4.2µs'`); `Trace.steps[].elapsed_us`
is `{"type": "integer", "minimum": 0}` — parse it, do not pass it through.

`trace=False` must return `trace: None` and, per NFR-RATE-2 and R3, an **identical** premium.
Test that explicitly: score the same context twice, traced and untraced, and compare the
whole `ScoringResult` with `trace` excluded.

- [ ] **Step 9: the FR-RATE-63 refusal guard, on broken input** *(the `cancellation` limb is
      blocked by F-W11-1-1)*

A `QuoteContext` with `purpose: "mid_term_adjustment"` against a Rating Version that mounts
no MTA sub-graph must refuse — never `outcome: "quoted"`. Write the test, confirm it fails
against a first implementation that ignores `purpose`, then make it pass. The requirement's
own words: pricing it as new business "is the failure this requirement exists to prevent,
and it is silent".

- [ ] **Step 10: the FR-RATE-64 refusal guard (F-W11-1-4)**

The second half of FR-RATE-64: a Quote Context asking for a payment schedule, an APR figure
or a credit-agreement term is **refused**, not answered approximately. Its own broken-input
test, alongside the `instalment_loading` rung's reconciliation test.

- [ ] **Step 11: NFR-RATE-3, proven on broken input**

Patch or block every DB and network call for the duration of a `score_one` call and assert
no exception. Then insert a deliberate DB call and confirm the *same* test fails. A mock
that catches nothing passes silently, and that is the failure mode this step exists to
close.

- [ ] **Step 12: NFR-RATE-7 and NFR-RATE-8**

Determinism: the same `content_hash` + `QuoteContext`, scored twice — once in-process, once
in a subprocess — byte-identical. Reconciliation: `reconcile_ladder` over a **battery of
generated contexts**, not one example; `03:784` requires the ladder reconcile in 100 % of
scored quotes.

- [ ] **Step 13: the concurrency smoke test**

`asyncio.gather` over N concurrent `score_one` calls against **one shared**
`CompiledBundle`. The spike Ruling 5 rests on used a bare `asyncio.run` and a fresh handle,
not a long-lived handle serving concurrent calls the way a worker process will. This is the
first test of that shape.

- [ ] **Step 14: the Ruling 5 follow-up, resolved here**

Ruling 5 names a follow-up for "whichever slice builds `model_call`'s ADR-0004 custom-node
integration": repeat `zen-evaluate-concurrency.md`'s Q2 and Q3 — event-loop blocking and
throughput — on a graph that actually invokes a booster mid-evaluation. Step 4 above *is*
that integration, so the condition is met and this is a criterion, not a conditional.

- [ ] **Step 15: wire the FR-RATE-56 startup self-check (F-W11-1-3)**

Call `assert_integer_minor_round_trip()` in `main.py`'s `lifespan`, and add a test that a
failing check prevents startup. Two lines and one test; the requirement has said "failing it
prevents the service starting" since W9 and nothing has enforced it.

- [ ] **Step 16: full gate, both halves, then commit.**

**Acceptance** — every item above, plus: `NFR-RATE-1` measured *component-level only*.
`score_one`'s in-process latency is not a substitute for the sustained-load, ASGI-embedded
measurement `NFR-RATE-1` actually names (`03:777` — p99 < 50 ms at **200 rps per replica**).
That is Slice 2's Task 2.1, and `zen-evaluate-concurrency.md` is explicit that no such
measurement exists yet.

**Must NOT touch.** `score_batch`'s signature — it stays `def` per Ruling 5; batch has no
shared-event-loop concern to protect.

---

## Task 1.5 — The bare-metal latency harness

**Unblocked — Ruling 6 (PR #368) rules DP3.** `scripts/bench-rating.py` is stdlib-only,
following `bench-model.py`'s shape; the sustained-load driver that Slice 2's Task 2.1 needs
is `asyncio` + `httpx` in the same `scripts/` convention. Neither is a CI gate; each
produces a dated `docs/research/` note. The frozen map tags this task `[depends on DP3]`;
that tag is now discharged, and PR #368's own findings section records the tag as
over-broad in the first place.

**Discharges** `docs/roadmap.md:392`'s risk mitigation — "Build the latency harness in W11
alongside the evaluator, not after" — at the component level. The full-HTTP-path
measurement, including the separately-named sustained-200 rps test
(`docs/roadmap.md:146`), is **Slice 2's Task 2.1**.

**Files**
- Create: `scripts/bench-rating.py`, following `scripts/bench-model.py` and
  `scripts/bench-data.py`. Their shared rule, verbatim from `bench-model.py:6-11`:

> Not a CI gate. A timing assertion on a shared runner fails for reasons that have
> nothing to do with the code, and a check that fails randomly teaches everyone to
> re-run it. This produces numbers for a workstream closure record instead, where a
> human reads them once against the budget.

- Create: a dated note under `docs/research/`, matching
  `zen-evaluate-concurrency.md`'s precedent.

**Acceptance**
- Measures `score_one` directly — no HTTP, no FastAPI — against a ~200-step motor structure
  with one `exact` GBM call, reporting p99 against NFR-RATE-1's **< 50 ms**; and without a
  GBM call, against **< 15 ms** (`03:777`).
- Measures trace overhead (NFR-RATE-2): the same calls with `trace=True` and `trace=False`,
  reporting the delta against the **≤ 20 %** bound (`03:778`).
- **Reports the distribution, not only the p99 against the bound.** A single number
  comfortably inside a budget and a number sitting on it are different findings, and only
  the distribution distinguishes them.
- The result is a dated note in `docs/research/`, not terminal output that scrolls away.

---

## Self-review

**1. Spec coverage.** Every requirement in the coverage table maps to a numbered task with
an exit criterion that proves rather than asserts it. Requirements excluded are listed
individually with their owning slice or workstream, so the exclusion is visible rather than
silent. FR-RATE-65 was added after checking the map's own list against `03` §3.4 — it was
missing (C5).

**2. Placeholder scan.** No bare TBD. **One** thing is genuinely unwritten and it says
exactly what blocks it: `purpose` handling in Task 1.4 Step 1 (F-W11-1-1). That is the
honest state of a blocked decision, not a placeholder — and it is why Task 1.4 cannot be
declared complete before F-W11-1-1 is ruled. Two other items were open when this plan's
evidence sweep ran and are not open now: Task 1.5's DP3 dependency and Task 1.4's decline
representation, both ruled by PR #368 while this was being written. One design choice is
deliberately left to the executor rather than pre-written — the loaded-booster seam's
naming, per Ruling 8's own reasoning that naming a function before it is designed is how a
spec acquires a signature nothing implements.

**3. Type consistency.** `CompiledBundle`, `load_bundle` and `to_wire` are named once in
Task 1.3's *Produces* block and used under those names in Task 1.4. `score_one`'s signature
is copied from `03:599-600`, not retyped. `apply_factor`'s third parameter is `mode`
throughout, matching the shipped code rather than §5.2's `rounding` (F-W11-1-5).

**4. Literals verified against shipped source, per `README.md`'s three unenforced
conventions.** Every file path, line number, function signature, enum member, error-code
string, permission name and JobKind in this plan was read out of the tree at `7b8473a` or
returned by a live call. The five engine facts were obtained by running code, not by reading
a docstring — which is what caught `passThrough` and the `customHandler` key, neither of
which appears in any document in this repository. Where a literal could not be verified,
this plan names the authority instead of supplying a sample: the rate-table fixture in Task
1.2 Step 1, the model content in Step 4, and the contract comparison in Task 1.4 Step 1 all
say "read the neighbouring code" rather than inventing a shape.

**5. Predicted failures are stated by cause.** Three tasks predict a first-run failure and
each names its discriminator: the 405-vs-404 split in Task 1.1 Step 3, the
`has no backend table yet (Phase 2)` detail string in Task 1.2 Step 2, and the
malformed-graph `RuntimeError` versus a wrong number in Task 1.3 Step 2. In each case the
plan says what a *differently*-shaped failure would mean, because a matching status with a
differing reason is a plan defect.

**6. What this plan does not decide.** Three things, each named with its owner. F-W11-1-1
and F-W11-1-5 are spec-vs-code conflicts and so the decision-maker's; whether Tasks 1.1–1.5
are five slices or one slice of five PRs is the lead's replan call, raised separately. A
planner supplies options and a recommendation and rules none of them
(`delivery-process.md` §3).

**7. Written against `7b8473a`, revised once before freeze.** The evidence sweep, every
line number and the five live engine measurements are at `7b8473a`. PR #368 landed six
rulings between the sweep and the commit, and this plan was revised rather than filed
stale — the revision is named at each point it applies rather than folded in silently, so a
reader can see which parts rest on evidence and which on a ruling. **F-W11-1-1 survives
that revision**: PR #368's own "findings reported, not ruled" section names two findings and
neither is the `purpose` enum, so it remains open and this plan is still its only record.
