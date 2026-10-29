---
id: FD-8284
family: finding
title: ten NFR-463 lows carried from FD-1959's close — F4, L4 to L10, the unnamed scrollers and the repeated status text
status: active
created: 2026-10-29               # drafted 2026-10-29 under working id 8284
owner: auditor
tree: 265a552ef3584eef22f506b9ffb001e8f3d27948   # origin/draft/sl-8281 as read by the executor, 2026-10-29
corrected_by: []
relates: [FD-1959, OQ-1960, RL-8283, PL-1546, SL-8281]
---

# FD-8284 — ten NFR-463 lows carried from FD-1959's close — F4, L4 to L10, the unnamed scrollers and the repeated status text

## Finding

**LOW, owner WK-675, due Thu 12 Nov 2026 (the P2 exit demo; `date -d 2026-11-12 +%A` prints Thursday).** Authority: the lead's
"2026-10-29 22:34:57 GMT" ruling (a) (aud-a11y's verdicts accepted; the ten carried lows become one new finding, minted in the
PR of SL 8281) and R10-DP2 (a) of "2026-10-29 22:13:59 GMT" (the lows that are not one line are carried, owner WK-675). Filed under
working id 8284.

FD-1959 closes at the merge of SL 8281 on its static limbs (RL-8283). Ten of its lows were not fixed in that slice. With FD-1959
closed they would have no finding, so this record is their home: one row each, with its site **read at the tree
`265a552ef3584eef22f506b9ffb001e8f3d27948`** (`draft/sl-8281` head; every path under `frontend/src/`) and the reason it was carried. No
mispricing and no data loss: every item is a name, a description, a focus order or an announcement on an interactive control whose
accessible name and value path are intact.

## Evidence

| # | Low (FD-1959's label) | WCAG | Site at `265a552e` | Why carried |
|---|---|---|---|---|
| 1 | F4: the help `<p>` has no `id` and the control has no `aria-describedby` | 1.3.1, 3.3.2 | `components/FormField.vue:35-40` (the control is the `<slot />` at `:33`) | Not one line: the control is the caller's slot, so `FormField` cannot set `aria-describedby` itself; it needs a slot prop or an id contract. |
| 2 | L4: `<VueFlow>` leaves `nodesFocusable` true, so each node is an extra tab stop and a second `role="group"` | 2.4.3, 3.3.2 | `components/dag/DagDesigner.vue:226-232` (the `<VueFlow` props); `components/dag/StepNode.vue:22-25` and `components/dag/MountNode.vue:46-52` (`role="group"` with `aria-label`) | Behavioural: node tab stops against the NodeNavigator; no one-line change. FD-1959 cited `StepNode.vue:239` and `MountNode.vue:333`, which do not resolve at this tree (the files are 70 and 103 lines); the `role="group"` lines above are the sites. |
| 3 | L5: `role="dialog"` on an always-visible inline section; no focus management | 4.1.2 | `components/rating/BulkOperationDialog.vue:63` | One line, but the role fix forces an edit of the existing assertion `views/__tests__/RateTableEditorView.test.ts:213` (`getByRole("dialog", { name: "Bulk operation" })`); existing tests stay unedited in this slice (the lead's ruling). |
| 4 | L6: "Review changes" is natively `disabled` with no text saying why | 4.1.2, 3.3.2 | `views/RateTableEditorView.vue:321-327` (`:disabled="!canReview"` at `:324`) | Not one line: `canReview` (`:67-69`) is three conditions (an edit, a non-blank change note, not busy), so the text must say which one fails. |
| 5 | L7: diff results appear on "Show changes", and page changes replace rows, with no announcement | 4.1.3 | `components/rating/RateTableDiffPanel.vue:179-183` (the `role="status"` carries progress text only), the results table from `:206`, the pager `:303-313` | Not one line: the results need a persistent summary region and the pager a count; both are new behaviour. |
| 6 | L8: the focused pager button becomes `disabled` on the last page and focus drops to `body` | 2.4.3 | `components/rating/RateTableDiffPanel.vue:303-313` (`:disabled="history.length === 0"` and `:disabled="nextCursor === null"`) | Not one line: needs a focus move to the other pager button or `aria-disabled`; a behavioural test. |
| 7 | L9: only the free-text and date branch gets `aria-invalid` and `aria-describedby`; the bool and enum controls are not linked to a problem | 3.3.1 | `components/sandbox/QuoteForm.vue:106-111` (bool checkbox), `:112-125` (enum select); the linked branch is `:137-138` | Not one line; whether `buildInputs` can raise a problem for an enum or a bool is not established statically. |
| 8 | L10: changing the status filter re-renders the groups with no result-count announcement | 4.1.3 | `views/RatingVersionListView.vue:118-139` (the `status-filter` select at `:124`) | Not one line: needs a live region with the count, a new element and a test. |
| 9 | The new F6 scrollers have no role or name: unnamed `tabindex="0"` regions | 4.1.2 | `views/RateTableEditorView.vue:277-278`; `components/rating/RateTableDiffPanel.vue:203-204` | Found at the head by the accessibility-tester (item 25, new issue 3). A code change now would move a non-docs file after the gated `6a0927c0`; the editor grid already holds focusable inputs, so its extra tab stop may also be redundant (a design choice for the owner). |
| 10 | Repeated identical status text may not re-announce | 4.1.3 | `views/QuoteSandboxView.vue:208-213` (`Score result: {outcome}.`); `views/RateTableEditorView.vue:256-261` (`Review ready: N cell(s) changed.`) | Found at the head by the accessibility-tester (item 25, new issue 4; the tester gave `QuoteSandboxView.vue:207-212` and `RateTableEditorView.vue:257-261`, one line off the `<p>` bounds read here); whether a screen reader re-announces an unchanged string is a rendered check, so it is OQ-1960's limb; same gated-head reason as row 9. |

Source of the first eight rows: FD-1959's low table (its sites at `origin/main` `7ed5c398`, re-read here at the tree above) and LG-8282's
low-by-low dispositions. Source of rows 9 and 10: the accessibility-tester's report (item 25, static read of `265a552e`), transcribed
by lead 29.

## Severity

**LOW.** Each is a low by FD-1959's own rating; none blocks a task, and the WK-675 forms, status messages and input borders that
FD-1959 rated serious or moderate were fixed in SL 8281.

## Remedy

The owning Work (WK-675) fixes each row, red first in vitest where a behaviour is testable, or accepts it with a dated line, by the
due date above; a rendered claim (focus order, an announcement) is OQ-1960's. WK-675's close
record lists this finding and OQ-1960 as carried forward (RL-8283, "What it obliges").

## Relates

OQ-1960's browser-verification limb (axe-core and Playwright) will re-test the same surfaces: rendered focus order, announcements and
the unchanged-string case belong to it, and a "yes" there is what turns rows 2, 5 to 7 and 9 to 10 from a static reading into a
measured result. FD-1959's essay and register row name this finding for the carried lows.

## Provenance

Carried from FD-1959's close by SL 8281, on the lead's "2026-10-29 22:34:57 GMT" ruling (a). Sites re-read by the executor at the tree
above on 2026-10-29.

## Disposition

Open, owner WK-675, LOW, due Thu 12 Nov 2026. Filed under working id 8284.
