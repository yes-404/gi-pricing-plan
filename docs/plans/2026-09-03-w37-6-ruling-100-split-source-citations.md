# W37-6 — Ruling 100: a citation into a split source is rewritten only when the citation determines its target (2026-09-03)

**Filed** 2026-09-03 by the decision-maker. **What this is.** PR #672 (`07f1e41`, *"record and
repoint every path-only relocation's citations"*) made the migration rewrite **path-only**
citations as well as id citations. For a source file that relocates to exactly **one**
destination that is correct and stays. For a source file the migration **splits** into several
destinations it is not: `token_map` is a flat `dict[str, str]` keyed on the old path, every
draft of a split source writes the same key, and **the last draft silently wins**. A citation
that named the source now names one arbitrary destination — it resolves, and it lies.

**This ruling extends Ruling 89 from the line-offset case to the path-only case.** Ruling 89
already forbids the shape: *"A rewrite that changes only the path is forbidden"*
(`docs/plans/2026-09-02-w37-container-family-and-line-citations-rulings.md:199-202`, under the
heading at `:153`). Ruling 89 reached citations *carrying a line offset*; #672 created the same
failure for citations carrying **no** offset, which Ruling 89's text does not reach. Nothing
about the defect is new — only the class of citation it now applies to.

**Filed under** delegation §1, *"NT-0019 §1/§4 amendments needed to reach a completing, green
run"* (`docs/plans/2026-09-03-w37-6-time-boxed-delegation.md:19-21`). This is a **scope marker
/ rewrite disposition**: which citations `migrate` is permitted to rewrite, and what it must do
with the rest.

**Window.** The second renewal expires `2026-09-03T20:30:39Z` (§7.2 of the delegation record,
appended by PR #674, `6195ca0`). This record is filed at `2026-09-03T13:00:11Z` (`date -u`),
inside it.

**`implementation: owed`** — per Amendment 3 (`…-time-boxed-delegation.md:281-295`, *"A ruling
PR names its implementing PR, or carries `implementation: owed`"*). The implementing change is
being built in parallel and is **not** named here because it does not yet exist. **What
discharges it**: a merged PR against `scripts/doc-id.py` that (a) removes split sources from
the flat path `token_map` and routes them through a per-citation resolver, (b) raises on a
duplicate path key with the source path and the competing targets in the message, and (c) ships
the §3 evidence and the §4 broken-input proof. Until that PR is merged and named, this ruling
has changed no behaviour.

## Authority

- The decision is the maintainer's under `CLAUDE.md` §12, delegated for this window by
  delegation §1. The substance below is the maintainer's, relayed through the lead and
  re-verified here against the tree before filing.
- The halt condition (delegation record, line 33 — *"Two options with no cell to read from is a
  halt, not a coin-flip"*) — **not triggered**. Every element reads from a named cell; the two
  rejected readings are priced in §4 against cells that exist and point the other way.

## Ruling 100 — a citation into a split source is rewritten only when the citation itself determines the target; `token_map` refuses a duplicate key

<!-- Structural note: this heading exists so `_discover_multi_ruling_files`
     (`_RULING_HEADING_RE`, `^##\s+Ruling\s+(\d+)`) discovers this record as one `RL-` draft
     rather than falling through to `_discover_plain_plans`'s `PL- kind: leaf, owner: planner`
     catch-all — the defect F96 (`docs/audit/findings/F96.md`) was filed for. -->

**Ruling number derivation.** `git grep -hoE "Ruling [0-9]+" -- docs/ .claude/ scripts/ | grep
-oE '[0-9]+' | sort -n | uniq | tail -1` → `99` at `6195ca0`; `git grep -n "Ruling 100"` over
the whole tree → no match, exit 1. **100 is the next free number**, derived rather than assumed.
(`git grep -h` drops filenames and is used here only to compute a maximum, never to cite.)

## 1. The mechanism, verified in the shipped source

Read directly at `6195ca0`, not relayed:

- `scripts/doc-id.py:5150` — `token_map: dict[str, str] = {}`. A flat dict. Nothing about it
  is keyed per-citation or per-target.
- `:5197` — `token_map.update(_path_rewrite_tokens(old_path, new_path))`, inside the loop over
  drafts, guarded only by `if old_path and new_path and old_path != new_path:` (`:5196`).
  **Every draft of a split source reaches this line with the same `old_path`.** `dict.update`
  overwrites. The last draft in iteration order wins, silently.
- `_path_rewrite_tokens` (`:4709-4745`) returns a plain `dict` built by three unconditional
  assignments (`:4738`, `:4741`, `:4744`) and `return tokens` (`:4745`). **There is no
  collision guard anywhere in it**, and none at the call site.
- `_rewrite_citations` (`:4748-4768`) then applies `token_map[tok]` as a literal substring
  substitution. It has no way to know a key was contested.

**Why this is worse than the failure it replaced.** Before #672 a path-only citation into a
moved file was left alone and **dangled** — and a dangling link is exactly what gate condition
7 catches (*"The auditor's general dangling-link scanner returns zero on the post-migration
snapshot"*, `docs/plans/2026-09-03-w37-6-time-boxed-delegation.md:249-264`, Amendment 1). After
#672 it **resolves**, to a real file, in the wrong record. No gate in the seven catches that,
because every one of them tests resolvability.

### 1.1 The worked example the lead named, verified and corrected

`scripts/register-lint.py:3` cites
`docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md` and names **Ruling 50** in the same sentence.
That source carries **five** `## Ruling N` headings — 49, 50, 51, 52, 53, at lines 30, 96, 181,
240, 295 (`grep -n "^## Ruling [0-9]"`). Five drafts, one `old_path` key, last write wins:
**the id resolves to Ruling 50's record and the path beside it resolves to Ruling 53's.** A
link that works and lies, in a file whose own docstring is quoting the ruling it is now
mis-pointing at.

**Reproduced end-to-end** (§1.3's run, at `07f1e41`). Post-migration `scripts/register-lint.py`
lines 2–4 read, verbatim: *"Ordered by **RL-990** (`docs/rulings/**RL-00993**-q5-file-by-the-f-id-…md`)"*.
The id is Ruling 50's document; the path is **Ruling 53's** — the last of the five drafts.

*Two corrections to the brief as relayed.* The pair was relayed as `RL-196` / `RL-00199`.

- **The padding difference is not the defect and is by design.** `scripts/_docid.py:104-108`
  (`canonical`, *"The citation form — NT-0019 §1.1 rule 2: unpadded, always"*) against `:111-116`
  (`padded`, *"The filename form — NT-0019 §1.1 rule 3"*). An unpadded id beside a zero-padded
  filename is correct. **The number gap is the defect** — 990 against 993 here, 196 against 199
  as relayed.
- **The absolute numbers were wrong at this tree.** The observed pair is `RL-990` / `RL-00993`.
  The relayed pair is structurally identical (first draft against last, Δ3) but was measured
  against a different numbering base. **Cite the observed pair, not the relayed one.**

### 1.2 It lands on the ruling that forbids it — with the direction corrected

`docs/plans/2026-09-02-w37-container-family-and-line-citations-rulings.md` is itself a split
source: two `## Ruling N` headings, **88 at `:61` and 89 at `:153`**. Ruling 89's heading is the
**later** of the two, so its draft is the last write and it wins the key.

**Every citation of that path was enumerated rather than sampled** — `git grep -n
"2026-09-02-w37-container-family-and-line-citations-rulings.md"` at `6195ca0`: **7 hits in 6
files**, and each was read for which ruling its prose names and which token form it carries:

| Citation | Names | Path form | Rewritten? |
|---|---|---|---|
| `docs/audit/findings/F80.md:9` | Ruling 88 | full `docs/plans/…` | **yes → Ruling 89's record** |
| `scripts/doc-id.py:1679` | Ruling 88 | full `docs/plans/…` | **yes → Ruling 89's record** |
| `docs/audit/ruling-acceptance-item-sweep.md:374` | Ruling 88 | bare filename | no |
| `docs/audit/ruling-acceptance-item-sweep.md:375` | Ruling 89 | bare filename | no |
| `docs/plans/2026-09-02-w37-6-migration-run-leaf-plan-v2.md:122` | Ruling 88 | bare filename | no |
| `docs/plans/2026-09-02-w37-gap-1-ruling-86-owner-ruling.md:20` | Ruling 88 | bare filename | no |
| `docs/plans/2026-09-02-w37-ruling-88-acceptance-amendment.md:6` | Ruling 88 | bare filename | no |

**The relayed phrasing — "the citation of Ruling 89's own file is repointed to a wrongly-named
target" — is correct in outcome and inverted in direction, and the corrected form is worse.**
The two rewritten citations both say **Ruling 88** and both land **on Ruling 89's record**: the
ruling that forbids a path-only rewrite is the destination the path-only rewrite invents. One
of the two is `scripts/doc-id.py:1679` — the migration's own source comment, repointed by the
migration it documents.

**Confirmed on the §1.3 run, not inferred.** The file's two `## Ruling N` headings become
`RL-1058` (Ruling 88) and `RL-1059` (Ruling 89); `RL-1059` is the last draft and wins the key.
Both surviving full-path citations read, post-migration:
*"**RL-1058** (`docs/rulings/**RL-01059**-a-line-number-citation-into-a-split-file-…md`, PR #601)"*
— at `scripts/doc-id.py:1679` and at `docs/findings/FD-01095-…:21` (F80's post-migration home).
**A correct id beside a wrong path, in the migration's own source, naming the ruling that
forbids the rewrite that broke it.**

**Two corrections to the framing, both of which narrow it and neither of which is cosmetic:**

- **It is 2 of the 7, not 7 of 7.** Five of the seven cite by **bare filename**, with no
  directory. `_path_rewrite_tokens` emits exactly three forms (`:4738`, `:4741`, `:4744`) — the
  full `docs/`-prefixed path, the `docs/`-stripped form, and the `docs/audit/`→`docs/findings/`
  form — and `_rewrite_citations` matches each as a whole token (`rf"\b{re.escape(tok)}\b"`,
  `:4751`). **None of the three is a bare filename**, so a sibling-relative link inside
  `docs/plans/` is invisible to the rewrite in either direction.
- **That is a second, separate defect and it is disclosed, not ruled on here.** Those five will
  **dangle** after the run, which is condition 7's job, not this ruling's. It is named so a
  later reader does not read this ruling's silence as coverage — and so the §3.1 census is not
  mistaken for a census of *all* citations into split sources, only of the rewritten ones.

### 1.3 The census, reproduced independently, with its predicate

The auditor's relayed figures were **1124 rows, 262 distinct moved `old_path`s, 27 splitting
into 2–21 targets, 171 occurrences in 68 surviving files**. Amendment 2 (`:265-280`) says a
relayed figure is a claim, not evidence, so this ruling **re-ran it rather than citing it**.

**Tree: `07f1e412ad0080b7b40b44c0f495e4716cec68cf`.** `migrate` has no dry-run and no output dir
(`migrate_parser`, `scripts/doc-id.py:5642-5647`, takes only `--repo-root` and mutates in
place), so the run was done against a throwaway clone, with a pristine `git archive` copy of the
same tree kept beside it as the pre-migration reference:

```
python3 scripts/doc-id.py migrate --repo-root /tmp/docid-audit
```

**Split sources** — `REDIRECTS.csv` is 1124 data rows; 422 moving rows; 262 distinct moving
`old_path`s:

```
awk -F, 'NR>1 && $3!="" && $4!="" && $3!=$4 {print $3"\t"$4}' docs/REDIRECTS.csv \
  | sort -u | cut -f1 | uniq -c | awk '$1>1' | wc -l      → 27
  ... | awk '$1>1{print $1}' | sort -n | sed -n '1p;$p'   → 2 … 21
```

**27 split sources, fan-out 2–21 — confirmed exactly.** The two largest are
`docs/audit/closure-records.md` (21) and `docs/audit/plan-reviews.md` (12); the other 25 are
`docs/plans/…-rulings.md` multi-`## Ruling N` files.

**Occurrences** — predicate stated in full, because a count without one is the F85 defect
(`CLAUDE.md` §13's predicate clause): for each of the 27 split `old_path` strings, a plain
literal `text.count(path)` over every file in `git ls-files` **read from the pre-migration
tree**, excluding the 27 source files themselves, then restricted to files that still exist
post-migration.

| Corpus | Occurrences | Files |
|---|---|---|
| All pre-migration tracked files (excl. the 27 sources) | 322 | 113 |
| **Restricted to surviving files** | **171** | **68** |

**171 in 68 — confirmed exactly**, which also recovers the auditor's predicate (pre-migration
text, post-migration survival filter). **This is a floor, not a ceiling**: only the full
repo-relative `docs/…` form was counted, and `_path_rewrite_tokens` registers two further forms
(`:4741`, `:4744`).

**The four buckets, first-match in order (i) → (ii) → (iii) → (iv), summing to 171:**

| Bucket | Predicate | Count |
|---|---|---|
| **(i)** adjacent id | a token matching `\b(Ruling \d+\|RL-\d+\|FD-\d+\|F\d+\|ADR-\d+\|NT-\d{4}\|PL-\d+\|RFC-\d+\|CR-\d+\|LG-\d+\|RS-\d+)\b` on the same line **and** listed as one of that `old_path`'s `old_id`s in `REDIRECTS.csv` | **55** |
| **(ii)** `#anchor` | `<path>#([A-Za-z0-9\-_%.]+)` on the line, slug matching a heading in exactly one target | **0** |
| **(iii)** line number | `<path>[:#]L?(\d+)` on the line, resolving through the source-tree section boundaries to exactly one target | **2** |
| **(iv)** undetermined | none of the above | **114**, in **40** files |

**Sum 55 + 0 + 2 + 114 = 171.** The boundary map for (iii) located every target for 26 of the
27 sources and 3 of 4 for `2026-08-30-nt-0012-0013-0014-adoption.md`; **no (iv) occurrence
carries a line number that failed to resolve** — the 114 have nothing to disambiguate with.

**(ii) is zero and that is a finding, not a formality.** No citation in this corpus uses an
anchor. Determinant (ii) is ruled in §2.1 because it is provable when present, not because it
is load-bearing today.

**The two (iii) cases**, named because there are only two:
`.claude/skills/close-workstream/SKILL.md:646` (`docs/audit/plan-reviews.md:987-1005` →
`docs/closures/CR-00908-…`) and
`docs/research/w11-task-1-4-model-call-concurrency.md:7`
(`docs/plans/2026-08-29-w11-prework-rulings.md:490-492` → an `RL-` record). The first is
**one of Ruling 89's own seventeen** — the overlap between the two rulings, made concrete.

**Bucket (iv)'s concentration** — `tests/test_doc_id_migrate.py` 25, `docs/roadmap.md` 19,
`scripts/doc-id.py` 14, then a long tail. **The migration's own test file and its own source are
the two largest citers of the sources it splits.**

### 1.4 A second consequence of the same key, disclosed and not ruled on

The `was:` field — the stamped provenance holding a document's pre-migration path — **is itself
a `token_map` key**, so Phase D rewrites it. Measured on the same run: **349 of 349 migrated
documents carrying a non-null `was:` end up naming a path that never existed pre-migration.**
For a single-target relocation `was:` names the document's own new path (useless, harmless).
**For a split source it names an arbitrary sibling's new path** — all five of Ruling 49–53's
records carry `was: docs/rulings/RL-00993-…`, the last draft's.

**`was:` therefore cannot recover a split document's origin; only `REDIRECTS.csv`'s `old_path`
column still carries it.** This is the same defect as §1 with a wider blast radius, and it is
**disclosed, not ruled on**: whether `was:` should be excluded from the rewrite entirely is a
question about the stamp set, and it belongs to whoever owns that — it is named here so the
implementing PR does not treat §2.2's guard as sufficient without checking it.

## 2. Ruled

### 2.1 A citation into a split source is rewritten only when its target is determined by the citation itself

**Three determinants, each mechanical and each provable. Nothing else is rewritten.**

- **(i) A document id adjacent to the path names the target.** The citing text carries the
  target's own identifier beside the path — `Ruling 50`, an `RL-`/`FD-`/`F<n>` id — and the
  migration knows which destination that id became.
- **(ii) A `#anchor` resolves to exactly one target's heading.** Exactly one; an anchor
  matching a heading in two destinations is not a determinant.
- **(iii) A line number maps to exactly one target through the split boundaries at the source
  tree.** This is **Ruling 89's re-derivation** (`:199-202`), performed **by the migration**
  rather than by hand — Ruling 89 permits (a) re-derivation or (b) replacement and leaves the
  choice per-citation; where the boundaries make the mapping unambiguous, the migration does
  (a) mechanically.

**Anything else is not rewritten. It dangles.** Gate condition 7 lists it, and **it is
dispositioned by name before the run** — re-derived or replaced, in Ruling 89's own shape
(`:199-202`, *"(a) re-derived … or (b) replaced by a form that needs no offset — the
destination record's id, with a quoted phrase or heading where precision is wanted"*).

**Why a deliberate dangle is the right residue.** Ruling 89 already settled the comparison, in
terms that are about detectability rather than about offsets: *"**Detection is not repair**, and
a citation that is wrong while resolving is worse than one that fails loudly"*
(`…-container-family-and-line-citations-rulings.md:209-210`). A dangle is caught by condition
7. A wrong resolution is caught by nothing.

### 2.2 `token_map` refuses a duplicate key; a split source never enters it

- **A split source never enters the path token map.** It enters a **per-citation resolver**
  that returns one target or none — one target when (i), (ii) or (iii) determines it; **none**
  otherwise, and none means the citation is left alone to dangle.
- **The collision guard raises**, naming **the source path and the competing targets**. It is a
  hard error, not a warning: `_rewrite_citations` cannot recover from a contested key, and
  `dict.update`'s silence at `:5197` is precisely the property that let this ship.
- **The guard's value is not limited to this defect.** It makes the whole class loud from now
  on: any future rule that splits a source, or any future token form that collides, fails at
  build time instead of producing 171 links that work and lie.

### 2.3 Single-target relocations are untouched

**Everything #672 built for a source that moves to exactly one destination stays as it is.**
This ruling reaches only the split sources. #672 is not reverted, not narrowed for the
single-target case, and not re-litigated.

### 2.4 Bucket (iv) decides the window

**Evidence before the fix merges** (§3.1), then the broken-input proof (§3.2), then **bucket
(iv)'s size decides what happens next**:

- **Small** → the bucket-(iv) citations are dispositioned by name in the same PR, and the gate
  re-runs.
- **Large** → **that is the second-fail handover with the list.** The maintainer's own grounds,
  verbatim: *"that is the second-fail handover with the list, and I would rather have that list
  than 171 links that work and lie."*

**No threshold is written here on purpose.** "Small" and "large" are the lead's read against
the clock left in the window (`20:30:39Z`, §7.2) and the go/no-go at `17:30:39Z` — a number
fixed now would be a number fixed without knowing what the buckets contain. What is fixed is
that **the decision is made from the measured bucket, after the measurement, not before it**.

**The measurement now exists** (§1.3): **bucket (iv) is 114 occurrences across 40 files** at
`07f1e41` — two thirds of the 171, and its two largest citers are the migration's own test file
and its own source. **This ruling records the number and does not make the call**: which side of
"small" that falls on is the lead's, and the record exists so the call is made against a
measured bucket rather than an impression of one.

## 3. What it obliges, before the fix merges

### 3.1 The census, bucketed, at one tree, with its predicate

**§1.3 discharges this obligation at `07f1e41`** — 55 / 0 / 2 / 114, summing to 171, with the
predicate for each bucket written out and the `migrate` command that produced the tree. It was
**run here, not relayed**: Amendment 2 (`…-time-boxed-delegation.md:265-280`) treats a relayed
figure as a claim, and the auditor's identical numbers are corroboration only because the two
runs were independent.

**It is discharged at one tree, and only that tree.** The implementing PR re-runs it at its own
tree, with the same predicate, because every input moves: the draft set, the split boundaries,
the surviving-file filter. **A count carried forward from `07f1e41` is a stale count**
(`CLAUDE.md` §13's reference rule, and the predicate clause the maintainer added 2026-09-02
discharging F85). A bucket count filed without its predicate, or whose four buckets do not sum
to the total, is the F85 defect exactly.

### 3.2 The broken-input proof

**A citation with two candidate targets and no determining evidence must not be rewritten** —
**red before the fix, green after.** The input is deliberately broken: a fixture source that
splits into at least two destinations, cited by a path with no adjacent id, no anchor and no
line number.

`CLAUDE.md` §13: *"enforcement is proven on deliberately broken input. A check that has never
printed a failure has not been tested."* Two failures must both be exercised: the **rewrite**
must not happen, and the **collision guard** must raise with both competing targets named.

### 3.3 What must not be built

- **No canonical-target choice.** Not "first heading wins", not "the largest destination", not
  a per-source hand-picked default.
- **No hardcoded list of 27 source paths.** The rule is a predicate over the draft set; a list
  goes stale the first time a split boundary moves.

## 4. The options not taken, priced

| Reading | What it produces | Cell it reads from | Cost of taking it instead |
|---|---|---|---|
| **A — the shipped behaviour, last draft wins** | Every path-only citation into all 27 split sources repointed to whichever draft iterated last. | `scripts/doc-id.py:5150`, `:5197` — a real, currently-shipped cell, not a straw option | The 171. Six citations naming Ruling 88 land on Ruling 89's record (§1.2); `register-lint.py:3` names Ruling 50 and points at Ruling 53 (§1.1). Every one resolves, so **no gate in the seven sees any of it** — the failure walks through condition 7 by construction, because condition 7 tests resolvability. |
| **B — a canonical target per split source** (pick one destination, rewrite every path-only citation to it) | Every citation resolves; a defensible-looking default; zero dangles; the gate stays green. | **No cell.** Ruling 89 (`:199-202`) forbids a rewrite that changes only the path, and names re-derivation and replacement as the two permitted repairs — a canonical target is neither. | **The maintainer's own grounds: *"it invents what Ruling 89 refused."*** It is strictly worse than A in one respect that matters: it makes the wrong answer look *chosen*. A reader who finds a citation pointing at a canonical target has no way to tell a determined target from a defaulted one, so the corpus loses the ability to distinguish a correct rewrite from a guess — permanently, since the original path is gone after the run. It also produces exactly the state Ruling 89 calls worse than failing loudly (`:208-209`). |
| **C — pure dangle: rewrite nothing into any split source** | All 171 dangle; condition 7 lists all 171; nothing is silently wrong. | Ruling 89 (`:199-202`) supports the *residue*, but no cell supports discarding a **determined** target: (b)'s *"the destination record's id"* is precisely a determinant the corpus already holds. | **The maintainer's own grounds: *"deriving nothing when the citation names its target is discarding evidence the corpus already holds."*** C is safe and lossy in the same act. It converts every (i)/(ii)/(iii) citation — where the target is *provable*, not guessed — into manual work, and puts them on the same list as the genuinely ambiguous ones, which is how the ambiguous ones get skimmed. Its cost is measured by bucket (i)+(ii)+(iii): every one of those is a rewrite C refuses to make on evidence it has. |

**This ruling is B's determinacy without B's invention, and C's honesty without C's waste**: it
rewrites exactly what is provable and dangles exactly what is not, which is why §3.1's bucketing
is an obligation rather than a nicety — the buckets *are* the boundary between the two.

**Neither rejected reading reaches the halt condition.** Both have a cell (B: Ruling 89
`:199-202`, which refuses it; C: the same passage's clause (b), which shows the evidence it
would discard), and in both cases the cell points away from the reading.

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
