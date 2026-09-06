---
id: RFC-897
family: proposal
kind: process
title: File taxonomy, reference coding, and custody investigation (rev 2)
status: draft                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-08-30
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this RFC itself corrects a frozen record
relates: []                     # ids only
was: docs/notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md
---

# File taxonomy, reference coding, and custody investigation (rev 2)

One-line thesis: the repository's document population has grown by local convention —
one flat `docs/plans/` holds at least eight undeclared types, 34 % of its files are
referenced by nothing, and the project's design memory (the NT notes) lives in `.claude/`,
blurring the boundary between project documentation and agent configuration on a public
repository — so: fix a closed category set with a home-by-consumer boundary rule, give
each category a reference standard, map each to an owning role, and audit whether every
category is genuinely created-read-retired by the workflow rather than merely
accumulating.

## 0. Opening evidence (measured at `7db62ca`, commands in §9)

- 238 files under `docs/`, 421 under `.claude/`; `docs/plans/` is the epicentre with 113.
- Hidden types in `docs/plans/` by name-suffix census: 16 `*-ledger`, 18 `*-ruling(s)`,
  4 `*-slice-map`, 4 `*-closure`, 3 `*-revised*`, plus remediation / review / recovery /
  direction / correction / addendum — **≥ 8 de-facto types, zero declared**.
- **38 of 113 plan files (34 %) are referenced by no other tracked file.** Some are
  legitimately terminal (a frozen leaf plan may be cited only by SHA-anchored closure
  records); the number is a question, not yet a verdict — Stage 4 turns it into one.
- Precedent findings of exactly this shape already in the register: F31 (a published file
  nothing true derives), F28-P5 (a procedure no document owns), RFC-778 (deferred items
  with no durable custody), RFC-756 (duplicated status goes stale).
- **The boundary evidence (rev 2):** the NT notes — the project's design memory, cited by
  CLAUDE.md §13 and six register rows — live in `docs/notes/`, a directory whose other
  contents (roles, skills, agents) are agent-runtime configuration. On a public
  repository this misfiles the most reader-worthy documents under tool config. The move
  is not free: **28 tracked files cite `docs/notes/` paths** — 7 frozen plans, 7
  intra-notes cross-references, 4 skills, CLAUDE.md, 2 process docs, 2 audit docs, and
  three pieces of *mechanism*: `.github/workflows/docs.yml`'s path filter names
  `docs/notes/**` because `scripts/audit-docs.py` checks 16–20 audit that directory,
  and `tests/test_audit_docs_finding_citations.py` pins it. A naive `git mv` would
  silently un-watch the notes — F26's gap, self-inflicted. (Register citations by bare
  `NT-00NN` id — 6 in the register alone — survive any move; path citations do not,
  which is itself an argument Stage 2 should adopt: cite notes by id, resolve via index.)

## 1. Design constraints (rulings to inherit, not re-litigate)

- **C1 — No retro-renames of cited artifacts.** Paths are citations: the register, rulings
  and closure records cite `docs/plans/...` paths throughout. Mass-renaming has the same
  blast radius as the F49 history rewrite — every citation dangles. The standard is
  **prospective**; legacy is indexed, never moved. (Same verdict class as F49:
  accept-with-instrument, not rewrite.)
- **C2 — No new id families.** `work-item-close.md`: "No new id family is minted."
  Categories reuse NT / W / F / OQ / ADR / Ruling / FR-NFR ids; the taxonomy names types,
  not new numbering schemes.
- **C3 — Ownership is derived from charters, not invented.** CLAUDE.md §12's grounding as
  quoted in `auditor.md`: "a role writes the artifacts its own charter names." A category
  no charter names is a *finding*, and assigning it is the decision-maker's, not this
  investigation's.
- **C4 — Frozen means frozen.** Plans and closure records are write-once; categorisation
  annotates around them (index file), never edits them.
- **C5 — Home is determined by consumer (rev 2).** `.claude/` is for what the agent
  runtime consumes (roles that spawn members, skills the tooling discovers, settings);
  `docs/` is for what the process and human readers consume. Applied: roles and skills
  **must stay** in `.claude/` — Claude Code's skill discovery reads that path, so moving
  them breaks tooling for cosmetic gain — while the NT notes are consumed by readers and
  citations, never by the runtime, so they belong under `docs/`. This principle decides
  every category's home column in §3, not just the notes'.

## 2. Stage 0 — Census (mechanical, one session, read-only)

Build `scripts/file-census.py` (C-class: deterministic, no LLM): for every tracked file
emit path, area, normalised name pattern (dates→DATE, numbers→N), size, mutability guess
(frozen / living / generated — from directory + header markers), and **referenced-by
count** (tracked files citing its basename or path, self excluded). Output one CSV +
a summary table, committed under `docs/audit/` as the investigation's evidence base,
stamped with the tree. Re-runnable — this script later becomes the drift check (Stage 5).

**Parallelism note:** this stage is read-only evidence gathering — the §8 carve-out
(`dispatching-parallel-agents`) applies; fan out freely.

## 3. Stage 1 — Taxonomy (the "determined category" question)

Cluster the census into a **closed** candidate set. Working hypothesis from §0 (to be
confirmed or amended by the data, not assumed):

| Candidate category | Mutability | Today's home |
|---|---|---|
| spec | living, §amended | docs/specs |
| plan (map / leaf) | frozen; dated revisions | docs/plans |
| rulings record | write-once-amend | docs/plans (mixed in) |
| ledger | append-only | docs/plans (mixed in) |
| closure / audit record | write-once | docs/audit/work, docs/plans (both!) |
| register + findings | write-once-amend | docs/audit |
| research note | frozen + correcting annotations | docs/research |
| ADR | immutable, superseded-by | docs/adr |
| contract (hand vs generated) | generated tier vs authored | docs/contracts |
| process / charter / skill | living | docs/process, .claude |
| note (NT) | frozen proposal | **docs/notes** (moved from `.claude` by §3a, C5) |
| workflow journey | living | docs/workflows |

Deliverable: a one-page taxonomy doc — each category: purpose, mutability class, home,
id family (C2), and the rule *"a new file that fits no category is a lint failure"*
(prospective only). The set is **ruled closed by the decision-maker**; adding a category
thereafter is a note, not a habit.

Known tension to rule on, surfaced by §0: closure material lives in **two** homes
(`docs/audit/work/**` records vs `docs/plans/*-closure*.md`) — one category, one home,
prospectively.

### 3a. The one permitted retro-move: notes to `docs/notes/` (rev 2)

C1 forbids retro-renames *in general*; this subsection defines the single exception and
why it clears the bar: the notes are the only category whose current home misrepresents
them to the repository's new public audience (C5), the id family already survives the
move (citations by `NT-00NN` id are path-independent), and the citation surface is fully
enumerated (§0) — 28 files, of which only 7 are frozen. The move is one atomic PR:

1. `git mv` the notes directory out from under `.claude` to `docs/notes` (history
   preserved).
2. **Living citations updated in the same PR** — CLAUDE.md, skills, process docs, audit
   docs, agents, `.gitignore`, and the three mechanism files together: `docs.yml`'s
   `paths:` filter, `audit-docs.py`'s checks-16–20 root, and the citation test. Note the
   filter simplifies: `docs/notes/**` is already inside `docs/**`, so the explicit notes
   entry is deleted rather than rewritten — with a comment saying why, so F26's
   archaeology never repeats.
3. **Frozen citations are not edited** (C4). Instead `docs/rfcs/README.md` remains as
   a tombstone: one paragraph and the old→new mapping, so any frozen plan's citation
   still resolves for a reader — RFC-777's own test ("would it still resolve for a reader
   holding none of your context") satisfied by redirection rather than rewriting history.
4. Acceptance within the PR: `grep -r '\docs/notes/' --exclude-dir=.git` returns
   exactly the tombstone and the 7 frozen files, zero others; a docs-only PR touching
   `docs/notes/**` triggers the docs workflow (proven by the PR itself); checks 16–20
   run green against the new root.

Sizing: one slice, but it must be scheduled at a gap — it touches CI filters, and F40's
lesson (register PRs merged mid-gate killed runs) applies doubly to workflow-file PRs.

## 4. Stage 2 — Reference coding standard

Per category: filename grammar (`DATE-<id>-<slug>.md` where dated; `<id>-<slug>.md` where
not), header block (category name, status, supersedes/superseded-by, verified-tree where
applicable), and citation form. Then:

- `docs/INDEX.md` (or per-directory index): **legacy mapping** old path → category, so
  the standard covers 100 % of files without moving one (C1).
- `scripts/file-lint.py`: new/renamed files must parse to a category grammar; legacy
  paths exempt via the index. Wire into the gate (CLAUDE.md §11 command list), warn-then-
  red with a dated flag-day (RFC-895 Q3's posture).
- Update the creating skills (`writing-plans`, `close-workstream`, `phase-review`,
  `adr-write`, `spec-change`) to emit the standard — the skills are where files are born,
  so they are where the standard binds (one source).

## 5. Stage 3 — Ownership map

A category × role matrix: **creates / amends / retires**, derived from the seven role
charters + maintainer (C3). Every cell cites the charter line that grants it. Empty rows
— a category no charter owns — and empty columns — a role owning nothing it's charged
with — are filed as findings (register rows per RFC-896's grammar, decaying to the §14
review if unowned). Expected hits, from precedent: the stand-down procedure (F28-P5),
roster state (F31), and whatever the 38 unreferenced plans turn out to be.

## 6. Stage 4 — Workflow-loop audit (the "in deed loop" question)

For each category, establish its **lifecycle triple** from the process spec + skills:
which step *creates* it, which step *reads* it, which step *retires or supersedes* it.
Evidence: census referenced-by data + grep of `delivery-process.md`, checklists, and
skills for the category's home path. Verdicts per category, four possible:

1. **Looped** — created, read, retired by named steps. Done.
2. **Write-only** — created by a step, read by nothing (F31's shape). Finding: either a
   reading step exists and must name it, or the category is retired.
3. **Read-only-in** — consumed but no creating step owns it (ad-hoc births). Finding:
   assign the creating step/skill.
4. **Terminal-by-design** — frozen records cited only at creation (some of the 38).
   Acceptable, but *declared* in the taxonomy so it never reads as abandonment.

The 38-of-113 number gets decomposed into verdicts 2 vs 4 here — that decomposition is
the single most informative output of the whole investigation.

## 7. Stage 5 — Migration and enforcement

- Prospective standard live from the flag-day (Stage 2).
- Legacy migrates **opportunistically-on-amendment only** (RFC-896 P4's rule) — a file is
  re-homed/renamed only when a change already touches it AND nothing frozen cites its
  path; otherwise the index carries it forever. Never a bulk-rename slice (C1).
- `file-census.py` re-runs at every phase close; growth in category "none" or verdict-2
  files is a red flag in the phase review.

## 8. Shape, sequencing, sizing

Stages 0–1: one investigation session each (read-only fan-out legal), producing the
census + taxonomy draft → **reconcile**: decision-maker rules the closed set, the
two-homes tension, and §3a's exception with Q5–Q7 → Stages 2–3: one Work, ~5 slices
(**S0 = the §3a notes move**, first because it's self-contained, its acceptance is fully
mechanical, and every later slice then writes `docs/notes/` paths; then lint + index;
skills; ownership matrix; findings filed) → Stage 4: one audit slice with the
fresh-context auditor → Stage 5: riders on the gate + phase-close checklist.
Dependencies: 1 needs 0; §3a needs only the reconcile ruling; 2 and 3 are independent
after 1; 4 needs 0's data and 3's matrix; 5 needs 2. Cross-reference: RFC-898's README
tour should point at `docs/notes/` — if RFC-898's Work lands first, its README cites the
old path and S0 updates it as a living citation (step 2), so the two notes compose in
either order.

Not in scope: code-file conventions under `backend/ packages/ frontend/` (owned by the
language skills and ruff/mypy already — different mechanism, already enforced), and the
generated contracts tier (owned by F27(c)'s gate-coverage item — do not double-own).

## 9. Reproduce the opening evidence

```bash
find docs .claude -type f | wc -l                     # populations
ls docs/plans | sed -E 's/2026-..-../DATE/;s/[0-9]+/N/g' | sort | uniq -c | sort -rn
ls docs/plans | grep -oE '(rulings?|ledger|slice-map|closure|revised|remediation|review|recovery|direction|correction|addendum)' | sort | uniq -c
for f in docs/plans/*.md; do b=$(basename "$f"); \
  n=$(grep -rl --exclude-dir=.git "$b" . | grep -v "^\./$f$" | wc -l); \
  [ "$n" -eq 0 ] && echo "UNREFERENCED $b"; done | wc -l   # 38 at 7db62ca
```

## 10. Open questions (decision-maker, at reconcile)

- Q1 — Is the taxonomy's closed set ruled per §3's table, amended, or rebuilt from the
  census? (Recommendation: rule on the census-clustered set, not the hypothesis.)
- Q2 — One home per category prospectively: where do rulings records and ledgers live —
  stay in `docs/plans/` with the grammar carrying the type, or split directories?
  (Recommendation: grammar-in-place; splitting multiplies C1 exposure for no reader gain.)
- Q3 — Verdict-4 declaration form: a `terminal` marker in the index, or a category
  attribute? One rule before Stage 4 files verdicts.
- Q4 — Does the ownership matrix live in `docs/process/` (living) or as an NT appendix
  (frozen)? (Recommendation: living, in process/ — it must track charter amendments.)
- Q5 (rev 2) — Destination: `docs/notes/` (recommended — the family keeps its name and
  its README), or fold into an existing docs family? Not `docs/adr/` — ADRs carry
  supersede semantics notes deliberately lack, and merging families violates C2's spirit.
- Q6 (rev 2) — Tombstone form: a README mapping (recommended — renders on GitHub,
  survives tooling) vs git symlinks (render poorly on github.com, and a symlinked
  directory would silently re-include notes under `.claude/` for path-scanning tools).
- Q7 (rev 2) — Prospective citation rule: cite notes by `NT-00NN` id resolved via the
  Stage-2 index (recommended — id citations survived this very move; path citations are
  what made §3a cost 28 files), or continue full paths? Rule once, before Stage 2's
  grammar lands.

## 11. Acceptance standard (draft)

Complete when: **(a)** the census script runs green in the gate and its output at the
close tree is committed; **(b)** every tracked file under `docs/` and `.claude/` resolves
to exactly one category via grammar or index — measured, count named; **(c)** the
category × role matrix has no unfiled empty row; **(d)** all 38 unreferenced plans (as
re-measured at the close tree) carry a verdict-2 finding or a declared verdict-4;
**(e)** `file-lint.py` red on three deliberately broken fixtures (uncategorisable name,
missing header, undeclared new category) — enforcement proven on broken input;
**(f)** one new file of each high-traffic category (plan, rulings, ledger) has been born
through the updated skills; **(g)** (rev 2) the §3a move's own acceptance holds at the
close tree — the old-path grep returns exactly the tombstone plus the 7 enumerated frozen
files, checks 16–20 run green against `docs/notes/`, and a docs-only notes PR has
demonstrably triggered the docs workflow. Each item names command, totals, tree.
