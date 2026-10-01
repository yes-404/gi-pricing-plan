---
id: RL-9783
family: ruling
title: PL-9788 DP-A1 and DP-A2 decided — NFR-502 gains one dated line naming responses= as documentation that validates nothing, and is re-measured at the model and at the route, base against HEAD
status: draft                  # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-01
owner: decision-maker
tree: 101e32dc5baf8edeb986063b680ccec31e5ba724
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-9788, FD-1335, RL-1343, RL-883, RL-872, SL-1345, SL-1259, FR-250, FR-262, FR-451, NFR-502, NFR-489]
---

# RL-9783 — PL-9788 DP-A1 and DP-A2 decided: `NFR-502` gains one dated line naming `responses=` as documentation that validates nothing, and is re-measured at the model and at the route, base against HEAD

## How this was ruled

**Ruled at effort `medium`**, by the decision-maker session `dm-9788dp`. Its first effort
check, `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"`, printed `CLAUDE_EFFORT=medium`, which is what
the lead's brief relays from the maintainer ("NOW … medium DM passes for PL 9788 DP-A1/A2",
2026-10-01; this session did not read the channel entry itself).

**Working id 9783**, allocated by the lead, who is the only allocator (`FD-1338`). It is
minted at its merge turn, and every citation of `RL-9783` is then re-pointed. The plan it
rules is itself under working id 9788 (draft PR #1036, branch `fd1335-part-a-leaf-plan`,
head `bbed9f26e2b0f93ad890fd68f1297ac6c8770d50`); this record cites it as `PL-9788`.

**The questions, as filed** (`PL-9788` §Decision points, the DP-A1 and DP-A2 rows):
- **DP-A1:** *"Does `03` NFR-502 change text when the route documents its 200?"* Options
  (a) no spec change, (b) one dated line, (c) a dated line only if the figure moved
  materially. The planner recommends (b).
- **DP-A2:** *"How is `NFR-502` measured again?"* Options (a) the w8 shape on a post-ladder
  `ScoringResult`, (b) route level, base and HEAD, (c) both with the script inline in the
  ledger, (d) as (c) with the script committed. The planner recommends (c).

DP-A3 and DP-A4 are the lead's (`PL-9788` activation need 6) and are not ruled here.

## Verified first, at 101e32dc5baf8edeb986063b680ccec31e5ba724

The plan read its premises at `9b0fb97c`. `origin/main` is now `101e32dc` (fetched
2026-10-01 07:58 BST). `git diff --stat 9b0fb97c 101e32dc -- backend docs/specs/03-rating-engine.md docs/findings/FD-01335* docs/rulings/RL-01343* docs/research/w8-spike-resolution.md`
prints nothing, so every premise below holds at both trees.

1. **`NFR-502`'s text** (`docs/specs/03-rating-engine.md:1203`, read to the end of both
   dated amendments). The rule: *"The scoring endpoint does **not** apply `response_model`
   validation to its response."* The 2026-08-27 amendment cites *"p99 0.070 ms, 0.14 % of
   the 50 ms budget"* for *"a realistic `ScoringResult` (premium, 20 rate steps, 60 factors,
   metadata)"*, validate and serialise. The 2026-08-29 amendment (`RL-883`) states the
   property: *"Validate inbound, never outbound; serialise the trusted result directly with a
   compiled encoder"*, and names the mechanism: *"a raw `Response` carrying those bytes runs
   no outbound validation at all."* Neither amendment names `responses=`.
2. **The code** (`backend/src/app/api/score.py`). Both decorators carry
   `responses=problems(401, 403, 404, 409, 422)` and no 200 entry (`:276-286`, `:330-335`).
   Both handlers return a raw `Response` of `model_dump_json()` (`:321` for `/score`, `:376`
   for `/score/compare`) and carry `-> Response`. The module docstring's `NFR-502` paragraph
   is `:21-27`. `ScoringResult` and `ScoreComparison` are imported at `:77-78`.
3. **`FD-1335` *Disposition* item 2** asks for `responses={200: {"model": …}}` on both routes
   and says: *"**Evidence required: `NFR-502` is re-read after the change, not assumed
   unchanged.** Its own figure is the one to re-check … The slice measures again with the
   route as changed and quotes the result."* Two demands, then: the requirement's own figure,
   and the route as changed.
4. **The mechanism, measured again by this session.** In the root checkout's venv (FastAPI
   `0.141.1`, the version `uv.lock` pins at this tree), a scratch app with
   `@app.post("/s", status_code=200, responses={200: {"model": M}})` and a handler
   `-> Response` returning `'{"not":"M"}'` printed:
   ```
   0.141.1 response_model: None response_field: None
   {'application/json': {'schema': {'$ref': '#/components/schemas/M'}}}
   200 {"not":"M"}
   ```
   The route object has **no `response_field`**, so FastAPI has nothing to validate a
   response against: `responses=` is read when the OpenAPI document is built, and the
   request path never consults it. This reproduces `FD-1335` Evidence §2 and adds the
   structural reason.
5. **The original measurement's method** (`docs/research/w8-spike-resolution.md` §T4 and
   §"Version and method"): `time.perf_counter`, 1000 iterations, p99 = the 990th sorted
   value, on a shape described as *"premium, 20 rate steps, 60 factors, metadata"*. The note
   carries **no script**, and that shape predates `ScoringResult`, so the shape has to be
   re-expressed in today's fields (DP-A2 below does that).
6. **`ScoringResult` today** (`packages/model-schema/src/model_schema/scoring.py:171-189`):
   `outcome`, `rating_version_ref`, `bundle_hash`, `premium_ladder: list[LadderRung]`,
   `outputs: dict[str, object]`, `decline_reasons`, `trace: Trace | None`, `timing_ms`.
   `SL-1345` (`PL-1348`, WK-674's ladder slice) is `active` and **not merged** at this tree
   (`git log --oneline 9b0fb97c..101e32dc` shows its activation, `214fd4d7`, and no
   delivery). It changes `LadderRung` (`03` FR-248's 2026-09-30 amendment: each rung
   records its unrounded value). `PL-9788` sequences after it.
7. **The existing behavioural proof.** `backend/tests/test_score.py:341-380`,
   `@pytest.mark.req("NFR-502")`: a `model_construct` result that violates its own types is
   served verbatim with a 200. `/score/compare` has no such test (`PL-9788` premise f;
   Acceptance 8 adds one).
8. **Supporting citations in the planner's rationale.** `RL-872` makes a load tool *"not a
   CI gate"* with its result a dated note (`docs/rulings/RL-00872-dp3-load-generation-tooling-for-the-sustained-200-rps-test.md:80-98`). `SL-1259` (WK-673 Slice 5)
   lists `NFR-502` among its measurements (`docs/roadmap.md:829`). Both hold.

## Options, weighed

### DP-A1

- **(a) No spec change.** The rule's sentence stays true: `responses=` is not
  `response_model`. But the requirement then cites a figure (0.070 ms) for a shape the code
  no longer serves, while the slice holds a newer one, and the requirement's mechanism
  sentence names only the raw `Response`. The next reader who sees `responses={200: {"model":
  ScoringResult}}` beside *"does not apply `response_model` validation"* has to rediscover
  item 4 above to know they are compatible. The FD asks for `NFR-502` to be *re-read*; a
  re-read whose result is only in a ledger leaves the requirement citing the old figure.
- **(b) One dated line.** It records the compatibility once, where the rule lives, and
  replaces the stale figure's standing with a current one and its tree. Cost: one row edit,
  which is in `PL-9788`'s write set and contends with nothing (`PL-9788` §File contention:
  `SL-1345` edits the NFR-496 row, a different row).
- **(c) A line only if the figure moved materially.** "Materially" has no definition, and
  the compatibility statement is needed whether or not the figure moves. Rejected.

### DP-A2

- **(a) Model level only.** Re-checks the requirement's own figure, as the FD asks. It does
  not touch the route, so it cannot show "the route as changed", the FD's second demand.
- **(b) Route level only.** Shows the route as changed, but an in-process ASGI request costs
  far more than the 0.070 ms being checked, so it cannot re-check the requirement's own
  figure.
- **(c) Both, script inline in the ledger.** Meets both demands. Inline keeps `PL-9788`'s
  write set unchanged.
- **(d) As (c), with `scripts/bench-score-response.py` committed.** A committed script
  widens the write set for a one-off; `RL-872` already makes such a measurement a dated
  record, not a gate, and `SL-1259` owns the full-path `NFR-502` measurement later. Rejected.

Neither timing limb can **discriminate** the property `NFR-502` states: a change that
validated outbound would add roughly what limb (a)'s validate-and-serialise figure measures,
well inside a route-level run's noise. Timing shows cost; it does not show that no
validation runs. The discriminating evidence is structural (item 4: no `response_field`) and
behavioural (item 7: a type-violating result served verbatim). The ruling adds the first to
the ledger and relies on `PL-9788` Acceptance 8 for the second on `/score/compare`.

## Ruled

### DP-A1: option (b), one dated amendment on the `NFR-502` row, with fixed content

`03` `NFR-502` gains **one** dated amendment, appended after the 2026-08-29 one, written by
the executor in `PL-9788` Task 4 **after** Task 5 so it quotes measured figures. It must say,
in the executor's words, these five things and nothing more:

1. Both `POST /api/v1/score` and `POST /api/v1/score/compare` document their 200 through the
   decorator's `responses=` mapping (`ScoringResult`, `ScoreComparison`), so the generated
   contract carries a `$ref` (`FR-451`, `FD-1335`).
2. `responses=` is read only when the OpenAPI document is built: the route has no
   `response_model` and no `response_field`, so nothing validates the response. Documenting
   a response is not validating it, and this amendment does not permit `response_model=` or
   a Pydantic return annotation.
3. The re-measured model-level p99 for each shape DP-A2 names (validate-and-serialise and
   serialise-only), with the tree measured at, beside the 0.070 ms it supersedes as the
   current figure.
4. The route-level `/score` p99s, base and HEAD, with both trees.
5. The rule and every budget are unchanged, citing `RL-9783` (re-pointed at mint).

The amendment cites `RL-9783`, not the ledger alone. `/score/compare` is named in clause 1
because `PL-9788` Acceptance 8 tags its new test `NFR-502`; that tag rests on this clause,
which makes explicit that the rule's *"scoring endpoint"* covers both routes that serialise a
trusted `ScoringResult`. This is a clarification of the requirement's scope, not a new
requirement: `/score/compare` already returns a raw `Response` (`score.py:376`) for the same
reason.

### DP-A2: option (c), both limbs, script inline in the ledger, with these specifications

**Limb 1, model level** (the requirement's own figure). At the executor's base after
`SL-1345` merges, build two `ScoringResult`s with `model_validate`, every field the then-current
`LadderRung` defines populated:
- **Shape U (served by default, untraced, `RL-862`):** `outcome="quoted"`; a valid
  `bundle_hash`; a `premium_ladder` carrying one rung per `LadderRungName` value, each with
  an `operation`; 60 entries in `outputs` (the w8 note's "60 factors"); `timing_ms` with 3
  keys; `trace=None`.
- **Shape T (traced, the w8 note's "20 rate steps"):** Shape U plus a `Trace` of 20
  `TraceStep`s, each with 3 `consumed` and 3 `produced` entries.

For each shape, time two operations with the w8 method (`time.perf_counter`, 1000
iterations after 100 discarded warm-up iterations, p99 = the 990th sorted value): **V+S**
`ScoringResult.model_validate(d).model_dump_json()` (what the 0.070 ms measured) and **S**
`r.model_dump_json()` on a pre-built result (what the route does). Run the whole set
**three times**; quote p50, p99 and max for each of the 12 runs.

**Limb 2, route level** (the route as changed). An in-process client posting to
`/api/v1/score` with `score_one` monkeypatched to return a pre-built Shape U result, the
same harness as `test_score.py:341-380`, 100 warm-up then 1000 timed requests, p99 = the
990th sorted value. Run it on the **base** tree and on **HEAD**, alternating
**base, HEAD, base, HEAD, base, HEAD**, so drift falls on both. Quote all six p50/p99/max.

**Limb 3, structural** (the discriminator neither timing limb provides). At HEAD, quote the
output of a one-liner that prints, for the `/api/v1/score` and `/api/v1/score/compare` POST
routes of the built app, `route.response_model` and `route.response_field` (both `None`
expected), and their 200 schemas from `app.openapi()` (a `$ref` each).

**Reading the figures.** No limb fails `NFR-502` on a number: the requirement is a design
rule, and the 50 ms budget is `NFR-489`'s. The figures are quoted beside 0.070 ms and 50 ms.
Two outcomes **stop the slice and go to the lead** before Task 4 is written:
- limb 3 prints anything other than `None`, `None` and a `$ref` for either route; or
- HEAD's median route-level p99 exceeds base's median by more than base's own range across
  its three runs (max p99 minus min p99). That threshold is the measurement's own noise, not
  a chosen number.

**Script, environment, record.** One script for limbs 1 and 3, one for limb 2, both inline in
the ledger with their sha256 prefixes, run in the lead's solo window under `PL-9788` Task 5's
conditions (`uptime`, `free -h`, both `flock -n` slot reads, before and after). No file under
`scripts/` is added.

## Acceptance — the violation that must become detectable

**DP-A1** — detectable if the amendment is missing, widened or rewrites earlier text:
- `git diff <base>..HEAD -- docs/specs/03-rating-engine.md` touches exactly one line, the
  `NFR-502` row, and the change is one appended `*(Amended 2026-…, … RL-9783 …)*` block; the
  rule's first sentence and both earlier amendments are byte-identical.
- The block contains `responses=`, `/score/compare`, a figure in ms with a 40-hex tree for
  the model level, and two trees for the route level.
- `python3 scripts/audit-docs.py` reports only check 31 (working ids) red while ids are
  unminted.

**DP-A2** — detectable if a limb is skipped or the figures are not the measured ones: the ledger carries 12 limb-1 rows, 6 limb-2 rows
labelled base/HEAD with both trees, the limb-3 output verbatim, both scripts with sha256
prefixes, and the before-and-after load readings; and the `NFR-502` amendment's figures
(DP-A1 clauses 3 and 4) are the medians of those rows.

## What it obliges

- **`PL-9788` Task 4** writes the amendment as DP-A1 rules, after Task 5.
- **`PL-9788` Task 5** runs DP-A2's three limbs. Where the plan's Task 5 and this ruling
  differ (three repetitions, warm-up, alternation, limb 3, the stop conditions), **the ruling
  wins** (`PL-9788` activation need 5), and the dispatch record names each difference.
- **`PL-9788` Acceptance 8** (the `/score/compare` `NFR-502` test) is the behavioural limb for
  the second route; DP-A1 clause 1 is what its `NFR-502` tag rests on.

## Spec changes in this commit

**None.** The `NFR-502` amendment is recorded here and applied by the slice (`PL-9788`
Task 4), because its clauses 3 and 4 quote figures that do not yet exist.

## Observed, not ruled (for the lead)

- **`RL-1343` §5's last bullet** says the slice that carries rule 4 *also* re-measures
  `NFR-502`. If DP-A3 is ruled (a) (separate slices), the rule-4 slice can reuse this
  ruling's limb 1 and limb 2 scripts from `PL-9788`'s ledger, so its figure is comparable.
  That is the lead's or that slice's planner's to adopt.
- **The w8 note has no script**, so the 0.070 ms figure cannot be reproduced exactly; limb 1
  re-expresses the shape in today's fields. The amendment's clause 3 calls the new figure
  the *current* one rather than claiming it confirms the old one.
