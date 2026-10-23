---
id: RS-1868
family: research
kind: audit
title: SL-1551 (WK-675) Slice 8 slice audit — the typed movers row and the dislocation views (LG-1867, PL-1833)
status: draft
created: 2026-10-23  # drafted 2026-10-22 under working id 8191; minted 2026-10-23 as RS-1868
owner: auditor
tree: c1fb3cd35737d08a9a36f0a1ba1f17543eed2ed6
phase: P2
work: WK-675
corrected_by: []
relates: [SL-1551, LG-1867, PL-1833, FR-263, FR-264, FR-265, FR-266, NFR-463]
---

# RS-1868 — SL-1551 slice audit

*(Minted 2026-10-23 as RS-1868 from working id 8191; the ledger cites below (LG-8146 as written) are re-pointed to LG-1867, its minted id. Working id 8191, written by `aud-1551` (auditor, sonnet, effort medium), 2026-10-22, from `brief-aud-1551-2026-10-22.md` (lead 26). Check 31 on this id is expected until the mint. Ledger cited by its working id `LG-1867`.)*

## Question

Does SL-1551 meet `PL-1833`'s Acceptance 1–9 and deliver FR-263..266 with the movers row typed once, exact maths and generated-only frontend types — and is the evidence reachable?

## Method

Range `origin/main...origin/sl-1551-wk675-s8`: main `71e481fa`, branch head `569fd8b848d4dc3e4d64774e4bf3b2b3203e5604`, tree `c1fb3cd35737d08a9a36f0a1ba1f17543eed2ed6`. Read only via `git -C /home/puzhenhao1989/gi-pricing-plan show/diff/grep`; no test, gate, DB or docker run. Scope derived first from `PL-1833` (Tasks 1–2 and Acceptance 1–9), then evidenced. Acceptance 2–6 re-run as the plan's own commands on the branch.

## Findings

### Verdict proposal: NOT-CLEAN — 3 blocking items, none a product defect; the code, maths and contract read correct

Verdict is the lead's.

| Acc. | Result | Evidence |
|---|---|---|
| 1 docs checks | delivered on LG (not re-run here) | LG-1867 build log: `audit-docs` rc 1 only check 31 on 8146, `doc-index --check` rc 0, `register-lint` rc 0 at e9d4cc64 |
| 2 route typed | **MET** | `generated.json` `/movers` 200 `items` = `{'$ref': '#/components/schemas/DislocationMover'}` |
| 3 one class | **MET** | one `class DislocationMover` (`dislocation.py:270`); `additionalProperties` False; only `columns` is open; test `test_the_mover_schema_has_one_open_property_and_it_is_columns` |
| 4 no hand-written shape | **MET** statically | one alias `DislocationMover = components["schemas"]["DislocationMover"]`; `generate-contracts --check` rc 0 recorded in LG (not re-run); `AttributionWaterfall.vue` `interface Step` is a local view model, not an API shape |
| 5 order gate | **MET**; broken input present but **LG says it was not run** | A=`4496daeb`, B=`b594fa50`, ancestor rc 0 (re-run); `scratch/sl-1551/accept5.log`: positive rc 0, broken rc 1 — contradicts LG-1867 Task 2 "was not run" (B2 below) |
| 6 FR tests | **MET** | FR-263/264/265/266 each in a frontend test file (re-run per id); route test `@pytest.mark.req("FR-263")` |
| 7 rounding/edge | **MET on LG claims** | helper mutated to truncation: 5 red; half-even: 4 red; edge-of-threshold test named; §4.6 dated line present |
| 8 accessible tables + a11y report | **MET** (static only) | report quoted in LG; 3 fixes, 2 low open, contrast/focus/reflow owed. The plan does not require a browser run |
| 9 gate green | **OWED** | no gate run yet (LG: "no gate has been run on this slice"; gate script written, not launched) |

### Blocking items

- **B1 — GREEN set not derived by import closure (seat brief item 29).** LG-1867 records frontend runs (127 files, 813 tests rc 0) and one pytest file, but not the changed-module list, the closure commands or the derived file list. `scratch/sl-1551/green-task1.log` ends at "waiting for /tmp/slots/small-test" and has no result. The full gate is decisive (re-merge of `71e481fa` brought main code), but the closure must be quoted before the MERGE-ACK. Remedy: derive and quote it in the LG.
- **B2 — LG-1867 contradicts its own evidence on Acceptance 5.** Task 2 says the broken-input run "was not run"; `accept5.log` (head 569fd8b8) shows it was (rc 1 vs rc 0), but that log lives under `scratch/`, not in the record. Remedy: correct the LG line and quote the log's seven lines in the LG.
- **B3 — Acceptance 9, the two-half gate, is owed** (the decisive green; MERGE-ACK to quote its "Test Files N passed"). Not a defect; listed because the slice is not PR-ready until it passes.

### Owed (not blocking the audit)

- Closing act (maintainer, "2026-10-21 15:56:56 BST"): correct the stale `docs/roadmap.md` SL-1551 paragraph in the closing commit — the branch's roadmap diff has only the activation line.
- Mint: audit-docs check 31/32 on 8146 (and this id) clear at the mint turn; re-run `doc-index.py` and `doc-index.py --check` after it.
- LG and SL `closed` after a clean audit and the lead's merge.
- Browser/screen-reader a11y items (focus ring, contrast, 200 % reflow): owed, not required by the plan.

### Maths and money (CLAUDE.md §7)

`mover_change_pct` (`pricing_core/rating/analysis.py`): `scaled = change_minor × 100 × 10⁶`; ceiling division of `|scaled|` by `baseline_minor` (positive: movers are banded), sign restored, `Decimal(...).scaleb(-6)` — exact integer arithmetic, rounded once, away from zero, as 03 §4.6 and DP-S8-2 (a) state. No float anywhere on the path. `DislocationMover.change_pct` is `PositionalDecimalStr`, minor fields `MoneyMinor`; a float `change_pct` and a float minor are refused by test. `columns` is `dict[str, JsonScalar]` (floats allowed there by the plan: a portfolio column is not money); `_json_value` stringifies `Decimal`, ISO-formats dates, and refuses any other non-scalar with a 422 rather than widening the type. Frontend shows `change_pct` as the string sent; `format.ts` `toFixed` is on the existing run-level derived shares (display only), not on money.

### Red-first and commits

Task 1 (spec, model-schema, route, tests, contracts) is one commit `4496daeb`, so commit order shows no red-before-code; red-first rests on the LG's recorded collection failures (`ImportError`, rc 2) before code. The 2026-10-10 01:54:02 ruling accepted "red-first on parent commits"; this one-commit form does not give a parent to run. Lead's call whether the LG record suffices. The two mutation runs (truncation, half-even) are the stronger evidence.

### Frontend and contracts

Four components, `DislocationView`, route `rating-dislocation` (inserted whole, no entry edited), and a `RatingVersionView` link (FR-25 reachability, accepted flag) read generated types only. The §5.1 `/movers` row and §4.6 carry dated amendment tags. `SL-1260` shares the §5.1 table: the later merge re-merges and re-runs its checks.

## Not examined

No test, gate, DB or browser run by this seat; the DB route test (24 passed, LG) is taken from the LG's quoted run, not reproduced.
