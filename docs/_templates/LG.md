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
extra: no template declares it, so it is not permitted (RL-981,
`docs/rulings/INDEX.md#2026-09-02-w37-field-set-and-rollup-rulingsmd`). A ledger's PR list lives in
the `## PRs` body section below, which is what §1.9's PR-title lint reads.

**Lean P2, L1 (a')** (amended 2026-10-08 by the maintainer (dated line by delegation), on RFC-9479 P6),
for every slice whose GO follows the maintainer's entry "2026-10-08 11:51:58 BST — USER
DECISION: LEAN P2 items 1, 3 and 5 APPROVED; IN PRACTICE NOW; the files are amended through
RFC 9479 P6 (the maintainer's amendment, by delegation)", as corrected by "2026-10-08 12:02:08
BST — #1240 P6 flagged readings RULED: (1) REJECTED, and my 11:51:58 L1 (a) wording CORRECTED
(the slice's one file is its LG-, not text under the roadmap row); (2) ACCEPTED": **this ledger
is the slice's one paperwork file.** The slice is one PR carrying the code, the tests, any spec
change, its one-line `SL-` roadmap row status change, and this file, with the five sections
below (`###` under `## Tasks`): Scope, Task list, Gate, Audit, Build log. There is no per-slice `PL-`, no dispatch `RL-` and
no activation PR. `plans:` names the Work's one plan and any delta that adds this slice. The
`## PRs` section stays, because the PR-title convention reads it.
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

**GO:** <the maintainer's GO header from `to-lead.md`, quoted verbatim, with its conditions.>
**MERGE-ACK:** <the MERGE-ACK header, quoted verbatim, added at merge.>

## Tasks

<From Lean P2 L1 (a'), this section holds the slice's five parts as `###` headings. They are
`###`, not `##`, because `audit-docs.py` check 37 requires every `##` heading of this template
in every ledger, including the ledgers written before L1; at `##` they would red all of them.>

### Scope

<The slice's row in its Work's plan, quoted verbatim with the plan's id and the row's heading
(L5: one plan per Work, slices as rows). Every requirement id it covers, listed. Any dispatch
record `delivery-process.md` §8 requires (a same-Work pair) is written here.>

### Task list

<One entry per task, in order, each naming the plan step it discharges and its acceptance
check.>

### Gate

<The full local gate's rc table at the slice PR's head: each command, its exit code, the tree
it ran on, and the failing excerpt if any.>

### Audit

<The slice audit, written by the auditor (`CLAUDE.md` §13, unchanged in substance): scope from
the spec, the four verdicts, NFRs measured, broken-input proofs, and the tree it ran on.>

### Build log

<Appended per task and per push, never rewritten: each entry dated, naming its commit.
Rulings inside the slice are entries here, with their date.>

## PRs

<The PR list `doc-id.py`'s GitHub-alignment convention expects (§1.9): number, title,
merge commit. This is what a merged PR's `SL-`-naming title gets checked against.>
