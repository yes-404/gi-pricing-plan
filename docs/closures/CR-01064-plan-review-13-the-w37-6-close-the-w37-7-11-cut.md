---
id: CR-1064
family: closure
kind: review
title: Plan review 13 — the W37-6 close, the W37-7…11 cut
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-18
owner: lead
tree: 4d9fe1d62328285ac0483b047c3959e39e0f5bd6
phase: P2
work: WK-697
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
---

### Plan review 13 — the W37-6 close (checkpoint 3), the W37-7…11 cut, 2026-09-18

**Base tree: `4d9fe1d62328285ac0483b047c3959e39e0f5bd6`** — `git log --oneline -1 origin/main`
→ `4d9fe1d skills: add doc-id-migration-run, capture W37-6 learnings`, fetched this session
into worktree `agent-a2df68e96672cbc56`, `git status --short` empty at branch creation. Every
count below was run at this tree unless another is named. Clock: `TZ=Europe/London date` in
this session → `2026-09-18 00:57:56 BST`.

**Role and authority.** Written by the planner (`.claude/roles/planner.md`). Per `CLAUDE.md`
§14 and §12 this is **a proposal and nothing else**: it edits no plan, no roadmap row and no
register row, it rules no decision point, and it binds nothing until the acceptance line at the
foot carries a date. The four §13 verdicts on W37-6's unevidenced items are the lead's, not
this document's; where a verdict is referred to below it is cited as the lead's, never restated
as this review's.

**Trigger.** `.claude/skills/phase-review` §"When" — **at each workstream close**. W37-6's run
merged to `main` in four PRs (`#784`→`0651c1e`, `#782`→`71f5a22`, `#785`→`1cd489c`,
`#783`→`4d9fe1d`) and its checkpoint-3 close is being cut now. This is the first of the two
fixed triggers; review 12 (`CR-1050`) was the off-trigger mid-window one it names in its own
preamble (`docs/closures/CR-01050-plan-review-12-the-w37-6-w37-11-boundary-mid-window.md:19-30`).

---

## Scope

**What this review audits: the plan, not the workstream.** `CLAUDE.md` §13 audits one
workstream against its own scope — that is the auditor's checkpoint-3 report and the lead's
close record. §14 audits **whether the plan still says the right thing** now that W37-6's run
is real. The scope is therefore derived from the plan, not from what was built:

- **The map plan `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`** — the
  sequencing table at `:365-383` and the five slice sections W37-7 (`:735`), W37-8 (`:760`),
  W37-9 (`:785`), W37-10 (`:815`) and W37-11 (`:839`), each read as written and tested against
  what the run produced.
- **`.claude/skills/phase-review`'s five questions in their fixed order**, each with a written
  answer including "no change".
- **Every `docs/findings/register.md` row that has decayed to this review**, generated rather
  than recalled, each with a disposition.
- **The open acceptance lines on the review sequence**, and the two dated decisions the lead
  made tonight, tested for whether the plan should absorb them.

**Out of scope, stated so the silence is not read as a finding:** the §13 verdicts on W37-6's
own requirements (the lead's), the Slice close itself (the lead's merge on a clean audit), the
Work close (the maintainer's, dated), and any edit to `docs/roadmap.md`, `docs/findings/register.md`
or any plan file — this review proposes and never applies.

## Evidence

## Two corrections to this review's own commissioning brief

Recorded rather than acted on, per the skill's "When a review gets its own premise wrong".

**Correction 1 — the brief's "#757's routing under CR-1050 §5's class line" is a citation the
lead built, not one CR-1050 contains.** `git grep -c '757' docs/closures/CR-01050-plan-review-12-the-w37-6-w37-11-boundary-mid-window.md`
returns nothing; CR-1050 is dated `2026-09-03` (`:7`) and PR #757 did not exist until
2026-09-17. What CR-1050 carries is the **class line** at `:226-236`, and the lead applied it.
The brief's phrasing reads as though CR-1050 routed #757; it did not, and the auditor's
checkpoint-3 report flags the same thing
(`/home/puzhenhao1989/gi-pricing-plan.local/handover/auditor-w37-6-cp3-report.md:309-319`).
The routing is sound; the citation shape is the defect, and it is the one
[`RFC-779`](../rfcs/RFC-00779-two-rules-for-reading-an-artifact-the-one-you-name-and-the-one-you-verify.md)'s second rule names — *verify the claim,
not just the citation*. **No finding filed: a brief is not a governed artifact** (CR-1050's own
handling of the same case, `:59-60`).

**Correction 2 — and this one supersedes a recommendation the brief asked me to carry forward.
Reviews 9, 10 and 11 are not pending. They were accepted by the maintainer on 2026-09-01.**

CR-1050 states at `:76-79`: *"**What has not happened is a maintainer acceptance date on
reviews 9, 10 or 11** — all three still read `pending` at this tree."* **This is false at
CR-1050's own base tree.** Verified three ways at `4d9fe1d`:

| Review | File | Dated acceptance line, quoted |
|---|---|---|
| 9 | `docs/closures/CR-00925-plan-review-9-at-wk-671-s-close.md:859-862` | *"**Maintainer acceptance: accepted as proposed, 2026-09-01 — dated together with reviews 10 and 11 under review 11's proposal 11.1.** The `_pending._` paragraph above is kept as the record of the pre-acceptance state"* |
| 10 | `docs/closures/CR-00926-plan-review-10-at-wk-671-s-second-close.md:314-316` | *"**Maintainer acceptance: accepted as proposed, 2026-09-01 — dated together with reviews 9 and 11 under review 11's proposal 11.1.** The `_pending._` sentence above is kept as the record"* |
| 11 | `docs/closures/CR-00932-plan-review-11-completing-the-review-sequence-at-wk-671-s-close-before-wk-672-opens.md:288-294` | *"**Maintainer acceptance: accepted as proposed, 2026-09-01 — dated together with reviews 9 and 10 under review 11's proposal 11.1.** … **Applied with the dating:** the eleven register rows behind this review now pass to their named owners"* |

And it was already true when CR-1050 was written. Three commands, run this session and pasted
with their output — the pre-migration path is what the historical revisions carry, so it appears
here as an exhibit, never as a live citation:

```
$ git log --format='%h %aI %s' -S'accepted as proposed, 2026-09-01' --all | tail -1
d95a997 2026-09-01T22:16:55+01:00 docs: apply the maintainer's 2026-09-01 acceptance batch — dated lines, two files (#552)

$ git merge-base --is-ancestor d95a997 198ea5d ; echo EXIT=$?
EXIT=0

$ git show 198ea5d:docs/audit/plan-reviews.md | grep -c 'accepted as proposed, 2026-09-01'
3
```

`d95a997` **is** an ancestor of CR-1050's own base tree `198ea5d`, and the file CR-1050 was
reading already carried all three dated lines, two days before it was written.

**The mechanism, because it will recur.** Each of the three files keeps its pre-acceptance
`**Maintainer acceptance:** _pending._` paragraph deliberately — *"kept as the record of the
pre-acceptance state"* — and the dated line lands **below** it as a blockquote. A grep for
`pending` hits the kept record and stops; the superseding line is two to six lines further
down. This is [`RFC-777`](../rfcs/RFC-00777-a-reference-that-resolves-only-in-the-writer-s-context.md)'s class seen
from the other side: a locator that resolves, over content that says the opposite of the claim.
The auditor's checkpoint-3 report carries the error forward at `:321-328` ("Four `pending` plan-
review acceptance lines (9, 10, 11, 12) are open simultaneously"), sourced to CR-1050 rather
than re-read — the relay, not the reading, is where it propagated.

**Consequence for this review's ask (3).** The brief instructed me to "carry forward the
recommendation from CR-1050" that the maintainer date reviews 9-11. **I do not carry it
forward. It is discharged, and repeating it would put a third document's weight behind a
claim the repository falsifies.** The ask that remains is one line, not four — see
§"The acceptance lines actually open" below.

---

## Register rows decayed to this review

`python3 scripts/register-owed.py review`, run at this tree, header pasted:

```
Generated by `python3 scripts/register-owed.py review` against `4d9fe1d (`worktree-agent-a2df68e96672cbc56`)`.
Mode: review (rows naming the CLAUDE.md §14 plan review). 23 owed row(s), 1 matched but excluded as opening with a resolution marker
```

**23 owed rows, enumerated** (ids taken from the run's own output, not recalled): `FR-240`
(`F-W9-3`), F27, F29, F31, F33, F48, F58, F61, F63, F74, F75, F86, F87, F88, F89, F90, F91,
F92, F93, F94, F96, **F97, F101**.

Twenty-one of these are exactly review 12's set (`CR-1050:66-98`). Per the skill's own rule —
*"if a fresh audit has just covered this, say so and move on"* — **the eleven predating rows
(`FR-240`, F27, F29, F31, F33, F48, F58, F61, F63, F74, F75) take no new disposition here**:
review 11's dated acceptance (`CR-932:288-294`) passed them to their named owners on
2026-09-01, and Correction 2 above is what makes that statement available. The ten WK-697 rows
(F86-F96) carry review 12's dispositions, which are pending acceptance, not absent.

**Two rows are new since review 12 and are disposed here**, which is the whole of this section's
own work:

| Row | Register text (quoted from the run) | Disposition |
|---|---|---|
| **F97** — *"A session ends leaving the shared checkout in a state its successor cannot fast-forward, and nothing announces it"* (work item `W37-6`, phase 2) | *"**carry forward, unowned-pending-authorisation** — the remedy touches `.claude/roles/lead.md`, whose amendment is the maintainer's (`CLAUDE.md` §12). Two shapes named, neither chosen … Absent an owner, decays to the next `CLAUDE.md` §14 plan review"* | **Carry forward with a named event, not unowned.** This review does not choose between the two shapes — choosing would be the "not decided here, decided anyway" pattern the skill warns against, and the row's own text says the remedy is a **charter** edit, which is `W37-8`'s slice and DP-6's maintainer gate by the map plan (`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md:760-785`). **Recommendation: route F97 to W37-8 as a disclosed candidate, not as scope** — W37-8's acceptance is charter *headers and §1.6 role content*, and a new behavioural clause in `lead.md` is a different kind of change that needs its own maintainer line. Named event: **W37-8's PR**, at which it is either drafted with the charter or explicitly declined with a date. |
| **F101** — *"A guard disarmed by the very event it was written to survive"* (work item `W37-6`, phase 2) | *"**carry forward, unowned** — two remedies named, neither chosen: a non-zero assertion on row (i)'s H-row count …, or exempting `_NT0019_PATH` from citation rewrite the way `was:` is exempted … Absent an owner, decays to the next `CLAUDE.md` §14 plan review"* | **Limb 2 appears discharged by the run; the row's text has not caught up.** `CR-01063-w37-6-run-2-the-closure-g-record.md`'s class-E disposition, quoted: *"id-pattern re-measured on the flattened form (226 members); `_NT0019_PATH` restored + marked. Loop 1."* That is the row's second named remedy, landed. **Limb 1 — the non-zero assertion on row (i)'s H-row count — is not evidenced anywhere**, and row (i) is itself the one RFC-937 §7 item the auditor could not walk (`auditor-w37-6-cp3-report.md:104`: *"(i) … 'every H row in §5 closed by a named commit' — not walked row-by-row by either session"*). **Recommendation: split the row. Limb 2 → discharged, cited to `CR-1063` class E, the register cell updated by the auditor (this review does not edit the register — `planner.md` does not own it). Limb 1 → W37-11, where (i)'s H-row table is that slice's own deliverable** (map plan `:849-853`). Filing it there is the only place a "count read zero and nobody noticed" guard has a consumer. |

**One row matched and was excluded as opening with a resolution marker** — the generator's own
line, unchanged from review 12's handling. Not re-verified here; out of scope, same as
CR-1050:66-68.

---

## 1. Completion — derived, never recalled

**`scope-audit.py` cannot answer this and reads zero by construction.** WK-697 is a
documentation-corpus migration, not a spec module; `scope-audit.py`'s axis is
`OVR, DATA, MODEL, RATE, OPT, MON, GOV, PLAT`. The auditor ran both forms and pasted the output
(`auditor-w37-6-cp3-report.md:127-138`):

```
$ uv run python scripts/scope-audit.py WK-697
  no requirements found for module 'WK-697'
EXIT:0
$ uv run python scripts/scope-audit.py W37-6
  no requirements found for module 'W37-6'
EXIT:0
```

**Neither run is a completion number** — `CLAUDE.md` §10's boundary-metric rule, stated in the
auditor's own words: *"**Do not cite either run as '0 gaps.'**"* This review does not re-derive
them; review 12 recorded the same non-applicability at `CR-1050:104-109` and nothing has
changed the axis.

**`req-coverage.py`** at this tree: **533 specified / 338 marked (63.4%)**, exit 0 — repository-
wide, unrelated to this slice, and cited only so the number is not mistaken for W37-6's.

**The derivable completion measure is RFC-937 §7's eleven acceptance items against the leaf
plan's 14-item Acceptance Standard**, and the auditor derived it
(`auditor-w37-6-cp3-report.md:92-105`). Restated as a count, not re-run — the skill's *"If a
fresh audit has just covered this, say so and move on"*:

- **(a) (b) (c) (e)** — evidenced by fresh runs this session. `doc-id.py check --classify` →
  489 total, no `none` row, `git ls-files docs/ | wc -l` → 489, **equal**; `doc-id.py check`
  exit 0, "0 file(s) skipped"; `doc-index.py --check` "OK (byte-stable)" with
  `git status --porcelain docs/INDEX.md` empty; check 32 clean with
  `tests/test_audit_docs_check_32_disposition.py` 5/5.
- **(d) (f)** — evidenced through the standing verify table, not an independent re-count.
- **(g)** — **the one standing FAIL**, `scripts/_docverify.py:3788`
  (`"g": FAIL, # the token-boundary defect — RL-1043 §2 row 1`).
- **(h)** — CI green on the measurement tree itself; the full local gate was **not** re-run by
  the auditor (`mypy`, full `pytest -q`, the pnpm suite, `generate-contracts.py --check`).
- **(i)** — not walked row by row by anyone.
- **(j) (k)** — **W37-11's, not W37-6's**, per the map plan `:839-845`.

**Whole-row verdict counts** (`_docverify.EXPECTED_VERDICTS`, `scripts/_docverify.py:3515-3835`,
read by the auditor by symbol at this tree, corroborated by `CR-1063` §1's own pasted log):
**8 PASS, 15 DISCLOSE, 1 FAIL, 24 rows**.

**Answer: W37-6 is complete against every §7 item its own slice owns except (g), which is a
disclosed, measured, standing FAIL, and (i), which nobody has walked.** The verdicts on both
are the lead's; the lead has stated them (`to-deputy.md`, 2026-09-18 00:55:09 BST relay: *"(g)
deferred → W37-11 with #757 first"*, *"11, 13, 14, §7(i) re-measured before the cut"*). **This
review's only completion finding is that (i) has no measurement at all** — not a disagreement
with the verdict, a note that the verdict on (i) is owed a re-measure before the record is cut,
exactly as the lead's own line says.

**The retry counters `.claude/skills/phase-review` §Output requires do not exist at this tree.**
`python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py show` returns an
object whose top-level keys are, pasted from the run:

```
KEYS ['schema', 'schema_version', 'project', 'position', 'in_flight_expensive_verifications', 'in_flight_expensive_verifications_live']
```

No `replan`/`fix` retry entry at any layer. The skill's own `Verified` note anticipated this:
*"Not yet exercised by a real review — no phase-level review has run since C2 existed to
populate the counters."* **Answer: no counter data; nothing to cite; this is the first review to
try and the skill's clause is now exercised and found empty.** Recorded, not fixed.

---

## 2. Omission — what would nobody notice was missing?

Three, all found by reading rather than relayed.

**2a. The roadmap row says the run has not happened.** `docs/roadmap.md:766`, the WK-697
narrative, contains verbatim (`sed -n '766p' docs/roadmap.md`):

```
W37-6 has not run and its go-ahead has not been asked for
```

and `grep -c '71f5a22\|CR-1063' docs/roadmap.md` returns **0** — no line in the file cites the
merge tree or the run's record. Review 12 found this row stale (`CR-1050:166-169`) fifteen days
ago; it is now stale **across a completed, irreversible, one-way corpus migration**. A reader
holding only `docs/roadmap.md` — which `CLAUDE.md` §0 makes the authority on status — believes
the migration is unstarted. **Not this review's to fix**: the map plan assigns it explicitly,
`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md:863`, verbatim:

> `## Proposal — the roadmap row (the lead's to apply; not written by this plan)`

**Recommendation: the row is rewritten in the same PR as the close record**, which is what the
lead's 00:55:09 BST relay already commits to. This review adds one requirement to that rewrite:
**it must cite the four merge SHAs and `CR-1063` by id**, because the row's current last
sentence dates itself to a *"throwaway snapshot"* dry run of 2026-09-02, and a rewrite that does
not name the real trees will be indistinguishable from the last one in three days' time.

**2b. The run's own new disclosures are filed nowhere the register can see.** Four items —
the idempotence gap, the three census rows' shrink, the check-35 output shape, the
`_h1_residue_by_file` docstring/implementation mismatch — exist only in `CR-1063` §§3-6 and the
squash-commit body. None is a `docs/findings/register.md` row. The consequence is mechanical:
`register-owed.py` keys off register rows, so when W37-11 opens and someone runs
`register-owed.py W37-11`, **none of the four will surface**. The worst of the four is the
idempotence item, because it is tracked under a label that collides with a real row: `CR-1063`
§5 quotes the channel shorthand verbatim as an exhibit — the second half of the pair does not
resolve in `docs/INDEX.md`, which is half the finding:

```
the F28/FD-1069 idempotence gap stays W37-11's
```

and F28 in
`docs/findings/register.md` is the unrelated RFC-840/841 adoption-pilot finding. **The label
resolves to the wrong row.** **Recommendation: file all four as register rows before W37-11's
first task is delegated**, the idempotence one under a fresh `F`-id with the "F28" shorthand
explicitly retired in the same edit. This is the auditor's flag
(`auditor-w37-6-cp3-report.md:289-294`) and this review endorses it as **blocking W37-11's
scope being derivable at all**, not as tidiness.

**2c. Artifact B's position block is stale and both its locators now dangle.**
`write_runtime_state.py show`, pasted:

```
"written_at": "2026-09-03T21:25:20Z",
"work":  {"value": "W37", "read_from": "docs/roadmap.md §7 row 382"},
"slice": {"value": "W37-6", "read_from": "docs/plans/2026-09-02-w37-6-migration-run-leaf-plan-v2.md"}
```

Checked at this tree, both commands pasted with their output — the dangling locator is an
exhibit, not a live path:

```
$ ls docs/plans/2026-09-02-w37-6-migration-run-leaf-plan-v2.md
ls: cannot access 'docs/plans/2026-09-02-w37-6-migration-run-leaf-plan-v2.md': No such file or directory

$ sed -n '382p' docs/roadmap.md
## Historical record
```

The migration renamed that plan to `docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md`,
and roadmap line 382 is a heading, not a work row. **This is the migration's own predictable
after-effect on a file nobody migrated** — artifact B is JSON state, outside `docs/`, so
`doc-id.py migrate`'s sweep never touched its embedded paths, and `audit-docs.py`'s checks do
not read it. F91 already names the staleness (`written_at` cannot say so); **what no row names
is that the `read_from` locators are now wrong, which is the harder half**: a stale timestamp is
visible, a dangling locator inside a JSON string is not. **Recommendation: a W37-7 item** —
W37-7 is "the remaining creating and reading instruments" (map plan `:735`), and
`write_runtime_state.py` is one. This is an **addition to W37-7's scope**, and it is the only
scope addition this review proposes.

---

## 3. Skills and research — the gap analysis

**Run as a currency check on what this window changed, not as an append.**

`HEAD` itself is a skills commit — `4d9fe1d skills: add doc-id-migration-run, capture W37-6
learnings`. That is the right direction: `CLAUDE.md` §12's *"Discovered a non-obvious procedure
…? Write or update a skill … commit both with the work"* discharged in the same window as the
work.

**One skill is behind the code, and it is this one.** `.claude/skills/phase-review/SKILL.md`'s
§Output clause requires citing RFC-895 artifact B's retry counters. §1 above shows the field
does not exist. The skill's own `Verified` block says it was never exercised. **Recommendation:
the clause is not wrong, it is unmet — amend it to say what a review writes when the counters
are absent** (this document's §1 paragraph is the shape), and refresh the `Verified` date in
the same commit per `CLAUDE.md` §12. **Owner: the planner** — `planner.md` explicitly permits
creating or updating a skill. **Not done in this PR**, because a review that edits its own
governing skill in the act of running it makes the record of which version it ran under
unreadable. Filed as a proposal here; the edit is a separate commit after acceptance.

**One skill is ahead of the code in the direction §14 exists to catch.** `close-workstream` is
W37-11's named executor skill (map plan `:371-383`), and its own description says it audits
*"one workstream against its own scope"*. Review 12 already named this
(`CR-1050:152-162`) — W37-11's charter is `(j)`, `(k)` and synthesis, which is narrower than
what is accumulating against the name. **The finding has not moved; §5 below is where it is
answered, not here.** Naming it once is enough, as review 12 said.

**No skill claims coverage it does not have on this window's evidence.** `phase-review`,
`writing-plans`, `close-workstream` and the CR template were read fresh for this review and
matched what they describe, except the one clause above. **No external skill installed; none
proposed.**

---

## 4. Document drift

**4a. The roadmap.** §2a above. Largest single instance; the lead's to apply.

**4b. `PL-1058:37-38` and `CLAUDE.md:283` contradict each other, and the contradiction has been
ruled.** The ledger's checkpoint-3 definition (`docs/plans/PL-01058-w37-6-migration-run-ledger.md:37-38`)
reads: *"**Checkpoint 3**: the slice closes per `.claude/skills/close-workstream`'s checklist —
every requirement evidenced or verdicted, NFRs measured not asserted, **the maintainer's dated
acceptance line recorded**."* `CLAUDE.md:283` reads that a Slice *"closes on a clean audit and
the lead's merge"* with no maintainer line. The deputy ruled it at 2026-09-18 00:55:09 BST
(`to-lead.md`): *"A ledger entry cannot add a requirement CLAUDE.md does not impose (§12: an
amendment to what CLAUDE.md requires is the maintainer's; a ledger is not that) … the line names
the review's acceptance line, which stays pending for the maintainer — not a gate on the
Slice."* **This review records the resolution rather than re-opening it**, and notes only that
the ruled correction — *"amend `PL-1058:37-38` by a dated correction that quotes the superseded
words and cites `CLAUDE.md:283`"* — **is owed inside the close PR and is not yet in the tree**
(`grep 'CLAUDE.md:283' docs/plans/PL-1058-*.md` finds nothing at `4d9fe1d`). Listed so it is
not lost between the ruling and the merge.

**4c. F92's owner and count disagree across three artifacts, and the plan is one of them.** The
auditor's measurement (`auditor-w37-6-cp3-report.md:262-267`): the register says **W37-11 / 53**;
live `audit-docs.py` check 35 prints *"50 owner check(s) deferred (owner: **W37-10**, RL-1046
§B — F92's stamp-deferred population)"*; the original assignment was W37-6. `CR-1063` §7's
class-A row gives the arithmetic for the smaller number, quoted: *"50 = 46+7 − 3 vendored
SKILL.md under F88's HeaderError gap"*. **Three owner tags, two counts, one item.** The lead has
ruled the reconciliation (00:55:09 BST relay: *"F92's owner of record W37-11 with the 'W37-10'
code tag recorded for W37-7/8 to align and the count 50 (53 struck, dated)"*). **This review
adds one thing the ruling does not cover: the `W37-10` string is a literal inside
`scripts/audit-docs.py`'s check-35 output, so aligning it is a code edit in a slice that does
not exist yet.** W37-10's scope (map plan `:815-838`) is `docs/` READMEs, checklists and the
three rituals — **a check-35 owner-tag correction is not in it**. **Recommendation: the tag
alignment is W37-7's** (instruments), named in W37-7's leaf plan when drafted, not left as "for
W37-7/8 to align" without a row.

**4d. F87 and F90's register cells still read "fix before close, W37-6" against evidence the
fix landed.** `docs/findings/register.md:125` (F87) and F90's cell, per the auditor's direct
read (`auditor-w37-6-cp3-report.md:240-254`). For F87 the run's own check-35 output (445 in
scope, 66 exempt, 50 deferred) is consistent with the widening having landed; for F90 review 12
already disposed it *"No change — already ruled at the right authority level (maintainer, via
D1/D2), already re-measured"* (`CR-1050:93`). **Neither cell has been updated.** This review
does not edit the register (`planner.md` does not own it). **Recommendation: the auditor's next
touch updates both cells with the citation**, exactly as review 12 recommended for F95
(`CR-1050:171-177`) — and this is the *second* review making that recommendation about the
register, which is itself the finding: a register cell that no role's charter puts on a
schedule goes stale by default.

**4e. Specs.** §14 makes the specification the main target. **No spec drift found, and the
reason is structural, not lucky**: WK-697 touches `docs/specs/` only through citation rewriting,
and `python3 scripts/audit-docs.py` exits 0 at this tree with *"533 requirements defined across
8 specs"* and *"119 of 119 §10 mirror rows carry their register status"*. **No requirement id
was minted, renumbered or superseded by this run.** Answer: **no change.**

---

## 5. Shape — is the W37-7…11 cut still right?

**Answer: yes. No slice moves, no id changes, no new slice. The eleven-slice cut survives its
hardest slice.** What follows is the evidence for that, item by item, because "no change" with
no working is the answer the skill says is indistinguishable from a question nobody asked.

**The boundary findings W37-6's run produced, each tested against the W37-7…11 slices as
written at `PL-939:735-862`:**

| # | Finding from the run | Evidence | Does it change a later slice's cut, scope or requirement set? | Recommendation |
|---|---|---|---|---|
| 1 | **The venv-sweep incident and the enumeration fix** — the sweep walked `root.rglob("*")` and wrote into a checkout's synced `.venv`, corrupting one inode (410131, 40 hardlinks) at `2026-09-17 13:43:54Z`; fixed by `_enumerate_tree(root)` using `git ls-files -z --cached --others --exclude-standard` | `CR-1063` §1, quoting `~/.claude/jobs/137a6dcd/tmp/migrate-T-prime.log:432-434` and the certifi `cacert.pem` block-12 diff; two tests, module `297 → 299`, `299 passed in 74.10s` | **No.** The fix is inside `doc-id.py`, merged, and proven both directions (negative: `test_sweep_never_reaches_a_gitignored_path`; positive control: `test_sweep_still_reaches_an_untracked_unignored_path`, both 2/2 at this tree per the auditor). No W37-7…11 slice's scope depends on it | **No change.** One note for W37-7: the mechanism is **exclusion by construction, not a guard** — the auditor's words, *"No literal refusal guard exists"* (`:232`). W37-7's `dev-commands` row should say so, because a reader looking for a refusal will not find one and may add a redundant one |
| 2 | **The CI verify on a migrated checkout** — `--ref HEAD` resolved to GitHub's PR merge ref (the already-migrated tree), producing `SET CHANGE (9): 9 fatal row(s)` and exit 3 on run `35261236904`/head `323b523`; fixed in `.github/workflows/docs.yml` by branching on `audit-docs.py`'s `migrated_tree()` sentinel | `CR-1063` §2, the `SET CHANGE (9)` block quoted in full; post-fix green on `f777159` and on `main`@`71f5a22` (`docs` run `35268549620`, `completed/success`) | **No — but it creates a standing obligation W37-11 already holds.** The fix pins `--ref` to `core.json`'s `meta.verified_against_tree` = `0651c1e` | **No change to the cut.** The obligation is item 3 below |
| 3 | **The pinned-base read of the W37-11 record** — `.github/workflows/docs.yml:117` resolves `--ref` to the pinned base and `scripts/_docverify.py:4333` loads the record from `snap.control`, so **a record edit made on `main` is invisible to the standing CI verify, forever** | `CR-1063` §3, quoted: *"the standing CI verify reads the W37-11 record **at the pinned base, forever** … until W37-11 decides where the standing check reads the record from post-migration (the control tree, for the run's own hermeticity, versus the live tree, for a standing check that should see later record edits). **Owner: lead, W37-11.**"* | **It changes W37-11's requirement set, not its cut.** W37-11's scope as written (`PL-939:839-853`) is `(j)`, `(k)` and the synthesising closure record. **This is a design decision with two named options and no default** — precisely the shape `CLAUDE.md` §10 says goes to `docs/open-questions.md` rather than being picked silently | **Add one requirement to W37-11's leaf plan, and raise the choice as an open question.** It is not synthesis and it is not `(j)`/`(k)`; it is a decision W37-11 must make before its own acceptance can mean anything, because until it is made the three census rows measured at 0 will print `PROGRESSED` on every CI run indefinitely. **Recommendation: raise it in `docs/open-questions.md` with the two options CR-1063 names and a recommendation, at W37-11's leaf-plan drafting** — the review does not choose |
| 4 | **The idempotence gap, `PL-960:909`** — *"Prove idempotence on the real tree: a second `migrate` run produces zero diff"*, still `- [ ]`. Determinism of a *first* run is proven (T⁗ and T⁵ both `6d058ba642481404815ab573e848a8cf34e671ee`); the literal second-run-over-migrated-output proof was not run | `CR-1063` §5; starting figure `REGRESSION (residue exceeds W37-11 ceiling): 'scripts/doc-id.py' (d10) — 41 hit(s) exceeds the W37-11 record's ceiling of 15 for 'd10'` (`handover/team2-ci-docs-323b523.log:1239`) | **It adds to W37-11's requirement set.** The carry is already stated in the squash commit — *"The idempotence item PL-960:909 carries to W37-11 with this incident's numbers"* — so the destination is settled; what is not settled is that it has **no register row and a colliding label** (§2b) | **Endorse the carry. Require the filing.** W37-11's leaf plan names it as an item with `PL-960:909` as its source and the `41 / ceiling 15` figure as its starting measurement. **Determinism ≠ idempotence** and the leaf plan must say which it is discharging — two runs agreeing from the same base is not a second run over the output |
| 5 | **Row (g)'s standing FAIL, with g2 = 251 classified-by-none, and #757 as W37-11's first item** | `CR-1063` §6: g1 reads `0 / 0 / 0` clean; g2 `classified-by-none=251` of 971 classified files, broken down by eight causes summing to 251 (136+34+28+16+13+11+7+6). `scripts/_docverify.py:3788` `"g": FAIL`. Ledger `:1955-2001`: #757 is 5 ahead / 13 behind `71f5a22` with content conflicts in the W37-11 record and `scripts/_docverify.py` (the ledger's own `merge-tree` exhibit at `:1955-2001` names both paths) | **It does not change the cut, and this is the load-bearing judgement of this review.** Row (g) is an **RFC-937 §7 acceptance item W37-6 owns and did not meet.** Deferring it to W37-11 is a §13 "deferred with an owner" verdict — legitimate, the lead's, and dated — **but it puts a corpus-measurement item into a slice whose charter is synthesis**, which is exactly the drift review 12 named at `CR-1050:226-238` | **Endorse the deferral, and write the guard review 12 asked for.** The deferral is right on its merits: g1 is clean, g2's residue is **fully measured and cause-attributed**, and #757 is the instrument change that reduces it. **But W37-11's leaf plan must state (g) as a first-class acceptance item with its own exit measurement (`classified-by-none` at a named tree, against 251 at `4d9fe1d`), not as a line in a synthesis narrative.** Without that, `close-workstream` — W37-11's executor skill — audits a scope its own charter does not describe, which is question 3's finding arriving as a real defect |

**On the two smells the skill names.** Neither is present. No W37-7…11 row has grown to span
incommensurable kinds — the four Stage 3 slices are cut by *artifact class* (instruments,
charters, root governance, `docs/` scaffolding), which is the cut that survives audit. And no
phase exit criterion is unmeetable: W37-11's acceptance
(`PL-939:855-857`) is *"every item of this plan's Acceptance Standard has a recorded result;
the maintainer has accepted the Work close with a dated line"* — both achievable, the second
outside the team's control by design.

**The one thing that did change, and it is a routing rule, not a cut.** Review 12 recommended
(`CR-1050:226-238`) that corpus-correctness defects go to W37-6 fix-before-close and
design-shaped items stay W37-11's, *"not a re-cut"*. The real run then routed to W37-11: row
(g), the idempotence gap, the three census rows, the docstring mismatch, the check-35 shape and
#757. **Is that consistent with review 12's line?** The auditor flagged it as an open question
(`auditor-w37-6-cp3-report.md:330-337`). **This review answers it: yes for all six, but only
because W37-6's window closed.** Review 12's line was written mid-window, when
"fix-before-close" was a live option. It is not any more — W37-6's merge is one-way and done.
**The line is therefore not violated; it is spent**, and continuing to cite it as the test for
post-merge items would be [`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md)'s mechanism applied
to a rule. **Recommendation: review 12's §5 routing principle is recorded as discharged at
W37-6's merge, and its successor rule — the one that governs from here — is written into
W37-11's leaf plan instead: an item carried to W37-11 is either (j)/(k), synthesis, or a named
acceptance item with its own exit measurement. Nothing else is carried there.** That is a
narrowing of practice back onto the map plan's line, not a re-cut, and it is the same
conclusion review 12 reached by a route that has since expired.

---

## The lead's dated decisions tonight — should the plan absorb them?

Two, read directly from `/home/puzhenhao1989/gi-pricing-plan.local/channel/to-deputy.md` with
`grep -n`.

**Decision 1 — the plan-of-record, `to-deputy.md:11020`, 2026-09-18 00:40:49 BST.** A four-stage
schedule with BST windows: S2 close `00:47–05:00` → S3 `05:00–13:30` → S4 `13:30–16:30` → W37
END `16:30–18:30 BST, 18 Sep`, each conditional on the maintainer's dated lines for W37-8,
W37-9 and the Work close. It cites the map plan's slice sections and `PL-1058:41`'s staging
constraint.

**Should the plan absorb it? No — and deliberately.** The map plan
(`PL-939:371-383`) carries **dependencies and parallelism**, not clock windows. A schedule is
a state that moves; `CLAUDE.md` §9 and [`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md) put
moving state in one place, and the lead's own `eta.md` plus the channel entry already are that
place. Writing `16:30–18:30 BST, 18 Sep` into a frozen plan creates a second copy that goes
stale within hours of the first slip. **Recommendation: the plan absorbs nothing from it. The
one durable fragment — that W37-7…W37-10 may run beside each other and all depend on W37-6 — is
already at `PL-939:377-381` and needs no edit.**

**Decision 2 — #757 → W37-11, `to-deputy.md:11044`, 2026-09-18 00:42:46 BST.** Quoted
verbatim: *"**DATED DECISION (lead, 2026-09-18 00:42 BST): PR #757 is routed to W37-11 — the
first W37-11 item — not a W37-6 fix-before-close item.** Test applied: CR-1050 §5's class line
… #757 changes how row (g)'s g2 residue is *classified* … not what the migrated corpus *is*;
its re-measure on the settled tree runs now and the decision stands unless that re-measure shows
a corpus-correctness defect (then it moves to W37-6 and checkpoint 3 waits on it)."*

**Should the plan absorb it? Yes — one sentence, into W37-11's leaf plan when it is drafted, not
into the map plan.** Three reasons. The decision is **correctly reasoned**: the deputy
independently reached it (`to-lead.md`, 2026-09-18 00:41:53 BST: *"it changes the verify
instrument's g2 classifier … not the corpus's compliance — by that line it is W37-11's"*), and
the ledger recorded it before either (`PL-1058`, `## 2026-09-17 21:12 BST — #757 recorded as
the first W37-11 item`). It is **conditional and the condition is live** — "unless that
re-measure shows a corpus-correctness defect" — so it must be written where the condition can be
discharged, which is W37-11's plan, not the map plan's frozen slice text. And the map plan is a
**frozen dated file** (`CLAUDE.md` §2): a filed plan is frozen at its date, and a
2026-09-18 decision does not get retro-written into a plan filed earlier. **Recommendation:
W37-11's leaf plan names #757 as its first item, carries the lead's dated decision by citation
(`to-deputy.md:11044`), and states the open condition explicitly so the re-measure has somewhere
to land.**

**One caution on Decision 2's own citation, for the record.** It cites *"CR-1050 §5's class
line (`…CR-1050…:226–236`, read at origin/main)"* — and that is **correct**; the line is there
and says what the decision quotes. Correction 1 above is about the *brief's* phrasing, not the
lead's. The lead's entry is the more careful of the two, and its own note — *"Citations
corrected from the plan-of-record entry: the staging rule is `to-lead.md:748` … not
delivery-process.md"* — is a correction made in the right direction, named and dated.

---

## The acceptance lines actually open

**One, not four.** Correction 2 establishes reviews 9, 10 and 11 were accepted 2026-09-01 in
`d95a997` (#552). What remains:

| Review | File:line | State |
|---|---|---|
| 12 | `docs/closures/CR-01050-plan-review-12-the-w37-6-w37-11-boundary-mid-window.md:284` | `**Maintainer acceptance:** _pending_` — **open, 15 days, spanning the run its recommendations were about** |
| 13 | this document, foot | `_pending_` — filed now |

**Ask to the maintainer, stated plainly:**

1. **Date CR-1050 (review 12), or state it is superseded.** Its §5 routing principle was cited
   as the governing test for a real, dated decision tonight (`to-deputy.md:11044`) while the
   document carrying it has never been accepted. **Whichever way it goes, this review recommends
   the accompanying note that §5's principle is spent at W37-6's merge** (§5 above) — accepting
   it as a live rule fifteen days after the window it governed has closed would bind the wrong
   thing.
2. **Date this review (13), or reject it.** Nothing in it binds until then, including the two
   scope recommendations (§2c's W37-7 addition, §5 row 3's W37-11 requirement) that Stage 3's
   leaf plans are told to reconcile against.
3. **The carried-forward recommendation to date reviews 9-11 is withdrawn, not left open** —
   it was discharged on 2026-09-01 and CR-1050 read it wrong. No action is asked for on those
   three.

**What this review does not ask for.** No maintainer line on W37-6's Slice close.
`CLAUDE.md:283` and the deputy's 00:55:09 BST ruling both put that with the lead's merge on a
clean audit. The Work (WK-697) close is the maintainer's, dated, and is not this document.

---

## What Stage 3's leaf-plan drafts must reconcile against

The deputy permitted Stage 3 leaf-plan drafting from 02:30 BST under four conditions
(`to-lead.md`, 2026-09-18 00:41:53 BST), the second being: *"(b) each draft is filed **undated**
with a mandatory section **'Reconciled against plan review 13'** left empty, completed and the
plan dated only after review 13 is filed — the close may change what the leaf plans build
against, and a draft that skips that section is not a plan."*

**This review is now filed. Here is the closed list that section must answer, one line each.
Nothing outside this list is owed to review 13**, so a drafter can discharge the section and
know they are done:

| For | Item this review produced | What the draft's section must say |
|---|---|---|
| **W37-7** (instruments) | **§2c** — `write_runtime_state.py`'s `position` block is stale and both its `read_from` locators dangle post-migration (the dated-form leaf-plan path it names no longer exists; `docs/roadmap.md:382` is `## Historical record`) | Whether W37-7 takes it. **This review recommends yes** — it is a reading instrument, which is W37-7's own definition. If declined, say so with a reason and a named event |
| **W37-7** | **§4c** — check-35's `W37-10` owner literal for F92 must align to the owner of record; W37-10's scope does not contain code | Whether W37-7 takes the tag alignment, or names the slice that does |
| **W37-7** | **§5 row 1** — the venv fix is exclusion-by-construction, **not a refusal guard** | That the `dev-commands` / `doc-id-migration-run` text says so, so no redundant guard is proposed |
| **W37-8** (charters) | **F97's disposition** — remedy touches `.claude/roles/lead.md`, a maintainer amendment under DP-6 | Whether F97 is drafted alongside the charter headers or explicitly declined with a date. **This review recommends disclosed candidate, not scope** |
| **W37-9** (root governance) | **Nothing.** §4e found no spec drift and this run minted no requirement id | *"No item from review 13 bears on this slice"* — stated, not omitted |
| **W37-10** (`docs/` scaffolding) | **§4d** — the F87/F90 register cells are stale, and no role's charter puts register-cell currency on a schedule | Whether the checklists W37-10 rewrites gain a register-currency line. Recommended, not required |
| **W37-11** (prove it) | **§5 row 3** — the pinned-base read: a record edit on `main` is invisible to the standing CI verify, forever. Two options, no default | That it is raised in `docs/open-questions.md` with both options and a recommendation, **before** W37-11's acceptance is written |
| **W37-11** | **§5 row 4** — the idempotence gap `PL-960:909`, starting figure `41 hit(s) … ceiling of 15 for 'd10'` | That the plan states **which** property it discharges — determinism is already proven, idempotence is not — and names the register row filed for it (§2b) |
| **W37-11** | **§5 row 5** — row (g) as a first-class acceptance item with its own exit measurement against `classified-by-none = 251` at `4d9fe1d`, and #757 as its first task carrying the lead's dated condition | That (g) appears in the Acceptance Standard, not only in the narrative |
| **W37-11** | **§5's closing recommendation** — the carry rule from here: `(j)`/`(k)`, synthesis, or a named acceptance item with its own exit measurement. Nothing else | That the plan states the rule it was cut against |
| **All four** | **§2b** — four run disclosures are filed in no register row, and the idempotence label collides with the real F28 | That each draft's scope was derived **after** the filing, or states that it was derived before and names the risk |

**A draft cannot complete that section by writing "reconciled".** Each row above names a
decision or a statement; the section is discharged row by row, and a row answered "declined"
with a reason is discharged. That is the §13 "silence is not a verdict" rule applied one level
down, to a plan instead of a requirement.

---

## Verdict

**The plan survives its hardest slice. No slice moves, no id changes, no new slice, and no
requirement id is minted, renumbered or superseded by this review.** Three slices gain
requirements (W37-7 one, W37-11 three) and one review-level routing rule is recorded as spent
and replaced. Every one of the five questions has a written answer above, "no change" included
(question 4's spec limb, and the map plan's cut under question 5).

**Nothing in this document binds until the acceptance line at its foot carries a date**
(`CLAUDE.md` §14). Until then the Stage 3 leaf-plan drafts reconcile against it as a proposal,
which is exactly what the deputy's condition (b) asks of them.

### Proposal summary

| # | Question | Finding | Recommendation |
|---|---|---|---|
| — | Brief correction 1 | "CR-1050 §5 routes #757" is not a citation CR-1050 contains; the class line at `:226-236` is, and the lead applied it correctly | No finding filed; the brief's phrasing noted so it is not repeated |
| — | Brief correction 2 | **Reviews 9, 10 and 11 were accepted 2026-09-01** (`d95a997`, #552), an ancestor of CR-1050's own base tree `198ea5d` where the file already carried three dated lines. CR-1050:76-79 is false and the auditor relayed it | **Withdraw the carried recommendation.** Only review 12's line is open |
| — | Register | 23 owed rows; 21 are review 12's set; **F97 and F101 are new** | F97 → W37-8 as disclosed candidate. F101 → split: limb 2 discharged by `CR-1063` class E, limb 1 → W37-11 with row (i) |
| 1 | Completion | `scope-audit.py` reads zero by construction, both forms. Against RFC-937 §7: (a)(b)(c)(e) freshly evidenced, (d)(f) by the standing table, **(g) standing FAIL**, (h) CI-green with the local gate not re-run, **(i) never walked**, (j)(k) W37-11's. Verdict rows 8 PASS / 15 DISCLOSE / 1 FAIL. **The skill's retry-counter clause has no data to cite — the field does not exist** | No completion number claimed from `scope-audit.py`. (i) is owed a re-measure before the record is cut. The `phase-review` skill's Output clause is amended to say what a review writes when the counters are absent |
| 2 | Omission | (a) the roadmap row still reads *"W37-6 has not run"* and cites no merge SHA; (b) four run disclosures exist in no register row, one under a label colliding with the real F28; (c) artifact B's `position` block is stale and both `read_from` locators now dangle | (a) rewritten with the close record, **citing the four SHAs and CR-1063 by id**; (b) all four filed before W37-11's first delegation, idempotence under a fresh id; (c) W37-7 — **the only scope addition this review proposes** |
| 3 | Skills | `phase-review` is behind the code (retry-counter clause unmet, never exercised); `close-workstream`'s charter is narrower than what is routed to W37-11 (review 12's standing finding, unmoved) | Amend `phase-review` in a separate commit after acceptance; `close-workstream` resolved by question 5's carry rule |
| 4 | Drift | Roadmap row; `PL-1058:37-38` vs `CLAUDE.md:283` ruled but the dated correction not yet in the tree; F92 three owners two counts; F87/F90 cells stale; **no spec drift, no requirement id touched** | Ledger correction lands in the close PR; F92's `W37-10` literal alignment → W37-7; register cells → the auditor's next touch |
| 5 | Shape | **The W37-7…11 cut holds. No slice moves, no id changes, no new slice.** Five boundary findings tested against `PL-939:735-862`: two change nothing, three add requirements to W37-11 without changing its cut | Add §2c to W37-7's scope; add the pinned-base decision, the idempotence item and row (g) to W37-11's requirement set; **record review 12's §5 routing principle as spent at W37-6's merge** and replace it with the carry rule above |

---

## Sources

Every item read directly at `4d9fe1d62328285ac0483b047c3959e39e0f5bd6` unless another tree is
named.

- `docs/closures/CR-01050-plan-review-12-the-w37-6-w37-11-boundary-mid-window.md` — read in
  full; lines `:7`, `:19-30`, `:66-98`, `:76-79`, `:104-109`, `:152-162`, `:166-177`, `:191-242`,
  `:226-238`, `:284`.
- `docs/closures/CR-01063-w37-6-run-2-the-closure-g-record.md` — §§1-7 and Verdict read
  directly.
- `docs/closures/CR-00925-plan-review-9-at-wk-671-s-close.md:859-862`,
  `docs/closures/CR-00926-plan-review-10-at-wk-671-s-second-close.md:314-316`,
  `docs/closures/CR-00932-plan-review-11-completing-the-review-sequence-at-wk-671-s-close-before-wk-672-opens.md:288-294` — the three
  dated acceptance lines, read directly.
- `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md:365-383` (sequencing),
  `:735-862` (W37-7…W37-11), `:863-870` (the roadmap-row proposal) — read directly.
- `docs/plans/PL-01058-w37-6-migration-run-ledger.md:30-45` (the three checkpoints and the
  go-ahead conditions), `:1955-2001` (the final entry, #757) — read directly.
- `docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md:909` — quoted via `CR-1063` §5,
  which read it directly.
- `docs/roadmap.md:766` — `sed -n '766p'`, the stale clause quoted verbatim;
  `grep -c '71f5a22\|CR-1063' docs/roadmap.md` → `0`; `sed -n '382p'` → `## Historical record`.
- `scripts/_docverify.py:3788` (`"g": FAIL`), `:3515-3835` (`EXPECTED_VERDICTS`, 8/15/1 over 24)
  — by symbol at this tree, read by the auditor and corroborated by `CR-1063` §1's logs.
- `/home/puzhenhao1989/gi-pricing-plan.local/handover/auditor-w37-6-cp3-report.md` — read in
  full; `:92-105`, `:104`, `:127-138`, `:232`, `:240-267`, `:289-294`, `:309-319`, `:321-328`,
  `:330-337`.
- `/home/puzhenhao1989/gi-pricing-plan.local/channel/to-deputy.md:11020` (plan-of-record,
  00:40:49 BST), `:11040` (00:41:18 correction), `:11044` (#757 decision, 00:42:46 BST) —
  `grep -n`, read directly.
- `/home/puzhenhao1989/gi-pricing-plan.local/channel/to-lead.md`, entries 2026-09-18 00:41:53
  BST (Stage 3 drafting, four conditions) and 00:55:09 BST (checkpoint-3 ruling) — read
  directly.
- `python3 scripts/register-owed.py review` → 23 owed, 1 excluded — run this session, header and
  the F97/F101 rows pasted above.
- `python3 scripts/req-coverage.py` → 533/338 (63.4%), exit 0 — run this session.
- `python3 scripts/doc-id.py next` → `1064`, exit 0 — run this session.
- `python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py show` — run this
  session; top-level keys pasted, no retry-counter field.
- The three git commands of Correction 2, pasted with their output in that section — run this
  session, establishing `d95a997` (#552) and its ancestry of `198ea5d`.
- `git log --oneline 0651c1e~30..origin/main` — run this session, for the four run PRs and the
  window's commit sequence.
- `.claude/skills/phase-review/SKILL.md`, `.claude/skills/writing-plans/SKILL.md`,
  `.claude/roles/planner.md`, `docs/_templates/CR.md`, `CLAUDE.md` §§0, 5, 9, 10, 12, 13, 14 —
  read in full for this review.

**Maintainer acceptance:** _pending_
