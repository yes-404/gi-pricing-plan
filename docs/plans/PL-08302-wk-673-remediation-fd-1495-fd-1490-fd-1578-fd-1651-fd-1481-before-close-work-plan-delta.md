---
id: PL-8302
family: plan
kind: map
title: WK-673 — remediation before close, FD-1495 first and alone, then FD-1490, FD-1578, FD-1651, the SL-1389 red-first proofs and FD-1481, cut as two slices — Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-11-03
owner: planner
tree: a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1267, FD-1495, FD-1490, FD-1578, FD-1651, FD-1481, RL-1470, RL-1958]
---

# PL-8302 — WK-673: remediation before close (S-a FD-1495; S-b the rest): Work-plan delta

> **For agentic workers:** this is a **Work-plan delta** under Lean P2 L5 and L1 (a')
> (`.claude/roles/planner.md`, the Lean P2 bullet). It does not replace
> [`PL-1267`](PL-01267-wk-673-dislocation-with-attribution-map-plan.md) (WK-673's map plan)
> or any WK-673 delta, and it leaves them all unedited. It adds **two rows**: **S-a (FD-1495)**
> and **S-b (the rest)**. Their slice and ledger ids are allocated by the lead at the
> maintainer's GO, so this file writes them as **SL &lt;a&gt; / LG &lt;a&gt;** and
> **SL &lt;b&gt; / LG &lt;b&gt;**. Each ledger quotes its row below as its scope. REQUIRED
> SUB-SKILL for each executor: subagent-driven-development (recommended) or executing-plans,
> task by task. Each executor also binds `test-driven-development` (every red is seen red **by
> its cause** at the row's base before the code that turns it green), `python-test` (the `req`
> marker; negative tests), `python-package` (`pricing-core` stays standalone and never raises
> `PlatformError`), `dev-commands` (both gate halves, the slot wrappers) and `git-hygiene`. It
> reads [`README.md`](README.md)'s five unchecked conventions and is spawned from
> `.claude/roles/executor.md`, model `sonnet` (the authority, below).

Filed under **working id PL 8302**, reserved by the lead in the brief
`brief-plan-wk673fix-2026-11-03.md`. Written 2026-11-03 by the planner (seat plan-wk673fix2).
Every `file:line` below was read at `origin/main` `a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe`
(tree `598c8c3a`) unless it names another tree. Nothing was run: no test and no probe. Every
"live at main" claim is **by reading** and names the line that shows it. The close audit is
**CR 8292** (working id), at `origin/docs/wk673-close-audit-2026-11-03` `ad7c93f4`. It audited
`c807a59d`, and its line numbers are cited as `CR 8292:<n>` at `ad7c93f4`.

## Authority

All entries are in `~/gi-pricing-plan.local/channel/to-lead.md`.

- **The plan and its order.** "2026-11-03 16:03:37 GMT", item (A), verbatim: *"GO — one WK-673
  remediation delta PL by an opus planner NOW, limbs in this order: FD-1495 first (a
  control-intent factor reaching the price through model_call — mispricing class, HIGH);
  FD-1490 (MONETARY_FLOAT_REFUSED never raised — a money check that cannot fire); FD-1578
  (AttributionError messages embedding quote_id and premiums — data in error text); FD-1651 +
  FD candidate 1 (the missing broken-input proofs, test-only); FD-1481. FR-364's
  rate_table_diffs limb: re-owned to P3 by a dated line (mine, by delegation) unless the CR
  shows it on the WF-699 / WF-701 exit-demo path — then it is a limb of this PL; the planner
  cites the CR line either way. Up to two sonnet executors after my GO on the rows; every limb
  red first; merges by Mon 9, before the Tue 10 freeze; the FD-1495 limb merges first and
  alone if the rest slip. Working ids at the GO."*
- **S-a's remedy shape, binding.** "2026-11-03 16:19:35 GMT", rulings (2) to (5), verbatim:
  *"(2) S-a's remedy shape, binding on the row: the refusal derives the model's consumed
  Factors from fields the schema actually carries on EACH arm (the GLM's coefficient/term
  names; the GBM's feature list), never from an optional key with an empty default — and an
  EMPTY derived feature set on a fitted model is itself a refusal (fail closed), with a red
  test per arm (GLM and GBM) proving CONTROL_FACTOR_IN_RATEABLE_PATH fires, plus a red test
  that a model whose fit_result lacks the fields refuses rather than compiles. The same
  empty-default read at rating_algorithms.py:142 (`required_model_inputs`) is in S-a's scope —
  same class, same fix. (3) S-a merges first and alone: target Wed 4, hard stop Thu 5; one
  sonnet executor at the GO; full SOLO gate; its DB window takes the next place in the queue
  after the FD-1823 reds (ahead of SL 8296 and SL 8299 — a mispricing fix outranks them). (4)
  FD-1490's remedy is RL-1958 (c) — drop errors.py:323 by Fri 6 — accepted as the planner's
  DP-3 reading; it rides S-b unless S-b slips past Fri 6, then it is its own one-line slice.
  (5) A whole-tree grep for every `fit_result.get(` / `.get("feature_order"` read, quoted in
  the LG, so no third site survives."* *(Amended 2026-11-03 by the planner, before the GO, on
  this entry: S-a's Acceptance 1–6, DP-1, Task 1–2, the row, Acceptance 17 and DP-3. The
  first draft's DP-1 (a), `_model_factors(pin)`, is withdrawn: it read the spec's Factors,
  not the fit's consumed set.)*
  **One premise in that entry differs from the source.** It says the schema defines no
  `feature_order` on `GlmFitResult` *"(or GbmFitResult)"*. `GbmFitResult` does carry it, as a
  required field: `feature_order: tuple[str, ...]` (`model_schema/modelling.py:1768`, class at
  `:1741`). The ruling's shape is unaffected. The GBM arm reads that required field through the
  validated class, not through `dict.get` with a default.
- **The calendar.** "2026-11-03 15:38:58 GMT": code freeze **Tue 2026-11-10**, docs freeze
  **Wed 2026-11-11**, P2 exit demo **Wed 2026-11-18**. The same entry keeps WK-673's close
  audit on its schedule. 16:03:37 accepts WK-673's close target as **Mon 9**. The weekdays
  were read with `date -d <d> +%A`: Thu 2026-11-05, Fri 2026-11-06, Mon 2026-11-09,
  Tue 2026-11-10, Wed 2026-11-18.
- **FD-1495's remaining scope.** `RL-1470` Ruled 8 (the refusal, built by SL-1472) and Ruled 9
  (OQ option (c), the declared reference): *"Ruled 8's refusal stays the default until the
  declared-reference capability lands"*, and *"a spec change FIRST (02 FR-88 and 03 FR-240 …),
  then its own WK-673 slice"* (`RL-1470`, lines 147–185).
- **FD-1490's remedy.** `RL-1958` §"Owners and dates, as ruled" item 1: *"Drop
  `"MONETARY_FLOAT_REFUSED",` from `errors.py:323` … Owner: WK-673. Date: by Fri 2026-11-06 …
  Its merge closes FD-1490."* Item 2 (B9's `Skip` becomes an asserted probe) and item 3 (the
  FR-227 route test) are **WK-1178's**, not this plan's.
- **FD-1481's remedy.** The maintainer's (by delegation) disposition "2026-10-06 00:51:59
  BST", quoted in FD-1481 §"Maintainer's disposition": *"(2) a CHARACTERISATION TEST pinning
  the 15-significant-digit echo at the handler boundary"*, carried by *"the next WK-673 slice
  that touches runtime.py, or a WK-1178 maintenance slice, whichever comes first"*.

## The brief against the record: three corrections

The lead's relay is not the plan's premise (common seat brief item 2). Three of its premises
differ from the primary source.

1. **FD-1495 is not closed. It is live at main on the GLM arm.** The register's partial note
   (`register.md:321`, 2026-10-25) says the HIGH limb is closed by SL-1472 (`7e3a4803`,
   2026-10-08). That was true for a GBM. SL-1463 (`2edc4d89`, #1262, 2026-10-10, a
   descendant of `7e3a4803`) then made a **GLM** score through `model_call`
   (`runtime.py:658-659`). The refusal reads only `fit_result.feature_order`
   (`compile.py:844-848`), and `GlmFitResult` has no such field (`model_schema/modelling.py:1670-1740`).
   The GLM scorer reads **every** Factor of the spec (`runtime.py:929`: `factors = tuple(carried[i]
   for i in spec.factors)`). So a GLM fitted on a `control`-intent Factor compiles, and the
   Factor's coefficient prices. The only GLM test in `test_rating_compile_fr240.py` is the
   seeding test (`:124-137`). Both model_call tests use an `xgboost` fit result (`:178-185`).
   `03` FR-240's 2026-10-08 text is model-type blind: *"a pinned model scored by a
   `model_call` was fitted on it"* (`03-rating-engine.md:140`). So **the code is behind the
   spec, and no spec change is needed.** The mispricing class the lead names is live, and S-a
   is its fix.
2. **FD-1490's remedy withdraws the code. It does not raise it.** The brief asks *"FD-1490's
   remedy raises a registered code — name where"*. `RL-1958` option (c) was ruled on
   2026-10-26. Under it `03:1136` already carries the tombstone *"withdrawn 2026-10-26,
   RL-1958"*, and FR-227 carries the dated clause *"`MONETARY_FLOAT_REFUSED` is not raised"*
   (`03:115`). The owed code is to **remove** `"MONETARY_FLOAT_REFUSED",` from
   `RATING_ERROR_CODES` (`backend/src/app/errors.py:323`). Nothing raises it: `git grep -n
   MONETARY_FLOAT_REFUSED -- ':!docs'` prints only that line. Raising it would contradict a
   ruled spec.
3. **FD-1490's ruled date is earlier than S-b's merge target.** `RL-1958` dates item 1 **Fri
   2026-11-06**, and 16:03:37 sets S-b's merge by **Mon 2026-11-09**. A channel order does not
   amend a ruling's date. DP-3 resolves this. *(Ruled 2026-11-03 16:19:35 (4): FD-1490 rides
   S-b unless S-b slips past Fri 6, and then it is its own one-line slice. Row 2 says so.)*

## FR-364's `rate_table_diffs` limb: not on the exit-demo path, no slice

**Decision (the rule the maintainer set at 16:03:37):** the limb is **not** on the WF-699 /
WF-701 exit-demo path. So it is **"re-owned to P3 by the maintainer's dated line (to-lead
16:03:37)"**, and this plan cuts no slice for it. Cites:

- **CR 8292:209** (§5): the limb is *"PROPOSED: not started — owner WK-673 by the spec; the
  slice row is owed or the obligation is re-owned by a dated line"*.
- **CR 8292:306-310** (FD candidate 2): *"Proposed MEDIUM: off the G2 path (the default
  policy does not name the kind), but the journey states a check the platform does not make."*
- **CR 8292:290** (§5c, WF-699 E2 `:96`): the step's wording *"rate diffs"* **disagrees** with
  the code. That is a wording defect in the journey. It does not put the limb on the path.
- **The code on the path, read at main:** `EVIDENCE_FLOOR["rating_version"]` is
  `("structural_diff", "regression_run", "dislocation_run")` (`model_schema/approvals.py:131`),
  and `DEFAULT_POLICY`'s entry is the same (`:432`). `effective_evidence` is the union of the
  two (`:289-303`). The `rate_table_diffs` verifier refuses only when a policy names the kind
  (`backend/src/app/platform/rating_versions.py:430-435`). `git grep -n rate_table_diffs --
  examples deploy` prints nothing, so the demo seed names it nowhere. **WF-701** names no rate
  diff. Its one evidence cite is the precondition *"An `approved` Rating Version with a complete
  evidence bundle"* (`WF-00701-deploy-and-monitor.md:28`), and that bundle is the floor above.
- **What stays owed, and not here:** the E2 wording correction belongs to FD candidate 2. The
  docs batch 7 auditor files it (16:03:37 item (C): *"FD candidates 1–3 filed"*). The
  re-owning dated line is the maintainer's.

## Goal

Before WK-673's close on Mon 2026-11-09, fix the defects CR 8292 §5b lists as owed code
(FD-1495's GLM arm, FD-1490, FD-1578) and record the proofs it lists as owed (FD-1651, FD
candidate 1, FD-1481's pin). Each limb is red first. FD-1495 is its own slice, so it can merge
first and alone.

## Acceptance Standard

Each item is checkable by the command or read named. "Red at base" means: run at the row's
base, failing by the cause stated, quoted in the slice's `LG-`. A matching status with a
different cause is a plan defect: stop and report.

**S-a (FD-1495), SL &lt;a&gt;**

1. **One derivation, per arm, from carried fields (16:19:35 (2)).** One `pricing-core`
   function returns a pinned model's **consumed feature names**. It lives beside
   `required_model_inputs` (`pricing_core/modelling/factors.py:505`). It validates the stored
   `fit_result` with `FIT_RESULT_ADAPTER` (`model_schema/modelling.py:2072`) and reads only
   fields the class carries:
   - **GBM** (`GbmFitResult`, `:1741`): the required `feature_order` (`:1768`).
   - **GLM** (`GlmFitResult`, `:1670`): the names of `coefficients[*].term` (`Coefficient.term`,
     `:1648`). The term `"intercept"` is excluded (`glm.py:824`, `:873`). A term is either
     `<slug>` or `<slug>[<level>]` (`glm.py:257`, `:1032`), and its Factor slug is the text
     before `[`.
   - **Any other arm, or an unparseable `fit_result`:** a refusal, never an empty set.

   **An empty consumed set on a fitted model is a refusal** (fail closed): an intercept-only
   GLM, or a GBM with `feature_order == ()`. Both use the code
   `CONTROL_FACTOR_IN_RATEABLE_PATH`, raised through `_raise_named`, and the message names the
   model and says that its consumed Factors cannot be derived. No `dict.get("feature_order",
   ())`, and no other optional key with an empty default, remains on any path that feeds a
   refusal or a required-input set.
2. **The refusal uses it.** `_refuse_control_factor_model_calls` (`compile.py:819-855`)
   refuses a `model_call` when any consumed name maps, by slug, to a pinned Factor with
   `intent is FactorIntent.CONTROL`. That covers the pin, each peril component, and a GLM's
   `offset.kind == "model"` source model (`resolved.offset_source`, `compile.py:555-557`). The
   message names the model ref, the feature and the Factor's `slug@version`, as today.
3. **Red tests in `packages/pricing-core/tests/test_rating_compile_fr240.py`** (`@pytest.mark.req("FR-88")`,
   `@pytest.mark.req("FR-240")`). Each is red at base by the stated cause and green after:
   - (a) `test_a_model_call_over_a_glm_fitted_on_a_control_factor_is_refused`: a GLM whose
     coefficients include `<control slug>[<level>]`. Red: `Failed: DID NOT RAISE <class
     'ValueError'>`.
   - (b) `test_a_model_call_over_a_glm_whose_offset_model_is_fitted_on_a_control_factor_is_refused`.
     Red: the same cause.
   - (c) the GBM arm, `test_a_model_call_over_a_gbm_fitted_on_a_control_factor_is_refused`
     (`:188-197`). It is already green at base, so its red is shown on the base with the GBM
     read scratch-broken (`feature_order` read as `()`), then reverted and quoted in LG
     &lt;a&gt;. The test is unedited.
   - (d) `test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused`,
     parametrised over a GLM with no `coefficients` (or intercept only) and a GBM-typed dict
     with no `feature_order`. Red: *DID NOT RAISE* (compile succeeds today).

   Controls, green at base and after: `test_a_model_call_over_a_glm_fitted_on_risk_factors_compiles`
   (new) and `test_a_model_call_over_risk_factors_compiles` (`:201`, unedited). They show the
   refusal is not refusing every model.
4. **`required_model_inputs`'s callers, the same class (16:19:35 (2) and (5)).** Every read
   that feeds `required_model_inputs` a `feature_order` through an empty default uses the
   function of item 1 instead:
   - `backend/src/app/platform/rating_algorithms.py:142`, `_accepted_feature_map_values`, the
     save check;
   - `compile.py:992` (`check_model_call_coverage`) and `compile.py:1059` (`_model_slugs`);
   - `runtime.py:621` (`_required_slugs`).

   `compile.py:844` is item 2's site. A red for `rating_algorithms.py:142` is written beside
   its save-check tests (the executor names the file in LG &lt;a&gt; from its Task 0 grep). A
   `feature_map` on a model whose `fit_result` lacks the fields is refused at save, not
   accepted as an empty map: red at base, green after.
5. **The whole-tree grep (16:19:35 (5)).** LG &lt;a&gt; quotes it at the base and at the head:

   ```bash
   git -C <wt> grep -n -E 'fit_result\.get\(|\.get\("feature_order"|fit_result or \{\}\)\.get\(' -- '*.py'
   ```

   At `a8ef6f19` it prints these non-test sites, read by this plan: `compile.py:844`, `:992`,
   `:1033`, `:1059`; `runtime.py:621`, `:641`, `:1008`; and `rating_algorithms.py:142` (the
   last through the `(row.fit_result or {}).get(` form). At the head, the only remaining
   matches are the `model_type` reads (`compile.py:1033`, `runtime.py:641`, `:1008`). Each of
   those dispatches on a required discriminator and feeds no refusal, and the LG states that
   for each one. `git -C <wt> diff origin/main...HEAD --stat` names no file under
   `docs/specs/`: `03` FR-240 (`03-rating-engine.md:140`) already says it.
6. **Small runs** through `run-small.sh`, each with summary line and rc quoted:
   `test_rating_compile_fr240.py`, `test_rating_peril_scoring.py`,
   `test_rating_glm_model_call.py`, and `test_quote_input_raise_sites.py` (common item 11: a
   `_raise_named` site changes). The DB-backed save-check test of item 4 runs in S-a's DB
   window: **next in the queue after the FD-1823 reds, ahead of SL 8296 and SL 8299**
   (16:19:35 (3)). The GREEN set is extended by import closure (common item 29), with the
   commands and the list quoted in LG &lt;a&gt;.

**S-b (the rest), SL &lt;b&gt;**

7. **FD-1490.** `backend/tests/test_errors.py` has `test_monetary_float_refused_is_withdrawn`
   (`@pytest.mark.req("FR-227")`), asserted by literal name as the neighbour at `:158-165`
   does. It asserts `"MONETARY_FLOAT_REFUSED" not in RATING_ERROR_CODES`, and that
   `PlatformError("MONETARY_FLOAT_REFUSED", …)` raises `ValueError` matching `unknown error
   code` (`errors.py:466-470`). It is red at base by `AssertionError` on the membership, and
   green after the one line `errors.py:323` is removed. `git grep -n MONETARY_FLOAT_REFUSED --
   ':!docs'` then prints only the new test.
8. **FD-1578, the class test.** `packages/pricing-core/tests/test_rating_attribution.py` has
   one test, `@pytest.mark.req("FR-1397")`, over every per-policy `AttributionError` raise in
   `attribute`:
   - the subset no-premium raise at `analysis.py:1129-1133`;
   - the two per-policy `_reconcile` raises (`:1003-1012`, called at `:1147`).

   For each raise it asserts that neither the portfolio's `quote_id` nor the policy's figures
   (`total`, the parts' sum) appear in `str(exc)` or in `safe_error_text(exc)`. It also asserts
   `isinstance(exc, CodedError)`. It is red at base because `"Q000"` is in `str(exc)`.
9. **FD-1578, the existing asserts.** The leak asserts at `test_rating_attribution.py:631`
   (`"Q0" in str(exc.value)`) and `:648` (`"Q000" in …`) are inverted to `not in`. That needs
   **the lead's OK under common item 13, given at the GO** (it changes an assert to match the
   ruled behaviour, FD-1578 §Disposition).
10. **FD-1578, the green.** `class AttributionError(CodedError)` (`analysis.py:521`;
    `CodedError` at `safe_error.py:108`). Its per-policy messages name no `quote_id` and no
    amount (DP-4). The portfolio-level `_reconcile("the portfolio", …)` (`:1157`) keeps its
    aggregate figures: they name no policy (FD-1578 §Finding item 2). After the change,
    `safe_error_text` keeps the message as `ValueError: <message>` (`safe_error.py:213-216`).
    The backend inputs that assumed the type-only rendering move with it, and each is listed
    in LG &lt;b&gt;:
    - the literal raise text at `backend/tests/test_dislocation_runs.py:470-476` becomes
      input-free (item-13 OK at the GO, as item 9);
    - the two reason strings at `backend/tests/test_worker_raise_sites.py:206-219` are
      re-worded (descriptive text, no assert).
11. **FD-1651.** No code changes. The three tests that FD-1651 §Evidence names, in
    `backend/tests/test_rating_version_evidence_floor.py`, are run three times:
    - against the base `rating_versions.py` (green);
    - against a scratch loop that skips an unknown kind, where `verify is None` continues
      instead of raising (`rating_versions.py:450-458`);
    - against a scratch `rate_table_diffs` verifier that returns `{}` (`:430-435`).

    Each scratch edit is reverted, and `git diff --stat` reads empty after the revert. LG
    &lt;b&gt; quotes each failing line by its cause. The auditor quotes that record in FD-1651's
    resolution (LG-1633 is frozen).
12. **FD candidate 1 (SL-1389's owed red-first).** No code changes. The LG-1582 table rows
    2, 5, 6 and 15 (`LG-1582:69-83`) and row 19's gate half are shown red. Each runs on its own
    scratch-broken variant of `rating_versions.py` and is reverted, with LG &lt;b&gt; quoting
    the failure by cause:
    - row 2: limb (2) not called;
    - row 5: `_approximation_gate` not called;
    - row 6: the threshold read from `load_settings()`;
    - row 15: an unset entry read as "no gate";
    - row 19: null read as 0.

    The three "(OWED: scratch-reverted)" docstrings at
    `test_rating_version_dislocation_gate.py:656`, `:696` and `:732` then cite LG &lt;b&gt;.
    That is a docstring-only edit.
13. **FD-1481.** `packages/pricing-core/tests/test_rating_wire_order.py` has a
    characterisation test (`@pytest.mark.req("FR-212")`, the file's marker). It sends the
    float `0.08487199515892163` through a `model_call` and pins the echoed value
    `0.0848719951589216` (the SL-1436 ledger's measurement, `register.md:311`). It is green at
    base: it is a pin. Its red-first proof is a scratch copy that expects the 17-digit input
    back unchanged. That copy fails, showing the 15-digit actual, and is reverted, and LG
    &lt;b&gt; quotes it. No `runtime.py` change.
14. Small runs (DB-free): `test_errors.py`, `test_rating_attribution.py`,
    `test_rating_wire_order.py`. DB-backed runs (items 10's backend tests, 11 and 12) run only
    in a **single-tenant DB window the lead grants in writing** (common items 12, 15, 22, 23).

**Both slices**

15. Each slice's head passes the **full SOLO gate, both halves** (common item 30: each moves
    files outside `docs/`). The gate log is SHA-first and rc-last (common item 37), with the
    skipped count at or below the baseline the lead states.
16. `flock -w 900 /tmp/slots/gate-2 env -C <wt> python3 scripts/audit-docs.py` and
    `scripts/doc-index.py --check` are rc 0 at each minted head. `req-coverage.py` is rc 0.
17. S-a's squash is on `main` first and alone: target **Wed 2026-11-04**, hard stop **Thu
    2026-11-05** (16:19:35 (3)). S-b's squash is on `main` by **Mon 2026-11-09**, and its
    FD-1490 limb by **Fri 2026-11-06** (DP-3, as ruled). Both are before the Tue 2026-11-10
    freeze.

## Global Constraints

- `pricing-core` stays standalone. It never imports FastAPI, SQLAlchemy or Redis, and never
  raises `PlatformError` (`CLAUDE.md` §2; ADR-703).
- Money is integer minor units, or `Decimal` in the rating path, never float (`CLAUDE.md`
  §7). No limb changes a price that a risk-only algorithm produces. S-a only adds a refusal.
- A requirement id is never renumbered (`CLAUDE.md` §5). `MONETARY_FLOAT_REFUSED` stays in
  `03:1136` as the tombstone `RL-1958` wrote. Only the code registry loses it.
- NFR-499 (`03:1589`, clarified 2026-08-30) governs **persistence, not only log output**. It
  is the clause FD-1578's error text breaks, and the one item 8 tests.
- No failing test is removed or weakened without the lead's OK (common item 13). Items 9 and
  10 name the only assert and input changes, and each needs that OK at the GO.
- Scratch-broken variants are never committed. The commit after each proof shows
  `git diff --stat` empty for `backend/src` and `packages/*/src`.
- Never `cd` (planner.md, executor.md). Every command names the seat's own worktree.

## The rows, cut

**Row 1 — S-a (FD-1495): SL &lt;a&gt; / LG &lt;a&gt;.** *A pinned model's consumed Factors
are derived from fields its fit-result class carries on each arm: a GBM's `feature_order`,
and a GLM's coefficient terms. They are never derived from an optional key with an empty
default, and an empty derived set on a fitted model is refused (fail closed). A `model_call`
over a model, peril component or offset model that consumes a `control`-intent Factor is
refused at compile with `CONTROL_FACTOR_IN_RATEABLE_PATH`. The same derivation replaces the
empty-default `feature_order` reads that feed `required_model_inputs`, including the save
check at `rating_algorithms.py:142`. This closes FD-1495's live GLM arm (FR-88, FR-240; the
binding shape of to-lead "2026-11-03 16:19:35 GMT" (2)–(5)).*
- **Scope:** Acceptance 1–6, 15–17.
- **Write set:**
  - `packages/pricing-core/src/pricing_core/modelling/factors.py` (the one derivation);
  - `packages/pricing-core/src/pricing_core/rating/compile.py` (`:844`, `:992`, `:1059` and
    the refusal);
  - `packages/pricing-core/src/pricing_core/rating/runtime.py` (`:621` only);
  - `backend/src/app/platform/rating_algorithms.py` (`:142` only);
  - `packages/pricing-core/tests/test_rating_compile_fr240.py`;
  - the save-check test file for `:142`, named in LG &lt;a&gt; from Task 0's grep.
- **Depends on:** nothing open.
- **Executor:** one, `sonnet`, at the GO.
- **Reds:** DB-free through `run-small.sh`. The save-check red runs in S-a's DB window, next
  in the queue after the FD-1823 reds and ahead of SL 8296 and SL 8299.
- **Gate:** full SOLO, both halves.
- **Merge by:** target Wed 2026-11-04, hard stop Thu 2026-11-05. It merges first and alone.
- **FD closing act:** the auditor closes FD-1495 citing S-a's PR and squash, **only once
  DP-2 is ruled**. Until then the row stays open on the declared-reference limb alone, with a
  dated line.

**Row 2 — S-b (the rest): SL &lt;b&gt; / LG &lt;b&gt;.** *FD-1490's registry entry is dropped
(FR-227, `RL-1958` item 1). `AttributionError` messages become input-free and the class
becomes a `CodedError` (FD-1578, NFR-499). The two FD-1651 broken-loop proofs and SL-1389's
five owed red-first proofs are recorded (FD candidate 1). FD-1481's 15-digit echo is pinned.*
- **Scope:** Acceptance 7–17.
- **Write set:**
  - `backend/src/app/errors.py` (one line);
  - `packages/pricing-core/src/pricing_core/rating/analysis.py` (the class and the two
    per-policy messages);
  - `backend/tests/test_errors.py`;
  - `packages/pricing-core/tests/test_rating_attribution.py`;
  - `backend/tests/test_dislocation_runs.py` (`:470-476` only);
  - `backend/tests/test_worker_raise_sites.py` (`:206-219` only);
  - `backend/tests/test_rating_version_dislocation_gate.py` (three docstrings only);
  - `packages/pricing-core/tests/test_rating_wire_order.py`.
- **Depends on:** nothing open. It shares no file with S-a.
- **Executor:** one, `sonnet`.
- **Reds:** DB-free first. Then one granted single-tenant DB window for Acceptance 10's
  backend runs, 11 and 12.
- **Gate:** full SOLO, both halves.
- **Merge by:** Mon 2026-11-09. **FD-1490 is due Fri 2026-11-06** (`RL-1958` item 1; 16:19:35
  (4)). It rides S-b unless S-b slips past Fri 6. If it does, FD-1490 becomes its own one-line
  slice (Acceptance 7, `errors.py:323` and `test_errors.py`), merged by Fri 6, and S-b loses
  those two files.
- **FD closing acts (the auditor's, each citing S-b's PR and squash):** FD-1490 closed
  (`RL-1958` item 1: *"Its merge closes FD-1490"*); FD-1578 closed; FD-1651 closed, its
  resolution quoting LG &lt;b&gt;'s proofs; FD candidate 1, once batch 7 has filed it, closed
  on the same record; FD-1481 closed (*"the finding stays open until the test merges"*).

The two rows share no file, so the executors may run in parallel. The order is the merge order
only.

## Tasks

### S-a, Task 0 — re-read at the base

Re-read every `file:line` above at the row's base (README convention 4). Run Acceptance 5's
grep, and `git -C <wt> grep -n '_accepted_feature_map_values\|required_model_inputs' --
backend/tests` to find `:142`'s test file. Then run `gh pr list --state open` and read any
open PR that touches S-a's write set. Quote all three in LG &lt;a&gt;.

### S-a, Task 1 — the reds (Acceptance 3, 4)

Write tests (a), (b) and (d) and the GLM control beside `:188-205`. Build the resolver as
`_model_fitted_on` (`:178-185`) does, using the existing `_FactorsResolver`, with a `glm` fit
result whose `coefficients` name `<slug>[<level>]` terms. Mirror `_glm_model`
(`test_rate_table_operations.py`, imported at `:13`) rather than writing a new payload. For
(b), set the offset source on the `ResolvedArtifact` the way compile sets it (`offset_source`,
`compile.py:555-557`). Show (c) red on the scratch-broken GBM read, then revert. Write the
`:142` save-check red. Run the file through `run-small.sh`, and the save-check red in the DB
window. (a), (b), (d) and the `:142` red must fail by the causes stated. Any other failure is
a fixture defect: fix the fixture, never the expectation.

### S-a, Task 2 — the green (Acceptance 1, 2, 4–6)

Write Acceptance 1's derivation in `modelling/factors.py`. Then point the refusal (Acceptance
2) and each `required_model_inputs` caller (Acceptance 4) at it. The refusal message names the
model ref, the feature and the Factor's `slug@version`, and ends *"which cannot be rated on
(FR-88, FR-240)"* as today. The empty-set refusal names the model and the arm. Update the
refusal's docstring: it no longer says that a payload with no `feature_order` binds no factor
(`compile.py:826`). Then run Acceptance 5's grep at the head and Acceptance 6's runs, then
the gate.

### S-b, Task 0 — re-read at the base

As S-a Task 0, for S-b's write set. Also run `git grep -n -E 'AttributionError|quoted in the
baseline' -- backend packages scripts` and quote it, so that every caller and test of the
message is known before it changes.

### S-b, Task 1 — FD-1490 (Acceptance 7)

Red, then remove `errors.py:323`. Common item 26's pre-PR id check is the lead's turn, not
this task's.

### S-b, Task 2 — FD-1578 (Acceptance 8–10)

Red (item 8), then the messages (DP-4), then `CodedError`, **in that order**. FD-1578
§Disposition step 2: promoting the class first would make the allow-list store the quote id.
Then make the item 9 and 10 test changes under the GO's item-13 OK.

### S-b, Task 3 — FD-1481 (Acceptance 13)

The pin, and its scratch red.

### S-b, Task 4 — the DB window (Acceptance 10's backend runs, 11, 12)

Run inside the lead's written grant: `createdb -T` copy, redis db 11–13, START and END lines,
both zeros quoted at the END (common items 15, 22, 23). Run one scratch variant at a time,
and revert each before the next. Then edit the three docstrings.

## Decision points

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-1 | What does the S-a refusal read? | **RULED 2026-11-03 16:19:35 (2), binding:** the consumed Factors per arm from carried fields (GBM `feature_order`; GLM coefficient terms), with an empty derived set refused. Acceptance 1–5 carry it. | The first draft's (a), `_model_factors(pin)` (the spec's Factors), is withdrawn by that ruling. |
| DP-2 | FD-1495's remaining limb, `RL-1470` Ruled 9's declared-reference scoring (a `control` Factor held at a declared value) | (a) carried to P3 by a dated register line, owner named by the maintainer: Ruled 8's refusal stays the default and no price can depend on a `control` Factor after S-a; (b) built in P2: a spec change first (`02` FR-88, `03` FR-240, the transparency clause `02` FR-132), then a code slice | **(a).** `RL-1470` Ruled 9 calls it *"NOT a G2 blocker"* and a new capability. Building it means a spec change, a versioned artifact and a transparency change before Mon 9, against a freeze on Tue 10. It is the maintainer's to rule, and FD-1495 cannot close until it is ruled. |
| DP-3 | FD-1490's date: `RL-1958` says Fri 2026-11-06, and S-b merges by Mon 2026-11-09 | **RULED 2026-11-03 16:19:35 (4):** FD-1490 stays due Fri 6 and rides S-b. If S-b slips past Fri 6, it becomes its own one-line slice. Row 2 carries it. | No re-dating line is needed. |
| DP-4 | How does a per-policy `AttributionError` message point at the failing policy without naming it? (FD-1578 §Disposition step 1 leaves it to the remedy) | (a) it names no policy: it gives the change ids (derived names) and says one policy of the book failed; (b) it gives the policy's ordinal in the sorted compared set; (c) it gives a hash of the `quote_id` | **(a).** The change ids already locate the failing subset, and an operator can re-run locally. (b) is meaningless outside the run, and (c) can be linked back to the policy, which is the leak NFR-499 forbids. If the maintainer wants (b) or (c), it is an `open-questions.md` row first, never a silent pick. |

## Hand-off (not this plan's writes)

- **The register's FD-1495 row** (`register.md:321`): its 2026-10-25 partial note ("the HIGH
  limb … is closed by SL-1472") is wrong at main for the GLM arm. A dated annotation citing
  SL-1463 (`2edc4d89`) and this plan is the auditor's.
- **FD-1495's declared-reference limb:** the DP-2 dated line, the maintainer's.
- **FR-364's `rate_table_diffs` limb:** the re-owning dated line, the maintainer's (16:03:37),
  and FD candidate 2 with the WF-699 E2 wording correction, for docs batch 7.
- **FD-1490's leftovers:** `RL-1958` items 2 and 3 (B9's probe, the `:47` pin, the FR-227
  route test) are WK-1178's, by the exit demo. `journey.py:88`'s
  `"KNOWN GAP B9: FD-1490"` therefore still names FD-1490 after S-b closes it. That is
  `RL-1958` item 4's sequence, not a defect of this plan.
- **The roadmap rows** for SL &lt;a&gt; and SL &lt;b&gt;: the planner's (planner.md Tools line),
  written once the lead allocates the ids at the GO.

## Self-review

- **Every limb red first:** S-a's Acceptance 3 (a), (b) and (d) and the `:142` save-check red
  are reds by cause. 3 (c) is red on a scratch break, and the two controls stay green.
  S-b items 7, 8, 11, 12 and 13 each name a red, and items 11–13 are proofs against a scratch
  variant, because nothing in them is code.
- **Every id listed individually:** FR-88, FR-240, FR-227, FR-1397, FR-212, NFR-499, and
  `02` FR-132 in DP-2 only. No range is written.
- **The brief's own premises checked against the source:** three corrections, above. FR-364
  was decided by the 16:03:37 rule, with the CR lines cited.
- **The four site classes (README convention 5) checked for each ruling's subject:** the
  16:19:35 S-a shape appears in Authority, Acceptance 1–6, Tasks 0–2 and Row 1. DP-3's ruling
  appears in correction 3, Acceptance 17, Row 2 and the DP table. DP-4 appears in Acceptance 10, Task 2 and the DP.
- **Not verified:** nothing was run. The GLM gap is shown by reading three files at
  `a8ef6f19`, and S-a's Acceptance 3 (a) is its proof. FD-1481's echoed value is the SL-1436 ledger's
  measurement, not re-run here.
