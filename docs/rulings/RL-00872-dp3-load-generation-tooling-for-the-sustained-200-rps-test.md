---
id: RL-872
family: ruling
title: DP3: load-generation tooling for the sustained-200 rps test
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slice1-rulings.md
---

# WK-671 Slice 1 decision-point rulings — the eight decisions that block Tasks 1.2 to 1.5 (2026-08-29)

**What this is.** `.claude/roles/decision-maker.md` requires every decision point to be
pre-resolved *before* its slice starts. WK-671 Slice 1 is the pilot for the RFC-840/841
process adoption (`docs/process/delivery-process.md` §14, step 6), so this is the record
that clears it. The frozen plan is
[`../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`](../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md); the recovered options and
recommendations behind three of the decisions below are
[`../plans/PL-00851-wk-671-five-decision-points-recovered.md`](../plans/PL-00851-wk-671-five-decision-points-recovered.md).
A frozen plan is never edited — this is its dated sibling, the same treatment
[`RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md`](RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md) gave Rulings 1–5.

**Numbering continues that record at 6.** Rulings 1–5 are its; nothing here reuses a
number, for the same reason `CLAUDE.md` §5 gives for requirement ids. A ruling is cited as
"Ruling N" plus the file it lives in, never by bare number.

**Mints no `FR-`/`NFR-`/`OQ-` id.** Every requirement id below is already defined in
`docs/specs/`. One error code is appended to an existing owned-code block — error codes are
a separate namespace from `FR-`/`NFR-`/`OQ-` and this paragraph does not cover them.

**Every literal, line number, route, signature and requirement id below was grepped or read
against `origin/main` at `7b8473a`** before being written down. Where a claim recovered from
an earlier document turned out to be wrong against that tree, this record says which claim
is wrong in its own first sentence rather than hedging — `docs/process/delivery-process.md`
§15.

**Three of the first six were on no list, and a seventh arrived after they were filed.**
RL-878 was raised by the planner during execution, which is the honest shape of
pre-resolution: it catches most of them early and not all of them. Rulings 7, 8 and 10's *subject* was named in
the recovery document; Rulings 7 and 8 as filed are new decisions found by reading the
shipped source that Tasks 1.2, 1.3 and 1.4 will actually build against. That is what
pre-resolution is for, and it is also the honest state of the frozen plan: it carries an
unresolved "or" (Task 1.2) and one factual claim about an existing function that does not
hold (Task 1.3).

---

## RL-872 — DP3: load-generation tooling for the sustained-200 rps test

**The decision, restated.** DP3 (`2026-08-29-w11-scoring.md:199-206`) asks which tool
generates load for the sustained-200 rps measurement `NFR-489`
(`../specs/03-rating-engine.md:777`) and `NFR-454` (`../specs/00-overview.md:518`) both
state, and which `../roadmap.md:146` schedules as a Phase 2 WK-671 test. Options as the plan
states them: **(a)** add `locust`; **(b)** hand-roll `asyncio` + `httpx` following the
`scripts/bench-model.py` / `scripts/bench-data.py` convention; **(c)** shell out to an
external CLI (`hey` / `wrk` / `k6`).

**Ruled: (b).**

Rationale, and two corrections to the plan's own framing of it:

- **(b) adds no dependency, and the plan's "(no new dependency)" gloss is right for a
  reason it does not give.** `httpx` is already a root dependency
  (`../../pyproject.toml:24`, present because FastAPI's `TestClient` is an `httpx`
  transport) and a backend one (`../../backend/pyproject.toml:18`). `asyncio` is stdlib.
  So (b) triggers neither of `.claude/skills/spec-change`'s coupled obligations — no `03`
  §8 row, no `../skills-map.md` row. **(a) triggers both**, and (c) trades a Python
  dependency for an unpinned system one that CI does not install, which is worse for a
  measurement that has to be reproducible to be worth taking.
- **Correction: `bench-model.py` and `bench-data.py` use no `asyncio` and no `httpx`.**
  Both are stdlib-only — `time.perf_counter` for timing and a daemon `threading.Thread`
  sampler for CPU occupancy (`../../scripts/bench-model.py`, 785 lines;
  `../../scripts/bench-data.py`, 307 lines). What (b) inherits from them is their
  **governance** convention, stated verbatim in `bench-data.py`'s docstring and quoted back
  by `bench-model.py:4-9`: *"Not a CI gate. A timing assertion on a shared runner fails for
  reasons that have nothing to do with the code, and a check that fails randomly teaches
  everyone to re-run it. This produces numbers for a workstream closure record instead,
  where a human reads them once against the budget."* That convention binds: the load
  generator is **not** a CI gate, and its result is a dated note under `docs/research/`.
  It does not follow that their library set binds, and stating the convention as
  "asyncio + httpx following bench-model.py" conflates the two.
- **Correction: Task 1.5 needs no load generator at all, and this ruling does not give it
  one.** The plan tags Task 1.5 `[depends on DP3]` and the sequencing table repeats it, but
  Task 1.5's own exit criteria measure `score_one` directly — *"no HTTP, no FastAPI"*
  (`2026-08-29-w11-scoring.md:452`). A single-process p99 over a loop needs `perf_counter`,
  not a load generator. **DP3 binds Task 2.1**, which is where the plan itself puts the
  sustained-200 rps measurement (`:439-442`, `:479`). Task 1.5 is unblocked either way; what it
  takes from this ruling is the governance convention above, which it was already told to
  follow.

**Disposition.** No spec change. `scripts/bench-rating.py` (Task 1.5) is stdlib-only and
follows `bench-model.py`'s shape. The sustained-load driver (Task 2.1) is `asyncio` +
`httpx` in the same `scripts/` convention, not a CI gate, its result a dated
`docs/research/` note. No `03` §8 row and no `../skills-map.md` row is owed by either.

**Acceptance test — the thing that must be true, stated as the violation.** If a later PR
adds `locust`, `k6`, `hey` or `wrk` to any `pyproject.toml`, `uv.lock`, CI workflow or
setup instruction for this measurement, this ruling has been overridden and needs a
successor record. As of `7b8473a` none of the four appears anywhere in the repository
except in DP3's own two option lines.

---
