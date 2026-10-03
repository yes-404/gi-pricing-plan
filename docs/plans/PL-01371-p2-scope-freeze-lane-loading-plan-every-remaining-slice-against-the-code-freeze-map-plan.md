---
id: PL-1371
family: plan
kind: map
title: P2 scope-freeze lane-loading plan — every remaining P2 slice by Work, lane and dependency order against the 4 Nov code freeze
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-10-03
owner: planner
tree: 49cd25be441382aebc1cc9c9ff325bd73fd81bc1
phase: P2
work: ~
supersedes: []
superseded_by: ~
corrected_by: []
relates: [CR-1212, RL-1263, PL-1237, PL-1267, PL-1268, PL-1276, PL-1277, PL-1254, PL-1286, PL-1364, PL-1368, FD-1209, FD-1244, FD-1245, FD-1356, FD-1357, FD-1358, FD-1366]
---

# PL-1371 — P2 scope-freeze lane-loading plan

> **This is a load plan, not an implementation plan.** It says what P2 has left to build, which
> gate slot carries each slice, in what order, and what that costs against the code freeze. It
> builds nothing and edits no other record. It was drafted as working id **9746**, reserved by the
> lead in `eta.md` ("9746 | PL (map) | planner-lanes"), and minted **PL-1371** on 2026-10-03 with the
> id the lead allocated (`python3 scripts/doc-id.py next` printed `1371`). It is `active`: every
> blocking decision point has its resolver (§9).
> **Executors bind nothing here:** each slice still runs from its own leaf plan, spawned from
> `.claude/roles/executor.md`. The lead dispatches from the priority list (§5) and the
> maintainer accepted §8 with four amendments on 2026-10-03 (§9).

## Goal

Re-baseline P2 at the scope freeze. Every remaining P2 slice gets an estimate, a lane
and a place in dependency order against the code freeze (Wed 2026-11-04), with three options and
their costs, the exit-demo split, the FD 9772 docs track, the WK-1178 serial queue, and the
planner's recommendation.

**Commission.** The maintainer's entry "2026-10-03 14:33:44 BST — RESUME (Sat 3 Oct): first GO to
the NEW lead (session 3018, opus/medium, verified from its cmdline plus settings); the rules
restated; today's ordered work", item 3, verbatim:

> **The scope-freeze re-baseline (task: today):** commission **ONE planner** (opus, medium) for
> the **lane-loading plan**: every remaining P2 slice by Work, with an estimate, lane and
> dependency order against the 4 Nov code freeze; options with costs ((i) scope to P3, (ii) a
> third lane, which is the user's call, (iii) re-homing); the Exit-demo split ((a) the real
> freMTPL2 algorithm after FD-1357's fix, (b) the script after WK-673/674); the FD 9772 docs
> track; and the WK-1178 serial queue. **Plus your recommendation.** It comes to me; I accept or
> amend; the user decides on the third lane.

**Spec.** No module spec is implemented here. The governing texts are `docs/roadmap.md` `## P2`
(exit criteria G1–G6 and "P2 freeze dates and target"), `RL-1263` (lanes),
`docs/process/delivery-process.md` §8, and the map plans named in §2.

## Acceptance Standard

Every command runs from a checkout of this branch, at the repository root.

1. **Every open P2 slice row is in the inventory.** This prints nothing:
   ```bash
   P=docs/plans/PL-01371-p2-scope-freeze-lane-loading-plan-every-remaining-slice-against-the-code-freeze-map-plan.md
   awk 'NR>=555 && NR<1406' docs/roadmap.md | python3 -c "
   import re,sys
   cur=None
   for l in sys.stdin:
       m=re.match(r'#### (SL-\d+)',l)
       if m: cur=m.group(1)
       s=re.match(r'status:\s*(draft|active)',l)
       if s and cur: print(cur); cur=None
   " | while read id; do grep -q "$id" "$P" || echo "MISSING $id"; done
   ```
   The line range is `## P2` → `## P3` at tree `49cd25be`; re-derive it with
   `grep -n '^## P[23]' docs/roadmap.md` on a later tree.
2. **Every open P2 Work has a §3 sub-table.** The eight are the `### WK-` sections of `## P2`
   whose `status:` is `active` at `49cd25be`. This prints `8`:
   `grep -E -c '^### 3\.[0-9]+ (WK-673|WK-674|WK-675|WK-690|WK-1169|WK-1170|WK-1178|WK-1250) ' "$P"`
3. **The load arithmetic reproduces.** Saving Appendix A's two blocks as `lanesim.py` and
   `run2.py` in one directory and running `python3 run2.py` prints `build slices 47 docs 2` on
   its first line and, on the `baseline R=2.0` line under `--- eff 1.00`, `ALL Sat 31 Oct`.
4. **Every option has a cost and the recommendation is one line.** `grep -c '^\*\*Cost' "$P"`
   prints `3`, and `grep -c '^\*\*Recommendation' "$P"` prints `1`.
5. **Docs checks.** `python3 scripts/audit-docs.py`, `python3 scripts/doc-index.py --check` and
   `python3 scripts/doc-id.py check` each exit 0.
6. **The inventory re-derives.** §8.1 item 3's command, run with tree `d8537220` in place of
   `origin/main`, prints `remaining 46 | §3 rows still open or uncut 46 | open P2 rows not in §3 0`
   on its last line: §3's 47 build rows less WK-675 S12, cut to P3 by DP-2 (a).

## Global Constraints

- **Lanes (`RL-1263`):** at most 2 build slices at once, from different Works; a measurement step
  runs alone with the other slot empty; two concurrent slices never edit the same existing
  function, class, spec section or policy table; preparation (plans, audits, rulings) holds no
  slot.
- **Sessions (the maintainer's entry "2026-10-01 11:36:55 BST — USAGE BUDGET RULES for the resume
  (the maintainer's 24h usage report); add them to the handover as rules 12–16"):** at most 3 live
  sessions besides the lead, "one executor per lane (≤2) plus ONE auditor-or-DM at a time";
  one audit per artifact and one scoped re-check at most; one DM session per Work per day.
  **A planner occupies that one preparation slot**, and when a lane is idle its slot may run a
  second preparation session, the total staying 3 (the maintainer, by delegation, answering the
  lead's amendment 4, entry "2026-10-03 14:56:08 BST — PL 9746 (#1076 @ee0ea8d2): ACCEPTED with your four amendments; DP-1 (a), DP-2 (a), DP-3 (a); amendment 4 answered; DP-4 to the user; no separate audit" in
  `~/gi-pricing-plan.local/channel/to-lead.md`).
- **Dates (`docs/roadmap.md` "P2 freeze dates and target"):** code freeze Wed 2026-11-04 (G1),
  docs freeze Thu 2026-11-05, exit demo Thu 2026-11-12. They are a forecast, not a target: "No
  Work, slice, plan, ruling or merge waits for a date." Scope freeze is today: "No new Work enters
  P2 after this date."
- **Holds** (`~/gi-pricing-plan.local/handover/holds-2026-10-01.md`): the FD-1366 per-route hold
  (a slice that calls one of the five untyped routes waits; a slice that edits one types it); the
  FD-1335 /score hold on WK-675 S6, S7 and S7b until `SL-1367` merges; the FD 9752 hold (no code
  reads the four approval responses until a DM rules the decision enum).

---

## 1. The finding that shapes the plan

**The lanes, not G2, are what is at risk.** The exit demo's chain (WK-674 S2 → WK-673's six build
slices → the script) finishes between 13 and 17 Oct in every scenario modelled (§6), three weeks
before the code freeze. What does not fit comfortably is **G1**: all seven open P2 Works
delivered. That is **47 build slices** (§3) on **2 gate slots**.

- **The planning baseline is five days in seven** (the rhythm the dates block says "slips about
  two weeks"): at the planning rate of 1 slice per lane per day, the 47 finish on **Tue 10 Nov**,
  6 days late. The 1–3 Oct pause was forced by the usage budget, which still binds, so this is
  the rhythm to plan on (the lead's amendment 1, adopted by the maintainer; §9).
- **The best case is every day** (the rhythm the P2 dates assume): the 47 finish on
  **Sat 31 Oct**, 4 days inside the freeze.

The rate is PL-1286's and the P2 sizing table's likely figure (§4). The observed rate in the
last burst was higher, but it ran under looser session rules than rules 12–16 now allow.

**WK-675 is not the bottleneck it looks like.** Its 15 slices are serial (one Work), but modelled
with its real dependencies, splitting it into two Works gains nothing (§6, row (iii)). The total
lane-days are the bottleneck. So what helps is fewer slices (option (i)), more slots
(option (ii)), or less preparation per slice (the re-homing this plan recommends under (iii)).

## 2. Inputs, verified at `49cd25be`

| Input | Read at | What it gave |
|---|---|---|
| `docs/roadmap.md` `## P2` (`:555`–`:1405`) | `49cd25be` | Works, SL rows and status (§3); G1–G6; the freeze dates; the Exit-demo row |
| `PL-1237` (WK-674 map, `active`) | `:691-711`, slice rows `:744-997` | S1 → S2 → S3 → S4 → S5 → S6, strictly in order; S5's measurements need a dedicated host |
| `PL-1267` (WK-673 map, `draft`; accepted by the maintainer 2026-09-30) | `:391-392`, `:433-604` | S1 → S2 → S7 → S3 → S4 → S5 → S6; S1 is spec-only; S5 needs `SL-1256` merged |
| `PL-1268` (WK-690 map, `active`) | `:385-550` | S3 needs S2 and the parity check; S4 needs S1; S5 needs S3 |
| `PL-1254` (WK-1250 map, `active`) | `:226-331` | S1 → S2 → S3; sizing 1.75 / 3.0 / 6.0 days |
| `PL-1286` (WK-675 map, `draft`) | `:240-246`, `:300-317`, `:336-345`, `:369` | 15 slices, 0.75 / 1 / 2 days each; DP-3 and DP-7 open, held to today |
| `PL-1276` (WK-1170 map, `draft`) | `:288-326` | six slices, S1 and S2 docs-only; lane cost 2.25 / 3.75 / 7.5 days |
| `PL-1277` (WK-1169 map, `draft`) | `:224-264` | four slices, only S3 holds a gate slot |
| Draft leaf plans PL 9762, PL 9764, PL 9776, PL 9789 | `origin/fd1356-fix-leaf-plan` `d4b69066`, `origin/plan-fd1357-pl9764` `0185d81d`, `origin/wk1178-f35-leaf-plan` `9a2ebc56`, `origin/wk690-s3-leaf-plan` `2323b544` | activation needs; PL 9762 needs "WK-674 S2 merged" |
| `RL-1263` | `:44-58`, `:117-189` | the two-lane rule; the 3-pair contention record (0 of 3 recorded, per `eta.md`) |
| Handover `lead-handover-2026-10-01-pause.md` | §"Saturday 3 Oct: scope-freeze agenda" | the WK-1178 serial queue; the agenda items |
| `holds-2026-10-01.md` | whole (47 lines) | the holds; "Saturday lane-loading plan — items to include" |
| `eta.md` | whole (127 lines) | the reservations; "Lane A's ~25 slices" (§3 re-derives it as 47 in all) |

**The predicate for "open slice":** a `#### SL-` heading inside `## P2` whose next `status:` line
reads `draft` or `active` (Acceptance 1 runs it). For slices with no row yet, the map plan's
slice table is the source, cited in §3.

## 3. Inventory: every remaining P2 slice, by Work

Estimates are lane-days at the likely rate, 1 day per build slice. Best is 0.75 and worst is
1.5–2 (§4). "Lane" is the primary slot; either slot takes the next ready slice when its own is
blocked (§5 rule 3). "Prep state" is what must exist before the slice can start.

### 3.1 WK-674 — Deployment (map `PL-1237`; 5 build slices left)

| Slice | Row | Est | Lane | Depends on | Prep state at `49cd25be` |
|---|---|---|---|---|---|
| S2 | `SL-1256` (`draft`) | 1 | A | `SL-1302` and `SL-1300` closed (both hold) | superseding PL 9765 (#1062 `44c43070`); needs #974 (RL 9986) minted in batch C, RL 9751 (#1068, **unaudited**) minted, the C18 scoped re-check |
| S3 | `SL-1257` (`draft`) | 1 | B | S2 | `PL-1342` |
| S4 | `SL-1258` (`draft`) | 1 | B | S3 | no leaf plan |
| S5 | `SL-1259` (`draft`) | 1 + solo window | B | S4, S2 | no leaf plan; **measurement: runs alone**; its dispatch carries NFR-490's post-F35 measurement, the multi-rung ladder bench and OQ 9777 |
| S6 | `SL-1260` (`draft`) | 1 | B | S5 | no leaf plan |

### 3.2 WK-673 — Dislocation (map `PL-1267`; 1 docs + 6 build slices; no SL rows cut)

| Slice | Est | Lane | Depends on | Prep state |
|---|---|---|---|---|
| S1 spec | 0.5, docs | — | `RL-1264`, `RL-1184` | `PL-1267` → `active` (DP-5 now has `RL-1361`); SL rows cut; S1 leaf |
| S2 run | 1 | A | S1 | leaf plan |
| S7 FR-231 weights | 1 | A | S2 | leaf plan; check `FD-1358` (FR-231 per-cell weight) against S7's scope at its leaf |
| S3 attribution | 1 | A | S7 (order) | leaf plan; never concurrent with a `compile_bundle` editor (WK-1250 S2/S3, WK-675 S3) |
| S4 Job and routes | 1 | A | S3 | leaf plan |
| S5 gate part 1 | 1 | A | S4; **`SL-1256` merged** | leaf plan; serialised with S2 and the FD-1356 fix on `approvals.py` |
| S6 floor wiring | 1 | A | S5 | leaf plan |

### 3.3 WK-675 — Frontend (map `PL-1286`; 15 slices, S1 included)

Dependencies are `PL-1286` `:302-317`'s "Depends on" column plus the holds.

| Slice | Row | Est | Lane | Depends on | Holds and prep |
|---|---|---|---|---|---|
| S1 | `SL-1369` (`draft`; activation #1069) | 1 | A | `RL-1307` | GO given; executor today |
| S2 | — | 1 | A | S1; DP-4, DP-5 | edits POST /rating-algorithms: types it in-slice (hold case ii); RL 9753, RL 9766 to mint |
| S3 | — | 1 | A | S2; DP-6 | RL 9767 to mint; carries FD 9759; never concurrent with a `compile.py` editor |
| S4 | — | 1 | A | DP-4 | new dependency `@tanstack/vue-table` |
| S13 | — | 1 | A | S4 (order) | — |
| S14 | — | 1 | A | S13 | — |
| S5 | — | 1 | A | S4; DP-3; WK-673 S7 | calls bulk-operation: waits until that route is typed (case i) |
| S6 | — | 1 | A | S1 | FD-1335 hold: after `SL-1367` |
| S7b | — | 1 | A | `RL-1261` | FD-1335 hold: after `SL-1367` |
| S7 | — | 1 | A | S6, S7b | FD-1335 hold |
| S10 | — | 1 | A | S6; DP-5; `SL-1256` | spec first: a new `03` FR and §5.1 row |
| S11 | — | 1 | A | S10 | — |
| S8 | — | 1 | A | S1; WK-673 S4 | — |
| S9 | — | 1 | A | S3; WK-1250 S3 | conditional cut, §8 C2 |
| S12 | — | 1 | — | `SL-1260` | **cut to P3** (DP-2 (a)), §8 C1 |

### 3.4 WK-690 — `expression` objectives (map `PL-1268`; 3 build slices left)

| Slice | Row | Est | Lane | Depends on | Prep state |
|---|---|---|---|---|---|
| S3 | `SL-1273` (`draft`) | 1 | A (first free day) | S2 (closed); the parity check `SL-1360` (merging today) | PL 9789 (#1037 `2323b544`) to mint and activate; carries FD 9780 |
| S4 | `SL-1274` (`draft`) | 1 | B | S1; never beside another WK-690 slice | leaf plan |
| S5 | `SL-1275` (`draft`) | 1 | B | S3 | leaf plan; conditional cut, §8 C2 |

### 3.5 WK-1250 — Sub-graphs (map `PL-1254`; 2 build slices left)

| Slice | Row | Est | Lane | Depends on | Prep state |
|---|---|---|---|---|---|
| S2 | `SL-1340` (`draft`) | 1 | B | S1 (closed); the FD-1246 trace ruling | leaf plan; `compile.py` contention with WK-673 S3 and WK-675 S3 |
| S3 | `SL-1341` (`draft`) | 1 | B | S2 | leaf plan |

### 3.6 WK-1170 — Create-read-retire audit (map `PL-1276`; 2 docs + 4 build slices)

| Slice | Est | Lane | Depends on | Prep state |
|---|---|---|---|---|
| S1 audit and register pass | docs | — | — | `PL-1276` → `active` (DP-4 has `RL-1318`); SL rows cut |
| S2 steps | docs | — | S1 | — |
| S3 audit-docs checks | 1 | B | S1 | leaf plan |
| S4 register tooling | 1 | B | S1's register pass | leaf plan |
| S5 migrate residue | 1 | B | S1's register pass | leaf plan |
| S6 gate coverage | 1 | B | S3, never alongside it | leaf plan |

### 3.7 WK-1169 — Charter investigation (map `PL-1277`; 3 docs + 1 build slice)

| Slice | Est | Lane | Depends on | Prep state |
|---|---|---|---|---|
| S1, S2, S4 | docs | — | WK-1170 S1; S4 never beside WK-1170 S2 | `PL-1277` → `active` (DP-2, DP-3 have `RL-1319`) |
| S3 checks | 1 | B | S2 | leaf plan |

### 3.8 WK-1178 — Standing maintenance: the serial queue (lane B)

The order is the maintainer's: "Lane B order: SL-1360 → FD-1357 fix (HIGH, blocks G2 A1–A2) →
FD-1356 fix (HIGH; gated on S2's merge) → RL-1343 decimal fix (guarded) → PL-1364 …" and "If
FD-1357's fix completes before S2 merges, the decimal fix runs in the gap" (entry "2026-10-01
10:10:32 BST — WK-674 S2 currency audit: ORDER AMENDED to (b) S2 → FD-1356 fix; a superseding PL
for S2; lane-B order SL-1360 → FD-1357 fix → FD-1356 fix; batch C re-cut"). This plan keeps that
order and appends the rest after "…".

| # | Item | Est | Depends on | Prep state |
|---|---|---|---|---|
| 0 | `SL-1360` permission parity | — | — | MERGE-ACK given 14:35:55 BST today |
| 1 | FD-1357 fix (multi-factor seeding; types seed-from-model) | 1 | — | PL 9764 + RL 9757 + SL 9763: scoped re-check of #1057, then mint |
| 2 | RL-1343 decimal-output fix (in the gap before S2 merges) | 1 | — | **no leaf plan yet**; must not share a file with S2 (re-check at dispatch) |
| 3 | FD-1356 fix (carries FD 9747 and FD 9748; states the demo DB end state) | 1 | WK-674 S2 merged | PL 9762 (#1063 `d4b69066`) + RL 9750 (#1070): final re-check, mint |
| 4 | `SL-1367` FD-1335 Part A (`PL-1364`) | 1 | never concurrent with S2 (score.py) | minted; activation |
| 5 | FD 9752 one ApprovalRequest shape | 1 | a DM rules the decision enum; after 3 (`approvals.py`) | FD filed (#1066); deadline before the exit demo |
| 6 | Exit demo (a): the real freMTPL2 algorithm | 1 | 1; Spike S1 of PL 9776 filed; FD 9773 minted | **unplanned**; WK-1178 by DP-1 (a) |
| 7 | Exit demo (b): the scripted `WF-699` journey | 1 | WK-673 S6, WK-674 S2, 3, 5, 6 | **unplanned**; WK-1178 by DP-1 (a) |
| 8 | F35 remedy (PL 9776) | 1 | 1; 4 | PL 9776 (#1051): align to RL 9771/9770, audit, mint |
| 9 | FD-1366 residue: the routes no handler-editing slice types (§8 (iii)) | 0–1 | — | leaf plan, sized at WK-1250 S2's leaf |
| 10 | FD 9772 check (audit-docs) | 1 | the docs track has marked every block (§7) | leaf plan |
| 11 | FD 9755 discharge (documented `migrate --verify` form plus the refusal) | 1 | — | leaf plan |
| — | NFR-526, NFR-527, NFR-536 measured on the exit tree | solo window | code freeze | at the exit tree, both slots empty |

Items 6 and 7 are WK-1178's: DP-1 was resolved (a) (§9). They keep their place first in §5.

## 4. Rates, and why these

- **Per slice:** PL-1286 sizes each WK-675 slice at 0.75 / 1 / 2 days (best / likely / worst,
  `PL-1286:336-345`). The P2 sizing table's rate is 0.5 / 0.75 / 1.5 (quoted at `PL-1276:309`).
  The accepted dates block cites "the measured 2 code slices per day", which is 1 per lane.
  **This plan uses 1 day per build slice per lane as likely**, the maintainer's figure for lane A.
- **Observed:** `git log 49cd25be --since=2026-09-28T00:00:00+01:00 --format='%s' | grep -E
  '^(feat|fix)\(' | grep -c -E 'SL-[0-9]+|Slice [0-9]'` prints `12`. It misses `SL-1300`
  (`2118679b`, "WK-1178 fix slice"), so 13 slices merged between `50e5271c` (28 Sep 15:01 BST)
  and `1dd5e264` (1 Oct 09:58 BST). Counting the pause to 3 Oct 14:36 BST, that is 2.6 per day.
  It ran with three gate slots until #925 and with 12 or more sessions, which rules 12–16 now
  forbid. It is an upper bound, not a forecast.
- **Preparation:** under rule 12, plan audits, slice audits and rulings share **one** session
  slot. 39 slices have no leaf plan (§3), so about 39 plan audits, 47 slice audits and about 10
  rulings, around 96 sessions in about 25 days, or 4 a day back to back. The model runs it at 2
  leaf plans ready per day (R=2) and at 1.5 (R=1.5). Below 1.5, preparation, not the lanes,
  sets the date, so R is measured at every Friday checkpoint (§8.1). Plans share that slot too:
  a planner occupies it, and an idle lane's slot may run a second preparation session (Global
  Constraints, Sessions). That raises the ceiling on R; it does not change the model's R=2.

## 5. Dependency order: the dispatch priority list

**Rules.** (1) G2's chain is dispatched first whenever a slice of it is ready: FD-1357 fix,
WK-674 S2, WK-673 S1–S6, the FD-1356 fix, FD 9752, and the two exit-demo slices. (2) Then the
longest remaining chain. (3) The lanes are slots, not owners: when lane A's next slice is blocked,
it takes lane B's next ready slice from a different Work, and the reverse. (4) Every pair is
checked for shared files before dispatch (`RL-1263` item 4), and these pairs are serialised
outright: WK-674 S2 / `SL-1367` (score.py); WK-674 S2 / FD-1356 fix / WK-673 S5 / FD 9752
(`approvals.py`); WK-673 S3 / WK-1250 S2 / WK-1250 S3 / WK-675 S3 (`compile.py`, `compile_bundle`);
FD-1357 fix / WK-674 S2 (`_CONTRACT_ARTIFACT_PATHS` and its test count: the second re-bumps).

**The load, by week of merge** (every-day rhythm, likely rate, R=2; Appendix A, `run2.py x`).
Lane A is the slot that carries WK-673 and then WK-675; lane B carries WK-1178 and then WK-674's
tail and the smaller Works. Either takes the other's next ready slice under rule 3.

| Week | Merges | Lane A (primary) | Lane B (primary) |
|---|---|---|---|
| Sat 3 – Fri 9 Oct | 9, plus `SL-1360` | WK-675 S1; WK-690 S3; WK-673 S2, S7, S3 | FD-1357 fix; WK-674 S2; FD-1356 fix; FD 9752 |
| Sat 10 – Fri 16 Oct | 13 | WK-673 S4, S5, S6; WK-675 S2, S4, S3, S13, S14 | exit demo (a), (b); WK-674 S3; RL-1343 fix; `SL-1367` |
| Sat 17 – Fri 23 Oct | 13 | WK-675 S6, S7b, S10, S5, S7, S11, S8 | F35; FD-1366 residue; FD 9755; WK-674 S4; WK-1170 S3, S4 |
| Sat 24 – Fri 30 Oct | 11 | WK-675 S9; WK-690 S4, S5 | WK-1170 S5, S6; WK-1250 S2, S3; WK-1169 S3; FD 9772 check; WK-674 S5 (solo window), S6 |
| Sat 31 Oct – Wed 4 Nov | 1 | WK-675 S12 (or cut, §8 C1); then slack | slack; NFR-526/527/536 on the exit tree |

The RL-1343 fix takes the gap before WK-674 S2 merges, as the maintainer ordered, **only if its
leaf plan is ready by then** (it has none today); otherwise it follows FD 9752, as the model
places it. The week cells are a view of Appendix A's day table, which the lead re-runs at each
re-baseline (§8). The model ignores file contention beyond rule 4's pairs, which costs some
packing. Read the table as an order, not as dates.

**Preparation order (the one auditor-or-DM slot, in this order):** (1) this plan's acceptance (done 2026-10-03, §9);
(2) mint batch B (FD 9775, OQ 9774, FD 9773); (3) the FD-1357 batch (#1057 scoped re-check; RL 9757
+ PL 9764 + SL 9763); (4) PL 9789 mint and activation (WK-690 S3); (5) RL 9751 audit (#1068) and
the maintainer's four DM questions, batch C (#974 + FD 9772), then the PL 9765 re-check and mint
(WK-674 S2); (6) `PL-1267` activation, WK-673's SL rows, its S1 and S2 leaves; (7) PL 9762 + RL
9750 final re-check and mint (FD-1356 fix); (8) one WK-675 DM session: DP-3 (OQ-1223) plus the
pending RL 9753, RL 9766, RL 9767 texts; (9) one DM session for FD 9752's enum and FD-1244 and
FD-1245; (10) the RL-1343 leaf plan; (11) the exit-demo leaves, under WK-1178 (DP-1 (a)); then leaves in
§5's order, about two days ahead of their slot.

## 6. What the model says

`python3 run2.py` (Appendix A) at `49cd25be`'s inventory. "ALL" is the day the last slice merges.

| Scenario | Every day: ALL | 5 days in 7: ALL | Exit demo (b) done |
|---|---|---|---|
| Baseline, R=2 | Sat 31 Oct | Tue 10 Nov | Tue 13 Oct / Sat 17 Oct |
| Baseline, R=1.5 | Mon 02 Nov | Tue 10 Nov | Wed 14 Oct / Sat 17 Oct |
| (i) S12 to P3 | Wed 28 Oct | Mon 09 Nov | as baseline |
| (i) S12, S13, S14 to P3 | Wed 28 Oct | Sat 07 Nov | as baseline |
| (i) S12–S14, S9, WK-690 S5 to P3 | Tue 27 Oct | Fri 06 Nov | as baseline |
| (ii) a third lane, R=2 | Wed 28 Oct | Wed 04 Nov | as baseline |
| (ii) a third lane, R=1.5 | Mon 02 Nov | Sun 08 Nov | as baseline |
| (iii) WK-675's views as a second Work | Thu 29 Oct | Tue 10 Nov | as baseline |

Read across: **on the five-days-in-seven baseline, two lanes do not fit**; **on the every-day
best case they fit** with 2 to 4 days of slack, and cutting S12 alone buys 3 more. **That slack
is an upper bound:** the model has no rework, no contention below rule 4's pairs and no new
slices from FD 9772's code-side errors (Appendix A, "What the model is not"; the lead's
amendment 3). On five days in seven, only a third lane with fast preparation fits by
4 Nov. Cutting 5 slices gets to 2 days late, and those 2 days come out of the docs freeze and the
exit-demo week, which have 8 days between them. On the every-day rhythm, the last slices after
the cuts are WK-675 S9 and the FD 9772 check, which waits for the docs track.

## 7. The exit-demo split and the FD 9772 track

**Exit demo (a): the real freMTPL2 rating algorithm in the seed.** Depends on the FD-1357 fix only.
It needs neither WK-673 nor WK-674, so it takes the first free slot after item 1. Acceptance, as
the maintainer set it in `holds-2026-10-01.md` ("Saturday lane-loading plan — items to include"):
PL 9776's Spike S1 harness re-run on the new algorithm, and "every step's reads ⊆ its declared
consumes", shown by running FD 9773's P5 sweep script on it (0 undeclared reads). Its dispatch
record also states "declares no decimal output" until the RL-1343 fix merges (the maintainer's
guard). It discharges FD-1209's algorithm half.

**Exit demo (b): the scripted `WF-699` journey**, A to E plus deploy, with A1–A2 on the 7-factor
GLM, and the journey test citing `WF-699` by id. **Its real dependencies, re-derived as `RL-1263`
item 5 requires:** WK-673 S6 (the run with attribution, and FR-364's floor at approval); WK-674
S2 only, because "deployment to `uat` and then `prod` (FR-429)" is FR-267, FR-428 and FR-429, all
in `SL-1256` (`03:195`, `07:139-140`); WK-674 S3–S6 (isolation, deployment path, switchover,
routing) are **bare sequencing**, and this plan lifts them. Also: the FD-1356 fix (the demo DB's
end state, the maintainer's entry "2026-10-01 11:13:17 BST"), FD 9752 (the script reads approval
responses), and the FD-1244 and FD-1245 rulings (the §10 gate "Before the P2 exit demo").
FD-1356's Task 0 query is re-run before the demo. If (b)'s leaf plan finds a call to an S4–S6
route, it adds that slice as a dependency (DP-6).

**FD 9772: two tracks.** (a) **Docs track, preparation, no slot:** the 10 structural failures,
each adjudicated by a DM for which side was wrong (`CLAUDE.md` §0), code-side errors filed as their
own FDs, `03:233` through FD 9773's ruling. Then each block marked as a class example or an
"illustrative fragment", with the rule written into the docs-process text first. A spec PR waits
for the merge of any build slice that changes the same spec section. (b) **The check, a code slice,
WK-1178 item 10:** marked blocks `model_validate`d in full, proven on broken input, the gate failing
on unmarked json. **The planner's choice, stated: the check merges after (a) has marked every
block, in gate mode from its first merge.** Not report-only first: a report-only mode is a check
that has never failed, and leaving it to flip later is the step that gets dropped. Cost: (a) must
finish by about 26 Oct to leave the check its slot before 4 Nov. **Risk:** each code-side error (a)
finds is a new FD and possibly a new slice; the plan has no allowance for them beyond the slack.

## 8. Options, costs and the recommendation

**(i) Scope to P3.** Candidates in order of least cost to cut:
- **C1, now: WK-675 S12, the Deployments view.** It is structurally last: it needs `SL-1260`,
  WK-674's last slice. DP-7 (OQ-1285) recommends folding it into `07`'s `/admin/environments`, a
  platform admin view. No G2 step reads it.
- **C2, conditional, in this order: WK-675 S13 and S14** (the Jobs views, `07`'s, added by
  FD-1284 option D); **WK-675 S9** (sub-graph mounting, after WK-1250 S3); **WK-690 S5** (the
  authoring view and `WF-702` Route B).

**Cost (i):** each cut is a dated maintainer line on the Work's row, and the cut scope is
"deferred with an owner" (the maintainer; event: the P2 phase closure record, for P3's first
plan), as `RL-1265` did for WK-690. Cutting S12 moves DP-7/OQ-1285 to P3 with it. Cutting S13 and
S14 reverses FD-1284's option D for P2, and `reachability.test.ts`'s exception stays. A cut slice
is a P2 promise that P3 inherits.

**(ii) A third lane.**

**Cost (ii):** a dated amendment of `RL-1263` and of
`delivery-process.md` §8, the user's call. `RL-1263`'s contention record stands at 0 of 3 pairs, so
two lanes are not yet shown contention-free. The VM was resized from e2-16 to e2-8 on 29 Sep and
#925 cut the gate slots from 3 to 2 for the 8-vCPU box, so a third slot probably needs the larger
VM back. Rule 12 caps live sessions at 3 besides the lead, so a third executor means amending rule
12, or the auditor-or-DM slot (already the scarcer one, §4) stalls. Gain: 3 days on the
every-day rhythm; 6 days on five in seven, but only if preparation keeps R=2 (2 days at R=1.5).

**(iii) Re-homing.** Not splitting WK-675 (§6: no gain). Instead, cut preparation by folding small
items into slices that already touch the same code, so each needs no plan or audit of its own:
- FD-1366 route typing goes into the slice that edits each handler (hold case ii): POST
  /rating-algorithms in WK-675 S2; seed-from-model in the FD-1357 fix (already so); the two
  sub-graph routes in WK-1250 S2 if its leaf edits them. Only the rest is WK-1178 item 9.
- FD 9759 stays in WK-675 S3; FD 9747 and FD 9748 stay in the FD-1356 fix (both already so).
- The exit-demo slices go to WK-1178 (DP-1 (a)), whose scope is "work that belongs to no other
  Work", rather than a new Work, which the scope freeze bars after today.

**Cost (iii):** each fold grows the receiving slice by a task and its write set; each is stated in
that slice's leaf plan and dispatch record. About 3 to 5 fewer prep cycles; no lane-day change.

**Recommendation: (iii) now, (i) C1 now, (i) C2 as a pre-agreed trigger, and (ii) held in reserve
for the user if C2 is exhausted and the trigger still fires.** The trigger: at each Friday
checkpoint from Fri 9 Oct, and at the re-baseline the dates block names (after WK-674 S2 merges),
the lead computes `today + remaining build slices ÷ (slices merged since 3 Oct ÷ days elapsed)`.
If that is later than Wed 4 Nov, the next C2 cut goes to the maintainer that day. If all four are
cut and it is still later, (ii) goes to the user. This keeps every cut reversible until the data
says it is needed.

**Accepted 2026-10-03** by the maintainer, by delegation, with the lead's four amendments
(§9 DP-1 to DP-3), and DP-4 ruled by the user (§9). On the baseline (§1) the trigger is expected
to fire at the first checkpoint, Fri 9 Oct. **When it fires, the lead brings the maintainer the
specific cut that day; a cut is never applied automatically** (DP-3).

### 8.1 The Friday checkpoint

Each Friday from Fri 9 Oct, and at WK-674 S2's merge, the lead records these in `eta.md`, each
with the tree it was read at:

1. **The trigger** (§8): `today + remaining ÷ (slices merged since 3 Oct ÷ days elapsed)`, with
   "remaining" from item 3. Later than Wed 4 Nov → the next C2 cut to the maintainer that day.
2. **R, leaf plans activated per day since 3 Oct** (the lead's amendment 2). Predicate: plan
   files under `docs/plans/` whose header reads `kind: leaf` and `status: active`, counted at the
   checkpoint tree minus at `49cd25be` (where it prints `129`), divided by days elapsed. A leaf
   plan superseded or retired inside the window drops out, so R reads low by that many. **R < 1.5
   is escalated to the maintainer the same day, separately from the trigger**: below it,
   preparation sets the date (§4). Saved as `r.py` and run as `python3 r.py 49cd25be origin/main`:
   ```python
   import re, subprocess, sys
   g = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
   for T in sys.argv[1:]:
       n = 0
       for f in g("ls-tree", "-r", "--name-only", T, "docs/plans").split():
           h = g("show", f"{T}:{f}").split("\n---", 1)[0]
           n += bool(re.search(r"^kind: leaf", h, re.M) and re.search(r"^status: active", h, re.M))
       print(T, "active leaf plans", n)
   ```
3. **The inventory, re-derived** (the maintainer's acceptance: "the Friday checkpoint re-derives
   it with a stated command, and a different count is reported"). The 47 of §3 is the planner's
   count at `49cd25be`. The command reads §3's build rows (an `Est` cell that starts with a digit
   or `0–1` and does not say `docs`) and the `SL-` rows of `docs/roadmap.md` `## P2` at tree `T`.
   A §3 row marked **cut to P3** never counts (S12 now; a later C2 cut is marked the same way
   in the same commit as its maintainer line). Any other §3 row counts as remaining when its `SL-` row (matched by id, or by Work and `Slice N`) is
   `draft` or `active`, or when it has no row yet (`uncut`). An open `## P2` row that matches no
   §3 row is printed `NEW` and counted. Two cases are struck by hand from the listing: a `NEW`
   WK-1178 row, matched to its §3.8 item (WK-1178 rows carry no slice number, so both would
   count), and an `uncut` item that merged without an `SL-` row. **The result is the "remaining"
   of item 1; a count other than 46 (47 less S12) less what merged is reported to the maintainer with its
   listing.** Saved as `inv.py` and run as `python3 inv.py "$P" origin/main`, with `P` as in
   Acceptance 1:
   ```python
   import re, subprocess, sys
   P, T = sys.argv[1], sys.argv[2]
   rm = subprocess.run(["git", "show", f"{T}:docs/roadmap.md"], capture_output=True, text=True, check=True).stdout.splitlines()
   lo = next(i for i, l in enumerate(rm) if l.startswith("## P2"))
   hi = next(i for i, l in enumerate(rm) if l.startswith("## P3"))
   rows, w, cur = {}, None, None
   for l in rm[lo:hi]:
       if m := re.match(r"### (WK-\d+)", l): w = m.group(1)
       if m := re.match(r"#### (SL-\d+)(?:.*?Slice (\d+[a-z]?)\b)?", l): cur = m.group(1); rows[cur] = [w, m.group(2) and "S" + m.group(2), None]
       if (s := re.match(r"status:\s*(\w+)", l)) and cur: rows[cur][2] = s.group(1); cur = None
   opn = lambda i: rows[i][2] in ("draft", "active")
   plan = open(P).read().split("\n## 3. ")[1].split("\n## 4. ")[0].splitlines()
   left, seen, w = [], set(), None
   for l in plan:
       if m := re.match(r"### 3\.\d+ (WK-\d+)", l): w = m.group(1); continue
       if not l.startswith("|") or set(l.strip()) <= set("|-"): continue
       c = [x.strip() for x in l.strip().strip("|").split("|")]
       if "Est" in c: est, idc = c.index("Est"), next(c.index(h) for h in ("Row", "Item", "Slice") if h in c); continue
       sl = re.search(r"SL-\d+", c[idc])
       key = (re.match(r"(S\d+[a-z]?)", c[0]) or [None])[0]
       hit = sl.group(0) if sl else next((i for i, r in rows.items() if r[0] == w and key and r[1] == key), None)
       if hit: seen.add(hit)
       if "cut to P3" in l: continue
       if not re.match(r"(\d|0–1)", c[est]) or "docs" in c[est]: continue
       if hit is None or opn(hit): left.append((w, c[0][:28], hit or "uncut"))
   new = [(r[0], i, "NEW") for i, r in rows.items() if opn(i) and i not in seen]
   for x in left + new: print(*x, sep="  ")
   print("remaining", len(left) + len(new), "| §3 rows still open or uncut", len(left), "| open P2 rows not in §3", len(new))
   ```
   At `49cd25be` and at `d8537220` it prints `remaining 46 | §3 rows still open or uncut 46 | open
   P2 rows not in §3 0`: the 12 open `SL-` rows (5 of WK-674, 3 of WK-690, 2 of WK-1250,
   `SL-1369` and `SL-1367`) plus 34 uncut. With the `cut to P3` line removed it prints 47, the
   planner's count, re-derived. It fails on broken input: with §3's `SL-1369` cell changed to
   `SL-1360` (closed at `d8537220`), it prints `remaining 46 | §3 rows still open or uncut 45 |
   open P2 rows not in §3 1`, dropping the closed row and listing `SL-1369` as `NEW`.
4. **The third lane is revisited at the Fri 9 Oct checkpoint** (the user's ruling, §9 DP-4).

## 9. Decision points

Every row is resolved or names its step, so the plan is `active` (`document-ids.md` §1.7, "Freeze
is mechanical"). The resolutions cite three dated entries in `~/gi-pricing-plan.local/channel/`:
the lead's verdict in `from-lead-2026-10-03.md`, entry "2026-10-03 14:55:17 BST — LEAD VERDICT on PL 9746 (#1076 @ee0ea8d2): ADOPT with four amendments; DP-1..3 to the maintainer, DP-4 to the user"; the
maintainer's acceptance, by delegation, in `to-lead.md`, entry "2026-10-03 14:56:08 BST — PL 9746 (#1076 @ee0ea8d2): ACCEPTED with your four amendments; DP-1 (a), DP-2 (a), DP-3 (a); amendment 4 answered; DP-4 to the user; no separate audit"; and the user's
ruling in `to-lead.md`, entry "2026-10-03 14:57:13 BST — DP-4 (the third lane): THE USER ruled "Not now"". The lead's four amendments
are applied at §1 (1), §8.1 item 2 (2), §6 (3) and Global Constraints, Sessions (4).

| # | Question | Options | Recommendation | Kind | Blocking? | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | Which Work carries the two exit-demo slices? | (a) WK-1178; (b) a new Work, opened today, before the scope freeze closes; (c) WK-673 or WK-674 | (a): its scope sentence fits, G1 exempts it, and no new Work enters | scope | yes, for the exit-demo SL rows | **Resolved (a)** by the maintainer, by delegation, entry "2026-10-03 14:56:08 BST — PL 9746 (#1076 @ee0ea8d2): ACCEPTED with your four amendments; DP-1 (a), DP-2 (a), DP-3 (a); amendment 4 answered; DP-4 to the user; no separate audit": the two slices go to WK-1178 and stay first in lane B's priority under §5 rule 1 |
| DP-2 | WK-675 S12 to P3 now? | (a) yes, with DP-7/OQ-1285; (b) keep it in P2 | (a) | scope | yes, for WK-675's DP-7 ruling | **Resolved (a)** by the maintainer, by delegation, entry "2026-10-03 14:56:08 BST — PL 9746 (#1076 @ee0ea8d2): ACCEPTED with your four amendments; DP-1 (a), DP-2 (a), DP-3 (a); amendment 4 answered; DP-4 to the user; no separate audit": S12 to P3 now, with DP-7/OQ-1285, deferred with an owner (the maintainer; event: the P2 phase closure record, for P3's first plan). The lead applies it as a dated line on WK-675's roadmap row (Task 2) |
| DP-3 | The C2 conditional cuts and their trigger, as §8 states them | (a) accept; (b) amend the order or the trigger; (c) cut now | (a) | scope | no: default (a) applied from Fri 9 Oct | **Resolved (a)** by the maintainer, by delegation, entry "2026-10-03 14:56:08 BST — PL 9746 (#1076 @ee0ea8d2): ACCEPTED with your four amendments; DP-1 (a), DP-2 (a), DP-3 (a); amendment 4 answered; DP-4 to the user; no separate audit": the order and the trigger as amended (§8, §8.1). When it fires, the lead brings the maintainer the specific cut that day; it is not applied automatically |
| DP-4 | A third lane | (a) not now, held for the trigger; (b) now | (a) | scope | no: default (a) | **Resolved (a), not now,** by the user, entry "2026-10-03 14:57:13 BST — DP-4 (the third lane): THE USER ruled "Not now"": two lanes; WK-675 S12 cut now; further cuts on the Fri 9 Oct trigger; a code-freeze slip of a few days accepted as possible; the third lane revisited at the Fri 9 Oct checkpoint (§8.1 item 4) |
| DP-5 | WK-675 DP-3 (OQ-1223) and DP-7 (OQ-1285), held to today | DP-3: rule it now, since S5 stays in P2. DP-7: moves to P3 if DP-2 (a); else rule it now | as stated | decision point | no: resolved before S5's and S12's leaves go `active` | decision-maker, in preparation item 8: DP-3 (OQ-1223) in the next WK-675 DM batch (adopted in entry "2026-10-03 14:55:17 BST — LEAD VERDICT on PL 9746 (#1076 @ee0ea8d2): ADOPT with four amendments; DP-1..3 to the maintainer, DP-4 to the user"); DP-7 moves to P3 with S12 (DP-2 (a)) |
| DP-6 | Does exit demo (b)'s script call any WK-674 S3–S6 route? | — | expected no (§7) | fact | no: checked in (b)'s leaf plan; until then (b) depends on S2 only | planner, at (b)'s leaf |
| DP-7 | FD 9759's re-homing if WK-675 S3 is cut | — | moot: S3 is not a cut candidate | scope | no | — |

## Tasks

A load plan's tasks are the steps that put it into use. None is an executor's.

- [x] **Task 1 (the maintainer; the user for DP-4):** accept or amend §8 and rule DP-1 to DP-4, each
  by a dated line. Done 2026-10-03: §9 cites each entry.
- [ ] **Task 2 (the lead):** apply each accepted cut as the maintainer's dated line on the Work's
  roadmap row, and route DP-5 to the WK-675 DM session (preparation item 8).
- [ ] **Task 3 (the planner, on the lead's order):** cut the exit-demo SL rows under DP-1's Work,
  `draft`, in `docs/roadmap.md`, and write their leaf plans in §5's preparation order.
- [ ] **Task 4 (the lead, each Friday from Fri 9 Oct, and at WK-674 S2's merge):** run §8.1:
  the trigger, R and the re-derived inventory, recorded in `eta.md`; bring the next C2 cut to
  the maintainer when the trigger fires, escalate R < 1.5 the same day, and revisit the third
  lane on Fri 9 Oct. Re-run Appendix A with the merged slices removed when the inventory changes.

## 10. Self-review

- Every open P2 SL row and every slice in the seven map plans' tables is in §3 (Acceptance 1, 2).
  The `eta.md` figure "Lane A's ~25 slices" counted lane A only. §3 counts 47 build slices across
  both lanes, including WK-674's five (`eta.md` read four) and WK-1178's 11 (the two exit-demo
  slices among them, by DP-1 (a)). WK-675 S12 stays listed, marked **cut to P3** (DP-2 (a)).
- No date here waits for a date: the trigger reads throughput, not the calendar.
- This plan's own id was minted from working id 9746 as `PL-1371`; no other id is minted or
  renumbered. Working ids are written with a space (`PL 9765`) and only minted
  ids go in `relates:`.
- What this plan does not do: cut SL rows (for WK-673, WK-675 S2–S14, WK-1169, WK-1170 and the
  exit demo, they are cut when their map plans activate or on the lead's order under DP-1 (a)), rule any decision point,
  or edit `docs/roadmap.md`.

## Appendix A — the load model (verbatim)

`lanesim.py`:

```python
"""Lane-loading simulation for PL-1371 (drafted as working id 9746). Day 0 = Sat 2026-10-03.

Slice tuple: (id, work, deps, ready_day, duration_days, kind)
  ready_day: day its leaf plan is minted+active; None = needs a leaf plan from the prep queue.
  kind: B build (one gate slot), D docs (no slot), M measurement (runs alone, RL-1263 item 3).
Rules modelled: <= `lanes` build slices at once; never two from one Work (RL-1263 item 2);
an M slice runs with the other slot empty; a slice starts only when deps are done and it is ready.
eff scales every duration (1.0 = work every day, as the P2 dates assume; 5/7 = five days in seven).
"""
import datetime as dt

S = [
    ("675-S1", "WK-675", [], 0, 1, "B"),
    ("1178-FD1357", "WK-1178", [], 2, 1, "B"),
    ("674-S2", "WK-674", [], 3, 1, "B"),
    ("690-S3", "WK-690", [], 2, 1, "B"),
    ("1178-FD1356", "WK-1178", ["674-S2", "1178-FD1357"], 3, 1, "B"),
    ("1178-SL1367", "WK-1178", ["674-S2", "1178-FD1356", "1178-RL1343"], 2, 1, "B"),
    ("1178-RL1343", "WK-1178", ["1178-FD1357"], None, 1, "B"),
    ("1178-F35", "WK-1178", ["1178-FD1357", "1178-SL1367"], 4, 1, "B"),
    ("1178-FD9752", "WK-1178", ["1178-FD1356"], None, 1, "B"),
    ("1178-FD9772chk", "WK-1178", [], 23, 1, "B"),  # waits for the docs track (section 7)
    ("1178-FD9755", "WK-1178", [], None, 1, "B"),
    ("1178-FD9779B", "WK-1178", [], None, 1, "B"),
    ("DEMO-a", "WK-1178", ["1178-FD1357"], None, 1, "B"),
    ("673-S1", "WK-673", [], None, 0.5, "D"),
    ("673-S2", "WK-673", ["673-S1"], None, 1, "B"),
    ("673-S7", "WK-673", ["673-S2"], None, 1, "B"),
    ("673-S3", "WK-673", ["673-S7"], None, 1, "B"),
    ("673-S4", "WK-673", ["673-S3"], None, 1, "B"),
    ("673-S5", "WK-673", ["673-S4", "674-S2"], None, 1, "B"),
    ("673-S6", "WK-673", ["673-S5"], None, 1, "B"),
    ("674-S3", "WK-674", ["674-S2"], 1, 1, "B"),
    ("674-S4", "WK-674", ["674-S3"], None, 1, "B"),
    ("674-S5", "WK-674", ["674-S4"], None, 1, "M"),
    ("674-S6", "WK-674", ["674-S5"], None, 1, "B"),
    ("690-S4", "WK-690", ["690-S3"], None, 1, "B"),
    ("690-S5", "WK-690", ["690-S4"], None, 1, "B"),
    ("1250-S2", "WK-1250", [], None, 1, "B"),
    ("1250-S3", "WK-1250", ["1250-S2"], None, 1, "B"),
    ("1170-S1", "WK-1170", [], None, 0.5, "D"),
    ("1170-S3", "WK-1170", ["1170-S1"], None, 1, "B"),
    ("1170-S4", "WK-1170", ["1170-S3"], None, 1, "B"),
    ("1170-S5", "WK-1170", ["1170-S4"], None, 1, "B"),
    ("1170-S6", "WK-1170", ["1170-S5"], None, 1, "B"),
    ("1169-S3", "WK-1169", ["1170-S1"], None, 1, "B"),
    # WK-675: PL-1286 :302-317 "Depends on" column, plus the holds register
    ("675-S2", "WK-675", ["675-S1"], None, 1, "B"),
    ("675-S3", "WK-675", ["675-S2"], None, 1, "B"),
    ("675-S4", "WK-675", ["675-S1"], None, 1, "B"),
    ("675-S13", "WK-675", ["675-S4"], None, 1, "B"),
    ("675-S14", "WK-675", ["675-S13"], None, 1, "B"),
    ("675-S5", "WK-675", ["675-S4", "673-S7", "1178-FD9779B"], None, 1, "B"),
    ("675-S6", "WK-675", ["675-S1", "1178-SL1367"], None, 1, "B"),
    ("675-S7b", "WK-675", ["1178-SL1367"], None, 1, "B"),
    ("675-S7", "WK-675", ["675-S6", "675-S7b"], None, 1, "B"),
    ("675-S10", "WK-675", ["675-S6", "674-S2"], None, 1, "B"),
    ("675-S11", "WK-675", ["675-S10"], None, 1, "B"),
    ("675-S8", "WK-675", ["675-S1", "673-S4"], None, 1, "B"),
    ("675-S9", "WK-675", ["675-S3", "1250-S3"], None, 1, "B"),
    ("675-S12", "WK-675", ["674-S6"], None, 1, "B"),
    ("DEMO-b", "WK-1178", ["673-S6", "674-S2", "DEMO-a", "1178-FD1356", "1178-FD9752"], None, 1, "B"),
]
BASE = dt.date(2026, 10, 3)


def prio(slices):
    ids = [s[0] for s in slices]
    succ = {k: [] for k in ids}
    for s in slices:
        for x in s[2]:
            if x in succ:
                succ[x].append(s[0])
    memo = {}

    def L(k):
        if k not in memo:
            memo[k] = 1 + max((L(y) for y in succ[k]), default=0)
        return memo[k]
    wl = {}
    for s in slices:
        wl[s[1]] = wl.get(s[1], 0) + 1
    work = {s[0]: s[1] for s in slices}
    boost = {k: 100 for k in G2}
    return sorted(ids, key=lambda k: (-(boost.get(k, 0) + L(k) + wl[work[k]]), ids.index(k)))


# G2's critical path is dispatched first whenever it is ready (the plan's sequencing rule 1)
G2 = ["1178-FD1357", "674-S2", "DEMO-a", "673-S1", "673-S2", "673-S7", "673-S3", "673-S4",
      "673-S5", "673-S6", "DEMO-b", "1178-FD1356", "1178-FD9752"]


def run(R=2.0, eff=1.0, drop=(), lanes=2, retag=None):
    sl = [s for s in S if s[0] not in drop]
    if retag:
        sl = [(s[0], retag.get(s[0], s[1]), s[2], s[3], s[4], s[5]) for s in sl]
    d = {s[0]: s for s in sl}
    order = prio(sl)
    ready = {k: v[3] for k, v in d.items()}
    t = 1.0
    for k in order:  # the prep queue hands out leaf plans in critical-path order
        if ready[k] is None:
            ready[k] = t + 1
            t += 1.0 / R
    done, running, start, day = {}, {}, {}, 0.0
    while len(done) < len(d) and day < 300:
        for k in list(running):
            if running[k] <= day + 1e-9:
                done[k] = running.pop(k)
        for k in order:
            if k in done or k in running:
                continue
            if ready[k] > day or not all(x in done for x in d[k][2] if x in d):
                continue
            if d[k][5] == "D":
                running[k] = day + d[k][4] / eff
                start[k] = day
                continue
            busy = [x for x in running if d[x][5] != "D"]
            if any(d[x][1] == d[k][1] for x in busy):
                continue
            if d[k][5] == "M":
                if busy:
                    continue
            elif any(d[x][5] == "M" for x in busy) or len(busy) >= lanes:
                continue
            running[k] = day + d[k][4] / eff
            start[k] = day
        day += 0.25
    return done, start, d


def date(x):
    return (BASE + dt.timedelta(days=int(-(-x // 1)))).strftime("%a %d %b")


def summary(label, **kw):
    done, _, _ = run(**kw)
    last = max(done, key=done.get)
    keys = ["674-S2", "673-S6", "674-S6", "DEMO-a", "DEMO-b", "675-S12"]
    print(f"{label:30} ALL {date(done[last])} (last {last}) | "
          + "; ".join(f"{k} {date(done[k]) if k in done else '-'}" for k in keys))


def lanes_table(**kw):
    done, start, d = run(**kw)
    for k in sorted(start, key=start.get):
        if d[k][5] != "D":
            print(f"{k:16} {d[k][1]:8} start {date(start[k])}  done {date(done[k])}")
```

`run2.py` (in the same directory; `python3 run2.py x` also prints the day table):

```python
import sys
sys.path.insert(0, ".")
import lanesim as m

nb = sum(1 for s in m.S if s[5] != "D")
print("build slices", nb, "docs", sum(1 for s in m.S if s[5] == "D"))
cutA = ("675-S12",)
cutB = ("675-S12", "675-S13", "675-S14")
cutC = cutB + ("675-S9", "690-S5")
views = {k: "WK-675v" for k in ("675-S13", "675-S14", "675-S10", "675-S11", "675-S12", "675-S8")}
for eff in (1.0, 5 / 7):
    print(f"--- eff {eff:.2f}")
    for R in (2.0, 1.5):
        m.summary(f"baseline R={R}", R=R, eff=eff)
    m.summary("(i) cut S12", eff=eff, drop=cutA)
    m.summary("(i) cut S12-S14", eff=eff, drop=cutB)
    m.summary("(i) cut S12-14,S9,690-S5", eff=eff, drop=cutC)
    m.summary("(ii) 3 lanes", eff=eff, lanes=3)
    m.summary("(ii) 3 lanes, prep R=1.5", eff=eff, lanes=3, R=1.5)
    m.summary("(iii) 675 views as 2nd Work", eff=eff, retag=views)
    m.summary("(iii)+(i) cut S12", eff=eff, retag=views, drop=cutA)
if len(sys.argv) > 1:
    print("=== lane table, baseline eff 1.0")
    m.lanes_table(eff=1.0)
```

**What the model is not.** Day 0's ready days for planned slices are the planner's reading of each
prep state in §3 (e.g. WK-674 S2 = day 3, after batch C and RL 9751), not measured. It has no
contention below rule 4's pairs, no rework, and no new slices from FD 9772's code-side errors. Its
dates are for comparing options against each other. The re-baseline trigger (§8) uses measured
throughput instead.
