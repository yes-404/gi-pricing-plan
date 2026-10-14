---
id: RL-1685
family: ruling
title: PL-1454 DP-1 to DP-4 — one read session per /score request and last_used_at written at most once a minute; no new cache; a replica is N worker processes (a spec clarification); the stall is gen2 GC, gc.freeze() after startup
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-12
owner: decision-maker
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-1178
slice: SL-1455
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1454, SL-1455, FD-1411, NFR-489, NFR-454, NFR-497, FR-259, FR-452, RL-921, RL-924, RL-1379, RL-1263]   # and LG working id 9932, added at its mint
---

# RL-1685 — PL-1454 DP-1 to DP-4, ruled from SL-1455 Task 0's record

*(Minted 2026-10-12 as RL-1685 from working id 9800, which the lead reserved in eta at 2026-10-12
02:22:40 BST. Every "RL 9800" in a quoted entry below is this ruling's working id; in the T-text
it reads RL-1685. "LG 9932" stays SL-1455's ledger by its working id, which is not minted here.)*

## How this was ruled

- **The order.** `~/gi-pricing-plan.local/channel/to-lead.md` (a local file, cited by entry
  header), the maintainer's (by delegation) entry *"2026-10-12 02:22:06 BST — SL-1455: Task 0 is
  COMPLETE once LG 9932 records the rerun; the next step is NOT the sweep but the
  decision-maker's DP-1..DP-4 ruling (PL-1454 :62-68, :106, :331)"*: *"Per PL-1454: Stage 1 =
  Task 0 → the decision-maker rules DP-1 to DP-4 FROM THE RECORD → that ruling merged + your go →
  Tasks 1–3 (the fix) → the acceptance sweep."* The same entry gives four points to weigh, *"for
  the decision-maker to rule, not my ruling"*; each is answered under its DP below.
- **The decision points are PL-1454's**, `docs/plans/PL-01454-…-leaf-plan.md` at this record's
  tree: the table at `:335-342`, whose preamble (`:331-333`) makes DP-1 to DP-4 the
  decision-maker's, *"ruled from Task 0's record"*, with recommendations *"conditional on Task 0
  confirming what reading suggests"*. Activation need 5 (`:106`): Tasks 1 to 6 wait on this
  ruling, merged, and the lead's go. The plan is frozen and is not edited (`document-ids.md`
  §1.6, PL row: *"decision-maker rules decision points as `RL-`, never edits the plan"*).
- **Two questions outside the plan's options went to the lead before ruling** (the seat's
  brief, item 3: *"any option the plan does not list: STOP and ask me"*): the value of N under
  DP-3 (b), and whether DP-1 (a)'s one read session also takes the two Setting reads the plan's
  table predates. **Both were ruled as this seat proposed** by the maintainer (by delegation),
  to-lead *"2026-10-12 07:44:13 BST — Three dropped decision-maker hand-offs: (1) RL 9852 = (A),
  with 3 conditions; (2) RL 9800's Q1 (i) and Q2 (A) RULED as the decision-maker proposed; (3)
  RL 9876 ACKED"*, item (2), verbatim:
  *"- Q1 (i): ACCEPTED. One read session also takes FR-452's scoring-limit Setting and FR-259's
  sampling-rate Setting, giving MAX_CHECKOUTS=1 and MAX_STATEMENTS=9.
  - Q2 (A): ACCEPTED as a spec CLARIFICATION, by ruling text. A replica = N uvicorn worker
  processes, one per dedicated vCPU. N is stated with every NFR-489/454 reading; N=4 on the
  shared VM is diagnostic only, and the reference N is fixed with G4's dedicated host.
  - Condition: the clarification lands as a dated line on NFR-489 and NFR-454 IN RL 9800's mint
  (the spec-change skill), and every bench output prints N in its header, so a reading without
  N cannot exist.
  - I also want the record to show the arithmetic that made (b) necessary: score_one's mean,
  × 200, against 1 s."*
  The lead relayed it in from-lead *"2026-10-12 07:44:36 BST"* (`from-lead-2026-10-09.md:2780`).
  The entry's labels are the reverse of this seat's: its Q1 is the membership question (option
  (i)) and its Q2 is N's (option (A)). The options are unambiguous, so the labels change
  nothing. The three conditions are met here: the dated lines are T2 and T3, applied in this
  record; the bench header is under **What it obliges**; the arithmetic is under DP-3.
- **The seat ran at high effort, verified.** The maintainer raised it, to-lead *"2026-10-12
  02:24:20 BST — RAISE: dm-pl1454 runs at HIGH for RL 9800; respawn before it drafts"* (it picks
  FD-1411's remedy; DP-1 (c) can change who may score; DP-2 weighs caches against RL-921 and a
  revoked-key window; DP-3 may raise a spec clarification). Two seats spawned through the Agent
  tool ran at medium (transcripts `92d4dee8` and `7efcf3a0`, `perTurnEffort` medium), so the
  maintainer chose a separate process, to-lead *"2026-10-12 02:26:23 BST — RL 9800 effort: (e)
  with ONE named route: a separate CLI process with --effort high, verified by the transcript
  field; else fall back to (c)"*. The lead's verification, from-lead *"2026-10-12 02:27:34 BST"*:
  (1) the process command line shows `--model opus --effort high --name dm-pl1454`; (2) the
  seat's transcript `b7174439-2c46-4832-bf71-624d5ea6d69b.jsonl` reads `"effort":"high"` ×13 and
  `"perTurnEffort":"high"` ×13, `requestedModel` `claude-opus-5-5`. This seat re-read both
  itself: `ps -o pid,ppid,args -p $PPID` shows PID 657803, `claude --model opus --effort high --name dm-pl1454 …`;
  `grep -oE '"(effort|perTurnEffort|requestedEffort|requestedModel)":"[^"]*"' <transcript> |
  sort | uniq -c` gave `"effort":"high"` 19, `"perTurnEffort":"high"` 19,
  `"requestedModel":"claude-opus-5-5"` 19, read on 2026-10-12 between this seat's clock reads
  of 02:27:04 and 02:34:59 BST.

## The record — read for this ruling

- **LG 9932** (SL-1455's ledger, under `docs/ledgers/` on the slice branch) at the slice head
  `origin/sl-1455-wk1178-nfr489-http` = `51cc9b13ee46498dea2676c38bd2d0c89ef1fd04`: run 1
  (asyncio debug ON, 2026-10-11 23:41:11 – 2026-10-12 00:14:49 BST), whose p50/p99 are void as a
  stall diagnosis and whose structural facts stand (to-lead *"2026-10-12 00:16:39 BST"*); the
  rerun's pre-registration; and the debug-OFF rerun, 2026-10-12 02:16:09 – 02:20:29 BST, both
  arms CLEAN by the pre-registered rule (from-lead *"2026-10-12 02:21:18 BST"*, lead-verified).
- **The rerun's results**, `~/gi-pricing-plan.local/scratch/sl1455-t0/out-20261012T021609/`
  (local; not in the repository): `results.md`, sha256
  `a88faec653f46e49bbef6a234ef72608e64e1ca4d20ee673f5c37d5f3f92e338`, generated by
  `t0_analyse.py` blob `2d2d0f44` (byte-identical to the pre-registered evidence commit
  `3200b5a507d28c13dfd04bbb449df4205c200f7d`, `evidence/sl-1455-t0/t0_analyse.py`; checked with
  `git hash-object` and `git rev-parse 3200b5a5:evidence/sl-1455-t0/t0_analyse.py`). The raw
  files every number below is computed from are the six measured passes' `client.json`,
  `requests.jsonl` and `events.jsonl` (18 files); their manifest digest is
  `ebc4a39a0d2a19d1489320ce754c93dd0a1b2670e50dd0541e2a1b644bd73772`, by
  `O=<that dir>; sha256sum $(ls -d $O/bench-*/r25-run*/{client.json,requests.jsonl,events.jsonl} | sort) | sed "s#$O/##" | sha256sum`.
- **The selection rule is the analyser's own** (`t0_analyse.py` `load_pass`): a request counts
  when `t >= client["measure_from"]` and `status == 200`. The medians the commands below print
  reproduce `results.md`'s p50 column (`score_one` 13.16 and 7.94 ms, `:36` and `:110`), so the
  selection is the same.
- **Code** is cited at this record's tree, `origin/main` `fc4401dc`. Task 0 measured `372fa92a`.
  `git diff --name-only 372fa92a fc4401dc` over the cited files lists
  `backend/src/app/api/score.py` (the 200 response documented through `responses=`, #1282; lines
  shift by 2), `packages/pricing-core/src/pricing_core/rating/score.py` (SL-1566, #1286; every
  hunk lies after `score_one`'s body, `:920-979`) and `docs/specs/03-rating-engine.md`; none
  changes what is counted or ruled here.

## Ruled

1. **DP-1 = (a) + (b).** Membership option (i), accepted in the 07:44:13 entry.
   - **(a)** One request-scoped session serves every READ a quoted request makes: the API-key
     authentication, the permission check, FR-452's scoring-limit Setting, the live Deployment,
     the version row, and FR-259's sampling-rate Setting. A warm, quoted, unsampled request takes
     **one** pool checkout. Only a sampled outcome opens the sampling WRITE's own
     `unit_of_work` (PL-1454 Task 3 Step 1, FR-259's failure isolation).
     **Binding condition:** a failure of the sampling-rate read still degrades to "not sampled,
     logged" and never fails the quote. `test_a_trace_sampling_failure_does_not_turn_the_response_into_a_500`
     (`backend/tests/test_score.py:1021`) stays green unchanged, and a red-first test injects
     the failure at the read in its new place.
   - **(b)** `last_used_at` is written only when it is `None` or older than **60 seconds**
     (`backend/src/app/auth/service.py:238`).
   - **(c) is not admitted.** **(d) is not admitted** on this record; it may be raised again
     only from Task 4's own pool-wait figures. **(e) is rejected** as inert.
   - **Task 2's bounds** (PL-1454 `:453-480`, *"the values DP-1's ruling fixes"*), for a warm,
     quoted request with `rating.trace_sample_rate` pinned at 0, as
     `test_a_quoted_outcome_at_rate_zero_persists_no_trace` (`test_score.py:913`) pins it:
     `MAX_CHECKOUTS = 1`, and `MAX_STATEMENTS = 9`, which is the record's 10 per request with
     the per-request `UPDATE` removed. (a) removes checkouts, pre-pings and commits; it removes
     no statement.
2. **DP-2 = (a): no new cross-request cache.** RL-921 stands, and so does F50's lesson.
3. **DP-3 = (b), as a spec clarification:** one process cannot serve 200 rps by arithmetic.
   N's form is option (A), accepted in the 07:44:13 entry. A **replica** is one serving
   instance running N `uvicorn` worker processes, one per dedicated vCPU. N is stated with every
   NFR-489 or NFR-454 reading, and the budget is read per replica at that N. On the shared VM,
   Task 4's sweep runs **N = 4**, with `bench-rating.py --workers 4` (PL-1454 Task 1 Step 3);
   a reading at N = 4 there is diagnostic only. Every bench output prints N in its header.
   The reference N for the verdict is fixed when G4's dedicated host is available. The spec
   text is T1 to T3 below.
4. **DP-4 = (a): GC, by `gc.freeze()` after startup**, at the end of `create_app`'s lifespan
   start-up (`backend/src/app/main.py:83`). The ~200–300 ms stall is **reproduced and
   attributed**, but outside the measured windows. It is neither "not reproduced" nor (d)
   "unattributed".
5. **DP-5 is not raised.** The shared VM's verdict is carried to the dedicated host under G4,
   which waits on the user's spend approval (the 02:22:06 entry, point 4).
6. **DP-6 stays ruled (b)** by the maintainer (by delegation): PL-1454 `:341`, to-lead
   *"2026-10-05 09:59:49 BST"*.

## Why — each DP from the record

### DP-1: the read path's checkouts and the UPDATE dominate, and they do not depend on the GBM

The maintainer's point 1: *"The gap remains with the stall gone: 25 rps p99 is 140–148 ms (gbm)
and 109–131 ms (nogbm), against budgets of 50 / 15 ms … DP-1's checkout consolidation is the
visible lever (6 checkouts, 10 statements, 2 commits per request)."* The record confirms the
condition PL-1454 attached to (a) + (b), *"if Task 0 shows checkouts and the UPDATE dominate"*:

```
python3 -I - <<'EOF' ~/gi-pricing-plan.local/scratch/sl1455-t0/out-20261012T021609
import json, statistics, sys
from pathlib import Path
LEAVES = ["auth_scope", "rbac_scope", "rate_limit", "serving_ref", "compiled_for", "score_one", "sample_trace", "serialise"]
root = Path(sys.argv[1])
for arm in ("bench-gbm", "bench-nogbm"):
    reqs = []
    for run in ("r25-run1", "r25-run2", "r25-run3"):
        d = root / arm / run
        start = json.loads((d / "client.json").read_text())["measure_from"]
        reqs += [r for r in map(json.loads, (d / "requests.jsonl").read_text().splitlines())
                 if r["t"] >= start and r.get("status") == 200]
    mean = lambda k: statistics.fmean(r["phases"][k] for r in reqs)
    un = statistics.fmean(r["phases"]["total"] - sum(r["phases"][k] for k in LEAVES) for r in reqs)
    db = statistics.fmean(sum(r["phases"][k] for k in LEAVES[:5]) + r["phases"]["sample_trace"] for r in reqs)
    print(arm, f"n={len(reqs)}", " ".join(f"{k}={mean(k):.2f}" for k in ["total"] + LEAVES),
          f"unaccounted={un:.2f} db_phases={db:.2f}")
EOF
```

prints (`LEAVES` is `t0_analyse.py`'s own list of disjoint phases):

```
bench-gbm n=1500 total=91.24 auth_scope=14.38 rbac_scope=8.25 rate_limit=11.31 serving_ref=9.59 compiled_for=8.56 score_one=14.18 sample_trace=12.34 serialise=0.08 unaccounted=12.53 db_phases=64.44
bench-nogbm n=1500 total=81.01 auth_scope=13.79 rbac_scope=7.97 rate_limit=10.70 serving_ref=9.01 compiled_for=8.49 score_one=8.27 sample_trace=11.53 serialise=0.08 unaccounted=11.17 db_phases=61.49
```

- **The six DB-bound phases are 64.44 of 91.24 ms (70.6 %) with the GBM and 61.49 of 81.01 ms
  (75.9 %) without**, and they are the same within 3 ms across the two arms: the cost is the
  request shape, not the model. Every request takes 6 checkouts, 10 statements and 2 commits
  at p50 (`results.md:40`, `:114`; run 1 agrees, LG 9932). The checkouts are 6, not the plan's
  5, because FR-452's scoring limit (#1280) resolves a Setting in its own session on every
  request.
- **Authentication is the largest DB phase**, `auth_scope` 14.38 / 13.79 ms (p50 13.94 / 13.51,
  `results.md:29`, `:103`). It carries three statements, the `UPDATE` of one shared
  `api_keys` row (`auth/service.py:238`) and a commit. (b) removes the write. (a) removes the
  commit and four checkouts with their pre-pings.
- **Why (a) is widened to the two Setting reads** (option (i), accepted 07:44:13): `rate_limit` (11.31 / 10.70
  ms) and `sample_trace` (12.34 / 11.53 ms) are each as large as authentication. On an unsampled
  request each is one Setting read with its own checkout, pre-ping and commit
  (`_maybe_sample_trace`, `backend/src/app/api/score.py:509`, awaited at `:429`). Reading them
  in the shared session costs no staleness and adds no cache, so DP-2 can stay (a). The write
  keeps its own `unit_of_work`, which is all Task 3 Step 1 isolates.
- **(b)'s 60 s.** `last_used_at` has one reader: the admin view's "last used" column
  (`docs/specs/07-platform.md:408`; `backend/src/app/api/service_accounts.py:147`). No spec
  gives it a precision finer than that.
- **(c) is not admitted.** Under (a) the role query costs no checkout of its own; it is one
  statement inside `rbac_scope`'s 8 ms. Skipping it relies on `effective_permissions` being
  exactly the union RL-924 taught it. That is an authorisation semantic PL-1454 already marks
  *"needs RL-924's reading confirmed (it may change who may score)"*, and a latency record
  cannot confirm it.
- **(d) is not admitted.** PL-1454 admits it *"only with a measured pool-wait figure"*. The
  record measures none: the longest single checkout, pre-ping included, is 12.57 / 17.34 ms
  (`results.md:40`, `:114`), and 0 new connections opened in the window (`:46`, `:120`). Pool
  sizing at 200 rps is Task 4's to observe, not this record's to infer.
- **(e) is rejected as inert.** Its saving needs a roll that *"exceeds the setting's maximum"*.
  `rating.trace_sample_rate` is constrained to max 1.0
  (`backend/src/app/platform/settings.py:229`), and `decide_sampling`'s roll is drawn from
  [0.0, 1.0) (`backend/src/app/platform/traces.py:78`, its docstring), so no roll ever exceeds
  it. (a) takes the read's cost instead.

### DP-2: no cache; the gap the caches could close is not the gap that remains

PL-1454 recommends (a) and says to *"revisit only if (a) misses the budget with Task 0's
numbers"*. By the record, (a) + (b) does not close the budget, and neither would any cache:

- **Without the GBM, the non-DB time alone exceeds the budget.** `score_one` 8.27 ms mean
  (p99 14.53, `results.md:110`) plus `unaccounted` 11.17 ms mean is about 19 ms against a 15 ms
  p99. No cache touches either.
- **The caches on offer trade security for one statement each.** A cached credential lets a
  revoked key score for the TTL; a cached permission lets a removed permission score (PL-1454
  `:338`). (c), the happy-path ref → hash memo for non-draft refs, saves one indexed read
  (`compiled_for` 8.56 / 8.49 ms, which also holds the slot lookup) and contradicts RL-921 and
  F50's lesson. Under DP-1 (a) that read no longer costs a checkout of its own.
- **The two Setting reads, the only low-risk candidates for (b)'s TTL, are already removed** by
  DP-1 (a) as widened, without a staleness window. *[If the lead answers (ii), this point is
  re-ruled: DP-2 (b) for `rating.trace_sample_rate` alone would then be the lever on it.]*

So a cache would add a staleness window to save milliseconds, while the remaining gap is CPU
on the event loop (DP-3) and the shared machine (G4, DP-5 not raised).

### DP-3: one event loop cannot carry 200 rps of `score_one`

The maintainer's point 2: *"At 200 rps, one event loop needs score_one's MEAN × 200 ≤ 1 s of CPU
per second. Ask for the mean from the record. If mean × 200 > ~0.7 s, one process cannot reach
200 rps by arithmetic, and DP-3 (b) must be raised as a spec clarification (never a silent
harness change, PL :339)."*

```
python3 -I - <<'EOF' ~/gi-pricing-plan.local/scratch/sl1455-t0/out-20261012T021609
import json, statistics, sys
from pathlib import Path
root = Path(sys.argv[1])
for arm in ("bench-gbm", "bench-nogbm"):
    xs, tot = [], []
    for run in ("r25-run1", "r25-run2", "r25-run3"):
        d = root / arm / run
        start = json.loads((d / "client.json").read_text())["measure_from"]
        for line in (d / "requests.jsonl").read_text().splitlines():
            r = json.loads(line)
            if r["t"] >= start and r.get("status") == 200:
                xs.append(r["phases"]["score_one"]); tot.append(r["phases"]["total"])
    m = statistics.fmean(xs)
    print(f"{arm}: n={len(xs)} score_one mean={m:.2f} ms median={statistics.median(xs):.2f} "
          f"mean*200={m*200/1000:.3f} s/s; total mean={statistics.fmean(tot):.2f} ms")
EOF
```

prints:

```
bench-gbm: n=1500 score_one mean=14.18 ms median=13.16 mean*200=2.837 s/s; total mean=91.24 ms
bench-nogbm: n=1500 score_one mean=8.27 ms median=7.94 mean*200=1.654 s/s; total mean=81.01 ms
```

- **2.837 and 1.654 seconds of `score_one` per second at 200 rps**, against the maintainer's
  ~0.7 s line and the hard 1 s ceiling of one event loop. The arithmetic, as the 07:44:13
  entry asks: 14.18 ms × 200 = 2.837 s per second (gbm) and 8.27 ms × 200 = 1.654 s per second
  (nogbm), each against the 1 s one process has in a second. Both exceed it, so one process
  cannot serve 200 rps, and (b) is necessary.
- **This mean is an upper bound on `score_one`'s CPU, and the conclusion holds below it.** The
  phase is wall time across `await bundle.decision.async_evaluate(...)`
  (`packages/pricing-core/src/pricing_core/rating/score.py:962`), so it can include other
  requests' turns on the loop. PL-1454's own sequential component figure, `score_one`'s *"5 to 8
  ms p50"* (`:251`), still gives 1.0 to 1.6 s per second at 200 rps. The plan saw the same
  thing at `:250-252`: *"At 200 rps on one process the mean must fall to about 10 ms"* for the
  whole request.
- **`score_one` is not the whole of the loop's CPU.** Authentication, the permission check, the
  ORM, Pydantic and the response run on the same loop. DP-1 shortens their I/O waits but not
  their Python. Whole-request CPU is not in the record, so the record bounds N from below and
  does not size it: N ≥ 3 for `score_one` alone at 100 % of a core, N ≥ 5 at 70 %.
- **"Per replica" is defined nowhere in the specs.** `git grep -n -i -E '\breplica'
  origin/main -- docs/specs docs/adr` at `fc4401dc` finds NFR-454 (`00:543`), NFR-489
  (`03:1504`) and three monitoring uses in `05`, but no definition. PL-1454 `:339` makes (a) the
  harness's habit, not a spec reading. So the choice is a clarification, written as spec text
  (T1 to T3), and never a silent `--workers` flag.
- **Why N is stated rather than open** (option (A), accepted 07:44:13): an N left "as deployed"
  passes at any N, so the requirement could not fail. **4 on the shared VM** leaves 4 of the
  e2-standard-8's vCPUs to the co-hosted PostgreSQL, Redis and MinIO that every request also
  uses. The reference N waits for the dedicated host, where G4 already carries the verdict.
  Fixing it now would put a sizing number into a platform NFR with no whole-request CPU figure
  behind it.

### DP-4: the stall is a gen2 collection, seen in every process but outside the measured windows

The maintainer's point 3: *"with debug off, loop stalls ≥50 ms = 0. The decision-maker decides
whether the ~200–300 ms stall the plan names still exists. (d) "unattributed: STOP" is not the
same as "not reproduced"; the ruling says which."*

`results.md` is true as written: loop stalls ≥ 50 ms in the measured windows are 0 (`:46`,
`:120`). It also prints *"GC gen2: 3 collections, longest 369.24 ms"* and *"… 360.00 ms"* (`:45`,
`:119`) for the same windows. Those two lines cannot both describe pauses inside the
requests, so the raw events were read:

```
python3 -I - <<'EOF' ~/gi-pricing-plan.local/scratch/sl1455-t0/out-20261012T021609
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
for d in sorted(root.glob("bench-*/r25-run*")):
    m = json.loads((d / "client.json").read_text())["measure_from"]
    ev = [json.loads(x) for x in (d / "events.jsonl").read_text().splitlines()]
    rq = [json.loads(x) for x in (d / "requests.jsonl").read_text().splitlines()]
    last = max(r["t"] for r in rq) - m
    g2 = [(e["t"] - m, e["ms"], sum(r["t"] - r["phases"]["total"] / 1000 <= e["t"] <= r["t"] for r in rq if r["t"] >= m))
          for e in ev if e["kind"] == "gc" and e["generation"] == 2]
    st = [(e["t"] - m, e["late_ms"]) for e in ev if e["kind"] == "loop_stall"]
    print(f"{d.parent.name}/{d.name}: last request +{last:.2f} s;",
          "gen2 " + ", ".join(f"{t:+.2f} s {ms:.0f} ms ({n} measured req overlap)" for t, ms, n in g2) + ";",
          "stalls " + ", ".join(f"{t:+.2f} s {ms:.0f} ms" for t, ms in st))
EOF
```

prints (times relative to `measure_from`; a `gc` event is stamped when the collection ends, a
`loop_stall` when the late tick fires):

```
bench-gbm/r25-run1: last request +19.97 s; gen2 -4.63 s 260 ms (0 measured req overlap), -2.54 s 303 ms (0 measured req overlap), +20.63 s 369 ms (0 measured req overlap); stalls -4.23 s 800 ms, -2.31 s 881 ms
bench-gbm/r25-run2: last request +19.97 s; gen2 -5.03 s 295 ms (0 measured req overlap), -2.59 s 333 ms (0 measured req overlap), +20.60 s 340 ms (0 measured req overlap); stalls -4.40 s 1068 ms, -3.99 s 50 ms, -2.34 s 953 ms
bench-gbm/r25-run3: last request +19.97 s; gen2 -4.70 s 269 ms (0 measured req overlap), -2.66 s 317 ms (0 measured req overlap), +20.55 s 360 ms (0 measured req overlap); stalls -4.27 s 861 ms, -2.40 s 911 ms
bench-nogbm/r25-run1: last request +19.97 s; gen2 -3.88 s 270 ms (0 measured req overlap), +20.54 s 302 ms (0 measured req overlap); stalls -3.44 s 840 ms
bench-nogbm/r25-run2: last request +19.98 s; gen2 -3.65 s 247 ms (0 measured req overlap), +20.53 s 315 ms (0 measured req overlap); stalls -3.21 s 825 ms
bench-nogbm/r25-run3: last request +19.97 s; gen2 -3.68 s 262 ms (0 measured req overlap), +20.60 s 360 ms (0 measured req overlap); stalls -3.26 s 810 ms
```

- **Every server process, in both arms, ran a gen2 collection of 247–369 ms**: the plan's
  ~200–300 ms band, debug mode off. The pause is timed by `gc.callbacks`, so it is the
  collector's own duration, and a collection holds the GIL, so the loop cannot run during it.
- **None overlapped a measured request.** One or two fell in the discarded 4 s warm-up
  (`t0_driver.py` `one_pass`), and every one of those lies inside a ticker stall of 800–1068 ms.
  For example, run 1's stall at −2.31 s, 881 ms late, spans −3.19 to −2.31 s and contains the
  303 ms collection that ended at −2.54 s. The rest of each warm-up stall is not attributed by
  the record. One more fell 0.53–0.63 s after the last measured request, as the client stopped
  and the driver signalled the server (`t0_driver.py` `stop_server`). That is why the analyser
  counts it in the window while no request saw it.
- **Hence "reproduced, attributed, outside the windows".** "Not reproduced" would deny pauses
  the record shows in all six processes. (d) "unattributed" would deny that `gc.callbacks`
  timed them. The 20 s measured windows sat between two collections because Task 0 started a
  fresh server for every pass (`t0_driver.py` `one_pass`), so each process's first collections
  fell in its warm-up. FD-1411's harness served every rung of an arm from one server
  (PL-1454 `:219`, *"each arm has its own server"*), so its collections could fall inside a
  measured rung. That is where FD-1411 saw its in-handler tail: *"handler p99 320.4 ms and queue
  plus loopback only 3.2 ms"* (FD-1411 `:132-134`), inside this record's 247–369 ms band. How
  often a collection recurs under sustained load, at 200 rps, is not in the record.
- **Why (a) is `gc.freeze()` after startup and not raised thresholds.** The warm-up
  collections freed 0 to 62 objects and still took 247–333 ms, which is the cost of traversing
  the long-lived start-up heap, not of garbage. `gc.freeze()` moves that heap out of every later
  collection. Raised thresholds would make collections rarer but no shorter. (b) is excluded:
  no measured pool wait and no new connection in the windows (DP-1). (c) is excluded: the
  rerun's sampling profile names no blocking I/O call among its top frames, only start-up import
  work (`_compile_bytecode`; LG 9932, the rerun's `py-spy` entry). And every loop block of
  200 ms or more the ticker saw contains a timed gen2 collection, 9 of 9:

  ```
  python3 -I - <<'EOF' ~/gi-pricing-plan.local/scratch/sl1455-t0/out-20261012T021609
  import json, sys
  from pathlib import Path
  for d in sorted(Path(sys.argv[1]).glob("bench-*/r25-run*")):
      ev = [json.loads(x) for x in (d / "events.jsonl").read_text().splitlines()]
      gcs = [(e["t"] - e["ms"] / 1000, e["t"]) for e in ev if e["kind"] == "gc" and e["generation"] == 2]
      for e in ev:
          if e["kind"] == "loop_stall" and e["late_ms"] >= 200:
              s0, s1 = e["t"] - e["late_ms"] / 1000, e["t"]
              print(d.parent.name, d.name, round(e["late_ms"]), any(s0 <= a and b <= s1 for a, b in gcs))
  EOF
  ```

  prints nine lines, each ending `True` (800, 881, 1068, 953, 861, 911, 840, 825, 810 ms).
- **The falsifier.** If Task 4's un-instrumented sweep still shows in-handler outliers of
  200 ms or more at any rate, the cause is not this one. DP-4 then reopens as (d), and Task 4
  Step 3's stop-and-report applies.

## What it does not change

- **RL-921**, F50's lesson, **RL-882 clause 4**, NFR-497's degraded read, FR-259's rates and its
  off-path trace production, `async def` on the handler, and "no new runtime dependency" — every
  PL-1454 Global Constraint (`:173-191`).
- **The pre-registered reading** of LG 9932's rerun (*"both arms CLEAN = debug mode was the
  stall"*). That rule is about the 20–60 s pool saturation of run 1, and it stands. The gen2
  pauses are a separate ~300 ms mechanism, read from the same record's raw events and not
  reinterpreted from the rule.
- **NFR-489's and NFR-454's budgets**: 50 ms and 15 ms, 200 rps. T1 to T3 define the unit, not
  the numbers.
- **DP-6 (b)**, its binding condition and Hand-off item 4.

## The spec text

Three edits, applied in this record's commit (see **Applying**). Each find string is counted
with `grep -cF` = 1 at `fc4401dc`; the replace strings are 0 there.

### T1 — `00-overview.md` §2.3, a glossary row after **Scoring**

`CLAUDE.md` §7 and `00` §2: *"A new term must be added here before it is used in any other
document."* "Replica" is already used undefined (NFR-454, NFR-489, `05` FR-333).

Find:

```
| **Scoring** | Evaluating a Rating Version for one or more risks. **Real-time** (single quote, target p99 < 50 ms) or **batch** (portfolio re-rate). |
```

Replace:

```
| **Scoring** | Evaluating a Rating Version for one or more risks. **Real-time** (single quote, target p99 < 50 ms) or **batch** (portfolio re-rate). |
| **Replica** | One serving instance of the scoring API: N `uvicorn` worker processes, one per dedicated vCPU, behind one listening address. Real-time scoring's throughput budgets are per replica, and N is stated with every reading of them. *(Added 2026-10-12, RL-1685, PL-1454 DP-3 (b).)* |
```

### T2 — `00-overview.md` NFR-454

Find:

```
| **NFR-454** | Real-time scoring: p99 < 50 ms server-side for a single quote against a live Rating Version, excluding network, at 200 rps sustained per replica. |
```

Replace:

```
| **NFR-454** | Real-time scoring: p99 < 50 ms server-side for a single quote against a live Rating Version, excluding network, at 200 rps sustained per replica. *(Clarified 2026-10-12, RL-1685, PL-1454 DP-3 (b): a replica is N worker processes (§2.3, **Replica**), not one process. One event loop cannot carry 200 rps of the evaluator alone: SL-1455 Task 0 measured `score_one` at a mean of 14.18 ms with one GBM call and 8.27 ms without, 2.8 and 1.7 s of evaluator time per second at 200 rps. Every reading states N; on the shared VM N = 4, a diagnostic reading only, and the reference N is fixed with G4's dedicated host.)* |
```

### T3 — `03-rating-engine.md` NFR-489

Find:

```
(Clarified 2026-10-05, OQ-1453: the ceiling governs untraced requests; a request served with an inline FR-258 trace is bounded by NFR-490.) |
```

Replace:

```
(Clarified 2026-10-05, OQ-1453: the ceiling governs untraced requests; a request served with an inline FR-258 trace is bounded by NFR-490.) (Clarified 2026-10-12, RL-1685, PL-1454 DP-3 (b): "per replica" is N worker processes, as `00` NFR-454 and `00` §2.3 **Replica** define it; every reading states N.) |
```

**Two choices in the wording, stated.** (1) T2 carries the two means because the clarification
rests on them, but not the bounds on N: those are this record's. A figure copied into a
requirement is the copy that goes stale (RFC-756), and the means are historical facts of one
dated record, not states. (2) T3 points at `00` rather than repeating it, as NFR-489 already
points at NFR-454.

## Applying

**Recommendation: apply T1 to T3 in this docs PR, in this record's commit, not in SL-1455.**
An `FR`/`NFR` is the decision-maker's to amend, via `spec-change` (`document-ids.md` §1.6, the FR
NFR DEP row). A spec edit lands with its ruling in one commit (this role's charter; RL-1645 applied its
T1 that way, in `c823ca83`, citing RL-1524 as the precedent). PL-1454's §"Write set" (`:274`) lists the two spec files
under DP-3 (b) *"with ruling text verbatim"*; applying them here meets that, so the slice's
write set loses the two spec rows rather than gaining work. The maintainer (by delegation)
confirmed it in the 07:44:13 entry's condition: the dated lines on NFR-489 and NFR-454 land in
RL-1685's mint (minted from working id 9800).

## What it obliges

- **At the mint (the minter):** done 2026-10-12 for the ruling's own id: "RL 9800" is rewritten
  to RL-1685 here and in T1 to T3's applied text, and the find strings were re-counted (0) and the
  replace strings (1) at the then-current main. Still owed by the LG's minter: LG 9932's minted
  id is added to `relates:`.
- **SL-1455, Tasks 1 to 3 (executor-sl1455), after this merges and the lead's go:**
  - Task 1 Step 3 runs: `--workers N` reaches `_serve`'s `uvicorn` arguments, and Task 4 runs
    every invocation at `--workers 4`, recording N in each ledger line. **Every bench output
    prints N in its header** (the 07:44:13 entry's condition), so a reading without N cannot
    exist; Task 1 Step 3 adds it with the flag, and a test asserts the header carries the N the
    server was started with.
  - Task 2's bounds are `MAX_CHECKOUTS = 1` and `MAX_STATEMENTS = 9` at rate 0. Add DP-1 (b)'s two
    tests at a 60 s interval and the sampling-read degrade test (Ruled 1 (a)). Add no cache test:
    DP-2 admits none.
  - Task 3: Step 1 as widened in Ruled 1 (a); Step 2 at 60 s; Step 3 is `gc.freeze()` at the end
    of the lifespan's start-up, with a timing-free red-first test that `gc.get_freeze_count()`
    is non-zero once the app has started. Pool arguments are unchanged.
  - Under option (i), accepted 07:44:13, the write set widens to FR-452's scoring-limit dependency
    (`backend/src/app/api/score.py:161`, `_enforce_score_rate_limit`) and, if the Setting read
    moves, `backend/src/app/platform/rate_limit.py` (`enforce`, `:112`). This record lists it;
    the LG records it as a widening by ruling.
- **SL-1259 (Hand-off 3):** the measurement basis changes with DP-3 (b). The lead routes T1 to
  T3 and N to SL-1259's planner.
- **G4's dedicated-host measurement** fixes the reference N. That is the maintainer's, with the
  carried verdict.

## Acceptance — the violation that must become detectable

- `grep -cF '| **Replica** |' docs/specs/00-overview.md` is 1 (0 at `fc4401dc`).
- `grep -cF 'Clarified 2026-10-12, RL-1685, PL-1454 DP-3 (b)' docs/specs/00-overview.md docs/specs/03-rating-engine.md`
  is 1 in each file (the minted id; the draft's "RL 9800" form was rewritten at the mint).
- In the product: a `/score` request that takes a second pool checkout, or writes `api_keys`
  twice within 60 s, fails `backend/tests/test_score_request_cost.py`. A server process with no
  frozen generation fails Task 3's freeze test. An NFR-489 reading with no N stated is not a
  reading under T2, and a bench output whose header does not print N fails Task 1 Step 3's
  header test.
