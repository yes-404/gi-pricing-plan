---
id: CR-8219
family: closure
kind: review
title: Plan review 17 — before the P2 exit demo — the six owed rulings routed to owned records
status: active                  # write-once; this is the only value this family ever takes
created: 2026-10-25
owner: lead
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-1178
corrected_by: []
relates: [CR-1247, RL-8220, RL-8221, OQ-8222, OQ-8223, PL-8224, SL-8225, LG-8226, FD-1209, FD-1723]     # ids only
---

# CR-8219 — Plan review 17, before the P2 exit demo

**Base tree:** origin/main `ff976406f1bf133cfe040d2c44d383011503988a`. Working id CR 8219, reserved
by lead 28 (`eta.md`, 2026-10-25 11:35:25 GMT), with the sibling ids RL 8220, RL 8221, OQ 8222,
OQ 8223, PL 8224, SL 8225 and LG 8226. Drafted by the planner (Opus 5.5, effort medium). This is a
**short index** (`.claude/skills/phase-review` §Output). The evidence lives in the records it cites.
The items E1–E7 come from the planner's working note r5
(`handover/s14-review-items-draft-2026-10-25-r5.md`, local, not in the repository).

## Scope

This is the `CLAUDE.md` §14 full review before the P2 exit demo (Thu 2026-11-12, `docs/roadmap.md`
`## P2`). It covers the previous review's records, the register rows decayed to this review, the
five questions, and the seven items E1–E7 that the maintainer ruled in the entry
`2026-10-25 11:32:17 GMT — Maintainer: §14 note r5 — the six owed rulings, decided now (dated lines for the review's rows)`
(`to-lead.md`; the channel file is local and is not in the repository).

## Tracking first — `CR-1247`'s twelve proposals, derived from the records at ff976406

| # | Record(s) | State at ff976406 | Open residue |
|---|---|---|---|
| 1 | RL-1305; `06` §4.1; PL-1359 | RL `active`; `06-governance.md:211` amended; PL-1279 `superseded` → PL-1359 `active` | none |
| 2 | none needed | resolved in `CR-1247` itself | none |
| 3 | RL-1518, RL-1519; PL-1520; SL-1536 | RLs `active`; SL-1536 `closed`; PL-1520 `draft`; the NFR-490 remedy is carried to P3 under G4 (PL-1537 R5.1) | **F55** (register:96) still reads "carry forward — unowned"; FD-1246 (:212) still waits on the TraceStep ruling |
| 4 | G4 row; PL-1237 | `roadmap.md:572–573` amended; PL-1237 `active` | none |
| 5 | RL-1252, RL-1296, RL-1311 | all `active`; the three OQs decided (`open-questions.md:221–223`) | none |
| 6 | FD-1238; `reporter.md`; `delivery-process.md` §3 | the reporter line is in (`reporter.md:33`, `:46`) | **the team-wide write boundary** is not in `delivery-process.md` §3 or the core extract |
| 7 | WK-1251 | `draft` (`roadmap.md:3285`) | `active` is the maintainer's at P3 |
| 8 | G6 restatement | done (`roadmap.md:576–578`) | none |
| 9 | an FD against `register-owed.py`; F61's event; F58/F91 reopened | **no record found** | all three |
| 10 | WK-1250; PL-1254; `CR-838` correction | WK-1250 `active`; PL-1254 `active`; `CR-838:46` | FD-1241's register cell (:209) does not name WK-1250 |
| 11 | OQ-1373 → RL-1519; `03` NFR-500 | decided; `03-rating-engine.md:1570` | the re-measurement sits in PL-1520 (`draft`) |
| 12 | the Exit demo row; the §10 gate *Before the P2 exit demo* | the row exists (`roadmap.md:607`); the gate row exists (`:3523`) | see Q4 (b) and (c) |

## Register rows decayed to this review

`python3 scripts/register-owed.py review` at ff976406 (committed register), run as
`flock -w 900 /tmp/slots/gate-2 env -C <wt> uv run --directory <wt> python scripts/register-owed.py review`,
rc 0: **33 owed rows**, 6 excluded as opening with a resolution marker. Each row gets a disposition:

| Rows | Disposition proposed |
|---|---|
| FR-240 (F-W9-3), F27, F29 | Owner and event stand: the create-read-retire audit Work (WK-1170), its first slice (`CR-1167`). The generator matched the superseded opening kept in each cell. That predicate gap is already F86's, so no new finding is raised. |
| F28, F31, F33, F74, F75, F86, F89, F90, F94, F96, F97, F101, F113, F114 | Owner and event stand: the lead, with the event each cell names (a WK-1169 or WK-1170 first slice, the first maintenance slice after WK-697, or the next `delivery-process` change). |
| F48 (NFR-499) | The row asks this review to confirm or overturn "provisionally WK-674". **Confirm WK-674**, because WK-674 is `active` and owns the tenancy mechanics (ADR-710). |
| F61 | Accepted deferral, with a new event. Its event, "plan review 15", has passed, and `CR-1247` P9 did not move it. New event: the review at P3's entry, read against artifact B. Artifact B was read here and has no `project`- or `phase`-layer entries (see *Retry counters*). |
| F63 | Owner stands: the maintainer. A plan review cannot discharge it (the row's own text). |
| F93 | Owner: the maintainer (the resolution is the maintainer's). Event: the process RFC after the exit demo (E4), or else the review at P3's entry. |
| FD-1209 | **Event met.** Its event, "the real freMTPL2 algorithm in the seed and `WF-699` end to end", was discharged by SL-1526 (`closed` 2026-10-11, `LG-1641`) and SL-1527 (`closed` 2026-10-12, `LG-1647`). The auditor closes FD-1209, citing both. |
| FD-1244 (and FD-1245) | Resolved by RL-1524 (stated in the middle of the cell, so the generator does not see it). The lead strikes both on the gate row in E6's gate-row edit. |
| FD-1281 | Owner stands: WK-677 (P3). The first half of its event (OQ-1234 → RL-1296) is done. |
| FD-1619, FD-1704, FD-1706, FD-1725, FD-1729 | Owner stands: WK-1178, to be resolved before any P3 start. Each is listed with its resolution in the P2 phase closure record. |
| FD-1679, FD-1727, FD-1728 | The FD is `closed` in its front matter, but the register row still reads as owed. The auditor's register pass cites the close. |
| FD-1723 | Owners are named by this review: FR-6's UI half and FR-109 go to the E5 Work row, and FR-127 goes to the E7.2 Work row. **FR-110 `power(k)`** is still the maintainer's choice, build or strike, and no line rules on it yet. The auditor updates the owner cell (E5). |

## The five questions

1. **Completion.** `scope-audit.py RATE --endpoints` at ff976406, under gate-2, rc 1 (the script exits 1
   when any requirement is unevidenced). Results: 85 of 89 in-scope requirements are evidenced, and
   44 of 44 declared endpoints are published. **No evidence: FR-1186, NFR-492, NFR-493, NFR-1443.**
   `req-coverage.py` (rc 0): 387 of 546 requirements are marked (70.9%). Both counts read only the
   `@pytest.mark.req("X")` form (FD-1725), so they are marker counts, not verdicts (E4). Proposed
   verdicts, which are the lead's to give (§13):
   - FR-1186 is a negative requirement: delivered but untested.
   - NFR-492 and NFR-493: deferred to G4's host (owner: the maintainer, `roadmap.md:572`).
   - NFR-1443: deferred to SL-1736's DIAGNOSTIC sweep (WK-1178).

   All eight P2 Works are still `active`, which agrees with `roadmap.md` §6.
2. **Omission.** Nobody would notice three things missing:
   - the owners of FR-6's UI half, FR-109 and FR-127, which E5 and E7.2 now give;
   - `CR-1247` P9's three records, which do not exist;
   - artifact B's writer, which last wrote `retry_counters` on 2026-10-05 and `position` on
     2026-09-29.

   The last relates to F58 and F91, which P9 had reopened, and the register still reads them as
   "Resolved". **Proposal T1:** the lead names an owner for each P9 record, or withdraws it with a
   dated reason. Accepted proposals are never left unowned (§14).
3. **Skills and research. No change.** Between `1c8762d9` (`CR-1247`'s tree) and ff976406, three
   dependencies were added: `sympy==1.14.0`, `@tanstack/vue-table` and `@vue-flow/core`. Each one's
   row in `docs/skills-map.md` was updated with it (`git diff 1c8762d9 ff976406 -- docs/skills-map.md`).
   No row is ahead of the code without a phase saying so.
4. **Document drift.**
   - (a) The `03` §5.1 endpoints agree with the contract (44 of 44). The other modules' §5 sections
     were not re-checked by this review.
   - (b) The Exit demo row (`roadmap.md:607`) reads "not started", but its two slices are closed.
     The lead restates the row.
   - (c) The gate *Before the P2 exit demo* (`:3523`) lists FD-1244 and FD-1245, which RL-1524
     resolved. The lead strikes both, in the same edit as E6's +1.
   - (d) The OQ gate rows: E3-B and E3-C.
   - (e) The register cells for FD-1241, FD-1679, FD-1727 and FD-1728 are behind their records.
     The auditor's register pass corrects them.
5. **Shape.** The P2 cut does not change. Two P3 Works are added as `draft` (E5 and E7.2). The exit
   demo becomes a pre-seeded WF-701 (E1), and one full rehearsal is added on Mon 9 Nov 2026 (E2).
   **Proposal T2:** `CR-1247` P6's team-wide write boundary gets an owner or a dated withdrawal (as T1).

**Retry counters (RFC-895 artifact B):** `write_runtime_state.py show`, rc 0. It has slice-layer
entries only: `slice:SL-1273:fix` count 1, and `slice:SL-1409:fix` count 2. It has no `project`- or
`phase`-layer `replan` or `fix` entry, so there is still no pilot data for question 5. **No change.**

## Evidence

The logs are local, and each one's first line is `head=ff976406…`:
- `/tmp/cr8219-regowed.log` (rc 0)
- `/tmp/cr8219-scope.log` (rc 1, explained in Q1)
- `/tmp/cr8219-reqcov.log` (rc 0)
- `/tmp/cr8219-rs.log` (rc 0)

The records read: `docs/roadmap.md`, `docs/findings/register.md`, `docs/open-questions.md`, `CR-1247`,
and the front matter of each FD, RL, PL and SL named above, all at ff976406.

## Index — proposal → record → owner → state

| Item | Family (§1.6) | Working id | Owner | State | Its dated line |
|---|---|---|---|---|---|
| E1 WF-701 exit-demo run (option b) | PL delta, `relates: [PL-1544]` | PL 8224 | the planner; WK-1178 | accepted | line 6, first sentence |
| E2 the full PL-1544 run, Mon 9 Nov 2026 | SL row + LG | SL 8225, LG 8226 | WK-1178 | accepted | line 6, "E2 — the run" |
| E2 row 6b, a WF-701 browser check | rides E1's PL delta | PL 8224 | the planner | accepted | line 6, "and **yes**" |
| E3-B OQ-1222 and OQ-1224 → Before Phase 3 | RL (three lines) | RL 8220 | the decision-maker; the §10 edits by the lead | accepted | line 1 |
| E3-C OQ-1285's label → Before Phase 3 | the same RL | RL 8220 | the decision-maker | accepted | line 1 |
| E4 the any-marker process finding | dated `process-backlog.md` row (no id) | — | WK-1178; the lead files it in the next docs PR | accepted | line 2 |
| E5 provenance and diagnostics views | new P3 WK row, `draft` | WK id at the review PR (not reserved) | the maintainer opens it; the planner writes its map plan in P3 | accepted | line 3 |
| E5 the shared `provenance` object | OQ (P3) | OQ 8222 | the decision-maker | accepted | line 3 |
| E5 FD-1723's owner cell | register edit | — | the auditor, in the same PR | accepted | line 3 |
| E7.1 FR-109's finer-level view | rides E5's WK row | — | the E5 Work row | accepted | line 3, "E7.1 rides this row" |
| E6 OQ 8206: unpaginated, with a cap of 500 | RL closing OQ 8206 | RL 8221 | the decision-maker; minted after OQ 8206 mints in S10's PR | accepted | line 4 |
| E6 the gate row | joins "Before the P2 exit demo" (+1) | — | the lead, in SL-1552's PR | accepted | line 4 |
| E7.2 FR-127 `spliced` and `excess` | new P3 modelling WK row, `draft` | WK id at the review PR (not reserved) | the maintainer opens it | accepted | line 5 |
| E7.2 the parameter forms | OQ (P3), then the FR-127 amendment with the Work's first slice | OQ 8223 | the decision-maker | accepted | line 5 |
| T1 `CR-1247` P9's three records | owner or withdrawal | — | the lead names one | **proposed** | none yet |
| T2 `CR-1247` P6's team-wide boundary | owner or withdrawal | — | the lead names one | **proposed** | none yet |
| FD-1723 FR-110 `power(k)` | build or strike | — | the maintainer | **owed** | none yet |

## The maintainer's dated lines, verbatim (the entry 2026-10-25 11:32:17 GMT)

1. "**E3-B — ACCEPTED: (i) "Before Phase 3" for both OQ-1222 and OQ-1224**, owner WK-1178 unchanged, for the reasons r5 gives (the interim is loud; OQ-1224's `model-schema` change would re-hash the demo's approved version). **E3-C — ACCEPTED:** OQ-1285's row label "Before WK-675 S12" → "Before Phase 3" (S12 moved 2026-10-03, roadmap:1302). One **RL**, decision-maker, three lines; the §10 row edits (Before-Phase-2 count 2 open → 0, Before-Phase-3 gains the three ids, each with a dated move line) by the lead in the RL's PR. No dated line inside the OQ texts — the gate row carries the timing."
2. "**E4 — a dated process-backlog row now** (L5, as 11:25:21), owner WK-1178, lead files it in the next docs PR. An RFC only if the row is still open after the 12 Nov exit demo."
3. "**E5 — ACCEPTED: a new P3 Work row, `draft`**, titled to name both views: *"Provenance and diagnostics views: the per-artifact `produced_by_job_id` display (narrowed FR-6) and the finer-level diagnostics view on the stored grouping chain (FR-109)"*. This dated line opens it; the lead adds the row in the review's PR citing this heading, the planner writes its map plan in P3, I set `active` then. Spec change first (§0): the shared `provenance` object is a P3 **OQ** (decision-maker), not an FR yet. E7.1 rides this row as 11:38:45 (B) accepted. The register's FD-1723 owner cell is updated by the auditor in the same PR."
4. "**E6 — decided (ii): unpaginated with a cap.** The named figure: **500 rating versions in one workspace**, measured as the row count of `rating_versions` per workspace on any real or demo workspace at each §14 review; a workspace above 500, or a measured `GET /api/v1/rating-versions` p95 above the platform's list budget, reopens the OQ as a slice under option (i). Record: the **RL** (decision-maker) closing OQ 8206, minted in the review's PR after OQ 8206 mints in S10's. **Gate-row form: JOIN the existing "Before the P2 exit demo" row (count +1)**; the S10 branch's new "…§14 plan review" row is folded into the existing row by the lead in SL-1552's PR before its gate (the branch is unmerged, so this is not a plan edit)."
5. "**E7.2 — ACCEPTED, the primary: a new P3 modelling Work row, `draft`**, *"FR-127 `spliced` and `excess` loss treatments: parameters, fit path and `spec_hash`"*, opened by this line the same way as E5's row; spec change first — an **OQ** (decision-maker) for the splice-point / excess-layer parameter forms, then the FR-127 amendment with the Work's first slice. The fallback is not needed."
6. "**E1 — option (b):** the exit demo shows WF-701 from a pre-seeded state; one **PL delta** (planner) `relates:` the exit-demo plan, recording the live run's measured duration as an observation with **no budget** (a cap from the fit stays refused). **E2 — the run:** one full PL-1544 checklist run (rows 0–9, row 6 included) on the exit tree on **Mon 9 Nov 2026**, owner WK-1178, as an **SL** row + LG; and **yes**, add a WF-701 browser check as row 6b by the same PL delta as E1, since the demo shows WF-701."

## Verdict

Every item E1–E7 has a family, an owner and a working id or a named row. All five questions are
answered, and every one of the 33 decayed register rows has a disposition. Three items are still
proposals, with no dated line yet: T1, T2 and FR-110. The lead gives a verdict on each, or the
maintainer gives a line. **Nothing here binds** beyond the six dated lines quoted above.

## Acceptance

**Maintainer acceptance:** E1–E7 accepted in the maintainer's entry `2026-10-25 11:32:17 GMT — Maintainer: §14 note r5 — the six owed rulings, decided now (dated lines for the review's rows)` (`to-lead.md`).
The register dispositions, T1, T2 and the review as a whole: _pending_.
