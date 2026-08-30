# NFR-RATE-5 — batch scoring throughput per worker (W11 Slice 3, Task 3D)

`docs/specs/03-rating-engine.md` §9 (`:886`): *"Batch scoring ≥ 1 M risks/hour per worker
(NFR-OVR-2), linear in workers."* **The requirement has two clauses, and this note measures
one of them.** The throughput clause is measured and **PASSES at 5.09× budget**. The
linearity clause is **NOT MEASURED** — only one worker ran. Read together with
`docs/plans/2026-08-29-w11-3-batch-scoring.md` Task 3D's acceptance standard, which
requires exactly this split rather than one collapsed verdict: *"'Linear in workers' is a
claim, not a measurement, unless two workers were run. If only one was, say so and mark
the linearity untested rather than implying it."*

**Not a CI gate.** Ruling 6's governance carried over unchanged
(`docs/plans/2026-08-29-w11-slice1-rulings.md`): a timing assertion on a shared runner
fails for reasons that have nothing to do with the code. This is a number for a workstream
closure record, read once against the budget by a human.

## Method

- **Code under test.** `app.worker.scoring_handlers._score_batch_handler`, invoked
  directly — no Celery, no `execute_job`, no HTTP, no FastAPI. The route
  (`POST /api/v1/score/batch`, Task 3C) only submits a Job; its own overhead is not this
  component's cost, the same reason `bench-rating.py` measures `score_one` directly and
  `bench-compiled-for.py` measures `_compiled_for` directly rather than through a route.
- **Script.** `scripts/bench-score-batch.py`, run as
  `uv run python scripts/bench-score-batch.py --rows 300000 --chunk-rows 50000
  --warmup-rows 5000`.
- **Fixture — no `model_call` step, and this is a disclosed simplification, not an
  attempt to make the number pass.** One compiled Rating Version: a single `int` input
  (`premium_in`), one expression step (`premium_in * 2`), no rate table pin, no GBM
  booster. Row width: **1 input column.** This is far simpler than NFR-RATE-1/2's own
  ~200-step motor structure (`bench-rating.py`), and **this note's numbers are not
  comparable to NFR-RATE-1/2's** — the same disclaimer `w11-3b-compiled-for-content-hash-
  delta.md` makes for its own narrower fixture. NFR-RATE-5's budget is about the batch
  **pipeline** (chunking, the manifest, scratch I/O, the final parquet write) at scale;
  per-row algorithm cost is NFR-RATE-1/2's budget, already measured separately. This note
  does not attempt to combine the two figures — that arithmetic is not a substitute for
  measuring a realistic (with-`model_call`) batch fixture directly, which this note does
  not do and does not claim to.
- **Real Postgres and MinIO**, exactly as production runs: the handler does real I/O (one
  version-row read, one dataset-table blob read, one scratch write + one scratch read per
  chunk, one final blob write). `docker compose -f deploy/docker-compose.yml up -d --wait`
  then `alembic upgrade head` before the run.
- **Chunk size.** 50,000 rows/chunk — 6 chunks over the measured 300,000-row run.
- **Warmup.** 5,000 rows, a separate Dataset Version, run and discarded before the timed
  block (3.298 s) — excluded from the reported figure.
- **Machine.** `x86_64`, 4 cores — a shared development machine, not a dedicated benchmark
  host, used concurrently by other sessions on this team.
- **Load.** Read three ways, because this box is shared and the condition is part of the
  measurement, not colour:
  - Ambient 1/5/15-minute load immediately before starting: **0.53 / 0.63 / 1.15**
    (`cat /proc/loadavg`; `pgrep -af 'pytest|uv run|celery'` from this session showed
    nothing else running at that moment, though other sessions' activity on the shared box
    cannot be ruled out).
  - The script's own 1-minute reading bracketing the *timed 300,000-row block only*
    (excludes setup and warmup): **1.05 → 2.62**.
  - Ambient 1/5/15-minute load shortly after the run finished (~15:22Z): **2.57 / 1.77 /
    1.50** — the 15-minute figure was already decaying from earlier CI activity on the
    box, so it was not cold going in.
  - **Load rose during the run rather than falling, and the run still passed at 5.09×
    budget.** Rising contention biases a wall-clock figure *slower*, not faster — the
    opposite of the direction that would make a marginal pass suspect. A number that holds
    under rising load is, if anything, a conservative one.
- **Tree.** `3dc8d6b1f8920aa135736328677be39a9d0df043` — `origin/main`'s tip after W11
  Task 3C merged (#475). This worktree's own branch (`feat/w11-3d-nfr-rate-5`) adds only
  `scripts/bench-score-batch.py` and this note on top of it; no scored code differs from
  that tree.
- **Pass count.** One run of the script (one measured 300,000-row block), preceded by one
  discarded 5,000-row warmup block. Not repeated: the result (5.09× budget) is not near the
  bound, so a single pass is sufficient per Task 3D's own acceptance standard and per the
  general rule that repetition matters most near a bound, not far from one.
- **Ref cardinality.** One Rating Version ref scored per run.
- **Worker cardinality.** **One.** No second concurrent worker was run — see *Result*
  below for what this means for the requirement's second clause.

## Result

| metric | value |
|---|---|
| rows measured | 300,000 |
| elapsed | 212.016 s |
| throughput | 1,415.0 rows/s |
| throughput | **5,093,947 risks/hour/worker** |
| budget (NFR-RATE-5, throughput clause) | ≥ 1,000,000 risks/hour/worker |
| **throughput clause verdict** | **PASS — 5.09× budget** |
| **linearity clause verdict** | **NOT MEASURED — one worker only** |

## What this does and does not show

**Shows:** the `score.batch` handler pipeline — manifest/scratch I/O through
`BlobStore.write_scratch`/`read_scratch`, `score_batch`'s own chunked Polars transform, and
the final content-addressed parquet write — sustains throughput well above NFR-RATE-5's
floor on this machine, for a trivial single-column algorithm, under real Postgres/MinIO I/O
and rising ambient load.

**Does not show:**

- **Throughput against a realistic motor structure.** No `model_call`/GBM step is in this
  fixture. A production batch run against NFR-RATE-1's own ~200-step structure would spend
  materially more CPU per row than this fixture's near-noop expression, and this note makes
  no claim — numeric or qualitative — about what that would do to the figure above. That is
  a distinct, unmeasured question, not answered here.
- **Linearity across workers (NFR-RATE-5's second clause).** Only one worker ran. "Linear
  in workers" is untested and must not be read as implied by a single-worker throughput
  figure, however large its margin.
- **Sustained/steady-state behaviour beyond one pass.** One run, one measured block. The
  margin (5.09×) is far from the 1 M/hour bound, which is why Task 3D's own acceptance
  standard treats a single pass as sufficient here — the caveat about repeating a
  measurement applies near a bound, not five times past one.

## Disposition

**Verdict, split at the requirement's own clauses (`CLAUDE.md` §13):**

- **Throughput clause — delivered and evidenced.** ≥ 1 M risks/hour/worker, measured
  directly against the handler, 5.09× budget, PASS.
- **Linearity clause — not started.** No second worker was run in this slice; nothing
  under W11 attempts a multi-worker throughput measurement. This is not a deferral of a
  failing result — it is an unattempted measurement, and it is named here rather than
  silently folded into a single "NFR-RATE-5 met" line, which is precisely the shape that
  produced the NFR-RATE-11 clause-collapse this note's own dispatch cites as the standing
  cautionary instance.
