---
id: LG-8048
family: ledger
title: WK-673 slice SL-1702 — FD-1679, FR-242's drafted change summary pairs a rate table's versions through the table step and refuses no pin set (PL-1701), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-14
owner: executor
tree: 81e9d4cc5a9b681981a3e1c691f6218c7ef6161c
phase: P2
work: WK-673
slice: SL-1702
plans: [PL-1701, PL-1677, PL-1267]
corrected_by: []
relates: [PL-1701, PL-1677, SL-1702, SL-1678, LG-1681, RL-1707, FD-1679, RL-1538, RL-1498, FR-242, FR-219, FR-231, FR-232, FR-237, FR-1399]
---

# LG-8048 — WK-673 slice SL-1702: the drafted change summary pairs rate tables through the `table` step

**GO:** the lead's relay, from-lead to `executor-sl1702`, "GO for SL-1702 (PL-1701), from the maintainer's to-lead '2026-10-14 13:32:07 BST'", build from `3ac63e35`, gate ALONE after SL-1695's, at load1 < 6 with all three locks, the demo `wf-699` with the frontend, pytest timeout 5400 s. The maintainer's entry itself is in `to-lead.md` (local, not in the repository); this record quotes the lead's relay of it, not the entry.
**MERGE-ACK:** not yet given.
**Audit:** not yet written; the auditor writes it.

## Tasks

### Scope

`docs/roadmap.md`, heading *"SL-1702 — WK-673 fix slice — RL-1707 / FD-1679: FR-242's drafted change summary pairs a rate table's versions through the `table` step that names them, and refuses no pin set"*, Work `WK-673`, plan `PL-1701` (a dated delta to `PL-1267`), ruling `RL-1707`. The row's body is not copied here; read it at that heading.

Requirements: `03` FR-242 (drafting limb: T1 and T2); FR-219, FR-231, FR-232, FR-237, FR-1399 read only. Discharges FD-1679's remaining limb, DP-P1. On the G2 path: merges before `SL-1543`.

Rulings in force, from `PL-1701`'s Decision points: DP-1 (a), DP-2 (a), DP-4 (a) and DP-5 (a), all ruled by the maintainer (by delegation), "2026-10-14 10:00:17 BST" (B). DP-5 (a) is set semantics: a ref listed twice is the ref once. The closing PR also sets `PL-1677` `closed` and carries FD-1679's register annotation: the maintainer (by delegation), to-lead "2026-10-14 12:02:46 BST" item (2), as `PL-1701`'s Task 5 quotes it.

### Task list

| Task | Plan step | Acceptance check | State |
|---|---|---|---|
| 0 | `PL-1701` Task 0 | LG scaffold, SL row `active`, plan `active` | done at `171d6852` (scaffold in this commit's successor) |
| 2 | `PL-1701` Task 2 | R1–R9, E8, U1, U2 red on the base by their causes | done at `65daf404`, re-run at `3ac63e35` (Build log) |
| 1 | `PL-1701` Task 1 | T1 and T2 verbatim | done at `af96ea6f`, checked by script (Build log) |
| 3 | `PL-1701` Task 3 | pairing, shape, guard removed; both files green; broken-input proof | code at `d87770c4`; green runs and proof are the gate window's (Gate) |
| 4 | `PL-1701` Task 4 | generated contract | `1ed595d5`; frontend client and type-check at the gate |
| 5 | `PL-1701` Task 5 | gate, closing acts | pending |

**Renamed tests (DP-2 (a)), old → new.** SL-1678's three functions were already flipped and renamed in the prep commit `65daf404`; the old names and old asserts are in `LG-1681`'s Task list. The prep file defines `test_r3_a_candidate_adding_a_second_version_names_it_alone` (parametrized `two_then_one` / `one_then_two`), `test_r3_a_candidate_dropping_one_of_two_baseline_versions_names_it_alone`; `_assert_refused` is deleted.

### Gate

ALONE gate-1 window, script `sl1702-gate.sh` (local, `.claude/jobs/…/tmp/`), logs in `sl1702-gate/`. Gated head `3e087672c487bdac583a86076c7b4d4d60f556b5`, tree `81e9d4cc5a9b681981a3e1c691f6218c7ef6161c`, started 2026-10-14T15:00:31Z, ended 2026-10-14T16:46:08Z. Load1 over the run, every 10 minutes: 8.41, 16.60, 10.00, 24.03, 17.39, 23.15, 21.92, 13.25, 19.05, 15.19, 9.11; the run was never below 6 after the start, so no timing figure is a measurement. Tree after the gate: 0 changed paths.

**Step 0, the broken-input proof (`PL-1701` Task 3 Step 6).** With `if previous is not None:` replaced by `if False:` in `pair_rate_tables`, both test files ran `6 failed, 27 passed`:
- FAILED `test_r1_a_repointed_step_and_a_seed_pin_are_both_named`
- FAILED `test_r2_a_repointed_step_beside_an_unchanged_seed_pin_is_one_entry`
- FAILED `test_r5_a_step_entry_and_an_extra_pin_are_both_named`
- FAILED `test_r6_a_step_pointing_at_another_table_is_two_entries_without_diffs`
- FAILED `test_r7_a_step_repointed_to_another_table_names_both_with_its_step_id`
- FAILED `test_r8_a_baseline_listing_one_ref_twice_is_not_refused`

R1, R2, R5 and R6 fail as required; E1 (`test_wf699_e1_…`) passes. The file was restored with `git checkout`, the tree was clean, and the restored run was `33 passed`.

| Stage | rc | Note |
|---|---|---|
| preflight (head guard, clean tree, createdb, alembic upgrade, 1 head, containers, pg_isready) | ok | |
| ruff / mypy / lint-imports | 0 / 0 / 0 | |
| req-coverage / `generate-contracts.py --check` | 0 / 0 | |
| audit-docs | 1 | check 29 (the FD-1679 register row's annotation named no PR, commit or docs path), check 31 (working-id gap 1717 to 8048, this ledger's id), check 32 (the ruling's working id, cited in this ledger's build log), check 33 (`PL-1677` status `closed`); checks 29, 32 and 33 are fixed in the docs-only commits after the gated head |
| pytest (timeout 5400) | 1 | `17 failed, 5843 passed, 6 skipped` in 4517 s; see below |
| pnpm install / generate:api / lint / type-check / build | 0 / 0 / 0 / 0 / 0 | |
| pnpm test | 1 | `1 failed, 729 passed`: `src/views/__tests__/RatingDesignView.test.ts`, `FR-1530: loads the algorithm the version pins, and draws one node per step`; classification is the lead's |
| `demo.py --journey wf-699` (with the frontend) | 124 | the journey finished (`journey done in 345s`, every step `ok` or `SKIPPED` for Phase 3, E1 `ok`), the frontend answered 200 at `http://localhost:5173/`, and the command then waits for Ctrl-C until the script's `timeout -s INT 1500` ended it; no step failed |

**The 17 pytest failures.** One is `backend/tests/test_score_rate_limit.py::test_the_counter_is_shared_across_replicas_and_the_refusal_carries_retry_after`, the rate-limit flake FD 8049 names, not re-run in this window. The other 16 are the docs-audit tests, which read the real tree and fail with it: `tests/test_audit_docs_finding_citations.py` (1), `test_audit_docs_ids.py` (2), `test_audit_docs_process_core_digest.py` (2), `test_audit_docs_w37_11_ceiling.py` (1), `test_doc_index.py` (1), `test_register_lint.py` (6), `test_register_owed.py` (1), `test_repository_invariants.py` (2). They read the same four audit findings; whether they pass once those are fixed is not yet shown by a run.

### Audit

**Auditor `auditor-sl1702`, 2026-10-14 17:57 BST (`TZ=Europe/London date`).** Range `origin/main...ba47b378` (`origin/main` = `beee5ebe`, an ancestor of the head: `git merge-base --is-ancestor origin/main ba47b378` exit 0). The head is the executor's re-merge of main on top of its docs commit `3f6ca9fa`; the gated head is `3e087672` (tree `81e9d4cc`).

**1. Change set** (`git diff --name-only origin/main...ba47b378`, 13 files, +516/-87): code `backend/src/app/platform/change_summary.py`, `backend/src/app/platform/rating_versions.py`, `packages/model-schema/src/model_schema/rating.py`; tests `backend/tests/test_change_summary_draft.py`, `backend/tests/test_rating_version_change_summary_route.py`; contract `docs/contracts/openapi/generated.json`; spec `docs/specs/03-rating-engine.md`; and docs `docs/INDEX.md`, `docs/findings/register.md`, this ledger, `PL-1677`, `PL-1701`, `docs/roadmap.md`.

**2. Code identity.** Loop: for every non-`docs/`, non-`.claude/` path in that range, `git rev-parse ba47b378:<f>` against `3e087672:<f>` and `origin/main:<f>`. All 5 code paths print `gated` (blob equal at the new head and at the gated head). A second loop over `git diff --name-only 3e087672 ba47b378` outside `docs/` (6 paths: `backend/tests/test_wf699_journey.py`, `examples/fremtpl2/README.md`, `examples/fremtpl2/journey.py`, `pricing_core/rating/analysis.py`, `test_quote_input_raise_sites.py`, `test_rating_attribution.py`, all SL-1695's #1306) prints `=main` for each: the blob equals main's. So no code path in this slice differs from the gated blob or from main. Not gated: the combination with #1306's code (the gated tree is `81e9d4cc`, not the head's); the PR's CI at the head is that check.

**3. The 13:32:07 ACK checklist.**
- `generated.json` vs main: `git diff origin/main...ba47b378 -- docs/contracts/openapi/generated.json` is exactly 2 hunks in `RateTableChange`: the description text (`@@ -12391`) and the `step_id` property (`@@ -12422`, `anyOf` string / null, not added to `required`). `git diff --name-only origin/main...ba47b378 -- docs/contracts` lists that one file. MET.
- `03` re-anchored by content, and `generated.json` regenerated after the last main re-merge: the `03` diff vs main is exactly two hunks, the FR-242 cell and the `change-summary-draft` row (§5.1), both found by content (no line offsets are cited). `uv run python scripts/generate-contracts.py --check` at the head, under the gate-2 flock: rc 0, `49 generated contracts match the models`. The last main re-merge (#1306) touches no model-schema or route file, so the check at the head covers it. MET.
- `git grep -n 'FD-1679' ba47b378 -- backend/src` prints nothing (exit 1). MET.
- T1/T2 verbatim: both blockquotes of `RL-1707` §"DP-T" (`:243-254`, `:259-261`), with `<date>` = 2026-10-14, `<RL>` = RL-1707, `<SL>` = SL-1702 substituted, were compared with `03` after removing only the markup characters `` ` `` `*` `~` and normalising whitespace: T1 found (1024 chars), T2 found (254 chars). The strike runs over the whole SL-1678 clause (`**409** … (**added 2026-10-12, SL-1678, FR-242**)`) as the ruling requires. MET.
- Broken-input proof: gate.log Step 0 prints `broken: 1 file changed, 1 insertion(+), 1 deletion(-)`, `step 0 broken run rc=1`, the six FAILED lines (R1, R2, R5, R6, R7, R8; `6 failed, 27 passed`), then `step 0: test_r1_ / r2_ / r5_ / r6_ FAILS as required`, `E1 passes under the break`, `tree clean after restore ok`, `step 0 restored run rc=0` (`33 passed`). MET. (R7 and R8 also fail under the break, beyond the four required; harmless.)
- `PL-1677` → `retired`, not `closed`: the front matter reads `status: retired`, with a dated reason citing the 13:32:07 GO and the 17:30:21 correction; the body is not edited (`git diff` shows the single `status:` line changed). MET. FD-1679's register discharge line: a dated line appended inside the row (the essay is untouched), naming the ledger path, `PL-1701`, `RL-1707`, "Resolved on `SL-1702`'s merge", the PR number to be added later. `python3 scripts/register-lint.py` at the head: rc 0, `0 violations`. MET (see F2).
- Code blob-identical to the gated head: item 2. MET.

**4. The gate result (logs in the lead's `sl1702-gate/`, gated head `3e087672`).**
- Step 0: item 3 above. Start load 8.41 / 11.88 / 11.97; end 13.30 / 11.65 / 13.20 (heavy, as for every gate today).
- rc: ruff 0, mypy 0, lint-imports 0, req-coverage 0, contracts 0; audit-docs 1; pytest 1 (`17 failed, 5843 passed, 6 skipped`, 4517 s); pnpm install / generate:api / lint / type-check / build 0; pnpm test 1; demo 124.
- audit-docs at `3e087672` printed `FAILED (3)`: check 31 (gap 1717 to 8048, the unminted ledger, accepted until minted), check 32 (the ruling's working id at line 60 of this ledger), check 33 (`PL-1677` `closed`), plus check 29 (the register annotation). At the new head, under the gate-2 flock, `audit-docs.py` prints `FAILED (1)`: `check 31: gap in the full allocation between 1718 and 8048` only (the gap moved from 1717 to 1718 because #1306 minted `LG-1718`). Checks 29, 32 and 33 are cleared. Accepted until `LG-8048` is minted.
- pytest's 17 F. (a) `backend/tests/test_score_rate_limit.py::test_the_counter_is_shared_across_replicas_and_the_refusal_carries_retry_after` (`assert 409 == 429` at `:128`): the rate-limit flake the maintainer's entries call FD 8049 (the 14:30:54 re-run rule); the file does not mention `change_summary` or `change-summary` (0 hits), and it was not re-run in this window. (b) The 16 docs-audit tests read the real tree and fail with it, each citing the same four audit findings (checks 29, 31, 32, 33): `test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`; `test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`; `test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`, `::test_the_committed_digest_currently_matches_the_committed_spec`; `test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`; `test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity` (cause: the check-31 gap); `test_register_lint.py` ×6 (`test_the_live_register_passes`, `test_check_29_is_wired_into_the_docs_gate`, `test_residue_counts_are_never_treated_as_lint_failures`, `test_register_lint_main_prints_the_residue_line`, `test_check_29_note_carries_the_residue_line`, `test_phase1b_residue_count_matches_check_29s_own_count`; cause: check 29, the register row); `test_register_owed.py::test_check_29_wiring_is_undisturbed`; `test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`, `::test_journey_citations_are_audited_in_ci`. 1 + 16 = 17. Not re-run: I run no pytest (charter); the re-pass of the 16 is shown only by the audit-docs rc above, and the check-31 cause persists until the ledger is minted.
- FE test: `src/views/__tests__/RatingDesignView.test.ts` "FR-1530: loads the algorithm the version pins, and draws one node per step" failed at 1080 ms (`Unable to find a label … input step Driver age (s_in_age)`), `1 failed, 729 passed`. The lead classifies it by run (the maintainer's 17:30:21 entry). My part of the entry's (ii): `grep -rln 'RateTableChange\|ChangeSummaryDraft\|change-summary-draft' frontend/src` outside `generated` prints nothing (exit 1), so no non-generated frontend file, including the view and its test, names the changed type. Lead's classification by run: (pending: the lead's line).
- Demo (`wf-699`, with the frontend): rc 124. The log prints `S1 ok prod scored 46332 minor units from the live version`, `journey done in 345s`, the change-summary-draft GET (200 at 16:27:38) inside the journey, the frontend answering 200 at `http://localhost:5173/`, then the script's hold for Ctrl-C ended by its own `timeout`. 124 is the hold's timeout, not a step failure; `demo.log` shows no failed step.

**5. Findings.**
- **F1 (INFO).** FD 8049 is a working id, not on main (a repository grep of main finds it only in this ledger; the channel entries name it). Disposition: accepted class per 14:30:54 and 17:30:21; the lead may require the one re-run. Not blocking.
- **F2 (LOW).** The FD-1679 register line and this ledger's Scope paragraph (`:31`) say `PL-1677` is retired / set `closed` citing the 12:02:46 item (2). That entry said `closed`; the correction to `retired` is 17:30:21 (`PL-1677`'s own front matter cites both correctly). Disposition: the executor adds "corrected to `retired` by 17:30:21" to the register parenthetical (living row) before the ACK; the Scope sentence is a past statement of the plan's wording and may stay, since `PL-1701` Task 5 is quoted there.
- **F3 (INFO).** The gated tree is not the head's tree: the head also carries #1306's code (`=main` blobs). Disposition: same handling as SL-1683; the PR's CI at the head is the combination check.
- **F4 (INFO).** After the re-merge, `audit-docs` still prints check 31 (gap 1718 to 8048) and the 16 docs-audit tests reflect the real tree; both clear only when `LG-8048` is minted, which is the lead's step at the PR.
- No HIGH or MEDIUM finding. The barred word on added lines in the range: `git diff origin/main...ba47b378 | grep '^+'` count 0.

**Proposed verdict (the lead's to give): CLEAN**, conditional on (a) the lead's by-run FE classification, (b) F2's one-line register fix, and (c) PR CI green at the final head. Audit-docs at `ba47b378` under the gate-2 flock: rc 1, check 31 only (accepted until the mint).

### Build log

- **2026-10-14, prep (`65daf404`, re-pointed at `3ac63e35`).** Worktree `.claude/worktrees/sl-1702`, branch `sl-8003-wk673-dpp1-fix`. `git merge-tree --write-tree origin/main HEAD` rc 0; `origin/main` merged (`50d95b2c`). the ruling's working id re-pointed to its minted id `RL-1707` in the two test files (4 occurrences). Reds run on the base through `run-small.sh`, one file per call, against the per-worktree database `gipricing_sl-1702_8a302640`, created with `createdb -T gipricing` and `alembic upgrade head` (disclosed to the maintainer by the lead; its keep-or-drop ruling is the lead's):
  - route file: 11 failed, 10 passed. R1, R2, R3 (three cases), R4, R5, R8, R9: `assert 409 == 200`, the detail naming FD-1679 (R8 and R9: "at versions 1 and 1"). R6: `assert 1 == 2` on the length. R7: `assert [None, None] == ['t', 't']`. E8, E1 and the first-version test pass.
  - draft file: U1 and U2 fail with `ValidationError` on `RateTableChange.step_id`, `Extra inputs are not permitted`, at `test_change_summary_draft.py:149` and `:166`.
- **2026-10-14, Task 1 (`af96ea6f`).** T1 and T2 applied with `<date>` = 2026-10-14, `<RL>` = RL-1707, `<SL>` = SL-1702. Checked by script against the whitespace-normalised blockquotes of `RL-1707` §"DP-T": both are found verbatim in `03-rating-engine.md`.
- **2026-10-14, Task 3 (`d87770c4`).** `pair_rate_tables`, `_table_refs`, `_entry_order` in `change_summary.py`; `RateTableChange.step_id`; `_rate_table_pins` replaces `_pins_by_slug`; the docstring sentence replaced. Premises read for this edit at `3ac63e35`: a–d, f, g, h (the code replaced); i, j, k–q not re-read. `git grep -n FD-1679 -- backend/src` prints nothing. A first `ruff format` run over `backend/src` and `packages` reformatted 86 files; all were reverted with `git checkout` before any commit, and the edits re-applied.
- **2026-10-14, Task 4 (`1ed595d5`).** `scripts/generate-contracts.py` wrote `docs/contracts/openapi/generated.json` only: two hunks in `RateTableChange`, the `step_id` property (`anyOf` string / null, not in `required`) and the description text.
- **2026-10-14, activation (`171d6852`).** SL-1702 row and `PL-1701` `active`.

## PRs

Not yet opened.
