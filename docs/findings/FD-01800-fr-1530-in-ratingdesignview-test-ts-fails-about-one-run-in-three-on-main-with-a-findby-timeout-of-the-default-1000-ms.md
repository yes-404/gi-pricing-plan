---
id: FD-1800
family: finding
title: FR-1530 in RatingDesignView.test.ts fails about one run in three on main, with a findBy timeout of the default 1000 ms
status: active
created: 2026-10-18   # filed 2026-10-17 under working id 8103; minted 2026-10-18 as FD-1800
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, SL-1740, SL-1547]
---

# FD-1800 — FR-1530 in RatingDesignView.test.ts fails about one run in three on main, with a findBy timeout of the default 1000 ms

## Finding

**MEDIUM; owner WK-1178; verdict deferred with an owner.** The maintainer's entry "2026-10-17
21:24:40 BST" (`to-lead.md`, item 3): the failure is a **flake in main's frontend**. It is counted
against neither SL-1740 nor SL-1547 (SL-1740 changes no frontend file). MEDIUM and not LOW,
because at about one run in three it will red a PR's frontend CI at random, which costs merges
and invites "re-run until green".

## Evidence

- **The failing test.** `frontend/src/views/__tests__/RatingDesignView.test.ts:65-73` at
  `origin/main` 9469721d, read by the author. It renders the view, then loops over `valid.steps`
  and, for each step, awaits `screen.findByLabelText(`${step.type} step ${step.label}
  (${step.step_id})`)` (`:68-70`) with no timeout option, then asserts
  `getRatingAlgorithm` was called with `("motor-gb", 1)`. The query is a `findBy`, so it already
  waits; the wait is the library default.
- **The failure, both proof gates.** `gi-pricing-plan.local/scratch/sl1740-gate/fe-test.log:8-13` and
  `sl1547-gate/fe-test.log:8-13`: `× FR-1530: loads the algorithm the version pins, and draws one
  node per step 1087ms` (SL-1740) and `1123ms` (SL-1547); `TestingLibraryElementError: Unable to
  find a label with the text of: input step Driver age (s_in_age)`. Totals: 1 failed | 729 passed
  (SL-1740), 1 failed | 776 passed (SL-1547); the other 115 and 122 test files passed.
- **The label is the first step.** `s_in_age` is `valid.steps[0]`
  (`frontend/src/components/dag/__tests__/fixtures.ts:39`). The loop failed on its first query, so
  no node had drawn when the wait ended.
- **Solo runs** (executor-1740f, the lead's entry of 2026-10-17 21:24:16 in `from-lead-2026-10-09.md`,
  as relayed; not re-run here): sl-1547 7 of 7 passed; sl-8045-prep run 1 failed, runs 2 and 3
  passed. One failure in three solo runs is the "about one in three" above. It is a sample of
  three, not a rate.
- **No configured wait.** `grep -n "asyncUtilTimeout\|testTimeout" frontend/vitest.config.* frontend/vite.config.*`
  at docs-d21 @358c194e returned nothing, so the Testing Library default (1000 ms) applies.

## Hypothesis (not verified)

The failed tests ran **1087 ms and 1123 ms**, just past the 1000 ms default `findBy` timeout.
The first query waits for Vue Flow to draw the first node after the async `getRatingVersionByRef`
and `getRatingAlgorithm` mocks resolve; the suite stubs `ResizeObserver` with a no-op class
(`:23-29`), so Vue Flow's own measurement step is not the real one. Under CPU load the
render-then-measure sequence can take over one second, and `findBy` gives up. The other
`findBy` calls in this file wait for one label and pass; this test waits for the first of seven
nodes. **Untested:** the proof that the cause is the 1000 ms default (rather than a missing
re-render trigger) is a run with a longer timeout under load, which this finding did not make
(no test run, per the brief).

## Standing rule until fixed

The maintainer's entry "2026-10-17 21:24:40 BST", verbatim: *"a PR CI frontend red ONLY on FR-1530
may be re-run ONCE, the re-run recorded in the PR (its run ids); a second failure = STOP."* Both
run ids go in the PR. A red on any other test, or on FR-1530 plus another test, is not covered.

## Options (none picked)

- **(a) A longer, explicit wait on this one query:** `findByLabelText(label, {}, { timeout })`.
  Smallest change; still a timer, so it moves the threshold rather than removing it.
- **(b) A deterministic wait:** await the mocks and a rendered-state signal first
  (`await vi.waitFor(() => expect(getRatingAlgorithm).toHaveBeenCalled())`, or `await flushPromises()`
  plus `nextTick`), then query with `getBy`. No timer in the assertion.
- **(c) A suite-wide `asyncUtilTimeout`** in the Vitest setup. Wider; changes every `findBy` in
  the frontend, so it hides slow tests rather than naming them.
- **(d) Cap the vitest workers** (the maintainer's 21:11 BST housekeeping, see
  `.claude/skills/dev-commands`): lowers load, which lowers the rate. It does not remove the race,
  so it is not a fix.

## Disposition

Deferred with an owner: WK-1178. Decision on the option is the lead's or an RL's; this record
picks none. The event that next discharges it: a merged change to the test (or its setup) plus a
repeated run under load that does not fail (more than the three solo runs above), or a dated
ruling accepting the absence. Filed under working id 8103.
