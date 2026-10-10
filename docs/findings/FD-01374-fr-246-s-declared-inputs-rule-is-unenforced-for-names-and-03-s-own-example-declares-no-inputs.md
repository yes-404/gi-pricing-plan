---
id: FD-1374
family: finding
title: FR-246's declared-inputs rule is unenforced for names, and 03's own canonical example declares no inputs
status: closed
created: 2026-10-03
owner: auditor
tree: 19155b505741317da6967362707f387b39bd2cef
corrected_by: []
relates: [WK-1178, FR-246, FR-244, FR-212]
---

# FD-1374 — FR-246's declared-inputs rule against an engine that never compares a read with `consumes`

**Filed** by auditor-fd9773 on the maintainer's ruling (the entry of `to-lead.md` after 09:34 BST beginning "P5 severity:
MEDIUM"), found by auditor-pl9776's sweep (the F35 plan, PL 9776 (working id)). The `tree:` is `origin/main` at `19155b50`;
every spec, code and sweep figure below was read or re-run at it.

## Finding

**Severity: MEDIUM; owner WK-1178; remedy via PL 9776 (working id).** The maintainer's reason: "a SILENT mispricing path
in shipped code (edges from consumes only, nothing refuses an undeclared read) and the spec's canonical example teaches
it. Not HIGH: 0 exposure today, and G2's algorithm is guarded by its acceptance line."

`docs/specs/03-rating-engine.md:148`, FR-246: "Expression steps cannot reference anything outside their declared inputs — no
globals, no environment, no time-of-day. `now()` does not exist; a quote timestamp is an input." Nothing in the code
enforces the first clause for any step type, and the spec's own example does not follow it.

### The mechanism

- **Compile does not compare identifiers with `consumes`.** `zen.compile_expression` checks syntax and the FR-244 allow-list;
  it does not resolve variables, so a name an expression reads is never matched to a declaration.
- **`RatingAlgorithm._graph_invariants`** (`packages/model-schema/src/model_schema/rating.py:394`) checks `consumes` against
  `produces` only: a consumed name with no producer raises `GraphUnresolvedRefError` (`:419`). It never looks at what a
  step reads.
- **`to_wire` builds edges from `consumes` only**: `edges.append(_edge(produced_by.get(name, _INPUT_ID), step_id))`
  (`packages/pricing-core/src/pricing_core/rating/runtime.py:412`). Every expression node sets `passThrough`
  (`runtime.py:162`, `:256`, `:322`; the rule is stated at `:152`), so an undeclared read resolves from the inherited context. An undeclared read of a name
  an earlier **step** produces has **no ordering edge**: the reader can run before the producer, or be ordered by accident of
  the topological sort.

The result is silent. The rating is computed with a value that was never declared, from whichever context the engine hands the
node. No check, no refusal, and no reason code.

### The spec gap

1. **FR-246's step-type scope is unstated.** It says "expression steps". A `constraint`'s `condition` and `clamp_bounds`, a
   `table`/`lookup` `key_expr` and a `model_call` `feature_map` also read names. The requirement neither covers nor excludes them.
2. **The canonical example declares no inputs.** The example's steps block is `03-rating-engine.md:252-274`; its five
   evaluating steps are `:254-271`, and `s_out` (`:272-274`) is the only step that declares `consumes`. `s_input_age`
   (`:252-253`, an `input` step) reads nothing and declares `produces`, so it is outside the reads question and inside the
   corrected-example range:
   - `s_area` (`:254-257`, `lookup`) has `"key_expr": ["postcode_outcode"]` and no `consumes`. A `lookup`'s `key_expr` is in
     the scope question of item 1.
   - `s_rp` (`:258-261`, `model_call`) has `"feature_map": {"driver_age": "driver_age", "rating_area": "rating_area"}` and no `consumes`.
   - `s_expense` (`:262-264`, `table`) has `"key_expr": ["distribution_channel"]` and no `consumes`.
   - `s_office` (`:265-267`, `expression`) has `"expr": "risk_premium_minor * expense_factor * commission_factor * profit_factor"`
     and **no `consumes`**: an expression step, FR-246's own named case, reading four names with none declared.
   - `s_minprem` (`:268-271`, `constraint`) has `"condition": "office_premium_minor >= min_premium_minor"` and
     `"clamp_bounds": {"min": "min_premium_minor"}` and **no `consumes`**.

   The trace example at `:466-482` shows `s_minprem` consuming `office_premium_minor` and `min_premium_minor`, so the example's
   declaration is what the engine saw at run time; the step as authored declares neither. A reader copying `:252-274` writes
   exactly the undeclared form.
3. **A second defect in the same example: `s_out` consumes a name nothing produces.** `s_out` (`:272-274`) declares
   `"consumes": "payable_premium_pre_round"`. No step in the example produces that name (`s_minprem` produces
   `office_premium_minor`; the only occurrence of `payable_premium_pre_round` in `03` is `:274`). `_graph_invariants`
   (`rating.py:394`) raises `GraphUnresolvedRefError` (`RATING_GRAPH_UNRESOLVED_REF`, `:419`) for a consumed name with no
   producer, so the example would fail the **existing** invariant, before any declared-reads check exists. The corrected
   example must pass both the existing invariant and the new declared-reads check.

## Evidence

**The sweep** is `/home/puzhenhao1989/.claude/jobs/6fa41099/tmp/p5/sweep.py` (auditor-pl9776's, re-run by the filer). Run as
`python3 sweep.py <tree>` over a `git archive origin/main packages backend examples scripts docs/contracts` extract at
`19155b50`.

**Predicate, in words.** A *step* is every dict literal in a tracked `*.py` with constant string `step_id` and a `type` in
`expression`, `table`, `lookup`, `model_call`, `constraint`, plus every `*.json` object with such a `step_id` and `type`
(`input` and `output` steps are skipped). A step's *reads* are the union of: the identifiers in `expr` and `condition`; the
identifiers in each `clamp_bounds` value; the identifiers in each `key_expr` entry; the identifier in a `lookup` step's `as_at` (**added 2026-10-01 in the 2nd
pre-mint correction; the first predicate did not read `as_at` at all, a blind spot**); and the `feature_map` **keys**. Identifiers
are found by PL 9776's `referenced_names` tokenizer: string literals stripped, then `[A-Za-z_]\w*` not preceded by `.`, `$`
or another word character and not followed by `(`, minus the keywords `true false null and or not in`. A step has an
*undeclared read* when its reads minus its `consumes` are non-empty.

**Name-bearing fields of the step models** (`packages/model-schema/src/model_schema/rating.py:262-320`), each with its
inclusion or exclusion: `expr` (`RatingExpressionStep`) and `condition` (`RatingConstraintStep`), included, evaluated
expressions; `clamp_bounds` values, included, evaluated; `key_expr` (`lookup`, `table`), included, names read as the key;
`as_at` (`lookup`), **included now**: `NON_EXPRESSION_FIELDS` (`pricing_core/rating/authored.py:60`) says it "names a date
input; nothing evaluates it" today and moves to evaluated when the runtime does (RL-1313 DP-G5 (i)), so it is a declared
name to count, not an evaluated read; `feature_map` **keys**, included (graph value names; the values are model feature names,
excluded); `consumes`/`produces`, the declarations themselves, excluded; `input_name` and `output_name` (`input`/`output`
steps, skipped by construction) and `reason_code` (a recorded code), excluded; `*_ref` fields, artifact references, excluded.

**Caveat.** The predicate is that tokenizer, **not the engine's parser, and it is unvalidated against the engine**. Spike S1
step 1 of PL 9776 (working id) validates it. A dotted path or a `$`-prefixed name is skipped by construction; the table is
therefore a floor on literal steps, not a proof of the engine's own reads.

**Exposure, as measured at `19155b50`** (filer's re-run, matching auditor-pl9776's). **Re-run 2026-10-01 with the `as_at`
predicate** over a fresh `git archive origin/main packages backend examples scripts docs/contracts` extract (script
`/home/puzhenhao1989/.claude/jobs/6fa41099/tmp/p5b/sweep2.py`, `sweep.py` plus the one `as_at` line): **identical to the
old predicate, 70 steps in 22 files, 4 undeclared, 12 not evaluated, seed 0, bench 0 literal, the same four steps, no new
under-declaring step**. The blind spot hid nothing in the scanned code (the `lookup` steps with an `as_at` add no
undeclared read); it hid `s_area` in `03`, which no code sweep reaches (`.md` is not
scanned) and the table below does not list:

| Population | Steps | Undeclared reads |
|---|---|---|
| All literal steps scanned | 70 steps in 22 files | **4 steps** |
| `packages/pricing-core/tests/test_rating_score.py:76` `s_clamp` (constraint) | | `min_premium_minor` |
| `packages/pricing-core/tests/test_rating_score.py:80` `s_decl_cap` (constraint) | | `sanity_cap_minor` |
| `packages/pricing-core/tests/test_rating_score.py:83` `s_decl_floor` (constraint) | | `sanity_floor_minor` |
| `packages/model-schema/tests/test_rating_algorithm.py:65` `s_minprem` (constraint) | | `min_premium_minor` |
| Seed builder `examples/fremtpl2/model.py:327` | | 0 |
| Bench builders (`scripts/bench-rating.py`) | | 0 literal; see below |
| `rating_algorithms` rows, every local `gipricing*` DB (81 databases; 78 have the table, 3 do not; **re-counted 2026-10-01: 82 databases, 79 have the table, 3 do not, 0 rows**) | | **0 rows** |

All four are `constraint` steps in **tests**; none is in shipped code, a seed or a database row. The 3 databases without the
table are `gipricing_w37_6_d7_g_executor`, `gipricing_clone_m2` and `gipricing_w37-6-run2` (relation does not exist).

**12 steps are non-literal and are "NOT EVALUATED", not zero.** The sweep cannot read a field whose value is not a literal
(an f-string, a variable or a call), so it neither passes nor fails them:

- `scripts/bench-rating.py:246` `s_v000`; `:234` `s_risk`
- `backend/tests/test_sub_graphs_api.py:54` `s_x`
- `packages/pricing-core/tests/test_rating_score.py:66` `s_risk`
- `packages/pricing-core/tests/test_rating_pin_membership.py:231` `s_veh`; `:237` `s_veh`; `:61` `s_expense`; `:255` `s_expr`
- `packages/pricing-core/tests/test_testing.py:472` `s_risk`
- `packages/pricing-core/tests/test_rating_compile.py:304` `s_last`
- `packages/pricing-core/tests/test_rating_runtime.py:121` `s_risk`
- `packages/model-schema/tests/test_rating_version.py:105` `s_rp`

Command, verbatim: `python3 /home/puzhenhao1989/.claude/jobs/6fa41099/tmp/p5/sweep.py <extract>`; last line
`steps scanned 70 files 22 steps_with_undeclared 4 steps_with_nonliteral_fields 12`. DB count:
`docker exec gi-pricing-postgres-1 psql -U gipricing -At -d <db> -c "select count(*) from rating_algorithms"`, over every
`pg_database` row `like 'gipricing%'`, 0 in each of the 78 that has the table.

**What the sweep does not show:** that the 4 test steps are wrong. A test may declare an input absent on purpose; they are
unlabelled, so nothing says so. Nor does it show that the 12 non-literal steps are clean.

## A third defect class: 03's example is refused three ways, with five unproduced raw names, plus a sixth (effective_date) under the widened predicate

The 2nd pre-mint correction. `RatingAlgorithm.model_validate` over the `03` §4.1 JSON block (`03-rating-engine.md:233-278`,
extracted verbatim), at `19155b50`, run as `uv run python v.py ex03.json` (`/home/puzhenhao1989/.claude/jobs/6fa41099/tmp/v.py`,
`v2.py`):

```
1 validation error for RatingAlgorithm
  Value error, declared output 'premium_ladder' has no output step (FR-214) [type=value_error, input_value={'slug': 'motor-gb', 'ver...mount_point': 's_ncd'}]}, input_type=dict]
```

The validator raises the first violation only, so the rest were found by removing each cause in turn (`v2.py`):

1. **FR-214**: three of four declared outputs, `premium_ladder`, `peril_risk_premium` and `decline_reasons`, have no `output`
   step (the only output step is `payable_premium_minor`).
2. After removing them: `Value error, step 's_out' consumes undefined value 'payable_premium_pre_round' (FR-212)` (item 3
   above).
3. After repointing `s_out`: `Value error, value 'office_premium_minor' is produced by 2 steps that do not form a single
   re-production chain (FR-212)`. `s_office` and `s_minprem` both produce it and `s_minprem` declares no `consumes`.
4. **Five raw names have no producer**: `postcode_outcode` is in `input_contract` (`:240`) but has no `input` step;
   `distribution_channel`, `commission_factor`, `profit_factor` and `min_premium_minor` are in neither `input_contract` nor any
   `produces`. The widened predicate adds a sixth, `effective_date` (read only by `s_area`'s `as_at`; in the contract, no
   `input` step). `purpose` is in the contract and read by no step.

These are defects of the same canonical example. The corrected example of DP-F35-1 must pass **every existing invariant**
(FR-214, both FR-212 limbs, the raw-name resolution) and the new declared-reads check, shown by the verbatim-compile test.

## Why it matters now

Phase 2's G2 algorithm is the first rating algorithm authored through the documented journey. Its author's reference is
`03:252-274`, which teaches the undeclared form and does not resolve. Today the exposure is 0 rows and 0 shipped steps, so the path is latent. The
first algorithm built from the example prices correctly only while the context happens to hold every name, and silently
otherwise.

## Disposition

**Fix before close with an owner: WK-1178.** Remedy via PL 9776 (working id) (the F35 plan). Proposed by the auditor, with the
maintainer's severity ruling recorded above; the lead gives the verdict.

1. **Decision.** PL 9776's DP-F35-1 decision-maker rules, explicitly: (a) FR-246's step-type scope (expression only, or also
   constraint `condition`/`clamp_bounds`, `key_expr`, `feature_map`); (b) whether `consumes` is mandatory. The ruling carries
   verbatim `03` text and its placement, **including the corrected example at `03:252-274`** (the whole steps block on this tree; it must fix the five
   under-declared evaluating steps, `s_out`'s unproduced `payable_premium_pre_round`, the FR-214 and second FR-212 refusals and
   the five unproduced raw names, plus a sixth (effective_date) under the widened predicate). The
   decision-maker receives this finding and the sweep output.
2. **Enforcement** lands with a **RED-FIRST constraint-step test**: a constraint step reading a name outside its `consumes`
   refuses at save, red on the current tree.
   **Widened by the maintainer (relayed by the lead, 2026-10-01), superseding the previous wording "passes BOTH the existing
   invariant and the new check": the corrected example must pass `RatingAlgorithm.model_validate` IN FULL, then compile, then
   the new declared-reads check, shown by a TEST that extracts the example verbatim from `03`, in Task 1A's commit** (PL 9776
   (working id)). The DP-F35-1 decision-maker writes a **complete valid algorithm**: an `input` step for every raw name and
   every declared output produced. Fixing all of §4.1's defects (the errors pasted in "A third defect class" above, as the
   filer's own run shows them) in one ruling, one edit of the same block, is accepted.
3. **The 4 test steps** are fixed, or kept as **named negative fixtures**.
4. **Interim guard.** G2's Exit-demo slice (a) acceptance line, "every step's reads ⊆ its declared consumes", checked by
   running the sweep on the new algorithm with 0 undeclared reads. Until enforcement lands, that line is the only guard.

Filed 2026-10-01 as working id 9773.

Corrected 2026-10-01 (pre-mint): five evaluating steps under-declare (s_area at 03:254-257 was missed), and s_out consumes an unproduced name.

Corrected 2026-10-01 (pre-mint, 2nd): the sweep predicate now reads as_at; 03's example also fails FR-214 and a second FR-212, and has five unproduced raw names, plus a sixth (effective_date) under the widened predicate.

Corrected 2026-10-01 (pre-mint, 3rd): the discharge clause is widened to model_validate in full, then compile, then the declared-reads check, on a complete valid algorithm.

## Resolution (2026-10-10, D8b batch)

**Closed**, fixed by `SL-1536` (`PL-1535`, ledger `LG-1594`), merged as `e4753e478ca546ecd2054994c2f6adf834add1a7` (#1267, "SL-1536: FD-1374 — a rating step reads only the names it declares (FR-246 enforced)"). `PL-1535`'s done-condition, quoted: "Done when `SL-1536` closes on its `LG-` and register row FD-1374 carries the fix's merge sha." `LG-1594` and the `SL-1536` roadmap row are both `closed` at that merge. The enforcement is `packages/pricing-core/src/pricing_core/rating/references.py` with the compile check; the corrected `03` §4.1 example and FR-246's row ride the same commit, and the two points `RL-1519` got wrong after the fact are corrected by `RL-1593` and `RL-1596`. Nothing above this section is edited.
