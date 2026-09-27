<!--
TEMPLATE — Reference: `process/`, `contracts/`, every `README.md`, `.claude/roles/`,
`.claude/skills/*/SKILL.md`, `.claude/agents/` (§1.2). Reference carries no prefix and
no number — it has no `id:` field, and is cited by path, never by `<PREFIX>-<n>`.
Fill in every placeholder, delete this comment block, and remove any field this
document does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `kind:`, `phase:`, `work:`, `slice:`,
`plans:`, `supersedes:` and `superseded_by:` do not apply to this family and must not
appear here — a Reference document has exactly two states, `active` and `retired`.
`owner:` is whichever of §1.6's five roles the document names: amendments to
`process/` arrive as an `RFC-` + `RL-` pair (§1.6); a charter's insufficiency is filed
as an `FD-` that the maintainer amends against; a skill's or agent's owner is whichever
role §1.6 assigns it.

A **generated** Reference document (a rendered contract, a generated index) carries
`generated: true` instead of a hand-authored body and is never hand-edited.

Four further keys — `name:`, `description:`, `tools:` and `model:` — are the Claude Code
harness's own front matter for a file it consumes directly: `.claude/agents/*.md` and
`.claude/skills/*/SKILL.md`. They are declared here, in this block, because RL-981 makes
the template the licensing instrument for a family's permitted fields — a commented block
elsewhere in this file is not read by `derive_field_policies` (RL-1140 DP-8.1 §2). They are
**permitted, never required**: `required = _CORE_HEADER_FIELDS ∩ permitted`, and none of
the four is core. A file merging them keeps them first, byte-identical, with the governed
keys inserted after.
-->

---
family: reference
title: <one line — what this document is a reference for>
status: active                  # active → retired (§1.2a)
created: YYYY-MM-DD
owner: maintainer                # whichever of §1.6's five roles the document names
tree: <commit-sha this was written against>
corrected_by: []
relates: []                      # ids only
name: <the Claude Code harness's own key — agent/skill files consumed by the harness only>
description: <ditto — harness key>
tools: <ditto — harness key, agent files only>
model: <ditto — harness key, agent files only>
---

# <Title>

<Body appropriate to what this Reference is — a process document's numbered sections,
a charter's role definition, a skill's SKILL.md, a README's map. RFC-937 does not
prescribe this family's body shape; only its header and its exemption from an id.>

<!--
Vendored skill detection (§1.5): a vendored skill carries two extra fields on its
`SKILL.md` only, declared here and nowhere else:

    vendored: true
    origin: <upstream project name and URL>

The files beneath a vendored skill are exempt from stamping, citation rewrite and shape
checks. Which skills count is a hand-kept list, not a filesystem property: shipping a
`LICENSE` is neither necessary (most vendored skills ship none) nor sufficient (the
repository's own root `LICENSE` does not make everything beneath it vendored) — RL-990
rejected that detection rule. The list itself is `scripts/_docid.py`'s `_VENDORED_SKILLS`
constant, seeded from `.claude/skills/README.md`'s provenance sections and reconciled
there against `pyproject.toml`'s `[tool.ruff] exclude` list so the two cannot silently
drift apart.
-->
