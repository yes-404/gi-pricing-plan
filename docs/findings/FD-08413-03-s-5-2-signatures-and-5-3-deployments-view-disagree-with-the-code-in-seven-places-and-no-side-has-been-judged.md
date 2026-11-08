---
id: FD-8413
family: finding
title: 03's §5.2 signatures and §5.3 Deployments view disagree with the code in seven places, and no side has been judged
status: active
created: 2026-11-08
owner: auditor
tree: 374a22bf33ad
corrected_by: []
relates: [FR-218, FR-248, OQ-1285, RL-1329, RL-1628, FD-2034]
---

# FD-8413 — 03's §5.2 signatures and §5.3 Deployments view disagree with the code in seven places

*(Working id 8413, born open, filed 2026-11-08 by the auditor on the P28 recon of module 03 and the §14 review accepted at to-lead "2026-11-08 09:02:21 GMT". Severity LOW: no limb names a wrong number or a price. Owner Work: P3-C.)*

## Finding

`docs/specs/03-rating-engine.md` §5.2 and §5.3 do not match the code at the tree below in seven places. **Which side is wrong is the owning P3 Work's first act, per limb**; this record judges neither side.

- **Predicate and corpus.** One row per (spec locus, code locus) pair whose quoted text differs in name, parameter list, return type or presence, over the §5.2 code block (spec lines 1249–1475), the §5.3 table (1477–1495) and the §4/§5 error-code ids. Counted by hand by the recon; no script run. Count 7. The §5.1 endpoint tables were not re-checked (the review found them clean).
- **Tree.** `374a22bf33ad`. Spec paths and line numbers are at that tree.

| Limb | Spec says | Code does | Consequence |
|---|---|---|---|
| 1 | `03:1487` §5.3 row `Deployments`, `/rating/environments` (the recon cited `:1330`, which is not that row at this tree) | No such route in `frontend/src/router/*.ts`; no view file | A declared view does not exist. **OQ-1285** asks whether it duplicates `07` §5.3's `/admin/environments`. `docs/roadmap.md:1409` (dated 2026-10-03, `PL-1371` §9 DP-2 (a)) moves WK-675 Slice 12, the Deployments view, to Phase 3: **a later-phase view, so a spec-only note, no code now** (`CLAUDE.md` §0). It waits on OQ-1285. |
| 2 | `diff_traces(base: Trace, comparison: Trace) -> TraceDiff` (`:1471`) | `rating/trace_diff.py:50` adds `base_algorithm`, `comparison_algorithm` | A caller copying the spec gets a `TypeError`. Sole backend caller `backend/src/app/api/score.py:698`. |
| 3 | `money.py`: `reconcile_ladder(risk_premium_minor: int, steps: list[tuple[str, int]]) -> bool` (`:1323`) | `rating/ladder.py:417` `reconcile_ladder(ladder: Sequence[LadderRung], inputs: LadderInputs) -> bool`; `money.py` defines only `apply_factor` | Wrong module and wrong parameters. The spec note at `:1321` (RL-879) predates the RL-1329 amendment. |
| 4 | `inline_mounts(algorithm, fragments)` (`:1259`) | `rating/inline.py:235` adds `purpose: str \| None = None`; `mounted_fragments` (`:190`) and `selected_purposes` (`:229`) are public and absent from §5.2 | FR-218 / RL-1628 behaviour sits only in a comment. |
| 5 | `bundle_hash(graph, pins) -> str` (`:1254`) | `rating/compile.py:676` adds `purpose_graphs: Mapping[str, JdmGraph] \| None = None` | A hash call written from the spec omits purpose graphs and yields a different bundle hash for a purpose-mounting version. |
| 6 | `to_wire(graph, payloads=None)` (`:1268`) | `rating/runtime.py:561` adds keyword-only `guards` | Undocumented in §5.2. The recon did not grep the rest of the spec for `guards`. |
| 7 | `extract_relativity_table(model, *, value_name=...)` (`:1341`) | `rate_tables/operations.py:161` adds `factor: str \| None = None` | The spec's RL-1361 note mentions `factor` only for `seed_from_model`. |

**Observations, not counted.** `RATE_TABLE_PARQUET_UNBUILT` (spec `:1202`, a 501 code "until W10-3") is named nowhere under `backend/src`, `packages/pricing-core/src` or `packages/model-schema/src`; the recon did not trace a 501 path under another name. Whether the exposure-weight column sits in the editor grid or only in `RateTableDiffPanel.vue:280` (the spec lists it as an editor element) was not settled. Both are for the P3-C first act.

## Evidence

The recon is `~/gi-pricing-plan.local/scratch/p28/recon-03.md` (local, not committed). The auditor re-read, at `374a22bf33ad`, the `def` lines of `diff_traces`, `reconcile_ladder`, `inline_mounts`, `bundle_hash`, `to_wire` and `extract_relativity_table` with `git grep -n -E "^def (diff_traces|reconcile_ladder|inline_mounts|bundle_hash|to_wire|extract_relativity_table)\(" 374a22bf33ad -- packages/pricing-core/src/pricing_core`; each file and line matches the table. The route absence of limb 1 and the spec quotations were taken from the recon.

## Disposition

**deferred with an owner: P3-C.** The Work's first act is, per limb, to decide which side was wrong, then amend the spec (§5.2 text, with a dated line) or the code. Limb 1 waits on OQ-1285 and is a Phase 3 view. Nothing here is a mispricing; the only limb with a price-adjacent effect is limb 5 (a different bundle hash), and the code is the side the platform runs.
