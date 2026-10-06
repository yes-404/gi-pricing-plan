---
id: PL-1447
family: plan
kind: leaf
title: WK-673 — FD-1420 fix, a lookup step reads the row in force as at its declared date (FR-221, FR-69): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-06            # original date 2026-10-05, set at the draft; minted 2026-10-06
owner: planner
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1374, RL-1313, RL-1263, SL-1409, PL-1408, PL-1403]
---

# PL-1447 — WK-673: the FD-1420 fix, a lookup step reads the row in force as at its declared date, leaf plan

*(Minted 2026-10-06 as PL-1447 from working id 9688, in the B1 batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

Filed under working id 9688 (this plan) and slice working id 9685 (its `SL-` row under WK-673 in
[`../roadmap.md`](../roadmap.md), `draft`). The lead reserved both. The finding is ~~FD 9707
(working id, draft PR #1132 at `9e51cbe8`)~~ FD-1420 (minted from #1132; see the pre-mint delta below). Everything below was measured at `origin/main`
`caa4e411a9c07a389cf47092a923c7761b2b92dc` on 2026-10-05, unless a line says otherwise.

## Delta, 2026-10-05 (after 19:36:07 BST, pre-mint): working ids re-pointed to minted ids

This plan is still an unmerged draft. This delta records one decision and every edit it makes.
The decision is the lead's, logged at 19:36:07 BST on 2026-10-05 in `mint-queue-2026-10-05.md`,
on the maintainer's (by delegation) instruction of about 19:34 BST to make the pre-mint fixes.
The edits change citations only. No scope, task, decision point, write-set path or acceptance
item changes.

1. **The hyphen form of FD 9888 → the space form `FD 9888`** (§ "Write set, and its
   contention", the open-PR table, row #972). The old text is replaced, not struck, because
   the audit reads struck text and the hyphen form is what it refuses.
   9888 is the working id of #972, which has not minted. PL-1314's residual note says so: "It is
   recorded as the LOW finding #972 (FD working id 9888, owner WK-1178), cited as prose until it
   mints." The hyphen form cited an unminted id (audit check 32). The id is **not** FD-1317:
   FD-1317 is the finding that rating condition and `clamp_bounds` strings are never validated.
2. **FD 9707 → FD-1420** (minted from #1132), at each citation. In prose, the old text is struck
   in place. Where the text is front matter, the H1 heading, or text the executor writes
   verbatim, a strike would be copied, so the text is replaced and listed here: the front-matter
   `title`; the H1; Task 1 Step 1's module docstring; Task 2 Step 3's replacement docstring
   paragraph; and the four commit messages the plan gives the executor (Task 1 Step 4, Task 2
   Step 5, Task 4 Step 8, Task 5 Step 3), which the executor writes after FD-1420 has minted.
   The filename keeps its working-id slug until the mint.
   **Left as written:** the verbatim quotes of dated entries in § "The decisions this plan rests
   on, quoted" (the **DP-1** item's item 20, the item 22 it quotes for DP-2, and the
   **Severity and order** item with its "Severity signals" quote), and the dated amendment
   line in § "Spec text T1", which quotes the text the ruling adopts.
   The commit messages were left as written at `b8b7d1bf`. The lead's correcting entry of
   19:36:58 BST on 2026-10-05 in `mint-queue-2026-10-05.md` supersedes the 19:36:07 entry's
   "commit-message text in the plan is listed and left" and re-points them. It names two of
   the four; the lead applied it to all four, because the other two are the same class.
3. **PL 9716 → PL-1419** (minted from #1127), struck in place in the write-set table's header.
4. **`../roadmap.md`, the SL-1448 row:** its heading, its `title` and its first paragraph cite
   FD 9707. Each is a citation, not a quote, and each is re-pointed to FD-1420 the same way:
   struck in the heading and the paragraph, replaced in the `title` field.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`: every reward test is seen red, by its stated cause, before the code that turns it green.
> - `python-test`: the `req` marker and negative tests.
> - `python-package`: pricing-core stays free of FastAPI and the database.
> - `fastapi-service`: Task 4's HTTP tests only.
> - `spec-change`: Task 5, the FR-221 text verbatim from the ruling.
> - `dev-commands`: the two-half gate, and `uv sync --all-packages` in a fresh worktree.
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

A `lookup` step returns the payload of the one row whose half-open window
`[effective_from, effective_to)` contains the quote's declared date. It does so on every
scoring path: `POST /api/v1/score`, `POST /api/v1/score/compare`, and the batch path
(`POST /api/v1/score/batch` → `score.batch` Job → `score_batch`). Today it returns the first
row for the key, whatever the date.

**Cause, read from the owning module.** `_decision_table_node`'s `lookup` branch
(`packages/pricing-core/src/pricing_core/rating/runtime.py:246-253`) builds one rule per
reference row. The only input it reads is the row's `key` (`i0`), under `"hitPolicy": "first"`
(`:264`), and it never reads `as_at`, `effective_from` or `effective_to`. The module docstring
says so itself (`:27-35`). The rows reach the bundle from `rows_as_at(..., as_at=None)`
(`backend/src/app/platform/rating_versions.py:519-526`), which orders them by key and then
by `effective_from` (`backend/src/app/platform/reference.py:521`). So **on every key with
more than one row, every quote is priced on the oldest row.** `lookup_as_at`
(`packages/pricing-core/src/pricing_core/data/reference.py:27`) implements the right rule,
but no scoring code calls it. All three paths evaluate the same `CompiledBundle.decision`,
built by `load_bundle` → `to_wire` (`runtime.py:646`), and the maintainer (by delegation) confirmed that no
upstream filter exists on any path (the entry quoted under DP-1 to DP-3, "Severity signals").

## The decisions this plan rests on, quoted

All three blocking decision points are decided, by the maintainer (by delegation), in
`~/gi-pricing-plan.local/channel/to-lead.md`. Each is cited by its entry header:

- **DP-1**, entry "2026-10-05 13:15:53 BST — DECISIONS 17–21 (PL-1452 DP-S3-2/3/6; FD-1420
  DP-1; RL-1428 follow-ups)", item 20: "FD-1420 DP-1: OPTION (a). `as_at` may name only
  `effective_date` or a declared `date` input. It is checked at compile (the named input's type
  is date, else refused naming it) AND at run time (the value is a strict ISO calendar date
  YYYY-MM-DD; an offset or datetime string, or a malformed one, is refused, never silently
  missed). Red first: the offset-string and malformed cases are tests."
- **DP-2**, entry "2026-10-05 13:20:26 BST — DECISIONS 22–27; severity signals for the four gap
  findings", item 22: "PL-1447 DP-2 (FD-1420's window): OPTION (a), in-graph per-rule
  `date($) >= date(from) and date($) < date(to)` (spiked on zen 0.53.0). Conditions: an
  open-ended window (no `to`) is handled and tested; overlapping windows for one key are REFUSED
  at table save or bundle compile (else "first match wins" returns by another door), with a
  named code and a test; boundary tests at `from` and at `to` (half-open), red first."
- **DP-3**, entry "2026-10-05 13:20:52 BST — DECISION 28 (PL-1447 DP-3): OPTION (a), with a
  pinning test": "DP-1's strict run-time check applies to `date` inputs named by `as_at`;
  QuoteContext.effective_date is NOT changed (no model-schema or contract change). Condition:
  the slice adds tests that PIN today's parsing of effective_date on /score: a plain YYYY-MM-DD
  is accepted; a midnight datetime with an offset yields its local calendar date (the row chosen
  is that date's); a non-midnight datetime and a malformed value are refused 422. If any of
  those does not behave as the lead describes, stop and bring it back: then (b) is reopened."
- **Severity and order**: entry "2026-10-05 13:11:05 BST — FD-1420 (B3, as_at lookup ignores
  effective dating): HIGH, provisional on the upstream-filter check; its fix goes FIRST in lane
  B after SL-1409". Items 2 and 3 say: owner WK-673, deadline before the P2 exit demo, and lane
  order. The 13:20:26 entry's "Severity signals" adds: "FD-1420 (#1132): HIGH CONFIRMED (no
  upstream filter on /score, /compare or batch)".

**Owner discrepancy, for the lead.** FD-1420's draft (#1132 @`9e51cbe8`, §Finding) proposes
owner WK-1178. The maintainer's (by delegation) 13:11:05 entry, item 2, says WK-673. This plan and its slice row
follow the maintainer (by delegation). The finding's mint reconciles its owner line.

## Status

`draft`. Every decision point is decided (above). DP-4 is non-blocking and keeps its
recommendation unless a ruling says otherwise. The plan moves to `active` only through a
separate activation PR, once every activation need below holds. That PR carries this plan's
status flip and the `SL-` row's.

### Activation needs, in order

1. **FD-1420 minted** (#1132). It is in the maintainer's (by delegation) first finding batch (13:13:32 BST entry,
   item 5).
2. **A ruling record (`RL-`) carries DP-1 to DP-4 and text T1** (§"Spec text T1"), because a
   decision lands as a dated artifact (`CLAUDE.md` §12). The decision-maker writes it from the
   three entries quoted above. If its text differs from this plan, the ruling wins, and the
   dispatch record names each difference.
3. **This plan made `active`** by a dated line in the activation PR.
4. **Lane.** It runs in lane B, after `SL-1409` merges. It goes **before PL-1454** (#1113, the
   NFR-489 remedy) if this plan is active first. If PL-1454 is dispatch-ready and this plan is
   not, PL-1454 goes first and this fix takes the next free build lane. The maintainer's (by delegation) priority
   rule (13:12:56 BST entry) also lets this fix, as a HIGH G2 blocker, take the first build
   lane that frees once it is active. **It never runs concurrently with PL 9776** (#1051, the
   F35 remedy): both edit `_decision_table_node`, the `runtime.py` docstring and
   `ALGORITHM_CHECKS` (RL-1263; §"Write set"). The dispatch record names which goes first.
5. **The dispatch GO**, with Task 0 re-run at dispatch.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means the named test was run at the slice's base and failed **for the stated cause** before
the code that turns it green. A failure with the right status and a different cause is a plan
defect ([`README.md`](README.md) rule 2). The ledger records each red with its failure line as
printed.

1. **The pricing-core reproduction is red first, then green.** `uv run pytest -q
   packages/pricing-core/tests/test_rating_lookup_as_at.py` passes. At the base, these failed
   with `AssertionError: the superseded row's rate returned`:
   - `test_score_one_prices_on_the_row_in_force[2026-01-01-at-from]`
   - `[2026-06-01]`
   - `[2099-01-01-open-ended]`
   - `test_score_batch_prices_on_the_row_in_force`

   `test_score_one_misses_before_every_row` (2019-12-31) failed with `Failed: DID NOT
   RAISE`. The first window's controls were green at the base: `[2020-01-01-at-from]` and
   `[2025-12-31-before-to]`. Planning time saw all of this (§"Task 0 at planning time", run 7).
2. **The three HTTP paths are red first, then green.** `uv run pytest -q
   backend/tests/test_score_as_at.py` passes against Postgres and MinIO (fixtures `database`
   and `blob_store`; the tests skip if either is down, and a skip is not a pass). At the base,
   each of these failed with `AssertionError: the superseded row's rate returned`:
   - `test_score_prices_on_the_row_in_force`
   - `test_score_compare_prices_both_sides_on_the_row_in_force`
   - `test_score_batch_job_prices_on_the_row_in_force`
3. **DP-1, compile half, is red first.** In `test_rating_lookup_as_at.py`, each of these
   compiled at the base (`Failed: DID NOT RAISE`) and is refused after the fix:
   - `test_as_at_naming_a_non_date_input_is_refused_at_compile` (`RATING_TYPE_MISMATCH`)
   - `test_as_at_naming_an_undeclared_value_is_refused_at_compile` (`RATING_GRAPH_UNRESOLVED_REF`)
   - `test_a_declared_effective_date_must_be_date_typed` (`RATING_TYPE_MISMATCH`)

   The error message names the step and the `as_at` value.
4. **DP-1, run-time half, is red first.**
   `test_a_malformed_as_at_value_is_refused_not_missed` is parametrised over
   `2026-01-01T00:30:00+01:00`, `2026-01-01T00:00:00`, `2026-1-1`, `20260101`, `2026-02-30`
   and `nonsense`. At the base, each case scored `quoted` (`Failed: DID NOT RAISE`). After the
   fix, each is refused with `INPUT_CONTRACT_VIOLATION`, and the message names the step.
   `test_an_input_shadowing_effective_date_is_checked` covers an undeclared input
   `effective_date` carrying an offset string. It is red first and refused the same way
   (§"A finding from planning").
5. **DP-2's boundary and open-ended conditions** are covered by Acceptance 1:
   - `from` of each row: `2020-01-01` and `2026-01-01`.
   - `to` of the old row: `2026-01-01` returns the new row; `2025-12-31` returns the old one.
   - The open-ended row: `2099-01-01`.
   - Before every row: `2019-12-31` gives `REFERENCE_LOOKUP_MISS` under `on_miss: error`.
6. **DP-2's overlap condition** is satisfied by the refusal at table save, which exists at the
   base: `REFERENCE_INTERVAL_OVERLAP` (409), raised at
   `backend/src/app/platform/reference.py:174` from the exclusion constraint added by
   migration `5bfde19b6085`. Its test is `backend/tests/test_api_datasets.py:389`. The slice
   adds `test_overlapping_windows_are_refused_at_table_save_with_their_code` to
   `test_score_as_at.py`. It loads the fixture key's two windows overlapping and asserts that
   code. It is green at the base, by design, because it pins the door DP-2 names. The ledger
   records it as a pin, not a red.
7. **DP-3's pins.** `test_score_as_at.py::test_effective_date_parsing_is_pinned` asserts, on
   `/score`:
   - `2026-06-01` is accepted.
   - `2026-01-01T00:00:00+01:00` is accepted and prices on the **2026-01-01** row (`180000`).
     That is the local calendar date, not UTC.
   - `2026-01-01T00:30:00+01:00` and `2026-13-01` are refused `422` with `code ==
     "VALIDATION_FAILED"`.

   The midnight-offset case is red first (`130000` at the base, by FD-1420's cause). The
   other three are pins. If any pin fails at the base, **stop and bring it back to the lead**
   (DP-3's condition).
8. **The registry follows RL-1313 DP-G5 (i).** `(RatingLookupStep, "as_at")` is in
   `EXPRESSION_FIELDS` and not in `NON_EXPRESSION_FIELDS`
   (`packages/pricing-core/src/pricing_core/rating/authored.py`).
   `test_rating_authored_fields.py` passes. Its assertion at `:189` is replaced, not deleted.
9. **No recorded price moves.** Task 0's script prints `TOTAL lookup_algorithms=0` at dispatch,
   or it lists every algorithm and its re-priced quotes in the ledger. Its three code greps
   print the counts in §"Task 0 at planning time" (lookups in golden, seed and demo code: 0).
   `backend/tests/test_demo_rating_evidence.py` and `backend/tests/test_regression_runs.py`
   pass unchanged.
10. **The whole suite is green, both halves**, per `dev-commands`: `uv run ruff check . && uv run
    mypy && uv run lint-imports && uv run pytest -q`, `python3 scripts/audit-docs.py`,
    `uv run python scripts/req-coverage.py`, `uv run python scripts/generate-contracts.py
    --check` (no diff: no shape changes), and the frontend half. The four fixtures that named a
    non-date `as_at` (Task 3) now name `effective_date`, and their tests pass with their
    original expected values.
11. **NFR-499 holds for the new refusal.**
    `test_quote_input_raise_sites.py::test_every_quote_input_raise_site_has_a_sentinel_case`
    passes with `_check_as_at_values` in `_INPUT_FREE`.
    `test_rating_lookup_as_at.py::test_the_as_at_refusal_never_carries_the_value` passes, and
    was red at the base with `Failed: DID NOT RAISE`.

## Global Constraints

- Money is integer minor units, never float (`CLAUDE.md` §7); the tests assert `payable_premium_minor` as `int`.
- `pricing-core` imports no FastAPI, SQLAlchemy or Redis (`CLAUDE.md` §2); `uv run lint-imports` holds it.
- No hand-written shape that exists in `model-schema` (`CLAUDE.md` §2). This slice adds no shape and changes none: `generate-contracts.py --check` stays clean.
- No pandas (`CLAUDE.md` §3); the batch test builds its frame in Polars.
- Engine: `zen-engine` 0.53.0 (`uv.lock:2786-2787`). The window expression was verified on that version only.
- Every new test carries `@pytest.mark.req("FR-221")`, plus `FR-69` on the boundary cases and `FR-255` on the miss case (`python-test`).

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | FR-221 | A `lookup` evaluates reference data as at the declared date; the date source is explicit and is `effective_date` or a `date` input (DP-1, text T1) | `req("FR-221")` on every new test |
| `01` | FR-69 | The half-open `[effective_from, effective_to)` window; overlap refused at load (DP-2's overlap door) | `req("FR-69")` on the boundary cases and the overlap pin |
| `01` | FR-71 | A reference lookup is evaluated as at a declared date, not "now" | covered by the FR-221 tests; no extra marker |
| `03` | FR-255 | A key with no row in force is a reference miss, typed per quote; a malformed date is a contract violation, never a miss | `req("FR-255")` on the miss case and the run-time refusals |
| `03` | FR-213 | Input-contract violations are refused per quote (the run-time strictness, DP-1) | `req("FR-213")` on the run-time refusals |
| `03` | FR-227 | Type checks on the authored algorithm (the compile half of DP-1 reuses `RATING_TYPE_MISMATCH`) | `req("FR-227")` on the compile refusals |
| `03` | FR-274 | The authored-field registry: `as_at` moves to the expression fields (RL-1313 DP-G5 (i)) | existing test, assertion replaced |
| `03` | FR-250, FR-262, FR-253 | The three paths: `/score`, `/score/compare`, batch. Behaviour is unchanged apart from the row chosen | the Task 4 HTTP tests also carry these markers |

### Task 0 at planning time (measured, not asserted)

**Run 1: the window expression on the locked engine.** At 2026-10-05 13:16 BST, on
`zen-engine` 0.53.0, the planner ran a scratch decision table:
`/home/puzhenhao1989/.claude/jobs/6cad77f9/tmp/spike.py`, scratch, not committed.

- Key-only rules over OLD/NEW returned `OLD` at 2026-06-01. That is FD-1420.
- The rule `date($) >= date('2025-01-01') and date($) < date('2026-01-01')` for OLD, with
  `date($) >= date('2026-01-01')` for NEW, gave:
  - `2024-12-31` → no match
  - `2025-01-01` → OLD
  - `2025-12-31` → OLD
  - `2026-01-01` → NEW
  - `2026-06-01` → NEW
- `2026-01-01T00:30:00+01:00` → **OLD**: ZEN's `date()` converts to UTC. That is DP-1's reason.
- `nonsense`, and a missing field, each gave **no match**: a silent miss. That is also DP-1's
  reason.
- `$ < '2026-01-01'` (string comparison) gave no match, as the module docstring says.

**Run 2: the reproduction as tests, at the base, through `compile_bundle` → `load_bundle` →
`score_one` and `score_batch`.** At 13:19 BST, the planner ran
`.venv/bin/python -m pytest` on `/home/puzhenhao1989/.claude/jobs/6cad77f9/tmp/test_spike_as_at.py`
(scratch, the code of Task 1 Step 1). Output, abridged to the failure lines:

```text
FAILED ::test_score_one[effective2-180000] - AssertionError: the superseded row's rate returned
FAILED ::test_score_one[effective3-180000] - AssertionError: the superseded row's rate returned
2 failed, 3 passed in 8.00s
```

`effective2` and `effective3` are 2026-01-01 and 2026-06-01: each priced `130000` against
`180000` in force. The batch row for 2026-06-01 printed
`'outputs_json': '{"payable_premium_minor": 130000}'`.

**Run 3: the fix, monkeypatched over `_decision_table_node`** (the code of Task 2, scratch
file `test_spike_fix.py`). All 10 passed:
- 2019-12-31 → `REFERENCE_LOOKUP_MISS`
- 2025-12-31 → `130000`
- 2026-01-01 → `180000`
- 2026-06-01 → `180000`
- batch 2026-06-01 → `180000`

The same run probed `QuoteContext.effective_date` (`model_schema/scoring.py:107`, `date`),
both through `model_validate` and through `model_validate_json`:

| Value | Pydantic |
|---|---|
| `2026-01-01T00:00:00` | → `2026-01-01` |
| `2026-01-01T00:00:00+01:00` | → `2026-01-01` (local date) |
| `2025-12-31T23:30:00-01:00` | refused |
| `20260101` | refused |
| `2026-01-01T00:30:00` | refused |

`/score` maps a refused body to `422 VALIDATION_FAILED` (`backend/src/app/errors.py:466-490`).
This is the behaviour DP-3 pins.

**Run 7: Task 1's module, as this plan writes it, at the base.** At 13:3x BST, the planner
extracted Task 1 Step 1's and Step 2's code blocks from this file with a script, made no
edits other than the one import line Step 2 says to move, and ran it with
`.venv/bin/python -m pytest -rA`. The scratch module is
`/home/puzhenhao1989/.claude/jobs/6cad77f9/tmp/test_rating_lookup_as_at.py`. Result:
`16 failed, 2 passed in 4.28s`.

- **Passed:** the two first-window controls.
- **Failed with `AssertionError: the superseded row's rate returned`:**
  - `[2026-01-01-at-from]`, `[2026-06-01]`, `[2099-01-01-open-ended]`
  - the batch test
  - `test_a_date_input_named_by_as_at_selects_the_row`
- **Failed with `Failed: DID NOT RAISE`:**
  - the miss test
  - the three compile refusals
  - all six malformed values
  - the shadowing test

Every red has the cause Task 1 Step 3 predicts.

**Run 8: Tasks 2 and 3, applied to the planning worktree's tree and then restored.** From
about 13:28 BST, a script inserted this plan's own Task 2 and Task 3 code blocks into
`runtime.py`, `compile.py`, `score.py` and `authored.py`. Nothing was committed. The four
files were restored with `git checkout --` at 13:37 BST, and `git status` then showed only
this plan and `docs/roadmap.md`.

- Task 1's module: **18 passed**. Every red turned green, and both controls stayed green.
- A targeted run of five files, about 13:35 BST: `15 failed, 121 passed`. The tail printed
  seven of the failures, all Task 3 work:
  - Four `lookup` cases of `test_rating_pin_membership.py`, whose fixtures still named
    `channel` or `veh` (Task 3 Step 4).
  - `test_every_non_expression_field_carries_a_reason` (Step 3).
  - `test_the_enumerator_yields_every_authored_string_with_its_field`. Its expected list
    lacks the new `as_at` entry (Step 3).
  - `test_no_check_module_reads_an_authored_field_off_a_step[pricing_core.rating.compile]`.
    The draft compile check read `step.as_at`; Step 1 now reads through the enumerator.

  An earlier `-x` run, at about 13:30 BST, stopped on
  `test_every_quote_input_raise_site_has_a_sentinel_case`, which named the new
  `_check_as_at_values` site (Step 3a). **The other eight failures were not captured.**
  Task 3 Step 5 is where the executor sees the whole list. A failure outside the sites Task 3
  names is a stop.
- **Not evidence:** a run of the whole `packages/pricing-core` suite, about 13:31–13:34 BST,
  printed `623 passed`, with no failures. That contradicts the targeted run on the same tree,
  so no figure here rests on it. It also broke the lead's standing rule of 13:35 BST (a
  planner never runs a full suite, and runs a targeted file only after both gate slots probe
  free). At 13:35:39 BST `gate-1` was held (SL-1409's gate) and the load average was 14.55.
  The planner reported the breach to the lead at once and ran nothing more.

**Run 4: cost.** These figures are indicative only, not an NFR measurement, taken on a shared
box at load 2.5–3.7. Scratch file `spike_perf.py`: one decision table, 6,000 rules, the
matching key last, 400 evaluations after 50 warm-ups, three runs.

| Rules | p50 | p99 |
|---|---|---|
| key-only | 3.1–3.9 ms | 5.9–14.3 ms |
| windowed | 3.3–4.4 ms | 8.3–11.9 ms |

The two cannot be told apart at this noise level. NFR-489's harness (`scripts/bench-rating.py`
`:309`, `:635`) pins no reference table, so this slice does not move PL-1454's measurement.
`CompiledBundle.content_hash` is `Bundle.content_hash` (`runtime.py:673`), not a hash of the
wire graph, so PL-1454's steady-state key is unchanged too.

**Run 5: exposure over every local database.** At 2026-10-05 12:20:47 UTC (13:20:47 BST), on
the compose server `gi-pricing-postgres-1`, the planner ran the script of Task 0 Step 1. Its
last line, verbatim: `DATABASES=93 TOTAL lookup_algorithms=0 multi_row_keys=2`.

- Three databases have no rating tables (`na`).
- The two keys with more than one row are in `gipricing_wt-d9d13-redo` and
  `gipricing_wt-paths-d9-d13` (test leftovers). No algorithm reads either.

**Run 6: golden quotes and the seed.** Commands run from the worktree root, with hit counts:

| Command | Hits | What the hits are |
|---|---|---|
| `grep -rnI '"lookup"' examples scripts backend/src/app/demo backend/src/app/api/demo.py backend/tests/test_demo_rating_evidence.py backend/tests/test_demo_command.py backend/tests/test_demo_postconditions.py backend/tests/test_demo_guide.py \| wc -l` | **0** | — |
| `git grep -nIi 'golden' -- backend/tests packages/pricing-core/tests packages/model-schema/tests examples \| grep -ci 'lookup'` | **0** | — |
| `git grep -nI '"type": "lookup"' -- ':!docs' ':!*.md'` | 10 | the four evaluated fixtures in Task 3, and validate-only or compile-only fixtures that already name `effective_date` |

- The freMTPL2 demo algorithm is input → expression → output, with `"reference_tables": []`
  (`examples/fremtpl2/model.py:323`, `:334-343`).
- The golden quotes in `backend/tests/test_regression_runs.py:152-206` use
  `_minimal_algorithm`, which has no lookup.

**So no golden quote and no seeded price changes.** The regression evidence is the unchanged
pass of those suites (Acceptance 9), plus the new reds.

### A finding from planning: an input can shadow the stamped date

`score_one` builds the engine context as
`{"effective_date": ctx.effective_date.isoformat(), "purpose": ctx.purpose, **ctx.inputs}`
(`score.py:910-912`, and `_score_context_sync` at `:1066-1068`). `_validate_inputs` tolerates
undeclared extra keys (`:334-337`). So an input named `effective_date` overrides the stamped
date, with any string, and ZEN reads that string.

The run-time check of DP-1 therefore reads **the value in the merged context** under each
lookup's `as_at`. On the stamp alone, that value is a strict ISO date by construction. With a
shadowing input, it is whatever the caller sent, and the check refuses it. This stays inside
DP-3 (a): `QuoteContext` is unchanged.

Whether an input may carry a stamped name at all is FD-1374's class: FR-246's declared-inputs
rule, remedy PL 9776 (working id), #1051. That remains its owner. **This plan does not decide
it.** It only refuses the shadowed value the lookup would read.

### Write set, and its contention (`RL-1263`)

RL-1263: "Two concurrent build slices may not both change the same **existing** function,
class, method, spec section, or policy table … **Any other shared path serialises** unless the
lead's dispatch record names the path and the check showing that no existing definition is
edited by both." The JSON keys are under `guards.parallelism.build_slices_across_works` in
`docs/process/delivery-process.core.json`: `no_shared_files` `:389`, `other_shared_path`
`:417`, `generated` `:394`, `registry_exempt_append_only` `:391`.

| Path | This slice | SL-1409 (lane B, in flight) | SL-1391 (lane A, ~~PL 9716~~ PL-1419, #1127) | WK-675 S2 (lane C, PL 9713, #1131) | PL-1454 (#1113) | Class |
|---|---|---|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | edited: `_decision_table_node` (`lookup` branch, `:240-253`), module docstring (`:22-35`); added: `_as_at_window` | — | — | — | reads `CompiledBundle.content_hash` (`:673`) only | none |
| `packages/pricing-core/src/pricing_core/rating/compile.py` | added: `_check_lookup_as_at`; edited: `ALGORITHM_CHECKS` (`:359-363`, one entry appended) | — | — | — | — | none |
| `packages/pricing-core/src/pricing_core/rating/score.py` | added: `_check_as_at_values`; edited: `score_one` (`:876`, one call), `_score_context_sync` (`:1045`, one call) | — | — | — | — | none |
| `packages/pricing-core/src/pricing_core/rating/authored.py` | edited: `EXPRESSION_FIELDS` (`:44-50`), `NON_EXPRESSION_FIELDS` (`:60-64`, entry removed) | — | — | — | — | none |
| `packages/pricing-core/tests/test_rating_lookup_as_at.py` | added (new module) | — | — | — | — | none |
| `packages/pricing-core/tests/test_rating_runtime.py` | edited: `test_lookup_step_wire_translation_matches_by_key` (`:435-475`) and the comment at `:427-432` | — | — | — | — | none |
| `packages/pricing-core/tests/test_rating_score.py` | edited: `test_a_reference_lookup_miss_is_refused` (`:383-`, `as_at` at `:399`, rows at `:411`) | — | — | — | — | none |
| `packages/pricing-core/tests/test_rating_pin_membership.py` | edited: `_lookup_algo` (`:58-68`, `as_at` `:62`), `_veh_algo` (`:228-`, `as_at` `:232`) | — | — | — | — | none |
| `packages/pricing-core/tests/test_rating_authored_fields.py` | edited: `test_every_non_expression_field_carries_a_reason` (`:187-190`), `test_the_enumerator_yields_every_authored_string_with_its_field` (`:103-116`) | — | — | — | — | none |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` | edited: `_INPUT_FREE` (`:62-79`, one entry added) | — | — | — | — | none found; any slice adding a pricing-core raise site edits the same dict (registry: append; the second to merge re-gates) |
| `backend/tests/test_score_as_at.py` | added (new module) | — | — | — | — | none. PL-1454 reads `backend/tests/test_score.py`, which "must stay green" (its plan `:267-268`); this slice does not edit it |
| `docs/specs/03-rating-engine.md` | edited: the FR-221 row (`:107`, §3.2), a dated amendment appended to the row (text T1) | — | §3.3 (FR-231 `:122`), §4.2, §5.1, §5.2 | §3.1, §3.4 (after FR-243), §5.1, §8 | only under its DP-3 (b) or DP-5 | **shared file, distinct sections**: allowed only if the dispatch record names the path and the check that no section is edited by both (RL-1263; `other_shared_path`). PL 9713 `:242` cites FR-221 ("a `lookup` step's `as_at` is a required, explicit field"). T1 keeps that clause and narrows the values, so S2's inspector should offer only `effective_date` and `date` inputs. That is a note for S2's dispatch, not an edit to S2 |
| `docs/roadmap.md` | added: the SL-1448 row (plan PR only) | — | #1127 edits the SL-1391 row (`:828`) | #1131 inserts after `:1054` | #1113 inserts after `:1436` | registry (append, distinct rows); the second to merge re-reads |
| `docs/INDEX.md`; the slice's ledger | regenerated; added | every PR | every PR | every PR | every PR | `generated` |

**A fifth plan writes the same definitions: PL 9776 (working id, `draft`, #1051, the F35
remedy, WK-1178).** Its write set (its plan `:494-516`, read on `origin/wk1178-f35-leaf-plan`
on 2026-10-05) edits:

- `_decision_table_node`, turning `passThrough` off (`:503`).
- The `runtime.py` module docstring's rule 3 (`:503`).
- `ALGORITHM_CHECKS`, appending `_check_declared_reads` (`:500`, `:1131-1132`; RL 9771, #1060,
  `:152-153`).
- `test_rating_score.py`'s `_algorithm_payload` and
  `test_trace_true_returns_a_populated_trace_and_the_identical_premium` (`:509`). That is not
  this slice's test, `test_a_reference_lookup_miss_is_refused`.

The first three are **the same existing definitions** this slice edits, so under RL-1263 the
two **serialise**. Neither is dispatched today. Whichever merges second rebases and re-reads
`runtime.py` and `compile.py`. The `ALGORITHM_CHECKS` append is the registry form (append;
the second to merge re-gates), but `_decision_table_node`'s body is not. The dispatch record
names the order.

**Open PRs read, at their heads on 2026-10-05 13:2x BST, none of which rules on this
slice's subject beyond what is quoted:**

| PR | What it is | Relation to this slice |
|---|---|---|
| #1132 | FD-1420 itself | — |
| #1051 / #1060 | PL 9776 and its ruling | above |
| #972 | FD 9888 | its fix edits `_reraise_engine_failure`, not on this list |
| #1059 | FD-1437 | a sweep of bare `ValueError` raises in the check functions; no write set yet |
| #1061 | RL-1438 | `test_rating_compile_bundle.py:234` only |
| #1055 | RL 9767 | moves `ValidationIssue` out of `compile.py` and keeps the name importable; if it lands first, Task 3 Step 1 imports it from its new home |
| #1126 | RL-1449 | appends an OQ row to `03` after `:1369` |
| #1048 | OQ-1453 | edits the NFR-489 row (`03:1330`) |

No open PR changes a file under `packages/` (`gh pr list --state open --limit 80 --json
number,headRefName,files`), except the dependabot PRs, which touch `uv.lock` only. The
only `status: active` slice row on `main` is SL-1409.

### Size

Small: about half an executor day. Five tasks after Task 0. One two-half gate run, which needs
a gate slot under `RL-1263`. The HTTP tests need Postgres and MinIO. The slice takes no NFR
measurement, so it need not run exclusive.

## Decision points

DP-1 to DP-3 were blocking, and each went to the lead as soon as it was found. The maintainer (by delegation)
decided all three (quoted above). DP-4 is non-blocking. The options are kept so a reader can
see what was weighed. The decisions' text governs.

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | What may `as_at` name, and how strict is its value? A `date` input is checked only to be a string (`score.py:366-369`); ZEN's `date()` converts an offset value to UTC and silently misses a malformed one (Task 0 run 1) | (a) `effective_date` or a declared `date` input, checked at compile, and at run time a strict `YYYY-MM-DD`; (b) any input, truncated to a date in the graph; (c) accept datetimes and compare in UTC | (a) | **DECIDED (a)** by the maintainer (by delegation), 13:15:53 BST item 20 | Tasks 1, 2, 3, 5 |
| **DP-2** | The window mechanism (FD-1420's Disposition sends it to a DP) | (a) in-graph per-rule `date($)` tests; (b) a numeric-ordinal expression node feeding the table; (c) a host-side pre-filter (not possible: the decision is built once per bundle and cached, while `as_at` varies per quote) | (a) | **DECIDED (a)** by the maintainer (by delegation), 13:20:26 BST item 22, with conditions: open-ended window tested; overlap refused at save or compile with a named code and a test; boundary reds at `from` and `to` | Tasks 1, 2 |
| **DP-3** | Does DP-1's run-time refusal reach `QuoteContext.effective_date`? | (a) no, the strict check applies to `date` inputs named by `as_at` (here: to the merged-context value, §"A finding from planning"), and `/score`'s parsing is pinned; (b) make the field strict: a model-schema and contract change | (a) | **DECIDED (a)** by the maintainer (by delegation), 13:20:52 BST decision 28, with the pinning tests (Acceptance 7) and a stop if a pin fails | Tasks 3, 4 |
| **DP-4** | DP-1's compile check: which codes, and where it runs | Codes: (i) `RATING_TYPE_MISMATCH` for a declared input of another type, and `RATING_GRAPH_UNRESOLVED_REF` for an undeclared name other than `effective_date`; (ii) one new code (a spec change to `03`'s owned codes, `:928-931`). Place: (p) appended to `ALGORITHM_CHECKS`, so it runs at save (`validate_algorithm`) and again at compile (`compile_bundle` re-runs it, `compile.py:573-583`); (q) in `compile_bundle` only | (i) and (p). Both codes are already `03`'s, with matching meanings (`03:844-845`). Running at save tells the author earliest, as FR-227's result-type check does at create. Every committed algorithm that names `effective_date` still saves: `backend/tests/test_rating_algorithms.py:38`, `:86`, `test_rating_compile.py:36`, `:84`, `test_rating_compile_bundle.py:47` | **planner; non-blocking.** The ruling of activation need 2 confirms or changes it | Task 3 |

### Spec text T1 (proposed for the ruling; applied verbatim in Task 5)

A dated amendment appended to the FR-221 row's cell (`docs/specs/03-rating-engine.md:107`),
after its existing sentence:

> *(Amended 2026-10-05, FD 9707; DP-1 to DP-3 decided by [the maintainer (by delegation)].)* **`as_at` names
> `effective_date` — the quote's stamped date — or a declared `date` input, and nothing else.**
> Anything else is refused when the algorithm is validated: a declared input of another type
> with `RATING_TYPE_MISMATCH`, and an undeclared name with `RATING_GRAPH_UNRESOLVED_REF`. **The
> value read is a calendar date, `YYYY-MM-DD`.** A datetime, an offset, or a malformed value is
> refused per quote with `INPUT_CONTRACT_VIOLATION`, never treated as a miss. **A row is in force
> when `effective_from ≤ as_at < effective_to`**: `01` FR-69's half-open interval, where an
> absent `effective_to` is open-ended. A key with no row in force is a reference miss (FR-255),
> resolved by the step's `on_miss`. Overlapping rows cannot reach a bundle: FR-69 refuses them
> when the version is loaded (`REFERENCE_INTERVAL_OVERLAP`).

## Tasks

### Task 0: Preconditions and exposure (no code)

**Files:** none committed. The script lives in the executor's job directory.

- [ ] **Step 1: Re-run the exposure query.** Write the script below (verbatim, Run 5's script)
  to the job's tmp directory and run it with `bash`. Paste its output in the ledger with the
  BST time.

```bash
#!/bin/bash
# PL-1447 Task 0: lookup-step exposure over every gipricing* database on the compose server.
# Per DB: rating algorithms holding a lookup step; reference-table keys with more than one row.
C=gi-pricing-postgres-1
q() { docker exec "$C" psql -U gipricing -d "$1" -Atc "$2" 2>/dev/null; }
tot_alg=0; tot_keys=0; n=0
for db in $(q gipricing "select datname from pg_database where datname like 'gipricing%' order by 1"); do
  n=$((n+1))
  alg=$(q "$db" "select count(*) from rating_algorithms a where exists (select 1 from jsonb_array_elements(a.content->'steps') s where s->>'type'='lookup')")
  keys=$(q "$db" "select count(*) from (select reference_table_version_id, key from reference_rows group by 1,2 having count(*)>1) k")
  [ -z "$alg" ] && alg=na; [ -z "$keys" ] && keys=na
  [ "$alg" != na ] && tot_alg=$((tot_alg+alg)); [ "$keys" != na ] && tot_keys=$((tot_keys+keys))
  echo "$db lookup_algorithms=$alg multi_row_keys=$keys"
done
echo "DATABASES=$n TOTAL lookup_algorithms=$tot_alg multi_row_keys=$tot_keys"
```

  Expected: the last line reads `TOTAL lookup_algorithms=0`. If it is not 0, list each
  algorithm (database, slug, version) in the ledger and tell the lead before Task 2. A
  persisted algorithm re-prices on merge, and that is a recorded-price change this plan
  measured as absent.

- [ ] **Step 2: Re-run Run 6's three greps** (§"Task 0 at planning time"), verbatim. Expect
  `0`, `0` and `10`. A different count is a scope change: report it to the lead.
- [ ] **Step 3: Re-read the open PRs for rulings on this subject.** Run `gh pr list --state
  open` and read any that touch the write set ([`README.md`](README.md) rule 4). Name the
  head SHA you read in the ledger. If the activation ruling's text differs from this plan,
  the ruling governs; record each difference.

### Task 1: The pricing-core reds (Acceptance 1, 3, 4, 5)

**Files:**
- Create: `packages/pricing-core/tests/test_rating_lookup_as_at.py`

**Interfaces:**
- Consumes: `_ctx`, `_FakeResolver`, `_version` from `test_rating_score` and `_ctx_to_row`
  from `test_rating_score_batch`, imported the way `test_rating_pin_membership.py:18-19`
  imports them.
- Produces: the module's `_algo(*, as_at=..., contract=...)`, `_compiled(algo=...)` and
  `_quote(effective, *, extra_inputs=...)`. Task 3 reuses them and Task 4 mirrors them.

- [ ] **Step 1: Write the module.** This code ran at the base as Run 2. Keep its literals.

```python
"""FD-1420: a `lookup` step reads the row in force as at its declared date.

FR-221 and `01` FR-69: the window is half-open, `[effective_from, effective_to)`. DP-1, DP-2
and DP-3 are decided in PL-1447.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

import polars as pl
import pytest
from test_rating_score import _ctx, _FakeResolver, _version
from test_rating_score_batch import _ctx_to_row

from model_schema.rating import Pins
from model_schema.scoring import QuoteContext, QuoteContextOptions
from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_batch, score_one

REF = "reference_table:area@1"
SUPERSEDED = "the superseded row's rate returned"

#: Two windows for one key: OLD until 2026-01-01 (exclusive), NEW from it, open-ended.
ROWS = [
    {"key": "SW1A", "payload": {"area_loading": "1.30"},
     "effective_from": "2020-01-01", "effective_to": "2026-01-01"},
    {"key": "SW1A", "payload": {"area_loading": "1.80"},
     "effective_from": "2026-01-01", "effective_to": None},
]

_CONTRACT = [
    {"name": "base_minor", "type": "int", "nullable": False},
    {"name": "postcode", "type": "string", "nullable": False},
]


def _algo(
    *, as_at: str = "effective_date", contract: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    return {
        "slug": "score-fixture", "version": 1,
        "input_contract": contract if contract is not None else _CONTRACT,
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in_base", "type": "input", "label": "Base", "input_name": "base_minor",
             "on_missing": "error", "produces": "base_minor"},
            {"step_id": "s_in_pc", "type": "input", "label": "Postcode", "input_name": "postcode",
             "on_missing": "error", "produces": "postcode"},
            {"step_id": "s_area", "type": "lookup", "label": "Area loading",
             "reference_table_ref": REF, "key_expr": ["postcode"], "as_at": as_at,
             "on_miss": "error", "consumes": ["postcode"], "produces": "area_loading"},
            {"step_id": "s_expr", "type": "expression", "label": "Apply",
             "expr": "base_minor * number(area_loading)", "result_type": "money_minor",
             "consumes": ["base_minor", "area_loading"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


async def _compiled(algo: dict[str, Any] | None = None) -> CompiledBundle:
    pins = {"rate_tables": [], "models": [], "reference_tables": [REF], "custom_objectives": []}
    version = _version().model_copy(update={"pins": Pins.model_validate(pins)})
    resolver = _FakeResolver()
    resolver._payloads["rating_algorithm:score-fixture@1"] = algo if algo is not None else _algo()
    resolver._payloads[REF] = {"rows": ROWS}
    return load_bundle(await compile_bundle(version, resolver))


def _quote(effective: date, *, extra_inputs: dict[str, Any] | None = None) -> QuoteContext:
    return QuoteContext.model_validate({
        **_ctx().model_dump(), "effective_date": effective,
        "inputs": {"base_minor": 100_000, "postcode": "SW1A", **(extra_inputs or {})},
        "options": QuoteContextOptions(rating_version_ref=_ctx().options.rating_version_ref),
    })


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-69")
@pytest.mark.parametrize(("effective", "price"), [
    pytest.param(date(2020, 1, 1), 130_000, id="2020-01-01-at-from"),
    pytest.param(date(2025, 12, 31), 130_000, id="2025-12-31-before-to"),
    pytest.param(date(2026, 1, 1), 180_000, id="2026-01-01-at-from"),
    pytest.param(date(2026, 6, 1), 180_000, id="2026-06-01"),
    pytest.param(date(2099, 1, 1), 180_000, id="2099-01-01-open-ended"),
])
async def test_score_one_prices_on_the_row_in_force(effective: date, price: int) -> None:
    result = await score_one(await _compiled(), _quote(effective))
    assert result.outcome == "quoted"
    assert int(result.outputs["payable_premium_minor"]) == price, SUPERSEDED


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-255")
async def test_score_one_misses_before_every_row() -> None:
    """`2019-12-31` is before the first row's `effective_from`: no row is in force."""
    with pytest.raises(ValueError, match=r"^REFERENCE_LOOKUP_MISS:"):
        await score_one(await _compiled(), _quote(date(2019, 12, 31)))


@pytest.mark.req("FR-221")
async def test_score_batch_prices_on_the_row_in_force() -> None:
    frame = pl.DataFrame([_ctx_to_row(_quote(d)) for d in (date(2025, 6, 1), date(2026, 6, 1))])
    out = score_batch(await _compiled(), frame.lazy()).collect()
    prices = [json.loads(v)["payable_premium_minor"] for v in out["outputs_json"]]
    assert prices == [130_000, 180_000], SUPERSEDED
```

  The miss case is its own test, because it raises rather than prices. Its red is `Failed:
  DID NOT RAISE`, since the base prices it at `130000`. Both `_raise_named`s (`compile.py:538`,
  `score.py:311`) raise `CodedError(f"{code}: {message}")`, and `CodedError` subclasses
  `ValueError` (`pricing_core/safe_error.py:64`). So the `ValueError` here and the
  `CodedError` in Step 2 both hold.

- [ ] **Step 2: Add the DP-1 tests to the same module.**

```python
from pricing_core.safe_error import CodedError  # move to the import block

_DATE_INPUT = {"name": "inception", "type": "date", "nullable": False}


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-227")
async def test_as_at_naming_a_non_date_input_is_refused_at_compile() -> None:
    with pytest.raises(CodedError, match=r"^RATING_TYPE_MISMATCH:.*s_area.*postcode"):
        await _compiled(_algo(as_at="postcode"))


@pytest.mark.req("FR-221")
async def test_as_at_naming_an_undeclared_value_is_refused_at_compile() -> None:
    with pytest.raises(CodedError, match=r"^RATING_GRAPH_UNRESOLVED_REF:.*s_area.*inception"):
        await _compiled(_algo(as_at="inception"))


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-227")
async def test_a_declared_effective_date_must_be_date_typed() -> None:
    contract = [*_CONTRACT, {"name": "effective_date", "type": "string", "nullable": False}]
    with pytest.raises(CodedError, match=r"^RATING_TYPE_MISMATCH:.*s_area.*effective_date"):
        await _compiled(_algo(contract=contract))


@pytest.mark.req("FR-221")
async def test_a_date_input_named_by_as_at_selects_the_row() -> None:
    algo = _algo(as_at="inception", contract=[*_CONTRACT, _DATE_INPUT])
    ctx = _quote(date(2025, 6, 1), extra_inputs={"inception": "2026-06-01"})
    result = await score_one(await _compiled(algo), ctx)
    assert int(result.outputs["payable_premium_minor"]) == 180_000, SUPERSEDED


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-213")
@pytest.mark.req("FR-255")
@pytest.mark.parametrize("raw", [
    "2026-01-01T00:30:00+01:00", "2026-01-01T00:00:00", "2026-1-1", "20260101",
    "2026-02-30", "nonsense",
])
async def test_a_malformed_as_at_value_is_refused_not_missed(raw: str) -> None:
    algo = _algo(as_at="inception", contract=[*_CONTRACT, _DATE_INPUT])
    compiled = await _compiled(algo)
    with pytest.raises(CodedError, match=r"^INPUT_CONTRACT_VIOLATION:.*s_area"):
        await score_one(compiled, _quote(date(2026, 6, 1), extra_inputs={"inception": raw}))


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-213")
async def test_an_input_shadowing_effective_date_is_checked() -> None:
    ctx = _quote(date(2026, 6, 1), extra_inputs={"effective_date": "2026-01-01T00:30:00+01:00"})
    with pytest.raises(CodedError, match=r"^INPUT_CONTRACT_VIOLATION:.*s_area"):
        await score_one(await _compiled(), ctx)
```

  `compile_bundle` turns the first `ValidationIssue` into
  `_raise_named(issues[0].code, issues[0].message)`, so a compile refusal's text is
  `CODE: <the issue's message>`. That is why the patterns can name the step and the
  `as_at` value.

- [ ] **Step 3: Run it red at the base.**

  Run: `uv run pytest -q packages/pricing-core/tests/test_rating_lookup_as_at.py`

  Expected FAIL, each by its cause:
  - `[2026-01-01-at-from]`, `[2026-06-01]`, `[2099-01-01-open-ended]` and
    `test_score_batch_prices_on_the_row_in_force`: `AssertionError: the superseded row's rate
    returned`.
  - `test_a_date_input_named_by_as_at_selects_the_row`: the same assertion. At the base,
    `as_at` is not read, so OLD wins.
  - `test_score_one_misses_before_every_row`, the three compile refusals, the six malformed
    values, and the shadowing test: `Failed: DID NOT RAISE`.

  Expected PASS (the controls): `[2020-01-01-at-from]` and `[2025-12-31-before-to]`. A pass on
  any expected red, or a red with any other cause, is a stop: record it and tell the lead.
  Paste the summary line and each failure line in the ledger.

- [ ] **Step 4: Commit the reds.** `test(pricing-core): FD-1420 reds — lookup ignores as_at
  (FR-221)`. The commit is red by design, and the ledger names its SHA.

### Task 2: The window, in the graph (DP-2 (a); Acceptance 1, 5)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/runtime.py`. Change the `lookup`
  branch of `_decision_table_node` (`:240-253`), add `_as_at_window` after `_reference_rows`
  (`:195-200`), and change the module docstring paragraph (`:22-35`).

**Interfaces:**
- Consumes: the JDM node's `as_at`. `to_jdm` dumps each step whole (`compile.py:484-485`), so
  the node carries it; Run 3 read it as `node["as_at"]`.
- Produces: `_as_at_window(row: Mapping[str, Any]) -> str`, module-private.

- [ ] **Step 1: Add the window helper** (`from datetime import date` joins the imports):

```python
def _as_at_window(row: Mapping[str, Any]) -> str:
    """One reference row's validity as a ZEN unary test on the step's `as_at` value.

    `01` FR-69's half-open `[effective_from, effective_to)`; an absent `effective_to` is
    open-ended. ZEN refuses `<` between strings, so both sides go through `date()` (verified
    on zen-engine 0.53.0, PL-1447 Task 0 run 1). The bounds are re-rendered through
    `date.fromisoformat`, so a malformed row raises here, at load, never inside the graph.
    """
    lower = date.fromisoformat(str(row["effective_from"])).isoformat()
    window = f"date($) >= date('{lower}')"
    if row.get("effective_to") is not None:
        upper = date.fromisoformat(str(row["effective_to"])).isoformat()
        window += f" and date($) < date('{upper}')"
    return window
```

- [ ] **Step 2: Replace the `lookup` branch** (`runtime.py:246-253`):

```python
    else:  # "lookup"
        ref = str(node["reference_table_ref"])
        rows = _reference_rows(payloads.get(ref))
        inputs = [
            {"id": "i0", "name": "key", "field": key_exprs[0] if key_exprs else "key"},
            {"id": "i1", "name": "as_at", "field": str(node["as_at"])},
        ]
        rules = [
            {"_id": f"r{i}", "i0": _quote(str(row["key"]), "string"),
             "i1": _as_at_window(row), "o0": json.dumps(
                str(row.get("payload", {}).get(output_name, ""))
            )}
            for i, row in enumerate(rows)
            if output_name in (row.get("payload") or {})
        ]
```

  `"hitPolicy": "first"` stays. Once windows are disjoint, at most one rule can match, and
  FR-69's load refusal keeps them disjoint (Acceptance 6).

- [ ] **Step 3: Rewrite the docstring paragraph** at `:22-35`. Keep its first sentence about
  `constraint`, then replace the rest from "A `lookup` step's `as_at`" with:

  > A `lookup` step's `as_at` window is translated per rule as a ZEN unary test,
  > `date($) >= date(from) and date($) < date(to)` (`_as_at_window`; the half-open interval of
  > `01` FR-69, open-ended when `to` is absent). ZEN's comparison operators refuse two strings
  > (verified live — `'b' > 'a'` raises `vmError: Opcode Compare: Unsupported type`), so both
  > sides go through `date()`. That function reads an offset as UTC, so the value it receives
  > must be a bare `YYYY-MM-DD`: `score.py`'s `_check_as_at_values` refuses anything else before
  > the engine runs (FR-221; PL 9688 DP-1). FD-1420 recorded the exact-key
  > translation this replaces.

- [ ] **Step 4: Run Task 1's module.** Run: `uv run pytest -q
  packages/pricing-core/tests/test_rating_lookup_as_at.py -k "prices or misses"`. Expected:
  every price and miss test passes. The DP-1 refusal tests stay red until Task 3.
- [ ] **Step 5: Commit.** `fix(pricing-core): a lookup reads the row in force as at its date
  (FD-1420, FR-221)`.

### Task 3: DP-1, compile and run time; the registry; the four fixtures (Acceptance 3, 4, 8, 10)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/compile.py`: add `_check_lookup_as_at`
  before `ALGORITHM_CHECKS` (`:359`), and append it to that tuple.
- Modify: `packages/pricing-core/src/pricing_core/rating/score.py`: add `_check_as_at_values`
  after `_validate_inputs` (`:333-392`), and call it in `score_one` and `_score_context_sync`
  right after each builds `context` (`:910-912`, `:1066-1068`).
- Modify: `packages/pricing-core/src/pricing_core/rating/authored.py`: move
  `(RatingLookupStep, "as_at")` from `NON_EXPRESSION_FIELDS` (`:60-64`) into
  `EXPRESSION_FIELDS` (`:44-50`).
- Modify: `packages/pricing-core/tests/test_rating_authored_fields.py` (`:189`, `:108-116`).
- Modify: `packages/pricing-core/tests/test_quote_input_raise_sites.py` (`_INPUT_FREE`).
- Modify: `packages/pricing-core/tests/test_rating_lookup_as_at.py` (Step 3a's sentinel test).
- Modify: the four fixtures that name a non-date `as_at` (`test_rating_runtime.py:445`,
  `test_rating_score.py:399` and its rows at `:411`, `test_rating_pin_membership.py:62` and
  `:232`).

**Interfaces:**
- Produces: `_check_lookup_as_at(algo: RatingAlgorithm) -> list[ValidationIssue]` and
  `_check_as_at_values(algorithm: RatingAlgorithm, context: Mapping[str, Any]) -> None`.

- [ ] **Step 1: The compile check** (DP-4 (i)+(p)). It reads `as_at` **through
  `authored_expression_fields`, never off the step**. Once Step 3 moves `as_at` into
  `EXPRESSION_FIELDS`, `test_no_check_module_reads_an_authored_field_off_a_step[compile]`
  (`test_rating_authored_fields.py:222-227`, FR-274) refuses any `.as_at` attribute read in
  `compile.py`. Run 8 saw that test fail on a `step.as_at` draft of this function.
  `compile.py` already imports `authored_expression_fields` (`validate_algorithm` iterates it).
  Import `RatingInputType` from `model_schema.rating` (`compile.py:28-40`) if it is absent.

```python
#: The date `score_one` and `score_batch` stamp into every engine context (`score.py`).
STAMPED_DATE = "effective_date"


def _check_lookup_as_at(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-221 (PL-1447 DP-1): a lookup's `as_at` names `effective_date` or a declared `date`
    input. A declared `effective_date` must itself be date-typed, because a declared input
    replaces the stamped date in the engine context. Read through the enumerator (FR-274)."""
    declared = {field.name: field.type for field in algo.input_contract}
    issues: list[ValidationIssue] = []
    for authored in authored_expression_fields(algo):
        if authored.field != "as_at":
            continue
        name = authored.text
        if name not in declared:
            if name == STAMPED_DATE:
                continue
            code = "RATING_GRAPH_UNRESOLVED_REF"
            why = "is neither effective_date nor a declared input"
        elif declared[name] == RatingInputType.DATE:
            continue
        else:
            code = "RATING_TYPE_MISMATCH"
            why = f"is a declared {declared[name].value!s} input, not a date"
        issues.append(ValidationIssue(
            code=code,
            message=(
                f"as_at of lookup step {authored.step_id!r} names {name!r}, which {why} (FR-221)"
            ),
            step_id=authored.step_id,
            field="as_at",
        ))
    return issues
```

  Then append `_check_lookup_as_at` to `ALGORITHM_CHECKS`. Only `RatingLookupStep` carries
  `as_at`, so `field == "as_at"` selects lookups. `ValidationIssue` takes `code`, `message`,
  `step_id` and `field` (`compile.py:384-389`). If RL 9767 (#1055) has moved it by dispatch,
  import it from its new home.

- [ ] **Step 2: The run-time check.**

```python
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _check_as_at_values(algorithm: RatingAlgorithm, context: Mapping[str, Any]) -> None:
    """FR-221 (PL-1447 DP-1, DP-3): the value each lookup's `as_at` reads, in the context the
    engine is about to receive, is a strict `YYYY-MM-DD` calendar date. ZEN's `date()` reads an
    offset as UTC and turns a malformed value into a miss, so neither may reach it. Reading
    the merged context also covers an input that shadows the stamped `effective_date`."""
    for step in algorithm.steps:
        if not isinstance(step, RatingLookupStep):
            continue
        value = context.get(step.as_at)
        if isinstance(value, str) and _ISO_DATE.fullmatch(value):
            try:
                date.fromisoformat(value)
                continue
            except ValueError:
                pass
        _raise_named(
            "INPUT_CONTRACT_VIOLATION",
            f"as_at of lookup step {step.step_id!r} reads {step.as_at!r}, which is not a "
            "YYYY-MM-DD calendar date (FR-221)",
        )
```

  Call `_check_as_at_values(algorithm, context)` on the line after `context = {...}` in
  `score_one` (`:910-912`) and in `_score_context_sync` (`:1066-1068`), before the engine call.
  The message never echoes the value: it names the step and the field, which keeps NFR-499's
  error-sink rule. `re` and `date` are already imported in `score.py` (`:362`, `:1029`).

- [ ] **Step 3: The registry.** Move the entry into `EXPRESSION_FIELDS` and delete its
  `NON_EXPRESSION_FIELDS` entry, whose reason text names this trigger. At
  `test_rating_authored_fields.py:189`, replace the assertion with
  `assert (rating_schema.RatingLookupStep, "as_at") in EXPRESSION_FIELDS` and
  `assert (rating_schema.RatingLookupStep, "as_at") not in NON_EXPRESSION_FIELDS`, importing
  `EXPRESSION_FIELDS` the way the module imports `NON_EXPRESSION_FIELDS`. Insert the entry
  directly after `(RatingLookupStep, "key_expr")`. Then add `("s_area", "as_at",
  "effective_date")` after `("s_area", "key_expr[0]", "channel")` in
  `test_the_enumerator_yields_every_authored_string_with_its_field`'s expected list
  (`:108-116`). Its fixture's `s_area` names `effective_date` (`test_rating_compile.py:84`),
  and run 8 saw this test fail without the entry. Every committed `as_at` (`effective_date`,
  `postcode`, `channel`, `veh`, `inception`) passes all five `STRING_CHECKS` (planner's run,
  13:2x BST: `[None, None, None, None, None]` for each).
- [ ] **Step 3a: The NFR-499 raise-site census.** `_check_as_at_values` is a new
  `_raise_named` site. `test_every_quote_input_raise_site_has_a_sentinel_case`
  (`packages/pricing-core/tests/test_quote_input_raise_sites.py:112-125`) fails until the
  site is accounted for; run 8 saw it fail, naming `('rating/score.py', '_check_as_at_values')`.
  Account for it the way RL-1346's ladder refusal is accounted for (`:66-68`):
  - Add `("rating/score.py", "_check_as_at_values"): 1` to `_INPUT_FREE`, with the comment
    `# FR-221 as_at refusal: step id and field name only, never the value
    (test_rating_lookup_as_at.py drives it with a sentinel)`.
  - Add this test to Task 1's module:

```python
_SENTINEL = "SENTINEL-quote-input-as-at-5e1f"


@pytest.mark.req("NFR-499")
@pytest.mark.req("FR-221")
async def test_the_as_at_refusal_never_carries_the_value() -> None:
    algo = _algo(as_at="inception", contract=[*_CONTRACT, _DATE_INPUT])
    compiled = await _compiled(algo)
    ctx = _quote(date(2026, 6, 1), extra_inputs={"inception": _SENTINEL})
    with pytest.raises(CodedError) as caught:
        await score_one(compiled, ctx)
    assert _SENTINEL not in str(caught.value)
    assert "'s_area'" in str(caught.value) and "'inception'" in str(caught.value)
    frame = pl.DataFrame([_ctx_to_row(ctx)])
    out = score_batch(compiled, frame.lazy()).collect()
    assert out["error_code"].to_list() == ["INPUT_CONTRACT_VIOLATION"]
    assert _SENTINEL not in (out["error_message"][0] or "")
```

  It is red at the base with `Failed: DID NOT RAISE`. The batch half reads `error_code` and
  `error_message`, the columns run 2 printed. Whether `_ctx_to_row` carries the `inception`
  input as its own column is not verified: if the batch half cannot reach the site, keep the
  `score_one` half and say so in the ledger.
- [ ] **Step 4: The four fixtures.** Each named a non-date value, and now names
  `effective_date`. Their expected values do not change.
  - `test_rating_runtime.py:445`: also add `"effective_date": "2026-06-01"` to both
    `evaluate` contexts (`:474-475`), and replace the comment at `:427-432`, whose "no as_at
    windowing" is now false.
  - `test_rating_score.py:399`: also give the row at `:411` `"effective_from": "2020-01-01",
    "effective_to": None`, and add `"effective_date": "2026-06-01"` to its `evaluate` context.
  - `test_rating_pin_membership.py:62` and `:232`.
- [ ] **Step 5: Run.** Run: `uv run pytest -q packages/pricing-core`. Expected: all pass,
  including every Task 1 test.
- [ ] **Step 6: Commit.** `fix(pricing-core): as_at names effective_date or a date input, and
  its value is a strict date (FR-221, DP-1)`.

### Task 4: The three HTTP paths, red first, and DP-3's pins (Acceptance 2, 6, 7)

**Files:**
- Create: `backend/tests/test_score_as_at.py`

This task's reds are run **at the slice's base**, before Tasks 2 and 3. Write this module
first: on a branch from the base, or in the same red commit as Task 1. The ledger records the
order used. Its tests need Postgres and MinIO; a skipped run is not a red.

- [ ] **Step 1: The fixture.** Mirror the neighbours rather than reinventing them
  ([`README.md`](README.md) rule 3):
  - **Reference table.** Mirror `_table` (`backend/tests/test_api_reference.py:35-51`), with
    `payload_columns: ["area_loading"]` and the two rows of Task 1's `ROWS`, created through
    the same three routes.
  - **Algorithm.** Task 1's `_algo()`, with `reference_table_ref` set to
    `f"reference_table:{slug}@1"`, created through `POST /api/v1/rating-algorithms`.
  - **Pinned version.** `_insert_version` (`test_rating_version_compile.py`), with
    `pins={"rate_tables": [], "models": [], "reference_tables": [f"reference_table:{slug}@1"],
    "custom_objectives": []}`, as `test_a_version_pinning_a_published_reference_table_compiles`
    does (`:453-495`).
  - **Compile.** Synchronous tests use `_run_compile_job`. The async batch test writes the
    compile out inline, as `test_scoring_handlers.py:95-127` explains.
  - **Headers.** Mirror each path's own header fixture: `test_score.py`'s `scoring_headers`,
    `test_score_compare.py`'s `reader_headers`, and `test_score_batch_api.py`'s
    `batch_headers`.
- [ ] **Step 2: `test_score_prices_on_the_row_in_force`.** `POST /api/v1/score` with
  `effective_date: "2026-06-01"`, inputs `{"base_minor": 100000, "postcode": "SW1A"}`, and the
  version ref. Assert `200` and `outputs["payable_premium_minor"] == 180000`, with the message
  `"the superseded row's rate returned"`.
- [ ] **Step 3: `test_score_compare_prices_both_sides_on_the_row_in_force`.**
  `POST /api/v1/score/compare` with `base` and `comparison` both the version's ref.
  Identical refs are allowed (`test_score_compare.py:166-175`), and the body's shape is
  `_body` there (`:118-130`). Assert both `body["base"]["outputs"]["payable_premium_minor"]`
  and `body["comparison"][...]` equal `180000`, with the same message.
- [ ] **Step 4: `test_score_batch_job_prices_on_the_row_in_force`.** Build a dataset version
  from a Polars frame shaped like `_scoring_frame` (`test_scoring_handlers.py:51-68`):
  `quote_id`, `purpose`, `effective_date`, `rating_version_ref`, plus `base_minor` and
  `postcode`. Use two rows, effective `2025-06-01` and `2026-06-01`. Store it with
  `_dataset_version` (`:71-92`). Then post `POST /api/v1/score/batch`, run the Job with
  `execute_job`, and read the output parquet, all as
  `test_the_route_answers_202_and_the_completed_job_yields_a_retrievable_parquet` does
  (`test_score_batch_api.py:144-196`). Assert that the `outputs_json` prices are
  `[130000, 180000]` in `quote_id` order, with the same message.
- [ ] **Step 5: `test_effective_date_parsing_is_pinned`** (DP-3). On `/score`:
  - `2026-06-01` → `200` and `180000`.
  - `2026-01-01T00:00:00+01:00` → `200` and **`180000`**: the local date's row. This is red
    at the base: `130000`.
  - `2026-01-01T00:30:00+01:00` → `422` with `code == "VALIDATION_FAILED"`.
  - `2026-13-01` → `422` with `code == "VALIDATION_FAILED"`.

  If any of the three pins fails at the base, **stop and report to the lead** (DP-3's
  condition).
- [ ] **Step 6: `test_overlapping_windows_are_refused_at_table_save_with_their_code`** (DP-2's
  overlap door). Load a version whose two `SW1A` rows overlap (OLD `effective_to` =
  `2026-02-01`) through the same route as Step 1. Assert `409` and `code ==
  "REFERENCE_INTERVAL_OVERLAP"`. This is a pin: it is green at the base.
- [ ] **Step 7: Run red at the base.** Run: `uv run pytest -q backend/tests/test_score_as_at.py`.
  Expected: Steps 2–4 and Step 5's midnight case fail with `the superseded row's rate
  returned`. The pins pass. Record the result in the ledger. After Tasks 2–3, all pass.
- [ ] **Step 8: Commit** (red, if before Task 2). `test(backend): FD-1420 reds on /score,
  /score/compare and batch (FR-221)`.

### Task 5: The spec text, verbatim from the ruling (activation need 2)

**Files:**
- Modify: `docs/specs/03-rating-engine.md`: the FR-221 row (`:107`, §3.2) only.

- [ ] **Step 1:** Append the ruling's T1 to the FR-221 cell. Use the ruling's text, not this
  plan's §"Spec text T1", where the two differ. Escape any `|` as `\|`.
- [ ] **Step 2:** Run `python3 scripts/audit-docs.py`. Expected: exit 0, or only the
  working-id check 31 rows the lead expects.
- [ ] **Step 3: Commit.** `docs(spec): FR-221 — as_at names effective_date or a date input;
  the row in force is half-open (FD-1420)`.

### Task 6: The gate and the ledger

- [ ] **Step 1:** Run the full two-half gate per `dev-commands`; it is Acceptance 10's
  commands. Use a gate slot under `RL-1263`. Record each command's exit code, and the tree
  it ran on, in the ledger.
- [ ] **Step 2:** Re-run Task 0 Steps 1 and 2. Record them (Acceptance 9).
- [ ] **Step 3:** Write the slice ledger `docs/ledgers/LG-<n>`. It holds every red with its
  failure line, the commit SHAs in order, Task 0's outputs, and any stop raised. Regenerate
  `docs/INDEX.md`.

## Hand-off

1. **FD-1420's register row** is discharged by the merge. The auditor writes that row, not
   this slice.
2. **For WK-675 S2 (PL 9713, #1131):** after T1, its inspector's `as_at` field should offer
   only `effective_date` and the algorithm's `date` inputs (PL 9713 `:242` cites FR-221). That
   is a note for S2's dispatch, not a change here.
3. **For FD-1374 / PL 9776 (#1051):** an input named `effective_date` can replace the stamped
   date in the engine context (§"A finding from planning"). This slice refuses the shadowed
   value only where a lookup reads it. Whether such an input may be sent at all stays with
   FR-246's remedy.

## Self-review

- **Spec coverage.** FR-221 (Tasks 1–3, 5) and FR-69 (Task 2, Acceptance 1, 5, 6). FR-255's
  miss and contract-violation types (Tasks 1, 3). FR-213 (Task 3). The three paths (Tasks 1
  and 4). DP-2's three conditions are Acceptance 1, 5 and 6. DP-3's pins are Acceptance 7.
  No requirement in §"Requirement coverage" lacks a task.
- **Literals checked against `caa4e411`.**
  - Route paths: `score.py:339-340`, `:415-416`, `:557-558`.
  - Codes: `03:928-931`, `01:934`, `reference.py:174`.
  - Test helpers: `test_rating_pin_membership.py:18-19`, `test_scoring_handlers.py:51`,
    `:71`, `:95`, `test_api_reference.py:35`.
  - `ZEN date()`, `QuoteContext.effective_date` parsing, and the Task 1 module: run, not
    recalled (Task 0 runs 1–3).
  - The two raisers' class, `CodedError`: read at `compile.py:538` and `score.py:311`.
  - Task 1's module was run as written (run 7). Task 2's and Task 3's code was not run as
    written. Task 2's logic is run 3's monkeypatch. Task 3's checks are new code, proven by
    Task 1's reds turning green.
- **Placeholders.** Task 4's tests are given as steps over named neighbours rather than full
  code. That is deliberate: their fixtures depend on four headers fixtures and a Postgres
  setup the planner did not run, and rule 3 says to name the authority rather than guess.
- **Types.** The names are consistent across tasks: `_as_at_window` (Task 2), and
  `_check_lookup_as_at`, `_check_as_at_values` and `STAMPED_DATE` (Task 3). Tasks 1 and 4
  share `_algo`, `ROWS` and `SUPERSEDED`.
