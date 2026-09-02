# RFC — the README row, the cell-extent rule, and §4 step 5's stamp set

**Date:** 2026-09-02 · **Tree:** `ffdd54c` · **Author:** the lead, recording the maintainer's
rulings · **Status:** `active`

**Authority.** The maintainer's rulings of 2026-09-02, following the README `owner:` derivation
([`…-w37-readme-owner-derivation.md`](2026-09-02-w37-readme-owner-derivation.md)) and the
counterexample hunt it produced. **Companion to, not part of,**
[`…-w37-rfc-bucket-c-owner-values.md`](2026-09-02-w37-rfc-bucket-c-owner-values.md).

## Why a second RFC rather than an append — the lead's answer, as asked

The maintainer asked whether the bucket-C RFC is past the point where appending is cleaner, and
said the substance does not change either way. **It is not a question of volume — 153 lines takes
four appends comfortably. It is that all four are outside that RFC's own declared scope, and it
says so itself.**

Its Global Constraints fix the scope at *"the four bucket-C rows of §1.6 and nothing else"*, and
**its §4 states of the README row: *"This is out of scope by constraint (a) and is not proposed
here."*** Appending the README row would make one document assert and deny the same thing, four
sections apart. Two of the four amendments are not `owner:` questions at all — they are **stamp
scope** — so they would sit under a title about owner values and be missed by anyone reading it
for what it says it is about.

**A filed document's scope clause is load-bearing or it is decoration.** This one was the
maintainer's own constraint (a), written to stop exactly this widening.

---

## Acceptance Standard

The violation this record must make detectable: **a `README.md` whose family is decided by its
filename, or a stamp set that two documents describe differently.**

1. No `README.md` is assigned a family by filename alone. **Violation:** a file taking Reference
   because it is called `README.md`, where §5.2 routes it elsewhere — the defect §1 exists to
   remove, and the one that would have mis-owned 17 closure records.
2. §4 step 5 and §5.2 name the same stamp set. **Violation:** a file one reaches and the other
   does not, which is the disagreement §4 resolves.
3. Every `tests/fixtures/` exemption is a **declared** entry in the census, not a path prefix
   swallowing a subtree. **Violation:** a fixture exempted by living in the directory rather than
   by being named.
4. The arithmetic in §4 closes: **six reached, one exempt, five stamped.** **Violation:** a total
   that does not decompose, which is how an exemption list grows silently (F83, condition 2).
5. No filed document is edited by this RFC, including the bucket-C RFC it accompanies.

---

## 1. The README row — routing decides the family, not the filename

**Ruled:**

> **A `README.md` takes the family §5.2 routes it to; one routed nowhere is Reference — README,
> `lead`. Population 14.**

**What this fixes.** The candidate row said *"every tracked `README.md` is in the family"*, and
the planner found that clause wrong for **17 files**: `docs/audit/work/*/README.md` (16) and
`docs/audit/phases/1b/README.md` (1). §5.2 routes those to `CR-` with `kind: work`/`phase`; §1.6's
`CR` row (`0019-one-id-per-document.md:152`) assigns that family to the **auditor**; and their own
first headings read *"# Work-item record — W11"*, *"# Phase record — 1b"*. **They are closure
records with a README filename**, and the filename was the only property they shared with the
rest.

**The amendment makes routing the discriminator**, which is the property that actually
distinguishes them. The 17 are then out of this row by construction rather than by exception —
there is no list to maintain and nothing to keep in step.

**The 17 are F84's, not this row's.** That finding stands on its own: they have no discovery code
and no census covers them (§5).

---

## 2. `docs/contracts/README.md` → `lead`, and the general rule that decides it

**Ruled:** `docs/contracts/README.md` takes **`lead`**, and:

> **A cell governs what its text names; an index is the README row's.**

**The collision.** The `contracts/` row was ruled *"`executor`, all 61"*, and `docs/contracts/` is
59 `.json` + 1 `.yaml` + **1 `.md`** — the `.md` is the README. So two ruled values reached one
file.

**Why `lead` wins.** The contracts cell names **the generator and `gi-pricing.yaml`**. It does not
name a hand-authored index, and §4.2's reasoning for that row was that the files are *generated*
and *cannot carry a header* — neither true of the README. **The population was drawn by directory
while the argument was drawn by format**, and the README is the single file where those diverge.

**The general rule is the durable part**, and it is wider than this case: a cell's extent is what
its **text** names, not the directory its examples happen to share. Every future row inherits it,
which is why it is stated as a rule rather than as a disposition for one file.

---

## 3. `tests/fixtures/` — exempt by path, each file declared

**Ruled:** `tests/fixtures/` is exempt by path, **each file a declared exception in the census.**

**Why an exemption is needed at all.** `tests/fixtures/docs-ids/w37-4-checks/check35-readme-allowlist/README.md`
is **deliberately headerless** — its own test says a header there *"would then also red check 30,
contaminating this check-35 proof."* A rule that stamps every README would stamp a file built to
be bare, breaking the proof it exists to carry.

**Why "declared", not a prefix.** A path prefix silently swallows every future file under it. A
**declared** exception is named, so the census can assert that the exempt set equals the
unstamped-in-scope set — **F83's condition 2 applied to a second population.** The exemption list
then cannot grow without an arithmetic failure saying so.

---

## 4. §4 step 5 governs the stamp set, and gains six

**Ruled:** **§4 step 5 governs the stamp set**, and gains the six READMEs §5.2 reaches that its
globs do not.

**The disagreement.** §4 step 5 stamps *"every file under `docs/`, `.claude/roles/`,
`.claude/skills/*/SKILL.md`, `.claude/agents/`"*. §5.2 reaches six files those globs miss —
`.claude/skills/README.md`, which `*/SKILL.md` structurally cannot match, plus the five outside
`docs/`. **Two sections of one standard described different stamp sets**, and the leaf plan's §10
finding 7 had generalised from one file to six.

**The six, named** — derived at `ffdd54c`, not counted:

| File | Why step 5 misses it |
|---|---|
| `.claude/skills/README.md` | `*/SKILL.md` matches a manifest, never the directory's own index |
| `README.md` (root) | outside every listed root |
| `deploy/README.md` | outside every listed root |
| `examples/fremtpl2/README.md` | outside every listed root |
| `packages/README.md` | outside every listed root |
| `tests/fixtures/…/check35-readme-allowlist/README.md` | outside every listed root |

**The arithmetic, stated because two rulings interact and the total would otherwise not
decompose:** step 5's scope **gains six**; **one of the six** — the check-35 fixture — is then
**exempt by §3**; so **five are newly stamped.** Scope and exemption are different layers, exactly
as in F83: a file is in scope *and* exempt *and* listed, rather than quietly absent.

---

## 5. F84 joins W37-5c

**Ruled:** F84 joins the slice, **discharged exactly per its falsifiable section** — discovery
**plus** a census that names the unmatched unit, proven on broken input. **Not** by the 17 landing
on the right owner.

**That last clause is the whole of it.** §1's routing rule means the 17 no longer take `lead`, so
the *symptom* is gone. **The defect is not.** `scripts/doc-id.py` still contains zero references
to `audit/work` or `audit/phases`, and no census covers the path — so the 17 remain invisible to
the migration, and the next corpus change there is unprotected. **A finding discharged by the
disappearance of its symptom is a finding that will recur under a different name.**

---

## 6. What this does not do

- **Does not edit any filed document**, including the bucket-C RFC it accompanies.
- **Does not grant W37-6's go-ahead**, or bear on it beyond adding F84 to W37-5c.
- **Does not re-open gap 2's four ruled rows** — §2 clarifies one cell's *extent*, which the
  cell-extent rule decides, and changes no ruled value.
- **Does not decide who owns the six newly-stamped READMEs** beyond §1's routing rule: five are
  routed nowhere and take Reference — README, `lead`; the sixth is exempt.

---

## Corrections after filing

**2026-09-02 — §1 and §2 treat `§5.2` as a source of `owner:` values. It is not one, and the
maintainer has ruled the constraint's scope.**

> *"'Cite the cell' means §1 — a §1.6 cell or a §1 sentence naming a role. §5.2 is the impact map
> and grants nothing; if it sourced a value it would be a second authority over the same files."*

**So the README population is uniform: all fourteen take `lead` from the README row**, and
`.claude/agents/README.md` is not a special case. §5.2 line 347 — *"README names agents as
Reference family owned by the lead"* — is recorded as **consistent with the row, not as its
source**.

**Why the distinction is worth more than the one value it moves.** §1 is the standard and §5.2 is
the map of what the migration does. Reading a grant out of the map would make **two documents
authoritative over the same files**, and they would then be free to diverge — which is `NT-0003`'s
mechanism, applied to ownership rather than to status. The derivation's *"one sourced, thirteen
unsourced"* framing is therefore superseded: **fourteen sourced, from one row, with one
corroborating sentence in the map.**

**§2 is unaffected in substance.** `docs/contracts/README.md` still takes `lead`, and still does so
because *a cell governs what its text names and an index is the README row's* — the cell-extent
rule, which is a §1.6 reading and never depended on §5.2.

**§4 is unaffected.** It concerns the **stamp set**, not ownership; §4 step 5 and §5.2 disagreeing
about which files are stamped is a question about the migration's own scope, which is exactly what
§5.2 is for.
