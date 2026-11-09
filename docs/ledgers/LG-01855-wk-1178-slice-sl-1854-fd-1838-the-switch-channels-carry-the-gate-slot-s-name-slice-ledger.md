---
id: LG-1855
family: ledger
title: WK-1178 slice SL-1854 — FD-1838, the deployment switch's channels carry the gate slot's name (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
slice: SL-1854
plans: []
corrected_by: []
relates: [SL-1854, FD-1838, SL-1711]
---

# LG-1855 — WK-1178 slice SL-1854: FD-1838, the deployment switch's channels carry the gate slot's name

Filed 2026-10-22 under working id 8171 (lead-reserved in eta.md); minted 2026-10-22 as LG-1855 (history lines below that quote "LG 8171" or "SL 8170" name this ledger and its slice by their working ids); executed by `exec-1838`, base `origin/main` `f3462d8fc1336dc4583fe8a7af92fed399993a55`, branch `fix/fd-1838-switch-namespace`.

**GO:** the maintainer's (by delegation) entry "2026-10-22 15:43:10 BST — Maintainer: SPEED MEASURES …" item 2 (`to-lead.md`): FD-1838 prioritised, built red-first, the remedy as reserved at "2026-10-21 21:13:34 BST"; dispatched by lead 26 in the brief `brief-exec-1838-2026-10-22.md`.
**MERGE-ACK:** not yet given.

*Correction: merged as #1363, squash 6753c495, 2026-10-22T20:41:15Z (gh); correction 2026-11-05 by aud-sl1854 on the lead's adoption.*

## Tasks

### Scope

`SL-1854` (a Work-plan delta row under WK-1178, Lean P2 L5), quoted: "one helper `switch_stack(environment, tenant_id)` that builds the stack prefix for both of its callers … and appends `basename($GIP_GATE_SLOT)` when the variable is set, through `RedisSwitch`'s existing `stack` argument; a process with no slot (production) is unchanged. Red first: a test with a foreign subscriber on the unsuffixed channel." Requirements covered: none new; FR-268 (the switch) keeps its behaviour. Remedy per FD-1838's "Remedy (not made here)".

### Task list

- [x] **Task 1, red first** (`a83531d0ada360cd92e87fd5a43d3a80668debf4`): `switch_stack` added behaviour-neutral, both callers moved onto it, and `backend/tests/test_deployment_switch_slot_namespace.py` (three tests).
- [x] **Task 2, the fix** (`b95c9d3d5ca070d396096c944e9544a55ba71dfe`): `switch_stack` appends `basename($GIP_GATE_SLOT)`; `.claude/skills/dev-commands/SKILL.md` gains a 3-line note beside the `GIP_GATE_SLOT` paragraph.
- [x] **Task 3, the gap run** (below).
- Where the switch is built: `backend/src/app/main.py` (`RedisSwitch(switch_client, switch_stack(...))`) and `backend/tests/test_deployment_switch_http.py` (`_Peer`). `scripts/run-small.sh` and the gate scripts already export `GIP_GATE_SLOT` (`scripts/run-small.sh:64`; `.claude/skills/dev-commands/SKILL.md` gate template), so none is changed.

**The gap run (2026-10-22, START 15:18:25 UTC, END 15:19:08 UTC; no gate, no other switch test).** Before each run `PUBSUB NUMSUB gip:switch:local:local:{dev,uat,prod}` = 0/0/0 and `PUBSUB CHANNELS 'gip:switch:*'` empty; after the green run, 0/0/0 and empty. Logs, first line `tree <sha>`: `~/gi-pricing-plan.local/scratch/fix-1838/red.log`, `~/gi-pricing-plan.local/scratch/fix-1838/green.log`.

- RED, `run-small.sh` on `backend/tests/test_deployment_switch_slot_namespace.py`, throwaway worktree at `a83531d0ada360cd92e87fd5a43d3a80668debf4`, rc=1:
  `FAILED backend/tests/test_deployment_switch_slot_namespace.py::test_two_gate_slots_get_two_stacks`
  `FAILED backend/tests/test_deployment_switch_slot_namespace.py::test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum`
  `E       app.platform.deployment_switch.SwitchIncompleteError: 1 of 2 subscribed processes acknowledged PREPARE; possibly stale (unacknowledged; a ghost of a crashed process may be among them): []`
  `2 failed, 1 passed, 2 warnings in 3.35s`
- GREEN, `run-small.sh` on `backend/tests/test_deployment_switch_slot_namespace.py` and `backend/tests/test_deployment_switch.py`, tree `b95c9d3d5ca070d396096c944e9544a55ba71dfe`, rc=0:
  `15 passed, 2 warnings in 0.26s` (0 failed, 0 skipped; the warnings are `GIP_TEST_DATABASE_URL is not set` and a Starlette deprecation).
- Throwaway worktree removed; `docker inspect` of the postgres, redis, minio and keycloak containers showed 0 mounts under it.
- Not run: `test_deploy_switch_runtime.py`, `test_deploy_stack_runtime.py` and the WF-701 journey (DB-backed); the slice gate's full suite is the decisive green.

**Static, at `b95c9d3d5ca070d396096c944e9544a55ba71dfe`:** `ruff check` on the 4 changed files rc 0; `ruff check .` rc 0; `ruff format --check` on the 4 changed files rc 0; `mypy` rc 0 (244 source files); `lint-imports` rc 0.

**Deviation (recorded, lead 26, 2026-10-22):** the full-repo `ruff check .`, `mypy` and `lint-imports` ran beside a running code gate, where the brief said changed files only.

### Gate

The gate ran 2026-10-22 from 16:09:23Z to 17:32:38Z on slot `gate-1b`, head `34c427ea3a65dfc38858890e0923f17437f95373` (tree `69a895dce4aca6c3281fce51f27eb19ed1994c0c`), script `~/gi-pricing-plan.local/scratch/fd1838-gate.sh` (a substitution-only copy of `sl1711-gate.sh` plus one `GIP_GATE_SLOT` preflight row); logs `~/gi-pricing-plan.local/scratch/fd1838-gate/`. The gate log, verbatim:

```
START head: 34c427ea3a65dfc38858890e0923f17437f95373 tree: 69a895dce4aca6c3281fce51f27eb19ed1994c0c branch: fix/fd-1838-switch-namespace load(date l1 l5 l15): 2026-10-22T16:09:23+00:00 2.09 2.68 2.78
| redis isolation | pytest db 2, demo db 4 (GIP_REDIS_URL) |
| bucket gip-test-blobs-gate-1b reset (start) | rc=0 |
| bucket gip-blobs-demo-gate-1b reset (start) | rc=0 |
| test bucket | GIP_TEST_BUCKET=gip-test-blobs-gate-1b |
| isolation (gate env) | gate effective broker: redis://localhost:6379/2 blob_bucket: gip-blobs blob_endpoint: http://localhost:9000 |
locks held: gate-1b held, gate-2 NOT-HELD, small-test held
## preflight
| head guard | ok |
| GIP_GATE_SLOT | /tmp/slots/gate-1b (exported) |
| branch | ok |
| clean tree | ok |
| createdb gipricing_fd-1838_gate | rc=0 |
| alembic upgrade | rc=0 |
| alembic heads | 1 head(s) |
| container gi-pricing-keycloak-1 | healthy |
| container gi-pricing-minio-1 | healthy |
| container gi-pricing-postgres-1 | healthy |
| container gi-pricing-redis-1 | healthy |
| pg_isready | rc=0 |
| redis db 2 FLUSHDB (start) | rc=0 |
| redis db 4 FLUSHDB (start) | rc=0 |
| redis dbsize after start flush | RT db 2=0 RD db 4=0 |
## python half
| ruff | rc=0 |
| mypy | rc=0 |
| import_linter | rc=0 |
| audit_docs | rc=1 |
| req_coverage | rc=0 |
| contracts | rc=0 |
| pytest | rc=1 |
pytest summary: 13 failed, 6646 passed, 19 skipped, 135 warnings in 3090.46s (0:51:30)
## frontend half
| pnpm install --frozen-lockfile | rc=0 |
| pnpm generate:api | rc=0 |
| pnpm lint | rc=0 |
| pnpm type-check | rc=0 |
| pnpm test --maxWorkers=2 | rc=0 |
| pnpm build | rc=0 |
tree after gate: 0 changed path(s)
## demo (wf-699, with the frontend)
| demo lock wait start | 2026-10-22T17:04:13+00:00 |
| demo lock acquired | 2026-10-22T17:04:13+00:00 |
| quiet window | load1 < 2.0 after 300 s |
NOTICE:  database "gipricing_fd-1838_demo" does not exist, skipping
| createdb demo | rc=0 |
| compose + bind mounts | = origin/main |
| demo redis db 4 purge (start) | rc=0 |
| isolation (demo worker env) | demo effective broker: redis://localhost:6379/4 blob_bucket: gip-blobs-demo-gate-1b blob_endpoint: http://localhost:9000 |
| demo alembic | rc=0 |
| demo start load1 | 1.97 at 2026-10-22T17:09:15+00:00 |
| demo | designed stop at 2026-10-22T17:31:52+00:00 (both lines seen) |
| demo.py --journey wf-699 | rc=0 |
| demo seconds | 1363 |
| dislocation #1 | 451 s |
| demo end load1 | 3.62 at 2026-10-22T17:31:58+00:00 |
| D7 | ok  19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units (full-book attribution cost: FD-1576) |
| demo redis db 4 purge (stop) | rc=0 |
| keycloak restore from tools-main (up -d --no-deps --wait keycloak) | rc=0 |
| keycloak bind source | /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy/keycloak-local  (under tools-main) |
| demo lock released | 2026-10-22T17:32:36+00:00 |
| bucket gip-test-blobs-gate-1b removed (end) | rc=0 |
| bucket gip-blobs-demo-gate-1b removed (end) | rc=0 |
| dropdb gipricing_fd-1838_gate (end) | rc=0 |
| dropdb gipricing_fd-1838_demo (end) | rc=0 |
| redis db 2 FLUSHDB (end) | rc=0 |
| redis db 4 FLUSHDB (end) | rc=0 |
| zeros | own-DB count=0 redis RT db 2 dbsize=0 redis RD db 4 dbsize=0 |
END 2026-10-22T17:32:38+00:00 4.15 4.24 4.40 (date l1 l5 l15)
```

Pytest: `13 failed, 6646 passed, 19 skipped`; vitest `Test Files  129 passed (129)`, `Tests  817 passed (817)`. The 13 FAILED lines, by file (a nodeid listed twice in `pytest.log` is counted once):

- `tests/test_audit_docs_finding_citations.py`: `test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`
- `tests/test_audit_docs_ids.py`: `test_the_real_tree_passes_all_ten_checks`, `test_doc_id_check_exits_0_on_the_real_tree`
- `tests/test_audit_docs_process_core_digest.py`: `test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`, `test_the_committed_digest_currently_matches_the_committed_spec`
- `tests/test_audit_docs_w37_11_ceiling.py`: `test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`
- `tests/test_doc_index.py`: `test_an_index_skipping_a_reserved_block_breaks_contiguity`
- `tests/test_register_lint.py`: `test_check_29_is_wired_into_the_docs_gate`, `test_check_29_note_carries_the_residue_line`, `test_phase1b_residue_count_matches_check_29s_own_count`
- `tests/test_register_owed.py`: `test_check_29_wiring_is_undisturbed`
- `tests/test_repository_invariants.py`: `test_money_discipline_is_enforced_by_the_docs_audit`, `test_journey_citations_are_audited_in_ci`

**Reading (lead 26, relaying the maintainer's standing 1(f) of "2026-10-22 18:02:34 BST"):** the frontend and the demo are green and the python failures are exactly the docs-audit set, the gate stands. These tests read `scripts/audit-docs.py` on the real tree, which exits 1 at this head on the unminted working ids (check 31: a gap in the allocation below the then-unminted ids); the 13 re-run on the minted head. The overlap: SL-1260's DB window ran beside this gate by the maintainer's deliberate exception (`to-lead.md` 17:10:35); its TestClients subscribe on the unsuffixed switch channels and this gate's are `gate-1b`-suffixed, and no switch-touching test failed here.

**The 13 re-run on the minted head** `89eea73d6e20fdd5dbf861c3809d9f70854cb489` (2026-10-22, `run-small.sh`, DB-free, three calls of at most 3 files; `audit-docs` at that head: rc 0, "All checks passed."):

- `tests/test_audit_docs_finding_citations.py`, `tests/test_audit_docs_ids.py`, `tests/test_audit_docs_process_core_digest.py`: rc=0, `124 passed in 202.81s (0:03:22)`.
- `tests/test_audit_docs_w37_11_ceiling.py`, `tests/test_doc_index.py`, `tests/test_register_lint.py`: rc=0, `110 passed in 94.71s (0:01:34)`.
- `tests/test_register_owed.py`, `tests/test_repository_invariants.py`: rc=0, `23 passed in 72.76s (0:01:12)`.

All 13 previously failing tests pass; the gate's pytest count is 13 failed, 6646 passed at `34c427ea`, and the full suite is not re-run for a docs-only delta (mint, merges of main).

### Audit

Audit by `aud-sl1854` (auditor, Sonnet 5.5), 2026-11-05T09:35:24Z, on `dae9637ea6f6a56f6502e9db70392cdfb2f3983d` (main), slice merge #1363, squash `6753c4953250fcd601f0309becb4ca142d0f13d2`; PR head `4d2110ba9a63742004f3bb268cf612aa1c65769e` (`refs/pull/1363/head`; `git diff --stat <head> 6753c495` is empty). Verdicts are PROPOSALS (CLAUDE.md §12). No test was re-run: `test_deployment_switch_slot_namespace.py` has two Redis tests (one in 3), so by brief it is cited from the gate record, not run. DB-free predicate for the code reads: `git -C <wt> diff 6753c495^ 6753c495 -- backend .claude` (read whole).

**Scope source.** No plan exists. Criteria are derived, before looking at evidence, from (a) FD-1838 "Remedy (not made here)" (essay lines 60-62), its Disposition (lines 66-68), and (b) the SL-1854 row's "Scope, exactly" (`docs/roadmap.md`, row under `#### SL-1854`) with LG-1855's Scope section (line 28).

| # | Criterion (source) | Verdict | Evidence |
|---|---|---|---|
| C1 | One helper `switch_stack(environment, tenant_id)` builds the stack prefix for both callers (roadmap SL-1854 Scope; LG Scope l.28) | MET | `deployment_switch.py` adds `switch_stack` (+`__all__`); `main.py:132` and `test_deployment_switch_http.py:86` call it; `git grep -n -E "RedisSwitch\(" 6753c495 -- backend packages scripts` finds only those two callers plus the new test; no inline `f"{environment}:{tenant_id}"` left. |
| C2 | It appends `basename($GIP_GATE_SLOT)` when set, through `RedisSwitch`'s existing `stack` argument; no new constructor (roadmap Scope; FD-1838 Remedy l.60-61) | MET | Body: `slot = os.environ.get("GIP_GATE_SLOT")`; `return f"{stack}:{os.path.basename(slot)}" if slot else stack`. `RedisSwitch`/`RedisSwitchTransport` signatures unchanged (diff touches neither class). |
| C3 | A process with no slot (production) is unchanged (roadmap Scope) | MET | Unset or empty slot returns `f"{environment}:{tenant_id}"`, the string the old inline code built. `test_without_a_gate_slot_the_stack_is_unchanged` asserts `== "local:local"` (pure function, `monkeypatch.delenv`). Read to the assert; not re-run (file mixes Redis tests). Gate record: pytest of the whole file passed in the GREEN run (15 passed). MET (code and assert read); run itself MET-BY-RECORD. |
| C4 | Red first: a test with a foreign subscriber on the unsuffixed channel (roadmap Scope; FD-1838 Remedy l.62; Disposition l.66-67) | MET-BY-RECORD | `test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum` subscribes a foreign pubsub to `gip:switch:local:local:dev`, builds the switch with `switch_stack` under `GIP_GATE_SLOT=/tmp/slots/gate-1`, and asserts `outcome.receivers == 1` and `prepared == {"slot-process"}` (asserts read). Needs live Redis, so not run here. RED at `a83531d0`, rc=1, `2 failed, 1 passed`, with `SwitchIncompleteError: 1 of 2 subscribed processes acknowledged PREPARE` (LG l.39-43); GREEN at `b95c9d3d`, rc=0, `15 passed` (LG l.44-45). Both SHAs: `merge-base --is-ancestor <sha> 4d2110ba` exit 0 (the squash commit has no ancestry to them, by construction). |
| C5 | The slot name is set per slot by the gate scripts and `run-small.sh`, not re-implemented (FD-1838 Remedy l.60; roadmap Scope "already export GIP_GATE_SLOT … not changed") | MET | `scripts/run-small.sh:64` at `6753c495`: `env GIP_GATE_SLOT="$slot"`; the slice diff touches no file under `scripts/` (`git diff --name-only 6753c495^ 6753c495 -- scripts` is empty). Gate script row `GIP_GATE_SLOT, /tmp/slots/gate-1b (exported)` is the LG's gate record (MET-BY-RECORD for the gate script itself; script not read here). |
| C6 | The remedy is shown to work under the slot named in a gate: the two paired slots do not share a channel (FD-1838 Evidence l.46-48) | MET | `test_two_gate_slots_get_two_stacks` asserts `gate-1` and `gate-1b` stacks differ and neither equals `local:local` (pure; read). The FD's own "not a reproduction" caveat for gate-1 + gate-1b is closed by this assert plus the gate-1b run being the slice's own. |
| C7 | FR-268 keeps its behaviour; no new requirement (LG Scope l.28) | MET-BY-RECORD | `test_deployment_switch.py` + new file: 15 passed (LG l.44-45); gate pytest `13 failed, 6646 passed`, the 13 being exactly the docs-audit set, re-run green on minted head `89eea73d` (LG l.129-148; 1(f) condition). `git diff` shows no spec file touched; `grep -n "FR-"` over `git diff 6753c495^ 6753c495 -- backend .claude` finds nothing (rc 1). Not re-run here (DB-backed or Redis). |
| C8 | Disposition: FD-1838 discharges on "a merged per-slot namespace with a red-first test against a concurrent subscriber" (FD-1838 l.66-67) | MET (code), OPEN (record) | The merged namespace and red-first test exist (C1-C4). The record is not yet updated: at `dae9637e` FD-1838 still reads `status: active` with Disposition "Open, owner WK-1178", the roadmap SL-1854 row says "MERGE-ACK: not yet given", and LG-1855 says "MERGE-ACK: not yet given" and "merge commit: not yet merged" while #1363 is merged as `6753c495`. These are the lead's/auditor's closing acts after adoption; this audit edits only the LG's Audit section. |

**NFRs.** None are claimed by the scope (no FR/NFR id). No measurement owed.

**Broken-input proof.** The red run (`a83531d0`, `2 failed`) is the deliberately-broken-input proof: the same assertions fail on the pre-fix code and pass on the fix; the LG gives the log paths (`~/gi-pricing-plan.local/scratch/fix-1838/red.log`, `green.log`), which this audit did not open.

**Ledger two-way match.** Every LG commit SHA (`a83531d0`, `b95c9d3d`, `34c427ea`, `89eea73d`) is reachable from PR head `4d2110ba` (`git merge-base --is-ancestor`, exit 0 each). Every changed path of the merge (8 files) is named by the LG scope or build log, or is `docs/INDEX.md`.

**Observations (not criteria).** (1) The gate's overlap note (LG l.140) says the other window's TestClients used the unsuffixed channels; the fix makes that harmless by design (C4). (2) A one-line note in the SKILL.md matches the code (`switch_stack`, `app.platform.deployment_switch`); verified by reading the diff.

**The lead's adoption:** "Lead's adoption, 2026-11-05 (lead 30, from-lead): C1–C7 ADOPTED as proposed (C3 / C4 / C7 MET-BY-RECORD: the slice's tests need live Redis; the gate record and the asserts were read, no re-run). C8 ADOPTED as MET for the code and OPEN for the record: FD-1838 remained `status: active` after #1363 merged (2026-10-22T20:41:15Z, squash 6753c4953250fcd601f0309becb4ca142d0f13d2); its closing act (essay + register row) and the SL-1854 roadmap row's merge line and status ride docs batch 10 (merge 61), not this commit."

### Build log

- 2026-10-22 `a83531d0` red commit; `b95c9d3d` fix commit; pushed to `fix/fd-1838-switch-namespace`.
- 2026-10-22 16:19 BST the gap run above (lead 26's "GAP OPEN 1838").

## PRs

- #1363 — `fix(backend): SL-1854 — FD-1838, the switch channels carry the gate slot's name`, opened 2026-10-22; merge commit: not yet merged.
  *Correction: merged as #1363, squash 6753c495, 2026-10-22T20:41:15Z (gh); correction 2026-11-05 by aud-sl1854 on the lead's adoption.*

*(Dated line, 2026-11-09, docs batch 27, by the executor, on to-lead "2026-11-09 10:00:22 GMT" item (4): this ledger's front matter reads `status: active` at origin/main `40ba57f4b320` while its slice SL-1854 reads `status: closed` in `docs/roadmap.md` there. The slice's code merged as #1363 (`6753c495`, "fix(backend): SL-1854 — FD-1838, the switch channels carry the gate slot's name (#1363)"); its row was set `closed` by #1432 (`2f108b1e`, "docs: docs batch 10 — eleven + one WK-1178 slice closes, the gate and adoption lines, FD-1838 + FD-2001 closing acts, the SL-1736 + SL-1854 audits, process rows (#1432)"). Derived by the predicate: ledger front matter `status: active` and its `slice:` row reading `closed` in `docs/roadmap.md` at `40ba57f4b320`; 13 ledgers, LG-2003 (SL-1736) and LG-1977 (SL-1976) excluded as their slices read `active`. The front matter is flipped to `status: closed` in this batch, per to-lead "2026-11-09 10:28:26 GMT" (LEDGERS), so the record no longer says `active` for a closed slice.)*
