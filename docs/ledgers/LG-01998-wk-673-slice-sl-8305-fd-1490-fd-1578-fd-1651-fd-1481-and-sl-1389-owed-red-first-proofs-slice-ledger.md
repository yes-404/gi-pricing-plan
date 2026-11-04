---
id: LG-1998
family: ledger
title: WK-673 slice SL-1997 — FD-1490, FD-1578, FD-1651's two proofs, FD-1481 and SL-1389's five owed red-first proofs (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-04   # drafted 2026-11-04 under working id 8306; minted as LG-1998
owner: executor
tree: a2679afe9e835d6c4d8027e60ed9a2420baeb5ed   # origin/draft/pl-wk673fix at the branch cut (origin/main a8ef6f19 an ancestor)
slice: SL-1997
phase: P2
work: WK-673
plans: [PL-1984]
corrected_by: []
relates: [FD-1490, FD-1578, FD-1651, FD-1481, PL-1984]
---

# LG-1998 — WK-673 slice SL-1997: the S-b remediation row

**GO:** to-lead "2026-11-03 16:28:44 GMT" (Maintainer: GO for PL 8302, minted as PL-1984): *"S-b = SL-1997 / LG-1998: FD-1490 (drop errors.py:323), FD-1578 (input-free AttributionError + CodedError), FD-1651's two proofs, candidate 1 (SL-1389's five proofs), FD-1481; full SOLO gate; merge by Mon 9."*
**Correction recorded (lead, 2026-11-03):** PL-1984 Acceptance 9 and 10 say the item-13 OK for the assert changes was *given at the GO*. The 16:28:44 entry does not name it. The lead gave it afterwards, under seat-brief item 13: Acceptance 9's leak asserts and Acceptance 10's raise text, each asserting the NFR-499 defect it now stops asserting. It was then extended to all four leak asserts (below).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-1984 "Row 2 — S-b (the rest)", Acceptance 7–13 (14–17 are gates). Write set as the row names it; no other file besides this ledger and the regenerated `docs/INDEX.md`. Requirements touched: FR-227 (item 7), FR-1397 and NFR-499 (items 8–10), FR-212 (item 13), FR-224 and FR-257 (the proofs, no code).

**Plan defect found:** Acceptance 9 names two leak asserts "at `:631` and `:648`". The tree has **four**, at `test_rating_attribution.py:632`, `:649`, `:662` and `:884` (the plan's two are off by one line). The lead extended the OK to all four.

**Grants used:** the lead's item-13 OK (above); to-lead "2026-11-03 17:19:47 GMT" (DB-free single-file runs, ENDED by the third load breach: runs began at load1 3.07, 3.35 and 3.98 against its "< 3"); the DB window opened by the lead at 05:12Z on 2026-11-04.

### Task list

- T0 re-read: the row's sites matched (`errors.py:323` = `"MONETARY_FLOAT_REFUSED",`; `analysis.py:521` `class AttributionError(ValueError)`; `:1003-1012` `_reconcile`; `:1129-1133` the subset raise; `test_dislocation_runs.py:470-476`; `test_worker_raise_sites.py:206-219`). Quoted: `git grep -n -E 'AttributionError|quoted in the baseline' -- backend packages scripts` at `a2679afe` printed 39 lines: raises in `analysis.py` (:597, :612, :797, :956, :1003, :1009, :1106, :1129), catches in `backend/src/app/platform/dislocation_runs.py:295` and `worker/dislocation_handlers.py:319`, and the tests named in the write set plus ten `pytest.raises(AttributionError)` in `test_rating_attribution.py`.
- T1/T2 FD-1490 (Acceptance 7): red `badd36b0`, fix `d55031ab`.
- T1/T2 FD-1578 (Acceptance 8–10): red `daa4ae6e` (reordered by `5c9b58f6`), fix `0cb69a0c` (messages, then `CodedError`, in that order), reason strings `00fc807c`, the four leak-assert inversions `518349ae`, the stubbed raise text `c48c5eb1`.
- T3 FD-1481 (Acceptance 13): pin `26924345`.
- T4 DB window (Acceptance 10's backend runs, 11, 12): below; docstrings `8347298d`.

### Gate

Owed: the full SOLO gate, both halves, in the slot the lead grants for the final head. Local: `ruff check` rc=0 and `mypy` rc=0 ("Success: no issues found in 251 source files", at `0cb69a0c`); `ruff check` rc=0 on each later touched file.

#**Verdict line, 2026-11-04 07:45:28 GMT (executor, at the mint; the audit is the auditor's):** the SOLO gate at `07e62951` (on `bb9781a9`, the item-21 merge re-test) STANDS under item 31 — from-lead "2026-11-04 07:38:28 GMT" (pytest "13 failed, 7047 passed, 22 skipped, 5 xfailed" = the 13 FAILED lines in exactly the eight item-31 files; frontend all rc 0, vitest 919 of 919; demo designed stop 1587 s, dislocation #1 592 s) and to-lead "2026-11-04 07:39:25 GMT", which accepts it and rules (a) on PL 8302: it duplicated main's PL-1984 (8 lines, id tokens and the created line), so this mint `git rm`s it and re-points its citations. Merge 54 (`824a891d`, `data/expressions.py` and its two tests) does not overlap the slice's eight non-docs files, so the gate evidence carries. Minted as SL-1997 and LG-1998.

## Audit

(The auditor's.)

### Build log

All results: tree `sl-8305` worktree. Red = the base file restored with `git show a2679afe:<path>` over the worktree, run, restored with `git checkout --`, `git status --porcelain` read 0 after each.

**2026-11-03, DB-free runs** (17:19:47 grant; `run-small.sh`; conftest chain root `conftest.py` + `packages/pricing-core/tests/conftest.py`, no autouse fixture; grep `postgres|redis|database_url|asyncpg|psycopg|localhost|5432|6379` over them and the test files with their sibling imports: no hits, rc 1):
- `head=5c9b58f6…` `packages/pricing-core/tests/test_rating_attribution.py`: 46 passed. `rc=0`
- same file, `analysis.py` = a2679afe: 7 failed, 39 passed. `rc=1`. The four inverted asserts fail with e.g. `assert 'Q000' not in 'policy Q000...changes [c1]'`; the class test's three cases fail on `assert 'Q0' not in …` (text before type, so the red names the leak).
- `test_rating_wire_order.py`: 15 passed `rc=0`; scratch (expects the 17-digit input back): `assert 0.0848719951589216 == 0.08487199515892163`, 1 failed `rc=1`. No `runtime.py` change.
- `test_quote_input_raise_sites.py`: 19 passed `rc=0`.

**2026-11-04 DB window, 05:12:49Z–05:30:42Z** (own copy `gipricing_sl-8305_0066f6cb` by `createdb -T gipricing`, migrated to `b7e4c2a91d36` = the template's; redis db 12; load1 0.66 at start; END: redis db 12 dbsize 0, own-db count 0, datnames `postgres template1 template0 gipricing`):

| Item | Run (file at `head=5c9b58f6…` unless noted) | Result |
|---|---|---|
| 7 FD-1490 | `backend/tests/test_errors.py`, `errors.py` = a2679afe | 1 failed 15 passed `rc=1`: `AssertionError: assert 'MONETARY_FLOAT_REFUSED' not in frozenset({…})` |
| 7 | same, fix in place | 16 passed `rc=0` |
| 7 | `git grep -n MONETARY_FLOAT_REFUSED -- ':!docs'` | only `test_errors.py:176` and `:178` |
| 10 | `test_dislocation_runs.py` | 24 passed `rc=0` |
| 10 | `test_worker_raise_sites.py` | 3 passed `rc=0` |
| 11 FD-1651 | `test_rating_version_evidence_floor.py` baseline | 10 passed `rc=0` |
| 11 | scratch A (`verify is None` → `continue`) | `test_a_policy_naming_an_unverifiable_kind_is_refused_by_name`: `Failed: DID NOT RAISE PlatformError`; 1 failed 9 passed `rc=1` |
| 11 | scratch B (`rate_table_diffs` verifier returns `{}`) | `test_a_policy_naming_rate_table_diffs_is_refused_naming_the_kind`: `Failed: DID NOT RAISE PlatformError`; 1 failed 9 passed `rc=1` |
| 12 row 2 | `test_rating_version_dislocation_gate.py` baseline | 25 passed `rc=0` |
| 12 row 2 | limb (2) not called | 5 failed (`test_limb_2_*`): 4× `DID NOT RAISE PlatformError`, 1× `KeyError: 'dislocation_run_id'` `rc=1` |
| 12 row 5 | `_approximation_gate` not called | 7 failed (`test_fr224_*` and the empty-banded-set test): `DID NOT RAISE PlatformError`, `KeyError: 'approximation_check'` `rc=1` |
| 12 row 6 | threshold overridden from `GIP_APPROXIMATION_MAX_ABS_CHANGE_PCT` | `test_fr224_threshold_ignores_environment_variables`: `DID NOT RAISE PlatformError`; 1 failed `rc=1`. *Settings has no such field; the scratch reads the environment directly, which is what `load_settings()` would do.* |
| 12 row 15 | unset entry returns `None` (no gate) | `test_fr224_an_unset_threshold_is_governed_by_the_default`: `DID NOT RAISE PlatformError`; 1 failed `rc=1` |
| 12 row 19 | null observed read as 0 | `test_an_empty_banded_set_has_null_quantiles_and_fr224_refuses`: `DID NOT RAISE PlatformError`; 1 failed `rc=1` |
| final | `head=8347298d…`: dislocation_gate / evidence_floor / test_errors / dislocation_runs / worker_raise_sites | 25 / 10 / 16 / 24 / 3 passed, each `rc=0` |

**Leak asserts (item 9), before → after** (`test_rating_attribution.py`): `:632` `assert "Q0" in str(exc.value)` → `assert "Q0" not in str(exc.value)`; `:649`, `:662`, `:884` `assert "Q000" in str(exc.value)` → `assert "Q000" not in str(exc.value)`. Each now proves the refusal text names no quote id; the `"c1"` assert beside `:884` is unchanged. **Item 10:** the stubbed raise in `test_dislocation_runs.py` was `"policy Q000 is quoted in the baseline and the candidate but has no premium under the subset bundle for changes [c1]"`, now `"one policy of the book is quoted in the baseline and the candidate but has no premium under the subset bundle for changes [c1]"`.

**Deviations:** `cd /tmp` in the first command (no effect; the shell reset); three DB-free runs started above the grant's load1 limit (above); a backend run was never made under the 17:19:47 grant (the session-autouse truncation, `conftest_db.py:1632`).

## PRs

(None yet; the lead opens the PR after the gate.)
