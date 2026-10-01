---
id: LG-9994
family: ledger
title: WK-1250 Slice 1 — the sub-graph artifact with typed ports and FR-227 at create
status: active
created: 2026-10-01
owner: executor
tree: f689c7828cb05eb2298f3fec505a4638c4437a11
phase: P2
work: WK-1250
slice: SL-1339
plans: [PL-1325]
corrected_by: []
relates: [RL-1309, RL-1263, FD-1326]
---

# LG-9994 — WK-1250 Slice 1 (SL-1339)

Executed from `PL-1325`. Branch `sl-1339-sub-graph-artifact`, from `origin/main`
`f689c7828cb05eb2298f3fec505a4638c4437a11` (#1027). Working id 9994, reserved by the lead
2026-10-01 00:01 BST; minted at the merge turn.

## Tasks

### Task 0 — preconditions

Executor check: `CLAUDE_EFFORT=medium`. `executor.md:13` reads: "`sonnet` (currently Sonnet 5); medium,
inherited from the lead — the highest-volume role; per-slice gates and the auditor's re-check bound the
risk of a cheaper setting."

**Dispatch record, FINAL, quoted verbatim**
(`gi-pricing-plan.local/handover/DISPATCH-WK-1250-S1-2026-10-01.md`; each line prefixed `> `):

> # Dispatch record — WK-1250 Slice 1 (SL-1339), from PL-1325 — FINAL
>
> **Status: DISPATCHED 2026-10-01 00:24:19 BST** (lane B GO by the lead). Drafted 00:01:16 BST. The maintainer's GO check PASSED (their entry "2026-10-01 00:03:18 BST — WK-1250 S1 dispatch DRAFT: GO check PASSED, conditional on #1027's merge"). #1027 merged on their MERGE-ACK as `f689c7828cb05eb2298f3fec505a4638c4437a11`. The executor's ledger Task 0 quotes the FINAL record verbatim. Plans are frozen by family: nothing in PL-1325 is edited, and activation facts live here.
>
> **The order:** the maintainer's entry "2026-09-30 23:57:25 BST — DECISION on the S3 halt: (A) carve the ladder half into its own slice; lane B takes WK-1250 S1 now", item 3. **This supersedes "WK-1250 S1 after S3"**: WK-1250 S1 goes FIRST on compile.py.
>
> ## Plan and slice status on main (the gate check, done FIRST this time)
> - **PL-1325:** `status: active` on main since #1023 (248dbf11), read by the lead with `grep -m1 '^status:'`.
> - **SL-1339:** `status: active` on main at f689c782, re-read by the lead with `git show origin/main:docs/roadmap.md | grep -A8 '^#### SL-1339' | grep '^status:'` at 2026-10-01 00:24:19 BST.
>
> ## Activation needs, quoted verbatim from PL-1325 ("Activation needs, in order"), each shown met
> 1. "RL-1309 on `main`. It rules every decision point this slice depends on." **Met:** RL-1309 is on main (mint batch 3, e3600789).
> 2. "PL-1254 `active`, and WK-1250's `SL-` rows cut." **Met:** PL-1254 active (#1023, 248dbf11); SL-1339..1341 cut (#1019, 71b67220).
> 3. "The WK-1178 fix slice (PL-1299) and the #967 code slice (#969, plan working id 9833) merged." **Met:** the fix slice #988 (SL-1300, 2118679b) and the #967 slice #1012 (SL-1315, 3a5f7cd5); PL-1299 reads `status: active`. All three SHAs were verified by the lead against `git log origin/main`. *Discrepancy, not blocking:* SL-1315's roadmap row still reads `status: active` (roadmap :1124), although #1012 merged. Need 3 asks only for "merged", which holds. The row's close goes in the next roadmap PR.
> 4. "A free RL-1263 gate slot, and the lead's dispatch record carrying the write-set check." **Met:** this record, condition 2. **Lane B grant: 2026-10-01 00:24:19 BST**, at main f689c782. The gate slot is granted per run. Lane A: WK-690 S2 is running a slotted baseline for its audit fix (F1), so one slot is in use at the grant.
>
> ## Decision points: every one has a resolver
> PL-1325 §Decision points: "Every decision point that bears on this slice is ruled; none is open." Map DP-1, DP-3 and DP-4 by **RL-1309**; DP-S1-1..DP-S1-4 as ruled in PL-1325 with RL-1309. PL-1254 DP-2 (**RL-1344**) blocks Slices 2 and 3 only, not this slice. **No task is held.**
>
> ## Conditions
> 1. **Write set:** PL-1325 §"File contention under RL-1263's option (c)" (`PL-1325:141-188`), verbatim, including its "Not in this slice's set" list: `compile_bundle`, `score.py`, `TraceStep`, `runtime.py`, any `approvals.py`, `errors.py`, `conftest*.py`, and any `pyproject.toml` or `uv.lock`.
> 2. **RL-1263 write-set check against lane A (WK-690 S2, PL-1327:90-127; built, in slice audit):**
>    - **`packages/model-schema/src/model_schema/__init__.py`:** both slices append exports. They may overlap only on the rule that **no existing line is edited by both**; the second to merge merges main in and re-runs its full gate (the maintainer's entry 22:33:30 BST, Decision 4).
>    - **`scripts/generate-contracts.py`:** this slice adds one slug → symbol map entry. WK-690 S2's write set does not list it (PL-1327:95-107). Task 0 checks WK-690 S2's actual diff (`gh pr diff` on its PR). If both touch it, append-only and second-to-merge re-gates.
>    - **Generated contracts and INDEX:** registry-exempt; the later slice regenerates.
>    - **Otherwise disjoint:** WK-690 S2 writes `modelling/`, `model_schema/objectives.py`, `02` and `bench-model.py`; this slice writes `rating/compile.py`, `model_schema/rating.py`, `graph_errors.py`, `rating_algorithms.py`, the new table and migration, `03`/`00`/`06`.
> 3. **compile.py order:** WK-1250 S1 first. The **ladder slice (SL-1345)** follows. It may overlap only if both are append-only on `ALGORITHM_CHECKS`; otherwise they serialise (the 23:57:25 entry, item 3). This slice refactors `_producer_types` and `_check_result_types` (existing definitions), so it is **not** append-only, and **SL-1345 does not build compile.py while this slice is open**.
> 4. **Holds (FD-1336, FD-1335):** not applicable. This slice reads no ladder rung values, and consumes neither `/score` nor any of FD-1335's open-object routes. It adds its own sub-graph routes, and their 2xx responses must be typed (no `{}` schema, per FD-1335's guard intent). Task 0 confirms.
> 5. **Decimal-output guard** (the maintainer's entry 22:43:26 BST): this slice commits no algorithm, seed or example declaring a `decimal` output. The ledger states it, with a grep.
> 6. **Gate evidence, for EVERY suite-level run (package and directory suites included, never unslotted):**
>    - a clean checkout of the named SHA, with `git status --porcelain` empty;
>    - `ruff check --no-cache`, and mypy on a fresh cache or with `--no-incremental`;
>    - the dev-commands slot wrapper verbatim (`.claude/skills/dev-commands/SKILL.md:122-171`), plus `LOKY_MAX_CPU_COUNT=4`, in the foreground with a timeout (executor.md S-11);
>    - `uptime` AND `free -h` at start and end;
>    - the other holder named as gate or not-gate via `flock -n`;
>    - wall and pytest time against the 1469.6s baseline.
>    **The wrapper exits 0 even when stages fail** (WK-690 S2's finding): read the stage table, never the exit code. A concurrent pair with lane A is an RL-1263 candidate; a missing field disqualifies it.
> 7. **After merging a main that adds a migration:** run `alembic upgrade head` on the per-worktree test DB first. This slice adds a migration: `down_revision` = the head at dispatch; the second to merge re-points.
> 8. **Red first:** every acceptance item. FD-1326 (was working id 9948) is fixed as Task 7, the last code task.
> 9. **Gate:** the full two-half gate before pushing. Docs checks run on a clean detached checkout.
> 10. **Ledger:** LG working id **9994**, reserved by the lead at 00:01 BST 1 Oct and checked free. The lead is the ONLY allocator (FD-1338). Task 0 quotes this FINAL record.
> 11. **Frozen records:** nothing in `docs/plans/` is edited, and no frozen record body.
> 12. **Executor:** a fresh `executor-1250s1`, spawned from `.claude/roles/executor.md` with its Model / effort line verbatim (sonnet, medium), in a new worktree from origin/main after #1027. It never `cd`s, not even `cd /tmp`.

**Premises a–n re-derived at `f689c782`**

| # | Result |
|---|---|
| a | Holds. `git grep -n -i 'sub_graph\|subgraph' -- backend/src ':(glob)packages/*/src/**'` prints 8 lines, none under `backend/src` (`model_schema/__init__.py:282,669`, `rating.py:340,343,390`, `refs.py:25`, `score.py:399,401`) |
| b, c | Hold (`rating.py:340`, `:390`; `refs.py:25`) |
| d | Holds. `RatingResultType` `rating.py:235`, `AlgorithmOutput` `:238` |
| e | Holds. `_produced_by` `:357`, `_consumed_by` `:365`; `_graph_invariants` `:393`; raises at `:407` (FR-214), `:419` (undefined value), `:439` (cycle) |
| i | **Moved.** The single head is now `a9f3c6d21b87` (49 revisions, scan of `revision` / `down_revision`), no longer `d7e2a9b5c418`. `down_revision` = `a9f3c6d21b87` |
| m | Mapped to post-#967 names. `_producer_types` `compile.py:90`, `_compatible` `:112`, `_check_result_types` `:120`, registered in `ALGORITHM_CHECKS` `:247-248`. Names unchanged, line numbers shifted |
| f, g, h, j, k, l, n | To be re-read at the task that uses each (Tasks 1, 3, 5, 6) and recorded there |

**Open PRs read** (`gh pr list --state open`, 2026-10-01, base `f689c782`): none rules on FR-217, FR-227,
sub-graphs or `compile.py`. #1025 (WK-690 S2, `gh pr diff 1025 --name-only`): touches
`model_schema/__init__.py` but **not** `scripts/generate-contracts.py`; its `docs/contracts` change is the
hand-authored `objective-certificate.schema.json`, not `generated/`. Overlap: `__init__.py` only,
append-only on both sides; second to merge merges main in and re-gates.

**Holds (condition 4):** N/A. This slice reads no ladder rung, and consumes neither `/score` nor an
open-object route of FD-1335; its own routes get typed 2xx responses.

**Decimal-output guard (condition 5).** This slice commits no algorithm, seed or example declaring a
`decimal` output. **Deviation from the plan's literal text:** Task 1's example (`PL-1325`) declares the
output port `ncd_factor` as `"type": "decimal"`. The dispatch record's condition 5 binds and the plan is
frozen, so the spec example declares `"type": "relativity"` instead. Guard grep, at the slice's final
tree: `git grep -n -E '"type": *"decimal"' origin/main...HEAD` over the added lines (recorded at Task 8).

**Typed-signal spike** (`library-spike`), `/tmp/ex1250s1/spike.py`: a `ValueError` subclass raised in a
`model_validator(mode="after")`, on a model and on its subclass.
Output: `B 2.13.5 value_error G True` and `S 2.13.5 value_error G True` — `errors()[0]["type"] ==
"value_error"`, and `ctx["error"]` is the instance. Holds at pydantic 2.13.5.

**Decision points** confirmed by record id (RL-1309): map DP-1 (b), DP-3 (a), DP-4 (a); DP-S1-1..4 (a) as
in PL-1325 *Decision points*. No difference found.

### Task 1 — spec (`03` §4.11 and §5.1, `00` §2.3, `06` §4.1)

`03` gains §4.11 `SubGraph` (shape, typed ports, invariants, example) and four §5.1 rows. `00` §2.3 gains
**Sub-graph**. `06` §4.1's `rating:read` row and the "Coarse write rights" note name Sub-graphs and
Regression Suites. Nothing else goes to `06`.

### Task 2 — `model-schema` shapes and contract

Red: `packages/model-schema/tests/test_sub_graph.py` failed at collection, `ModuleNotFoundError: No module
named 'model_schema.graph_errors'` (the plan predicted the `sub_graphs` module; the test imports both, so
the first missing one raised). Green: 15 passed. New modules `graph_errors.py` and `sub_graphs.py`; the
fragment validator reuses `_produced_by`, `_consumed_by`, `_as_list` and `RatingAlgorithm._reachable` /
`_reaches_output`, and keeps its own Kahn loop (`_topological_order`) so `rating.py` is untouched until
Task 7. `--check`: 34 generated contracts match. `sub-graph.schema.json` properties: `change_note`,
`inputs`, `outputs`, `slug`, `steps`, `version`. `test_contracts.py` passes (144 passed, 2 skipped).
`mypy` (repo config): no issues in 214 files. `ruff check --no-cache .`: clean.

### Task 3 — table and migration

Red: `backend/tests/test_migration_sub_graphs.py` failed at collection, `ImportError` on
`SubGraphVersionRow` (the plan predicted `UndefinedTable`; the import fails before any query). Green:
2 passed. Revision `2f598e89d12c`, `down_revision = a9f3c6d21b87`; `alembic heads` prints one head.
`upgrade head`, `downgrade -1`, `upgrade head` each ran on the per-worktree DB (the log lines show the
three steps; the shell rc was a pipe's, so the lines are the evidence). `tests/test_repository_invariants.py`:
11 passed, 2 failed (`test_money_discipline_is_enforced_by_the_docs_audit`,
`test_journey_citations_are_audited_in_ci`): both assert `audit-docs.py` exits 0, and it exits 1 on
check 31 alone (working ids 9994 unminted), the expected red of a working-id draft. Re-run at Task 8.
The `SubGraphVersionRow` model is appended at the end of `models.py`.

### Task 4 — `pricing-core`: FR-227 refactor and the fragment entry point

Red: four new fragment tests failed `ImportError: cannot import name 'fragment_output_type_issues'`
(as predicted); the new algorithm-path test `test_an_algorithm_type_mismatch_reports_the_output_step` was
green before the refactor (it pins "behaviour unchanged"). Names used: `producer_types(steps, typed_names)`,
`output_type_issues(types, outputs)`, `fragment_output_type_issues(steps, input_ports, output_ports)`, all
public and in `__all__`; `_producer_types(algo)` and `_check_result_types(algo)` kept as thin wrappers, the
latter still registered in `ALGORITHM_CHECKS`. Green: `test_rating_compile.py` and
`test_rating_authored_fields.py` (the #967 closure tests) 79 passed; `git diff --numstat` of the tests dir
shows additions only (0 removed). `lint-imports`: 4 kept, 0 broken; ruff, mypy clean.

### Task 5 — the service, the resolver and the mapper extraction

Characterisation first (new tests in `backend/tests/test_rating_algorithms.py`, four): **before** the
extraction `8 passed, 1 xfailed`; **after** `8 passed, 1 xfailed` (the `cycle_note` case is the xfail,
`strict=True`). Extracted: `graph_validation_error(exc, *, artifact)` and `raise_first_issue(issues)` (the
proposed names); `_parse_algorithm` and `_issues_to_error` call them. Red for the service: collection error
on `app.platform.sub_graphs` (missing module). Green: `test_sub_graphs_service.py` 12 passed. Broken-input
proof: with the `audit.record` call removed locally, `test_create_writes_version_one_and_one_audit_event`
failed (1 failed, the count of events read 0); the call was restored and never committed. Service names:
`create_sub_graph`, `create_version`, `get_version`, `list_versions`, `resolve_ref`; the content column
holds the body (`inputs`, `outputs`, `steps`, `change_note`), the slug and version are columns. A list of an
unknown slug is a 404 `NOT_FOUND` (the plan is silent). `resolve_ref` refuses a ref of another type with 422
`VALIDATION_FAILED`, the others with 404 `NOT_FOUND`. ruff, mypy, lint-imports clean.

### Task 6 — the routes

Red: first run `assert (404, 'NOT_FOUND') == (422, 'RATING_GRAPH_CYCLIC')` (no route mounted, as
predicted). Green: `test_sub_graphs_api.py` 28 passed, 1 xfailed (`cycle_note`, strict, Task 7 turns it
green); with `test_api_authorisation_sweep.py`, `test_demo_guide.py` and `test_contracts.py`: 189 passed,
2 skipped, 1 xfailed. The four routes return typed 2xx schemas in `docs/contracts/openapi/generated.json`
(`SubGraph`, `Page_SubGraph_`), none an open object; `--check` exits 0 after regeneration. Two test
adaptations, both because the TestClient runs the app on another event loop: the lost-race double adds
the rival row inside the service's own session (so the unique constraint fires at its flush); the
"no PUT/PATCH/DELETE" check reads `app.openapi()` paths. A scoped-to-one-algorithm principal (assignment
`scope_type=rating_algorithm`) is 403 on all four routes, as is a role-less member.

### Task 7 — the typed-signal fix (FD-1326, was working id 9948)

Red: with the two `xfail(strict=True)` marks removed, both `…cycle_note_is_validation_failed` cases failed
`assert 'RATING_GRAPH_CYCLIC' == 'VALIDATION_FAILED'` (the wrong code the substring match returns); the new
`packages/model-schema/tests/test_graph_errors.py` failed 2 of 3 (`assert False` on the class check; the
FR-214 case was green, as it stays a plain `ValueError`). Fix: `rating.py` raises `GraphUnresolvedRefError`
and `GraphCycleError` at the two sites, messages unchanged, FR-214 untouched; `graph_validation_error` reads
the class from `exc.errors()` (cycle, then unresolved, then fall-through) and never `str(exc)`. Green:
78 passed across `test_graph_errors.py`, `test_rating_algorithm.py`, `test_sub_graph.py`,
`test_rating_algorithms.py` (six tests, the four characterisation cases and the two existing),
`test_sub_graphs_api.py` and `test_sub_graphs_service.py`. No other caller matches the message text.

### Task 8 — gate, run 1 (head `a0c0a57a44003e5227fe604eaf272ca1da41dbab`)

Clean tree (`git status --porcelain` empty), `ruff check --no-cache .` and `mypy --no-incremental` clean
beforehand; wrapper verbatim from `.claude/skills/dev-commands/SKILL.md` plus `LOKY_MAX_CPU_COUNT=4`, in a
`timeout 3300` shell, foreground-waited. Start 23:47:07 BST, end 00:09:11 BST. Start: `uptime` load 0.88
1.94 2.86, `free -h` 21Gi free of 31Gi; end: load 1.31 2.05 2.29, 19Gi free. Other holder: `flock -n` on
`gate-1` and `gate-2` both free before the start. Stage table:

| stage | result |
|---|---|
| ruff | pass |
| mypy | pass |
| import_linter | pass |
| audit_docs | FAIL (check 31 only: working id 9994 gap, expected until minted) |
| req_coverage | pass |
| contracts | pass |
| pytest | FAIL: 17 failed, 4420 passed, 3 skipped in 1310.35s (baseline 1469.6s) |

Of the 17 failures, 14 are tests that assert `audit-docs.py` / `doc-id.py` exit 0 on the real tree and
fail on that same check 31 (`test_audit_docs_ids`, `test_doc_index`, `test_register_lint`,
`test_register_owed`, `test_repository_invariants`, `test_audit_docs_process_core_digest`,
`test_audit_docs_w37_11_ceiling`, `test_audit_docs_finding_citations`). **Three were real regressions of
this slice, found by the gate**, fixed in the next commit (existing-test registry lines, plan gap 3):
- `test_error_sinks`: `_SINKS` keyed the `str(exc)` sink on `_parse_algorithm`; the extraction moved it to
  `graph_validation_error`, and Task 7 removed the keyword read, so the count is 1.
- `test_worker_raise_sites`: `_SITES` keyed the dynamic raise on `_issues_to_error`; it moved to
  `raise_first_issue`.
- `test_rating_committed_strings`: the scan read the `title` of the `expr`/`clamp_bounds` property
  definitions in the new generated schemas as authored strings; `docs/contracts/openapi/generated.json`
  and `docs/contracts/schemas/generated/` join `_SKIP_PREFIXES`.
Those three files pass (10 passed). A new head needs a new grant (S-13).

**Gate, run 2 (head `74d46cf1b138fd8dbd1dccacc1e39899f19361ea`, a detached checkout of that SHA in this
worktree, `git status --porcelain` empty).** `ruff check --no-cache` and `mypy --no-incremental` clean
first; the same wrapper, `timeout 3300`, foreground-waited. 00:12:13 to 00:33:30 BST. Start: load 0.84 1.64
2.10, 18Gi free of 31Gi; end: load 1.47 1.58 1.74, 20Gi free. Both slots free via `flock -n` before the
start. Stage table: ruff pass, mypy pass, import_linter pass, **audit_docs FAIL** (check 31 only, the
working-id gap 1345..9994), req_coverage pass, contracts pass, **pytest FAIL: 14 failed, 4423 passed,
3 skipped in 1263.42s** (baseline 1469.6s). The 14 failures are exactly the run-1 audit-docs-rc set (the
three real regressions are gone: 17 → 14); each asserts `audit-docs.py` or `doc-id.py` exits 0 and fails on
check 31. They pass once LG-9994 is minted. Frontend half on the same SHA: `pnpm install --frozen-lockfile`,
`generate:api`, `lint`, `type-check`, `build` all rc 0; `pnpm test` 97 files, 609 tests passed.

**The committed-strings exclusion, with it removed** (lead's Delta 3). `_authored_strings()` with the two
generated prefixes taken out of `_SKIP_PREFIXES`, run at `a0c0a57a`, reports exactly **8** unexplained
hits, over 4 files × 2 strings: `docs/contracts/openapi/generated.json` and the three
`docs/contracts/schemas/generated/sub-graph{,-create,-body}.schema.json`, each with `'Clamp Bounds'` and
`'Key Expr'`. Classification: all 8 are the `title` of the JSON Schema *property definition* named
`clamp_bounds` / `key_expr` (a pydantic-generated label), not an authored rating expression; none is
an expression, a condition or a bound. No generated file carries an authored string. The exclusion
removes no authored string from the scan; it removes generated property labels. The hand-authored
`rating-algorithm.schema.json` stays scanned.

## Deviations from PL-1325, each named

1. **Decimal example** (Task 1): the §4.11 example declares the output port type `relativity`, not
   `decimal`. Grounds: dispatch condition 5 and the maintainer's 2026-09-30 22:43:26 BST entry. The lead
   agreed.
2. **No `03` §2 glossary row** (Task 1): `scripts/audit-docs.py` check 13 fails a `03` §2 row for a term
   `00` §2 already defines ("reference it, do not redefine"). The plan's restating row is therefore
   omitted; `03` §4.11 points at `00` §2.3 instead.

3. **`backend/tests/test_contracts.py`** (Task 2) gains three `ONE_SIDED_SLUGS` entries
   (`sub-graph`, `sub-graph-create`, `sub-graph-body`, "first written form — 03 §4.11"), append-only.
   The plan's write set omits this file; `test_every_one_sided_slug_is_declared` goes red without it.
4. **`scripts/audit-docs.py`** gains three entries in its F83 exemption register (the three generated
   `sub-graph*.schema.json` files, dated comment, the `score-comparison` precedent). Checks 30 and 35 fail
   without them. The plan's write set omits the file; append-only.
5. **`docs/contracts/openapi/generated.json`** regenerates with a large diff (7319 added, 6002 removed
   lines by `git diff --numstat origin/main...HEAD`): FastAPI re-hoists shared component schemas once the
   new response models reference the step union. It is generated, never hand-edited, and `--check` exits 0.
6. **Decimal guard (condition 5), grep over the added lines**,
   `git diff origin/main...HEAD -U0 | grep -E '^\+' | grep -n -E 'type.*decimal'`: three hits, none a
   committed algorithm, seed or example declaring a `decimal` output: two lines of this ledger that state
   the guard, and one test (`test_a_compatible_fragment_output_port_raises_no_issue`) whose expression
   step has `result_type="decimal"` against a `money_minor` port — a test fixture, which the
   maintainer's 22:43:26 BST entry excludes ("no committed algorithm outside tests").
7. **Three existing test registries** (plan gap 3, found by the gate): `backend/tests/test_error_sinks.py`
   (`_SINKS` key renamed), `backend/tests/test_worker_raise_sites.py` (`_SITES` key renamed),
   `packages/pricing-core/tests/test_rating_committed_strings.py` (`_SKIP_PREFIXES` appended).

## PRs

None yet.

#1034 (draft), branch `sl-1339-sub-graph-artifact`, opened 2026-10-01. Appended, not replaced (the ledger is append-only).

## Closing verdicts

- **FR-217** (`03` §3.1): artifact limb delivered (SL-1339); pin and inlining limbs not started, owned by
  Slice 2 (SL-1340).
- **FR-227** (`03` §3.2): delivered at create for a fragment's output ports whose producer type is known at
  save (an `expression` step or an input port); the algorithm path is unchanged.
- **Slice audit item 4 (adopted, Delta 4):** the committed-strings exclusion is narrowed. The two
  `_SKIP_PREFIXES` entries are dropped; `_json_strings` ignores only the `title` of a field-named property
  definition directly under `properties`, with a broken-input test that a `default` in the same definition
  is still scanned. New gate below.

### Task 8 — gate, run 3 (merged head `4e6272a878f2280ea072a8ce73e521415faf979e`)

`origin/main` `214fd4d7` (#1031, #1032, docs only) merged first (`docs/INDEX.md` regenerated, never
hand-merged; no migration came in). Clean tree (`git status --porcelain` empty), `ruff check --no-cache .`
and `mypy --no-incremental` clean beforehand, the same wrapper under `timeout 3300`, foreground-waited.
00:43:14 to 01:06:27 BST. Start: load 1.59 1.57 1.67, 19Gi free of 31Gi; end: load 1.44 1.89 1.86, 19Gi
free. Both slots free via `flock -n` before the start. Stage table: ruff pass, mypy pass, import_linter
pass, **audit_docs FAIL** (check 31 only, the gap 1348..9994), req_coverage pass, contracts pass,
**pytest FAIL: 14 failed, 4424 passed, 3 skipped in 1376.75s** (baseline 1469.6s). The 14 are the same
audit-docs-rc set as run 2, each failing on check 31 alone; no other test fails. Frontend half on the
same head: install, `generate:api`, `lint`, `type-check`, `build` rc 0; `pnpm test` 97 files, 609 tests.

### Correction (2026-10-01, BST): the gate windows above are UTC, not BST

The three gate windows in Task 8 above were read from the box clock (`date`), which is UTC, and were
labelled BST. BST is UTC+1 (`TZ=Europe/London date` confirms). The old lines stand; the windows in BST:

| run | head | as written (UTC, mislabelled BST) | in BST (UTC+1) |
|---|---|---|---|
| 1 | `a0c0a57a` | 23:47:07 to 00:09:11 (30 Sep to 1 Oct) | 00:47:07 to 01:09:11, 1 Oct |
| 2 | `74d46cf1` | 00:12:13 to 00:33:30 | 01:12:13 to 01:33:30, 1 Oct |
| 3 | `4e6272a8` | 00:43:14 to 01:06:27 | 01:43:14 to 02:06:27, 1 Oct |

The `uptime` load and `free -h` readings are unaffected (they carry no zone).

