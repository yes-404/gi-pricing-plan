---
id: LG-8424
family: ledger
title: P2 exit demo run r1 (ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-11
owner: lead
tree: c0216baccf241364ec40beeabbfdc50e49edcd10   # the tree of 374a22bf33ad3c62a4d2c8b69ba83bd334d4b167, the frozen code tree the demo ran
phase: P2
work: WK-1178
plans: [PL-1544, PL-1912]
corrected_by: []
relates: [CR-2110, LG-2107, PL-1544, PL-1912, SL-1913, FD-8428]
---

# LG-8424 — P2 exit demo, run r1 (Wed 11 Nov 2026)

*Disclosure: working id LG 8424, given by lead 33 (`from-lead` 2026-11-11 11:00:21 GMT); unminted on this branch. Written by the auditor (aud-p2close, Claude Opus 5.5), 2026-11-11, on the maintainer's entry `to-lead` 2026-11-11 10:58:58 GMT item (2)(b), from the run's own logs. Every reading below is quoted from a log, with its locator; every stamp is the log's own. The run was lead 33's (`from-lead` 2026-11-11 10:36:58 to 10:58:38 GMT). This is the run record for `CR-2110` G2; it is not a slice ledger, and no slice is named.*

**Authority.** The user named the hour: "I would like to start the demo now, plz help me to arrange it" (`to-lead` 2026-11-11 10:36:21 GMT). The runbook of record is `handover/exit-demo-runbook-wed-18-nov.md`, FINAL at sha256 `c5b260a10792` (`CR-2110` G2 (e)). The rehearsal of record is `LG-2107`.

**Sources** (all under `~/gi-pricing-plan.local/scratch/exit-demo-2026-11-11/`, sha256 prefixes read 2026-11-11): `demo-row.sh` `67fb8e513b09`; `r1/start.log` `34da40ac49cd` (= `r1.out`, byte-equal); `r1/stop.log` `dc0be5b980a9`; `r1/demo.log` `857b5f6a65a1` (3625 lines); `r1/restore.log` `6043cf21033a`; `r1/infra-before.txt`, `r1/infra-after.txt`. `demo-row.sh` against `scratch/exec-sl1913/demo-row.sh`: a `diff` after mapping the names prints only the header comment, the scratch path, the DB name and the bucket name (names only, as lead 33's line of 10:36:58 GMT says).

## Tasks

### Scope

`CR-2110` G2: "`WF-699` end to end on the freMTPL2 seed with its deploy step to `uat` then `prod`, from one command to a served page; approval by a principal neither submitter nor author; D7 decomposes into at least two groups", run on the frozen code tree as the runbook FINAL's OPEN 2 rules: "the demo runs the frozen code tree 374a22bf33ad (tree c0216baccf24) with the stack from tools-main". The user drives (OPEN 3).

### Task list

**Head.** `r1/start.log:1`: `head=374a22bf33ad3c62a4d2c8b69ba83bd334d4b167`.

**START rows** (`r1/start.log`, verbatim):

| Line | Row |
|---|---|
| 2 | `\| template guard START \| alembic_version=1 environments=3 tenant_marker=1 \|` |
| 3 | `\| redis db0 dbsize \| 56 \|` |
| 4 | `\| redis db3 dbsize \| 0 \|` |
| 5 | `\| tools-main deploy diff \| quiet-rc0 \|` |
| 6 | `\| createdb gipricing_exitdemo_r1 \| 1 \|` |
| 7 | `\| alembic upgrade on copy \| rc=0 \|` |
| 8 | `\| alembic_version on copy \| b7e4c2a91d36 \|` |
| 9 | `\| quiet window \| waited 0s load1=1.26 \|` |
| 10 | `\| demo start \| 2026-11-11T10:37:03+00:00 1.26 0.99 0.49 \|` |
| 11 | `\| demo env db \| GIP_REDIS_URL=redis://localhost:6379/3 \|` |
| 12 | `\| demo \| designed stop reached (both lines seen) 2026-11-11T10:50:59+00:00 \|` |
| 13 | `\| demo seconds \| 836 \|` |
| 14 | `\| dislocation #1 \| 288 s (552/558 earlier; today 555/592/623/697) \|` |
| 15 | `\| demo end \| 2026-11-11T10:50:59+00:00 1.33 1.62 1.28 \|` |

**Seed.** `demo.log:20` "33.2 MB CSV, 678,013 rows"; `:23` "ingest: v1, 678,013 rows, 14 columns profiled, 2.1s". Full seed, no `--rows`.

**Journey step lines** (`r1/demo.log`, in the order printed, verbatim after the step tag):

| Line | Step | Printed |
|---|---|---|
| 140 | A1 | ok 7 tables, one per rateable Factor of the approved GLM |
| 141 | A2 | ok |
| 162 | A3 | ok wf699-region: both diffs non-empty, a weight per changed cell |
| 165 | A4 | ok wf699-area: +2 % as a recorded operation |
| 168 | A5 | ok a duplicate key is refused |
| 169 | A6 | KNOWN GAP A6: FD-1491 |
| 174 | B6 | ok a dangling input cannot be saved |
| 179 | B9 | KNOWN GAP B9: FD-1490 |
| 184 | B4 | ok model_call on peril_structure:fremtpl2-ad@1: exact, 8 features mapped; the structure is approved with a passing reconciliation |
| 192 | B3 | ok reference_table:wf699-region-loading@1: a pinned lookup as at the effective date |
| 195 | B7 | ok sub_graph:ncd-ladder@1 saved over HTTP and mounted by exact pin |
| 200 | B1 | ok fremtpl2-rate@2 forked from @1 |
| 201 | B2 | ok 9 inputs declared: types, ranges, domains, nullability |
| 202 | B5 | ok 14 table steps, 4 expression steps, the model_call, the lookup and the outputs |
| 203 | B8 | ok one payable output step, rounding half_even at 0 dp: rounded exactly once |
| 248 | C1 | ok the version pins the algorithm, every table, both models and the ladder |
| 285 | C2 | ok 202 and a rating.compile Job, which the worker ran |
| 286 | C4 | ok PIN_NOT_APPROVED: the GBM is not approved |
| 373 | C5 | transparency artifact built in 21 s |
| 392 | C5 | ok the GBM approved through the workflow, then recompiled |
| 395 | C3 | ok every pin, reference and type resolved at once: the compile passed |
| 396 | C6 | ok sha256:d269916cdac56da8eb0e49c2d7f8f16a3d353189c26709b45f86543025fc5f5c |
| 429 | D1 | ok the suite, with the D4 property, ran against the first version |
| 430 | D2 | ok 3 of 3 golden quotes moved |
| 445 | D3 | ok new suite version; the run passes |
| 499 | D4 | ok premium-increasing-in-bonus-malus failed between 95 and 131 (spacing 45) |
| 529 | D5 | ok the same property passes |
| 532 | E1 | ok drafted from the structural and rate diffs, then edited |
| 535 | E2 | ok POST /rating-versions/{id}/submit, the route RL-1524 names |
| 536 | E3 | ok EVIDENCE_INCOMPLETE: no Dislocation Run for this version yet |
| 3405 | D6 | ok a 20,000-policy sample of the freMTPL2 book (full-book cost: PL-1574) |
| 3408 | D7 | ok 19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units (full-book attribution cost: FD-1576) |
| 3409 | D8 | ok dislocation run 01a1ca3b-691a-7f85-b5c3-3340057b2f7d, attribution cited by id |
| 3410 | D9 | SKIPPED D9: GIPP check; Phase 4; WK-685 |
| 3413 | E4 | ok dislocation run, resubmitted |
| 3416 | E5 | SKIPPED E5 inline review: Phase 3; WK-678 |
| 3421 | E6 | ok changes requested; the version is back in draft (FR-355) |
| 3424 | E7 | SKIPPED E7 Commentary Block: Phase 3; WK-680 |
| 3433 | E8 | ok the submitter and the author are refused; two approvers approve |
| 3436 | E9 | ok approved, evidence pinned |
| 3453 | DEP | ok dev, uat, then prod through a decided Deployment Request (FR-429) |
| 3462 | S1 | ok prod scored 87296 minor units from the live version |

Then `:3463` "journey done in 766s"; `:3471` "served page: http://localhost:5173/ answered 200"; `:3476` "Seeded to a usable state in 834s from the start of this command  (NFR-529's budget is < 5 min; this run is not a timing measurement)." The non-ok lines are the ruled ones only, the same set as `LG-2107` row 5: A6 and B9 KNOWN GAP (FD-1491, FD-1490), D9, E5 and E7 SKIPPED.

**Times.** Demo start 10:37:03 GMT; journey done 766 s; the designed stop ("both lines seen") at 10:50:59 GMT, 836 s from the start (`start.log:12-13`); dislocation #1 288 s (`start.log:14`, against 539 s at `LG-2107` row 5). 834 s to a usable state is about 2.8 times NFR-529's 300 s budget; the demo prints that it is not a timing measurement, and none is claimed here.

**B3.** `:192` B3 ok. No tie line is printed: `grep -n -iE '\btie|tie-?break|tied' r1/demo.log` gives 0 step lines, so the tie rule was not invoked (lead 33: "B3 ok (no tie)", `from-lead` 10:51:35 GMT).

**The four job-handler tracebacks are the scripted negatives.** Counted with `grep -c 'Traceback (most recent call last)'` and each read to its last exception line:

| Traceback at | Worker line | Exception |
|---|---|---|
| `demo.log:218` | `[2026-11-11 10:38:12,669: ERROR/ForkPoolWorker-2] job handler failed` | `:244` `PlatformError: PIN_NOT_APPROVED` |
| `:256` | `[2026-11-11 10:38:13,656: ERROR/ForkPoolWorker-2] job handler failed` | `:282` `PlatformError: PIN_NOT_APPROVED` |
| `:410` | `[2026-11-11 10:38:37,819: ERROR/ForkPoolWorker-2] job handler failed` | `:422` `PlatformError: GOLDEN_QUOTE_MISMATCH` |
| `:482` | `[2026-11-11 10:38:45,720: ERROR/ForkPoolWorker-2] job handler failed` | `:494` `PlatformError: GOLDEN_QUOTE_MISMATCH` |

4 = 2 PIN_NOT_APPROVED (C4's refusal, before the GBM's approval) + 2 GOLDEN_QUOTE_MISMATCH (D2's moved golden quotes). The same count read the same way over `scratch/exec-sl1913/r5/demo.log` (`LG-2107` row 5) gives the same four: `:228`, `:264` PIN_NOT_APPROVED; `:462`, `:546` GOLDEN_QUOTE_MISMATCH.

**Version.** Rating version `01a1ca30-4e79-7a19-b358-dd302e5e6053` (its compile `POST` at `demo.log:508`, 202; its regression run `POST` at `:516`, 202) approved: lead 33 read it from the copy DB ("Version 01a1ca30-4e79-7a19-b358-dd302e5e6053 approved (copy DB read)", `from-lead` 2026-11-11 10:51:35 GMT). The copy is dropped; that read is not re-derivable from the logs.

**Ports**, as lead 33 logged them (`from-lead` 2026-11-11 10:51:35 GMT, verbatim): "Ports curl rc 0 http 200: 5173 / and /demo, 8000 healthz/readyz, 8080 realm." The stack came up from tools-main (`from-lead` 10:36:58 GMT: "stack four healthy from tools-main, keycloak bind under tools-main, redis -n 0 dbsize 56").

**The user's page walk** (10:51 to 10:58 GMT, the demo serving; the maintainer's entry 10:58:14 GMT: "the user drove every page over forwarded ports and signed in as analyst (the password's first live test: passed)"). The client lines the walk printed, for the record, none on a journey step: `demo.log:3500` and `:3521` "[Unhandled rejection] ProblemError: Development identity is enabled; supply x-dev-principal-id." (2; the same message `LG-2107` row 6 records on every load); `:3540` "10:54:13 AM [vite] (client) [Unhandled rejection] TypeError: Cannot read properties of null (reading '0')" in `echarts/lib/coord/View.js` (a graph view), after `:3539` "[ECharts] Can't get DOM width or height" (1). Not diagnosed here. Filed as FD 8428 ([`FD-8428`](../findings/FD-08428-the-dataset-lineage-graph-raises-an-unhandled-echarts-typeerror-on-the-dataset-detail-view-not-diagnosed.md)): LOW, deferred with an owner, WK-1914 (lead 33, 2026-11-11).

**The user's acceptance of the demo**, verbatim (the maintainer's entry `to-lead` 2026-11-11 10:58:14 GMT): "yes I go through all the page and it looks good, I am happy to accept the demo".

**Cleanup END** (the cleanup word, `to-lead` 10:58:14 GMT (1); `r1/stop.log`, verbatim; the file carries no clock stamp of its own, and lead 33 logged it at `from-lead` 2026-11-11 10:58:38 GMT):

| Line | Row |
|---|---|
| 1 | `\| SIGINT to group 10022 \| rc=0 \|` |
| 2 | `\| pgrep uvicorn\|vite \|  \|` |
| 3 | `\| infra inspect diff \| rc=0 \|` |
| 4 | `\| restore from tools-main \| rc=0 \|` |
| 5 | `\| keycloak bind \| /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy/keycloak-local  \|` |
| 6 | `\| dropdb gipricing_exitdemo_r1 \| rc=0 \|` |
| 7 | `OK` |
| 8 | `\| bucket gip-blobs-exitdemo-r1 removed \| rc=0 \|` |
| 9 | `\| redis db3 dbsize \| 0 \|` |
| 10 | `\| redis db0 dbsize \| 56 \|` |
| 11 | `\| pg_database rows named gipricing_exitdemo_r1 \| 0 \|` |
| 12 | `\| template guard END \| alembic_version=1 environments=3 tenant_marker=1 \|` |

Template guard END equals START; db 0 = 56 before and after; db 3 = 0; `infra-before.txt` and `infra-after.txt` name the same four container ids and start times.

### Gate

Not a slice: no gate ran for this record. The code tree is the freeze gate's tree of record, `374a22bf33ad`, gate rc 0 (`CR-2110` §Freeze gates).

### Audit

*Read by the auditor (aud-p2close, Claude Opus 5.5), 2026-11-11, against the files named under Sources; a proposal, the lead's to adopt.* Every row above is read from its log. **Form note** (as `LG-2107` N1, waived there for that slice): `start.log` opens with `head=` but does not end with `rc=`; `stop.log` carries neither and no clock stamp; `demo.log` carries `head=` only in its sibling `start.log`. No result is affected. **Not verifiable from the logs:** the version's `approved` status (the copy DB is dropped; lead 33's read is quoted); the port readings (quoted from lead 33's line); the user's page walk beyond the client lines quoted.

### Build log

- 2026-11-11 (auditor, aud-p2close): this ledger created from `docs/_templates/LG.md` and the form of `LG-2107`, on branch `docs/p2-close-batch34-2026-11-11` from `78671a70d194`.

## PRs

(Added when the P2-close batch's PR opens.)
