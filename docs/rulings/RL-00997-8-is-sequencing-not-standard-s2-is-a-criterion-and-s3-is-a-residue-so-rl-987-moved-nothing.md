---
id: RL-997
family: ruling
title: §8 is sequencing, not standard; S2 is a criterion and S3 is a residue, so RL-987 moved nothing
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-stage-boundary-authority-ruling.md
---

# Does moving population across a §8 stage boundary need the maintainer? Row 36, ruled (2026-09-02)

**What this is.** Register row 36 of
[`../plans/PL-00961-w37-6-everything-it-owns-before-the-run-one-list-with-each-item-s-state-and-what-discharges-it.md`](../plans/PL-00961-w37-6-everything-it-owns-before-the-run-one-list-with-each-item-s-state-and-what-discharges-it.md),
the one group-A item the lead declined to decide: *"The identifier standard's §8 assigns 'seven
charters, the eleven primary skills' to **S3**, after the migration. RL-987 pulls three
charters and several skills into **S2**, which is this commit. §8 is unamended."* Ruled below as
RL-997.

**The lead asked for options, trade-offs and a recommendation rather than a ruling, on the
condition that reading 2 is right — and reserved the ruling to the maintainer in that case.**
The derivation concludes **reading 1**, so it is ruled here; both readings are set out in full
with their evidence, because a conclusion that happens to enlarge the deciding role's own
authority should be readable by someone who wants to overturn it. **One item is routed to the
maintainer anyway**, and it is not the one row 36 expected.

**The short answer.** §8 is **not** part of the accepted standard, on the standard-bearing
document's own account: `docs/process/document-ids.md` is titled *"RFC-937 §1, lifted verbatim"*
and lifts §1.1 through §1.13 — not §4, §5, §7 or §8. And §8's own construction does not have a
boundary to move: **S2 is a criterion with an illustrative list, S3 is a residue.** RL-987
applied S2's stated criterion; it did not re-cut anything.

**The finding that settles reading 2's best argument.** §8 says *"the eleven primary skills"*.
§5.4 of the same note marks **six** rows `**primary**`. The word *"eleven"* appears exactly once
in RFC-937 — in §8 itself — with no support anywhere else in the note. **§8's enumeration was
already stale against its own §5 at filing**, which is what a shorthand looks like and not what a
binding population looks like.

## Authority

- **Routed by the lead** under the maintainer's delegation of 2026-09-01
  ([`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md)
  §1), with an explicit instruction not to decide alone if the answer is that this is an
  amendment. **That instruction is honoured by the shape of this record**: §1 establishes which
  reading holds before §2 rules anything, and §2 rules only because §1 concludes reading 1.
- **The conflict of interest is stated rather than managed quietly.** Reading 1 is the reading
  under which this role may decide, and this role reached it. Every step of §1 is therefore a
  quotation or a count, not a judgement: the standard-bearing document's own title, §8's own
  sentence structure, the roadmap row's scope clause, and a number measured twice.
- **Every figure is measured at `b648c22`**, `origin/main`'s tip when this record was written and
  the commit this branch is cut from — a fresh branch, because the previous one's remote was
  deleted on merge and its base predates the squash.
- **This record amends no filed plan and edits no note.** W37-6's leaf plan is frozen; RFC-937 is
  the maintainer's.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims that scope — register finding F68,
carried forward with RFC-937's migration as its trigger. Honoured here; the check is not patched
from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 85 immediately after 84, no duplicate, no skip.
2. §1 states **both** readings with the evidence for each, and names reading 2's strongest
   argument before answering it — not after.
3. The acceptance in §4 is stated as a violation that must become detectable.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-ruling-85-stage-boundary` names exactly this one new
   file.
6. Every quotation is verbatim from the artifact named, and every count was produced by running
   the command shown.

---

## RL-997 — §8 is sequencing, not standard; S2 is a criterion and S3 is a residue, so RL-987 moved nothing

### 1. Verified first, at `b648c22`

**(a) §8 has no scope clause. That is the first finding, and it is a negative one.** The section
is titled *"Sequencing"* and consists of four stage descriptions in one paragraph. It does not
say it binds, and it does not say it is descriptive. **The question cannot be settled from §8's
own text**, which is why the rest of this section looks outside it. Anyone answering row 36 by
reading §8 alone will find nothing either way.

**(b) The standard-bearing document lifts §1 and nothing else.**
[`docs/process/document-ids.md`](../process/document-ids.md) — the maintainer-owned reference
that `CLAUDE.md` and the templates cite as *the* standard — carries:

```
title: The document-id standard (RFC-937 §1, lifted verbatim)
...
Lifted verbatim from RFC-937 §1.1 through §1.13,
```

Its headings run `## 1.1` to `## 1.13`. **There is no §4, §5, §7 or §8 in it.** So *"part of the
accepted standard"* has a documentary answer rather than an interpretive one: the standard is
§1, and §8 is not in it. This is the same boundary the template-parser record relied on when it
held that §1.6 makes `process/` the maintainer's, amendable only by an `RFC-` plus an `RL-` —
that ownership attaches to the lifted §1, which is what `document-ids.md` contains.

**(c) RFC-937's own amendment mechanism is about §1's structures, not §8's stages.** §1.12
*"Extending the frame"* gives three levers — a new `kind:`, a new document family, a new row
family — each with what it takes (*"a template variant and one line in the family's kind
vocabulary; an `RL-`"*; *"an `RFC-` and an `RL-` naming prefix, directory, unit, mutability,
status subset…"*). **Every lever operates on §1.2's family table.** Nothing in the note describes
amending a stage, because a stage is not a frame element. Row 36's first disposition — *"an
amendment to §8"* — names a procedure the note does not define.

**(d) The Work's own scope clause omits §8.** `docs/roadmap.md`'s WK-697 row:

> **Scope:** the note's §1 standard in full — … ; its §4 one-time scripted migration; its §5
> impact map — …; and its §7 acceptance items (a)–(k).

**§1, §4, §5, §7. Not §8.** Because §8 was consumed as *input*: the map plan
[`../plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`](../plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md) cut
the Work into eleven slices *from* §8's stages. A map plan is the planner's, revisable by a
replan (`CLAUDE.md` §12, RFC-937 §1.6's `PL-` row). So even on the reading most hostile to
RL-987, re-cutting §8 is at worst **the planner's**, never the maintainer's.

**(e) §8's own sentence structure gives S2 a criterion and S3 a residue.** Verbatim:

> **S2 — the migration PR** (§4) at a gap, **with the H rows that must land in the same
> commit**: `audit-docs.py` parsers and roots, `register-*.py`, … `delivery-process.md`
> vocabulary. **S3 — conventions: every remaining H row** — `CLAUDE.md`, README/CONTRIBUTING/PR
> template, seven charters, the eleven primary skills, `docs/` READMEs, checklists, rituals.

S2's membership test is *"the H rows that **must land in the same commit**"* — a criterion —
followed by a colon and an enumeration of what the author expected to satisfy it. S3's is
*"every **remaining** H row"* — a subtraction — followed by a dash and the names expected to
remain. **S3's population is therefore computed from S2's, not declared independently of it.**
RL-987 held that the instrument set is a criterion rather than a list and derived thirteen
members; that is S2's own test, applied. On this reading nothing crosses a boundary, because the
boundary is a subtraction that resolves differently once the criterion is applied correctly.

**One corroborating detail inside §8 itself:** S2's list already contains
`delivery-process.md` vocabulary — a `process/` document, which by S3's own description
(*"conventions … checklists, rituals"*) looks like S3 material. §8 already puts a
convention-shaped document in S2 when the same-commit criterion demands it.

**(f) Reading 2's strongest argument, stated before it is answered.** Two things support it, and
they are not weak.

1. **S3's names carry counts** — *"seven charters"*, *"the eleven primary skills"*. A number
   reads as an enumerative commitment, not an illustration. If three charters and six skills
   move, S3 has four and five, contradicting its own text.
2. **The leaf plan's closing rule**: *"On any disagreement between this plan and
   [`RFC-937`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md), the note wins and the disagreement is a
   finding against this plan."* (leaf plan `:1263-1265`). The leaf plan §6.2 is where the
   thirteen are derived, so if §8 and §6.2 disagree, the note wins by the plan's own rule.

**(g) The measurement that answers (f)(1), and it is decisive.** `"eleven"` appears in RFC-937
exactly once:

```
$ grep -n 'eleven' docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md
430:**S1 — instruments, no moves:** … (this is §8's own line)
```

Meanwhile §5.4 marks its primary skills explicitly:

```
$ sed -n '<§5.4>,<§5.5>p' docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md | grep -c 'primary'
6
```

— `writing-plans`, `subagent-driven-development` (+ `scripts/task-brief`), `close-workstream`,
`phase-review`, `adr-write`, `spec-change`. **§8 says eleven; §5.4 marks six; the note contains
no other statement of the number.** `"seven charters"` is, by contrast, accurate —
`ls .claude/roles/*.md` returns 7.

So one of S3's two counts was **already wrong against its own §5 on the day the note was
accepted**, and the other is right. A list with a stale member is a shorthand; a binding
population would have had to survive contact with the impact map in the same document. **This
does not make §8 careless — it makes it a summary**, which is what a sequencing section is for.

**(h) The answer to (f)(2).** The closing rule's precedence is *plan* below *note*. **RL-987
is neither.** The chain runs ruling → plan: §6.2 derives the instrument set *that RL-987
requires*, and the leaf plan cites RL-987 as an obligation it discharges. The closing rule
resolves a plan-versus-note conflict and is silent on ruling-versus-note — and on (e)'s reading
there is no conflict to resolve, because applying a criterion the note states is not disagreeing
with the note. **Where the closing rule does bite is the opposite way**: if someone later
concludes §8's enumeration binds, the finding it produces is *"against this plan"*, i.e. a
replan, not a maintainer amendment.

### 2. Ruled

**Reading 1. §8 is sequencing, not part of the accepted standard; moving population between its
stages is not an amendment; RL-987 stands as issued and needs nothing further.**

Row 36's two dispositions were *"either an amendment to §8, or a ruling that RL-987's
criterion reaches"*. **Neither is quite right, and the difference matters:** there is no boundary
to reach across. S3 is defined as what S2 leaves, so a correct application of S2's criterion
resizes S3 by construction. RL-987 did not extend into S3's population; it computed S2's
correctly, and S3's population is whatever remains.

**Rejected: reading 2, that §8 is part of the standard and this is an amendment.** Rejected on
(b) — the standard-bearing document lifts §1 and stops — and on (c): the note defines an
amendment procedure, and it operates on families, not stages. Its best evidence, S3's counts,
fails on (g): one of the two counts contradicts §5.4 within the same note.

**Rejected: treating this as a genuinely open choice and sending options to the maintainer.**
This was the lead's requested form and it is declined *for this question*, with the reason
stated: four documentary facts point one way and the strongest contrary argument is a number the
note itself refutes. Manufacturing a balanced options table over that would misrepresent the
evidence as evenly split — and `CLAUDE.md` §10's options-and-recommendation form is for a choice
that is *genuinely* open, not for one whose answer is inconvenient to hold alone.

**Rejected: ruling this silently and letting it ride.** See §3 item 3 — it travels to the
maintainer as a disclosed item even though it is ruled, because the lead is right that the
go-ahead cannot authorise a run whose contents are undetermined, and because a maintainer who
disagrees should meet this before the run rather than after.

### 3. What it obliges

1. **W37-6's commit contains the thirteen instruments RL-987's criterion derives**, including
   the three charters and the skills. No amendment, no `RFC-`, no further ruling.
2. **§8 is not edited to match.** It is the maintainer's note; a summary being coarser than the
   impact map it summarises is not a defect the migration fixes.
3. **This ruling is disclosed in the go-ahead package**, in one line naming what it decided and
   what the maintainer would change by overturning it: with reading 2 instead, the thirteen leave
   the commit and §4.6's gap reopens — see §4's third item for what that costs.
4. **Row 36 is closed by this record**, not by an amendment. The obligations list's *"NEEDS A
   RULING"* state resolves to `RL-997`, and the register row's disposition column should name
   it.
5. **Nothing here touches RL-987's own acceptance.** RL-970 already withdrew that ruling's
   acceptance item 2; this record does not revisit it.

### 4. Acceptance — the violation that must become detectable

**The violation: an instrument that teaches a retired grammar survives the migration commit, or
a document is created from one between the migration and W37-7.**

- **A check that every instrument in RL-987's derived set is modified by the migration
  commit**, run against the commit's own diff. *Violation: an instrument in the set whose file
  is absent from the migration diff.* This is what makes §3 item 1 enforceable rather than
  advisory, and it must be shown failing on a deliberately-omitted member.
- **Acceptance (j) is the live test of the gap, and it already exists**: *"one new item per
  family born through its skill with a number from `doc-id.py next`."* If an instrument is
  stale, the item born through it carries the retired form and (j) fails. *Violation: (j)
  passing while an instrument still teaches the old grammar* — which is possible only if (j) is
  run for a family whose instrument was in the commit, so (j) must be exercised across the
  families whose instruments the criterion named, not one convenient family.
- **The cost of the other reading, stated concretely because the maintainer will weigh it.**
  Under reading 2 with a refusal, the thirteen stay in S3 and land after the run. In the gap
  between the migration commit and W37-7, every document created by following `spec-change`,
  `adr-write`, `close-workstream`, `writing-plans`, `phase-review` or
  `subagent-driven-development` is produced against the retired grammar — a filename with no
  padded id, no YAML header, a legacy prefix — and lands in a tree where checks 30–39 are scoped
  to everything. **Each such document is a red gate at creation**, and the author's recourse is
  to hand-write what the instrument should have taught. The gap is not hypothetical: W37-7 is
  four slices away and the session creates governed documents continuously — this record is one.

---

## Routed to the maintainer — one item, and not the one row 36 expected

**§8's *"the eleven primary skills"* is wrong against §5.4's six, and has been since the note was
accepted.** It is not a blocker: §8 is sequencing, nothing reads it mechanically, and this ruling
does not depend on the number. It is worth correcting when §1 is next opened, by the same
`RFC-` route already carrying the `exit_criteria` / `exit criteria` divergence that
[`RL-00999-the-phase-section-is-plain-fields-under-its-heading-the-fence-requirement-in-scan-phase-sections-is-the-defect-and-its-unbounded-lookahead-is-what-makes-the-failure-silent-instead-of-loud.md`](RL-00999-the-phase-section-is-plain-fields-under-its-heading-the-fence-requirement-in-scan-phase-sections-is-the-defect-and-its-unbounded-lookahead-is-what-makes-the-failure-silent-instead-of-loud.md)
routed there. Two textual corrections, one visit.

**The reason it is disclosed rather than filed and forgotten:** the number is load-bearing for
anyone who reads §8 as an enumeration, which is exactly what row 36 did. Leaving it uncorrected
leaves the next reader the same trap.

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **Whether the maintainer accepts this reading** | A ruling under delegation stands as the maintainer's own, but a standing delegation is a default, not a bar (delegation record §2, last row). This one enlarges the commit the maintainer is being asked to authorise | **The maintainer**, as a disclosed line in the go-ahead package — §3 item 3 |
| **Correcting §8's count** | `CLAUDE.md` §12 reserves the note to the maintainer; §1.6 makes `process/` amendable only by `RFC-` + `RL-` | **The maintainer**, via the `RFC-` route, batched with the `exit_criteria` divergence |
| **Whether RL-987's thirteen is still the right set** | RL-987 settled the criterion; the leaf plan §6.2 derived the members and RL-970 already withdrew the acceptance item that would have re-derived them. Re-opening membership is a new question, not this one | **The lead**, if anyone raises it |
| **Whether the map plan should be re-cut to say so** | A map plan revision is the planner's (`CLAUDE.md` §12) | **The planner**, at the next revision, if it wants §8's stages restated in the plan's own terms |

## Provenance

Routed by the lead on 2026-09-02 as register row 36 — the one group-A item it declined to decide
— with three things the derivation was required to establish: what §8 says about its own force,
whether the note states how it may be amended, and what each reading costs at the run. The first
returned a negative result (§8 says nothing), which is why §1(b) to §1(d) look outside it. Every
quotation is verbatim; the two counts in §1(g) were produced by the commands shown.
