---
id: RL-1040
family: ruling
title: `RL.md`'s body shape becomes RL-984's four sections; the detector is asymmetric and excludes placeholder headings
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-03
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-03-w37-6-d1-d2-rulings.md
---

## RL-1040 — `RL.md`'s body shape becomes RL-984's four sections; the detector is asymmetric and excludes placeholder headings

### 1. Verified first, at `15ed00d`

**(a) The template's declared shape describes no ruling ever written.** `docs/_templates/RL.md`
declared four `##` sections at lines 41, 46, 51 and 55 of the file as it stood at `15ed00d`:
`Question`, `Ruling`, `Rationale`, `Acceptance — the violation that must become detectable`.
Measured over the real corpus — every heading under a `## Ruling <n>` block in `docs/plans/`,
with a leading `N. ` ordinal stripped, **94 ruling blocks at `15ed00d`**:

| Heading text | Blocks carrying it |
|---|---|
| `Ruled` | **48** |
| `What it obliges` | **39** |
| `Acceptance — the violation that must become detectable` | **32** |
| `Verified first, at <a sha>` | 40, across **18 distinct texts** |
| `Question` | **0** |
| `Rationale` | **0** |

**Three of the four declared sections are written by nobody; three sections written by most
rulings are declared by nothing.** The template was aspirational in one direction and blind in
the other.

**(b) RL-984 is the shape that is actually used.**
`docs/rulings/RL-00984-owner-is-who-may-amend-the-a-series-takes-decision-maker.md` lines 61, 107, 134 and 156 are its
four sections:

```
### 1. Verified first, at `64f63ee`
### 2. Ruled
### 3. What it obliges — and what is *not* struck
### 4. Acceptance — the violation that must become detectable
```

**(c) `Verified first` cannot be a required literal, and that is a fact about the corpus, not a
choice.** Its text carries the tree: 40 occurrences, **18 distinct strings**. A literal match can never
require it.

**(d) A symmetric detector would create an unsatisfiable requirement — measured, not feared.**
`docs/_templates/SL.md:18` and `docs/_templates/WK.md:17` declare exactly one body heading
each, both at `###` and both pure placeholder. Deriving required sets both ways:

```
work     asymmetric=[]  symmetric=['WK-NNNNN — <Title>']
slice    asymmetric=[]  symmetric=['SL-NNNNN — <Title>']
```

**A required section no document can ever carry.** It is latent today only because the migrated
corpus holds zero `slice` and zero `work` documents — the trap the decisions record named
(`2026-09-03-w37-6-maintainer-decisions.md`, D1 recommendation: *"a latent trap measured as
harmless only because the migrated corpus holds zero documents of either family"*).

### 2. Ruled

**`docs/_templates/RL.md`'s body becomes RL-984's four sections** — `Verified first, at
<tree>`, `Ruled`, `What it obliges`, `Acceptance — the violation that must become detectable`.

**The detector is asymmetric**: the required set is derived from the template at `##`
**exactly**, as now; a document is scanned at **any depth**, with a leading `N. ` / `N.N. `
ordinal stripped. **Placeholder headings are excluded** from the required set — a template
heading whose text holds a `<…>` placeholder or a run of four or more `N`s is not a constant
and cannot be a required literal.

The resulting required set for `ruling`, run:

```
RL required set: ['Ruled', 'What it obliges', 'Acceptance — the violation that must become detectable']
```

`Verified first, at <tree>` stays in the template as the shape an author copies, and is
required of the author, not of the checker. `Question` and `Rationale` are gone: their content
is absorbed into `Verified first` and `Ruled` respectively, where the corpus already puts it.

**The option not taken, priced: a symmetric depth-agnostic detector**, which is F90's option 4
and the one the 2026-09-02 order named. **Struck.** It costs the unsatisfiable
`SL-NNNNN — <Title>` / `WK-NNNNN — <Title>` requirements measured in §1(d), and it buys nothing
F90 has not already measured at `95 → 95` (`F90.md` §B item 1). The two mechanisms adopted
instead close that trap from **both** sides independently — asymmetry, because SL/WK declare no
`##` heading at all; placeholder exclusion, because the heading they do declare is not a
constant — and each alone is sufficient, which is why both are kept.

**`## Acceptance — the violation that must become detectable` keeps its exact text.**
`docs/_templates/RL.md`'s own leading comment states why: *"the load-bearing"* heading that
`scripts/ruling-acceptance-item-census.py` matches on *"(any heading depth, case-sensitive)"*.
**That script is the precedent for the any-depth document-side match** adopted here — the
repository already reads real ruling bodies at any depth; check 37 was the outlier.

### 3. What it obliges — and the two broken-input proofs

Both proofs were **executed** on the fully migrated snapshot (§4's predicate), not asserted.
Output pasted verbatim:

```
A. NON-EXEMPT documents carrying a NON-EMPTY required set (the enforced population):
     TOTAL ENFORCED = 0
   (exempt by `was:` = 292, by family {'decision': 6, 'closure': 38, 'ledger': 10,
    'plan': 121, 'research': 2, 'proposal': 20, 'ruling': 95})

   RL required set: ['Ruled', 'What it obliges', 'Acceptance — the violation that must become detectable']

B. PROOF 1 — marked (`was:`) body with no sections:
     reds = 0  -> PASS (correct: exempt)
C. PROOF 2 — unmarked ruling missing `Acceptance — …`:
     check 37: docs/rulings/RL-99002-proof-unmarked-missing.md: missing required section(s)
     ['Acceptance — the violation that must become detectable'] for family 'ruling'
     reds = 1  -> RED (correct: caught)

D. CONTROL — same document with the section added back:
     reds = 0  -> green (the check tracks the input)
```

**What the shape change obliges, found by the suite rather than by reading.** Changing
`RL.md`'s declared sections reds every **hand-written `ruling` fixture** that was built to the
old shape — they carry no `was:`, so RL-1039 does not exempt them, which is the exemption
behaving correctly. Two were affected and both are updated in the same commit:
`tests/fixtures/docs-ids/w37-4-checks/check34-dangling-corrected-by/rulings/RL-01950-frozen.md`
and `RL-01951-corrector.md`. The failure surfaced as
`test_check_34_reds_alone_on_a_dangling_corrected_by_entry` — a test that asserts check 34 reds
**alone** — so a second check firing on its fixture is exactly what it is built to catch.
`tests/fixtures/docs-migration/docs/_templates/RL.md` is left as it is: it is a deliberately
abridged *template* fixture, and `_id_scope_documents` excludes `_templates/` from check 37
(RL-981), so it is not a document instance and nothing reds on it.

**Proof 2's input is a genuine post-flag-day ruling**: a real header with no `was:`, and a body
carrying `## 1. Verified first, at \`15ed00d\``, `## 2. Ruled` and `## 3. What it obliges` —
ordinal-prefixed, so it also proves the ordinal stripping works — with only the `Acceptance`
section removed. **Control D matters**: the same document goes green when the section is added
back, so the red tracks the input rather than something incidental about the fixture
([`RFC-789`](../rfcs/RFC-00789-zero-calls-above-200k-tokens-measures-the-compaction-cap-not-discipline.md)).

### 4. Acceptance — the violation that must become detectable

**The violation: `check 37 reds 0` entering the W37-6 gate record as a bare number.**

**The measurement, with its tree and its predicate.** On a disposable snapshot of `15ed00d`
with these two changes applied, `migrate()` run to completion (1092 files written, 204 deleted,
**0 warnings**), then the real `check_shape()` with `_ID_SCOPE_ROOTS` widened to
`(<snap>/docs, <snap>/.claude)`:

| | Before (this branch's base) | After |
|---|---|---|
| Documents **examined** | 531 | **531** |
| **Exempt** as verbatim-migrated (`was:`) | — | 292 |
| **Shape-checked** | 531 | 239 |
| Of those, carrying a **non-empty required set** — the **enforced population** | 292 | **0** |
| **RED** | **286** | **0** |

**Before, 292 documents were in the enforced population and 286 of them red** — the six that
passed are the whole `decision` family, the only family whose migrated bodies already match
their template. After, the enforced population is empty.

**`check 37` reds `0` of `531` documents examined at `15ed00d`.** The `529` of gate condition 2
is this same measurement at `32fc63c`; the difference is the two `docs/plans/` files added
between the trees, per RL-1039 §1(e).

**The disclosure that must travel with that zero.** The enforced population is **0**. Every
document on the migrated corpus that carries a non-empty required set is exempt by `was:`; the
239 shape-checked documents are 222 `.claude/skills` and `.claude/agents` files that parse to
no family and 17 `reference` documents, and **`reference`, `work` and `slice` are the three
families whose templates declare no required section at all**. So the zero is a zero over an
empty enforced set.

**This is the ruled outcome, not a defect** — it is exactly what D1's option A was priced with
(*"284 documents leave the check's scope on day one"*). But a zero over an empty population is
the boundary metric [`RFC-789`](../rfcs/RFC-00789-zero-calls-above-200k-tokens-measures-the-compaction-cap-not-discipline.md)
warns about: a heavy corpus and an empty one produce the same zero. `CLAUDE.md` §13 puts it
directly — *"a check that has never printed a failure has not been tested"* — and on the
migrated corpus check 37 never prints one.

**So the evidence for condition 2 is the control, not the zero.** Proof 2 (§3) shows the check
fires on the first real document that enters its scope, and proof 1 shows the exemption is what
holds the rest out rather than a detector that has stopped working. **A reader who meets
`0 of 531` without them will draw the opposite conclusion from the one the evidence supports**,
which is why the three figures are bound together here and must stay bound wherever this is
quoted: `0` red of `531` examined, `292` exempt, enforced population `0`, **and the proof**.

*Violation: a document of the `ruling` family, without `was:`, missing `Ruled`,
`What it obliges` or `Acceptance — the violation that must become detectable`, passing
check 37.* Red in §3, proof 2.

*Violation: `required_sections("work")` or `required_sections("slice")` returning a
placeholder-bearing string.* Both return `[]`; the symmetric counterfactual in §1(d) is the
positive control showing what the exclusion is preventing.

---

## What this record does not do

- **It does not authorise the W37-6 run.** Gate condition 2 of the delegation is satisfied by
  §4's measurement; the other five are not this record's, and the re-ask's §10 line is the
  lead's to sign.
- **It does not close F90.** F90's amendment is PR #656's, unmerged. RL-1039 disposes of the
  prior question F90 raised in its own §B; the register row's disposition is a separate act.
- **It does not amend `CLAUDE.md`, RFC-937 §1, or `docs/findings/FD-01027-check-37-reds-on-95-of-95-post-migration-rulings-unconditional-on-the-flag-day-because-its-section-detector-cannot-see-a-level-heading.md`.**
- **It does not backfill any body.** D1's option B — reconciling every family's template with
  the shape its documents are actually written in — is untouched and unowned.

## Provenance

Ruled by the maintainer on 2026-09-03; filed by the decision-maker under
[`RL-01049-w37-6-the-maintainer-s-time-boxed-delegation-2026-09-03.md`](RL-01049-w37-6-the-maintainer-s-time-boxed-delegation-2026-09-03.md) §1,
within the window opening `2026-09-03T00:07:32Z`. Measurements at `15ed00d`, on disposable
snapshots, by executing the modules' own functions — `doc_id.migrate` and
`audit_docs.check_shape` — never an approximation of them.
