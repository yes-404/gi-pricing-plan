# 01 — Data Management

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `DATA`
**Prerequisites:** [`00-overview.md`](00-overview.md) — read §2 (glossary) and §4 (entity map) first.

---

## 1. Purpose & scope

### 1.1 In scope

This module owns everything between "an actuary has a file or a database connection" and
"a Dataset Version is `validated` and safe to fit a model on":

1. **Ingestion** — registering sources, loading policy/claims/exposure data into an
   immutable Dataset Version stored as parquet.
2. **Schema inference and declaration** — deriving a candidate pandera schema, letting the
   user correct it, freezing it with the version.
3. **Preparation** — the deterministic, declarative transformations applied on the way in:
   type coercion, date parsing, currency normalisation, policy–claim joining, exposure
   derivation, deduplication.
4. **Validation** — the four-layer gate (structural, referential, actuarial sanity,
   distributional) that decides whether a Dataset Version may be modelled on.
5. **Profiling** — descriptive statistics and one-way summaries used everywhere
   downstream.
6. **Reference data** — effective-dated lookup tables (postcode→area, vehicle group,
   occupation) used by validation and by the rating engine.
7. **Dataset lineage** — derived datasets (samples, splits, filtered cohorts) that record
   what they came from and how.

### 1.2 Out of scope

| Not here | Where instead |
|---|---|
| Factors, bandings, groupings | `02-modelling.md` — they are *modelling* transformations of a validated dataset, deliberately not baked into the dataset |
| Feature engineering that encodes modelling judgement | `02-modelling.md` |
| Rate tables and reference data *lookups at scoring time* | `03-rating-engine.md` (it consumes our Reference Table Versions) |
| Data warehousing, ETL from source systems of record | External; we ingest from files, object storage, or a read-only SQL connection |
| PII storage, customer identity resolution | Out of platform (FR-OVR-9) |
| **IBNR and claims-development adjustment** | **Out of platform.** The user supplies developed data; the platform consumes it as given and warns where experience is immature (`VR-ACT-14`). Development is an actuarial exercise with its own methods, judgement and review, and a pricing platform that half-performed it would produce developed amounts nobody had signed off (OQ-DATA-4, decided 2026-08-14) |

### 1.3 The single most important rule

> **A Model may only be fitted on a Dataset Version whose status is `validated`.**
> There is no override, no "force fit", and no admin bypass. If an actuary believes a
> failing rule is wrong, the rule is changed (and that change is reviewed and audited) —
> the gate is not skipped.

---

## 2. Concepts & glossary

Terms defined in `00-overview.md` §2.1 (Dataset, Dataset Version, Record grain, Exposure,
Reference Table, Validation Rule, Validation Report, Acknowledgement, Profile, PSI) are
used here unchanged. Additional terms owned by this module:

| Term | Definition |
|---|---|
| **Source** | A registered origin of data: `upload` (file), `object_store` (S3 prefix), `sql` (read-only connection + query), `pipeline` (Dagster asset). Holds connection config and credentials by reference, never inline. |
| **Ingestion Run** | One execution of a Source into a new Dataset Version. A Job (FR-OVR-10). Records row counts in/out, rejected rows, and the exact preparation recipe applied. |
| **Preparation Recipe** | The declarative, ordered list of preparation steps applied during ingestion. Stored with the Dataset Version; re-running it on the same source bytes reproduces the same version (FR-OVR-8). |
| **Dataset Table** | One parquet table within a Dataset Version, with a `record_grain` and a pandera schema. A Dataset Version typically has `policy_exposure` and `claim` tables, sometimes more. |
| **Validation Rule Set** | The named, versioned collection of Validation Rules bound to a Dataset. Changing it creates a new Rule Set version and invalidates nothing retrospectively — old reports keep the rule set version they ran under. |
| **Rule Outcome** | Per-rule result: `pass` · `warn` · `fail` · `error` (the rule itself blew up) · `skipped` (a dependency was unavailable). |
| **Offending Sample** | Up to N (default 100) primary keys of rows that triggered a non-pass outcome, persisted with the report so an actuary can go look. |
| **Reference Dataset Version** | The Dataset Version a distributional rule compares against — usually the prior period's data. Pinned explicitly on the Rule Set, never inferred as "the previous one". |
| **Derived Dataset Version** | A Dataset Version produced from another by a recorded operation (`sample`, `split`, `filter`, `union`), carrying `parent_id` and the operation's parameters. |
| **Data Dictionary** | Per-column metadata for a Dataset: business description, unit, source system, PII classification, allowed values. Lives on the Dataset (not the version) and is inherited, so descriptions are not retyped per version. |

---

## 3. Functional requirements

### 3.1 Sources & ingestion

| ID | Requirement |
|---|---|
| **FR-DATA-1** | An Analyst can register a **Source** of type `upload`, `object_store`, `sql`, or `pipeline`. Credentials are stored as a reference to a platform secret (`07-platform.md`), never in the Source record, and are never returned by any API. |
| **FR-DATA-2** | An Ingestion Run creates exactly one new Dataset Version at `version = max(existing) + 1`, status `draft`. Ingestion never mutates an existing version. If a run fails, the partially written version is marked `failed` and its blobs garbage-collected; the version number is consumed, not reused (ID-2). |
| **FR-DATA-3** | The platform accepts CSV, TSV, parquet, and Excel (`.xlsx`, first sheet or a named sheet) for `upload`/`object_store` sources, and any query result for `sql`. Compressed variants (`.gz`, `.zst`) are transparently handled. |
| **FR-DATA-4** | On first ingestion the platform **infers** a candidate schema (column names, dtypes, nullability, cardinality, candidate keys, date formats) and presents it for confirmation. The user may correct any inference before the version leaves `draft`. Subsequent versions of the same Dataset default to the previous version's schema. |
| **FR-DATA-5** | Column names are normalised to `snake_case` on ingest; the original name is retained in the Data Dictionary as `source_name`. The normalisation is deterministic and collision-detecting (a collision is an ingestion error, not a silent rename). |
| **FR-DATA-6** | Ingestion records, per run: rows read, rows written, rows rejected with reject reason and a sample, bytes read, duration, source fingerprint (file sha256 / query text hash + extraction timestamp), and library versions. |
| **FR-DATA-7** | Rows that cannot be parsed at all (malformed CSV, unparseable dates in a required date column) are **rejected to a quarantine table** stored with the version rather than dropped silently. A version with rejects can still be validated; a configurable rule (`ingest.reject_rate`) fails it above a threshold. |
| **FR-DATA-8** | Ingestion is resumable and idempotent: re-running an Ingestion Run with the same `Idempotency-Key` and unchanged source fingerprint returns the original Dataset Version rather than creating another. |
| **FR-DATA-40** | **Ingestion produces full snapshots** (OQ-DATA-2, decided 2026-08-14). A Dataset Version is always a complete, independently validatable body of data — never a delta against a predecessor. Should an `append` mode be added later (Phase 2), it must still **materialise a complete, content-addressed version** so that FR-OVR-1 immutability and the validation model are unaffected and only the *cost* of producing it changes. Content-addressing (ID-4) already deduplicates unchanged parquet parts across versions, so most of the storage saving is available without an append mode at all. |

### 3.2 Preparation

| ID | Requirement |
|---|---|
| **FR-DATA-9** | A **Preparation Recipe** is an ordered list of declarative steps applied during ingestion. Supported step types are exactly: `rename`, `cast`, `parse_date`, `trim_whitespace`, `normalise_case`, `map_values`, `fill_null`, `derive_expression`, `filter_rows`, `deduplicate`, `join_table`, `derive_exposure`, `explode_period`, `attach_claims`, `pseudonymise`. No free-form code. |
| **FR-DATA-10** | `derive_expression` accepts a restricted expression over existing columns (the same restricted expression grammar defined in `02-modelling.md` §4.6 for custom objectives, minus statistical functions). It cannot call out to the network, filesystem, or Python builtins. |
| **FR-DATA-11** | `explode_period` splits a policy record spanning a mid-term change or a period boundary into multiple exposure rows with correctly apportioned exposure, preserving `sum(exposure)` exactly (checked as a post-condition, using `Decimal`). |
| **FR-DATA-12** | `attach_claims` links the claim table to the policy-exposure table on a declared key and validates the linkage: every claim resolves to exactly one exposure row, and the claim's `date_of_loss` falls inside that row's exposure period. Unlinked claims and multi-linked claims are reported as counts and samples, and are individually rule-gated (see VR-ACT-6, VR-ACT-7). |
| **FR-DATA-13** | `pseudonymise` replaces a declared identifier column with a stable HMAC (workspace-scoped key), so the same customer maps to the same token across versions but the token is meaningless outside the workspace. Columns classified `direct_identifier` in the Data Dictionary must be dropped or pseudonymised; otherwise ingestion fails (FR-OVR-9). |
| **FR-DATA-41** | *(appended 2026-08-15, and numbered rather than suffixed — §5's ids are append-only)* The refusal in FR-DATA-13 is enforced **at ingestion**, before any row is written: a source whose columns include one the Data Dictionary classifies `direct_identifier`, and whose recipe neither drops nor pseudonymises it, is rejected with `DIRECT_IDENTIFIER_PRESENT`. `Dataset.modelling_forbidden_columns` names the classes that trigger it, and `special_category` is refused on the same terms. **Delivered 2026-08-15.** |
| **FR-DATA-14** | The Preparation Recipe is persisted with the Dataset Version and is replayable: `replay(recipe, source_bytes) == stored version` byte-for-byte on parquet content hash, given pinned library versions. |

### 3.3 Validation — the gate

| ID | Requirement |
|---|---|
| **FR-DATA-15** | Validation runs as a Job against a `draft` Dataset Version, executing every rule in the Dataset's Validation Rule Set and producing exactly one **Validation Report** per run. Reports are immutable and retained; re-validation creates a new report, it does not overwrite. |
| **FR-DATA-42** | *(appended 2026-08-15)* "Immutable" is enforced **in the database**, not by convention: `validation_reports`, `profiles` and `validation_acknowledgements` carry append-only triggers refusing `UPDATE`, `DELETE` and `TRUNCATE`, as `audit_events` already does (`06` FR-GOV-22), together with `SELECT, INSERT`-only privileges for the application role. `blobs` is **not** append-only — see the amendment below — but its content columns (`sha256`, `bytes`, `media_type`) may never change. **Delivered 2026-08-15.** |
| **FR-DATA-47** | *(appended 2026-08-18, W5, the backtest slice)* **Every artifact table carries both layers, and three do not.** FR-DATA-42's trigger exists because revoking `UPDATE` from the *owner* does nothing — ownership carries implicit privileges — so a table with the grants alone is protected against the application role and not against a direct connection. `diagnostics`, `model_comparisons` and `transparency_artifacts` were each created with the grants and **no trigger at all**; measured on a migrated database, 2026-08-18: two triggers each on `validation_reports`, `profiles`, `validation_acknowledgements` and `backtests`, zero on those three. Each is evidence something is approved against — `02` §4.8 makes diagnostics the condition of `fitted`, and `06` §3.3 makes a comparison required evidence for a Model approval where a predecessor exists. **Verdict: not started, and not this slice's** — `backtests` was built with both layers and the first test in the repository to exercise a trigger rather than only the grants (`backend/tests/test_backtests.py`), which is the pattern the fix follows. **Owner: W5's next slice or W13, whichever reaches it first**; the migration is three tables through the loop `a1b2c3d4e5f6` already writes, plus a negative test each. **Delivered 2026-08-18 (W5), and the count was wrong: six, not three.** Measuring the invariant across every table rather than re-reading the three found `bandings`, `groupings` and `objective_certificates` each carrying the `TRUNCATE` trigger and not the row one — and `c3d4e5f6a7b8` asserting in a comment that a direct `UPDATE` was refused while it was not. `e1f2a3b4c5d6` attaches the missing triggers to all six. The requirement is therefore **stated as an invariant and checked as one**: a table whose grants are exactly `SELECT, INSERT` is a table the schema has declared append-only, and it must carry both triggers. `backend/tests/test_artifact_immutability.py` derives its table list from those grants rather than restating it, so the next artifact table built with the grants alone fails a test on the day it is added; a companion test pins the grant set itself, since a table quietly regranted `UPDATE` would otherwise drop out of the derived set unchecked. `blobs` and `custom_objectives` are correctly outside it — both hold `UPDATE` for a reason FR-DATA-42 records, and both carry their own narrower trigger. |
| **FR-DATA-16** | Validation covers four layers, all of which must be present in every Rule Set (a Rule Set with an empty layer is a configuration warning surfaced in the UI): **structural**, **referential**, **actuarial sanity**, **distributional/stability**. §4.4 enumerates the built-in rules. |
| **FR-DATA-17** | Transition to `validated` requires: zero `fail` outcomes, zero `error` outcomes, and every `warn` outcome carrying an **Acknowledgement** by a Pricing Actuary with a non-empty justification (audited, FR-OVR-4). An Analyst cannot acknowledge. |
| **FR-DATA-18** | An Acknowledgement is scoped to `(dataset_version_id, rule_id, report_id)`. It does not carry forward to the next version or the next report — each version's warnings are acknowledged on their own evidence. The UI **may pre-fill** the justification from the last acknowledgement of the same rule, but the act itself is always explicit and separately audited: fatigue is a UI problem, and a standing acknowledgement that goes stale hides the change it was meant to surface (OQ-DATA-6, decided 2026-08-14). |
| **FR-DATA-19** | Rules execute independently; one rule's `error` does not prevent others from running. A rule that exceeds its time budget is recorded as `error` with reason `timeout`, and blocks validation (an unrun rule is never treated as a pass). |
| **FR-DATA-20** | Every non-pass outcome persists: rule id and version, severity, affected row count, affected exposure, the measured value vs the threshold, and an Offending Sample of up to 100 primary keys. |
| **FR-DATA-21** | Users can define **custom Validation Rules** declaratively (§4.5). A custom rule is an Artifact with its own `draft → review → approved` lifecycle; only `approved` rules may run in a Rule Set used for a Dataset feeding an `approved` Model. |
| **FR-DATA-22** | A Rule Set is versioned. A Validation Report records the exact `rule_set_version` and each `rule_version` it executed, so an old report remains interpretable after rules change. |
| **FR-DATA-43** | *(appended 2026-08-15, found by driving the exit demo)* A `validating` version whose report contains `fail`s transitions to **`failed`**, not left in `validating`. `validating` is a transient state — a version resting in it reads as "still running" on every screen that shows a status, and `FAILED → VALIDATING` exists precisely so a failed version can be re-validated once the data or the rule set is corrected. A version already `validated` and re-validated to a failing report goes to **`draft`** instead, which is FR-DATA-23 — it *was* good, and the report reference is cleared with the status. **Delivered 2026-08-15** (OQ-DATA-7, decided). |
| **FR-DATA-23** | Validation is re-runnable on a `validated` version (e.g. after a rule set update). If the new report contains `fail`s, the version transitions **back** to `draft` and every Model fitted on it is flagged `dataset_invalidated` — models are not deleted, but the flag is surfaced on the model, on any Rating Version referencing it, and to the Approver. |
| **FR-DATA-24** | Validation is incremental where sound: structural and actuarial rules stream over parquet row groups; distributional rules use pre-computed profile aggregates rather than re-scanning. |
| **FR-DATA-50** | *(appended 2026-08-19, OQ-DATA-9 decided)* The dataset list's **status badge and last-validated date are projections of Dataset Versions, not fields on `Dataset`.** The container gains neither: `DatasetVersion.status` together with `is_fittable` is the single answer to "can I fit on this?" (§1.3), and a second status on `Dataset` would be a second answer free to disagree with it. `GET /api/v1/datasets` therefore returns two derived, read-only fields alongside `latest_version`: **`latest_version_status`**, the status of the version `latest_version` names, and **`last_validated_at`**, the transition timestamp of the most recently `validated` version of the Dataset — which **need not be the latest one**. The two are scoped differently on purpose: the badge answers *what state is the newest version in*, the date answers *when was this Dataset last usable*, and a Dataset whose v12 is a fresh `draft` above a `validated` v11 would otherwise render as never validated. Where the two refer to different versions the list states which, so the pair cannot be read as one fact. Both are computed per request from `dataset_versions`; neither is stored on `datasets`, and neither is writable. **Not delivered. Phase 1b, owner W6b** — the list endpoint already batches the latest version per dataset (`_latest_versions`), so this is one further aggregate plus the two columns in the view. Trigger: the slice that completes §5.3's Dataset list row. |

> **Two enforcement gaps, recorded 2026-08-15 after an independent audit — and closed the
> same day.** Both were cases where the requirement was right and the code did not meet it,
> so the spec gained the precise obligation rather than being softened to match. The record
> of what was wrong stays below; what changed is that FR-DATA-41 and FR-DATA-42 are now
> delivered, each with the deliberately-broken-input proof `CLAUDE.md` §13 rule 4 requires —
> five injections, five caught.
>
> **FR-DATA-13's refusal does not happen.** `DIRECT_IDENTIFIER_PRESENT` is registered in
> the error catalogue and raised nowhere; `Dataset.modelling_forbidden_columns` has no
> caller. All four `FR-DATA-13` test markers sit on `pseudonymise`, the requirement's
> *other* half, and FR-OVR-9 — which states the same rule at system level — carries no
> marker at all. A dataset carrying a direct identifier ingests today.
>
> **FR-DATA-15's immutability is convention.** Only `audit_events` has append-only
> triggers. An audit rewrote 190 stored reports from `fail` to `pass` in one statement
> (rolled back). `docs/roadmap.md` §5 lists artifact immutability among the things that
> cannot be retrofitted cheaply, and Phase 1a was where it was meant to land.
>
> **Amended when FR-DATA-42 was built, 2026-08-15: `blobs` is not one of the append-only
> tables.** As first written the requirement named it, and building it found why it cannot
> be: `ref_count` is updated on every reference and release (FR-PLAT-22), and
> reference-counted garbage collection *deletes* unreferenced rows. A blob's **content** is
> immutable for a stronger reason than a trigger — the row is keyed by the sha256 of its
> bytes, so changed content is a different row. What the trigger adds there is a guard that
> `sha256`, `bytes` and `media_type` can never be updated, leaving the lifecycle columns
> free. The requirement is corrected rather than the table quietly dropped from the
> migration.
>
> They were owned by W6b and delivered in Phase 1a as a gate on its exit demo (plan review
> 2, accepted 2026-08-15). The proofs: the refusal removed, the recipe remedy ignored, the
> row trigger dropped, the statement trigger dropped, and `UPDATE` granted back to the
> application role — a trigger nobody has tried to defeat is the same kind of claim these
> notes exist to stop.

### 3.4 Profiling

| ID | Requirement |
|---|---|
| **FR-DATA-25** | Profiling runs automatically after successful ingestion and produces, per column: null count and rate, distinct count, min/max, mean/std (numeric), percentiles (p1, p5, p25, p50, p75, p95, p99), top-20 levels by exposure and by count (categorical), and inferred semantic type (`identifier`, `categorical`, `ordinal`, `continuous`, `date`, `money`, `boolean`). |
| **FR-DATA-26** | Profiling additionally produces **one-way summaries** per candidate rating column: exposure, claim count, claim amount, observed frequency, severity, and burning cost by level or banded interval, with Poisson/Gamma confidence intervals. These are the inputs to the factor workbench in `02-modelling.md` and are computed once, here. |
| **FR-DATA-27** | Profiles are computed with DuckDB directly over the version's parquet files and persisted as an artifact. The UI never recomputes a profile client-side or ad-hoc on request. |
| **FR-DATA-28** | A **profile comparison** between any two Dataset Versions of the same Dataset is available on demand: per-column PSI, mean shift, null-rate shift, new/vanished levels. This is the same computation that the distributional validation layer consumes. |
| **FR-DATA-46** | *(appended 2026-08-17; OQ-OVR-7, decided)* FR-DATA-26's one-way row names its two mean fields **`mean_severity`** and **`mean_burning_cost`** — not `severity_minor` and `burning_cost_minor`. Both are means and therefore floats, kept as floats deliberately, because rounding a mean to whole minor units would lose the precision the confidence interval beside it expresses. The values are right; the *names* are what FR-OVR-7 objects to, since `_minor` is reserved for integer minor units. Both stay expressed in the workspace currency's minor unit, so only the names change. **Delivered 2026-08-18**, in the slice that added FR-DATA-48's histogram — the change to the profile contract OQ-OVR-7 was waiting for. The hand-written money-scan exclusion in `backend/tests/test_contracts.py` is deleted: `mean_severity` and `mean_burning_cost` do not match the scan's pattern, so nothing needs excluding. **Corrected 2026-08-19**: the rename carried the *names* and left the *types* — both fields went on declaring `MoneyMinor`, that is `{"type": "integer"}`, in the hand-authored `profile.schema.json` and `banding.schema.json`, so the published contract asserted exactly the rounding this requirement forbids. The divergence predates the rename; nothing caught it because every conformance test compared field names only. §4.7's note of that date carries the finding, the correction, and the type comparison that now enforces it. |
| **FR-DATA-48** | *(appended 2026-08-18; `ColumnProfile` had no `histogram` while `01` §4.7's contract example, `docs/contracts/schemas/profile.schema.json` and §5.3's Profile view all declared one — a divergence recorded in `docs/roadmap.md` and built around in silence since 2026-08-15.)* Profiling additionally produces, for every **numeric non-identifier** column, a **histogram**: `HISTOGRAM_BINS` (20) equal-width bins over the observed `[min, max]`, published as `edges` (one more than there are bins), `counts`, and — where the version carries an exposure column — one exact decimal `exposure` weight per bin. Bins are half-open, `[e(i), e(i+1))`, except the last, which is closed. A constant column yields a single bin. **Equal-width bins over the observed range, computed from edges chosen in Python rather than by either engine's own histogram function**: FR-DATA-27 requires one answer regardless of engine, and every divergence `test_the_two_profiling_paths_agree` has ever caught came from an engine default — tie-breaking, null handling, quantile interpolation. |
| **FR-DATA-49** | *(appended 2026-08-18, Task 6 — the profile contract's generated counterpart, comparing `docs/contracts/schemas/profile.schema.json` against `ColumnProfile` for the first time.)* **`ColumnProfile.top_levels` must carry `exposure_years` per level, not only `count`.** FR-DATA-25 asks for "top-20 levels by exposure and by count", and the contract has always declared each top level as `{level, count, exposure_years}` — but the model carries `top_levels: tuple[tuple[str, int], ...]`, a two-element tuple with no exposure weight and no field names, so a top-20 by count is silently substituted for a top-20 by exposure wherever it is read. **Not fixed in this slice, on the controller's ruling**: closing the gap means computing per-level exposure in both profiling engines (`profile_frame` and `profile_parquet`) and reworking every reader that treats `top_levels` as `(str, int)` — `compare_profiles` and `psi_from_weights` in `pricing_core.data.profile`, the distributional validation layer's `_level_counts`/PSI checks in `pricing_core.data.validate`, and `ProfileView.vue`'s chip list — 22 call sites across 7 non-generated files by the count taken 2026-08-18. That is a feature the size of FR-DATA-48's histogram work, not a reconciliation, so `backend/tests/test_contracts.py`'s nested conformance test compares `ColumnProfile`'s property *names* only (where `top_levels` exists on both sides and this gap is invisible) rather than each item's shape. **Owner: W5's next slice or whoever picks up FR-DATA-49**, no trigger beyond "before `top_levels` is read anywhere the exposure-vs-count distinction matters for a pricing decision". |


### 3.5 Reference data

| ID | Requirement |
|---|---|
| **FR-DATA-29** | A **Reference Table** holds effective-dated lookup rows with a declared key, declared payload columns, and half-open `[effective_from, effective_to)` validity (FR-OVR-12). Overlapping intervals for the same key are rejected at load time. |
| **FR-DATA-30** | Reference Table Versions are immutable and independently approvable. Both validation (referential layer) and the rating engine pin an explicit Reference Table Version — neither ever resolves "latest" at runtime. |
| **FR-DATA-31** | A reference lookup is evaluated **as at a declared date** (typically the policy inception date), not as at "now". The date column used is declared on the rule or the rating step. |
| **FR-DATA-32** | The platform ships **loaders** for the common UK reference sets: ONS postcode directory, ABI vehicle group tables, occupation/industry code lists, and a bank-holiday calendar. Each is a Reference Table like any other — no special-casing in the engine. **Actual rows are shipped only where the licence is unambiguously permissive** (ONS NSPL and the bank-holiday calendar, both OGL); every other source ships a loader and a documented fetch step. **ABI vehicle group tables are never shipped** — they are not freely redistributable, and bundling them would put a licence breach in every clone of the repository (OQ-DATA-5, decided 2026-08-14). |

### 3.6 Derived datasets & lineage

| ID | Requirement |
|---|---|
| **FR-DATA-33** | Derived Dataset Versions are produced by declared operations — `sample` (with seed and method: random, stratified, exposure-weighted), `split` (train/test/validation with seed and method: random, temporal, grouped-by-key), `filter` (restricted expression), `union` — each recording its parameters and `parent_id`. |
| **FR-DATA-34** | A Derived Dataset Version inherits its parent's schema, Data Dictionary, and Rule Set, and must be validated in its own right — but rules can be marked `skip_on_derived` where they are meaningless (e.g. a volume-based distributional check on a 1 % sample). |
| **FR-DATA-35** | Lineage is queryable in both directions: "what was this built from?" and "what depends on this?" — the latter spanning Models, Rating Versions, and Monitoring baselines (used to compute the blast radius of FR-DATA-23). |
| **FR-DATA-36** | Train/test splits are recorded on the *parent* version as a named split artifact, so that two models can be compared on provably identical holdout rows. |
| **FR-DATA-44** | A derived version produced by `split` **holds its part's rows**, not its parent's. Added 2026-08-16 (W5, diagnostics), because FR-DATA-33's "produced by declared operations" and FR-DATA-34's "inherits its parent's schema, Data Dictionary and Rule Set" had been implemented as inheriting the parent's *data*: `dataset.derive` recorded the operation and pointed the child at the parent's blob. A 1 % sample therefore held 100 % of the rows, and a train/test split produced two versions each containing everything — so a model "fitted on train" was fitted on all of it and its "holdout" contained every training row. The partition is a pure function of the recorded method, seed and fractions, so the `train` Job and the `test` Job agree without coordinating. **Every other operation is refused rather than left inheriting** — FR-DATA-45, which is OQ-DATA-8 decided. |
| **FR-DATA-45** | *(appended 2026-08-17; OQ-DATA-8, decided)* Every declared operation **other than `split` is refused**, with `DERIVATION_NOT_MATERIALISED`, until it produces its own rows. FR-DATA-44 materialised `split` because the diagnostics slice needed an honest holdout; leaving the others inheriting is worse than refusing them, because the failure is silent — a version that records `sample` and holds 100 % of the parent's rows validates, profiles and fits, and every number it produces is the parent's. FR-DATA-33's purpose is that a derivation is reproducible, and a sample nobody sampled can be neither reproduced nor defended. Each is materialised **in the slice that first needs it**, on FR-DATA-44's terms: the child's rows written as its own content-addressed blob, computed as a pure function of the recorded parameters. **Owner: W7 for `sample`** — the demo seed's `--rows` path is the first real caller. `filter`, `join` and `aggregate` are unowned and stay refused until one exists. **Delivered 2026-08-17** (the refusal; the materialisation is the obligation above). |

> **FR-DATA-33's operation list and the implementation's disagree, and FR-DATA-45 is why it
> currently costs nothing.** The requirement names `sample`, `split`, `filter` and `union`;
> `dataset.derive` accepts `sample`, `split`, `filter`, `join` and `aggregate` — so `union`
> is refused as undeclared while two operations nobody specified are accepted. Recorded
> 2026-08-17 rather than silently reconciled (`CLAUDE.md` §0): which side is right is a real
> question — `union` (stack two versions of one schema), `join` (widen by key) and
> `aggregate` (change grain) are three different operations, not one renamed twice.
>
> **Neither side is edited to match the other here**, because FR-DATA-45 now refuses every
> one of them: no caller can reach the difference, and the set is settled by the slice that
> materialises the first of them, which must state which operations exist and amend this
> requirement in the same commit. Until then the implementation's set is the one the error
> message quotes, and `union` is refused twice over.

### 3.7 Access, retention, deletion

| ID | Requirement |
|---|---|
| **FR-DATA-37** | Dataset access is role- and dataset-scoped (`06-governance.md`). A user without read access to a Dataset cannot see it in lineage, in a model's provenance, or in search results — only an opaque "restricted" placeholder. |
| **FR-DATA-38** | `archived` Dataset Versions remain readable to Auditors and remain referenceable by existing Models; they cannot be the target of a new fit. |
| **FR-DATA-39** | GDPR erasure is supported as an Admin-only, audited **purge** of specific pseudonymous subject tokens across all versions of a Dataset, producing a new "redacted" version and a tombstone record explaining the gap. Historic Validation Reports and Models are annotated, never silently altered. |
| **FR-DATA-51** | *(appended 2026-08-19, OQ-DATA-9 decided)* `Dataset` carries an explicit **`owner_id`** — a non-null user id, set to the creating user at ingestion, changeable only by an Admin or the current owner, and audited as a metadata change (FR-OVR-4). It is **not** derived from `workspace_id`: that would make every Dataset in a workspace equally owned, and `06`'s RBAC and approval trails need a named subject — "who owns this data" is a question a workspace cannot answer. Ownership confers no privilege by itself; it names the accountable party a review, a retention decision (FR-DATA-38) or an erasure request (FR-DATA-39) is addressed to, and it is what §5.3's owner column displays. **Not delivered. Phase 1b, owner W6b**, with FR-DATA-50 — a migration adding the column, backfilled from each Dataset's creating audit event, plus the field on `Dataset` in `model-schema`. Trigger: the same slice. |

---

## 4. Data contracts

JSON Schemas live in `docs/contracts/schemas/`. Field types below use JSON Schema
vocabulary; every entity also carries the `ArtifactEnvelope` from `00-overview.md` §4.3.

### 4.1 `Dataset`

```json
{
  "slug": "motor-gb-quote-bind",
  "name": "Motor GB — quote & bind",
  "owner_id": "uuid",
  "line_of_business": "motor",
  "territory": "GB",
  "currency": "GBP",
  "default_record_grain": "policy_exposure",
  "data_dictionary": {
    "policy_id":        {"description": "Pseudonymous policy key", "semantic_type": "identifier", "pii_class": "pseudonymous_key"},
    "exposure_years":   {"description": "Time on risk", "semantic_type": "continuous", "unit": "years"},
    "driver_age":       {"description": "Age of main driver at inception", "semantic_type": "continuous", "unit": "years"},
    "vehicle_group":    {"description": "ABI group 1-50", "semantic_type": "ordinal", "reference_table": "abi-vehicle-group"}
  },
  "validation_rule_set_id": "uuid",
  "latest_version": 12
}
```

`pii_class` ∈ `none | pseudonymous_key | quasi_identifier | direct_identifier | special_category`.
`direct_identifier` and `special_category` columns are rejected for modelling use (FR-OVR-9,
FR-DATA-13).

`owner_id` is FR-DATA-51's accountable party, and it is the **only** one of §5.3's three dataset-list
columns that is a field on `Dataset`. The other two — `latest_version_status` and `last_validated_at` —
are derived per request from the Dataset's versions and returned by `GET /api/v1/datasets`; they are
deliberately absent here, because `Dataset` is a container and FR-DATA-50 keeps `DatasetVersion.status`
the single answer to whether the data is fittable *(OQ-DATA-9, decided 2026-08-19)*.

### 4.2 `DatasetVersion`

```json
{
  "dataset_id": "uuid",
  "version": 12,
  "status": "draft | validating | validated | failed | archived",
  "kind": "ingested | derived",
  "tables": [
    {
      "name": "policy_exposure",
      "record_grain": "policy_exposure",
      "primary_key": ["policy_id", "exposure_start"],
      "row_count": 4821904,
      "blob": {"sha256": "…", "bytes": 412_000_000, "media_type": "application/vnd.apache.parquet", "part_count": 8},
      "pandera_schema_ref": "blob:sha256:…",
      "arrow_schema": {"policy_id": "large_string", "exposure_start": "date32", "exposure_years": "decimal128(9,6)"}
    },
    {"name": "claim", "record_grain": "claim", "primary_key": ["claim_id"], "row_count": 213_884, "blob": {"…": "…"}},
    {"name": "_rejected", "record_grain": "quarantine", "row_count": 17, "blob": {"…": "…"}}
  ],
  "source_id": "uuid",
  "source_fingerprint": {"kind": "file_sha256", "value": "…", "extracted_at": "2026-08-14T09:00:00Z"},
  "preparation_recipe_id": "uuid",
  "ingestion_run_id": "uuid",
  "period_covered": {"from": "2023-01-01", "to": "2026-06-30"},
  "totals": {"exposure_years": "4183221.482", "claim_count": 213884, "claim_amount_minor": 918_442_100_00},
  "validation_report_id": "uuid|null",
  "profile_id": "uuid|null",
  "derived_from": {"parent_version_id": "uuid", "operation": "split", "params": {"method": "temporal", "cutoff": "2025-07-01", "part": "train"}},
  "library_versions": {"polars": "1.x", "duckdb": "1.x", "pandera": "0.x"}
}
```

**Invariants**

- `version` is unique per `dataset_id` and never reused (ID-2).
- `status = validated` ⟹ `validation_report_id` is set, that report's `overall = pass`, and
  every `warn` in it is acknowledged (FR-DATA-17).
- `kind = derived` ⟹ `derived_from` is set.
- `totals.exposure_years > 0`; monetary totals are integer minor units (FR-OVR-7).

### 4.3 `ValidationRule` and `ValidationRuleSet`

A rule is a tagged union on `layer` + `check`:

```json
{
  "slug": "exposure-positive",
  "layer": "actuarial_sanity",
  "check": "range",
  "severity": "fail",
  "target": {"table": "policy_exposure", "column": "exposure_years"},
  "params": {"min_exclusive": 0, "max_inclusive": 1.05},
  "scope": {"filter": null, "skip_on_derived": false},
  "tolerance": {"max_violating_rows": 0, "max_violating_exposure_fraction": 0.0},
  "message": "Exposure must be > 0 and ≤ 1.05 policy-years per exposure row.",
  "rationale": "Zero/negative exposure breaks the frequency offset; > 1.05 indicates a period-splitting bug.",
  "owner": "pricing-actuary@example.com",
  "status": "approved"
}
```

```json
{
  "slug": "motor-gb-standard",
  "version": 4,
  "dataset_id": "uuid",
  "rules": [{"rule_id": "uuid", "rule_version": 2, "enabled": true, "severity_override": null}],
  "reference_dataset_version_id": "uuid",
  "status": "approved"
}
```

**Invariants** — `severity_override` may only *raise* severity (`warn → fail`), never lower
it; lowering requires editing the rule itself, which is a reviewed change (FR-DATA-21).
A Rule Set used by a Dataset feeding an `approved` Model must contain only `approved` rules.

> **Amended 2026-08-15 (W6a).** `PUT /datasets/{slug}/rule-set` takes `rules` — the entries
> above — and not a bare list of rule ids. The first implementation took ids, so neither
> `enabled` nor `severity_override` could be expressed by any caller: a rule could be turned
> off nowhere but in the database, and the "may only raise" invariant guarded something
> unreachable. A downgrade attempt is refused with `RULE_SEVERITY_DOWNGRADE_FORBIDDEN`
> (409). Found by building §5.3's rule-set editor against the API and having nothing to
> bind its enable/disable control to.

### 4.4 Built-in rule catalogue

Rule IDs here are stable and referenced by workflows and by the UI.

**Layer 1 — Structural** (executed against the version's stored `DatasetTableSchema`)

> **Amended 2026-08-15, after an independent audit.** This layer said "executed via the
> stored **pandera** schema", §5.2 declared `compile_pandera_schema(...)`, and §8 tied
> NFR-DATA-2's ≤ 2 min budget to pandera's lazy Narwhals backend. **pandera is not a
> dependency of this repository** — it appears in no `pyproject.toml` and no lockfile —
> and the structural checks are implemented directly over Polars in
> `pricing_core.data.validate`.
>
> The code is the right side here. Every `VR-STR-*` rule below is implemented and tested;
> what pandera would have added is schema *serialisation*, and the version already stores
> its schema as a `DatasetTableSchema`. Adopting a second schema system to restate a shape
> `model-schema` already owns would be the "shape defined twice" hazard `CLAUDE.md` §2
> forbids.
>
> `DatasetTable.pandera_schema_ref` (§4.1) is therefore **unset by anything** and is
> superseded rather than removed — field names are permanent for the same reason
> requirement ids are. NFR-DATA-2's budget is met without it: 0.1 s for the structural
> layer at 2 M rows, against 120 s.

| Rule | Default severity | Check |
|---|---|---|
| `VR-STR-1` column-presence | fail | Every column declared in the schema exists |
| `VR-STR-2` dtype-match | fail | Each column's Arrow dtype matches the declaration (no silent coercion) |
| `VR-STR-3` nullability | fail | Columns declared non-nullable contain no nulls |
| `VR-STR-4` primary-key-unique | fail | Declared primary key is unique and non-null (policy id × exposure period) |
| `VR-STR-5` date-parse | fail | All date columns parsed to `date32`/`timestamp` with no fallback-to-string |
| `VR-STR-6` encoding | warn | No mojibake / invalid UTF-8 sequences in string columns |
| `VR-STR-7` allowed-values | fail | Categorical columns contain only values in the declared domain |
| `VR-STR-8` no-unexpected-columns | warn | No columns present that are absent from the schema |
| `VR-STR-9` reject-rate | fail | Quarantined rows ≤ threshold (default 0.1 % of rows read) — FR-DATA-7 |

**Layer 2 — Referential**

| Rule | Default severity | Check |
|---|---|---|
| `VR-REF-1` reference-resolve | fail | Every value of a reference-backed column resolves in the pinned Reference Table Version, evaluated as at the declared date column (FR-DATA-31) |
| `VR-REF-2` reference-coverage | warn | ≥ X % of reference table keys are exercised by the data (catches a stale or wrong reference version) |
| `VR-REF-3` effective-date-in-range | fail | The declared as-at date lies within the Reference Table Version's covered period |
| `VR-REF-4` cross-table-key | fail | Every `claim.policy_id` exists in `policy_exposure` |
| `VR-REF-5` code-list-drift | warn | New codes present that did not exist in the reference dataset version |

**Layer 3 — Actuarial sanity**

| Rule | Default severity | Check |
|---|---|---|
| `VR-ACT-1` exposure-positive | fail | `exposure_years > 0` for every row |
| `VR-ACT-2` exposure-plausible | fail | `exposure_years ≤ 1.05` per row; annual policies sum to ≈ 1.0 per policy year |
| `VR-ACT-3` exposure-period-consistent | fail | `exposure_end > exposure_start`; `exposure_years ≈ (end − start)/365.25` within tolerance |
| `VR-ACT-4` no-overlapping-exposure | fail | A single `policy_id` has no overlapping exposure intervals |
| `VR-ACT-5` claim-date-in-exposure | fail | `date_of_loss ∈ [exposure_start, exposure_end)` for the linked row (FR-DATA-12) |
| `VR-ACT-6` claim-linkage-complete | fail | 100 % of claims link to exactly one exposure row |
| `VR-ACT-7` claim-not-multi-linked | fail | No claim links to more than one exposure row |
| `VR-ACT-8` claim-count-non-negative | fail | `claim_count ≥ 0`, integer |
| `VR-ACT-9` claim-amount-sign | warn | Negative incurred amounts exist only where recoveries/reversals are expected; flagged with counts |
| `VR-ACT-10` severity-outlier | warn | Claims above a configurable threshold (absolute, or a percentile of the peril's own distribution) are flagged for large-loss treatment — never auto-removed |
| `VR-ACT-11` frequency-plausible | warn | Portfolio and per-peril frequency within a configured band (e.g. motor AD 0.02–0.25) |
| `VR-ACT-12` severity-plausible | warn | Portfolio and per-peril mean severity within a configured band |
| `VR-ACT-13` zero-claim-cohort | warn | No factor level with material exposure (> 1 % of total) has exactly zero claims where the prior version had claims |
| `VR-ACT-14` development-maturity | warn | The most recent N months of experience are flagged as immature (IBNR risk) with the configured development pattern; modelling on them without an adjustment is a warning. **This is the platform's only treatment of development** — adjustment itself is out of scope (§1.2, OQ-DATA-4), so the warning exists to make fitting on immature periods a visible choice rather than an accident |
| `VR-ACT-15` currency-consistency | fail | All monetary columns share the Dataset's declared currency; no mixed-currency rows |
| `VR-ACT-16` duplicate-claim | warn | No two claims share (policy, date_of_loss, peril, amount) — a classic double-load signature |

**Layer 4 — Distributional / stability** (vs `reference_dataset_version_id`)

| Rule | Default severity | Check |
|---|---|---|
| `VR-DST-1` psi-column | the rule's own severity, at `warn_above` | Per-column PSI against the reference version. **Categorical, ordinal and boolean columns only** — the reference weights come from the Profile's `top_levels`, which numeric columns do not carry |
| `VR-DST-2` new-level | warn | Categorical levels present now, absent in reference |
| `VR-DST-3` vanished-level | warn | Levels with material reference exposure now absent |
| `VR-DST-4` null-rate-shift | warn | Null rate moved by more than X percentage points (a broken feed's clearest signal) |
| `VR-DST-5` volume-shift | warn | Row count against the reference version's row count |
| `VR-DST-6` mean-shift | warn | Numeric column mean moved more than N reference standard errors |
| `VR-DST-7` target-rate-shift | warn | Observed frequency / severity / burning cost moved more than X % vs reference |
| `VR-DST-8` mix-shift-exposure | warn | Exposure distribution across a declared key factor moved (PSI on the exposure weights, not the row counts) |

Thresholds are Rule Set configuration, not code. Every threshold shown is a default.

> **Amended 2026-08-15, after an independent audit — a rule carries one severity.**
>
> `VR-DST-1` read "warn at PSI > 0.10, **fail at > 0.25**", and `VR-DST-5` read "total
> exposure or row count, period-adjusted". Neither two-band form is reachable: a
> `CheckOutcome` reports pass or fail against a single threshold, and `_run_one` then maps
> that through the **rule's** static severity. A `warn` rule measuring PSI 0.90 reports
> `warn`; there is no channel by which a check escalates itself.
>
> The spec is the wrong side here, and deliberately so: severity belongs to the Rule Set
> entry, where `01` §4.3 lets a workspace *raise* it under review, and a check that could
> escalate itself would route around that. **Two bands are two rules** — one `warn` at
> 0.10 and one `fail` at 0.25, both in the set — which is also how an actuary sees which
> threshold fired.
>
> `VR-DST-5` is corrected to what it does: row count. Exposure-weighted and period-adjusted
> volume shift is **not implemented**, and is a spec change away from being a new rule
> rather than a silent gap in this one.

### 4.5 Custom validation rule format

Custom rules use the same tagged-union shape (§4.3) with `check` drawn from a fixed
vocabulary — never arbitrary code (governance parity with custom objectives, ADR-0003).
The vocabulary is enforced when the rule **runs**, not when it is authored: an unknown
`check` produces an `error` outcome that FR-DATA-19 refuses to count as a pass, and the
mandatory dry-run (step 2 below) is what stops it reaching approval.

**The column a check applies to is `target.column`**, not a param. Params configure the
check; the target says where it points. Only `uniqueness` takes a list, because a composite
key is one target with several columns.

| `check` | Target | Params | Meaning |
|---|---|---|---|
| `range` | `column` | `min_inclusive`, `min_exclusive`, `max_inclusive`, `max_exclusive` | Numeric bounds |
| `set_membership` | `column` | `allowed[]`, `case_sensitive` | Value domain (alias of the built-in `allowed_values`) |
| `regex` | `column` | `pattern` | String format. **Unanchored** — a pattern matches anywhere in the value unless it carries its own `^` and `$` |
| `uniqueness` | — | `columns[]` | Key uniqueness (alias of `unique_key`) |
| `not_null` | `column` | `key_columns[]` for the offending sample | Completeness |
| `relationship` | `column` | `left`, `right`, `operator` | Cross-column comparison (`exposure_end > exposure_start`) |
| `expression` | `column` | `expr` (restricted grammar), `expect` | Row-level boolean predicate |
| `aggregate` | `column` | `agg` (`sum`/`mean`/`count`/`quantile`/`min`/`max`), `group_by[]`, `quantile`, and a bound: `min`, `max` or `equals` | Group-level assertion |
| `reference_lookup` | `column` | `reference_table`, `as_at_column` or `as_at` | Referential resolution against the **pinned** reference version |
| `distribution_compare` | `column` | `metric` (`psi`/`mean_shift`), plus the delegate's params | Stability vs the reference version |
| `sql` | — | `query` (single `SELECT`, read-only, run in DuckDB against the version's parquet, must return a row count or a boolean), `timeout_s` | Escape hatch for genuinely bespoke checks |

> **Amended 2026-08-15, after an independent audit — this table did not describe the
> implementation, and a rule authored exactly as it read would fail.**
>
> `not_null` and `reference_lookup` were documented as taking `columns[]` and
> `key_columns[]`; both read `target.column`, so a rule written from this page raised
> `KeyError` and became an `error` outcome — which FR-DATA-19 correctly refuses to treat as
> a pass, so nothing was silently accepted, but the rule could never run either.
>
> Three params were declared and never read: `distribution_compare`'s `weight_column` and
> `thresholds` (the delegated built-in owns both), and `aggregate`'s `expect` (it takes
> `min`/`max`/`equals`). `aggregate` also implements `min` and `max` aggregations this
> table did not list.
>
> **`metric: ks` is withdrawn.** KS needs the reference column's *values*; FR-DATA-24 says
> a distributional rule reads the stored **Profile**, which keeps summaries and not values.
> The check skips it with that reason, which is right — the spec was asking for something
> the design excludes. Reinstating it would mean retaining reference values, and that is a
> different requirement.
>
> `scope.filter`, `scope.skip_on_derived` and `tolerance.max_violating_exposure_fraction`
> (§4.3) have **no reader** in the engine; `create_rule` stores `{}` for both. They are
> retained in the artifact as declared-but-inert and named here so nobody writes a rule
> that depends on them. `affected_exposure_fraction` *is* computed per result.

**Governance of custom rules (FR-DATA-21):**

1. Authored by an Analyst or Actuary → `draft`.
2. **Dry-run required** — the rule must execute successfully against at least one existing
   Dataset Version, and the dry-run result is attached to the approval request.
3. Submitted → `review` → approved by an Approver (never the author).
4. `approved` rules are immutable; edits create a new rule version needing re-approval.
5. The `sql` check carries extra controls (**OQ-DATA-3, decided 2026-08-14**):

   - **Authored by an Admin only** — not by an Analyst or Actuary as in step 1. The
     control that matters is how few people can write one, not how many must approve it.
   - **A single Approver**, as for every other rule. Requiring two was the original
     proposal and was dropped: dual approval on a check nobody may author anyway adds
     ceremony without adding a decision, and ceremony is what turns review into signature.
   - **Gated by the `features.sql_validation_check_enabled` workspace setting, which
     defaults to off** (`07` FR-PLAT-46). A workspace that never needs the escape hatch
     never carries its risk.
   - Parsed and rejected if it contains anything but a single `SELECT`; executed against a
     read-only DuckDB connection with no filesystem or extension access; subject to a hard
     time budget (FR-DATA-19).

   The declarative checks cover the great majority of real rules. This exists for the
   remainder, and is deliberately expensive to reach for. **Revisit after Phase 1** with
   evidence of what it was actually used for — if the answer is "nothing the declarative
   checks could not express", it should go.

### 4.6 `ValidationReport`

```json
{
  "dataset_version_id": "uuid",
  "rule_set_id": "uuid",
  "rule_set_version": 4,
  "job_id": "uuid",
  "started_at": "2026-08-14T09:12:00Z",
  "finished_at": "2026-08-14T09:14:37Z",
  "overall": "pass | pass_with_warnings | fail | error",
  "counts": {"pass": 41, "warn": 3, "fail": 0, "error": 0, "skipped": 1},
  "results": [
    {
      "rule_id": "uuid", "rule_slug": "psi-driver-age", "rule_version": 2,
      "layer": "distributional", "severity": "warn", "outcome": "warn",
      "measured": {"psi": 0.148}, "threshold": {"warn_above": 0.10, "fail_above": 0.25},
      "affected_rows": null, "affected_exposure_fraction": null,
      "detail": "Driver age distribution shifted; largest contribution from band 17-21 (+2.1pp).",
      "offending_sample": [],
      "evidence_blob": "blob:sha256:… (bucketed distribution table)",
      "acknowledgement": {
        "user_id": "uuid", "at": "2026-08-14T10:02:11Z",
        "justification": "Expected: new young-driver telematics product launched 2026-04."
      }
    }
  ],
  "reference_dataset_version_id": "uuid"
}
```

**Invariants** — `overall` is a function of the rule results alone:
`fail` if any result is `fail`; `error` if any is `error` and none is `fail`;
`pass_with_warnings` if any is `warn` and none is `fail`/`error`; `pass` otherwise.
The transition to `validated` is permitted for `pass` and `pass_with_warnings` only, and
`pass_with_warnings` **additionally requires every `warn` to carry an acknowledgement** —
checked at promotion (FR-DATA-17), not baked into `overall`.

> **Amended 2026-08-14 (W4).** `overall` previously read *"`pass_with_warnings` iff no
> `fail`/`error` and every `warn` has an `acknowledgement`"*, which had two problems.
>
> It left a state unnamed: a report with three warnings and no acknowledgements yet — the
> state *every* report with warnings is in the moment it is written — was none of the four
> values. Implementing it surfaced this immediately, because the field is `NOT NULL`.
>
> More seriously it made `overall` depend on acknowledgements, which arrive minutes or days
> after the run. A report is an immutable artifact and NFR-DATA-5 requires byte-identical
> bodies across runs; a verdict that changes when somebody clicks acknowledge is neither.
> Acknowledgement is a fact *about* a report, recorded beside it and scoped to
> `(dataset_version_id, rule_id, report_id)` by FR-DATA-18 — not a fact inside it.
>
> Nothing is lost: the promotion rule is unchanged, because `promote_to_validated` already
> took `unacknowledged_warnings` as a separate argument. `fail` outranks `error` when both
> are present — a definite failure is more actionable than "a rule could not tell", and
> both block promotion identically.

### 4.7 `Profile`

```json
{
  "id": "uuid",
  "dataset_version_id": "uuid",
  "job_id": "uuid",
  "computed_at": "2026-08-14T09:16:00Z",
  "row_count": 4824356,
  "weight_column": "exposure_years",
  "library_versions": {"polars": "1.9.0", "duckdb": "1.1.1"},
  "columns": [
    {
      "name": "driver_age", "semantic_type": "continuous", "dtype": "int32",
      "row_count": 4824356, "null_count": 412, "null_rate": 0.0000854, "distinct_count": 74,
      "minimum": 17, "maximum": 92, "mean": 43.8, "std": 15.2,
      "quantiles": {"p1": 19, "p5": 22, "p25": 32, "p50": 43, "p75": 55, "p95": 71, "p99": 80},
      "histogram": {"edges": [17, 20.75, 24.5, ..., 88.25, 92], "counts": [...], "exposure": [...]},
      "top_levels": []
    }
  ],
  "one_ways": [
    {
      "column": "driver_age", "banding": "profile_default_deciles",
      "rows": [
        {"level": "17-21", "exposure_years": "82141.20", "claim_count": 9142,
         "claim_amount_minor": 41_882_100_00, "frequency": 0.1113, "frequency_ci": [0.1090, 0.1136],
         "mean_severity": 458_128.42, "severity_ci": [449_200.0, 467_300.0],
         "mean_burning_cost": 50_987.93}
      ]
    }
  ]
}
```

> *(2026-08-18)* The example above has always shown a `histogram`, and so has the committed
> contract; `ColumnProfile` did not carry one until FR-DATA-48. **The contract was right and
> the requirement was incomplete** — FR-DATA-25 enumerates the statistics and never named
> this one. The example's edges were illustrative, not a specification, and were uneven:
> FR-DATA-48 fixes equal-width bins, because two engines must agree and quantile-derived
> edges collapse to duplicates on a low-cardinality column, with each engine deduplicating
> differently. The example above now shows the equal-width edges the requirement mandates.

> *(2026-08-18, Task 6 — `profile.schema.json` generated and compared against `Profile` for
> the first time.)* **The contract's `min`/`max` are renamed here to `minimum`/`maximum`,
> matching the model rather than the other way round.** `min` and `max` are Python
> builtins, `ColumnProfile` has named these fields `minimum`/`maximum` since Phase 1a, and
> every consumer — the validation layer's `_reference_column` reads, `ProfileView.vue` —
> already reads those names. Renaming the model to match a document nobody had compared it
> against would have broken a working consumer to tidy a schema; the example above is
> updated to match.
>
> The same comparison found the contract silent on five fields the model has always
> produced — `id`, `job_id`, `row_count` (on `Profile` and, separately, on each
> `ColumnProfile` — the count `VR-DST-6`'s standard-error check divides by), and
> `library_versions` — now added to the contract. `job_id` and `weight_column` ran the other
> way: the contract declared both and the model carried neither, so `Profile` gains
> `job_id: UUID | None` (matching the `job_id` every other per-Job artifact in this
> repository already carries, per `00` FR-OVR-3's `produced_by_job_id`) and
> `weight_column: str = "exposure_years"` (recording, on the artifact itself, which column
> `one_ways` was weighted by). Both are wired from the real profiling path, not left
> decorative: `profile_frame`/`profile_parquet` accept `job_id` and record their
> `exposure_column` argument as `weight_column`, and the worker's `_profile_version` handler
> now passes its own Job's id through — which it had never done, because `JobProgress`
> carried no public accessor for it before this slice added one.
>
> `top_levels`' item shape is a divergence this comparison found and did **not** fix: see
> FR-DATA-49.

> *(2026-08-19)* **The example above is corrected to match the model, not the other way
> round.** It had gone on showing FR-DATA-46's superseded one-way names — `severity_minor`
> and `burning_cost_minor`, both integer-looking and both `_minor`-suffixed — three commits
> after the rename to `mean_severity` / `mean_burning_cost` landed in `OneWayRow` and in the
> committed contract. `severity_ci` keeps its name: it is the interval *around* the mean
> severity, and renaming an unchanged field to match a neighbour's rename would break
> `ProfileView.vue` for symmetry alone. The values are unchanged in magnitude and now read
> as the floats they are: a mean severity is claim amount divided by claim count, a ratio
> rather than an amount, which is precisely why FR-OVR-7's `_minor` suffix had to go.
>
> The example also gained the fields the note above added to the contract — `id`, `job_id`,
> `row_count` on both `Profile` and each `ColumnProfile`, `weight_column` and
> `library_versions`. Three of those are `required` — `Profile.id`, `Profile.row_count` and
> `ColumnProfile.row_count` — so a reader copying the previous example produced an object
> the contract rejects. Enumerating them in prose was not enough: `01`
> §5.3's own audit exists because a Contents column was read and a view was not, and an
> example is read far more often than the paragraph under it.

> *(2026-08-19, found in this slice's closing review)* **FR-DATA-46's rename carried the
> field names across and left the types behind — the contract was wrong, and is corrected
> here.** `mean_severity` and `mean_burning_cost` went on `$ref`-ing
> `common/money.schema.json#/$defs/MoneyMinor`, which is `{"type": "integer"}`, in both
> `docs/contracts/schemas/profile.schema.json` and `docs/contracts/schemas/banding.schema.json`;
> `profile.schema.json` additionally typed `severity_ci`'s two interval bounds as integers
> where `banding.schema.json`'s copy of the identical shape typed them as numbers. The
> model has declared all three `float` since Phase 1a. A mean severity of 45812.42 — the
> ordinary case, not an edge one — fails all four declarations, so the published contract
> asserted precisely the rounding FR-DATA-46 exists to forbid.
>
> **All five predate this slice**: the divergence is `severity_minor: MoneyMinor` against
> `float | None` at the branch base, inherited rather than introduced, and the rename moved
> it under new names without ever looking beneath them. That is the more useful half of the
> finding, because it says what the *check* was missing rather than what one commit was.
>
> **Nothing compared types.** Every conformance test in `backend/tests/test_contracts.py`
> compared field *names* — `test_generated_and_authored_agree_on_field_names`,
> `test_an_artifact_shape_carries_exactly_what_its_contract_declares`, and even
> `test_the_column_profile_shape_matches_its_contract`, which was written specifically to
> look one level deeper and still compared only the set of property names it found there.
> Names agreeing is a much weaker claim than it reads as, and it is the claim four earlier
> `Banding`/`Grouping` divergences also satisfied. `test_generated_and_authored_agree_on_scalar_types`
> now compares the JSON types the two documents admit, across all six shapes that have both
> a generated and a hand-authored contract, following `$ref`s between files and unwrapping
> `anyOf` so an optional field is read the same way on both sides.
>
> Two limits of that comparison, both deliberate. It ignores `null`, because the generated
> contracts mark every `X | None` nullable and the authored ones mark almost none — a
> uniform difference of idiom worth reconciling on its own, not inside a test aimed at
> integer-for-a-float. And it compares only paths present on both sides, so it says nothing
> about `top_levels`, where the two documents disagree on *structure* rather than type;
> that one stays FR-DATA-49's, recorded with an owner rather than suppressed by an
> exemption list here.
>
> The non-obvious mechanism, which cost the first version of the walker its teeth:
> **Pydantic emits a fixed-length tuple as `prefixItems`, not `items`.** A walker reading
> only `items` is silently blind to every tuple field in every contract — `severity_ci`
> among them — and reports success. It passed with the bounds deliberately typed as
> integers, which is how the blindness was found.
> `test_the_type_comparison_reaches_the_one_way_row` names the three paths rather than
> counting them: a threshold expressed as a fraction of the walker's own output moves out
> of the way of the defect it is meant to catch, since a walker that stops descending
> shrinks the numerator and the denominator together.

### 4.8 `ReferenceTable` / `ReferenceTableVersion`

A **table** declares what it is keyed by; a **version** holds effective-dated rows.

```json
{
  "table": {
    "slug": "ons-postcode-directory",
    "key_columns": ["postcode_outcode"],
    "payload_columns": ["rating_area", "urbanity", "region"],
    "latest_published_version": 7
  },
  "version": {
    "slug": "ons-postcode-directory",
    "version": 7,
    "status": "published",
    "row_count": 2987,
    "covers_from": "2026-04-01",
    "covers_to": null,
    "source_note": "ONS NSPL Feb 2026 release, aggregated to outcode."
  },
  "row": {
    "key": "SW1A",
    "payload": {"rating_area": 12},
    "effective_from": "2026-04-01",
    "effective_to": null
  }
}
```

**Invariants** — for a given key, validity intervals `[effective_from, effective_to)` across
versions must not overlap (FR-DATA-29), enforced by a PostgreSQL exclusion constraint. The
interval is **half-open**: a row ending on a date does not cover that date, which is what
lets consecutive versions abut without overlapping.

**Lifecycle: `draft → published`.** A version is loaded whole into `draft` and made
pinnable by publishing it. Validation and rating resolve a **published** version by id and
never "the latest" (FR-DATA-30); a lookup against a table with no published version is
refused with `REFERENCE_VERSION_NOT_PINNED` rather than falling back.

> **Amended 2026-08-15, after an independent audit.** The example above described one flat
> artifact carrying `effective_from`/`effective_to`/`blob`/`status: "approved"`, and the
> word "publish" appeared nowhere in this document. What was built is relational — table,
> version, and per-row intervals under the exclusion constraint — with **no blob**, and a
> `draft → published` lifecycle realising FR-DATA-30's "independently approvable".
>
> The code is the right side: per-row intervals are what the exclusion constraint can
> enforce, and a blob could not be. The gap was that the lifecycle existed in the
> implementation, in the database and in two API routes while being declared in no spec —
> which meant the endpoint audit, comparing §5.1 against the contract, reported a complete
> surface. **An endpoint missing from both is invisible to it.**

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/sources` | Register a Source (FR-DATA-1) |
| `GET` | `/api/v1/sources` | List sources (credentials redacted) |
| `POST` | `/api/v1/sources/{id}/preview` | Read first N rows + inferred schema without creating a version |
| `POST` | `/api/v1/datasets` | Create a Dataset (metadata + data dictionary) |
| `GET` | `/api/v1/datasets` | List / filter datasets, each with `latest_version`, `latest_version_status` and `last_validated_at` (FR-DATA-50) |
| `GET` | `/api/v1/datasets/{slug}` | Dataset detail incl. `latest_version` |
| `PUT` | `/api/v1/datasets/{slug}/dictionary` | Update the Data Dictionary (audited) |
| `GET` | `/api/v1/datasets/{slug}/versions` | Version timeline, newest first, cursor-paginated |
| `POST` | `/api/v1/datasets/{slug}/versions` | **202** Start an Ingestion Run → Job (FR-DATA-2) |
| `GET` | `/api/v1/datasets/{slug}/versions/{version}` | Dataset Version detail |
| `PATCH` | `/api/v1/datasets/{slug}/versions/{version}/schema` | Correct the inferred schema while `draft` (FR-DATA-4) |
| `GET` | `/api/v1/dataset-versions/{id}` | Dataset Version detail **by id** — the resource the nine routes below hang off |
| `POST` | `/api/v1/dataset-versions/{id}/validate` | **202** Run validation → Job (FR-DATA-15) |
| `GET` | `/api/v1/dataset-versions/{id}/validation-reports` | Report history |
| `GET` | `/api/v1/validation-reports/{id}` | Full report |
| `POST` | `/api/v1/validation-reports/{id}/results/{rule_id}/acknowledge` | Acknowledge a warn, with justification (FR-DATA-17) |
| `POST` | `/api/v1/dataset-versions/{id}/transition` | `{"to": "validated" \| "archived"}` — enforces §4.6 invariants |
| `GET` | `/api/v1/dataset-versions/{id}/profile` | Profile artifact (FR-DATA-25) |
| `GET` | `/api/v1/dataset-versions/{id}/one-ways?column=` | One-way summary for a column (FR-DATA-26) |
| `GET` | `/api/v1/dataset-versions/{id}/compare?against={id}` | Profile comparison / PSI (FR-DATA-28) |
| `POST` | `/api/v1/dataset-versions/{id}/derive` | **202** A declared derivation (FR-DATA-33). Only `split` is materialised; the Job fails with `DERIVATION_NOT_MATERIALISED` for the rest (FR-DATA-45) |
| `POST` | `/api/v1/dataset-versions/{id}/splits` | **201** Record a named split over parts already derived (FR-DATA-36) |
| `GET` | `/api/v1/dataset-versions/{id}/splits` | Splits recorded on this version, for a Model Spec to cite (FR-DATA-36) |
| `GET` | `/api/v1/dataset-versions/{id}/lineage?direction=up\|down` | Lineage graph (FR-DATA-35) |
| `GET` | `/api/v1/dataset-versions/{id}/rejected` | Quarantined rows (paged) (FR-DATA-7) |
| `POST` | `/api/v1/validation-rules` | Create a custom rule → `draft` (FR-DATA-21) |
| `POST` | `/api/v1/validation-rules/{id}/dry-run` | **202** Execute against a chosen version |
| `POST` | `/api/v1/validation-rules/{id}/submit` | Submit for approval |
| `POST` | `/api/v1/validation-rules/{id}/approve` | Approve a rule in review — never its author (§4.5 step 3) |
| `GET`/`PUT` | `/api/v1/datasets/{slug}/rule-set` | Read / replace the Rule Set (creates a new rule-set version) |
| `POST` | `/api/v1/reference-tables` | Declare a Reference Table (`admin:manage_settings`) |
| `GET` | `/api/v1/reference-tables` | List declared Reference Tables |
| `POST` | `/api/v1/reference-tables/{slug}/versions` | Load a new Reference Table Version (FR-DATA-29) |
| `GET` | `/api/v1/reference-tables/{slug}/versions` | The version timeline, with each version's covered period |
| `POST` | `/api/v1/reference-tables/{slug}/versions/{version}/publish` | `draft → published`; a version is pinnable only once published (FR-DATA-30) |
| `GET` | `/api/v1/reference-tables/{slug}/versions/{version}/rows?as_at=` | Rows of a **pinned** version, optionally as at a date (FR-DATA-30) |
| `GET` | `/api/v1/reference-tables/{slug}/lookup?key=&as_at=` | Point lookup for debugging (FR-DATA-31) |

> **Three reference read routes added 2026-08-15 (W6a).** §5.3 asks the `/reference` view
> for a table list, a version timeline and an effective-date viewer, and §5.1 declared none
> of them: the surface was write-plus-lookup. The endpoint audit compares this table against
> the published contract, so an endpoint missing from **both** read as complete coverage —
> the same blind spot §13 records for requirement markers, one level up.
>
> The rows route always reads the version named in the path and never falls back to the
> latest, because FR-DATA-30 is the rule this screen is most likely to teach by example.

> **`GET /dataset-versions/{id}` added 2026-08-15 (W5).** Nine routes in this table are
> children of `/dataset-versions/{id}` — validate, transition, derive, profile, one-ways,
> compare, lineage, rejected, validation-reports — and the parent was not among them. The
> only version detail route was `/datasets/{slug}/versions/{version}`, so **anything holding
> a version id and not its dataset slug could not resolve it at all.**
>
> Found by building `02` §5.3's factor workbench, whose route is `/factors/:datasetVersionId`
> and which needs the `dataset_id` a Banding is keyed to. Not a new capability — the same
> resource, addressed by its own id — so it carries no new requirement; it is the row this
> table should always have had.

> **`GET /datasets/{slug}/versions` added 2026-08-15 (W6a).** §5.3 requires the Dataset
> detail view to render a **version timeline**, and §5.1 offered only `latest_version` and
> per-version detail — so a client had to issue one request per version to draw it, and
> could not show a status without fetching them all. Found by building the view against the
> table.
>
> Newest first and cursor-paginated like every other collection (`00` §5.2): a dataset
> refreshed monthly for ten years has a hundred and twenty versions, and a timeline is read
> from the top.

> **`POST /validation-rules/{id}/approve` added 2026-08-15 (W6a).** §4.5 step 3 describes
> the step — "submitted → `review` → approved by an Approver (never the author)" — and the
> service enforced it, but §5.1 exposed no route. A rule could be authored, dry-run and
> submitted, and then sat in `review` with no way out; since a Rule Set refuses any rule
> that is not `approved` (FR-DATA-21), nothing authored through the API could ever be used.
> Found by walking the chain the rule-set editor needs.
>
> Approval **policies** — quorum, escalation, evidence bundles — remain `06`'s (FR-GOV-9..19,
> W17). This is the module's own step in the module's own terms, which is what §4.5 states.

**Error codes owned by this module:** `DATASET_NOT_VALIDATED`, `DATASET_VERSION_IMMUTABLE`,
`SCHEMA_INFERENCE_CONFLICT`, `COLUMN_NAME_COLLISION`, `DIRECT_IDENTIFIER_PRESENT`,
`VALIDATION_HAS_FAILURES`, `WARN_NOT_ACKNOWLEDGED`, `ACKNOWLEDGE_FORBIDDEN_ROLE`,
`RULE_NOT_APPROVED`, `RULE_SEVERITY_DOWNGRADE_FORBIDDEN`, `RULE_TIMEOUT`,
`ACKNOWLEDGEMENT_ALREADY_RECORDED`,
`REFERENCE_INTERVAL_OVERLAP`, `REFERENCE_VERSION_NOT_PINNED`, `SOURCE_UNREACHABLE`,
`REJECT_RATE_EXCEEDED`, `DERIVATION_NOT_MATERIALISED`.

### 5.2 `pricing-core` interfaces

```python
# packages/pricing-core/src/pricing_core/data/ingest.py     (added W4, 2026-08-14)
def normalise_column_name(name: str) -> str                  # FR-DATA-5
def normalise_columns(names: list[str]) -> ColumnMapping     # raises on collision
def infer_schema(frame: pl.DataFrame) -> InferredSchema      # FR-DATA-4
def partition_rejects(
    frame: pl.DataFrame, *, required_non_null: list[str] | None = None
) -> RejectPartition                                          # FR-DATA-7

# packages/pricing-core/src/pricing_core/data/prepare.py
def apply_recipe(
    tables: dict[str, pl.LazyFrame],
    recipe: PreparationRecipe,
    *,
    progress: ProgressCallback | None = None,
) -> PreparationResult:            # .tables, .rejected, .stats

# packages/pricing-core/src/pricing_core/data/validate.py
def run_validation(
    tables: dict[str, pl.LazyFrame],
    rule_set: ValidationRuleSet,
    *,
    reference_profile: Profile | None = None,
    reference_tables: Mapping[str, ReferenceTableVersion],
    time_budget_s: float = 300.0,
    progress: ProgressCallback | None = None,
) -> ValidationReport

# packages/pricing-core/src/pricing_core/data/profile.py     (corrected 2026-08-15)
def profile_frame(
    tables: Mapping[str, pl.DataFrame],
    *,
    dataset_version_id: UUID,
    exposure_column: str = "exposure_years",
    one_way_columns: Sequence[str] | Literal["auto"] = "auto",
) -> Profile
def profile_parquet(...) -> Profile          # same shape, aggregated in DuckDB (FR-DATA-27)
def compare_profiles(current: Profile, reference: Profile) -> ProfileComparison   # PSI etc.
def candidate_rating_columns(columns, *, exposure_column="exposure_years") -> tuple[str, ...]

# packages/pricing-core/src/pricing_core/data/prepare.py     (corrected 2026-08-15)
def explode_period(df: pl.DataFrame, spec: ExplodePeriodSpec) -> pl.DataFrame     # FR-DATA-11
def attach_claims(exposure: pl.DataFrame, claims: pl.DataFrame, spec: AttachClaimsSpec) -> AttachResult

# packages/pricing-core/src/pricing_core/data/expressions.py — the restricted AST that
# compiles a recipe expression to Polars without `eval` (FR-DATA-9)
# packages/pricing-core/src/pricing_core/data/reference.py   — effective-dated resolution
```

> **Amended 2026-08-15, after an independent audit.** §5.2 declared `profile_version(...)`
> with a `schema` argument and a `weight_column`, and put `explode_period`/`attach_claims`
> in an `exposure.py` that does not exist. It was amended for `ingest.py` in W4 and not for
> the rest, so it described the shape of the code as it was designed rather than as it was
> written. Two modules it never mentioned are listed above.

All of these are pure: no I/O, no database, `parquet_uris` read through an injected
filesystem object supplied by the caller (ADR-0001).

`ingest.py` was added in W4. The §5.2 list originally began at preparation, but three
ingestion decisions are deterministic functions of a frame — how a column name normalises,
what the candidate schema is, which rows are unusable — and FR-DATA-5 requires the first of
them to be *deterministic and collision-detecting*, which is a property of a function
rather than of a service. Reading the file remains the caller's job; only the decisions
moved.

### 5.3 Frontend views

| View | Route | Contents |
|---|---|---|
| Dataset list | `/data` | Datasets with latest version, status badge, last validated, owner |
| Dataset detail | `/data/:slug` | Version timeline, data dictionary editor, rule set link, lineage graph |
| Version detail | `/data/:slug/v/:version` | Table inventory, row counts, totals, schema viewer, rejected-rows drawer |
| **Validation report** | `/data/:slug/v/:version/validation` | Four layer sections, per-rule outcome rows, measured-vs-threshold, offending sample table, acknowledge dialog with mandatory justification, and a prominent blocked/unblocked banner |
| Profile | `/data/:slug/v/:version/profile` | Per-column cards, histograms, one-way charts with CI bands (ECharts), PSI comparison selector |
| Rule set editor | `/data/:slug/rules` | Rule list by layer, enable/disable, threshold editing, custom-rule builder with dry-run |
| Reference tables | `/reference` | Table list, version timeline, effective-date viewer, lookup debugger |

**Interaction requirement:** the validation view is the module's centrepiece. It must make
"why can I not fit a model on this?" answerable in one screen without scrolling past the
fold: overall banner → failing rules → warnings needing acknowledgement → everything else.

> *(2026-08-19)* **The Profile row's four Contents items are now three built and one not.**
> Histograms landed with FR-DATA-48; per-column cards and the one-way charts with their CI
> bands were built in W6a. The **PSI comparison selector has not been built**:
> `compareProfiles()` is implemented, typed and exported from `frontend/src/api/profiles.ts`
> with **zero callers**, and the dtype label that borrowed `psiBand`'s colour has been
> uncoloured rather than left reading as support the view lacks — `psiBand(null)` returned
> `"stable"` before any threshold, so the badge was never showing a PSI band, only the
> colour of one. FR-DATA-28's endpoint exists and is served; the view that reads it is
> unowned.
>
> The row keeps the claim rather than losing it (`CLAUDE.md` §14: resolve, never soften).
> **Owner: the next slice to open `ProfileView.vue`, or W6b** — the selector needs a
> reference-version picker, which is the first piece of Profile state that must outlive a
> route, and `docs/roadmap.md`'s W6a record already names it as the trigger for the
> frontend's first Pinia store.
>
> **Resolved 2026-08-19 on the Dataset list row above: status badge, last validated, owner.**
> The question of which entity carries them was recorded as OQ-DATA-9 rather than picked, and the
> maintainer decided it — **two of the three are projections, one is a field**. `Dataset` gains an
> explicit `owner_id` (FR-DATA-51) because no version carries ownership and `06`'s RBAC needs a
> subject; the badge and the date are read off the Dataset's versions by the list endpoint
> (FR-DATA-50), so the container never holds a second status that could disagree with
> `DatasetVersion.status`. **Still undelivered, and still W6b's** — the decision moved the row from
> *unanswerable* to *unbuilt*, which is a different and smaller thing.

---

## 6. Workflows

| Step | Actor | Action |
|---|---|---|
| 1 | Analyst | Registers/selects a Source, previews inferred schema (`POST /sources/{id}/preview`) |
| 2 | Analyst | Confirms or corrects the schema and Preparation Recipe |
| 3 | Frontend → Backend | `POST /datasets/{slug}/versions` → `202` + Job |
| 4 | Worker → pricing-core | `apply_recipe` → parquet written to blob store → Dataset Version `draft` |
| 5 | Worker → pricing-core | `profile_version` runs automatically (FR-DATA-25) |
| 6 | Analyst | Reviews profile; triggers `POST /dataset-versions/{id}/validate` |
| 7 | Worker → pricing-core | `run_validation` across four layers → Validation Report persisted |
| 8a | — | Any `fail` → version stays `draft`; the actuary fixes data, recipe, or rule |
| 8b | Pricing Actuary | Each `warn` acknowledged with justification (audited) |
| 9 | Pricing Actuary | `POST /dataset-versions/{id}/transition {"to":"validated"}` |
| 10 | Backend | Emits Audit Event; the version becomes eligible for model fitting (`02-modelling.md`) |

Full journey with screens and decision points: [`wf-01-dataset-to-model.md`](../workflows/wf-01-dataset-to-model.md).
Rule authoring governance mirrors [`wf-05-custom-objective-lifecycle.md`](../workflows/wf-05-custom-objective-lifecycle.md).

---

## 7. Cross-module dependencies

### 7.1 This module consumes

| From | What | Why |
|---|---|---|
| `07-platform` | Jobs, blob storage, secrets, scheduling | Ingestion/validation/profiling are Jobs; credentials are secret references (FR-DATA-1) |
| `06-governance` | RBAC, approval workflow, audit sink | Acknowledgement role check (FR-DATA-17), custom rule approval (FR-DATA-21) |

### 7.2 This module provides

| To | What | Contract |
|---|---|---|
| `02-modelling` | `validated` Dataset Versions, profiles, one-way summaries, named splits | Fitting is gated on status (§1.3); one-ways feed the factor workbench (FR-DATA-26) |
| `03-rating-engine` | Reference Table Versions | Pinned by Rating Versions for lookup steps (FR-DATA-30) |
| `04-optimisation` | Portfolio Dataset Versions | The book that dislocation and optimisation are evaluated over |
| `05-monitoring` | Reference distributions and profiles | The baseline that live drift is measured against (`VR-DST-*` logic is reused) |
| `06-governance` | Dataset lineage and validation evidence | Included in generated model documentation |

### 7.3 Contract notes

- `02-modelling` must never re-derive a one-way summary itself; it reads the Profile
  (FR-DATA-27) so that the number in the factor workbench and the number in the validation
  report are provably the same number.
- `05-monitoring` reuses `compare_profiles` rather than reimplementing PSI, so that a drift
  alert and a validation warning use identical maths.

---

## 8. Tech dependencies

| Component | Used for | Notes for `skills-map.md` |
|---|---|---|
| **Polars** | Preparation recipe execution, row-level rules, exposure explosion | Lazy frames; strict dtypes are load-bearing (ADR-0005) |
| **DuckDB** | Profiling, one-ways, PSI, `sql` custom checks, comparison queries | Runs directly over parquet; read-only connection for user SQL |
| ~~**pandera (Polars backend)**~~ | ~~Layer-1 structural schemas~~ — **not adopted** (2026-08-15) | The structural layer is implemented directly over Polars in `pricing_core.data.validate`, and the version already stores its schema as a `DatasetTableSchema`. Adopting pandera would restate a shape `model-schema` owns, which is the hazard `CLAUDE.md` §2 forbids; its serialisation is the only thing it would have added. NFR-DATA-2's ≤ 2 min structural budget is met without it — 0.1 s at 2 M rows. The research finding (F9) stands as a correct assessment of pandera; the decision went the other way. |
| **Apache Parquet / Arrow** | Dataset Version storage, `decimal128` for money and exposure | Row groups sized for predicate pushdown; explicit schema persisted |
| **Object storage (S3/MinIO)** | Content-addressed parquet blobs (ID-4) | Multipart upload for large versions |
| **PostgreSQL 16** | Version metadata, reports, rule sets, lineage edges | JSONB for report bodies + GIN indexes; exclusion constraint for reference effective dating (FR-DATA-29) |
| **Celery + Redis** | Ingestion, validation, profiling, derivation Jobs | Progress callbacks; per-rule time budgets (FR-DATA-19) |
| **Dagster** | Scheduled recurring ingestion from `pipeline` sources | Partitioned assets keyed by dataset version |
| **SciPy** | Poisson/Gamma confidence intervals on one-ways (FR-DATA-26) | Exact CIs at low counts, not normal approximations |
| **ECharts + TanStack Table (frontend)** | One-way charts with CI bands; report and rejected-row grids | Virtualised grids for large offending samples |

New skills this spec adds to `skills-map.md`:
DuckDB read-only sandboxing; PostgreSQL exclusion constraints for effective dating;
PSI/KS implementation details; parquet decimal logical types.

---

## 9. Non-functional requirements

| ID | Requirement |
|---|---|
| **NFR-DATA-1** | Ingest + prepare 10 M rows × 80 columns from parquet in ≤ 15 min on a 16-core worker; from CSV in ≤ 30 min. |
| **NFR-DATA-2** | Full validation of a 10 M-row version with ~50 rules completes in ≤ 10 min; structural layer alone in ≤ 2 min so it can fail fast. |
| **NFR-DATA-3** | Profiling a 10 M-row version completes in ≤ 5 min, and its memory **does not scale with row count**: every statistic is aggregated in DuckDB and only aggregates are materialised (see the note below). |
| **NFR-DATA-4** | A one-way summary read from a stored Profile returns in < 300 ms (NFR-OVR-4); it is never computed on request. |
| **NFR-DATA-5** | Validation is deterministic: the same version + rule set version produces byte-identical report bodies apart from timestamps and job ids (FR-OVR-8). |
| **NFR-DATA-6** | Storage overhead of a Dataset Version is ≤ 1.2× the parquet payload; identical tables across versions are deduplicated by content hash (ID-4). |
| **NFR-DATA-7** | The validation report API returns the summary in < 500 ms for reports with up to 500 rules; offending samples are lazily paged. |
| **NFR-DATA-8** | Audit: dataset transitions, acknowledgements, dictionary edits, rule-set changes, and purges each emit an Audit Event with before/after state (FR-OVR-4). |
| **NFR-DATA-9** | A user-supplied `sql` check cannot read outside the target version's parquet files, cannot write, cannot load DuckDB extensions, and is killed at its time budget (FR-DATA-19, §4.5). |
| **NFR-DATA-10** | Ingestion of a source that fails mid-run leaves no partially-visible version: version rows become visible only on successful commit. |

> **NFR-DATA-3 amended 2026-08-14.** It previously bounded profiling memory at "2× the
> largest column's compressed size". That number is not achievable and was never the
> property worth requiring. Measured on the W4 benchmark (`scripts/bench-data.py`), 80
> columns × 2 M rows: the largest compressed column is 15.4 MB, so the old bound was
> 30.7 MB — while a Python process with `polars`, `duckdb`, `scipy` and `pydantic`
> imported occupies 140 MB before it has read a byte. The bound counted the interpreter
> against the dataset.
>
> The property that actually protects the platform is that profiling does not hold the
> data, and that *is* measurable: over a 10× increase in payload (109 MB → 1,092 MB),
> peak RSS above the import baseline moved 113 MB → 236 MB. Sub-linear, so a 10 M-row
> version does not need 10 M rows' worth of memory.
>
> The requirement was met in intent and missed in fact by the first implementation, which
> ran `SELECT *` and handed the frame to the in-memory profiler — 2,278 MB peak on that
> same 1,092 MB payload, and roughly 11 GB at the scale the requirement is written
> against. The parenthetical "DuckDB streaming, not full materialisation" was already in
> the spec; the code did not do it, and no test asked.

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-DATA-1** | Should large-loss handling (capping, spreading above a threshold) be a *preparation* step baked into the dataset, or a *modelling* decision applied at fit time? Baking it in makes exposure/claims totals consistent everywhere; applying it at fit time lets one dataset serve multiple capping assumptions. |
| **OQ-DATA-2** | Do we support incremental/append ingestion (adding a new month to an existing version) or is every version a full snapshot? Full snapshots are simpler and match immutability; append is far cheaper for a 10-year book refreshed monthly. |
| ~~**OQ-DATA-3**~~ ✔ | ~~Does the `sql` custom check earn its keep, and if kept, is dual approval the right control or should it be admin-only?~~ **Decided 2026-08-14: kept, Admin-authored, single Approver, behind a workspace flag defaulting to off (§4.5). Revisit after Phase 1.** |
| ~~**OQ-DATA-4**~~ ✔ | ~~Where do IBNR / claims-development adjustments live — a preparation step producing developed claim amounts, a modelling offset, or out of scope entirely (user supplies developed data)? `VR-ACT-14` currently only *warns*. |~~ **Decided 2026-08-14: out of scope — the user supplies developed data; `VR-ACT-14` warns about immature periods (§1.2).**
| ~~**OQ-DATA-5**~~ ✔ | ~~Should the platform hold the ONS/ABI reference sets as shipped data, given their licensing terms, or only ship loaders and require the user to supply the files? |~~ **Decided 2026-08-14: loaders for every source; rows shipped only under an unambiguous licence; ABI group tables never (FR-DATA-32).**
| ~~**OQ-DATA-7**~~ ✔ | ~~Nothing in the platform ever sets a Dataset Version to `failed`. `DatasetStatus.FAILED` exists in the enum and in `VALID_DATASET_TRANSITIONS`, and no code path transitions to it — so a version whose first validation fails rests in **`validating`**, which every screen reads as "still running". FR-DATA-2 uses `failed` for a broken ingestion run and FR-DATA-23 sends a *re-validated* version back to `draft`; the first-failure case was specified nowhere. Found by exercising Phase 1a's exit demo, 2026-08-15.~~ **Decided and delivered 2026-08-15: `failed`** (FR-DATA-43). |
| ~~**OQ-DATA-8**~~ ✔ | ~~`sample`, `filter`, `join` and `aggregate` derived versions inherit their parent's rows rather than being produced from them — a 1 % sample holds 100 % of them.~~ **DECIDED 2026-08-17: materialise all four, each in the slice that first needs it, and refuse them until then rather than leaving the silent version.** Specified as FR-DATA-45 and the refusal delivered the same day; `split` remains the one materialised operation (FR-DATA-44). Owner: W7 for `sample`; `filter`, `join` and `aggregate` unowned. Raised 2026-08-16 (W5). |
| ~~**OQ-DATA-6**~~ ✔ | ~~Is `warn` acknowledgement per-rule-per-report the right granularity, or should an actuary be able to pre-approve a recurring known warning for a defined period (with expiry) to avoid acknowledgement fatigue? |~~ **Decided 2026-08-14: per report as FR-DATA-18 specifies, plus a pre-fill affordance that still requires an explicit, separately audited act.**
| ~~**OQ-DATA-9**~~ ✔ | ~~§5.3 asks the dataset list to display a status badge, a last-validated date and an owner. `Dataset` carries none of the three: status and `validation_report_id` live on `DatasetVersion`, and ownership is only implied by `workspace_id`. Does `Dataset` gain the three fields, or does §5.3 mean the latest version's status and validated-at, plus a workspace-level owner?~~ **DECIDED 2026-08-19: two of the three are projections of the latest versions, one is a new field.** Specified as FR-DATA-50 (`latest_version_status` and `last_validated_at`, derived by the list endpoint, never stored) and FR-DATA-51 (`Dataset.owner_id`, explicit, not derived from `workspace_id`). Neither is delivered; both are W6b's, with the trigger named in the requirements. Raised 2026-08-18 (W5). |
