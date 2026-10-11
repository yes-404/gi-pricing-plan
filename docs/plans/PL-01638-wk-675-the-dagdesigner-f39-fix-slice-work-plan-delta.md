---
id: PL-1638
family: plan
kind: map
title: WK-675 — the DagDesigner F39 fix slice (the validate route stubbed in DagDesigner.test.ts, the debounce's teardown cancel proven): Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-11
owner: planner
tree: 99f22479a20e7fa64f8b6654e0d371c595b1e35a
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1546, PL-1286, PL-1556, SL-1557, SL-1559, FD-1611, SL-1639]
---

# PL-1638 — WK-675: the DagDesigner F39 fix slice, Work-plan delta

*Disclosure: drafted under working ids 9918 (this plan), 9916 (its slice row) and 9914 (the
finding it discharges), all reserved by the lead in
`~/gi-pricing-plan.local/handover/brief-wave1b-2026-10-11.md` "Reserved working ids". Minted
2026-10-11 in the slice PR's mint commit: 9918 as PL-1638, 9916 as SL-1639, 9917 as LG-1640; 9914 had already
been minted as FD-1611 in the D10 batch, so no new FD was filed.*

> **For agentic workers:** this is a **one-row WK-675 Work-plan delta** under Lean P2 L5. It
> adds one slice, SL-1639, to WK-675 beside the eight rows of
> [`PL-1546`](PL-01546-wk-675-slices-5-to-11-work-plan-delta.md), which is frozen since its first
> merge, so a new slice is a new delta (`.claude/skills/writing-plans/SKILL.md`, "One plan per
> Work"). No leaf plan. The slice is one PR under L1 (a'); its `LG-` (LG-1640, drafted as working id 9917) quotes the
> row below as its scope. REQUIRED SUB-SKILL for the executor: executing-plans (the slice is
> small). The executor also binds `vue-testing-best-practices`, `vue-frontend`,
> `test-driven-development` (the red seen first, by its cause), `dev-commands` (the two-half
> gate, `uv sync --all-packages` in a fresh worktree) and `git-hygiene`; reads
> [`README.md`](README.md)'s five unchecked conventions; and is spawned from
> `.claude/roles/executor.md`.

Written 2026-10-11 from 10:48 BST (`TZ=Europe/London date`, 10:48:27 BST) by the planner
(planner-wk675). Evidence read at `origin/main` `99f22479a20e7fa64f8b6654e0d371c595b1e35a`
(#1271, WK-675 S3). **No test was run at planning time**; every fact below is a read of a named
file at that tree.

## Authority

- **The fix slice**: the maintainer's (by delegation) entry "2026-10-11 10:38:57 BST — DagDesigner
  F39 reds: an FD against WK-675 at D10 ADOPTED, with a small fix slice queued; …" in
  `channel/to-lead.md`, item 3, verbatim: *"The fix rides as a SMALL fix slice under WK-675 (not
  folded into S4, whose write set is backend), seated in wave 2 ahead of the non-G2 items: — stub
  /rating-algorithms/validate for the whole file (or for the composable's module); — AND flush or
  cancel the debounce in teardown (fake timers or an unmount flush); — red-first: the debounce made
  to fire after the test body (e.g. advance timers past the debounce after the assertions) shows
  the F39 failure on base, and passes after."*
- **The finding**: the same entry, item 2: an FD at D10, owner WK-675 (FD-1611, drafted as working id 9914,
  authored by minter-d10 in the D10 batch).
- **Lane C order**: "2026-10-11 10:39:56 BST — USER: … RULED: WK-675 is OUR standing lane C to
  its end …", item 2, position (0b): *"the DagDesigner F39 fix slice (10:38:57; small)"*.
- **The gate**: "2026-10-11 10:41:41 BST — CORRECTION to my 10:41:33 item 2c: the DagDesigner fix
  gets the FULL two-half gate, not "frontend half plus CI"".

## What the code says, at `99f22479`

- **The guard.** `frontend/src/test-setup.ts` replaces `globalThis.fetch` with a recorder and, in
  an `afterEach`, throws `F39: this test called fetch without stubbing it: <urls>` (:13–24). It
  is the suite's `setupFiles` entry (`frontend/vitest.config.ts:38`).
- **The debounce.** `useGraphValidation(draft, delayMs = 400)`
  (`frontend/src/components/dag/useGraphValidation.ts:14`) watches the draft with
  `immediate: true` and, `delayMs` after the last change, calls `validateRatingAlgorithm` from
  `@/api/ratingAlgorithms` (:34). `DagDesigner.vue:52` calls it with the default, so **the delay
  is 400 ms** and a validate call is scheduled at every mount.
- **The teardown cancel already exists.** `onBeforeUnmount` bumps the sequence and calls
  `cancel()` (`useGraphValidation.ts:52–54`), which clears the timer and aborts the controller
  (:22–25). `@testing-library/vue` unmounts every rendered component in an `afterEach` when
  `afterEach` is global (`dist/index.js:47`, version 8.1.0 in the root checkout's `node_modules`;
  `package.json:33` pins `^8.1.0`), and `vitest.config.ts:37` sets `globals: true`. **So the F39
  window is the test body itself**: a test whose body runs longer than 400 ms after its last draft
  change fires the real fetch. On an idle box no `DagDesigner.test.ts` test does; under a loaded
  gate two did (10:38:57's evidence). No test proves the cancel: `useGraphValidation.test.ts` has
  four tests (:38, :54, :66, :84), none of which unmounts.
- **The un-stubbed file is the only one.** A sweep at `99f22479` over every test file naming
  `DagDesigner`, `RatingDesignView` or `useGraphValidation` (predicate, verbatim:
  `grep -rlE "DagDesigner|RatingDesignView|useGraphValidation" frontend/src --include=*.test.ts`,
  then `grep -c 'vi.mock("@/api/ratingAlgorithms"'` per file): `DagDesigner.test.ts` 0;
  `DagDesignerValidation.test.ts` 1 (:10); `DiffOverlay.test.ts` 1 (:18);
  `useGraphValidation.test.ts` 1 (:10); `RatingDesignView.test.ts` 1 (:17). The only other mount
  of the designer is `views/RatingDesignView.vue`, lazily routed at `router/index.ts:247`; no test
  file that builds a router also names the designer or its view.
- **No shared stub helper exists.** Each of the four files above stubs the module inline
  (`vi.hoisted` plus `vi.mock("@/api/ratingAlgorithms", …)`); `fixtures.ts` in the same
  directory carries graph fixtures only. **So the write set is the one test file**, in the
  sibling files' own pattern.

## Goal

`DagDesigner.test.ts` cannot reach the network through the validate route, whatever the load,
and the designer's debounce is proven to be cancelled when the component unmounts. Done when
SL-1639 closes on its `LG-` with the red on base, the green ×3, the broken-input proof and the
full two-half gate, and FD-1611's register row carries the fix's merge sha.

## Acceptance Standard

Each item is a command run from the slice worktree's root, quoted in the `LG-` with its exit
code and the lines it names. "Base" is `origin/main` at the slice's first commit.

1. **Red first, on base, by its cause.** The regression test (Task 1, step 1) is added to
   `DagDesigner.test.ts` before the stub, and
   `flock -w 300 /tmp/slots/small-test pnpm --dir frontend exec vitest run src/components/dag/__tests__/DagDesigner.test.ts`
   exits 1 with the line `F39: this test called fetch without stubbing it:` naming
   `/api/v1/rating-algorithms/validate`. Any other failure is not the red this slice is about.
2. **Green, three times.** After the stub, the same command exits 0 three times in a row, each
   run listing every test in the file as passed.
3. **The stub is what holds it (broken input).** With the `vi.mock("@/api/ratingAlgorithms", …)`
   line removed (uncommitted), the regression test fails with the item-1 line; restored, it
   passes.
4. **The teardown cancel is proven (broken input).** The unmount test (Task 1, step 3) passes;
   with `cancel();` at `useGraphValidation.ts:54` removed (uncommitted, reverted at once), it
   fails because the mocked `validateRatingAlgorithm` was called after unmount.
5. **Test files only.** `git diff --stat origin/main...HEAD` lists
   `frontend/src/components/dag/__tests__/DagDesigner.test.ts`, the `LG-` and
   `docs/roadmap.md` (SL-1639's status lines) and nothing else.
6. **The full gate is green.** Every `CLAUDE.md` §11 command, both halves, exits 0 against
   `origin/main...<slice branch>`, in gate-1 on the lead's grant, queued in the background.
7. **Barred word.** `git diff origin/main...HEAD | grep '^+' | grep -ciE 'dep''uty'` prints 0.

## Global Constraints

- **Never hand-write an API type** (`CLAUDE.md` §3): the mock returns objects typed by the
  `@/api/ratingAlgorithms` exports, as `DagDesignerValidation.test.ts` does; no shape is redeclared.
- **No source change.** The teardown cancel exists (above); this slice proves it. A change to a
  non-test file stops the slice and goes to the lead (the brief's executor section).
- **The F39 guard is not weakened.** `test-setup.ts` is not in the write set: the fix stubs the
  call; it never silences the guard.
- **One PR per slice** (L1 (a')): the test file, SL-1639's status lines and one `LG-`.
- **Small tests one file at a time under the small-test slot; the full gate only in gate-1 on the
  lead's grant** (`.claude/roles/executor.md`; the brief's rule 4).

## Tasks

Under L5 a Work plan's tasks are its slice rows; this row's steps follow the table.

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Lane | Size |
|---|---|---|---|---|---|---|
| 0b (lane C) | SL-1639 — WK-675 fix slice — FD-1611: DagDesigner.test.ts stubs the validate route, and the debounce's unmount cancel is proven | In `frontend/src/components/dag/__tests__/DagDesigner.test.ts` only: a regression test that lets the 400 ms debounce elapse after its assertions, red on base with F39; the module `@/api/ratingAlgorithms` mocked for the whole file in the sibling files' pattern; a test that unmounts before the debounce elapses and proves no validate call follows. **Out of scope:** any non-test file, including `useGraphValidation.ts` and `test-setup.ts`; the other four test files, which already mock the module | `03` §3: FR-1607 (its live-validation tests, unchanged); register row F39 (the guard, held) | none: S3 (`SL-1557`) is merged; it runs beside S4 (`SL-1559`, backend write set) under `RL-1445` item 2 only if the dispatch names both | C | ≈ 0.25 lane-day, derived: one file, three tests, one full gate |

### Task 1: SL-1639

**Files:** modify `frontend/src/components/dag/__tests__/DagDesigner.test.ts`; create the `LG-`
(LG-1640) under `docs/ledgers/`; `docs/roadmap.md` SL-1639's status lines.

- [ ] **Step 1: the regression test, red on base.** Add a test that renders `DagDesigner` with
  the file's `props`, makes its assertion, then lets the debounce elapse past 400 ms before it
  ends. Either form fires the timer inside the test body: real time
  (`await new Promise((r) => setTimeout(r, 450))`), or fake timers as
  `useGraphValidation.test.ts:31` uses them (`vi.useFakeTimers()`, then
  `await vi.advanceTimersByTimeAsync(400)`, with `vi.useRealTimers()` in an `afterEach`). If fake
  timers are used in a test that also uses `userEvent`, set it up with
  `userEvent.setup({ advanceTimers: vi.advanceTimersByTime })`, or the click waits on a frozen
  clock. Run acceptance item 1's command; quote it, its exit code and the F39 line in the `LG-`.
- [ ] **Step 2: the stub.** Add, at the top of the file, the sibling pattern
  (`DagDesignerValidation.test.ts:9–10`): a `vi.hoisted` object with `validateRatingAlgorithm`
  as a `vi.fn()` and `vi.mock("@/api/ratingAlgorithms", () => api)`, plus a `beforeEach` that
  resets it and resolves it to an empty report (`{ issues: [] }`, the shape the composable
  reads at `useGraphValidation.ts:39`). Mock every export the designer's import graph reads from
  that module, or the mock factory fails at import; the run shows any that is missing.
- [ ] **Step 3: the unmount test.** Render, `unmount()` before 400 ms have elapsed, advance past
  400 ms, and assert the mocked `validateRatingAlgorithm` was not called.
- [ ] **Step 4: green ×3 and the two broken-input proofs** (acceptance items 2–4), each quoted.
- [ ] **Step 5: the diff and the closing acts.** Acceptance items 5 and 7; the `LG-` and the SL
  row `closed` at the head (L1); push; report "ready to queue @<head>"; the full gate on the
  lead's grant (item 6).

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | 10:38:57 item 3's second limb, "flush or cancel the debounce in teardown": add it, or prove the cancel that exists? | (a) prove it: the unmount test (Task 1, step 3) plus its broken-input proof, no source change; (b) add an explicit `afterEach` unmount or timer flush in the test file, redundant with the auto-cleanup | (a): the cancel is at `useGraphValidation.ts:52–54` and runs at testing-library's auto-cleanup; what is missing is the proof, not the mechanism. (b) adds a second teardown that would hide a regression of the first | fact | no; (a) applies unless the lead rules otherwise at the GO | Task 1, step 3 |

## Hand-off (not this plan's writes)

- **The 10:38:57 item 4 interim** ("a gate whose ONLY frontend red is a DagDesigner F39
  un-stubbed-validate failure is classified WK-675's") is not ended by this plan. Whether it
  lapses at SL-1639's merge is the lead's to say.
- **FD-1611's register row and its discharge** are minter-d10's and the auditor's, at D10 and at
  this slice's merge.

## Self-review

- Every requirement id in the row is listed individually (FR-1607, register F39); no range.
- The write set is derived from a full-class sweep (the predicate is quoted above), not from the
  ruling's file name alone; it finds one un-stubbed file.
- The 400 ms delay is read from the source (`useGraphValidation.ts:14`, `DagDesigner.vue:52`),
  not assumed.
- Each acceptance item is a command with an expected exit code; items 3 and 4 fail on broken
  input.
- The plan changes no spec text and rules no decision: DP-1 is a fact with a default the lead may
  overrule at the GO.
