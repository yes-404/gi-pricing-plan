---
id: RS-1930
family: research
kind: audit
title: S2 (WK-1178, FD-1610 limb 2) slice audit at 84aadaec — TraceStep.dropped_inputs (d), MODEL_CALL_REQUIRED_INPUT_ABSENT (c), the boundary zero of S2-C0
status: draft
created: 2026-10-26               # drafted 2026-10-25 under working id 8247
owner: auditor
tree: ee6f22e3a9d69a881ac332afa209c353e22e0d35
phase: P2
work: WK-1178
corrected_by: []
relates: [LG-1929, PL-1927, FD-1610, FR-222, FR-239, FR-255, FR-240, NFR-499]
---

# RS-1930 — S2 slice audit (FD-1610 limb 2, `draft/s2-fd1610` @84aadaec)

*(Working id 8247, written by `aud-s2` (auditor, sonnet, effort medium), 2026-10-25, from `brief-aud-s2-2026-10-25.md` (lead 28). Check 31/32 on this id and on the slice's own working ids (LG-1929, PL-1927) are expected until the mint. No test, gate, DB or docker command was run by this seat; only `git`, `grep`, `ruff format --check`/`--diff` (read-only) and file reads.)*

## Question

Does `merge-base(84aadaec, origin/main)...84aadaec` meet the scope the maintainer ruled in to-lead "2026-10-25 11:40:12 GMT" ((d) then (c)), "11:53:23 GMT" (DP-S2 (i)/(i)/(i)), "22:16:18 GMT", "22:26:43 GMT" and "22:38:42 GMT" (the C0 grant, its amendment, the boundary-zero ruling) and `PL-1927`'s S2 section (`origin/draft/pl-8227`, `docs/plans/PL-01927-…`, lines 364–372 for S2-C0), and is the evidence in LG-1929 reachable and honest?

## Method

Range: merge-base `102341aade6720dc7b71a1e696cc5b6d8017a2f1` ... head `84aadaec2424ea0f15b92fbd5a05ec3042207214`, tree `ee6f22e3a9d69a881ac332afa209c353e22e0d35`. 11 files, +303/−9 (`git diff <merge-base> 84aadaec --stat`): model-schema `scoring.py`; pricing-core `runtime.py`, `score.py`, the raise-site census test and the new `test_rating_model_call_dropped_inputs.py`; `03-rating-engine.md`; three `docs/contracts/` files; LG-1929; INDEX. Scope was derived from the rulings and PL-1927 first (quoted below), then evidence read by `git diff/show/blame/grep` and plain reads in worktree `aud-s2`. Ancestry by `git merge-base --is-ancestor`. The red/green numbers were read from LG-1929 and from-lead "2026-10-25 22:36 GMT" (`from-lead-2026-10-09.md:8027`); **not re-run** (the gate confirms). Format by `ruff format --check/--diff` on the five S2 `.py` files (read-only) at 84aadaec.

## Scope (derived first)

- 11:40:12: "(d) first: every `feature_map` key the runtime drops … is recorded in the trace as an additive field; price and hash unchanged (FR-239 holds by construction). Then (c): a dropped key that feeds a **required** model input raises a coded, input-free scoring error — only after the essay's exposure query returns 0 … red first for both parts … a dated line under `03` FR-222 for the refusal and one for the trace field; if the trace shape is a `model-schema` type, the field is added there and `docs/contracts/` regenerated, never hand-written."
- 11:53:23 DP-S2 (i)/(i)/(i): "`MODEL_CALL_REQUIRED_INPUT_ABSENT` surfaced through `_model_call_failure` (FD-1753 precedent); the (d) field is `TraceStep.dropped_inputs: list[str] | None` … not compared, with a dated `03` §4.10 line."
- 22:26:43 / 22:38:42: S2-C0 option (1) then (a): "a boundary zero, recorded as such, never as hits=0 … (c) proceeds … the 21:54:12 build-before-C0 is a disclosed line … format split: only S2's own lines in the flagged files."

## Findings

| # | Class | Finding | Evidence |
|---|---|---|---|
| F1 | met | (d): `TraceStep.dropped_inputs: list[str] \| None = None`, ruled type, `None` when nothing is dropped, set only on a `model_call` step | `scoring.py:195` `dropped_inputs: list[str] \| None = None`; `score.py:869-887` `dropped = sorted(name for name in step.feature_map if name not in consumed) if isinstance(step, RatingModelCallStep) else []` … `dropped_inputs=dropped or None`. Test `test_a_step_that_drops_nothing_records_none` asserts `... is None` on `s_risk` and on `s_expense` |
| F2 | met | (d) price and `content_hash` unchanged | `test_tracing_a_dropped_key_changes_neither_price_nor_hash`: `priced_stray.outputs == priced_clean.outputs`, `premium_ladder ==`, `stray.content_hash == clean.content_hash`, `dropped_inputs == [_STRAY]`. The field is written only in `_build_trace`, after pricing; it is read by nothing that prices |
| F3 | met | (c): `MODEL_CALL_REQUIRED_INPUT_ABSENT` through `_model_call_failure`; message names step + graph names, no value (NFR-499) | `runtime.py:~790-805`: `absent = sorted(name for name, slug in step.feature_map.items() if name not in context and slug in required_by_step[step.step_id])` → `return _model_call_failure(step, f"MODEL_CALL_REQUIRED_INPUT_ABSENT: step {step.step_id!r} maps {absent} onto a required model input …", context)`. Required set = `required_model_inputs` (FR-240's compile definition) in `_required_slugs`. Test `test_a_dropped_key_that_feeds_a_required_input_is_refused`: `match=MODEL_CALL_FAILED.*MODEL_CALL_REQUIRED_INPUT_ABSENT`, asserts `"s_risk"` and `"driver_years"` in the message and `str(_AGE)` (47) not in it; a second test repeats it with `trace=True` |
| F4 | met | Catalogue entry and raise-site census 3 → 4 | `03` §5 `MODEL_CALL_REQUIRED_INPUT_ABSENT` entry after `MODEL_CALL_FEATURE_COLLISION`, "(added 2026-10-25 …)"; `test_quote_input_raise_sites.py`: `("rating/runtime.py", "handler"): 3` → `4` with the comment naming the fourth site |
| F5 | met | Red first | `git merge-base --is-ancestor 7231abea 65841ccc` rc 0 ((d)), `… b919b9f1` rc 0 ((c)); 7231abea's parent is `102341aa` (the merge-base), so the red tests precede both code commits. LG: RED @7231abea "5 failed, 22 passed in 8.01s" rc 1 (5 = the five tests of the new file); GREEN @ab7e107b "27 passed in 7.64s" rc 0 and "25 passed in 1.44s" rc 0. Matches from-lead 22:36 line for line |
| F6 | met | `test_trace_diff.py` / `test_scoring_compare.py` stay green at 7231abea: they are regression guards, not missed reds | `trace_diff.py:23-26` compares an explicit allow-list (`consumed`, `produced`, `matched`, `violation`) and `elapsed_us` is excluded, so a new field is "not compared" by construction; they pin that existing behaviour, they assert nothing about the new field and could not go red before it exists. See N1 |
| F7 | met | Spec: dated, append-only | `03` FR-222 row (line 110): the word diff shows additions only; two `*(Amended 2026-10-25, WK-1178, S2, FD-1610 limb 2 (d)/(c), on the maintainer's (by delegation) entries headed "2026-10-25 11:40:12 GMT …" and "2026-10-25 11:53:23 GMT …")*` clauses appended at the row's end. §4.5 (line 647 area): dated field line citing both stamps. §4.10 (line 956): dated "recorded and never compared … derived from fields already compared". §5: dated `(added 2026-10-25 …)` entry. Every cited stamp exists as a heading in `to-lead.md` (lines 30479, 30514) |
| F8 | met | Contracts: hand-authored property matches the model | model `list[str] \| None = None`; generated schema `anyOf [array of string, null]`, default null; hand-authored `scoring.schema.json`: `"dropped_inputs": {"type": ["array", "null"], "items": {"type": "string"}}` — same type and nullability. `docs/contracts/` change is 3 files (`generated.json`, `score-comparison.schema.json`, `scoring.schema.json`); LG: `generate-contracts.py --check` "58 generated contracts match the models" rc 0 @3ffdbe3f |
| F9 | met | C0: boundary zero verbatim, never `hits=0` alone; proof shows `hits=1` | LG-1929: block opens `head=3ffdbe3f787c195e43ebd3f8ae6a17143777d2e8`; proof "rows=1 blobs_read=1 hits=1 required_hits=1" rc 0 in throwaway `s2-pg-3ffdbe3f` + `s2-minio-3ffdbe3f` (planted `driver_years`→`age_years`), `docker rm -fv` rc 0, `ps -a --filter name=s2-` 0/0, dangling volumes 16/16; real run: command (a) rc 0 zero rows, "rows=0 blobs_read=0 hits=0 required_hits=0 rc=0 — a **boundary zero, not hits=0 alone**. exposure on the dev DB: none measurable — 0 compiled rating versions at 3ffdbe3f…; the proof row is the instrument check", bucket `gip-blobs` "named and not read". Matches the 22:38:42 wording. The disclosure line (c built before C0, red at 7231abea precedes b919b9f1) and the dated correction to PL-1927 (blob, not the `bundle` column) are both present |
| F10 | met | Format split (84aadaec) | `git show 84aadaec`: 1 file, +5/−2, only the `_ctx(inputs={…})` dict inside `test_a_dropped_key_that_feeds_a_required_input_is_refused` (S2's own new file). `ruff format --check` on the five files: "3 files would be reformatted, 2 files already formatted"; the residue hunks (`runtime.py` @643/770/837/868/884, `score.py` ten hunks, `test_quote_input_raise_sites.py` seven) are outside S2's added ranges (`git blame`: line 773-775 is `24b537dfe`, main; S2's `required_by_step` 776-779 is not flagged) — main's lines only |
| N1 | N | "Not compared" (§4.10) has no failing case of its own; the claim rests on the allow-list in `trace_diff.py` | no test in `test_trace_diff.py` or `test_scoring_compare.py` feeds two traces differing only in `dropped_inputs`. Suggest one guard (non-blocking: the field cannot enter the compare without editing the allow-list, and the allow-list is itself tested) |
| N2 | N | (c) refuses on the literal ruling ("a dropped key that feeds a required input"): a `feature_map` with two graph names onto one required slug, one present and one absent, refuses though the row holds the slug | `runtime.py` `absent` test is per graph name; no test covers this shape. Matches the 11:40:12 text and the dev-DB exposure is nil (F9), but it is a possible false refusal; record for the maintainer, no change asked |
| N3 | N | Green was not re-run at the head: later commits are `072e7ac5` (docstring E501), `84aadaec` (format of one dict) | LG lines are @ab7e107b / @072e7ac5 / @3ffdbe3f; no behaviour change after ab7e107b (`git diff --stat ab7e107b 84aadaec -- packages` = `test_rating_model_call_dropped_inputs.py` only (+6/−3, docstring and dict format); no `src/` file differs). The gate is the decisive green |
| N4 | N | §4.10 line says the field is "derived from fields already compared, `consumed` and the step's own `feature_map`"; `feature_map` is not in the trace | prose imprecision: the derivation is from the trace's `consumed` plus the algorithm, not two compared trace fields. No behaviour impact |

No blocking finding. `docs/INDEX.md` regenerated under the gate-2 flock with this record.

## Proposed verdict

**CLEAN** (proposed; the lead adopts). Owed to the gate: pytest/mypy/ruff at 84aadaec by the gate (N3), `ruff format --check` residue is main's.
