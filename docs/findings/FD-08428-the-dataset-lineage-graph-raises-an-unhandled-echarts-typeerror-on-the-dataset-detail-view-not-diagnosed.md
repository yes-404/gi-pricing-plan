---
id: FD-8428
family: finding
title: The dataset lineage graph raises an unhandled ECharts TypeError on the dataset detail view; not diagnosed
status: active
created: 2026-11-11
owner: auditor
tree: 374a22bf33ad
corrected_by: []
relates: [LG-8424, LG-2107, CR-2110, WK-1914]
---

# FD-8428 — The dataset lineage graph raises an unhandled ECharts TypeError on the dataset detail view

*Working id FD 8428, given by lead 33 (`from-lead` 2026-11-11); unminted on this branch. Filed by the auditor (aud-p2close, Claude Opus 5.5) on lead 33's disposition (3) of 2026-11-11, which set the severity, the owner and the first step.*

## Finding

During the user's page walk at the P2 exit demo (run r1, Wed 11 Nov 2026, frozen tree `374a22bf33ad`; `LG-8424`), opening a dataset's detail page logged an ECharts warning that the chart container has no size, and then an unhandled promise rejection, a `TypeError`, inside ECharts' graph-view coordinate system. The page that was open is the dataset detail view. Its lineage request is the last API call before the warning. At `374a22bf`, `frontend/src/views/DatasetDetailView.vue:17` imports `LineageGraph.vue` and mounts it at `:241-249`, under `v-if="lineage"`. `LineageGraph.vue:90` is the frontend's only ECharts series of `type: "graph"` (`git grep -n -E "type: ?['\"]graph['\"]" 374a22bf -- frontend/src` prints that one line), and `:153` sets `autoresize`. The rejection did not stop the user's walk. It touches no money path and no journey step. Whether the graph then drew, and whether the cause is a zero-size container on first paint, is **not diagnosed**.

## Evidence

`~/gi-pricing-plan.local/scratch/exit-demo-2026-11-11/r1/demo.log` (sha256 prefix `857b5f6a65a1`), verbatim. The lineage request, `:3537-3538`:

```
{"ts":"2026-11-11T10:54:12.011Z","level":"INFO","logger":"app.request","message":"request completed","trace_id":"3b5386c2d43eff42c5913db343494ce6","method":"GET","path":"/api/v1/dataset-versions/01a1ca2f-8262-7b58-845c-44a2a47598ba/lineage","status":200,…
{"ts":"2026-11-11T10:54:12.011Z","level":"INFO","logger":"uvicorn.access","message":"127.0.0.1:48528 - \"GET /api/v1/dataset-versions/01a1ca2f-8262-7b58-845c-44a2a47598ba/lineage HTTP/1.1\" 200"}
```

`:3539-3550`:

```
10:54:12 AM [vite] (client) [console.warn] [ECharts] Can't get DOM width or height. Please check dom.clientWidth and dom.clientHeight. They should not be 0.For example, you may need to call this in the callback of window.onload.
10:54:13 AM [vite] (client) [Unhandled rejection] TypeError: Cannot read properties of null (reading '0')
 > copy$1 node_modules/.pnpm/zrender@6.1.0/node_modules/zrender/lib/core/matrix.js:14:15
 > legacyCopyOverallTrans node_modules/.pnpm/echarts@6.1.0/node_modules/echarts/lib/coord/View.js:382:4
 > viewCoordSysUpdateOverallTrans node_modules/.pnpm/echarts@6.1.0/node_modules/echarts/lib/coord/View.js:369:2
 > viewCoordSysUpdateTransform node_modules/.pnpm/echarts@6.1.0/node_modules/echarts/lib/coord/View.js:314:2
 > viewCoordSysSetViewRect node_modules/.pnpm/echarts@6.1.0/node_modules/echarts/lib/coord/View.js:307:4
 > createViewCoordSysSimply node_modules/.pnpm/echarts@6.1.0/node_modules/echarts/lib/component/helper/roamHelper.js:156:13
 > createViewCoordSys node_modules/.pnpm/echarts@6.1.0/node_modules/echarts/lib/chart/graph/createView.js:94:25
 > injectCoordSysByOption node_modules/.pnpm/echarts@6.1.0/node_modules/echarts/lib/core/CoordinateSystem.js:288:17
 > node_modules/.pnpm/echarts@6.1.0/node_modules/echarts/lib/chart/graph/createView.js:60:4
 > GlobalModel.<anonymous> node_modules/.pnpm/echarts@6.1.0/node_modules/echarts/lib/model/Global.js:593:11
```

Counts over the whole log: `grep -c "Unhandled rejection\] TypeError"` = 1; `grep -c "ECharts\] Can't get DOM width"` = 1. The rehearsal's logs do not show it: `grep -rl "Cannot read properties of null (reading '0')" ~/gi-pricing-plan.local/scratch/exec-sl1913/` prints nothing. That is not evidence of absence, because no rehearsal row opened a dataset's detail page in a browser.

**Context only, not this finding.** The same walk logged `[Unhandled rejection] ProblemError: Development identity is enabled; supply x-dev-principal-id.` twice (`demo.log:3500`, `:3521`; `grep -c` = 2). The rehearsal's `scratch/exec-sl1913/r5/demo.log` shows the same message 8 times (`grep -c 'ProblemError: Development identity'`), first at `:5604`. `LG-2107` row 6 records it "on every load".

## Disposition

Register decision: **deferred with an owner: WK-1914** (Provenance and diagnostics views), owner by name. Lead 33 decided this on 2026-11-11, with severity LOW: the rejection did not stop the user's walk, and no money path is touched. First step: reproduce it in a browser at the frozen tree `374a22bf33ad`, and say whether the cause is the zero-size container on first paint (the `Can't get DOM width or height` warning one second before the rejection). Only then a fix, or a dated ruling. The user saw no visible failure: they reported every page looked good, so this is a console error, not a visible failure (the maintainer's entry of to-lead "2026-11-11 11:52:22 GMT", which accepts the finding as filed).
