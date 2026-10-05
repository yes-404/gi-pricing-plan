---
id: PL-9494
family: plan
kind: leaf
title: WK-1178 — compile refuses a model_call whose feature_map misses the pinned model's required inputs, per component for a Peril Structure (FR-240): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: planner
tree: ecbd1954d90b1faf0bd197174d720d90ad8f6c6d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1263, PL-1371]
---

# PL 9494 (working id) — WK-1178: compile refuses a `model_call` whose `feature_map` misses the pinned model's required inputs, leaf plan

Filed under working id 9494 (this plan) and slice working id 9495 (its `SL-` row under
WK-1178 in [`../roadmap.md`](../roadmap.md), `draft`, added by this PR). Both were reserved
by the lead in `~/gi-pricing-plan.local/handover/eta.md` (row "SL 9495 / PL 9494", 5 Oct
18:52:06). The ruling this plan applies is **RL 9491** (working id, the decision-maker's,
drafted in parallel on branch `dm-9491-fr240-compile-completeness`). Nothing here is minted.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every red is seen failing, by its cause, before the
> code that turns it green), `python-package` (`pricing-core` stays standalone),
> `spec-change` (Task 4, RL 9491's text only), `dev-commands` (the two-half gate) and
> `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step. The executor is spawned from `.claude/roles/executor.md`.

## Goal

`compile_bundle` refuses a Rating Version whose `model_call` step's `feature_map` does not
supply every input the **pinned** model requires — its Factors, or its `feature_order` when
it has no Factors — and, for a `peril_structure_ref` step, every input of **each** component
model. The refusal is `MODEL_CALL_FEATURE_MAP_INVALID` (A-2's code, reused), naming the step
and the missing features. Today such a version compiles, approves and deploys, and fails on
every quote at score time as `MODEL_CALL_FAILED`.

**Architecture:** one pure check in `pricing_core/rating/compile.py`, called by
`compile_bundle` after every pinned model and every Peril Structure component has been
resolved (the pin loop, PL 9649's `ResolvedArtifact.factors`, A-3's
`_resolve_peril_components`). No database, no new code, no new shape. The backend reaches it
through the existing compile route's `ValueError` mapping (`rating_versions.py:558-565`).

**Tech Stack:** Python 3.12, Pydantic v2, pytest (pricing-core and backend suites).

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) FR-240 (`:137`),
amended by RL 9491's dated T-text; FR-222 (`:108`, the `model_call` step); FR-255 (the
`MODEL_CALL_FAILED` category this moves earlier); `02` FR-188 (the Peril Structure).

## The decision this plan rests on, quoted

The maintainer (by delegation), `~/gi-pricing-plan.local/channel/to-lead.md`, entry
"2026-10-05 18:51:33 BST — Save-time completeness: DECIDED NOW as (b), completeness at
COMPILE; no OQ; an RL with the FR-240 T-text; A-2's code reused", verbatim:

> Decided now rather than opened as an OQ: the trade-off is clear and G2's peril path (A-3/A-4, the exit demo) is exactly where a short-mapped GBM would fail per quote after deploy.
> (b): compile_bundle refuses a model_call step whose feature_map does not cover the PINNED model's required Factors (or its feature_order where it has none), using the existing resolver, before approval or deploy. Per component for a peril_structure_ref (17:44 DP-A3-7's per-component limb now has its home, at compile, not at save).
> CODE: REUSE MODEL_CALL_FEATURE_MAP_INVALID (A-2's code, once A-2 owns it in 03), naming the step and the missing features, not a new code: one fault, one code, at save (membership) and at compile (completeness). If A-2's code is not yet in 03's owned list when this RL is drafted, the RL cites A-2's T-text as the code's home and serialises after A-2.
> RECORDS: ONE RL (a DM when a seat frees) with the FR-240 T-text (a dated amendment: "all references resolvable" extended to a model_call's feature coverage of its pinned model), plus a note in PL 9597 (A-2) that its membership check is explicitly NOT a completeness check. The build is a small WK-1178 slice after A-2 (the same function family) and before A-4's demo path. Reserve the ids. (a), (c) and (d) are recorded as not taken.
> FD 9497's reservation released: correct (no requirement was broken; this is a new requirement, so it is spec first).

**The code's home.** At `ecbd1954`, `MODEL_CALL_FEATURE_MAP_INVALID` is not in `03` (`git
grep -c MODEL_CALL_FEATURE_MAP_INVALID origin/main -- docs/specs/03-rating-engine.md` prints
nothing) nor in `backend/src/app/errors.py`. A-2 (PL 9597, #1178 @`176a6a75`) appends it to
`03` §5.1's owned-codes list (its T3) and to `RATING_ERROR_CODES` (its write set). This slice
adds the code to neither: it raises the same string through `_raise_named`, and the backend's
compile mapping turns it into a 422 `PlatformError` carrying that code.

## Status

`draft`. It moves to `active` only through a separate activation PR, by a dated line, after
every activation need below holds.

### Activation needs, in order

1. **RL 9491 minted**, carrying the FR-240 T-text and its `grep -cF` anchor. Task 4 applies
   that text verbatim; nothing in this plan words it.
2. **PL 9649's slice merged** (#1152, the FR-240 family fix). It adds
   `ResolvedArtifact.factors: tuple[Factor, ...] = ()` and fills it in the backend
   `_Resolver.resolve`'s `model` branch. Without it a GLM's required Factors are invisible at
   compile (the Model's spec names them only by UUID, `model_schema/modelling.py:842`), and
   the check would pass every GLM vacuously. A-2 already needs it, so this holds through
   need 3.
3. **A-2 merged** (SL 9598 / PL 9597, working ids): the code is in `03`'s owned list and in
   `RATING_ERROR_CODES`, and a GLM `model_call` scores, so the end-to-end red (Acceptance 7)
   has a GLM to refuse. Serialisation: **after A-2**, the maintainer's "after A-2 (the same
   function family)".
4. **A-3 merged** (SL 9596 / PL 9595, working ids). The per-component limb (Acceptance 3)
   reads each component model's `ResolvedArtifact`, and only A-3's
   `_resolve_peril_components` (PL 9595 Task 2 Step 1, `compile.py`) resolves them. *The
   planner's sequencing:* A-2 → A-3 → **SL 9495** → A-4. It keeps the maintainer's order
   ("after A-2 … before A-4's demo path") and adds A-3 between them, because A-3 is already
   ahead of A-4 (PL 9593 activation need 4). The alternative, SL 9495 between A-2 and A-3
   with A-3 taking the per-component limb, splits one ruled check over two slices and edits
   A-3's frozen-at-merge plan; not proposed.
5. **Before A-4's dispatch.** A-4 (SL 9594 / PL 9593) does not yet name this slice as a need.
   *Proposal for the lead:* A-4's activation needs gain "SL 9495 merged", so the exit demo's
   B4 `model_call` compiles against the completeness check, as the ruling intends (G2's peril
   path is "exactly where a short-mapped GBM would fail per quote after deploy").
6. **The lane and the dispatch GO**; `active` by a dated line.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red
first" means the named test was run and failed **for the stated cause** before the code that
turns it green ([`README.md`](README.md) rule 2); a red with a different cause is a plan
defect, reported, not worked around. Each red is recorded in the slice's ledger with its
failure line as printed. The pricing-core tests are in
`packages/pricing-core/tests/test_rating_compile_completeness.py` (new), each marked
`@pytest.mark.req("FR-240")`.

1. **(i) A GLM missing a Factor's mapping is refused at compile.**
   `test_a_glm_model_call_missing_a_factor_is_refused_at_compile`: a GLM `model:` pin whose
   `ResolvedArtifact.factors` carries two Factors (slugs `driver_age_band`, `area_group`);
   the step's `feature_map` maps only `driver_age_band`. `compile_bundle` raises
   `ValueError` whose message starts `MODEL_CALL_FEATURE_MAP_INVALID: ` and names the step id
   (`'s_risk'`), the model ref and `area_group`. Red first: at the base `compile_bundle`
   returns a Bundle (`pytest.raises` reports `DID NOT RAISE`).
2. **(ii) A GBM missing a `feature_order` entry is refused.**
   `test_a_gbm_model_call_missing_a_feature_order_entry_is_refused_at_compile`: a GBM pin
   with no Factors (`factors=()`) and `fit_result.feature_order == ["age_years",
   "vehicle_power"]`; the map supplies only `age_years`. The message carries the code, the
   step id and `vehicle_power`. Red first: `DID NOT RAISE`.
3. **(iii) A Peril Structure with one component starved is refused, naming the component.**
   `test_a_peril_model_call_starving_one_component_is_refused_at_compile`: a
   `peril_structure:` pin whose one peril is `frequency_severity`; the frequency GLM needs
   `driver_age_band`, the severity GLM needs `driver_age_band` and `vehicle_group`; the map
   supplies `driver_age_band` only. The message carries the code, the step id, the
   structure's ref, the peril code, the role `severity_model`, the severity model's ref and
   `vehicle_group`, and does not name the frequency component. Red first: `DID NOT RAISE`
   (after A-3's merge the structure compiles).
4. **(iv) The complete controls compile.** `test_a_complete_feature_map_compiles` is
   parametrised over the three fixtures of items 1–3 with each map completed; each returns a
   Bundle. A map carrying **extra** entries beyond the required inputs also compiles
   (completeness never refuses a surplus; membership is A-2's save check). Run with the items
   above in one command:
   `uv run pytest -q packages/pricing-core/tests/test_rating_compile_completeness.py`.
5. **(v) The offset column is not required as a Factor (A-2's R2).**
   `test_an_unmapped_offset_column_is_not_a_completeness_failure`: a GLM whose spec declares
   a `log_column` offset on `exposure`, every Factor mapped, `exposure` not in the map.
   `compile_bundle` returns a Bundle. (The missing offset is still refused at score, as
   `MODEL_OFFSET_MISSING` inside `MODEL_CALL_FAILED`, PL 9597 item 3; the ruling covers
   Factors and `feature_order` only.) This test is green at the base and stays green; it
   guards against the implementation reading the offset as a required input.
6. **(vi) An empty `feature_map` is not an identity map** *(reading R-a below; held for the
   decision-maker)*. `test_an_empty_feature_map_is_refused_when_the_model_has_inputs`: the
   GBM of item 2 with `feature_map == {}` is refused, naming both features. Red first:
   `DID NOT RAISE`. If R-a is ruled the other way, this item is replaced by the ruled
   behaviour before the plan is activated.
7. **The real resolver path refuses it (end to end).**
   `test_a_glm_version_missing_a_factor_mapping_fails_to_compile` appended to
   `backend/tests/test_rating_glm_model_call.py` (A-2's new module): a GLM fitted and
   persisted as A-2's module does, an algorithm whose `model_call` omits one Factor's slug,
   a version pinning both, compiled through the route A-2's module uses. The compile is
   refused with `code == "MODEL_CALL_FEATURE_MAP_INVALID"` and a detail naming the step and
   the Factor; no Bundle is written. Red first: at the base the version compiles. This is the
   check that the backend resolver really fills `factors`: a vacuous pass in pricing-core
   would survive items 1–6, not this one.
8. **The FR-240 text is RL 9491's, verbatim.** `grep -cF '<RL 9491's anchor>'
   docs/specs/03-rating-engine.md` prints `1`, with the anchor copied from the minted RL;
   `python3 scripts/audit-docs.py` exits with no new FAILED line. *(Dated note, 2026-10-05,
   pre-mint: before applying, the find string is re-counted at this slice's own base under
   the FR-240 anchor rule (§"Write set", the SL 9647 row). The ledger records that count;
   any count other than 1 is a STOP to the maintainer. After applying, a distinctive
   phrase of RL 9491's own text counts 1.)*
9. **One fault, one code.** `git diff origin/main...HEAD -- backend/src/app/errors.py`
   is empty (the code is A-2's), and `git grep -c MODEL_CALL_FEATURE_MAP_INVALID --
   packages/pricing-core/src/pricing_core/rating/compile.py` prints `1` or more.
10. **The write set.** `git diff --stat origin/main...HEAD` names only §"Write set"'s paths.
11. **Existing compile and score tests still pass, with every fixture edit named.** Each
    module that compiles a `model_call` is run on its own:
    `test_rating_compile_bundle.py`, `test_rating_runtime.py`, `test_rating_score.py`,
    PL 9649's `test_rating_compile_fr240.py`, A-2's and A-3's modules, and
    `backend/tests/test_rating_version_compile.py`. A fixture whose map does not cover its
    model is a fixture the ruling now refuses: it is completed, never the check weakened, and
    the ledger lists each such edit with its file and line. At `ecbd1954` every committed
    `model_call` literal in these files carries a `feature_map` (`git grep` for
    `"type": "model_call"` against `feature_map` per file, §"Task 0 at planning time").
12. **The gate.** The full two-half gate passes on the merge tree, run once, holding a slot.

## Global Constraints

- `pricing-core` stays importable standalone, with zero FastAPI/SQLAlchemy/Redis deps
  (`CLAUDE.md` §2). The check reads `ResolvedArtifact`s; it never resolves anything itself.
- No new error code and no new shape (the ruling: "REUSE MODEL_CALL_FEATURE_MAP_INVALID …
  not a new code"; `CLAUDE.md` §2: "Nobody hand-writes a shape that already exists").
- No pandas in new code (`CLAUDE.md` §3).
- A coded refusal uses `_raise_named(code, message)` (`compile.py:538`), and its message ends
  `(FR-240)` as the module's other refusals end with their requirement.
- No ref is resolved twice (the RL-859 note in `compile_bundle`, `compile.py:598-602`).
- The executor runs no full suite outside the gate; one test file or a `-k` selection only.

## Scope

### Requirement coverage, each id individually

| Spec | Id | Where |
|---|---|---|
| `03` | FR-240 (as RL 9491 amends it) | Acceptance 1–8 |
| `03` | FR-222 (the `model_call` step: `model_ref` or `peril_structure_ref`, `feature_map`) | Acceptance 1–3, 6 |
| `03` | FR-255 (`MODEL_CALL_FAILED`, which these faults no longer reach) | Acceptance 5 (the one case that still reaches it) |
| `02` | FR-188 (the Peril Structure's components) | Acceptance 3 |

### Readings for the decision-maker (to confirm in RL 9491 or at the dispatch)

- **(R-a) An empty `feature_map`.** `runtime.py:553-555` gives a GBM an empty-map fallback:
  `pl.DataFrame({slug: [context.get(slug)] for slug in gbm_result.feature_order})`, reading
  each feature off the quote under its own slug. The ruling refuses a map that "does not
  cover" the required inputs, and `{}` covers none, so read literally an empty map is
  refused (Acceptance 6). *Recommendation: the literal reading.* No committed `model_call`
  literal has an empty map (`git grep -n -E 'feature_map"?: *\{\}' origin/main` prints
  nothing at `ecbd1954`), so nothing in the repository relies on the fallback. The fallback
  code is then unreachable through `compile_bundle`; this slice does not remove it (no
  ruling asks), and the ledger says so.
- **(R-b) What "required" reads.** A model's required inputs are the slugs of
  `ResolvedArtifact.factors` when it is non-empty; otherwise
  `payload["fit_result"]["feature_order"]` when present; otherwise none. This is the ruling's
  "required Factors (or its feature_order where it has none)", and A-2's R3 reads the same
  pair for membership. A payload with neither (an intercept-only GLM; the stub payload in
  `test_rating_compile_bundle.py:107-121`, which has no `fit_result`) has no required input
  and passes. *Recommendation: as written.*

### Task 0 at planning time (read, not run)

At `ecbd1954` (origin/main, read 2026-10-05 18:40–18:56 BST):

| Row | Fact | Where |
|---|---|---|
| 0.1 | `compile_bundle` resolves each pin in one loop and keeps only `payloads[str(ref)] = resolved.payload` | `compile.py:624-632` |
| 0.2 | `ResolvedArtifact` has `status` and `payload` only; `factors` is PL 9649's | `compile.py:434-440` |
| 0.3 | the handler builds `feature_row` from `step.feature_map.items()`, keyed by Factor slug | `runtime.py:542-546` |
| 0.4 | a GBM missing a column fails `SCORING_FEATURES_MISMATCH` inside `predict_gbm` | `modelling/gbm.py:1290-1296` |
| 0.5 | `PerilComponent` has `peril`, `method`, and `frequency_model`, `severity_model`, `burning_cost_model` refs | `model_schema/perils.py:214-229` |
| 0.6 | the backend compile route maps a coded `ValueError` to a 422 `PlatformError` with that code | `backend/src/app/platform/rating_versions.py:558-565` |
| 0.7 | every committed `model_call` literal carries a `feature_map` (per-file counts: `test_rating_algorithms.py` 2/2, `test_rating_algorithm.py` 1/2, `test_rating_version.py` 1/1, `test_rating_compile.py` 2/2, `test_rating_compile_bundle.py` 1/2, `test_rating_runtime.py` 1/1, `test_rating_score.py` 1/1, `bench-rating.py` 1/1, as `model_call`-literal count / `feature_map` line count) | `git grep -c` per file |

### Write set, and its contention (`RL-1263`, `RL 9620`)

| Path | Change |
|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | added: `required_model_inputs`, `check_model_call_coverage`; edited: `compile_bundle` (one call, after the pin loop and A-3's component resolution), its docstring, `__all__` |
| `packages/pricing-core/tests/test_rating_compile_completeness.py` | added (Acceptance 1–6) |
| `backend/tests/test_rating_glm_model_call.py` | appended (Acceptance 7; A-2's module) |
| existing test fixtures | only if Acceptance 11 finds an incomplete map; each named in the ledger |
| `docs/specs/03-rating-engine.md` | the FR-240 row (`:137`): RL 9491's T-text, verbatim |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated |

**Not written:** `backend/src/app/errors.py`, `03` §5.1's owned-codes list (A-2's),
`packages/model-schema/`, `runtime.py`, any `frontend/` file, any migration.

**Contention.** Classes as in `docs/process/delivery-process.core.json`'s `no_shared_files`.
**Snapshot: open PRs listed 2026-10-05 18:43 BST; each plan read from its branch at the head
named.** `PL-1371` §5 rule 4 serialises `compile_bundle` outright.

| Other slice (Work; PR @ head read) | Shared path | Them | Us | Class → consequence |
|---|---|---|---|---|
| **A-2**, PL 9597 (WK-1178; #1178 @`176a6a75`) | `compile.py` `ResolvedArtifact`, `compile_bundle`'s pin loop, `_check_result_types`; `03` §5.1 owned list; `errors.py`; `backend/tests/test_rating_glm_model_call.py` | `bandings`, `groupings`; GLM inputs written; the code appended; the module added | reads the code and the module; one call in `compile_bundle` | **plan dependency** (need 3) → after A-2, never concurrent |
| **A-3**, PL 9595 (WK-1178; #1174 @`2404ac86`) | `compile.py` `compile_bundle`, `_resolve_peril_components`; `03` FR-240 cell (`:137`) | adds the component resolution and `_check_peril_model_calls`; T-texts on FR-240 | reads the components; RL 9491's text on the same cell | **plan dependency** (need 4) → after A-3; the FR-240 cell edited by both → **SERIALISE** (already serial) |
| **SL 9568**, PL 9567 (WK-673; #1193 @`42d8be16`) | `docs/roadmap.md` | its SL row (in WK-673) | the SL 9495 row (WK-1178) | registry, distinct rows → ALLOWED; `compile.py` is not in its write set ("`compile.py` is not in the write set", its `:592`) |
| **PL 9521**, the FD 9549 fix (WK-1178; #1202 @`9396bdb3`) | `compile.py` | `_compatible`, `output_type_issues`, `_check_result_types` | `compile_bundle`, two new functions, `__all__` | different definitions in one file, **same Work** → ALLOWED one-sided only with the dispatch record naming each definition, `RL 9620` (a)/(b) written ((b): neither consumes the other's output). FD 9549's fix **is** PL 9521 (its `:23`, FD 9549 → FD-1424, #1197 merged); no separate plan exists |
| **PL 9578**, WK-675 S3 (#1186 @`aea4b634`) | `compile.py` | import block, `ValidationIssue`, `compile_bundle` (`:614`, the mode check wrapped), `__all__` | `compile_bundle`, `__all__` | `compile_bundle`: **SERIALISE** (rule 4, PL 9578's own `:392`) |
| **PL 9649**, FR-240 family fix (WK-673; #1152 @`df8ba756`) | `compile.py` `ResolvedArtifact`, `compile_bundle`; `03` FR-240 cell | `factors`; three checks; T1/T5 on FR-240 | reads `factors`; the same cell | **plan dependency** (need 2) → never concurrent |
| **PL 9610**, **PL 9609** (WK-1250 S2/S3; #1170, #1173) and **PL 9689** (WK-673 S3; #1138) | `compile.py` `compile_bundle` | as A-2's table records | one call | **SERIALISE** (rule 4) |
| **A-4**, PL 9593 (WK-1178; #1175 @`24eca966`) | none (`examples/`, backend tests) | B4's `model_call` over the AD structure | the check A-4's map must pass | **plan dependency, reversed**: A-4 follows this slice (need 5's proposal) |
| `docs/roadmap.md` WK-1178 tail | — | A-3 (SL 9596) and A-4 (SL 9594) append at the same place | the SL 9495 row | registry append, distinct rows → the second to merge re-reads |
| **SL 9647**, PL 9649 applying RL 9633's T1 (WK-673; #1152 @`df8ba756`; RL 9633 #1155 @`95590c87`) *(row added 2026-10-05, pre-mint)* | `03` FR-240 row (`:137`), its second cell | T1 appended with the find string `The message names the step and the rung.)* \|` | RL 9491's T-text appended with the **same** find string (RL 9491 #1214 @`b900e008`) | the same anchor: whichever slice applies second counts 0 → **SERIALISE** on the FR-240 row, under the anchor rule below |

*Dated note, 2026-10-05 (pre-mint): **the FR-240 anchor rule**, accepted by the maintainer (by
delegation) in the entry "2026-10-05 18:58:28 BST — S7 gate 1: (a) _SINKS entries ADOPTED;
the re-gate plan CONFIRMED, with an explicit allowed-failure set; the measurement re-run in
the slot" (`channel/to-lead.md`), item 4, verbatim: "RL 9491 #1214 @b900e008 and the FR-240
anchor collision with RL 9633 T1: the rule (append after the last amendment then present,
re-counted at its own base, ≠1 is a STOP to me) is ACCEPTED, and it is named in BOTH RL 9491
and PL 9649's contention." SL 9495 and SL 9647 serialise on the FR-240 row. The slice that
applies second appends its text at the end of FR-240's second cell, after the last amendment
then present; it re-counts its find string at its own base; any count other than 1 is a STOP
to the maintainer. This slice follows PL 9649 (need 2), so SL 9495 is expected to apply
second. The code's home is unchanged: `MODEL_CALL_FEATURE_MAP_INVALID` is not yet in `03`'s
owned list (A-2's T3 homes it), so SL 9495 serialises after A-2 (need 3).*

### Size

Half an executor-day: one pure function pair, one call, six pricing-core tests on fakes, one
backend test appended to a module that already builds a persisted GLM, one spec cell.

## Decision points

- **DP-1 — Where "a model's required inputs" is defined (owner: the decision-maker).** A-2's
  save check (backend, `platform/rating_algorithms.py`, beside `create_algorithm`) computes
  R3's "Factors, or `feature_order` when it has none" for membership; this slice computes the
  same pair for completeness.
  - (a) This slice's `required_model_inputs` in `pricing-core` only; A-2's backend function
    is not edited. Cost: the R3 choice lives in two places, one per check.
  - (b) `required_model_inputs` is public in `pricing-core`, and A-2's backend function calls
    it for its R3 choice. Cost: one edit to A-2's merged function, covered by A-2's own items
    13, 18 and 19; one more path in the write set.
  - *Recommendation: (b).* A definition written twice diverges (`CLAUDE.md` §2), and the two
    checks are the ruling's "one fault, one code". If A-2's merged function does not compute
    the pair (Task 0 Step 2 reads it), (a) is moot and (b) applies trivially.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm each activation need at `origin/main`: RL 9491 minted (`ls
  docs/rulings | grep -i fr-240` and read its T-text and anchor); `git grep -n "factors:"
  -- packages/pricing-core/src/pricing_core/rating/compile.py` shows PL 9649's field;
  `git grep -c MODEL_CALL_FEATURE_MAP_INVALID -- docs/specs/03-rating-engine.md
  backend/src/app/errors.py` prints a count for each; `git grep -n
  "_resolve_peril_components" -- packages/pricing-core/src` shows A-3's function.
- [ ] **Step 2:** Read A-2's merged save check in `backend/src/app/platform/rating_algorithms.py`
  and A-3's `_resolve_peril_components`: record in the ledger its return type and the key of
  its dict, and whether A-2's function computes R3's pair (DP-1).
- [ ] **Step 3:** Re-read `compile_bundle` at the merge base and record where PL 9649 keeps
  the resolved model artifacts after the pin loop. Reuse that mapping; do not resolve again.

### Task 1: The reds (Acceptance 1–3, 6)

**Files:** Create `packages/pricing-core/tests/test_rating_compile_completeness.py`.

**Interfaces:** Consumes `compile_bundle`, `ResolvedArtifact` (with PL 9649's `factors`),
`RatingVersion`. Build each `Factor` the way PL 9649's `test_rating_compile_fr240.py` does,
and each GBM payload from `test_rating_runtime.py`'s `_gbm_model_payload`
(`:42`) with `feature_order` replaced; mirror those modules' fixtures rather than this plan's
names, and do not reinvent them ([`README.md`](README.md) rule 3). The algorithm is
`test_rating_runtime.py`'s `_algorithm_payload` shape with the `s_risk` step's
`feature_map` set per test.

- [ ] **Step 1:** Write a fake resolver taking `dict[str, ResolvedArtifact]`, and the four red
  tests. The assertion shape for each:

```python
with pytest.raises(ValueError, match=r"^MODEL_CALL_FEATURE_MAP_INVALID: ") as caught:
    await compile_bundle(version, resolver)
message = str(caught.value)
assert "'s_risk'" in message
assert "area_group" in message          # the missing feature, per test
assert "driver_age_band" not in message  # a mapped feature is never named as missing
```

- [ ] **Step 2:** Run `uv run pytest -q
  packages/pricing-core/tests/test_rating_compile_completeness.py`. Expected: the four reds
  fail with `DID NOT RAISE`. Any other failure (a fixture `ValidationError`, a `KeyError`)
  is a fixture defect: fix the fixture until the only failure is `DID NOT RAISE`. Record each
  failure line in the ledger.
- [ ] **Step 3:** Add Acceptance 4's parametrised control and Acceptance 5's offset test; run
  the module; both green at the base. Commit: `test: reds for compile-time feature_map
  completeness (FR-240)`.

### Task 2: The check (Acceptance 1–6)

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/compile.py`.

**Interfaces:** Produces `required_model_inputs(resolved: ResolvedArtifact) -> tuple[str,
...]` and `check_model_call_coverage(algorithm: RatingAlgorithm, resolved: Mapping[str,
ResolvedArtifact]) -> None`, where `resolved` holds every pinned model and every Peril
Structure component, keyed by `str(ref)`.

- [ ] **Step 1:** Add the two functions after `check_step_refs_pinned`:

```python
def required_model_inputs(resolved: ResolvedArtifact) -> tuple[str, ...]:
    """A pinned model's required inputs: its Factors' slugs, or its `feature_order`
    when it has no Factors (RL 9491, FR-240). The offset column is not one (A-2's R2)."""
    if resolved.factors:
        return tuple(factor.slug for factor in resolved.factors)
    fit_result = resolved.payload.get("fit_result") or {}
    return tuple(fit_result.get("feature_order") or ())


def check_model_call_coverage(
    algorithm: RatingAlgorithm, resolved: Mapping[str, ResolvedArtifact]
) -> None:
    """Refuse a `model_call` whose `feature_map` misses an input its pinned model needs
    (FR-240, RL 9491). Per component for a `peril_structure_ref`. Membership is the
    save check's (A-2); this is completeness only."""
    for step in algorithm.steps:
        if not isinstance(step, RatingModelCallStep):
            continue
        mapped = set(step.feature_map.values())
        if step.model_ref is not None:
            targets = [(str(step.model_ref), "")]
        else:
            assert step.peril_structure_ref is not None  # exactly one is set (FR-222)
            structure = PerilStructure.model_validate(
                resolved[str(step.peril_structure_ref)].payload
            )
            targets = [
                (
                    str(ref),
                    f" (structure {step.peril_structure_ref}, peril {component.peril}, {role})",
                )
                for component in structure.perils
                for role in ("frequency_model", "severity_model", "burning_cost_model")
                if (ref := getattr(component, role)) is not None
            ]
        for ref, where in targets:
            missing = [s for s in required_model_inputs(resolved[ref]) if s not in mapped]
            if missing:
                _raise_named(
                    "MODEL_CALL_FEATURE_MAP_INVALID",
                    f"step {step.step_id!r}: the feature_map does not map {missing}, "
                    f"which {ref}{where} requires (FR-240)",
                )
```

  Adapt `structure` and `targets` to A-3's merged return type (Task 0 Step 2); if A-3
  already validated the structure, reuse that value rather than validating twice.
- [ ] **Step 2:** In `compile_bundle`, after the pin loop and A-3's component resolution,
  build the `resolved` mapping from the artifacts already in hand (Task 0 Step 3) and call
  `check_model_call_coverage(algorithm, resolved)`. Add one docstring sentence and both names
  to `__all__`.
- [ ] **Step 3:** Run the new module: all green. Under DP-1 (b), point A-2's backend function
  at `required_model_inputs` and run `backend/tests/test_rating_algorithms.py` and
  `backend/tests/test_sub_graphs_api.py` (one file per run). Commit: `feat: compile refuses
  a model_call whose feature_map misses its pinned model's inputs (FR-240)`.

### Task 3: End to end, and the existing suites (Acceptance 7, 11)

- [ ] **Step 1:** Append Acceptance 7's test to `backend/tests/test_rating_glm_model_call.py`,
  reusing that module's persisted-GLM fixture and its compile call. Run it at the commit
  before Task 2 (`git stash` is forbidden; use a detached checkout of the Task 1 commit in a
  scratch worktree) to see it red by its cause (the version compiles), then at HEAD (green).
- [ ] **Step 2:** Run each Acceptance 11 module, one per command. Complete any incomplete
  fixture map and list it in the ledger. Commit: `test: the backend compile refuses a short
  feature_map end to end (FR-240)`.

### Task 4: The spec text (Acceptance 8)

- [ ] **Step 1:** Apply RL 9491's FR-240 T-text to `docs/specs/03-rating-engine.md`'s FR-240
  row, verbatim, at the position the RL names. Run the RL's `grep -cF` anchor (prints `1`)
  and `python3 scripts/audit-docs.py`. *(Dated note, 2026-10-05, pre-mint: under the FR-240
  anchor rule (§"Write set", the SL 9647 row), re-count the find string at this slice's own
  base first. If SL 9647's T1 is already applied, append at the end of FR-240's second cell,
  after the last amendment then present. Any count other than 1 is a STOP to the
  maintainer, never a re-anchoring by the executor.)*
- [ ] **Step 2:** Commit: `docs(specs): FR-240 — compile refuses a model_call's incomplete
  feature_map (RL 9491)`.

### Task 5: The gate and the ledger (Acceptance 9, 10, 12)

- [ ] Run Acceptance 9 and 10's commands, then the full two-half gate once in a slot; record
  each exit code and the tree in the ledger.

## Hand-off

1. The lead mints PL 9494 and SL 9495 at the merge turn and dispatches only after every
   activation need holds.
2. The lead's proposal (need 5): A-4's activation needs gain "SL 9495 merged".
3. When this slice merges, PL 9597's pre-mint note ("its feature_map check is
   membership-only") is discharged by the code it points to.

## Self-review

1. **Coverage of the ruling, clause by clause.** "compile_bundle refuses … does not cover the
   PINNED model's required Factors": Acceptance 1, 7. "(or its feature_order where it has
   none)": Acceptance 2. "using the existing resolver": Task 2 reads only resolved artifacts,
   and Acceptance 7 runs the backend resolver. "before approval or deploy": compile precedes
   both (FR-240). "Per component for a peril_structure_ref": Acceptance 3. "REUSE
   MODEL_CALL_FEATURE_MAP_INVALID … naming the step and the missing features": Acceptance 1–3,
   9. "after A-2 … before A-4's demo path": needs 3 and 5. The brief's five reds are
   Acceptance 1, 2, 3, 4 and 5.
2. **Placeholders.** The one deferred literal is RL 9491's anchor (Acceptance 8), which is
   that ruling's to write; the plan names where it comes from.
3. **Type consistency.** `required_model_inputs` and `check_model_call_coverage` are named
   the same in Task 2, the write set, and DP-1.
4. **Repository literals read at `ecbd1954`:** every row in §"Task 0 at planning time". The
   `ResolvedArtifact.factors` type is PL 9649's plan (#1152 @`df8ba756`, its `:674`), and
   `_resolve_peril_components`'s return type is A-3's plan (#1174 @`2404ac86`, Task 2
   Step 1); both are re-read at Task 0, merged.
5. **What was not executed.** No test or code was run. The sketches are against names quoted
   above; each red is seen failing before its code.
