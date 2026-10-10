---
id: PL-1577
family: plan
kind: map
title: WK-1178 — R6, the exit demo's dislocation portfolio is a 20,000-policy sample of the freMTPL2 book built by the seed's existing sampler: a dated delta to PL-1544
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
owner: planner
tree: 61e2a8d9d06087cadd3760e9668b3caff881b85c
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1544, PL-1525, PL-1371, SL-1526, SL-1527, WF-699, FR-263, FR-266, RL-1521, LG-1417, PL-1574, FD-1573, FD-1576]
---

# PL-1577 — WK-1178, R6: the dislocation portfolio is a 20,000-policy sample (delta to PL-1544)

*Disclosure: drafted under working id 9452; minted as PL-1577 on 2026-10-10, in the D5 batch mint PR.*

> **For agentic workers:** this is a **dated delta** under Lean P2 L5 (`document-ids.md` §1.6,
> PL row: *"a change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's
> plan"*). It does not replace
> [`PL-1544`](PL-01544-wk-1178-exit-demo-slice-b-the-scripted-wf-699-journey-over-http-to-a-served-page-leaf-plan.md)
> (exit-demo slice (b), frozen since its merge) or
> [`PL-1525`](PL-01525-wk-1178-exit-demo-slice-a-the-real-fremtpl2-rating-algorithm-in-the-seed-leaf-plan.md)
> (slice (a)); it `relates:` both. **Read `PL-1544` §Goal, §Size and its journey table rows
> D6–D8 first, then this file**; where they differ, this file is the later statement. The
> executor of the carrying slice binds `python-test`, `test-driven-development`, `dev-commands`
> and `git-hygiene`, and is spawned from `.claude/roles/executor.md`.

Filed under the working id named in the disclosure line above, reserved by the lead. Written 2026-10-10 by the planner
(planner-r6a1) on the lead's brief `brief-planner-r6-a1-spec-2026-10-10.md`, deliverable 2.
Evidence read at `origin/main` `61e2a8d9` (2026-10-10 00:31 BST).

## The ruling this delta records

The maintainer's ruling, by delegation, `to-lead.md` entry **"2026-10-10 00:27:18 BST —
RULING: R6 = (A1), a 20,000-policy demo portfolio built by the seed's existing sampler; (D) is
the named fallback; (B) and (C) rejected"**. A repository reader cannot resolve a local entry
(RFC-777), so its five conditions are quoted here verbatim, numbered as there:

> 1. SPEC FIRST (§0), in one docs change BEFORE the seed code: a. WF-699 D6 (and :30) says the
> demo portfolio is a 20,000-policy sample of the freMTPL2 book, built by the seed, named as a
> sample. b. WF-699:87 (D7, "1.28 M policies") is corrected by a dated line to the real book
> size (678,013 rows / ~677,442 policies, quoted from the seed), because it is wrong at every
> option. c. A dated DELTA to PL-1544 (a new PL with relates:, L5; PL-1544 is frozen) records
> the R6 ruling and the sample. This rides D5, or the next docs batch, with PL 9447.
> 2. HONESTY: the demo script and the demo's README state that the dislocation and attribution
> run on a 20,000-policy sample, and point to PL 9447 (dislocation) and FD 9451 (attribution)
> for full-book cost. No demo text implies full-book performance.
> 3. REPRODUCIBLE: the sampler takes a FIXED seed and a fixed size, both named in the WF-699
> text. The same seed DB gives the same 20,000 policies every run. The seed change asserts that.
> 4. The seed change (examples/ only) lands in the slice that builds the seed (PL-1544 slice (a)
> / SL-1526) or a WK-1178 slice. The lead names which in the dispatch, with its compile.py
> position if any.
> 5. FD 9446 → LOW and FD 9451 → MEDIUM, as the auditors' conditional re-rates. The full-book
> costs stay OWNED, measured targets (PL 9447; FD 9451's owner named), not demo-day steps.

[Bracketed note on the quoted block: PL 9447 is minted as PL-1574, FD 9451 as FD-1576, FD 9446 as FD-1573.]

And its fallback, verbatim: *"(D) is the named FALLBACK if (A1) fails at its proving run:
pre-run the full book and show the persisted run. It would need its own dated line (RL-1521 is
silent; your grep)."* FR-263 sets no size, so no FR changes (the ruling's first paragraph).

## Goal

Record, as a dated delta to `PL-1544`, the maintainer's (by delegation) R6 ruling and the
sample it adopts, so that the exit demo's D6 dislocation run and its D7 attribution run go over a
reproducible 20,000-policy sample of the freMTPL2 book, built by the seed and named as a sample,
while ingestion, validation and the 7-factor GLM stay on the full book. The ruling is the entry
quoted above (00:27:18: *"R6 = (A1), a 20,000-policy demo portfolio built by the seed's existing
sampler"*), and the decision points below are ruled by the entry **"2026-10-10 00:34:03 BST —
RULINGS on PL 9452 (draft/r6-a1-spec @bb9e9fa4): DP-1 yes, DP-2 yes (condition 3 re-read), DP-3
yes; SL-1526 carries; FD 9451 owner WK-673. The DM seat may apply the WF-699 text"**, which says,
verbatim:

> DP-1 YES: a separate 20,000-policy portfolio DV for dislocation and attribution; the GLM stays
> fitted on the full book (the model stays real).
> DP-2 YES. My condition 3 ("fixed seed") is RE-READ as its intent, reproducibility: fixed size +
> pinned input + the sampler's deterministic every-n-th rule, named in WF-699 and asserted (same
> 20,000 rows every run). One addition: a systematic sample over an ORDERED file can be
> unrepresentative, so the seed change writes a short comparison (sample vs book) into its LG for
> a few rating columns (exposure mean, claim frequency, and two factor distributions, e.g. region
> and vehicle age). If any differs materially, report it to me before the demo text is final. No
> new code beyond that check.
> DP-3 YES: assert the measured count exactly.
> Carrying slice: SL-1526 (no compile.py position).
> FD 9451's owner: WK-673 (the attribution engine is S3's), discharge before WK-673's Work close
> or carried by name at P2's close. FD 9446/PL 9447 stays WK-1178.

[Bracketed note on the quoted block: PL 9452 is minted as this file, PL-1577; FD 9451 as
FD-1576; FD 9446 as FD-1573; PL 9447 as PL-1574.]

Done for this delta when the four Tasks below have landed and its Acceptance Standard passes:
WF-699 names the sample at D6 and `:30` and carries the dated D7 correction (Task 1); the seed
ingests the portfolio as its own Dataset Version in `SL-1526` and asserts the same 20,000 rows
every run and their measured count (Task 2); the demo text says "20,000-policy sample" and points
to `PL-1574` and `FD-1576` for full-book cost (Task 3); and `FD-1573` and `FD-1576` carry the
re-rates (Task 4). No demo text states or implies a full-book rate.

## What changes in PL-1544

| PL-1544 site (at `61e2a8d9`) | Was | Now |
|---|---|---|
| §Size, `:468-470` | *"The one-command run is the full seed (`--rows 20000` in rehearsal; the full 678,013 rows on demo day)."* | The one-command run is still the full seed on demo day for ingestion, validation and modelling. **The D6 dislocation run and its D7 attribution run over the 20,000-policy portfolio sample** (DP-1), never over the full book. |
| journey table, D6 (`:364`) | `POST /dislocation-runs` → `202; run persisted`; names no Dataset Version | `DislocationSpec.portfolio_dataset_version_id` (`packages/model-schema/src/model_schema/dislocation.py:41`) is the sample's Dataset Version, which the seed creates and records (DP-1 (b)). |
| the journey's printed output and `examples/fremtpl2/README.md` | nothing about portfolio size | the honesty text of condition 2 (Task 3). |

**The book's size, quoted, not derived.** `examples/fremtpl2/seed.py:5` at `61e2a8d9`:
*"`uv run python examples/fremtpl2/seed.py            # full 678 013 rows`"*; `seed.py:13`:
*"571 of freMTPL2's rows carry an exposure above 1.0"*, which the v2 recipe drops
(`seed.py:recipe`, `filter_rows`, `:84-91`). The v2 count is measured, in `LG-1417`'s B4 run
(`docs/ledgers/LG-01417-…md:533`): *"version 2 holds 677,442 rows"*.

## The sampler, read at `61e2a8d9`

`examples/fremtpl2/seed.py`, `build_csv(rows: int | None) -> bytes` (`:95`), sized by the
seed's `--rows` argument (`:673`, *"Seed a sample rather than all 678 013"*); `scripts/demo.py`
forwards `--rows` (`:228-229`). The sampling lines, verbatim (`:131-132`):

```python
        step = max(joined.height // rows, 1)
        joined = joined.gather_every(step).head(rows)
```

**It has no random seed parameter.** It is a systematic every-`step`-th-row sample, chosen
deliberately over `head` because the file is ordered by claim count (`:127-130`). It is
deterministic given its input, and the input is pinned: `examples/fremtpl2/fetch.py:10`,
*"Checksums are pinned."* (sha256, `fetch` at `:38`). Condition 3's "FIXED seed" therefore has
no parameter to name on the existing function — DP-2.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | Which Dataset Version is the sample? | (a) `--rows 20000` for the whole seed: no new code, but the 7-factor GLM that WF-699 A1–A2 seeds from is then fitted on 20,000 rows too, and v2 holds 20,000 less the sampled rows above exposure 1.0. (b) the seed ingests the full book as today (v1 fails, v2 validated, models fitted on v2) **and** ingests one more Dataset Version, the portfolio, from `build_csv(20000)` through the v2 recipe, recording its id for D6 | **(b).** The ruling names the sample as the *demo portfolio*, not the modelling data; `FD-1576`'s handler reads exactly `spec.portfolio_dataset_version_id` (its `:29`), so a separate version is the seam the code already has. (a) silently shrinks the model the demo shows | scope | yes — the carrying slice | the 00:34:03 entry: *"DP-1 YES: a separate 20,000-policy portfolio DV for dislocation and attribution; the GLM stays fitted on the full book (the model stays real)."* |
| DP-2 | What is condition 3's "FIXED seed" on a sampler that has none? | (a) the reproducibility is the existing sampler's determinism: fixed size 20,000, `step = max(height // rows, 1)`, over the sha256-pinned input; WF-699 names those, and the seed asserts the same `IDpol` set every run. (b) a seeded random draw (`DataFrame.sample(n=20000, seed=<k>)`): has a seed to name, but it is not "the seed's existing sampler" the ruling adopts | **(a)**, with a dated line from the lead confirming that "FIXED seed" reads as the fixed size plus the pinned input. The ruling's text and the function disagree; that is not the planner's to settle | decision point | yes — the WF-699 text | the 00:34:03 entry: *"DP-2 YES. My condition 3 ("fixed seed") is RE-READ as its intent, reproducibility: fixed size + pinned input + the sampler's deterministic every-n-th rule, named in WF-699 and asserted (same 20,000 rows every run)."* |
| DP-3 | The size: 20,000 sampled rows, or 20,000 validated policies? `build_csv` samples before the v2 recipe drops exposure above 1.0, so the portfolio version may hold fewer than 20,000 | (a) the label says "20,000-policy sample" and the seed asserts the portfolio version's validated row count against a constant measured at the proving run; every demo text that gives a count quotes that constant. (b) sample from the filtered book so the count is exactly 20,000 (moves the filter into `build_csv`, against the seed's story that the platform's recipe fixes it, `seed.py:12-15`) | **(a).** Measured, not derived; no demo text claims a count the seed did not assert | fact | no — Task 2 measures it; default (a) | the 00:34:03 entry: *"DP-3 YES: assert the measured count exactly."*; the count is the proving run's ledger line |
| DP-4 | Which slice carries the seed change (condition 4)? | (a) **SL-1526** (slice (a), leaf plan `PL-1525`). (b) a new single-row WK-1178 slice | **(a).** `PL-1544` assigns the file to slice (a), `:455-457`: *"`examples/fremtpl2/model.py`, `seed.py` and `algorithm.py` (slice (a)'s)"*; `PL-1525`'s file table already edits `seed.py:run` (its `:486`). A separate slice would be serial with SL-1526 on `seed.py:run` anyway. **compile.py position: none** — `PL-1525`'s file table edits no `compile.py` (its only `compile.py` mentions, `:236` and `:769`, are about `import zen`), and the lead's inventory lists the `compile.py` serial set without demo (a) (`~/gi-pricing-plan.local/handover/p2-inventory-2026-10-09.md:180`, local). SL-1526's own row scopes "the real freMTPL2 rating algorithm in the seed"; this delta adds the portfolio to it | the lead (condition 4: "The lead names which in the dispatch") | yes — Task 2 | the 00:34:03 entry: *"Carrying slice: SL-1526 (no compile.py position)."* |

## Tasks

**Task 1 — spec first (condition 1 a–b), the decision-maker's.** WF-699 is owned by the
decision-maker via `spec-change` (`document-ids.md` §1.6, WF row), not the planner. Its edits —
D6 (`:86`) and the precondition row (`:30`) name the portfolio as a 20,000-policy sample built
by the seed (sampler, size and DP-2's reproducibility basis named); D7 (`:87`) carries a dated
correction from "1.28 M policies" to the book's quoted size — land in the same docs change as
this file, before Task 2.

**Task 2 — the seed change, in the slice DP-4 names (`examples/` only).**
- [ ] A test in `examples/fremtpl2/test_seed.py` asserts `build_csv(20000)` returns the same
  `IDpol` set on two calls, and that set's row count; seen red first.
- [ ] `seed.py:run` ingests the portfolio version (DP-1 (b)) through the v2 recipe and records
  its id where the journey reads it.
- [ ] The proving run: `uv run python scripts/demo.py` (full seed), then D6–D7 over the
  sample; the ledger records wall time, the portfolio's validated row count (DP-3) and exit code.
  If it fails, stop: the (D) fallback needs its own dated line before anything is built for it.

**Task 3 — honesty (condition 2), in slice (b) (`SL-1527`) and the README.** The journey's D6
and D7 output and `examples/fremtpl2/README.md` say "20,000-policy sample" and point to
`PL-1574` (full-book dislocation cost) and `FD-1576` (full-book attribution cost). No demo text
states or implies a full-book rate.

**Task 4 — the re-rates (condition 5), the auditors' and the lead's.** `FD-1573` → LOW,
`FD-1576` → MEDIUM. The full-book costs stay owned, measured targets: dislocation by `PL-1574`;
attribution by `FD-1576`'s owner, **WK-673** (the 00:34:03 entry: *"FD 9451's owner: WK-673 (the
attribution engine is S3's), discharge before WK-673's Work close or carried by name at P2's
close."*; FD 9451 is minted as FD-1576). Neither is a demo-day step.

## Acceptance Standard

1. WF-699 at the batch tree: `git grep -n '20,000' -- docs/workflows/WF-00699-*.md` hits D6 and
   the `:30` row; the D7 row keeps "1.28 M" visible and carries a dated correction quoting
   678,013 and 677,442 with their sources.
2. `uv run pytest -q examples/fremtpl2/test_seed.py` passes, and includes the same-`IDpol`-set
   assertion of Task 2, seen red first in the slice's ledger.
3. The carrying slice's ledger records the proving run's command, wall time, exit code and the
   portfolio version's validated row count.
4. `git grep -n -i 'sample' -- examples/fremtpl2/README.md examples/fremtpl2/journey.py` shows
   the condition 2 text naming `PL-1574` and `FD-1576`.
5. `FD-1573` and `FD-1576` carry the re-rates, and `FD-1576`'s full-book target names an owner.
6. `python3 scripts/audit-docs.py` passes on the batch tree that carries this file.
7. `SL-1526`'s ledger carries the sample-vs-book comparison of the 00:34:03 entry, verbatim:
   *"a systematic sample over an ORDERED file can be unrepresentative, so the seed change writes
   a short comparison (sample vs book) into its LG for a few rating columns (exposure mean, claim
   frequency, and two factor distributions, e.g. region and vehicle age). If any differs
   materially, report it to me before the demo text is final."* The ledger shows the exposure
   mean, the claim frequency and two factor distributions for both the sample and the book; if
   any of them differs materially, it also records that the difference was reported before the
   demo text was final.
