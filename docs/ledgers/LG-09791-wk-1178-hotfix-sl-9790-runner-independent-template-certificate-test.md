---
id: LG-9791
family: ledger
title: WK-1178 hotfix SL 9790 — runner-independent template-certificate test
status: active
created: 2026-10-01
owner: executor
tree: 7190787f494a921f89339ae62f8e3ae666bc4e2b
phase: P2
work: WK-1178
slice: SL-9790
corrected_by: []
relates: [FD-9792, LG-1350]
---

# LG-9791 — WK-1178 hotfix SL 9790

Branch `sl-9790-template-certificate-runner-independent`, from `origin/main` `8933a29e`. Executor: executor-hotfix790.
Working ids 9790 (SL), 9791 (this ledger), 9792 (FD); the lead mints the final ids. Append-only.

## Tasks

### Task 0 — the dispatch record, verbatim

`DISPATCH-WK-1178-HOTFIX-9790-2026-10-01.md` (local, outside the repository), quoted whole:

~~~~markdown
# Dispatch record: WK-1178 hotfix, slice working id SL 9790 (main red since #1025). FINAL

**Status: FINAL, GO given 2026-10-01 03:32:46 BST by the lead (session gi-pricing-team).**

**The order:** w37-maintainer's cross-session RULING of 2026-10-01 (reply to the lead's entry "2026-10-01 03:28:29 BST — MAIN IS RED since #1025"), quoted:

> RULING (A); (B) is refused (no ACK onto a red main).
> - The fix (test-only, WK-1178 hotfix §1.9): normalise the error figure like elapsed seconds, AND assert the parsed figure ≤ that check's tolerance, so it's still tested. Red-first, plus a planted mutation (figure > tolerance → red). Full two-half gate on a separate detached worktree (--no-cache, porcelain, uptime and free -h, the other holder). CI at the head run TWICE (re-run python) to prove it's stable.
> - WHO: a FRESH executor (sonnet, executor.md), its own ledger. LANE B (WK-1250 S1 is built and waiting, not building).
> - FD LOW, WK-1178: pinned runner-dependent measurement, plus a SWEEP for other pinned measured floats (predicate, command, count).
> - #1034 waits, then merges main and re-runs CI; my ACK needs it green. No ACK lands on a red main.

**The slice:** a hotfix. Per `docs/process/document-ids.md:214`, the lead mints its `SL-` at triage under the phase's standing maintenance Work, **WK-1178**. There is no leaf plan: this record and the ruling above are the scope.

## The failure (evidence, read by the lead)
- Main's push CI, run 36801276738 at 8933a29e: `GATE: FAIL — 1 of 8 stages failed: pytest`, with 6 failed and 4411 passed. All six are `packages/pricing-core/tests/test_objectives.py::test_template_certificate_unchanged[tweedie|asymmetric_squared|asymmetric_poisson|huber|pseudo_huber|quantile]`.
- The diff: the `analytic_vs_numeric_hessian` detail is `max relative error 2.28e-12 …` on main's runner, against `3.21e-12 …` pinned in `_BEFORE` (`test_objectives.py:931`). The detail is produced by `objectives.py:1150` (`{h_error:.3g}`); the gradient detail at `:1141` has the same form. #1025's PR CI was green, so the pinned figure depends on the runner.
- #1034 (run 36804433191, head 68b90647) fails the same six and nothing else.

## Conditions
1. **Write set:**
   - `packages/pricing-core/tests/test_objectives.py`, only the `test_template_certificate_unchanged` comparison and `_BEFORE` if its figures must change form;
   - the FD 9792 file under `docs/findings/`, plus its row in `docs/findings/register.md`;
   - the ledger LG 9791 under `docs/ledgers/`;
   - the SL 9790 row in `docs/roadmap.md` under WK-1178, appended, `status: active`;
   - regenerated `docs/INDEX.md`.
   **Not** `objectives.py` or any `src/` file: this is test-only. If the fix appears to need a src change, STOP and report.
2. **The fix:**
   - normalise every `max relative error <x>` figure in the compared details, the same way the elapsed seconds are normalised;
   - AND parse each figure and assert it is ≤ that check's own tolerance, taken from the engine (`objectives.py`), not re-typed as a literal unless the engine exposes no symbol. Name the symbol in the ledger.
   Status and overall assertions are unchanged.
3. **Red first:** show the current test failing on a planted runner-style figure change before the fix (or cite the CI run above as the red, with the figure), then green after. **Planted mutation:** a figure above tolerance must turn the new assertion red. Paste the output and revert.
4. **FD 9792 (LOW, WK-1178):** a pinned runner-dependent measurement. Include a **SWEEP** of the test tree for other pinned measured floats, stating the predicate, the exact runnable command, the corpus/tree and the count; list each hit with a verdict. A hit is fixed here only if it lies in this test's write set; otherwise the FD records it.
5. **Gate:** the full two-half gate on a SEPARATE detached worktree of the pushed SHA (`git worktree add --detach`), with:
   - `git status --porcelain` empty;
   - `uv sync --all-packages`;
   - `ruff check --no-cache`, and `mypy --no-incremental`;
   - the dev-commands slot wrapper verbatim (`.claude/skills/dev-commands/SKILL.md:122-171`) plus `LOKY_MAX_CPU_COUNT=4`, in the foreground with a timeout;
   - `uptime` and `free -h` at start and end;
   - the other holder named via `flock -n /tmp/slots/gate-{1,2}`.
   **The wrapper exits 0 on failure: read the stage table.** Single-file pytest runs are exempt from the slot; anything wider is not.
6. **CI twice:** after pushing, the PR's CI must go green at the head, and python must then be re-run (`gh run rerun <id>`) and go green a second time. Record both run ids and GATE lines in the ledger.
7. **Ledger:** LG working id 9791. Append-only; Task 0 quotes this record verbatim. The lead is the only id allocator (FD-1338): ask for any new id.
8. **Frozen records:** nothing in `docs/plans/`, `docs/rulings/` or any frozen body is edited. The ledger LG-1350 is not edited: the FD cites it.
9. **Lanes (RL-1263):** lane B. Lane A holds SL-1345 (executor-ladder; building `rating/`, tests under `rating`), which is disjoint from this write set except `docs/roadmap.md` (append-only row; the second to merge re-gates docs) and INDEX (registry-exempt). WK-1250 S1 (#1034) is built and not building; it merges main after this.
10. **Executor:** a fresh `executor-hotfix790`, spawned from `.claude/roles/executor.md` with its Model / effort line (sonnet, medium), in a new worktree from origin/main (8933a29e). It never `cd`s.
11. **PR:** a draft, titled `fix(modelling): SL 9790 — runner-independent template-certificate test (WK-1178 hotfix)`. No merge: the lead merges on the maintainer's MERGE-ACK.

~~~~

### Task 1 — red, fix, mutation (2026-10-01 03:40 BST)

Evidence is in `FD-9792` under *Evidence* 1 to 3 (red on the planted runner figure: `1 failed, 11 passed`; green after
the fix with the same plant: `12 passed`; planted mutation `1e-05 > 1e-06` red). The tolerance symbols are
`_TOLERANCE_PASS` and `_TOLERANCE_WARN` in `packages/pricing-core/src/pricing_core/modelling/objectives.py`; the engine
exposes only these private module constants, so the test imports them rather than typing a literal. Write set:
`packages/pricing-core/tests/test_objectives.py` only (the data file and `src/` are unchanged).

## PRs

(Appended below as the PR is opened and its CI runs complete.)
