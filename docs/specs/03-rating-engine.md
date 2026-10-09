# 03 — Rating Engine

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `RATE`
**Prerequisites:** [`00-overview.md`](00-overview.md) §2.3; [`02-modelling.md`](02-modelling.md) §3.9 (peril structures); [ADR-706](../adrs/ADR-00706-gorules-zen-engine-executes-rating-dags.md).

---

## 1. Purpose & scope

### 1.1 In scope

Everything between "an approved Peril Structure exists" and "a live system gets a price":

1. **Rating Algorithm** — the declarative DAG that turns quote inputs into a final premium.
2. **Rate Tables** — the versioned, typed tables of factors, loadings, and constants that
   an actuary edits when making a rate change.
3. **Rating Versions** — immutable deployable bundles pinning the algorithm, every rate
   table, every referenced model, and every reference table version.
4. **Scoring** — real-time single-quote scoring (NFR-454) and batch portfolio re-rating.
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
> **R2 — Money is integer minor units or `Decimal` throughout** (FR-10). The engine
> refuses to construct a rating step whose output is a float-typed monetary value.
>
> **R3 — Every scoring call can produce a full Trace**, and a traced call and an untraced
> call return identical premiums. Tracing changes performance, never results.
>
> **R4 — A Rating Version cannot reach `approved` without dislocation evidence, a passing
> regression suite, and (where applicable) a GIPP check** (FR-257).

---

## 2. Concepts & glossary

Terms from `00-overview.md` §2.3 are used unchanged. Additional terms owned here:

| Term | Definition |
|---|---|
| **Rating Input** | A named, typed field the algorithm expects from the caller (`driver_age: int`, `postcode: string`). The input contract is part of the Rating Version and is versioned with it. |
| **Quote Context** | The complete input to one scoring call: rating inputs, a quote timestamp, an effective date, and a `purpose` (`new_business` \| `renewal` \| `mid_term_adjustment` \| `cancellation` \| `what_if`). `cancellation` was added 2026-08-18 with FR-218: OQ-617's answer mounts the refund sub-graph on `purpose`, and the value it keys on has to exist. |
| **Derived Value** | A named intermediate produced by a step and consumable by downstream steps. The DAG's edges are these name references, not hand-drawn arrows. |
| **Rate Table Version** | An immutable version of one rate table. Rate tables version independently of the algorithm so a pure rate change does not require touching structure. |
| **Bundle** | The serialised, self-contained artifact a Rating Version compiles to: algorithm + tables + model artifacts + reference slices + input contract. What gets deployed and cached. |
| **Compiled Bundle** | The bundle transformed into its execution form (a ZEN JDM graph plus loaded tables and boosters), held per worker process once pre-warmed (FR-243). Not itself cached in Redis or content-hash-keyed — only `Bundle` is (FR-239, FR-268). *(Clarified 2026-08-29, WK-671 Slice 2: that denial is of the **distribution** role. A `CompiledBundle` is never what Redis holds and is never addressed by content hash across processes. A per-worker in-process slot may still index the `CompiledBundle` it holds by the `content_hash` of the `Bundle` it was loaded from — which is what FR-243's exposure of that hash exists to make possible, and without which FR-268's "either the old or the new bundle, never a mix" is unverifiable at runtime. Ruled in `docs/rulings/RL-00882-d4-slice-2-builds-a-per-worker-in-process-slot-and-it-is-the-first-cache-of-its-kind-in-this-backend.md` RL-882.)* |
| **Golden Quote** | A named quote context with an expected premium, stored with a Rating Version. Golden quotes must reproduce exactly before promotion. *(Amended 2026-09-28, `PL-1189`: stored in a versioned Regression Suite bound to a Rating Algorithm by `algorithm_slug`, not inside a Rating Version, which is immutable after `draft`; the Rating Version's evidence pins the suite version it was checked against.)* |
| **Regression Suite** | A collection of golden quotes plus property assertions (monotonicity, no-negative-premium, bounded relativity) run against a candidate Rating Version. |
| **Dislocation Run** | Batch re-rating of a fixed portfolio under two Rating Versions, producing the distribution of premium change. |
| **Premium Ladder** | The ordered decomposition of the final premium: risk premium → loaded premium → office premium → payable premium, with each loading named. The ladder is a first-class output, not a UI presentation choice. |

---

## 3. Functional requirements

### 3.1 Rating algorithms

| ID | Requirement |
|---|---|
| **FR-212** | A **Rating Algorithm** is a directed acyclic graph of Rating Steps. Cycles, orphaned steps, and references to undefined Derived Values are rejected at save time, not at scoring time. *(Amended 2026-10-05, FD-1425.)* The order in which an algorithm lists its steps carries no meaning: each consumed name is wired to its producer through the graph, over a stable topological order of the dependency edges. A misordered list is not refused at save. |
| **FR-213** | The algorithm declares a typed **input contract**: for each Rating Input, a name, type (`int`, `decimal`, `string`, `date`, `bool`, `enum`), nullability, valid range or enum domain, and a description. Scoring rejects a Quote Context violating the contract with a field-level error. *(Amended 2026-10-05, FD-1425.)* A Quote Context input whose name is a value some step produces, and is not itself a declared input, is a contract violation, refused with a field-level error naming the key: a quote input never stands in for a produced value. |
| **FR-214** | The algorithm declares typed **outputs**, always including `payable_premium_minor` and the full Premium Ladder (§3.6), and may include additional named outputs (per-peril risk premium, decline reason, IPT amount). *(Amended 2026-09-30, `RL-1343` (`OQ-1334`): a declared output of type `decimal` is served as a JSON string on every scoring path (`/score`, both results of `/score/compare`, and the batch column `outputs_json`), never as a JSON number. Its value is the engine's exact decimal for the output step's source, read across the binding as a string (FR-273) and never from a float. It is rounded once with the output step's declared rounding (FR-226) and written positionally with exactly `dp` digits after the point, no exponent, and no sign on a zero. `/score` and `outputs_json` carry the same string. A `decimal` output may carry money (FR-227), and this rule holds whether or not it does. `ScoringResult` refuses a float anywhere in `outputs`, and the contract admits no non-integer number there. Delivered by WK-1178 after WK-674 Slice 3 merges; until then `/score` serves the engine's float, and neither path applies the declared rounding (`FD-1333`).)* |
| **FR-215** | Every step has a stable `step_id`, a human label, an optional note, and declares exactly which Derived Values it consumes and which it produces. Renaming a label never changes a `step_id`. |
| **FR-216** | The graph is evaluated in topological order. Evaluation is deterministic: no wall-clock reads, no randomness, no external calls except pinned model invocations (FR-11). |
| **FR-217** | An algorithm can be composed from **sub-graphs** (reusable fragments, e.g. "no-claims-discount ladder", "IPT and fees") that are versioned artifacts referenced by the parent and inlined at bundle time. |
| **FR-218** | **A mid-term adjustment or cancellation is priced by the same Rating Algorithm for the *risk price*, with pro-rata, refund and charge logic in a separately-versioned sub-graph (FR-217) mounted only when `purpose ∈ {mid_term_adjustment, cancellation}`.** (OQ-617, decided 2026-08-18; **Phase 2**.) One risk price, because two algorithms that must agree about risk are two things that will disagree about risk — and the disagreement surfaces as a customer charged one price at renewal and another for the same cover mid-term. Separate policy-administration maths, because pro-rata, cancellation charges and refund rules are genuinely not new-business maths, and folding them in would put an MTA-only branch in every graph that never performs one. The mount is **declared on the Rating Version and version-pinned like any other sub-graph**, so "which refund rules were in force for this cancellation" is answered by the same pinning that answers it for a rate table. A version that mounts no such sub-graph refuses an MTA or cancellation quote rather than pricing it as new business — pricing it as new business is the failure this requirement exists to prevent, and it is silent. *(Amended 2026-09-29, an interim rule, `RL-1242`, on the maintainer's decision of 2026-09-29 16:34:39 BST: while FR-217's bundle-time inlining is not built, declaring and pinning the mount is necessary but not sufficient, because no sub-graph can be applied to a quote. Until the inlining is built, no Rating Version can price a `mid_term_adjustment` or `cancellation` quote, and every such quote must be refused with `INPUT_CONTRACT_VIOLATION`, never priced as new business. The Work that builds FR-217's inlining retires this rule. The gap is recorded in the finding titled "CR-838 marks FR-217 delivered, but its pin and bundle-time inlining are not built".)* *(Amended 2026-09-30, `RL-1344` (`PL-1254` DP-2): where the mount is declared. "Declared on the Rating Version" means declared by the algorithm version the Rating Version pins (`algorithm_ref`), as an ordinary sub-graph mount (FR-217) in the algorithm's `sub_graphs`, with an optional `purposes` selector. Its exact sub-graph version is pinned in the Rating Version's `pins` like every other mount; there is no second declaration site and no purpose-specific pin. A mount without `purposes` is mounted for every purpose. A mount with `purposes` lists one or both of `mid_term_adjustment` and `cancellation`, and no other value: a selector that could mount a fragment for `new_business` or `renewal` would price the two differently inside one algorithm, against this requirement's one risk price and the ENBP comparison of `04` FR-294. The algorithm satisfies FR-212 for each purpose's mounted graph. An MTA or cancellation quote is refused unless the bundle inlines a mount whose `purposes` includes its purpose; the interim rule above stands until WK-1250 Slice 3 delivers this.)* |
| **FR-219** | Algorithm edits are diffable: the UI and API expose a structural diff between two algorithm versions (steps added/removed/changed, tables re-pointed), which is attached to the approval request. |
| **FR-1530** | **A Rating Algorithm version is readable by its `slug@version`.** *(Added 2026-10-08, `RL-1475`, `PL-1286` DP-4.)* `GET /api/v1/rating-algorithms/{slug}@{version}` returns the saved `RatingAlgorithm` (§4.1) exactly as it passed save-time validation (FR-212). The DAG designer loads a Rating Version's algorithm through the version's `algorithm_ref` (FR-237), and edits it into a new algorithm version, never in place. The read requires `rating:read` and answers **404** `NOT_FOUND` for an unknown version or another workspace's. |

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
| **FR-220** | `table` steps resolve a Rate Table Version pinned by the Rating Version (R1). Key expressions may band a continuous input inline, but the banding is a stored artifact reference (`02` FR-97), not an inline literal list. |
| **FR-221** | `lookup` steps evaluate reference data **as at a declared date** — normally the policy effective date, never "now" (`01` FR-71). The date source is explicit in the step. *(Amended 2026-10-08, `RL-1446`, FD-1420.)* **`as_at` names `effective_date` — the quote's stamped date — or a declared `date` input, and nothing else.** Anything else is refused when the algorithm is saved, and again when its bundle is compiled: a declared input of another type with `RATING_TYPE_MISMATCH`, and an undeclared name with `RATING_GRAPH_UNRESOLVED_REF`. **The value read is a calendar date, `YYYY-MM-DD`.** A datetime, an offset, or a malformed value is refused per quote with `INPUT_CONTRACT_VIOLATION`, never treated as a miss. **A row is in force when `effective_from ≤ as_at < effective_to`**: `01` FR-69's half-open interval, where an absent `effective_to` is open-ended. A key with no row in force is a reference miss (FR-255), resolved by the step's `on_miss`. Overlapping rows cannot reach a bundle: FR-69 refuses them when the version is loaded (`REFERENCE_INTERVAL_OVERLAP`). |
| **FR-222** | `model_call` steps declare `mode`: `exact` invokes the model itself; `approximation` uses the model's GLM approximation relativity tables (`02` OQ-575). The choice is recorded on the Rating Version and surfaced at approval with the fidelity statement. |
| **FR-223** | **Both modes are supported, and the mode belongs to the Rating Version rather than to the step.** `RatingVersion.model_reference_mode` (§4.3) is the declaration; every `model_call` step's `mode` (FR-222) must equal it, checked at save time beside FR-227's type check, and a version whose steps disagree with it is refused with `MODEL_REFERENCE_MODE_INCONSISTENT`. This makes one identifier derived from the other rather than closing a capability: `rating-version.schema.json` enumerates `exact \| approximation` and nothing else, so a per-step mix was never expressible in the published contract. What an `approximation`-mode version must *prove* before it may deploy is **not** settled here — FR-136's fidelity statement is descriptive and nothing gates on it (`02` OQ-576). (`02` OQ-575, decided 2026-08-17.) **Amended 2026-10-05 (`RL-1438`): the check runs where the version and its algorithm meet, not at save time.** "Checked at save time" named a point where the Rating Version is not available: an algorithm is saved without one, and one algorithm version may be pinned by versions of either mode. The check runs at bundle compilation (FR-240), always, where a mismatch fails the `rating.compile` Job with `MODEL_REFERENCE_MODE_INCONSISTENT`, naming the first mismatching `model_call` step and both modes; and at any route that writes a Rating Version's `algorithm_ref` or `model_reference_mode`, which refuses a mismatching write with **422** `MODEL_REFERENCE_MODE_INCONSISTENT`. Algorithm save and `POST /api/v1/rating-algorithms/validate` do not check it. The spec was wrong about the check point; the code, which checked at compilation but answered `BUNDLE_COMPILE_FAILED`, was wrong about the code. |
| **FR-224** | **An `approximation`-mode Rating Version cannot reach `approved` without a Dislocation Run (FR-263) whose baseline is the same version in `exact` mode, inside a workspace-declared premium-deviation threshold; FR-136's fidelity statement is the cheap pre-check that runs first and is never itself the gate.** (`02` OQ-576, decided 2026-08-18; **Phase 2**, with the deployment path it gates — it needs FR-263 built, and nothing in Phase 1 deploys a Rating Version.) FR-223 made both modes legal and left this open deliberately: a mode whose deployed prices are by construction not the model that was validated had no floor at all. The approval question is *how different are the prices we will charge*, and only a run over the actual book answers it — R² and coefficient agreement answer a question about the surrogate, and a surrogate can agree on coefficients and disagree on premium wherever exposure is thin. The prerequisite holds: spike S2 (OQ-615) measured `exact` at p99 1.09 ms (WK-668 re-measured 1.626 ms — still comfortably inside budget; see OQ-615), so the baseline costs a portfolio pass rather than a redesign. The threshold is the workspace's — a maximum absolute percentage deviation at a declared portfolio quantile, so that a long tail cannot be averaged away — and the Phase 2 slice that builds this decides where the setting lives; it is recorded on the approval beside FR-257's other evidence either way. A run that exceeds it is refused at submission with `EVIDENCE_INCOMPLETE` (re-raised from `06`) naming the quantile and the observed deviation. Ordering the fidelity statement first is what keeps the gate cheap: a plainly poor surrogate is refused before a portfolio run is spent on it. |
| **FR-225** | `constraint` steps are how business and regulatory limits are expressed: minimum premium, maximum year-on-year increase, decline rules, capping of a relativity. Each carries a `reason_code` that appears in the Trace and in any decline response. |
| **FR-226** | `output` steps declare rounding explicitly (mode and unit — e.g. `half_even` to the penny, `ceiling` to the pound). Rounding is never implicit and never happens twice. |
| **FR-227** | Every step declares its result type, and type compatibility is checked at save time. A monetary result must be `decimal` or `money_minor` (R2). |

### 3.3 Rate tables

| ID | Requirement |
|---|---|
| **FR-228** | A **Rate Table** is a typed table with declared key columns (each bound to a Factor or a banded input), a declared value column with a type and unit (`relativity`, `money_minor`, `percentage`, `count`), and an optional default row. **Clarified 2026-10-03 (`RL-1361`): the binding is a declared field.** "Bound to a Factor" is `factor_ref`, a pinned `factor:<slug>@<version>`. "A banded input" is `banding_ref`, a pinned Banding with no Factor. A key carries at most one of them, and `model-schema` refuses a key that carries both. A key with neither is joined by its own name. A version written before `factor_ref` existed stays unbound (FR-4). |
| **FR-229** | Rate Table Versions are immutable. Editing produces a new version with a required change note. The previous version stays referenceable by existing Rating Versions. |
| **FR-230** | A rate table can be **seeded from a Model**: a GLM's relativity table (or a GBM's GLM-approximation relativities) is imported as a starting point, recording the source model reference. Subsequent manual edits are diffed against that seed, so "how far have we moved from the technical rate?" is always answerable. **Clarified 2026-10-03 (`RL-1361` section A): a seed request names one Factor.** The request's required `factor` is the Factor's slug, a key of the model's relativities. The seeded table holds that Factor's relativities under one key, bound by `factor_ref` to the Factor version the model pins, so a model with K categorical factors seeds K tables. A continuous factor has no relativity table and is refused. A lineage holds one Factor: a re-seed that names another Factor's slug is refused, and a newer version of the same Factor is accepted. A hand-authored table may still have several keys (FR-228).*(Amended 2026-10-08, `RL-1470`, FD-1422.)* A seed request naming a `control`-intent Factor is refused with **422** `CONTROL_FACTOR_IN_RATEABLE_PATH` (`02` FR-88): a `control` factor is fitted to absorb variance and is never rated on, so no rate table is seeded from it. |
| **FR-231** | Rate table edits are diffable cell-by-cell against any prior version, with the diff showing absolute and relative change and the exposure weight behind each cell (from the portfolio dataset), so an actuary sees which edits matter. **Clarified 2026-10-05 (`RL-1361`): how the exposure weight is computed.** The caller names a `validated` portfolio Dataset Version, and there is no default. Each portfolio row maps to at most one cell of the current version through each key's binding (FR-228): a `factor_ref` key through that Factor's resolution, a `banding_ref` key through that Banding, and an unbound key by the column of its own name, compared in the key's declared type. A cell's weight is Σ exposure over the rows that map to it, and it weights the aggregate `exposure_weighted_mean_change_pct`. A cell whose Σ is 0 carries no weight. The diff reports the portfolio's total exposure and the exposure that mapped to a cell. A portfolio whose rows map to no cell is refused, and so is a null or negative exposure. This clarification does not make the diff show the weight per cell: that is FD-1358. **Clarified 2026-10-05 (`RL-1418`): the weight behind each cell (FD-1358).** Each changed cell's baseline and current value, absolute and relative change and exposure weight are served by `GET /api/v1/rate-tables/{slug}@{version}/diff/cells` (§5.1), one cursor page at a time in §4.2's key order. Every changed cell is served: a page bounds one response, not the cells. `RateTableDiff`, on the diff route, stays the aggregate summary of the same cells. |
| **FR-232** | **A Rate Table Version's cells are stored as PostgreSQL rows up to a workspace-configurable cell count (default 250 000) and spill to a content-addressed parquet blob above it, under one contract either way.** (OQ-616, decided 2026-08-18; **Phase 2**, with the rate-table slice.) Rows are the default because they are what makes the rest of this section cheap: FR-231's cell diff is a SQL join, its exposure weighting is a join to the portfolio dataset, and the editor pages without a job. Blobs exist because a vehicle × area table reaches millions of cells, where rows stop being free — and the tail must not dictate the design for the many small tables that are the common case. **The threshold is a stored property of the version, not a runtime decision**: `storage` is `rows \| parquet` on `RateTableVersion` (§4.2), fixed when the version is written and immutable with it, so a reader never has to ask which form a past version took and a change of threshold cannot silently re-home existing versions. **What degrades above the threshold is stated rather than discovered:** FR-231's diff and its exposure weighting become a Job returning the same artifact, and the API answers 202 rather than 200 for them (`07` FR-411's model). Everything a caller may *ask* is identical; only the latency and the status code differ. **Amended 2026-10-05 (`RL-1442`, FD-1439): the first request for a diff may answer 202, on either storage.** "The editor pages without a job" holds for every request to FR-231's diff and to its per-cell diff (`GET …/diff` and `GET …/diff/cells`, §5.1) after the first request for a key, the two versions and the `portfolio`: that first request may answer **202** with one `rate_table.diff_cells` Job, whatever `storage` either version has, because a weighted diff at the threshold exceeds `07` §1.3 R1's 2 s; later requests are read from the key's stored artifact and answer **200** without a Job. |
| **FR-233** | Bulk operations are first-class and recorded as such: uplift a whole table by a percentage, uplift a subset by key filter, floor/cap values, and rebase to a chosen base level. Each records its parameters, not just the resulting cells. |
| **FR-234** | Rate tables validate on save: complete coverage of the declared key domain (or an explicit default row), no null values, values within declared bounds, and no key duplication. |
| **FR-235** | Rate tables can be exported to and imported from CSV/XLSX for offline work, with a strict round-trip check on import: keys, types, and completeness must match, and the import is presented as a diff for confirmation before it creates a version. |
| **FR-236** | A rate table declares whether it is **rateable** (part of the price) or **diagnostic** (present for analysis). Only rateable tables can be referenced by a step feeding the premium ladder. |
| **FR-1186** | **A Rate Table Version has no approval lifecycle and no status.** It is governed through the Rating Version that pins it (FR-237). That Rating Version's submission carries the rate table diffs (`06` §3.3), and its approval is the one approval of the change. FR-229's change note is still required on every version. `compile_bundle`'s maturity gate does not apply to a `rate_table` pin, so RL-856's exemption is the permanent rule, no longer a provisional one. **Revisit trigger:** a Rate Table Version pinned by more than one Rating Version in practice. That is OQ-620's deciding test, which cannot be measured in Phase 2. (OQ-620, decided 2026-09-28 by delegation, option (b); `RL-1184` E8.) |

### 3.4 Rating versions and bundles

| ID | Requirement |
|---|---|
| **FR-237** | A **Rating Version** pins: one Rating Algorithm version, an exact Rate Table Version per referenced table, an exact Model/Peril Structure version per `model_call`, an exact Reference Table Version per `lookup`, and the input contract. Nothing is unpinned. *(Amended 2026-10-05, RL-1428, FD-1421.)* The algorithm version and the pins are declared when the Rating Version is created (`POST /api/v1/rating-versions`, §5.1) and are checked at compile (FR-240). Where `algorithm_ref` resolves in the workspace, the create route also checks FR-223's model-reference-mode consistency and refuses a mismatch with **422** `MODEL_REFERENCE_MODE_INCONSISTENT`, as RL 9758 (working id) item 2 binds every route that writes a version's `algorithm_ref` or `model_reference_mode`. An `algorithm_ref` that does not resolve is stored and left to compile, which refuses it. |
| **FR-238** | Lifecycle is `draft → review → approved → live → retired`. Only `approved` versions can be deployed; `live` is a property of a Deployment, and the same Rating Version can be `live` in `uat` and not in `prod`. |
| **FR-239** | A Rating Version compiles to a self-contained **Bundle** with a content hash. The bundle is sufficient to score with no database access (NFR-491) and is what gets cached and distributed. *(Amended 2026-10-04, RL-1379, on FD-1393: a compile runs only while the Rating Version is `draft`. A compile requested for a version in any other status — `review`, `approved`, `live`, `retired` — is refused with `RATING_VERSION_IMMUTABLE` (409), synchronously by the route when the status is already non-draft and by the `rating.compile` Job, which ends `failed` with that code, when the status changed after submission; the version's Bundle summary and blob key are unchanged. A version in `review` is recompiled only after the decision path returns it to `draft` (`06` FR-355), which resubmits it through FR-257's gate; an `approved` or later version is never recompiled, and a new compiled output is a new version (`00` FR-4).)* |
| **FR-240** | Bundle compilation validates the whole structure: DAG acyclic and fully connected, all references resolvable and at a sufficient maturity (FR-20), all types compatible, all constraints satisfiable, no `control`-intent factor in a rateable path (`02` FR-88), no unapproved custom objective transitively reachable. *(Amended 2026-09-30, `RL-1329`: saving an algorithm and compiling a bundle also refuse, with `LADDER_CLAMP_UNPLACEABLE` (422), a `clamp` constraint that the Premium Ladder cannot place; the check is one of the algorithm checks that `validate_algorithm` runs at both points. That is a clamp whose produced name is the source of a ladder rung other than the last rung present before `constraints` (FR-247), or whose produced name is a rung's source but differs from the name it consumes. The ladder records a binding clamp on the `constraints` rung (FR-248), so a clamp anywhere else would break the ladder's chain on every quote on which it binds. The message names the step and the rung.)**(Amended 2026-10-08, `RL-1470`, FD-1469, FD-1422 and FD 9639.)* **"Transitively reachable" means through a pinned model**: a pinned model whose spec names a custom objective (a GBM's `spec.objective` with `kind: custom`) reaches that objective, and compilation refuses it with `PIN_NOT_APPROVED` unless it is approved or better, exactly as if it were pinned. The message names the model and the objective. A `deprecated` objective is refused, as a new specification may not select one (`02` OQ-609). The bound is one hop. **Known gap:** a peril structure's models are not reached, because a peril structure cannot be resolved at compile; FD-1456 owns that gap, and this clause reaches them when it is fixed. Custom evaluation metrics are not objectives and do not reach a price, so they are outside this clause. **A `control`-intent factor is in a rateable path when a pinned rate table has a key bound by `factor_ref` to it**, whatever the table's `rateable` flag; compilation refuses it with `CONTROL_FACTOR_IN_RATEABLE_PATH` (422), naming the table, the key and the Factor. **A `control`-intent factor is also in a rateable path when a pinned model scored by a `model_call` was fitted on it**: compilation refuses the version with `CONTROL_FACTOR_IN_RATEABLE_PATH` (422), naming the model, the feature and the Factor, because scoring applies every fitted feature's effect and `02` FR-88 lets Rating Versions use only `risk` factors. Scoring at a declared reference level for a `control` factor is an open question (FD 9639), not a permission. |
| **FR-241** | A Rating Version declares its `effective_from` business date and optional `effective_to`, independent of when it is deployed. Scoring uses the version bound to the environment; the effective date is metadata for governance and monitoring, not a runtime selector — unless the deployment explicitly uses date-based routing (FR-247). |
| **FR-242** | Rating Versions carry a required **change summary**: what changed versus the previous version, why, and expected impact. It is generated as a draft from the structural and rate-table diffs and edited by the actuary. |
| **FR-243** | **`CompiledBundle` is a distinct runtime type, produced from a `Bundle` by a hydration step, never a rename of `Bundle` and never itself serialised.** It holds whatever the ZEN engine binding needs to execute the graph and any GBM boosters loaded from `resolved_payloads` into live objects. `Bundle` stays the plain, serialisable, content-hashed form that is compiled once, distributed, and cached in Redis (FR-239, FR-268); `CompiledBundle` is what pre-warming (FR-268, NFR-494) produces, held per worker process, and what `score_one`/`score_batch`/`dislocate`/`run_regression` actually take (§5.2). (Ruled 2026-08-29, `docs/rulings/RL-00867-compiledbundle-is-spec-only-bundle-is-the-only-thing-that-exists-and-they-are-not-the-same-type.md` RL-867.) |
| **FR-1531** | **A Rating Version is addressed by its `slug@version`; its `id` is a handle, not an address.** *(Added 2026-10-08, `RL-1473`, `PL-1286` DP-5.)* The pair `(slug, version)` is unique within a workspace, and every §5.3 view route names a Rating Version by that pair: in `/rating/:slug/v/:version/…`, `:slug` and `:version` are the Rating Version's own `slug` and `version` (§4.3), never its algorithm's, whose version is read from `algorithm_ref`. `GET /api/v1/rating-versions/{slug}@{version}` reads the version by the pair. Its response carries the `id` that the §5.1 routes keyed by `{id}` take, so a view resolves the pair once and then acts by `id`. Both reads, by pair and by `id`, require `rating:read` and answer **404** `NOT_FOUND` for another workspace's version exactly as for one that does not exist. `00` §5.6's routes are unchanged. |

### 3.5 Expression grammar in rating

| ID | Requirement |
|---|---|
| **FR-244** | `expression` steps use the same restricted grammar as `02` §4.6, extended with decimal-safe operators and these rating-specific functions: `round(x, mode, dp)`, `band(x, banding_ref)`, `coalesce(a, b)`, `date_diff_years(a, b)`, `min`, `max`, `clip`. No other functions. **Availability is verified against the engine at compile time (FR-276)** — S1 found the two-argument `min`/`max` forms are not valid ZEN calls, so this list states intent, not a guarantee. **Amended 2026-09-30, `RL-1265` DP-5 (in part; one sentence held for #967):** the rating grammar is verified against the engine by FR-276. It shares function names with `02` §4.6 where they coincide, but it is not one of §4.6's profiles, and `pricing_core.data.expressions` never parses it. "The same restricted grammar as `02` §4.6" is superseded by this amendment. Nothing is struck. The sentence that defines the rating grammar itself was held until the FR-244 ruling was minted; it is released below (2026-09-30, `RL-1312`, `RL-1313` DP-G1 (b): the WK-1178 code slice writes it, spec first, from `RL-1312`'s text). **Amended 2026-09-30, `RL-1265` DP-5 and `RL-1312`:** the rating grammar is FR-244's own: ZEN's expression language, **restricted to an enforced allow-list of operators and functions** and verified against the engine by FR-276. It shares function names with `02` §4.6 where they coincide, but it is not one of §4.6's profiles, and `pricing_core.data.expressions` never parses it. **Operators:** `+ - * /` (and unary `-`), parentheses, `== != < <= > >=`, `and or not`, the ternary `c ? a : b`, and `??`, which returns its right operand when its left is null. It is the coalescing form the function list above names `coalesce(a, b)`, and it is never a division guard (FR-274). **Literals:** numbers, `true`, `false`, `null` and single-quoted strings. **Functions:** `min([…])`, `max([…])`, `abs` and `number(x)`. `number(x)` exists because a `lookup` step's output is always a string. It converts a numeric string (surrounding spaces and exponent form such as `1e3` are accepted) to an exact decimal inside the engine, returns a number unchanged, and converts a boolean to `1` or `0`. Any other string (for example `abc`, an empty string, or `1,07`) and null fail the quote with `RATING_EVALUATION_FAILED`. Write `number(v ?? '1.0')` to default a missing value (`RL-1322`, correcting `RL-1312`). **No rounding function** (`round`, `floor`, `ceil`): money is rounded only by an `output` step's declared rounding (FR-226), never twice (NFR-496). Whether rounding is offered anywhere else is an open question (`03` §10, `OQ-1316`). The list above states intent that the engine does not meet. `coalesce(a, b)` is written `a ?? b`, `clip(x, lo, hi)` is `min([max([x, lo]), hi])`, `round(x, mode, dp)` is the output step's rounding, `band` is a `table` step with a banded key (FR-228), and `date_diff_years` is an input (FR-246). The allow-list binds every authored rating string (`expr`, `condition`, clamp bounds, `key_expr`), and anything outside it is refused at save with `EXPRESSION_INVALID_VOCABULARY`. **Numbers at the engine boundary:** inside ZEN, arithmetic is exact decimal (`0.1 + 0.2 == 0.3`). Callers pass money as integer minor units (FR-273). The binding refuses a `Decimal` input, and takes a `str` input as a string, never a number. Outputs return as floats and are taken through `_round_minor` (`Decimal(repr(x))`, quantized with the output step's declared mode). Integers above 2^53 at the boundary are untested. "The same restricted grammar as `02` §4.6" is superseded by this sentence. |
| **FR-245** | Arithmetic on monetary values is evaluated in `Decimal` with an explicit context (28 significant digits, `ROUND_HALF_EVEN`), never in binary floating point (R2). Mixing a monetary value and a float-typed value in one expression is a compile-time error. |
| **FR-246** | Expression steps cannot reference anything outside their declared inputs — no globals, no environment, no time-of-day. `now()` does not exist; a quote timestamp is an input. |

### 3.6 Premium ladder

| ID | Requirement |
|---|---|
| **FR-247** | Every Rating Version produces a **Premium Ladder** as a structured output, with each rung named, typed, and traceable: `risk_premium` (from the Peril Structure) → `+ expense loadings` → `+ commission` → `+ profit loading` → `office_premium` → `± optimisation adjustment` → `± constraints (min premium, capping)` → `+ IPT and fees` → `payable_premium`. |
| **FR-248** | Each ladder rung records both the value and the operation that produced it (multiplicative factor or additive amount), so the ladder reconciles exactly: applying every recorded operation to `risk_premium` reproduces `payable_premium` to the penny. This reconciliation is asserted at scoring time in `dev`/`uat` and sampled in `prod`. *(Amended 2026-09-30, `RL-1329` (DP-S3-5): the replay runs on the unrounded chain and rounds once. Each rung records its **unrounded value**, the engine's exact decimal for that rung in minor units, read across the binding as a string and never as a float (FR-273), beside its displayed `value_minor`. The displayed value is that rung's own unrounded value rounded once with the rung's declared rounding (FR-226); it is never computed from another rounded value. Each recorded operation is the operation the rung applied, recovered from the two unrounded values exactly where the engine did not round, and to the engine's precision where it did: a factor, a divisor (a gross-up such as `÷ 0.875`), or an exact added amount. It is never a ratio of rounded values. A binding clamp is recorded on the `constraints` rung as a `clamp` operation that names its bound (`min` or `max`) and the bound's exact value; the rung before it carries the value before the clamp. Replaying the recorded operations from the first rung's unrounded value, in exact decimal arithmetic with no intermediate rounding, and then applying the `payable_premium` rung's `round`, gives `payable_premium` to the penny. A `clamp` sets the replayed value to its bound. That `round` is the only rounding on the replay (NFR-496). Each operation also reproduces its own rung's unrounded value to the engine's precision (within 10⁻²⁶ of it, relative). The first rung is the first rung present, whatever its name, and its unrounded value is checked against the engine's value for its source, never against the ladder itself.)* *(Amended 2026-09-30, `RL-1346` (PL-1342 DP-S3-1): what a failure does. A scored quote whose ladder does not reconcile is **not served**. The shared evaluator (FR-254) refuses it with `LADDER_RECONCILIATION_FAILED`. Which Environments and sampling rates the check covers is this row's own `RL-1329`/Task 1 clause's to state; the refusal applies wherever the check runs. `POST /api/v1/score` answers 500 with that code, and `/score/compare` answers 500 naming the failing side. Batch scoring writes an `"error"` row with that code and continues (FR-255). A golden quote or an FR-261 property case that meets it fails. The message carries no quote input (NFR-499). Each refusal on `/score` is logged and counted by Environment. So every quote the platform serves has a reconciling ladder (NFR-496), and the count of refusals is measured, not assumed. An empty ladder, from an algorithm that declares no rung output, is not refused.)* *(Amended 2026-10-01, `PL-1348` (SL-1345), on the maintainer's entry headed `2026-09-30 15:17:54 BST — audit round-up: decisions`: the reconciliation runs on every scored quote in every Environment and is never sampled, superseding this row's "asserted at scoring time in `dev`/`uat` and sampled in `prod`". The trace-sampling rate (`rating.trace_sample_rate`, FR-259) governs trace persistence only; no Environment can switch the check off.)* |
| **FR-249** | Per-peril risk premium components are available as outputs, since monitoring (`05`) and reinsurance analysis both need them. |

### 3.7 Scoring

| ID | Requirement |
|---|---|
| **FR-250** | **Real-time scoring**: `POST /api/v1/score` evaluates one Quote Context against the Rating Version currently live in the target environment, returning the ladder, outputs, and (optionally) a Trace. Target p99 < 50 ms server-side (NFR-454). |
| **FR-251** | Scoring accepts an explicit `rating_version_ref` for what-if and testing; in `prod` this is permitted only for `approved` versions and is recorded as a `what_if` purpose, never as a quotable price. |
| **FR-252** | **The platform prices the *annual* payable premium, and instalment loading is an optional final ladder rung (`instalment_loading`) read from a rate table. APR calculation and schedule generation are downstream and are not built here.** (OQ-619, decided 2026-08-18; **Phase 2**.) The loading exists because it changes the price the customer actually compares, and without it `04-optimisation.md`'s demand model is fitted against a price nobody was offered. It stops at a loading because APR and schedule generation carry a consumer-credit regulatory surface — disclosure, the regulated APR formula, and rules about what may be charged — that belongs to a billing system with its own compliance obligations, and taking it on here would make every rating release a consumer-credit release. **The boundary is drawn where the maths stops being rating maths**: the platform outputs an annual premium and, where the rung is mounted, the loaded annual equivalent; it never emits a payment schedule, an APR figure, or a credit agreement term. A Quote Context asking for one is refused rather than answered approximately, because an APR that is nearly right is a compliance defect and not a rounding one. |
| **FR-253** | **Batch scoring**: `POST /api/v1/score/batch` re-rates a Dataset Version against one or more Rating Versions as a Job, writing results to a new content-addressed parquet output with the quote key, ladder, and selected outputs per row. |
| **FR-254** | Batch scoring is chunked, resumable, and progress-reporting, and uses the identical compiled bundle and code path as real-time scoring — never a separate "batch implementation" that could diverge. *(Clarified 2026-08-29, WK-671 Slice 3: where "resumable" lives, what it is keyed on, and what sits outside it. **Chunk checkpointing is the Job handler's, never `score_batch`'s** — §5.2's signature takes and returns a `pl.LazyFrame` and carries no Job identity, output location or resume point, and ADR-703/DEP-3 forbids `pricing-core` the durable state a checkpoint needs; so the handler records each completed chunk and skips it on re-entry, while `score_batch` stays a pure chunked transform reporting progress and honouring cancellation. **The checkpoint is keyed on the run's content identity** — the compiled bundle's content hash (FR-239), the Dataset Version reference and the chunk index — **never on the Job id**, because no terminal Job is ever re-run: `VALID_TRANSITIONS` gives `failed` no outbound edge, and `07` FR-414 releases a failed key so the next submission is a *fresh* Job. Chunk parts are scratch written outside the content-addressed store and released when the run completes, so FR-420's reference-counted GC never holds them. **The re-run trigger itself is outside this requirement**: it is `07` FR-403 and FR-414's, owned by whichever workstream builds FR-413, so until that is built a batch run is resumable and nothing in production resumes it. Ruled in `docs/rulings/RL-00857-d6-chunk-checkpointed-resume-built-in-the-job-handler-and-keyed-on-content-not-on-the-job.md` RL-857.)* |
| **FR-255** | Scoring errors are typed and per-quote: contract violation, reference miss, table miss, constraint decline, model failure. A batch run reports counts and samples per error type and does not abort on individual failures unless the failure rate exceeds a declared threshold. *(Clarified 2026-08-29, WK-671 Slice 3: where "declared" lives. The threshold is the workspace setting `rating.batch_abort_failure_rate` (`07` FR-448), **unset by default** — undeclared means no rate-based abort, and the counts-and-samples half above still applies. A batch request may carry its own value, and it may only **lower** the effective threshold, never raise it: `01` FR-56 already decided that a threshold has no safe direction to move in, and `01` §4's `severity_override` is the one-directional shape that follows from it. The run's value is an argument to the Job, not a Setting, so `07` FR-446's environment-variable → workspace-setting → platform-default precedence is unchanged and stays fully inspectable. When a run aborts it records both the threshold in force and the observed failure rate, because an abort nobody can reconstruct is not auditable. Ruled in `docs/rulings/RL-00889-d3-the-batch-abort-threshold-is-a-workspace-setting-with-a-one-directional-per-run-argument.md` RL-889.)* |
| **FR-256** | A `decline` outcome from a `constraint` step is a **successful** scoring response with `outcome: declined` and reason codes — not an HTTP error. *(Amended 2026-08-29, WK-671 Slice 1: "reason codes" is plural because evaluation does not short-circuit. The whole DAG evaluates in topological order — FR-216 defines no early-exit primitive — so `decline_reasons` collects the `reason_code` of every firing constraint step and not only the first, which is what FR-225's "each ... appears ... in any decline response" requires; and `premium_ladder` stays populated through to `payable_premium`, reconciling under NFR-496, so a declined quote still reports what it would have cost. `docs/contracts/schemas/scoring.schema.json` already requires `premium_ladder` for every `outcome` including `declined` and types `decline_reasons` as `array<string>`; this amendment makes the requirement say what that contract already assumes. Ruled in `docs/rulings/RL-00875-how-a-decline-is-represented-the-whole-dag-evaluates-and-every-firing-constraint-s-code-is-collected.md` RL-875.)* |

### 3.8 Trace, testing, and promotion evidence

| ID | Requirement |
|---|---|
| **FR-257** | A Rating Version cannot reach `approved` without: a passing Regression Suite, a Dislocation Run against the current live version over an agreed portfolio, a change summary (FR-242), and — where the insurer has enabled it — a passing GIPP check (`04-optimisation.md`) (R4). *(Clarified 2026-09-28, WK-672 Slice 3, the deputy's DP-S3-1 by delegation.)* A passing Regression Suite has at least one golden quote; a submission whose suite has none, or whose algorithm has no suite, is refused with `EVIDENCE_INCOMPLETE`. It applies forward, at submit. |
| **FR-258** | **Trace**: on request, scoring returns every step's id, label, consumed values, produced value, matched table row key, and elapsed time, plus the bundle hash and rating version reference. Traces are the same structure in real-time and batch. |
| **FR-259** | In production, traces are **sampled** (default 1 %, configurable, plus 100 % of declines and errors) and persisted for ≥ 13 months (NFR-459), feeding `05-monitoring.md`. *(Clarified 2026-08-29, WK-671 Slices 3 and 4 — the scope these two opening words already carry, written down because two separate planning documents read this requirement and FR-258 as silent about batch. **Batch scoring contributes nothing to the sampled stream**, so `score_batch` takes no sampling policy: the stream is the production real-time quoting path, which is what §5.1's route and `05` §7's dependency row both call "sampled production traces", and what NFR-500 sizes at 1 % of 50 M annual *quotes*. The division of labour is already decided elsewhere — `05` FR-317's 2026-08-26 amendment (OQ-627) puts full-coverage A/E on a batch re-score of the exposure dataset and, in its own words, *not from traces* — leaving sampling for quote-level metrics. A batch run may still produce traces on request under FR-258, and they are written with that Job's own output and never returned by the production traces route. Ruled in `docs/rulings/INDEX.md#2026-08-29-w11-slices-3-4-rulingsmd` RL-890.)* *(Clarified 2026-08-30, WK-671 Task 4B: what the environment recorded on a sampled trace means, written down because the first implementation derived it from the caller's granted scope. It is the environment the quote was served in — the same target environment FR-250 selects the live Rating Version from, and the one FR-430 (`07`) scopes the presented key to. It stands in for the ScoringTrace's Deployment parent (`00` §4.1) until Deployment exists in WK-674, which is the deferral RL-888 made, so its value must be reconcilable to the Deployment that actually served the quote. It is therefore not derived from the set of environments a Service Account is granted: FR-389 (`07`) grants an account named environments, plural, and FR-430's per-key check presupposes that it may, so the granted set is an authorisation scope while the served environment is a property of the call. A sampled real-time trace always records one; absence is reserved as the signal that a trace was produced on request for a batch run (FR-258, RL-890), so a real-time trace is never written without it. Ruled in `docs/rulings/RL-00916-the-field-is-the-environment-the-quote-was-served-in-the-spec-already-says-so-and-the-branch-does-not-merge-until-it-says-so-too.md` RL-916.)* *(Clarified 2026-10-05, WK-1178 — whether a sampled trace reproduced the quote it is listed against, written down because the route listed a re-score that did not reproduce the served result exactly as one that did (FD-1433). A sampled real-time trace's body is produced off the serving request by a deterministic re-score of the pinned bundle, and that re-score is compared with the result actually served (`RL-862`, condition (b)). Each item of `GET /api/v1/traces` therefore carries `status`: `complete` when the re-score reproduced the served result, `mismatch` when it did not. A `mismatch` item stays listed, so the record of what the re-score did is kept, but it is never presented as the quote's trace: the served result stands, and the item's body documents a re-score that differed from it. A trace still awaiting its re-score, or one whose pinned bundle could not be resolved, has no body and is not listed. Ruled in `RL-1434`.)* |
| **FR-260** | A **Golden Quote** stores a Quote Context and the expected outputs. Promotion re-scores every golden quote and refuses promotion on any mismatch beyond a declared tolerance (default: exact for money). *(Amended 2026-09-28, the deputy's DP-S2-1 and DP-S2-2 decisions by delegation, `PL-1189`. (1) The check runs at `POST /api/v1/rating-versions/{id}/submit`. (2) The submission's evidence pins the suite version it used, by content hash. (3) The evidence lists every golden quote added, removed, or whose expected output, tolerance or quote context changed since the suite pinned by the most recently approved Rating Version of the same algorithm. Each change names its author, who is the actor of the creation Audit Event of the suite version that introduced it (`06` FR-368). (4) Where the algorithm has no suite, the evidence says so explicitly (`regression_suite: "none"`, "no golden quotes were checked"), never an empty pass. Whether a suite is required is decided by WK-672 Slice 3.)* |
| **FR-261** | A **Regression Suite** may also contain property assertions evaluated over generated quote contexts: premium is positive, premium is monotone in a declared input, no output is null, the ladder reconciles (FR-248), and premium is bounded by declared limits. Generation uses hypothesis-style sampling over the input contract with a persisted seed. *(Amended 2026-09-28, WK-672 Slice 3, the deputy's F4 decision in `RS-1176`; mints no id.)* The generated cases and every counterexample are persisted with the run and are its reproduction record; replaying a run re-scores them. The seed, with the generator version persisted beside it, serves same-version regeneration only. The case store is `FR-1221`. *(Clarified 2026-09-28, WK-672 Slice 3, the deputy's DP-S3-5, DP-S3-6 and DP-S3-7 by delegation.)* **"Premium is monotone in a declared input" is a *ceteris paribus* property:** every generated context is a base, and each base is swept over a grid of the named input with every other input held fixed. The grid is a uniform grid of five points, the declared bounds included (the property's `lower` and `upper`, else the input contract's `min` and `max`), plus five points sampled from a generator seeded by the suite's seed and the input's name, all inside the bounds; the suite's seed fixes them, so a replay visits exactly the same points. **The sampled points are the same for every base context** (they depend on the suite's seed and the input's name only), so the grid is one fixed set of at most ten points per property. The range is the property's `lower` and `upper` intersected with the contract's `min` and `max`, so a lone `lower` or `upper` is valid when the contract supplies the other end. Four cases are refused with `REGRESSION_PROPERTY_INVALID` (422) **at declaration**: (1) no range at all (an end that neither the property nor the contract gives); (2) a range empty after the intersection; (3) a decimal range holding no two-place value; (4) an input absent from the algorithm's input contract or not orderable (neither `int` nor `decimal`). The refusal is made by `POST /api/v1/regression-suites/{slug}/versions` against the latest saved version of the suite's algorithm, and again by the `rating.regression` Job, naming the property (the refusal is `class UnsweepableProperty(ValueError)` in `pricing_core/rating/properties.py`, the only exception mapped to this code; any other exception ends the Job `JOB_HANDLER_FAILED` with the exception's type name alone, never its message, because a message may carry a quote input, NFR-499). The declaration check is a **fast refusal** against the algorithm's **latest saved version**; the Job is the **authoritative** check, made against the version actually run, so a Rating Version pinning an older version is caught there; it never reaches a running Job as a raw exception. A lone `lower` or `upper` is valid when the input contract supplies the other end. Premiums are compared exactly in integer minor units, with no tolerance, and must be non-decreasing (or non-increasing if declared), strictly so only when the property declares `strict`. A declined grid point is skipped and each quoted point is compared with the next quoted point across the gap, so a legitimate decline band is not a failure; a property whose every sweep had fewer than two quoted points compared nothing and **fails** (`MONOTONE_NO_COMPARABLE_PAIRS`), never a vacuous pass. A counterexample is the base context and the two adjacent grid values at which the order broke. The run records `grid: uniform+sampled` on the result, because this is the weaker form: **the compiled bundle pins no Banding, so no band edge is in the grid, and an inversion narrower than the spacing between the grid and sampled points may not be detected** until `OQ-1224` lands. `no_null_output` requires every *declared* output present and non-null, because a null output is omitted from `ScoringResult.outputs` and a check over the returned values alone could never fail. The named input must be an `int` or `decimal` with a range (`OQ-1223`: ordinal inputs; `OQ-1222`: a GBM's split thresholds). |
| **FR-262** | The **Quote Sandbox** lets an actuary score an arbitrary quote against any accessible Rating Version and see the full trace inline, alongside the same quote scored against a comparison version with a step-by-step difference. *(Clarified 2026-09-29, WK-672 Slice 4, `RL-1172` §5.)* The endpoint `POST /api/v1/score/compare` delivers the backend limb: two `score_one` calls and a step-level trace diff, no new evaluator. The Quote Sandbox view is WK-675's. |
| **FR-1221** | A Regression Run's generated cases and counterexamples are persisted as one content-addressed canonical JSON blob (`BlobRef`), referenced from the run. They are replayed by re-scoring and never regenerated (`RS-1176` condition 4). The blob carries the same access control as a sampled trace and a Golden Quote: read only with `rating:read` in its workspace, and never logged (NFR-499). *(Added 2026-09-28, WK-672 Slice 3, the deputy's DP-S3-4 (i) by delegation. Its id is a working id, owned by this branch's pull request, and is renumbered at that request's mint turn.)* *(Clarified 2026-09-29: minted as FR-1221 in #886 (squash 6a8b8e70); the working-id sentence above is historical.)* |

### 3.9 Dislocation

| ID | Requirement |
|---|---|
| **FR-263** | A **Dislocation Run** re-rates a fixed portfolio Dataset Version under a baseline and a candidate Rating Version and reports: the distribution of premium change (absolute and percentage), average change overall and by declared segment, the exposure/policy count in each change band, movers beyond configurable thresholds with drill-down to individual quotes, and total portfolio premium change. |
| **FR-264** | Dislocation results are sliceable by any Factor available on the portfolio dataset, and by the ladder rung at which the change originated — answering "which part of the change caused this?", not merely "how much did it change?". |
| **FR-265** | Dislocation output is a persisted, citable artifact referenced by the approval request, not a transient screen. |
| **FR-266** | Where the candidate and baseline differ in more than one respect (new model *and* rate table edits), dislocation supports **attribution**: re-rating with each change applied in isolation and cumulatively, so the change is decomposed into its causes. *(Amended 2026-10-03, WK-673 Slice 1, on OQ-1187's decision (`RL-1184` F3), the deputy's F3 decision of 2026-09-28 12:10:21 BST as corrected at 13:57:02 BST (`RS-1201`), `RL-1264` and `RL-1394`.)* **The attribution of record is exact Shapley over the declared changes, for K ≤ 6.** For each policy, each change's Shapley value is computed exactly, as a rational with denominator K!, from v(S) for each of the 2^K subsets S of the declared changes, where v(S) is the policy's payable premium in integer minor units under the subset bundle for S (FR-1398), or a ladder replay proven equal to it under `RL-1264`'s feasibility rule. The K values are allocated to integer minor units by **largest remainder**, ties broken in the declared change order (FR-1399), so that the policy's parts sum exactly to its candidate minus baseline payable premium; plain rounding is forbidden. Portfolio figures are sums of the per-policy integer parts. The **isolated** figure (the change applied alone) and the declared-order **cumulative** figure are views beside the Shapley figure, never the attribution, and the **interaction residual**, total − Σ isolated, is its own line. **Above K = 6** the analyst groups the changes into at most 6 change groups (FR-1399) and Shapley runs over the groups; where the analyst does not group them, the isolated-plus-cumulative method with its residual line is shown with R and a lower bound on S (`RS-1201` defines both), labelled order-dependent and never presented as a decomposition. R is exact. The bound is the maximum over a declared number of orders, at least 2 and always including the declared order and its reverse; it is printed as "S ≥ x over n orders", never as S, and the run records n. Exactness holds on the integer minor units each rating returns through FR-273's boundary, not on a decimal carried through the engine (§3.11). |
| **FR-1397** | **Attribution reconciles exactly on the rating path's own integers, on every run.** Every attribution part, the interaction-residual line and the total are integer minor units taken from the payable premium's `value_minor` as the rating path produces it (FR-273). Per policy and at portfolio level, the Shapley parts sum exactly to the total, and the isolated figures plus the residual line sum exactly to the total, as integers, with no float summed after rounding. The run checks both on every run and fails, naming the first policy that does not reconcile, rather than persist a result that does not. The check is proven on deliberately broken input: a plain-rounding allocation, on a policy where plain rounding does not sum to the total, and a Shapley value perturbed by one minor unit are each refused. *(Added 2026-10-03, WK-673 Slice 1: the deputy's F3 item 4, corrected 2026-09-28 13:57:02 BST; `RL-1394`.)* |
| **FR-1398** | **Attribution runs on the ZEN engine through the ordinary compile path, and its subset bundles are ephemeral.** Each subset of the declared changes is a bundle built at step granularity from the baseline's pins and algorithm with that subset's changes substituted, compiled by `compile_bundle` and hydrated by `load_bundle`, so it passes the same validation as a real version (FR-240, FR-274, FR-275, FR-276) and is rated by the engine, never by a mirror of it. This holds for every subset bundle a run compiles, whether v(S) is read from it or it verifies a ladder replay (FR-266's amendment). A subset bundle is content-addressed and has **no Rating Version identity**: it is never a `rating_version` row, and it is never approvable, deployable or listed in any version list. It is cached per run by its content hash and discarded with the run's scratch. A subset that fails to compile fails the run with `BUNDLE_COMPILE_FAILED`, naming the subset; it is never skipped. The run artifact records how many subset bundles were compiled and their content hashes, and whether v(S) came from re-rating or from ladder replay (§4.6). *(Added 2026-10-03, WK-673 Slice 1: `RL-1264` DP-1 (a), with its conditions; `RL-1394`.)* |
| **FR-1399** | **The declared changes are derived, and the analyst may group them.** The server derives the change list from the difference between baseline and candidate, at step granularity: each `step_id` the structural diff (FR-219) reports as added, removed, or present in both with any field changed is exactly one derived change, however many of its fields changed. Its kind is `step_added`, `step_removed`, `table_repointed` where the only changed field is the step's table or lookup reference, or `step_changed`. A pin difference (FR-237) that a derived step change accounts for, through that step's table, lookup or model reference, is part of that change, never a second one; a pin difference no step change accounts for is its own derived change, of kind `pin`. Derived changes are numbered `c1`, `c2`, … in the derived order: step changes sorted by `step_id`, then unaccounted pin differences sorted by their reference string. The analyst may merge derived changes into at most 6 named **change groups** in the `DislocationSpec`. The server checks that the groups partition the derived list exactly, every derived change in exactly one group, and refuses otherwise with `VALIDATION_FAILED`, naming each change left out or placed twice. With no groups given, each derived change is its own group, named by its id, and above 6 FR-266's above-six rule applies. The **declared change order** is the order of the groups as the analyst gives them, or with no groups the derived order. The derived list and the groups are both on the artifact (§4.6). *(Added 2026-10-03, WK-673 Slice 1: `RL-1264` DP-2 (c); `RL-1394`.)* |

### 3.10 Deployment

| ID | Requirement |
|---|---|
| **FR-267** | A **Deployment** binds an `approved` Rating Version to an Environment, recording who, when, why, and the bundle hash. Only a Deployer can deploy; `prod` deployment additionally requires the approval record to be complete (`06-governance.md`). |
| **FR-268** | Deployment is atomic per environment: a scoring call sees either the old or the new bundle, never a mix. Bundles are pre-warmed into cache before the switch. |
| **FR-269** | **Rollback** to any previously-deployed Rating Version in that environment is a single audited operation with the same guarantees, and does not require re-approval. |
| **FR-270** | Optional **date-based routing** allows an environment to hold multiple deployed versions selected by the quote's effective date, for pre-loading a future rate change. Overlapping date ranges are rejected at deployment time. |
| **FR-271** | Optional **shadow scoring**: a proportion of live traffic is additionally scored against a candidate version, with results recorded but never returned to the caller — the pre-deployment safety net feeding `05-monitoring.md`. |
| **FR-272** | Every deployment, rollback, and routing change emits an Audit Event and a notification to a configured channel. **Amended 2026-09-28 (`RL-1232` DP-4): the two halves are split by phase.** WK-674 emits the Audit Event in the same transaction as the change. That event is the durable deployment event `05` consumes (§7). WK-674 builds ~~no channel and~~ no second event store. ~~Delivering a notification to a configured channel, with the retry and failure-surfacing obligations of `05` FR-336, is `05`'s alert routing, owned by WK-688 (Phase 4). Until WK-688 delivers it, no channel is configured and none is claimed.~~ **Amended 2026-09-29 (`RL-1232` DP-4, the maintainer's answer Q848-1): the channel is `07` FR-453's signed deployment-notification webhooks.** Which Work delivers FR-453's deployment-notification limb is open (`07` §10, `OQ-1233`). Until it is decided and delivered, no channel is configured and none is claimed. *(Amended 2026-09-29, `RL-1252`: `OQ-1233` is decided (b). The notification limb is deferred to Phase 4, with WK-688 as its owner, and is delivered through FR-453's signed webhooks, which WK-688 builds for both limbs. The Audit Event limb stays WK-674's, in Phase 2. Until WK-688 delivers the notification, no channel is configured and none is claimed.)* |

> **The Deployment contract, added 2026-10-03 (WK-674 Slice 2, `PL-1392`), for FR-267.** The Deployment's shape, its invariants (append-only, `approved` Rating Versions only, a `rating_version` reference only), the Deployment Request that gates a `prod` deployment (`RL-1301` A) and the audit actions this Work emits are §4.12. The requirement above is not reworded. `GET /api/v1/environments/{env}/deployments` (§5.1) is the history that `06` FR-382 reads.
>
> **The Audit Event limb for deploy, dated 2026-10-03 (WK-674 Slice 2, `PL-1392`), for FR-272.** Slice 2 delivers the Audit Event limb for a deployment only: `deployment.created`, written in the same transaction as the Deployment row (§4.12). The rollback event `deployment.rolled_back` is Slice 5's, and the routing and shadow events are Slice 6's; §4.12 names all four once. The notification limb stays WK-688's (`RL-1232` DP-4, as amended above).

### 3.11 Numeric precision at the engine boundary

Spike **S1** (2026-08-14, `zen-engine` 0.53.0) tested this end to end. The result splits
cleanly, and it **corrects an earlier conclusion of ours**
([`research`](../research/track-a-findings.md) F14).

**Inside the engine, arithmetic is exact.** `0.1 + 0.2 == 0.3` evaluates `true`;
`1.005 * 100` gives `100.5`; `1.1 * 3 == 3.3` is `true`. ADR-706 stands.

**At the Python binding, there is no decimal type at all.** A Python `Decimal` is
*rejected* (`TypeError: unsupported type Decimal`), and every value returned is a Python
`float` — `1/3` comes back as `0.33333333333333337`. Exactness cannot be carried across the
boundary in either direction.

After F1 we recorded that the integer-minor-units workaround was "not required for
correctness". **That was wrong** — right about the engine, wrong about the system. The
engine is exact; the binding is not, and the binding is what the platform talks to.

| ID | Requirement |
|---|---|
| **FR-273** | **Money crosses the engine boundary only as integer minor units.** The binding accepts no decimal type and returns `float`, so exactness cannot survive the crossing as a fractional value. Integers up to 2^53 are exactly representable in `float64` (≈ £90 trillion in pence), which is why the integer form is safe where the fractional form is not. Fractional quantities — relativities, loadings, factors — may be *held* in rate tables and applied *inside* the engine, but any value returning to Python for further arithmetic is an integer minor unit or a string. A startup self-check asserts the round-trip; failing it prevents the service starting. |
| **FR-274** | **Division is the guarded operation, not transcendentals.** S1 found `log` and `sqrt` do not exist in the ZEN expression language at all (they fail to parse), so the earlier requirement guarded operations that cannot be called. The real hazard is **division by zero, which returns `null` and does not raise**: `1/0`, `0/0` and `premium/0` all evaluate to `null` silently. The null then raises a `vmError` at the point it is *used*, reporting the multiply rather than the division that caused it. Every division in a rateable path carries an explicit zero guard, bundle compilation (FR-240) rejects an unguarded one, and **a `null` reaching an `output` step is a hard error** — otherwise a null premium can be emitted. |
| **FR-275** | Bundle compilation checks that no rate table value, constant, or intermediate requires a decimal scale beyond `rust_decimal`'s limit of 28, and fails with a named error rather than allowing a silent loss of precision deep in a ladder. Confirmed relevant by S1: `(1/3) * 3 == 1` evaluates `false`, so repeated division loses exactness inside the engine too. |
| **FR-276** | The `expression` step's function vocabulary (FR-244) is validated **against the engine actually in use**, not against this specification's list. S1 found `abs`, `round`, `floor`, `ceil` and `sum` available, but the two-argument `min(a, b)` / `max(a, b)` forms rejected as invalid function calls. Bundle compilation resolves every function name against the engine's real vocabulary and fails on a mismatch, so a graph cannot reference a function that exists only in our documentation. |

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
  "sub_graphs": [{"ref": "sub_graph:ncd-ladder@4", "mount_point": "s_ncd",
                  "inputs": {"ncd_years": "ncd_years"}, "outputs": {"ncd_factor": "ncd_factor"}}]
}
```

**Invariants** — DAG acyclic; every `consumes` name is `produced` by exactly one upstream
step; every declared output has an `output` step; no step is unreachable from an `input`
and unreferenced by an `output` (FR-212). *(Amended 2026-10-09, WK-1250 Slice 2, `RL-1309` DP-3 items 2 to 4: a mount is a node. Its mapped outputs are produced by it and its mapped inputs are consumed by it, and acyclicity and "produced by exactly one upstream step" count it. `mount_point` matches `^[A-Za-z][A-Za-z0-9_]*$`, contains no `__`, and is unique among the parent's `step_id`s and its other mounts. Every input port of the mounted sub-graph is mapped exactly once, and the mapped output ports are a non-empty subset; an unmapped output port is legal, and a parent step that consumes one is refused by FR-212.)*

### 4.2 `RateTable` / `RateTableVersion`

```json
{
  "slug": "motor-driver-age-relativity",
  "version": 6,
  "rateable": true,
  "storage": "rows",
  "keys": [{"name": "driver_age_banded", "type": "string", "factor_ref": "factor:driver_age_banded@3"}],
  "value": {"name": "relativity", "type": "relativity", "min": 0.2, "max": 5.0},
  "default_row": null,
  "rows": [
    {"driver_age_banded": "17-20", "relativity": "1.8400"},
    {"driver_age_banded": "21-24", "relativity": "1.4100"},
    {"driver_age_banded": "25-29", "relativity": "1.1200"}
  ],
  "seeded_from": {"model_ref": "model:motor-ad-frequency@7", "seeded_at": "2026-07-02T10:00:00Z"},
  "created_by_operation": null,
  "created_by_import": null,
  "change_note": "Softened 17-20 from 1.92 to 1.84 following competitor review; see OPT run 2026-07-11.",
  "diff_vs_previous": {"changed_cells": 3, "max_abs_change_pct": 4.2,
                       "exposure_weighted_mean_change_pct": 0.8,
                       "portfolio_exposure": "48210.5", "matched_exposure": "47902.0"},
  "diff_vs_seed": {"changed_cells": 7, "exposure_weighted_mean_change_pct": -2.1,
                   "portfolio_exposure": "48210.5", "matched_exposure": "47902.0"}
}
```

Values are stored as decimal strings, never JSON floats (R2).

> **`factor_ref` added 2026-10-03 (`RL-1361`, FR-228).** A key's `factor_ref`
> pins the Factor version the key is bound to, and a key carries at most one of
> `factor_ref` and `banding_ref`. A seeded table has one key, named after the Factor's slug
> and bound by `factor_ref` (FR-230), and this example is one.

> **Coverage added 2026-10-05 (`RL-1361`, FR-231).** `RateTableDiff` carries
> `portfolio_exposure` and `matched_exposure`, decimal strings: the named portfolio's total
> exposure and the exposure that mapped to a cell of the current version. Both are null
> when no portfolio is named. They tell apart the reasons for a null mean: no portfolio,
> weights on no changed cell, or only zero-weight cells.

> **Per-cell diff added 2026-10-05 (`RL-1418`, FR-231, FD-1358).** The diff's changed
> cells are served one page at a time by `GET …/diff/cells` (§5.1), as `RateTableDiffCell`
> items in `model-schema`: `key`, an object holding each declared key's name and the cell's
> stored value for it; `change`, one of `added`, `removed`, `changed`; `baseline_value` and
> `current_value`, decimal strings, null on the side where the cell is absent;
> `abs_change`, `current_value − baseline_value`, null unless both are present;
> `rel_change_pct`, `(current_value − baseline_value) / baseline_value × 100`, null unless
> both are present and the baseline is not zero; and `weight`, a decimal string: the
> cell's Σ exposure as FR-231 states it, `"0"` for a cell of the current version whose Σ is
> 0, one that no portfolio row maps to included, and null when no portfolio is named or the cell is `removed`
> (rows map only to cells of the current version). The set is exactly the cells
> `changed_cells` counts, added and removed cells included. The order is ascending by key
> tuple, the keys taken in declaration order and each value compared as its stored string
> by code point; a version is immutable and a key tuple unique within it, so the order is
> total and every page is reproducible. The items agree with the summary:
> `max_abs_change_pct` is the largest `|rel_change_pct|`, and
> `exposure_weighted_mean_change_pct` is Σ(`weight` × `rel_change_pct`) / Σ `weight` over
> the items where both are present and `weight` is not zero. The per-cell view adds no field
> to `RateTableDiff`.

> **`storage` added 2026-08-18 with FR-232** (OQ-616). `rows` or `parquet`, decided
> against the workspace's cell-count threshold when the version is written and **immutable
> with the version**, so a reader never has to ask which form a past version took and raising
> the threshold cannot silently re-home versions already written. Above the threshold `rows`
> is absent from this document and the cells are addressed by a `BlobRef`; every other field
> here, and every question a caller may ask, is unchanged — what changes is that FR-231's
> diff and its exposure weighting answer **202 with a Job** rather than 200.

> *(`created_by_operation` and `created_by_import` added 2026-08-28, W10-3 readiness.)* A
> version created by a bulk operation carries the operation record — `BulkOperation`,
> `04` §4.4 — which is what FR-233's "records its parameters, not just the resulting
> cells" means. A version created by CSV/XLSX import carries the source file's identity
> and the strict round-trip verdict (`created_by_import`: `{"filename", "content_sha256",
> "round_trip": "passed", "applied_to"}`; `applied_to` added 2026-08-28, naming the
> addressed baseline version — the import endpoint addresses `{slug}@{version}`, so the
> record mirrors `BulkOperation.applied_to`); `filename` (amended 2026-08-28, DP5) is the
> name of the actually-uploaded file as the endpoint received it (stored as text, bounded
> length, never used as a path), not a format-derived constant — per FR-235. Both are
> set at creation and immutable with the version; the before/after cells and the actor
> belong to NFR-498's Audit Event, not here. This example's version was edited by
> hand, so both are `null`.

> **Seed lineage survives every derivation.** `seeded_from` is set only by
> seed-from-model, ~~on the first version of a lineage~~ on every version a seed creates:
> the first version of a lineage, or a re-seed appended to it, which records its own
> source model and starts a new seed origin (**amended 2026-10-03, `RL-1375` DP-1**).
> `against=seed` on a version resolves to its seed origin: the lowest-numbered version of
> the table whose `seeded_from` equals that version's. Every derived version — manual
> edit, bulk operation, import — inherits the baseline's `seeded_from` unchanged, and a
> version whose baseline had none carries none. This example's hand-edited version keeps
> its `seeded_from`, and FR-230's "how far have we moved from the technical rate?"
> must stay answerable along the whole chain, so `diff_vs_seed` remains meaningful on
> every derived version. Save-time validation (FR-234) checks the equality against
> the resolved baseline — `BulkOperation.applied_to` or `created_by_import.applied_to` —
> and a derived version may not invent or drop the anchor. `created_by_operation` and
> `created_by_import` remain mutually exclusive.

> **Re-seeding an existing table (added 2026-10-03, `RL-1375` DP-2, FR-230).** A seed
> into an existing table is accepted only when its current version has exactly one key,
> and that key either carries a `factor_ref` naming the named Factor's slug, at any
> version, or carries neither `factor_ref` nor `banding_ref` and is named after that slug,
> as every key seeded before `factor_ref` existed is. The new version's key is bound by
> `factor_ref`. Any other existing table refuses the seed with **422**
> `VALIDATION_FAILED`, naming the table and its keys; seed a new table slug instead.

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
    "custom_objectives": ["custom_objective:capped-gamma@3"],
    "sub_graphs": ["sub_graph:ncd-ladder@4"]
  },
  "model_reference_mode": "exact",
  "effective_from": "2026-10-01", "effective_to": null,
  "bundle": {"content_hash": "sha256:…", "bytes": 84_112_904, "compiled_at": "2026-08-14T12:00:00Z", "blob_sha256": "…"},
  "change_summary": "AD frequency model refit on 2026H1 data; driver-age relativities softened at young ages; minimum premium raised to £280.",
  "evidence": {
    "regression_suite_run_id": "uuid",
    "dislocation_run_id": "uuid",
    "gipp_check_id": "uuid",
    "structural_diff_blob": "blob:sha256:…",
    "golden_quotes": {
      "status": "checked",
      "suite_ref": "regression_suite:motor-gb-core@4",
      "suite_content_hash": "sha256:…",
      "bundle_hash": "sha256:…",
      "results": ["…§4.9 golden_results items…"],
      "delta": {
        "baseline_rating_version_ref": "rating_version:motor-gb@26",
        "baseline_suite_ref": "regression_suite:motor-gb-core@3",
        "baseline_suite_content_hash": "sha256:…",
        "changes": [
          {"name": "young-driver-london", "change": "changed", "changed_fields": ["expected"],
           "before": {"payable_premium_minor": 112480, "outcome": "quoted"},
           "after": {"payable_premium_minor": 112900, "outcome": "quoted"},
           "steps": [{"version": 4, "changed_fields": ["expected"], "author": "…principal uuid…"}]}
        ]
      }
    }
  },
  "approval_request_id": "uuid"
}
```

Where the algorithm has no Regression Suite, `evidence.golden_quotes` takes the explicit
not-checked form instead, never an empty result list that reads as "0 mismatches"
(FR-260, amended 2026-09-28):

```json
{"status": "not_checked", "regression_suite": "none", "message": "no golden quotes were checked", "reason": "no_suite_for_algorithm"}
```

**Invariants** — `status ≥ approved` ⟹ every `evidence` field required by the workspace
policy is present and passing (R4, FR-257); every ~~pin resolves to an artifact whose
status is `approved` or better (FR-20)~~ *(restated by class 2026-10-09, WK-1250 Slice 2, `RL-1309` DP-1 item 5)* every pin to an artifact that has an approval lifecycle resolves to `approved` or better (FR-20); a pin to an artifact that has none (Rate Table Version, Rating Algorithm, Sub-graph Version) is governed by the pinning Rating Version's own approval; `bundle.content_hash` is reproducible from the
pins; every `model_call` step's `mode` equals `model_reference_mode`
(FR-223). *(Added 2026-09-28, `PL-1189`.)* `evidence.golden_quotes` is written only by the
submit gate (FR-260) and never edited after.

> *(Scoped 2026-08-27, W7-3 — OD1.)* Phase 1b builds the **minimal subset** of this shape:
> `slug`, `version`, `status` (`draft → review → approved`), `workspace_id`,
> `dataset_version_id`, a single pinned `model:{slug}@{version}` reference, `created_at`,
> `created_by`, `updated_at`. Compile, score, rate tables, the `pins`/`evidence`/`bundle`
> blocks, `model_reference_mode`, and deployment stay Phase 2 (FR-440). The
> `RatingVersion` model in `model-schema` carries only the Phase 1b subset; a Phase 2
> build widens the shape with the full contract.
>
> *(Discharged 2026-10-05, RL-1428, FD-1421.)* This note scoped Phase 1b only. W9-3
> (#293) widened `RatingVersion` with `algorithm_ref`, `pins` and `model_reference_mode`
> (CR-838), and `POST /api/v1/rating-versions` declares them (§5.1, FR-237). The note's
> statement that `model-schema` carries only the Phase 1b subset is no longer true and does
> not govern.

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
    {"rung": "risk_premium", "value_minor": 24_150, "unrounded_minor": "24150", "rounding": {"mode": "half_even", "dp": 0}, "operation": null,
     "components": {"AD": 9_820, "TP_BI": 11_400, "TP_PD": 2_180, "WINDSCREEN": 750}},
    {"rung": "expense_loading", "value_minor": 27_772, "unrounded_minor": "27772.5", "rounding": {"mode": "half_even", "dp": 0}, "operation": {"kind": "multiply", "factor": "1.15"}},
    {"rung": "commission", "value_minor": 31_411, "unrounded_minor": "31410.6975", "rounding": {"mode": "half_even", "dp": 0}, "operation": {"kind": "multiply", "factor": "1.131"}},
    {"rung": "profit_loading", "value_minor": 33_609, "unrounded_minor": "33609.446325", "rounding": {"mode": "half_even", "dp": 0}, "operation": {"kind": "multiply", "factor": "1.07"}},
    {"rung": "office_premium", "value_minor": 33_609, "unrounded_minor": "33609.446325", "rounding": {"mode": "half_even", "dp": 0}, "operation": {"kind": "none", "applied": []}},
    {"rung": "optimisation_adjustment", "value_minor": 32_268, "unrounded_minor": "32268.4294166325", "rounding": {"mode": "half_even", "dp": 0}, "operation": {"kind": "multiply", "factor": "0.9601"}},
    {"rung": "constraints", "value_minor": 32_268, "unrounded_minor": "32268.4294166325", "rounding": {"mode": "half_even", "dp": 0}, "operation": {"kind": "none", "applied": []}},
    {"rung": "ipt_and_fees", "value_minor": 36_108, "unrounded_minor": "36108.4294166325", "rounding": {"mode": "half_even", "dp": 0}, "operation": {"kind": "add", "amount_unrounded_minor": "3840"}},
    {"rung": "payable_premium", "value_minor": 36_108, "unrounded_minor": "36108.4294166325", "rounding": {"mode": "half_even", "dp": 0}, "operation": {"kind": "round", "mode": "half_even", "dp": 0}}
  ],
  "outputs": {"payable_premium_minor": 36_108, "peril_risk_premium": {"AD": 9_820, "…": "…"}},
  "decline_reasons": [],
  "trace": {"…see 4.5…"},
  "timing_ms": {"total": 7.4, "evaluate": 6.6}
}
```

*(Corrected 2026-08-31, F62 — the decision-maker ruled the example was wrong.)* `timing_ms`
carries exactly the two keys `score_one` emits: `total` (the whole call, `t_start` to
return) and `evaluate` (`async_evaluate()` alone, the DAG walk inside the ZEN engine); their
difference is input validation and post-evaluation ladder/output construction. No
requirement anywhere in this suite names a `model_call`/`table_lookups`/`expressions`
breakdown — `docs/rulings/RL-00931-correct-the-example-do-not-build-the-breakdown.md` RL-931.

*(Note 2026-09-30, `RL-1329`.)* The ladder in the example above does not reconcile, and it predates FR-248's 2026-09-30 amendment. For example, 24_150 × 1.15 is 27_772.5, but the example shows 27_780, and 27_780 × 1.1310 is 31_419.18, not 31_420. Under `RL-1329`, every rung also carries `unrounded_minor` (an exact decimal string, in minor units) and `rounding` (the rung's declared mode and dp). The operation kinds are `multiply` (`factor`), `divide` (`divisor`), `add` (`amount_unrounded_minor`), `clamp` (`bound`, `min` or `max`, and `bound_unrounded_minor`, on `constraints` only), `round` (`mode`, `dp`, on `payable_premium` only) and `none`. `factor`, `divisor` and the unrounded values are exact decimal strings in positional form, never in exponent form. `amount_minor` is kept only so that ladders stored before the ruling still validate. *(Replaced 2026-09-30, WK-674 Slice 3.)* The example above is that replacement: it was changed in the commit that changed the contract (`scoring.schema.json` and `model_schema.scoring`), and it reconciles (24_150 × 1.15 = 27_772.5, shown as 27_772 and carried on at 27_772.5; the one rounding is at `payable_premium`, 36_108.4294… to 36_108).

*(Note 2026-09-30, `RL-1329`: declared rung outputs change.)* A declared non-payable rung output (for example `office_premium_minor`) is served as the engine's exact value of its output step's source, after every step has run, rounded once with that step's declared rounding; it is never read from a float. Where no clamp binds, it equals its ladder rung's `value_minor` exactly. Where a clamp binds on it, it equals the bound exactly (the `constraints` rung's value), as it did before the ruling: a minimum-premium quote serves the minimum, not the rung's pre-clamp value. Before WK-674 Slice 3, the builder derived each loading factor from the previous rounded rung and cut it to 4 dp, so a rung could be off by up to about 10⁻⁴ of its value. That drift is corrected, so the served number changes on 57–64 % of quotes. `RL-1329` measured it in four seeded sweeps (42 000 quotes, tree `fa9a73c2`). The largest change over all four is **12521 minor units**, at premiums of about 1e7 minor units. The largest change at that scale in each sweep is 9997 (seed 20260930), 12521 (seed 7), 11724 (seed 1257) and 7820 (seed 42). In seed 20260930 (7000 quotes), the largest change is 1, 8, 101, 951 and 9997 minor units for premiums of about 1e3, 1e4, 1e5, 1e6 and 1e7 minor units. Of the non-payable rungs that changed in that sweep, 2052 changed by 1 minor unit, 682 by 2, 1848 by 3 to 9, and 9012 by 10 or more. The payable premium changes only at a near-tie within float resolution, by exactly 1 minor unit; the ruling's four sweeps (42 000 quotes) found none. The maintainer accepted the change as a correction, on 2026-09-30. A declared `money_minor` output that is not a rung is also served as the engine's exact value of its source rounded once with its output step's rounding, an integer; before the ruling it was served as the engine's unrounded float. That changes the served value by at most one rounding unit and its JSON type from a number with a fraction to an integer; the maintainer acknowledged it as a fix of an FR-273 violation, on 2026-09-30.

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
  "ladder_reconciled": true,
  "ladder_check_version": 2
}
```

*(Added 2026-10-01, `PL-1348` (SL-1345), from `PL-1342`'s Acceptance 10 and `RL-1346` §2. `ladder_check_version` is optional. Absent or `1` means the stored `ladder_reconciled` came from the check before this change, which compared the first rung and integer-ness only, and is **not** a reconciliation; a stored trace is never upgraded. `2` means FR-248's full check: `RL-1329`'s predicate over `RL-1329`'s ladder shape. Every trace built after this change carries `2` and `ladder_reconciled: true`, because a ladder that does not reconcile is refused (FR-248, `RL-1346`) and no trace is built for it.)*

### 4.6 `DislocationRun`

*(Amended 2026-10-03, WK-673 Slice 1, `RL-1394`: reconciled with `dislocation-run.schema.json` (`job_id`, `by_ladder_rung` and `errors` added to the example) and extended with FR-266's attribution as amended, FR-1397, FR-1398 and FR-1399. Money is integer minor units. `mean_change_pct` and `cumulative_change_pct` on an `attribution` item are derived views: `shapley_minor` (or, under `order_dependent`, `isolated_minor`) and `cumulative_minor` as a percentage of `totals.baseline_premium_minor`. `method` is `shapley` or `order_dependent`; `shapley_minor` is null only under `order_dependent`, and `order_sensitivity_lower_bound`, `residual_share` and `orders_sampled` are non-null only under it. S and R are decimal strings. `subset_valuation` is `rerate` or `ladder_replay`, and `replay_fell_back` is true where a replay mismatch fell the run back to re-rates (`RL-1264`); Slice 3 may amend these two with a dated note if it does not adopt replay.)*

```json
{
  "baseline_ref": "rating_version:motor-gb@26",
  "candidate_ref": "rating_version:motor-gb@27",
  "portfolio_dataset_version_id": "uuid",
  "job_id": "uuid",
  "policy_count": 1_284_902, "exposure_years": "1240118.400000",
  "totals": {"baseline_premium_minor": 41_882_100_00, "candidate_premium_minor": 42_698_300_00,
             "change_pct": 1.95},
  "outcomes": {"quoted_both": 1_284_902, "quoted_to_declined": 0, "declined_to_quoted": 0,
               "declined_both": 0, "error": 0, "zero_baseline": 0, "negative_baseline": 0},
  "distribution": [
    {"band": "< -10%", "policies": 41_204, "exposure_share": 0.031, "mean_change_pct": -14.2},
    {"band": "-10% to -5%", "policies": 118_402, "exposure_share": 0.092, "mean_change_pct": -7.1},
    {"band": "-5% to 0%", "policies": 402_118, "exposure_share": 0.314, "mean_change_pct": -2.2},
    {"band": "0% to +5%", "policies": 511_402, "exposure_share": 0.398, "mean_change_pct": 2.6},
    {"band": "+5% to +10%", "policies": 174_882, "exposure_share": 0.136, "mean_change_pct": 7.0},
    {"band": "≥ +10%", "policies": 36_894, "exposure_share": 0.029, "mean_change_pct": 14.8}
  ],
  "by_segment": [{"factor": "driver_age_band", "level": "17-20",
                  "policies": 22_104, "mean_change_pct": -6.4, "exposure_share": 0.017}],
  "by_ladder_rung": [{"rung": "risk_premium", "contribution_pct": 1.11},
                     {"rung": "constraints", "contribution_pct": 0.84}],
  "derived_changes": [
    {"id": "c1", "kind": "step_changed", "description": "s_model: peril_structure:motor-gb-2026h2@1 → @2"},
    {"id": "c2", "kind": "table_repointed", "description": "s_age: rate_table:motor-driver-age-relativity@5 → @6"},
    {"id": "c3", "kind": "step_changed", "description": "s_minprem: min_premium 26000 → 28000"}
  ],
  "change_groups": [{"name": "models", "changes": ["c1"]}, {"name": "age curve", "changes": ["c2"]},
                    {"name": "minimum premium", "changes": ["c3"]}],
  "attribution": [
    {"group": "models", "shapley_minor": 594_700_00, "isolated_minor": 571_000_00,
     "cumulative_minor": 571_000_00, "mean_change_pct": 1.42, "cumulative_change_pct": 1.36},
    {"group": "age curve", "shapley_minor": -129_800_00, "isolated_minor": -131_200_00,
     "cumulative_minor": -128_100_00, "mean_change_pct": -0.31, "cumulative_change_pct": -0.31},
    {"group": "minimum premium", "shapley_minor": 351_300_00, "isolated_minor": 322_400_00,
     "cumulative_minor": 373_300_00, "mean_change_pct": 0.84, "cumulative_change_pct": 0.89}
  ],
  "attribution_summary": {"method": "shapley", "total_change_minor": 816_200_00,
                          "residual_minor": 54_000_00, "order_sensitivity_lower_bound": null,
                          "residual_share": null, "orders_sampled": null,
                          "subset_bundle_count": 8, "subset_bundle_hashes": ["sha256:…"],
                          "subset_valuation": "rerate", "replay_fell_back": false},
  "largest_movers_blob": "blob:sha256:…",
  "errors": []
}
```

*(Amended 2026-10-04, WK-673 Slice 2, `RL-1402`: the run's arithmetic, for FR-263 and FR-264. The example's top band label, its `exposure_years`, `by_ladder_rung` and `errors` were changed and `outcomes` added to match.)*

**Outcomes, and the two sets.** `policy_count` counts every portfolio row. `outcomes` counts each policy once by its two outcomes: `quoted_both`, `quoted_to_declined`, `declined_to_quoted`, `declined_both` and `error` (an `"error"` row in either pass), which sum to `policy_count`; `zero_baseline`, the quoted-both policies whose baseline payable premium is 0; and `negative_baseline`, those whose baseline payable premium is below 0. The **compared set** is the quoted-both policies. The **banded set** is the compared policies whose baseline payable premium is above 0: the compared set less its `zero_baseline` and `negative_baseline` policies, so Σ `distribution[].policies` = `quoted_both` − `zero_baseline` − `negative_baseline`. A negative baseline is a value a Rating Version can return, not an error (no-negative-premium is a Regression Suite property, not a runtime bound): it stays in the compared set and enters no band and no mover. `errors` has one item for each error code with at least one policy, in code order: an `error` policy is counted once, under its baseline pass's `error_code` where that pass errored and otherwise under its candidate pass's, so the counts sum to `outcomes.error`; `sample` holds up to 10 of those policies as `{"quote_id": …}`, the first 10 by `quote_id`.

**Money and ratios.** Every money figure is a sum over the compared set of the `payable_premium` rung's `value_minor`, as integers (FR-1397's arithmetic, NFR-496). A policy's change is its candidate minus its baseline payable premium. A mean or total change in percent over a group is the group's Σ change ÷ Σ baseline × 100, computed as an exact rational of the integers and rounded once to 2 decimal places, half-even. An `exposure_share` is the group's Σ `exposure_years` ÷ the Σ over the set the group is part of, rounded once to 6 places, half-even. A ratio whose denominator is 0 is `null`. `exposure_years` is the exact decimal sum over every policy, rounded once to 6 places, half-even. `totals`, `by_segment` and `by_ladder_rung` cover the compared set.

**Bands and movers** cover the banded set, because they need a per-policy percentage change, (candidate − baseline) ÷ baseline × 100, exactly. `band_edges_pct` (required; decimals; at least one; strictly increasing) cuts it into half-open bands `[lo, hi)`, labelled "< e₀%", "eᵢ% to eᵢ₊₁%" and "≥ eₙ%", each edge printed as its plain decimal string with no exponent and no trailing zeros, with "+" before a positive edge. Every band is listed, in edge order; an empty band has `policies` 0. A **mover** is a banded policy whose percentage change has an absolute value of at least `mover_threshold_pct` (required; a positive decimal), decided exactly on the integers. Movers are ordered by the absolute percentage change, largest first, then by the absolute change in minor units, largest first, then by `quote_id` in code-point order.

**Rungs.** A compared policy's **originating rung** is the first rung, in the ladder's fixed order (FR-247, FR-252), that differs between its two ladders: present in one ladder only, or with a different `value_minor`, or with a different `unrounded_minor` compared as decimal values. A policy with no differing rung has a change of 0. `by_ladder_rung` has one row for each rung that originates at least one compared policy's change, in ladder order; its `contribution_pct` is those policies' Σ change ÷ the compared set's Σ baseline × 100. The integer sums of change by originating rung add up exactly to `candidate_premium_minor − baseline_premium_minor`.

**Segments.** Each name in `segments` (distinct) is a portfolio column of a string, categorical, integer, boolean or date dtype; any other dtype, or an absent column, is refused with `VALIDATION_FAILED` naming the column. `by_segment` has one row per segment and level, in `segments` order, then by level in the value's own order (strings by code point, integers by value, `false` before `true`, dates by date), with the null level last. The level is the value as a string (an integer in decimal, a date in ISO form, a boolean as `true` or `false`), or `null`: null values form one level and are never dropped.

**`exposure_years` as read.** §4.8's "decimal" is how the column is read: an integer or decimal dtype exactly; a float dtype row by row as the decimal of the value rounded to 6 places (FR-62's rule); a NaN or infinite value is refused with the nulls; any other dtype is refused with `VALIDATION_FAILED` naming the column and its dtype.

### 4.7 `RegressionSuite` and `GoldenQuote`

```json
{
  "slug": "motor-gb-core",
  "version": 4,
  "algorithm_slug": "motor-gb",
  "change_note": "young-driver-london re-based to the 2026H2 relativities",
  "content_hash": "sha256:…",
  "created_at": "2026-09-28T09:00:00Z",
  "created_by": "…principal uuid…",
  "golden_quotes": [
    {"name": "young-driver-london", "context": {"…QuoteContext…"},
     "expected": {"payable_premium_minor": 112_480, "outcome": "quoted"},
     "tolerance": {"money_minor": 0},
     "note": null}
  ],
  "properties": [
    {"name": "premium-positive", "check": {"kind": "premium_positive"}},
    {"name": "monotone-in-age", "check": {"kind": "monotone", "input": "driver_age",
      "direction": "decreasing", "strict": false, "lower": "25", "upper": "70"}},
    {"name": "no-null-output", "check": {"kind": "no_null_output"}},
    {"name": "ladder-reconciles", "check": {"kind": "ladder_reconciles"}},
    {"name": "premium-bounded", "check": {"kind": "premium_bounded", "lower_minor": 28000, "upper_minor": 2500000}}
  ],
  "generation": {"cases": 5000, "seed": 20260814, "strategy": "input_contract_sampling"}
}
```

*(Corrected 2026-09-28, `RL-1172` item 3c; the deputy's F4 assertion-language ruling;
`PL-1189`.)* The free-text `assertion` strings are replaced by a structured union of
FR-261's five classes, discriminated on `check.kind`: `premium_positive`, `monotone`
(`input`, `direction`, `strict`, optional `lower`/`upper` as decimal strings),
`no_null_output`, `ladder_reconciles` (FR-248) and `premium_bounded` (`lower_minor`
and/or `upper_minor`, at least one). This artifact stores them; WK-672 Slice 3 evaluates
them. The earlier example's relative bound (`20 * risk_premium_minor`) is not one of the
five classes and is dropped; a bound is absolute, in minor units. `expected` compares
`payable_premium_minor` (the `payable_premium` ladder rung's `value_minor`) and `outcome`
only, never `timing_ms` (RL-931). `payable_premium_minor` is null exactly when `outcome`
is not `quoted`. `content_hash` is `sha256:` over the canonical JSON (sorted keys, no
whitespace) of the content fields — `algorithm_slug`, `golden_quotes`, `properties`,
`generation` — so any `expected` or `tolerance` edit changes it. A suite is versioned
(`POST /api/v1/regression-suites/{slug}/versions`, §5.1), bound to one Rating Algorithm by
`algorithm_slug` (one suite per algorithm per workspace), not approvable, and every read
is permission-checked because a golden quote's `context` is a full quote input (NFR-499).
*(Added 2026-09-28, `PL-1189`, the lead's ruling on a plan gap.)* `regression_suite` is an
artifact type (`00` ID-3) so that the evidence can pin `regression_suite:{slug}@{version}`
by reference. It is a **reference only**: it has no approval policy entry and no creation
action in the approval module, so an approval request naming one is refused, and the
approval route never resolves one.

### 4.8 `score_batch`'s frame contract

*(Added 2026-08-30, WK-671 Task 3A follow-up — RL-923,
`docs/rulings/INDEX.md#2026-08-30-w11-reopen-scope-and-batch-frame-contract-rulingsmd`. Mints no
requirement id: it documents a shape FR-253, FR-254 and `05-monitoring.md`
FR-317 already reach, not a new capability.)*

§5.2's `score_batch(bundle: CompiledBundle, frame: pl.LazyFrame, ...) -> pl.LazyFrame`
fixes the function's signature only. Nothing else in this suite fixes a row shape for it,
and this is the first of the four `pl.LazyFrame`-taking/returning signatures §5.2
publishes (`score_batch`'s `frame`, `dislocate`'s `portfolio`, `attribute`'s `portfolio`,
`score_batch`'s own return) to become real — `dislocate` and `attribute` are unbuilt. This
subsection is written so it can hold the portfolio frame's schema when WK-673 designs it; it
does not design that schema now. *(Superseded in part 2026-10-03: the portfolio frame's schema is designed in "The portfolio frame (WK-673)" below, `RL-1394`.)*

**Not a `model-schema` artifact.** No document under `docs/contracts/` defines a tabular
row schema, and Polars column layouts have no generator, no `scripts/generate-contracts.py
--check` drift check, and no frontend consumer — the seam ADR-704 defines does not carry
this. Publishing it here, and guarding it with a test asserting every `ScoringResult` field
is either a mapped column or a named exclusion
(`packages/pricing-core/tests/test_rating_score_batch.py`), is `CLAUDE.md` §2's "a shape
defined twice will diverge" enforced by a test rather than by a generator, because there is
no generator to enforce it and inventing one is an ADR-scale decision this subsection does
not make.

**Input row.** One column per reserved name below, plus one column per name in
`bundle.algorithm.input_contract` (`model_schema.rating.InputContractField.name`) —
forwarded into `QuoteContext.inputs` verbatim, tolerating extra columns the algorithm does
not declare, exactly as `_validate_inputs` already tolerates extra `ctx.inputs` keys.

| Column | Type | Notes |
|---|---|---|
| `quote_id` | string, nullable | FR-253's "quote key"; `ScoringResult` carries no such field (RL-857 §3), so this is carried through rather than read off the result |
| `purpose` | string | one of `QuotePurpose`'s five members |
| `effective_date` | string | ISO date |
| `rating_version_ref` | string | the canonical `ArtifactRef` string (`"{type}:{slug}@{version}"`) |

**`rating_version_ref` is a `score_batch` input column, and Task 3B stamps it — never
carries it through from the input dataset.** `CompiledBundle` (`pricing_core.rating.
runtime`) carries `content_hash`, `decision`, `algorithm`, `boosters`, never a Rating
Version reference, so `score_batch` cannot itself verify a row's `rating_version_ref`
against the `bundle` it is scoring with. For `score_one` this never diverges: the caller
resolves one ref into one bundle for one call, so the two agree by construction. For
`score_batch`, the frame and the bundle are supplied independently, so that construction is
gone unless the handler restores it. **Task 3B resolves the reference once per Rating
Version it loops (FR-253's "one or more") and stamps that resolved ref into every row
of the frame it builds for that bundle — it does not read `rating_version_ref` from the
Dataset Version being scored.** A build that accepts the ref from the input dataset
produces a parquet attributing premiums to a Rating Version that did not compute them.

**Output row.** A projection of `ScoringResult`
(`packages/model-schema/src/model_schema/scoring.py`), plus `quote_id` and two error
columns; `trace` and `timing_ms` are excluded.

| Column | Type | `ScoringResult` field | Notes |
|---|---|---|---|
| `quote_id` | string, nullable | — | carried through from the input row |
| `outcome` | string | `outcome` | `"quoted"`, `"declined"`, or `"error"` — all three are `ScoringOutcome`'s own members, `"error"` included; `score_batch` is simply the first caller to produce it |
| `rating_version_ref` | string | `rating_version_ref` | the resolved ref Task 3B stamped (above) |
| `bundle_hash` | string | `bundle_hash` | |
| `premium_ladder_json` | string, nullable | `premium_ladder` | the rung list, pre-serialised to JSON text (a nested `LadderRung` list has no flat columnar form); `null` on an `"error"` row |
| `outputs_json` | string, nullable | `outputs` | pre-serialised to JSON text, total over every `AlgorithmOutput.type` this path can produce (`money_minor` as a JSON number, `decimal` as a JSON string — never a JSON number, so an exact `Decimal` and a lossy `float` cannot be confused reading the column back) and refusing, not stringifying, anything else; `null` on an `"error"` row |
| `decline_reasons` | list of strings | `decline_reasons` | empty on an `"error"` row |
| `error_code` | string, nullable | — | populated only on an `"error"` row, the `_raise_named` convention's code (`INPUT_CONTRACT_VIOLATION`, `MODEL_CALL_FAILED`, …) |
| `error_message` | string, nullable | — | populated only on an `"error"` row |

**Two `ScoringResult` fields are deliberately excluded, and no third:** `trace` (batch
requests no engine trace — RL-890 gives `score_batch` no sampling parameter, so this is
always absent) and `timing_ms` (a per-call wall-clock breakdown that means nothing
aggregated across a chunk).

**One failing row becomes an `"error"` output row rather than aborting the chunk it is
in** — the structural half of FR-255 ("does not abort on individual failures") a
chunked transform has to provide regardless of which task is charged with the requirement
id. The threshold policy that decides whether the *run* aborts, and the per-category
counting and sampling FR-255 also names, are Task 3B's, reading `error_code` off this
column.

#### The portfolio frame (WK-673, added 2026-10-03)

*(Added 2026-10-03, WK-673 Slice 1, PL-1395; the ruling `RL-1394`; `RL-1361` §E for pass-through.)* `dislocate`'s and `attribute`'s `portfolio` is one row per policy of a portfolio Dataset Version.

| Column | Type | Rule |
|---|---|---|
| `quote_id` | string | required, non-null and unique: the policy's identity, the key on which the baseline and candidate passes are joined, and the drill-down key for movers |
| `exposure_years` | decimal | required, non-null and never negative; zero allowed; never read as 0 when null (`RL-1361` §E). The weight for exposure shares (FR-263) and for FR-231's per-cell weights |
| each name in either bundle's `input_contract` | as declared | the algorithm inputs |

**A portfolio that breaks this schema is refused before any rating, with `VALIDATION_FAILED`,** naming the column and the count of offending rows: a missing, null or duplicated `quote_id`; a missing, null or negative `exposure_years`; a column named `purpose`, `effective_date` or `rating_version_ref`. A fault in one row's algorithm inputs is not a frame refusal: it is that row's own error, as below.

**`purpose`, `effective_date` and `rating_version_ref` are stamped, never read from the portfolio.** `DislocationSpec.purpose` (`new_business` or `renewal`) and `DislocationSpec.as_at` (an ISO date) are written into every row of every pass as `purpose` and `effective_date`. The baseline pass and the candidate pass stamp their own Rating Version's `rating_version_ref`, as this subsection requires of every `score_batch` frame. An attribution subset pass stamps the **baseline's** `rating_version_ref`, because a subset bundle has no Rating Version (`03` §3.9) and `score_batch` requires a reference on every row; its output rows are scratch inputs to attribution, never persisted or returned as scoring results, and the subset is identified by their `bundle_hash`, never by that reference. A `mid_term_adjustment`, `cancellation` or `what_if` row therefore cannot occur in a run; when FR-217's inlining is built, admitting the first two is a change to this subsection (FR-218).

**Every other column passes through the reader** and stays available for slicing by any Factor (FR-264), for exposure weighting, for drill-down, and for resolving a Factor's source columns (FR-231, `RL-1361`). **It never reaches the engine.** Each scoring pass — the baseline, the candidate and every attribution subset — rates a frame of the stamped columns, `quote_id`, and exactly the names in **that pass's own bundle's** `input_contract`; the other columns are joined back to the scored rows by `quote_id`. A name a bundle declares but the portfolio lacks is FR-213's missing input, written as an `"error"` row with `INPUT_CONTRACT_VIOLATION`, as `score_batch` already does. `score_batch`'s own tolerance of extra columns (above) is unchanged: this projection is `dislocate`'s and `attribute`'s, because forwarding an undeclared column lets an undeclared read resolve from the book (`FD-1374`) and lets a column with a billing name refuse every row (FR-252), so a run's result would depend on columns no contract names.

### 4.9 `RegressionRun`

*(Added 2026-09-28, WK-672 Slice 1, `PL-1177`. Mints no requirement id: it documents the
execution record that FR-260's promotion check and FR-261's property run produce, matching
`docs/contracts/schemas/regression-run.schema.json`'s `RegressionRun` definition, which
predates this text. That contract is the hand-authored Phase 0 draft; `RL-1172` item 3c
makes `RegressionRun` a `model-schema` artifact in the slice that first builds it, WK-672
Slice 3, and this subsection then describes the generated shape.)* *(Amended 2026-09-28,
WK-672 Slice 2, `PL-1189`: the citation moved from `regression-suite.schema.json` to
`regression-run.schema.json`, because Slice 2 split that file — the suite became a
generated `model-schema` artifact and the run definition moved, unchanged, to its own
hand-authored file.)*

```json
{
  "suite_ref": "regression_suite:motor-gb-core@3",
  "suite_content_hash": "sha256:5b1f3a0c7d2e94a86c01d4f7e3b9a2c5d8e6f0a1b3c4d5e6f708192a3b4c5d6e",
  "rating_version_ref": "rating_version:motor-gb@27",
  "bundle_hash": "sha256:86d0cef0fbc4111163c63591ad555b6afc8bae35ca532846d51e14a6f08a77fe",
  "job_id": "ad48274d-de75-4385-b966-b9df9579b63e",
  "started_at": "2026-09-28T09:00:00Z",
  "finished_at": "2026-09-28T09:00:04Z",
  "overall": "fail",
  "generation": {"seed": 20260928, "cases": 5000, "hypothesis_version": "6.165.7"},
  "cases_blob": {"sha256": "0c9e4d1b7a3f58e2d6b0a91c4f7e3d2a8b5c6d7e8f901a2b3c4d5e6f708192a3", "bytes": 1048576, "media_type": "application/json"},
  "golden_results": [
    {"name": "young-driver-london", "status": "fail",
     "expected_minor": 112480, "actual_minor": 112900, "difference_minor": 420}
  ],
  "property_results": [
    {"name": "premium_positive", "status": "pass", "cases_run": 5000},
    {"name": "monotone_in_age", "status": "fail", "cases_run": 5000,
     "counterexample": {"age": 25}, "counterexample_minimal": false,
     "shrink": "stopped_on_limit", "error_code": "PROPERTY_ASSERTION_FAILED",
     "grid": "uniform+sampled", "counterexample_points": [37, 58]}
  ]
}
```

*(Amended 2026-09-28, WK-672 Slice 3, `PL-1205`: the example gains `suite_ref` in place of
`suite_slug`, `suite_content_hash`, `generation`, `cases_blob`, and on `property_results[]`
`shrink`, `counterexample_minimal`, `grid` (a `monotone` property's grid kind, `uniform+sampled`), `counterexample_points` (the two adjacent grid values of a `monotone` counterexample) and, on a failing entry, `error_code`. `cases_blob` is a
`BlobRef` to the run's case log (`FR-1221`). `shrink` is `completed` or `stopped_on_limit`;
a counterexample whose shrink stopped on a limit is reported as **unminimised**
(`counterexample_minimal: false`), never presented as minimal. A `MONOTONE_NO_COMPARABLE_PAIRS` failure (`error_code`, FR-261) has no counterexample and carries `shrink: completed`: nothing is shrunk, and `completed` there means only that there is nothing further to minimise.)*

`overall == "fail"` blocks promotion (FR-260). A `golden_results` entry's `status` is
`"fail"` when `difference_minor` exceeds the golden quote's declared tolerance (default:
exact — zero — for money, FR-260's own text). A `property_results` entry's
`counterexample`, when present, is the failing case reduced to a minimal one an actuary can
read, as the contract's own description states; how it is generated and reduced is
`pricing-core`'s `rating/testing.py` (§5.2), built in Slice 3. A Rating Version's approval
evidence reads the run whose `bundle_hash` equals the version's current bundle hash
(`RL-1172` item 4).

### 4.10 `ScoreComparison`

*(Added 2026-09-29, WK-672 Slice 4, `PL-1213`; FR-262. The shapes are `model-schema`'s: `ScoreCompareRequest`, `StepChange`, `TraceDiff`, `ScoreComparison`, generated as `score-comparison.schema.json`. They are distinct from FR-219's structural `AlgorithmDiff`, which compares two algorithm definitions; these describe two executed traces.)*

**Request.** One Quote Context and two Rating Version references, so the two sides cannot drift into two different quotes. A `context` that carries its own `options.rating_version_ref` is refused (422): `base` and `comparison` name the versions.

```json
{
  "context": {"purpose": "new_business", "quoted_at": "2026-08-30T09:00:00Z",
              "effective_date": "2026-09-01", "inputs": {"premium_in": 1000}},
  "base": "rating_version:motor-gb@27",
  "comparison": "rating_version:motor-gb@28"
}
```

**Response.** Both `ScoringResult`s, each traced, and the diff of their traces:

```json
{
  "base": {"...": "a traced ScoringResult"},
  "comparison": {"...": "a traced ScoringResult"},
  "diff": {
    "steps": [
      {"step_id": "s_rate", "change": "changed", "changed_fields": ["produced"],
       "own_change": true, "base": {"...": "TraceStep"}, "comparison": {"...": "TraceStep"}},
      {"step_id": "s_total", "change": "changed", "changed_fields": ["consumed", "produced"],
       "own_change": false, "base": {"...": "TraceStep"}, "comparison": {"...": "TraceStep"}}
    ],
    "unchanged": 11
  }
}
```

- `change` is `added`, `removed` or `changed`; `changed_fields` is a subset of `type`, `label`, `consumed`, `produced`, `matched`, `violation`; `base` or `comparison` is `null` on the side where the step is missing.
- **Matching and comparing.** Steps match by `step_id`. `elapsed_us` is recorded and never compared. Values compare as canonical JSON, so `1`, `1.0` and `true` are three different values. `steps` lists base steps in base order, then added steps in comparison order. A duplicate `step_id` in one trace is a `ValueError`.
- **`own_change`.** True for an added or removed step, and for a changed step whose `consumed` is identical on both sides (the step saw the same inputs and behaved differently). A changed rate table moves every downstream step's `consumed`, so those steps are listed with `own_change: false` and the edited step is the one entry with `own_change: true`.
- **`own_change: false` means "no own change attributable from the traces".** It never means "unchanged" or "not edited".
- **Known limit (auditor-b F5).** `own_change` is derived from `consumed`, so a downstream step that is itself edited *and* whose input moved reads `own_change: false`: the diff reports the change but cannot separate the two causes. The one-step acceptance of `RL-1172` §5 holds for a single edit. OQ-1231 (§10) asks whether `own_change` should come from step-definition equality instead. *(2026-09-29: this limit ends when WK-675 delivers `RL-1261`, below.)*
- **`own_change` from step definitions** *(amended 2026-09-29, `RL-1261`, deciding `OQ-1231` (b); owner WK-675, not yet built)*. For a step present on both sides and changed in the traces, `own_change` is true exactly when its definition differs between the two compiled algorithms, as FR-219's `diff_algorithms` reports it: an entry in its `changed_steps` for that `step_id` whose field is not `note` (`note` is excluded at this call site; `diff_algorithms` keeps counting it). An added or removed step stays true. Each step carries its own pinned refs, so a changed rate table is a changed `rate_table_ref` on the step that reads it. `diff_traces` takes both algorithms as well as both traces. The request and response shapes do not change. Until WK-675 delivers it, the trace-derived rule above stays in force.

### 4.11 `SubGraph`

*(Added 2026-10-01, WK-1250 Slice 1, `PL-1325`; FR-217's artifact limb, FR-227 at create. Ruled by `RL-1309`. The shapes are `model-schema`'s: `SubGraphInputPort`, `SubGraphBody`, `SubGraphCreate` and `SubGraph`, generated as `sub-graph.schema.json`, `sub-graph-create.schema.json` and `sub-graph-body.schema.json`. The pin, the inlining and the mount port map are Slice 2's; FR-218's purpose mount is Slice 3's.)* *(Amended 2026-10-09, WK-1250 Slice 2, `SL-1340`, `RL-1309` and WK-1250 Slice 2's decisions: the pin (`Pins.sub_graphs`), the port map and the inlining landed; FR-218's purpose mount is still Slice 3's, and `RL-1242`'s interim refusal stands. Compile refuses a mount whose sub-graph is not pinned (`RATING_VERSION_UNPINNED`), a fragment reference that is not among the Rating Version's pins (`RATING_VERSION_UNPINNED`), an unmapped or undeclared port (`RATING_GRAPH_UNRESOLVED_REF`), an incompatible input type (`RATING_TYPE_MISMATCH`), and a nested mount, a `mount_point` that breaks its pattern or clashes, or a namespaced name equal to a parent name (`VALIDATION_FAILED`). FR-216, FR-274, FR-275 and FR-276 run over the inlined algorithm.)*

A Sub-graph Version is a stored, immutable fragment of a Rating Algorithm, addressed as `sub_graph:<slug>@<version>`. It is **not a Governed Artifact** (`RL-1309` DP-1): it has no status and no approval lifecycle of its own. Its change reaches approval inside the Rating Version that pins it, and every version carries a required, non-empty `change_note`.

```json
{
  "slug": "ncd-ladder",
  "version": 4,
  "inputs": [{"name": "ncd_years", "type": "int"}],
  "outputs": [{"name": "ncd_factor", "type": "relativity", "required": true}],
  "steps": [
    {"step_id": "s_ncd", "type": "table", "label": "NCD ladder",
     "rate_table_ref": "rate_table:ncd@2", "key_expr": ["ncd_years"],
     "consumes": "ncd_years", "produces": "ncd_factor"}
  ],
  "change_note": "Step-back after one claim is two years, not three."
}
```

- **Typed ports** (`RL-1309` DP-3). An input port is a `name` and a `type` (a result type, never `float`, FR-227). An output port is an `AlgorithmOutput` (`name`, `type`, `required`): the same shape and result-type vocabulary as a Rating Algorithm's outputs, with no second vocabulary. The fragment's own names are namespaced when a parent inlines it (Slice 2).
- **No `input` or `output` steps.** The ports replace them. A fragment carrying either step type is refused.
- **Mounts nothing** (`RL-1309` DP-4). The shape has no `sub_graphs` field and is `extra="forbid"`, so a fragment cannot mount another: depth is 1.
- **Inlining and namespacing** *(added 2026-10-09, WK-1250 Slice 2, RL 9586 (working id))*. At compile, a pinned mount is inlined at its `mount_point` (FR-217). Every fragment `step_id`, and every fragment name that is not a mapped port, becomes `<mount_point>__<name>`: `__`, not `/`, because `/` is FR-244's division operator. A mapped input port's name becomes the parent value it is mapped to, and a mapped output port's name becomes the parent name it is mapped to. Names are renamed by FR-244 token in every field that holds one (`consumes`, `produces`, `key_expr`, `expr`, `condition`, the values of `clamp_bounds` and `feature_map`), never by substring. A `mount_point` matches `^[A-Za-z][A-Za-z0-9_]*$` and contains no `__`. Mounted under §4.1's example, this fragment's step `s_ncd` becomes `s_ncd__s_ncd`; it consumes the parent's `ncd_years` and produces the parent's `ncd_factor`. Compile refuses an unmapped or undeclared port (`RATING_GRAPH_UNRESOLVED_REF`), an incompatible input type (`RATING_TYPE_MISMATCH`), a mount whose sub-graph is not pinned (`RATING_VERSION_UNPINNED`), and a `mount_point` that breaks the pattern, clashes, or produces a namespaced name equal to a parent name, step id or engine-derived key (`VALIDATION_FAILED`). A mount whose fragment writes its own input port is refused (`VALIDATION_FAILED`); revisit if an algorithm needs it *(ruled 2026-10-09, WK-1250 Slice 2)*.
- **Graph invariants** (FR-212, restated for ports). Every name a step consumes is an input port or is produced by a step (`RATING_GRAPH_UNRESOLVED_REF`). Every output port is produced by a step (`RATING_GRAPH_UNRESOLVED_REF`: a port is a reference to a named value). An input port is the first producer of its name; a step that produces it without consuming it is refused, while a step that consumes it and re-produces it (a clamp chain) is accepted. A step reachable from no input port and contributing to no output port is refused. A cycle is refused (`RATING_GRAPH_CYCLIC`). A duplicate `step_id` is refused. These other refusals are `VALIDATION_FAILED`.
- **Result types at create** (FR-227; `RL-1309` DP-S1-4). An output port whose declared type is incompatible with its producing step's result type is refused with `RATING_TYPE_MISMATCH`, naming the producing step and the port. Only producers whose type is known at save are checked: an `expression` step's `result_type` and an input port's declared type. An output produced by a `table`, `lookup` or `model_call` step is not checked at create, as for an algorithm today; its type is known only against the pinned artifact, at compile.
- **Versions are immutable** (`00` FR-4). The server numbers versions: the current maximum plus one. There is no update and no delete. Every write records an Audit Event `sub_graph.created` with `entity_ref` `sub_graph:<slug>@<version>`, in the same transaction (`06` FR-368).

### 4.12 `Deployment`

*(Added 2026-10-03, WK-674 Slice 2, `PL-1392`; FR-267, and FR-272's Audit Event limb for deploy. The Deployment Request follows `RL-1301` A, the promotion skip `RL-1296`, the Environment's immutable slug `RL-1301` A.6. The shapes are `model-schema`'s: `Deployment`, `DeploymentRequest` and `PromotionSkip`, generated as `deployment.schema.json` and `deployment-request.schema.json`. The Environment is `07` §4.2's, declared once there.)*

A Deployment binds one `approved` Rating Version to one Environment at a point in time. It is a record, not a Governed Artifact: it has no status and no approval lifecycle of its own. Approval attaches to the **Deployment Request** that precedes it, below.

```json
{
  "id": "6f1c0e52-8a43-4d3b-9b0e-2f6a7c1d9e10",
  "workspace_id": "0c6e8f0a-5d21-4b7e-8d62-1a9b3c4d5e6f",
  "environment": "prod",
  "rating_version_ref": "rating_version:motor-gb@27",
  "bundle_hash": "sha256:9f2c…",
  "deployed_by": "3b8e4d7a-1c52-4f09-a6d3-7e5b2c8f1a04",
  "deployed_at": "2026-10-01T06:00:00Z",
  "reason": "Annual rate review, effective 1 November",
  "deployment_request_ref": "deployment:prod@3"
}
```

- **`environment` is the Environment's slug** (`07` §4.2), which a rename cannot change (`RL-1301` A.6). `bundle_hash` is the Rating Version's compiled Bundle hash at the time of the deploy (FR-239). `deployment_request_ref` is the approved Deployment Request this Deployment executed, and is `null` only for a target that has no `deployment` entry in the Approval Policy (`06` §4.2; `RL-1301` A.5).
- **Append-only.** A Deployment is never updated in place and never deleted (`00` FR-4). The live Deployment of an Environment is derived from these rows, never stored a second time (`07` §4.2).
- **`approved` Rating Versions only** (FR-238). A request to deploy a version in any other status is refused.
- **Compiled Rating Versions only** (FR-239; `RL-1401`). A version whose `bundle` metadata is absent, or has no `content_hash`, has no Bundle hash to record and is refused with 409 `BUNDLE_COMPILE_FAILED`, at Deployment Request submission and at deploy. It cannot be compiled once it has left `draft` (`RL-1379`). The way forward is a new draft version.
- **Not into a retired Environment** (`07` FR-428; `RL-1301` A.6; `RL-1401`). A deploy or a Deployment Request whose target Environment is retired is refused with 409 `VALIDATION_FAILED`, naming the slug and when it was retired. The refusal comes after the permission check and before the Rating Version is read. An unknown slug is 404 `NOT_FOUND`. A request approved before its target was retired is refused when it is executed.
- **A Rating Version is the only deployable subject.** A `sub_graph` reference, or any reference whose type is not `rating_version`, is refused. A Sub-graph reaches a deployment only inside the Rating Version that pins it (§4.11).
- **Audit actions this Work emits**, each named here once so that no later slice appends to the catalogue. **The deployment request:** `deployment_request.created` (WK-674 Slice 2: a Deployment Request is written and submitted; `before` `null`, `after` the request with its pins and its pinned evidence; `entity_ref` exactly the request's reference `deployment:<environment slug>@<n>`; the submitting Principal as actor; in the same transaction as the row and its approval request). Its actor is the request's Author for `06` FR-353, as amended 2026-10-03 (`RL-1401`). **FR-272's four:** `deployment.created` (WK-674 Slice 2: a Deployment row is written, `before` the previous live Deployment of the Environment or `null`, `after` this one, in the same transaction as the row); `deployment.rolled_back` (Slice 5, FR-269); `deployment.routing_changed` and `deployment.shadow_configured` (Slice 6, FR-270 and FR-271). The `entity_ref` of each of FR-272's four names the Deployment or the Environment it changes. **The Environment (WK-674 Slice 2, added 2026-10-04):** `environment.created` (`before` `null`, `after` the Environment), `environment.updated` and `environment.retired` (`before` and `after` the Environment); the `entity_ref` of each is `environment:<slug>`.

#### Deployment Request

An Environment may be gated by a `deployment` entry in the Approval Policy (`06` §4.2; `prod` by default). A deploy into a gated Environment names an **approved Deployment Request**. A Deployment Request is an artifact owned by this module (`RL-1301` A.1, DP-S2-2).

- **Reference form** `deployment:<environment slug>@<n>`, for example `deployment:prod@3`: the third request into `prod`. The slug is the target Environment's immutable slug, so a reference never changes its meaning; the version is monotone per Environment (`00` ID-2). `deployment` is a member of the artifact reference types (`ARTIFACT_TYPES` in `model-schema`; `docs/contracts/schemas/common/artifact-ref.schema.json` carries the same list), and an approval request for a Deployment Request carries `artifact_type: "deployment"`.
- **Pins.** The request pins the approved Rating Version it deploys and the target Environment's identity. It is the subject of the `deployment` approval request, whose `environment` is the Environment's slug.
- **Two pinned evidence items**, written once at submission and never updated (FR-356, `00` FR-4), the floor of `06` FR-364: `rating_version_approval`, the decided approval request of the pinned Rating Version; and `uat_deployment`, the predecessor item, which is **either** the id of the successful Deployment of that Rating Version in the predecessor Environment, **or** a `PromotionSkip` (`skipped_environment`, and a `reason` that is not empty after trimming). A skip is valid only where the target's environment-qualified `deployment` entry lists the skipped Environment (`RL-1296`; `07` FR-429). **A gated target with no predecessor** — an Environment whose `requires_prior_environment` is `null` and which a `deployment` entry names — has no predecessor item to pin, so every Deployment Request into it is refused with 422 `EVIDENCE_INCOMPLETE` (`07` FR-429; `06` FR-364: the floor kind is never removed). The refusal names the remedy: remove the entry, which makes the target ungated (`RL-1301` A.5), because `requires_prior_environment` cannot be changed after creation. *(Added 2026-10-04, `RL-1404`.)*
- **The deploy route executes only an approved request.** It re-evaluates `07` FR-429's one predicate from the request's **pinned** evidence and never re-reads a changeable source. A request is executed once. A target with no `deployment` entry needs no request: the predicate then reads the predecessor's successful Deployment directly, and no skip is possible (`RL-1301` A.5). A deploy into such a target that names a `deployment_request_ref` is refused with 422 `VALIDATION_FAILED`, naming the Environment, and writes nothing: the Deployment would otherwise record a request it did not execute. *(Added 2026-10-04, `RL-1404`.)*
- **Submission** is `POST /api/v1/environments/{env}/deployment-requests` (§5.1), which writes the request and submits it through the generic approval path in one transaction. The Deployer permission (`deployment:promote`) is checked with the target Environment as the resource (`06` FR-345).


---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/rating-algorithms` | Create/version an algorithm (validated on save, FR-212) |
| `GET` | `/api/v1/rating-algorithms/{slug}@{version}/diff?against=` | Structural diff (FR-219) |
| `GET` | `/api/v1/rating-algorithms/{slug}@{version}` | Read one Rating Algorithm version (FR-1530); requires `rating:read`. **200** with a `RatingAlgorithm` (§4.1); 401; 403; **404** `NOT_FOUND` on an unknown version or another workspace's. **Added 2026-10-08** (`RL-1475`) |
| `POST` | `/api/v1/sub-graphs` | Create a Sub-graph (version 1) from a `SubGraphCreate`; requires `rating:write`. **201**; **409** `VALIDATION_FAILED` on an existing slug; **422** `RATING_GRAPH_CYCLIC`, `RATING_GRAPH_UNRESOLVED_REF`, `RATING_TYPE_MISMATCH` or `VALIDATION_FAILED` (FR-217, FR-227; §4.11). **Added 2026-10-01** (`PL-1325`) |
| `POST` | `/api/v1/sub-graphs/{slug}/versions` | New version of an existing Sub-graph from a `SubGraphBody`; requires `rating:write`. **201**; **404** `NOT_FOUND` on an unknown slug; **409** on a lost numbering race; the same 422 codes (FR-217). **Added 2026-10-01** (`PL-1325`) |
| `GET` | `/api/v1/sub-graphs/{slug}@{version}` | Read one Sub-graph version; requires `rating:read`; **404** `NOT_FOUND` on an unknown version or another workspace's (FR-217). **Added 2026-10-01** (`PL-1325`) |
| `GET` | `/api/v1/sub-graphs/{slug}/versions` | List a Sub-graph's versions, cursor-paginated; requires `rating:read` (FR-217). **Added 2026-10-01** (`PL-1325`) |
| `POST` | `/api/v1/rate-tables/{slug}/versions` | New Rate Table Version from manual cell edits, with a required change note (FR-229). This is the manual-editing path, and it follows the import route below: the request names the base version and carries the edited cells, and the response is a cell diff against that base for confirmation (FR-231). `confirm: true` re-computes the diff and creates the version. **Amended 2026-09-28** (`RL-1184` E5): this row named no request shape, and no route implements it (register F-W10-3). Owner: WK-675's editor slice. |
| `POST` | `/api/v1/rate-tables/{slug}/seed-from-model` | **201** Seed one Factor's relativities from a model (FR-230). The body is `{"model_ref", "factor", "change_note"}`; `factor` is required and is the Factor's slug, a key of the model's `relativities`. The seeded table has one key, bound by `factor_ref` to the Factor version the model pins. **422** `VALIDATION_FAILED` for a `factor` that names no relativity entry of the model (a continuous factor included), for a named entry with no pinned Factor of its slug, for two pinned Factors with that slug, and for a re-seed of a lineage bound to another Factor's slug; **404** `NOT_FOUND` for a pinned Factor id that does not resolve in the caller's workspace (`load_factors`) (**amended 2026-10-03, `RL-1361` sections A and D**); **422** `CONTROL_FACTOR_IN_RATEABLE_PATH` for a `factor` that names a `control`-intent Factor (FR-230, `02` FR-88) (**amended 2026-10-08, `RL-1470`, FD-1422**) |
| `POST` | `/api/v1/rate-tables/{slug}@{version}/bulk-operation` | Uplift / floor / cap / rebase on that version's cells → new version, operation + parameters recorded (FR-233) |
| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against=&portfolio=` | **200** Cell-level diff (FR-231), exposure-weighted when `portfolio` names a `validated` portfolio Dataset Version, with §4.2's coverage figures, read from the manifest of the query's stored cell artifact, the one the diff/cells row below pages, and no chunk; **202** with that row's `rate_table.diff_cells` Job and a `Location` header where the artifact is not yet stored, whatever `storage` either version has (FR-232, `07` §1.3 R1), the Job's parameters carrying `portfolio`; the same request then answers **200** from the manifest. The artifact is keyed, and a request during the key's Job answered, as on the diff/cells row, so a query's diff and its cells come from one Job. The 202's Job kind was `rate_table.diff` until 2026-10-05, a wire change: `rate_table.diff` stays a valid kind in `job.schema.json` and `JobKind` for existing Job rows, and this route no longer creates it. With `portfolio`, these are checked before the artifact is looked up and before any Job: **403** without `dataset:read`, the same for any id; **404** `NOT_FOUND` for a portfolio that is missing or in another workspace; **409** `DATASET_NOT_VALIDATED` for a `draft` or `archived` portfolio. **404** `NOT_FOUND` for a `factor_ref` or `banding_ref` that does not resolve, naming the key and the ref, also before any Job, whatever `storage` either version has, since resolving a ref reads no cell. A fault that depends on the portfolio's content is the Job's failure, never the first response: `VALIDATION_FAILED` naming the key, the column or the ref for an absent column, a non-numeric banded column, a resolution error, a null or negative exposure, or a portfolio that maps to no cell. A Job fails with the same codes (**amended 2026-10-05, `RL-1361`; the 202 condition, the artifact, the Job kind, the ref 404 and the content faults amended 2026-10-05, `RL-1442`, FD-1439**) |
| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff/cells?against=&portfolio=&limit=&cursor=` | **200** One cursor page of the diff's changed cells (FR-231), `Page[RateTableDiffCell]` (§4.2), read from the query's stored cell artifact: every cell the diff's `changed_cells` counts, ordered by key tuple (§4.2), with each cell's baseline and current value, absolute and relative change, and its exposure weight when `portfolio` names a `validated` portfolio Dataset Version, weighted as the diff row states. The pages together hold every changed cell: a page bounds one response, not the cells. Requires `rating:read`. `limit` is 1 to `MAX_LIMIT`, default `DEFAULT_LIMIT` (`00` §5.2); `next_cursor` is null on the last page; `total_estimate` is the diff's `changed_cells`, counted up to `COUNT_CAP`. **202** with a `rate_table.diff_cells` Job and a `Location` header where the query's cell artifact is not yet stored, whatever `storage` either version has (FR-232, `07` §1.3 R1): the Job writes every changed cell, in order, as content-addressed chunk blobs of a fixed cell count no smaller than `MAX_LIMIT`, and one manifest holding the chunks' sha256s in order, the total, and the query's `RateTableDiff` with both coverage figures; the same request then answers **200** with pages read from them. A page reads the manifest and the chunks its cursor range spans, at most two for every legal `limit`. While the key's Job is queued or running, a request answers **202** with that Job and its `Location`, never a second Job; after it fails, the next request answers **202** with a new Job, and the failed Job stays readable by its id; after it succeeds, with its artifact present, **200**. The artifact is keyed by the query's immutable identity, the table `slug` and the `version` of each side, `against` taken as the version it resolves to, and the `portfolio` Dataset Version's id (or no portfolio), so a page finds it without loading or hashing any cell; two versions with identical cells do not share an artifact. An artifact that cannot be found is computed again, never served from another query. `against` and `portfolio` are checked as on the diff row, before any cell is read and before any Job, whatever `storage` either version has: **404** `NOT_FOUND` for an unknown table, version or `against`; with `portfolio`, **403** without `dataset:read`, the same for any id, **404** `NOT_FOUND` for a portfolio that is missing or in another workspace, **409** `DATASET_NOT_VALIDATED` for a `draft` or `archived` portfolio, and **404** `NOT_FOUND` for a `factor_ref` or `banding_ref` that does not resolve. The diff row's portfolio faults that depend on the portfolio's content are the Job's failure, `VALIDATION_FAILED`, never the first response. **400** `VALIDATION_FAILED` for a cursor this API did not issue or one past the last cell; **422** `VALIDATION_FAILED` for a `limit` out of range. A Job fails with the same codes. This route adds no field to `RateTableDiff`. (**added 2026-10-05, `RL-1418`, FD-1358; the 202 condition, the artifact, the key, the Job in flight, the ref 404 and the content faults amended 2026-10-05, `RL-1442`, FD-1439**) |
| `GET` | `/api/v1/rate-tables/{slug}@{version}/export/csv` | Export cells to CSV (FR-235) |
| `GET` | `/api/v1/rate-tables/{slug}@{version}/export/xlsx` | Export cells to XLSX (FR-235) |
| `POST` | `/api/v1/rate-tables/{slug}@{version}/import` | Import CSV/XLSX → returns a diff vs the addressed version for confirmation; `confirm: true` re-computes the diff and creates the version (FR-235) |
| `POST` | `/api/v1/rating-versions` | Create a draft Rating Version with pins (FR-237). The body takes `slug`, `dataset_version_id`, `model_ref` and, optionally, `algorithm_ref` (a `rating_algorithm` ref), `pins` (§4.3's `Pins`) and `model_reference_mode`; a ref of the wrong type in any of them is **422** `VALIDATION_FAILED`. Resolvability and maturity are checked at compile (FR-240), and a version created without `algorithm_ref` or `pins` is refused there with `RATING_VERSION_UNPINNED`. *(Amended 2026-10-05, RL-1428, FD-1421.)* |
| `GET` | `/api/v1/rating-versions/{slug}@{version}` | Read one Rating Version by its `slug@version` (FR-1531); requires `rating:read`. **200** with a `RatingVersion` (§4.3); 401; 403; **404** `NOT_FOUND` on an unknown version or another workspace's. Registered before the `{id}` read, which would otherwise take the request. **Added 2026-10-08** (`RL-1473`) |
| `GET` | `/api/v1/rating-versions/{id}` | Read one Rating Version by `id`, the handle the `{id}` routes below take (FR-237); requires `rating:read`. **200** with a `RatingVersion` (§4.3); 401; 403; **404** `NOT_FOUND` on an unknown id or another workspace's. Built in Phase 1b (FR-440); records an existing route, 2026-09-30; declared 2026-10-08 (`RL-1473`), owner WK-675 (`PL-1286` DP-5) |
| `POST` | `/api/v1/rating-versions/{id}/compile` | **202** Compile + validate the bundle (FR-240); **409** `RATING_VERSION_IMMUTABLE` unless the version is `draft` (FR-239) |
| `POST` | `/api/v1/rating-versions/{id}/submit` | Submit for approval; evidence completeness checked (FR-257); golden quotes re-scored and the suite pinned (FR-260). **Amended 2026-09-28** (`PL-1189`) |
| `POST` | `/api/v1/regression-suites/{slug}/versions` | Create a new Regression Suite version; `rating:write`; **201** (FR-260). **Added 2026-09-28** (`PL-1189`) |
| `GET` | `/api/v1/regression-suites/{slug}@{version}` | Read a Regression Suite version; `rating:read`; access-controlled per NFR-499 (FR-260). **Added 2026-09-28** (`PL-1189`) |
| `POST` | `/api/v1/score` | Real-time single quote (FR-250) |
| `POST` | `/api/v1/score/batch` | **202** Batch re-rate → Job (FR-253) |
| `POST` | `/api/v1/score/compare` | Score one quote against two versions with a step-level diff (FR-262); §4.10. Requires `rating:read`. Any compiled version may be named, `draft` included; both calls are traced, run one after the other, and nothing is persisted or logged (NFR-499). **200** with a `ScoreComparison`; 401; 403; 404 when either ref names no version; 409 `BUNDLE_COMPILE_FAILED` when either is not compiled; 422 for a `context` carrying its own `options.rating_version_ref` or for FR-255's per-quote codes; **500** `LADDER_RECONCILIATION_FAILED`, the problem naming the failing side (FR-248, `RL-1346`). **Amended 2026-09-28:** a per-quote error on either side answers 422 with that code, and the problem names the failing side (`base` or `comparison`), so a later switch to a 200 with a partial result is a breaking change. 404 and 409 name their side the same way. |
| `POST` | `/api/v1/rating-versions/{id}/regression-runs` | **202** Run the regression suite (FR-260/261) |
| `GET` | `/api/v1/rating-versions/{id}/regression-runs/{run_id}` | Read a Regression Run; `rating:read`; a failing property's counterexample is a quote-input fragment, so access-controlled per NFR-499 (FR-261). **Added 2026-09-28** (`PL-1205`) |
| `GET` | `/api/v1/rating-versions/{id}/regression-runs/{run_id}/cases` | Read the run's case log (its generated cases and counterexamples); `rating:read`; the only route that reads this blob, which `GET /api/v1/blobs/{sha256}` refuses (`FR-1221`, NFR-499). **Deliberately unpaginated:** the log holds at most `generation.cases` contexts, and `RegressionGeneration.cases` is capped at 10 000, so the response is bounded by that cap (about 10 000 Quote Contexts plus one counterexample per failing property). **Added 2026-09-28** (`PL-1205`) |
| `POST` | `/api/v1/dislocation-runs` | **202** Baseline vs candidate over a portfolio (FR-263) |
| `GET` | `/api/v1/dislocation-runs/{id}` | Dislocation artifact |
| `POST` | `/api/v1/environments/{env}/deployments` | Deploy an approved version (FR-267) *(Refusals added 2026-10-03, `RL-1401`: 409 `VALIDATION_FAILED` when the Environment is retired; 409 `BUNDLE_COMPILE_FAILED` when the Rating Version has no compiled bundle; §4.12.)* |
| `POST` | `/api/v1/environments/{env}/deployments/rollback` | Roll back (FR-269) |
| `PUT` | `/api/v1/environments/{env}/shadow` | Configure shadow scoring (FR-271) |
| `GET` | `/api/v1/traces?rating_version=&from=&to=` | Sampled production traces (FR-259) |
| `GET` | `/api/v1/environments/{env}/deployments` | Deployment history for an environment (FR-267; read by `06` FR-382) |
| `POST` | `/api/v1/environments/{env}/deployment-requests` | Submit a deployment request for approval (FR-267, FR-429) *(Refusals added 2026-10-03, `RL-1401`: 409 `VALIDATION_FAILED` when the Environment is retired; 409 `BUNDLE_COMPILE_FAILED` when the Rating Version has no compiled bundle; §4.12.)* |

**Error codes owned by this module:** `RATING_GRAPH_CYCLIC`, `RATING_GRAPH_UNRESOLVED_REF`,
`RATING_TYPE_MISMATCH`, `MONETARY_FLOAT_REFUSED`, `EXPRESSION_NON_DETERMINISTIC`,
`EXPRESSION_UNGUARDED_DIVISION`, `EXPRESSION_SCALE_OVERFLOW`, `EXPRESSION_INVALID_VOCABULARY`,
`RATING_VERSION_UNPINNED`, `INPUT_CONTRACT_VIOLATION`,
`REFERENCE_LOOKUP_MISS`, `RATE_TABLE_MISS`, `RATE_TABLE_INCOMPLETE`,
`RATE_TABLE_KEY_DUPLICATE`, `CONTROL_FACTOR_IN_RATEABLE_PATH` *(registered 2026-10-08, `RL-1470`, FD-1422 and FD 9639: **422** at `seed-from-model` (FR-230) and at bundle compile (FR-240); the message names the table, the key and the Factor, or for a `model_call` the model, the feature and the Factor)*, `PIN_NOT_APPROVED`,
`BUNDLE_COMPILE_FAILED`, `EVIDENCE_INCOMPLETE` (re-raised from `06`), `GOLDEN_QUOTE_MISMATCH`,
`PROPERTY_ASSERTION_FAILED`, `REGRESSION_PROPERTY_INVALID` *(added 2026-09-28, WK-672 Slice 3: 422 at `POST /api/v1/regression-suites/{slug}/versions` and from the `rating.regression` Job, naming the `monotone` property whose input is absent, not orderable, has no range, has a range empty after the contract's own bounds, or has no two-place decimal value)*, `DEPLOY_REQUIRES_APPROVAL`, `DEPLOY_DATE_RANGE_OVERLAP`,
`LADDER_RECONCILIATION_FAILED` *(status added 2026-09-30, `RL-1346`: **500** from `POST /api/v1/score` when a scored quote's Premium Ladder does not reconcile (FR-248), and 500 naming the failing side from `/score/compare`; an `"error"` row in batch scoring, counted by type (FR-255). A platform fault, not a per-quote 422: the input is valid, and the failure is deterministic, so the response carries no `Retry-After`. The message names the failed clause, the rungs and the minor-unit difference, and carries no quote input)*, `LADDER_CLAMP_UNPLACEABLE` *(added 2026-09-30, `RL-1329`: 422 at algorithm save and at bundle compile, FR-240's clamp-placement check; the message names the step and the rung and carries no quote input)*, `MODEL_REFERENCE_MODE_INCONSISTENT`,
`RATE_TABLE_SEED_MISMATCH`
*(added 2026-08-28, W10-3C)*, `NO_RELATIVITIES`, `FILTER_UNKNOWN_KEY`,
`FLOOR_ABOVE_CAP`, `REBASE_NO_MATCH`, `REBASE_AMBIGUOUS`, `REBASE_ZERO_REFERENCE`,
`IMPORT_KEY_MISMATCH`, `IMPORT_TYPE_MISMATCH`, `IMPORT_PARSE_ERROR`
*(added 2026-08-28, W10-3C)*, `MODEL_CALL_FAILED`
*(added 2026-08-29, WK-671 Slice 1 — FR-255's fifth category, model failure; ruled in `docs/rulings/RL-00877-model-call-failed.md` RL-877)*, `NO_LIVE_RATING_VERSION`
*(added 2026-08-29, WK-671 Slice 2 — **409**. FR-250's default path resolves the Rating Version live in the target environment, and `live` is a property of a Deployment (FR-238), which is WK-674's. A `POST /api/v1/score` omitting `rating_version_ref` is refused with this code rather than scored against a guessed version. The branch is permanent, not a stub: after WK-674 it is what an environment holding no Deployment answers. Ruled in `docs/rulings/RL-00880-dp1-post-api-v1-score-takes-an-explicit-rating-version-ref-in-wk-671-and-refuses-rather-than-guesses-when-it-is-absent.md` RL-880)*,
`BATCH_ABORT_THRESHOLD_ABOVE_SETTING`, `BATCH_ABORTED`
*(added 2026-08-30, WK-671 Slice 3 Task 3B — FR-255, RL-889. The first: a `score.batch`
Job argument may only lower `rating.batch_abort_failure_rate`'s resolved effective threshold,
never raise it; a request whose argument is above it is refused with this code before any
row is scored. The second: a run whose observed per-quote failure rate crosses the effective
threshold aborts, recording both the threshold in force and the observed rate — never a
silent partial result)*,
`TRACE_RETENTION_FLOOR`
*(added 2026-08-30, WK-671 Task 4A — **409**. FR-259's sampled traces are persisted for
≥ 13 months (NFR-459), a preservation floor rather than an expiry (RL-888's
correction). Deleting a `scoring_traces` row while it is still inside that floor is refused
with this code; outside the floor it is permitted. `app.platform.traces.delete_trace` is
the only raiser)*,
`TRACE_NOT_PENDING`
*(added 2026-08-30, WK-671 Task 4B — **409**. RL-862 moves trace production off the
serving request: a sampled real-time outcome is first persisted `pending`, and an
off-path Job re-scores the pinned bundle and fills in the body. This code is refused when
that completion is attempted against a row that is not `pending` — already completed, or
never a pending row — so a re-delivered Job stops rather than re-running the re-score and
orphaning a blob. `app.platform.traces.complete_pending_trace` is the only raiser)*,
`RATING_VERSION_IMMUTABLE`
*(added 2026-10-04, RL-1379, WK-674 Slice 2 — **409**. FR-239: a compile of a Rating Version whose status is not `draft`. `POST /api/v1/rating-versions/{id}/compile` refuses it synchronously and creates no Job; a `rating.compile` Job whose version left `draft` after submission ends `failed` with this code. `app.platform.rating_versions.require_compilable` is the only raiser)*,
`DATASET_NOT_VALIDATED` (re-raised from `01`)
*(added 2026-10-05, `RL-1361` — **409** from
`GET /api/v1/rate-tables/{slug}@{version}/diff` when the named `portfolio` is not
`validated`, and the failure of its `rate_table.diff` Job when the portfolio is archived
between submit and run; the detail names the diff)*.

> **`RATING_VERSION_UNPINNED` (meaning added 2026-09-30, on FD-1297, FR-237).** The Rating
> Version cannot be compiled, or a compiled bundle cannot be loaded: it has no `algorithm_ref`,
> has no `pins`, or has a `table`, `lookup` or `model_call` step whose ref is not in the
> matching pin list (`rate_tables`, `reference_tables`, `models`) at that exact version.

> **`RATING_EVALUATION_FAILED` (added 2026-09-30, on FD-1317, FR-255, `RL-1313` DP-G4).** The
> engine failed evaluating an authored expression, condition or clamp bound at scoring, and
> the failure is not a table or lookup miss.

> **RATE_TABLE_PARQUET_UNBUILT (2026-08-28, W10-2).** A diff touching a `parquet`-stored
> version is refused with **501** until W10-3 delivers the 202-with-Job form. No version
> can yet be written as parquet — seeding always writes `rows` — so the branch is declared
> rather than discovered, mirroring `01`'s `DERIVATION_NOT_MATERIALISED` precedent: a
> fabricated diff or a worker-less JobKind would fail later and silently.

> **Superseded 2026-08-28 (W10-3D): the 501 is retired and the 202-with-Job form is
> live.** The diff Job runs on the compute queue (`JobKind.RATE_TABLE_DIFF`,
> `07` FR-411's model) and computes the same artifact the 200 path computes — the
> same service call, a parquet-stored version materialised from its blob — then stores
> it as a JSON blob and returns `result.ref` as the blob's sha256, fetchable from
> `/blobs/{sha256}`: the codebase's first `JobResult(kind="blob")`. The refusal and its
> code are removed; the blockquote above stands as the record of the interim. The Job
> exists only where either version is `storage: parquet`; the 200 read path is unchanged
> and now serves compute-on-read through the DP3 cache (rulings 2026-08-28) — keyed by
> both versions' content hashes and the portfolio dataset version's identity, never a
> date, and failing open to a plain compute when Redis is unreachable.

> **Bulk-operation and import refusals (2026-08-28, W10-3C).** The bulk operations
> (04 §4.4) and the import preview refuse with their own names: `RATE_TABLE_SEED_MISMATCH`
> is the save-time seed-lineage equality proof (FR-234), `NO_RELATIVITIES` is the seed
> gate, `FILTER_UNKNOWN_KEY` / `FLOOR_ABOVE_CAP` / `REBASE_NO_MATCH` / `REBASE_AMBIGUOUS` /
> `REBASE_ZERO_REFERENCE` are the four operations' named refusals, and
> `IMPORT_KEY_MISMATCH` / `IMPORT_TYPE_MISMATCH` / `IMPORT_PARSE_ERROR` are the strict
> round-trip's refusals (FR-235). All ten were declared in `app/errors.py` before
> first use — an unregistered code would surface as a 500, so the ownership block is
> the declaration of record.

> *(Ruled 2026-08-28, decision-maker — bulk-operation, import and export address a
> specific version, `{slug}@{version}`.)* The WK-670 plan's T4 drafted `/versions/{version}/`
> forms; the ruling adopts `@{version}`, this module's established versioned addressing
> (the diff row above), because an operation must state the baseline it transforms — an
> implicit "latest" would race concurrent writers and make the recorded operation's
> meaning drift from the cells it actually changed. Export gained its rows here:
> FR-235 requires export, and §5.1 previously had only the import row.

> *(`created_by_import.filename` ruled 2026-08-28, DP5.)* The import request carries the
> uploaded file and its name (multipart/form-data); `created_by_import.filename` records
> the upload's name as received.

> *(`confirm` ruled 2026-08-28, W10-3C.)* The import request is multipart/form-data; without
> `confirm` it returns the diff and creates nothing. With `confirm: true` the same upload is
> parsed again and, verdict strict, the version is created — the diff is re-computed on the
> same bytes against the same immutable baseline, so the created version cannot diverge from
> the preview. Confirmation cannot override the round-trip verdict: a mismatch in keys, types
> or completeness is the same named error on both calls.

### 5.2 `pricing-core` interfaces

```python
# pricing_core/rating/compile.py
def validate_algorithm(algo: RatingAlgorithm) -> list[ValidationIssue]
async def compile_bundle(version: RatingVersion, resolver: ArtifactResolver) -> Bundle  # inlines each pinned sub-graph mount (FR-217), validates the inlined algorithm; amended 2026-10-09 (WK-1250 Slice 2)
def to_jdm(algo: RatingAlgorithm) -> JdmGraph          # ADR-706 translation layer
def bundle_hash(graph: JdmGraph, pins: Pins) -> str    # corrected 2026-08-27 (F-W9-3-2)
def assert_integer_minor_round_trip() -> None          # FR-273's startup self-check; added 2026-09-28 (F60 (3), RL-1172)

# pricing_core/rating/inline.py                      # added 2026-10-09 (WK-1250 Slice 2, FR-217)
def inline_mounts(algorithm: RatingAlgorithm,         # pure; the one inliner compile_bundle and load_bundle both call
                  fragments: Mapping[str, SubGraph]) -> RatingAlgorithm

# pricing_core/rating/runtime.py                      # added 2026-08-29 (WK-671 Slice 1)
def load_bundle(bundle: Bundle) -> CompiledBundle     # FR-243's hydration step
def to_wire(graph: JdmGraph,                          # the ZEN engine's wire payload;
            payloads: Mapping[str, Any] | None = None) -> dict[str, Any]  # added 2026-09-28 (F60 (1), RL-1172)

# pricing_core/rating/score.py
async def score_one(bundle: CompiledBundle, ctx: QuoteContext, *,
              trace: bool = False) -> ScoringResult
def build_scoring_result(bundle: CompiledBundle, ctx: QuoteContext,  # FR-254's shared tail;
                         rating_version_ref: ArtifactRef,            # added 2026-09-28
                         result: Mapping[str, Any],                  # (F60 (4), RL-1172)
                         engine_trace: Mapping[str, Any] | None) -> ScoringResult
def score_batch(bundle: CompiledBundle, frame: pl.LazyFrame, *,
                chunk_rows: int = 100_000,
                progress: ProgressCallback | None = None) -> pl.LazyFrame

# pricing_core/rating/analysis.py
def dislocate(baseline: CompiledBundle, candidate: CompiledBundle,
              portfolio: pl.LazyFrame, spec: DislocationSpec) -> DislocationRun
def read_portfolio(portfolio: pl.LazyFrame, *,                     # added 2026-10-04 (WK-673 S2, RL-1402): §4.8's
                   segments: Sequence[str] = ()) -> pl.LazyFrame    # reader; refuses at the call; Slice 7 reuses it
def dislocation_frame(baseline: CompiledBundle, candidate: CompiledBundle,
                      portfolio: pl.LazyFrame, spec: DislocationSpec) -> pl.DataFrame   # one row per policy
def select_movers(frame: pl.DataFrame, spec: DislocationSpec) -> pl.DataFrame          # FR-263's movers, in §4.6's order
def summarise_dislocation(frame: pl.DataFrame, spec: DislocationSpec) -> DislocationRun  # dislocate = this ∘ dislocation_frame
async def derive_changes(baseline: RatingVersion, candidate: RatingVersion,    # added 2026-10-03 (WK-673 S1, FR-1399)
                         resolver: ArtifactResolver) -> list[BundleDelta]
async def attribute(baseline: RatingVersion, candidate: RatingVersion,         # amended 2026-10-03 (WK-673 S1,
                    portfolio: pl.LazyFrame, spec: DislocationSpec,            # RL-1264 premise: the old form took
                    resolver: ArtifactResolver) -> Attribution                 # no baseline and could not compile subsets)

# pricing_core/rating/testing.py
def run_regression(bundle: CompiledBundle, suite: RegressionSuite,
                   *, rating_version_ref: ArtifactRef,               # amended 2026-09-28 (seed: suite's)
                   now: Callable[[], datetime]) -> tuple[RegressionRun, CasesLog]  # (PL-1205)
def generate_contexts(contract: Sequence[InputContractField],   # corrected 2026-09-28
                      n: int, seed: int,                        # (RL-1172); was InputContract
                      *, expect_version: str | None = None) -> list[QuoteContext]  # PL-1205
class GeneratorVersionMismatch(ValueError): ...                 # added 2026-09-28 (PL-1205)
def evaluate_golden_quotes(bundle: CompiledBundle, golden_quotes: Sequence[GoldenQuote],   # added 2026-09-28
                           *, rating_version_ref: ArtifactRef) -> list[GoldenQuoteResult]  # (PL-1189)

# pricing_core/rating/replay.py                       # added 2026-09-28 (WK-672 Slice 3, PL-1205)
def replay_cases(bundle: CompiledBundle, cases: CasesLog, suite: RegressionSuite,
                 *, recorded: RegressionRun, rating_version_ref: ArtifactRef,
                 now: Callable[[], datetime]) -> RegressionRun

# pricing_core/rating/trace_diff.py                   # added 2026-09-29 (WK-672 Slice 4, PL-1213)
def diff_traces(base: Trace, comparison: Trace) -> TraceDiff   # pure; §4.10

# pricing_core/money.py — the decimal discipline (R2); path and signatures
# corrected 2026-08-29 (WK-671 Slice 1, RL-879) — there is no rating/money.py
def apply_factor(amount_minor: int, factor: Decimal, mode: RoundingMode) -> int
def reconcile_ladder(risk_premium_minor: int, steps: list[tuple[str, int]]) -> bool
# to_minor is model-schema's, not pricing-core's: model_schema/money.py

# pricing_core/rate_tables/operations.py
from model_schema.rating import KeyFilter  # corrected 2026-09-28 (F59, RL-1172): model-schema's shape, imported, never redefined here
def uplift_table(table: RateTableVersion, *, percentage: Decimal) -> RateTableVersion
def uplift_by_filter(table: RateTableVersion, *, percentage: Decimal,
                     filter: KeyFilter) -> RateTableVersion
def floor_and_cap(table: RateTableVersion, *, floor: Decimal, cap: Decimal) -> RateTableVersion
def rebase_to_level(table: RateTableVersion, *, base_level: KeyFilter) -> RateTableVersion
def decide_storage_mode(cell_count: int, threshold: int = 250_000) -> Literal["rows", "parquet"]
def export_to_csv(table: RateTableVersion) -> bytes
def export_to_xlsx(table: RateTableVersion) -> bytes
def import_from_csv(version: RateTableVersion, content: bytes, *, filename: str) -> ImportPreview
def import_from_xlsx(version: RateTableVersion, content: bytes, *, filename: str) -> ImportPreview
def import_confirmed(version: RateTableVersion, content: bytes, *, filename: str) -> ImportResult
# the six below added 2026-09-28 (F60 (2), RL-1172) — live behind published endpoints;
# CellRow = dict[str, str] and Cells = Sequence[CellRow] are this module's aliases
def check_model_approved(model: Model) -> None
def extract_relativity_table(model: Model, *, value_name: str = "relativity") -> list[CellRow]
# `factor` and `factors` added 2026-10-03 (RL-1361 section D): the platform loads the
# model's Factors and passes them in; the pure function binds the one key to `factor`'s Factor
def seed_from_model(model: Model, *, factor: str, factors: Sequence[Factor], table_slug: str,
                    change_note: str, seeded_at: datetime, rateable: bool = True,
                    value_name: str = "relativity") -> SeedResult
def validate_rate_table(cells: Cells, keys: Sequence[RateTableKey], value: RateTableValue, *,
                        key_domains: Mapping[str, frozenset[str]],
                        default_row: CellRow | None = None) -> list[ValidationIssue]
def diff_vs_previous(previous_cells: Cells, current_cells: Cells,
                     keys: Sequence[RateTableKey], value: RateTableValue, *,
                     weights: Weights | None = None) -> RateTableDiff
def diff_vs_seed(seed_cells: Cells, current_cells: Cells,
                 keys: Sequence[RateTableKey], value: RateTableValue, *,
                 weights: Weights | None = None) -> RateTableDiff
def diff_cells(baseline_cells: Cells, current_cells: Cells,            # added 2026-10-05 (RL-1418, FD-1358):
               keys: Sequence[RateTableKey], value: RateTableValue, *,  # every changed cell in §4.2's order,
               weights: Weights | None = None) -> list[RateTableDiffCell]  # the set diff_vs_* count

# pricing_core/rate_tables/weights.py                # added 2026-10-05 (WK-673 Slice 7, RL-1418, RL-1361)
def exposure_weights(portfolio: pl.LazyFrame, keys: Sequence[RateTableKey], cells: Cells, *,
                     factors: Mapping[str, Sequence[Factor]],
                     bandings: Mapping[UUID, Banding],
                     groupings: Mapping[UUID, Grouping]) -> PortfolioWeights
```

*`DislocationSpec` (added 2026-10-03, `RL-1394`): `baseline_ref`, `candidate_ref`, `portfolio_dataset_version_id`, `purpose`, `as_at` (§4.8's portfolio frame), `segments` (the Factors FR-263 averages by), `band_edges_pct`, `mover_threshold_pct` (FR-263), and optional `change_groups` (FR-1399). `BundleDelta`: one derived change, `id`, `kind`, `description`, as §4.6's `derived_changes` item. `Attribution`: §4.6's `derived_changes`, `change_groups`, `attribution` and `attribution_summary` together. All three are defined in `model-schema` by the slice that first returns them (WK-673 Slices 2 and 3) and match §4.6 field for field.*

*`analysis.py`'s public surface (added 2026-10-04, WK-673 Slice 2, `RL-1402`).* `read_portfolio` checks §4.8's frame and each name in `segments` (present, of a dtype §4.6 admits) when it is called, not when its result is collected, and returns the frame with every column kept and `exposure_years` read as §4.6 states. `PortfolioFrameError` is a `ValueError` with `code = "VALIDATION_FAILED"`, raised for any such fault, and by `dislocation_frame` for a portfolio column named as one of its own columns; its message names the column and the count, or the column and its dtype, and never a value; the platform maps it to `VALIDATION_FAILED`. `dislocation_frame` calls `read_portfolio(portfolio, segments=spec.segments)` before any rating and returns one row per policy, sorted by `quote_id`: `quote_id`; `baseline_outcome`, `candidate_outcome`; `baseline_minor`, `candidate_minor`, the `payable_premium` rung's `value_minor` as an integer, null unless that pass quoted; `change_minor`, `candidate_minor − baseline_minor`, null unless both passes quoted; `baseline_error_code`, `candidate_error_code`; `origin_rung` (§4.6), null unless both passes quoted and a rung differs; then every portfolio column, in the portfolio's order. `select_movers` returns the frame's rows for FR-263's movers, in §4.6's mover order; Slice 4 writes them to `largest_movers_blob`. `dislocate(b, c, p, s)` is exactly `summarise_dislocation(dislocation_frame(b, c, p, s), s)`. `band_edges_pct` and `mover_threshold_pct` keep the names `RL-1394` gave them; §4.6 states their rules.*

*`weights.py`'s public surface (added 2026-10-05, WK-673 Slice 7, `RL-1418`, on `RL-1361` items 2 to 4).* `exposure_weights` computes FR-231's exposure weight per cell of a rate table version. `portfolio` is `read_portfolio`'s output, so §4.8's frame refusals have already run. `keys` and `cells` are the **current** version's. `factors` maps each `factor_ref` in `keys`, as its `factor:<slug>@<version>` string, to that Factor followed by any interaction operands. `bandings` and `groupings` hold, by id, every Banding a `banding_ref` names and every Banding or Grouping those Factors pin. The platform loads all three, because this function takes no database (ADR-703). Each key is resolved by exactly one branch of `RL-1361` item 2: `resolve_factors` for a `factor_ref`, `apply_banding` for a `banding_ref`, and the same-named column otherwise. The comparison with each cell's stored key string is made in the key's declared type. `PortfolioWeights` is a frozen dataclass with three fields. `weights` is a `dict[KeyTuple, Decimal]` mapping each cell's stored key tuple to Σ `exposure_years` over the rows that map to it, with any cell whose Σ is 0 omitted; it is a `Weights` and is passed unchanged as `weights` to `diff_vs_previous`, `diff_vs_seed` and `diff_cells`, so the aggregate mean and the per-cell weights come from one map. `portfolio_exposure` is Σ `exposure_years` over every row, and `matched_exposure` is that sum over the rows that map to a cell; these are §4.2's two coverage figures. `WeightJoinError` is a `ValueError` with `code = "VALIDATION_FAILED"`. It is raised for an absent column, a non-numeric banded column, a `FactorResolutionError`, and a portfolio whose rows map to no cell. Its own message names the key, the column or the ref, never a value; a `FactorResolutionError`'s message is carried as it is, with its count and example value (`RL-1361` item 3). The platform maps it to `VALIDATION_FAILED`.

> *(Corrected 2026-09-28, RL-1172 — the decision-maker ruled the spec was wrong on F59 and
> on all four limbs of F60, and the code right.)* The block above had omitted nine live
> public functions: `to_wire`, the six rate-table functions that published endpoints reach,
> `assert_integer_minor_round_trip` (the startup call FR-273 requires), and
> `build_scoring_result`. It had also placed
> `KeyFilter`'s definition in `operations.py`, which only imports it: the shape is
> `model_schema.rating`'s (`CLAUDE.md` §2). In the `testing.py` block, `InputContract`
> named a type that does not exist. The input contract is `RatingAlgorithm.input_contract`,
> a `list[InputContractField]`. `run_regression` **stays plain `def`**. It runs inside the
> 202 Job that `POST …/regression-runs` starts. It reaches the engine through the
> synchronous `evaluate()` path `score_batch` uses (RL-868), and so through the same
> `build_scoring_result` tail as `score_one` (RL-858). The generator is decided on spike
> F4's record, not here. Both `testing.py` functions live in
> `pricing-core` and hold no persistence. The backend owns the suite store, the Job and the
> gates. *(Added 2026-09-28, `PL-1189`, the deputy's DP-S2-3 decision by delegation.)*
> `evaluate_golden_quotes` is plain `def` on the same synchronous `evaluate()` path as
> `run_regression` (RL-868, RL-858). It returns one `GoldenQuoteResult` per golden quote,
> in input order, comparing exactly in integer minor units (FR-273) within each quote's
> declared tolerance; an engine refusal for one quote becomes that quote's `fail`, never an
> abort of the rest. `run_regression` composes it; the submit gate (FR-260) calls it
> directly. *(Added 2026-09-28, WK-672 Slice 3, `PL-1205`.)* `replay_cases` only re-scores
> the persisted cases and counterexamples of a `CasesLog` (`FR-1221`); the module never
> imports `hypothesis` or `testing`, so a replay cannot regenerate. `generate_contexts`
> raises `GeneratorVersionMismatch` when `expect_version` is given and differs from the
> installed `hypothesis` version. `evaluate_golden_quotes` is implemented in the
> hypothesis-free `pricing_core/rating/golden.py` and re-exported by `testing.py` under its
> declared name.
> *(Amended 2026-09-28, WK-672 Slice 3, `PL-1205`, auditor findings.)* `run_regression`
> takes no seed of its own: it draws under `suite.generation.seed`, the persisted seed, so a
> run cannot be made under one seed and recorded as another. `replay_cases` raises
> `SuiteMismatchError` before scoring anything when `suite.content_hash` differs from the
> recorded run's `suite_content_hash`, because that hash is `FR-257`'s pin (DP-S3-2).
> `generate_contexts` samples an `int` or `decimal` input with no declared `min` or `max`
> over `-1 000 000..1 000 000`, symmetric about zero, so a property that fails only for
> negative values is reachable; a `decimal` bound is quantised to two places, the minimum
> rounded up and the maximum down, and an input with no two-place value between its bounds is
> refused by name.
> *(Amended 2026-09-28, WK-672 Slice 3, `PL-1205` Task 4.)* `run_regression` and
> `replay_cases` take the keyword-only `rating_version_ref` and `now`, because
> `pricing-core` holds no clock (`CLAUDE.md` §2) and the run record carries both a
> reference and start and finish times; `now` is read at the start and the end. Neither
> sets `job_id`, and `cases_blob` is the case log's own content address, computed
> purely. `run_regression` also returns the `CasesLog` the backend stores as that blob
> (`FR-1221`). `replay_cases` takes the `recorded` run, the source of the generation
> record and of each failing property's persisted `shrink` and `counterexample_minimal`:
> a replay cannot shrink, so it reports what was recorded, and reports a property that now
> fails on an unshrunk case as `stopped_on_limit`, unminimised. *(The `monotone` reading is FR-261's dated clarification of 2026-09-28: its grid, its handling of declined points and its known weakness are stated there.)*

> *(`import_confirmed` added 2026-08-28, DP6 — the confirmation half of FR-235.)*
> `POST /import` with `confirm: true` re-parses the same upload through the same strict
> pipeline and creates the version; `import_confirmed` returns the checked cells and the
> verdict (`ImportResult`), and the API persists — confirmation cannot override the
> round-trip verdict, so the created version cannot diverge from the preview (same
> bytes, same immutable baseline).

`ImportPreview` is the FR-231 cell diff of the would-be version **against the
addressed version** plus the strict round-trip verdict (FR-235); a mismatch in keys,
types or completeness is a named error — completeness is checked against the addressed
version's validated domain (an explicit `default_row` waives it) — and the import only
creates a version after the diff is confirmed. `KeyFilter`
matches FR-233's "key filter"; `rebase_to_level`'s `base_level` names the reference
level (single-key tables: the key value; multi-key: the combination) whose value becomes
1.0. Each operation validates the result before persisting (FR-234) and returns a
new immutable version whose `created_by_operation` carries the `BulkOperation` record
(`04` §4.4). The verdict's `filename` is the upload's name as passed, recorded on the
created version's `created_by_import.filename`.

> *(`import_from_csv`/`import_from_xlsx` corrected 2026-08-28 — the W10-3 readiness
> amendment named a bare `RateTable`; the decision-maker ruled the signature wrong.)* The
> import endpoint addresses `{slug}@{version}` (§5.1), and the confirmation diff that
> FR-235's workflow depends on must show what the import changes against the version
> the actuary exported — an empty-baseline "all cells new" preview cannot confirm anything,
> so the round-trip confirmation would be a rubber stamp. The signature therefore takes
> the addressed `RateTableVersion`: the preview diffs the would-be version against it, and
> completeness is checked against its validated domain. Import into a versionless table is
> out of scope — the endpoint addresses a version, as the ruling on bulk-operation
> addressing established.

> *(Corrected 2026-08-27, F-W9-3-2 — the decision-maker ruled the spec was wrong.)* The
> content hash is `bundle_hash(graph, pins)`, never `bundle_hash(bundle)`: the Bundle
> carries `compiled_at`, and hashing a timestamp would make the hash unreproducible. Per
> DP1 and FR-239, the hash covers the graph and the pinned artifact references and is
> reproducible from the pins; `compiled_at` is metadata and is excluded.

> *(Corrected 2026-08-29, WK-671 Slice 3 — the decision-maker ruled the spec was wrong.)* This
> read *"`score_one` and `score_batch` share the identical step evaluator"*. There is no shared
> step evaluator and there was never going to be one: per-step evaluation happens inside the ZEN
> engine, not in this repository, and `pricing_core.rating.score` exports exactly
> `build_scoring_result` and `score_one`. Per RL-868, `score_one` reaches the engine through
> `async_evaluate()` while `score_batch` stays plain `def` — different methods, so the phrase was
> inaccurate at the engine level too. RL-858,
> `docs/rulings/INDEX.md#2026-08-29-w11-3-d6-batch-resumability-rulingmd`.

`score_one` and `score_batch` share the identical **post-evaluation tail** —
`build_scoring_result`, the one function turning an already-evaluated engine result into a
`ScoringResult` (FR-254). The byte-identity a batch implementation must prove is exactly
that function producing the same output from the same input, not two implementations that
happen to agree. `score_batch` is a vectorised driver over the same compiled graph, not a
second engine.

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
| 1 | Pricing Actuary | Seeds rate tables from the approved Peril Structure's models (FR-230) |
| 2 | Pricing Actuary | Edits the algorithm in the DAG designer; validation runs on every change |
| 3 | Pricing Actuary | Edits rate tables; diffs vs previous and vs technical seed stay visible |
| 4 | Frontend → Backend | `POST /rating-versions` + `POST /{id}/compile` → bundle hash |
| 5 | Analyst | Runs the regression suite; fixes any golden-quote or property failure |
| 6 | Analyst | Runs dislocation vs the current live version, with attribution (FR-266) |
| 7 | Pricing Actuary | Runs a GIPP check where enabled (`04-optimisation.md`) |
| 8 | Pricing Actuary | Writes the change summary (drafted from diffs) and submits |
| 9 | Approver | Reviews structural diff, rate diffs, dislocation, tests, GIPP → approves |
| 10 | Deployer | Deploys to `uat`, shadow-scores, then deploys to `prod` (FR-267/271) |
| 11 | Backend | Pre-warms the bundle, switches atomically, emits Audit Event + notification |

Full journeys: [`WF-699-model-to-rating-version.md`](../workflows/WF-00699-approved-models-to-approved-rating-version.md),
[`WF-700-rate-change-impact.md`](../workflows/WF-00700-rate-change-impact-optimisation-dislocation-gipp-decision.md),
[`WF-701-deploy-and-monitor.md`](../workflows/WF-00701-deploy-and-monitor.md).

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
- Reference lookups use the same effective-dating semantics as `01` FR-71; there is
  one implementation, in `pricing-core`.
- `05-monitoring` consumes traces as they are; this module does not pre-aggregate for it.

---

## 8. Tech dependencies

| Component | Used for | Notes for `skills-map.md` |
|---|---|---|
| **GoRules ZEN Engine** | DAG execution substrate (ADR-706) | JDM graph format, decision tables, `Variable::Number` is `rust_decimal` (exact decimal — verified); the `arbitrary_precision` serde feature and where it is *not* default; `maths-nopanic` returning 0 on invalid input; custom nodes for rate-table lookup and `model_call`; Python binding overhead at 200 rps; native trace output |
| **Python `decimal`** | All monetary arithmetic (R2, FR-245) | Contexts, `ROUND_HALF_EVEN`, integer minor units, avoiding float contamination through JSON serialisation |
| **Polars** | Batch scoring driver, dislocation aggregation, rate table storage in memory | Chunked lazy evaluation; joining portfolio rows to rate tables at scale |
| **DuckDB** | Dislocation slicing and segment aggregation over scored parquet | Window functions for change-band distributions |
| **Redis** | `Bundle` cache keyed by content hash; hot-path lookup | Cache warming before an atomic deployment switch (FR-268) |
| **FastAPI** | The scoring endpoint on the latency path | Async request handling, response model overhead, avoiding Pydantic re-validation on the hot path |
| **XGBoost / LightGBM** | `model_call` in `exact` mode | Booster load time, single-row prediction latency, thread pinning to avoid contention at 200 rps |
| **hypothesis** | Property assertion generation (FR-261) | Strategies derived from an input contract; shrinking counterexamples an actuary can read. **A `pricing-core` runtime dependency, pinned `==6.165.7`** *(2026-09-28, WK-672 Slice 3, `RS-1176` condition 1)*: an exact pin, because shrink-limit detection reads `hypothesis.statistics.collector`, which is internal API |
| **Vue Flow (frontend)**: `@vue-flow/core` 1.48.2, MIT (adopted 2026-09-28, `RS-1269` F2; added in WK-675 Slice 2) | The DAG designer | Custom node types per step type, edge validation, layout, undo/redo, mapping canvas state to the `RatingAlgorithm` contract |
| **openpyxl** | CSV/XLSX import/export with strict round-trip (FR-235) | XLSX read + write in one library; CSV is stdlib; round-trip keeps decimal strings — never float through the file |
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
| **NFR-489** | Real-time scoring p99 < 50 ms server-side at 200 rps per replica for a ~200-step motor structure with one `exact` GBM call (NFR-454). Without a GBM call, p99 < 15 ms. (Clarified 2026-10-05, OQ-1453: the ceiling governs untraced requests; a request served with an inline FR-258 trace is bounded by NFR-490.) |
| **NFR-490** | Tracing adds ≤ 20 % to scoring latency and never changes the result (R3). |
| **NFR-491** | A compiled bundle scores with **zero** database or network access; everything it needs is inside it (FR-239). |
| **NFR-492** | Bundle compilation for a large motor structure completes in < 60 s; bundle size stays under 500 MB including booster artifacts. |
| **NFR-493** | Batch scoring ≥ 1 M risks/hour per worker (NFR-455), linear in workers. |
| **NFR-494** | Deployment switchover is atomic with no dropped or mixed-bundle requests, and completes within 30 s of the deploy command including cache warming. |
| **NFR-495** | Determinism: identical bundle hash + quote context ⟹ identical premium, byte-for-byte, across processes, machines, and platform versions (FR-11). |
| **NFR-496** | Money exactness: no rounding is applied more than once; the ladder reconciles to the penny in 100 % of scored quotes (FR-248), asserted continuously in non-prod and sampled in prod. *(Amended 2026-10-01, `PL-1348` (SL-1345), on the maintainer's entry headed `2026-09-30 15:17:54 BST — audit round-up: decisions`: "asserted continuously in non-prod and sampled in prod" is superseded. The check runs on every scored quote in every Environment and is never sampled (FR-248); the trace-sampling rate governs trace persistence only. NFR-499's "sampled traces" are trace persistence, not this reconciliation.)* |
| **NFR-497** | Availability: the scoring endpoint targets 99.95 % monthly, degrading to the last-known-good cached bundle if metadata storage is unavailable. |
| **NFR-498** | Audit: algorithm edits, rate table versions, bulk operations, compilations, approvals, deployments, rollbacks, and routing changes all emit Audit Events with before/after state. |
| **NFR-499** | Security: the scoring API authenticates per Consumer System with scoped credentials and per-client rate limits; quote inputs are never logged in full outside sampled traces, which are access-controlled. *(Clarified 2026-08-30, WK-671: what "logged" reaches, and the store this clause never carved. **The clause governs persistence, not only log output.** The carve-out names sampled traces, and a trace is not a log, so a rule reaching only log lines would have had no need of that exception — the domain is records of a quote input, of which a trace is one. Read that way it collided with FR-260, which has a Golden Quote **store a Quote Context** outside any trace, and the defect is here rather than there: this clause names a single instance where its own justification, *"which are access-controlled"*, states a class. **A full quote input may be held only in an access-controlled artifact this specification names for that purpose, and those are sampled traces (FR-259) and Golden Quotes (FR-260).** A Golden Quote's stored Quote Context carries the same access-control obligation a trace carries, because that property is what justifies the exception rather than the artifact's name. **Any further store requires its own requirement**, so the next one is a visible decision rather than a third silent collision. FR-261 persists a seed rather than quote data and FR-262's sandbox is inline, so neither needs a carve-out. Nothing is in breach: `GoldenQuote` exists in no module, so this is settled before WK-672 builds it. Ruled in `docs/rulings/RL-00917-the-clause-reaches-persistence-and-nfr-499-is-the-defective-one.md` RL-917.)* *(Clarified 2026-09-28, WK-672 Slice 3, the deputy's DP-S3-4 (ii) by delegation.)* A Regression Run's case store (`FR-1221`) is the **third** named quote-input store, after sampled traces (FR-259) and Golden Quotes (FR-260), and carries the same access-control obligation. **This corrects the sentence above that FR-261 "persists a seed rather than quote data":** since `RS-1176` condition 4, a regression run persists the generated quote inputs and every counterexample, so FR-261 does hold quote data and needs the carve-out. The correction is written, not silent. |
| **NFR-500** | Trace storage: 1 % sampling of 50 M annual quotes stays under 200 GB/year with the sampled-trace schema. |
| **NFR-501** | GBM `model_call` steps execute with **`nthread=1` per request**. Measured (S2): single-threading beats all-cores at the tail — p99 1.09 ms vs 1.48 ms, worst case 4.5 ms vs 19.9 ms — because thread-pool spin-up dominates a single-row prediction. Parallelism belongs across concurrent requests, not inside one. *(Amended 2026-08-27, WK-668 — re-measured on the verification machine: p99 1.626 ms vs all-cores' 4.737 ms (max 6.143 ms vs 26.692 ms); `docs/research/w8-spike-resolution.md`. nthread=1 stays 0.34x of all-cores at the tail — the original S2 order holds, though the absolute figures are higher on this machine (slower `DMatrix` construction). p99 1.626 ms is still 3.3 % of the 50 ms budget: PASS. The design rule is unchanged: `nthread=1` per request.)* |
| **NFR-502** | The scoring endpoint does **not** apply `response_model` validation to its response. Pydantic validation costs roughly 1 ms per request — 2 % of the 50 ms budget before any pricing work — and the response path otherwise runs three to five transformations. `ScoringResult` is constructed by `pricing-core` and is already trusted, so it is serialised directly with a C-speed encoder (`ORJSONResponse`). Inbound `QuoteContext` **is** validated: untrusted input must be checked, trusted output need not be. *(Amended 2026-08-27, WK-668 — the premise's ~1 ms figure was not reproduced. A realistic `ScoringResult` (premium, 20 rate steps, 60 factors, metadata) validates and serialises at p99 0.070 ms, 0.14 % of the 50 ms budget, on the verification machine; `docs/research/w8-spike-resolution.md`. The measured shape is the one the premise describes, so the figure was an over-estimate, not a different context. The design rule is unchanged: validate inbound, never outbound; encode with `ORJSONResponse`.)* *(Amended 2026-08-29, WK-671 Slice 2 — the rule now states the property and no longer names the class. **Validate inbound, never outbound; serialise the trusted result directly with a compiled encoder.** `ORJSONResponse` was named when it was the way to get one. It is deprecated in the pinned FastAPI (0.141.1), it asserts at **render** rather than at import when `orjson` is absent — so a lost dependency boots clean and fails on the first quote — and the replacement its own deprecation notice names, a return type or `response_model`, is outbound validation, which this requirement's first sentence forbids: measured on the verification machine, an annotated route returning a shape that violates its model answers 500, and one returning a valid model drops any extra key. Pydantic v2's own compiled serialiser satisfies the property with no new dependency — `model_dump_json` emits an unvalidated model's contents verbatim, and a raw `Response` carrying those bytes runs no outbound validation at all. Ruled in `docs/rulings/RL-00883-f1-nfr-502-is-amended-to-the-property-it-was-always-about-orjson-is-not-added.md` RL-883.)* |
| **NFR-1443** | Rate-table cells-diff paging (`GET /api/v1/rate-tables/{slug}@{version}/diff/cells`, FR-231, FR-232), below `07` §1.3 R1 and NFR-457. **Budget:** every page after the first request for a key (the two versions and the `portfolio`) answers with **p95 ≤ 300 ms** at `limit` = `DEFAULT_LIMIT`, on both storage paths; the first request for a key may answer **202** with a Job under R1. **Measured, not asserted:** n ≥ 100 pages, on a quiet box, at **250 000 cells** with both versions `storage: rows` and at **1 000 000 cells** with both versions `storage: parquet`; each figure states its size, `limit`, percentile and n. **A page's cost is bounded by its `limit`, not by the table's cell count:** on each storage path, the page p95 at 250 000 cells is within **2×** of the page p95 at 10 000 cells at the same `limit`, both measured as above, with the workspace threshold (FR-232) set so that both versions take the path measured. *(Added 2026-10-05, RL-1441, deciding OQ-1440; FD-1439.)* |

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-614** | ~~Does the ZEN Engine preserve exact decimal semantics for money?~~ **Resolved 2026-08-14** — it represents numbers as `rust_decimal::Decimal`, so engine arithmetic is exact and ADR-706 stands. The risk moved to the boundaries and is now specified as FR-273/274/275; the S1 spike is re-scoped, not cancelled. See [`research`](../research/track-a-findings.md) F1. |
| **OQ-615** | ~~Is `model_call` in `exact` mode viable inside the 50 ms p99 budget?~~ **RESOLVED 2026-08-14 by spike S2 — comfortably yes.** A 500-tree × 60-feature booster scores a single row at **p99 1.09 ms** including `DMatrix` construction (0.33 ms predict-only) — about 2 % of the budget. `nthread=1` beat all-cores at the tail (p99 1.09 vs 1.48 ms; max 4.5 vs 19.9 ms), so per-request single-threading is correct. **OQ-575 is therefore a genuine design choice, not one forced by latency.** *(Amended 2026-08-27, WK-668 — re-measured on the verification machine: p99 1.626 ms vs all-cores' 4.737 ms (max 6.143 ms vs 26.692 ms); `docs/research/w8-spike-resolution.md`. nthread=1 still 0.34x of all-cores at the tail — the original S2 order holds, though the absolute figures are higher on this machine. p99 1.626 ms is still 3.3 % of the 50 ms budget: still comfortably viable. Recorded in NFR-501, amended the same way.)* |
| **OQ-616** | ~~Should rate tables live in PostgreSQL as rows or as content-addressed parquet blobs?~~ **DECIDED 2026-08-18: rows to a configurable cell count, spilling to parquet above it under one contract — FR-232**, with `storage` recorded on the version and the diff degrading to a Job above the threshold. |
| **OQ-617** | ~~How do mid-term adjustments and refunds work — a `purpose` on the same algorithm, or a genuinely separate calculation path?~~ **DECIDED 2026-08-18: the same algorithm for the risk price, with pro-rata/refund/charge logic in a separately-versioned sub-graph mounted on `purpose` — FR-218.** §2's `purpose` gained `cancellation` in the same edit, because the answer keys on a value that did not exist. |
| ~~**OQ-618**~~ | ~~Do we support multi-product bundling (motor + home in one quote with a bundle discount) in Phase 2, or is each product a separate Rating Version with bundling left to the Consumer System?~~ **Deferred to Phase 4**: Phase 2 ships single-product Rating Versions and a Consumer System bundling two quotes is a supported pattern — the bundle discount is then unpriced and unmonitored, and cross-product pricing follows the optimisation work that needs the same joint demand modelling. **DECIDED 2026-08-26: deferral confirmed — Phase 4; Consumer System bundling is the supported pattern** |
| **OQ-619** | ~~Should the platform own instalment/APR calculation, or is that a downstream billing concern?~~ **DECIDED 2026-08-18: price the annual premium, offer `instalment_loading` as a final ladder rung, and leave APR and schedules downstream — FR-252.** Enough for `04`'s demand model; not enough to make a rating release a consumer-credit release. |
| **OQ-620** | ~~Does a **Rate Table Version** have an approval lifecycle? `06` §2 lists it as a Governed Artifact — *"any artifact with an approval-bearing lifecycle"* — and `06` §3.3 gives it required evidence at submission; this section gives it no status at all and `rate_table_versions` has no status column, so `compile_bundle`'s FR-20 maturity gate has nothing to read for a `rate_table` pin.~~ **DECIDED 2026-09-28 by delegation — option (b): a Rate Table Version is governed through the Rating Version that pins it, with no lifecycle and no status** (FR-1186; `RL-1184` E8). Status: **decided**. *(Raised 2026-08-29 from WK-671 Task 1.2, which needed a maturity to report and found none; the pin is exempted from the gate meanwhile, declared and guarded so a status column turns the exemption red. Ruled in `docs/rulings/RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the-exemption-is-declared-and-self-invalidating.md` RL-856.)* |
| **OQ-1187** | ~~How does a Dislocation Run attribute a premium change to its causes when the changes interact (FR-266; WK-673)?~~ **DECIDED 2026-09-28 — option (b), exact Shapley with largest-remainder allocation (deputy, on spike F3's RS record)** (`RL-1184` F3). The options are isolated plus cumulative in a declared step order with an interaction-residual line; Shapley over steps; or cumulative only. The recommendation is the first. The pass criterion was ruled on 2026-09-28: exact Decimal reconciliation is a hard gate; the first option passes if order-sensitivity and residual are each at most 0.10 of the summed absolute isolated effects, on every set of K = 3 to 6 changes; otherwise exact Shapley at K ≤ 6. Raised 2026-09-28 from the deputy's item F3; decided on the F3 spike's research record. Isolated and declared-order cumulative figures stay as FR-266's views, beside the Shapley figures, with the interaction residual as its own line. Mirrored in `docs/open-questions.md`. Status: **decided**. |
| **OQ-1222** | Can the `monotone` grid take breakpoints from a GBM's split thresholds (XGBoost and LightGBM), per library? Mirrored in `docs/open-questions.md`. Status: **open** (owner WK-1178). |
| **OQ-1223** | How does an ordinal categorical input take part in a `monotone` property? Mirrored in `docs/open-questions.md`. Status: **open** (owner WK-675). |
| **OQ-1224** | Should the compiled bundle pin its Bandings, with an explicit input-to-band link, so that band edges become derivable? Mirrored in `docs/open-questions.md`. Status: **open** (owner WK-1178). |
| ~~**OQ-1231**~~ ✔ | ~~Should `StepChange.own_change` be derived from step-definition equality instead of `consumed` equality (§4.10)?~~ **DECIDED 2026-09-29: (b), `RL-1261`**, with `note` excluded from the comparison (§4.10, amended). Mirrored in `docs/open-questions.md`. Status: **decided** 2026-09-29 (`RL-1261`; owner WK-675, delivery). *(Noted 2026-09-29, the decision-maker: the gate is now **Before WK-675's map plan**, the roadmap §10 row placed on the maintainer's instruction of 2026-09-29 19:49:56 BST. "The route and `diff_traces` do not change for it" is superseded for option (b), read at `f0c3d197`: `diff_traces(base: Trace, comparison: Trace)` (`packages/pricing-core/src/pricing_core/rating/trace_diff.py:41`) takes only the two traces, so (b) changes its signature to take the two algorithms as well. The route (`backend/src/app/api/score.py:351-354`, `:374`) already holds each side's `CompiledBundle`, whose `algorithm` field (`packages/pricing-core/src/pricing_core/rating/runtime.py:561`) carries the step definitions, and discards it, so (b) changes the route's body to pass them. The route's request and response shapes do not change. That backend change is why the answer precedes the map plan's slice cuts.)* |
| **OQ-1285** | **Is §5.3's Deployments view (`/rating/environments`) a duplicate of `07` §5.3's Environments view (`/admin/environments`), given that both name the live deployments and the shadow configuration, and `00` §5.6 lists only `/admin/*` for environments?** Minted as OQ-1285 at #920's merge turn, 2026-09-30 (working id 9871 before the mint). Raised 2026-09-30 by the planner (WK-675's map plan), on the maintainer's #949 scope decision. Mirrored in `docs/open-questions.md`. Status: **open** (owner WK-675; for the decision-maker; gate: before WK-675 S12's leaf plan). |
| **OQ-1316** | **Is rounding offered inside a rating algorithm anywhere other than an `output` step's declared rounding (FR-226), and if so where, with what mode, and how is it recorded so the ladder reconciles (FR-248) and nothing rounds twice (NFR-496)?** Raised 2026-09-30 by the decision-maker in `RL-1312`, which keeps `round`, `floor` and `ceil` out of FR-244's P2 allow-list meanwhile. Mirrored in `docs/open-questions.md`. Status: **open** (owner WK-1178, raised 2026-09-30). *(Cross-reference added 2026-09-30, on the maintainer's instruction: if this question is decided (a), rounding recorded as its own rung, `RL-1329`'s R0 ("`round` appears only on the last rung") must be amended by that ruling; `RL-1329` says so itself.)* |
| **OQ-1321** | **OPEN** — **Should a `lookup` step's output be typed from its reference table's declared column type?** A lookup's output is always a string (`runtime.py:239-240`), and `RL-1322` (correcting `RL-1312`) adds `number(x)` to FR-244 so that it can be used in arithmetic. A non-numeric value then fails at scoring. FR-227's result type is not declared on a lookup. Raised 2026-09-30 by the decision-maker (`RL-1322`). Mirrored in `docs/open-questions.md`. Status: **open** (owner WK-1178). |
| ~~**OQ-1334**~~ ✔ | ~~Should `/score` serve a declared `decimal` output as a JSON string, as batch scoring does, instead of the float JSON number it serves today?~~ **DECIDED 2026-09-30: (a), a JSON string on every scoring path, the engine's exact value rounded once by its output step; a `decimal` output may carry money; owner WK-1178, after WK-674 Slice 3 merges, by `RL-1343`.** See FR-214's dated clause. Mirrored in `docs/open-questions.md`. Status: **decided** (owner WK-1178, delivery after WK-674 Slice 3 merges, raised 2026-09-30, decided 2026-09-30). |
| **OQ-1373** | **What does NFR-500's "sampled-trace schema" name?** Raised 2026-10-01 (working id 9774, allocated by the lead), as the OQ that `CR-1247` Proposal 11's accepted clause requires. NFR-500 (`:1201`) budgets trace storage "with the sampled-trace schema" and names no schema; it is measured failing, about 2.58×. Options: (a) the `Trace` contract after the F55/F35 trim, measured uncompressed; (b) the persisted encoding with a named compression; (c) both: the trimmed `Trace`, persisted with a named compression, the budget stated for the persisted bytes. Recommendation (the planner's): **(a)**. Owner: the F35 plan (`PL-1520`, WK-1178), ruled by the decision-maker with its `TraceStep` ruling. Mirrored in `docs/open-questions.md`. Status: **open** (raised 2026-10-01). |
| ~~**OQ-1440**~~ ✔ | ~~What latency budget does a rate-table cells-diff page (`GET …/diff/cells`) carry below `07` §1.3 R1's 2 s, on the rows path and on the parquet path, and at what table size: is a page a "metadata read" under `00` NFR-457 (300 ms p95), or what other interactive budget does it carry?~~ **DECIDED 2026-10-05: (b) plus (e), one route NFR in §9 for both storage paths (p95 ≤ 300 ms for every page after the first request for a key, measured at n ≥ 100 at 250 000 cells on rows and 1 000 000 on parquet) and a page cost bounded by its `limit` (page p95 at 250 000 cells within 2× of that at 10 000); (a), (c) and (d) not taken; by RL-1441, on the maintainer's (by delegation) entry "2026-10-05 20:58:27 BST — FD 9487 and OQ 9486 drafts: the severity path accepted; OQ 9486 DECIDED as (b)+(e)".** Its §9 row is the ruling's T1, applied by SL-1391 (S7, WK-673). Raised 2026-10-05 (working id 9486, minted as OQ-1440) by the decision-maker, on the maintainer's (by delegation) filing rule for the WK-673 Slice 7 cost measurement; its trigger is FD-1439. R1 and NFR-457 bound the route (the maintainer's (by delegation) entry of 2026-10-05 20:53:32 BST, which makes a rows page p99 ≤ 2 s at 250 000 cells S7's merge condition); this question is the budget below R1. At 260 000 cells a page measured parquet p50 948 / p99 1098 ms and rows p50 9604 / p99 9995 ms (n=10, `limit` 50, #1206 at `386f4d54`). Options: (a) a page is a metadata read, NFR-457's 300 ms p95 as written; (b) one route NFR for both paths at stated sizes; (c) per-path budgets; (d) no budget below R1; with (e), a page cost bounded by `limit`, not by the table size. Recommendation on file: (b) at 300 ms, with (e). Mirrored in `docs/open-questions.md`. Status: **decided** (owner WK-673, applied by FD-1439's fix slice in WK-1178, raised 2026-10-05, decided 2026-10-05). |
| ~~**OQ-1450**~~ ✔ | ~~Which `input_contract` and `outputs` does a proper attribution subset bundle declare?~~ **DECIDED 2026-10-05: (c), the baseline's with each delta whose change is in the subset applied, a removed input and a changed type included; changes that depend on each other must share a group, refused up front, by RL-1449.** FR-1398 and FR-1399 are amended by WK-673 Slice 3 with its code (RL-1449's T1 to T3); a contract or output delta travels with the one step change that reads or writes it, otherwise it is its own change (RL-1449 DP-3, (β), 2026-10-05 13:04:03 BST). Raised 2026-10-03 by `RL-1394` under working id 9739. Mirrored in `docs/open-questions.md`. Status: **decided (c), the maintainer by delegation, "2026-10-05 12:58:22 BST — DECISIONS (the maintainer, by delegation): FD 9780; DP-A; OQ-1450; RL-1449 DP-2; PL 9716 DP-B; the OQ-1450 row", items 3, 4 and 6** (owner SL-1387, raised 2026-10-03, decided 2026-10-05). |
| ~~**OQ-1453**~~ ✔ | ~~**Does NFR-489's real-time p99 ceiling cover TRACED requests?**~~ **DECIDED 2026-10-05: (a). NFR-489's p99 ceiling (< 50 ms with one GBM call, < 15 ms without) governs UNTRACED real-time requests. A traced request (a caller-requested FR-258 inline trace) is bounded by NFR-490 instead (tracing adds ≤ 20 % to scoring latency).** Raised 2026-10-01 by the auditor (working id 9777), from F35's re-own: SL-1345's traced p99 of 68.015 ms and 69.874 ms is above NFR-489's 50 ms ceiling if that ceiling covers traced requests. The maintainer's lean is (a), untraced only, with traced requests bounded by NFR-490. Mirrored in `docs/open-questions.md`. Status: **decided (a), the maintainer by delegation, "2026-10-05 10:47:03 BST — OQ-1453 (#1048) DECIDED (a); the combined mint order ACCEPTED; pairing coupled records in one mint PR ACCEPTED (max 3 records per PR)"** (owner SL-1259, raised 2026-10-01). |
| **OQ-1460** | **Should a Peril Structure `model_call` carry per-peril risk-premium components as outputs (FR-249), and in what shape?** Raised 2026-10-05 (working id 9570, reserved by the lead) by the decision-maker in `RL-1459`, on the maintainer's (by delegation) ruling in the entry "2026-10-05 17:08:35 BST — A-3 / A-4 DP memo (handover/dp-memo-a3-a4-2026-10-05.md) RULED; the reconciliation TOLERANCE set", item 2: "FR-249's per-peril map (PL-1286 puts it in WK-675 S6, which has no backend producer under DP-A3-1 (c)): a NEW 03 OQ, owner WK-1178, decided after G2: a dated carry. WK-675 S6's FR-249 limb is carried with it (recorded in S6's dispatch record when S6 is planned), so S6 does not build a view with no producer." At `4d3be141`: `_model_call_handler` (`packages/pricing-core/src/pricing_core/rating/runtime.py`) writes one value to every produced name; `03` §4's example declares `peril_risk_premium` as `map<string, money_minor>`, and no `map<` type is handled in `model_schema/rating.py` or `pricing_core/rating`. `RL-1459` item 4 makes a Peril Structure `model_call` declare exactly one produced name in P2, so FR-249 has no producer until this is decided. Options: (a) **A second produced name typed as a per-peril map** `{peril: money_minor}`: meets FR-249 as `03` §4's example declares it; a map has never crossed ZEN's pass-through, FR-226's rounding or the ladder, so it needs a spike first. (b) **One scalar produced name per peril** (e.g. `peril_ad_risk_premium_minor`), declared by the step: uses existing scalar types; the step's outputs depend on the structure's perils, so a new structure version can change the step's shape. (c) **Per-peril components in the trace only**, not as outputs: no output-contract change; does not meet FR-249's "available as outputs" for monitoring (`05`) and reinsurance analysis. Recommendation: **(a)**, after a spike *(the decision-maker's, in `RL-1459`)*: it is the shape `03` §4 already declares, and FR-249's consumers read a keyed map rather than names that vary with the structure; the spike measures the map through ZEN, the rounding and the ladder before the build. Mirrored in `docs/open-questions.md`. Owner WK-1178 now, **re-decided at the Fri 2026-10-09 checkpoint**; if no slice fits before the Wed 2026-11-04 code freeze it carries into Phase 3, listed in the P2 phase closure record; WK-675 S6 shows per-peril output as absent meanwhile (carry text accepted in the maintainer's (by delegation) entry "2026-10-05 17:12:40 BST — CORRECTION to my 17:02:50 rounding ruling: OPTION (B); A-2 gains the model-schema field; C4 stays (c); FR-249 carry text accepted"). Status: **open** (owner WK-1178; raised 2026-10-05). |
| **OQ-1539** | **Should compile refuse a seeded rate table applied as an absolute relativity where a `model_call` in the same Rating Version reaches the table's source model, so the double count FR-230's clarification forbids is enforced rather than conventional?** Raised 2026-10-05 (working id 9587, reserved by the lead) by the decision-maker in `RL-1538`, on the maintainer's (by delegation) ruling in the entry "2026-10-05 16:54:17 BST — CLEANUP NOW (the maintainer chose "now, before lane A starts", window to ~17:20 BST); the missing 16:47 slot order; WK-1250 S2 DPs and the DOUBLE-COUNT DP RULED": "B2 (a `relative_to: seed` field plus a compile refusal, +0.5–1 executor-day): raised as a NEW 03 OQ, owner WK-1178, decided AFTER G2". `RL-1538` rules Option B, built as B1: a seeded table enters the price as its ratio to its seed origin, written with two `table` steps and an `expression` step. Nothing checks that form. At `137bc817`, `seeded_from` is read by neither `pricing_core/rating/compile.py` nor `pricing_core/rating/runtime.py`, so an algorithm that multiplies the `model_call` output by the absolute seeded table compiles and scores, and counts the source model's effect twice, silently. Options: (a) **B2: declare and refuse.** The `table` step gains `relative_to: seed` (a field, not an eighth step type); compile resolves the seed origin itself and refuses, with a new registered code, an absolute seeded table whose `seeded_from` model is reachable from a `model_call` in the same version. Cost: `model-schema`, contract regeneration (FR-451) and compile, about +0.5–1 executor-day. (b) **Stay with B1's convention**, and surface the seed lineage of every table on the premium path at approval (`06`) instead of refusing. Cheaper; still silent at compile. Recommendation (the decision-maker's): **(a)**, after G2: the double count is a mispricing that nothing reports, and a declared field makes the form checkable rather than a reading of the expression. Not needed for the exit demo if B1's Task 0 (A-4, PL-1542) passes; if Task 0 fails, B2 becomes required before then (`RL-1538` Ruled 3). Owner: WK-1178, ruled by the decision-maker after G2. Mirrored in `docs/open-questions.md`. Status: **open** (raised 2026-10-05). |
