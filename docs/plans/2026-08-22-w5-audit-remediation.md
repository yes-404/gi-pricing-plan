# W5 Audit Remediation — Sequenced Slice Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement each slice task-by-task. This document is a **sequencing plan**, not a task plan — it names six slices, their scope, files, exit criteria and blocking decisions. Each slice gets its own detailed TDD plan in `.planning/YYYY-MM-DD-<slice>.md` when it starts, following the house pattern set by `2026-08-21-regularisation-and-cv.md`.

**Goal:** Clear every finding from the 2026-08-22 W5 closure audit so that W5 can be closed against `CLAUDE.md` §13 with an honest closure record.

**Architecture:** Six slices in dependency order. Two are blocked on maintainer decisions and are sequenced accordingly; one (the contract half) is large enough that it is the only slice whose first task is a deliberately-failing guard rather than a feature. The last slice writes the closure record and must run last, because it states the final position of every other slice.

**Tech Stack:** Python 3.12, Pydantic v2 (`model-schema`), Polars, glum, XGBoost/LightGBM/interpret-core, SQLAlchemy 2.x async + Alembic, PostgreSQL 16, pytest + `@pytest.mark.req`, Vue 3 (untouched by every slice here).

**Spec:** `docs/specs/02-modelling.md` (the module), `docs/specs/06-governance.md` (slices 1 and 6), `docs/specs/07-platform.md` (slice 2's error-code registration), `docs/roadmap.md` §6 and the W5 slice records. The audit this plan answers: https://claude.ai/code/artifact/45b1666c-1d29-4654-b916-e16ae5659cb3

---

## Global Constraints

Every slice's requirements implicitly include these. Values are copied verbatim from `CLAUDE.md` and the specs.

- **Requirement IDs are permanent** (§5). Never renumber. Append, or mark superseded. "Remove a requirement" means *mark superseded*.
- **Spec and code disagreeing is a finding, not a cleanup** (§0). Where the code is right, amend the spec with a dated note saying which side was wrong and why. Where the *spec* is right, the spec gains the precise obligation — an appended requirement, an owner, a verdict — rather than being edited down to what was built.
- **One commit spans spec + code + tests + skill update.** Splitting them means the audit reports a consistency the repository does not have.
- **The gate is both halves**, run locally, each command's own exit code read:
  ```bash
  uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
  python3 scripts/audit-docs.py
  uv run python scripts/req-coverage.py
  uv run python scripts/generate-contracts.py --check
  pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
  pnpm --dir frontend lint && pnpm --dir frontend type-check
  pnpm --dir frontend test && pnpm --dir frontend build
  ```
- **A negative test for every invariant introduced**, each carrying `@pytest.mark.req("<ID>")`. For a governed system the suite must prove the wrong thing *cannot* happen.
- **Enforcement is proven, not assumed** (§13 rule 4). Any new check must be shown to fail on deliberately broken input before it is trusted.
- **Money is integer minor units or `Decimal`, never `float`.** `DecimalStr` is the wire type for exact decimals.
- **Nobody hand-writes a shape that already exists in `model-schema`.** `docs/contracts/schemas/generated/` and `openapi/generated.json` are generated — never hand-edit.
- **Alembic head is `2b2e2a481fb1`** (`2b2e2a481fb1_metric_certify_job_kind.py`). Any new revision chains from the then-current head, re-checked with `uv run alembic heads` at slice start.
- **`audit-docs.py` check 10 trap:** a bolded anchor phrase such as `**§5.1**` inside an `FR-` table row breaks the check. Write "§5.1 ownership block" or leave the reference unbolded.
- **Do not build ahead of the phase.** `02` §5.3's model spec builder, diagnostics, comparison and peril-structure views are **W6b's**. No slice here adds a frontend view.
- **Work in a worktree**, branch from `main`, Conventional Commits, squash-merge. Plans live in `.planning/`; write in the worktree and copy back before exiting.

---

## Sequencing

| # | Slice | Depends on | Blocking decision | Size |
|---|---|---|---|---|
| 1 | Governance correctness | — | none | small |
| 2 | FR-MODEL-23 + OQ-PLAT-7 | — | **OQ-PLAT-7 (a)/(b)/(c)** | small |
| 3 | NFR evidence | — | NFR-MODEL-1/2/10 fixture; NFR-MODEL-3 fix-or-restate | medium |
| 4 | Bühlmann–Straub | — | **build vs supersede FR-MODEL-80** | medium |
| 5 | The contract half, the interfaces, and four strays | — | none | **large** |
| 6 | Bookkeeping + closure record | 1–5 | FR-MODEL-6 acceptance | medium |

Slices 1–5 are mutually independent and may run in parallel in separate worktrees. Slice 6 must run last. **Take the three decisions before starting**, so slices 2, 3 and 4 are not blocked mid-flight: OQ-PLAT-7's option, whether FR-MODEL-80 is built or superseded, and whether a 5M-row fixture is built.

---

## Slice 1 — Governance correctness

Three defects that share one path: an artifact's evidence pointer, the reference an approval pins, and the floor a policy may not drop below. Small individually; together they are one reviewer's gate.

**Requirements:** `02` R2 (artifact immutability), `06` FR-GOV-36, `06` FR-GOV-19/37.

### 1a — `models.diagnostics_id` into the immutability trigger

**The defect.** `models_fit_immutable()` refuses changes to `fit_result`, `spec`, `spec_hash` and `dataset_version_id` once `fit_result IS NOT NULL`. `diagnostics_id` is not in that list, so a fitted — and possibly approved — Model's diagnostics pointer can be repointed. The evidence an approval rested on can be swapped without the trigger objecting. Artifact immutability is on `docs/roadmap.md` §5's retrofit-impossible list.

**Files**
- Create: `backend/migrations/versions/<rev>_diagnostics_id_immutable.py` — `CREATE OR REPLACE FUNCTION models_fit_immutable()` adding the column to the existing `IF` chain. The function is replaced wholesale, not altered; copy the existing body from `b2c3d4e5f6a7_model_fit_immutable.py:32-50` and add one `OR NEW.diagnostics_id IS DISTINCT FROM OLD.diagnostics_id`.
- Modify: `backend/tests/test_model_lifecycle.py` — add the negative test beside the existing trigger test at `:162`.

**The one design question, and its answer.** Diagnostics are written *after* the fit, by the same job — so a naive guard would refuse the legitimate first write. Check the real ordering in `backend/src/app/worker/model_handlers.py`'s `record_fit` before writing the migration. If `fit_result` and `diagnostics_id` land in one `UPDATE`, the guard is safe as written. If `diagnostics_id` lands in a *later* statement, the condition must be `OLD.diagnostics_id IS NOT NULL AND NEW.diagnostics_id IS DISTINCT FROM OLD.diagnostics_id` — freezing it once set, rather than once fitted. **Do not guess: read the handler, then choose, and say in the migration docstring which case held.**

**Exit criteria**
- A negative test proving a repoint on a fitted model raises, marked `@pytest.mark.req("FR-MODEL-65")` or whichever requirement `02` R2 carries — check `docs/specs/02-modelling.md` §4.8 for the R2 requirement id rather than inventing one.
- A positive control proving the legitimate first write still succeeds.
- `uv run alembic upgrade head` then `downgrade -1` both clean.

**Must NOT touch.** The delete guard (`models_fitted_undeletable`), any other artifact table's triggers, or `a1b2c3d4e5f6`'s six artifact tables.

### 1b — FR-GOV-36, resolving the pinned artifact

**The defect.** `POST /approval-requests` validates only the grammar of `{type}:{slug}@{version}`. A request can be pinned to a version that was never created; the owning module cannot move an artifact that does not exist, so the request decides without effect. `approvals.submit()` (`backend/src/app/platform/approvals.py:119-176`) checks `policy.entry_for(...)` at `:139` and constructs the row at `:143` without ever resolving the reference. **No `FR-GOV-36` marker exists anywhere in the suite** — this slice adds the first.

**The requirement's own framing, and why it is only half right.** FR-GOV-36 (`docs/specs/06-governance.md:161`) says resolution "needs a lookup per artifact type and DEP-1 forbids `GOV` importing `DATA`–`MON`, so this is a resolver registered *with* governance by each owning module, or a check in each module's own submit path."

**Prefer the third option the requirement does not name, because the codebase already chose it.** `backend/src/app/api/approvals.py:311-339`'s `_carry_to_the_artifact` already solves exactly this problem for the *decide* direction, by fanning out per artifact type **in the route** — which sits above both governance and the owning modules, so DEP-1 is satisfied without a registry at all. Its docstring makes the argument:

> One call per artifact type rather than a branch here: each module's function returns `None` for a request that is not its own, so adding a type is a change in that module and not in this route.

A resolver registry would be a *second* mechanism for the same seam. Follow the existing one unless there is a reason not to, and record the choice in the requirement's amendment note. (A registry precedent does exist if wanted — `backend/src/app/worker/handlers.py:27-44`, whose `register_handler` refuses to replace an existing registration because "two handlers for one kind means the behaviour depends on import order". But it is registered from `worker/entrypoint.py:44-48`, and **the API process never calls it** — so choosing the registry means also solving where registration happens on the API path, most plausibly beside `health.register_probe` in `main.py:68-69`.)

**Note for the amendment: DEP-1 is not machine-enforced.** `.importlinter` holds three contracts — ADR-0001's infrastructure ban, ADR-0002's pydantic-only rule, and DEP-3's three-layer stack. **None constrains one `app.platform` module against another**, so an import from governance into modelling passes `lint-imports` today and violates DEP-1 only on the page. Worth flagging in the slice record; adding such a contract is a separate proposal, not this slice's.

**The lookups that already exist**, so no module needs new query code:

| Type | Existing lookup | Ready? |
|---|---|---|
| `custom_objective` | `objectives.resolve_ref(session, *, workspace_id, ref)` `:327-353` | **The template.** Ref-shaped, queries `(workspace_id, slug, version)`, raises `NOT_FOUND` |
| `model` | `modelling.load_model(..., slug, version=None)` `:839-859` | Yes — already `(slug, version)` keyed, already raises `NOT_FOUND` at `:853` |
| `custom_metric` | `metrics.resolve_ref(...)` `:296-321` | Shape is right but raises **`METRIC_REF_UNRESOLVED`**, deliberately per its docstring at `:297-301`. FR-GOV-36 says `NOT_FOUND` — **reconcile explicitly, do not paper over it** |
| `peril_structure` | `perils.load_structure(..., structure_id)` `:356-362` | By UUID; `(workspace_id, slug, version)` is unique at `db/models.py:1508`, so a slug/version query is one line |
| `validation_rule` | `validation_rules.load_rule(..., rule_id)` `:203-211` | By UUID; unique at `db/models.py:1067` |
| `dataset_version` | `datasets.load_version(..., version_id)` `:601-621` | By UUID; needs `DatasetRow.slug` joined to `DatasetVersionRow.version` (unique at `db/models.py:768`) |
| `rating_version` | **none — `03`/RATE is unbuilt** | Has a `DEFAULT_POLICY` entry (`approvals.py:245-250`) and no module. The design **must tolerate an unresolvable type** |

**`NOT_FOUND` needs no registration.** It is in `_GENERIC_ERROR_CODES` (`backend/src/app/errors.py:244-247`), folded into `_KNOWN_CODES`, and is the 404 default at `:348`. It belongs to no module, so raising it from `approvals.submit` requires no edit to any error-code list.

**Files**
- Modify: `backend/src/app/platform/approvals.py:119-143` — resolution between the policy check and the row construction.
- Modify: `backend/src/app/api/approvals.py:110-146` — the fan-out, and **`responses=problems(401, 403, 409, 422)` at `:114` must grow a 404**.
- Modify: whichever owning modules need a `(slug, version)` lookup they do not have.
- Modify: `backend/src/app/platform/modelling.py:1240-1254` — the `return None` block that documents this hole; replace it with what is now true.
- Modify: `docs/specs/06-governance.md:161` — a dated amendment recording which shape was built and why.
- Test: `backend/tests/test_api_approvals.py` — existing FR-GOV markers are at `:56, :72, :99, :119, :138, :161, :175, :197, :209, :227`.

**Exit criteria**
- A reference naming a non-existent version is refused with `NOT_FOUND`, marked `@pytest.mark.req("FR-GOV-36")`.
- A negative test per resolvable type, or one parametrized over them.
- **An unresolvable type fails closed** — a test pinning `rating_version:x@1` proves the behaviour is decided rather than accidental. Follow `07`'s `JOB_HANDLER_NOT_REGISTERED` reasoning (`docs/specs/07-platform.md:317+`): a system deployable before every kind has an implementation must say so, not guess.
- `metrics.resolve_ref`'s divergent code either changed or documented as deliberate with the reason.

**Must NOT touch.** The approval decision path (`approvals.py:257` onward), the policy shape, or `EVIDENCE_FLOOR` — those are 1c's and slice 6's. Do not add an import-linter contract here.

### 1c — The `custom_metric` evidence floor

**The defect, stated accurately.** `06` §4.2's `DEFAULT_POLICY` ships `custom_metric → ["metric_certificate"]`, but §3.3's table has no Custom Metric row, so `EVIDENCE_FLOOR` has no key for it and `below_floor()` returns nothing.

**This is not exploitable, and the plan must not pretend otherwise.** `backend/src/app/platform/metrics.py:645-665` already documents the gap in full and explains what actually protects a metric: the lifecycle. Submission requires status `certified`; only `record_certificate` sets that status; it sets it alongside a `certificate_id`; and the `certified_metric_has_a_certificate` CHECK refuses the pair coming apart at a layer a direct `UPDATE` cannot walk past. An uncertified metric cannot be submitted even under an emptied policy.

What is real: **the policy reader is told a floor exists where none does** — the failure `POLICY_BELOW_EVIDENCE_FLOOR` was added to prevent — and §3.3 and the code disagree, which §0 says to resolve.

**Order matters and is stated in the code.** The §3.3 row comes **first**; adding the `EVIDENCE_FLOOR` entry alone would put the code above its own specification.

**Files**
- Modify: `docs/specs/06-governance.md` §3.3's FR-GOV-19 evidence table — a Custom Metric row citing `02` FR-MODEL-45/105/108.
- Modify: `packages/model-schema/src/model_schema/approvals.py:92` — `"custom_metric": ("metric_certificate",)`.
- Modify: `packages/model-schema/tests/test_approvals.py` — the floor test; note `:93` currently asserts `"peril_structure" not in EVIDENCE_FLOOR`, which stays true and is a different case.
- Modify: `backend/src/app/platform/metrics.py:638-665` — replace the "known gap" docstring with what is now true. **Do not delete the history**; follow the file's own convention of a dated correction.

**Exit criteria**
- `PUT /api/v1/approval-policy` refuses an entry dropping `metric_certificate` with `POLICY_BELOW_EVIDENCE_FLOOR`, proven by a negative test.
- `audit-docs.py` passes — §3.3 is a table, so watch the row's cell count and the check-10 anchor trap.

**Must NOT touch.** `custom_objective`'s floor, or the lifecycle CHECK constraint that is doing the real work.

---

## Slice 2 — FR-MODEL-23's remainder, and OQ-PLAT-7

One defect at two layers. Fixing either alone leaves the caller unable to see a named error, which is why they are one slice.

**Requirements:** `02` FR-MODEL-23; `07`'s error registry; OQ-PLAT-7 (open, maintainer-owned).

### The two layers

**Layer 1 — `pricing-core` loses the name.** `packages/pricing-core/src/pricing_core/modelling/glm.py:641` catches only `np.linalg.LinAlgError` around `estimator.fit(...)` and translates it to `GLM_RANK_DEFICIENT`. A bare `ValueError` from glum — a non-positive response under a log link, a malformed weight vector — is not caught, so it propagates raw. The covariance site at `:729` already catches `(np.linalg.LinAlgError, ValueError)`, so the asymmetry is within one file and visible in six lines of context.

**Layer 2 — the job boundary loses the code.** `backend/src/app/worker/tasks.py:181`'s `except Exception` stores `JobError(code="JOB_HANDLER_FAILED", ...)` for *every* unexpected exception, `PlatformError` included. `PlatformError.__init__` calls `super().__init__(detail or title)`, so `str(exc)` is never the code. **A named error raised in a handler is indistinguishable from any other handler failure once it reaches the caller.**

### The blocking decision

**OQ-PLAT-7 is open and maintainer-owned** (`docs/open-questions.md:132`), with three options and a recommendation of **(a)**: a dedicated `except PlatformError` clause before the generic one, storing `JobError(code=exc.code, message=exc.detail or exc.title)`. Take this decision before starting. If (b) or (c) is chosen instead, layer 1 still gets fixed but its exit criteria shrink to a pricing-core unit test, because no test through `execute_job` can then assert the code.

### Files
- Modify: `packages/pricing-core/src/pricing_core/modelling/glm.py:637-651` — widen the `except`, or add a sibling clause with its own code if a bad response vector deserves a different name from a singular design. **Prefer a distinct code**: `GLM_RANK_DEFICIENT`'s message names collinear terms, which is a lie for a non-positive response.
- Modify: `backend/src/app/errors.py` — register the new code in `MODELLING_ERROR_CODES` if one is added.
- Modify: `docs/specs/02-modelling.md` §5.1's error-code block — the catalogue entry.
- Modify (if OQ-PLAT-7 (a)): `backend/src/app/worker/tasks.py:175-195`.
- Modify: `docs/open-questions.md:132` — record the decision with its date.
- Test: `packages/pricing-core/tests/test_glm.py` beside the existing FR-MODEL-23 markers at `:134` and `:429`; and `backend/tests/test_model_jobs.py` for the job-boundary assertion.

### Exit criteria
- A negative test fitting a GLM whose response violates the family's domain, asserting the named code — **not** `JOB_HANDLER_FAILED`, if (a) was chosen.
- The existing `GLM_SEPARATION_DETECTED` and `GLM_RANK_DEFICIENT` tests unchanged and passing: this widens coverage, it does not move behaviour.
- `retryable` behaviour unchanged — OQ-PLAT-7's recommendation is explicit that `JobError.retryable` still defaults to `False`.

### Must NOT touch
The retry policy, other handlers' error paths, or `JOB_HANDLER_FAILED` itself, which remains correct for genuinely unexpected exceptions.

---

## Slice 3 — NFR evidence

The largest block of MODEL scope without evidence: **1 of 12**, and the one that is evidenced covers half its requirement. Exactly one `NFR-MODEL` marker exists in the whole 1626-test suite.

**Requirements:** NFR-MODEL-1…12 (`docs/specs/02-modelling.md:2332-2343`).

### The roadmap's own classification is wrong, and this slice corrects it

`docs/roadmap.md:2579` groups NFR-MODEL-7/8/9 as *"Testable today, no fixture needed."* Two of the three are not:

- **NFR-MODEL-7 has nothing to test.** There is **no Model export or import path anywhere in the repository** — not a route, not a CLI, not a bundle schema. The only `export` in the HTTP surface is the audit log (`backend/src/app/api/audit.py:238`). `FR-OVR-2`, its parent, carries **zero markers**.
- **NFR-MODEL-8's "position-accurate error" is not met.** `ExpressionError` (`packages/pricing-core/src/pricing_core/data/expressions.py:65`) attaches no `lineno`/`col_offset`; `_check` at `:69-86` refuses without position. `test_prepare.py:95` catches `(ExpressionError, SyntaxError)` interchangeably, so the two are not distinguished today.

**Correct the roadmap rows as part of this slice** — §0 forbids leaving a claim standing that the code contradicts.

### 3a — Testable today, genuinely

| NFR | Work | Anchor |
|---|---|---|
| **NFR-MODEL-6, GLM half** | Mirror the GBM determinism test: two `fit_glm` calls on one spec, `abs(a - b) <= 1e-10` pairwise over `GlmFitResult.coefficients`. **Note `GlmSpec` has no `seed`** — the GLM half is `spec_hash` determinism plus IRLS determinism, not seeded sampling. Say so in the test docstring. | Mirror `packages/pricing-core/tests/test_gbm.py:269-283`; use `test_glm.py`'s `_frequency_data()` `:39`, `_spec()` `:60`, `_factor()` `:32`. Assertion style: `test_ebm.py:428` |
| **NFR-MODEL-9** | Assert an Audit Event with `before`/`after` for each named act. **The four status transitions already carry `before`** (`modelling.py:1093, 1282, 1344, 1380`). | Mirror the `01` twin exactly: `backend/tests/test_data_nfrs.py:147`, which queries `AuditEventRow` by `workspace_id` + `action` |

**NFR-MODEL-9's real gap, and the verdict it needs.** `factor.created` (`modelling.py:248`), `banding.created` (`transformations.py:286`), `grouping.created` (`:344`), `model.reserved` (`modelling.py:438`) and `model.fitted` (`:827`) pass **`after=` only, no `before=`**. The requirement says "creation and edit … with before/after state". For a versioned artifact where an "edit" *is* a new version, create-only events arguably have no before by construction — **write that verdict down rather than adding an empty `before={}` to satisfy a grep.** Objective *derivation* is Phase 2 (`objectives.py:243` refuses `expression`), so it is out of scope and should be named as such.

### 3b — Measurement only

Record each in `02` §9 as a blockquote, following the NFR-MODEL-3 precedent at `docs/specs/02-modelling.md:2345-2366` **exactly**: a bolded verdict sentence with requirement id, date and `(W5)`; the data scale, machine and budget; a `| Thing | Measured | Verdict |` table with real numbers and bolded **met**/**not met**; the cause of any shortfall in numbers with the miss as a percentage; and routes out with a bolded **Owner:**. Then mirror it as a short pointer from `docs/roadmap.md` — spec first, roadmap points at it, never the reverse.

| NFR | Budget | How |
|---|---|---|
| **NFR-MODEL-4** | diagnostics ≤ 30% of fit wall-clock | `fit_seconds` already exists on all three fit results (`glm.py:652`, `gbm.py:690`, `ebm.py:282`). **There is no diagnostics-side timer** — wrap the three `compute_*_diagnostics` calls at `backend/src/app/worker/model_handlers.py:395-420` with `time.perf_counter()` and divide. A ratio needs no data scale, which is why it is measurable today |
| **NFR-MODEL-5** | certification < 3 min | The smoke fit already times itself (`pricing_core/modelling/objectives.py:1280`, reported in the check detail at `:1294`). `ObjectiveCertificate` has **no duration field**, so time `record_certificate` (`backend/src/app/platform/objectives.py:425`) or the pricing-core `certify` call |
| **NFR-MODEL-11** | diagnostics artifact < 50 MB | One JSONB document — `DiagnosticsRow.payload` (`db/models.py:1445`). Measure `len(json.dumps(d.model_dump(mode="json")).encode())`. The blob-spill the requirement names partly exists: `residual_blob`, `leverage_blob` (`model_schema/diagnostics.py:233-234`) |

**The one in-repo timing pattern to copy** is `backend/tests/test_api_datasets.py:442-456`: assert against generous slack (2500 ms against a 500 ms budget), `print` the real number, and state the budget in the assertion message. Its reasoning is `scripts/bench-data.py`'s docstring, which the plan should reuse verbatim: *"Not a CI gate. A timing assertion on a shared runner fails for reasons that have nothing to do with the code."* If a harness is wanted, `scripts/bench-model.py` is the natural sibling — `bench-data.py` knows only `01`'s budgets. Registering a new `slow`/`bench` marker needs `pyproject.toml:109-115`, which runs `--strict-markers` and registers only `req`.

### 3c — The two that need a decision, not code

- **NFR-MODEL-3 is measured and breached** — `hierarchical_clustering` at 6.52 s against 5 s, 30% over, Ward linkage O(n²). Its recorded owner, "the slice that builds the factor workbench", shipped 2026-08-15 without it. **Fix it** (a contiguous 1-D partition is legitimate since clusters are contiguous in rate order by construction, but it is a different method under the same name; or compute from the stored Profile as the requirement's own wording suggests, `01` FR-DATA-26), **or amend the budget with the reason.** Silence is the one option §13 rule 1 does not allow.
- **NFR-MODEL-1/2/10 need a fixture that does not exist.** All three name 5M rows × 60 factors; freMTPL2 is 678 013. Either build a synthetic fixture, or measure at a stated smaller scale **and write the extrapolation down**. NFR-MODEL-2's second clause (an `expression` objective adding ≤ 25%) is **Phase 2 regardless** — expression objectives do not exist.

### 3d — NFR-MODEL-7 and -8: decide the scope before writing tests

- **NFR-MODEL-7.** Either build a real export/import pair, or scope the requirement to "serialise Model + Diagnostics + blobs to JSON, reload in a clean process, `score_fitted` twice, compare bit-for-bit". The second is achievable with existing parts: `pricing_core.modelling.predict.score_fitted` (`predict.py:406`) dispatches all three model types, and `packages/pricing-core/tests/test_scoring_without_the_fitting_stack.py` already runs a subprocess with an import `Blocker` that makes `glum`/`sklearn`/`interpret` unimportable and passes artifacts as JSON on argv — the nearest thing to "a clean instance" that exists. **The first is a feature and would be its own slice.** Note the EBM round-trip tests (`test_ebm.py:221, :330`) are evidence for the EBM artifact only, and the roadmap says so at `:2820`.
- **NFR-MODEL-8.** The `eval`/`exec` clause is testable now — mirror `packages/pricing-core/tests/test_sql_check.py:73-151`'s four parametrized `NFR-DATA-9` refusals, and note `test_prepare.py:88`'s hostile-input list already covers `eval('1')`, lambdas, comprehensions, subscripts and f-strings under an `FR-DATA-10` marker. The position clause needs `lineno`/`col_offset` attached to `ExpressionError` first — small, but a feature.

**Two further §4.6 divergences found while mapping this, and they belong to whoever takes NFR-MODEL-8:** `02` §4.6 (`:829`) requires "AST node count ≤ 200 (configurable); nesting depth ≤ 20" and **neither limit is implemented**; and §4.6 declares the functions `log exp sqrt abs min max clip where log1p expm1` while `_FUNCTIONS` (`expressions.py:60`) provides `abs min max round floor ceil coalesce log exp sqrt` — `clip`, `where`, `log1p`, `expm1` absent and four extras present. Record both with a verdict.

### Exit criteria
- Nine NFRs carry evidence a reader can check — a marker, or a recorded measurement with the reason a test is the wrong instrument (§13 rule 1's "evidence is not only markers").
- Every NFR **not** closed has a written verdict and an owner. Twelve of twelve accounted for.
- The two wrong roadmap rows corrected.

### Must NOT touch
The four NFRs' budgets, unless amending one is the recorded decision. Do not invent a test that stands in for a measurement — the roadmap already asked for the opposite at `:2578`.

---

## Slice 4 — Bühlmann–Straub, or the decision not to build it

**Requirements:** `02` FR-MODEL-80 (`docs/specs/02-modelling.md:115`), OQ-MODEL-5 (decided 2026-08-15).

### The blocking decision, and why it is a decision rather than a task

W5's scope was set by a written decision: *"both, limited fluctuation as the default, recorded per grouping (FR-MODEL-80) — **so W5 builds two methods rather than choosing one**"* (`docs/roadmap.md:112`). One shipped. The refusal test's own docstring says it plainly: *"FR-MODEL-80 specifies it and this build does not implement it."*

So there are exactly two honest outcomes, and §0 forbids a third:
1. **Build it** — this slice.
2. **Supersede FR-MODEL-80's second method** with a dated amendment saying which side was wrong and why, and re-open OQ-MODEL-5 or raise a successor.

What is not allowed is closing W5 with FR-MODEL-80 counted among the 108 evidenced while the method it names is refused at runtime. **Take this decision before starting.**

### What the requirement actually demands

> Bühlmann–Straub is selectable and persists its variance components — **EVPV, VHM and the resulting `k`** — in the grouping evidence, so a reviewer can re-derive `Z` rather than take it.

The field is already declared: `GroupingEvidence.credibility_components: dict[str, float] | None = None` (`packages/model-schema/src/model_schema/modelling.py:478`), documented in §4.3 as *"carries Bühlmann–Straub's EVPV, VHM and `k` and is `null` under limited fluctuation"* (`02` `:467`). The hand-authored contract names the exact keys — `evpv`, `vhm`, `k` with `exclusiveMinimum: 0` (`docs/contracts/schemas/grouping.schema.json:52-56`).

**It is assigned nowhere.** `grouping_evidence`'s constructor (`groupings.py:497-505`) omits the field entirely, so it is always `None` — declared-and-unbuilt in FR-MODEL-87's sense.

### Where the code goes

| Piece | Location |
|---|---|
| The refusal to invert | `packages/pricing-core/src/pricing_core/modelling/groupings.py:222-232`. Note it reuses `GROUPING_NOT_EXHAUSTIVE`, which is about exhaustive mappings, not unimplemented methods — **if the code survives in any form, give it an honest code** |
| The limited-fluctuation path to sit beside | `_credibility_weighted` `:214`; portfolio rate `:242`; `Z = sqrt(min(n/n_full, 1))` `:247`; shrunk rate `:249`; sort-and-sweep merge `:255-268` |
| The full-credibility standard | `_full_credibility_claims(p, k)` `:51`, used at `:177` (stored rounded into `method_params`) and `:238` (fallback) |
| The per-level input | Not a Polars frame at this layer — `OneWaySummary`/`OneWayRow` from `01` (`pricing_core/data/profile.py:361`; fields at `model_schema/profiles.py:142-162`: `level`, `exposure_years`, `claim_count`, `claim_amount_minor`, `frequency`, `mean_severity`, `mean_burning_cost`). EVPV and VHM are computable from these |
| Where components must land | `grouping_evidence(...)` `:436-444` — **which has no `credibility_model` parameter and does not know which theory ran.** Threading the components through it widens a signature published in `02` §5.2 at `:1913-1914`, so this is a spec change too |

### Two things to fix while here

- **Marker misattribution.** `test_credibility_weighted_merges_on_shrunk_rates` (`test_groupings.py:271`) and `test_buhlmann_straub_is_refused_rather_than_silently_substituted` (`:289`) are marked `FR-MODEL-14`, not `FR-MODEL-80`, although they assert FR-MODEL-80's content. `scope-audit.py` therefore credits the wrong requirement. Fix the markers whichever way the decision goes.
- **A contract divergence for slice 5's list.** `source_level_stats` appears in `grouping.schema.json:63` and not in the Python `GroupingEvidence`. Record it; do not fix it here.

### Exit criteria

**If built:** `credibility_components` populated with `evpv`, `vhm`, `k` on a `buhlmann_straub` grouping and `None` on a limited-fluctuation one; a test proving the two methods give *different* answers on thin cells — the `:177` "not the same method under another name" precedent is the pattern; `(p, k)` still recorded for the limited-fluctuation path; the refusal test at `:289` inverted rather than deleted, so the record of what was once refused survives; `02` §4.3 and `grouping.schema.json` agreeing on the three keys.

**If superseded:** a dated amendment on FR-MODEL-80 stating which side was wrong; a successor open question or an explicit "one method is the whole capability" verdict; the refusal test kept and re-marked `FR-MODEL-80`; and `credibility_components` given a verdict rather than left declared-and-unbuilt forever.

### Must NOT touch
`bandings.py`'s `min_claims_per_band`, which is a separate credibility path that does not share `_full_credibility_claims`. `reference_hierarchy`, whose refusal is architecturally justified — a Reference Table needs a database, which ADR-0001 keeps out of pricing-core — and which therefore needs a backend-side implementation and its own owner.

---

## Slice 5 — The contract half

The largest single piece of work on the list, and the only slice whose **first task is a failing guard rather than a feature**. `docs/contracts/` is a published specification artifact external consumers read (FR-PLAT-48), so this is a wrong public contract, not an internal inconsistency.

**Requirements:** `00` FR-OVR-6, `07` FR-PLAT-48, `02` FR-MODEL-86/87/111.

### Why it went unnoticed — build the guard first

Two tests guard the hand-authored half and **neither can see a missing field**:

- `test_an_artifact_shape_carries_exactly_what_its_contract_declares` (`backend/tests/test_contracts.py:275`) is the only field-*existence* check and is parametrized over four slugs: `banding`, `grouping`, `custom-objective`, `profile`.
- `test_generated_and_authored_agree_on_scalar_types` compares only the **intersection** of dotted paths present on both sides and drops `null` by design (`:414-421`). A field on one side only is structurally invisible; so is every nullability divergence.

Of 26 hand-authored schemas, 12 are in `COMPARED_SLUGS` and only 4 have the existence check. **Eight lack it; six are MODEL-owned** — `model`, `model-spec`, `diagnostics`, `transparency-artifact`, `objective-certificate`, `peril-structure`. The remaining two (`audit-event`, `job`) belong to GOV and PLAT. The other 14 unguarded schemas are later-phase modules and are **out of scope**.

**Task 1 is therefore: add those six slugs to the existence test's parametrize list and watch it go red.** That converts a prose audit finding into a mechanical one and gives every later task its own failing test. Do not fix a single schema before this is red.

### The known divergences

Verified during the audit; expect the red test to find more, and treat the list as a floor rather than a ceiling.

| Schema | Divergence |
|---|---|
| `model` | `dataset_version_id` absent from `properties` entirely, though `Model.dataset_version_id: UUID` has no default. `fit_result` is written for the GLM arm only: `required` names `converged`, which `GbmFitResult` does not have, and omits `booster_format`, `base_margin` and `best_iteration`, which a GBM needs to be scoreable. `feature_dtypes`, `categorical_maps` and `dropped_eval_metrics` undeclared. `monotone_constraint_vector` is really `monotone_constraints`. `Coefficient.exposure_years` is fictional; `relativity` is nullable in code and non-nullable in the contract — the contract still models the pre-fix behaviour of a bug the spec documents as resolved. |
| `model-spec` | The nested `regularisation` object that FR-MODEL-87 says was "corrected in place" to flat `GlmSpec` fields. No `tweedie` property, so FR-MODEL-22 is inexpressible. Missing `loss_treatment`, `approximates_model_id`, `interval_for` — three of the ten fields that moved `spec_hash`. **`ebm` is in the `model_type` enum with no `if`/`then` branch**, so a malformed EBM spec validates with zero field-level checking. Conversely `filter` and `custom_objective_ref` are declared and do not exist on the types. |
| `diagnostics` | The `gbm` block differs in name, cardinality or shape on nearly every field: `importances` plus a separate `permutation_importances`; `partial_dependence` is structured objects not a blob string; `monotonicity` is a tuple of checks not a boolean; three depth fields not a `tree_summary`; `quantile_crossing` (FR-MODEL-78) has no property at all; `best_iteration` is declared here but lives on the fit by explicit design. |
| `transparency-artifact` | `id`, `created_at`, `job_id` absent. `kinds` is a derived `@property` declared as a writable array. `approximating_model_id` unconditionally `required` though it is optional and mutually exclusive with inline coefficients. `r_squared`/`deviance_explained` carry `minimum: 0` the code deliberately does not apply. `relativity_table_blob` typed `string` where the payload is a `BlobRef` object. |

### Error codes — same slice, same class of defect

- **Dead:** `OBJECTIVE_NOT_CERTIFIED`, `TRANSPARENCY_ARTIFACT_REQUIRED`, `PICKLE_PERSISTENCE_REFUSED` are claimed by `02` §5.1's catalogue and appear nowhere in `errors.py`. The features they would guard use generic codes instead — `VALIDATION_FAILED` (`platform/objectives.py:508`) and `06`'s `EVIDENCE_INCOMPLETE` (`platform/modelling.py:1148`). `PICKLE_PERSISTENCE_REFUSED` would raise `ValueError: unknown error code` if anything tried to raise it.
- **Uncatalogued:** `MODEL_SPLIT_REQUIRED` is live, registered and raised from two sites in `model_handlers.py`, and appears only in prose.
- **Why the gate is silent:** `audit-docs.py` checks error-code ownership-*exclusivity*, not existence.

**The §0 question each dead code poses:** was the spec right and the code wrong (build the named code), or the code right and the spec wrong (mark the catalogue entry superseded with a dated note)? Answer per code, in writing. `PICKLE_PERSISTENCE_REFUSED` is the interesting one — `model_schema/modelling.py:1526` references it in a comment, so decide whether pickle refusal deserves a branchable code at all.

### 5b — The interfaces the spec no longer describes

Same theme, different file: §5.1's endpoint table matches the code in both directions (all 40 rows, verified), but the **parameters** and §5.2's **signatures** do not. A caller copying from the page writes a call that fails loudly, or — worse — one that silently does nothing.

| Interface | Spec says | Code does | Consequence |
|---|---|---|---|
| `fit_glm`, `linear_predictor`, `predict_glm`, `predict_glm_interval`, `compute_diagnostics`, `backtest_model` (`02` `:1918-1933`) | no `model_offset` | all take `model_offset: np.ndarray \| None = None` (`glm.py:517`, `predict.py:198/230/260`, `diagnostics.py:562/695/706`) | FR-MODEL-24 is documented at length in §3.4 and unreachable from §5.2 |
| `fit_gbm` (`:1946-1951`) | no `metrics` | takes `metrics: Mapping[str, CustomMetric] \| None = None` (`gbm.py:592`) | custom metrics unexercisable from pricing-core by a §5.2 reader |
| `compute_gbm_diagnostics` (`diagnostics.py:915`) | **not declared at all** | exported, in `__all__`, called from `model_handlers.py:401` | the GBM diagnostics entry point has no published signature |
| `resolve_factors`, `propose_banding`, `check_banding`, `propose_grouping`, `grouping_evidence` (`:1899-1915`) | first arg `df`; `check_banding` defaults `0.0/0.0/False` | first arg is `frame` everywhere; defaults are `None`-sentinels falling back to the banding's own `minimums`; `exposure_column`/`claim_count_column`/`claim_amount_column`/`source` undeclared | `check_banding(df=...)` raises `TypeError`; and a reader believes an unconfigured check floors at 0 |
| `GET /api/v1/factors?dataset={slug}` (`:1511`) | `dataset` taking a slug | `dataset_id: UUID` (`api/models.py:227`) | **the slug form is silently ignored** and every factor comes back unfiltered — the worst failure mode on this list |
| `GET /api/v1/models/{id}/diagnostics` (`:1523`) | `{id}` | `{slug}` + `?version=` | the sibling row got exactly this amendment on 2026-08-15; this one did not. **Only this row is wrong** — the other `{id}` rows are correct, those routes really do take a `model_id` |

**§5.3's views.** Six of eight are unbuilt and only two carry an in-spec "not built" note (`:2225-2236`). The other four — spec builder, diagnostics, comparison, peril structure — are recoverable as W6b's only from `CLAUDE.md`'s layout table. **This is a sequencing gap, not a defect**: add the notes, and do not build the views.

### 5c — Four strays that belong here

| Item | Work |
|---|---|
| **No `GET /models` list route** | Factors, bandings and groupings each publish one; models publish none, and §5.1 does not declare one. So "40 of 40 endpoints, 100%" is true but measures the spec against itself. Noticed while writing lifecycle tests that had to read a family slug straight from the database (`roadmap.md:1537`), recorded as "worth a plan-review question" and never answered. **Answer it**: add the route and the §5.1 row, or record why a list route is wrong here |
| **`ReconcileRequest.tolerance` is a bare `Decimal`** | `backend/src/app/api/peril_structures.py:96`. A JSON number coerces there and is stringified into the job parameters — the same float hole `DecimalStr` closed one layer up under FR-OVR-18. Recorded when found, never fixed, no owner |
| **`02` §4.8 has never carried a GBM `fit_result` example** | Examples exist for GLM (`:1017`) and EBM (`:1144`) only, so `dropped_eval_metrics` had none to join and FR-MODEL-111's amendment points readers at the generated contract instead |
| **FR-MODEL-88's three unbuilt factor arms** | `spline`, `polynomial`, `offset` are refused by name; each needs its own contract field and resolver argument. **No owner named.** Give it one or a dated deferral — do not leave it counted among the evidenced |

### Exit criteria
- The six MODEL-owned slugs pass the field-existence test, which is red at task 1 and green at the end.
- A decision recorded for the nullability question: either the existence test compares nullability too, or `:414-421`'s reason is restated as still-deliberate with a dated note.
- Every dead error code either exists or is marked superseded; `MODEL_SPLIT_REQUIRED` is in the catalogue.
- `generate-contracts.py --check` still 0 — **this slice must not touch `schemas/generated/` or `openapi/generated.json`.**
- Every §5.2 signature in the table above matches the code, checked in both directions.
- `GET /factors`'s parameter and the diagnostics row corrected, each with a dated amendment naming which side was wrong (§0).
- The four unbuilt §5.3 views carry an in-spec "not built, owner W6b" note.
- Each of 5c's four strays either fixed or given a dated verdict with an owner.

### Must NOT touch
The generated half. The 14 later-phase unguarded schemas. `audit-event` and `job`, which are GOV's and PLAT's — note them for their owners in the slice record instead.

---

## Slice 6 — Bookkeeping, owners, and the closure record

Runs **last**: it states the final position of every other slice. Nothing here changes what is built; all of it changes what a reader believes is built, which is the thing §13 exists to protect.

**Procedure:** `.claude/skills/close-workstream`, which carries the commands and worked examples. `CLAUDE.md` §13 is the standard it implements. Run `.claude/skills/phase-review` as well — §14 requires a plan review *at every workstream close*.

### 6a — Eight stale or contradictory claims

Each is a one-line edit; the discipline is that corrections are **appended or struck, never overwritten**, because what was believed on the day is what a governed record cannot lose.

| Location | Says | Correct to |
|---|---|---|
| `roadmap.md:2906` | "twenty-two slices in" | **27.** The enumeration omits regularisation/CV, Tweedie, offsets, EBM and GBM weights. Corrected twice before for exactly this |
| `roadmap.md:2562` | "**one** [buildable slice remains]" | **Zero** — all five rows beneath are struck as delivered |
| `roadmap.md:1446-1451` | FR-MODEL-56, 63, 64, 67, 77, 78 "Not started" | Delivered by later slices. The same table struck 53 and 57 when they landed |
| `roadmap.md:1240` | FR-GOV-10 "not started, W4/W5" | **Delivered** — `backend/tests/test_model_lifecycle.py:246` proves `EVIDENCE_INCOMPLETE` fails closed. A W3-era verdict nobody struck |
| `roadmap.md:65` | AST parser "Phase 1, W5" | Contradicts OQ-MODEL-1 (expressions → Phase 2) and `:2981` (W30 owns it) |
| `roadmap.md:1291` | "one slice of seventy-eight requirements" | **124**, re-derived 2026-08-22 |
| `roadmap.md:264` | "writing that skill is the outstanding item" | `.claude/skills/phase-review/` exists |
| PRs #124, #125 | — | Landed with **no slice records**. The 3rd and 4th such omission; the file names the first two and not these |

**The two missing slice records are the substantive item here**, not a typo. Write them from the branches' commits the way the GLM-approximation record was reconstructed on 2026-08-19 — and say in each that it was written late, because that is the process finding.

### 6b — Five owners defined by an event nothing schedules

§13 rule 1 allows four verdicts for an unevidenced requirement: delivered-but-untested, deferred with an owner, reassigned, or not started. An owner phrased as a future event that nothing has scheduled is none of them — it reads as an owner and functions as silence. Give each a workstream or a dated deferral.

| Item | Owner as written |
|---|---|
| `models.diagnostics_id` guard | "the next slice to touch that trigger" — **discharged by slice 1a**; strike it |
| FR-MODEL-59 excess layer | "the slice that fits an excess-layer model" |
| FR-GOV-37 remainder (`model_comparison_if_predecessor`) | "the slice that gives model_comparisons a queryable model reference" |
| Penalised covariance | "the slice that builds the first such consumer" |
| EBM `interactions=2` triples | **nothing at all** — the 2026-08-22 record names this a defect in its own right but does not apply the same judgment to the other four |

### 6c — The headline number

**Restate MODEL's completion as three numbers, not one.** `scope-audit.py` counts a requirement as evidenced when any test carries its marker, and five requirements — FR-MODEL-23, 59, 80, 87, 88 — carry markers on tests asserting the feature is *refused*. So 108/124 means 87% **declared-or-refused**, not 87% built.

The roadmap already caught this once, on FR-MODEL-81, 2026-08-16: *"the requirement counted as evidenced because a test marked it."* The lesson was recorded against that one requirement and never applied to the headline. The closure record must not repeat it.

Report as: **N built · N declared-and-refused-by-name · N deferred with an owner**, with the refused list enumerated.

### 6d — Verify one failure class before signing

The 2026-08-22 slice ran `git log -S` and found that a "dated note 2026-08-21, owner W5" the EBM slice claimed to have written **had never been written** — an obligation recorded as discharged against evidence that did not exist. Before closing, verify every remaining "dated note, owner W5" claim in a slice record against `02-modelling.md` rather than trusting it. `git log -S'<phrase>' -- docs/specs/02-modelling.md` is the instrument.

### 6e — The blocking decision

**FR-MODEL-6's reassignment to W30 is "maintainer acceptance pending"** at `roadmap.md:2589` and `:2985`, dated 2026-08-19. §14 requires an explicit dated acceptance line. Until it is accepted or rejected, a requirement inside W5's own module has formally ambiguous ownership and W5 cannot honestly disown it.

### Exit criteria
- §13's eight rules each answered in the closure record, including rule 6's "state what was *not* delivered" with a verdict and owner for every unevidenced requirement.
- The roadmap status table, §2's layout marks, and `docs/open-questions.md` updated in the same PR.
- `uv run pytest backend/tests/test_demo_guide.py` passes — FR-PLAT-54's guide is derived, so the check is that it still derives.
- No open PRs for W5; branch deleted after merge, **verified by content** (`git diff --stat main <branch>`), because squash-merge rewrites history.
- A §14 phase review recorded, every question answered including "no change".

### Must NOT touch
Any requirement's number. Any accepted ADR's body — amend by addendum. And do not close a slice-1-to-5 item here that its own slice left open; record it instead.
