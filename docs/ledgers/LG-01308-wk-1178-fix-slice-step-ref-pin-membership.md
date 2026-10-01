---
id: LG-1308
family: ledger
title: WK-1178 fix slice (SL-1300) — compile_bundle refuses a step ref not pinned at its exact version (FR-237)
status: closed
created: 2026-09-30
owner: executor
tree: f965b4174d4d2d8676deccfec3c691f3dacb6305
phase: P2
work: WK-1178
plans: [PL-1299]
corrected_by: []
relates: [FD-1297, RL-1298, RL-1263]
---

# LG-1308 — WK-1178 fix slice (SL-1300): step-ref pin membership (FR-237)

Executed from `PL-1299` (SL-1300) under `RL-1298`, on lane B (`RL-1263`). Branch
`sl-1300-pin-membership`, from `origin/main` `22fe674b4a590c47095c6ba608fe974264581139`
(`git rev-parse origin/main` at the rebase). Drafted under working id 9941 (given by the lead) and minted `LG-1308` at its merge turn,
after #981 (LG-1304) and batch 2 (RL-1305, PL-1306, RL-1307). Numbers in the entries below are
as measured at the heads they name.

## Task 0 — preconditions

- Tree: `git rev-parse HEAD^{tree}` at `f965b417` prints
  `4846f08639ddbb0ba58883d70227eec5a40ddebe`. `uv sync --all-packages` rc 0. A per-worktree
  test database was created (`createdb -T`) and `alembic upgrade head` rc 0.
- **Premises a–q** were re-read at `bf790e22`, with `git diff --stat 04b34558 HEAD -- packages
  backend frontend` empty, so no code moved since the plan's tree. Line-checked: `compile.py`
  :421-422, :434-443, :464-491; `runtime.py` :50, :533, :579; `errors.py` :298, :325;
  `test_rating_version_compile.py` :85, :181; `test_safe_error.py` :28; `03` :772-776;
  `git grep -n RATING_VERSION_UNPINNED -- docs/specs` prints only `03:774`. All hold.
  Premises d, e, k, m (model_schema and fixture lines) were covered by the empty diff, not
  re-read. After the rebase onto `22fe674b` only docs moved. None failed.
- **DP resolutions:** DP-F1 (a), DP-F2 (c) with the handler limb dropped, DP-F3 (a), all
  `RL-1298`.
- **Names the new file imports** from `backend/tests/test_rating_version_compile.py`
  (dispatch condition 1b): `_handlers` (:44, autouse), `_headers` (:74), `_empty_pins` (:81),
  `_insert_version` (:85), `_run_compile_job` (:112), `_minimal_algorithm` (:49).

## Baseline (origin/main `bf790e22`, Python half)

`uv run pytest -q`: **3881 passed, 3 skipped, 0 failed**. 12:02:07 to 12:27:04 UTC, wall
1497s (pytest 1469.58s). Load at the start 2.17/1.17/1.68, at the end 3.00/2.29/2.12. Caps
LOKY=4, OMP=2, OPENBLAS=2 (the pre-correction form). Run under `flock` on gate-1 without
`GIP_GATE_SLOT`, so the root `conftest.py` hook also took gate-2. Classified **solo** by the
lead from `/proc/locks` at 12:23 UTC (the other executor's flock was waiting, never granted).

## Red first

Tests: `packages/pricing-core/tests/test_rating_pin_membership.py` (26 cases), commit `139d8e13`.
At that commit, 16 failed and 10 passed, for the predicted causes:

| Group | Result | Cause |
|---|---|---|
| 7 refusals (table, lookup, model by `model_ref`, peril by `peril_structure_ref`; absent and wrong-version) | 7 failed | `DID NOT RAISE CodedError` |
| 3 tolerant-consumer refusals | 3 failed | `DID NOT RAISE CodedError` |
| 2 auditor-933 refusals | 2 failed | `DID NOT RAISE CodedError` |
| GBM and GLM at `runtime.py:533` | 2 failed | `KeyError: 'model:motor-freq@1'`, `KeyError: 'model:motor-freq-glm@1'` |
| 5a, two hand-built pre-fix bundles | 2 failed | `DID NOT RAISE CodedError` (`load_bundle` returned) |
| Controls (1507, 2740, 1507 with an extra pin, lookup 1507 and 2740, 130000 x2, 180000 x2), the 5a control | 10 passed before any change | as required |

**Pre-fix prices**, from scratch runs at the pre-change tree, never committed: table unpinned
**1370**; lookup unpinned **1370**; lookup step `@1` with only `@2` pinned **1370**;
auditor-933 lookup and table unpinned **100000** each. Acceptance 5a's hand-built `Bundle`
through `load_bundle` then `score_one`: control **1507**, unpinned **1370**, step `@1` with
`@2` pinned **1370**. Each matches FD-1297.

**NFR-499 guard** (`test_every_quote_input_raise_site_has_a_sentinel_case`): removing the
`check_step_refs_pinned` entry gave the assert "a `_raise_named` site is not accounted for"
(`Found {... ('rating/compile.py', 'check_step_refs_pinned'): 1 ...}`). The entry is added in
the same commit as the site, and `("rating/runtime.py", "_load_boosters"): 1` likewise
(commit `5d677ef3`). `("rating/runtime.py", "handler")` stays 2 and `compile_bundle` stays 5.

**Platform** (acceptance 6): with `check_step_refs_pinned` temporarily commented out of
`compile_bundle`, the new test failed with `assert JobStatus.SUCCEEDED is JobStatus.FAILED`,
the predicted red. Restored; nothing from that edit was committed.

**Condition 8a** (`_handlers` is autouse): with its import removed from
`backend/tests/test_rating_pin_membership_api.py`, `test_the_autouse_handler_registration_fixture_applies_to_this_module`
failed (`assert '_handlers' in ['event_loop_policy', '_empty_the_database_after_the_session',
'_isolate_probes', 'request']`) and the compile test failed with `'JOB_HANDLER_NOT_REGISTERED'
== 'RATING_VERSION_UNPINNED'` (2 failed). With the import restored, 2 passed.

## Tasks

Commits are `git log --oneline origin/main..HEAD` before this ledger. Task 0 above; Task 1 `139d8e13`; Task 2 `171fd0f9`; Task 3 `5d677ef3`; Task 4 `aa37a024` and
`f965b417`; Task 5 is this ledger and the gate below.

- `139d8e13` test(rating): FR-237 pin-membership refusals, red
- `171fd0f9` fix(rating): compile_bundle refuses a step ref not pinned at its exact version;
  `03` §5.1 gains the dated meaning line in the same commit
- `5d677ef3` fix(rating): load_bundle re-checks step pins and codes the missing model payload
- `aa37a024` test(rating): a step ref the pins do not carry fails its compile Job
- `f965b417` test(rating): prove the autouse handler fixture applies (8a)

## Acceptance

1. Spec first, same commit as the refusal (`171fd0f9`); FR-237 is not reworded.
   `python3 scripts/audit-docs.py` exits 0 at `f965b417`.
2-5a. Green after Tasks 2-3 (see the gate).
6. Through the platform, in a new file (dispatch condition 1b, a deviation made by the dispatch
   record, accepted by the maintainer at 12:36:02 BST): `backend/tests/test_rating_pin_membership_api.py`.
   `test_rating_version_compile.py` is not edited.
7. Existing fixtures: **none newly refused, no fixture corrected** (the full suite is green,
   below). One guard test changes by design (NFR-499, above).
8. `git diff origin/main...HEAD -- packages/pricing-core/src/pricing_core/rating/compile.py`
   touches neither `_GUARD_MARKERS` nor `_check_vocabulary`, nor any expression handling.
9. **Reusable function:** `check_step_refs_pinned(algorithm: RatingAlgorithm, pins: Pins) -> None`
   in `packages/pricing-core/src/pricing_core/rating/compile.py`, exported in `__all__`;
   raises `CodedError` `RATING_VERSION_UNPINNED: step '<id>' names <ref> …`. WK-1250 Slice 2's
   G1 calls it over the inlined algorithm. `runtime.py` imports it for `load_bundle`.
10. `uv run python scripts/req-coverage.py` lists FR-237 with 13 test files.

## Gate

Head `f965b417`. The dev-commands slot wrapper (`SKILL.md` lines 123-170, verbatim) with
`LOKY_MAX_CPU_COUNT=4` exported. Started 12:36:34 UTC, ended 13:01:22 UTC, **wall 1488s**.
Uptime at the start: load 4.32/5.09/3.73. At the end: load 5.55/6.02/4.72. At 12:36:31 gate-1
was busy and gate-2 free; at the end gate-1 was still busy and gate-2 free, so this run held
gate-2 and the other holder was on gate-1 (corrected at the mint: most likely #981's gate, executor-690s1, from 12:36 to 12:57 UTC, not lane A; I did
not read its process). pytest: **3909 passed, 3 skipped, 0 failed**, 1471.00s (the baseline was
3881 passed, +28 = the 26 new pricing-core cases and 2 new backend cases). This is RL-1263 contention pair 1 of 3, the
overlap figure against the solo 1497s wall (pytest 1469.58s): 1488s wall (pytest 1471.00s) is
no slower.

| stage | result |
|---|---|
| ruff | pass, exit 0 |
| mypy | pass, exit 0 |
| import_linter | pass, exit 0 |
| audit_docs | pass, exit 0 |
| req_coverage | pass, exit 0 |
| contracts | pass, exit 0 |
| pytest | pass, exit 0 |

Frontend half at the same head: `pnpm --dir frontend install --frozen-lockfile` and
`generate:api` rc 0; `lint` rc 0; `type-check` no errors; `test` 609 passed (609);
`build` built.

## Deviations

- **The 8a commit.** `f965b417` added the 8a test rather than only a comment. The lead accepted it
  as within 8a's scope. The gate ran on that head before the lead's S-13 grant, which named a
  comment-only head.
- **RL-1263 result.** Contention **pair 1 of 3** (RL-1263 :140-149 requires the first three
  concurrent pairs): pytest 1471.0s overlapped against 1469.6s solo, about 1.00x, under 1.5x, so it
  passes. The maintainer's dated correction withdrew an earlier "two slots confirmed"; two slots
  continue provisionally until pairs 2 and 3 are measured. (Audit note W1: this is one pair, not
  the three.)
- **Clocks.** Every time in this ledger is UTC. The dispatch record's 13:02:07 is BST.
- **An unslotted run.** At about 12:31 UTC I ran `uv run pytest -q packages/pricing-core`
  (965 passed, 96s) without the slot wrapper. Load was 8.93/5.78/3.80 at 12:35:08. Disclosed to
  the lead; no other harm found.
- Baseline ran with the pre-correction slot form (above).
- Dispatch condition 1b: the backend test is in a new file.
- The harness moved two foreground calls to the background at its 600s cap. Each wrapper's
  `flock` and `timeout` stayed in force, and I waited for the output file in my own turn.

## PRs

The slice PR is opened after the gate, from `sl-1300-pin-membership`, titled `SL-1300: …`. The
push SHA (from `git ls-remote`) is reported to the lead; the lead merges. MERGE-ACK is the
maintainer's, in the lead's channel file, never on the PR.
