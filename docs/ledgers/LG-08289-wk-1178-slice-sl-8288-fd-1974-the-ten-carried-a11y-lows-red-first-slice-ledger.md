---
id: LG-8289
family: ledger
title: WK-1178 slice SL-8288 — FD-1974's ten carried a11y lows (NFR-463) on the WK-675 surfaces, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-03
owner: executor
tree: a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe   # origin/main at the branch cut
slice: SL-8288
phase: P2
work: WK-1178
plans: [PL-1927]
corrected_by: []
relates: [FD-1974, PL-1927]
---

# LG-8289 — WK-1178 slice SL-8288: FD-1974's ten carried a11y lows, red first

**GO:** to-lead "2026-11-03 15:52:04 GMT": the GO on PL-1927 row 7 (S5); DP-S5-1 (a), DP-S5-2 (a), DP-S5-3 (a), DP-S5-4 (a), DP-S5-5 (G1, the full code gate); owner WK-1178; and "2026-11-03 15:46:13 GMT" (full speed).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

`docs/plans/PL-01927-…` section "Delta, row 7 (S5) — FD-1974: the ten carried a11y lows (NFR-463) on the WK-675 surfaces", cherry-picked unedited from 6793eedd (`-x`, clean). Requirement: NFR-463 (no spec change). Lows L-1 to L-10 of FD-1974, one row each in that section's table.

### Task list

- S5-0 Base: `origin/main` a8ef6f19. `git diff --name-only c807a59d..HEAD -- frontend/src` printed nothing; every site was re-read and matches the row's quotes.
- S5-1 Reds: 70b22c5e (tests only), run singly at head ebec1394; logs under `~/gi-pricing-plan.local/scratch/sl-8288-fd1974-a11y-lows/red-*.log` (head= first, rc= last).
- S5-2/3 Fixes: one commit per file group (see Build log); the DP-S5-2 test edit is its own commit b90a751d.
- S5-4 Greens: each red file singly at the final head (below). The import-closure GREEN set and the gate are G1, the lead's slot.

### Gate

Not run by the executor (DP-S5-5 G1: the lead grants the slot). Executor's own checks at head 16daec1c: `pnpm --dir frontend lint` rc=0; `pnpm --dir frontend type-check` rc=0.

### Audit

(The auditor's.)

### Build log

2026-11-03 (GMT), executor exec-s5lows, branch sl-8288-fd1974-a11y-lows from a8ef6f19.

**T0.** No `frontend/src` change since c807a59d; sites re-read unchanged (FormField.vue:35-40, DagDesigner.vue:226-231, BulkOperationDialog.vue:63, RateTableEditorView.vue:162-169/276-279/321-327, RateTableDiffPanel.vue:179-184/201-206/301-316, QuoteForm.vue:106-116, RatingVersionListView.vue:118-139, QuoteSandboxView.vue:78).

**Reds** (head=ebec139489862384d21ff7032c38861d32f1a82a with the tests of 70b22c5e in the tree; rc=1 each; one vitest file per run):
- L-1 `FormField.test.ts` "gives the slot the help id…": `expect(element).toHaveAccessibleDescription()` (no description: the control is not tied to the help).
- L-1 on QuoteForm `QuoteFormA11y.test.ts` (run as `QuoteForm.test.ts`): "describes a ranged int by its hint…": `toHaveAccessibleDescription()`.
- L-2 `DagDesigner.test.ts` "renders no node wrapper that is focusable": `AssertionError: expected …(11) to have a length of +0 but got 11`.
- L-3 `BulkOperationDialog.test.ts` "is found by its heading as a region": `Unable to find an accessible element with the role "region" and name "Bulk operation"`.
- L-4 `RateTableEditorView.test.ts` "L-4…": `expect(element).toHaveAccessibleDescription()`.
- L-5 `RateTableDiffPanel.test.ts` "L-5…": `Unable to find an element with the text: Showing 2 changed cells, page 1.`.
- L-6 same file "L-6…": `AssertionError: expected <body><div>…(1)</div></body> to be <button type="button" …(1)></button>` (focus fell to body).
- L-7 enum `QuoteFormA11y.test.ts` "marks a required enum…": `expect(element).toHaveAttribute("aria-invalid", "true")`.
- L-8 `RatingVersionListView.test.ts` "keeps a status region…": `Unable to find an element with the text: Showing 3 rating versions.`.
- L-9 `RateTableEditorView.test.ts` "L-9…" and `RateTableDiffPanel.test.ts` "L-9…": `Unable to find an accessible element with the role "region"` (names "Rate table cells", "Changed cells").
- L-10 editor `RateTableEditorView.test.ts` "L-10…": `AssertionError: expected <p role="status" class="sr-only"></p> to be null` (the stale "Review ready" status stands while the second review is pending).

**Fixes:** 673b822b L-1 (+ L-7 enum, which shares QuoteForm's `describedBy` helper); b90a751d the DP-S5-2 edit of `RateTableEditorView.test.ts:213` (dialog → region, same name); b6341d5c L-2; 7c877c30 L-3; the diff panel L-5/L-6/L-9; the editor L-4/L-9/L-10; the list L-8; a style commit (eslint --fix); a rename; an `ObjectivePicker` prop type fix (vue-tsc TS2379 under exactOptionalPropertyTypes).

**Two departures from the row, named.** (1) The row names a new `components/sandbox/__tests__/QuoteForm.test.ts`, which differs only in case from the existing `quoteForm.test.ts`; vue-tsc refuses the pair (TS1149, type-check rc=2). The file is `QuoteFormA11y.test.ts`. (2) The diff panel's L-5, L-6 and L-9 are one file and one commit; the editor's L-4, L-9, L-10 likewise; L-7's enum rides the L-1 commit.

**Greens** (each head=16daec1c4c0278a064ef4556eefe9f23bdc123d8 first line, rc=0 last line; logs `green-*.log` beside the reds): FormField 6/6; DagDesigner 7/7; BulkOperationDialog 8/8; RateTableEditorView 16/16; RateTableDiffPanel 14/14; QuoteFormA11y 3/3; RatingVersionListView 17/17.

**Static evidence (dated 2026-11-03, tree 16daec1c):**
- L-2, the duplicate `role="group"`: `components/dag/StepNode.vue:22` `role="group"`, `:25` `:aria-label="label"`; `components/dag/MountNode.vue:46` `role="group"`, `:52` `:aria-label="label"`. Vue Flow's node wrapper is the focusable element (11 wrappers with `tabindex="0"` at the base, 0 after); the inner `role="group"` stays. Rendered focus order and announcements stay OQ-1960's.
- L-7 bool: `components/sandbox/quoteForm.ts:60-63` `if (field.type === "bool") { inputs[field.name] = value === true; continue; }` — no problem is ever set for a bool, so there is no failing case and no change.
- L-10 sandbox: `views/QuoteSandboxView.vue:78` `result.value = null;` before the await, so the status region empties between two scores; no change; re-announcement is OQ-1960's.
- Acceptance 4: `grep -n 'role="dialog"' frontend/src/components/rating/BulkOperationDialog.vue` prints nothing. Acceptance 5: `DagDesigner.vue:232: :nodes-focusable="false"`. Acceptance 6: the editor grid (`RateTableEditorView.vue:284-286`) and the diff scroller (`RateTableDiffPanel.vue:230-232`) carry `role="region"`, an `aria-label` and `tabindex="0"`.

## PRs

(None yet; the lead opens it.)
