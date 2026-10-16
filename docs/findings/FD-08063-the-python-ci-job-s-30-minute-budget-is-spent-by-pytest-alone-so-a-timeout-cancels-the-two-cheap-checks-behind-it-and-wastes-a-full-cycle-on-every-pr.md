---
id: FD 8063
family: finding
title: The python CI job's 30-minute budget is spent by pytest alone, so a timeout cancels the two cheap checks queued behind it and wastes a full cycle on every pull request at risk
status: active
created: 2026-10-16
owner: auditor
tree: 0877e6e7a756c4621890713a4d3b016e75e33654
corrected_by: []
relates: [WK-1178, SL 8064, P2]
---

# FD 8063 — `python.yml` runs `pytest -q` first, inside a 30-minute job cap that pytest alone now fills

*(Filed under working id 8063, reserved by the lead; a minter folds it into the docs batch.
Authority: the maintainer's (by delegation) entry "2026-10-16 09:57:34 BST" in
`channel/to-lead.md`, which fixes the severity (MEDIUM), the owner (WK-1178), the fix (one small
slice, SL 8064) and the P3 option recorded below. Reads were made at `origin/main`
`0877e6e7a756c4621890713a4d3b016e75e33654`; the log lines are read from the run, not copied.)*

## Finding

**Severity: MEDIUM, as ruled by the maintainer (by delegation): a throughput loss that recurs on
every pull request, not a false green. Owner WK-1178, fixed by SL 8064.**

The `python` job of `.github/workflows/python.yml` carries `timeout-minutes: 30` at job level
(`:94`). Inside it, the Tests step (`uv run pytest -q`, `:298-302`) runs **before** the step
"Generated contracts are current" (`uv run python scripts/generate-contracts.py --check`,
`:312-315`) and the step "Requirement coverage" (`uv run python scripts/req-coverage.py`,
`:319-322`). Neither of those two needs the database. The suite now takes 26 to 29 minutes
of a 30-minute job. When it does not finish inside the cap, the runner cancels the whole job:
the step in flight is killed, every later step except `if: always()` ones is **skipped**, and the
two cheap checks never run. A contract drift or a requirement-coverage regression then shows as
"skipped" behind a cancelled test step, and costs one 30-minute cycle to find out.

The consequence is a wasted cycle, **not a false green**. A cancelled run ends `cancelled`, the
Gate summary step (`if: always()`, `:336-337`) prints `FAIL` for every stage that did not
succeed, and the maintainer's ruling states the run ends `cancelled`, so it cannot be read as a pass.

## Evidence

### 1. The incident: PR #1309 @`5098ebd1`, run 38873614111, attempt 1

Read with `gh run view 38873614111 --repo yes-404/gi-pricing-plan --attempt 1 --log`, filtered
by `grep -n -E 'passed|operation was canceled|Gate summary.*\|'`. The run's current attempt is
2 (the re-run, still in progress when read); the lines below are attempt 1's.

| Log line | UTC time |
|---|---|
| Set up job | 2026-10-16T08:25:45 |
| Tests step starts | 2026-10-16T08:26:46 |
| `5869 passed, 6 skipped, 116 warnings in 1734.13s (0:28:54)` | 2026-10-16T08:55:52 |
| `##[error]The operation was canceled.` | 2026-10-16T08:55:58 |
| Gate summary: `pytest \| FAIL \| cancelled`, `contracts \| FAIL \| skipped`, `req_coverage \| FAIL \| skipped` | 2026-10-16T08:55:58 |

The suite **passed** (5869 passed, 0 failed). pytest printed its summary 30 minutes 7 seconds
after the job started, and the runner cancelled the job 6 seconds later, while the step was
still shutting down. The job's own set-up and the lint, MinIO and migrate stages before Tests
take about 1 minute together (08:25:45 to 08:26:46), and they are inside the same cap, which is
why 1734 s of pytest is enough to exceed 30 minutes.

### 2. The trend: the margin has been going

Earlier durations of the same step, from `channel/from-lead-2026-10-09.md` (14 Oct runs
38607168256, 38626659293, 38621840266): **1566.18 s, 1592.00 s, 1671.39 s**. The run read above
is **1734.13 s**, 68 s above the largest of those and 168 s above the smallest. A suite that
grows by tests, and a shared runner whose speed varies by minutes, put the next failure inside the
noise: the cap was never a margin, only a number nobody had measured against.

### 3. The order is the defect

`git grep -n -E 'timeout-minutes|id: (pytest|contracts|reqcoverage)' 0877e6e7 --
.github/workflows/python.yml` shows `timeout-minutes: 30` at job level, and the three ids in the
order `pytest`, `contracts`, `reqcoverage`. The two cheap steps have `continue-on-error: true`
and no `if:` on the DB (`:312-322`), so nothing but position makes them wait for pytest.

## Severity: the reasoning

MEDIUM, as ruled. It is not HIGH because no wrong result ships: the run ends `cancelled`, never
`success`, and the Gate summary names the three stages that did not pass. It is not LOW because
it recurs on every pull request near the cap, each occurrence costs a full ~30-minute cycle plus a
re-run, and the two checks it skips are the two that cost about a minute.

## Disposition

**Fix with an owner: WK-1178, as one small slice, SL 8064** (one PR, one SL, lean P2), next after
#1310 in the merge order, by the maintainer's (by delegation) "2026-10-16 09:57:34 BST" entry:

1. **Move** the contracts `--check` and requirement-coverage steps to **before** Tests (they need
   no database). A timeout can then never skip them, and a contract drift fails in about one
   minute instead of thirty.
2. **Raise** the job's `timeout-minutes` from 30 to 50: headroom over the measured ~29 minutes,
   and a hung job is still bounded.
3. The **Gate summary** step still reports every stage, and its `if:` conditions still run after a
   failure. The slice's ledger cites a CI run with all stages present.

**The event that next discharges this finding:** the merge of SL 8064 with its own `python` CI run
green and the contracts and requirement-coverage steps logged **before** pytest.

**P3 option, recorded and not taken now (owner WK-1178):** split or parallelise pytest (xdist, or
sharding across jobs). It attacks the cause (a 29-minute serial suite) rather than the exposure.
It is **not** done now because the suite shares one database, and parallel workers risk
shared-database flakiness at the 4 Nov code freeze. If the suite keeps growing, this is the
option that stops the budget being re-raised.

**Not in this finding.** The suite's speed itself, and any test-selection policy, are not
changed by SL 8064.
