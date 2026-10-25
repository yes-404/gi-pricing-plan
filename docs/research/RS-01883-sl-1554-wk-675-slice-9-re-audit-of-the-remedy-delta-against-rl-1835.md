---
id: RS-1883
family: research
kind: audit
title: SL-1554 (WK-675 Slice 9, Designer III) re-audit of the remedy delta against RL-1835 and RS-1882
status: draft
created: 2026-10-25   # drafted 2026-10-22 under working id 8158; minted 2026-10-25 as RS-1883
owner: auditor
tree: 05b5a865f822565b901e3892ff295d6651f7de74
phase: P2
work: WK-675
corrected_by: []
relates: [SL-1554, PL-1546, RL-1835, RS-1882]
---

# RS-1883 — SL-1554 re-audit of the remedy delta

*(Working id 8158, reserved by the lead. Written by `aud-1554b`, 2026-10-22 13:2x BST. Check 31 on this id is expected until the mint.)*

## Question

RS-1882 found B1 (no RED/GREEN record in LG-1881), N1–N3 (dashed edges, enabled save, slug-change reset untested) and (v) (an undisclosed choice). Does the delta `ce22af6e..ab48b63e` close them? Read-only: no test, gate or DB was run; the vitest results below are read from the logs, not re-run.

## Method

Range `origin/main` (`f3462d8fc1336dc4583fe8a7af92fed399993a55`)`...sl-1554-wk675-s9` (`ab48b63ef052a0478fe163a9bef3883c938be44a`, tree `05b5a865f822565b901e3892ff295d6651f7de74`; `git rev-parse` of the local branch and of `origin/sl-1554-wk675-s9` agree). The delta since RS-1882 is 4 commits (`git log ce22af6e..ab48b63e`): `ab405217` (three test files, +46 −0), `fe8b8cae`, `a9797eea`, `f8bf2a19` (LG), `f41c918f` and `ab48b63e` (LG). `git diff --name-only ab405217 ab48b63e` lists only the LG file; `git diff ce22af6e ab405217 -- frontend` touches only `__tests__` files. No product code changed in the delta. Evidence read: the LG at `ab48b63e`, every log in `~/gi-pricing-plan.local/scratch/sl1554-vitest/` (12 files).

## B1 — RED/GREEN record: MET

The LG entry "RED/GREEN record (RS-1882 B1)" quotes four RED and eight GREEN summary lines with rc and log path. Compared with the logs (`grep -aE "Test Files|Tests  |^rc="`):

- RED: `graphMounts` `4 failed | 1 passed (5)` rc=1; `MountInspector` `6 failed (6)` rc=1; `DagDesignerMounts` `11 failed (11)` rc=1; `RatingDesignViewMounts` `3 failed (3)` rc=1. All four match; 4+6+11+3 = 24, the figure relayed earlier.
- GREEN: `graphMounts` 5, `MountInspector` 8, `DagDesignerMounts` 12, `NodeNavigator` 8, `DagDesigner` 6, `DiffOverlay` 5, `RatingDesignViewMounts` 4, `RatingDesignView` 7, each `passed` with rc=0. All eight match; 5+8+12+8+6+5+4+7 = 55, as the LG says.
- Which commit each ran at: the kept RED logs carry mtimes 12:16:35–12:16:59Z, after `ab405217` (12:16:33Z, `git log --format=%aI`); the test counts at `7576489f` are 11/6/3/5 (`grep -cE '^\s*(it|test)\('` of `git show 7576489f:<file>`) and equal the RED totals, while at `ab405217` they are 12/8/4/5 and equal the GREEN totals. So the counts prove the RED ran on the pre-N1–N3 test files and the GREEN on the post-N1–N3 ones. The log's `RUN` line names the `sl-1554` worktree. The checked-out sha at run time is not in any log; the counts are the only proof, and they suffice.
- The discarded first RED attempt is disclosed in the LG (hook rejected a trailer, checkout aborted, four logs deleted, RED re-run after the commit).
- `7576489f` is the test-only commit before the first code commit `c91c3223` (10:50:36Z vs 10:50:40Z), so a RED at it is a RED against the stub code.

Limit, not a defect: one run each, and the LG says so.

## N1–N3 — each asserts what RS-1882 asked: MET

- **N1** (`DagDesignerMounts.test.ts`, +11): after the mount renders, the `.vue-flow__edge[data-id*="m_refund"] path` has `style.strokeDasharray` `"6 4"` and the `m_fees` edge `""`. A missing edge returns `null`, which fails both `toBe`s, so the test cannot pass vacuously. It asserts the dashed edge of the conditional mount and the solid edge of the unconditional one (RL-1835 (i) 4).
- **N2** (`RatingDesignViewMounts.test.ts`, +15): pins omit the mount's version; asserts the not-pinned text, `aria-disabled="false"` on "Save as new version" (`RatingDesignView.vue:164`, `:aria-disabled="!canSave"`), then a click and `saveRatingAlgorithm` called once with "Saved as motor-gb@2". This is RL-1835 (ii) 3's "Testable as", stronger than RS-1882 asked.
- **N3** (`MountInspector.test.ts`, +19): a pin of another slug emits `ref`, `inputs` `{}`, `outputs` `{}`; another version of the same slug emits `ref` and keeps `FEES.inputs` and `FEES.outputs`. Both halves of RS-1882 N3 are there.
- None weakens an existing assertion: `git diff ce22af6e ab405217 -- frontend` is +46 −0, three files, additions only.

Observation: the LG says N1–N3 "pin existing behaviour; no red is possible", so no negative control was run for them (RL-1835's "shown red once" lists nine violation tests, which are the RED set above; N1–N3 are additions beyond it). Non-blocking; the lead may ask for a one-off mutation of `DagDesigner.vue:119` and `setRef`.

## (v) the slug-change reset: named, with its reason, contradicts no clause

The LG names it ("ruled implementation within RL-1835's intent", citing the to-lead entry "2026-10-22 13:15:28 BST" as relayed by lead 26; I did not re-read that channel entry) with the reason (a different fragment's ports; compile refuses a map naming a port that does not exist), and N3 pins it. RL-1835 (i) 5 rules the select and the port rows, (iii) 1 the select's options; neither says what happens to the maps on a re-point, and none requires keeping them. `MountInspector.vue` `setRef` (`:44-47`) resets both maps only on a slug change. It contradicts no RL-1835 clause. **No return to the maintainer.**

## The empty-string observation: not a defect against a named clause

`setInput` (`MountInspector.vue:49`) stores `""` when an input field is cleared. The clauses that touch it: RL-1835 (i) 5 "every input port is required, `03:352`", and `03:352` "Every input port of the mounted sub-graph is mapped exactly once". The designer's duty under (i) 5 is to offer one row per input port; neither clause says the inspector refuses to store an empty name. `SubGraphRef.inputs` is `dict[str, str]` with no length rule, and the model docstring says completeness is "compile's to check". RL-1835 (ii) 4 says the port rows "prevent the unmapped and undeclared cases", and clearing a field lets an unmapped input back in as `""`; that sentence gives a reason, not a requirement, and (ii) 4 also leaves such checks to the compile route. So: **an observation, not a defect**; the compile route reports it. It is disclosed in the LG. If the maintainer wants the inspector to hold it, that is a new requirement (spec first, `CLAUDE.md` §0), not a fix to RL-1835.

## Findings

No `FD-` is filed. New defects in the delta: none (below).

None found. The delta has no product-code change, and the LG edits read against the logs and the diff above. One wording point: the LG's GREEN heading says "at `ab405217` (the branch head with N1–N3)"; the branch head is now `ab48b63e`, which differs from `ab405217` only in the LG file, so the claim is true of the code and tests.

## Still owed (from RS-1882 (vi), unchanged by this delta)

The full gate (both halves); the LG-1881 mint (working id 8141, `tree:` front matter `c35113b2`), its "PRs" and "MERGE-ACK" lines, closing acts and the SL-1554 `closed` row; the PR and CI; the re-merge of `origin/main` before the PR; the id sweep (`idsweep.sh`) before the PR.

## Proposal

**CLEAN for the remedy** (the verdict is the lead's): B1 and N1–N3 are met and (v) is named, reasoned and pinned without contradicting RL-1835. No `FD-` is filed. Everything in "Still owed" remains before the slice can close.
