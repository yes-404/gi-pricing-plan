---
id: FD-8401
family: finding
title: WF-701 C4 and H4 claim a notification that 03 FR-272 defers to WK-688
status: closed
created: 2026-11-06   # working id 8401, drafted 2026-11-06 (aud-wk674b), filed by exec-cr8315
owner: auditor
tree: 9b18810ae6af807d6c1c4f3bae5556b4ab02c96d
corrected_by: []
relates: [WK-674, FR-272, NFR-494, FR-268, RL-1252, CR-8315]
---

# FD-8401 — WF-701 C4 and H4 claim a notification that FR-272 defers

*(Filed 2026-11-06 from working id 8401, in the PR of CR 8315, as ruled by to-lead "2026-11-05 12:02:53 GMT" ("FD CANDIDATES: C ... FILE, LOW, owner WK-674's docs acts") and `to-lead` "2026-11-06 09:58:14 GMT" (4).)*

## Finding

`docs/workflows/WF-00701-deploy-and-monitor.md` step C4 says "emits the Audit Event and notification" and step H4 says "emits an Audit Event and a notification". `03` FR-272, as amended by `RL-1252`, claims no notification channel until WK-688, Phase 4. Roadmap §12's dated line defers A3's notification and names A3 only, so C4 and H4 claim what A3 no longer does.

## Evidence

Both lines at `9b18810a`; `git diff --stat 2f108b1e 9b18810a -- docs/workflows` is empty (CR-8315 §5c).

## Severity

LOW: a journey document, no behaviour.

## Disposition

Which side is wrong is `CLAUDE.md` §0's question; the specification (FR-272 as amended by `RL-1252`) is the later decision, so the journey is the side that is fixed. A dated line on each of C4 and H4, citing `RL-1252` and naming WK-688, lands in the same PR as this record (the maintainer, "2026-11-06 09:58:14 GMT" (4): "fix it where it is known"). The step text is not edited. No row is owed by WK-674.

***Resolved 2026-11-06*** — closed in place by the executor: the dated lines are on both steps, in this PR. This PR; its number, squash commit and merge date are written at the merge's date-of-record
