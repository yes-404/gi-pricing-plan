---
id: LG-8341
family: ledger
title: WK-1178 slice SL-8340 — DecimalStr serialises positionally (PL-8339, FD-1337)
status: active
created: 2026-11-05
owner: executor
tree: 9632320c797cabe58d5907700e83f091700d1a5d
phase: P2
work: WK-1178
slice: SL-8340
plans: [PL-8339]
corrected_by: []
relates: [FD-1337, PL-8339, RL-1329, RL-1343, FR-10, FR-21]
---

# LG-8341 — WK-1178 slice SL-8340: `DecimalStr` serialises positionally

**GO:** to-lead "2026-11-05 15:55:35 GMT"; DP-L1 to DP-L3 ruled "2026-11-05 10:36:35 GMT"; brief `brief-exec-sl8340-2026-11-05.md` (sha256 prefix 0577549ad10b).
**MERGE-ACK:** (added at merge)

## Tasks

### R0 — premises and spec (`614a7c2a`)

Base `ddec34fe`, merged by sha: C `4abb3798`, R1 `662867bb` (INDEX.md: theirs, regenerated). Reach re-run at the merged tree: `git grep -n -E ':\s*(tuple\[|list\[)?(DecimalStr|Relativity)\b' HEAD -- packages/model-schema/src ':!packages/model-schema/src/model_schema/money.py'` = **29 lines** (the plan's figure, unchanged by C and R1). Hash sites read: `suite_content_hash` (`regression.py:220`, reached by `MonotoneInInput.lower/upper`); `bundle_hash` (`compile.py:676`, hashes `JdmGraph` + `Pins`, neither holds a `DecimalStr`); `spec_hash` (`modelling.py:161`, none); `version_content_hash`/`definition_hash` (`diff_cache.py`, cells and keys); `canonical_payload` (`audit.py:116`, hashes the JSON a writer passes: A5's audit-writer sweep is owed in the window). FR-21 gained a dated clause (`docs/specs/00-overview.md`).

### R2 — red first (`9632320c`)

`packages/model-schema/tests/test_money.py`, `uv run --directory <wt> pytest -q packages/model-schema/tests/test_money.py` at `9632320c`: **9 failed, 25 passed**.
- T1 (8 cases: `DecimalStr` and `Relativity` x `1E-7`, `1.2E-28`, `1E+2` twice): `AssertionError: 1E-7` — `re.fullmatch('^-?[0-9]+(\.[0-9]+)?$', '1E-7')` is `None`.
- T2: `AssertionError` over three hashes for `10`, `1E+1`, `10.0` (`sha256:028228ef…`, `sha256:19a11329…`, `sha256:a50acf09…`).
- T3 control: green (`66000.440` kept).

### R3 — green (drafted, uncommitted until the window)

Patch `~/gi-pricing-plan.local/scratch/sl-8340-decimalstr-positional/code.patch` sha256 `10615855409b657995ef72e2039d7dbef72c95d290356632a8b9589f7f9679df`, 3 files; `test_money.py` 34 passed, `ruff check packages/model-schema` clean on the drafted tree. Noted: `Decimal("-0").normalize()` formats `-0` (pattern admits it); `-0` and `0` would still hash apart.

## Re-measure (A3 to A5)

(window result added after the lead's grant)
