---
id: FD-9862
family: finding
title: The generated ownership matrix lists owners §1.6 does not grant, because a role named in an owner cell is counted as its owner
status: active
created: 2026-09-30
owner: auditor
tree: eeda8f4ba20d247ac18d6a35d7f81589c8527ed2
corrected_by: []
relates: [WK-1169]
---

# FD-9862 — The generated ownership matrix lists owners §1.6 does not grant, because a role named in an owner cell is counted as its owner

## Finding

**Severity: low.** `ownership_matrix()` (`scripts/doc-index.py:958-969`) marks a role as the owner
of a family whenever `role in owner_text`, over `_OWNERSHIP_TABLE` (`:924-947`), a hand-transcribed
copy of §1.6's "Owner — creates & amends" column. Naming a role in a cell is not owning: a cell
also names who *assesses*, *approves* and *writes a different document*. The generated
`## Ownership matrix` in `docs/INDEX.md` (`:1445-1456` at `eeda8f4b`) therefore lists three
owners §1.6 does not grant, and omits owners it does. `doc-index.py --check` is green, because it
checks that the file matches the generator, not that the generator matches §1.6 (`CLAUDE.md` §13:
*"a generated artifact matching its source proves neither correct"*).

## Evidence

Measured at `origin/main` `eeda8f4ba20d247ac18d6a35d7f81589c8527ed2`, in a detached scratch worktree.

**The predicate, verbatim:** `if role in owner_text: matrix[role].append(family_label)`.
A word-boundary variant (`re.search(r'\b' + role + r'\b', owner_text)`) gives the identical matrix
(`substring == word-boundary: True`), so this is not a substring accident. The defect is that
"is named in the cell" is the wrong predicate.

**Each wrong row, against `docs/process/document-ids.md` §1.6:**

| Matrix row (`INDEX.md`) | §1.6 owner cell (`document-ids.md`) | What is wrong |
|---|---|---|
| planner owns **work (WK)** | `:153` WK: *"maintainer opens (`draft`); planner writes its map plan; maintainer sets `active`"* | The planner writes a **PL** (`plan`), not the WK. The WK's owner is the maintainer. |
| lead owns **proposal (RFC)** | `:157` RFC: *"maintainer mints and owns; any role drafts on instruction; lead assesses"* | The lead assesses. §1.6 says the maintainer owns. |
| lead owns **reference: skills** | `:169` skills: *"the five roles already permitted; lead approves"* | The lead approves. The owners are the five permitted roles, which the cell does not name. |

**Rows wrong by omission, from the same cells:**

- **reference: skills** has no owner among the five permitted roles in the matrix, because the
  cell names none of them; the matrix shows only the lead, an approver.
- **RFC** shows the maintainer only; *"any role drafts on instruction"* names no role, so it is
  unrepresented. Whether drafting is ownership is §1.6's to say, not this record's.
- **reference: `contracts/`** (`:171`) is *"generated from `model-schema`; `gi-pricing.yaml`
  executor via `contract-schema`"*. The transcription drops the `gi-pricing.yaml` limb, so the
  matrix gives the executor the whole directory, including the generated files no role owns.

**Other rows, using my own predicate:** I classified every `_OWNERSHIP_TABLE` row by hand — does
the cell name this role as the one who creates or amends the family? — against §1.6 `:150-171`.
The remaining role/family pairs agree (decision-maker: FR/NFR/DEP, OQ, WF, ADR, RL; maintainer:
phase, WK, RFC, RL, `process/`, charters; lead: phase, CR `review`; planner: SL, PL map/leaf;
executor: PL handover, LG, RS spike/measurement; auditor: PL review, RS audit, CR work/phase, FD).
The maintainer's RL row rests on *"the maintainer may author one on scope or process"*, a
permission rather than ownership, and is left as §1.6 states it. `reporter` and `watcher` are
empty in both.

## Disposition

**Carry forward, owner WK-1169.** The fix path is already ruled: the #940 ruling (working id
9854, fact (A) and DP-2/DP-3) has one exact owner table, derived once, feed the matrix,
each directory's *Permitted owners* line and check 35, so no second transcription exists to
drift. This record adds the evidence and the three wrong rows to that fix's acceptance. The
proof on delivery is on this input: the regenerated matrix must show the WK owner as the
maintainer, RFC as the maintainer and skills without the lead as owner; **the five permitted
roles as the owners of skills** (§1.6 `:169`); and **the executor as owner of only
`gi-pricing.yaml`** under `contracts/` (§1.6 `:171`). A deliberately wrong owner cell must fail a
check rather than reach `INDEX.md` with `doc-index.py --check` green.

*Drafted under working id 9862.*
