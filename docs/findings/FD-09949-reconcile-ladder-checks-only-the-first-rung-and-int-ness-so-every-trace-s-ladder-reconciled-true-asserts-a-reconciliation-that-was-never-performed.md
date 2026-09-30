---
id: FD-9949
family: finding
title: reconcile_ladder checks only the first rung and int-ness, so every trace's ladder_reconciled true asserts a reconciliation that was never performed (FR-248)
status: active
created: 2026-09-30
owner: auditor
tree: 11c76b6c83647c512796fedb9c0143927dcd78cb
corrected_by: []
relates: [WK-674, SL-1257, FR-248, NFR-496, FR-261]
---

# FD-9949 — `reconcile_ladder` cannot check a rung transition, and at its scoring call site it compares a value with itself

## Finding

**Severity: medium**, on the maintainer's decision (see *Severity*). **Proposed by the auditor; the
disposition is the lead's.** FD-9949 is a working id, minted at the records PR.

`reconcile_ladder(risk_premium_minor, steps)` (`packages/pricing-core/src/pricing_core/money.py:55`)
says in its docstring that the ladder reconciles when "each rung's recorded value is exactly what the
previous rung plus that rung's operation produced" (FR-248, "to the penny"). Its body is:

```python
if not steps:
    return True
if steps[0][1] != risk_premium_minor:
    return False
return all(isinstance(value, int) for _, value in steps)
```

It is given `steps` as `(rung, value_minor)` pairs, **not the operations**, so it **cannot** compare any
rung with the previous rung plus an operation. It checks the first rung against a number the caller
supplies, and that every value is an `int`. At its scoring call site it is **vacuous**:
`score.py:736-738` sets `risk_premium_minor = ladder_steps[0][1]` and then calls
`reconcile_ladder(risk_premium_minor, ladder_steps)`, so the first-rung comparison compares the value with
itself, and every `int` ladder returns `True`. `score_one` writes the result to `Trace.ladder_reconciled`
on every trace it builds (`score.py:738`, `:744`). `score.py:103` calls the check "shallow — first-rung
and int-ness only" in a comment about the ladder, and the module states that the ladder reconciles "by
construction", so the flag reads as a verified fact where no verification runs.

**So every stored trace's `ladder_reconciled: true` asserts an FR-248 reconciliation that was never
performed.** That flag is the field a reader, a regression property (`ladder_reconciles`, FR-261) and
`NFR-496`'s "asserted continuously in non-prod and sampled in prod" rely on. The prices themselves are
probably right, because the ladder is built by construction (below); what is missing is the **detector**,
and what is overstated is the **evidence**. `LADDER_RECONCILIATION_FAILED` is registered
(`backend/src/app/errors.py:326`) and raised nowhere.

A second consumer has the same weakness: `properties.py:303`, the `LadderReconciles` regression property,
calls `reconcile_ladder(risk if risk is not None else 0, steps)` with `risk` read from the ladder's own
`risk_premium` rung. That rung is the first rung, so it is vacuous the same way.

## Evidence

Read and run at `origin/main` `11c76b6c83647c512796fedb9c0143927dcd78cb`, 2026-09-30.

**1. The code.** `money.py:55-70` as quoted above, with its docstring: "This is asserted continuously in
non-prod and sampled in prod, so it lives in the core where both paths reach it." Its callers, by
`git grep -n "reconcile_ladder" -- packages backend/src`: `score.py:215` (import), `:738` (the call above),
`properties.py:41` (import) and `:303` (the second call). **No test calls `reconcile_ladder` directly**
(`git grep -n "reconcile_ladder" -- packages/pricing-core/tests backend/tests tests` finds only two
mentions in a docstring at `test_rating_score.py:192` and `:195`).

**2. Nothing raises the code.** `git grep -n "LADDER_RECONCILIATION_FAILED" -- packages backend/src`
returns only `backend/src/app/errors.py:326`; the other hits are `backend/tests/test_worker_raise_sites.py:38`
(a list of codes) and documents. `03` §5.1 owns the code (`03:779`). The same observation was made on
2026-08-29 as `F-W11-2-1` in `PL-847` (`docs/plans/PL-00847-*.md:570`), owner "the decision-maker",
which argued the ladder "reconciles by construction" so the check "can only fire on a genuine defect".
`git grep -n "F-W11-2-1" -- docs` outside that plan finds no register row and no other citation. What that
finding did not say, and this one does, is that the check **cannot fire on a genuine defect either**.

**3. The requirement it overstates.** `FR-248` (`03:155`): "Each ladder rung records both the value and
the operation that produced it (multiplicative factor or additive amount), so the ladder reconciles
exactly: applying every recorded operation to `risk_premium` reproduces `payable_premium` to the penny.
This reconciliation is asserted at scoring time in `dev`/`uat` and sampled in `prod`." `NFR-496`
(`03:1157`): "the ladder reconciles to the penny in 100 % of scored quotes (FR-248), asserted continuously
in non-prod and sampled in prod." `SL-1257` (WK-674 Slice 3) carries "NFR-496 prod-sampling limb" in its
title (`docs/roadmap.md:767`).

**4. What a real check would read is already recorded.** Each `LadderRung` carries its `operation`
(`model_schema/scoring.py:127-133`; `LadderOperation`: `kind` `multiply`, `add`, `round` or `none`, with
`factor`, `amount_minor`, `mode`, `dp`). A transition check therefore needs only the `ScoringResult`'s own
`premium_ladder`, no new data. The check exists in one place, as test code:
`packages/pricing-core/tests/test_rating_score.py:191-236` (`test_the_ladder_reconciles_over_a_battery_of_generated_contexts`,
the `NFR-496` marker) applies `apply_factor` for `multiply`, adds `amount_minor` for `add`, and compares
after each rung. Its docstring says the manual half "is strictly stronger than `reconcile_ladder` itself,
which only checks the first rung and int-ness". Two limits a fix must design for, not decide here: the
`payable_premium` rung's `round` operation is derived from the un-rounded engine value
(`score.py:_build_ladder`), not from the previous integer rung, so the test can only compare that rung with
its own recorded value; and `_build_ladder` derives each recorded operation from the delta between
consecutive rungs and reapplies it, so a check over the *recorded* operations proves consistency of the
record, which is what FR-248 states.

**5. Reproduction** (scratch script `ladder_repro.py`, kept with the evidence, run under `uv run --no-sync
python` at `11c76b6c`; it reuses `test_rating_score.py`'s `_compiled` and `_ctx`). Output, verbatim:

```text
reconcile_ladder(good)      -> True
reconcile_ladder(off-by-1)  -> True
reconcile_ladder(way off)   -> True
reconcile_ladder(first rung != risk) -> False (the only value it can reject)
clean run: ladder [('risk_premium', 1305), ('office_premium', 1436), ('constraints', 1436), ('instalment_loading', 1507), ('payable_premium', 1507)] trace.ladder_reconciled = True
tampered run (rung 2 + 1 minor): ladder [('risk_premium', 1305), ('office_premium', 1437), ('constraints', 1436), ('instalment_loading', 1507), ('payable_premium', 1507)] trace.ladder_reconciled = True
re-derivation DISAGREES at rung office_premium : 1436 != 1437
```

The first three lines call the function with a correct ladder, a ladder whose second rung is one penny too
high, and a ladder that is wildly wrong (`[1000, 99999, 5]`): all three return `True`. The only input it
can reject is a first rung different from the number the caller passes, which `score.py:737` never does.
The last three lines are end to end through `score_one(…, trace=True)`: `_build_ladder`'s result is
tampered by one minor unit on the second rung, the trace still reports `ladder_reconciled = True`, and the
manual re-derivation that `NFR-496`'s test performs disagrees at `office_premium`.

**6. The data read.** *Question:* how many stored traces carry `ladder_reconciled`, and with what value?
`scoring_traces` (`id, workspace_id, quote_id, rating_version_ref, bundle_hash, sample_reason, environment,
blob_sha256, created_at, status, pending_quote_context, served_summary`) stores a blob reference, so the flag
lives in the trace blob.

| Store | Corpus | Predicate and command | Result |
|---|---|---|---|
| PostgreSQL 16 (`gi-pricing-postgres-1`) | 80 databases with `datallowconn`, **3787 tables** (every `relkind` r, p, m outside `pg_catalog`, `information_schema`, `pg_toast`, `pg_temp*`), every column as `r::text` | per table `select count(*) … where r::text ~ 'ladder_reconciled"+\s*:\s*true'` (and `…false`, and `ladder_reconciles`), each in `BEGIN TRANSACTION READ ONLY` with `PGOPTIONS='-c default_transaction_read_only=on'`; `ladder_data.py` with `PG_ONLY=1` | **0 rows** for `true`, **0** for `false`, **0** for `ladder_reconciles` |
| `scoring_traces` population | 75 databases hold the table | `select count(*) from scoring_traces` | **24 rows** (references only) |
| MinIO (`gi-pricing-minio-1`) | all 5 buckets, **15 327 objects**, each object with the text `ladder_reconcile` parsed as JSON | boto3 list and get only; `ladder_data.py` | **4134** objects with `ladder_reconciled = true`, **0** with `false`, none non-JSON; **all in `gip-test-blobs`** |

The 4134 are the trace-shaped records (per-quote score traces) that auditor-922 classified in FD-1297's
sweep (3986 then; the growth is test runs since). So **every stored `ladder_reconciled` in every reachable
store is `true`, none is `false`, and all are in a test-scratch bucket**: there is no production
deployment yet (WK-674 builds one). A `false` could never have been written by a real defect either, for
the reason above.

*Positive control for the PostgreSQL path, and a bug it caught.* A `TEMP` table with `{"ladder_reconciled":
true}`, `{"ladder_reconciled": false}` and `{"x": 1}` was scanned with the same predicate. The first
predicate I wrote, `"ladder_reconciled"\s*:\s*true`, counted **0**: `r::text` renders a `jsonb` column with
its quotes doubled (`(1,"{""ladder_reconciled"": true}")`), so a plain double quote never matches. It was
changed to `ladder_reconciled"+\s*:\s*true`, which counts **1** on the planted true row and, with `false`,
**1** on the planted false row. The first full PostgreSQL run (0 rows) used the wrong predicate and is
**withdrawn**; the corrected run is the one reported. (The MinIO path parses JSON and was not affected; its
positive population is the 4134.)

*Slot and load.* Both multi-database runs took a gate slot: `flock -w 1800 -E 99 /tmp/slots/gate-1` (the
first, PostgreSQL and MinIO; `uptime` `14:15:29` load 4.84 at the start, `14:29:02` load 2.87 at the end)
and `gate-2` (the corrected PostgreSQL run; `14:37:09` load 2.82 and `14:38:01` load 3.47), with
`LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2`.

*Limits, stated so the zeros are read correctly.* The MinIO count is at one tree of the store (test runs add
objects); other environments, any dev or uat stack elsewhere, and CI databases are out of scope, as in
FD-1294's and FD-1297's checks. Regression-run property results (`ladder_reconciles`) were searched as text
in PostgreSQL and in every MinIO object containing the string, and none was found.

## Severity

**Medium**, on the maintainer's entry of 2026-09-30 15:13:26 BST in `~/gi-pricing-plan.local/channel/to-lead.md`,
"DECISIONS: the reconcile_ladder FD (MEDIUM, WK-674 S3); DP-S3-3 → (a), ruled by me as scope" (outside the
repository; quoted verbatim):

> **FD: yes, MEDIUM, owner WK-674 S3** (it carries the fix). **Verified by me at 11c76b6c:** `reconcile_ladder(risk_premium_minor, steps)` (money.py:55-70) **isn't given the operations**, so it *cannot* check rung transitions; its body checks only the first rung and int-ness. LADDER_RECONCILIATION_FAILED is raised nowhere (only errors.py:326 and a test list). **And it feeds governance evidence:** score.py:738 sets **`ladder_reconciled` on every scoring trace** from this shallow check (score.py:103's comment admits "shallow"). So **every stored trace's `ladder_reconciled: true` asserts an FR-248 reconciliation that was never performed.**
>   - The FD states that meaning explicitly. **The fix must not back-fill "verified":** historical traces keep a flag documented as "first-rung plus int only (pre-fix)", or get a separate `ladder_check_version`. The S3 plan says which. **Acceptance, red first:** an off-by-one-penny rung fails; a correct ladder passes; the trace flag reflects the real check.
>   - **Why MEDIUM, not HIGH:** a missing detector plus overstated evidence, not a mispricing, and no production. The data read (how many stored traces carry the flag) goes in the FD.

## Disposition

**Proposed by the auditor; the verdict is the lead's.** The maintainer's decision, recorded here rather than
restated as a ruling:

- **Owner: WK-674 Slice 3** (`SL-1257`), which carries the fix and the `NFR-496` prod-sampling limb. The
  slice's plan (working id 9947) says how historical flags are handled.
- **Acceptance, red first:** an off-by-one-penny rung fails the check; a correct ladder passes; **the trace
  flag reflects the real check**, at both call sites (`score.py:738` and `properties.py:303`, the
  `ladder_reconciles` property).
- **No back-fill of "verified".** A stored `ladder_reconciled: true` from before the fix is not upgraded.
  Historical traces keep a flag documented as "first-rung plus int only (pre-fix)", **or** a separate
  `ladder_check_version` distinguishes them. Adding a version field changes the trace contract
  (`model_schema/scoring.py:168`, `docs/contracts/schemas/scoring.schema.json:88`, regenerated from
  `model-schema`), which is a spec-first change; the plan chooses.
- **`LADDER_RECONCILIATION_FAILED`:** whether a failed reconciliation is refused (raising the registered
  code) or only recorded is the plan's decision point; this finding does not decide it. The stored flag
  must not read `true` for a ladder that has not been checked.
- **Data:** no stored trace anywhere reachable carries `false`, and all carry `true` in a test bucket, so
  nothing stored needs a correction record today. The historical-flag rule still binds the first
  production traces.

**Event that next confirms or discharges it:** WK-674 Slice 3 merges with a `reconcile_ladder` (or its
replacement) that takes the operations, is red first on an off-by-one-penny rung and green on a correct
ladder at both call sites, and with the historical-flag rule implemented as the plan states.

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it. The owner and
the medium severity are the maintainer's, per the entry quoted under *Severity*.

Ownership shape: event
