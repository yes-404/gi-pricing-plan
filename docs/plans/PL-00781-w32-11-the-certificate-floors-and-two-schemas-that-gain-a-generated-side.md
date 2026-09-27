---
id: PL-781
family: plan
kind: leaf
title: W32-11 — the certificate floors, and two schemas that gain a generated side
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-24
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-24-w32-11-certificate-floors-and-two-generated-sides.md
---

# W32-11 — the certificate floors, and two schemas that gain a generated side

**Written 2026-08-24.** The slice [`PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md`](PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md)
did not contain. It was allocated on 2026-08-24 when that proposal's Part C was decided: two of the
three rows there — one *reassigned*, one *not started* — turned out to be the same backend
[`../../CLAUDE.md`](../../CLAUDE.md) §2 contract work, and both were unowned. **This is the last
slice before closure** (maintainer instruction, 2026-08-24): WK-692 does not close until it lands, and
does not stay open for anything discovered inside it — see Task 5.

## Goal

Give `ObjectiveCertificate` and `MetricCertificate` the check-count floors FR-158 requires,
and give `dataset-version` and `validation-report` a generated side so the drift guard can see
them. Two items, three commits, one Part C row each.

## What is already decided, and is not reopened here

- **OQ-600 is decided: option (a)**, on the maintainer's instruction, 2026-08-23. Leave
  `CertificateResult` unbounded; enforce nine checks on `ObjectiveCertificate` and four on
  `MetricCertificate` where each is constructed; correct the authored contract to `minItems: 9`.
- **Option (b), splitting the shared type, was rejected** because it "would duplicate a shape
  `CLAUDE.md` §2 says must exist once". **Option (c), publishing the floor unenforced, was also
  rejected.** Neither is available to this slice.
- **OQ-600 is directive about atomicity**: the carve-out
  `UNRESOLVED_CONSTRAINT_DISAGREEMENTS["objective-certificate"]` "must be removed in the same
  commit that makes the two sides agree". Task 1 is therefore one commit and may not be split.
  **The mechanism runs the opposite way to the intuitive reading**, which is worth stating because
  the intuitive reading was written down once and corrected: bumping the authored floor 8 → 9 on its
  own leaves the pair *disagreeing* (generated `1` against authored `9`), so the carve-out test keeps
  passing. It is the **narrowings** that force the atomicity — unbinding the shared type makes the
  generated side emit no `minItems` at all (M5), the double intersection skips it (M6), the pair
  stops disagreeing, and the test asserting it still does goes red unless the carve-out leaves in the
  same commit. M7's `102 passed, 1 skipped` is that sequence completed.

## What was measured before this plan was written

Measured 2026-08-24 against `faff060`, in a throwaway worktree, every probe reverted. **Recorded so
that execution does not repeat it** — and because two of these facts contradict what the closure
proposal's readers assumed.

| # | Question | Measured answer |
|---|---|---|
| M1 | Is the certificate result inlined per file, or `$ref`'d? | **`$ref`** into a per-file `$defs`. `properties.result` is `{"$ref": "#/$defs/CertificateResult"}`; the OpenAPI document shares a single component |
| M2 | Does a bare `@model_validator` move the generated schema? | **No.** Nothing moves; `minItems` stays 1. Runtime only |
| M3 | Does `Field(json_schema_extra=...)` reach the nested schema? | **No.** Dict and callable forms both emit a `$ref` **sibling** at `result`; the callable is handed `{'$ref': ...}` and cannot reach `properties` |
| M4 | Does a narrowed subtype emit the floor? | **Yes**, in place, blast radius confined to objective-certificate — but only by making the type not shared, i.e. rejected option (b) |
| M5 | With `min_length=1` removed, what does generated emit? | `minItems` **absent entirely**, not `0`, in both certificate files |
| M6 | What does the guard do with a keyword present on one side only? | **Silently skips it, both directions.** The comparison is a double intersection over paths then keywords; the docstring calls a one-sided constraint "a difference of intent" |
| M7 | Does option (a) leave the suite green with the carve-out deleted? | **Yes.** `102 passed, 1 skipped` — the skip is the carve-out test collecting zero cases, not an error |

**M6 and M7 are the load-bearing pair.** They are why this slice is executable as decided, rather
than a §0 finding that FR-158 asks for a shape the pipeline cannot express.

## Three findings the decision did not contemplate

Each gets a §13 verdict in the ledger, and a disposition below. **None blocks the slice, and none
holds WK-692 open**; none is silently absorbed either.

| # | Finding | Why it matters |
|---|---|---|
| F1 | With the shared type unbounded the floor is published **only on the authored side** — generated emits none, and the OpenAPI document's one shared `CertificateResult` component carries none | A client generated from the contract gets no floor. Enforcement is server-side only |
| F2 | **No authored-keyword completeness check exists** — none of the tests in the contract module asserts that an authored keyword has a generated counterpart | Nothing would catch the authored `9` drifting later. The module's own comment records this gap letting `gbm.quantile_crossing` sit missing for months with a green suite |
| F3 | **`metric-certificate` has no authored contract at all** — it is in neither the compared-slug list nor `docs/contracts/schemas/` | Its four-check floor is model-side only and uncompared by construction |

F1 and F2 together mean Task 1 makes the two sides agree **by not comparing them**. That is a true
statement about this guard, and it is written down rather than left for the next auditor.

## Task 1 — the floors, the contract, and the carve-out, in one commit

Evidences FR-158, and FR-148 and FR-157 for the two batteries.

1. Delete `min_length=1` from `CertificateResult.checks`
   (`packages/model-schema/src/model_schema/objectives.py`). The shared type becomes unbounded, as
   FR-158 requires. **Do not** add a floor to it, and do not subclass it.
2. Add a `@model_validator(mode="after")` to `ObjectiveCertificate` requiring **nine** checks.
   Assert the nine **names**, not merely the count — the nine are already enumerated in
   `pricing_core.modelling.objectives` and in the authored `name` enum, and a count-only check
   admits a certificate with `branch_discontinuity` missing and something else duplicated.
3. Add the equivalent to `MetricCertificate` (`metrics.py`) for the **four** of FR-157.
4. Write the negative tests first, in `packages/model-schema/tests/`. **Today a battery of one
   passes both models** — measured: the package suite is green with the floor removed — so these
   tests are the whole evidence that the behaviour can fail. Two per certificate: a short battery is
   rejected, and a battery of the right length carrying a wrong name is rejected.
5. Correct `docs/contracts/schemas/objective-certificate.schema.json` `minItems` **8 → 9**. Record
   in that file's `description` that 8 was a stale pre-amendment count, dated.
6. Delete the `"objective-certificate"` entry from `UNRESOLVED_CONSTRAINT_DISAGREEMENTS`
   (`backend/tests/test_contracts.py`) **and its preceding rationale block**. Confirm
   `test_the_escalated_constraint_disagreements_are_still_unresolved` then reports **skipped with an
   empty parameter set**, not an error.
7. Regenerate and confirm what moved: `uv run python scripts/generate-contracts.py`, then
   `git status --short docs/contracts/`. Expect the OpenAPI document and both generated certificate
   schemas to move, because the shared type lost a keyword.
8. **This slice changes the OpenAPI document, so the frontend half of the gate is required.**

## Task 2 — `dataset-version` gains a generated side

Evidences FR-451, and closes the first half of Part C's third row.

1. Add the `dataset-version` → `DatasetVersion` entry to `GENERATED_SHAPES`
   (`scripts/generate-contracts.py`), with the per-addition comment that file's entries carry.
2. Register the slug in the compared-slug list (`backend/tests/test_contracts.py`) — forced, not
   optional: `test_every_eligible_schema_is_compared` goes red the moment a generated side exists
   without it. Check the nullability-compared list and its guard in the same pass.
3. Regenerate, then run the contract module and **read the failures as the deliverable**. The first
   comparison of a shape is where its drift surfaces.
4. **Every divergence is a `CLAUDE.md` §0 verdict, one at a time**: which side is wrong, with a
   reason. Do not adjust the walker, and do not make either side match the other to get green. The
   W32-2 precedent ([ledger](PL-00760-w32-2-the-validation-rule-catalogue-execution-ledger.md)) resolved all
   three of its divergences the code's way and moved only the authored contract — that is a
   precedent, not a rule; a divergence where the code is wrong is a code fix.
5. Record each resolution in the authored schema's own `description`, dated, as W32-2 did.

## Task 3 — `validation-report` gains a generated side

Identical in shape to Task 2, for `ValidationReport`
(`packages/model-schema/src/model_schema/validation.py`). A separate commit: its drift is unrelated
to `dataset-version`'s, and the two verdict sets should be reviewable apart.

## Task 4 — counts, ledger, roadmap

1. **Recompute the uncompared-schema counts from the merged tree, never from a plan** — including
   this one. W32-1b restates them as 13 and two; these two generated sides then take it to 11. If
   the merged `.claude/skills/contract-guard/SKILL.md` says anything other than 13 and two, stop and
   reconcile rather than assume.
2. Correct only what this slice made stale, and refresh that skill's `Verified` date per §12.
3. File the ledger beside this plan; record F1, F2 and F3 with a §13 verdict each, and every §0
   verdict from Tasks 2 and 3.
4. **File F2 and F3 as rows in [`../open-questions.md`](../open-questions.md) before the roadmap
   edit**, and give each row two things the closure record needs: **which WK-692 goal it bears on**,
   and that the goal is **dispositioned rather than delivered**. The closure line is written by
   another session, and it should be able to *quote* these rows rather than reconstruct them — a
   paraphrase is where two records drift, and drift between a closure line and the questions it
   rests on is the exact failure this slice exists downstream of. A goal met by a booked-forward
   disposition says so in the closure line itself, never in a footnote reached after the headline
   has been believed.
5. Append the slice record to [`../roadmap.md`](../roadmap.md) in the shape the other WK-692 records use.

## Verification

```bash
uv run pytest packages/model-schema/tests/ -q
uv run pytest backend/tests/test_contracts.py -q
uv run python scripts/generate-contracts.py --check
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

**Prove the new checks bite** — run the negative tests against the unamended models once and watch
them fail. Both halves of the gate are required: Task 1 moves the OpenAPI document, and the
frontend workflow triggers on `docs/contracts/openapi/**` precisely because the client derives
from it.

## Ordering

- **After W32-1b merges, rebased onto it.** Both slices edit `backend/tests/test_contracts.py`.
  W32-1b rewrites the constraint comparator and its test — the regions **bracketing** the carve-out
  this slice deletes. No semantic conflict, but git will flag that hunk: **resolve it by hand and
  re-read the rewritten comparator in full**, rather than diffing around it.
- **Re-confirm M6 against the merged tree before relying on it.** If W32-1b's rewrite changes how a
  one-sided keyword is treated, Task 1's premise moves, and that is a §0 question to raise rather
  than route around. W32-1b's ledger states, positively either way, whether that treatment changed.
- Task 1 is one commit and may not be split (OQ-600). Tasks 2 and 3 are a commit each.

## Task 5 — close WK-692 — *not this slice's, as of 2026-08-24*

**W32-11 is the last slice before closure** (maintainer instruction, 2026-08-24). Once Tasks 1–4
are green, [`../../CLAUDE.md`](../../CLAUDE.md) §13's checklist runs and the result is recorded in
[`../roadmap.md`](../roadmap.md), with the §14 review triggering at the same point.

**Both states, because the first is why the second was settled.** This task was written into
W32-11 on the morning of 2026-08-24, when the closure record had no owner. It was handed to the
session holding the WK-692 docs the same day, and lands as **a second PR after W32-11 merges** — not
inside this slice. The reasoning is that session's and it is the right reasoning: it holds the WK-692
row, the five back-filled slice records and both acceptance tables, and a closure line written in a
different hand from the records it closes over is a seam a later reader has to reconcile. §14 also
requires a maintainer acceptance line with a date, which is that session's to draft and the
maintainer's to sign.

**So this slice ends at Task 4.** What remains below is the condition the closure record is written
against, kept here because it is what Tasks 1–4 must leave true.

**A finding this slice cannot resolve does not hold WK-692 open.** It is booked forward — into a named
later slice, a later workstream, or a spec change for a later phase — with an owner and a §13
verdict. Silence is still not a verdict; an open question with an owner is. What closure requires is
that every unevidenced requirement has a *disposition*, not that every disposition is *done*.

## Where the three findings go

| # | Disposition | Why it does not hold WK-692 open |
|---|---|---|
| F1 | **Delivered.** FR-158 asks for the floor to be enforced where each certificate is constructed; it never asked the generated client to carry it. Recorded as a stated limit — enforcement is server-side — not as a gap | The requirement is satisfied as written. The limit is published, not implied |
| F2 | **Booked forward** as an open question with an owner. It is the `gbm.quantile_crossing` shape — the gap that let a missing keyword sit green for months, which is the argument W32-10 was built on — and it is a guard-design change, not certificate work | Discovered inside this slice, outside every requirement WK-692 owns. Fixing it here would be new capability in a closing slice |
| F3 | **Booked forward.** `metric-certificate` has no authored contract at all, so giving it one is a new contract, not a comparison of an existing pair. Out of the scope written for this slice | Task 1 still enforces its four-check floor model-side, which is what FR-157 asks for. Only the *comparison* is deferred |

**F2 and F3 are filed as owned rows in `../open-questions.md` before the closure record is
written** — a precondition of Task 4, not a follow-up to it. The maintainer's instruction relaxes
*what* closure requires (every unevidenced requirement carries a disposition; not every disposition
is done) but not *where* a disposition lives. **A finding booked forward into prose in a slice
ledger is §13's silence wearing a different hat**: the next planner never meets it. Neither is a
requirement WK-692 owns, and neither is a §0 disagreement — both are reach, not correctness.
