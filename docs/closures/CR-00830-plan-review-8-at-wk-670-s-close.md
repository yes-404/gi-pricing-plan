---
id: CR-830
family: closure
kind: review
title: Plan review 8 — at WK-670's close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-28
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 8 — at WK-670's close, 2026-08-28

`CLAUDE.md` §14's eighth run, filed retroactively on 2026-08-29 alongside review 7 — see
review 7's opening for why both were owed. **The output is a proposal, never a change.**
Findings about a later phase are spec changes only (§0's table). Evidence as review 7:
derived at `origin/main` `07ae047`, rebased onto `d4bc394` — see review 7's opening.

**1. Completion — reused, not re-derived.** WK-670's own closure record already covers its
scope in full (`docs/closures/CR-00834-work-item-record-wk-670-rate-tables.md:29-37`): FR-228, FR-229, FR-230, FR-231, FR-233, FR-234, FR-235, FR-236 and FR-232, all
"delivered and tested." Module-wide, current: **78 `RATE` requirements in scope, 34
evidenced (44 %)** (`scope-audit.py RATE`, run this session at `main@74b1b10`, confirmed
unchanged through `07ae047` and `d4bc394` — both touched only prose (working notes; the
FR-252/NFR-501 correction this review's own Question 4 discusses), no code, no
markers). §3.7/§3.8's eleven WK-671 requirements are 0/11 evidenced — expected, WK-671 has not
started. No
disagreement between the roadmap's completion claim and the derived numbers.

**2. Omission.** No new omission beyond what the register already carries with named
owners: **F-W10-2** (FR-231 exposure-weight wiring, owner: portfolio-dataset
integration) and **F-W10-3** (`POST /rate-tables/{slug}/versions` has no route, owner: the
WK-675 rate-table editor) — both `docs/findings/register.md:26,29`, neither WK-671's. This review's
actual findings are research and shape gaps, Questions 3 and 5 below, not requirement-
ownership gaps, which is why they sit there instead of here.

**3. Skills and research — re-run, not appended to.** Carried from review 7: **no spike or
research artifact has ever exercised the ZEN engine's evaluate-side (Decision/graph
execution) behaviour.** Spike S1 (`docs/research/track-a-findings.md` F1/F14) tested
decimal-semantics correctness through the engine's expression path; spike S2 tested a bare
XGBoost booster's latency (`nthread=1`) in a Python loop, with no ZEN graph involved at all —
confirmed directly: `packages/pricing-core/src/pricing_core/rating/compile.py` is the only
file anywhere that imports `zen`, and only for `zen.compile_expression`'s syntax check.
Nothing anywhere calls the engine's `Decision`/evaluate API. WK-671's evaluator will be the
first code in this repository to do so, under real concurrency (NFR-454's 200 rps
sustained per replica), and nobody has verified the Python binding's behaviour under
concurrent async calls — whether it blocks the event loop, whether it is thread-safe.

> **Recommendation:** a short, targeted spike on the ZEN binding's evaluate-side concurrency
> behaviour, in the shape of S1/S2 (a dated finding in `docs/research/`, not a full skill),
> run at the *start* of WK-671's evaluator slice rather than discovered mid-slice. This is
> research, not a workstream deliverable in itself — it gates an architecture choice
> (whether `score_one` needs `run_in_executor` thread-pool offload) rather than adding a
> requirement.
>
> **Maintainer acceptance: accepted 2026-08-29 — and already discharged, so this line confirms
> the route rather than authorising it.** The spike ran and landed as
> `docs/research/zen-evaluate-concurrency.md` (PR #321), in exactly the shape proposed: a dated
> finding under `docs/research/`, not a skill, run at the start of the evaluator slice rather
> than discovered mid-slice. It answered the architecture question the recommendation named —
> sync `evaluate()` blocks the event loop, thread-offloaded `evaluate()` is worse than
> sequential, `async_evaluate()` is both non-blocking and faster — and that answer is now
> prework RL-868. **Owner: discharged.** One limit worth recording where the acceptance is,
> because it is the kind of thing a "discharged" mark otherwise hides: the spike measured an
> expression-only graph, and RL-868 carries a named follow-up to repeat it once a
> `model_call` custom node exists. Accepting 3.1 does not accept that follow-up as done.

**4. Document drift.** **The requirement-range omission has now fired twice, and it is a
finding about how rows are written, not two coincidences.** WK-670's own row read
`FR-228, FR-229, FR-230, FR-231, FR-233, FR-234, FR-235, FR-236` and omitted FR-232 (added mid-workstream, corrected at WK-670's close,
`docs/roadmap.md:375`). WK-671's row reads `FR-250, FR-251, FR-253, FR-254, FR-255, FR-256, FR-257, FR-258, FR-259` and omits **FR-252**
(`03-rating-engine.md:162`, §3.7, decided 2026-08-18 with OQ-619, sitting between
FR-251 and FR-253 in the spec's own document order) — the same mechanism: an
append-only id landed inside a section after the roadmap row naming that section's range was
already written, and the row was never re-checked against the section's current membership.

> **Recommendation — landed while this review was being filed.** WK-671's row and NFR-501
> both needed exactly the correction this review was about to propose, and PR #314
> (`d4bc394`) shipped both before this PR opened: the row now reads `FR-250, FR-251, FR-253, FR-254, FR-255, FR-256, FR-257, FR-258, FR-259,
> FR-252 (added 2026-08-18 with OQ-619 — the row's original "FR-250, FR-251, FR-253, FR-254, FR-255, FR-256, FR-257, FR-258, FR-259" omitted
> it); NFR-489 is the hard target` (`docs/roadmap.md:376`), mirroring WK-670's own
> correction exactly as recommended; and NFR-501 now carries a dated amendment
> (`03-rating-engine.md:788`, amended 2026-08-27, WK-668) reconciling it to the 1.626 ms
> figure the register already cited, the same treatment NFR-502 got. Recorded here as
> confirmation, not as an open recommendation — updated in this branch after rebasing onto
> the fix, so this document does not assert something main had already made false. No
> action remains on either point.
>
> **The mechanical fix is still open, and is this review's actual proposal:** a numeric
> range in a workstream row is a derived summary of a spec section's membership, and it
> silently rots every time that section gains an append-only id — which is guaranteed to
> keep happening, since append-only is the rule (`CLAUDE.md` §5). The row should name the
> **section** (`§3.7`, `§3.8`) as the citation of record, with the numeric range kept only
> as a human-readable gloss beside it, never as the sole scope statement — so a check as
> cheap as "does every bolded FR- id in this section appear in the row it maps to" can catch
> the omission mechanically instead of at the next close. Whether that check belongs in
> `audit-docs.py` or `scope-audit.py` is an implementation choice for whoever owns it, not
> decided here. Landing the two individual fixes (above) does not close this half — the same
> mechanism will fire a third time on some future row unless the check exists.
>
> **Maintainer acceptance: the mechanical fix is accepted 2026-08-29. Unowned, and the
> mechanism has since fired a third time.** What binds is the shape: a workstream row cites
> the spec **section** as its scope of record, with any numeric range kept only as a
> human-readable gloss beside it, never as the sole scope statement.
>
> **Acceptance does not choose where the check lives.** The recommendation left that open —
> *"whether that check belongs in `audit-docs.py` or `scope-audit.py` is an implementation
> choice for whoever owns it, not decided here"* — and nothing in today's acceptance closes
> it. **Owner: unowned**, per review 4's question-5 rule.
>
> **The third firing, verified at `3edd75a` rather than predicted.** `docs/roadmap.md`'s WK-671
> row still reads `FR-250, FR-251, FR-253, FR-254, FR-255, FR-256, FR-257, FR-258, FR-259, FR-252`, and **FR-243 sits outside that range** —
> it is the requirement that defines `CompiledBundle` as a distinct runtime type, `03` §3.4,
> discharged by WK-671 Slice 1 Task 1.3, and `git grep -n "FR-243" -- docs/roadmap.md`
> returns nothing. So the recommendation's own prediction — *"the same mechanism will fire a
> third time on some future row unless the check exists"* — is now an observation. Recorded
> here rather than fixed here: correcting the row is a `docs/roadmap.md` edit and this is a
> review document.
>
> **The two individual corrections remain live and needed no acceptance line to bind.**
>
> **A second mechanism, distinct from the range omission and with a different fix.** The
> same period produced corrections to a *measured figure* — NFR-501 (#314) and
> OQ-615 across six locations (#317). The executor, who swept them, named why they were
> never caught together: **a fact copied into free prose is corrected only where the
> tooling structurally links the copy back to its source.** This repository has exactly one
> such link — the OQ mirror pair, enforced by `audit-docs` checks 4 and 23 — and it worked:
> the two OQ-615 copies could not diverge. Everywhere the same figure was merely *quoted in
> passing* — a requirement's rationale (FR-224's body), a roadmap cell, a
> `skills-map.md` row, and another module's open question (OQ-576) — nothing but a
> literal-text grep could find it. So each correction event fixed the one location that
> prompted it, and every other copy survived until someone ran that grep.
>
> **Recommendation:** extend the pattern this repository has already built rather than
> invent a new check — the OQ mirror pair is the working precedent. The cheaper floor, if
> extending the structural link is too costly: make *"grep the figure or range across all
> of `docs/`"* a standing step in the correction procedure itself, so the sweep is not left
> to whoever happens to think of it. Credit: found and articulated by the executor while
> sweeping OQ-615.
>
> **A worked instance found while filing this review, in the tool that catches this
> everywhere else.** `scripts/audit-docs.py`'s own module docstring enumerates checks 1
> through 22; the code also runs check 23 (`:821`, the open-question mirror status this
> paragraph cites) and check 24 (`:760`, the §5.3/§5.6 route-column agreement), neither
> listed there; `.claude/skills/docs-audit/SKILL.md` separately states "twenty-three
> checks." Three artifacts, three counts, and nothing links them — the same mechanism this
> question names, surviving inside the instrument built to prevent it.
>
> **Maintainer acceptance: accepted 2026-08-29 — the proposal binds, the limb is not chosen,
> and the worked instance is fixed.** The recommendation is a disjunction — *extend the
> OQ-mirror pattern (`audit-docs` checks 4 and 23) to a measured figure,* **or** *make
> "grep the figure or range across all of `docs/`" a standing step in the correction
> procedure.* Accepting the proposal accepts that one of them must happen; it does not pick
> which, and satisfying either limb is what discharges it. Naming that explicitly, because
> declining one limb of a disjunction is not satisfying it, and a later reader checking only
> the mirror half would read a satisfied proposal as open. **Owner: unowned.**
>
> **The worked instance is resolved, verified at `3edd75a` rather than assumed from its age.**
> `scripts/audit-docs.py`'s module docstring now enumerates checks 1 through **24**, so 23 and
> 24 are no longer unlisted; and `.claude/skills/docs-audit/SKILL.md` no longer states a count
> at all, saying instead that *"the script's own module docstring is the numbered list, kept
> current there rather than counted here."* Three artifacts with three counts became one
> artifact with the count and two pointing at it — which is the structural half of this
> proposal applied to the instrument, arrived at independently of this line. **The general
> proposal is not discharged by it**: one instance being fixed is not the standing step, and
> the credit to the executor who found and articulated the mechanism stands as recorded.

**5. Shape — is the cut still right?**

**Yes, this review has a shape finding, and it is the one this pair of reviews exists to
raise.** The roadmap's workstream table numbers Phase 2 linearly — WK-671 (scoring), WK-672
(testing), WK-673 (dislocation), WK-674 (deployment) — and that numbering describes an execution
order the requirements themselves do not support:

- **FR-250** (`03:160`, WK-671) scores against "the Rating Version currently live in the
  target environment." FR-238 (`03:134`) is explicit that "live is a property of a
  **Deployment**, and the same Rating Version can be live in `uat` and not in `prod`."
  Deployment (FR-267, §3.10) and the Environment domain entity itself (FR-428, `07`)
  are both **WK-674**'s (`docs/roadmap.md:379`) — three workstreams after WK-671. No Environment or
  Deployment class exists in code today (confirmed: only an unrelated app-config
  `Environment` enum in `backend/src/app/config.py`, and a bare `environment: str | None`
  field on an unrelated model in `packages/model-schema/src/model_schema/approvals.py`).
  `docs/workflows/WF-00701-deploy-and-monitor.md` confirms the intended sequence directly: its
  Phase A step A4 has a Consumer System scoring test quotes *after* a Deployment (step A1)
  already exists — the workflow was never written assuming WK-671 alone reaches a live quote.
- **FR-257** (`03:172`, WK-671) refuses `approved` without a passing Regression Suite
  (FR-261, **WK-672**) and a Dislocation Run (FR-263, **WK-673**) — both unbuilt when WK-671
  starts. `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md` steps D1/D6/E2/E3 confirm this is
  load-bearing, not incidental: step E3 names a concrete failure (`EVIDENCE_INCOMPLETE`, a
  stale dislocation run) that cannot be produced before WK-673 ships.

Neither dependency is a defect in the *spec* — FR-238 and FR-257 read exactly as
intended. The defect, if it is one, is in treating WK-671 → WK-672 → WK-673 → WK-674's numbering as an
*execution* order, when the actual dependency graph has WK-671 needing pieces of WK-674 and
WK-672/WK-673 before WK-671's own two requirements can be *completed* — not merely started.

**Recommendation: no re-cut of the workstream boundaries.** Three reasons:

1. **The mechanism that handles this already exists and already works.** F-W9-1
   (NFR-502/501, carried to WK-671), F-W10-2 (FR-231 exposure weighting, carried to
   portfolio-dataset integration) and F-W10-3 (the rate-table-version route, carried to WK-675)
   are the same shape of problem at smaller scale — a workstream ships what it can and
   defers the rest to a named owner in the register. FR-250's live default path and
   FR-257's two preconditions are larger instances of the identical pattern, not a new
   one.
2. **The dependency is domain-inherent, not an artifact of the cut.** No renumbering of
   WK-671-W14 changes the fact that "live" cannot mean anything before a Deployment exists, or
   that a Dislocation Run cannot run before WK-673 builds it. Moving code between workstream
   numbers does not make Deployment exist sooner; only building it does.
3. **Re-cutting has a real cost the deferral does not.** Pulling a piece of
   FR-428/FR-267 forward into WK-671 would blur WK-671's boundary into WK-674's territory for
   a shape (`Environment`'s promotion-order behaviour, `WF-701` step C2) that is not actually
   separable into a cheap shell — it would mean partially building WK-674 under WK-671's name.
   Holding WK-671 back until WK-672-W14 land first would idle the evaluator work — the thing at
   the most schedule risk per this same roadmap's own risk row (`docs/roadmap.md:392`) —
   behind three workstreams that do not touch it.

The precedent this leans on is Phase 1a's own: no single workstream (WK-669, bundle compilation;
WK-670, rate tables) was independently demo-able either, and neither was held to that bar. The
phase's demo-able outcome (`docs/roadmap.md:365-367`) already names the full
WK-671-through-WK-674 sequence as what is demonstrable, not any one workstream — consistent with
treating this as a completion-ordering fact about two specific requirements, not a mis-cut
of the workstreams that carry them.

**What this recommendation does not excuse:** FR-250 and FR-257 must each get an
explicit, named, dated deferral in the register when WK-671 closes — not silence, and not a
plan that quietly ships a stub and calls the requirement done. That is WK-671's own plan's job
(its DP1 and DP2), not this review's; this review's job is only to say the boundaries
holding it are the right ones.

> **Maintainer acceptance: accepted 2026-08-29 — no re-cut of Phase 2's WK-671–WK-674 boundaries.**
> The completion-ordering reading binds: FR-250's default-live path and FR-257's
> approval gate are not separable into a cheap shell, and neither pulling WK-674 forward nor
> holding WK-671 behind WK-672–WK-674 is worth its cost.
>
> **Acceptance makes the paragraph above binding. It does not meet it.** The clause is a
> condition on WK-671's close, not a recommendation that acceptance discharges: FR-250 and
> FR-257 must **each** get an explicit, named, dated deferral in
> [`../findings/register.md`](../findings/register.md) when WK-671 closes — not silence, and not a stub shipped and
> called done. Approving the no-re-cut recommendation is what puts that obligation in force;
> it is the price of the boundaries being held, and reading this date as having satisfied it
> would invert the clause.
>
> **Unmet as of 2026-08-29, verified rather than assumed.** `git grep -n
> "FR-250\|FR-257" docs/findings/register.md` at `3edd75a` returns exactly one line, and
> it is F-W9-2's prose about FR-224 — *"specialises FR-257's general approval-evidence
> gate, which WK-671 builds"* — a mention of the requirement inside another row, not a deferral
> of it. Neither id has a row of its own. **Two rows are owed at WK-671's close, and DP1 and DP2
> having since been ruled does not write them**: a ruling settles what the code does, a
> register row records what the workstream did not deliver, and those are different artifacts.
> **Owner: WK-671's close** — an owner this acceptance can name without a roadmap edit, because
> the review already named when the obligation falls due rather than who would carry it.

#### Proposals, consolidated — review 8

| # | Proposal | Kind |
|---|---|---|
| 3.1 | A short ZEN-evaluate-side concurrency spike, run at WK-671 evaluator-slice start | research |
| 4.1 | WK-671's roadmap row corrected for FR-252 | docs — **landed, PR #314** |
| 4.2 | Workstream rows cite the spec section as the row of record, range as gloss only | tool or convention |
| 4.3 | NFR-501 gains a dated amendment reconciling the 1.09 ms / 1.626 ms figures | spec — **landed, PR #314** |
| 4.4 | A distinct mechanism (a measured figure copied into free prose, not mirrored) — extend the OQ-mirror pattern (`audit-docs` checks 4 and 23) to it, or make a `docs/`-wide grep a standing correction step (executor's finding, credited) | tool or convention |
| 5.1 | **No re-cut** of Phase 2's WK-671-W14 boundaries; FR-250/257 get named deferrals inside WK-671's own plan | plan — no change |

**Maintainer acceptance: accepted as proposed, 2026-08-29.** All six rows bind from that date,
recorded per row with the owner review 4's question-5 rule now requires:

- **3.1 — accepted, and discharged** by `docs/research/zen-evaluate-concurrency.md` (PR #321).
  **Owner: discharged**, with RL-868's `model_call` follow-up expressly not covered.
- **4.1 — accepted, and already landed** (PR #314). **Owner: discharged.**
- **4.2 — accepted. Unowned**, and the mechanism has fired a third time on FR-243; see the
  per-item line above. Where the check lives is not decided by this acceptance.
- **4.3 — accepted, and already landed** (PR #314). **Owner: discharged.**
- **4.4 — accepted. Unowned**, and it is a disjunction: either limb discharges it, and this
  line picks neither. The worked instance inside `audit-docs.py` is separately resolved.
- **5.1 — accepted: no re-cut.** **Owner: WK-671's close**, which owes FR-250 and FR-257 a
  named dated register deferral each. **Binding from today and unmet today** — see the per-item
  line above for the verification.

**What is still owed, enumerated rather than counted** — because the first draft of this
sentence carried a tally and got it wrong, which is the defect questions 4 and 5 of this very
review are about. **Open: 4.2** (unowned, and now fired a third time), **4.4** (unowned, limb
unchosen), and **5.1's condition** (two register rows at WK-671's close). **Not open: 3.1**
discharged by the spike, **4.1** and **4.3** landed in PR #314 before this date. What this
acceptance mostly does is make the record say what the repository already did; a reader looking
for what is still owed should read the three named above and derive no total from them.

#### Sources — reviews 7 and 8

- `docs/closures/CR-00838-work-item-record-wk-669-the-rating-contract-validation-and-bundle-compilation.md`, `docs/closures/CR-00834-work-item-record-wk-670-rate-tables.md` — closure records, reused
  per the skill's own guidance rather than re-derived.
- `docs/specs/03-rating-engine.md` §3.1-§3.11, §4.3, §5.1 — read directly at `07ae047`;
  NFR-501's amendment confirmed at `d4bc394` after rebasing.
- `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`, `WF-701-deploy-and-monitor.md` — read
  directly.
- `docs/roadmap.md` §7 (workstream table, risk table) — read directly, plus a full-file grep
  for FR-223/224/218.
- `docs/findings/register.md` — rows F-W9-1, F-W10-2, F-W10-2-1, F-W10-2-2, F-W10-3.
- `scope-audit.py RATE` / `--endpoints`, run this session at `main@74b1b10`.
- Codebase, read directly: `backend/src/app/platform/rating_versions.py`,
  `backend/src/app/config.py`, `packages/model-schema/src/model_schema/approvals.py`,
  `packages/pricing-core/src/pricing_core/rating/compile.py`.

---
