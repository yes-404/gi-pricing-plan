---
id: PL-1574
family: plan
kind: map
title: WK-1178 — the FD-1573 remedy, dislocation_frame's memory and time at book scale (a profiling spike first, then the measured fix): single-row Work plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
owner: planner
tree: 61e2a8d9d06087cadd3760e9668b3caff881b85c
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1371, PL-1535, SL-1387, SL-1388, SL-1526, SL-1527]
---

# PL-1574 — WK-1178: the FD-1573 remedy, single-row Work plan

*Disclosure: drafted under working ids 9447 (this plan) and 9448 (its slice row); minted as PL-1574 and SL-1575 on 2026-10-10, in the D5 batch mint PR.*

> **For agentic workers:** this is a **single-row WK-1178 Work plan** under Lean P2 L5, in the
> form of `PL-1535`: WK-1178 has no map plan, so this is one row, the slice SL-1575 (working
> id), cut on this file's branch. Its `LG-` quotes the row below as its scope. REQUIRED
> SUB-SKILL for the executor: subagent-driven-development (recommended) or executing-plans.
> The executor also binds `python-test` (the `req` marker, broken-input proofs),
> `test-driven-development` (every red seen first, by its cause), `dev-commands` (the gate slot
> wrapper, the two-half gate, `uv sync --all-packages` in a fresh worktree) and `git-hygiene`;
> reads [`README.md`](README.md)'s five unchecked conventions; and is spawned from
> `.claude/roles/executor.md`.

Filed under the working ids named in the disclosure line above, both reserved by the lead in
`~/gi-pricing-plan.local/handover/brief-w3-quartet-2026-10-10.md` Section C. Written by the
planner (planner-remedy) on 2026-10-10 from 00:14:41 BST (`TZ=Europe/London date`). Evidence
read at `origin/main` `61e2a8d9d06087cadd3760e9668b3caff881b85c` (#1253,
2026-10-09T14:25:58+01:00) unless a line names another commit. **No test and no measurement
was run at planning time.** Every figure below is either quoted from a log with its file, or
labelled *derived*.

**Draft, not frozen.** The three decision points (DP-1 to DP-3) are ruled, by the maintainer's
entry "2026-10-10 00:20:03 BST — RULINGS on the FD 9446 remedy plan (PL 9447 + SL 9448
@5921b3dc): DP-1 (a), DP-2 (a) as a PLAN TARGET, DP-3 (a); …" [PL 9447 is minted as PL-1574, SL 9448 as SL-1575, FD 9446 as FD-1573] in `channel/to-lead.md`. Each
ruling is quoted under its DP below. The plan does not activate until FD-1573
carries its severity and the R6 size (DP-2) is quoted.

## Authority

- **The order**: the maintainer's entry "2026-10-10 00:08:17 BST — USER: go ahead. FD 9446 on
  the measured curve, a remedy-slice proposal, and the Friday re-baseline (after S3's merge, in
  W3)" [FD 9446 is minted as FD-1573] in `channel/to-lead.md`, item 2: *"REMEDY-SLICE PROPOSAL (for my ruling): WK-1178, owner
  the lead, placed before SL-1526 in the exit-demo chain. The hypothesis to test first is memory
  per policy in score_batch (`.collect()` materialisation, frame width). Its plan opens with a
  1-hour profiling spike (py-spy or memray on 200k), not a redesign. Lane choice and the
  merge-order slot (compile.py serialisation) come with it."*
- **The path to profile**: the maintainer's entry "2026-10-10 00:10:36 BST — USER: more than
  10% of the weekly allowance is left …", B: *"The remedy spike profiles the PATH THE EXIT DEMO
  USES (the dislocation step, if that is the G2 path). Quote it."* And the lead's correction in
  `channel/from-lead-2026-10-09.md`, "2026-10-10 00:08:46 BST — Lead: RECEIPT for 00:08:17, and
  a CORRECTION to its curve: two rating paths, two rates …".
- **The escalation**: "2026-10-09 19:40:02 BST — RULING: R2 step 1 = S1 …", item 3b: *"If it
  is HIGH, the lead proposes the remedy slice under WK-1178 with an owner and a place in the
  exit-demo chain (before SL-1526, the real freMTPL2 algorithm slice), for my ruling."*
- **The compile.py order this slice is placed against**: "2026-10-09 15:29:43 BST — RULINGS on
  the lead's 15:29:15 …": *"The default order is exit-demo first: S4 → A-1 → SL-1340 → FD-1374
  → WK-675 S3, unless a GO request argues otherwise."*
- **One plan per Work**: "2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items 1, 3 and 5
  APPROVED …", L5; the single-row form is `PL-1535`'s.

## What was measured, and what the code says it was

**Logged** (`~/gi-pricing-plan.local/task7-s3e/out/`; harness `inv-rss.sh`, peak RSS =
`getrusage(RUSAGE_CHILDREN).ru_maxrss`; tree `f59b546e748eca464c279a77ca48e166689d5a0e`, each
run alone in gate-1):

| Run (`progress.log` name) | Command (`measure-attribution-cost.py`) | Whole invocation | `score_batch` alone (`.jsonl`) | Peak RSS | load1 at END |
|---|---|---|---|---|---|
| `50-sb-200k` | `cost --policies 1000 --score-policies 200000 --ks "" --runs 1` | 21:13:07–21:37:19 BST | 424.86 s, 470.74 pol/s | 6,513,848 KiB | 2.45 |
| `60-sb-400k` | `cost --policies 1000 --score-policies 400000 --ks "" --runs 1` | 21:37:35–22:23:27 BST | 848.41 s, 471.47 pol/s | 12,515,908 KiB | 2.80 |

**What the untimed part is** (read in code at `f59b546e`; `analysis.py`'s three functions
below are identical at `origin/main`, 28 lines higher there, and at S3's head `8d026a7e`):

- `cmd_cost` (`scripts/measure-attribution-cost.py:645-684`) times only
  `score_batch(bundle, frame).collect()` (:666-669). Before it, untimed, it builds each book with
  `portfolio_for(fx, n).collect()` (:655, :659).
- `portfolio_for` (:477-495) calls **`dislocation_frame(bundle, bundle, first, …)`** (:493) to
  set `current_premium_minor`.
- `dislocation_frame` (`packages/pricing-core/src/pricing_core/rating/analysis.py:177-226` at
  `origin/main`) collects the portfolio (:190), then calls `_score_pass` **twice** (:192-193),
  and each `_score_pass` (:144-174) runs a full `score_batch(...).collect()` (:159), then for
  every quoted row does `json.loads` of `premium_ladder_json` and `LadderRung.model_validate`
  per rung (:163), and **retains the validated ladder of every policy** in its returned dict
  (:168-173) until both passes are done and the row loop (:196-211) has finished.

**Derived, not measured:** at 200k the untimed remainder is 1452 − 425 ≈ 1027 s (the lead's
00:08:46 figure). Two `score_batch` passes at the logged 470.74 pol/s are ≈ 850 s, so the
`dislocation_frame` overhead beyond its two scoring passes (portfolio collect, JSON and Pydantic
re-parse, the row loop, the join), plus the fixture load and compile, is ≤ ≈ 177 s. **The "≈ 195
pol/s" of the second path is therefore mostly two scoring passes, not a slow third mechanism.**
Peak RSS is linear at ≈ 31 KiB per policy (6,513,848 / 200,000 = 32.6; 12,515,908 / 400,000 =
31.3), whole-invocation and not separable by path from these runs.

**The exit demo's path** (read at WK-673 S4's head `8af8a9b4`, not on `main`): `WF-699` D6 is
`POST /dislocation-runs` (`docs/workflows/WF-00699-…md:86`, `03` FR-263), and S4's handler
`_dislocation_run` calls `dislocation_frame(loaded.baseline_bundle, loaded.candidate_bundle,
lazy, spec)` at `backend/src/app/worker/dislocation_handlers.py:223`, then `attribute(...)` at
:231. On `origin/main`, `JobKind.DISLOCATION_RUN` has a queue (`backend/src/app/platform/
jobs.py:80`) but no handler. **So the demo's dislocation step runs `dislocation_frame`, which
contains `score_batch` twice: one profile of `dislocation_frame` covers both paths the lead's
correction names.** Whether the demo's portfolio is the full 678,013-policy book or a subset is
the R6 size, which the 00:20:03 BST entry makes URGENT. It is not this plan's to fix. At
`origin/main` `61e2a8d9` and S4's `8af8a9b4`, no text names the D6 portfolio Dataset Version
(the planner's quote file `~/gi-pricing-plan.local/handover/r6-portfolio-size-2026-10-10.md`,
2026-10-10 00:21:59 BST). So the R6 size is **pending**.

## Goal

Make the `WF-699` D6 dislocation run complete on the exit demo's portfolio within DP-2's ruled
target (a plan acceptance target, not an NFR), by removing the cause the spike measures, without
changing one value of `dislocation_frame`'s output. Done when SL-1575 closes on its `LG-` with
the after-measurement beside the before-measurement, and FD-1573's register row carries the
fix's merge sha.

## Acceptance Standard

Each item is checked by a command run from the repository root on the slice's merge tree, or
read from the `LG-`, which quotes the command and its printed lines.

1. **Task 0's spike is filed before any code changes**: the `LG-` carries both spike outputs
   (`spike-20k.jsonl`, `spike-200k.jsonl`, every line quoted), the tree sha each ran on, the
   start and end stamps from `date`, load1, and the DP-3 rule's outcome stated as "H1 confirmed"
   or "H1 falsified" with the arithmetic shown.
2. **The output is unchanged, value for value**: `uv run pytest -q
   packages/pricing-core/tests/test_rating_dislocation.py` exits 0, and the new test
   `test_dislocation_frame_retains_no_ladder_objects` was seen red first by its cause (the
   `LG-` quotes the red line), and the new test
   `test_dislocation_frame_output_unchanged_on_the_fixture_book` passes: it builds the frame on a
   fixed 2,000-policy book with the old code path (a copy kept in the test module) and the new
   one and asserts `old.equals(new)`; proven on broken input by flipping one candidate rung's
   `unrounded_minor` and seeing it fail.
3. **Memory is measured, not asserted**: Task 0's harness re-run at 200,000 on the merge tree,
   alone in a gate slot, N=1; the `LG-` tables before (Task 0) and after, per stage, VmHWM and
   seconds. The after VmHWM per policy is at or below DP-2's ruled ceiling (15.5 GiB) divided by
   the R6 size (pending; see Authority).
4. **Time is measured, not asserted**: the same run's `dislocation_frame` wall time at 200,000
   is no more than Task 0's (a slower fix fails this item).
5. **The R6 size, once**: `measure-attribution-cost.py cost --policies <R6 size> --ks ""
   --runs 1` under `inv-rss.sh`, alone, completes within its inner timeout. The `LG-` quotes
   its `progress.log` START and END lines and `ru_maxrss_KiB`, read against DP-2's target
   (peak RSS ≤ 15.5 GiB, ≤ 60 min). `<R6 size>` is the quoted R6 size: 678,013 if the R6
   ruling names the full book, or the subset's size otherwise. The `LG-` cites the R6 text it
   used.
6. **The gate is green**: the `CLAUDE.md` §11 commands, both halves, each exit 0, against
   `origin/main...<slice branch>`, in a gate slot.

## Global Constraints

- **Money is integer minor units or `Decimal` in the rating path, never float** (`CLAUDE.md`
  §7). The fix keeps `value_minor` as the `int` and `unrounded_minor` as the value
  `LadderRung.model_validate` produced; it never re-parses either itself.
- **`dislocation_frame`'s signature and return frame are unchanged** (`03` FR-263; WK-673 S4's
  handler, `dislocation_handlers.py:223` at `8af8a9b4`, consumes it). Same columns, dtypes, row
  order (`sort("quote_id")`) and values.
- **Determinism and money exactness hold** (`03` NFR-495, NFR-496): item 2 is their evidence for
  this change; the existing `NFR-495`/`NFR-496` tests in `test_rating_dislocation.py` stay
  green.
- **`pricing-core` stays importable standalone** (`CLAUDE.md` §2; `.importlinter`): every
  change is inside `pricing_core.rating.analysis`.
- **No new dependency: standard library only** (DP-3 (a), ruled 2026-10-10 00:20:03 BST;
  `CLAUDE.md` §10 and §3): neither
  py-spy nor memray is in `pyproject.toml`, `uv.lock` or `docs/skills-map.md` at `origin/main`,
  and `which py-spy memray` finds neither on the box (exit 1, checked 2026-10-10 00:17:57 BST). Task 0 as
  written uses the standard library only.
- **A spike or measurement run is a slot job**: queued by the lead, alone, never beside a gate
  or another measurement (the 00:08:41 entry, item 3; the sweep-pause rule in
  `.claude/roles/executor.md`).
- **One PR per slice** (L1 (a')): code, tests, SL-1575's status line and one `LG-`.

## Tasks

Under L5 a Work plan's tasks are its slice rows; this row's steps follow the table.

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Lane | Size |
|---|---|---|---|---|---|---|
| 1 | SL-1575 — WK-1178 fix slice — FD-1573: `dislocation_frame`'s memory and time at book scale | Task 0, the 1-hour profiling spike of `dislocation_frame` at 20,000 (Python heap) and 200,000 (RSS and time), with the H1 decision rule; then, only if H1 is confirmed, Task 1: `_score_pass` retains each rung's `(value_minor, unrounded_minor)` instead of the validated `LadderRung` objects; then Task 2, the after-measurement. **Out of scope:** `score_batch`'s per-row engine evaluation (its docstring: *"This is not genuine polars streaming"*, `score.py:1186-1234`); `attribute`'s 2^K re-rates (S3's code; see DP-1); any change to `03` text | `03` §8: NFR-493 (rated, not changed); `03` §3: FR-263 (output unchanged); `03` §8: NFR-495, NFR-496 (held) | WK-673 S3 (`SL-1387`) merged, because `analysis.py` and `measure-attribution-cost.py` are its write set; FD-1573 minted with HIGH; DP-1 to DP-3 ruled | B (recommended; see Sequencing) | ≈ 1.5 lane-days, derived (see Size) |

### Task 0: the profiling spike (1 hour; the run is a slot job)

**Files:** none in the repository. The harness is written to
`~/gi-pricing-plan.local/task-9447/spike.py`; output to the same directory.

**Tree:** S3's merge commit on `main` if S3 has merged; otherwise a fresh detached worktree at
`f59b546e748eca464c279a77ca48e166689d5a0e` (the measured tree), created with
`git worktree add --detach`, followed by `uv sync --all-packages` in it. Record the sha. Never
the S3 executor's worktree.

**Hypotheses, stated before the run** (the maintainer's "memory per policy … `.collect()`
materialisation, frame width", made specific to the code read above):

- **H1 (memory, retention):** the dominant memory is `_score_pass`'s returned dict, which holds
  every policy's validated `LadderRung` list for **both** passes at once (:168-173, :192-193).
- **H2 (memory, transient):** the dominant memory is `score_batch(...).collect()`'s whole-pass
  output (:159), including the `premium_ladder_json` strings, while the other pass's dict is
  alive.
- **H3 (time):** the JSON and Pydantic re-parse (:163) is a material share (≥ 20 %) of each
  pass's time beyond `score_batch`.

- [ ] **Step 1: Write the harness.** It wraps the module globals `dislocation_frame` looks up at
  call time, so the real function runs once and each stage is stamped.

```python
"""PL-1574 Task 0: dislocation_frame's stages at N policies — time, RSS, Python heap."""
from __future__ import annotations

import argparse
import asyncio
import gc
import importlib.util
import json
import sys
import time
import tracemalloc
from pathlib import Path


def _status() -> dict[str, int]:
    out: dict[str, int] = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in ("VmRSS", "VmHWM"):
            out[key + "_KiB"] = int(value.split()[0])
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tree", required=True)
    p.add_argument("--policies", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--tracemalloc", action="store_true")
    a = p.parse_args()

    loader = importlib.util.spec_from_file_location(
        "mac", Path(a.tree) / "scripts" / "measure-attribution-cost.py"
    )
    assert loader is not None and loader.loader is not None
    mac = importlib.util.module_from_spec(loader)
    sys.modules["mac"] = mac
    loader.loader.exec_module(mac)

    import polars as pl
    from pricing_core.rating import analysis
    from pricing_core.rating.compile import compile_bundle
    from pricing_core.rating.runtime import load_bundle

    log = open(a.out, "w")
    t0 = time.perf_counter()

    def mark(stage: str, **extra: object) -> None:
        gc.collect()
        rec: dict[str, object] = {"stage": stage, "t_s": round(time.perf_counter() - t0, 2)}
        rec.update(_status())
        if a.tracemalloc:
            cur, peak = tracemalloc.get_traced_memory()
            rec.update(traced_current_B=cur, traced_peak_B=peak)
        rec.update(extra)
        log.write(json.dumps(rec) + "\n")
        log.flush()

    real_score_batch = analysis.score_batch
    real_score_pass = analysis._score_pass
    real_read_portfolio = analysis.read_portfolio
    passes = {"n": 0}

    def score_batch(bundle, frame, **kw):  # type: ignore[no-untyped-def]
        mark(f"pass{passes['n'] + 1}.score_batch.start")
        out = real_score_batch(bundle, frame, **kw).collect()
        mark(f"pass{passes['n'] + 1}.score_batch.collected", est_B=out.estimated_size())
        return out.lazy()

    def score_pass(*args, **kw):  # type: ignore[no-untyped-def]
        result = real_score_pass(*args, **kw)
        passes["n"] += 1
        rungs = sum(len(v["ladder"]) for v in result.values())
        mark(f"pass{passes['n']}.retained", policies=len(result), rungs=rungs)
        return result

    def read_portfolio(*args, **kw):  # type: ignore[no-untyped-def]
        mark("read_portfolio.start")
        return real_read_portfolio(*args, **kw)

    analysis.score_batch = score_batch
    analysis._score_pass = score_pass
    analysis.read_portfolio = read_portfolio

    if a.tracemalloc:
        tracemalloc.start()
    mark("start")
    fx = mac.load_fixture()
    df = mac.load_portfolio(a.policies)
    cols = ["quote_id", "exposure_years", *mac.FACTORS_V1, *mac.FACTORS_V2_ONLY]
    book = df.select(cols).lazy().with_columns(
        pl.lit(10**9, dtype=pl.Int64).alias("current_premium_minor")
    )
    mark("portfolio.loaded", rows=df.height, est_B=df.estimated_size())
    base_v, _cand_v, resolver = mac.versions_for(fx, [])
    bundle = load_bundle(asyncio.run(compile_bundle(base_v, resolver)))
    spec = mac._spec(base_v, base_v)
    mark("compiled")
    frame = analysis.dislocation_frame(bundle, bundle, book, spec)
    mark("dislocation_frame.returned", rows=frame.height, est_B=frame.estimated_size())


if __name__ == "__main__":
    main()
```

  It mirrors `portfolio_for` (:477-495): the same columns, the same placeholder
  `current_premium_minor`, baseline against itself. `gc.collect()` at each mark adds time; the
  `LG-` says so beside every time figure.

- [ ] **Step 2: Smoke it at 1,000 policies** (seconds; allowed outside a slot as a small run,
  `nice -n 19`, only when no gate slot is held — check `flock -n /tmp/slots/gate-1 true` and the
  same for `gate-2` first):
  `nice -n 19 uv run --directory <tree> python ~/gi-pricing-plan.local/task-9447/spike.py --tree <tree> --policies 1000 --out ~/gi-pricing-plan.local/task-9447/spike-1k.jsonl`.
  Expected: 11 lines, stages in the order `start`, `portfolio.loaded`, `compiled`,
  `read_portfolio.start`, `pass1.score_batch.start`, `pass1.score_batch.collected`,
  `pass1.retained`, `pass2.score_batch.start`, `pass2.score_batch.collected`, `pass2.retained`,
  `dislocation_frame.returned`. A
  missing stage means a wrapper did not bind: stop and report, do not edit `analysis.py`.

- [ ] **Step 3: The two runs, as ONE slot job queued by the lead** (≈ 3 min, then ≈ 25 min,
  derived from the 200k invocation's 24.2 min less the 1,000-policy book build):
  first `--policies 20000 --tracemalloc --out …/spike-20k.jsonl`, then
  `--policies 200000 --out …/spike-200k.jsonl`, each under `timeout 2700`, nothing else
  running. Stamp START and END with `date` and `cut -d' ' -f1 /proc/loadavg`.

- [ ] **Step 4: Apply the decision rule (DP-3's recommended form) and file it in the `LG-`.**
  - **Python heap retained per policy (20k run):** `R = (traced_current_B at pass2.retained −
    traced_current_B at read_portfolio.start) / 20000`.
  - **Peak per policy (200k run):** `P = VmHWM_KiB at dislocation_frame.returned × 1024 /
    200000`.
  - **H1 confirmed** if `R ≥ 0.4 × P`. Then Task 1 applies as written.
  - **H2 indicated** if the VmHWM step from `pass2.score_batch.start` to
    `pass2.score_batch.collected` is the largest single step. **H3 indicated** if
    `(t at pass1.retained − t at pass1.score_batch.collected) ≥ 0.2 × (t at pass1.retained −
    t at pass1.score_batch.start)`.
  - **H1 falsified**: the executor stops after Step 4. The remedy for the measured cause is a
    dated Work-plan delta (a new `PL-` that `relates:` this one), never an edit here.

  tracemalloc sees only memory allocated through Python's allocator; Polars' buffers are not in
  it. That is why the rule takes the retained Python heap from the 20k run and the peak from the
  RSS of the 200k run, not both from one.

### Task 1: `_score_pass` retains rung values, not `LadderRung` objects (only if H1 is confirmed)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/analysis.py` (`_origin_rung` :128-141,
  `_score_pass` :144-174, `dislocation_frame`'s row loop :209 — line numbers at `origin/main`;
  re-read at the slice's base, S3's merge, where they sit 28 lines lower)
- Test: `packages/pricing-core/tests/test_rating_dislocation.py`

**Interfaces:**
- Produces: `_RungValues = dict[str, tuple[int, object]]` (rung name → `(value_minor,
  unrounded_minor)`, both exactly as `LadderRung.model_validate` produced them);
  `_rung_values(ladder: Sequence[LadderRung]) -> _RungValues`;
  `_origin_rung_of(baseline: _RungValues, candidate: _RungValues) -> str | None`.
- Keeps: `_origin_rung(baseline: Sequence[LadderRung], candidate: Sequence[LadderRung]) -> str |
  None`, now delegating, so the existing tests at `test_rating_dislocation.py:383-390` are
  unchanged; `dislocation_frame`'s signature and frame.

- [ ] **Step 1: Write the failing tests.**

```python
@pytest.mark.req("NFR-495")
def test_dislocation_frame_output_unchanged_on_the_fixture_book() -> None:
    """The new retention gives the frame the old code gave, value for value."""
    baseline, candidate, book, spec = _book_2000()
    new = analysis.dislocation_frame(baseline, candidate, book, spec)
    old = _old_dislocation_frame(baseline, candidate, book, spec)
    assert old.equals(new)


def test_dislocation_frame_retains_no_ladder_objects() -> None:
    """_score_pass keeps (value_minor, unrounded_minor) per rung, never a LadderRung."""
    baseline, _candidate, book, spec = _book_2000()
    out = analysis._score_pass(baseline, book, book.collect_schema().names(), spec, spec.baseline_ref)
    quoted = [v for v in out.values() if v["outcome"] == "quoted"]
    assert quoted
    assert all("ladder" not in v for v in quoted)
    assert all(
        isinstance(name, str) and isinstance(pair, tuple) and len(pair) == 2
        for v in quoted
        for name, pair in v["rungs"].items()
    )
```

  `_book_2000()` builds 2,000 policies from the module's existing book builder (`_book16()` is
  the precedent; read it and scale it with distinct `quote_id`s, both bundles differing in at
  least one rung's `unrounded_minor` only, so `origin_rung` is exercised).
  `_old_dislocation_frame` is a verbatim copy, in the test module, of `_score_pass`,
  `_origin_rung` and `dislocation_frame` as they stand at the slice's base, with a comment naming
  that sha; it is deleted by no later task.

- [ ] **Step 2: Run them.**
  `nice -n 19 uv run pytest -q packages/pricing-core/tests/test_rating_dislocation.py -k "unchanged_on_the_fixture_book or retains_no_ladder_objects"`.
  Expected: the `unchanged` test PASSES (both paths are the same code now) and the `retains` test
  FAILS on `assert all("ladder" not in v …)`, because `_score_pass` stores `"ladder"` (:172).
  A failure on anything else is a plan defect: stop and report.

- [ ] **Step 3: The change.**

```python
_RungValues = dict[str, tuple[int, object]]


def _rung_values(ladder: Sequence[LadderRung]) -> _RungValues:
    return {r.rung: (r.value_minor, r.unrounded_minor) for r in ladder}


def _origin_rung_of(baseline: _RungValues, candidate: _RungValues) -> str | None:
    """The first rung, in `RUNG_ORDER`, present in one ladder only or differing in `value_minor`
    or in `unrounded_minor` (compared as the validated values, never as strings)."""
    for name in RUNG_ORDER:
        b, c = baseline.get(name), candidate.get(name)
        if b is None and c is None:
            continue
        if b is None or c is None or b[0] != c[0]:
            return name
        if b[1] != c[1]:
            return name
    return None


def _origin_rung(baseline: Sequence[LadderRung], candidate: Sequence[LadderRung]) -> str | None:
    """The first rung, in `RUNG_ORDER`, present in one ladder only or differing in `value_minor`
    or in `unrounded_minor` (a `Decimal`: `Decimal("100") == Decimal("100.0")`)."""
    return _origin_rung_of(_rung_values(baseline), _rung_values(candidate))
```

  In `_score_pass`, the loop body becomes:

```python
        rungs: _RungValues = {}
        premium: int | None = None
        if row["outcome"] == "quoted":
            ladder = [LadderRung.model_validate(r) for r in json.loads(row["premium_ladder_json"])]
            payable = [r for r in ladder if r.rung == "payable_premium"]
            if not payable:
                raise ValueError("dislocation: a quoted row carries no payable_premium rung")
            premium = int(payable[0].value_minor)
            rungs = _rung_values(ladder)
        out[row["quote_id"]] = {
            "outcome": row["outcome"],
            "error_code": row["error_code"],
            "minor": premium,
            "rungs": rungs,
        }
```

  and in `dislocation_frame`'s row loop, `_origin_rung(b["ladder"], c["ladder"])` becomes
  `_origin_rung_of(b["rungs"], c["rungs"])`. The `str` keys are sound: `LadderRung.rung` and
  `RUNG_ORDER`'s elements are both `LadderRungName`, a `Literal` of strings
  (`packages/model-schema/src/model_schema/scoring.py:49`, read at `origin/main`).

- [ ] **Step 4: Run the file.**
  `nice -n 19 uv run pytest -q packages/pricing-core/tests/test_rating_dislocation.py`. Expected:
  all pass, the two new tests included.

- [ ] **Step 5: Broken-input proof.** In `_origin_rung_of`, temporarily delete the
  `if b[1] != c[1]: return name` branch; re-run the `unchanged` test; expected FAIL on
  `assert old.equals(new)` (the fixture differs in an `unrounded_minor` only). Restore; the `LG-`
  quotes the red line.

- [ ] **Step 6: Commit** `fix(pricing-core): dislocation_frame retains rung values, not ladder
  objects (FD-1573)`, with `git add` of the two files only.

### Task 2: the after-measurement and the gate

- [ ] **Step 1:** Task 0's harness at 200,000 on the slice's head, as one slot job, alone; then,
  the `cost` run at the R6 size under `inv-rss.sh` (Acceptance 5; DP-1 (a), DP-2 (a)).
  Before-and-after tables in the `LG-` (Acceptance 3–5).
- [ ] **Step 2:** the `CLAUDE.md` §11 gate, both halves, in a gate slot (Acceptance 6). Then
  SL-1575's status line and the `LG-` closed at the head (the 13:29:49 standing rule (3)).

## Sequencing, lane and merge-order slot

- **Not in the `compile.py` serial set.** The write set is `analysis.py` and its test file;
  neither is `compile.py`, `compile_bundle` or `errors.py`. The ruled default order **S4 → A-1 →
  SL-1340 → FD-1374 → WK-675 S3** is unaffected, and this slice takes no place in it.
- **Its own serial set is `analysis.py`**: WK-673 S3 (`SL-1387`, head `8d026a7e`) edits it, and
  WK-673 S4 (`8af8a9b4`) and A-1 (`f0379205`) carry the same `analysis.py` as S3's head
  (`git diff --stat 8d026a7e <head> -- …/analysis.py` prints nothing for both). So this slice
  branches from S3's merge and merges after it; it rebases cleanly past S4 and A-1 on that file.
  It changes nothing S4's handler calls.
- **In the exit-demo chain, before SL-1526** (the 00:08:17 placement): its merge is an
  activation need of `SL-1526` only by a dated line the lead adds, not by an edit to `SL-1526`'s
  row (planner Tools line). Recommended: SL-1526's own acceptance re-runs Task 0's harness on
  the real algorithm, because the measured fixture is RS-1201's attribution algorithm
  (`FIXTURE = examples/fremtpl2/rating`, `measure-attribution-cost.py:39`), not SL-1526's.
- **Lane: B, recommended.** Lane B is WK-673 S3's; it frees at S3's merge, and this slice
  starts from that merge on S3's own file. Lane A carries the `compile.py` chain (S4 → A-1 …),
  so putting this slice there would queue it behind four `compile.py` merges it does not
  conflict with. Lane C is the alternative if the lead keeps lane B for WK-673 S5.
- **Slot use**: Task 0 Step 3 ≈ 30 min, Task 2 Step 1 ≈ 25 min plus the full-book run
  (DP-1), Task 2 Step 2 one gate. None runs beside S3's `70-sets`, #1250's gate, or each other.

## Size

≈ 1.5 lane-days, **derived, not measured**: Task 0 one hour (Step 3's ≈ 30 min run plus the
rule); Task 1 a two-function change and two tests in one file, ≈ half a day with the
broken-input proof; Task 2 one 200k run (≈ 25 min), one full-book run (≈ 78 min *derived* by the
lead at 00:08:46 for the pre-fix code; less if the fix holds), and one gate. If H1 is falsified
the slice ends after Task 0 (≈ 0.2 lane-days) and the delta is sized from the spike.

## Decision points

*For the maintainer, by delegation, through the lead.*

**DP-1 — the scope: the full book, and `attribute`.**
- (a) The demo scores the full 678,013-policy book: Acceptance 5 runs at 678,013.
- (b) The demo scores a subset named in the G2 text: Acceptance 5 runs at that size.
- (c) As (a) or (b), and also bound `attribute`'s cost in D6, which S4's handler calls at :231
  when attribution is requested: the lead's 21:41:09 status derives K=3 on the full book at
  3.1–3.7 h.

**Recommendation: (a) or (b) as FD-1573's G2 quote decides, and NOT (c) in this slice.**
`attribute` is S3's code, measured under PL-1452. Its full-book cost is a separate exit-demo
risk. It needs its own FD and owner, which the lead raises; folding it in would double this
slice and couple it to S3's Acceptance 20.

**Ruled 2026-10-10 00:20:03 BST: (a)**, in the entry's words: *"DP-1 ADOPTED: the remedy
covers dislocation_frame's memory and time only. The spike's pre-registered H1/H2/H3 rule, and
the stop on falsification (fix becomes a dated delta), are approved as drafted."* The scope is
`dislocation_frame`'s memory and time only, and (c) is not in this slice. The entry adopts the
`attribute` full-book cost *"as a separate FD now … Not folded into PL 9447."* [PL 9447 is minted as PL-1574] The size this
plan measures at is the R6 size (DP-2). That size replaces the option text's "678,013" until R6
is quoted.

**DP-2 — the budget Acceptance 3 and 5 are read against.** No spec NFR covers dislocation's
memory. NFR-493 (`03` §8: *"Batch scoring ≥ 1 M risks/hour per worker (NFR-455), linear in
workers."*) is a scoring rate. Which path it governs is FD-1573's to state.
- (a) Peak RSS ≤ 15.5 GiB at the demo's size (half the 31 GiB box), and wall time ≤ 60 min
  (`WF-699`'s phase table, *"D — Regression + dislocation | 30–60 min compute"*, `WF-699`
  :150; an elapsed estimate, not an NFR).
- (b) Only "completes, with the measured figures recorded", and no ceiling.
- (c) A new NFR in `03` §8, which is a spec change first (`CLAUDE.md` §0).

**Recommendation: (a)** for this slice, with (c) proposed separately as an open question. The
time half is likely already met (two passes at 471 pol/s on 678,013 ≈ 48 min, *derived*);
memory (≈ 20.3 GiB *derived*) is what fails it. Note that D6 runs twice in the journey (E3
rejects a stale run; E4 *"Re-runs dislocation"*, `WF-699` :97-98).

**Ruled 2026-10-10 00:20:03 BST: (a)**, *"ADOPTED as a PLAN ACCEPTANCE TARGET, not an NFR"*.
The target is a plan acceptance target, not an NFR: peak RSS ≤ 15.5 GiB and ≤ 60 min per
dislocation run at the R6 size, pending. No spec text changes. (c) stays out: the entry says
it *"would be a spec change (an OQ for P3, not now)"*.

**DP-3 — the profiling tool.** The 00:08:17 entry names *"py-spy or memray"*. Neither is
installed, and adding either is a dependency choice (`CLAUDE.md` §10: `skills-map.md` is
updated in the same PR when a tech dependency changes).
- (a) The standard library only: `/proc/self/status`, `tracemalloc`, `time`, as Task 0 is
  written. No dependency.
- (b) py-spy, via `uvx py-spy` (not declared), as `PL-1454` :409 already does, for a native
  CPU flame graph of `score_batch`. No lockfile change, but an unpinned tool, and `PL-1454` :412
  records that it may not attach on this machine.
- (c) memray as a declared dev dependency in `[dependency-groups] dev`, with a `skills-map.md`
  row, in this slice's PR, for native-allocation attribution.

**Recommendation: (a).** The hypotheses are about Python-object retention, which `tracemalloc`
measures exactly, and RSS per stage separates the rest. (b) or (c) is worth a ruling only if
Step 4 reads H2 or H3 and the next question is *where in native code*. In that case it goes in
the dated delta, not in this slice.

**Ruled 2026-10-10 00:20:03 BST: (a)**, *"DP-3 ADOPTED: standard library only (no new
dependency, no skills-map row)."*

## Hand-off (not this plan's writes)

- The lead lists this plan on WK-1178's roadmap row (L5) at mint, and adds the dated line that
  makes SL-1575's merge an activation need of `SL-1526`. The 00:20:03 BST entry rules it:
  *"SL 9448 becomes an activation need of SL-1526 by a dated line at the mint."* [SL 9448 is minted as SL-1575]
- The minter cuts the ids in the batch the lead names; FD-1573 mints first, with its severity.
  The entry says *"PL 9447 rides D5 or the next batch."* [PL 9447 is minted as PL-1574]
- DP-1 (c) is declined. The `attribute` full-book cost is its own FD (the auditor's, on a
  `draft/` branch), as the 00:20:03 BST entry adopts.

## Self-review

- **Spec coverage.** FR-263 (the dislocation run whose output must not change), NFR-495 and
  NFR-496 (held, evidenced by Acceptance 2), and NFR-493 (rated in FD-1573, not changed here). No
  requirement is added. A memory NFR is DP-2 (c), a spec change and not this plan's.
- **Placeholders.** None. `<tree>` and `<slice branch>` are run-time values that Task 0 and
  Acceptance 6 define. `_book_2000()` is specified against the module's existing builder, which
  the executor reads first.
- **Type consistency.** `_RungValues`, `_rung_values` and `_origin_rung_of` are used with the
  same names and shapes in Task 1 Steps 1, 3 and 5. The `"rungs"` key replaces `"ladder"` in
  both `_score_pass` and the row loop, and the `retains` test asserts it.
- **Literals verified at source.** `analysis.py` :144-226 and `LadderRung` (`scoring.py:149-163`)
  were read at `origin/main`. `cmd_cost`, `portfolio_for`, `FIXTURE`, `FACTORS_V1`,
  `FACTORS_V2_ONLY`, `load_fixture`, `load_portfolio`, `versions_for` and `_spec` were read at
  `f59b546e`. `dislocation_handlers.py:223,231` were read at `8af8a9b4`. The harness's
  `_spec(base_v, base_v)` call mirrors `portfolio_for`'s at :493.
- **Rulings since the sweep.** The 00:20:03 BST entry is applied, quoted under each DP
  (planner-r6, 2026-10-10 00:23:42 BST, read in `channel/to-lead.md` from its line 20626). Re-check `channel/to-lead.md` after 00:10:36 BST and FD-1573's
  branch head (`draft/fd-9446`, `08f50d11` at writing; the rewrite is pending) before the plan
  is minted.
