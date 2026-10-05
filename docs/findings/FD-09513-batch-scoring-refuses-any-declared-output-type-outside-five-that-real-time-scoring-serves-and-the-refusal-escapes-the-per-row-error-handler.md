---
id: FD-9513
family: finding
title: Batch scoring refuses any declared output type outside five that real-time scoring serves, and the refusal escapes the per-row error handler
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: 5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a
corrected_by: []
relates: [WK-1178, FR-214, FR-227, FR-253, FR-254, FR-255, FD-1333, RL-1343, RL-923]
---

# FD-9513 — `_coerce_output_value` raises for `int`, `count`, `relativity` and `percentage`, which `/score` serves

**Filed** by the auditor on the lead's brief of 2026-10-05, working id 9513 (reserved in the lead's `eta.md`). The claim
came from planner-a12fold's planning-time reading and was **not verified when made**. The maintainer (by delegation)
ordered the check in `to-lead.md` (a local channel file, so cited by its header), entry headed
"2026-10-05 17:52:50 BST — GO: confirm the /score vs batch output divergence NOW (read-only auditor); if confirmed, a SEPARATE FD (option (b)) now",
item 2, quoted verbatim:

> 2. GO: one read-only auditor, now. It reads both paths in full at 5fe56b87 (real-time _build_outputs and its callers; batch _outputs_json, _KNOWN_OUTPUT_TYPES and the decimal stringification) and runs one mktemp probe per case: (i) a declared int (and count) OUTPUT, (ii) a declared relativity or percentage output, (iii) a declared decimal output. Each goes through the real-time path and the batch serializer, recording the served JSON value and type or the refusal. No suite; nice; OMP_NUM_THREADS=1.
>    - If CONFIRMED: file the SEPARATE FD now (option (b)) with a proposed severity, owner WK-1178; its fix edits score.py and runs after SL 9561. LIVENESS decides the severity: whether any committed algorithm, fixture or the demo declares a non-{money_minor, decimal, bool, string, date} output. The auditor also states which side the spec (03 §5 / FR-226 and the batch scoring FRs) says is RIGHT. That is a reading, and the fix plan carries the decision.
>    - If NOT confirmed: report with the probe output; Step 1a stays as ruled.
>    PL 9521 Step 1a then CITES the FD instead of discovering it.

**Every fact below was read or measured at `origin/main` `5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a`**; `tree:` is that
commit. Paths are `packages/pricing-core/src/pricing_core/rating/score.py` unless written in full.

## Finding

**CONFIRMED for the four non-decimal types; proposed severity MEDIUM, LATENT; owner WK-1178** (the maintainer sets
severity; liveness below is "none committed"). The batch serialiser `_coerce_output_value` (`:950`) raises
`ValueError("score_batch: cannot serialise a declared output type …")` for any declared type outside
`_KNOWN_OUTPUT_TYPES = {money_minor, decimal, bool, string, date}` (`:947`, `:964-965`). The declared-type vocabulary is
wider: `AlgorithmOutput.type` is a free string that only refuses `float`
(`packages/model-schema/src/model_schema/rating.py:225-247`), and the save-time check treats `int`, `decimal`,
`money_minor`, `relativity`, `percentage` and `count` as the numeric family (`compile.py:57`, `_compatible` `:124-129`).
So an algorithm that declares an `int`, `count`, `relativity` or `percentage` output saves, compiles, and is **served on
`POST /api/v1/score`**, but **cannot be batch scored**.

**Worse than a refusal: the raise is not a per-row error.** `_score_batch_row` (`:1081`) builds its `"error"` row only
for what is raised inside its `try` (`:1096-1102`, closed by the `except (ValueError, RuntimeError)` at `:1103`). The
call `_outputs_json(algorithm, scored.outputs)` sits in the `return` after that `try` (`:1123`), so the `ValueError`
leaves the row handler. `_score_batch_chunk` (`:1130-1132`) has no handler, and the Job handler loop
(`backend/src/app/worker/scoring_handlers.py:222-232`, `score_batch(...).collect()`) has no `try`/`except` in the file
(`grep -n 'except\|try:'` finds none). I did not run the handler; the probe below ran `score_batch` directly and the
exception left it. Read together, one quote of a declared `int` output would end the whole batch run, where FR-255 says
errors are "typed and per-quote" and a run "does not abort on individual failures unless the failure rate exceeds a
declared threshold".

**The decimal half is already filed and decided.** A declared `decimal` output reaches `/score` as a JSON number and
batch as a JSON string. That is `FD-1333`, decided by `RL-1343` and written into FR-214's dated clause (JSON string on
every scoring path, delivered by WK-1178). It is not re-filed here. The probe's decimal rows are a control that the
probe sees it (below).

## Evidence

**1. The two paths, at the sha.**

| Step | Real-time `/score` | Batch |
|---|---|---|
| Entry | `score` route `backend/src/app/api/score.py:351` | `score_batch` `score.py:1135`, per chunk `_score_batch_chunk` `:1130` (Job loop `scoring_handlers.py:222-232`) |
| Per quote | `score_one` `:876` | `_score_batch_row` `:1081` through `_score_context_sync` `:1045` |
| Shared tail | `build_scoring_result` `:830` → `_build_outputs` `:729` | same `build_scoring_result` → `_build_outputs` |
| Output value | `_build_outputs` `:729-763` (the `elif` at `:756`): a rung or `money_minor` output is the engine's exact value rounded once; **anything else is `result[name]` unchanged** (`:756-757`) | `_outputs_json` `:991-1003` → `_coerce_output_value` `:950-988`, keyed by the declared type |
| To the wire | `Response(content=result.model_dump_json())` (`backend/src/app/api/score.py:386`) | `json.dumps(coerced)` (`:1003`), a string column `outputs_json` |

Both paths share `_build_outputs`. They diverge only after it. Real-time applies no type coercion and no refusal. Batch
applies `_coerce_output_value`.

**2. Probes.** Tree: a detached `git worktree` of `5fe56b87`, `uv sync --all-packages`, `OMP_NUM_THREADS=1 nice -n 10 uv run`.
The algorithm is Task 1.4's fixture shape (`test_rating_score._algorithm_payload`, the `_DecimalOutputResolver`
pattern of `test_rating_score_batch.py:79-114`), with one added `expression` step and `output` step declaring
`probe_out` of the type under test. No suite and no database. The probe script was written in a `mktemp -d` under the
job directory, outside the repository. Each case runs `score_one` then `ScoringResult.model_dump_json()` (the route's
own call) and `score_batch` on the same context (driver age 18).

```
[int]        REALTIME wire outputs = {"payable_premium_minor": 1507, "probe_out": 18}   probe_out JSON type = int
[int]        BATCH RAISED OUT OF score_batch (not an error row): ValueError: score_batch: cannot serialise a declared output type 'int'
[count]      REALTIME wire outputs = {"payable_premium_minor": 1507, "probe_out": 18}   probe_out JSON type = int
[count]      BATCH RAISED OUT OF score_batch (not an error row): ValueError: score_batch: cannot serialise a declared output type 'count'
[relativity] REALTIME wire outputs = {"payable_premium_minor": 1507, "probe_out": 27}   probe_out JSON type = int
[relativity] BATCH RAISED OUT OF score_batch (not an error row): ValueError: score_batch: cannot serialise a declared output type 'relativity'
[percentage] REALTIME wire outputs = {"payable_premium_minor": 1507, "probe_out": 27}   probe_out JSON type = int
[percentage] BATCH RAISED OUT OF score_batch (not an error row): ValueError: score_batch: cannot serialise a declared output type 'percentage'
[decimal]    REALTIME wire outputs = {"payable_premium_minor": 1507, "probe_out": 27}   probe_out JSON type = int          (expr driver_age * 1.5, a whole value)
[decimal]    BATCH outcome=quoted error_code=None error_message=None outputs_json='{"payable_premium_minor": 1507, "probe_out": "27"}'   probe_out JSON type = str
[decimal]    REALTIME wire outputs = {"payable_premium_minor": 1507, "probe_out": 19.8}  probe_out JSON type = float        (expr driver_age * 1.1)
[decimal]    BATCH outcome=quoted error_code=None error_message=None outputs_json='{"payable_premium_minor": 1507, "probe_out": "19.8"}'   probe_out JSON type = str
```

The `decimal` rows are the positive control: the same probe through the same two paths shows batch serialising a known
type (as a string) while real-time serves a number, which is `FD-1333`, so the harness does exercise both serialisers.
A whole-valued `decimal` expression reaches `/score` as a JSON **integer** and a fractional one as a JSON **float**, so
the real-time JSON type of a `decimal` output also depends on the value, which `FD-1333` and `RL-1343` do not mention
(they say "float").

**3. What the refusal does to the Job.** Not run. Read: `:1123` is outside the `try`, `_score_batch_chunk` and the
Job loop catch nothing. The exception type is a plain `ValueError`; whether the Job's generic failure path stores its
message is `FD-1217`'s subject and not re-measured here.

## Liveness

**None committed.** Predicate: `git grep -nE "type.: *.(int|count|relativity|percentage|float|integer|number)." -- . ':!docs' ':!*.json'`
at the tree (78 lines, most of them inputs, test asserts or JSON Schema), read by hand for the declarations that sit in an `outputs` list. Every committed rating algorithm's declared output is
`money_minor`: `examples/fremtpl2/model.py:336`, `backend/tests/test_bundle_slot.py:53`,
`backend/tests/test_regression_suites.py:312`, `backend/tests/test_rating_algorithms.py:26,74`,
`backend/tests/test_rating_version_compile.py:58`, `packages/model-schema/tests/test_graph_errors.py:23`. The scripts
`scripts/bench-rating.py`, `bench-score-batch.py` and `bench-compiled-for.py` declare `money_minor` outputs (the `int`
and `relativity` they carry are an input and a rate-table value column). The one `decimal` output is
`packages/pricing-core/tests/test_rating_score_batch.py:84` (the batch test fixture; `FD-1333`). The only declared
`relativity` **outputs** are Sub-graph output ports (`backend/tests/test_sub_graphs_api.py:29`,
`test_sub_graphs_service.py:27`, `packages/model-schema/tests/test_sub_graph.py:25`); a Sub-graph is not scored
through `score_one` or `score_batch` (`03:841`: a parent inlines it in Slice 2; nothing else scores one). `int` appears as a declared output
only as a rejection case (`test_sub_graphs_api.py:85`, `test_graph_errors.py:62`, `test_sub_graph.py:73`). The demo
(`examples/fremtpl2/model.py`) and `backend/src/app/demo/` declare none. So the gap is open to any author who declares
one of these types, and nothing committed does. That is why LATENT.

## Spec reading (a reading, not a decision)

- **FR-254** (`03:166`): batch "uses the identical compiled bundle and code path as real-time scoring — never a separate
  'batch implementation' that could diverge." The two paths share `build_scoring_result`, then diverge in
  `_coerce_output_value`. On this text the divergence is the batch side's.
- **The batch column** (`03:692`): `outputs_json` is "total over every `AlgorithmOutput.type` this path can produce …
  and refusing, not stringifying, anything else". Real-time produces an integer for each of the four types (probe), and
  `AlgorithmOutput.type` admits all four, so by this sentence's own words they are in the set the column must be total
  over; "anything else" can then only mean a value no path produces. `RL-923` §5(i) ruled "total over the value types
  the rating path can produce" and refusing an unnamed type; the type list in `_KNOWN_OUTPUT_TYPES` is the
  implementation's reading of that, and neither text enumerates it. This is the reading that makes batch the wrong side.
  The text does not say how the four types must be written (JSON number, or string as for `decimal`).
- **FR-255** (`03:167`): errors are per quote and a run does not abort on individual failures. A refusal that leaves the
  row handler is outside this, whichever way the type question is decided.
- **FR-214 / FR-227** (`03:83`, `:113`): FR-214 fixes only `decimal` (string on every path, by `RL-1343`) and the ladder
  and `payable_premium_minor`; FR-227 names only the monetary types. No FR, §4 example or table says what a `count`,
  `relativity` or `percentage` output's JSON form is, or whether those types are valid output types at all.
  `docs/contracts` types `ScoringResult.outputs` as a bare object (`FD-1333`, evidence 2).

**Which side is right:** by FR-254 and `03:692`, real-time is the reference and batch is the side that must change.
What is open is the JSON form of the four types (a number as on `/score` today, or a string), and whether the vocabulary
should be closed at save time instead (so that `_coerce_output_value` and the compile check agree on one list). That
is the fix plan's to decide, with `RL-1343` as the precedent for `decimal`.

## Disposition

**Proposed by the auditor; the verdict is the lead's.** Carry forward with an owner, **WK-1178**, at MEDIUM, LATENT,
the grade the sibling FD 9549 (save-time numeric interchange, working id, not merged at this tree) proposes. Why not lower: one declared output of an accepted type fails an
entire batch run rather than one row. Why not higher: nothing committed declares one. The fix edits `score.py` and runs
after SL 9561, in `PL 9521`'s Step 1a (working ids), which cites this record. It needs: (1) the serialised form decided
for the four types; (2) `_outputs_json` moved inside the row's `try`, or the types made total, so no declared type can
leave the row handler (red first: a batch fixture declaring each of the four types, with an assertion on the row, not on
a raised exception); (3) `FD-1333`'s change and this one made in one place so `/score` and `outputs_json` stay one
function of the declared type. Event that next confirms or discharges it: a merged change to `_coerce_output_value`
and `_score_batch_row`, or a dated ruling that closes the output-type vocabulary at save time.
