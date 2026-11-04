---
id: FD-1982
family: finding
title: SL-1388 and SL-1389 closed with no slice audit, and SL-1389's red-first proofs are owed
status: closed
created: 2026-11-03   # drafted 2026-11-03 under working id 8307
owner: auditor
tree: 55bddaf279fc73fd9b52f523fdea908d6c4aada3   # origin/main when read
corrected_by: []
relates: [WK-673, SL-1388, SL-1389, LG-1570, LG-1582, PL-1267, CR-1981, FD-1651, SL-1997, LG-1998, PL-1984]
---

# FD-1982 — SL-1388 and SL-1389 closed with no slice audit, and SL-1389's red-first proofs are owed

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

Open, owner WK-673, `fix before close with an owner`. **Discharged by SL 8305** (S-b of PL-1984,
row 2, which carries the five owed proofs: the plan's "SL-1389's five owed red-first proofs are
recorded (FD candidate 1)"); the finding closes when that slice's ledger quotes the red-first of
each proof and the auditor's slice audit is filed for SL-1388 and SL-1389 or the gap is accepted
by a dated line. Filed under working id 8307.

***Resolved 2026-11-04*** — closed in place 2026-11-04 by the executor, as the closing act of the mint of SL-1997 (WK-673, LG-1998, PL-1984; ~~this PR, its number and squash written at the merge's date-of-record~~ [PR #1426, squash commit db92a7bc0424059ed0aff4e5cebf445661c3be81 on main, merged 2026-11-04T08:45:16Z; written 2026-11-04 in docs batch 8 on to-lead "2026-11-04 10:00:29 GMT" closing acts (route per "2026-11-04 09:57:14 GMT")]), on the lead's brief under the GO "2026-11-03 16:28:44 GMT" (`to-lead.md`, a local channel file), row 2 of PL-1984 (S-b). Delivered remedy: the five owed red-first proofs of SL-1389 (`PL-1984` row 2) are recorded in LG-1998 and the "(OWED: scratch-reverted)" docstrings in `test_rating_version_dislocation_gate.py` are re-pointed to it. Against a baseline of 25 passed, each scratch-reverted proof fails: FR-257 limb (2) not called, 5 failed (`DID NOT RAISE PlatformError`, `KeyError: 'dislocation_run_id'`); `_approximation_gate` not called, 7 failed; the threshold read from `GIP_APPROXIMATION_MAX_ABS_CHANGE_PCT`, `test_fr224_threshold_ignores_environment_variables` red; an unset entry returning `None`, `test_fr224_an_unset_threshold_is_governed_by_the_default` red; a null observed read as 0, `test_an_empty_banded_set_has_null_quantiles_and_fr224_refuses` red. This discharges limb 2 of the finding as `PL-1984` row 2 names it. Limb 1, the missing slice audit for SL-1388 and SL-1389, is not delivered by this slice: it stays for the auditor's filing or a dated acceptance of the gap, and the lead gives the verdict on that. The slice-audit limb — the auditor's slice audit of SL-1388 and SL-1389 — is ACCEPTED as a gap by the maintainer's dated line, to-lead "2026-11-04 08:05:12 GMT" (`to-lead.md`, a local channel file; ruling (a)); condition carried: WK-673's fresh close audit names SL-1388 and SL-1389 among the slices it evidences, each requirement with its test or verdict. Gate evidence is in LG-1998: the SOLO gate at `07e62951` (pytest "13 failed, 7047 passed, 22 skipped, 5 xfailed" = the 13 item-31 docs-audit failures only; frontend all rc 0, vitest 919 of 919; demo designed stop 1587 s, dislocation #1 592 s), from-lead "2026-11-04 07:38:28 GMT", accepted under item 31 by to-lead "2026-11-04 07:39:25 GMT".
