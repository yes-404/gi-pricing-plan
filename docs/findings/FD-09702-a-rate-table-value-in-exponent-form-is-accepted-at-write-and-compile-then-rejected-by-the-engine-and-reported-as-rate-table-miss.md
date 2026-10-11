---
id: FD-9702
family: finding
title: A rate-table value in exponent form is accepted at write and compile, then rejected by the engine at scoring and reported as RATE_TABLE_MISS
status: active
created: 2026-10-11
owner: auditor
tree: 4af5997e14861bafda4685730180233db54dc243
corrected_by: []
relates: [WK-1178, SL-1526, LG-1641, FR-228, FR-234, FR-255]
---

# FD-9702 — an `E`-form decimal the engine cannot parse, and the wrong code it is reported under

Found by SL-1526 (LG-1641) on its 2 000-row seed fit. Filed from the lead's entry "2026-10-11 19:25:28 BST — SL-1526 (D) result: NO row dropped; a PLATFORM defect (exponent-form decimals the engine cannot parse) → FD, MEDIUM, owner WK-1178" (`to-lead.md`, a local channel file, cited by its header), item 1, and corrected by the lead's entry "2026-10-11 19:38:54 BST — CORRECTION of my 19:36:01 item 5 … FD 9702's premise "0 exponent values at 20k" was TRUE". Every `file:line` below was re-read at `origin/main` `4af5997e14861bafda4685730180233db54dc243` on 2026-10-11, not copied from the entry (main moved since the entry: `operations.py` `:160` is now `:166`).

## Evidence

The chain, each link read at `4af5997e`:

1. **Write.** `extract_relativity_table` (`packages/pricing-core/src/pricing_core/rate_tables/operations.py:149`) renders a fitted relativity at `:166`: `value_name: str(Decimal(str(level.relativity)))`. `str()` of a `Decimal` switches to exponent form when the adjusted exponent is below −6, that is for a magnitude under 1e-6. Run at this tree: `str(Decimal(str(1.36e-7)))` is `'1.36E-7'` and `str(Decimal(str(9.9e-7)))` is `'9.9E-7'`; `1e-6` and `2.15e-6` render positionally (`'0.000001'`, `'0.00000215'`). The upper-case `E` is `Decimal`'s own.
2. **Check.** `_value_issue` (`operations.py:290`) tests the value with `Decimal(raw)`, which accepts `'1.36E-7'`. Run at this tree with a `RateTableValue(name="relativity", …)`: `_value_issue({"area": "F", "relativity": "1.36E-7"}, value, ["area"])` returns `None` (no issue), as does the positional `'0.000000136'`. Save, the bulk operations and compile all rely on this check, so the cell is stored and a bundle compiles over it.
3. **Wire.** `to_wire` (`packages/pricing-core/src/pricing_core/rating/runtime.py:282`) writes the stored text into the ZEN decision-table node unquoted: `"o0": str(row[value_column])`. The engine reads the cell as an expression.
4. **Engine.** The engine, probed at this tree through the repository's `zen` binding with `zen.evaluate_expression`: `'1.36e-7'` evaluates (`1.36e-07`), `'0.000000136'` evaluates (`1.36e-07`), `'1.36E-7'` fails with `{"type":"parserError","source":"Incomplete parser output"}`. The engine accepts the lower-case exponent and rejects the upper-case one that `Decimal` produced.
5. **Report.** The failure reaches `_reraise_engine_failure` (`packages/pricing-core/src/pricing_core/rating/score.py:524`), which names `RATE_TABLE_MISS` (`:559-560`) when the failing node directly consumes the output of an `on_miss="error"` table step. In the lead's trace the failing node is `s_premium`, a step that consumes the table's output, which is exactly that case (the author of this essay did not re-run the full trace). The function's docstring states the limit (`:540`): "A failing step that itself directly consumes such an output, and fails for another reason, still reports the miss code … a wrong diagnosis on a refused quote, never a silent price", pinned by `test_the_stated_residual_still_reports_the_miss_code`. This finding is a live, ordinary instance of that stated limit.

**Reachability.** The values come from `seed_from_model` over a fitted GLM, and a level with no or few claims fits a relativity near zero. The lead's measurement (entry 19:38:54, in-process, with `operations.py`'s exact expression; not re-run by the author of this essay): exponent-form levels are many at 2 000 rows, 2 at 5 000 (`R43`, `R83`), 4 at 10 000, **0 of 56 at 20 000 and 0 on the full book** (min relativity 0.707, the demo-day fit). The seeded 20 000-row relativities lie in 0.86 to 2.1 (entry 19:25:28 item 2). So the defect is reachable on any fit of 10 000 rows or fewer and is not reached by the demo's fits.

## Finding

**Severity MEDIUM (proposed by the auditor; the lead accepts it as the proposal, entry 19:25:28 item 1).** Failure mode **LOUD, never a misprice**: the quote is refused and no price is produced. But any real fit with a separated level, or any value whose `Decimal` text goes to exponent form, publishes a rating version that cannot score, and the refusal carries the wrong diagnosis. Two limbs:

- **(a) The consumer's grammar is not checked where the value is written or compiled.** Neither `extract_relativity_table` (`operations.py:166`) nor `_value_issue` (`:290`) knows that the engine's grammar has no upper-case `E`.
- **(b) The misdiagnosis.** A ZEN parse failure at scoring is reported as `RATE_TABLE_MISS`, a lookup miss, so the author looks for a missing row. The residual at `score.py:559-565` must not relabel an engine parse error as a lookup miss.

## Remedy options (the decision-maker rules)

For limb (a), the lead's recommendation (19:25:28 item 1) is both of: positional notation at every rate-table write (`format(d, "f")`), and a compile refusal of a literal the engine cannot parse, validated at the boundary whose grammar applies (compile), so any path in is caught (defence in depth). For limb (b), the residual must stop reporting `RATE_TABLE_MISS` for a node error that is not a lookup miss; `score.py:540-546` says closing it needs a wire-level change that makes the translation itself fail gracefully.

## Disposition

**Owner: WK-1178, fix before close.** Decision: `fix before close with an owner: WK-1178`; a fix slice planned under WK-1178, not on the G2 path (the demo's fits have no exponent-form value). Event that next confirms or discharges it: a merged slice with a red-first test that an exponent-form value is refused or written positionally, and a test that a ZEN parse error is not reported as `RATE_TABLE_MISS`. Rides D13. Filed by the executor from the lead's entries, 2026-10-11; the lead gives the verdict.
