---
id: FD-1209
family: finding
title: The freMTPL2 demo has no real rating algorithm, and Slice 3's demo fixture does not satisfy G2
status: active
created: 2026-09-28
owner: auditor
tree: 5ec47dc46ac2f174c5d427f5558a6cb365ff8166
corrected_by: []
relates: [WK-672, PL-1205, WF-699]
---

# FD-1209 — The freMTPL2 demo has no real rating algorithm, and Slice 3's demo fixture does not satisfy G2

**Severity: medium.** The auditor filed this finding on 2026-09-28, on the lead's instruction and
the deputy's DP-S3-8 ruling (his entry of 21:23:15 BST in the lead's local channel file
`to-lead.md`, decision (b): *"The real freMTPL2 algorithm for G2 goes as an FD now"*). It is not
a defect in shipped behaviour. It is a gap that stops a phase exit criterion from being met, so
the severity rests on that criterion, not on any live failure.

## Finding

The freMTPL2 demo's rating version has no rating algorithm. WK-672 Slice 3, on branch
`p2-d-s3` (unmerged, no PR at filing), makes submission require a passing Regression Run and a
golden quote (`PL-1205`, the deputy's DP-S3-1). So the seed has to produce both. The deputy's
DP-S3-8 ruling has Slice 3's seed author a **labelled demo-fixture algorithm**, with a bundle,
suite and golden quote produced by executing the real path, so that the seed passes the new
gate. **That fixture does not satisfy G2.**

**G2** is the exit demo that plan review 15 proposes, in its closure record on #863 (branch
`p2-review-15`): *"The exit demo is `WF-699` end to end on the freMTPL2 seed, with its deploy
step."* `WF-699` (`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`) has
the actuary build rate tables (Phase A), design the rating algorithm (Phase B, steps B1–B5) and
compile and pin (Phase C). A labelled fixture is not the algorithm those phases produce from the
approved freMTPL2 models.

## Evidence

At `origin/main` `5ec47dc4`:

- `examples/fremtpl2/model.py:303`, `create_approved_rating_version`, is the demo's only
  rating-version step. It calls `rating_versions_service.create_rating_version` with
  `slug="fremtpl2-demo"`, a `dataset_version_id` and a `model_ref`. Its docstring reads *"The
  rating version pins the approved GLM as `model:{slug}@{version}`"*.
- `backend/src/app/platform/rating_versions.py:201`, `create_rating_version`, takes exactly
  `session`, `workspace_id`, `actor`, `slug`, `dataset_version_id` and `model_ref`. It has no
  algorithm and no rate-table parameter.
- So the demo's approved rating version pins a model and nothing else. `WF-699`'s Phase B
  (algorithm) and Phase C (compile with every pin) do not appear in the seed.
- The deputy's DP-S3-8 conditions on the fixture, read in full: the evidence is produced by
  execution and never inserted; the fixture is labelled "demo fixture" in the algorithm, suite
  and golden quote; the demo tests stay green in Slice 3's gate.

Not verified by the auditor: the content of Slice 3's seed change, which is not merged. This
record relies on the deputy's ruling for what it will contain.

## Disposition

**Deferred with an owner — the lead**, as G2's exit-demo item. **Due before plan review 16**, not
under WK-674, by the deputy's ruling. The algorithm comes from the approved freMTPL2 models, and
deployment is only its last step. The event is the real algorithm existing in the seed and
`WF-699` running end to end on it.

## Status at the WK-672 Work close, 2026-09-29

Recorded by the auditor at the WK-672 Work close (`CR-1243`). Read at `origin/main` `1c8762d9ed235f80e0f2fff80c44003694828e97`. **The finding stays `active`.**

- **Slice 3's seed change is now merged** (#886, squash `6a8b8e70`), so the line above that it was "not verified by the auditor" is answered: `examples/fremtpl2/model.py:327` `_demo_algorithm` is *"`payable = premium_in * 2`. **Not priced from the GLM** (DP-S3-8) … the real algorithm around the approved freMTPL2 models is G2's"*; the label `DEMO_FIXTURE = "demo-fixture"` is at `:316`, and the suite's change note reads *"demo fixture: not priced from the GLM"* (`:434`).
- **The event has not happened.** No real freMTPL2 algorithm is in the seed (the only algorithm the seed creates is `_demo_algorithm()`, `:386-387`), and no test drives `WF-699` end to end: `git ls-files | grep -iE 'wf.?699|test_wf'` prints only `backend/tests/test_wf01_journey.py`, whose docstring opens *"WF-698 — dataset to approved Model"*.
- **"Plan review 16" now names two reviews.** The row's event is *"due before plan review 16, not WK-674"*. When it was written, the only review 16 on record was plan review 15's G6 (`CR-1212` Proposal 1): *"A plan review 16 is filed after G1–G5 and before the demo"*, and G1 needs every P2 Work resolved. The maintainer's structure entry of 2026-09-29 15:26:00 BST (`to-lead.md`, local) calls the `CLAUDE.md` §14 review at **this** Work close "plan review 16". Read literally, the event is now due before a review that follows this close directly, and it cannot be met there: the real algorithm is `WF-699` Phases A to C on the approved models, which no WK-672 slice planned. The `decision:` is the lead's; the auditor's proposal is in the WK-672 close record.
