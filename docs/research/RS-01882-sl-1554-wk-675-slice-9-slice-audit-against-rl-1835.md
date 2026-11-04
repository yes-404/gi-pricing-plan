---
id: RS-1882
family: research
kind: audit
title: SL-1554 (WK-675 Slice 9, Designer III — sub-graph mounting) slice audit against RL-1835
status: draft
created: 2026-10-25   # drafted 2026-10-22 under working id 8156; minted 2026-10-25 as RS-1882
owner: auditor
tree: 578cdb200de333e1725a03740ab516d3e891537d
phase: P2
work: WK-675
corrected_by: []
relates: [SL-1554, PL-1546, PL-1286, RL-1835, RL-1344]
---

# RS-1882 — SL-1554 slice audit

*(Working id 8156, reserved by the lead. Written by `aud-1554`, 2026-10-22. Check 31 on this id is expected until the mint.)*

## Question

Does the tree `origin/main...sl-1554-wk675-s9` meet RL-1835's acceptance, and what does LG-1881 fail to evidence? Read-only: no test, gate or DB was run; test results below are the seat's, read from the ledger or not at all.

## Method

Range `origin/main` (`f3462d8fc1336dc4583fe8a7af92fed399993a55`)`...sl-1554-wk675-s9` (`ce22af6eea3afad18ba7023fd6b09e2aae2dc111`, tree `578cdb200de333e1725a03740ab516d3e891537d`), 16 files, +972 −67 (`git diff --stat origin/main...ce22af6e`). Scope first, from `RL-1835` (i) 1–7, (ii) 1–4, (iii) 1–4 and its "Acceptance" list, `PL-1546` row 8, to-lead "2026-10-21 15:39:13 BST" with its 15:39:19 correction, and the resume GO "2026-10-22 11:44:34 BST"; evidence second, by reading the diff. `7576489f`, `452b401e` and `e411c85a` are ancestors of `ce22af6e` (`git merge-base --is-ancestor`, rc 0 each).

## (i) Write set

`git diff --name-only origin/main...ce22af6e` outside `frontend/`: `docs/INDEX.md`, `docs/roadmap.md` (SL-1554 row `draft → active` plus its one activation line), the LG-1881 file. The same diff restricted to `packages`, `backend`, `docs/contracts`, `docs/specs`, `frontend/src/router`, `frontend/src/api/generated` lists 0 paths. **MET** — RL-1835 "What it obliges" and the LG's file condition with S8 (no router edit).

## (ii) Generated types

`frontend/src/api/subGraphs.ts` (12 lines) imports `components["schemas"]["SubGraph"]` from `./generated/schema` and `SubGraphRef` from `./generated/schema.requests`; its one function reads `GET /sub-graphs/{slug}@{version}`. No hand-written shape. **MET** ((i) 5, §2/§3). Note: LG Task 1 writes `getSubGraph(ref)`; the code is `(slug, version)` — the LG already discloses it.

## (iii) The two test edits after the WIP commit

- **`7576489f`** (`graphMounts.test.ts`, 1 line: source `s_minprem` → `s_office`). In `frontend/src/components/dag/__tests__/fixtures.ts` `s_office` (line 112) produces `office_premium_minor` first and `s_minprem` (line 124) second. Main's `edgesOf` takes the first producer (`origin/main:frontend/src/components/dag/graph.ts`, `if (!producer.has(name))`), the branch's keeps that (`list.length === 0 || (node.mount …)`), and RL-1835 (i) 3 says "the same producer → consumer rule as a step's". The WIP test contradicted the ruling; the edit makes it agree. Commit precedes `c91c3223` (the first code). **MET**; no assertion weakened.
- **`452b401e`** (`DagDesignerMounts.test.ts:72`, adds `await screen.findByLabelText(/sub-graph mount m_refund/)`). One added line; the issue assertion (`m_refund closes a cycle` inside `m_refund`, absent from `m_fees`) is untouched. LG-1881 records the cause (synchronous `node()` before Vue Flow mounted: `no node m_refund`) and the negative control (await kept, issue removed from the fixture → 1 failed, 10 passed). **MET** as to no weakening; the negative control is the seat's, not re-run here.

## (iv) RED/GREEN record

LG-1881 at `ce22af6e` holds the two entries above (the e411c85a stub and misplaced line; the :72 race). It does **not** hold the RED run (4 files, 24 failures at `7576489f`) or the GREEN run (8 files at the head) the brief relays: `grep -niE "RED|GREEN|24|rc "` over the LG finds none, and no commit body carries them. RL-1835 "Acceptance" requires each violation test "shown red once". **The record is absent from the ledger; I could not verify the numbers from a primary source.** The two owed lines (empty stub of `MountInspector.vue` at `e411c85a`; the misplaced "migration not applied" line) are both written (entry 2026-10-22, first), as GO item 3 asked. Reading `e411c85a` it is true the stub is 6 lines per the LG; not re-read here.

## Scope against evidence (RL-1835 items)

| Item | Evidence (file / test) | Proposed verdict |
|---|---|---|
| (i)1 a mount is a node, id = `mount_point` | `graph.ts` `nodesOf`; `DagDesignerMounts.test.ts:49` "one node per mount, its id the mount_point" | MET |
| (i)2 collapsed: mount_point, slug@version, badge | `MountNode.vue`; same test file | MET |
| (i)3 edges by the step rule | `graphMounts.test.ts:11,19,30` | MET |
| (i)4 badge text + dashed border + dashed edges | border/badge `DagDesignerMounts.test.ts:56`; edge flag `graphMounts.test.ts:30`; the style `strokeDasharray` is applied at `DagDesigner.vue:119` and **no test asserts it** | MET for border/badge; edge rendering delivered but untested |
| (i)5 inspector: version select, mount_point, port rows, two purposes boxes, none → no key | `MountInspector.vue`; `MountInspector.test.ts:21,29,39,48,57,64` | MET |
| (i)6 add/remove, keyboard (`NodeNavigator`) | `DagDesignerMounts.test.ts:102,109,116,126` | MET |
| (i)7 diff marks the mount and no other | `DagDesignerMounts.test.ts:84`; `DiffOverlay.vue` lists `sub_graph_mounts` | MET |
| (i) a validate issue at `mount_point` shown on the node | `DagDesignerMounts.test.ts:67` (negative control in LG) | MET |
| (ii)2 no pin writing; no write to `/rating-versions` | `RatingDesignViewMounts.test.ts:55` (asserts no write path starts `/rating-versions`) | MET |
| (ii)3 not-pinned warning, save stays enabled | warning `DagDesignerMounts.test.ts:77`; **"save control stays enabled" is not asserted** | warning MET; enabled-save untested |
| (iii)1 select = `pins.sub_graphs` | `MountInspector.test.ts:57` | MET |
| (iii)4 empty pins: add disabled with a text reason | `DagDesignerMounts.test.ts:133`; `RatingDesignViewMounts.test.ts:74` | MET |
| (iii)3 no model-schema/backend/contracts change | write-set check above | MET |

## (v) A choice not in RL-1835

`MountInspector.vue` `setRef`: when the picked pin has a **different slug** from the current one, `inputs` and `outputs` are reset to `{}`; the same slug keeps them. RL-1835 (i) 5 and (iii) 1 rule the select and the port rows but not this. It is consistent with the ruling's intent (a port map for another fragment's ports would name ports that do not exist, which compile refuses), and it is not silent data loss of a valid map. **Outside the ruling, not contradicting it; no test covers it, and the LG does not disclose it.** Proposal: the lead adopts it, and LG-1881 names it and one test pins it. Related, small: `setInput` stores `""` when a field is cleared, so an empty parent name can be saved for a required input (the ruling says every input port is required).

## (vi) Owed, not defects

The full gate (both halves); the LG-1881 mint (still working id 8141 at `ce22af6e`, `tree:` front-matter `c35113b2`), the LG "PRs" and "MERGE-ACK" lines, its closing acts and the SL-1554 `closed` row; the PR and its CI; the re-merge of `origin/main` before the PR (S8/S10/S11 may merge first, to-lead 15:39:19); a regenerated `docs/INDEX.md` after any mint.

## Findings

No `FD-` is filed: B1 and N1–N3 are slice-ledger and test gaps for the executor to close before the PR, not product defects. The proposal follows.

## Proposal

**NOT-CLEAN, one blocking item** (the verdict is the lead's): (B1) LG-1881 carries no RED/GREEN record, so RL-1835's "shown red once" is not evidenced in a durable artifact. Add the vitest result lines (file count, failed/passed, the commit each ran on) to the LG. Non-blocking: (N1) no test asserts the dashed-edge style; (N2) no test asserts save stays enabled with an unpinned mount ((ii)3 "Testable as"); (N3) the slug-change reset of (v) is undisclosed and unpinned by a test. Everything else in RL-1835 is MET by the code and tests read.
