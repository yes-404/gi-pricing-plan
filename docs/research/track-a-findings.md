# Track A — Research findings

**Run:** 2026-08-14 · **Scope:** [`skills-map.md`](../skills-map.md) §7 research priority
**Method:** primary documentation, plus **four executable spikes** run against real library
versions. Spike scripts are throwaway and were not committed; every result below is
reproducible from the description given.

> **Read this first:** three findings *changed the specification* and one **corrected a
> fabricated number** in it. Those are marked ⚠. Findings that merely confirmed an existing
> design are marked ✓.

| # | Question | Verdict | Effect |
|---|---|---|---|
| F1 | Does the ZEN Engine preserve exact decimal money? | ✓ **Yes** — `rust_decimal`, not `f64` | **OQ-614 resolved**; ADR-706 confirmed; spike re-scoped |
| F2 | Can SymPy differentiate the `where()` → `Piecewise` form? | ✓ Yes, and the spec's derivatives are provably correct | FR-144 confirmed |
| F3 | Does the certification design work on a piecewise objective? | ⚠ **No** — it would reject sound objectives | §4.7 amended |
| F4 | Is the spec's example convexity figure real? | ⚠ **It was invented** | Corrected |
| F5 | Does `predt` include `base_margin` in a custom objective? | ✓ Yes — the spec's comment was right | Confirmed, with a new silent-failure risk |
| F6 | Do discriminated unions survive to JSON Schema? | ✓ Yes, but in a different shape than drafted | Contracts note added |
| F7 | Is `Decimal` safe through the generated contract? | ⚠ **Generated schema permits a lossy `number`** | FR-10 gap closed |
| F8 | Does glum expose standard errors? | ✓ Yes — named API | FR-113 confirmed |
| F9 | Is pandera's Polars support production-ready? | ✓ Yes, plus a lazy backend | NFR-466 strengthened |
| F10 | Is the Polars streaming engine safe for aggregation? | ⚠ Open memory regression | ADR-707's split validated |
| F11 | What actually consumes a 50 ms p99 budget? | ⚠ Pydantic on the hot path | NFR-489 guidance added |
| F13 | Is LightGBM's `init_score` symmetric with XGBoost's `base_margin`? | ⚠ **Half** — symmetric at fit, **asymmetric at scoring** | FR-129 added (spike S3) |

---

## F1 — ZEN Engine numeric semantics (OQ-614) ✓

**The suite's highest-risk unknown is resolved, favourably.**

`zen-types` defines the `Variable` enum with `Number` backed by **`rust_decimal`**, and
"all node inputs/outputs and expression results use this type system". Evaluating
`50 * tax.percentage / 100` returns `Variable::Number(dec!(5))` — an exact decimal, not a
float.

`rust_decimal` characteristics: 96-bit integer mantissa, ~28–29 significant digits, values
of the form `m / 10^e` with `-2^96 < m < 2^96` and `e ∈ [0, 28]`.

**ADR-706 stands.** The integer-minor-units workaround proposed in the original OQ-614
recommendation is **not required for correctness** inside the engine.

### But the risk moved rather than vanished

| Residual risk | Evidence | Mitigation now specified |
|---|---|---|
| **Serialisation boundary** | `rust_decimal` "currently serializes numbers in a float like format by default"; exact JSON needs the `serde-with-arbitrary-precision` feature. `arbitrary_precision` is no longer default for Rust crate consumers, though **Python/Node/C/UniFFI bindings opt in automatically** | `03` FR-273 — verify arbitrary precision on **both** parse and serialise at every boundary crossing |
| **`maths-nopanic` returns `0`** | `zen-engine` enables this feature; invalid input to `ln`/`log10` yields **0 instead of panicking** | `03` FR-274 — no unguarded transcendental in a rateable path; a domain guard is mandatory |
| **Scale capped at 28** | `rust_decimal` scale ∈ [0, 28] | Bounded by the ladder's rounding discipline (FR-226); worth a check in the S1 spike |

The S1 spike is **not cancelled — it is re-scoped**: from "can the engine do decimal?" to
"is precision preserved across the Python binding boundary, and does any rateable path
reach a `maths-nopanic` sink?"

**Sources:** [gorules/zen](https://github.com/gorules/zen) ·
[zen internals](https://deepwiki.com/gorules/zen) ·
[rust_decimal](https://docs.rs/rust_decimal/latest/rust_decimal/)

---

## F2–F4 — Custom objective certification (spike, SymPy 1.14.0)

The spike took the asymmetric burning-cost objective **exactly as written in
`02` §4.6** and put it through the pipeline FR-144 describes.

### F2 — SymPy handles the grammar ✓

`where(cond, a, b)` → `Piecewise((a, cond), (b, True))` differentiates cleanly, twice.
The derived form pushes the `Piecewise` **outward**:

```
LOSS : w*(y - exp(f))**2*Piecewise((w_under, y > exp(f)), (w_over, True))
GRAD : Piecewise((2*w*w_under*(-y + exp(f))*exp(f), y > exp(f)), (2*w*w_over*(...)*exp(f), True))
HESS : Piecewise((2*w*w_under*(-y + 2*exp(f))*exp(f), y > exp(f)), (2*w*w_over*(...), True))
```

The spec presented the derivatives with the `Piecewise` as an inner multiplicative factor.
**Symbolic identity check confirmed the two forms are equal** (`simplify(derived - spec) == 0`
for both gradient and hessian), so the spec's mathematics is correct — but the *canonical*
form a reviewer will see is the outward one. `02` §4.6 now shows the canonical form.

### F3 — The certification design would reject sound objectives ⚠

Running the §4.7 checks as specified:

```
symbolic vs numeric gradient :  8.92e-07   pass
symbolic vs numeric hessian  :  3.01e-01   FAIL
```

The hessian failure is **not a derivative error**. The objective has a genuine kink at
`exp(f) = y`, where the hessian is discontinuous, and a central second difference straddling
that point is simply invalid:

| Distance from kink | Worst relative error |
|---|---|
| ≥ 1e-5 | **3.77e-04** (pure truncation on a steep function) |
| at the kink | **~2.5e-01, and it does not shrink with step size** |

Halving the step does not help: the contaminated band narrows with `h`, but the relative
error inside it stays at ~1.1e-01 for every `h` tested (1e-4, 1e-6, 1e-8).

**Consequence:** as originally written, FR-146 would have failed **every**
`where()`-based objective — the entire reason the expression form exists. Amended in
`02` FR-146 and §4.7:

1. Sample points within `h` of a `Piecewise` branch boundary are **excluded** from the
   finite-difference comparison, and the excluded count is reported.
2. The kink is reported as a **finding in its own right** — a discontinuous hessian affects
   boosting stability and is real information, not noise to suppress.
3. Tolerances are **step-aware**. The spec's original `7.4e-8` example was unrealistically
   tight: truncation alone gives `3.8e-04` at `h=1e-6` on a steep function. Richardson
   extrapolation is recommended where the function is smooth.

### F4 — A fabricated figure, corrected ⚠

`02` §4.7's example certificate stated *"hessian < 0 on 12.3% of the sampled domain"*. **That
number was invented and formatted to read as a measurement.** Measured on the spike's grid
the figure is **63.9 %**, and it is strongly dependent on the sampling ranges.

Corrected in the spec, and the example is now explicitly labelled as illustrative with its
sampling domain stated — because a certificate is an evidence artifact and an invented
number inside one is exactly the failure the governance design exists to prevent.

---

## F5 — XGBoost `base_margin` (spike, XGBoost 3.4.0) ✓ + ⚠

`02` §5.2 asserted, in a code comment, that `base_margin` is already included in the
`predt` handed to a custom objective. XGBoost's documentation never states this. Measured:

| Setup | `predt` at iteration 0 |
|---|---|
| No `base_margin`, `base_score=0.5` | `[0.5, 0.5, 0.5, …]` |
| `base_margin = log(exposure)` | `[-0.791873, -0.259083, …]` — **exactly `log(exposure)`** |

**Verdict: `predt` does include `base_margin`. The spec's comment was correct** and a custom
objective must *not* add the offset again.

### The new finding ⚠ — `base_margin` replaces `base_score`, and omitting it fails silently

At prediction time, omitting `base_margin` does not merely drop the offset — XGBoost
substitutes `base_score` in its place:

```
predict without margin : [ 0.217962,  0.217962,  0.154070, …]   (trees + base_score 0.5)
predict with    margin : [-1.073911, -0.541121, -0.706240, …]   (trees + log(exposure))
difference             : log(exposure) − 0.5, not log(exposure)
```

No error is raised. A forgotten `base_margin` at scoring time yields a **confidently wrong
premium**. `02` FR-125 and FR-193 now require the offset construction to be
persisted with the booster and **asserted at load time**, not merely documented.

**Sources:** [Advanced custom objectives](https://xgboost.readthedocs.io/en/latest/tutorials/advanced_custom_obj.html) ·
[Custom metric & objective](https://xgboost.readthedocs.io/en/stable/tutorials/custom_metric_obj.html)

---

## F6–F7 — Pydantic v2 → JSON Schema (spike, Pydantic 2.13.4 / pydantic-core 2.46.4)

### F6 — Discriminated unions survive ✓ (in a different shape)

`TypeAdapter(...).json_schema()` emits `oneOf` plus a proper `discriminator`:

```json
{"propertyName": "model_type",
 "mapping": {"glm": "#/$defs/GlmSpec", "xgboost": "#/$defs/GbmSpec",
             "lightgbm": "#/$defs/GbmSpec", "ebm": "#/$defs/EbmSpec"}}
```

A `Literal` with two values maps **both tags onto one branch** — exactly the
`xgboost`/`lightgbm` sharing that `model-spec.schema.json` needs. ADR-704's generation
path is viable.

**Note for Phase 1:** the hand-drafted contracts express variants as `allOf` + `if`/`then`.
Pydantic generates `oneOf` + `discriminator`. **These are different shapes**, and generation
will replace the drafted form. Recorded in `contracts/README.md` so nobody treats the
hand-written `if`/`then` as the target.

**Minor gap:** an invalid tag raises `union_tag_invalid` with an **empty error location**
(`loc == ()`). `00` §5.3 promises a field-level `errors[].field`, so the backend must
synthesise the discriminator's field name for these errors.

### F7 — `Decimal` reaches JSON Schema as a permissive `anyOf` ⚠

```json
"relativity": {"anyOf": [{"type": "number"},
                         {"type": "string", "pattern": "…"}]}
```

Serialisation itself is safe — `model_dump_json()` emits `"1.0400"` as an exact **string**.
But the *generated schema also permits `{"type": "number"}`*, the lossy binary-float form
that FR-10 forbids.

The contract would therefore be satisfiable by a payload the specification prohibits.
`contracts/README.md` and FR-10 now require monetary and relativity fields to be
**constrained to the string form** in the generated schema, not left as `anyOf`.

---

## F8 — glum ✓

`GeneralizedLinearRegressor` exposes `std_errors()` and `covariance_matrix()` supporting
non-robust, robust (HC-1) and clustered variants, plus a coefficient table with confidence
intervals and p-values. Exposure offsets are handled natively.

**FR-113 is achievable as written**, and `02` §8 now names the real API instead of
assuming one exists.

**Source:** [glum changelog](https://glum.readthedocs.io/en/latest/changelog.html)

---

## F9 — pandera ✓

Version 0.29 (January 2026) is mature across pandas, Polars, Dask, Modin, PySpark and Ibis
from one schema definition. Polars `DataFrame` and `LazyFrame` are both supported via
`DataFrameSchema` and `DataFrameModel` (since 0.19).

**New capability worth adopting:** 0.32.0 ships an optional **Narwhals-powered backend that
keeps validation fully lazy**, installable as `pandera[narwhals,polars]`. This directly
serves NFR-466 (structural layer must fail fast in ≤ 2 min) — recorded in `01` §8.

**Sources:** [pandera Polars](https://pandera.readthedocs.io/en/latest/polars.html) ·
[0.19 release](https://github.com/unionai-oss/pandera/discussions/1617)

---

## F10 — Polars streaming engine ⚠ (and an accidental validation of ADR-707)

The new morsel-driven streaming engine has out-of-core group-by, equi-join and sort with
spill-to-disk, and is the recommended path for large workloads in 2026.

**However** — [issue #25607](https://github.com/pola-rs/polars/issues/25607), **still open**:
a simple group-by over Parquet consumes **> 6 GB RAM** on Polars 1.35.2 where the *old*
streaming engine (1.15) did not. A regression, with no team response recorded.

**This validates [ADR-707](../adrs/ADR-00707-polars-duckdb-as-the-data-engine-not-pandas.md)'s division of labour
for a reason the ADR did not anticipate.** The ADR assigns *aggregation* to DuckDB and
*row-level transformation* to Polars. Profiling, one-ways, PSI and dislocation — the heavy
group-bys — therefore never touch the affected code path. Recorded as an addendum to
ADR-707 rather than a change to it.

---

## F11 — Low-latency serving ⚠

Relevant to NFR-489 (p99 < 50 ms) and NFR-490:

- Pydantic validation costs roughly **~1 ms per request** as a baseline — 2 % of the budget
  before any pricing work happens.
- **`response_model` forces outbound validation** and is expensive; the response path runs
  three to five transformations (model → dict → JSON → bytes).
- Pydantic v2 is 4–17× faster than v1 (Rust `pydantic-core`), so the baseline assumption
  holds only on v2.
- `ORJSONResponse` is a C encoder that releases the GIL during encoding.

**Consequence for `03`:** the scoring endpoint must **not** use `response_model` validation
on the hot path — the `ScoringResult` is constructed by `pricing-core` and is already
trusted. Added as NFR-502.

---

## F12 — Vue Flow ✓

`isValidConnection` supports per-handle or global edge validation, which is the mechanism
behind `03` FR-212's "an invalid graph is visibly invalid before save". Large graphs
need memoised custom node components, and Web Workers are the escape hatch for heavy layout
— relevant because a motor structure is ~200 steps.

---

## F13 — LightGBM `init_score` (spike S3, LightGBM 4.7.0 / XGBoost 3.4.0) ⚠

The dual-backend contract assumed `init_score` behaves like `base_margin`. **It does at fit
time and does not at scoring time**, which is the half that matters.

| Behaviour | XGBoost 3.4.0 | LightGBM 4.7.0 | Symmetric? |
|---|---|---|---|
| Offset included in the raw score passed to a custom objective | yes (`base_margin`) | yes (`init_score`) | **✔ yes** |
| Implicit intercept when no offset is supplied | `base_score` = 0.5 | **0.0** — none under a custom objective | ✘ (benign) |
| Offset can be re-supplied at prediction time | ✔ `DMatrix.set_base_margin()` | ✘ **no such parameter exists** | **✘ — the material one** |
| Failure mode if the offset is missing at scoring | silently substitutes `base_score` | silently returns trees only | both silent, different causes |

**Fit time (symmetric).** With `init_score = log(exposure)`, the raw score at iteration 0 is
exactly `log(exposure)`. Without it, iteration 0 is `0.0` — LightGBM adds no implicit
intercept under a custom objective, where XGBoost adds `base_score`.

**Scoring time (asymmetric).** `Booster.predict()`'s parameters are
`data, start_iteration, num_iteration, raw_score, pred_leaf, pred_contrib,
data_has_header, validate_features` — **there is nowhere to put an offset**. Measured
against the fitted raw score:

```
corr(predict_raw            , train_raw) = 0.449336
corr(predict_raw + log_expo , train_raw) = 0.998968
mean |predict_raw           - train_raw| = 0.550092
mean |predict_raw + log_expo - train_raw| = 0.037736   (residual is the one-round lag)
```

`predict()` returns **tree contributions only**. The caller must add the offset back.

**Why this is worse than it looks.** A shared "apply the offset" helper written against
XGBoost's API sets `base_margin` on a matrix. On LightGBM there is no equivalent call, so
the natural port is *no call at all* — and predictions are then wrong by exactly
`log(exposure)`, with nothing raising. The XGBoost failure at least has an API surface you
might notice you skipped; this one does not.

Recorded as **FR-129**: implement the scoring-side offset per backend, and assert on
each backend independently that `predict(fit_data)` reproduces the fitted raw score.

**Spike S3 is closed.**

---

## F14 — ZEN binding precision (spike S1, zen-engine 0.53.0) ⚠

**This corrects F1.** F1 established the engine's internal type is `rust_decimal` and I
concluded the integer-minor-units workaround was "not required for correctness". S1 tested
the whole path and found that conclusion **right about the engine and wrong about the
system**.

**Inside the engine — exact.** The decisive test passes:

```
0.1 + 0.2 == 0.3   ->  true          1.005 * 100  ->  100.5
1.1 * 3   == 3.3   ->  true          2.675 * 100  ->  267.5
```

A float engine fails every one of these. ADR-706 stands.

**At the Python binding — no decimal type exists.**

```
Decimal("1.005")  ->  TypeError: argument 'ctx': unsupported type Decimal
1/3               ->  0.33333333333333337        (Python float)
36120 + 7         ->  36127.0                    (Python float)
```

Exactness cannot cross the boundary in either direction. Hence **FR-273 rewritten**:
money crosses as integer minor units, which *are* exactly representable in `float64` up to
2^53 (≈ £90 trillion in pence). The workaround is required after all — not because the
engine is inexact, but because the binding is.

### FR-274 was aimed at the wrong operation

It guarded `ln`/`log10` under `maths-nopanic`. S1 found **`log` and `sqrt` do not exist in
the ZEN expression language** — they fail to parse. The requirement guarded calls that
cannot be made.

The real hazard is **division**:

```
1/0  ->  None      0/0  ->  None      premium/0  ->  None     (no exception)
(1/0) + 5  ->  RuntimeError vmError                            (raises only on USE)
```

A null propagates until something consumes it, and the error then names the *multiply*,
not the division that produced it. Worse, a null reaching an `output` step would emit a
null premium. Rewritten accordingly.

### A third find

`min(1,2)` / `max(1,2)` are **invalid function calls** in ZEN, yet `03` FR-244 lists
`min` and `max` as available. `abs`, `round`, `floor`, `ceil`, `sum` do work. Added
**FR-276**: resolve the function vocabulary against the real engine at compile time,
so a graph cannot call something that exists only in our documentation.

**Spike S1 closed.**

---

## F15 — `exact`-mode GBM latency (spike S2, XGBoost 3.4.0) ✓

500 trees × 60 features, single-row raw-margin prediction — what a `model_call` does per
quote. 3 000 iterations after warm-up:

| Path | mean | p50 | p95 | **p99** | max |
|---|---|---|---|---|---|
| `nthread=1`, incl. `DMatrix` build | 0.377 | 0.345 | 0.476 | **1.088** | 4.501 |
| `nthread=1`, predict only | 0.109 | 0.084 | 0.169 | **0.326** | 1.200 |
| all cores, incl. build | 0.409 | 0.351 | 0.511 | **1.477** | 7.341 |
| all cores, predict only | 0.101 | 0.079 | 0.146 | **0.356** | 19.897 |
| `inplace_predict`, `nthread=1` | 0.350 | 0.302 | 0.526 | **0.773** | 4.618 |

(ms; measured on a 2-core box.)

**`exact` mode costs ~1 ms of a 50 ms budget — about 2 %.** OQ-615 resolves favourably,
and importantly **OQ-575 is not decided by force**: rating on the exact model or on its
GLM approximation stays a genuine design choice.

**Threading is the actionable finding.** All-cores is *worse* at the tail than single-thread
— p99 1.48 vs 1.09 ms, and a 19.9 ms worst case against 4.5 ms — because thread-pool
spin-up dominates a single-row prediction. Parallelism belongs across concurrent requests.
Recorded as **NFR-501**.

**Caveat:** this measures per-request latency on an unloaded 2-core machine, not p99 under
200 rps sustained. The per-request measurement is the right unit for a single-threaded
model call, and 50× headroom is robust to the caveat, but a load test still belongs in
Phase 2.

**Spike S2 closed.**

## What this changes

| Document | Change |
|---|---|
| [`open-questions.md`](../open-questions.md) | OQ-614 → `decided`; S1 spike re-scoped |
| [`02-modelling.md`](../specs/02-modelling.md) | FR-146 kink handling; §4.7 corrected figures + step-aware tolerance; §4.6 canonical derivative form; FR-125/193 base_margin assertion; §8 glum API named |
| [`03-rating-engine.md`](../specs/03-rating-engine.md) | New FR-273/274 (precision boundary, `maths-nopanic`); NFR-502 (no `response_model` on the hot path) |
| [`01-data-management.md`](../specs/01-data-management.md) | pandera Narwhals lazy backend |
| [`ADR-706`](../adrs/ADR-00706-gorules-zen-engine-executes-rating-dags.md) | Addendum: confirmed, residual risks named |
| [`ADR-707`](../adrs/ADR-00707-polars-duckdb-as-the-data-engine-not-pandas.md) | Addendum: split validated by the streaming regression |
| [`contracts/README.md`](../contracts/README.md) | `oneOf`+`discriminator` is the generated shape; `Decimal` must be string-constrained |
| [`skills-map.md`](../skills-map.md) | Version-pinned specifics replacing assumptions; LightGBM row now verified |
| [`roadmap.md`](../roadmap.md), [`closures/CR-00709-phase-0-specification-status.md`](../closures/CR-00709-phase-0-specification-status.md) | S1 re-scoped, gate counts updated |

## What Track A did not cover

Items deferred, with nothing blocking on them: interpret/EBM export shapes, SHAP cost at
scale, ZEN custom-node authoring, and the §8–§9 practice items in `skills-map.md`.

*(LightGBM's `init_score` was listed here as unverified; it became spike S3 and is now
closed — see F13. The assumption of symmetry was half wrong, which is why it was worth
running.)*
