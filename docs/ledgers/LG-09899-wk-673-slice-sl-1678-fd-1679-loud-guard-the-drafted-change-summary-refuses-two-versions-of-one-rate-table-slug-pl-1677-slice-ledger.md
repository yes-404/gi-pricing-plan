---
id: LG-9899
family: ledger
title: WK-673 slice SL-1678 — FD-1679 loud guard, the drafted change summary refuses two versions of one rate-table slug (PL-1677), slice ledger
status: active                 # active → closed (§1.2a)
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

# LG-9899 — WK-673 slice SL-1678: the FD-1679 loud guard

*(Working id 9899, reserved by the lead. The id is minted at the merge turn; until then every citation of this record is by working id.)*

**GO:** the lead's from-lead entry "2026-10-12 06:05:28 BST — GO SL-1678 (WK-673, FD-1679 loud guard) → executor-sl1678 (sonnet)" (`channel/from-lead-2026-10-09.md`), citing the maintainer's (by delegation) entries "2026-10-12 05:57:57 BST" (ACK: DP-K rate_tables only, DP-G1 409, DP-G2 inside `_pins_by_slug`) and "2026-10-12 05:58:56 BST" (FD-1679 mints in the same PR) in `to-lead.md`.
**MERGE-ACK:** not yet given.

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

## PRs

- Not yet opened (the slice PR is opened at the first gate-ready push).
