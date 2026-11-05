---
id: PL-8336
family: plan
kind: map
title: WK-1178 — the FR-1530 test awaits the lazy chunk, a deterministic wait for both flake findings (FD-1748, FD-1800), SL-8337 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8336
owner: planner
tree: dae9637ea6f6a56f6502e9db70392cdfb2f3983d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1748, FD-1800, FD-1747, FR-1530]
---

# PL-8336 — WK-1178: the FR-1530 test awaits the lazy chunk (SL 8337, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds one slice row, SL 8337, and edits no filed plan.
> The executor's skills are `superpowers:test-driven-development`, `vue-testing-best-practices`,
> `.claude/skills/vue-frontend` and `git-hygiene`. PL 8336, SL 8337 and LG 8338 are working ids
> reserved by the lead.

## Authority

- **The rulings, closed, verbatim** (the maintainer's entry "2026-11-05 09:51:53 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`): "(3) FD-1800 → option (b), the same deterministic
  wait as FD-1748's ruled remedy; one slice carries both." and "(4) FD-1746, FD-1488, FD-1748
  severities RULED MEDIUM as proposed."
- **FD-1748's ruled remedy** (the entry "2026-10-14 17:51:06 BST", as the essay quotes it): "await the
  chunk … or the component's own ready signal, **never a blanket timeout raise** and never a sleep.
  **Red first**, by forcing a slow chunk load: mock the dynamic import to resolve after more than 1 s
  (a mocked delayed import, injected, not a real wait on the box)". Its event: the slice "awaits the
  lazy chunk in `RatingDesignView.test.ts`, red first with a delayed-import mock, and no timeout
  change".
- **FD-1800's event:** "a merged change to the test (or its setup) plus a repeated run under load that
  does not fail (more than the three solo runs above)".
- **The order.** "2026-11-05 09:58:58 GMT".

## Goal

The FR-1530 test does not race the `DagDesigner` chunk, so it stops failing at random on PR CI and on
loaded gates. Both findings close. No product code changes.

## Evidence at `dae9637e`

- `frontend/src/views/__tests__/RatingDesignView.test.ts:65-73`, the test; `:68-70` `findByLabelText` per
  step, no timeout option; `:23-30` the file's `beforeAll`, which stubs `ResizeObserver`.
- `frontend/src/views/RatingDesignView.vue:21-22`: "Async, so `@vue-flow` stays in its own lazy chunk",
  `defineAsyncComponent(() => import("@/components/dag/DagDesigner.vue"))`, used at `:205`.
- `frontend/vitest.config.ts` sets `setupFiles` (`:38`) and no timeout. No `asyncUtilTimeout` anywhere.
- FD-1748's sweep stands, read against this tree by `git grep -nE 'defineAsyncComponent' origin/main --
  frontend/src`: the only hit is `RatingDesignView.vue:22`. **The pattern occurs once.**
- **FD-1800's cause is a hypothesis in its own text.** Both failures sit 87 ms and 123 ms past 1000 ms,
  on the first query. FD-1748 attributes that to the chunk, FD-1800 to Vue Flow's draw. The ruling joins
  them under one wait. **If the chunk is the whole cause, the repeated run shows it. If it is not, A5
  fails and that is a finding, not a reason to raise a timeout.**
- **The requirement.** FR-1530 (`03:90`) is a read route, and the test's label is the row the test's own
  title names: nothing in the spec changes.
- **A trap in the option's wording.** FD-1800's (b) says "then query with `getBy`". Each later node is
  still drawn by the same pass, but a `getBy` straight after the chunk would assert a synchronous
  draw the view does not promise. The plan keeps `findBy` and removes only the chunk from what it
  waits for: a deterministic wait for the chunk, as FD-1748 rules, and no timer change. DP-F1 asks the
  maintainer to confirm that reading.
- **`hookTimeout`** is vitest's default (10 s): a `beforeAll` import has that budget, against the
  1.1 s seen. It is not raised.

## Decision points

**Both ruled** (the entry "2026-11-05 10:36:35 GMT"): DP-F1 (a); DP-F2 (a), "granted when F asks", "never beside a timed gate
stage". F's gate goes "in the first slot after D's". The table is kept as the record of the options.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-F1 | Does "(b), the same deterministic wait" allow `findBy` after the chunk await? | (a) **Yes:** await the chunk, keep `findBy`. No timer is changed; the default wait now covers only the draw. (b) Also replace `findBy` with `waitFor`-then-`getBy`, the option's literal text. A timer by another name, and a larger diff. | **(a).** It is FD-1748's ruled remedy exactly, which the ruling names as the wait. |
| DP-F2 | What is FD-1800's "repeated run under load", given common seat brief item 28's "load1 < 6"? | (a) **20 consecutive runs of this one file, load1 ≥ 6 read at the start of each, by a written grant lifting item 28 for this file and this count**, outside any gate. (b) 20 runs at whatever load item 28 allows, plus PR CI. Weaker: it is not "under load". | **(a).** The box has sat at 4 to 9 today, so no load need be manufactured. Any one failure fails A5. |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's merge
tree. Items 1 and 2 apply to this plan; A1 to A8 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing
   line except check 31 / check 32 lines naming working ids 8336, 8337 or 8338. After the mint,
   `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no
   line that stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only
  `frontend/src/views/__tests__/RatingDesignView.test.ts`, LG 8338, and the mint's files. **Not**
  `RatingDesignView.vue`, `vitest.config.ts` or `test-setup.ts`.
- **A2. Red first, by cause, for both findings.** LG 8338 quotes, on the slice's named base with the
  delayed-import mock of R1 in place: `FR-1530 … Unable to find a label with the text of: input step
  Driver age (s_in_age)`, failing just past 1000 ms. The mock is **injected and not committed**.
- **A3. Green under the same mock.** With R2 in place and the same mock, the file passes. `git diff
  --quiet` on the test file after removing the mock, rc 0 against the commit.
- **A4. No timer.** `git diff origin/main...HEAD -- frontend | grep -E '^\+.*(timeout|Timeout|setTimeout|sleep)'`
  prints nothing, and no `asyncUtilTimeout` or `configure(` is added.
- **A5. The repeated run under load**, as DP-F2 rules: every run's `Test Files  1 passed`, its load1 and
  its rc, in LG 8338. **Zero failures in the count.** One failure stops the slice and is reported with
  its time and its query: FD-1800's hypothesis then did not hold.
- **A6. The GREEN set and the gate.** The file's own closure (common seat brief, item 29): commands and
  list in the LG. **The full code gate, both halves, SOLO**, green at the re-merged head, every rc quoted,
  with the `Test Files N passed` line.
- **A7. The closing acts.** **FD closing act in the FD-1842 form, in the slice's own PR, by the slice's
  auditor,** for FD-1748 and FD-1800: the essay's `status: closed`, `relates:` gaining the slice's ids, a
  `***Resolved <date>***` paragraph naming the delivered remedy, its red and its LG, the same on the
  register row, and the PR number and squash at the merge's date of record. Each register row records its
  ruling of 09:51:53.
- **A8. The LG Audit section**, with the lead's adoption, lands in the audit's own commit, and
  `docs/INDEX.md` is regenerated after the closing acts (common seat brief, item 17).

## Global Constraints

- **G1. Never a blanket timeout raise, never a sleep** (FD-1748, ruled).
- **G2. The view is correct and is not touched** (FD-1748 §0).
- **G3. The vitest guard binds every run** (common seat brief, item 28, the maintainer's "2026-10-22
  13:34:04 BST"): `test -f "$FILE" || exit 64`, the call names that path, and the run passes only if its
  output shows `Test Files  1`.
- **G4. No test is removed or weakened** (common seat brief, item 13).

## Needs

No DB, no Redis, no docker, nothing on the NFR VM. A5's written grant, outside any gate, about 15 min.

## Tasks

### SL 8337 — the deterministic wait

**The row.** WK-1178 fix slice. One `sonnet` executor. Requirements: FR-1530 (the test's subject; no
spec change). Register: FD-1748 and FD-1800 (both MEDIUM), closing at the merge (A7). Depends on: the GO; A5's grant; the first gate slot
after D's. **Size:** 1.5 h (triage 2 h), with A5's 15 min. SOLO gate about 2.5 h, not
counted. Merged before Thu 12 Nov 2026; still red at Wed 11 Nov 12:00 → the exception list.

**R1 — red first (injected, not committed).** At the top of the test file, in the working tree only:

```ts
vi.mock("@/components/dag/DagDesigner.vue", async (importOriginal) => {
  await new Promise((resolve) => setTimeout(resolve, 1200));
  return importOriginal();
});
```

Run the file by G3's form, one file. **The red:** A2's line. The other tests that await "Algorithm
version" stay green, which shows the delay reached only the chunk. A mock that does not delay the import
is a failed proof: if the file is green here, stop and report.

**R2 — green.** In the file's existing `beforeAll` (`:23`):

```ts
beforeAll(async () => {
  // A browser API happy-dom lacks (Vue Flow itself is NOT stubbed here).
  globalThis.ResizeObserver ??= class { ... };
  // The chunk the view's `defineAsyncComponent` loads, so a `findBy` waits for the draw and
  // never for the import (FD-1748, FD-1800). Deterministic: no timer is changed.
  await import("@/components/dag/DagDesigner.vue");
});
```

With R1's mock still in, the file passes (A3). Remove the mock. Commit the `beforeAll` only.

**R3 — A5's runs,** under the grant. **G.** Full code gate, both halves, SOLO. CI set from the three-dot
diff: `frontend`, `docs`, `history-policy`; `python` only if a filter matches.

### Write set

- `frontend/src/views/__tests__/RatingDesignView.test.ts`.
- LG 8338 under `docs/ledgers/`.
- At the mint: the SL 8337 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, the two essays
  and `docs/findings/register.md` (A7).

### Files shared with other groups

None. **Safe in parallel with every group.** It needs no window but A5's grant.

## Hand-off (not this plan's writes)

- The GO and A5's grant: the maintainer. The gate slot: the lead. The LG: the executor. A7:
  the auditor.
- **The gate order is ruled:** F in the first slot after D's (10:36:35), as FD-1748's "land early" asks.
- **After merge:** common seat brief item 25's standing FR-1530 re-run rule has no further use. Retiring it
  is the maintainer's.

## Self-review

1. **Every cite was read** at `dae9637e`. 2. **Requirements by id**, no range. 3. **No placeholder:** `{ ... }`
is the file's existing class body, unchanged. 4. **The red is by cause and injected,** as ruled. 5. **The
rulings are carried verbatim.** 6. **The unverified hypothesis is named,** and A5 tests it. 7. **Calendar:**
12 Nov 2026 is a Thursday, 11 Nov a Wednesday.
