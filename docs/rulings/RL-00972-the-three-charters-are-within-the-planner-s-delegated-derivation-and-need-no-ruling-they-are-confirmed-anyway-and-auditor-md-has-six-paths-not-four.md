---
id: RL-972
family: ruling
title: the three charters are within the planner's delegated derivation and need no ruling; they are confirmed anyway, and `auditor.md` has six paths, not four
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-6-leaf-plan-findings-rulings.md
---

## RL-972 — the three charters are within the planner's delegated derivation and need no ruling; they are confirmed anyway, and `auditor.md` has six paths, not four

### 1. Verified

| Claim | Verdict |
|---|---|
| No skill among the 46 mints a ruling record | **Confirmed.** `git grep -n 'RL\.md\|RL-' -- .claude/ docs/_templates/` returns hits only inside `docs/_templates/`. Zero in any `SKILL.md` or any `.claude/roles/*.md` |
| Nothing routes an author to `docs/_templates/RL.md` | **Confirmed.** `adr-write` — one of `decision-maker.md`'s three mandatory skills — contains no occurrence of "ruling" at all; it covers `docs/adr/` only. `decision-maker.md` has no occurrence of `_templates` |
| `docs/_templates/RL.md` exists and prescribes the post-migration form | **Confirmed:** *"Copy this file to `docs/rulings/RL-<nnnnn>-<slug>.md`"* |
| `docs/rulings/` is empty and every real ruling lives in `docs/plans/` | **Confirmed.** Zero tracked files under `docs/rulings/` at `e93e0e4` |
| The `RL-` window is occupied | **Confirmed.** 72 ruling headings across 29 files, and this record adds six more |
| `planner.md` files the §14 review at a path this commit deletes | **Confirmed**, line 22: *"filed to `docs/closures/INDEX.md#plan-reviewsmd` as a dated `### Plan review N` section"*, and its Tools bullet names the same path |
| `auditor.md` carries four `docs/audit/` filing paths in one bullet | **Confirmed as to the bullet; the file names six.** §1 V9 |

### 2. Ruled

**This is the planner's delegated derivation, not a decision reserved to this role, and it needed
no ruling to proceed.** RL-987 §2 made the set *"a criterion, not a list"* and §3 obliged
*"W37-6's leaf plan carries a section deriving the instrument set from checks 30-39."* Adding a
member the criterion selects is executing that delegation. The plan was right to add the three
and did not need to ask; asking cost nothing and this paragraph is the answer for the next time.

**All three are nevertheless confirmed as members, on the criterion.**

- **`.claude/roles/planner.md`.** Its output is a `CR- kind: review`. Its instruction files that
  document at `docs/closures/INDEX.md#plan-reviewsmd` under a `### Plan review N` heading — a directory this
  commit deletes and a heading form no template declares. Following it after the flip produces a
  document that reds checks 30, 31 and 37. In scope.
- **`.claude/roles/auditor.md`.** Its output is a `CR- kind: work`/`phase`, an `FD-` and an
  `RS- kind: audit`, and it names six paths into the dissolving tree. In scope, **and the fix
  covers all six.** W37-6's task list says *"all four `docs/audit/…` filing paths in its one
  bullet"*; taken literally that strands `docs/audit/findings/<F-id>.md` and
  `docs/audit/findings/README.md` in the next bullet. Sweep the file, not the reported bullet.
- **`.claude/roles/decision-maker.md`.** Its output is the `RL-` — and it is a member *because* it
  teaches no form, which reads backwards on a first pass and is right. An instrument that teaches
  a wrong form fails loudly at the first document; one that is silent routes the author nowhere,
  and after this commit *"recorded as dated sibling records"* produces a headerless file in
  `docs/plans/` that reds check 30 (no header) and check 31 (directory ≠ family). In scope.

**This record is that defect's own exemplar, and the evidence is free.** It is a ruling. It is
filed at `docs/plans/2026-09-02-<slug>.md`, as a dated sibling of a plan, with no header block —
because that is what the charter says and because `docs/rulings/` does not exist yet. It is
exactly the document RL-970's limb 2a asks the executor to manufacture, produced here in the
ordinary course by the role the charter governs. The executor may cite it rather than build one.

**A correction to the plan's supporting quotation, so it is not re-cited in the stronger form.**
RFC-937 D10 reads *"Charters, skills and agents carry the header \| They are the `owner:`
vocabulary and the creating instruments."* The phrase attaches to the three-member group, not to
charters alone; the plan's *"D10 calls charters 'the creating instruments' in as many words"*
overstates it. The conclusion survives on D10's own text — charters are inside the group named —
and does not need the stronger reading, so the weaker and accurate one is what this record uses.

### 3. What it obliges

- The `decision-maker.md` edit is a **routing sentence**, not a rewrite: it names
  `docs/_templates/RL.md` and `docs/process/document-ids.md` §1.6 and replaces *"dated sibling
  records"*. The template already carries the correct instruction and is already migrated.
- The `auditor.md` edit covers **six** paths. The verification is a grep of the merged file for
  `docs/audit/`, returning nothing — not a count of bullets.
- **Add a third party to the dependency check W37-6 already schedules.** The plan asks which of
  `close-workstream` and `auditor.md` ends up holding the `FD-` essay's header and shape.
  Measured: `close-workstream/SKILL.md` does **not** state the `docs/audit/work/<id>/README.md`
  closure-record path — `auditor.md` states it, and so does `.claude/skills/docs-audit/SKILL.md`,
  which the plan excludes to W37-7 as a *reading* instrument. The exclusion may well be right,
  but the executor records where each of the three forms actually ends up, so W37-7 does not
  later remove one from a file on the assumption that another holds it.

### 4. Acceptance — the violation that must become detectable

1. **The `RL-` route must work end to end for a document produced by the charter alone.** After
   W37-6, an author following **only** `.claude/roles/decision-maker.md` files the next ruling
   record, and `python3 scripts/audit-docs.py` runs on it before any hand correction.
   **Violation: check 30, 31, 33 or 37 firing on it.** This is RL-987 acceptance item 1's form,
   applied to the family whose window is most occupied.
2. **No `docs/audit/` path may survive in a charter.** **Violation:**
   `git grep -n 'docs/audit/' -- .claude/roles/` returns any line at the merge tree. Stated as a
   grep over the directory rather than over the two files named here, so a third charter that
   acquires one is caught too.

---
