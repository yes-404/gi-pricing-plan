---
id: RL-1042
family: ruling
title: a whole-file citation into a split source resolves to the split's index entry, not to any target
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-03
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-03-w37-6-ruling-100-split-source-citations.md
---

## RL-1042 — a whole-file citation into a split source resolves to the split's index entry, not to any target

<!-- Structural note: this heading exists for the reason the RL-1041 heading above gives —
     `_discover_multi_ruling_files` (`_RULING_HEADING_RE`, `^##\s+Ruling\s+(\d+)`) must discover
     this record's second ruling as its own `RL-` draft rather than letting it fall through to
     `_discover_plain_plans`'s `PL- kind: leaf, owner: planner` catch-all — the defect F96
     (`docs/findings/FD-01055-a-filed-ruling-that-omits-the-ruling-n-heading-migrates-as-pl-owner-planner-and-nothing-catches-it.md`) was filed for. It is placed AFTER §4 deliberately: the
     splitter cuts spans at each `## Ruling N` heading, so a heading placed before §1 would
     carry §1-§4 -- RL-1041's own evidence and reasoning -- into RL-1042's document. -->

**Filed** 2026-09-03 by the maintainer, recorded by the lead. **Ruling number derivation**, at
`198ea5d`, the tree at which this was written:

```
git grep -hoE 'Ruling [0-9]+' -- docs/ .claude/ scripts/ | grep -oE '[0-9]+' \
  | sort -n | uniq | tail -1        → 100
git grep -n 'RL-1042' -- docs/ .claude/ scripts/    → no match, exit 1
```

**101 is the next free number**, derived rather than assumed. (`git grep -h` drops filenames and
is used here only to compute a maximum, never to cite.)

**It supersedes §2.4 and amends §2.1 and §2.2 as §2.5 records.** RL-1041's three
determinants, its per-citation resolver, its collision guard and its single-target carve-out all
stand.

### 101.1 The rule

**A whole-file citation into a split source — one that determines no target under RL-1041's
(i), (ii) or (iii) — resolves to `docs/<family>/INDEX.md#<old-basename>`.** That section lists
**every** target of the split, each with its `was:` provenance.

**The maintainer's own grounds, verbatim:**

> *"Not choosing a target — it is the REDIRECTS row made navigable."*

**So bucket (iv) is 0 by construction**, and §2.4's "small or large decides the window" has
nothing left to weigh.

**Why this is not the canonical-target choice §3.3 forbids, and the distinction is the whole
ruling.** §3.3 refuses *"first heading wins", "the largest destination"*, and a hand-picked
per-source default; §4's option **B** is priced and rejected on the maintainer's grounds that
*"it invents what RL-980 refused."* Every one of those names **one** target and thereby
asserts that the citation meant that one. **The index entry names none of them.** It resolves to
a page that says, in full, *"the file you cited became these N documents"* — which is exactly
what `REDIRECTS.csv` already records and exactly what a reader following a citation needs. The
test §4 applies to B is whether a later reader can tell a determined target from a defaulted
one; the index entry passes it, because it never claims a target at all.

**And why it is not option C's waste.** §4 rejects the pure dangle because *"deriving nothing
when the citation names its target is discarding evidence the corpus already holds."* RL-1042
discards nothing: (i), (ii) and (iii) still rewrite to the determined target, and only the
genuinely undetermined citation goes to the index. **It is B's navigability without B's
invention, on top of what §4 already said this record was** — and it removes the residue Ruling
89 was willing to tolerate rather than merely detecting it.

### 101.2 `was:` is provenance, not a citation

> *"`was:` is provenance, not a citation. It is written from `REDIRECTS.csv` and is excluded
> from `_rewrite_citations` — the rewriter touches bodies, never headers."*

**`_rewrite_citations` must not touch a `was:` header field.** The rewriter's jurisdiction is
document **bodies**; a header `was:` is the record of where a document came from, and rewriting
it destroys the one field that makes the index section above possible. A `was:` repointed to a
post-migration path is a provenance record that no longer records any provenance.

**This is a live defect, not a hypothetical.** `was:` is currently corrupted across the migrated
corpus — **the figure relayed to this record is 349 documents, and under Amendment 2 that is a
claim, not evidence: the executor re-measures it and the auditor re-runs it.**

**Obligation — the broken-input proof, and its shape is specified because a looser one proves
nothing.** A document whose header `was:` names a split source is put through the rewrite, and
the header is **byte-identical** afterwards. Not "still parses", not "still resolves", not
`git status` clean: byte-identical. A proof that exercises only a `was:` naming a
**single-target** source would pass against the unfixed code and is therefore not the proof.

### 101.3 The new check — an empty index section is the new silent failure

**Alongside gate condition 7:** every `INDEX.md#<anchor>` that a citation resolves to **exists**,
and its section **lists ≥ 2 documents**.

> *"A link to an empty index section is the new silent failure; make it loud first."*

**The `≥ 2` is not a stylistic floor; it is what makes the check able to fail.** An anchor that
exists but lists nothing, or lists one document, means one of two things: the split it claims to
describe did not happen, or the index was generated from something other than the redirect rows.
Both resolve. Both are wrong. **Condition 7 cannot see either**, for the same reason it could
not see the 171 of §1.3: condition 7 tests resolvability, and both failures resolve. **That is
the second time in this window a defect has walked through condition 7 by construction**, and it
is why this check is stated as a condition rather than left to review.

**"Make it loud first" is an ordering, and it is binding.** The check is proven **red** — on an
emptied section and on a missing anchor, with the failure naming the citing file and the anchor
— **before** it is proven green. `CLAUDE.md` §13: *"a check that has never printed a failure has
not been tested."*

### 101.4 What this obliges before the fix merges

- **Bucket (iv) measured at 0**, at one named tree, with the predicate verbatim — and the
  reclassification's **before and after counts with their sum unchanged**, so a citation cannot
  be quietly dropped from the population on its way between buckets. §2.4's measurement of
  bucket (iv) — **114 occurrences across 40 files at `07f1e41`** — is the baseline that must go
  to 0, and it is cited here with its tree because a bare "0" proves nothing without the number
  it came from.
- **The `was:` broken-input proof of §101.2**, byte-identical, on a split source.
- **The index check of §101.3**, red before green, on both failure shapes.
- **The gate still holds**: `migrate()` completes returning a `MigrateResult` rather than
  raising, **RFC-937 §7(a)'s `none` row = 0**, and condition 7's scanner — **unmodified** — at
  zero.

**Anything not measured at the frozen tree is not evidence for this ruling**, and under
Amendment 2 (delegation §7.4) a figure reported by the agent that produced the work is a claim
until the auditor re-runs it.

### 101.5 Left open, deliberately

**The anchor's exact slug form is not fixed here.** `<old-basename>` is the citing path's
basename, but whether the `.md` extension is carried, and how a basename containing characters
GitHub's anchor slugging alters is normalised, is **not decided by this ruling** — it is a
property of the index generator, and it must be **written down where that generator lives, with
its own test**, rather than inferred from one worked example. Two citations that differ only in
their basename's punctuation must not resolve to two different anchors by accident.

**This is recorded as open rather than picked** (`CLAUDE.md` §10), and it is the executor's to
raise as an open question if the implementation forces a choice. **What is fixed is the form
`docs/<family>/INDEX.md#<old-basename>` and that the section lists every target with its
`was:`.**
## Acceptance Standard

The violation this record must make detectable: **a path-only citation into a source the
migration splits, rewritten to a target the citation itself does not determine — a link that
resolves and is wrong — or a duplicate path key entering `token_map` without raising.**

### Acceptance — the violation that must become detectable

1. *Violation: a citation naming a split source, carrying no adjacent id, no `#anchor` and no
   line number, rewritten to any target.* It must be left alone and appear in condition 7's
   list. **Red before the fix, green after** (§3.2).
2. *Violation: two drafts sharing one `old_path` both reaching `token_map` without an
   exception.* The collision guard must raise, and its message must name the source path **and
   every competing target** — a guard that raises without naming them is not this ruling's
   guard.
3. *Violation: a bucket census filed without its predicate, or whose four buckets do not sum to
   the total, or measured across more than one tree.* `CLAUDE.md` §13's predicate clause; a
   sum that does not close means a citation was silently dropped from a bucket.
4. *Violation: a bucket figure taken from a relay rather than run by the agent recording it —
   **or §1.3's `07f1e41` figures carried into the implementing PR instead of re-run there**.*
   Amendment 2 (`…-time-boxed-delegation.md:265-280`) for the first; §3.1 for the second — the
   draft set, the split boundaries and the surviving-file filter all move with the tree.
   **`was:` (§1.4) is re-checked in the same run**: a guard that stops the citation rewrite
   while `was:` still names a sibling has fixed half the key's damage.
5. *Violation: a canonical target, a first-heading-wins default, or a hardcoded list of the 27
   split source paths, in any form.* §3.3.
6. *Violation: any change to the rewrite of a source that relocates to exactly one destination.*
   §2.3 — #672's single-target behaviour is untouched.
7. *Violation: bucket (iv)'s window decision taken before the bucket is measured.* §2.4 fixes
   the order, not the threshold.
8. *Violation: this ruling merged with an implementing PR named that does not ship §3.1's
   evidence and §3.2's proof, or merged and then left with `implementation: owed` unresolved
   past the run.* Amendment 3 (`…-time-boxed-delegation.md:281-295`).
9. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
