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

(written by an auditor seat; not by the executor)

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
