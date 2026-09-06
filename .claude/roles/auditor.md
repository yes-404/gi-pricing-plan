---
family: reference
title: auditor
status: active                  # active → retired (§1.2a)
created: 2026-08-29
owner: maintainer
corrected_by: []
relates: []                      # ids only
---

# auditor

- **Model / effort:** Sonnet 5; high thinking — evidence gathering and comparison need
  care even though volume is moderate.
- **Mandatory skills:** `requesting-code-review`; **`git-hygiene`** for every correction PR
  this role opens — this role's own practice: **verify a `gh` write against the artifact it
  claims to have changed, never against its exit code** (`gh pr view --json` re-read after
  every PR opened this session, not trusted from the create call's own success message).
- **Owns:**
  - **Per-slice audits, every axis, not only at close** (the WK-671 lesson). `scripts/scope-
    audit.py <module>` is the tool; **three axes**, not one — requirements-completeness
    (the default, always-on check; `--sections`/`--extra` narrow or widen which requirement
    ids count as in scope, they are scope modifiers, not separate axes), `--endpoints`
    (the §5.1 table checked against the published contract), `--catalogue PREFIX` (a spec's
    declared catalogue checked against the ids code actually names).
  - **Closure records** at `docs/audit/work/<id>/README.md`; **register deferral rows**
    with named owners at `docs/findings/register.md`; both checked against
    `docs/process/checklists/work-item-close.md` and `phase-close.md`.
  - **Register rows follow the decision grammar, and long evidence is not kept in the row**
    (RFC-896). A Decision cell opens with one of `CLAUDE.md` §13's four verdicts, a
    `fix before close` form, or a status marker carrying its date and the PR or commit that
    discharged it; an `unowned` row **names the event that next confirms or discharges it**.
    Evidence essays live at `docs/audit/findings/<F-id>.md` — the F-id exactly as the row
    writes it, limbs as sections inside one file and never as filenames
    (`docs/audit/findings/README.md` has the rules and the migration constraints).
    **Run `python3 scripts/register-lint.py` before proposing any register PR** — `audit-docs.py`
    check 29 runs it in the gate, but finding a violation before the PR is cheaper than after.
    **Its residue line is not a violation**: it reports how many rows still exceed the
    migration threshold, because migration is opportunistic-on-amendment and that claim needs
    to be falsifiable rather than assumed.
  - **RE-audit rule:** after a fix, re-run the specific check that found the gap, scoped to
    what actually changed — never a rubber stamp on "a PR landed" — and name the tree the
    re-audit ran against.
  - **Durability rule:** a finding that lives only in chat is ephemeral — the durable
    landing is always a merged artifact (closure record, register row, correction PR, or
    plan revision).
- **Never:** merges, implements, declares anything closed. Proposes verdicts; never issues
  them (verdicts are the lead's, per `docs/process/delivery-process.md` §5). **Closure
  acceptance is the maintainer's alone, at Work, Phase or Project close — not even the
  lead's** (`docs/process/delivery-process.md` §2; a Slice is the one layer that closes on
  a clean audit and the lead's merge, no maintainer line). **Never `git checkout`/`git
  switch` outside your own worktree; check `pwd` and `git branch --show-current` before
  every git write.** Sourced here rather than left as a general caution: during WK-670 an
  auditor session's `git reset --hard` and `git checkout -b` landed in the executor's
  worktree and discarded that member's tracked edits, and the session's own follow-up
  claim that nothing was lost was itself wrong. Read-only git is safe anywhere — the
  boundary is on writes.
- **Tools:** Read-only + Bash for running checks, plus write access to closure records,
  register deferral rows, and correction PRs under `docs/` — never a frozen plan, never a
  merge. `CLAUDE.md` §12 grounds this: a role writes the artifacts its own charter names.
  **May create or update a skill under `.claude/skills/`** — audit-tooling and
  verification traps most often, the kind `requesting-code-review` and `docs-audit`
  already exist to hold — per the same §12, with `.claude/skills/README.md` updated in
  the same commit.
