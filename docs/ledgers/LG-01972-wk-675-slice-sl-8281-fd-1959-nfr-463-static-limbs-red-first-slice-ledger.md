---
id: LG-1972
family: ledger
title: WK-675 slice SL-1971 — FD-1959's NFR-463 static limbs on the WK-675 surfaces, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-29               # drafted 2026-10-29 under working id 8282
owner: executor
tree: aad4fd58bde87f59fffe646466f4f86bb2373bf8   # origin/main at the branch cut
slice: SL-1971
phase: P2
work: WK-675
plans: [PL-1546]
corrected_by: []
relates: [FD-1959, PL-1546]
---

# LG-1972 — WK-675 slice SL-1971: FD-1959's NFR-463 static limbs, red first

**GO:** to-lead "2026-10-29 22:13:59 GMT": PL-1546 row 10 ACCEPTED at 7e14e2e3; R10-DP1 (b), R10-DP2 (a), R10-DP3 (b), R10-DP4 (c); executor seated for T0 and T1 only (the fix, T2, is on the lead's word).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

Row 10 of `docs/plans/PL-01546-wk-675-slices-5-to-11-work-plan-delta.md`, "### Row 10 — FD-1959: NFR-463's static limbs on the WK-675 surfaces" (acceptance items 17 to 27, R10-DP1 to R10-DP4). Requirement: NFR-463 (`docs/specs/00-overview.md:586`). Branch `draft/sl-8281` from `origin/main` aad4fd58; `git merge --no-ff origin/draft/pl-a11y` (head 7e14e2e3) brought the accepted row in as merge a8303d94.

### Task list

- [x] **T0. Base re-read** (below, "T0").
- [x] **T1. Reds** (below, "T1"). Tests only; no `.vue` edit.
- [ ] T2 the fix, T3 greens, T4 the gate, T5 records: not started (the lead's word).

### Gate

(Not yet run: T4.)

### Audit

(Written by the auditor.)

### Build log

#### 2026-10-29 T0 — base re-read at `a8303d94` (merge of the row onto aad4fd58)

Every line the row quotes is unchanged at the base:

- `DecimalCellInput.vue` :34 `const isInvalid = computed(() => syntaxError.value || Boolean(props.invalid));` · :50 `:aria-invalid="isInvalid ? 'true' : 'false'"` · :51 `:aria-describedby="invalid ? errorId : undefined"` · :54 `:class="isInvalid ? 'border-red-600' : 'border-slate-300'"` · :58 `v-if="invalid"`.
- F3 sites, each a `<p v-if=... aria-live="polite">` that mounts with its text: `RateTableDiffPanel.vue:173-186` (loading/waiting, stalled), `RateTableEditorView.vue:250-256` (`created`), `BulkOperationDialog.vue:126-131` (`created`), `RateTableImportExport.vue:137-142` (`created`).
- M3 `RateTableEditorView.vue`: `<section v-if="diff" aria-label="Changes to confirm">` starts at :323 (the row's 313-330 spans the button and the section). M4 `QuoteSandboxView.vue:208-226`: `<template v-if="result">` at :208, closing `</div>` :226, no live region and no focus move.

Lows, re-located by description at the base:

| Low | Site at base | Class | Red written |
|---|---|---|---|
| F4 | `FormField.vue:35-40` help `<p>` has no `id`; the control is the caller's slot | not one line: the control is a slot, so FormField cannot set `aria-describedby` itself (needs a slot prop or an id contract) | none; carried (R10-DP2 (a)) unless the lead rules a shape |
| F5 | `class="hover:underline"` at `QuoteSandboxView.vue:117`, `DislocationView.vue:88`, `RegressionSuiteView.vue:80`, `RateTableEditorView.vue:224`, `RatingDesignView.vue:103` | one class per site; class only, not testable in vitest | grep: `git grep -n 'hover:underline'` prints those 5 lines (no `underline` without hover) |
| F6 | scroll regions without `tabindex`: `RateTableEditorView.vue` the `overflow-x-auto` div around `RateTableGrid` (:271), `RateTableDiffPanel.vue:204`, `RegressionSuiteView.vue:243-244` (the counterexample `<pre>`) | one line each | 3 tests (below) |
| L4 | `DagDesigner.vue:226-232`, `StepNode.vue:239`, `MountNode.vue:333` | behavioural (node tab stops against the NodeNavigator) | none; carried |
| L5 | `BulkOperationDialog.vue:63` `role="dialog"` | one line, **but** `RateTableEditorView.test.ts:213` asserts `getByRole("dialog", { name: "Bulk operation" })`: the fix needs that existing assertion edited, which needs the lead's OK | grep: `role="dialog"` at :63; no test written |
| L6 to L10 | as FD-1959 lists | not one line | none; carried (R10-DP2 (a)) |
| L11 | `RegressionSuiteView.vue:243-244` `aria-label` on a bare `<pre>` | one line (a role, or move the label) | 1 test |
| L12 | first column is `<td>` (golden :186, property :229); `:173` is a `<th scope="col">` as the row said | one line per table | 1 test |

#### 2026-10-29 T1 — the reds

Tests commit `9fe6a6b0` on `draft/sl-8281`. Each file run alone, `Test Files  1` each, load1 < 2 each; logs `~/gi-pricing-plan.local/scratch/draft-sl-8281/*.red.log` (`head=` first, `rc=` last; run on `a8303d94` plus the then-uncommitted test files, the same bytes as `9fe6a6b0`'s tests; no `.vue` differs). Existing tests in each file pass unedited (the failed counts below are exactly the new tests).

| File | Result | New red test → assertion line |
|---|---|---|
| `components/rating/__tests__/DecimalCellInput.test.ts` | 2 failed, 5 passed (incl. the server-error test :36-41) | F1 `expect(input).toHaveAccessibleDescription("Enter a decimal number")` → received `""`; same for `"Enter a whole number"` with `integer` |
| `…/RateTableDiffPanel.test.ts` | 2 failed, 9 passed | F3 `AssertionError: expected [] to include <p aria-live="polite" …>`; F6 `expect(element).toHaveAttribute("tabindex", "0")` |
| `…/BulkOperationDialog.test.ts` | 1 failed, 6 passed | F3 `AssertionError: expected [] to include <p aria-live="polite" …>` |
| `…/RateTableImportExport.test.ts` | 1 failed, 6 passed | F3 `AssertionError: expected [] to include <p aria-live="polite" …>` |
| `views/__tests__/RateTableEditorView.test.ts` | 3 failed, 10 passed | F3 `expected [] to include <p aria-live="polite" …>`; M3 `expected false to be true` (no persistent region and no focus on the heading); F6 `toHaveAttribute("tabindex", "0")` |
| `views/__tests__/QuoteSandboxView.test.ts` | 1 failed, 19 passed | M4 `expected false to be true` (no persistent region, no focus in the result) |
| `views/__tests__/RegressionSuiteView.test.ts` | 3 failed, 11 passed | L12 `Unable to find an accessible element with the role "rowheader"`; L11 `expected true to be false` (a bare `<pre>` with no role); F6 `toHaveAttribute("tabindex", "0")` |

Method for F3, M3 and M4: the test records the live regions (`[role="status"], [aria-live="polite"]`) before the trigger, and asserts the element that holds the message after the trigger is one of them, so a region that mounts with its text by `v-if` fails and a persistent region passes. M3 and M4 also pass if focus moves to the heading or into the result.

**F2 baseline (item 20 (a)), no vitest red.** `git grep -n 'border-slate-300' HEAD -- frontend/src ':!*__tests__*'` at `a8303d94`: 122 hits (`f2-grep.log`; counted `grep -c "^HEAD:"`). On inputs, selects or textareas (R10-DP1 (b) set): `DecimalCellInput.vue:54`; `BulkOperationDialog.vue:81,107,116`; `RateTableDiffPanel.vue:140,160`; `RateTableEditorView.vue:310`; `QuoteSandboxView.vue:174`; `QuoteForm.vue:74,95,116,136`; `DagDesigner.vue:295`; `DislocationView.vue:114`; `RegressionSuiteView.vue:129`; `RatingVersionListView.vue:126`; and the sweep additions `dag/DiffOverlay.vue:86`, `RatingDesignView.vue:158`, `dag/MountInspector.vue:69` (the `field` constant), `dag/StepInspector.vue:44`. Other WK-675 hits are `<section>`, `<th>`, button or node borders, not F2's 1.4.11 limb (`RateTableDiffPanel.vue:126,213-250,303,311`, `RateTableGrid.vue:68`, `RateTableImportExport.vue:93,101`, `RateTableEditorView.vue:284,292,326,357`, `DagDesigner.vue:222,308,317`, `NodeNavigator.vue:163,202`, `StepNode.vue:24`, `MountNode.vue:49`, `DislocationView.vue:119`, `BulkOperationDialog.vue:65`).

#### 2026-10-29 T2/T3 — the fix and the greens (lead's GO, to-lead 22:15:19 cont.)

Source commit `0fd78f71`, test typing commit `6a0927c0` (head `6a0927c0b4301b8bec17e38b9af6d55feb690499`). Source edits only in `frontend/src/**/*.vue`: `DecimalCellInput` (F1: one message tied by `aria-describedby` whenever invalid, "Enter a decimal number" / "Enter a whole number"), `RateTableDiffPanel`, `BulkOperationDialog`, `RateTableImportExport`, `RateTableEditorView` (F3/M3: a `role="status"` region always rendered, only its text conditional; the editor also has an `sr-only` status that announces the review), `QuoteSandboxView` (M4: `sr-only` status "Score result: <outcome>."), F2 on the 23 input hits (`border-slate-300` → `border-slate-500`), F5 (`hover:underline` → `underline` at the 5 sites), F6 (`tabindex="0"` on the three scroll regions), L11 (`role="group"` + `tabindex="0"` on the counterexample `<pre>`), L12 (`<th scope="row">` for the first column of the golden and property tables). No `package.json`, lockfile, backend or deploy change.

Each red file re-run singly at the fix head (logs `*.green.log`, `head=` first, `rc=` last): DecimalCellInput 7 passed rc=0; RateTableDiffPanel 11 passed rc=0; BulkOperationDialog 7 passed rc=0; RateTableImportExport 7 passed rc=0; RateTableEditorView 13 passed rc=0; QuoteSandboxView 20 passed rc=0; RegressionSuiteView 14 passed rc=0 (these ran at `0fd78f71`; `6a0927c0` changed only the helper's TypeScript signature, and the full suite below ran on it).

**F2 evidence (item 20).** (b) `contrast.py` (quoted in `contrast.log`) reads `--color-slate-500: oklch(55.4% 0.046 257.417)` from the installed `tailwindcss/theme.css`: hex #62748e, relative luminance 0.17026, contrast against #ffffff = **4.77:1** (≥ 3:1). (a) `f2-after.log`: over the 14 R10-DP1 (b) files, `git grep -n -B8 'border-slate-300'` finds no `<input>`, `<select>` or `<textarea>`; the 21 remaining hits are a canvas, `<section>`, `<th>` and button borders. Outside WK-675 `border-slate-300` is still on inputs (`FactorCreateForm`, `RuleBuilder`, `FactorWorkbenchView`, …): R10-DP1 (c), not this slice.

**GREEN set by import closure (item 29).** `python3 -I closure.py <wt>` (`closure.log`): changed non-test modules = `git diff --name-only origin/main...HEAD -- frontend/src` minus `__tests__` (15); closure = those + importers + one more level (43 files); GREEN = every test file importing a closure file (25): components/dag/__tests__/DagDesigner.test.ts, components/dag/__tests__/DagDesignerMounts.test.ts, components/dag/__tests__/DagDesignerValidation.test.ts, components/dag/__tests__/DiffOverlay.test.ts, components/dag/__tests__/MountInspector.test.ts, components/dag/__tests__/StepInspector.test.ts, components/rating/__tests__/BulkOperationDialog.test.ts, components/rating/__tests__/DecimalCellInput.test.ts, components/rating/__tests__/RateTableDiffPanel.test.ts, components/rating/__tests__/RateTableGrid.test.ts, components/rating/__tests__/RateTableImportExport.test.ts, router/__tests__/guard.test.ts, router/__tests__/index.test.ts, router/__tests__/objectiveEditorRoute.test.ts, router/__tests__/routeGraph.test.ts, views/__tests__/DiagnosticsView.test.ts, views/__tests__/DislocationView.test.ts, views/__tests__/ModelComparisonView.test.ts, views/__tests__/ModelDetailView.test.ts, views/__tests__/QuoteSandboxView.test.ts, views/__tests__/RateTableEditorView.test.ts, views/__tests__/RatingDesignView.test.ts, views/__tests__/RatingDesignViewMounts.test.ts, views/__tests__/RatingVersionListView.test.ts, views/__tests__/RegressionSuiteView.test.ts. The full suite below includes all of them.

**The lows (item 21).**

| Low | Disposition |
|---|---|
| F4 | **carried**: needs a FormField contract, not one line; owner WK-675, to the P2 close with OQ-1960 (the lead's ruling, R10-DP2 (a)) |
| F5 | **fixed**: `hover:underline` → `underline` at `QuoteSandboxView.vue:117`, `DislocationView.vue:88`, `RegressionSuiteView.vue:80`, `RateTableEditorView.vue:224`, `RatingDesignView.vue:103`; grep: no `hover:underline` remains at them |
| F6 | **fixed**: `tabindex="0"` at `RateTableEditorView` (grid wrapper), `RateTableDiffPanel` (results wrapper), `RegressionSuiteView` (counterexample `<pre>`); 3 tests green |
| L4 | **carried** (behavioural; node tab stops against the navigator): owner WK-675, to the P2 close with OQ-1960 |
| L5 | **carried**: the fix would edit `RateTableEditorView.test.ts:213`; existing tests stay unedited in this slice; owner WK-675, to the P2 close with OQ-1960 (the lead's ruling) |
| L6 to L10 | **carried** (R10-DP2 (a)): owner WK-675, to the P2 close with OQ-1960 |
| L11 | **fixed**: `role="group"` + `tabindex="0"` on the `<pre>`, `RegressionSuiteView.vue`; 1 test green |
| L12 | **fixed**: `<th scope="row">` for the first column of the golden and property tables; 1 test green |

#### 2026-10-29 T4 — the frontend half of the gate (R10-DP3 (b)), head `6a0927c0b4301b8bec17e38b9af6d55feb690499`

Each command its own call, logs `gate-<name>.log` (`head=` first, `rc=` last), run in the slice worktree, load1 3.4 at the start:

| Command (`pnpm --dir frontend …`) | rc |
|---|---|
| `install --frozen-lockfile` | 0 |
| `generate:api` | 0 |
| `lint` | 0 |
| `type-check` | 0 |
| `test` | 0 — `Test Files  137 passed (137)`, `Tests  905 passed (905)` |
| `build` | 0 |

A first run at `0fd78f71` had `type-check` rc=2 (12 `TS2379` errors in my new live-region helper's `HTMLElement` signature, which also failed `test` and `build`); fixed in `6a0927c0` (helper typed over `Element`) and the whole table re-run at the new head. The first-run logs were overwritten.

Docs set: see the next entry.

#### 2026-10-29 T4 — the docs set, at head `69d14488ca2930925b599df7c60faa937d442051`

Logs `docs-audit.log`, `docs-index.log`, `docs-register.log` (`head=` first, `rc=` last); audit-docs and doc-index through `run-heavy.sh --light` (load1 2.55), register-lint under the gate-2 flock. A first attempt was refused at load1 4.96 (rc=66) and retried at 2.55.

| Check | rc | Reading |
|---|---|---|
| `audit-docs.py` | 1 | 6 FAILED, all expected and named: check 32 ×5 (`LG-1972` and `SL-1971` do not resolve in `docs/INDEX.md`: working ids, minted by the lead) and check 39 (`docs/INDEX.md` stale: not regenerated before the mint, seat brief item 17). No other failure. |
| `doc-index.py --check` | 1 | `docs/INDEX.md is stale` (the same check 39 cause: the new LG is not in it). |
| `register-lint.py` | 0 | `register.md: OK (0 violations)` |

No `status:` or id was changed under `docs/` other than this ledger's own working ids, so `docs/INDEX.md` is left for the mint.

### Audit (auditor, 2026-10-29)

*Proposed verdicts only; the verdicts are the lead's (`delivery-process.md` §5). Range: `origin/main...draft/sl-8281`; tree: `265a552ef3584eef22f506b9ffb001e8f3d27948` (`git ls-remote` re-read 22:2x GMT, unmoved). Read-only: no test, DB, docker or git write was run. The frontend gate ran at `6a0927c0`; `69d14488` and `265a552e` change only this ledger (`git diff --stat 6a0927c0 265a552e`: 1 file).*

**Scope, derived from the spec first** (PL-1546 "Row 10", items 17 to 27; FD-1959 Finding, Evidence and Remedy; NFR-463; R10-DP1 (b), DP2 (a), DP3 (b), DP4 (c) from to-lead "2026-10-29 22:13:59 GMT"): F1 (item 17), F3 at four sites (18), M3 and M4 (19), F2 (20; sites = the 14 listed plus DiffOverlay:86, RatingDesignView:158, MountInspector:69, StepInspector:44), the 12 lows F4, F5, F6, L4 to L12 (21), the diff scope (22), the import-closure GREEN set (23), the gate (24), the accessibility-tester (25), the FD-1959 records (26) and the merge date (27).

| # | Evidence | Proposed verdict |
|---|---|---|
| 17 F1 | `DecimalCellInput.red.log` (head a8303d94): 2 failed, 5 passed; `toHaveAccessibleDescription` received `""` for both `1.2.3` and `12.5` with `integer`; green log rc=0, 7 passed. Tests also `getByText(...).toBeVisible()`. Server-error test unedited (`git diff --numstat origin/main...HEAD -- '*__tests__*'`: every test file additions only, 0 deletions). Source: `message` computed, `:aria-describedby="isInvalid ? errorId : undefined"`, `v-if="isInvalid"`. | **delivered and tested** |
| 18 F3 ×4 | Four component reds, each `AssertionError: expected [] to include <p aria-live="polite" …>` (no region before the trigger): DiffPanel, EditorView, BulkOperationDialog, ImportExport; all four green (rc=0). Source: `role="status"` rendered always, text conditional (diff read). | **delivered and tested** |
| 19 M3, M4 | `RateTableEditorView.red.log` M3 and `QuoteSandboxView.red.log` M4: `expected false to be true` (no persistent region, no focus move); green rc=0. Source: `<p role="status" class="sr-only">` placed outside the `v-if="diff"` section (EditorView) and outside `<template v-if="result">` (QuoteSandboxView :209–214), so the region is in the DOM before the text. | **delivered and tested** |
| 20 F2 | (a) `f2-after.log` (head 6a0927c0): the 14 R10-DP1 (b) files hold no `border-slate-300` on an input, select or textarea; my own classification over the whole tree at `265a552ef3584eef22f506b9ffb001e8f3d27948` (`classify.py`, 102 hits) agrees: every input-like hit is in 13 files outside the scope (53 hits). The remaining in-scope hits sit on buttons (e.g. DagDesigner:308, DiffOverlay:92), `th`, `section`, as the log's element column shows. The four unlisted R10-DP1 sites are fixed (diff: `const field` in MountInspector and StepInspector, DiffOverlay, RatingDesignView). (b) slate-500 #62748e vs #ffffff: seat 4.77:1; recomputed here 4.76:1 (WCAG 2.2 luminance 0.1704); the replaced slate-300 is 1.48:1. Both ≥ 3:1. | **delivered, evidenced** (no vitest red by design; broken-input proof is the base hit count 122 → 102 and the 1.48:1 baseline) |
| 21 lows | 12 lines in LG-1972 (F4, F5, F6, L4 to L12). Fixed with hunk and test or grep: F5 (5 sites `hover:underline` → `underline`, verified in the diff), F6 (3 `tabindex="0"`, 3 red/green tests), L11 (`role="group"`, 1 test), L12 (`<th scope="row">` ×2, 1 test). Carried (R10-DP2 (a), owner WK-675, to the P2 close with OQ-1960): F4, L4, L5, L6, L7, L8, L9, L10. | fixed 4: **delivered and tested** (F5: **delivered, grep-evidenced**). Carried 8: **deferred with an owner**, but the LG lines give no calendar date; item 21 asks for "owner and date" → **date owed** (see carries) |
| 22 diff scope | `git diff --name-only origin/main...HEAD`: 22 `.vue`/test files, plus the LG and PL-1546 (the accepted row's merge). No `package.json`, lockfile, spec or contract. The roadmap SL row, the FD-1959 essay, the register row and `docs/INDEX.md` are **not yet in the diff** (T5 not done). | **not started** for the records (T5, with the mint); the code scope is clean |
| 23 GREEN set | `closure.log` (head 0fd78f71): 15 changed non-test modules, closure 43, GREEN 25 files; the decisive full suite below runs all of them. The sandbox/QuoteForm, RatingVersionListView and DislocationView tests are in the list. | **delivered** (the closure list was not recomputed here; the full suite covers any miss) |
| 24 gate | Frontend half at `6a0927c0`, every log `head=` first and `rc=` last: install 0, generate:api 0, lint 0, type-check 0, test 0 (`Test Files  137 passed (137)`, `Tests  905 passed (905)`), build 0. Docs set at `69d14488`: audit-docs rc 1 with exactly 6 FAILED (check 32 ×5 on LG-1972/SL-1971, check 39 INDEX stale) and no other failure; doc-index --check rc 1 (the same stale INDEX); register-lint rc 0. **Owed, not run:** the 8 docs-audit pytest files via run-small, `req-coverage.py` and `generate-contracts.py --check` (R10-DP3 (b) names the docs-only set; item 30), all after the mint. The END row is not yet in the LG. | frontend half **delivered and tested**; docs half **not started** until the mint; END row **owed** |
| 25 accessibility-tester | `item25-a11y-check-report.md` (static read of `265a552e`, transcribed by lead 29): PASS on F1, F2 (all listed + R10-DP1 (b) sites; slate-500 4.76:1, matches my recomputation, the seat's 4.77 is 0.01 high), F3 ×4, M3, M4, F5 on the five sites, F6 ×3, L11, L12. Four new issues: (1) ~60 input-like borders outside the list → the candidate finding; (2) `hover:underline` remains on in-text links outside the five sites (LargestMovers:126, ModelDetailView:172/186, DatasetDetailView:97/123; 1.4.1 applicability not established) → the candidate finding; (3) the new F6 scrollers have no role or name (RateTableEditorView:277, RateTableDiffPanel:203; the editor grid already holds focusable inputs) and (4) repeat announcements with an unchanged string may not re-announce (QuoteSandboxView:207-212, RateTableEditorView:257-261) → carried lows, owner WK-675, to the P2 close with OQ-1960 (lead's disposition 2026-10-29). Not statically verifiable: real announcement, focus order and visible focus, rendered contrast (OQ-1960's limb). Shows F1, F3, M3, M4 and the in-scope F2 sites as PASS, as item 25 requires. | **delivered, evidenced** (the report is the lead's transcription of the agent's return; quote it in the LG per item 5's form) |
| 26 FD-1959 records | Drafted in `closes.md` and the scratch draft of RL-1973; nothing applied to the branch (T5). | **not started** (drafts ready) |
| 27 merge ≤ 2026-10-30 | Not merged; 2026-10-30 is a Friday (`date -d`). | **open** |

**Reds by cause.** All seven red logs name the cause in an assertion line, not a generic failure: description `""` (F1); `expected [] to include <p aria-live>` (F3 ×4); `expected false to be true` with the test's own message about no region or focus (M3, M4); `tabindex` missing (F6 ×3); no `rowheader` (L12); a bare `<pre>` with a name (L11). Base and test bytes: the red logs say `head=a8303d94 (+uncommitted …)`; no test file differs between `9fe6a6b0` and the fix `0fd78f71` (`git diff --name-only 9fe6a6b0 0fd78f71 -- '*__tests__*'` prints nothing), so the tests that went red are the committed ones. The only later test edit, `6a0927c0`, changes 4 lines per file ×5: the helper's type (`HTMLElement` → `Element`).

**Greens.** Seven green logs rc=0, `Test Files  1 passed (1)` each, `head=8e6ac342 (+uncommitted source)`. The ledger says they ran at `0fd78f71`; the log header names its parent plus an uncommitted tree, so the stated head is inexact (wording to correct). They are superseded as evidence by the full-suite gate at `6a0927c0` (137 passed), which includes all seven files.

**What the overwritten first-run logs cost as evidence.** The type-check rc 2 at `0fd78f71` (12 TS2379 in the seat's own helper, also failing `test` and `build`) rests on the ledger's word. It costs nothing the verdict depends on: the fix is verifiable (`git diff 0fd78f71 6a0927c0` is the 4-line helper retyping in 5 test files) and the whole table was re-run at the new head, all rc 0. It does cost the record of the first run's other failures: if `test` or `build` failed for any reason besides the helper, no log shows it. A broader point for the lead: single-file vitest runs do not type-check, so a typing error in a new test helper was invisible until the gate (a process-backlog line, not a finding).

**For the lead's record (brief item 3).** The seat ran vitest and the build bare, not through `run-heavy`, because the T4 list named the bare commands: a brief defect, not the seat's. The docs checks did go through `run-heavy.sh --light` and the gate-2 flock.

**Observations (not blocking; for item 25 and OQ-1960).** (1) The F6 `tabindex="0"` wrappers on the editor grid and the diff-results scroller are focusable `div`s with no role or name (only the regression `<pre>` got `role="group"` and its label); a focusable region without a name is a 4.1.2-adjacent question for the accessibility-tester. (2) The M4 test finds its region by `/quoted/i` on the region text, tying it to the outcome value "quoted"; red by cause at base, so it works. (3) The ledger and the accessibility-tester say ~60 outside-WK-675 input borders; my classification counts 53 input-like hits in 13 files at the head (heuristic, see the candidate draft); the difference is unreconciled and the lead should re-count before quoting a number. (4) The accessibility-tester's issue 3 repeats my observation (1).

**Carries, with owner and date.**
| Carry | Owner | Date |
|---|---|---|
| F4, L4, L5, L6, L7, L8, L9, L10, plus the accessibility-tester's new 3 (unnamed focusable scrollers) and 4 (repeat announcements) | WK-675 | "the P2 close" per R10-DP2 (a); **calendar date not written in the LG; the lead names it** |
| OQ-1960 (the browser-verification limb: axe-core and Playwright) | WK-675 | decided at the P2 close |
| The 8 docs-audit pytest files, req-coverage, generate-contracts --check, INDEX regeneration | the executor, after the mint | before the PR |
| The outside-WK-675 input borders (candidate finding) | the Work that owns each surface; no live owner found (Phase 1 surfaces) | the lead decides whether it is filed in this PR |

**Open for the lead.** (a) With FD-1959 closing at the merge (RL-1973), the ten carried lows (the eight and the tester's two new) lose their finding; WK-675's close record is then their home (R10-DP2 (a)) and must list them. (b) The RL's owner field: the brief says `lead`; `document-ids.md` §1.6 names the decision-maker, with the maintainer able to author one.

**Verdicts (lead 29, on to-lead 2026-10-29 22:34:57 GMT):** items 17–20, 23, 25 delivered; 21 delivered for F5, F6, L11, L12 and the rest carried as FD-1974 (owner WK-675, due Thu 12 Nov 2026); 22 and 26 delivered by this mint; 24 delivered — the frontend half of §11 at 6a0927c0 all rc 0 (137 test files, 905 tests) and the docs half at this mint's head rc 0 (quoted below); 27 open until the merge (on or before 2026-10-30).

#### Note — the candidate finding is not filed (lead 29, RULED (b), to-lead "2026-10-29 22:34:57 GMT"; register-free)

R10-DP1 (b) left a candidate finding for the input borders outside WK-675's surfaces. It is **not filed in this PR**, and no `FD-` number is minted for it; two heuristics give two counts, and neither is reconciled:

- **The auditor's `classify.py`** (`~/gi-pricing-plan.local/scratch/a11y-aud/classify.py`; command `python3 -I classify.py 265a552ef3584eef22f506b9ffb001e8f3d27948`, re-run by the executor at the mint: 102 lines, byte-identical to the auditor's `classify-head.txt`). Selection rule, verbatim from the script: the files are `git grep -l border-slate-300 <ref> -- frontend/src ':!*__tests__*'`; for each hit line, the tag is the last `<tag` found scanning back from that line up to 15 lines (`re.findall(r'<([a-zA-Z][\w-]*)', line)`, the last match on the first line that has one); a hit with no tag, or on a line with `const ` or an `=` and no `<` and no `class=`, is `CONST?`. A hit is input-like when its tag is `input`, `select` or `textarea`. Result at `265a552e`: 102 hits (29 select, 25 button, 21 input, 8 th, 8 RouterLink, 4 section, 3 textarea, 3 div, 1 ul); input-like 29 + 21 + 3 = **53 hits in 13 files, all outside the WK-675 surfaces** (`outside-typed.txt`, `outside-by-file.txt`). The auditor's own limit: two `input` hits sit within six lines of a `type="button"`, so the true count may be 51 to 53.
- **The accessibility-tester's static read** (item 25, new issue 1): "about 60" (the report's "~60"), with **no predicate given**.

Unreconciled; the finding is filed in the next docs batch with a predicate-stated recount and owners per surface.

#### 2026-10-29 mint — the records and the docs half of §11, at head `9c710d61f07e99e2286345a59b85611d2b64687e`

Executor, on the lead's brief under the grant "2026-10-29 22:34:57 GMT". Free-check of ids 1971 to 1974 on `origin/main` `aad4fd58`: both greps empty. Mint tool `mint-repoint.py` (sha256 `4d83681a0f30b3301cc05afc7992634d67fb8499ef06f56c50df5f91902f286d`), `--frozen-on origin/main`: dry run 59 re-points, real run 59, identical (the three front-matter id lines were hand-edited first). The non-docs diff since the gated head is empty: `git diff --name-only 6a0927c0 HEAD -- . ':!docs'` printed nothing, so the frontend half stands at `6a0927c0` and was not re-run. Two corrections after the first audit-docs run at `729e58e5` (check 37 on RL-1973, check 32 on this ledger's audit section line quoting the scratch draft's file name) are named in the commit message of `9c710d61`.

| Check (docs half, run at `9c710d61`) | rc | Result |
|---|---|---|
| `uv run ruff check .` | 0 | `All checks passed!` |
| `audit-docs.py` (run-heavy `--light`) | 0 | `All checks passed.`, DISCLOSED 849 at or under the W37-11 ceiling |
| `doc-index.py --check` | 0 | `OK (byte-stable)` |
| `register-lint.py` | 0 | `OK (0 violations)` |
| `req-coverage.py` | 0 | completed |
| `generate-contracts.py --check` | 0 | `58 generated contracts match the models` |
| `tests/test_audit_docs_finding_citations.py`, `test_audit_docs_ids.py`, `test_audit_docs_process_core_digest.py` (run-small) | 0 | `124 passed in 277.13s` |
| `tests/test_audit_docs_w37_11_ceiling.py`, `test_doc_index.py`, `test_register_lint.py` (run-small) | 0 | `110 passed in 133.66s` |
| `tests/test_register_owed.py`, `test_repository_invariants.py` (run-small) | 0 | `23 passed in 104.77s` |

Quote parity `265a552e..729e58e5`: `quote-parity: 29 changed line(s), 0 violation(s); quote-parity rc=0`.

## PRs

(None yet.)
