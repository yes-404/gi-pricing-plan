---
id: RS-1847
family: research
kind: audit
title: SL-1711 (WK-674) delta re-audit, f279e7cc to 1cac9494, against RS-1846 B2 to B5
status: draft
created: 2026-10-22
owner: auditor
tree: f6c5510e0d70b8eaa2fa9b3d2fa59cb1bb25365b
phase: P2
work: WK-674
corrected_by: []
relates: [SL-1711, PL-1710, RS-1846, LG-1841, FD-1576, FD-1838]
---

# RS-1847 — SL-1711 fresh narrow delta re-audit

*(Working id 8174, written by `aud-1711r`, 2026-10-22, from the brief `brief-aud-1711r-2026-10-22.md` (lead 26). Check 31 on this id is expected until the mint. The ledger is cited as `LG-1841`, its minted id on the branch.)*

## Question

Does the delta `f279e7cc..1cac9494` on `origin/sl-1711-wk674-wf701-demo` meet the four blocking items B2 to B5 of `RS-1846`, and does it carry anything that is not the R5 fix or evidence? Authority: the maintainer, `to-lead.md` "2026-10-22 16:58:36 BST" (fresh narrow delta re-audit of the R5 fix and the ledger evidence against B2 to B5). Read with "2026-10-22 13:29:19 BST" (items 2 to 4; the row 6 waiver) and "2026-10-22 16:22:33 BST" (the `mc mb` setup accepted).

## Method

Object: `1cac9494b31d7df6cc2eeb9729dfd29a43df8d01`, tree `f6c5510e0d70b8eaa2fa9b3d2fa59cb1bb25365b`. Read by `git show/diff` on `origin/` refs only; no test, DB, docker or gate was run by this seat. The delta contains the merge `d25e7e74` of `origin/main` `71e481fa`, so two ranges were kept apart: the slice's net change is `git diff 71e481fa 1cac9494` (13 files, +2404 −64), and the R5 fix is `git diff f279e7cc be830a88` (5 files, +110 −9). B2 to B5 are quoted from `RS-1846` (`origin/aud-1711-2026-10-22`, `31fc1c83`).

**The branch tip has moved past the object.** `origin/sl-1711-wk674-wf701-demo` is `1406766c`, one commit after `1cac9494` (`git log 1cac9494..origin/sl-1711-wk674-wf701-demo`), `docs(ledgers): LG-1841 — the 13 docs-audit node ids, collected and passing`: +16 lines in the ledger only (`git diff --stat`). It lists the 13 node ids and says `257 = 124 + 110 + 23`. I checked its arithmetic against the logs (below) but the verdicts here are at `1cac9494`; the lead should name which head the ACK request carries.

## B2 — R2, R3, R4, R6 red lines quoted in the LG (acceptance 1)

*RS-1846 B2:* "R2, R3, R4, R6 red lines are not quoted … the red-by-cause line the plan requires 'quoted in the LG with its failure line as printed' is absent."

**MET.** The ledger's section "W1 — in-process reds" (LG-1841 table; lines from `Red | Scratch edit | Log …`) quotes R1, R2a, R2b, R3a, R3b, R3c, R4+R6+R7b and R7a, each with the scratch edit, the log, the result line and the failure line. Checked against the logs in `scratch/sl1711-reds/`:

| Red | Log, first line | Quoted failure line present (`grep -cF`) | Result line in the log |
|---|---|---|---|
| R1 | `r1.log`, `eb8cec5d…` | `ModuleNotFoundError: No module named 'journey_wf701'` (1) | `1 warning, 1 error in 0.34s`, `rc=2` |
| R2a | `r2a.log`, `be830a88…` | `C2(prod): EVIDENCE_INCOMPLETE (HTTP 422)` (5) | `2 failed, 14 passed … in 62.05s`, `rc=1` |
| R2b | `r2b.log` | `C2(route): PROMOTION_ORDER_VIOLATION (HTTP 409)` (5) | `2 failed, 14 passed … in 63.18s`, `rc=1` |
| R3a | `r3a.log` | `C3(ii): DEPLOY_REQUIRES_APPROVAL (HTTP 409)` (5) | `2 failed, 14 passed … in 114.63s`, `rc=1` |
| R3b | `r3b.log` | `FR-238: VALIDATION_FAILED (HTTP 409)` (5) | `2 failed, 14 passed … in 60.70s`, `rc=1` |
| R3c | `r3c.log` | `C3(iii): READ_REVIEW` (5) | `2 failed, 14 passed … in 57.78s`, `rc=1` |
| R7a | `r7a.log` | `C7(iii): DECLINED_TRACES_0_OF_20` (2) | `1 failed, 15 passed … in 329.29s`, `rc=1` |
| R4, R6, R7b | `r4-r6-r7.log` | `A2: BUNDLE_HASH_NEITHER_OLD_NOR_NEW` (1), `C7: TRACE_COUNT_0_OUTSIDE_BAND_3_45` (2), `C7(iii): DECLINED_TRACES_0_OF_20` (2) | `3 failed, 13 passed … in 295.00s`, `rc=1` |
| R8, R9 in process | `r8-r9-pre-t6.log` | line 185 `8 failed, 21 passed, 1 warning in 2.95s` | the ledger explains `8` against the build-time `6` |

Every R2 to R7 log first-lines `be830a88` (the head the ledger names); R1 first-lines `eb8cec5d`, which the ledger names as the parent of `7e5e3e3e`. Two readings I did not verify: the line numbers in the "Assert carrying the cause" column (`journey_wf701.py:778` etc.), and the scratch edits themselves; the logs carry the failures, not the edits. R6 is quoted from a combined run (`r4-r6-r7.log`), not alone; it is separated by its failure line and its `:365` assert, which is acceptable for a red-by-cause.

## B3 — R5 on compose, R7, R9 live (acceptance 4)

*RS-1846 B3:* "R5 on compose and R7 (decline floor removed in a scratch copy) are not quoted, R9 only in process."

**MET.**

1. **R5 fix (`be830a88` and around).** Red-first order holds: `52ef8e5f` (tests) is an ancestor of `0c1a4a1f` (fix). The named line is composed by `scripts/demo.py` `journey_failure_line` (`git show 0c1a4a1f:scripts/demo.py`): `f"the {journey.upper()} journey failed at {failure.step}: {failure.code}{status}"`, then `[{names joined ", "}; +{extra} extra]` when set. `check_commit_set` (`examples/fremtpl2/journey_wf701.py`) now passes `names=tuple(missing)` and `extra=len(extra)`; `JourneyStepFailed` (`examples/fremtpl2/journey.py`) gains `names` and `extra`. With status `None` and extras 0, a ghost replica yields exactly `the WF-701 journey failed at A2: COMMIT_SET_DIFFERS_FROM_THE_REPLICAS [ghostreplica]`. The maintainer's constraint (13:32:12, item 2) holds: only the missing set (client-computed `expected - got`) is printed; the extras are a count; `detail` stays unprinted; the bundle-hash check prints the journey's own `old`/`new`. Its test, `backend/tests/test_wf701_failure_line.py`, asserts `COMMIT_SET_DIFFERS_FROM_THE_REPLICAS`, `host-b`, `host-c`, `+1 extra` **and** `"host-x" not in line` (the extra's text), the bundle-hash twin asserts the hashes present and the stray absent, and a third pins that a failure without names keeps the old line. Clean-checkout logs: `scratch/sl1711-r5fix/red-clean.log` first-lines `52ef8e5f…`, `2 failed, 1 passed … rc=1`; `green-clean.log` first-lines `0c1a4a1f…`, `3 passed … rc=0`. The test file is DB-free as the ruling required.
2. **R5 live.** `r5-compose.log` first-lines `be830a8838ec2cd0938304e95326ea143f0a4ee3`; **line 141** reads `  the WF-701 journey failed at A2: COMMIT_SET_DIFFERS_FROM_THE_REPLICAS [ghostreplica]`; **line 143** is `rc=1`, a recording `echo rc=$?` line, not an inference. `r5-compose.rc` holds only `done` (the ledger says so and does not use it). `WF-699 part done in 1340s` is at line 130. `r5-relay-watch.log` has 0 `KILL` lines (`grep -c KILL`). `r5-compose-jobs.txt` exists. The maintainer read the same lines (16:58:36).
3. **R9 live.** `r9-compose-down.log` first-lines `be830a88…`; its message `The compose stack is not up. Missing: lb, worker-compute, worker-default, worker-io, worker-scoring, api (x2; 0 running). …` and a closing `rc=1` line are in the file.
4. **R7.** Both limbs are quoted: R7a (`DECLINED_TRACES_0_OF_20` with `deploy_k2()` removed, `r7a.log`) and R7b (decline floor deleted, `r4-r6-r7.log`).

Limit: the quoted R5 line proves the *journey-computed* naming on the real stack with a scratch edit of `api_hosts()` (one line, restored; the ledger states it). It does not prove that a genuinely missing replica produces a missing-set (the unit test does).

## B4 — acceptance 5 and 6 (NFR quotes; the PL-1544-form checklist)

*RS-1846 B4:* "the S5 `LG-1824` NFR-494 and NFR-489 lines by tree, and the `PL-1544`-form rehearsal checklist at the head, are absent."

**MET, with row 6 waived by a dated line.**

- **Acceptance 5.** The ledger quotes `LG-1824` lines 249 and 252 whole at `71e481fa`, naming blob `9b7cc583be7ce6fecc8b43d2810c602e07dc0f04`. Verified: `git rev-parse 71e481fa:<path>` and `1cac9494:<path>` both print that blob, and `git show 71e481fa:<path> | sed -n '249p;252p'` begins `- **NFR-489** — deferred with an owner …` and `- **NFR-494** — deferred with an owner …`. The text is a quote, not a verdict, and the journey's C4 line keeps "not the NFR-494 verdict".
- **Acceptance 6.** The ledger's rows 0 to 9 are present. Spot checks: row 5 cites `scratch/sl1711-gate/gate.log:52` (`| demo.py --journey wf-699 | rc=0 |`) and `demo.log` lines 4595, 4603, 4606 (`journey done in 1074s`, `served page: http://localhost:5173/ answered 200`, `Open  http://localhost:5173/demo`); `gate.log` line 1 names head `be830a88…`, tree `3c846b0e…`, matching the ledger. Row 7 cites `pytest.log:10240`: `13 failed, 6643 passed, 13 skipped, 134 warnings in 3648.11s (1:00:48)`. Row 4's four SHAs are ancestors of `origin/main` (`merge-base --is-ancestor`, rc 0 each). Row 6 is **WAIVED** by "2026-10-22 13:29:19 BST" item 2, stated in the ledger with the entry cited; the frontend count `0` still holds on the net change: `git diff 71e481fa 1cac9494 --stat` lists no `frontend/` file.

**Observation, not a defect of this delta:** the gate of record at `be830a88` was **red** on `13 failed` (the docs-audit set, red on the id gap 1838 to 1841). The ledger says this and says the 13 pass at the re-merged head. That is a claim about a different head than the gate's; it rests on the 13 reruns below. The decisive green is the next gate or CI, which the lead's ACK request carries; this delta does not replace it.

## B5 — the stale `LG 8136` cites on main

*RS-1846 B5:* "two stale `LG 8136` cites on `main` (the FD-1838 essay line 39, `register.md:409`), not re-pointed by the mint."

**PARTLY MET: the register row is re-pointed, the essay line is not.**

- `register.md`: the FD-1838 row now reads `SL-1711 run 2 (LG-1841 @135c0b89)` (`git diff 71e481fa 1cac9494 -- docs/findings/register.md`); the other register change is the dated line on the FD-1576 row, `register.md:332`. It is appended in that row's form (`***Dated line, 2026-10-22 (measurement; no re-rating).***`) and carries the four spans 549.4, 718.2, 517.1 and 542.3 s (2326.9 s of 2573 s), the `OQ-1789` comparison and the 13:22:09 ruling (iii), "no new FD". Those four spans and the 76 rows match `RS-1846` and `LG-1841`'s compose section.
- The essay `docs/findings/FD-01838-the-deployment-switch-s-pub-sub-channel-is-not-isolated-per-gate-slot-so-a-concurrent-subscriber-inflates-the-prepare-quorum.md:39` still reads `… @135c0b89, LG 8136): rc 1, 40 passed,` at `1cac9494` and at the branch tip (`git grep -n -E '\b8136\b'`: that line and the two intended disclosure lines, LG lines 19 and 21). The brief names only the register row as a re-point, and the essay is a finding body; I do not know whether the lead holds it frozen. **Residual, for the lead:** either re-point that one citation in the SL-1711 PR or add a correcting dated line; otherwise `LG 8136` resolves to nothing after the merge.
- `LG-1824` :249/:252 quotes match the file at `71e481fa` (B4).

## The brief's checks 3 to 5

**Evidence spot checks (check 2).** `r5-compose.log`, `r9-compose-down.log`, `w2-up-worker-io-exit.log` first-line `be830a88…`; `docs13-final-1/2/3.log` first-line `1cac9494b31d7df6cc2eeb9729dfd29a43df8d01` and end `124 passed in 190.68s`, `110 passed in 95.55s`, `23 passed in 74.04s`, each `rc=0`. The ledger text (at `1cac9494`) quotes `docs13-1/2/3.log` at `d25e7e74`: `124 passed in 191.26s`, `110 passed in 97.00s`, `23 passed in 68.71s`, `rc=0`, exactly as those files read; they first-line `d25e7e74060edfedace9f8485084d4d7225c92d6`, which is the head the ledger names. The `final` logs are at the later head and are cited only by the tip commit. The R5 and R9 `rc=` values are recording lines (above). 124 + 110 + 23 = 257 matches the tip commit's collect count; `docs13-collect.log` first-lines `1cac9494…`. I did not re-run the 13 tests.

**Disclosures (check 3).** Present and accurate: the W2 attempt-1 failure (`Exited (2)` for `gi-pricing-worker-io-1` in `w2-up-worker-io-exit.log:13`, `BucketAlreadyOwnedByYou` in the log's container output) is assigned to **FD-1850**, "a product defect and not SL-1711's", citing 16:22:33; the `mc mb` setup is stated to **mask the race in this run, not to prove it absent**, as the maintainer's entry words it; the other seat's small-test overlap is disclosed with the HELD/free times and the judgement that R5 is a functional red. One small gap: the `up -d --wait` stderr line the ledger quotes (`container gi-pricing-worker-io-1 exited (2)`) is not itself in the cited log, which holds `ps` and container output; the content is supported, the wording is the seat's.

**Scope creep (check 5).** The slice's net change against `71e481fa` is 13 files. Non-evidence, non-R5 code in them is the slice's own build (journey, demo, the two tests and the two rating JSONs), already audited by `RS-1846`; the delta since `f279e7cc` that is the slice's own is `test_wf701_failure_line.py`, `journey.py`, `journey_wf701.py` and `scripts/demo.py` (the R5 fix, authorised by the 13:32:12 ruling, whose item 1 has `JourneyStepFailed` gaining a field) plus the ledger and `register.md`. Everything else in `git diff f279e7cc 1cac9494` (28 files, `git diff --stat f279e7cc 1cac9494 -- . ':!docs/ledgers'`, which lists SL-1275's frontend, backend, model-schema, contract and spec files) is the SL-1275 merge `71e481fa`, not the slice's. No other slice change found. `journey.py` is the shared WF-699 module; the edit adds two defaulted fields and changes no existing call.

## Findings

- None blocking beyond the B5 residual. Open items for the lead, none of them a defect in the evidence: (1) the FD-1838 essay line 39 `LG 8136`; (2) the object (`1cac9494`) is not the branch tip (`1406766c`); the tip adds the 13 node ids and no code; (3) the gate of record is at `be830a88` and was red on the 13 docs-audit tests; the ACK request needs the post-merge gate or CI line (the maintainer lists CI incl. python); (4) `RS-1846` B1 (the gate of record) is outside this narrow delta and was not re-audited; (5) a `cd /tmp` was issued once by this seat in a Bash call by mistake (the shell reset to the original cwd the same call; no git write followed from `/tmp`).

## Verdict proposal (the lead's to adopt, amend or reject)

| Item | Proposal |
|---|---|
| B2 (R2, R3, R4, R6 red lines) | met |
| B3 (R5 on compose, R7, R9 live; R5 fix) | met |
| B4 (acceptance 5 NFR quotes; acceptance 6 checklist, row 6 waived) | met |
| B5 (stale `LG 8136` cites) | register row met; essay line 39 deferred, owner the lead |
| Scope creep | none found |
| Overall | **CLEAN on B2 to B4; B5 CLEAN conditional on the lead's call on the essay line** |

## Next step

Nothing closes on this record. The lead adopts, amends or rejects; the executor handles the B5 residual if the lead so decides. This record is a draft until the docs batch mints it.
