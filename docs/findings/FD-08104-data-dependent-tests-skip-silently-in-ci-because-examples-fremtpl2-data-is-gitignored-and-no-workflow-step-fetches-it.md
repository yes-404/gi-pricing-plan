---
id: FD-8104
family: finding
title: Data-dependent tests skip silently in CI because examples/fremtpl2/data is gitignored and no workflow step fetches it
status: active
created: 2026-10-17
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, FD-8103]
---

# FD-8104 — Data-dependent tests skip silently in CI because examples/fremtpl2/data is gitignored and no workflow step fetches it

## Finding

**LOW; owner WK-1178; verdict deferred with an owner.** The maintainer's entry "2026-10-17
21:26:31 BST" (`to-lead.md`, the CI-caveat paragraph on SL 8099), which accepted a LOW FD in D21.
`examples/fremtpl2/data/` is gitignored and is filled only by `examples/fremtpl2/fetch.py`
(sha256-pinned) or by `scripts/demo.py`. A test that calls `pytest.skip` when the data is absent
therefore reports *skipped*, not *failed*, in PR CI, and its parity or golden limb never runs
there. Nothing mispriced; the cost is a check that reads as present and is not.

## Evidence

- **Ignored:** `.gitignore:61` is `examples/fremtpl2/data/`, read at docs-d21 @358c194e.
- **Not fetched in CI:** `grep -n "fremtpl2\|fetch.py" .github/workflows/*.yml` at `origin/main`
  9469721d returned no fetch step (the only `fetch` hits are `fetch-depth: 0`, in
  `history-policy.yml:60` and `python.yml:144`). `python.yml` path-filters on `examples/**`
  (`:21`, `:59`) and `pyproject.toml` lists `examples/fremtpl2` in `testpaths` (`:180`), so these
  tests are collected in PR CI and skip there.
- **Skip sites** found by `git grep -n -E "pytest\.skip|skipif|importorskip|pytest\.mark\.skip"
  <ref> -- examples backend/tests 'packages/*/tests' scripts`, filtered on `fremtpl|fetch|data is not|not fetched|arff|data/`:

  | Ref | Site | Skips on | Tests behind it |
  |---|---|---|---|
  | `origin/main` 9469721d | `examples/fremtpl2/test_seed.py:136`, inside fixture `scratch_seed` (`:120-121`) | `freMTPL2freq.arff` absent | at least `:168` `test_the_seed_reruns_against_a_seeded_database` and `:189` `test_a_small_seed_is_refused_for_its_degenerate_fit` take the fixture; the file's other tests were not traced |
  | `origin/pl-8098-glm-scalar-predict-2026-10-17` d0b2bad2 | the same `test_seed.py:136` | the same | the same |
  | `origin/pl-8098-glm-scalar-predict-2026-10-17` d0b2bad2 | `packages/pricing-core/tests/test_glm_scalar_predict.py:326-329` `_demo_modules` | `examples/fremtpl2/data/freMTPL2freq.arff` absent | its one caller is the module-scoped fixture `demo` (`:345-351`); tests naming it include `:398` `test_the_demo_goldens_score_bit_identically` and `:409` `test_every_seed_portfolio_row_scores_bit_identically` (the goldens and seed limb the maintainer's entry names) |
  | `origin/main` | `backend/tests/` (7 files mention `fremtpl2`) | none of them contains a skip call (a per-file count of skip calls returned 0) | not data-skipping at this tree |

  `test_glm_scalar_predict.py:437` also has a `pytest.skip`, on a Factor-shape refusal, which is
  not data-dependent and is not counted here.
- **Not covered by this list:** skips raised by a fixture in a `conftest.py`, or by an
  `exists()` check with a message that matches none of the filter words, would not appear in it.
  Database-unreachable skips (`backend/tests/conftest_db.py:190`, `:197`) are a different cause:
  CI provides the service.

## Standing mitigation (the maintainer's, SL 8099)

The gate runs with the data present and `pytest -rs`; the record must show no skip line for the
goldens and seed limb, quoted; the PR body states that CI runs only the synthetic limb.

## Options (none picked)

- **A pinned CI fetch:** a workflow step runs `examples/fremtpl2/fetch.py` (sha256-verified), with
  the 36 MB cached by checksum. Closes the gap; adds a network dependency to PR CI.
- **A required-data marker:** a test that needs the data carries a marker, and CI fails if one of
  them skips (`-rs` plus a check on the skip list). Keeps CI offline; does not run the tests.

## Disposition

Deferred with an owner: WK-1178. Decision on the option is the lead's or an RL's; this record
picks none. The event that next discharges it: a merged CI step or skip check, or a dated ruling
accepting the absence. Filed under working id 8104.
