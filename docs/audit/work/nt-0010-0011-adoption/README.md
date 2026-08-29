# Audit record — nt-0010-0011-adoption (`CLAUDE.md` §15 step 5)

> Not a `CLAUDE.md` §13 workstream closure record — the NT-0010/0011 adoption is not a
> numbered workstream, and closure acceptance for a Work, Phase or Project stays the
> maintainer's alone (§12, §13). This is the audit trail for one gate inside §15's adoption
> procedure: whether Task 5 of `docs/plans/2026-08-29-nt-0010-0011-adoption.md` delivered
> what the ruled proposal (`docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md`)
> required. Filed because the audit itself had no durable home anywhere else — found while
> slimming the auditor's own handover file, filed as task #29.

## Why this record exists, and why now

A clean verdict on this audit was the trigger for a real, consequential sequence: handover
rework, an unattended team stand-down, a respawn of all seven roles from
`.claude/roles/*.md`, and W11 slice 1 run as the pilot — all of it before the maintainer
saw any of it (the gate sits *after* the pilot, not before). The people who held this
audit's reasoning are the people about to be replaced. Without this record, the fact that
the audit was NOT CLEAN before it was CLEAN — and exactly why — would not have survived the
stand-down anywhere but a chat log.

## Scope

Two passes over the same target: does the landed implementation represent every obligation
in the ruled proposal, with every divergence recorded against a legitimising ruling, and
are the adopted documents mutually consistent? Not a requirements-coverage audit against
`docs/specs/` — there is no spec here, only a proposal and a plan to check the
implementation against.

## First pass — NOT CLEAN, at `2d3824e`

**Verdict: NOT CLEAN.** Delivered 2026-08-29 to `team-lead`. Range audited: `30fcfa9..
2d3824e` — PR #335 (`3171520`) and PR #336 (`2d3824e`, the separately-ruled §9 fix).

**Blocking finding.** All seven `.claude/roles/*.md` files, as landed by Task 5, failed the
spawn-input test — "does this file alone brief a fresh session with no fallback," not "does
it describe the role accurately." Task 5 had only edited the files' `Tools:` lines (the
Part A2 write-scope gate); the `Owns:`/`Never:` sections, where the actual gaps lived, were
untouched. Confirmed directly on `auditor.md` (three gaps: the three audit axes named
without the command or which three; `docs/audit/work/`, `register.md` and the two
checklists never cited by path; "re-run the checks" not saying which checks). Corroborated
independently by the lead finding the identical shape on `watcher.md`/`reporter.md` (states
WHAT a mechanism is, never HOW it runs — no threshold, no escalation timing, a placeholder
where a number belonged). A clean verdict on files already known to be spawn-insufficient
would have authorised spawning a team from files known broken — disqualifying regardless of
anything else found clean.

**Standing caveat, stated at the time and reaffirmed at the second pass — the single most
important line in this record.** These gaps were found by **directed inspection** — the
lead and the auditor deliberately reading role files against a named test — **not by the
pilot**. The eventual clean verdict describes the *repaired* files. **The pilot must never
be cited as evidence that the original role files were sufficient a priori — they were not,
and were fixed before the pilot ran, not proven adequate by it.**

**Two non-blocking findings, both real:**
1. The rulings record's own "Both notes' Status field stays open" line was false as of PR
   #335 (both flipped to `landed`) and undisclosed — unlike the source notes' own similar
   staleness, which #335's PR description explicitly named and reasoned through as
   acceptable.
2. `.claude/roles/**` carried zero CI coverage. Confirmed via `gh pr view 327 --json
   statusCheckRollup` → `[]`, not inferred from the workflow's `paths:` filter. Filed as
   task #18 (open — see Open items below).

**Two findings ruled cosmetic, but not trivial:**
1. `CLAUDE.md` §12's "`.claude/roles/` for the team roles" read as an index claim to a
   directory with no README.
2. `docs/process/delivery-process.md` §2's "verbatim" quote of the maintainer's Part A1
   ruling dropped the clause "close a work stream: " that the rulings record's own citation
   of the same quote kept — two artifacts both claiming *verbatim*, disagreeing.

**What checked clean on the first pass, in full — the credibility of a NOT CLEAN verdict
rests on showing what was not wrong, not only what was:** `CLAUDE.md` §12's ruled
replacement text, word-for-word exact against the rulings record's quoted block; the old
"Team process" paragraph removed rather than duplicated; the four then-amended role files'
`Tools:` lines matching Part A2's per-role ruling exactly, including the auditor's "never a
frozen plan, never a merge" qualifier; §13/§14 and `.claude/agents/README.md` explicitly
stated "checked and found inapplicable" in #335's PR description, not silently absent; the
frozen-plan vs. maintainer-directed authority groups present and labelled in the same PR
description; PR citations #315/#320/#322/#323/#329/#308/#309 lightweight-verified against
their actual merged diffs, not accepted from the rulings record's own account of them;
`audit-docs.py` clean.

## Disposition of the first pass's findings

Adopted in full by the lead the same day.

| Finding | Disposition | Landed |
|---|---|---|
| Blocking — role files fail spawn-input | Six-file amendment (task #21); `auditor.md` drafted separately, corrected by the auditor, sent directly to the executor | #338 `99946cc`, #339 `c780fde`, #341 `d708be3` |
| Non-blocking 1 — stale Status field | Routed to the decision-maker (file owner); fixed as a dated addendum, not a silent edit | #342 `22bf2e7` |
| Non-blocking 2 — zero CI on `.claude/roles/**` | Lead adopted the auditor's direct observation over their own inference from the path filter; the CI gap itself was not fixed, only the reasoning about it was corrected | Evidence only — #18 remains open |
| Cosmetic 1 — §12 index implication | Ruled: reword, do not build a README to match the wrong description | Folded into #338 |
| Cosmetic 2 — dropped quote clause | Ruled not actually cosmetic — two artifacts both claiming verbatim and disagreeing is a defect regardless of clause length; restored | Folded into #338 |

Two items surfaced between passes, pre-flagged by the lead and folded into the second
pass's scope before it ran: the `CLAUDE.md` §14 phase-review ownership split (ruled:
planner drafts and files, lead answerable for the trigger, maintainer accepts) needed
*both* `planner.md` and `lead.md` to carry their half; a second dangling "not by this plan"
reference in `reporter.md`, found by widening the sweep past the one the lead had already
found in `watcher.md`.

## Second pass — CLEAN, at `bc92ed9`

**Verdict: CLEAN.** Delivered 2026-08-29 to `team-lead`, adopted in full the same turn
("VERDICT ADOPTED. CLEAN at `bc92ed9`. §15 step 5 is closed."). Range audited: `2d3824e..
bc92ed9` — PRs #335 through #344 plus `bc92ed9` itself.

Re-verified everything fresh at the final tree rather than trusting the first pass or any
PR title:

- All seven `.claude/roles/*.md` files re-read in full. §14 split correctly carried by both
  `planner.md` and `lead.md`, each deferring final acceptance to the maintainer's line, not
  to each other. Both dangling "this plan" references fixed to name
  `docs/plans/2026-08-29-nt-0010-0011-adoption.md` by path (`watcher.md:27-28`,
  `reporter.md:35`). `decision-maker.md` confirmed to carry no clause reserving `CLAUDE.md`
  §0's spec-vs-code decision to the lead — a near-miss instruction the decision-maker had
  independently refused earlier, confirmed here as never having landed. `auditor.md` landed
  exactly as the auditor's own corrected text, unaltered. `executor.md` unchanged.
- Line counts (`wc -l`): 38/38/32/36/41/36/29 across the seven files — matching the "roughly
  doubled" claim exactly.
- Both cosmetic fixes and Finding 1's dated addendum (#342) re-read directly and confirmed
  well executed — the addendum cites current state with line numbers, follows the record's
  own header precedent, and re-verifies neighbouring bullets were not also stale.
- `audit-docs.py` clean; 533 requirements defined (up from 532, PR #340's FR-RATE-65).
- The CI gap (task #18) reinforced by a second, independent method beyond the first pass's
  `gh run list` grep: `gh pr view {341,343,344} --json statusCheckRollup` all three return
  `[]` against their merge commits (`d708be3`, `884e327`, `30fa593`) — role/skill-file-only
  PRs get zero CI; a mixed PR gets CI as a side effect of the other file, never because the
  filter learned about `.claude/`.
- **New on this pass, not previously registered — reading the seven files as a set rather
  than checklist-item-by-item**, specifically named by the lead as more valuable than the
  verdict itself: `watcher.md` and `reporter.md` name each other's boundary and agree
  (`watcher.md:24`, `reporter.md:33`); `lead.md`/`executor.md`/`decision-maker.md`
  independently agree sole merge authority is the lead's, with no drift; `executor.md`'s
  citation to the rulings record (`:30-32` → `...rulings.md:356-357`) verified verbatim.
- Holistic spawn-input verdict stated explicitly: all seven files pass, as a class — task
  #21 closed, not just its six named instances.

**The standing caveat, restated rather than dropped now that the verdict is clean:**
clean-now is not retroactive proof the files were sufficient from the start — the first
pass already established the opposite, and the repair was found by directed inspection,
not by any pilot run. Task #18 stayed open at this pass too; the new evidence reinforces
the disposition already adopted after the first pass, it does not resolve the gap.

## What the clean verdict released

Per the maintainer's own gate (ruled ahead of this audit, `CLAUDE.md` §15): handover rework
→ an unattended team stand-down → a new team respawned from `.claude/roles/*.md` → W11
slice 1 run as the pilot → **then** the maintainer's own confirmation, seen for the first
time only after the pilot has already run. This record is the fullest surviving account of
the reasoning the gate actually turned on.

**The pilot ran. Its findings are [`pilot-findings.md`](pilot-findings.md)** — §15 step 6's
output, and an input to both the gate and step 7. It carries the same scope limit this
record does: the repairs were found by directed inspection beforehand, so the pilot tests
only whether the **repaired** files are sufficient to spawn from.

## Open items at the close of this audit

Not resolved by this record; tracked on the team's task board, cited here so the citation
survives the stand-down:

- **#18** — `.claude/roles/**` (and `.claude/skills/**`) outside CI; two-halved fix, not
  landed.
- **#25** — five W11 decision points reduced to bare names in every durable artifact.
- **#26** — no role charter granted `.claude/skills/` writes despite four such PRs having
  landed; ruled (a), repeat-with-local-grounding, scoped to the five repo-write roles —
  check `.claude/roles/*.md` directly for whether it has landed by the time this is read.
- **#27** — the maintainer's 50-word team-message rule needs a durable home in
  `docs/process/delivery-process.md`. *(Landed 2026-08-29 in **§15**, "Correction and
  message discipline", not §13 as this line first said — §13 is the monitoring and comms
  loop. The wrong section number was the lead's, corrected before the rule merged; it is
  fixed here rather than silently, because a citation that does not resolve is the defect
  this record exists to document.)*
- **#28** — the reporter's three scripts, ruled but not yet filed under
  `.claude/skills/reporter-cycle/`.
- **#30** — three further promotion candidates surfaced by the same handover-slimming pass
  that produced this record (the verify-don't-accept evidence trail, W11's true
  13-requirement scope, two undocumented tool caveats), each with a proposed owner, none
  yet landed.

## Closed — §15 step 7, accepted 2026-08-29

**Accepted by the maintainer, 2026-08-29**, on the lead's presentation of this record plus
the pilot findings. On acceptance `NT-0010` and `NT-0011` received dated `superseded` status
and **`docs/process/delivery-process.md` became authoritative**; both notes are kept as the
proposal record, because the adopted specification does not carry the reasoning that produced
it.

**Five things this close is on the record as stating, because each is easy to lose:**

1. **The pilot was Task 1.1, not all of Slice 1.** Ruled by the maintainer mid-pilot. The
   Slice 1 plan (`docs/plans/2026-08-29-w11-1-evaluator-core.md`) still says at line 57 that
   §7's instrumentation *"starts with this slice — it is the pilot"* — true when written, now
   narrower in fact. **The plan was deliberately not edited to agree**, per
   `docs/plans/README.md`: a filed plan records what was believed. **This record is the
   authoritative document for the narrowing**, and the plan's line is not a defect.

2. **The a-priori caveat.** The role-file gaps were found by **directed inspection before the
   pilot**. The pilot cannot be cited as evidence that the original role files were sufficient
   a priori — they were not. It tests only whether the **repaired** files are sufficient to
   spawn from.

3. **Two kinds of finding, and only one is charter evidence.** `pilot-findings.md`'s P1–P5
   answer §15 step 6's own question. **P7–P14 are findings about engineering and verification**
   — real, and not evidence about charter sufficiency. Do not present them as one body.

4. **Acceptance discharges nothing carried.** Register row **F28** lists every pilot finding
   with its disposition — fixed, or carried with a named owner. Six are carried to the lead,
   four to the planner's §14 review at W11's close. They are enumerated there rather than
   copied here, because a second copy would age against the first. `CLAUDE.md` §14 still
   governs: nothing starts in the next phase while an open finding lacks a resolution.

5. **What no gate caught, which is the most consequential result.** `audit-docs.py` was green
   at every point a defect existed. The gates check **documents against documents** and **code
   against code**; nothing checks a document against the artifact it specifies. That gap
   contains the plans that instruct executors, the acceptance criteria that certify their
   output, and the hand-authored contracts describing shipped types — and it is why F27, F29
   and F30 exist. Every catch in this pilot came from a person declining to accept something.

## Provenance

Both passes audited and both verdicts proposed by the auditor role (`w11-auditor`); both
adopted, in full, by the lead — the only authority `CLAUDE.md` §12 gives a verdict to. This
record does not itself close, accept, or re-open anything: it documents an audit that had
already run and already been acted on, filed here only because it previously had no
durable home. Filed 2026-08-29 as task #29.
