---
id: CR-925
family: closure
kind: review
title: Plan review 9 — at WK-671's close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-30
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 9 — at WK-671's close, 2026-08-30 — **FILED, with its drafting history intact**

> **Status header, added on filing 2026-08-30.** This review was drafted against `origin/main`
> at `19eaabc` **while WK-671's close was in doubt** — the maintainer had stopped the run at the
> end of Slice 2, and for several hours no close was going to happen. The planner's own verdict
> at that point was *abandon, do not land it*, on the sound ground that filing a §14 review of a
> workstream that never closed would misstate the record.
>
> **WK-671 then closed**, at `1da81cd`, under a delegation from the maintainer to the lead. That
> voids the reason for abandoning it, so it is filed rather than discarded.
>
> **Two things a reader must hold, and they are not the same.** The **operative** §14 review for
> WK-671's close is the closure record's §7 (`docs/closures/CR-00927-work-item-record-wk-671-scoring.md`) — short, and written
> against the closed state. **This is the fuller working analysis**, kept for its evidence and
> its derivations, several of which the closure record cites rather than repeats.
>
> **Its forward-looking statements are superseded by the close.** Where it says Slices 2–4 have
> not landed, or that a tally cannot yet be final: Slice 2 landed in full, Slices 3 and 4 never
> ran, and the final verdicts are in the closure record. Nothing here is edited to hide that —
> a review is a dated artifact, and rewriting its predictions after the fact destroys the record
> of what was believed when the plan was being tested, which is the whole point of §14.

`CLAUDE.md` §14's ninth run, triggered by WK-671's close (`docs/roadmap.md` §7). **This section is
not the filed review.** Slice 1 is complete (`c1a0dde`, all five tasks merged), but Slices 2–4 are
not: Slice 2 Task 2A is delivered as PR #435 with a second PR (#436, register row `F41`) open
behind it, both gate-in-flight as of this draft's base tree, and Slices 3–4 have plans but no code.
The §13 closure audit this review would normally reuse for question 1 has not itself finished.
Written now, at the lead's request, so it can be reviewed and extended as the remaining slices land
rather than started from nothing once they do. **Nothing below binds anything** until a maintainer
acceptance line is dated (§14's own rule); the status table after question 5 says which findings
are already stable and which need reconfirming.

**Base tree:** `origin/main` at `19eaabc` (this branch's parent, confirmed identical to
`origin/main` at the time of writing). Every citation below is to a file at that tree, a commit
reachable from it, or a reproducible command — not to the session-local working notes that first
surfaced several of these findings (`~/w11-handover-2026-08-29/*.md`), which will not outlive this
session (handover directories are not repository artifacts here). Where one of those notes first
found something, it is credited by name in prose; the finding itself is restated with its own
durable citation so this review does not depend on a path a future reader cannot open.

One correction made while drafting, recorded beside the finding rather than instead of it, per this
skill's own guidance for when a review's inputs turn out wrong: the evidence handed to this draft
reported a finding as **"Registered F42."** Verified directly against `docs/findings/register.md` at
`19eaabc`: no F42 exists. The finding itself (`req-coverage.py`'s occurrence-count mislabel, at a
large-fraction scale still being re-measured — this draft deliberately does not quote the exact
count, since it moved once already between two of this evidence base's own passes and is not
load-bearing to anything below) was **withdrawn before filing** because it duplicates `F36`
(`register.md:42`) and will amend that row instead of opening a new one — not yet landed as of this
tree. Question 3 below cites `F36` as it stands today, not the amendment.

**Re-read after the evidence base itself changed mid-draft**, per the lead's note. Two changes:
a new §I (a leaf-plan Files-block gap, verified at `7952f76`, taken up under question 3 below), and
a correction to §F's own headline figure ("sixteen requirements, all on the NFR side" corrected to
"ten NFRs and six FRs"). The second one is not simply adopted — question 1 below re-derives it
directly against the row and the leaf plans, because the corrected figure and this draft's own
independent first pass disagreed with each other in a way neither fully explained, and both turn
out right for differently-scoped questions rather than one being simply wrong.

---

**1. Completion — reused where a fresh derivation exists, and provisional as a whole.**

Two independent, same-night derivations exist, and this review reuses rather than re-runs them:
`scope-audit.py RATE --sections 3.7,3.8 --extra 'FR-252,NFR-489,NFR-502,NFR-501'`
(pinned `6e548f8`), and a full read of `03` §3.7, §3.8 and §9 against every WK-671 leaf plan's own
coverage table (pinned `28ec778`). Both recorded the exact commands that produced them; re-running
now would confirm, not discover.

The row (`docs/roadmap.md:376`) names **13 ids**: `FR-RATE-34..42, 64` and `NFR-RATE-1, 13, 14`.
The section sweep returns 16 in scope, over-including three WK-672 ids (`FR-260/261/262`, confirmed
excluded by name in every WK-671 leaf plan) — net of that, section and row agree at 13.

**Beyond that 13, two different questions each have a correct, different-sized answer — kept
separate here because this draft's own first pass, and the evidence base it drew on, both
collapsed them into one number and disagreed with each other as a result (`phase-review-inputs.md`
§F was itself corrected mid-session, from "sixteen, all NFR" to "ten NFRs and six FRs," while this
draft's own first pass had independently reached fourteen — neither of those two prior numbers was
wrong so much as each answered a different question without saying so).**

**Question A — what does a WK-671 leaf plan claim that the row's text never says?** **Sixteen ids**,
matching the evidence base's corrected figure exactly: `FR-RATE-22, 24, 25, 56, 63, 65` (six —
each with markers in a WK-671 leaf plan's own Requirement Coverage table, enumerated per-id in the
scope-derivation pass) and `NFR-RATE-2, 3, 4, 5, 7, 8, 9, 11, 12` plus `NFR-459` (ten), none of
which appear inside the row's `FR-RATE-34..42, 64`.

**Question B — what is claimed by no row anywhere in `docs/roadmap.md`, full stop?** A narrower
**fourteen, enumerated rather than left as arithmetic** (the arithmetic below is shown once, as
the derivation, not as a substitute for the list — restating only "sixteen minus four plus two"
is exactly the kind of bare count Candidate B warns against, and was not enough for this figure
to be checked without a second round-trip):

> `FR-218, FR-243` (two) · `NFR-RATE-2, 3, 4, 5, 7, 8, 9, 10, 11, 12` (ten) ·
> `NFR-458, NFR-459` (two). **2 + 10 + 2 = 14.**

That is Question A's sixteen, minus four `FR-` ids *also* named by **WK-669's** row
(`docs/roadmap.md:374`, `FR-RATE-1..13, 22..27, 56/57/58/59`) through a bare-number continuation a
per-id search does not match, plus two ids (`NFR-498`, `NFR-458`) that sit **outside**
Question A entirely, because no WK-671 plan claims them either — a worse gap than the other twelve's
"claimed by a plan, absent from the row," and the reason the addition is not optional:

- `FR-RATE-22, 24, 56` are WK-669's, and WK-671's own tests re-exercise rather than newly discharge them
  — except `FR-273` is a deeper case than the other two: per independent corroboration, WK-671
  Task 1.4's test is *"the first proving the check is wired into the running service,"* i.e. real
  completion work on a requirement WK-669 had booked on weaker evidence. That is exactly why Question
  A, not Question B, is the one that should decide whether WK-671's own row mentions it — the row
  can be silent about *owning* `FR-273` while still being wrong to hide that WK-671's own plan
  did something to it.
- `FR-240` is also WK-669's by the same continuation, and **already tracked in full** as `F-W9-3`
  (`register.md:25`) — not a new finding under either question.
- `FR-218` (`03:87`, §3.1) and `FR-243` (`03:139`, §3.4) are claimed by **no** row at all.
  `FR-243` is already ruled WK-671's (RL-861,
  `docs/rulings/RL-00861-wk-671-s-and-it-is-forced-rather-than-chosen.md:33-47`, 2026-08-29; the mechanical row edit
  is outstanding, see question 5). `FR-218` is not yet ruled by anyone — see question 2.
- `NFR-498` and `NFR-458` are the two ids named above that sit outside Question A entirely
  (see question 2 for both).

**Both totals are correct, for the question each answers, and neither replaces the other** — the
practice this review's own Candidate B recommends below (a count states the granularity it was
taken at), applied to its own headline number rather than only proposed for someone else's.

**Since the pinned derivation (`28ec778`), Slice 1 Task 1.5 has merged (`c1a0dde`)**, converting
three of the above from a leaf plan's stated intent into register rows: `NFR-490`'s correctness
limb tested-but-mismarked and latency limb measured failing (`F35`, `register.md:41`),
`NFR-489`'s without-GBM half not established across five runs (`F38`, `register.md:44`),
`NFR-500`'s missing storage format (`F37`, `register.md:43`). Slice 1 is complete in the sense
this review can check today, not merely planned complete.

**What this question cannot yet answer:** a final tally for the close, because Slices 2–4 have not
landed and the §13 closure audit that owns the final verdict-per-id has not run. `FR-254`
(three limbs) and `NFR-497` (`F41`, PR #436, open) are named only to flag that this review has
deliberately not analysed them — both depend on Slice 2 outcomes not yet on `main`.

**Two PRs are moving under this review as it is written.** PR #435 (Slice 2 Task 2A) and PR #436
(`F41`, `NFR-497`) are both open at this base SHA, gate reported in flight. If either merges
before this draft is finalised, the list above should be re-checked against the new tree before
filing — deliberately not re-checked here, rather than guess at an outcome not yet on `main`.

**2. Omission — beyond the row-naming gap already covered under question 1.**

- **`NFR-498`** (`03` §9: audit events on "algorithm edits, rate table versions, bulk
  operations, **compilations**, approvals, deployments, rollbacks, and routing changes") is engaged
  by name — WK-671 Task 1.2 built the `RATING_COMPILE` Job — and built without the audit event:
  `backend/src/app/worker/rating_handlers.py`'s `_rating_compile` calls `compile_rating_version`
  then `blob_store.put`, no `audit.record`; every other rating platform module returns zero calls
  to it, against a positive control of 20 `platform/*` modules that do call it
  (`app/platform/audit.py:52`). Named in no plan, ruling or register row before this evidence pass.
  This is a real gap, not a deferred-and-tracked one, and needs one of the four verdicts at the
  close — which this review does not give; §13's verdicts are the lead's (`CLAUDE.md` §12).
- **`NFR-458`**, as under question 1: recorded inside `F22`'s range, owner-clause resolving to
  nothing. Distinct from `NFR-498` — `F22` carries no `RATE` ids at all (`register.md:13`), so
  the two are separate gaps that happen to share a shape.
- **`FR-218`**, as under question 1: evidenced, unclaimed, and — unlike `FR-243` — not yet
  put in front of anyone to rule. Recommend the same treatment RL-861 gave `FR-243` (a
  short, dated attribution ruling) before the close; this review does not make that call itself.
- **No new instance of `WF-698…05` evidenced by nothing** (review 2's finding): `WF-699` and `WF-701`
  are both cited by name in WK-671 rulings and register rows this pass touched. Not re-checked
  exhaustively; flagged "no change" per this skill's own rule that a silent question cannot be
  told apart from one nobody asked.
- **The gate-coverage cluster** (`F27(c)` + `F29` + `F33`) and `F-W9-3`'s clauses (4), (5), (6) are
  a different kind of omission — not undiscovered, but pre-designated by RL-860
  (`docs/rulings/RL-00860-owners-for-the-seven-unowned-register-findings-and-one-new-row.md:16-85`) to be decided **at this review**,
  and still undecided. See the decision point after question 5.
- **Two fresh defects on `F-W9-3`'s own row, found by the same kind of limb-level audit that
  produced it — verified directly, both concrete claims.** `docs/closures/CR-00838-work-item-record-wk-669-the-rating-contract-validation-and-bundle-compilation.md:27`
  verdicts `FR-237, FR-238, FR-239, FR-240, FR-241, FR-242` "delivered" as one row on a bare marker count (22: 3, 23: 1, 24: 4,
  25: 1, 26: 1, 27: 1); opening the tests shows three of those six markers are the *same* test
  (`packages/model-schema/tests/test_rating_version.py:44-47` stacks `@pytest.mark.req` for
  `FR-237`, `26`, `27` on one pydantic parse-and-round-trip, `test_the_full_43_contract_parses`).
  A limb-level decomposition of four of the six (22, 23, 24, 26) found 21 limbs, 7 enforced and
  14 with nothing enforcing them (2/6, 1/4, 3/5, 1/6 respectively) — **not evenly bad**:
  `FR-239`'s three of five limbs (self-containment, content hash, zero-DB-access with a
  positive control) are solidly built and tested, and only its caching/distribution tail is weak
  and already known to be. Two limbs are new, unregistered gaps: **`FR-237`'s
  pins-completeness gap** — `compile.py:431-434` refuses only total absence of `algorithm_ref` or
  `pins`, verified directly, with nothing cross-checking that `pins.rate_tables` covers every
  table the algorithm's own steps reference, so a partial under-pin compiles clean and surfaces
  later as a missing key at hydration rather than a named refusal — and **`FR-241` is
  near-totally unenforced**: `rating.py:131` declares `effective_from: datetime | None = None`
  (verified directly) and no path to `approved` requires it be set. **Same treatment as `F27(c)`
  and `F-W9-3` above, and for the identical reason**: this is a missing check against what a
  closed workstream declared delivered, not a defect in what WK-669 built — reopening WK-669's close is
  the maintainer's alone (`CLAUDE.md` §13) — and these two need a verdict this review does not
  give.

**3. Skills and research — one shape, seven instances, reframed by an eighth.**

- **`delivery-process.md` §8's gate-in-flight control** ("announce an expensive verification…and
  check for one already in flight before starting," `delivery-process.md:170-172`) has no live
  mechanism carrying its announce half: `watcher.md:11-24`'s roster-state publication was meant to
  be the visible, shared state the rule itself says coordination needs ("coordination state must be
  visible, not relayed pairwise," `delivery-process.md:173`), and the one script that attempted it
  was a heredoc emitting a constant with a live timestamp, now withdrawn (`F31`, `register.md:37`).
  Three real contention incidents resulted, one producing a spurious `403 UNAUTHENTICATED` against
  the shared Postgres that did not reproduce on a quiet re-run. The compensating manual check
  (`pgrep -af 'bin/pytest'`) could not return a negative — it matches its own invocation string —
  and was not a discipline failure so much as a check broken from the moment it was written and
  never run against a quiet box to notice. The corrected form
  (`ps -eo pid,args | grep -E '[b]in/pytest'`) is known; **no mechanical replacement for the
  announce half has been built.**
- **The 50-word message rule** (`delivery-process.md:310-314`, landed 2026-08-29) was breached
  **four times, after a remedy for it had been formally adopted** — not merely observed as broken
  once. That is a sharper claim than "the rule was breached": adopting a remedy is not the same as
  the remedy holding, which bears directly on how much confidence this section's own
  "adopt a mechanical check" recommendations should carry if any of them stop short of mechanical.
  Nothing checked it at the point of sending, before or after adoption; each breach was caught by a
  different teammate reading the message, never by the author and never by a check.
- **The §14 trigger itself** has fired on time for none of the three workstream closes it has been
  due at: WK-669 and WK-670 were both reviewed retroactively, together, after the fact (reviews 7 and 8,
  both filed 2026-08-29 for closes on 2026-08-27 and 2026-08-28); this review, for WK-671, exists only
  because the lead explicitly tasked it, not because anything noticed the close and asked for it.
- **A fifth instance, and it is the sharpest one, because it is the fix for the other four.**
  `close-workstream` §5a (`.claude/skills/close-workstream/SKILL.md:340-368`) was written hours
  before this draft, by the same person who had just diagnosed this whole shape, to catch exactly
  it — a binding plan-review condition (review 8's 5.1, the `FR-250`/`FR-257` register
  rows discussed under question 5) whose demanded artifact nobody was checking for. §5a is
  **prose plus a suggested `grep`**: nothing in `audit-docs.py` verifies that an accepted
  condition's artifact actually exists. The remedy for "a rule with no check" was itself a rule
  with no check. Not worthless — a checklist step inside a procedure read start-to-finish is
  stronger than a rule floating loose in a process document — but the weaker of the two available
  instruments, chosen without the stronger one being ruled out.
- **A sixth instance, self-reported, and the strongest of the six because it controls for
  knowledge and motivation, which the other five do not.** In one night, and immediately after
  diagnosing this exact class, the lead broke three rules it had itself just written down: the
  50-word message rule (above — by then already a case of a formally adopted remedy breached
  anyway); the elided-prefix continuation trap
  (`w11-scope-derivation.md`'s own "Method notes" — "before reporting any id as absent, search the
  range and slash forms," which is precisely what a first pass over `FR-237/239/240/273` skipped);
  and the rule that a bare count is not load-bearing (Candidate B, question 5 — restating "sixteen"
  and then "ten NFRs and six FRs" without the enumerated list underneath either figure, corrected
  above under question 1). Each was caught by a different teammate reading the artifact, none by a
  check. Where the other five instances leave room to read the gap as an execution shortfall, this
  one does not: the person with the most reason to comply, right after writing the rule down, still
  needed a second reader to catch it.
- **A seventh instance, and a different failure inside the same family: a control that was
  adopted and followed, aimed at the wrong property.** §8's own justification for serialising gate
  runs is CPU/load contention — "two suites at once drove load average past 11 and both read as
  stalled agents" (`delivery-process.md:166`). But `backend/tests/conftest_db.py`'s
  `_empty_the_database_after_the_session` fixture (`scope="session", autouse=True`,
  `conftest_db.py:251-252`) truncates the whole shared Postgres at teardown **regardless of
  load** — so two pytest sessions running at the same time against it can mutually destroy each
  other's fixtures with zero CPU contention at all. Following §8's own stated reasoning (avoid
  contending for CPU) does not by itself prevent this, because the hazard the rule argues from and
  the hazard that actually bites are different properties — compliance and safety came apart, not
  because anyone was careless but because the rule's own justification pointed at the wrong thing.
  **This was not a fresh discovery — it was already documented**, `.claude/skills/python-test/
  SKILL.md:284-319`, "That teardown makes two concurrent runs mutually destructive," measured
  2026-08-24 across three overlapping runs, six days before this workstream re-hit it. The skill
  gives two remedies, and the first shares this section's own instance 2's defect: *"Serialise…
  `pgrep -af 'pytest'` before starting"* is the identical self-matching check, so retrieving this
  documented remedy would not by itself have helped. The second — **"give each session its own
  database"** (`test_database_url()` already reads `GIP_TEST_DATABASE_URL` before falling back to
  a shared default, `conftest_db.py:35,39`; `createdb gipricing_$USER_$SLOT` and point at that) —
  sidesteps the coordination problem entirely rather than requiring a working check.
  **Recommendation 3.1 is therefore not to build anything**: adopt the already-documented,
  already-scoped per-session-database remedy the skill names, rather than design a new lock file
  against a hazard whose fix already exists and does not need one.
- **These are one shape, not six unrelated notes**: a rule stated in prose with nothing making
  compliance visible at the moment of the action it governs, or (this section's seventh instance)
  visible but aimed at a proxy for the real hazard rather than the hazard itself.
  **Recommendation (3.2), no design proposed here:** either
  the §14 trigger, the 50-word rule and §5a's condition-artifact check get an equivalent mechanical
  check, or the maintainer accepts that all three remain enforced only by memory and says so rather
  than leaving the gap implicit.
- **An eighth item that is not an eighth instance — it reframes the seven above, and the lead
  called it the strongest input of the night.** Raised by the decision-maker, of its own work:
  *"Every ruling that improved on its own first draft did so by finding something already in the
  repository… The failure mode wasn't insufficient thinking; it was answering before reading the
  artifact that already had the answer."* Three of its eight tabled instances are independently
  verifiable from this document alone: the `F42`/`F36` duplicate this draft's own opening already
  corrects; the elided-prefix trap this draft's question 1 re-derived, which (per the
  decision-maker's finding) the lead had already written down on 2026-08-25 before repeating it on
  `roadmap.md:374` five days later; and this section's own seventh instance, whose remedy —
  per-session databases — was sitting in `python-test/SKILL.md` the whole time. **The claim that
  matters is sharper than §A's**: §A says rules exist and nothing enforces them, which argues for
  building enforcement. This says the *answer* already existed, indexed and searchable, for every
  instance checked — so a new control would not have helped where a `git grep` before writing
  would have. **The proposal explicitly warns against the obvious response**: "read more before
  writing" is §A-shaped and fails the same way, because a general intention is exactly what these
  instances show does not survive the moment of writing. What worked instead, every time (per the
  same finding), was **one grep command attached to a specific act** — before allocating a finding
  id, before writing a literal into a spec, before filing a defect as new. **Recommendation
  (3.5):** wherever this review has proposed a mechanical check above (3.1's per-session database
  aside, since that removes the need to check anything), consider whether a one-command grep tied
  to the specific writing act would catch more of this class more cheaply than a general
  enforcement mechanism — this review flags the question rather than answering it for each case.
  **One caution carried forward rather than dropped**: every instance in this class was caught, by
  a second person reading the artifact — so the table is a *lower bound*, and says nothing about
  how many were not caught.
- **A measurement-methodology gap, distinct from the process-control shape above.** `F38`
  (`register.md:44`, `NFR-489`'s without-GBM half) shows a single quiet run can pass while five
  runs under varied load reveal the true verdict is *not established* (two of five breach a 15 ms
  bound) — and shows why printing that one run's own distribution would not have caught it: a
  single run's spread is necessarily narrow near its own mean, so the criterion as written was
  satisfiable by exactly the run that got the verdict wrong. **Recommendation (3.3):** an NFR
  acceptance criterion measured near its bound should require repetition under varied load, not a
  reported distribution from one run — the leaf plan asked for the distribution and got exactly
  that, correctly, and it was not enough. This is a convention gap (a testing or `dev-commands`
  skill, or the leaf-plan-writing convention itself), not a spec gap; this review does not pick
  which document carries it.
- **A distinct measurement-practice gap: five instances tonight of a figure labelled with a tree
  it was not taken on** — self-named by the batch executor after producing one, having caught two
  others earlier the same session; three of the five are the lead's own, by the lead's own count.
  One is this draft's own opening correction above (the withdrawn-finding's scale, first quoted
  from a figure re-measured on a moving tree, now stated without the number rather than repeated).
  **Why this earns its own entry rather than folding into question 4's citation-error discussion**:
  every instance is *correctly formatted* by `CLAUDE.md` §13's own standard — each names a tree, a
  PR state, or a file, which is exactly what makes a citation survive review on a first read.
  **Naming a tree is not the same as having measured on it**, and nothing in the current standard
  distinguishes the two: a figure taken on a working tree and labelled with the branch's base SHA,
  a `gh` read reported as current after a push landed behind it, a gate's own stale result file
  from three hours earlier read as the current run's — caught only by an `mtime` check. **The
  fifth is the sharpest of the five because no reasoning error was involved at all**: correct
  extraction, correct arithmetic, wrong source file. **Recommendation (3.6), mechanical rather
  than a discipline reminder:** a figure quoted in a durable artifact is produced by a command that
  prints its own tree in the same invocation — `git rev-parse HEAD` beside the number, so the
  label cannot drift from the measurement because both come from one run; a file read as evidence
  is quoted with its `mtime` beside it. Both are one flag each, and both fail loudly rather than
  silently — the same "true by construction" standard 3.1's per-session-database fix meets, applied
  to citation rather than coordination.
- **A related but distinct pattern: a bounded query answers a narrower question than the one
  asked, and the answer looks complete.** Self-reported, four instances tonight: an ANSI-blind
  `grep FAILED` that missed escape-coded output, a grep for a phrase that had wrapped across a
  line break, a `head -5` that silently dropped the remainder, and a stability check against a
  guessed cutoff. **One shape, not four lessons** — each query was answered correctly for the
  literal scope it encoded, and each answer was then read as though it covered the broader
  question actually being asked. Distinct from this section's tree-mislabelling class (that names
  a real tree wrongly; this runs a real command too narrowly) and from §J's retrieval failures
  (nothing here was already known and skipped — each query was novel, just under-scoped).
  **Recommendation (3.9):** unlike 3.6, no single mechanical fix generalises across `grep`, `head`
  and a statistical cutoff the same way — this review names the shape and leaves whoever owns
  `dev-commands` or a testing skill to decide whether a query's own scope stated beside its result
  is worth a checklist item, or whether review density (§D's own finding about what that already
  buys) is the cheaper answer here.
- **Two smaller items, self-reported, each with its own remedy already applied.** A correction
  that states a new position without naming what it supersedes leaves both readings live until
  someone checks — three incidents tonight, one of which would have reverted work the executor had
  already correctly completed under the position being silently replaced; carried into Q5's
  Candidates A/B discussion below as a third, unnumbered candidate for the same rule set. And a
  3h22m stall from relying on notifications rather than a standing 15-minute check the lead's own
  rule already requires — self-diagnosed, and a background watcher is now armed rather than relied
  on to be remembered, which is this section's own recurring fix applied to itself.
- **A leaf-plan convention gap, found by the process working rather than failing.** Every WK-671
  route-adding leaf plan (Task 2B's `w11-2`; Slice 3's `w11-3-batch-scoring`; Slice 4's
  `w11-4-trace-sampling-persistence`) omits the regenerated OpenAPI contract
  (`docs/contracts/openapi/generated.json`) from its own **Files** block, despite adding a route
  that forces its regeneration (`scripts/generate-contracts.py:163`, `FR-451`) — verified
  directly: `docs/plans/PL-00847-wk-671-slice-2-the-real-time-scoring-endpoint-its-bundle-slot-and-the-nfrs-that-need-the-http-path.md` has four `**Files**`
  headings and none names it. Two of the three plans do name `generate-contracts.py --check`
  inside a boilerplate gate-block, which is worse than silence in one respect — it reads as
  coverage while naming the detector, not the deliverable. The knock-on a plan reader would not
  predict: `frontend.yml`'s path filter includes `docs/contracts/openapi/**`
  (`.github/workflows/frontend.yml:21,29`, confirmed), so a route-adding backend PR arms a
  **second** CI workflow, and a red frontend job on it is a real failure, not a stray. Caught by
  the executor surveying integration points *before* writing any code (`delivery-process.md` §6's
  own ordering) — an instance of the process paying for itself, not the reverse.
  **Recommendation (3.4):** a plan step that adds or changes a route states the regenerated
  contract as a deliverable in its own Files block, and names the second CI workflow it arms —
  `writing-plans` is this charter's own mandatory skill and the natural home for the convention,
  but this review proposes rather than lands it, consistent with how it has treated every other
  skill-amendment finding above.
- **A frozen leaf plan's line-number citations go stale under any insertion above them — and the
  repository already has the rule that would have prevented it, unfired.** Three forms of the same
  locator behave differently under edit: a **symbol** (`approvals.submit` inside
  `submit_for_review`) stays stable under any edit that does not rename it; a **line stated with
  its tree** (`:178` at `e16c459`) ages into a historical statement that still resolves, forever,
  with no maintenance; a **bare line** (`:178`, no tree) rots silently on the next edit above it and
  gives no signal when it does.

  **A controlled comparison, not an argument, settles which form to prefer.** The same fact was
  cited twice, hours apart. `docs/findings/register.md`'s `F44` row (confirmed directly at
  `origin/main`) writes: "at `e16c459`… `rating_versions.submit_for_review` (`:153`) calls
  `approvals.submit` at `:178`" — the tree is stated once and covers both numbers. The lead's own
  dispatch cited the same call as a bare `:178`, no tree. Verified directly, both sides: at
  `e16c459` the citation is exactly right; at `origin/main`'s current tip, `submit_for_review` is
  now at `:214` and the call to `approvals.submit(` at `:239` — a real 61-line shift from Task 2B's
  merge, landing between the two citations being written. F44's form still resolves correctly,
  unmaintained, because it never claimed to describe an undated present; the bare form now points
  at whatever else occupies `:178` today, silently.

  **The rule that would have caught this already exists.** `CLAUDE.md` §13: "a reference carries
  its scope and its measurement… a `Verified` date carries the tree"
  ([RFC-777](../rfcs/RFC-00777-a-reference-that-resolves-only-in-the-writer-s-context.md)). The
  auditor's F44 row followed it; the lead's dispatch did not, and the lead is the one who cites §13
  at other people. **Three instances tonight of an existing rule failing to fire on someone who
  already knew it**: this locator (§13's own scope rule, against its own author); the 3h22m
  notification stall two bullets above (the lead's own standing 15-minute check, not run); and the
  reporter's charter, which — independently, and now confirmed landed at `origin/main`
  (`.claude/roles/reporter.md`, "The Slack post: facts only, never inference") — went from silent
  on inference to an explicit two-sided rule: a named whitelist of permitted sources paired with
  the concrete violating lines as examples, which this review's own 4.6 below independently
  proposed and can now mark discharged rather than pending. **The recommendation this supports is
  not "add a rule."** All three rules already existed. It is that **a rule which can only be
  honoured by remembering fails precisely when the person invoking it is busy and confident — which
  is when it matters** — and the reporter's own fix is the model: it did not add a reminder, it
  changed the artifact from silent to enforcing, so the next reader inherits a structure rather
  than an absence.

  **Recommendation (3.10):** a frozen leaf plan (and, by the same rule, a dispatch or a register
  row) cites a locator as **symbol, or line stated with its tree** — never a bare line number — so
  the citation either survives the edit that would break it or names the point at which it stopped
  being current. A sweep across frozen leaf plans found **4 wrong across 88** such citations under
  the bare form. Squarely a `writing-plans` convention, proposed rather than landed, per this
  review's standing practice above. **Credit:** the auditor designed the F44-vs-dispatch comparison
  that settles the form; this review generalises it.

  **A related class, three instances tonight, only this one developed elsewhere in the review**:
  the locator above; a re-plan the lead performed around a quota constraint without first testing
  whether the constraint was removable (a rerun request — which a quota-exhausted repository
  refuses outright — resolved it in ten minutes, run last rather than first, after inverting §8
  for two agents and escalating a 40-minute infrastructure question to the maintainer); and an
  executor's own storage-bucket reasoning error, self-reported as the same shape. **The class, not
  any one instance, is what is worth naming**: an argument or inference stood in for a cheap,
  direct test that was available the whole time. This review does not attempt one mechanical fix
  for a class this varied — a locator, an infrastructure assumption and a storage error share no
  single instrument — and names the shape once so a future instance is recognised faster than
  these three were.
- **No change** on review 8's ZEN-evaluate-side research recommendation (its 3.1) — discharged,
  with its own named follow-up (the `model_call` node re-test) not yet due.
- **`CLAUDE.md` §13's four verdicts have no slot for what `NFR-490` actually produced: adverse
  evidence, not absent evidence.** All four verdicts ("delivered but untested," "deferred with an
  owner," "reassigned," "not started") presuppose a gap in evidence; `NFR-490` was measured
  properly and found failing, and "deferred with an owner" is the closest fit only by discarding
  the number, which is the most valuable thing Task 1.5 produced. Two further mismatches:
  a workstream can fully discharge its *own* scope (WK-671 committed to *measure* `NFR-490`, not
  meet it) while the requirement's own state is "failing" — both true at once, which §13 has no
  way to say without conflating them — and `NFR-490` itself needs two verdicts, one per limb
  (`FR-254` needs three), where §13 assumes one verdict per id. **Not an isolated case**:
  `NFR-489`'s without-GBM limb (`F38`) is in the identical state — measured, unstable, not
  established — and `FR-240`'s control-intent clause (`F-W9-3` above) is a fourth shape again:
  marked with a real test, and enforced nowhere the marker claims. Three WK-671-touched rows need a
  verdict this standard has no slot for, not one. **The perverse incentive this leaves in place**:
  an NFR nobody measures books cleanly as "delivered but untested," and an NFR someone measures and
  finds failing has no clean verdict at all — the standard rewards not looking.
  **Recommendation (3.7), not drafted here**: `CLAUDE.md` §13 needs a fifth verdict (or a
  qualifier on the existing four) for measured-and-failing, and an explicit rule for how many
  verdicts a multi-limb requirement takes. This is a `CLAUDE.md` §13 amendment — the maintainer's
  alone (`CLAUDE.md` §12) — and this review surfaces it rather than proposing wording.
- **The one constructive recommendation in this workstream's evidence: prefer the design whose
  safety property has a failing case.** This did not arrive by generalising it across everything
  above — that generalisation was tried and withdrawn as asserted rather than enumerated, twice,
  before this draft could adopt it. **Checked directly against this section's own bullets rather
  than carried from that count, and the corpus is stated because a count without one is the same
  defect a third time**: **two, within this section's own bullets** — not a claim about this
  document as a whole or about the wider evidence base — qualify as "a check that exists and is
  structurally incapable of reporting the failure it is asked about," as opposed to being merely
  related to that shape: the `pgrep` self-match (instance 2, duplicated verbatim inside instance
  7's "serialise" remedy, so one defect with two sightings rather than two instances) and the
  authorisation example below. **The rest of this section is a different, adjacent shape each
  time, worth telling apart rather than folding in**: the announce half, the §14 trigger and
  §5a's suggested `grep` are *absent* checks, not defective ones — there is no mechanism to be
  structurally blind, only none built yet. §8's CPU justification for the database-truncation
  hazard *measures correctly at the wrong target*, which is a different defect from measuring
  nothing. §J's table is explicitly, in its own words, a *retrieval* failure and "something
  cheaper and more damning" than "nothing enforces this," not a restatement of it. The
  tree-mislabelling class is a *provenance* defect on an otherwise correctly computed number.
  **Two named candidates sit outside that stated corpus, checked by neither this count nor its
  predecessor, and are left there rather than folded in without the same rigor**: `F31`'s roster
  freshness indicator (cited above under instance 1, but not previously examined from this
  angle) and RL-863's finding that sampling would hide `NFR-489`/`2`'s violation below the
  metric's own resolution. Both are already tied, by their own source documents, to
  [`RFC-789`](../rfcs/RFC-00789-zero-calls-above-200k-tokens-measures-the-compaction-cap-not-discipline.md)'s "a boundary metric
  reads zero by construction" — plausible third and fourth instances of this section's narrow
  shape, or possibly a related-but-distinct family of their own; this review does not decide
  which, only declines to count them before checking either with the care the six above got.
  **The proposal stands on the two instances it has been checked against**, arrived at from a live
  choice between two implementations of the same authorisation repair — re-derive a `Caller`'s
  permissions from its account row, or pass the authenticated set as a parameter. They
  behave identically today (`backend/src/app/auth/service.py:230` populates identity permissions
  straight from the account row — verified directly), so the choice looked cosmetic. **It is not**:
  a re-derived implementation cannot be made to fail the test that would separate them (*"a
  `Caller` whose permissions differ from its account row must be enforced on the `Caller`'s"*) —
  it has no way to disagree with the row it derives from. Its defining flaw is not being wrong
  today; it is that nothing could ever tell you when it became wrong. **Why this belongs in a plan
  review rather than only in the ruling it came from**: it lifts `CLAUDE.md` §13's existing
  enforcement standard — "proven on deliberately broken input" — from *checking a check* to
  *choosing a design*, which is a standing decision-making criterion, not a one-off fix. It also
  retires a weaker remedy this evidence base tried first: a prose tripwire proposed for this exact
  hazard, withdrawn once the acceptance test above was shown to do the same work mechanically —
  the general lesson being that "document the danger" should first be tested against "can the
  danger be given a failing case instead." **Recommendation (3.8), alongside 3.7 and for the
  same reason not drafted here**: extend `CLAUDE.md` §13's deliberately-broken-input standard, in
  words, to design selection as well as check verification — again the maintainer's call, since it
  reaches the same section.

**An open question, distinct from every recommendation above — no recommendation number, because
this review is not proposing a remedy.** `delivery-process.md` §6 step 2 requires the test
written first, red before green, before step 3's implementation (`delivery-process.md:107-109`,
verified directly). Task 1.2 (`docs/plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md:692-740`) built the
`_Resolver`'s new branches, `Bundle` persistence of `graph`/`resolved_payloads`, and a wholly new
`rating_handlers.py` Job-handler module (mirroring `rate_table_handlers.py`'s shape) — the types
and the module under test did not exist yet, so a test written first would not have imported. The
compensation was writing the tests immediately after, in the same PR, against the implementation
as built.

Two readings are both defensible and this review takes neither side:
- **§6 gains an explicit carve-out** for a slice task that introduces a wholly new type or module:
  red-green governs behaviour added to something that already exists, and a task that scaffolds
  the thing itself writes its test immediately after, same PR — a documented exception, not a
  silent deviation each time it recurs.
- **§6's general rule was already wrong and this is what it should have said from the start**:
  not "test before implementation" but "test in the same PR, never a later one" — satisfied by
  Task 1.2 as executed, and it would cover the ordinary case too without naming an exception.

**This is a maintainer decision, not a planner's**: choosing between them is re-planning a
governance document this charter does not extend to, and recording it as resolved either way here
would erase the record of which reading was open when the question was raised. It is written down
as the open question it is, for the maintainer to settle.

**4. Document drift.**

- **Three `03` §9 requirements leave their deciding variable unstated, found together because WK-671
  is the first workstream chartered to *measure* rather than build against them** (`03:797-798,
  807-808`):
  - `NFR-490` ("Tracing adds ≤ 20 % to scoring latency…") names no statistic — mean, p99, or
    otherwise. Its neighbour, `NFR-489`, states "p99" twice in the same table. Measured failing
    regardless of which statistic is meant (`F35`), but the margin depends on it.
  - `NFR-499` — **resolved.** RL-917 (`03:807`, 2026-08-30) settled what "logged" reaches
    (persistence, not only log lines) and reconciled it against `FR-260`'s Golden Quote store.
    No further action.
  - `NFR-500` — no storage format named, and format is what decides the verdict (2.6× over
    budget uncompressed, 4 % of budget under gzip). Already registered (`F37`, `register.md:43`)
    with its own remedy (a spec amendment plus a Slice 4 measurement obligation). No new action
    beyond what `F37` already carries.
  - **Recommendation (4.1):** state the statistic, the population it is measured over, and — where
    storage is involved — the encoding, in the same sentence as any numbered NFR's budget. Ruling
    34 (`docs/rulings/RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md:112-130`) already states
    the population-scoping half directly for `NFR-489` ("if [the population] is ever narrowed…
    the narrowing must be written into the requirement"); `F37`'s own remedy is the encoding half
    for `NFR-500`. The statistic half has no precedent yet; this review adds it. **Predicted,
    not asserted:** every other module's §9 table has been read but not yet measured against —
    expect the same yield when each module's turn comes.
- **A spec cross-reference points at the wrong requirement, verified at source.** `FR-241`
  (`03:137`) ends "unless the deployment explicitly uses date-based routing (`FR-247`)."
  `FR-247` (`03:153`) is the **Premium Ladder** — confirmed directly. Date-based routing is
  `FR-270` (`03:196`), also confirmed directly, and it has **zero implementation hits**
  anywhere in `backend/` or `packages/` (`git grep -rn "FR-270"` returns nothing) — a wrong
  citation pointing at an unrelated requirement, whose correct target is itself unbuilt. This is
  ordinary spec-change territory (a citation fix), not a workstream finding; flagged here because
  nothing has filed it yet.
- **`lead.md`'s self-description is contradicted by this workstream's own record.** It states the
  lead is "the only role that mostly relays rather than derives." Self-reported or caught in flight
  this workstream: the planner (four citation errors, self-caught), the scope-derivation pass (a
  range false-zero it had just warned about, and an overstated contract finding, self-corrected),
  the decision-maker (two citation errors from reading a fragment), and the lead (five, by its own
  count). **Recommendation (4.2):** correct or drop the parenthetical — the charter is a document
  like any other, and this is drift between what it claims and what the record shows, even though
  the artifact is a role file rather than a spec.
- **No role file names the specific trigger this workstream's evidence names for the authority
  boundary**: a correctly-proved finding is exactly when choosing the remedy too is hardest to
  resist, evidenced twice each by the planner and the lead, and by the clean counter-example (the
  decision-maker's refusal to rule the Quote Context governance question, which is why a second
  viewpoint caught the `NFR-499` access-control question at all). **Recommendation (4.3):**
  name that trigger explicitly in every role file rather than a generic "stay in your lane." This
  review does not draft the wording — role-file edits are outside this charter's grant
  (`planner.md`'s Tools line names `docs/plans/` and `docs/closures/INDEX.md#plan-reviewsmd`, not
  `.claude/roles/`).
- **A sharper, distinct failure sits behind the authority-boundary material above, raised by the
  decision-maker against its own error, and it pairs with 4.3 rather than restating it.** 4.3 is
  about whether a role decides something outside its lane; this is about whether a **correctly
  named** rule was actually checked against the **specific act**, which can fail entirely inside a
  role's own lane. In the decision-maker's own words: *"Identifying a rule's interest is necessary
  but not sufficient; you still have to check whether the act is inside it."* Its own instance is
  self-refuting: RL-871's entire point was that a proposed test measured the wrong interest,
  yet the same author, having correctly named resource contention as §8's interest, then applied
  it to a merge — an act that starts no local process. Three more instances the same night, one
  self-reported by the lead: a parameters-carrier field checked against its stated purpose but not
  against whether *this* field is a returned API surface; a `test_worker.py` "directly" qualifier
  read without the alternative its own sentence names; and the lead's own "holding the merge until
  the gate clears," announced, then superseded by a merge three minutes later without correcting
  the announcement — during which the decision-maker cited the withdrawn rule back approvingly, so
  the wrong claim outran its own correction.

  **The datum that decides the remedy, not just illustrates it.** Minutes after naming this exact
  pattern for the third time in an hour, the decision-maker raised a scope objection to a table it
  had not seen, inferring from the lead's phrasing that its own observation had already been
  tabled there — the same tell, committed while describing the tell: *"Awareness of the pattern
  did not defeat the pattern. I had named it three times in the preceding hour. It still fired on
  the next assertion I made."* That rules out the obvious fix: "check the scope before asserting"
  is a remembered discipline, and a remembered discipline is what just failed under stated
  awareness. What worked, that same night, worked mechanically every time and required nobody to
  remember anything — `audit-docs.py` catching an unescaped pipe, a positive control catching a
  `GoldenQuote` zero, re-reading `origin/main` catching a tree that had moved, the memory file's
  own duplicate guard catching a repeat write. **Recommendation (4.8):** this pattern needs a
  mechanical check local to each act, not a restated instruction to check the scope — and this
  review does not propose one check to cover all four instances above, because a merge's
  disturbance, a field's API-surface status, a qualifier's alternative and a role's authority
  boundary (4.3) share no single instrument. Where 4.3 is landable as a role-file amendment now,
  this recommendation is narrower: a future instance of this shape gets a mechanical, act-local
  check before anyone proposes a reminder — a reminder is the thing this section's own evidence
  just falsified.
- **`delivery-process.md:310-315`'s own list of durable homes for reasoning is wrong for its
  stated audience — a document-drift finding that names itself while being written.** The rule
  names "a task" as an acceptable durable home for reasoning a 50-word message cannot carry. But
  members cannot read the lead's task board, so for the reader a dispatch actually addresses, a
  task id is inert — through this workstream the board silently accumulated the fourteen owed
  register rows, a whole correction batch and every input this review draws on, none of it
  reachable by whoever was meant to act on it. **The self-demonstration**: this review's own
  evidence-base file opens by calling one of its findings "itself one of the findings below," and
  that finding was not below when first read — the same rule's failure, caught in the act of
  citing it. What actually surfaced the trapped material was one member refusing to reconstruct
  five items from board access it did not have and asking for a filesystem artifact instead — the
  refusal produced exactly the documents this review has been citing throughout.
  **Recommendation (4.5):** the rule's list of durable homes should say a member-facing dispatch
  cites a **filesystem path**, not a task id — paths resolve between agents that cannot share a
  board, which is the audience the rule is written for.

  **A second gap the rule does not state: citing a path presumes the path already exists.** A
  compliant dispatch requires the artifact to be written **before** the dispatch that cites it, not
  after. Task #82's F42 quantification message ran to roughly 140 words because its durable home
  was that task itself, which the auditor cannot open; faced with a choice between breaching the
  50-word rule and stopping to write a file first, the author carried the reasoning inline instead.
  The rule should state the sequencing it currently only implies: the artifact exists first, the
  dispatch cites it second, or the dispatch waits.
- **The reporter published two wrong lines to the team's external Slack channel in one hour, both
  inferences presented as fact** — "a peak-hours pause was in effect" when the pause is
  weekday-scoped and it was Sunday, and "WK-671 close audit in progress" before it had started.
  Neither line was in the file the reporter's own brief says to publish verbatim; both were
  derived from partial signals, and the role corrected itself once told (not a discipline
  problem — its later cycles are clean). **The connection to the row above, and why it belongs
  with question 4's authority-boundary finding rather than beside it**: in both cases the
  information a role needed was unreachable by that role, and one of the two closed the gap by
  inference while the other refused and asked — the same contrast question 4's `NFR-499`
  counter-example already makes for a governance question, here for an information-access one.
  **Recommendation (4.6), narrower than 4.3 and specific to reporting roles — already landed,
  verified at `origin/main`, not merely proposed.** `.claude/roles/reporter.md`'s "The Slack post:
  facts only, never inference" section now states a positive whitelist of three named, verbatim
  sources ("What goes in") — the core of what this recommendation asked for, and checkable by the
  reader of the post in a way a list of forbidden inferences never is, because the next inference
  is always a new one nobody enumerated. It also keeps named violation examples ("What does NOT go
  in," quoting these exact two lines) rather than dropping them — an addition this recommendation's
  original framing did not call for but does not conflict with; the whitelist, not the examples, is
  what makes a future post checkable. **Owner: discharged**, by the reporter itself rather than by
  this review; recorded here because this review's own reconciliation caught it only on a fresh
  read of the current tree (cross-referenced from 3.10 above).
- **`docs/roadmap.md`'s WK-671 row is missing `FR-243`** (RL-861, mechanical edit outstanding)
  **and the sixteen ids question 1's Question A enumerates** — what WK-671's own plans claim that the
  row's text does not. See question 5 for the recurring mechanism this instantiates.
- **WK-672's row (`docs/roadmap.md:377`, `FR-260, FR-261, FR-262`) disagrees with its own charter text in both
  directions.** The charter names "regression runs"; no requirement defines one as such —
  `FR-261` presupposes a Regression Suite defined elsewhere, and the run itself exists only as
  a route (`03` §5.1:519) and a `pricing-core` signature (§5.2), neither cited by any requirement's
  own text. `FR-262` (the Quote Sandbox, `03` §5.1:518) is in the range and outside the
  three-item charter, and is separately claimed by WK-675's row ("quote sandbox + ladder
  waterfall") — double-homed. `RegressionRun` is documented only in the hand-authored contract tier
  (`docs/contracts/schemas/regression-suite.schema.json`), not in `03` §4's own text — a drift
  between the spec and its own contract, on the side `contract-guard`'s drift check does not reach.
  `GOLDEN_QUOTE_MISMATCH` is declared at `03` §5.1 (error codes owned by this module) and confirmed
  absent from `backend/src/app/errors.py`'s `RATING_ERROR_CODES` — not yet a live defect (nothing
  raises it today) but the same shape as `F29`, one workstream early. See question 5 for whether
  any of this should hold up WK-672's start.
- **A planning artifact asserted a decision existed when it did not, verified directly against
  the ruling it cites.** `docs/plans/PL-00848-wk-671-slice-3-still-held-on-one-unruled-decision-and-d6-the-decision-that-releases-it.md:72` states
  "`score_batch` stays plain `def` (RL-868, restated in the module docstring)" — but RL-868
  (`docs/rulings/RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md:16-59`) rules `score_one`'s real-time path
  specifically, and its own text says so: "`score_batch`… is **not** ruled here and its own `def`
  signature… is untouched." The citation names a ruling that explicitly disclaims the thing it is
  cited for. **This is a stronger defect than an omission**, and the same document's own title —
  "WK-671 Slice 3 — still held, on one unruled decision; and D6, the decision that releases it" —
  shows the cost directly: `D6` (batch resumability) was the actual open decision, and it sat
  behind this false "already ruled" reading until a later, dedicated ruling addressed it. An
  omission gets noticed when someone goes looking for the answer; a false positive does not,
  because the reader has no reason to look again. **Recommendation (4.7):** a readiness or
  planning sweep that books an item as "ruled" reads the cited ruling's own scope clause before
  citing it, not merely confirms the ruling exists — the same discipline this document has
  applied throughout to its own citations, here proposed as a standing step rather than a
  one-off habit.

  **The same false claim has an earlier, compressed sighting, and its coverage was partial.**
  `docs/rulings/RL-00888-d2-trace-persistence-is-a-thin-row-plus-a-blob-body-and-the-recovery-document-s-retention-argument-is-backwards.md:23-24` — the readiness sweep itself — already
  wrote "Recovery items 1, 3 and 5 are already ruled (Rulings 10, 5 and 9 respectively)." Item 3 is
  `docs/plans/PL-00851-wk-671-five-decision-points-recovered.md:106`'s "Batch chunk/resume" — confirmed
  directly — the same D6 the leaf plan's own title later names as still open. The claim was not
  made once: it originated compressed in the sweep, then was carried forward and quoted, expanded,
  into the leaf plan, uncaught at either step. Per the decision-maker's own count (attributed, not
  re-derived here): the sweep consulted only **3 of the 9** ruling-record documents that existed —
  consistent with a sweep that never reached RL-868's own disclaiming sentence.

  **It also undercuts a conclusion filed outside this review's own sources.** A session-local
  working note (`process-instrumentation.md` — not a repository artifact, not otherwise cited in
  this review) draws a cross-task conclusion that fix-loop count correlates with whether a task
  was pre-resolved rather than with its size, counting Task 1.2 as pre-resolved on the strength of
  exactly the reading just shown false. This review does not edit that note — it is neither a
  repository file nor within this charter's grant (`docs/plans/`, `docs/closures/INDEX.md#plan-reviewsmd`) —
  but the conclusion should carry this qualification, or be re-checked against which inputs were
  genuinely pre-resolved, before anyone reads it as settled.

**5. Shape.**

- **No re-cut of the WK-671–WK-674 boundary.** Review 8 already asked this and answered it (accepted
  2026-08-29): `FR-250`'s live-default path and `FR-257`'s two preconditions are
  domain-inherent dependencies on WK-673/WK-674, not artifacts of the cut. Nothing in this pass's
  evidence disturbs that finding; this review reaffirms it rather than reopening it.
- **Review 8's own binding condition on this boundary is still unmet.** Its 5.1 acceptance bound
  WK-671's close to a named, dated register deferral each for `FR-250` and `FR-257` — "not
  silence, and not a plan that quietly ships a stub and calls the requirement done" (review 8,
  question 5). Verified directly at this review's own base SHA: `git grep -n
  "FR-250\|FR-257" docs/findings/register.md` at `19eaabc` returns exactly one line,
  `F-W9-2`'s prose mention of `FR-257` inside a different row — **neither id has a row of its
  own.** Not a new finding; review 8 already found it and gave it an owner ("WK-671's close").
  Restated because §14's own rule is that nothing proceeds while an earlier review's finding lacks
  a resolution, and this one is still open at the moment this draft is written. `FR-250`'s own
  limb split (explicit-ref path delivered; live-default path deferred to WK-674, the 409
  `NO_LIVE_RATING_VERSION` standing in as the interim refusal) has reportedly been ruled since this
  evidence was gathered; the register row itself is not yet written, and this review does not write
  it — that is the closure record's artifact, not this one's.
- **WK-672 is not ready to build as currently scoped, independent of the WK-671–WK-674 boundary question.**
  Its row and its own charter text disagree in both directions (question 4), and two spec-level
  gaps sit under it (`RegressionRun` undeclared in `03` §4's own text; `GOLDEN_QUOTE_MISMATCH`
  unregistered). None of this is a boundary problem — the row's text is wrong about what WK-672 is,
  discoverable and fixable now, independent of anything WK-671 still owes. **Recommendation (4.4):**
  correct WK-672's row and close the two spec-level gaps before or as part of its opening slice.
  `CLAUDE.md` §0's table already treats "a capability not yet specified" as spec-change-first work;
  this is that case for the workstream about to start, not a later phase, and this review surfaces
  it rather than mandating a specific slice shape.
- **Review 8's proposal 4.2** (a workstream row cites the spec section as its scope of record, a
  numeric range only as a human-readable gloss) **was accepted 2026-08-29, left unowned, and has
  since fired on `FR-243` alone and now on this review's own Question-A sixteen under
  question 1** — a repeat firing at a much larger scale than either single-id instance it has
  already been checked against. RL-861 additionally found the proposal needs a temporal
  qualifier before it can be built as a mechanical check: "the section is the row of record as of
  the owning workstream's close; a requirement appended after that workstream closed belongs to
  whoever builds it" (`docs/rulings/RL-00861-wk-671-s-and-it-is-forced-rather-than-chosen.md:63-66`) — recorded here
  for whoever eventually owns 4.2, since nothing in that acceptance line disturbs it.
  **Recommendation (5.1):** given four firings (`FR-223`→WK-669 and `FR-252`→WK-671, both already
  fixed; `FR-243`→WK-671, ruled; this review's sixteen-id gap, six `FR` and ten `NFR`) at a
  growing and now much larger cost each time, 4.2 needs an assigned owner rather than continuing
  unowned — this review does not choose who.
  **A further sighting, in a different kind of document, named rather than added to that count**:
  `docs/closures/CR-00838-work-item-record-wk-669-the-rating-contract-validation-and-bundle-compilation.md:27`'s own verdict table compresses `FR-237, FR-238, FR-239, FR-240, FR-241, FR-242` into one
  "delivered" row on a bare marker count (question 2 above) — the identical bare-continuation
  mechanism, reaching a closure record's verdict table rather than a roadmap workstream row.
  `NFR-502/501`'s own omission-then-correction (`docs/roadmap.md:376`'s own note) is a further
  data point of a related but distinct shape — carried forward but never transcribed, rather than
  compressed out of view — and is likewise not folded into the four above; the two counts answer
  different questions and this document does not merge them into a new one. **What both widen is
  the fix's reach, not its urgency**: whatever check 4.2 becomes needs to cover verdict tables
  under `docs/audit/work/*/README.md` as well as `docs/roadmap.md`'s own rows.
- **A related, narrower proposal, its own owner already named.** RL-861 separately proposed
  that `.claude/skills/spec-change` require a new `FR-`/`NFR-` to name its workstream row in the
  same commit that mints it, symmetric with the existing rule for a new `OQ-`
  (`docs/rulings/RL-00861-wk-671-s-and-it-is-forced-rather-than-chosen.md:75-91`), naming "the same §14 review that
  owns 4.2" as its owner. **Recommendation (5.2):** adopt it — the preventive form of 5.1's
  reactive check, costing one sentence in an existing skill, within any role's standing grant to
  write a skill (`CLAUDE.md` §12). This review proposes the wording exist before WK-673 or WK-674 mint
  their own first append; it does not draft the sentence itself, on the same logic review 8 used
  for its own unowned proposals.
- **`F31`'s charter correction is drafted and ready, not decided here.** `watcher.md:11-24`'s
  roster-derivation clause has no live implementation; the withdrawal notice already states the
  honest replacement text in full. **Recommendation (5.3):** apply it — a role-file edit outside
  this charter's grant to make directly, but costing nothing further to draft.
- **No new instance of "a row nothing can be said to have closed"** (review 8's own smell) for WK-671
  itself — it spans several features but one technology layer, unlike WK-664's Vue-view/OIDC/
  database-trigger span. WK-672's row, on today's evidence, is heading toward the same smell before it
  has even started (three named deliverables, a range that both under- and over-counts them) —
  flagged under question 4, not asserted here as a re-cut.
- **No new instance of "a phase exit criterion the phase cannot meet."** Phase 2's exit criterion
  (`docs/roadmap.md:365-367`) needs a live quote inside the latency budget; `NFR-489`'s
  without-GBM half is *not established*, not *failing*, and its own remedy is already scheduled
  (Slice 2 Task 2D, per `F38`'s register row) — the roadmap's own risk mitigation
  (`docs/roadmap.md:392`, "build the latency harness in WK-671 alongside the evaluator") did exactly
  what it was for. Worth watching at Phase 2's exit demo, not a finding now.
- **Candidates A and B, from the unnumbered "Pending proposals" section above, formally taken up
  here** — that section's own text anticipated this ("the review at WK-671's close folds these in").
  **Candidate A** (do not push to a branch someone is reading while reviewing or auditing it) and
  **Candidate B** (a count is not load-bearing unless stated at the granularity it was counted at)
  are both **recommended for adoption (5.4)** into `delivery-process.md` §15, alongside its
  existing five rules. Per that section's own stated rule, **numbering happens at acceptance** —
  this review does not assign either a rule number; that is the maintainer's action alongside the
  acceptance line, as it was left.
  **A third candidate for the same rule set, raised under question 3 above**: a correction states
  what it supersedes, not only what it asserts — a corrected claim without a named prior leaves
  both readings live until a reader checks, which is how a correction tonight nearly reverted work
  already correctly done under the position it silently replaced. Recommended for the same
  adoption, same unnumbered treatment, same reason.

---

**Decision point, not a recommendation — RL-860 named this review as where it is decided, and
`CLAUDE.md` §12 reserves the decision itself to the lead.** The gate-coverage cluster (`F27(c)` +
`F29` + `F33`, `register.md:33,35,39`) and `F-W9-3`'s clauses (4), (5) and (6) (`register.md:25`) —
one mechanism comparing a spec-declared shape against its implementation on four separate axes —
are due a placement now: "decide whether it becomes a workstream row or a maintainer task"
(RL-860). Options, not a pick:

(a) **A dedicated slice**, bundled as RL-860's own author argued (one mechanism answers all
    four; a partial fix on any single row is not the target shape), landing inside a Phase 2
    workstream still to open (WK-672's own spec-change slice, or WK-675/WK-690).
(b) **A maintainer task outside the workstream ladder**, since none of the four blocks any
    requirement's own delivery today.
(c) **Split by cost** — the `mypy` `files` widening (`F33`) is closer to a config change than the
    other three; taking it alone first and bundling the remaining three later trades the "one
    mechanism" argument for faster partial progress.

This review's own reading favours (a), for the reason RL-860 already gave — but the choice, and
which workstream if (a), is the lead's to rule, not this document's.

---

#### Status of this draft, by question

| Question | Status | What would change it |
|---|---|---|
| 1. Completion | **Provisional** | Final per-id tally needs Slices 2–4 landed and the §13 closure audit run; PRs #435/#436 may also land before filing |
| 2. Omission | **Settled** as a list; **open as verdicts** — the gate-coverage cluster (decision point) and the two fresh WK-669 defects (`FR-237` pins-completeness, `FR-241`) all need one this review does not give | Slices 2–4 could surface more; none expected to remove what is listed here |
| 3. Skills and research | **Settled** | Process-control findings do not depend on the unbuilt slices |
| 4. Document drift | **Settled** for what is found; more likely once Slices 2–4's own spec sections get read as closely as Slice 1's was here | A fresh drift pass once Slices 2–4's plans exist on `main` |
| 5. Shape | **Mostly settled** — no-re-cut and WK-672-readiness stand on their own; the gate-coverage placement and `F31`'s charter fix are open by design (the lead's and a role-file owner's, respectively) | The lead's ruling on the decision point; Slices 2–4 landing does not itself change this question |

#### Proposals, consolidated — review 9 (draft)

| # | Proposal | Kind |
|---|---|---|
| 2.1 | `FR-218` gets a Ruling-30-style attribution ruling before the close | ruling needed |
| 3.1 | Adopt `python-test`'s already-documented per-session-database remedy (not a new lock file) for the shared-database hazard | adopt existing doc, no new mechanism |
| 3.2 | Either the §14 trigger, the 50-word rule and `close-workstream` §5a's condition-artifact check get a mechanical check, or the maintainer accepts and states that all three are enforced only by memory | process — maintainer to weigh |
| 3.3 | NFR acceptance criteria measured near their bound require repetition under varied load, not a one-run distribution alone | convention (skill or leaf-plan template) |
| 3.4 | A route-adding plan states the regenerated OpenAPI contract as a Files-block deliverable and names the second CI workflow it arms | convention (`writing-plans`) |
| 3.5 | For each mechanical-check proposal above, ask whether a one-command grep tied to a specific act of writing would catch more, more cheaply, than a general enforcement mechanism | methodology — question posed, not answered |
| 3.6 | A figure quoted in a durable artifact prints `git rev-parse HEAD` in the same invocation; a file quoted as evidence carries its `mtime` | mechanical — citation discipline |
| 3.9 | Whoever owns `dev-commands`/testing-strategy decides whether a query's own scope stated beside its result is worth a checklist item | methodology — question posed, not answered |
| 3.7 | `CLAUDE.md` §13 gains a fifth verdict (or a qualifier) for measured-and-failing evidence, and a rule for multi-limb requirements | `CLAUDE.md` §13 amendment — maintainer's |
| 3.8 | `CLAUDE.md` §13's "proven on deliberately broken input" standard extended from checking a check to choosing a design | `CLAUDE.md` §13 amendment — maintainer's |
| 3.10 | A frozen leaf plan cites a symbol as its primary locator and a line number only as a hint | convention (`writing-plans`) |
| 4.1 | A numbered NFR budget states its statistic, population, and (where storage is involved) encoding, in the same sentence as the number | spec-writing convention |
| 4.2 | Correct or drop `lead.md`'s "only role that relays" parenthetical | role-file correction |
| 4.3 | Name the authority-boundary trigger (question 4's shape) explicitly in every role file | role-file amendment |
| 4.4 | Correct WK-672's row against its own charter; declare `RegressionRun` in `03` §4; register `GOLDEN_QUOTE_MISMATCH` before or at WK-672's opening slice | docs + spec-change |
| 4.5 | `delivery-process.md`'s durable-homes rule names a filesystem path, not a task id, for a member-facing dispatch — and states the sequencing: artifact first, dispatch second | process-rule correction |
| 4.6 | The reporter's brief states the positive rule — publish only what a named artifact says, and name it | role-file amendment (reporter) — **already landed**, `.claude/roles/reporter.md`, owner: discharged |
| 4.7 | A readiness or planning sweep reads a cited ruling's own scope clause before booking an item as "ruled" | methodology — standing step, proposed |
| 4.8 | A future instance of "is this act inside the interest I just named?" gets a mechanical, act-local check, not a restated reminder | methodology — question posed, not answered |
| 5.1 | Assign review 8's proposal 4.2 an owner, now that it has fired a fourth time at a much larger scale, carrying RL-861's temporal-qualifier refinement | tool or convention — unowned since 2026-08-29 |
| 5.2 | Amend `.claude/skills/spec-change` so a new `FR-`/`NFR-` names its workstream row in the same commit that mints it, symmetric with the existing `OQ-` rule (RL-861's own proposal) | skill amendment |
| 5.3 | Apply `F31`'s charter correction to `watcher.md` — text already drafted in the withdrawal notice | role-file edit |
| 5.4 | Adopt Candidates A, B and a third (branch-freeze while under review; a count states its own granularity; a correction names what it supersedes) into `delivery-process.md` §15 | process rule — numbered at acceptance |
| DP-1 | Decide the gate-coverage cluster's placement (options a/b/c above) | **decision, the lead's — not a proposal** |

**Maintainer acceptance:** _pending._ This is a draft circulated to the lead ahead of the
maintainer, not yet presented for acceptance. Before it can be filed: Slices 2–4 land (or are far
enough along that question 1's tally is real rather than provisional), the §13 closure audit
completes, review 8's still-open binding condition (the `FR-250`/`FR-257` register rows)
is met, and the decision point above is ruled by the lead. Everything in questions 2 through 5 is
not expected to change on those events, but will be re-read against whatever tree is current
before filing, per this document's own rule that a claim names the tree it was checked at.

> **Maintainer acceptance: accepted as proposed, 2026-09-01 — dated together with reviews 10 and
> 11 under review 11's proposal 11.1.** The `_pending._` paragraph above is kept as the record of
> the pre-acceptance state; the preconditions it names were met before this line was dated
> (review 10's §5d records the first two, at `b749acb`).

#### Sources

- `docs/roadmap.md` §7 (workstream table, risk table, Phase 2 demo-able outcome) — read directly at
  `19eaabc`.
- `docs/findings/register.md`, in full — read directly at `19eaabc`.
- `docs/specs/03-rating-engine.md` §3.1, §3.4, §3.6, §3.7–§3.9, §5.1, §9 — read directly at
  `19eaabc`, including `FR-241`, `FR-247` and `FR-270`'s own text for the
  cross-reference check.
- `docs/process/delivery-process.md` §8, §15 — read directly at `19eaabc`.
- `docs/closures/CR-00838-work-item-record-wk-669-the-rating-contract-validation-and-bundle-compilation.md:27` — read directly for the `FR-237, FR-238, FR-239, FR-240, FR-241, FR-242` verdict row.
- `packages/model-schema/tests/test_rating_version.py:44-47` — read directly to confirm the
  three stacked markers on one test.
- `packages/pricing-core/src/pricing_core/rating/compile.py:425-440` — read directly to confirm
  `FR-237`'s presence-only check.
- `packages/model-schema/src/model_schema/rating.py:131` — read directly to confirm
  `effective_from: datetime | None = None`.
- `git grep -rn "FR-270"` against `backend/` and `packages/` — run this session, zero hits.
- `backend/src/app/errors.py` — read directly to confirm `GOLDEN_QUOTE_MISMATCH`'s absence from
  `RATING_ERROR_CODES`.
- `.claude/roles/watcher.md`, `.claude/roles/planner.md` — read directly.
- `.claude/skills/close-workstream/SKILL.md:340-368` (§5a) — read directly at `19eaabc`.
- `backend/tests/conftest_db.py:12,35,39,251-252` — read directly to confirm the fixture's scope,
  autouse status, and the `GIP_TEST_DATABASE_URL` override.
- `.claude/skills/python-test/SKILL.md:284-319` — read directly to confirm the mutual-truncation
  finding, its 2026-08-24 measurement, and both remedies (serialise via `pgrep`; per-session
  database).
- `.github/workflows/frontend.yml:10,18-29` — read directly to confirm the `docs/contracts/
  openapi/**` path filter.
- `docs/plans/PL-00847-wk-671-slice-2-the-real-time-scoring-endpoint-its-bundle-slot-and-the-nfrs-that-need-the-http-path.md` — read directly (`grep -c
  '\*\*Files\*\*'` returns 4, none naming `generated.json`), at `19eaabc`.
- Rulings 29, 30, 34, 36 — `docs/rulings/INDEX.md#2026-08-29-w11-algorithm-pin-maturitymd`,
  `2026-08-29-w11-fr-rate-65-attribution.md`,
  `2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md` — read directly; RL-917 as amended
  into `03-rating-engine.md:807`.
- `git log`, `git grep`, `git merge-base --is-ancestor` against `origin/main` at `19eaabc` — run
  this session to confirm the ancestry and absence claims above, not assumed from the working notes
  that first reported them.
- `gh pr view 436` — run this session to confirm `F41`'s content and open status.
- Review 8 and the unnumbered "Pending proposals" section, both above in this document — read
  directly here rather than re-derived.
- `docs/plans/PL-00848-wk-671-slice-3-still-held-on-one-unruled-decision-and-d6-the-decision-that-releases-it.md:72` — read directly to confirm the
  "`score_batch` stays plain `def` (RL-868…)" citation.
- `docs/rulings/RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md:16-59` — read directly to confirm RL-868 rules
  `score_one` and its own text disclaims `score_batch`.
- `backend/src/app/platform/rating_versions.py` at `c1a98b1` (`git show c1a98b1:...`) — read
  directly to confirm `submit_for_review` (def at `:153`) calls `approvals.submit(` at `:178`.
- `docs/plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md:692-740` — read directly to confirm Task 1.2's
  scope (new `_Resolver` branches, `Bundle` persistence, a new `rating_handlers.py` module).
- `docs/process/delivery-process.md:107-109` (§6, steps 2-3) — read directly to confirm the
  red-before-green ordering the open question above turns on.
- `docs/findings/register.md`'s `F44` row — read directly at `origin/main` (`6f77abb`, fetched this
  session; the row itself states it was filed against `e16c459`) to confirm its tree-anchored
  locator and cross-check it against the bare-line citation in 3.10.
- `backend/src/app/platform/rating_versions.py` at `origin/main` (`6f77abb`) — read directly
  (`git show origin/main:...`) to confirm `submit_for_review` now at `:214` and `approvals.submit(`
  at `:239`, a 61-line shift from the `:153`/`:178` both F44 and this review's own earlier citation
  recorded at `e16c459`/`c1a98b1`.
- `.claude/roles/reporter.md` at `origin/main` (`6f77abb`) — read directly, "The Slack post: facts
  only, never inference," to confirm Recommendation 4.6 is already landed.
- `docs/rulings/RL-00888-d2-trace-persistence-is-a-thin-row-plus-a-blob-body-and-the-recovery-document-s-retention-argument-is-backwards.md:23-24` and
  `docs/plans/PL-00851-wk-671-five-decision-points-recovered.md:106` — read directly to confirm the
  readiness sweep's own compressed mis-citation and that its "item 3" is batch chunk/resume (D6).
- `CLAUDE.md` §13 — read directly (this file's own governing text, present in every session) for
  "a reference carries its scope and its measurement… a `Verified` date carries the tree," cited in
  3.10.
- Session-local working notes that first surfaced several of the above, credited by name in prose
  and not cited as resolvable paths: `phase-review-inputs.md`, `w11-scope-derivation.md`,
  `close-audit-baseline.md`, `register-rows-owed.md`, `eta.md` (all
  `~/w11-handover-2026-08-29/`, 2026-08-30). None of this review's findings depends on a reader
  having access to them.

---
