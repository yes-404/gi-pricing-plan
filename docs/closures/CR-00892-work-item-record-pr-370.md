---
id: CR-892
family: closure
kind: work
title: Work-item record — pr-370
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-29
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/work/pr-370/README.md
---

# Work-item record — pr-370

Pre-merge slice-plan review, not a close. The lead asked four specific checks before
merging PR #370 (branch `w11-slice1-plan`, author pilot-planner): every RL-872–11
disposition reflected, no frozen-plan edit, cited line numbers resolve at `origin/main`
`b826790`, and the plan passes the project's cold-start bar. Reported per-check, not as a
merge recommendation, per the lead's explicit instruction and this role's charter (auditor
proposes, never issues, a verdict).

## Scope

PR #370 files `docs/plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md` (1333 lines at Pass 1's
`d40804d`; 1485 at Pass 2's `786f21e` — the branch is under active, rapid revision, several
commits per hour; every claim below names the SHA it was checked against) — the
task-granular leaf plan for WK-671 Slice 1's five tasks, `delivery-process.md` §6 step 1 — plus
an index update to `docs/plans/README.md`. It supersedes nothing in the frozen sequencing
plan (`docs/plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`); five corrections to that map are recorded
inline instead of editing it.

## Checklist

Not the `close-workstream` checklist — this is a pre-merge plan review against the lead's
four named checks (delivery-process.md §6 step 1's plan/resolve/decide gate), run once,
2026-08-29.

## Evidence

**Pass 1 — tree: PR #370 branch (`pr370-review` locally) at commit `d40804d`.** Rulings and
citations checked against `b826790`, confirmed to be `origin/main`'s tip at the time of
review (no drift at that moment).

**Self-correction: Pass 1's own citation was a defect of the kind it found.** This record
first named the audited tree by commit *message* ("docs(plans): a plan's premises age
faster than its literals"), not by SHA — even though the SHA (`d40804d`) was captured in
the same terminal output and simply not carried into this file or into the report sent to
the lead. A message is not a locator: PR #370 gained six more commits in the time between
Pass 1 and the lead reading the report, including `d41f379` ("apply RL-878"), six
minutes after `d40804d` — which fixed the RL-878 finding below before Pass 1's report
even reached the lead. Caught by the lead, not by this session. Every SHA in this record
from Pass 2 onward is cited as a SHA, never a message.

- **No frozen-plan edit** — confirmed directly: `gh pr diff 370 --name-only` lists exactly
  `docs/plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md` and `docs/plans/README.md`.
  `2026-08-29-w11-scoring.md` does not appear. **Pass.**
- **Rulings 6–11 reflected** — all six confirmed, each against `docs/plans/2026-08-29-
  w11-slice1-rulings.md` (the rulings file PR #368/`b826790` filed) and a specific line in
  the new plan: RL-872 (plan:1244), 7 (plan:870-873, 879-883), 8 (plan:884-892, 964-980),
  9 (plan:1153-1167), 10 (plan:893-901), 11 (plan:1124-1151, both of its own corrections
  named explicitly). **Pass.**
- **"Five corrections to the frozen map"** — confirmed exactly five (plan:311-339): C1
  (`_Resolver` has two real branches today, not the map's implied none/four), C2
  (`predict_gbm` lives in `gbm.py` not `predict.py`), C3 (neither predictor takes `nthread`
  — a signature change, not a call-site keyword), C4 (`DislocationRun.largest_movers_blob`
  doesn't exist; `rate_table_handlers.py` is the real Job-handler precedent), C5 (the map's
  Slice-1 requirement list omits FR-243). **Pass.**
- **`python3 scripts/audit-docs.py`** re-run independently on PR #370's actual tree (an
  isolated `git worktree add` off the PR branch, not the shared checkout) — clean, exit 0.

**Pass 2 — tree: PR #370 branch (`FETCH_HEAD` at fetch time) at commit `786f21e`; rulings
at `002f4d8` (`origin/main`'s tip for that file at the same fetch, carrying the original
Rulings 6-12 plus a "RL-878 addendum" from PR #373).** Re-audited against the lead's
correction that a citation count cannot tell narration-correct from steps-wrong — this
pass checked every ruling's actual Task steps/exit-criteria, not whether its number appears
in prose, and quotes plan line numbers with the step text, not just headings.

- **The original pr370-ruling12-not-reflected finding: confirmed fixed.** All of Rulings
  6-11 and RL-878's original three obligations (five-member `purpose` enum,
  `scoring.schema.json:12` correction, FR-218's both-limb test) are now genuinely
  reflected in Task 1.4's operative Steps and Acceptance block, not merely narrated —
  independently re-derived, not taken from the lead's say-so.
- **New finding — RL-878's addendum (obligation 4) is missing, not narration-only,
  absent.** **Correction to how this was first reported to the lead:** obligation 4's
  substance is lifting `"scoring"` from `backend/tests/test_contracts.py`'s exclusion dict
  (reason on file today: `"later-phase — 03 rating"`) — a **forward guard** against the
  contract-vs-generated-code drift that becomes possible the moment Task 1.4 creates
  `QuoteContext`/`ScoringResult`/`Trace` in `model-schema` (`...rulings.md:586-594`, `002f4d8`).
  Registering those three shapes in `scripts/generate-contracts.py`'s `GENERATED_SHAPES` is
  the companion action the same paragraph names (`...rulings.md:596-598`) — necessary, but
  not itself what the addendum is *about*; leading with `GENERATED_SHAPES` in my first report
  put the mechanical half in front of the substantive one. Searched the full 1485-line plan
  for `GENERATED_SHAPES`, `test_contracts.py`, "exclusion": zero hits — both halves of
  obligation 4 are absent, not just the one I named first. Directly relevant to PR #371's own
  contract-drift CI failure (see `pr-371`'s record): Task 1.1's Acceptance block (plan:682)
  *does* correctly require "the contract regenerated and committed" (so the plan is right
  there), but nothing in Task 1.4 names either half of obligation 4 — the same class of gap,
  one task earlier. The rulings file separately reports (not rules — "the remedy is scope,
  and scope is the lead's," `...rulings.md:607`) that three already-shipped `model-schema`
  types (`RatingVersion`, `RatingAlgorithm`, `RateTable`) sit in the state obligation 4
  prevents right now, unrelated to Task 1.4 — tracked elsewhere as F27 (task board #41), not
  re-litigated here.
- **RL-879 (`f318287`) correctly out of scope by timing**, not omission: it landed
  2026-08-29T15:27:56Z, 24 seconds after `786f21e` (2026-08-29T15:27:32Z). Noted without
  penalty; re-check once the plan has had a chance to incorporate it. The plan already
  names PR #375 for F-W11-1-5 ahead of that commit landing, which is itself worth a glance
  next pass, not asserted as a problem here.
- **Count mismatch, resolved by the lead, not by re-counting here:** "five" (the number
  the lead first gave this session) was the lead's own count and had aged — the planner
  found one more, filed as prose, after it was said. The plan's self-review's "six" is
  current. Per the lead's own instruction following from this: **cite the enumeration
  itself, never a bare count, for exactly this class of finding** — a number goes stale
  the moment one more site is found or one is fixed, the list of sites does not. No site
  is enumerated by number in this record for that reason.

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| **pr370-ruling12-not-reflected** | Task 1.4's `purpose`/`cancellation` handling (F-W11-1-1), found at `d40804d`: the plan named only Rulings 6-11 and Task 1.4 Step 1 said to leave `purpose` unresolved, even though RL-878 (same rulings file, same base commit) had already ruled it. | **fixed** between `d40804d` and `786f21e` (commits `d41f379`/`58e72a6`); re-verified at `786f21e` by reading Task 1.4's actual Steps/Acceptance, not by citation count | resolved |
| **pr370-ruling12-addendum-missing** | RL-878's addendum (`002f4d8`, `...rulings.md:586-598`) obligation 4 is lifting `"scoring"` from `test_contracts.py`'s exclusion dict — a forward guard against contract-vs-generated-code drift once Task 1.4 creates `QuoteContext`/`ScoringResult`/`Trace` in `model-schema`; registering those shapes in `generate-contracts.py`'s `GENERATED_SHAPES` is the companion action, not the obligation's substance (my first report to the lead named the companion action first — corrected here). Neither half was named anywhere in the plan at `786f21e`. | **fixed before merge.** PR #370 merged as `59fe0a7`; independently re-verified at that exact commit (not taken from the lead's report): both halves are now operative in Task 1.4's Files (plan:1105-1106), Steps (plan:1158-1165), and Acceptance (plan:1363-1365) — not narration. The plan's own self-review also names the root cause of how this was first missed: a heading-based ruling sweep is structurally blind to an addendum, which gets no new `## Ruling N` heading of its own (plan:1495-1499) — fixed there by enumerating by `git diff` of the rulings record instead of by heading. The stale phrase "Three obligations land in this one PR" survives only as a quoted, past-tense example inside that same self-review (plan:1504-1507), not as a live claim anywhere else — checked directly, not assumed from the lead's characterization. | resolved |
| **pr370-s9-citation-shift** | Four `03-rating-engine.md` §9 NFR-budget citations used in Tasks 1.3-1.5 (`:777`, `:778`, `:780`, `:784`) shifted +4 lines when PR #368 edited §3/§5.1/§5.2 upstream of §9. The plan's own re-derivation disclaimer (plan:65-69) names only §3/§5.1/§5.2 as shifting, not §9 — an undisclosed casualty of the same edit. Each citation still sits beside its correct NFR- id and is re-derivable by grep (confirmed); no substance lost, pointer imprecise. | accept — re-derivable, not load-bearing (proposed) | open |
| **pr370-fr-rate-22-cite-slip** | The *frozen* plan's own Task 1.1 text says to add the FR-237 citation at `03-rating-engine.md:512`; the citation already existed, at `:513` (verified directly — line 513 is the exact `POST /api/v1/rating-versions` row). Pre-existing in the frozen map, not introduced by PR #370; PR #371 (Task 1.1) correctly verified this directly rather than following the stale line number. | accept — pre-existing, not this PR's defect (proposed) | open, not owned by pr-370 |
| **pr370-coldstart-provenance-nit** | The PR description's claim that "the 405/404 split... was verified against a running FastAPI app" is not evidenced inside the committed plan file itself, only in PR/GitHub metadata (which does not survive as a durable citation once the PR closes). The underlying causal reasoning (`models.py:1092` is the GET registration) is independently confirmed sound regardless. | accept — reasoning holds independently of where the empirical claim lives (proposed) | open |

## Sign-off

**PR #370 merged as `59fe0a7` (the lead's merge decision, not this role's).** The one
blocking finding (`pr370-ruling12-addendum-missing`) was fixed before merge and
independently re-verified at the merge commit itself, not accepted on report. The three
remaining findings (`pr370-s9-citation-shift`, `pr370-fr-rate-22-cite-slip`,
`pr370-coldstart-provenance-nit`) are minor/pre-existing and were not raised as blockers;
they stay `open` here for the record rather than silently dropped now that the PR is
closed — none has a named owner yet, which the next slice or a phase-review pass should
give one rather than let sit unassigned. Not a Slice, Work or Phase close — no maintainer
line applies (`delivery-process.md` §2); this is a pre-merge plan review's record, done.
