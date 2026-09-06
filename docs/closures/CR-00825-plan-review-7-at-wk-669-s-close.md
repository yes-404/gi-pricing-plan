---
id: CR-825
family: closure
kind: review
title: Plan review 7 — at WK-669's close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-27
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 7 — at WK-669's close, 2026-08-27

`CLAUDE.md` §14's seventh run, filed retroactively on 2026-08-29 together with review 8:
WK-669 closed 2026-08-27 and WK-670 closed 2026-08-28, and `CLAUDE.md` §14's trigger is fixed —
"at each workstream close" — so both were owed and neither had been filed before WK-671 was
next in line. **The output is a proposal, never a change** — every recommendation below
needs a dated maintainer acceptance line before it binds. Evidence derived at `origin/main`
`07ae047`, rebased onto `d4bc394` while this PR was open (see review 8, Question 4: `d4bc394`
is in fact one of this pair's own recommendations, landed independently before either review
was filed). Nothing else moved underneath this review — `07ae047` (#313) touched only
`docs/notes/`, and `d4bc394` (#314) touched only the two lines review 8 names.

**1. Completion — reused, not re-derived.** WK-669's own closure record already carries fresh
completion evidence for its scope (`docs/closures/CR-00838-work-item-record-wk-669-the-rating-contract-validation-and-bundle-compilation.md:26-29`), so it is cited
rather than repeated: FR-212, FR-213, FR-214, FR-215, FR-216, FR-217, FR-219, FR-220, FR-221, FR-222, FR-225, FR-226, FR-227, FR-237, FR-238, FR-239, FR-240, FR-241, FR-242 and FR-273/274/275/276 delivered, and —
outside WK-669's own row's stated numeric range — **FR-223**, marker-evidenced (3 files),
correctly caught the same way WK-670 later caught FR-232. No change proposed to WK-669's
completion claim.

**2. Omission — what the phase needs that no row names.**

**FR-224 and FR-218 have no workstream row.** (Verifying the hypothesis this review
was handed: it named FR-223 alongside FR-224. FR-223 is not part of this gap —
see Question 1 — it was verdicted in WK-669; its own roadmap-row text simply omits it from the
literal range, a wording correction rather than a coverage gap.) Both 61 and 63 were decided
2026-08-18 — OQ-576 into FR-224 (`03-rating-engine.md:110`, §3.2), OQ-617 into
FR-218 (`:87`, §3.1). Neither appears in any `W_` row's stated scope: a full-file grep of
`docs/roadmap.md` for both ids returns exactly two hits, both inside OQ-617's and
OQ-576's own decided-narrative text (`:536`, `:567`), never inside a workstream row.

**The two are not the same shape of gap, and the lead's own verdicts on this evidence (issued
2026-08-29, `CLAUDE.md` §12 — verdicts stay in the main thread) say so precisely; this review
carries that finding rather than re-deriving a competing one.** FR-218 is a **WK-669 close
gap**, not an orphan: nothing blocked it — FR-217 (sub-graphs) was W9-1's own delivery,
and FR-218 is a `RatingVersion` pins-extension structurally identical to what W9-3 built
for FR-223 in the *same* PR (#293). It was decided 2026-08-18, nine days before WK-669
closed (2026-08-27) — not the one-day window first reported (`git log`, UTC: #291 at
2026-08-27T21:48Z, #292 at 22:42Z, #293 at 23:44Z, and WK-669's close commit `eb9b6a1` at 23:47Z
the same day). A week-plus window, not a same-day scramble: FR-223,
decided one day *before* FR-218, rode into #293 on that same merge, so the
identical-shape sibling requirement had every opportunity to ride in beside it and did not.
WK-669's own scope prose
names four sections totalling 26 requirements; it verdicted 24. **WK-669's closure record
reports a completeness the repository does not have** — `CLAUDE.md` §13's own stated failure
mode, on work already closed. FR-224, by contrast, genuinely could not have been built
by WK-669: its own text needs a Dislocation Run (FR-263), which is WK-673's, so it is orphaned
at birth rather than missed at a close.

Why it matters going forward, not only as a retrospective correction: **FR-224
specialises FR-257's approval gate for the approximation-mode case** — WK-671 builds the
general gate, and WK-673 already owns the Dislocation Run that both need, making WK-673 the
natural single owner of the specialisation rather than splitting one gate's logic across two
workstreams. **FR-218 bears directly on WK-671's evaluator regardless of who owns the id,
and it itself splits in two.** `purpose` is not a hypothetical extension point — it is
already a fully-typed `QuoteContext` field every scoring call reads unconditionally
(`03-rating-engine.md:63` glossary: `new_business | renewal | mid_term_adjustment |
cancellation | what_if`; `:389` shows it live in the request JSON example), so both halves
below are properties of code WK-671 slice 1 is building regardless of FR-218's ownership:

- **The refusal guard** — when `purpose ∈ {mid_term_adjustment, cancellation}` and the
  Rating Version has no matching mounted sub-graph, `score_one` must refuse rather than
  silently price as new business (`03:87`: "it is silent" is the failure named). This is a
  `score_one` correctness property with the same universal shape as FR-274's
  null-output guard — provable only by a slice-1 test on deliberately broken input — and has
  no dependency on anything WK-669 did or did not build: even before any Rating Version can
  mount such a sub-graph, the guard is meaningful, because it turns an unbuildable feature
  into a loud, correct refusal instead of a silent wrong price. **Recommend: WK-671 slice 1,
  unconditionally.**
- **Sub-graph mounting and refund/pro-rata authoring** — declaring the separately-versioned
  sub-graph itself, version-pinning it, and mounting it on a Rating Version — is algorithm
  *definition* work, the same kind as WK-669's own scope (§3.1), not scoring/evaluation work.
  Folding it into WK-671 would blur WK-671's boundary into authoring territory the same way pulling
  Environment/Deployment forward would (Question 5, review 8) — for a capability nothing in
  WK-671 needs in order to build the guard above. **Recommend: a small, separately-owned
  catch-up slice, landing with or before WK-671 but not part of its plan** — matching the shape
  of W9-3's own delivery of FR-223, since FR-218 is that requirement's structural
  twin. This review does not name a workstream id for it; that is the maintainer's, the same
  restraint plan review 2's Proposal B applied to naming WK-664's split.

> **Recommendation:** FR-224 gets a register row with owner **WK-673** — it never depended
> on this review, since WK-671 was never a candidate owner for it, and it has since landed as
> `docs/findings/register.md`'s F-W9-2 (PR #319), recorded here as confirmation rather than an
> open ask. FR-218's id-level ownership (a corrected WK-669 closure note, or a new row) is
> this review's to propose and the maintainer's to accept — deliberately held out of the
> register until this line carries a date, so a row does not pre-empt the acceptance that
> names its owner. Its build obligation does not wait on that answer either way and splits
> as above — the refusal guard in WK-671 slice 1 unconditionally, the authoring half in its own
> small slice separate from WK-671. Not a roadmap edit on this review's own authority.
>
> **Maintainer acceptance: accepted 2026-08-29 — the split binds; the owner is still not
> named.** What is accepted is the *shape*: FR-218's refusal guard is WK-671 slice 1's
> unconditionally, and the sub-graph mounting and refund/pro-rata authoring half is a separate
> small catch-up slice, WK-669-shaped, landing with or before WK-671 but not part of its plan.
>
> **What acceptance does not do is name the workstream.** This review deliberately declined to
> name one — *"that is the maintainer's, the same restraint plan review 2's Proposal B
> applied"* — and the acceptance relayed today carries no id either. So FR-218's id-level
> ownership (a corrected WK-669 closure note, or a new row) is **accepted as owed and explicitly
> unowned**, per review 4's question-5 rule above. Verified at `3edd75a`: `FR-218` appears
> in `docs/findings/register.md` only inside F27's prose about `scoring.schema.json`'s `purpose`
> enum, and in `docs/roadmap.md` only at the OQ-619 decision prose — no register row and no
> workstream row owns the id. The register row this recommendation was held out of is now
> released to be written, and writing it is not this document's to do.
>
> **F-W9-2 needed no acceptance line to bind**, since it was never this review's proposal to
> make; that half is unchanged by this date.

**3. Skills and research — re-run, not appended to.**

One gap found, self-referential: **the `phase-review` skill's own "Output" section was
stale.** It named `docs/roadmap.md` as where a review's proposals land; the location moved
to `docs/closures/INDEX.md#plan-reviewsmd` on 2026-08-27 (RFC-813), two days before this skill was next
read. **Fixed in this commit** (`CLAUDE.md` §12: a skill found wrong is fixed in the same
session, `Verified` date refreshed) — the file this review is filed into is the proof the fix
is correct.

No other skill or research gap found against WK-669's own scope. Carried into review 8's
Question 3, not repeated here: no spike or research artifact covers the ZEN engine's
*evaluate*-side behaviour — WK-669 never needed it, WK-671 will be the first to.

**4. Document drift.** Two disagreements found, both inside code WK-669 itself shipped, both
routed to the decision-maker rather than ruled here (`CLAUDE.md` §0: stop and resolve, never
quietly make either side match — this review's job is to name the disagreement precisely,
not to rule it):

- **The compile endpoint is specified 202 and implemented 200.** `03-rating-engine.md:513`
  specifies `POST /rating-versions/{id}/compile` as `**202** Compile + validate the bundle`;
  the shipped route (`backend/src/app/api/models.py:1139-1161`, wired to
  `compile_rating_version`, `backend/src/app/platform/rating_versions.py:226-288`) returns
  200 synchronously. Bears directly on WK-671: today the route persists only
  `{content_hash, bytes, compiled_at}` and discards the full compiled Bundle
  (`rating_versions.py:283-287`) — the slice that fixes that and persists the Bundle proper
  may push the operation past a synchronous-response budget, which is a reason to rule
  before that slice starts, not after. Two further code-vs-spec items surfaced since this
  review began, queued to the same decision-maker ruling rather than re-litigated here:
  `compile_bundle` is async in code (`compile.py:387`) against a synchronous §5.2 signature,
  and `CompiledBundle` — the type every §5.2 scoring/dislocation/regression signature
  takes — has no code definition anywhere; the shipped class is `Bundle`, and whether that is
  a rename or `CompiledBundle` must become a distinct loaded-runtime wrapper is an
  architecture question for WK-671 slice 1, not a spelling one.
- **`POST /api/v1/rating-versions` (`03:512`) cites no requirement.** Every other §5.1 row
  names the FR- it implements; this one reads only "Create a draft Rating Version with
  pins." Two readings are both live: a capability the spec never got around to numbering
  (needs an appended FR), or a Phase-1b-era row (`03` §4.3's own OD1/W7-3 scoping note
  describes exactly this kind of provisional minimal shape) never tombstoned when Phase 2
  widened the contract. Which reading is correct changes what the register owes it.

> **Recommendation:** all four items go to the decision-maker's queue before WK-671's plan is
> filed — the compile 202/200 divergence, the async/sync mismatch and the
> `Bundle`/`CompiledBundle` question before any slice touches `compile_rating_version` or
> starts the evaluator, the missing citation whenever convenient since nothing currently
> depends on its answer. None is resolved in this review — that queue reports itself
> complete as of this filing, which this review notes rather than duplicates: the rulings
> themselves are a decision-maker record, not a plan-review one.
>
> **Maintainer acceptance: accepted 2026-08-29 — and all four items have since been ruled, so
> this line confirms rather than releases them.** Verified at `3edd75a`, each against the
> artifact that discharged it rather than against recollection: the compile-endpoint 202/200
> divergence is `docs/rulings/RL-00865-the-compile-endpoint-specified-202-implemented-200.md` RL-865; the async/sync
> `compile_bundle` mismatch is RL-866; the `Bundle`/`CompiledBundle` question is RL-867;
> and the missing citation on `POST /api/v1/rating-versions` is now on the row itself —
> `docs/specs/03-rating-engine.md:513` reads *"Create a draft Rating Version with pins
> (FR-237)"*, landed with WK-671 Task 1.1 (PR #371). **Owner: discharged, none owed.** The
> recommendation was that these reach the decision-maker's queue before WK-671's plan was filed;
> they did, and the acceptance records that the route taken was the route proposed.

**5. Shape.** No change proposed to WK-669's own scope or boundary — it closed against a
coherent, single-subject row and nothing in this review's evidence argues otherwise. The
shape question that matters is about the workstreams *after* WK-669, visible only once WK-670's
close is reached and WK-671 is next — carried into review 8 immediately below, where it belongs.

#### Proposals, consolidated — review 7

| # | Proposal | Kind |
|---|---|---|
| 2.1 | FR-224: register row, owner **WK-673** (specialises FR-257 for approximation mode; never depended on this review) | decision — **landed, F-W9-2, PR #319** |
| 2.2 | FR-218: id-level ownership (corrected WK-669 note, or a new row) is this review's to propose | decision |
| 2.3 | FR-218 splits: the refusal guard is WK-671 slice 1's, unconditionally; sub-graph mounting/authoring is a separate small catch-up slice, WK-669-shaped, not part of WK-671 | decision |
| 3.1 | `phase-review` skill's Output section corrected to `docs/closures/INDEX.md#plan-reviewsmd` | skill (fixed in this commit) |
| 4.1 | Compile-endpoint 202/200 divergence, the async/sync `compile_bundle` mismatch, and the `Bundle`/`CompiledBundle` question ruled by the decision-maker before WK-671 touches `compile_rating_version` or the evaluator | decision — queue reports complete as of this filing |
| 4.2 | `POST /api/v1/rating-versions`'s missing FR- citation ruled | decision |

**Maintainer acceptance: accepted as proposed, 2026-08-29.** All six rows bind from that date.
Per row, with the owner review 4's question-5 rule now requires — and where no owner can be
named without a `docs/roadmap.md` edit, the row says **unowned** rather than leaving it to be
inferred:

- **2.1 — accepted, and already landed.** F-W9-2, PR #319. Never depended on this review.
  **Owner: WK-673**, as the row states.
- **2.2 — accepted as owed, owner not named. Unowned.** See the per-item line above: the
  review declined to name a workstream and today's acceptance names none either.
- **2.3 — accepted.** The refusal guard is **WK-671 slice 1's**; the authoring half is its own
  small catch-up slice, **unowned** until 2.2's owner is named.
- **3.1 — accepted, and landed. Owner: discharged** — but not on the date the table claims,
  and the divergence is recorded rather than smoothed. The row reads *"fixed in this commit"*,
  i.e. review 7's own filing on 2026-08-27; `.claude/skills/phase-review/SKILL.md`'s `Verified`
  block dates the Output correction to **2026-08-29** and says it was *"caught while filing
  plan reviews 7 and 8"* — caught then, applied two days later. The skill now reads
  *"Proposals land in `docs/closures/INDEX.md#plan-reviewsmd`"* (`:110`), so the proposal is discharged
  either way; what was wrong was the parenthetical, checked here rather than restated on the
  table's word.
- **4.1 — accepted, and discharged** by prework Rulings 2, 3 and 4. **Owner: discharged.**
- **4.2 — accepted, and discharged**: the FR-237 citation is on `03` §5.1's row at
  `:513`. **Owner: discharged.**

---
