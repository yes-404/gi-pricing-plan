---
id: LG-1990
family: ledger
title: WK-1250 Slice SL-1989 — FD-1768's fix, a purposes-only mount change is worded "mount purposes changed" (FR-1399)
status: active                 # active → closed (§1.2a)
created: 2026-11-03
owner: executor
tree: 5a9e47c5d72bb9e7e03438b93fbf269c8015322c   # origin/main at the re-merge
phase: P2
work: WK-1250
slice: SL-1989
plans: [PL-1991]
corrected_by: []
relates: [FD-1768, FR-1399, RL-1686, RL-1344]
---

(Minted 2026-11-04 from working id 8297, with SL-1989 from working id 8296 and PL-1991 from working id 8298, on the lead's mint order and the maintainer's GO "2026-11-03 17:30:53 GMT", with the mint tool of record `mint-repoint.py` (sha256 `4d83681a`); finding FD-1768; executed on branch `sl-8296-wk1250-fd1768-purposes-wording`.)

# LG-1990 — WK-1250 Slice SL-1989: a purposes-only mount change is worded "mount purposes changed"

**GO:** the maintainer's entry "2026-11-03 17:30:53 GMT — Maintainer: GO for PL 8298 / SL 8296 / LG 8297 (WK-1250, FD-1768) at origin/draft/pl-fd1768 5a48fa9e" in `to-lead.md`; DP-5 (a), DP-6 (a) and DP-7 (a) accepted in the entry "2026-11-03 16:13:02 GMT".
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1991`, "SL-1989 — FD-1768's fix: a purposes-only mount change is worded "mount ports
re-mapped"": R1 (red first, no database), R2 (green) and G (the gate). Requirement: FR-1399.
Write set: `analysis.py` mount loop, one test file, this ledger, FR-1399's dated amendment.
Open point of the brief: whether `rating.py:1093-1095` is in scope. Settled below by a test.

### Task list

- **T0 — re-read, no line moved.** At `origin/draft/pl-fd1768` 5a48fa9e merged with `origin/main`
  5a9e47c5 (merge commit 0fc28ace; only `docs/INDEX.md` conflicted, main's taken and regenerated,
  `doc-index.py --check` rc 0): `analysis.py:662-669` and `rating.py:1093-1095` read as `PL-1991`
  cites them; `RL-1686` descriptions and FR-1399's mount sentence as cited.
- **The `rating.py` verdict: `rating.py:1093-1095` verified correct at base by
  `test_mount_purposes_alone_is_one_structural_mount_change_with_before_equal_after`
  (`packages/pricing-core/tests/test_rating_attribution.py`), no change.** It asserts through
  `diff_algorithms` that a `purposes`-only change is one mount change, `before == after`,
  `ports_changed` false, `purposes_changed` true (`RL-1344` acceptance 5). It passed at base
  (44 passed, 1 failed in the red run; the one failure is the next task's). `rating.py` is not
  edited. An older test of the same behaviour is
  `packages/model-schema/tests/test_rating_algorithm.py:686`; it was not run (outside the brief).
- **T1 — reds, commit 7e2fdfa2.** `test_mount_purposes_changed_forms` (`req("FR-1399")`): three
  cases (purposes alone, DP-5; ports and purposes, DP-5; re-point and purposes, DP-6). Red by its
  cause: `AssertionError` on the description, actual
  `m_ncd: mount ports re-mapped (sub_graph:ncd-ladder@4)`, expected
  `m_ncd: mount purposes changed (sub_graph:ncd-ladder@4)`.
- **T2 — fix, commit 1063f39e.** The mount loop of `analysis.py` words the `before == after` branch
  by its flags (ports first, then `; purposes changed` when both) and the re-point branch adds
  `; purposes changed`. FR-1399's mount sentence names the fifth case and carries a dated
  amendment (DP-7 (a)). `test_mount_ports_re_mapped_forms` is not edited (the diff of the test
  file is added lines only).
- **GREEN set (item 29), by import closure.** Changed module:
  `git diff --name-only origin/main...HEAD -- packages/pricing-core/src` gives
  `pricing_core/rating/analysis.py`. Importers, level 1:
  `git grep -lE "pricing_core\.rating\.analysis|from pricing_core\.rating import .*analysis" -- '*.py'`
  gives `backend/src/app/api/dislocation_runs.py`, `backend/src/app/platform/dislocation_runs.py`,
  `backend/src/app/platform/rate_tables.py`, `backend/src/app/worker/dislocation_handlers.py`,
  `backend/tests/test_dislocation_runs.py`, `examples/fremtpl2/test_seed.py`,
  `packages/pricing-core/tests/test_fremtpl2_rate_fixture.py`,
  `packages/pricing-core/tests/test_rate_table_weights.py`,
  `packages/pricing-core/tests/test_rating_attribution.py`,
  `packages/pricing-core/tests/test_rating_dislocation.py`, `scripts/measure-attribution-cost.py`.
  Level 2 (importers of the backend modules, their test files) was not derived by this seat: those
  run in the slice's full gate. Run by this seat: `test_rating_attribution.py` only.

### Gate

Not the full gate (a separate seat, after the lead's slot grant). Checks run by this seat, tree
named in each log under `~/gi-pricing-plan.local/scratch/sl-8296/`:

| Check | Head | rc |
|---|---|---|
| `test_rating_attribution.py` (red, `red2.log`) | 7e2fdfa2 | 1 (1 failed, 44 passed) |
| `test_rating_attribution.py` (green, `green.log`) | 1063f39e (fix uncommitted at the run; the same tree as the commit) | 0 (45 passed) |
| `ruff check .` | 1063f39e | 0 |
| `mypy` | 1063f39e | 0 (251 source files) |
| `req-coverage.py` | 1063f39e | 0 |
| `doc-index.py --check` | after regeneration | 0 |
| `audit-docs.py` | 1063f39e | 1; the one failure is check 31 (gap before the working ids 8297, 8298, 8296), expected until the mint |

All pytest runs: `scripts/run-small.sh` under the gate-2 flock, conftest chain `conftest.py` (root)
and `packages/pricing-core/tests/conftest.py`, neither loads `backend/tests/conftest_db.py`;
`GIP_TEST_DATABASE_URL` and `GIP_TEST_APP_DATABASE_URL` set to
`postgresql+asyncpg://nobody:nobody@127.0.0.1:1/none`; load1 below 3 at each start; grant:
`to-lead` "2026-11-03 17:19:47 GMT".

### Audit

Written by the auditor.

### Build log

- 2026-11-03: branch cut from `origin/draft/pl-fd1768` 5a48fa9e, re-merged `origin/main` 5a9e47c5
  (0fc28ace); reds 7e2fdfa2; fix 1063f39e.

## PRs

None yet.

## 2026-11-04 — the verdict at the mint

Verdict from the gate evidence: the full gate at `322b20ec` (window 2026-11-03 23:08:40 to END 2026-11-04 01:08:27 GMT): python half 13 failed, exactly the eight docs-audit test files of the common seat brief's item 31, with skipped 22 = baseline and audit-docs failing only check 31 on this slice's own working ids; frontend lint, type-check, test and build all rc 0, vitest 905 of 905; demo stopped by design at 1999 s, dislocation #1 586 s. The item-31 class stands for the code on the conditions of that item, which this mint's checks discharge (see the minted-head rows of the report). Mint 2026-11-04: SL-1989, LG-1990 and PL-1991 (working ids 8296, 8297, 8298); FD-1768 closed in place.

## 2026-11-04 — process line: the push before the push grant

The branch was pushed at 01:28:19 GMT (origin reflog) to `38d19a47`, before the maintainer's push grant. Cause: the lead's mint brief, step 6, over-granted against the 01:10:01 grant, which reserved the push. Effect: the branch only moved; no CI ran, no PR was opened, main was untouched. The INDEX regeneration at load1 4.6, outside the gate-2 flock, was the mint seat's breach of the 01:10:01 grant. The lead's rule is adopted: a mint brief ends unpushed when a grant reserves the push. No FD (nothing wrong got through). Source: to-lead 2026-11-04 01:30:18 GMT.
