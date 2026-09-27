---
id: LG-726
family: ledger
title: WK-661 — the model lifecycle, and `If-Match` against a real precondition
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-17
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — the model lifecycle, and `If-Match` against a real precondition, 2026-08-17 *(in progress, not closed)*

The sixth slice, and it opens the arm of `WF-698` that had no code at all. FR-202's six
states existed as an enum: `draft → fitted` was enforced at three layers and **nothing beyond
it existed**, so E6–E10 — submit, pin, review, approve, transition — were unreachable, and an
approved *request* would have sat beside a model still in `review` with nothing joining them.

| Delivered | Evidence |
|---|---|
| The lifecycle as data (FR-202) | `VALID_MODEL_TRANSITIONS` in `model-schema`, following `01`'s `VALID_DATASET_TRANSITIONS`. The tests assert the edges that must **not** exist, because a table only ever asked about legal moves is a lookup rather than an invariant |
| `POST /models/{id}/submit` | Declared in `02` §5.1 since Phase 0, served by nothing. `fitted → review`, the approval request, `approval_request_id` and the audit event in one transaction |
| `POST /models/{id}/archive` | **Added to `02` §5.1** — FR-202 names `archived` and no endpoint reached it. One unreachable state of six is how a partial machine gets recorded as complete |
| The decision reaches the artifact (`WF-698` E10) | `06` FR-351 stops the approval machine at `approved`. The `decide` route carries the decision across **in the same transaction**, because `MODEL` depends on `GOV` and never the reverse (DEP-1) — the seam WK-659 established with `withdraw`'s `artifact_is_live` |
| `superseded`, automatically | Approving version *n* supersedes every earlier **approved** version of the family, each audited. A family with two approved versions has nothing to say which one a Rating Version means. A merely `fitted` predecessor is left alone — it is a candidate, not something that was once in force |
| FR-205's flag | **Computed, not stored.** `01` FR-53 makes validation re-runnable, so a column written at fit time would answer `[]` for exactly the model the requirement exists to stop. A flagged model cannot reach `approved`; the refusal rolls the decision back with it |
| `models.status` finally enumerates its lifecycle | A `String(16)` with no constraint until now: `'live'` was a legal status, and a model holding one is skipped by every lifecycle query rather than refused. The existing CHECKs hid half the gap — a bogus status was caught *if* it had no `fit_result`, and accepted on a fitted model |
| **`00` §5.4 `If-Match`, and `CONFLICT_STALE_WRITE` registered** | `app/api/concurrency.py`, required on both lifecycle routes, checked **inside the transaction holding the row lock**. `If-Match: *` is refused rather than honoured: RFC 9110 gives it the meaning "if the resource exists", which is the precondition `00` §5.4 replaces, and a rule one character can disable is not one |
| Two declared-and-inert things made real | **`model:submit`** — a permission held by `pricing_actuary` that gated nothing; and **`EVIDENCE_INCOMPLETE`** — registered in the error catalogue and raised by nothing, the shape of gap `01` had with `RULE_TIMEOUT`. It now **fails closed** on an evidence kind this build cannot verify, so a policy tightening cannot silently do nothing |

**WK-660's reasoning about `If-Match` was right about the mechanism and wrong about the value.**
It deferred the header because an ETag over a status guarded by a state machine and a row lock
is "a second, weaker guard over the same field" — which is true. What it misses is that the
two produce the same 409 with different meanings: without the header a stale client is told
"your transition is invalid" and cannot tell that from "you asked for something never legal";
with it, the answer is "what you read is stale, read it again", and only that one is
actionable by a screen. The header is a precondition on the **caller's view**, and the record
now says so rather than claiming a lost-update guard the mechanism does not provide.

**Two divergences resolved rather than absorbed** (`CLAUDE.md` §0):

* **`06` FR-355 amended.** It returned a `changes_requested` artifact to `draft`; for a
  Model that is wrong, because `02` uses `draft` for *reserved but not yet fitted* and R2
  makes the coefficients immutable — a model cannot un-fit. It now reads "its pre-submission
  state", which is `draft` for most types and `fitted` for a Model.
* **`06` FR-386 appended.** `POST /approval-requests` validates the grammar of an artifact
  reference and never resolves it, so a request can be pinned to a version that was never
  created — and FR-356's pinning then pins nothing. This is the case where the **spec is
  right and the code is not**, so the spec gained the obligation rather than being edited down
  to what was built. Owner: WK-661's peril-structure slice, the first to add a second artifact type
  to the same path. Until then a decision on an unresolvable `model:` reference moves nothing
  rather than failing, because a request nobody can close is worse than one that decides
  without effect.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| `06` §3.3's fuller Model evidence — transparency artifact, model comparison, factor rationale, dataset lineage | **Deferred.** §3.3 and §4.2's defaults disagree about what a submission requires, and the code enforces §4.2 because that is the artifact a workspace can edit and a check can read. Raised as **OQ-639** with a recommendation (§3.3 as a floor, §4.2 may only add) rather than settled here. Comparison is FR-186, the next slice |
| FR-205's propagation to Rating Versions and the Approvals inbox | **Not started** — `03` is Phase 2, and ~~FR-358's inbox is WK-664~~ — **corrected 2026-08-23: it is `WK-678`'s, in Phase 3.** Three other statements in this file already read that way (§5's retrofit prose, WK-659's closure verdict, and the Phase 3 workstream table), WK-664's own row has never named the inbox, and `06` assigns no owner, as a spec should not. One parenthetical against three and a silent owning row makes this the slip. The model-side flag and the block on `approved` are delivered |
| `If-Match` on every other mutating endpoint | **Partial, and stated.** The mechanism is shared; this slice wires it to the two routes that have a genuine precondition to express. WK-660's status routes remain guarded by their state machine alone, which is the reading above — not a gap discovered late |
| A `GET /models` list route | **Absent from the spec and from the code.** Noticed while writing the tests, which had to read a family slug from the database. Not added: an endpoint with no requirement behind it is the inverse of `01`'s reference-lifecycle omission. Worth a plan-review question rather than a quiet addition |
| `models.diagnostics_id` is not covered by the immutability trigger | **Found here, not fixed here.** The trigger refuses changes to `fit_result`, `spec`, `spec_hash` and `dataset_version_id` on a fitted model; `diagnostics_id` can be repointed, which would change the evidence behind an approval after the approval. The `diagnostics` rows themselves are insert-only (FR-43), so the artifact cannot be rewritten — only the pointer. Owner: the next slice to touch that trigger  **Discharged 2026-08-22 by the audit-remediation slice.** Migration `9e4c7b21fa08` adds `diagnostics_id` to `models_fit_immutable()`'s frozen set. The guard stays conditional on `OLD.fit_result IS NOT NULL` because `record_fit` writes the fit result, the pointer and the status in **one `UPDATE`** — checked in the handler rather than assumed, which is what the original note asked for. Proven three ways: the negative test fails at the pre-fix revision, a deliberately *naive* unconditional guard is caught by the positive control, and `downgrade -1` restores the exact prior function body. ~~Owner: the next slice to touch that trigger~~ — which is the phrasing §13 rule 1 does not accept, and it happened to be answered only because an audit went looking. |
