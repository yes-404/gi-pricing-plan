---
id: CR-720
family: closure
kind: work
title: WK-666 — freMTPL2 data seed: closed
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-15
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/closure-records.md
---

### WK-666 — freMTPL2 data seed: closed 2026-08-15

The data half of WK-665 (`07` FR-439), taken before WK-663 so the frontend has real data to
render and so the platform meets a dataset nobody generated. Phase 1a's exit criterion is
now runnable rather than only tested:

```bash
uv run python examples/fremtpl2/fetch.py && uv run python examples/fremtpl2/seed.py
```

**678 013 rows, two versions, 13.4 s end to end**, driving real Jobs through
`execute_job` — the path a worker takes in production, not the services underneath it.

| | Result |
|---|---|
| v1, the file as uploaded | **fails** — 571 rows carry an exposure up to 2.01 (VR-ACT-2). Promotion refused with `VALIDATION_HAS_FAILURES` |
| v2, one preparation step later | `pass_with_warnings` — 125 claims ≥ €35 630 flagged for large-loss treatment and **not removed**; acknowledged by an actuary; **`validated`** |

The 571 figure agrees with an independent `awk` count over the raw file, and nothing about
the failure is injected: freMTPL2's exposure anomaly is in the file as published.

**Measured on real data** — corroborating rather than replacing WK-660's synthetic
extrapolations:

| | 678 013 rows | → 10 M | Budget |
|---|---|---|---|
| Ingest + prepare + profile | 2.9 s | 43 s | 900 s (NFR-465) |
| Validation, 9 rules | 0.3 s | 4.4 s | 600 s (NFR-466) |

#### Three defects in WK-660, found by real data after WK-660 closed

Recorded here rather than by amending WK-660's record: the record states what was known when it
was written, and this is what a real dataset was always going to add.

| Defect | Resolution |
|---|---|
| **`allowed_values` read `values` where `01` §4.5 names the parameter `allowed`.** Its declared domain was therefore always empty, so it **failed every row** — naming as offenders the very values the author had allowed. It refused a 50 000-row dataset on the first run of the seed | Both names accepted, `allowed` preferred; an absent domain now **skips**. `case_sensitive` implemented, which §4.5 also declares |
| **Seven of the eleven check names `01` §4.5 declares for custom rules were unregistered.** A rule authored exactly as the spec documents produced `unknown_check` → an `error`, making FR-50 undeliverable. `scope-audit --catalogue VR` could not see it, because that audits the built-in rule *ids* while this is the custom-rule *vocabulary* — two different lists, and only one had a check | `regex`, `relationship`, `expression`, `aggregate` and `distribution_compare` implemented; `set_membership` and `uniqueness` aliased to the built-ins they duplicate, so a rule set citing either keeps working. 11/11 |
| **The whole-catalogue probe tested one direction only.** It asserted no check reports `pass` with nothing to check, and never that none reports `fail` — which is why the first defect survived it. The first attempt to extend it did not bite either: its target column was absent, so every check errored before it could condemn anything | Split into two tests, one per direction, the second against a frame whose columns *exist* and whose rules carry no configuration. Proven against the real defect: it names `allowed_values` and its alias |

Two further findings needed no code change and are recorded in
[`examples/fremtpl2/README.md`](../../examples/fremtpl2/README.md): `IDpol` normalises to
`i_dpol` (no mechanical splitter can know `ID` is the acronym; `source_names` keeps the
original and the recipe renames it), and `ingest_upload` accepts one table per version
while `01` §4.2's `tables[]` is plural — **multi-table ingestion is a gap**, and the seed
joins the two source files before upload as an analyst would today.

**Not delivered by WK-666.** The rest of FR-439 — models and a rating version in the
seeded workspace — needs WK-661, and `NFR-529`'s "usable seeded state in < 5 min" is not
yet measured from a cold compose stack. Both stay with **WK-665**.

---
