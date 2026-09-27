# NFR-492 measurement — WK-671 Task 1.3, `CompiledBundle`/`load_bundle`

Measured 2026-08-29 against this branch's `packages/pricing-core/src/pricing_core/rating/
compile.py` (`compile_bundle`) and `runtime.py` (`load_bundle`), on the CI-equivalent
`.venv` this worktree built with `uv sync --all-packages`. NFR-492
(`docs/specs/03-rating-engine.md:780`): compile time **< 60 s** and serialised `Bundle`
size **< 500 MB**, "for a real large structure". Per Task 1.3's own instruction, measured
once 1.1 and 1.2 make a real Rating Version compilable — this is that measurement, on
`compile_bundle()` proper, not an estimate.

**Method.** A throwaway script (not committed — `docs/research/zen-evaluate-concurrency.md`
established the precedent of a spike script living outside the repository), built to be
"real large" on both axes NFR-492 cares about independently: many rating steps (so
`to_jdm`'s translation and the JSON round-trip have real work to do) and a GBM booster big
enough that its own serialised size dominates, the way a real fitted model's would.

- 153 rating steps: 12 `input` steps, one `model_call` (GBM), 139 chained `expression`
  steps, one `output` step.
- A real, trained XGBoost booster: 12 features, 300 trees, max depth 6, fit on 5,000
  synthetic rows — not a toy 3-tree fixture. Persisted the same way `fit_gbm` does
  (`bytes(booster.save_raw(raw_format="json"))`), then carried inline in the resolved
  payload exactly as Task 1.2's real resolver does (RL-873) — `booster_content`, a
  decoded JSON-text string, alongside the rest of the `Model` dump.
- Timed `compile_bundle(version, resolver)` directly (`time.perf_counter()`), and measured
  `len(bundle.model_dump_json().encode("utf-8"))` for the serialised size — the persisted
  form, per RL-873's reading of the budget ("measured on the persisted form, not an
  in-memory estimate"), not this task's own `load_bundle`/`CompiledBundle`, which is never
  itself serialised (FR-243) and so has no size of its own to measure against this NFR.
- A sanity `async_evaluate()` call after `load_bundle`, confirming the compiled structure
  actually runs end to end rather than merely serialising.

## Result

| Metric | Measured | Budget | Margin |
|---|---|---|---|
| `compile_bundle()` wall time | 8.3 ms (13.1 ms on a colder run) | < 60,000 ms | ~4,500x |
| Serialised `Bundle` size | 1,906,584 bytes (1.82 MB) | < 500 MB | ~275x |
| Booster JSON text alone | 1,843,631 bytes (1.76 MB) | — | 97% of the Bundle's size |

Both halves of NFR-492 pass by a wide margin on this structure. `load_bundle()` itself
(not this NFR's own metric — RL-873 scopes NFR-492 to the persisted `Bundle`, and
`CompiledBundle` is a different, unserialised type) took 94–187 ms across two runs,
dominated by `xgb.Booster().load_model()` on the 1.76 MB booster — recorded here only
because it is the number RL-874's "one deserialisation, not N" property is *about*: paid
once per `load_bundle` call, never per quote.

## Reading the margin, not just the number

**The booster dominates, and boosters scale further than this one does.** 97% of this
Bundle's serialised size is the JSON-text booster, and 300 trees × 12 features is a modest
real-world GBM — thousands of trees and dozens of features is not unusual for a mature
motor peril model, and text encoding (required — `booster_format` has no pickle spelling,
ADR-705) inflates a binary booster's size rather than shrinking it. RL-873 already named
the real ceiling to watch, and this measurement gives it a concrete anchor rather than a
guess: **Redis's own per-value limit is 512 MB**, and a 500 MB Bundle budget leaves only
12 MB of headroom below it. A booster that grew roughly 280x from this run's 1.76 MB — not
a fanciful multiple for a large, mature fleet or motor-liability model with many boosted
rounds — would exhaust NFR-492's budget on the booster alone, before counting a single
rating step. **This is a finding against NFR-492's margin for a large real deployment,
not against this task or against RL-873's ruling**, which already flagged it; recorded
here with a number so a future close-workstream audit does not have to re-derive it.

**Step count scales cheaply by comparison.** 139 chained expression steps added a JSON
round-trip and a `to_jdm` translation over ~150 dict entries, not a multi-second cost —
consistent with `compile_bundle`'s own work being dict/string manipulation with no model
fitting or database I/O on this path (NFR-491). Step count is not the risk this NFR
should be re-measured against; booster size is.

## Scope

This measures `NFR-492` alone, Task 1.3's own assignment in the plan's requirement
coverage table. `NFR-489` (component), `2`, `3`, `7`, `8` and `14` are Task 1.4/1.5's to
measure and record, per that same table — not claimed here.
