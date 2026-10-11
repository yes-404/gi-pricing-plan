---
id: PL-9921
family: plan
kind: map
title: WK-674 — Slices 4 and 5 (deployment path; switchover, rollback and the measurements) after SL-1455 returned to P2: Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-11
owner: planner
tree: 99f22479a20e7fa64f8b6654e0d371c595b1e35a
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1537, PL-1583, PL-1454, RL-1232, RL-1263, RL-1347, RL-1365, OQ-1453, FD-1411, FD-1211, SL-1257, SL-1258, SL-1259, SL-1455]
---

# PL-9921 — WK-674 Slices 4 and 5 after SL-1455 returned to P2: Work-plan delta

> **For agentic workers:** this is a **Work-plan delta** under Lean P2 L5. It does not replace
> [`PL-1237`](PL-01237-wk-674-deployment-environments-switchover-tenancy-map-plan.md) (WK-674's
> map plan, `active`) or [`PL-1537`](PL-01537-wk-674-slices-4-to-6-work-plan-delta.md) (the
> 2026-10-08 delta for Slices 4 to 6). It `relates:` both, and it states every change to
> Slices 4 and 5 since `PL-1537`. **Read `PL-1237` Tasks 4–5, its Acceptance Standard and Global
> Constraints, then `PL-1537`, then this file.** Where they differ, this file is the later
> statement. Slice 6 (`SL-1260`) is not changed. No per-slice leaf plan is written. Each slice is
> one PR under L1 (a'), and its `LG-` quotes its `PL-1537` row **and** this file's changes for
> that slice as its scope. REQUIRED SUB-SKILL for each slice's executor:
> subagent-driven-development (recommended) or executing-plans. Each executor also binds
> `python-test`, `test-driven-development`, `dev-commands` (the two-half gate, the slot wrapper,
> the NFR measurement rules), `fastapi-service`, `contract-schema` and `git-hygiene`. It reads
> [`README.md`](README.md)'s five unchecked conventions and is spawned from
> `.claude/roles/executor.md`.

Filed under working id 9921, reserved by the lead (brief `brief-planner-wk674-2026-10-11.md`).
Written 2026-10-11 by the planner (planner-wk674). Evidence read at `origin/main` `99f22479`
(#1271, 2026-10-10 23:44 BST merge). The sweep is by full class: every `docs/` file that names
`SL-1258` or `SL-1259`, by the predicate `grep -rln 'SL-1258\|SL-1259' docs --include=*.md`, and
every `to-lead.md` entry naming `PL-1537`, `SL-1258`, `SL-1259`, `SL-1455` or WK-674 S4/S5 since
`PL-1537`'s mint (2026-10-09).

## Authority

- **The form:** the maintainer's entry "2026-10-11 10:55:55 BST — WK-674 S4/S5 readiness: PL 9921
  (one delta, L5) ACCEPTED; DP-S5-a → the same DM seat after OQ-1223; DP-S5-b is the USER's
  (exit criterion + spending), raised with the user now", item 1: "PL 9921 as one Work-plan delta
  (relates PL-1237, PL-1537) covering S4+S5 under L5: ACCEPTED. PL-1537 R5.2/R5.3a are stale
  since SL-1455 returned to P2 (21:29:10), and the delta says so with a dated line."
- **Lean P2 L5** (`docs/plans/README.md:16-19`; `.claude/skills/writing-plans/SKILL.md:30-37`):
  one plan per Work, and "a change of slice scope [is] one dated Work-plan delta … a new `PL-`
  that `relates:` the Work's plan".
- **What changed:** the entry "2026-10-10 21:29:10 BST — USER DECISION: R2 = (A). Roadmap §12
  row 2 (P2's exit criterion) STANDS as written" (items 1 and 2), and "2026-10-10 21:38:39 BST —
  DISPATCH GO: SL-1455 (Task 0; FD-1411's NFR-489 HTTP remedy) and WK-674 S3 (PL-1583);
  OP-1455-M1/M2/M3; the register :293 record" (items 2 to 7), and the user's DP-S5-b decision
  recorded at "2026-10-11 10:57:16 BST" (D0.3).

## Goal

Bring the `SL-1258` and `SL-1259` rows of `PL-1537` up to date with three changes since
2026-10-08: SL-1455 is back in P2, "per replica" is ruled in P2, and S4 and S5 are on P2's exit
path. Each row can then be GO'd from `PL-1537` plus this file. The Work's goal is `PL-1237`'s, unchanged.

**Dated line, 2026-10-11, on `PL-1537` (frozen; not edited):** `PL-1537` R5.2 ("`SL-1455` is
carried to Phase 3; Slice 5 no longer follows it") and R5.3a ("NFR-489 is recorded under both
'per replica' readings … names the interpretation as carried: owner WK-1178, event P3's first
plan") are **stale since 2026-10-10 21:29:10 BST**. They are replaced by D5.1 and D5.2 below.
`PL-1537`'s Global Constraints bullet "Priority on every on-day" is replaced for S4 and S5 by
D0.1. Every other line of `PL-1537` for S4 and S5 stands.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the named
tree.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` each exit 0 at the
   branch head. The one exception is check 31's line naming this file's working id 9921, which
   clears at the mint.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids. Every id is listed individually in the Tasks table.
3. **Each slice's ledger quotes both rows.** For each of `SL-1258` and `SL-1259`, one `LG-` under
   `docs/ledgers/` quotes the `PL-1537` row and this file's changes for that slice (D0.x, plus
   D4.x or D5.x), and cites this delta by its minted id. `git grep -l '<minted id>' -- docs/ledgers`
   prints one file per slice by the Work's close.
4. **Slice 4:** `PL-1537` Acceptance item 4 holds, unchanged. In addition, the `LG-` quotes, at
   its base, the function or key format that S3's limiter uses for the scoring counter. It shows
   that the management-API counter uses a different key and a different limit (D4.1):
   `uv run pytest -q backend/tests -k management_rate_limit` exits 0 and collects at least 2
   tests, and the `LG-` quotes each test's red line.
5. **Slice 5:** `PL-1537` Acceptance item 5 holds as changed by D5.1 to D5.5. For every
   measurement run, the `LG-` records the tree, the load at start, the issued and offered rate,
   the error count, the replica and worker count, the topology, and the host (`nproc`,
   `free -g`, and the machine type from the metadata server or the console).
   `git grep -nE 'NFR-489|NFR-490|NFR-493|NFR-494|NFR-501|NFR-502' -- <the LG>` prints a line for
   each id. The NFR-489 line names the ruling that DP-S5-a gave and the DP-3 reading it used.
6. **The gate is green on each slice's merge tree**: the `CLAUDE.md` §11 commands, both halves,
   each exit 0, named against `origin/main...<slice branch>`.

## Global Constraints

`PL-1237`'s and `PL-1537`'s Global Constraints apply, except where D0.1 below replaces one.

- **D0.1 — S4 and S5 are on P2's exit path.** This replaces, for S4 and S5, `PL-1537`'s "Priority
  on every on-day" bullet ("WK-674 S4–S6 are 'the rest'"). 21:29:10 item 1: "WK-674 S3 → S4 → S5
  (WF-701 A–D needs S5's switchover; Phase B optional with S6, still cut-ladder rung 5) stay P2
  scope, serial behind each day's G2-chain slice". S6 keeps `PL-1537` R6.3 (rung 5).
- **D0.2 — a measurement runs ALONE.** `RL-1263` item 3 (which names WK-674 S5) is read in the
  form of 21:38:39 item 5: "The sweep runs ALONE: both slots, no gate, no SL-1526 proving run, no
  migrate --verify". The lead books the window in `eta`, and the `LG-` carries its start and end
  stamps. S5's window and SL-1455's Task 4 sweep are never the same window.
- **D0.3 — the verdict runs go on a temporary dedicated VM.** The user ruled DP-S5-b in the
  maintainer's entry "2026-10-11 10:57:16 BST — USER DECISION, DP-S5-b: "Temporary dedicated VM"
  for the ALONE NFR measurements. Exact type and cost to the user by Thu 15 Oct BEFORE any VM is
  created": "a short-lived second VM used ONLY for the solo speed tests (SL-1455's sweep; WK-674
  S5's measured verdicts), then deleted". Item 1 of that entry: "This is the fallback's own
  discharge event … The measurement on it can be a real pass or fail." Item 3: "WK-674 S5's
  verdicts run there, and the local ALONE windows become rehearsals." No slice waits for the VM
  to **build**. The VM is created only after the user approves the spend (item 2).

## Tasks

The columns follow L5 (a). Each row is `PL-1537`'s, as changed below. The lead assigns the lane at GO.

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | `SL-1258` — Slice 4: the deployment path | `PL-1537` row 1 (with R4.1 to R4.3), plus D4.1 to D4.3 | `07` §3.6: FR-434, FR-435, FR-437; `07` §3.2: FR-412 (memory half), FR-415 (worker service); `07` §3.9: FR-452 (management-API limb); `07` §9: NFR-531, NFR-534; register FD-1211 | `SL-1257` closed (and so S3's limiter on main) | 1 |
| 2 | `SL-1259` — Slice 5: switchover, rollback and the measurements | `PL-1537` row 2 (with R5.1, R5.3 to R5.10), plus D5.1 to D5.5 | `03` §3.10: FR-268, FR-269, FR-272 (rollback audit limb); `03` §9: NFR-489, NFR-490, NFR-493 (linearity limb), NFR-494, NFR-497 (mechanism), NFR-498 (rollback limb), NFR-501, NFR-502; register F-W9-1, F38, F41, FD-1411 (measurement half), F35 (measurement half) | `SL-1258` closed; `SL-1256` (closed, met); DP-S5-a resolved | 1 + an ALONE window |

The requirement set is `PL-1537`'s, unchanged. No id is added or removed.

### Slice 4 (`SL-1258`) — changes since `PL-1537`

- **D4.1 — R4.1 is re-derived against S3's merged limiter, at S4's base.** `PL-1537` R4.1 says S4
  reuses "Slice 3's counter mechanism under a separate key and limit, per Environment and
  Principal". S3's leaf plan (`PL-1583`, line 44) fixes the scoring counter: FR-452's scoring
  limb, as `RL-1347` amended it, counts "`POST /api/v1/score` … in a shared Redis counter, one per
  (Environment, Principal) per fixed one-second window". That code is not on main at this tree
  (`SL-1257` is `draft`, and its branch `sl-1257-wk674-s3-env` @`ae6d9fda` holds gate-1). At GO,
  the executor quotes S3's key function at the slice base. If that function cannot take a second
  key without a change to the scoring limb's behaviour, the executor **stops and reports**. That
  case is a spec-versus-code question, and it is the decision-maker's. Red cases stand as R4.1 wrote
  them: a management route past its limit answers `429` with `Retry-After`, and `/score` is not
  refused when the management limit is exhausted. Each is seen red by its cause.
- **D4.2 — the harness records what OP-1455-M1 makes a condition.** The harness of `PL-1237`
  Task 4 ("drives `/score` at 200 rps against n ∈ {2, 4, 8} replicas") keeps R4.3, the recorded
  topology. It also prints, per run, the **issued** and **offered** rate and the error count.
  21:38:39 item 2 states NFR-489's condition as "issued = offered, 0 errors". A run whose issued
  rate falls short of its offered rate is void, never a reading.
- **D4.3 — the shared paths at this tree.** S3 serialises with SL-1455 "on score.py, deps.py,
  auth/service.py and main.py's lifespan" (21:38:39 item 6). S4's R4.1 edits the limiter that S3
  builds under `backend/src/app/`, so it can meet the same files. At GO, the executor runs
  `git diff --name-only origin/main...origin/<SL-1455 branch>` and the same for each branch in
  flight. It names every shared path in its `LG-`, and the later PR rebases onto the earlier.
  This file names no order between S4 and SL-1455 Tasks 1 to 3. That order is the lead's.

### Slice 5 (`SL-1259`) — changes since `PL-1537`

- **D5.1 — replaces R5.2: SL-1455 is in P2, and it builds FD-1411's remedy.** 21:29:10 item 2:
  "NFR-489 (the /score HTTP path) stays in P2's exit: FD-1411 (HIGH, owner SL-1455) needs its
  remedy built and MEASURED (a pass at the HTTP path, not the model_call step) before the exit
  demo." Slice 5 does not build that remedy. Slice 5's NFR-489 limb is governed by **DP-S5-a**.
  Register `:293`'s dated line is D10's, per 21:38:39 item 7, and it is not this plan's write.
- **D5.2 — replaces R5.3a: "per replica" is ruled in P2.** 21:38:39 item 3: "OP-1455-M2: YES.
  DP-3 ('per replica') is ruled in P2 from Task 0's record, because 'meeting NFR-489' cannot be
  judged without it. 8 Oct DP B (c)'s P3 parking is superseded for DP-3 only". Slice 5 measures
  under the reading that ruling gives (`PL-1454` DP-3: (a) one process, or (b) N `uvicorn`
  workers, N stated). If that ruling is not minted at S5's GO, S5 records both readings, as R5.3a
  said, and names the ruling as pending, never as carried to P3.
- **D5.3 — the host (DP-S5-b, ruled).** S5's code is built and gated on this VM. Its
  measurement runs are made in two places. First, a **rehearsal** in a local ALONE window
  (D0.2), recorded as diagnostic. Second, the **verdict runs** on the temporary dedicated VM
  (D0.3), which give a real pass or fail for the F1 test, NFR-489 (both limbs, F38 included),
  NFR-502, NFR-493's linearity limb and NFR-494. NFR-490 keeps `PL-1237` Task 5's form (FAIL
  with figures if red). The `LG-` names the host of every run (Acceptance item 5), and it
  carries the record that the host was provided, as 10:57:16 item 1 asks. The dated line at
  `docs/roadmap.md:569-570` is the lead's. **If the VM is not approved or not available** when
  S5 is otherwise ready, the fallback form of `PL-1237` Acceptance item 6 applies unchanged
  ("measured, diagnostic on the shared VM; the verdict is carried, owner the maintainer,
  discharge event a dedicated host available"), and the lead reports the miss to the user.
- **D5.4 — R5.4 is not met at this tree.** NFR-502's row (`docs/specs/03-rating-engine.md:1479`,
  read in full at `99f22479`) does not name `/score/compare`. R5.4's own rule then applies: S5
  measures `/score` only, unless the re-check at S5's base finds the extension.
- **D5.5 — R5.6 is still open.** `SL-1367` (`PL-1364`) has no GO at this tree (the maintainer's
  entry "2026-10-11 10:46:55 BST", gap 1). S5's window and `PL-1364` Task 5's window are booked
  apart, as R5.6 says.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S5-a | Who carries the exit-tree NFR-489 reading: Slice 5 on Slice 4's replicated path, or SL-1455's Task 4 sweep? SL-1455 measures "on one replica" (`PL-1454:58`). Its harness serves "one replica", a single `uvicorn` process (`scripts/bench-rating.py:866-867`, `_serve`). Only Slice 4's path has n replicas behind a load balancer. | (a) S5 carries it on the S4 path, and SL-1455's sweep is the remedy's proof only. (b) SL-1455's sweep carries it, and S5 cites it. (c) Both are recorded: SL-1455's sweep is the per-replica reading under DP-3 as ruled, S5's n ∈ {2, 4, 8} run on the S4 path is the deployment-path reading under the same protocol (D4.2), and the closure record sets them side by side. | **(c).** NFR-489 is stated "per replica", and the exit row says "meeting NFR-489" (21:29:10). The per-replica figure is SL-1455's to give, and only S5 can show that it holds on the path that ships. (c) adds one arm pair to a window S5 books anyway (D0.2). If the two readings disagree, the decision-maker rules. Neither is picked silently. | scope / measurement | **yes, for S5 only** | open: the decision-maker seat named in the maintainer's entry "2026-10-11 10:55:55 BST", item 2 ("then DP-S5-a") |
| DP-S5-b | Can §12 row 2 ("meeting NFR-489") be met from the shared VM? If not, which host? | Put to the user by the maintainer (10:55:55 item 3): a temporary dedicated VM for the ALONE windows only; a temporary resize; or carry | none from this plan: an exit-criterion and spending question | exit criterion / spending | no, for S5's build | **ruled**: the user, "Temporary dedicated VM" (the maintainer's entry 2026-10-11 10:57:16 BST). The spend for the exact type is approved separately, by Thu 15 Oct (D0.3, D5.3) |

This plan stays `draft` while DP-S5-a is open (`document-ids.md` §1.7).

## Hand-off (not this plan's writes)

- The lead lists this delta's minted id on WK-674's roadmap row (L5). The dated lines on the
  `SL-1258` and `SL-1259` rows that point at it are the planner's at the mint batch, and they
  change no status.
- Register `:293` (FD-1411) and the `SL-1455` row's dated lines are D10's (21:38:39 item 7).
- DP-S5-a's ruling is the decision-maker's (an `RL-`). When it is minted, the activation line
  sets this plan `active` and cites that `RL-`.

## Self-review

- **Spec coverage.** The Tasks table lists every id in `PL-1537` rows 1 and 2, individually:
  FR-268, FR-269, FR-272, FR-412, FR-415, FR-434, FR-435, FR-437, FR-452, NFR-489, NFR-490,
  NFR-493, NFR-494, NFR-497, NFR-498, NFR-501, NFR-502, NFR-531 and NFR-534, plus the register
  rows FD-1211, F-W9-1, F38, F41, FD-1411 and F35. Nothing is added or dropped.
- **Placeholders.** None. Each change cites its source, by entry header for channel rulings and
  by path and line at `99f22479` for files. "`<SL-1455 branch>`" in D4.3 is a value read at GO,
  because no SL-1455 branch exists on `origin` at this tree.
- **Consistency.** D5.1 and D5.2 replace R5.2 and R5.3a only. R5.1 (F35 carried) and R5.3 (NFR-489
  untraced, `OQ-1453`, `03:1466`) stand. D0.3 and D5.3 restate `PL-1237`'s fallback without
  changing it.
- **Rulings since the sweep.** `to-lead.md` was read to the 2026-10-11 10:57:16 BST entry. Re-read at the
  mint, and add any ruling on WK-674 S4 or S5 as a dated line.
