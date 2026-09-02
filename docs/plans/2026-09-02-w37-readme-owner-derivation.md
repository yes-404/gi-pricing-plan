# The README `owner:` row — a derivation for ruling

> **For agentic workers:** a derivation, not a plan and not a ruling. It answers one routed
> question under the *"cite the cell"* constraint and recommends a shape. **It binds nothing.**

**Goal:** bring a candidate `owner:` for the README row the gap-2 ruling deliberately did not
fold in, under the same constraint that made the other four defensible — **a value must be read
from a cell, not derived from what a role ought to own.**

**Spec:** [`../notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md) §1.2,
§1.6, §4 step 5, §5.2.

**Tree:** every count, path and quotation was produced at **`2e48960`**.

## Acceptance Standard

1. **The population is enumerated and classified before any value is proposed.** *Violation: a
   value proposed against "the READMEs" as one class.*
2. **Every candidate names the cell it is read from, and a candidate that needs an inference
   says which inference.** *Violation: a scope inference typeset as a reading.*
3. **Where no cell sources a value, that is stated as the answer** rather than filled with a
   plausible one. *Violation: a value with no provenance.*
4. **`python3 scripts/audit-docs.py` and `python3 scripts/req-coverage.py` both exit 0.**

## Global Constraints

- **The maintainer decides.** A §1 amendment, if that is the outcome, is theirs alone.
- **No filed document is edited.**

---

## 1. The population is not 33

33 tracked `README.md` exist. **Nineteen of them are not Reference documents after the
migration**, by §5.2's own rows:

| Class | Count | §5.2 row |
|---|---|---|
| `audit/work/*/README.md` and `audit/phases/1b/README.md` → `CR-`, `kind: work` / `phase` | **17** | *"`audit/work/*/README.md` (15), `audit/phases/1b/README.md`, `audit/exit-demo-uat.md` → `closures/CR-0nnnn-*.md`"* |
| `audit/README.md` → deleted | **1** | *"deleted; content to `findings/` and `closures/` READMEs"* |
| `.claude/notes/README.md` → deleted with the stubs | **1** | *"`notes/*.md` (19 stubs) + README → deleted; `REDIRECTS.csv` rows"* |
| **remaining, and needing an `owner:`** | **14** | |

*(§5.2's row says 15 work READMEs; 16 exist at `2e48960` — W37-5b's closure record was filed
after the row was written. The row's count is stale, its rule is not, and the derivation uses
the rule.)*

**The fourteen:** `docs/README.md`, `docs/adr/README.md`, `docs/audit/findings/README.md`,
`docs/contracts/README.md`, `docs/notes/README.md`, `docs/plans/README.md`,
`docs/workflows/README.md`, `.claude/agents/README.md`, `.claude/skills/README.md`, and five
outside `docs/` — the repository root, `deploy/`, `examples/fremtpl2/`, `packages/`, and one
test fixture.

---

## 2. Exactly one of the fourteen has an owner named in a cell

**§5.2, line 347:** *"`agents/README.md`, `ci-watcher.md`, `spec-reconciler.md` | header;
citations; **README names agents as Reference family owned by the lead**"*.

**`.claude/agents/README.md` → `owner: lead`.** Read from a cell — a §5.2 cell rather than a
§1.6 one, which the constraint permits since it names an owner directly and §1.6 does not
reach this file at all.

**For the other thirteen, no cell names an owner.** §1.6 has no README row; §5.2 names an owner
only in that one line. That is the finding, and §4 says what follows from it.

---

## 3. A §4-versus-§5.2 conflict, surfaced by counting

The two sections disagree about **which** of the fourteen are stamped at all.

| Source | Reach |
|---|---|
| **§4 step 5** — *"every file under `docs/`, `.claude/roles/`, `.claude/skills/*/SKILL.md`, `.claude/agents/`"* | the 7 under `docs/`, plus `.claude/agents/README.md` = **8** |
| **§5.2 line 398** — *"every README outside `docs/` is Reference family and gets the header"* | the 5 outside `docs/` |
| **§5.2 line 354** — the skills README gets a *"header"* | `.claude/skills/README.md` |

**§5.2 stamps six files §4 step 5 does not reach.** Step 5's glob `.claude/skills/*/SKILL.md`
cannot match a README sitting directly under `.claude/skills/`, and its list does not mention
the repository root, `deploy/`, `examples/` or `packages/` at all.

**This is the leaf plan's §10 finding 7 generalised.** That finding recorded step 5 and §5.4
disagreeing about one file, `.claude/skills/README.md`. The same disagreement covers **six**.
Recorded here because counting the population surfaced it; **not resolved here** — which of §4
and §5.2 governs is not this question.

**And one of the five reads oddly under §5.2's literal wording.**
`tests/fixtures/docs-ids/w37-4-checks/check35-readme-allowlist/README.md` is a fixture built to
test check 35's own owner allowlist. *"Every README outside `docs/`"* reaches it literally.
Stamping a fixture that exists to be parsed as broken input is unlikely to be intended.

---

## 4. The candidate reading, and its honest status

**"An index inherits the row of the tree it indexes."** Each of the thirteen unsourced READMEs
indexes a tree §1.6 does govern, so a value can be reached — at a cost stated below.

| README | Tree it indexes | §1.6 row | Yields |
|---|---|---|---|
| `docs/adr/README.md` | ADRs | `ADR` — *"decision-maker, via `adr-write`"* | `decision-maker` |
| `docs/workflows/README.md` | workflows | `WF` — *"decision-maker, via `spec-change`"* | `decision-maker` |
| `docs/notes/README.md` | notes → the `RFC` family | `RFC` — *"maintainer mints and owns"* | `maintainer` |
| `docs/audit/findings/README.md` | findings | `FD` — *"auditor (register row + essay)"* | `auditor` |
| `docs/contracts/README.md` | contracts | Reference — `contracts/`, ruled `executor` | `executor` |
| `.claude/skills/README.md` | skills | Reference — skills, ruled one standing `lead` | `lead` |
| **`docs/plans/README.md`** | plans | `PL` **×3** — planner (`map`/`leaf`), auditor (`review`), executor (`handover`) | **three values** |
| **`docs/README.md`** | the whole spec suite | `FR NFR DEP`, `OQ`, `WF` … | **several** |
| the five outside `docs/` | code trees | *no row* | **nothing** |

**Why this is weaker provenance than the four already ruled, stated rather than glossed.** The
ruled four needed **one** step: read the verb in the Owner cell that matches *"creates &
amends"*. This reading needs **two**: that step, plus a prior inference that **a row governing
a family also governs that family's index**. §1.6 does not state that inference anywhere. It is
a reasonable inference and it is still an inference, which is exactly what the constraint was
written to exclude.

**And it fails on the two largest indexes, for the reason the skills row failed.** `docs/plans/`
and `docs/` are indexes of trees with **several** owners, so there is no single row to inherit —
the same shape that made Reference—skills unsourceable, arriving one level up.

---

## 5. The answer

**Under a strict reading of "cite the cell": one value is sourced and thirteen are not.**

- **`.claude/agents/README.md` → `lead`**, from §5.2 line 347.
- **The other thirteen have no cell.** §1.6 has no README row, and §5.2 names an owner once.

**So the honest output is a finding rather than a value set: §1.6 needs a README row**, and
adding one is a §1 amendment and therefore the maintainer's. Per the routing instruction's own
terms — *"no cell sources this is a finding about §1.6, and a better answer than a plausible
value with no provenance"* — that is what this derivation returns.

**If the maintainer prefers not to amend §1**, §4's inheritance reading is available and costed:
it sources **six** of the thirteen, leaves `docs/plans/README.md`, `docs/README.md` and the five
outside `docs/` unsourced, and requires accepting a scope inference §1.6 does not state. **It
is offered as an alternative, not as a recommendation**, because a rule that resolves 6 of 13
while introducing an unstated inference is worse value than a row that resolves all 14.

**A README row would also settle §3's conflict**, since it would have to say which READMEs are
in the family before it could say who owns them.

---

## 6. What this derivation does not do

- It does not rule, and does not amend §1.6.
- It does not resolve the §4-versus-§5.2 stamp conflict of §3 — surfaced, owner not assigned.
- It does not decide whether a test fixture is a governed README.
- It does not revisit the four values already ruled.
