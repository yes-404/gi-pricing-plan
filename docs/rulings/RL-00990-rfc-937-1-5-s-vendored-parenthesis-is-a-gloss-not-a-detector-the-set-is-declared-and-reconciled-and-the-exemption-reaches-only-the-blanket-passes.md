---
id: RL-990
family: ruling
title: RFC-937 §1.5's vendored parenthesis is a gloss, not a detector: the set is declared and reconciled, and the exemption reaches only the blanket passes
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-migration-preconditions-rulings.md
---

## RL-990 — RFC-937 §1.5's vendored parenthesis is a gloss, not a detector: the set is declared and reconciled, and the exemption reaches only the blanket passes

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
| The ruff exclude list is therefore the right criterion | **Refuted, and this is the finding the report did not reach.** Nine of the 28 carry a change row in RFC-937 §5.4: `brainstorming`, `executing-plans`, `graphify`, `planning-with-files`, `requesting-code-review`, `secret-hygiene`, `subagent-driven-development`, `testing-strategy`, `writing-plans`. **Two of those nine — `writing-plans` and `subagent-driven-development` — are primary creating instruments** that RL-987 places in W37-6's commit. Adopting the ruff list as `is_vendored` would exempt them from the migration entirely, which collides head-on with RL-987 |
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
RL-987 requires in W37-6's commit. It is also authoritative for a different purpose — lint
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
deviation from *"as upstream wrote them"*. RFC-937 §1.5 mandates it, and the maintainer's
precedence ruling of 2026-09-01 makes RFC-937 outrank current practice. A rule that yields
still yields visibly: it is recorded in `.claude/skills/README.md` **once, as a class covering
all 28**, not 28 times.

### 3. What it obliges

- W37-2 replaces `is_vendored`'s body with the membership test and keeps its signature; the
  constant lands with it.
- W37-4 adds the reconciliation check against the ruff exclude list, with its own broken-input
  proof.
- W37-6 applies the nine §5.4 rows as deliberate edits and lands the README entries in the same
  commit. Two of the nine are also RL-987's creating instruments, so they are in that
  commit for two independent reasons.
- **Nothing in `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` is edited.** §1 stays byte-identical to
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
- **Any change to RFC-937 §2's D0–D14, or to §1's text.** None is made. RL-990 resolves a
  §1.5 contradiction entirely inside the implementation for exactly this reason.
- **DP-4 and DP-6** are untouched. DP-4 is non-blocking and resolves at W37-11; DP-6 concerns
  amendments to `CLAUDE.md`'s own requirements, which §12 reserves to the maintainer and which
  no delegation this record relies on reaches.

## Provenance

Written 2026-09-02 by the decision-maker role. Every claim in each `### 1.` table was checked
against the repository at `04ec6bf` in this session, by the command named beside it; none was
taken from the lead's relay, and three of the plan's stated grounds were found wrong and are
recorded as such rather than repeated — the 767-file figure (RL-988), the reason option (b)
fails (RL-988), and the reason option (c) fails (RL-989). The delegation under which
DP-1 and DP-2 were ruled is quoted in the Authority section above with its date; the maintainer
did not rule these personally.
