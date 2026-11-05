---
id: CR-8314
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-690 fresh Work close audit — expression custom objectives (re-tests CR-1980)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-11-05   # drafted 2026-11-05 under working id 8314
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: 2f108b1eda22a4835279cee9b4c9e305babe3662
phase: P2
work: WK-690
corrected_by: []
relates: [CR-1980, CR-1212, CR-754, PL-1268, PL-1621, PL-1665, PL-1996, RL-1265, RL-1362, RL-1616, SL-1275, SL-1994, LG-1839, LG-1995, FD-1751, FD-1842]
---

# CR-8314 — WK-690 fresh Work close audit

*Working id CR 8314, reserved by the lead. The auditor seat aud-wk690c wrote this record on
2026-11-05 from 11:08 UTC (`date -u`). The instruction is the lead's brief
`brief-aud-wk690c-2026-11-06.md` with its dated line of 2026-11-05 11:07:59 GMT, on the maintainer's
entries "2026-11-05 11:07:14 GMT" and "2026-11-05 11:08:46 GMT" in
`~/gi-pricing-plan.local/channel/to-lead.md`. The brief asks for `created: 2026-11-06`; the seat was
seated a day early and `date -u` reads 2026-11-05, so this record carries that date. It re-tests
`CR-1980` (NOT CLOSE-READY, 3 Nov) and follows `.claude/skills/close-workstream`, `CLAUDE.md` §13
and §14.*

**What this record is.** It gathers evidence and **proposes**. Every §13 verdict below is written
"PROPOSED" and is the lead's to give. **The close is the user's dated acceptance line.** This record
does not close WK-690. It is a **draft that records a block**: its PR waits for nfr-bench-1 S2's
readings (to-lead "2026-11-05 11:08:46 GMT").

**Object.** `origin/main` at `2f108b1eda22a4835279cee9b4c9e305babe3662` (tree
`446043bb1712d31b876793855a5f55e79beb5a85`), read with `git ls-remote origin refs/heads/main` at the
start, plus the S1 records on `origin/docs/nfrbench-s1-wk690-2026-11-05` at `827de1b8` (the LG-1839
addendum, read with `git diff 2f108b1e...827de1b8`; not on main at this writing). Every `file:line`
and count below is at that tree unless it names another. Branch `docs/wk690-fresh-close-2026-11-06`,
cut from that commit. The form is `CR-2000`'s.

**The two S1 findings are working ids here.** FD 8350 (NFR-476) and FD 8352 (FR-1840 3c) are filed by
batch 11 and are on no branch at this writing (`git grep` on `origin/docs/fdclose-2026-11-05` at
`41890138` finds neither). They enter `relates:` at the mint.

## §R. Re-test of CR-1980's findings

CR-1980 (tree `c807a59d`, NOT CLOSE-READY, adopted at "2026-11-03 16:02:43 GMT") named three blocks
and five findings. Each, re-tested at `2f108b1e`:

| # | CR-1980 item | What changed (PR, squash) | Re-test | Status now |
|---|---|---|---|---|
| 1 | Block 1: FD-1842 | **#1425, `824a891da8b421d8a0fbe9430934aff8ecd4d574`** (SL-1994, LG-1995, PL-1996; merge 54, MERGE-ACK "2026-11-04 06:20:47 GMT") | `expressions.py` `parse_expression`: `_check_limits` runs before `_check_structure`; register row `***Resolved 2026-11-04***`; §1b | **discharged** |
| 2 | Block 1: FD-1751, guarded limb | none in code; re-dispositioned by "2026-11-03 16:13:51 GMT" decision (ii) | `diagnostics.py:1085`, `:1517` still omit by `EXPRESSION_FACTOR`; `:1095` and `:1351` not reached for it (`diagnostics.py` unchanged since `c807a59d`: `git diff --shortstat` prints nothing). Register row: owner ~~WK-690~~ WK-1178 | **discharged by the guard** |
| 2a | FD-1751, the expression-Factor diagnostic (FR-174, FR-175, FR-177) | carried, same entry | register row: carried to P3, owner WK-1178; CR-1980's Deferral line | **deferred with an owner: WK-1178 (P3)**, with DP-8301-3's monotonicity omission (`diagnostics.py:673`) beside it |
| 3 | Block 2: `PL-1665` 5.7 (FR-1840 3c, 3d) unmeasured | S1 item B, `dae9637e`, 2026-11-05 10:15:20–10:18:52Z | §4 | **measured: 3d PASS, 3c UNMET → FD 8352** |
| 3a | SL-1275's closing acts | none | roadmap `:1931` row and LG-1839 `status: active`; the closing condition (5.7 measured) is now met | **owed, docs only** (§Findings F1) |
| 4 | Block 2: NFR-476's full shape unmeasured | S1 item A, `dae9637e`, 2026-11-05 09:33:06–10:13:06Z; rulings "2026-11-05 10:14:38 GMT", corrected by "2026-11-05 11:12:59 GMT" | §4: the process hit its cap; fit time unmeasured; **the fit limb is not WK-690's** (`CR-754:163`); the expression limb, WK-690's, not run | **split:** fit limb carried by `CR-754:163`, its measurement on a 16-core host owed there; **expression limb open, BLOCKS until S2 item M** |
| 5 | Block 3: the fresh full gate | exec-gate1250 at `824a891d`, accepted "2026-11-04 09:44:40 GMT" | §2: contains all seven WK-690 squashes; every rc 0 | **PROPOSED discharged** (§2 states the condition) |
| F1 | SL-1275 merged and `active` | see 3a | | **open** |
| F2 | FR-207's move not in the WK-690 section | none | `roadmap.md:1841` unchanged | **open**, a dated line owed |
| F3 | SL-1274 row "MERGE-ACK: not yet given" | none | `roadmap.md:1929` unchanged | **open**, a dated line owed |
| F4 | Two measurements on no schedule | nfr-bench-1 plan items A and B, accepted "2026-11-04 09:04:20 GMT" | both ran in S1 | **discharged** |
| F5 | `register-owed.py WK-690` lists FD-1704 by text mention | none | still listed (§5b); `process-backlog.md:109` is the mid-cell defect, a different one | **open**, a process row owed |
| §5c | Five `WF-702` steps disagree | docs batch 7, `4df71cd7`, "Wording corrected 2026-11-03" on the rulings "16:03:37" and "19:25:11" | §5c | **discharged** |

## Scope

### §0. The requirement set, derived from the documents before any evidence

**Predicate** (runnable from the repository root at `2f108b1e`): the union of the ids cited by the
WK-690 roadmap section (`docs/roadmap.md:1827`, up to the next `### WK-` heading at `:1995`) and every
plan with `work: WK-690` (now seven: `PL-1268`, `PL-1295`, `PL-1327`, `PL-1382`, `PL-1621`, `PL-1665`,
`PL-1996`):

```bash
( sed -n '1827,1994p' docs/roadmap.md
  cat $(grep -lE '^work: *WK-690' docs/plans/*.md)
) | grep -ohE '\b(FR|NFR)-[0-9]+\b' | sort -u -V
```

It prints **60 ids**; the section alone prints 33. The deliverable set is unchanged from CR-1980, read
again from `PL-1268`'s core-scope table and the two ids appended after it: **24 ids**: `02` FR-95,
FR-144, FR-145, FR-146, FR-147, FR-148, FR-149, FR-150, FR-152, FR-163, FR-165, FR-207, FR-208 (the
`expression` arm), FR-1840, NFR-476, NFR-480, NFR-483, NFR-484; `06` FR-366, FR-367; `07` FR-448,
FR-449; `01` FR-36; `03` FR-244. Unnumbered items: `02` §4.6's profile table, `02` §4.7's expression
half, `02` §5.3's Custom objective library, `01` §4.5's `expression` check, `WF-702` Route B. SL-1994
adds no id: its requirements are FR-145 with §4.6's clarification of 2026-11-03, and FR-150 and FR-95
for the two callers' codes (LG-1995 Scope).

**The growth from 57 to 60** is FR-89, FR-174 and FR-175 (`comm -13` of the predicate at `c807a59d`
and at `2f108b1e`; none removed). None joins the deliverable set: FR-174 and FR-175 are §R 2a's, and
FR-89 is context, not a `PL-1268` core-scope id.

**Moved out of WK-690, each by a dated record:** FR-85, FR-86's field, FR-210 with FR-208's `spline`
and `polynomial` arms, FR-154's expression half (Phase 3, `RL-1265`, `roadmap.md:1841`); FR-207's two
`custom_objective_ref` residuals (Phase 3, `RL-1362` DP-S3-5, `02` FR-207); FR-176, FR-177, FR-178
(WK-1178, FD-1195); FR-174, FR-175 and FR-177's expression-Factor limb (P3, owner WK-1178, "2026-11-03
16:13:51 GMT" (ii)).

**E and F are not WK-690's.** The brief asks: S1 items E (SL-1569) and F (SL-1367) go to WK-690 only if
their rows say so. They do not. `roadmap.md:2591`, "#### SL-1569 — WK-1178 fix slice — a declared
decimal output is served as an exact JSON string on every scoring path", `work: WK-1178`;
`roadmap.md:2205`, "#### SL-1367 — WK-1178 slice — FD-1335 Part A: …", `work: WK-1178`. Item C
(NFR-489 ladder) is WK-674's by the brief's pre-stage note.

**Requirements axis.** `scope-audit.py`, one run per module, through `run-heavy.sh` without `--light`
(the brief's CORRECTION), the `tools-main` venv and this worktree's script. Each log opens `head=` and
closes `rc=`, under `~/gi-pricing-plan.local/scratch/docs-wk690-fresh-close-2026-11-06/`:

```bash
run-heavy.sh -- uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py MODEL --sections NONE \
  --extra FR-95,FR-144,FR-145,FR-146,FR-147,FR-148,FR-149,FR-150,FR-152,FR-163,FR-165,FR-207,FR-208,FR-1840,NFR-476,NFR-480,NFR-483,NFR-484
# and GOV --extra FR-366,FR-367; PLAT --extra FR-448,FR-449; DATA --extra FR-36; RATE --extra FR-244
```

| Run | In scope | With a `@pytest.mark.req` marker | No marker | rc |
|---|---|---|---|---|
| MODEL | 18 | 16 (89%) | NFR-476, NFR-480 | 1 |
| GOV | 2 | 1 (50%) | FR-366 | 1 |
| PLAT | 2 | 2 | — | 0 |
| DATA | 1 | 1 | — | 0 |
| RATE | 1 | 1 | — | 0 |
| **Total** | **24** | **21** | **3** | |

`req-coverage.py`, the same route: rc 0. Each log's first line is `head=2f108b1e…`.

A marker on an id is not evidence of WK-690's limb of it (CR-1980 §0): FR-207's and FR-208's markers
are on other limbs, as they were.

**Endpoints axis.** `scope-audit.py MODEL --endpoints`: 45 published of 45 declared (100%), "every declared endpoint is published in the contract". The log's rc 1 is the run's default requirements section, which lists `02` NFRs outside this Work's `--extra` set, not the endpoint table.

**Catalogue axis.** `02` declares no catalogue in the form the script reads: `grep -cE '^\|
`[A-Z]{2,4}-[A-Z]{2,4}-[0-9]+` [a-z0-9-]+' docs/specs/02-modelling.md` prints `0`.

## Evidence

### §1. Each deliverable: exists and works

CR-1980 §1 read each assert at `c807a59d`. **Re-read predicate:** `git diff --shortstat c807a59d
2f108b1e -- <path>` over `expressions.py`, `expression_objective.py`, `modelling/objectives.py`,
`diagnostics.py`, `model_schema/objectives.py`, `permissions.py`, `model_schema/modelling.py`,
`api/custom_objectives.py`, `platform/objectives.py`, `platform/objective_preview.py`,
`platform/settings.py`, `test_wf702_route_b.py`, `ObjectiveEditorView.vue`, `ObjectiveLossCurve.vue`,
`uv.lock`. **Two paths moved**: `expressions.py` (SL-1994, +3 −1, §1b) and `uv.lock` (33 lines, not
`sympy`: `uv.lock:2395-2396` still `1.14.0`, `pricing-core/pyproject.toml:19` `"sympy==1.14.0"`). So
CR-1980's table stands at this tree for every row except FR-145, and is not repeated. Re-read here:
the flag default (`settings.py:341`, `False`), and the two rows below.

| Deliverable | Exists, at `2f108b1e` | Works: the assert read |
|---|---|---|
| Node and depth limits ahead of the recursive walk (FR-145, §4.6, NFR-483) | `expressions.py` `parse_expression`: `_check`, then `_check_limits`, then `_check_structure`, with its comment | §1b |
| FR-1840 3c's "never queue ahead" limb | `objective_preview.py:46`: `ThreadPoolExecutor(max_workers=PREVIEW_WORKERS, thread_name_prefix="objective-preview")`; `:43` `PREVIEW_WORKERS = 2` | `backend/tests/test_objective_preview.py:185`, `test_3c_the_preview_executor_is_its_own_and_shared_with_nothing`: the separate-executors test `PL-1665` 5.7's last sentence requires. **It discharges the queueing limb only; the p99 limb is §4's** |

### §1b. SL-1994 (merged since CR-1980), per requirement

Route (a) of to-lead "2026-11-04 09:57:14 GMT": "SL-1994 (WK-690's fresh audit Fri names it)". This
section is that audit. Scope from `PL-1996` as amended by "2026-11-03 16:13:51 GMT" (limb 1 struck).

| Requirement | Evidence: the assert read | Red first |
|---|---|---|
| FR-145 (§4.6: node count ≤ 200, depth ≤ 20; the clarification of 2026-11-03) | `test_expression_limits.py:116-122`: `-`×99 + `x` raises `ExpressionError` matching "depth 100; the limit is 20", under a lowered recursion limit, both strict profiles; `:125-137` the 2000-character chain and the long sum; `:139-149`: `_check_structure` patched to raise, so the walk is proven not entered | 8 failed, 19 passed at `84e9ad34`, by `RecursionError` at `expressions.py:259` (LG-1995 Gate); green 27 passed, rc 0 (`green-limits3-c6d4d2b1….log`, read) |
| FR-150 (the create path's code) | `test_custom_objectives_expression.py:629-648`: flag on, `POST /custom-objectives`, a 2000-character chain and the over-bound cases: 422, `OBJECTIVE_GRAMMAR_VIOLATION`, one error on `loss`, "FR-145" in its message | `backend-prefix-84e9ad34.log`: 3 failed, 6 passed, rc 1 (read); the create case answered 500 `INTERNAL_ERROR` before the fix |
| FR-95 (the factor caller's code) | `:606-627`: 422 `VALIDATION_FAILED` at both factor tests | the same log; green 32 passed, rc 0 at `c6d4d2b1` (read) |
| `grammar_refusal` (FD-1842's named site) | `:564-572`: no `RecursionError`, and "depth 100; the limit is 20" in the refusal | the same log |

**Six of the nine pre-fix cases were already 422** (LG-1995's characterisation): only the deep chain
was a real defect, at both callers. **Two-way ledger check:** T-1 `9e1c4288`, T1 `84e9ad34`,
`c6d4d2b1`, `cdfceea5` and the gated `8a913212` are each ancestors of the MERGE-ACKed PR head
`7966fe1c` (`git merge-base --is-ancestor`, rc 0 ×5). The squash tree equals the PR head's:
`5282fbda133a7fad2212c8cd46ccb8bd9bef69c7`. **PROPOSED: SL-1994 audit CLEAN**, no finding. One disclosed
correction stands: LG-1995 T0 records that only create answers `OBJECTIVE_GRAMMAR_VIOLATION`, and the
§4.6 clarification states both codes.

### §2. The gate

**Gate of record per slice.** Every squash below is an ancestor of `2f108b1e` and of S1's checkout
`dae9637e` (`git merge-base --is-ancestor`, rc 0 ×14), and `dae9637e` of `2f108b1e`.

| Slice | Squash on main | The gate of record |
|---|---|---|
| SL-1271 (#981) | `bd67fb51` | CR-1980 §2, re-read not owed: pytest 4037 passed, 3 skipped (LG-1304:323) |
| SL-1272 (#1025) | `8933a29e` | CR-1980 §2: 7 of 7 stages (LG-1350:251) |
| SL-1273 (#1122) | `36a9f483` | CR-1980 §2: every stage 0 at `76897a8b` (LG-1412) |
| SL-1622 (#1295) | `2a819741` | CR-1980 §2: check-31-only, accepted (LG-1680:73) |
| SL-1274 (#1344) | `d87dd259` | CR-1980 §2: the working-id cascade set at `ebcb6eaa` (LG-1817) |
| SL-1275 (#1359) | `71e481fa` | CR-1980 §2: both halves rc 0 at `96354f9c` (LG-1839:61) |
| **SL-1994 (#1425)** | `824a891d` | below |

**SL-1994's gate.** Head `8a913212`, from-lead "2026-11-04 05:12:15 GMT", ruled STANDS by to-lead
"2026-11-04 05:13:46 GMT". Read from `scratch/sl8299-gate/gate/`:

| Stage | rc | Line |
|---|---|---|
| ruff, mypy, import_linter, req_coverage, contracts | 0 each | |
| pytest | 1 | `13 failed, 7041 passed, 22 skipped, 5 xfailed, 146 warnings in 4875.28s` |
| audit_docs | 1 | checks 31 and 32 on the slice's own working ids |

The 13 `FAILED` lines by file (`grep '^FAILED' pytest.log`): `test_audit_docs_finding_citations` 1,
`_ids` 2, `_process_core_digest` 2, `_w37_11_ceiling` 1, `test_doc_index` 1, `test_register_lint` 3,
`test_register_owed` 1, `test_repository_invariants` 2: exactly the eight item-31 files. The frontend
rows and the demo are quoted from the 05:13:46 entry (vitest 905/905; demo designed stop, 1718 s).

**#1425's CI.** PR head `7966fe1c`: python **41781425247**, docs 41781425195, history-policy
41781425185. Push at `824a891d`: python **41784947542**, docs 41784947559, history-policy 41784947611.
All `success` (`gh run view`, read). Latest python on main: 42011496062 at `2f108b1e`, `success`.

**Fresh full gate.** CR-1980 owed one. exec-gate1250's gate ran at `824a891d`, accepted "2026-11-04
09:44:40 GMT"; `scratch/wk1250-gate/gate/*.rc` read: audit_docs, contracts, import_linter, mypy,
pytest, req_coverage, ruff all 0; `7072 passed, 22 skipped, 5 xfailed`; frontend vitest 919/919 quoted
from the entry. It contains all seven WK-690 squashes. Since then (`git log 824a891d..2f108b1e`, 7
commits) `git diff --name-only -- packages backend/src frontend/src` prints five paths: `errors.py`,
`validation_rules.py`, `rating/analysis.py` and two rating tests, none a WK-690 deliverable.
**PROPOSED: it serves as WK-690's fresh gate, unless a code fix lands for FD 8350 or FD 8352**, in which
case a gate is owed at that head. This audit ran no test, no build and no gate.

**The S1 readings' tree.** `dae9637e` to `2f108b1e` is one commit (docs batch 10), and `git diff --stat
dae9637e 2f108b1e -- packages backend/src frontend/src scripts` prints nothing, so A and B stand at main.

### §3. New checks proven on broken input

CR-1980 §3 stands. New since it:

| Check | Red, and the red line | Reaches |
|---|---|---|
| The bound before the structure walk (FR-145, FD-1842) | `84e9ad34`: 8 failed, 19 passed, `RecursionError` at `expressions.py:259` and `AssertionError: _check_structure ran before the FR-145 bound refused`; backend 3 failed at the same commit, `500 INTERNAL_ERROR` | `7966fe1c` (#1425 head), rc 0 |

### §4. NFRs

**S1's environment** (LG-1839 addendum, `827de1b8`): `dae9637e`, dedicated VM `nfr-bench-1`, GCE
e2-standard-8, 8 vCPU, 32 GB, Xeon 2.20 GHz; quiet bar read before each start. Raw logs:
`~/gi-pricing-plan.local/scratch/nfr-bench-1/s1/`.

| NFR | Reading | PROPOSED |
|---|---|---|
| **NFR-476, fit limb** (5 M × 60 × 500, < 1200 s) | **Process cap reached; fit time unmeasured.** `itemA-fit.log`: `start=2026-11-05T09:33:06Z load1=0.82`, `cmd_rc=124`, `end=2026-11-05T10:13:06Z`, 210 bytes, no harness line. **The reading of record (to-lead "2026-11-05 11:12:59 GMT", correcting "10:14:38"): "the GBM arm (synthesis + fit + diagnostics + artifact) did not finish within 2400 s on an 8-vCPU host" — the fit's own time is UNMEASURED, not "≥ 2× over".** | **Not WK-690's limb** (below). FD 8350, MEDIUM as re-ruled, is carried to P3 on the P2 closure record's list |
| **NFR-476, expression limb** (≤ 1.25 over N ≥ 3 pairs): **WK-690's own** | **Not run in S1** (ruling (1) of 10:14:38; S2 item M, else S3). The only readings stay LG-1350's near-bound 1 M × 60 × 100: median 1.273 [1.166, 1.338] and 1.255 [1.215, 1.290], no verdict | **deferred with an owner: WK-690**, event item M. **Unmeasured, so it blocks** (§13) |
| **FR-1840 3c** (`/score` p99 at a moderate rate unaffected while previews saturate) | 25 rps, N = 3, 30 s, n = 750 each, errors 0, one uvicorn worker (`bench-b-pl1665-57.py` `--workers` default 1). ALONE p99 84.691 / 39.193 / 35.188 ms, median 39.193, range 49.503. SATURATED (8 in flight, ~1115 previews per run, all 200, preview p50 ~240 ms) 355.461 / 483.061 / 304.985 ms, median 355.461. Delta 316.268 ms > 49.503. Driver `AFFECTED`. Matches `itemB-run.log` line by line; driver sha256 `c68de47c…` re-hashed on this box | **UNMET → FD 8352 (MEDIUM, owner WK-690)**, per "2026-11-05 10:20:03 GMT" |
| **FR-1840 3d** (p95 ≤ 2 s, 500-point grid) | 100 sequential: p50 28.8, **p95 31.6**, p99 56.0, max 56.0 ms; non-200 0; `ok:false` 0. Driver `PASS`. (The 10:20:03 entry quotes p99 against the budget; the budget is p95. Both pass.) | **delivered, measured**; the provisional budget holds, so FR-1840's "replaces it by a dated amendment if it does not hold" does not trigger |
| NFR-480 | CR-1980 §4: measured, met, 1.174 s against 180 s | delivered |
| NFR-483, NFR-484 | CR-1980 §4: asserted by tests; NFR-483 gains SL-1994's bound-before-walk tests | delivered |

**Item A: what the reading proves.**

1. **The cap wrapped the process, not the fit.** `bench-model.py --only gbm` runs `bench_gbm` (`:388-414`):
   `synthesise`, then `fit_gbm` inside `timed("NFR-476 gbm fit, 500 trees")`, then
   `compute_gbm_diagnostics`, `_gbm_passes` and `_artifact_size`. The 2400 s covers all of it, so the
   fit may have ended at any point, under 1200 s included.
2. **The empty log does not show the fit still running.** The harness prints `machine:` at `:873`,
   before any work, and a line after each phase (`:148-153`). The log has neither, so harness stdout
   never reached it. LG-1839's "the harness prints at completion" is not what the script does. Lost in
   a block buffer on SIGTERM, or never captured: not determinable from here, the VM's `~/logs/s1/`
   being off. The correction is the lead's, through batch 11 (lead, 2026-11-05).
3. **The timed fit is 3.75 M rows, not 5 M.** `bench_gbm` fits `train`, `frame.head(int(rows * 0.75))`.
   A true reading at item L describes 3.75 M unless the harness or the reading scales it.
4. **The budget names a bigger machine than the reading's.** `00` NFR-456: "on a 16-core worker. GBM
   fitting: same data, 500 trees, < 20 min". `02:3257-3259`: "the 16-core machine these three
   requirements name … a dedicated run there settles all three, and nothing short of it does". The
   10:14:38 entry calls 8 vCPU "the environment of record"; no spec does. The plan's R3 requires only
   that the reading state it, as LG-1839 does.

None of this shows the fit is fast. **The expected form holds as far as it can be read**:
`gbm.py:858` `tree_method: hist`; `max_bin` unset (`_shared_params`, `:569-575`, passes hyperparameters
only); native categoricals by `enable_categorical`. Item L as accepted at 11:12:59 (`python -u`, stdout
and stderr captured, phases split, the fit read from its `timed` line or trees 500/500, never a kill,
the host stated) closes points 1 and 2. Its 8-vCPU reading is, by that ruling, "a LOWER BOUND on a
non-spec host", never pass/fail.

**Whose limb: answered from the records, on ruling (b) of 11:12:59.** Verbatim:

- `CR-754:162-163` (WK-661's close, the "Not delivered by WK-661" table, columns Requirement, Verdict,
  Owner):
  > `| NFR-475, -10 | **Measured by extrapolation** — 173 s of 600 s, 16.0 GB of 32 GB | The slice with a 16-core worker |`
  > `| NFR-476 | **Measured once, growth unmeasured** — 963 s of 1 200 s on an *assumed* linearity | Same |`
- `CR-1212:135`, under "`02` §9 (WK-690's expression kind)":
  > "NFR-476 has an expression limb with no measurement (`CR-754`:163 covers the builtin only)."
- `CR-1212` disposition (e), accepted 2026-09-28:
  > "(e) **WK-690 owns NFR-476, NFR-480, NFR-483 and NFR-484's expression limbs.**"
- Consistent with both: `PL-1268:206` (NFR-476: "Expression objective overhead ≤ 25 % versus the
  builtin") and `02:3257-3259` ("Owner: the slice that first has a worker resembling the 16-core machine
  these three requirements name").

**So `CR-754:163` carries NFR-476's fit limb to "the slice with a 16-core worker", and CR-1212 (e) gives
WK-690 the expression limb only.** Under ruling (b) of 11:12:59: **fit limb carried by `CR-754:163`; its
measurement on a 16-core host owed there.** WK-690's own NFR-476 limb is the expression limb, proven or
not by S2 item M. FD 8350 does not block this close.

**The carrier named an event, not a Work; the owner is now ruled.** No roadmap row is "the slice with a
16-core worker" (`git grep -n -iE '16-core|16 core'` over `docs/roadmap.md`, `docs/plans`, `docs/closures`,
`docs/rulings` and the register finds it only at `PL-750:107` and `PL-1735`, which quote the owner and
measure NFR-485, and WK-661 is closed). To-lead "2026-11-05 11:23:52 GMT" (2) rules it, verbatim: "FD 8350
and NFR-475's carry on the same CR-754:163 line are OWNED BY THE P2 CLOSURE RECORD's carry-forward list —
filed now as a dated carry line in batch 11 citing this entry ("carried to P3: the 16-core-worker
measurement; owner: the P2 closure record, maintainer-accepted at the P2 close; the §14 review proposes the
P3 Work that measures NFR-475 / NFR-476 on the spec's host"); the L reading on 8 vCPU is evidence for that
proposal, not a pass/fail."

**FR-1840 3c: two limbs.** "Can never queue ahead" is delivered and tested (§1). "Unaffected" is what
S1 read as UNMET. `objective_preview.py:46` is a thread pool, so it isolates queueing and not CPU within
one process; that is a reading of the code, not a proven cause. FR-1840 and `PL-1665` 5.7 call the
result diagnostic ("neither result fails the gate on its own"), which is why this is an FD by ruling
and not a gate failure. Its remedy is the §14 round's (10:20:03).

### §5. Every requirement without evidence, with a PROPOSED verdict

| Id | What is missing | PROPOSED §13 verdict |
|---|---|---|
| NFR-476 fit limb | a true fit time on a 16-core host (§4) | **reassigned**: not WK-690's; carried by `CR-754:163`, owned by the P2 closure record's carry-forward list ("2026-11-05 11:23:52 GMT" (2), §4) |
| NFR-476 expression limb | a full-shape ratio | **deferred with an owner: WK-690**, event S2 item M or S3. It blocks: a WK-690-owned limb, unmeasured |
| FR-1840 3c, p99 limb | the isolation (§4) | **deferred with an owner: WK-690**, event the §14 round's option; FD 8352 |
| NFR-480 | no marker; measured, met | **delivered**, evidenced outside the instrument |
| FR-366 | no marker; live half asserted under FR-166 and FR-367 markers (CR-1980 §5) | **delivered**, evidenced outside the instrument |
| FR-207 (WK-690's limb) | | **reassigned**: Phase 3, owner the maintainer, `RL-1362` DP-S3-5 |
| FR-147, FR-148 on a real `where()` | LG-1412 A10's runs, no marked expression test | **delivered but untested** for the expression kind |
| FR-174, FR-175, FR-177 expression-Factor limb | the diagnostic | **deferred with an owner: WK-1178 (P3)**, the 16:13:51 entry |

**The 09:51:05 rule on a WK-690-owned FD.** "Unmet → an FD owned by WK-690, resolved by fix or a named
carry at its close": a WK-690 owner cannot carry its own finding past its own close (CR-1980 §5b), so
FD 8352 needs a fix or a named carry before the user's line. FD 8350 leaves this Work by batch 11's dated carry
line (§4).

**The §5 retrofit-impossible list.** Nothing on it lands here (CR-1980 §5, unchanged).

### §5a. Binding plan-review conditions

CR-1980 §5a stands. Predicate `grep -l 'kind: review' docs/closures/*.md`, then `grep -c WK-690`, adds
only CR-1999, a one-line mention in another Work's audit, which binds nothing. CR-1907 does not name
WK-690. CR-1212 (e): NFR-480, NFR-483, NFR-484 met; NFR-476's expression limb **still owed** (§4).

### §5b. The owed list, generated

```text
Generated by `python3 scripts/register-owed.py WK-690` against `2f108b1e (`docs/wk690-fresh-close-2026-11-06`)`.
Mode: work item 'WK-690'. 3 owed row(s), 6 matched but excluded as opening with a resolution marker
- The `factors` table is not append-only at the database … (FD-1704's row)
- The two per-factor GBM diagnostics read the first source column of a Factor … (FD-1751's row)
- The grammar refusal's structure walk raises RecursionError … (FD-1842)
Excluded as opening with a resolution marker — verify:
- FD-1195, FD-1294, FD-1349, FD-1492, FD-1511, FD-1512
```

*(Titles shortened; the command reproduces the full output.)* `register-owed.py review`: **31 owed
rows**, 11 excluded.

| Row | Read by hand | PROPOSED |
|---|---|---|
| FD-1704 (`register.md:369`) | owner WK-1178; matched on "WK-690 S4" (F5) | **removed**: WK-1178's |
| FD-1751 (`:387`) | owner ~~WK-690~~ WK-1178; dated line re-dispositions it | **removed**: guarded, carried (§R 2, 2a) |
| FD-1842 (`:412`) | `***Resolved 2026-11-04***` mid-cell: the known defect | **removed**: discharged by #1425 (§1b) |
| FD-1195, FD-1294, FD-1349, FD-1492, FD-1511, FD-1512 | each opens "Resolved" | resolved, as CR-1980 read them |

**Corrected owed list: empty on the register at `2f108b1e`; FD 8352 joins it with batch 11.** FD 8350 is
owned by the P2 closure record's carry-forward list, not by WK-690.
A cross-check by owner cell (`grep -n WK-690 docs/findings/register.md`) adds FD-1619 (`:345`), owner
WK-1178, as CR-1980 read it. Filter by working id too: "8350" and "8352" appear in no register row.

### §5c. Workflow steps that cite this close's requirements

CR-1980's candidate predicate at `2f108b1e` prints 47 pairs (run against `c807a59d` here it prints 36;
CR-1980 wrote 37). The added pairs sit on batch 7's rewritten rows: `git diff c807a59d 2f108b1e --
docs/workflows/WF-00702-custom-objective-lifecycle.md | grep -c '^+|'` prints 7, and `WF-698` has no
commit in the range. Each of CR-1980's five disagreements, read to its end:

| Step | Now | Verdict |
|---|---|---|
| B1.4 (`WF-702:86`) | "on every settled edit", the parse is the backend's (FR-1840) | **still says it** |
| B1.5 (`:87`), §7 (`:173`) | corrected 16:03:37 | **still says it** |
| B4.2 (`:121`) | corrected 16:03:37 | **still says it** |
| C5 (`:137`), §7 (`:181`) | text names the round, the row count and `y`, `f`; the range is a structured attribute (FR-165) | **still says it** |
| §10 C first fit (`:219`) | the bound is for an `expression` objective (NFR-476) | **still says it** |

**Not re-read:** the 32 pairs CR-1980 found agreeing, which no commit since has touched except by batch
7's lines above (`git log c807a59d..2f108b1e -- docs/workflows/` for that file prints only `4df71cd7`).
**FR-145's clarification is consistent with B1.4 and §7.**

## Findings

No id is written here; each is the lead's to file.

- **F1 — SL-1275's closing acts are owed.** LG-1839's condition (2) is "closes only on the 5.7
  measurement", now taken. Owed, docs only: the row and LG-1839 `closed`. **LG-1839 records too little
  for 5.7:** `PL-1665` 5.7 asks the `LG-` for "the box load before and after each run, and the command
  verbatim"; the addendum gives one start load and the driver with "defaults otherwise". Both are in
  `itemB-run.log`, so a dated line can carry them. PROPOSED order: after item L, so the ledger closes once.
- **F2 — FR-207's move is still not in the WK-690 section** (`roadmap.md:1841`). A dated line owed.
- **F3 — the SL-1274 row still reads "MERGE-ACK: not yet given"** (`roadmap.md:1929`). A dated line owed.
- **F5 — `register-owed.py` matches an owner by text mention.** A process row owed, as CR-1980 proposed.
- **F6 (new) — `PL-1996` reads `status: draft`** though SL-1994 merged and closed. Every other WK-690
  plan reads `active`. A status flip owed, docs only.
- **F7 (new) — LG-1839's "the harness prints at completion"**, and the 10:14:38 reading built on it (§4).
  Corrected at 11:12:59; LG-1839's sentence and FD 8350's essay take dated lines in batch 11.
- **F8 (new) — `bench_gbm` times 3.75 M rows against a 5 M budget** (§4 point 3). FD candidate, or a
  line in FD 8350's essay: any budget comparison needs the row count the number was read at. `02:3249`'s
  14.45 s basis needs the same check; whether its "75 000 rows" was the frame or the fit was not
  established here.
- **F9 (new) — NFR-476's fit limb and NFR-475 had a carrier with no Work** (§4). Ruled at 11:23:52 (2);
  batch 11 files the carry line. Re-test at the mint that it is on main.

## Replan check (`CLAUDE.md` §14, `RFC-1248`)

1. **Completion — no.** The deliverable set is CR-1980's; SL-1994 added no id.
2. **Omission — yes.** S2 carries L and M, and nothing yet carries FD 8352's option.
3. **Skills and research — yes.** A timed harness's output capture (`python -u`, a capped run yields a
   rate): a batch 11 process row. It moves no scope.
4. **Drift — yes.** NFR-476's budget note rests on an unmeasured extrapolation (`02:3249-3259`), and
   FR-1840's "shared box" wording predates the dedicated VM. Neither moves a slice yet.
5. **Shape — no.** No phase boundary or Work scope moved: the fit limb was never WK-690's, so naming that
   is a correction of a ruling, not a move.

`register-owed.py review` at `2f108b1e`: **31 owed rows** (11 excluded).

**Triggers:**

- A phase boundary or Work scope moved: **not fired**.
- An exit criterion at risk: **fired**. G1 needs WK-690 closed by the user's dated line; S2 item M and
  FD 8352 hold it. G4's carry for the fit limb is ruled (F9). To-lead 11:23:52 (3)(f) confirms the §14 full
  review of Mon 16 Nov 2026 as the response to WK-674's fired trigger.
- A replan decided: **not fired yet**. The §14 round of the 10:20:03 entry is conditional.
- A finding that moves a slice or a phase: **not fired**; carrying FD 8352 to P3 would fire it.

**PROPOSED:** no separate full review now: 10:20:03 already routes FD 8352 to the §14 round, and the
review before the P2 exit demo is fixed. Decide after item M. **The verdict is the lead's.**

## Verdict

PROPOSED: **NOT CLOSE-READY at `2f108b1e` + S1 records.** CR-1980's own blocks are discharged or
carried: FD-1842 fixed, FD-1751 guarded and carried, 5.7 measured, a fresh gate standing on a tree with
every WK-690 squash, the §5c steps corrected. SL-1994's audit is proposed CLEAN (§1b). **The close is
blocked by:**

1. **NFR-476's expression limb**, WK-690's own and unmeasured: S2 item M, else S3.
2. **FD 8352** (FR-1840 3c, MEDIUM): a fix or a named carry, from the §14 round.
3. **Docs closing acts**: SL-1275 and LG-1839 (F1), F2, F3, F6.

**FD 8350 (MEDIUM, as re-ruled 11:12:59) does not block it**: the fit limb is carried by `CR-754:163`, its
measurement on a 16-core host owed there, and owned by the P2 closure record's carry-forward list
("2026-11-05 11:23:52 GMT" (2); batch 11 files the line, F9).

The §5 verdicts are proposals. **The close itself is the user's dated line.** The WK-690 row reads
"fresh close audit filed (CR 8314, re-testing CR-1980), acceptance owed" until then. This draft's PR
waits for S2's readings; a dated delta line then carries M, L as information, and the rest.
