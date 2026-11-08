---
id: CR-8417
family: closure
kind: review
title: Plan review 18 — before the P2 exit demo — the binding re-read at the freeze tree
status: active                  # write-once; this is the only value this family ever takes
created: 2026-11-08   # working id 8417
owner: lead
tree: 374a22bf33ad3c62a4d2c8b69ba83bd334d4b167
phase: P2
work: WK-1178
corrected_by: []
relates: [CR-1907, WK-8418, FD-2099, FD-2100, FD-2101, FD-2102, FD-1706, FD-1723, FD-1381, FD-1482, FD-1725, FD-2034, OQ-1960]     # ids only
---

# CR-8417 — P2 pre-demo plan review (`CLAUDE.md` §14): the binding re-read at the freeze tree

**Filing note.** The accepted working file is `~/gi-pricing-plan.local/scratch/plan-s14/review-2026-11-08-freeze.md`, 160 lines, sha256 `73420bb468ca`, written against tree `374a22bf33ad3c62a4d2c8b69ba83bd334d4b167`. The text below is that file, with two changes only: its first heading is this record's heading, and its blank acceptance line is the Acceptance section below. The section "Filing: proposal, record, owner, state" is added at filing. Quotes are verbatim.


plan-s14high (planner, Opus 5.5, `$CLAUDE_EFFORT` = high), Sun 8 Nov 2026, read 08:48–08:58 UTC. Brief `brief-plan-s14high-2026-11-08.md`, sha256 `531cb020ece8`. Inputs index sha256 `a0569ce3c71e`.

**Object.** `origin/main` head `374a22bf33ad3c62a4d2c8b69ba83bd334d4b167`, tree `c0216baccf24`, read in a detached scratch worktree. Gate END `2026-11-08T08:46:35+00:00` rc=0; every rc part 0; Acceptance 11 PASS; pytest `7660 passed, 28 skipped, 5 xfailed`; demo 1462 s PASS; dislocation 497 s quiet; D7 ok (to-lead "2026-11-08 08:47:21 GMT"). Channel facts are cited by stamp and are read to "2026-11-08 08:50:28 GMT".

**A proposal, never a change. It binds nothing until the maintainer's line at the end is dated.** Every §13 verdict here is proposed; the verdicts are the lead's. Drafts r1 (`4da6bf835713`) and r2 (`13385504a8d0`) are inputs, not authority. New rows are named P3-A to P3-D, working labels only; no id is allocated.

**What this seat did not do.** §5.2 signature and §5.3 Contents reconciliation was not run (the brief bars subagents; P28). `audit-docs.py` was not re-run here; its rc 0 is the gate's. No S3 reading exists yet.

## 0. Tracking: the previous review's records, and r1/r2's proposals

| Item | Record | State at this tree or by stamp |
|---|---|---|
| CR-1907 E1, E2 row 6b | PL-1912 | filed; the rehearsal it orders has not run |
| CR-1907 E2 | SL-1913 | `draft`; heading and `title:` still read Mon 9 Nov; two dated lines (2026-11-04, 2026-11-05) govern, Mon 16 Nov |
| CR-1907 E3 | RL-1908 | `active` |
| CR-1907 E5, E7 | WK-1914, WK-1915 | `draft`, `## P3`; absent from P3's `works:` (P27) |
| CR-1907 E5, E7.2 | OQ-1910, OQ-1911 | OPEN |
| CR-1907 E6 | RL-1909, OQ-1901 | DECIDED |
| r1 P1 / D-1 | OQ-2035, FR-2082, SL-2084 (#1471, `d8626fa5`), FD-2028 | **DECIDED**, option D with sub-question (a), to-lead 23:22:37, corrected 23:29:34 (7 Nov). Carried here as a decision |
| r1 P2 / D-2 | to-lead "2026-11-08 08:14:15 GMT" | limb (a) **DECIDED**: the Wed 18 demo runs on this e2 box. Limb (b) is P16 |
| r1 P3 | FD-2034 | homes ruled, to-lead "2026-11-05 22:04:05 GMT" (3); not yet rows (P24) |
| r1 P4 / D-3 | FD-1836 | **open by design**, S3 addendum (P22) |
| r1 P5 | FD-2007 | void as asked: L MET, reassigned |
| r1 P6 | FD-2009 | NAMED CARRY, to-lead "2026-11-07 20:28:26 GMT" (3) |
| r1 P8, P10 | SL-1913 | dated line landed; fetch owner is the rehearsal's seat, the demo seeds from the digest cache (08:14:15) |
| r1 P9 | pair 4 | both gates CLEAN, no interference (03:29:47): **no change**, r1's placeholder closes |
| r1 P11 | roadmap | SL-1913 settled by dated lines; `works:` lists still stale (P27); status row is batch 23 (07:46:27) |
| r2 P17 | LG-2003 | carry line landed, batch 18, owner WK-1178 (P19 re-owns; P22b) |
| FD-2093, FD-2094 (FD 8403 / 8404) | SL-2096 (#1469, `9775f352`), LG-2097, PL-2095 | **closed** in place (register :464, :465); S3's I and J read the fixed harness, S3 brief amendment 2026-11-08 |
| O3 | FD-1723 D0 §7 | the lead's; SL-2060 is now `closed` (P23) |
| O4 | FD-2034 | answered 22:04:05 (3): C2+C3 one Work; others placed |
| O5 | "the P3 plan review" | answered at P26 |

**Retry counters (artifact B).** `write_runtime_state.py show`: two slice-layer `fix` entries (SL-1273 count 1, SL-1409 count 2), last written 2026-10-05; no `project` or `phase` entry; `position` written 2026-09-29. Withdrawn 2026-10-25 (T1(2), r1 §0d). No pilot data exists for Q5.

**Register rows decayed to this review.** `python3 scripts/register-owed.py review`, at `374a22bf (detached)`, rc 0: **"17 owed row(s), 1 matched but excluded"**. Each is disposed of below.

| Row | Disposition |
|---|---|
| FD-1244, FD-1648, FD-1704, FD-1729, FD-1916, FD-2028 | **Already resolved** by a marker mid-cell; listed because `_is_resolved` reads the cell's prefix (the FD-1916 record states this). No action. FD-2028's `<at merge>` is batch 23 |
| FD-1660 (excluded) | Verified: `Resolved 2026-10-16`, #1310. No residue affecting G2 was read |
| FD-1281 | Owner WK-677 stands (P3). Phase cell reads 2: correct by dated line |
| FD-1491, FD-1576 | Re-own to P3-C, P19. "P3 plan review" replaced, P26 |
| FD-1508 | Event met; §14 proposal named in the row: P7 |
| FD-1619 | OQ-1617 undecided. Carried to P3-C at the close, with the OQ |
| FD-1706 | **Finding against the register.** RL-1712 chose A; FR-259 clarified (#1354, `0ac7164c`); `test_wf701_journey.py:55-58` walks "C7-errors: refused, not traced". The row still reads open. P23 |
| FD-1723 | Limbs placed: FR-6 UI, FR-109 WK-1914; FR-127, `power(k)` WK-1915; FR-14, FR-15 P3-C; FR-7 see P23 |
| FD-1725 | **Unfixed at this tree**: `scripts/req-coverage.py:58` and `scripts/scope-audit.py:82` still match one marker form, and the row says "fixed in P2". Fix or carry owed (P23); Q1's counts are a floor until then |
| FD-1836 | D-3, S3 addendum, P22 |
| FD-2033, FD-2077 | Re-own to P3-A, P16 |

## 1. Completion

**Answer: the roadmap's count holds; the phase is not complete; G1 is at risk on two Works.**
- **Works (roadmap `### WK-`, `status:` at this tree):** closed WK-668 to 673, 675, 693 to 697, 1250. Active: **WK-674, WK-690, WK-1178**. WK-1169 and WK-1170 are `phase: P3`, moved by dated line. This agrees with the G1 count line.
- **WK-690:** NOT CLOSE-READY (CR-2078 D7, lead's adoption 20:27:38). **WK-674:** not ready (CR-2071, to-lead 2026-11-05 11:23:52); Acceptance 11 now met at this tree (08:47:21), so its remaining blocks are FD-1836 with FD-1411 and the docs acts.
- **`scope-audit.py <M> --endpoints` (rc 1 on any unevidenced id, by design), evidenced of in-scope:** RATE 87/92, MODEL 133/144, PLAT 62/79, DATA 63/67, GOV 29/53 (P3). Published: 45/45, 45/45, 26/26, 40/40, 13/25.
- **`req-coverage.py`:** "requirements specified : 549", "requirements marked : 391 (71.2%)". Both are floors (FD-1725).
- **RATE's five unmarked ids carry verdicts:** FR-1186 delivered but untested, FR-1903 delivered outside the instrument (CR-1952); NFR-492, NFR-493 deferred WK-1178 (register :444, :440); NFR-1443 diagnostic, SL-1736 (CR-1952:263). MODEL's 11 and PLAT's 17 unmarked ids were **not each traced to a verdict here**; those read sit in Phase 1 closes or WK-1251 (FR-433, FR-438), and the rest is the closure audit's. FR-2082 carries 9 markers, all in `test_rate_table_bulk_ops.py`.

## 2. Omission

**Answer: yes, six.**
1. **No P3 row measures the host-bound limbs** (FD-2077, FD-2009, FD-2007/NFR-475, FD-2033): P16.
2. **FR-350 is on no Work.** `grep -n 'FR-350' docs/roadmap.md` gives one hit, prose at :4645; WK-676's row ends at FR-349. C5 lands with it: P24.
3. **C2 and C3 have no Work:** P24 (P3-B).
4. **Thirteen rows open "unowned":** F45, F47, F52, F55 and FD-1246 (its cell opens so, though later amended to WK-1178), and F7, F65, F66, F69, F72, F79, F89, F93. "Unowned" is not a permitted state: P19.
5. **S3's order names no NFR-490 item,** though LG-2003's addendum heading says "the exit reading is S3's", and G4's amendment says "NFR-490 is unaffected" by the host carry. P22b.
6. **"The P3 plan review" is a discharge event nothing schedules** (FD-1491, FD-1576, FD-1495 limb, FR-364 `rate_table_diffs`, F35's "P3's first plan"): `## P3` has `exit criteria: ~`. P26.

**Not an omission:** the endpoint axis in reverse. Every operation in `docs/contracts/openapi/generated.json` is in some spec's §5.1 table, by `scope-audit.py`'s own `declared_endpoints` ∪ over eight modules against `implemented_endpoints`: 171 published including framework paths, 169 declared; the 2 others are `GET /docs` and `/redoc`.

## 3. Skills and research

**Answer: two skills behind; two tool defects; no research record found wrong, on a narrow sweep.**
- **`phase-review`:** asks for artifact B (withdrawn); its Verified line says the replan check is "not yet exercised" while CR-1999, CR-2000, CR-2071 and CR-2078 all carry one. P12.
- **`phase-review` Output, "derived from the records":** `docs/INDEX.md` `execution` is no verdict (FD-2073, two instances). Tracking above reads `status:` and CR verdicts, not that cell. P12.
- **`dev-commands` "three silent failure modes":** FD-1725 is a fourth, and neither it nor `python-test` names multi-argument or `pytestmark` markers (grep, no hit). P12.
- **`req-coverage.py`'s "test file(s)" column counts markers, not files:** `claimed[rid]` appends once per marker (`FR-2082` prints 9; `git grep -c` gives one file, 9 markers). Goes with FD-1725, P23.
- **Skills-map, ahead or behind:** checked only `pandera` (absent, right), `statsmodels` (one skills-map line, not locked; `CLAUDE.md` §3 decided against it), `interpret` (locked as `interpret-core`), `lightgbm`, `sympy` (locked), `playwright` (ahead, OQ-1960). **This is not the full gap analysis;** owed with P28.
- **Research:** no RS record was swept against S2's readings beyond FD-2077's and FD-2033's own limits. No claim is made that NFR-476's 25 % rests on a research record.

## 4. Document drift

**Answer: yes. The endpoint axis is clean both ways; §12 row 2 disagrees with G4; the smaller items follow.**
- **§12 row 2 "meeting NFR-489" against G4** (roadmap :4886): S1 read p99 37.5–41.2 ms against 15 ms, a clear miss, while G4 carries NFR-489 as "**measured, diagnostic**" with "No near-bound pass or fail is claimed from the shared VM". A miss of that size is not near-bound, and the row cannot read met on the present evidence. P22.
- **NFR-476** against the code: 1.502 at full shape (FD-2077). §0's question, held by the ruled carry: measure first.
- **Four clauses cite FD-2007 for FD-2034's carries:** RULED "2026-11-08 08:50:28 GMT", batch 24. No proposal needed.
- **FR-23's suffix against a rate cell** (`money_minor` holding a fraction, D-1 (a)): the maintainer sent it here as a P3 spec proposal. P26.
- **`works:` and `gates:`:** P2 still lists WK-1169, WK-1170; P3 omits WK-1169, WK-1170, WK-1914, WK-1915; P2 `gates: ~` though dates are accepted. P27.
- **`process-backlog.md` header** still reads exit demo "Thu 2026-11-12" (:11, :19). P13.
- **The evidence's platform, not the spec:** S1 Broadwell Xeon, S2 AMD EPYC 7B12, 8 vCPU (LG-2003, LG-1839, LG-1760 addenda). No S2 number compares with S1 without that sentence; S3's item C is FD-1836's control, run first.
- **§5.2, §5.3 and named catalogues:** not re-run; r1's pre-read counts (`03` 5, `07` 8, `02` 5 + 5 cells, at `4daac158`) stand unverified at this tree. P28.

## 5. Shape

**Answer: one trigger fired and is absorbed; the cut holds; the plan has two dates that cannot both be right. No replan is proposed; that call is the lead's.**
1. **O10 ruled:** the 20:28:26 carry fires "a finding moves a slice or phase", absorbed here.
2. **Exit criteria at this tree.** G1 open, needs the user's lines on WK-674 and WK-690. G2: the gate demo PASS, rehearsal Mon 16. G3: 383 register rows, 311 open by the opening predicate; row-by-row is the closure audit's (07:46:27). G4: S3, then P16's carries. G5: rc 0 here; **batches 23–28 move the tree, so it is owed again at the exit tree.** G6: P21.
3. **G6's order.** "Filed after G1–G5 are met" cannot be met by a filing on Tue 10 (batch 25) or by the Fri 13 addendum: G1 needs two user lines not yet given, and G5 needs the exit tree. **Somebody must choose:** P21.
4. **D-3's remedy branch has no landing slot.** Code freeze is Thu 12; S3's exit reading is Fri 13, on the frozen tree; the freeze dates are not delegated (17:30:49). A "remedy inside P2's scope" chosen after S3 needs the user's freeze exception. Only a budget amendment lands on the plan's dates. This is not a recommendation on D-3, which remains the maintainer's in the addendum: P22.
5. **A closed Work cannot own an open limb:** O11 ruled (a); P19.
6. **WK-1178** runs 1,843 roadmap lines (:2127–:3969), shows 154 owed rows by `register-owed.py WK-1178` (text mentions included, so an upper bound), and several rows already read "WK-1178, phase 3" while it is `phase: P2`. It is the row nothing can be said to have closed. P25.
7. **G4's "dedicated host"** stays undefined, and nfr-bench-1 is deleted after S3 (S3 brief): P16.

## 6. Proposals index

Families per `document-ids.md` §1.6 and the skill's Output table. WK rows: the maintainer opens (`draft`), §1.6 :153.

| # | Proposal and rationale | Family | Owner | State |
|---|---|---|---|---|
| D-1 | OQ-2035 option D with (a); FR-2082; SL-2084 merged. **A decision, carried** | RL/FR landed | maintainer (by delegation) | decided |
| D-2 (a) | The Wed 18 demo on this box | dated line, runbook | maintainer (by delegation) | decided |
| D-3 | FD-1836 / NFR-489, remedy or budget, in the S3 addendum. **No recommendation from this seat:** the exit reading does not exist | RL + spec amendment, or a remedy row | maintainer (by delegation); decision-maker writes | open, Fri 13 |
| P7 | FD-1508: refuse-at-save, a P3 spec amendment to `06` FR-364 and `07` FR-429. Better design; later phase, so spec only | RL + spec | decision-maker | proposed |
| P12 | `phase-review`: artifact B dated line, Verified line, "`INDEX` `execution` is no verdict"; `dev-commands`: the fourth failure mode | skill fix | planner | proposed |
| P13 | Process backlog: disposition of its 127 dated rows (`grep -cE '^\| *\**2026-'`), header dates corrected | RFC | planner drafts; maintainer owns | proposed |
| P14 | The nine fold-check gaps: one read seat. Not read here | FD if lost | lead seats | carried from r1 |
| P15 | The closure list: the skeleton's carry-forward table (its predicate, 46 lines), **plus** FD-2033, FD-2073, NFR-490's carry line, FD-2007 and FD-2034 as separate rows (08:50:28), the Dependabot four, each with Appendix A's target; **minus** FD-1513 (`Resolved 2026-11-05`) | `CR- kind: phase` | auditor | proposed |
| **P16** | **P3-A, spec-host measurement (D-2 (b)).** One P3 Work on a 16-core host of the `02` NFR-475 class, for measurement and P3's demos. Measure first, fix second. Scope: Appendix A. A dated G4 line says nfr-bench-1 is single-tenant but **not** that host. **That a non-e2 host removes FD-2033's stall is an assumption until read or measured** | WK row `draft`; dated G4 line | maintainer opens; planner writes its plan | proposed |
| **P19** | O11 (a): every P2-owned deferred limb re-owned to a named P3 row at the P2 close, by Appendix A. The closure record's list is an owner only until the rows exist | WK row edits; CR verdict lines | lead; auditor lists | ruled; mapping proposed |
| P20 | S3's readings as a dated addendum, Fri 13 | dated part of this CR | lead | ruled (O12) |
| **P21** | G6's order. **(a) Recommended:** a short third dated part at the Mon 16–17 session reading G1–G5 at the exit tree, with G6 read against that part. (b) A dated amendment of G6 to accept the Tue 10 filing. (a) keeps G6's maintainer-worded text | dated part; or G6 line | **maintainer's choice** | open |
| **P22** | §12 row 2 against G4, and D-3's timing. The addendum states which branch is available without a freeze exception, and how row 2 reads after it. **Whether P2 exits with row 2 unmet is the user's** ("Nobody but the user carries FD-1836 past S3", CR-2071) | dated line, roadmap §12 | maintainer | proposed |
| **P22b** | NFR-490: S3's order either gains one item, or the closure list says no S3 reading was taken and the indication is the last | S3 brief dated line | lead | proposed |
| **P23** | Register closing acts, each verified first: FD-1706 (§0's evidence); FD-1723 FR-7 (SL-2060 `closed`, row silent); FD-1381 (SL-2085, #1465, row still "named exception"); FD-1482 limb 2 (SL-2091, #1467); FD-1725 **fix or carry**. Without these, G3 reads worse than it is, and FD-1725 reads better | FD dated lines | auditor; lead sets `decision:` | proposed |
| **P24** | **P3-B, unreached lifecycle states** (C2, C3, FD-2064, OQ-2063, OQ-2037). C5 and **FR-350** to WK-676; C1, C4, C6 to WK-679 (22:04:05 (3)) | WK row `draft`; WK row edits | maintainer opens | proposed |
| **P25** | **WK-1178 closes with P2, by the user's line, and is not re-phased.** P3-C and P3-D succeed it, split by kind: product code against tools. Scope crossing those kinds cannot be audited as one thing | WK rows `draft`; close line | maintainer | proposed |
| P26 | **"The P3 plan review" as an assignment event is discharged by Appendix A.** What remains is spec: a Dislocation Run budget NFR (FD-1576, FD-1983); FR-23 and FR-273 against a rate cell (D-1). Later phase, spec only | OQ, then RL + spec | decision-maker | proposed |
| P27 | Roadmap: both `works:` lists; P2 `gates:` with the dates of record | WK rows; milestone edit | lead | proposed |
| P28 | One `spec-reconciler` per module for `03`, `07`, `02`, then the skills gap analysis, before the Mon 16 session. Q3 and Q4 are incomplete until then | evidence; FD if drift | lead seats | proposed |
| OQ-1960 | axe-core and Playwright, "decided at the P2 close", owner WK-675 (closed). Owner to P3-D, or decided at the close | OQ row | decision-maker | proposed |

## Appendix A. P19 (a): the re-owning map (moves to the P2 closure record at filing)

**Predicate, tree `374a22bf33ad`, corpus `docs/findings/register.md`, cells split on unescaped `|`.** Open: Decision cell does not open, leading `*_\`~ ` stripped, with `resolved|fixed`. 383 rows, 311 open. Deferred or carried with no mid-cell marker: opens `deferred|carry forward|carried`, and no `\*{1,3}(resolved|fixed)\b`: **134**. P2-owned: of those, `WK-(1178|674|690|673|671|672|675|1250)\b|P2 closure` in the Work cell or the Decision's first 260 characters: **65**, every one listed below. The other 69 are in the class table. Not in the map: 38 unmarked `fix before close` rows (11 name closed or discharged in prose) and the 72 with a mid-cell marker, which are the closure audit's (07:46:27); any still open at the exit tree takes the row its class names here.

**Rows named `verify` looked discharged or accepted on a partial read; the auditor confirms each before re-owning.**

| Target | Limbs |
|---|---|
| **P3-A** spec-host measurement | FD-2007, NFR-475; FD-2077; FD-2009; FD-2033; F-W9-1 (NFR-501); F35 (NFR-490 remedy); NFR-490 result limb, :445; NFR-494, :439; NFR-493, :440, F52; NFR-501, :441; F1, :442; O4, :443; NFR-492, :444; NFR-502; NFR-529 |
| **P3-B** unreached lifecycle states | FD-2034 C2, C3; FD-2064 |
| **P3-C** rating and platform correctness | FD-1220, FD-1240, FD-1246, F55, FD-1331, FD-1335, FD-1491, FD-1576, FD-1619 (with OQ-1617), FD-1751, FD-1756, FD-1783 (with OQ-1784), FD-1796, FD-1798, FD-1815, FD-1963, FD-1978, FD-1983, FD-2031, FD-2058, FD-1219; expression-Factor limb FR-174/175/177; FD-1495 limb; FD-1723 FR-14, FR-15 |
| **P3-D** process and instruments | F26, F30, F33, F45, F46, F47, FD-1214, FD-1215, FD-1216, FD-1218, FD-1227 (with OQ-1229), FD-1238, FD-1338, FD-1480, FD-1725, FD-1684 sweep, FD-1801, FD-1820, FD-2029, FD-2030, FD-2073; Dependabot #1440, #1441, #1443, #1444 (ruled; #1443's failure read before any merge) |
| **WK-676** | FD-2034 C5, FR-350; FD-1197 |
| **WK-677** | FD-1508 (with P7); FR-364 `rate_table_diffs` |
| **WK-679** | FD-2034 C1, C4, C6 |
| **WK-1914, WK-1915** | FD-1723 FR-6 UI, FR-109; FR-127, `power(k)` |
| **WK-1251** | FR-433, FR-437 (names the Work, RL-1232); the binding precondition, verbatim |
| **WK-1169, WK-1170** (P3, event already named) | F31 (WK-1169); F27, F29 (WK-1170) |
| **WK-687** | F41 (NFR-497, re-homed 2026-11-06) |
| **Per D-3** | FD-1836, F38; FD-1411 tied to it. Only the user carries it past S3 |
| **verify** | F-W10-3 (contract publishes `POST /api/v1/rate-tables/{slug}/versions`; row says no such route); F44 (limbs annotated closed); FD-1199 (row ends "accepted") |

**The 69 not owned by a P2 Work:** WK-1170 event, 27 rows; WK-1169 event, 13 rows; a named P3 or P4 Work, 5 (FR-353 limb, FD-1281, FD-1658, FD-1663, FD-1715). **Unowned, 8:** F7 (by design, with a trigger), and F65, F66, F69, F72, F79, F89, F93, to P3-D. **Other, 16:** F38 above; F6, F8, F9, F22, F-W10-1, F39, F57 (artifact B, withdrawn), F63, F68, F107, F112, F113, FD-1193, FD-1202, FD-1226 are old rows whose named event has passed or is the lead's and the maintainer's. Each takes a line at the closure audit: a resolution or P3-D.

## Filing: proposal, record, owner, state

State at filing, 2026-11-08. A record with no id yet names its family, owner and event, so no accepted proposal is unowned (`CLAUDE.md` §14).

| # | Record | Owner | State |
|---|---|---|---|
| D-1 | OQ-2035, FR-2082, SL-2084 (#1471, `d8626fa5`), FD-2028 | maintainer (by delegation) | decided; landed |
| D-2 (a) | to-lead "2026-11-08 08:14:15 GMT"; SL-1913's dated lines | maintainer (by delegation) | decided: the Wed 18 demo runs on this box |
| D-3 | FD-1836, NFR-489; the S3 addendum | maintainer (by delegation) | **open by design** until S3's addendum; the budget branch is the default unless S3's control reading says otherwise, and a remedy branch would need the user's freeze exception, which the maintainer will not ask for |
| P7 | FD-1508; an RL at P3 start, then `06` FR-364 and `07` FR-429 | decision-maker | accepted; P3 spec proposal, no id yet |
| P12 | this batch: `.claude/skills/phase-review`, `dev-commands`, and skills-gap F1 to F9, A1, A3, A6, A7 | planner | landed in this batch |
| P13 | an RFC, not yet minted | maintainer | accepted; P3 |
| P14 | one fold-check read seat; FD if anything is lost | lead | accepted; open |
| P15 | the P2 `CR- kind: phase`, its closure list | auditor | accepted; due at the P2 close |
| P16 | a P3-A WK row, `draft`, not yet minted; a dated G4 line | maintainer | accepted; opened at the P2 close (D-2 (b)) |
| P19 (a) | Appendix A, moved to the P2 closure record's re-owning table | lead; auditor lists and confirms each `verify` row first | accepted; due at the P2 close |
| P20 | S3's readings, a dated addendum | lead | ruled (O12); due Fri 13 |
| P21 (a) | a third dated part at the Mon 16 to 17 session, in the P2 CR | maintainer | option (a) accepted; due Mon 16 to 17 |
| P22 | the S3 brief's dated line; the addendum states D-3's available branch | maintainer | accepted as the entry states; due with S3's addendum |
| P22b | the S3 brief, `997762bc318b`: NFR-490 via `scripts/bench-rating.py`, or the "no S3 reading taken" sentence | lead | done (to-lead "2026-11-08 09:04:05 GMT") |
| P23 | FD-1706, FD-1723, FD-1381, FD-1482, FD-1725: dated lines, docs batch 25a (#1474, `7bf10751`) | auditor; lead sets `decision:` | landed; verdicts from-lead "2026-11-08 09:30:19 GMT" |
| P24 | WK 8418, `draft`, opened to-lead "2026-11-08 09:40:05 GMT"; WK-676 and WK-679 dated lines, this batch | maintainer opened; row owner lead | landed in this batch |
| P25 | a proposal to the user's P2 close line; P3-C and P3-D rows, not yet minted | maintainer; the user's line | accepted as a proposal; due at the P2 close |
| P26 | P3 spec items: a Dislocation Run budget NFR; FR-23 and FR-273's wording | decision-maker | accepted; P3 spec only |
| P27 | `docs/roadmap.md` `works:` and `gates:`, docs batch 24 (#1473, `a8ad2d01`) | lead | landed in batch 24 |
| P28 | recon-03 `b6aae4d22369`, recon-07 `bce13c79988c`, recon-02 `4ebcf6fbb6d8`, skills-gap `ea387abb9e1e`; FD-2099, FD-2100, FD-2101, FD-2102 (#1474, `7bf10751`) | lead; auditor filed the findings | complete; the line closes with those reports |
| OQ-1960 | OQ-1960 | P3-D | owner moved; decided at the close |

## Acceptance

**Maintainer acceptance: by delegation; the P2 close line stays the user's.** Date: 2026-11-08 09:02:21 GMT. The entry, verbatim, from `to-lead.md`:

> 2026-11-08 09:02:21 GMT — Maintainer: §14 REVIEW ACCEPTED (by delegation; the P2 close line stays the user's): scratch/plan-s14/review-2026-11-08-freeze.md, 160 lines, sha256 73420bb468ca, by plan-s14high (opus, $CLAUDE_EFFORT=high verified from its transcript and cmdline; brief 531cb020ece8; inputs index a0569ce3c71e) against the freeze tree 374a22bf33ad3c62a4d2c8b69ba83bd334d4b167 (gate END 2026-11-08T08:46:35+00:00 rc 0, acceptance 11 PASS); the seat edited nothing (freeze-tree porcelain 0, HEAD 374a22bf; no file under the worktree newer than the gate END). Read against my 12-tick list: all met — header, five answers in order each with evidence by command and count, 20-row proposals index routed by family and owner, Q5 absorbed, P19 (a) map (Appendix A), D-1/D-2/D-3 as lines with stamps, the carries named, S3 as addendum, Acceptance 11 read, acceptance line blank, no plan edit, drafts as inputs. ACCEPTED PROPOSALS, each becoming an owned record in its family (document-ids §1.6): P16 (P3-A spec-host measurement = D-2 (b)) → WK row `draft`, I open it at the P2 close; P24 (P3-B unreached lifecycle states; FR-350 + C5 → WK-676; C1/C4/C6 → WK-679) → WK row draft + row edits, batch 25; P25 (WK-1178 closes with P2 by the user's line; P3-C product, P3-D tools succeed it) → proposal to the user's close line; P19 (a) Appendix A map → the P2 closure record's re-owning table, each "verify" row confirmed by the auditor first; P23 register closing acts (FD-1706 row corrected, FD-1723 FR-7, FD-1381, FD-1482 limb 2, FD-1725 carried to P3-D with "fixed in P2" struck by dated line) → batch 24/25 after verification; P27 roadmap works:/gates: → batch 24; P28 spec-reconciler ×3 + skills gap analysis before Mon 16 → lead seats Mon 9–Tue 10, run-light, never beside a timed stage; P12 skill fixes → planner, batch 25; P13 process-backlog RFC → P3, mine; P14 fold-check read seat → lead; P15 closure-list contents → the P2 CR; P21 (a) third dated part at the Mon 16–17 session → the P2 CR; P22 and P22b → S3 brief dated line (NFR-490 item or the "no reading" sentence) and the addendum states D-3's available branch; P26 → P3 spec items (Dislocation Run budget NFR; FR-23/FR-273 wording); P7 FD-1508 refuse-at-save → P3 spec proposal, RL at P3 start; OQ-1960 → owner P3-D, decided at the close. NOT ACCEPTED AS WRITTEN: none. OPEN BY DESIGN: D-3 (FD-1836/NFR-489) until S3's addendum; a remedy branch would need the user's freeze exception — I will not ask for one; the budget branch is the default unless S3's control reading says otherwise. Two findings against the register (FD-1706 stale row; FD-1725 "fixed in P2" false) → register corrections by dated line, batch 24; no new FD (neither let a wrong merge, number or price through). The review is FILED as batch 25 (Tue 10) under docs/closures/ as the index record its kind names, with this entry quoted as the acceptance line; the Mon 16–17 session reads it finished.

Corrected two minutes later, verbatim from the entry's opening:

> 2026-11-08 09:04:05 GMT — Maintainer: CORRECTION to 09:02:21 — the proposals index has 22 rows (the seat's FINAL; three decision lines D-1/D-2/D-3, the P-rows and OQ-1960); my "20-row" counted P-ids only; same file, sha 73420bb468ca; the acceptance is unchanged.

That count was corrected in turn, verbatim from the entry's opening:

> 2026-11-08 09:49:26 GMT — Maintainer: CORRECTION to my 09:04:05 line — the §14 proposals index has 21 DATA rows; the 22 counted the header row with the `^\| ` predicate; the acceptance (09:02:21, sha 73420bb468ca) is unchanged, and CR 8417 quotes the entries and states no count.
