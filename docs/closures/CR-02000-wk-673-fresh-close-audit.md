---
id: CR-2000
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-673 fresh Work close audit — Dislocation with attribution (re-tests CR-1981)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-11-04   # drafted 2026-11-04 under working id 8310
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: db92a7bc0424059ed0aff4e5cebf445661c3be81
phase: P2
work: WK-673
corrected_by: []
relates: [CR-1981, PL-1267, PL-1500, PL-1501, PL-1984, RL-1504, SL-1388, SL-1389, SL-1985, SL-1997, LG-1570, LG-1582, LG-1986, LG-1998, FD-1481, FD-1490, FD-1491, FD-1495, FD-1576, FD-1578, FD-1651, FD-1982, FD-1983]
---

# CR-2000 — WK-673 fresh Work close audit

*Working id CR 8310 (minted as CR-2000), reserved by the lead. The auditor seat aud-wk673b wrote this record on
2026-11-04 from 09:44 GMT (`date -u`). The instruction is the lead's brief
`brief-aud-freshclose-2026-11-04.md`, on the maintainer's entry "2026-11-04 08:46:25 GMT" (the
ruling: the fresh close audits) and the condition in "2026-11-04 08:05:12 GMT" (FD-1982 ruling
(a)), both in `~/gi-pricing-plan.local/channel/to-lead.md`. It re-tests `CR-1981` (NOT CLOSE-READY,
3 Nov) and follows `.claude/skills/close-workstream`, `CLAUDE.md` §13 and §14.*

**What this record is.** It gathers evidence and **proposes**. Every §13 verdict below is
written "PROPOSED" and is the lead's to give. **The close is the user's dated acceptance line.**
This record does not close WK-673. The roadmap row it edits says "fresh close audit filed,
acceptance owed".

**Object.** `origin/main` at `db92a7bc0424059ed0aff4e5cebf445661c3be81` (tree
`ede3bf38bf33b0e9dfdc54e4c7b6590809ceb7fd`), read with `git ls-remote origin refs/heads/main` at
the start. Every `file:line` and every count below is at that tree unless it names another.
Branch `docs/wk673-fresh-close-2026-11-04`, cut from that commit. The form is `CR-1981`'s.

## Scope

### §0. The requirement set, derived from the documents before any evidence

**Predicate** (runnable from the repository root at `db92a7bc`). The union of the ids cited by
the WK-673 roadmap section (`docs/roadmap.md:688`, up to the next `### WK-` heading at `:1065`)
and the 16 plans whose front matter reads `work: WK-673` (CR-1981's 15 plus `PL-1984`):

```bash
( sed -n '688,1064p' docs/roadmap.md
  cat $(git grep -l '^work: WK-673' -- docs/plans)
) | grep -ohE '\b(FR|NFR)-[0-9]+\b' | sort -u -V
```

It prints **75 ids**: CR-1981's 74 at `c807a59d` (the same predicate over that tree) plus `02`
FR-132, which `PL-1984:464` and `:490` cite in DP-2 only (`RL-1470` Ruled 9, carried to P3). Each id
was mapped to its module by the spec holding its `| **<id>** |` row.

**Requirements axis, the whole predicate.** One run per module, through `run-heavy.sh --grant
"2026-11-04 08:46:25 GMT"` (not `--light`, which refuses any script but `audit-docs.py` and
`doc-index.py`). `--sections NONE` selects no section, so only the `--extra` ids are in scope:

```bash
python3 scripts/scope-audit.py <MOD> --sections NONE --extra <the module's ids from the predicate>
```

| Module | In scope | With a `@pytest.mark.req` marker | No marker | rc |
|---|---|---|---|---|
| RATE | 52 | 51 (98%) | NFR-493 | 1 |
| MODEL | 8 | 8 | — | 0 |
| GOV | 6 | 5 (83%) | FR-365 | 1 |
| DATA | 3 | 3 | — | 0 |
| PLAT | 3 | 3 | — | 0 |
| OVR | 2 | 2 | — | 0 |
| OPT | 1 | 0 | FR-294 | 1 |
| **Total** | **75** | **72** | **3** | |

The three unmarked ids are the same as CR-1981's, and are context, not WK-673 deliverables: FR-294
(`04`'s GIPP check, Phase 4, WK-685), NFR-493 (the batch throughput floor, a cost input), FR-365
(option (a) of `PL-1267`'s DP-3, not taken). FR-132 is context (a P3 carry).

**WK-673's own deliverable set is 16 ids**, unchanged from CR-1981 §0: the roadmap row's ten
(`docs/roadmap.md:700`) — FR-263, FR-264, FR-265, FR-266, FR-224, FR-257 limb (2), `06` FR-364,
FR-231 (the F-W10-2 weight limb), NFR-495, NFR-496 (applied) — the three minted ids FR-1397,
FR-1398, FR-1399, and the three fix-slice ids FR-221, FR-240, FR-242. The two slices merged since
CR-1981 touch FR-88 and FR-240 (SL-1985, `LG-1986` Scope) and FR-227, FR-1397, NFR-499, FR-212,
FR-224, FR-257 and FR-364 (SL-1997, `LG-1998:27`); of these only FR-88, FR-227, FR-212 and NFR-499
are outside the 16, and they are evidenced in §1b. The row carries no count to reconcile.

```bash
python3 scripts/scope-audit.py RATE --sections 3.9 \
  --extra FR-224,FR-257,FR-231,NFR-495,NFR-496,FR-240,FR-242,FR-221 --endpoints
python3 scripts/scope-audit.py GOV --sections none --extra FR-364 --endpoints
```

RATE: `3.9 Dislocation 7/7 evidenced`, "in scope: 15, with evidence: 15 (100%)", rc 0. GOV:
FR-364 `evidenced`, "in scope: 1, with evidence: 1 (100%)", rc 1 from the endpoint axis only.

**Endpoints axis.** RATE: "declared: 45, published: 45 (100%) — every declared endpoint is
published in the contract". GOV: "declared: 23, published: 13 (57%)" — the same ten unpublished
P3 governance routes CR-1981 §0 lists; none is WK-673's, and WK-673 adds no GOV route.

**Catalogue axis.** `scope-audit.py RATE --catalogue VR` and `GOV --catalogue VR` print
"03-rating-engine.md declares no VR-* catalogue" and "06-governance.md declares no VR-* catalogue".
Nothing to compare.

**Assigned elsewhere** (unchanged, `PL-1267:293-297`): the Dislocation view is WK-675's; FR-257
limbs (1), (3), (4) are not WK-673's; NFR-496's production-sampling limb is WK-674's. **New since
CR-1981:** `06` FR-364's `rate_table_diffs` limb is re-owned to P3, owner WK-1178 (§5).

## Evidence

### §1. Each deliverable: exists and works

CR-1981 §1's table stands at `db92a7bc` for the 16 ids. What changed in the code since `c807a59d`
(`git diff --stat c807a59d db92a7bc -- . ':!docs'`) is SL-1985 (#1421), SL-1997 (#1426) and three
other Works' slices (#1417, #1422 to #1425); WK-673's changes are in §1b. Two cells of CR-1981 §1
moved:

- **FR-1397, NFR-499.** `class AttributionError(CodedError)` at
  `packages/pricing-core/src/pricing_core/rating/analysis.py:521` (was `ValueError`, FD-1578). The
  leak asserts are inverted: `packages/pricing-core/tests/test_rating_attribution.py:632`
  `assert "Q0" not in str(exc.value)`, `:649`, `:662`, `:884` `"Q000" not in`; `:941`
  `test_per_policy_attribution_errors_name_no_policy_and_no_figure` asserts no quote id in
  `str(error)` or `safe_error_text(error)` (`:951-952`) and `isinstance(error, CodedError)`
  (`:956`).
- **FR-240 (the GLM arm).** SL-1985: a pinned model's consumed Factors derive per arm; an empty
  derived set refuses (§1b).

### §1a. SL-1388 and SL-1389, per requirement (the condition of 2026-11-04 08:05:12 GMT)

The condition: this audit "names SL-1388 and SL-1389 among the slices whose requirements it
evidences, each requirement with its test or its verdict". Each acceptance item of the slice's leaf
plan is mapped to its test at `db92a7bc`; each test was located by `def` and its markers read from
the lines above it; the load-bearing asserts were read.

**SL-1388** (Slice 4, #1256, `84ff9f0b`; leaf `PL-1501` Acceptance Standard `:183`; `B` =
`backend/tests/test_dislocation_runs.py`):

| Item | Requirement | Test at `db92a7bc` (markers) | Assert read |
|---|---|---|---|
| 1 run persists as a citable row | FR-265, FR-263, FR-266 | `B:413` `test_a_dislocation_run_persists_with_its_job_id_and_movers_blob` (FR-263, FR-265, FR-266) | one row; `run.job_id == job_id == row.job_id`; blob sha matches; `job.result` is the `dislocation_run:<id>` ref; attribution present |
| 2 movers blob holds no portfolio column, never served generically | NFR-499 | `B:430` `test_the_stored_movers_hold_no_portfolio_column`; `B:173` `test_the_generic_blob_route_refuses_a_movers_blob` (NFR-499 each) | located |
| 3 subset bundle never a Rating Version | FR-1398 | `B:443` `test_dislocation_subset_bundles_never_become_rating_versions` (FR-1398) | located (CR-1981 §1) |
| 4 bad partition refused before any Job | FR-1399 | `B:598` `test_post_refuses_groups_that_do_not_partition_the_derived_changes` (FR-1399) | 422 `VALIDATION_FAILED`, `"c2"` in detail, 0 jobs |
| 5 reconciliation failure by its own code | FR-1397 | `B:465` `test_a_run_that_does_not_reconcile_fails_with_attribution_reconciliation_failed` (FR-1397) | `FAILED`, code `ATTRIBUTION_RECONCILIATION_FAILED`, `"Q000" not in` the error and the served body (FD-1578's inversion), no row |
| 6 ruled permissions | FR-265, FR-263 | `B:611` `test_post_needs_rating_compile_and_dataset_read` (FR-263); `B:637` `test_get_needs_rating_read_and_scopes_to_the_workspace` (FR-265) | the outcome map; 403 `PERMISSION_DENIED`, 404 unknown, 404 cross-workspace |
| 7 estimate before launch | FR-263 | `B:654` `test_the_estimate_is_returned_before_any_job` (FR-263) | located |
| 8 byte-identical artifact | NFR-495 | `B:493` `test_two_runs_of_the_same_spec_are_byte_identical` (NFR-495) | rows equal without the job id; blob sha equal; job ids differ |
| 9 `dislocation-run` compared | FR-265 | `backend/tests/test_contracts.py:47` `"dislocation-run"` in `COMPARED_SLUGS` | — |
| 10 markers | FR-265, FR-263, FR-1398, FR-266 | `req-coverage.py` rc 0 in the gate of record (§2) | — |
| 11 resolver move changed nothing | — | the full suite in the gate of record | — |
| 12 two-half gate | — | the gate of record, §2 | — |
| 13 closes on MERGE-ACK + clean audit | — | MERGE-ACK 2026-10-10 05:13:20 BST; **no slice audit** — accepted by FD-1982 ruling (a), discharged here | — |
| 14 over-bound run refused before any Job | FR-263 | `B:674` `test_a_run_estimated_over_the_single_job_bound_is_refused_before_any_job` (FR-263) | 422 `VALIDATION_FAILED`, the bound named, 0 jobs; estimate 96 |
| 15 redelivery fix | FR-263 | `B:510` `test_the_celery_visibility_timeout_exceeds_the_single_job_bound`; `B:520` `test_a_second_delivery_for_a_running_dislocation_job_does_nothing` (FR-263 each) | located |
| 16 `/movers` joins the portfolio at read | FR-263, NFR-499 | `B:696` `test_movers_route_joins_the_portfolio_columns_at_read` (FR-263, NFR-499) | located |

**SL-1389** (Slice 5, #1260, `db0642c4`; leaf `PL-1500` Acceptance Standard `:280`; `G` =
`backend/tests/test_rating_version_dislocation_gate.py`, `M` =
`packages/model-schema/tests/test_approvals.py`, `S` = `backend/tests/test_rating_versions.py`).
"Red first" cites `LG-1998`'s DB-window table (2026-11-04 05:12:49Z–05:30:42Z, `LG-1998:61-80`),
each red a scratch revert of the named call, restored after:

| Item | Requirement | Test at `db92a7bc` (markers) | Red first |
|---|---|---|---|
| 1 `structural_diff` persisted | `06` FR-364, FR-219 | `G:248` `test_submission_persists_the_structural_diff_as_a_blob` | not recorded |
| 2 limb (2) refuses | FR-257 | `G:92`, `G:105`, `G:124` (`no_dislocation_run`, `stale_candidate_bundle_hash`, `baseline_is_not_the_current_live_version`) | **yes** — limb (2) not called: 5 failed (`LG-1998` row "12 row 2") |
| 3 limb (2) accepts the right run | FR-257 | `G:142` `test_limb_2_accepts_a_run_against_the_live_version_and_records_it` | in the same 5 (`KeyError: 'dislocation_run_id'`) |
| 4 first version (DP-S5-1) | FR-257 | `G:164` `test_limb_2_with_nothing_live_or_approved_records_the_first_version`; `G:225` `test_a_first_versions_diff_is_taken_against_an_empty_algorithm` | in the same 5 (all `test_limb_2_*`) |
| 5 FR-224 refuses above the threshold | FR-224 | `G:590`, `G:606`, `G:618`, `G:637` | **yes** — `_approximation_gate` not called: 7 failed ("12 row 5") |
| 6 threshold never from Settings | FR-224 | `G:651` `test_fr224_threshold_ignores_environment_variables` | **yes** — overridden from `GIP_APPROXIMATION_MAX_ABS_CHANGE_PCT`: 1 failed ("12 row 6") |
| 7 threshold field validated | FR-224 | `M:372` `test_the_deviation_threshold_is_only_on_rating_version_entries`; `M:392` `test_the_deviation_threshold_bounds` | not recorded |
| 8 FR-136 pre-check first | FR-224, FR-136 | `G:488` `test_fr136_precheck_refuses_before_any_run` | not recorded |
| 9 no Approval Request after a refusal | FR-257, FR-224 | asserted inside items 2, 4–6, 8 (CR-1981 §1) | through items 2, 5, 6 |
| 10 existing gate unchanged | FR-257 | `S` in the gate of record | — |
| 11 contracts | — | `generate-contracts.py --check` rc 0 in the gate of record | — |
| 12 two-half gate | — | the gate of record, §2 | — |
| 13 closes on MERGE-ACK + clean audit | — | MERGE-ACK 2026-10-10 08:40:44 BST; **no slice audit** — accepted by FD-1982 ruling (a), discharged here | — |
| 14 version carries its summary | FR-242 | `S:419` `test_submit_writes_the_change_summary_on_the_version` | not recorded |
| 15 unset threshold governed by default | FR-224 | `G:691` `test_fr224_an_unset_threshold_is_governed_by_the_default` | **yes** — unset returns `None`: 1 failed ("12 row 15") |
| 16 the default is re-readable | FR-224 (RL-1504 DP-S5-2 condition (ii)) | **none** — a ledger reading, not a test | **OWED** (`LG-1582:84`); §5, FD candidate A |
| 17 nearest rank | FR-224 | `G:366` `test_quantiles_are_nearest_rank_not_interpolated` | not recorded |
| 18 rounding once toward +∞ | FR-224 | `G:384` `test_quantiles_round_once_toward_positive_infinity` | not recorded |
| 19 empty banded set refused | FR-224 | `G:728` `test_an_empty_banded_set_has_null_quantiles_and_fr224_refuses` | **yes** — null read as 0: 1 failed ("12 row 19") |

Every SL-1389 test passes at the final head: `LG-1998:80` "dislocation_gate … 25 … passed, rc=0",
and in the gate of record (§2). The five red-first proofs `PL-1984` row 2 owed (items 2, 5, 6, 15,
19) are recorded; items 3, 4 and 9 fall red inside them. Items 1, 7, 8, 14, 17 and 18 have no
recorded red; FD-1982 ruling (a) accepts the slice-audit gap on the ground that "limb 1 is met" —
the five owed proofs — so they are not re-opened here.

### §1b. SL-1985 and SL-1997 (merged since CR-1981)

Both rows sit in WK-673's section with `work: WK-673` (`docs/roadmap.md:1026-1043` and
`:1046-1063`). **Neither ledger has an audit: `LG-1986:244-246` and `LG-1998:47-49` read "(the
auditor's)"** — the FD-1982 shape, before close rather than after (§5, closing acts).

| Slice | Requirement | Test at `db92a7bc` | Red first (ancestor of the PR head, `git merge-base --is-ancestor` rc 0) |
|---|---|---|---|
| SL-1985 (#1421 `dfbce89b`, head `13a94a07`) | FR-240, FR-88 | `packages/pricing-core/tests/test_rating_compile_fr240.py`: `test_a_model_call_over_a_glm_fitted_on_a_control_factor_is_refused`, `…_glm_whose_offset_model_is_fitted_on_a_control_factor_is_refused`, `…_model_whose_fit_result_lacks_the_fields_is_refused[glm-no-coefficients, glm-intercept-only, gbm-no-feature_order, gbm-empty-feature_order]` (`:274`, `:297`, `:323`; FR-88, FR-240 each); the peril component `test_rating_peril_scoring.py:282` `test_a_control_factor_in_a_peril_component_is_refused` | `LG-1986:60-69`, 6 failed rc 1; red commits `ada52401`, `c9142a2b`, `5c17c974`, `cc8fca15`, fix `c9a35475`, each rc 0 against `13a94a07` |
| SL-1997 (#1426 `db92a7bc`, head `84b1d859`) | FR-227 (FD-1490) | `backend/tests/test_errors.py:170` `test_monetary_float_refused_is_withdrawn` (FR-227): `"MONETARY_FLOAT_REFUSED" not in RATING_ERROR_CODES` (`:176`) | `LG-1998` "7 FD-1490" 1 failed rc 1; `badd36b0` red, `d55031ab` fix |
| SL-1997 | FR-1397, NFR-499 (FD-1578) | `test_rating_attribution.py:632`, `:649`, `:662`, `:884`, `:941` (§1) | `LG-1998:57` 7 failed rc 1; `daa4ae6e` red, `0cb69a0c` fix, `518349ae` inversions |
| SL-1997 | `06` FR-364 (FD-1651) | `backend/tests/test_rating_version_evidence_floor.py:204` `test_a_policy_naming_an_unverifiable_kind_is_refused_by_name`, `:223` `test_a_policy_naming_rate_table_diffs_is_refused_naming_the_kind` (FR-364 each) | `LG-1998` "11" scratch A and B, each `DID NOT RAISE`, rc 1 |
| SL-1997 | FR-212 (FD-1481) | `packages/pricing-core/tests/test_rating_wire_order.py:245` `test_a_float_read_after_a_model_call_is_cut_to_15_significant_digits` (FR-212): `echoed == _FLOAT_ECHOED`, `echoed != _FLOAT_IN` | a characterisation pin, green at base by design (`:246`); `26924345` |
| SL-1997 | FR-224, FR-257 (FD-1982) | §1a | §1a |

`git grep -n MONETARY_FLOAT_REFUSED -- ':!docs'` prints `backend/tests/test_errors.py:176` and
`:178` only. `8347298d`, `07e62951` (the gated head) are ancestors of `84b1d859` (rc 0 each).

**The §5 retrofit-impossible list.** Unchanged from CR-1981: WK-673 consumes the invariants and
regresses none.

### §2. The gate

**Evidence of record** (the maintainer's "2026-11-04 08:46:25 GMT" ruling), each read from its
primary source:

1. **The S-b gate at `07e62951`** (on `bb9781a9`), logs `~/gi-pricing-plan.local/scratch/sl8305-gate/gate/`:
   `START head: 07e62951ef472bac7ac7865db78836eb56a4d837 … 2026-11-04T05:46:19+00:00`, `END
   2026-11-04T07:36:01+00:00 … rc=1`. The `.rc` files: ruff 0, mypy 0, import_linter 0,
   req_coverage 0, contracts 0, audit_docs 1, pytest 1. `pytest.log`'s last line: "13 failed, 7047
   passed, 22 skipped, 5 xfailed, 146 warnings in 4715.81s (1:18:35)"; the 13 `FAILED` lines lie in
   exactly the eight seat-brief item-31 files (`test_audit_docs_finding_citations` 1, `_ids` 2,
   `_process_core_digest` 2, `_w37_11_ceiling` 1, `test_doc_index` 1, `test_register_lint` 3,
   `test_register_owed` 1, `test_repository_invariants` 2). `audit_docs.log`: "FAILED (2)", both
   check 31 (gaps → 8302, → 8305, the slice's own working ids then). Frontend six rows rc 0;
   `fe-test.log` "Test Files 138 passed (138)", "Tests 919 passed (919)". Demo: "designed stop …
   (both lines seen)", "demo seconds 1587", "dislocation #1 592 s". Accepted under item 31 at
   to-lead "2026-11-04 07:39:25 GMT".
   **Carry to `db92a7bc`:** `git diff --stat 07e62951 db92a7bc -- . ':!docs'` lists four files —
   merge 54's three (`data/expressions.py`, `test_expression_limits.py`,
   `test_custom_objectives_expression.py`, `git diff --name-only bb9781a9 824a891d`) and
   `test_rating_version_dislocation_gate.py` +3/−3, all three lines the docstring re-point `LG 8306`
   → `LG-1998`.
2. **Merge 55's PR CI python run 41797547929**: `gh run view` reads `pull_request`, head
   `84b1d859`, `completed/success`, jobs "ruff · mypy · import-linter · pytest: success". Merge 55's
   squash `db92a7bc` has tree `ede3bf38` (`git rev-parse db92a7bc^{tree}`). Main's own push runs at
   `db92a7bc` are also green: python 41801937131, docs 41801937092, history-policy 41801937102,
   each `push db92a7bc completed/success`.
3. **S-a's gate for SL-1985** (#1421): gate 1 at `1e77bd04` (from-lead "2026-11-03 20:36 GMT":
   pytest "13 failed, 7032 passed, 22 skipped", the 13 docs-audit names; frontend 905/905; demo
   rc 124 at the 1500 s cap) plus the demo-only re-gate accepted at to-lead "2026-11-03 21:49:50
   GMT" (designed stop, 1529 s, dislocation #1 540 s).

The 15 earlier slices' gates of record are CR-1981 §2's table. This seat ran no test and no gate.

### §3. New checks proven on broken input

CR-1981 §3 stands, with its two open rows now discharged:

| Check | Broken-input proof | Where |
|---|---|---|
| `06` FR-364 floor loop (SL-1390) | scratch A (`verify is None` → `continue`), scratch B (`rate_table_diffs` verifier `{}`): each `DID NOT RAISE`, rc 1 | `LG-1998:61-80` row 11 — **FD-1651 closed** |
| FR-257 limb (2), FR-224 refusals (SL-1389) | items 2, 5, 6, 15, 19 red with the call removed | `LG-1998` row 12 — **FD-1982 closed** |
| FR-240 GLM arm (SL-1985) | six red at base | `LG-1986:60-69` |
| FR-227 withdrawal (SL-1997) | `test_errors.py` red with `errors.py` at the base | `LG-1998` row 7 |
| NFR-499 input-free attribution (SL-1997) | 7 failed at the base `analysis.py` | `LG-1998:57` |

Each proof commit is an ancestor of its PR head (§1b). A passing positive control licenses "this
check fires", not "this rule is enforced".

### §4. NFRs

- **NFR-495, NFR-496 (applied):** property NFRs, tested by assertion (§1, §1a item 8). No
  measurement owed.
- **The attribution cost:** FD-1576 is **carried, owner WK-1178**, discharge a budget NFR at the
  P3 plan review (register `:332`, dated line 2026-11-03, the maintainer's "2026-11-03 16:03:37
  GMT" ruling (B)). The S-b gate's dislocation #1 (592 s) is an environment reading, not a
  measurement against any bound.
- **FD-1983's two figures** (`LG-1545:363-364`): owed, §5.
- Nothing of WK-673 is owed to nfr-bench-1 (Thu 5 – Fri 6 Nov 2026); NFR-489 on a mounted bundle is
  WK-1250's.

### §5. Every requirement without evidence, with a PROPOSED verdict

| Item | PROPOSED verdict |
|---|---|
| `06` FR-364's `rate_table_diffs` limb | **PROPOSED: deferred with an owner — WK-1178 until the P3 plan review assigns a P3 Work; discharge event the P3 plan review.** `06-governance.md` FR-364 row, "Re-owned 2026-11-03 to P3" on the maintainer's "2026-11-03 16:03:37 GMT" ruling (A) and "2026-11-03 16:28:44 GMT", owner clause corrected by "2026-11-03 19:30:13 GMT". Its refusal is tested (`test_rating_version_evidence_floor.py:223`). |
| FD-1495's remaining limb (`RL-1470` Ruled 9, declared-reference scoring) | **PROPOSED: deferred with an owner — WK-1178, P3**, discharge the P3 plan review (register `:321`, "Closed in place 2026-11-03"; `PL-1984` DP-2 (a), the GO "2026-11-03 16:28:44 GMT"). |
| FD-1491 (FR-229's author change note) | **PROPOSED: deferred with an owner — WK-1178, P3** (register `:317`, dated line 2026-11-03, ruling (B) of 16:03:37). |
| FD-1576 (full-book attribution cost) | **PROPOSED: deferred with an owner — WK-1178** (§4). |
| FD-1983 (LG-1545's per-set S figures and the 690/976 per-policy maxima) | **PROPOSED: deferred with an owner (WK-673), undischarged.** Register `:434`: "discharged before WK-673's Work close by a slice that changes `scripts/measure-attribution-cost.py` … or carried or accepted by a dated ruling". `git log c807a59d..db92a7bc -- scripts/measure-attribution-cost.py` prints nothing; no entry after its mint names FD-1983 except the mint notes (`grep -n 'FD-1983' to-lead.md`: `:32469`, `:32481`). **Blocks the close until discharged, carried or accepted.** |
| SL-1389 item 16 — `RL-1504` DP-S5-2 condition (ii): "S5's first freMTPL2 run reports the observed quantiles … into its ledger, and the default is re-read against them at the next checkpoint" | **PROPOSED: not started, owner WK-673 by the ruling.** `LG-1582:84` reads OWED; `git grep -l abs_change_pct_quantiles -- docs` finds no record of observed figures; the S-b gate's `demo.log` prints none. No register row carries it (the F41 shape). FD candidate A. The FR-224 default `{0.99, 10}` stands unfalsified. |
| SL-1389 items 1, 7, 8, 14, 17, 18 — no recorded red first | **PROPOSED: delivered, accepted** under FD-1982 ruling (a) ("limb 1 is met"); tests located and green (§1a). |

### §5a. Binding plan-review conditions

`CR-1907` (plan review 17) still does not name WK-673: `grep -c 'WK-673'
docs/closures/CR-01907-*.md` prints 0. No later `kind: review` CR exists (the latest by `created:`
is `CR-1907`, 2026-10-25). CR-1981 §5a's four conditions stand met; its two "closing act owed"
rows (`register.md:60`, `:64`) were closed in place 2026-11-03 (#1420). **New binding condition:**
the maintainer's "2026-11-04 08:05:12 GMT" (FD-1982 ruling (a)) — **artifact: §1a of this record.**

### §5b. The owed list, generated

```text
Generated by `python3 scripts/register-owed.py WK-673` against `db92a7bc (`docs/wk673-fresh-close-2026-11-04`)`.
Mode: work item 'WK-673'. 23 owed row(s), 2 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).
```

The 23, by register line: `:60` FR-224 (F-W9-2), `:64` FR-231 (F-W10-2), `:85` FR-257 (F44),
`:285` FD-1358, `:297` FD-1420, `:299` FD-1422, `:301` FD-1425, `:303` FD-1433, `:305` FD-1439,
`:307` FD-1469, `:311` FD-1481, `:316` FD-1490, `:317` FD-1491, `:321` FD-1495, `:332` FD-1576,
`:333` FD-1578, `:335` FD-1586, `:346` FD-1651, `:383` FD-1754, `:386` FD-1757, `:424` FD-1954,
`:433` FD-1982, `:434` FD-1983. Excluded by the script: FD-1660 and FD-1679 (as at CR-1981).

**Read by hand — 22 removed:**

- **Resolved or closed in place mid-cell (the known defect), 17:** `:60`, `:64`, `:285`, `:335`,
  `:386` (closed in place 2026-11-03 by the auditor, #1420); `:297` FD-1420, `:299` FD-1422,
  `:301` FD-1425, `:305` FD-1439 (essay `status: closed`), `:307` FD-1469 (as at CR-1981); `:311`
  FD-1481, `:316` FD-1490, `:333` FD-1578, `:346` FD-1651, `:433` FD-1982 ("Resolved 2026-11-04",
  SL-1997); `:321` FD-1495 ("Closed in place 2026-11-03", SL-1985; its residual limb is §5's P3
  carry); `:85` F44 (limb (2) annotation 2026-11-03; limbs (1), (3), (4) are other Works').
- **Not WK-673's, 5:** `:303` FD-1433 and `:383` FD-1754 (WK-1178), `:424` FD-1954 (WK-675,
  Resolved 2026-10-29), `:317` FD-1491 and `:332` FD-1576 (carried to WK-1178 by the 2026-11-03
  dated lines).

**The corrected list, 1 row owed by WK-673:** `:434` FD-1983 — deferred with owner WK-673,
undischarged (§5). Every id in the generated block appears above with a resolution; the findings
below add only the two candidates that have no register row.

### §5c. Workflow steps that cite this close's requirements

```bash
git grep -n -E '\b(FR-(263|264|265|266|1397|1398|1399|224|257|231|364|240|242|221)|NFR-(495|496))\b' -- 'docs/workflows/WF-*.md'
```

18 lines at `db92a7bc`, the same as CR-1981's. Since `c807a59d` the journeys changed only at WF-699
C1 (`55bddaf2`, CR-1981's own commit) and WF-702 (#1420, no hit above). Every step verdict of
CR-1981 §5c stands, re-read at `db92a7bc`, with one updated:

| Journey | Step | Ids | Verdict |
|---|---|---|---|
| WF-699 | E2 (`:96`) | FR-257/260, `06` FR-352/363 | **still disagrees.** E2 still says "Evidence completeness is checked at submission: structural diff, **rate diffs**, …". `06` FR-364 now re-owns the `rate_table_diffs` limb to P3 and says "a policy naming the kind is refused, naming it". The re-owning ruled the limb, not the journey line; no register row, essay or dated workflow line carries E2. FD candidate B. |

## Findings

No id is written here; each is the lead's to file.

- **FD candidate A — `RL-1504` DP-S5-2 condition (ii) was never discharged: no ledger records the
  observed `abs_change_pct_quantiles` of a freMTPL2 Dislocation Run, so FR-224's default threshold
  `{quantile: 0.99, max_abs_change_pct: 10}` was never re-read against data.** Evidence:
  `RL-1504` item 3 condition (ii) and `:161-163`; `PL-1500` Acceptance item 16; `LG-1582:84` OWED;
  no hit outside the spec, contract, plan and ruling (`git grep -l abs_change_pct_quantiles --
  docs`); FD-1982 names items 2–6, 8, 9, 14, 15, not 16. Proposed LOW (the default is a
  per-workspace setting and governs only when unset; a ruled check that nobody ran). Every gate's
  WF-699 demo runs a Dislocation Run on the freMTPL2 sample, so the reading is one query away.
- **FD candidate B — WF-699 E2 says rate diffs are checked at submission; `06` FR-364 re-owns
  `rate_table_diffs` to P3 and the default policy names no such kind.** CR-1981 FD candidate 2's
  journey limb; the 2026-11-03 rulings disposed of the requirement limb only. Proposed LOW: off the
  exit-demo path (a dated workflow correction line, the 16:02:43 rule's form, would discharge it).

**Closing acts owed (not findings):**

1. SL-1985 and SL-1997: each `status: active` (`docs/roadmap.md:1031`, `:1051`) with an empty
   Audit section (`LG-1986:244-246`, `LG-1998:47-49`); `LG-1986` and `LG-1998` `active`. The
   auditor's slice audit and the `closed` acts, or a dated ruling that this record's §1b evidences
   them as FD-1982 ruling (a) did for SL-1388 and SL-1389.
2. The register rows FD-1481 (`:311`), FD-1490 (`:316`), FD-1495 (`:321`), FD-1578 (`:333`),
   FD-1651 (`:346`) and FD-1982 (`:433`) still read "this PR, number written at the merge" (or "its
   number and squash written at the merge's date-of-record"); `grep -c -E '#1421|dfbce89b'` and
   `'#1426|db92a7bc'` over `register.md` print 0 each. The numbers are #1421 `dfbce89b` (FD-1495)
   and #1426 `db92a7bc` (the other five).
3. `PL-1984` reads `status: draft` while both its rows are merged.
4. `register.md:60` (F-W9-2) and `:85` (F44) still say LG-1582's red-first "is OWED, FD-1982";
   discharged by SL-1997 (§1a). A dated annotation, not an edit of the earlier text.

## §R. Re-test of CR-1981's findings

CR-1981's verdict ("not ready for acceptance at `c807a59d`") named four blockers. Each, at
`db92a7bc`:

| CR-1981 item | What changed (PR, squash) | Status now |
|---|---|---|
| 1. FD-1481 open | SL-1997, #1426 `db92a7bc`: the 15-digit characterisation pin (`test_rating_wire_order.py:245`) | **closed** (register `:311`, essay `closed`) |
| 1. FD-1490 open | SL-1997, #1426 `db92a7bc`: the registry entry dropped (RL-1958 (c)) | **closed** (`:316`) |
| 1. FD-1491 open | ruling (B), recorded by #1420 `4df71cd7` | **carried to P3, owner WK-1178** (`:317`) |
| 1. FD-1495 open | SL-1985, #1421 `dfbce89b` | **closed**; Ruled 9's limb carried to P3, WK-1178 (`:321`) |
| 1. FD-1576 open | ruling (B), #1420 `4df71cd7` | **carried, owner WK-1178** (`:332`) |
| 1. FD-1578 open | SL-1997, #1426 `db92a7bc`: `AttributionError(CodedError)`, input-free text | **closed** (`:333`) |
| 1. FD-1651 open | SL-1997, #1426 `db92a7bc`: the two broken-loop proofs | **closed** (`:346`) |
| 2. FD candidate 1 | filed as FD-1982 (#1420 `4df71cd7`); five proofs by SL-1997 (#1426); ruling (a) "2026-11-04 08:05:12 GMT" | **closed**; its condition is discharged by §1a, subject to the lead's verdict |
| 2. FD candidate 2 | FR-364's limb re-owned to P3 in `06` (#1420 `4df71cd7`), owner WK-1178 | **requirement limb deferred with owner**; the WF-699 E2 limb is **unfiled** — FD candidate B |
| 2. FD candidate 3 | filed as FD-1983 (#1420 `4df71cd7`) | **open, undischarged** — the one owed row (§5b) |
| 3. Closing acts: register `:60`, `:64`, `:85`, `:285`, `:335`, `:386`; FD-1439's essay | #1420 `4df71cd7` | **done** (each "closed in place 2026-11-03"; FD-1439 `status: closed`) |
| 3. LG-1570, LG-1582, LG-1633 empty Gate tables | none | unchanged; LG-1570 and LG-1582 accepted by FD-1982 ruling (a), LG-1633's proofs by FD-1651's close |
| 4. Fresh full gate OWED | the S-b gate at `07e62951` + CI 41797547929 (§2) | **met** |

## Replan check (`CLAUDE.md` §14, `RFC-1248`)

1. **Completion — yes.** The 16-id deliverable set is unchanged; two fix slices were added
   (SL-1985, SL-1997) and two limbs left the Work (FR-364 `rate_table_diffs`, FD-1495's Ruled 9 —
   both to P3). Moves no Work scope beyond what the 3 Nov rulings recorded.
2. **Omission — yes.** RL-1504 condition (ii)'s reading (FD candidate A) is needed and named
   nowhere; FD-1983 has an owner and no slice.
3. **Skills and research — yes.** As CR-1981: `scope-audit.py` cannot run under `--light`;
   `register-owed.py` counted 17 resolved rows as owed here (22 of 23 removed by hand). Neither
   moves scope.
4. **Drift — yes.** WF-699 E2 against `06` FR-364 (§5c). Moves no slice or phase.
5. **Shape — no.** No phase boundary or Work scope moved beyond the dated 3 Nov re-ownings.

`register-owed.py review` at `db92a7bc` (through `run-heavy.sh`, rc 0): **31 owed rows** (11
excluded as opening with a resolution marker).

**Triggers:**

- A phase boundary or Work scope moved: **not fired** (the P3 carries are dated rulings of 3 Nov,
  already recorded "no trigger" at "2026-11-03 16:03:37 GMT").
- An exit criterion at risk: **not fired.** The code blockers of CR-1981 are merged; what remains is
  one LOW deferral (FD-1983), two LOW candidates and docs-only closing acts, against code freeze Tue
  10 Nov and docs freeze Wed 11 Nov 2026.
- A replan decided: **not fired**.
- A finding that moves a slice or a phase: **not fired.**

**PROPOSED:** no trigger; carried to the §14 review before the exit demo (Wed 18 Nov 2026). **The
verdict is the lead's.**

## Verdict

PROPOSED: **not ready for acceptance at `db92a7bc` — on records only.** The code of WK-673 is
complete: every deliverable carries a read assertion (§1, §1a, §1b), every new refusal is proven red
first, and the gate of record is green under item 31 with main's push CI green at `db92a7bc`. The
close is blocked by:

1. FD-1983 — discharged by a slice, carried or accepted by a dated ruling (§5);
2. FD candidate A (RL-1504 condition (ii)) — filing, then the reading or a dated disposition;
3. the SL-1985 / SL-1997 slice audits and closing acts, or a dated ruling (closing act 1).

FD candidate B and closing acts 2–4 are docs hygiene that need not block. The §5 verdicts are
proposals. **The close itself is the user's dated line.**

## 2026-11-04 — delta: batch 8 landed

*(Dated line 2026-11-04 11:28 GMT, by the auditor, read at `origin/main` e3c150c4827a2f2f29e5314bb264c24125d714a7. No verdict is rewritten.)*

- **Batch 8 merged as #1427**, squash commit `e3c150c4827a2f2f29e5314bb264c24125d714a7`, at 2026-11-04 11:25:06 GMT (from-lead "2026-11-04 11:25:06 GMT").
- **What it carries on main**, each read at that squash:
  - SL-1985 and SL-1997 closed: `docs/roadmap.md:1031` and `:1051` (`status: closed`); their ledgers `LG-1986` and `LG-1998` carry `status: closed` at `:5`. Route (a) of "2026-11-04 09:57:14 GMT", adopted in "2026-11-04 10:00:29 GMT", is written at `docs/ledgers/LG-01986-wk-673-slice-sl-8303-fd-1495-glm-control-factor-red-first-slice-ledger.md:248`.
  - The register rows annotated with the PR number: `docs/findings/register.md:60` and `:85` (LG-1998, SL-1997, #1426 `db92a7bc`).
  - PL-1984 active: `docs/plans/PL-01984-wk-673-remediation-fd-1495-fd-1490-fd-1578-fd-1651-fd-1481-before-close-work-plan-delta.md:6`.
  - FD-1983's carry: `docs/findings/register.md:434` (the FD stays open, carried to P3; the owner and phase struck and re-set); essay `docs/findings/FD-01983-two-wk-673-deferrals-of-lg-1545-s-13-live-only-in-the-ledger-the-per-set-s-figures-and-the-690-976-per-policy-maxima.md:5` (`status: active`).
  - FD-2002 closed: `docs/findings/FD-02002-rl-1504-dp-s5-2-ii-s-observed-abs-change-pct-quantiles-of-a-fremtpl2-dislocation-run-are-recorded-nowhere.md:5` (`status: closed`), with its Resolved line at `:50`. The register carries no row for it (`grep -c 'FD-2002' docs/findings/register.md` reads 0 at this tree); the essay is its record.
- **The 10:00:29 condition for CLOSE-READY (batch 8 on main) is met; the user's dated line is the close.** The §5 verdicts above stay PROPOSED and the lead's.
