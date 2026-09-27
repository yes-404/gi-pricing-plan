---
id: RL-947
family: ruling
title: Q6: tombstone form is a README mapping; symlinks are rejected
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-01
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md
---

## RL-947 — Q6: tombstone form is a README mapping; symlinks are rejected

### 1. Verified first, at `b2fb122`

| Claim | Verdict |
|---|---|
| `check_notes` (checks 16–20) guards on `NOTES.is_dir()` and globs `NOTES.glob("*.md")` | **Confirmed** — `scripts/audit-docs.py:281` and `:295` (`:235`/`:249` at `b551060`; the constant itself moved from `:52` to `:66` — line numbers only, no behaviour change) |
| a `pathlib.Path.is_dir()` / `.glob()` call resolves through a symlink | **Confirmed by inspection of the code path** — nothing in `check_notes` or `check_finding_citations`'s `scan_dirs` (`:551-552`, current tree) distinguishes a real directory from a symlinked one; both satisfy `is_dir()` and both glob successfully |
| `scan_dirs` at check 25 already lists the notes root alongside two `docs/` directories in one list | **Confirmed** — see RL-946 §1, same line |
| the note's own text names the same disqualification independently | **Confirmed** — `.claude/rfcs/0016-…md:236-237`: symlinks "render poorly on github.com, and a symlinked directory would silently re-include notes under `.claude/` for path-scanning tools" |

### 2. Ruled

**Chosen: a `README.md` mapping at the vacated `.claude/notes/` path. Rejected: a git
symlink.**

The disqualification is mechanical, not stylistic. A symlinked `.claude/notes` pointing at
`docs/notes/` would keep resolving for every tool in this repository that checks directory
existence and globs for `*.md` — which is exactly what `audit-docs.py` does, at both the
checks-16–20 root and the check-25 scan. That means both paths would go on being "real" to
every consumer indefinitely: the old path never stops working, so nothing forces the 13
living citations (§1a of the plan) to ever migrate, and a future contributor citing either
path is equally correct. That is the two-homes ambiguity the move exists to end, recreated by
the tombstone meant to close it. A plain-text `README.md` has no such property: it is not a
directory, so `is_dir()` on the old path returns false, `check_notes` correctly reports
absence (and, once Slice 1 lands, fails loudly rather than skipping silently — see the
plan's §1b and §6), and a reader or tool landing on the old path gets one paragraph and an
explicit old→new mapping rather than a second live copy of the directory.

This question is purely mechanical and does not depend on Q1.

### 3. What it obliges

Slice 4 Step 6 writes `.claude/rfcs/README.md` as a tombstone: one paragraph plus the
old-to-new mapping, exactly as the plan's §9 describes. No symlink is created at any point in
the slice.

**Overridden if** a future slice creates a symlink, junction, or any other mechanism that
makes the old path continue to resolve as a directory.

---
