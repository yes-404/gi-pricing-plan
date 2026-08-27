# Phase 1b Pre-decision Implementation Plan — findings, dispositions, UAT-readiness

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reach the auditor's close-confirmation for Phase 1b. File every open finding with a disposition. Make the exit demo UAT-ready. End with the auditor confirming that the phase can go to the close decision.

**Architecture:** Two halves. Half 1 enumerates every open finding from the W7 close residue, plan review 6, `docs/audit/register.md`, and the deferred items, and gives each a disposition. Half 2 defines what UAT-ready requires for the exit demo and lands the fix-before-close findings. The sequence ends at the auditor's close-confirmation.

**Tech Stack:** Backend tests (`backend/tests/`), frontend tests (`frontend/src/views/__tests__/`), `packages/pricing-core/src/pricing_core/data/validate.py`, the audit registers (`docs/audit/`), `scripts/demo.py`.

**Spec:** Plan review 6 (P1: the core `wf-01` journey is the Phase 1b exit criterion) · the W7 close record (`docs/audit/closure-records.md`) · the W6b close record carry-forward · `docs/audit/register.md` and `docs/audit/phases/1b/register.md`.

**Highest ids:** No new requirement id is minted in this plan.

## Global Constraints

- The gate has two halves. Both must pass before a push (CLAUDE.md §11).
- Write prose in ASD-STE100. Code, identifiers and file paths stay unchanged.
- A filed plan stays frozen at its date. The plan file commits on the branch, never copied back.
- Requirement ids are permanent. Append, never renumber (CLAUDE.md §5).
- Every spec change runs `python3 scripts/audit-docs.py` before commit (CLAUDE.md §0).
- The phase register derives from `docs/roadmap.md` §6 and never repeats it (the audit structure convention).
- A finding gets one of three dispositions: fix before close, carry forward with an owner, or accept. Silence is not an option (CLAUDE.md §13).
- A disposition that is the maintainer's call is an explicit decision point, never a silent pick.

---

## The findings and their dispositions

The sources: the W7 close residue, plan review 6, the audit register, and the deferred items. Each row names the finding, its state, and the proposed disposition. A ruling on a decision point can move a disposition.

**The disposition default is FIX (maintainer, 2026-08-27).** A finding is deferred only with a very strong reason. The strong reasons are two: a phase boundary, where CLAUDE.md §0 forbids building a later phase's capability now, and a trigger that has not fired, where no consumer has asked for the work. Every deferral below states its reason. The expected outcome is every fixable finding fixed, deferrals near-zero.

| # | Finding | State | Proposed disposition |
|---|---|---|---|
| F1 | The `validate.py` "minor units" strings (auditor finding 6a) | `packages/pricing-core/src/pricing_core/data/validate.py:1007` and `:1084` assert minor units on a statistic | fix before close (MD1) |
| F2 | The `GET /api/v1/me/workspaces` and `POST /api/v1/me/workspace` routes | **RESOLVED** — `backend/src/app/api/me.py:175` and `:210`, `record_switch` called at `:263` | discharged |
| F3 | Batch C's change set has no test files. The demo postcondition check runs in the exit demo, not in pytest | the `_verify_journey_postconditions` check is exercised by the W7-5 demo run | fix before close, add a pytest test for the postcondition check (MD3) |
| F4 | The `RatingVersionView` loading and network-error states | the view and a happy-path test exist (`frontend/src/views/__tests__/RatingVersionView.test.ts`). The two error states are untested | fix before close, add the two state tests (MD4) |
| F5 | NFR-MODEL-14 has no marker | measured 0.0480 fits per pass against the 0.06 budget. The marker is missing | fix before close, add the marker (MD5) |
| F6 | FR-DATA-57 (`unrun_layers`) | Phase 2 handoff, not built in Phase 1b | defer with a strong reason: the phase boundary. Owner, the Phase 2 validation-report successor |
| F7 | FR-DATA-52 (exposure-ordered top-20) | trigger-checked 2026-08-27. The trigger has not fired. Unowned by design | defer with a strong reason: the trigger has not fired. No consumer has asked for the work |
| F8 | The full `03` rating surface (compile, score, rate tables, deployment) | Phase 2 | defer with a strong reason: the phase boundary |
| F9 | The `wf-01` §4 surfaces the demo does not seed (bandings, Peril Structure, reconciliation) | Phase 2, plan review 6 P1 | defer with a strong reason: the phase boundary |
| F10 | The `listRules` client gap (backlog #8) | **RESOLVED** — `frontend/src/api/rules.ts:114` exports `listRules` with tests | discharged |
| F11 | FR-MODEL-63/98 (prediction) delivered-but-untested | markers exist in the prediction path | discharged, verify the markers at close |
| F12 | The four frozen-plan items (backlog #103, #87, #127, #131) | each exists only in a frozen plan | fix before close, resolve each item's work or record its disposition (MD6) |

---

## Maintainer decision points

**MD1 — F1, the `validate.py` strings.** The strings assert minor units on a statistic. The W6b close record says they need their own line item. Options: fix before close (rewrite the strings to not assert minor units), or carry forward to the next money-correctness pass. **Recommendation:** fix before close. The strings are user-visible and small.

**MD2 — the demo UAT scope.** UAT-ready covers the core `wf-01` journey over HTTP: validated dataset, split, factors, GLM and GBM fits, comparison, approval, rating version. The surfaces plan review 6 records as Phase 2 — bandings, Peril Structure, reconciliation — stay out of the UAT. **Recommendation:** accept the core-journey scope.

**MD3 — F3, the postcondition check.** The demo postcondition check is exercised by the exit demo run, not by pytest. Options: fix before close, or defer with a strong reason. **Recommendation:** fix before close. A pytest test exercises the check logic without the full seed.

**MD4 — F4, the `RatingVersionView` states.** The happy path is tested. The loading and network-error states are not. Options: add the two state tests before close, or accept them as minor. **Recommendation:** fix before close. Two tests complete the view coverage.

**MD5 — F5, the NFR-MODEL-14 marker.** The measurement exists. The marker is missing. Options: add the marker to the measured test, or accept the recorded measurement as the evidence. **Recommendation:** fix before close. A marker makes the measurement visible to `req-coverage.py`.

**MD6 — F12, the frozen-plan items.** Four backlog items exist only in frozen plans. Options: fix before close, or defer with a strong reason. **Recommendation:** fix before close. Each item names real work a session agreed to. Resolve each item's work or record why it cannot be resolved now.

---

## Demo UAT-readiness

UAT-ready means the exit demo runs the core `wf-01` journey end to end over HTTP, the postconditions verify, and the UI shows the journey results. The acceptance mechanism is the scripted HTTP run, with the UI available for hands-on driving.

The UAT checklist:

- The seed completes: validated freMTPL2 dataset, split, factors, GLM and GBM fits.
- The comparison artifact exists.
- One model is approved.
- The rating version is approved.
- The postcondition check passes over HTTP (`_verify_journey_postconditions`).
- The UI reaches the model list, the model detail, the diagnostics, and the rating version.
- The total seed time stays within the NFR-PLAT-4 budget, or the deviation is recorded.

The fix-before-close findings (F1, F3, F4, F5, F12) land before the UAT run. The discharged findings (F2, F10, F11) are recorded in the register. The deferrals (F6 to F9) carry their stated reasons.

---

## Sequence to the auditor's close-confirmation

1. The findings and dispositions are filed in `docs/audit/register.md` and `docs/audit/phases/1b/register.md`.
2. The maintainer rules on MD1 to MD6.
3. The fix-before-close findings land.
4. The exit demo UAT runs and the postconditions verify.
5. The auditor reviews the register and the UAT evidence.
6. The auditor confirms the phase can go to the close decision.
7. The close decision follows (the next stage).

---

## Tasks

### T1. File the findings and dispositions in the registers.

**Files:**
- Modify: `docs/audit/register.md`
- Modify: `docs/audit/phases/1b/register.md`

- [ ] Write each finding from the table above into the register rows. Key each by the requirement or artifact id it concerns.
- [ ] Mark the discharged findings (F2, F10, F11) with their evidence.
- [ ] Mark the carried findings (F6, F7, F8, F9) with their named owners and their stated reasons.
- [ ] Mark the fix-before-close findings (F1, F3, F4, F5, F12) as `fix before close`, the maintainer's default.
- [ ] Run `python3 scripts/audit-docs.py`.

### T2. F1 — correct the `validate.py` strings (MD1, fix before close).

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/data/validate.py:1007, :1084`

- [ ] Rewrite the two strings so they do not assert minor units on a statistic.
- [ ] Add a `@pytest.mark.req` marker if a requirement governs the message text.
- [ ] Run the pricing-core tests.

### T3. F4 — add the `RatingVersionView` state tests (MD4, fix before close).

**Files:**
- Modify: `frontend/src/views/__tests__/RatingVersionView.test.ts`

- [ ] Add a test for the loading state.
- [ ] Add a test for the network-error state (the RFC 9457 problem alert).
- [ ] Run the frontend test half.

### T4. F5 — add the NFR-MODEL-14 marker (MD5, fix before close).

**Files:**
- Modify: the backend test that holds the NFR-MODEL-14 measurement

- [ ] Add `@pytest.mark.req("NFR-MODEL-14")` to the measured test.
- [ ] Verify `req-coverage.py` now reports NFR-MODEL-14 as evidenced.
- [ ] Run the test to confirm the marker is valid.

### T5. F3 — add a pytest test for the postcondition check (MD3, fix before close).

**Files:**
- Create: a backend test under `backend/tests/`

- [ ] Extract or exercise the postcondition-check logic so a pytest test covers it without the full seed.
- [ ] Write the test: the check refuses to start the browser when no approved model exists, and passes when one does.
- [ ] Mark the test with the journey reference if a requirement governs it.
- [ ] Run the backend test half.

### T6. Define the UAT checklist.

**Files:**
- Create or modify the demo acceptance document under `docs/audit/` or the close record

- [ ] Write the UAT checklist from the Demo UAT-readiness section into the acceptance document.
- [ ] State the acceptance mechanism: scripted HTTP run, UI available for hands-on driving.

### T7. Run the exit demo UAT.

- [ ] Run `scripts/demo.py` end to end with the full seed.
- [ ] Verify each UAT checklist item.
- [ ] Record the total seed time against NFR-PLAT-4. If it exceeds the budget, sample with `--rows` and record the deviation.

### T8. File the acceptance statement.

- [ ] Update the roadmap's Exit demo row from `pending` to `accepted` with the date, or record the pending state with the reason.
- [ ] Run `python3 scripts/audit-docs.py`.

### T9. The auditor's close-confirmation.

- [ ] Hand the register and the UAT evidence to the auditor.
- [ ] The auditor confirms the phase can go to the close decision, or returns findings.
- [ ] Record the confirmation in the phase register.

---

## Verification

- Both gate halves pass locally before a push:
  - `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
  - `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
  - `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test && pnpm --dir frontend build`
- Every open finding has a disposition in the register. No row is silent.
- The fix-before-close findings are green, with their tests passing.
- The exit demo UAT completes and the postconditions verify.
- `req-coverage.py` reports NFR-MODEL-14 as evidenced.

---

## Sources

- `docs/audit/closure-records.md`: the W7 close record §7 residue, the W6b close record §7 carry-forward.
- `docs/audit/plan-reviews.md`: plan review 6, P1 and P2.
- `docs/audit/register.md` and `docs/audit/phases/1b/register.md`: the registers the findings file into.
- `docs/roadmap.md` §6: the Phase 1b status table and the Exit demo row.
- `W6B-AUDITOR-HANDOVER.md` §24-§27: the W7 audit records and the close position.
- `packages/pricing-core/src/pricing_core/data/validate.py`, `backend/src/app/api/me.py`, `frontend/src/api/rules.ts`, `frontend/src/views/__tests__/RatingVersionView.test.ts`: verified at `5c1fb9b`.
