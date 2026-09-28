---
id: RS-WORKING
family: research
kind: spike
title: Does a persisted seed with a pinned hypothesis reproduce the same cases and the same shrunk counterexample across processes?
status: draft
created: 2026-09-28
owner: executor
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
work: WK-672
corrected_by: []
relates: [FR-261]
---

# RS-WORKING — hypothesis seed and shrink determinism across processes (spike F4)

Spike F4 of Track F, run 2026-09-28 by the executor `spike-f4`. The timebox started
at 11:36:28 BST. The measurement closed at 12:01:57 BST. **The verdict below is a
proposal. The deputy decides on this record** (the Decision section quotes that
decision).

## Question

FR-261 (`docs/specs/03-rating-engine.md` §3.8) says property assertions are
"evaluated over generated quote contexts" and that "Generation uses hypothesis-style
sampling over the input contract with a persisted seed". `hypothesis` is a dev-only
dependency at this tree: the root `pyproject.toml` `[dependency-groups] dev` lists
`hypothesis>=6`. Reading alone cannot tell whether a persisted seed reproduces the
generated cases, and the shrunk counterexample, in a fresh process. The deputy framed
the question twice; both entries are quoted verbatim from the lead's channel file
(`~/gi-pricing-plan.local/channel/to-lead.md`).

**The F4 item of the deputy's entry "2026-09-28 11:33:12 BST · deputy · THE OQ
STREAM":**

```text
## 2026-09-28 11:33:12 BST · deputy · THE OQ STREAM: 15 items that could block Phase 2, each RULED by delegation or sent to a spike. Two new tracks: E (file the decisions) and F (timeboxed spikes)
[…]
**F4 · WK-672 Slice 3 property assertions:** the **language is decided now as a structured union of FR-261's five classes** (declarative JSON artifacts, CLAUDE.md §2; no free-text expressions). The spike covers only **seed determinism**: does a persisted seed reproduce the same cases with a pinned generator? It also covers the dependency question: `hypothesis` is dev-only, so the choice is a runtime dependency or our own seeded numpy generator. Recommendation: our own generator, unless the spike shows otherwise. **F4 is on Track D's critical path, so run it first.**
```

**Item 3 of the deputy's entry of 2026-09-28 11:35:56 BST** (the pass condition; the
entry's heading is quoted in full at the top of the block):

```text
## 2026-09-28 11:35:56 BST · deputy · RL-1171: dm-d's reading of DP1 CONFIRMED; E1 in RL-1171's PR ACCEPTED; the `hypothesis` runtime dependency is made CONDITIONAL on spike F4; the assertion language stays the structured union
[…]
3. **`hypothesis` as a pricing-core runtime dependency (RL-1171 placement) is CONDITIONAL on spike F4.** F4 must show that a persisted seed with a pinned `hypothesis` version reproduces the same generated cases, and that shrinking yields the same minimal counterexample, across two processes. If F4 passes, S3 takes the dependency as RL-1171 says, and dm-d's shrinking argument for FR-261 is sound. If F4 fails, S3's leaf plan uses a seeded generator of our own and FR-261's "shrunk counterexample" clause is re-read at S3. **RL-1171 states that condition in its placement item.** It must not settle the dependency ahead of the measurement I ruled.
```

## Method

**Tree and environment.**
- **Tree:** a detached scratch worktree at `df8e5811a151a99c7317690faf9278a6dc3400be`
  (origin/main when the spike started), after `uv sync --all-packages`.
- **Pins, from that tree's `uv.lock`:** `hypothesis` 6.165.7, `numpy` 2.5.2, Python 3.12.
- **Host:** 16 CPUs, shared with other spikes and Track D.

**Input contract.** Seven `InputContractField` rows
(`packages/model-schema/src/model_schema/rating.py`) cover all six `RatingInputType`
values:
- `int` with `min`/`max`, twice, one of them `nullable`;
- `decimal` with `min`/`max` at 2 places;
- `enum` with a `domain`;
- `string` with a `pattern`;
- `date`;
- `bool`.

A generated context is one value per field. For hypothesis, the strategy is
`st.fixed_dictionaries` over one strategy per field, derived from the field
(`integers`, `decimals(places=2)`, `sampled_from`, `from_regex(fullmatch=True)`,
`dates`, `booleans`, and `none() |` for a nullable field).

**Property.** A toy Decimal premium function and a planted breach of FR-261's "premium
is bounded by declared limits" class (limit 900.00). The property fails for some
contexts, so every seed has a counterexample to shrink.

**What is compared.** Each process writes one canonical JSON log (`sort_keys`, compact
separators, Decimal and date as strings). The log holds:
- every context passed to the property, in call order, **including every call of the
  shrink phase**;
- then the final result (the counterexample, or `passed`).

The runner hashes each log with `sha256sum` and reports two counts per cell: the
distinct whole-log hashes (`distinct_logs`) and the distinct final records
(`distinct_final`). **A cell is deterministic only when `distinct_logs=1`.** A match on
the final counterexample alone is not evidence (result 3).

**Arms.**

| Arm | Settings |
|---|---|
| `numpy` | the baseline: `numpy.random.default_rng(seed)` per field in contract order, then a greedy deterministic shrink (per field, try the simplest value). The shrinker is a toy |
| `hyp_seed` | `@seed(s)`, `database=None`, `deadline=None`, `report_multiple_bugs=False`, `max_examples=200` |
| `hyp_derand` | as `hyp_seed` but `derandomize=True` and no `@seed` |
| `hyp_derand_seed` | `derandomize=True` and `@seed(s)` |
| `hyp_defaults` | `@seed(s)`, `max_examples=200`, every other setting at the hypothesis default |
| `hyp_pass` | as `hyp_seed` with a passing property: generation only, no shrink |
| `hyp_db_shared` | as `hyp_seed` with a `DirectoryBasedExampleDatabase` shared by the processes of the cell |
| `hyp_random` | **negative control:** as `hyp_seed` with no `@seed` and no `derandomize` |

**Replication.** Seeds 0, 1, 42, 20260928 and 987654321. Each (arm, seed) cell runs
in **3 fresh interpreter processes**, with `PYTHONHASHSEED` set to `0`, `1` and
`random`.

**Commands.** The spike code is `spike_f4/harness.py` and `spike_f4/run.sh` at the
salvage ref. From the scratch root:

```
bash spike_f4/run.sh                                                   # run 1
ARMS="hyp_random" SEEDS="0 1" bash spike_f4/run.sh                     # run 1 control
ARMS="numpy hyp_seed hyp_defaults hyp_db_shared hyp_random" taskset -c 8-15 bash spike_f4/run.sh   # run 2
uv run --frozen --with hypothesis==<v> python spike_f4/harness.py hyp_seed 42 <out>   # result 4, twice per version
```

## Findings

**1. The numpy baseline is deterministic.** Run 1, arm `numpy`: all 5 seeds gave
`distinct_logs=1` and `distinct_final=1` across 3 processes. The calls before shrinking
ended were 144, 39, 22, 13 and 95. Run 2 repeated this with the same counts.

**2. hypothesis is deterministic in cases AND in shrinking.**
- Run 1 covered all six hypothesis arms × 5 seeds = 30 cells. **Every cell gave
  `distinct_logs=1` and `distinct_final=1`.**
- The whole-log hash covers the shrink phase, so **the shrink sequences are
  byte-identical across processes**, not only the final counterexample.
- `hyp_seed` needed 390, 413, 420, 379 and 387 calls per seed. Run 2 reproduced these
  counts exactly.
- **`derandomize` ignores the seed.** `hyp_derand` produced the same log for every seed,
  385 calls each. Its randomness comes from the test function, not from a persisted
  seed, so it cannot carry FR-261's seed.
- **`@seed` wins over `derandomize`.** `hyp_derand_seed` matched `hyp_seed` seed for
  seed.
- **`@seed` disables the example database.** The `hyp_db_shared` directories held 0
  files after 15 runs, so no process replayed another's failure.
- Run 2 was under `taskset -c 8-15` and covered `numpy`, `hyp_seed`, `hyp_defaults` and
  `hyp_db_shared` × 5 seeds. All 20 cells gave `distinct_logs=1` and `distinct_final=1`.

**3. The negative control fails, so the comparator can fail.**
- **Run 1**, `hyp_random`, seeds 0 and 1: 3 distinct logs out of 3 processes each. The
  final counterexample still converged (`distinct_final=1`).
- **Run 2**, 5 seeds: `distinct_logs=3` in 5 of 5 cells. The counterexample also
  differed in 4 of 5 seeds (2, 2, 2 and 3 distinct values), and in one process the
  property passed without finding the breach.
- **Consequence:** an identical counterexample is not evidence of seeding, because the
  shrinker converges without it. Compare the whole log.

**4. A persisted seed is valid only at the pinned hypothesis version.**
- Seed 42, arm `hyp_seed`, 2 processes per version, through `uv run --frozen --with
  hypothesis==<v>`.
- 6.165.7 and 6.160.0 gave the same log hash (prefix `f042ce6c409a5be5`).
- 6.140.0 gave a different log (prefix `2991065dd6ff1f22`) **and a different
  counterexample**:
  - 6.140.0: `region` `N`, `vehicle_value` `68751.26`, 72 calls;
  - the pin: `region` `LDN`, `vehicle_value` `16827.89`, 420 calls.
- Within each version, the 2 processes agreed.
- **An upgrade changes the cases and the counterexample silently.**

**5. The engine has wall-clock cut-offs that this spike did not trigger.**
`hypothesis/internal/conjecture/engine.py` at 6.165.7 has three:
- `MAX_SHRINKING_SECONDS: int = 300` (line 95), enforced through
  `finish_shrinking_deadline` (lines 770 and 1689);
- a 10-second limit on the search for more bugs after the first one, when
  `report_multiple_bugs` is on (lines 1163–1167);
- the default `deadline` of 200 ms, which turns a slow example into a different error.

None fired here, because the toy property is fast. They were **not measured against a
real engine call** (see What remains).

**Load.**
- Run 1: the load average went from 1.89 at the start to 19.54. The high load came from
  other spikes' processes; this spike ran one process at a time.
- Run 2: pinned to cores 8–15, from 11:53:56 to 12:01:57 BST. The load was recorded per
  cell and fell from 12.35 to 3.34 (1-minute).

Determinism held across this whole range.

## Verdict (proposal)

**PASS at the pinned version; version-coupled.** At `hypothesis` 6.165.7, a persisted
seed applied with `@seed` reproduced the same generated cases and the same shrunk
counterexample across fresh processes, byte for byte:
- 5 seeds × 3 processes;
- 6 settings arms in run 1, and 3 hypothesis arms plus the numpy baseline in run 2;
- the negative control failing as it should.

The condition is met **only while the version is pinned**: at 6.140.0 the same seed
gives different cases and a different counterexample (result 4).

## Recommendation

`hypothesis` may be a `pricing-core` runtime dependency on these conditions:
- **An exact `==` pin.** At this tree it is `hypothesis>=6` in the dev group.
- **The hypothesis version is persisted beside the seed** on the run.
- **Fixed settings:** `@seed(persisted)`, `database=None`, `deadline=None`,
  `report_multiple_bugs=False`, and a bounded `max_examples`. `derandomize` is not used.
- **A replay refuses a version mismatch.**

The numpy baseline is also deterministic, but FR-261 needs a shrunk counterexample, and
the baseline's shrinker is a toy that would have to be built and maintained.

## Decision

Quoted verbatim, attributed: the deputy's entry in `~/gi-pricing-plan.local/channel/to-lead.md`
headed "2026-09-28 11:54:48 BST · deputy · Spike F4 DECIDED", given by the maintainer's
delegation.

```text
## 2026-09-28 11:54:48 BST · deputy · Spike F4 DECIDED: `hypothesis` becomes a `pricing-core` runtime dependency under six conditions; the generated cases are persisted, so an old run's replay never depends on the library version (answers your 11:54:10)

Given by the maintainer's delegation (28 Sep). It is final on the RS record once I read it there with these figures; the decision line goes into the record, quoted and attributed. **Slice 3's leaf plan builds on it from now.**

**Why hypothesis, and not the platform's own generator (this reverses my 11:33:12 recommendation, as that line allowed):**
- FR-261 requires a *shrunk* counterexample. numpy's `default_rng` is seed-stable but has no shrinker, and building one is a slice of its own with no track record.
- F4 showed seed **and** shrink determinism. There was 1 distinct call log and 1 counterexample per seed, over 5 seeds × 3 fresh interpreters × 6 settings arms, and the shrink sequences were byte-identical.
- The negative control produced 3 distinct logs, so the comparator can fail.
- Determinism held with load between 1.9 and 19.5, so contention does not break it at this scale.

**The conditions. Each is a Slice 3 requirement, and each is written into RL-1172's placement item by a dated line at S3's leaf plan:**
1. **An exact `==` pin** in `packages/pricing-core/pyproject.toml` (currently `hypothesis>=6`, dev group only). `03` §8 and `docs/skills-map.md` are updated in the same PR (CLAUDE.md §10).
2. **The settings are fixed in code, not left at the defaults:** `@seed(persisted)`, `database=None`, `deadline=None`, `report_multiple_bugs=False`, and a bounded `max_examples` declared on the `RegressionSuite` artifact. `derandomize` is not used, because it ignores the seed.
3. **The hypothesis version is persisted beside `generation.seed`** on the run. **Regenerating** from a seed refuses a version mismatch, by name.
4. **Every generated case and the shrunk counterexample are persisted on the `RegressionRun`**, as a content-addressed JSON blob of canonical cases, the same form the spike hashed. **Replaying a past run re-scores these persisted cases and never regenerates them.** The seed serves same-version regeneration and debugging. Audit reproducibility rests on the cases, so an upgrade of hypothesis cannot invalidate a Rating Version's regression history. If FR-261's wording names the seed as the reproduction mechanism, this is a dated amendment in S3's spec change.
5. **Wall-clock cut-offs are detected, not assumed away.** The spike did not measure them (`engine.py` at 6.165.7: `MAX_SHRINKING_SECONDS`, and the multi-bug search that condition 2 disables). S3 records on the run whether shrinking completed or stopped on a limit. A stopped shrink reports its counterexample as **unminimised**, never as the minimal one. The S3 leaf plan names the mechanism, verified at the pin (read to the function body, not the constant).
6. **The spike's matrix becomes S3's test:** two fresh processes, seeds from the persisted artifact, identical canonical case logs and counterexamples, plus the no-seed negative control. It is a CI test, so a hypothesis upgrade that breaks determinism fails the gate rather than the audit record.

`pricing-core` stays standalone: hypothesis pulls no FastAPI, SQLAlchemy or Redis. S3's PR shows the resolved dependency set, and `lint-imports` stays green. **F4 is off Track D's critical path.** Re-derive the ETA for S3 on this decision. Push the salvage ref `d0f432c5` with the others.
```

Two notes on the quoted text, recorded and not resolved here:
- **The ruling's id.** The 11:35:56 entry names the WK-672 opening ruling by the id it
  held before minting. The decision names it by the id it carries in the open PR #829
  (branch `p2-d-rl`), filed there as the WK-672 opening rulings. It is one ruling, not
  two.
- **Where the pin is.** Condition 1 says the pin is in
  `packages/pricing-core/pyproject.toml`. At this record's `tree:`, that file does not
  name `hypothesis`. The `hypothesis>=6` pin is in the root `pyproject.toml`'s
  `[dependency-groups] dev`.

## What remains

- **The wall-clock cut-offs of result 5 are unmeasured against a real engine call.** A
  property that calls the ZEN engine under load could hit the shrink cap, or, with the
  defaults, the deadline or the multi-bug search. It could then stop at a different
  point in two processes. Not measured: the spike's property is a toy Decimal function.
  Condition 5 of the decision assigns detection to S3.
- **Version sensitivity was sampled, not swept.** Three versions (6.140.0, 6.160.0 and
  6.165.7), one seed, one arm.
- **One contract shape.** Seven fields, one pattern and one domain.
- **The numpy baseline's shrinker is a toy.** Its determinism shows the stream is
  stable, not that a production shrinker is feasible.

## Salvage

The spike code and its outputs are at `refs/salvage/2026-09-28/spike-f4`, three commits
in a line:
- `d0f432c5bd3c6a406e998701c493a3c24cb6ad67` holds `spike_f4/harness.py` (all eight
  arms, including `hyp_random`), `spike_f4/run.sh` and run 1's table
  (`spike_f4/run1.txt`, 35 cells). It was pushed to origin by the lead. **Run 1's
  two-seed negative-control output was read from the terminal and not saved**; run 2's
  five-seed control is saved.
- `b370c2b3` adds the per-cell time and load stamp to `run.sh`, and run 2's table
  (`spike_f4/run2.txt`, 25 cells).
- `8596edc61a1656a2e24979387666a13ce6b20734` adds result 4's six output logs
  (`spike_f4/vers/`). The local ref points here, and it still needs to be pushed.
