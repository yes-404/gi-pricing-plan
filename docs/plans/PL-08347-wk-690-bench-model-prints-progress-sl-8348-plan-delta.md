---
id: PL-8347
family: plan
kind: map
title: WK-690 — scripts/bench-model.py prints a per-N-trees progress line, so a capped run yields a rate and a projection (NFR-476), SL-8348 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8347
owner: planner
tree: 2f108b1eda22a4835279cee9b4c9e305babe3662
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1665, NFR-476]
---

# PL-8347 — WK-690: `bench-model.py` prints progress (SL 8348, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds one slice row, SL 8348, and edits no filed plan. The
> executor's skills are `superpowers:test-driven-development`, `.claude/skills/python-test` and
> `git-hygiene`. PL 8347, SL 8348 and LG 8349 are working ids reserved by the lead. **Work:** the ruling
> makes NFR-476's finding WK-690's ("NFR-476 is WK-690's row, PL-1665 §5.7"), and this harness change serves
> it. The lead re-points the row if it belongs under WK-1178.

## Authority

The maintainer's entry "2026-11-05 10:14:38 GMT" in `~/gi-pricing-plan.local/channel/to-lead.md`, verbatim: "the
harness is made to PRINT PROGRESS: bench-model.py gains a per-N-trees progress line to stderr (elapsed seconds,
trees done, rows/s) so a capped run yields a RATE and a projection, never nothing; that is a ≤ 1 h harness change
on the chain before Thu 12 (red test on the progress line), merged before S2 or carried onto the VM's checkout as
a dated exception if S2 comes first." The process row: "a timed harness prints progress; a capped run must yield a
rate". The lead's message: S2 is Fri 6 Nov 2026, about 08:45.

## Goal

A capped `--only gbm` run leaves a rate and a projection in its stderr. The model, the timed figure and stdout do
not change.

## Evidence at `2f108b1e`

- **The trees are not in the script.** `bench_gbm` calls `fit_gbm` (`scripts/bench-model.py:406`), and the loop is
  `xgb.train(…, callbacks=callbacks or None, verbose_eval=False)` at
  `packages/pricing-core/src/pricing_core/modelling/gbm.py:950-956`, whose `callbacks` hold only `EarlyStopping`
  when configured (`:921`, `:939`). **So a harness-only change must reach the callback list from outside.** Adding a
  `callbacks` parameter to `fit_gbm` would put a bench seam on the product path, in `pricing-core`, on a measured
  function. Not this plan.
- **The seam:** `xgb.train` is looked up on the module at each call, in `gbm.py` and at `bench-model.py:477,483`. A
  context manager in the script replaces `xgboost.train` for the run and appends one callback. Nothing under
  `packages/` changes.
- **The callback API** is xgboost 3.4.1 (RUN, tools-main's venv): `xgboost.callback.TrainingCallback`,
  `before_training`, `after_iteration(model, epoch, evals_log)`, which returns `False` to continue.
- **Stdout is parsed.** `tests/test_measure_p2_nfr_sweep.py:139` holds `parse_bench_line`, on stdout. Stderr is free.
- **The flags are read from the parser** (`main`, `:820-866`, by reading, not by a single-line grep): `--only`,
  `--rows`, `--factors`, `--rounds`, `--pairs`, `--peak` and the rest. `--progress-every` is new and free.
- **The cost, RUN:** one `print(…, file=f, flush=True)` of this line to a file: **15 µs**. At N = 25 over 500 trees,
  20 lines plus a start line is about 0.3 ms, and a Python no-op call per tree about 0.5 ms more: **under 1 ms in a
  fit of at least 1200 s, less than one part in a million.** It sits inside `timed("NFR-476 gbm fit…")` and cannot
  move a reading. Stderr is the only output added.

## Decision points

None open. **The gate form is a question for the lead, with this answer.** `~/gi-pricing-plan.local/handover/seat-brief-common-2026-10-23.md`
item 30, verbatim: "A change whose diff vs origin/main lies ENTIRELY under `docs/` uses the DOCS-ONLY gate … Anything
outside docs/ → the full code gate." No rule exempts a harness: `scripts/**` fires `python.yml`, and PL-2004's SL-2005, the
same class, took a SOLO full gate. **So under the rules, CI plus the bench tests does not suffice; a SOLO full gate is
needed to merge.** It need not stand first: the entry itself allows "carried onto the VM's checkout as a dated exception
if S2 comes first".

**Recommended:** (1) the executor finishes R1 and R2 today, DB-free, on the branch; (2) **the VM carries that file for
S2 by the dated exception**: `scripts/bench-model.py` alone, from the named commit, sha256 quoted before S2, S2's record naming
the tree plus that one file (the gate and D's window hold gate-1, so a merge before 08:45 is not to be counted on); (3) the
merge rides the chain before Thu 12, **folded onto T's or LAST-2's `scripts/` gate** to spend no gate of its own, if the
maintainer allows, else its own. The VM is not this plan's: nothing here touches it.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's merge tree. Items 1 and 2
apply to this plan; A1 to A8 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing line except check
   31 / check 32 lines naming working ids 8347, 8348 or 8349. After the mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no line that stands for a
   set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists `scripts/bench-model.py`,
  `backend/tests/test_bench_model_progress.py`, LG 8349 and the mint's files. **Nothing under `packages/`.**
- **A2. Red first, by cause.** LG 8349 quotes T1 failing because the stderr holds no progress line, on a stub
  `progress_lines` that appends no callback. A `NameError` is not the red.
- **A3. The line.** T1 green: on a 6-round train with `every=2`, stderr holds a start line and lines at trees 2, 4, 6,
  each matching the format below, `trees` rising, `rows_per_s` > 0.
- **A4. The projection.** T2: `eta_s` is `elapsed_s * (total - trees) / trees`, on a stubbed clock.
- **A5. The model is unchanged.** T3: `Booster.save_raw()` from one small seeded fit, with and without the callback, are
  byte-identical.
- **A6. Stdout is unchanged.** T4: nothing of the line reaches stdout, and `xgboost.train` is restored after the context,
  on an exception too.
- **A7. A capped run leaves a rate.** LG 8349 quotes `timeout 20 uv run python scripts/bench-model.py --only gbm --rows 200000
  --factors 10 --rounds 500 --progress-every 5`, by a lead-granted run if the box is held, with rc 124 and at least one line.
- **A8. The gate and the close.** As Decision points rules; every rc quoted. There is no finding to close here; **the LG
  Audit section, with the lead's adoption, lands in the audit's own commit**, and `docs/INDEX.md` is regenerated after the
  closing acts (common seat brief, item 17). The new NFR-476 finding (FD 8350) stays with batch 11.

## Global Constraints

- **G1. Nothing under `packages/` changes:** the fit path is what is being measured.
- **G2. Stderr only.** `flush=True`, so a killed process has written every line.
- **G3. Readings already taken stand.** A flag of 0 turns the line off, for a run that wants the old bytes.
- **G4. Red first, by cause. No test is weakened** (common seat brief, item 13).

## Needs

No DB, no Redis, no docker. Tests are DB-free through `~/gi-pricing-plan.local/handover/run-small.sh`. A7's 20 s of CPU, never
beside a timed stage. **Nothing on the NFR VM from this slice.**

## Tasks

### SL 8348 — the progress line

**The row.** One `sonnet` executor. Requirement: NFR-476 (read: the harness that measures it). **Size:** 1 h. SOLO gate as above,
not counted. **Before Fri 6 Nov 2026 08:45** on the branch; merged before Thu 12 Nov 2026.

**R1 — red first.** New `backend/tests/test_bench_model_progress.py`, `pytestmark = pytest.mark.req("NFR-476")`, loading a copy of
the script by `importlib.util.spec_from_file_location` as `test_bench_rating_header.py` does (`monkeypatch.setitem` on
`sys.modules`, for `@dataclass`), running a 6-round `xgb.train` on 50 synthetic rows with `nthread=1`. T1 to T4.

**R2 — green.** In `scripts/bench-model.py`, beside `timed`:

```python
class _Progress(xgb.callback.TrainingCallback):
    """One stderr line every `every` trees, so a capped run leaves a rate (NFR-476; the entry
    2026-11-05 10:14:38 GMT). Reads the clock and nothing of the model; `False` means continue."""

    def __init__(self, every: int, rows: int, total: int) -> None:
        self.every, self.rows, self.total = every, rows, total
        self.started = time.perf_counter()

    def _line(self, trees: int) -> None:
        elapsed = time.perf_counter() - self.started
        rate = self.rows * trees / elapsed if trees else 0.0
        eta = elapsed * (self.total - trees) / trees if trees else 0.0
        print(
            f"bench-model progress: elapsed_s={elapsed:.1f} trees={trees}/{self.total} "
            f"rows_per_s={rate:.0f} eta_s={eta:.0f}",
            file=sys.stderr, flush=True,
        )

    def before_training(self, model: Any) -> Any:
        self._line(0)
        return model

    def after_iteration(self, model: Any, epoch: int, evals_log: Any) -> bool:
        if (epoch + 1) % self.every == 0:
            self._line(epoch + 1)
        return False


@contextmanager
def progress_lines(every: int) -> Iterator[None]:
    """Append `_Progress` to every `xgb.train` of the run. `pricing_core` is untouched: its fit
    is what is measured, and it looks `xgb.train` up at each call."""
    if every <= 0:
        yield
        return
    original = xgb.train

    def train(params: Any, dtrain: Any, *args: Any, **kwargs: Any) -> Any:
        total = int(kwargs.get("num_boost_round", args[0] if args else 10))
        extra = _Progress(every, dtrain.num_row(), total)
        kwargs["callbacks"] = [*(kwargs.get("callbacks") or ()), extra]
        return original(params, dtrain, *args, **kwargs)

    xgb.train = train  # type: ignore[assignment]
    try:
        yield
    finally:
        xgb.train = original  # type: ignore[assignment]
```

`main`: `--progress-every`, type `int`, default 25, help naming this plan; the phase dispatch runs inside `with
progress_lines(args.progress_every):`. If `xgb` is a local import at `:470`, it moves to the top with the others: read at R1.
`uv run ruff check .` and `ruff format --check` on the two files, rc quoted (common seat brief, item 16).

### Write set

`scripts/bench-model.py`, `backend/tests/test_bench_model_progress.py`, LG 8349 under `docs/ledgers/`; at the mint, the SL 8348 row in
`docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`.

### Files shared with other groups

None. **Safe in parallel with every group.**

## Hand-off (not this plan's writes)

The gate form, the dated exception and its sha256 on the VM: the maintainer and the lead. The row and the mint: the lead. The LG: the
executor. The audit: the slice's auditor. FD 8350 and the 90-min run: batch 11 and S2.

## Self-review

1. **Every cite was read** at `2f108b1e`; the cost and the version were run. 2. **Requirements by id**, no range. 3. **No placeholder.**
4. **The red is by cause.** 5. **The gate answer quotes its rule,** and says the rules do not allow less. 6. **Calendar:** 6 Nov 2026 is a
Friday, by `date -d`, and 12 Nov a Thursday.
