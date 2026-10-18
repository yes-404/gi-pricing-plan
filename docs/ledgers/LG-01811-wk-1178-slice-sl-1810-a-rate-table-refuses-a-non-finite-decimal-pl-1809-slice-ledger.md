---
id: LG-1811
family: ledger
title: WK-1178 slice SL-1810 — a rate table refuses a non-finite decimal as a named FR-234 issue (PL-1809), slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-18   # filed 2026-10-18 under working id 8109; minted 2026-10-18 as LG-1811
owner: executor
tree: 4a53f19492ad73ebfb699cabcab19765c68a5a76
phase: P2
work: WK-1178
slice: SL-1810
plans: [PL-1809]
corrected_by: []
relates: [FR-234]
---

# LG-1811 — WK-1178 slice SL-1810: a rate table refuses a non-finite decimal

*(Minted 2026-10-18 as PL-1809, SL-1810 and LG-1811 from the lead's working ids PL 8107, SL 8108 and LG 8109; section 3 below records the re-point and keeps the working ids it re-pointed.)*

**Base:** merge `e5e8cca2` of `origin/main` `4a53f19492ad73ebfb699cabcab19765c68a5a76` into the branch. Commit 1 is `0ac06deb`; commit 2 (the code) follows. The two are not squashed locally.

## Assumptions and build-time lines

- **DP-1 assumption.** No stored rate-table row holds a non-finite value, and the fix closes every write path (seed, manual edit, import, bulk). A diff over a legacy non-finite row raises the named `ValueError("OUT_OF_BOUNDS: …")` and is not mapped to a 422 (DP-1 (a)).
- **BUILD-TIME (f) pin and default traps.** Test (f) is replaced by the pin `test_a_bulk_operation_cannot_be_given_a_non_finite_percentage`. The default `Decimal` traps raise and do not yield ±Inf/NaN: `git grep -n "setcontext\|getcontext()\|localcontext\|traps" -- packages/pricing-core/src/pricing_core/rate_tables` printed nothing, and `git grep -n "setcontext\|getcontext()" -- packages backend/src` (tests excluded) printed nothing, rc 0, at the merged head.
- **Ordering deviation from PL-1809's "No change" row.** `uplift_table` and `uplift_by_filter` built the operation record *after* `_validate_result`. The record's `UpliftTableParameters` / `UpliftByFilterParameters` validate the parameters (`percentage` is a `DecimalStr` that refuses a non-finite value) and `_validate_result` computes on the result, so input validation belongs first. Both functions now build the operation record before `_validate_result`. The reason is input-validation order (the maintainer, to-lead "2026-10-18 08:33:40 BST"); this also makes the plan's row claim, that a NaN percentage never reaches `_validate_result`, true.

## Census — every `Decimal(` call in the rate-table code

Pattern: `git grep -n "Decimal(" -- packages/pricing-core/src/pricing_core/rate_tables backend/src/app/platform/rate_tables.py` (backend: no hit).

| Site | Verdict |
|---|---|
| `operations.py:166` (`str(Decimal(str(float)))`) | Covered: `seed_from_model` validates the result via `_value_issue`. |
| `operations.py:316` | **The fix**: `is_finite()` before the bounds compares. |
| `operations.py:414` (`_index_rows`) | **The fix (hardening)**: named `ValueError`. |
| `operations.py:451`, `weights.py:219-220` | Out of scope: exposure weights, not rate-table input. |
| `operations.py:502,504,735,757,844` | Constants / arithmetic, not a parse. |
| `operations.py:696,763,835,842` | Stored values, validated at save; results re-validated by `_validate_result`. |

## Red → green

- Red, `0ac06deb` plus the merge, run-small on `packages/pricing-core/tests/test_rate_table_operations.py`: `24 failed, 36 passed in 4.93s`.
- Green, the code commit, same file: `60 passed in 1.90s`. Also green: `test_rate_table_bulk_ops.py`, `test_rate_table_weights.py`, `test_demo_b4_premium.py` (73 passed) and `test_rating_compile_bundle.py`, `test_rating_runtime.py`, `test_rating_lookup_as_at.py` (67 passed).
- DB-backed rate-table tests (`backend/tests/test_rate_tables_service.py`, `test_api_rate_tables.py`) not run: no backend code changed; owed to the gate.

## Tasks

- Task 1 (commit `0ac06deb`): FR-234 amendment and class `TestEveryValueIsAFiniteDecimal` (24 red, the bounds pin green).
- Task 2 (commit 2): `_non_finite_message`, the `is_finite()` check in `_value_issue` before the bounds, the named `ValueError` in `_index_rows`, the operation record built before `_validate_result` in the two uplift functions.

## PRs

None opened by the executor; the lead opens the PR after the gate.

## Audit

*(Written by `auditor-8108`, 2026-10-18, on head `0ec839b64f92e5500300eb85f4333a1c37ae0f45` (tree `f596c00759d553535c927ae65a9de61450a3539d`), range `4a53f194...0ec839b6` (the slice's own change; `4a53f194` is an ancestor of `origin/main`). Code read-only; no test, docs check or DB run by the auditor; the gate is the lead's.)*

**1. Change set** (`git diff --stat 4a53f194...0ec839b6`, 7 paths, +534 -9): `operations.py` (37 lines changed), `test_rate_table_operations.py` (+128), `03-rating-engine.md` (FR-234 row), `roadmap.md` (SL-1810 row), `INDEX.md`, PL-1809, this ledger. Commits: `0ac06deb` (commit 1: FR-234 amendment + red-first tests), `06c0ec31` (commit 2: code), `0ec839b6` (ledger/plan note); merges `c373df27`, `e5e8cca2`. `git merge-base --is-ancestor` rc 0 for `0ac06deb`, `06c0ec31`, `e5e8cca2` against `0ec839b6`.

**2. Obligations, derived from PL-1809's Acceptance Standard and the rulings (to-lead 2026-10-17 22:51:59, 22:56:37; 2026-10-18 04:37:16, 08:33:40) first, then evidenced:**
- **Spec first (Acc. 1, ruling 22:56:37).** FR-234 (`03-rating-engine.md:127`) carries the dated amendment (rule, issue text, "A non-finite value is never compared with a bound", the four save paths). The wording matches PL-1809's hunk; the only deviation is the date, 2026-10-18 against 2026-10-17, which the plan allows ("the build's date"). **Met.**
- **Finite check at the parse point, before the bounds (Acc. 3, constraint 3).** `operations.py:316` parses; `:319-323` returns `OUT_OF_BOUNDS` for `not decimal_value.is_finite()` via `_non_finite_message` (`:290`); the `min`/`max` compares follow at `:325`/`:331`. A NaN is never compared. The unparseable branch (`:311`-`:314`) is unchanged. **Met.** `_value_issue` is the one parse every save path runs: `validate_rate_table` (import `_checked_import`), `seed_from_model`, `_validate_result` (bulk) and `apply_cell_edits`.
- **Diff path (`_index_rows`, `:414`, DP-1 (a)).** Same predicate and message, raised `ValueError("OUT_OF_BOUNDS: …")`. The backend diff routes still do not catch it (DP-1 (a) accepts that; a legacy non-finite row would still answer 500, now with a named cause). **Met as planned.**
- **Census of `Decimal(` sites (the parse-site census, LG table).** `git grep -n 'Decimal(' 0ec839b6 -- packages/pricing-core/src/pricing_core/rate_tables backend/src/app/platform/rate_tables.py` returns 15 hits (`operations.py` 166, 316, 414, 451, 502, 504, 696, 735, 757, 763, 835, 842, 844; `weights.py` 219, 220; backend none). Each is in the ledger table with the same verdict I reach on reading: 166 reaches 316 through `seed_from_model`; 696/763/835/842 read stored values validated at save, results re-validated; 451/`weights.py` are exposure weights; the rest are constants. No unlisted parse path. **Met.**
- **Operation record before `_validate_result` (ruling 08:33:40).** `uplift_table` and `uplift_by_filter`: `_validate_result` moved after the operation record is built (diff hunks at old `:714`, `:749`). Both functions otherwise unchanged; `UpliftTableParameters.percentage` is `DecimalStr`, so a NaN percentage is refused by the record's schema before any computation. The pin test asserts `ValueError` matching `finite number`. `floor_cap` and `rebase_to_level` do not build a record before validating and were not changed; their inputs are `DecimalStr`/stored values (PL-1809's table). **Met.**
- **Tests, read not named (Acc. 3).** `TestEveryValueIsAFiniteDecimal` (`test_rate_table_operations.py`, +128): (a) 6 strings x 3 columns, each asserts `len(issues)==1`, `code=="OUT_OF_BOUNDS"`, `field=="relativity"`, `message.endswith("is not a finite decimal number")`; (b) NaN with bounds asserts `["OUT_OF_BOUNDS"]` and the call returns; (c) seeding `inf`/`nan` asserts `ValueError` `^OUT_OF_BOUNDS:`; (d) manual edit NaN asserts `["OUT_OF_BOUNDS"]` and `cells == ()`; (e) import `Infinity` asserts `^OUT_OF_BOUNDS:`; (f) pin as ruled; (g) diff over a NaN cell asserts `^OUT_OF_BOUNDS:.*not a finite decimal number`; (h) `"abc"` keeps `is not a decimal number`; plus a bounds test (`RateTableValue` min/max refuse inf/nan/`1e999`, closing PL-1809's "not verified" JSON-number question). All carry `@pytest.mark.req("FR-234")` through the class. **Met.** Limit: (d) and (e) assert the code/prefix only, not the message text.
- **Red, then green (Acc. 2, 4).** Ledger: red `24 failed, 36 passed` at `0ac06deb` + merge; green `60 passed` on the one file. 18 + 1 + 2 + 1 + 1 + 1 = 24 matches the count of the non-pin cases in the test file (the pin, the bounds test and the unparseable test are green by design). Not re-run by the auditor.
- **Gate (Acc. 7), read from the logs, not re-run.** `gate.log` (`sl8108-gate/`) START head `0ec839b6…`, tree `f596c007…`, END 2026-10-18T09:01:09Z; `pytest.log` `13 failed, 6246 passed, 9 skipped`; frontend 6/6 rc 0. The 13 FAILED lines are the known cascade per the lead's ruling 11:29:02 ("only-new 0"); the auditor did not re-derive the baseline. The paired demo capped (not evidence). The SOLO series (`demo-series/sl8108/`): START head and tree identical, `journey done in 1206s`, D1-D8 ok, D7 `sum +489842011 (reference +489842011)`, END 2026-10-18T10:28:19Z, zeros 0/0/0, keycloak bind under tools-main. The verdict that the gate is green is the lead's/maintainer's (ruling 11:29:02).
- **Backend mapping, read not run.** `rate_tables.py:119` maps `OUT_OF_BOUNDS` to `RATE_TABLE_INCOMPLETE`; `ValueError` is caught at the import, seed and bulk call sites (`:175`, `:190`, `:908`, `:939`, `:1567`). FR-234's guarantee, a named refusal on every save path and no NaN against a bound, holds in `pricing-core`; the route-level 422 for the new message rests on the existing mapping and was not exercised by a backend test in this slice (the ledger says the DB tests were owed to the gate, which passed with no new failure per the lead).

**3. Working-id cites to re-point at the mint** (`git grep -n -E 'FD 810[56]|PL 8107|SL 8108|LG 8109' 0ec839b6 -- .`, 33 line hits in 7 files). FD 8106 is FD 1803 and FD 8105 is FD 1802 on `origin/main` (`docs/findings/` files 01803 and 01802; `register.md:400-401`).
- **LIVE (re-point):** `docs/roadmap.md:2837, 2842, 2853, 2855` (SL 8108 row: FD 8106, PL 8107); `docs/specs/03-rating-engine.md:127` (the FR-234 amendment: "SL 8108, FD 8106"); `packages/pricing-core/tests/test_rate_table_operations.py:522` ("FD 8106, SL 8108") and `:592` ("PL 8107"); `LG 8109 file:19` (the working-id note) and `:27` ("PL 8107's"); `PL 8107 file:21, 24, 28, 29` (header prose naming SL 8108, LG 8109, PL 8107, FD 8106) and the body prose at `:85, :130, :134, :138, :204, :230, :273, :277, :282, :292, :296`. The plan is frozen from its first merge: re-point only if the mint ruling allows editing it, otherwise leave it as the plan's own record (the lead's call).
- **Generated:** `docs/INDEX.md:252` (FR-234 row) and `:1965` (SL row), regenerated by `doc-index.py` after the re-point.
- **QUOTED / frozen, do not re-point:** `PL 8107 file:35` (the 22:51:59 entry title "FD 8106 → HIGH"), `:58-59` ("FD 8105 widened…", the 22:56:37 entry title), `:63`, `:67`, `:96` (the amendment text quoted verbatim, whose live twin is `03:127`); `docs/ledgers/LG-01786-…:106` (SL-1547's ledger, a frozen record quoting "FD 8106 (reserved…)"). The plan lines `:35`, `:58-59`, `:96` are quotations of entry titles or of the spec hunk and are not touched.
- **Not in the brief's pattern but worth the mint's own grep:** `SL 8099`, `FD 8103` and `SL-1543` mentions in PL 8107 (`:282` and elsewhere) are other families' ids.

**4. Requirements without evidence, four verdicts:**
- *FR-234, the finiteness clause:* delivered and tested (code `operations.py:316-323`, `:414-417`; tests above; red/green recorded; gate accepted by ruling 11:29:02).
- *PL-1809 Acceptance 5 (census output line `0 non-finite` copied into this ledger at build):* **delivered but not recorded here.** The plan's census (`18 files 3552 value cells 0 non-finite`) exists in PL-1809; the build-base re-run is not in this ledger. Owner: the lead's mint edit (add the line) or the executor.
- *Backend route-level test of the new message on the import/seed/bulk 422:* **deferred, owner the lead / the next backend slice** (existing `test_rate_tables_service.py` / `test_api_rate_tables.py` ran in the gate; none asserts the new text); not required by PL-1809 Acceptance 3.
- *Live-database census of stored rate tables (PL-1809, DB lane):* **deferred, owner the lead** (a DB-lane action; a hit would be a STOP and a finding under DP-1).

**5. Findings.**
- **A1 (LOW):** this ledger's red/green record is thinner than PL-1809 Acceptance 2 asks: no FAILED lines verbatim, no tree for the red run, commit 2's sha `06c0ec31` unnamed, and the "Base" paragraph still says commit 2 "follows". The Acceptance 5 census line is also absent. Fix at the lead's mint edit; recorded here.
- **A2 (LOW):** tests (d) and (e) assert code/prefix only; the message text is pinned only through (a), (g), (h). Acceptable: one predicate and one message helper serve all paths.
- **A3 (observation, DP-1):** a diff over a legacy stored non-finite value answers 500 with a named cause in the log; no committed table holds one (PL-1809 census 0 of 3552). Unchanged by this slice, by design.
- **A4 (observation):** the amendment is dated 2026-10-18 while PL-1809's hunk says 2026-10-17; permitted by the plan. The mint should keep the spec date as written.
- No HIGH or MEDIUM finding. The `uplift` reorder is covered by the ruling 08:33:40 and by the pin.

**6. Proposed verdict:** all obligations delivered and evidenced, two items (Acceptance 5 census line; route-level message test) carried with owners; A1-A4 LOW or observation. Proposal only; the lead adopts, amends or rejects. MERGE-ACK: not yet given. This ledger is not closed by the auditor.
