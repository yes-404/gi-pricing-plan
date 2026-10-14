---
id: FD-8053
family: finding
title: RatingDesignView.test.ts FR-1530 awaits the lazily imported DagDesigner chunk with findByLabelText's 1000 ms default, so it fails on main under load
status: active
created: 2026-10-14
owner: auditor
tree: beee5ebedcfebc03c1658728442827960975392a
corrected_by: []
relates: [WK-1178, FD-8049, FR-1530, P2]
---

# FD-8053 — a 1000 ms wait races a lazy chunk: FR-1530 fails on main when the box is loaded

*(Filed under working id 8053, reserved by the lead; a minter folds it into the docs batch.
Authority: the maintainer's (by delegation) entry "2026-10-14 17:51:06 BST — SL-1702's FE red:
MAIN's load-sensitive test, NOT a slice defect" in `channel/to-lead.md`. Citations read at
`origin/main` `beee5ebedcfebc03c1658728442827960975392a`, written 2026-10-14 17:52:38 BST.)*

## Finding

**Severity: MEDIUM, proposed by the auditor (the maintainer's entry proposes it). Owner WK-1178.**

`frontend/src/views/__tests__/RatingDesignView.test.ts:65-73`, "FR-1530: loads the algorithm the
version pins, and draws one node per step", renders `RatingDesignView` and awaits, for each step,
`screen.findByLabelText(`${step.type} step ${step.label} (${step.step_id})`)` (`:68-70`). Those
labels are drawn by `DagDesigner`, which the view loads as
`const DagDesigner = defineAsyncComponent(() => import("@/components/dag/DagDesigner.vue"))`
(`RatingDesignView.vue:22`, used at `:205`). The first `findByLabelText` therefore waits for a
dynamic import of the chunk (the comment at `:21` says it keeps `@vue-flow` in its own lazy chunk), and
testing-library's `findBy*` has a 1000 ms default timeout. No `asyncUtilTimeout` or `configure(` setting
exists in `frontend/` (`git grep -nE 'asyncUtilTimeout|testTimeout|configure\(' origin/main -- frontend`: 0
hits). When the box is loaded the import takes longer than 1 s and the test fails with
`Unable to find a label with the text of: input step Driver age (s_in_age)`.

### §0 classification — which side is wrong

**The test (its wait) is wrong; the view is correct.** The lazy chunk is intended and documented
(`:21`); a user waits for a chunk without harm. The test asserts "within 1000 ms of mount the lazy
chunk is loaded and drawn", a latency claim the requirement (FR-1530: load the pinned algorithm and
draw a node per step) does not make. The same file's other six tests pass at the same load because
they await the view's own "Algorithm version" label (`:61`, `:77`, `:100`, `:119`, `:131`), which is not
behind the lazy import.

### Evidence, by run, 2026-10-14 (recorded as the lead reported it in the entry above)

| Run | Tree | Load | Result | Failing at |
|---|---|---|---|---|
| SL-1702, ×3, `RatingDesignView.test.ts` | head `3e087672` | ≈ 12 | 0 of 3 passed | 1024, 1098, 1087 ms |
| CONTROL: sl-1455 ×3; its frontend is identical to main's (`git diff origin/main <head> -- frontend` = 0 files) | sl-1455 head | 12.9 – 13.4 | 0 of 3 passed | 1022, 1020, 1085 ms |
| SL-1695's gate | | 6.37 | passed | |

Logs for the SL-1702 runs: `/home/puzhenhao1989/.claude/jobs/b6860f8f/tmp/fe1530/run{1,2,3}.log`
(read by the auditor: each shows `7 tests | 1 failed`, the FR-1530 test failing at 1024, 1098 and
1087 ms with the error above). The control's output is in the lead's log at "2026-10-14 17:51:00 BST"
(from-lead), not re-read here. Every failing time sits just above 1000 ms: the `findBy` timeout, not a
slow assertion. SL-1702 changes no frontend file, so the control decides: **main itself fails under
load**. The maintainer's entry pre-classifies this exact failure (FR-1530, load > 6, no slice
frontend change) for today's gates; any other frontend failure is classified separately.

## Remedy (ruled in the 17:51:06 entry)

A deterministic wait for the lazy component: await the chunk (`await import("@/components/dag/DagDesigner.vue")`
before the first `findBy`, which resolves the same module the view's `defineAsyncComponent` loads) or
the component's own ready signal, **never a blanket timeout raise** and never a sleep. **Red first**,
by forcing a slow chunk load: mock the dynamic import to resolve after more than 1 s (a mocked delayed
import, injected, not a real wait on the box), red on today's test, green once the test awaits the
chunk. Land early: it costs gate classification in every loaded gate.

## Sweep (item: other `findBy*` against lazily imported components)

Predicate A (lazy component declarations):
`git grep -nE 'defineAsyncComponent|[^a-zA-Z]import\(' origin/main -- frontend/src`, excluding `frontend/src/api/generated`.
Predicate B (tests that go through a lazy route): `git grep -nE 'from "@/router"|from "\.\./index"|router/index' origin/main -- frontend/src`.

| Hit | Reading | Exposed? |
|---|---|---|
| `views/RatingDesignView.vue:22` (`defineAsyncComponent`) | the only `defineAsyncComponent` under `frontend/src` | **YES**: test `RatingDesignView.test.ts:65` awaits nodes the chunk draws. Other tests in the file await view-owned labels |
| `router/index.ts:31-305` (28 `() => import("@/views/…")` route components) | lazy route chunks | no: tests that import the router use `routes`/`router.resolve` only (`DiagnosticsView.test.ts:9`, `ModelDetailView.test.ts:5`, `ModelComparisonView.test.ts:4`, `:102-103`, `router/__tests__/index.test.ts:4`, `routeGraph.test.ts:9`) or `await router.push("/data")` (`guard.test.ts:24,30`) with no `findBy` against the loaded view; views are rendered directly, not through the router |
| `router/__tests__/routeGraph.test.ts:20,25` | test-local lazy route stubs | no `findBy` |
| `components/__tests__/FactorCreateForm.test.ts:109`, `ModelSelector.test.ts:137`, `views/__tests__/ModelSpecBuilderView.test.ts:157,184`, `RatingVersionView.test.ts:98` (`await import("@/api/problem")`) | dynamic import of an already-loaded module inside a test | no: not a component under render |
| `ModelComparisonView.test.ts:31`, `ProfileView.test.ts:16` (`importOriginal<typeof import("vue-router")>`) | type-position `import()`, not a load | no |

So the pattern occurs **once**. `DagDesigner` is also rendered directly, not lazily, by
`DagDesigner.test.ts`, `DagDesignerValidation.test.ts` and `DiffOverlay.test.ts`, which are not exposed.
Limit of the sweep: it covers `frontend/src` test files at the stated tree; it does not time other
`findBy` waits against slow *non-lazy* work (an API mock that resolves late), a different class.

## Why MEDIUM, proposed

- Against HIGH: no product behaviour is wrong; the view works.
- Against LOW: it fails on main under load, 0 of 3 in two independent trees at load ≥ 12, and each
  occurrence costs a gate cycle (the maintainer's entry: it "will recur in every loaded gate today").
- Re-rate trigger: HIGH if a gate-time frontend red of this shape is mistaken for a slice defect
  and a real regression is let through on that pre-classification.

## Disposition

The event that next discharges it: the WK-1178 slice in P2 that awaits the lazy chunk in
`RatingDesignView.test.ts`, red first with a delayed-import mock, and no timeout change. Same
family as FD-8049 (a test racing a time-dependent resource), different mechanism.
