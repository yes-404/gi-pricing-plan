---
id: FD-9949
family: finding
title: reconcile_ladder is vacuous at its call site, so every trace's ladder_reconciled true asserts a reconciliation that was never performed, and the vacuity hid a 4 dp drift that breaks FR-248 at realistic scale
status: active
created: 2026-09-30
owner: auditor
tree: 11c76b6c83647c512796fedb9c0143927dcd78cb
corrected_by: []
relates: [WK-674, SL-1257, FR-248, NFR-496, FR-261]
---

# FD-9949 — `reconcile_ladder` is vacuous, and it hid the premium ladder's 4 dp drift

## Finding

**Severity: HIGH**, on the maintainer's entry of 2026-09-30 15:33:22 BST (see *Severity*). **Proposed by
the auditor; the disposition is the lead's.** FD-9949 is a working id, minted at the records PR. **Two
limbs, one root: the vacuous check hid the builder's drift.**

**Limb 1 — the check is vacuous.** `reconcile_ladder(risk_premium_minor, steps)`
(`packages/pricing-core/src/pricing_core/money.py:55`) says in its docstring that the ladder reconciles
when "each rung's recorded value is exactly what the previous rung plus that rung's operation produced"
(FR-248, "to the penny"). Its body is:

```python
if not steps:
    return True
if steps[0][1] != risk_premium_minor:
    return False
return all(isinstance(value, int) for _, value in steps)
```

It is given `(rung, value_minor)` pairs, **not the operations**, so it **cannot** compare any rung with the
previous rung plus an operation. At its scoring call site it is **vacuous**: `score.py:736-738` sets
`risk_premium_minor = ladder_steps[0][1]` and then calls `reconcile_ladder(risk_premium_minor,
ladder_steps)`, so the only comparison it can fail compares a value **with itself**; every `int` ladder
returns `True` **by construction**, a check that cannot fail (`CLAUDE.md` §13). `score_one` writes the result
to `Trace.ladder_reconciled` on every trace it builds (`score.py:738`, `:744`); `score.py:103` calls the check
"shallow — first-rung and int-ness only" and the same comment says the ladder reconciles "by construction".
**So every stored trace's `ladder_reconciled: true` asserts an FR-248 reconciliation that was never
performed.** `LADDER_RECONCILIATION_FAILED` is registered (`backend/src/app/errors.py:326`) and raised
nowhere. A second consumer is vacuous the same way: `properties.py:303`, the `LadderReconciles` regression
property (FR-261), calls `reconcile_ladder(risk, steps)` with `risk` read from the first rung.

**Limb 2 — FR-248 fails at realistic scale, and the vacuous check hid it.** `_build_ladder`
(`score.py:551-624`) quantises each multiply factor to 4 decimal places from raw values,
`factor = (Decimal(repr(raw)) / Decimal(prev_minor)).quantize(Decimal("0.0001"))`, records that factor, and
sets each rung's value as `apply_factor(prev_minor, factor, mode)`; but it sets the `payable_premium` rung
from the **raw output** (`_round_minor(raw, mode)`), labelled `round`. The recorded operations therefore do
not replay to the recorded payable premium. At raw `60000.4 → 66000.44 → 69402.0` the ladder is 60000,
66000, 66000, 69399 (×1.0515), 69402 (round), and **replaying the recorded operations gives 69399, not
the recorded payable 69402** (evidence 6). At fixture scale (~1300 minor units) the difference rounds away,
which is why the tests never saw it. The **price is right**; the governed transparency artifact misstates how
it was reached, at every quote large enough for a 4 dp factor to move a whole minor unit. FR-248 (`03:155`)
and `NFR-496` (`03:1157`) say "to the penny" and "in 100 % of scored quotes".

## Evidence

Read and run at `origin/main` `11c76b6c83647c512796fedb9c0143927dcd78cb`, 2026-09-30, by the filer, except
where a claim names another auditor.

**1. The code (limb 1).** `money.py:55-70` as quoted, with its docstring line "This is asserted continuously
in non-prod and sampled in prod, so it lives in the core where both paths reach it." Callers, by
`git grep -n "reconcile_ladder" -- packages backend/src`: `score.py:215` (import), `:738` (the call above),
`properties.py:41` (import), `:303` (the second call). **No test calls `reconcile_ladder` directly**
(`git grep -n "reconcile_ladder" -- packages/pricing-core/tests backend/tests tests` finds a docstring at
`test_rating_score.py:192` and `:195`).

**2. Nothing raises the code.** `git grep -n "LADDER_RECONCILIATION_FAILED" -- packages backend/src` returns
only `backend/src/app/errors.py:326`; the other hits are `backend/tests/test_worker_raise_sites.py:38` (a list
of codes) and documents. `03` §5.1 owns the code (`03:779`). The same observation was made on 2026-08-29 as
`F-W11-2-1` in `PL-847` (`docs/plans/PL-00847-*.md:570`), owner "the decision-maker", which argued the ladder
"reconciles by construction" so the check "can only fire on a genuine defect".
`git grep -n "F-W11-2-1" -- docs` outside that plan finds no register row and no other citation. What that
finding did not say is that the check **cannot fire on a genuine defect either**, and that limb 2 is one.

**3. The requirement it overstates.** `FR-248` (`03:155`): "Each ladder rung records both the value and the
operation that produced it (multiplicative factor or additive amount), so the ladder reconciles exactly:
applying every recorded operation to `risk_premium` reproduces `payable_premium` to the penny. This
reconciliation is asserted at scoring time in `dev`/`uat` and sampled in `prod`." `NFR-496` (`03:1157`):
"the ladder reconciles to the penny in 100 % of scored quotes (FR-248), asserted continuously in non-prod and
sampled in prod." `model_schema/scoring.py:172-177` (the `ScoringResult` docstring) and
`scoring.schema.json:59-62` state the same invariant as "enforced by `pricing_core.rating.score`". `SL-1257`
(WK-674 Slice 3) carries "NFR-496 prod-sampling limb" in its title (`docs/roadmap.md:767`).

**4. What a real check reads is already recorded.** Each `LadderRung` carries its `operation`
(`model_schema/scoring.py:127-133`; `LadderOperation`: `kind` `multiply`, `add`, `round` or `none`, with
`factor`, `amount_minor`, `mode`, `dp`). A transition check needs only the `ScoringResult`'s own
`premium_ladder`. The one place it exists is test code, `test_rating_score.py:191-236` (the `NFR-496`
marker), which applies `apply_factor` for `multiply` and adds `amount_minor` for `add`, and says its manual half
"is strictly stronger than `reconcile_ladder` itself". **It is weaker in one place that matters for limb 2:**
for `kind == "round"` it sets `value = rung.value_minor`, so it accepts *any* payable premium. A `round` at
`dp=0` on an integer minor-unit value is the identity, so a strict replay must leave the value unchanged and
compare it with the recorded rung.

**5. Reproduction, limb 1 (the check is vacuous)** (scratch script `ladder_repro.py`, kept with the evidence,
under `uv run --no-sync python` at `11c76b6c`; it reuses `test_rating_score.py`'s `_compiled` and `_ctx`).
Output, verbatim:

```text
reconcile_ladder(good)      -> True
reconcile_ladder(off-by-1)  -> True
reconcile_ladder(way off)   -> True
reconcile_ladder(first rung != risk) -> False (the only value it can reject)
clean run: ladder [('risk_premium', 1305), ('office_premium', 1436), ('constraints', 1436), ('instalment_loading', 1507), ('payable_premium', 1507)] trace.ladder_reconciled = True
tampered run (rung 2 + 1 minor): ladder [('risk_premium', 1305), ('office_premium', 1437), ('constraints', 1436), ('instalment_loading', 1507), ('payable_premium', 1507)] trace.ladder_reconciled = True
re-derivation DISAGREES at rung office_premium : 1436 != 1437
```

The first three lines call the function with a correct ladder, a ladder whose second rung is one penny too high,
and a ladder that is wildly wrong: all return `True`. The only input it can reject is a first rung different
from the number the caller passes, which `score.py:737` never does. **The last three lines are through the real
call site:** `score_one(…, trace=True)` with `_build_ladder`'s result tampered by one minor unit on the second
rung, so a one-penny-off ladder comes out of `score_one` with `trace.ladder_reconciled = True`.

**6. Reproduction, limb 2 (the drift).** Scratch script `ladder_drift.py`, kept with the evidence. It calls the
real `_build_ladder` (`score.py:551`) on the fixture's compiled algorithm with raw values as the engine result,
and replays the recorded operations strictly (item 4: `round` at `dp=0` is the identity). **Not run through
`score_one`:** the repository's fixture algorithm scores at ~1300 minor units, where the drift is rare (below),
and no fixture algorithm scores at ~6e4; building one would be a new fixture, not a run of the shipped path.
The flag for such a ladder is computed by the same `reconcile_ladder` call, shown below. Output for the
maintainer's raw chain, verbatim:

```text
output steps (name -> consumes, dp, mode):
   risk_premium_minor -> ['risk_premium_minor'] 0 half_even
   office_premium_minor -> ['office_premium_minor'] 0 half_even
   instalment_loading_minor -> ['instalment_loading_minor'] 0 half_even
   payable_premium_minor -> ['instalment_loading_minor'] 0 half_even

raw 60000.4 -> 66000.44 -> 69402.0 (risk, office, instalment; payable = the instalment raw):
   risk_premium 60000 None
   office_premium 66000 ('multiply', '1.1000', 'half_even')
   constraints 66000 ('none', None, None)
   instalment_loading 69399 ('multiply', '1.0515', 'half_even')
   payable_premium 69402 ('round', None, 'half_even')
replay of the recorded operations: DISAGREES at payable_premium: replay 69399 != recorded 69402
trace flag at this ladder (reconcile_ladder as shipped): True
```

The `payable_premium` step consumes `instalment_loading_minor`, so the payable rung is `round(raw)`
(69402) while the instalment rung is `apply_factor(66000, 1.0515)` (69399); the factor `1.0515` is a
4 dp back-derivation, not a rate. **Scale sweep** (2000 random quotes per magnitude, seed 20260930; raw chain
`office = risk × 1.10`, `instalment = office × 1.05`, `payable = instalment`; strict replay):

| Magnitude (minor units) | Ladders that do not replay | Largest \|replay − payable\| |
|---|---|---|
| 1 000 | 53 / 2000 (2.7 %) | 1 |
| 10 000 | 571 / 2000 (28.6 %) | 1 |
| 100 000 | 718 / 2000 (35.9 %) | 2 |
| 1 000 000 | 739 / 2000 (37.0 %) | 2 |
| 10 000 000 | 784 / 2000 (39.2 %) | 2 |

The sweep is over a synthetic raw chain with a realistic 5 % loading, **not over stored quotes**; it shows the
drift is not a corner case at realistic scale, and that at ~1e3 it is already present in one quote in
thirty-seven. It does not measure how often real algorithms hit it. Finding: auditor-close1255's scratch run of
`_build_ladder` at `11c76b6c` (as relayed by the lead) is the first observation of the 69399 / 69402 case; the
filer reproduced it and swept it.

**7. The data read.** *Question:* what stored records carry `ladder_reconciled`, and what stored premium
ladders exist that could be replayed? `scoring_traces` stores a blob reference (`blob_sha256`) plus
`served_summary` and `pending_quote_context` (`jsonb`); the persisted `Trace` (`model_schema/scoring.py:158-168`)
has `steps` and `ladder_reconciled` and **no ladder**, so a stored trace cannot be replayed; only a stored
`ScoringResult` ladder can.

| Store | Corpus | Predicate and command | Result |
|---|---|---|---|
| PostgreSQL 16 (`gi-pricing-postgres-1`) | 80 databases, **3787 tables** (every `relkind` r, p, m outside `pg_catalog`, `information_schema`, `pg_toast`, `pg_temp*`), every column as `r::text` | `select count(*) … where r::text ~ 'ladder_reconciled"+\s*:\s*true'` (and `…false`, and `ladder_reconciles`), in `BEGIN TRANSACTION READ ONLY` with `PGOPTIONS='-c default_transaction_read_only=on'`; `ladder_data.py`, `PG_ONLY=1` | **0** rows `true`, **0** `false`, **0** `ladder_reconciles` |
| MinIO (`gi-pricing-minio-1`) | 5 buckets, **15 327 objects**, each object containing `ladder_reconcile` parsed as JSON | boto3 list and get only; `ladder_data.py` | **4134** objects `ladder_reconciled = true`, **0** `false`; all in `gip-test-blobs` |
| PostgreSQL, stored ladders | 81 databases, **3841 tables** | `select count(*) … where r::text ~ 'premium_ladder'` per table, then the matching `served_summary` and `pending_quote_context` values parsed and each ladder replayed strictly; `ladder_stored.py`, `ladder_pg_rows.py` | **11** rows contain `premium_ladder`, all in `scoring_traces.served_summary` in **one** database (`gipricing_wt-ci-structure`, `environment = uat`, `created_at` 2026-09-06 09:35 to 09:36); 10 parse as ladders |
| MinIO, stored ladders | **15 428 objects** | boto3, JSON parsed, `premium_ladder` searched recursively | **0** objects |

The 4134 `ladder_reconciled` objects are the trace-shaped records auditor-922 classified in FD-1297's sweep (3986
then; the growth is test runs since). **Every stored `ladder_reconciled` in every reachable store is `true`,
none is `false`, and all are in a test-scratch bucket.** The 10 stored ladders are **synthetic**: two rungs
(`risk_premium` 10000, `payable_premium` 12000) with `operation: null`, which `_build_ladder` never emits (it
always records an operation on every rung after the first, `payable_premium` as `round`), so 9 of the 10
"disagree" only because they have no operations, and **they say nothing about the builder's drift**. **No stored
ladder produced by the real builder exists to replay**, so the number of stored traces whose ladder does not
replay is **not measurable from stored data**: it is 0 replayable and unknown otherwise. There is no
production deployment yet (WK-674 builds one).

*Positive controls and a bug they caught.* (a) A `TEMP` table with `{"ladder_reconciled": true}`,
`{"ladder_reconciled": false}` and `{"x": 1}` scanned with the same predicate: the first predicate I wrote,
`"ladder_reconciled"\s*:\s*true`, counted **0**, because `r::text` renders a `jsonb` column with its quotes doubled
(`(1,"{""ladder_reconciled"": true}")`); it was changed to `ladder_reconciled"+\s*:\s*true`, which counts **1** on the
planted true row and **1** on the planted false row. The first full PostgreSQL run (0 rows) used the wrong
predicate and is **withdrawn**; the corrected run is reported. (b) `ladder_lib_ctl.py`: the strict replay of the
69399/69402 ladder returns `('payable_premium', 69399, 69402)`, a consistent ladder returns `None`, and the
recursive finder finds a ladder nested in a `served_summary`-shaped object. The MinIO paths parse JSON, so (a)
does not apply to them; their positive population is the 4134.

*Slot and load.* Every multi-database run took a gate slot (`flock -w 1800 -E 99 /tmp/slots/gate-1` or
`gate-2`, with `LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2`); `uptime` at start and end:
flag scan `14:15:29` load 4.84 to `14:29:02` load 2.87; corrected PostgreSQL flag scan `14:37:09` load 2.82 to
`14:38:01` load 3.47; stored-ladder scan (PostgreSQL and MinIO) `14:41:22` load 4.96 to `15:11:12` load 17.97;
`scoring_traces` replay `15:11:43` load 17.68 to `15:30:01` load 3.47. The load spike during the third run was
other work on the box, not this scan's.

*Limits.* The MinIO counts are at one tree of the store (test runs add objects). Other environments, any dev or
uat stack elsewhere and CI databases are out of scope, as in FD-1294's and FD-1297's checks. Batch score outputs
(parquet) were not decoded; regression-run results were searched as text only.

## Severity

**HIGH**, on the maintainer's entry of 2026-09-30 15:33:22 BST in `~/gi-pricing-plan.local/channel/to-lead.md`,
"DECISIONS on N5 (the ladder builder's drift): fold into FD 9949 → HIGH; the builder design is a DP for a
fresh high-effort DM" (outside the repository; quoted):

> **(1) Fold N5 into FD 9949 as limb 2; FD 9949 is now HIGH.** One root: the vacuous check hid the builder's 4-dp factor drift. Limb 2's evidence: auditor-close1255's scratch run of the real `_build_ladder` (score.py:551-624) at 11c76b6c; raw 60000.4 → 66000.44 → 69402.0 gives a ladder replaying to **69399 ≠ payable 69402**. **The price is correct; the governed transparency artifact misstates how it was reached** for realistic-scale quotes, so FR-248 fails today. **HIGH** because the platform's core promise ("transparency of the maths", CLAUDE.md §1) is violated on every realistic quote's evidence, though no production or mispricing. **The data read** (stored traces whose ladder doesn't replay) goes in the FD.

This **supersedes** the same file's earlier severity, **medium**, set by the entry "2026-09-30 15:13:26 BST —
DECISIONS: the reconcile_ladder FD (MEDIUM, WK-674 S3); DP-S3-3 → (a), ruled by me as scope" ("a missing
detector plus overstated evidence, not a mispricing, and no production"), which covered limb 1 alone. The
vacuity itself is confirmed by the entry "2026-09-30 15:14:36 BST — FD 9949: the vacuity is confirmed by me"
(the title says *vacuous*, not "shallow"). The data-read gap the 15:33:22 entry names ("stored traces whose ladder
doesn't replay") is answered in evidence 7: not measurable, because no stored ladder from the real builder exists.

## Disposition

**Proposed by the auditor; the verdict is the lead's.** The maintainer's decisions, recorded here rather than
restated as rulings:

- **Owner: WK-674 Slice 3** (`SL-1257`), which carries the fix and the `NFR-496` prod-sampling limb. The
  slice's plan (working id 9947) holds it on the pending decision below.
- **Limb 1, the check (the entry "2026-09-30 15:17:54 BST — audit round-up: decisions", the ruling on the plan
  for working id 9947):** **decouple the ladder check from sampling.** `reconcile_ladder`, taking the
  operations (the signature changes; the write-set adds `pricing_core/__init__`, `rating/properties.py` and the
  census tests), **runs on every scored quote in every Environment, never sampled**;
  `rating.trace_sample_rate` governs trace persistence only, so no Environment can switch the FR-248 / NFR-496
  check off. If the spec text ("sampled in prod": `03:155`, `03:1157`, the `money.py` docstring) says otherwise,
  the slice's spec task amends it, dated, citing that entry.
- **Limb 1 acceptance, red first, through the real call site** (the 15:14:36 entry): `score_one` on a ladder with
  a one-penny-off rung yields **not reconciled**, not only a unit test of the function; the trace flag reflects
  the real check; **with `trace_sample_rate = 0` a one-penny-off ladder is still not reconciled through
  `score_one`**. A correct ladder passes.
- **No back-fill of "verified".** A stored `ladder_reconciled: true` from before the fix is not upgraded.
  Historical traces keep a flag documented as "first-rung plus int only (pre-fix)", **or** a separate
  `ladder_check_version` distinguishes them (a contract change, `model_schema/scoring.py:168` and
  `scoring.schema.json:88`, regenerated from `model-schema`, spec-first); the plan chooses.
- **Limb 2, which side is corrected — DP-S3-5, pending.** This is a transparency design choice (FR-248's exact
  semantics against FR-226 / NFR-496's "rounding once"), routed by the maintainer to a fresh high-effort
  decision-maker. **This finding does not pre-empt it.** The maintainer's steer, for that ruling to weigh, is in
  the 15:33:22 entry (the ladder must show the true operations an actuary recognises, not a back-derived
  ×1.0515, and still reconcile to the penny). What it must decide includes any amendment to FR-248, the
  ladder's contract shape (a `model-schema` change) and golden-quote impact.
- **Limb 2 acceptance** (the maintainer's, 15:33:22): an **exact-replay red case at realistic scale** (a quote
  whose ladder must replay to the payable premium exactly, red before the fix), plus a **scale sweep of about
  1e3 to 1e7 minor units** in S3's acceptance. Evidence item 6's sweep is the shape of the control, not a
  substitute for it.
- **`LADDER_RECONCILIATION_FAILED`:** whether a failed reconciliation is refused (raising the registered code) or
  only recorded is the plan's decision point; this finding does not decide it. The stored flag must never read
  `true` for a ladder that has not been checked.

**Event that next confirms or discharges it:** WK-674 Slice 3 merges with (a) a `reconcile_ladder` (or its
replacement) that takes the operations, runs on every scored quote, and is red first on a one-penny-off rung
through `score_one` (also at `trace_sample_rate = 0`) at both call sites (`score.py:738`, `properties.py:303`);
(b) the DP-S3-5 ruling implemented, with the realistic-scale exact-replay red case and the 1e3 to 1e7 sweep; and
(c) the historical-flag rule implemented as the plan states.

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it. The owner and the
HIGH severity are the maintainer's, per the entries quoted under *Severity* and *Disposition*.

Ownership shape: event
