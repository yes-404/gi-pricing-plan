---
id: FD-9641
family: finding
title: The requirement anchors document-ids.md §1.4 line 71 requires exist in no spec, so a requirement deep link does not resolve
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: 83ea509023d6d705d6f78fe74b7124fdf1375739
corrected_by: []
relates: [WK-1178, RFC-937, FR-451]
---

# FD-9641 — `document-ids.md` line 71 requires `<a id="fr-<n>">` anchors that no spec carries

**Filed under working id 9641.** Raised by the maintainer (by delegation)'s ID AUDIT of 2026-10-05 14:15:12 BST
(`~/gi-pricing-plan.local/channel/to-lead.md`, local, not in the repo, entry headed "2026-10-05 14:15:12 BST — ID AUDIT …"). The `tree:` is
`origin/main` at `83ea5090`; every locator below was read at that tree. **Severity LOW and owner WK-1178**, ruled by the maintainer (by delegation) in that entry ("FD 9641 (LOW, WK-1178 …)") and again in the entry headed "2026-10-05 14:21:22 BST — DECISIONS 35–38 …; FD 9641 noted" ("LOW as proposed"); the remedy choice goes to WK-1178's backlog and is not ruled; the lead gives the verdict at the mint.

## Finding

### The rule

`docs/process/document-ids.md:71`, verbatim:

> A row family's id resolves to a file *and an anchor* (`docs/specs/02-modelling.md#fr-<n>`,
> `docs/roadmap.md#wk-<n>`); a document family's id resolves to a file. Roadmap rows are
> headings, so their anchors exist; requirement rows are bold ids in tables, so `spec-change`
> emits `<a id="fr-<n>"></a>` before each definition and the migration adds one for every
> existing clause. `INDEX.md` has one row per number for both.

The same text is `RFC-00937-…md:65` (there with the example ids `fr-1187` and `wk-1201` in place of `<n>`).

### The measurement

`git grep -c '<a id="fr-' origin/main -- docs/specs` prints nothing and exits **1** (no match
in any file): **0 anchors in `docs/specs/`**. `git grep -c '<a id=' origin/main -- docs`
finds one match in each of two files, `docs/process/document-ids.md` and the RFC-937 file —
the sentence above, quoted in each; neither is an anchor in a spec.

Three claims in the quoted sentence are false at this tree:

1. **"the migration adds one for every existing clause"** — it did not; no spec carries one.
2. **"`spec-change` emits `<a id="fr-<n>"></a>`"** — `.claude/skills/spec-change/SKILL.md`
   has no match for `a id=` or `anchor`; it does not emit them.
3. **"Roadmap rows are headings, so their anchors exist"** — they are headings
   (`docs/roadmap.md:198`, `### WK-657 — Repo foundations: …`), but a GitHub heading anchor
   carries the whole heading text (`#wk-657--repo-foundations-…`), so `#wk-<n>` alone does
   not resolve either. Read from the heading form and GitHub's slug rule; **not tested in a
   browser**.

## Evidence

### No existing finding

`docs/findings/register.md` has no row about requirement anchors (its only `anchor` hits are
unrelated). Searching `docs/findings`, `docs/rulings`, `docs/rfcs`, `docs/plans`,
`docs/closures` and `docs/open-questions.md` for `a id="fr-`, `requirement anchor` and
`fr-<n>` found only the RFC-937 text and two plans' unrelated `req("FR-<n>")` pytest-marker
text. No open PR's title or body matches (`gh pr list --state open`, 100 most recent).

### What breaks

A deep link to a requirement — `docs/specs/02-modelling.md#fr-<n>` — does not land on the
requirement: the target does not exist, so the browser opens the file at the top.

**What does not break, read in `scripts/`:** nothing in `scripts/audit-docs.py`,
`scripts/doc-index.py`, `scripts/_docid.py` or `scripts/doc-id.py` reads an `fr-` anchor (a
search for `a id`, `#fr` and `fr-` in the four files found none that concern one);
`INDEX.md`'s columns are `id | family | kind | title | status | owner | phase | execution`,
with no anchor or link column; and `git grep -E 'docs/specs/[0-9a-z-]+\.md#' -- docs
':!docs/INDEX.md'` finds no existing link to a spec anchor. **So no gate fails and no
current link is broken.** The harm is the unmet promise: `document-ids.md` and RFC-937 state
a resolution the repository does not provide, and a future link or tool built on that
statement would fail silently. Not searched: the frontend and `.claude/` prose for such
links.

## Disposition

Re-read at `origin/main` 809a3794, 2026-10-05: `document-ids.md:71`, RFC-937 `:65`, `docs/roadmap.md:198`, the 0-anchor measurement (rc 1) and the `spec-change` skill's lack of `a id=` or `anchor` all hold unchanged.

### Remedy, proposed, no pick

- **A. Honour the rule.** `spec-change` emits `<a id="fr-<n>"></a>` before each new
  requirement definition, plus a one-time migration that adds one per existing clause
  (every FR, NFR, DEP and OQ row id in the specs), and a check that every requirement id in
  `INDEX.md` has its anchor.
- **B. Amend line 71** (and say so in the same commit, per `CLAUDE.md` §5's append-only
  rule for ids — this is prose, not an id) to what is true: requirement ids resolve to the
  file and the row id as text, and name no `#fr-<n>` anchor; fix the roadmap clause to the
  actual heading slug.

A is the larger change: it touches every spec row and needs a migration. B changes one
paragraph and leaves deep links unavailable. The choice is the lead's; if it is a design
choice between the two, `CLAUDE.md` §0 sends it to `docs/open-questions.md`.

**Disposition:** `fix before close with an owner: WK-1178`, severity and owner ruled as above; the lead gives the verdict at the mint. The remedy choice above is not made here.
