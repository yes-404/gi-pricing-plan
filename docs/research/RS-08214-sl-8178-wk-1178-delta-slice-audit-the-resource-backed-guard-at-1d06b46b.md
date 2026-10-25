---
id: RS-8214
family: research
kind: audit
title: SL-8178 (WK-1178 delta) slice audit, the RESOURCE_BACKED guard at 1d06b46b
status: draft
created: 2026-10-23
owner: auditor
tree: 1d06b46b497bec8fd9c9a052b3f39ca82433ddeb
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-8178, LG-8179, FD-1851, RL-1848]
---

# RS-8214 — SL-8178 slice audit, the RESOURCE_BACKED guard

*(Working id 8214, written by `aud-8178`, 2026-10-23 11:54 BST, from the brief `brief-aud-8178-2026-10-23.md` (lead 27). Check 31/32 on this id and on SL-8178, LG-8179 are expected until the mint. Range audited: `origin/main...1d06b46b` on `fix/fd-8175-resource-backed-guard`; `origin/main` is `ff976406`. No test, database or gate was run by this seat; every run quoted below is the executor's log, read.)*

**Verdict PROPOSED (the lead's to adopt): CLEAN, with B1 and B2 (appended-line corrections to LG-8179) and the red-first reading in section 3 for the lead to take to the maintainer if the strict reading is wanted.** No blocking defect in the code.

## Question

Does the branch deliver what the maintainer's 17:21:38 BST item 2 and RL-1848 item 4 oblige, and is the ledger true to its logs?

## Method

Scope derived from the authority first (below), then evidence read from the code at `1d06b46b`, the executor's logs and the ledger. No test, database or gate run by this seat.

## 1. Scope, from the authority first

- **Authority:** `to-lead.md` "2026-10-22 17:21:38 BST" item 2, verbatim: "The guard "RESOURCE_BACKED may hold only /environments/{env}/ paths": **YES, as a test**, red-first via an injected non-env path. It goes in the FD 8175 close vehicle, a WK-1178 delta row (test-only, small), NOT in SL-1260. If it fails on main today, STOP and report."
- **RL-1848** "What it obliges" item 4 (`docs/rulings/RL-01848-…md`:237-240): "A test asserts that every `RESOURCE_BACKED` key in `backend/tests/test_api_authorisation_sweep.py` names an `/api/v1/environments/{env}/` path. It is shown **red first** on an injected non-Environment path." Owner: FD-1851's close vehicle, a WK-1178 delta row, test-only; the stop condition is the entry's.
- **Expected scope (3 obligations):** (O1) a test over every key of `RESOURCE_BACKED`; (O2) shown red first on an injected non-Environment path; (O3) test-only, a WK-1178 delta row, outside SL-1260; STOP if red on main.

## 2. Evidence, per obligation

**O1 — the assert vs the ruling.** `backend/tests/test_api_authorisation_sweep_scope.py` (48 lines, new): `_outside_the_environment_scope(backed)` returns `sorted(key for key in backed if not key[1].startswith(ENVIRONMENT_PREFIX))`, `ENVIRONMENT_PREFIX = "/api/v1/environments/{env}/"` (trailing slash, so `/api/v1/environments-extra/…` is not accepted). `test_resource_backed_holds_only_environment_scoped_paths` asserts `RESOURCE_BACKED` (imported, not copied: the only project import) is non-empty and `_outside_the_environment_scope(RESOURCE_BACKED) == []`. This is the ruling's predicate, quantified over all keys, on the path element `key[1]`. DELIVERED. The mapping on main holds five entries (deployments, deployment-requests, deployments/rollback, routing, shadow; `backend/tests/test_api_authorisation_sweep.py`:307-325 at `ff976406`, which equals the branch's copy: `git diff --stat ff976406 origin/fix/fd-8175-resource-backed-guard -- backend` is the one new file). All five start with the prefix. The "fails on main today" STOP did not fire: `main-run.log` (first line `71e481fa…`, `2 passed, 2 warnings in 0.19s`, rc=0) at the base, and `rerun-8435ab45-run.log` (first line `8435ab45…`, `2 passed, 2 warnings in 0.34s`, `GIP_REDIS_URL` db 12) at the 5-entry head. Marker `@pytest.mark.req("FR-343")` on both tests; `FR-343` exists (`docs/specs/06-governance.md`:79).

**O3 — vehicle.** Write set `git diff --name-only origin/main...1d06b46b`: the test file, `docs/INDEX.md` (+2 rows SL-8178, LG-8179), `docs/roadmap.md` (+20, the SL-8178 row under WK-1178, `owner: lead`), the LG. Four files, as expected; no `backend/src`, `packages`, contract or spec file. Test-only, WK-1178 delta. DELIVERED.

**Cites resolve.** On the branch, no `FD 8175` / `RL 8176` remains (`git grep -E "\b(FD|RL)[ -]0?(8175|8176)\b"` over the tree except INDEX: only the minted-id records themselves). `FD-1851` resolves (register row `docs/findings/register.md`:412 and the essay `FD-01851-…md`, status `retired` on main = closed-as-accepted); `RL-1848` resolves (`docs/rulings/RL-01848-…md`, active); front matter `relates: [SL-8178, FD-1851, RL-1848]` (LG) and `[FD-1851, LG-8179, RL-1848]` (roadmap row). The test docstrings cite `RL-1848` only.

**LG lines vs logs.** The build-log sha/time claims match the log files read: `main-run.log`/`green-run.log`/`weakened-run.log` first line `71e481fa…`; `rerun-8435ab45-run.log` first line `8435ab45…` and the `0.34s`, `load 3.38` claims; `audit-0935.log` ends `FAILED (1): check 31: gap in the full allocation between 1859 and 8178` (the slice's own ids). The committed head `1d06b46b` is the LG-only commit that adds the `8435ab45` bullet (its own sha cannot be in the bullet; the bullet names the code head `8435ab45`, which is the same code and test tree as `1d06b46b`).

**Closure (GREEN scope, item 29).** `git diff --name-only origin/main...HEAD -- backend/src packages` empty; the one importer of the sweep module is the new file (`git grep -nE "test_api_authorisation_sweep import|import test_api_authorisation_sweep" -- backend packages`: only `…_scope.py:12`). So GREEN = the new file (run, 2 passed). `backend/tests/test_api_authorisation_sweep.py` (main's, DB-backed: `membership`/`database` fixtures) is **not** in this slice's change set and is not run by this slice's small runs; it is **owed to the full gate**, which is the decisive green (LG "Gate" is empty, correctly: not yet granted). Importing it at module level in the new file needs no DB (proved by the two passing DB-free runs).

## 3. The red-first form: two readings, and a proposal

Item 2 says "red-first via an injected non-env path".

- **What was done.** (a) The guard function exists beside an injection test that passes a copy of `RESOURCE_BACKED` plus `/api/v1/datasets/{dataset_id}/versions` and the near-miss `/api/v1/environments-extra/{env}/deployments` and asserts the function returns exactly those two keys (green by design). (b) The proof of "red" is a weakened guard (the `startswith` check replaced by `if False`, scratch, never committed, restored by `cmp`): `weakened-run.log` `1 failed, 1 passed, rc=1`, `assert [] == [('POST', '/a…deployments')]`. So the **injection test** was seen red against a broken guard; the **real-list test** was green in the same run (it passes either way, as the LG itself says).
- **Reading A (strict, literal).** "Red first on an injected non-env path" = the *guard test itself* (the one over `RESOURCE_BACKED`) is run red once with a non-Environment key present in `RESOURCE_BACKED` (a scratch copy of the mapping with an injected key, or a monkeypatch), then green on main's list. Under A the delivered proof is **one step short**: no run ever shows the real-list test failing. It is shown red only by composition (the helper is proven to return violations; the real test asserts `== []` over that helper).
- **Reading B (functional).** The point of red-first is to show the guard *can* fail and is not vacuous. The delivered pair does that: the injection test pins the helper's behaviour on a violating input (including the near-miss prefix), the non-empty assert stops an emptied mapping passing, and the `if False` mutation shows the pair bites. The real-list test is a one-line composition of the proven helper and the real mapping; no logic remains unproven except the import of the right object.
- **Proposal.** Accept B as satisfying item 2's purpose and RL-1848's text ("shown red first on an injected non-Environment path": the injection *is* the path, the red is the weakened-guard run). It is not literally A. If the lead or the maintainer wants A, the cost is one DB-free small run (a scratch edit adding a non-Environment key to a copy of the sweep file's mapping, or `monkeypatch.setitem(RESOURCE_BACKED, …)` in a scratch test, `run-small`, expect `1 failed`, restored by `cmp`), recorded as an appended LG line; no code change to the slice. The lead's call; recorded here so the choice is dated rather than silent.

## 4. Findings

- **B1 — a verbatim quote in the LG was altered by the id re-point.** LG-8179 `**GO:**` line quotes the entry as "…It goes in the FD-1851 close vehicle…" inside quotation marks; the entry (`to-lead.md` "2026-10-22 17:21:38 BST" item 2) reads "FD 8175 close vehicle". The re-point of `FD 8175`→`FD-1851` (build-log bullet 3) reached into a quotation. Fix: an appended line in LG-8179 noting the quote is of the entry as written (`FD 8175` = `FD-1851`), not an edit of the line. Same class, on main and **out of this slice's write set**: `RL-1848` quotes the entry's heading as "RL-1848 ADOPTED" where the heading reads "RL 8176 ADOPTED" (`RL-01848-…md`:24-25). Not this slice's; for the lead to route.
- **B2 — LG Scope paragraph is stale.** "**Owed, not on this branch:** FD-1851's own close … happens in the docs batch" — FD-1851 is `retired` on main (register row :412). A correction by an appended line (the readiness file `readiness-8194-8178-2026-10-23.md` B(g)5 reached the same); the line stays, the append says it is discharged.
- **B3 (note) — the LG's "The 2 warnings are the per-worktree test-database teardown notice" is inexact.** The log (`main-run.log`, `rerun-8435ab45-run.log`) shows two different warnings: a Starlette `httpx` deprecation (`testclient.py:1`) and the `conftest_db.py:437` teardown-notice `UserWarning`. Only the second is the teardown notice. Appended-line correction with B1/B2; no effect on the verdict.
- **B4 (note) — "The three entries … all pass"** (LG build log, first bullet) is the base `71e481fa` count; main now has five (SL-1260 added `routing` and `shadow`), covered by the `8435ab45` run. Not wrong (dated), but a reader of the ledger alone sees "three". Same appended line.
- **Process, not findings:** LG `tree:` is the base `71e481fa…`, and the roadmap row `tree:` likewise (the other LGs on main carry the slice base the same way; not checked further). The row says `owner: lead` while the executor was `exec-8178`; consistent with a lead-owned slice row.

## 5. Four verdicts for the unevidenced

None: every obligation O1-O3 has evidence. The one thing owed is not a requirement without evidence but a gate: the DB-backed `test_api_authorisation_sweep.py` and the full suite are **deferred to the slice gate, owner: the lead's gate grant** (LG "Gate" empty). Verdict for the lead to issue.

## 6. NFRs and broken-input proof

No NFR in scope. Broken-input proof: delivered as the weakened-guard run above (the injection test goes red, rc=1); the near-miss prefix `environments-extra` is in the injected case. Not re-run by this seat (no tests).

## 7. Owed before the PR (the lead's, derived)

1. Re-merge `origin/main` (INDEX conflict expected, take theirs and regenerate) and re-run the guard at that head (`run-small`, redis db 11-13, DBSIZE 0). 2. Full code gate, serial, on the granted slot. 3. This RS folded and minted in the PR (item 34), LG "### Audit" filled from it, B1-B3 appended lines. 4. Mint SL-8178/LG-8179 at their turn (`idsweep.sh`, whole-tree grep for `8178`/`8179` in both forms, INDEX regenerated, `--check` rc 0). 5. PR CI incl. python.
