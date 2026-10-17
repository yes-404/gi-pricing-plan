---
id: LG-1743
family: ledger
title: WK-1178 slice SL-1742 — FD-1741, the python CI job runs its cheap checks before pytest and has a 50-minute budget, slice ledger
status: closed                 # active → closed (§1.2a) — set `closed` at slice close, 2026-10-17, on the closing audit below
created: 2026-10-17 # original date 2026-10-16, set at the draft; minted 2026-10-17
owner: executor
phase: P2
work: WK-1178
slice: SL-1742
plans: []
corrected_by: []
relates: [SL-1742, FD-1741]
---

# LG-1743 — WK-1178 slice SL-1742: the python CI job budget

*(Minted 2026-10-17 as LG-1743 from working id 8065, with SL-1742 (working id 8064) and FD-1741 (working id 8063), in the SL-1742 PR.)*

**GO:** the maintainer's ruling "2026-10-16 09:57:34 BST — RULING — the python CI job budget (#1309's cancelled run): finding MEDIUM, owner WK-1178, fix now" in `to-lead.md`. The finding is FD-1741.
**CI is the gate:** the ruling's proof is the slice's own python CI run, success, with the contracts and req_coverage stages logged before pytest. No local full gate.
**MERGE-ACK:** not yet given.
**Audit:** the pre-PR audit is written below ("Pre-PR audit", by `auditor-8064r`); the closing audit is written below ("Closing audit", by `auditor-8064`, 2026-10-17): CLEAN, proposed to the lead.

## Tasks

Branch `sl-8064-ci-job-budget-2026-10-16`, worktree `.claude/worktrees/sl-8064`, cut from `origin/main` `0877e6e7`.

- **Order:** `Generated contracts are current` and `Requirement coverage` move to before `Tests` in `.github/workflows/python.yml`. Neither reads a step between (no DB, no output of `Migrate`/`Tests`).
- **Budget:** `timeout-minutes` 30 → 50.
- **Gate summary:** unchanged; it reads `steps.<id>.outcome` for all eight stages, so it is order-independent and keeps `if: always()`.

## PRs

Not opened yet. FD-1741 (the finding this slice discharges, filed by the auditor on `fd-8063-ci-job-budget-2026-10-16`) is merged into this branch with a no-ff merge; the lead opens the PR.

## CI run

PR #1318, head `f290783c`, `python` run **39024391811**: conclusion `success`, job `ruff · mypy · import-linter · pytest` 2026-10-17T10:18:25Z to 10:47:30Z (29 min 5 s, inside the 50-minute cap). Log order (`gh run view 39024391811 --log`): `Generated contracts are current` 10:19:27Z, `Requirement coverage` 10:19:37Z, `Tests` 10:19:37Z; Tests last line `5878 passed, 6 skipped, 116 warnings in 1656.96s (0:27:36)`; Gate summary `GATE: pass — 8 of 8 stages passed`, all eight rows `pass | success`.

## Pre-PR audit

Written 2026-10-16 10:14:45 BST by `auditor-8064r` (seat of the auditor role) on the range `origin/main...origin/sl-8064-ci-job-budget-2026-10-16`, branch head `081ccd26` before this audit's own commit, merge base `0877e6e7` (= `origin/main`). Read against the maintainer's ruling "2026-10-16 09:57:34 BST" in `to-lead.md`. This audit is a proposal to the lead (§12); the lead's merge is the verdict.

| # | Item | Verdict | Locator |
|---|---|---|---|
| 1 | Contracts `--check` and req-coverage run before Tests, needing no DB | PASS | `.github/workflows/python.yml` at the branch head: `Generated contracts are current` (`:301-304`) and `Requirement coverage` (`:308-311`) now precede `Tests` (`:313-322`); the diff moves the `Tests` step verbatim (same text removed above, added below). Neither moved step has an `if:` or a `DB` env; both keep `continue-on-error: true`, so a failure does not skip Tests. Tests keeps `if: steps.minio.outcome == 'success'`. |
| 2 | `timeout-minutes` 30 → 50 | PASS | `python.yml:94` (`timeout-minutes: 50`); the one hunk in the job header. No other `timeout-minutes` line changed (`git diff origin/main...HEAD -- .github/workflows/python.yml` has three hunks: the timeout, the removal of Tests, the insertion of Tests). |
| 3 | Gate summary reports every stage; `if: always()` kept | PASS | The `Gate summary` step has no hunk in the diff. Body read: `if: always()`; eight `S_*` env lines from `steps.<id>.outcome` (ruff, mypy, importlinter, minio, migrate, pytest, contracts, reqcoverage); `stages="ruff mypy import_linter minio migrate pytest contracts req_coverage"`; the loop writes a row per stage and the step ends `[ "$nfail" -eq 0 ]`. It reads step ids, so it is order-independent. All eight step ids still exist. |
| 4 | Working-id form (lead correction 10:13) | FIXED | `scripts/_docid.py:67`: `ID_RE = re.compile(r"\b(FR\|NFR\|DEP\|OQ\|WK\|SL\|WF\|ADR\|RFC\|PL\|LG\|RL\|RS\|CR\|FD)-0*(\d+)\b")` — the tool's id grammar has a hyphen and no space alternative, so `FD-1741` is not an id the tooling sees in `id:` or `relates:`. Precedents read on the draft branches: `id: FD 8040` (`origin/docs-d18-2026-10-14`), `id: LG 8059` with `slice: SL-1722` and `relates: [..., SL-1722, FD-1730, ...]` (`origin/sl-1722-wk1178-fd1730-upload-404`), `id: PL 8030 (now PL-1733)` (`origin/docs-p1-plans-2026-10-14`), `id: SL-1719` and `#### SL-1719` (roadmap on sl-1722). Changed to hyphen: FD-1741 (`id:`, `relates:`, heading), LG-1743 (`id:`, `slice:`, `relates:`, `title:`, heading), SL-1742 (heading, `id:`, `relates:` in `docs/roadmap.md`). Prose keeps space form. File names keep the padded form (`FD-1741-…`, `LG-1743-…`), as on the precedent branches. |
| 5 | Register row | PASS | `docs/findings/register.md` last row: 5 cells under an unescaped-pipe split, same as the two rows above it; the two literal pipes in the quoted Gate summary are written `\|`. Severity MEDIUM, owner WK-1178, P2, P3 option (xdist, sharding; owner WK-1178; held back by shared-database flake risk) as ruled. Citations checked at `0877e6e7`: `timeout-minutes: 30` `:94`; Tests `:298-302`; contracts `:312-315`; req-coverage `:319-322` — all four match. The FD essay's own MEDIUM / owner / P3 lines (`:17-24`, `:79`, `:100`) agree with the ruling. |
| 6 | Scope | PASS | Five files: `python.yml`, the FD, the register row, this ledger, the roadmap SL block. No `backend/`, `docs/specs/`, `docs/contracts/` change. |

**Observation, not a failure.** The slice and ledger front matter carry no `tree:` line, which the precedent slice and ledger blocks do. Whether `audit-docs.py` requires it is not known until the check runs; the closing acts decide.

### Owed after GATE END (item 10: no `/tmp/slots` flock during the ALONE gate)

None of these has been run: this audit is by reading, `git` and `sed`. Each is **NOT RUN**, not green.
1. `flock -w 900 /tmp/slots/gate-2 env -C <wt> python3 scripts/doc-index.py` (regenerate `docs/INDEX.md`; the new records are not in it yet), then commit.
2. `… scripts/audit-docs.py`.
3. `… scripts/doc-index.py --check`.
4. `… scripts/register-lint.py`.

**Proof, owed at the PR:** the PR's own `python` CI run is success, with `contracts` and `req_coverage` logged before pytest and all eight stages in the Gate summary table. Cite the run id in the "CI run" section above. Until then, the workflow change is unproven in CI.

### Re-merge, 2026-10-16 10:40 BST (Europe/London)

`origin/main` a2f77b2dcad5aaec41a5f10aa664383caf421e8b merged `--no-ff` into this branch (was 806f97a9). `git merge-tree --write-tree` rc 0 before the merge: no conflicts, no hand resolution; `docs/INDEX.md`, the roadmap and the register took the merge result unedited. The INDEX regeneration stays owed (item 1 above).

### Mint and re-merge, 2026-10-17 (Europe/London), by `executor-8064b`

`origin/main` 055b5e6b merged `--no-ff` (conflicts in `docs/roadmap.md`, resolved by keeping both SL blocks, and in `docs/INDEX.md`, taken from main and regenerated). FD-1741, SL-1742 and LG-1743 minted from working ids 8063, 8064 and 8065; the unminted ids cited in the audit row 4 (FD 8040, LG 8059) are in space form, and PL 8030 is PL-1733 (#1317). The PR is opened by this seat as a ready PR on the brief's explicit exception; the lead merges.

## Closing audit

*(Written by `auditor-8064`, 2026-10-17 11:5x BST (Europe/London), on head `f290783c64e9aa0cfcb3d0c432f6d5da9a7b8e93`, range `origin/main...origin/sl-8064-ci-job-budget-2026-10-16`. Read-only on code; no pytest, no database run by the auditor. A proposal to the lead (§12); the lead's merge is the verdict.)*

Scope from FD-1741's Disposition (three obligations) and SL-1742's block, then evidence.

| # | Obligation | Verdict | Evidence |
|---|---|---|---|
| 1 | Contracts `--check` and req-coverage run before Tests (no DB) | MET | `git diff origin/main...HEAD -- .github/workflows/python.yml`: the `Tests` step is removed above and re-inserted verbatim below them; at the head the step ids are in the order `migrate` (`:291`), `contracts` (`:302`), `reqcoverage` (`:309`), `pytest` (`:314`). CI log: contracts 10:19:27Z, req-coverage 10:19:37Z, Tests 10:19:37Z. |
| 2 | `timeout-minutes` 30 → 50 | MET | one hunk, `python.yml:94`; no other timeout line changed. Run took 29 min 5 s of 50. |
| 3 | Gate summary unchanged, reports every stage, `if: always()` kept | MET | no hunk in the Gate summary step (`:336-346`); eight `S_*` env lines still read `steps.<id>.outcome` for all eight ids, which all exist. Run 39024391811 prints all eight rows `pass \| success` and `GATE: pass — 8 of 8 stages passed`. |
| 4 | Nothing else changed in CI semantics; SHA-pinned actions kept (FD-1194) | MET | the diff contains no `uses:` line (0 matches); the two `uses:` lines in the file stay 40-hex SHA pins (`checkout@3d3c42e5…`, `setup-uv@c18668ad…`). No other `.github` path in the range; no `backend/`, `packages/` or `docs/specs/` path in the range. |
| 5 | The proof: the slice's own python run is success with the cheap checks before pytest | MET | run 39024391811, see "CI run". Positive case only; the cancel-at-cap case is not re-provoked (it would need a 50-minute suite). The finding's evidence of the old failure is run 38873614111 attempt 1. |
| 6 | The mint: old-id sweep and INDEX rows | MET | the old-id sweep (predicate under the table) prints nothing (0 hits, whole tree). INDEX gains exactly three rows (FD-1741, SL-1742, LG-1743) and the register one row. The `created:` lines read "2026-10-17 # original date 2026-10-16, set at the draft; minted 2026-10-17" on all three: the disclosure is present. |

Sweep predicate, verbatim: `git grep -n -I -E '(FD§SL§LG)[ -]0*(8063§8064§8065)\b' origin/sl-8064-ci-job-budget-2026-10-16`, with `§` read as the alternation bar (spelled out because an unescaped bar splits a table row, audit-docs check 22).

**Findings.** None at HIGH or MEDIUM.
- **A1, INFO.** The commit subject of `f290783c` carries the working ids in parentheses ("FD 8063, SL 8064, LG 8065"); a commit message is frozen and the sweep above covers the tree only. Accepted.
- **A2, INFO.** The roadmap SL-1742 block is still `status: active`; this audit sets the ledger `closed` only, as the brief names. Closing the roadmap block (the LG-1732 precedent does both) is the lead's act at the merge.
- **A3, INFO.** FD-1741's register row stays open until the merge: its discharging event is "the merge of SL-1742 with its own python run green and the contracts and requirement-coverage steps logged before pytest". The run half of that is met here; the auditor sets the row `closed` in place citing the PR and merge commit after the lead merges.
- **A4, INFO.** The margin note: pytest alone took 1656.96 s on this run (1734.13 s on the failing one), so the 50-minute cap leaves about 20 minutes of headroom; FD-1741's P3 option (xdist or sharding, owner WK-1178) remains the cause-side remedy and is not touched.

**Checks run at this tree** (`flock -w 900 /tmp/slots/gate-2`, `env -C` the worktree, 2026-10-17): `doc-index.py` rc 0 (INDEX regenerated, no row change expected); `audit-docs.py` rc 0 and `register-lint.py` rc 0 at the committed tree (the commit's report to the lead carries the final lines).

**Proposed verdict: CLEAN. SL-1742 satisfies FD-1741's remedy on the evidence above; the workflow change is the proven change.** Lead's adoption line to follow.

**Lead adoption (2026-10-17 11:50:16 BST, the lead, transcript 99374ddb):** the auditor's proposed verdict CLEAN is ADOPTED as written (obligations 1–6 met; INFO A1–A4 accepted; A2 discharged in this commit: SL-1742 `status: closed` in docs/roadmap.md; A3 — FD-1741's register row is closed after the merge, citing the PR and the merge commit). Proof read by the lead from the job log of python run 39024391811: req-coverage 10:19:37Z before pytest; "5878 passed, 6 skipped, 116 warnings in 1656.96s (0:27:36)"; "GATE: pass — 8 of 8 stages passed".
