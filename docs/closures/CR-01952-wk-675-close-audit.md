---
id: CR-1952
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-675 Work close audit — DAG designer, rate table editor, quote sandbox and compare, dislocation views, rating version list and regression suite view
status: active                  # write-once; this is the only value this family ever takes
created: 2026-10-26   # drafted 2026-10-26 under working id 8261
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: 1e0a8abbc90723ae9c887a901f700b72f6f94cc1
phase: P2
work: WK-675
corrected_by: []
relates: [PL-1286, PL-1546, PL-1927, RL-1900, RL-1909, CR-1907, FD-1283, FD-1284, FD-1437, FD-1585, FD-1652, FD-1656, FD-1936]
---

# CR-1952 — WK-675 Work close audit

*Working id CR-1952, reserved by the lead; it mints at the lead's id turn. The auditor seat
aud-wk675 wrote this record on 2026-10-26 from 10:36 GMT, on the user's instruction relayed by
the maintainer in `~/gi-pricing-plan.local/channel/to-lead.md`, entry "2026-10-26 10:33:40 GMT —
Maintainer: INSTRUCTION (the user's, 10:3x GMT) — run the WK-675 close audit now". It follows
`.claude/skills/close-workstream`, `CLAUDE.md` §13 and §14.*

**What this record is.** It gathers evidence and **proposes**. Every §13 verdict below is
written "PROPOSED" and is the lead's to give. **The close is the user's dated acceptance line.**
This record does not close WK-675, and the roadmap row it edits says "close audit filed,
acceptance owed".

**Object.** `origin/main` at `1e0a8abbc90723ae9c887a901f700b72f6f94cc1` (tree
`a53558a662ff73d6dd36aa07044b5b2c9e0f2238`). Every `file:line` and every count below is at that
tree unless it names another. Branch `docs/wk675-close-audit-2026-10-26`, cut from that commit.

## Scope

### §0. The requirement set, derived from the documents before any evidence

**Predicate** (runnable from the repository root at `1e0a8abb`). The union of the ids cited by
the WK-675 roadmap section (`docs/roadmap.md:1286`, up to the next `### WK-` heading at `:1685`),
`PL-1546` and `PL-1927`:

```bash
( sed -n '1286,1684p' docs/roadmap.md
  cat docs/plans/PL-01546-wk-675-slices-5-to-11-work-plan-delta.md \
      docs/plans/PL-01927-wk-1178-open-high-findings-s1a-s1b-fd-1729-split-s2-fd-1610-limb-2-s4-fd-1754-gbm-factor-read-plan-delta.md
) | grep -ohE '\b(FR|NFR)-[0-9]+\b' | sort -u -V
```

It prints 51 ids. Three are added, each with its source:

- **FR-1903** and **FR-1932**: appended to `03` by S10 and S11 (spec first, after the plans were
  filed). The brief names both.
- **FR-214**: the predicate misses it. `PL-1286`'s view table names it for the DAG designer
  (`docs/plans/PL-01286-…-map-plan.md:167`). It is the only id in that table that the
  predicate does not print.

The slice plans `PL-1764`, `PL-1833` and `PL-1937` also cite FR-440, FR-26, FR-1397, FR-1398,
FR-1399 and FR-1607. They are kept in the run below as a widening check.

**Assigned elsewhere, kept out of WK-675's verdicts:** `PL-1927` is WK-1178's plan. It names
`SL-1552` and `SL-1553` only for serialisation (`PL-1927:347`, `:356`). Its ids FR-44, FR-222
(the WK-1178 S4 limb), FR-239, FR-240, FR-447 and NFR-499 are WK-1178's. FR-10 and FR-21 are
cited by the WK-675 section as context, not as deliverables. `PL-1286` (`:206-222`, `:315-317`,
`:409`, `:434-446`) names FR-146,
FR-216, FR-224, FR-236 to FR-243, FR-245, FR-250, FR-253, FR-254, FR-257, FR-259, FR-267 to
FR-273, FR-276, FR-401, FR-402, FR-432, FR-433, FR-438, FR-443, FR-444, FR-446, NFR-461,
NFR-526, NFR-527, NFR-530, NFR-533 and NFR-536 as **not this Work's**, each with its owner.

**Requirements axis.** `scope-audit.py` takes one module per run, so it ran four times. The
script is not a `run-heavy.sh` command (`--light` refuses anything but `audit-docs.py` and
`doc-index.py`, rc 78), so it ran directly under `nice -n 19`, through the `tools-main` venv,
with the paths in this worktree:

```bash
uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py RATE --sections NONE \
  --extra FR-212,FR-213,FR-214,FR-215,FR-217,FR-218,FR-219,FR-220,FR-221,FR-222,FR-223,FR-225,FR-226,FR-227,FR-228,FR-229,FR-230,FR-231,FR-232,FR-233,FR-234,FR-235,FR-239,FR-240,FR-241,FR-244,FR-246,FR-247,FR-248,FR-249,FR-251,FR-252,FR-255,FR-256,FR-258,FR-260,FR-261,FR-262,FR-263,FR-264,FR-265,FR-266,FR-1186,FR-1221,FR-1397,FR-1398,FR-1399,FR-1607,FR-1903,FR-1932,NFR-499 --endpoints
uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py OVR  --sections NONE --extra FR-10,FR-21,FR-24,FR-25,NFR-463
uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py DATA --sections NONE --extra FR-26,FR-44
uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py PLAT --sections NONE --extra FR-440,FR-447
```

`--sections NONE` selects no section, so only the `--extra` ids are in scope.

| Run | In scope | With a `@pytest.mark.req` marker | No marker | rc |
|---|---|---|---|---|
| RATE | 51 | 49 (96%) | FR-1186, FR-1903 | 1 |
| OVR | 5 | 2 (40%) | FR-24, FR-25, NFR-463 | 1 |
| DATA | 2 | 2 | — | 0 |
| PLAT | 2 | 2 | — | 0 |
| **Total** | **60** | **55** | **5** | |

WK-675's own deliverable set is **46 ids**, the rows of §1's table: 43 `03` ids plus FR-24,
FR-25 and NFR-463. That is the 60 above less 14 ids. Eight of them are context or another Work's:
FR-10, FR-21, FR-44, FR-239, FR-240, FR-241 (FR-1903's effective-date source), FR-447 and NFR-499.
The other six are the widening ids FR-26, FR-440, FR-1397, FR-1398, FR-1399 and FR-1607, each
with a marker. FR-222 stays in, because its WK-1178 limb shares the id. The WK-675 row carries no count to reconcile against. `docs/roadmap.md:3359` reads
"≈ 67 `RATE`" for the whole phase, which is a planning figure, not this Work's count.

**Endpoints axis.** `scope-audit.py RATE --endpoints`: "declared: 45, published: 45 (100%) —
every declared endpoint is published in the contract".

**Catalogue axis.** `03` declares no catalogue in the form the script reads: `grep -cE '^\|
`[A-Z]{2,4}-[A-Z]{2,4}-[0-9]+` [a-z0-9-]+' docs/specs/03-rating-engine.md` prints `0`. Nothing
to compare.

**§0a and §0b.** `scope-audit.py` sees backend markers only. WK-675 is a frontend Work, so a
backend marker evidences the backend limb at most. The view limb is read from the vitest files
in §1, by assertion, not by marker.

## Evidence

### §1. Each deliverable: exists and works

The slices on main, every one an ancestor of `1e0a8abb` (`git merge-base --is-ancestor <sha>
1e0a8abb` rc 0 for all 14):

| Slice | What | Squash (PR) | Ledger, status at `1e0a8abb` |
|---|---|---|---|
| SL-1369 S1 | ChartFigure column descriptors (NFR-463) | `52940524` (#1079) | LG-1378 closed |
| SL-1477 S2 | Designer I: canvas, inspector, load and save | `75f8a7b4` (#1245) | LG-1532 closed |
| SL-1557 S3 | Designer II: live validation, diff | `99f22479` (#1271) | LG-1606 closed |
| SL-1559 S4 | Editor I: grid, manual edit | `372fa92a` (#1281) | LG-1635 closed |
| SL-1639 | FD-1611 fix | `71c7cbd1` (#1283) | LG-1640 closed |
| SL-1548 S6 | Sandbox: form, ladder waterfall, trace | `604ea084` (#1291) | LG-1673 closed |
| SL-1549 S7b | compare backend `own_change` | `a3fc2e8d` (#1301) | LG-1699 closed |
| SL-1550 S7 | Sandbox compare view | `8cfa1c96` (#1330) | LG-1778 closed |
| SL-1547 S5 | Editor II: diff shading, bulk, CSV | `9c3e737e` (#1334) | LG-1786 closed |
| SL-1551 S8 | Dislocation views | `034781b3a3bd1031c02a08dab5b6dc002d963cb6` (#1372) | LG-1867 **active** |
| SL-1554 S9 | Designer III: sub-graph mounting | `ef3ac6c8a7fde1559ee3f907e5340f6697d5a552` (#1384) | LG-1881 **active** |
| SL-1552 S10 | Rating version list | `85eac5b29bef93d90d3107abc72adf5126d013c8` (#1388) | LG-1902 **active** |
| SL-1553 S11 | Regression suite view | `866cec47e446eec7f9ccba7cc9e318d6c831ef11` (#1396) | LG-1933 **active** |
| SL-1938 | FD-1936 fix: no blank parent port name | `8f5aead6a826f9dbb82589cee0e5b355ab9f49ed` (#1397) | LG-1939 **active** |

Moved to Phase 3 by dated lines, not missing: S12 Deployments (`docs/roadmap.md:1304`, 2026-10-03),
S13 Jobs and S14 Job detail (`:1306`, 2026-10-08).

**The five lane-C slices are merged and verified on main, but their records still read `active`.**
The roadmap rows `SL-1551`, `SL-1552`, `SL-1553`, `SL-1554` and `SL-1938` read `status: active`,
and so do their ledgers. LG-1902 and LG-1933 read "MERGE-ACK: not yet", and LG-1939 "not yet
given". The maintainer's entry "2026-10-25 18:59:00 GMT" says that SL-1554 "closes on this merge".
LG-1939 also has no `slice:` field, and its file name still carries working id 8250. The slice
closing acts are the auditor's (`auditor.md`, "sets the `LG-` and the `SL-` row `closed`"). This
record does not do them, because the brief permits no other roadmap edit. **They are owed** (see
the owed list).

**The view limb, by requirement.** The view and component are read at `1e0a8abb`, and the assert
lines are read for the test cited. An evidence-collector subagent gathered this table. The
auditor re-read FR-230 and the FD-1936 asserts.

| Id | View / component | Backend it consumes | Test, and what the assert checks |
|---|---|---|---|
| FR-212 | `RatingDesignView.vue:82`; `dag/useGraphValidation.ts` | `api/rating_algorithms.py:35`, `:65` | `DagDesignerValidation.test.ts:29-43`: an unresolved name shows on its node and save is not called. **Gap:** no UI test of an on-node cycle or orphan. |
| FR-213 | `sandbox/QuoteForm.vue:3`; `quoteForm.ts:4-41` | `api/score.py:547` | `QuoteSandboxView.test.ts:139-143`: one control per declared input. `StepInspector.test.ts:30-40`: a bound is sent as a string. |
| FR-214 | `StepInspector.vue:577` (output step) | save | Backend only. **Gap:** no UI reference to the declared outputs (`payable_premium_minor`, ladder). |
| FR-215 | `StepInspector.vue:115` | save | `StepInspector.test.ts:43-49`: `step_id` is read-only, and a relabel keeps the id. |
| FR-217 | `DagDesigner.vue:83-110`; `MountInspector.vue:49-151`; `api/subGraphs.ts:10` | `api/sub_graphs.py:32`, `:54`, `:71` | `MountInspector.test.ts:57-64`: the options are exactly the pins. `DagDesignerMounts.test.ts:137-150`: a mount is added and saved. |
| FR-218 | `MountInspector.vue` purposes (~`:60-70`) | `api/sub_graphs.py` | `MountInspector.test.ts:39-55`: no purposes when none is checked, and canonical order. The authoring view is the purposes control. |
| FR-219 | `dag/DiffOverlay.vue:48` | `api/rating_algorithms.py:78` | `DiffOverlay.test.ts:59-67`, `:99-110`: removed, added and changed markers. |
| FR-220 | StepInspector table step | save | `StepInspector.test.ts:52-59`: the options are exactly the two pins, with no free text. |
| FR-221 | `StepInspector.vue:80`, `:307` | save | `StepInspector.test.ts:62-82`: `as_at` is required, with two options. |
| FR-222 | StepInspector mode flag | save | `StepInspector.test.ts:98-113`: the flag names both modes. |
| FR-223 | `StepInspector.vue:479`, `:487` | compile path | `StepInspector.test.ts:116-127`: a new `model_call` takes the version's mode. `test_rating_mode_mismatch_api.py:45-69`: the compile Job fails with the named code. Save is 201 (`:54`), per RL-1438. |
| FR-225 | `StepInspector.vue:549` | save | `StepInspector.test.ts:130-135`; `RatingDesignView.test.ts:124-137`: save is blocked. |
| FR-226 | `StepInspector.vue:577`, `:599` | save | `StepInspector.test.ts:138-155`: the exact rounding options, dp default 0. |
| FR-227 | server validate only | `platform/rating_algorithms.py:389` | Backend `test_rating_algorithm_validate.py:127-137`. **Gap:** no UI test of a type mismatch on a node. |
| FR-228 | `rating/RateTableGrid.vue:3`, `:5`, `:20` | `api/rate_tables.py:452`, `:465` | `RateTableGrid.test.ts:27-42`: the column order, and the value last with its unit. |
| FR-229 | `RateTableEditorView.vue:7` | `api/rate_tables.py:142` | `RateTableEditorView.test.ts:110-123`: save is disabled until an edit and a non-blank note. |
| FR-230 | diff vs seed, `RateTableDiffPanel.vue:145` | `api/rate_tables.py:100` (seed) | **No frontend caller of seed-from-model** (`git grep -n -i -E 'seed-from-model\|seedFromModel\|seed_from_model' -- frontend/src`, excluding `generated/`, prints nothing). **No frontend test names FR-230.** |
| FR-231 | `RateTableDiffPanel.vue:4`, `:25`, `:145`; `diffShading.ts:2` | `api/rate_tables.py:389`, `:488` | `RateTableDiffPanel.test.ts:51-57`: against previous by default, "+5.0000%". |
| FR-232 | `RateTableEditorView.vue:76` | `api/rate_tables.py:465` | `RateTableEditorView.test.ts:93-106`: a cursor page, Next is disabled at the end. |
| FR-233 | `rating/BulkOperationDialog.vue:3`, `:6` | `api/rate_tables.py:183` | `BulkOperationDialog.test.ts:34-45`: the percentage is sent as a string. |
| FR-234 | `DecimalCellInput.vue:6`, `:12` | `api/rate_tables.py:142` | `RateTableEditorView.test.ts:155-180`: a 422 marks the cell `aria-invalid`. Coverage and duplicates are server-side only. |
| FR-235 | `RateTableImportExport.vue:3` | `api/rate_tables.py:222`, `:250`, `:286` | `RateTableImportExport.test.ts:43-78`: the export body, the preview creates nothing, create after confirm. |
| FR-244 | StepInspector `expr` | save | `StepInspector.test.ts:156-165`. The grammar refusal is server-side. |
| FR-246 | none (a server rule) | save | Backend `test_fremtpl2_algorithm.py:191-288`. A rule with no view limb. |
| FR-247 | `sandbox/LadderWaterfall.vue:3`; `QuoteSandboxView.vue:160` | `api/score.py:547` | `LadderWaterfall.test.ts:28-36`: every rung drawn. `ladder.test.ts:15-27`. |
| FR-248 | `ladder.ts:21`, `:53` | `api/score.py:547` | `ladder.test.ts:25-27`: the operands as sent. |
| FR-249 | `QuoteOutcome.vue:73` | score | `QuoteSandboxView.test.ts:204-208`: "not available" (shown absent under OQ-1460, R6.1). |
| FR-251 | `QuoteForm.vue:69`; `api/score.ts:9`, `:18` | `api/score.py:547` | `QuoteSandboxView.test.ts:150-158`: `purpose: "what_if"` and the explicit ref. |
| FR-252 | `LadderWaterfall.vue:6` | score | `LadderWaterfall.test.ts:28-42`: `instalment_loading` present or omitted. |
| FR-255 | `sandbox/QuoteError.vue:3` | score | `QuoteSandboxView.test.ts:188-201`: a typed refusal, and a client-side whole-number check. |
| FR-256 | `QuoteOutcome.vue:4`, `:6` | score | `QuoteSandboxView.test.ts:168-175`: declined, with reasons and no alert. |
| FR-258 | `sandbox/TraceTimeline.vue:3` | `api/traces.py:79` | `TraceTimeline.test.ts:27-40`: each step in order, with its values. |
| FR-260 | `RegressionSuiteView.vue:188-198` | `api/models.py:1325`, `:1400` | `RegressionSuiteView.test.ts:136-150`: the pass/fail rows and the money diff. **No frontend test names FR-260.** |
| FR-261 | `RegressionSuiteView.vue:234-247` | `api/models.py:1400` | `RegressionSuiteView.test.ts:186-226`: the counterexample, "unminimised", and `MONOTONE_NO_COMPARABLE_PAIRS`. **No frontend test names FR-261.** |
| FR-262 | `sandbox/QuoteComparison.vue:3`; `api/score.ts:37` | `api/score.py:647` | `QuoteSandboxView.test.ts:224-276`: the picker excludes the version in view, both refs are sent, and the per-side error. |
| FR-263 | `dislocation/ChangeHistogram.vue:3`, `LargestMovers.vue:3` | `api/dislocation_runs.py:94`, `:140`, `:186` | `dislocation.test.ts:42-53`; `DislocationView.test.ts:58-90`. |
| FR-264 | `dislocation/SegmentGrid.vue:3`, `:5` | run payload | `dislocation.test.ts:67-79`. |
| FR-265 | `DislocationView.vue:4`; `router/index.ts:268` | `api/dislocation_runs.py:94`, `:140` | `DislocationView.test.ts:58-81`: the run is cited by id. |
| FR-266 | `dislocation/AttributionWaterfall.vue:3` | run payload | `dislocation.test.ts:101-135`: the isolated and cumulative values. |
| FR-1186 | none (a rule: no status) | none | `RateTableEditorView.test.ts:201-205`: a negative regex over the container text. No marker. |
| FR-1221 | `api/regressionRuns.ts:27` | `api/models.py:1401`, `:1418` | `RegressionSuiteView.test.ts:248-256`: GET only, no `/cases`. |
| FR-1903 | `RatingVersionListView.vue:15-29`, `:45-74`, `:196-213`; `router/index.ts:249-256` | `api/models.py:1112`; `api/environments.py:39` | `RatingVersionListView.test.ts:121-325`: grouping, DP-S10-4 order, badges across pages, 403, failed page, page cap. No marker. |
| FR-1932 | `RegressionSuiteView.vue:51-55`, `:141-146` | `api/models.py:1359`, `:1400` | `RegressionSuiteView.test.ts:136-184`, `:258-280`; backend `test_regression_runs.py:549-632`. **Gap:** the truncated notice and the 10-page cap are untested. |
| FR-24 exception | `dag/useGraphValidation.ts:10` | `api/rating_algorithms.py:65` | `DagDesignerValidation.test.ts:29-57`; `useGraphValidation.test.ts:38-54`. |
| FR-25 | `router/index.ts:249`, `:282`, `:294` | none | `router/__tests__/reachability.test.ts:64-88`: `unreachable == []` and `dead == []`. |
| NFR-463 | `ChartFigure.vue:3` and the chart components | none | `dislocation.test.ts:48-53`, `:109-113`; `LadderWaterfall.test.ts:45-49`. See §4. |

**PL-1546 Acceptance, run as written:**

- **Item 2** (`git grep -l 'PL-1546' -- docs/ledgers`) prints 10 ledgers: one for each of the 8
  rows, plus LG-1640 and LG-1939. Four of the 8 row ledgers are **not closed** (LG-1867, LG-1881,
  LG-1902, LG-1933). The plan's Goal is "each … has closed on its own `LG-`", so it is **not met
  at `1e0a8abb`**.
- **Item 3** (`grep -rlE '<id>[^0-9]' frontend/src --include=*.test.ts` per row id). It prints
  **0 files for FR-230, FR-260, FR-261, FR-217 and FR-218**, and at least 1 file for each of the
  other 22 ids the rows list. So **item 3 is not met for 5 ids.** For FR-217, FR-218, FR-260 and
  FR-261 the behaviour is tested (table above) by tests that do not name the id.
- **Item 5** (an `accessibility-tester` report quoted in the LG of a slice that adds a chart):
  `grep -c -i 'accessibility-tester\|accessibility review'` gives LG-1786 1, LG-1867 1, LG-1902 2,
  LG-1933 2 and LG-1673 0. LG-1933's hits are the plan line and "Owed: … the accessibility review
  (task 7)" (`:116`). **S6 (LG-1673) adds the ladder waterfall chart, and its LG quotes no
  report.** S11's review is recorded as owed and never as done.
- **Item 7** (`own_change: false` is never rendered as "unchanged"): met.
  `components/sandbox/__tests__/QuoteComparison.test.ts:95` and `:105` assert
  `queryByText(/unchanged|not edited/i)` is `null` on the row.

### §2. The gate

**Gate of record per slice.** The sha is the gated head. The run ids are PR CI on the PR's head,
read back with `gh run view <id> --json conclusion,headSha` at 10:4x GMT today.

| Slice | Gate of record (LG) | PR CI on the PR head, all `success` |
|---|---|---|
| SL-1551 (#1372) | `47faad82`, tree `b682a918…`, gate-1b, pytest `14 failed, 6688 passed` = the 13 docs-audit set + 1 (LG-1867:95), STANDS | `d5994fb2`: python 40198787986, frontend 40198787917, docs 40198787852, history-policy 40198787935 |
| SL-1554 (#1384) | `11c3db18`, STANDS under 1(f) (to-lead "2026-10-25 14:19:54 GMT"). **LG-1881 has no gate-of-record line**: its last gate note says "the full gate is still owed" (`:65`) | `d5c3d7f0`: python 40221003975, frontend 40221004020, docs 40221004141, history-policy 40221003966 |
| SL-1552 (#1388) | `6975e2be`, tree `551abc3b…`, pytest `14 failed, 6781 passed` = 13 + the FD-1920 isolation defect, STANDS with a named exception (LG-1902:85-89; to-lead "2026-10-25 19:28:31 GMT") | `d16dedbc`: python 40237029675, frontend 40237029712, docs 40237029658, history-policy 40237029663 |
| SL-1553 (#1396) | `57bf2fbb…`, pytest `13 failed, 6899 passed` (the 13), **mypy.rc=1** (`regression_runs.py:125`, two `tuple_` arg-type errors), fixed at `eb269d53` under the extended exception (to-lead "2026-10-26 01:14:30 GMT"; LG-1933:93) | `e6f8292c`: python 40267039303, frontend 40267038673, docs 40267038693, history-policy 40267038681 |
| SL-1938 (#1397) | `40ca2645`, pytest 13 failed (the 1(f) set), STANDS under 1(f) (to-lead "2026-10-26 02:23:16 GMT"; LG-1939:63) | `fe3bee61`: python 40273091823, frontend 40273091735, docs 40273091850, history-policy 40273091862 |
| S1–S7, SL-1639 | closed on their own slice audits; each gate line is in its closed LG (LG-1378:94, LG-1532:375, LG-1606, LG-1635, LG-1786:49, LG-1673:86, LG-1699:54, LG-1778:93, LG-1640:39). Not re-derived here | — |

**Fresh full gate: OWED** — gate-1b after S1b's END, paired under the isolated template; head =
the head of this record's branch at that time. The lead runs it. This audit ran no test, no
build and no gate (the brief's ban: S1b's gate holds gate-1).

**Retry counters** (`write_runtime_state.py show`): no entry for any WK-675 slice. The
`retry_counters` block was last written at `2026-10-05T13:09:09Z`, before S5 to S11 ran. So
"none recorded" here is not evidence of a clean first pass.

### §3. New checks proven on broken input

Ancestry: `git merge-base --is-ancestor <red> <PR head>` rc 0 for every red commit below.

| Check | Red commit, and the red line | Reaches the PR head |
|---|---|---|
| FD-1936's mount refusal (SL-1938), `model_schema/rating.py:709-730` | `4290018b`: `3 failed, 10 passed` rc 1. FAILED `test_an_input_port_mapped_to_a_blank_name_is_refused_naming_the_port[]` and `[  ]`, because the message named `''` and not the port (LG-1939:53). The asserts (`test_graph_invariant_issues.py:181-184`) pin the code, the step, the port name and the absence of the old message. The UI limb's broken input: `setInput` changed to delete on `""`, `1 failed \| 8 passed`, reverted (LG-1939:57) | `fe3bee61`, rc 0 |
| The regression-run list's typed cursor (SL-1553) | Backend `892a2f74`: `4 failed, 1 passed, 13 deselected`, because "the four list tests answer 405" (LG-1933:114). **This red is by absence of the route, not by cause of the cursor check.** `test_a_cursor_that_is_not_a_run_of_this_version_is_a_400` (`test_regression_runs.py:607-621`) has never been shown failing with the route present and the cursor check broken. Model-schema `c07ad757`: "1 failed, 26 passed" (ImportError, by absence). Frontend: red at `bb564bdb` plus the uncommitted test, committed `da819fde`: `Tests 1 failed \| 15 passed (16)`. The truncated branch of `listRegressionRuns` (`REGRESSION_RUN_PAGE_CAP`, `api/regressionRuns.ts:16`) has no test | `892a2f74`, `c07ad757` and `bb564bdb` all reach `e6f8292c`, rc 0 |
| FR-1903's list guard (SL-1552): "unknown is never not live" (`RatingVersionListView.vue:15-29`; `api/paging.ts:21-55`) | `6968bba2`: `Test Files 1 failed (1)` / `Tests 10 failed (10)`, cases (a) to (f) (LG-1902:65). DP-S10-4 `05c151f2`: `2 failed \| 9 passed`. Reachability `fff804c9`: `1 failed \| 2 passed`, "expected […] to include '/rating'" (LG-1902:71). The 403, failed-page and page-cap asserts are `RatingVersionListView.test.ts:212-246` | `d16dedbc`, rc 0 for all three |

PROPOSED: the typed cursor's own refusal is **delivered but not proven on broken input**. One
mutation run is owed: break the `(finished_at, id)` check or the version filter at
`platform/regression_runs.py`, and show `:607` red. It needs a DB window, which is the lead's to
grant.

### §4. NFRs

The WK-675 section's NFR clause names **one NFR: NFR-463**. The predicate `grep -n 'NFR'
<the section>` hits only the SL-1369 heading and title. The brief's walk:

| NFR | Whose | State |
|---|---|---|
| NFR-463 (WCAG 2.2 AA; every chart has a table) | WK-675 | **Not measured as a whole.** The tabular-equivalent half is mechanised: the `ChartFigure` descriptor form, with `vue-tsc` checking each accessor against the row type (S1), and table asserts per chart (§1). The WCAG 2.2 AA half has only per-slice `accessibility-tester` static reads (LG-1786, LG-1867, LG-1902), none for S6 or S11, and no browser or screen-reader run. PROPOSED: **deferred with an owner**. One `accessibility-tester` pass over the six P2 views on the exit tree, owner WK-675, before Thu 2026-11-12. Or "measured" is accepted as the static reads plus the vitest table asserts, which is the lead's call. |
| NFR-454, NFR-489 (scoring p99 per replica) | WK-674 / WK-1178 (`SL-1259`, `SL-1455`; `roadmap.md:1283`, `:2168`) | Not cited by the WK-675 section, PL-1546 or PL-1927 (the §0 predicate). Deferred to `nfr-bench-1` (Thu 30 to Fri 31 Oct) under their own owners. Not this close's. |
| NFR-1443 (cells-diff paging p95 ≤ 300 ms), the route S5 consumes | WK-1178 `SL-1736` (`roadmap.md:2756`) | Not WK-675's. Measured DIAGNOSTIC there. |
| NFR-499 | WK-1178 (PL-1927) | Assigned elsewhere. |
| Dislocation-view budgets | — | `03` has no NFR row on the dislocation views. The predicate is `grep -nE '^\| \*\*NFR-[0-9]+\*\*' docs/specs/03-rating-engine.md \| grep -i dislocation`, which prints nothing. The dislocation run's compute is WK-673's. |

### §5. Not delivered: every requirement without evidence, with a PROPOSED verdict

| Id | What is missing | PROPOSED §13 verdict |
|---|---|---|
| FR-1903 | no `@pytest.mark.req` marker. The view is tested in vitest (§1), and the backend list route is tested at `test_rating_versions.py:191-218` without the FR-1903 marker | **delivered, evidenced outside the instrument**. No verdict is needed. A marker on `test_rating_versions.py:191` would make it visible (§0a). **LEAD VERDICT (to-lead 10:54:44 adopted): delivered** (vitest asserts, outside the marker instrument) |
| FR-1186 | a rule with no view, tested only by a negative regex (`RateTableEditorView.test.ts:201-205`), which passes on any view that lacks those words | **delivered but untested** (no test can fail if a status appears under another word). Owner WK-675, or accept at the P2 close. **LEAD VERDICT (to-lead 10:54:44 adopted): delivered but untested** (the negative-regex test cannot fail). Owner WK-675 |
| FR-24 | an `00` documentation rule. WK-675's part is its "on-node live validation" exception, which is tested | **delivered**. FR-24 is otherwise a docs rule with no WK-675 deliverable. Reassigned to no Work. **LEAD VERDICT (to-lead 10:54:44 adopted): delivered** (on-node live validation tested; otherwise a docs rule) |
| FR-25 | no marker. `reachability.test.ts:64-88` asserts it statically | **delivered, evidenced outside the instrument**. **LEAD VERDICT (to-lead 10:54:44 adopted): delivered** (vitest asserts; outside the marker instrument) |
| NFR-463 | see §4 | **deferred with an owner** (WK-675), or the lead accepts the static evidence. **LEAD VERDICT (to-lead 10:54:44 adopted): deferred with an owner: WK-675**, one `accessibility-tester` pass over the six views by Mon 3 Nov 2026 (before the docs freeze); the measurement lines go into the CR addendum |
| FR-230 (view limb) | no frontend seed action, and no test names FR-230 (PL-1546 item 3) | **delivered but untested** for diff vs seed (`RateTableDiffPanel.vue:145`). The seed action itself has no view: **not started** if the lead reads FR-230 as owing one, or reassigned to no view if the lead reads it as API-only (WF-699 A2 seeds over HTTP). **LEAD VERDICT (to-lead 10:54:44 adopted): by limb, against PL-1546's FR-230 row quoted verbatim in §5d.** Diff-vs-seed: **delivered but untested**, owner WK-675. Seed action: **reassigned** to the owner of the seed endpoint (the API), because the quoted row assigns WK-675 no seed view. See §5d |
| FR-214, FR-227, FR-212 on-node cycle and orphan display | the UI shows no declared outputs. Type mismatch and cycle on a node are untested in the UI | **delivered but untested** (the UI limb), owner WK-675. **LEAD VERDICT (to-lead 10:54:44 adopted): delivered but untested** (FR-214, FR-227, FR-212 on-node display; the UI limb) |
| FR-1932 truncated notice and page cap | no test | **delivered but untested**, owner WK-675. **LEAD VERDICT (to-lead 10:54:44 adopted): delivered but untested** (truncated notice and page cap) |
| FR-217 / FR-218 / FR-260 / FR-261, by name | the behaviour is tested, but no frontend test names the id (PL-1546 item 3) | **delivered**. Item 3 is not met as written: one comment line per test, or the lead accepts. **LEAD VERDICT (to-lead 10:54:44 adopted): delivered.** PL-1546 item 3 is not met by name, so it goes to the owed list (§5b, owed row 1) |

**The §5 retrofit-impossible list.** WK-675 is a frontend Work, and `docs/roadmap.md` §5's items
are invariants it consumes. "No hand-written API shape": `frontend/src/api/generated` is
generated, and the docs and frontend CI ran green on every lane-C PR head (§2). Nothing on the
list lands here.

### §5a. Binding plan-review conditions

| Condition | The artifact it demands | Where it is at `1e0a8abb` |
|---|---|---|
| PL-1546 Acceptance 2: each slice closed on its own LG | 8 closed LGs | 4 of 8 **not closed** (§1) |
| PL-1546 Acceptance 3: a test names each FR | a vitest file per id | **5 ids with none** (§1) |
| PL-1546 Acceptance 5: an `accessibility-tester` report in the LG of each slice that adds a chart | a quoted report | **S6 has none. S11's is recorded as owed** |
| PL-1546 Acceptance 8: the gate is green per slice | the gate of record | Every slice's gate STANDS by a ruling (§2). **SL-1554's is not in its LG** |
| PL-1927 (lane C rows) | serialisation only | No WK-675 obligation (`:347`, `:356`). Nothing owed |
| RL-1900 DP-S11-1 (a): `RegressionRunSummary`, newest first, cursor-paginated; the view opens the newest, takes `?run=`, marks the evidence run | FR-1932, code, tests | **Met**: `packages/model-schema` `RegressionRunSummary` (red `c07ad757`), `api/models.py:1359`, `RegressionSuiteView.test.ts:136-184`, backend `test_regression_runs.py:549-632` |
| CR-1907 E6: RL-1909 closes OQ-1901, the cap of 500 goes into `03` §5.1, the mirrors are struck, and the gate row is recounted | four edits (RL-1909 "What it obliges" 1 to 4) | **Not applied.** RL-1909's own acceptance predicate, `grep -n "RL-1909" docs/specs/03-rating-engine.md`, prints **0 lines** (it needs 2). OQ-1901 reads **OPEN** at `docs/open-questions.md:165` and in `03` §10 (`:1636`), and is unstruck in `roadmap.md:3801`. RL-1909 minted in #1390 (`f7a1ccd9`), after S10 merged (`git merge-base --is-ancestor 85eac5b2 f7a1ccd9` rc 0), and that PR's diff touches `open-questions.md` by 2 lines and `03` by none. **FD candidate**, reported to the lead |
| CR-1907 E3-C: OQ-1285's label becomes "Before Phase 3" (RL-1908) | the gate-row move | `roadmap.md` cites RL-1908 3 times, and the move moves OQ-1285 with S12 to P3. Met as far as read |
| CR-1907 E6 gate row: OQ-1901 joins "Before the P2 exit demo" | the row | Met (`roadmap.md:3801`, "OQ-1901 joined 2026-10-25") |

### §5b. The owed list, generated

```text
Generated by `python3 scripts/register-owed.py WK-675` against `1e0a8abb (`docs/wk675-close-audit-2026-10-26`)`.
Mode: work item 'WK-675'. 10 owed row(s), 1 matched but excluded as opening with a resolution marker
- 03 §5.1 POST /rate-tables/{slug}/versions (F-W10-3) — carry forward with an owner — the WK-675 rate-table editor slice
- Three 03 §5.3 views … owned by no Work (FD-1283) — Reassigned to WK-675
- Five 07 §5.3 platform views … (FD-1284) — Reassigned
- The /api/v1/score 200 response has no schema … (FD-1335) — carry forward with an owner (WK-1178)
- Untyped JSON request bodies … (FD-1366) — fix before close with an owner: WK-1178
- FR-223's MODEL_REFERENCE_MODE_INCONSISTENT is emitted nowhere … (FD-1437) — fix before close with an owner: WK-675 S3's leaf
- The existing rate-table diff routes answer 404 RATE_TABLE_MISS … (FD-1585) — WK-675
- SL-1559 never recorded the stored-data query … (FD-1652) — fix before close with an owner: WK-675
- Two docstrings … "stays on the synchronous 200 path" … (FD-1656) — fix before close with an owner: WK-675
- A mount output mapped to a blank parent name saves … (FD-1936) — fix before close with an owner: WK-675
Excluded as opening with a resolution marker — verify:
- The DagDesigner live-validation debounce … (FD-1611)
```

*(Each row's title is shortened here. The full output, 16 lines, is reproduced by the command at
this tree. `register-owed.py review` at the same tree reports 29 owed rows, the replan check's
evidence line.)*

**Each row, resolved against `1e0a8abb`:**

| Row | State at `1e0a8abb` | PROPOSED |
|---|---|---|
| F-W10-3 | the route exists, `api/rate_tables.py:142` (SL-1559, #1281) | delivered. **The row's discharge marker is owed** |
| FD-1283 | the version list (#1388) and the regression suite (#1396) are on main, and Deployments moved to P3 (`roadmap.md:1304`) | discharged for its two P2 views. **The row's annotation is owed**, with Deployments carried with S12 |
| FD-1284 | Jobs and Job detail moved to P3 (`roadmap.md:1306`) | carried, owner the maintainer, event the P2 phase closure record. Not a WK-675 blocker |
| FD-1335, FD-1366 | owner WK-1178 (FD-1366 remainder: `POST /sub-graphs` and `POST /sub-graphs/{slug}/versions`) | assigned elsewhere. Not this close's |
| FD-1437 | discharged by S3: the compile-site typed error `platform/rating_versions.py:320`, test `test_rating_mode_mismatch_api.py:45-69`, the limb (3) sweep at LG-1606:117, and limb (1) RL-1438. The FD and its register row still read `active` | delivered. **The closing act is owed** (set `closed` citing #1271 `99f22479`) |
| FD-1585 | **not fixed**: the two diff routes (`api/rate_tables.py:388-450`, `:487+`) have no `spec_not_found()`, and `backend/tests/test_api_rate_tables.py:506`, `:601`, `:929`, `:1121` and `:1184` still assert `"RATE_TABLE_MISS"` | **open, a close blocker**: fix before close, owner WK-675 (a small slice), or the maintainer accepts it |
| FD-1652 | **not done**: the two read-only `jsonb_typeof` counts are not recorded in `docs/findings/FD-01652-…md`, and its own date "no later than Fri 2026-10-23" has passed | **open, a close blocker, overdue**. It needs a read-only dev-DB count, a DB window the lead grants |
| FD-1656 | **not fixed**: "stays on the synchronous 200 path" still at `backend/src/app/platform/rate_tables.py:435` and `backend/tests/test_rate_tables_service.py:492` | **open, a close blocker**: fix (docstrings, three sites) or accept at the P2 close, as the row allows |
| FD-1936 | discharged by SL-1938 (#1397, `8f5aead6`). The FD reads `active` | delivered. **The closing act is owed** (closed in place, merge sha `8f5aead6a826…`) |
| FD-1611 (excluded) | SL-1639 (#1283) | resolved. Nothing residual read |

**The OQ rows raised by WK-675's slices:** OQ-1901, open, owner WK-675, decided by RL-1909 but not
applied (§5a). OQ-1285, open, moved with S12 to P3 (RL-1908). OQ-1843, decided by RL-1876.
OQ-1460 and OQ-1931 belong to WK-1178. OQ-1223 and OQ-1231 are decided. **Process backlog:**
`grep -n 'WK-675' docs/process/process-backlog.md` prints nothing.

**Reconciliation.** Every id in the generated block appears in the table above with a resolution.
The Findings below add only what no register row carries: the five unclosed lane-C slice records,
the unapplied RL-1909 texts, the SL-1554 LG gate line, PL-1546 items 3 and 5, and the cursor's
missing broken-input proof.

### §5c. Workflow steps that cite this close's requirements

**Predicate** (a candidate list, not a reading), at `1e0a8abb`:

```bash
grep -n -E '\b(FR|NFR)-(212|213|214|215|217|218|219|220|221|222|223|225|226|227|228|229|230|231|232|233|234|235|244|246|247|248|249|251|252|255|256|258|260|261|262|263|264|265|266|1186|1221|1903|1932|24|25|463)\b' docs/workflows/WF-*.md
```

The hits are in WF-699, WF-700 and WF-701 only. WF-698 and WF-702 cite none, and no journey
cites FR-24, FR-25 or NFR-463. For each hit, the owning step was opened, and the cited row was
read to its end with its dated amendments (a subagent read them, and the auditor re-read the
one disagreement).

| Journey | Step | Id | Verdict |
|---|---|---|---|
| WF-699 | A1, A2 | FR-230 | still says it (one Factor per request, RL-1361) |
| WF-699 | A3 | FR-231 | still says it |
| WF-699 | A4 | FR-233 | still says it |
| WF-699 | A5 | FR-234 | still says it (the finite-decimal amendment of 2026-10-18 adds and does not contradict) |
| WF-699 | A6 | FR-229 | still says it |
| WF-699 | B2 | FR-213 | still says it |
| WF-699 | B3 | FR-221 | still says it |
| WF-699 | B4 | FR-222 | still says it (the superseded sentences of 2026-10-18 and 2026-10-25 do not touch B4) |
| WF-699 | B5 | FR-220, FR-225 | still says it |
| WF-699 | B6 | FR-212 | still says it |
| WF-699 | B7 | FR-217 | still says it |
| WF-699 | B8 | FR-226 | still says it |
| WF-699 | **B9** (and the §3 row at `:112`) | **FR-227** | **disagrees**. B9 (the WF-699 file, line `:64`) says a `money_minor` times a float-typed value "is refused: `MONETARY_FLOAT_REFUSED`" at save. FR-227 (`03:115`, amended 2026-10-17 by RL-1564) closes `money_minor` both ways at save and refuses every other pair with **`RATING_TYPE_MISMATCH`**. Its closed type list has no float type, and no `03` requirement row says when `MONETARY_FLOAT_REFUSED` (registered at `03:1136`) is raised |
| WF-699 | D1 to D5 | FR-260, FR-261 | still says it |
| WF-699 | D6 to D8 | FR-263, FR-264, FR-266 | still says it |
| WF-699 | §3 `:111` | FR-212 | still says it. The row gives only `RATING_GRAPH_CYCLIC` for "a cycle or an unresolved reference", where `03` also registers `RATING_GRAPH_UNRESOLVED_REF`. FR-212 names no code, so this is not a disagreement with FR-212 |
| WF-699 | §3 `:115`, `:116` | FR-234, FR-260 | still says it (`:116`'s "deliberately accepted" means "expected value changed", per FR-260 amendment (3)) |
| WF-700 | E5, E6 | FR-266, FR-263 | still says it |
| WF-701 | A5 | FR-262 | still says it |
| WF-701 | A6 | FR-258 | still says it |
| WF-701 | H1, §3 `:136` | FR-255 | still says it |
| WF-701 | H6 | FR-260 | still says it |

The one disagreement is an FD candidate (Findings 4). Which side is wrong is `CLAUDE.md` §0's
question.

**Correction to the B9 row, 2026-10-26 10:57 GMT (lead verdict, to-lead "2026-10-26 10:54:44
GMT", and the lead's correction in `from-lead-2026-10-09.md`, "2026-10-26 10:55:24 GMT").** The
lead's first pack said `03` has 0 hits for `MONETARY_FLOAT_REFUSED`. That was a misreading, and
the count is corrected here with its predicate, at `1e0a8abb` (the tree this record is cut from):

```bash
git -C <wt> grep -c MONETARY_FLOAT_REFUSED -- docs/specs/03-rating-engine.md
# docs/specs/03-rating-engine.md:1
git -C <wt> grep -n MONETARY_FLOAT_REFUSED -- docs/specs/03-rating-engine.md | cut -d: -f1,2
# docs/specs/03-rating-engine.md:1136
```

The one hit is `03:1136`, the error-code enumeration. The code is also defined in the backend:
`backend/src/app/errors.py:323` is the line `        "MONETARY_FLOAT_REFUSED",` inside
`RATING_ERROR_CODES`. **Reclassified:** the code is enumerated in `03`, but **no §5.x row owns it**
(the enumeration at `:1136` is the only hit, so no endpoint row says when it is raised), against
WF-699 B9's claim (`:64`, and the §3 row at `:112`) that it is raised at save. That is **not**
"never named". The defect is a code without an owner, set against a workflow that gives it a
raise point which FR-227 (`03:115`, RL-1564) assigns to `RATING_TYPE_MISMATCH`. It is FD-1954
(Findings, below).

### §5d. FR-230 by limb, against PL-1546's row

The FR (`03:123`) says a rate table can be seeded from a Model and that subsequent manual edits are
diffed against that seed. It names no view. PL-1546's FR-230 row, quoted verbatim from
`docs/plans/PL-01546-wk-675-slices-5-to-11-work-plan-delta.md:146` (the only table row of that
plan that carries FR-230; line 230 is the self-review list of ids):

```text
| 1 | SL-1547 — S5: Editor II: diff shading, bulk, import, export | `PL-1286` S5 row, plus R5.1–R5.3 | `03` §3.3: FR-230, FR-231, FR-232, FR-233, FR-235; `00`: FR-25; NFR-463; register F-W10-1, F-W10-2 (view limb) | S4 closed; **OQ-1223 decided** (DP-3); `SL-1391` (closed, met); the FD-1366 bulk-operation typing slice (WK-1178) merged | at GO | 1 | no |
```

The row it cites, `PL-1286:307` (S5), reads "Diff-vs-previous and diff-vs-seed **shading** (FR-230,
FR-231)". The row's slice title is "diff shading, bulk, import, export". **The quoted row assigns WK-675
a diff shading, and no seed view or seed action.**

| Limb | Verdict (lead, to-lead 10:54:44, adopted) | Evidence |
|---|---|---|
| Diff vs seed | **delivered but untested.** Owner WK-675; the test is owed at the P2 close, or in the sibling of the Tue 27 Oct docs PR | `frontend/src/components/rating/RateTableDiffPanel.vue:145` is `          <option value="seed">`, the diff-against-seed choice; no frontend test names FR-230 |
| Seed action (seed a rate table from a Model) | **reassigned** to the owner of the seed endpoint, the API (`backend/src/app/api/rate_tables.py:100`, the seed route, §1 above). **Not "not started" against WK-675**, because the quoted row does not assign WK-675 a seed view | the quoted row (above) names shading, bulk, import and export for S5; `git grep -n -i -E 'seed-from-model\|seedFromModel\|seed_from_model' -- frontend/src` (excluding `generated/`) prints nothing, which is consistent with a row that never asked for it. WF-699 A2 seeds over HTTP |

The reading is the quoted row's. If a later ruling reads FR-230 as owing a seed view to WK-675,
the seed-action limb becomes **not started**.

### §5e. The owed list, RULED (to-lead "2026-10-26 10:54:44 GMT")

Five rows, each with an owner, a date and the artifact that discharges it. The maintainer (by
delegation) ruled them; the lead's verdict pack is the source of the contents.

| # | Owed | Owner | Date | Discharged by |
|---|---|---|---|---|
| (1) | **One docs PR, lane C:** FD-1656's docstring correction (three sites, §5b); the closing acts for SL-1551, SL-1552, SL-1553, SL-1554 and SL-1938, and LG-1902, LG-1933 and LG-1939; RL-1909's four edits applied in `03` (FD-1953); PL-1546 item 3 (one `// FR-xxx` naming line per frontend test, **or** the item amended by a dated line to say the behaviour is tested under the slice's LG) and item 5; and FD-1955's typed-cursor proof re-run on genuinely broken input | the lead (lead 28) | Tue 27 Oct 2026 | that docs PR |
| (2) | **FD-1585 fix** (the two diff routes answer `RATE_TABLE_MISS`; register `docs/findings/register.md:334`, "The existing rate-table diff routes answer 404 `RATE_TABLE_MISS` …") | WK-675 | Wed 28 Oct 2026 | a gated code slice from `main` |
| (3) | **FD-1652's stored-data query** (the two read-only `jsonb_typeof` counts; register `docs/findings/register.md:347`) | WK-675 | the next DB window, by Wed 28 Oct 2026 | the counts quoted in FD-1652's register row |
| (4) | **NFR-463 deferred:** one `accessibility-tester` pass over the six P2 views | WK-675 | Mon 3 Nov 2026 (before the docs freeze) | the measurement lines in the CR addendum |
| (5) | **A fresh full gate** on gate-1b at this record's head, after S1b's END | the lead | after S1b's END | the END row, below |

```text
Object measured: ffca3a45a2f83b98e3e3ace080328cb8b031fd64 (tree df19d144), gate-1b, wk675-gate.sh e90dbfb1ae98f26e
END 2026-10-26T12:42:16+00:00 3.49 2.21 1.99 (date l1 l5 l15) rc=1
| END rc parts | python max=1 fe max=0 demo=0 restore rc_kc=0 role rc_role=0 skip rc_skip=0 |
rc files: audit_docs=1, contracts=0, import_linter=0, mypy=0, pytest=1, req_coverage=0, ruff=0
pytest: 13 failed, 6963 passed, 21 skipped, 5 xfailed, 146 warnings in 3023.89s (0:50:23)
| pytest skipped | 21 (<= 21) |
| pnpm install --frozen-lockfile | rc=0 |
| pnpm generate:api | rc=0 |
| pnpm lint | rc=0 |
| pnpm type-check | rc=0 |
| pnpm test --maxWorkers=2 | rc=0 | Test Files  137 passed (137); Tests  892 passed (892)
| pnpm build | rc=0 |
| pg_roles before | gip_app,gip_app_login |
| pg_roles after provision | gip_app,gip_app_login |
| pg_roles at END | gip_app,gip_app_login |
| demo.py --journey wf-699 | rc=0 |
| D7 | ok  19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units (full-book attribution cost: FD-1576) |
Ruling: the maintainer (by delegation), to-lead "2026-10-26 12:45:15 GMT — Maintainer: WK-675 gate @ffca3a45 on gate-1b STANDS under 1(f) (verified from the gate dir); S1b read-back VERIFIED; proceed to the mint"
```

**Register rows cited by line, because an id token does not always resolve a row** (`grep -n
'<id>' docs/findings/register.md`, at the tree of `44d58c44`): FD-1585 is cited by
`docs/findings/register.md:334` and its title above (it does not resolve by `(FD-1585)` or
`**FD-1585**`; the FD-1754 lesson). The others resolve by the token and are given by line:
F-W10-3 `:67`; FD-1283 `:216`, `:217`; FD-1284 `:217`; FD-1335 `:228`, `:286`, `:287`, `:363`;
FD-1366 `:287`; FD-1437 `:304`; FD-1652 `:347`; FD-1656 `:352`; FD-1936 `:420`; FD-1611 `:341`.

**Process backlog (owned by no id).** The three process rows are in `docs/process/process-backlog.md`
(the lean-P2 list of RFC-1506 P6, 8 Oct), dated 2026-10-26: the unclosed lane-C SL and LG
records (including LG-1939's missing `slice:` and its working-id filename); LG-1881's missing
gate-of-record line; and the doc-index leaf-plan flip (below).

## Findings

**FD candidates** (no id is minted or written here. The lead reserves one if adopted):

1. **RL-1909's four obliged edits were never applied.** OQ-1901 is decided but reads open in both
   mirrors, and `03` §5.1 states no cap. The evidence is in §5a. The mirror check cannot see it,
   because both mirrors agree.
2. **The five lane-C slices are merged but their LG and SL records still read `active`**, two LGs
   say "MERGE-ACK: not yet", and LG-1939 lacks `slice:` (§1). That is a records lag of the kind
   the `roadmap.md:607` exit-demo row was dated for on 2026-10-25. It is probably a process-backlog
   row, not an FD; the lead names the limb.
3. **LG-1881 (SL-1554) carries no gate-of-record line.** The gate @`11c3db18` STANDS only in
   `to-lead.md` (§2). This is the "results only in chat" shape. Probably a process row.
4. **WF-699 B9 and its §3 row at `:112` name `MONETARY_FLOAT_REFUSED` at save, where FR-227 (as
   amended 2026-10-17, RL-1564) refuses with `RATING_TYPE_MISMATCH`** (§5c).

Not new: FD-1585, FD-1652 and FD-1656 are open, owned by WK-675, and block this close (§5b).

**Dated amendment 2026-10-26 10:57 GMT: dispositions, ruled in to-lead "2026-10-26 10:54:44
GMT".** Three FD candidates are accepted as findings with essays and register rows, in working-id
form only (never minted here):

| Candidate | Working id | Essay | Severity (proposed; the lead decides) |
|---|---|---|---|
| 1. RL-1909's four obliged edits never applied | FD-1953 | `docs/findings/FD-01953-rl-1909-s-four-obliged-edits-were-never-applied-so-oq-1901-reads-open-in-both-mirrors.md` | MEDIUM |
| 4. WF-699 B9 vs FR-227 | FD-1954 | `docs/findings/FD-01954-wf-699-b9-says-monetary-float-refused-at-save-where-fr-227-refuses-with-rating-type-mismatch-and-no-5x-row-owns-the-code.md` | LOW |
| the typed cursor's only red (§3) | FD-1955 | `docs/findings/FD-01955-the-regression-run-typed-cursor-has-only-a-red-by-absence-of-the-route-so-its-refusal-has-never-been-shown-failing.md` | MEDIUM |

Candidates 2 and 3 (the unclosed lane-C records; LG-1881's gate line) are process-backlog rows, not
FDs. A third process-backlog row, not among the candidates, is disclosed in the Verdict (the
doc-index leaf-plan flip). The register has no severity scale in its README (`grep -n -i
severity docs/findings/README.md` prints nothing); the severities follow the register's
usage: HIGH when a price or data is wrong, MEDIUM when a wrong merge, a false green or a wrong
governance record is let through, LOW when nothing of that kind moves.

## Replan check (`CLAUDE.md` §14, `RFC-1248`)

1. **Completion — yes.** The scope audit adds FR-214 (named in `PL-1286`'s designer row but in no
   WK-675 roadmap text or PL-1546 row), and four PL-1546 rows are not closed on their LGs. Neither
   moves scope.
2. **Omission — no.** Nothing the phase needs is unnamed. The unfixed items each have a register
   row (FD-1585, FD-1652, FD-1656) or a ruling (RL-1909).
3. **Skills and research — yes.** `close-workstream` §0's `scope-audit.py` example cannot be run
   through `run-heavy.sh --light`, which refuses it (rc 78). The brief and the skill assume a
   route that does not exist for this script. It does not move scope.
4. **Drift — yes.** OQ-1901 is decided by RL-1909 but open in the OQ register, in `03` §10 and in
   the roadmap §10 row, and `03` §5.1 lacks the cap (§5a). It moves no slice or phase.
5. **Shape — no** since the last review (CR-1907, 2026-10-25). S12, S13 and S14 moved to P3 on
   2026-10-03 and 2026-10-08, before that review, and were recorded there.

`register-owed.py review` at `1e0a8abb`: **29 owed rows** (11 excluded as opening with a
resolution marker).

**Triggers:**

- A phase boundary or Work scope moved: **not fired**. No move since CR-1907.
- An exit criterion at risk: **fired, borderline**. G1 needs WK-675 closed by a dated acceptance
  line before the exit demo on Thu 2026-11-12. Three WK-675 "fix before close" rows are open, one
  of them overdue (FD-1652), and the five slice records are unclosed. Each is small, and there are
  17 days left.
- A replan decided: **not fired**.
- A finding that moves a slice or a phase: **not fired**. The candidates above move none.

**PROPOSED:** no full review is needed now. The exit-criterion line is recorded and carried to
the full review before the P2 exit demo, on two conditions: the lead names an owner and a date
for FD-1585, FD-1652 and FD-1656, and for the slice closing acts. **The verdict is the lead's.**

**Replan check: ADOPTED (lead, to-lead "2026-10-26 10:54:44 GMT").** Q1 yes, Q2 no, Q3 yes,
Q4 yes, Q5 no; "exit criterion at risk" FIRED; no second full review: CR-1907 is the
`CLAUDE.md` §14 review before the exit demo (#1390, merged 2026-10-26 at 00:01) and covers it. The fired trigger's
resolution is the owners and dates of §5e.

## Verdict

PROPOSED: **not ready for acceptance at `1e0a8abb`.** The deliverables exist and work. Each of the
46 own ids has its limb on main with a read assertion (§1), except the gaps that §5 lists, and
every lane-C slice's gate STANDS with green PR CI. The close is still blocked by:

1. FD-1585, FD-1652 and FD-1656, which are open and owned by WK-675;
2. the slice closing acts for SL-1551, SL-1552, SL-1553, SL-1554 and SL-1938 and their LGs;
3. RL-1909's unapplied edits (a docs fix that needs an owner);
4. PL-1546 items 3 and 5;
5. the fresh full gate (OWED, gate-1b after S1b's END).

The §5 verdicts are proposals. **The close itself is the user's dated line.**

**LEAD VERDICT (to-lead "2026-10-26 10:54:44 GMT", adopted by the maintainer (by delegation)):
not ready for acceptance at `1e0a8abb`.** The deliverables exist and work; the close is blocked by
the open owned findings, the slice closing acts, RL-1909's unapplied edits, PL-1546 items 3
and 5, and the fresh gate. The owners and dates are in §5e.

**Close statement.** Re-presented as a CR addendum when owed rows (1)–(3) and (5) of §5e have
landed. The WK-675 row stays "close audit filed (CR-1952), acceptance owed" until the user's dated
acceptance line. This record does not write "closed" on that row.

**Disclosure: the INDEX regeneration shows PL-1368 as closed.** `docs/INDEX.md` is generated, and
`scripts/doc-index.py` derives a WK-675 leaf plan as closed once any `CR-` record with
`work: WK-675` exists. This record is such a record. **That is not an acceptance** of WK-675, and
it is not hand-edited (the INDEX is generated). It is a process-backlog row
(`docs/process/process-backlog.md`).

## Addendum 2026-10-27 — the auditor's corrections to this record, and the status of the five owed rows

Appended in the lane-C docs PR by the auditor (`aud-tue27`), on the lead's addendum accepting corrections (1) to (3) (the plan `plan-tue27-docs-pr-2026-10-26.md`, LEAD ADDENDUM) and on the maintainer's (by delegation) entry "2026-10-26 15:37:48 GMT" for items (5) and (6). The record above is not edited; where it and this addendum differ, this addendum is the later reading, and each correction names the tree it was read at. The verdicts remain the lead's to adopt and the close the maintainer's.

**(1) FR-230 diff-vs-seed is tested; the limb is delivered.** §5d gives "diff vs seed" as "delivered but untested" because "no frontend test names FR-230". At `3dbdf07625efb71eea5181999dd245b13c2b52d5` (the lane-C head before this commit; `git diff --stat 1e0a8abb <it> -- frontend` is empty, so the frontend is the CR's own), `frontend/src/components/rating/__tests__/RateTableDiffPanel.test.ts:60-64`, `it("compares against the seed on request")`, renders the panel, chooses `seed`, and asserts `getDiffCells` is called with `("area@3", { against: "seed" })`. That asserts the seed request, not the rendered shading of a seed diff; the limb is **delivered**, with the shading of a seed diff the one part not asserted. The test did not name the id; the executor's naming line in the same PR does (PL-1546 item 3). §5d's second row (the seed action, reassigned to the seed endpoint's owner) is unchanged.

**(2) SL-1551's roadmap row was already `closed` at `1e0a8abb`.** §1 reads the row as `status: active`. `git show 1e0a8abb:docs/roadmap.md` has `status: closed` in the `id: SL-1551` block (the slice PR #1372 set it; its closing line reads "Closed 2026-10-23 as a Slice, closing acts in the slice PR"). The row is not re-closed in this PR; SL-1551's open closing act was the ledger `LG-1867`, closed here.

**(3) S11 is not an item-5 gap.** §1 counts S11's review as a PL-1546 item-5 miss. Item 5 binds a slice that adds a chart. At `3dbdf076…`, `git grep -l -E 'ChartFigure|echarts' -- frontend/src/components frontend/src/views` (non-test files) names the shared chart components, `dislocation/{AttributionWaterfall,ChangeHistogram,SegmentGrid}.vue` (S8) and `sandbox/LadderWaterfall.vue` (S6), and nothing under `frontend/src/views` or a regression-suite component: S10 and S11 add no chart. The only slice with a chart and no report in its ledger was S6 (`LG-1673`); the report is now in `LG-1673`'s dated section (see (5)).

**(4) §5b's FD-1585 list wrongly includes `backend/tests/test_api_rate_tables.py:929`.** §5b gives the assertions that still read `"RATE_TABLE_MISS"` at `:506`, `:601`, `:929`, `:1121` and `:1184`. At `3dbdf076…`, `:925-929` is the end of a **bulk-operation** test (`json=_bulk_body("uplift_table", …)`, then `assert response.status_code == 404` and `response.json()["code"] == "RATE_TABLE_MISS"`). FD-1585 is the two **diff** routes; the bulk route's `RATE_TABLE_MISS` is a different route and out of FD-1585's scope. The list is the other four. (Not read: whether the other four are all diff-route asserts; that is FD-1585's own slice's first act.)

**(5) NFR-463 is NOT met; the chart limb is delivered.** §4 gave NFR-463 as "Not measured as a whole" and §5e row (4) deferred it to one pass. The pass ran 2026-10-26 (static, `7ed5c398`; report `~/gi-pricing-plan.local/scratch/a11y-nfr463/report-2026-10-26.md`, verbatim in `LG-1673`'s dated section): 17 distinct FAIL defects, 0 critical, 1 serious, 4 moderate, 12 low. The maintainer (by delegation), "2026-10-26 15:37:48 GMT": **NFR-463 is not met** on the static limbs, recorded as **FD-8272** (MEDIUM, owner WK-675, fix before WK-675's close, by Tue 3 Nov 2026), and the **chart limb holds at all five sites** (`ChartFigure` tables, waterfall direction labels, diff shade sign and %): delivered. The static-only limit is a carried limb (OQ 8273, decided at the P2 close). This moves NFR-463 from "not measured as a whole" to "measured on the static limbs, not met".

**(6) The five owed rows of §5e, at the lane-C branch (`docs/tue27-lanec-aud` over `docs/tue27-lanec-2026-10-27` `c721f3cc`; the PR is not yet merged, so "landed" below means "on the branch").**

| # | Row | Status | Evidence |
|---|---|---|---|
| (1) | The lane-C docs PR | **on the branch, not merged.** Landed: FD-1656's three docstrings (`7d752ca1`); RL-1909's four edits (`5b0ccc2c`); the closing acts for SL-1552, SL-1553, SL-1554 and SL-1938 and for LG-1902, LG-1933, LG-1939, LG-1867 and LG-1881 (SL-1551's row was already closed, (2)); FD-1656, FD-1953, FD-1652, FD-1936 and FD-1437 closed in place. Not yet landed on the auditor's side: FD-1955 and FD-1954 (they close after the typed-cursor runs and RL 8268's mint). The executor's items (PL-1546 item 3's naming lines, item 5's `LG-1673` section, LG-1939's rename) are the executor's commits | the branch's commits |
| (2) | FD-1585 fix | **owed**, not in this PR; code and gate scheduled for Tue 27 (to-lead "2026-10-26 15:58:34 GMT") | register `:334` |
| (3) | FD-1652's stored-data query | **discharged, closed measured:** no persisted pre-retype data exists in this environment (databases enumerated: `gipricing`, `postgres`); the instrument detects a planted non-string; today's writers produce strings (to-lead "2026-10-26 15:56:23 GMT") | the essay's "Measured close", `FD-01652-*.md:140-142` |
| (4) | NFR-463 pass | **done, result NOT MET**, correction (5) | FD-8272 |
| (5) | A fresh full gate at this record's head | **discharged by the END row in §5e** (gate-1b, `ffca3a45`, `rc=1`, STANDS under 1(f), to-lead "2026-10-26 12:45:15 GMT"). Not a gate of the lane-C branch, which has its own cover under DP-T27-6 | §5e |

The Verdict above is unchanged by this addendum: the close is the maintainer's dated line, and WK-675's row stays "close audit filed (CR-1952), acceptance owed". The user's acceptance of WK-675 reads FD-8272 and OQ 8273.
