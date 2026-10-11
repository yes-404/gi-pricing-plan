---
id: LG-9966
family: ledger
title: WK-1178 slice SL-1526 — exit demo (a): the real freMTPL2 rating algorithm in the seed and the 20,000-policy portfolio sample (PL-1525 + PL-1577 slice ledger)
status: active
created: 2026-10-10
owner: executor
tree: 31b88780aa52894624a5e08454ce2d5925d04b37
phase: P2
work: WK-1178
slice: SL-1526
plans: [PL-1525, PL-1577]
corrected_by: []
relates: [PL-1525, PL-1577, FD-1209, FD-1573, FD-1576]
---

# LG-9966 — WK-1178 slice SL-1526: exit demo (a)

*(LG-9966 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1526` from PL-1525 and its delta PL-1577, base `origin/main`
`31b88780aa52894624a5e08454ce2d5925d04b37`. Times are BST (`TZ=Europe/London date`) unless marked.

**GO:** `to-lead.md` "2026-10-10 21:36:36 BST — DISPATCH GO: SL-1526 (exit demo (a)) and SL-1529 (FD-1416); FD-1573 severity; SL-1575 OFF the G2 serial path (corrects my 21:33:57 items 2 and 4)", item 3: "GO SL-1526 (PL-1525 + delta PL-1577), needs 1–4 MET … author now, activate in the slice PR's first commit, merge on its ACK." Condition (item 2): the merge-ack carries PL-1577's proving run, alone in a slot: wall time and peak RSS of the 20,000-policy dislocation and attribution against DP-2's plan target of at most 60 minutes and 15.5 GiB per run; a miss is a stop to the lead (fallback (D)). The algorithm declares no decimal output.
**MERGE-ACK:** added at merge.

## Tasks

### Scope

The slice's row is `#### SL-1526 — WK-1178 exit-demo slice (a) — the real freMTPL2 rating algorithm in the seed` in `docs/roadmap.md`, under PL-1525 and its delta PL-1577. Requirement ids: `03` FR-212, FR-213, FR-226, FR-230, FR-237, FR-240, FR-246, FR-257, FR-260, FR-261; `02` FR-97, FR-101; `07` FR-440; `01` NFR none measured here. Write set: PL-1525 §Write set plus PL-1577 Task 2 (`examples/fremtpl2/{algorithm.py,model.py,seed.py,README.md,test_seed.py}`, `backend/tests/test_demo_rating_evidence.py`, `backend/tests/test_fremtpl2_algorithm.py`, this ledger, `docs/INDEX.md`, the row and plan status lines).

### Task list

- Task 0 — preconditions; premises P1–P8 re-read (Build log).
- Task 1 — the builder and its tests (Acceptance 3, 4, 5, 7).
- Task 2 — bandings, seeded tables, the Rating Version's pins, and the portfolio Dataset Version (Acceptance 1, 2; PL-1577 Task 2).
- Task 3 — golden quotes priced independently of the bundle (Acceptance 3, 6).
- Task 4 — the demo run, the gate, the proving run, the sample-vs-book comparison (Acceptance 7–11; PL-1577 Acceptance 7).

### Gate

(filled at the slice head)

### Audit

(the auditor's)

### Build log

- 2026-10-10 21:4x — Task 0. Base `31b88780`. Premise moved: P6 (`pricing_core/rating/references.py:referenced_names` now exists, SL-1536 `e4753e47`); reported to the lead, ruling awaited.
- Task 1, part 1 — red: `uv run pytest -q backend/tests/test_fremtpl2_algorithm.py` → collection error `FileNotFoundError: …/examples/fremtpl2/algorithm.py`; green after `algorithm.py`: 7 passed (one first-run failure was the test's own expectation of the input set, fixed). Commit `1f789d57`.
- Deviations, both ACCEPTED by the lead (message of 2026-10-10, after the 21:43:24 entry) as implementation choices within PL-1525: (1) rate-table slugs forbid `_` (`packages/model-schema/src/model_schema/refs.py:36`, `_SLUG = r"[a-z0-9][a-z0-9-]{1,62}"`; only the Factor grammar at `:40` admits `_`), so a table slug is `fremtpl2-<factor slug with _ → ->`, not `fremtpl2-<factor slug>`; (2) banded Factor slugs are `driv_age_band`, `veh_age_band`, `veh_power_band`, because a step's produced name may not equal its raw input's name.
- P6 RULED (A), `to-lead.md` "2026-10-10 21:43:24 BST" item B: Acceptance 4 and 7 import `referenced_names` (`packages/pricing-core/src/pricing_core/rating/references.py:38`), with no hand-copied predicate. Independence condition, quoted: "besides the planted-mismatch case (a step reading a name outside its consumes must FAIL the check, shown red), one step's expected reads set is written out literally in the test, so a wrong predicate cannot pass by agreeing with itself." Met by `test_the_reads_check_refuses_an_undeclared_read` (one name dropped from `s_premium.consumes` → exactly `{"s_premium": {"rel_veh_gas"}}`), `test_the_cross_check_refuses_a_planted_mismatch` (both directions, one failure each, naming the name) and `test_a_predicate_that_agrees_with_itself_is_not_the_oracle` (`s_premium`'s eight reads, `s_band_driv_age_band`, `s_t_veh_gas` and `s_base` written out literally). The plan's wording departure ("FD-1374's predicate, not Task 1A's code") is the lead's dispatch delta.
- Task 1, part 2 — Acceptance 4 and 7 (a)(b)(c): 12 passed in `backend/tests/test_fremtpl2_algorithm.py` (small-test slot). One first-run failure: the edge claim was written as equality, but an `output` step only declares `consumes` and evaluates nothing, so it is now "reads add no edge the declaration lacks". Per-step read sets printed by the test (`-s`): e.g. `s_premium ['base_premium_minor', 'rel_area', 'rel_driv_age_band', 'rel_region', 'rel_veh_age_band', 'rel_veh_brand', 'rel_veh_gas', 'rel_veh_power_band']`; the cross-check printed `[]` failures for all 12 evaluated strings; no `as_at` string exists ("predicate only": none). 0 undeclared reads, so 0 added edges and 0 added cycles.
- Task 2 (PL-1577 part), red: `uv run pytest -q examples/fremtpl2/test_seed.py` → `ImportError: cannot import name 'PORTFOLIO_ROWS' from 'seed'`; then green after the constant, with one expectation of my own corrected (`ids[-1] == "39999"`: `step = height // rows` = 2 over 50 001 rows, and `head(rows)` of that stride ends at policy 39 999, so the sample never reaches the last 10 002 rows: 8 passed, 1 skipped).
- **Sample vs book (PL-1577 Acceptance 7; measured 2026-10-10 with a one-off polars script over the sha256-pinned book, `build_csv(None)` vs `build_csv(20000)`, `exposure_years <= 1.05`):** the sampler is deterministic (two calls, same `IDpol` list: True). Raw rows 678 013 book / 20 000 sample; after the v2 recipe 677 442 / **19 979** (so `PORTFOLIO_VALIDATED_ROWS = 19_979`, 21 policies dropped; to be confirmed by the seed's own profile row count at the proving run). Exposure mean 0.5282 book / 0.5332 sample. Claim frequency (claims / exposure) **0.1008 book / 0.1060 sample (+5.2 %)**; claims per policy 0.0532 / 0.0565. Region share, max absolute difference over 22 regions 0.75 pp (R24 0.2370 / 0.2446; R11 0.1029 / 0.0980). Vehicle-age bands 0-2 / 3-9 / 10+: book 27.7 % / 39.2 % / 33.1 %, sample 26.1 % / 39.4 % / 34.5 % (max difference 1.7 pp). Cause check: `step` is 33 on the real file, so the sample ends at row 660 000 of 678 013; the head 660 000 rows have frequency 0.1014 and the tail 18 013 rows 0.0613 (the book 0.1007), so the truncation explains about 0.0007 of the 0.0052 gap and the rest reads as sampling noise (about 1 130 claims in the sample, standard error about 3 %). **Reported to the lead before the demo text is final**, as the 00:34:03 entry requires if any column differs materially; the frequency is the one that does.
- Task 2 (examples/), code: `model.py` (banded Factors `driv_age_band`/`veh_age_band`/`veh_power_band` on 5 quantile Bandings proposed by `transform_service.propose_banding_for_version`; `create_demo_bandings`, `seed_demo_rate_tables`, `demo_base_premium`, `demo_golden_cases`, `monotone_property`, the real `author_demo_rating_evidence` and `create_approved_rating_version`); `seed.py` (the portfolio sample as its own Dataset Version, ingested through the v2 recipe, validated and promoted, its id and row count written into `last-seed.json`, the exact count asserted); `algorithm.py` (`glm_premium_minor`). Offline preview of the Bandings the proposal gives on the full cleaned book (pure `propose_banding`, quantile, 5 bands): `driv_age` (18, 32, 40, 48, 57, 100) labels 18-31 / 32-39 / 40-47 / 48-56 / 57+; `veh_age` (0, 2, 4, 8, 12, 100) labels 0-1 / 2-3 / 4-7 / 8-11 / 12+; `veh_power` (4, 5, 6, 7, 8, 15) labels 4-4 / 5-5 / 6-6 / 7-7 / 8+. The saved Bandings' own ids and edges are printed by the seed and recorded here at the proving run.
- Task 2/3 DB tests (`backend/tests/test_demo_rating_evidence.py`: one table per Factor, the pins, the GLM premium to the penny with non-circular golden quotes and the monotone property) are written and collect (3 tests); they need the DB stack and wait for my gate slot. Red-first for them is shown at that slot on the base tree (`origin/main` has no `seed_demo_rate_tables`), then green at the head.
- **Sampler fix, `to-lead.md` "2026-10-10 21:55:37 BST — SL-1526 sample-vs-book: NOT material; the tail skip IS fixed in-slice, WITH WF-699 :30's dated amendment in the same commit"** (items 1–5). Not material (+5.2 % was 1.7 standard errors); fixed in this slice: `seed.py:build_csv` takes the evenly spaced integer indices `[i * N // n for i in range(n)]` (all rows when `n >= N`), replacing `gather_every(height // rows)`; WF-699 :30 carries the dated amendment with the old text struck, in the same commit. PL-1577 is frozen (its DP-2 names the every-nth-row rule); this entry records the change. Red first: `uv run pytest -q examples/fremtpl2/test_seed.py` → `AssertionError: assert ['1', '3', '5'...] == ['1', '3', '6'...]` ("At index 2 diff: '5' != '6'"; the old stride against the re-derived indices); green: 8 passed, 1 skipped. No seeded golden quote moves: the golden quotes are the GLM's premiums, the GLM is fitted on the full book (or `--rows`) and the sample is only the dislocation portfolio, so no price changes.
- **Re-measure after the fix** (same script and book as above, the sample is deterministic: True): after the v2 recipe 677 442 book / **19 985** sample (15 dropped; `PORTFOLIO_VALIDATED_ROWS` is now 19_985). Exposure mean 0.5282 book / 0.5276 sample. Claim frequency **0.1008 book / 0.0957 sample (-5.1 %)** on 1 009 sample claims (relative SE about 3.1 %, so 1.6 SE; |gap| < 6 %, no STOP). Claims per policy 0.0532 / 0.0505. Region share max absolute gap **0.24 pp** (was 0.75). Vehicle-age bands 0-2 / 3-9 / 10+: book 27.7 / 39.2 / 33.1 %, sample 27.3 / 39.3 / 33.4 % (max gap **0.44 pp**, was 1.7). The README quotes the measured -5.1 %. The sample now spans the book; the remaining frequency gap is sampling noise of a different draw (the sign flipped), as the SE says.

- **Gate fixes after the full gate at `e00c71c1` (classified by the lead, `from-lead` "2026-10-11 00:42:22 BST"; item numbers are that classification's).** #2: the monotone property's name carried the banded column's `_` (`premium-monotone-in-veh_age_band`-style), which `RegressionSuiteContent`'s property-name slug refuses; it is now `column.replace("_", "-")`. Red first: `uv run pytest -q backend/tests/test_demo_rating_evidence.py -k monotone_property_name` with the replace removed → `1 failed` (`ValidationError … RegressionSuiteContent`); with it → `1 passed` (new pure test, no DB). #3: `uv run mypy` 7 errors in `examples/fremtpl2/model.py` (:507 untyped lambda call, :540–541 `float | None` comparisons) → typed `picks` as `Callable[[Sequence[RelativityLevel]], RelativityLevel]` and narrowed the relativity series; `mypy` 0 and `ruff check .` 0 on the whole tree.

- **In-process counterexample, 2026-10-11 ~10:38 (the maintainer's narrow exception, `to-lead.md` "2026-10-11 11:36:45 BST — EXCEPTION GRANTED (narrow, named): SL-1526's counterexample computed IN-PROCESS beside SL-1529's gate"; one process, no DB, no pytest).** Command: `timeout 180 nice -n 19 ionice -c3 uv run --directory <sl-1526 worktree> python ~/gi-pricing-plan.local/handover/sl1526-regate/inproc.py` at head `dc11d9d1`, load1 6.69 before / 6.42 after, rc 0, 5 s. The script compiles the demo algorithm (`test_fremtpl2_algorithm._full_algorithm`) with seven rows-tables built from the DB test's `_ESTIMATES`, then runs `pricing_core.rating.properties` over the three golden bases and over `generate_contexts(contract, 25, SPLIT_SEED)`, the suite's own generation. **Finding:** the three golden bases pass the monotone `veh_age` increasing property, `no_null_output` and `premium_bounded` (premiums 25000, 27629, 32101 from `veh_age` 0, 7, 15 on the first base). **All 25 generated contexts fail**, because the generator draws arbitrary text for the five categorical inputs (`veh_brand`, `veh_gas`, `area`, `region`, ...): `testing.py:138-140` samples a declared `domain` only for an `enum` input, and `algorithm.py` declares them `string` with a `domain`. A table lookup on a value outside the table (`on_miss: error`) is refused, the scorer returns `None`, and every property treats `None` as a failure (monotone `broken_at=(v, v)`). So the red is not a non-monotone premium and not the slug fix; it is the input contract's type. Output, verbatim:

```text
contract veh_age: [('veh_age', 0, 30)]
base=base-levels inputs={'bonus_malus': 100, 'driv_age': 18, 'veh_age': 0, 'veh_power': 4, 'veh_brand': 'B1', 'veh_gas': 'Diesel', 'area': 'A', 'region': 'R11'}
  grid/premiums=[(0, ('quoted', 25000)), (7, ('quoted', 27629)), (9, ('quoted', 27629)), (15, ('quoted', 32101)), (22, ('quoted', 32101)), (23, ('quoted', 32101)), (28, ('quoted', 32101)), (30, ('quoted', 32101))]
  monotone increasing veh_age: broken_at=None quoted=8
  no_null_output: holds=True
  premium_bounded: holds=True
base=first-non-base-levels inputs={'bonus_malus': 100, 'driv_age': 25, 'veh_age': 3, 'veh_power': 6, 'veh_brand': 'B2', 'veh_gas': 'Regular', 'area': 'B', 'region': 'R24'}
  grid/premiums=[(0, ('quoted', 25000)), (7, ('quoted', 27629)), (9, ('quoted', 27629)), (15, ('quoted', 32101)), (22, ('quoted', 32101)), (23, ('quoted', 32101)), (28, ('quoted', 32101)), (30, ('quoted', 32101))]
  monotone increasing veh_age: broken_at=None quoted=8
  no_null_output: holds=True
  premium_bounded: holds=True
base=last-levels inputs={'bonus_malus': 100, 'driv_age': 40, 'veh_age': 10, 'veh_power': 8, 'veh_brand': 'B2', 'veh_gas': 'Regular', 'area': 'B', 'region': 'R24'}
  grid/premiums=[(0, ('quoted', 35477)), (7, ('quoted', 39208)), (9, ('quoted', 39208)), (15, ('quoted', 45553)), (22, ('quoted', 45553)), (23, ('quoted', 45553)), (28, ('quoted', 45553)), (30, ('quoted', 45553))]
  monotone increasing veh_age: broken_at=None quoted=8
  no_null_output: holds=True
  premium_bounded: holds=True

== generated contexts: 25 under seed 20260827 (the suite's generation) ==
case 0 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'driv_age': 18, 'veh_age': 0, 'veh_power': 4, 'veh_brand': '0', 'veh_gas': '0', 'area': '0', 'region': '0', 'bonus_malus': 50}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 1 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'driv_age': 30, 'veh_age': 0, 'veh_power': 4, 'veh_brand': '0', 'veh_gas': '0', 'area': '0', 'region': '0', 'bonus_malus': 50}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 2 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'region': '0Bsw8l', 'veh_brand': 'eFgat', 'veh_gas': 'luY2', 'driv_age': 30, 'area': 'R', 'bonus_malus': 91, 'veh_power': 8, 'veh_age': 12}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 3 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'driv_age': 33, 'area': 'ot7', 'veh_power': 5, 'veh_gas': '4HRtaaKZn2', 'region': 'mTl5G', 'veh_age': 6, 'bonus_malus': 91, 'veh_brand': 'ZVTGSHZ2I9'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 4 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'bonus_malus': 173, 'veh_age': 12, 'veh_gas': 'iigY', 'veh_brand': 'X0jM', 'area': 'LT2AIBpoMn', 'region': 'YVcdSnzOz1a1', 'veh_power': 4, 'driv_age': 67}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 5 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_age': 3, 'veh_power': 12, 'area': 'gFe', 'driv_age': 65, 'region': 'ErWRGh0ANsXu', 'veh_gas': 'Gp', 'bonus_malus': 171, 'veh_brand': 'Z'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 6 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'area': 'R', 'region': 'QJ', 'veh_gas': 'ptdQMmmuVStE', 'bonus_malus': 77, 'driv_age': 71, 'veh_power': 13, 'veh_brand': 'EUCg', 'veh_age': 7}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 7 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'bonus_malus': 170, 'area': 'czS', 'veh_power': 7, 'veh_age': 1, 'region': 'xyLd', 'driv_age': 51, 'veh_gas': 'a', 'veh_brand': 'Z'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 8 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_brand': 'FKOCMS', 'bonus_malus': 58, 'area': 'X1jhqm8TA', 'region': 'gaaahm2VkkUD', 'veh_age': 29, 'veh_power': 11, 'veh_gas': 'hy', 'driv_age': 86}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 9 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'area': 'qkxKf5Tf', 'veh_brand': 'A', 'driv_age': 59, 'veh_age': 28, 'veh_gas': 'LPj9LBD', 'bonus_malus': 100, 'region': 'GS', 'veh_power': 4}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 10 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_brand': 'kFM', 'region': 'HG', 'driv_age': 60, 'area': 'h8Ug6f', 'veh_gas': 'atiY', 'veh_age': 14, 'veh_power': 5, 'bonus_malus': 189}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 11 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_brand': 'kFM', 'region': 'HG', 'driv_age': 60, 'area': 'h8Ug6f', 'veh_gas': 'kFM', 'veh_age': 14, 'veh_power': 5, 'bonus_malus': 189}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 12 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_brand': 'kFM', 'region': 'HG', 'driv_age': 60, 'area': 'h8Ug6f', 'veh_gas': 'kFM', 'veh_age': 14, 'veh_power': 4, 'bonus_malus': 189}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 13 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_brand': 'kFM', 'region': 'HG', 'driv_age': 60, 'area': 'h8Ug6f', 'veh_gas': 'kFM', 'veh_age': 14, 'veh_power': 4, 'bonus_malus': 50}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 14 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_brand': 'kFM', 'region': 'HG', 'driv_age': 60, 'area': 'h8Ug6f', 'veh_gas': 'kFM', 'veh_age': 14, 'veh_power': 14, 'bonus_malus': 50}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 15 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_brand': 'kFM', 'region': 'HG', 'driv_age': 18, 'area': 'h8Ug6f', 'veh_gas': 'kFM', 'veh_age': 14, 'veh_power': 14, 'bonus_malus': 50}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 16 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_brand': 'kFM', 'region': 'HG', 'driv_age': 18, 'area': 'h8Ug6f', 'veh_gas': 'HG', 'veh_age': 14, 'veh_power': 14, 'bonus_malus': 50}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 17 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_power': 12, 'region': 'get', 'veh_gas': 'Permission', 'driv_age': 49, 'bonus_malus': 176, 'veh_age': 19, 'veh_brand': '0', 'area': 'ewzdY6'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 18 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_power': 12, 'region': 'get', 'veh_gas': 'Permission', 'driv_age': 49, 'bonus_malus': 176, 'veh_age': 0, 'veh_brand': '0', 'area': 'ewzdY6'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 19 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_power': 4, 'region': 'get', 'veh_gas': 'Permission', 'driv_age': 49, 'bonus_malus': 176, 'veh_age': 0, 'veh_brand': '0', 'area': 'ewzdY6'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 20 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_power': 4, 'region': 'get', 'veh_gas': 'Permission', 'driv_age': 49, 'bonus_malus': 50, 'veh_age': 0, 'veh_brand': '0', 'area': 'ewzdY6'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 21 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_power': 4, 'region': 'get', 'veh_gas': 'Permission', 'driv_age': 49, 'bonus_malus': 50, 'veh_age': 0, 'veh_brand': '0', 'area': 'get'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 22 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_power': 4, 'region': 'get', 'veh_gas': 'Permission', 'driv_age': 18, 'bonus_malus': 50, 'veh_age': 0, 'veh_brand': '0', 'area': 'get'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 23 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_power': 4, 'region': 'get', 'veh_gas': 'Permission', 'driv_age': 18, 'bonus_malus': 50, 'veh_age': 18, 'veh_brand': '0', 'area': 'get'}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
case 24 FAILS monotone_broken_at=(0, 0) no_null=False bounded=False
  base={'veh_age': 9, 'veh_brand': '1fz', 'area': 'lqqXMc5', 'region': 'r8', 'veh_gas': '4VNuXsHJNN', 'veh_power': 12, 'driv_age': 54, 'bonus_malus': 100}
  grid/premiums=[(0, None), (7, None), (9, None), (15, None), (22, None), (23, None), (28, None), (30, None)]
done
```

- **The enum fix (`86e6a645`; GO `from-lead` after the maintainer's "2026-10-11 11:4x BST — SL-1526 cause …", option 1, conditions (a)-(d)).** `examples/fremtpl2/algorithm.py:143` declares the categorical inputs `"type": "enum"` (was `"string"`). Red first: `uv run pytest -q backend/tests/test_fremtpl2_algorithm.py -k generated_categorical` with `string` → `AssertionError: assert {('area', '0'...), ('region', 'GS'), ('region', 'QJ'), ...} == set()` (generated values outside the declared domains); green is shown at the next slot (I ran that one red test under `small-test` while SL-1529 held gate-1, which the addendum's rule 3 forbids; disclosed to the lead). The in-process script (same bounded form, `timeout 180 nice -n 19 ionice -c3`, load1 ≤ 3.1, no DB, no pytest) was rebuilt on the DB test's own base (`_BASE_MINOR`) and run before and after, the "before" by reverting that one line in the worktree. Output, verbatim.
  - **(a) golden prices unchanged.** Before (`string`):
```text
load average: 2.97, 4.29, 4.36
golden base-levels: scored=200000 expected=200000
golden first-non-base-levels: scored=221034 expected=221034
golden last-levels: scored=364424 expected=364424
generated contexts passing all three properties: 0 of 25
bundle content_hash: sha256:c4e2d1a6d73a65b41f0e2471c61e9a2ad164cf5657e21e64a289863cc76d44d5
```
  After (`enum`):
```text
load average: 2.89, 4.25, 4.35
golden base-levels: scored=200000 expected=200000
golden first-non-base-levels: scored=221034 expected=221034
golden last-levels: scored=364424 expected=364424
generated contexts passing all three properties: 25 of 25
bundle content_hash: sha256:74730d2632e8768893b21c49e4d27319f2818c8245a088ed733f0548fa09f5d6
```
  Each golden quote scores to the independent expectation both ways: base-levels 200000 → 200000, first-non-base-levels 221034 → 221034, last-levels 364424 → 364424. The generated contexts passing all three properties go from 0 of 25 to 25 of 25.
  - **(b) pinned bundle hash.** The slice pins none: no test or file in `git diff origin/main...HEAD` holds a bundle hash, and `examples/fremtpl2/algorithm.py` does not exist on `origin/main` (`git cat-file -e origin/main:examples/fremtpl2/algorithm.py` → fatal: not in origin/main), so no hash on main can change. The in-process bundle's own `content_hash` moves, as the lead predicted (the input contract is hashed): `sha256:c4e2d1a6…` → `sha256:74730d26…` (in-process, synthetic tables).
  - **(c) behaviour change**, probed in-process with `veh_brand="ZZZ"` on the base context (`P._score_context_sync`): before `CodedError RATE_TABLE_MISS: the engine failed evaluating step 's_premium' (FR-255); an on_miss='error' step it consumes most likely found no matching row`; after `CodedError INPUT_CONTRACT_VIOLATION: input 'veh_brand' is not in ['B1', 'B2']`. The engine code is measured; the HTTP status of that code is not measured here.
  - **(d)** 25 of 25 generated contexts plus the three goldens pass (above).

- **Condition (b) does not apply, recorded at the lead's instruction.** The slice has no "own pinned hash": no test or file in `git diff origin/main...HEAD` pins a bundle hash, and `examples/fremtpl2/algorithm.py` is not on `origin/main`, so no hash on main changes. The only hash that moved is the in-process bundle's own `content_hash`, `sha256:c4e2d1a6d73a65b41f0e2471c61e9a2ad164cf5657e21e64a289863cc76d44d5` → `sha256:74730d2632e8768893b21c49e4d27319f2818c8245a088ed733f0548fa09f5d6` (synthetic tables).
- **Re-slot script:** `~/gi-pricing-plan.local/handover/sl1526-regate/slot3.sh`, head guard `bbe74c34`, the standing PREFLIGHT (alembic upgrade head rc 0, exactly one head, postgres/redis/minio healthy), then the 3 DB tests, `test_fremtpl2_algorithm.py` (with the new categorical-domain test) and `test_seed.py` at full `-v` output, whole-tree mypy, ruff and DagDesigner alone; logs in `sl1526-regate/logs/`.

- **Re-gate at `b7c54bd5` (the HTTP-422 test added), 2026-10-11 14:15:44-14:16:36 BST, gate-1, `slot3.sh` (head guard `b7c54bd5`), load1 7.80 at acquire.** Preflight ok (alembic upgrade head rc 0, 1 head, postgres/redis/minio healthy). Logs: `~/gi-pricing-plan.local/handover/sl1526-regate/logs/`, output `slot3.out`, end marker `end 2026-10-11T14:16:36+01:00 rc=1`.

  | Stage | rc | Result |
  |---|---|---|
  | db_tests (`test_demo_rating_evidence.py`) | 0 | 5 passed, 9.97s; `test_a_categorical_outside_its_declared_domain_is_a_422_through_the_api` PASSED: base quote 200, `veh_brand="ZZZ"` 422, code `INPUT_CONTRACT_VIOLATION`, detail names `veh_brand` |
  | red_control | 1 | "UNEXPECTED" by the script; ruled the setup-red below |
  | algorithm_and_seed | 0 | 21 passed, 1 skipped |
  | mypy | 0 | 234 source files |
  | ruff | 0 | |
  | dagdesigner_alone | 0 | |

  **red_control.** The same test against the parent's `string` `algorithm.py` (`86e6a645^`, via `GIP_FREMTPL2_EXAMPLE_DIR`) fails in SETUP, before any request: `red_control.log:141` `E           RuntimeError: demo regression Job failed`, `:143` `.../red-example/model.py:661: RuntimeError`, `:151` job handler failed with `"code":"PROPERTY_ASSERTION_FAILED"` (`rating_handlers.py:210`). The script expected a red at the status assert and got one at setup, so it marked the stage UNEXPECTED. **The property is not named in the log** (the code is sanitised); the suite's properties are `no-null-output`, `premium-bounded` and `premium-monotone-in-veh-age`, and the link to this slice's defect rests on the separate in-process measurement above (`string` 0 of 25 generated contexts pass all three, `enum` 25 of 25). **The HTTP-status contrast on the parent was not measured**: the parent cannot reach the request, and a status-only contrast would not discriminate (the parent most likely answers 422 with `RATE_TABLE_MISS`, unmeasured); what discriminates is the head's 422 carrying `INPUT_CONTRACT_VIOLATION` and naming `veh_brand`. **Only the head-guard abort of the script's PREFLIGHT is proven** (a wrong expected head: `HEAD GUARD REFUSED`, `end ... rc=97`); the alembic and health aborts (exits 93-95) were not exercised.
  **Ruling (a) accepted, (b) rejected**: `to-lead.md` "2026-10-11 14:19:08 BST — SL-1526 re-gate @b7c54bd5 GREEN; red_control setup-red: (a) ACCEPTED; next its ALONE window" - the parent fails in setup from the very defect this slice fixes, so it cannot reach the assert, and that is the red for condition (c); rc 1 is that setup-red, not a harness fault. (b), a regression-gate bypass so the parent reaches the request, is not run.

- **Defect fix, 2026-10-11 (the maintainer's ruling, `to-lead.md` "2026-10-11 18:59:23 BST" item 1): the demo suite's properties are fixed declarations, read from no fit.** `monotone_property(fit, bandings)` chose a `monotone` property from the fit it then checked (a property chosen from the fit cannot fail); it is deleted. `examples/fremtpl2/model.py` now has `declared_properties()` (no parameters: `no-null-output`, `premium-bounded`), and `author_demo_rating_evidence` lost its `monotone` parameter. **No monotonicity is declared for `veh_age`**, and the fitted relativities are the evidence why (`out-2026-10-11b/wrapper.out`, "fitted relativities, factor veh_age_band", the real GLM fit; base `12+`): `0-1` 2.1436, `2-3` 1.0990, `4-7` 1.1016, `8-11` 1.3526, `12+` 1.0 (base). They are not monotone in the band order. Red first: `backend/tests/test_demo_rating_evidence.py::test_the_declared_properties_do_not_depend_on_the_fit` against `386058fc` (two different fits, one rising and one jagged, given to `monotone_property`) failed with `AssertionError` (the two property lists differ); replaced by `test_the_declared_properties_are_fixed_and_read_no_fit` (green; `ruff` 0, `mypy` 0 over 234 files). The DB test's `premium-monotone-in-veh-age` assertion and the name-slug test went with the function.

## PRs

(added at the PR)
