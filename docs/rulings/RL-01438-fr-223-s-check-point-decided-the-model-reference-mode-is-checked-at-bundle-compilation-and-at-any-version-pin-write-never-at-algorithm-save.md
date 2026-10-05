---
id: RL-1438
family: ruling
title: FR-223's check point decided — the model reference mode is checked at bundle compilation and at any route that writes a version's pins, never at algorithm save; the spec's "save time" was wrong, and so was the code's error code
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # original date 2026-10-01, set at the draft; minted 2026-10-05
owner: decision-maker
tree: 8bd782acbbdde8e3b4195b5a0acb89183b5a0253
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FR-222, FR-223, FR-227, FR-237, FR-239, FR-240, FR-403, PL-1286]
---

# RL-1438 — FR-223's check point decided: the model reference mode is checked at bundle compilation and at any route that writes a version's pins, never at algorithm save

## How this was ruled

**Ruled 2026-10-01 10:25 BST at effort `medium`** by the decision-maker session `dm-675dp56`.
The command line is `claude --effort medium --model opus --name dm-675dp56`, and the session
printed `CLAUDE_EFFORT=medium`. The lead relayed the commission. Every stamp in this record is
from `TZ=Europe/London date`. *(2026-10-01 10:27 BST: the clock remark is withdrawn; the lead's
earlier stamps were estimates; one box clock.)* The maintainer's words, as the
lead relayed them: "a DM rules FR-223's check point (compile + the RL 9767 validate route vs
'save'), verbatim text, recording which side was wrong". This session did not read the
channel entry itself.

**Working id 9758**, allocated by the lead. It is minted at its merge turn, and every
`RL-<this>` below is then its minted id.

**It discharges limb (1) of FD-1437 (LOW; filed by auditor-1055):** where the
check runs, and which code each site returns. Limbs (2) and (3) are obligations, not ruled
here (see *What it obliges*).

**Evidence tree:** origin/main `1dd5e264` (tree `8bd782ac`).

## Evidence at `1dd5e264`

- **FR-223, read to the clause** (`docs/specs/03-rating-engine.md:109`). It has no dated
  amendment. The clause in question is: every `model_call` step's `mode` "must equal it,
  checked at save time beside FR-227's type check, and a version whose steps disagree with
  it is refused with `MODEL_REFERENCE_MODE_INCONSISTENT`". "It" is
  `RatingVersion.model_reference_mode`.
- **The check function exists.** `check_model_reference_mode(version, algorithm)`
  (`packages/model-schema/src/model_schema/rating.py:172-183`) raises a bare `ValueError` on
  the first mismatching `model_call` step. The message begins `model_call step …`.
- **It runs at one site, compilation.** `compile_bundle` calls it after `validate_algorithm`
  (`packages/pricing-core/src/pricing_core/rating/compile.py:614`).
- **What compilation answers today.** `compile_rating_version`
  (`backend/src/app/platform/rating_versions.py:395`) catches the `ValueError`
  (`:530-536`). The message does not begin with an upper-case code, so the code falls back
  to **`BUNDLE_COMPILE_FAILED`**, as a `PlatformError` with 422. The compile runs in the
  `rating.compile` Job (`backend/src/app/worker/rating_handlers.py:61`;
  `JobKind.RATING_COMPILE`, `model_schema/jobs.py:53`). A `PlatformError` raised in a Job
  fails the Job with that error's code (`backend/src/app/worker/tasks.py:197`).
- **The specified code is emitted nowhere.** `MODEL_REFERENCE_MODE_INCONSISTENT` appears in
  no file under `backend/src` or `packages/*/src`. It is not in `03` §5.1's owned-code list
  (`03:816` has `BUNDLE_COMPILE_FAILED` and no such code), and it is not in the backend's
  rating code registry (`backend/src/app/errors.py:300-315`).
- **"Save time" has no reachable site.**
  - An algorithm is saved without a version (`POST /rating-algorithms`,
    `backend/src/app/api/rating_algorithms.py:28`). Its `model_call` steps carry `mode`
    (`rating.py:302`), but there is no version `model_reference_mode` to compare them with.
  - No route writes a Rating Version's `algorithm_ref`, `pins` or `model_reference_mode`.
    `create_rating_version` (`rating_versions.py:202-209`) takes `slug`,
    `dataset_version_id` and `model_ref` only. A grep for assignments to those fields in
    `backend/src` finds only `to_schema`'s read (`:110-115`).
  - So the version and its algorithm first meet at compilation.
- **Compilation gates use.** Scoring needs a compiled bundle (FR-239). `/score/compare`
  answers 409 `BUNDLE_COMPILE_FAILED` for a version that is not compiled (`03` §5.1). So no
  version is scored, submitted with golden quotes or deployed with a mismatch that
  compilation would refuse.

## Options

| | Option | Assessment |
|---|---|---|
| (a) | Check at **compilation**, always, and at **any route that writes a version's `algorithm_ref` or `model_reference_mode`**, once one exists. Both answer `MODEL_REFERENCE_MODE_INCONSISTENT`. The spec is amended from "save time" | It runs where the two facts meet, and compilation is a point every usable version passes. It needs only the code fixed. The second site has no route today, so it binds the slice that adds one. |
| (b) | Keep "save time": check at algorithm save | Unreachable. The algorithm has no version to compare with, and one algorithm version may be pinned by versions of either mode. Making the algorithm carry the mode contradicts FR-223's "the mode belongs to the Rating Version". |
| (c) | Also check in RL 9767 (working id)'s validate route, with an optional `rating_version_ref` | Earlier feedback, but it changes a record whose ruled options were just audited unchanged. The designer shows the version's mode read-only (`PL-1286` S2), and the authoritative check is compilation either way. Refused for now; a later DP may raise it. |
| (d) | At algorithm save, refuse `model_call` steps that disagree with each other, a necessary condition of FR-223 | It is checkable at save, but it is a second rule point for one requirement, and it never catches the real case: every step agrees, but with the wrong mode for the version. Refused. |

## Ruled

**(a).**

1. **Bundle compilation is the check point, always** (FR-240). A mismatch fails the
   `rating.compile` Job with **`MODEL_REFERENCE_MODE_INCONSISTENT`** (422 semantics, carried
   as the Job's error code under FR-403), never with `BUNDLE_COMPILE_FAILED`. The message
   names the first mismatching `model_call` step's `step_id`, the step's mode and the
   version's mode, as today's message does.
2. **Any route that writes a Rating Version's `algorithm_ref` or `model_reference_mode`**
   refuses a mismatching write with **422 `MODEL_REFERENCE_MODE_INCONSISTENT`**, through
   the same function. No such route exists at this tree, so this binds the slice that adds
   one.
3. **Algorithm save (`POST /api/v1/rating-algorithms`) and RL 9767 (working id)'s validate
   route do not check FR-223.** RL 9767's item 7 stands.
4. **Which side was wrong.** The **spec** was wrong about the check point: "checked at save
   time" names a point where the version is not available. The **code** was right about the
   check point but wrong about the outcome: it answers `BUNDLE_COMPILE_FAILED` where the
   spec names `MODEL_REFERENCE_MODE_INCONSISTENT`. The spec was also incomplete: that code
   is missing from `03` §5.1's owned-code list. *(Amended 2026-10-01 10:30 BST, F2: a clause
   naming audit-docs check 10 is struck. That check finds a code claimed by more than one
   module and cannot see a missing one, so no mechanical check covers this gap.)*

**Why.** The check compares two artifacts, and compilation is the first point where both are
present. It is also a point every scored, submitted or deployed version must pass. A
"save-time" check that cannot see the version checks nothing. The named code is kept,
because FR-403 makes the code the contract and the spec already promised it.

**Routes this ruling touches.** None is created. The `rating.compile` Job's failure code
changes for this case only. No request or response shape changes, so the ACK rule has
nothing to type here. The future pin-writing route of item 2 carries its own typed request
and 2xx response under that rule.

## Spec changes this ruling requires

These are applied by **the slice that builds limb (2)** under `.claude/skills/spec-change`,
in the same commit as the code that emits the code (`CLAUDE.md` §2). They are not applied in
this commit. Placement was read at origin/main `1dd5e264`, and re-read at main `ef5dc6e7` on
2026-10-05: each find string below is found there exactly once. Placeholders: `RL-<this>` is this
record's minted id, and `<date>` is the date of the applying commit. Nothing else in a text
is a placeholder.

**T1 — `03` FR-223, a dated amendment.** Placement: `docs/specs/03-rating-engine.md`, the
FR-223 row (`:109`). The text is **appended** to the end of the second cell, after
`(`02` OQ-575, decided 2026-08-17.)` and one space, before the closing ` |`. Nothing is
struck.

```text
**Amended <date> (`RL-<this>`): the check runs where the version and its algorithm meet, not at save time.** "Checked at save time" named a point where the Rating Version is not available: an algorithm is saved without one, and one algorithm version may be pinned by versions of either mode. The check runs at bundle compilation (FR-240), always, where a mismatch fails the `rating.compile` Job with `MODEL_REFERENCE_MODE_INCONSISTENT`, naming the first mismatching `model_call` step and both modes; and at any route that writes a Rating Version's `algorithm_ref` or `model_reference_mode`, which refuses a mismatching write with **422** `MODEL_REFERENCE_MODE_INCONSISTENT`. Algorithm save and `POST /api/v1/rating-algorithms/validate` do not check it. The spec was wrong about the check point; the code, which checked at compilation but answered `BUNDLE_COMPILE_FAILED`, was wrong about the code. |
```

The text ends with ` |`, which replaces the cell's existing closing ` |`. So the find
string is `(`02` OQ-575, decided 2026-08-17.) |`, and it is replaced with
`(`02` OQ-575, decided 2026-08-17.) ` followed by the block above.

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop. If a find string is not found exactly once, that is a stop too, reported to the lead; the executor does not re-word it.

## What it obliges

- **This commit:** this record only. No spec is edited.
- **FD-1437, limb (2): the typed error, red first.** Build owned by S3, as the
  lead relayed it.
  - `check_model_reference_mode`'s mismatch reaches compilation's caller as
    `MODEL_REFERENCE_MODE_INCONSISTENT`, not as a bare `ValueError` that falls back to
    `BUNDLE_COMPILE_FAILED`.
  - The code is added to `backend/src/app/errors.py`'s rating registry.
  - T1 lands in the same commit.
  - Red first: a compile test with an `approximation` version pinning an `exact`
    `model_call` asserts the Job's error code. On main it reads `BUNDLE_COMPILE_FAILED`.
  - How the error is typed is the build's to design. This record does not rule its code.
  - *(Added 2026-10-01 10:30 BST, auditor-1061 F1.)* FD-1437 limb (2)'s
    validate-route clause falls away by item 3. The validate route has no Rating Version,
    and so no `model_reference_mode`; RL 9767 (working id) item 7 agrees. Limb (2) is
    discharged by the compile-site typed error alone. The maintainer accepted this on
    2026-10-01 at 10:30:00 BST, in the `to-lead.md` entry headed "2026-10-01 10:30:00 BST —
    ACCEPTANCE: RL 9770 (NFR-490's statistic = p99) as the spec interpretation; FD 9759
    limb (2) discharged at the compile site alone; #1060 audit noted", as the lead relayed
    it. That supersedes the maintainer's earlier "at compile AND in the validate route".
- **FD-1437, limb (3): the bare-`ValueError` sweep.** Build owned by S3. The
  build finds the other bare `ValueError`s that reach `compile_rating_version`'s fallback
  (`rating_versions.py:530-536`), and either names them or records why
  `BUNDLE_COMPILE_FAILED` is right for each. Not ruled here.
- **Item 2's future route:** the slice that adds a write of `algorithm_ref` or
  `model_reference_mode` carries the 422 check and its negative test.
- **`PL-1286` is not edited.** Placing limbs (2) and (3) in a slice is the planner's and the
  lead's.

## Acceptance — the violation that must become detectable

The violation: **a version whose `model_call` modes disagree with its declared mode,
refused under the wrong code or not refused at all.**

1. **Compile, named.** An `approximation` version pinning an algorithm with an `exact`
   `model_call` step fails the `rating.compile` Job with
   `MODEL_REFERENCE_MODE_INCONSISTENT`, and the message names the step. Red on main:
   `BUNDLE_COMPILE_FAILED`. *(Amended 2026-10-01 10:30 BST, F3.)* No route writes
   `model_reference_mode`, so the test sets it on the row or the schema directly. At the
   pure level it can extend pricing-core's existing fixture,
   `packages/pricing-core/tests/test_rating_compile_bundle.py:234`
   (`test_a_mode_mismatch_is_refused_at_compile`). That test asserts only a `ValueError`
   matching `FR-223`, and it is tightened to the named code.
2. **Compile, agreeing.** The same version with a matching step compiles.
3. **Spec and code agree.** `MODEL_REFERENCE_MODE_INCONSISTENT` is in `03` §5.1's
   owned-code list and in `RATING_ERROR_CODES` (`backend/src/app/errors.py:297`).
   *(Amended 2026-10-01 10:30 BST, F2.)* No mechanical check covers this: audit-docs check
   10 (`scripts/audit-docs.py:15`) finds a code claimed by more than one module and cannot
   see a missing one. So the slice adds a test, red first, that asserts the code is in both.
   It reads the §5.1 owned list from `docs/specs/03-rating-engine.md` and imports
   `RATING_ERROR_CODES`.
4. **No save-time check.** Saving the mismatching algorithm through
   `POST /rating-algorithms` succeeds (201). It carries no version, and that is now the
   spec's statement, not a gap.

## Amendment, 2026-10-01 10:30 BST: auditor-1061's F2 and F3

*By the decision-maker session `dm-675dp56` (effort `medium`), on auditor-1061's audit of
`f70593b5`, as the lead adopted it at 10:29 BST. The ruling is unchanged.*

- **F1** *(folded in at 10:30 BST, on the maintainer's answer of 10:30:00 BST, relayed by the
  lead).* FD-1437 limb (2) is discharged at the compile site alone. The
  validate-route clause falls away by item 3. The new bullet is in *What it obliges*.

- **F2.** Item 4 and Acceptance 3 cited audit-docs check 10, which cannot see a missing
  owned code. The clause in item 4 is struck. Acceptance 3 now requires a test that
  `MODEL_REFERENCE_MODE_INCONSISTENT` is in both `03` §5.1's owned list and
  `RATING_ERROR_CODES`.
- **F3.** Acceptance 1 now says how the red test is built when no route writes the mode:
  it sets the mode on the row or the schema directly, or tightens pricing-core's
  `test_rating_compile_bundle.py:234`.

## Amendment, 2026-10-05: citations re-read at main `ef5dc6e7`, before mint

Citation and currency update only. Nothing ruled above changes (decision-maker `dm-amend-2`,
on the lead's brief of 2026-10-05 10:50 BST, which adopted the batch-2 triage).

- **T2 is re-anchored by the paragraph, not the line.** The owned-code list moved
  `03:816` → `:934`, inside the §5.1 paragraph that begins
  `**Error codes owned by this module:**` (`:928`). T2's find string occurs there exactly
  once. **T1's** FR-223 row is still `:109`, and its find string
  `(`02` OQ-575, decided 2026-08-17.) |` occurs exactly once.
- **Currency.** At `ef5dc6e7`, `MODEL_REFERENCE_MODE_INCONSISTENT` is still emitted nowhere
  in `backend/src` or `packages`, and it is not in `RATING_ERROR_CODES` (`git grep`, no
  hits). The Evidence's code-path premise holds.
- **Flagged, not changed: the owned-list half of the Evidence is false at its own tree.**
  The Evidence says the code "is not in `03` §5.1's owned-code list (`03:816` has
  `BUNDLE_COMPILE_FAILED` and no such code)". At `1dd5e264` the same paragraph's `:818`
  ends `` `MODEL_REFERENCE_MODE_INCONSISTENT`, `` (listed since #95, `a72cc1b2`), and
  at `ef5dc6e7` it is `:936`. T2 as written would add a second occurrence to that list.
  Changing T2 changes what this record rules, so it is not done in this citation pass. It
  is raised to the lead for a decision before the mint.
- **The Evidence section is a dated reading at `1dd5e264`** and resolves there. It is not
  rewritten. At `ef5dc6e7` its moved cites are: `03:816` → `:934` (above);
  `check_model_reference_mode` `model_schema/rating.py:172-183` → `:173-184`, its `mode`
  field `:302` → `:303`; `create_rating_version` `rating_versions.py:202-209` → `:230-237`,
  `compile_rating_version` `:395` → `:423`, its `except ValueError` `:530-536` →
  `:559-565`; the rating code registry `errors.py:300-315` → `:300-320`. FR-223 `03:109`,
  `to_schema`'s read `rating_versions.py:110-115`, `compile.py:614`,
  `rating_handlers.py:61`, `jobs.py:53`, `tasks.py:197`, `errors.py:297`,
  `api/rating_algorithms.py:28` and `test_rating_compile_bundle.py:234` are unchanged.
- **`status:` is `active`, not `draft`.** `document-ids.md` §1.2a gives a ruling the subset
  `active`, `superseded`, `retired`, and `audit-docs.py` check 33 refused `draft`. The
  working-id rulings of batch 1 (#977, #979) carry `active` in the same form.
- `tree:` stays `8bd782ac`, the tree of `1dd5e264` that the Evidence was read at, as
  `RL-1407` keeps its own evidence tree. `created:` changes at the mint. RL 9767 and RL 9770
  are still working ids (#1055, #1060) and are cited as such; FD-1437 is minted as FD-1437 in the same PR.

## Pre-mint correction, 2026-10-05 (the maintainer, by delegation)

*Recorded by the decision-maker session `dm-premint-3` (effort `medium`), on the lead's brief
of 2026-10-05 12:16:21 BST. This section rules nothing: it records the maintainer's ruling, by
delegation, from `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
"2026-10-05 11:02:39 BST — RL 9758 (#1061, unminted): DROP T2 with a dated pre-mint note; no
re-ruling (the maintainer, by delegation)". Its given text, with the elided premise filled
from this record's Evidence, verbatim:*

T2 withdrawn. Its premise, that `MODEL_REFERENCE_MODE_INCONSISTENT` "is not in `03` §5.1's
owned-code list", was false at this record's tree; the code has been in 03 §5.1's owned list
(:936) since a72cc1b2. No other text depends on T2.

Item 4's sentence 'The spec was also incomplete: that code is missing from `03` §5.1's owned-code list.' rests on the same false premise and is withdrawn with T2: the code has been in that list since #95 (`a72cc1b2`). Item 4 otherwise stands: the spec was wrong only about the check point, and the code only about the outcome.

- **Applied.** T2's placement and its two text blocks are removed from *Spec changes this ruling requires*, and *What
  it obliges* reads "T1 lands in the same commit." T1 and the rest of the record stand.
- **Verified at origin/main `072c56e1ba386a790160ac4d90ad667f611df67c`.** In
  `docs/specs/03-rating-engine.md`, the paragraph that begins
  `**Error codes owned by this module:**` is `:928`, and `:936` ends
  `` `MODEL_REFERENCE_MODE_INCONSISTENT`, ``. At this record's tree `8bd782ac` (commit
  `1dd5e264`) the same entry is `:818`. `git log origin/main -S'MODEL_REFERENCE_MODE_INCONSISTENT'
  -- docs/specs/03-rating-engine.md` names one commit, `a72cc1b2` (2026-08-17, #95).
