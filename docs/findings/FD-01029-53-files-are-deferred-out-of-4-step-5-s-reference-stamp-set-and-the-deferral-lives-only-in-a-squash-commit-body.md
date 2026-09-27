---
id: FD-1029
family: finding
title: 53 files are deferred out of §4 step 5's Reference stamp set, and the deferral lives only in a squash-commit body
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F92.md
---

# F92 — 53 files are deferred out of §4 step 5's Reference stamp set, and the deferral lives only in a squash-commit body

**Raised** 2026-09-02 by the W37-5c close auditor; id allocated on the lead's direction rather
than by the auditor, for the reason in *Why the id waited* below. Work item **W37-6**, phase 2.
Register row: `(F92)` in [`register.md`](register.md).

**The deferral is correct. Where it is recorded is the defect.** Nothing here argues the 53
should have been stamped in W37-5c.

## What was deferred, and why that was right

`47eb2ba` (#639) built item 2's discovery-and-stamp path and **deferred 53 files** out of it.
Measured at `d8d6e3f`, by the predicate rather than by the commit body:

```
git ls-files '.claude/skills/*/SKILL.md'                   | wc -l   ->  46
git ls-files '.claude/agents/*.md' | grep -v 'README.md$'  | wc -l   ->   7
                                                                        ---
                                                                         53
```

Every one already carries the harness's own YAML front matter. `_docid.parse_header` reads
`lines[0] == "---"` and then to the closing `---`, so a file has exactly one block: a stamp
cannot be **prepended**, it must be **merged** into the existing one — and check 30 then rejects
`name`, `description` and the rest as unknown fields unless `docs/_templates/REFERENCE.md`
declares them. That template change is W37-6's own §7.1 Task 1, under RL-981's licensing
instrument.

**Building it inside a precondition slice would have been building ahead of the phase**
(`CLAUDE.md` §0's table). The deferral is the right call, and the run is not blinded by it: the
53 are carried by name on `MigrateResult.deferred_reference_stamps` (`scripts/doc-id.py:1028`)
and printed unconditionally by `_cmd_migrate`.

## The defect: two records of one population, and nothing joins them

**Searched at `d8d6e3f`:**

```
git grep -n "deferred_reference_stamps" -- docs .claude        -> no hits
git grep -ln "already carry their own front matter" -- docs    -> no hits
```

The disposition — *that W37-5c's `migrate()` now defers exactly this population* — exists in
exactly two places: **`47eb2ba`'s squash-commit body**, which cannot be amended, and **at
runtime**, visible only to someone who has already run the migration this deferral is a
precondition of.

**And the same 53 files are already in a plan, under a different description.** The **frozen**
leaf plan [`../plans/PL-00960-w37-6-the-migration-run-leaf-plan.md`](../plans/PL-00960-w37-6-the-migration-run-leaf-plan.md)
reaches the identical population from the other end — item 13 at `:1194`, evidence at
`:748-761`: *"Check 30's unknown-field rule reds 53 files the moment they are stamped … all
**46** `.claude/skills/*/SKILL.md` … all **7** `.claude/agents/*.md` … the migration must
**merge** its fields into the existing front matter."*

**46 + 7 = 53 — the same files, the same root cause, described twice and joined nowhere.** The
**active superseding** plan carries neither: `grep -n "REFERENCE.md\|merge.*front matter\|Task 1"`
over `…-leaf-plan-v2.md` returns nothing. **A W37-6 planner working from the active plan sees
neither the deferral nor its cause.**

## Why this is a finding and not housekeeping — the precedent is F87's

[`FD-01024-widening-id-scope-roots-reaches-no-non-markdown-file-so-62-of-the-65-exempt-files-stay-invisible-to-checks-30-39.md`](FD-01024-widening-id-scope-roots-reaches-no-non-markdown-file-so-62-of-the-65-exempt-files-stay-invisible-to-checks-30-39.md) was filed for this exact shape, in its own words: the fact *"lived only in a
passing test … invisible to whoever plans W37-6, who is the person who needs it."* The 53 live
in a commit body and a runtime print — the same invisibility by a different route.

**`RFC-778`, quoted by F83's own register row, is the rule**: *"a deferred item with no owner is
not deferred, it is lost."*

## Why the register, and not the roadmap

The register is **the only home `register-owed.py W37-6` can return** — so it is the only one
that reaches a planner who does not already know to look. That is the argument that decided it,
not an argument about altitude.

The frozen plan is out (`CLAUDE.md` §2, and `../../plans/README.md`: *"Do not edit a filed plan
to agree with today's repository"*). The roadmap would be a second copy of a detail whose
canonical home is elsewhere — `RFC-756`'s failure, already live in the same WK-697 row this close
had to correct. The active plan gets a **pointer, not a copy**, appended dated under its own
`Corrections after filing` section, so the figure lives in one place.

## Why the id waited

W37-5c's closure record adopted this disposition before the id existed, and **deliberately did
not mint one**. `F88` limb 3 records two executors filing different findings as `F87` within an
hour on 2026-09-02, each having computed the next free id from `main` correctly, neither able to
see the other's unmerged PR, with no allocator. Allocating an id the lead had not directed is
that incident seen from the other side. **`F92` was verified free before use** — absent from
`origin/main` and from this branch (`git grep -n "F92" origin/main -- docs .claude`, and the
same at `HEAD`), with `F91` the highest allocated.

## Falsifiable

Discharged when a **single document a W37-6 planner reads** names the population, its cause and
its owner together — the register row plus the active plan's pointer to it — **and** the join to
the frozen plan's item 13 is stated, so the two descriptions of one population resolve to each
other. Not discharged by the 53 being stamped: stamping removes the population, and the next
deferral recorded only in a commit body would be unprotected. Re-opened if a later deferral is
disclosed in a merge body without a register row.
