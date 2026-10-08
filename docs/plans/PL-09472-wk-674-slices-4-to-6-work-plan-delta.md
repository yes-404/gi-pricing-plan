---
id: PL-9472
family: plan
kind: map
title: WK-674 — Slices 4 to 6 (deployment path, switchover and measurements, routing and shadow) as rows, after the 2026-10-08 re-plan: Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-08
owner: planner
tree: 60e9254c22972c03fb11f10fcce8dae4f1c00dd9
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1371, PL-1392, PL-1454, RL-1232, RL-1263, RL-1311, RL-1365, OQ-1453, FD-1211, FD-1246, FD-1411, CR-1247, LG-1363, LG-1405, SL-1258, SL-1259, SL-1260]
---

# PL 9472 (working id) — WK-674 Slices 4 to 6 as rows: Work-plan delta

> **For agentic workers:** this is a **Work-plan delta** under Lean P2 L5. It does not replace
> [`PL-1237`](PL-01237-wk-674-deployment-environments-switchover-tenancy-map-plan.md) (WK-674's
> map plan, `active`, frozen at 2026-09-29); it `relates:` it and states, in one place, every
> change to Slices 4, 5 and 6 since that date. **Read `PL-1237` Tasks 4–6, its Acceptance
> Standard and Global Constraints first, then this file**; where they differ, this file is the
> later statement. No per-slice leaf plan is written for these slices: each slice is one PR
> under L1 (a'), and its `LG-` quotes its row below as its scope. REQUIRED SUB-SKILL for each
> slice's executor: subagent-driven-development (recommended) or executing-plans. Each executor
> also binds `python-test`, `test-driven-development`, `dev-commands` (the two-half gate, the
> slot wrapper, the NFR measurement rules), `fastapi-service`, `contract-schema` and
> `git-hygiene`, reads [`README.md`](README.md)'s five unchecked conventions, and is spawned from
> `.claude/roles/executor.md`.

Filed under working id 9472, reserved by the lead. Written 2026-10-08 by the planner
(planner-replan) on the lead's brief `brief-planner-replan-2026-10-08.md`, deliverable 2. Evidence
read at `origin/main` `60e9254c` (#1242, 2026-10-08T12:40:57+01:00), by a full-class sweep: every
file under `docs/` naming `SL-1258`, `SL-1259`, `SL-1260` or WK-674 Slice 4, 5 or 6 (predicate:
`git grep -nE 'SL-1258|SL-1259|SL-1260|WK-674 [Ss]lices? [456]|later WK-674 slice' origin/main -- docs`),
plus the register's Decision cells (Python `re` over each row's last cell for
`WK-674 Slice|SL-1258|SL-1259|SL-1260|WK-674 S[456]`).

## Authority

- **Lean P2 L5**, the maintainer's entry "2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items
  1, 3 and 5 APPROVED; IN PRACTICE NOW; the files are amended through RFC 9479 P6 (the
  maintainer's amendment, by delegation)", as corrected by "2026-10-08 12:02:08 BST — #1240 P6
  flagged readings RULED: (1) REJECTED, and my 11:51:58 L1 (a) wording CORRECTED (the slice's one
  file is its LG-, not text under the roadmap row); (2) ACCEPTED": one plan per Work, slices as
  rows; a change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan.
- **The P2 re-plan**, the entry "2026-10-08 12:55:22 BST — P2 RE-PLAN RULED on the inventory
  (handover/p2-inventory-2026-10-09.md, at 60e9254c): F-1 (a), F-2 (b), F-3 (b), F-4 (a)+(b), F-5
  (a)/(b), F-6 (a)", F-5 (a): this delta is written now; and its correction "2026-10-08 13:00:11
  BST — FD-1374 (silent mispricing) STAYS IN P2: DP-F35-1 split out as a P2 WK-1178 slice; F35's
  performance remainder carries; and fewer, consolidated status messages".
- `kind: map`, because the PL template admits `map | leaf | review | handover` only and a delta
  is a Work-level plan with slices as rows (the lead's decision (b), 2026-10-08).

## Goal

Restate WK-674's last three slices as L5 rows, each carrying everything a dispatch needs, so that
each can be GO'd without a leaf plan: `SL-1258` (Slice 4, the deployment path), `SL-1259`
(Slice 5, switchover, rollback and the measurements) and `SL-1260` (Slice 6, date routing and
shadow). The Work's own goal is `PL-1237`'s, unchanged: the Work is done when every id in its Scope
has a verdict and the switchover meets the F1 acceptance test on the deployment path this Work
builds. **What changed since 2026-09-29** is listed per row under "Changes", each with its source.
Slice 3 (`SL-1257`, leaf plan `PL-1342`, `draft`, drafted before 11:51:58) is **not** in this
delta: it mints as-is (the entry "2026-10-08 11:53:19 BST — L5 transition RULED: per-slice plans
drafted before 11:51:58 MINT AS-IS (T8, B6, B9); their slices still follow L1 at GO").

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the named
tree.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` each exit 0 at the
   branch head, except check 31's line naming this file's working id, which clears at the mint.
2. **Every requirement id this delta cites is defined in a spec.** `audit-docs.py` (item 1) refuses
   an undefined `FR-`/`NFR-` id; the Self-review lists every id individually, and no row uses a
   numeric range: `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints only the
   prose sentences that list the ids beside the range.
3. **Each slice closes on its own L1 (a') ledger.** For each of `SL-1258`, `SL-1259`, `SL-1260`,
   one `LG-` under `docs/ledgers/` whose scope section quotes that slice's row below, verbatim:
   `git grep -lE 'SL-1258|SL-1259|SL-1260' -- docs/ledgers` prints one file per slice by the Work's
   close, and each cites this delta by its minted id.
4. **Slice 4:** `PL-1237` Acceptance items 2 and 12 hold on the Slice 4 path (FR-434 with NFR-534,
   FR-435 with NFR-531, each with its broken-input proof), and the FR-452 management-API limb test
   below is green and was seen red: `uv run pytest -q backend/tests -k management_rate_limit`
   exits 0, collects at least 2 tests, and the `LG-` quotes each one's red line.
5. **Slice 5:** `PL-1237` Acceptance items 5 and 6 hold in the host-fallback form, and the `LG-`
   records, each with the tree and the load at start: the F1 test (≥ 3 runs per n ∈ {2, 4, 8});
   NFR-489 **untraced** (OQ-1453 (a)), under both "per replica" readings (R5.3a); NFR-502; NFR-490 (FAIL with figures if red, carried per
   L4 of the 2026-10-08 move lines); NFR-493's linearity limb; NFR-494; NFR-501 (R5.10); and
   LG-1363's O4 multi-rung ladder bench.
   `git grep -nE 'NFR-489|NFR-490|NFR-493|NFR-494|NFR-501|NFR-502' -- <the LG>` prints a line for
   each id.
6. **Slice 6:** `uv run pytest -q backend/tests -k "routing or shadow"` exits 0, and the
   Environment-only flag refusal (RL-1311 item 3) and the routing-change-without-Audit-Event red
   proof are each quoted in the `LG-` by their printed line.
7. **The gate is green on each slice's merge tree**: the `CLAUDE.md` §11 commands, both halves,
   each exit 0, named against `origin/main...<slice branch>`.

## Global Constraints

`PL-1237`'s Global Constraints apply unchanged (money never float; `pricing-core` standalone; no
hand-written `model-schema` shape; spec first; push before poll; validate inbound only; ids listed
individually; measurement discipline). Added since:

- **One PR per slice** (L1 (a')): code, tests, any spec change, the `SL-` row's status line and one
  `LG-`; no leaf plan, no dispatch `RL-`, no activation PR. The `LG-` quotes the GO and ACK headers.
- **A measurement runs alone** (`RL-1263` item 3, which names WK-674 S5): an exclusive gate slot,
  nothing heavy beside it; and the sweep-pause rule of every role file (`.claude/roles/planner.md`).
- **The host fallback** (the maintainer's entry "2026-09-29 16:08:24 BST", quoted in `PL-1237`
  Acceptance item 6) governs every near-bound verdict: measured, diagnostic on the shared VM;
  carried, owner the maintainer, discharge event a dedicated host available.
- **Priority on every on-day** (the entry "2026-10-08 12:59:36 BST — USER: VM days follow the
  weekly allowance (about 4–5 project days after each reset). RE-BASELINE: plan on 4-in-7; a
  ranked CUT LADDER; pause-proof scheduling", item 2): G2's chain first, then the money and contract
  fixes, then the rest. WK-674 S4–S6 are "the rest" (`PL-1371` DP-6 (a): exit demo (b) needs WK-674
  S2 only).
- **Pause-proof** (same entry, item 3): Slice 5's solo window is booked to the first on-window
  after a resume, never to a calendar night.

## Tasks

Under L5 a Work plan's tasks are its slice rows; each slice's steps are written in its `LG-` by its executor.

Columns follow L5 (a): scope, requirements, dependencies, lane and order. Size is `PL-1371` §3.1's
likely figure. Lane is `PL-1371` §3.1's (lane B); the lead assigns the live lane at GO.

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Lane | Size |
|---|---|---|---|---|---|---|
| 1 | `SL-1258` — Slice 4: the deployment path | `PL-1237` Task 4 unchanged, plus R4.1 to R4.3 below | `07` §3.6: FR-434, FR-435, FR-437 (reference deployment); `07` §3.2: FR-412 (memory half), FR-415 (worker service); `07` §3.9: FR-452 (management-API limb, R4.1); `07` §9: NFR-531, NFR-534; register FD-1211 | `SL-1257` closed | B | 1 |
| 2 | `SL-1259` — Slice 5: switchover, rollback and the measurements | `PL-1237` Task 5, as changed by R5.1 to R5.10 below (with R5.3a) | `03` §3.10: FR-268, FR-269, FR-272 (rollback audit limb); `03` §9: NFR-489, NFR-490, NFR-493 (linearity limb), NFR-494, NFR-497 (mechanism), NFR-498 (rollback limb), NFR-501 (R5.10), NFR-502; register F-W9-1, F38, F41, FD-1411 (measurement half), F35 (measurement half) | `SL-1258` closed; `SL-1256` (closed, met) | B, **solo window** | 1 + solo window |
| 3 | `SL-1260` — Slice 6: date routing and shadow | `PL-1237` Task 6, as changed by R6.1 to R6.3 below | `03` §3.10: FR-270, FR-271, FR-272 (routing and shadow audit limb); `03` §9: NFR-498 (routing limb) | `SL-1259` closed | B | 1 |

Strictly in order, one at a time within the Work (`PL-1237` Sequencing). Under `RL-1263` a slice
of another Work may run beside S4 or S6; nothing heavy runs beside S5's measurement.

### Write sets and shared paths (the 2026-10-08 deltas audit, F3)

The expected write set of each row, at the path level, read against `origin/main` and the in-flight
PRs (#1243 `5da13384`, #1245 `ee858902`, #1247 `7e1f44d3`, by
`git diff --name-only origin/main...<sha>`). The executor states the actual set in its `LG-`.

| Slice | Expected write set |
|---|---|
| S4 `SL-1258` | `deploy/docker-compose.yml` (the `api` and `worker` services); Slice 3's rate-limit code under `backend/src/app/` (R4.1's management key); `backend/tests/` (the FR-452 and Task 4 tests); `docs/specs/07-platform.md` if a contract is clarified |
| S5 `SL-1259` | `backend/src/app/api/deployments.py`, `backend/src/app/platform/deployments.py` (switch and rollback); `backend/src/app/errors.py` if a code is added; `docs/specs/03-rating-engine.md` (§3.10, §9 verdict text); `docs/contracts/openapi/generated.json`; `backend/tests/` |
| S6 `SL-1260` | `backend/src/app/api/deployments.py`, `backend/src/app/api/environments.py`, `backend/src/app/platform/` (routing, shadow); `backend/src/app/errors.py` (the routing codes); `docs/specs/03-rating-engine.md` §3.4 (the FR-241 cross-reference, `PL-1237:976`), §4 (the routing and shadow contracts) and §5.1 (the routing route); `docs/contracts/openapi/generated.json`; a migration under `backend/migrations/versions/` if the routing rule is persisted |

**Shared paths, rebase-serialised:**
- **`backend/src/app/errors.py`** — S5 and S6 add codes; `SL-1472` (#1247) and SL 9469 (`PL 9470`)
  also edit it. One registry line each; the later PR rebases onto the earlier.
- **`03` §3.4 (Rating versions)** — S6 corrects FR-241's cross-reference there; WK-675 S10 adds its
  new FR there. `PL-1286:398` records it: "S10 (its new FR) | `03` §3.4 (Rating versions) | WK-674
  Slice 6 (the FR-241 cross-reference in §3.4, `PL-1237`:976) | **serialise**". The two never
  run in parallel on that section; the later rebases onto the earlier.
- **`docs/specs/03-rating-engine.md` and `docs/contracts/openapi/generated.json`** as files — touched
  by #1243, #1245 and #1247 and by every route-adding slice: ordinary rebase serialisation.

Nothing here edits `SL-1472`'s code paths (`compile.py`, `modelling.py`, `rating_versions.py`).

### Slice 4 (`SL-1258`) — changes since `PL-1237`

- **R4.1 — FR-452's management-API limb is placed here** (planner's slice design; `docs/roadmap.md`
  `SL-1257` row: "carried to a later WK-674 slice, which a planner names … before WK-674 closes; that
  slice's row is annotated when named"). FR-452 (`07` §3.9): "scoring limits configured separately
  from management-API limits, and `429` responses carrying `Retry-After`". Slice 3 builds the
  scoring counter (`RL-1347`); this slice applies the management-API limit on the `api` service it
  deploys, reusing Slice 3's counter mechanism under a separate key and limit, per Environment and
  Principal. Tests, named `test_management_rate_limit_*` and marked `req("FR-452")`: a management
  route called past its limit answers `429` with `Retry-After`; and `/score`, under its own limit,
  is not refused when the management limit is exhausted. Each is seen red before the code, by that
  cause (no limit applied; one shared counter), never by a bare status. **The lead annotates
  `SL-1257`'s roadmap line when this delta mints** (the roadmap sentence's own instruction).
  Why S4: it is the slice that stands up the `api` service and its harness, so the limit is proven
  on the path it ships on; S6 would place it after the measurements it does not affect.
  **Accepted by the maintainer**, the entry "2026-10-08 14:32:33 BST — DELTAS AUDIT (handover/audit-deltas-2026-10-08.md) noted; fixes proceed; DP A, B (c), C confirmed, D AMENDED (build in reverse ladder order)", item A: "ACCEPTED: FR-452's management-API
  limb goes in WK-674 S4 (roadmap :989 left the slice to a planner). S4 is not a ladder rung; its
  write set is named per F3."
- **R4.2 — FD-1211's event, stated whole.** The design states whether `worker` and `api`
  **finalize the interpreter on stop or recycle** (`FD-1211`, register `:196`), and the test that
  repeats the extension-loading exit states its count (already in `PL-1237` Task 4's gate).
- **R4.3 — "per replica" is stated, not assumed.** `PL-1454` DP-3 (`:339`) found that no spec
  defines "per replica" for NFR-489, and `PL-1454` is carried to Phase 3 with `SL-1455` (move line
  L4, 2026-10-08). The harness this slice builds therefore records, for every run, the replica
  count, the worker count and the load-balancing topology, so Slice 5's NFR-489 figure can be read
  under either reading. It does not choose the reading (DP-1 below, ruled (c)).

### Slice 5 (`SL-1259`) — changes since `PL-1237`

- **R5.1 — F35's remedy is carried to Phase 3; Slice 5 no longer waits on it.** `CR-1247:306`
  ("F35's remedy is a WK-1178 slice before WK-674 Slice 5") and `FD-1246`'s "the WK-1178 trace
  slice sequenced before WK-674 Slice 5" are overtaken by F-3 (b) as corrected at 13:00:11:
  PL 9776 (working id) less its DP-F35-1 limb carries, owner the maintainer, event P3's first
  plan. **NFR-490 is measured on Slice 5's tree and, if red, recorded FAIL with the figure, the tree
  and the log** (`PL-1237` Task 5, unchanged), and the residual is stated with that owner — which is
  also register `:77`'s form ("states the residual with an owner"), so the two now agree.
- **R5.2 — `SL-1455` is carried to Phase 3; Slice 5 no longer follows it.** `PL-1454:268` ("this
  slice precedes SL-1259") falls with the carry. FD-1411's Decision cell (register `:293`: "fix before
  close with an owner: SL-1259 … Event: the remedy merges and SL-1259 records the NFR-489 verdict")
  now has its remedy in Phase 3; Slice 5 records NFR-489's verdict as measured, diagnostic (host
  fallback) and names FD-1411's remedy as carried. The register cell's dated line is the register
  minter's (see **Hand-off**).
- **R5.3a — NFR-489 is recorded under both "per replica" readings** (DP-1, ruled (c) by the
  entry "2026-10-08 14:32:33 BST — DELTAS AUDIT (handover/audit-deltas-2026-10-08.md) noted; fixes proceed; DP A, B (c), C confirmed, D AMENDED (build in reverse ladder order)", item B: "NFR-489 'per replica' records BOTH readings. The interpretation is
  ruled in P3's first plan, owner WK-1178, since the remedy is carried to P3 and NFR-489 stays
  diagnostic under G4. No P2 work depends on the choice."). Slice 5's `LG-` gives the figure per
  `api` process and per container behind the load balancer, from R4.3's recorded topology, and
  names the interpretation as carried: owner WK-1178, event P3's first plan.
- **R5.3 — NFR-489 is measured untraced.** `OQ-1453`, decided (a) 2026-10-05
  (`open-questions.md:144`; `03:1424`): NFR-489 "governs UNTRACED real-time requests"; a traced
  request is bounded by NFR-490.
- **R5.4 — NFR-502 on `/score/compare` too, if the extension has landed.** `RL-1365:130,181`: the
  maintainer accepted NFR-502's scope extension to `/score/compare`, and `SL-1259` owns the
  full-path measurement. If `03`'s NFR-502 row carries the extension on Slice 5's base tree
  (`git grep -n 'score/compare' -- docs/specs/03-rating-engine.md` on NFR-502's row), Slice 5 measures
  both routes; if not, `/score` only, and the `LG-` says which.
- **R5.5 — LG-1363's O4: the multi-rung ladder bench.** `LG-1363:229`: "Owner: SL-1259 …
  Discharging event: a multi-rung bench (6–8 rungs), before and after, in a solo window." It runs
  in Slice 5's solo window.
- **R5.6 — never in PL-1364 Task 5's window.** `PL-1364:771`: Slice 5's NFR-502 measurement "never
  shares a window with Task 5's".
- **R5.7 — rollback reuses Slice 2's route shape**, and replaces Slice 2's per-request resolution
  with the switch (`PL-1392:1396-1397`). The rollback's Audit Event action is
  `deployment.rolled_back`, its `entity_ref` naming the Deployment or Environment it changes; no new
  catalogue entry is appended (`03:908`; `PL-1392:1015-1016`).
- **R5.8 — NFR-497's degraded-read evidence is quoted beside the verdict at the close**
  (`RL-1232:188`); the availability verdict stays the lead's.
- **R5.9 — the trigger does not apply.** The F-4 (b) contingency trigger (A-3 by Tue 27 Oct) is
  G2's; Slice 5 is not on G2 (`PL-1371` DP-6 (a)). If exit demo (b)'s plan finds a call to an S4–S6
  route, it adds that slice as a dependency (`PL-1371:366`); none is expected (`PL-1371:522`).
- **R5.10 — NFR-501 is placed here** (the 2026-10-08 deltas audit, F1). `PL-1237` Acceptance item
  7 (`:193`) places register row F-W9-1 as "NFR-502 and NFR-501, Slice 5"; NFR-501 (`03` §9,
  `03-rating-engine.md:1393`: GBM `model_call` steps execute with `nthread=1` per request) is
  not in `PL-1237`'s Scope table, which is why the first statement of this row missed it. Slice 5
  verifies on its deployment path that a GBM `model_call` step runs with `nthread=1`, and the
  `LG-` records the verdict beside NFR-502's under F-W9-1.

### Slice 6 (`SL-1260`) — changes since `PL-1237`

- **R6.1 — the flags are Environment-only.** `OQ-1235` is decided by `RL-1311` (item 3, `:251`):
  FR-270's and FR-271's flags are declared Environment only. Test (`RL-1311:275`): a workspace-level
  write of either flag is refused, and an Environment-level write enables it in that Environment
  only.
- **R6.2 — the audit action names are fixed:** `deployment.routing_changed` and
  `deployment.shadow_configured`, each `entity_ref` naming the Deployment or Environment it
  changes; nothing is appended to the catalogue (`03:908`; `PL-1392:1015-1016`).
- **R6.3 — nothing waits on it in P2.** WK-675 S12 (the Deployments view, which waited on
  `SL-1260`) moved to Phase 3 on 2026-10-03 (`docs/roadmap.md`, the WK-675 move line). **Slice 6 is
  rung 5 of the ruled cut ladder**, the maintainer's entry "2026-10-08 13:21:00 BST — CUT LADDER
  (handover/cut-ladder-2026-10-08.md) RULED: rungs 1–7 adopted in that order (7 conditional); rung 8
  VOID; rung 9 OFF the automatic ladder; mid-week application limited", item (1): "WK-674 S6" is the
  fifth rung. It is cut only when that rung applies, by a dated move line quoting the header above.

### Carried rows that no WK-674 slice takes

- **FR-272's notification limb:** `OQ-1233` is decided (b), FR-453 to WK-688 (`docs/roadmap.md`;
  `03:207`). No WK-674 slice takes it; the closure record's verdict is "reassigned".

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | What does NFR-489's "per replica" mean for Slice 5's verdict? (`PL-1454` DP-3, carried to P3 unruled) | (a) per `api` process; (b) per container behind the load balancer; (c) record both, verdict carried | (c) | spec interpretation | no | **ruled (c)** by the maintainer, 2026-10-08 14:32:33 BST, item B (R5.3a): both readings recorded; the interpretation is ruled in P3's first plan, owner WK-1178 |
| DP-2 | Is WK-674 Slice 6 kept in P2? | (a) keep; (b) cut to P3 by a dated move line | none from this plan: it is **rung 5** of the cut ladder the maintainer ruled at 2026-10-08 13:21:00 BST (R6.3), applied only by a dated move line | scope | no | ruled: the ladder, rung 5 |

## Hand-off (not this plan's writes)

- The lead lists this delta's id on WK-674's roadmap row (L5) and annotates `SL-1257`'s line for
  FR-452 (R4.1).
- The register minter appends dated lines to FD-1411 (`:293`) and F35 (`:77`, already drafted as R1
  in the move-line file) so that their events read against the carries; F-W9-1 (`:59`) and F38
  (`:80`) still name pre-`PL-1237` owners and are stale (sweep finding; the auditor's to correct).
- `RL-1365:98` calls `SL-1259` "WK-673 Slice 5" — a frozen record; a correcting record, if wanted,
  is the decision-maker's.

## Self-review

- **Spec coverage.** Every id in `PL-1237` Scope assigned to Slices 4–6 appears in a row: FR-268,
  FR-269, FR-270, FR-271, FR-272, FR-412, FR-415, FR-434, FR-435, FR-437, NFR-489, NFR-490, NFR-493,
  NFR-494, NFR-497, NFR-498, NFR-502, NFR-531, NFR-534; plus FR-452's management limb, which was
  unassigned, and NFR-501 (R5.10), which `PL-1237` places by Acceptance item 7 and not by its Scope
  table (added 2026-10-08 on the deltas audit's F1). FR-267, FR-428, FR-429 (Slice 2), FR-430, FR-431 and NFR-496 (Slice 3), FR-18 and FR-436
  (Slice 1) are not this delta's.
- **Placeholders.** None: each change cites its source by path and line at `60e9254c`.
- **Consistency.** R5.1 and register `:77` now agree; R5.2 changes FD-1411's event, routed to the
  register minter, not edited here.
- **Rulings since the sweep.** `gh pr list --state open` at 2026-10-08 13:06 BST (`date`), titles matched
  with `grep -iE 'WK-674|SL-1258|SL-1259|SL-1260|deployment|switchover'`: #1116 (FD 9721) and #976
  (FD 9890), both Slice 2 findings in batch B3, neither ruling on Slices 4–6. Re-run at mint.
