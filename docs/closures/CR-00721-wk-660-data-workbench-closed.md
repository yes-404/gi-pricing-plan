---
id: CR-721
family: closure
kind: work
title: WK-660 — Data Workbench: closed
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-15
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/closure-records.md
---

### WK-660 — Data Workbench: closed 2026-08-15

**Scope, derived from `01` §3 before opening any source file: 50 requirements** — 40
`FR-DATA` (§3.1 nine, §3.2 six, §3.3 ten, §3.4 four, §3.5 four, §3.6 four, §3.7 three) and
10 `NFR-DATA`. Plus three endpoints reassigned from WK-658 by the interface audit: the two blob
routes and `/metrics`.

**The roadmap's row says "All 49 `DATA` requirements"; the spec holds 50.** The
disagreement is a finding, not a rounding: FR-34 ("ingestion produces full snapshots",
OQ-558) was appended in PR #16 *after* the row was written in PR #15. Exactly the shape
of WK-658's "of 60" against a spec holding 61. The row is left as written and this record
carries the correction — a roadmap row states what was known when it was written.

| Deliverable (roadmap §6) | Evidence |
|---|---|
| Sources | Register, list, preview; credentials held by reference and absent from every response shape, asserted rather than redacted |
| Ingestion | Blob → version → profile in one Job; rejects quarantined as a table on the version (FR-32); idempotent by source fingerprint |
| Preparation recipes | Applied **during** ingestion and stored with the version; `explode_period` preserves exposure exactly; expressions compile to Polars through a restricted AST, never `eval` |
| Parquet | Content-addressed blobs, deduplicated across versions by digest, presigned download |
| Profiling | Aggregated in DuckDB; the frame and parquet paths produce identical Profiles; one-ways read from storage and never recomputed |
| Four validation layers + built-in catalogue | **38 check implementations**, each with a firing and a non-firing case; the `sql` escape hatch sandboxed. **Not 38 shipped rules** — corrected 2026-08-15, see below |
| Reference tables | Effective-dated versions, half-open intervals, overlap refused by a `btree_gist` exclusion constraint, publish-then-pin |
| *(reassigned from WK-658)* Blob endpoints, `/metrics` | Presigned upload and 307 download; Prometheus exposition with bounded label cardinality |

**Gate (local, 2026-08-15):** ruff clean · mypy --strict on 83 source files · import-linter
3 kept / 0 broken · **565 tests** · 7 generated contracts match the models · docs audit
15/15 · req-coverage 118 of 418 requirements marked.

**Coverage, all three axes re-derivable from documents:**

| `scope-audit.py DATA …` | Result |
|---|---|
| requirements | **48 / 50** (96 %) |
| `--endpoints` | **28 / 28** (100 %) |
| `--catalogue VR` | **1 / 38** — the number this check reports since it was fixed on 2026-08-15. It read 38/38 by counting ids in **prose** |

**Enforcement proven, not assumed** (§13 rule 3). Every check the workstream added was
shown to fail on deliberately broken input, with the exit code read from the check itself
rather than from a `grep` in the pipeline after it:

- `--endpoints` against a contract with one path deleted → 27/28, exit 1.
- `--catalogue VR` against a rule id removed from source → 37/38, exit 1. **This one was
  silently weak**: it scanned test files too, so a rule existing nowhere but in a test read
  as implemented. The broken run failed to notice the deletion, which is how the weakness
  was found; the scan was made source-only.

  > **It was still weak, and the injection above is why the second weakness survived.**
  > Deleting an id from a *docstring* also makes the count drop, so the proof passed while
  > the check was measuring prose. An independent audit found the whole 38 were docstring
  > mentions — and that one reading `VR-ACT-1/2/8` was slash-expanded into three, two of
  > which (`VR-ACT-2`, `VR-ACT-8`) appear in no source file at all.
  >
  > Corrected 2026-08-15: the scan parses to an AST and counts ids a program **evaluates**.
  > It reports **1 of 38**, and that one is an id inside an error message.
  >
  > **What WK-660 shipped is 38 reusable check implementations and no built-in rule
  > catalogue.** `01` §4.4 says "Rule IDs here are stable and referenced by workflows and
  > by the UI", which is a claim about data — `BUILTIN_ROLES` is what it looks like when it
  > is true. The rules the freMTPL2 seed installs are constructed in `examples/`, not
  > shipped by the platform. The capability §4.4 describes is **not delivered**; the
  > checks behind it are.
- The DuckDB sandbox: dropping `enable_external_access` makes three tests fail, and
  removing the interrupt watchdog hangs the timeout test rather than failing it.
- The two profiling paths: reinstating either the tie-break or the quantile default breaks
  the agreement test.
- Metrics cardinality: resolved-path labels, path-labelled 404s, status codes instead of
  classes, and a gauge that never clears — four injections, four caught.
- The catalogue rules: five injections, **four** caught on the first pass. The miss was
  real — the `vanished_level` fixture had no level below the materiality threshold, so
  deleting the filter changed nothing. It has one now.

**NFRs measured, not asserted.**

| NFR | Measured | Budget |
|---|---|---|
| NFR-465 parquet ingest + prepare | 5.2 s | 900 s |
| NFR-465 CSV ingest + prepare | 29.6 s | 1800 s |
| NFR-466 validation, ~50 rules | 0.3 s | 600 s |
| NFR-466 structural layer alone | 0.1 s | 120 s |
| NFR-467 profiling | 91.7 s | 300 s |
| NFR-467 memory | 113 MB → 236 MB above baseline over a 10× payload increase | does not scale with rows |
| NFR-471 report summary, 500 rules | 30 ms | 500 ms |

`scripts/bench-data.py` at 2 M rows × 80 columns, extrapolated to 10 M; the machine has
13 GB and 80 float64 columns at 10 M rows is 6.4 GB resident before any operation runs.

**Specification defects found by implementing it.** Five, each resolved in the spec rather
than worked around:

| Defect | Resolution |
|---|---|
| NFR-467 bounded profiling memory at "2× the largest column's compressed size" — 30.7 MB, while a Python process with `polars`, `duckdb`, `scipy` and `pydantic` imported occupies 140 MB before reading a byte | Amended to the property that is protective *and* measurable: memory does not scale with row count |
| `01` §4.6's `overall` invariant left unnamed the state every report with warnings is in when written, and made an immutable artifact's verdict depend on acknowledgements arriving days later | `overall` is now a function of the rule results alone; acknowledgement is a fact *about* a report, checked at promotion |
| `01` §5.1 had no code for a duplicate acknowledgement | `ACKNOWLEDGEMENT_ALREADY_RECORDED` appended |
| `01` §4.5 read as requiring an Admin author *in addition to* `dataset:write`, leaving no built-in role able to author a `sql` rule | Read as *instead of*, per §4.5 step 5; the permission depends on the check |
| `07` §3 had no requirement about metric label cardinality — a property whose violation is silent | `FR-407` appended |

**Not delivered by WK-660.** Every unevidenced requirement with a verdict:

| Item | Verdict |
|---|---|
| NFR-465, NFR-466 | **Measured, not tested.** Numbers above. A timing assertion on a shared runner fails for reasons unrelated to the code and teaches everyone to re-run it — the same reasoning that left NFR-529 measured rather than asserted |
| FR-54, streaming half | **Reassigned to WK-665.** The distributional half is delivered — those rules read the reference Profile instead of re-scanning. Streaming structural rules over parquet row groups needs a real 10 M-row dataset to be designed against, which arrives with the freMTPL2 seed |
| `POST /sources/{id}/preview` for `object_store` / `sql` sources | **Partial.** Implemented for uploaded bytes, the flow FR-29 is written around. The other source kinds need connectors, which no requirement in WK-660's scope asked for |
| `pipelines/` — scheduled ingestion | **Deferred to WK-665.** `CLAUDE.md` §2 assigned it to 1a WK-660; WK-660's own roadmap row never named it, and `pipeline` as a Source *kind* is registrable without a scheduler. The mark is corrected rather than the gap hidden |
| `GET`/`POST /api/v1/environments`, `PUT .../settings` | **WK-674**, which owns `07` FR-428, FR-429, FR-430, FR-431 |
| `00` §5.4 `If-Match` optimistic concurrency | **Delivered in WK-661, 2026-08-17** — see the model-lifecycle slice record, which also corrects the reasoning below. *(Original WK-660 verdict, kept:)* **Not delivered, reassigned to WK-661.** WK-658 named WK-660 as "the first workstream with versioned artifacts", which was right — but WK-660's mutating endpoints act on a version's *status*, and the transition state machine already refuses every unsafe move by reading the current status under a row lock. An ETag would add a second, weaker guard over the same field. `CONFLICT_STALE_WRITE` is still absent from the error registry; the first genuine lost-update risk is a Model's editable metadata in WK-661, and it should be built there against a real one |
| FR-39's refusal | **Not delivered, and not previously stated.** `DIRECT_IDENTIFIER_PRESENT` is registered and raised nowhere; `modelling_forbidden_columns` has no caller; all four FR-39 markers sit on `pseudonymise`, the other half of the requirement. Closed as **FR-40** on 2026-08-15. Found by an independent audit, not by this record |
| pandera | **Not a dependency, and never was.** WK-660 delivered the structural layer over Polars while `01` named pandera as its mechanism in four places and `skills-map.md` marked it ★★ *Verified*. The spec is corrected (2026-08-15); the layer itself is delivered and tested |
| `00` §5.4 `Idempotency-Key` header | **Delivered, after the audit found it wrong.** All four `202` endpoints accept it. It had been implemented as a *query parameter* on one of them — a retry is generated by an HTTP client that knows nothing about the endpoint's query string, and a key in the URL is also a key in every access log |

**Retrofit list (§5) — where WK-660 leaves each item:**

| Item | State after WK-660 |
|---|---|
| Append-only audit in the caller's transaction | **Delivered and used.** Every WK-660 mutation — version transitions, acknowledgements, dictionary edits, rule-set replacement, reference loads, schema corrections — writes through `audit.record` inside the caller's unit of work. 46 audit tests |
| Artifact immutability + versioning + `parent_id` | ~~**Delivered.**~~ **Partial — corrected 2026-08-15, then completed the same day.** Every WK-660 artifact is `frozen=True` *in Python*, versions are allocated under an advisory lock and never reused, and `derived_from` carries lineage. But **nothing stops the database being written directly**: only `audit_events` has append-only triggers, and an audit rewrote 190 stored reports from `fail` to `pass` in one statement. A `frozen` Pydantic model is a rule about one process; the retrofit list means the guarantee. Closed as **FR-43** on 2026-08-15: append-only triggers and `SELECT, INSERT`-only privileges on the three artifact tables, five injections proven. The check constraint named here does hold — but see the note under WK-663 about the state FR-53 leaves it in |
| `model-schema` as SSOT | **Delivered.** `Dataset`, `DataDictionaryEntry`, `PiiClass`, `RecordGrain`, `Profile`, `ValidationReport` and the rule shapes all live there; the contract regenerates and CI fails on drift |
| Job model with progress and cancellation | **Delivered and exercised.** The four `dataset.*` handlers run through it; progress and cooperative cancellation are the `pricing-core` `ProgressCallback` |
| Decimal money discipline | **Delivered.** `MoneyMinor` and `DecimalStr` throughout `01`'s shapes; one-way ratios derive from the stored Decimal so a published frequency equals published claims ÷ published exposure |
| `trace_id` propagation | **Delivered by WK-658, used by WK-660.** Carried into every Job and every audit event WK-660 writes |
| RBAC from the first endpoint | **Delivered.** Every route declares its permission; acknowledgement raises the spec's own `ACKNOWLEDGE_FORBIDDEN_ROLE` rather than a generic denial |
| Content-addressed blob store | **Delivered by WK-658, load-bearing in WK-660.** Parquet tables are blobs; identical tables across versions are stored once, asserted by test |

---
