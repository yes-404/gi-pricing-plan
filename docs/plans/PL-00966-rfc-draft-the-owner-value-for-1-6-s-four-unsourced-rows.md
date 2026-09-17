---
id: PL-966
family: plan
kind: leaf
title: RFC draft — the `owner:` value for §1.6's four unsourced rows
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-02
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-09-02-w37-rfc-bucket-c-owner-values.md
---

# RFC draft — the `owner:` value for §1.6's four unsourced rows

> **For agentic workers:** this is an **`RFC-` in draft**, written by the planner on the
> maintainer's instruction under §1.6's `RFC` row — *"maintainer mints and owns; any role
> drafts on instruction; lead assesses."* **It decides nothing.** The maintainer accepts or
> strikes each value; the lead assesses first.

**Why it is filed here and not in `docs/rfcs/`.** That directory does not exist before the
migration (`git ls-tree -d 22d8d64 -- docs/rfcs` returns nothing). Like every other
pre-migration governance artifact it lands under `docs/plans/`, and becomes
`RFC-<nnnnn>` with `kind: process` when the migration runs.

**Deliverable:** a stated `owner:` for each of §1.6's four rows that do not yield one, so the
migration can stamp **152 files and rows** without a silent pick.

**Spec:** [`../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) §1.6.

**Tree:** every count and quotation was produced at **`22d8d64`**.

## Acceptance Standard

1. **Every row carries a candidate value and the source it was read from, side by side.**
   *Violation: a value with no source cell named.*
2. **A row whose value cannot be sourced carries no value.** *Violation: an inferred candidate
   presented as a read one — the maintainer's instruction is to accept or strike values, and an
   unsourced candidate invites acceptance without the check.*
3. **Read and derived are marked differently.** *Violation: a derivation typeset as a reading.*
4. **The population is counted, not described.** *Violation: a class stated without its count,
   or a count without the command that produced it.*
5. **Scope is the four rows and nothing else.** *Violation: gap 1, or the README gap of §4,
   folded in rather than named.*

## Global Constraints

- **The maintainer accepts; the lead assesses; the planner drafts.** Nothing here binds.
- **Gap 1 — the disambiguating rule for §1.6's bucket-B rows — is not in scope.** It stays
  with the decision-maker, where the `owner:` derivation put it.
- **No filed document is edited.**

---

## 1. The four rows, with a candidate and its source

§1.6's column is **"Owner — creates & amends"**. These four cells name several roles, or a set,
and do not yield one value.

| # | §1.6 row | Cell, verbatim | Candidate `owner:` | Source | Read or derived |
|---|---|---|---|---|---|
| 1 | **Phase** `P<n>` | *"maintainer opens the section; lead maintains it"* | **`maintainer`** *or* **`lead`** — the maintainer strikes one | The cell splits the column's own two verbs: **maintainer** *creates* (*"opens"*), **lead** *amends* (*"maintains"*) | **Read, but to two values.** Neither is a derivation; the cell genuinely names both |
| 2 | **WK** | *"maintainer opens (`draft`); planner writes its map plan; maintainer sets `active`"* | **`maintainer`** | Same cell, first and third clauses. The planner's act produces a **different artifact** — a `PL-` map plan — not an amendment to the `WK-` row, so it does not bear on this row's owner | **Read** |
| 3 | **Reference — skills** | *"the five roles already permitted; lead approves"* | *(none)* | Unsourceable. §1.6 never enumerates *"the five"* — `grep -n 'five roles'` returns **one** line, this cell itself (`:156`). *"lead approves"* belongs to the **"Accepts / decides"** column, not this one. `docs/_templates/REFERENCE.md:26` offers a second source and **contradicts itself**: the value is `owner: maintainer`, the comment beside it reads *"whichever of §1.6's five roles the document names"* | **Neither.** §2 states the sub-questions |
| 4 | **Reference — `contracts/`** | *"generated from `model-schema`; `gi-pricing.yaml` executor via `contract-schema`"* | `gi-pricing.yaml` → **`executor`**; the other 60 → *(none)* | The second clause names the executor for that one file. The first names a **generator**, not a role | **Read** for the one; **unsourceable** for the 60 — §2 |

---

## 2. The two rows that cannot be sourced, and what the maintainer is actually being asked

### 2.1 Reference — skills (46 files, the largest class)

**Two sub-questions, and the second is the one that matters:**

1. **Which five roles?** §1.6 says *"the five roles already permitted"* and never lists them.
   Seven role files exist (`auditor`, `decision-maker`, `executor`, `lead`, `planner`,
   `reporter`, `watcher`), and §1.6's own closing paragraph excludes two — *"the reporter and
   the watcher own no governed document"*. **That yields five, and it is the only reading under
   which the count is right.** Stated as a candidate derivation, not a reading.
2. **Does the field carry a per-skill value or one standing value?** If per-skill, `owner:` on a
   `SKILL.md` answers *"which role wrote this"* — the author reading the `owner:` derivation
   found the field does not otherwise take. If one standing value, the natural candidate is
   **`lead`**, sourced from *"lead approves"* — but that clause sits in the wrong column.

**A third fact the migration meets whichever way this goes.** Of the 46 `SKILL.md`, **43 parse
under `_docid.parse_header` and 3 raise `HeaderError`**:

| Skill | Raises on |
|---|---|
| `create-adaptable-composable` | `  author: github.com/vuejs-ai` |
| `vue-best-practices` | `  author: github.com/vuejs-ai` |
| `planning-with-files` | `user-invocable: true` |

**Two of the three fail because they record an author** — upstream metadata the closed field
set refuses. All three are vendored. So the corpus's only documents that carry authorship as a
field are the ones the standard cannot parse, which is the same absence from the other side:
§1.6 asks who owns a skill, the schema has nowhere to say who wrote one, and where upstream
says it anyway the parser stops. **Named because it is a stamping precondition for this row, not
to widen the scope** — RL-990 settled the *deviation* of stamping a vendored file; it did not
settle a file whose existing block does not parse.

### 2.2 Reference — `contracts/` (61 files)

**One is sourced, sixty are not.** `gi-pricing.yaml` → `executor`, read off the cell. The other
60 are generated from `model-schema` and no role creates or amends them by hand; §1.2's
Reference row admits `generated: true` for exactly this case. **The question is whether a
`generated: true` file carries an `owner:` at all** — and if it must, whose. `check_owner`
requires a member of `{maintainer} ∪ role stems` on every file in scope, with no exemption for
generated ones.

---

## 3. The population, counted

Commands are `git ls-tree -r --name-only 22d8d64 -- <path>` and, for the roadmap, a count of
distinct row keys and phase headings in `docs/roadmap.md`.

### 3.1 The four rows in scope — 152

| §1.6 row | Population | Count | Sourced? |
|---|---|---|---|
| Reference — `contracts/` | `docs/contracts/` | **61** | 1 of 61 |
| Reference — skills | `.claude/skills/*/SKILL.md` | **46** | no |
| **WK** | distinct `W<n>` row keys in `docs/roadmap.md` | **41** | yes — `maintainer` |
| **Phase** | phase sections in `docs/roadmap.md` | **4** | to two values |
| | | **152** | |

### 3.2 The Reference rows §1.6 *does* source — 18, listed so the disclosure is complete

| §1.6 row | Population | Count | Owner, read off the cell |
|---|---|---|---|
| Reference — agents | `.claude/agents/*.md` | **8** | `lead` |
| Reference — charters | `.claude/roles/*.md` | **7** | `maintainer` |
| Reference — `process/` | `docs/process/*.md` | **3** | `maintainer` |

### 3.3 What no discovery function reaches

`_discover_vendored_skill_manifests` is the only code path that touches a `SKILL.md`, it reaches
the vendored subset, **and it assigns no `owner:` at all** — verified by reading its `_Draft`
construction. Every other `owner=` in `scripts/doc-id.py` sits inside a governed-*document*
discovery. **There is no discovery or stamp path for `.claude/skills/`, `.claude/agents/` or
`.claude/roles/`**, while §4 step 5 stamps all three and check 35 will demand a valid owner on
each once `_ID_SCOPE_ROOTS` widens.

---

## 4. Named, not folded in — a fifth row that has no cell at all

§1.2 places **every `README.md` anywhere in the tree** in the Reference family. §1.6's Reference
rows are `process/`, charters, skills, agents and `contracts/` — **there is no README row.**
**32 tracked `README.md` files** therefore have no owner cell to be ambiguous about.

**This is out of scope by constraint (a) and is not proposed here.** It is worse-shaped than the
four rows — an absent cell rather than a multi-valued one — and it is named so that accepting
this RFC is not mistaken for closing the class.

---

## 5. What accepting this produces

- Four values (or three plus a struck alternative), each citable, so the migration stamps 152
  files and rows from a stated rule rather than a silent pick.
- **It does not resolve gap 1**, and does not touch §1.6's bucket-B rows.
- **It does not resolve §4's README row.**
- **It does not decide the three unparseable vendored manifests** — §2.1 names them as a
  stamping precondition for row 3, and their disposition follows whichever way row 3 goes.
