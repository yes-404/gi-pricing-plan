# W37's migration preconditions — DP-1, DP-2, DP-3 and the vendored-skill criterion, ruled (2026-09-02)

**What this is.** Four questions that must be settled before Slice W37-6 — NT-0019's single
supervised migration run — may start. Three are the `Decision points` rows of
[`2026-09-01-nt-0019-id-standard-map-plan.md`](2026-09-01-nt-0019-id-standard-map-plan.md)
marked blocking on W37-6; the fourth is a self-contradiction inside
[`NT-0019`](../notes/0019-one-id-per-document.md) §1.5, raised by the W37-2 executor and
relayed by the lead. Each is ruled below as Rulings 66 through 69.

**The frozen plan is not edited.** `CLAUDE.md` §2 freezes a filed plan at its date, and this
role's charter forbids editing one. This record is the sibling that supplies the resolver ids
its `Decision points` table asks for; the table's own cells stay as filed.

## Authority — and it was not the maintainer personally

- **DP-3** was assigned to this role by the plan itself (*"decision-maker, one ruling"*).
- **DP-1 and DP-2** are labelled `maintainer` in that table. The lead routed both here under
  the maintainer's delegation of 2026-09-01, recorded at
  [`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md)
  §1: *"I authoris the lead to allocate technical questions to decision-maker to make decision
  on behalf of me."* **A reader must be able to see the maintainer did not rule these
  personally, and this paragraph is that record.** The lead's routing judgement was accepted,
  and for DP-1 the note's own text turns out to make the routing unnecessary — see Ruling 66's
  §1.
- **The vendored-skill question** (Ruling 69) is a spec-versus-implementation conflict, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) and
  [`delivery-process.md`](../process/delivery-process.md) §3 already place with this role
  (*"Rules decision points and spec-vs-code conflicts before a plan or slice can proceed"*).
  No delegation is needed for it.
- **Nothing here reopens D0–D14.** NT-0019 §2's fifteen decisions are fixed inputs. D14
  (*"Enforcement red from the migration PR"*) is load-bearing for Rulings 66 and 69 and is
  applied, never questioned.
- **Nothing here was declined.** The boundary that would have made me decline is stated at the
  end, under *What would have gone back to the maintainer*.

**Numbering continues at 66.** Verified rather than relayed:
`git grep -hoE '^#+ Ruling [0-9]+' -- docs/plans` at `04ec6bf` yields a maximum of **65**, and
`git grep -nE 'Ruling 6[6-9]' -- docs .claude` returns nothing.

**Evidence tree.** Every measurement below was taken at `04ec6bf` — `origin/main`, fetched at
the start of this session — over the corpus `git ls-files`, **1360 tracked files**. Where a
figure is quoted from another document, the tree that document states is named with it.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while its own
docstring disclaims exactly that scope. That disagreement is register finding (F68) — see
[`../audit/register.md`](../audit/register.md) — carried forward with NT-0019's migration as
its trigger. It is honoured here rather than evaded, and the check is not patched from this
branch.

1. `git grep -c '^## Ruling 6[6-9] —' docs/plans/2026-09-02-w37-migration-preconditions-rulings.md`
   returns `4`, and `git grep -n '^#\+ Ruling ' docs/plans/` shows 66–69 filling the gap
   immediately after Ruling 65 with no duplicate and no skip.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option** in its
   opening paragraph, with the measured evidence that separated them.
3. Each ruling carries a `### 4.` section stating its acceptance as **a violation that must
   become detectable**, never as a description of correct behaviour.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-dp-rulings-66-68` names exactly this one new file.
   No frozen plan, no note, no roadmap row and no script is edited by this branch.
6. Every numeric claim below names the tree it was measured at and the command that produced
   it, per `CLAUDE.md` §13's reference rule.

---

## Ruling 66 — DP-1: the creating instruments land in W37-6's commit, and the set is a criterion rather than a list of seven

### 1. Verified first, at `04ec6bf`

| Claim | Verdict |
|---|---|
| The plan's "seven creating skills" is a real class in NT-0019 §5.4 | **Confirmed.** §5.4 marks six rows **primary** — `writing-plans`, `subagent-driven-development`, `close-workstream`, `phase-review`, `adr-write`, `spec-change` — and gives `library-spike` an H row reading *"writes `RS- kind: spike` via `doc-id.py next`"*. Seven instruments that mint a governed document. §8's S3 phrase *"the eleven primary skills"* is that seven plus `docs-audit`, `dev-commands`, `git-hygiene` and `reporter-cycle`; "seven creating" is a correct subset of it, not a different set |
| The window is real | **Confirmed, and the plan's enumeration of it is under-inclusive.** A document created between W37-6 and W37-7 under the retired grammar fails check 30 (a header on every file under `docs/`) and check 31 (id, filename and directory agreement). The plan says *"checks 30-32"*; check 32 governs citation resolution and fires only if the new document also cites a retired id, while **check 36** — *"no pre-migration form survives outside the CSV and `was:` lines"* — fires on the filename alone. Check 33 (`work:`/`slice:` must resolve) and check 39 (a merged PR's title names its `SL-`) are further exposure the plan does not name |
| D14 is what makes the window bite | **Confirmed.** §2, D14: *"Enforcement red from the migration PR"*, reason *"No population to phase in"*. There is no warn phase and no date switch to hide behind; W37-4's own text rules both out |
| The window is empty, so (c) is a survivable bet | **Refuted, from the plan's own text.** W37-6's acceptance requires §7 (a)–(h) *"each recorded with its command and output in the slice's ledger"*, and W37-7's requires *"every §5.4 row not landed in W37-6 is named by a commit in this slice's ledger"*. A ledger is an `LG-` document (§1.2, §1.4) and the instrument that mints one is `subagent-driven-development` — one of the seven. Executing W37-7 at all therefore creates at least two governed documents inside the window (its leaf plan, `PL-`, and its ledger, `LG-`) using instruments that have not been migrated. **The window is occupied by construction** |
| Stage-to-slice allocation is the maintainer's | **Refuted, by NT-0019's own header block.** Status row: *"The planner cuts §8 into slices."* Owner row: *"The maintainer accepts. **The planner slices §8.** The executor runs the migration script and the hand edits."* No decision in §2's D0–D14 concerns sequencing. §8's stage boundaries are not a maintainer decision |
| The plan already exercised that authority | **Confirmed, twice.** *"Departure 1 from §8"* cuts S1 into four slices on the planner's own authority without escalating. And W37-6's *"What lands in this one commit"* list, introduced as *"§8's S2 list, verbatim"*, adds `graphify-docs-extract.py` — an H row in §5.5 that §8's S2 sentence does not name. An H row has already been moved from S3 into S2 without anyone treating it as a maintainer question |
| The marginal cost is small | **Confirmed.** §5.4's final row makes *"every `SKILL.md` (46) — header stamped"* an M row, so W37-6's script already writes to all seven files. Option (a) adds content to files the commit touches regardless |

### 2. Ruled

**Chosen: option (a)** — the creating instruments land in W37-6's single commit.

**Rejected: option (b), freeze all document creation between W37-6 and W37-7.** It cannot
cover the interval it exists to protect: W37-7's own leaf plan and ledger are created inside
that interval, so the freeze would have to exempt the work it is protecting, which is not a
freeze. Independently, a document-creation freeze is a standing instruction to every role on a
team whose every artifact is a document, with no bounded end date — that is a process
direction, not a mechanism, and it is not this role's to impose.

**Rejected: option (c), accept the window.** For the same reason. "Accept" would mean
accepting a red gate on W37-7's own pull request, which contradicts D14 rather than living
within it.

**And the set is a criterion, not a list.** Seven is the floor, not the ceiling. The rule:
**every instrument whose output is checked by checks 30–39 from the migration commit lands in
W37-6.** W37-6's leaf plan derives the set by walking checks 30–39 and asking of each, *which
instrument tells an author how to produce the thing this check tests?*, and records the derived
list with the check each entry answers to. The seven the plan names are the floor;
`git-hygiene` (check 39's branch and PR-title grammar) and `.claude/skills/README.md`
(`CLAUDE.md` §12 requires the index to move with the skills, and §5.4 gives it a *"creates"*
column) are named here as candidates the derivation must dispose of **explicitly — adopted or
excluded with a reason** — not as members asserted by this record. A list of exemplars invites
fixing the exemplars and stranding the rest; a criterion does not
([`NT-0003`](../notes/0003-duplicated-status-goes-stale.md)).

### 3. What it obliges

- W37-6's leaf plan carries a section deriving the instrument set from checks 30–39, one row
  per instrument naming the check that puts it there. The plan's seven are the floor.
- Every instrument moved into W37-6 has its `Verified` date refreshed in the same commit
  (`CLAUDE.md` §12), and `.claude/skills/README.md` moves with them if the derivation includes
  it.
- W37-7's scope needs no plan edit: it is already worded *"§5.4's rows, less whatever DP-1
  moves into W37-6"*. The two leaf plans carry the split.
- The dated maintainer go-ahead that W37-6's preconditions already require **covers the
  enlarged commit only if the enlargement is disclosed when it is asked for.** It is not
  assumed by this ruling.
- `docs/roadmap.md`'s W37 row currently reads *"three block the migration run itself (two the
  maintainer's, one the decision-maker's)"*. After this record none of the three is the
  maintainer's. Amending that row is the lead's, not this role's — flagged, not done.

### 4. Acceptance — the violation that must become detectable

Two, because a mutation proof tests the implementation against the check and never the check
against the requirement.

1. **Requirement-facing, and it costs nothing extra because the artifact must exist anyway.**
   W37-7's own leaf plan and its ledger are created by following **only** the instruments
   merged in W37-6, and `python3 scripts/audit-docs.py` is run on W37-7's branch *before* any
   hand correction. **Violation: any of checks 30, 31, 33 or 36 fires on either of those two
   files.** If one does, DP-1 was not implemented — and hand-correcting the file rather than
   the instrument is the same failure repeating, so the correction is filed as a finding
   against W37-6, never as a quiet edit.
2. **Implementation-facing.** For each instrument in the derived set, restoring that one file
   to its merge-base content and re-running W37-6's acceptance sweep must produce at least one
   hit naming that file. **Violation: an instrument whose reversion changes nothing any check
   can see** — it is either out of scope or its edit was cosmetic, and either way the set was
   derived wrong.

---

## Ruling 67 — DP-2: the legacy-form sweep is repaired in two parts — fix the pattern first, then a bounded, load-bearing exclusion list

### 1. Verified first, at `04ec6bf`

| Claim | Verdict |
|---|---|
| §7 (d) *"is unpassable as written"* | **Confirmed, by the strongest available witness: the item matches its own text.** Running (d)'s pattern against line 426 of `docs/notes/0019-one-id-per-document.md` — the line that *is* §7 — returns one hit: `NT-00`, the bare prefix fragment inside (d)'s own alternation. After the migration that file is a frozen `RFC-` whose body lines the migration may not change (§4: *"Never changed: a body line of any frozen file"*), and `NT-00` with no following digits is not a citation the step-6 prefix allow-list can consume. The item fails on itself, permanently, with no defect anywhere in the migration |
| `REDIRECTS.csv` is among the *"structural hits"* the plan lists | **Loose, and it does not weaken the conclusion.** (d) already excludes `REDIRECTS.csv` and `was:` lines by name — those are the *"two"* exclusions option (a) proposes extending |
| *"(c) drops the code tree, which is where 767 of the citations live"* | **Not confirmed. The figure is a misreading, and the correct measurement is different and stronger.** 767 is NT-0019 §10's count of **files** — whole tree, all areas — matching the requirement-id pattern at `8f5d57d`; it is neither a code-tree share nor a count of citations. The same command returns **773 files** at `04ec6bf`, and `docs/roadmap.md`'s W37 row has already re-measured the in-scope figure to 768 at `bc7bc36`. Measured against (d)'s **own** pattern at `04ec6bf`: **881 files hit, of which 598 (68 %) lie outside `docs/`** — 496 of them code (`backend` 217, `frontend` 144, `packages` 135), plus `.claude` 55, `scripts` 16, `tests` 13, `examples` 6, `.github` 3, `deploy` 2 and seven root files |
| (d) and check 36 are the same rule | **Confirmed, and nothing in the plan connects them.** Check 36's third clause is *"no pre-migration form survives outside the CSV and `was:` lines"* — (d) at the migration tree, check 36 standing thereafter |

### 2. Ruled

**Chosen: option (a)** — a named constant exclusion list, extended from the two the item
already states, with a reason per entry — **in two parts, the first of which shrinks the list
the second has to carry.**

**Part 1 — fix the pattern; do not exclude the file.** Every alternative in (d) must match a
**complete** legacy identifier or path, never a proper prefix of one. `NT-00` is a prefix
fragment: it exists to catch `NT-00nn`, and written in the complete-id form it still catches
every note id that has ever existed while no longer matching its own text. The executor audits
every alternative against that rule, not only this one. **This is an amendment to the item's
pattern and is stated as one so it is visible** — a rule that yields still yields visibly.
Excluding a whole frozen file to hide a single fragment match would blind the sweep to every
genuine unrewritten citation in that same file, which is the opposite of what (d) is for.

**Part 2 — the residue, bounded.** What survives Part 1 is the class of file whose *function*
is to carry legacy forms as data. Exclusion is permitted for that class only, entry by entry:
`REDIRECTS.csv` (already in the item); `was:` lines wherever they appear (already in the item);
and a file whose purpose is to **name** legacy forms in order to detect or rewrite them —
`doc-id.py`'s rewrite pattern table, and the fixtures and expected-output files of the
migration and of check 36. Nothing else. In particular **no exclusion may name a path the
migration is required to rewrite**, which is what stops option (c) being smuggled back in one
entry at a time.

**Rejected: option (b), construct every pattern so it cannot self-match.** Not merely
unmaintainable — **insufficient**. The decisive self-match is `NT-00` inside NT-0019 §7's own
text: a body line of a file that after the migration is frozen and that §4 forbids the
migration to change. No amount of care in writing `doc-id.py` reaches it. The plan rejects (b)
for its cost; it should have rejected it for not working, and an implementer who reads only the
cost argument may revive (b) on the belief that a tidy encoding solves it.

**Rejected: option (c), narrow (d) to `docs/`.** It drops 598 of 881 files (68 %) at
`04ec6bf`, including all 496 code files, all of `.claude/`, `scripts/`, `tests/` and the root
governance files. That is a reduction in what the migration is *verified* to have done. It is
rejected on the merits — and see *What would have gone back to the maintainer* below, because
had it been the right answer it would not have been mine to give.

**One shared constant.** (d) and check 36 are one rule at two times, so they read **one**
constant in `scripts/audit-docs.py`, pattern and exclusion list defined once. Two definitions
of "a legacy form" will drift, which is `NT-0003`, and is exactly how the process-core extract
fell two commits behind its source with the gate green throughout (`CLAUDE.md` §15).

### 3. What it obliges

- W37-4 defines the constant alongside check 36 — the slice already carries a single
  module-level scoping constant for checks 30–39, so this is a second one beside it, not a new
  mechanism. **DP-2 therefore blocks W37-4, not only W37-6**; the plan marks it blocking on
  W37-6 alone, and that is the earlier of the two dates that matters.
- W37-5's fixture corpus proves the constant; W37-6's acceptance item (d) runs it.
- Each exclusion entry carries its reason inline, in the constant, not in a commit message.

### 4. Acceptance — the violation that must become detectable

1. **Every exclusion must be load-bearing.** Removing any single entry from the exclusion
   constant must make the sweep return at least one hit, and the hit must come from the file
   class that entry names. **Violation: an entry whose removal changes nothing** — it is
   unjustified and must be deleted. This is the check that keeps option (a) from decaying into
   option (c) by accretion.
2. **The sweep must still catch a real survivor.** Insert into a file that is **not** excluded
   one line per family carrying a complete legacy identifier — `NT-0016`, `FR-MODEL-45`,
   `F-W9-3`, `F27`, `wf-01`, `Ruling 62`, `ADR-0001`, `W11-3`, `docs/audit/`, `.claude/notes/`
   — and the sweep must return every one. **The positive control must invoke the shipped
   constant, never a re-typed copy of the pattern**: a control that runs a different regex body
   goes green because of what it misses. **Violation: any of the ten not returned.**
3. **One definition, not two.** Mutate the constant and both (d) and check 36 must change
   behaviour. **Violation: one changes and the other does not.**

---

## Ruling 68 — DP-3: (g) is a property of the script, its filter is a closed enumeration, and it shares check 34's predicate

### 1. Verified first, at `04ec6bf`

| Claim | Verdict |
|---|---|
| The collision is real | **Confirmed.** §7 (g) requires *"the migration diff filtered to hunks that are neither header nor citation-token"* to be empty. §8's S2 sentence names hand-edited items that *"must land in the same commit"* — `audit-docs.py` parsers and roots, `register-*.py`, `req-coverage.py`, `scope-audit.py`, `file-census.py`, the ten fixture tests, the `docs.yml` filter, the core-JSON digest, the `roadmap.md` restructure, `delivery-process.md`'s vocabulary. Counted: **ten**, as the plan says. None is a header stamp or a citation-token substitution, so over the commit diff (g) cannot be empty |
| A path exclusion could separate them | **Refuted.** Counting §5.2 rows whose Kind cell carries both an M and an H — and excluding the one "H / M" row, which splits a set of *new* files rather than marking one file twice — gives **thirteen**: the specs, the roadmap, the workflows, the ADRs, the notes, the plans, the W11 conformance audit, the register, the findings files, the two split records, the checklists, `delivery-process.md` and its core JSON. The same *file* receives script output and a hand edit in the same commit, so excluding those paths would exclude the script's own output for exactly the files (g) most needs to inspect |
| *"(c) is refused by §8's 'same commit'"* | **Not confirmed — the ground does not hold.** `CLAUDE.md` §10 requires squash-merge on every PR, and `origin/main` is a chain of single-parent squash commits (`04ec6bf`, `d4e094b`, `106e322`, each carrying a `(#N)` suffix). A two-commit branch therefore lands on `main` as one commit, so a boundary *inside the branch* does not violate §8's *"same commit"* at all. (c) fails for a different reason, given below. This is recorded because an implementer who reads *"refused by §8"* and then discovers squash-merge will conclude the ruling was wrong and split the merge |
| (g)'s filter is defined | **Refuted.** *"Neither header nor citation-token"* does not classify the script's own remaining steps — the splits of §4 step 2, the `roadmap.md` restructure of step 3, the moves of step 4, or the regenerated artifacts of step 7. Left as worded, an executor invents a filter at the console |

### 2. Ruled

**Chosen: option (a)** — (g) is a property of the **script**, computed over the script's own
output on a clean tree; the H rows are applied afterwards and land in the same commit.

**Rejected: option (b), a path exclusion for the H files** — refuted above: twelve §5.2 rows
put script output and hand edits in the same file.

**Rejected: option (c), split the commit** — but **not** for the reason the plan gives. Under
squash-merge a branch-internal boundary satisfies §8 either way. (c) fails because a commit
boundary is a **one-time observation on a branch that is deleted at merge** (`CLAUDE.md` §10,
branch auto-delete), and `CLAUDE.md` §13 warns against naming a tip rather than a range for
precisely this reason. Option (a) makes (g) re-derivable at any later date from the recorded
merge-base, because §4 states the script is *"deterministic and idempotent"*. **What is not
rejected is the branch structure**: an executor may produce (g)'s evidence by committing the
script's output first and the H rows second, because that is a cheap and mechanical way to
compute the same diff. This ruling settles what (g) *means*, not how many commits the branch
has before it is squashed.

**(g)'s filter is a closed enumeration.** §4's steps 1–7 are the closed list of what `migrate`
is permitted to do, and the filter is that list — a hunk is permitted only where it is:

1. a front-matter block added, together with the legacy prose or bullet header it replaces
   being removed (§4 step 5);
2. a reference token substituted inside a line, from the step-6 allow-list (§4 step 6);
3. a file moved or renamed, detected as a rename, with no content change (§4 step 4);
4. a split, where the concatenation of the outputs reproduces the input's body lines in order
   (§4 step 2);
5. the `roadmap.md` restructure of §4 step 3;
6. a generated artifact regenerated in full — `INDEX.md`, `REDIRECTS.csv`, `docs/contracts/`,
   the core-JSON digest (§4 step 7).

**A hunk the filter cannot classify fails; it is never passed through.** A filter that silently
drops what it does not understand is the same defect as the vanished scan root that once made
five checks skip while the audit printed *"All checks passed"* and exited 0.

**One definition of "reference tokens only", not two.** Where the file belongs to a frozen
family, (g) uses the predicate the plan already disposed of under DP-7 rather than a second
one: *the new bytes, after removing the leading front-matter block and applying the inverse of
every `REDIRECTS.csv` mapping, are byte-identical to the merge-base bytes.* That is stronger
than a hunk filter, it is already being implemented for check 34, and implementing it twice is
how the two drift apart.

### 3. What it obliges

- W37-6's ledger records the merge-base SHA **and** the exact command that computed (g), so the
  result is re-derivable by checking that SHA out and re-running `migrate`.
- (g)'s filter is implemented as code with the six classes named, not as a shell pipeline
  composed at the console.
- The frozen-family branch of the filter calls check 34's DP-7 predicate rather than
  reimplementing it.

### 4. Acceptance — the violation that must become detectable

1. **The filter must fail on a body-line change.** A mutation fixture in W37-5's corpus makes
   `migrate` alter one word of a body line that is neither a header nor a reference token.
   **Violation: (g) is empty on the mutated run** — the filter is wider than the rule, and (g)
   is not testing the script. It must be non-empty *and* name that file.
2. **The filter must fail on what it cannot classify.** Feed it a hunk in none of the six
   classes — a body line reordered within a file. **Violation: an unclassifiable hunk that
   produces no output.**
3. **One predicate, not two.** Mutate check 34's DP-7 allowance. **Violation: (g)'s
   frozen-family branch does not change with it.**

---

## Ruling 69 — NT-0019 §1.5's vendored parenthesis is a gloss, not a detector: the set is declared and reconciled, and the exemption reaches only the blanket passes

### 1. Verified first, at `04ec6bf`

§1.5 reads: *"A vendored skill (`planning-with-files`, `ui-ux-pro-max`, `graphify`,
`systematic-debugging`, the `vue-*` skills — anything shipping its own `LICENSE`) carries
`vendored: true` and `origin:` on its `SKILL.md` only; the files beneath are exempt from
stamping, citation rewrite and shape checks."* §5.4 restates the criterion with a carve-out:
*"any directory holding a `LICENSE` that is not the repository's own"*.

| Claim | Verdict |
|---|---|
| Exactly two skills ship a `LICENSE` | **Confirmed.** `git ls-files '.claude/skills/**'` filtered for a licence filename returns `planning-with-files/LICENSE` and `ui-ux-pro-max/LICENSE`, and nothing else anywhere under `.claude/`. The repository's own root `LICENSE` exists, so §5.4's carve-out is needed and correct as far as it goes |
| The criterion misses three of the five names in its own parenthesis | **Confirmed.** `graphify`, `systematic-debugging` and every `vue-*` skill ship no licence file |
| The repository's recorded vendored set is 28 | **Confirmed, from two independent expressions.** `pyproject.toml` lines 52–79 exclude **28** skill directories from `ruff`, which `CLAUDE.md` §12 makes the marker of a vendored file (*"Vendored files stay as upstream wrote them, excluded from `ruff`"*); and `.claude/skills/README.md` records the provenance as fourteen from `obra/superpowers`, five from `wdm0006/python-skills` and six from `yes-404/vue3-skills`, plus three standalone — 28. There are 46 skills in total |
| So the published criterion under-exempts | **Confirmed and quantified.** 339 tracked files lie beneath the 28 vendored `SKILL.md` files; **240** of them lie beneath the 26 that ship no licence. Those 240 are what a `LICENSE`-keyed `is_vendored` would fail to exempt from stamping and the tree-wide citation rewrite |
| The ruff exclude list is therefore the right criterion | **Refuted, and this is the finding the report did not reach.** Nine of the 28 carry a change row in NT-0019 §5.4: `brainstorming`, `executing-plans`, `graphify`, `planning-with-files`, `requesting-code-review`, `secret-hygiene`, `subagent-driven-development`, `testing-strategy`, `writing-plans`. **Two of those nine — `writing-plans` and `subagent-driven-development` — are primary creating instruments** that Ruling 66 places in W37-6's commit. Adopting the ruff list as `is_vendored` would exempt them from the migration entirely, which collides head-on with Ruling 66 |
| Any set can answer the question | **Refuted.** `planning-with-files` is one of the *two* the published criterion selects **and** carries a §5.4 edit row. Every candidate population contains a file the note requires the migration to change, so no choice of population resolves the contradiction |
| `CLAUDE.md` §12 forbids editing a vendored file | **Refuted — read to the end of the clause.** It reads *"Vendored files stay as upstream wrote them, excluded from `ruff`, **every deviation recorded in the README rather than made silently**."* Deviation is permitted and bounded by a record, not prohibited. `.claude/skills/README.md` already carries several, including a renamed skill and two changes to a vendored script |
| The exemption covers the whole subtree | **No — it covers the files *beneath* `SKILL.md`.** §1.5 puts the fields *"on its `SKILL.md`"* and exempts *"the files beneath"*; §5.4's final row stamps **every** `SKILL.md` (46) and adds two fields for vendored ones. A vendored skill's own `SKILL.md` is stamped either way |

### 2. Ruled

**Chosen: the third option — `vendored` is declared and reconciled, never detected.** §1.5's
parenthesis is a **gloss identifying which skills the author had in mind**, not a specification
of an algorithm: it names nine and then offers a shorthand that is wrong about three of those
nine and about 26 of the repository's 28. What §1.5 states *normatively* is a **field** —
`vendored: true` and `origin:` — and a **consequence**. A field is a declaration, and a
declaration needs no detector. **§1.5 is not edited, and nothing in §1 moves**; only the
implementation changes.

**Rejected: keying `is_vendored` on `LICENSE` presence, as published.** It under-exempts 240
tracked files at `04ec6bf` and contradicts its own examples.

**Rejected: adopting `pyproject.toml`'s ruff exclude list as the criterion.** It over-exempts:
nine of its 28 entries carry a §5.4 change row, and two of those are creating instruments
Ruling 66 requires in W37-6's commit. It is also authoritative for a different purpose — lint
scope — and would silently redefine the migration's reach whenever someone edited a lint
setting.

**The mechanism, in four parts.**

1. **One constant, seeded once by hand.** `_VENDORED_SKILLS` is a named constant listing the
   28 skill directories, seeded from `.claude/skills/README.md`'s provenance sections, which
   `CLAUDE.md` §12 makes the place vendoring is recorded. It is the single source the migration
   and checks 30–39 consume. Because the migration is what *creates* the headers, the set
   cannot be read from them at migration time; that is why it is a constant and not a header
   sweep.
2. **Reconciled against the second expression, so drift is loud.** A gate check asserts that
   `_VENDORED_SKILLS` equals `pyproject.toml`'s ruff `exclude` restricted to
   `.claude/skills/`. The ruff list is **not** the criterion; it is the independent second
   witness. If either moves without the other, the gate reds and a human decides — never a
   silent pick. This is the answer to the objection that the ruff list can drift: we do not
   trust it, we reconcile against it.
3. **The exemption reaches only the blanket passes.** A vendored skill's own `SKILL.md` is
   stamped like the other 45 and additionally carries `vendored: true` and `origin:`. The files
   **beneath** it are exempt from the blanket stamp, the tree-wide citation rewrite and check
   37's shape check. **Exempt from the blanket pass is not the same as never touched:** a named
   row in §5.4 is a deliberate edit and is applied, with the deviation recorded in
   `.claude/skills/README.md` in the same commit. Nine such rows exist at `04ec6bf`, named
   above.
4. **The interface is preserved.** `is_vendored`'s signature is unchanged, so W37-3 and W37-4
   compile against the same contract; only its body changes, from a filesystem probe to a
   membership test. The executor implemented the published rule and flagged the defect rather
   than redesigning silently, which is the behaviour this ruling wants to keep cheap.

**On stamping an upstream file at all.** Adding front matter to a vendored `SKILL.md` is a
deviation from *"as upstream wrote them"*. NT-0019 §1.5 mandates it, and the maintainer's
precedence ruling of 2026-09-01 makes NT-0019 outrank current practice. A rule that yields
still yields visibly: it is recorded in `.claude/skills/README.md` **once, as a class covering
all 28**, not 28 times.

### 3. What it obliges

- W37-2 replaces `is_vendored`'s body with the membership test and keeps its signature; the
  constant lands with it.
- W37-4 adds the reconciliation check against the ruff exclude list, with its own broken-input
  proof.
- W37-6 applies the nine §5.4 rows as deliberate edits and lands the README entries in the same
  commit. Two of the nine are also Ruling 66's creating instruments, so they are in that
  commit for two independent reasons.
- **Nothing in `docs/notes/0019-one-id-per-document.md` is edited.** §1 stays byte-identical to
  the maintainer's original.

### 4. Acceptance — the violation that must become detectable

1. **Population drift must be loud.** Remove one entry from `_VENDORED_SKILLS`, or one skill
   line from `pyproject.toml`'s ruff `exclude`, and the gate must red naming which side moved.
   **Violation: either edit passing green** — a check that reads only one of the two sources
   cannot fail this way, and that is precisely the test.
2. **Under-exemption.** On a fixture tree, a vendored skill has a file beneath its `SKILL.md`
   carrying a legacy citation and no header. After `migrate`, that file must be byte-identical.
   **Violation: it gained a front-matter block, or its citation changed.**
3. **Over-exemption.** After W37-6, `writing-plans` and `subagent-driven-development` must both
   differ from their merge-base content by their §5.4 edits. **Violation: either is unchanged**
   — the exemption swallowed a creating instrument, which is the exact failure mode of adopting
   the ruff list as the criterion.
4. **Recorded deviation.** **Violation:** `git diff --name-only <merge-base>..HEAD` names a file
   under a vendored skill while `.claude/skills/README.md` is absent from the same diff.

---

## What would have gone back to the maintainer

Stated so the boundary is visible rather than implied, and so a future reader can tell that the
delegation was read narrowly by the party it empowered.

- **DP-1 option (b)** — a standing document-creation freeze across the team — would have been a
  process direction with no end date, not a mechanism. Had it been the right answer, it would
  have gone back.
- **DP-2 option (c)** — narrowing the sweep to `docs/` — would have reduced what the migration
  is verified to have done by 598 of the 881 files the sweep covers (68 %). That is a scope
  reduction and would have gone back. It is rejected on the merits instead, so the question
  does not arise.
- **Any change to NT-0019 §2's D0–D14, or to §1's text.** None is made. Ruling 69 resolves a
  §1.5 contradiction entirely inside the implementation for exactly this reason.
- **DP-4 and DP-6** are untouched. DP-4 is non-blocking and resolves at W37-11; DP-6 concerns
  amendments to `CLAUDE.md`'s own requirements, which §12 reserves to the maintainer and which
  no delegation this record relies on reaches.

## Provenance

Written 2026-09-02 by the decision-maker role. Every claim in each `### 1.` table was checked
against the repository at `04ec6bf` in this session, by the command named beside it; none was
taken from the lead's relay, and three of the plan's stated grounds were found wrong and are
recorded as such rather than repeated — the 767-file figure (Ruling 67), the reason option (b)
fails (Ruling 67), and the reason option (c) fails (Ruling 68). The delegation under which
DP-1 and DP-2 were ruled is quoted in the Authority section above with its date; the maintainer
did not rule these personally.
