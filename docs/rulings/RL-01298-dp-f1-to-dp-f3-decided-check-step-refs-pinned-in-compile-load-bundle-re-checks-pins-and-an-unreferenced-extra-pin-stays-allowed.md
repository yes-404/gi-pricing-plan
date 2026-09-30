---
id: RL-1298
family: ruling
title: DP-F1 to DP-F3 decided — check_step_refs_pinned in compile, load_bundle re-checks pins, and an unreferenced extra pin stays allowed
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 48792023e09cd79c771c2184d6808e378732b76b
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1263, FD-1297]
---

# RL-1298 — DP-F1 to DP-F3 decided: (a), (c), (a)

## How this was ruled

**Ruled at effort `medium`**, under the maintainer's decision by delegation of 2026-09-30
10:28:11 BST (`to-lead.md`, entry headed "DECISION: [the #963 plan's] DP routing; DP-F2 (c) scope
pre-accepted"). That entry reads: "DP-F1..F3 go to the medium-effort DM. They are narrow and
code-local, inside a fix whose shape is already decided". It also reads: "DP-F2 (c) is
pre-accepted as within the fix's scope, if the DM rules it … Its acceptance adds a red-first
case: a pre-fix-style bundle with an unpinned or wrong-version step ref is refused at load."
The session's `$CLAUDE_EFFORT` read `medium`.

**Minted 2026-09-30 as RL-1298** (`doc-id.py next --ref origin/main` = 1298 at `4009de14`);
it was filed under working id 9978.

**Sources.**
- The decision points are those of the WK-1178 fix-slice leaf plan, #963 (working id 9873),
  branch `wk1178-pin-membership-leaf`. I read the plan at `529928cf`, then again at
  `d024eb60`, where its three DP rows (`:272-274`) are unchanged.
- The finding it fixes is `FD-1297` (filed as #961 under working id 9977, severity high;
  read at head `f78d4340`).
- The plan is not minted, so it is cited as prose.

## Verified first, at 48792023e09cd79c771c2184d6808e378732b76b

Each premise was read in its owning module with `git show 48792023:<path>`.

| Premise | Where | Present? | What the source says |
|---|---|---|---|
| `compile_bundle` never compares a step ref with the pins | `packages/pricing-core/src/pricing_core/rating/compile.py:425-492` | **absent**, as the finding says | `all_refs` is built from the four pin lists only (`:466-472`). No line reads a step's `rate_table_ref`, `reference_table_ref`, `model_ref` or `peril_structure_ref` |
| The new check's insertion point | `compile.py:464` | present | `check_model_reference_mode(version, algorithm)`, followed by payload resolution at `:466` |
| Refusals are coded | `compile.py:421-422`, and `safe_error.py:64` | present | `_raise_named` raises `CodedError(f"{code}: {message}")`, where `class CodedError(ValueError)`. `compile.py:37` imports it |
| `RATING_VERSION_UNPINNED` is already raised at compile | `compile.py:434-443` | present | Raised only for a missing `algorithm_ref` or `pins` |
| zen swallows handler exceptions | `runtime.py:81-121` (docstring at `:85-91`) | present | A raised exception surfaces as a generic `RuntimeError` `NodeError`. `_model_call_failure` returns a sentinel `MODEL_CALL_FAILED: …` (`:119-121`) |
| The GLM handler indexes the payload unguarded | `runtime.py:463` | present | `payload = payloads[ref_str]`, a bare `KeyError` inside the handler |
| The booster loader indexes the payload unguarded | `runtime.py:533` | present | `fit_result = payloads[ref_str].get("fit_result", {})`, a bare `KeyError` in `_load_boosters` |
| `load_bundle` checks nothing about pins | `runtime.py:565-590` | **absent** | It validates the algorithm, then calls `_load_boosters` (`:579`), the handler and `to_wire`. Nothing reads `bundle.pins` |
| `Bundle.pins` is always present | `compile.py:388-401` (the `Bundle` model) | present | `pins: Pins`, which is required, not optional |
| `runtime` may import from `compile` | `runtime.py:50`; `compile.py` imports | present, one way | `from pricing_core.rating.compile import Bundle, JdmGraph`. `compile.py` imports no `runtime` |
| The sentinel becomes a coded raise at score | `score.py:442-443` | present | `if MODEL_CALL_ERROR_KEY in result: raise CodedError(...)` |
| `load_bundle`'s production callers | `backend/src/app/api/score.py:215`, `backend/src/app/worker/rating_handlers.py:175` | present | Both call `load_bundle(bundle)` on a stored or cached `Bundle` |
| Both codes are registered | `backend/src/app/errors.py:298`, `:325` | present | `"RATING_VERSION_UNPINNED"` and `"MODEL_CALL_FAILED"` |
| The `Pins` shape, and its promise | `packages/model-schema/src/model_schema/rating.py:63-76` | present | Four lists. The docstring says "every custom objective reachable from a `model_call` is pinned", reached through a model, never named by a step |
| `check_model_reference_mode` | `model_schema/rating.py:171` | present | Raises a bare `ValueError` in the shared-shape package |
| FR-237 | `docs/specs/03-rating-engine.md:134` | present | "an exact Rate Table Version per referenced table, an exact Model/Peril Structure version per `model_call`, an exact Reference Table Version per `lookup` … Nothing is unpinned." |

## Proof — executable, red on today's `load_bundle`, green on (c)

**Where it ran.**
- The proof is scratch and never committed: `test_dp_f_load_backstop.py`, sha256 prefix
  `f0d6373b17b8847c`, in `/home/puzhenhao1989/.claude/jobs/0081b83b/dm-f-proofs/`.
- It ran in a worktree at `48792023` after `uv sync --all-packages`.
- It uses the real `compile_bundle` and `load_bundle`, and the score fixture
  (`packages/pricing-core/tests/test_rating_score.py`: `_version`, `_FakeResolver`,
  `_rate_table_payload`).

**What it builds.**
- Today's `compile_bundle` does not compare step refs with pins. So a bundle it produces with
  `pins.rate_tables` changed is exactly the "pre-fix stored bundle" of DP-F2.
- The deciding part:

```python
def check_step_refs_pinned(algorithm, pins):          # the DP-F1 (a) contract, written out
    for step in algorithm.steps:
        table/lookup/model_call -> ref, pool (rate_tables / reference_tables / models)
        if ref not in pool: raise CodedError("RATING_VERSION_UNPINNED: step … names … (FR-237)")

def load_bundle_c(bundle):                             # DP-F2 (c)
    check_step_refs_pinned(RatingAlgorithm.model_validate(bundle.resolved_payloads[bundle.algorithm_ref]), bundle.pins)
    return load_bundle(bundle)

LOADERS = {"today": load_bundle, "c": load_bundle_c}   # every test parametrised over both
test_unpinned_table_step_refused_at_load        # pins.rate_tables = []            -> expect CodedError UNPINNED
test_wrong_version_table_step_refused_at_load   # step @1, pin rate_table:…@2     -> expect CodedError UNPINNED
test_control_pinned_bundle_loads                # step @1, pin @1                 -> loads
test_dp_f3_extra_unreferenced_pin_loads         # pins @1 and @2, step names @1   -> loads
```

**Commands and results** (2026-09-30 10:29:39 BST):

```text
$ PYTHONPATH=packages/pricing-core/tests uv run --no-sync pytest -q -p no:cacheprovider --rootdir=$S $S/test_dp_f_load_backstop.py
FAILED …::test_unpinned_table_step_refused_at_load[today] - Failed: DID NOT RAISE CodedError
FAILED …::test_wrong_version_table_step_refused_at_load[today] - Failed: DID NOT RAISE CodedError
2 failed, 6 passed, 34 warnings in 8.52s                        rc=1
$ … -k "not today"
4 passed, 4 deselected, 34 warnings in 6.12s                    rc=0
```

**What the proof shows.**
- Today, a bundle whose `table` step names a ref that is unpinned, or pinned at another
  version, **loads without complaint**. `FD-1297`'s *Evidence* shows what such a bundle then
  prices.
- Under (c), both are refused at load with `RATING_VERSION_UNPINNED`.
- The pinned control loads, and a bundle carrying an extra pin no step names still loads.
  That is the DP-F3 (a) case, `FD-1297` Table 1's "both table v1 and v2 pinned" row.

## Ruled

**DP-F1 — (a).** The comparison is
`pricing_core.rating.compile.check_step_refs_pinned(algorithm: RatingAlgorithm, pins: Pins) -> None`.
- It raises `CodedError` `RATING_VERSION_UNPINNED` on the first mismatch, in step order.
- It is exported in `compile.py`'s `__all__`.
- `compile_bundle` calls it after `check_model_reference_mode` (`:464`), before it resolves
  the pins.
- The rule it enforces: a step ref must be **in its kind's pin list at that exact version**.
  - `table` → `pins.rate_tables`;
  - `lookup` → `pins.reference_tables`;
  - `model_call` → `pins.models`, for `model_ref` or `peril_structure_ref` alike (`03:355`).

Why:
- The refusal is a coded `pricing-core` error, and `runtime.py` can import it one way (see
  the table).
- WK-1250 Slice 2's G1 needs a named function to call, which excludes (c).
- (b) would put a coded rating refusal into the shared-shape package, which raises only bare
  `ValueError`s there. `compile_bundle` would then have to re-code it.

**DP-F2 — (c), with the handler limb dropped** *(amended 2026-09-30, before merge, on
auditor-933's F1 against #963; see "Amendment" below)*.
- `load_bundle` calls `check_step_refs_pinned(algorithm, bundle.pins)` first, before
  `_load_boosters` (`:579`).
- `_load_boosters` (`runtime.py:533`) raises `CodedError` `RATING_VERSION_UNPINNED` naming
  the ref, when a pinned model ref has no payload.
- **The handler (`runtime.py:463`) is not edited and gets no test.** It is unreachable (see
  "Amendment" below).

Why (c):
- (a) and (b) code only the model path. They leave a bundle compiled before this fix able
  to price a `table` or `lookup` step against a missing or wrong-version payload, and that
  is the finding's defect (the proof: it loads today).
- The check is one pass over the steps, with no I/O, so NFR-491 holds.
- It reuses DP-F1's function.
- `Bundle.pins` is always present.
- The maintainer pre-accepted it as within scope (10:28:11).

(b)'s extra text inside the sentinel is not ruled: it only changes the handler, which the
amendment below finds unreachable.

**Amendment — the `:463` limb (2026-09-30, before merge).** auditor-933's #963 audit (F1)
reported that the handler site is unreachable. I verified it at `48792023`
(`git diff --quiet 48792023 origin/main -- packages` → rc 0 at 10:35 BST):
- `_load_boosters` runs `fit_result = payloads[ref_str].get("fit_result", {})` (`:533`)
  for **every** `model_call` step, before it looks at the model type (`:534-535`).
  `load_bundle` calls it (`:579`) before it builds the handler (`:580`).
- `CompiledBundle(` is constructed only in `load_bundle` (`runtime.py:587`), by
  `git grep -n "CompiledBundle(" 48792023 -- packages backend/src`, excluding `tests/`.
  `_model_call_handler(` is called only at `:580` outside tests.
- Probe, scratch file `probe_463.py`, run at 10:35:00 BST. It takes a `compile_bundle` of the
  score fixture, deletes every `model:*` key from `resolved_payloads`, and calls
  `load_bundle`. Its output:
  - `glm KeyError 'model:motor-freq-glm@1' at runtime.py:533 in _load_boosters`
  - `gbm KeyError 'model:motor-freq@1' at runtime.py:533 in _load_boosters`

  So a GLM model's missing payload never reaches the handler either.

**Ruled on the limb: (i), drop the `:463` edit and its test.** Four reasons:
- The only code path to the handler is through `load_bundle`. That path refuses first,
  twice: at the new pin check, and at `:533` for a pinned ref with no payload.
- A test for `:463` would have to hand-build a `CompiledBundle` that no production code can
  build. It would prove a branch no quote can take.
- Option (ii), defence in depth, was weighed. Its only benefit is if a future change made
  `_load_boosters` skip non-GBM models. That change would itself move the `:533` guard, and
  it is the change's own reviewer's to see.
- The maintainer's condition ("any coded outcome") is met at `:533` and by the load check.

**DP-F3 — (a).** A pin that no step references is **not** refused by this slice.

Why:
- FR-237 (`03:134`) requires every reference to be pinned, not every pin to be referenced.
- `Pins`' own docstring pins custom objectives "reachable from a `model_call`". No step names
  them, so (b) would need an exemption the spec does not state.
- A second rule is a spec change first (`CLAUDE.md` §0), not a slice's choice.
- The proof's last test is the (a) behaviour, and it stays green under (c).

**Departure from the recommendations: none.** The plan recommends (a), (c) and (a), and this
record rules the same.

**Not touched here.** The `??` operator and `03` FR-244 are a separate `CLAUDE.md` §0 question held for
the decision-maker at effort high. This record says nothing about `_GUARD_MARKERS`,
`_check_vocabulary` or any expression handling.

**Narrowness: narrow.**
- It changes no FR text and no published contract: no schema, no route, and no new error
  code, since both codes are registered.
- `03` §5.1's meaning line for `RATING_VERSION_UNPINNED` is the plan's Task 2, already inside
  the maintainer's decided scope (`FD-1297`, *Disposition*).
- One effect is disclosed: under (c), a stored bundle with an unpinned or wrong-version step
  ref stops loading. `FD-1297` (at `f78d4340`, *Sweeps*, auditor-922 at `eeda8f4b`) reports the
  sweep's result:
  - PostgreSQL: 0 such bundles.
  - MinIO: 6519 bundle JSONs across its buckets, 0 with a graph step ref outside their pins
    or `resolved_payloads`.
  - One gap is stated, not counted as zero: 3986 algorithm-shaped blobs in `gip-test-blobs`
    carry no pins, so they cannot be checked on their own.

  Refusing such a bundle is the intended outcome, because otherwise it would misprice.

## What it obliges

The WK-1178 fix slice (#963's plan):
- **Task 2:** DP-F1 as ruled.
- **Task 3:** DP-F2 (c) as amended: the `load_bundle` call and the `:533` code; the `:463` handler step and its test are dropped.
- **Acceptance 4:** DP-F3 (a)'s control row.

The ledger records the resolutions by this record's id (Task 0). This commit edits no spec,
plan or roadmap text.

## Acceptance — the violation that must become detectable

In the slice's own suite, each item is shown red first.
- *Violation: a pre-fix-style bundle (built without the compile check) whose step ref is
  unpinned is accepted by `load_bundle`.* This is the maintainer's red-first case (10:28:11),
  and it must raise `RATING_VERSION_UNPINNED`.
- *Violation: the same, with the step ref pinned at another version* (step `@1`, pin `@2`).
- *Violation: `compile_bundle` accepts either case.*
- *Violation: `_load_boosters` raises a bare `KeyError` for a missing payload,* for a GBM
  and for a GLM model. The fixture is a hand-built `Bundle` whose pins include the ref and
  whose payloads lack it, so it passes the `load_bundle` check and reaches `:533`. No test
  targets the handler (`:463`): the amendment above finds it unreachable.
- *Violation: a bundle with an extra, unreferenced pin is refused* (DP-F3 (a)'s control).
