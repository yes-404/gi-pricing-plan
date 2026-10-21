---
id: LG-8138
family: ledger
title: WK-690 slice SL-1275 — Slice 5, the authoring view and WF-702 Route B end to end (PL-1268, PL-1621, PL-1665) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-21
owner: executor
tree: ac34e2a06e2a430512c447161e05d9ffcb35ebd9
phase: P2
work: WK-690
slice: SL-1275
plans: [PL-1268, PL-1621, PL-1665]
corrected_by: []
relates: [PL-1268, PL-1621, PL-1665, RL-1616, SL-1275, SL-1273, SL-1274]
---

# LG-8138 — WK-690 slice SL-1275: Slice 5, the authoring view and WF-702 Route B end to end

Filed 2026-10-21 under working id 8138 (lead-reserved in eta.md); executor seat `exec-1275`, branch `sl-1275-wk690-s5-authoring-view`, base `origin/main` `44c18e11ca028d25c8b4c9d92077cc0f3622ef8e` (re-merged into the branch, rc 0, no conflict).

**GO:** the maintainer's entry "2026-10-21 15:03:33 BST — Maintainer: GOs on the 15:02:44 work queue", item 4: "GO SL-1275 (PL-1268): build in parallel, off the row-2 path. Gate order is SL-1711 first, then by readiness." **MERGE-ACK:** not yet given.

## Needs census (on origin/main 44c18e11)

- `SL-1273` (Slice 3): roadmap row `status: closed`. `SL-1274` (Slice 4) merged #1344 (`d87dd259`), so the one-WK-690-slice-at-a-time rule (`PL-1621` Global Constraints) is met.
- `PL-1268`, `PL-1665` active; `PL-1621` stands as `PL-1665` amends it (read in full for Slice 5: `PL-1268` :532-554, `PL-1621` 5.1-5.6 and R5.1-R5.4, `PL-1665` 5.1'/5.3'/5.7).
- `DP-S5-1`: `RL-1616` (read in full). `OQ-550`: decided (c), WK-675's, `docs/open-questions.md:41`.
- `5.7` needs a **TRUE ALONE window** booked by the lead (`PL-1665` S5 row). **Not met at the time of the build**: the code is built before the window, and the slice does not close until 5.7 is measured.

## Decisions the slice made (PL-1665 5.1': "the values in 3a, 3b and 3d are the slice's choice")

| Clause | Value | Reason |
|---|---|---|
| 3a grid maximum | 500 points (`PREVIEW_MAX_GRID_POINTS` in `model-schema`, so the contract carries `maximum: 500`) | One curve on one chart: a few hundred points draw smoothly, and it bounds the kernel work per call to a vectorised pass over 500 floats. |
| 3b workers / timeout | 2 workers, 5 s from submission | Two keeps a typist's overlapping calls from queueing behind one slow derivation; 5 s is well past a typical `derive` and short enough that a held worker frees fast. SymPy cannot be interrupted, so a started derivation finishes (bounded by FR-145's 200-node/20-depth limits) and its result is discarded; unstarted work is cancelled. |
| 3d budget | p95 <= 2 s for a 500-point grid | Provisional until 5.7 is measured in the ALONE window; the measured value replaces it through a spec amendment if it does not hold. |

## Tasks

1. **Activation** (`41f73db2`): SL-1275 `active`, this ledger opened, INDEX regenerated, `doc-index.py --check` rc 0, `audit-docs.py` red only on check 31 (the working-id gap 8138, expected until the mint).
2. **Spec first** (`8d2fe052`): `02` §3.7 new FR (working id FR-8140, clauses 3a-3d and the audit sentence), §5.1 row, §5.3 dated built line; `model-schema` shapes `ObjectivePreview*` (the request reuses `ObjectiveParameter`); `generate-contracts.py` wrote `docs/contracts/openapi/generated.json`, `--check` rc 0 ("54 generated contracts match the models"); `pnpm --dir frontend generate:api` rc 0 and `frontend/src/api/generated` is VCS-ignored (`git check-ignore` prints it).
3. **Backend** (`8d2fe052`): `app/platform/objective_preview.py` and the route in `app/api/custom_objectives.py`; `grammar_refusal` extracted from `_require_the_grammar` so create and preview share one position computation. **Red first:** `uv run ... run-small.sh backend/tests/test_objective_preview.py` at the tree without the module: `ImportError: cannot import name 'objective_preview' from 'app.platform'` (collection error, rc 2). **Green:** `12 passed`. The DB-backed `test_objective_preview_api.py` and `test_wf702_route_b.py` are written and **owed a DB run**.
4. **Frontend** (`c74da4f1`): `previewObjective`/`createObjective` on the generated types, `ObjectiveLossCurve.vue` (a `ChartFigure` caller), `ObjectiveEditorView.vue`, route `/objectives/new`, library link. **Red first:** at `073fd135`'s stubs the four prep test files give `Tests 17 failed | 1 passed (18)` (the one pass is the route test that the library and certificate routes are undisturbed). **Green:** the same files, `Tests 11 passed` (+ 9 for the client and curve); whole suite `Test Files 129 passed (129), Tests 817 passed (817)`; `pnpm lint` rc 0; `pnpm type-check` rc 0. The prep fixtures' provisional field names (`position`, `timeout`, row-wise `curve`) were re-bound to the generated shapes, as the prep's own comments instruct; every asserted behaviour is unchanged.
5. **5.5 one parser:** `git diff --name-only origin/main...HEAD -- frontend/src | grep -ciE 'pars|grammar|evaluat'` prints `0` (grep exit 1 is its no-match code).
6. **WF-702 Route B** (`90078720`): `backend/tests/test_wf702_route_b.py`, written, not yet run.

## Findings carried to the lead

- **B4.2 is not built.** `WF-702` B4.2 says a `violated` convexity check escalates to the two-approver rule; the default `custom_objective` policy asks one approver and nothing escalates on a finding. The Route B file sets the workspace policy to two approvers and says so in its docstring. Code and spec disagree here; neither was edited.
- **`WF-702` B1.4/B1.5 text** says the frontend "parses on every keystroke" and the rejection is `OBJECTIVE_GRAMMAR_VIOLATION`; `RL-1616` has the editor call the route and the route answer 200 `ok: false`. `PL-1665` 5.1' lists a B1.4 citation of the route as a slice disposition, but a `WF-` is not the executor's to amend (`executor.md`), so it is **not done** and waits for the lead.
- **The editor learns the flag only from the first preview's 409** (the frontend has no settings read), so a flag-off workspace sees an enabled editor until the first keystroke settles.

## Accessibility review (`accessibility-tester`, a code read, 2026-10-21; PL-1621 5.4)

Reviewed `ObjectiveEditorView.vue` and `ObjectiveLossCurve.vue`; no screen reader or browser was used, and no axe/Playwright coverage exists to cite. The table carries every plotted point, the chart is non-colour (one series) and the loss textarea, slug and every number input are named. 13 findings; dispositions:

- **Fixed:** created message now inside one persistent `role="status"` region (the same region as the not-enabled and timeout notices, so there is exactly one status); focus moves to that region when the 409 disables the textarea; textarea has `aria-invalid` and `aria-describedby` to its error; input borders `slate-500` (non-text contrast); parameter rows are `role="group"` with row-numbered names and Remove labels; "to" is "Score f to"; required marked on slug and loss; a hint says why Create is disabled; gradient/hessian wrap; new row's name input takes focus; the chart canvas is `aria-hidden` (the table is its text alternative).
- **Not changed, bound by the prep tests:** the debounced parse error stays `role="alert"` (the prep tests find it by that role, `ObjectiveEditorView.test.ts`); the reviewer would prefer `role="status"` (polite) for text produced mid-typing. Raised to the lead, not silently re-tested.
- **Not changed, advisory:** the created link is a plain `<a>` (a full page load; the library uses the same href form); raw enum values as response labels; no pending indicator for the 600 ms debounce.

## PRs

None opened (the lead opens the PR after the gate).
