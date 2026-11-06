---
id: PL-2050
family: plan
kind: map
title: WK-1178 — slice G, the test-only limbs (FD-1723 slice B, FD-1747 limb 2 and its reproduction, FD-1887 H1 and H2, FD-1354's metrics guard), SL-2051 — a dated Work-plan delta
status: active                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-06   # original date 2026-11-05, working id 8355, minted 2026-11-06
owner: planner
tree: 2f108b1eda22a4835279cee9b4c9e305babe3662
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1856, FD-1723, FD-1747, FD-1887, FD-1354, FR-33, FR-41, FR-80, FR-123, FR-452]
---

# PL-2050 — WK-1178: slice G, the test-only limbs (SL-2051, a dated Work-plan delta)

*(Minted 2026-11-06 as PL-2050 from working id 8355, with the slice SL-2051 (working id 8356) and ledger LG-2052 (working id 8357), in the SL-2051 PR.)*

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It `relates:` `PL-1856` and leaves it unedited; its Slice B, never
> seated, is carried here with three more rows. One slice row, SL-2051. The executor's skills are
> `superpowers:test-driven-development`, `.claude/skills/python-test` and `git-hygiene`. PL-2050, SL-2051
> and LG-2052 are working ids reserved by the lead.

## Authority

- **The lead's task,** on `~/gi-pricing-plan.local/handover/p2-code-owed-triage2-2026-11-05.md` (`c9e75802158f`)
  §3 "NEW slice G": 6.5 h, "one SOLO gate", "one DB window", and "Any test red unmutated: STOP (PL-1856 B3); that
  is a finding, not a test fix."
- **`PL-1856`**, Slice B, tasks B0 to B3 and Acceptance 11 to 14, and DP-C ruled "TESTS" (the maintainer's entry
  "2026-10-22 16:02:49 BST"). Its Global Constraint, verbatim: "**A test-only limb that goes red unmutated is a
  defect, not a test to adjust** (seat brief item 13): STOP to the lead, who routes a new FD."
- **FD-1747.** "must fail loudly when the limiter failed open, by asserting `metrics.rate_limit_unenforced` did not
  move across the test", and "with the by-run reproduction printed here". Its re-rate trigger: "HIGH if the by-run
  reproduction shows the production limiter, not the test, can reset".
- **FD-1887.** "Both are owed, by WK-1178, before the P2 close." H1 and H2 as RS-1890 states them.
- **FD-1354.** "**Owned item: WK-1178, `…/modelling/metrics.py:122,135,152-153`**, to guard before any test pins a
  metric certificate's text."
- **The freeze.** The entry "2026-11-05 09:58:58 GMT".

## Goal

Four evidence gaps close with tests alone: FR-41, FR-33, FR-80 and FR-123 each have a test that can fail; a limiter
that failed open fails its test loudly, and FD-1747's cause is proved by run; the freMTPL2 guard reads what a guard
actually tests; and a metric certificate's text cannot be pinned unseen. **No source file changes.**

## Evidence at `2f108b1e`

Every cite was read at `origin/main` `2f108b1eda22a4835279cee9b4c9e305babe3662`. `git diff --stat dae9637e 2f108b1e --
backend/tests packages scripts deploy` is empty.

- **`PL-1856`'s cites have moved.** `ingest_upload` is `backend/src/app/data/ingestion.py:97` (**not** `platform/`), the
  recipe at `:169-183`, the stored `derived_from["recipe"]` at `:238-239`, `IngestionRunRow(` at `:249`, `_find_run` at
  `:289`, `_store_table` at `:309`.
- **FR-33.** Markers at `backend/tests/test_ingestion.py:164,188`; neither fails a run. A failing recipe refuses at
  `:177`, "The preparation recipe could not be applied".
- **FR-80.** `backend/tests/test_lineage.py:454`, `test_an_archived_version_stays_readable_and_referenceable`: reads the row
  and asserts its status. It is marked FR-80 and proves less than its name. The route module is
  `backend/src/app/api/dataset_versions.py`.
- **FR-123.** `packages/pricing-core/tests/test_gbm.py:642`, `:657`. The second's docstring: "the constraint cannot change
  the answer". The constraint reaches XGBoost at `gbm.py:867` and LightGBM at `:1020`.
- **FD-1747.** Limb 1 is merged: `backend/tests/test_score_rate_limit.py:57`, `_KEY_TTL_SECONDS` 3600 (`d657736b`).
  `_unenforced(environment)` is `:225`, used only by `test_a_redis_outage_admits_counts_and_logs_each_request` (`:243`,
  `:249`). **Two tests fail open on purpose**: that one and `test_without_the_fail_open_guard_an_outage_is_a_500` (`:258`).
  The new check must exempt them by name, or it reds on them.
- **FD-1887.** `tests/test_fremtpl2_data_guard.py`: `_is_guard` `:140-148` asks only for `exists` in the `If` test, so
  `if other.exists(): pytest.skip(...)` passes (H2 open). `_names_the_data_path` (`:94`) matches the literal
  `fremtpl2/data` and a `BinOp` join, so `os.path.join(...)` and `Path("examples", "fremtpl2", "data")` pass unseen, and
  lowercase `fremtpl2` in a join is not matched (H1 open). `_data_aliases` (`:124`) is where an import alias would meet
  it. **Hardening a guard can red real tests:** a test that reaches the data with a guard H2 now refuses goes red at base
  (a finding: the test needs a real guard, and that test is in the write set only as this plan's R3 says).
- **FD-1354.** `git grep -n -E 'value at f=log|one unit away|value changes by a factor|constant population of 1,000'
  origin/main -- packages backend/tests` prints **only `metrics.py:122,135,152`**. Zero pins. So no defect exists on main, and
  the owned item is a watch, not a fix.

## Decision points

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-G1 | FD-1354's owned item: fix or carry? No test pins the text, so there is no defect today. | (a) **A guard test, this slice:** one test that fails if any test file pins a measured `metrics.py` phrase, 0.5 h, test-only, and the owned item is discharged by the guard it asked for. (b) **Source fix:** normalise the four details as `objectives.py` did (status only). Removes the risk at root, but it is a source change in a test-only slice, and it changes the text of a certificate that may be stored. (c) **A dated carry** on the same event, 0 h. Nothing breaks; the item stays open past the close. | **(a).** It is the item's own word, "to guard", it costs less than its row's 0.75 h, it keeps G test-only, and it leaves the next person a failing test rather than a register line. |

No other choice is open: `PL-1856` DP-C is ruled TESTS, and H1 and H2 are stated.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's merge tree. Items 1 and 2
apply to this plan; A1 to A11 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing line except check 31 /
   check 32 lines naming working ids 8355, 8356 or 8357. After the mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no line that stands for a set
   of ids.

The slice:

- **A1. Test-only.** `git diff --name-only origin/main...HEAD -- backend/src packages/pricing-core/src packages/model-schema/src
  frontend deploy scripts` prints nothing.
- **A2. Unmutated red is a STOP.** A new test red with no mutation: the slice stops, the failing line goes to the lead, and no
  assert is softened (`PL-1856` B3). The rest of the slice may continue only on the lead's word.
- **A3. Each limb has a mutation, applied, run, recorded, reverted.** LG-2052 quotes each red, and `git diff --quiet -- backend/src
  packages` rc 0 after each. T1 to T4 by `PL-1856` Acceptance 11 to 14, restated below.
- **A4. FR-41.** T1: bytes `B` with recipe `R` into one Dataset, then `B` with the stored `derived_from["recipe"]` into a second;
  each stored table's blob content hash is equal. Mutation: drop one replayed step; fails on the hash.
- **A5. FR-33.** T2: a key `K` with a failing recipe is refused; `K` again with a good recipe creates a version, `reused is False`.
  Mutation: write a `status="failed"` run before the refusal, and have `_find_run` return it; fails.
- **A6. FR-80.** T3: over the API, an Auditor `GET`s an archived Dataset Version, 200, status `archived`; a `GET` of a Model fitted on
  it is 200 and names the version, which resolves. Mutation: filter `archived` out of the read; fails. The old row test stays.
- **A7. FR-123.** T4, both backends, on data with a real cross-group interaction: no root-to-leaf path splits on two groups, and
  holdout predictions differ from the unconstrained fit. Mutation: drop the constraint before the backend call; the path assert fails.
- **A8. FD-1747.** T5: an autouse check in `test_score_rate_limit.py` fails a test across which `metrics.rate_limit_unenforced` moved,
  naming "limiter not enforced"; the two deliberate fail-open tests are exempt by name. Mutation: a test run with the store timing out
  reds by that message, not by `409 == 429`. **The reproduction**, by the essay's recipe, in a scratch copy never under the repo, with
  `_KEY_TTL_SECONDS` at its shipped value: `GAP=2.5` RED `assert 409 == 429`, `GAP=0` GREEN, and with 3600 `GAP=2.5` GREEN. All three
  outputs in LG-2052. **A different result, or any sign that the production limiter resets, is FD-1747's HIGH trigger: STOP.**
- **A9. FD-1887.** T6, T7 added to the guard's own tests: H2: `if other.exists(): pytest.skip(...)` is not a guard. H1: lowercase
  `fremtpl2` in a join, a `Path(...)` call, `os.path.join` inside a function, and `from … import x as y`, each caught. Each red at
  base by being passed. `test_every_test_that_reaches_the_fremtpl2_data_carries_the_guard` stays green over the real tree, or A2
  governs.
- **A10. FD-1354,** under DP-G1 (a). T8: fails if a test file other than `test_objectives.py`'s reference holds one of the four phrases.
  A planted pin in a scratch copy reds it; the plant is quoted and not committed.
- **A11. The gate and the records.** The GREEN set by import closure (common seat brief, item 29), commands and list in the LG. **The
  full code gate, both halves, SOLO**, after R, A and D (triage2 §5), green at the re-merged head, every rc quoted. **FD closing acts
  in the FD-1842 form, in the slice's own PR, by the slice's auditor:** FD-1747, with the reproduction printed in the essay as it
  orders, and FD-1887. **Dated lines, not closes:** FD-1723 (its FR-7 row stays a named exception; FR-14 and FR-15 by their own
  rulings) and FD-1354's register row `:284`, which reads as fully discharged. **The LG Audit section, with the lead's adoption, lands
  in the audit's own commit**, and `docs/INDEX.md` is regenerated after the closing acts (common seat brief, item 17).

## Global Constraints

- **G1. No source file.** A source change appears only through a STOP and a ruling (`PL-1856` Write set B).
- **G2. No assert is softened to make a test pass** (common seat brief, item 13).
- **G3. A mutation is never committed.** Each is applied, run, reverted, and proved reverted.
- **G4. At most 3 files per run** (`PL-1856` B1).
- **G5. The reproduction's sleep lives in a harness outside the repository,** in the seat's scratch.
- **G6. The old FR-80 test stays.** T3 is added beside it.

## Needs

- **One DB window, lead-granted in writing,** about 45 min, single-tenant, no gate or timed stage beside it: a `createdb -T` copy under
  the slice's own name, **never the template**. T1, T2, T3, T5 and the reproduction. **Redis: the brief names one of `-n 11`, `12`, `13`;
  `GIP_REDIS_URL` is set explicitly; never db 0, which is live.** It ends with `redis-cli -n <db> dbsize` = 0 and the copy dropped, both
  quoted (common seat brief, items 22, 23, 33).
- **T4, T6, T7, T8** are DB-free, through `~/gi-pricing-plan.local/handover/run-small.sh`.
- **Docker** beyond the shared services, **NFR VM:** nothing.

## Tasks

### SL-2051 — the test-only limbs

**The row.** After R, A and D at the gate. WK-1178. One `sonnet` executor. Requirements: `01` FR-41, FR-33, FR-80; `02` FR-123; `07`
FR-452 (FD-1747). Depends on: DP-G1 ruled; the GO; the DB window; a gate slot. **Size:** 6.25 h (triage2 6.5 h, less 0.25 h under DP-G1 (a)):
FD-1723 B 3.5, FD-1747 1.25, FD-1887 1, FD-1354 0.5. SOLO gate about 2.5 h, not counted. Merged before Thu 12 Nov 2026; still red at Wed
11 Nov 12:00 → the exception list. **Split point:** T6 to T8 are DB-free and can be done first.

**R0.** Re-read every cite at the base; name the blob ref's content-hash field read in T1 (`_store_table`, `:309`); read `to-lead.md` for
any later ruling on these rows.

**R1 — FD-1723 slice B, the DB half (T1, T2, T3), in the window.** `backend/tests/test_ingestion.py`, `req("FR-41")`:
`test_the_stored_recipe_replayed_over_the_same_bytes_gives_the_same_tables`; `req("FR-33")`:
`test_a_key_whose_run_failed_is_released_and_the_next_run_ingests`. `backend/tests/test_lineage.py`, `req("FR-80")`:
`test_an_auditor_reads_an_archived_version_and_its_model_over_the_api`.

**R2 — FR-123.** `packages/pricing-core/tests/test_gbm.py`, `req("FR-123")`, parametrised on `BACKENDS`:
`test_a_constrained_booster_has_no_cross_group_split`. Build `y` with a real `a * b` term, group `(a,)`, `(b,)`. Walk the trees (XGBoost
`trees_to_dataframe`, LightGBM `dump_model`), collecting features along each root-to-leaf path. Assert no path holds both, and that the
unconstrained booster's holdout predictions differ.

**R3 — FD-1887.** In `tests/test_fremtpl2_data_guard.py`: `_is_guard` requires the `.exists()` expression to name the data (`DATA_DIR`,
`ARFF`, a `fremtpl2` or `.arff` string, or an alias from Reach); `_names_the_data_path` recognises lowercase `fremtpl2` in a join, a `Path(...)`
call and `os.path.join`; `_loaded` follows `from … import x as y`. If the real-tree test then names a test whose guard was never real, A2
governs: **that is the guard working**, and the lead rules the fix to that test.

**R4 — FD-1747, in the window.** In `test_score_rate_limit.py`:

```python
#: The two tests that fail open on purpose; anything else that moves the counter was not enforced.
_FAILS_OPEN = {
    "test_a_redis_outage_admits_counts_and_logs_each_request",
    "test_without_the_fail_open_guard_an_outage_is_a_500",
}


@pytest.fixture(autouse=True)
def _limiter_was_enforced(request: pytest.FixtureRequest) -> Iterator[None]:
    """FD-1747: a fail-open admit and a correct admit are both `!= 429`, so a Redis timeout
    otherwise reads as a limiter bug."""
    before = _unenforced_total()
    yield
    if request.node.name not in _FAILS_OPEN:
        assert _unenforced_total() == before, "limiter not enforced: it failed open in this test"
```

`_unenforced_total` sums `_unenforced` over every environment the module uses, or reads the metric family across labels: read at R0. Then the
reproduction (A8), and paste the three outputs.

**R5 — FD-1354.** T8, `packages/pricing-core/tests/test_metrics.py`, under DP-G1 (a):
`test_no_test_pins_a_metric_certificates_measured_text`, the four phrases, over `packages/*/tests` and `backend/tests`, excluding this
test's own file, with a comment citing the essay's item.

**G.** A11. No migration, no contract regeneration. CI from the three-dot diff: `python`, `docs`, `history-policy`.

### Write set

- `backend/tests/test_ingestion.py`, `backend/tests/test_lineage.py`, `backend/tests/test_score_rate_limit.py`,
  `packages/pricing-core/tests/test_gbm.py`, `packages/pricing-core/tests/test_metrics.py`, `tests/test_fremtpl2_data_guard.py`.
- Any test the hardened guard names, only on the lead's ruling (R3).
- LG-2052 under `docs/ledgers/`.
- At the mint: the SL-2051 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, the essays and `docs/findings/register.md` (A11).

### Files shared with other groups

No file with D, R, A, C, T, H, F, LAST-1, LAST-2 or P, read from each Write set. `conftest_db` changes under H sit beneath T1 to T3: a re-merge
only. **Safe in parallel for building.** Its gate goes after R, A and D; its DB window is serial with all.

## Hand-off (not this plan's writes)

- DP-G1 and the GO: the maintainer. The window, the redis db in the brief, the gate slot: the lead. The row and the mint: the lead. The LG: the
  executor. A11: the auditor.
- `PL-1856` is not edited. Its Slice B row in that plan stands as filed, and the roadmap's row for this slice says it carries B.
- FD-1723's FR-7 row is a named exception in triage2 §4, not here.

## Self-review

1. **Every cite was read** at `2f108b1e`; `PL-1856`'s moved paths are corrected. 2. **Requirements by id**, no range. 3. **Placeholders:** `_unenforced_total`'s
body is left to R0's read, with both forms named. 4. **Each limb's red is a mutation or a planted case,** since these tests assert behaviour believed to hold;
an unmutated red is A2. 5. **Calendar:** 12 Nov 2026 is a Thursday, 11 Nov a Wednesday.

*(Dated line, 2026-11-06, by the executor at the mint, on the lead's calls in to-lead "2026-11-06 00:01:53 GMT" (e): the "after A" ordering the plan assumed had no technical ground and lapsed. G ran single, alone, for the auditor's reason: R4's autouse guard sits under the 50 ms client timeout at load. That is an inference, unmeasured, and cheap to respect. The plan's wording that T1 "fails on the hash" is not met as worded; the requirement is met (LG-2052, Audit). SL-2051 is closed at this PR's audit commit.)*
