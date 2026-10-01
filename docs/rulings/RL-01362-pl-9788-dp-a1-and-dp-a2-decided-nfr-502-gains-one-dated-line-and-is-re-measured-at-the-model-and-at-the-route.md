---
id: RL-1362
family: ruling
title: PL-9788 DP-A1 and DP-A2 decided — NFR-502 gains one dated line naming responses= as documentation that validates nothing, and is re-measured at the model and at the route, base against HEAD
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
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

# RL-1362 — PL-9788 DP-A1 and DP-A2 decided: `NFR-502` gains one dated line naming `responses=` as documentation that validates nothing, and is re-measured at the model and at the route, base against HEAD

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
   (`git log --oneline -1 214fd4d7` shows its activation, which is an ancestor of
   `9b0fb97c`; no later commit to `101e32dc` delivers it). *(Corrected at the text-fix
   pass, audit F1: the command cited here was `git log --oneline 9b0fb97c..101e32dc`, which
   cannot show `214fd4d7` because that commit is an ancestor of `9b0fb97c`.)* It changes `LadderRung` (`03` FR-248's 2026-09-30 amendment: each rung
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
the executor in `PL-9788` Task 4 **after** Task 5 so it quotes measured figures. It says
these five things and nothing more, in the exact text given under *The exact text* below:

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
4. The route-level p99s, base and HEAD, with both trees: `/score`, and `/score/compare`
   stated as measured, with no new target.
5. The rule and every budget are unchanged, citing `RL-1362` (re-pointed at mint).

The amendment cites `RL-1362`, not the ledger alone.

### The exact text

*(Added at the final pre-mint text pass, 2026-10-01, on the maintainer's exact-text rule.)*
Placement: `docs/specs/03-rating-engine.md`, the `NFR-502` row (`03:1203` at `origin/main`
`65fc6129`). The text is **appended** as a dated note at the end of the row's second cell,
after `` Ruled in `docs/rulings/RL-00883-f1-nfr-502-is-amended-to-the-property-it-was-always-about-orjson-is-not-added.md` RL-883.)* `` and one space, before the closing ` |`. Nothing is struck, and
the rule's first sentence and both earlier amendments stay byte-identical.

The placeholders are: `<Task 4 date>`, the date of the Task 4 commit; `RL-1362`, this
ruling's minted id; and, from the DP-A2 ledger rows, `<limb 1 tree, 40 hex>`, the four limb-1
medians (`<V+S untraced p99>`, `<V+S traced p99>`, `<S untraced p99>`, `<S traced p99>`, in ms
to three decimal places), the four limb-2 medians (`<score base p99>`, `<score HEAD p99>`,
`<compare base p99>`, `<compare HEAD p99>`, in ms to two decimal places), and `<base tree, 40
hex>` and `<HEAD tree, 40 hex>`. Every other word is fixed. Each sentence maps to a clause
above: the first two bold runs are clauses 1 and 2, "Re-measured" is clause 3, "Route level" is
clause 4, and the last sentence is clause 5.

```text
*(Amended <Task 4 date>, PL-9788 Task 4 — `RL-1362` DP-A1; the scope extension to `/score/compare` accepted by the maintainer, by delegation, 2026-10-01. **Two routes document their 200, and this requirement's scope extends to the second.** `POST /api/v1/score` and `POST /api/v1/score/compare` document their 200 through the decorator's `responses=` mapping (`ScoringResult`, `ScoreComparison`), so the generated contract carries a `$ref` (`FR-451`, `FD-1335`). Naming `/score/compare` is a dated scope extension of this requirement, not a clarification: compare serialises a `ScoreComparison`, and it too returns a raw `Response` built from trusted models. **`responses=` is documentation, not validation.** It is read only when the OpenAPI document is built. Neither route has a `response_model` or a `response_field`, so nothing validates the response. Documenting a response is not validating it, and this amendment does not permit `response_model=` or a Pydantic return annotation. **Re-measured at `<limb 1 tree, 40 hex>`**, each figure the median of three runs of the p99 of 1000 iterations after 100 warm-up: validate-and-serialise <V+S untraced p99> ms untraced and <V+S traced p99> ms traced (20 rate steps); serialise-only, the route's own operation, <S untraced p99> ms untraced and <S traced p99> ms traced. These are the current figures. They supersede the 0.070 ms above as the current figure and do not confirm it. **Route level**, in process with `score_one` stubbed so that no GBM runs, each figure the median p99 of three alternating runs: `/score` <score base p99> ms at base `<base tree, 40 hex>` and <score HEAD p99> ms at `<HEAD tree, 40 hex>`; `/score/compare`, stated as measured with no new target, <compare base p99> ms at base and <compare HEAD p99> ms at HEAD. **The rule and every budget are unchanged**: NFR-489's 50 ms, and 15 ms without a GBM call.)*
```

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop.

**Naming `/score/compare` in clause 1 is a dated scope extension of `NFR-502`, not a
clarification.** *(Corrected at the text-fix pass, audit F2.)* An earlier text of this
paragraph called it a clarification, on the ground that compare serialises a trusted
`ScoringResult`. It does not: it serialises a `ScoreComparison` (`score.py:376`). Naming a
second route widens the requirement, so the scope decision is the maintainer's. The
maintainer decided it, in the entry headed *"2026-10-01 08:14:25 BST — ruling-audit fixes:
dm-fixes at MEDIUM agreed; one scope decision (RL 9783 F2); RL 9782 F1 is a likely stop; FD
9780 MEDIUM confirmed by me"* in the lead's channel:

> *"2026-10-01 — the maintainer (by delegation) accepts extending NFR-502's measured scope
> to `POST /api/v1/score/compare`. That route serves the same raw `Response` path that PL
> 9788 adds a documented 200 schema to, so the no-validation claim must be measured on both.
> This is a scope extension made before the 3 Oct freeze. The budget for compare is stated
> as measured (no new target invented); a regression is a stop."*

The true reason is the one quoted: compare also returns a raw `Response` built from trusted
models, so the same rule applies and must be measured. `PL-9788` Acceptance 8 tags its
compare test `NFR-502`; that tag rests on this extension. The amendment's clause 1 says it
is a scope extension and cites this record.

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
*(Added at the text-fix pass, on the maintainer's F2 decision.)* Run the same harness, in
the same alternation, against `/api/v1/score/compare`, with `score_one` returning a
pre-built Shape T result (compare calls it with `trace=True`, `score.py:362`). Quote those
six p50/p99/max too. Compare's figure is stated as measured; no target is set for it.

**Limb 3, structural** (the discriminator neither timing limb provides). At HEAD, quote the
output of a one-liner that prints, for the `/api/v1/score` and `/api/v1/score/compare` POST
routes of the built app, `route.response_model` and `route.response_field` (both `None`
expected), and their 200 schemas from `app.openapi()` (a `$ref` each).

**Reading the figures.** No limb fails `NFR-502` on a number: the requirement is a design
rule, and the budgets are `NFR-489`'s: *"Real-time scoring p99 < 50 ms server-side at 200 rps per replica for a ~200-step motor
structure with one `exact` GBM call (NFR-454). Without a GBM call, p99 < 15 ms."* (`03:1190`). *(Amended at
the text-fix pass, audit F3.)* Limb 1 measures one component of either path and is quoted
beside 0.070 ms, 50 ms and 15 ms. Limb 2 stubs `score_one`, so no GBM runs: its figures are
read beside the 15 ms no-GBM budget, not the 50 ms one. Limb 3 is structural and has no
budget.
Two outcomes **stop the slice and go to the lead** before Task 4 is written:
- limb 3 prints anything other than `None`, `None` and a `$ref` for either route; or
- for either route, HEAD's median route-level p99 exceeds base's median by more than base's
  own range across its three runs (max p99 minus min p99). That threshold is the measurement's own noise, not
  a chosen number.

**Script, environment, record.** One script for limbs 1 and 3, one for limb 2, both inline in
the ledger with their sha256 prefixes, run in the lead's solo window under `PL-9788` Task 5's
conditions (`uptime`, `free -h`, both `flock -n` slot reads, before and after). No file under
`scripts/` is added.

## Acceptance — the violation that must become detectable

**DP-A1** — detectable if the amendment is missing, widened or rewrites earlier text:
- `git diff <base>..HEAD -- docs/specs/03-rating-engine.md` touches exactly one line, the
  `NFR-502` row, and the change is one appended `*(Amended 2026-…, … RL-1362 …)*` block; the
  rule's first sentence and both earlier amendments are byte-identical.
- The block contains `responses=`, `/score/compare`, a figure in ms with a 40-hex tree for
  the model level, and two trees for the route level.
- `python3 scripts/audit-docs.py` reports only check 31 (working ids) red while ids are
  unminted.

**DP-A2** — detectable if a limb is skipped or the figures are not the measured ones: the ledger carries 12 limb-1 rows, 12 limb-2 rows
(6 for `/score`, 6 for `/score/compare`) labelled base/HEAD with both trees, the limb-3 output verbatim, both scripts with sha256
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

**None.** The `NFR-502` amendment is recorded here as exact text (*The exact text*, under
DP-A1) and applied by the slice (`PL-9788` Task 4), because its clauses 3 and 4 quote figures
that do not yet exist. The slice fills the placeholders and changes no other word.

## Observed, not ruled (for the lead)

- **`RL-1343` §5's last bullet** says the slice that carries rule 4 *also* re-measures
  `NFR-502`. If DP-A3 is ruled (a) (separate slices), the rule-4 slice can reuse this
  ruling's limb 1 and limb 2 scripts from `PL-9788`'s ledger, so its figure is comparable.
  That is the lead's or that slice's planner's to adopt.
- **The w8 note has no script**, so the 0.070 ms figure cannot be reproduced exactly; limb 1
  re-expresses the shape in today's fields. The amendment's clause 3 calls the new figure
  the *current* one rather than claiming it confirms the old one.

Drafted as working id 9783; minted 2026-10-01 as RL-1362.
