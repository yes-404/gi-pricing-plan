---
id: LG-1681
family: ledger
title: WK-673 slice SL-1678 — FD-1679 loud guard, the drafted change summary refuses two versions of one rate-table slug (PL-1677), slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: f7ca32ec5450d61aa6948e82fbf6262ac1ed307a
phase: P2
work: WK-673
slice: SL-1678
plans: [PL-1677, PL-1267]
corrected_by: []
relates: [PL-1677, PL-1267, SL-1678, FD-1679, SL-1503, RL-1498, RL-1538, SL-1543, FR-242, FR-237]
---

# LG-1681 — WK-673 slice SL-1678: the FD-1679 loud guard

*(Minted 2026-10-12 as LG-1681 from working id 9899, at the mint turn, allocated by the lead. Live citations are re-pointed; quoted entries, command output and the dated gate table keep the working id they were written under.)*

**GO:** the lead's from-lead entry "2026-10-12 06:05:28 BST — GO SL-1678 (WK-673, FD-1679 loud guard) → executor-sl1678 (sonnet)" (`channel/from-lead-2026-10-09.md`), citing the maintainer's (by delegation) entries "2026-10-12 05:57:57 BST" (ACK: DP-K rate_tables only, DP-G1 409, DP-G2 inside `_pins_by_slug`) and "2026-10-12 05:58:56 BST" (FD-1679 mints in the same PR) in `to-lead.md`.
**MERGE-ACK:** not yet given.
**Audit:** written 2026-10-12 by `auditor-sl1678` (the section below); verdicts are proposed, the lead's to give.

## Tasks

Base: branch `sl-1678-wk673-fd1679-guard`, worktree `.claude/worktrees/sl-1678`, cut from `origin/pl-9896-wk673-fd9895-guard` at `f7ca32ec5450d61aa6948e82fbf6262ac1ed307a` (PR #1294, the mint of `PL-1677`/`SL-1678`/`FD-1679`, not yet on `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a`). `origin/main` is merged in once #1294 lands. The activation commit is the branch's first.

### Task 0 — preconditions (`PL-1677` Task 0)

- Premise c re-read at the base: `backend/src/app/platform/rating_versions.py` `_pins_by_slug` still reads `return {ref.slug: ref for ref in Pins.model_validate(pins).rate_tables}`; premises a, b, d–i to be re-read and recorded here before Task 2.
- `gh pr list --state open` at the start: #1292, #1293, #1294 (no other writer on the write set). `to-lead.md` read to its tail: the last entry on `FD-1679` is the maintainer's (by delegation) "2026-10-12 05:58:56 BST"; nothing later rules on `pins_by_slug`, the change summary, DP-K, DP-G1 or DP-G2.


### Tasks 1 and 2 — spec clause, Reds 1–4, the guard (2026-10-12)

**Test DB:** own database `gipricing_sl-1678_f12bc072` (`createdb -T gipricing` in the container, `alembic upgrade head` rc 0). All runs through `run-small.sh`, `-k "pinning_two or first_version_pinning"` on the base code (no guard), file `backend/tests/test_rating_version_change_summary_route.py`.

**Reds on the base code (before any change to `rating_versions.py`), each by its cause: `3 failed, 1 passed`.**

| Red | Order / side | Create | Today's `GET change-summary-draft` | Fails with |
|---|---|---|---|---|
| 1 | candidate `[X@two, X@one]`, baseline `[X@one]` | 201 (asserted) | **200**, `rate_tables == []` (the edited table's change silently dropped) | `assert 200 == 409` |
| 2 | candidate `[X@one, X@two]`, baseline `[X@one]` | 201 (asserted) | **200** with a FALSE `X one→two` entry, though the candidate still pins `X@one` | `assert 200 == 409` |
| 3 | baseline `[X@one, X@two]`, candidate `[X@two]` | `_insert` | **200**, `rate_tables == []` | `assert 200 == 409` |
| 4 | first version `[X@one, X@two]`, no baseline | 201 | 200, `baseline` null, `rate_tables == []` | passes on the base: a **guard**, not a red |

**Red 2's response, verbatim (the maintainer's (by delegation) 05:57:57 BST direction to quote it):**

```text
{"baseline":"rating_version:motor-rv@1","structural_diff":{"added_steps":["s_extra"],"removed_steps":[],"changed_steps":[{"step_id":"s_out","field":"consumes","before":["payable"],"after":["payable2"]}],"repointed_tables":[],"input_contract_changed":false,"outputs_changed":false,"sub_graph_mounts":[],"input_contract_deltas":[],"output_deltas":[]},"rate_tables":[{"slug":"motor-driver-age-5100fb12","from_ref":"rate_table:motor-driver-age-5100fb12@1","to_ref":"rate_table:motor-driver-age-5100fb12@2","diff":{"changed_cells":1,"max_abs_change_pct":"4.166666666666666666666666667","exposure_weighted_mean_change_pct":null,"portfolio_exposure":null,"matched_exposure":null},"pending":false}],"text":"Drafted against rating_version:motor-rv@1.\nStep added: s_extra.\nStep s_out field consumes changed: ['payable'] -> ['payable2'].\nRate tables (unweighted, no portfolio joined):\n- motor-driver-age-5100fb12: version 1 -> 2, 1 cell(s) changed, largest absolute change 4.166666666666666666666666667%.\nWhy:\nExpected impact:"}
```

It reports `version 1 -> 2` for a candidate that pins both versions.

**Green:** `_pins_by_slug` raises `PlatformError("VALIDATION_FAILED", …, 409, …)` naming the slug and FD-1679 (DP-G1, DP-G2); `draft_change_summary_for`'s docstring gains the sentence. The file: `12 passed` (8 existing unchanged, Reds 1–3 green, Red 4 green). `create_rating_version` is untouched.

**Broken-input proof (Step 5):** with the guard's `if` disabled (`if False and ref.slug in by_slug:`), the same file gives `3 failed, 9 passed`: Reds 1–3 fail again, Red 4 and the 8 existing tests pass. The guard was restored (file bytes identical to the green run).

**Spec:** `docs/specs/03-rating-engine.md` §5.1 change-summary-draft row, a dated clause appended (added 2026-10-12, SL-1678, FR-242). `generate-contracts.py --check` rc 0; `git diff origin/main --stat -- docs/contracts` prints nothing. `ruff check` (touched files) clean; `mypy` clean (239 source files). `audit-docs.py`: check 31 only (working-id gap, expected until the mint).

**Acceptance 4 note:** the test file's diff against the base is additions plus one changed line, the import `from backend.tests.approved_rows import add_approved` → `… import add_approved, mark_approved` (ruff's isort would merge a second line); no existing test body changes.
### Task 3 — the full two-half gate (2026-10-12)

Granted by the lead at head `d01cf107bf01f76fdb19527e7527a1da269e3c93` (from-lead "2026-10-12 06:13:21 BST" entry's grant message), clean tree, own database `gipricing_sl-1678_f12bc072` recreated from the template, run under `flock -w 14400 /tmp/slots/gate-1` through `slot-preflight.sh` (preflight ok: head guard, clean tree, slot held + `GIP_GATE_SLOT` exported, containers healthy, `alembic upgrade head` rc 0, 1 head). Output `~/gi-pricing-plan.local/scratch/sl1678/gate.out`, stage logs in `scratch/sl1678/logs/`. Base `f7ca32ec` (#1294 not yet on main at this head).

| stage | exit | cause |
|---|---|---|
| ruff | 0 | |
| mypy | 0 | |
| import-linter | 0 | |
| pytest | 1 | 13 failed, 5734 passed, 6 skipped (47 min 22 s): all 13 are the audit-on-tree test class (9 files), failing on check 31 only |
| audit-docs | 1 | check 31 only: gap 1673→1677 (1674–1676 not on this base) and gap 1679→9899 (this ledger's working id, then unminted) |
| req-coverage | 0 | |
| contracts --check | 0 | |
| frontend install | 0 | |
| frontend generate:api | 0 | |
| frontend lint | 0 | |
| frontend type-check | 0 | |
| frontend test | 0 | |
| frontend build | 0 | |

Both failing stages are the expected working-id reds (the same class as the 13 on LG-1673's gate); the check-31 gaps close at the merge-main re-merge and the mint. The lead's merge-tree re-checks after #1294 lands are the proof that they close.

## PRs

- Opened at the mint turn, 2026-10-12: title `fix(rating): the drafted change summary refuses two versions of one rate-table slug — SL-1678 (FD-1679)`; PR number and merge commit: not yet merged. Merges after #1295.

## Closing acts (mint turn, 2026-10-12)

Merge head: `origin/main` `50bbdd96` (carrying #1294's `PL-1677`, `SL-1678`, `FD-1679`) merged into the slice branch at `7757a2f8`. Gate: at `d01cf107bf01f76fdb19527e7527a1da269e3c93`, accepted by the lead as check-31-only after reading all 13 failure bodies (from-lead "2026-10-12 07:38:09 BST"). The 13 failing tests, by file: `test_audit_docs_finding_citations.py` (1), `test_audit_docs_ids.py` (2), `test_audit_docs_process_core_digest.py` (2), `test_audit_docs_w37_11_ceiling.py` (1), `test_doc_index.py` (1), `test_register_lint.py` (3), `test_register_owed.py` (1), `test_repository_invariants.py` (2). Small re-checks at `7757a2f8` via `run-small.sh`: change-summary route file 12 passed, `ruff check .` 0, `mypy` 0, `generate-contracts.py --check` 0. Closing acts here: `SL-1678` closed, this ledger closed, `FD-1679`'s guard limb discharged (DP-P1 keeps it open), `PL-1677` stays `active` (DP-P1 open).

**Gated head versus merge head:** the gate table names `d01cf107`, the gated head. The slice's own code (`rating_versions.py`, the route test file, the `03` spec row) is byte-identical at the merge head (`git diff --quiet d01cf107 HEAD` over the two code files exits 0); the only `backend/` differences since are the files `origin/main` brought in with SL-1669 (`api/rate_tables.py`, `test_api_rate_tables.py`, `test_contracts.py`). CI on the PR head covers the merge (the lead, from-lead "2026-10-12 07:38:09 BST").

## Audit

Auditor `auditor-sl1678`, 2026-10-12, range `origin/main...origin/sl-1678-wk673-fd1679-guard` at PR #1296's head `56a780fc949d2a564087b861535c44197d22c92d` (the brief named `1ea26bc8`, an ancestor; `56a780fc` adds only this ledger's last paragraph). Authorities: the maintainer's (by delegation) entries "2026-10-12 05:43:54 BST", "05:44:45 BST", "05:57:57 BST", "05:58:56 BST" (`to-lead.md`); the lead's from-lead entries "2026-10-12 06:05:28 BST", "06:13:21 BST", "07:38:09 BST". I did not re-run the route test file or the gate (charter: no full suite); test evidence is read from the code and the raw logs in `scratch/sl1678/logs/`.

**Acceptance (`PL-1677` Acceptance Standard), proposed verdicts**

| # | Item | Evidence | Proposed |
|---|---|---|---|
| 1 | Reds 1–3 pass; each failed on the base by its cause and again on the planted reversal | Tests `test_a_candidate_pinning_two_versions_of_one_table_is_refused[two_then_one|one_then_two]` and `test_a_baseline_pinning_two_versions_of_one_table_is_refused` each go through `_assert_refused` (409, `code == "VALIDATION_FAILED"`, slug and `FD-1679` in `detail`). This ledger: base `3 failed, 1 passed` with `assert 200 == 409` per red; guard disabled `3 failed, 9 passed`; green `12 passed` | MET |
| 2 | Create stays permissive | `_create_over_http` asserts 201 for the duplicate-slug candidate (Red 1, Red 2, Red 4). `git diff -U0 origin/main...HEAD -- backend/src` has three hunks (`:1337` docstring, `:1405-1414` `_pins_by_slug`); none in `create_rating_version` | MET |
| 3 | A first version is answered | Red 4 asserts 200, `baseline is None`, `rate_tables == []` | MET |
| 4 | Existing tests unchanged, diff adds lines only | One changed line: the import now `add_approved, mark_approved`. No test body changes. Lead-accepted deviation (from-lead "2026-10-12 06:13:21 BST") | MET with the accepted deviation |
| 5 | No contract drift | `git diff --stat origin/main...HEAD -- docs/contracts frontend` prints nothing; `contracts.rc` 0 in the gate logs | MET |
| 6 | Spec says it; `audit-docs.py` exits 0 with the LG minted | `03` §5.1 change-summary-draft row carries the dated clause (added 2026-10-12, SL-1678, FR-242), matching the behaviour (409 `VALIDATION_FAILED`, either side, create unchanged, RL-1538). `audit-docs.py` at `56a780fc` (gate-2, flocked): rc 1, exactly one failure, `check 31: gap in the full allocation between 1679 and 1681` (1680 is LG-1680 on #1295) | clause MET; exit 0 NOT YET: closes when #1295 merges and this branch re-merges `main` |
| 7 | Gate green on the merge tree | Gate ran at `d01cf107` on base `f7ca32ec`, not the merge tree: `ruff`, `mypy`, import-linter, req-coverage, contracts, frontend ×5 rc 0; `pytest` rc 1 (`13 failed, 5734 passed, 6 skipped`); `audit-docs` rc 1. Logs: `audit_docs.log` lists only check 31 gaps `1673→1677` and `1679→9899`; `pytest.log` shows the same two lines as the cause in the audit-on-tree tests (13 FAILED lines in 8 files, matching the count above). The slice's code is byte-identical at the merge head (this ledger's closing acts) | PARTIAL: accepted by the lead as check-31-only; the merge tree is covered by CI, which is not yet complete |

**Reds by cause.** Red 1 (candidate `[X@two, X@one]`, edit silently dropped), Red 2 (candidate `[X@one, X@two]`), Red 3 (baseline side) each assert 409 `VALIDATION_FAILED` naming the slug and `FD-1679`. Red 2's FALSE entry is quoted verbatim above (`version 1 -> 2` for a candidate that still pins both). Red 4 is labelled a guard in the code comment and in this ledger. `grep -n 9895` over the code and the test file: no hit (code cites the minted id only; the maintainer's (by delegation) entry "2026-10-12 05:58:56 BST").

**Write set.** `git diff --stat origin/main...HEAD`: `rating_versions.py`, the route test file, `03-rating-engine.md`, `docs/roadmap.md`, `PL-1677` (status only), `FD-1679` (dated line), this ledger, `docs/INDEX.md`. `models.py` and `docs/contracts` untouched, as planned. Nothing outside PL-1677's write set except the closing-act files it names.

**Findings (all for the lead's verdict)**

1. LOW, evidence gap: `PL-1677` Task 0 requires premises a–i re-read at the slice base and each recorded with its locator. This ledger records premise c only and says the rest are "to be re-read and recorded here before Task 2"; they never are. The code diff shows premises c and d unchanged in effect; a, b, e–i are unrecorded. Verdict options: delivered but untested (record the re-read in this ledger) or accept.
2. LOW, stale text: the SL-1678 roadmap row still reads "Work-plan delta `PL-1677` (`draft`)" mid-row; `PL-1677` is `active`.
3. LOW, completeness: the `## PRs` section does not name the PR number (#1296).
4. INFO, gate scope: Acceptance 7 and 6 close only after #1295 merges, this branch re-merges `main`, and CI on the new head is green. At the audit CI on `56a780fc`: `history-policy` completed success; `python` and `docs` in progress; the runs on `1ea26bc8` were cancelled (superseded). CI is not green yet.
5. INFO, behaviour: the 409 `detail` names the slug and the two versions but not which side (candidate or baseline) carries the duplicate. Within PL-1677's text; no action proposed.

**Closing acts.** `SL-1678` `closed` with a dated line (roadmap) and this ledger `closed`: present; the roadmap line's "Audit: pending" is filled by the commit that adds this section. `FD-1679` dated line: guard limb discharged, DP-P1 keeps it open, owner WK-673: present and accurate. `PL-1677` `active`: correct while DP-P1 is open. `MERGE-ACK` is the lead's and the maintainer's.

**Proposed verdict (the lead decides):** the guard delivers every behavioural acceptance item (1–5, 6's clause); items 6 (exit 0) and 7 (merge-tree gate) are open on #1295 and CI, not on the code. No finding blocks the merge on the code. Findings 1–3 are fixable in the re-merge commit.
