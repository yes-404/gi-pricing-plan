# ADR-0001 — Example fixtures stay dependency-free

- **Status:** accepted
- **Date:** 2026-08-11
- **Deciders:** maintainer
- **Related:** FR-EX-1

## Context

A worked example of the legacy ADR bullet header that the migration script converts to
front matter: the bullet block is removed, a YAML front-matter block is added in its
place, and everything from the first `##` heading onward is kept byte-for-byte (aside
from citation-token rewrites). This decision follows on from the note discussed in
`NT-0001`, a second worked example of a citation elsewhere getting rewritten once its
own target is renumbered.

## Decision

Fixture ADRs carry no real decision — this file exists only to give the migration script a
correctly-shaped legacy ADR to convert.

## Consequences

None outside this test corpus.
