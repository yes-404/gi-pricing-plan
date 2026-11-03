---
id: CR-1981
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-673 Work close audit — Dislocation with attribution
status: active                  # write-once; this is the only value this family ever takes
created: 2026-11-03   # drafted 2026-11-03 under working id 8292
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: c807a59d1a26d12e63d88bc395ac3dcc373aa919
phase: P2
work: WK-673
corrected_by: []
relates: [PL-1267, RL-1264, RL-1504, CR-1212, CR-1907, FD-1358, FD-1481, FD-1490, FD-1491, FD-1495, FD-1576, FD-1578, FD-1586, FD-1651, FD-1757]
---

# CR-1981 — WK-673 Work close audit

*Working id CR 8292, reserved by the lead; minted as CR-1981 at the lead's id turn. The auditor seat
aud-wk673 wrote this record on 2026-11-03 from 15:47 GMT. The instruction is the lead's brief
`brief-aud-g1close-2026-11-03.md`, on the maintainer's entry "2026-11-03 15:36:59 GMT" item (5)
(the G1 close schedule) and the user's order in the entry "2026-11-03 15:46:13 GMT" (both in
`~/gi-pricing-plan.local/channel/to-lead.md`). It follows `.claude/skills/close-workstream`,
`CLAUDE.md` §13 and §14.*

**What this record is.** It gathers evidence and **proposes**. Every §13 verdict below is
written "PROPOSED" and is the lead's to give. **The close is the user's dated acceptance line.**
This record does not close WK-673. The roadmap row it edits says "close audit filed,
acceptance owed".

**Object.** `origin/main` at `c807a59d1a26d12e63d88bc395ac3dcc373aa919` (tree
`10b01c900d7303394ca514dcc7c631a85e699508`), read with `git ls-remote origin main` at the
start. Every `file:line` and every count below is at that tree unless it names another.
Branch `docs/wk673-close-audit-2026-11-03`, cut from that commit.

## Scope

### §0. The requirement set, derived from the documents before any evidence

**Predicate** (runnable from the repository root at `c807a59d`). The union of the ids cited by
the WK-673 roadmap section (`docs/roadmap.md:686`, up to the next `### WK-` heading at `:1023`)
and the 15 plans whose front matter reads `work: WK-673`:

```bash
( sed -n '686,1022p' docs/roadmap.md
  cat $(git grep -l '^work: WK-673' -- docs/plans)
) | grep -ohE '\b(FR|NFR)-[0-9]+\b' | sort -u -V
```

It prints **74 ids**. Each id was mapped to its module by the spec that holds its
`| **<id>** |` row (`**Module code:**` header line of each `docs/specs/0*.md`).

**Requirements axis, the whole predicate (a widening check).** `scope-audit.py` takes one
module per run. The script has no third-party import, so it ran as `python3` through
`run-heavy.sh --grant "2026-11-03 15:46:13 GMT"` (not `--light`, which refuses any script but
`audit-docs.py` and `doc-index.py`, rc 78). `--sections NONE` selects no section, so only the
`--extra` ids are in scope:

```bash
python3 scripts/scope-audit.py <MOD> --sections NONE --extra <the module's ids from the predicate>
```

| Module | In scope | With a `@pytest.mark.req` marker | No marker | rc |
|---|---|---|---|---|
| RATE | 52 | 51 (98%) | NFR-493 | 1 |
| MODEL | 7 | 7 | — | 0 |
| GOV | 6 | 5 (83%) | FR-365 | 1 |
| DATA | 3 | 3 | — | 0 |
| PLAT | 3 | 3 | — | 0 |
| OVR | 2 | 2 | — | 0 |
| OPT | 1 | 0 | FR-294 | 1 |
| **Total** | **74** | **71** | **3** | |

The three unmarked ids are context, not WK-673 deliverables: FR-294 is `04`'s GIPP check, Phase 4
(WK-685), named by `PL-1499:203` only to say GIPP cannot be enabled yet; NFR-493 is the batch
throughput floor, cited by `PL-1267:324` and `PL-1452:326` as a cost input; FR-365 is option (a)
of `PL-1267:360`'s DP-3, not taken.

**WK-673's own deliverable set is 16 ids**, the rows of §1's table:

- the roadmap row's ten (`docs/roadmap.md:698`, "From Workstreams"): FR-263, FR-264, FR-265,
  FR-266, FR-224, FR-257 (limb (2) only), `06` FR-364, FR-231 (F-W10-2, the exposure-weight limb
  only), NFR-495 and NFR-496 (applied to this Work's artifacts) — the same ten as `PL-1267`'s
  "Requirement coverage" table (`PL-1267:272-285`);
- the three requirements this Work minted: FR-1397, FR-1398 and FR-1399 (SL-1385's closing line,
  `docs/roadmap.md:725`);
- the three requirements a WK-673 fix slice was cut against: FR-221 (SL-1448, FD-1420), FR-240
  (SL-1472, FD-1422 and FD-1469) and FR-242 (SL-1503, SL-1678, SL-1702).

The other 58 ids are context or another Work's. The WK-673 row carries no count, so there is no
count to reconcile. `PL-1267`'s acceptance item 2 names the same ten as the row.

```bash
python3 scripts/scope-audit.py RATE --sections 3.9 \
  --extra FR-224,FR-257,FR-231,NFR-495,NFR-496,FR-240,FR-242,FR-221 --endpoints
python3 scripts/scope-audit.py GOV --sections none --extra FR-364 --endpoints
```

RATE: `3.9 Dislocation 7/7 evidenced` (FR-263 to FR-266, FR-1397 to FR-1399), the eight extras
each `evidenced`, "in scope: 15, with evidence: 15 (100%)", rc 0. GOV: FR-364 `evidenced`, "in
scope: 1, with evidence: 1 (100%)", rc 1 from the endpoint axis only (below).

**Endpoints axis.** RATE: "declared: 45, published: 45 (100%) — every declared endpoint is
published in the contract". The four `dislocation-runs` routes are `03-rating-engine.md:1123-1126`.
GOV: "declared: 23, published: 13 (57%)", ten not published: `GET /api/v1/artifacts/{}/history`,
`GET /api/v1/roles`, `POST /api/v1/attestations`, `POST /api/v1/audit/anchor`,
`POST /api/v1/break-glass`, `POST /api/v1/dossiers`, `POST /api/v1/dossiers/{}/commentary`,
`POST /api/v1/regulatory-exports`, `POST /api/v1/role-assignments`, `POST /api/v1/roles`. None is
in WK-673's scope (`06` §3.1, §3.4–§3.6 are P3 governance). WK-673 adds no GOV route.

**Catalogue axis.** `03` and `06` declare no catalogue in the form the script reads (the same
result as `CR-1952` §0 for `03`). Nothing to compare.

**Assigned elsewhere, kept out of WK-673's verdicts** (`PL-1267:293-297`): the Dislocation view
(`03` §5.3) is WK-675's; FR-257 limb (1) is WK-672 Slice 3's (RL-1172 item 4), limb (3) is
already enforced, limb (4) is `04`'s; NFR-496's production-sampling limb is WK-674's (CR-1212).

**§0a and §0b.** Every one of the 16 ids carries a marker (marker count per id, `git grep -c -E
'mark\.req\([^)]*"<id>"' -- '*.py'` summed: FR-263 52, FR-264 11, FR-265 5, FR-266 13, FR-1397 6,
FR-1398 15, FR-1399 24, FR-224 20, FR-257 28, FR-231 65, FR-364 21, NFR-495 9, NFR-496 8, FR-240
77, FR-242 6, FR-221 17). The load-bearing asserts were read; they are in §1.

## Evidence

### §1. Each deliverable: exists and works

"Works" means the cited test asserts the requirement's own clause; each was read.

| Id | Exists (code) | Works (the assert read) |
|---|---|---|
| FR-263, FR-264 | `dislocate` `packages/pricing-core/src/pricing_core/rating/analysis.py:493`; Job handler `backend/src/app/worker/dislocation_handlers.py:244` | `test_rating_dislocation.py:690` asserts integer totals 8800/9580 over a 16-row book with a stated mutation; `:798` by-rung parts sum to the total |
| FR-265 | `POST /api/v1/dislocation-runs` `backend/src/app/api/dislocation_runs.py:71`, `GET …/{id}` `:139`, `GET …/{id}/movers` `:185` (typed `list[DislocationMover]`, so LG-1570's "/movers untyped" known gap is closed) | `backend/tests/test_dislocation_runs.py` (5 FR-265 markers); `dislocation-run` is in `COMPARED_SLUGS` (`backend/tests/test_contracts.py:47`, one hit), not one-sided — `PL-1267` acceptance 6 met |
| FR-266, FR-1397 | `_shapley_numerators` `analysis.py:966`, `_allocate` (largest remainder, ties in index order) `:979`, `_residual` `:993`, `_reconcile` `:998`; `attribute` `:1059` | `test_rating_attribution.py:594` exact Shapley against a formula and hand values; `:602` ties in declared order; `:624` plain rounding **refused** with `ATTRIBUTION_RECONCILIATION_FAILED`; `:636` a Shapley part perturbed by one minor unit **refused**; `:653` residual off by one **refused** — `PL-1267` acceptance 4 met |
| FR-1398, FR-1399 | subsets compiled and scored on ZEN; changes derived one per step id (`derive_changes` `analysis.py:762`) | `test_rating_attribution.py:299-549` (derivation, partition refusal `:459`, a non-compiling subset fails the run by name `:471`); `test_dislocation_runs.py:443` subset bundles never become Rating Versions — `RL-1264`'s negative tests (`PL-1267` acceptance 11, Slice 1/3 limb) |
| FR-224 | `_approximation_gate` in `submit_for_review` (`backend/src/app/platform/rating_versions.py:344`); `ApproximationDeviation` and `DEFAULT_POLICY` `packages/model-schema/src/model_schema/approvals.py:376` | `backend/tests/test_rating_version_dislocation_gate.py:589` above the threshold refused `EVIDENCE_INCOMPLETE` 422 naming the quantile and the figure, no Approval Request opened; `:605` no exact twin refused; `:650` threshold ignores six `GIP_` variables |
| FR-257 limb (2) | `dislocation_run_verified` `rating_versions.py:1253` | `test_rating_version_dislocation_gate.py:91` (no run), `:104` (stale hash), `:123` (baseline not live): each asserts `EVIDENCE_INCOMPLETE`, 422, `"FR-257 limb (2)"` in the detail, status stays `draft`, no request row — `PL-1267` acceptance 7 met in the code |
| `06` FR-364 | `structural_diff_verified` `rating_versions.py:1247`; the floor map `:444`, `rate_table_diffs_unproduced` `:431` | `test_rating_version_dislocation_gate.py:246-331`; `test_rating_version_evidence_floor.py`. **The `rate_table_diffs` limb is not built** — §5 |
| FR-231 (weight limb) | `weight` per cell `packages/model-schema/src/model_schema/rating.py:1319`; `GET /rate-tables/{slug}@{version}/diff/cells` `backend/src/app/api/rate_tables.py:490` | `backend/tests/test_rate_table_diff_portfolio.py:325` hand-computed weighted figures (`-1.428571`, exposure 7.5/7.5); `packages/pricing-core/tests/test_rate_table_weights.py:84-248` |
| NFR-495 (applied) | — | `test_rating_dislocation.py:1008` and `test_rating_attribution.py:983`: byte-identical output from two fresh interpreters; the comparator shown able to fail when the portfolio changes (`test_rating_dislocation.py`, `test_the_comparator_can_fail_when_the_portfolio_changes`) |
| NFR-496 (applied) | — | `test_rating_dislocation.py:690` (totals are `int`, sums of per-policy minor units); reconciliation to the minor unit on every attribution (`_reconcile`, refusals above) |
| FR-221 | lookup as at the declared date (SL-1448) | `packages/pricing-core/tests/test_rating_lookup_as_at.py:150`, `:158` |
| FR-240 | `_refuse_unapproved_objectives` in `compile.py`; `CONTROL_FACTOR_IN_RATEABLE_PATH` (SL-1472) | `backend/tests/test_fr240_governance.py:124`, `:147` |
| FR-242 | `draft_change_summary_for` `rating_versions.py:1329`; pairing through the `table` step (SL-1702) | `backend/tests/test_change_summary_draft.py:44`, `:65` |

`PL-1267` acceptance 3 (FR-266's amendment): `03-rating-engine.md:195` carries "exact Shapley",
"largest remainder", "declared order", "cumulative", "residual" and "K ≤ 6". Acceptance 1: seven
leaf plans `PL-1395`, `PL-1403`, `PL-1452`, `PL-1501`, `PL-1500`, `PL-1499`, `PL-1419`, all
`work: WK-673`.

**The §5 retrofit-impossible list.** WK-673 consumes these invariants and regresses none: the
run and the attribution are integer minor units (`int` asserted at `test_rating_dislocation.py:695`);
the persisted run is a declarative, compared contract; no shape is hand-written.

### §2. The gate

Every slice row is `closed` (`docs/roadmap.md:706-1022`, 15 rows). Each squash commit is on
`origin/main`'s first-parent line; `git merge-base --is-ancestor <sha> c807a59d` printed 0 for all
15 and for SL-1543's `4a53f194`.

| Slice | PR | Squash | MERGE-ACK (`to-lead.md` heading) | Gate of record (the LG) |
|---|---|---|---|---|
| SL-1385 | #1094 | `1ab1776d` | 2026-10-03 23:28:41 BST (conditional) | LG-1400:322 "GATE: pass — 13 of 13", 4624 passed |
| SL-1386 | #1107 | `f68db62a` | 2026-10-04 18:13:35 BST | LG-1406:303 pytest pass, 4841 passed |
| SL-1387 | #1243 | `e40ab532` | 2026-10-10 01:42:52 BST | LG-1545:206-208, 13 check-31 reds + 3 fixed; lead's §13 verdicts `:361` |
| SL-1388 | #1256 | `84ff9f0b` | 2026-10-10 05:13:20 BST | **Gate table empty** (LG-1570:38); build log `:71` re-gate at `648ee30e`, audit-docs check 31 only; CI 4/4 in the ACK |
| SL-1389 | #1260 | `db0642c4` | 2026-10-10 08:40:44 BST | **Gate table empty** (LG-1582:36-40); build log `:105` gate file 24 passed; CI 4/4 in the ACK |
| SL-1390 | #1279 | `3065770c` | 2026-10-11 16:11:02 BST | **Gate table empty** (LG-1633:46-50); build log `:87`; CI in the ACK |
| SL-1391 | #1206 | `a9ef6777` | 2026-10-06 01:46:18 BST | LG-1444:417, 13 failed (the check-31 set) |
| SL-1436 | #1228 | `2b83e089` | 2026-10-06 04:23:19 BST | LG-1467:543 pytest pass, 5064 passed; frontend all rc 0 `:545` |
| SL-1448 | #1236 | `680fb9ac` | 2026-10-08 13:05:49 BST | LG-1487:160, 13 failed (check-31) |
| SL-1472 | #1247 | `7e3a4803` | 2026-10-08 20:01:03 BST | LG-1533:88, 13 failed (check-31) at `d06b9d1e` |
| SL-1503 | #1285 | `1b04cb05` | 2026-10-11 23:11:42 BST | LG-1642:70, 13 failed (mint artefacts) |
| SL-1678 | #1296 | `36e2610a` | 2026-10-12 09:02:11 BST | LG-1681:85, 13 failed (check-31) |
| SL-1695 | #1306 | `beee5ebe` | 2026-10-14 16:09:23 BST | LG-1718:53, 13 failed (check-31) |
| SL-1696 | #1310 | `6b25b9bc` | 2026-10-16 22:17:50 BST | LG-1732:65, 13 failed (check-31) |
| SL-1702 | #1309 | `a2f77b2d` | 2026-10-16 10:24:40 BST | LG-1731:68, 17 failed; classified by the lead (`:96`) |

**Fresh full gate: OWED — the lead schedules it; head = the head of
`docs/wk673-close-audit-2026-11-03` at that time.** This seat ran no test and no gate.

### §3. New checks proven on broken input

| Check | Broken-input proof | Where |
|---|---|---|
| Reconciliation (FR-1397) | plain-rounding and ±1 perturbed allocators refused | `test_rating_attribution.py:616-664` (the injections live in the tests and run on every gate) |
| Replay exactness (`PL-1267` acc. 5) | red with `replay_subset`'s multiply broken | LG-1545:181-182 |
| Attribution mount guard / fix (FD-1660) | Step 0b, 12 of 12 red on pre-guard source | LG-1732:82-94 |
| Change-summary pairing (FD-1679) | guard `if` disabled, 6 failed | LG-1731:52-60; LG-1681:71 |
| `06` FR-364 floor loop (SL-1390) | `broken1.rc` = 1, `broken2.rc` = 1 in `~/gi-pricing-plan.local/scratch/sl1390/gatelogs/` (local, not quoted in any record) | **FD-1651 open**, its discharge date "no later than Fri 2026-10-23" passed |
| FR-257 limb (2), FR-224 refusals (SL-1389) | **none recorded.** LG-1582:69-74 lists the red-first of acceptance items 2, 5, 6 and 15 as "OWED"; the test docstrings still read "(OWED: scratch-reverted)" at `test_rating_version_dislocation_gate.py:656`, `:696`, `:732` | **FD candidate 1** (Findings) |

### §4. NFRs

- **NFR-495, NFR-496 (applied to this Work's artifacts):** property NFRs, tested by assertion (§1),
  not timed. No measurement is owed.
- **The attribution cost** (`PL-1267` acceptance 5): measured in LG-1545:279-296, `attribute` on the
  first 20,000 freMTPL2 policies by `scripts/measure-attribution-cost.py cost`: K = 3 median
  366.85 s (N = 5, load1 1.80–2.85), K = 4 median 734.73 s (N = 5), K = 6 3,024.77 s (**N = 1**, not
  5 — disclosed at LG-1545:285). No FR or NFR bounds a Dislocation Run, so no verdict is drawn;
  **FD-1576** carries it (owner WK-673, MEDIUM; "discharged before WK-673's Work close or carried
  by name at P2's close"). Nothing of WK-673 is owed to nfr-bench-1 (Thu 5 – Fri 6 Nov 2026)
  unless the lead routes FD-1576's measured run there.

### §5. Every requirement without evidence, with a PROPOSED verdict

All 16 ids carry a marker. The limbs and owned obligations below lack evidence:

| Item | PROPOSED verdict |
|---|---|
| `06` FR-364's `rate_table_diffs` limb. The amendment (`06-governance.md`, FR-364, "Amended 2026-10-10 (WK-673 Slice 6, RL-1504)") reads "owner: WK-673, the slice named in Slice 6's dispatch record"; LG-1633:80 names a new WK-673 slice, working id SL 9965, "the row is not created here". No such row exists in WK-673's section, and no register row carries it. | **PROPOSED: not started** — owner WK-673 by the spec; the slice row is owed or the obligation is re-owned by a dated line. FD candidate 2. |
| LG-1545's §13 verdicts 1 and 2 (the lead, 2026-10-10 01:15:46 BST, LG-1545:363-364): the per-set S figures of Acceptance 20 and the 690/976 per-policy maxima, "deferred with an owner. Owner WK-673; discharged before WK-673's Work close". No WK-673 commit touched `scripts/measure-attribution-cost.py` after `e40ab532` (`git log e40ab532..HEAD -- scripts/measure-attribution-cost.py` prints only `1aab7a21`, WK-1178's SL-1575). No register row. | **PROPOSED: deferred with an owner (WK-673), undischarged** — needs a register row or discharge before acceptance. FD candidate 3. |
| FR-257 limb (2) and FR-224: the refusals' broken-input proofs. | **PROPOSED: delivered but untested on broken input** — FD candidate 1. |
| `06` FR-364 floor loop: the two broken-loop proofs. | **PROPOSED: delivered but untested on broken input** — FD-1651, open and past its date. |
| The full-book attribution cost. | **PROPOSED: deferred with an owner** — FD-1576 (WK-673, or carried by name at P2's close per its row). |

### §5a. Binding plan-review conditions

`CR-1907` (plan review 17, accepted 2026-10-25 11:32:17 GMT) does not name WK-673:
`grep -c 'WK-673' docs/closures/CR-01907-*.md` prints 0. No later review exists (the `kind:
review` CRs naming WK-673 end at `CR-1247`, 2026-09-29). The earlier conditions on WK-673:

| Condition | Artifact | State |
|---|---|---|
| `CR-1212` L60: F-W9-2 (FR-224) → WK-673 | SL-1389 (#1260) | delivered; register row `register.md:60` still reads "carry forward" — closing act owed |
| `CR-1212` L64: F-W10-2 (FR-231 weight) → WK-673 | SL-1391 (#1206) | delivered; `register.md:64` still open — closing act owed |
| `CR-1212` Proposal 2 / `CR-1247` P12: WK-674 then WK-673 then WK-675; exit demo after WK-673 and WK-674 | sequencing | met |
| Roadmap `:569` (2026-10-12): G2 needs SL-1543, SL-1695 and SL-1696 merged | `4a53f194`, `beee5ebe`, `6b25b9bc` | met |

### §5b. The owed list, generated

```text
Generated by `python3 scripts/register-owed.py WK-673` against `c807a59d (`docs/wk673-close-audit-2026-11-03`)`.
Mode: work item 'WK-673'. 21 owed row(s), 2 matched but excluded as opening with a resolution marker.
```

The 21, by register line: `:60` FR-224 (F-W9-2), `:64` FR-231 (F-W10-2), `:85` FR-257 (F44),
`:285` FD-1358, `:297` FD-1420, `:299` FD-1422, `:301` FD-1425, `:303` FD-1433, `:305` FD-1439,
`:307` FD-1469, `:311` FD-1481, `:316` FD-1490, `:317` FD-1491, `:321` FD-1495, `:332` FD-1576,
`:333` FD-1578, `:335` FD-1586, `:346` FD-1651, `:383` FD-1754, `:386` FD-1757, `:424` FD-1954.
Excluded by the script: FD-1660 (Resolved 2026-10-16, #1310) and FD-1679 (Resolved 2026-10-22,
`a2f77b2d`).

**Read by hand.** Eight rows are removed. Six carry "Resolved" mid-cell (the known defect): FD-1420
(`:297`, Resolved 2026-10-08, SL-1448 `680fb9ac`), FD-1422 (`:299`, 2026-10-09, SL-1472),
FD-1425 (`:301`, 2026-10-06, SL-1436), FD-1433 (`:303`, 2026-10-06; owner WK-1178), FD-1439
(`:305`, 2026-10-06, SL-1391 — **its essay still reads `status: active`**, a closing act owed) and
FD-1469 (`:307`, 2026-10-09, SL-1472). Two are not WK-673's: FD-1754 (`:383`, owner WK-1178) and
FD-1954 (`:424`, owner WK-675, Resolved 2026-10-29).

**The corrected list, 13 rows owed by WK-673:**

| Row | State at `c807a59d` | Owed |
|---|---|---|
| `:60` FR-224 (F-W9-2) | delivered, SL-1389 | closing act |
| `:64` FR-231 (F-W10-2) | delivered, SL-1391 | closing act |
| `:85` FR-257 (F44) | limb (2) delivered, SL-1389; limbs (3), (4) not WK-673's | a limb-(2) dated annotation |
| `:285` FD-1358 | delivered: RL-1418 and SL-1391; `weight` per cell `rating.py:1319`, the `diff/cells` route | closing act |
| `:335` FD-1586 | fixed: `awk 'length>300' docs/specs/03-rating-engine.md \| sort \| uniq -d \| wc -l` prints 0 | closing act |
| `:386` FD-1757 | fixed by SL-1543 (#1335, `4a53f194`): `examples/fremtpl2/seed.py:150-157` keeps an unknown amount null | closing act |
| `:311` FD-1481 | open: the ruled characterisation test does not exist (`git grep -n 'FD-1481' -- '*.py'` prints nothing) | test |
| `:316` FD-1490 | open: `MONETARY_FLOAT_REFUSED` is registered at `backend/src/app/errors.py:323` and raised nowhere in `packages/*/src` or `backend/src` | code or unpublish |
| `:317` FD-1491 | open: waits on the spec ruling on FR-229 | ruling, then test |
| `:321` FD-1495 | open: the HIGH limb closed by SL-1472; `RL-1470` (c) limb carries to WK-673 | code |
| `:332` FD-1576 | open, MEDIUM | measured run, or carried by name at P2 close |
| `:333` FD-1578 | open: `class AttributionError(ValueError)` at `analysis.py:521`; the reconciliation message still names the quote id (asserted at `test_rating_attribution.py:632`, `:649`) | code |
| `:346` FD-1651 | open, past its 2026-10-23 date | proofs quoted |

The lead's evidence pass listed 12 (FD-1358, 1420, 1422, 1425, 1469, 1490, 1491, 1495, 1576,
1578, 1651, 1757). Against the hand read: FD-1420, 1422, 1425 and 1469 are resolved; FD-1481,
FD-1586 and the three F-rows (`:60`, `:64`, `:85`) are owed and missing from it.

### §5c. Workflow steps that cite this close's requirements

```bash
git grep -n -E '\b(FR-(263|264|265|266|1397|1398|1399|224|257|231|364|240|242|221)|NFR-(495|496))\b' -- 'docs/workflows/WF-*.md'
```

18 lines at `c807a59d`. Seven are not steps (the failure table `WF-699:113-114`, the phase map
`WF-699:137-140`, `WF-700:139`, the precondition `WF-701:28`). The steps, each read against the
requirement to its end with every dated amendment:

| Journey | Step | Ids | Verdict |
|---|---|---|---|
| WF-699 | A3 (`:43`) | FR-231 | still says it (RL-1418 serves the weight per cell) |
| WF-699 | B3 (`:58`) | FR-221 | still says it |
| WF-699 | C3 (`:72`), C4 (`:73`) | FR-240 | still says it (FR-240's transitive clause, `03:140`) |
| WF-699 | D6 (`:86`) | FR-263 | still says it |
| WF-699 | D7 (`:87`) | FR-263/264/266 | still says it (attribution over derived, groupable changes, FR-1399) |
| WF-699 | D8 (`:88`) | FR-266 | still says it |
| WF-699 | E1 (`:95`) | FR-242 | still says it (drafted from the structural and rate-table diffs, amended 2026-10-14) |
| WF-699 | E2 (`:96`) | FR-257/260, `06` FR-352/363 | **disagrees.** E2 says "evidence completeness is checked at submission: structural diff, **rate diffs**, regression run, dislocation run, GIPP check where enabled, change summary". `06` FR-364's 2026-10-10 amendment says `rate_table_diffs` "has no persisted artifact yet and is refused, naming the kind, when a policy names it", and `DEFAULT_POLICY`'s `rating_version` entry names `("structural_diff", "regression_run", "dislocation_run")` only (`approvals.py`, the entry after `:376`). No rate diff is checked at submission. FD candidate 2. |
| WF-700 | E5 (`:91`) | FR-266 | still says it |
| WF-700 | E6 (`:92`) | FR-263 | still says it |

## Findings

No id is written here; each is the lead's to file.

1. **FD candidate 1 — SL-1388 and SL-1389 closed with no slice audit, and SL-1389's red-first
   proofs were never recorded.** LG-1570:38-44 and LG-1582:36-44 hold an empty Gate table and the
   placeholder "(Written by the auditor at slice close.)"; no `RS-` or `CR-` covers either
   (`git grep -l -E 'SL-1388|SL-1389' -- docs/research docs/closures` prints nothing; RS-1649's
   retro audit covers SL-1390, not these). LG-1582:69-74 lists the red-first of acceptance items 2,
   5, 6 and 15 as OWED and nothing later discharges them; `PL-1267` acceptance 11's FR-224
   environment-variable test is therefore not shown red. The same class as FD-1651. Proposed
   MEDIUM (a governance record that reads complete and is not).
2. **FD candidate 2 — `06` FR-364's `rate_table_diffs` limb has an owner (WK-673) and no row, and
   WF-699 E2 says it is checked.** §5 and §5c above. The working id SL 9965 that LG-1633:80 names
   was also spent elsewhere (RL-1322 "filed under working id 9965", minted in batch 6). Proposed
   MEDIUM: off the G2 path (the default policy does not name the kind), but the journey states a
   check the platform does not make.
3. **FD candidate 3 — two WK-673-owned deferrals live only in LG-1545.** §5 above. Invisible to
   `register-owed.py` because no row carries them: the F41 shape `close-workstream` §5b exists to
   catch. Proposed LOW (no price moves; the record is incomplete).

Closing acts owed (not findings): the register rows `:60`, `:64`, `:85` (limb (2)), `:285`,
`:335`, `:386` and FD-1439's essay status; LG-1570, LG-1582 and LG-1633's empty Gate tables.

## Replan check (`CLAUDE.md` §14, `RFC-1248`)

1. **Completion — yes.** The roadmap row names ten ids; the Work also minted FR-1397–FR-1399 and
   owns FR-364's `rate_table_diffs` limb by the spec, which no row names. It moves no scope.
2. **Omission — yes.** The `rate_table_diffs` slice row (FD candidate 2) and LG-1545's two
   deferrals (FD candidate 3) are needed and unnamed. Neither is on the G2 path.
3. **Skills and research — yes.** As at CR-1952: `close-workstream` §0's `scope-audit.py` cannot
   run through `run-heavy.sh --light` (rc 78); this audit ran it through `run-heavy.sh` without
   `--light`. `register-owed.py` counts mid-cell "Resolved" rows as owed (8 of 21 here), already a
   backlog row (to-lead 15:36:59 item 5). Neither moves scope.
4. **Drift — yes.** WF-699 E2 against `06` FR-364 (§5c). It moves no slice or phase.
5. **Shape — no.** No phase boundary or Work scope moved since CR-1907 (2026-10-25).

`register-owed.py review` at `c807a59d`: **29 owed rows** (11 excluded as opening with a
resolution marker).

**Triggers:**

- A phase boundary or Work scope moved: **not fired**.
- An exit criterion at risk: **not fired, watched.** G1 needs WK-673 accepted before the exit demo
  (Wed 18 Nov 2026, the user's calendar of 2026-11-03 15:38:58 GMT); the close is scheduled for
  Fri 6 Nov. Six code-or-test rows (FD-1481, 1490, 1495, 1578, 1651 and candidate 1's proofs) plus
  a ruling (FD-1491) remain against a code freeze of Tue 10 Nov.
- A replan decided: **not fired**.
- A finding that moves a slice or a phase: **not fired.** FD candidate 2 adds a slice inside
  WK-673 or re-owns the limb; it moves no phase.

**PROPOSED:** no full review now; the risk line is carried to the §14 review before the exit demo
(the week of Mon 16 Nov). **The verdict is the lead's.**

## Verdict

PROPOSED: **not ready for acceptance at `c807a59d`.** The deliverables exist and work: all 16 ids
carry read assertions (§1), the reconciliation is proven on broken input, and every slice merged
on a MERGE-ACK with green CI. The close is blocked by:

1. the open WK-673 rows: FD-1481, FD-1490, FD-1491, FD-1495, FD-1576, FD-1578, FD-1651 (§5b);
2. FD candidates 1 to 3 (filing, then a disposition each);
3. the closing acts on six register rows and FD-1439's essay (§5b);
4. the fresh full gate (OWED).

The §5 verdicts are proposals. **The close itself is the user's dated line.**
