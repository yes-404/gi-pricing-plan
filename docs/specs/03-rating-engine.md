# 03 — Rating Engine

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `RATE`
**Prerequisites:** [`00-overview.md`](00-overview.md) §2.3; [`02-modelling.md`](02-modelling.md) §3.9 (peril structures); [ADR-0004](../adr/0004-zen-engine-for-rating-execution.md).

---

## 1. Purpose & scope

### 1.1 In scope

Everything between "an approved Peril Structure exists" and "a live system gets a price":

1. **Rating Algorithm** — the declarative DAG that turns quote inputs into a final premium.
2. **Rate Tables** — the versioned, typed tables of factors, loadings, and constants that
   an actuary edits when making a rate change.
3. **Rating Versions** — immutable deployable bundles pinning the algorithm, every rate
   table, every referenced model, and every reference table version.
4. **Scoring** — real-time single-quote scoring (NFR-OVR-1) and batch portfolio re-rating.
5. **Trace** — the per-step record of a scoring call: the backbone of explainability,
   dispute resolution, and testing.
6. **Testing** — quote sandbox, regression test suites pinned to a rating version, and
   golden-quote checks that run at promotion time.
7. **Dislocation** — the distribution of premium change between two Rating Versions over a
   fixed portfolio.
8. **Deployment** — binding a Rating Version to an Environment, and rolling back.

### 1.2 Out of scope

| Not here | Where instead |
|---|---|
| Fitting models, deriving relativities statistically | `02-modelling.md` — this module consumes approved artifacts |
| Choosing *what* the rate change should be | `04-optimisation.md` — this module executes and measures it |
| Post-deployment drift and A/E monitoring | `05-monitoring.md` — this module emits the traces it consumes |
| Approval mechanics | `06-governance.md` |
| Quote & buy journeys, broker/aggregator integration, panel logic | Out of platform — Consumer Systems call our scoring API |
| Underwriting acceptance rules that decline a risk outright | Supported as a `constraint` step producing a `decline` outcome, but the *business* rules for who to decline are the insurer's content, not platform logic |

### 1.3 Hard rules

> **R1 — A `live` Rating Version is immutable and fully pinned.** Every model, rate table,
> and reference table version it uses is fixed at bundle time. Nothing resolves "latest" at
> scoring time. Ever.
>
> **R2 — Money is integer minor units or `Decimal` throughout** (FR-OVR-7). The engine
> refuses to construct a rating step whose output is a float-typed monetary value.
>
> **R3 — Every scoring call can produce a full Trace**, and a traced call and an untraced
> call return identical premiums. Tracing changes performance, never results.
>
> **R4 — A Rating Version cannot reach `approved` without dislocation evidence, a passing
> regression suite, and (where applicable) a GIPP check** (FR-RATE-40).

---

## 2. Concepts & glossary

Terms from `00-overview.md` §2.3 are used unchanged. Additional terms owned here:

| Term | Definition |
|---|---|
| **Rating Input** | A named, typed field the algorithm expects from the caller (`driver_age: int`, `postcode: string`). The input contract is part of the Rating Version and is versioned with it. |
| **Quote Context** | The complete input to one scoring call: rating inputs, a quote timestamp, an effective date, and a `purpose` (`new_business` \| `renewal` \| `mid_term_adjustment` \| `cancellation` \| `what_if`). `cancellation` was added 2026-08-18 with FR-RATE-63: OQ-RATE-4's answer mounts the refund sub-graph on `purpose`, and the value it keys on has to exist. |
| **Derived Value** | A named intermediate produced by a step and consumable by downstream steps. The DAG's edges are these name references, not hand-drawn arrows. |
| **Rate Table Version** | An immutable version of one rate table. Rate tables version independently of the algorithm so a pure rate change does not require touching structure. |
| **Bundle** | The serialised, self-contained artifact a Rating Version compiles to: algorithm + tables + model artifacts + reference slices + input contract. What gets deployed and cached. |
| **Compiled Bundle** | The bundle transformed into its execution form (a ZEN JDM graph plus loaded tables and boosters), cached in memory and in Redis, keyed by bundle content hash. |
| **Golden Quote** | A named quote context with an expected premium, stored with a Rating Version. Golden quotes must reproduce exactly before promotion. |
| **Regression Suite** | A collection of golden quotes plus property assertions (monotonicity, no-negative-premium, bounded relativity) run against a candidate Rating Version. |
| **Dislocation Run** | Batch re-rating of a fixed portfolio under two Rating Versions, producing the distribution of premium change. |
| **Premium Ladder** | The ordered decomposition of the final premium: risk premium → loaded premium → office premium → payable premium, with each loading named. The ladder is a first-class output, not a UI presentation choice. |

---

## 3. Functional requirements

### 3.1 Rating algorithms

| ID | Requirement |
|---|---|
| **FR-RATE-1** | A **Rating Algorithm** is a directed acyclic graph of Rating Steps. Cycles, orphaned steps, and references to undefined Derived Values are rejected at save time, not at scoring time. |
| **FR-RATE-2** | The algorithm declares a typed **input contract**: for each Rating Input, a name, type (`int`, `decimal`, `string`, `date`, `bool`, `enum`), nullability, valid range or enum domain, and a description. Scoring rejects a Quote Context violating the contract with a field-level error. |
| **FR-RATE-3** | The algorithm declares typed **outputs**, always including `payable_premium_minor` and the full Premium Ladder (§3.6), and may include additional named outputs (per-peril risk premium, decline reason, IPT amount). |
| **FR-RATE-4** | Every step has a stable `step_id`, a human label, an optional note, and declares exactly which Derived Values it consumes and which it produces. Renaming a label never changes a `step_id`. |
| **FR-RATE-5** | The graph is evaluated in topological order. Evaluation is deterministic: no wall-clock reads, no randomness, no external calls except pinned model invocations (FR-OVR-8). |
| **FR-RATE-6** | An algorithm can be composed from **sub-graphs** (reusable fragments, e.g. "no-claims-discount ladder", "IPT and fees") that are versioned artifacts referenced by the parent and inlined at bundle time. |
| **FR-RATE-63** | **A mid-term adjustment or cancellation is priced by the same Rating Algorithm for the *risk price*, with pro-rata, refund and charge logic in a separately-versioned sub-graph (FR-RATE-6) mounted only when `purpose ∈ {mid_term_adjustment, cancellation}`.** (OQ-RATE-4, decided 2026-08-18; **Phase 2**.) One risk price, because two algorithms that must agree about risk are two things that will disagree about risk — and the disagreement surfaces as a customer charged one price at renewal and another for the same cover mid-term. Separate policy-administration maths, because pro-rata, cancellation charges and refund rules are genuinely not new-business maths, and folding them in would put an MTA-only branch in every graph that never performs one. The mount is **declared on the Rating Version and version-pinned like any other sub-graph**, so "which refund rules were in force for this cancellation" is answered by the same pinning that answers it for a rate table. A version that mounts no such sub-graph refuses an MTA or cancellation quote rather than pricing it as new business — pricing it as new business is the failure this requirement exists to prevent, and it is silent. |
| **FR-RATE-7** | Algorithm edits are diffable: the UI and API expose a structural diff between two algorithm versions (steps added/removed/changed, tables re-pointed), which is attached to the approval request. |

### 3.2 Rating step types

Exactly seven step types exist. Adding an eighth requires a spec change and an ADR.

| Type | Purpose | Key fields |
|---|---|---|
| `input` | Surfaces a Rating Input as a Derived Value, applying declared coercion and defaulting | `input_name`, `on_missing` (`error` \| `default` \| `null`) |
| `lookup` | Resolves a value from a **Reference Table Version** as at a declared date | `reference_table_ref`, `key_expr[]`, `as_at`, `on_miss` (`error` \| `default`) |
| `table` | Looks up a **Rate Table Version** by one or more keys, with banding applied | `rate_table_ref`, `key_expr[]`, `on_miss`, `interpolation` (`none` \| `linear`) |
| `expression` | Computes a value from Derived Values using the restricted grammar (§3.5) | `expr`, `result_type` |
| `model_call` | Invokes a pinned Model or Peril Structure and yields its prediction(s) | `model_ref` \| `peril_structure_ref`, `feature_map`, `mode` (`exact` \| `approximation`) |
| `constraint` | Asserts a condition; on violation, clamps, declines, or errors | `condition`, `on_violation` (`clamp` \| `decline` \| `error`), `clamp_bounds`, `reason_code` |
| `output` | Marks a Derived Value as a declared output | `output_name`, `rounding` |

| ID | Requirement |
|---|---|
| **FR-RATE-8** | `table` steps resolve a Rate Table Version pinned by the Rating Version (R1). Key expressions may band a continuous input inline, but the banding is a stored artifact reference (`02` FR-MODEL-8), not an inline literal list. |
| **FR-RATE-9** | `lookup` steps evaluate reference data **as at a declared date** — normally the policy effective date, never "now" (`01` FR-DATA-31). The date source is explicit in the step. |
| **FR-RATE-10** | `model_call` steps declare `mode`: `exact` invokes the model itself; `approximation` uses the model's GLM approximation relativity tables (`02` OQ-MODEL-3). The choice is recorded on the Rating Version and surfaced at approval with the fidelity statement. |
| **FR-RATE-60** | **Both modes are supported, and the mode belongs to the Rating Version rather than to the step.** `RatingVersion.model_reference_mode` (§4.3) is the declaration; every `model_call` step's `mode` (FR-RATE-10) must equal it, checked at save time beside FR-RATE-13's type check, and a version whose steps disagree with it is refused with `MODEL_REFERENCE_MODE_INCONSISTENT`. This makes one identifier derived from the other rather than closing a capability: `rating-version.schema.json` enumerates `exact \| approximation` and nothing else, so a per-step mix was never expressible in the published contract. What an `approximation`-mode version must *prove* before it may deploy is **not** settled here — FR-MODEL-36's fidelity statement is descriptive and nothing gates on it (`02` OQ-MODEL-11). (`02` OQ-MODEL-3, decided 2026-08-17.) |
| **FR-RATE-61** | **An `approximation`-mode Rating Version cannot reach `approved` without a Dislocation Run (FR-RATE-46) whose baseline is the same version in `exact` mode, inside a workspace-declared premium-deviation threshold; FR-MODEL-36's fidelity statement is the cheap pre-check that runs first and is never itself the gate.** (`02` OQ-MODEL-11, decided 2026-08-18; **Phase 2**, with the deployment path it gates — it needs FR-RATE-46 built, and nothing in Phase 1 deploys a Rating Version.) FR-RATE-60 made both modes legal and left this open deliberately: a mode whose deployed prices are by construction not the model that was validated had no floor at all. The approval question is *how different are the prices we will charge*, and only a run over the actual book answers it — R² and coefficient agreement answer a question about the surrogate, and a surrogate can agree on coefficients and disagree on premium wherever exposure is thin. The prerequisite holds: spike S2 (OQ-RATE-2) measured `exact` at p99 1.09 ms, so the baseline costs a portfolio pass rather than a redesign. The threshold is the workspace's — a maximum absolute percentage deviation at a declared portfolio quantile, so that a long tail cannot be averaged away — and the Phase 2 slice that builds this decides where the setting lives; it is recorded on the approval beside FR-RATE-40's other evidence either way. A run that exceeds it is refused at submission with `EVIDENCE_INCOMPLETE` (re-raised from `06`) naming the quantile and the observed deviation. Ordering the fidelity statement first is what keeps the gate cheap: a plainly poor surrogate is refused before a portfolio run is spent on it. |
| **FR-RATE-11** | `constraint` steps are how business and regulatory limits are expressed: minimum premium, maximum year-on-year increase, decline rules, capping of a relativity. Each carries a `reason_code` that appears in the Trace and in any decline response. |
| **FR-RATE-12** | `output` steps declare rounding explicitly (mode and unit — e.g. `half_even` to the penny, `ceiling` to the pound). Rounding is never implicit and never happens twice. |
| **FR-RATE-13** | Every step declares its result type, and type compatibility is checked at save time. A monetary result must be `decimal` or `money_minor` (R2). |

### 3.3 Rate tables

| ID | Requirement |
|---|---|
| **FR-RATE-14** | A **Rate Table** is a typed table with declared key columns (each bound to a Factor or a banded input), a declared value column with a type and unit (`relativity`, `money_minor`, `percentage`, `count`), and an optional default row. |
| **FR-RATE-15** | Rate Table Versions are immutable. Editing produces a new version with a required change note. The previous version stays referenceable by existing Rating Versions. |
| **FR-RATE-16** | A rate table can be **seeded from a Model**: a GLM's relativity table (or a GBM's GLM-approximation relativities) is imported as a starting point, recording the source model reference. Subsequent manual edits are diffed against that seed, so "how far have we moved from the technical rate?" is always answerable. |
| **FR-RATE-17** | Rate table edits are diffable cell-by-cell against any prior version, with the diff showing absolute and relative change and the exposure weight behind each cell (from the portfolio dataset), so an actuary sees which edits matter. |
| **FR-RATE-62** | **A Rate Table Version's cells are stored as PostgreSQL rows up to a workspace-configurable cell count (default 250 000) and spill to a content-addressed parquet blob above it, under one contract either way.** (OQ-RATE-3, decided 2026-08-18; **Phase 2**, with the rate-table slice.) Rows are the default because they are what makes the rest of this section cheap: FR-RATE-17's cell diff is a SQL join, its exposure weighting is a join to the portfolio dataset, and the editor pages without a job. Blobs exist because a vehicle × area table reaches millions of cells, where rows stop being free — and the tail must not dictate the design for the many small tables that are the common case. **The threshold is a stored property of the version, not a runtime decision**: `storage` is `rows \| parquet` on `RateTableVersion` (§4.2), fixed when the version is written and immutable with it, so a reader never has to ask which form a past version took and a change of threshold cannot silently re-home existing versions. **What degrades above the threshold is stated rather than discovered:** FR-RATE-17's diff and its exposure weighting become a Job returning the same artifact, and the API answers 202 rather than 200 for them (`07` FR-PLAT-15's model). Everything a caller may *ask* is identical; only the latency and the status code differ. |
| **FR-RATE-18** | Bulk operations are first-class and recorded as such: uplift a whole table by a percentage, uplift a subset by key filter, floor/cap values, and rebase to a chosen base level. Each records its parameters, not just the resulting cells. |
| **FR-RATE-19** | Rate tables validate on save: complete coverage of the declared key domain (or an explicit default row), no null values, values within declared bounds, and no key duplication. |
| **FR-RATE-20** | Rate tables can be exported to and imported from CSV/XLSX for offline work, with a strict round-trip check on import: keys, types, and completeness must match, and the import is presented as a diff for confirmation before it creates a version. |
| **FR-RATE-21** | A rate table declares whether it is **rateable** (part of the price) or **diagnostic** (present for analysis). Only rateable tables can be referenced by a step feeding the premium ladder. |

### 3.4 Rating versions and bundles

| ID | Requirement |
|---|---|
| **FR-RATE-22** | A **Rating Version** pins: one Rating Algorithm version, an exact Rate Table Version per referenced table, an exact Model/Peril Structure version per `model_call`, an exact Reference Table Version per `lookup`, and the input contract. Nothing is unpinned. |
| **FR-RATE-23** | Lifecycle is `draft → review → approved → live → retired`. Only `approved` versions can be deployed; `live` is a property of a Deployment, and the same Rating Version can be `live` in `uat` and not in `prod`. |
| **FR-RATE-24** | A Rating Version compiles to a self-contained **Bundle** with a content hash. The bundle is sufficient to score with no database access (NFR-RATE-3) and is what gets cached and distributed. |
| **FR-RATE-25** | Bundle compilation validates the whole structure: DAG acyclic and fully connected, all references resolvable and at a sufficient maturity (FR-OVR-14), all types compatible, all constraints satisfiable, no `control`-intent factor in a rateable path (`02` FR-MODEL-3), no unapproved custom objective transitively reachable. |
| **FR-RATE-26** | A Rating Version declares its `effective_from` business date and optional `effective_to`, independent of when it is deployed. Scoring uses the version bound to the environment; the effective date is metadata for governance and monitoring, not a runtime selector — unless the deployment explicitly uses date-based routing (FR-RATE-31). |
| **FR-RATE-27** | Rating Versions carry a required **change summary**: what changed versus the previous version, why, and expected impact. It is generated as a draft from the structural and rate-table diffs and edited by the actuary. |

### 3.5 Expression grammar in rating

| ID | Requirement |
|---|---|
| **FR-RATE-28** | `expression` steps use the same restricted grammar as `02` §4.6, extended with decimal-safe operators and these rating-specific functions: `round(x, mode, dp)`, `band(x, banding_ref)`, `coalesce(a, b)`, `date_diff_years(a, b)`, `min`, `max`, `clip`. No other functions. **Availability is verified against the engine at compile time (FR-RATE-59)** — S1 found the two-argument `min`/`max` forms are not valid ZEN calls, so this list states intent, not a guarantee. |
| **FR-RATE-29** | Arithmetic on monetary values is evaluated in `Decimal` with an explicit context (28 significant digits, `ROUND_HALF_EVEN`), never in binary floating point (R2). Mixing a monetary value and a float-typed value in one expression is a compile-time error. |
| **FR-RATE-30** | Expression steps cannot reference anything outside their declared inputs — no globals, no environment, no time-of-day. `now()` does not exist; a quote timestamp is an input. |

### 3.6 Premium ladder

| ID | Requirement |
|---|---|
| **FR-RATE-31** | Every Rating Version produces a **Premium Ladder** as a structured output, with each rung named, typed, and traceable: `risk_premium` (from the Peril Structure) → `+ expense loadings` → `+ commission` → `+ profit loading` → `office_premium` → `± optimisation adjustment` → `± constraints (min premium, capping)` → `+ IPT and fees` → `payable_premium`. |
| **FR-RATE-32** | Each ladder rung records both the value and the operation that produced it (multiplicative factor or additive amount), so the ladder reconciles exactly: applying every recorded operation to `risk_premium` reproduces `payable_premium` to the penny. This reconciliation is asserted at scoring time in `dev`/`uat` and sampled in `prod`. |
| **FR-RATE-33** | Per-peril risk premium components are available as outputs, since monitoring (`05`) and reinsurance analysis both need them. |

### 3.7 Scoring

| ID | Requirement |
|---|---|
| **FR-RATE-34** | **Real-time scoring**: `POST /api/v1/score` evaluates one Quote Context against the Rating Version currently live in the target environment, returning the ladder, outputs, and (optionally) a Trace. Target p99 < 50 ms server-side (NFR-OVR-1). |
| **FR-RATE-35** | Scoring accepts an explicit `rating_version_ref` for what-if and testing; in `prod` this is permitted only for `approved` versions and is recorded as a `what_if` purpose, never as a quotable price. |
| **FR-RATE-64** | **The platform prices the *annual* payable premium, and instalment loading is an optional final ladder rung (`instalment_loading`) read from a rate table. APR calculation and schedule generation are downstream and are not built here.** (OQ-RATE-6, decided 2026-08-18; **Phase 2**.) The loading exists because it changes the price the customer actually compares, and without it `04-optimisation.md`'s demand model is fitted against a price nobody was offered. It stops at a loading because APR and schedule generation carry a consumer-credit regulatory surface — disclosure, the regulated APR formula, and rules about what may be charged — that belongs to a billing system with its own compliance obligations, and taking it on here would make every rating release a consumer-credit release. **The boundary is drawn where the maths stops being rating maths**: the platform outputs an annual premium and, where the rung is mounted, the loaded annual equivalent; it never emits a payment schedule, an APR figure, or a credit agreement term. A Quote Context asking for one is refused rather than answered approximately, because an APR that is nearly right is a compliance defect and not a rounding one. |
| **FR-RATE-36** | **Batch scoring**: `POST /api/v1/score/batch` re-rates a Dataset Version against one or more Rating Versions as a Job, writing results to a new content-addressed parquet output with the quote key, ladder, and selected outputs per row. |
| **FR-RATE-37** | Batch scoring is chunked, resumable, and progress-reporting, and uses the identical compiled bundle and code path as real-time scoring — never a separate "batch implementation" that could diverge. |
| **FR-RATE-38** | Scoring errors are typed and per-quote: contract violation, reference miss, table miss, constraint decline, model failure. A batch run reports counts and samples per error type and does not abort on individual failures unless the failure rate exceeds a declared threshold. |
| **FR-RATE-39** | A `decline` outcome from a `constraint` step is a **successful** scoring response with `outcome: declined` and reason codes — not an HTTP error. |

### 3.8 Trace, testing, and promotion evidence

| ID | Requirement |
|---|---|
| **FR-RATE-40** | A Rating Version cannot reach `approved` without: a passing Regression Suite, a Dislocation Run against the current live version over an agreed portfolio, a change summary (FR-RATE-27), and — where the insurer has enabled it — a passing GIPP check (`04-optimisation.md`) (R4). |
| **FR-RATE-41** | **Trace**: on request, scoring returns every step's id, label, consumed values, produced value, matched table row key, and elapsed time, plus the bundle hash and rating version reference. Traces are the same structure in real-time and batch. |
| **FR-RATE-42** | In production, traces are **sampled** (default 1 %, configurable, plus 100 % of declines and errors) and persisted for ≥ 13 months (NFR-OVR-6), feeding `05-monitoring.md`. |
| **FR-RATE-43** | A **Golden Quote** stores a Quote Context and the expected outputs. Promotion re-scores every golden quote and refuses promotion on any mismatch beyond a declared tolerance (default: exact for money). |
| **FR-RATE-44** | A **Regression Suite** may also contain property assertions evaluated over generated quote contexts: premium is positive, premium is monotone in a declared input, no output is null, the ladder reconciles (FR-RATE-32), and premium is bounded by declared limits. Generation uses hypothesis-style sampling over the input contract with a persisted seed. |
| **FR-RATE-45** | The **Quote Sandbox** lets an actuary score an arbitrary quote against any accessible Rating Version and see the full trace inline, alongside the same quote scored against a comparison version with a step-by-step difference. |

### 3.9 Dislocation

| ID | Requirement |
|---|---|
| **FR-RATE-46** | A **Dislocation Run** re-rates a fixed portfolio Dataset Version under a baseline and a candidate Rating Version and reports: the distribution of premium change (absolute and percentage), average change overall and by declared segment, the exposure/policy count in each change band, movers beyond configurable thresholds with drill-down to individual quotes, and total portfolio premium change. |
| **FR-RATE-47** | Dislocation results are sliceable by any Factor available on the portfolio dataset, and by the ladder rung at which the change originated — answering "which part of the change caused this?", not merely "how much did it change?". |
| **FR-RATE-48** | Dislocation output is a persisted, citable artifact referenced by the approval request, not a transient screen. |
| **FR-RATE-49** | Where the candidate and baseline differ in more than one respect (new model *and* rate table edits), dislocation supports **attribution**: re-rating with each change applied in isolation and cumulatively, so the change is decomposed into its causes. |

### 3.10 Deployment

| ID | Requirement |
|---|---|
| **FR-RATE-50** | A **Deployment** binds an `approved` Rating Version to an Environment, recording who, when, why, and the bundle hash. Only a Deployer can deploy; `prod` deployment additionally requires the approval record to be complete (`06-governance.md`). |
| **FR-RATE-51** | Deployment is atomic per environment: a scoring call sees either the old or the new bundle, never a mix. Bundles are pre-warmed into cache before the switch. |
| **FR-RATE-52** | **Rollback** to any previously-deployed Rating Version in that environment is a single audited operation with the same guarantees, and does not require re-approval. |
| **FR-RATE-53** | Optional **date-based routing** allows an environment to hold multiple deployed versions selected by the quote's effective date, for pre-loading a future rate change. Overlapping date ranges are rejected at deployment time. |
| **FR-RATE-54** | Optional **shadow scoring**: a proportion of live traffic is additionally scored against a candidate version, with results recorded but never returned to the caller — the pre-deployment safety net feeding `05-monitoring.md`. |
| **FR-RATE-55** | Every deployment, rollback, and routing change emits an Audit Event and a notification to a configured channel. |

### 3.11 Numeric precision at the engine boundary

Spike **S1** (2026-08-14, `zen-engine` 0.53.0) tested this end to end. The result splits
cleanly, and it **corrects an earlier conclusion of ours**
([`research`](../research/track-a-findings.md) F14).

**Inside the engine, arithmetic is exact.** `0.1 + 0.2 == 0.3` evaluates `true`;
`1.005 * 100` gives `100.5`; `1.1 * 3 == 3.3` is `true`. ADR-0004 stands.

**At the Python binding, there is no decimal type at all.** A Python `Decimal` is
*rejected* (`TypeError: unsupported type Decimal`), and every value returned is a Python
`float` — `1/3` comes back as `0.33333333333333337`. Exactness cannot be carried across the
boundary in either direction.

After F1 we recorded that the integer-minor-units workaround was "not required for
correctness". **That was wrong** — right about the engine, wrong about the system. The
engine is exact; the binding is not, and the binding is what the platform talks to.

| ID | Requirement |
|---|---|
| **FR-RATE-56** | **Money crosses the engine boundary only as integer minor units.** The binding accepts no decimal type and returns `float`, so exactness cannot survive the crossing as a fractional value. Integers up to 2^53 are exactly representable in `float64` (≈ £90 trillion in pence), which is why the integer form is safe where the fractional form is not. Fractional quantities — relativities, loadings, factors — may be *held* in rate tables and applied *inside* the engine, but any value returning to Python for further arithmetic is an integer minor unit or a string. A startup self-check asserts the round-trip; failing it prevents the service starting. |
| **FR-RATE-57** | **Division is the guarded operation, not transcendentals.** S1 found `log` and `sqrt` do not exist in the ZEN expression language at all (they fail to parse), so the earlier requirement guarded operations that cannot be called. The real hazard is **division by zero, which returns `null` and does not raise**: `1/0`, `0/0` and `premium/0` all evaluate to `null` silently. The null then raises a `vmError` at the point it is *used*, reporting the multiply rather than the division that caused it. Every division in a rateable path carries an explicit zero guard, bundle compilation (FR-RATE-25) rejects an unguarded one, and **a `null` reaching an `output` step is a hard error** — otherwise a null premium can be emitted. |
| **FR-RATE-58** | Bundle compilation checks that no rate table value, constant, or intermediate requires a decimal scale beyond `rust_decimal`'s limit of 28, and fails with a named error rather than allowing a silent loss of precision deep in a ladder. Confirmed relevant by S1: `(1/3) * 3 == 1` evaluates `false`, so repeated division loses exactness inside the engine too. |
| **FR-RATE-59** | The `expression` step's function vocabulary (FR-RATE-28) is validated **against the engine actually in use**, not against this specification's list. S1 found `abs`, `round`, `floor`, `ceil` and `sum` available, but the two-argument `min(a, b)` / `max(a, b)` forms rejected as invalid function calls. Bundle compilation resolves every function name against the engine's real vocabulary and fails on a mismatch, so a graph cannot reference a function that exists only in our documentation. |

---

## 4. Data contracts

### 4.1 `RatingAlgorithm`

```json
{
  "slug": "motor-gb",
  "version": 14,
  "input_contract": [
    {"name": "driver_age", "type": "int", "nullable": false, "min": 17, "max": 99,
     "description": "Age of main driver at policy inception"},
    {"name": "postcode_outcode", "type": "string", "nullable": false, "pattern": "^[A-Z]{1,2}[0-9][A-Z0-9]?$"},
    {"name": "effective_date", "type": "date", "nullable": false},
    {"name": "purpose", "type": "enum",
     "domain": ["new_business", "renewal", "mid_term_adjustment", "cancellation", "what_if"]}
  ],
  "outputs": [
    {"name": "payable_premium_minor", "type": "money_minor", "required": true},
    {"name": "premium_ladder", "type": "ladder", "required": true},
    {"name": "peril_risk_premium", "type": "map<string, money_minor>", "required": false},
    {"name": "decline_reasons", "type": "array<string>", "required": false}
  ],
  "steps": [
    {"step_id": "s_input_age", "type": "input", "label": "Driver age",
     "input_name": "driver_age", "on_missing": "error", "produces": "driver_age"},
    {"step_id": "s_area", "type": "lookup", "label": "Rating area from outcode",
     "reference_table_ref": "reference_table:ons-postcode-directory@7",
     "key_expr": ["postcode_outcode"], "as_at": "effective_date",
     "on_miss": "error", "produces": "rating_area"},
    {"step_id": "s_rp", "type": "model_call", "label": "Technical risk premium",
     "peril_structure_ref": "peril_structure:motor-gb-2026h2@2", "mode": "exact",
     "feature_map": {"driver_age": "driver_age", "rating_area": "rating_area"},
     "produces": ["risk_premium_minor", "peril_risk_premium"]},
    {"step_id": "s_expense", "type": "table", "label": "Expense loading",
     "rate_table_ref": "rate_table:motor-expense@3", "key_expr": ["distribution_channel"],
     "on_miss": "default", "produces": "expense_factor"},
    {"step_id": "s_office", "type": "expression", "label": "Office premium",
     "expr": "risk_premium_minor * expense_factor * commission_factor * profit_factor",
     "result_type": "money_minor", "produces": "office_premium_minor"},
    {"step_id": "s_minprem", "type": "constraint", "label": "Minimum premium",
     "condition": "office_premium_minor >= min_premium_minor",
     "on_violation": "clamp", "clamp_bounds": {"min": "min_premium_minor"},
     "reason_code": "MIN_PREMIUM_APPLIED", "produces": "office_premium_minor"},
    {"step_id": "s_out", "type": "output", "label": "Payable premium",
     "output_name": "payable_premium_minor",
     "rounding": {"mode": "half_even", "dp": 0}, "consumes": "payable_premium_pre_round"}
  ],
  "sub_graphs": [{"ref": "sub_graph:ncd-ladder@4", "mount_point": "s_ncd"}]
}
```

**Invariants** — DAG acyclic; every `consumes` name is `produced` by exactly one upstream
step; every declared output has an `output` step; no step is unreachable from an `input`
and unreferenced by an `output` (FR-RATE-1).

### 4.2 `RateTable` / `RateTableVersion`

```json
{
  "slug": "motor-driver-age-relativity",
  "version": 6,
  "rateable": true,
  "storage": "rows",
  "keys": [{"name": "driver_age_band", "type": "string", "banding_ref": "banding:driver-age-actuarial-v2@2"}],
  "value": {"name": "relativity", "type": "relativity", "min": 0.2, "max": 5.0},
  "default_row": null,
  "rows": [
    {"driver_age_band": "17-20", "relativity": "1.8400"},
    {"driver_age_band": "21-24", "relativity": "1.4100"},
    {"driver_age_band": "25-29", "relativity": "1.1200"}
  ],
  "seeded_from": {"model_ref": "model:motor-ad-frequency@7", "seeded_at": "2026-07-02T10:00:00Z"},
  "change_note": "Softened 17-20 from 1.92 to 1.84 following competitor review; see OPT run 2026-07-11.",
  "diff_vs_previous": {"changed_cells": 3, "max_abs_change_pct": 4.2,
                       "exposure_weighted_mean_change_pct": 0.8},
  "diff_vs_seed": {"changed_cells": 7, "exposure_weighted_mean_change_pct": -2.1}
}
```

Values are stored as decimal strings, never JSON floats (R2).

> **`storage` added 2026-08-18 with FR-RATE-62** (OQ-RATE-3). `rows` or `parquet`, decided
> against the workspace's cell-count threshold when the version is written and **immutable
> with the version**, so a reader never has to ask which form a past version took and raising
> the threshold cannot silently re-home versions already written. Above the threshold `rows`
> is absent from this document and the cells are addressed by a `BlobRef`; every other field
> here, and every question a caller may ask, is unchanged — what changes is that FR-RATE-17's
> diff and its exposure weighting answer **202 with a Job** rather than 200.

### 4.3 `RatingVersion`

```json
{
  "slug": "motor-gb",
  "version": 27,
  "status": "draft | review | approved | live | retired",
  "algorithm_ref": "rating_algorithm:motor-gb@14",
  "pins": {
    "rate_tables": ["rate_table:motor-driver-age-relativity@6", "rate_table:motor-expense@3"],
    "models": ["peril_structure:motor-gb-2026h2@2"],
    "reference_tables": ["reference_table:ons-postcode-directory@7", "reference_table:abi-vehicle-group@12"],
    "custom_objectives": ["custom_objective:capped-gamma@3"]
  },
  "model_reference_mode": "exact",
  "effective_from": "2026-10-01", "effective_to": null,
  "bundle": {"content_hash": "sha256:…", "bytes": 84_112_904, "compiled_at": "2026-08-14T12:00:00Z"},
  "change_summary": "AD frequency model refit on 2026H1 data; driver-age relativities softened at young ages; minimum premium raised to £280.",
  "evidence": {
    "regression_suite_run_id": "uuid",
    "dislocation_run_id": "uuid",
    "gipp_check_id": "uuid",
    "structural_diff_blob": "blob:sha256:…"
  },
  "approval_request_id": "uuid"
}
```

**Invariants** — `status ≥ approved` ⟹ every `evidence` field required by the workspace
policy is present and passing (R4, FR-RATE-40); every pin resolves to an artifact whose
status is `approved` or better (FR-OVR-14); `bundle.content_hash` is reproducible from the
pins; every `model_call` step's `mode` equals `model_reference_mode`
(FR-RATE-60).

> *(Scoped 2026-08-27, W7-3 — OD1.)* Phase 1b builds the **minimal subset** of this shape:
> `slug`, `version`, `status` (`draft → review → approved`), `workspace_id`,
> `dataset_version_id`, a single pinned `model:{slug}@{version}` reference, `created_at`,
> `created_by`, `updated_at`. Compile, score, rate tables, the `pins`/`evidence`/`bundle`
> blocks, `model_reference_mode`, and deployment stay Phase 2 (FR-PLAT-67). The
> `RatingVersion` model in `model-schema` carries only the Phase 1b subset; a Phase 2
> build widens the shape with the full contract.

### 4.4 `QuoteContext` and `ScoringResult`

```json
{
  "quote_id": "external-ref-or-uuid",
  "purpose": "new_business",
  "quoted_at": "2026-10-05T14:22:31Z",
  "effective_date": "2026-10-20",
  "inputs": {"driver_age": 34, "postcode_outcode": "SW1A", "vehicle_group": 22,
             "ncd_years": 5, "annual_mileage": 9000, "distribution_channel": "aggregator"},
  "options": {"trace": true, "rating_version_ref": null}
}
```

```json
{
  "outcome": "quoted | declined | error",
  "rating_version_ref": "rating_version:motor-gb@27",
  "bundle_hash": "sha256:…",
  "premium_ladder": [
    {"rung": "risk_premium", "value_minor": 24_150, "operation": null,
     "components": {"AD": 9_820, "TP_BI": 11_400, "TP_PD": 2_180, "WINDSCREEN": 750}},
    {"rung": "expense_loading", "value_minor": 27_780, "operation": {"kind": "multiply", "factor": "1.1500"}},
    {"rung": "commission", "value_minor": 31_420, "operation": {"kind": "multiply", "factor": "1.1310"}},
    {"rung": "profit_loading", "value_minor": 33_620, "operation": {"kind": "multiply", "factor": "1.0700"}},
    {"rung": "office_premium", "value_minor": 33_620, "operation": null},
    {"rung": "optimisation_adjustment", "value_minor": 32_280, "operation": {"kind": "multiply", "factor": "0.9601"}},
    {"rung": "constraints", "value_minor": 32_280, "operation": {"kind": "none", "applied": []}},
    {"rung": "ipt_and_fees", "value_minor": 36_120, "operation": {"kind": "add", "amount_minor": 3_840}},
    {"rung": "payable_premium", "value_minor": 36_120, "operation": {"kind": "round", "mode": "half_even", "dp": 0}}
  ],
  "outputs": {"payable_premium_minor": 36_120, "peril_risk_premium": {"AD": 9_820, "…": "…"}},
  "decline_reasons": [],
  "trace": {"…see 4.5…"},
  "timing_ms": {"total": 7.4, "model_call": 3.1, "table_lookups": 0.9, "expressions": 0.4}
}
```

### 4.5 `Trace`

```json
{
  "rating_version_ref": "rating_version:motor-gb@27",
  "bundle_hash": "sha256:…",
  "quote_id": "…",
  "steps": [
    {"step_id": "s_area", "type": "lookup", "label": "Rating area from outcode",
     "consumed": {"postcode_outcode": "SW1A", "as_at": "2026-10-20"},
     "produced": {"rating_area": "A3"},
     "matched": {"reference_table": "reference_table:ons-postcode-directory@7",
                 "key": {"postcode_outcode": "SW1A"}, "effective_from": "2026-04-01"},
     "elapsed_us": 41},
    {"step_id": "s_minprem", "type": "constraint", "label": "Minimum premium",
     "consumed": {"office_premium_minor": 26_400, "min_premium_minor": 28_000},
     "produced": {"office_premium_minor": 28_000},
     "violation": {"applied": "clamp", "reason_code": "MIN_PREMIUM_APPLIED"},
     "elapsed_us": 3}
  ],
  "ladder_reconciled": true
}
```

### 4.6 `DislocationRun`

```json
{
  "baseline_ref": "rating_version:motor-gb@26",
  "candidate_ref": "rating_version:motor-gb@27",
  "portfolio_dataset_version_id": "uuid",
  "policy_count": 1_284_902, "exposure_years": "1240118.4",
  "totals": {"baseline_premium_minor": 41_882_100_00, "candidate_premium_minor": 42_698_300_00,
             "change_pct": 1.95},
  "distribution": [
    {"band": "< -10%", "policies": 41_204, "exposure_share": 0.031, "mean_change_pct": -14.2},
    {"band": "-10% to -5%", "policies": 118_402, "exposure_share": 0.092, "mean_change_pct": -7.1},
    {"band": "-5% to 0%", "policies": 402_118, "exposure_share": 0.314, "mean_change_pct": -2.2},
    {"band": "0% to +5%", "policies": 511_402, "exposure_share": 0.398, "mean_change_pct": 2.6},
    {"band": "+5% to +10%", "policies": 174_882, "exposure_share": 0.136, "mean_change_pct": 7.0},
    {"band": "> +10%", "policies": 36_894, "exposure_share": 0.029, "mean_change_pct": 14.8}
  ],
  "by_segment": [{"factor": "driver_age_band", "level": "17-20",
                  "policies": 22_104, "mean_change_pct": -6.4, "exposure_share": 0.017}],
  "attribution": [
    {"change": "peril_structure:motor-gb-2026h2@1 → @2", "mean_change_pct": 1.42},
    {"change": "rate_table:motor-driver-age-relativity@5 → @6", "mean_change_pct": -0.31},
    {"change": "min_premium 26000 → 28000", "mean_change_pct": 0.84}
  ],
  "largest_movers_blob": "blob:sha256:…"
}
```

### 4.7 `RegressionSuite` and `GoldenQuote`

```json
{
  "slug": "motor-gb-core",
  "golden_quotes": [
    {"name": "young-driver-london", "context": {"…QuoteContext…"},
     "expected": {"payable_premium_minor": 112_480, "outcome": "quoted"},
     "tolerance": {"money_minor": 0}}
  ],
  "properties": [
    {"name": "premium_positive", "assertion": "payable_premium_minor > 0"},
    {"name": "monotone_in_age", "assertion": "monotone_decreasing(payable_premium_minor, driver_age, 25, 70)"},
    {"name": "ladder_reconciles", "assertion": "ladder_reconciled == true"},
    {"name": "bounded_relativity", "assertion": "payable_premium_minor <= 20 * risk_premium_minor"}
  ],
  "generation": {"cases": 5000, "seed": 20260814, "strategy": "input_contract_sampling"}
}
```

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/rating-algorithms` | Create/version an algorithm (validated on save, FR-RATE-1) |
| `GET` | `/api/v1/rating-algorithms/{slug}@{version}/diff?against=` | Structural diff (FR-RATE-7) |
| `POST` | `/api/v1/rate-tables/{slug}/versions` | New Rate Table Version with change note |
| `POST` | `/api/v1/rate-tables/{slug}/seed-from-model` | Seed from a model's relativities (FR-RATE-16) |
| `POST` | `/api/v1/rate-tables/{slug}/bulk-operation` | Uplift / floor / cap / rebase, recorded as parameters (FR-RATE-18) |
| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against=` | **200** Cell-level diff with exposure weights (FR-RATE-17); **202** with a Job where either version is `storage: parquet` (FR-RATE-62) |
| `POST` | `/api/v1/rate-tables/{slug}/import` | Import CSV/XLSX → returns a diff for confirmation (FR-RATE-20) |
| `POST` | `/api/v1/rating-versions` | Create a draft Rating Version with pins |
| `POST` | `/api/v1/rating-versions/{id}/compile` | **202** Compile + validate the bundle (FR-RATE-25) |
| `POST` | `/api/v1/rating-versions/{id}/submit` | Submit for approval; evidence completeness checked (FR-RATE-40) |
| `POST` | `/api/v1/score` | Real-time single quote (FR-RATE-34) |
| `POST` | `/api/v1/score/batch` | **202** Batch re-rate → Job (FR-RATE-36) |
| `POST` | `/api/v1/score/compare` | Score one quote against two versions with a step-level diff (FR-RATE-45) |
| `POST` | `/api/v1/rating-versions/{id}/regression-runs` | **202** Run the regression suite (FR-RATE-43/44) |
| `POST` | `/api/v1/dislocation-runs` | **202** Baseline vs candidate over a portfolio (FR-RATE-46) |
| `GET` | `/api/v1/dislocation-runs/{id}` | Dislocation artifact |
| `POST` | `/api/v1/environments/{env}/deployments` | Deploy an approved version (FR-RATE-50) |
| `POST` | `/api/v1/environments/{env}/deployments/rollback` | Roll back (FR-RATE-52) |
| `PUT` | `/api/v1/environments/{env}/shadow` | Configure shadow scoring (FR-RATE-54) |
| `GET` | `/api/v1/traces?rating_version=&from=&to=` | Sampled production traces (FR-RATE-42) |

**Error codes owned by this module:** `RATING_GRAPH_CYCLIC`, `RATING_GRAPH_UNRESOLVED_REF`,
`RATING_TYPE_MISMATCH`, `MONETARY_FLOAT_REFUSED`, `EXPRESSION_NON_DETERMINISTIC`,
`EXPRESSION_UNGUARDED_DIVISION`, `EXPRESSION_SCALE_OVERFLOW`, `EXPRESSION_INVALID_VOCABULARY`,
`RATING_VERSION_UNPINNED`, `INPUT_CONTRACT_VIOLATION`,
`REFERENCE_LOOKUP_MISS`, `RATE_TABLE_MISS`, `RATE_TABLE_INCOMPLETE`,
`RATE_TABLE_KEY_DUPLICATE`, `CONTROL_FACTOR_IN_RATEABLE_PATH`, `PIN_NOT_APPROVED`,
`BUNDLE_COMPILE_FAILED`, `EVIDENCE_INCOMPLETE` (re-raised from `06`), `GOLDEN_QUOTE_MISMATCH`,
`PROPERTY_ASSERTION_FAILED`, `DEPLOY_REQUIRES_APPROVAL`, `DEPLOY_DATE_RANGE_OVERLAP`,
`LADDER_RECONCILIATION_FAILED`, `MODEL_REFERENCE_MODE_INCONSISTENT`.

### 5.2 `pricing-core` interfaces

```python
# pricing_core/rating/compile.py
def validate_algorithm(algo: RatingAlgorithm) -> list[ValidationIssue]
def compile_bundle(version: RatingVersion, resolver: ArtifactResolver) -> Bundle
def to_jdm(algo: RatingAlgorithm) -> JdmGraph          # ADR-0004 translation layer
def bundle_hash(graph: JdmGraph, pins: Pins) -> str    # corrected 2026-08-27 (F-W9-3-2)

# pricing_core/rating/score.py
def score_one(bundle: CompiledBundle, ctx: QuoteContext, *,
              trace: bool = False) -> ScoringResult
def score_batch(bundle: CompiledBundle, frame: pl.LazyFrame, *,
                chunk_rows: int = 100_000,
                progress: ProgressCallback | None = None) -> pl.LazyFrame

# pricing_core/rating/analysis.py
def dislocate(baseline: CompiledBundle, candidate: CompiledBundle,
              portfolio: pl.LazyFrame, spec: DislocationSpec) -> DislocationRun
def attribute(changes: Sequence[BundleDelta], portfolio: pl.LazyFrame) -> list[Attribution]

# pricing_core/rating/testing.py
def run_regression(bundle: CompiledBundle, suite: RegressionSuite,
                   *, seed: int) -> RegressionRun
def generate_contexts(contract: InputContract, n: int, seed: int) -> list[QuoteContext]

# pricing_core/rating/money.py — the decimal discipline (R2)
def to_minor(value: Decimal, currency: str) -> int
def apply_factor(amount_minor: int, factor: Decimal, rounding: Rounding) -> int
```

> *(Corrected 2026-08-27, F-W9-3-2 — the decision-maker ruled the spec was wrong.)* The
> content hash is `bundle_hash(graph, pins)`, never `bundle_hash(bundle)`: the Bundle
> carries `compiled_at`, and hashing a timestamp would make the hash unreproducible. Per
> DP1 and FR-RATE-24, the hash covers the graph and the pinned artifact references and is
> reproducible from the pins; `compiled_at` is metadata and is excluded.

`score_one` and `score_batch` share the identical step evaluator (FR-RATE-37);
`score_batch` is a vectorised driver over the same compiled graph, not a second engine.

### 5.3 Frontend views

| View | Route | Contents |
|---|---|---|
| Rating version list | `/rating` | Versions by status, live-in-environment badges, effective dates |
| **DAG designer** | `/rating/:slug/v/:version/design` | Vue Flow canvas with typed nodes per step type, live validation (cycles, unresolved refs, type mismatches) shown on the node, node inspector panel, sub-graph mounting, structural diff overlay against another version |
| Rate table editor | `/rating/:slug/v/:version/tables/:tableSlug` | TanStack Table grid, inline editing with decimal input, diff-vs-previous and diff-vs-seed heat shading, exposure weight column, bulk-operation dialog, CSV import diff confirmation |
| Quote sandbox | `/rating/:slug/v/:version/sandbox` | Quote form generated from the input contract, ladder waterfall chart, trace timeline with per-step values, side-by-side compare against another version |
| Regression suite | `/rating/:slug/v/:version/tests` | Golden quotes with pass/fail and actual-vs-expected, property assertion results with counterexamples |
| Dislocation | `/rating/:slug/v/:version/dislocation` | Change distribution histogram, segment breakdown grid, attribution waterfall, largest-movers drill-down to individual traces |
| Deployments | `/rating/environments` | Per-environment live version, deployment history, rollback control, shadow configuration |

**Interaction requirement:** the DAG designer must make an invalid graph *visibly* invalid
before save — a step referencing an undefined value shows the error on the node, not in a
save-time toast. The premium ladder waterfall is the single most useful screen in the
module and must be reachable in one click from any traced quote.

---

## 6. Workflows

| Step | Actor | Action |
|---|---|---|
| 1 | Pricing Actuary | Seeds rate tables from the approved Peril Structure's models (FR-RATE-16) |
| 2 | Pricing Actuary | Edits the algorithm in the DAG designer; validation runs on every change |
| 3 | Pricing Actuary | Edits rate tables; diffs vs previous and vs technical seed stay visible |
| 4 | Frontend → Backend | `POST /rating-versions` + `POST /{id}/compile` → bundle hash |
| 5 | Analyst | Runs the regression suite; fixes any golden-quote or property failure |
| 6 | Analyst | Runs dislocation vs the current live version, with attribution (FR-RATE-49) |
| 7 | Pricing Actuary | Runs a GIPP check where enabled (`04-optimisation.md`) |
| 8 | Pricing Actuary | Writes the change summary (drafted from diffs) and submits |
| 9 | Approver | Reviews structural diff, rate diffs, dislocation, tests, GIPP → approves |
| 10 | Deployer | Deploys to `uat`, shadow-scores, then deploys to `prod` (FR-RATE-50/54) |
| 11 | Backend | Pre-warms the bundle, switches atomically, emits Audit Event + notification |

Full journeys: [`wf-02-model-to-rating-version.md`](../workflows/wf-02-model-to-rating-version.md),
[`wf-03-rate-change-impact.md`](../workflows/wf-03-rate-change-impact.md),
[`wf-04-deploy-and-monitor.md`](../workflows/wf-04-deploy-and-monitor.md).

---

## 7. Cross-module dependencies

### 7.1 Consumes

| From | What |
|---|---|
| `02-modelling` | `approved` Models and Peril Structures; GLM approximation relativity tables for seeding and for `approximation` mode; bandings referenced by table keys |
| `01-data-management` | Reference Table Versions for `lookup` steps; portfolio Dataset Versions for dislocation and batch scoring |
| `06-governance` | Approval workflow, RBAC (Deployer role), audit sink |
| `07-platform` | Environments, jobs, bundle cache (Redis), blob storage, API gateway and rate limiting |

**Not a dependency:** `04-optimisation` *writes into* this module — it materialises
proposals as Rate Table Versions and its run id is stored on a Rating Version as an opaque
evidence reference. This module never calls optimisation code, so the direction is
OPT → RATE and DEP-1 is respected.

### 7.2 Provides

| To | What |
|---|---|
| Consumer Systems | The scoring API — the platform's externally-facing product surface |
| `04-optimisation` | Batch scoring of candidate price surfaces; the current live price as the optimisation baseline |
| `05-monitoring` | Sampled production traces, deployment events, premium ladders, and per-peril risk premium components |
| `06-governance` | Structural diffs, dislocation artifacts, regression results, and deployment history for generated documentation |

### 7.3 Contract notes

- The engine never re-implements model prediction; `model_call` delegates to `pricing-core`
  `predict_*` (`02` §7.3), so a diagnostic prediction and a quoted premium cannot diverge.
- Reference lookups use the same effective-dating semantics as `01` FR-DATA-31; there is
  one implementation, in `pricing-core`.
- `05-monitoring` consumes traces as they are; this module does not pre-aggregate for it.

---

## 8. Tech dependencies

| Component | Used for | Notes for `skills-map.md` |
|---|---|---|
| **GoRules ZEN Engine** | DAG execution substrate (ADR-0004) | JDM graph format, decision tables, `Variable::Number` is `rust_decimal` (exact decimal — verified); the `arbitrary_precision` serde feature and where it is *not* default; `maths-nopanic` returning 0 on invalid input; custom nodes for rate-table lookup and `model_call`; Python binding overhead at 200 rps; native trace output |
| **Python `decimal`** | All monetary arithmetic (R2, FR-RATE-29) | Contexts, `ROUND_HALF_EVEN`, integer minor units, avoiding float contamination through JSON serialisation |
| **Polars** | Batch scoring driver, dislocation aggregation, rate table storage in memory | Chunked lazy evaluation; joining portfolio rows to rate tables at scale |
| **DuckDB** | Dislocation slicing and segment aggregation over scored parquet | Window functions for change-band distributions |
| **Redis** | Compiled bundle cache keyed by content hash; hot-path lookup | Cache warming before an atomic deployment switch (FR-RATE-51) |
| **FastAPI** | The scoring endpoint on the latency path | Async request handling, response model overhead, avoiding Pydantic re-validation on the hot path |
| **XGBoost / LightGBM** | `model_call` in `exact` mode | Booster load time, single-row prediction latency, thread pinning to avoid contention at 200 rps |
| **hypothesis** | Property assertion generation (FR-RATE-44) | Strategies derived from an input contract; shrinking counterexamples an actuary can read |
| **Vue Flow (frontend)** | The DAG designer | Custom node types per step type, edge validation, layout, undo/redo, mapping canvas state to the `RatingAlgorithm` contract |
| **TanStack Table (frontend)** | Rate table editor | Virtualised editable grids, decimal-safe cell input, diff shading |
| **ECharts (frontend)** | Ladder waterfall, dislocation histogram, attribution waterfall | Waterfall chart construction; large-histogram rendering |
| **OpenTelemetry** | Per-step timing on the latency path | Low-overhead spans; sampling so tracing does not become the bottleneck |

New skills this spec adds to `skills-map.md`: ZEN JDM custom nodes and trace output;
decimal money discipline across a JSON boundary; Redis cache warming for atomic switchover;
single-row GBM inference latency tuning; hypothesis strategies from a declarative contract.

---

## 9. Non-functional requirements

| ID | Requirement |
|---|---|
| **NFR-RATE-1** | Real-time scoring p99 < 50 ms server-side at 200 rps per replica for a ~200-step motor structure with one `exact` GBM call (NFR-OVR-1). Without a GBM call, p99 < 15 ms. |
| **NFR-RATE-2** | Tracing adds ≤ 20 % to scoring latency and never changes the result (R3). |
| **NFR-RATE-3** | A compiled bundle scores with **zero** database or network access; everything it needs is inside it (FR-RATE-24). |
| **NFR-RATE-4** | Bundle compilation for a large motor structure completes in < 60 s; bundle size stays under 500 MB including booster artifacts. |
| **NFR-RATE-5** | Batch scoring ≥ 1 M risks/hour per worker (NFR-OVR-2), linear in workers. |
| **NFR-RATE-6** | Deployment switchover is atomic with no dropped or mixed-bundle requests, and completes within 30 s of the deploy command including cache warming. |
| **NFR-RATE-7** | Determinism: identical bundle hash + quote context ⟹ identical premium, byte-for-byte, across processes, machines, and platform versions (FR-OVR-8). |
| **NFR-RATE-8** | Money exactness: no rounding is applied more than once; the ladder reconciles to the penny in 100 % of scored quotes (FR-RATE-32), asserted continuously in non-prod and sampled in prod. |
| **NFR-RATE-9** | Availability: the scoring endpoint targets 99.95 % monthly, degrading to the last-known-good cached bundle if metadata storage is unavailable. |
| **NFR-RATE-10** | Audit: algorithm edits, rate table versions, bulk operations, compilations, approvals, deployments, rollbacks, and routing changes all emit Audit Events with before/after state. |
| **NFR-RATE-11** | Security: the scoring API authenticates per Consumer System with scoped credentials and per-client rate limits; quote inputs are never logged in full outside sampled traces, which are access-controlled. |
| **NFR-RATE-12** | Trace storage: 1 % sampling of 50 M annual quotes stays under 200 GB/year with the sampled-trace schema. |
| **NFR-RATE-14** | GBM `model_call` steps execute with **`nthread=1` per request**. Measured (S2): single-threading beats all-cores at the tail — p99 1.09 ms vs 1.48 ms, worst case 4.5 ms vs 19.9 ms — because thread-pool spin-up dominates a single-row prediction. Parallelism belongs across concurrent requests, not inside one. |
| **NFR-RATE-13** | The scoring endpoint does **not** apply `response_model` validation to its response. Pydantic validation costs roughly 1 ms per request — 2 % of the 50 ms budget before any pricing work — and the response path otherwise runs three to five transformations. `ScoringResult` is constructed by `pricing-core` and is already trusted, so it is serialised directly with a C-speed encoder (`ORJSONResponse`). Inbound `QuoteContext` **is** validated: untrusted input must be checked, trusted output need not be. *(Amended 2026-08-27, W8 — the premise's ~1 ms figure was not reproduced. A realistic `ScoringResult` (premium, 20 rate steps, 60 factors, metadata) validates and serialises at p99 0.070 ms, 0.14 % of the 50 ms budget, on the verification machine; `docs/research/w8-spike-resolution.md`. The measured shape is the one the premise describes, so the figure was an over-estimate, not a different context. The design rule is unchanged: validate inbound, never outbound; encode with `ORJSONResponse`.)* |

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-RATE-1** | ~~Does the ZEN Engine preserve exact decimal semantics for money?~~ **Resolved 2026-08-14** — it represents numbers as `rust_decimal::Decimal`, so engine arithmetic is exact and ADR-0004 stands. The risk moved to the boundaries and is now specified as FR-RATE-56/57/58; the S1 spike is re-scoped, not cancelled. See [`research`](../research/track-a-findings.md) F1. |
| **OQ-RATE-2** | ~~Is `model_call` in `exact` mode viable inside the 50 ms p99 budget?~~ **RESOLVED 2026-08-14 by spike S2 — comfortably yes.** A 500-tree × 60-feature booster scores a single row at **p99 1.09 ms** including `DMatrix` construction (0.33 ms predict-only) — about 2 % of the budget. `nthread=1` beat all-cores at the tail (p99 1.09 vs 1.48 ms; max 4.5 vs 19.9 ms), so per-request single-threading is correct. **OQ-MODEL-3 is therefore a genuine design choice, not one forced by latency.** |
| **OQ-RATE-3** | ~~Should rate tables live in PostgreSQL as rows or as content-addressed parquet blobs?~~ **DECIDED 2026-08-18: rows to a configurable cell count, spilling to parquet above it under one contract — FR-RATE-62**, with `storage` recorded on the version and the diff degrading to a Job above the threshold. |
| **OQ-RATE-4** | ~~How do mid-term adjustments and refunds work — a `purpose` on the same algorithm, or a genuinely separate calculation path?~~ **DECIDED 2026-08-18: the same algorithm for the risk price, with pro-rata/refund/charge logic in a separately-versioned sub-graph mounted on `purpose` — FR-RATE-63.** §2's `purpose` gained `cancellation` in the same edit, because the answer keys on a value that did not exist. |
| ~~**OQ-RATE-5**~~ | ~~Do we support multi-product bundling (motor + home in one quote with a bundle discount) in Phase 2, or is each product a separate Rating Version with bundling left to the Consumer System?~~ **Deferred to Phase 4**: Phase 2 ships single-product Rating Versions and a Consumer System bundling two quotes is a supported pattern — the bundle discount is then unpriced and unmonitored, and cross-product pricing follows the optimisation work that needs the same joint demand modelling. **DECIDED 2026-08-26: deferral confirmed — Phase 4; Consumer System bundling is the supported pattern** |
| **OQ-RATE-6** | ~~Should the platform own instalment/APR calculation, or is that a downstream billing concern?~~ **DECIDED 2026-08-18: price the annual premium, offer `instalment_loading` as a final ladder rung, and leave APR and schedules downstream — FR-RATE-64.** Enough for `04`'s demand model; not enough to make a rating release a consumer-credit release. |
