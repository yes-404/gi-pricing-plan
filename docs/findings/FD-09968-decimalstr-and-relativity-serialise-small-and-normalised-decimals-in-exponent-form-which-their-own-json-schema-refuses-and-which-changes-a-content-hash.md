---
id: FD-9968
family: finding
title: DecimalStr and Relativity serialise small and normalised decimals in exponent form, which their own JSON Schema refuses, and the spelling changes a content hash
status: active
created: 2026-09-30
owner: auditor
tree: 32f3fa92afad81d1be611b21ae16ff35211eded8
corrected_by: []
relates: [WK-1178, FR-10, FR-451]
---

# FD-9968 — `DecimalStr` serialises exponent form and preserves spelling, so a value can violate its own schema and change a hash

## Finding

**Severity (proposed): medium.** The maintainer sets it after the count; the reasons are under *Severity*. **Proposed
by the auditor; the disposition is the lead's.** FD-9968 is a working id, minted at the records PR.

`model_schema.money.DecimalStr` (`packages/model-schema/src/model_schema/money.py:85-91`) and `Relativity`
(`:94-99`) serialise with `PlainSerializer(str, …)`, and `str()` of a `Decimal` uses exponent form outside
a plain-positional range. Two consequences, both measured at `origin/main`
`32f3fa92afad81d1be611b21ae16ff35211eded8` (evidence 1 to 3):

1. **A value the type accepts serialises to a string the type's own JSON Schema refuses.** The generated schema
   for both types is `{"type": "string", "pattern": "^-?[0-9]+(\.[0-9]+)?$"}` (`_DecimalStrSchema`,
   `money.py:46-58`; the pattern is the type's contract: "Exact decimal as a string; never a binary float
   (FR-10)"). `Decimal("0.0000001")` serialises as `"1E-7"`, `Decimal("0.00000000000000000000000000012")` as
   `"1.2E-28"`, and any decimal with a positive exponent, such as `Decimal(100).normalize()`, as `"1E+2"`: none
   matches the pattern. The value round-trips in Python (`Decimal("1E-7")` parses), so nothing fails in-process;
   a consumer that validates against the published contract does.
2. **The serialised spelling follows the input's spelling, not the value.** `"10"` and `"1E+1"` are equal
   decimals and serialise as `"10"` and `"1E+1"`; `"66000.440"` stays `"66000.440"`. So two value-equal contents
   have different bytes, and **any hash taken over the dump differs**. Evidence 3 shows it on the one content
   hash that includes a `DecimalStr`.

`dm-eh-s3`'s RL 9963 (working id 9963, part 1a) found it while ruling the premium ladder and recorded it as an
observation "for the lead", and chose a **new** `PositionalDecimalStr` for the ladder's own fields rather than
change `DecimalStr`, because "`DecimalStr` has 23 uses in `model_schema` outside `money.py` … some of them in
content-hashed artifacts. Changing its serialiser would change stored bytes and hashes beyond this slice."
This record measures that.

## Evidence

Run at `origin/main` `32f3fa92afad81d1be611b21ae16ff35211eded8`, 2026-09-30, by the filer, under
`uv run --no-sync python`; the scripts are kept with the evidence.

**1. The reproduction** (`decstr_repro.py`; the first block is RL 9963's own snippet). Output, verbatim:

```text
1. the RL 9963 part 1a snippet, at this tree:
   '0.0000001'                          -> {"a":"1E-7","r":"1E-7"}
   '0.00000000000000000000000000012'    -> {"a":"1.2E-28","r":"1.2E-28"}
   '10'                                 -> {"a":"10","r":"10"}
   '1E+1'                               -> {"a":"1E+1","r":"1E+1"}
   '66000.440'                          -> {"a":"66000.440","r":"66000.440"}

2. the type's own JSON Schema pattern: ^-?[0-9]+(\.[0-9]+)?$
   re.fullmatch(pattern, '1E-7') -> False
   re.fullmatch(pattern, '0.0000001') -> True
   re.fullmatch(pattern, '1E+1') -> False
   re.fullmatch(pattern, '10') -> True

3. equal values, different bytes: Decimal('10') == Decimal('1E+1'): True | dumps: {"a":"10","r":"1"} vs {"a":"1E+1","r":"1"}
   and arithmetic results: Decimal(100).normalize() -> 1E+2 | dumps: {"a":"1E+2","r":"1"}
```

**2. The uses.** `DecimalStr` is the type of **13 fields in 8 models** (`git grep -n -E ":\s*(tuple\[|list\[)?(DecimalStr|Relativity)"
-- packages/model-schema/src`, minus `money.py`): `DoubleLiftBin.exposure_years` (`comparison.py:136`),
`VersionTotals.exposure_years` (`datasets.py:281`), `AeCell.exposure_years` (`diagnostics.py:93`),
`LiftBin.exposure_years` (`:114`), `BandingMinimums.min_exposure_per_band` (`modelling.py:334`),
`LargeLossTreatment.restoration_loading` and `.loading_factor` (`perils.py:155`, `:165`),
`Reconciliation.tolerance` (`:308`), `Histogram.exposure` (a tuple, `profiles.py:67`), `LevelCount.exposure_years`
(`:110`), `OneWayRow.exposure_years` (`:154`) and `MonotoneInInput.lower` and `.upper` (`regression.py:103-104`).
The 23 in RL 9963 is a line count (`git grep -n "DecimalStr\b"` outside `money.py` also counts imports and the
`__init__` re-export); `Relativity` is declared but is the type of no field. **Where a value feeds a content
hash:** `suite_content_hash` (`regression.py:219`) is `sha256` over
`RegressionSuiteContent.model_dump(mode="json")`, which includes each property's `check`, and `MonotoneInInput`
carries `lower` and `upper`. **These two fields, `MonotoneInInput.lower` and `.upper`, are the only `DecimalStr`
fields in a hash the code computes itself.** `spec_hash` (`backend/src/app/platform/modelling.py:155`,
`SPEC_HASH_VERSION = 11`) hashes `ModelSpec`, which pins a `Banding` by id rather than embedding it, so
`BandingMinimums` is not in it; `bundle_hash` (`compile.py:408`) hashes the graph and the pins, no decimals; the
blob store's digests are over bytes and none of the JSON payloads it stores carries these fields (`model_handlers.py:534`,
`:540` store a booster and a covariance). The `exposure_years` fields are in profile, diagnostics and comparison
artifacts persisted as `jsonb` rows, not hashed.

**3. A content hash that changes with the spelling.** `decstr_repro.py` builds a `RegressionSuiteContent` whose
one property is `MonotoneInInput(lower=…)` and takes `suite_content_hash`. Output, verbatim:

```text
4. a content hash that changes with the spelling (RegressionSuiteContent, `suite_content_hash`, regression.py:219):
   lower='10'           -> dumped '10'           hash sha256:b7986380b94f4741...
   lower='1E+1'         -> dumped '1E+1'         hash sha256:60852424a1223d86...
   lower='0.0000001'    -> dumped '1E-7'         hash sha256:62e4bb1541ed8b41...
   lower='0.00000010'   -> dumped '1.0E-7'       hash sha256:f4201a88382f83b3...
```

Equal values (`10` and `1E+1`) give different suite hashes. The suite hash is pinned as evidence
(`evidence.golden_quotes.suite_content_hash`, `backend/src/app/platform/rating_versions.py:612`, `:639`), so a suite
re-created from the same values with a different spelling would compare as a different suite. That fails loudly
(a hash mismatch), not silently, and needs a `lower` or `upper` an actuary typed in exponent or padded form.

**4. The measured count of committed artifacts holding an exponent-form value.**
*Predicate, verbatim* (`decexp.py`, `python3 decexp.py 32f3fa92afad81d1be611b21ae16ff35211eded8`): over the
tracked blobs of that tree (`git ls-tree -r -z --name-only`, then `git show <ref>:<path>`, so the working tree and
this record's own additions are never read; 1901 files, all decodable as UTF-8), the Python regular expressions below,
the first over any quoted string in the shape `DecimalStr` serialises, the second requiring a `DecimalStr` field name
as its key:

```python
Q = re.compile(r"""(?:"|')(-?\d+(?:\.\d+)?[eE][+-]?\d+)(?:"|')""")
FIELDS = ("exposure_years", "min_exposure_per_band", "restoration_loading", "loading_factor", "tolerance", "exposure", "lower", "upper", "factor")
KEYED = re.compile(r"""(?:"|')(%s)(?:"|')\s*:\s*\[?\s*(?:"|')(-?\d+(?:\.\d+)?[eE][+-]?\d+)(?:"|')""" % "|".join(FIELDS))
```

| Corpus | Result |
|---|---|
| All 1901 tracked files | **7** quoted exponent-form strings in **5** files |
| … in `examples/`, fixtures, golden files, `docs/contracts/` or any JSON, YAML or CSV file | **0** |
| … keyed to a `DecimalStr` field name | **0** |

The 7 are not stored values: `packages/model-schema/tests/test_money.py:78` (`float("1e-7")`, a float the type
must refuse), `packages/pricing-core/tests/test_objectives.py:285` (an assertion that an error detail contains `1e-04`),
`packages/pricing-core/tests/test_rate_table_operations.py:324` (`Decimal("1e-9")` as an `approx` tolerance),
`tests/test_watcher_runtime_state.py:218` and `:243` (`"1407e09"`, an id) and two prose mentions of `1e3` in
`docs/rulings/RL-01322-*.md`. **So no committed artifact holds an exponent-form `DecimalStr` value**, and no
committed file is a content-hashed artifact carrying a `DecimalStr` field (`sha256:` appears only in
`.github/workflows/python.yml`, `docs/process/delivery-process.core.json` and `docs/specs/03-rating-engine.md`).
*Population, so a 0 is not read from an empty corpus:* a second predicate (`decexp2.py`, the same `git show` reading, quoted
plain-decimal strings under a `DecimalStr` field name), finds **34** in tracked files (13 `exposure_years`, 10 `lower`, 8 `upper`, 2
`min_exposure_per_band`, 1 `tolerance`), in tests and specification examples, none in exponent form.
*Positive control:* `decexp_ctl.py` builds a scratch git repository (committed, then read by the same script at `HEAD`) with `{"lower": "1E-7", "upper": "0.5"}`,
`{"exposure_years": "1.2E-28"}` and `{"lower": "0.0000001", "upper": "10", "x": "1E+1"}`: the predicate counts **3**
exponent strings in 3 files (including the positive-exponent `1E+1`), and **2** keyed to a field name; the plain
`0.0000001` and `10` are not counted. The scratch directory was removed.

**5. Stored values (not asked for by the maintainer's count; measured for the severity).** The maintainer asked for committed artifacts only; a
read-only scan of the reachable PostgreSQL databases gives the stored side. *Predicate* (`decexp_pg.py`): per
table, `select count(*) … where r::text ~ '"+-?[0-9]+(\.[0-9]+)?[eE][+-]?[0-9]+"+'`, i.e. a quoted exponent-form
decimal, with one or two quote characters because a `jsonb` column renders its quotes doubled inside a record's text
(the lesson of FD-9949's positive control), in `BEGIN TRANSACTION READ ONLY` with `PGOPTIONS='-c
default_transaction_read_only=on'`. *Corpus:* **81 databases, 3841 tables**. *Result:* **0 rows**. *Positive
control:* a `TEMP` table with `{"lower": "1E-7"}`, `{"lower": "0.0000001"}` and `{"exposure_years": "1.2E-28", "u":
"10"}`: the predicate counts **2** (the two exponent rows; the plain one is not counted). *Population for the hashed
fields:* `decpop_pg.py` counts `regression_suite_versions` in the **15** databases that have the table: **0** suite
versions in all of them, so no stored suite (and no stored `lower` or `upper`) exists to hash. Both multi-database runs
took a gate slot (`gate-1`, `uptime` `15:38:08` load 6.35 to `16:02:08` load 7.69; `gate-2`, `16:09:38` load 4.77 to
`16:09:49` load 5.05). **Not measured:** MinIO objects (a JSON artifact written to the blob store), and any environment
beyond this box; the predicate for it is the same string match over each JSON object's string values. The committed
count (evidence 4) and this stored count are both 0.

## Severity

The maintainer's routing, in `~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 16:34:36 BST — RL 9963 fix
(9b15183cdf8ccca3e6fd1129c4ea1b0c72601cd7): decisions on condition 2, the line's scope, and DecimalStr" (outside the
repository; item (3) quoted verbatim):

> **(3) DecimalStr exponent serialisation: file the FD now, not the backlog.** It sits in content-hashed artifacts, so the longer it goes unfixed the more stored hashes a fix would move. The FD states:
>   - how many committed artifacts contain an exponent-form value today (measured);
>   - the fix direction: positional form, with a hash-migration or version-bump note;
>   - an owner (WK-1178 unless model-schema ownership says otherwise).
>   I set severity after the count.


**Proposed: medium.** For: it is a contract defect on a type used across eight models, the type accepts inputs whose
serialisation fails its own published pattern, and it makes one governed hash (`suite_content_hash`) depend on
spelling; the fix changes bytes and so needs a migration. Against, and why it is not high: **0 committed artifacts
hold an exponent-form value**, no price depends on it, the failure modes are loud (a schema-validation error, or a
hash mismatch), and the only hashed field pair is a regression suite's property bound. The maintainer decides;
low is defensible if the stored count is also 0 and nothing is hashed in production.

## Disposition

**Proposed by the auditor; the verdict is the lead's.**

- **Fix direction.** Serialise positionally, as RL 9963 already rules for the ladder's own decimals
  (`PositionalDecimalStr`: the same float refusal and the same JSON Schema, and a serialiser that renders
  `format(value, "f")`). Two decisions belong to the fix's plan, not to this finding: (a) **whether `DecimalStr` itself
  changes or a second type is kept** (RL 9963 kept `DecimalStr`, to avoid changing stored bytes in S3; this finding
  is the count that decides it), and (b) **whether to also normalise trailing zeros** so equal values have one
  spelling (`66000.440` and `66000.44`), which the positional form alone does not do. Normalising and rendering
  positionally together makes the serialised form a function of the value.
- **Hash migration or version bump for already-hashed artifacts.** `suite_content_hash` has no version today.
  `spec_hash` does (`SPEC_HASH_VERSION`, `v11:` prefix and the same number inside the payload, precedent: a
  digest of an older version is "stale and findable with `LIKE 'v10:%'`"). Changing the serialisation changes
  `suite_content_hash` for any suite whose `lower` or `upper` is not already in normal positional form, so the fix
  either carries a `suite_content_hash` version in the payload and prefix (the `spec_hash` precedent), or proves by a
  read-only count that no stored suite is affected and records that. Evidence 5 is that count for the reachable stores.
- **Owner: WK-1178**, the standing maintenance Work (`docs/roadmap.md`, the WK-1178 row: "work that belongs to no other
  Work"; `docs/process/document-ids.md` §1.9 routes hotfixes there). No Work in the roadmap owns `model-schema` as a
  component: the rows that name it are `WK-657` (repo foundations, closed) and `WK-692` (Phase 1b's non-browser
  work, closed), and `document-ids.md` names `model-schema` only as the source the contracts are generated from
  (`:171`). A `model-schema` type change also regenerates `docs/contracts/` and runs the contract guard
  (`backend/tests/test_contracts.py`, the `contract-guard` skill), which the slice's write set must carry.
- **Acceptance, red first:** `Decimal("0.0000001")`, `Decimal("0.00000000000000000000000000012")` and
  `Decimal(100).normalize()` each serialise to a string that matches the type's JSON Schema pattern; two value-equal
  inputs (`"10"` and `"1E+1"`; `"66000.440"` and `"66000.44"`, if normalising is chosen) give one serialised form and one
  `suite_content_hash`; a generated-contract validation of a model dump for a small value passes.

**Event that next confirms or discharges it:** the WK-1178 slice merges with a positional (and, if decided, normalised)
serialiser, the contract regenerated, and the `suite_content_hash` handling (version bump or a recorded zero count).

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it. The severity and owner
are the maintainer's.

Ownership shape: event
