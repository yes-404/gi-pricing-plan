---
id: PL-WORKING
family: plan
kind: leaf
title: WK-672 Slice 2 — Golden Quotes and promotion re-scoring: leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-28
owner: planner
tree: ea6162b9b67b19d7bc315432c6a82e00bc1f9ee5
phase: P2
work: WK-672
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-930, PL-1177, RL-1172, RL-917, LG-1182]
---

# WK-672 Slice 2 — Golden Quotes and promotion re-scoring: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `python-package` and `contract-guard` (Task 2), `python-test` (every task), `fastapi-service` (Tasks 4–5) and `dev-commands` (the gate), and reads `docs/plans/README.md`'s five unchecked conventions before its first step.

## Goal

Build FR-260: a persisted, access-controlled Regression Suite of Golden Quotes; a pure
`pricing-core` re-score of those quotes; and the check at `POST …/submit` that refuses
promotion on any mismatch. Per the deputy's DP-S2-1 condition, pin the exact suite a
submission was checked against, and show the approver every golden-quote change since the
previous approved Rating Version of the same algorithm, each with its author.

**Architecture:** The leaf plan for Slice 2 of the map plan `PL-930`
(`docs/plans/PL-00930-wk-672-testing-map-plan.md`), which stays the map. It applies
`RL-1172` (`docs/rulings/RL-01172-wk-672-opening-rulings-f60-and-f59-are-spec-defects-the-regression-executor-lives-in-pricing-core-and-fr-257-limb-1-is-slice-3-s.md`)
and the deputy's decisions on DP-S2-1, DP-S2-2 and DP-S2-3, quoted whole under "Decision
points". Slice 1 (`PL-1177`, executed by #853, closed by `LG-1182` in #858) is done and is
not redone. RL-1172 item 3c places the work:
- **`pricing-core`** (`rating/testing.py`) holds only the pure re-score. It does no I/O and
  imports no FastAPI, SQLAlchemy or Redis (`CLAUDE.md` §2).
- **The backend** owns the suite store, the routes, the audit events and the submit gate.
- **`model-schema`** owns every new shape (ADR-704).

No `SL-` row exists in the roadmap, so this plan carries no `slice:` field (the `PL-1070`,
`PL-1144` and `PL-1177` precedent).

**Tech Stack:** Pydantic v2 (`model-schema`), `pricing-core` (the synchronous engine path of
RL-868), FastAPI, SQLAlchemy 2.x async with Alembic, PostgreSQL 16, and pytest with the `req`
marker. No new dependency.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md). The sections this
plan uses, at `ea6162b9`:
- §2, the glossary rows Golden Quote (`03:68`) and Regression Suite (`03:69`);
- §3.8, FR-257 (`03:173`), FR-260 (`03:176`) and FR-261 (`03:177`);
- §4.3 `RatingVersion` and its `evidence` block (`03:343`);
- §4.7 `RegressionSuite` and `GoldenQuote` (`03:483`);
- §4.9 `RegressionRun` (`03:581`);
- §5.1, the section at `03:623` with its route table at `03:625`, and the error codes (`03:650`);
- §5.2, the `testing.py` block (`03:765-768`);
- §9, NFR-499 as clarified (`03:989`, RL-917).

Also [`../specs/06-governance.md`](../specs/06-governance.md): FR-353 (approver ≠ author,
#861), FR-364 (the evidence floor) and FR-368 (audit events). And
[`../workflows/WF-00699-approved-models-to-approved-rating-version.md`](../workflows/WF-00699-approved-models-to-approved-rating-version.md)
steps D1–D3 and E2.

## Acceptance Standard

Every command runs in the executor's own worktree (`env -C <worktree> …`), against the
range `origin/main...HEAD`, never a tip SHA alone. Each test named below carries
`@pytest.mark.req(...)` with the id given. A test that is "shown red first" has its failing
run quoted in the ledger with the failing assert line, and a failure of any other cause is a
plan defect, not the predicted one.

1. **Spec changes.** In `docs/specs/03-rating-engine.md`:
   - (a) `grep -n 'regression-suites' docs/specs/03-rating-engine.md` prints the two new §5.1 rows (Task 1).
   - (b) `grep -n 'def evaluate_golden_quotes' docs/specs/03-rating-engine.md` prints one line inside the §5.2 `testing.py` block.
   - (c) `grep -n '"assertion"' docs/specs/03-rating-engine.md` prints nothing: §4.7 carries the structured union.
   - (d) FR-260 carries a dated amendment naming the pinned suite hash and the delta.
   - (e) §4.3's `evidence` example shows `golden_quotes`.
   - (f) §4.9 cites `regression-run.schema.json`.

   `python3 scripts/audit-docs.py` adds no failure row, and no requirement id is minted.
2. **Shapes are `model-schema`'s, generated and compared.**
   - `uv run python scripts/generate-contracts.py --check` exits 0, and `docs/contracts/schemas/generated/regression-suite.schema.json` exists.
   - `grep -n '"regression-suite"' backend/tests/test_contracts.py` shows the slug in `COMPARED_SLUGS` and not in `ONE_SIDED_SLUGS`.
   - `"regression-run"` is in `ONE_SIDED_SLUGS` with a label naming Slice 3.
   - `uv run pytest backend/tests/test_contracts.py -q` passes.
   - No shape defined in `model_schema/regression.py` is redeclared anywhere under `backend/` or `packages/pricing-core/` (`grep -rn 'class GoldenQuote\b\|class RegressionSuite\b' backend packages` prints only `model_schema/regression.py`).
3. **The assertion union refuses free text.** `uv run pytest packages/model-schema/tests/test_regression.py -v` passes. It covers:
   - each of the five kinds round-tripping;
   - a property carrying an `assertion` string, refused;
   - an unknown `kind`, refused;
   - `premium_bounded` with neither bound, refused;
   - duplicate golden-quote names, refused;
   - `suite_content_hash` stable under key order and changed by any `expected` or `tolerance` edit.

   All carry `req("FR-261")` or `req("FR-260")`.
4. **The pure re-score is exact.** `uv run pytest packages/pricing-core/tests/test_testing.py -v` passes. It covers:
   - an exact match passing;
   - one minor unit over a zero tolerance failing, with `difference_minor == 1`;
   - a difference inside the declared tolerance passing;
   - an outcome mismatch (`quoted` expected, `declined` actual) failing;
   - a golden quote whose context violates the input contract becoming a `fail` result rather than raising;
   - the function called from a plain synchronous test, with no event loop.

   Carries `req("FR-260")` and `req("FR-273")`. `uv run lint-imports` exits 0.
5. **The store is access-controlled and audited.** `uv run pytest backend/tests/test_regression_suites.py -v` passes, with the DB stack checked up first. It covers:
   - a principal without `rating:write` refused creation (403);
   - a principal without `rating:read` refused the read (403);
   - every created version having exactly one `regression_suite.created` Audit Event whose actor is the creator (`req("FR-368")`);
   - neither that event's `before`/`after` nor any captured log line containing a golden quote's context input values (`req("NFR-499")`);
   - a second suite slug for an algorithm that already has one refused (409), **by the database**: the `regression_suites` registry is unique on `(workspace_id, algorithm_slug)` and on `(workspace_id, slug)`, and the service maps the `IntegrityError` to 409;
   - **a concurrency test:** two `create_suite_version` calls for one algorithm under two different slugs, in two separate sessions run with `asyncio.gather`, give exactly one 201 and one 409, and leave one registry row. It is shown red first against a check-then-insert implementation with no constraint;
   - changing `algorithm_slug` across versions of one slug refused (409).
6. **The submit gate refuses a mismatch.** `uv run pytest backend/tests/test_rating_versions.py -k golden -v` passes. It covers:
   - a submission whose suite has a mismatching golden quote refused with `GOLDEN_QUOTE_MISMATCH` (409), the Rating Version still `draft` and no approval request created, shown red first;
   - a matching suite moving the version to `review`, with `evidence.golden_quotes` holding the suite ref, its content hash, and the `content_hash` of the `CompiledBundle` actually scored;
   - a loaded bundle whose `content_hash` differs from `row.bundle["content_hash"]` refused with `BUNDLE_COMPILE_FAILED` (409), nothing written;
   - with metadata storage failing, submit refuses rather than scoring the slot's last-known-good bundle: the gate uses `_fetch_bundle`, never `_compiled_for`;
   - a suite present but no compiled bundle refused with `BUNDLE_COMPILE_FAILED` (409);
   - no suite for the algorithm: the submission proceeds, and `evidence.golden_quotes` is the explicit `GoldenQuoteNotChecked` record — `regression_suite: "none"` and `message: "no golden quotes were checked"` — never null and never an empty result list that reads as "0 mismatches" (DP-S2-4 as the deputy accepted it).

   All carry `req("FR-260")`.
7. **The pin holds.** A test creates a new suite version after a submission and asserts the submitted version's `evidence.golden_quotes.suite_content_hash` is unchanged (`req("FR-260")`).
8. **The delta surfaces a changed expectation, shown red first** (the deputy's DP-S2-1 condition, items 2 and 3):
   - Principal A creates suite v1. Rating Version 1 of algorithm X is submitted and approved.
   - Principal B creates suite v2, changing one golden quote's `expected.payable_premium_minor`.
   - Rating Version 2 of X is submitted.
   - Its `evidence.golden_quotes.delta.changes` lists that quote as `changed` with `changed_fields == ["expected"]`, `before`, `after` and a `steps` list whose one entry is `{version: 2, changed_fields: ["expected"], author: B's principal id}`, the author read from v2's `regression_suite.created` event.
   - **A second red-first test does the same with a tolerance-only widening:** principal B raises one quote's `tolerance.money_minor` in suite v2, and RV2's delta lists it as `changed` with `changed_fields == ["tolerance"]`, `before_tolerance`, `after_tolerance` and one step authored by B (the deputy's 15:57:21 item (ii)).

   Companion tests:
   - an added quote and a removed quote each listed;
   - a context-only change listed as `changed` with `changed_fields == ["context"]` and differing `before_context_hash`/`after_context_hash`, the context itself not copied into the evidence (NFR-499);
   - with no previous approved version, every quote listed as `added`;
   - of two approved versions of X, the later-approved one used as baseline;
   - an approved version of a different algorithm ignored;
   - **a later cosmetic edit does not mask a substantive one** (audit finding F3): X widens a tolerance in v2, Y edits only that quote's `note` in v3, and the delta lists the quote with one step, `{version: 2, changed_fields: ["tolerance"], author: X}`. Y appears nowhere, because a note is not a compared field. Shown red first against a last-touch attribution;
   - two substantive edits by different principals (X widens the tolerance in v2, Y changes the expected value in v3) give two steps, each with its own author;
   - a suite version whose `regression_suite.created` event is missing makes submit refuse with `APPROVAL_AUTHOR_UNRESOLVED`, 403 (#861's code and status; Task 5 starts only after #861 has merged).

   The delta is visible in `GET /api/v1/rating-versions/{id}` to a principal holding `approval:decide`.
8a. **The gate cannot be skipped, and the delta's author cannot approve** (DP-S2-5, DP-S2-6). `uv run pytest backend/tests/test_rating_versions.py -k 'golden and (bypass or evidence_author)' -v` passes. It covers:
   - on the tree with the WK-1178 approval-status PR merged, a `draft` Rating Version whose algorithm has a mismatching suite, sent to `POST /api/v1/approval-requests` directly, is refused, and the version never reaches `approved` without `evidence.golden_quotes`;
   - principal C authors suite v2's change; the Rating Version's delta lists C; C (holding `approval:decide`, and neither submitter nor RV author) is refused with 403 `APPROVAL_BY_EVIDENCE_AUTHOR`, and no decision row is written. Shown red first;
   - a principal who authored no change in the delta is not refused by this rule.

   All carry `req("FR-260")`, and the second also `req("FR-353")`.
9. **The full two-half gate exits 0** on the committed tree, each exit code recorded in the ledger beside its `HEAD`. It is the six lines of `CLAUDE.md` §11, run as `dev-commands` gives them. `alembic upgrade head` and `downgrade -1` run clean on the per-worktree test database. **The determinism repeat also runs on the final tree:** `uv run pytest packages/pricing-core/tests/test_rating_score.py -q`, five times, all rc 0, each rc in the ledger. **If any of the five aborts, the slice does not pass its gate**, and the finding's triage moves ahead of this slice (the deputy's 15:57:21 entry; Global Constraints, "the scoring path's threading is unchanged").
10. **The four docs checks pass on a detached copy of the committed tree:**
    - `python3 scripts/audit-docs.py`;
    - `python3 scripts/doc-id.py check`;
    - `python3 scripts/doc-index.py --check`;
    - `python3 scripts/register-lint.py`.

    The ledger quotes each rc, the `FAILED (n)` line or "All checks passed.", and the `DISCLOSED (…)` line. DISCLOSED is no higher than main's at the merge base.
11. **The change set is exactly the slice's:** `git diff --stat origin/main...HEAD` lists only the paths named in the Files blocks below, the slice's `LG-` ledger and `docs/INDEX.md`.
12. **The deputy's merge acknowledgement is recorded** on the PR before the lead merges, and
    the slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and
    the lead's merge — no maintainer acceptance line is required for this slice, and none is
    to be waited on.

## Global Constraints

- **Money is integer minor units, never float** (`CLAUDE.md` §7; FR-273). Every money field
  is `MoneyMinor` (`model_schema/money.py:61`). The comparison is integer subtraction.
- **`pricing-core` stays standalone** (`CLAUDE.md` §2): `rating/testing.py` imports only
  `model_schema` and `pricing_core`. `lint-imports` enforces it.
- **Nobody hand-writes a shape `model-schema` owns** (`CLAUDE.md` §2; ADR-704). The backend
  request and response bodies are the `model-schema` models or thin wrappers declared there.
- **A full quote input is held only in an access-controlled artifact, and never logged**
  (NFR-499 as clarified, RL-917). A golden quote's `context` lives in the suite row. Every
  read is permission-checked, and no audit payload or log line carries it.
- **No approvable type is added.** Under DP-S2-1 (A) the suite is not approvable, so no
  `regression_suite` entry goes into #861's `CREATION_ACTIONS`. Had (C) been decided, the
  slice would have added that entry and its fail-closed test. The deputy decided (A), so no
  such task exists.
- **S2's FR-260 hook does not merge before the approval-status-bypass PR** (audit finding F1; the deputy's decision of 2026-09-28, quoted whole under "Decision points"). On main at `3a3df367`, a `draft` Rating Version can be approved through the generic `POST /api/v1/approval-requests` without `…/submit`, so a submit-time gate is skippable. That hole is fixed **outside this slice**, by the WK-1178 approval-status PR (its number follows; executor-s1, after #861). **This slice does not duplicate that fix.** Task 5 starts by checking that the WK-1178 approval-status PR's squash is on `origin/main`, and **stops and reports** if it is not. It keeps one negative test proving the golden-quote gate cannot be skipped through the generic route once that PR has landed.
- **An approver who authored a suite change in the delta is refused** (audit finding F4; the deputy's decision (i), the same entry). If the deciding principal is the `author` of any `GoldenQuoteChangeStep` in the Rating Version's `evidence.golden_quotes.delta`, the decision is refused with **403 `APPROVAL_BY_EVIDENCE_AUTHOR`**, the sibling of #861's `APPROVAL_AUTHOR_UNRESOLVED`. The code is registered in `GOVERNANCE_ERROR_CODES` and in `06`'s error list by this slice. **This is not the general component-author case**, which stays carried to WK-677. It applies only to the delta the approver is shown.
- **Task 5 depends on #861 MERGING.** Task 5 reads the author from the creation Audit Event,
  which is #861's definition, and refuses with #861's registered code
  `APPROVAL_AUTHOR_UNRESOLVED` at #861's status, **403**. A reused code keeps its status.
  **If #861 has not merged when Task 5 starts, the executor stops and reports.** Tasks 1–4
  do not depend on it.
- **The scoring path's threading is unchanged.** The `_score_context_sync` extraction (Task
  3) moves code only. It adds no thread, no executor, no lock and no change to how or where
  `bundle.decision.evaluate` is called. The pricing-core determinism test
  `test_scoring_is_deterministic_across_a_subprocess` (`packages/pricing-core/tests/test_rating_score.py`)
  aborted natively in CI on #830 (a GIL-state abort, 1 in ≥ 40 runs). That is being filed as
  a finding owned by the lead, and this slice sits beside it.
- **Permissions: `rating:write` to create a suite version, `rating:read` to read one.** Both
  already exist (`packages/model-schema/src/model_schema/permissions.py`, `RATING_WRITE` and
  `RATING_READ`), and none is added. The grounds are #856's catalogue ruling, DP-A (c),
  decided by the deputy: the code's coarse `rating:write` is the P2 catalogue name for
  rating-artifact writes. That answers #855's permission-catalogue finding, which requires
  every permission-touching slice to name its choice. Its condition, that author and approver
  are separated, is #861's, and the delta in Task 5 is what the approver reads.
- **Requirement ids are permanent** (`CLAUDE.md` §5). This slice mints no requirement id.
  FR-260 takes a dated amendment.
- **Spell no retired legacy path** (RL-1140, check 36).

---

## Scope

### Requirement coverage, each id individually

- **FR-260** (`03` §3.8): every task. The store, the re-score, the submit gate, the pin and
  the delta.
- **FR-261** (`03` §3.8): Task 2 only. The five property classes are *stored* as the
  structured union. Their evaluation is Slice 3's.
- **FR-273** (`03` §3.11): Task 3. The comparison is exact in integer minor units.
- **FR-257** (`03` §3.8): not built here. Limb (1) is Slice 3's (RL-1172 item 4). This slice
  leaves the `regression_run` evidence floor (`06` FR-364) untouched.
- **NFR-499** (`03` §9, clarified by RL-917): Tasks 4 and 5, the access-controlled store and
  the no-logging tests.
- **`06` FR-353, FR-364, FR-368:** FR-368 is Task 4 (the creation event) and Task 5 (the
  author is read from it). FR-353 is #861's, consumed and not changed. FR-364 is unchanged.

### What Slice 1 already delivered, and which item each unblocks

| Delivered by `PL-1177` / #853 | At `ea6162b9` | Unblocks |
|---|---|---|
| `GOLDEN_QUOTE_MISMATCH` registered in `RATING_ERROR_CODES` | `backend/src/app/errors.py:343` | Task 5's refusal: raised, not registered |
| `03` §4.9 `RegressionRun` declared, with the `golden_results` item shape | `03:581` | Task 2's `GoldenQuoteResult` is that item, field for field |
| WK-672's charter names FR-260 and the submit-time evidence | `docs/roadmap.md`, WK-672 section | the scope this plan cites |
| the `regression-suite` scope-out relabelled to `03` and WK-672 | `backend/tests/test_contracts.py:91` | Task 2 lifts it into `COMPARED_SLUGS` |

### Carried to later slices — named, not planned here

- **Slice 3:** it owns the following.
  - Evaluation of the five property classes stored here.
  - `run_regression`, which composes this slice's `evaluate_golden_quotes`.
  - `RegressionRun` as a `model-schema` artifact. It is generated as `regression-run` and
    lifted out of `ONE_SIDED_SLUGS`.
  - FR-257 limb (1) (RL-1172 item 4).
  - `PROPERTY_ASSERTION_FAILED` together with its raiser (`PL-1177`'s carried list).
  - Validating that a `monotone` property's `input` names a field of the algorithm's input
    contract.
  - `hypothesis` under the deputy's six F4 conditions (research record `RS-1176`). They
    include `generation.cases` as the bounded example count and the hypothesis version
    persisted beside `generation.seed`. Slice 3 amends §4.7's `generation` block for the
    second of these.
- **Slice 3 must decide** whether a Regression Suite with at least one golden quote is **required** for submission, at least for Rating Versions headed to `prod`, as a DP if it is a scope question. The `not_checked` interim rule (DP-S2-4) is not carried past Slice 3 silently (the deputy's 15:57:21 item (i)).
- **WK-677:** the general component-author case (an approver who authored a pinned component). Only the suite-delta case is refused here (DP-S2-6).
- **WK-1178:** the approval-status bypass fix (DP-S2-5). This slice depends on it and does not duplicate it.
- **Slice 4:** `POST /api/v1/score/compare` (RL-1172 item 5).
- **WK-675:** rendering the golden-quote delta in the approval view. This slice makes it
  readable through the API, which is the approver's evidence.
- **Not WK-672's:** the native abort in `test_scoring_is_deterministic_across_a_subprocess`,
  which the deputy's entry quoted below records against #830. The lead owns it.

### Decision points

The deputy's entry is quoted whole, fenced, as the record each row's "Resolved by" cites.

```text
## 2026-09-28 15:48:14 BST · deputy · WK-672 S2: DP-S2-1, DP-S2-2 and DP-S2-3 DECIDED (DP-S2-1 with a governance condition); #830's flaky python job: the re-run is right, and the FD is filed with a severity note

Given by the maintainer's delegation. The S2 leaf plan quotes this entry and records it in a decision-maker `RL-` or its own DP table's "Resolved by" column, dated.

**DP-S2-1: (A) DECIDED, with one condition.** The suite is its own versioned artifact (`POST /api/v1/regression-suites/{slug}/versions`), referenced outside `pins`, so the bundle hash stays pins-only. It is not approvable. **The condition, which closes the gap (A) opens:** a non-approvable suite means anyone with `rating:write` could change a golden quote's expected value so that their own Rating Version passes. The check is only as honest as its expectations. So:
1. **The submission's evidence pins the exact suite version** (its content hash) that the FR-260 re-score used.
2. **The approval evidence shows the suite's delta:** whether the pinned suite differs from the one used for **the previous approved Rating Version of the same algorithm**, listing every golden quote added, removed or whose expected output changed, with the author of each change (the creation-event actor, per my 15:10:33 definition).
3. The approver, who is by #861 never the author, **sees that delta before deciding**. No new approvable type is added, and the gate stays FR-260's.

S2's acceptance includes a test in which changing a golden quote's expected value **appears in the next submission's evidence delta**. It is shown red first, with no delta surfaced, then green.

**DP-S2-2: (a) DECIDED.** FR-260's "promotion" check runs at `POST …/submit`, joining FR-364's evidence floor (`regression_run`). It fails fast, and because the suite version is pinned in the evidence (DP-S2-1 item 1), a later suite edit cannot silently change what was checked.

**DP-S2-3: (a) DECIDED.** A new pure `evaluate_golden_quotes` in `pricing-core`, on which S3's `run_regression` builds. It keeps RL-1172's placement (pure execution in `pricing-core`, no persistence). Money comparisons are exact in integer minor units (FR-273; my 13:57:02 correction).

**The five-class assertion field design** is the plan's own work, as you say. It must be the structured union I ruled for F4 (declarative JSON, no free text), and S2 only *stores* assertions; S3 evaluates them.

**#830's failure:** `test_scoring_is_deterministic_across_a_subprocess` aborted with `PyGILState_Release … must be current` (rc −6) in run 36436160310. #830 is docs-only, and the re-run is right. **The FD's severity note:** a native abort in the **scoring path's** determinism test is possibly a thread-safety defect in the engine binding or Polars, **in production scoring code**, not only in CI. Its first triage step is reproducing it under load with N repeats (the failure is 1 in ≥ 40 runs). It is filed after #860 as you sequenced, owner the lead, and **it is on plan review 15's list of open P2 risks**. The #830 ACK request states the first failure beside the green re-run, and names the retitle.
```

The deputy's second entry, deciding DP-S2-4 and the tolerance question, quoted whole:

```text
## 2026-09-28 15:57:21 BST · deputy · S2 (#862): DP-S2-4 ACCEPTED with a visibility condition; tolerance-only changes stay in the delta (ACCEPTED)

**(i) DP-S2-4, a Rating Version with no suite passes at submit until S3 decides: ACCEPTED as the interim rule, with one condition.** A pass with zero golden quotes is vacuous: nothing mismatches because nothing is checked. So:
- **The submission evidence says so explicitly:** `regression_suite: none` (not an empty list that renders as "0 mismatches"), shown to the approver as "**no golden quotes were checked**".
- **S3's leaf plan must decide** whether a suite (with at least one golden quote) is **required** for submission, at least for Rating Versions headed to `prod`, and state it as a DP if it is a scope question. The interim rule is not carried silently past S3.
- FR-364's approval floor (`regression_run` for `rating_version`) is unaffected: S6 wires it after S3, as planned.

**(ii) Tolerance-only changes flagged in the delta: ACCEPTED, and they are required, not optional.** Widening a golden quote's tolerance weakens the check exactly as changing its expected value does. The delta lists **expected output, tolerance, and quote-context changes** alike, each with its author. S2's red→green test covers a tolerance-only widening as well as a value change.

**Your two notes to the planner are right.** The unresolved-author refusal is **403** (an authorisation outcome, consistent with #861's `APPROVAL_AUTHOR_UNRESOLVED` class), not 409. **N = 5 runs** of `test_rating_score.py` in S2's gate, because of the determinism abort, with every run's result recorded in the ledger. **If any of the 5 aborts, S2 does not pass its gate:** the FD's triage moves ahead of S2, since S2 builds on that scoring path.
```

The deputy's third entry, deciding the approval-status bypass (audit finding F1) and audit finding F4, quoted whole:

```text
## 2026-09-28 16:01:27 BST · deputy · The approval status bypass: (a) DECIDED, fixed NOW as WK-1178's top priority. Plus S2-plan F4: (i) refuse the approver who authored a suite change

**Confirmed by me at `3a3df367`:**
- `backend/src/app/api/approvals.py:394` `_resolve_rating_version` returns only `row is not None`;
- `backend/src/app/platform/rating_versions.py:283` sets `APPROVED` with no check of the current status;
- `:293` writes `before={"status": RatingVersionStatus.REVIEW.value}` regardless of the real prior state.

So **a draft Rating Version can be approved without `…/submit`**. Every gate submit enforces (FR-260's golden quotes, FR-364's evidence floor) is skippable, and **the audit trail records a false before-state**. That is a governance hole and an audit-integrity defect, live on main.

**(a) DECIDED, and it outranks every other WK-1178 item.** One PR, spec and code in one commit, **after #861 merges** (both touch `approvals.py`; do not widen #861, which is under audit):
1. **The route refuses** an approval request for an artifact version **not in its type's review state**, with a registered error code (409, a state conflict) naming the current state. This applies to **all 7 approvable types**, enumerated by command. The sweep covers every type's `_resolve_*` and every `apply_approval_decision`.
2. **Each `apply_approval_decision` checks the current status in the same transaction** and refuses a transition not permitted from it: defence in depth, so the route is not the only guard.
3. **The audit `before=` is the real prior state, read from the row**, never a literal. The sweep lists every hard-coded `before=` in the approval hooks. At `3a3df367`, `rating_versions.py:293` is one; `metrics.py:537` and `modelling.py:1173` need reading to decide whether theirs are genuine. Each is fixed or justified in the PR.
4. **Negative tests, red then green:** a draft version's approval request is refused (per type, or parametrized), and the audit before-state equals the real state. The reds are quoted against current main.
5. **`06` gains the rule where it is missing** (dated): an approval decision applies only to a version in review. If the spec already says so, cite it; the code then simply failed it (CLAUDE.md §0, the spec right, the code corrected).
6. **The data question, answered in the PR:** does any existing Rating Version (or other type) in a fixture, seed or local DB reach `approved` without having passed through `review`? Checked by query against the Audit Events. There is no production deployment yet, so the blast radius is test and seed data, but it is stated, not assumed.
7. **An FD** (auditor-b, in #855 or a follow-up) records the hole, the live window (since the route was added, per `git log -S`) and this fix, with severity high. **Plan review 15 lists it** among P2's open risks until merged.

**WK-672 S2's plan** cites this PR and **does not merge its FR-260 hook until this fix is on main**. Otherwise S2 would add a check that the bypass can skip.

**S2-plan F4, an approver who authored a SUITE change in the delta: (i) DECIDED, refuse.** If the approver authored any golden-quote change listed in the submission's delta (value, tolerance or context, by the creation-event author definition), the approval is refused with the same 403 class as `APPROVAL_AUTHOR_UNRESOLVED`'s sibling. The suite delta is the evidence the approver is judging, so its author cannot be its judge. **This is not the general component-author case**, which stays carried to WK-677. It applies only to the delta the approver is shown. S2 carries a negative test.
```

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S2-1 | How is a Regression Suite stored and bound to a Rating Version? `03` §5.1 declares no route that writes one | (A) its own versioned artifact behind `POST /api/v1/regression-suites/{slug}/versions`, referenced outside `pins` so the bundle hash stays pins-only; (B) embedded in the draft Rating Version; (C) as (A), but approvable | (A) | decision point | yes | **(A), with the pin-and-delta condition.** The deputy's decision by delegation, 2026-09-28, the entry above; applied in Tasks 2, 4 and 5 |
| DP-S2-2 | Which transition is FR-260's "promotion"? | (a) `POST …/submit`; (b) the approval decision; (c) deployment (WK-674) | (a) | decision point | yes | **(a).** The deputy's decision by delegation, 2026-09-28, the entry above; applied in Task 5 |
| DP-S2-3 | Which pure function does the gate re-score through? | (a) a new `evaluate_golden_quotes` in `rating/testing.py`, which Slice 3's `run_regression` builds on; (b) `run_regression` built early with properties skipped; (c) a backend loop over `score_one`, which breaks RL-1172 item 3c | (a) | decision point | yes | **(a), exact in integer minor units.** The deputy's decision by delegation, 2026-09-28, the entry above; applied in Task 3 |
| DP-S2-4 | A Rating Version whose algorithm has no suite: does submit refuse? | (a) pass, and leave existence to FR-257 limb (1); (b) refuse at submit | (a): FR-260 re-scores "every golden quote", and zero is vacuous; the existence gate is FR-257's "passing Regression Suite", owned by Slice 3 | decision point | no | **(a) as the interim rule, with a visibility condition:** the evidence says `regression_suite: "none"`, shown as "no golden quotes were checked". The deputy's decision by delegation, 2026-09-28, the second entry above; applied in Tasks 2 and 5. Slice 3's leaf plan must decide whether a suite is required (carried) |
| DP-S2-5 | Audit finding F1: the generic approval route approves a `draft` Rating Version without `…/submit`, so the FR-260 gate is skippable. Who fixes it? | (a) fixed now, outside S2, as WK-1178's top-priority PR; (b) inside S2's Task 5 | (a), the lead's recommendation | decision point | yes (Task 5 only) | **(a).** The deputy's decision by delegation, 2026-09-28, the third entry above. S2 cites "the WK-1178 approval-status PR" and does not merge its hook before it (Global Constraints; Task 5 Step 0) |
| DP-S2-6 | Audit finding F4: may a principal who authored a suite change in the delta approve the Rating Version? | (i) refuse, 403 with a named code; (ii) allow, since the change is visible | none; the planner does not pick this | decision point | yes (Task 5 only) | **(i) refuse.** The deputy's decision by delegation, 2026-09-28, the third entry above; `APPROVAL_BY_EVIDENCE_AUTHOR`, 403; not the general component-author case (WK-677). Applied in Task 1 Step 8 and Task 5 |

### Sequencing

Tasks 1 → 6 in order, each with its own commit. Task 1 (spec) lands first because it is the
design every later task implements (`CLAUDE.md` §0). Task 2's shapes feed Tasks 3–5.

---

## Tasks

### Task 1: Spec change — `03` §2, §3.8, §4.3, §4.7, §4.9, §5.1, §5.2

**Files:**
- Modify: `docs/specs/03-rating-engine.md`; `docs/specs/06-governance.md` (the error-code list at `06:491` and the FR-353 rows, Step 8 only)

**Interfaces:**
- Consumes: the deputy's decisions (above), RL-1172 item 3c and the F4 assertion-language ruling.
- Produces: the declared shapes, routes and signature that Tasks 2–5 implement.

- [ ] **Step 1: Glossary (`03:68`).** Append to the Golden Quote row: *"(Amended 2026-09-28, `PL-WORKING`: stored in a versioned Regression Suite bound to a Rating Algorithm by `algorithm_slug`, not inside a Rating Version, which is immutable after `draft`; the Rating Version's evidence pins the suite version it was checked against.)"*
- [ ] **Step 2: FR-260 (`03:176`).** Append this dated amendment. It mints no id:

  > *(Amended 2026-09-28, the deputy's DP-S2-1 and DP-S2-2 decisions by delegation, `PL-WORKING`.)*
  >
  > - The check runs at `POST /api/v1/rating-versions/{id}/submit`.
  > - The submission's evidence pins the suite version it used, by content hash.
  > - The evidence lists every golden quote added, removed, or whose expected output, tolerance or quote context changed since the suite pinned by the most recently approved Rating Version of the same algorithm. Each change names its author, who is the actor of the creation Audit Event of the suite version that introduced it (`06` FR-368).
  > - Where the algorithm has no suite, the evidence says so explicitly (`regression_suite: "none"`, "no golden quotes were checked"), never an empty pass. Whether a suite is required is decided by WK-672 Slice 3.

- [ ] **Step 3: §4.3 evidence.** Add `"golden_quotes": {"suite_ref": "regression_suite:motor-gb-core@4", "suite_content_hash": "sha256:…", "bundle_hash": "sha256:…", "results": ["…§4.9 golden_results items…"], "delta": {"baseline_rating_version_ref": "rating_version:motor-gb@26", "baseline_suite_ref": "regression_suite:motor-gb-core@3", "baseline_suite_content_hash": "sha256:…", "changes": [{"name": "young-driver-london", "change": "changed", "changed_fields": ["expected"], "before": {"payable_premium_minor": 112480, "outcome": "quoted"}, "after": {"payable_premium_minor": 112900, "outcome": "quoted"}, "steps": [{"version": 4, "changed_fields": ["expected"], "author": "…principal uuid…"}]}]}}` to the `evidence` example, with `"status": "checked"`. Show the no-suite form beside it: `{"status": "not_checked", "regression_suite": "none", "message": "no golden quotes were checked", "reason": "no_suite_for_algorithm"}`. Add one invariant sentence: `evidence.golden_quotes` is written only by the submit gate and never edited after.
- [ ] **Step 4: §4.7.** Replace the example with the Task 2 shape. It carries `slug`, `version`, `algorithm_slug`, `change_note`, `content_hash`, `golden_quotes` (each with `name`, `context`, `expected`, `tolerance`, `note`), `properties` (each `{"name", "check": {"kind": …}}`, one of the five kinds with the fields in Task 2) and `generation`. Add a dated note: *"Corrected 2026-09-28 (`RL-1172` item 3c; the deputy's F4 assertion-language ruling): the free-text `assertion` strings are replaced by a structured union of FR-261's five classes. This artifact stores them; WK-672 Slice 3 evaluates them. The earlier example's relative bound (`20 * risk_premium_minor`) is not one of the five classes and is dropped; a bound is absolute, in minor units."* `expected` compares `payable_premium_minor` (the `payable_premium` ladder rung's `value_minor`) and `outcome` only, never `timing_ms` (RL-931).
- [ ] **Step 5: §4.9.** Change the contract citation from `regression-suite.schema.json` to `regression-run.schema.json`, with a dated clause saying Task 2 split the file.
- [ ] **Step 6: §5.1.** Add two rows after the `rating-versions/{id}/submit` row:
  - `POST` `/api/v1/regression-suites/{slug}/versions`: "Create a new Regression Suite version; `rating:write`; **201** (FR-260)".
  - `GET` `/api/v1/regression-suites/{slug}@{version}`: "Read a Regression Suite version; `rating:read`; access-controlled per NFR-499 (FR-260)".

  Amend the submit row's purpose to add "golden quotes re-scored and the suite pinned (FR-260)".
- [ ] **Step 7: §5.2.** Add to the `testing.py` block:
  ```python
  def evaluate_golden_quotes(bundle: CompiledBundle, golden_quotes: Sequence[GoldenQuote],
                             *, rating_version_ref: ArtifactRef) -> list[GoldenQuoteResult]
  ```
  Add a dated sentence to the note below the block. It says the function is plain `def` on the same synchronous `evaluate()` path as `run_regression` (RL-868, RL-858), that it compares exactly in integer minor units, and that `run_regression` composes it (DP-S2-3).
- [ ] **Step 8: `06` (DP-S2-6).** Add `APPROVAL_BY_EVIDENCE_AUTHOR` to `06`'s error-code list (`06:491`), dated, and add one dated sentence beside FR-353 (as #861 amended it at your tree): *"(Added 2026-09-28, `PL-WORKING`, the deputy's decision on audit finding F4.) For a Rating Version, an approver who authored any golden-quote change listed in the submission's delta (`03` FR-260) is refused with `APPROVAL_BY_EVIDENCE_AUTHOR` (403). This is not the general component-author rule, which WK-677 owns."* Re-read FR-353 at your tree first: #861 amends it.
- [ ] **Step 9:** Run `python3 scripts/audit-docs.py`. It must add no failure row, and every cited FR and NFR is defined. Then commit: `docs(spec): 03 — Regression Suite store, submit-time golden-quote gate, pinned suite and delta (FR-260)`.

### Task 2: `model-schema` shapes, the generated contract, and the authored-file split

**Files:**
- Create: `packages/model-schema/src/model_schema/regression.py`; `packages/model-schema/tests/test_regression.py`; `docs/contracts/schemas/regression-run.schema.json` (hand-authored, moved out of `regression-suite.schema.json`); `docs/contracts/schemas/generated/regression-suite.schema.json` (generated)
- Modify: `packages/model-schema/src/model_schema/__init__.py` (exports); `packages/model-schema/src/model_schema/rating.py:116` (`RatingVersionEvidence` gains `golden_quotes`); `scripts/generate-contracts.py:38-127` (`GENERATED_SHAPES` gains `"regression-suite": "RegressionSuite"`); `docs/contracts/schemas/regression-suite.schema.json` (the `RegressionSuite` part rewritten to the Task 1 shape, and `RegressionRun` removed); `backend/tests/test_contracts.py` (`COMPARED_SLUGS` at `:38` gains `regression-suite`; `ONE_SIDED_SLUGS` at `:67` drops it and gains `"regression-run": "authored-only until WK-672 Slice 3 builds it — 03 §4.9"`)

**Interfaces.** It produces the following. Every model is `ConfigDict(frozen=True, extra="forbid")`.

```python
GoldenQuoteExpected:  payable_premium_minor: MoneyMinor | None; outcome: ScoringOutcome
                      # None exactly when outcome != "quoted" (model validator)
GoldenQuoteTolerance: money_minor: int = Field(default=0, ge=0, strict=True)
GoldenQuote:          name: Slug; context: QuoteContext; expected: GoldenQuoteExpected
                      tolerance: GoldenQuoteTolerance = GoldenQuoteTolerance(); note: str | None = None
# FR-261's five classes, a union discriminated on `kind`:
PremiumPositive:   kind: Literal["premium_positive"]
MonotoneInInput:   kind: Literal["monotone"]; input: str (min_length=1)
                   direction: Literal["increasing", "decreasing"]; strict: bool = False
                   lower: DecimalStr | None = None; upper: DecimalStr | None = None   # lower <= upper when both set
NoNullOutput:      kind: Literal["no_null_output"]
LadderReconciles:  kind: Literal["ladder_reconciles"]                               # FR-248
PremiumBounded:    kind: Literal["premium_bounded"]
                   lower_minor: MoneyMinor | None = None; upper_minor: MoneyMinor | None = None
                   # at least one set; lower_minor <= upper_minor when both set
PropertyCheck = Annotated[PremiumPositive | MonotoneInInput | NoNullOutput | LadderReconciles
                          | PremiumBounded, Field(discriminator="kind")]
RegressionProperty:   name: Slug; check: PropertyCheck
RegressionGeneration: cases: int = Field(ge=1); seed: int = Field(ge=0)
                      strategy: Literal["input_contract_sampling"]
RegressionSuiteContent: algorithm_slug: Slug; golden_quotes: list[GoldenQuote]
                        properties: list[RegressionProperty]; generation: RegressionGeneration
                        # unique golden_quotes[].name; unique properties[].name
RegressionSuite:      slug: Slug; version: int = Field(ge=1); change_note: str (min_length=1)
                      content_hash: str (pattern ^sha256:[a-f0-9]{64}$)
                      created_at: datetime; created_by: UUID; plus the RegressionSuiteContent fields
GoldenQuoteResult:    name: str; status: Literal["pass", "fail"]
                      expected_minor: MoneyMinor | None; actual_minor: MoneyMinor | None
                      difference_minor: int | None          # = 03 §4.9 golden_results[], field for field
GoldenQuoteChange:    name: str; change: Literal["added", "removed", "changed"]
                      changed_fields: list[Literal["expected", "tolerance", "context"]]
                      # non-empty exactly when change == "changed"; empty otherwise (model validator)
                      before: GoldenQuoteExpected | None; after: GoldenQuoteExpected | None
                      before_tolerance: GoldenQuoteTolerance | None; after_tolerance: GoldenQuoteTolerance | None
                      before_context_hash: str | None; after_context_hash: str | None
                      # sha256 of the canonical context JSON; the context itself is never copied here (NFR-499)
                      steps: list[GoldenQuoteChangeStep]   # non-empty; ascending version
GoldenQuoteChangeStep: version: int; changed_fields: list[Literal["added", "removed", "expected", "tolerance", "context"]]
                      author: UUID
                      # one per suite version in (baseline, current] that changed this quote's expected,
                      # tolerance or context, or added or removed it; a version changing only `note` is no step
GoldenQuoteDelta:     baseline_rating_version_ref: ArtifactRef | None; baseline_suite_ref: ArtifactRef | None
                      baseline_suite_content_hash: str | None; changes: list[GoldenQuoteChange]
GoldenQuoteCheck:     status: Literal["checked"]; suite_ref: ArtifactRef; suite_content_hash: str
                      bundle_hash: str; results: list[GoldenQuoteResult]; delta: GoldenQuoteDelta
GoldenQuoteNotChecked: status: Literal["not_checked"]; regression_suite: Literal["none"]
                      message: Literal["no golden quotes were checked"]
                      reason: Literal["no_algorithm_ref", "no_suite_for_algorithm"]
GoldenQuoteEvidence = Annotated[GoldenQuoteCheck | GoldenQuoteNotChecked, Field(discriminator="status")]
def context_hash(context: QuoteContext) -> str   # same canonical form as suite_content_hash
def suite_content_hash(content: RegressionSuiteContent) -> str
    # "sha256:" + sha256 of json.dumps(content.model_dump(mode="json"), sort_keys=True,
    #  separators=(",", ":")).encode()
```

The delta is **not** its own generated slug. It is embedded in `RatingVersionEvidence.golden_quotes`, because it exists only as a Rating Version's evidence.

- [ ] **Step 1: Write the failing tests** in `test_regression.py`, one per acceptance item 3 clause, before `regression.py` exists. Run `uv run pytest packages/model-schema/tests/test_regression.py -v`. Expected: an `ImportError` on `model_schema.regression`, and nothing else.
- [ ] **Step 2: Implement `regression.py`**, export every name from `model_schema/__init__.py`, and add `golden_quotes: GoldenQuoteEvidence | None = None` to `RatingVersionEvidence` (`rating.py:116`). `None` means "not yet submitted"; a submitted version always carries one of the two variants. Re-run until green.
- [ ] **Step 3: Split the authored contract.** Read `.claude/skills/contract-guard/SKILL.md` first. Move the `RegressionRun` `$defs` entry to a new `regression-run.schema.json` unchanged. Rewrite `regression-suite.schema.json`'s suite definition to the Task 1 shape. Add the `GENERATED_SHAPES` entry, run `uv run python scripts/generate-contracts.py`, and update `COMPARED_SLUGS` and `ONE_SIDED_SLUGS` as the Files block says. Then run `uv run pytest backend/tests/test_contracts.py -q`.
  - Expected: pass. Any comparison failure is an authored/generated disagreement. Fix the authored side to match the model, because the model is the source (ADR-704).
  - `test_every_one_sided_slug_is_declared` failing on `regression-run` means the label entry is missing.
- [ ] **Step 4:** `uv run mypy && uv run ruff check packages/model-schema`, then commit: `feat(model-schema): RegressionSuite, GoldenQuote, the five-class property union and the golden-quote evidence shapes (FR-260, FR-261)`.

### Task 3: `pricing-core` — `evaluate_golden_quotes`

**Files:**
- Create: `packages/pricing-core/src/pricing_core/rating/testing.py`; `packages/pricing-core/tests/test_testing.py`
- Modify: `packages/pricing-core/src/pricing_core/rating/score.py`. Extract the synchronous single-context body of `_score_batch_row` (`:914`) into a private `_score_context_sync(bundle: CompiledBundle, ctx: QuoteContext, rating_version_ref: ArtifactRef) -> ScoringResult`. It runs `_validate_inputs` (`:329`), `_check_purpose_mount` (`:391`), `_check_billing_surface` (`:414`), `bundle.decision.evaluate(context)` and `build_scoring_result` (`:707`). `_score_batch_row` calls it, and its behaviour is unchanged.

**Interfaces:**
- Consumes: `CompiledBundle` (`rating/runtime.py:544`); `GoldenQuote` and `GoldenQuoteResult` (Task 2).
- Produces: `def evaluate_golden_quotes(bundle: CompiledBundle, golden_quotes: Sequence[GoldenQuote], *, rating_version_ref: ArtifactRef) -> list[GoldenQuoteResult]`. It returns one result per quote, in input order.

**The rule.** `actual` is the `payable_premium` rung's `value_minor` when `outcome == "quoted"`, and `None` otherwise.
- **`pass`** requires two things:
  - `outcome` equals `expected.outcome`;
  - when both are `quoted`, `abs(actual - expected) <= tolerance.money_minor`. The subtraction is integer.
- **`difference_minor`** is `actual - expected` when both are integers, and `None` otherwise.
- **A `PlatformError`-free engine refusal** (input contract, purpose mount) for one quote becomes that quote's `fail`, with `actual_minor=None`. It never aborts the rest.

- [ ] **Step 1:** Write the acceptance item 4 tests against a small compiled bundle. Mirror the fixture `packages/pricing-core/tests` already uses for `score_batch`; do not invent a new one. Run them. Expected: an `ImportError` on `pricing_core.rating.testing`.
- [ ] **Step 2:** Do the `_score_context_sync` extraction first, as a pure move. **Its authority** is DP-S2-3 (a), the deputy's decision quoted above, which puts the re-score in `pricing-core` on the synchronous engine path, together with RL-1172 item 3a, which rules that path the regression executor's. That departs from `PL-930`'s Slice 2 text, "Reuses `score_one` and `CompiledBundle` unchanged": the public `score_one`, `score_batch` and `CompiledBundle` stay unchanged, and only a private helper is extracted (audit finding F10). It must not change threading: no new thread, executor or lock, and `bundle.decision.evaluate` is called exactly as before. Run `uv run pytest packages/pricing-core -q` and confirm the same passed count as the base, so `score_batch` is unchanged. Then run `uv run pytest packages/pricing-core/tests/test_rating_score.py -q` **five times** and record each rc. **If any of the five aborts natively (a negative rc, or a `PyGILState` message), the slice does not pass its gate:** it stops, the run's output goes to the lead, and the finding's triage moves ahead of this slice. It is never re-run until green.
- [ ] **Step 3:** Implement `testing.py`. Re-run the new tests, then run `uv run lint-imports`.
- [ ] **Step 4:** Commit: `feat(pricing-core): evaluate_golden_quotes — exact integer re-score on the synchronous engine path (FR-260)`.

### Task 4: The suite store, its routes and its creation event

**Files:**
- Create: `backend/migrations/versions/<rev>_regression_suite_versions.py`, with `down_revision = "d3b955a63d6a"`, the head at `ea6162b9`. Re-read the head at your tree. `backend/src/app/platform/regression_suites.py`; `backend/src/app/api/regression_suites.py`; `backend/tests/test_regression_suites.py`
- Modify: `backend/src/app/db/models.py`, adding two rows after `RateTableCellRow` (`:2013`):
  - `RegressionSuiteRow`, table `regression_suites`: `id`, `workspace_id`, `slug`, `algorithm_slug`, `created_at` and `created_by`. It is unique on `(workspace_id, slug)` **and** on `(workspace_id, algorithm_slug)`. This is the one-suite-per-algorithm rule, enforced by the database, not by check-then-insert (audit finding F6).
  - `RegressionSuiteVersionRow`, table `regression_suite_versions`: `id`, `suite_id` (FK to `regression_suites.id`), `version`, `content` JSONB, `content_hash`, `change_note`, `created_at` and `created_by`. It is unique on `(suite_id, version)`. Also modify `backend/src/app/main.py:122-143` to register the router with `prefix=API_PREFIX`.

**Interfaces:**
- `async def create_suite_version(session, *, workspace_id: UUID, actor: Principal, slug: str, content: RegressionSuiteContent, change_note: str) -> RegressionSuiteVersionRow`. It mirrors `rating_versions.create_rating_version` (`rating_versions.py:166`):
  - `rbac.require_permission(..., permission=Permission.RATING_WRITE)`;
  - next version `1 + coalesce(max(version), 0)`;
  - `content_hash = suite_content_hash(content)`;
  - `audit.record(session, workspace_id=…, actor=actor, source=JobSource.API, action="regression_suite.created", entity_ref=f"regression_suite:{slug}@{version}", before={}, after={"content_hash": …, "change_note": …, "algorithm_slug": …, "golden_quote_names": [...]})`. **`after` carries no `context`** (NFR-499).
  - The first version of a slug inserts its `regression_suites` row in the same transaction. An `IntegrityError` on either unique constraint is mapped to 409 `VALIDATION_FAILED` ("this algorithm already has a Regression Suite"). There is no pre-check to race.
  - A later version whose `content.algorithm_slug` differs from its registry row's is refused with 409 `VALIDATION_FAILED`.
- `async def load_suite_version(session, *, workspace_id, actor, slug, version) -> RegressionSuiteVersionRow`, which requires `RATING_READ`. Also `async def current_suite_for_algorithm(session, *, workspace_id, algorithm_slug) -> RegressionSuiteVersionRow | None`, which returns the highest version of the one suite the registry holds for that algorithm (unambiguous by the constraint).
- Routes: `POST /regression-suites/{slug}/versions` (201, `requires(Perm.RATING_WRITE)`) and `GET /regression-suites/{slug}@{version}` (`requires(Perm.RATING_READ)`). Both return `RegressionSuite`. Their `responses=problems(...)` follow the `/rating-versions` routes (`api/models.py:1154-1190`).

- [ ] **Step 1:** Write the acceptance item 5 tests using the DB fixtures `database`, `workspace_id`, `principal`, `grant` and `membership` (`backend/tests/conftest_db.py`). Check the DB stack is up first; never assume it. Run them. Expected: an import failure on `app.platform.regression_suites`.
- [ ] **Step 2:** Add the row, the migration, the service, the routes and the router registration. Run `alembic upgrade head` then `downgrade -1` then `upgrade head` with `dev-commands`' DSN. Re-run until green.
- [ ] **Step 3:** Commit: `feat(rating): Regression Suite store — versioned, access-controlled, creation-audited (FR-260, NFR-499, FR-368)`.

### Task 5: The submit gate, the pin, and the delta

**Files:**
- Modify: `backend/src/app/platform/rating_versions.py`, in `submit_for_review` (`:214-249`), two new private helpers and a public `golden_quote_delta_authors`; `backend/src/app/api/models.py`, in the submit handler (`:1182-1190`); `backend/src/app/platform/approvals.py`, in `decide` (`:237`, as #861 left it); `backend/src/app/api/approvals.py`, in the decide handler; `backend/src/app/errors.py`, adding `APPROVAL_BY_EVIDENCE_AUTHOR` to `GOVERNANCE_ERROR_CODES` (`:248`)
- Test: `backend/tests/test_rating_versions.py`

**Interfaces.** `submit_for_review` gains a keyword `load_compiled: Callable[[ArtifactRef], Awaitable[CompiledBundle]]`.
- The route supplies it by wrapping `api/score.py`'s `_fetch_bundle` (`:139`). **Never `_compiled_for` (`:206`)**, which degrades to the slot's last-known-good bundle when metadata storage is down. A governance gate refuses rather than degrade (audit finding F5). Bundle fetching stays in the API layer, and the service can be tested with a real or a stubbed loader.

The order inside `submit_for_review`, after the existing status check and **before** `approvals.submit`, so it fails fast:
1. **Find the suite.** If `row.algorithm_ref` is set, `suite = current_suite_for_algorithm(algorithm_slug=ArtifactRef.parse(row.algorithm_ref).slug)`. If there is no algorithm ref or no suite, write `evidence.golden_quotes = GoldenQuoteNotChecked(status="not_checked", regression_suite="none", message="no golden quotes were checked", reason=…)` and continue to `approvals.submit` (DP-S2-4, the deputy's interim rule with its visibility condition).
2. **Load the bundle.** If `row.bundle` is null, raise 409 `BUNDLE_COMPILE_FAILED` ("compile before submitting: a suite exists for this algorithm"). Otherwise `bundle = await load_compiled(ref)`. **If `bundle.content_hash` (`rating/runtime.py:559`) differs from `row.bundle["content_hash"]`, raise 409 `BUNDLE_COMPILE_FAILED`** ("the loaded bundle is not this version's bundle") and write nothing.
3. **Re-score.** `results = evaluate_golden_quotes(bundle, suite.golden_quotes, rating_version_ref=ref)`. If any is `fail`, raise `PlatformError("GOLDEN_QUOTE_MISMATCH", "Golden quote mismatch", 409, detail=<the failing names>)`. Nothing is written, and the version stays `draft`.
4. **Build the delta.** `delta = await _golden_quote_delta(session, workspace_id, algorithm_slug, suite, exclude_id=row.id)`, as specified below.
5. **Pin the evidence.** Write `row.evidence["golden_quotes"] = GoldenQuoteCheck(status="checked", suite_ref=regression_suite:{slug}@{version}, suite_content_hash=suite.content_hash, bundle_hash=bundle.content_hash, results=results, delta=delta).model_dump(mode="json")`. Then call `approvals.submit` as today.

**`_golden_quote_delta`: where the baseline comes from, and the author of each change.**
- **The baseline Rating Version** is the most recently approved version of the same algorithm, excluding this one.
  - Candidates are `RatingVersionRow`s in the workspace whose `algorithm_ref` slug equals `algorithm_slug` and whose status is `approved`, `live` or `retired`.
  - They are ordered by the `at` of their `rating_version.approved` Audit Event, newest first. The action is written at `rating_versions.py:291`. The audit trail is the one governance source, as in the deputy's author definition.
  - The first candidate is the baseline. Its `evidence.golden_quotes.suite_ref` and `suite_content_hash` are the baseline suite.
- **No baseline**, or a baseline whose `golden_quotes` is `not_checked` or absent: every current golden quote is `added`, and the three baseline fields are null.
- **Comparing** baseline content with current content, by golden-quote `name`:
  - `added`: in current, not in baseline;
  - `removed`: in baseline, not in current;
  - `changed`: in both, with `expected`, `tolerance` or `context` unequal. `changed_fields` names which, in that order. **Tolerance and context changes are required, not optional** (the deputy's 15:57:21 item (ii)): widening a tolerance or swapping the quote under test weakens the check exactly as editing the expected value does. A context change is recorded by `before_context_hash`/`after_context_hash`, never by copying the context (NFR-499).
- **The authors of each change** are found by walking the suite's versions from `baseline_version + 1` to the current version, comparing each version with the one before it. **Every** version in that range that added or removed the quote, or changed its `expected`, `tolerance` or `context`, becomes one `GoldenQuoteChangeStep`, in ascending version order. A version that changed only fields the delta does not compare (`note`) is no step, so a later cosmetic edit cannot mask a substantive one (audit finding F3). Each step's `author` is the principal id in the `actor` of that version's `regression_suite.created` Audit Event, read from `AuditEventRow` (`db/models.py:164`), never from `created_by`. That is the deputy's one-source definition, the same one #861 uses.
- **If that event is missing, raise `APPROVAL_AUTHOR_UNRESOLVED` with status 403.** That is #861's fail-closed code, and a reused code keeps the status #861 registers. **Before Step 1, confirm #861 has merged** (`git log --grep '(#861)' -1 origin/main` prints its squash). If it has not, stop and report: the code and the creation-event semantics are #861's. A test covers the missing-event case: a suite version whose `regression_suite.created` event is deleted in the fixture makes submit refuse with `APPROVAL_AUTHOR_UNRESOLVED`, 403.

**The evidence-author refusal (DP-S2-6).** `approvals.decide` gains a keyword `evidence_authors: EvidenceAuthorResolver | None`, a `Protocol` in the same form as `ArtifactResolver` (`approvals.py:64`), so `approvals` imports nothing from `rating_versions`. The decide route passes `rating_versions.golden_quote_delta_authors` for `artifact_type == "rating_version"`. It returns the set of `author`s over every step of every change in the version's `evidence.golden_quotes.delta`, empty when the evidence is `not_checked`. `decide` refuses with 403 `APPROVAL_BY_EVIDENCE_AUTHOR` when the approver's id is in that set, **before** any decision row is written. It is placed immediately after #861's author check; read `decide` at your tree for the exact place.

- [ ] **Step 0: Preconditions.** Run `git log --grep '(#861)' -1 origin/main` and the same for the WK-1178 approval-status PR's number (the lead gives it). If either prints nothing, **stop and report**: Task 5 needs #861's author definition and code, and must not merge its hook while the generic route can skip it.
- [ ] **Step 1:** Write the acceptance item 6, 7, 8 and 8a tests. Acceptance item 8's main test is written and run **before** Step 3, against a gate that pins but builds no delta, and must fail on the missing `changes` entry. Quote that red run in the ledger.
- [ ] **Step 2:** Implement the gate and the pin (order steps 1–3 and 5), with the delta stubbed as an empty `GoldenQuoteDelta`. Acceptance items 6 and 7 go green, and item 8 stays red for the predicted cause.
- [ ] **Step 3:** Implement `_golden_quote_delta` and the author walk. Everything goes green.
- [ ] **Step 4:** Confirm the existing `test_create_submit_approve_a_rating_version` (`backend/tests/test_rating_versions.py:66`) still passes unchanged. It is the no-suite path. Then commit: `feat(rating): submit-time golden-quote gate, pinned suite hash and the approver's delta (FR-260)`.

### Task 6: The slice gate and the ledger

- [ ] **Step 1:** Run the full two-half gate and the five-run determinism repeat (acceptance item 9), each process started with `env -C <worktree>`, and record every exit code and the `HEAD` in the slice's `LG-` ledger (id from the lead).
- [ ] **Step 2:** Run the four docs checks on a detached copy (acceptance item 10).
- [ ] **Step 3:** Record `git diff --stat origin/main...HEAD` (acceptance item 11) in the ledger.
- [ ] **Step 4:** Open the PR. The auditor's pass and the deputy's acknowledgement follow (acceptance item 12).

---

## Self-review

**1. Spec coverage.** Each item maps to a task:
- FR-260's store, re-score and refusal: Tasks 2, 3, 4 and 5.
- The deputy's condition item 1 (pin): Task 5 step 5, acceptance item 7.
- Condition item 2 (the delta, its baseline and its author): Task 5 `_golden_quote_delta`, acceptance item 8.
- Condition item 3 (red then green): Task 5 steps 1–3, acceptance item 8.
- DP-S2-2 (submit): Task 5. DP-S2-3 (a pure exact function): Task 3.
- FR-261 stored as the five-class union: Task 2.
- NFR-499: Tasks 4 and 5.
- FR-368: Tasks 4 and 5.

Every ruling site was checked across narrative, Files, Steps and Acceptance (`docs/plans/README.md` convention 5).

**2. Placeholder scan.** Two exact values are left to the executor's tree:
- the new migration's revision hash, which Alembic generates;
- `<rev>` in its filename.

Both are named as such. `PL-WORKING` in Task 1's inserted text is this plan's working id, replaced at the mint by the renumber commit.

**3. Literals, checked against the shipped source at `ea6162b9`.** None comes from memory:
- `MoneyMinor` (`money.py:61`) and `DecimalStr` (exported, `__init__.py:183`);
- `ScoringOutcome` and `LadderRung` (`scoring.py:70`, `:127`); the payable premium is a ladder rung, not a field;
- `RatingVersionEvidence` (`rating.py:116`); `RatingVersionRow.evidence` is JSONB;
- `GENERATED_SHAPES` (`generate-contracts.py:38`); `COMPARED_SLUGS` and `ONE_SIDED_SLUGS` (`test_contracts.py:38`, `:67`);
- `audit.record` (`audit.py:52`); `rbac.require_permission` (`rbac.py:274`);
- `create_rating_version` (`rating_versions.py:166`); `submit_for_review` (`:214`); `rating_version.approved` (`:291`);
- `_fetch_bundle` (`api/score.py:139`), used, and `_compiled_for` (`:206`), refused; `CompiledBundle.content_hash` (`rating/runtime.py:559`); the head migration `d3b955a63d6a`;
- the DB fixtures (`conftest_db.py`); `Permission.RATING_WRITE` and `RATING_READ`.

**4. Rulings between the sweep and the PR.** These were read before the push:
- #861, open: the author definition and `APPROVAL_AUTHOR_UNRESOLVED` (registered at 403) are consumed and not redefined, and Task 5 waits for its merge;
- #855 and #856, open: cited by PR number;
- #860, open: the mint waits for it.

None changes this slice's subject beyond what is applied above.
