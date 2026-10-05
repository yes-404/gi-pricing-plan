---
id: RL-1361
family: ruling
title: PL-1267 DP-5 decided — a seeded rate table holds one Factor, and a named portfolio joins each key through its bound Factor, its declared Banding or its same-named column; the cache key covers the definition
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-01              # the ruling date; first prepared 2026-09-30 (see "How this was ruled")
owner: decision-maker
tree: 101e32dc5baf8edeb986063b680ccec31e5ba724
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: [RL-1383, RL-1418]
corrects: ~
relates: [PL-1267, FR-228, FR-230, FR-231, FR-232, RL-1264, FD-1357, FD-1358]
---

# RL-1361 — PL-1267 DP-5 decided — a seeded rate table holds one Factor, and a named portfolio joins each key through its bound Factor, its declared Banding or its same-named column; the cache key covers the definition

## How this was ruled

**Ruled 2026-10-01 07:43 BST at effort `high`** by the decision-maker session `dm-dp5`. The
process command line is `claude --effort high --model opus --name dm-dp5`, and the session's
`echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`. The session was opened on
the maintainer's raise of 2026-10-01, as the lead relayed it: "Commission DP-5's ruling now: a
fresh --effort high DM per its role file".

**This record's history on PR #941.** It keeps working id 9855. The lead mints the id at the
merge turn.

1. **Prepared** at effort `medium` (`ca949339` to `490b7ef4`, 2026-09-30, "PREPARED, NOT
   RULED"), evidence tree `dd25db94`. The prepared recommendation was option (d).
2. **A first effort-high pass** by session `dm-effort-high` (`d8ec408d` to `ded14eb3`,
   2026-09-30 10:24–10:45 BST). It confirmed (d) and took in:
   - the maintainer's decisions on `736de32e` (the portfolio must be `validated`; the
     weighted key carries the workspace);
   - the maintainer's decision on auditor-plans' N2 (`dataset:read` only when a portfolio is
     given);
   - auditor-plans' findings F1–F3 and N1.

   That pass was never minted. It set `status: active` on an unminted record.
3. **The dm-dp5 pass** re-verified every premise at origin/main `9b0fb97c`. It **replaces (d) with
   (e)**, for the reasons under "New at the dm-dp5 pass". **The maintainer's decisions in item 2
   are kept as they were made.** They are inputs to this ruling, not this role's to reopen,
   and they appear in items 7 and 5 below. `status` goes back to `draft` until the mint.
4. **An amending pass** by session `dm-9855b` (2026-10-01, from 08:00 BST), at effort
   `high`: the process command line is `claude --effort high --model opus --name dm-9855b`,
   and `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`. It was opened on
   the maintainer's raise of 2026-10-01: "F1 breaks the ruling's decisive premise, so the
   (e)-vs-(d) argument must be re-made against the seeding shape the fix defines." Its input
   is auditor-rl9855's audit of `9b0fb97c...40153afb`, verdict FINDINGS, adopted by the lead
   at 07:55:11 BST (findings F1–F5). This pass merged origin/main `101e32dc` (no rebase),
   re-checked every locator there, and wrote "Amendments by the amending pass" below. **The ruling is
   still (e).** Its reasons changed: see section C there.

### Premise disclosure — required by the maintainer, 2026-10-01 07:50 BST

This record was set `status: active` before it was minted, and with a different ruling.
Verified with `git show <commit>:<file>` at each commit of the branch:

- **`d8ec408d` (2026-09-30 10:24:48 BST) to `9bcf8036` (2026-10-01 07:47:17 BST):**
  `status: active`, with a "Ruled" section headed "DP-5 — option (d)". The session
  `dm-effort-high` set it so on 30 Sep. `9bcf8036` is `dm-dp5`'s merge of main and did not
  touch the record, so the `active` status was still there.
- **`40153afb` (2026-10-01 07:47:53 BST):** `dm-dp5` set `status: draft` and ruled (e).

An unminted record has no id that the gate resolves, and a ruling is not in force until the
lead mints it. So for those 21 hours the record claimed a standing it did not have, and it
claimed it for (d). This disclosure is the record of it. The amending pass does not know
whether any reader acted on that claim.

### Argument withdrawal disclosure — required by the maintainer, 2026-10-01 (after 08:10 BST)

The argument **"(d) cannot weight a seeded table"** was this record's decisive reason for
(e) at `40153afb`. It was **withdrawn on 2026-10-01** by `dm-9855b`'s amendment (commit
`8d870f8e`, 2026-10-01 08:07:51 BST), after audit findings F1 and F3. Why: F1 showed that a
seeded table with two or more factors cannot be made on main, so the seeded-table shape
the argument reasoned about was undefined. F3 showed that the defect belonged to today's
seeding code, which writes `banding_ref: None`, and not to (d): seeding could set
`banding_ref`, and (d) would then band the key with the same `apply_banding` that
`resolve_factors` calls. (e) now rests on Grouping keys, interaction keys and a declared
binding for identity keys (section C). The ruling's outcome, (e), did not change; its
reason did. Any reader who relied on the withdrawn argument should re-read section C.

## Locators — evidence tree `dd25db94` against origin/main `9b0fb97c`

`git diff --stat dd25db94 9b0fb97c` was run over every file cited below. Every code file is
unchanged **except** `packages/model-schema/src/model_schema/rating.py`. That file gained one
import line at `:27`, so every later line moves by +1. In `03`, hunks at `:459` (+4), `:740`
(+28) and `:778` (+4) move every later line. `02` moves by +48 before `:2045`. `01`, `06:64`
and PL-1267 are unchanged. The claim column was re-read at `9b0fb97c`, body and all.

**Re-checked at origin/main `101e32dc` by the amending pass.**
`git diff --stat 9b0fb97c 101e32dc -- <every file cited here>` prints nothing: no cited file
changed, so every locator in this record holds at `101e32dc`. The Slice 7 row is corrected
(audit F5). The rows after the table are new at the amending pass.

| What | At `dd25db94` | At `9b0fb97c` | Claim at `9b0fb97c` |
|---|---|---|---|
| PL-1267 premise (k); DP table; DP-5; Slice 7 | `:319`; `:356`; `:362`; heading `:584`, body to `:605` | unchanged | holds; DP-5 still "open (decision-maker)". *(Corrected by the amending pass, audit F5: the earlier text gave Slice 7 as `:585-606`.)* |
| `Weights`, `KeyTuple` (`pricing_core/rate_tables/operations.py`) | `:85`, `:87-88` | unchanged | holds |
| `_index_rows` | `:322-328` | unchanged | keys are the cells' **stored strings**, exact-matched |
| `_compute_diff` | `:331-381` | unchanged | holds; and `total_weight` 0 divides by zero (`:370-372`), new below |
| `diff_vs_previous` / `diff_vs_seed` | `:383-392` / `:395-404` | unchanged | both call `_compute_diff` identically |
| `_value_matches_key_type` | `:702-717` | unchanged | `int("03")` passes, `bool` is case-folded: stored key strings are **not canonical**, new below |
| `seed_from_model` key construction | `:191-194` | unchanged | `RateTableKey(name=factor, type=STRING, banding_ref=None)` **always**, new below |
| `backend/src/app/platform/rate_tables.py` `diff` | `:237-300` | unchanged | `:253-254` "this slice passes none"; cache read `:285-292` before any portfolio use |
| `api/rate_tables.py` `RatingReadDep`; `rate_table_diff` | `:46`; `:314-364` | unchanged | `against` is the only query parameter; the 202 branch submits `JobKind.RATE_TABLE_DIFF` |
| `worker/rate_table_handlers.py` `_rate_table_diff` | `:24-54` | unchanged | calls `service.diff` with **no cache and no portfolio**, new below |
| `diff_cache.py` `version_content_hash`; `DiffCache.key` | `:46-56`; `:77-88` | unchanged | the hash is canonical JSON of the cell **dicts**, so it covers the column **names**; the key adds the portfolio id |
| `RatingLookupStep`; `RatingTableStep` (`model_schema/rating.py`) | `:275-280`; `:283-288` | `:276-281`; `:284-289` | +1; holds |
| `RateTableKeyType`; `RateTableKey` | `:632-638`; `:661-668` | `:633-639`; `:662-669` | +1; types `int`/`string`/`date`/`bool`; no Factor binding exists |
| `ArtifactRef` (`model_schema/refs.py`); `banding`, `factor` types | `:56-75`; `:24` | unchanged | pins `version: int`; frozen |
| `Banding` (`model_schema/modelling.py`) | `:339-380` | unchanged | "Versioned, never edited"; has `column`; no `status` |
| `Factor.banding_id` / `grouping_id` | `:122-161` | unchanged | a Factor pins its Banding or Grouping by id |
| `apply_banding` (`pricing_core/modelling/bandings.py`) | `:419-463` | unchanged | casts to `Float64` (`:427`); null refusal `:456`; range refusal `:480` in `_resolve_edge`, naming a count and **one** example value |
| `resolve_factors` (`pricing_core/modelling/factors.py`) | `:106` | unchanged | pure; refuses a missing source column and a missing artifact by name |
| `BandingRow`, `FactorRow` unique keys (`backend/src/app/db/models.py`) | — | `:1331`, `:1361` | unique on (`workspace_id`, `slug`, `version`) |
| `load_bandings` / `_refuse_missing` (`platform/transformations.py`) | — | `:390-411` | a missing artifact is `NOT_FOUND` 404, never an empty map |
| `fittable_or_refuse`; `load_version` (`platform/datasets.py`) | `:743-760`; `:763-781` | unchanged | holds |
| `ReadDatasets` (`api/dataset_versions.py`); `rbac._covers` | `:60`; `:205-217` | unchanged | holds |
| ADR-710's tenancy line (`api/deps.py`) | `:26-27` | unchanged | holds |
| `03` FR-228; FR-1186 | `:119`; — | `:119`; `:128` | holds |
| `03` §4.2 `RateTable` example | — | `:284-300` | a **seeded** table whose key declares `banding_ref` |
| `03` §4.8 (portfolio frame held for WK-673) | `:563`, `:575` | `:567`, `:579` | +4; still not designed: PL-1267 Slice 1 has not landed |
| `03` §5.1 bulk-operation row; diff row | `:748`; `:749` | `:784`; `:785` | +36; diff row names no portfolio parameter |
| `03` §5.1 owned error codes | `:771-782` | `:807-821` | +36; no portfolio code; `DATASET_NOT_VALIDATED` absent |
| `01` owns `DATASET_NOT_VALIDATED`; `02` re-raises it | `:929`; `:2045` | `:929`; `:2093` | `02` +48; holds |
| `06` Governed Artifact list | `:64` | `:64` | holds; Banding is not on it |

**New locators, read at `101e32dc` by the amending pass.** Paths as above unless named.

| What | At `101e32dc` | Claim |
|---|---|---|
| `extract_relativity_table` (`operations.py`) | `:142`; the row at `:156` | each row carries **one** factor's key: `{factor: level.level, value_name: …}` |
| `validate_rate_table` | `:269`; the read at `:289` | reads every declared key from every row: `KeyError` on a second factor (reproduced below) |
| `seed_from_model` (pure); `_key_domains_of` | `:168`; `:160` | one table, one key per relativity entry; one domain per entry |
| `GlmFitResult.relativities` (`model_schema/modelling.py`) | `:1588` | `dict[str, tuple[RelativityLevel, …]]`, keyed by **factor slug**: `_design` iterates `matrix.terms` (`glm.py:247`), whose keys are slugs (`factors.py:86-99`) |
| `_relativities` (`pricing_core/modelling/glm.py`) | `:922`; loop `:950` | one table per categorical factor; a continuous factor has none |
| Level labels: `_levels`, `_design` | `glm.py:217`, `:252` | `series.cast(pl.String)`, so a boolean level is `"true"` |
| `RelativityLevel` | `model_schema/modelling.py:1530` | per-factor, marginal levels: no joint combinations |
| `ModelSpecCommon.factors`; `Model.spec` | `model_schema/modelling.py:842`; `:2057` | `tuple[UUID, …]`: no slug, no version |
| `Factor.banding_id` | `model_schema/modelling.py:154` | a banding Factor pins its Banding by id |
| `resolve_factors` banding; grouping; interaction | `factors.py:190`; `:194`; `_cross` `:246` | calls `apply_banding`; calls `apply_grouping`; crosses the operands' resolved levels |
| `load_factors` (`backend/src/app/platform/modelling.py`) | `:284` | loads a spec's Factors by id, operands too; a missing id is `NOT_FOUND` |
| platform `seed_from_model` (`platform/rate_tables.py`) | `:95` | passes no Factors to the pure function |
| `03` seed route; §5.2 `seed_from_model` | `:783`; `:973-974` | the body names a model only; the signature takes no Factors |
| `03` §4.2 diff examples | `:304-306` | aggregate only |

**F1 reproduced at the amending pass**, as the audit did, on the row shape and not end-to-end
through `seed_from_model`. With this worktree's `pricing_core` on the path,
`validate_rate_table([{"age": "17-20", "relativity": "1.8"}, {"region": "north",
"relativity": "1.1"}], <keys age, region>, …)` raised `KeyError 'region'`.

## New at the dm-dp5 pass

1. **Model-seeded tables bind no key.** FR-230 seeding is the only path that builds a rate
   table automatically. It writes every key as `type: string, banding_ref: None`
   (`operations.py:191-194`). Under (d), a seeded table's banded key therefore takes the
   same-named branch: it looks for a portfolio column named after the factor. That column
   holds raw values, never band labels, so nothing matches, and the zero-match refusal is the
   only result. (d) cannot weight the case it was chosen for, on the tables most diffs will
   be about.

   *(Amended by the amending pass, audit F1 and F3.)* The last sentence holds for today's
   code only, and it was this ruling's decisive argument. Two corrections:
   - **Multi-factor seeded tables cannot exist today.** Seeding a model with two or more
     factors raises `KeyError` (FD-1357). Every seeded table that exists has one
     key. The seeded-table shape was therefore undefined; section A defines it.
   - **The defect is not intrinsic to (d).** Seeding could set `banding_ref`, and (d) would
     then band the key with `apply_banding`, the same function `resolve_factors` calls
     (`factors.py:190`). Section C re-makes the argument without this item.
2. **A spec-vs-code disagreement, ruled here (`CLAUDE.md` §0).**
   - **The spec.** FR-228 says every key is "bound to a Factor or a banded input" (`03:119`).
     `03` §4.2's own example is a seeded table whose key declares `banding_ref`
     (`03:284-300`).
   - **The code.** `RateTableKey` has no field that can hold a Factor binding
     (`rating.py:662-669`), and seeding binds nothing.
   - **Ruling:** the code is wrong. FR-228 is normative, and the example shows the intended
     reading.
3. **(d) also refuses Grouping and interaction keys, and identity keys that are renamed.**
   - A Grouping key (vehicle group, postcode area) and an interaction key are derived, like a
     band. (d) has no branch for either.
   - An identity factor whose slug differs from its source column also misses, because the
     key is named after the factor.
   - `resolve_factors` (`factors.py:106`) already resolves every one of these from the Factor
     artifact, and it needs no database. It produced the levels that the model's relativities
     carry, and so the levels that seeded cells carry. Its `FactorMatrix` docstring states the
     purpose: "the relativity table weights them by exposure".

   *(Amended by the amending pass.)* Section C weighs each limb. The Grouping and
   interaction limbs carry the ruling. The renamed-identity limb is weak, because seeding
   could name an identity key after its source column instead.
4. **Stored key strings are not canonical.**
   - `_index_rows` matches the cells' stored strings exactly.
   - An import accepts `"03"` for an `int` key and `"True"` for a `bool` key
     (`operations.py:702-717`).
   - A portfolio `Int64` value of 3, cast to a string, misses a cell stored as `"03"`, and
     nothing reports it.
5. **The earlier pass's "neither name is in the key" was half wrong.** `version_content_hash`
   hashes the cell **dicts** (`diff_cache.py:46-56`), so the column names are in the hash.
   What the hash does not hold:
   - which column is a key and which is the value;
   - each key's type;
   - each key's `banding_ref` (and, from this ruling, its `factor_ref`).

   The definition component in item 5 is still required. Its reason is corrected.
6. **All-zero weights crash.** If every weighted changed cell has Σ exposure 0, `_compute_diff`
   divides by a zero `total_weight` (`:370-372`). Decimal raises, and the route answers 500.
7. **The 202 path is not covered.** The parquet path runs `_rate_table_diff` in a worker
   (`rate_table_handlers.py:24-54`). The worker has no cache, and its parameters carry no
   portfolio. The earlier text ruled the check order only "before the cache is read", which
   leaves a Job path that has no checks at all.
8. **A binding can dangle.** Nothing at table creation checks that a `banding_ref` resolves.
   Bandings and Factors are unique per (`workspace_id`, `slug`, `version`) (`models.py:1331`,
   `:1361`). So a ref resolves only inside its own workspace.
9. **`apply_banding` on a non-numeric column** fails in a Polars cast (`:427`), not as a
   named refusal. The earlier text's "`bandings.py:456` names the offending values" was also
   wrong: `:456` is the null refusal, which gives a count. The range refusal is at `:480`,
   and it gives a count and **one** example value.

## Amendments by the amending pass

### A. The seeded-table shape (audit F1): the shape FD-1357's fix builds

**Ruled: one table per Factor.** A model with K relativity entries seeds K tables, one per
seed request. Each seeded table has exactly one key, bound to the Factor its relativities
came from.

- **The request names the entry.** The body of `POST /api/v1/rate-tables/{slug}/seed-from-model`
  (`03:783`) gains a required `factor`: the Factor's slug, which is the key of
  `GlmFitResult.relativities`. One rule for every model, so a one-factor model names its
  factor too. At `101e32dc` the route's only caller is `backend/tests/test_api_rate_tables.py`
  (`grep -rln 'seed-from-model\|seedFromModel' frontend/src backend/tests`); the frontend
  has none.
- **The key** is `{"name": <factor slug>, "type": "string", "factor_ref": "factor:<slug>@<version>"}`.
  Its domain is the entry's levels that carry a relativity, as `_key_domains_of` computes it
  today.
- **Refused by name, 422 `VALIDATION_FAILED`:** a `factor` that names no relativity entry
  of the model. A continuous factor is one, because it has no relativity table
  (`glm.py:950` iterates categorical levels only).
- **A lineage holds one Factor.** Seeding into an existing table appends its next version
  (platform `rate_tables.py:95`). If the named Factor's slug differs from the slug the
  lineage's key is bound to, the seed is refused by name. A newer version of the same
  Factor is accepted.
- **An interaction is one entry, so one table.** Its key's levels are the crossed labels
  `_cross` builds (`factors.py:246`).
- **No migration.** A seed of two or more factors has never succeeded, so every seeded
  table that exists already has this shape, less the binding.

**Why one table per Factor.** The lead named two shapes for one table with a key column per
factor. Both are refused.

| Shape | Against FR-230 | Against FR-228 | Verdict |
|---|---|---|---|
| One table, the full cross-product of every factor's levels, each cell Π relativities | Cells grow as the product of the level counts: ten factors of ten levels is 10^10 cells, against FR-232's default row threshold of 250 000. FR-234 requires every combination. One edited relativity changes every cell that holds it, so "how far have we moved from the technical rate?" counts products, not edits. FR-233's "rebase to a chosen base level" has no one factor to rebase. | Each key is bound to a Factor, but no cell value belongs to one Factor. | refused |
| One table, the model's observed level combinations | The Model holds marginal relativities per factor (`RelativityLevel`), never joint ones. The combinations need the training data at seed time, so seeding stops being a read of the Model. An unseen combination fails FR-234 unless a `default_row` invents its rate. | As above. | refused |
| **One table per Factor** | FR-230 imports "a GLM's relativity table", and the fit makes one per factor (`_relativities`, `glm.py:922`). A diff against the seed counts edited levels. The product of factors is the algorithm's work: one `table` step per factor (`RatingTableStep`, `rating.py:284-289`). `03` §4.2's own seeded example (`03:284-300`) has one key. | The one key is bound to exactly the Factor its values came from. | **ruled** |

FR-228 still permits a hand-authored table with several keys (FR-232's vehicle × area
table). This shape binds seeding only.

### B. The cell key tuple

- **For any table (unchanged).** `KeyTuple` (`operations.py:87`): one stored string per
  declared key, in key-declaration order. `_index_rows` indexes cells by it, and `Weights`
  is keyed by it (`:90`).
- **For a seeded table.** The 1-tuple `(level,)`, where `level` is the named entry's
  `RelativityLevel.level`. That string is the Factor's resolved value under
  `cast(pl.String)` (`glm.py:217`, `:252`): a band label, a group label, an interaction's
  crossed label, or an identity value as Polars renders it (`"true"`, never `"True"`).
- **The join for a `factor_ref` key** applies the same `cast(pl.String)` to the resolved
  frame column and compares exactly. This is Ruled item 2's "comparison in the key's type"
  for a `string` key, and it is how the stored strings were made.

### C. The (e)-versus-(d) argument, re-made against this shape

Under A, a seeded table has one key, bound to one Factor. Take (d) together with a seeding
fix that sets `banding_ref`, and test it on each Factor type:

- **Banding: (d) suffices.** Seeding could set `banding_ref` to the Banding the Factor pins
  (`Factor.banding_id`). (d) then bands the Banding's `column` with `apply_banding`, the
  function `resolve_factors` calls (`factors.py:190`). The labels agree. **"(d) cannot weight
  a seeded table" described today's code, not (d). It is withdrawn as a reason for (e).**
- **Identity: (d) suffices** if seeding names the key after the source column instead of
  the slug. Under A no two keys share a table, so the names cannot collide. The cost is that
  the binding becomes a coincidence of names. FR-228 says "bound", and `03` §4.2 names its
  key `driver_age_band`, which is not a column. This is a weak reason for (e), not a
  decisive one.
- **Grouping: (d) cannot.** A key has no field for a Grouping. Adding one is a
  `grouping_ref`.
- **Interaction: (d) cannot.** The level is the operands' levels crossed, and each operand
  is banded, grouped or raw (`_cross`, `factors.py:246`). Covering it puts the operand list,
  and each operand's transformation, on the key.

So (d), widened to cover what seeding produces, puts on the key a `banding_ref`, a
`grouping_ref`, operand refs and a naming rule. Each is a second statement of which
transformation produced the key's labels. The first statement is the Factor's own
`banding_id`, `grouping_id` and `operand_factor_ids` (`model_schema/modelling.py:154-161`), which
`resolve_factors` reads. The two statements can diverge, and a table whose key names one
transformation while its labels came from another misjoins without an error. *(Amended by
the text-fix pass, re-audit A1: this paragraph said the restatement is "a second statement
of the `Factor` shape, which `CLAUDE.md` §2 forbids". §2 forbids hand-writing a shape that
already exists in `model-schema`; a `grouping_ref` would be a new field, so §2's rule does
not reach it. The argument is the single source of derivation. §2 is cited for its spirit
only: "a shape defined twice will diverge".)* (e)'s `factor_ref` points at the one
statement, and `resolve_factors` already resolves every type from it. Groupings (vehicle group, postcode area) and
interactions are ordinary in UK motor and home rating, so refusing them is not a narrow
loss.

**Ruling: (e) stands.** It rests on Grouping and interaction keys, and on a declared binding
for identity keys. The seeded banding case is not one of its reasons.

### D. Factor resolution at seeding (audit F2)

- `ModelSpecCommon.factors` is `tuple[UUID, …]` (`model_schema/modelling.py:842`). The pure
  `seed_from_model` takes no database (ADR-703), so it cannot turn a UUID into
  `factor:slug@version`.
- **The platform loads the Factors and passes them in.** Platform `seed_from_model`
  (`rate_tables.py:95`) calls `load_factors` (`platform/modelling.py:284`) with
  `model.spec.factors`, under the caller's workspace. A missing id is `load_factors`'s
  `NOT_FOUND`, never an empty list.
- **The pure signature** gains `factor: str` and `factors: Sequence[Factor]`. It takes the
  passed Factor whose slug equals `factor`, and sets `factor_ref` from its slug and version.
- **Refused by name, 422:** a relativity entry with no Factor of that slug among those
  passed, and two passed Factors with that slug.

### E. Two rulings the audit found missing (audit F4)

- **Null exposure is refused.** A null in the exposure column gives 422
  `VALIDATION_FAILED`, naming the column and the count of null rows. It is not read as 0:
  a weight read as 0 makes a figure smaller and says nothing. This joins Ruled item 3.
- **A null resolved key** maps to no cell, unless the Factor's or Banding's own null policy
  refuses it first (`bandings.py:456`). Its exposure counts in Ruled item 4's total, not in
  its matched figure.
- **The portfolio-frame premise.** Every branch of Ruled item 2, and (a) and (d) as well,
  needs the frame to carry each Factor's and Banding's source columns under the names the
  model's Dataset uses (`Factor.source_columns`). `03` §4.8's schema is PL-1267 Slice 1's,
  and Slice 2's reader reads it. **That schema must let columns outside its declared set
  pass through.** A reader that keeps only the declared columns makes every bound key fail
  with "source column absent". This is a dependency on Slice 1, reported to the lead.
  PL-1267 is not edited.

### F. FR-231's per-cell weight (FD-1358)

This ruling computes a weight per cell and feeds it to the aggregate
`exposure_weighted_mean_change_pct`. It does **not** deliver FR-231's "exposure weight
behind each cell" in the diff output. `RateTableDiff` (`rating.py:717-729`) and the spec's
own examples (`03:304-306`) are aggregate only. That gap predates this ruling. It is FD-1358, owner WK-673, and its fix is not decided here.

## Options, re-derived

| | Option | For | Against |
|---|---|---|---|
| (a) | A `portfolio` parameter. A row maps to a cell by same-named columns. | Explicit, citable, no algorithm | Refuses every derived key: band, group, interaction, renamed identity |
| (b) | Evaluate the algorithm's `table` step `key_expr` (the plan says "`lookup`", but a `lookup` step feeds reference tables, `rating.py:276-281`) | Honours any derivation | A partial re-rate. The diff depends on an algorithm version that the cache key does not carry. |
| (c) | A workspace default portfolio | No parameter | The weighting portfolio cannot be cited |
| (d) | (a), plus `apply_banding` where a key declares `banding_ref` | Covers a hand-authored banded key; with seeding setting `banding_ref`, a seeded banding key too (section C) | Refuses Grouping and interaction keys (section C). An identity key matches only if its name is its column. *(Amended by the amending pass: the earlier cell said "dead on seeded tables", which was today's code, not (d).)* |
| **(e)** | (d), plus a key bound to a **Factor** is resolved through that Factor with `resolve_factors` | FR-228's own binding. Covers every factor type a model can carry, including Grouping and interaction. Still a join, with no algorithm and no expression evaluator. The labels come from the function that made them. | One optional field on `RateTableKey`. Seeding must set it, so it waits on FD-1357's fix and on section D's Factor loading. |

## Ruled

**Option (e).**

1. **Which portfolio.**
   - The caller names a portfolio Dataset Version in a `portfolio` query parameter on
     `GET /api/v1/rate-tables/{slug}@{version}/diff` (`03:785`).
   - The frame is read through PL-1267 Slice 2's reader, against `03` §4.8's portfolio-frame
     schema, which Slice 1 writes.
   - The exposure column is **the one that schema names**. This ruling chooses no literal.
   - There is no workspace default.
2. **How a row maps to a cell.** This applies to each `RateTableKey` of the **current**
   version's definition. That is the definition `diff` uses for both sides
   (`rate_tables.py:276`). Exactly one branch applies:
   - **`factor_ref` set (new field, below).** Resolve the pinned Factor version over the frame
     with `resolve_factors`. Pass the Banding or Grouping the Factor pins, and an
     interaction's operand Factors. The key's value is the resolved level.
   - **`banding_ref` set.** Band the pinned Banding version's `column` with `apply_banding`.
     The Banding's out-of-range and null policies apply as declared.
   - **Neither set.** Use the portfolio column of the key's own name.
   - **Comparison is in the key's declared type, never by raw string.**
     - The key's value from the frame and each cell's stored key string are both read as the
       key's `type`: `int` as an integer, `bool` case-folded, `date` as a date, `string`
       exactly.
     - They match when the two typed values are equal.
     - The weight is then keyed by the cell's **stored** key tuple, which is the tuple
       `_compute_diff` looks up.
   - **The weight.** A cell's weight is Σ exposure over the rows that map to it, computed in
     Polars. It is passed as `weights` to `diff_vs_previous` or `diff_vs_seed`.
     - A cell whose Σ is 0 is given **no** weight, so the division in new item 6 cannot
       happen.
     - A negative exposure value is refused (item 3).
   - **Artifacts are resolved as pinned, under the caller's workspace, with no approval
     check.** A Banding has no lifecycle (`06:64`). A rate table has none either (FR-1186).
     The diff reports what the table declares. Reading them needs no permission beyond item 7,
     because the diff returns only aggregates.
3. **Refusals.** Each one names the key, the column or the ref.
   - **`VALIDATION_FAILED` 422** is the code for each of these:
     - a same-named column is absent;
     - a Banding's or Factor's source column is absent (`resolve_factors` already refuses
       this by name);
     - a banded source column is not numeric. This is checked before `apply_banding` casts.
     - a resolution error: `FactorResolutionError` from a Banding or Grouping policy. The
       response carries its message, which gives the count and the example value;
     - a negative exposure value;
     - a null exposure value, naming the count (section E, new at the amending pass);
     - **a portfolio whose rows match no cell of the table.**
   - **`NOT_FOUND` 404** for a `factor_ref` or `banding_ref` that does not resolve in the
     caller's workspace. The detail names the key and the ref. This is the form of
     `_refuse_missing` (`transformations.py`). A missing artifact is never an empty map.
   - **The `None` mean.** It has three causes: no portfolio; weights on no changed, comparable
     cell; or only zero-weight cells. Only a zero match is refused. **Item 4's coverage
     figures tell the other cases apart.**
4. **Coverage is reported.** With a portfolio, `RateTableDiff` (`model-schema`) carries two
   figures: total exposure, and the exposure that mapped to a cell of the current version.
   Both are regenerated into the contract (FR-451's drift check).
5. **The cache key** carries everything the answer depends on:
   - the two versions' cell hashes (already there);
   - the portfolio Dataset Version id (already there, `diff_cache.py:77-88`);
   - **always**, a hash of the canonical JSON of the current definition's `keys` and `value`.
     This covers each key's name, type, `banding_ref` and `factor_ref`, and the value's name
     and type (new item 5);
   - **the caller's workspace id when a portfolio is given** (the maintainer's decision on
     `736de32e`).

   **Why this is sound under banding versions.** A ref pins an immutable version (FR-4; a
   Banding is "Versioned, never edited"). A Factor pins its Banding or Grouping by an
   immutable id. Refs are unique per workspace (new item 8). So the workspace plus the
   definition hash fixes every artifact that shaped the weights.
6. **No portfolio.** The diff answers unweighted and says so (PL-1267 Slice 7).
7. **Portfolio permission, scope and status, before the cache read and before any Job.**
   These are the maintainer's decisions, kept unchanged.
   - **Permission.** The route stays `RatingReadDep`, so an unweighted diff stays open to a
     rating-only reader. When `portfolio` is given, the handler also requires
     `Perm.DATASET_READ`, workspace-wide. It is checked without loading the version, so the
     403 is the same for any id.
   - **Scope.** Use `load_version`'s predicate. The answer is one `NOT_FOUND` 404 body for a
     missing version and for another workspace's version. A read may drop the row lock.
   - **Status.** `validated` only, using `fittable_or_refuse`'s predicate. `draft` and
     `archived` are refused with **`DATASET_NOT_VALIDATED` 409**, re-raised from `01`, and the
     detail names the diff. A weighted figure is reproduced from its persisted evidence item,
     never by re-running against an archived portfolio.
   - **Order.** These checks run before the cache is read, and the test runs on a warm cache.
8. **The 202 path (new).**
   - The route runs item 7's checks **before** it submits `JobKind.RATE_TABLE_DIFF`. A refused
     portfolio never becomes a Job.
   - The Job's parameters carry `portfolio`.
   - The worker calls the same service path. That path re-runs the scope and status checks
     under the Job's workspace. A portfolio archived between submit and run fails the Job with
     `DATASET_NOT_VALIDATED`.
   - The worker computes the same weights as the 200 path. It has no cache, and this ruling
     adds none.
9. **The binding.**
   - **The new field.** `RateTableKey` gains `factor_ref: ArtifactRef | None = None`, of type
     `factor`. **A key carries at most one of `factor_ref` and `banding_ref`**, and the
     `model-schema` validator enforces this. `banding_ref` stays for "a banded input" with no
     Factor.
   - **Seeding.** FR-230 seeding sets `factor_ref` on every key to the Factor version that the
     model pins for that relativity entry. A relativity entry with no pinned Factor is
     refused by name at seeding. *(Amended by the amending pass.)* The seeded table has
     section A's shape: one table per Factor, one key. The Factors come from section D:
     the platform loads them and passes them in.
   - **Existing versions** are immutable (FR-4), so they stay unbound. Their derived keys are
     refused under item 3 until the table is re-seeded. No migration rewrites them.
10. **(b) is not planned.** A key derived by an arbitrary expression is refused by name. If
    such keys turn out to matter, that is a later spec change.

**Why (e).** *(Restated by the amending pass; section C has the argument.)*
- It keeps everything the planner valued in (a): a citable portfolio, no algorithm, and a
  join.
- It weights Grouping and interaction keys. (d) cannot weight them without a second,
  key-level statement of which transformation produced the labels (`grouping_ref`,
  operand refs), which can diverge from the Factor's `grouping_id` and
  `operand_factor_ids`. *(Reworded at the text-fix pass, re-audit A1.)*
- It makes the binding FR-228 names a declared field, not a coincidence of names.
- It uses the function that produced the levels, so band and group labels agree by
  construction.
- (d) with a seeding fix that sets `banding_ref` would weight a seeded banding key as well
  as (e) does. That case is not a reason for (e). *(The earlier bullet said (d) "leaves the
  FR-230 path … unweightable". That held for today's code only, and is withdrawn.)*

## Spec changes this ruling requires

These are recorded here and **applied by Slice 7's spec-first step** under
`.claude/skills/spec-change` (PL-1267 Slice 7, "Spec first"). They are not applied in this
commit, and PL-1267 is not edited.

*(Amended by the amending pass.)* The seeding changes, marked **[seeding]** below, are
applied instead by FD-1357's fix (owner WK-1178), in the same commit as its code
(`CLAUDE.md` §2: spec, code and tests land as one commit). The `factor_ref` field lands with
whichever of that fix and Slice 7 comes first, and the other cites it. Which comes first is
the lead's to order.

- **FR-228, dated clarification.** "Bound to a Factor" is `factor_ref`. "A banded input" is
  `banding_ref`. A key has at most one of them. A key with neither is joined by its name.
- **FR-230, dated clarification [seeding].** A seed request names one Factor. A seeded
  table holds that Factor's relativities, with one key bound to that Factor's version as
  the model pins it (section A). A lineage holds one Factor.
- **FR-231, dated clarification.** The weight is Σ portfolio exposure per cell, under item 2's
  mapping, from a named `validated` portfolio Dataset Version. Coverage is reported. A
  portfolio that matches no cell is refused. *(Amended by the amending pass.)* The
  clarification says how the weight is **computed** and that it feeds the aggregate mean.
  It must not say the diff shows the weight per cell: that is FD-1358 (owner
  WK-673), open.
- **`03` §4.2.** The `RateTable` shape gains `factor_ref`. `RateTableDiff` gains the two
  coverage figures. Both go through `model-schema` and the contract regeneration.
- **`03` §4.2's seeded example (`03:284-300`) [seeding].** *(New at the amending pass, audit
  F3.)* It is a seeded table, so its key carries `factor_ref`, names the Factor's slug, and
  has no `banding_ref`; its rows use that key name. The example stays a one-key table.
- **`03` §5.1, the seed route (`:783`) [seeding].** *(New at the amending pass.)* The body
  gains the required `factor`. The row names the 422 refusals of sections A and D and
  `load_factors`'s 404.
- **The contract, a breaking change [seeding].** *(New at the text-fix pass, re-audit A2.)*
  The required `factor` on the seed body breaks every existing caller of the route. The
  `model-schema` request shape changes, and the contracts are regenerated in the same
  commit: the seed route in `docs/contracts/openapi/gi-pricing.yaml:234` and
  `"/api/v1/rate-tables/{slug}/seed-from-model"` in `docs/contracts/openapi/generated.json`
  (line 25235 at `101e32dc`). The commit message marks the break.
- **WF-699 step A1, dated clarification [seeding].** *(New at the text-fix pass, re-audit
  A2.)* `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:41` reads as
  one seed request that makes "its relativity table" the starting rate table. Under
  section A, a model with K categorical factors gives K seed requests and K tables, one
  per Factor. The clarification says so.
- **`03` §5.2, `seed_from_model` (`:973-974`) [seeding].** *(New at the amending pass.)* The
  signature gains `factor: str` and `factors: Sequence[Factor]` (section D).
- **`03` §5.1, the diff row (`:785`).** Add the `portfolio` parameter, the 403, 404, 409 and
  422 refusals, and the 202 path's carriage of the parameter.
- **`03` §5.1, the owned codes (`:807-821`).** Add `DATASET_NOT_VALIDATED`, marked "(re-raised from
  `01`)" so that check 10 (one owner per code) holds.

Every item above is carried as exact text in *The exact texts* below (T1 to T12). Where a
bullet above and its text differ in wording, the text is the one applied.

### The exact texts

*(Added at the final pre-mint text pass, 2026-10-01, on the maintainer's exact-text rule.)*
Each item gives the file, the place, who applies it, and the exact bytes to find and to
write. Placement was read at `origin/main` `65fc6129`. The placeholders are:
`RL-1361`, this ruling's minted id; `<fix date>`, the date of FD-1357's fix commit;
`<Slice 7 date>`, the date of the WK-673 Slice 7 commit that applies the item;
`<first date>`, the date of whichever of those two commits first lands `factor_ref`;
`<WF date>`, the date of the decision-maker's `WF-699` commit. Nothing else in a text is a
placeholder.

**T1 — `03` FR-228, applied with `factor_ref` (FD-1357's fix or Slice 7, whichever is
first).** Placement: `docs/specs/03-rating-engine.md`, the FR-228 row (`:119`). The text is
**appended** to the end of the second cell, after `and an optional default row.` and one
space, before the closing ` |`. Nothing is struck.

```text
**Clarified <first date> (`RL-1361`): the binding is a declared field.** "Bound to a Factor" is `factor_ref`, a pinned `factor:<slug>@<version>`. "A banded input" is `banding_ref`, a pinned Banding with no Factor. A key carries at most one of them, and `model-schema` refuses a key that carries both. A key with neither is joined by its own name. A version written before `factor_ref` existed stays unbound (FR-4).
```

**T2 — `03` FR-230 [seeding], FD-1357's fix (WK-1178).** Placement: the FR-230 row
(`:121`). The text is **appended** to the end of the second cell, after `is always
answerable.` and one space, before the closing ` |`. Nothing is struck.

```text
**Clarified <fix date> (`RL-1361` section A): a seed request names one Factor.** The request's required `factor` is the Factor's slug, a key of the model's relativities. The seeded table holds that Factor's relativities under one key, bound by `factor_ref` to the Factor version the model pins, so a model with K categorical factors seeds K tables. A continuous factor has no relativity table and is refused. A lineage holds one Factor: a re-seed that names another Factor's slug is refused, and a newer version of the same Factor is accepted. A hand-authored table may still have several keys (FR-228).
```

**T3 — `03` FR-231, Slice 7 (WK-673).** Placement: the FR-231 row (`:122`). The text is
**appended** to the end of the second cell, after `so an actuary sees which edits matter.`
and one space, before the closing ` |`. Nothing is struck.

```text
**Clarified <Slice 7 date> (`RL-1361`): how the exposure weight is computed.** The caller names a `validated` portfolio Dataset Version, and there is no default. Each portfolio row maps to at most one cell of the current version through each key's binding (FR-228): a `factor_ref` key through that Factor's resolution, a `banding_ref` key through that Banding, and an unbound key by the column of its own name, compared in the key's declared type. A cell's weight is Σ exposure over the rows that map to it, and it weights the aggregate `exposure_weighted_mean_change_pct`. A cell whose Σ is 0 carries no weight. The diff reports the portfolio's total exposure and the exposure that mapped to a cell. A portfolio whose rows map to no cell is refused, and so is a null or negative exposure. This clarification does not make the diff show the weight per cell: that is FD-1358.
```

**T4 — `03` §4.2's seeded example [seeding], FD-1357's fix.** Placement: the
`RateTable` / `RateTableVersion` JSON block (`:284-300`). Four lines are **replaced**; the
example stays a one-key table and names `02` §4.2's own example Factor. Replace

```text
  "keys": [{"name": "driver_age_band", "type": "string", "banding_ref": "banding:driver-age-actuarial-v2@2"}],
```

with

```text
  "keys": [{"name": "driver_age_banded", "type": "string", "factor_ref": "factor:driver_age_banded@3"}],
```

and replace the three lines

```text
    {"driver_age_band": "17-20", "relativity": "1.8400"},
    {"driver_age_band": "21-24", "relativity": "1.4100"},
    {"driver_age_band": "25-29", "relativity": "1.1200"}
```

with

```text
    {"driver_age_banded": "17-20", "relativity": "1.8400"},
    {"driver_age_banded": "21-24", "relativity": "1.4100"},
    {"driver_age_banded": "25-29", "relativity": "1.1200"}
```

**T5 — `03` §4.2, the `factor_ref` note, in the same commit as T1.** Placement: a new
blockquote paragraph **inserted** after the line below (one line in the spec,
`docs/specs/03-rating-engine.md:310` at `origin/main` `65fc6129`; it occurs exactly once in
the file) and one blank line, before the `storage` note.

```text
Values are stored as decimal strings, never JSON floats (R2).
```

```text
> **`factor_ref` added <first date> (`RL-1361`, FR-228).** A key's `factor_ref`
> pins the Factor version the key is bound to, and a key carries at most one of
> `factor_ref` and `banding_ref`. A seeded table has one key, named after the Factor's slug
> and bound by `factor_ref` (FR-230), and this example is one.
```

**T6 — `03` §4.2, the coverage figures, Slice 7.** Placement: the same JSON block. The two
diff lines are **replaced**. Replace

```text
  "diff_vs_previous": {"changed_cells": 3, "max_abs_change_pct": 4.2,
                       "exposure_weighted_mean_change_pct": 0.8},
  "diff_vs_seed": {"changed_cells": 7, "exposure_weighted_mean_change_pct": -2.1}
```

with

```text
  "diff_vs_previous": {"changed_cells": 3, "max_abs_change_pct": 4.2,
                       "exposure_weighted_mean_change_pct": 0.8,
                       "portfolio_exposure": "48210.5", "matched_exposure": "47902.0"},
  "diff_vs_seed": {"changed_cells": 7, "exposure_weighted_mean_change_pct": -2.1,
                   "portfolio_exposure": "48210.5", "matched_exposure": "47902.0"}
```

and **insert** this blockquote paragraph after T5's, with one blank line between them:

```text
> **Coverage added <Slice 7 date> (`RL-1361`, FR-231).** `RateTableDiff` carries
> `portfolio_exposure` and `matched_exposure`, decimal strings: the named portfolio's total
> exposure and the exposure that mapped to a cell of the current version. Both are null
> when no portfolio is named. They tell apart the reasons for a null mean: no portfolio,
> weights on no changed cell, or only zero-weight cells.
```

**T7 — `03` §5.1, the seed route [seeding], FD-1357's fix.** Placement: the §5.1 row
(`:783`), **replaced**. Replace

```text
| `POST` | `/api/v1/rate-tables/{slug}/seed-from-model` | Seed from a model's relativities (FR-230) |
```

with

```text
| `POST` | `/api/v1/rate-tables/{slug}/seed-from-model` | **201** Seed one Factor's relativities from a model (FR-230). The body is `{"model_ref", "factor", "change_note"}`; `factor` is required and is the Factor's slug, a key of the model's `relativities`. The seeded table has one key, bound by `factor_ref` to the Factor version the model pins. **422** `VALIDATION_FAILED` for a `factor` that names no relativity entry of the model (a continuous factor included), for a named entry with no pinned Factor of its slug, for two pinned Factors with that slug, and for a re-seed of a lineage bound to another Factor's slug; **404** `NOT_FOUND` for a pinned Factor id that does not resolve in the caller's workspace (`load_factors`) (**amended <fix date>, `RL-1361` sections A and D**) |
```

**T8 — the seed route's design stub [seeding], FD-1357's fix.** Placement:
`docs/contracts/openapi/gi-pricing.yaml`, the `/rate-tables/{slug}/seed-from-model`
`description` (`:238`), **replaced**. Replace

```text
      description: FR-230. Records the source model so the diff-vs-technical-seed stays answerable.
```

with

```text
      description: FR-230. The body names the model (`model_ref`), one Factor (`factor`, required, the Factor's slug) and a `change_note`; one seeded table holds one Factor. Records the source model so the diff-vs-technical-seed stays answerable.
```

**T9 — `03` §5.2, `seed_from_model` [seeding], FD-1357's fix.** Placement: the §5.2
signature block (`:973-974`), **replaced**. Replace

```text
def seed_from_model(model: Model, *, table_slug: str, change_note: str, seeded_at: datetime,
                    rateable: bool = True, value_name: str = "relativity") -> SeedResult
```

with

```text
# `factor` and `factors` added <fix date> (RL-1361 section D): the platform loads the
# model's Factors and passes them in; the pure function binds the one key to `factor`'s Factor
def seed_from_model(model: Model, *, factor: str, factors: Sequence[Factor], table_slug: str,
                    change_note: str, seeded_at: datetime, rateable: bool = True,
                    value_name: str = "relativity") -> SeedResult
```

**T10 — `03` §5.1, the diff row, Slice 7.** Placement: the §5.1 row (`:785`), **replaced**.
Replace

```text
| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against=` | **200** Cell-level diff with exposure weights (FR-231); **202** with a Job where either version is `storage: parquet` (FR-232) |
```

with

```text
| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against=&portfolio=` | **200** Cell-level diff (FR-231), exposure-weighted when `portfolio` names a `validated` portfolio Dataset Version, with §4.2's coverage figures; **202** with a Job where either version is `storage: parquet` (FR-232), the Job's parameters carrying `portfolio`. With `portfolio`, these are checked before the cache is read and before any Job: **403** without `dataset:read`, the same for any id; **404** `NOT_FOUND` for a portfolio that is missing or in another workspace; **409** `DATASET_NOT_VALIDATED` for a `draft` or `archived` portfolio. **404** `NOT_FOUND` for a `factor_ref` or `banding_ref` that does not resolve, naming the key and the ref; **422** `VALIDATION_FAILED` naming the key, the column or the ref for an absent column, a non-numeric banded column, a resolution error, a null or negative exposure, or a portfolio that maps to no cell. A Job fails with the same codes (**amended <Slice 7 date>, `RL-1361`**) |
```

**T11 — `03` §5.1, the owned codes, Slice 7.** Placement: the end of the "Error codes owned
by this module" paragraph (`:807-842`). The final `)*.` is **replaced** by an appended code.
Replace

```text
orphaning a blob. `app.platform.traces.complete_pending_trace` is the only raiser)*.
```

with

```text
orphaning a blob. `app.platform.traces.complete_pending_trace` is the only raiser)*,
`DATASET_NOT_VALIDATED` (re-raised from `01`)
*(added <Slice 7 date>, `RL-1361` — **409** from
`GET /api/v1/rate-tables/{slug}@{version}/diff` when the named `portfolio` is not
`validated`, and the failure of its `rate_table.diff` Job when the portfolio is archived
between submit and run; the detail names the diff)*.
```

**T12 — `WF-699` step A1 [seeding], applied by a decision-maker, not an executor.**
`document-ids.md` §1.6's WF row gives a journey to the decision-maker via `spec-change`, and
an executor "never amends the journey itself". A decision-maker applies T12 in its own PR
after FD-1357's fix merges. Placement:
`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`, the A1 row (`:41`),
**replaced**. Replace

```text
| A1 | Pricing Actuary | `POST /rate-tables/{slug}/seed-from-model` on the AD frequency model — its relativity table becomes the starting rate table, with `seeded_from` recorded. | `03` FR-230 |
```

with

```text
| A1 | Pricing Actuary | `POST /rate-tables/{slug}/seed-from-model` on the AD frequency model, naming one Factor — that Factor's relativity table becomes the starting rate table, its one key bound to the Factor by `factor_ref`, with `seeded_from` recorded. *(Clarified <WF date>, `RL-1361` section A: one seed request per Factor, so a model with K categorical factors gives K requests and K tables.)* | `03` FR-230 |
```

**The contract, corrected at this pass.** The "contract, a breaking change" bullet above
says the `model-schema` request shape changes and both contracts are regenerated. At
`65fc6129` neither holds. The seed body is `body: dict[str, Any]`, parsed by `_seed_body`
(`backend/src/app/api/rate_tables.py:57`, `:120`), so no `model-schema` shape carries it,
and `generated.json` publishes it as an open object (`"additionalProperties": true`). Adding
`factor` does not change `generated.json`; `generate-contracts.py --check` must still pass.
`gi-pricing.yaml` is the hand-authored design stub, which `generate-contracts.py` never
overwrites (its module docstring), so it gets T8. The break is behavioural: a body without
`factor` is now refused 422, and the commit message still marks it. Whether the body gains a
typed `model-schema` shape is not decided by this ruling.

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop. If a text's find string is not found exactly once, that is a stop too, reported to the lead; the executor does not re-word it.


## What it obliges

- **This commit:** this record only.
- **PL-1267, which is the planner's file and is not edited here:**
  - DP-5's resolver cell cites this record once it is minted.
  - Slice 7's scope gains items 3–5, 8 and 9.
  - **The seeding limb of item 9 may be cut as its own process-slice before Slice 7.** Slice
    design is the planner's.
  - *(New at the amending pass.)* **Slice 1's `03` §4.8 schema must pass through columns
    outside its declared set** (section E). Without it, no key of any kind is weightable.
- **FD-1357 (owner WK-1178)** builds section A's shape and section D's Factor
  loading. Until it lands, a seeded table with two or more factors cannot be made. A table
  seeded before `factor_ref` exists stays unbound (FR-4) and must be re-seeded to be
  weighted through a Factor.
  - *(Noted at the text-fix pass for the fix planner of FD-1357; not a defect of this ruling.)*
    `03` §4.2 (`03:334-335`) says `seeded_from` is set only on the first version of a
    lineage, but seeding into an existing table sets it on the appended version
    (`backend/src/app/platform/rate_tables.py:108-111`, `:162`). "A lineage holds one
    Factor" relies on that behaviour, so the fix must settle which of the two is right.
- **Not decided here.** *(Amended by the amending pass: now filed.)* FR-231's per-cell
  weight in the diff output is FD-1358 (owner WK-673), section F.

## Acceptance — the violation that must become detectable

The violation: **a weighted diff whose weights do not come from the named portfolio under
the table's own key declaration.** Each case is shown failing on deliberately broken input.

**The join**
- **Seeded and banded, red-first, with two or more factors.** *(Amended by the amending
  pass, audit F1.)* The fixture GLM has at least two categorical Factors: a banding Factor
  and a grouping Factor. It is seeded once per Factor.
  - On main `101e32dc` the seed raises `KeyError`. That is the red (FD-1357).
  - After the fix, the seeds give two one-key tables, each with `factor_ref`.
  - Each table is weighted. Σ exposure per band, and per group, equals a hand-computed
    figure.
  - With seeding's `factor_ref` removed, the request is refused with zero match, and the
    test fails.
- **Seeding refusals (section A, D).** *(New at the amending pass, audit F2.)* Each is
  refused by name:
  - a relativity entry with no Factor of its slug among those passed to the pure function.
    With a fallback to an unbound key, the seed succeeds and the test fails;
  - two passed Factors with the same slug;
  - a `factor` that names no relativity entry, including a continuous factor;
  - a re-seed of a lineage with a different Factor slug;
  - The platform path: a `model.spec.factors` id that does not resolve in the caller's
    workspace gives `NOT_FOUND` 404.
- **Re-seed with a newer version of the same Factor is accepted.** *(New at the text-fix
  pass, re-audit A3.)* The lineage gains its next version, and that version's key carries
  `factor_ref` to the newer Factor version. If the slug check compares the whole
  `factor:<slug>@<version>` reference, the seed is refused and the test fails.
- **One test per Factor type** that `resolve_factors` implements: identity with a slug that
  differs from its column, banding, grouping, and interaction. Each is weighted equal to a
  hand-computed figure.
- **A hand-authored `banding_ref` key** is weighted through `apply_banding`. A table carrying
  both `factor_ref` and `banding_ref` is refused by `model-schema`.
- **Typed comparison.** Cells stored as `"03"` and `"True"` receive the weight of portfolio
  values `3` and `true`. With a raw string join, the test fails.

**Refusals**
- A missing same-named column, a missing source column, a non-numeric banded column, a
  negative exposure, and a portfolio that matches nothing: each gives 422 and names the
  column. With the zero-match refusal removed, a `None` mean comes back and the test fails.
- A Banding with `error` policy that meets an out-of-range value gives 422 and names the
  column.
- A dangling `factor_ref` or `banding_ref` gives 404 and names the key and the ref. A ref
  that exists only in another workspace gives the same 404.
- Only zero-weight changed cells: a `None` mean, no 500, and non-zero coverage figures.
  *(Amended by the amending pass, audit F4.)* With the zero-weight exclusion removed, the
  division at `operations.py:370-372` raises, the route answers 500, and the test fails.
- *(New at the amending pass, audit F4.)* A null exposure value gives 422 and names the
  column and the null count. With nulls read as 0, a figure is served and the test fails.
- *(New at the amending pass, audit F4.)* **The frame premise.** A portfolio whose Factor
  source column is outside `03` §4.8's declared set is read through Slice 2's reader, and the
  Factor resolves it. With the reader keeping only the declared columns, the request is
  refused "source column absent" and the test fails.
- A matched portfolio with no changed cell: a `None` mean, non-zero matched exposure, not
  refused.
- The coverage figures equal the fixture's total and matched exposure.

**The cache key**
- Two portfolios give two entries.
- The same content and portfolio in two workspaces give two entries.
- Two versions with identical cells whose definitions differ only in a key's role, a key's
  type, a `banding_ref` or a `factor_ref` give two entries, with and without a portfolio.
- Each test is red-first: with that component removed from the key, the second request is
  served the first one's figure, and the test fails.

**Permission, scope and status**
- A rating-only caller succeeds on an unweighted diff.
- With a `portfolio`, a rating-only caller gets 403, the same for an existing id and a
  nonexistent one. With `dataset:read` made route-wide, the unweighted case fails. With the
  handler check removed, the weighted case is served.
- Another workspace's portfolio gives the same 404 as a nonexistent id. This is also tested
  on a warm cache, with the foreign entry placed first. With the checks moved after the cache
  read, the test fails.
- A `draft` portfolio and an `archived` one each give `DATASET_NOT_VALIDATED` 409. A
  `validated` one is accepted.

**The 202 path**
- A refused portfolio on a parquet version gives the refusal and **no Job row**.
- An accepted one gives a Job whose result equals the 200 path's weighted figure on the
  rows-stored twin.
- *(New at the amending pass, audit F4.)* A rating-only caller with a `portfolio` on a
  parquet version gets 403 and **no Job row**.
- *(New at the amending pass, audit F4.)* A portfolio archived after submit and before the
  worker runs fails the Job with `DATASET_NOT_VALIDATED`. With the worker's re-check
  removed, the Job succeeds and the test fails.
- *(New at the amending pass, audit F4.)* A dangling `factor_ref` or `banding_ref` on a
  parquet version fails the Job with `NOT_FOUND`, naming the key and the ref.

Drafted as working id 9855; minted 2026-10-01 as RL-1361.
