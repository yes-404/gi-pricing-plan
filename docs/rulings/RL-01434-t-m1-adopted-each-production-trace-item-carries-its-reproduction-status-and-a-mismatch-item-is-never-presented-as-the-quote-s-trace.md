---
id: RL-1434
family: ruling
title: T-M1 adopted on FR-259 — each production traces route item carries its reproduction status, complete or mismatch, and a mismatch item stays listed but is never presented as the quote's trace
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # original date 2026-10-05, set at the draft; minted 2026-10-05
owner: decision-maker
tree: 5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FR-259, FR-258, RL-862, RL-890, RL-916]
---

# T-M1 adopted: a production trace item carries its reproduction status

## How this was ruled

- **Filed under working id 9505 (minted as RL-1434), reserved by the lead.** The mint sweep (`PL-1419` D4's
  practice) replaces every `RL-1434`, `FD-1433`, `PL-1435`, `SL-1436`, `PL 9776` and `FD-1425`
  below with its minted id.
- **The decision is not this record's.** It is the maintainer's, by delegation, in two
  entries in `~/gi-pricing-plan.local/channel/to-lead.md`, quoted verbatim under "The
  maintainer's entries" below. The 18:01:45 BST entry's item 1 (b) orders this record: "a NEW
  small RL adopting T-M1 (spec first; the 03 §5.1 row for GET /api/v1/traces or FR-259, as the
  DM finds the right anchor), NOT an RL-1423 amendment".
- **This record chooses the anchor and states T-M1 as text. It decides nothing else.** The one
  open point the applying plan hands it (whether `mismatch` items stay listed or are also
  filterable, `PL-1435` Delta 5 item 2) is settled by the entry's own word "MARKED"; see Ruled,
  item 3.
- **The finding** is FD-1433 (an auditor files it; proposed owner WK-1178). **The
  applying plan** is `PL-1435` / `SL-1436` (#1193, head `8f6cca29ab9b00b35df1e6bd2da2a2138c1f9429`
  when read): its Task 2d applies T-M1 byte for byte, and its activation need is "RL-1434
  minted" (Delta 6 item 3). That head may move; the mint head governs.
- **Brief:** `brief-dm-tm1-2026-10-05.md` (the lead, 2026-10-05).

## Verified first, at `5fe56b87`

Each line was read at `origin/main` `5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a`, in a fresh
worktree.

- **The worker compares.** `backend/src/app/worker/trace_handlers.py:90-96`: a bundle whose
  `content_hash` differs from `row.bundle_hash` completes the row with `trace=None` (condition
  (a), no body). `:98` re-scores with `trace=True`; `:99` takes
  `traces_service.summarise_result(result)`.
- **The comparator.** `backend/src/app/platform/traces.py:143-156`, `summarise_result`, dumps
  `_SUMMARY_FIELDS` (`:64`: `outcome`, `decline_reasons`, `premium_ladder`, `outputs`). The
  serving route stores the same summary as `served_summary` (`write_pending_trace`,
  `:159-202`).
- **The mark.** `complete_pending_trace` (`traces.py:205-278`): `trace is None` sets
  `blob_sha256 = None` and `status = "mismatch"` (`:248-251`); otherwise the body is written and
  retained (`:253-256`) and `status = "complete" if reproduced_summary == row.served_summary
  else "mismatch"` (`:257`). Its docstring (`:228-232`): the body "is written and kept either
  way … the ruling requires the mismatch *recorded*, not the trace discarded".
- **The ruling that mark serves.** `RL-862` condition (b),
  `docs/rulings/RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md:129-133`:
  "The persisted trace must be checked against the premium actually served, and a mismatch
  recorded rather than swallowed. … **A trace that silently does not match the quote it
  purports to explain is worse than no trace**".
- **The read route drops the mark.** `backend/src/app/api/traces.py`: `_filtered`
  (`:119-142`) tests `environment IS NOT NULL` and `blob_sha256 IS NOT NULL`, never `status`;
  `TraceView` (`:100-116`) has no `status` field; `_view` (`:145-157`) builds the item from the
  row's identity fields and the body alone. So a `mismatch` row with a body is listed exactly as
  a `complete` one is. A condition (a) `mismatch` row has no body and is not listed.
- **No existing field or code fits.** `backend/src/app/errors.py` registers two trace codes,
  `TRACE_RETENTION_FLOOR` (`:375`) and `TRACE_NOT_PENDING` (`:382`); neither means "did not
  reproduce", and an error would refuse the item, where the entry asks for it MARKED. `Trace`
  (`packages/model-schema/src/model_schema/scoring.py:187-201`) has no status field.
- **The spec is silent.** `docs/specs/03-rating-engine.md:924`, the §5.1 row, reads only
  "Sampled production traces (FR-259)". FR-259 (`03:176`) carries two dated clarifications
  (`RL-890`, `RL-916`) and says nothing of reproduction. `grep -n` for `` `mismatch` `` in `03`
  finds nothing.
- **The same mark serves `PL 9776`.** #1051, head `c7621ca2e500ef63f9538353541035a778134959`
  when read, `PL 9776`'s file under `docs/plans/` (slug `wk-1178-f35-remedy-what-the-trace-records-per-node-and-nfr-490-s-trace-overhead-leaf-plan`) `:300`,
  DP-F35-8 option (c): the off-path producer's result "is compared with the stored
  `served_summary` at `traces.py:257` and marked `mismatch` there, unchanged; T-M1 carries the
  mark to the reader." The 18:01:45 BST entry's item 2 adopts (c) as "ONE mechanism shared with
  item 1".

## The maintainer's entries, quoted verbatim

From `~/gi-pricing-plan.local/channel/to-lead.md`, read 2026-10-05 18:05 BST.

**"2026-10-05 17:51:03 BST — RL 9519 noted; PL 9567 delta 4 accepted with one question on
traces; DP-F35-7 = (a) with two conditions", item 2:**

> 2. PL 9567 #1193 @504db2f7 delta 4: condition B's named golden set and the byte-for-byte method (old bundle vs fresh compile, equal hash; ScoringResult, errors and the raw engine dict) are ACCEPTED. Serialising A-1/A-2/A-3 with SL 9568 on _model_call_handler: agreed.
>    ONE QUESTION, answered in the plan pre-mint: trace_handlers.py:90 checks only the hash and :98 RE-SCORES. So a pending trace of a pre-fix quote re-scores on the chain and can show a price that differs from the quote the customer got, where FD 9572 bit. The plan states what the trace does then (does it compare against the stored quote result and say so, or silently show the new value?). If it is silent, a red in SL 9568: a re-scored trace whose result differs from the stored quote is MARKED as differing, never presented as the quote's trace. No new route; an existing field or error if one fits, else spec first.

**"2026-10-05 18:01:45 BST — Trace mismatch: a NEW small RL for T-M1 AND an FD (it is live on
main today); DP-F35-8 = (c); the U measurement accepted", item 1:**

> 1. TRACE: planner-rb2's reading is accepted (the worker marks status "mismatch" at traces.py:257, but api/traces.py _filtered :119-142, TraceView :100-116 and _view :145-157 drop it). This is a DEFECT ON MAIN TODAY, independent of FD 9572: any mismatch (from any cause) is already listed as the quote's trace. So:
>    (a) an FD, filed by an auditor when a seat frees, with a proposed severity and owner WK-1178, and liveness (are there any mismatch rows in a seeded or demo database, and can one arise without the chain change). Its fix is SL 9568's Task 2d (the red plus the field), so the FD names SL 9568 as its discharger.
>    (b) a NEW small RL adopting T-M1 (spec first; the 03 §5.1 row for GET /api/v1/traces or FR-259, as the DM finds the right anchor), NOT an RL 9562 amendment: RL 9562 must not be held, because it gates the emergency PL 9560. PL 9567's new activation need = that RL minted. Agreed.

## Ruled

1. **T-M1 is adopted** as the text below: each `GET /api/v1/traces` item carries `status`,
   `complete` or `mismatch`, and a `mismatch` item is never presented as the quote's trace.
2. **The anchor is FR-259, as a third dated clarification, not the §5.1 row.** The reason:
   FR-259 is where this route's item semantics already live. Its two existing clarifications
   each decide what the route returns: `RL-890`'s says batch traces are "never returned by the
   production traces route", and `RL-916`'s says what the environment recorded on each item
   means. The §5.1 row (`03:924`) is a one-line index entry that defers to FR-259 by name and
   carries no item fields. T-M1 is a third statement of the same kind, and it is a behavioural
   obligation (what an item may be presented as), which is an FR's to carry, not an interface
   row's. One place only: the §5.1 row is not edited, so the text has one home.
3. **A `mismatch` item stays listed, marked; no filter is added.** The entry's word is
   "MARKED", and `RL-862` (b) requires the mismatch "recorded rather than swallowed": dropping
   the item from the list would swallow it. A `status` query parameter would be a new interface
   the entry does not ask for, so none is added (see "What this record does not decide").
4. **The mechanism is the existing one, named once.** The comparator is `summarise_result`
   (`traces.py:143-156`) and the mark is `traces.py:257`'s `status`, both unchanged. T-M1 only
   carries that mark to the reader. `PL 9776`'s DP-F35-8 (c) uses the same comparator and the
   same mark (Verified first, last item): there is one mechanism for both plans.
5. **The contract change is the backend route view, not `model-schema`.** `status` is a
   property of the stored `scoring_traces` row (`backend/src/app/db/models.py`, the `status`
   column), not of the `Trace` body, so `Trace` (`model_schema/scoring.py:187-201`) does not
   change. `TraceView` (`backend/src/app/api/traces.py:100-116`) gains a required `status`
   field typed to exactly the two values, and `docs/contracts/openapi/generated.json` is
   regenerated by `uv run python scripts/generate-contracts.py`, never hand-edited. Both are
   `SL-1436` Task 2d's, in one commit with the spec text (`CLAUDE.md` §2).

## The spec text

**T-M1 — `03` FR-259, a third dated clarification.** File:
`docs/specs/03-rating-engine.md`. Placement, read at `5fe56b87`: in FR-259's row (`03:176`),
**insert immediately after** the text `RL-916.)*` that closes the row's 2026-08-30
clarification, and before the row's closing ` |`, separated from `RL-916.)*` by one space.

The anchor, on whole text: `grep -cF 'RL-916.)* |' docs/specs/03-rating-engine.md` prints `1`
at `5fe56b87` (run in this record's worktree; the same `grep -cF` for
`so a real-time trace is never written without it.` also prints `1`, and is on the same row).

The placeholders are `<Task 2d date>` (the date of `SL-1436`'s Task 2d commit) and `RL-1434`
(replaced by the minted id at the mint sweep). Nothing else is a placeholder. Insert

```text
*(Clarified <Task 2d date>, WK-1178 — whether a sampled trace reproduced the quote it is listed against, written down because the route listed a re-score that did not reproduce the served result exactly as one that did (FD-1433). A sampled real-time trace's body is produced off the serving request by a deterministic re-score of the pinned bundle, and that re-score is compared with the result actually served (`RL-862`, condition (b)). Each item of `GET /api/v1/traces` therefore carries `status`: `complete` when the re-score reproduced the served result, `mismatch` when it did not. A `mismatch` item stays listed, so the record of what the re-score did is kept, but it is never presented as the quote's trace: the served result stands, and the item's body documents a re-score that differed from it. A trace still awaiting its re-score, or one whose pinned bundle could not be resolved, has no body and is not listed. Ruled in `RL-1434`.)*
```

## What it obliges

- **`PL-1435` / `SL-1436` Task 2d** applies T-M1 byte for byte under `spec-change`, adds
  `status` to `TraceView` and sets it in `_view` from `row.status`, leaves `_filtered`
  unchanged, regenerates the contracts, and runs `python3 scripts/audit-docs.py`. Its test,
  commit message and ledger cite `RL-1434` and FD-1433 by their minted ids. Where the plan's
  reading of T-M1 in Task 2d differs from this text, this text wins (Task 2d's own rule).
- **`PL-1435`'s activation need** "RL-1434 minted" (Delta 6 item 3) holds at this record's mint.
- **`PL 9776`** cites T-M1 for the mark its DP-F35-8 (c) relies on; it adds no second mark.
- **FD-1433**, when filed, names `SL-1436` as its discharger and this record as the spec text
  its fix applies.

## What this record does not decide

- **FD-1433's severity and liveness.** The auditor's to propose, per the 18:01:45 entry's item
  1 (a).
- **A `status` filter on the route.** Not added; a later need for one is a spec change of its
  own.
- **Batch-produced traces (FR-258).** They are never returned by this route (`RL-890`), and
  this record says nothing about how a batch run's traces record reproduction.
- **How `05-monitoring.md`'s quote-level metrics treat a `mismatch` item.** T-M1 forbids
  presenting it as the quote's trace; what a metric then does with it is `05`'s.
- **The `status` column's own comment.** `backend/src/app/db/models.py`'s comment on
  `blob_sha256` says "every other status requires it", while condition (a) writes a `mismatch`
  row with no body (`traces.py:248-251`). The listed behaviour T-M1 states is the code's
  (`_filtered` excludes a row with no body). The comment is not this record's to change; it is
  noted for the executor of Task 2d.
- **The mint order** of this record against FD-1433 and `PL-1435`: the lead's.

## Acceptance — the violation that must become detectable

The violation: **a sampled trace whose re-score did not reproduce the served result is listed
by `GET /api/v1/traces` with nothing to tell it from one that did.** Each test is shown
failing on deliberately broken input, in `SL-1436` Task 2d.

- **The mark is carried.** A `complete` row and a `mismatch` row with a body are both listed;
  the first carries `status` `complete` and the second `mismatch`. Red at `5fe56b87`: the item
  has no `status` (`None == 'complete'`).
- **The mark is read from the row.** With `_view` changed to pass `"complete"` for every row,
  the test fails at the `mismatch` item (`'complete' == 'mismatch'`).
- **Still listed.** The `mismatch` item is in the page, with its body. With `_filtered`
  changed to exclude `mismatch` rows, the test fails.
- **The contract.** `uv run python scripts/generate-contracts.py --check` exits 0, and
  `git diff origin/main...HEAD -- docs/contracts/` adds only `TraceView`'s `status`, with the
  two values. A hand edit of `docs/contracts/` fails the check.
- **The text.** `03`'s diff for T-M1 is byte-equal to the block above with its two placeholders
  filled, and `grep -cF` of its first sentence in `03` prints `1`.

Drafted as working id 9505; minted as RL-1434.
