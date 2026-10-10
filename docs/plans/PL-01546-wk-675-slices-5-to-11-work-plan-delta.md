---
id: PL-1546
family: plan
kind: map
title: WK-675 — Slices 5 to 11 (editor II, sandbox, compare, rating version list, regression suite view, dislocation views, sub-graph mounting) as rows, after the 2026-10-08 re-plan: Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-10  # original date 2026-10-08, set at the draft; minted 2026-10-10
owner: planner
tree: 60e9254c22972c03fb11f10fcce8dae4f1c00dd9
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1286, PL-1371, PL-1364, PL-1267, PL-1254, PL-1419, RL-1261, RL-1263, RL-1307, RL-1418, RL-1459, RL-1473, RL-1474, RL-1483, OQ-1223, OQ-1440, OQ-1460, FD-1283, FD-1335, FD-1366, SL-1367, SL-1388, SL-1341, SL-1256]
---

# PL-1546 — WK-675 Slices 5 to 11 as rows: Work-plan delta

> **For agentic workers:** this is a **Work-plan delta** under Lean P2 L5. It does not replace
> [`PL-1286`](PL-01286-wk-675-frontend-dag-designer-rate-table-editor-quote-sandbox-and-dislocation-views-map-plan.md)
> (WK-675's map plan, `draft` at this tree); it `relates:` it and states, in one place, the
> eight slices WK-675 has not planned — S5, S6, S7b, S7, S10, S11, S8 and S9 — with every change
> to them since `PL-1286` was written. **Read `PL-1286`'s Goal, Acceptance Standard, Global
> Constraints, Carried obligations table (its S5–S11 rows) and Sequencing first, then this
> file**; where they differ, this file is the later statement. No per-slice leaf plan is written:
> each slice is one PR under L1 (a'), and its `LG-` quotes its row below as its scope. REQUIRED
> SUB-SKILL for each slice's executor: subagent-driven-development (recommended) or
> executing-plans. Each executor also binds `vue-frontend`, `vue-best-practices`,
> `vue-testing-best-practices`, `python-test` (for S7b and any backend route), `test-driven-development`,
> `dev-commands` (the two-half gate) and `git-hygiene`; a slice with a chart also has
> `accessibility-tester` verify it. Each reads [`README.md`](README.md)'s five unchecked
> conventions and is spawned from `.claude/roles/executor.md`.

Drafted under working id 9471, reserved by the lead; minted 2026-10-10 as PL-1546, with its eight SL rows (SL-1547 … SL-1554), in the D2 batch mint (re-minted +1 on 2026-10-09 by the minting rewrite, on the lead's 13:09:28 BST ruling (1): first minted as PL 1545 and SL 1546 … SL 1553, space form so the old ids are not live citations, before D1's PL-1535 and PL-1537 took their ids). Written 2026-10-08 by the planner
(planner-replan) on the lead's brief `brief-planner-replan-2026-10-08.md`, deliverable 2. Evidence
read at `origin/main` `60e9254c` (#1242, 2026-10-08T12:40:57+01:00), by a full-class sweep over
`docs/` for every later statement on these slices (predicates, verbatim:
`git grep -nE 'WK-675 (S|Slice )(5|6|7|7b|8|9|10|11)\b' origin/main -- docs ':(exclude)docs/plans/PL-01286-*'`;
`git grep -nE '\bS7b\b'`; `git grep -n 'OQ-1223'`; `git grep -ln 'PL-1286'`; and
`git grep -n 'WK-675' -- docs/findings/register.md`).

## Authority

- **Lean P2 L5**, the maintainer's entry "2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items
  1, 3 and 5 APPROVED; IN PRACTICE NOW; the files are amended through RFC 9479 P6 (the
  maintainer's amendment, by delegation)", as corrected by "2026-10-08 12:02:08 BST — #1240 P6
  flagged readings RULED: (1) REJECTED, and my 11:51:58 L1 (a) wording CORRECTED (the slice's one
  file is its LG-, not text under the roadmap row); (2) ACCEPTED".
- **The P2 re-plan**, "2026-10-08 12:55:22 BST — P2 RE-PLAN RULED on the inventory
  (handover/p2-inventory-2026-10-09.md, at 60e9254c): F-1 (a), F-2 (b), F-3 (b), F-4 (a)+(b), F-5
  (a)/(b), F-6 (a)", F-2 (b): "The ONE WK-675 delta (S5–S11) is written now; map PL-1286 is made
  active in that delta's batch, its status line only"; and S13 and S14 move to P3.
- **The cut ladder**, "2026-10-08 12:59:36 BST — USER: VM days follow the weekly allowance (about
  4–5 project days after each reset). RE-BASELINE: plan on 4-in-7; a ranked CUT LADDER; pause-proof
  scheduling", item 1: S9, then S10/S11, are its first rungs. **This delta does not pre-cut them**;
  it marks them, and a dated move line applies a rung when the maintainer's ladder says so.
- **The ladder as ruled**, "2026-10-08 13:21:00 BST — CUT LADDER (handover/cut-ladder-2026-10-08.md)
  RULED: rungs 1–7 adopted in that order (7 conditional); rung 8 VOID; rung 9 OFF the automatic
  ladder; mid-week application limited", item (1): this Work's rungs are S9 (rung 1), S10+S11
  (rung 2) and S8 (rung 7, "void if PL 9629's served page is that view; the #1164 pass decides
  it"); "Rung 9 (WK-675 S7+S7b) is REMOVED from the automatic ladder … If rungs 1–7 are spent and
  the line is still missed, it comes to me as a decision."
- **The build order**, "2026-10-08 14:32:33 BST — DELTAS AUDIT (handover/audit-deltas-2026-10-08.md)
  noted; fixes proceed; DP A, B (c), C confirmed, D AMENDED (build in reverse ladder order)", item D:
  "build WK-675 in REVERSE LADDER ORDER where no dependency forbids it: S5 → S6 → S7b → S7 → S8 → S10
  → S11 → S9."
- `kind: map`, because the PL template admits `map | leaf | review | handover` only (the lead's
  decision (b), 2026-10-08).

## Goal

Plan WK-675's remaining P2 slices as L5 rows so each can be GO'd without a leaf plan. Done for
this delta when each of S5, S6, S7b, S7, S10, S11, S8 and S9 has closed on its own `LG-`, or has
been moved to Phase 3 by a dated move line. The Work's own goal is `PL-1286`'s, less what has
left P2: **S12** (2026-10-03) and **S13, S14** (2026-10-08, F-2 (b)). S3 (PL 9578) and S4 (PL 9582)
were planned before 11:51:58 and mint as-is (the entry "2026-10-08 11:53:19 BST — L5 transition
RULED: per-slice plans drafted before 11:51:58 MINT AS-IS (T8, B6, B9); their slices still follow
L1 at GO"); they are not rows here.

**`PL-1286` goes `active`** in this delta's mint batch, by its status line only (F-2 (b)). Its
Decision points table is not edited: DP-1 is ruled by `RL-1307` (c), DP-2 by `RL-1261` (b), DP-4 by
the maintainer's 2026-09-30 05:34:33 scope decision (a), DP-5 by `RL-1473`, DP-6 by `RL-1474`,
DP-7 moved to Phase 3 with S12; **DP-3 (OQ-1223) is the one still open**, and it is non-blocking for
the freeze (`PL-1286`: "no — resolved before Slice 5's leaf plan goes `active`"), so it now blocks
S5's GO instead.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` exit 0 at the
   branch head, except check 31's line naming this file's working id, which clears at the mint.
2. **Each slice closes on its own L1 (a') ledger**, whose scope section quotes that slice's row
   below verbatim: by the Work's close, `git grep -l 'PL-<this delta's minted id>' -- docs/ledgers`
   prints one `LG-` per slice that was not moved to Phase 3, and each names its slice's `SL-` id.
3. **Each FR a row lists has a test naming it** (`PL-1286` Acceptance item 3, unchanged):
   `grep -rlE '<id>[^0-9]' frontend/src --include=*.test.ts` prints at least one file per id, and a
   backend route a row adds carries `@pytest.mark.req("<id>")`.
4. **No hand-written API shape:** `uv run python scripts/generate-contracts.py --check` exits 0, and
   `pnpm --dir frontend generate:api` leaves `git status --short frontend/src/api/generated` empty.
5. **Every chart a row adds has its accessible table** in `RL-1307`'s column-descriptor form
   (NFR-463), and `accessibility-tester`'s report is quoted in that slice's `LG-`.
6. **S5 does not start before OQ-1223 is decided:** `git grep -n 'OQ-1223' -- docs/open-questions.md`
   on S5's base tree shows the row decided, with its resolver `RL-`.
7. **S7's `own_change` rule:** `PL-1286` Acceptance item 8 holds — a compare-view test asserts that
   `own_change: false` is never rendered as "unchanged" or "not edited".
8. **The gate is green on each slice's merge tree**: the `CLAUDE.md` §11 commands, both halves,
   each exit 0, against `origin/main...<slice branch>`.

## Global Constraints

`PL-1286`'s Global Constraints apply unchanged: Vue 3 `<script setup lang="ts">` only; no hand-written
API type; money never a float (FR-10, FR-21); WCAG 2.2 AA and a table for every chart (NFR-463);
every route reachable (FR-25); a new dependency changes `docs/skills-map.md` and the spec's §8 in
the same PR. Added since:

- **One PR per slice** (L1 (a')): code, tests, any spec change, the slice's `SL-` row status line
  and one `LG-`; no leaf plan, no dispatch `RL-`, no activation PR.
- **At most two build slices at once, from different Works** (`RL-1263`), and one WK-675 slice at a
  time within the Work (`PL-1286`).
- **Priority on every on-day** (the 12:59:36 entry, item 2): G2's chain, then money and contract
  fixes, then the rest. WK-675 is off G2's critical path (RL 9623, working id, #1160) and is "the rest".
- **Spec first** (`CLAUDE.md` §0): S10 and, if needed, S11 each change `03` before their code, in
  the same PR.

## Tasks

Under L5 a Work plan's tasks are its slice rows; each slice's steps are written in its `LG-` by its
executor. Columns follow L5 (a): scope, requirements, dependencies, lane and order. Size is
`PL-1286`'s likely figure (worst 2). **Lane: assigned at GO** for every row. WK-675 from S3 on is
PROPOSED to move to a second contributor team (to-lead "2026-10-08 13:07:20 BST — USER: the new
contributor runs HER OWN Claude team (team B). The two-team protocol; CONTRIBUTING.md re-scoped to
it; WK-675 is the proposed team-B Work", T1, in effect when team B starts); the lane or team is
fixed at each slice's GO. **Order is reverse ladder order** (item D of the 14:32:33 entry), which
amends `PL-1286:370` (S12, S13 and S14 removed) by moving S8 ahead of S10 and S11: the least likely to
be cut are built first, so a cut never discards finished work. **No S8 dependency on S10 or S11
exists** (checked, item D's condition): S8 needs S1 and `SL-1388` only (`PL-1286:363` and
`:381-382`), and `PL-1286:377-380` calls S10/S11-before-S8 "a preference, not a dependency". A slice
whose dependency is unmet waits; the next ready slice in this order takes its turn (`PL-1286:372-387`).
If exit demo (b)'s served page is S8's view (the #1164 pass), S8 is a demo need and moves earlier still.

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Lane | Size | Ladder |
|---|---|---|---|---|---|---|---|
| 1 | SL-1547 — S5: Editor II: diff shading, bulk, import, export | `PL-1286` S5 row, plus R5.1–R5.3 | `03` §3.3: FR-230, FR-231, FR-232, FR-233, FR-235; `00`: FR-25; NFR-463; register F-W10-1, F-W10-2 (view limb) | S4 closed; **OQ-1223 decided** (DP-3); `SL-1391` (closed, met); the FD-1366 bulk-operation typing slice (WK-1178) merged | at GO | 1 | no |
| 2 | SL-1548 — S6: Sandbox: form, waterfall, trace | `PL-1286` S6 row, plus R6.1–R6.2 | `03` §3.1: FR-213; §3.6: FR-247, FR-248, FR-249 (shown absent, R6.1); §3.7: FR-251, FR-252, FR-255, FR-256; §3.8: FR-258; FR-25; NFR-463 | S1 (closed, met); **`SL-1367` merged** (FD-1335 hold) | at GO | 1 | no |
| 3 | SL-1549 — S7b: Compare backend | `PL-1286` S7b row, plus R7b.1 | `03` §4.10 `StepChange.own_change`; §3.8: FR-262 (backend limb) | `RL-1261` (met); **`SL-1367` merged first** (both edit `score_compare`) | at GO | 1 | not on the automatic ladder (rung 9 is OFF; to the maintainer if rungs 1–7 are spent) |
| 4 | SL-1550 — S7: Sandbox compare | `PL-1286` S7 row | `03` §3.8: FR-262 (view limb); §4.10's `own_change` rendering rule | S6, S7b closed; `SL-1367` merged | at GO | 1 | not on the automatic ladder (rung 9 is OFF; to the maintainer if rungs 1–7 are spent) |
| 5 | SL-1551 — S8: Dislocation views | `PL-1286` S8 row, plus R8.1 | `03` §3.9: FR-263, FR-264, FR-265, FR-266; NFR-463 | S1 (met); **`SL-1388`** (WK-673 S4) closed | at GO | 1 | **rung 7 (conditional on #1164's served page)**: void if exit demo (b)'s served page is this view |
| 6 | SL-1552 — S10: Rating version list | `PL-1286` S10 row, as changed by R10.1 | `03` §3.4: one new FR (spec first, R10.1); FR-25; `FD-1283` option A | S8 (order, item D); DP-5 (`RL-1473`, met); `SL-1256` (closed, met); **`03` §3.4 serialised with WK-674 S6** (`SL-1260`, R10.2) | at GO | 1 | **candidate, rung 2** (with S11) |
| 7 | SL-1553 — S11: Regression suite view | `PL-1286` S11 row | `03` §3.8: FR-260, FR-261, FR-1221; `FD-1283` option A; a run-list read route under DP-4 (a) only if the version's evidence gives no run id | S10 (order); DP-5 (met) | at GO | 1 | **candidate, rung 2** (with S10) |
| 8 | SL-1554 — S9: Designer III: sub-graph mounting | `PL-1286` S9 row | `03` §3.1: FR-217 (the mount), FR-218 (authoring view) | S3 closed; **`SL-1341`** (WK-1250 S3) closed | at GO | 1 | **candidate, rung 1** |

### Changes since `PL-1286`, per slice

- **R5.1 — the cells route.** `PL-1419:790-792` (WK-673 S7): "WK-675 Slice 5 … is unblocked … Its
  diff shading and exposure-weight column page through the cells route", and `RL-1418:289`: "PL-1286
  S5 (WK-675) reads the per-cell weight from this route". S5 uses that paged cells route for the
  shading and the weight column, never a whole-table read.
- **R5.2 — the cells route's latency budget.** `OQ-1440` (decided, `open-questions.md:142`) sets a
  p95 budget on that route; S5 renders against it and does not re-measure it.
- **R5.3 — the bulk-operation typing hold.** `PL-1371:195` and its model (`:611`, "1178-FD9779B"):
  S5 calls `bulk-operation`, so it waits until that route is typed — the FD-1366 residue, which
  WK-1178 builds in P2 (F-3 (b) keeps it in the money and contract group).
- **R6.1 — FR-249's per-peril limb has no producer yet.** `RL-1459:34,71`: "WK-675 S6's FR-249 limb
  is carried with it …, so S6 does not build a view with no producer"; S6 "shows per-peril output as
  absent meanwhile". `OQ-1460` (owner WK-1178) carries the question. S6 renders the per-peril
  components as absent, with a test that says so, and its `LG-` records FR-249's view limb as
  carried under `OQ-1460`.
- **R6.2 — the FD-1335 hold.** `PL-1364:734` ("held: S6 does not dispatch until this slice merges")
  and `PL-1364:1068`; `FD-1335`'s disposition: Part A lands before any WK-675 slice that consumes
  `/score` or `/score/compare`. Same for S7 (`PL-1364:735`).
- **R7b.1 — S7b serialises after `SL-1367`.** `PL-1364:736`: "**serialise.** `score_compare` is one
  existing function, and this slice edits its decorator. Recommended order: this slice first".
  `PL-1286:310,368` listed S7b as needing nothing from another Work; `PL-1371:197` and
  `PL-1364:736` add the order. S7b also handles WK-1250 S2's namespaced `step_id`s if `SL-1340` has
  merged on its base (`PL-1286:403`).
- **R10.1 — the list route already exists; S10 amends its row.** `RL-1483:220-228`: `GET
  /api/v1/rating-versions` exists in code (`models.py:1113`); that ruling's slice adds its `03` §5.1
  row as "records an existing route", and "The list read belongs to WK-675 Slice 10 (FD-1283)"; the
  owners' later spec changes "amend those rows, not add them". So S10's spec-first task is: **the
  new `03` §3.4 FR for the list view's read, and an amendment to the existing §5.1 row** (filters by
  status, the live badge's source), not a new row. If the row is not on S10's base tree
  (`git grep -n 'GET.*/rating-versions' -- docs/specs/03-rating-engine.md`), S10 stops and reports:
  adding it is `RL-1483`'s slice's, not S10's. Whether `RatingVersionView` stays is S10's question
  (`RL-1473:124-126`), answered in its `LG-`.
- **R10.2 — `03` §3.4 is serialised with WK-674 S6.** `PL-1286:398`: "S10 (its new FR) | `03` §3.4
  (Rating versions) | WK-674 Slice 6 (the FR-241 cross-reference in §3.4, `PL-1237`:976) |
  **serialise**". S10's spec-first change and `SL-1260`'s FR-241 correction never edit §3.4 in
  parallel; whichever merges second rebases onto the first. PL-1537 states the same
  from WK-674's side.
- **R8.1 — the slug route form.** `RL-1473:200`: "Slices 3–8, 10 and 11 use the same resolution.
  None of them adds a second lookup." Applies to S8, S10 and S11.

### The cut-ladder rows (marked, not cut)

**S9** (rung 1), **S10 with S11** (rung 2) and **S8** (rung 7, conditional on #1164's served page)
are this Work's rungs on the ladder the maintainer ruled at 13:21:00 (see Authority). **S7 and S7b
are not on the automatic ladder**: rung 9 is OFF, and if rungs 1–7 are spent they go to the
maintainer as a decision. Cutting S9 leaves FR-217's and
FR-218's authoring limbs for Phase 3 and breaks nothing in P2 (nothing depends on S9). Cutting S10
and S11 leaves `FD-1283`'s two views unbuilt, keeps the interim FR-25 path through
`RatingVersionView`, and avoids R10.1's spec change. Cutting S8 leaves FR-263, FR-264, FR-265 and
FR-266's view limbs for Phase 3; the rung is void if exit demo (b)'s served page is S8's view. Until
a dated move line applies a rung, these rows stand, and the reverse ladder order schedules them
last.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-3 = OQ-1223 | How does an ordinal categorical input take part in a `monotone` property? (`PL-1286` DP-3) | as the OQ states them: (a) declare ordinality on `InputContractField`; (b) read the order of `domain` | the OQ's own (a), "when the rate-table editor introduces the order" | decision point | **yes, for S5's GO** (was "before S5's leaf plan goes active"; there is no leaf plan under L5) | decision-maker, by `RL-` |

## Hand-off (not this plan's writes)

- The lead lists this delta on WK-675's roadmap row (L5) and sets `PL-1286` `active` by its status
  line in the mint batch (F-2 (b)).
- **SL rows.** S5, S6, S7b, S7, S10, S11, S8 and S9 had no `SL-` rows on main (`PL-1371:550`). The lead
  reserved SL-1547 (S5), SL-1548 (S6), SL-1549 (S7b), SL-1550 (S7), SL-1551 (S8), SL-1554 (S9), SL-1552 (S10)
  and SL-1553 (S11); their planner-cut `draft` rows are in `docs/roadmap.md` under WK-675, on this branch.
- `PL-1286` Acceptance item 2 counts "nine views' routes"; with S12, S13 and S14 in Phase 3 the
  closing auditor reads it against the views still in P2, and records the three as moved, not missing.
- `PL-1286`'s locator for `03` §5.3 (`03:1041-1058`) has drifted to `03:1277-1286` at this tree; a
  frozen plan is not edited — read by heading.

## Self-review

- **Spec coverage.** Every id `PL-1286` assigns to S5–S11 is in a row: FR-213, FR-217, FR-218,
  FR-230, FR-231, FR-232, FR-233, FR-235, FR-247, FR-248, FR-249, FR-251, FR-252, FR-255, FR-256,
  FR-258, FR-260, FR-261, FR-262, FR-263, FR-264, FR-265, FR-266, FR-1221, FR-25, NFR-463, and
  register F-W10-1, F-W10-2. FR-249's view limb is carried (R6.1), not dropped.
- **Placeholders.** None; the `SL-` ids are the lead's reservation of 2026-10-08.
- **Consistency.** The order is reverse ladder order (item D, 14:32:33), S8 before S10/S11, which
  amends `PL-1286:370`'s preference; no dependency forbids it (Tasks). `PL-1371:304` lists S5 after
  S10, which is a calendar, not a dependency.
- **Rulings since the sweep.** `gh pr list --state open` at 2026-10-08 13:11 BST (`date`), titles
  matched with `grep -iE 'WK-675|OQ-1223|S7b'`: #1198 (RL 9543, S3/S4/S13 DPs), #1185, #1186, #1187,
  #1189 (S13, S3, S4, S14 leaf plans) and #1160 (RL 9623). None rules on S5–S11. **#1187 also cuts
  `SL` rows 9577 and 9575 for S13 and S14**, which move to Phase 3 (move line L3): the minter keeps or
  drops them as the lead rules. Re-run at mint.
