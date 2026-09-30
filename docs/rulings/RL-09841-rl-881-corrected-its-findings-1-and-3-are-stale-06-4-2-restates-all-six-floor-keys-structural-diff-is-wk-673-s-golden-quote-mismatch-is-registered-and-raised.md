---
id: RL-9841
family: ruling
title: RL-881 corrected — its findings 1 and 3 are stale; 06 §4.2 restates all six floor keys, structural_diff is WK-673's, GOLDEN_QUOTE_MISMATCH is registered and raised
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 0bc69b5b2c3c16ec8391387cdfab19734ff85d2b
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-881
relates: [RL-881, RL-885, RL-1184, RL-1263, RL-1264, PL-1267]
---

# RL-9841 — RL-881 corrected: its findings 1 and 3 are stale

## How this was ruled

**Ruled at effort `medium`**, under the maintainer's decision by delegation of 2026-09-30
08:00:36 BST (`to-lead.md`, entry headed "08:00 CHECKPOINT DECISION: an interim
medium-effort pass for #937 and #946 ONLY; the rest wait for effort high"). That entry
reads: "The DM rules #946 (the RL-881 correction) now, at medium effort. It records facts
and decides nothing new. Choose (b) or (c); my steer is (c)". The decision-maker's role line
sets effort `high` for a ruling on the maintainer's raise; this pass is the maintainer's
stated exception, and is recorded as such. The record was prepared earlier at medium effort
(PR #946, head `efa232bf`, "PREPARED, NOT RULED"); this pass re-verified each fact and rules
it.

**Working id 9841.** The id is minted at the merge turn, which the lead schedules.

## Verified first, at 0bc69b5b2c3c16ec8391387cdfab19734ff85d2b

RL-881 is
`docs/rulings/RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md`.
Its *Findings reported, not ruled* section (`:144` onward) holds three statements no longer
true at this tree. Each was read at `0bc69b5b` with `git show 0bc69b5b:<path>`.

1. **Finding 1, `:155-158`** — *"`06` §4.2's restatement (`:290-295`) names the floor for
   `model`, `validation_rule`, `custom_objective` and `peril_structure`, and omits
   `rating_version`, `custom_metric` and `deployment` — three of the six keys
   `EVIDENCE_FLOOR` actually holds."*
   **Now false.** `docs/specs/06-governance.md:344-352` restates all six keys:
   `validation_rule` — `dry_run_result`; `custom_objective` — `objective_certificate`;
   `custom_metric` — `metric_certificate`; `model` — `diagnostics` and
   `transparency_artifact_if_non_glm`; `rating_version` — `structural_diff`,
   `regression_run` and `dislocation_run`; `deployment` — `rating_version_approval` and
   `uat_deployment`. These equal `EVIDENCE_FLOOR`
   (`packages/model-schema/src/model_schema/approvals.py:101-108`) key for key. The fix is
   dated in place (`06-governance.md:355-358`, "Corrected 2026-08-29, WK-671 Slice 2 …
   Ruled in … RL-885") and landed at `2891d426` (2026-08-29T18:12:09+01:00, #398), after
   RL-881 was written.
2. **Finding 1, `:153`** — *"`structural_diff` has no owner named anywhere."*
   **Now false.** `RL-1184` E4 (its `:114`): "**E4 — `structural_diff`'s owner is
   WK-673.**" `06` FR-364 (`06-governance.md:145`) carries it: "**Amended 2026-09-28
   (`RL-1184` E4): `structural_diff` has an owner, WK-673.** At submission, WK-673 persists
   `03` FR-219's structural diff as a content-addressed blob and registers a verifier for the
   `structural_diff` kind."
3. **Finding 3, `:168-172`** — *"`GOLDEN_QUOTE_MISMATCH` … is registered nowhere in code. It
   is absent from `RATING_ERROR_CODES` … so `PlatformError("GOLDEN_QUOTE_MISMATCH", ...)`
   would raise `ValueError: unknown error code`."*
   **Now false.** It is registered inside `RATING_ERROR_CODES` (the frozenset opening at
   `backend/src/app/errors.py:286`; the entry at `:353`), and raised by `_golden_quote_gate`
   (`backend/src/app/platform/rating_versions.py:551`; the raise at `:596-597`) and by the
   `rating.regression` handler (`backend/src/app/worker/rating_handlers.py:209`). First
   registered at `50e5271c` (2026-09-28T15:01:34+01:00, WK-672 Slice 1, #853); first raised
   at `109cd065` (2026-09-28T19:49:22+01:00, WK-672 Slice 2, #867) — both by
   `git log --reverse -S'"GOLDEN_QUOTE_MISMATCH",' 0bc69b5b -- backend/src/app/errors.py backend/src/app/platform/rating_versions.py`.
   The finding's other clause — that `03` §5.1 owns the code — is not corrected.

**Checked and still true — not corrected.**
- **RL-881's disposition, including "Lands with the last enabler | WK-673" (`:35`).**
  `regression_run` is verified by `_regression_run_gate` (`rating_versions.py:619`, called
  at `:289`), since WK-672 Slice 3 (`6a8b8e70`, 2026-09-29T12:26:52+01:00, #886). The two
  kinds still unverified, `structural_diff` and `dislocation_run`, are both WK-673's, so
  WK-673 is still the last enabler.
- **Finding 2** (`DEFAULT_POLICY` has no `deployment` entry) is WK-674's and is not touched
  here; the prepared ruling on OQ-1234 (working id 9901, #935) bears on it.
- **`RL-1263` and `delivery-process.md` §8** do not bear on RL-881: RL-881 assigns the
  wiring by artifact ownership, not Work order (prepared record's check; not re-run in this
  pass, since nothing in RL-881 or `delivery-process.md` has changed on this branch).

## Ruled

**Option (c): RL-881 is corrected in all three stale statements — finding 1's two and
finding 3's.** Read RL-881's findings as follows from this record's merge:

- Finding 1's `06` §4.2 sentence: **§4.2 restates all six `EVIDENCE_FLOOR` keys**
  (`06-governance.md:344-352`), corrected 2026-08-29 under RL-885. FR-364 mechanism (i) is
  met for the floor's restatement.
- Finding 1's `structural_diff` sentence: **its owner is WK-673** (`RL-1184` E4; `06` FR-364,
  amended 2026-09-28).
- Finding 3: **`GOLDEN_QUOTE_MISMATCH` is registered in `RATING_ERROR_CODES` and raised**
  (sites above). The gap it describes is closed.

**Why (c), not (b).** Each statement is a fact, verified here at one tree. Leaving finding 3
uncorrected would leave RL-881 carrying a statement known false today, and a later reader
would have to rediscover it. (d), supersession, stays wrong: RL-881's disposition and its
refusal reasons still stand; `corrects:` is the form for a false statement in a frozen
record (`document-ids.md` §1.5).

**Nothing else is decided.** RL-881's body stays as filed. No spec, plan or code change
follows.

## What it obliges

- **This commit:** RL-881's header gains `corrected_by: [RL-9841]`, the one header edit
  §1.5 permits on a frozen record. Nothing else in RL-881 changes.
- **Nobody else.** No slice, spec or roadmap edit follows.

## Acceptance — the violation that must become detectable

RL-881's `corrected_by:` names this record and this record's `corrects:` names RL-881.
`scripts/audit-docs.py` check 34 cross-checks the pair, so removing either side fails the
audit. A reader of RL-881's findings reaches this correction through RL-881's header.
