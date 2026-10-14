---
id: RS-1649
family: research
kind: audit
title: Retro slice audits of the eight slices merged on 2026-10-11 without a written audit
status: draft
created: 2026-10-12
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
phase: P2
work: WK-1178
corrected_by: []
relates: [FD-1650, FD-1651, FD-1652, FD-1653, FD-1654, FD-1655, SL-1601, SL-1257, SL-1541, SL-1529, SL-1631, SL-1390, SL-1559, SL-1600, SL-1557, PL-1583, PL-1540, PL-1528, PL-1630, PL-1499, PL-1558, PL-1599, PL-1556, LG-1634, LG-1608, LG-1623, LG-1632, LG-1633, LG-1635, LG-1609, LG-1606]
---

# RS-1649 — Retro slice audits of the eight slices merged on 2026-10-11

*(Minted 2026-10-12 as RS-1649 from working id 9703, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

## Question

Eight slices merged on 2026-10-11 with their `LG-` and `SL-` rows already `closed` and the
`### Audit` section of each ledger reading "Not yet" or empty. Does each merge tree satisfy
its plan's Acceptance Standard, and what does each ledger fail to evidence?

Authority: `to-lead.md` entry "2026-10-11 19:57:42 BST", item 3 (one auditor seat, G2/exit
slices first, each slice against its own plan at its own merge sha, one record, one row per
slice, every finding an `FD-` with an owner, a missing requirement reopens through an `FD-`
and never by editing a closed row). The family is `RS` `audit` (`document-ids.md` §1.6:
"auditor — a bespoke audit's method, evidence and verdicts; files every finding as `FD-`").

## Method

Scope was derived from each slice's plan first (its Acceptance Standard, write set and
closing acts), then evidenced at the slice's squash-merge commit on `origin/main`
(`git show <sha>:<path>`, `git diff <sha>^1 <sha>`, `git grep <pat> <sha> -- <path>`).
Evidence is read, not run: **no test, gate or build was run by this audit**; "MET" means
the named test or text exists at the merge sha and its assert was read where the row says
so, and a result quoted from an `LG-` is marked CARRIED-by-LG. **CI on each PR head was read**
twice: by this audit (`gh pr view <n> --json statusCheckRollup`, `gh run view <id> --log`:
pytest `N passed` with no `failed` line for seven PRs; #1271's run log returned no text)
and by the lead (`gh run list --commit <head>`, from-lead 2026-10-11 20:14:10 BST). CI ran
on each PR head, not on the squash-merge tree.

| PR | PR head | Workflows green (lead's read) | pytest passed (audit's read) |
|---|---|---|---|
| #1271 | 26b78e49 | python, docs, frontend, history-policy | log empty |
| #1272 | 559ed54a | python, docs, history-policy | 5469 |
| #1273 | 71d578ae | python, docs, history-policy | 5497 |
| #1276 | eea1adac | python, docs, frontend, history-policy | 5507 |
| #1278 | 4726e440 | python, docs, history-policy | 5512 |
| #1279 | 64fe7eda | python, docs, history-policy | 5522 |
| #1280 | 418f78e6 | python, docs, frontend, history-policy | 5562 |
| #1281 | 024208de | python, docs, frontend, history-policy | 5604 |

Verdicts below are proposals; the lead adopts, amends or rejects them (`CLAUDE.md` §13).

| Slice | PR | Merge sha (parent) | Plan | Ledger |
|---|---|---|---|---|
| SL-1257 | #1280 | fe80aec6 (3065770c) | PL-1583 | LG-1634 |
| SL-1541 | #1272 | d699a561 (99f22479) | PL-1540 | LG-1608 |
| SL-1529 | #1276 | e3a98c97 (b1cdefb5) | PL-1528 | LG-1623 |
| SL-1631 | #1278 | fbde0f70 (ff0edc39) | PL-1630 | LG-1632 |
| SL-1390 | #1279 | 3065770c (fbde0f70) | PL-1499 | LG-1633 |
| SL-1559 | #1281 | 372fa92a (fe80aec6) | PL-1558 | LG-1635 |
| SL-1600 | #1273 | 02f23b4a (d699a561) | PL-1599 | LG-1609 |
| SL-1557 | #1271 | 99f22479 (14fa6fb3) | PL-1556 | LG-1606 |

## Findings

One row per slice. "A<n>" is the plan's Acceptance item n. Each row ends with the lead's
verdict, quoted from the lead's message of 2026-10-11 (logged at from-lead 20:14:10 BST).

| Slice | Acceptance items | Gaps (audit's proposal) | Closing acts at the merge sha | Lead verdict (team-lead, from-lead 2026-10-11 20:14:10 BST) |
|---|---|---|---|---|
| SL-1257 (#1280) | A1, A2, A4–A8 MET; A3 PARTIAL; A9 CARRIED-by-LG and CI; A10 see closing | A3: no committed migration round-trip test and no "existing `api_keys` rows unchanged" test; the round trip is a slot-script result in the ledger | `LG-1634` and `SL-1257` `closed`; Audit "Not yet run"; MERGE-ACK "not yet given"; PRs "None yet" | `FD-1650`, MEDIUM, WK-674, delivered but untested; A10 goes to `FD-1655` |
| SL-1541 (#1272) | A1–A9, A13 MET; A11 CARRIED-by-LG; A12 PARTIAL | A12: ruff E501 fixed after the local gate, per-file check only; CI green on the PR head. Write-set additions all carried by quoted rulings; `FD-1610` filed for the inliner defect | `LG-1608` `closed`; Audit "Not yet given"; MERGE-ACK "not yet given" | A12 limb to `FD-1655` (ii) |
| SL-1529 (#1276) | A1–A9, A11–A13 MET; A10 PARTIAL | A10: ruff fixes after the local gate, "not re-gated"; plan delta D1 (4 exempt slugs, not 5) only in the ledger and a channel message | `LG-1623` `closed`; Gate table "(not yet run)" above a later record; Audit empty | `FD-1655` (ii) and (iii) |
| SL-1631 (#1278) | (a)–(e) MET, (d) a GUARD not a red; LG lines 1, 4, 5 MET or CARRIED | LG lines 2 and 3 (no money change; NFR-499) not written | `LG-1632` `closed`; no Audit section | Accepted; no finding |
| SL-1390 (#1279) | A1–A3, A5–A7, A10 MET; A4 UNEVIDENCED; A8 CARRIED-by-CI | A4: broken-loop proofs and the base reds of A3/A4/A10 not recorded; `LG-1633` `### Gate` empty | `LG-1633` `closed`; Audit "(Written by the auditor at slice close.)" | `FD-1651`, MEDIUM, WK-673, delivered but untested; the gate-record limb to `FD-1655` (ii) |
| SL-1559 (#1281) | A1–A9, A11–A17 MET by presence; A10 GAP; A18 PARTIAL | A10: the stored-data stop query (RL-1475) never recorded; the slice retyped `rows`/`default_row` and shipped a migration | `LG-1635` `closed`; Gate "Not run." above a real record; GO line stale | `FD-1652`, MEDIUM, WK-675, delivered but untested; discharge is a read-only count; gate limb to `FD-1655` (ii) |
| SL-1600 (#1273) | A1–A5, A7, A8, A11, A12 MET; A6 GAP; A9 PARTIAL | A6: ACK states 28/12 where the plan states 30/10 and 74; reconciled at `02f23b4a` (two lax date types moved to authored, recorded as a plan delta in `LG-1609`); the ACK omits the changed total (76) and the reached-today list. B1/B2 plain raises render the generic 422 text until P3 | `LG-1609` `closed`; "Written by the auditor." | A6: `FD-1653`, LOW-MEDIUM, WK-1178, delivered but untested; reconciled by the auditor in the FD. Final: LOW, ACCEPTED, discharged at filing by the reconciliation at `02f23b4a` (from-lead 2026-10-11 20:24:40 BST); the residue belongs to `FD-1655` limb (iii). B1/B2: no FD, carried by the live roadmap row `SL-1601` ("WK-1178 P3 carry — FD-1589 row 8, remedy (c), B1 and B2", status draft, phase P3, relates FD-1589/SL-1600). Gate limb to `FD-1655` (ii) |
| SL-1557 (#1271) | A1–A23 MET by presence; A24 CARRIED-by-CI (conclusion only); A16/A19 HTTP mismatch tests are GUARDS | Ledger gate section empty. Executor's finding candidate: no owned code for a malformed stored pinned payload | `LG-1606` `closed`; Audit "Not yet." | `FD-1654`, LOW, WK-1178 (spec / decision-maker), deferred with owner. The GUARD classification accepted as carried. Gate limb to `FD-1655` (ii) |

Cross-slice, filed once as `FD-1655` (MEDIUM, owner: process backlog, Lean P2 item 5):

- **(i)** All eight ledgers and slice rows were set `closed` in the slice PR while the
  ledger's own `### Audit` read "Not yet" or was empty and `MERGE-ACK` read "not yet given".
- **(ii)** The gate was not run on the final tree, or the ledger has no gate record (SL-1541
  A12, SL-1529 A10, SL-1390, SL-1559, SL-1600, SL-1557); the CI table in Method is what exists.
- **(iii)** Plan deltas accepted in channel messages (SL-1529 D1; SL-1559 "04:19:42" and
  "04:23:36"; SL-1600 "23:03:19" and "23:53:00"; SL-1541 "23:46:57") are recorded in ledger
  build logs, not in the frozen plan.

## Result

Eight slices audited; no code defect was found by reading, and CI at all eight PR heads was
green. Findings filed: `FD-1650` (SL-1257, MEDIUM, WK-674), `FD-1651` (SL-1390, MEDIUM,
WK-673), `FD-1652` (SL-1559, MEDIUM, WK-675), `FD-1653` (SL-1600, LOW-MEDIUM, WK-1178; reconciled in the FD, accepted LOW),
`FD-1654` (SL-1557, LOW, WK-1178), `FD-1655` (cross-slice, MEDIUM, process backlog). Not
filed: the B1/B2 generic-text regression (carried by `SL-1601`) and SL-1631's two omitted
ledger lines (accepted). The record is a proposal; the verdict column is the lead's.
