---
id: LG-8155
family: ledger
title: WK-1178 slice SL-1736 — the P2 NFR measurement sweep (NFR-467, 468, 470, 485, 1443 DIAGNOSTIC; NFR-472 red-first) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
slice: SL-1736
plans: [PL-1735]
corrected_by: []
relates: [PL-1735, SL-1736, SL-1259, RL-1441, LG-1444, RL-1614, FD-1745, FD-1746]
---

# LG-8155 — WK-1178 slice SL-1736: the P2 NFR measurement sweep

Filed 2026-10-22 under working id 8155 (lead-reserved); executed by seat `exec-1736`, base
`origin/main` `f3462d8fc1336dc4583fe8a7af92fed399993a55`.

**GO:** the maintainer's entry "2026-10-22 11:53:15 BST — Maintainer: SL-1569 and SL-1736 slice GO; D1–D4 and the two orders ruled"; for this slice, verbatim: "**SL-1736** (WK-1178, PL-1735). Its non-ALONE prep may start now on a seat. **ORDER:** its 4 ALONE grants run after SL-1275 and SL-1711 merge, with the build seats parked. Each grant is requested from me with the exact commands. **D2:** Task 4's dated line goes under the row that owns the measurements now (roadmap :1278), not the closed SL-1259 row. **D3:** five runs. The plan's "six" is a miscount, and LG records the correction. **D4:** Task 0's load1 < 1.0 start allows up to 10 min to settle. Then record the reading and STOP to the lead, who brings it to me. I then rule: proceed at the reading, or move the grant to nfr-bench-1."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Quoted from the slice's Work-plan row, `docs/roadmap.md` `#### SL-1736` (`PL-1735` is the plan; WK-1178 has no Work plan, so the row is the slice's Work-plan row):

> NFR-468 (`01`: the one-way read, p95 < 300 ms, never computed), NFR-470 (`01`: storage ≤ 1.2× the parquet payload; dedup by content hash), NFR-485 (`02`: 5 M × 60 fit within 32 GB) and NFR-1443 (`03`: the cells-diff page p95 ≤ 300 ms, and the 2× property) are each measured on the shared VM with a committed instrument (`scripts/measure-p2-nfr-sweep.py`; `scripts/bench-model.py --peak hwm`), labelled DIAGNOSTIC, latency figures also "server-side, in-process, excludes network". Thresholds and reading rules are committed before the first run. […] **A reading that comes out OVER goes to the lead for an `FD-`. Its requirement's text is not changed.**

Requirements: NFR-467, NFR-468, NFR-470, NFR-472 (red-first test + fix), NFR-485, NFR-1443 (`PL-1735` "Scope and requirements").

**Activation commit (L1):** this ledger, the `SL-1736` row `status: active` with its dated line, and `PL-1735` `status: draft` → `active` ride the slice PR (the #1286 `cad75a7e` and #1331 `2bc4dc8c` precedent, as the GO entry's preamble confirms for PL-1735).

**Rulings of the GO entry that bind this ledger**
- **D2:** Task 4, Step 4's dated line goes under the roadmap row that owns the nfr-bench-1 measurements now (`docs/roadmap.md`, the "Dated 2026-10-19 … `nfr-bench-1` … owner row" line at `:1278`, in the `SL-1259` block's tail), not on the closed `SL-1259` row's own fields. `PL-1735` Task 4 Step 4 and its write set say "under `SL-1259`'s row"; the GO ruling changes the placement, and this ledger records the delta.
- **D3 — correction to the plan.** `PL-1735` says "Six runs" for NFR-1443 (NFR-1443 section, Instrument). The runs it lists are five: rows 10 000, rows 250 000, parquet 10 000, parquet 250 000, parquet 1 000 000. **The sweep runs five.** `LG-1444` Hold B is cited by the plan as "six" with the same list; the list, not the count, is followed.
- **D4:** Task 0's ALONE start requires load1 < 1.0. The executor may let it settle for up to 10 minutes; if it is still ≥ 1.0 it records the reading and STOPS to the lead, who brings it to the maintainer, who rules: proceed at the reading, or move the grant to nfr-bench-1.

### Task list

- [ ] Activation commit (L1): this ledger, the row, the plan status.
- [ ] Task 0 Step 2 (P0): `contention` subcommand and its constants, committed before any factor run.
- [ ] Task 0 Step 4 (P1): sweep constants, committed before any sweep run.
- [ ] Task 1: NFR-472 red-first test, then the fix (a DB test; owed a lead-granted DB lane).
- [ ] Tasks 2, 3, 5, 5a: `one-way`, `storage`, `cells-diff`, `profile` subcommands.
- [ ] Task 3 Step 4: NFR-470's dated clarification.
- [ ] Task 4: `bench-model.py --peak hwm`; the dated line (D2 placement).
- [ ] Task 6: gate, per-NFR rows, hand-off.

### Gate

Not yet run.

### Audit

Not yet written (auditor seat).

### Build log

#### 2026-10-22 — activation (tree `f3462d8fc1336dc4583fe8a7af92fed399993a55`)

Phase restriction in force: the SL-1711 compose retry is ALONE; edits and git only, no measurement and no test run until the lead releases it.

## PRs

None yet.
