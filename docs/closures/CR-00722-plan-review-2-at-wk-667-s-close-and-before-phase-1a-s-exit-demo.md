---
id: CR-722
family: closure
kind: review
title: Plan review 2 — at WK-667's close and before Phase 1a's exit demo
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-15
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

# Plan reviews

> Moved from `docs/roadmap.md` by the roadmap slim (RFC-813, accepted 2026-08-27).
> Each review is the §14 output at its date; the proposals and acceptance lines are
> the record.

### Plan review 2 — at WK-667's close and before Phase 1a's exit demo, 2026-08-15

`CLAUDE.md` §14's second run. Both triggers fire at the same moment: WK-667 closed, and the
exit demo is the next milestone. Five questions, in order, each answered — **including the
ones whose answer is "no change"**.

This review is short on questions 1 and 4 on purpose. The independent audit that ran hours
earlier is the evidence for both, and repeating its work would be re-deriving from the same
sources rather than testing the plan.

**1. Completion — derived, not recalled.**

| Module | §5.1 endpoints published | Requirements evidenced |
|---|---|---|
| `DATA` | **34 / 34** | 48 / 52 |
| `PLAT` | 18 / 21 | 40 / 65 |
| `GOV` | 11 / 20 | 23 / 43 |
| `OVR` | — | 8 / 25 |

423 requirements specified, 121 marked (28.6 %) — the phase covers `DATA` and the `PLAT`
and `GOV` foundations under it, which is what Phase 1a's rows claim and no more. `DATA`'s
four unevidenced requirements each carry a verdict: NFR-465/466 measured rather than
tested, FR-40 and FR-43 appended this morning and owned by WK-664. `PLAT`'s three
unpublished endpoints are WK-674's environments routes.

**The plan and the derivation now agree** — because the audit made them agree this morning,
not because they always did. Three closure records claimed more than they established and
were rewritten; that reconciliation is recorded above and is not repeated here.

**2. Omission — what the phase needs that no row names.**

*The workflow journeys are evidenced by nothing.* `docs/workflows/WF-698…05` are the
cross-module contracts — a module spec says what one module does, a workflow says what
actually happens — and **no test in the repository cites one**. Phase 1a's exit criterion is
a slice of `WF-698`, covered by `test_data_jobs.py::test_the_failure_loop_then_validated`,
which does not name it. `audit-docs.py` check 14 reports "workflow coverage: DATA 50 %",
which measures whether the workflow *documents mention* a requirement id — not whether the
journey runs. No workstream row owns "the journeys work", and none of the five has been
read against the code since it was written.

This is the same shape as the audit's other findings: a number exists, it is not measuring
the thing its name suggests, and nobody had looked.

> **Recorded as OQ-543** *(2026-08-15)*, with a recommendation: a mechanical audit that
> every journey step cites an endpoint, requirement or artifact that exists — the
> `--endpoints` idea one level up — **now**; one end-to-end journey test per workflow as its
> modules land; and explicitly **not** a marker on an existing test, which would claim a
> journey where one slice is covered. A journey belongs to the workstream that completes
> the last module it touches, so `WF-698` is WK-661's to finish. Phase 1a's exit demo walks its
> data half and is that half's first evidence.
>
> **Accepted 2026-08-15**, unchanged, as **FR-19**. Writing it down sharpened two things:
> the audit's real content is **endpoint and `pricing-core` function** citations, because
> requirement ids and `§` references are already checked; and the ownership rule needs no
> new machinery, since "the workstream that completes the last module" is in every case the
> phase whose exit criterion names that journey (§12).

*Two model/contract divergences have no owner.* `Dataset` carries no status, validated-at or
owner while `01` §5.3 asks the dataset list to display all three; `ColumnProfile` has no
`histogram` while `01` §4.4 **and** `docs/contracts/schemas/profile.schema.json` both define
one. WK-664 cannot build those view items until someone says which side is wrong, and no row
owns the deciding.

*Not omissions:* Playwright E2E is deferred with a stated reason, `pipelines/` is WK-665's, and
the six `PLAT` endpoints remain WK-674's.

**3. Skills and research — re-run, not appended to.**

`docs/skills-map.md`'s pandera row was retired this morning (it read ★★ **Verified** for a
library this repository depends on nowhere). Nothing else in the map is now ahead of or
behind the code. No new external skill is proposed, and none would be installed without the
maintainer's approval.

One gap, from this week rather than from the map: **`close-workstream` does not warn that a
proof can pass for the wrong reason.** §13 rule 4 requires a check be shown to fail on
deliberately broken input. The catalogue check was shown exactly that — and the injection
deleted an id from a *docstring*, so it proved the counter could count while the counter was
counting prose. The skill should say that the injection must break the thing the check
*claims* to measure, not merely something the check happens to read.

`close-workstream` also carries no `Verified` date, alone among the eleven written here.

**4. Document drift.**

Repaired this morning across three commits: the specs now describe what was built, the three
closure records say what the audits establish, and `CLAUDE.md` §2's tree is accurate. What
remains unchecked is `docs/workflows/` — see question 2 — along with `docs/README.md` and
`docs/closures/CR-00709-phase-0-specification-status.md`, neither of which has been read against the repository since Phase
0 closed.

**5. Shape — two proposals.**

*Proposal A — Phase 1a cannot exit as its criterion is written.* §6's exit reads: "a
freMTPL2 dataset version reaches `validated`, including at least one deliberate round
through the failure loop. **The retrofit list (§5) is fully in place by the end of 1a** —
that is the phase's other, quieter deliverable." The first half holds and is now drivable by
hand. The second does not: FR-43, artifact immutability, is on that list and is
enforced by nothing — `frozen=True` is a rule about one process, and an audit rewrote 190
stored reports in a single statement. It is owned by WK-664, in Phase 1b.

> **Recommendation:** land **FR-40 and FR-43 before the exit demo**, keeping the
> criterion as written. They are small — a check at ingestion and four append-only triggers
> with their broken-input proofs — and everything Phase 1b builds sits on artifacts that
> nothing currently protects. The alternative, amending the criterion to exclude
> immutability enforcement, is coherent but should be chosen deliberately and with the risk
> stated, not arrived at by the demo happening first.
>
> **Maintainer accepted 2026-08-15.** FR-40 and FR-43 are a **gate on Phase 1a's
> exit demo**: the criterion stands as written, and the demo does not run until artifact
> immutability is enforced in the database rather than asserted in Python.
>
> The bookkeeping is stated rather than tidied away: **WK-664's row still names both
> requirements**, and WK-664 is a Phase 1b row. The work therefore lands in Phase 1a while its
> nominal owner sits in 1b. That is the maintainer's decision, taken twice; recording it
> this way keeps the record honest about where the work happened, which matters more than
> which row it hangs from.

*Proposal B — WK-664 is now three workstreams in one row.* It carries `02` §5.3's factor
workbench, model detail and diagnostics — a full frontend workstream on its own — plus
browser authentication (FR-393), accessibility beyond semantics (NFR-463), workspace
selection, the audit's six missing `01` §5.3 Contents items, threshold editing, and the two
enforcement gaps. **The last two are not frontend work at all**, and a row whose scope spans
a Vue view, an OIDC flow and a database trigger is a row nothing can be said to have closed.

> **Recommendation:** split the non-frontend half out under its own id when Phase 1b is
> planned, leaving WK-664 the views and the browser. No id is proposed here — naming one is
> the maintainer's, and the last two attempts at it cost two corrections.
>
> **Maintainer accepted 2026-08-15.** The non-frontend half splits out when Phase 1b is
> planned; WK-664 keeps the views and the browser. The id is assigned at that point, not here.

*No change* to the phase boundaries, to WK-661, to WK-665's remaining modelling half, or to Phases
2–4. Nothing this review found argues for re-cutting them.
