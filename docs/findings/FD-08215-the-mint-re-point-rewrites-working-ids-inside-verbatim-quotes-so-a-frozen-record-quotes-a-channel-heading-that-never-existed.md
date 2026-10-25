---
id: FD-8215
family: finding
title: The mint re-point rewrites working ids inside verbatim quotes, so a frozen record quotes a channel heading that never existed
status: active
created: 2026-10-25
owner: auditor
tree: 3cd5fcf7ee514db1ae8ab681d7cacc1761945091
corrected_by: []
relates: [WK-1178]
---

# FD-8215 — The mint re-point rewrites working ids inside verbatim quotes, so a frozen record quotes a channel heading that never existed

## Finding

**LOW; owner WK-1178 (tooling).** Authority: the maintainer's (by delegation) entry "2026-10-23 11:58:33 BST — Maintainer: SL 8178 RS 8214 CLEAN adoption CONFIRMED (4 LG lines + strict red-first); quote-alteration-at-mint class → one LOW FD, no body edits" (`to-lead.md`), item (B): no body edit to RL-1848 or any merged record; one LOW FD carrying the mechanism, the instances from one docs-only alternation sweep, and the remedy; the FD is the accepted disclosure for every listed instance; no per-instance correcting RL; an unmerged record is fixed in place before merge.

**The defect.** A record drafted under a working id quotes a `to-lead.md` entry heading that carries that working id ("RL 8176 ADOPTED"). At the mint the id is re-pointed over the whole tree. The re-point does not distinguish a citation from a verbatim quotation, so the quoted heading becomes "RL-1848 ADOPTED", which `to-lead.md` never contained. The known instance: RL-1848 on `origin/main` quotes the entry as "…RL-1848 ADOPTED, option (A) with one amendment…" where the heading reads "RL 8176 ADOPTED, option (A) with one amendment…" (2026-10-22 17:21:38 BST, `to-lead.md`). Others known: RS 8214 B1 and LG 8179 (both unmerged, fixed in place).

## Mechanism

There is no re-point script. `scripts/doc-id.py` has only `next`, `check`, `widen`, `migrate`, `migrate-verify`; the `repoint` helpers in it serve the W37-6 relative-link migration. The mint re-point is a seat-run whole-tree rename procedure written in prose:

- `.claude/skills/mint-and-finish/SKILL.md` §1 step 4: rename each old id, highest first, in one commit, then `git grep -c` of each OLD id = 0 "outside verbatim quotes".
- Common seat brief item 26 (the maintainer, "2026-10-18 09:17:30 BST"): grep the WHOLE tree for each working id (space and hyphen forms) "and re-point every hit".

Item 26 says every hit; step 4 exempts quotes; step 7 of the same skill says "Quoted channel headers keep their working ids" but gives no way to find them. An unmechanised rename over every hit, with an exemption that only a reader applies, rewrites quotes. Nothing then compares a quoted heading with `to-lead.md`: `audit-docs.py` has no such check, so the altered quote merges.

## Evidence

Tree: `origin/main` 3cd5fcf7ee514db1ae8ab681d7cacc1761945091 (fetched 2026-10-25). Read-only `git grep` over `docs/`, run beside SL 8185's gate under the maintainer's "2026-10-25 12:55:59 GMT" item (b), load1 3.1 at the start; log `~/gi-pricing-plan.local/scratch/aud-8215-sweep-2026-10-25.log`.

Commands (verbatim; `<wt>` is the aud-8215 worktree):

1. `git -C <wt> grep -n -P -e '["“][^"”]{0,200}\b(RL|FD|SL|LG|PL|OQ|RS|WK|CR)-[0-9]{4,5}\b[^"”]{0,200}["”]' 3cd5fcf7ee514db1ae8ab681d7cacc1761945091 -- docs` (all quoted spans carrying a hyphen-form id: 1305 lines).
2. `git -C <wt> grep -n -P -e '["“]20\d\d-\d\d-\d\d \d\d:\d\d[^"”]*\b(RL|FD|SL|LG|PL|OQ|RS|WK|CR)-[0-9]{4,5}\b[^"”]*$' 3cd5fcf7ee514db1ae8ab681d7cacc1761945091 -- docs` (the same for a quote whose closing mark is on a later line, which command 1 cannot see: 91 lines; this is the pass that finds RL-1848).

Comparison (offline, over the two outputs and `to-lead.md`): for each quoted span that opens with a channel-entry timestamp and carries a hyphen-form id, find the `## <timestamp>` heading in `~/gi-pricing-plan.local/channel/to-lead.md` and compare ids. **Instance** = a quoted id (any `FAM-nnnn`) that appears in the cited heading in neither hyphen nor space form. In every instance below the heading carries a working id (space form) where the record quotes a minted id. (Not the brief's `ADOPTED`-only alternation: that form finds 9 lines in the first output and misses most of the class, which is not confined to verdict words.)

**Result: 56 instances, in 27 files, quoting 29 distinct headings.** Of 459 quoted channel-heading spans checked, 375 agree with their heading, 56 are instances, and 28 cite a heading not in `to-lead.md` (a lead or role channel file), which this sweep could not check and does not count.

Limits: a heading is matched by its timestamp, the first `##` heading with that prefix; a quote that does not open with a timestamp is not seen; a quote that elides the heading's ids is counted only if it carries an id the heading lacks. Some rows are generated copies of a record title (`docs/INDEX.md`, `docs/findings/register.md`, `docs/open-questions.md`) or a spec cross-reference: they repeat the same altered quote and are listed because each is a separate line a reader meets. The edit that fixes the class is the record's own quote; the rest follow.

| # | File:line | Quoted heading (timestamp) | Quoted ids absent from the heading | The heading's ids |
|---|---|---|---|---|
| 1 | `docs/INDEX.md:240` | "2026-10-16 10:52:08…" | FD-1753 | FD 8070, SL 1274 |
| 2 | `docs/INDEX.md:240` | "2026-10-17 11:15:37…" | FD-1753, SL-1761 | FD 8070, SL 8074 |
| 3 | `docs/INDEX.md:258` | "2026-10-17 11:15:37…" | FD-1753, SL-1761 | FD 8070, SL 8074 |
| 4 | `docs/INDEX.md:1606` | "2026-10-05 12:58:22…" | OQ-1450, RL-1449 | FD 9780, OQ 9739, PL 9716, RL 9715 |
| 5 | `docs/INDEX.md:1610` | "2026-10-05 10:47:03…" | OQ-1453 | OQ 9777 |
| 6 | `docs/findings/FD-01511-the-quantile-template-certifies-convexity-violated-and-no-second-approver-is-enforced.md:71` | "2026-10-05 12:58:22…" | FD-1511 | FD 9780, OQ 9739, PL 9716, RL 9715 |
| 7 | `docs/findings/FD-01679-the-drafted-change-summary-pairs-rate-table-pins-by-slug-alone-so-two-pinned-versions-of-one-slug-are-silently-dropped-or-mis-paired.md:52` | "2026-10-12 05:44:45…" | FD-1679 | FD 9895, RL 1538 |
| 8 | `docs/findings/register.md:326` | "2026-10-05 12:58:22…" | FD-1511 | FD 9780, OQ 9739, PL 9716, RL 9715 |
| 9 | `docs/ledgers/LG-01839-wk-690-slice-sl-1275-slice-5-the-authoring-view-and-wf-702-route-b-end-to-end-pl-1268-slice-ledger.md:21` | "2026-10-22 00:57:13…" | RS-1844, SL-1275 | RS 8151, SL 1275 |
| 10 | `docs/open-questions.md:149` | "2026-10-05 12:58:22…" | OQ-1450, RL-1449 | FD 9780, OQ 9739, PL 9716, RL 9715 |
| 11 | `docs/open-questions.md:150` | "2026-10-05 10:47:03…" | OQ-1453 | OQ 9777 |
| 12 | `docs/plans/PL-01286-wk-675-frontend-dag-designer-rate-table-editor-quote-sandbox-and-dislocation-views-map-plan.md:201` | "2026-09-30 05:35:06…" | FD-1284 | FD 9693 |
| 13 | `docs/plans/PL-01408-wk-1178-fd-1356-fix-validation-rule-approval-through-the-workflow-leaf-plan.md:939` | "2026-10-01 11:16:23…" | RL-1407 | RL 9750 |
| 14 | `docs/plans/PL-01447-wk-673-fd-9707-fix-a-lookup-step-reads-the-row-in-force-as-at-its-declared-date-leaf-plan.md:102` | "2026-10-05 13:15:53…" | FD-1420, PL-1452 | FD 9707, PL 9689, RL 9695 |
| 15 | `docs/plans/PL-01447-wk-673-fd-9707-fix-a-lookup-step-reads-the-row-in-force-as-at-its-declared-date-leaf-plan.md:114` | "2026-10-05 13:20:52…" | PL-1447 | PL 9688 |
| 16 | `docs/plans/PL-01447-wk-673-fd-9707-fix-a-lookup-step-reads-the-row-in-force-as-at-its-declared-date-leaf-plan.md:121` | "2026-10-05 13:11:05…" | FD-1420 | FD 9707, SL 1409 |
| 17 | `docs/plans/PL-01454-wk-1178-nfr-489-remedy-the-score-request-path-meets-its-p99-budget-leaf-plan.md:92` | "2026-10-05 13:11:05…" | FD-1420 | FD 9707, SL 1409 |
| 18 | `docs/plans/PL-01454-wk-1178-nfr-489-remedy-the-score-request-path-meets-its-p99-budget-leaf-plan.md:134` | "2026-10-05 10:47:03…" | OQ-1453 | OQ 9777 |
| 19 | `docs/plans/PL-01454-wk-1178-nfr-489-remedy-the-score-request-path-meets-its-p99-budget-leaf-plan.md:387` | "2026-10-04 19:46:13…" | FD-1411 | FD 9729, PL 9728 |
| 20 | `docs/plans/PL-01454-wk-1178-nfr-489-remedy-the-score-request-path-meets-its-p99-budget-leaf-plan.md:582` | "2026-10-05 10:47:03…" | OQ-1453 | OQ 9777 |
| 21 | `docs/plans/PL-01544-wk-1178-exit-demo-slice-b-the-scripted-wf-699-journey-over-http-to-a-served-page-leaf-plan.md:134` | "2026-10-04 19:58:33…" | PL-1454 | PL 9728 |
| 22 | `docs/plans/PL-01544-wk-1178-exit-demo-slice-b-the-scripted-wf-699-journey-over-http-to-a-served-page-leaf-plan.md:778` | "2026-10-08 13:12:28…" | PL-1544 | FD 1494, PL 9624, PL 9629 |
| 23 | `docs/plans/PL-01620-wk-674-slices-4-and-5-after-sl-1455-returned-to-p2-work-plan-delta.md:44` | "2026-10-11 10:55:55…" | PL-1620 | OQ 1223, PL 9921 |
| 24 | `docs/plans/PL-01677-wk-673-fd-1679-the-change-summary-refuses-two-versions-of-one-rate-table-slug-plan-delta.md:55` | "2026-10-12 05:43:54…" | FD-1679 | FD 9895, SL 1543 |
| 25 | `docs/plans/PL-01677-wk-673-fd-1679-the-change-summary-refuses-two-versions-of-one-rate-table-slug-plan-delta.md:68` | "2026-10-12 05:44:45…" | FD-1679 | FD 9895, RL 1538 |
| 26 | `docs/plans/PL-01772-wk-1178-a-scalar-one-row-glm-predict-for-model-call-plan-delta.md:108` | "2026-10-17 21:26:31…" | SL-1773 | SL 8099 |
| 27 | `docs/plans/PL-01787-wk-1178-sl-1543-the-d7-split-test-on-the-real-derived-list-sl-1696-audit-finding-a1-plan-delta.md:48` | "2026-10-16 09:51:34…" | PL-1787 | PL 8055, RL 8060 |
| 28 | `docs/plans/PL-01787-wk-1178-sl-1543-the-d7-split-test-on-the-real-derived-list-sl-1696-audit-finding-a1-plan-delta.md:78` | "2026-10-17 11:18:51…" | PL-1787, SL-1543 | PL 8055, SL 1543 |
| 29 | `docs/plans/PL-01787-wk-1178-sl-1543-the-d7-split-test-on-the-real-derived-list-sl-1696-audit-finding-a1-plan-delta.md:328` | "2026-10-16 09:54:43…" | PL-1787 | PL 8055 |
| 30 | `docs/process/delivery-process.core.json:398` | "2026-10-05 15:27:25…" | RL-1445 | RL 9620 |
| 31 | `docs/process/delivery-process.core.json:406` | "2026-10-05 15:15:11…" | RL-1263, RL-1445 | RL 1263, RL 9633 |
| 32 | `docs/roadmap.md:955` | "2026-10-12 05:43:54…" | FD-1679, SL-1543 | FD 9895, SL 1543 |
| 33 | `docs/roadmap.md:955` | "2026-10-12 05:44:45…" | FD-1679, RL-1538 | FD 9895, RL 1538 |
| 34 | `docs/roadmap.md:2703` | "2026-10-17 11:15:37…" | FD-1753 | FD 8070, SL 8074 |
| 35 | `docs/roadmap.md:2705` | "2026-10-16 10:52:08…" | FD-1753 | FD 8070, SL 1274 |
| 36 | `docs/roadmap.md:3177` | "2026-09-30 05:35:06…" | FD-1284 | FD 9693 |
| 37 | `docs/roadmap.md:3337` | "2026-09-30 05:35:06…" | FD-1284 | FD 9693 |
| 38 | `docs/rulings/RL-01287-cr-1212-s-docs-only-label-for-wk-1170-and-wk-1169-corrected-both-carry-code-slices.md:61` | "2026-09-29 22:58:26…" | PL-1276, WK-1170 | PL 9811, WK 1170 |
| 39 | `docs/rulings/RL-01287-cr-1212-s-docs-only-label-for-wk-1170-and-wk-1169-corrected-both-carry-code-slices.md:62` | "2026-09-29 23:05:29…" | PL-1277, WK-1169 | PL 9812, WK 1169 |
| 40 | `docs/rulings/RL-01407-pl-1408-dp-1-2-3-5-6-decided-the-rule-routes-are-clients-of-the-approval-workflow-an-unreadable-or-error-dry-run-is-refused-and-the-reset-is-an-audited-script.md:649` | "2026-10-01 11:16:23…" | RL-1407 | RL 9750 |
| 41 | `docs/rulings/RL-01445-rl-1263-amended-at-most-three-build-slices-one-full-gate-at-a-time-same-work-concurrency-only-with-resolved-file-sets-and-no-plan-dependency.md:85` | "2026-10-05 15:27:25…" | RL-1445 | RL 9620 |
| 42 | `docs/rulings/RL-01446-wk-673-fd-9707-s-fix-activated-pl-9688-dp-1-to-dp-4-and-fr-221-s-text.md:75` | "2026-10-05 13:20:52…" | PL-1447 | PL 9688 |
| 43 | `docs/rulings/RL-01449-oq-9739-decided-a-subset-bundle-s-input-contract-and-outputs-are-the-baseline-s-with-the-deltas-of-the-subset-s-own-changes-applied-and-dependent-changes-share-a-group.md:315` | "2026-10-05 12:58:22…" | OQ-1450, RL-1449 | FD 9780, OQ 9739, PL 9716, RL 9715 |
| 44 | `docs/rulings/RL-01449-oq-9739-decided-a-subset-bundle-s-input-contract-and-outputs-are-the-baseline-s-with-the-deltas-of-the-subset-s-own-changes-applied-and-dependent-changes-share-a-group.md:321` | "2026-10-05 12:58:22…" | OQ-1450, RL-1449 | FD 9780, OQ 9739, PL 9716, RL 9715 |
| 45 | `docs/rulings/RL-01451-wk-673-slice-3-dp-s3-1-to-10-decided-the-authored-contract-is-hand-edited-field-level-deltas-sit-on-algorithmdiff-v-s-is-always-a-re-rate-and-the-attribution-spec-texts.md:31` | "2026-10-05 13:25:23…" | RL-1451 | RL 9663 |
| 46 | `docs/rulings/RL-01451-wk-673-slice-3-dp-s3-1-to-10-decided-the-authored-contract-is-hand-edited-field-level-deltas-sit-on-algorithmdiff-v-s-is-always-a-re-rate-and-the-attribution-spec-texts.md:90` | "2026-10-05 13:15:53…" | FD-1420, PL-1452, RL-1428 | FD 9707, PL 9689, RL 9695 |
| 47 | `docs/rulings/RL-01451-wk-673-slice-3-dp-s3-1-to-10-decided-the-authored-contract-is-hand-edited-field-level-deltas-sit-on-algorithmdiff-v-s-is-always-a-re-rate-and-the-attribution-spec-texts.md:128` | "2026-10-05 13:25:23…" | RL-1451 | RL 9663 |
| 48 | `docs/rulings/RL-01483-wk-674-slice-2-dp-s2-4-decided-each-route-s-permission-is-declared-in-a-permission-column-on-its-module-s-5-1-table.md:246` | "2026-10-05 10:11:16…" | RL-1483 | RL 9907 |
| 49 | `docs/rulings/RL-01848-environment-scoped-writes-keep-load-first-the-404-is-accepted-and-the-order-is-written-into-06-fr-343.md:25` | "2026-10-22 17:21:38…" | RL-1848 | FD 8177, RL 8176 |
| 50 | `docs/rulings/RL-01849-fr-345-dataset-scope-on-routes-with-no-handler-scope-check-versions-and-blobs-honour-it-reference-tables-stay-workspace-wide.md:24` | "2026-10-22 17:36:24…" | RL-1849 | FD 8184, RL 8182 |
| 51 | `docs/rulings/RL-01849-fr-345-dataset-scope-on-routes-with-no-handler-scope-check-versions-and-blobs-honour-it-reference-tables-stay-workspace-wide.md:47` | "2026-10-22 17:27:15…" | FD-1852 | FD 8177 |
| 52 | `docs/specs/03-rating-engine.md:110` | "2026-10-16 10:52:08…" | FD-1753 | FD 8070, SL 1274 |
| 53 | `docs/specs/03-rating-engine.md:110` | "2026-10-17 11:15:37…" | FD-1753, SL-1761 | FD 8070, SL 8074 |
| 54 | `docs/specs/03-rating-engine.md:140` | "2026-10-17 11:15:37…" | FD-1753, SL-1761 | FD 8070, SL 8074 |
| 55 | `docs/specs/03-rating-engine.md:1601` | "2026-10-05 12:58:22…" | OQ-1450, RL-1449 | FD 9780, OQ 9739, PL 9716, RL 9715 |
| 56 | `docs/specs/03-rating-engine.md:1602` | "2026-10-05 10:47:03…" | OQ-1453 | OQ 9777 |

Not checkable here (cited heading not in `to-lead.md`; not counted): `docs/findings/FD-01656-two-docstrings-still-say-a-rows-only-rate-table-diff-stays-on-the-synchronous-200-path-after-the-route-began-answering-202-on-the-first-request-for-a-key.md:17` (2026-10-11 21:13:13); `docs/ledgers/LG-01396-wk-1178-slice-sl-1377-the-fd-1357-fix-multi-factor-seeding.md:381` (2026-10-03 20:14:41); `docs/ledgers/LG-01533-wk-673-slice-sl-1472-the-fr-240-family-fix-model-approval-and-compile-refuse-an-unapproved-custom-objective-or-a-control-intent-factor-pl-1471-slice-ledger.md:97` (2026-10-08 16:59:56); `docs/ledgers/LG-01637-wk-1178-slice-sl-1367-fd-1335-part-a-the-score-and-score-compare-200-responses-documented-and-the-untyped-body-guard-slice-ledger.md:19` (2026-10-11 10:58:50); `docs/ledgers/LG-01637-wk-1178-slice-sl-1367-fd-1335-part-a-the-score-and-score-compare-200-responses-documented-and-the-untyped-body-guard-slice-ledger.md:329` (2026-10-11 16:28:30); `docs/ledgers/LG-01637-wk-1178-slice-sl-1367-fd-1335-part-a-the-score-and-score-compare-200-responses-documented-and-the-untyped-body-guard-slice-ledger.md:348` (2026-10-11 15:32:15); `docs/ledgers/LG-01641-wk-1178-slice-sl-1526-exit-demo-a-the-real-fremtpl2-rating-algorithm-and-the-20000-policy-portfolio-pl-1525-pl-1577-slice-ledger.md:254` (2026-10-11 19:59:05); `docs/ledgers/LG-01643-wk-1178-slice-sl-1566-batch-scoring-serialises-every-declared-output-type-and-never-aborts-on-one-row-pl-1565-slice-ledger.md:24` (2026-10-11 11:45:36); `docs/ledgers/LG-01681-wk-673-slice-sl-1678-fd-1679-loud-guard-the-drafted-change-summary-refuses-two-versions-of-one-rate-table-slug-pl-1677-slice-ledger.md:21` (2026-10-12 06:05:28); `docs/ledgers/LG-01697-wk-1178-slice-sl-1675-rows-whose-declared-weight-is-0-are-excluded-from-the-fit-and-every-diagnostic-pl-1674-slice-ledger.md:24` (2026-10-12 06:06:16); `docs/ledgers/LG-01777-wk-1178-slice-sl-1722-fd-1730-the-upload-completion-step-blob-promote-and-the-blob-upload-record-pl-1721-slice-ledger.md:146` (2026-10-16 09:52:42); `docs/ledgers/LG-01786-wk-675-slice-sl-1547-s5-editor-ii-diff-shading-bulk-operations-csv-import-and-export-pl-1546-pl-1668-slice-ledger.md:21` (2026-10-12 06:54:14); `docs/ledgers/LG-01859-wk-674-sl-1260-slice-6-date-routing-and-shadow-scoring-slice-ledger.md:374` (2026-10-22 23:03:12); `docs/plans/PL-01621-wk-690-slices-4-and-5-expression-factors-and-the-authoring-view-work-plan-delta.md:36` (2026-10-11 11:14:34); `docs/plans/PL-01621-wk-690-slices-4-and-5-expression-factors-and-the-authoring-view-work-plan-delta.md:297` (2026-10-11 11:20:43); `docs/plans/PL-01674-wk-1178-rows-whose-declared-weight-is-0-are-excluded-from-the-fit-and-every-diagnostic-plan-delta.md:79` (2026-10-12 05:36:12); `docs/plans/PL-01674-wk-1178-rows-whose-declared-weight-is-0-are-excluded-from-the-fit-and-every-diagnostic-plan-delta.md:80` (2026-10-12 05:38:06); `docs/plans/PL-01677-wk-673-fd-1679-the-change-summary-refuses-two-versions-of-one-rate-table-slug-plan-delta.md:79` (2026-10-12 05:44:28); `docs/plans/PL-01688-wk-674-the-scheduler-and-frontend-image-row-fr-432-s-last-two-limbs-work-plan-delta.md:253` (2026-10-12 05:37:23); `docs/plans/PL-01764-wk-675-s7-sl-1550-the-sandbox-compare-view-and-its-red-first-tests-work-plan-delta.md:37` (2026-10-16 09:33:10); `docs/plans/PL-01766-wk-674-slice-5-before-its-go-sl-1455-as-a-dependency-the-s4-premises-and-five-decision-points-work-plan-delta.md:68` (2026-10-16 10:29:33); `docs/plans/PL-01794-wk-674-slice-5-before-its-go-sl-1455-as-a-dependency-the-s4-premises-and-five-decision-points-work-plan-delta.md:66` (2026-10-16 10:29:33); `docs/plans/PL-01833-wk-675-s8-sl-1551-the-typed-movers-row-as-need-and-scope-work-plan-delta.md:38` (2026-10-17 19:34:39); `docs/roadmap.md:955` (2026-10-12 06:05:28); `docs/roadmap.md:1217` (2026-10-22 23:03:12); `docs/roadmap.md:2038` (2026-10-11 10:58:50); `docs/roadmap.md:2400` (2026-10-11 11:45:36); `docs/rulings/RL-01383-sl-1377-s-factor-ref-corrected-a-factor-reference-s-slug-admits-an-underscore-and-a-field-built-reference-is-validated-like-a-parsed-one.md:32` (2026-10-03 17:27:30).

Known instance, read at the same tree: RL-1848 (file `docs/rulings/RL-01848-…`) line 25 (row above) reads "RL-1848 ADOPTED"; `to-lead.md` line 29659 reads "RL 8176 ADOPTED".

## Remedy (not made here)

1. The re-point skips spans inside quotation marks (the mint-and-finish procedure and, if it is ever scripted, the script).
2. The auditor's mint check greps each quoted heading and requires it to exist verbatim in `to-lead.md`.

## Disposition

Accepted disclosure for every instance listed above, per the maintainer's (by delegation) entry "2026-10-23 11:58:33 BST". No body edit to any merged record and no per-instance correcting RL. The remedy is owned by WK-1178 (tooling).

## Addendum 2026-10-25 — working-id cites in frozen records (class ruling (a))

Added 2026-10-25 under the maintainer's (by delegation) entries "2026-10-25 16:50:20 GMT" (RL-1876:32 ruled (a), leave as filed, listed here) and "2026-10-25 16:51:21 GMT" (class ruling (a) for FD-1852, FD-1853, RL-1849 and RL-1876: left as filed, all listed in this FD's instance table, one remedy point, no one-off lines), both in `to-lead.md`. The sweep above counted quoted channel headings only. The records below are the same class one step wider: a merged record cites a working id in the space form, the id was minted afterwards, and the minted record's `created` comment names the working id, so each cite resolves. Nothing was re-pointed and no line was appended to any of them.

Lines read at `origin/main` 18be14a05a914951f5903d7c4581233dcaeeed32 with `git grep -n -E '\b(PL|SL|LG|RS)[ -]0?(8181|8185|8186|8158)\b' 18be14a0 -- 'docs/findings/FD-01852*' 'docs/findings/FD-01853*' 'docs/rulings/RL-01849*' 'docs/rulings/RL-01876*'`. This table is one row per record, not per hit, and its rows are not counted in the 56 instances above.

| # | Record (file) | Lines | Working id text found | Minted as | Outcome |
|---|---|---|---|---|---|
| A1 | `docs/rulings/RL-01876-a-mount-never-maps-a-port-to-a-blank-name-the-graph-invariants-refuse-it-on-the-mount-and-the-designer-shows-it-through-the-validate-route.md` | 32 | "RS 8158" | RS-1883 (by SL-1554) | left as filed (class ruling (a), to-lead 2026-10-25 16:51:21 GMT; entry 16:50:20 GMT) |
| A2 | `docs/findings/FD-01852-three-route-level-scope-less-requires-guards-refuse-a-resource-scoped-grant-before-the-handler-s-scoped-check-latent.md` | 19, 56, 64 | "PL 8181" (19, 56), "SL 8185" (56, 64), "LG 8186" (56, 64) | PL-1877, SL-1878, LG-1879 (by SL 8185) | left as filed (class ruling (a), to-lead 2026-10-25 16:51:21 GMT) |
| A3 | `docs/findings/FD-01853-portfolio-dataset-read-is-checked-with-no-resource-so-a-dataset-scoped-grant-is-refused-latent.md` | 51 | "SL 8185" | SL-1878 | left as filed (class ruling (a), to-lead 2026-10-25 16:51:21 GMT) |
| A4 | `docs/rulings/RL-01849-fr-345-dataset-scope-on-routes-with-no-handler-scope-check-versions-and-blobs-honour-it-reference-tables-stay-workspace-wide.md` | 23, 33, 36, 98, 111, 134, 170, 210, 220, 221, 222, 223, 226, 255 (14 lines) | "PL 8181" (23, 33, 36, 98, 111, 134, 170, 210, 220, 221), "SL 8185" (23, 36, 221, 222, 223, 226, 255), "LG 8186" (36); line 36 is the quoted heading "17:38:11 BST — Maintainer: PL 8181 (FD-1852 fix) DP-0..DP-3 RULED; GO (SL 8185 / LG 8186)" | PL-1877, SL-1878, LG-1879 | left as filed (class ruling (a), to-lead 2026-10-25 16:51:21 GMT) |

If this FD's remedy later rules that a dated re-point line is appended to merged records, rows A1 to A4 take it with the rest. The count of 56 instances in 27 files above is the heading sweep's and is unchanged; with this addendum 4 more records (A1 to A4) are listed under the same disposition.
