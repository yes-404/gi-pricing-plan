---
id: CR-932
family: closure
kind: review
title: Plan review 11 — completing the review sequence at WK-671's close, before WK-672 opens
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-31
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 11 — completing the review sequence at WK-671's close, before WK-672 opens, 2026-08-31

**Base tree: `origin/main` at `567eea2`**, clean, confirmed by `git status --short` returning
nothing before this review was drafted. Every claim below was checked at that tree or names
the commit it was checked at.

**A premise this review was dispatched under was wrong, and the correction is recorded here
rather than silently acted on** (`.claude/skills/phase-review` §"When a review gets its own
premise wrong"). The dispatch stated "nobody has run a §14 review for WK-671's close." False:
[Plan review 9](#plan-review-9--at-w11s-close-2026-08-30) and
[Plan review 10](#plan-review-10--at-w11s-second-close-2026-08-30) both exist, both dated
2026-08-30, both drafted with real evidence against real trees. What is true, verified
directly against this document: **both still carry `Maintainer acceptance: pending` — neither
has ever been dated.** The corrected statement, endorsed by the lead in the same exchange that
authorised this filing: *the review sequence for WK-671's close was run but never closed out.*

**What this review is and is not.** It does not re-derive the five questions from a blank
sweep — review 9 and review 10 already did that, at `19eaabc` and `b749acb` respectively, and
re-deriving now would look like work and confirm nothing (`phase-review`'s own rule). Its job
is the agenda that decayed onto "the §14 review at WK-671's close" since those two were drafted:
eleven `docs/findings/register.md` rows that now name this review by that phrase, two residual
items inside a row (F28) that reviews 9 and 10 did not pick up, and the two items named
outside the register when this review was commissioned — the unnumbered rule candidates, and
RFC-896's unfiled impact-matrix row. **Per the lead's ruling on how this review may act:
every disposition below is a recommendation with a rationale, never a filed owner.** Assigning
an owner to a register row is re-planning, and re-planning was carved out of this review's
authority explicitly, the same way it is carved out of every workstream close
(`delivery-process.md` §3). Where the register text already proposes an owner, this review
says so and cites it; it does not adopt the proposal by repeating it as a decision.

---

#### Register rows decayed to this review

`python3 scripts/register-owed.py review`, run against the clean tree above, returns **eleven
owed rows** naming this review (one further row, F28, is excluded by the script as opening
with a resolution marker — its own text says "verify none carries a residual item," and §"F28
residuals" below is that verification, because it does carry two). Grouped by shape, not by id
order, because three of the eleven are one decision and listing them separately would suggest
three separate choices exist where RL-860 already found one mechanism.

**Decision point A (not new — reaffirmed, and explicitly excluded from WK-672).** `FR-240`
(`F-W9-3`) clauses (4)–(6), `F27(c)`, `F29` and `F33` are, per review 9's own framing
(`docs/closures/CR-00925-plan-review-9-at-wk-671-s-close.md:775-778`), **one mechanism** — comparing a spec-declared shape
against its implementation on four axes (contract drift, error-code registration, transitive
maturity resolution, and `mypy` file coverage) — not four independent findings. Review 10
recorded it as **DP-1**, undecided, and the RFC-895/898 reconciliation
(`docs/plans/PL-00900-rfc-895-rfc-898-the-joint-reconciliation-2026-08-30.md:64-69`) confirms it is still open:
*"this reconciliation records that it leaves them; plan review 10 carries them as an open
decision point."* **The lead has since ruled its relationship to WK-672, not its placement**:
the cluster stays **out** of WK-672's spec-change slice, because WK-672's job is to unblock WK-672's
own start and a cross-cutting, unbounded mechanism should not make that start conditional on
a decision nobody has made. This review carries that ruling forward and restates review 10's
three placement options for whoever decides the cluster's actual home — a dedicated slice
(inside a still-to-open Phase 2 workstream), a maintainer task outside the workstream ladder,
or a split by cost (`F33`'s `mypy` widening first, the rest bundled later) — without picking
one. **The one instance inside this cluster's shape that does sit in WK-672's own scope**,
`GOLDEN_QUOTE_MISMATCH` (`F29`'s pattern, one workstream early), **is scoped into WK-672's
spec-change slice directly** — a slice-scoping call the lead made explicitly, on the ground
that the instance is WK-672's even though the class is not. See the WK-672 map plan.

**F26 — still open, verified rather than assumed stale.** Register text: *"owner decided: WK-671
(RL-860)... to land before the charter amendments R6 is holding for the §14 review."* WK-671
closed (twice) without landing it. Verified directly: `.github/workflows/docs.yml:16,18`'s
`paths:` filter is `['docs/**', 'docs/notes/**', 'scripts/audit-docs.py', 'CLAUDE.md',
'.github/workflows/docs.yml']` — no `.claude/roles/**` or `.claude/skills/**`. The gap Ruling
29 named is exactly as open as it was at WK-671's close. **Recommendation**: name a fresh owner
now that WK-671 cannot discharge it — the fix is small and self-contained (a path-filter addition
plus a content check, per task #21's spawn-input constraints already read as a ready-made
spec) and could ride with whichever Work row eventually carries RFC-895/896's own process
tooling, but this review does not pick that Work; it only confirms WK-671 is no longer a live
candidate.

**F31 — reaffirm review 10's own proposal 5.3, still pending.** Register text (amended
2026-08-31): *"review 10 ... drafted exactly this row's 'charter drops the claim' branch and
recommended applying it, but stated explicitly it is 'not decided here.'"* Verified directly:
`.claude/roles/watcher.md:11-24` still describes the roster-derivation clause. Nothing to add
— this review carries proposal 5.3 forward into the acceptance batch below rather than
re-arguing it.

**F48 — the register asks this review to confirm or overturn a provisional WK-674 placement;
this review confirms it, as a recommendation.** `NFR-499`'s per-client rate limit cannot
be an in-process limiter (a per-replica memory counter is not a limit on a multi-replica
deployment), so it needs shared state across replicas or a gateway in front of them. WK-674 is
where the `Environment`/`Deployment` domain entities and their shared-state infrastructure
land (`docs/roadmap.md:379`); building a cross-replica limiter before that infrastructure
exists would mean building a piece of WK-674 under another workstream's name, the same objection
review 8 raised against pulling `FR-250`/`FR-257`'s dependencies forward. **This
review's reading**: keep WK-674. It is a confirmation, not new evidence; the maintainer may still
prefer a platform-level workstream instead, since `NFR-499`'s clause is not itself
`Environment`/`Deployment`-shaped, only dependent on infrastructure that lives there.

**F58 and F61 — one register, two related loose ends, both explicitly asking this review for
an owner and neither getting one from this review.** F58: no process writes
`~/gi-pricing-plan.local/handover/runtime-state.json` on a cycle — verified directly, the file
does not exist and none of the three live watcher-class processes (`balance_watch.py`,
`reporter-cycle.sh`, `watch-external-prs.sh`) reference `write_runtime_state.py`. F61: the C2
retry-cap hook (`scripts/hooks/retry_cap_hook.py`) is disableable per-session
(`disableAllHooks`, or a gitignored `settings.local.json` override) with no CI-equivalent
backstop, unlike its dissolved sibling C3. Both are "needs the lead to name an owner" rows by
their own text. **Recommendation, not a pick**: F58's fix is wiring one of the three live
watcher processes (or a fourth) to call `write_runtime_state.py cycle` on a schedule — a small
task, no research needed; F61's two branches are build the reconciliation RL-907(b) assigns
to "a future watcher cycle," or the lead/maintainer accepts the residual gap as proportionate
in writing. Both fit naturally as one small follow-up to RFC-895 adoption slice G rather than
a new workstream, but this review does not schedule that follow-up — it only says the two
belong together if someone does.

**F62 — routed to the decision-maker, not decided here.** `03` §4.4's `timing_ms` example
names four keys; `score_one` emits two. This is a spec-vs-code disagreement, and
`CLAUDE.md` §0 and `delivery-process.md` §3 both give that call to the decision-maker, not to
a plan review. **Recommendation**: the decision-maker rules between extending
`score_one`/`build_scoring_result` to emit the full four-key breakdown, or correcting `03:419`'s
example to the two keys the engine actually emits. This review requests the ruling; it does
not attempt it.

**F63 — two readings, both already on the register row, the maintainer's to choose between.**
`register-owed.py WK-671` at `f99b55d` found ten register rows attributed to WK-671 that the closure
record's own findings sections never name, all filed before either close. The row states two
readings without choosing: **(a)** F41's own failure recurring at roughly 4x scale — a
hand-compiled closure-record sweep losing genuinely open, WK-671-attributed rows the same way F41
itself was lost; or **(b)** legitimate, undisclosed scoping — a narrower reading of "open
finding" nobody wrote down as a rule. **This review's own reading favours (a)**: F41 was
exactly this shape at one row, and the closure record's own §10.6 text ("None of these are in
the reopen's requirement scope... it revisits exactly the 4 items §6 already named") describes
a sweep scoped to what the closer already knew, which is the same mechanism F41 named, not a
disclosed rule. **The choice is the maintainer's alone**: reopening a Work close is
`CLAUDE.md` §13's exclusive maintainer act, and this review does not attempt it — it states a
reading and stops.

**F28 residuals — two of three carried items were never picked up, and this is new.** F28's
own row lists three items "carried to the §14 review as proposals": P7, P12, and P1b's
working-note half. Review 9 folded in **P7** (Candidate A, the writer's-half branch-freeze
rule) via its proposal 5.4. Verified directly (`grep` across review 9 and review 10's own
text, lines 1233–2472): **neither review mentions P12 or P1b.**
- **P12** (`docs/findings/FD-00894-rfc-840-841-adoption-pilot.md:643`): *"a correction is
  checked by a differently-shaped probe than the one that found the original, never by
  re-reading the passage just edited."* Distinct from review 9's own third candidate ("a
  correction states what it supersedes") — same family of correction-discipline rule, not a
  duplicate. **Recommendation**: fold P12 into the same `delivery-process.md` §15 candidate
  batch as Candidates A, B and the third, numbered together at acceptance rather than left to
  decay a second time.
- **P1b's working-note half** (`pilot-findings.md:632`): *"Still carried: a working note of
  its own, since the reasoning failure generalises past this repository."* The failure is
  diagnosing from a log you have been writing to yourself without subtracting your own
  attempts first — `watcher.md`'s operational fix landed, but the generalisable working note
  never did. Checked `docs/notes/` in full (eighteen notes, `0001`–`0018`): none covers
  this. **Recommendation**: write the note (a `docs/rfcs/0019-…` candidate); this review
  does not write it, since a role writes what its own charter names
  (`.claude/roles/planner.md`) and an NT-numbered working note is nobody's charter item by
  default — flagging it is as far as this review's grant reaches.

---

#### The two items named at commission

**(a) The unnumbered rule candidates.** Status, verified directly: Candidate A (branch-freeze
while under review) and the third candidate raised under review 9's question 3 (a correction
names what it supersedes) are **both already folded into review 9's proposal 5.4**
(`docs/closures/CR-00925-plan-review-9-at-wk-671-s-close.md:775-787`), with numbering deliberately deferred to maintainer
acceptance — correct, per the "Pending proposals" section's own rule that "numbering happens
at acceptance." Candidate B (a count states its own granularity) is in the same proposal.
**P12, surfaced above, was not** — it belongs in the same batch and was missed until this
review re-checked F28's own row against what actually got folded in, rather than trusting that
"carried to the §14 review" had been discharged because a §14 review had since run.
**Recommendation**: the maintainer's acceptance of review 9 (see the bundling recommendation
below) numbers all four candidates — A, B, the third, and P12 — into `delivery-process.md` §15
in one pass, rather than three followed by a stray fourth later.

**(b) RFC-896's impact-matrix row 15.** Verified directly: `docs/rfcs/R
FC-00896-the-register-is-a-ledger-evidence-is-a-file.md:114` names row 15 as *"Adoption plan
`docs/plans/<date>-nt-0015-adoption.md`."* No such file exists in `docs/plans/` (checked by
listing), and `docs/roadmap.md:424` already records why: *"writing a plan today for work
already landed would record a sequencing that did not happen... the deviation is the next
§14 review's to dispose of."* This is that review. **Recommendation, endorsed by the lead
in the dispatch that commissioned this filing**: accept the deviation as deliberate and
dated — by this paragraph, 2026-08-31 — rather than file a plan that would misstate when the
work was sequenced, and close RFC-896's impact-matrix row 15 on that basis. This review
proposes the acceptance; it does not close the row itself, consistent with the same rule that
keeps every other disposition above a recommendation.

---

#### The five questions, in order

**1. Completion — no change, reused from review 10.** `git diff --stat b749acb..567eea2`
touches `.claude/roles/`, `.claude/skills/`, `docs/audit/`, `docs/plans/`,
`docs/process/`, `scripts/`, `tests/` and one line of `docs/roadmap.md` — no file under
`backend/`, `packages/` or `frontend/` changed. Nothing in the RATE requirement surface moved
since review 10's tally; its answer stands without re-derivation.

**2. Omission — one, and it is item (b) above.** RFC-896's row 15 is exactly the shape this
question asks for: a plan the impact matrix named that nobody would otherwise have noticed was
missing, because the work it would have described already landed. Disposed above. No further
omission found in this pass.

**3. Skills and research — the candidate-numbering gap (item (a) and P12) is this question's
finding**, disposed above. `F58`/`F61` (the watcher/RFC-895-adoption loose ends) are process
gaps of the same general kind and are cross-referenced there rather than repeated here.

**4. Document drift.**
- **`FR-241` still cites `FR-247` where it means `FR-270`** — verified directly,
  `docs/specs/03-rating-engine.md:137` unchanged since review 10's proposal 4.1. Two
  characters, still unfixed, still without an owner beyond "the next docs commit." Carried
  forward rather than re-argued.
- **WK-672's row disagrees with `FR-260, FR-261, FR-262` in both directions — reaffirmed, and this is
  what the maintainer's spec-change-slice direction for WK-672 already answers.** Verified
  directly against `docs/roadmap.md:377` and `docs/specs/03-rating-engine.md:176-178,596-597,
  611`: the charter's "regression runs" names an execution route
  (`POST /api/v1/rating-versions/{id}/regression-runs`) that no requirement's own text cites —
  `RegressionRun` is defined only in `docs/contracts/schemas/regression-suite.schema.json`,
  not in `03` §4 — while `FR-262` (Quote Sandbox) sits inside the id range but outside the
  three-item charter and is separately claimed by WK-675's row. `GOLDEN_QUOTE_MISMATCH` (`03:611`)
  is confirmed absent from `backend/src/app/errors.py`'s `RATING_ERROR_CODES`. This is review
  9's own proposal 4.4, unactioned until now; the WK-672 map plan filed alongside this review
  closes the two spec-level gaps and corrects the row's text, and raises `FR-262`'s
  ownership as a named decision point (DP1) in that plan rather than resolving it here — the
  planner's charter reserves decision points with options and recommendations to the plan, not
  the review.
- **`F62`** — disposed above (routed to the decision-maker).

**5. Shape.**
- **No re-cut.** Nothing in this pass disturbs review 8's or review 9's no-re-cut findings for
  the WK-671–WK-674 boundary.
- **DP-1's placement stays a decision, and stays outside WK-672** — the lead's ruling, recorded
  above, carried forward rather than reopened.
- **WK-672 readiness**: the map plan filed alongside this review closes the row-text and
  spec-declaration gaps before any build slice opens, per `CLAUDE.md` §0's table treating "a
  capability not yet specified" as spec-change-first work.

---

#### Recommendation: bundle reviews 9, 10 and 11 into one maintainer acceptance pass

Reviews 9 and 10 have sat with `Maintainer acceptance: pending` since 2026-08-30. The eleven
register rows above cannot be given a final disposition — even the recommended ones — while
the reviews that first surfaced most of them remain unaccepted, and three of the four
unnumbered candidates cannot be numbered without an acceptance line to number them at. **This
review recommends putting all three to the maintainer together, as three acceptances on one
occasion rather than a fourth wait.** The lead has stated this is accepted as a recommendation
and will be carried.

#### Proposals, consolidated — review 11

| # | Proposal | Kind |
|---|---|---|
| 11.1 | Bundle reviews 9, 10 and 11 for one maintainer acceptance pass | process |
| 11.2 | Name a fresh owner for F26 (the CI path-filter gap), now that WK-671 cannot discharge it | owner decision — maintainer/lead |
| 11.3 | Fold P12 into the same `delivery-process.md` §15 candidate batch as Candidates A, B and the third; number all four at acceptance | convention — numbered at acceptance |
| 11.4 | Write the working note P1b's carried half still owes (diagnosing from a self-written log without subtracting your own attempts, generalised past this repository) | working note — unowned |
| 11.5 | Accept RFC-896 impact-matrix row 15 as a deliberate, dated deviation (this section, 2026-08-31) rather than file a backdated plan; close the row on that basis | process acceptance — lead/maintainer |
| 11.6 | Confirm F48's provisional WK-674 placement (this review's reading), or overturn it for a platform-level workstream instead | confirm/overturn — maintainer |
| 11.7 | Give F58 and F61 one combined owner as a small RFC-895-adoption follow-up (wire a live cycle writer; decide C2's reconciliation-or-accept branch) | owner decision — lead |
| 11.8 | Rule F62 (spec-vs-code disagreement on `timing_ms`'s keys) | decision — decision-maker |
| 11.9 | Choose F63's reading (a) or (b); this review's own reading favours (a) | decision — maintainer alone (`CLAUDE.md` §13) |
| DP-1 | (Not new.) The gate-coverage cluster's placement — dedicated slice, maintainer task, or split by cost — stays undecided and stays outside WK-672, per the lead's ruling | decision — lead/maintainer |

#### What this review did not do

- **It did not re-derive questions 1–5 from scratch.** Review 10's completion tally is reused;
  no RATE-surface code changed since `b749acb`.
- **It did not assign an owner to any register row.** Every disposition above is a
  recommendation, per the lead's explicit carve-out for this filing.
- **It did not fold the gate-coverage cluster (DP-1) into WK-672.** The lead ruled that
  separately; this review records the ruling rather than re-arguing it.
- **It did not decide `FR-262`'s ownership.** That is named as a decision point in the WK-672
  map plan, not resolved here.
- **It did not close RFC-896's impact-matrix row 15 itself**, only recommends the acceptance
  that would.

**Maintainer acceptance:** _pending._ Nothing above binds until this line carries a date, and
per proposal 11.1 this review recommends it be dated alongside reviews 9 and 10 rather than
separately.

> **Maintainer acceptance: accepted as proposed, 2026-09-01 — dated together with reviews 9 and
> 10 under review 11's proposal 11.1.** The `_pending._` sentence above is kept as the record;
> the premise-correction sentence in the section above it ("neither has ever been dated") is
> likewise superseded by these datings and kept as the record of the state it was written
> against. **Applied with the dating:** the eleven register rows behind this review now pass to
> their named owners (this review's own table above lists which); the four unnumbered rule
> candidates — Candidate A, Candidate B, review 9's third, and P12 — are numbered in the same
> pass into `docs/process/delivery-process.md` §15, applied by the lead, not written here.

#### Sources

- `docs/closures/INDEX.md#plan-reviewsmd` — reviews 8, 9 and 10, read directly in full (lines 1–2472) for
  the premise correction, the DP-1 history, and the candidate-folding check.
- `python3 scripts/register-owed.py review`, run against `567eea2` — eleven owed rows, one
  excluded (F28).
- `docs/findings/register.md` rows FR-240/F-W9-3, F26, F27, F29, F31, F33, F48, F58, F61, F62,
  F63, F28 — read directly at `567eea2`.
- `docs/plans/PL-00900-rfc-895-rfc-898-the-joint-reconciliation-2026-08-30.md:40-69` — read directly, for DP-1's
  status and the gate-coverage cluster's disposition.
- `.github/workflows/docs.yml:16,18` — read directly, to confirm F26's path filter is
  unchanged.
- `.claude/roles/watcher.md:11-24` — read directly, to confirm F31's clause is unchanged.
- `docs/findings/FD-00894-rfc-840-841-adoption-pilot.md:600-650` — read directly, for F28's
  P7/P12/P1b dispositions and owners.
- `docs/notes/` (`0001`–`0018`), listed in full — to confirm no note covers P1b's carried
  half.
- `docs/rfcs/RFC-00896-the-register-is-a-ledger-evidence-is-a-file.md:114` and
  `docs/roadmap.md:424` — read directly, for RFC-896's row 15 and its own stated disposition
  owner.
- `docs/specs/03-rating-engine.md:137,176-178,596-597,611` — read directly.
- `docs/contracts/schemas/regression-suite.schema.json` — read directly, confirming
  `RegressionRun`'s shape and its absence from `03` §4's own text.
- `backend/src/app/errors.py` — read directly (`grep -n GOLDEN_QUOTE_MISMATCH`, zero hits),
  confirming the code is unregistered.
- `git diff --stat b749acb..567eea2` — run this session, to confirm no RATE-surface code
  changed since review 10.
- `git status --short` — run this session, confirming a clean tree at `567eea2` before
  drafting.

---

#### Correction appended 2026-09-01 — review 11's F31 paragraph misattributes proposal 5.3

**The paragraph above — "F31 — reaffirm review 10's own proposal 5.3" (this file, line 2549
at `43fd277`) — names the wrong review.** The only proposal numbered 5.3 in this file sits
inside plan review 9's section: its prose at `:1979-1981` ("Recommendation (5.3): apply it —
a role-file edit…") and its consolidated table row at `:2066` ("5.3 — Apply F31's charter
correction to `watcher.md` — text already drafted in the withdrawal notice"). Plan review 10's
section (`:2151-2476`) carries no 5.3 in prose or table — `sed -n '2151,2476p'` piped to
`grep '5\.3'` returns nothing. **What the paragraph *meant* is unchanged**: review 11 carries
proposal 5.3 forward into the acceptance batch; the review that first proposed it is review 9.

The same misattribution is shared by the register text the paragraph quotes —
`docs/findings/register.md`'s F31 row cites `plan-reviews.md:1979-1981` but labels it "review
10" — and is flagged here for the register's owner rather than edited: the register is the
auditor's file, not the planner's (`.claude/roles/planner.md`). The landing package's §1.2
(`docs/plans/PL-00938-rfc-897-landing-package-the-reconciliation-update-the-work-row-draft-and-the-acceptance-batch-2026-09-01.md`) made the same error when written and is
corrected on its own branch, PR #549.

---
