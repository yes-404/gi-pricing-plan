---
id: RL-1329
family: ruling
title: DP-S3-5 decided — the premium ladder records each rung's exact unrounded value and the operation it applied, and reconciles by an exact replay that rounds once
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: fa9a73c2d8b5cfebf4c699961015e6ff8dde1fb1
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1237, RL-1312, RL-862, FR-226, FR-240, FR-247, FR-248, FR-261, FR-273, FR-275, NFR-496, OQ-1316]
---

# RL-1329 — DP-S3-5 decided: the ladder carries each rung's exact unrounded value and the operation it applied, and reconciles by an exact replay that rounds once

## How this was ruled

**Ruled at effort `high`.** The maintainer ordered a fresh high-effort decision-maker for this
decision in `to-lead.md`, in the entry headed "2026-09-30 15:33:22 BST — DECISIONS on N5 (the
ladder builder's drift): fold into FD 9949 → HIGH; the builder design is a DP for a fresh
high-effort DM". This session's first command printed `CLAUDE_EFFORT=high`.

**Minted 2026-09-30 as RL-1329** (`python3 scripts/doc-id.py next --ref 3229ac6d54952b302c5fb0fa615b4e7b3d52a4df` printed `1329`, and the lead allocated it in mint batch 9). It was filed under working id 9963, hand-assigned by the lead. Quotations of the maintainer's entries keep "RL 9963" as written, and so does the appendix script's docstring, whose bytes are hashed.

**Sources.**
- The decision point is DP-S3-5 of the WK-674 Slice 3 (SL-1257) leaf plan, working id 9947,
  read at `06e3e8969e9932d58d43b4e4ce9ae4a6df8d858a` in the planner's worktree
  (under `docs/plans/`, the file whose slug is `wk-674-slice-3-environment-isolation-leaf-plan`). I read its
  Acceptance 10 (`:214-305`), DP-S3-1 (`:403`) and Acceptance 1 (`:100-115`). The plan is
  not minted, so it is cited as prose. It is frozen (`document-ids.md` §1.5): this record is
  the delta, and the plan is not edited.
- The finding is filed under working id 9949. The maintainer's 15:33:22 entry folds this
  drift into it as limb 2, at severity HIGH. It is not on `main`, so it is cited as prose.
- The maintainer's steer, quoted from that entry, item (2): "the ladder must show the **true
  operations an actuary recognises** (the rating table's own factor, e.g. ×1.05, **not** a
  back-derived ×1.0515 or a fabricated ratio), **and** reconcile to the penny"; "a candidate:
  rungs carry the **exact unrounded running value** (Decimal) alongside the displayed rounded
  value; operations are the true factors; **reconciliation replays on the unrounded chain**,
  and only the final `round` rung rounds, so rounding happens once (FR-226/NFR-496) and the
  replay equals payable exactly". The same entry says that **the scale-sweep control
  (~1e3–1e7 minor units) is required** in S3's acceptance, with a realistic-scale red case.

## Verified first, at fa9a73c2d8b5cfebf4c699961015e6ff8dde1fb1

`origin/main` moved from `e3600789` to `fa9a73c2` while I worked (mint batch 4, #994). That
merge changed only one row in `03`, the OQ-1316 row at `:1186`. `git diff --stat 11c76b6c
fa9a73c2` over `score.py`, `money.py`, `runtime.py`, `model_schema/scoring.py`,
`scoring.schema.json` and `test_rating_score.py` is empty. So the auditor's tree
(`11c76b6c`) and this tree hold the same code. Every citation below is at `fa9a73c2`.

| Premise | Where | What the source says |
|---|---|---|
| A rung's value is read as a float | `packages/pricing-core/src/pricing_core/rating/score.py:592` | `raw = float(result[source_key])` |
| A multiply factor is a ratio to the **rounded** previous rung, cut to 4 dp, then reapplied | `score.py:609-611` | `factor = (Decimal(repr(raw)) / Decimal(prev_minor)).quantize(Decimal("0.0001"))`, then `value_minor = apply_factor(prev_minor, factor, mode)` |
| The payable rung is the raw output rounded, **labelled** `round` | `score.py:598-600` | `value_minor = _round_minor(raw, mode)`; `operation = LadderOperation(kind="round", …)` |
| The module docstring claims reconciliation "by construction" | `score.py:97-103` | "the ladder reconciles **by construction**, to the penny" |
| `outputs` reuses the rung values | `score.py:626-644`, `:641` | `outputs[declared.name] = by_rung[rung_name]` |
| The check is vacuous at its call site | `score.py:737-738`; `pricing_core/money.py:55-70` | The first rung is passed as the risk premium, and the rest of the check is int-ness |
| The manual re-derivation test does not replay the `round` rung | `packages/pricing-core/tests/test_rating_score.py:224-225` | `elif op.kind == "round": value = rung.value_minor`. It assigns the recorded value, so drift before the payable rung cannot fail it |
| The contract shapes | `packages/model-schema/src/model_schema/scoring.py:63`, `:108-124`, `:127-135`; `docs/contracts/schemas/scoring.schema.json:25-45`, `:59-62` | Four kinds; `factor` a string; `amount_minor` an integer; the FR-248 invariant as text |
| Stored served ladders are compared on re-score | `backend/src/app/platform/traces.py:64`, `:143-150` | `_SUMMARY_FIELDS` includes `premium_ladder` (RL-862 §8.2 (b)) |
| A golden quote compares the payable only | `docs/specs/03-rating-engine.md` §4.7 (`:512-561`) | "`expected` compares `payable_premium_minor` … and `outcome` only" |
| Money crosses the binding as an integer or a string | `03` FR-273 (`:222`) | "any value returning to Python for further arithmetic is an integer minor unit or a string" |
| No rounding function is offered in an expression in P2 | `RL-1312` item 1; `OQ-1316` (`03:1186`) | `round`, `floor` and `ceil` are off the allow-list. "The platform's own generated" ZEN is "outside the check, which reads authored strings before they are wired" |
| The engine version | `packages/pricing-core/pyproject.toml:64` | `zen-engine==0.53.0` |

## Proof — a scratch reproduction on the real builder and the real engine

**Where it ran.** The session scratch directory, which is ephemeral:
`/tmp/claude-1000/-home-puzhenhao1989-gi-pricing-plan/4596a3be-8b6e-4963-aa87-087f2df4e2bb/scratchpad/`.
It is not committed. The interpreter is the root checkout's `.venv` (`zen-engine 0.53.0`,
`numpy 2.5.2`), with `PYTHONPATH` set to this worktree's `packages/pricing-core/src` and
`packages/model-schema/src`. `python -c 'import pricing_core.rating.score as s; print(s.__file__)'`
under the same environment printed this worktree's `score.py`, which proves which builder the
script imports. It is reproduced in full in the appendix, sha256
`7c39cf44e1827e0f98e0172a2e239b15e759273610923cd7089ae0a644675a4b`. *It was re-run in full on each audit round of 2026-09-30, each time with counters added and none changed: the clamp case and the magnitude counter (`05b92737…`); the relative-error counters for S4 (`36179350…`); the quote-wide sum for R1 (`13a8a195…`); the own term (`78106d73…`); and the exact bound (`7c39cf44…`, the appendix). Every earlier figure reproduced unchanged each time.*

**Steps.**
1. `git worktree add <path> fa9a73c2` (any checkout of this tree).
2. `export PYTHONPATH=<path>/packages/pricing-core/src:<path>/packages/model-schema/src`
3. The four runs, verbatim: `python dp_s3_5_evidence.py 200 20260930 x`, `… 200 7 x`,
   `… 500 1257 x` and `… 300 42 mixed x`. The third argument `mixed` puts rungs that apply
   more than one operation into the sweep. In that run, the trailing `x` turns on the
   `MISS` lines, which name any rung whose recorded operation differs from the applied one;
   none printed. In the other three runs the `x` has no effect (`len(sys.argv) > 4` is
   false). The final runs (`7c39cf44…`) were made with the script saved as `work_v8.py`,
   so that the previous version could finish its own runs under the other name; the
   content is the appendix, byte for byte.

**What it builds.** A real ZEN decision: one expression node per rung, and one final node
that reads every value with the engine's `string()`. It then runs:
- `today` — `origin/main`'s real `_build_ladder` on the float values the binding returns;
- `replay_today` — the S3 plan's Acceptance 10 replay (`multiply` → `apply_factor`, `add` → `+`,
  `round`/`none` → unchanged);
- `build_ruled` and `reconciles` — a prototype of this ruling's builder and predicate;
- `plants` — deliberately broken ladders that the predicate must refuse;
- `clamp_case` — FD 9967's clamped ladder, built with the clamp node's generated
  `__before` and `__bound` reads (part 5).

### Results

**1. The binding.** A chain of eight table factors from a 13-digit value:

| Step | Float from the binding equals the exact product? | `string()` equals it? | Digits |
|---|---|---|---|
| ×1.15 | yes | yes | 15 |
| ×1.131 … ×1.0375 | **no**, from the second step | yes | 18 to 29 |
| ×0.985 | no | **no** | 29 |

- **A float loses exactness after one or two rungs. `string()` stays exact** until the
  engine's own precision runs out.
- **The engine rounds its own intermediates at 28–29 significant digits.** The eighth
  product has 30 digits exactly, and the engine returned 29 digits.
- **The engine converts an input float differently from Python.** Python's
  `repr(1e7/3)` is `3333333.3333333335`, and the engine's string is `3333333.333333334`. So
  the first rung's exact value must also come from the engine, never from `repr`.
- **The float path can misprice at a near-tie.** For an engine value of
  `1234.50000000000000012345`, the float is `1234.5`, and today's `_round_minor` gives
  **1234**. The exact value rounded once gives **1235**. For `1235.49999999999999987645`,
  the float path gives 1236 and the exact path 1235. The sweeps below found no such case in
  realistic data (`payable_differs: 0`), but the mechanism is real.

**1a. `DecimalStr` serialises exponent form** (added on audit, B2). Run at `fa9a73c2` with
the same interpreter and `PYTHONPATH`:

```text
$ python -c "
from pydantic import BaseModel
from model_schema.money import DecimalStr, Relativity
class M(BaseModel):
    a: DecimalStr
    r: Relativity
for s in ('0.0000001','0.00000000000000000000000000012','10','1E+1','66000.440'):
    m=M(a=s, r=s); print(repr(s), '->', m.model_dump_json())
"
'0.0000001' -> {"a":"1E-7","r":"1E-7"}
'0.00000000000000000000000000012' -> {"a":"1.2E-28","r":"1.2E-28"}
'10' -> {"a":"10","r":"10"}
'1E+1' -> {"a":"1E+1","r":"1E+1"}
'66000.440' -> {"a":"66000.440","r":"66000.440"}
```

**2. The auditor's case on today's builder** (raw 60000.4 → 66000.44 → 69402.0), reproduced:
`risk 60000 · expense 66000 (×1.1000) · office 66000 · constraints 66000 · instalment 69399
(×1.0515) · payable 69402 (round)`. The replay gives **69399 ≠ 69402**.

**3. A worked 9-rung ladder at risk 60000.4.** Expense ×1.15, commission ÷(1 − 0.125),
profit ×1.07, optimisation ×0.9601, instalment ×1.05, IPT and fees ×1.12 + 250.

| Rung | Today | Ruled: `value_minor` | Ruled: `unrounded_minor` | Ruled: operation |
|---|---|---|---|---|
| risk_premium | 60000 | 60000 | 60000.4 | — |
| expense_loading | 69000 ×1.1500 | 69000 | 69000.460 | ×1.15 |
| commission | **78860 ×1.1429** | 78858 | 78857.668571428571428571428571 | **÷0.875** |
| profit_loading | 84380 ×1.0700 | 84378 | 84377.70537142857142857142857 | ×1.07 |
| office_premium | 84380 ×1.0000 | 84378 | (same) | none |
| optimisation_adjustment | 81013 ×0.9601 | 81011 | 81011.03492710857142857142857 | ×0.9601 |
| constraints | 81013 | 81011 | (same) | none |
| instalment_loading | 85064 ×1.0500 | 85062 | 85061.58667346400000000000000 | ×1.05 |
| ipt_and_fees | 95519 **+10455** | 95519 | 95518.97707427968000000000000 | +10457.39040081568000000000000 |
| payable_premium | 95519 round | 95519 | (same) | round, half_even |

Today's replay reaches 95519, because the `add` rung absorbs the drift. But **six rungs are
misstated by 1–2p, the commission factor is back-derived (×1.1429 for ÷0.875), and the IPT
amount is 2p wrong.** An exact replay that only checks the payable rung would miss all of
that. This is why the predicate below checks every rung.

**4. A fixture-shaped red case** (the shape of `test_rating_score.py`'s fixture: office = risk
× 1.1 from a table, instalment = office × 1.05). At risk **61234.5**, today's ladder is
`61234 · 67357 (×1.1000) · 67357 · 70725 (×1.0500) · 70726 (round)`. The replay gives
**70725 ≠ 70726**. The ruled ladder is `61234 · 67358 (×1.1) · 67358 · 70726 (×1.05) ·
70726`, and it reconciles. At 123456.7, today's replay gives 142593 ≠ 142592.

**5. A binding clamp** (added on audit, C1; FD 9967's reproduction shape). Risk 1305.4,
office = risk × 1.1, a minimum-premium clamp at 5000 on office, instalment = office × 1.05:

| Rung | Today | Ruled |
|---|---|---|
| risk_premium | 1305 | 1305 (1305.4) |
| office_premium | **5000, ×3.8314** | 1436 (1435.94), ×1.1 |
| constraints | 5000, `none` | 5000, **`clamp` min 5000**, `MIN_PREMIUM_APPLIED` |
| instalment_loading | 5250, ×1.0500 | 5250 (5250.00), ×1.05 |
| payable_premium | 5250 | 5250, round |

The clamp's generated node returned `__before` = 1435.94 and the clamped value 5000 under
the same name. The ruled ladder reconciles. With the minimum at 1000 (not binding), the
`constraints` rung is `none` and the ladder reconciles. Two planted defects fail: the bound
+ 0.001, and the clamp recorded as `none`.

**6. The scale sweep.** Premiums in every decade from 1e3 to 1e7 minor units, drawn as
`float32` values like a real model's output. Every optional-rung count from 0 to 6. One
random rung subset per (decade, count) cell. Table factors of 4 dp in [0.8, 1.4]; one
gross-up rung (÷(1 − 0.125)); one IPT rung (×1.12 + 250).

| Run | Quotes | Today: replay ≠ payable | Today: a rung ≠ its own value rounded once | Today: factor ≠ the one applied | Ruled: not reconciled | Ruled: operation ≠ the one applied | Planted broken ladders | Planted, not caught |
|---|---|---|---|---|---|---|---|---|
| `200 20260930` | 7000 | 1997 | 4142 | 1634 | **0** | **0** | 66200 | **0** |
| `200 7` | 7000 | 1551 | 3980 | 1452 | **0** | **0** | 66600 | **0** |
| `500 1257` | 17500 | 4390 | 10435 | 3533 | **0** | **0** | 168000 | **0** |
| `300 42 mixed` | 10500 | 2532 | 6724 | 1062 | **0** | **0** | 98400 | **0** |

Where a cell shows 0 for today's replay, the last loading is the `add` rung, which absorbs
the drift. The misstated-rung column shows that the drift is still there.

**How large today's misstatement is** (added on audit, W2). The predicate, verbatim from the
script: for every rung of today's ladder that is present and is not `payable_premium`,
`abs(r.value_minor - rnd(values[present[r.rung]]))`, where `values` is the engine's exact
`string()` value and `rnd` rounds half-even to 0 dp. Counted over the corpus of each run
above, at tree `fa9a73c2`:

| Run | Max by decade: 1e3 / 1e4 / 1e5 / 1e6 / 1e7 | Rungs off by 1 · 2 · 3–9 · ≥10 minor units |
|---|---|---|
| `200 20260930` | 1 / 8 / 101 / 951 / **9997** | 2052 · 682 · 1848 · 9012 |
| `200 7` | 1 / 9 / 82 / 1050 / 12521 | 2958 · 837 · 1837 · 7152 |
| `500 1257` | 1 / 11 / 101 / 1089 / 11724 | 7423 · 2015 · 4475 · 19005 |
| `300 42 mixed` | 1 / 9 / 59 / 428 / 7820 | 3287 · 1409 · 4158 · 14300 |

**Relative to the value** (added on the second re-audit, S4), the script prints two
maxima over the same non-payable rungs. With the one rounding unit included,
`diff / value`, the largest are 6.696 × 10⁻⁴, 7.683 × 10⁻⁴, 9.906 × 10⁻⁴ and
8.309 × 10⁻⁴ — each a 1-minor-unit difference on a value near 1e3, so that ratio measures
the rounding unit, not the drift. With the rounding unit taken out, `(diff − 1) / value`,
the largest are **4.453 × 10⁻⁵** (seed 20260930), **4.854 × 10⁻⁵** (seed 7), **4.445 × 10⁻⁵**
(seed 1257) and **4.607 × 10⁻⁵** (seed 42, mixed). The maximum over the four runs is
**4.854 × 10⁻⁵**, on an `optimisation_adjustment` rung whose factor is below 1. This
figure supports the maintainer's "about 1e-4". It is not Acceptance 8's stop bound, which
is the exact per-rung bound derived from the mechanism (see there).

The cause is today's 4-dp factor quantisation (`score.py:610`). Each factor can be off by up
to 5 × 10⁻⁵, so a rung is off by up to about 10⁻⁴ of its value. "1–2p" holds only at
fixture scale (about 1e3). The quotes affected are the misstated-rung column of the sweep
table: 4142 of 7000 (59 %) in seed 20260930, and 57–64 % across the four runs.

**Payable near-tie flips** (condition 3 of the maintainer's W2 entry). The predicate,
verbatim: `v1[-1].value_minor != payable`, today's payable rung (the float path) against
the engine's exact payable value rounded once. The counts are **0 of 7000** (seed 20260930),
**0 of 7000** (seed 7), **0 of 17 500** (seed 1257) and **0 of 10 500** (seed 42, mixed) — 0
of 42 000 in all, at tree `fa9a73c2`. So the maximum payable delta observed is **0**. A flip
can only move a payable by exactly 1 minor unit, because both paths round the same value
to 0 dp and differ only in which side of a half the float lands. The two constructed cases
in part 1 show that it can happen (1234 → 1235, 1236 → 1235).

**Two design defects the sweep found in my own first prototype, both fixed before this
ruling.** They are recorded so that S3 does not repeat them.
- **A gross-up recorded as a truncated factor fails at a tie.** 746941.5625 ÷ 0.875 is
  exactly 853647.5, a tie. As ×1.14285714285714285714285714, the replay reaches
  853647.4999…, which rounds to 853647, and the payable is 853648. The first prototype
  (sha256 `bdab7ea8…`) failed 15 of 500 quotes in seed 1257's (1e5, commission-only) cell
  this way. **Fix: a `divide` operation with
  the exact divisor.**
- **The second prototype preferred the shorter operand, and it tested "at the engine's
  precision limit" by counting digits.** It recorded four ×1.25 table factors as ÷0.8. It
  also recorded nine ÷0.875 gross-ups as `add`, because the engine's rounded value had only
  27 digits. **Fix: an exact factor first, then an exact divisor, then a short operand
  (fewer than 20 significant digits) within the engine's precision, else the exact amount
  added. No digit count is used.**

## Ruled

### 1. The option: the steer, adopted, with three departures, each forced by the engine

**Ruled: neither (a) nor (b). The ladder records the engine's exact unrounded value on every
rung, and each operation is the one the rung applied. Reconciliation replays on the
unrounded chain in exact decimal arithmetic, and it rounds once, at the payable rung.**
FR-248 is amended to say so, in this commit.

**(a) as posed is rejected.** Building each rung from the previous *rounded* rung plus its
operation, and making the payable rung `round(prev)`, is the S3 plan's Acceptance 10 replay. It
rounds at every multiply rung, so it breaks FR-226 ("never happens twice") and NFR-496. It
cannot in general equal the engine's price, which rounds once: that replay over today's
builder misses the payable on 1551 to 1997 of every 7000 sweep quotes above. With true
factors applied to rounded values, (a) changes the price. With factors back-derived to hit
the price (×1.0515, ×1.1429), it misstates them, and the maintainer ruled that out.

**(b) is rejected.** A final `adjust` carrying the residual records the misstatement instead
of removing it. The residual has no cause on any rung, so the ladder would still say that
commission was 78860 when it was 78858. It is also an operation outside FR-248's "factor
or amount". And it would make the reconciliation pass by construction, which is how FD
9949's vacuity began.

**The steer is adopted, with three departures.**
1. **Where the unrounded value comes from.** The steer does not say. Today's float cannot
   carry it (results, part 1). **Ruled: the engine's own exact decimal, read across the
   binding with the engine's `string()`, never the float.** This is FR-273's string limb.
   The first rung is read the same way, because the engine's conversion of an input float
   differs from `repr`.
2. **"Exact" at the unrounded level means "to the engine's precision" for each rung's own
   check.** The engine rounds its own intermediates at 28–29 significant digits (part 1).
   So an exact equality between a replayed product and the engine's value would fail on
   realistic quotes that have a float model output at the base and several rungs above it.
   **Ruled: each operation must reproduce its own rung's unrounded value within 10⁻²⁶ of it,
   relative.** One engine rounding is about 10⁻²⁸ relative, so this has a 100× margin.
   auditor-plans measured the worst case over this ruling's sweep corpus at 2.7 × 10⁻²⁹,
   about 370× inside it (*corrected on audit: this line first said 10×*). At 1e7 minor
   units the tolerance is about 10⁻¹⁹ minor units. **The chained replay to the
   payable is exact at the penny**, which is FR-248's own statement.
3. **"The true factor" includes the true divisor.** A commission gross-up, ÷(1 − c), has no
   finite decimal factor. Recorded as a truncated factor, its replay fails at ties (the
   first defect above). **Ruled: a `divide` operation**, so the ladder shows ÷0.875, which is
   what the rate manual says.

**A binding clamp is a `clamp` operation on the `constraints` rung** (*added on audit,
finding C1, 2026-09-30; the maintainer confirmed that C1 is ruled in this record*). Today
a clamp's effect is carried by the rung it overwrites, and the `constraints` rung says only
`none` (the finding filed under working id 9967). An `add` of the exact difference would
replay correctly, but it states an addition, and a minimum premium is not an addition. So
the ladder records what the clamp did: it set the value to a named bound. The rung before
`constraints` carries the value before the clamp, read from the engine by the clamp's own
generated node (part 5). The details are in §2, §3 and §5.

**Not an ADR.** The decision is one module's contract. `03` owns it through FR-248, and
`model-schema`, `pricing-core` and the backend trace summary only carry it. It is
reversible by a later ruling while no stored ladder of the new shape exists outside
development.

### 2. The builder, as S3 implements it

For each rung present in `_RUNG_ORDER` (the fixed order is unchanged):
1. **The value.** `unrounded_minor` is the engine's exact decimal for the name the rung's
   output step consumes, read through `string()` (`to_wire` adds that read as generated ZEN).
   The float in `result` is never used for ladder or payable arithmetic. The `constraints`
   rung carries the previous rung's `rounding` forward. Its `unrounded_minor` is the previous
   rung's value, or, when a clamp binds, the engine's value after the clamp (step 5).
2. **The displayed value.** `value_minor` is `unrounded_minor` rounded once, with the rung's
   own output step's `RoundSpec`, which is recorded as `rounding`. It is never computed from
   another rung's `value_minor`. So displayed values do not multiply into each other: 60000
   ×1.1 is shown as 66000, because the unrounded value is 66000.44. The unrounded column is
   the one that replays.
3. **The operation.** The first rung has none (`null`). The `payable_premium` rung, when it
   is not first, has `round` with its declared `mode` and `dp`. `constraints` has `clamp`
   when a clamp binds (step 5), and otherwise `none`, with `applied` in both cases. `ipt_and_fees`, or any rung whose previous value is 0, has
   `add`. Every other rung, and a checkpoint rung whose value changed (today's "degrades to
   `multiply`" convention, `score.py:89-96`), gets the operation it applied, recovered from
   the two unrounded values in this order:
   1. the **exact factor**, if `cur / prev` terminates and `prev × factor == cur`;
   2. else the **exact divisor**, if `prev / cur` terminates and `cur × divisor == prev`;
   3. else the shortest factor, then the shortest divisor, that reproduces `cur` within
      10⁻²⁶ relative, **if it has fewer than 20 significant digits**. That is a terminating
      operation whose result the engine rounded. A non-terminating ratio needs at least 26
      digits to meet the tolerance, so 20 separates the two cases by 6 orders of magnitude;
   4. else `add`, with `amount_unrounded_minor` = `cur − prev` exactly. That is a rung that
      applied more than one operation. The ladder states what the rung did, and it never
      invents a factor.

   An unchanged non-multiply rung (the `office_premium` checkpoint) is `none`. An unchanged
   multiply rung is ×1.
5. **A binding clamp.** A clamp is a `constraint` step with `on_violation: "clamp"`. It
   overwrites the name it produces in place (`runtime.py:275-279`, `_constraint_node`).
   - **The read.** `_constraint_node` adds generated expressions to the clamp's own node,
     ahead of the clamp expression: `<step_id>__before` = `string(<consumed name>)`, the
     exact value before the clamp, and one `string()` per bound present:
     `<step_id>__min` = `string(<clamp_bounds.min>)` and `<step_id>__max` =
     `string(<clamp_bounds.max>)`, both when both are declared (*named on audit, W-b*).
     Part 5 shows that the engine returns the before value and a bound, and returns the
     clamped value under the name.
   - **The clamp produces the name it consumes** (*ruled on audit, W-b*). The generated
     clamp reads `consumes[0]` and writes `produces[0]` (`runtime.py:296-315`). Only when
     the two are the same name does the clamp overwrite a value in place. A clamp whose
     produced name differs from its consumed name, and is the source of a rung, is refused
     at compile time (below).
   - **"Binds" is the comparison the clamp makes** (*ruled on audit, W-a, by the
     maintainer's entry "2026-09-30 16:41:11 BST — RL 9963 C2 …": "define it by the
     comparison actually used (pre-clamp < bound for a minimum), not in prose"*). With
     `before` = `<step_id>__before`: the `min` side binds when `before < min`; the `max`
     side binds when the value after the `min` side is `> max`. That is exactly the
     generated expression's order and test (`runtime.py:310-314`). It does not depend on
     the authored `condition`, which the generated clamp does not read.
   - **`applied` comes from the disposition**, as today: the reason codes of the clamp
     steps whose `__violated` flag is true (`_apply_constraints`). **If the disposition and
     the comparison disagree** — a step binds but its condition is not violated, or its
     condition is violated but no side binds — the ladder records `applied` from the
     disposition and the operation from the comparison, and R0 fails (§5). The authored
     condition and bounds then contradict each other, and the platform cannot say which
     one priced the quote. What a failure does is DP-S3-1's.
     **This can fail every binding quote of a valid version** (*stated on audit, S5*). `03`
     lets `condition` and `clamp_bounds` be authored separately (§3.2, the `constraint`
     row), and whether they agree depends on values, so no save-time or compile-time check
     can see it. S3's false-positive control therefore counts the quotes on which a clamp's
     comparison and disposition disagree, over every fixture and committed suite. A count
     above 0 stops the slice for the lead.
     These are generated strings, so RL-1312's authored-string check does not read them
     (RL-1312 item 1: generated ZEN is "outside the check, which reads authored strings
     before they are wired").
   - **Where it goes.** When a clamp binds on the source name of **the last rung present
     before `constraints`**, that rung's `unrounded_minor` is the value before the first
     binding clamp on that name, and its operation is recovered against it (step 3). The
     `constraints` rung's `unrounded_minor` is the engine's value after the clamp.
   - **The operation.** `kind: "clamp"`, with `bound` (`"min"` or `"max"`: the side the
     final value equals), `bound_unrounded_minor` (that bound's exact value) and `applied`
     (every binding clamp's reason code, in step order). If two clamps bind on the same
     name, the operation names the last one, which set the value.
   - **A clamp that the ladder cannot place is refused when the algorithm is saved and when
     a bundle is compiled** (*ruled on audit, W-c; placed in the check registry on the
     second re-audit, S1*). A clamp step whose produced name is the source of a rung other
     than the last rung present before `constraints` (an earlier rung, whose later rungs
     before `constraints` consume the clamped value, or a rung after `constraints`) cannot
     be stated at the `constraints` position without breaking the chain. The same applies
     to a clamp whose produced name is a rung's source but differs from its consumed name.
     Both are decidable from the algorithm alone.
     - **Where the check lives: option (b), a registered algorithm check.** It is a new
       `_check_clamp_placement(algo) -> list[ValidationIssue]` in `compile.py`, appended to
       the `ALGORITHM_CHECKS` registry that the in-flight #967 code slice creates (PL-1314,
       "Produces, in `compile.py`": `ALGORITHM_CHECKS: tuple[Callable[[RatingAlgorithm],
       list[ValidationIssue]], ...]`). `validate_algorithm` runs every registered check at
       save (`backend/src/app/platform/rating_algorithms.py:58-69`) and at compile
       (`compile_bundle`, `compile.py:497-499` at `origin/main` `32f3fa92`). So the refusal
       comes at save, which is earlier and better than at compile. It edits no existing
       definition: it appends one function and one registry entry. **It reads only
       `on_violation`, `consumes` and `produces` of a `constraint` step, and the output
       steps' `output_name` and `consumes`**, never `expr`, `condition`, `clamp_bounds` or
       `key_expr`. So it passes #967's closure 3c (i), which bans reading those four fields
       outside the enumerator (*added on the third re-audit, E1*). Option (a), an edit
       inside `compile_bundle`, is rejected: it collides with #967's condition 3 and with
       WK-1250 S2.
     - **The code: a new `LADDER_CLAMP_UNPLACEABLE` (422)**, registered in `03` §5.1 by this
       commit and in `backend/src/app/errors.py` by S3, as a new member of
       `RATING_ERROR_CODES` (`errors.py:297` at `origin/main` `8d5c67a5`). **The same
       ordering condition applies to that edit** (*added on the third re-audit, E1*):
       #967 edits the same frozenset (PL-1314 `:160`), so S3's `errors.py` edit comes after
       #967's code slice merges, as its `compile.py` edit does. The dispatch record names the
       path and RL-1263's check: S3 appends a distinct member and edits no other. S2a's
       `GOVERNANCE_ERROR_CODES` edit has merged (`8d5c67a5`), so it is no longer an
       ordering constraint; the file is shared, nothing more. `BUNDLE_COMPILE_FAILED`, which the
       previous commit named, is a compile code and would mislabel a refusal at save. The
       `ValidationIssue` names the step and the rung, and carries no quote input. The check
       adds no `_raise_named` site: `compile_bundle` raises the first issue through its
       existing site (`compile.py:498-499`). If S3 adds a new `_raise_named` site anyway,
       it lists it in `_INPUT_FREE` in `test_quote_input_raise_sites.py`, as #988 did.
     - **The ordering condition.** S3's `compile.py` edit starts only after #967's code
       slice has merged, because the registry does not exist on `main` until then. The
       dispatch record names this path, and records RL-1263's no-shared-definition check
       against WK-1250 S1 (Task 4: `_producer_types`, `_check_result_types`) and WK-1250 S2
       (`compile_bundle`). The one line S3 shares with them is its entry in the
       `ALGORITHM_CHECKS` tuple, so S3 serialises with any slice that edits that tuple.
     - **The rung mapping moves to a lower module** (*S2*). The mapping from rungs to their
       sources — `_RUNG_ORDER`, `_output_steps_by_name` and the `<rung>_minor` naming — is
       private to `score.py`. `compile.py` cannot import it, because `score` imports
       `runtime` (`score.py:217`), which imports `compile` (`runtime.py:50`). S3 moves it to
       a new `pricing_core/rating/ladder.py` that imports only `model_schema`, and both
       `score.py` and `compile.py` import it from there. **That is an edit of existing
       definitions in `score.py`**, inside S3's own write set.
     - **Reach and consequence** (*S3*).
       - An algorithm with such a clamp can no longer be saved. A Rating Version pinning one
         can no longer be compiled, so it must be re-published on a corrected algorithm as
         a new version.
       - Live scoring reads the stored bundle and does not recompile (`backend/src/app/api/score.py`).
         So a bundle compiled before S3 keeps scoring. On a quote where its clamp binds, R0
         fails at runtime, and DP-S3-1 decides what that does.
       - S3 counts how many committed fixture algorithms and stored bundles in the stores
         this repository reaches the check refuses. A count above 0 stops the slice for the
         lead. **The count covers this repository's fixtures and reachable stores only, not
         any deployment's data.**
     FR-247 puts `constraints` after `optimisation_adjustment`, so an algorithm that clamps
     earlier has a ladder the platform cannot state truthfully.
   - A `decline` or `error` constraint changes no value, as today.
6. **What the ladder never does.** It never records a jump it cannot explain as `round`. If
   the payable source differs from the previous rung's value, the builder still records
   the true `unrounded_minor`, and the predicate fails. It never recovers a factor from
   rounded values, and it never quantises an operand to a fixed number of places.

### 3. The contract shape

`model_schema.scoring` (`scoring.py:63-135`) and the hand-authored
`docs/contracts/schemas/scoring.schema.json` (`:25-45`) change together, and the generated
contract is regenerated.

| Shape | Field | Change | Type and representation |
|---|---|---|---|
| `LadderRung` | `unrounded_minor` | **added** | exact decimal, minor units: `PositionalDecimalStr` (below); JSON `common/money.schema.json#/$defs/Decimal` |
| `LadderRung` | `rounding` | **added** | `{mode, dp}`, JSON `common/money.schema.json#/$defs/Rounding`; the rung's declared rounding |
| `LadderRung` | `value_minor` | meaning restated | `MoneyMinor`: `unrounded_minor` rounded once with `rounding` |
| `LadderOperation.kind` | `divide`, `clamp` | **added** to the enum | `multiply`, `divide`, `add`, `clamp`, `round`, `none` |
| `LadderOperation` | `factor` | type and meaning changed | `PositionalDecimalStr` (was `str`); the factor the rung applied, in full; never quantised to 4 dp |
| `LadderOperation` | `divisor` | **added** | `PositionalDecimalStr`; the `divide` operand |
| `LadderOperation` | `amount_unrounded_minor` | **added** | `PositionalDecimalStr`, minor units; the `add` operand |
| `LadderOperation` | `bound` | **added** | `"min"` or `"max"`; on `clamp` only |
| `LadderOperation` | `bound_unrounded_minor` | **added** | `PositionalDecimalStr`, minor units; the bound the clamp set; on `clamp` only |
| `LadderOperation` | `applied` | meaning widened | reason codes of the binding clamps, on `constraints`, with `clamp` or `none` |
| `LadderOperation` | `amount_minor` | **legacy** | kept only so that stored pre-ruling ladders validate; the builder no longer emits it |
| `LadderOperation` | `mode`, `dp` | narrowed | emitted only on `round` |
| `ScoringResult` invariant | `scoring.schema.json:60` | reworded | to FR-248 as amended |

- **The new fields are optional in both schemas**, not in `required`. Stored ladders are
  write-once and lack them, and `extra="forbid"` models would otherwise refuse to read them.
  **The builder emits every new field that applies to each rung it builds**, and S3 tests
  that.
- **The decimal type: a new `PositionalDecimalStr`, not a change to `DecimalStr`** (*ruled
  on audit, finding B2; this record first said that S3 would render each value with
  `format(value, "f")` before it became a field, and that does not work*). `DecimalStr`
  (`model_schema/money.py:85-91`) re-parses the value and re-serialises it with `str()`.
  So whatever the builder renders, `"0.0000001"` serialises as `"1E-7"` and
  `"0.00000000000000000000000000012"` as `"1.2E-28"` (verified at `fa9a73c2`, part 1a).
  Both break the type's own JSON Schema pattern `^-?[0-9]+(\.[0-9]+)?$`. The fix belongs in
  the type:
  - **Ruled: `PositionalDecimalStr` in `model_schema/money.py`**, beside `DecimalStr`, with
    the same float refusal and the same JSON Schema, and a serialiser that renders
    `format(value, "f")`. The five ladder fields above use it.
  - **Not `DecimalStr` itself.** `DecimalStr` types 13 fields in 11 models (the finding
    under working id 9968; re-counted here at `fa9a73c2` by walking every class body in
    `packages/model-schema/src/model_schema/*.py` except `money.py` for an annotated field
    whose annotation names `DecimalStr`), some of them in content-hashed artifacts. *(Corrected
    2026-09-30, at the mint: this said "23 uses". That was the number of lines that
    `git grep -n "DecimalStr\b" -- packages/model-schema/src | grep -v money.py` printed
    at `fa9a73c2`, imports and `__all__` entries included, not a count of typed fields.)* Changing its serialiser
    would change stored bytes and hashes beyond this slice. That is recorded as an
    observation for the lead below.
  - **This is a `model-schema` contract change.** S3's write set therefore carries
    `model_schema/money.py`, the regenerated `docs/contracts/` (the generator's `--check`
    green) and the contract guard (`backend/tests/test_contracts.py`, the `contract-guard`
    skill), quoted in the ledger.
- `Trace.ladder_check_version` (the S3 plan's Acceptance 10) value `2` means **this ruling's
  predicate over this ruling's shape**. S3 ships both together, so a version-2 trace never
  carries a pre-ruling ladder.

### 4. `outputs`, displayed values, stored ladders, golden quotes and Regression Suites

- **What a declared output serves** (*ruled on audit, finding C2, by the maintainer's entry
  "2026-09-30 16:41:11 BST — RL 9963 C2: declared outputs keep the POST-clamp served value;
  the acceptance is NOT widened"*). A declared output keeps today's meaning: the value of
  its output step's own source after every step has run, which for a clamped name is the
  post-clamp value. It is **not** read from the ladder rung, because under §2 step 5 a
  clamped rung carries the pre-clamp value. Concretely, `_build_outputs` serves each
  declared rung output as the engine's exact `string()` value of the output step's source
  (the terminal read of §2 step 1, never the float), rounded once with that step's own
  `RoundSpec`. There is no float and no second rounding. **The restated invariant, both
  cases:**
  - **unclamped:** the served output equals its ladder rung's `value_minor` exactly (the
    same exact value, rounded once, with the same rounding), so the 10⁻⁴ correction below
    still reaches it;
  - **clamped:** the served output equals the bound rounded once with the output step's
    `RoundSpec`, which is the `constraints` rung's `value_minor`. When the bound is a whole
    number of minor units, that is the bound exactly (*sharpened on audit, S6*). On FD
    9967's quote, `office_premium_minor` serves **5000**, as today, and not the rung's
    pre-clamp 1436.

  The payable output is unchanged by this: it equals the `payable_premium` rung. The
  maintainer's acceptance below is **not** widened to cover a pre-clamp served value.
- **Declared money outputs that are not rungs** (*brought into scope on audit, S6*). Today
  `_build_outputs` serves a declared output that is not a rung straight from
  `result[source]`, which is the float (`score.py:643-645`). **Ruled: every declared output
  of type `money_minor` is served as the engine's exact `string()` value of its output
  step's source, rounded once with that step's `RoundSpec`, as an integer.** This is FR-273
  and `CLAUDE.md` §7, and it is part of the finding under working id 9949 that S3 owns.
  The same terminal read supplies it.
  **This is a visible change of value** (*stated on the third re-audit, R2*). On `/score`,
  such an output changes from the engine's float to an integer. The two differ by less than
  one rounding unit of the step's `RoundSpec` (at most half a unit for the `half_*` modes,
  under one unit for `ceiling` and `floor`). The maintainer ruled it a defect fix, quoted
  verbatim as relayed by the lead:

  > "2026-09-30 — the maintainer (by delegation) acknowledges that RL 9963 changes declared non-rung `money_minor` outputs served by /score from an unrounded float to the exact value rounded once by the output step's RoundSpec, an integer: a served-value change of at most one rounding unit plus a JSON type change from number-with-fraction to integer. This corrects a violation of FR-273 and aligns /score with score_batch, which already refuses a float money_minor. Conditions 1 and 2 of the W2 entry (a dated 03 note; a release-note line) cover it too."

  So S3's release-note line (W2 condition 2) names this change too, and this commit adds
  it to the `03` §4.4 note (condition 1). `score_batch` already raises on a float
  `money_minor` output (`_coerce_output_value`, `score.py:834`).
  **No contract types these outputs, so no contract change follows** (checked at
  `a8fef919`, which carries `fa9a73c2`'s contracts unchanged):
  - the hand-authored `docs/contracts/schemas/scoring.schema.json:54`: `"outputs": {"type": "object"}`;
  - the generated `docs/contracts/schemas/generated/score-comparison.schema.json`,
    `$defs.ScoringResult.properties.outputs`: `{"additionalProperties": true, "title":
    "Outputs", "type": "object"}`;
  - the generated `docs/contracts/openapi/generated.json`, `paths["/api/v1/score"].post.responses["200"]`:
    `"schema": {}`, an untyped response.

  The lead relayed the maintainer's confirmation that "the money_minor integer contract
  change plus its regeneration" go in S3's write set. The check above finds no field for
  that change to act on: `outputs` is a map keyed by the names each algorithm declares, and
  every contract types it as an untyped object. **So S3 edits no contract for R2.** Its
  contract-guard run and `generate-contracts --check` stay in the write set (B2), and they
  must stay green. Typing the `/score` response, which OpenAPI leaves as `{}`, would be a
  separate contract question. It is not ruled here; it is listed under Observed and filed
  as the finding under working id 9971.
  **Declared outputs of type `decimal` are out of S3 scope pending OQ 9970** (raised by the
  finding filed under working id 9969: should `/score` serve declared `decimal` outputs as
  strings, and may a `decimal` output carry money, which FR-227 allows?). This ruling does
  not pre-decide that question (*amended 2026-09-30, on the maintainer's entry of 17:08:59
  BST; this sentence first said they "are not money"*). Serving them as exact strings would
  change their JSON type on `/score` from number to string. No acceptance covers that visible change. `score_batch` already emits them as
  strings (`_coerce_output_value`, `score.py:834`). Owner to be set by OQ 9970's ruling
  (see Observed).
- **`outputs`, and the rung values it serves: they change on most quotes** (*restated on
  audit, W2*). Outside the clamped case, every declared non-payable rung output (for example
  `office_premium_minor`, served by `/score`) becomes that rung's engine value rounded once.
  **On most quotes that is a different number from today's**: 57–64 % of quotes across the
  four seeded sweeps, by up to about 10⁻⁴ of the value — 1–2p at 1e3, and up to 12521 minor
  units at 1e7, the maximum over all four sweeps (per seed at 1e7: 9997, 12521, 11724 and
  7820; the magnitude table in the results). In the 61234.5 case it is 67358, not
  today's 67357. It is a correction: today's number is FD 9949's drift.
- **The maintainer's acceptance of that change.** It was given three times on 2026-09-30,
  each line superseding the one before. The first said "1–2p on ~59% of quotes", and the
  measurement above contradicted it. The second, a dated CORRECTION in `to-lead.md`, is kept
  as it was quoted here:

  > ~~"2026-09-30 — the maintainer (by delegation) accepts RL 9963's change to declared non-payable rung outputs (the error today is about 1e-4 relative, from 4-dp factor quantisation; measured maximum 9997 minor units at the 1e7 scale; ~59% of quotes affected, per dm-eh-s3's sweep at fa9a73c2, seed 20260930) as a correction of FD 9949's drift, on conditions 1–3 of the W2 entry. Payable prices are accepted as changing only at near-ties, by at most 1 minor unit, as condition 3's count in RL 9963 must show; any payable change beyond that voids this acceptance."~~
  >
  > *Superseded 2026-09-30 by the line below. The maintainer widened it because a bound must
  > be the maximum over all the measurements, and 9997 is one seed's.*

  The line in force, quoted verbatim, as relayed by the lead:

  > "2026-09-30 — the maintainer (by delegation) accepts RL 9963's change to declared non-payable rung outputs (the error today is about 1e-4 relative, from 4-dp factor quantisation; measured maximum 12521 minor units at the 1e7 scale; 57–64% of quotes affected, across dm-eh-s3's 4 seeded sweeps at fa9a73c2) as a correction of FD 9949's drift, on conditions 1–3 of the W2 entry. Payable prices are accepted as changing only at near-ties, by at most 1 minor unit (measured: 0 flips in 42,000 quotes); any payable change beyond that voids this acceptance."

  The three conditions, as relayed by the lead, and where each is met:
  1. *A dated `03` note stating the change, its cause and its magnitude* — this record's
     commits add it to §4.4, with the maximum over all four sweeps, the per-seed maxima,
     and the per-decade maxima and histogram of seed 20260930.
  2. *A CHANGELOG or release-note line in the S3 slice* — no CHANGELOG exists at `fa9a73c2`
     (`git ls-files | grep -i -E "changelog|release-notes"` prints nothing). **Ruled: S3
     carries the release-note line in its squash-commit body and in its ledger** (the
     squash body is the permanent record, `git-hygiene`), with the `03` §4.4 note. The
     maintainer accepted this (relayed by the lead, 2026-09-30); a CHANGELOG file goes on
     the WK-1178 backlog.
  3. *The count of payables that move at near-ties, and by how much* — **0 of 42 000**
     sweep quotes across four runs at `fa9a73c2`, maximum delta 0; a flip can move a
     payable by exactly 1 minor unit (the results, "Payable near-tie flips").
- **The price.** `payable_premium` becomes the engine's exact value rounded once. It
  differs from today's float path only at a near-tie within float resolution (part 1), by
  exactly 1 minor unit; the sweeps found no such quote. **Any golden re-baseline is dated
  and needs the maintainer's ACK** (the maintainer's W2 decision).
- **Stored served ladders and traces are not re-baselined.** They are write-once (`UPDATE`
  is revoked on `scoring_traces` by migration `835988d1de4c`, `backend/src/app/platform/traces.py:208`), and they keep their old shape. The absence of
  `unrounded_minor`, and a `ladder_check_version` that is absent or 1, identify them. **One
  effect is disclosed and not handled:** a pending trace served by pre-S3 code and
  completed by post-S3 code re-scores to a different `premium_ladder`, so RL-862's
  comparison (`traces.py:64`) records `mismatch`. That is correct, because the served ladder
  misstated the maths. It affects only rows pending across the deploy.
- **Golden quotes and Regression Suites: no re-baseline is ruled.** A golden quote compares
  `payable_premium_minor` and `outcome` only (§4.7), and neither moves except at a near-tie.
  S3's false-positive control (the S3 plan's Acceptance 10, N2 (c)) re-scores every committed
  suite's golden quotes. **If any expected payable changes, S3 stops and reports it to the
  lead.** It never edits a fixture and never edits a stored suite version. A re-baseline, if
  the lead routes one, is a **new** suite version (§4.7: versioned and content-hashed),
  whose `change_note` cites this ruling and the engine's exact value. The stored version is
  never changed.

### 5. The reconciliation predicate S3 implements

**Inputs.** The ladder. Also, **read from the evaluated result and the algorithm, never
from the ladder**: for each rung that has an output step, the engine's exact value of that
step's source (`E(rung)`) and its declared rounding (`D(rung)`). The priced payable is
`round(E(payable_premium), D(payable_premium))`. **For each clamp step** (*added on audit,
W-b*): the name it produces and consumes; `before` (its `__before` read); each bound
present (`__min`, `__max`); the side that binds, by §2 step 5's comparison; and whether
the disposition lists its reason code. Where the inputs come from is the fix for
FD 9949's limb 1. The Python signature is S3's to choose.

**The ladder reconciles when all of these hold.**
- **R0 Shape.** The ladder is empty, or its last rung is `payable_premium`. The first rung
  has no operation, and every later rung has one. `round` appears only on the last rung, and
  `clamp` only on `constraints`. No clamp binds on a name other than the source of the last
  rung before `constraints` (§2 step 5). For every clamp step, the comparison and the
  disposition agree: it binds exactly when its reason code is in the disposition.
- **R1 Sources.** For every rung except `constraints`: `unrounded_minor == E(rung)` exactly,
  and `rounding == D(rung)`. When a clamp binds on a rung's source, `E(rung)` is the value
  before the clamp (the generated `__before` read), and `E(constraints)` is the engine's
  value after it; `constraints` must then equal `E(constraints)`. With no binding clamp,
  `constraints` equals the previous rung. Its `rounding` always equals the previous
  rung's.
- **R2 Display.** Every `value_minor == round(unrounded_minor, rounding)`.
- **R3 Each operation explains its rung.** Applying the operation to the previous rung's
  `unrounded_minor`, in exact decimal arithmetic, agrees with this rung's `unrounded_minor`
  within 10⁻²⁶ of it, relative. `none` and `round` require equality with the previous
  rung's value. `clamp` requires the rung's value to equal `bound_unrounded_minor` exactly,
  the bound to equal the engine's value of that bound expression, and the previous rung's
  value to lie strictly on the far side of it (below a `min`, above a `max`), because the
  clamp binds only then.
- **R4 The replay (FR-248).** Start from the first rung's `unrounded_minor`, and apply every
  recorded operation in order with no rounding (a `clamp` sets the running value to its
  bound). Then apply the `payable_premium` rung's
  `round`, the only rounding. The result equals that rung's `value_minor` **and** the priced
  payable, to the penny.

"Exact decimal arithmetic" means a context of at least 100 significant digits. Addition and
multiplication of engine-sized values are then exact. Division is exact when it terminates,
and otherwise has an error 70 orders of magnitude below the tolerance.

**The first rung, and an algorithm with no `risk_premium_minor` step.** The anchor is the
first rung present, whatever its name, checked by R1 against its own output step's source.
A ladder whose only rung is `payable_premium` reconciles when R1, R2 and its `value_minor`
equal to the priced payable hold. The replay has no operation to apply. (The prototype
returns False for this shape; the sweep never builds it; S3's test covers it.)

**An empty ladder** arises only for an algorithm that declares no rung output step at all.
It has nothing to reconcile, and the check returns True **for that case alone**, named in
the code as such. Whether every Rating Version must declare `payable_premium_minor`
(FR-247) is a compile-time question, not ruled here. **A ladder with rungs but no final
`payable_premium` does not reconcile.**

**Residual risk, stated rather than hidden.** When a rung is recovered by step 3 (a
terminating operation whose result the engine rounded), R4's replay differs from the
engine's chain by up to about 10⁻²⁶ relative. It can flip the payable penny only if the
engine's final value is an exact tie. After an engine rounding at 28–29 digits, that needs
the exact maths to lie within about 10⁻²² of a tie. If it ever happens, the check fails
loudly and truthfully: the recorded operations then really do not reproduce the price.
What a failure does is DP-S3-1's.

## Acceptance — the violation that must become detectable

S3 carries each item red first, shown failing on `origin/main`.

1. **The realistic-scale red case, through `score_one` with `trace=True`** (a fixture whose
   risk source is controllable: an `expression` or `input` source is enough, because the
   builder does not care where the value comes from). Risk 61234.5, office = risk × 1.1
   from a table, instalment = office × 1.05, payable = instalment. **Red today:**
   `ladder_reconciled` is True while the ladder replays to 70725 against a payable of 70726.
   **Green:** 61234 · 67358 (×1.1) · 67358 · 70726 (×1.05) · 70726; reconciled; and
   `outputs["office_premium_minor"]`, if declared, is 67358. The auditor's case (60000.4 →
   66000.44 → 69402.0) is added at unit level on the builder.
2. **The scale sweep, required by the maintainer.** It runs on S3's own builder and
   predicate through a real ZEN evaluation, not on a reimplementation. Coverage: every
   decade from 1e3 to 1e7 minor units; every optional-rung count from 0 to 6; float32
   risk values; 4-dp table factors; one gross-up rung; one `add` rung; and one run with
   rungs that apply more than one operation. At least 200 quotes per cell, with a fixed
   recorded seed, **and at least two seeds**. Assertions: 100 % reconciled; every
   single-operation rung records the applied operand exactly (×1.25 stays ×1.25, ÷0.875
   stays ÷0.875); every rung's `value_minor` equals its engine value rounded once. **The
   same sweep over `origin/main`'s builder must fail**, which proves the sweep can print a
   failure (CLAUDE.md §13).
3. **Planted-defect controls on the predicate:** a displayed value + 1 on any rung; a
   factor or divisor × 1.000001; an added amount + 0.01; the payable `value_minor` + 1; the
   first rung's unrounded value + 0.001; a payable source 0.6 away from the previous rung.
   Each must fail.
4. **The binding:** the near-tie case from part 1 prices 1235, not 1234. A rung value is
   never read from the float; a test fails if `_build_ladder` receives only floats.
5. **The contract:** every rung of a new result carries `unrounded_minor` and `rounding`;
   a new `ScoringResult` validates against the hand-authored and the generated schema; a
   stored pre-ruling ladder still validates; and the contract guard is green.
   **`PositionalDecimalStr`, red first:** a model holding `Decimal("0.0000001")`,
   `Decimal("1.2E-28")` and `Decimal("1E+1")` in a ladder field serialises them as
   `"0.0000001"`, `"0.00000000000000000000000000012"` and `"10"`. Today's `DecimalStr`
   gives `"1E-7"`, `"1.2E-28"` and `"1E+1"` (part 1a), so the test is red until the type
   exists.
6. **The shapes in §5:** a first rung that is not `risk_premium`; a payable-only ladder; a
   ladder with rungs but no payable rung.
7. **The re-derivation test** (`test_rating_score.py:191-231`) is replaced by R4. Its
   `round` branch (`:224-225`) assigns instead of replaying, which is why it passed over
   the drift.
8. **The false-positive control** (the S3 plan's Acceptance 10, N2 (c)) runs under this
   predicate, and adds three counts, each of which stops the slice if it is above 0:
   - golden quotes whose payable changes;
   - golden quotes on which a declared rung output moves by more than its mechanism
     bound (*made explicit on audit, S4; ruled on the third re-audit, R1, by the
     maintainer, relayed by the lead: the **exact** form below is in force. It supersedes
     the flat 5 × 10⁻⁵ bound, the maintainer's sum over the quote's factors, and the
     own-term form*). For rung `i` of a golden quote, `new_i` is the ruled value and
     `base_i` the baseline value. The slice stops if:
     - on a `multiply` rung: **`|base_i − new_i| > 5 × 10⁻⁵ · |base_{i−1}| + (e_apply +
       e_ruled)`** minor units, where `base_{i−1}` is the previous rung in the baseline
       ladder;
     - on an `add` or a `round` rung, and on the first rung: `|base_i − new_i| > e_apply +
       e_ruled`, where on the first rung `e_apply` is the error of today's single rounding;
     - on a `constraints` rung where a clamp binds: `new_i` is not exactly the bound.

     `e` is a rounding's largest error: **0.5 for a `half_*` mode, and 1 for `ceiling`,
     `floor` and `down`**. `e_apply` is that of the rounding today's builder applied (the
     step's mode passed to `apply_factor`, or to `_round_minor`), and `e_ruled` is that of
     the rung's declared `RoundSpec`. So the constant is 1 for half and half, 1.5 for a
     half and a directed mode, and 2 for two directed modes. **The comparison is evaluated
     in integers and `Decimal`, never in float.**
     *(Amended 2026-09-30, at the mint, on the maintainer's entry headed "2026-09-30
     17:14:16 BST — RL 9963: the independent re-run MEETS my condition; the bound's
     constant term AMENDED; ACK at the mint", which supersedes the constant "+ 1" and the
     "≤ 1" of the add and round rungs.)* **"validated on half_even only; directed modes are covered by derivation, not measurement"**: the sweeps declare `half_even` on every rung. The entry also rules:
     **"If S3's golden set contains a directed-mode rung, S3's first run records its tightness as the first measurement."**
     - **Derived from FD 9949's cause, not fitted** (`score.py:609-611`). Today's rung is
       `apply_factor(base_{i−1}, q_i)`, where `q_i` is `raw_i / base_{i−1}` cut to 4 dp,
       so `|q_i − raw_i / base_{i−1}| ≤ 5 × 10⁻⁵`, and `|base_{i−1} · q_i − raw_i| ≤
       5 × 10⁻⁵ · |base_{i−1}|`. `apply_factor`'s rounding and the ruled value's rounding
       add at most `e_apply` and `e_ruled`: 0.5 each in a `half_*` mode, up to 1 each in a
       directed mode (*corrected at the mint: this sentence said "at most 0.5 each"*). The drift does not accumulate, because each rung's factor is
       re-derived from its own raw value.
     - **Validated on the four-sweep corpus** at tree `fa9a73c2`: seeds 20260930, 7, 1257
       and 42 (mixed). The runs were `python work_v8.py 200 20260930 x`, `… 200 7 x`,
       `… 500 1257 x` and `… 300 42 mixed x`, where `work_v8.py` is the appendix's script,
       sha256 `7c39cf44…`, under a working name. **The exact bound had 0 exceedances on
       every seed:** 0 of 31 200 rung outputs (seed 20260930), 0 of 31 600 (seed 7),
       0 of 80 500 (seed 1257) and 0 of 45 900 (seed 42, mixed), 189 200 in all. Its
       tightness, `(|diff| − 1) / (5 × 10⁻⁵ · |base_{i−1}|)`, reached 0.9998, 0.9998,
       0.9996 and 0.9992, so the derived bound is almost attained, as the mechanism
       predicts. `5 × 10⁻⁵ · |base_{i−1}| / |new_i|` reached at most 6.25 × 10⁻⁵ (the
       sweep's smallest factor, 0.8), below the 2 × 10⁻⁴ report line.
     - **Two other counters, recorded for the record.** The same runs also counted:
       - the maintainer's earlier quote-wide sum, `Σ 5 × 10⁻⁵ / |q_j|` (first run with
         script `13a8a195…`): 0 exceedances in 189 200 rung outputs. But the sum ran above
         2 × 10⁻⁴ on 4491 of 31 200, 4961 of 31 600, 11 792 of 80 500 and 6050 of 45 900
         rung outputs (max 3.28 × 10⁻⁴), because it assumed that the drift accumulates;
       - the own term, `(5 × 10⁻⁵ / |q_i|) · |new_i| + 1` (first run with script
         `78106d73…`): 0 exceedances on every seed, but tightness up to 0.9999, 0.9998,
         0.9996 and 0.9991. It approximates `|base_{i−1}|` by `|new_i| / |q_i|`, so an
         own-term exceedance with no exact exceedance would be expected. It is not a stop.
     - **The 2 × 10⁻⁴ report** applies to `5 × 10⁻⁵ · |base_{i−1}| / |new_i|`: if it
       exceeds 2 × 10⁻⁴ on a golden quote (a factor below about 0.25), S3 reports it to
       the maintainer before it continues.
     - **Any exceedance of the exact bound is reported to the maintainer**, with no looser
       fallback. It would mean a second cause of drift.
     - The acceptance line's "about 1e-4" stands: the measured maximum of `(|diff| − 1) /
       value` is 4.854 × 10⁻⁵ (results part 6).
     - **The baseline is `origin/main`'s builder run on the same golden contexts at S3's
       base tree**, because a golden quote's `expected` stores only the payable and the
       outcome (§4.7).
   - quotes on which a clamp's comparison and disposition disagree (S5).
9. The ledger records `scripts/bench-rating.py` before and after (one extra generated node
   with one `string()` per rung). No budget is changed here.
10. **A binding clamp (FD 9967), red first.** On the finding's reproduction (the score
    fixture with `min_premium_minor` 5000): `office_premium` stays **1436** with factor
    ×1.1; `constraints` is **5000** with `kind: "clamp"`, `bound: "min"`,
    `bound_unrounded_minor: "5000"` and `MIN_PREMIUM_APPLIED` in `applied`; instalment and
    payable stay 5250; the ladder reconciles. Today, `office_premium` is 5000 and
    `constraints` is `none` (part 5). The unclamped case is unchanged. **Planted:** the
    bound + 0.001, and the clamp recorded as `none`, each fail the predicate. A `max` clamp
    is covered as well as a `min`, since the finding did not measure one, and so is a step
    declaring both bounds. **The test S3 replaces:**
    `test_a_clamp_overrides_the_ladder_and_is_recorded_on_the_constraints_rung`
    (`test_rating_score.py:262-276`), which asserts `office.value_minor == 999_999` and so
    fixes the misattribution (*named on audit, W-d*). **The disposition disagreeing with the
    comparison** (a clamp that binds while its condition holds, and a violated condition on
    which no side binds) fails R0 (W-a).
    **The placement refusal (W-c, S1), red first:** an algorithm whose clamp produces the
    source of `office_premium` while an `optimisation_adjustment` rung follows it, one whose
    clamp produces the `instalment_loading` source, and one whose clamp produces a name
    other than the one it consumes, are each refused with `LADDER_CLAMP_UNPLACEABLE`, both
    when saved and by `compile_bundle`. Today all three save and compile. The score fixture
    (a clamp on the source of the last rung before `constraints`) still saves and compiles.
    `_check_clamp_placement` is in `ALGORITHM_CHECKS`, so #967's closure test (ii) passes.
11. **An engine-precision guard (W3).** A test pins what the 10⁻²⁶ tolerance rests on: on
    `zen-engine` 0.53.0, the chain in part 1 returns an eighth product of 29 significant
    digits, `2095.3120014523377649903134154`, which differs from the exact 30-digit product,
    `2095.31200145233776499031341545` (*corrected on audit, W-e: this item first called the
    engine's result the exact product*).
    If an engine upgrade changes the engine's precision, the test fails, and the tolerance
    is re-ruled before the upgrade lands. The test sits beside FR-273's startup self-check
    (`assert_integer_minor_round_trip`, `03` §5.2).
12. **The release-note line** (W2, condition 2) is in S3's squash-commit body and ledger,
    and it states the change to declared non-payable rung outputs and its measured size.
13. **The served declared output (C2), both cases.** The fixture declares
    `office_premium_minor` as an output. On FD 9967's min-premium quote, `/score` serves
    **5000**, equal to the `constraints` rung and the bound, and not the office rung's
    1436. On an unclamped quote, it serves exactly the office rung's `value_minor`. The
    first case is green today and must stay green. **It is red first against a planted
    mutation:** a `_build_outputs` that serves the rung's `value_minor`, which gives 1436.
    A test also asserts that the served value is built from the exact string read, not from
    the float. **A declared non-rung `money_minor` output (S6)** is served as an integer
    from the exact string; red first, because today it is the float from `result`.

## What it obliges

WK-674 Slice 3 (the leaf plan filed under working id 9947), in Task 6:
- the builder (§2) and `to_wire`'s generated `string()` read, and `_constraint_node`'s
  generated `__before` and bound reads (`runtime.py`);
- `PositionalDecimalStr` in `model_schema/money.py` (§3);
- `_build_outputs` serving declared outputs from their own source, exact and rounded once
  (§4, C2);
- `_check_clamp_placement` in `ALGORITHM_CHECKS`, after #967's code slice has merged, and
  the rung mapping moved to `pricing_core/rating/ladder.py` (§2 step 5, W-c, S1, S2);
- `LADDER_CLAMP_UNPLACEABLE` in `backend/src/app/errors.py`;
- declared `money_minor` outputs from the exact string (§4, S6);
- the contract (§3): `model_schema.scoring`, the hand-authored `scoring.schema.json` and the
  regenerated contract, in one commit with **§4.4's example replaced**, as the dated note
  added there by this commit says;
- the predicate (§5) in `reconcile_ladder` and every caller the plan lists
  (`score.py:738`, `properties.py:298-303`, `pricing_core/__init__.py:31`). **The FR-261
  property must take the scoring-time verdict with its independent inputs. It must not
  rebuild the anchors from the ladder that it checks**;
- the docstrings that describe the old construction: `score.py:62-103` (the "Ladder construction" section), and
  `model_schema/scoring.py`'s `LadderOperation` and module docstrings;
- the Acceptance section above.

**S3's write set gains** (beyond the plan's rows at `:391-393`):
`packages/pricing-core/src/pricing_core/rating/runtime.py` (`to_wire`, `_constraint_node`);
`packages/model-schema/src/model_schema/money.py` (the new type); `docs/contracts/`
regenerated, with `scripts/generate-contracts.py --check` green; the contract guard,
`backend/tests/test_contracts.py`; `packages/pricing-core/src/pricing_core/rating/compile.py`
(one appended function and one `ALGORITHM_CHECKS` entry, after #967 merges); the new
`packages/pricing-core/src/pricing_core/rating/ladder.py`; `backend/src/app/errors.py` (the
new code); and `docs/specs/03-rating-engine.md` §4.4 (the example
replacement). These edit existing files, so each serialises with any in-flight slice
editing the same file, by the plan's own rule for its rows.

**What this record supersedes in the S3 plan** (*rewritten on audit, finding B1: this
paragraph first said that only the replay rule was superseded, and that was false*). The
plan is read at `06e3e896` on branch `wk674-s3-leaf-plan`. Each item below is replaced by
the section of this record named beside it:

| Plan item (quoted) | Replaced by |
|---|---|
| Acceptance 10, "The signature changes": "`reconcile_ladder` receives the **recorded operations** … and the **real** risk premium, the algorithm's own risk-premium output, never the first rung" | §5 *Inputs*: the ladder, plus `E(rung)` and `D(rung)` for every rung, read from the result and the algorithm; the anchor is the first rung present, whatever its name |
| Acceptance 10, "the risk premium's source and check": "the check takes that **unrounded** output value and the step's declared rounding mode, rounds it once, and requires the first rung's `value_minor` to equal the result" | §5 R1 and R2: the first rung's `unrounded_minor` equals `E(rung)` exactly, and its `value_minor` equals that value rounded once |
| Acceptance 10, "the four operation kinds … `multiply` → `apply_factor(prev, Decimal(factor), mode)` … `add` → `prev + amount_minor`; `round` at `dp = 0` → `prev` unchanged …; `none` → `prev` unchanged (the `constraints` rung, whose `applied` codes explain nothing numeric)" | §3 and §5 R3–R4: six kinds (`multiply`, `divide`, `add`, `clamp`, `round`, `none`), replayed on unrounded values in exact decimal arithmetic; `add` uses `amount_unrounded_minor`; `constraints` is `clamp` when a clamp binds |
| Acceptance 10, "the comparison: every replayed value equals that rung's recorded `value_minor`, and the last equals `payable_premium` — to the penny, integers throughout" | §5 R2–R4: displays equal their own value rounded once; each operation agrees within 10⁻²⁶ relative; the chained replay rounds once and equals the payable to the penny |
| Acceptance 10, "Never sampled": the rationale "it is integer arithmetic over a handful of rungs" | The conclusion stands (every quote, every Environment). The rationale becomes: exact decimal arithmetic, in a context of at least 100 digits, over a handful of rungs |
| Global Constraints: "the reconciliation compares integers" | It compares integers at the payable and the displays (R2, R4), and exact decimals on the chain (R1, R3) |

**Everything else in Acceptance 10 stands:** the corrected premise; the false-positive
control (extended by Acceptance 8 above); the call-site red case with `trace=True` and the
untraced failure's signal; the property red case; the raise-site census (the message
carries rung names and the difference, which is now a decimal string in minor units); and
`ladder_check_version`.

**The delta travels in S3's dispatch record.** A plan is frozen by family, a draft
included (`document-ids.md` §1.5), so the lead's dispatch record for WK-674 Slice 3 carries
the table above, and the slice's ledger quotes it in Task 0.
The plan's Acceptance 1 dated clauses on FR-248 and NFR-496 ("never sampled") still land
in S3's Task 1, beside this commit's clause.

**This record's commits edit `03` in four places:** FR-240 gains a dated clause (`03:137`)
for the refusal, at save and at compile, of a clamp the ladder cannot place (W-c, S1).
§5.1's list of owned codes gains `LADDER_CLAMP_UNPLACEABLE`. FR-248 gains the dated clause (`03:155`), which
now also records the clamp and says "exactly where the engine did not round, and to the
engine's precision where it did" (W4). §4.4 gains a dated note: the example does not
reconcile (24_150 × 1.15 = 27_772.5, not 27_780); the new kinds and fields; and W2's
condition 1, the change to declared rung outputs with its cause, maxima and histogram,
and C2's rule for a clamped rung's served output.
S3 replaces the example. The generated reads in `runtime.py` need no spec change: `03`
§5.2 declares `to_wire`'s signature (`:874-875`) and says nothing of its generated
expressions, and neither signature changes. No other spec, no plan, no roadmap and no
contract is edited here.

**Departures from the maintainer's steer:** three, as ruled in §1: the string read, the
engine-precision tolerance on each rung's own check, and `divide`. The `clamp` kind (C1) is
an addition the steer did not address, not a departure from it. Two limbs of the steer
stand unchanged: true operands, and one rounding on the replay path.

## Observed, not ruled (for the lead)

- **Today's builder also breaches FR-273, not only FR-248.** Fractional rung values cross the binding
  as floats and feed Python arithmetic (`score.py:592`, `:609-611`), and FR-273 says such a
  value is "an integer minor unit or a string". This ruling's string read closes it for the
  ladder and the payable. The lead may fold it into the finding under working id 9949.
- **The "intermediate" limb of FR-275 is not met at runtime.** The engine rounds a 30-digit
  intermediate to 29 digits silently (part 1). FR-275 asks bundle compilation to fail
  "rather than allowing a silent loss of precision deep in a ladder", but compilation
  cannot see runtime values. The effect is about 10⁻²⁸ relative, and this ruling tolerates
  it. The requirement's wording is a separate question.
- **The shared `DecimalStr` and `Relativity` types can emit exponent form** (found on
  audit, B2). Both serialise with `str()` (`model_schema/money.py:85-100`), so
  `Decimal("0.0000001")` becomes `"1E-7"`, which their own JSON Schema pattern refuses. This
  ruling does not change them (§3 says why). Whether any stored value is affected, and the
  fix, are filed as the finding under working id 9968: MEDIUM, owner WK-1178.
- *(Removed on audit: the clamp-attribution item is now ruled, §1 and §2 step 5.)*
- **The `/score` response is untyped in the generated OpenAPI** (`docs/contracts/openapi/generated.json`,
  `paths["/api/v1/score"].post.responses["200"]`, `"schema": {}`), and so is `/score/compare`'s.
  A client generated from it gets no `ScoringResult` type (*found on the third re-audit,
  R2*). Filed as the finding under working id 9971.
- **Declared `decimal` outputs reach `/score` as floats** (*added on audit, S6*).
  `_build_outputs` serves them from `result[source]`, and `score_one` does not convert them,
  while `score_batch` serialises them as strings. This ruling brings only `money_minor`
  outputs into S3 (§4). The question is OQ 9970, raised by the finding under working id
  9969. Owner to be set by OQ 9970's ruling.
- **This ruling interacts with OQ-1316.** If OQ-1316 is decided (a) (an intermediate
  rounding recorded as its own rung), R0's "`round` only on the last rung" must be amended
  by that ruling.

## Appendix — the evidence script, verbatim

`dp_s3_5_evidence.py` (the final runs used the working name `work_v8.py`), sha256 `7c39cf44e1827e0f98e0172a2e239b15e759273610923cd7089ae0a644675a4b`:

```python
"""DP-S3-5 evidence (RL-9963). Scratch only, never committed.

Run from any directory with PYTHONPATH naming the tree's pricing-core and model-schema src
dirs, under an interpreter that has zen-engine 0.53.0 and numpy:
    python dp_s3_5_evidence.py <quotes-per-cell> <seed>
"""
import copy
import json
import random
import sys
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from types import SimpleNamespace

import numpy as np
import zen

import pricing_core.rating.score as score
from model_schema.rating import RatingOutputStep
from pricing_core.money import apply_factor

ENGINE = zen.ZenEngine()
DIFF_MAX, DIFF_HIST = {}, {}
REL_MAX = [(Decimal(0), 0, '', '')]
REL1_MAX = [(Decimal(0), 0, '', '')]
MECH = {'rungs': 0, 'exceed_per_output': 0, 'exceed_quote_wide': 0, 'sigma_max': Decimal(0), 'sigma_over_2e-4': 0, 'tightness_max': Decimal(0), 'exceed_own_term': 0, 'own_max': Decimal(0), 'own_tightness_max': Decimal(0), 'exceed_exact_prev': 0, 'exact_tightness_max': Decimal(0), 'exact_rel_max': Decimal(0)}


# ---- a real ZEN graph: a chain of expression nodes, then one node that reads every value as
# ---- an exact string (the engine's `string()`), as S3's to_wire would.
def _node(nid, exprs):
    return {"id": nid, "type": "expressionNode", "name": nid, "position": {"x": 0, "y": 0},
            "content": {"expressions": [{"id": f"{nid}_{i}", "key": k, "value": v}
                                        for i, (k, v) in enumerate(exprs)], "passThrough": True}}


def evaluate(steps, inputs):
    """steps: [(key, expr)], or [[(key, expr), ...]] for one node with several expressions,
    evaluated in order. Returns the result, with `<key>__exact` for every key."""
    nodes = [{"id": "in", "type": "inputNode", "name": "in", "position": {"x": 0, "y": 0}}]
    edges, prev = [], "in"
    steps = [s if isinstance(s, list) else [s] for s in steps]
    for i, exprs in enumerate(steps):
        nodes.append(_node(f"n{i}", exprs))
        edges.append({"id": f"e{i}", "sourceId": prev, "targetId": f"n{i}", "type": "edge"})
        prev = f"n{i}"
    keys = sorted({k for exprs in steps for k, _ in exprs} | set(inputs))
    nodes.append(_node("exact", [(f"{k}__exact", f"string({k})") for k in keys]))
    nodes.append({"id": "out", "type": "outputNode", "name": "out", "position": {"x": 0, "y": 0}})
    edges += [{"id": "ex", "sourceId": prev, "targetId": "exact", "type": "edge"},
              {"id": "eo", "sourceId": "exact", "targetId": "out", "type": "edge"}]
    graph = {"nodes": nodes, "edges": edges}
    return ENGINE.create_decision(json.dumps(graph)).evaluate(inputs)["result"]


def out_step(rung, src):
    return RatingOutputStep.model_validate({
        "step_id": f"o_{rung}", "type": "output", "label": rung, "output_name": f"{rung}_minor",
        "rounding": {"mode": "half_even", "dp": 0}, "consumes": [src]})


def today(present, result):
    """origin/main's real `_build_ladder` on the float values the binding returns."""
    alg = SimpleNamespace(steps=[out_step(r, k) for r, k in present.items()])
    return score._build_ladder(alg, {k: result[k] for k in set(present.values())}, [])[0]


def replay_today(ladder):
    """The S3 plan's (working id 9947) Acceptance 10 replay: multiply -> apply_factor, add -> +, round/none -> prev."""
    value = ladder[0].value_minor
    for rung in ladder[1:]:
        op = rung.operation
        if op.kind == "multiply":
            value = apply_factor(value, Decimal(op.factor), op.mode)
        elif op.kind == "add":
            value += op.amount_minor
    return value


# ---- the ruled design (a prototype of RL-9963's builder and predicate) ----
REL_TOL = Decimal("1e-26")
ORDER = ["risk_premium", "expense_loading", "commission", "profit_loading", "office_premium",
         "optimisation_adjustment", "constraints", "instalment_loading", "ipt_and_fees",
         "payable_premium"]
MULTIPLY = {"expense_loading", "commission", "profit_loading", "optimisation_adjustment",
            "instalment_loading"}
ADD = {"ipt_and_fees"}


def rnd(u):
    return int(u.quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


def agrees(a, b):
    with localcontext() as ctx:
        ctx.prec = 200
        return abs(a - b) <= abs(b) * REL_TOL


SHORT = 20  # an operand this short is a terminating operation that lost only engine precision


def _shortest(ratio, reproduces):
    with localcontext() as ctx:
        for k in range(1, 60):
            ctx.prec = k
            f = ctx.plus(ratio)
            if reproduces(f):
                return f
    raise AssertionError("unreachable")


def true_operation(prev, cur):
    """The operation the rung applied, recovered exactly from the engine's two values:
    1. an exact factor; 2. an exact divisor; 3. the shortest factor, then the shortest
    divisor, reproducing `cur` to the engine's precision, if it has fewer than SHORT
    significant digits; 4. otherwise the exact amount added."""
    with localcontext() as ctx:
        ctx.prec = 120
        r, d = cur / prev, (prev / cur if cur != 0 else None)
    if exact("*", prev, r) == cur:
        return {"kind": "multiply", "factor": format(r.normalize(), "f")}
    if d is not None and exact("*", cur, d) == prev:
        return {"kind": "divide", "divisor": format(d.normalize(), "f")}
    f = _shortest(r, lambda f: agrees(exact("*", prev, f), cur))
    if len(f.as_tuple().digits) < SHORT:
        return {"kind": "multiply", "factor": format(f.normalize(), "f")}
    if d is not None:
        g = _shortest(d, lambda g: agrees(_div(prev, g), cur))
        if len(g.as_tuple().digits) < SHORT:
            return {"kind": "divide", "divisor": format(g.normalize(), "f")}
    return {"kind": "add", "amount": format(exact("-", cur, prev), "f")}


def _div(a, b):
    with localcontext() as ctx:
        ctx.prec = 200
        return a / b


def exact(op, a, b):
    with localcontext() as ctx:
        ctx.prec = 200
        return {"+": a + b, "-": a - b, "*": a * b}[op]


def build_ruled(present, values, clamp=None):
    """present: rung -> source key; values: key -> the engine's exact Decimal. clamp: a binding
    clamp on the source of the last rung before `constraints`: {key, before, side, bound, code}."""
    ladder, prev = [], None
    for rung in ORDER:
        if rung == "constraints":
            if prev is not None and clamp:
                u = values[clamp["key"]]  # the engine's post-clamp value
                op = {"kind": "clamp", "bound": clamp["side"], "bound_value": format(clamp["bound"], "f"),
                      "applied": [clamp["code"]]}
                ladder.append({"rung": rung, "u": u, "value_minor": rnd(u), "op": op})
                prev = u
            elif prev is not None:
                ladder.append({"rung": rung, "u": prev, "value_minor": rnd(prev), "op": {"kind": "none"}})
            continue
        if rung not in present:
            continue
        u = values[present[rung]]
        if clamp and present[rung] == clamp["key"] and ORDER.index(rung) < ORDER.index("constraints"):
            u = clamp["before"]  # the pre-clamp value, read by the generated clamp node
        if prev is None:
            op = None
        elif rung == "payable_premium":
            op = {"kind": "round", "mode": "half_even", "dp": 0}
        elif rung in ADD or prev == 0:
            op = {"kind": "add", "amount": format(exact("-", u, prev), "f")}
        elif rung in MULTIPLY or u != prev:
            op = true_operation(prev, u)
        else:
            op = {"kind": "none"}
        ladder.append({"rung": rung, "u": u, "value_minor": rnd(u), "op": op})
        prev = u
    return ladder


def reconciles(ladder, anchors, payable_minor):
    """anchors: rung -> the engine's exact value of that rung's source, read from the result,
    never from the ladder. payable_minor: that payable value rounded once, independently."""
    if not ladder or ladder[-1]["rung"] != "payable_premium" or ladder[0]["op"] is not None:
        return False
    v = ladder[0]["u"]
    for i, r in enumerate(ladder):
        if (r["rung"] != "constraints" or "constraints" in anchors) and r["u"] != anchors[r["rung"]]:
            return False                                       # R1 sources
        if r["value_minor"] != rnd(r["u"]):
            return False                                       # R2 display, rounded once
        if i == 0:
            continue
        prev, op = ladder[i - 1], r["op"]
        if op is None:
            return False
        if op["kind"] == "round":
            return (i == len(ladder) - 1 and r["u"] == prev["u"]  # R3 round changes nothing
                    and rnd(v) == r["value_minor"] == payable_minor)  # R4 the one rounding
        if op["kind"] == "multiply":
            local, v = exact("*", prev["u"], Decimal(op["factor"])), exact("*", v, Decimal(op["factor"]))
        elif op["kind"] == "divide":
            local, v = _div(prev["u"], Decimal(op["divisor"])), _div(v, Decimal(op["divisor"]))
        elif op["kind"] == "add":
            local, v = exact("+", prev["u"], Decimal(op["amount"])), exact("+", v, Decimal(op["amount"]))
        elif op["kind"] == "clamp":
            bound = Decimal(op["bound_value"])
            if not (prev["u"] < bound if op["bound"] == "min" else prev["u"] > bound):
                return False                                   # R3 the clamp bound
            if r["u"] != bound:
                return False                                   # R3 the rung is the bound
            local, v = bound, bound                            # R4 the replay takes the bound
        else:
            local = prev["u"]
        if not agrees(local, r["u"]):
            return False                                       # R3 the operation explains its rung
    return False


def plants(ladder):
    out = []
    for i, r in enumerate(ladder):
        if 0 < i < len(ladder) - 1:
            b = copy.deepcopy(ladder); b[i]["value_minor"] += 1; out.append(("display+1", b))
        if r["op"] and r["op"]["kind"] == "multiply":
            b = copy.deepcopy(ladder)
            b[i]["op"]["factor"] = str(Decimal(r["op"]["factor"]) * Decimal("1.000001"))
            out.append(("factor*1.000001", b))
        if r["op"] and r["op"]["kind"] == "divide":
            b = copy.deepcopy(ladder)
            b[i]["op"]["divisor"] = str(Decimal(r["op"]["divisor"]) * Decimal("1.000001"))
            out.append(("divisor*1.000001", b))
        if r["op"] and r["op"]["kind"] == "add":
            b = copy.deepcopy(ladder)
            b[i]["op"]["amount"] = str(Decimal(r["op"]["amount"]) + Decimal("0.01"))
            out.append(("amount+0.01", b))
    b = copy.deepcopy(ladder); b[-1]["value_minor"] += 1; out.append(("payable+1", b))
    b = copy.deepcopy(ladder); b[0]["u"] += Decimal("0.001"); out.append(("anchor+0.001", b))
    return out


def ladder_case(risk, loadings, print_it=False):
    """loadings: [(rung, expr-of-prev)] in ladder order; `{p}` is the previous key."""
    steps, present, prev = [], {"risk_premium": "k_risk"}, "k_risk"
    for rung, expr in loadings:
        key = f"k_{rung}"
        steps.append((key, expr.format(p=prev)))
        present[rung] = key
        if rung == "profit_loading":
            present["office_premium"] = key
        prev = key
    present["payable_premium"] = prev
    result = evaluate(steps, {"k_risk": risk})
    values = {k: Decimal(result[f"{k}__exact"]) for k in set(present.values())}
    v1 = today(present, result)
    v2 = build_ruled(present, values)
    anchors = {r: values[k] for r, k in present.items()}
    payable = rnd(values[present["payable_premium"]])
    if print_it:
        print("  today:", [(r.rung, r.value_minor, r.operation and (r.operation.factor or r.operation.amount_minor or r.operation.kind)) for r in v1])
        print("  today replay:", replay_today(v1), " payable:", v1[-1].value_minor)
        print("  ruled:", [(r["rung"], r["value_minor"], format(r["u"], "f"), r["op"] and (r["op"]["kind"], r["op"].get("factor") or r["op"].get("divisor") or r["op"].get("amount") or "")) for r in v2])
        print("  ruled reconciles:", reconciles(v2, anchors, payable))
    return v1, v2, anchors, payable, present, values


def clamp_case(risk, min_p, plant=None):
    """FD 9967's shape: office = risk * 1.1, a min-premium clamp on office, instalment = office * 1.05.
    The generated clamp node also reads the exact pre-clamp value and the bound (`__before`, `__bound`)."""
    steps = [("k_office", "k_risk * 1.1"),
             [("s_clamp__before", "string(k_office)"), ("s_clamp__violated", "!(k_office >= min_p)"),
              ("k_office", "(k_office < (min_p) ? (min_p) : k_office)"), ("s_clamp__bound", "string(min_p)")],
             ("k_inst", "k_office * 1.05")]
    result = evaluate(steps, {"k_risk": risk, "min_p": min_p})
    present = {"risk_premium": "k_risk", "office_premium": "k_office", "instalment_loading": "k_inst",
               "payable_premium": "k_inst"}
    values = {k: Decimal(result[f"{k}__exact"]) for k in set(present.values())}
    fired = result["s_clamp__violated"]
    clamp = {"key": "k_office", "before": Decimal(result["s_clamp__before"]), "side": "min",
             "bound": Decimal(result["s_clamp__bound"]), "code": "MIN_PREMIUM_APPLIED"} if fired else None
    v1 = today(present, result)
    v2 = build_ruled(present, values, clamp)
    anchors = {r: values[k] for r, k in present.items()}
    if clamp:
        anchors["office_premium"], anchors["constraints"] = clamp["before"], values["k_office"]
    if plant == "bound+0.001":
        v2[2]["op"]["bound_value"] = str(Decimal(v2[2]["op"]["bound_value"]) + Decimal("0.001"))
    if plant == "clamp-as-none":
        v2[2]["op"] = {"kind": "none"}
    payable = rnd(values["k_inst"])
    print(f"  risk={risk} min={min_p} fired={fired} plant={plant}")
    print("   today:", [(r.rung, r.value_minor, r.operation and (r.operation.kind, r.operation.factor or r.operation.applied)) for r in v1])
    print("   ruled:", [(r["rung"], r["value_minor"], format(r["u"], "f"), r["op"] and {k: v for k, v in r["op"].items() if v}) for r in v2])
    print("   ruled reconciles:", reconciles(v2, anchors, payable))


def part_engine_boundary():
    print("== 1. the binding: float vs string, and the engine's own precision")
    r = 1304.837261934
    steps, prev = [], "r"
    for i, f in enumerate(["1.15", "1.131", "1.07", "0.9601", "1.05", "1.12", "1.0375", "0.985"]):
        steps.append((f"k{i}", f"{prev} * {f}"))
        prev = f"k{i}"
    res = evaluate(steps, {"r": r})
    exact_v, p = Decimal(repr(r)), res["r__exact"]
    for i, f in enumerate(["1.15", "1.131", "1.07", "0.9601", "1.05", "1.12", "1.0375", "0.985"]):
        exact_v = exact("*", exact_v, Decimal(f))
        s = res[f"k{i}__exact"]
        print(f"  x{f:<7} float={res[f'k{i}']!r:<22} float-exact? {Decimal(repr(res[f'k{i}'])) == exact_v!s:<5} "
              f"string={s:<32} digits={len(Decimal(s).as_tuple().digits)} string-exact? {Decimal(s) == exact_v}")
    res = evaluate([("y", "x * 1")], {"x": 1e7 / 3})
    print(f"  input conversion: python repr={1e7 / 3!r} engine string={res['x__exact']}")
    for x, f in ((1234.5, "1.0000000000000000001"), (1235.5, "0.9999999999999999999")):
        res = evaluate([("p", f"x * {f}")], {"x": x})
        print(f"  near-tie x={x} *{f}: float={res['p']!r} exact={res['p__exact']} "
              f"float path={score._round_minor(res['p'], 'half_even')} exact path={rnd(Decimal(res['p__exact']))}")


def main(n_per_cell, seed):
    part_engine_boundary()
    print("== 2. the auditor's case on the real builder (raw 60000.4 -> 66000.44 -> 69402.0)")
    present = {"risk_premium": "r", "expense_loading": "e", "office_premium": "e",
               "instalment_loading": "i", "payable_premium": "i"}
    v1 = today(present, {"r": 60000.4, "e": 66000.44, "i": 69402.0})
    print("  ", [(r.rung, r.value_minor, r.operation and r.operation.factor) for r in v1],
          "replay", replay_today(v1), "payable", v1[-1].value_minor)
    print("== 3. worked 9-rung ladder at risk 60000.4")
    nine = [("expense_loading", "{p} * 1.15"), ("commission", "{p} / (1 - 0.125)"),
            ("profit_loading", "{p} * 1.07"), ("optimisation_adjustment", "{p} * 0.9601"),
            ("instalment_loading", "{p} * 1.05"), ("ipt_and_fees", "{p} * 1.12 + 250")]
    ladder_case(60000.4, nine, print_it=True)
    print("== 4. fixture-shaped red candidates (office = risk * 1.1, instalment = office * 1.05)")
    for risk in (61234.5, 123456.7):
        print(" risk", risk)
        ladder_case(risk, [("office_premium", "{p} * 1.1"), ("instalment_loading", "{p} * 1.05")], True)
    print("== 5. a binding clamp (FD 9967), the pre-clamp read, and two planted clamp defects")
    clamp_case(1305.4, 5000)
    clamp_case(1305.4, 1000)
    clamp_case(1305.4, 5000, plant="bound+0.001")
    clamp_case(1305.4, 5000, plant="clamp-as-none")
    print(f"== 6. scale sweep: {n_per_cell} quotes per (decade, optional-rung count), seed {seed}, argv {sys.argv[3:]}")
    rng = random.Random(seed)
    optional = [("expense_loading", "mul"), ("commission", "gross"), ("profit_loading", "mul"),
                ("optimisation_adjustment", "mul"), ("instalment_loading", "mul"), ("ipt_and_fees", "ipt")]
    if len(sys.argv) > 3 and sys.argv[3] == "mixed":  # rungs that apply more than one operation
        optional = [("expense_loading", "mix1"), ("commission", "gross"), ("profit_loading", "mix2"),
                    ("optimisation_adjustment", "mul"), ("instalment_loading", "mul"), ("ipt_and_fees", "ipt")]
    totals = dict(quotes=0, today_replay_fails=0, today_rung_misstated=0, today_factor_wrong=0,
                  ruled_fails=0, ruled_factor_wrong=0, payable_differs=0, planted=0, planted_missed=0)
    print("  decade count subset                                   today_replay_fails ruled_fails")
    for decade in range(3, 8):
        for count in range(0, len(optional) + 1):
            chosen = [optional[i] for i in sorted(rng.sample(range(len(optional)), count))]
            cell_today = cell_ruled = 0
            for _ in range(n_per_cell):
                risk = float(np.float32(rng.uniform(10 ** decade, 10 ** (decade + 1))))
                loadings, applied = [], {}
                for rung, kind in chosen:
                    if kind == "mul":
                        f = str(Decimal(rng.randint(8000, 14000)) / 10000)
                        loadings.append((rung, "{p} * " + f)); applied[rung] = ("multiply", format(Decimal(f).normalize(), "f"))
                    elif kind == "gross":
                        loadings.append((rung, "{p} / (1 - 0.125)")); applied[rung] = ("divide", "0.875")
                    elif kind == "mix1":
                        loadings.append((rung, "{p} * 1.1 / (1 - 0.125)"))
                    elif kind == "mix2":
                        loadings.append((rung, "{p} * 1.07 + 35"))
                    else:
                        loadings.append((rung, "{p} * 1.12 + 250"))
                v1, v2, anchors, payable, present, values = ladder_case(risk, loadings)
                totals["quotes"] += 1
                if replay_today(v1) != v1[-1].value_minor:
                    totals["today_replay_fails"] += 1; cell_today += 1
                if any(r.value_minor != rnd(values[present[r.rung]]) for r in v1 if r.rung in present):
                    totals["today_rung_misstated"] += 1
                sigma, quote_sigma = Decimal(0), sum(
                    (Decimal("5E-5") / abs(Decimal(x.operation.factor)) for x in v1
                     if x.operation and x.operation.kind == "multiply"), Decimal(0))
                own = Decimal(0)
                for idx, r in enumerate(v1):
                    exact_term = Decimal(0)
                    if idx > 0 and r.operation and r.operation.kind == "multiply":
                        exact_term = Decimal("5E-5") * abs(v1[idx - 1].value_minor)
                    if r.rung in present and r.rung != "payable_premium":
                        d_exact = abs(r.value_minor - rnd(values[present[r.rung]]))
                        if d_exact > exact_term + 1:
                            MECH["exceed_exact_prev"] += 1
                        if exact_term > 0:
                            MECH["exact_tightness_max"] = max(MECH["exact_tightness_max"],
                                Decimal(max(d_exact - 1, 0)) / exact_term)
                            MECH["exact_rel_max"] = max(MECH["exact_rel_max"],
                                exact_term / abs(rnd(values[present[r.rung]])))
                    own = Decimal(0)
                    if r.operation and r.operation.kind == "multiply":
                        own = Decimal("5E-5") / abs(Decimal(r.operation.factor))
                        sigma += own
                    if r.rung in present and r.rung != "payable_premium":
                        new_v = rnd(values[present[r.rung]])
                        if abs(r.value_minor - new_v) > own * abs(new_v) + 1:
                            MECH["exceed_own_term"] += 1
                        MECH["own_max"] = max(MECH["own_max"], own)
                        if own > 0:
                            MECH["own_tightness_max"] = max(MECH["own_tightness_max"],
                                Decimal(max(abs(r.value_minor - new_v) - 1, 0)) / (own * abs(new_v)))
                        mech = sigma * abs(new_v) + 1  # the per-output mechanism bound
                        MECH["rungs"] += 1
                        if abs(r.value_minor - new_v) > mech:
                            MECH["exceed_per_output"] += 1
                        if abs(r.value_minor - new_v) > quote_sigma * abs(new_v) + 1:
                            MECH["exceed_quote_wide"] += 1
                        MECH["sigma_max"] = max(MECH["sigma_max"], sigma)
                        if sigma > Decimal("2E-4"):
                            MECH["sigma_over_2e-4"] += 1
                        if sigma > 0:
                            MECH["tightness_max"] = max(MECH["tightness_max"],
                                Decimal(max(abs(r.value_minor - new_v) - 1, 0)) / (sigma * abs(new_v)))
                        diff = abs(r.value_minor - rnd(values[present[r.rung]]))
                        rel = Decimal(diff) / abs(values[present[r.rung]])
                        if rel > REL_MAX[0][0]:
                            REL_MAX[0] = (rel, diff, format(values[present[r.rung]], "f"), r.rung)
                        rel1 = Decimal(max(diff - 1, 0)) / abs(values[present[r.rung]])
                        if rel1 > REL1_MAX[0][0]:
                            REL1_MAX[0] = (rel1, diff, format(values[present[r.rung]], "f"), r.rung)
                        if diff:
                            key = f"1e{decade}"
                            DIFF_MAX[key] = max(DIFF_MAX.get(key, 0), diff)
                            DIFF_HIST[min(diff, 10)] = DIFF_HIST.get(min(diff, 10), 0) + 1
                if any(r.rung in applied and applied[r.rung][0] == "multiply" and Decimal(r.operation.factor) != Decimal(applied[r.rung][1]) for r in v1):
                    totals["today_factor_wrong"] += 1
                if not reconciles(v2, anchors, payable):
                    totals["ruled_fails"] += 1; cell_ruled += 1
                for r in v2:
                    if r["rung"] in applied and (r["op"]["kind"], r["op"].get("factor") or r["op"].get("divisor")) != applied[r["rung"]]:
                        totals["ruled_factor_wrong"] += 1
                        if len(sys.argv) > 4:
                            print("   MISS", r["rung"], applied[r["rung"]], r["op"], "digits", len(r["u"].as_tuple().digits))
                if v1[-1].value_minor != payable:
                    totals["payable_differs"] += 1
                for _label, broken in plants(v2):
                    totals["planted"] += 1
                    if reconciles(broken, anchors, payable):
                        totals["planted_missed"] += 1
            names = ",".join(r.split("_")[0] for r, _ in chosen) or "-"
            print(f"  1e{decade}   {count}     {names:<48} {cell_today:<18} {cell_ruled}")
    print("  totals:", totals)
    print("  today's non-payable rung value minus its engine value rounded once, |diff| by decade (max):", DIFF_MAX)
    print("  rungs by |diff| in minor units (10 = 10 or more):", dict(sorted(DIFF_HIST.items())))
    rel, diff, value, rung = REL_MAX[0]
    print(f"  largest |diff| / engine value over non-payable rungs: {rel:.3E} ({diff} minor units on {rung} = {value})")
    rel, diff, value, rung = REL1_MAX[0]
    print(f"  largest (|diff| - 1) / engine value over non-payable rungs: {rel:.3E} ({diff} minor units on {rung} = {value})")
    print("  mechanism bounds: sigma = sum of 5E-5/|q| over today's quantised factors up to the rung; own = the rung's own 5E-5/|q|; bound = term * |new| + 1; exact_prev: bound = 5E-5 * |today's previous rung| + 1 on a multiply rung, else 1:",
          {k: (f"{v:.3E}" if isinstance(v, Decimal) else v) for k, v in MECH.items()})


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
```
