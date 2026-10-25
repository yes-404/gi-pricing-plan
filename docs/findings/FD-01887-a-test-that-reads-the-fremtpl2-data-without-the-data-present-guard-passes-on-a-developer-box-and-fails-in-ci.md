---
id: FD-1887
family: finding
title: A test that reads the freMTPL2 data without the data-present guard passes on a developer box and fails in CI
status: active
created: 2026-10-25   # drafted 2026-10-23 under working id 8194; minted 2026-10-25 as FD-1887
owner: auditor
tree: ff976406f1bf133cfe040d2c44d383011503988a
corrected_by: []
relates: [WK-1178, SL-1888, LG-1889, SL-1711]
---

# FD-1887 — A test that reads the freMTPL2 data without the data-present guard passes on a developer box and fails in CI

## Finding

**LOW-MEDIUM; owner WK-1178. A test-environment defect; no product code is wrong and no price is affected.** Authority: the
maintainer's entry "2026-10-22 18:19:23 BST — Maintainer: #1361 CI red (2 freMTPL2 tests without the data guard): the fix plan
ACCEPTED; a STATIC guard as an FD" (`to-lead.md`): "The process note becomes an FD (working id, LOW-MEDIUM, owner WK-1178)."
Filed under working id 8194.

`examples/fremtpl2/data` is fetched (sha256-pinned) and gitignored, so CI never has it. A test that reads it with no
data-present guard passes where the data was fetched and raises `FileNotFoundError` in CI. #1361 (SL-1711, WK-674) added two such
tests; CI at its head `0a6cd6c9` ran python "2 failed, 6679 passed" (the entry above).

## Evidence

- **The two tests:** `backend/tests/test_wf701_journey.py::test_wf701_journey_runs_end_to_end` and
  `::test_c7_fails_naming_the_band_when_the_sample_rate_is_zero`, both `FileNotFoundError` on
  `examples/fremtpl2/data/freMTPL2freq.arff` (the entry above).
- **Why a grep did not see it:** the test file names no path and no reader. The read is three calls away:
  `_run_in_process` → `_full_level_world` → `journey_wf701.portfolio_policies` → `seed.build_csv` → `to_csv(DATA_DIR/…)`
  (LG-1889, Enumeration).
- **The existing guard form:** an `if <path>.exists()`-then-`pytest.skip` (`packages/pricing-core/tests/test_glm_scalar_predict.py`),
  or a redirect of `DATA_DIR` to synthetic files (`examples/fremtpl2/test_seed.py`). LG-1889 enumerates six files that reach the
  data at `origin/main` `71e481fa`; five were already safe or needed none, one (#1361's) was the failure.
- **Not stated by the entry or the LG:** the CI run ids of #1361's red run. LG-1889 does not name them and the PR body draft carries
  the placeholder `<run id>`; none is invented here.
- **Impact bound:** CI-only. The same two tests are the WF-701 journey evidence of record; the maintainer's condition on the fix
  is that CI skips them for want of data and the evidence of record is the local gate and the compose SOLO (both logged).

## Severity

LOW-MEDIUM, as ruled. The auditor's reading: product impact is none (no mispricing, no data loss); the cost is a red CI on a
merge candidate and a class of defect (a data-dependent test with no guard) that recurs wherever a new test reaches the
example's data through a helper. The rating is the maintainer's; the auditor does not lower it.

## Remedy

SL-1888 / LG-1889, branch `fix/fd-8194-fremtpl2-data-guard`: `tests/test_fremtpl2_data_guard.py`, a static, DB-free AST check that
every test reaching the data carries a guard, red-first by an injected unguarded test. Its slice audit is RS-1890 (working id).
The guard's stated and found limits are in RS-1890, Checks 2 and 3.

**Second step: hardening owed before the P2 close, owner WK-1178.** The maintainer (by delegation), `to-lead.md`
"2026-10-23 12:02:21 BST" (2): H1 and H2 go into this essay "as its remedy's second step — 'hardening owed before the P2 close,
owner WK-1178' — in the fold at its mint; no new id". RS-1890 (working id), line 55, states them: "**H1 (optional hardening,
the lead's call).** Recognise lowercase `fremtpl2` in a join, a `Path(...)` call and `os.path.join` inside a function, and follow
`from … import x as y`; both are a few lines in `_names_the_data_path` and `_loaded`. **H2:** require the guard's `.exists()`
expression to name the data (`DATA_DIR`, `ARFF`, a `fremtpl2` or `.arff` string, or an alias found in Reach) so an unrelated skip
no longer passes." LG-1889 (working id), line 124, states the same: H1 (recognise lowercase `fremtpl2` in a join, `Path(…)` and
`os.path.join` inside a function; follow `import … as`) and H2 (require the guard's `.exists()` expression to name the data).
Both are owed, by WK-1178, before the P2 close.

## Disposition

Open, owner WK-1178; **fix before close**: SL-1888 (LG-1889). Closed in place citing the PR when that slice merges.
Filed under working id 8194.
