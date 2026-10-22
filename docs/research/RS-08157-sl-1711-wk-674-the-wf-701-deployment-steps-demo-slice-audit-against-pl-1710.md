---
id: RS-8157
family: research
kind: audit
title: SL-1711 (WK-674, the scripted WF-701 deployment-steps demo) slice audit against PL-1710, at f279e7cc
status: draft
created: 2026-10-22
owner: auditor
tree: f279e7ccc0186020e2bd4c50919be2996cee7880
phase: P2
work: WK-674
corrected_by: []
relates: [SL-1711, PL-1710, WF-701, FD-1576, OQ-1789, RL-1712]
---

# RS-8157 — SL-1711 slice audit

*(Working id 8157, reserved by the lead. Written by `aud-1711`, 2026-10-22 13:16 BST, from the brief `brief-aud-1711-2026-10-22.md` (lead 26, 13:13:31 BST). Check 31 on this id is expected until the mint. The ledger is cited as `LG 1841`, its minted id on the branch; the lead's brief calls it LG 8136, its working id.)*

## Question

Does `origin/main...sl-1711-wk674-wf701-demo` meet PL-1710's SL-1711 acceptance standard, what does `LG 1841` fail to evidence, and is a 9 to 12 minute `dislocation.run` at the demo's volumes a product performance finding?

## Method

Range `origin/main` (`f3462d8fc1336dc4583fe8a7af92fed399993a55`)`...sl-1711-wk674-wf701-demo` (`f279e7ccc0186020e2bd4c50919be2996cee7880`, tree `11b06958f26f9c64f1b0733f2fee4c65d24f5606`), 10 files, +2224 −58 (`git diff --stat origin/main...origin/sl-1711-wk674-wf701-demo`); `f3462d8f` is an ancestor of the head (`git merge-base --is-ancestor`, rc 0). Scope was read first from PL-1710's "SL-1711 — acceptance standard" (items 1 to 8), Task T7 and reds R1 to R9 (read from `origin/main:docs/plans/PL-01710-…md`), then each item was matched to evidence in `LG 1841` and on disk. Read-only: no test, DB, docker or gate was run by this seat. The branch was read only through `git show/diff origin/…`; the sl-1711 worktree and tools-main were not touched.

Ledger SHAs: of the 11 commit SHAs `LG 1841` cites that resolve, 10 exit 0 under `git merge-base --is-ancestor <sha> origin/sl-1711-wk674-wf701-demo`; the eleventh, `51f1c261`, is the tools-main incident commit (deviation 9 below), cited as an incident, not as evidence, and is not on the branch by design. The other 8-hex strings in the ledger are trees or container config hashes, not commits.

**The gate of record at `f279e7cc` is OWED:** it runs in the sl-1711 worktree from about 14:30 BST and had not ended when this record was written. Nothing below is a gate verdict.

## Scope against evidence (PL-1710 acceptance standard)

| # | Item | Evidence found | Proposed verdict |
|---|---|---|---|
| 1 | `test_wf701_journey.py` docstring + `req` markers; pytest exits 0; R1, R2, R3, R4, R6, R8 quoted in the LG | Journey runs 6 and 7′ green in process (41 passed; 36 passed in both orders), `LG 1841` lines under "Journey DB runs 6 and 7" and "C7(i) scoped…". R1 quoted (ModuleNotFoundError at collection, ledger T1-T4 row). R8/R9 quoted ("6 failed" against the pre-change demo.py). **R2, R3, R4, R6 are not quoted by name or failure line anywhere in the LG** (grep of the LG for `R2`/`R3`/`R4`/`R6`: only the R6 band mention in the T1-T4 row). The marker list was not re-read by this seat. | delivered, partly untested-in-record: R2, R3, R4, R6 red lines owed to the LG; markers owed to the gate |
| 2 | Every in-scope step walked in order; only the two ruled lines; no `KNOWN GAP C7-errors` | Compose log (`scratch/sl1711-compose-wf701.log`) shows A1 to A6, C1 to C4, C6, C7(i) to (iv) in order, `C7-errors: refused, not traced (FR-259, RL-1712)` present, no `KNOWN GAP C7-errors`. The two `KNOWN GAP A6: FD-1491` / `B9: FD-1490` lines are WF-699 part steps (before the `WF-699 part done` line), not WF-701 steps. The `COMPOSE-ONLY A2/C4/C6 replica limb` line is the in-process mode's and is asserted by the test (run 6). | delivered |
| 3 | Refusals match on `code`: C2 `EVIDENCE_INCOMPLETE` and `PROMOTION_ORDER_VIOLATION`; C3(ii) `DEPLOY_REQUIRES_APPROVAL`; FR-238 extra `VALIDATION_FAILED`; C3(iii) review after one of two approvals; `PRECONDITION dev:` | All printed in the compose log in that form (`C2(prod)`, `C2(route)`, `C3(ii)`, `FR-238`, `C3(iii)`, `PRECONDITION dev:`). | delivered |
| 4 | Compose: `--journey wf-701 --target compose` rc 0, per-step lines, A2/C4 (i)(ii)(iii) set of 2, C6 about 50 quotes, C7 inside [3, 45] with N, p, band and exactly M declined traces; **R5, R7, R9 quoted**; alone, elapsed against 10 min | rc 0 (`scratch/sl1711-compose-wf701.rc` = `rc=0`). Lines: A2 "13 responses; 2 replicas committed", C4 "2 replicas committed; 0.5 s (< 30 s functional bound, not the NFR-494 verdict)", C6 "50 prod quotes", C7(i) "12 traces of N = 2000 quotes at p = 0.01; band [3, 45] (outside it: 8.030e-07)", C7(iii) "exactly 20 of 20 declined quotes". `WF-701 part done in 1165s: OVER the pre-registered 10 min target (recorded, not tuned)`; `journey done in 2500s` (= 1335 + 1165); `compose run done in 2573s`. Alone: the `demo` slot, no gate, end guards re-read. **R5 on the stack and R7 (decline floor removed in a scratch copy) are not quoted in the LG**: line 53 still says they are "owed to the compose window", and the compose section does not discharge them. R9 is quoted only as the in-process test red (6 failed → 24 passed), not on a stack with services down. | rc 0 and the per-step lines delivered; elapsed target MISSED, recorded; **R5, R7 (and R9 on a live stack) not started in the record** |
| 5 | NFR verdicts not this slice's; rehearsal quotes S5's `LG-` NFR-494 and NFR-489 lines by tree; "< 30 s … not the NFR verdict" | The C4 line carries the "functional bound, not the NFR-494 verdict" wording. The rehearsal quote of S5's `LG-1824` NFR-494 and NFR-489 lines by tree (PL-1710 T7) **is absent** from `LG 1841` (`grep -n 'NFR-494\|NFR-489' ` on the LG returns no line). | deferred with an owner: the executor (a quote with a tree) — not started |
| 6 | The rehearsal checklist (`PL-1544`'s form), run once in full on the slice head, by command and tree | No checklist record in the LG. The compose SOLO run ran at `4b958a94`, not at the head `f279e7cc` (`git diff --stat 4b958a94 f279e7cc` touches the INDEX, the ledger and a 2-line comment re-point in `journey_wf701.py`, no executable line). | not started as a checklist; the run exists |
| 7 | Gate green on the merge tree, both halves, named against `origin/main...<branch>` | **OWED** (gate of record at `f279e7cc` has not ended). The ledger has no gate rc table. | not started in the record; owed to the gate |
| 8 | Write set inside the plan's list | The 10 files: `backend/tests/test_demo_command.py`, `backend/tests/test_wf701_journey.py`, `examples/fremtpl2/journey_wf701.py`, the two new `examples/fremtpl2/rating/fremtpl2-wf701.*.json`, `scripts/demo.py`, the LG, and three the plan does not list as the build's: `docs/INDEX.md`, `docs/roadmap.md` (SL-1711 row `draft → active` plus the activation line) and `docs/workflows/WF-00701-deploy-and-monitor.md` (two dated lines). The WF-701 lines are the maintainer's (by delegation) 11:14:40 ruling items (1) and (2) (PL-1710 line 533 names this file and "nothing else in that file"); the roadmap/INDEX lines are the L1 status change. No S5 file, no contract, no spec, and not `journey.py` (`git diff --stat` shows it absent). `docs/workflows/` is a workflow, not a spec (CLAUDE.md §4). | delivered |

## The questions the brief asks

### (i) The demo.py `COMPOSE_FILE` fix (H2: `abcc70d2` tests → `4b958a94` fix)

- **Red/green.** `abcc70d2` (+52 lines in `test_demo_command.py`) adds three tests: unset `COMPOSE_FILE` keeps `-f deploy/docker-compose.yml` (a regression pin, green before and after); set `COMPOSE_FILE` yields no `-f` (the red); `demo_env()` keeps `COMPOSE_FILE` (green before and after). `LG 1841` quotes the red "by name": `1 failed, 28 passed`, rc 1, 0 errors, 0 skipped; green `29 passed, 1 warning`, rc 0, on a per-worktree DB, dropped. One red out of three is the expected shape, since the other two pin behaviour that must not change. The test commit precedes the fix (10:15:51Z, 10:16:42Z). Not re-run by this seat.
- **Correct for every compose call `demo.py` makes?** `compose_command` is used by `compose_running` (`ps --status running`), `api_hosts` (`ps -q api`) and the relay's `run --rm -d worker-default … beat`. All three now read the file list from `COMPOSE_FILE` when it is set; with it unset all three keep `-f deploy/docker-compose.yml`. The local-mode infrastructure `up` and the build do **not** go through `compose_command` (they hard-code `-f deploy/docker-compose.yml`, `demo()`), so they are unchanged. An empty `COMPOSE_FILE` is treated as unset (`os.environ.get` falsy), which matches docker's own reading. `-p` (`GIP_COMPOSE_PROJECT`) and `--profile app` are unchanged. One limit: a relative path inside `COMPOSE_FILE` resolves against the subprocess cwd (`ROOT`, passed as `cwd=ROOT` on all three calls), so it holds; the compose run used absolute paths. The `GIP_BUILD` amendment (the relay resolves `image: gi-pricing-app:${GIP_BUILD:-unset}` from the env) is a run-time env, not a code change, and is disclosed (deviation 6). Verdict proposal: correct for all three call sites; broken-input proof exists for the one that mattered (the relay), none is claimed for `ps`/`ps -q`, which share the function.
- The relay watcher (`scratch/sl1711-relay-watch.log`, 493 lines, 0 `KILL` lines; last poll `12:03:53+00:00` shows `GIP_DATABASE_URL=postgres:5432/gipricing_sl1711_compose`, redis db 13, bucket `gip-blobs-sl1711-compose`) is the live evidence that the fix reached the relay's environment.

### (ii) The compose SOLO pass against acceptance 4 / T7

rc 0; the demo's own closing lines are `WF-699 part done in 1335s`, `WF-701 part done in 1165s: OVER the pre-registered 10 min target (recorded, not tuned)`, `journey done in 2500s`, `compose run done in 2573s`, read from `scratch/sl1711-compose-wf701.log`. The 600 s figure is a **MISS recorded, not a failure**, exactly as PL-1710 T7 ("a miss is recorded, not tuned away") and acceptance 4 ("elapsed recorded against ≤ 10 min") read; the maintainer's 12:06:24 BST entry ruled the same. **The target was always unreachable at this volume:** two of the four `dislocation.run` spans (517.1 s and 542.3 s, 1059.4 s together, from `scratch/sl1711-compose-jobs.txt`) fall in the WF-701 part, so dislocation alone is 91 % of its 1165 s and exceeds the whole 600 s by 459 s. That the 10 min figure was pre-registered without that fact is a plan observation (below), not a slice defect.

Jobs file check: 76 job rows by kind (3 + 12 + 2 + 3 + 1 + 1 + 1 + 1 + 6 + 2 + 5 + 2 + 33 + 4 = 76), `sl1711-compose-jobs.err` empty. The four `dislocation.run` rows give 549.4 s, 718.2 s, 517.1 s, 542.3 s, total 2327.0 s (the LG says 2326.9 s: rounding, not a discrepancy). Together with 2573 s that is 90.4 %.

### (iii) Is a 9 to 12 minute `dislocation.run` a product performance finding?

**Proposal: not a new finding. It is `FD-1576`'s finding, measured again; propose a dated evidence line on `FD-1576` (and, if the lead reads the OQ-1789 trigger as fired, one new FD+OQ pair, below).** Reasons, each from a primary source:

1. **No NFR or FR bounds a Dislocation Run.** `git grep -n -i dislocation origin/main -- docs/specs` lines mentioning NFR/budget/seconds/minutes return FR-224 (the approximation gate) and the endpoint rows, and `OQ-1789` states it itself: "no specification states a run-time budget for a Dislocation Run or its attribution". So there is no budget for this to breach, and an FD here would name no NFR.
2. **The cost is known and owned.** `FD-1576` (MEDIUM, owner WK-673, register row `docs/findings/register.md:332`) records that attribution cost scales about 2× per extra change group and is derived at 3.1 to 3.7 h over the full book; its "event that next confirms or discharges it" is "a measured attribution run at that size and K".
3. **The new numbers match the old ones, so no regression.** `OQ-1789` measured on a SOLO local gate (SL-1543 @`5a5cb2e7`) K = 1: about 525 s, K = 2: about 718 s on 19 985 policies. This compose run: first span (K = 1, D6) 549.4 s, second (K = 2, D7) **718.2 s**. Per policy about 28 ms and 36 ms against 26 ms and 36 ms. The two WF-701 spans (517 s, 542 s) are the same K = 1-ish cost again (K1 and K2 each submit a run). The cost is deterministic and compose adds no measurable overhead.
4. **One worker, one synchronous step.** The stack ran one `worker-compute` at concurrency 2 (ledger "Conditions"); a `dislocation.run` is one job and `worker-compute` read 133 % CPU during one, so the second slot does not help. That matches `FD-1576`'s "one synchronous job step" cause.

**What is new, and is a decision, not a finding: the `OQ-1789` revisit trigger.** `OQ-1789` (decided 2026-10-18) says: "if SL-1711, which lengthens the same journey, makes a QUIET journey exceed about 1,400 s at its gate, the cap question reopens BEFORE SL-1711 merges, by an FD plus a new OQ, not a silent cap raise." Read against the tree: (a) the gate template runs `scripts/demo.py --journey wf-699` with a 1500 s cap (`scratch/gate-template-demostop.sh:124,133`), and SL-1711 does not change that command, so the gate's journey is not lengthened; (b) the new journey, `--journey wf-701`, runs the WF-699 part and then WF-701, **2500 s on compose** (1335 s + 1165 s), and the WF-699 part alone took 1335 s on compose against 1134 to 1210 s SOLO local in OQ-1789 (compose load is a different topology, not a like-for-like quiet local run). On the literal text the trigger has not fired, because it is tied to "its gate". On the intent (the demo's cost in a quiet window) it arguably has, because the demo now has a 2500 s variant that no gate runs and no cap covers (the ad-hoc `timeout 3600` of the re-run is the only bound). **I do not decide this; it is the lead's and the maintainer's reading.**

**If the lead reads the trigger as fired, the proposal is:** an FD, owner **WK-673** (the attribution engine is S3's, per `FD-1576`'s dated line; WK-674 owns the demo and could be named instead), severity **MEDIUM** (it does not let a wrong number, a mispricing or data loss through; it makes the WF-701 demo unrehearsable inside the 600 s target and a 2500 s run the only variant), **NFR named: none** (none exists; the finding's remedy would be to create one or to change the demo's size), title in the form "The WF-701 demo's two Dislocation Runs make its part 1165 s against a pre-registered 600 s: no budget in any spec", with the numbers above; plus an OQ with the options (a) keep 600 s and shrink the WF-701 part's sample (K1/K2 on fewer policies), (b) replace the 600 s target with a measured one (about 1200 s on compose), (c) wait for `FD-1576`'s remedy. **If not read as fired:** no FD; add one dated measurement line to the `FD-1576` essay with the four spans, the tree `f279e7cc`, and the 718.2 s K = 2 match. Either way the record that carries it is the lead's to adopt.

### (iv) Disclosed deviations in `LG 1841` — all present, none hidden

| Item in the brief | Where in the LG | Cross-check |
|---|---|---|
| TenantMismatch STOP | "Disclosed deviations", try 1 (`app/platform/tenancy.py:69`; shared `gip-blobs` carries tenant `local`) | ruling A (11:10:17) named; nothing written beyond `ensure_bucket`'s lifecycle merge |
| Relay `-f` blocker | "Disclosed deviations" + "Code change that the run proved necessary (H2)" | ruling 11:14:25 named; red/green quoted |
| Run 1 rc 124 and the lost jobs dump | "Disclosed deviations" (rc 124 at about 11:19:50Z; dump lost because the DB was dropped before the 12:06 instruction arrived) | partial record `scratch/sl1711-compose-jobs-lead-snapshot.txt` (7422 bytes, present); re-run under `timeout 3600` pre-approved at 12:13:55 |
| Watcher fix | "Disclosed deviations" (`ps -eo pgid=` padding, `tr -d " "`, restarted about 4 s after start) | watcher log 493 lines, 0 `KILL`, starts at the demo start |
| Relay left running | "Disclosed deviations" (`…worker-default-run-03621ab1587b`, up 28 min, stopped by name) | the end guards report no `-run-` container |
| Absolute `-f` | "Disclosed deviations" (accepted 11:05:58; Dockerfile byte-identical `f3462d8f` vs `3ac2e499`) | not re-verified by this seat |
| `GIP_BUILD` | "Disclosed deviations" (lead's amendment, accepted 11:42:48) | image tag `gi-pricing-app:4b958a94…` in "Image" |
| tools-main incident | "Disclosed deviations" (re-audit seat's commit, HEAD `51f1c261`, restored detached `f3462d8f`; 11:48:11 rule) | `51f1c261` is the one non-ancestor SHA, explained; common brief item 27 is that rule |
| Pre-existing `ruff format` rc 1 | "Disclosed deviations" (`scripts/demo.py`, fails on `origin/main`; CI runs `ruff check .` only) | **not re-run here (no checks).** The `python.yml:199` claim is the ledger's, not verified by this seat |
| `journey_wf701.py` comment re-point | The mint: the file header now reads "LG 1841 deviation 3" (`journey_wf701.py:16`); no "8136" remains in `examples/` or `backend/` on the branch | the Disclosure line at LG line 19 names the mint |

Two things are disclosed **in the ledger body but not in the Disclosed-deviations list**, which makes them findable only by reading all of it: the 4-run DB budget being exceeded to 7 runs (rulings of 22:20:10 and 22:28:30 BST), and run 7's reused DB (an executor-admitted terms-reading error, "Journey DB run 7"). Neither is hidden.

### (v) The mint 8136 → 1841 and every re-point

- Branch: the file is the ledger file (`docs/ledgers/`), front matter id hyphenated, `relates` and `plans` hyphenated, INDEX row present (`docs/INDEX.md:2016`), `f279e7cc` "mint LG 8136 as LG 1841 (id order (a) of the 2026-10-22 11:46:33 BST entry)". Working-id mentions that remain in the ledger are in the two disclosure sentences (LG lines 19 and 21), intended. In `examples/`, `backend/`, `scripts/` there is no `8136` on the branch. The journey comment is re-pointed.
- **Not re-pointed: two cites on `origin/main` itself.** `docs/findings/the FD-1838 essay file (`docs/findings/`):39` ("SL-1711 run 2 (`origin/sl-1711-wk674-wf701-demo` @135c0b89, LG 8136)") and `docs/findings/register.md:409` ("SL-1711 run 2 (LG 8136 @135c0b89)"). Both were minted on `main` (`f3462d8f`, #1358) while LG 8136 was still a working id; the branch's mint commit does not touch them (`git grep -n -E '\b8136\b'` on the branch returns exactly these two plus the two intended disclosure lines). Common brief item 26 says to "re-point every hit" in the whole tree at a mint. After the SL-1711 PR merges, `LG 8136` resolves to nothing in `docs/INDEX.md`. Whether to edit an FD essay body and a register row for this is the lead's call (a frozen record's body is not edited; a register row is a living document); I propose the register row and the essay line be re-pointed to `LG 1841` in the SL-1711 PR, or a dated correcting line be added if the lead holds the essay frozen.
- `LG 1841` front matter `tree: 03c6397f200868f1a0827c197ffbc6de0bf65eda` is the tree of `44c18e11` (the base the build started on, `git rev-parse 44c18e11^{tree}`), not of the head `f279e7cc` (`11b06958…`) or of the earlier merge. It is the authoring tree, stated as such in "Needs census (on main 44c18e11)"; an observation, not a defect.

## Findings

**Blocking items for closing SL-1711 (the audit proposal is NOT-CLEAN at `f279e7cc`, as a closing audit; each is a "not yet evidenced", none is a defect in what exists):**

- **B1 — the gate of record is owed** (acceptance 7); the ledger has no gate rc table and no Audit or build-log section; its header still says `MERGE-ACK: not yet given` and "PRs: (none; the lead opens the PR)". Verdict proposal: **deferred**, owner the executor, discharged by the gate END at `f279e7cc` and the lead's MERGE-ACK.
- **B2 — R2, R3, R4, R6 red lines are not quoted** in the LG (acceptance 1). Verdict proposal: **delivered but untested-in-record**: the journey test exists and passed in runs 6 and 7′, but the red-by-cause line the plan requires "quoted in the LG with its failure line as printed" is absent; owner the executor.
- **B3 — R5 on compose and R7 (decline floor removed in a scratch copy) are not quoted, R9 only in process** (acceptance 4). The compose run itself passed. Verdict proposal: **not started** in the record; owner the executor, in the same compose window if it is not to be a second SOLO run (the lead and the maintainer decide whether a second window is worth it; it would be another 2500 s alone on the box).
- **B4 — T7 / acceptance 5 and 6**: the S5 `LG-1824` NFR-494 and NFR-489 lines by tree, and the `PL-1544`-form rehearsal checklist at the head, are absent. Verdict proposal: **not started** (they are quotations plus a checklist, not new runs).
- **B5 — two stale `LG 8136` cites on `main`** (the FD-1838 essay line 39, `register.md:409`), not re-pointed by the mint (v above). Verdict proposal: **deferred** to the SL-1711 PR or a correcting line; owner the lead.

**Non-blocking observations:** the Task 0 limbs 0.1 (the `require_startable` pass and broken-input red on `test_api_jobs.py`), 0.3 (re-read of the rate-limit default at the run) and 0.5 to 0.7 are marked "owed" in the ledger and no later section discharges them (the DB runs covered `test_wf701_journey.py` and `test_demo_command.py` only; the gate's full pytest will cover the passing half of 0.1 but not its broken-input red) — verdict proposal **deferred with an owner (the executor)** or struck as superseded by the lead; the plan's 600 s target was pre-registered without the 1059 s the two WF-701 dislocation runs cost (planner observation for the next plan delta, not a finding); the commit trailers read `Co-Authored-By: executor (Claude Sonnet 5)` while the commits' author is `Claude Opus 5.5` (author field, not the trailer form the common brief item 7 governs); the seat did not verify `python.yml:199`.

**Broken-input proofs:** (1) the `COMPOSE_FILE` set-case test is red at `abcc70d2` by name (ledger), the strongest one in the slice; (2) R1, R8, R9 red by cause are quoted for the in-process side; (3) `C7(i)`'s band is non-vacuous (the compose line prints "outside it: 8.030e-07" and the ledger records the run-7 DID-NOT-RAISE at rate 0 as the red); (4) `traces_not_in` scoping is shown red/green by a standalone `python -I` check (ledger).

## Verdict proposals (the lead's to adopt, amend or reject)

| Item | Proposal |
|---|---|
| Acceptance 2, 3, 8 | delivered |
| Acceptance 1 | delivered, red lines for R2/R3/R4/R6 owed to the LG |
| Acceptance 4 | rc 0 and per-step lines delivered; 600 s target missed and recorded; R5, R7 not started |
| Acceptance 5, 6 | not started (quotation and checklist) |
| Acceptance 7 | deferred: the gate of record is owed |
| `COMPOSE_FILE` fix | correct for all three compose call sites |
| `dislocation.run` 9 to 12 min | not a new finding; `FD-1576`'s; dated measurement line proposed; FD+OQ pair only if the lead reads the `OQ-1789` trigger as fired |
| Disclosures | complete |
| Mint 8136 → 1841 | one gap: two `main` cites not re-pointed |

## Next step

Nothing closes on this record. The lead adopts, amends or rejects the verdict proposals; the executor discharges B1 to B5; this auditor re-audits the specific items that change (B2, B3, B4), against the tree the lead names, before the `LG 1841` Audit section and the slice close.
