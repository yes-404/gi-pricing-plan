# `_compiled_for` component delta: the content-hash shortcut vs. the full blob-read path — W11 Slice 3 Task 3B

**This is not an NFR-RATE-1 re-measurement, and no number in this note may be read as
one** (Ruling 42 §6, `docs/plans/2026-08-30-w11-reopen-scope-and-batch-frame-contract-
rulings.md`). It does not run at 200 rps, it does not run on a dedicated host, and it does
not arm Ruling 41 §4's 15 ms trigger. **NFR-RATE-1 stays measured and FAILING** — that
verdict is unchanged by anything in this note, and `docs/audit/work/W11/README.md` §4's row
and §6's carry-forward row are not edited by it (Ruling 39 §2 keeps the closure record as at
the close; the remediation is recorded in the appended reopen section instead).

What this note measures is Ruling 41 §2's own predicate: after the fix, does a slot hit on
the freshly-read content hash actually skip the blob primary-key lookup, the object-store
read and `Bundle.model_validate_json` — the three terms Ruling 41 §1 found dominate the
pre-fix path?

## Method

- **Code under test.** `backend/src/app/api/score.py`'s `_fetch_bundle`/`_compiled_for`,
  measured directly — no HTTP, no FastAPI — for the same reason `bench-rating.py` measures
  `score_one` directly: a route's own overhead is not this component's cost.
- **Script.** `scripts/bench-compiled-for.py`, run as
  `uv run python scripts/bench-compiled-for.py --calls 200`.
- **Fixture.** One compiled Rating Version (`_minimal_algorithm`'s single-step graph — no
  GBM, no rate table pin), one workspace, `bundle_slot_capacity` left at its shipped
  default of 1 — **not raised**; Ruling 41 §4 left it unset and its own code comment
  requires a latency-harness measurement to raise it, which this note does not attempt.
- **Two conditions, same run, same tree, same host:**
  - **hit** — one `BundleSlot`, pre-warmed by a first call (excluded from both
    distributions), then 200 repeat calls against the same ref. Every call after the first
    is a genuine slot hit on a hash re-read from the version row on *that* call — never
    served from `slot.hash_for(ref)`'s memo of an earlier one.
  - **full path** — a fresh `BundleSlot()` per call, forcing a cold miss every time: the
    path every request paid before Ruling 41 §2, and what a first-ever request to a worker
    still pays today.
- **Machine.** `x86_64`, 4 cores — a shared development machine, not a dedicated benchmark
  host. 1-minute load 2.16 at the time of the run.
- **Tree.** `feat/w11-3b-batch-handler`, branched from `main` at `59407f2` (W11 Task 3A,
  merged) — measured against this task's own commit, carrying the `_fetch_bundle`/
  `_compiled_for` change this note is about; not self-citable by its own hash, so named by
  branch and base rather than by a commit this run necessarily predates.
- **Pass count.** One run of the script; each condition is 200 sequential calls within it.
- **Ref cardinality.** One. Ruling 41 §4's own warning applies directly: *"with capacity 1
  and more than one ref in play the slot thrashes and every request pays the full path"* —
  these numbers describe the single-ref workload measured, not a multi-tenant one.

## Result

| condition | n | mean | p50 | p99 | max |
|---|---|---|---|---|---|
| hit | 200 | **3.657 ms** | 3.535 ms | 5.957 ms | 8.037 ms |
| full path | 200 | **11.637 ms** | 11.481 ms | 15.861 ms | 16.700 ms |

**Mean delta: 7.979 ms.** The hit condition is a version-row `SELECT` plus a slot lookup;
the full-path condition adds the blob primary-key lookup, the object-store read and
`Bundle.model_validate_json` on top of the identical `SELECT` — so the delta is
attributable to exactly the three terms Ruling 41 §2 orders removed from the hot path on a
hit, and the fact that it is removed at all (not merely reduced) is the property being
tested, not the millisecond figure itself.

**What this does not show.** It does not show NFR-RATE-1 passing — the fixture here carries
no GBM call and no ~200-step graph, so it is not comparable to Ruling 41 §1's `_fetch_bundle`
figures or to NFR-RATE-1's own budget at all. It does not show the fix helping at scale —
that needs `bundle_slot_capacity` raised with its own evidence, and more than one ref, both
explicitly out of scope here. It is a proof that the mechanism Ruling 41 §2 describes is the
mechanism actually running, on real code against a real (if minimal) compiled bundle and a
real Postgres row — not a proof of any requirement.

## Disposition

Filed alongside the code change (`backend/src/app/api/score.py`) and the two register-row
corrections (F50, `backend/src/app/platform/bundle_slot.py`'s docstring; F51, a dated
annotation on `docs/research/w11-task-2d-nfr-rate-1-full-path.md`) that Ruling 42 §7 assigns
to the same task. The requirement re-measurement Ruling 41 §4 names — a dedicated host, more
than one pass, `bundle_slot_capacity` set from its own evidence — remains W14's.
