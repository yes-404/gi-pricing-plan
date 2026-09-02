# W37-6 — The migration run: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement
> this plan task-by-task, **single executor, supervised, not fanned out**. Steps use checkbox
> (`- [ ]`) syntax for tracking.

**Goal:** Run NT-0019's migration once, as one supervised pull request at a gap — renumber
every document and requirement id in the repository onto one global sequence, move every
governed document into its family directory, dissolve `docs/audit/`, stamp a machine-readable
header on every governed file, rewrite every citation across the tracked tree, widen
`audit-docs.py` checks 30-39 from their two S1 scope roots to the whole corpus, and land in
the same commit every instrument an author would otherwise follow to produce a document the
widened checks reject.

**Architecture:** A leaf plan under
[`2026-09-01-nt-0019-id-standard-map-plan.md`](2026-09-01-nt-0019-id-standard-map-plan.md)'s
Slice W37-6, per [`../process/delivery-process.md`](../process/delivery-process.md) §3. The
map plan cut the Work into eleven slices and sized them; **this plan's task list is written
from the auditor's full-class sweep**
([`../audit/nt-0019-verification-and-impact-sweep.md`](../audit/nt-0019-verification-and-impact-sweep.md),
pinned at `89dd2b1`), not from the map plan's evidence table — the map plan says so in its own
W37-6 section, and the sweep corrected the two largest rows of NT-0019 §5.6 by more than a
factor of two. Every population is **re-measured at `39ee30c`** here and both figures shown,
because the sweep's pin is nine commits behind `origin/main` as this plan is filed and four of
the classes have grown.

The work divides into three kinds and this plan keeps them apart, because they fail
differently: **script output** (deterministic, re-derivable, proven on a fixture corpus in
W37-5), **hand edits the script cannot know** (NT-0019 §5's **H** rows scoped to stage S2), and
**instruments** (Ruling 66's derived set — the files that tell an author how to produce a
document the widened checks will judge).

**Tech Stack:** Python 3.12 standard library only for `scripts/doc-id.py`,
`scripts/doc-index.py` and the `scripts/audit-docs.py` changes (Global Constraint G4 — a
verified fact about the docs CI job, not a preference). `pytest` for the fixture proofs. Git
plumbing (`git ls-files`, `git mv`, `git log --diff-filter=A`) for provenance and moves. No new
dependency is added to any `pyproject.toml` by this slice.

**Spec:** [`../notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md) — §4
(migration steps 1-8), §5 (impact map, **M**/**H** kinds), §7 (acceptance items (a) to (k)),
§8 (sequencing, stage S2). The note is `accepted` and outranks current practice (G1); its §1
standard and its D0 to D14 decisions are fixed inputs, never reopened here.

**Filed:** 2026-09-02 (UTC), against `origin/main` at `39ee30c`, by the planner. Frozen at this
date — a filed plan is a record of what was believed then, not an instruction edited to agree
with the repository later ([`README.md`](README.md) in this directory). A replan is a new dated
file that supersedes this one, never an edit to it.

**Status of this document: complete except where a line says `PENDING W37-5`.** W37-5
(`doc-id.py migrate` and its fixture corpus) is in flight as this plan is filed, so the
`migrate` command's exact flag surface and output shape are not yet fixed. Every such
dependency is marked in place rather than guessed, and §3 lists all six together.

---

## Acceptance Standard

The slice is complete when every item below passes **at the merge tree**, each recorded in the
slice's ledger with the exact command and its output. Every item is stated as **a violation
that must become detectable**, never as a property asserted: an item that cannot fail has not
been tested (`CLAUDE.md` §13).

1. **(a) Classification — nothing unclassified.** `python3 scripts/doc-id.py check --classify`
   prints a per-family count table whose total equals `git ls-files docs/ | wc -l` and whose
   `none` row is **0**. *Violation: a positive `none` row, or a total below the `git ls-files`
   count — a file that failed to parse, or one silently dropped from the walk.*
2. **(b) Sequence integrity.** `python3 scripts/doc-id.py check` exits 0: zero duplicate
   numbers, the sequence contiguous over merged records, every file's header `id` equal to the
   integer its filename pads. *Violation: any duplicate, gap, or id/filename disagreement —
   proven detectable by re-running against a copy of the tree with one filename's number
   incremented by one, which must exit 1 naming that file.*
3. **(c) Index byte-stability.** `python3 scripts/doc-index.py --check` exits 0 **and**
   `git status --porcelain docs/INDEX.md` is empty after a fresh `python3 scripts/doc-index.py`
   run. *Violation: a non-empty `git status` — the committed index is not what the generator
   produces, the drift `CLAUDE.md` §2 forbids for a generated artifact.*
4. **(d) Legacy-form sweep.** The sweep runs from the **shipped constant** in
   `scripts/audit-docs.py` (Ruling 67: one constant, pattern and exclusion list defined once,
   shared with check 36 — never a re-typed copy at the console) over `git ls-files`, and
   returns nothing. Two violations, both required: *(i) any hit outside the exclusion set;
   (ii) the positive control — insert into a **non-excluded** file one line per family carrying
   a complete legacy identifier and the sweep must return every one; any not returned is a
   violation.* Ruling 67 acceptance item 2 fixes the control's ten members. Every exclusion
   entry must additionally be **load-bearing**: removing it must make the sweep return at least
   one hit from the file class that entry names. *Violation: an entry whose removal changes
   nothing.*
5. **(e) No padded id in prose.** `python3 scripts/audit-docs.py` check 32 exits 0 over the
   **whole corpus**, and its deliberately-broken fixture (a padded id outside a link target)
   makes it exit 1. *Violation: check 32 green on the broken fixture.*
6. **(f) No product identifier moved.** `git grep -c 'VR-DST-1'`, summed over all files, equals
   the value recorded in this slice's ledger **from the run's own merge-base**, re-derived in
   the running session. *Violation: any difference.* See §5.4 — the baseline is **not** the
   historical figure NT-0019 §7 (f) names, and pinning it to that figure guarantees a false red.
7. **(g) The script touched only headers and reference tokens.** The `migrate` run's own diff
   on a clean tree, filtered through the six-class closed enumeration Ruling 68 fixes,
   implemented **as code**, is empty; its frozen-family branch calls
   `audit_docs.frozen_diff_is_permitted` rather than a second equivalent predicate. Three
   violations: *(i) a body-line mutation fixture that leaves (g) empty; (ii) an unclassifiable
   hunk that produces no output; (iii) mutating check 34's DP-7 allowance without (g)'s
   frozen-family branch changing behaviour.*
8. **(h) Both halves of the gate, green, at the merge tree.** `python3 scripts/audit-docs.py`;
   `uv run python scripts/req-coverage.py`; `uv run ruff check .`; `uv run mypy`;
   `uv run lint-imports`; `uv run pytest -q`;
   `uv run python scripts/generate-contracts.py --check`; `pnpm --dir frontend lint`,
   `type-check`, `test`, `build`. *Violation: any non-zero exit. A Python-only run is not the
   gate (`CLAUDE.md` §11, G7).*
9. **The scan-roots guard was re-derived, not loosened.** `tests/test_audit_docs_scan_roots.py`
   asserts the **new** literal constant text, and its mutation still reds the audit; the same
   proof exists for **each of the five `docs/audit/`-dependent paths in
   `check_finding_citations`** enumerated in §7.2. *Violation: the assertion weakened to a
   substring, a regex or an existence probe; or any of the five re-pointed without a mutation
   proof that reds.*
10. **The widened scope is the stamped set, exactly.** The post-flip value of
    `_ID_SCOPE_ROOTS` selects the same file set NT-0019 §4 step 5 stamps, and
    `python3 scripts/audit-docs.py` prints that count per root. *Violation: check 30 demanding
    a header on a file step 5 does not stamp (237 such files exist at `39ee30c` — §7.1), or
    silence about a file step 5 does stamp.*
11. **Every derived instrument is load-bearing — tested on its H content, not on its file.**
    Ruling 66 acceptance item 2 says reverting a member to its merge-base content must produce
    at least one hit naming that file. **Run as written, that test passes for every member and
    for 930 non-members alike**, because §4 step 6 rewrites citations in every tracked file, so
    any reversion produces an item-(d) hit (§10 finding 12). The discriminating form, which is
    what the ruling's *"either out of scope or its edit was cosmetic"* is reaching for: revert
    **only the member's H content** — its taught filename, id, header-field or section form —
    leaving its rewritten citations in place, then produce the document that instrument mints
    and run `python3 scripts/audit-docs.py`. *Violation: no check in 30-39 fires on that
    document.* **Two members are exempt from this item, and the exemption is stated here rather
    than discovered:** member 13 (`.claude/skills/README.md`), which is adopted on `CLAUDE.md`
    §12 and mints nothing, and member 12 (`brainstorming`), whose correction *removes* a `docs/`
    path rather than replacing one, so there is no document to produce from the reverted form.
12. **Requirement-facing, and it is the one that matters.** W37-7's own leaf plan and its
    ledger are created by following **only** the instruments merged in this slice, and
    `python3 scripts/audit-docs.py` is run on W37-7's branch **before** any hand correction.
    *Violation: any of checks 30, 31, 33 or 36 firing on either of those two files.* If one
    does, DP-1 was not implemented, and hand-correcting the file rather than the instrument is
    the same failure repeating — the correction is filed as a finding against W37-6, never as a
    quiet edit (Ruling 66 acceptance item 1).
13. **Vendored exemption reaches only the blanket passes.** After the run, a file beneath a
    vendored skill's `SKILL.md` carrying a legacy citation and no header is byte-identical to
    its merge-base content; `writing-plans` and `subagent-driven-development` both differ from
    their merge-base by their §5.4 edits. *Violations: the first gained a front-matter block or
    a rewritten citation; either of the second two is unchanged* (Ruling 69 acceptance items 2
    and 3). And: *`git diff --name-only <merge-base>..HEAD` names a file under a vendored skill
    while `.claude/skills/README.md` is absent from the same diff* (item 4).
14. **The three W37-4 deferrals are discharged or re-deferred with a named owner**, each in the
    ledger with its verdict. *Violation: any of the three unmentioned* — silence is not one of
    `CLAUDE.md` §13's four verdicts.

---

## Global Constraints

Every task's requirements implicitly include the map plan's **G1 to G10**
([`2026-09-01-nt-0019-id-standard-map-plan.md`](2026-09-01-nt-0019-id-standard-map-plan.md),
its Global Constraints section), copied there verbatim from their sources and not restated here
— one source, not two. The four that bite hardest in this slice:

- **G2 — the permanence rule yields, at two sites, and not in this slice.** `CLAUDE.md` states
  *"Requirement IDs and section numbers are permanent ... Never renumber"* at line 27 and again
  at line 107. D2 renumbers every requirement id. **Both sites are edited in W37-9, not here.**
  Between this slice's merge and W37-9's, the governed contract states a rule the repository has
  just broken. Disclosed in §4.6 rather than left for a reader to discover.
- **G4 — standard library only.** The docs CI job installs no dependencies. Nothing this slice
  adds to `audit-docs.py`, `doc-id.py` or `doc-index.py` may import PyYAML or any other
  third-party package.
- **G5 — product identifiers are never touched.** `VR-*`, artifact ids and job kinds are product
  data governed by `docs/specs/` (D5). The rewrite list in `doc-id.py` is an **allow-list** of
  prefixes; `VR` is not on it.
- **G10 — the local working tree is outside the standard.** Nothing outside the repository is
  migrated, stamped, renamed or linted — enforced by the tool as well as by the rule: §4 step 6
  operates over `git ls-files`, which cannot reach outside the repository.

Two more bind this slice specifically:

- **G11 — every touched file is compiled and its suite run.** §5.6's closing sentence is the
  reason: *"a rewrite inside an asserted string is the reason."*
- **G12 — the rebase rule.** §4 step 8: *"Land at a gap; rebase any branch that appears by
  re-running step 6 on its diff."* If a branch appears mid-run, the recovery is to **re-run the
  citation rewrite over that branch's diff** — never to hand-edit it, and never to merge it
  ahead of the migration and re-run `migrate`.

---

## 1. Preconditions — re-derived in the running session, never inherited from this plan

The map plan states these. This plan deliberately does **not** record today's answers to the
three volatile ones: a plan that bakes in a gap check turns a live condition into a stale claim
the executor then reads as satisfied. Each is re-run in the session that runs the migration and
its output pasted into the ledger with a timestamp.

- [ ] **DP-1, DP-2 and DP-3 each carry a resolver id.** Satisfied at filing:
      [`2026-09-02-w37-migration-preconditions-rulings.md`](2026-09-02-w37-migration-preconditions-rulings.md)
      — Ruling 66 (DP-1), Ruling 67 (DP-2), Ruling 68 (DP-3). Ruling 69 in the same record fixes
      NT-0019 §1.5's vendored criterion, which this slice applies. Rulings 70, 71 and 72
      ([`2026-09-02-w37-field-set-and-rollup-rulings.md`](2026-09-02-w37-field-set-and-rollup-rulings.md))
      each carry an obligation onto this slice; they are discharged in §7.8 and §8.
- [ ] **The auditor's full-class sweep has landed and its per-row result is attached to this
      leaf plan.** Satisfied at filing:
      [`../audit/nt-0019-verification-and-impact-sweep.md`](../audit/nt-0019-verification-and-impact-sweep.md),
      merged as PR #560, pinned at `89dd2b1`. §5.3 carries its per-row result and what it
      changed about this task list.
- [ ] **`gh pr list --state open` returns nothing.** *Re-run in the session.* At filing, W37-5's
      branch exists locally and its PR is expected, so **this precondition will be false until
      W37-5 is merged.** That is the sequencing constraint, not an obstacle to discover on the
      day.
- [ ] **`git branch -r` lists only `origin/main`.** *Re-run in the session.*
- [ ] **`git status --porcelain` is empty.** *Re-run in the session, in the worktree the
      migration runs in.* Note the shared-checkout hazard: sibling worktrees share this `.git`,
      so `origin/main` can advance between the check and the run. Record what
      `git rev-parse origin/main` returns **in the same command** that records the check.
- [ ] **The maintainer has given a dated go-ahead for this specific run, with the enlargement
      disclosed.** Ruling 66 §3: the go-ahead *"covers the enlarged commit only if the
      enlargement is disclosed when it is asked for. It is not assumed by this ruling."* §4 is
      that disclosure.

**This plan contains no acceptance line and must not be read as one.** The maintainer's
acceptance is theirs alone; this document exists to make it an informed one.

---

## 2. What this plan is complete on

| Part | Section | State |
|---|---|---|
| The derived instrument set, with the check that puts each member there | §6 | Complete — 13 members, 9 exclusions, closed against an exhaustive enumeration |
| The maintainer's disclosure | §4 | Complete |
| The precondition checklist | §1 | Complete |
| The measured baseline, at two pins | §5 | Complete |
| The sweep-driven task list | §7 | Complete except the six `PENDING W37-5` lines |
| The scan-roots handling, all five path dependencies enumerated | §7.2 | Complete |
| The acceptance items, each a detectable violation | Acceptance Standard | Complete |
| The three W37-4 deferrals and register finding F68 | §8, §9 | Complete |
| Findings against the inputs | §10 | Complete |

---

## 3. What waits for W37-5 — named gaps, not guesses

W37-5 builds `scripts/doc-id.py migrate` and its fixture corpus. Its interface is not fixed at
filing, so this plan states the **obligation** at each point and leaves the **invocation** to be
filled from the merged script. An executor filling one of these in reads the merged `--help`
output; none is invented here.

| # | Depends on W37-5 | What this plan fixes regardless |
|---|---|---|
| 3.1 | The `migrate` subcommand's flag surface — whether the dry run, the diff filter and the classification report are flags, subcommands or separate entry points | That a dry run must exist and must run first; that its output reaches the ledger before anything moves |
| 3.2 | The exact output shape of the (g) diff filter — a hunk list, an exit code, a report file | Ruling 68's six permitted classes; that it is implemented **as code**, not a shell pipeline composed at the console; that an unclassifiable hunk **fails** rather than passing through; that its frozen-family branch calls `frozen_diff_is_permitted` |
| 3.3 | The classification report's format for acceptance item (a) | That the `none` row must be 0 and the total must equal `git ls-files docs/ \| wc -l` |
| 3.4 | Whether `REDIRECTS.csv` is written by `migrate` or by a separate step, and its column order | That every `was:` value has a row, every row's target exists, and the inverse mapping is what `frozen_file_matches_after_migration_stamp` consumes |
| 3.5 | The fixture corpus layout under `tests/fixtures/docs-migration/` | That the mutation fixtures Ruling 68 acceptance items 1 and 2 require exist there **before** the real run |
| 3.6 | Whether `migrate` re-runs step 6 over an arbitrary diff (the G12 rebase path) or that is a separate invocation | That a branch appearing mid-run is recovered by re-running the citation rewrite over its diff, never by hand-editing it |

**A named gap is fine; a guessed CLI is not.** An executor who finds one of these six already
answered by the merged W37-5 records the answer in the ledger. An executor who finds W37-5
answered it *differently* from what this plan assumes files a finding against this plan rather
than adapting silently.

---

## 4. The disclosure — what the maintainer's go-ahead authorises

*Written for the maintainer. Read this before giving the dated go-ahead §1 requires. Nothing
here is a decision; every line states what one commit will do.*

### 4.1 In one sentence

**One squash-merged commit renumbers every document and requirement identifier in this
repository, moves most governed documents to new paths, deletes the `docs/audit/` directory,
rewrites citations in every tracked file that carries one, turns ten audit checks from "scoped
to two paths" to "scoped to everything", and — because of Ruling 66 — also rewrites the
instruments that tell every role how to create a document.**

### 4.2 The size, by area rather than as one total

**1447 tracked files at `39ee30c`.** A single number that large invites either a rubber stamp
or a flinch, so it is broken down by *what the migration actually does to each file*. Commands
are in §5.5; no figure here is estimated or rounded.

| The migration… | Files | Which |
|---|---|---|
| **rewrites a citation token in** | **930** | Every file matching NT-0019 §7 (d)'s own pattern; 20 507 matching lines. By tree: `docs/` 297 · `backend/` 217 · `frontend/` 144 · `packages/` 135 · `.claude/` 55 · `tests/` 45 · `scripts/` 19 · `examples/` 6 · `.github/` 3 · `deploy/` 2 · 7 root files |
| **stamps a header on** | **295** | 234 `.md` under `docs/` (247 less the 13 templates, exempt by path) + 46 `SKILL.md` + 8 agent files + 7 role charters. This set overlaps the 930 |
| **moves, splits or deletes** | **213** | The four trees named by `git ls-tree -r --name-only 39ee30c -- docs/audit .claude/notes docs/notes docs/plans`: `docs/audit/` (43, dissolved into four trees), `docs/notes/` (→ `docs/rfcs/`), `docs/plans/` (130 dated files reclassified, **plus 72 ruling records split out of 29 of them**), `.claude/notes/` (19 stubs deleted) |
| **regenerates, never hand-edits** | **61** | `docs/contracts/` — rebuilt from `model-schema` after §7.9's docstring rewrite, then drift-checked |
| **does not touch at all** | **517** | 1447 − 930. Carries no form the migration rewrites |
| **must leave unchanged, by rule** | **52** | Files carrying a `VR-` catalogue id — **41 distinct ids, 418 occurrences**. D5 and G5 put these permanently out of scope: an id stored, transmitted or asserted by an API contract is product data governed by `docs/specs/`. **5** of the 52 enter the requirement-citation population *only* via a `VR-` id (776 with `VR-` less 771 without) and must come out of the run untouched on that account. Acceptance item (f) is the check |

Two more figures the maintainer will want: **710 distinct requirement ids** are renumbered, and
**1988 `@pytest.mark.req` markers** are rewritten. Ten audit checks widen from two scope roots to
the whole corpus, and **13 instruments** are rewritten under Ruling 66 (§6.2).

### 4.2a The number is growing, and the growth is self-referential

**Both figures already written down were true when written, and both have aged.** Verified by
re-running the same command at each pin rather than by trusting either record:

| Pin | Tracked files | Files the migration rewrites |
|---|---|---|
| `89dd2b1` — the map plan's evidence table, and its W37-6 precondition (*"rewrites citations in 1355 tracked files"*) | **1355** | **876** |
| `04ec6bf` — Ruling 66's evidence tree | **1360** | **881** |
| `39ee30c` — `origin/main` as this plan is filed | **1447** | **930** |

`git ls-tree -r --name-only <sha> | wc -l` reproduces 1355 and 1360 exactly at their own pins, so
neither figure was ever wrong. **The tracked count grew +92 and the rewrite population +54 across
a single session.**

**The mechanism, measured rather than assumed.** Of the 93 files added between `89dd2b1` and
`39ee30c` (`git diff --name-status 89dd2b1 39ee30c --diff-filter=A`):

- **25 under `docs/`** — 13 `_templates/`, 7 `audit/` (finding records and the auditor's sweep),
  4 `plans/` (ruling records and a landing package), 1 `process/` (`document-ids.md`). **Every one
  is a governed document** this migration must classify, stamp, renumber and index. This is the
  self-referential part: NT-0019's own slices produce documents NT-0019 must migrate.
- **65 under `tests/`** — almost all the `tests/fixtures/docs-ids/` corpus W37-4 built.
- **3 under `scripts/`** — `doc-id.py`, `doc-index.py`, `_docid.py`.

**The dominant term is fixtures, not governed documents, and that cuts the other way.** Ruling 67
Part 2 permits excluding exactly this class from the legacy-form sweep — *"a file whose purpose is
to **name** legacy forms in order to detect or rewrite them"* — so the 65 enlarge the tracked
count without enlarging what must be rewritten. **The honest measure of direction is the +54
rewrite population, not the +92 tracked count**, and it is the figure this section leads with.

**Where the cost genuinely is non-linear**, stated because it is the part a flat count hides:
every fixture corpus that names a legacy form adds an entry to `LEGACY_SWEEP_EXCLUSIONS`, and
Ruling 67 acceptance item 1 requires **every entry to be load-bearing** — removing it must make
the sweep return a hit from the class that entry names. W37-5 is building a second such corpus
(`tests/fixtures/docs-migration/`) now. Each one is a small permanent addition to what acceptance
item (d) must justify, and unlike the document count it does not shrink after the migration.

**This is presented as a trend, not as an argument for haste.** A maintainer weighing *now or
later* should know that later is measurably larger and that the size is not constant while the
decision is open; nothing here says the decision should be quick.

### 4.3 The enlargement Ruling 66 requires, stated plainly

The map plan's W37-6 said this commit carries the migration's output plus a list of scripts,
tests, CI and process edits. **Ruling 66 adds the creating instruments**, because a document
created after this commit and before W37-7 would be produced by a skill still teaching the
retired grammar, and D14 makes enforcement red from this commit with no warn phase and no date
switch.

Ruling 66 makes the set **a criterion, not a list**: *"every instrument whose output is checked
by checks 30-39 from the migration commit lands in W37-6."* §6 derives it against the merged
check bodies **and** against an exhaustive enumeration of every instrument in the repository
that teaches an id, filename, header, branch or index form. **Thirteen members** (§6.2) —
the map plan's seven, plus three role charters (`planner`, `auditor`, `decision-maker`),
`writing-skills`, `brainstorming` and `.claude/skills/README.md`. **Nine explicit exclusions**
(§6.3), each with its slice. So the derivation **adds six members the map plan does not name and
excludes one of the two candidates Ruling 66 itself named** — both with reasons, as Ruling 66
requires.

### 4.4 What becomes irreversible

- **Every document's path changes.** Any link held outside this repository — a bookmark, a chat
  message, a local note — pointing at `docs/notes/…`, `docs/audit/register.md` or
  `docs/plans/2026-…` breaks. `REDIRECTS.csv` records every old-to-new mapping *inside* the
  repository; it cannot fix a link held elsewhere.
- **Every requirement id changes.** A module-qualified id becomes a bare number. Anyone holding
  one in their head, in a notebook, or in a local file outside the repository (G10) is holding a
  retired one. `was:` and `REDIRECTS.csv` make the translation mechanical, not automatic.
- **`docs/audit/` ceases to exist.** Its register, closure records, plan reviews, work READMEs,
  checklists and findings become four other trees.
- **The commit is squash-merged and the branch auto-deletes.** Ruling 68 chose option (a) — (g)
  computed as a property of the *script* over its own output — precisely so the evidence
  survives that deletion: it is re-derivable at any later date from the recorded merge-base,
  because `migrate` is deterministic and idempotent. **The recorded merge-base SHA is
  load-bearing evidence, not a courtesy.**
- **`git blame` and `git log --follow` degrade** across every moved file. Rename detection
  handles a pure move; a move plus a header stamp plus a citation rewrite in one commit is
  detected as a rename only above git's similarity threshold. This is not recoverable later.

### 4.5 What does *not* change

- **No product identifier moves** (G5, D5). `VR-*` catalogue ids, artifact ids, job kinds and
  any string persisted or asserted as data are out of scope; acceptance item (f) is the check.
- **Nothing outside the repository is touched** (G10) — by construction, not only by rule.
- **No body line of a frozen file changes.** Splits preserve every line; stamps add lines;
  rewrites change reference tokens only. Acceptance item (g) is the check, and Ruling 68 makes
  it a closed enumeration with **no pass-through** for a hunk the filter cannot classify.
- **Nothing in NT-0019 §1 is edited.** Rulings 69, 70, 71 and 72 each say so explicitly; §1
  stays byte-identical to the maintainer's original.

### 4.6 The window this closes, and the one it opens

**Closes:** the DP-1 window — a document created between the migration and W37-7 under a retired
grammar, which checks 30, 31, 33 and 36 would red. Ruling 66 established that this window is
**occupied by construction**: executing W37-7 at all creates its own leaf plan (`PL-`) and its
own ledger (`LG-`) inside it.

**Opens, and is disclosed rather than fixed here:**

- Between this commit and W37-9, `CLAUDE.md` lines 27 and 107 state a permanence rule the
  repository has just broken (G2). The map plan already assigns both sites to W37-9; this is a
  known interval, not an oversight.
- Between this commit and W37-7, `git-hygiene` teaches a branch and PR-title grammar naming work
  keys that no longer exist after the roadmap restructure. §6.3 explains why it is excluded from
  this commit, and what follows.

### 4.7 What the go-ahead does not cover

NT-0019 §7's items (i), (j) and (k) belong to later slices — (i) to the Work's closure record,
(j) and (k) to W37-11. **Accepting this run is not accepting the Work close**, which is a
separate dated line under `CLAUDE.md` §12.

---

## 5. The measured baseline

Two pins, both shown, because they disagree and the disagreement is the point: the sweep's
`89dd2b1` is nine commits behind `origin/main` at filing.

### 5.1 Repository-wide

| Figure | `89dd2b1` (sweep) | `39ee30c` (filing) |
|---|---|---|
| Tracked files | 1355 | **1447** |
| Files matching NT-0019 §7 (d)'s legacy-form pattern | 876 | **930** (20 507 lines) |
| Files with a requirement-family citation, with `VR-` | 770 | **776** |
| ...without `VR-` | — | **771** |
| Distinct requirement-family ids | 710 | **710** |
| `@pytest.mark.req` markers | 1988 | **1988** |
| `ADR-0<nnn>` — files / occurrences | — | **164 / 445** |
| `backend/src/app/` | 88 | **88** |
| `backend/tests/` | 93 | **93** |
| `backend/migrations/` | 28 | **28** |
| `packages/pricing-core/` | 70 | **70** |
| `packages/model-schema/` | 57 | **57** |
| `frontend/src/` | 142 | **142** |
| `frontend/` (whole) | 144 | **144** |
| `examples/` + `deploy/` + `packages/README.md` | 9 | **6 + 2 + 1 = 9** |
| `scripts/` | 16 | **13** |
| `docs/` | — | **246** |
| `.claude/` | — | **18** |

| Population | `89dd2b1` (sweep) | `39ee30c` (filing) |
|---|---|---|
| `docs/specs/*.md` | 8 | **8** |
| `docs/workflows/wf-*.md` | 5 | **5** |
| `docs/adr/*.md` (incl. README) | 6 + README | **7** |
| `docs/notes/` numbered notes | 19 | **19** |
| `docs/plans/2026-*.md` | 126 | **130** |
| ...ledgers / maps / review / verified / handover / leaf | — | **16 / 3 / 1 / 1 / 1 / 108** |
| `docs/research/*.md` | 11 | **11** |
| `docs/audit/findings/F*.md` | 5 | **11** |
| `docs/audit/work/*/README.md` | 15 | **15** |
| `.claude/roles/` | 7 | **7** |
| `.claude/agents/` (incl. README) | 8 | **8** |
| `.claude/skills/*/SKILL.md` | 46 | **46** |
| `.claude/notes/` stubs | 19 | **19** |
| `docs/_templates/` | 13 | **13** |
| `.github/workflows/` | 3 | **3** |

### 5.2 `docs/audit/` — the tree being dissolved, enumerated

**43 files** at `39ee30c`. NT-0019 §5.2's rows account for **41** of them. The two with no
destination row are named here rather than left to the executor to discover:

| Group | Count | §5.2 destination |
|---|---|---|
| `findings/F*.md` + `findings/README.md` | 12 | `docs/findings/FD-…`; README rewritten |
| `work/*/README.md` | 15 | `docs/closures/CR-…`, `kind: work` |
| `register.md`, `phases/1b/register.md`, `phases/1b/README.md` | 3 | one `docs/findings/register.md`; the phase register merges in with `phase: P1b`; the phase README becomes a `CR- kind: phase` |
| `closure-records.md`, `plan-reviews.md` | 2 | split into `CR-` files (`work`, `review`); preambles to `closures/README.md` |
| `checklists/*.md` | 2 | `docs/process/checklists/` |
| `retrofit-impossible.md`, `security-posture.md` | 2 | `docs/process/` |
| `file-census.md`, `file-census-5ef559d.csv`, `file-taxonomy-draft.md` | 3 | `docs/research/RS-…` |
| `exit-demo-uat.md` | 1 | `docs/closures/CR-…`, `kind: phase` |
| `README.md` | 1 | deleted; content to the `findings/` and `closures/` READMEs |
| **`nt-0019-verification-and-impact-sweep.md`** | 1 | **No §5.2 row.** It is a bespoke audit record: §5.4's bespoke-audit rule makes it `RS- kind: audit`, owner auditor |
| **`work/nt-0010-0011-adoption/pilot-findings.md`** | 1 | **No §5.2 row.** §5.2's row names `work/*/README.md` only, and this is not a README |

### 5.3 What the sweep changed relative to the map plan's table

The map plan's evidence table sized the slices; the sweep enumerated the rows and corrected
them. Four corrections change this task list:

| Row | Map plan / NT-0019 §5.6 | Sweep at `89dd2b1`, re-confirmed at `39ee30c` | Effect |
|---|---|---|---|
| `backend/src/app/` | ≈200 | **88** | The two largest rows each independently claimed roughly the *combined* backend total |
| `backend/tests/` | ≈210 | **93** | Real combined backend population ≈209-210, not ≈410 — a task list built from the note's figures would be sized wrong by more than 2× |
| `backend/migrations/versions/` | 3 | **28** | Undercounted ~9×; the citations were inspected by hand, not assumed noise. A real task, not a rounding error |
| `packages/pricing-core/` `ADR-1 (91)` | 91 occurrences of `ADR-1` | **49** padded, **0** bare, in that package | Two independent errors: the table described the post-migration convention as if it were today's, and "91" was the whole-tree total for the padded form, misattributed to one package. Repo-wide at `39ee30c` the padded form is **445** occurrences over **164** files |

Two rows the sweep left **deliberately unreconciled**, which this plan also declines to fit:
NT-0019 §5.5's *"fourteen scripts"* (no reading — 17 raw, 19 named, 16 citation-bearing —
equals 14; 13 citation-bearing at `39ee30c`) and §5.8's *"two CI workflows"* (three exist, one
changes). Both are counted from the tree in §7, never from the note's summary line.

### 5.4 Acceptance item (f)'s baseline — re-derived, not inherited

NT-0019 §7 (f) reads *"`git grep -c 'VR-DST-1'` is unchanged from `8f5d57d`"*. The map plan's
acceptance item 6 names a different baseline, `89dd2b1`. **Neither is usable, because the figure
is not stable across ordinary repository activity:**

| Pin | `git grep -c 'VR-DST-1' <sha>` summed | Files |
|---|---|---|
| `8f5d57d` — NT-0019 §7 (f)'s baseline | 104 | 25 |
| `89dd2b1` — map plan item 6's baseline | 107 | 26 |
| `39ee30c` — `origin/main` at filing | 109 | 28 |

The drift is ordinary prose: new plans, `document-ids.md` and NT-0019 itself all mention
`VR-DST-1`. **Pinning acceptance (f) to either named SHA guarantees a false red.** The
executable form, which supplies what the item lacks without lowering the bar (G3):

> **(f), executable:** record `git grep -c 'VR-DST-1'`, summed, at **this run's own
> merge-base**, before the run; re-derive it at the merge tree; the two must be equal.

Two properties of the command, recorded so a later reader does not mistake the figure for what
its name suggests:

- `git grep -c` counts **matching lines**, not occurrences. At `39ee30c` the line count is
  **109** and the exact-token count (`git grep -ohE 'VR-DST-1\b' 39ee30c | wc -l`) is **112**:
  three lines carry the token twice.
- `'VR-DST-1'` is an **unanchored substring** and would also match `VR-DST-10` to `VR-DST-19`.
  No such identifier exists at `39ee30c` (`git grep -ohE 'VR-DST-1[0-9]' 39ee30c` returns
  nothing), so the figure is uncontaminated today — but the item is a **stability invariant**,
  not a count of `VR-DST-1`, and must be run **identically** at both ends. Anchoring it at the
  second run only would break it.

### 5.5 Commands

Every figure above is reproducible at the named revision. `R` is
`\b(FR|NFR|OQ|DEP|VR)-[A-Z]+-[0-9]+\b`; `SWEEP` is NT-0019 §7 (d)'s own alternation.

| Figure | Command |
|---|---|
| Tracked files | `git ls-tree -r --name-only 39ee30c \| wc -l` |
| Legacy-form files / lines | `git grep -lE "$SWEEP" 39ee30c \| wc -l` · `git grep -cE "$SWEEP" 39ee30c \| awk -F: '{s+=$NF} END {print s}'` |
| ...by tree | the `-l` form, `\| sed 's/^39ee30c://' \| awk -F/ '{print $1}' \| sort \| uniq -c \| sort -rn` |
| Citation-bearing files, per path | `git grep -lE "$R" 39ee30c -- <path> \| wc -l` |
| Distinct ids | `git grep -ohE "$R" 39ee30c \| sort -u \| wc -l` |
| Markers | `git grep -c 'pytest.mark.req' 39ee30c -- backend packages \| awk -F: '{s+=$NF} END {print s}'` |
| Padded ADR form | `git grep -lE 'ADR-0[0-9]{3}' 39ee30c \| wc -l` · same with `-ohE … \| wc -l` |
| Ruling headings to split | `git grep -c -E '^#+ Ruling [0-9]+' 39ee30c -- docs/plans` |
| Header-gaining `.md` under `docs/` | `find docs -name '*.md' -type f \| wc -l` less the 13 templates |
| Non-`SKILL.md` markdown under `.claude/skills/` | `find .claude/skills -name '*.md' ! -name 'SKILL.md' \| wc -l` |
| (f)'s baseline | `git grep -c 'VR-DST-1' <merge-base> \| awk -F: '{s+=$NF} END {print s}'` |

---

## 6. Ruling 66's derivation — the instrument set

Ruling 66 rules DP-1 as option (a) and makes the set a **criterion**:

> **every instrument whose output is checked by checks 30-39 from the migration commit lands in
> W37-6.**

It obliges this plan to derive the set by walking checks 30-39 and asking of each: **which
instrument tells an author how to produce the thing this check tests?**, recording the derived
list with the check each entry answers to. The seven skills the map plan names are **the floor,
not the ceiling**. *"A list of exemplars invites fixing the exemplars and stranding the rest; a
criterion does not."*

The walk below is made **against the merged code at `39ee30c`** — `scripts/audit-docs.py`,
checks 30-39 merged as PR #573 — not against a description of it.

### 6.1 The walk

| Check | What it tests | Does it put an instrument in scope? |
|---|---|---|
| **30** Header present and parseable; no unknown field; required fields per family read from `docs/_templates/` | The YAML front-matter block of every produced document | **Yes** — every instrument that mints a document of a family. The field policy itself is read from `docs/_templates/` (Ruling 70), already migrated in W37-1, so the templates are not an enlargement |
| **31** Header `id` prefix and integer equal the filename's; directory equals family; numbers unique and contiguous; `created` non-decreasing | The filename, the directory and the allocated number a creating instrument tells an author to use | **Yes** — the same set. This is the check that fires on a document filed at the retired `YYYY-MM-DD-<slug>.md` path form |
| **32** Every `<PREFIX>-<n>` in prose resolves in `docs/INDEX.md`; prefix matches the number's family; no padded id outside a link target | Citations written into a produced document | **No new member.** The citation convention is NT-0019 §1.7, carried by `docs/process/document-ids.md`, already migrated. A creating skill holding a stale citation is caught by §4 step 6's mechanical rewrite, which exempts nothing |
| **33** `supersedes`/`superseded_by` symmetric; `status:` in the standard's vocabulary and the family's own subset; `work:`/`slice:` resolve; the map-plan roll-up raise surfaced | The status word, the supersession link and the placement fields a creating instrument tells an author to write | **Yes** — the same set. The roll-up half is `doc-index.py`'s and is already in this commit |
| **34** A frozen family's diff against its merge-base touches only `status:` (forward only), `superseded_by:`, appended `corrected_by:`, or (ledgers) appended `plans:` | An **edit** to an already-filed document | **Yes**, and it is the check that most sharply names `adr-write` (whose whole subject is the addendum-versus-edit rule) and `subagent-driven-development` (the ledger append is the only permitted mutation of an `LG-`) |
| **35** `owner:` is a role filename under `.claude/roles/` or `maintainer`, and one the directory's `README.md` permits where that README declares a list | The `owner:` value a creating instrument tells an author to write; and a directory README's permitted-owner list | **Yes** for the creating instruments. The second clause is **inert corpus-wide**: `grep -rn "Permitted owners" docs/ .claude/` returns **zero** at `39ee30c`, so `readme_owner_allowlist` returns `None` everywhere and the clause enforces on no directory. §7.4 |
| **36** Every `was:` has a `REDIRECTS.csv` row; every row's target exists; no pre-migration id or path form survives outside `REDIRECTS.csv` and `was:` lines | **Every byte of every tracked file** | **No new member — and this is the decisive line of the derivation.** Check 36 reaches every file, but §4 step 6 rewrites citations across the whole tree (`git ls-files`, nothing exempt), so every instrument's *citations* land in this commit **by construction**. What no rewrite can supply is the **instruction content**, and that is what checks 30, 31, 33, 34, 35 and 37 test |
| **37** A document carries every `##` section its family's template body declares | The body shape a creating instrument tells an author to write | **Yes** — the same set. `required_sections()` derives them from each family's template, so an instrument teaching a stale section list produces a document check 37 reds |
| **38** Loop signal | **Nothing.** `check_loop_signal` *"never fails the gate, only notes"*; its body appends a note and returns | **No.** An instrument whose output is touched only by check 38 cannot cause a failure, and admitting one would fail Ruling 66's own acceptance item 2 |
| **39** `docs/INDEX.md` byte-stable against a fresh regeneration; **a merged PR's title names its `SL-`** and the slice's ledger records the PR | The index (generated by `doc-index.py`, already in this commit) and the PR-title/ledger pair | **No new member.** The byte-stability clause has no authoring instrument. The PR-title clause is **explicitly not checked**: `check_index_stable`'s body appends the note *"PR-title/ledger cross-reference needs GitHub PR context this tree-snapshot tool does not have … not checked here"*. §6.3 |

### 6.2 The derived set — adopted

Each row names the check that puts it there. Where a member's ground is not a check, the row
says so rather than borrowing one.

**Thirteen members.** The seven the map plan names, plus six the criterion adds. Each row names
the check that puts it there and the passage that makes it an instrument — read at `39ee30c`,
never inferred from the skill's name.

| # | Instrument | Family it mints | Checks | What it teaches that a check will judge |
|---|---|---|---|---|
| 1 | `.claude/skills/writing-plans/` | `PL-` (`map`, `leaf`, `review`, `handover`) | 30, 31, 33, 34, 37 | ``Save plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md` `` (line 18) — the retired filename grammar, plus the header template and the section shape |
| 2 | `.claude/skills/subagent-driven-development/` (+ `scripts/task-brief`) | `LG-` | 30, 31, 33, **34** | The ledger append is the only permitted mutation of an `LG-`, which is check 34's own allowance; its hard-coded paths move with it |
| 3 | `.claude/skills/close-workstream/` | `CR- kind: work`; files `FD-`; sets `LG-`/`SL-` `closed` | 30, 31, 33, 37 | ``### W<n> — <name>: closed <YYYY-MM-DD>`` (line 542) — the closure-record heading grammar. Also carries the bespoke-audit rule (§5.4): a bespoke audit's record is `RS- kind: audit`, owner auditor, every finding an `FD-` |
| 4 | `.claude/skills/phase-review/` | `CR- kind: review` | 30, 31, 33, 37 | ``lands in `docs/audit/plan-reviews.md` as a dated `### Plan review N` section`` (line 22) — a path into the dissolving tree **and** a heading grammar |
| 5 | `.claude/skills/adr-write/` | `ADR-` | 30, 31, **34**, 37 | ``File as `docs/adr/NNNN-kebab-title.md` `` (line 16) — the retired directory and padding; and the addendum-versus-edit rule, which is check 34's subject exactly |
| 6 | `.claude/skills/spec-change/` | `FR-`/`NFR-`/`DEP-`/`OQ-` rows; `WF-` amendments | 30, 31, 33 | *"Requirement IDs are append-only. Never renumber."* (line 20) — the rule D2 overrides, still stated as binding |
| 7 | `.claude/skills/library-spike/` | `RS- kind: spike` | 30, 31, 33 | ``Write it up in `docs/research/` `` (line 86); §5.4's **H** row makes it *"writes `RS- kind: spike` via `doc-id.py next`"* |
| 8 | `.claude/roles/planner.md` | `PL-`; **`CR- kind: review`** | 30, 31, 37 | ``filed to `docs/audit/plan-reviews.md` as a dated `### Plan review N` section`` (line 22) — the charter files the §14 review itself, at a path this commit deletes, in a heading form no template declares |
| 9 | `.claude/roles/auditor.md` | `CR- kind: work`/`phase`; `FD-`; `RS- kind: audit` | 30, 31 | Four filing paths into the dissolving tree in one bullet (lines 16-25): ``Closure records at `docs/audit/work/<id>/README.md` ``, ``register deferral rows … at `docs/audit/register.md` ``, ``checked against `docs/audit/checklists/…` ``, ``Evidence essays live at `docs/audit/findings/<F-id>.md` `` |
| 10 | `.claude/roles/decision-maker.md` | **`RL-`**; records `OQ-` | 30, 31 | *"recorded as dated sibling records"* (line 7, the `Owns` bullet) — **the only filing instruction for `RL-` anywhere.** No skill mints a ruling record; its three mandatory skills are `spec-change`, `git-hygiene` and `adr-write`, none of which covers `RL-`; and nothing routes the role to `docs/_templates/RL.md`. After this commit a ruling is `docs/rulings/RL-<nnnnn>-<slug>.md` with a header, and *"dated sibling record"* produces a headerless file in the wrong directory |
| 11 | `.claude/skills/writing-skills/` | Reference — `SKILL.md` | **30**, 35 | *"Two required fields: `name` and `description`"* (line 75). After the flip, check 30 reads every `SKILL.md`'s front matter and rejects an **unknown field** — see §7.1's second finding. This is the instrument that declares that front matter |
| 12 | `.claude/skills/brainstorming/` | — (writes under `docs/`) | 30, 31 | ``save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` `` (lines 100, 206). That is a path **under `docs/`**, so anything written there is in check 30's scope after the flip. §5.4's one-sentence edit — *scratch is not a document; the committed record is `PL-`/`LG-`* — is what removes it |
| 13 | `.claude/skills/README.md` | — (the index) | **None — adopted on `CLAUDE.md` §12** | Ruling 66 named it as a candidate the derivation must dispose of. **Adopted, and the ground is stated honestly: no check in 30-39 reaches it.** `CLAUDE.md` §12 requires the index to move with the skills (*"update the README, commit both with the work"*), and nine skills change in this commit; §5.4 gives it a *"creates"* column per creating skill. Leaving it behind puts `CLAUDE.md` §12 in violation **inside this commit itself** |

**On the charters — the criterion was applied to all seven, and it separates them.** Three are
adopted because they carry a **filing instruction of their own**, verified by reading the whole
file rather than trusting a summary: `planner.md` and `auditor.md` name paths into the dissolving
`docs/audit/` tree, and `decision-maker.md` names the only `RL-` filing rule that exists
anywhere. Four are excluded because they **defer**: `executor.md` routes every form to
`git-hygiene`, `subagent-driven-development` and `executing-plans`; `lead.md`'s only branch or PR
reference is a pointer to `git-hygiene`; and `reporter.md` and `watcher.md` own no governed
document, which NT-0019 §1.6 states outright (*"the generated ownership matrix shows two
deliberately empty rows rather than two gaps"*). Every charter's **M** row — the mechanical
citation rewrite — lands in this commit regardless, by §4 step 6; what members 8, 9 and 10 move
is **H** content.

**Member 10 deserves its own sentence, because a first reading gets it backwards.**
`decision-maker.md` teaches no filename, no id form and no directory — and that is precisely why
it is a member. An instrument that teaches a *wrong* form fails loudly at the first document; an
instrument that is *silent* routes the author nowhere, and after this commit the author files a
dated sibling of a plan with no header at all, which checks 30 and 31 both red. `docs/_templates/RL.md`
carries the correct instruction and is already migrated — so the fix is a routing line, not a
rewrite, and it costs one sentence.

**The dependency members 3 and 9 create, stated so it is not discovered late.** If
`close-workstream` as edited carries the `FD-` **essay's** header and shape as well as the
register row's, `auditor.md`'s adoption is belt-and-braces; if it does not, `auditor.md` is
carrying that instruction alone. Either way both are in this commit, so the risk is closed —
but §7.12 checks which of the two ends up holding it, because W37-7 must not later remove it
from one on the assumption that the other has it.

### 6.3 Explicitly excluded, with reasons

Ruling 66 requires its two named candidates to be *"adopted or excluded with a reason, not left
unmentioned"*. Both are disposed of here, together with four the walk raised.

| Candidate | Verdict | Reason |
|---|---|---|
| **`git-hygiene`** — Ruling 66's named candidate, on *"check 39's branch and PR-title grammar"* | **Excluded from the enlargement; its H row stays in W37-7** | Check 39's PR-title clause is **not implemented as a check**. `check_index_stable`'s body appends a note saying the clause *"needs GitHub PR context this tree-snapshot tool does not have … not checked here"*, and check 38 is warn-only, so **no check in 30-39 can red on a branch name or a PR title.** Under the criterion as ruled — *whose output is **checked** by checks 30-39* — `git-hygiene` is not a member, and its taught output (a branch name, a PR title) is not a document at all. **The consequence, disclosed not hidden:** between this commit and W37-7 there is no valid instruction for naming a branch or a PR title, because the work keys the current grammar names (`w37-7-…`) no longer exist after the roadmap restructure. That is not gate-detectable; it argues for running W37-7 immediately after this slice with `git-hygiene` first in its order — **a sequencing recommendation for the lead, not a decision this plan makes.** Note this exclusion does **not** rest on Ruling 66's acceptance item 2, which §10 finding 12 shows cannot discriminate here |
| **`.claude/skills/README.md`** — Ruling 66's other named candidate | **Adopted** | §6.2 member 13. Adopted on `CLAUDE.md` §12, explicitly **not** on a check-30-39 ground |
| `dev-commands` | **Excluded; stays in W37-7** | A command reference; no document is created by following it. The enumeration confirms its `docs/` mentions are citations of existing paths, not a taught grammar, and that it does not mention `doc-id.py` or `doc-index.py` at all — so a stale `dev-commands` cannot misdirect an author toward a retired form. It is silent, not wrong |
| `docs-audit` | **Excluded; stays in W37-7** | A **reading** instrument: it describes what the checks verify; it does not tell an author how to produce a document. It teaches the `NT-NNNN` id form and the `YYYY-MM-DD-` grammar, but as description of the corpus, not as instruction for filing. Half the bespoke-audit rule belongs to it and half to `close-workstream`; the `close-workstream` half is in this commit, where the rule is *authored* |
| `repo-architecture` | **Excluded; stays in W37-7** | Teaches an id form (``notes/ maintainer notes, `NT-NNNN` ``) inside an annotated tree that **describes** the repository. Nobody files a document by following it. §5.4's row replaces the tree with §1.4's |
| `executing-plans` | **Excluded; stays in W37-7** | Its one repo-adapted line names the **directory** `docs/plans/`, which does not change. The filename form is `writing-plans`'s, and that is a member |
| `planning-with-files` | **Excluded; stays in W37-7** — and this **splits §5.4's row**, deliberately | It teaches `.planning/YYYY-MM-DD-<slug>/`, which is scratch and outside the standard by §1.12 and G10, so no check reaches it. Its row-mate `brainstorming` teaches a path **under `docs/`** and is member 12. The row is split because the criterion reaches one half and not the other; W37-7 applies the remaining sentence |
| `.claude/agents/README.md` | **Excluded; stays in W37-8** | An **index** (category E), not an authoring instruction — the enumeration found no id, filename or header grammar in it. Agent files are stamped wholesale by §4 step 5, so this commit gives all seven their headers; a *new* agent created before W37-8 would red check 30, but an agent is not created **by construction** during W37-7, which is the whole basis of Ruling 66's window argument. Caught loudly at its own PR is the correct behaviour, not the DP-1 failure mode |
| `.github/PULL_REQUEST_TEMPLATE.md` | **Excluded; stays in W37-9** | Same ground as `git-hygiene`: it shapes a PR body, which no check in 30-39 reads |
| `CLAUDE.md` | **Excluded; stays in W37-9** | G2 assigns its two permanence sites to W37-9, and no check in 30-39 reads it. §4.6 discloses the interval |
| `docs/_templates/` (13 files) and `docs/process/document-ids.md` | **Not an enlargement — already in scope** | `_ID_SCOPE_ROOTS`'s two members today, migrated in W37-1, and they already teach the post-migration forms (`docs/rulings/RL-<nnnnn>-<slug>.md` and so on). Checks 30 and 37 read the templates as a **policy and shape source** (Ruling 70), never as documents to validate. **Two corrections they nevertheless need land here** — §7.1 and §7.4 — because this commit is what consumes them, not because DP-1 moved them |

### 6.4 How the derivation was closed

The walk in §6.1 was made against the merged check bodies. It was then cross-checked against an
**exhaustive enumeration** of `.claude/skills/**`, `.claude/agents/**`, `.claude/roles/**`,
`docs/_templates/**`, `docs/process/**`, `.github/**`, `CLAUDE.md` and `.claude/CLAUDE.md` — five
`grep -rn` sweeps (an id literal `[A-Z]{2,}-[0-9]{3,4}`; a governed-document path; a
header/filename grammar; a branch or PR-title grammar; a front-matter key), plus a full read of
every file whose name suggests it creates a document, **regardless of grep hits**, because a
skill can teach a form by example without matching a regex. **34 files qualified**, classified as
(A) an id form, (B) a filename or path convention, (C) a header field set, (D) a branch or
PR-title grammar, or (E) an index that must move with what it indexes. The negative list — files
opened and rejected with a reason each — is what makes the enumeration exhaustive rather than a
sample, and it is what excluded 40-odd skills the walk would otherwise have had to argue about
one at a time.

**The enumeration changed the answer, which is why it was worth running.** It added members 8,
9, 11 and 12, which the walk alone had missed: the walk asked *which instrument mints this
family* and got the skills; the enumeration asked *which file contains a form* and got the
charters as well. It also **contradicted** a provisional reading of `decision-maker.md` — a
first pass excluded it on the ground that it "defers to `spec-change`/`adr-write`/`git-hygiene`",
which the enumeration reported and which is literally true. Reading the whole charter showed the
deferral is the defect: none of those three covers `RL-`, so the deferral routes nowhere.
Member 10's note records both readings and why the second wins.

**An instrument in neither §6.2 nor §6.3 is a finding against this plan.** The executor adds it
under the same criterion rather than filing a document and correcting it afterwards — Ruling 66
acceptance item 1's rule that hand-correcting the *document* rather than the *instrument* is the
same failure repeating.

### 6.5 The enumeration's result, in one table

The 34 qualifying files account for themselves exactly, **11 + 15 + 8**:

- **11** are §6.2 members — `writing-plans`, `close-workstream`, `phase-review`, `adr-write`,
  `spec-change`, `library-spike`, `writing-skills`, `brainstorming`, `.claude/skills/README.md`,
  `.claude/roles/planner.md`, `.claude/roles/auditor.md`.
- **15** are already in this commit for another reason: all 13 `docs/_templates/` files and
  `docs/process/document-ids.md` (the two `_ID_SCOPE_ROOTS` members, migrated in W37-1) and
  `docs/process/delivery-process.md` (§7.8's **H** row).
- **8** are §6.3 exclusions with a named later slice: `git-hygiene`, `docs-audit`,
  `repo-architecture`, `executing-plans`, `planning-with-files`, `.claude/agents/README.md`,
  `.github/PULL_REQUEST_TEMPLATE.md`, `CLAUDE.md`.

**The enumeration alone would have missed two members, which is why both methods were run.**
`subagent-driven-development` and `.claude/roles/decision-maker.md` are §6.2 members 2 and 10 and
neither appears in the 34: the enumeration rejected the first because its `docs/plans/` mentions
are incidental filenames inside a worked-example transcript, and the second because it teaches no
form of its own. The check-walk reaches both — the first because check 34's only permitted
mutation of an `LG-` is the append this skill performs, the second for the reason member 10's row
gives. Conversely the walk alone would have missed members 8, 9, 11 and 12. **Neither method is
sufficient; the set is the union, and a future re-derivation that runs only one of them will come
out short.** §6.3 additionally disposes of `dev-commands`, which the enumeration rejected and the
walk raised.

The rejected files that most deserve naming, because a later reader will wonder: every
`vue-*` skill, `ui-ux-pro-max`, `systematic-debugging` and `testing-strategy` carry **no**
document-id or filename grammar at all; `contract-schema` teaches an artifact-reference grammar
(`{type}:{slug}@{version}`) that `document-ids.md` §1.1 rule 4 **excludes from the standard by
name**; `watcher-runtime-state` and `reporter-cycle` govern runtime state that §1.12 excludes as
scratch; and `python-test`, `python-package`, `fastapi-service` and `vue-frontend` **cite**
existing requirement and ADR ids as worked examples but never mint one. All four classes are
**M** rows: the mechanical rewrite reaches them, and nothing else must.

---

## 7. The task list

Derived from the auditor's sweep (§5) and NT-0019 §5's **H** rows scoped to stage S2 — not from
the map plan's evidence table.

### 7.1 Task 1 — Fix `_id_scope_documents` before flipping `_ID_SCOPE_ROOTS`

**Files:** `scripts/audit-docs.py`, `tests/test_audit_docs_ids.py`.

**The flip is not "one constant and one visible line", and establishing that before anything
moves is the point of putting this first.** PR #573's own commit message says *"The scope widens
in W37-6's diff, which is one constant and one visible line, per the plan."* Measured at
`39ee30c`, it cannot be:

- `_id_scope_documents` handles a root that is either a **file** (appended) or a **directory**
  (`rglob("*.md")`). It can express neither a glob nor an exclusion.
- NT-0019 §4 step 5 stamps `docs/**`, `.claude/roles/**`, **`.claude/skills/*/SKILL.md`** and
  `.claude/agents/**`. The third is a glob, and it is the one that matters:
  `find .claude/skills -name '*.md' ! -name 'SKILL.md' | wc -l` returns **237** at `39ee30c`
  — 236 inside skill directories plus `.claude/skills/README.md` — spread over **20**
  directories, `vue-debug-guides` alone holding 139.
- Adding `.claude/skills` as a **directory** root therefore makes check 30 demand a header on
  237 files step 5 does not stamp and Ruling 69 §3 explicitly exempts from the blanket pass. The
  result is 237 immediate failures, and the tempting fix — exempting them — is how the vendored
  exemption grows into a hole.

**Do:**
- [ ] Extend `_id_scope_documents` to accept a **glob root** alongside a file and a directory, so
      `_ID_SCOPE_ROOTS`'s post-flip value can be written as exactly §4 step 5's stamp set.
- [ ] Keep the `roots=None` late-binding contract intact. It exists so a test's runtime
      monkeypatch of `_ID_SCOPE_ROOTS` is visible to every no-argument caller; a default value
      bound at definition time would silently disable every broken-input proof in the family.
- [ ] Make the scope **print its own coverage** — files selected, per root. A check that has
      never seen a file cannot be enforcing anything (Ruling 70 acceptance item 3, which caught
      exactly this: a check 30 that parsed 0 of 13 templates and exited 0).
- [ ] Broken-input proof: point one root at a path selecting zero files; the audit must **fail
      loudly**, not report a smaller plausible number.

*Violation: `audit-docs.py` green while any root's selected-file count is zero; or check 30
firing on a file NT-0019 §4 step 5 does not stamp.*

**The second finding in this task, and it reds 53 files rather than 237.** Check 30 rejects an
**unknown field**, with the permitted set derived from the family's template. Every governed file
under `.claude/` that §4 step 5 stamps **already has YAML front matter of its own**, and none of
its keys is in `docs/_templates/REFERENCE.md`'s declared set (`family`, `title`, `status`,
`created`, `owner`, `tree`, `corrected_by`, `relates`, plus `vendored:`/`origin:`):

- all **46** `.claude/skills/*/SKILL.md` carry `name:` and `description:`, and a handful
  additionally carry `allowed-tools:`, `license:`, `metadata:` or `version:`;
- all **7** `.claude/agents/*.md` carry `name:`, `description:`, `tools:` and `model:`.

A stamp cannot prepend a second `---` block — `_docid.parse_header` reads `lines[0] == "---"` and
then to the closing `---`, so there is exactly one block per file — which means the migration
must **merge** its fields into the existing front matter, and check 30 then sees `name` and
`description` as unknown fields on 53 files.

- [ ] Declare the skill and agent keys in `docs/_templates/REFERENCE.md`'s front matter, marked
      conditional in the template's own comment. Ruling 70 makes the template the licensing
      instrument — *"the permitted set for a family is the set of keys in that family's template
      front matter"* — so this is the sanctioned route and not a widening of NT-0019 §1.5's
      closed set. **Nothing in §1 is edited.**
- [ ] Prove it the way Ruling 70 acceptance item 2 specifies: add a key to the template and a
      header using it becomes permitted; remove it and the same header reds. *Violation: check
      30's verdict is unchanged by editing the template* — the signature of a policy transcribed
      into the checker instead of read from the declaration.
- [ ] Confirm the merge preserves key order and the existing values byte-for-byte: a
      `SKILL.md`'s `name:` must still equal its folder name, which `.claude/skills/README.md`
      requires.

### 7.2 Task 2 — The scan-roots guard, and the five path dependencies behind it

**Files:** `scripts/audit-docs.py`, `tests/test_audit_docs_scan_roots.py`.

**The guard will fire, and that is the guard working.**
`tests/test_audit_docs_scan_roots.py` asserts the **literal source string**
`NOTES = REPO / "docs" / "notes"` is present in `audit-docs.py`, with the message *"the NOTES
constant has moved -- re-derive this test before trusting it"*. This migration moves
`docs/notes/` to `docs/rfcs/` and dissolves `docs/audit/`. The test trips on the constant's
**text**, and it is telling the truth.

**The fix is to re-point the roots and re-derive the test against the moved ones — never to
loosen the assertion** — and the re-run must happen **after** the move, on the test's own stated
principle that *"a green audit after a directory move proves nothing on its own."*

**The map plan calls `check_finding_citations`'s `scan_dirs` "the second root". Read at
`39ee30c`, that check has five path dependencies, four of them on the dissolving tree:**

| # | Site | Line at `39ee30c` | If the path vanishes |
|---|---|---|---|
| 1 | `NOTES = REPO / "docs" / "notes"` | 121 | Caught by the literal-string test, and by site 5 |
| 2 | `register_file = ROOT / "audit" / "register.md"`, guarded by `.is_file()` | 599-601 | **Silently contributes nothing** to `registered` |
| 3 | `(ROOT / "audit" / "phases").glob("*/register.md")` | 602 | **Silently contributes nothing** |
| 4 | `(ROOT / "audit" / "work").glob("*/README.md")` and `ROOT / "audit" / "closure-records.md"`, the latter guarded by `.is_file()` | 611-614 | **Silently contributes nothing** |
| 5 | `scan_dirs = [ROOT / "research", ROOT / "plans", NOTES]` | 618 | `fail()`s loudly — a prior fix, and the only one of the five that does |

Sites 2 to 4 degrade to an empty `registered` set. The **net** effect of losing all of them is
loud, because every finding citation in `docs/plans/` then resolves nowhere — but a **partial**
re-point (site 2 fixed, sites 3 and 4 left pointing at dissolved paths) reds only the citations
to the ids those two sources carried, which reads as a handful of unrelated failures rather than
as a missing root.

**Do:**
- [ ] Re-point all five: `docs/rfcs/` for `NOTES`; `docs/findings/register.md` for site 2; site
      3 may become unnecessary because §5.2 merges the phase register into one
      `findings/register.md` with `phase: P1b` — **prove it is unnecessary, do not assume it**;
      `docs/closures/` for the work READMEs and the split `closure-records.md`; and `scan_dirs`
      widened to where citations are now *made*: `docs/research/`, `docs/plans/`, `docs/rfcs/`,
      `docs/rulings/`, `docs/ledgers/`.
- [ ] Re-derive `tests/test_audit_docs_scan_roots.py` against the moved constant text.
- [ ] Give **each of the five** a mutation proof: repoint it at a non-existent path and the
      audit must exit non-zero naming that path.
- [ ] Re-run **after** the move, not before.

*Violation: the literal assertion replaced by a substring, a regex or an existence probe; or any
of the five re-pointed without a mutation proof that reds.*

### 7.3 Task 3 — `audit-docs.py`'s parsers, regexes and pins

**Files:** `scripts/audit-docs.py`, `tests/test_audit_docs_*.py`. Per NT-0019 §5.5's
`audit-docs.py` row, each item verified against the shipped source rather than the row's summary:

- [ ] Check 16 to a front-matter parser — the notes' prose header no longer exists.
- [ ] `_FINDING_ID` to the `FD-` form.
- [ ] Requirement-id regexes to the global form; **check 19's two hard-coded `ADR-(\d{4})`
      sites** (lines 410 and 2289 at `39ee30c`) and the `ADR id` pattern at line 1910.
- [ ] Per-module numbering check to global uniqueness; the *"Next free"* exemption re-pointed at
      the global next.
- [ ] `check_notes_tombstone` is already renamed to `check_redirects` (slot 30 to 36, merged in
      #573); **this slice deletes the 19 `.claude/notes/` stubs it protected** (§4 step 4), which
      by NT-0019 §5.5's own resolution is where that check's protective job ends.
- [ ] The process-core digest re-pinned after §7.8's `delivery-process.md` changes.
- [ ] Check 28's plan-kind classification — §9.

### 7.4 Task 4 — Flip `_ID_SCOPE_ROOTS`, and record the two clauses that cannot fail

- [ ] Flip `_ID_SCOPE_ROOTS` to §4 step 5's stamp set, using Task 1's glob support.
- [ ] **Check 35's second clause is inert corpus-wide.** `grep -rn "Permitted owners" docs/
      .claude/` returns **zero** at `39ee30c`, so `readme_owner_allowlist` returns `None` for
      every README and the clause enforces on no directory. This slice **creates** four
      directory READMEs (`docs/closures/`, `docs/findings/`, `docs/rulings/`, `docs/ledgers/` —
      §5.2 lists them as new). Decide and record: either they carry a `Permitted owners:` line,
      and the clause becomes live for those four, or they do not, and it stays inert until
      W37-10 writes the `docs/` READMEs. **Do not leave it undecided** — an inert clause reading
      green is exactly the boundary metric NT-0007 warns about.
- [ ] **Six of the ten checks examine nothing at all today, and this commit is their first real
      run.** `python3 scripts/audit-docs.py` at `39ee30c` reports, verbatim: check 30 *"1 governed
      document(s) checked in scope"*; check 31 *"0 id(s) in scope, 0 distinct number(s)"*; check
      32 *"no docs/INDEX.md yet — citation and padding checks skipped"*; check 33 *"1 header(s)"*;
      check 34 *"0 frozen-family file(s) in scope"*; check 35 *"1 owner(s)"*; check 36 *"no
      docs/REDIRECTS.csv yet — the legacy-form sweep is a post-migration invariant and is
      skipped"*, *"0 legacy-form hit(s)"*; check 37 *"1 document(s)"*; check 38 warn-only; check
      39 *"nothing to check yet"*. **The whole family's corpus is one file** — `document-ids.md` —
      and checks 31, 32, 34, 36, 38 and 39 have never executed their main body against anything.
      Their broken-input proofs exercise them on fixtures, which is what W37-4 delivered; what has
      never happened is a run over a real corpus. Plan for that: the first execution of check 32's
      citation resolution and check 36's legacy sweep over ~1400 files happens **inside this PR**,
      and a large first-run failure list is the expected case, not a signal that something went
      wrong. Budget for it, and do not narrow a check to make the list shorter.
- [ ] **Check 38 is warn-only and check 39's PR clause is not checked.** Record both in the
      ledger as *known non-enforcing*, so a green run is not read as evidence they passed.
- [ ] **Correct `docs/_templates/REFERENCE.md`'s vendored-detection comment, which contradicts
      Ruling 69 in the words Ruling 69 rejected.** The template's closing comment block states:
      *"`doc-id.py`'s detection rule (`grep`-able: any directory holding a `LICENSE` that is not
      the repository's own) is what decides this, **not a hand-kept list**."* Ruling 69 rejected
      exactly that (*"Rejected: keying `is_vendored` on `LICENSE` presence, as published. It
      under-exempts 240 tracked files at `04ec6bf` and contradicts its own examples"*) and ruled
      the opposite mechanism: `_VENDORED_SKILLS`, **a declared constant seeded by hand** from
      `.claude/skills/README.md`, reconciled against the ruff exclude list as a second witness.
      The template landed in W37-1, before Ruling 69; Ruling 69 §3 obliges W37-2, W37-4 and
      W37-6 and does not name the template, which is how it survived. It is inside
      `_ID_SCOPE_ROOTS`, so it is governed and in this commit's reach. *Violation: the template
      still names `LICENSE` presence as the decider after this commit.*

### 7.5 Task 5 — Run `migrate`, and commit its output alone

- [ ] Record the merge-base SHA and acceptance (f)'s baseline **in the same command** that
      records §1's precondition checks (§5.4).
- [ ] Dry run first; its output reaches the ledger before anything moves. **PENDING W37-5**
      (§3.1) for the invocation.
- [ ] Run `migrate`; commit **the script's output alone** as the branch's first commit. This is
      not a required commit boundary — Ruling 68 settles what (g) *means*, not how many commits
      the branch has before it is squashed — but it is *"a cheap and mechanical way to compute
      the same diff"*, and it is the recommended shape.
- [ ] Compute (g) with the six-class filter. **PENDING W37-5** (§3.2) for the invocation; the
      obligations are fixed: implemented as code; no pass-through for an unclassifiable hunk;
      the frozen-family branch calls `audit_docs.frozen_diff_is_permitted`, which is already
      exported at module level for exactly this purpose, its docstring saying so.
- [ ] Prove idempotence on the real tree: a second `migrate` run produces zero diff.

**Three split rules that do not partition the tree as written, measured at `39ee30c`.** Each is
a place the script will silently do the wrong thing unless the executor fixes the rule first:

- §4 step 2 says *"Multi-ruling files → one per `## Ruling N`"*. There are **72** ruling headings
  across **29** files, of which **3 are `#` (h1), not `##`** —
  `2026-09-01-ruling-60-census-provenance-checkout-depth.md`,
  `2026-09-01-ruling-61-notes-tombstone-stubs-watched.md` and
  `2026-09-01-nt-0016-slice2-fr-data-32-ruling.md` (Rulings 60, 61 and 59). A splitter matching
  `^## Ruling` misses all three and files them as `PL-` in `docs/plans/`, which **no check
  catches** — the family and directory agree, so check 31 is satisfied by the wrong answer.
- **Two of the 29 are not named `*ruling*`** —
  `2026-08-29-w11-algorithm-pin-maturity.md` and `2026-08-29-w11-fr-rate-65-attribution.md`. A
  filename-keyed detector misses both.
- §4 step 2 says *"`closure-records.md` → one `CR-` per work heading"* and *"`plan-reviews.md` →
  one `CR-` per review"*. `closure-records.md` has **zero `##` headings**; its per-record
  headings are **21 `###`**, of which one is a phase (*"Phase 1a — exit demo accepted"*) and
  three are marked *"(in progress, not closed)"* — so a level-keyed splitter produces closure
  records for things that were never closed. `plan-reviews.md` has **14 `###`**, of which **11**
  are `### Plan review N`; the other three sit under a `## Pending proposals` section that is
  not a review and has no destination in §5.2.

- [ ] Fix each of the three rules before the run, and record the fixed rule in the ledger.

### 7.6 Task 6 — The remaining gate scripts

Counts taken from the tree, never from §5.5's *"fourteen scripts"* (§5.3).

- [ ] `register-lint.py`, `register-owed.py` — paths, `FD-` parser, `WK-`/`SL-` in the Work-item
      column, docstrings.
- [ ] `req-coverage.py` — spec regex to the global bold-id form; marker form; docstrings.
- [ ] `scope-audit.py` — requirement-id regex; docstrings.
- [ ] `file-census.py` — family table read from `document-ids.md`; id-match in `referenced_by`;
      output path moves to `docs/research/`; docstrings.
- [ ] `graphify-docs-extract.py` — front-matter parsing; requirement regex.
- [ ] `generate-contracts.py` — re-run after §7.9's `model-schema` rewrite; `docs/contracts/`
      regenerated and its drift check green.
- [ ] `doc-id.py`, `doc-index.py` — any path constant naming a pre-migration directory.
- [ ] The §5.5 **M** rows (docstring citations only): `revalidate-artifacts.py`, `demo.py`, the
      six `bench-*.py`, `hooks/retry_cap_hook.py`.

### 7.7 Task 7 — The tests §5.7 names

- [ ] Delete `test_audit_docs_notes_tombstone.py` and `test_notes_move_citations.py`; their job
      passes to `test_audit_docs_redirects.py`.
- [ ] Update the ten named test files' fixture ids and paths; re-pin the digest.
- [ ] **The tree-scanning invariant tests are in scope even though this slice adds no caller.** A
      file-adding and file-moving change puts every test that walks the tree in scope, and
      `--collect-only` is blind to all of them. Name them explicitly in the ledger and run them.

### 7.8 Task 8 — Process, roadmap, register and CI

- [ ] `docs/roadmap.md` — the §4 step 3 restructure: phase sections as milestones with
      `status`/`opened`/`target`/`gates`/exit criteria; each Work a `WK-` row with a fenced
      header; each slice an `SL-` row under it. The **H** part is the *"what a Work produces"*
      paragraph, which must name the families.
- [ ] `docs/process/delivery-process.md` §3 — the Project → Phase → Work → Slice vocabulary now
      names `P<n>`, `WK-`, `SL-`; what each layer produces names the families; §15's *"name the
      tree"* gains *"and the id"*.
- [ ] `docs/process/delivery-process.core.json` — path values, `WK`/`SL` vocabulary, regenerated
      digest. **The markdown is authoritative; the extract is derived** (`CLAUDE.md` §15), and
      the gate check that holds them together resolves each block's *citations*, not its
      content — which is how the extract once fell two commits behind its source with the gate
      green throughout. Regenerate it; never hand-edit it.
- [ ] `docs/findings/register.md` — header prose rewritten so the **row's** field set is declared
      in one place. **Ruling 70 obliges this on W37-6**, because a register row is not a
      header-bearing record and §1.5's template mechanism does not reach it; **Ruling 71 obliges
      the unowned-ownership shape in the same place.**
- [ ] `.github/workflows/docs.yml` — `paths:` gains `scripts/doc-id.py`, `scripts/doc-index.py`
      and `.claude/**`; the two new steps; the comment block replaced. The other two workflow
      files are unchanged; §5.8's *"two CI workflows"* is one of the sweep's two unreconciled
      figures and is not used as a count here.

### 7.9 Task 9 — The code rewrite, sized from the sweep

Every figure is the sweep's, re-confirmed at `39ee30c` (§5.1). **The `≈200`/`≈210` figures in
NT-0019 §5.6 are not used.**

- [ ] `backend/src/app/` — **88** citation-bearing files.
- [ ] `backend/tests/` — **93**, plus the **1988** `@pytest.mark.req` markers across
      `backend` and `packages`.
- [ ] `backend/migrations/versions/` — **28**, not 3.
- [ ] `packages/pricing-core/` — **70**.
- [ ] `packages/model-schema/` — **57**, then **regenerate contracts**.
- [ ] `frontend/src/` — **142** (the 144 in §5.6 is the whole `frontend/` directory).
- [ ] `examples/` **6**, `deploy/` **2**, `packages/README.md` **1**.
- [ ] **Every touched file is compiled and its suite run** (G11).

### 7.10 Task 10 — The vendored set, and the nine deliberate rows

Ruling 69 fixes the mechanism: `_VENDORED_SKILLS` is a **declared constant** of 28 skill
directories, reconciled against `pyproject.toml`'s ruff `exclude` restricted to
`.claude/skills/` as an independent second witness — never keyed on `LICENSE` presence, and
never taking the ruff list as the criterion.

- [ ] Stamp each vendored `SKILL.md` like the other 45, plus `vendored: true` and `origin:`.
- [ ] **Exempt from the blanket pass is not the same as never touched.** Apply the nine §5.4 rows
      that name a vendored skill as deliberate edits, and record the deviation in
      `.claude/skills/README.md` **once, as a class covering all 28** — not 28 times.
- [ ] Two of the nine are §6.2 members (`writing-plans`, `subagent-driven-development`), so they
      are in this commit for two independent reasons.
- [ ] Prove the reconciliation reds in both directions: remove one entry from
      `_VENDORED_SKILLS`, then one skill line from the ruff `exclude`, and the gate must red
      **naming which side moved**.

### 7.11 Task 11 — Delete, dissolve, redirect

- [ ] Delete the **19** `.claude/notes/` stubs (§4 step 4).
- [ ] Dissolve `docs/audit/`'s **43** files into `findings/`, `closures/`, `research/` and
      `process/` per §5.2's table — **including the two files with no §5.2 row**:
      `nt-0019-verification-and-impact-sweep.md` (an `RS- kind: audit`, owner auditor, under
      §5.4's bespoke-audit rule) and `work/nt-0010-0011-adoption/pilot-findings.md`.
- [ ] Write the four new directory READMEs (§7.4 decides the permitted-owner question).
- [ ] `REDIRECTS.csv` carries a row for every old id and path; every `was:` value has a row and
      every row's target exists (check 36).

### 7.12 Task 12 — The derived instruments (Ruling 66)

One sub-item per §6.2 member. Every one has its `Verified` date refreshed in the same commit
(`CLAUDE.md` §12).

- [ ] 1 `writing-plans` · [ ] 2 `subagent-driven-development` (+ `scripts/task-brief`) ·
      [ ] 3 `close-workstream` · [ ] 4 `phase-review` · [ ] 5 `adr-write` · [ ] 6 `spec-change` ·
      [ ] 7 `library-spike`.
- [ ] 8 `.claude/roles/planner.md` — replace the `docs/audit/plan-reviews.md` filing path and the
      `### Plan review N` heading form with the `CR- kind: review` route.
- [ ] 9 `.claude/roles/auditor.md` — all four `docs/audit/…` filing paths in its one bullet:
      work closures, the register, the checklists, the finding essays.
- [ ] 10 `.claude/roles/decision-maker.md` — one sentence routing `RL-` to
      `docs/_templates/RL.md` and `docs/process/document-ids.md` §1.6, replacing *"dated sibling
      records"*.
- [ ] 11 `.claude/skills/writing-skills/` — the `SKILL.md` front-matter field set, aligned with
      §7.1's `REFERENCE.md` declaration so a newly written skill passes check 30.
- [ ] 12 `.claude/skills/brainstorming/` — the one sentence §5.4 specifies; **its row-mate
      `planning-with-files` stays in W37-7** (§6.3), so the row is deliberately split.
- [ ] 13 `.claude/skills/README.md` — the *"creates"* column, plus Ruling 69's class-level
      vendored-deviation note (§7.10).
- [ ] **Check the dependency §6.2 names:** confirm which of `close-workstream` and
      `.claude/roles/auditor.md` ends up carrying the `FD-` **essay's** header and shape (as
      distinct from the register row's). Record it, so W37-7 does not later remove it from one on
      the assumption that the other has it.
- [ ] Re-run §6.4's enumeration at the merge tree. **An instrument in neither §6.2 nor §6.3 is a
      finding against this plan**, added under the criterion — never filed and corrected after.
- [ ] Per-member load-bearing proof, in Acceptance Standard item 11's **discriminating** form
      (revert the H content only), for members 1 to 11.

### 7.13 Task 13 — Acceptance, recorded

- [ ] Run (a) through (h) at the merge tree; paste each command **and its output** into the
      ledger.
- [ ] Record the merge-base SHA **and** the exact command that computed (g), so the result is
      re-derivable by checking that SHA out and re-running `migrate` (Ruling 68's obligation).
- [ ] Run the requirement-facing proof of Acceptance Standard item 12 on **W37-7's** branch, not
      this one. It is the item that actually tests DP-1, and it costs nothing extra because
      W37-7's leaf plan and ledger must exist anyway.

---

## 8. Carried in from W37-4 — three deferrals

All three are named in #573's merge commit on `main`, so the record is durable.

| # | Deferral | What discharges it here |
|---|---|---|
| 1 | **Ruling 70's** *"a fixture register row with no `decision:` must fail check 30"* — `docs/findings/register.md` is a markdown table, not YAML front matter, and is unreachable from `_ID_SCOPE_ROOTS` | §7.8 rewrites the register's header prose to declare the row's field set. Build the register-row check against **that** declaration, with Ruling 70 acceptance item 1's fixture proof: a fixture row with no `decision:` must fail. *Violation: it passes* |
| 2 | **Ruling 68's** *"one predicate, not two"* — `frozen_diff_is_permitted` is built and proven standalone, but the property that W37-6 **reuses** it rather than writing a second equivalent check is only checkable once W37-6 exists | (g)'s frozen-family branch **calls** `audit_docs.frozen_diff_is_permitted`. The proof is Ruling 68 acceptance item 3: mutate check 34's DP-7 allowance and (g)'s frozen-family branch must change behaviour. *Violation: one changes and the other does not.* The function is already exported at module level for this purpose, and its docstring says so |
| 3 | **Check 36's canonical proof is the only one of the ten that does not run through the full ten-check orchestrator** — an out-of-tree `tmp_path` fixture makes a later check's `.relative_to(REPO)` raise | Once `_ID_SCOPE_ROOTS` is the whole corpus, an **in-tree** fixture becomes possible. Attempt it; if it restores orchestrator isolation, check 36 gains the *"reds only its target check, not two"* cross-check the other nine have. **If it does not, re-defer with a named owner** — silence is not one of `CLAUDE.md` §13's four verdicts |

---

## 9. Register finding F68

`audit-docs.py` check 28 classifies every dated file in `docs/plans/` outside four suffixes as a
plan requiring an `## Acceptance Standard` section, while `check_plan_acceptance_standard`'s own
docstring disclaims that scope and warns against widening it to catch *"a future ledger, ruling
record or handover file."* The register carries this as [`F68`](../audit/findings/F68.md), with
the disposition **carry forward with a trigger — NT-0019's S2 migration PR**, which is this
slice.

- [ ] After the migration, `docs/plans/` holds only `PL-` files and rulings live in
      `docs/rulings/` as `RL-` files, so the shape that produced the false failure no longer
      exists in that directory. **Prove that; do not assume it.** Run the check's classification
      over the post-migration `docs/plans/` population and confirm no non-plan-kind file remains.
- [ ] Record the discharge in the ledger against the falsifiable condition the register row
      already states, and annotate the row in place with the date and this PR. *Violation: a
      ruling record filed in `docs/rulings/` after this commit still being asked for an
      Acceptance Standard section.*

**This slice does not patch check 28 from its own branch to make its own documents pass.** Two
documents in the session that wrote this plan were failed by check 28, and both included the
section rather than fighting it. This plan does the same.

---

## 10. Findings — what did not hold when the plan was written against it

Filed here because the map plan is frozen and a filed plan is not edited to agree with the
repository later. Each is verified against the shipped artifact at `39ee30c`, not relayed.

1. **Acceptance (f)'s baseline is not stable, and the two documents that name one name
   different ones.** NT-0019 §7 (f) pins to `8f5d57d` (104); the map plan's acceptance item 6
   pins to `89dd2b1` (107); `origin/main` at filing is 109. Pinning to either guarantees a false
   red. §5.4 supplies the executable form — which G3 requires without lowering the bar, so this
   is supplied, not waived.
2. **`git grep -c 'VR-DST-1'` does not count `VR-DST-1`.** It counts matching **lines** with an
   **unanchored substring**: 109 lines against 112 exact-token occurrences at `39ee30c`. The item
   works as a stability invariant provided the identical command runs at both ends — worth
   saying, because the obvious "improvement" of anchoring it at the second run only would break
   it.
3. **The `_ID_SCOPE_ROOTS` flip is not one constant and one line.** `_id_scope_documents`
   supports a file or a directory, and §4 step 5's stamp set contains a glob
   (`.claude/skills/*/SKILL.md`). Widening to the directory pulls in **237** files step 5 does
   not stamp. §7.1.
4. **`check_finding_citations` has five path dependencies on the dissolving trees, not one.** The
   map plan calls `scan_dirs` *"the second root"*; four further sites read `docs/audit/`, and
   three of the five degrade **silently** to an empty set rather than failing. §7.2.
5. **Check 39's PR-title clause is noted, not checked — and that decides `git-hygiene`.** Ruling
   66 names `git-hygiene` as a candidate on the strength of *"check 39's branch and PR-title
   grammar"*. The merged `check_index_stable` explicitly does not check it. Under Ruling 66's own
   criterion and its own acceptance item 2, `git-hygiene` is **not** a member. §6.3.
6. **Ruling 66's floor of seven is missing three families, all carried by charters.** No skill
   among the 46 mints a ruling record (`RL-`), and nothing routes the decision-maker to
   `docs/_templates/RL.md`; the §14 plan review (`CR- kind: review`) is filed by
   `.claude/roles/planner.md` at a path this commit deletes; and `.claude/roles/auditor.md`
   carries four filing paths into the dissolving `docs/audit/` tree in a single bullet. NT-0019
   D10 calls charters *"the creating instruments"* in as many words. **72** ruling headings exist
   across **29** files and more are minted every session, so the DP-1 window is occupied for
   `RL-` as surely as for `PL-` and `LG-`. §6.2 members 8, 9 and 10.
7. **NT-0019 §4 step 5 and §5.4 disagree about `.claude/skills/README.md`.** Step 5's stamp
   enumeration names `.claude/skills/*/SKILL.md`, which does not reach a README sitting directly
   under `.claude/skills/`; §5.4's first row gives that README an **H + M** change including a
   header. Disposed of in §6.2 member 13 — adopted on `CLAUDE.md` §12 grounds, with the honest
   statement that no check puts it there — and it is why §7.1 requires the scope roots to be
   written as step 5's set exactly, so *stamped* and *checked* are one set rather than two.
8. **Check 35's second clause is inert corpus-wide.** Zero `Permitted owners:` lines exist
   anywhere in `docs/` or `.claude/`. A green check 35 proves the first clause only. §7.4 makes
   the four new directory READMEs an explicit decision rather than an accident.
9. **§4 step 2's three split rules do not partition the tree as written.** Three of 72 ruling
   headings are `#` not `##`; two of the 29 ruling-bearing files are not named `*ruling*`;
   `closure-records.md` has zero `##` headings and three of its 21 `###` records are marked *"in
   progress, not closed"*; `plan-reviews.md` has 14 `###` of which 11 are reviews, the rest
   sitting under a `## Pending proposals` section with no destination in §5.2. §7.5.
10. **Two files under `docs/audit/` have no destination row in NT-0019 §5.2** — the auditor's own
    sweep record (this plan's evidence base) and
    `work/nt-0010-0011-adoption/pilot-findings.md`. §5.2's rows cover 41 of the directory's 43
    files. §7.11.
11. **The two filed size figures are both correct and both stale, and the corpus grows while the
    decision is open.** The map plan's W37-6 precondition says the go-ahead covers a run that
    *"rewrites citations in 1355 tracked files"*; Ruling 66's evidence tree states 1360 at
    `04ec6bf`. Re-running `git ls-tree -r --name-only <sha> | wc -l` at each pin reproduces both
    exactly, so **neither was ever wrong — both aged**: 1355 → 1360 → **1447** at `39ee30c`, and
    the population the migration actually rewrites 876 → 881 → **930**. Two further defects in the
    map plan's sentence, separate from the ageing: 1355 was its count of **tracked files**, not of
    files carrying a citation, so it overstated the rewrite population by ~480 even at its own
    pin; and NT-0019 §10's own figure for that population was 767 over a narrower pattern. §4.2
    replaces the flat total with a per-area breakdown and §4.2a carries the growth, its measured
    mechanism, and the correction that the dominant growth term is **fixtures, not governed
    documents** — which cuts against the intuitive reading, because Ruling 67 Part 2 excludes
    exactly that class from the sweep.
12. **Ruling 66's acceptance item 2 cannot discriminate a member from a non-member.** It says
    reverting a member to its merge-base content must produce *"at least one hit naming that
    file"* in W37-6's acceptance sweep. But §4 step 6 rewrites citations in **every** tracked
    file — *"`git ls-files`, nothing exempt"* — so reverting **any** of the 930 files carrying a
    legacy form produces an item-(d) hit, member or not. The test as written passes for
    `git-hygiene`, `dev-commands`, `repo-architecture` and 900-odd files nobody proposes to
    adopt. It measures *"is this file in the commit"*, which the **M** row already guarantees,
    not *"was its instruction content corrected"*, which is what DP-1 is about. Acceptance
    Standard item 11 states the discriminating form — revert the **H content only**, then produce
    the document and require a check to fire. **This is a defect in a ruling's acceptance item,
    which only its author can amend; this plan supplies the stronger form and names the weaker
    one rather than quietly substituting it** (G3).
13. **Check 30's unknown-field rule reds 53 files the moment they are stamped.** Every one of the
    46 `SKILL.md` files and all 7 agent charters already carries YAML front matter whose keys
    (`name`, `description`, and on agents `tools`, `model`) are absent from
    `docs/_templates/REFERENCE.md`'s declared field set; a handful of vendored skills add
    `allowed-tools`, `license`, `metadata` or `version`. A file has exactly one front-matter
    block — `_docid.parse_header` reads `lines[0] == "---"` to the closing `---` — so the stamp
    must merge, and check 30 then sees unknown fields on all 53. §7.1 carries the fix and the
    proof. **Neither NT-0019 §5.4's *"every `SKILL.md` (46) — header stamped"* row nor the
    template anticipates this.**
14. **`docs/_templates/REFERENCE.md` contradicts Ruling 69, in the words Ruling 69 rejected.** It
    states the vendored set is decided by *"any directory holding a `LICENSE` that is not the
    repository's own … **not a hand-kept list**"*. Ruling 69 rejected keying on `LICENSE`
    presence (it under-exempts 240 tracked files) and ruled for a hand-seeded declared constant
    reconciled against the ruff exclude list. The template landed in W37-1, before Ruling 69,
    and Ruling 69 §3's obligations name W37-2, W37-4 and W37-6 but not the template — which is
    how it survived. It is inside `_ID_SCOPE_ROOTS`, so it is governed. §7.4.
15. **Six of the ten new checks have never run against a corpus, and this commit is their first
    exercise.** At `39ee30c` the ten checks between them examine **one** document; checks 31, 32,
    34, 36, 38 and 39 examine zero. W37-4's ten broken-input proofs exercise each check on a
    fixture, which is the right proof of *"a check that has never printed a failure has not been
    tested"* — but it is not the same as running over ~1400 real files. §7.4 records this so a
    large first-run failure list inside this PR is read as the expected case rather than as
    something having gone wrong, and so nobody narrows a check to shorten the list.
16. **The sweep's own instrument reading needed a second pass, and the correction is worth
    recording.** An exhaustive enumeration reported `.claude/roles/decision-maker.md` as carrying
    *"no filename/id form of its own"* — literally true, and a first pass excluded it on that
    ground. Reading the whole charter showed the deferral **is** the defect: its three mandatory
    skills are `spec-change`, `git-hygiene` and `adr-write`, none of which covers `RL-`, and
    nothing routes the role to `docs/_templates/RL.md`. An instrument that teaches a wrong form
    fails loudly at the first document; one that is silent routes the author nowhere. §6.2
    member 10.

---

## Self-review

- **Every id cited individually, never as a range.** Rulings 66, 67, 68, 69, 70, 71 and 72 are
  each named where they bind; NT-0019's acceptance items are cited as (a) to (h) individually. No
  bare numeric range appears — a range silently drops an append-only id landed inside it.
- **Scope derived from the specification first, then evidenced.** The task list walks NT-0019
  §5's **H** rows scoped to S2 and the sweep's per-row corrections; it is not a recollection of
  what the map plan listed.
- **Every acceptance item is a violation that must become detectable.** Fourteen items, each with
  its failing case. Items 11 and 12 are Ruling 66's own pair, kept in its terms, because a
  mutation proof tests the implementation against the check and never the check against the
  requirement.
- **Volatile conditions are re-run, not recorded.** The three gap checks carry no answer.
- **Pending work is named, not guessed.** Six W37-5 dependencies in §3, each stating the
  obligation that holds regardless of the interface.
- **Every count carries its command and its corpus**, and where two pins disagree both are shown.
- **What did not hold is filed, not smoothed over.** Sixteen findings in §10, each verified against
  the shipped artifact at `39ee30c`.
- **No acceptance line.** §1's last precondition is the maintainer's, and §4 exists to make it
  informed. This plan does not write it and does not imply it has been given.

---

## Execution Handoff

**Executor skill:** `subagent-driven-development`. **Single executor, supervised, not fanned
out** — NT-0019 §4: *"one scripted PR, once."*

**Order:** §7.1, §7.2, §7.3, §7.4 **before anything moves** — the scope machinery must be able to
express the right set before the set exists, and the split rules of §7.5 must be fixed before the
splitter runs. Then §7.5 (the run). Then §7.6 to §7.12 in any order. Then §7.13.

**Do not start** until §1's preconditions are re-derived green **in the running session** and the
maintainer's dated go-ahead exists with §4 disclosed.

**On any disagreement between this plan and
[`../notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md), the note wins and
the disagreement is a finding against this plan.**
