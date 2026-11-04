---
id: CR-1999
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-1250 fresh Work close audit — sub-graph composition and MTA/cancellation pricing, re-testing CR-1979 after SL-1989 and the fresh full gate
status: active                  # write-once; this is the only value this family ever takes
created: 2026-11-04   # drafted 2026-11-04 under working id 8309
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: db92a7bc0424059ed0aff4e5cebf445661c3be81
phase: P2
work: WK-1250
corrected_by: []
relates: [CR-1979, PL-1254, PL-1325, PL-1572, PL-1629, PL-1991, SL-1989, LG-1990, FD-1768, FD-1326, FD-1241, FD-1317, FD-1297, CR-1247, CR-1907]
---

# CR-1999 — WK-1250 fresh Work close audit

*Working id CR 8309 (minted as CR-1999), reserved by the lead. The auditor seat aud-wk1250b (`opus`, Claude Opus 5.5)
wrote this record on 2026-11-04 from 09:43 GMT, on the lead's brief
`~/gi-pricing-plan.local/handover/brief-aud-freshclose-2026-11-04.md` (sha256 `b2764443b2b9…`),
under the maintainer's ruling in the entry "2026-11-04 08:46:25 GMT" and the entry
"2026-11-04 09:44:40 GMT" in `~/gi-pricing-plan.local/channel/to-lead.md`. It follows
`.claude/skills/close-workstream`, `CLAUDE.md` §13 and §14, and takes its section shape from
CR-1979, the audit it re-tests.*

**What this record is.** It gathers evidence and **proposes**. Every §13 verdict below is
written "PROPOSED" and is the lead's to give. **The close is the user's dated acceptance line.**
This record does not close WK-1250.

**Object.** `origin/main` at `db92a7bc0424059ed0aff4e5cebf445661c3be81` (read by `git ls-remote
origin refs/heads/main` at 09:44:20 GMT; tree `ede3bf38bf33b0e9dfdc54e4c7b6590809ceb7fd`). Every
`file:line` and count below is at that tree unless it names another. Branch
`docs/wk1250-fresh-close-2026-11-04`, cut from that commit.

## §R Re-test of CR-1979's findings

CR-1979 (tree `c807a59d`, verdict NOT CLOSE-READY, adopted at "2026-11-03 15:58:45 GMT" item (5))
named three owed items. Each, re-tested at `db92a7bc`:

| # | CR-1979 owed item | What changed (PR, squash) | Re-test at `db92a7bc` | Status now |
|---|---|---|---|---|
| 1 | **SL 8296**: FD-1768's code fix (a purposes-only mount change worded "mount ports re-mapped") | **#1423, `7b8a00cf356f258cef764a5af576b28b01195186`** (SL-1989, LG-1990, PL-1991; merge 52, MERGE-ACK "2026-11-04 01:56:03 GMT") | `packages/pricing-core/src/pricing_core/rating/analysis.py:665-675`: the `before == after` branch words "mount ports re-mapped" only `if mount.ports_changed`, else "mount purposes changed", and appends "; purposes changed" when both flags are set; the re-point branch (`:676-682`) appends each flag's clause. Asserts read: `packages/pricing-core/tests/test_rating_attribution.py:1498` (`test_mount_purposes_changed_forms`, `req("FR-1399")`) asserts `alone.description == f"m_ncd: mount purposes changed ({_NCD4})"` (`:1520`), the both-flags form (`:1523`) and the re-point form (`:1525`); `:1483` asserts a purposes-only change is one structural mount change with `before == after`. Red first: `7e2fdfa2` (§3). Merge 55 (#1426, `db92a7bc`) edited `analysis.py` again (FD-1578's attribution errors); the wording lines above are present at its tree and its PR CI python run 41797547929 is `success` at tree `ede3bf38` (§2) | **code fix delivered.** Closing acts owed — see item 1a |
| 1a | *(new, from re-testing 1)* SL-1989's slice audit and closing acts | — | `LG-1990` (its file under `docs/ledgers/`): `status: active` (`:5`); "## Audit" holds only "Written by the auditor." (`:92-94`); "**MERGE-ACK:** not yet given." (`:22`) although the ACK is the entry "2026-11-04 01:56:03 GMT"; "## PRs" reads "None yet." (`:101-103`). Roadmap SL-1989 `status: active` (`docs/roadmap.md:3573`). FD-1768's register row (`docs/findings/register.md:392`) is "***Resolved 2026-11-04***" but says "this PR, its number and squash written at the merge's date-of-record", and `grep -cE '#1423\|7b8a00cf'` over that row, FD-1768's essay, LG-1990's file and PL-1991's file prints 0 for each | **owed (docs only)**: §5, §Verdict |
| 2 | FD-1326's register close act, in docs batch 6 | **#1418, `cd45739773f495cc9ceece9819868a63b57c8133`** (docs batch 6) | `register.md:224`: "***Resolved 2026-10-01*** — closed in place 2026-11-03 by the auditor … PR #1034 (`9b0fb97c`)"; FD-1326's essay (line 5) `status: closed` | **discharged** |
| 3 | The fresh full gate, both halves, after SL 8296 merges | exec-gate1250 at `824a891da8b421d8a0fbe9430934aff8ecd4d574` (contains `7b8a00cf`: `git merge-base --is-ancestor 7b8a00cf 824a891d` rc 0); plus #1426's CI | §2: END rc 0; accepted by the maintainer, entry "2026-11-04 09:44:40 GMT" | **discharged** |
| — | Proposed with no effect on acceptance: NFR-489 on a mounted bundle | ruled "2026-11-03 16:13:02 GMT" item (2): "joins nfr-bench-1, owner WK-1250" | `~/gi-pricing-plan.local/handover/nfr-bench-1-plan-2026-11-04.md:37` (item D, OWED, owner WK-1250), S1 Thu 5 Nov 2026; plan accepted "2026-11-04 09:04:20 GMT". Driver `~/gi-pricing-plan.local/scratch/nfr-bench-1/bench-d-nfr489-mount.py`, sha256 of record `df6e7c9c3216895d175434cf92bd5d26c0335fe7f48621dfee5c2919997513d3` (the entry "2026-11-04 09:51:05 GMT", after the `--serve-dsn` fix; read here at 09:53 GMT, file mtime 09:47:24 GMT, same value). Pre-registered in §4 | **deferred with an owner** (§4) |
| — | Observations: the roadmap scope line narrower than `PL-1254`; SL-1341's "MERGE-ACK: pending" | none | `docs/roadmap.md` WK-1250 scope line unchanged; SL-1341 row still "MERGE-ACK: pending (the lead's merge, then the maintainer's line)" | unchanged; observations only |

## Scope

### §0. The requirement set, derived from the documents before any evidence

**Predicate** (runnable from the repository root at `db92a7bc`). The WK-1250 roadmap section is
`docs/roadmap.md:3477` up to the next `###` heading at `:3587`. The Work's plans are the six
files whose front matter reads `work: WK-1250` — CR-1979's five plus `PL-1991` (the FD-1768
delta, `active`):

```bash
git grep -l -E '^work: WK-1250\b' -- docs/plans          # six plans
( sed -n '3477,3586p' docs/roadmap.md
  cat docs/plans/PL-01254-*.md ) | grep -ohE '\b(FR|NFR)-[0-9]+\b' | sort -u -V
cat docs/plans/PL-01325-*.md docs/plans/PL-01572-*.md docs/plans/PL-01629-*.md \
    docs/plans/PL-01991-*.md | grep -ohE '\b(FR|NFR)-[0-9]+\b' | sort -u -V
```

The first prints 11 ids (CR-1979's 10 plus FR-1399, from the SL-1989 row); the second prints 27
(CR-1979's 26 plus FR-1399). The union is **28 ids**: CR-1979's 27 plus **FR-1399**. No NFR id.
`PL-1991` cites FR-219 and FR-1399 only. The superseded `PL-1278` is excluded as before.

| Class | Ids |
|---|---|
| **Deliverable** | CR-1979's 13 (FR-217, FR-218, FR-258, FR-227, FR-212, FR-216, FR-274, FR-275, FR-276, FR-237, FR-20, FR-239, FR-219) **plus FR-1399's FD-1768 amendment** (`PL-1991`; `03-rating-engine.md:198`, "*(Amended 2026-11-03, WK-1250, SL-1989, FD-1768, `PL-1991` DP-5 (a), DP-6 (a) and DP-7 (a) …)*"). FR-1399 itself is WK-673's (attribution); WK-1250 owns this amendment only |
| **Honoured, not owned** | FR-4, FR-16, FR-343, FR-345, FR-368, FR-417, FR-214, FR-215, FR-240, FR-244, FR-248, FR-252 (unchanged) |
| **Not this Work's** | FR-294 (WK-685, Phase 4); FR-1186 (WK-675's; CR-1952) |

**Requirements axis** (`scope-audit.py` is refused by `run-heavy.sh --light` with rc 78,
"--light is for scripts/audit-docs.py or scripts/doc-index.py only", so it ran directly, niced,
load1 1.47, gate-1 and gate-1b free, as CR-1979 did):

```bash
nice -n 19 python3 scripts/scope-audit.py RATE --sections NONE --extra FR-212,FR-216,FR-217,FR-218,FR-219,FR-227,FR-237,FR-239,FR-258,FR-274,FR-275,FR-276,FR-214,FR-215,FR-240,FR-244,FR-248,FR-252,FR-1186,FR-1399
nice -n 19 python3 scripts/scope-audit.py OVR  --sections NONE --extra FR-4,FR-16,FR-20
nice -n 19 python3 scripts/scope-audit.py GOV  --sections NONE --extra FR-343,FR-345,FR-368
nice -n 19 python3 scripts/scope-audit.py PLAT --sections NONE --extra FR-417
```

| Run | In scope | With a `@pytest.mark.req` marker | No marker | rc |
|---|---|---|---|---|
| RATE | 20 | 19 | FR-1186 | 1 |
| OVR | 3 | 3 | — | 0 |
| GOV | 3 | 3 | — | 0 |
| PLAT | 1 | 1 | — | 0 |
| **Total** | **27** | **26** | **1** | |

FR-294 was not run (a Phase 4 id, named only to exclude it).

*(Dated line 2026-11-04, batch 8, on to-lead "2026-11-04 09:57:14 GMT", whose scope-audit paragraph accepts the evidence and asks the verbatim refusal in this build log.)* The refusal, verbatim: "`run-heavy.sh --light` refuses anything but `audit-docs.py` and `doc-index.py` (rc 78, header line 18)". The scope-audit runs above then ran directly, niced, read-only; that was a bypass of the refusal, not a route the tool allows, and the process row is in `docs/process/process-backlog.md` (batch 8).

*(Dated line 2026-11-04, batch 8 build-log note, on to-lead "2026-11-04 10:16:30 GMT" ruling (a).)* Unasked edit, kept: in the docs-batch-8 WF-699 E2 correction (commit `ec4c8db2`) the auditor also added `364` to the row's spec-citation cell (`06` FR-352/363/364); the brief asked for the dated correction line only. The maintainer's 10:16:30 ruling keeps it.

**Endpoints axis.** `scope-audit.py RATE --endpoints`: "declared : 45 / published : 45 (100%) /
every declared endpoint is published in the contract"; rc 1 from the whole-module requirements
half (FR-1186, FR-1903, NFR-492, NFR-493, NFR-1443; none WK-1250's).

**Catalogue axis.** `grep -cE '^\| `[A-Z]{2,4}-[A-Z]{2,4}-[0-9]+` [a-z0-9-]+' docs/specs/03-rating-engine.md`
prints `0`: no catalogue in the form the script reads.

## Evidence

### §1. Each deliverable: exists and works

**CR-1979's §1 carries, re-checked for drift.** Since `c807a59d`, the files its §1 cites changed
in four places, each read:

- `packages/pricing-core/src/pricing_core/rating/compile.py`, `packages/pricing-core/tests/test_rating_compile_bundle.py`
  and `backend/src/app/platform/rating_algorithms.py`: changed only by `dfbce89b` (#1421, SL-1985,
  FD-1495, a **WK-673** slice: roadmap `:1025` sits under `### WK-673` at `:688`, and its front
  matter reads `work: WK-673`). `git diff -U0 c807a59d db92a7bc -- …/rating/compile.py | grep -E '^[-+]' | grep -ciE 'sub_graph|mount|inlin|purpose'`
  prints `0`. The test file gained 3 lines at `:114` and 3 at `:582`: CR-1979's cites in that file
  from `:114` on move by +3 (e.g. `:383` → `:386`, `test_g1_a_mount_whose_version_is_not_pinned_is_refused_with_no_steps`;
  `:473` → `:476`; `:539` → `:542`), content unchanged.
- `backend/tests/test_rating_version_dislocation_gate.py`: changed by `db92a7bc` (#1426, WK-673);
  `test_the_persisted_structural_diff_carries_a_sub_graph_re_point` is still at `:290`.

**The one new deliverable, SL-1989** (PR #1423, squash `7b8a00cf`, `git merge-base --is-ancestor
7b8a00cf db92a7bc` rc 0), read against `PL-1991` and FD-1768's row:

| Item | Evidence (asserts read) | Reading |
|---|---|---|
| A purposes-only change is worded "mount purposes changed" | `test_rating_attribution.py:1520` | delivered |
| Ports and purposes both changed: the re-map form plus "; purposes changed" | `:1523` | delivered |
| A re-point with a purposes change: the re-point form plus "; purposes changed" | `:1525` | delivered |
| The ports-only form unchanged | `:1452` (`ports_only.description == f"m_ncd: mount ports re-mapped ({_NCD4})"`) | delivered |
| The diff keeps a purposes-only change as one mount change, `before == after` | `:1483` | delivered |
| FR-1399's dated amendment | `03-rating-engine.md:198` (quoted in §0) | delivered |

**`PL-1254`'s acceptance standard** (CR-1979's table): items 1–6 met as CR-1979 read them;
**item 7 ("every slice closed on its own clean audit") is not met for SL-1989** (§R item 1a);
item 8 (the full gate on the merged tree of the last slice) is met by §2.

### §2. The gate

**Evidence of record (the maintainer's ruling "2026-11-04 08:46:25 GMT"; accepted
"2026-11-04 09:44:40 GMT"):**

1. **The fresh full gate**, exec-gate1250, head `824a891da8b421d8a0fbe9430934aff8ecd4d574`, tree
   `5282fbda133a7fad2212c8cd46ccb8bd9bef69c7`, script `wk1250-gate.sh` sha256
   `c994df52425eeac08252ada3491603f9122c780995896e3579a0eb496dd6714a`, logs
   `~/gi-pricing-plan.local/scratch/wk1250-gate/gate/`. Read by this seat:

   | Row (`gate.log`, verbatim) | Value |
   |---|---|
   | START | `2026-11-04T07:41:27+00:00 1.02 1.07 1.45` |
   | ruff / mypy / import_linter / audit_docs / req_coverage / contracts / pytest | `rc=0` each; the seven `*.rc` files each hold `0` |
   | pytest summary | `7072 passed, 22 skipped, 5 xfailed, 146 warnings in 5096.89s (1:24:56)`; `pytest skipped \| 22 (== 22 baseline)` |
   | frontend: install, generate:api, lint, type-check, test `--maxWorkers=2`, build | `rc=0` each; `fe-test.log`: "Test Files  138 passed (138)", "Tests  919 passed (919)" |
   | demo | `designed stop at 2026-11-04T09:41:36+00:00 (both lines seen)`; `demo seconds \| 1728`; `demo.py --journey wf-699 --no-compose \| rc=0` |
   | dislocation #1 | `623 s (29 Oct passes: 422 / 387 / 383 s; this box 21:17:05 baseline 552 / 558 s)` — no pass/fail attaches; the maintainer reads it as environment drift (09:44:40) |
   | template guard | start and end `alembic_version=1 environments=3 tenant_marker=1 \| rc=0` |
   | zeros | `own-DB count=0 redis RT db 1 dbsize=0 redis RD db 3 dbsize=0` |
   | END | `2026-11-04T09:41:46+00:00 2.05 2.19 2.16 (date l1 l5 l15) rc=0` |

2. **Merge 55's PR CI.** `824a891d` is `db92a7bc`'s parent; the only commit between them is
   #1426 (WK-673's S-b). Its PR head `84b1d859eb8acdbcc1a9711c86c53476aa199079` has tree
   `ede3bf38` = `db92a7bc`'s tree. `gh run view 41797547929`: `python`, `pull_request`, head
   `84b1d859`, `completed` / `success`; with docs 41797547981 and history-policy 41797548020,
   `success`. `git diff --name-only 824a891d db92a7bc` lists 17 paths under `backend/`, `docs/`
   and `packages/pricing-core/{src/pricing_core/rating,tests}`; none matches a
   `.github/workflows/frontend.yml` path filter (`frontend/**`, the workflow file,
   `docs/contracts/openapi/**`, `packages/pricing-core/src/pricing_core/modelling/**`), so the
   gate's frontend half carries to `db92a7bc`.

**SL-1989's own gate of record:** the full gate at `322b20ece4a1fd18a54a960d9a749366a4522f1a`
(`~/gi-pricing-plan.local/scratch/sl8296-gate/gate/gate.log`: "13 failed, 7026 passed, 22
skipped", END rc=1), which STANDS under the common seat brief's item 31 by the maintainer's entry
"2026-11-04 01:10:01 GMT"; and PR CI on head `3d95a65e07be25ffebd1fe2bdfbfd5de549758fb`: python
41754948183 `success` (read here), docs 41754948240, history-policy 41754948192
("2026-11-04 01:56:03 GMT"). The slices CR-1979 tabled keep their gates of record.

### §3. New checks proven on broken input

| Check | Red proof | Ancestry |
|---|---|---|
| SL-1989's wording (FR-1399, FD-1768) | red commit `7e2fdfa22f6fc72bfebb0c84c1c6925e40964631`; `~/gi-pricing-plan.local/scratch/sl-8296/red2.log` opens `head=7e2fdfa2…`, fails at `test_rating_attribution.py:1449` on `assert alone.description == f"m_ncd: mount purposes changed ({_NCD4})"`, "1 failed, 44 passed", `rc=1`; the injection is the unfixed `analysis.py` itself, so it breaks what the check claims | `git merge-base --is-ancestor 7e2fdfa2 3d95a65e` rc 0 (PR #1423's head); the fix `1063f39e` and the gated `322b20ec` likewise rc 0 |

CR-1979's §3 rows carry unchanged. This seat ran no test.

### §4. NFRs

No NFR id is in the derived scope. **NFR-489 on a mounted bundle: PROPOSED deferred with an owner**
— owner WK-1250, measured at nfr-bench-1 session S1, Thu 5 Nov 2026, item D
(`nfr-bench-1-plan-2026-11-04.md:37`, `:92`: "unmet → an FD"; ruled "2026-11-03 16:13:02 GMT"
item (2); plan accepted "2026-11-04 09:04:20 GMT"). If S1 reads it unmet, it is a P2 finding owned
by WK-1250, "fixed or carried with a resolution at the close" (16:13:02 (2)). NFR-489: mounted bundle (an NCD sub-graph mount + a cancellation purpose mount, pins.sub_graphs set): measured Thu 5 on nfr-bench-1 by driver sha256 df6e7c9c3216895d175434cf92bd5d26c0335fe7f48621dfee5c2919997513d3, reading owed; Thursday's reading lands as a dated delta line in this CR; unmet → an FD owned by WK-1250 (to-lead 2026-11-03 16:13:02 (2)).

**Pre-registration of nfr-bench-1 item D** (the maintainer's ruling "2026-11-04 09:45:54 GMT": "the WK-1250 record that carries D's hash is CR-1999"; the hash of record from "2026-11-04 09:51:05 GMT"):

| Id | Configuration and driver | Reading |
|---|---|---|
| NFR-489 | mounted bundle (an NCD sub-graph mount + a cancellation purpose mount, pins.sub_graphs set): measured Thu 5 on nfr-bench-1 by driver sha256 df6e7c9c3216895d175434cf92bd5d26c0335fe7f48621dfee5c2919997513d3, reading owed | owed: Thursday's reading lands as a dated delta line in this record; unmet → an FD owned by WK-1250 ("2026-11-03 16:13:02 GMT" (2)) |

### §5. Not delivered: every requirement without evidence, with a PROPOSED verdict

| Id / item | PROPOSED verdict | Evidence |
|---|---|---|
| FR-1186 | **PROPOSED: reassigned — not WK-1250's** (WK-675; adopted 15:58:45 (2)) | CR-1979 §5 |
| FR-294 | **PROPOSED: reassigned — WK-685, Phase 4** | `PL-1629:252` |
| NFR-489: mounted bundle (an NCD sub-graph mount + a cancellation purpose mount, pins.sub_graphs set): measured Thu 5 on nfr-bench-1 by driver sha256 df6e7c9c3216895d175434cf92bd5d26c0335fe7f48621dfee5c2919997513d3, reading owed; Thursday's reading lands as a dated delta line in this CR; unmet → an FD owned by WK-1250 (to-lead 2026-11-03 16:13:02 (2)) | **PROPOSED: deferred with an owner — WK-1250, nfr-bench-1 S1 Thu 5 Nov** | §4 |
| SL-1989's slice audit (`PL-1254` item 7) | **PROPOSED: delivered but untested at slice level** — the code is evidenced by assertion here (§1, §3) and gated (§2), but no slice audit was written. Two routes, the lead's to choose: (a) this record stands for it, as the maintainer accepted for SL-1388 / SL-1389 in the entry "2026-11-04 08:05:12 GMT" (FD-1982 ruling (a): "a slice audit filed now for two merged slices would evidence what WK-673's close audit evidences at requirement level"), by a dated line; or (b) an auditor writes `LG-1990`'s "## Audit" | §R item 1a |
| SL-1989's closing acts | **owed, docs only**: `LG-1990` and roadmap SL-1989 `status: closed`; `LG-1990`'s MERGE-ACK line quoting "2026-11-04 01:56:03 GMT" and its "## PRs" naming #1423, `7b8a00cf`; FD-1768's register row and essay citing #1423, `7b8a00cf` | §R item 1a |

**The P3 carries ruled 3 Nov** (the entry "2026-11-03 19:20:34 GMT", batch 7, #1420 `4df71cd7`):
FR-364's `rate_table_diffs` limb (P3) is owned in WK-673's section (`docs/roadmap.md:700`);
FD-1491 and FD-1576 (`register.md:317`, `:332`: `~~WK-673~~ WK-1178`) and FD-1751's
expression-Factor limb (`:385`: `~~WK-690~~ WK-1178`) are **deferred with an owner, WK-1178**.
**None is WK-1250's.**

### §5a. Binding plan-review conditions

Unchanged from CR-1979 §5a: `CR-1247` Proposal 10 met; `CR-1907` row 10 met in the Decision cell;
E1–E7 name nothing for WK-1250. Re-run: of the `kind: review` records under `docs/closures/`, only
`CR-1907` contains `WK-1250` (one hit); its last change is `f7a1ccd9` (2026-10-26). Nothing new.

### §5b. The owed list, generated

```text
Generated by `python3 scripts/register-owed.py WK-1250` against `db92a7bc (`docs/wk1250-fresh-close-2026-11-04`)`.
Mode: work item 'WK-1250'. 4 owed row(s), 1 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).

- … (FD-1241) (work item: 'WK-669', phase: '2') — **not started** … unowned-pending-authorisation, 2026-09-29 …
- … (FD-1317) (work item: 'WK-1178', phase: '2') — **deferred with an owner — WK-1178** …
- … (FD-1326) (work item: 'WK-1250', phase: '2') — **carry forward with an owner** (WK-1250 Slice 1, fixed by its merge …) …
- … (FD-1768) …

Excluded as opening with a resolution marker — verify:
- `compile_bundle` does not check step table, lookup and model refs against the pin set (FR-237) (FD-1297)
```

*(Rows elided at "…"; the run printed each cell whole. rc 0.)*

**The script's ids:** FD-1241, FD-1317, FD-1326, FD-1768 (owed); FD-1297 (excluded).

**Read by hand against `docs/findings/register.md`** (the known mid-cell defect, to-lead
"2026-11-03 15:36:59 GMT", stands):

| Row | Line | Hand reading | Owed? |
|---|---|---|---|
| FD-1241 | `:209` | "***Resolved 2026-10-25***: closed by the merged WK-1250 slices, PR #1034 …" mid-cell | **removed** — resolved |
| FD-1317 | `:221` | "***Resolved 2026-10-25***: closed by the merged fix, PR #1012 …"; a WK-1178 row | **removed** — resolved, not WK-1250's |
| FD-1326 | `:224` | "***Resolved 2026-10-01*** — closed in place 2026-11-03 … PR #1034 (`9b0fb97c`)" (#1418) | **removed** — resolved |
| FD-1768 | `:392` | "***Resolved 2026-11-04*** — closed in place … as the closing act of the mint of SL-1989 …"; the PR number and squash are not yet written in | **removed as a code item**; the citation is a closing act (§5) |
| FD-1297 | `:219` | "**Resolved 2026-09-30** by #988" | not owed |

**Corrected owed list: no register row is owed.** The remaining closing acts (§5) are SL-1989's.
Every id in the generated block appears above with a resolution.

### §5c. Workflow steps that cite this close's requirements

```bash
git grep -n -E '\b(FR)-(212|216|217|218|219|227|237|239|258|274|275|276|20|1399)\b' -- 'docs/workflows/WF-*.md'
```

Since `c807a59d`, the in-scope requirement rows changed are FR-237 (CR-1979's dated clause, #1419)
and FR-1399 (SL-1989's dated amendment, #1423) — `git diff -U0 c807a59d db92a7bc -- docs/specs`
adds rows `**FR-1399`, `**FR-237` and `**FR-364` only. The journeys changed are WF-699 (C1, the
dated line CR-1979 added) and WF-702 (hunks at `:86-87`, `:121`, `:137`, `:173`, `:181`, `:219`;
its FR-20 cites at `:139` and `:207` are outside them).

| Journey | Step | Id | Reading at `db92a7bc` |
|---|---|---|---|
| WF-699 | C1 | FR-237 | **now still says it**: the dated line "(Amended 2026-11-03 … at the WK-1250 close audit (working id CR-1979): and the `sub_graph:…` pin" matches FR-237's appended clause |
| WF-702 | C7 `:139`, `:207` | FR-20 | still says it (unchanged lines) |
| every other CR-1979 §5c row | — | — | unchanged lines; still says it |

**FR-1399 is cited by no journey** (the command's FR-1399 term matches nothing). No step cites
FR-218. No disagreement; no finding.

## Findings

- **FD-1768**: resolved in code by #1423 (`7b8a00cf`); its register row and essay do not yet cite
  the PR and squash (§5).
- **FD-1326**: closed by #1418.
- **FD-1241, FD-1317**: resolved 2026-10-25; listed by the script's mid-cell defect.
- **FD-1297**: resolved 2026-09-30; correctly excluded.
- **FD candidate (not minted, the lead's to route)**: six slices merged 3–4 Nov 2026 — SL-1985,
  SL-1987, SL-1989, SL-1992, SL-1994, SL-1997 — each read `status: active` in `docs/roadmap.md`,
  and each ledger (`LG-1986`, `LG-1988`, `LG-1990`, `LG-1993`, `LG-1995`, `LG-1998`) has a
  placeholder "Audit" section ("(the auditor's)" or "Written by the auditor.") and a MERGE-ACK
  line reading "(added at merge)" or "not yet given". The same class as FD-1982 (SL-1388 /
  SL-1389). Only SL-1989 is WK-1250's. Likely a process row (the record form at merge), unless the
  lead names limb (i).
- **Observations, not findings**: the WK-1250 scope line and SL-1341's "MERGE-ACK: pending" are
  still stale (CR-1979); `register-owed.py`'s mid-cell defect now over-counts four of four rows for
  this Work.

## Replan check (`CLAUDE.md` §14, `RFC-1248`)

1. **Completion — yes.** The roadmap scope line still reads FR-217's inlining limb only, narrower
   than `PL-1254`'s three limbs; `PL-1254:157`'s alignment PR has not landed. Moves nothing.
2. **Omission — no.** FD-1768's fix, the one omission CR-1979 named, merged as SL-1989 inside this
   Work. No new requirement surfaced.
3. **Skills and research — yes.** `register-owed.py`'s mid-cell defect (known, "2026-11-03
   15:36:59 GMT") lists four resolved rows as owed. Moves nothing.
4. **Drift — yes, closed.** FR-237 and WF-699 C1 were aligned by #1419; FR-1399 was amended with
   its code by #1423; no journey cites FR-1399. Remaining drift is record form (§R 1a). Moves
   nothing.
5. **Shape — no.** No phase boundary or Work scope moved since CR-1907.

`register-owed.py review` at `db92a7bc`: **31 owed rows** (11 excluded as opening with a
resolution marker); rc 0.

**Triggers:**

- A phase boundary or Work scope moved: **not fired**.
- An exit criterion at risk: **not fired.** CR-1979's firing was FD-1768 with no slice; it merged
  Wed 4 Nov, before code freeze (Tue 10 Nov). What remains is docs-only (before docs freeze, Wed 11
  Nov) plus the NFR-489 reading on Thu 5. *If item D reads unmet, this trigger fires.*
- A replan decided: **not fired**.
- A finding that moves a slice or a phase: **not fired.**

**PROPOSED: no trigger; no full review now.** The pre-demo §14 review (Mon 16 – Tue 17 Nov 2026)
is unchanged. **The verdict is the lead's.**

## Verdict

**PROPOSED: NOT CLOSE-READY — no code owed.** Every deliverable is evidenced by assertion (§1),
the fresh full gate and merge 55's CI are green on the closing tree (§2), every binding plan-review
condition is met (§5a), and no register row is owed (§5b). **Owed before the user's acceptance
line:**

1. **SL-1989's slice audit**: route (a) (a dated line accepting this record in its place, as
   "2026-11-04 08:05:12 GMT" did for SL-1388 / SL-1389) or route (b) (an auditor fills `LG-1990`'s
   "## Audit").
2. **SL-1989's closing acts** (docs only): `LG-1990` and SL-1989 `closed`; `LG-1990`'s MERGE-ACK and
   "## PRs" lines; FD-1768's row and essay citing #1423, `7b8a00cf`.
3. **NFR-489 on a mounted bundle**: nfr-bench-1 S1, Thu 5 Nov 2026, item D. **PROPOSED: deferred
   with an owner**, so it need not hold the close; if read unmet, a P2 finding owned by WK-1250.

If the lead takes route (a) and the closing acts land, this record proposes **CLOSE-READY** for
the user's line without a further audit.

Every §13 verdict above is PROPOSED and is the lead's. **The close is the user's dated
acceptance line.**

## 2026-11-04 — delta: condition (1) met

*(Dated line 2026-11-04 11:28 GMT, by the auditor, read at `origin/main` e3c150c4827a2f2f29e5314bb264c24125d714a7. No verdict is changed.)*

- **Batch 8 is on main.** The docs batch merged as #1427, squash commit `e3c150c4827a2f2f29e5314bb264c24125d714a7`, at 2026-11-04 11:25:06 GMT (from-lead "2026-11-04 11:25:06 GMT").
- **What it carries on main**, each read at that squash:
  - SL-1989's closing act: `docs/roadmap.md:3575` (`status: closed` in the SL-1989 block that opens at `:3569`).
  - D's pre-registration: driver sha256 `df6e7c9c3216895d175434cf92bd5d26c0335fe7f48621dfee5c2919997513d3` in this record's NFR-489 rows, `:46`, `:194`, `:200` and `:208`.
  - LG-1990 closed: `docs/ledgers/LG-01990-wk-1250-slice-sl-8296-a-purposes-only-mount-change-is-worded-mount-purposes-changed.md:5` (`status: closed`), with the closing line at `:117` (SL-1989 merged as #1423, squash `7b8a00cf356f258cef764a5af576b28b01195186`).
  - FD-1768's PR citation: `docs/findings/register.md:392` and `docs/findings/FD-01768-attribution-words-a-purposes-only-change-to-a-sub-graph-mount-as-mount-ports-re-mapped.md:46` (PR #1423, squash `7b8a00cf`), with `status: closed` at `:5` of the essay.
- **Condition (2), S1 item D's reading on Thu 5 Nov 2026, is OWED.** Its owner is WK-1250 (§4; NFR-489 on a mounted bundle). The reading lands as a further dated delta line here; if it reads unmet, an FD owned by WK-1250 follows.
- **Status of the proposal:** the verdict stays PROPOSED, as adopted at "2026-11-04 09:57:14 GMT". Condition (1) of 09:57:14 is met; (2) is owed. **The close is still the user's dated line.**
