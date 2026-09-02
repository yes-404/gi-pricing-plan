# What `owner:` means: the family table, the historical author, or neither — a derivation for ruling (2026-09-02)

> **For agentic workers:** this is a derivation, not a plan and not a ruling. It answers four
> questions and recommends a shape. It binds nothing until the decision-maker rules on it.
> **PR #603 is held on it** and no code should be written to it before it is ruled.

**Goal:** answer the general question Ruling 88 routed here — *"does `owner:` follow §1.6's
family table, or the historical author?"* — with the divergence enumerated against real
documents rather than argued in the abstract.

**Spec:** [`../notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md) §1.6,
and `scripts/_docid.py`'s header schema.

**Tree:** every field list, line number and count below was read or produced at **`e2dccfb`**.

## Acceptance Standard

Complete when every item holds; each is a violation that must be detectable.

1. **The `was:` question is settled from the schema, not from a ruling's assumption about it.**
   *Violation: an answer to question 3 that cites Ruling 88 rather than the field's definition
   and its assignments.*
2. **The divergence is enumerated per family against §1.6's actual cells**, not asserted.
   *Violation: a claim that the readings "often" or "rarely" differ with no table behind it.*
3. **The answer names which of the three shapes it takes** — the table decides, the author
   decides, or §1.6 has a gap — and if a gap, says exactly where. *Violation: a recommendation
   that does not choose among the three.*
4. **The recommendation is handed over, not applied.** *Violation: this document changing any
   script, template or governed document.*
5. **`python3 scripts/audit-docs.py` and `python3 scripts/req-coverage.py` both exit 0.**

## Global Constraints

- **The decision is the decision-maker's.** A planner derives and recommends.
- **No filed document is edited**, and no ruling is corrected — where a ruling's supporting
  sentence is wrong, that is stated with what survives it.
- **Requirement ids and section numbers are permanent** (`CLAUDE.md` §5).

---

## 1. Question 3 first, because it is load-bearing: `was:` does not carry authorship

**It carries the old id or the old path. Nothing else, and no field carries the author.**

**The schema, read rather than inferred.** `scripts/_docid.py` declares the complete key set:

```
_STR_FIELDS          family, title, status, owner
_OPTIONAL_STR_FIELDS id, kind, phase, work, tree, superseded_by, corrects, was, origin
_LIST_FIELDS         plans, supersedes, corrected_by, relates
_KNOWN_KEYS          the above, plus slice, created, vendored
```

**Twenty keys. None of them is an author.** There is no `author:`, `drafted_by:`, `by:` or
equivalent, and `_KNOWN_KEYS` is closed — check 30 fails an unknown field, so one cannot be
added by convention.

**What the standard says `was:` is for.** NT-0019 §4 step 1: *"`was:` and `REDIRECTS.csv` keep
every old **id and path**."* Ids and paths. Its own worked examples are the same shape —
`was: NT-0019`, `was: Ruling 62`, `was: F27`, `was: 2026-08-18-profile-contract.md`.

**What the code assigns.** Every one of the migration's `was=` assignments is a path or a token:
`path.relative_to(root).as_posix()` at `scripts/doc-id.py:1034`, `:1083`, `:1394`; `rel` at
`:1152`, `:1186`; the literal `"docs/audit/closure-records.md"` at `:1268`; `None` at `:2024`.

### 1.1 So Ruling 88's disposal of the objection has the hole the lead anticipated

Ruling 88 §2 ground 1: *"The planner's authorship is not erased by this; it is in the body and
in `was:`."* **The `was:` half is false.** `was:` will carry
`docs/audit/plan-reviews.md` — a path, from which no author is recoverable without already
knowing who wrote that file.

**And for its own subject the body half is false too.** The container carries no byline, no
`owner:` line and no author field; its heading gives a drafting date and nothing more.

**Ruling 88's outcome survives, and this is not a challenge to it.** Grounds 2 and 3 are
independent and hold: `owner: planner` would be the only `RFC-` contradicting §1.6, with
nothing to catch it; and the container's own text — *"takes them to the maintainer"* — makes it
a proposal *to* the maintainer. One supporting sentence is wrong; the ruling is not.

### 1.2 The consequence the lead asked me to test, and it lands somewhere else

The lead's worry: *"if `was:` does not carry it, adopting the family table silently destroys the
record that the lead ruled A1–A3 under delegation."*

**The record is not destroyed by `owner:`, and it is not preserved by the body either. It is
severed by the split.** Rulings A1, A2 and A3 sit at
`docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md:67,81,96`. **Their own subsections mention
neither the delegation, nor the lead, nor the maintainer** — checked line by line. The
delegation lives at **§1.1 of the same file**, under a different heading, which the split leaves
with the residual `PL-`.

So under the recommended three-`RL-` split, each ruling record is separated from the only
artifact that records the authority under which it was made — **whatever value `owner:` takes.**

**The remedy is therefore not an `owner:` value.** Setting `owner: lead` would encode the
*author* while still losing the *authority*, and would put a value in `RL`'s `owner:` that §1.6
does not admit. The remedy is a **cross-reference obligation on the split**: each of the three
`RL-` records carries a `relates:` to the `PL-` the delegation stays in, or the delegation
clause is reproduced in each record's body. Both are cheap; neither is an `owner:` question.
**Named here, not decided — it is a consequence of Ruling 86's split, and it goes back with
this.**

---

## 2. Question 2: what `owner:` is for — answered by §1.6's own column heading

**§1.6's column is titled "Owner — creates & amends".** It is one of **five** relationships the
table defines per family; the other four are "Accepts / decides", "Reads & acts", "Verifies &
closes" and "Supersedes / retires". The header field captures the first and only the first.

**Nothing reads `owner:` as authorship, because there is nothing to read it with.** Its one
consumer in the gate is `check_owner` (check 35), which tests membership only:

```
_VALID_OWNERS = frozenset({"maintainer", *(p.stem for p in _ROLES_DIR.glob("*.md"))})
```

Eight values at `e2dccfb`: `maintainer`, `auditor`, `decision-maker`, `executor`, `lead`,
`planner`, `reporter`, `watcher`. **`lead` is a valid stem**, so `owner: lead` on an `RL-`
passes check 35 — the hole Ruling 88 named, confirmed here independently.

**So the "two fields conflated into one" diagnosis is wrong in a specific and useful way.** There
are not two fields fighting over one slot. There is **one field, meaning *who may amend*, and a
missing one**. If authorship is to survive the migration as data rather than as prose, that is a
**new field**, not a reinterpretation of this one — and adding it is a §1 amendment, which is
the maintainer's.

---

## 3. Question 1: where the two readings actually diverge

**The table is not a list of values. It is a set of sentences, and only some of them yield one
role.** Classified against §1.6's own cells:

| Bucket | Rows | Yields a single `owner:`? |
|---|---|---|
| **A — one role, stated plainly** | `OQ`, `SL`, `WF`, `ADR`, `PL review`, `PL handover`, `LG`, `RS spike/measurement`, `FD`, Reference—agents | **Yes.** The cell names one role and nothing else |
| **B — one role after a rule the cell implies but never states** | `RFC` (*"mints and **owns**"* — the verb disambiguates), `CR` (*"auditor (`work`, `phase`); lead (`review`)"* — `kind:` disambiguates), `RL` (*"decision-maker; the maintainer **may**"* — primary vs conditional), `PL map/leaf` and `RS audit` and Reference—`process/`/charters (the semicolon introduces a duty or a route, not a second owner) | **Yes, but the reader must supply the rule.** Ruling 88 had to infer *"owns wins"* for `RFC`; §1.6 never states it |
| **C — several roles, no disambiguator** | **`Phase`** (*"maintainer opens the section; lead maintains it"*), **`WK`** (*"maintainer opens; planner writes its map plan; maintainer sets `active`"*), **Reference—skills** (*"the five roles already permitted; lead approves"*), **Reference—`contracts/`** (*"generated from `model-schema`; `gi-pricing.yaml` executor"*) | **No.** The cell describes a lifecycle across roles, and a single-valued field cannot hold it |

**Bucket C is where the question actually lives, and its largest member is not `RL`.**

| Bucket C row | Files needing an `owner:` at the migration |
|---|---|
| Reference — skills | **46** `SKILL.md` |
| Reference — `contracts/` | 61 (generated) |
| `WK` / `Phase` | the roadmap's rows and phase sections |

**And no code assigns one.** Every `owner=` in `scripts/doc-id.py` sits inside a
`_discover_*` for a *governed document* family — notes, ADRs, rulings, closure records, plans,
requirements, roadmap rows, the register. **`_discover_vendored_skill_manifests` assigns no
owner, and there is no discovery or stamp path for `.claude/skills/`, `.claude/agents/` or
`.claude/roles/` at all** — while §4 step 5 stamps all of them and check 35 will demand a valid
owner on every one once the scope widens.

**The divergence between "table" and "author", enumerated for the family that prompted the
question:** `RL`'s cell names the decision-maker and, conditionally, the maintainer. Rulings
A1–A3 were made by the **lead** under the §1.1 delegation — a role the cell does not name.
**Three documents.** By itself that is a small question. Bucket C is not.

---

## 4. Question 4: does a bounded delegation transfer ownership, or only drafting?

**§1.6 does not contemplate delegation at all.** No row has a delegation clause; the word does
not appear in the section. So the question cannot be answered from the table, and the executor's
reading — that the delegation transfers ownership — is a genuine argument rather than a mistake,
made in the absence of a rule.

**The two readings, and what each costs:**

- **Delegation transfers drafting only.** `owner:` stays `decision-maker` for A1–A3. The field
  keeps meaning *who may amend*, consistently with §1.6 and with Ruling 88's own logic applied
  to `RL`. Cost: nothing in the header records that the lead made them — which §1.2 shows is
  already true of every document, since no field records authorship for any of them.
- **Delegation transfers ownership.** `owner: lead`. Cost: the only `RL-` in the corpus whose
  owner contradicts §1.6, invisible to check 35; and it answers *"who wrote this"* with a field
  the other 80-odd records use for *"who may amend"*, so the field stops meaning one thing.

**The delegation's own text decides it, and it decides against transfer.** §1.1 is explicit and
deliberately narrow: it covers *"the landing of NT-0012, NT-0013 and NT-0014, and nothing
else"*, and *"does **not** convert the lead into the maintainer for other purposes."* A
delegation that declines to convert the role for other purposes is a grant of an **act**, not of
an **ownership**. Amending those rulings later is one of the other purposes.

---

## 5. The answer, and its shape

**Of the three shapes the lead named, it is the third: §1.6 has a gap — and there are two,
which are different problems with different owners.**

**The table wins where it yields a value**, which is buckets A and B, and that covers `RL`, so
**question 4 resolves to `owner: decision-maker` for Rulings A1–A3** and PR #603's
`_ruling_file_owner` is wrong to derive `lead` from the delegation clause. `_PLAN_KIND_OWNER`,
its other half, is right. **The two halves are not two readings of one rule; one applies the
rule and the other applies a rule that does not exist.**

**Gap 1 — the disambiguating rule in bucket B is never stated.** Ruling 88 supplied it correctly
for `RFC` and its reasoning generalises, but the next reader re-derives it. *Recommendation: a
ruling states the rule — where a cell names several roles, `owner:` is the one the cell says
**owns**, or the one selected by `kind:`; a conditional clause (`may`) never displaces the
primary.* No §1 amendment needed; this reads §1.6 rather than changing it.

**Gap 2 — bucket C has no value to state, and it is the migration's largest stamp population.**
46 `SKILL.md` files, 8 agents, 7 charters, the roadmap's rows and phase sections. *This is a §1
amendment and therefore the maintainer's* (`CLAUDE.md` §12). **Recommendation: it is raised as
an `RFC-`, not resolved inside W37-6** — and until it is, the migration cannot stamp a
defensible `owner:` on those files. **That makes it a W37-6 precondition, and it is not on any
list I have seen.**

**And a third thing, which is neither reading:** authorship is carried by no field, for any
document. If the project wants it preserved as data, that is a new field and a §1 amendment. If
prose is enough — which it has been until now — then §1.2's severance finding is the live risk,
not `owner:`.

---

## 6. What this derivation does not do

- **It does not rule.** The decision is the decision-maker's; gap 2 is the maintainer's.
- **It does not challenge Ruling 88's outcome.** §1.1 records that one supporting sentence is
  wrong and that two independent grounds carry it.
- **It does not fix `_ruling_file_owner`.** PR #603 is held; §5 says which half is wrong and why.
- **It does not decide the severance remedy** of §1.2, which is a consequence of Ruling 86's
  split and goes back with this record.
