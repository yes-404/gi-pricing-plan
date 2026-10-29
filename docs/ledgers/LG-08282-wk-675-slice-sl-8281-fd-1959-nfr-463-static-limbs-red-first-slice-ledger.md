---
id: LG-8282
family: ledger
title: WK-675 slice SL-8281 — FD-1959's NFR-463 static limbs on the WK-675 surfaces, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-29
owner: executor
tree: aad4fd58bde87f59fffe646466f4f86bb2373bf8   # origin/main at the branch cut
slice: SL-8281
phase: P2
work: WK-675
plans: [PL-1546]
corrected_by: []
relates: [FD-1959, PL-1546]
---

# LG-8282 — WK-675 slice SL-8281: FD-1959's NFR-463 static limbs, red first

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

## PRs

(None yet.)
