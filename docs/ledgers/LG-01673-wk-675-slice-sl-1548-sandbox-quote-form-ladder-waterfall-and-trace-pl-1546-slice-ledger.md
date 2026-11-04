---
id: LG-1673
family: ledger
title: WK-675 slice SL-1548 — Sandbox, quote form, ladder waterfall and trace (PL-1546), slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-12  # minted 2026-10-12
owner: executor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-675
slice: SL-1548
plans: [PL-1546, PL-1286]
corrected_by: []
relates: [PL-1546, PL-1286, RL-1459, OQ-1460, FD-1671, FD-1335, SL-1367, FR-213, FR-247, FR-248, FR-249, FR-251, FR-252, FR-255, FR-256, FR-258, FR-25, NFR-463]
---

# LG-1673 — WK-675 slice SL-1548: Sandbox, quote form, ladder waterfall and trace

*(Minted 2026-10-12 as LG-1673 from working id 9869, at the merge turn. Live citations are re-pointed; quoted entries, command output and the build log's dated lines keep the working id they were written under.)*

**GO:** the maintainer's (by delegation) entry in `to-lead.md`: "2026-10-12 02:53:52 BST — Readiness rulings: GO S6 SL-1548 (swap planner-wk673-c out); FD 9862 LOW, owner WK-677; PL 9864 + PL 9865 deltas OK; FD 9860 (ii)", item 1: "GO SL-1548 (WK-675 S6), executor-sl1548 (sonnet) … R6.1: the per-peril components render ABSENT, with a test, while OQ-1460 is open. The S5 `ordered` drift is recorded in eta: whichever of S5/S6 merges second re-merges and re-gates its quote-form tests." The lead's readiness record of 2026-10-12 02:53:18 BST: `SL-1367` closed (`13a02bba`, #1282), the only activation need.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Quoted from `PL-1546`'s order table, row 2: "SL-1548 — S6: Sandbox: form, waterfall, trace | `PL-1286` S6 row, plus R6.1–R6.2 | `03` §3.1: FR-213; §3.6: FR-247, FR-248, FR-249 (shown absent, R6.1); §3.7: FR-251, FR-252, FR-255, FR-256; §3.8: FR-258; FR-25; NFR-463 | S1 (closed, met); **`SL-1367` merged** (FD-1335 hold)". Requirements: FR-213, FR-247, FR-248, FR-249 (view limb carried under `OQ-1460`, below), FR-251, FR-252, FR-255, FR-256, FR-258, FR-25, NFR-463.

Branch `sl-1548-wk675-s6-sandbox`, worktree `.claude/worktrees/sl-1548`, cut from `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9`. Row: `SL-1548` in `docs/roadmap.md`.

**R6.1 — FR-249's view limb is carried under `OQ-1460`.** `RL-1459`: FR-249's per-peril limb has no producer yet, so S6 builds no view for it; the per-peril components render absent, with a test that asserts their absence while `OQ-1460` is open.

### Task list

- **T1 — API client and form logic.** `frontend/src/api/score.ts` (`POST /score`, generated types); `components/sandbox/quoteForm.ts`, `QuoteForm.vue` (FR-213). The form types values only; range, domain and pattern stay the platform's (`INPUT_CONTRACT_VIOLATION`). A `decimal` input is sent as a JSON number because `packages/pricing-core/src/pricing_core/rating/score.py:353` refuses anything but `int`, `float` or `Decimal` (a string fails `INPUT_CONTRACT_VIOLATION`), and `QuoteContext.inputs` is `dict[str, object]` (`packages/model-schema/src/model_schema/scoring.py:109`, so the generated type is `additionalProperties: true`). The JSON-number path is kept, ruled by the lead (from-lead "2026-10-12 03:04:15 BST"): it is the platform's contract (`scoring.py:109`; `score.py:353`; `score.py:955-962`). Decimal inputs cross `/score` as binary floats, so no exact path exists beyond about 15 significant digits. Carried under FD-1671, a platform finding that is not this slice's to fix.
- **T2 — Ladder waterfall.** `LadderWaterfall.vue`, `ladder.ts` through `ChartFigure` (FR-247, FR-248, FR-252, NFR-463). **Currency: none is picked.** Amounts render as two-decimal major units with no symbol, and the chart and table caption say "currency not configured (OQ-551)". Carried under `OQ-551` (open); the lead's correction of 2026-10-12 replaced an earlier hard-coded GBP.
- **T3 — Outcome, typed errors, trace.** `QuoteOutcome.vue` (FR-256), `QuoteError.vue` (FR-255), `TraceTimeline.vue` (FR-258).
- **T4 — View, route, link.** `QuoteSandboxView.vue`, route `/rating/:slug/v/:version/sandbox`, link from `RatingVersionView` (FR-25, FR-251).
- **R6.1 (FR-249).** No component reads a rung's `components`; tests in `LadderWaterfall.test.ts`, `QuoteOutcome.test.ts` and `QuoteSandboxView.test.ts` assert the absence. The view limb is carried under `OQ-1460`.
- **Write set (inferred).** `PL-1546` and `PL-1286` give S6 no write-set list; the set inferred, and accepted by the lead on 2026-10-12, is the files above plus this ledger, the `SL-1548` row and `docs/INDEX.md`. 

### Gate

Full two-half gate, granted by the lead at 03:13:49 BST on gate-1, at head `c0d3923495dad3f25c2da78ff7f46ffd3f76c120` (clean tree), own database, run 03:14–04:04 BST under `flock /tmp/slots/gate-1` through `handover/slot-preflight.sh`. Output `/home/puzhenhao1989/gi-pricing-plan.local/evidence/sl1548-gate.out`, per-stage logs `.../evidence/sl1548-gate-logs/`.

| stage | exit | cause |
|---|---|---|
| ruff | 0 | |
| mypy | 0 | |
| import-linter | 0 | |
| pytest | 1 | 13 failed, 5708 passed, 6 skipped (45 min 48 s): all 13 are the audit-on-tree test class, failing on check 31 only (see below) |
| audit-docs | 1 | check 31 only: "gap in the full allocation between 1646 and 9869" (this ledger's working id, unminted) |
| req-coverage | 0 | |
| contracts --check | 0 | |
| frontend install | 0 | |
| frontend generate:api | 0 | |
| frontend lint | 0 | |
| frontend type-check | 0 | |
| frontend test | 0 | |
| frontend build | 0 | |

The 13 pytest failures, each read in the log: `test_audit_docs_finding_citations::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`, `test_audit_docs_ids::test_the_real_tree_passes_all_ten_checks`, `test_audit_docs_ids::test_doc_id_check_exits_0_on_the_real_tree`, `test_audit_docs_process_core_digest` (two), `test_audit_docs_w37_11_ceiling::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`, `test_doc_index::test_an_index_skipping_a_reserved_block_breaks_contiguity`, `test_register_lint` (three), `test_register_owed::test_check_29_wiring_is_undisturbed`, `test_repository_invariants` (two). Each asserts a clean docs audit or a contiguous allocation on the real tree and reports the 1646-to-9869 gap (twelve name it or check 31 in their message; the ceiling test's baseline run is the same `audit-docs` exit 1). Expected and removed at the mint, when LG 9869 takes its sequence number; the minted-head gate re-proves them.

### Audit

Written by the auditor (`auditor-sl1548`), 2026-10-12, over `origin/main...129fae7c94ef652c59a711965f65bf4ea64951d0` (`origin/main` `249670fe`, the final head the lead named; PR #1291). The code was first audited at `a73444fd` (interim table accepted by the lead), then at this head. Scope was derived first from `PL-1546`'s order-table row 2 (S6), R6.1 and R6.2, and the `PL-1286` S6 row, and only then evidenced from the diff, the tests' asserts and the gate logs. The lead's rulings applied are quoted by header, since the entries are local channel files (RFC-777): `to-lead.md` "2026-10-12 02:53:52 BST" and "2026-10-12 03:04:43 BST"; the lead's "2026-10-12 03:04:15 BST" and "2026-10-12 03:13:49 BST".

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | FR-213 quote form from the input contract | MET | `QuoteForm.vue`, `quoteForm.ts` type values only and leave range, domain and pattern to the platform; `quoteForm.test.ts` (6 tests, including "does not re-check range or domain"). Red-first. |
| 2 | FR-251 explicit `rating_version_ref`, `what_if`, trace on | MET | `QuoteSandboxView.test.ts:104`. |
| 3 | FR-247, FR-248, FR-252, NFR-463 waterfall with its table, `instalment_loading` present and absent | MET | `LadderWaterfall.vue` through `ChartFigure`; `LadderWaterfall.test.ts:28,38`; `ladder.test.ts` (rung changes, operation operands as sent). |
| 4 | FR-256 declined quote is a result, reasons plural, ladder still shown | MET | `QuoteOutcome.vue`; `QuoteSandboxView.test.ts:122`. |
| 5 | FR-255 typed errors rendered distinctly | MET | `QuoteError.test.ts`: an `it.each` over the four error codes, a field-naming test, and a fallback test that never shows a generic failure; the fifth kind, a constraint decline, is item 4's. |
| 6 | FR-258 trace timeline | MET | `TraceTimeline.test.ts:27,38`: step id, label, consumed, produced, elapsed, matched row key, bundle hash, version reference. |
| 7 | FR-25 waterfall one click from a traced quote; route reachable | MET | Route `/rating/:slug/v/:version/sandbox` matches `03` §5.3 (`:1407`). `RatingVersionView.vue` links to it; `RatingVersionView.test.ts:53` asserts the href (red by its cause, then green). Outcome, ladder and trace share one page (`QuoteSandboxView.test.ts:114`). The router suite passes (4 files, 23 tests: guard, index, reachability, routeGraph). There is no sandbox-specific router test; reachability rests on the generic `reachability.test.ts` plus the link test, which I judge sufficient. |
| 8 | R6.1 FR-249 per-peril components absent, with a test | MET, view limb CARRIED | No source reads a rung's `components`. `LadderWaterfall.test.ts:60` gives a rung `components` and asserts the chart option has no `frequency`, `severity` or `components`; `QuoteOutcome.test.ts:33` and `QuoteSandboxView.test.ts:158` assert the "not available" element naming `OQ-1460`. The view limb is carried under `OQ-1460` (owner WK-1178). |
| 9 | R6.2 FD-1335 hold | MET | `SL-1367` merged (`13a02bba`, #1282); `13a02bba` is an ancestor of the head. |
| 10 | CLAUDE.md §3: `<script setup lang="ts">` only, no hand-written API type | MET | Every `<script` in the sandbox files and the view is `setup lang="ts"`. `score.ts` takes `ScoringResult`, `LadderRung`, `Trace`, `TraceStep` and `QuoteContext` from `generated/schema` and `schema.requests`. `QuoteFormSubmit`, `BuiltInputs` and `RungChange` are view-models, not API shapes. |
| 11 | OQ-551 no hard-coded currency | MET | A grep of the sandbox sources for GBP, £, USD and EUR finds none. The amount formatter has no symbol, and the chart axis and caption say "currency not configured (OQ-551)"; `ladder.test.ts:32` asserts it. Carried under `OQ-551` (open). |
| 12 | Decimal Rating Inputs as JSON numbers | CARRIED | Re-verified at `origin/main` `249670fe`: `score.py:353` is the `isinstance(value, (int, float, Decimal))` check (a string is refused); `scoring.py:109` is `inputs: dict[str, object]`; `score.py:955-962` builds the context from the raw value. The finding is on main as `FD-1671` (`docs/findings/register.md:360`, LOW, ruled at "2026-10-12 03:04:43 BST"), and this ledger cites `FD-1671`, with no live working id left outside quoted lines. The JSON-number path is the platform's contract (the lead's "2026-10-12 03:04:15 BST"); no exact path exists beyond about 15 significant digits. Not this slice's to fix. |
| 13 | No money as float in the display path | MET with a note | `ladder.ts` subtracts integer minor units; `formatAmount` is `minor / 100` through `toLocaleString`, for display only. `formatMinor` needs a currency, so it could not be reused without picking one (item 11). |
| 14 | Red-first | MET, disclosed | `sl1548-red.out`: 8 of 8 files failed at `64fe67fe` plus the eight test files. Seven fail on `Failed to resolve import` of the module under test (I confirmed all seven names), so those reds prove only that the tests need the implementation; `RatingVersionView.test.ts` fails by cause (`Unable to find role="link" and name "Open the quote sandbox"`, 1 failed and 6 passed). The ledger's Build log discloses this. |
| 15 | Green, lint, type-check | MET | `sl1548-green1.out`: 8 files, 45 tests passed; `sl1548-lint.out` and `sl1548-types.out` rc 0; the gate's `fe_test` is 116 files and 730 tests passed. |
| 16 | The gate at `c0d39234` | CARRIED to the minted-head CI | rc 0: ruff, mypy, import-linter, req-coverage, contracts, frontend install, generate, lint, type-check, test, build. pytest rc 1: 13 failed, 5708 passed, 6 skipped. I matched the 13 `FAILED` names in `pytest.log` to the ledger's list and read each failure block: every block ends in `check 31: gap in the full allocation between 1646 and 9869` (`test_audit_docs_w37_11_ceiling`'s message is truncated; its cause is at `pytest.log:4617`). `audit_docs.log` ends "FAILED (1): check 31". The cause is the unminted working id, removed by the mint. No pytest run of those modules exists on the minted tree; the merge-head CI on #1291 is the carried check. |
| 17 | Write set | MET | `git diff --stat origin/main...129fae7c`: 23 paths. They are the sandbox components and tests, `score.ts`, the router entry, `RatingVersionView.vue` and its test, `QuoteSandboxView.vue` and its test, this ledger, the `PL-1546` status line (`draft → active`), the `SL-1548` roadmap row and `docs/INDEX.md`. That is the inferred set the ledger records and the lead accepted. No generated, contract or backend path. |

**Re-verified at `129fae7c`.**
- **The merge of main.** `git diff --name-only c0d39234 129fae7c -- frontend packages` is empty. `git diff origin/main...129fae7c` lists no `backend`, `packages` or `docs/contracts` path, so the only backend difference from `c0d39234` is main's own (`073bf5b4`, SL-1527). The code audited at `a73444fd` and `c0d39234` is the code at the final head.
- **Mint.** Ledger `id: LG-1673`, `status: closed`; `relates` carries `FD-1671`. The roadmap `SL-1548` row is `closed` and cites `LG-1673`. The PRs line names #1291, "merge commit: not yet merged". The `MERGE-ACK` line reads "not yet given", correctly, since the lead gives it.
- **Ledger SHAs.** The commit SHAs in this ledger (`1205dc6a`, `13a02bba`, `64fe67fe`, `b2ec0653`, `c0d39234`) each exit 0 from `git merge-base --is-ancestor <sha> 129fae7c`.
- **audit-docs.** Run once, under the `gate-2` flock with `gate-1` free, `python3 scripts/audit-docs.py` on the worktree at `129fae7c`: rc 0, "All checks passed" (check 36's legacy-form lines are the standing notes).
- **CI on #1291** (head `129fae7c`): `no-session-links` SUCCESS; `specification audit`, `check` and `ruff · mypy · import-linter · pytest` were IN_PROGRESS at 04:55 BST. CARRIED until green.
- **House rules.** No barred word in added hunks (the text says "by delegation"); every commit carries the Co-Authored-By line.

**Observations, none a gap.**
1. `LG-1673` and the `SL-1548` row are marked `closed` in the mint commit, before this audit, as `LG-1647` and `LG-1643` were. Acceptance is verified here, so `closed` stands if the lead's verdict below accepts the carries.
2. The roadmap row's closing line says "Closed 2026-10-12 on a clean slice audit"; that holds only through this audit.

**Requirements without evidence.** None. The set was taken from `PL-1546` row 2, not from recollection: FR-213, FR-247, FR-248, FR-251, FR-252, FR-255, FR-256, FR-258, FR-25 and NFR-463 are evidenced above. FR-249's view limb is **deferred with an owner**: `OQ-1460`, owner WK-1178, per R6.1. `scripts/scope-audit.py` was not run.

**Findings and proposed owners.** None new. `FD-1671` (decimal Rating Inputs cross `/score` as float, LOW) is already on main; its owner and disposition are the lead's.

**Proposed verdict: DELIVERED.** FR-249's view limb stays carried under `OQ-1460`; decimal-input exactness stays carried under `FD-1671`; currency stays carried under `OQ-551`. Carried check: the merge-head CI on #1291, including the 13 audit-on-tree modules that failed only on the pre-mint check 31.

Lead verdict (team-lead, from-lead 2026-10-12 04:55:58 BST): DELIVERED; Audit adopted; carried: merge-head CI, FR-249 view limb (OQ-1460), decimal-input exactness (FD-1671), currency (OQ-551); no new FD; S5 merges second and re-gates its quote-form tests (drift rule, 02:53:52).

### Build log

- 2026-10-12 — Build commit `1205dc6a`: T1–T4 and their tests, written while a functional window barred test runs; no test, lint or type-check had run at that head.
- 2026-10-12 04:04 BST — Full gate at `c0d39234` ended: every code and frontend stage 0; pytest and audit-docs red on check 31 only (Gate section).
- 2026-10-12 03:11–03:13 BST — **Red-first proof, run after the lead's CLOSE of 03:11:05**, each through `run-small.sh`, `pnpm exec vitest run`:
  - **RED**, at `64fe67fe` (scratch detached worktree) plus only the eight test files (six under `components/sandbox/__tests__/`, `QuoteSandboxView.test.ts`, `RatingVersionView.test.ts`): rc 1, 8 files failed, `/home/puzhenhao1989/gi-pricing-plan.local/evidence/sl1548-red.out`. Seven files are red by `Failed to resolve import` of the module under test (`quoteForm`, `ladder`, `LadderWaterfall.vue`, `QuoteOutcome.vue`, `QuoteError.vue`, `TraceTimeline.vue`, `QuoteSandboxView.vue`): unavoidable, the modules do not exist there, so those reds prove only that the tests need the implementation. The eighth, `RatingVersionView.test.ts`, is red by its intended cause: `Unable to find role="link" and name "Open the quote sandbox"` (its six older tests pass).
  - **GREEN**, at the slice head before this entry (`b2ec0653`): the same files, rc 0, 8 files and 45 tests passed, `/home/puzhenhao1989/gi-pricing-plan.local/evidence/sl1548-green1.out`.
  - `pnpm lint` rc 0 (`/home/puzhenhao1989/gi-pricing-plan.local/evidence/sl1548-lint.out`); `pnpm type-check` rc 0 (`/home/puzhenhao1989/gi-pricing-plan.local/evidence/sl1548-types.out`); `vitest run src/router` rc 0, 23 tests (`/home/puzhenhao1989/gi-pricing-plan.local/evidence/sl1548-router.out`, covers route reachability with the new route).
  - No test here is labelled a guard: every new test was shown red, seven by absence of its module.
- 2026-10-12 — Lead's four corrections: red-first to be proven after CLOSE (new tests against `64fe67fe` plus the test files only, then green; both runs with out-file paths recorded here, a test not shown red labelled a guard); no GBP (done, below); decimal contract cited, ruled and carried under FD-1671; write set recorded as inferred. Currency change made in the next commit.
- 2026-10-12 — Activation commit: `SL-1548` `draft → active` with a dated line citing the 02:53:52 BST GO; `PL-1546` `draft → active` (status line only); this ledger opened under working id 9869.

## PRs

- #1291 — `feat(frontend): quote sandbox — form from the input contract, ladder waterfall, trace — SL-1548 (WK-675 S6)`; merge commit: not yet merged.

## Addendum 2026-10-26 — exec-tue27a — discharges PL-1546 item 5 (the accessibility-tester report for this slice)

Appended to a closed ledger by the lead's ruling (to-lead "2026-10-26 13:56:26 GMT", DP-T27-3 (a); the report itself per "2026-10-26 15:37:48 GMT"); the status of this ledger is unchanged. The report below is the file `scratch/a11y-nfr463/report-2026-10-26.md` copied verbatim; it is a static read at tree `7ed5c398` (no browser, no screen reader), 17 FAIL (0 critical, 1 serious, 4 moderate, 12 low), 31 vitest files and 221 tests passed.

# NFR-463 accessibility verification — WK-675 views (2026-10-26)

Tree: `.claude/worktrees/tools-main` @ `7ed5c398333aa24432bd9917bd204f7b540fb39c` (read-only; no edits).
Standard, `docs/specs/00-overview.md:586` NFR-463: WCAG 2.2 AA; every chart has an accessible tabular
equivalent; the equivalent reads its cells from the chart's own rows (`ChartFigure` column descriptors, RL-1307).

Method and limits
- Static code review of the Vue sources and the installed `@vue-flow/core` dist. No browser, no screen reader, no axe
  (axe/Playwright is not in `frontend/package.json`). Everything needing rendering is `NOT VERIFIABLE STATICALLY`.
- Tests run (read-only): `pnpm --dir <tree>/frontend exec vitest run` over dag, rating, sandbox, dislocation component
  dirs plus the 5 view tests. Result: 31 files, 221 tests passed, no type errors, rc=0. The full gate (lint, type-check,
  build, generate:api) was not run. Do not read this as a gate pass.
- Contrast is computed from Tailwind v4 default palette hexes. Key values:
  slate-500 #64748b on white 4.76:1, on slate-50 ~4.55:1; sky-700 #0369a1 on white ~5.9:1; amber-700 on white ~5.0:1;
  red-700 on red-50 ~5.9:1; **slate-300 #cbd5e1 on white ~1.6:1**. Text pairs all pass 4.5:1. See F2 for the border.
- Severity scale: critical, serious, moderate, low.
- Views: 7 routes exist and are routed (`router/index.ts`: `/rating-versions/:id`, `/rating`, design, dislocation,
  tests, sandbox, tables). None of the WK-675 views is missing. No component-level axe-style tests exist; the only a11y
  assertions are cited per section.

## Cross-cutting findings (cited once, referenced by view)

- F1 FAIL (WCAG 3.3.1, serious): `components/rating/DecimalCellInput.vue:31-34,50-61` a syntactically bad value
  (`syntaxError`) is signalled only by `border-red-600` and `aria-invalid="true"`. No text message or `aria-describedby`
  is rendered (the message span appears only for the server's `invalid`). The error is not identified in text, and
  colour is the only visible cue (also 1.4.1). Used by the rate table grid. Test coverage asserts only `aria-invalid`
  (`DecimalCellInput.test.ts:19,33,39`).
- F2 FAIL (WCAG 1.4.11, moderate): every text input, select and textarea in scope has a `border-slate-300` boundary
  (~1.6:1 on white; 3:1 required) and no other visible boundary. Examples: `DagDesigner.vue:295`, `RateTableDiffPanel.vue:140,160`,
  `DecimalCellInput.vue:54`, `BulkOperationDialog.vue:81,107,116`, `QuoteForm.vue:74,95,116,136`, `RateTableEditorView.vue:310`,
  `DislocationView.vue:114`, `RegressionSuiteView.vue:129`, `RatingVersionListView.vue:126`. Buttons are exempt (text label).
- F3 FAIL (WCAG 4.1.3, moderate): status text mounted together with its live region by `v-if`. Screen readers generally miss
  the content of a live region inserted already populated. `DislocationView.vue` and `RegressionSuiteView.vue` do it
  correctly with persistent regions; these do not: `RateTableDiffPanel.vue:173-186` (`aria-live` on `v-if` paragraphs),
  `RateTableEditorView.vue:250-256` ("Created …"), `BulkOperationDialog.vue:128`, `RateTableImportExport.vue:139`.
  (`role="alert"` siblings are fine.)
- F4 FAIL (WCAG 1.3.1 / 3.3.2, low): `components/FormField.vue:35-40` help text is a bare `<p>` with no `id` and no
  `aria-describedby` on the control, so hints (field ranges, "what_if is a test price") are not programmatically associated.
- F5 FAIL (WCAG 1.4.1, low): breadcrumb links are `hover:underline` only, in the same colour as the adjacent plain text
  (`text-slate-500`): `QuoteSandboxView.vue:117`, `DislocationView.vue:88`, `RegressionSuiteView.vue:80`,
  `RateTableEditorView.vue:224`, `RatingDesignView.vue:103`. A link is told apart from text by hover only.
- F6 FAIL (WCAG 2.1.1, low): horizontally scrolling regions with no `tabindex`, so a keyboard-only user may not be able to
  scroll them (browser-dependent: recent Chromium focuses scrollers, Firefox/Safari behaviour differs):
  `RateTableEditorView.vue:271`, `RateTableDiffPanel.vue:204`, `RegressionSuiteView.vue:244` (`<pre>`).
- Focus indicator: no `outline-none` / `outline: none` anywhere under `frontend/src` (grep), so the UA default ring
  applies; custom `focus-visible` rings exist on the listbox, step inspector fields and list links. PASS (2.4.7).
  Focus Not Obscured (2.4.11) with sticky chrome: NOT VERIFIABLE STATICALLY.
- Charts: all 6 chart sites in scope (ladder waterfall, change histogram, segment grid x2, attribution waterfall)
  go through `ChartFigure`, which always renders the table in the DOM with column descriptors. The `ECharts` canvases
  carry no `aria` option or role (advisory only; the adjacent table is the equivalent). PASS for NFR-463's equivalence limb.

## 1. DAG designer (`components/dag/DagDesigner.vue`, hosted by `views/RatingDesignView.vue`)

- PASS (2.1.1): a keyboard path to every node exists without the canvas. `NodeNavigator.vue:157-183` is a listbox with a
  roving `aria-activedescendant`, arrows, Home/End, typeahead, Enter to select, Delete to remove. Mounts are included.
  Tests: `NodeNavigator.test.ts:24,34,43,50,57`.
- PASS (2.4.7): listbox and active option have visible focus/active styling (`NodeNavigator.vue:163,175`).
- PASS (3.3.4 / 2.4.3): Delete opens an `alertdialog` (`NodeNavigator.vue:184-215`), focus moves to Cancel, Esc and Cancel
  return focus to the list (`:96-107`). It is not modal and has no trap; acceptable as it is inline.
- PASS (4.1.3): removal is announced through a persistent `role="status"` (`NodeNavigator.vue:151`); the active option moves
  to the neighbour. Test: `NodeNavigator.test.ts:74`. Issue count is a persistent `aria-live` (`DagDesigner.vue:241-246`;
  `DagDesignerValidation.test.ts:57`); `GraphIssues.vue:397` is a persistent `role="status"`.
- PASS (1.4.1): non-colour channels exist. Invalid nodes have a 2px border plus a "⚠ n" count and message list
  (`StepNode.vue:241,268-280`). Diff marks are text badges, "added"/"changed" (`StepNode.vue:254`). Conditional mounts have a
  dashed border plus a text badge (`MountNode.vue:337,361`); conditional edges are dashed. Selected option has a border
  and bold (`NodeNavigator.test.ts:85`).
- PASS (1.4.3): text pairs used all >= 4.5:1 (slate-500 on white/slate-50, red-800 on red-50, amber-900).
- PASS (1.3.1): inspector controls labelled; `aria-invalid`/`aria-describedby` tested (`StepInspector.test.ts:171-173`).
- FAIL (WCAG 2.4.3 / 3.3.2, low-moderate): `DagDesigner.vue:226-232` `<VueFlow>` leaves `nodesFocusable` at its default
  `true` (`@vue-flow/core` dist: `nodesFocusable: true`, nodes rendered with `tabIndex=0`, `role="group"`,
  `aria-describedby=vue-flow__node-desc-…`, line 9587-9590). Every node is an extra tab stop that duplicates the listbox,
  nests a second `role="group"` (`StepNode.vue:239`, `MountNode.vue:333`), and its description is Vue Flow's default
  "select / move node with arrow keys" instruction, which is false here (`elements-selectable`, `nodes-draggable` are false).
  Static evidence only; confirm in a browser. Fix direction: `:nodes-focusable="false"` or a 3.3.2-accurate description.
- FAIL (WCAG 3.3.1 / F1, F2, F4 apply): see cross-cutting. Add-step select border `DagDesigner.vue:295` (F2).
- NOT VERIFIABLE STATICALLY: edge exposure in the accessibility tree (Vue Flow renders focusable edges with default
  "Edge from x to y" labels, possibly via `ARIA_EDGE_DESC`); canvas zoom/pan operability (2.5.7 dragging alternative: the
  navigator plus `fitView` on select are the alternative); reflow at 320px (`lg:grid-cols-[1fr_22rem]` stacks below lg;
  fixed `h-[28rem]` canvas).

## 2. Rate table editor (`views/RateTableEditorView.vue`, `components/rating/RateTableGrid.vue`, `BulkOperationDialog.vue`, `RateTableImportExport.vue`)

- PASS (1.3.1): grid is a real `<table>` with `scope="col"` heads and `scope="row"` key cells (`RateTableGrid.vue:384-406`);
  each cell input has an accessible name "value for key a, key b" (`:412`).
- PASS (3.3.1, server errors): a server cell error is rendered as text and referenced by `aria-describedby`
  (`DecimalCellInput.vue:51,57-61`; `RateTableEditorView.test.ts:172-176`).
- FAIL (WCAG 3.3.1, serious): F1, client-side syntax error has no text.
- FAIL (WCAG 1.4.11, moderate): F2. Cell inputs, change note (`RateTableEditorView.vue:310`), bulk and import controls.
- FAIL (WCAG 4.1.3, moderate): F3 on "Created …" (`:250`), bulk (`BulkOperationDialog.vue:128`), import (`:139`).
- FAIL (WCAG 4.1.3, moderate): `RateTableEditorView.vue:323-363` "Review changes" mounts the "N cells changed / Confirm" section
  with no focus move, no live region and no status. A keyboard or screen-reader user presses the button and nothing is
  announced. The section appears after the button in DOM order, so it is reachable, but unannounced.
- FAIL (WCAG 4.1.2, low): `BulkOperationDialog.vue:62-64` `role="dialog"` on an always-visible inline `<section>`: it
  is not modal, not opened or closed, and has no focus management. The role over-promises; use a plain labelled region.
- FAIL (WCAG 4.1.2 / 3.3.2, low): `RateTableEditorView.vue:313-320` "Review changes" is natively `disabled` until a note and an
  edit exist, with no text explaining why; focusable-disabled or a hint would help. (Contrast the design view, which uses
  `aria-disabled` and `aria-describedby` to a problems list, `RatingDesignView.vue:164-165`.)
- FAIL (WCAG 2.1.1, low): F6 at `:271`. FAIL (WCAG 1.4.1, low): F5 at `:224`.
- PASS (1.4.3): sky-700/white buttons ~5.9:1; red-800 on red-50; emerald-800 on emerald-50.
- NOT VERIFIABLE STATICALLY: 2.5.8 target size (inputs `w-28 py-1` ~ 30px high, passes by class arithmetic); text spacing
  1.4.12; reflow of a wide grid (container scrolls, which is allowed for tables).

## 3. Rate table diff panel (`components/rating/RateTableDiffPanel.vue`, `diffShading.ts`)

- PASS (1.4.1, the non-colour channel): shading follows size, and direction is written as the sign and `%` in the cell
  (`diffShading.ts:28-30`, `RateTableDiffPanel.vue:286-288`), plus `data-direction`; the "Change" column carries the text
  kind. The header comment states the intent ("colour is never the only signal"). Tests: `RateTableDiffPanel.test.ts`.
- PASS (1.4.3): body text (slate-900 default) on amber-50..300 and sky-50..300 all >= 10:1.
- PASS (1.3.1): `<thead>` with `scope="col"`; first key cell `scope="row"` + `role="rowheader"`; remaining key cells are
  plain `<th>` without scope (acceptable; no mis-association because only the first is the row header).
- PASS (3.3.1): failure is `role="alert"` (`:187-193`).
- FAIL (WCAG 4.1.3, moderate): F3 at `:173-186`. "Loading…", "Building the comparison…" and the stalled message are
  `aria-live` paragraphs created by `v-if`.
- FAIL (WCAG 4.1.3, low): results (the table, "No cells differ.") appear on "Show changes" with no announcement and no focus
  move; page changes (Next/Previous) replace the rows silently, and the focused pager button may become disabled
  (focus loss: `:304,312` `disabled` toggled on the clicked button, so focus drops to `body` after the last page).
- FAIL (WCAG 2.4.3, low): same pager lines: activating "Next page" on the final page disables the focused control.
- FAIL (WCAG 1.4.11, moderate): F2 at `:140,160`. FAIL (WCAG 2.1.1, low): F6 at `:204`.
- PASS: `id="diff-against"` is also used in `DiffOverlay.vue:500`, but the two are on different routes (design vs tables),
  never on one page; no duplicate-id (4.1.1 is obsolete in 2.2 anyway).
- NOT VERIFIABLE STATICALLY: 1.4.10 reflow of the 9-column table (container scrolls); actual rendered contrast of shade steps.

## 4. Quote sandbox and compare (`views/QuoteSandboxView.vue`, `components/sandbox/*`)

- PASS (1.3.1 / 3.3.2): form fields labelled by `FormField` `for`/`id`; `novalidate` form with typed problems per field
  (`QuoteForm.vue:179-266`); problem text is `role="alert"` and referenced by `aria-describedby`, `aria-invalid` set.
- PASS (1.3.1): comparison tables use `<caption>`, `scope="col"`/`scope="row"` (`QuoteComparison.vue:35-117`). Tests:
  `QuoteComparison.test.ts`.
- PASS (1.4.1): outcome "declined" is stated in words in the heading and in a text box "Declined — the ladder below…"; the amber
  colour is additional (`QuoteOutcome.vue:301-312`). Error kind is a heading text plus code (`QuoteError.vue:395-398`).
  Errors are `role="alert"` (`QuoteError.vue:391`).
- PASS (NFR-463, charts): the premium ladder waterfall goes through `ChartFigure` with Rung / Value / Change / Operation columns;
  increase vs decrease are in the Change column and the signed figure, not only bar colour (`LadderWaterfall.vue:27-36`).
  Legend colours rely on ECharts defaults for Total/Increase/Decrease: legend-only colour is covered by the table.
- PASS (4.1.3): loading is a persistent `role="status"` (`QuoteSandboxView.vue:125-131`).
- FAIL (WCAG 4.1.3, moderate): `QuoteSandboxView.vue:208-226` the score result (outcome, ladder, trace, comparison) replaces
  a hint paragraph with no live region and no focus move. The submit button text changes to "Scoring…", but completion is
  never announced, and the result sits in a second column after the form in DOM order.
- FAIL (WCAG 1.3.1, low): F4: field hints (`QuoteForm.vue`, `FormField.vue:35`).
- FAIL (WCAG 1.4.11, moderate): F2 at `QuoteForm.vue:74,95,116,136` and `QuoteSandboxView.vue:174`.
- FAIL (WCAG 3.3.1, low): `QuoteForm.vue:99-141` only the free-text/date input branch gets `aria-invalid`/`aria-describedby`;
  the `<p role="alert">` problem is rendered after every branch (`:259-266`) but bool and enum controls are not linked to it.
  Whether `buildInputs` can raise a problem for an enum (a required choice left at "Choose…") is not established
  statically; if it can, the control is unlinked.
- FAIL (WCAG 1.4.1, low): F5 at `:117`.
- NOT VERIFIABLE STATICALLY: trace timeline reading order and `<dl>` semantics (static markup looks sound:
  `TraceTimeline.vue` ol/dl); canvas rendering of the waterfall at 200% zoom.

## 5. Dislocation views (`views/DislocationView.vue`, `components/dislocation/*`)

- PASS (4.1.3): persistent `role="status"` and `role="alert"` regions with changing content, with a comment saying why
  (`DislocationView.vue:99-121`). This is the pattern F3 asks for elsewhere.
- PASS (NFR-463): all 4 charts (`ChangeHistogram`, `SegmentGrid` x2, `AttributionWaterfall`) use `ChartFigure` with
  descriptor columns. The attribution waterfall encodes direction by blue `#1d4ed8` vs amber `#b45309` plus the "+"/"−" bar
  labels (`AttributionWaterfall.vue:72-81`) and a "Direction" Increase/Decrease column. This is a non-colour channel. Test:
  `dislocation.test.ts`.
- PASS (4.1.2): the movers disclosure is a `<button>` with `aria-expanded` and `aria-controls` (`LargestMovers.vue:119-121`,
  `dislocation.test.ts:171`); the button text names the quote.
- PASS (1.4.3): slate-500 on slate-50 (`LargestMovers` expanded row) ~4.55:1, just over.
- FAIL (WCAG 1.4.11, moderate): F2 at `DislocationView.vue:114`.
- FAIL (WCAG 1.4.1, low): F5 at `:88`.
- NOT VERIFIABLE STATICALLY: tooltip-only information on the charts (the ECharts tooltips are mouse-driven; the tables carry
  every value, so no information is lost).

## 6. Rating version list (`views/RatingVersionListView.vue`, `RatingVersionView.vue`)

- PASS (1.3.1): one `<h2>` and one captioned table per slug, `scope` on every head and the row header (`:` table block).
- PASS (2.5.3): link `aria-label`s begin with the visible text ("Design x@1" for "Design"), so label-in-name holds.
- PASS (1.4.1): "Live in" environments are text chips ("none"/"unavailable" in words); status is a word.
- PASS (2.4.7): `focus-visible` outline on filter and every link (`:126,217-246`).
- PASS (2.5.8): links are `inline-block py-1` ~ 28px high; `space-x-2` gives spacing.
- PASS (4.1.3, loading and error): persistent-less but `role="status"`/`role="alert"` are inserted populated; `role` regions
  are acceptable for alert; the loading `role="status"` is subject to F3-style caution (low).
- FAIL (WCAG 4.1.3, low): changing the status filter (`:122-136`) re-renders the groups with no result-count announcement.
- FAIL (WCAG 1.4.11, moderate): F2 at `:126`.
- PASS (1.4.3): slate-500 header and label text 4.76:1; emerald-800 on emerald-100.

## 7. Regression suite view (`views/RegressionSuiteView.vue`)

- PASS (4.1.3): persistent status and alert regions (`:85-108`), with the explanatory comment.
- PASS (1.3.1): both result tables have `aria-label` and `scope="col"` heads. Pass/fail is a word, never colour alone
  ("unminimised" text accompanies amber).
- PASS (1.3.1): the run `<select>` is labelled; the evidence run is marked in words, " · approval evidence" (`:36-38`).
- FAIL (WCAG 4.1.2, low): `RegressionSuiteView.vue:243-244` `aria-label` on a bare `<pre>`. A `<pre>` has the generic role,
  which does not allow naming (ARIA 1.2); the name is ignored by AT. Use a labelled wrapper or `role="group"`.
- FAIL (WCAG 2.1.1, low): F6 at `:244`.
- FAIL (WCAG 1.3.1, low): table row headers: `<td>` first column (`:173,215`) is the row's name but not a `<th scope="row">`,
  unlike the other tables in scope.
- FAIL (WCAG 1.4.11, moderate): F2 at `:129`. FAIL (WCAG 1.4.1, low): F5 at `:80`.
- NOT VERIFIABLE STATICALLY: re-announcement of the table when the run `<select>` changes the route query (the whole
  region reloads; focus stays on the select; the results change with no live announcement, same shape as F-list change).

## Summary

Distinct FAIL defects: 17 (cross-cutting items F1-F6 counted once, wherever they recur). No critical.

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

NFR-463's chart limb (tabular equivalent from the chart's own rows) holds at all 5 chart sites in scope. The failures are
WCAG 2.2 AA gaps in forms, status messages and non-text contrast.

Evidence gaps (gaps, not passes): no browser, screen reader, axe or Playwright; the 221 passing vitest tests assert
`aria-invalid`, `aria-live`, `aria-expanded` and listbox keyboard behaviour, but none asserts live-region announcement after
a result, focus order, or contrast. The full frontend gate (lint, type-check, build) was not run.
