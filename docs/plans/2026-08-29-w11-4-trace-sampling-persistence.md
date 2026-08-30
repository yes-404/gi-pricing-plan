# W11 Slice 4 — trace sampling, the row-plus-blob store, and the retention floor

> **For agentic workers:** REQUIRED SUB-SKILL: use `subagent-driven-development`
> (recommended) or `executing-plans` to implement this plan task-by-task, plus
> `test-driven-development` and `git-hygiene` — the three skills
> [`.claude/roles/executor.md`](../../.claude/roles/executor.md) makes mandatory for this
> role. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist the `Trace` objects Task 1.4 already builds — sampled at 1 % plus 100 % of
declines and errors, stored as a thin queryable row beside a blob body, readable through
`GET /api/v1/traces`, and protected by a floor that refuses early deletion.

**Architecture:** Four tasks. **4A** is the storage shape — the row, the migration, and the
write that produces row and body from one serialisation. **4B** is the sampling decision, a
pure function, applied on the real-time path only. **4C** is the read route and its access
control. **4D** is the NFR-RATE-12 capacity projection, which is a measurement and not a
guess. 4A → 4B → 4C is a chain; 4D needs 4A.

**Tech Stack:** SQLAlchemy 2.x async + Alembic for the row; the content-addressed blob store
(`backend/src/app/platform/blobs.py`) for the body; FastAPI for the read route;
`model_schema.scoring.Trace` as the artifact, already shipped.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) — §3.7 (FR-RATE-41),
§3.8 (FR-RATE-42), §4.5 (the `Trace` shape), §5.1 (the `/traces` row), §9 (NFR-RATE-11,
NFR-RATE-12). Retention floor: [`../specs/00-overview.md`](../specs/00-overview.md) NFR-OVR-6.
Blob store: [`../specs/07-platform.md`](../specs/07-platform.md) FR-PLAT-18, 19, 20.

**Slice source:** [`2026-08-29-w11-scoring.md`](2026-08-29-w11-scoring.md), Slice 4. **That
file is frozen and is not edited by this one.**

**Rulings this plan rests on, cited by number and not re-argued:**
[`2026-08-29-w11-slices-3-4-rulings.md`](2026-08-29-w11-slices-3-4-rulings.md) Rulings 23 and
25. Ruling 23 rules the storage shape *and corrects the retention reasoning the recovery
document proposed*; Ruling 25 rules that batch contributes nothing to this stream.

**Process:** [`../process/delivery-process.md`](../process/delivery-process.md) §6, §8, §9.

**Highest ids in use, re-derived at `d6505e9` by scanning
[`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) and
[`../open-questions.md`](../open-questions.md):** FR-RATE-65, NFR-RATE-14, OQ-RATE-7.
Next free: `FR-RATE-66`, `NFR-RATE-15`, `OQ-RATE-8`.

**This plan mints none of them**, and `OQ-RATE-8` in particular is **deliberately not taken** —
Ruling 25 examined the batch-sampling question this slice was expected to raise it for and
found the suite already answers it. It cites ids that already exist and registers no new error
code.

---

## Corrections after filing (2026-08-30, at `25c5688`)

**One statement in this plan is wrong, and it appears twice.** Task 4A, merged at `25c5688`
(PR #480), falsified it. What was believed is preserved above rather than deleted, per
[`README.md`](README.md): no Steps, Files or Acceptance text in this file has been edited to
agree with the repository, and this section is additive only.

**Why in the plan rather than beside it.** [`README.md`](README.md)'s rule — *"a filed plan is
a record, not an instruction"* — governs a plan whose execution is finished. Tasks 4B, 4C and
4D have not run, so this file is still being read as an instruction set, and
[`2026-08-29-w11-3-batch-scoring.md`](2026-08-29-w11-3-batch-scoring.md)'s own corrections
section gives the reason: *"a plan is an instruction set and an executor who reads a wrong step
does the wrong thing"*. This slice's other correction —
[`2026-08-30-w11-4-always-capture-correction.md`](2026-08-30-w11-4-always-capture-correction.md),
resolved the same day by Ruling 35 — was filed as a sibling document instead. **Both are live
and an executor must read both**; that record carries a binding constraint on Task 4B which
this section does not repeat.

### Correction 1 — this slice does register a new error code

The header block above says this plan *"cites ids that already exist and registers no new error
code"*, and the F29 row in *The register rows this slice must honour* repeats it. **Both are
wrong.** Task 4A registered `TRACE_RETENTION_FLOOR` (409) in both places a code must appear:
`backend/src/app/errors.py:332`, and `03`'s owned-code block at
[`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) `:628`. It is raised by
`app.platform.traces.delete_trace` (`traces.py:126`) when a delete falls inside NFR-OVR-6's
≥ 13-month floor.

**It is a wrong prediction, not a broken rule, and Task 4A is not a deviation.** Three reasons,
in the order that decides it:

1. **The plan requires the behaviour that requires the code.** Acceptance criterion 4 and Task
   4A's *Interfaces — Produces* both demand a deletion path that *refuses* inside the floor. In
   this codebase a typed refusal is a `PlatformError` carrying a registered code — the precedent
   Task 4A followed is `DATASET_VERSION_IMMUTABLE` (`backend/src/app/platform/datasets.py:537`)
   and `MODEL_IMMUTABLE` (`backend/src/app/platform/modelling.py:816`), both 409 refusals of an
   immutability rule. Read as a rule, the sentence forbids what this plan's own acceptance
   standard mandates; read as a prediction, it is simply mistaken. Only the second reading is
   internally consistent.
2. **It is stated in the indicative, inside a derivation, not as a prohibition.** The F29 row
   uses it as a premise — *"so it neither worsens nor discharges it"* — and this plan states its
   real prohibitions imperatively (*"Must NOT touch"*, *"the budget must not assume it"*, *"Do
   not let that serialise the whole slice"*).
3. **Nothing reserves an error code the way an id is reserved.** The id half of the same
   sentence is a rule because `scripts/audit-docs.py` enforces the `Next free:` marker; error
   codes have no equivalent machinery, which is F29's substance.

**The F29 row's conclusion survives its premise.** F29 is that nothing checks error-code
registration in either direction — a code owned by a spec and absent from `errors.py`, or a code
in `errors.py` owned by no spec. Task 4A registered both sides, so it creates no instance of
either failure mode: the row still neither worsens nor discharges F29, for a different reason
than the one given. **No new register row is owed for this.** What Task 4A did not do is make
anything *check* that registration — nothing does, and that is F29, already open and owned.

### Correction 2 — Task 4C's exclusion signal is a null environment, not a batch parent

Task 4C Step 3 tells its executor to *"construct the row directly with a batch parent"*. **The
row Task 4A built has no parent field to set.** `ScoringTraceRow`
(`backend/src/app/db/models.py:2033`) carries `workspace_id`, `quote_id`, `rating_version_ref`,
`bundle_hash`, `sample_reason`, `environment`, `blob_sha256` and `created_at` — and no Job
reference. The signal Ruling 25's exclusion must be written against is a **null `environment`**:
the real-time path sets it, and a trace written on request for a `score.batch` Job carries none.
Step 3's test is still the right test and still writable before Slice 3's traces exist —
construct the row with no environment and assert `GET /api/v1/traces` does not return it.

### Not corrected, because they are right as written

- **C2's owed register row.** The `Deployment` parent is still W14's, Task 4A stored the
  environment as a plain string exactly as C2 says, and the row remains owed at the close.
- **Task 4A's *Interfaces — Produces* line.** `write_trace` takes more than a `Trace` and a
  `sample_reason`: also the session, the `BlobStore`, `workspace_id` and `environment`
  (`backend/src/app/platform/traces.py:47-55`). That is a wider interface than the plan
  sketched, not a different one — but a Task 4B caller needs the full signature.

### Filed against a second plan, and deliberately not corrected there

[`2026-08-29-w11-3-batch-scoring.md`](2026-08-29-w11-3-batch-scoring.md) carries the same
sentence and is falsified the same way: its Task 3B (`eda70d6`) registered
`BATCH_ABORT_THRESHOLD_ABOVE_SETTING` and `BATCH_ABORTED`, and that plan's Task 3B likewise
required a *refusal*. All four of its tasks have merged, so it is a finished record and
[`README.md`](README.md)'s rule applies to it without the executor-safety exception used above.
**Both of the two plans that used the sentence were wrong**, which makes it a plan-writing
finding rather than a slip: it is carried to the [`CLAUDE.md`](../../CLAUDE.md) §14 plan review
due at W11's close, not edited into that file.

---

## Acceptance standard for the slice as a whole

`delivery-process.md` §3 requires one that is explicit and testable. Slice 4 is accepted when
**all six** hold, each by a command a fresh reviewer can run.

1. **A sampled trace round-trips.** A scored quote whose sampling decision is *sample* writes
   one row and one blob; reading the row back and fetching its body reproduces a `Trace` equal
   to the one `score_one` returned.
2. **The sampling policy is exact at the boundaries, not merely approximate in aggregate.**
   100 % of declines and 100 % of errors are sampled regardless of rate; at rate `0.0` a quoted
   outcome is never sampled; at `1.0` always. The 1 % default is verified statistically over a
   large N with a tolerance stated in the test, not eyeballed.
3. **The row and the body cannot diverge.** A test proves they are produced from **one**
   serialisation of one object — Ruling 23's second constraint. The discriminating assertion is
   that `quote_id`, `rating_version_ref` and `bundle_hash` in the row equal the ones inside the
   stored body, on a trace where those values are non-default.
4. **The retention floor is enforced on deliberately broken input.** Deleting a trace row
   younger than NFR-OVR-6's ≥ 13-month floor is **refused**. **Overridden if any build reclaims
   a trace blob whose row still exists, or ships an expiry job that deletes rows on a schedule
   shorter than the floor** — Ruling 23's acceptance test.
5. **Traces are access-controlled** (NFR-RATE-11), and **no batch-produced trace appears in the
   production stream** (Ruling 25): `GET /api/v1/traces` returns nothing attributable to a
   `score.batch` Job.
6. **NFR-RATE-12 is projected from a measurement**, not an estimate: the projection uses the
   **actual serialised size** of traces this slice stores, and the note records the shape those
   traces had.

**Not in this slice, and not a gap:** `score_batch` and any batch trace output are Slice 3's;
the `Deployment` parent of a `ScoringTrace` is W14's (see C2); the 99.95 % availability target
is W14's.

## Global Constraints

- **Money is integer minor units or `Decimal`, never `float`** — a `Trace` carries `consumed`
  and `produced` maps that include money values, and re-serialising them must not float them.
- **The row is a projection of the blob, written from the same object** (Ruling 23). Serialise
  once, write both in one operation.
- **No expiry job.** Ruling 23's correction: FR-PLAT-20's GC is a *deletion* mechanism and
  NFR-OVR-6 is a *preservation floor*; they do not compose into "GC-based retention". A
  referenced blob is not a GC candidate at all (`blobs.py:301-305` selects on
  `ref_count == 0`), so the only way to breach the floor is to delete the row early. **The
  guard Slice 4 owes is on row deletion, not on retention scheduling.**
- **Deduplication will not help and the budget must not assume it** (Ruling 23). `TraceStep`
  carries `elapsed_us`, so no two traces are byte-identical even for identical inputs.
  NFR-RATE-12 must be met by the schema and the sample rate alone.
- **A negative test for every invariant introduced**, marked `@pytest.mark.req("<id>")`.
- **Worktree hygiene:** your own worktree, never `git checkout`/`git switch` outside it.
- **The gate, both halves, run locally before every push:**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
```

---

## Verified facts at `d6505e9`

### The artifact already exists and is fully typed

`packages/model-schema/src/model_schema/scoring.py`, all frozen with `extra="forbid"`:

```python
class Trace(BaseModel):
    rating_version_ref: ArtifactRef
    bundle_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    quote_id: str | None = None
    steps: list[TraceStep]
    ladder_reconciled: bool

class TraceStep(BaseModel):
    step_id: str
    type: TraceStepType
    label: str | None = None
    consumed: dict[str, object] = Field(default_factory=dict)
    produced: dict[str, object] = Field(default_factory=dict)
    matched: dict[str, object] | None = None
    violation: dict[str, object] | None = None
    elapsed_us: int = Field(ge=0, default=0)
```

**Three of the four fields Ruling 23's row needs are already in the body** — `quote_id`,
`rating_version_ref`, `bundle_hash`. **Only `sample_reason` is new.** That is the whole reason
for the "one serialisation" constraint: a projection assembled separately from the body it
projects will diverge.

`score_one(bundle, ctx, *, trace: bool = False)` returns a `ScoringResult` whose
`trace: Trace | None` is populated only when `trace=True`. **Slice 4 decides that boolean.**

### What exists, and what does not

| Thing | State at `d6505e9` |
|---|---|
| `Trace`, `TraceStep` | Exist and are shipped types — `model_schema/scoring.py:157`, `:137` |
| Any trace persistence | **None.** `git grep -ln "ScoringTrace\|scoring_trace\|trace_sampling\|sample_reason" -- packages backend` returns nothing (Ruling 23 ran this at `d614f24`; re-run it at your own commit) |
| `GET /api/v1/traces` | No route. Specified at `03` §5.1 as *"Sampled **production** traces (FR-RATE-42)"* |
| Blob store | `backend/src/app/platform/blobs.py`, `class BlobStore` at `:98`. Methods are `put(session, content, media_type) -> BlobRef` (`:130`), `open(ref)` (`:181`), `read(ref)` (`:208`). **There is no `get`** |
| Blob GC | `blobs.py:301-305` selects `BlobRow.ref_count == 0` and `created_at < cutoff`; `retain`/`release` at `:339-350`; grace period from `retention.blob_gc_grace_days`, default 30 (`platform/settings.py:194-201`) |
| Any `JobKind` beginning `TRACE` | **None.** The only `TRACE_` symbols are request-tracing constants — `observability/trace.py:31` `TRACE_ID_PATTERN`, `middleware.py:26` `TRACE_HEADER` — an unrelated meaning a grep for "trace" surfaces first |
| `DislocationRun.largest_movers_blob` | Specified at `03` §4.6 (`:472`) as the row-plus-blob precedent. **It exists in the spec and in no `.py` file** — the frozen map cited it as a code precedent and Slice 1's correction C4 found otherwise. The real backend precedent is `backend/src/app/worker/rating_handlers.py`'s blob write |

### The register rows this slice must honour

`delivery-process.md` §9. All rating-bearing rows are listed; a row skipped silently is
indistinguishable from one that does not exist.

| Row | Bearing on Slice 4 |
|---|---|
| `03 rating surface (F8)` | The phase-boundary row; W11 discharges its scoring quarter |
| `NFR-RATE-13/14 (F-W9-1)` | Slice 1's and Slice 2's halves. Not this slice's |
| `FR-RATE-61 (F-W9-2)`, `FR-RATE-25 (F-W9-3)` | W13's and Task 1.2's. Not this slice's |
| `03 rating shapes vs hand-authored contracts (F27)` | Owner decided (Ruling 29): the §14 review at W11's close. **Bears indirectly** — if 4A gives the trace *row* a published contract, it joins that comparison; Ruling 23 says the row needs no published contract unless the slice finds it does |
| `Error codes across the spec/code boundary (F29)` | Open, owned. This slice registers no new error code, so it neither worsens nor discharges it |
| The six W10 rows | W10's and W15's. Not this slice's |

**Nothing in the register blocks Slice 4.**

---

## Corrections to the frozen map

**C1 — the map's Slice 4 line reads as a settled mechanism and was not one.** It says *"sampling
policy … applied to Task 1.4's already-captured `Trace` objects; persistence to the blob
store"*. The row-plus-blob split, and the retention question underneath it, were an unruled
recommendation until Ruling 23.

**C2 — a `ScoringTrace`'s parent is a Deployment, and Deployment is W14's.** Ruling 23 names a
deferral the map does not: [`../specs/00-overview.md`](../specs/00-overview.md) §4.1's
entity-relationship map (`:261`) reads `Deployment ──< ScoringTrace (sampled) ──<
MonitoringAggregate`. **Slice 4 builds the artifact and its storage shape; the row carries the
parent it can resolve** — the rating version reference, the bundle hash, and the environment as
a plain string — gaining the Deployment reference in W14. Booked the same way as Ruling 14's
deferral: a register row, which is the lead's to write at the close.

**C3 — the retention mechanism the recovery document proposed is backwards, and building it
would have breached the floor it was meant to honour.** Ruling 23's correction, quoted because
an executor who reads only the recovery document will build the wrong thing: *"FR-PLAT-20's GC
is not a retention mechanism; it is a deletion mechanism, and NFR-OVR-6 is a preservation
floor."* There is **no expiry job to build**.

**C4 — the map's exit criteria say "1% of 50M annual quotes"; the budget is over quotes, not
batch rows**, and Ruling 25 makes that load-bearing rather than incidental: batch contributes
nothing to this stream, so the projection must not include batch volume.

**C5 — this plan's predecessor expected to owe an `OQ-RATE`; it does not.**
[`2026-08-29-w11-slices-2-4-planning-readiness.md`](2026-08-29-w11-slices-2-4-planning-readiness.md)
listed signal S-J — *"the FR-RATE-41/42 batch-sampling silence resolved as an `OQ-RATE` or a
spec change"* — as the longest-lead item nobody was working. Ruling 25 dissolved it: the suite
answers the question in three independent places, and the readiness document (like the recovery
document before it) had read a scoped requirement as a silent one. **No `OQ-` is raised and
`OQ-RATE-8` is not taken.** Recorded rather than folded in, because the readiness document's
reasoning was wrong in a way worth being able to find.

---

## Requirement coverage

Every id listed individually.

| Requirement | Where | Discharged by | How it is proven |
|---|---|---|---|
| FR-RATE-41 | `03` §3.7 | 4A | The persisted body is a `Trace` equal to the one `score_one` returned. **Capture** was Slice 1's; this is persistence |
| FR-RATE-42 | `03` §3.8 | 4A, 4B | 1 % default configurable, plus 100 % of declines and errors; persisted with the ≥ 13-month floor enforced |
| NFR-OVR-6 | `00` §9 | 4A | Deleting a trace row inside the floor is refused, proven on broken input |
| NFR-RATE-11 | `03` §9 | 4C | Traces are access-controlled; an unauthorised caller is refused |
| NFR-RATE-12 | `03` §9 | 4D | A projection from the measured serialised size, over quotes only |

**Deliberately excluded, each with its owner:** FR-RATE-34, 35, 40 → Slice 2. FR-RATE-36, 37,
38's batch half → Slice 3. FR-RATE-43, 44, 45 → W12. FR-RATE-46–49 → W13. FR-RATE-50,
FR-PLAT-28 → W14. NFR-RATE-1, 9, 13 → Slice 2. NFR-RATE-5 → Slice 3.

---

## Sequencing and blockers

| Task | Depends on | Blocked by | Why |
|---|---|---|---|
| 4A — row, migration, write | Slice 1 (merged) | — | Nothing to sample into until the store exists |
| 4B — the sampling decision | 4A | **Slice 2**, for the end-to-end half | See below |
| 4C — `GET /api/v1/traces` | 4A | — | Reads what 4A writes |
| 4D — NFR-RATE-12 projection | 4A | — | Needs real serialised traces to measure |

**4B's dependency on Slice 2 is real and the frozen map does not carry it.** Ruling 25 scopes
sampling to *"the real-time path only"*, and the real-time path is Slice 2's endpoint. The
sampling *function* is pure and fully testable without it; the *wiring* — deciding `trace=True`
per request and writing the result — has no call site until `POST /api/v1/score` exists.

**Do not let that serialise the whole slice.** 4A, 4C and 4D need only Slice 1. Build them, and
land 4B's wiring behind Slice 2. If Slice 2 has already merged when this slice starts, the
dependency is discharged and 4B is a single task.

---

## Task 4A — the trace row, its migration, and the one-serialisation write

**Files**
- Modify: `backend/src/app/db/models.py` — one row type. Fields: the three projected from the
  body (`quote_id`, `rating_version_ref`, `bundle_hash`), `sample_reason` (the only new one),
  the environment as a **plain string** (C2 — not a Deployment FK, which is W14's), the blob
  reference, and the created timestamp the retention floor is measured from.
- Create: an Alembic migration. **Read `.claude/skills/dev-commands` for the DSN trap** — the
  bare `alembic` command does not use the DSN you expect.
- Create: `backend/src/app/platform/traces.py` — the write, the read, and the deletion guard.
- Test: `backend/tests/test_traces.py`.

**Interfaces — Produces** (4B and 4C rely on these):
- A write taking one `Trace` plus a `sample_reason`, performing **one** serialisation and
  writing row and blob from it.
- A deletion path that refuses inside the retention floor.

**Steps**

- [ ] **Step 1: Write the failing round-trip test.** Persist a `Trace` with non-default
      `quote_id`, `rating_version_ref` and `bundle_hash`; read the row; fetch the body; assert
      the reconstructed `Trace` equals the original.
- [ ] **Step 2: Run it.** Expected: an import or attribute error for the new module. **A
      database error about a missing table means the migration ran but the module exists** —
      a different state, and a sign the steps were taken out of order.
- [ ] **Step 3: Write the divergence test — the one that makes "one serialisation" testable.**
      Assert the row's three projected fields equal the values *inside the stored body*, on a
      trace where all three are non-default. A projection built from a separate source passes a
      naive round-trip and fails this.
- [ ] **Step 4: Write the retention-floor test on broken input.** Attempt to delete a trace row
      whose age is inside NFR-OVR-6's floor; assert refusal. Then attempt one outside it and
      assert it is permitted, so the guard is shown to have an edge rather than refusing
      everything. Mark `@pytest.mark.req("NFR-OVR-6")`.
- [ ] **Step 5: Run all three and confirm each fails for its own cause.**
- [ ] **Step 6: Implement the row, the migration and the write.** Blob body via
      `BlobStore.put(session, content, media_type)`; **there is no `get`** — read back with
      `read(ref)`.
- [ ] **Step 7: Confirm the GC interaction rather than assuming it.** Write a trace, run the
      blob GC, assert the body survives. Ruling 23 says a referenced blob is not a candidate
      (`ref_count == 0` is the selector) — **verify it holds for this row type**, because that
      is the claim the whole retention design rests on.
- [ ] **Step 8: Run the gate. Commit.** `feat(rating): trace rows with blob bodies (W11 Task 4A)`

**Must NOT touch.** `model_schema.scoring.Trace` — it is shipped and its shape is `03` §4.5's.
If the row needs a field the body does not have, that is `sample_reason` and the environment,
both of which belong on the row.

---

## Task 4B — the sampling decision

**Files**
- Modify: `backend/src/app/platform/traces.py` — a **pure function** taking the outcome and the
  configured rate and returning sample-or-not plus the reason.
- Modify: `backend/src/app/config.py` or the workspace settings — the rate. FR-PLAT-45's
  enumerated workspace settings already name *"trace sampling rate"*, so it has a home; follow
  the neighbouring settings' resolver rather than inventing a second mechanism.
- Modify (**after Slice 2**): the scoring route, to call it and write the result.

**Steps**

- [ ] **Step 1: Write the boundary tests first, not the statistical one.** 100 % of declines and
      100 % of errors are sampled at **any** rate including `0.0`; a quoted outcome at `0.0` is
      never sampled; at `1.0` always. These are exact and cannot flake.
- [ ] **Step 2: Write the statistical test for the 1 % default.** Over a large N, with a
      tolerance stated in the test and a **fixed seed**. State the tolerance's basis in a
      comment — a test whose tolerance is unexplained gets widened the first time it flakes,
      which is how a sampling bug ships.
- [ ] **Step 3: Run them.** Expected: the function does not exist. **A failure asserting a
      wrong rate means a stub was written first** — not the predicted red.
- [ ] **Step 4: Implement the decision function.** Pure; no I/O; the rate is passed in, not read
      inside.
- [ ] **Step 5: Wire it — only once Slice 2's endpoint exists.** Decide `trace=True` per
      request, and on a sampled quote write via 4A. **A declined or errored quote is sampled at
      100 %, which means `trace=True` must be decided *before* the outcome is known** — the
      request either always requests a trace and discards it when not sampled, or re-scores,
      and re-scoring is not acceptable on a 50 ms budget. Take the first; note the cost in 4D's
      measurement, because always-tracing changes the latency figure Slice 2 measured.
- [ ] **Step 6: Run the gate. Commit.**

**A note the executor needs and the map does not give.** The 100 %-of-declines rule interacts
with `trace`'s position in the signature: `score_one` takes `trace` as an *input*, but the
sampling rule depends on the *outcome*. This is the one genuinely awkward corner of the slice,
and the resolution above (always capture, discard when not sampled) is a design choice this
plan makes explicitly so it is visible rather than discovered. **If measurement in 4D shows
always-capturing breaches NFR-RATE-1, that is a finding for the decision-maker, not a licence
to drop the 100 % rule** — the rule is FR-RATE-42's text.

---

## Task 4C — `GET /api/v1/traces` and its access control

**Files**
- Create: `backend/src/app/api/traces.py`; register it in `backend/src/app/main.py`'s router
  list.
- Test: `backend/tests/test_traces_api.py`.

**The route is specified, not invented:** `03` §5.1 declares
`GET /api/v1/traces?rating_version=&from=&to=` as *"Sampled **production** traces
(FR-RATE-42)"*.

**Steps**

- [ ] **Step 1: Write the failing filter test** — traces for one rating version and date range
      are returned; another version's are not.
- [ ] **Step 2: Write the access-control test** (NFR-RATE-11). An unauthorised caller is
      refused. Mirror the RBAC fixtures the neighbouring API tests already use; do not build new
      ones.
- [ ] **Step 3: Write the Ruling 25 exclusion test.** A trace row written with a `score.batch`
      Job as its parent must **not** be returned. Mark `@pytest.mark.req("FR-RATE-42")`.
      **This test can and should be written now even though Slice 3 does not exist**: construct
      the row directly with a batch parent. Writing it here is what stops Slice 3 from wiring
      batch traces into the production stream later — the ruling's own override condition.
- [ ] **Step 4: Run all three, confirm the causes, implement the route, re-run.**
- [ ] **Step 5: Run the gate. Commit.**

---

## Task 4D — the NFR-RATE-12 projection

**Files**
- Create: a dated note under [`../research/`](../research/), matching
  `zen-evaluate-concurrency.md`'s precedent.

**Acceptance**
- **Measure, do not estimate.** Serialise real traces produced by 4A from real scored quotes and
  record the actual byte sizes. The frozen map's own criterion is *"against the actual serialised
  `Trace` size Task 1.4 produces, not an estimate"*.
- **Report the distribution, not a mean.** Trace size scales with step count, so a mean over a
  single fixture answers almost nothing. Record the size against the step count, and say which
  structure was scored.
- **Project over quotes only** — NFR-RATE-12 budgets *"1 % sampling of 50 M annual **quotes**"*.
  Batch rows are excluded by Ruling 25, and including them would be projecting a budget the
  requirement does not set.
- **Assume no deduplication benefit** (Ruling 23): `elapsed_us` on every step makes two traces
  of identical inputs byte-distinct.
- **State the limit of what the projection proves.** It is a projection from measured sizes at
  one step count and one sample rate, not an observation of a year of production.

---

## Self-review

**1. Spec coverage.** Every requirement the frozen map allocates to Slice 4 appears in the
coverage table with its source and its task, listed individually, plus NFR-OVR-6, which the map
mentions only in passing and which carries this slice's sharpest broken-input test.

**2. Placeholder scan.** No TBD. One design choice — always-capture-then-discard in 4B Step 5 —
is made explicitly rather than left to the executor, with the reasoning and the escalation path
if measurement contradicts it.

**3. Type consistency.** `Trace` and `TraceStep` are used with the field names
`model_schema/scoring.py` declares, copied rather than retyped. `sample_reason` is named once as
the only new field and used under that name in 4A and 4B.

**4. Literals verified against shipped source at `d6505e9`**, including the two negatives that
matter: the blob store has `put`/`open`/`read` and **no `get`**, and no `JobKind` begins with
`TRACE` — the `TRACE_` symbols a grep surfaces first are request-tracing constants with an
unrelated meaning.

**5. Predicted failures are stated by cause** in 4A Steps 2 and 5, 4B Step 3, and 4C Step 4. 4A
Step 4 and Step 7 are the two broken-input proofs: the retention guard is shown to refuse inside
the floor *and* permit outside it, so it is not a blanket refusal; and the GC claim the whole
design rests on is verified for this row type rather than inherited from the ruling.

**6. What this plan does not decide.** Nothing in a charter above this one. The two questions
that could have been silently answered are named instead: the `Deployment` parent is deferred to
W14 with a register row owed (C2), and the always-capture cost is escalated to the
decision-maker if it breaches NFR-RATE-1 rather than resolved by dropping a requirement's clause.

**7. One correction to this plan's own predecessor is recorded rather than folded in** — C5. The
readiness document called the batch-sampling gap the longest-lead item in W11; Ruling 25 found
the requirement was scoped, not silent, and that two independent readers had made the same
misreading. The correction is left visible because "the suite was already clear" is exactly the
kind of finding that disappears once the document that got it wrong is quietly updated.
