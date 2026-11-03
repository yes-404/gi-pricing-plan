---
id: LG-1988
family: ledger
title: WK-1178 slice SL-1987 — FD-1974's ten carried a11y lows (NFR-463) on the WK-675 surfaces, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-03
owner: executor
tree: a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe   # origin/main at the branch cut
slice: SL-1987
phase: P2
work: WK-1178
plans: [PL-1927]
corrected_by: []
relates: [FD-1974, PL-1927]
---

(Minted 2026-11-03 from working id 8289, with SL-1987 from working id 8288, on the lead's mint order and the mint tool of record `mint-repoint.py` (sha256 `4d83681a`); finding FD-1974; executed on branch `sl-8288-fd1974-a11y-lows`.)

# LG-1988 — WK-1178 slice SL-1987: FD-1974's ten carried a11y lows, red first

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

## 2026-11-03 — the gate of record (rc 124) and the StepInspector 3.3.1 assertion change

**Gate of record** (head=211e1d4b184aa2134dc3b6ff9aaf4ee458e9d5a0; logs `scratch/sl8288-gate/gate/`, 16:11:49 → 18:19:37 GMT): END `rc=124` (the demo stage hit its time cap). Rc parts: ruff 0, mypy 0, import_linter 0, req_coverage 0, contracts 0; audit_docs 1 and pytest 1 (`13 failed, 7024 passed, 22 skipped, 5 xfailed`: the 1(f) docs-audit set, cleared at the mint); frontend `Test Files 1 failed | 137 passed (138)`, `Tests 1 failed | 918 passed (919)` (the one failure is `StepInspector.test.ts`, below); demo=124 (dislocation #1 669 s against 422 / 387 / 383 s on the 29 Oct passes, at load1 up to 4.98 with seats running beside it: contention, not the slice). Template guard exact at END; zeros clean. Rulings: the maintainer, to-lead "2026-11-03 18:21:40 GMT" (1)–(4): the known classes cleared at the mint, skipped 22 = baseline, the frontend half and the demo stage re-run SOLO on a quiet box, the python half standing on `git diff --stat 211e1d4b <new head>` showing `frontend/src` and this LG only.

**The test change** (the lead's item-13 OK; the maintainer's acceptance, to-lead "2026-11-03 18:06:07 GMT" (a)). `frontend/src/components/dag/__tests__/StepInspector.test.ts`, test "3.3.1: a field with a required-field problem is marked invalid and points at the problem list". The "Reason code" `FormField` has `help="Required (FR-225)."`, so its slot `describedby` is the help id `${fieldId}-help` = `si-reason-help` (`FormField.vue:31`), and `StepInspector.vue:574` binds `` `${describedby ?? ''} si-problems`.trim() ``: the attribute is the token list `si-reason-help si-problems`, which the exact assertion refused. Only the assertion line changes; it gets stricter on tokens (both required) and no looser on the problem list.

Before: `expect(field).toHaveAttribute("aria-describedby", "si-problems");`

After:
```
expect((field.getAttribute("aria-describedby") ?? "").split(/\s+/)).toEqual(
  expect.arrayContaining(["si-reason-help", "si-problems"]),
);
```

Run (tree d0dc6466): `vitest run src/components/dag/__tests__/StepInspector.test.ts` rc 0, `Test Files  1 passed (1)`, `Tests  11 passed (11)`; `pnpm type-check` rc 0; `pnpm lint` rc 0.

## PRs

(None yet; the lead opens it.)
