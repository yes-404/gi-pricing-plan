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
---

# <Title>

<Body appropriate to what this Reference is — a process document's numbered sections,
a charter's role definition, a skill's SKILL.md, a README's map. NT-0019 does not
prescribe this family's body shape; only its header and its exemption from an id.>

<!--
Vendored skill detection (§1.5): a vendored skill (`planning-with-files`,
`ui-ux-pro-max`, `graphify`, `systematic-debugging`, the `vue-*` skills — any directory
under `.claude/skills/` holding a `LICENSE` file that is not the repository's own)
carries two extra fields on its `SKILL.md` only, declared here and nowhere else:

    vendored: true
    origin: <upstream project name and URL>

The files beneath a vendored skill are exempt from stamping, citation rewrite and shape
checks — `doc-id.py`'s detection rule (`grep`-able: any directory holding a `LICENSE`
that is not the repository's own) is what decides this, not a hand-kept list.
-->
