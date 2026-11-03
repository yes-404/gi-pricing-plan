---
id: FD-8307
family: finding
title: SL-1388 and SL-1389 closed with no slice audit, and SL-1389's red-first proofs are owed
status: active
created: 2026-11-03               # drafted 2026-11-03 under working id 8307
owner: auditor
tree: 55bddaf279fc73fd9b52f523fdea908d6c4aada3   # origin/main when read
corrected_by: []
relates: [WK-673, SL-1388, SL-1389, LG-1570, LG-1582, PL-1267, CR-1981, FD-1651]
---

# FD-8307 — SL-1388 and SL-1389 closed with no slice audit, and SL-1389's red-first proofs are owed

## Finding

**MEDIUM, owner WK-673** (a governance record that reads complete and is not; the same class as
FD-1651). Filed from CR-1981 "FD candidate 1" (`docs/closures/CR-01981-wk-673-close-audit.md`,
§ Findings), by the maintainer's "2026-11-03 16:03:37 GMT" entry, ruling (C) ("Docs batch 7
accepted … FD candidates 1–3 filed"), in `to-lead.md`, a local channel file.

1. **No slice audit.** LG-1570 (SL-1388) and LG-1582 (SL-1389) are `status: closed` and each holds
   an empty Gate table (`(empty: no gate yet; …)` in LG-1582) and the placeholder "(Written by the
   auditor at slice close.)" in its Audit section. No `RS-` or `CR-` covers either:
   `git grep -l -E 'SL-1388|SL-1389' -- docs/research docs/closures` at `55bddaf2` prints only
   `docs/closures/CR-01981-wk-673-close-audit.md`, the audit that found it (RS-1649's retro audit
   covers SL-1390, not these).
2. **SL-1389's red-first proofs are OWED and nothing later discharges them.** LG-1582's acceptance
   record (`:69-87`) reads OWED in the Red-first column for items 2, 3, 4, 5, 6, 8, 9, 14 and 15
   (among others); CR-1981 names items 2, 5, 6 and 15. `PL-1267` acceptance 11's FR-224
   environment-variable test (LG-1582 item 6, "broken variant (reads `load_settings()`) OWED") is
   therefore not shown red.

## Evidence

The two facts above are the evidence, each with its command and file:line: the empty `### Gate` table and placeholder in `LG-1570` and `LG-1582` (`:38-44`, `:36-44`); the `git grep -l` result at `55bddaf2`; the OWED red-first cells of `LG-1582:69-87`. Source: `docs/closures/CR-01981-wk-673-close-audit.md` § Findings, candidate 1.

## Disposition

Open, owner WK-673, `fix before close with an owner`. **Discharged by SL 8305** (S-b of PL 8302,
row 2, which carries the five owed proofs: the plan's "SL-1389's five owed red-first proofs are
recorded (FD candidate 1)"); the finding closes when that slice's ledger quotes the red-first of
each proof and the auditor's slice audit is filed for SL-1388 and SL-1389 or the gap is accepted
by a dated line. Filed under working id 8307.
