---
id: PL-1666
family: plan
kind: map
title: WK-674 — Slice 4 (deployment path) at GO readiness: FD-1650's migration round trip, the FR-452 management limb's decision point, and the activation paper — Work-plan delta
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1537, PL-1620, PL-1583, RL-1347, RL-1614, SL-1257, SL-1258, SL-1259, FD-1211]
---

# PL-1666 — WK-674 Slice 4 at GO readiness: Work-plan delta

*(Minted 2026-10-12 as PL-1666 from working id 9865, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

> **For agentic workers:** this is a **Work-plan delta** under Lean P2 L5. It does not replace
> [`PL-1237`](PL-01237-wk-674-deployment-environments-switchover-tenancy-map-plan.md) (the map
> plan), [`PL-1537`](PL-01537-wk-674-slices-4-to-6-work-plan-delta.md) (Slices 4 to 6 as rows) or
> [`PL-1620`](PL-01620-wk-674-slices-4-and-5-after-sl-1455-returned-to-p2-work-plan-delta.md) (S4
> and S5 after SL-1455 returned to P2). It `relates:` all three and changes **Slice 4 only**.
> **Read `PL-1237` Task 4, then `PL-1537` row 1 with R4.1 to R4.3, then `PL-1620` D0.1 to D0.3 and
> D4.1 to D4.3, then this file.** Where they differ, this file is the later statement. Slices 5 and
> 6 are not changed. S4 stays one PR under L1 (a'), and its `LG-` quotes this file's D4.4 to D4.6
> beside the rows it already quotes. REQUIRED SUB-SKILL for the executor: subagent-driven-development
> (recommended) or executing-plans, plus `PL-1620`'s list (`python-test`,
> `test-driven-development`, `dev-commands`, `fastapi-service`, `contract-schema`, `git-hygiene`)
> and `spec-change` for D4.5's spec-first edit. Spawned from `.claude/roles/executor.md`; reads
> [`README.md`](README.md)'s five unchecked conventions.

Filed under working id 9865, reserved by the lead (team-lead to planner-wk674-s4, 2026-10-12, in its reply to
the readiness report). Written 2026-10-12 by the planner (planner-wk674-s4).
Evidence read at `origin/main` `fc4401dc` (#1288) and at the authored S4 branch
`origin/sl-1258-wk674-s4` `a04ff676` (base `d699a561`, #1272).

## Authority

- **FD-1650 into S4:** the maintainer's entry "2026-10-11 20:17:38 BST — Audit verdicts (your
  20:14:10) ACCEPTED, with each retro FD's DISCHARGE PATH named; SL-1503 is UNBLOCKED (WK-675 S3
  and S4 both merged), so it is the gate's G2 work now", item 4: "FD 9704 (SL-1257 migration
  round-trip): fold into WK-674 S4's write set (its next alembic slice) as a red-first round-trip
  test". The finding is FD-1650 (working, D13): on `origin/docs-d13-2026-10-11`, the file under
  `docs/findings/` whose name ends `sl-1257-has-no-committed-migration-round-trip-or-api-keys-unchanged-test.md`
  (its working-id prefix is elided here because it does not resolve before the mint), *Discharge path*: "`upgrade` / `downgrade -1` / `upgrade` on a database holding `api_keys` rows,
  asserting the rows unchanged. Date: merged with SL-1258 and no later than the P2 exit demo".
- **The GO request is owed now:** the maintainer's entry "2026-10-11 11:32:09 BST", item 2: "The
  activation and GO request come to me when PL 9921 is minted (D11), with its needs quoted. No
  gate before that." PL 9921 is `PL-1620`, minted in D11 (#1275, `b1cdefb5`).
- **This delta accepted in form:** the maintainer's entry "2026-10-12 02:53:52 BST", item 4:
  "WK-674 S4: PL 9865 delta with FD 9704's round-trip test, OK." The same item rules DP-S4-2 (ii)
  and routes DP-S4-1 (Decision points).
- **Lean P2 L5** (`docs/plans/README.md:16-19`): a change of slice scope is one dated Work-plan
  delta that `relates:` the Work's plan.

## Goal

Make `SL-1258` GO-able: put FD-1650's test into its write set and Acceptance, state FR-452's
management limb as a decision point instead of a silent pick, record `PL-1537`'s activation, and
keep FD-1661 (the compose `scheduler` gap) out of S4. The Work's goal is `PL-1237`'s, unchanged.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the named
tree.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` exit 0 at the
   branch head, except check 31's lines naming the working ids 9865, 9704 and 9860, which clear at
   their mints.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids.
3. **FD-1650's test (D4.4).** On the S4 merge tree,
   `uv run pytest -q backend/tests -k environment_settings_round_trip` exits 0 and collects at
   least 1 test, and the `LG-` quotes its red line from the deliberately broken input D4.4 names,
   with the cause in the line (an `api_keys` row differs), never a bare migration error.
4. **FR-452's management limb (D4.5).** `PL-1537` Acceptance item 4 holds
   (`uv run pytest -q backend/tests -k management_rate_limit` exits 0, at least 2 tests, red lines
   quoted), **after** DP-S4-1 is ruled, and `git grep -n 'FR-452' -- docs/specs/07-platform.md`
   shows a dated amendment citing that ruling's `RL-` id before the code commit.
5. **FD-1661 is not in S4 (D4.6).** `git diff --name-only origin/main...<S4 branch>` names no
   file under `frontend/`, and `deploy/docker-compose.yml` on the S4 branch adds no `scheduler`
   or `beat` service: `git show <S4 head>:deploy/docker-compose.yml | grep -nE '^  (scheduler|beat):'`
   prints nothing.
6. **The activation paper.** At this delta's mint, `PL-1537`'s front matter reads
   `status: active`, and `git grep -n 'PL-1620' -- docs/roadmap.md` prints a line in each of the
   `SL-1258` and `SL-1259` sections.
7. **The gate is green on the S4 merge tree**, both halves of the `CLAUDE.md` §11 commands, named
   against `origin/main...<S4 branch>` (`PL-1620` Acceptance item 6, unchanged).

## Global Constraints

`PL-1237`'s, `PL-1537`'s and `PL-1620`'s Global Constraints apply unchanged (D0.1: S4 is on P2's
exit path).

- **D0.4 — the S4 branch merges main before any new task.** The authored branch's base `d699a561`
  does not contain `SL-1257`'s squash-merge `fe80aec6` (#1280):
  `git merge-base --is-ancestor fe80aec6 d699a561` exits 1 at this delta's tree. `PL-1620` D4.1
  re-derives against S3's limiter **at the slice base**, so the base is moved first. At
  `fc4401dc`, `git merge-tree --write-tree origin/main origin/sl-1258-wk674-s4` exits 0.
- **D0.5 — the deploy runtime tests run only in the build window.**
  `backend/tests/test_deploy_stack_runtime.py` skips unless `GIP_DEPLOY_TESTS=1` (`:33` on the
  branch), and it builds two images, N and N-1 (`:7`, `:58`). The gate does not set the variable,
  so their evidence exists only from the window the lead books. The `LG-` records that window's
  start and end, the command line, and each test's result.

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | `SL-1258` — Slice 4: the deployment path | `PL-1537` row 1 (R4.1 to R4.3), `PL-1620` D4.1 to D4.3, and D4.4 to D4.6 below | `07` §3.6: FR-434, FR-435, FR-437; `07` §3.2: FR-412 (memory half), FR-415 (worker service); `07` §3.9: FR-452 (management-API limb); `07` §9: NFR-531, NFR-534; register FD-1211; FD-1650 (working, D13) | `SL-1257` closed (met: `fe80aec6`); DP-S4-1 ruled (for Task C only); FD-1650 minted, or cited by working id | 1 + a build window |

The requirement set is `PL-1620`'s, unchanged. FD-1650 is a register row, not a requirement.

### Slice 4 (`SL-1258`) — changes since `PL-1620`

- **D4.4 — FD-1650's migration round trip.** One test in a new
  `backend/tests/test_migration_environment_settings.py`, named
  `test_environment_settings_round_trip_leaves_api_keys_unchanged`, mirroring the neighbouring
  `test_the_migration_round_trips` (`backend/tests/test_migration_deployments.py:348-365` at
  `fc4401dc`: its marker form and its `_alembic(command.…)` helper), never a new fixture
  scheme. The revision is `c5a91e7d3b26`
  (`backend/migrations/versions/c5a91e7d3b26_environment_settings.py:21-22`, `down_revision =
  "b8d2f4a6c0e1"`). It is **not** the head: `d4e81b7a2c95` follows it (`:22-23` of that file), so
  `downgrade -1` from head would reverse the wrong revision. The test pins each step by revision
  id: upgrade to `b8d2f4a6c0e1`; insert `api_keys` rows through the neighbour's own seeding path;
  upgrade to `c5a91e7d3b26`; downgrade to `b8d2f4a6c0e1`; upgrade to `c5a91e7d3b26`. After each
  step, it reads every `api_keys` row (all columns, ordered by primary key) and asserts equality
  with the rows read before the first upgrade. Marker `req("FR-417")` plus the requirement the
  neighbour cites for the revision's own feature. **Red first, by cause** (convention 2): the
  revision is already correct, so the test is seen red against a **scratch** edit of
  `c5a91e7d3b26`'s `upgrade()` that changes one `api_keys` value. The edit is reverted before
  commit. The quoted red line names the differing row. A red line from a migration error or a
  missing table is a fixture defect, not the red. Write set: that test file only (FD-1650 names no
  code change).
- **D4.5 — FR-452's management limb is spec-first, behind DP-S4-1.** `07` §3.9 FR-452 at
  `fc4401dc` (`docs/specs/07-platform.md:183`) defines only the scoring limb. Its amendment of
  2026-10-10 places the management limb in `SL-1258`, but it names no counted route set, no
  Setting and no rule for a Service Account's `rate_limit_rps`. The limiter at `fc4401dc` needs all
  three. `RateLimiter.key` already takes `route` (`backend/src/app/platform/rate_limit.py:77-84`),
  and `enforce` takes `route`, `default_setting` and `account_limit` as parameters (`:112-127`). So
  a second key does not touch the scoring limb, which `PL-1620` D4.1's stop condition asks the
  executor to confirm at the base. Task C does not start until DP-S4-1 is ruled. The ruling is
  then written into `07` §3.9 FR-452 as a dated amendment, and into the §3.8 Settings registry if
  a Setting is added, **in a commit before the code**. That path is in `PL-1537`'s S4 write set
  (`PL-1537:147`, "`docs/specs/07-platform.md` if a contract is clarified"). Tasks A and B1 to B5
  do not wait for DP-S4-1.
- **D4.6 — FD-1661 stays out of S4.** FD-1661 (working, D13, reserved 2026-10-12 02:48:51 BST):
  `deploy/docker-compose.yml` lacks the Celery worker and beat services that `07` FR-432 lists
  (`07:148`: "`api`, `worker`, `scheduler` (the beat tick, FR-413), `frontend`"). The authored S4
  branch adds a `worker` service under the `app` profile
  (`deploy/docker-compose.yml:141-145` at `a04ff676`), and no `scheduler` and no `frontend`.
  FR-432 and FR-413 are not in S4's requirement set, and S4 is not widened (the lead, 2026-10-12).
  So S4 closes FD-1661's worker half only. FD-1661's placement is DP-S4-2, **ruled (ii)** by the
  maintainer's entry "2026-10-12 02:53:52 BST — Readiness rulings: GO S6 SL-1548 (swap
  planner-wk673-c out); FD 9862 LOW, owner WK-677; PL 9864 + PL 9865 deltas OK; FD 9860 (ii)",
  item 4: "FD 9860: (ii) ACCEPTED, beat as its own row after S4, serialised on
  deploy/docker-compose.yml. FR-432 is not met until both land, and the FD stays open until beat
  merges." **For the D13 assembler:** word FD-1661 against the S4 branch, or its "lacks the
  worker" clause goes stale when S4 merges. The FD stays open past S4's merge.
- **Follow-on note — the beat row (not cut here; its `SL-` id is reserved by the lead on the
  planner's request).** What the row needs, from the ruling and this delta's evidence:
  - **Scope:** a `scheduler` service in `deploy/docker-compose.yml` under S4's `app` profile,
    from S4's one image (`deploy/Dockerfile`), running the Celery beat tick FR-413 names.
    Requirements: `07` §3.2 FR-432 (its `scheduler` limb) and FR-413. FD-1661, discharged
    at that row's merge.
  - **Depends on:** `SL-1258` merged (the same compose file, the `app` profile and the
    image). Serialised on `deploy/docker-compose.yml`, so it is never in flight beside an S4 or S5
    edit of that file.
  - **Acceptance shape:** a shape test beside S4's `backend/tests/test_deploy_stack.py`, so that
    the service exists under the `app` profile, runs the beat command and gets one replica. A
    broken-input proof is that test seen red against the compose file without the service. A
    runtime proof behind `GIP_DEPLOY_TESTS=1` shows the tick firing, in a build window, as D0.5 says.
- **FR-432's three unmet limbs (dated 2026-10-12).** The maintainer's entry "2026-10-12 03:08:30
  BST — (1) noted, close after the SIGINT report; (2) the frontend image is FR-432's THIRD limb, so
  FD-1661 lists all three and FR-432 stays open until all land; (3) integers stay accepted; (4)
  HIGH, separate CLI: agreed", item 2: "worker (SL-1258, WK-674 S4); beat (its own row after
  S4); the `frontend` image (a third row). FR-432 and FD-1661 stay open until ALL listed limbs
  merge." So the three limbs of `07` FR-432 (`07:148`) are:
  1. **`worker`**: `SL-1258` (D4.6 above).
  2. **`scheduler` (beat)**: its own row after S4 (the follow-on note above).
  3. **`frontend` image**: **folded into the beat row, in P2**, by DP-S4-3 ruled (b). It is not
     added to S4.
- **The beat-and-frontend row's conditions (DP-S4-3, ruled 2026-10-12).** The maintainer's entry
  "2026-10-12 03:09:50 BST — DP-S4-3: (b) fold the frontend image into the beat row; P2 scope, with
  the cut-ladder move line pre-named". The row's plan carries all three conditions:
  1. **The cut-ladder move is pre-named.** "if the cut ladder takes the lane, the row moves to P3
     by a dated line with an owner (WK-674) and a discharge event. It is never dropped." The
     discharge event is the row's merge, which closes FR-432's last two limbs and FD-1661.
  2. **Tech dependency in the same PR.** "A new frontend Dockerfile brings a base image (node
     build stage plus a static server, e.g. nginx). If that is a new tech dependency for the
     stack, docs/skills-map.md is updated in the SAME PR (CLAUDE.md §10), and 07's
     tech-dependencies section if it names images." At `fc4401dc`, `docs/skills-map.md:142` has a
     "Docker Compose / Helm" row (`deploy/`), and `07` §8 starts at `07:463`. The row's planner
     reads both and states whether the static server is a new dependency.
  3. **Reachable, not declared.** "Test it from a fresh checkout: the image builds and serves the
     built app (a curl 200 on /), recorded in the LG." The `LG-` records the clean checkout's
     commit, the build command and its rc, and the `curl` command with its status line.
  The row's acceptance adds the `frontend` image beside the beat shape test. The image exists
  under the `app` profile, and the broken-input proof is that test seen red against the compose
  file without the service.

### Activation of `PL-1537` (dated 2026-10-12)

`PL-1537` was minted `draft` (D1, #1252, `d471a43b`). Both of its decision points are ruled:
DP-1 **(c)** and DP-2 **(the ladder, rung 5)**, both in the maintainer's entry "2026-10-08 14:32:33
BST — DELTAS AUDIT (handover/audit-deltas-2026-10-08.md) noted; fixes proceed; DP A, B (c), C
confirmed, D AMENDED (build in reverse ladder order)" and the cut-ladder ruling of 2026-10-08
13:21:00 BST (`PL-1537`'s Decision points table, "Resolved by" column). DP-1's carriage to P3 is
replaced by `PL-1620` D5.2 and does not reopen it. No decision point of `PL-1537` is open, so it
goes `active` in this delta's branch, by its status line only. Its body is not edited (the
`PL-1583` precedent: `fe80aec6` changed that plan's status line and nothing else).

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S4-1 | FR-452's management-API limb: (1) which routes are counted; (2) where the limit comes from; (3) does a Service Account's own `rate_limit_rps` apply to them? `07:183` states the scoring limb only. | (1a) every `/api/v1/*` route except the `/score` family and the health probes; (1b) the state-changing routes only (`POST`, `PUT`, `PATCH`, `DELETE`) outside `/score`. (2a) a new Setting, for example `platform.default_management_rate_limit_rps`: unset by default, workspace or Environment scope, resolved by §3.8 as `scoring.default_client_rate_limit_rps` is; (2b) the scoring Setting reused. (3a) no: `rate_limit_rps` stays the scoring limit; (3b) yes: one account limit for both. | **(1a), (2a), (3a).** FR-452 says the scoring limit is "configured separately from management-API limits". Options (2b) and (3b) put both limbs on one source, which reads against that clause. (1a) has no per-method list for the spec to keep in step with routes. With (2a) unset by default, nothing changes for a deployment that sets nothing: the same no-counter-call path as RL-1347 rule 2. The Environment and fail-open rules are the scoring limb's: the key's Environment, empty for a bearer caller; admitted and counted on `gip_rate_limit_unenforced_total` if Redis is down. | spec interpretation | **yes, for Task C only** | the decision-maker (an `RL-`), seated by the lead |
| DP-S4-2 | Where does FD-1661's remaining half go: the `scheduler` (beat) service, and with it the rest of FR-432's service list? | (i) widen S4 with the `scheduler` service. This adds FR-432 and FR-413 to S4's requirement set, so it needs a further delta. (ii) a separate row after S4, serialised on `deploy/docker-compose.yml`, built on S4's `app` profile and Dockerfile. | **(ii).** S4 is on P2's exit path (`PL-1620` D0.1), and the beat tick is not on `WF-701` A to D. A row after S4 reuses the image and profile S4 builds, with no second edit to the same compose file in flight. | scope | no, for S4 | **ruled (ii)**: the maintainer, "2026-10-12 02:53:52 BST", item 4 (D4.6) |
| DP-S4-3 | FR-432's third limb, the `frontend` image (`07:148`; the maintainer, "2026-10-12 03:08:30 BST", item 2): is it P2 scope, and in which row? `frontend/` has no Dockerfile at `fc4401dc`, and the S4 branch adds none. | (a) a third WK-674 row in P2, after the beat row, serialised on `deploy/docker-compose.yml`: one image that builds `frontend/` (`pnpm --dir frontend build`) and serves the static output under the `app` profile. (b) fold the image into the beat row, so one P2 row after S4 closes both remaining limbs with one more edit of the compose file. (c) carry it to P3 by a dated move line, with an owner and a discharge event, leaving FR-432 and FD-1661 open past the P2 close with that carriage recorded in the phase closure record (`CLAUDE.md` §14). | **(b).** The beat and `frontend` limbs share the dependency (S4's `app` profile), the file and the serialisation. One row makes one compose edit instead of two serialised ones, and it lets FR-432 and FD-1661 close together in P2. Neither limb is on `WF-701` A to D (`PL-1620` D0.1), so the row stays off the exit path. If the cut ladder needs the lane, the row is moved to P3 by a dated move line, which is (c) applied later and never a silent drop. | scope | no, for S4 | **ruled (b)**: the maintainer, "2026-10-12 03:09:50 BST", with three conditions (D4.6) |

A plan is "`draft` while decision points are open, `active` on freeze" (`document-ids.md` §1.6,
the PL `map`/`leaf` row). DP-S4-1 blocks Task C, so this delta mints `draft`. It goes `active` by a
dated line once DP-S4-1's `RL-` is minted. DP-S4-2 and DP-S4-3 are ruled, and neither blocks S4. The same entry,
item 4, sends DP-S4-1 to a decision-maker "when a seat frees (medium unless it writes spec text)".
The ruling's content is written into `07` §3.9 by S4's executor (D4.5). Whether that makes the
ruling "write spec text" is the lead's reading.

## Hand-off (not this plan's writes)

- **The lead (L5):** list `PL-1620` (and this delta, once minted) on WK-674's roadmap row. At
  `fc4401dc`, `git grep -n 'PL-1620' -- docs/roadmap.md` prints nothing. The D13 minter writes
  it.
- **The decision-maker:** DP-S4-1, as an `RL-`.
- **The lead:** reserve the beat row's `SL-` id on the planner's request (D4.6's follow-on
  note). That one row carries beat and the `frontend` image (DP-S4-3 (b)). No second `SL-` id is
  needed.
- **The D13 minter:** FD-1650 and FD-1661 are minted with their batch. Once they are minted, this
  file's working-id cites resolve in the mint commit, as `PL-1620`'s did.

## Self-review

- **Spec coverage.** The requirement set is `PL-1620` row 1's, unchanged: FR-412, FR-415,
  FR-434, FR-435, FR-437, FR-452, NFR-531 and NFR-534, plus register FD-1211, with FD-1650 added
  as a register row. No requirement id is added or dropped. FR-432 and FR-413 are named only to
  keep them **out** of S4 (D4.6, DP-S4-2, DP-S4-3). FR-432's three limbs are listed in D4.6.
- **Literals verified at `fc4401dc`** (conventions 1 and 3): the revision ids and `down_revision`
  lines; the neighbour test's name and lines; `RateLimiter.key`'s and `enforce`'s parameters; the
  Setting key `scoring.default_client_rate_limit_rps` (`backend/src/app/platform/settings.py:233`).
  `platform.default_management_rate_limit_rps` is marked as an example name. It is DP-S4-1's to
  fix.
- **Convention 4.** `to-lead.md` was read from `PL-1620`'s last entry (2026-10-11 11:02:35 BST) to
  "2026-10-12 02:47:50 BST", grepping for `SL-1258`, `674 S4`, `PL-1620`, `9921` and `9810`, and
  reading each hit. The two rulings found are the 11:32:09 and 20:17:38 entries above.
  `gh pr list --state open` at 2026-10-12 01:53 UTC: one open PR, #1289 (`SL-1527`), which does not
  rule on S4.
- **Placeholders.** `<S4 branch>` and `<S4 head>` are values read at GO.
