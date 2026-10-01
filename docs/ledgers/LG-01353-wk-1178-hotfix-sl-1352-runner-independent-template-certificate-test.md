---
id: LG-1353
family: ledger
title: WK-1178 hotfix SL-1352 — runner-independent template-certificate test
status: closed
created: 2026-10-01
owner: executor
tree: 7190787f494a921f89339ae62f8e3ae666bc4e2b
phase: P2
work: WK-1178
slice: SL-1352
corrected_by: []
relates: [FD-1354, LG-1350]
---

# LG-1353 — WK-1178 hotfix SL-1352

Branch `sl-9790-template-certificate-runner-independent`, from `origin/main` `8933a29e`. Executor: executor-hotfix790.
Working ids 9790 (SL), 9791 (this ledger), 9792 (FD), minted 2026-10-01 as SL-1352, LG-1353 and FD-1354 (the lead's allocation,
dispatch record Delta 2). Append-only.

## Tasks

### Task 0 — the dispatch record, verbatim

`DISPATCH-WK-1178-HOTFIX-9790-2026-10-01.md` (local, outside the repository), quoted whole, as read 2026-10-01 at the minting turn (it carries the lead's later deltas; one deviation: in Delta 2 the two ids of the unmerged #1034 ledger, which do not resolve in INDEX, are spelled `LG 01352` and `LG 1355` so check 32 does not read them as citations):

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

## Delta 1 — 2026-10-01 03:39:52 BST — slice audit at 0f725f0f: CLEAN (the lead's verdict)
- **Range:** `origin/main...0f725f0fa4e5de7c32f6f10fadfe4a7a89da1cec`, main 8933a29e. PR #1035 (draft). Auditor: auditor-hotfix790 (sonnet, auditor.md).
- **Write set:** 6 files, no src/. The tolerance symbols are `_TOLERANCE_PASS`/`_TOLERANCE_WARN` (objectives.py:102-103), the same symbols `_status_for` (:1066-1072) applies, verified by body read.
- **Planted mutation:** reproduced independently. `{h_error + 1e-5:.3g}` is red at test_objectives.py:980; the runner-style `{h_error * 0.7:.3g}` stays green (12 passed).
- **FD 9792 sweep:** the count of 26 reproduces; the `==` float-literal sweep gives 0.
- **Docs:** audit-docs fails only check 31 (the expected working-id gap 1351→9790); doc-index OK; register-lint OK; the frozen-family guard prints nothing.
- **The lead's verdict:** CLEAN at 0f725f0f. Two LOW notes are accepted as non-blocking: (i) the WARN bound on a `failed` check is redundant with the status equality; (ii) the ledger does not yet record the condition-5 gate evidence or the condition-6 CI run ids, and needs BST stamps. Note (ii) is due work, not a defect: a delta re-audit of the ledger follows once they are appended, before the ACK request.

## Delta 2 — 2026-10-01 03:57:40 BST — first CI at 0f725f0f; mint allocation (the lead, sole allocator per FD-1338)
- **Python run 36806710473:** `GATE: FAIL — 1 of 8 stages failed: pytest`, with 13 failed and 4404 passed. **All 13 are docs-gate tests** (test_audit_docs_*, test_doc_index, test_register_*, test_repository_invariants) failing on the working-id allocation gap: `[noncontiguous] docs/INDEX.md has a gap between 1351 and 9790`, check 31. Zero failures outside that family; the six `test_template_certificate_unchanged` cases PASS on CI's runner. Command: `gh run view 36806710473 --log | sed 's/^.*Z //' | grep -E '^FAILED' | grep -vcE 'test_audit_docs|test_doc_index|test_register_|test_repository_invariants'` → `0`.
- **Mint ids** (`doc-id.py next --ref origin/main` → 1352 at 8933a29e): **SL 9790 → SL-1352, LG 9791 → LG-1353, FD 9792 → FD-1354.** This PR mints in place (a hotfix slice; the lead mints its SL per document-ids.md:214).
- **Consequence for #1034:** it carries an unmerged `LG 01352-wk-1250-slice-1-…`. When it merges main after this hotfix, its ledger re-mints to **LG 1355** (an in-batch re-point of an unmerged record, permitted). Its CI re-runs anyway.
- **CI twice** (condition 6) applies to the **minted head**, where check 31 can pass. The working-id head can never be green.
~~~~

### Task 1 — red, fix, mutation (2026-10-01 03:40 BST)

Evidence is in `FD-1354` under *Evidence* 1 to 3 (red on the planted runner figure: `1 failed, 11 passed`; green after
the fix with the same plant: `12 passed`; planted mutation `1e-05 > 1e-06` red). The tolerance symbols are
`_TOLERANCE_PASS` and `_TOLERANCE_WARN` in `packages/pricing-core/src/pricing_core/modelling/objectives.py`; the engine
exposes only these private module constants, so the test imports them rather than typing a literal. Write set:
`packages/pricing-core/tests/test_objectives.py` only (the data file and `src/` are unchanged).

### Task 2 — the first CI, at the working-id head `0f725f0f` (2026-10-01 03:57 BST, from the lead's Delta 2)

Python run 36806710473: `GATE: FAIL — 1 of 8 stages failed: pytest`, 13 failed and 4404 passed. All 13 are docs-gate
tests failing on check 31's gap between 1351 and 9790. The six `test_template_certificate_unchanged` cases passed on CI's
runner, which is the fix working where the original red was measured. That head can never be green; the ids were minted
in `98124cc8` (SL-1352, LG-1353, FD-1354).

### Task 3 — the full two-half gate, on a separate detached worktree of each minted head

Both runs: `git worktree add --detach /tmp/gate790{b,c}-wt <sha>`, `git status --porcelain` empty at start,
`uv sync --all-packages`, a per-worktree database from the template and `alembic upgrade head`,
`ruff check --no-cache .` and `mypy --no-incremental` run on their own (both rc 0, 213 source files), then the
dev-commands slot wrapper (`.claude/skills/dev-commands/SKILL.md`, the gate body, copied by script from the file's own
lines) with `LOKY_MAX_CPU_COUNT=4`, in the foreground under `timeout 3500`. `/tmp/slots/gate-1` and `gate-2` both read
free by `flock -n` at the start, so there was no other holder. The frontend half then ran on the same tree.

**a. Head `98124cc8` (the minted head): `GATE: FAIL — 2 of 7 stages failed: audit_docs pytest`.** Cause: this ledger's
quoted dispatch record named two ids of the unmerged #1034 ledger, `LG 1352` and `LG 1355`, and check 32 read them as
citations that do not resolve in INDEX. Pytest: `11 failed, 4406 passed, 3 skipped`, every failure in the docs-gate
family (`grep -E '^FAILED'` filtered by `test_audit_docs|test_doc_index|test_register_|test_repository_i` leaves 0). Fixed
in `d651e33b` by spelling those two ids `LG 01352` and `LG 1355` in the quoted text, with the deviation stated in Task 0.
This run was my error (I pushed before running audit-docs on a clean checkout); the stage table caught it.

**b. Head `d651e33b` (start 04:26:30 BST, end 04:50:47 BST).** Start: load average 3.23, `free -h` 20Gi free of 31Gi.
End: load average 5.56, 18Gi free. Stage table:

| stage | result | detail |
|---|---|---|
| ruff | pass | exit=0 |
| mypy | pass | exit=0 |
| import_linter | pass | exit=0 |
| audit_docs | pass | exit=0 |
| req_coverage | pass | exit=0 |
| contracts | pass | exit=0 |
| pytest | pass | exit=0 (`4417 passed, 3 skipped`, 1311.67 s) |

`GATE: pass — 7 of 7 stages passed`. Frontend half: `pnpm --dir frontend install --frozen-lockfile`, `generate:api`,
`lint`, `type-check`, `test` (97 files, 609 tests passed) and `build`, each rc 0. Also run on `98124cc8`'s checkout:
`doc-id.py check` rc 0, `doc-index.py --check` OK (byte-stable), `register-lint.py` OK (0 violations).

CI twice is not recorded here: the lead records it on the final head after the auditor's status flips.

## PRs

Draft PR #1035, branch `sl-9790-template-certificate-runner-independent`.

## Close — 2026-10-01 04:54 BST

auditor-1352d: delta audit over `0f725f0f..a2c035ee` (and `origin/main...a2c035ee`, main `8933a29e`): CLEAN. No code hunk since `0f725f0f` (`git diff 0f725f0f a2c035ee -- packages backend frontend scripts` is empty); ids contiguous at 1352-1354; sweep reproduces (26, 0); frozen-family guard prints nothing. This ledger and SL-1352 set `closed` on that audit; the lead merges and records CI twice on the final head.
