---
id: RL-1616
family: ruling
title: WK-690 Slice 5 decided — one stateless, bounded, flag-gated preview route parses, derives and evaluates a loss without persisting or auditing anything
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-11            # original date 2026-10-11, set at the draft; minted 2026-10-11
owner: decision-maker
tree: d699a561d6a93f33b74beb9c07023f8e655bb8c7
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1265, RL-1362, RL-1410, PL-1268, SL-1275, FR-144, FR-145, FR-150, FR-367, NFR-483, NFR-484]
---

# RL-1616 — WK-690 Slice 5: DP-S5-1 decided

*(Minted 2026-10-11 as RL-1616 from working id 9935, in the D11 batch mint PR.)*

## How this was ruled

- **The decision is not this record's.** It is the maintainer's, by delegation, in the entry
  headed *"2026-10-11 11:28:14 BST — DP-S5-1 RULED (a): one stateless POST
  /api/v1/custom-objectives/preview, with BOUNDS so a keystroke route cannot starve the platform;
  SL-1622 noted"* in `~/gi-pricing-plan.local/channel/to-lead.md`. Items 1 to 5 read, verbatim:

  > 1. (a) ADOPTED: no grid → parse only; with a grid → derive and evaluate with the SAME derive()/compile_kernel() as the fit (one implementation, never a preview copy). A bad loss → 200 ok:false with the position (the /model-specs/validate precedent). SPEC FIRST: the §3.7 FR, the §5.1 row, and the model-schema request/response shapes (generated contract; never hand-written in the frontend).
  > 2. Permissions: model:fit + custom_objective:author; flag off → 409 OBJECTIVE_KIND_NOT_ENABLED. No audit, because it persists nothing; the FR says NFR-484's "objective derivation" means the stored /derive result only, and create refuses `derived`, so a preview can never become a stored one.
  > 3. CONDITIONS (a CPU-heavy route on the shared box, called per keystroke), each a numbered clause in the FR and each tested:
  >    a. INPUT BOUNDS: the parser's existing limits (the §4.6 profile limits, FR-145) apply unchanged; the grid has a hard maximum point count named in the FR; over a bound → 422 VALIDATION_FAILED, before any SymPy work.
  >    b. TIME BOUND: derivation and evaluation run OFF the event loop, in a bounded executor (a small fixed worker count named in the FR), with a wall-clock timeout. A timeout returns ok:false with a timeout reason (not a 500); the worker is never left running unbounded.
  >    c. ISOLATION: preview work can never queue ahead of /score. A test or measurement shows /score's p99 at a moderate rate is unaffected while previews saturate their executor. (NFR-489's bar is S5's; this is a non-interference check, shared box, diagnostic.)
  >    d. S5 measures the preview's own latency budget (the FR states it), diagnostic on the shared VM.
  > 4. RL-1410 R4 unchanged. Sizing ~0.3 slice: accepted (conditions 3a–3c may add a little; the plan says so).
  > 5. Rejected, as recommended: drafts per keystroke, dropping live parse (that would cut scope; not taken), and a client-side parser (a second parser = two grammars, the need-4.5 class of defect).

- **The options memo** is `~/gi-pricing-plan.local/handover/dm-wk690-dps5-1-2026-10-11.md` (a
  local file; decision-maker `dm-wk690`, 2026-10-11). The decision point comes from
  planner-wk690's `readiness-wk690-s4s5-2026-10-11.md` (needs 5.4, 5.5 and 5.8). WK-690's L5 delta
  PL-1621 (minted in the same D11 batch) carries it as DP-S5-1.
- **Written 2026-10-11 by `date`**, by the decision-maker seat `dm-wk690`. Every fact below was
  read at `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7`.
- **This record rules a plan's decision point and never edits the plan** (`document-ids.md`
  §1.6, PL row).

## Locators — read at `d699a561`

| Fact | Where |
|---|---|
| The eight custom-objective routes: list, create, get, derive, certify, certificate, submit and usage. None parses without persisting | `docs/specs/02-modelling.md` §5.1 `:1843-1850`; `backend/src/app/api/custom_objectives.py` `:170-439` |
| Create parses `loss` in the `objective` profile and answers 422 with the position, then writes a `draft` and `custom_objective.created` | `backend/src/app/platform/objectives.py` `_require_the_grammar` `:297-312`; audit `:279-286` |
| Create does not accept `derived`: *"the platform generates it at `/derive`"* | `custom_objectives.py` `CreateCustomObjective` `:100-101` |
| `/derive` checks `model:fit` and `custom_objective:author` before the flag, then refuses with `OBJECTIVE_KIND_NOT_ENABLED` while the flag is off | `custom_objectives.py` `derive_custom_objective` `:313-339`, docstring `:320-325` |
| A second derive is refused 409 `VALIDATION_FAILED` | `RL-1410` R4 |
| The pure functions the preview composes | `pricing_core/data/expressions.py` `parse_expression`; `pricing_core/modelling/expression_objective.py` `derive` `:100`, `compile_kernel` `:217` |
| The 200-with-`ok: false` precedent for a live-validation route | `02` §5.1 `:1829` (`/model-specs/validate`); `backend/src/app/api/models.py` `validate_model_spec` `:683-699` |
| NFR-484 lists *"objective derivation/certification/approval"* among the audited events | `02` `:2936` |
| The audit log is *"the append-only record of every state change that affects a price"* | `docs/specs/06-governance.md` `:18` |

## Ruled

| Item | Ruling |
|---|---|
| **DP-S5-1** | **(a).** One stateless route, `POST /api/v1/custom-objectives/preview`. **With no `grid`, it parses only. With a `grid`, it also derives and evaluates**, through the same `derive()` and `compile_kernel()` the fit uses: one implementation, never a preview copy. A loss that does not parse answers **200 with `ok: false`** and RL-1362 DP-S3-3's positioned error, as `/model-specs/validate` does. A malformed request answers 422 |
| **Spec first** | A new FR in `02` §3.7, a new §5.1 row, and the `model-schema` request and response shapes. The request reuses `ObjectiveParameter`. The contract is generated, and the frontend client is generated from it, never hand-written (`CLAUDE.md` §2, §3) |
| **Permission and flag** | `model:fit` and `custom_objective:author` (FR-367), both checked before the flag. While `expression_objectives_enabled` is off, the answer is 409 `OBJECTIVE_KIND_NOT_ENABLED` (FR-150). DP-3's default-off (`RL-1265`) is unchanged |
| **Audit** | No Audit Event, because the route persists nothing. **The FR states** that NFR-484's *"objective derivation"* is the derivation stored by `/derive`, and that create refuses `derived`, so a preview can never become a stored derivation |
| **Condition 3a: input bounds** | The §4.6 profile limits (FR-145) apply unchanged. The grid has a hard maximum point count, named in the FR. Over any bound the answer is 422 `VALIDATION_FAILED`, **before any SymPy work** |
| **Condition 3b: time bound** | Derivation and evaluation run off the event loop, in a bounded executor whose fixed worker count is named in the FR, with a wall-clock timeout. A timeout answers `ok: false` with a timeout reason, not a 500. No worker is left running unbounded |
| **Condition 3c: isolation** | Preview work can never queue ahead of `/score`. A test or a measurement shows `/score`'s p99 at a moderate rate is unaffected while previews saturate their executor. This is a non-interference check on the shared box, diagnostic. NFR-489's bar stays S5's |
| **Condition 3d: own budget** | S5 measures the preview's own latency budget, which the FR states. Diagnostic, on the shared VM |
| **RL-1410 R4** | Unchanged. The preview touches no persisted objective |
| **Editing (need 5.8)** | The editor is create-only. FR-367's "create, edit and version" is met by create, which versions on a reused slug (the route summary *"Create or version a Custom Objective"*, `custom_objectives.py:235`). No edit route is added |
| **Rejected** | A draft per keystroke (an audit log of typing; R4 refuses its second derive). Dropping live parse (a scope cut, not taken). A client-side parser (a second parser, so two grammars, which is the need-4.5 class of defect in `RL-1615`, working id) |

**Each of conditions 3a to 3d is a numbered clause in the FR, and each is tested.**

## The spec dispositions

These land in **S5's commit with the code**, or before it, never after (`CLAUDE.md` §2), through
`spec-change`, each citing this record:

- `02` §3.7: the new FR, with clauses 3a to 3d and the audit sentence.
- `02` §5.1: the new row.
- `02` §5.3: a dated line on the Custom objective library row's 2026-08-27 "not rendered" note.
- `WF-702` B1.4: a citation of the route.
- The `model-schema` shapes, with `docs/contracts/` regenerated.

The FR's id is appended under `spec-change`, from the global sequence.

## What it obliges

- **PL-1621's planner** cites this record on DP-S5-1. S5's estimate gains about 0.3 of a slice
  (accepted), plus whatever conditions 3a to 3c add, and the plan says so.
- **WK-690 Slice 5 (`SL-1275`)** builds the route and the editor against it, red first. The tests
  cover: the flag; both permissions; `ok: false` with a position; the grid cap's 422 before
  SymPy; the timeout's `ok: false`; the curve agreeing with `compile_kernel` on the same inputs;
  and condition 3c's non-interference result.
- **Nothing is audited and nothing is persisted.** Any test that sees a new row or event after a
  preview call is a failure.

## Acceptance — the violation that must become detectable

Each is red first in Slice 5:
1. *A keystroke route starves the platform.* An over-cap grid is refused before SymPy runs, and
   a slow derivation times out to `ok: false`.
2. *A preview disagrees with the fit.* The curve equals `compile_kernel`'s output for the same
   loss, parameters and grid.
3. *A preview leaves a trace in governed state.* No row and no Audit Event is written.
4. *A caller without the permissions, or with the flag off, learns anything.* The answers are
   403, then 409 `OBJECTIVE_KIND_NOT_ENABLED`, in that order.
