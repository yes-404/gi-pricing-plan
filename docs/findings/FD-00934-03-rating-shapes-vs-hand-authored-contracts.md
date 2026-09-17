---
id: FD-934
family: finding
title: 03 rating shapes vs hand-authored contracts
status: active                  # active → closed | retired (§1.2a)
created: 2026-08-31
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F27.md
---

# F27 — 03 rating shapes vs hand-authored contracts

**Register row:** `docs/findings/register.md`, the row self-naming `(F27)`. This file is the
evidence essay migrated out of that row's Concerns and Decision cells, per RFC-896 P4 and
`docs/audit/findings/README.md`'s naming and compression rules. The row keeps the index —
Finding id, a short Concerns synopsis, Work item, Phase, and Decision compressed to its
disposition — and is the record `register-lint.py`, `register-owed.py` and
`scripts/audit-docs.py` check 25 all read; nothing here is parsed by any of them.

Migrated 2026-08-31 as the RFC-896 P4 exemplar, chosen because it is the longest live row
and because RL-913 (`docs/rulings/RL-00913-q5-file-by-the-f-id-verbatim-the-requirement-id-cannot-name-a-file-and-is-cross-linked-from-inside-it.md`) names this row's
own `(c)` limb as the worked example for "limbs never mint a filename." Content below is
carried over verbatim from the register row as it stood at `35b62b8`, reformatted into
sections; no wording is changed.

## Concerns — the divergence, enumerated

`rating-version`, `rating-algorithm`, `rate-table` ship in `model-schema` (`rating.py:104`,
`:341`, `:651`; plus `RateTableVersion` `:818` and `RateTableDiff` `:684`) and each has a
hand-authored contract under `docs/contracts/schemas/`, but nothing has ever compared the
two: `grep -n "RatingVersion\|RatingAlgorithm\|RateTable" scripts/generate-contracts.py`
returns zero (a true negative — `GENERATED_SHAPES` values are literal class names, consumed
by `getattr(model_schema, name)` at `:174`), and `backend/tests/test_contracts.py` excluded
all three as `"later-phase — 03 rating"`, a reason that expired when WK-669 and WK-670 built them.

Live divergences, enumerated rather than counted because this row's first version said
"two" and the second field alone turned out to be seven (a bare count in this area has now
aged four times in one day; the list is the artifact).

**`scoring.schema.json`**: `purpose` has five values in `03:63` and four at `:12` —
`cancellation`, added 2026-08-18 with FR-218.

**`rate-table.schema.json` vs `model-schema`'s `RateTableVersion`**: missing `storage`
(added 2026-08-18 with FR-232 per `03:310`), `cells`, `created_by_operation`,
`created_by_import`; and carrying `bulk_operations`, `diff_vs_previous`, `diff_vs_seed`,
which the model does not define. `slug`/`version` come from the composed
`common/artifact-envelope.schema.json` and are not divergences.

**And one defect harder than missing-or-extra: the contract is unsatisfiable for half of
what FR-232 defines.** Its `required` list carries `rows`, typed `array` with
`minItems: 1`; `_cells_match_storage_mode` raises *"a parquet version addresses its cells by
a BlobRef, never inline rows (FR-232)"* whenever `storage != ROWS`. So a
parquet-stored `RateTableVersion` — the whole point of FR-232's spill-above-threshold
rule — **cannot satisfy this schema at any value.** The file is not stale, it is wrong.

**The code is not the stale side**: `RateTableVersion.storage: RateTableStorageMode` exists
with a `_cells_match_storage_mode` validator, so FR-232 is implemented and only the
Phase-0 hand-authored contract was left behind.

## Decision — reasoning

**Carry forward with an owner, and WK-669/WK-670 are NOT reopened.** Reopening a Work close is the
maintainer's alone (`CLAUDE.md` §13) and this is a missing *check*, not a defect in what
those workstreams delivered — reopening would re-litigate rather than fix. Three things are
separated deliberately:

### (a) — landed with this row

The three exclusion reasons now say what is true, because a false reason is what let this
survive two closes.

### (b) — WK-671's, accepted

RL-878's fourth obligation on Task 1.4, which keeps `scoring` from becoming the fourth
uncompared shape, the only part that is in WK-671's own scope.

### (c) — unowned, needs its own authorisation

The systemic check comparing every spec-declared shape against its hand-authored contract,
and whether the three types join the generated tier.

**Asked and answered: does this row own the `storage` correction itself, since the contract
is wrong on `main` now?** No, and deliberately. A hand-patch of `storage` alone would leave
six divergences in the same file, produce a contract that is wrong in fewer places and
still wrong, and spend the evidence that motivates (c) — the divergence is structural, not
a missed field.

**The unsatisfiability makes that decisive rather than merely tidy**: adding the four
missing fields still leaves `required` demanding `rows` from a parquet version, because
`required` has to become *conditional on a field the contract does not yet have*. There is
no partial patch that leaves this file correct. The correction *is* (c): regenerate from
`model-schema`, which is what joining the generated tier means. Until then the contract is
knowingly stale and this row is where that is written down. Assigning (c) a workstream row
is re-planning.

**Owner decided (RL-860): the §14 review at WK-671's close**, bundled with F29 and the
mypy files-coverage gap (F33) as **one** gate-coverage item — one mechanism answers all
three, so a partial fix on any single row is not the target shape. Sibling of F26: both are
gaps where a green gate means *unrun*, not *passed*.
