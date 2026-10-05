---
id: FD-9502
family: finding
title: The trace read route lists a mismatch trace as the quote's trace
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: 5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a
corrected_by: []
relates: [WK-1178, WK-671, SL-1391, FR-259, FR-258, RL-862]
---

# The trace read route lists a mismatch trace as the quote's trace

**Filed under working id 9502** by the auditor, on the lead's order of 2026-10-05, from the
maintainer's (by delegation) entry headed "2026-10-05 18:01:45 BST — Trace mismatch: a NEW small
RL for T-M1 AND an FD (it is live on main today); DP-F35-8 = (c); the U measurement accepted"
(`to-lead.md`, a local channel file, so cited by its header), item 1 (a), quoted verbatim:

> an FD, filed by an auditor when a seat frees, with a proposed severity and owner WK-1178, and
> liveness (are there any mismatch rows in a seeded or demo database, and can one arise without
> the chain change). Its fix is SL 9568's Task 2d (the red plus the field), so the FD names SL 9568
> as its discharger.

The `tree:` is `origin/main` at `5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a`; every locator below was
read at that tree, each function in full with its signature. The claim is planner-rb2's, accepted by
the maintainer (by delegation) in the same entry; the auditor re-read every line.

## Finding

**Proposed severity: MEDIUM (the maintainer sets it); owner: WK-1178; discharged by SL 9568 Task 2d
(`PL 9567`, #1193), spec first through `RL 9505` (working id, drafting).**

A `scoring_traces` row whose off-path re-score did not reproduce the served result is stored with
`status = "mismatch"` **and its body kept**. `GET /api/v1/traces` never reads `status`, so it lists
that row exactly as it lists a `complete` one, as the quote's trace. A reader of the route cannot
tell a trace that reproduced the served quote from one that did not.

Only one of the two mismatch forms is affected, and the difference matters to the fix:

| Form | Producer | Body | Listed today |
|---|---|---|---|
| (a) bundle no longer resolves | `trace_handlers.py:90-96` calls `complete_pending_trace(…, None, reproduced_summary=None)` | none (`blob_sha256` NULL) | **No** — `_filtered` requires `blob_sha256 IS NOT NULL` (`api/traces.py:134`) |
| (b) re-score ran, summary differs | `trace_handlers.py:98-107`; `traces.py:257` | kept | **Yes** |

Form (a) is hidden by a condition written for a different purpose (a pending row has no body); form
(b) has no condition at all.

## Evidence

### 1. The worker marks the row and keeps the body

- `backend/src/app/worker/trace_handlers.py`: `_score_trace_produce` (:44)'s inner `work()` (:51) runs `score_one(compiled, ctx, trace=True)` (:98), then `reproduced_summary = traces_service.summarise_result(result)` (:99), then `complete_pending_trace(session, blob_store, trace_id, result.trace, reproduced_summary=…)` (:101-107).
- `backend/src/app/platform/traces.py`: `_SUMMARY_FIELDS` (:64) is `outcome`, `decline_reasons`, `premium_ladder`, `outputs`. `summarise_result` (:143-156) is `result.model_dump(mode="json", include=_SUMMARY_FIELDS)`. `complete_pending_trace` (:205-278) writes the blob first for a given `trace` (:252-256), then sets `status = "complete" if reproduced_summary == row.served_summary else "mismatch"` (:257). Its own docstring says the body "is written and kept either way, because a trace that failed to reproduce is still evidence of what the re-score actually did, and the ruling requires the mismatch *recorded*, not the trace discarded."
- `served_summary` is written at serve time: `write_pending_trace` (:159-202), called from `backend/src/app/api/score.py:515` with `traces_service.summarise_result(result)`. The column is `ScoringTraceRow.served_summary` (`backend/src/app/db/models.py:2305`), `status` is at `:2293-2296`.

### 2. The read route drops it

- `backend/src/app/api/traces.py` `_filtered` (:119-142) builds `workspace_id`, `environment IS NOT NULL` (:132), `blob_sha256 IS NOT NULL` (:134), and the optional `rating_version`, `from` and `to` conditions. It never tests `status`.
- `TraceView` (:100-116) has `id`, `quote_id`, `rating_version_ref`, `bundle_hash`, `sample_reason`, `environment`, `created_at`, `trace` — **no `status` field**, and `extra="forbid"`, so a client cannot see it by any route.
- `_view` (:145-157) builds the view from the row's own columns and `read_trace`'s body; `status` and `served_summary` are not read.
- `list_traces` (:161 onward) documents itself as "excluding anything not a **complete** real-time production trace". The code excludes a pending row and a batch row, and form (a) by accident of its null body; it does not exclude form (b). The docstring and the code disagree at this tree.
- The published contract carries the same shape: `docs/contracts/openapi/generated.json` has `TraceView` (description at :14308) with no status property.

### 3. No test pins the route against a mismatch row

`grep -n -i mismatch backend/tests/test_traces_api.py` returns nothing. `backend/tests/test_traces.py:444-479` tests only the service: a non-reproducing re-score lands `mismatch` (:464), and `trace=None` lands `mismatch` with no body (:479). Nothing reads either row back through `GET /api/v1/traces`.

### 4. Other readers of trace rows or bodies

Predicate: `git grep -n -E "ScoringTraceRow|scoring_traces|read_trace|/traces|TraceView|served_summary" origin/main -- backend/src frontend/src packages scripts` at `5fe56b87`, minus the three owning modules and the migrations, then each hit read.

| Reader | Locator | Status-blind? |
|---|---|---|
| The read route | `backend/src/app/api/traces.py:119-157` | **Yes**, the finding |
| Retention floor | `platform/traces.py` `delete_trace` (:295 onward) | No: it keys on `created_at`, and its own comment names the pending case |
| Blob GC and the quote-input blob guard | `backend/src/app/platform/blobs.py:497` (`QUOTE_INPUT_BLOB_COLUMNS`) | No: it reads `blob_sha256` only, the guard applies to any status |
| Frontend | `frontend/src` | **None** — no view, store or client reads the traces route; the only hits are prose in `PerilStructureDetailView.vue:15` and its test |
| Replay, export, monitoring | `backend/src`, `scripts/` | **None** at this tree. `scripts/bench-trace-size.py` measures body size only. `05`'s monitoring is a later phase |

So the route is the only reader. Every consumer added later (the Phase 2 monitoring and replay
surfaces, `05` §7's "sampled production traces" dependency) inherits the blindness unless the field
is on the view.

## Liveness

1. **Can a `mismatch` row exist today?** Yes, by construction. Form (b) needs the worker to re-score the pinned bundle and get a different summary. Re-score is "deterministic" by RL-862's premise, so a mismatch needs a divergence between serve time and re-score time that the bundle hash does not cover:
   - a code change in the engine or `pricing-core` between serve and re-score, under the same `bundle_hash` (the hash is the compiled bundle's `content_hash`, `trace_handlers.py:90`, so it does not move when the evaluator does);
   - **the chain change of FD 9572 under the same hash**, on `PL 9567`'s condition A: if the `to_wire` list-order fix changes a price for a stored bundle without changing its hash, every pending row served before the fix and re-scored after it lands `mismatch`;
   - non-determinism in the re-score path, were any to exist (not measured here; RL-862's premise says none does);
   - a worker whose version differs from the serving process.
   Form (a) arises when the Rating Version has moved on since serve (`trace_handlers.py:90`); it is already hidden by the null body.
2. **Does one exist now?** A read-only count was run against every local database holding a `scoring_traces` table, with `default_transaction_read_only=on` set on the connection, on 2026-10-05: `select status, count(*) from scoring_traces group by 1` returned **0 rows** in `gipricing`, `gipricing_sl-1391_d5679908`, `w37-6-767-772-test-a1` and `w37-6-767-772-test-a2`. The table is empty everywhere reachable. So there is no seeded or demo mismatch row, and the defect has **not been exercised on a real row**; the claim is established by reading the code, and by the absence of a test (Evidence 3), not by an observed listing. The `gip` database (`gip:gip@localhost/gip`, `config.py`'s default DSN) refused the password: it was **not counted**, and is not a 0.
3. **Can one arise without the chain change?** Yes: any of the other causes above. The chain change is the likeliest to make mismatches routine rather than rare.

## Spec reading (a reading, not a ruling)

- **FR-259** (`docs/specs/03-rating-engine.md:176`): "In production, traces are **sampled** … and persisted for ≥ 13 months (NFR-459), feeding `05-monitoring.md`." Its RL-916 clarification calls the persisted record the trace *of the quote served in the environment*. It says nothing of a trace that failed to reproduce the served result.
- **§5.1** (`:924`): `GET /api/v1/traces?rating_version=&from=&to=` — "Sampled production traces (FR-259)".
- **FR-258** (`:175`): a trace is "every step's id, label, consumed values, produced value, matched table row key, and elapsed time, plus the bundle hash and rating version reference". Nothing in the text says a trace is the account of the quote that was served.
- `RL-862`'s own text records the mismatch rather than discarding it, so the platform has already decided a mismatch is recorded; the specs do not say how a reader is to be told.

Read plainly: a listed item is a "sampled production trace", and the natural reading of "the quote's trace" is the trace that explains the quote that was served. A (b) row is, by its own definition, a trace that does **not** reproduce what was served. Presenting it under the same shape as a `complete` one is not forbidden by any sentence of FR-259 or §5.1, and it is not what either means. That is a gap in the specs, not a contradiction of a clause, so **the spec comes first**: the maintainer has ordered `RL 9505` (T-M1, working id) to state it, and §5.1's row or FR-259 is the anchor the decision-maker finds. This finding does not pick the rule. Two shapes are open to it: a `status` field on `TraceView` with mismatch rows listed and marked, or `status = 'complete'` added to `_filtered`. The entry that ordered this finding names "the red plus the field", which is the first.

## Severity (proposed): MEDIUM

- **For raising it:** it is silent. The route is the audit-facing read of what pricing did, and a governed system's trace that does not match the served quote is the kind of evidence an auditor would trust wrongly. The fix for FD 9572 makes a mismatch an expected event for every pending row it touches, so this finding turns from latent to routine at that moment.
- **For holding it at MEDIUM:** no reader beyond the route exists today (Evidence 4), no mismatch row exists in any reachable database, form (a) is already hidden, the data is intact (the row records `mismatch` and nothing is lost), and the fix is one field and one test.
- **Condition:** if `PL 9567`'s chain change can reach a database holding pending rows before Task 2d lands, the exposure is HIGH. The ordering of the two inside SL 9568 should keep Task 2d first or in the same slice.

## Remedy (a proposal; `RL 9505` states the rule)

Task 2d, in `backend/src/app/api/traces.py`: the red first, a route test that writes a `mismatch` row with a body and reads it back through `GET /api/v1/traces`; then the rule `RL 9505` states, with the contract regenerated (`docs/contracts/openapi/generated.json`; FR-451). The `list_traces` docstring is corrected in the same change.

## Disposition

Open. Owner WK-1178. Discharged by SL 9568 Task 2d on `RL 9505`. Closed in place by the auditor, citing the PR, when it merges and the re-audit has read the route against a `mismatch` row.

### Disposition — the lead's decision (pre-mint), 2026-10-05 18:06 BST

Per `docs/process/document-ids.md` §1.6; the maintainer may override. **MEDIUM; carry forward with an owner, WK-1178; discharged by SL 9568 Task 2d.** The spec rule comes first, via `RL 9505` (working id).

**Condition:** within SL 9568, Task 2d (the route carries the status) lands **before, or in the same commit as, the chain change**, so that no chain-caused mismatch is ever listed as the quote's trace. This is the HIGH trigger named under "Severity (proposed)" above, discharged by ordering.

### Disposition — accepted by the maintainer (by delegation), 2026-10-05

The maintainer (by delegation) accepted the decision above in `to-lead.md`, entry headed "2026-10-05 18:07:10 BST — FD 9502 decision ACCEPTED with your ordering condition; …", item 2, quoted verbatim: "your decision is ACCEPTED: MEDIUM; WK-1178; discharged by SL 9568 Task 2d, ON THE CONDITION that Task 2d lands BEFORE or IN THE SAME COMMIT as the chain change. That ordering is a GATE CONDITION of SL 9568's close and of my ACK of its merge: I check the commit order. The refinement (form a is already hidden by the blob_sha256 filter at traces.py:134; only form b is listed) is accepted."
