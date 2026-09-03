# W37-6 — Ruling 102: the acceptance standard becomes an instrument, and the failing rows become the work list (2026-09-03)

**Filed** 2026-09-03 by the maintainer, recorded by the lead. **What this is.** Three windows
have now halted rather than ship a bad one-way commit, and each halt was caused by a defect
**a hand-built gate could not see** — not by a defect the gate saw and rejected. This ruling
stops rebuilding the gate by hand and makes it a script, and turns the six failing acceptance
rows into a work list with an owner each.

**It is filed as a dated maintainer ruling rather than another append to the delegation
record**, on the maintainer's instruction, because it is not a term of a window: **it removes
the window as the mechanism until a precondition is met.**

## Authority

- The decision is the maintainer's under `CLAUDE.md` §12. **An amendment to what a
  maintainer's own prior ruling required is the maintainer's alone**, and decisions 3 and 4
  below reverse parts of §8.5 and of an earlier deferral.
- **The maintainer's own grounds for the change of approach, verbatim:** *"This is rule 1 done
  properly; I should have written it this way the first time."*

## Ruling 102 — no further delegated window until §7 (a)–(i) is an instrument

<!-- Structural note: this heading exists so `_discover_multi_ruling_files`
     (`_RULING_HEADING_RE`, `^##\s+Ruling\s+(\d+)`) discovers this record as an `RL-` draft
     rather than falling through to `_discover_plain_plans`'s `PL- kind: leaf, owner: planner`
     catch-all — the defect F96 (`docs/audit/findings/F96.md`) was filed for. -->

**Ruling number derivation, run by the lead in its own worktree at `e5e20d6`** (decision 7's
own rule — a figure the lead has not run is marked relayed or is absent):

```
git grep -hE '^#{1,6}[ \t]+Ruling[ \t]+[0-9]+' origin/main -- docs/ \
  | grep -oE 'Ruling[ \t]+[0-9]+' | grep -oE '[0-9]+' | sort -n | uniq | tail -1   → 101
git grep -n 'Ruling 102' origin/main -- docs/ .claude/ scripts/                    → no match
```

**102 is the next free number**, derived rather than assumed.

### 1. The gate becomes a script, and the go-ahead becomes the script

**`doc-id.py migrate --verify <snapshot>`** — spelling not fixed here; `accept` is equally
acceptable. It:

- **runs the migration on a disposable snapshot**, never a real checkout;
- **computes all nine §7 (a)–(i) rows with their predicates, as one table**;
- **exits 1 on any fail.**

**It runs in CI on every PR touching `doc-id.py` or `audit-docs.py`, and is red on `main`
until green.**

> **"The go-ahead becomes: the script is green at the tree. No hand gate, no seven
> conditions."**

**Conditions 1–7 fold into it as rows, or are struck as covered.** Neither the seven nor the
sixteen survive as a hand-maintained table. **A row that cannot be expressed as a predicate the
script computes is a row that was never enforceable**, and the three windows are the evidence:
condition 7 alone was redefined once and had **four** blind spots measured in it, every one
found by someone measuring a different thing from what the check measured.

**Why an instrument and not a better table.** A table's rows are re-derived by hand each
window, and each re-derivation is a fresh chance to substitute a narrower predicate for the
name of a wider one. A script's predicate is the thing that runs. **`CLAUDE.md` §13's own
words — a count carries "the predicate it counted with" — are satisfied structurally once the
predicate is the artifact.**

### 2. The failing rows are the work list, one executor each, in this order

**The order is the maintainer's and is not a priority hint — it is the sequence.**

| # | row | the work |
|---|---|---|
| 1 | **(g)** | **The token-boundary bug.** *"A rewrite may not match inside a longer identifier."* **`NFR-RATE-13/14` is the broken-input proof.** |
| 2 | **(h)** | **The same-commit H rows that make `audit-docs.py`'s parsers see the migrated tree** — *"that's why (h) is vacuous, and those rows are W37-6's regardless of where the others sit."* |
| 3 | **(d)** | Per alternative. |
| 4 | **(b)** | **Allocate ids after exemptions so the sequence is contiguous.** |
| 5 | **(e)/(f)** | **Each gets one reading, ruled by the decision-maker citing §7's sentence — not two.** |

**On (g): the diagnosis is the maintainer's, not a symptom description.** The 391 mangled
citations are not a citation-rewrite scope question; they are **a token-boundary defect**. A
rewrite that matches inside a longer identifier turns `NFR-RATE-13/14` into `NFR-775/14` —
one real requirement and one meaningless fragment. That single example is named as **the
broken-input proof**, so the fix is falsifiable before it is written.

**On (e)/(f): two readings is not an acceptable state for an acceptance row.** Both were
reported with two readings and neither picked, which is correct for a *measurement* and wrong
for a *standard*. **The decision-maker rules each, citing §7's own sentence** — not the lead,
and not by choosing the more convenient number.

### 3. §7(i) is W37-10's — eight rows, and §8.5's nine were the lead's error

**Confirmed: (a)–(h) are W37-6's, (i) is W37-10's, (j)–(k) are W37-11's. Eight rows, not
nine.** The maintainer's words: *"my ruling on your framing corrected."*

**§8.5 records nine because the lead put "(a)–(i)" to the maintainer**, having **already been
corrected once on this same clause** — the map plan's coverage table assigns §5.2's H rows to
**W37-10**, whose acceptance is *"every §5.2 H row is named by a commit"*, which is §7(i)
verbatim. **The maintainer ruled on the lead's framing and has now corrected its own ruling.**
§8.5 stands as filed; this supersedes its row count.

**The carve-out (h) forces, and it is not optional:**

> **"Any H row without which `audit-docs.py` finds zero requirements lands with the run. Name
> them."**

**The naming is owed and is not attempted here.** The evidence is in place — on a migrated
tree `audit-docs.py` exits 1 with 547 failures and its *passing* lines read *"0 requirements
defined across 8 specs"* and *"0 of 0 §10 mirror rows carry their register status"* (**relayed**
— the auditor's measurement) — but **which H rows those are is a list nobody has produced, and
inventing it would be the same relay failure decision 7 exists to stop.** It is assigned, not
assumed.

### 4. `Ruling [0-9]+` = 74 is rewritten, not deferred

**Reversed from a deferral.** The maintainer's grounds, verbatim:

> **"Each has one target — the `RL-` the ruling became — so it's a determined single-target
> token under Ruling 100 (i). Deferral is for the ambiguous; this isn't."**

**So the 74 are work, not a disclosure.** They are exactly Ruling 100 clause (i) — a document
id adjacent to the path, naming its target — and the corpus already holds the mapping. Ruling
100 §4's rejection of option C applies directly: *"deriving nothing when the citation names its
target is discarding evidence the corpus already holds."*

**The count reached this ruling bare, with no reading attached, because that is what was
asked** (*"I want its count, not a recommendation"*). **The count being bare is what let the
decision be made on the ruling's own grounds rather than on the reporter's framing** — and it
is why the deferral was refused rather than confirmed.

**`\bF[0-9]{2}\b` remains excluded with its count disclosed** (§8.5); this ruling reaches
`Ruling [0-9]+` only.

### 5. Check 37's exemption keys on the parsed `was:` field, never a substring

**Ruled.** And: **condition 2's pass is re-measured after that.**

The exemption currently keys on a substring test. **Measured (relayed):** of 393 stamped
documents carrying a `was:` field, **3 carry correct provenance** — 261 name the file's own new
path, 129 name a path that never existed, and **90 of those name a real post-migration file
that is a different document.** So the *"enforced population is 0"* result recorded as
**condition 2's evidence**, accepted once by the maintainer with a disclosure under Ruling 96,
**was granted on a field that does not work.**

**Condition 2 is therefore not carried forward as MET.** Its pass is re-measured once the
exemption keys on the parsed field. This is the second time a `was:`-keyed result has needed
re-deriving, and both times the cause was a substring test standing in for a field test.

### 6. Ruling 101's cross-family placement — the route decides, not the sort order

**Ruled**, resolving the premise Ruling 101 clause 1 assumed and which does not hold — three
sources split **across** families, so `docs/<family>/INDEX.md` names no single family for them.

> **"The index section lives in the INDEX of the family §5.2 routes the source to —
> `closure-records.md` → `docs/closures/INDEX.md` — and lists every target with its path,
> including those in other families. One link, derivable from the route, no invention."**

**This is Ruling 101's own principle applied one level up.** The section still chooses no
target; it now also chooses no *family* — §5.2's routing table already decides where the
source goes, so the anchor's location is **derived** rather than picked. The executor's
sorted-first placement was the right conservative call and **stands until this is
implemented**.

### 7. Amendment 4 — the lead publishes no figure it has not run

**Extending the window's Amendment 2, which bound agents, to bind the lead specifically.**

> **"The lead publishes no figure it has not run in its own worktree. A relayed number appears
> with the word relayed beside it or not at all."**

**Grounds: §12 of the second-fail handover — eight lead errors in one window, every one a
relay, six of them caught by Amendment 2.** A figure or a scope restated without being
re-derived. The list includes a scope assertion that had already produced a wrong instruction
to an auditor, a lint fix that would have silently narrowed a predicate, a table whose own
three numbers did not sum, and two figures (`137`, and `OQ-OVR-11`'s claimants) that an
executor refused to reconcile to and was right both times.

**The rule is mechanical on purpose.** It does not ask the lead to be more careful; it makes an
unrun figure visibly labelled or absent, which is a property a reader can check.
**This record obeys it**: the ruling-number derivation above is the lead's own run, and every
measured figure in §3, §5 and §6 is marked **relayed**.

## What happens next, and what does not

> **"When `--verify` is green on main at a quiet tree, one window, one objective, run. Not
> before."**

**So there is no window now.** The sequence is: the instrument is built and green on `main`;
the six rows are fixed in the order of §2; then **one** window, **one** objective, and the run.

**Nothing in this ruling opens that window**, and the Work close remains the maintainer's
alone (`CLAUDE.md` §12).

## Acceptance Standard

**This record is accepted when it is merged.** Its substance binds from that point; the two
items it assigns rather than answers — the H-row naming of §3 and the (e)/(f) readings of §2 —
are owed by the parties named there, and **neither is discharged by this record**.

**Implementation: owed** (delegation §7.5 — a ruling names its implementing PR or carries
`implementation: owed`). **No implementing PR exists for any of the seven decisions.** The
instrument of §1 does not exist; the six rows of §2 are unstarted; §5's re-keying and §6's
placement rule are unimplemented, with the executor's conservative handling standing in §6's
place meanwhile.

### Acceptance — the violation that must become detectable

*Violation: a delegated window opened, or a migration run started, before `--verify` is green
on `main` at a quiet tree.*

*Violation: a hand-maintained gate table used as the go-ahead after this record merges — the
seven, the sixteen, or any successor table — rather than the script's own output.*

*Violation: a §7 row struck as "covered" without a predicate in the script that computes it.*

*Violation: the (g) fix accepted without `NFR-RATE-13/14` exercised as a broken-input proof,
red before green.*

*Violation: (e) or (f) recorded with two readings after the decision-maker's ruling, or ruled
by the lead rather than the decision-maker.*

*Violation: `Ruling [0-9]+`'s 74 treated as a deferral, or counted toward W37-11's owed
citation-form item.*

*Violation: condition 2 recorded as MET before check 37's exemption keys on the parsed `was:`
field and the pass is re-measured.*

*Violation: an index section placed by sort order rather than by §5.2's route, once §6 is
implemented.*

*Violation: a figure published by the lead that the lead has not run, without the word
`relayed` beside it.*

*Violation: the H rows of §3's carve-out treated as named when no list exists.*
