<!--
TEMPLATE — Ledger (`LG-`), one slice's execution record.
Copy this file to `docs/ledgers/LG-<nnnnn>-<slug>.md`, where `<nnnnn>` is the padded
result of `python3 scripts/doc-id.py next`. A ledger is opened by the executor at the
start of a slice and appended to per task and per PR; fill in every placeholder below,
delete this comment block, and remove any field this ledger does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `kind:` and `supersedes:` /
`superseded_by:` do not apply to this family (a ledger is never superseded) and must not
appear here. `plans:` is this family's own field — append-only, never used elsewhere.
`prs:` is **not** a header field, despite §1.5's parenthetical naming it as a ledger
extra: no template declares it, so it is not permitted (Ruling 70,
`docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md`). A ledger's PR list lives in
the `## PRs` body section below, which is what §1.9's PR-title lint reads.
-->

---
id: LG-NNNNN
family: ledger
title: <one line — the slice this ledger executes>
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
created: YYYY-MM-DD
owner: executor
tree: <commit-sha this was written against>
phase: P<n>
work: WK-NNNNN
slice: SL-NNNNN
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
---

# LG-NNNNN — <Title>

## Tasks

<One entry per task, in order, each naming the plan step it discharges.>

## PRs

<The PR list `doc-id.py`'s GitHub-alignment convention expects (§1.9): number, title,
merge commit. This is what a merged PR's `SL-`-naming title gets checked against.>
