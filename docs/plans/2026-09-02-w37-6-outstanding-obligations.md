# W37-6 — everything it owns before the run: one list, with each item's state and what discharges it

> **For agentic workers:** this is not an implementation plan and no step in it is
> executable on its own. It is the obligation list the maintainer asked for before
> authorising W37-6's run. §3 is the list; every other section exists to make a row in it
> readable.

**Goal:** put in front of the maintainer, in one table, every obligation standing between
`main` and W37-6's irreversible migration run — each with its state, its owner, and the
specific thing that discharges it.

**Architecture:** scope derived from the ruling record and the specification first, then
evidenced by running commands at a named tree — never from recollection of what was built
(`CLAUDE.md` §13). Every figure was produced in the session that wrote this file, at the
revision its row names.

**Tech Stack:** no code changes. `scripts/audit-docs.py`, `scripts/doc-id.py`,
`scripts/doc-index.py`, `scripts/_docid.py` and `scripts/register-lint.py` are read, never
modified.

**Spec:** [`../notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md),
with the frozen
[`2026-09-02-w37-6-migration-run-leaf-plan.md`](2026-09-02-w37-6-migration-run-leaf-plan.md)
as the plan this list is measured against.

**Trees.** Figures are measured at **`59bba94`** — `main` as this file is written. The lead's
brief named `ffac8ba`; `main` advanced twice while this was being assembled, and §4.4
records the movement rather than hiding it, because the movement is itself evidence about
the decision. Where a figure is quoted at `ffac8ba` or `39ee30c` its row says so.

## Acceptance Standard

Complete when every item below holds. Each is stated as a violation that must be
detectable, never as a property asserted.

1. **The list is derived, not recalled.** Every row in §3 cites the artifact that created
   the obligation — a ruling section, a leaf-plan finding, a register row, or a command's
   output. *Violation: a row whose source names no artifact, or names one that does not
   contain the obligation when opened.*
2. **Every row carries a state and a named owner.** *Violation: a blank state, or an owner
   given as "the team" or left absent — silence is not one of `CLAUDE.md` §13's four
   verdicts.*
3. **Every discharge is an action that can be taken and then checked**, not a disposition.
   *Violation: a discharge cell that restates the problem or says only "fix it".*
4. **No figure is inherited.** *Violation: any count here traceable only to another
   document. The test a reviewer runs: re-execute the stated command at the stated
   revision and reproduce the stated value.*
5. **The frozen leaf plan is not edited.** *Violation: any diff in the pull request
   carrying this file that touches
   `docs/plans/2026-09-02-w37-6-migration-run-leaf-plan.md` (`CLAUDE.md` §2).*
6. **An item whose state depends on work in flight names that work and does not predict
   its outcome.** *Violation: a row asserting an in-flight branch's result.*
7. **Both gate scripts pass on the branch carrying this file** —
   `python3 scripts/audit-docs.py` and `uv run python scripts/req-coverage.py` exit 0.
   *Violation: any non-zero exit.*

## Global Constraints

- **This document decides nothing.** §7's scope-versus-replan answer is a **proposal**.
  `CLAUDE.md` §15 and `.claude/roles/planner.md` reserve replan-versus-proceed to the lead
  and every Work, Phase or Project close to the maintainer. A planner supplies a new dated
  plan when told to; it does not decide to write one.
- **No ruling is made here.** Where an item needs a decision or a ruling the row says so
  and names its holder. Two items are the planner's own derivations, and they are recorded
  as work owed, not performed in this file.
- **Requirement ids and section numbers are permanent** (`CLAUDE.md` §5). Nothing here
  renumbers anything.
- **Every count carries its tree and the corpus it counted over**
  ([`NT-0004`](../notes/0004-a-reference-that-resolves-only-for-the-writer.md)).

---

## 1. How this list was built, and what would make it wrong

Four passes, in this order:

1. **The ruling record**, every dated record under `docs/plans/` carrying a `Ruling N`
   heading — 82 headings across 32 files at `59bba94`. Each ruling's *"What it obliges"*
   and *"Acceptance"* sections were read for an assignment naming W37-6, and each
   assignment was then checked against the code or document it names.
2. **The frozen leaf plan's own §10**, all sixteen findings, each re-tested at `59bba94`
   rather than assumed still true. Three are now discharged by later rulings; twelve still
   hold; one is superseded in a way that changes its remedy (§6.3).
3. **The scripts themselves**, run rather than read where running was possible — the
   legacy-form sweep through the shipped constant, the vendored-set arithmetic, the
   full `audit-docs.py` report, the checks-30-39 scope counts.
4. **A sweep for obligations belonging to nobody**, which is where items 30 to 34 came
   from. Those were on none of the sources the lead supplied.

**What would make this list wrong.** It is a snapshot of a repository three agents are
writing to concurrently. `main` moved from `ffac8ba` to `59bba94` during the four hours
this took, landing two ruling records that changed four rows. Two more rulings exist on a
branch with no pull request. **The correct use of this document is to re-run §3's
verification column, not to trust its states.** Every row's state cell is dated
2026-09-02 and names what to re-run.

---

## 2. The state vocabulary

Six states, and each means something a maintainer can act on differently.

| State | Meaning | What the maintainer does with it |
|---|---|---|
| **FIXED** | Landed on `main`; nothing remains | Nothing |
| **RULED, UNMERGED** | A decision exists as a dated record on a branch, not on `main` | Ask why the branch has not merged |
| **IN FLIGHT** | Being worked now; the worker is named | Ask for its state, not for a plan |
| **FILED, NOT FIXED** | The defect is recorded and understood; no code exists | Decide whether it precedes the run |
| **NEEDS A DECISION** | A design or routing question with no ruling; the decision-maker's | Route it, or accept the delay |
| **OWED BY THE PLANNER** | A derivation this role owes before a ruling can be made | Tell the planner to start |

---

## 3. The list

**Gate** says when the item must be discharged relative to the run: **A** before it,
**B** by it, **C** neither. The gate is derived, and where a ruling states the ordering
the row cites it rather than asserting it.

| # | Gate | Item | State | Owner | What discharges it |
|---|---|---|---|---|---|
| 1 | A | `_discover_plan_reviews` under-discovers silently: 14 `###` headings, regex matches 10, function returns 10; the four unmatched fold into `Plan review 1` (2026-08-15), which absorbs lines 1061-2155 including the whole of `Plan review 9` (2026-08-30). Ruling 82 §1(b) | IN FLIGHT | agent `exec-plan-reviews`, branch `worktree-plan-reviews-fix`, zero commits at 08:47Z | Trailing-text capture group in the shape `#585` used for `_CLOSURE_HEADING_RE`, plus the coverage assertion of Ruling 83; positive control = the four headings named, red before, green after |
| 2 | A | `_discover_roadmap` converts 0 of 41 works and `migrate` reports success. Guard added in `#584` raises; the pattern is untouched. Ruling 79/80 record's *Correction* section | FILED, NOT FIXED | unassigned | A roadmap transform designed against the real shape — semantics in decoration (`~~**W4**~~ ✔`), non-work rows in the work column, free-prose status cells, several status tables per phase — not a widened regex |
| 3 | A | `_discover_register` matches 0 of 73 data rows: `_REGISTER_FINDING_RE.fullmatch` wants a bare `F<n>`, real cells are compound. Guard added in `#584` raises; the pattern is untouched | FILED, NOT FIXED | unassigned | A cell pattern derived from the register's declared row grammar, plus Ruling 83's census applied to the row unit (Ruling 83 *Not ruled* routes the measurement to W37-6's executor) |
| 4 | A | Ten `W5 —` closure records carry no family; `_discover_closure_records` raises on the **first** and stops, so clearing them is ten sequential resolve-and-re-run cycles, not one | RULED, UNMERGED | Ruling 84, branch `docs/w37-rulings-83-84-…` at `2694fc3`, no pull request at 08:47Z | Merge Ruling 84; the "not closed" branch emits `LG-` with `work:` and no `slice:`; the test asserting 21 drafts as 8 `CR- work` + 1 `CR- phase` + 2 `RS- audit` + 10 `LG-` |
| 5 | A | The guard class fails on zero, not on undercount. Both shipped guards test only "zero drafts from a non-blank file", which is why item 1 passes ungoverned at 10 of 14 | RULED, UNMERGED | Ruling 83, same branch | Merge Ruling 83; implement the level-independent census with buckets 1-3 balancing and unit-naming failure text. **Ruling 83 §3 item 1 puts the census before W37-6, not inside it** |
| 6 | A | What `Ruling A1`, `A2`, `A3` are — a family and id-form question the census cannot proceed past. Ruling 83 *Not ruled*: *"the census cannot be cleared while three units are unclassified"* | OWED BY THE PLANNER | planner, then the decision-maker | A derivation enumerating the option set under the id standard §1.2 and §1.7, returned to be ruled |
| 7 | A | The `## Pending proposals` container's family and `kind:`. Ruling 82 §3 item 3 fixes four constraints and hands the positive assignment over | OWED BY THE PLANNER | planner, then the decision-maker | A derivation testing both surviving placements — own record, or `Plan review 9`'s preamble — against Ruling 68 acceptance (g) class 4, saying what `Plan review 9`'s two self-citations rewrite to |
| 8 | A | Rulings 79 and 80: `_ROW_FIELDS` is a transcribed field policy wrong in both directions; `scan_phase_sections` requires a fence the templates do not use and reads with unbounded lookahead | IN FLIGHT, zero commits | agent `exec-rulings-79-80`, branch `fix/doc-index-row-phase-fields`, byte-identical to `main` at 08:47Z | Ruling 81: one pull request, merged on its own, before W37-6, carrying reader and writer together, plus two fixtures' phase sections rewritten unfenced. Ruling 81 §3 item 3: if it does not land first the work reverts to W37-6 |
| 9 | A | `_VENDORED_SKILLS` does not exist. `is_vendored` still keys on `LICENSE` presence — the criterion Ruling 69 rejected — exempting 2 of 46 skills where the repository treats 28 as vendored, under-exempting 240 tracked files | FILED, NOT FIXED | W37-6 executor, per Ruling 76 | A declared constant reconciled against the ruff exclude list, drift loud. **This blocks leaf-plan acceptance item 13** — see §5.4 |
| 10 | A | `docs/_templates/REFERENCE.md` lines 39-49 still teach the rejected criterion in the words Ruling 69 rejected: *"not a hand-kept list"*. It is inside `_ID_SCOPE_ROOTS`, so it is governed today | FILED, NOT FIXED | W37-6 executor, per Ruling 76 | Rewrite to the declared-constant rule. Member 2 of Ruling 76's three-site class |
| 11 | A | Five tests pin the rejected criterion: `test_is_vendored_*` at `tests/test_doc_id.py:387,398,410,427,438` | FILED, NOT FIXED | W37-6 executor, per Ruling 76 | Re-point all five and add the reconciliation broken-input proof. Member 3 of the class, and on none of the known sources |
| 12 | A | F76 — check 39 calls `build_corpus` unguarded at `scripts/audit-docs.py:2207`; it is the last call in `check_ids_30_39()`, which `main()` runs before six further checks. **Check 28 is one of the six** | FILED, NOT FIXED | W37-6 per Ruling 79 | Guard it, with a broken-input proof that a malformed header does not silence the six. See §5.5 |
| 13 | A | No check feeds a template's own example block to the parser that consumes it. Ruling 79 §4 first acceptance bullet | FILED, NOT FIXED | W37-6 executor | A check that fails today with `unknown row field 'tree'` — the positive control the corpus already supplies |
| 14 | A | `plan-reviews.md`'s heading mis-nesting: reviews 9 to 11 sit under a `##` titled *"Pending proposals"*. Ruling 82 §3 item 4 | FILED, NOT FIXED | the lead, as a finding | A structural correction to the document. Blocks nothing; Ruling 82: *"the migration should not be the first thing to discover it"* |
| 15 | A | Whether the multi-ruling splitter tries to split the three h1 ruling files. Ruling 83 *Not ruled* | NEEDS A DECISION — as a measurement | W37-6 executor, inside the census | Run the splitter over them. If it does try, that is a new finding |
| 16 | B | Ruling 66's thirteen creating instruments, with `Verified` dates refreshed in the same commit. The thirteen live in leaf plan §6.2, not in Ruling 66, which states seven as a floor | FILED, NOT FIXED | W37-6 | The single commit, plus the nine explicit exclusions each with its slice |
| 17 | B | Ruling 68's *"one predicate, not two"*: `frozen_diff_is_permitted` exists at `scripts/audit-docs.py:1711` and has **zero callers outside its own tests**; `scripts/doc-id.py` contains zero occurrences of it | FILED, NOT FIXED | W37-6 | (g)'s frozen-family branch calls it. Proof: mutate check 34's allowance and (g) must change behaviour with it |
| 18 | B | Ruling 70 and Ruling 71 both oblige the register's header prose to declare the row field set and the ownership shapes in one place | FILED, NOT FIXED | W37-6 | The rewrite, with Ruling 70 acceptance item 1's fixture: a register row with no `decision:` must fail |
| 19 | B | Check 36's canonical proof is the only one of ten that does not run through the full orchestrator | FILED, NOT FIXED | W37-6 | An in-tree fixture once the scope widens; **or** a re-deferral with a named owner — silence is not a verdict |
| 20 | B | F68 — check 28 classifies every dated `docs/plans/` file outside four suffixes as a plan | FILED, NOT FIXED | W37-6 | Run the classification over the post-migration population and prove no non-plan-kind file remains. Not by patching check 28 |
| 21 | B | The `_ID_SCOPE_ROOTS` flip is not one constant and one line: 237 non-`SKILL.md` markdown files sit under `.claude/skills/` that the stamp set does not reach | FILED, NOT FIXED | W37-6 | `_id_scope_documents` expressing the stamp set exactly, so *stamped* and *checked* are one set |
| 22 | B | `check_finding_citations` has five path dependencies on the dissolving trees; three degrade silently to an empty set | FILED, NOT FIXED | W37-6 | Each re-pointed with its own mutation proof that reds |
| 23 | B | Check 35's second clause is inert corpus-wide: zero `Permitted owners:` lines exist in any governed document | FILED, NOT FIXED | W37-6 | The four new directory READMEs as an explicit decision |
| 24 | B | Checks 30-39 have never met a corpus. Measured at `59bba94`: checks 30, 33, 35 and 37 each examine **one** document — the same one; 31, 32, 34, 36, 38 and 39 examine **zero** | FILED, NOT FIXED | W37-6 | Nothing discharges it before the run. It is the largest untested surface in the package and belongs in the disclosure |
| 25 | B | Ruling 73 amends leaf-plan acceptance item 11 in three respects: `brainstorming`'s exemption removed, limb 2b (the exclusion list) added, limb 2c (neither list) added | FILED, NOT FIXED | W37-6 | Running 2a, 2b and 2c. **The frozen plan cannot carry the amendment**, so a run against the frozen text alone applies a weaker standard — see §6.3 |
| 26 | B | Ruling 74's negative obligation: no W37-6 artifact may assert that the identifier standard's PR-title clause is enforced, satisfied or discharged | FILED, NOT FIXED | W37-6 | Running limb 2b over `git-hygiene` and recording *"no document to produce"* as evidence rather than a silent pass |
| 27 | B | Ruling 75's charter edits: `decision-maker.md` still reads *"recorded as dated sibling records"*; `auditor.md` names **six** dissolving paths, not the four the task list states; `planner.md` names `plan-reviews.md` throughout | FILED, NOT FIXED | W37-6 | The three edits, verified by `git grep -n 'docs/audit/' -- .claude/roles/` returning nothing at the merge tree |
| 28 | B | Ruling 77's two orphan files need `REDIRECTS.csv` rows **by explicit path** — a glob-driven generator misses both | FILED, NOT FIXED | W37-6 | Both rows, plus the prospective-only findings clause. The routing question itself is settled |
| 29 | B | Acceptance item (f)'s baseline must be re-derived at the run's own merge base | FILED, NOT FIXED | W37-6 | The leaf plan §5.4 executable form. See §5.3 — the drift is accelerating |
| 30 | A | `_discover_requirements` is the only discovery function with **no guard at all**: silent, unwrapped, 660 drafts against the real corpus. The three guard calls sit at `scripts/doc-id.py:1829, 1834, 1842`; it is called at `:1839` and guarded by none | FILED, NOT FIXED | W37-6 executor | Ruling 83's census applied to it too. On none of the known sources, and it is the largest single output of the migration |
| 31 | A | Four more discovery functions are silent by construction — `_discover_multi_ruling_files`, `_discover_headed_split_file`, `_discover_plain_plans`, and the skip paths of `_discover_notes` and `_discover_adrs` | FILED, NOT FIXED | W37-6 executor | The same census. `_discover_headed_split_file` is the shared mechanism behind item 1 |
| 32 | C | Leaf plan §4.2 states 710 requirement ids are renumbered. 41 of those are `VR-` ids the same table guarantees untouched. The renumbered population is **673** at `59bba94` | FILED HERE | the next disclosure | §5.1 |
| 33 | C | Leaf plan §4.2 states 1988 markers are rewritten. That is the `backend`+`packages` figure; the run rewrites **2445**, of which **421** sit inside frozen dated plans | FILED HERE | the next disclosure | §5.2 |
| 34 | C | The technique Ruling 83 ratifies already exists in this repository — `scripts/register-lint.py` asserts `classified == seen` for a different file and was never applied to `migrate`'s discovery functions | FILED HERE | W37-6 executor | Reuse it rather than inventing a second form. On none of the known sources |
| 35 | C | The permanence rule is broken between W37-6's merge and W37-9's: `CLAUDE.md` states it at two sites and D2 renumbers every requirement id | DISCLOSED, ACCEPTED | maintainer, via the go-ahead | Nothing before the run. Leaf plan §4.6 discloses it; it is listed here so it is not mistaken for an oversight |

**Three items from the leaf plan's §10 are discharged and are listed so nobody re-opens
them:** the two `docs/audit/` files with no destination row (Ruling 77, settled
unconditionally); `git-hygiene`'s exclusion from the instrument set (Ruling 74, confirmed
on two independent grounds); and the three role charters' membership (Ruling 75, confirmed,
with the correction that `auditor.md` carries six paths rather than four).

---

## 4. The figures, re-derived

### 4.1 The size of the run

| The migration… | `39ee30c` (leaf plan §4.2) | `59bba94` (today) |
|---|---|---|
| tracked files | 1447 | **1473** |
| rewrites a citation token in | 930 | **938** |
| ...matching lines | 20 507 | **21 048** |
| stamps a header on | 295 | **304** |
| moves, splits or deletes | 213 | **222** |
| regenerates, never hand-edits | 61 | **61** |
| does not touch at all | 517 | **535** |
| ruling headings split out of `docs/plans/` | 72 over 29 files | **82 over 32 files** |

Reproduce: `git ls-files` for the tracked count; `sweep_legacy_forms` called with the
shipped `LEGACY_FORM_PATTERNS` over that list for the rewrite population — never a re-typed
copy of the pattern, per Ruling 67 acceptance item 2 applied to measurement as well as to
the control.

### 4.2 The rewrite population by tree

| Tree | `39ee30c` | `59bba94` |
|---|---|---|
| `docs/` | 297 | **306** |
| `backend/` | 217 | **217** |
| `frontend/` | 144 | **143** |
| `packages/` | 135 | **135** |
| `.claude/` | 55 | **54** |
| `tests/` | 45 | **46** |
| `scripts/` | 19 | **19** |
| root files | 7 | **7** |
| `examples/` · `.github/` · `deploy/` | 6 · 3 · 2 | **6 · 3 · 2** |

Two rows moved **down** while the total moved up. Growth is not uniform, and one total
conceals that.

### 4.3 The trees being dissolved

| Tree | `39ee30c` | `59bba94` |
|---|---|---|
| `docs/audit/` | 43 | **46** |
| `docs/plans/` | 131 | **137** |
| `docs/notes/` | 20 | **20** |
| `.claude/notes/` | 19 | **19** |
| total | 213 | **222** |

Every file `docs/plans/` gained is W37's own governance output, and three of the four
`docs/audit/` additions are finding records this Work filed. The self-referential growth
leaf plan §4.2a measured is still the mechanism.

### 4.4 The tree moved twice while this was written

| Time (UTC) | `main` | Tracked | What landed |
|---|---|---|---|
| session start | `ffac8ba` | 1471 | — |
| 08:47 | `0e9f620` | — | Rulings 81 and 82 (`#589`) |
| 08:47 | `59bba94` | 1473 | The withheld go-ahead recorded, and the roadmap's `plan-reviews` figures corrected (`#590`) |

**The shared checkout moved under a measurement in progress.** The first pass of §4.1 ran
partly at `ffac8ba` and partly at `59bba94`; it was discarded and re-run with `HEAD`
stamped before and after, which is why every figure above is at one pin. The incident is
recorded rather than tidied away because it is the same failure mode the maintainer
identified in the disclosure: *a figure that does not carry the tree it was taken at is
not a figure.*

---

## 5. Five things on none of the known sources

### 5.1 The disclosure says 710 ids are renumbered; 41 of them must never move

Leaf plan §4.2 closes: *"**710 distinct requirement ids** are renumbered."* The figure
reproduces, because §5.5's pattern `R` includes `VR`:

| Pattern at `59bba94` | Distinct ids |
|---|---|
| `\b(FR\|NFR\|OQ\|DEP\|VR)-[A-Z]+-[0-9]+\b` — §5.5's `R` | 716 |
| `\b(FR\|NFR\|OQ\|DEP)-[A-Z]+-[0-9]+\b` — the renumbered population | **673** |
| `\bVR-[A-Z]+-[0-9]+\b` | 43 |

The same §4.2 table, four rows above that sentence, names those ids as *"must leave
unchanged, by rule"* on D5 and G5 grounds, and acceptance item (f) exists to prove they did
not move. **The disclosure states that identifiers are renumbered on the same page where it
guarantees they are not.** §5.1's own table row is not at fault — it is headed *"Distinct
requirement-family ids"*, a neutral population count, and 710 was right for that at
`39ee30c`. The defect is the verb in §4.2.

### 5.2 The disclosure says 1988 markers are rewritten; the run rewrites 2445

§5.5's command for the marker figure is scoped — `-- backend packages`. §4.2 states the
result as an unscoped property of the run, and step 6 rewrites over `git ls-files`,
*"nothing exempt"*. Decorator occurrences at `59bba94`:

| Where | `@pytest.mark.req(` |
|---|---|
| `backend/` + `packages/` — the measured scope | 1985 |
| `docs/plans/` — inside frozen dated plans | **421** |
| `docs/` elsewhere | 14 |
| `tests/` and `examples/` — executable, outside the scope | 20 |
| `.claude/`, `scripts/`, `pyproject.toml` | 5 |
| **repository-wide** | **2445** |

The understatement is 460 (23%). The part that matters is not the size: **421 of the 460
sit inside frozen dated plans**, the one class whose diff is not free but governed by
Ruling 68's six-class permitted-diff predicate. Each is a citation the run rewrites and the
freeze predicate must then classify. The disclosure does not put that load in front of the
maintainer.

*(1988 is a line count; 1985 decorators sit on 1988 matching lines. Both reproduce; neither
is the repository-wide figure.)*

### 5.3 Acceptance (f)'s baseline moved further in one day than in all the time before it

| Pin | `git grep -c 'VR-DST-1' <sha>`, summed |
|---|---|
| `8f5d57d` — the identifier standard's own baseline | 104 |
| `89dd2b1` — the map plan's baseline | 107 |
| `39ee30c` — leaf plan filing | 109 |
| **`59bba94` — today** | **120** |

**+11 in one day, against +5 across every commit before it.** This does not change leaf
plan §5.4's remedy; it strengthens it, and it quantifies the maintainer's own reason for
withholding. (`git grep -c` counts lines: the exact-token count at `59bba94` is 124.)

### 5.4 `is_vendored` exempts 2 skills; the repository treats 28 as vendored

| Set at `59bba94` | Count |
|---|---|
| skill directories under `.claude/skills/` | 46 |
| carrying their own `LICENSE` — what `is_vendored` exempts | **2** |
| in the ruff exclude list — what the repository treats as vendored | **28** |
| ruff-excluded, carrying no `LICENSE` | **26** |
| tracked files beneath those 26, excluding their manifests | **240** |

The 240 matches `is_vendored`'s own docstring, derived here independently rather than read
from it.

**The consequence, which is what is new.** Leaf plan acceptance item 13 requires that after
the run *"a file beneath a vendored skill's `SKILL.md` carrying a legacy citation and no
header is byte-identical to its merge-base content."* Exactly two tracked files meet that
description — `.claude/skills/graphify/references/update.md` and
`.claude/skills/subagent-driven-development/scripts/task-brief` — and under the shipped
`LICENSE` predicate neither is vendored, so the run rewrites both. **Acceptance item 13
cannot pass until `_VENDORED_SKILLS` exists.** Item 9 is not a tidiness item deferred to
taste; it is a precondition for the slice's own acceptance standard.

### 5.5 F76 costs six checks, and check 28 is one of them

`check_index_stable()` calls `_doc_index.build_corpus(ROOT)` unguarded
(`scripts/audit-docs.py:2207`). It is the tenth and last call inside `check_ids_30_39()`,
which `main()` runs before exactly six further checks:

| # | Lost to one uncaught header error |
|---|---|
| 1 | `check_open_question_mirror_status` |
| 2 | `check_finding_citations` |
| 3 | `check_process_core_drift` |
| 4 | `check_process_core_digest` |
| 5 | `check_plan_acceptance_standard` — **check 28** |
| 6 | `check_register_grammar` — check 29 |

The count of six is confirmed. The detail worth adding is which six. During a commit whose
purpose is to stamp headers on 304 files for the first time, a malformed header silently
disarms the check that holds every filed plan to an acceptance standard — including
W37-6's own ledger.

---

## 6. Three corrections to the frozen plan, which is not edited

`CLAUDE.md` §2 freezes a filed plan at its date. These are recorded here so that a reader
holding the leaf plan alone does not act on a superseded instruction.

### 6.1 Acceptance item 13 is unsatisfiable as things stand

§5.4 above. The remedy is item 9, not a change to item 13.

### 6.2 §4.2's two closing figures

§5.1 and §5.2 above. Both reproduce at their own pin; both mis-state what the run does.

### 6.3 Acceptance item 11 is amended in three respects, and the plan cannot say so

Ruling 73 withdrew Ruling 66's acceptance item 2 and replaced it with a three-limb
H-content test. Its §4 holds that leaf plan **item 11 is the discriminating form and stands
as written** — with `brainstorming`'s exemption **removed**, and limbs **2b** (the same
proof over the exhaustive exclusion list) and **2c** (an instrument in neither list) added.

The frozen plan's item 11 still states two exemptions, one of which Ruling 73 rejects by
name and with a reason: the reverted instruction *"is an instruction to save a design
document at a path under `docs/`"*, which the stamp set reaches once the flip lands.

**An executor following the leaf plan alone applies a weaker acceptance standard than the
ruling requires, and would wrongly exempt one of the thirteen.** This is the clearest
single argument in §7 for a plan revision: the frozen document cannot carry its own
amendment, and the amendment is to its acceptance standard.

---

## 7. Proposal: scope, or replan

**A proposal only.** `.claude/roles/planner.md` reserves replan-versus-proceed to the lead;
a planner supplies a new dated plan once told to, and does not decide to write one.

### 7.1 The remainder does not fall on one side

Walking all 35 rows, they separate on a property that decides the question by itself:
**can the item be proven on deliberately broken input outside the irreversible commit?**

| Group | Rows | Testable outside the run? |
|---|---|---|
| **A — preconditions** | 1-15, 30, 31 | **Yes.** Every one is a defect in already-merged code or in an instrument. None needs the migration to have happened |
| **B — genuinely in-run** | 16-29 | **No.** Each is observable only once the corpus has moved |
| **C — neither** | 32-35 | Not a gate either way |

### 7.2 Two rulings have already placed group A before the run

This is not my inference. **Ruling 81 §2** holds that the parser fix *"lands as its own
pull request, merged on its own, before W37-6 runs"*, on the ground that it creates no red
state on `main` and *"a migration run against an already-correct parser is one fewer
variable in the run that can least afford one."* **Ruling 83 §3 item 1** holds that *"the
census runs before W37-6, not during it"*, and its §2 explicitly rejects deferring it:
*"the guard fix is testable today against a corpus that already produces four distinct
violations."*

So the boundary is already drawn by ruling for rows 5, 8 and, through the census, 1, 2, 3,
15, 30 and 31. What has not been decided is whether the rest of group A joins them and
whether the collection is a slice.

### 7.3 Why the rest of group A should join them

Two of the four discovery defects are not bug fixes. The roadmap transform is a **parser
design problem** — semantics in decoration, non-work rows sharing the work column,
free-prose status cells, several tables per phase. `_discover_plan_reviews` is the same
species: Ruling 82 had to decide what the *unit* is before any regex could be written.

**A design question resolved inside an irreversible commit is resolved without a
rehearsal.** That reasoning already produced W37-5 as its own slice with its own fixture
corpus. It has not changed — only the evidence that W37-5's corpus was not representative
of the tree it was built to migrate.

### 7.4 What I propose

**One new slice, and one plan revision.**

1. **Insert `W37-5b` between W37-5 and W37-6**, scoped to group A. It is the second half of
   W37-5 and takes W37-5's own discipline: every fix proven on deliberately broken input,
   and the corpus supplying its own expected count. The slice-letter form has precedent in
   this repository (`w32-1b`, `w11-2b`, `w6b-13b`), so no id is renumbered and none reused.
   Its acceptance standard is one sentence and is already written, in Ruling 83:
   **every unit a source offers is classified into exactly one of a record, derived body,
   or a declared exception, and the three sum to the total** — run against the real corpus,
   not a fixture.
2. **File a new dated leaf plan for W37-6, superseding the frozen one.** Not because the
   frozen plan is weak — every figure in it reproduces at its own pin, which is rarer than
   it should be — but because three things under it have moved and a frozen plan is not
   edited to agree with them: its acceptance item 11 is amended by Ruling 73 (§6.3); its
   §3 dependency model covers *"the interface is not fixed yet"* and not what happened,
   which is that the dependency merged, went green, and is defective in four places; and
   its §4 figures are pinned at a tree that is 15 commits behind, while Ruling 66 §3
   requires the disclosure to arrive **with** the ask.

**What I do not propose:** no re-cut of W37 into different workstreams, no change to the
identifier standard's §4 step list, no change to the S1/S2 boundary, no change to any
requirement id, and no change to W37-6's own task list, which group B leaves intact.

### 7.5 Sizing

| | Estimate | Basis |
|---|---|---|
| `W37-5b` | comparable to W37-5 | four discovery functions, two of them design work, plus the census, plus five instrument and guard fixes that are small and independent |
| The W37-6 leaf-plan revision | one planner session | §5, §6 and §7 of the frozen plan carry over nearly unchanged; §1, §3, §4 and the Acceptance Standard are rewritten |
| W37-6 itself | unchanged | nothing in group B has grown |

**The counter-argument, stated because it is real.** Inserting a slice makes the corpus
grow further under the decision, and the growth is monotonic: +26 tracked files and +8
rewrite-population files between `39ee30c` and `59bba94`, with the `VR-DST-1` baseline
moving +11 in a single day. **Waiting is measurably more expensive than not waiting.** That
cost is real, and it is still smaller than resolving two parser-design questions inside a
commit that cannot be re-run.

---

## 8. What this document does not do

- It does not rule the guard property. Ruling 83 does, on a branch with no pull request.
- It does not perform the two derivations rows 6 and 7 name. They are the planner's, they
  are sized in §7.5, and they are on the critical path: Ruling 83's census cannot be
  cleared while three units are unclassified.
- It does not amend, edit or supersede the frozen leaf plan.
- It does not give, imply, or anticipate the maintainer's go-ahead.
