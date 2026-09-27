---
id: RL-931
family: ruling
title: correct the example; do not build the breakdown
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-31
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-31-f62-timing-ms-ruling.md
---

# F62 — `timing_ms`'s key set: `03` §4.4's example is wrong, not `score_one` (2026-08-31)

`CLAUDE.md` §0 code-vs-spec ruling, owed to the decision-maker by **F62**
(`docs/findings/register.md:92`, filed `890b06e`) per its own Decision cell: *"carry forward
with an owner — the decision-maker, per `CLAUDE.md` §0, to rule which side is correct...
Absent a dated ruling this decays to the next `CLAUDE.md` §14 phase review."* Ruled ahead of
that decay, on the lead's dispatch (Plan review 11, filed the same day, lists F62 as owed
here).

**Numbering continues at 54.** Rulings 1–43 are catalogued from
[`RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md`](RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md) forward (see that
file's own chain and [`RL-00916-the-field-is-the-environment-the-quote-was-served-in-the-spec-already-says-so-and-the-branch-does-not-merge-until-it-says-so-too.md`](RL-00916-the-field-is-the-environment-the-quote-was-served-in-the-spec-already-says-so-and-the-branch-does-not-merge-until-it-says-so-too.md)'s
index); 44 is that file's own; 45–49 in
[`RL-00908-impact-matrix-row-4-does-not-sit-forever-it-inverts-and-part-c-row-5-closes-here.md`](RL-00908-impact-matrix-row-4-does-not-sit-forever-it-inverts-and-part-c-row-5-closes-here.md); 50–53 in
[`RL-00913-q5-file-by-the-f-id-verbatim-the-requirement-id-cannot-name-a-file-and-is-cross-linked-from-inside-it.md`](RL-00913-q5-file-by-the-f-id-verbatim-the-requirement-id-cannot-name-a-file-and-is-cross-linked-from-inside-it.md).

**Read against `origin/main` at `567eea2`** (`git log -1 --format=%H origin/main`,
re-verified immediately before writing this record).

---

## RL-931 — correct the example; do not build the breakdown

**The finding, restated precisely.** `docs/specs/03-rating-engine.md:419`, the
`ScoringResult` worked example in §4.4, shows `"timing_ms": {"total": 7.4, "model_call":
3.1, "table_lookups": 0.9, "expressions": 0.4}` — four keys. `score_one`
(`packages/pricing-core/src/pricing_core/rating/score.py:800`) emits
`scored.model_copy(update={"timing_ms": {"total": total_ms, "evaluate": eval_ms}})` — two
keys, one of which (`evaluate`) names none of the spec's other three. `build_scoring_result`
(`:747`) sets `timing_ms={}`, a placeholder its own docstring says callers fill in — but
`score_one` is `build_scoring_result`'s only caller today, so the two-key shape is what a
caller actually receives.

**Read at the artifact, both sides:**

- `docs/specs/03-rating-engine.md:419` — the example, quoted above, verbatim at
  `567eea2`.
- `packages/pricing-core/src/pricing_core/rating/score.py:747,776-800` — `build_scoring_
  result`'s docstring and `score_one`'s body, quoted above, verbatim at `567eea2`.

**Whether a requirement — not the example — settles it: it does not.** `git grep -n
"timing_ms"` against `docs/specs/03-rating-engine.md` returns exactly three hits: the
`:419` example, `:548`'s batch-exclusion sentence, and `:564`'s restatement of the same
exclusion ("a per-call wall-clock breakdown that means nothing aggregated across a chunk").
Neither exclusion sentence states or implies a key set — both discuss only *whether*
`timing_ms` appears in a batch output row, never its shape. No `FR-RATE-` row anywhere in
the module mentions `timing_ms`, `model_call` timing, `table_lookups` timing, or
`expressions` timing as a deliverable:
  - `FR-250` sets the *total* latency target (p99 < 50 ms, `NFR-454`) — a whole-call
    budget, not a breakdown requirement.
  - `FR-258` is the mechanism that actually carries per-step timing — Trace, which
    returns *"every step's id, label, ... and elapsed time"* — but Trace is opt-in
    (`score_one(..., trace: bool = False)`) and reports per-`step_id`, not aggregated by
    node type; nothing sums it into `model_call`/`table_lookups`/`expressions` buckets, and
    nothing requires that summation to exist.
  - `NFR-502` discusses the cost of `response_model` validation on the way out, not
    `timing_ms`'s content.
  - No occurrence of "illustrative", "non-normative" or "example only" appears anywhere in
    `03-rating-engine.md` (checked directly, `grep -in` over the whole file) — §4.4 carries
    no disclaimer either way, so the example is the only textual authority for either shape,
    and it is exactly the artifact in dispute.

So this is F62's own finding restated correctly: **the shape is specified only by an
example**, and CLAUDE.md §0 puts the choice of which side is wrong to a ruling rather than a
default.

**The published contract does not choose either side.** `model_schema.scoring.ScoringResult.
timing_ms` (`packages/model-schema/src/model_schema/scoring.py:188`) is `dict[str, float] =
Field(default_factory=dict)`; `docs/contracts/schemas/scoring.schema.json:57` mirrors it as
an open object with no required or enumerated keys. Both key sets are contract-legal. This
ruling is about what the illustrative example should show and, downstream of that, whether
the engine owes a capability it does not have — not about a schema violation.

**Ruled: correct `03:419`'s example to the two keys `score_one` emits (`total`,
`evaluate`). The engine is not extended to produce a `model_call`/`table_lookups`/
`expressions` breakdown.**

Rationale:

- **The two keys the code emits are a real, meaningful decomposition, not an accidental
  stub.** `total_ms` runs `t_start` (before input validation) to return; `eval_ms` runs
  `t_eval` (immediately before `await bundle.decision.async_evaluate(...)`) to immediately
  after it returns. `total − evaluate` is therefore input validation
  (`_validate_inputs`/`_check_purpose_mount`/`_check_billing_surface`) plus
  `build_scoring_result`'s post-evaluation work (ladder, outputs, decline reasons, optional
  trace construction) — a genuine "inside the engine" vs. "everything else in `score_one`"
  split, not two arbitrary numbers.
- **The four-key breakdown the example shows is not a small correction to what exists —
  it is a capability nothing in this codebase builds.** `score_one` reaches the engine
  through exactly one call, `bundle.decision.async_evaluate()` (RL-868,
  `2026-08-29-w11-prework-rulings.md`), a single opaque invocation of the GoRules ZEN
  binding (ADR-706). `pricing-core` does not — and by that ruling's own reasoning, should
  not — split that call into a thread-pool of per-node-type sub-calls it could separately
  time. The only sub-DAG timing this platform has at all is Trace's per-`step_id`
  `elapsed_us` (FR-258), which requires the engine's own trace mode
  (`{"trace": trace}` passed into `async_evaluate`) and is opt-in per request. Producing
  `model_call`/`table_lookups`/`expressions` for *every* call — matching the example's
  unconditional presence in `timing_ms`, which `score_one` populates whether or not
  `trace=True` — would mean turning trace mode on unconditionally and adding a
  step-type-keyed aggregation pass, on every real-time request.
- **That cost lands on the one budget this platform is already failing.** `docs/roadmap.
  md`'s WK-671 closure record: `NFR-489` (p99 < 50 ms) is **measured and FAILING** —
  `_fetch_bundle` alone costs p99 66.294 ms, and even with the fetch excluded the
  without-GBM limb is p99 23.027 ms against a 15 ms sub-budget. Adding unconditional trace
  capture plus a new aggregation step to `score_one`'s hot path, to satisfy an example with
  no requirement behind it, moves in exactly the wrong direction while that NFR is open and
  carried to an architectural ruling before WK-674 (RL-921 discharged the architectural
  *question*, not the requirement — `docs/roadmap.md` row **WK-671**). A capability that costs
  latency on every request and is owed to nothing but a worked example is not owed at all.
- **Nothing else in the suite reads the four-key shape as load-bearing.** The batch-output
  spec (`03:548,564`) excludes `timing_ms` entirely and never inspects its keys either way.
  `05-monitoring.md` was not searched for a dependency on this shape because F62's own row
  records none, and this ruling does not need to extend that search: the two sentences that
  *do* mention `timing_ms` in `03` both predate and survive this correction unchanged — they
  said "excluded" before and say "excluded" after.

**This is not "the engine may owe the breakdown; §4.4 may be aspirational" left open, per
F62's own framing of the two options — it is decided: the example was wrong, in a document
that is otherwise consistent with the code (no other `ScoringResult` field in the same
example disagrees with what `score_one`/`build_scoring_result` produce, checked by reading
`premium_ladder`, `outputs`, `decline_reasons`, `outcome`, `rating_version_ref`,
`bundle_hash` against the same functions).**

## Acceptance Standard

The testable definition of "done" for this ruling, each item checkable by a command a
fresh reviewer can run:

1. `git grep -n '"model_call": [0-9]' docs/specs/03-rating-engine.md`,
   `git grep -n '"table_lookups"' docs/specs/03-rating-engine.md` and
   `git grep -n '"expressions": [0-9.]*}' docs/specs/03-rating-engine.md` each return
   **zero** matches (today, before this ruling lands, all three return the one hit at the
   old `:419`).
2. `docs/specs/03-rating-engine.md:419`'s `timing_ms` example reads `{"total": 7.4,
   "evaluate": 6.6}`, immediately followed by a paragraph naming what the two keys are and
   citing this ruling by date and F-id.
3. `python3 scripts/audit-docs.py` exits clean on the branch carrying this change, with no
   new `FR-`/`NFR-`/`ADR-`/`OQ-` id introduced.
4. No file under `packages/pricing-core/`, `packages/model-schema/` or
   `docs/contracts/schemas/` changes in the same commit — this ruling is a documentation
   correction, and a code diff alongside it is a violation of the ruling, not part of it.
5. **A gap this ruling deliberately leaves open, named rather than silently left:**
   `score_one`'s two-key shape is not pinned by any existing test.
   `packages/pricing-core/tests/test_rating_score.py:518-519,557,621-622` all normalise
   `timing_ms` to `{}` via `model_copy(update={"timing_ms": {}})` before comparing, to make
   timing-insensitive equality checks, and none inspects the key set — no test fails today
   if a third key is added. Closing it (an assertion on `set(result.timing_ms) ==
   {"total", "evaluate"}`) is small enough to fold into whichever slice next touches
   `score.py`, and is not itself owed a new workstream by this ruling.

## Disposition

- **Spec correction made in this commit, no new id, no meaning change to any `FR-`/`NFR-`
  row:** `03-rating-engine.md:419`'s `timing_ms` example is corrected to `{"total": 7.4,
  "evaluate": 6.6}`, with one paragraph immediately after the code block (before §4.5)
  naming what the two keys are and citing this ruling.
- **No code change and no workstream is owed one.** F62's Decision cell posed extending the
  engine as one of the two dispositions; this ruling closes that limb — the four-key
  breakdown is not built, because nothing requires it and building it costs the wrong
  budget. If a future spec change wants a real per-phase timing breakdown, it is a new
  `FR-RATE-` requirement stating the need and its cost against `NFR-489`/`NFR-501`,
  not a silent extension of `score_one`.
- **F62 is discharged.** The register row (`docs/findings/register.md:92`) is not edited by
  this commit — the auditor holds that file (lead's instruction, 2026-08-31) — so the lead
  or auditor appends the closing note citing this ruling and the merged PR number, per §9's
  "appended as a dated note citing the merging PR, never rewritten" convention.
- **The lead merges**, after the gate; this record does not.

## Verification

`python3 scripts/audit-docs.py` run clean on this branch before commit (one spec edit, no
new `FR-`/`NFR-`/`ADR-`/`OQ-` id, no section renumbering). No code, tests or contracts
change — `docs/contracts/schemas/scoring.schema.json`'s open-shaped `timing_ms` already
covers both the old and new example, so `scripts/generate-contracts.py --check` and the
Python/frontend gate halves are unaffected and were not re-run for this docs-only change.
