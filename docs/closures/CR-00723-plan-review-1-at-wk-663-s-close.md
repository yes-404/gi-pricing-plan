---
id: CR-723
family: closure
kind: review
title: Plan review 1 — at WK-663's close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-15
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 1 — at WK-663's close, 2026-08-15

The first run of `CLAUDE.md` §14, raised as `RFC-711`. §13 asks whether a workstream did
what it said; this asks whether the plan still says the right thing. Five questions, in
order, each with a written answer — **"no change" included**, because a silent question is
indistinguishable from one nobody asked.

**1. Completion — what is actually done, derived from the specs.**

`scope-audit.py` and `req-coverage.py`, not recollection. Phase 1a's workstreams WK-657, WK-658,
WK-659, WK-660, WK-666 and WK-663 are closed with records on this page. `DATA` stands at 48/50
requirements (the two are measured NFRs), **33/33** endpoints and **38/38** catalogue
rules; `PLAT` is unchanged since WK-658 at ~35 of 61 with six endpoints owned by WK-674.

One disagreement with the plan, and it is the finding: the WK-663 row said "app shell,
dataset views, validation report view" — three items — while `01` §5.3 names **seven**
views. The row was written before the spec's view table was read against it. All seven
shipped, so the plan under-described the work rather than the work under-delivering; the
row is left as written and the closure record carries the correction, as WK-658's and WK-660's do.

**2. Omission — what the phase needs that no row names.**

*Browser authentication.* No workstream row mentions it. `07` §3.7 specifies the API side
completely and the client side not at all, and the gap was invisible from either end: the
backend's tests authenticate through dependency overrides, the frontend's stub `fetch`.
A real browser got 401 on everything. Raised as **OQ-644** with a recommendation
(PKCE), fixed for the dev loop only.

*The pattern behind it.* Three of this workstream's six API findings — the version
timeline, the approve route, the reference read routes — were endpoints the spec's §5.1
table never declared. `scope-audit.py --endpoints` compares that table against the
published contract, so **an endpoint missing from both reads as complete coverage**. This
is the same shape as §13's "requirement coverage is not interface coverage", one level up,
and the honest mitigation is the one used here: derive the surface from what §5.3's views
must *do*, not from what §5.1 lists.

*Not an omission:* `pipelines/` remains correctly assigned to WK-665, and Playwright E2E is
deferred to WK-665 for a stated reason rather than forgotten.

**3. Skills and research — re-run, not appended to.**

`docs/skills-map.md`'s frontend rows survive contact with the code: Vue 3, Router, Pinia,
Tailwind, ECharts, openapi-typescript and Vitest are all cited and all still accurate.
`.claude/skills/vue-frontend` gains the development-identity procedure, which is exactly
the kind of non-obvious dev-loop step §12 exists to capture — it cost an entire workstream
before anyone noticed.

Two rows are now *ahead* of the code rather than behind it: TanStack Table and Vue Flow
are declared and not installed, which is right for their phases. One is behind: Pinia is
installed and registered with no store, because nothing has yet needed to outlive a route.
No skill has gone stale. No new external skill is proposed — and none would be installed
without the maintainer's approval in any case.

**4. Document drift.**

`CLAUDE.md` §2's `frontend/` mark and its "add with the code" note on `frontend.yml` were
both stale and are corrected in this PR. `01` §5.1 now carries four dated amendments from
WK-663's findings. `open-questions.md` gains OQ-644. The roadmap's own Phase 1a percentage
("~26 %") is an estimate from before any code existed and is left alone: it is a planning
figure, and re-deriving it per workstream would make it a second progress table
disagreeing with the one above it.

**5. Shape — are the remaining phases still cut in the right place?**

Yes, with one proposal.

*No change* to the 1a/1b split, to WK-661–WK-665, or to any phase boundary. Taking WK-666 (the data
seed) before WK-663 was the right call and the reason WK-663 rendered real data from day one;
nothing suggests a second such reordering is needed.

*Proposal — three items name `WK-664` as their owner and WK-664's row does not cover them.*
NFR-463's tabular chart fallback, browser authentication once OQ-644 is decided, and
the frontend half of governance surfacing all point at WK-664 in closure records, while the
row itself reads "factor workbench, model detail, diagnostics" — modelling views only. An
owner naming a scope that does not include the work is how work becomes nobody's.

> **Correction, 2026-08-15.** As first written this said WK-664 "is not yet a row and should
> be". It is a row, at Phase 1b, and had been since the 1a/1b split; the review missed it.
> The substance survives — the three items still had no owner — but the change is to
> **extend** WK-664, not to create it. Recorded rather than edited away, because a review that
> quietly fixes its own premise leaves nobody able to tell what was believed.

> **Recommendation:** extend `WK-664` to `Frontend: factor workbench, model detail,
> diagnostics — **and the frontend platform**: browser authentication (FR-393),
> accessibility beyond semantics (NFR-463), workspace selection`. It gains a dependency
> on OQ-644 being decided. Spec and plan only; no code follows from a review
> (`CLAUDE.md` §14 rule 3).
>
> **Maintainer accepted 2026-08-15**, together with OQ-644's recommendation (PKCE in the
> SPA for Phases 1–2, now FR-393). Applied to WK-664's row and to the Phase 1b table
> below.

---
