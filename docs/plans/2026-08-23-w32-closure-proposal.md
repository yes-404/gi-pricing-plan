# W32 — what closure needs, and why it cannot happen yet

**Written 2026-08-23.** A proposal under [`../../CLAUDE.md`](../../CLAUDE.md) §14: recommendation
and rationale, with an acceptance line the maintainer signs. **Nothing here is applied.**
[`../roadmap.md`](../roadmap.md) is not edited by this document, and neither is
[`2026-08-22-w6b-slice-map.md`](2026-08-22-w6b-slice-map.md) — a filed plan is frozen at its date.

## The verdict

**W32 cannot be closed.** Two independent reasons, and the second is the one that would otherwise
be missed:

1. **Unbuilt scope.** Four requirement groups W32 owns have no implementation, and three pieces of
   shipped W32 behaviour have no test that could fail if the behaviour were wrong.
2. **The workstream does not exist in the roadmap.** There is no `W32` row in Phase 1b's
   workstream table (`../roadmap.md:3773-3777` lists W5, W6b and W7 only). Closing a workstream
   the plan does not contain would record progress against nothing —
   [`CLAUDE.md`](../../CLAUDE.md) §13's failure mode exactly.

## Part A — the work, and the five plans that close it

Five plans are filed alongside this one, one per subsystem, each independently testable. They were
cut this way because the open items span four unrelated subsystems plus a test-hardening set;
a single plan would have coupled a database migration to a frontend-visible contract change to a
test-only fix.

| Proposed slice | Plan | Closes |
|---|---|---|
| **W32-7** | [workspace identity and selection](2026-08-23-w32-7-workspace-identity-and-selection.md) | FR-PLAT-62, FR-PLAT-63, FR-PLAT-65 |
| **W32-8** | [artifact library list routes](2026-08-23-w32-8-artifact-library-list-routes.md) | FR-MODEL-127 |
| **W32-9** | [transparency exposure share](2026-08-23-w32-9-transparency-exposure-share.md) | FR-MODEL-36, FR-MODEL-79 |
| **W32-1b** | [drift guard arm attribution](2026-08-23-w32-1b-drift-guard-arm-attribution.md) | the constraint guard's arm blindness, and the `contract-guard` skill's stale counts |
| **W32-10** | [untested behaviour](2026-08-23-w32-10-untested-behaviour.md) | FR-DATA-51, FR-MODEL-124, FR-MODEL-125 — evidence, not new behaviour |

**`W32-1b` rather than `W32-11`** because §3 of the slice map already uses that name for this
work: *"belong to `W32-1`'s successor, not to `W32-1` itself"*
([slice map](2026-08-22-w6b-slice-map.md):174-175), and the `contract-guard` skill uses it too.
Renaming it now would break both references to save nothing.

**W32-10 is the one that is easy to skip and should not be.** It adds no capability. What it adds
is the ability for three shipped behaviours to fail:

- The `82edffbe1dce` owner backfill has **no test**, and no test anywhere in this repository
  exercises a migration. Its `LIKE 'dataset:' || slug || '@%'` would silently resolve `motor` to
  `motor-ad`'s creator if the `@` were ever dropped.
- The EBM predict route is asserted over HTTP only by *the route is published* and *no permission
  is refused*. Neither would notice it scoring an EBM as a GLM.
- The partial-dependence share assertion is `0.0 < share < 0.5`, which **passes identically under
  the row-count definition W32-5 replaced**. The requirement's entire content is untested, and the
  test that was written to prove the fix cannot distinguish fix from bug.

That third one is the argument for the whole slice: a green test suite has been reporting W32-5 as
delivered on evidence that does not bear on the requirement.

## Part B — three structural blockers, each needing a maintainer decision

These are not work. They are decisions only the maintainer makes, and no amount of code closes
them.

### B1. Phase 1b has no W32 row

**Recommendation:** add one to the table at `../roadmap.md:3773`, after W6b, since W32 is the
non-frontend half of the same split:

| # | Workstream | Depends on | Notes |
|---|---|---|---|
| **W32** | Everything in Phase 1b that is not a browser — contract guards, `model-schema` shapes, a migration, backend defects, endpoint tests, and one skill | W5 | Split from W6b 2026-08-22 (`2026-08-22-w6b-slice-map.md` §1). Ten slices; W6b-1, -3, -5 and -13 are blocked on it |

**Rationale:** the split was made and accepted on 2026-08-22 (slice map acceptance table, first
row, the only one not *pending*), work has been merged under the name through W32-6, and yet the
plan the project reads has no such workstream. Every week this stands, the coverage figure under
"Phase 1b" describes a scope that excludes work being done inside the phase.

### B2. The slice boundaries are still *pending*

The slice map's acceptance table (`:190-194`) marks **four of five rows *pending***, including *"the
slice boundaries and sequencing in §3"*. So W32-1 … W32-6 are proposals that have been executed,
and W32-7 … W32-10 are proposals stacked on unaccepted proposals.

**Recommendation:** accept §3's boundaries as executed for W32-1 … W32-6, and accept or amend the
five new ids above. If any boundary is wrong, now is materially cheaper than after execution — the
plans are independent by construction, so a slice can be re-cut without touching the other four.

### B3. Five slices have no slice record

Only **W32-6** has one. W32-1 through W32-5 were built and merged with ledgers filed under
`docs/plans/` but no record in `../roadmap.md`, so the roadmap cannot answer *what did W32 deliver*
without reading six plan files.

**Recommendation:** back-fill five slice records in the W32-6 record's shape, each naming the
requirements it evidenced and any it left with a §13 verdict. This is bookkeeping, but it is the
bookkeeping §13 exists to force: *"closing without it produces a roadmap reporting progress the
repository does not have, which the next workstream is then planned against"* — and W6b-1, -3, -5
and -13 are the workstream being planned against it.

## Part C — what remains unevidenced after all five plans

§13 rule 2: every requirement without evidence gets one of four verdicts, and silence is not one.
These are the ones the five plans deliberately do **not** close.

| Requirement | Verdict | Owner / reason |
|---|---|---|
| **FR-PLAT-63**, the fourth obligation — the request-path *trigger* that records a switch | **Deferred with an owner** | W32-7 builds `record_switch` and audits both chains, but *when* a switch is recorded is a genuine design choice (audit every selection with `left=None`, versus store the previous selection and diff). Recorded as an open question by W32-7 Task 5; owner **W6b-11**, the workspace switcher, as the first caller that knows |
| **FR-MODEL-126** — the escalated constraint disagreements | **Reassigned** | Named in `UNRESOLVED_CONSTRAINT_DISAGREEMENTS` and governed by `open-questions.md:83`, which is directive that the carve-out is removed in the same commit the two sides agree. W32-1b deliberately does not touch it |
| `dataset-version` and `validation-report` having no generated side | **Not started** | Out of W32-1b's scope with a stated reason; they are a gap in the guard's *reach*, not in its arm attribution |

## Part D — five disagreements the plans record and do not fix

[`CLAUDE.md`](../../CLAUDE.md) §0: when code and spec disagree, stop and resolve — never quietly
make either match the other. Each of these is raised by a plan as an open question and left for the
maintainer, because in every case **which side is wrong is a real question**.

| # | The disagreement | Which side looks wrong |
|---|---|---|
| 1 | `02` §5.2 declares a `holdout` kwarg on `build_shap_summary` that the code does not have | **Neither — this one is not a disagreement.** Commit `b019070` added the signature and appended FR-MODEL-128 (*(appended 2026-08-23, OQ-MODEL-31)*, `../specs/02-modelling.md:232`) together: a dated, owned forward declaration of a function not yet built. Listed so a later audit does not re-raise it |
| 2 | `transparency.py:430-435` prints "% of rows"; `02-modelling.md:1354` says "of exposure" | **The code.** The spec is right and W32-9 changes the code |
| 3 | FR-MODEL-127 says "the three artifact libraries §5.3 renders"; §5.3 renders **one** | **The spec, twice over** — recommendation is to add the two missing §5.3 rows |
| 4 | FR-MODEL-127 says unqualified "`usage_count` is on the row"; §5.1's peril row omits it | Open — W32-8 follows §5.1 and asserts the asymmetry so it cannot close by accident |
| 5 | `.claude/skills/contract-guard/SKILL.md:203-217` counts are stale — 14 uncompared should be 13, three Phase-1a should be two, since W32-2 gave `validation-rule` a generated side | **The skill.** W32-1b fixes it and refreshes `Verified` per §12 |

Number 1 was raised as a §0 stop-and-resolve case and is not one; it is kept in the table because
the difference between *a spec that is ahead of the code on purpose* and *a spec that drifted* is
invisible without reading `git log`, and the next auditor will otherwise spend the same hour.

Number 3 is the one worth a second look: an FR describing three views where the spec renders one is
the kind of drift that produces a route nobody has a screen for.

## Recommended sequence

W32-10 first — it is tests only, it touches nothing the other four touch, and it removes the
false-evidence problem before more work is planned against the same suite. Then W32-9 (smallest
behaviour change), W32-8, W32-1b, and W32-7 last: it is the only one that changes the OpenAPI
surface and so the only one requiring the frontend half of the gate.

B1–B3 are independent of all five and can be settled today.

## Maintainer acceptance

| Item | Accepted |
|---|---|
| The verdict: W32 cannot be closed | **2026-08-24** — accepted, and it now rests on a second ground the proposal did not have: **W32-11**, allocated by Part C's decisions, is unbuilt |
| **B1** — the proposed Phase 1b `W32` row | **2026-08-24** — accepted as recommended; the row is at `../roadmap.md`, after W6b. *(The proposal cited `:3773`; the table had moved to `:3926` by the time the row was written — the W32-9 and W32-10 records landed between.)* |
| **B2** — the slice boundaries, and the five new ids `W32-7`, `-8`, `-9`, `-1b`, `-10` | **2026-08-24** — accepted, no boundary amended: §3's cuts are accepted as executed for W32-1 … W32-6 and as scoped for the five new ids. Mirrored into the slice map's own acceptance table, whose row 2 was the *pending* this depended on |
| **B3** — back-filling five slice records | **2026-08-24** — accepted; the five are written, from each slice's ledger and merge commit rather than from the diffs, and each says in its own text that it was written late |
| Part C's three verdicts, and their owners | **2026-08-24** — the verdicts accepted, **two of the three owners amended**. FR-MODEL-126 and the two uncompared schemas both go to a newly allocated **W32-11** — which had **no executor assigned** when this row was signed, leaving W32 un-closeable by design until the maintainer assigned one, and which **acquired one the same day**: the closure-execution session surfaced the inference and the maintainer confirmed it, adding that W32-11 is the **terminal** slice and that findings it cannot resolve are booked forward with an owner rather than held against the close. Both states are kept — the gap was real when signed: the proposal reassigned FR-MODEL-126 without naming a successor, and OQ-MODEL-30 already owns it to *W32*, so that was not a reassignment; and the schema row said *not started* without recording that it was also **unowned** after W32-1b declined it in writing. **FR-PLAT-63's verdict is not accepted today**: it is *deferred with an owner* only once W32-7 has shipped the mechanism, and until then all four obligations are *not started*. Instantiated against fact at close |
| Part D's five entries, and which side is wrong in each of the four real ones | **2026-08-24** — accepted; **the spec was the wrong side in all four**, and each is amended in place with a dated note rather than rewritten. Item 2 needed no decision — W32-9 merged as `faff060` and settled it in code. One refinement: item 4's conclusion must **not** rest on the peril side's absent `/usage` route, which is a separate question; it rests on the count being undefinable in the direction §4.10 declares |
| The recommended sequence | **2026-08-24** — accepted as amended, and already partly spent: W32-10 (`0e44db9`) and W32-9 (`faff060`) merged before this decision was written. The amendment is the tail — **W32-11 is appended and W32 does not close until it lands** |

**Who accepted, and on what authority — added 2026-08-24, after this plan was filed on
2026-08-23, and forming no part of the document as filed.** *(It sits with the acceptance table
because it is the acceptance record, which `docs/plans/README.md` exempts from the freeze;
Parts A through D above are unaltered, and a reader comparing against the filing-date document
should expect this paragraph and the seven dated rows to be the whole of the difference.)*
The maintainer directed this session on 2026-08-24 to decide Parts B, C and D of this proposal; these acceptances are that instruction discharged,
and the provenance is stated rather than assumed because `CLAUDE.md` §14 makes a review's
output a proposal and never a change. **Anything the instruction did not reach stays
*pending*** — the slice map's rows 3, 4 and 5 are the visible cases, and they go back to the
maintainer rather than being signed here on the strength of being adjacent.
