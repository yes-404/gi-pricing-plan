# Phase record — 1b (Modelling Workbench)

Closed 2026-08-27. Written per the [`phase-close`](../../checklists/phase-close.md)
checklist, which follows the [`phase-review`](../../../../.claude/skills/phase-review/SKILL.md)
skill. The register is [`register.md`](register.md); this record is the roll-up.

## Scope reconciliation

The phase as filed: Modelling Workbench, four workstreams — W5 (modelling core), W6b
(modelling-workbench UI), W32 (the backend half the browser does not own), W7 (the
freMTPL2 demo seed, modelling half) — with the exit criterion `wf-01` end to end on
freMTPL2. The phase review (`docs/audit/plan-reviews.md`) re-cut the plan twice: W32 split
from W6b on 2026-08-22, and the Phase 1b exit demo's scope was settled at plan review 6 —
the core journey (dataset → factors → GLM + GBM fits → comparison → approval → rating
version), with bandings, Peril Structure and reconciliation recorded as Phase 2.

What the phase actually delivered: 374 requirements in scope at the close audit, 276
evidenced, 98 unevidenced with a verdict each; every workstream closed; the exit demo UAT
passed all seven checklist items. The `wf-01` journey is the first of the five journeys
driven end to end over HTTP.

## Finding roll-up

Every finding the phase carried has a resolution. A fixed finding is delivered; an accepted
one names the enforcement that stands as its evidence; a deferred one names its owner and
its strong reason.

| Finding id | Concerns | Verdict | Owner |
|---|---|---|---|
| F1 | `validate.py` "minor units" strings on a statistic | fixed — PR #280 | W6b |
| F2 | `GET /me/workspaces` and `POST /me/workspace` routes | discharged — `me.py:175`, `:210`, `record_switch` at `:263` | W6b-11 |
| F3 | demo postcondition check ran only in the exit demo | fixed — PR #280 (`backend/tests/test_demo_postconditions.py`) | W7-5 |
| F4 | `RatingVersionView` loading state untested | fixed — PR #280 (loading-state test; the 404 test landed in #273) | W7-5 |
| F5 | NFR-MODEL-14 marker missing | fixed — PR #280; `req-coverage.py` reports it evidenced | W7 |
| F6 | FR-DATA-57 (`unrun_layers`) | deferred — phase boundary; owner the Phase 2 validation-report successor | Phase 2 |
| F7 | FR-DATA-52 (exposure-ordered top-20) | deferred — the trigger has not fired; no consumer has asked | — |
| F8 | the full `03` rating surface | deferred — phase boundary | Phase 2 |
| F9 | `wf-01` §4 surfaces the demo does not seed (bandings, Peril Structure, reconciliation) | deferred — phase boundary (plan review 6 P1) | Phase 2 |
| F10 | the `listRules` client gap | discharged — `frontend/src/api/rules.ts:114` exports `listRules` with tests | W7 |
| F11 | FR-MODEL-63/98 (prediction) delivered-but-untested | discharged — markers exist in the prediction path | W6b-6b |
| F12 | the four frozen-plan items (#103, #87, #127, #131) | resolved — PR #280 records each as shipped by its PR | — |
| F13 | FR-OVR-22 route reachability | accepted — the Vitest reachability suite is the enforcement | — |
| F14 | FR-OVR-20 `_minor` suffix rule | fixed — PR #280; `req-coverage.py` reports it evidenced | — |
| F15 | FR-OVR-21 §5.3 cell is prose | accepted — the declared-prose affordance | — |
| F16 | FR-PLAT-55 browser PKCE | accepted — the Vitest auth suite is the enforcement | — |
| F17 | FR-PLAT-59 no IdP in prod | fixed — PR #280; `req-coverage.py` reports it evidenced | — |
| F18 | NFR-PLAT-4 compose stack < 5 min | accepted — measured 27 s (roadmap `:298`) | — |
| F19 | FR-OVR-9 pseudonymisation | accepted — ingestion enforces the refusal; the PII-guard gap is recorded in the roadmap | — |
| F20 | cross-cutting OVR without markers | accepted — conventions, ADRs and the audit's own checks | — |
| F21 | measured NFRs without markers | accepted — measured, not asserted | — |
| F22 | Phase 2/3/4 unevidenced requirements | deferred — phase boundary (CLAUDE.md §0); owners are the later-phase workstreams | Phase 2/3/4 |
| F23 | empty `client_id` at browser sign-in | fixed — PR #283 | — |
| F24 | localhost-only redirect origin | fixed — PR #283 | — |
| F25 | seed-wipe — the pytest suite truncates the shared DB | re-seeded; root cause documented in `backend/tests/conftest_db.py` and `.claude/skills/python-test` | — |

The carried findings (F6-F9, F22) are in the phase register and the global register
([`../../register.md`](../../register.md)). No finding lacks a resolution.

## Cross-cutting checks

- **Contract drift** — the contract guard (`backend/tests/test_contracts.py`) compares
  generated against hand-authored schemas; the docs audit's route reconciliation (check 24)
  holds `00` §5.6 canonical against each module's §5.3. Green at the close.
- **Money discipline** — `MoneyMinor`/`DecimalStr` types plus `audit-docs.py` check 12
  (FR-OVR-7/20); the two `validate.py` strings that asserted minor units on a statistic
  were the last prose offenders and were fixed (F1).
- **Workflow coverage** — `wf-01` is the first journey driven end to end; check 21
  (journey citations) is green.
- **Dependency direction** — DEP-1 and the import-linter contract (3 contracts) green.
- **The full gate** — both halves green at each close: ruff, mypy, lint-imports, pytest
  (2044 passed at the final run), audit-docs, req-coverage, and the frontend
  lint/type-check/test/build.

## Retrospective

**What the shape got right.** The W32/W6b split gave the backend half an owner the browser
work could not take; the phase review ran at every close and re-cut the plan twice before
the re-cut became expensive. The demo-first exit (UAT over HTTP) found three real defects
(F23-F25) that no unit test reached, which is what an exit criterion is for. The
fix-before-close discipline (F1-F25 all resolved or accepted) kept the close from carrying
unresolved residue into Phase 2.

**What the phase got wrong.** The demo and the pytest suite share one database, so running
one wipes the other (F25) — the seed-wipe is documented, not solved; a separate test
database is Phase 2 work. The `wf-01` §4 surfaces the demo does not seed (bandings, Peril
Structure, reconciliation) are recorded as Phase 2 but were visible gaps throughout. The
summary-line and route-reconciliation checks (F14, T6.3) were written at the close, not at
the start — the audit instrument arrived after the drift it would have caught.

## Evidence

- Scope and verdicts: `register.md`, filed 2026-08-27 from the §13 evidence pass at
  `84e98f5` (374 requirements in scope, 276 evidenced, 98 with a verdict).
- UAT: [`../../exit-demo-uat.md`](../../exit-demo-uat.md) — all seven checklist items pass;
  seed-to-usable-state 90 s against NFR-PLAT-4's 300 s budget, measured on this tree.
- Gate: the per-command table was green on both halves at the final close run; pytest
  2044 passed / 2 skipped / 1 xfailed, reconciled against 2047 collected.
- The auditor's close-confirmation is in `register.md` (T9, 2026-08-27).

## Sign-off

Accepted by the maintainer on 2026-08-27. The record is tagged at the close.
