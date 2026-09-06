---
id: RL-945
family: ruling
title: Q4: the ownership matrix lands in `docs/process/`; a note appendix is rejected
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-01
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md
---

# RFC-897's Q4, Q5, Q6 and Q7's notes half, ruled (2026-09-01)

**What this is.** Four of the seven open questions in
[`../rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md`](../rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md)
§10 — Q4, Q5, Q6, and the notes half of Q7 — which
[`../plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md`](../plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md) §2 finds
**rulable now**, over evidence that plan re-measured at its pinned tree `b551060`. Each
recommendation arrived from the note carrying a proposal; a note decides nothing
([`../rfcs/README.md`](../rfcs/README.md)), so each is re-verified
below rather than adopted on the strength of being the only text on the table.

**Q1, Q2, Q3 and Q7's general half are NOT ruled here.** The plan's §2 finds the evidence to
rule them does not exist yet — they presuppose a closed category set the census (Slice 2)
and taxonomy draft (Slice 3) have not yet produced, and §4 names the decision gate after
Slice 3 as their trigger. This record does not pre-empt that gate. Independent re-check
against this plan's own reasoning (not against a fresh read of the underlying evidence, which
does not exist yet to check against) found no ground to disagree: ruling any of the four
today would be a ruling on the note's hypothesis rather than on data, which is exactly the
outcome §10's authors wrote the split to avoid.

**This ruling is what unblocks Slice 4.** §9 of the plan blocks the notes move on "Slice 1
merged, and Q5, Q6 and Q7's notes half ruled by the decision-maker." Slice 1 is a separate,
independent PR; this record discharges the second half of that gate. Q4 is included because
the plan finds it rulable and ruling it in the same record costs nothing additional.

**Numbering continues at 55.** Verified rather than relayed: every `## Ruling N` heading
under `docs/plans/` at `b2fb122` (`origin/main`, fetched immediately before this record was
written) yields a maximum of 54, in
[`RL-00931-correct-the-example-do-not-build-the-breakdown.md`](RL-00931-correct-the-example-do-not-build-the-breakdown.md).

**Everything measured here was measured at `b2fb122`.** The plan pins its own evidence to
`b551060`, five commits behind. Where a figure moved between the two trees, both are stated;
none of the plan's five load-bearing evidence claims changed in substance between them — see
each ruling's §1 and the summary at the foot of this record.

**This record's own dependence on the plan.** Every claim in the plan's §1, §1a, §1b and §2
that this record's four rulings rest on re-verified true, at its own stated tree, with no
defect found in that reasoning — only ordinary drift in line numbers and citation-surface
counts, which the plan's own framing anticipates (`CLAUDE.md` §13: "a count carries the tree
and the corpus it counted over"). **One defect was found elsewhere in the plan** — in Slice
1's own Step 1 test code, unrelated to any of the four questions ruled here — and is recorded
as a correction appended to the plan's own *Corrections after filing* section, per this
role's charter and RFC-897 C4, rather than edited into the frozen text. See that section for
detail; it does not change any ruling in this record.

## Acceptance Standard

The testable definition of "done" for this ruling record, each item checkable by a command a
fresh reviewer can run:

1. `git grep -c "^## RL-868[5-8] —" docs/rulings/INDEX.md#2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulingsmd`
   returns `4`, and `git grep -n "^## Ruling " docs/plans/` shows 55–58 filling exactly the
   gap after RL-931 with no duplicate and no skip.
2. Each of the four `### 2. Ruled` subsections names both the chosen option and the rejected
   option in its opening sentence.
3. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
4. `git grep -nE '\bFR-[A-Z]+-[0-9]|\bNFR-[A-Z]+-[0-9]|\bOQ-[A-Z]+-[0-9]|\bADR-[0-9]' docs/rulings/INDEX.md#2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulingsmd`
   returns zero matches — no requirement or ADR identifier is minted, per RFC-897 C2 and the
   parent plan's own scope.
5. `git diff --stat <merge-base>..<branch> -- docs/plans/` names exactly two files: this
   record, and the *Corrections after filing* append to
   [`../plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md`](../plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md) — no other
   file under `docs/plans/` changes, and the append is additive only (`git diff` on that file
   shows only inserted lines).
6. Q1, Q2, Q3 and Q7's general half are named in this record only inside the preamble's "NOT
   ruled here" paragraph and RL-948's scope note — never inside a `### 2. Ruled` verdict —
   confirmed by `grep -n "### 2. Ruled" -A2` on each of the four rulings naming no other `Q`
   than its own.

---

## RL-945 — Q4: the ownership matrix lands in `docs/process/`; a note appendix is rejected

### 1. Verified first, at `b2fb122`

| Claim | Verdict |
|---|---|
| C3 — "ownership is derived from charters, not invented" — is a design constraint the note states and does not re-litigate | **Confirmed** — `.claude/rfcs/0016-…md:58-61` |
| `CLAUDE.md` §12 grounds the same principle, and `.claude/roles/auditor.md` quotes it | **Confirmed** — `CLAUDE.md:222`: *"writes the artifacts its charter names, including under `docs/`"*; `.claude/roles/auditor.md:50`: *"a role writes the artifacts its own charter names"* |
| seven role charters exist, each independently amendable | **Confirmed** — `.claude/roles/{auditor,decision-maker,executor,lead,planner,reporter,watcher}.md`, 7 files |
| `docs/process/` today holds only living documents, none frozen | **Confirmed** — `agent-settings.md`, `delivery-process.md`, `delivery-process.core.json`; no dated/write-once file among them |
| the note's own recommendation is "living, in `docs/process/` — it must track charter amendments" | **Confirmed** — `.claude/rfcs/0016-…md:230-231` |
| no ownership-matrix file exists yet at either candidate location | **Confirmed** — `git grep -il "ownership matrix"` returns only the note and the plan themselves |

### 2. Ruled

**Chosen: `docs/process/`, as a living document. Rejected: an NT note appendix, frozen.**

A note appendix is frozen by the same convention every note obeys — see RL-946 below and
`.claude/rfcs/README.md`'s own custody rule. An ownership matrix's content is a cross-cutting
read of all seven role charters' `Owns`/`Never` clauses, and those charters are themselves
living — `.claude/roles/decision-maker.md`, this record's own charter, was itself amended
mid-project (its own text names two incidents that changed it). A frozen appendix could not
track the next such amendment without either going stale silently or being edited in
violation of the freeze it lives under — the exact duplicated-status decay
`.claude/rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md` catalogues, reproduced one level down. A
living document in `docs/process/`, alongside `delivery-process.md` and
`agent-settings.md` — which already track process facts that change as the team's charters
and settings change — has no such failure mode: it is amended in the same commit as the
charter change that motivates it.

This question does not depend on Q1. The matrix cross-references existing charters; nothing
about *which* file-category taxonomy the census yields changes where the cross-reference of
charters to categories should live.

### 3. What it obliges

Whichever future slice files the ownership matrix (Stage 2/3, unscoped by this plan) creates
it as a living file under `docs/process/`. This ruling fixes the directory and the mutability
class only — not a filename, which is that slice's to choose and outside this record's scope.

**Overridden if** a future slice files the matrix as a note appendix, or as any other frozen
artifact under `docs/plans/` or `.claude/notes/`.

---
