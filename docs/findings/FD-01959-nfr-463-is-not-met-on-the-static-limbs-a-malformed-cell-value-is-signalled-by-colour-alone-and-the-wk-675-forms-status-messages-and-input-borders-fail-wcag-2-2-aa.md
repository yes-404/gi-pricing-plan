---
id: FD-1959
family: finding
title: NFR-463 is not met on the static limbs — a malformed cell value is signalled by colour alone, and the WK-675 forms, status messages and input borders fail WCAG 2.2 AA
status: closed
created: 2026-10-29               # drafted 2026-10-26 under working id 8272
owner: auditor
tree: a3969209d62012cd6206a81598094d799efaa2cf
corrected_by: []
relates: [WK-675, CR-1952, PL-1546, RL-1307, RL-1973, FD-1974, OQ-1960, SL-1971, LG-1972]
---

# FD-1959 — NFR-463 is not met on the static limbs

## Finding

**MEDIUM; owner WK-675; fix before WK-675's close, by Tue 3 Nov 2026.** A WCAG 2.2 AA failure on the rate-table editing path;
no mispricing and no data loss; it blocks WK-675's acceptance through NFR-463. Authority: the maintainer (by delegation), `to-lead.md`
"2026-10-26 15:37:48 GMT — Maintainer: NFR-463 NOT MET at 7ed5c398 (static read) — YES to one new FD, working id 8272 (next 8273),
MEDIUM, owner WK-675, fix before WK-675's close by Mon 3 Nov" (the weekday corrected to Tuesday by the entry "2026-10-26 16:00:41 GMT":
`date -d 2026-11-03 +%A` prints Tuesday; the date stands). Filed under working id 8272.

NFR-463 (`docs/specs/00-overview.md:586`): WCAG 2.2 AA; every chart has an accessible tabular equivalent that reads its cells from
the chart's own rows (`ChartFigure` column descriptors, RL-1307). At `origin/main` `7ed5c398333aa24432bd9917bd204f7b540fb39c`, on the
static limbs, NFR-463 is **not met**: 17 distinct FAIL defects, 0 critical, 1 serious, 4 moderate, 12 low. The chart limb holds.

The serious one, F1 (verified by the maintainer (by delegation) at `origin/main`, 15:37:48): `frontend/src/components/rating/DecimalCellInput.vue`
:34 `isInvalid = syntaxError || Boolean(props.invalid)` and :50 `aria-invalid` follow `isInvalid`, but :51 `aria-describedby="invalid ? errorId : undefined"`
and :58 `v-if="invalid"` render the message only for the server's `invalid` prop. A malformed number sets the red border and
`aria-invalid` with no text (WCAG 3.3.1, and 1.4.1: colour is the only visible cue).

## Evidence

Source: the report `~/gi-pricing-plan.local/scratch/a11y-nfr463/report-2026-10-26.md` (local, not in the repository; it lands verbatim
in `LG-1673`'s dated 2026-10-27 section). **Tree:** `.claude/worktrees/tools-main` at `7ed5c398333aa24432bd9917bd204f7b540fb39c`, read-only.

**Method and stated limits.** Static code review of the Vue sources and the installed `@vue-flow/core` dist. No browser, no screen
reader, no axe (axe and Playwright are not in `frontend/package.json`). Everything needing rendering is "NOT VERIFIABLE STATICALLY".
`vitest run` over the dag, rating, sandbox and dislocation component directories plus the 5 view tests: 31 files, 221 tests passed,
no type errors, rc 0. **That is not a gate pass:** lint, type-check, build and generate:api were not run. Contrast is computed from the
Tailwind v4 default palette hexes (text pairs all pass 4.5:1; `border-slate-300` on white is about 1.6:1).

**The report's summary table, verbatim:**

| Severity | Count | Defects |
|---|---|---|
| critical | 0 | |
| serious | 1 | F1 |
| moderate | 4 | F2, F3, editor review section, sandbox result |
| low | 12 | F4, F5, F6, DAG node tab stops, bulk `role=dialog`, review button disabled w/o reason, diff results/pager unannounced, diff pager focus loss, QuoteForm enum/bool unlinked, list filter unannounced, regression `<pre aria-label>`, regression row headers |

| View | PASS | Own FAIL | Cross-cutting FAIL hitting it | NOT VERIFIABLE |
|---|---|---|---|---|
| DAG designer | 7 | 1 | F2, F4 | 3 |
| Rate table editor | 3 | 5 | F1, F2, F3, F5, F6 | 3 |
| Rate table diff panel | 5 | 3 | F2, F3, F6 | 2 |
| Quote sandbox / compare | 6 | 2 | F2, F4, F5 | 2 |
| Dislocation views | 4 | 0 | F2, F5 | 1 |
| Rating version list | 6 | 1 | F2 | 0 |
| Regression suite | 3 | 2 | F2, F5, F6 | 1 |

**The 17 defects with their sites** (all paths under `frontend/src/`; line numbers as the report gives them at `7ed5c398`):

| # | Defect | WCAG | Severity | Sites |
|---|---|---|---|---|
| F1 | A malformed number is shown by border and `aria-invalid` only; no message text, no `aria-describedby` | 3.3.1, 1.4.1 | serious | `components/rating/DecimalCellInput.vue:31-34,50-61`; test asserts only `aria-invalid` (`DecimalCellInput.test.ts:19,33,39`) |
| F2 | Every text input, select and textarea has a `border-slate-300` boundary, about 1.6:1 against 3:1 | 1.4.11 | moderate | `DagDesigner.vue:295`, `RateTableDiffPanel.vue:140,160`, `DecimalCellInput.vue:54`, `BulkOperationDialog.vue:81,107,116`, `QuoteForm.vue:74,95,116,136`, `RateTableEditorView.vue:310`, `QuoteSandboxView.vue:174`, `DislocationView.vue:114`, `RegressionSuiteView.vue:129`, `RatingVersionListView.vue:126` |
| F3 | Status text mounted together with its live region by `v-if`; screen readers generally miss it | 4.1.3 | moderate | `RateTableDiffPanel.vue:173-186`, `RateTableEditorView.vue:250-256`, `BulkOperationDialog.vue:128`, `RateTableImportExport.vue:139` (four sites in the report; the ruling says "three places") |
| M3 | "Review changes" mounts the "N cells changed / Confirm" section with no focus move, no live region, no status | 4.1.3 | moderate | `views/RateTableEditorView.vue:323-363` |
| M4 | The score result replaces a hint paragraph with no live region and no focus move | 4.1.3 | moderate | `views/QuoteSandboxView.vue:208-226` |
| F4 | Help text is a bare `<p>` with no `id` and no `aria-describedby` on the control | 1.3.1, 3.3.2 | low | `components/FormField.vue:35-40` |
| F5 | Breadcrumb links are told from text by hover underline only | 1.4.1 | low | `QuoteSandboxView.vue:117`, `DislocationView.vue:88`, `RegressionSuiteView.vue:80`, `RateTableEditorView.vue:224`, `RatingDesignView.vue:103` |
| F6 | Horizontally scrolling regions with no `tabindex` | 2.1.1 | low | `RateTableEditorView.vue:271`, `RateTableDiffPanel.vue:204`, `RegressionSuiteView.vue:244` |
| L4 | `<VueFlow>` leaves `nodesFocusable` true: every node an extra tab stop, a second `role="group"`, a false "select / move node with arrow keys" description | 2.4.3, 3.3.2 | low | `DagDesigner.vue:226-232`, `StepNode.vue:239`, `MountNode.vue:333` |
| L5 | `role="dialog"` on an always-visible inline section; no focus management | 4.1.2 | low | `BulkOperationDialog.vue:62-64` |
| L6 | "Review changes" is natively `disabled` with no text saying why | 4.1.2, 3.3.2 | low | `RateTableEditorView.vue:313-320` |
| L7 | Diff results appear on "Show changes", and page changes replace rows, with no announcement | 4.1.3 | low | `RateTableDiffPanel.vue` (results; pager `:304,312`) |
| L8 | The focused pager button becomes `disabled` on the last page; focus drops to `body` | 2.4.3 | low | `RateTableDiffPanel.vue:304,312` |
| L9 | Only the free-text/date branch gets `aria-invalid`/`aria-describedby`; bool and enum controls are not linked to the problem | 3.3.1 | low | `QuoteForm.vue:99-141,259-266` (whether `buildInputs` can raise a problem for an enum is not established statically) |
| L10 | Changing the status filter re-renders the groups with no result-count announcement | 4.1.3 | low | `RatingVersionListView.vue:122-136` |
| L11 | `aria-label` on a bare `<pre>` (generic role, name ignored) | 4.1.2 | low | `RegressionSuiteView.vue:243-244` |
| L12 | First column is a `<td>`, not `<th scope="row">` | 1.3.1 | low | `RegressionSuiteView.vue:173,215` |

The labels M3, M4 and L4 to L12 are this essay's, for reference; the report names those defects by description. The report counts the
chart-site list as "all 6 chart sites" in one line and names five (ladder waterfall, change histogram, segment grid ×2, attribution
waterfall), and its summary says five; five is the count here.

**The chart limb holds (delivered).** All five chart sites go through `ChartFigure`, which always renders the table in the DOM with
column descriptors: the ladder waterfall (`LadderWaterfall.vue:27-36`, Rung / Value / Change / Operation), the change histogram, the two
segment grids and the attribution waterfall (direction as "+"/"−" bar labels and a "Direction" Increase/Decrease column,
`AttributionWaterfall.vue:72-81`); the diff shading writes direction as sign and `%` in the cell (`diffShading.ts:28-30`).
NFR-463's tabular-equivalent limb is **delivered** at all five sites; recorded the same way in the addendum to `CR-1952`.

**Evidence gaps (the report's, gaps and not passes):** the 221 passing tests assert `aria-invalid`, `aria-live`, `aria-expanded` and
listbox keyboard behaviour; none asserts live-region announcement after a result, focus order or contrast.

## Severity

**MEDIUM**, as ruled: a WCAG AA failure on the editing path, no mispricing, no data loss, and it blocks WK-675's acceptance through
NFR-463. The auditor's reading agrees: F1 is serious by WCAG impact (a user who cannot see colour gets no error text), but it is a UI
defect on a path whose server-side refusals are already text; the rating is the maintainer's.

## Remedy

**Fix limb (before WK-675's close, by Tue 3 Nov 2026, owner WK-675): F1 and the four moderates, red first in vitest where testable.**
- F1: a test that types a malformed number into `DecimalCellInput` and asserts the message text and `aria-describedby`; red on the
  current component (no text, no `aria-describedby`), green after.
- F3: a test that the live region is present before the status text mounts, at each of the four sites.
- F2: the input boundary raised to 3:1 (a class change); not testable in vitest (rendered contrast), so evidence is the class and the
  computed ratio.
- M3 and M4: an announcement (a persistent status region or a focus move) when the review section and the score result appear;
  testable as the F3 form.

**Low limb: the 12 lows (F4, F5, F6, L4 to L12 above), each with its site above;** each fixed in the same slice where it is one line,
otherwise carried in this essay with a dated line naming its owner.

**Carried limb: the static-only limit.** Dated 2026-10-26: rendering checks (contrast as rendered, focus order, announcements, Focus Not
Obscured 2.4.11, reflow, text spacing, target size) are unverified without a browser pass. The decision on adding axe-core and
Playwright to `frontend/package.json` is OQ-1960, owner WK-675, decided at the P2 close; a "yes" changes `docs/skills-map.md` in the same PR.
The user's acceptance of WK-675 reads this finding and OQ-1960, not a "pass".

## Disposition

Open, owner WK-675. The finding closes when F1 and the four moderates are fixed and their tests are green on `origin/main`, the lows are
fixed or carried with a date, and OQ-1960 is decided.

*(Amended 2026-10-29 by RL-1973, on the maintainer's entry "2026-10-29 22:13:59 GMT" (`to-lead.md`), R10-DP4 (c); append-only — the paragraph above is kept.)* FD-1959 closes at the merge of SL-1971 on its static limbs: F1, F2, F3, M3, M4 and the lows as R10-DP2 sets them. The condition "and OQ-1960 is decided" no longer gates the close: the browser-verification limb (axe-core and Playwright; rendered contrast, focus order, announcements, 2.4.11, reflow, text spacing, target size) lives in OQ-1960 only, owner WK-675, decided at the P2 close.

***Resolved 2026-10-29***: closed by the merged fix, this PR (SL-1971 / LG-1972; the merge sha is added at the read-back) and amended by RL-1973. Fixed: F1 (`DecimalCellInput.vue`: one message tied by `aria-describedby` whenever invalid), F3 at the four sites and M3, M4 (a persistent `role="status"` region), F2 (`border-slate-300` to `border-slate-500`, 4.77:1 on white by the seat's script and 4.76:1 recomputed by the auditor and the accessibility-tester, at the R10-DP1 (b) input sites), F5, F6, L11, L12. Carried, owner WK-675, due Thu 12 Nov 2026 (the P2 exit demo), as **FD-1974**: F4, L4, L5, L6, L7, L8, L9, L10, and two found at the head by the accessibility-tester (the unnamed focusable scroll regions at `RateTableEditorView.vue:277` and `RateTableDiffPanel.vue:203`; a repeated identical status text that may not re-announce at `QuoteSandboxView.vue:208-213` and `RateTableEditorView.vue:256-261`). The browser-verification limb is held by **OQ-1960** alone. Evidence: reds by cause at base `aad4fd58` and greens at the slice head, frontend gate `Test Files  137 passed (137)` at `6a0927c0`, the F2 ratio and grep, and the accessibility-tester's report: LG-1972 "Build log" and "Audit". The input borders outside WK-675's surfaces (53 input-like hits in 13 files by the auditor's `classify.py`, "about 60" by the accessibility-tester, unreconciled) are not filed in this PR; LG-1972 carries a register-free note and the finding is filed in the next docs batch.
