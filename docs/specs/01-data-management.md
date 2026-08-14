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
| **FR-DATA-14** | The Preparation Recipe is persisted with the Dataset Version and is replayable: `replay(recipe, source_bytes) == stored version` byte-for-byte on parquet content hash, given pinned library versions. |

### 3.3 Validation — the gate

| ID | Requirement |
|---|---|
| **FR-DATA-15** | Validation runs as a Job against a `draft` Dataset Version, executing every rule in the Dataset's Validation Rule Set and producing exactly one **Validation Report** per run. Reports are immutable and retained; re-validation creates a new report, it does not overwrite. |
| **FR-DATA-16** | Validation covers four layers, all of which must be present in every Rule Set (a Rule Set with an empty layer is a configuration warning surfaced in the UI): **structural**, **referential**, **actuarial sanity**, **distributional/stability**. §4.4 enumerates the built-in rules. |
| **FR-DATA-17** | Transition to `validated` requires: zero `fail` outcomes, zero `error` outcomes, and every `warn` outcome carrying an **Acknowledgement** by a Pricing Actuary with a non-empty justification (audited, FR-OVR-4). An Analyst cannot acknowledge. |
| **FR-DATA-18** | An Acknowledgement is scoped to `(dataset_version_id, rule_id, report_id)`. It does not carry forward to the next version or the next report — each version's warnings are acknowledged on their own evidence. |
| **FR-DATA-19** | Rules execute independently; one rule's `error` does not prevent others from running. A rule that exceeds its time budget is recorded as `error` with reason `timeout`, and blocks validation (an unrun rule is never treated as a pass). |
| **FR-DATA-20** | Every non-pass outcome persists: rule id and version, severity, affected row count, affected exposure, the measured value vs the threshold, and an Offending Sample of up to 100 primary keys. |
| **FR-DATA-21** | Users can define **custom Validation Rules** declaratively (§4.5). A custom rule is an Artifact with its own `draft → review → approved` lifecycle; only `approved` rules may run in a Rule Set used for a Dataset feeding an `approved` Model. |
| **FR-DATA-22** | A Rule Set is versioned. A Validation Report records the exact `rule_set_version` and each `rule_version` it executed, so an old report remains interpretable after rules change. |
| **FR-DATA-23** | Validation is re-runnable on a `validated` version (e.g. after a rule set update). If the new report contains `fail`s, the version transitions **back** to `draft` and every Model fitted on it is flagged `dataset_invalidated` — models are not deleted, but the flag is surfaced on the model, on any Rating Version referencing it, and to the Approver. |
| **FR-DATA-24** | Validation is incremental where sound: structural and actuarial rules stream over parquet row groups; distributional rules use pre-computed profile aggregates rather than re-scanning. |

### 3.4 Profiling

| ID | Requirement |
|---|---|
| **FR-DATA-25** | Profiling runs automatically after successful ingestion and produces, per column: null count and rate, distinct count, min/max, mean/std (numeric), percentiles (p1, p5, p25, p50, p75, p95, p99), top-20 levels by exposure and by count (categorical), and inferred semantic type (`identifier`, `categorical`, `ordinal`, `continuous`, `date`, `money`, `boolean`). |
| **FR-DATA-26** | Profiling additionally produces **one-way summaries** per candidate rating column: exposure, claim count, claim amount, observed frequency, severity, and burning cost by level or banded interval, with Poisson/Gamma confidence intervals. These are the inputs to the factor workbench in `02-modelling.md` and are computed once, here. |
| **FR-DATA-27** | Profiles are computed with DuckDB directly over the version's parquet files and persisted as an artifact. The UI never recomputes a profile client-side or ad-hoc on request. |
| **FR-DATA-28** | A **profile comparison** between any two Dataset Versions of the same Dataset is available on demand: per-column PSI, mean shift, null-rate shift, new/vanished levels. This is the same computation that the distributional validation layer consumes. |

### 3.5 Reference data

| ID | Requirement |
|---|---|
| **FR-DATA-29** | A **Reference Table** holds effective-dated lookup rows with a declared key, declared payload columns, and half-open `[effective_from, effective_to)` validity (FR-OVR-12). Overlapping intervals for the same key are rejected at load time. |
| **FR-DATA-30** | Reference Table Versions are immutable and independently approvable. Both validation (referential layer) and the rating engine pin an explicit Reference Table Version — neither ever resolves "latest" at runtime. |
| **FR-DATA-31** | A reference lookup is evaluated **as at a declared date** (typically the policy inception date), not as at "now". The date column used is declared on the rule or the rating step. |
| **FR-DATA-32** | The platform ships loaders for the common UK reference sets: ONS postcode directory, ABI vehicle group tables, occupation/industry code lists, and a bank-holiday calendar. Each is a Reference Table like any other — no special-casing in the engine. |

### 3.6 Derived datasets & lineage

| ID | Requirement |
|---|---|
| **FR-DATA-33** | Derived Dataset Versions are produced by declared operations — `sample` (with seed and method: random, stratified, exposure-weighted), `split` (train/test/validation with seed and method: random, temporal, grouped-by-key), `filter` (restricted expression), `union` — each recording its parameters and `parent_id`. |
| **FR-DATA-34** | A Derived Dataset Version inherits its parent's schema, Data Dictionary, and Rule Set, and must be validated in its own right — but rules can be marked `skip_on_derived` where they are meaningless (e.g. a volume-based distributional check on a 1 % sample). |
| **FR-DATA-35** | Lineage is queryable in both directions: "what was this built from?" and "what depends on this?" — the latter spanning Models, Rating Versions, and Monitoring baselines (used to compute the blast radius of FR-DATA-23). |
| **FR-DATA-36** | Train/test splits are recorded on the *parent* version as a named split artifact, so that two models can be compared on provably identical holdout rows. |

### 3.7 Access, retention, deletion

| ID | Requirement |
|---|---|
| **FR-DATA-37** | Dataset access is role- and dataset-scoped (`06-governance.md`). A user without read access to a Dataset cannot see it in lineage, in a model's provenance, or in search results — only an opaque "restricted" placeholder. |
| **FR-DATA-38** | `archived` Dataset Versions remain readable to Auditors and remain referenceable by existing Models; they cannot be the target of a new fit. |
| **FR-DATA-39** | GDPR erasure is supported as an Admin-only, audited **purge** of specific pseudonymous subject tokens across all versions of a Dataset, producing a new "redacted" version and a tombstone record explaining the gap. Historic Validation Reports and Models are annotated, never silently altered. |

---

## 4. Data contracts

JSON Schemas live in `docs/contracts/schemas/`. Field types below use JSON Schema
vocabulary; every entity also carries the `ArtifactEnvelope` from `00-overview.md` §4.3.

### 4.1 `Dataset`

```json
{
  "slug": "motor-gb-quote-bind",
  "name": "Motor GB — quote & bind",
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

### 4.4 Built-in rule catalogue

Rule IDs here are stable and referenced by workflows and by the UI.

**Layer 1 — Structural** (executed via the stored pandera schema)

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
| `VR-ACT-14` development-maturity | warn | The most recent N months of experience are flagged as immature (IBNR risk) with the configured development pattern; modelling on them without an adjustment is a warning |
| `VR-ACT-15` currency-consistency | fail | All monetary columns share the Dataset's declared currency; no mixed-currency rows |
| `VR-ACT-16` duplicate-claim | warn | No two claims share (policy, date_of_loss, peril, amount) — a classic double-load signature |

**Layer 4 — Distributional / stability** (vs `reference_dataset_version_id`)

| Rule | Default severity | Check |
|---|---|---|
| `VR-DST-1` psi-column | warn at PSI > 0.10, fail at > 0.25 | Per-column PSI against the reference version |
| `VR-DST-2` new-level | warn | Categorical levels present now, absent in reference |
| `VR-DST-3` vanished-level | warn | Levels with material reference exposure now absent |
| `VR-DST-4` null-rate-shift | warn | Null rate moved by more than X percentage points (a broken feed's clearest signal) |
| `VR-DST-5` volume-shift | warn | Total exposure or row count moved more than X % vs reference, period-adjusted |
| `VR-DST-6` mean-shift | warn | Numeric column mean moved more than N reference standard errors |
| `VR-DST-7` target-rate-shift | warn | Observed frequency / severity / burning cost moved more than X % vs reference |
| `VR-DST-8` mix-shift-exposure | warn | Exposure distribution across a declared key factor moved (PSI on the exposure weights, not the row counts) |

Thresholds are Rule Set configuration, not code. Every threshold shown is a default.

### 4.5 Custom validation rule format

Custom rules use the same tagged-union shape (§4.3) with `check` drawn from a fixed
vocabulary — never arbitrary code (governance parity with custom objectives, ADR-0003):

| `check` | Params | Meaning |
|---|---|---|
| `range` | `min_inclusive`, `min_exclusive`, `max_inclusive`, `max_exclusive` | Numeric bounds |
| `set_membership` | `allowed[]`, `case_sensitive` | Value domain |
| `regex` | `pattern` | String format (e.g. postcode) |
| `uniqueness` | `columns[]` | Key uniqueness |
| `not_null` | `columns[]` | Completeness |
| `relationship` | `left`, `right`, `operator` | Cross-column comparison (`exposure_end > exposure_start`) |
| `expression` | `expr` (restricted grammar), `expect` | Row-level boolean predicate |
| `aggregate` | `agg` (`sum`/`mean`/`count`/`quantile`), `group_by[]`, `expect` | Group-level assertion |
| `reference_lookup` | `reference_table`, `key_columns[]`, `as_at_column` | Referential resolution |
| `distribution_compare` | `metric` (`psi`/`ks`/`mean_shift`), `column`, `weight_column`, `thresholds` | Stability vs the reference version |
| `sql` | `query` (single `SELECT`, read-only, run in DuckDB against the version's parquet, must return a row count or a boolean) | Escape hatch for genuinely bespoke checks |

**Governance of custom rules (FR-DATA-21):**

1. Authored by an Analyst or Actuary → `draft`.
2. **Dry-run required** — the rule must execute successfully against at least one existing
   Dataset Version, and the dry-run result is attached to the approval request.
3. Submitted → `review` → approved by an Approver (never the author).
4. `approved` rules are immutable; edits create a new rule version needing re-approval.
5. The `sql` check carries extra controls: parsed and rejected if it contains anything but
   a single `SELECT`, executed against a read-only DuckDB connection with no filesystem or
   extension access, and subject to a hard time budget (FR-DATA-19). It is the only check
   requiring two approvers (see OQ-DATA-3).

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

**Invariants** — `overall = pass` iff no `fail`/`error` and no `warn`;
`pass_with_warnings` iff no `fail`/`error` and every `warn` has an `acknowledgement`.
The transition to `validated` is permitted for `pass` and `pass_with_warnings` only.

### 4.7 `Profile`

```json
{
  "dataset_version_id": "uuid",
  "computed_at": "2026-08-14T09:16:00Z",
  "columns": [
    {
      "name": "driver_age", "semantic_type": "continuous", "dtype": "int32",
      "null_count": 412, "null_rate": 0.0000854, "distinct_count": 74,
      "min": 17, "max": 92, "mean": 43.8, "std": 15.2,
      "quantiles": {"p1": 19, "p5": 22, "p25": 32, "p50": 43, "p75": 55, "p95": 71, "p99": 80},
      "histogram": {"edges": [17, 21, 25, 30, 40, 50, 60, 70, 93], "counts": [...], "exposure": [...]}
    }
  ],
  "one_ways": [
    {
      "column": "driver_age", "banding": "profile_default_deciles",
      "rows": [
        {"level": "17-21", "exposure_years": "82141.20", "claim_count": 9142,
         "claim_amount_minor": 41_882_100_00, "frequency": 0.1113, "frequency_ci": [0.1090, 0.1136],
         "severity_minor": 458_100, "severity_ci": [449_200, 467_300], "burning_cost_minor": 50_990}
      ]
    }
  ]
}
```

### 4.8 `ReferenceTable` / `ReferenceTableVersion`

```json
{
  "slug": "ons-postcode-directory",
  "key_columns": ["postcode_outcode"],
  "payload_columns": ["rating_area", "urbanity", "region"],
  "version": 7,
  "effective_from": "2026-04-01",
  "effective_to": null,
  "row_count": 2987,
  "blob": {"sha256": "…", "media_type": "application/vnd.apache.parquet"},
  "status": "approved",
  "source_note": "ONS NSPL Feb 2026 release, aggregated to outcode."
}
```

**Invariants** — for a given key, validity intervals `[effective_from, effective_to)` across
versions must not overlap (FR-DATA-29), enforced by a PostgreSQL exclusion constraint.

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/sources` | Register a Source (FR-DATA-1) |
| `GET` | `/api/v1/sources` | List sources (credentials redacted) |
| `POST` | `/api/v1/sources/{id}/preview` | Read first N rows + inferred schema without creating a version |
| `POST` | `/api/v1/datasets` | Create a Dataset (metadata + data dictionary) |
| `GET` | `/api/v1/datasets` | List / filter datasets |
| `GET` | `/api/v1/datasets/{slug}` | Dataset detail incl. `latest_version` |
| `PUT` | `/api/v1/datasets/{slug}/dictionary` | Update the Data Dictionary (audited) |
| `POST` | `/api/v1/datasets/{slug}/versions` | **202** Start an Ingestion Run → Job (FR-DATA-2) |
| `GET` | `/api/v1/datasets/{slug}/versions/{version}` | Dataset Version detail |
| `PATCH` | `/api/v1/datasets/{slug}/versions/{version}/schema` | Correct the inferred schema while `draft` (FR-DATA-4) |
| `POST` | `/api/v1/dataset-versions/{id}/validate` | **202** Run validation → Job (FR-DATA-15) |
| `GET` | `/api/v1/dataset-versions/{id}/validation-reports` | Report history |
| `GET` | `/api/v1/validation-reports/{id}` | Full report |
| `POST` | `/api/v1/validation-reports/{id}/results/{rule_id}/acknowledge` | Acknowledge a warn, with justification (FR-DATA-17) |
| `POST` | `/api/v1/dataset-versions/{id}/transition` | `{"to": "validated" \| "archived"}` — enforces §4.6 invariants |
| `GET` | `/api/v1/dataset-versions/{id}/profile` | Profile artifact (FR-DATA-25) |
| `GET` | `/api/v1/dataset-versions/{id}/one-ways?column=` | One-way summary for a column (FR-DATA-26) |
| `GET` | `/api/v1/dataset-versions/{id}/compare?against={id}` | Profile comparison / PSI (FR-DATA-28) |
| `POST` | `/api/v1/dataset-versions/{id}/derive` | **202** Sample / split / filter / union (FR-DATA-33) |
| `GET` | `/api/v1/dataset-versions/{id}/lineage?direction=up\|down` | Lineage graph (FR-DATA-35) |
| `GET` | `/api/v1/dataset-versions/{id}/rejected` | Quarantined rows (paged) (FR-DATA-7) |
| `POST` | `/api/v1/validation-rules` | Create a custom rule → `draft` (FR-DATA-21) |
| `POST` | `/api/v1/validation-rules/{id}/dry-run` | **202** Execute against a chosen version |
| `POST` | `/api/v1/validation-rules/{id}/submit` | Submit for approval |
| `GET`/`PUT` | `/api/v1/datasets/{slug}/rule-set` | Read / replace the Rule Set (creates a new rule-set version) |
| `POST` | `/api/v1/reference-tables/{slug}/versions` | Load a new Reference Table Version (FR-DATA-29) |
| `GET` | `/api/v1/reference-tables/{slug}/lookup?key=&as_at=` | Point lookup for debugging (FR-DATA-31) |

**Error codes owned by this module:** `DATASET_NOT_VALIDATED`, `DATASET_VERSION_IMMUTABLE`,
`SCHEMA_INFERENCE_CONFLICT`, `COLUMN_NAME_COLLISION`, `DIRECT_IDENTIFIER_PRESENT`,
`VALIDATION_HAS_FAILURES`, `WARN_NOT_ACKNOWLEDGED`, `ACKNOWLEDGE_FORBIDDEN_ROLE`,
`RULE_NOT_APPROVED`, `RULE_SEVERITY_DOWNGRADE_FORBIDDEN`, `RULE_TIMEOUT`,
`REFERENCE_INTERVAL_OVERLAP`, `REFERENCE_VERSION_NOT_PINNED`, `SOURCE_UNREACHABLE`,
`REJECT_RATE_EXCEEDED`.

### 5.2 `pricing-core` interfaces

```python
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

def compile_pandera_schema(schema: DatasetTableSchema) -> pandera.polars.DataFrameSchema

# packages/pricing-core/src/pricing_core/data/profile.py
def profile_version(
    parquet_uris: Mapping[str, list[str]],
    schema: DatasetSchema,
    *,
    one_way_columns: Sequence[str],
    weight_column: str = "exposure_years",
) -> Profile                        # DuckDB-backed (FR-DATA-27)

def compare_profiles(current: Profile, reference: Profile) -> ProfileComparison   # PSI etc.

# packages/pricing-core/src/pricing_core/data/exposure.py
def explode_period(df: pl.DataFrame, spec: ExplodePeriodSpec) -> pl.DataFrame     # FR-DATA-11
def attach_claims(exposure: pl.DataFrame, claims: pl.DataFrame, spec: AttachClaimsSpec) -> AttachResult
```

All of these are pure: no I/O, no database, `parquet_uris` read through an injected
filesystem object supplied by the caller (ADR-0001).

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
| **pandera (Polars backend)** | Layer-1 structural schemas, stored with each version | Lazy validation to collect all errors in one pass; schema serialisation. Polars `DataFrame` and `LazyFrame` both supported since 0.19; **0.32+ ships an optional Narwhals-powered backend that keeps validation fully lazy** (`pandera[narwhals,polars]`) — adopt it, since NFR-DATA-2 requires the structural layer to fail fast in ≤ 2 min without materialising the dataset. See [`research`](../research/track-a-findings.md) F9 |
| **Apache Parquet / Arrow** | Dataset Version storage, `decimal128` for money and exposure | Row groups sized for predicate pushdown; explicit schema persisted |
| **Object storage (S3/MinIO)** | Content-addressed parquet blobs (ID-4) | Multipart upload for large versions |
| **PostgreSQL 16** | Version metadata, reports, rule sets, lineage edges | JSONB for report bodies + GIN indexes; exclusion constraint for reference effective dating (FR-DATA-29) |
| **Celery + Redis** | Ingestion, validation, profiling, derivation Jobs | Progress callbacks; per-rule time budgets (FR-DATA-19) |
| **Dagster** | Scheduled recurring ingestion from `pipeline` sources | Partitioned assets keyed by dataset version |
| **SciPy** | Poisson/Gamma confidence intervals on one-ways (FR-DATA-26) | Exact CIs at low counts, not normal approximations |
| **ECharts + TanStack Table (frontend)** | One-way charts with CI bands; report and rejected-row grids | Virtualised grids for large offending samples |

New skills this spec adds to `skills-map.md`: pandera Polars backend + serialisation;
DuckDB read-only sandboxing; PostgreSQL exclusion constraints for effective dating;
PSI/KS implementation details; parquet decimal logical types.

---

## 9. Non-functional requirements

| ID | Requirement |
|---|---|
| **NFR-DATA-1** | Ingest + prepare 10 M rows × 80 columns from parquet in ≤ 15 min on a 16-core worker; from CSV in ≤ 30 min. |
| **NFR-DATA-2** | Full validation of a 10 M-row version with ~50 rules completes in ≤ 10 min; structural layer alone in ≤ 2 min so it can fail fast. |
| **NFR-DATA-3** | Profiling a 10 M-row version completes in ≤ 5 min and requires no more memory than 2× the largest column's compressed size (DuckDB streaming, not full materialisation). |
| **NFR-DATA-4** | A one-way summary read from a stored Profile returns in < 300 ms (NFR-OVR-4); it is never computed on request. |
| **NFR-DATA-5** | Validation is deterministic: the same version + rule set version produces byte-identical report bodies apart from timestamps and job ids (FR-OVR-8). |
| **NFR-DATA-6** | Storage overhead of a Dataset Version is ≤ 1.2× the parquet payload; identical tables across versions are deduplicated by content hash (ID-4). |
| **NFR-DATA-7** | The validation report API returns the summary in < 500 ms for reports with up to 500 rules; offending samples are lazily paged. |
| **NFR-DATA-8** | Audit: dataset transitions, acknowledgements, dictionary edits, rule-set changes, and purges each emit an Audit Event with before/after state (FR-OVR-4). |
| **NFR-DATA-9** | A user-supplied `sql` check cannot read outside the target version's parquet files, cannot write, cannot load DuckDB extensions, and is killed at its time budget (FR-DATA-19, §4.5). |
| **NFR-DATA-10** | Ingestion of a source that fails mid-run leaves no partially-visible version: version rows become visible only on successful commit. |

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-DATA-1** | Should large-loss handling (capping, spreading above a threshold) be a *preparation* step baked into the dataset, or a *modelling* decision applied at fit time? Baking it in makes exposure/claims totals consistent everywhere; applying it at fit time lets one dataset serve multiple capping assumptions. |
| **OQ-DATA-2** | Do we support incremental/append ingestion (adding a new month to an existing version) or is every version a full snapshot? Full snapshots are simpler and match immutability; append is far cheaper for a 10-year book refreshed monthly. |
| **OQ-DATA-3** | Does the `sql` custom check earn its keep given the sandboxing burden, and if kept, is dual approval the right control or should it be admin-only? |
| **OQ-DATA-4** | Where do IBNR / claims-development adjustments live — a preparation step producing developed claim amounts, a modelling offset, or out of scope entirely (user supplies developed data)? `VR-ACT-14` currently only *warns*. |
| **OQ-DATA-5** | Should the platform hold the ONS/ABI reference sets as shipped data, given their licensing terms, or only ship loaders and require the user to supply the files? |
| **OQ-DATA-6** | Is `warn` acknowledgement per-rule-per-report the right granularity, or should an actuary be able to pre-approve a recurring known warning for a defined period (with expiry) to avoid acknowledgement fatigue? |
