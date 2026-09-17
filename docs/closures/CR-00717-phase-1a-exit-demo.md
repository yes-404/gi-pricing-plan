---
id: CR-717
family: closure
kind: phase
title: Phase 1a — exit demo
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-15
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/closure-records.md
---

# Closure records and historical findings

> Moved from `docs/roadmap.md` by the roadmap slim (RFC-813, accepted 2026-08-27).
> This is the archive: per-workstream closure records, the Phase 1a exit-demo record,
> the independent audit, WK-660's mid-workstream findings, and WK-661's in-progress and slice
> records. The roadmap now points here for the history.

### Phase 1a — exit demo accepted 2026-08-15

**Accepted by the maintainer. What it was accepted on is worth stating exactly**, because
the criterion's own words are "a person driving the screen", and this record first claimed
more than happened.

| | |
|---|---|
| The stack came up in one command | `uv run python scripts/demo.py`, **27 s** to a served page against NFR-529's 300 s |
| The failure loop ran on real data | version 1 fails on 571 rows of genuine exposure above 1.0, promotion refused with `VALIDATION_HAS_FAILURES`, version 2 reaches `validated` after one preparation step |
| The screens were exercised **by Claude, over HTTP**, not by a person in a browser | the entrance, the guide, the dataset list, the version timeline |
| The maintainer **accepted it without driving it**, deferring hands-on testing until more functionality exists | their words: *"I cannot really test anything on the demo platform, I will test more after more functions added"* |

So the exit criterion's mechanical half is met and evidenced; its *human* half is
outstanding by the maintainer's own choice, and the phase closes on that basis rather than
on a claim nobody made. The entrance exists and works, which is what WK-667 owed; the person
driving it comes when there is more to drive.

**Two defects found by exercising it, neither by any test.** That is the argument
FR-408 makes for the entrance, and it holds even though the exercising was done over
HTTP rather than in a browser:

| Found | State |
|---|---|
| The dataset list's **latest version** column was empty for every row — the list called `to_schema(row)` with no version while the detail route passed one. `01` §5.3 names it as one of four columns the list must show, and it is the demo's first screen | **Fixed**, with the injection proof |
| **Nothing in the platform ever sets a version to `failed`.** `DatasetStatus.FAILED` is in the enum and in `VALID_DATASET_TRANSITIONS`, and no code path transitions to it — so a version whose first validation fails rests in `validating`, which every status screen reads as "still running" | **OQ-562**, open, recommendation `failed`; specified as **FR-52**, not implemented |

Neither was visible to an audit. The first was a column nobody asserted; the second is a
*state* rather than a requirement, so no marker could be missing and no coverage number
could drop. A person opening the screen saw both in under a minute.
