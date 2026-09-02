# W37-5c — the slice decision, and gap 2 ruled

**Date:** 2026-09-02 · **Tree:** `2e48960` · **Author:** the lead, recording the maintainer's
instruction · **Status:** `active`

**Authority.** The maintainer's dated line of 2026-09-02 on
[`2026-09-02-w37-6-go-ahead-ask.md`](2026-09-02-w37-6-go-ahead-ask.md) §8 — *"Decision: not yet.
Date: 2026-09-02."* — together with the sequencing and gap-2 rulings in the same instruction. **A
go-ahead for W37-6 is not granted and is not sought here.**

**What this is.** The slice cut, its scope, and the `owner:` rule W37-5c builds against. **Two
points the maintainer asked to have challenged are in §4, and one of them changes their
instruction.**

---

## Acceptance Standard

The violation this record must make detectable: **a slice built against a rule that was inferred
rather than ruled, or a scope narrower than "everything that stops or blinds the run".**

1. Every scope item in §2 traces to the maintainer's own words or to a numbered finding.
   **Violation:** an item in scope that neither quotes the instruction nor cites an `F-` id.
2. Every `owner:` value in §3 cites the §1.6 cell it is read from. **Violation:** a value derived
   from what a role *ought* to own rather than from a cell — the failure the RFC was written to
   prevent.
3. §4's two challenges are answered before the slice starts, not during it. **Violation:** an
   executor building `contracts/` header emission before the impossibility in §4.2 is ruled.
4. No frozen plan is edited by this decision. **Violation:** either leaf plan, or the ask,
   modified to agree with anything decided here.
5. The slice's own arithmetic closes over the **real corpus**, not a fixture. **Violation:** a
   census or count in W37-5c evidenced only against `tmp_path`.

---

## 1. The decision

**`W37-5c` is inserted between `W37-5b` and `W37-6`.** It is the second slice cut from the same
mechanism as W37-5b: work that **must land outside the irreversible commit** because it is
provable on deliberately broken input and the migration commit is not re-runnable.

**The criterion is the maintainer's and is wider than the three abort guards:** *"everything that
stops **or blinds** the run and is provable on broken input outside it."* A check that cannot
fail **blinds** the run as surely as a guard that aborts **stops** it — which is why Addendum A's
two owed acceptance items are in scope rather than carried forward.

---

## 2. Scope — six items

| # | Item | Why it is in scope | Evidence |
|---|---|---|---|
| 1 | **F80, F81, F82** | The three unconditional guards that abort a real `migrate()` run, in pipeline order | Ask §5.1; `doc-id.py:2984`, `:3000`, `:3008` |
| 2 | **The discovery-and-stamp path for `.claude/skills/`, `.claude/agents/`, `.claude/roles/` and the README population** | Stamp targets with no discovery coverage. **The README figure in this row was wrong when written and is corrected here rather than left**: 32 was a relayed raw count, the true raw count is **33**, and the population that matters is **14** — the rest are not Reference documents after the migration (17 become `CR-`, and two are deleted with the trees they index). **Also in scope: §4 step 5 and §5.2 disagree about which READMEs are stamped at all** — step 5 reaches 8 of the 14, §5.2 reaches six more that step 5's `*/SKILL.md` glob cannot match, and §5.2's *"every README outside `docs/`"* reaches, literally, the fixture built to exercise check 35's own owner allowlist | Handover §6; §3 row 5 below |
| 3 | **The three unparseable vendored manifests** | A stamping precondition on no list — Ruling 69 settled *stamping* a vendored file, not one whose front matter does not parse | §5 below |
| 4 | **R84 §4 item 2 built** | Vacuous at birth: `_stamp_header` skips `slice` unconditionally, so nothing can write the value the check reads. **Blinds** | Addendum A row 1; `doc-id.py:946`; register F77 |
| 5 | **R86 §4 item 3 rebuilt so it can pass on some input** | After `2e48960` the value it demands cannot be produced by any input, by construction. **Blinds** | Addendum A row 4 |
| 6 | **Same discipline as W37-5b** | Red-before/green-after on every fix; **the arithmetic closes over the real corpus** | Maintainer's instruction, verbatim |

**Not in scope, explicitly:** the README `owner:` row (§3 row 5), which the maintainer has routed
to the planner rather than folded in; and anything in W37-6's own task list.

---

## 3. Gap 2, ruled — the `owner:` value for §1.6's four unsourced rows

**Ruled by the maintainer, 2026-09-02**, discharging the `RFC-` filed at `d47a5f5` (#613). Each
value cites the cell it is read from, which was the RFC's binding constraint.

| Row | Value | The cell it is read from |
|---|---|---|
| **Phase** | **`lead`** | §1.6's Phase row amends cell: *"maintainer opens the section; **lead maintains it**"*. §1.6 makes the maintainer the **acceptor** — *"maintainer closes"* — not the routine author |
| **WK** | **`maintainer`** *(as read — see §4.1)* | §1.6's WK row: *"maintainer opens (`draft`); planner writes its map plan; maintainer sets `active`"*. Both state transitions are the maintainer's; the planner's artifact is a different document |
| **Skills** | **`lead`**, one standing value | The approves/retires cells. **Per-skill authorship is a missing field, not this one** — the maintainer's words, and the distinction that dissolves the row |
| **`contracts/`** | **`executor`**, all 61 | The generate/regenerate cells — **but see §4.2, which changes how the value is carried** |
| **README** | **not ruled — one of 14 is sourced** | The derivation is filed (PR #624). **The population is 14, not 33.** Exactly one value has a cell: §5.2 line 347 names agents' README *"Reference family **owned by the lead**"*, so `.claude/agents/README.md` → `lead`. **For the other thirteen there is no cell**, and the derivation's own output is therefore the finding: **§1.6 needs a README row**, which is a §1 amendment and the maintainer's. See §4.3 |

---

## 4. The two points the maintainer asked to have challenged

### 4.1 `WK` → `maintainer`: the principle bites, and the asymmetry with `Phase` is real

**It bites.** `CLAUDE.md` §12 reserves acceptance of a Work close to the maintainer, and §1.6's WK
row says *"maintainer accepts the close"*. Setting `owner: maintainer` makes the maintainer **both
the routine author of the row and the acceptor of its close** — precisely the collapse that
`Phase → lead` was chosen to avoid, by the maintainer's own stated reasoning.

**But the asymmetry is real rather than an inconsistency, and this is why the answer differs.**
The `Phase` cell names an explicit routine maintainer *of the row itself* — *"lead maintains
it"* — so `lead` is the true author and the maintainer's role there is genuinely only acceptance.
**The `WK` cell names no such person.** Both WK state transitions, `draft` and `active`, are
performed by the maintainer personally; the planner writes the **map plan**, a different artifact
with its own id. So for `Phase` the collapse was an artefact of reading the wrong actor; for `WK`
there is no delegation being papered over — the maintainer really does author and really does
accept.

**There is also no alternative that satisfies the constraint.** `lead` is available only from
*"lead runs it"*, which is the **uses** column, not creates-and-amends. Reading a value out of the
wrong column is the failure the *"cite the cell"* constraint exists to prevent, and it would be
worse than the collapse it fixes.

**Recommendation: keep `maintainer`, and record the reason** — the collapse is genuine but
narrower than for `Phase`, because no separation is lost that the cell ever established. **If the
maintainer wants the separation anyway, the clean fix is a §1 amendment** naming a routine
maintainer of the WK row, which is theirs and not this slice's. Flagged as asked; not decided
here.

### 4.2 `contracts/` → `executor`: the generator **cannot** emit the header, for 59 of the 61

**The maintainer's option — *"the generator emitting the header so regeneration doesn't strip
it"* — is not available, and the reason is stronger than cost.** Measured at `2e48960`:

```
59 × .json   1 × .yaml   1 × .md      (git ls-files docs/contracts/)
```

**A JSON file cannot carry a YAML front-matter header.** JSON has no comment syntax; prepending
`---` … `---` produces a file that is not JSON, and every consumer fails at parse — `json.load`,
the OpenAPI toolchain, and `frontend/src/api/generated`'s generator. This is not *"a bigger
change"*; it is **a format impossibility for 59 of 61 files**, and no amount of generator work
changes it. The `.yaml` file is in the same position for the same reason: front matter ahead of
`openapi: 3.1.0` breaks the document.

**So the maintainer's own fallback is the answer: take the `generated: true` exemption in check
35** — they wrote *"say so and I'll take the exemption"*, and this record says so.

**A third option exists and is worth one line, because it also answers §5.** A **sidecar** — one
manifest carrying the header fields for files that cannot hold their own — serves `contracts/`
and the unparseable vendored manifests with a single mechanism rather than two. It is more work
than the exemption and buys machine-readable ownership for 61 files the exemption would leave
unowned. **Not recommended for this slice**; named so the exemption is chosen knowing what it
forgoes.

### 4.3 The README row: one sourced value, thirteen with no cell, and a constraint question

**The population is 14.** The planner derived it by asking what the migration does to each of the
33 raw READMEs rather than counting them: **17 become `CR-`** (16 work + 1 phase), `audit/README.md`
is deleted, `.claude/notes/README.md` goes with the stubs. **Verified by the lead** — 33 raw, 17
under `docs/audit/work/` and the phase directory. *(§5.2's own row says 15 work READMEs where 16
now exist; the planner used the rule, not the count, which is why the figure survives the drift.)*

**One value is sourced.** §5.2 line 347: *"README names agents as Reference family **owned by the
lead**"* — an owner stated outright, not a verb to be read. So `.claude/agents/README.md` → `lead`.

**And that raises a question the maintainer must settle, because it is their constraint.** That
citation is a **§5.2** cell, not a **§1.6** one. If *"cite the cell"* means §1.6 specifically, this
value falls back with the rest and all fourteen are unsourced.

**The lead's reading, offered as a recommendation:** it satisfies the constraint, and satisfies it
**better** than the four already ruled. The constraint exists to stop a value being derived from
what a role *ought* to own; §5.2 line 347 **states the owner** where §1.6's Phase row required
reading a verb. A cell that names the owner is the strongest possible provenance, and §1.6 does not
reach the file at all.

**Thirteen have no cell, and the derivation's output is that finding: §1.6 needs a README row.**
That is a §1 amendment and the maintainer's.

**One reading was found that would source six more, costed and declined.** *"An index inherits the
row of the tree it indexes"* needs **two** steps where the ruled four needed one — the verb reading,
**plus a prior inference that a row governing a family also governs its index**, which §1.6 states
nowhere. It also **fails on the two largest indexes**, `docs/plans/README.md` and `docs/README.md`,
for the same reason Reference-skills failed: a tree with several owners has no single row to
inherit. **Six of thirteen at the price of an unstated inference is worse than a row that resolves
all fourteen** — and declining it is the constraint working as intended.

---

---

## 5. The three unparseable vendored manifests — the option, as asked

**`CLAUDE.md` §12 is absolute: vendored files stay as upstream wrote them.** The maintainer's
constraint follows — *"a manifest that won't parse gets its header from a sidecar or an
exemption, never an edit"*. Both options are therefore edit-free by construction:

- **Exemption** — the three are named in an exempt-by-path list, as `docs/_templates/` already
  is under NT-0019 §1.4. Cheapest; leaves them unowned and invisible to checks 30–39; the
  exemption list becomes the record of which files are unstamped and why.
- **Sidecar** — the header lives beside the file rather than in it, and the same mechanism serves
  `contracts/` (§4.2). Keeps every governed file owned and machine-readable; costs a new
  convention, a parser change, and a rule for keeping sidecar and file in step.

**The lead's recommendation: exemption for this slice, sidecar recorded as the option not taken.**
Two unstamped populations are a known, listed gap; a new convention introduced inside a
precondition slice is the kind of scope growth that put W37-6 where it is. **The maintainer's
call, and it is the only thing in §2 item 3 that is not already decided.**

---

## 6. What this decision does not do

- **Does not grant W37-6's go-ahead**, or ask for it.
- **Does not rule the README `owner:` row** — routed to the planner.
- **Does not amend NT-0019 §1** — §4.1's alternative and §4.2's exemption are both flagged to the
  maintainer, not taken.
- **Does not edit any frozen plan**, including either leaf plan and the ask.

---

## 7. The re-ask, and its four conditions

Quoted from the instruction, because these are what the next ask is built to and nothing else:

> *"§3 and §4 re-derived at that tree, the addendum merged and re-run, F80–F82 shown cleared by
> execution. Then I read one document and write one line."*

**One document.** The re-ask is a single record, not a package: the re-derived disclosure, the
re-run addendum, and the execution evidence that the three guards no longer abort — with the
maintainer's line at the end of it.
