# ADR-0001 — Example fixtures stay dependency-free

- **Status:** accepted
- **Date:** 2026-08-11
- **Deciders:** maintainer
- **Related:** FR-EX-1

## Context

A worked example of the legacy ADR bullet header that `doc-id.py migrate` converts to front
matter, in order, per NT-0019 §4 step 5: the bullet block is removed, a YAML front-matter
block is added in its place, and everything from the first `##` heading onward is kept
byte-for-byte (aside from citation-token rewrites).

## Decision

Fixture ADRs carry no real decision — this file exists only to give the migration script a
correctly-shaped legacy ADR to convert.

## Consequences

None outside this test corpus.
