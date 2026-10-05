---
id: RL-9586
family: ruling
title: WK-1250 Slice 2 decided — a pinned sub-graph is re-inlined at load behind a node-id check, and its port map, the separator __, token renaming and codes are fixed
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # working id; the mint date is set at the mint (check 31)
owner: decision-maker
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-1250
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1309, RL-1344, PL-1254, SL-1340, FR-212, FR-217, FR-244, FR-258, FR-274]
---

# RL 9586 (working id) — WK-1250 Slice 2: DP-S2-1 and DP-S2-2 decided

## How this was ruled

- **The decisions are not this record's.** They are the maintainer's, by delegation, in the
  entry headed *"2026-10-05 16:54:17 BST — CLEANUP NOW (the maintainer chose "now, before lane A
  starts", window to ~17:20 BST); the missing 16:47 slot order; WK-1250 S2 DPs and the
  DOUBLE-COUNT DP RULED"* in `~/gi-pricing-plan.local/channel/to-lead.md`, its "WK-1250 S2"
  part, verbatim:

  > WK-1250 S2 (handover/dp-memo-wk1250-s2-2026-10-05.md):
  > - DP-S2-1: (a), re-inline at load, WITH C1: load_bundle refuses BUNDLE_COMPILE_FAILED when the graph's node ids and the re-inlined step ids differ, red first.
  > - DP-S2-2: shape (a), completeness and codes as recommended. The SEPARATOR is `__`, not `/` (`/` is FR-244's division token; _check_division_guards, compile.py :273/:282, would refuse every inlined expression naming an internal value). mount_point matches ^[A-Za-z][A-Za-z0-9_]*$ and contains no `__` (VALIDATION_FAILED); collision checks cover the parent's step ids and the to_wire-derived keys. The inliner renames by FR-244 TOKEN through a shared vocabulary._tokenize helper, never by substring, with 2 red tests (an internal name in an expression; `ncd` vs `ncd_years`). vocabulary.py joins the write set. 03 §4.11's example is corrected in the DM's T-text.

- **The decision points** are PL 9610's (working id, #1170, branch `pl-9610-wk1250-s2-leaf` at
  `ca407ed9c7d296a676a0bbc248d5ce6706a40f59`), §"Decision points". The DP memo the ruling
  names is `~/gi-pricing-plan.local/handover/dp-memo-wk1250-s2-2026-10-05.md` (a local file).
- **Written 2026-10-05 17:02 BST (by `date`)**, by the decision-maker session `dm-finals2`, on
  the lead's order. Every fact below was read at `origin/main`
  `137bc817ef1fb40ea57e9053e0ad40b73bdff3a8`, by symbol with its line at that tree. PL 9610 is
  unminted, so it is cited in working-id form and kept out of `relates:` (check 32).
- **This record rules a plan's decision points and never edits the plan** (`document-ids.md`
  §1.6, PL row). Its texts for PL 9610 (P1 to P4) are applied by the planner as a pre-mint edit,
  or carried by the dispatch record if the plan is minted first. P5 is **proposed by the DM, not
  in the 16:54 ruling: for the ACK.**

## Locators — read at `137bc817`

| Fact | Where |
|---|---|
| FR-244's name token is `[A-Za-z_][A-Za-z0-9_]*`, and `/` is an operator | `packages/pricing-core/src/pricing_core/rating/vocabulary.py` `_NAME` `:41`, `OPERATORS` `:20-25`, `_tokenize` `:49` |
| FR-274's save-time guard refuses any expression text containing `/` without a guard marker | `compile.py` `_check_division_guards` `:273`, the test at `:282` |
| `load_bundle` runs the engine from the stored `bundle.graph`, and takes `algorithm` from `resolved_payloads[algorithm_ref]` for `check_step_refs_pinned`, `_load_boosters`, `_model_call_handler` and `CompiledBundle.algorithm` | `runtime.py` `load_bundle` `:646` |
| `_model_call_handler` routes on `steps_by_id` from one algorithm; `_build_trace` skips any engine entry whose id is not an algorithm step | `runtime.py` `_model_call_handler` `:512`; `score.py` `_build_trace` `:781`, `:788-794` |
| `to_wire` derives engine keys from a `step_id`: `{id}_e`, `{id}__violated`, `{id}__before`, `{id}__min`, `{id}__max`; and reserves `__exact_reads` / `__exact__` | `runtime.py` `:67-68`, `_expression_node` `:163`, `:278`, `:308` |
| Name-bearing step fields: `consumes`, `produces`; `key_expr` (table, lookup); `expr` (expression); `feature_map` values (model_call); `condition` and `clamp_bounds` values (constraint) | `packages/model-schema/src/model_schema/rating.py` `RatingStepBase` `:258`, `:277`, `:285`, `:293`, `:298`, `:316` |
| `SubGraphRef` is `ref` plus `mount_point: str`, with no pattern | `rating.py` `class SubGraphRef` `:342-352` |
| The codes are registered: `RATING_GRAPH_UNRESOLVED_REF`, `RATING_TYPE_MISMATCH`, `RATING_VERSION_UNPINNED` and `BUNDLE_COMPILE_FAILED` in `RATING_ERROR_CODES`; `VALIDATION_FAILED` as a platform code | `backend/src/app/errors.py` `RATING_ERROR_CODES` `:310-322`, `:401` |
| `to_wire` wires each consumed name to the producer seen so far **in node order**; a name not yet seen is wired to `inputNode`. `to_jdm` inserts nodes in `algorithm.steps` order | `runtime.py` `to_wire` `:412`, `produced_by` `:472-492`; `compile.py` `to_jdm` `:477` |

## Ruled

**Decided by the maintainer, by delegation, 2026-10-05 16:54:17 BST (quoted above).**

| DP | Ruling |
|---|---|
| **DP-S2-1** | **(a), re-inline at load.** `load_bundle` rebuilds the inlined algorithm with the same pure inliner `compile_bundle` uses. `Bundle`'s shape is unchanged. **C1:** `load_bundle` refuses with `BUNDLE_COMPILE_FAILED` when the set of `bundle.graph` node ids differs from the set of the re-inlined algorithm's `step_id`s, naming the first difference, before it builds the engine. Red first. A bundle with no mounts passes by identity |
| **DP-S2-2, shape** | **(a)**: `SubGraphRef.inputs: dict[str, str]` (port → parent value) and `SubGraphRef.outputs: dict[str, str]` (port → parent name), `extra="forbid"` |
| **DP-S2-2, completeness** | Every input port is mapped exactly once; the output ports mapped are a non-empty subset. An unmapped output port is legal; a parent step consuming one is refused by FR-212 |
| **DP-S2-2, separator** | **`__`**, not `/`. Every fragment `step_id`, and every fragment name that is not a mapped port, becomes `f"{mount_point}__{name}"` |
| **DP-S2-2, `mount_point`** | Matches `^[A-Za-z][A-Za-z0-9_]*$` and contains no `__`, else `VALIDATION_FAILED` |
| **DP-S2-2, collisions** | A namespaced name or step id equal to a parent name, a parent `step_id`, or a key `to_wire` derives from a `step_id` (`<id>__violated`, `<id>__before`, `<id>__min`, `<id>__max`) is refused with `VALIDATION_FAILED`; a `mount_point` clash likewise |
| **DP-S2-2, renaming** | **By FR-244 token, never by substring**, through a shared helper over `vocabulary._tokenize`. Only `_NAME` tokens that are fragment names are renamed, never a function or a literal word. Every name-bearing field is covered: `consumes`, `produces`, `key_expr`, `expr`, `condition`, `clamp_bounds` values, `feature_map` values. Two red tests: an internal name inside an expression; `ncd` beside `ncd_years`, where only the exact name is renamed |
| **DP-S2-2, codes** | An unmapped or undeclared port → `RATING_GRAPH_UNRESOLVED_REF`; an incompatible input type → `RATING_TYPE_MISMATCH`; a sub-graph not pinned → `RATING_VERSION_UNPINNED`; a nested mount → `VALIDATION_FAILED`; a `mount_point` clash or a namespacing collision → `VALIDATION_FAILED`. No new code; `errors.py` is not edited |
| **Write set** | `packages/pricing-core/src/pricing_core/rating/vocabulary.py` joins PL 9610's write set (the shared tokenizer helper) |
| **`03` §4.11's example** | Corrected by T2 below: the worked namespacing of the §4.11 fragment under the §4.1 mount |

## The spec texts

**T1 and T2 do not land in this PR.** They describe behaviour, so they land in one commit with
the code (`CLAUDE.md` §2), applied by WK-1250 Slice 2 (`SL-1340`) as its Task 1. Each find string
has exactly one hit at `137bc817`.

### T1 — `03` §4.1, the mount in the example (`03:283`)

Find `` "sub_graphs": [{"ref": "sub_graph:ncd-ladder@4", "mount_point": "s_ncd"}] `` and replace it with:

```json
  "sub_graphs": [{"ref": "sub_graph:ncd-ladder@4", "mount_point": "s_ncd",
                  "inputs": {"ncd_years": "ncd_years"}, "outputs": {"ncd_factor": "ncd_factor"}}]
```

The port names are the §4.11 fragment's (`03:830-831`). `s_ncd` stays: it matches the
`mount_point` pattern, and no parent step is called `s_ncd`, so PL 9610 Task 1's conditional
rename to `m_ncd` is not needed. Like the example's other steps, it shows the shape, not a
complete FR-212 graph: the example's own `postcode_outcode` and `payable_premium_pre_round` are
not produced by any step either, and are not this ruling's.

### T2 — `03` §4.11, the namespacing bullet. Find `` so a fragment cannot mount another: depth is 1. `` and insert after the end of that bullet's line, as a new bullet

```markdown
- **Inlining and namespacing** *(added <date>, WK-1250 Slice 2, RL 9586 (working id))*. At compile, a pinned mount is inlined at its `mount_point` (FR-217). Every fragment `step_id`, and every fragment name that is not a mapped port, becomes `<mount_point>__<name>`: `__`, not `/`, because `/` is FR-244's division operator. A mapped input port's name becomes the parent value it is mapped to, and a mapped output port's name becomes the parent name it is mapped to. Names are renamed by FR-244 token in every field that holds one (`consumes`, `produces`, `key_expr`, `expr`, `condition`, the values of `clamp_bounds` and `feature_map`), never by substring. A `mount_point` matches `^[A-Za-z][A-Za-z0-9_]*$` and contains no `__`. Mounted under §4.1's example, this fragment's step `s_ncd` becomes `s_ncd__s_ncd`; it consumes the parent's `ncd_years` and produces the parent's `ncd_factor`. Compile refuses an unmapped or undeclared port (`RATING_GRAPH_UNRESOLVED_REF`), an incompatible input type (`RATING_TYPE_MISMATCH`), a mount whose sub-graph is not pinned (`RATING_VERSION_UNPINNED`), and a `mount_point` that breaks the pattern, clashes, or produces a namespaced name equal to a parent name, step id or engine-derived key (`VALIDATION_FAILED`).
```

## The texts for PL 9610 (applied by the planner, pre-mint)

Each find string has exactly one hit in PL 9610 at `ca407ed9`.

- **P1 — Task 3, Step 1, namespacing.** Find `` `f"{mount_point}/{name}"` under DP-S2-2's separator; `` and replace it with
  `` `f"{mount_point}__{name}"` (RL 9586, the separator `__`), renamed by FR-244 token in every name-bearing field, never by substring; ``.
- **P2 — Task 3, Step 1, the two token tests.** Find `` - **collisions:** a namespaced name equal to a parent name → refused (DP-S2-2); `` and insert after it:
  `` - **token renaming** (RL 9586): an internal name inside an `expr` is renamed and the expression passes `_check_division_guards`; with `ncd` and `ncd_years` both present, only the exact token `ncd` is renamed; ``
- **P3 — File contention, a row for `vocabulary.py`.** Find the row
  `` | `packages/pricing-core/src/pricing_core/rating/inline.py` | **new**: the pure inliner (Task 3) | none | Not shared | ``
  and insert after it:
  `` | `packages/pricing-core/src/pricing_core/rating/vocabulary.py` | the shared tokenizer helper the inliner renames with (RL 9586) | the dispatch record checks in-flight plans for `vocabulary.py` | An existing-module edit. The dispatch record names it | ``
- **P4 — Task 5, Step 4, C1.** Find `` `_load_boosters`. Update its docstring. `` and replace it with
  `` `_load_boosters`. Then C1 (RL 9586): refuse with `BUNDLE_COMPILE_FAILED` when the set of `bundle.graph` node ids differs from the set of the inlined algorithm's `step_id`s, naming the first difference, before the engine is built; red first, on a bundle whose graph has one node renamed. Update its docstring. ``
- **P5 — PROPOSED BY THE DM, NOT IN THE 16:54 RULING: FOR THE ACK.** Task 3, Interfaces, the
  inlined step order. Find
  `` has `sub_graphs == []` and the parent's steps followed by each mount's namespaced steps, in ``
  and replace that line and the next (`` mount order. It is a proposal name, recorded in the ledger if it differs. ``) with:
  `` has `sub_graphs == []`, and its steps in a stable topological order: the parent's order, with each mount's namespaced steps inserted before the first step that consumes any of its outputs. It is a proposal name, recorded in the ledger if it differs. ``
  with a red test that scores `03` §4.1's shape through `load_bundle` and asserts that the parent
  step consuming `ncd_factor` reads the fragment's value. **Why:** `to_wire` wires a consumed
  name to the producer seen so far in node order (Locators, last row). With the mount's steps
  appended after the parent's, a parent step consuming a mount output is wired to `inputNode`
  and does not read the fragment's value. This is by code reading at `137bc817`; nothing was
  run. Whether `to_wire` should itself sort topologically, for an authored algorithm listed out
  of dependency order, is **not ruled here**: it goes to the maintainer separately.

## What it obliges

- **PL 9610's planner** applies P1 to P4 as a pre-mint edit to #1170, and P5 only if the ACK
  accepts it. The plan's DP-S2-1 and DP-S2-2 rows then cite this record. Activation need 2
  ("DP-S2-1 and DP-S2-2 ruled by an `RL-`") is met at this record's mint.
- **WK-1250 Slice 2 (`SL-1340`)** applies T1 and T2 verbatim in its Task 1 spec commit, with its
  code (`CLAUDE.md` §2).
- **The dispatch record** names `vocabulary.py` in the write-set check.

## Acceptance — the violation that must become detectable

Each is red first in Slice 2:
1. *A fragment whose `expr` names an internal intermediate is refused at compile.* Under `/` it
   is refused `EXPRESSION_UNGUARDED_DIVISION`; under `__` it compiles and prices.
2. *Renaming touches a name that merely contains a fragment name.* The `ncd` / `ncd_years` test
   fails.
3. *`load_bundle` scores a bundle whose graph and re-inlined algorithm disagree.* C1's test, on a
   graph with one node renamed, expects `BUNDLE_COMPILE_FAILED`.
4. *A `mount_point` such as `a__b` or `9x`, or one producing a name equal to `<parent id>__violated`,
   is accepted.* Each is refused with `VALIDATION_FAILED`.
