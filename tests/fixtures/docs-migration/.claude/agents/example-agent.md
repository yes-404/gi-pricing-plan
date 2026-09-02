---
name: example-agent
description: The fixture's stand-in for the seven real agent definitions, which all carry the harness's own front matter.
tools: Read, Grep
model: haiku
---

This file exists to prove the deferral, not the stamp. `name:`, `description:`, `tools:` and
`model:` are not in NT-0019 §1.5's closed field set, and `_docid.parse_header` reads exactly
one front-matter block per file — so the Reference header has to be **merged** into this
block rather than prepended in front of it, and the keys have to be declared in
`docs/_templates/REFERENCE.md` first. That is W37-6's Task 1, so `migrate` reports this file
by name on `deferred_reference_stamps` and leaves it alone.
