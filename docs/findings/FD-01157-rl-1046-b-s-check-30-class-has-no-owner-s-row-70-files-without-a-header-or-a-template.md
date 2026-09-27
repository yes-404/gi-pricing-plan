---
id: FD-1157
family: finding
title: RL-1046 §B's check-30 class is disclosed without a register row — 70 in-scope files carry no header or no known template
status: active
created: 2026-09-27
owner: auditor
tree: 3749db65eb29fbe95dd46e6b787960fa8386af0b
corrected_by: []
relates: [PL-1144, PL-1073, LG-1139]
---

# FD-1157 — RL-1046 §B's check-30 class is disclosed without a register row — 70 in-scope files carry no header or no known template

Filed by the auditor at 2026-09-27 15:04:42 BST, under the lead's adoption of 2026-09-27 14:58:11 BST
(C11 → a finding filed before the closure record). This is `PL-1144` Scope A item C11. It is
filed in one commit with FD-1154 to FD-1162, before the W37 closure record cites any of
them. That meets condition 1 of the deputy's ruling of 11:16:34 BST: *"a deferred row carries
a register row before it is deferred"*. At `3749db65` the register had no row for this class.

## Finding

`RL-1046` §B classes `audit-docs.py` check 30's failures on RFC-937 §5.1/§5.3/§5.4 content
rows as disclosed and non-fatal, labelled `owner: W37-10`. `RL-1138` ("What it obliges") then
disclosed it as unowned. `PL-1073` §1.4 row S-5 (`:266`, measured at `:312-339`) proposed
*"reassigned, to W37-11"*. `LG-1139:181-183` handed it on as a proposal. `PL-1144` typed it
C11, *deferred with the lead as owner*. No register row ever carried it, so until this record
the deferral had nowhere to live except in plan prose.

The class needs code to discharge. Whether a file is stamped or registered unstampable is
decided by `UNSTAMPABLE_EXEMPTIONS` in `scripts/audit-docs.py`. `docs/INDEX.md`'s header would
be a change to `scripts/doc-index.py`. The skill manifests belong to their owners.

## Evidence

The predicate, verbatim: `python3 scripts/audit-docs.py 2>&1 | grep -c '^  - check 30'`.

- **At `3749db65`** (a detached copy; audit rc 0, every line inside the `DISCLOSED` block): **70**.
  By message:
  - 43 lines read *"family '' has no known template under docs/_templates"*, all under
    `.claude/skills/`.
  - 27 lines read *"no `---` front-matter header found"*: 12 under `docs/research/`, 8 under
    `docs/specs/` and 2 under `docs/process/`, plus one each for `docs/INDEX.md`, the findings
    register, `docs/open-questions.md`, `docs/roadmap.md` and `docs/skills-map.md`.
- **At `4ed1f88`** (`PL-1073:318-324`): **77**. That was 50 no-template lines (43 skills and 7
  agents) and the same 27 no-header lines.
- **The difference is 7, the agent manifests.** They gained `family: reference` in W37-8
  (`6cad8e4d`, #807). So the class shrinks only when an owner stamps its files.

## Disposition

**Deferred with an owner — the lead** (the deputy's adoption of `PL-1144` C11 at
2026-09-27 11:16:34 BST; the lead's adoption of 14:58:11 BST). The event, verbatim from
`PL-1144` Scope A: *"Event: the first slice of RFC-937 §8's charter investigation Work."* The
reading is re-taken at each gate with the predicate above.
