---
id: RS-9801
family: research
kind: spike
title: Can Vue Flow carry WK-675's designer at 200 steps — pan/zoom fps, live connection checks, keyboard focus and delete, and the bundle cost?
status: draft
created: 2026-09-28
owner: executor
tree: 85e33e75e2312ef08d12408adb5df4a33d793a8c
phase: P2
work: WK-675
corrected_by: []
relates: [FR-212, FR-240]
---

# RS-9801 — Vue Flow for the WK-675 DAG designer at 200 steps (spike F2)

Spike F2 of Track F, run 2026-09-28 by the executor `spike-f2`. The timebox started at
11:36:37 BST. The last measurement ended at 12:19:59 BST. **The verdict in this record
is the executor's proposal. The deputy decides on this record**, and the Decision section
quotes that decision whole.

**Clocks.** Every stamp is Europe/London (BST) unless it is marked otherwise. The logged
`uptime` lines print the machine clock, which is UTC and reads one hour behind BST. So
the logged `10:44:47` is 11:44:47 BST. This record quotes `uptime` load figures with
their logged UTC time, marked "UTC".

## Question

`03-rating-engine.md` §5.3 describes the DAG designer as a "Vue Flow canvas with typed
nodes per step type, live validation (cycles, unresolved refs, type mismatches) shown on
the node". NFR-489 sizes a motor structure at about 200 steps. Reading the library's
documentation cannot settle four things: whether the canvas stays smooth at that size,
whether validation on every hover is cheap enough, whether keyboard users can focus and
delete a node, and what the library costs in the bundle.

The deputy set the question and the pass criterion. The entry below is quoted whole
from the lead's channel file (`~/gi-pricing-plan.local/channel/to-lead.md`). F2 is the
second item under "Needs a spike".

```text
## 2026-09-28 11:33:12 BST · deputy · THE OQ STREAM: 15 items that could block Phase 2, each RULED by delegation or sent to a spike. Two new tracks: E (file the decisions) and F (timeboxed spikes)

**Maintainer decisions by delegation (deputy, on the maintainer's instruction of 2026-09-28 11:24 BST), on read-only research at origin/main `df8e5811`.** I re-verified the key counts: `open-questions.md` holds 2 open OQs (OQ-554, OQ-620) out of 72 rows, and the roadmap's "Before Phase 2 — 13 (0 open)" holds. Most blockers are unruled decision points outside the OQ log. The team must re-read every file:line at main before writing, since several register line numbers have drifted.

### Decided now (Track E files each through `spec-change`: an OQ row with options, recommendation and my dated line as "decided", mirrored in the spec's §10, or a register/RL entry where no OQ fits)
- **E1 · F60 + F59 (`03` §5.2 signatures vs code):** the code is right. Amend `03` §5.2 for all five items: `to_wire`; the six public `operations.py` functions (e.g. `seed_from_model`, `diff_vs_previous`, `diff_vs_seed`); `assert_integer_minor_round_trip`; `build_scoring_result`; and `KeyFilter`'s real home, `model_schema/rating.py`. **This is WK-672's Slice 1** (F60 says "before WK-672 opens"), so it goes in Track D's RL/Slice 1, not a separate PR.
- **E2 · WK-690 grammar (`02` §4.6) vs the parser: the spec is right for the objective grammar.** The parser is to gain `where()` (SymPy `Piecewise`, evidenced), refuse bare comparisons, `%` and ternaries outside `where`, and enforce the node-count and depth limits. File it as a new OQ with (a) spec right / (b) parser right, recommendation (a), decided (a). The fix is WK-690's first slice, not today's.
- **E3 · WK-690's start gate is MET:** the certification machinery shipped in WK-661 (CR-754) and has run for a phase (P1b accepted closed 2026-08-27, CR-822). Record it as a dated line in WK-690's roadmap row. Note there that WK-690 must add `sympy` (0 hits in `uv.lock`) together with the `skills-map.md` update.
- **E4 · `structural_diff` in the rating_version evidence floor:** the owner is **WK-673**. At submission it persists FR-219's diff as a blob and registers the verifier, before WK-673 wires FR-257's gate (RL-881). This is a spec change in `06` naming the owner and the mechanism.
- **E5 · F-W10-3 (no route creates a rate-table version from manual edits):** add the route to `03` §5.1 now, following the existing create paths (a change note is required; confirm, then create). Owner WK-675's editor slice. Spec change first, as the row demands.
- **E6 · F48 (NFR-499 per-client rate limits):** a **shared Redis counter, per tenant** (ADR-710 makes Redis per-tenant; an in-process limiter "is not a limit"). Record the decision on the F48 row now; WK-674's map plan builds it.
- **E7 · F54 (service-account keys minted only for the first environment):** the owner is **WK-674**, and the shape is **one key per granted environment**. That shape isolates a leaked key to its environment and matches ADR-710's boundary. A spec change in `07` (FR-430) comes first.
- **E8 · OQ-620 (does a rate table version have an approval lifecycle?): decided, option (b) as recommended.** Nothing contradicts it, and its deciding test cannot be measured in Phase 2. The decision is taken now so that WK-675's editor slice does not inherit it.
- **E9 · OQ-554 (does anything check that a cited FR still says what the step claims?): decided, option (b),** a review step at each close. Put it on the gate table's "Deferred / any time" row as decided.
- **E10 · OQ-550:** its trigger fired (#257 added a `ChartFigure` caller; there are now 13 call sites). **Re-open it as a WK-675 entry decision**, due at WK-675's map plan, and fix the gate-table cell that shows it struck.
- **E11 · housekeeping:** set the P1a/P1b roadmap headers to `status: closed` (P1b accepted 2026-08-27, CR-822). Make the §2 "Where the project is" row a pointer to the phase headers, not a restatement (RFC-756). Correct PL-930:109's stale citation of `03:597` to `03:603` in Track D's RL.

### Needs a spike (Track F; each is TIMEBOXED to 3 hours today in a scratch worktree, merges nothing, and reports as an `RS-` research record with its measurements, pass criterion and verdict; I decide on the record)
- **F1 · WK-674 bundle switchover across workers:** N workers at 200 rps with a push-at-deploy switch (RL-876/RL-882). Pass: zero mixed or dropped responses (bundle hash asserted on every response) and switch ≤ 30 s including warm-up (NFR-494). If 3 h is not enough, the RS reports the partial measurement and what remains.
- **F2 · WK-675 Vue Flow designer:** a 200-step structure, typed custom nodes, and live validation with `isValidConnection`. **The pass criterion is set here:**
  - pan/zoom at ≥ 30 fps on the dev build;
  - a connection check under 50 ms at 200 nodes;
  - node focus and delete work from the keyboard;
  - the bundle-size delta is reported.
- **F3 · WK-673 attribution method:** file the OQ first, with options (a) isolated plus cumulative in a declared step order, with an explicit interaction-residual line so the parts reconcile to the total; (b) Shapley over steps; (c) cumulative only. Recommendation (a). The spike runs on freMTPL2 and measures the size of the residual and how much the order changes the result. I decide on the record.
- **F4 · WK-672 Slice 3 property assertions:** the **language is decided now as a structured union of FR-261's five classes** (declarative JSON artifacts, CLAUDE.md §2; no free-text expressions). The spike covers only **seed determinism**: does a persisted seed reproduce the same cases with a pinned generator? It also covers the dependency question: `hypothesis` is dev-only, so the choice is a runtime dependency or our own seeded numpy generator. Recommendation: our own generator, unless the spike shows otherwise. **F4 is on Track D's critical path, so run it first.**

### Organisation
- **E** is one decision-maker, with two PRs at most: E2 to E10 as one spec/OQ PR, and E11 as a roadmap-only PR (or folded into the next roadmap-touching PR). E1 rides Track D.
- **F** is up to four executors, one per spike, in worktrees under their job dirs. Spikes run no full gate, so the gate slots stay with Track D. Each RS id is minted at its turn.
- The id log and first-ready-first-merged apply to E and F as to A–D.
- **Order:** F4 and E1 first (Track D's path), then E2–E10 and F1–F3 in parallel.
- Re-derive eta.md with E and F as their own bands.
```

**The pass criterion, verbatim from the entry above:**

- pan/zoom at ≥ 30 fps on the dev build;
- a connection check under 50 ms at 200 nodes;
- node focus and delete work from the keyboard;
- the bundle-size delta is reported.

## Method

**Trees.** The spike ran in a scratch worktree detached at origin/main `df8e5811`. The
spike code was never merged. It is kept under the salvage ref
`refs/salvage/2026-09-28/spike-f2`. The lead pushed `a3862e01` (the code and the first
logs). `a6f41714` is its child and adds the final gated logs under `pw/results/final/`.
This record was written against `85e33e75`.

**What was built** (scratch, under `frontend/src/components/dag/`):

- `graph.ts`. A deterministic 200-step structure over all seven step types of `03` §3.2:
  30 `input`, 10 `lookup`, 70 `table`, 5 `model_call`, 60 `expression`, 20 `constraint`,
  5 `output`, with 328 edges. It also holds `checkConnection`, the live validator behind
  Vue Flow's `isValidConnection`. The validator rejects a self-link, a source with no
  output, a target that takes no input, a type mismatch against the slot's declared type,
  a duplicate edge, and a cycle (FR-212, FR-240). It rebuilds its adjacency on every call
  and has no cache. That makes it the worst case on purpose.
- `StepNode.vue`. One typed custom node component, registered under each of the seven
  step types.
- `DagDesigner.vue`. The canvas, with `:is-valid-connection`, `:delete-key-code` set to
  Delete and Backspace, and `:only-render-visible-elements="false"`, so all 200 nodes are
  in the DOM.
- A route `/spike/designer`, unguarded for measurement. It sits in the real app shell, so
  the canvas is 1104 × 900 px inside a 1600 × 900 viewport.
- **The step data type is hand-written, and only because the spike had no other option.**
  `RatingAlgorithm` is in `model-schema` but not in the generated OpenAPI. See "What
  remains", item (a).

**Dependency.** `@vue-flow/core` 1.48.2, MIT licence, added with `pnpm add` in scratch
only.

**Environment.** 16 CPUs (Intel Xeon @ 2.20 GHz), shared with other spikes. After a load
breach from another spike (below), every measurement ran under `taskset -c 8-15`. Every
run was held by a load gate (`gate.sh`: wait until the 1-minute load is ≤ 12). `uptime`
was logged before and after each run. The final set also quotes each process's
`readlink /proc/<pid>/cwd` and `taskset -pc <pid>`. Every process in it (vite, node,
chrome-headless-shell, vitest) ran from the scratch tree on CPUs 8-15.

**Browser.** Playwright 1.63.0, chromium-headless-shell 153.0.8010.12. The lead approved
installing it into the scratch tree, user-space only. **Its renderer is SwiftShader, a
software rasteriser** (`ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero)))`).
That is a harder case than a user's GPU, and **it limits what the fps figures mean. It
is not a pass condition.**

**The build the fps come from: the Vite DEV build** (`vite --port 5391 --strictPort`,
started with `env -C <scratch>/frontend setsid taskset -c 8-15 pnpm exec vite …`). No
fps figure in this record comes from a production build. The bundle figures come from
`vite build`.

## Findings

### Criterion 1 — pan/zoom ≥ 30 fps on the dev build

**Instrument** (`pw/fps2.mjs`). Chrome trace `DrawFrame` events are counted over each
action: fps = (frames − 1) / span. The script also reports frame-gap p50, p95 and max,
and the `DroppedFrame` events. A `MutationObserver` on `.vue-flow__transformationpane`
proves that the viewport really changed during the action. Each action starts from the
same viewport (`setViewport({x: 400, y: 40, zoom: 0.17})`, so all 200 nodes are on
screen). The actions are:

- **pan-drag**: a pointer drag starting on a point proven to be `.vue-flow__pane` (by
  `elementFromPoint`). It is 400 moves out and 400 back, with no waits, so input never
  limits the rate.
- **zoom-wheel**: 240 back-to-back wheel events at ±25, alternating every 30 events.
- **viewport-transition-3s**: `setViewport({x: -600, y: -900, zoom: 1.2}, {duration: 3000})`.
  This is the d3-zoom transition that a zoom-to-fit uses, and it is limited only by
  rendering.

Command, per run:
`run.sh fps <scratch>/pw env PLAYWRIGHT_BROWSERS_PATH=<scratch>/.pw node fps2.mjs http://localhost:5391/spike/designer`

**Final set, N=5** (runs started 11:13:45–11:15:44 UTC; 1-minute load at run start
0.99–1.94):

- pan-drag: **59.2 / 59.7 / 59.9 / 59.8 / 59.6 fps**. 800 frames per run, gap p50
  16.6–16.7 ms, p95 17.8–18.4 ms, max 26.2–46.5 ms, 0–9 dropped frames. 401 transform
  mutations per run.
- zoom-wheel: **30.0 fps in all 5 runs**. 240 frames for 240 events, gap p95 34.5–35.5 ms,
  0–1 dropped frames.
- viewport-transition-3s: **59.8 fps in all 5 runs**. 178 frames over about 2.96 s, gap
  max 20.7–23.7 ms.

**Earlier set, N=5**, with the same instrument (runs started 11:05:06–11:07:06 UTC; load
1.76–2.66): pan-drag 58.7–59.6 fps, zoom-wheel 29.9–30.0 fps, transition 59.8–59.9 fps.
The deputy's decision quotes this set.

**The wheel figure is a ceiling of the input-dispatch harness, not a render limit.**
Playwright's `mouse.wheel` returns only after the renderer acknowledges the event. The
blank-page control (`pw/control.mjs`, N=3, runs started 11:02:52–11:04:21 UTC, load
1.25–1.82) sends the same 240 wheel events to a page with no Vue Flow. They take
7161–7186 ms, which is 29.8–29.9 ms per event. On the designer they take 7993–8013 ms,
which is 33.3–33.4 ms per event. So the dispatch rate is capped at about 30 per second
on both pages. The designer draws exactly one frame per event, 240 of 240. The renderer
adds about 3.5 ms per wheel event, which is well inside a 33 ms frame. The programmatic
transition exercises the same transform path without the harness cap and runs at
59.8 fps.

**The instrument I replaced, kept so that its failure stays on record.** The first
instrument (`pw/measure.mjs`, 10:52–10:55 UTC) counted `requestAnimationFrame` callbacks.
**It read 60 fps for pan and zoom while the pan never moved.**

- The drag started at (8, 890). That point is outside the canvas, because the app shell
  centres the canvas at x 248–1352.
- The rAF callbacks fire on every frame the main thread begins, whether or not anything
  is drawn.
- A second instrument, built a different way (`pw/verify.mjs`, N=3), exposed both
  faults. It found the viewport transform unchanged after the pan, and 0–1 trace
  `DrawFrame` events during it.
- That run's load also rose to 14.81 by its end.

None of its fps figures are used. Its live-validation and keyboard figures are also not
used, because the load went over 12 during the run. The same harness was re-run later
under the gate (below).

**Verdict, criterion 1: PASS**, with a stated limit. The limit is headless SwiftShader,
not a user's GPU. Pan is about 2× the criterion. The zoom limb is met by the
programmatic zoom and pan transition at 59.8–59.9 fps, about 2× the criterion. Wheel zoom
at 29.9–30.0 fps is input-rate-bound, with one frame per dispatched event (240 of 240). It
is not counted as a ≥ 30 fps measurement in either direction. This follows the deputy's
dated line of 12:25:21 BST, quoted under Decision.

### Criterion 2 — a connection check under 50 ms at 200 nodes

**(i) A real drag in the browser** (`pw/measure.mjs`, the live-validation part).
`DagDesigner.vue` wraps `isValidConnection` in `performance.now()` and pushes each
duration to `window.__f2Timings`. The run starts a connection drag from the source
handle of `s_constraint_19`, then moves across every visible target handle, two steps
per handle. Vue Flow calls `isValidConnection` for the handles it hovers.

Command:
`run.sh live <scratch>/pw env PLAYWRIGHT_BROWSERS_PATH=<scratch>/.pw node measure.mjs http://localhost:5391/spike/designer 5`

- **Final set, N=5** (11:16:19–11:19:29 UTC; load 1.87 → 0.93): 774 calls per run,
  **p50 0.5 ms, p99 0.8–0.9 ms, max 1.0–1.3 ms**.
- Earlier set, N=5 (11:07:57–11:11:11 UTC; load 2.23 → 2.59): 774 calls per run,
  p50 0.5 ms, p99 0.8–1.0 ms, max 1.1–1.2 ms.
- **Not the same as the deputy's quoted figure.** The deputy's decision quotes "max
  1.2 ms" from the earlier set. The final set's max is **1.3 ms** (run 1). Both are
  inside the criterion by more than 35×.

**(ii) A unit harness over every ordered pair**
(`frontend/src/components/dag/graph.spec.ts`, vitest and happy-dom). It runs
`checkConnection` over all 200 × 200 = 40,000 ordered pairs, five times per invocation,
and asserts p99 < 50 ms for each run. The same file tests each rejection class on
deliberately broken input: self, no-output, no-input, duplicate, cycle and
type-mismatch. It also asserts the 8 incident edges that the keyboard test depends on.

Command (final set):
`F2_OUT=<log> run.sh timing <scratch>/frontend pnpm exec vitest run src/components/dag/graph.spec.ts`

| Invocation (start, UTC) | 1-min load start → end | p99 range over 5 runs (ms) | max (ms) | Used? |
|---|---|---|---|---|
| 10:44:47 | 20.37 → n/a | 0.0917–0.1440 | 6.4995 | **No.** Taken before the pause; load over 12 |
| 10:46:47 | 11.79 → 12.82 | 0.0969–0.1351 | 8.3691 | Yes. Started under the gate; the end load is disclosed |
| 10:47:00 | **12.82** → 13.08 | 0.0917–0.1117 | 6.9187 | **No. EXCLUDED: started at load 12.82, over the limit** |
| 11:11:11 | 2.59 → 2.65 | 0.0686–0.0841 | 4.0120 | Yes |
| 11:11:21 | 2.65 → 2.48 | 0.0701–0.0832 | 3.9230 | Yes |
| 11:19:29 (final) | 0.93 → 1.02 | 0.0695–0.0799 | 3.5579 | Yes |
| 11:19:39 (final) | 1.02 → 1.02 | 0.0682–0.0851 | 3.5909 | Yes |
| 11:19:49 (final) | 1.02 → 1.17 | 0.0707–0.0818 | 3.7283 | Yes |

Over the used invocations: **p99 0.068–0.135 ms, and the single worst call is 8.37 ms**.
All tests passed: 3/3 in the earlier invocations and 4/4 after the edge assertion was
added. The first invocation failed only on vitest's default 5 s test timeout, not on its
assertion. The timeout was then raised to 300 s.

**Verdict, criterion 2: PASS.** The browser p99 is about 1 ms. The worst single call in
any harness is 8.4 ms. The limit is 50 ms.

### Criterion 3 — node focus and delete from the keyboard

**Instrument** (`pw/measure.mjs`, the keyboard part, a real browser). The test clicks
the page to blur it, then presses `Tab` until `document.activeElement` is a
`.vue-flow__node`. It presses `Enter`, which selects the node (Vue Flow's
`elementSelectionKeys`), and asserts the `selected` class. It then presses `Delete` and
counts the nodes and edges.

- **Final set, N=5** (the same runs as criterion 2(i)): in every run, focus lands on
  `s_input_0`, Enter selects it, and Delete removes it. Nodes go 200 → 199, the node is
  no longer present, and edges go 328 → 320.
- Earlier set, N=5: identical.
- The 8 edges removed are exactly the node's incident edges. The unit test
  `s_input_0 has exactly 8 incident edges` asserts this.

**Verdict, criterion 3: PASS.**

**Finding: the tab order is linear.** Vue Flow gives every node `tabIndex=0`, so the tab
order is DOM order. Reaching node *k* takes *k* presses of Tab, which on a 200-step
structure is not a usable way to navigate. The deputy's condition 2 takes this up.

### Criterion 4 — the bundle-size delta

**Instrument** (`size.sh`). Run `npx vite build`, then total the bytes of every `.js`
and `.css` file in `dist/`, raw and after `gzip -9`. N=3 per side. Every run gave
identical bytes, so the build is deterministic.

- Base: the scratch tree at `df8e5811` with no spike changes. **1,068,500 B raw,
  359,712 B gzip.**
- After: `@vue-flow/core` plus the spike route. **1,230,625 B raw, 410,951 B gzip.**
- **Delta: +162,125 B raw, +51,239 B gzip.**
- Where it lands:
  - the lazy `SpikeDesignerView` chunk is 154,062 B raw (49,445 B gzip), plus 6,721 B of
    CSS;
  - the rest, about +1.3 kB raw, is the router entry for the new route.
- No `manualChunks` entry was added in the spike. Vue Flow went into the view's lazy
  chunk by default.

**Verdict, criterion 4: PASS** (the delta is reported).

## Verdict — the executor's proposal

**PASS on all four criteria.** The fps figures were measured on the Vite dev build under
headless SwiftShader software rendering, which is a limit of this measurement. The zoom
limb rests on the programmatic zoom and pan transition. The wheel figure is
input-rate-bound, as the blank-page control shows, and it is not counted as an fps
measurement.
Recommendation: adopt Vue Flow for WK-675's designer. Before any designer code lands,
the items under "What remains" apply.

## Decision

The deputy's decision is quoted whole from the lead's channel file:

```text
## 2026-09-28 12:13:47 BST · deputy · Spike F2 DECIDED: PASS. Vue Flow is adopted for WK-675's designer under five conditions; final on its RS record (answers your 12:13:13)

Given by the maintainer's delegation (28 Sep), against my criterion of 11:33:12 (pan/zoom ≥ 30 fps on the dev build; a connection check < 50 ms at 200 nodes; keyboard focus and delete; the bundle delta reported). It becomes final when I read the RS record with the same figures, and it goes into that record quoted whole, fenced.

**The reading:**
- **fps:**
  - pan-drag 58.7–59.6 and programmatic 59.8–59.9, over N=5;
  - wheel zoom 29.9–30.0, **which is the harness's input-dispatch ceiling**: the blank-page control, N=3, gives the same ~30 ms per event, so it does not bound the renderer.

  All of it was measured under **SwiftShader software rendering**, which is harder than a user's GPU. The replaced rAF instrument is kept in the record and its failure explained. That is the right handling, since it read 60 fps while nothing moved.
- **isValidConnection:** browser p99 0.8–1.0 ms and max 1.2 ms. The unit worst case is 8.4 ms at load ≤ 11.8, and the one sample at load 12.82 is excluded, disclosed. That is two orders of magnitude inside 50 ms.
- **Keyboard:** delete removes exactly the node's 8 incident edges (200 → 199 nodes, 328 → 320 edges), N=5.
- **Bundle:** +51,239 B gzip in total, almost all of it in the lazy designer chunk (49,445 B gzip + 6,721 B CSS). The shared entry grows by ~1.3 kB.

**Conditions: WK-675 requirements, and each goes into its leaf plan:**
1. **`RatingAlgorithm` reaches the generated OpenAPI before any designer code.** The spike's hand-written local type is not carried over (CLAUDE.md §2: nobody hand-writes a shape that exists in model-schema; §3: never hand-write an API type).
2. **A keyboard node navigator is an acceptance requirement, not UX polish.** A linear tab order across 200 nodes is not an accessible designer. The WK-675 slice specifies the navigation model (graph-order or spatial arrow keys, plus a jump-to-node), and the `accessibility-tester` agent verifies it against WCAG 2.2 AA.
3. **The bundle stays split.** `@vue-flow` is in the lazy designer chunk with a `manualChunks` entry (the ECharts precedent). The measured deltas are recorded as WK-675's baseline, and any growth of the shared entry chunk is reported in each slice's PR.
4. **Vue Flow is a new tech dependency.** `docs/skills-map.md` and the relevant spec's §8 change in the same PR that adds it (CLAUDE.md §10), with its licence stated.
5. **"On the dev build":** the RS record states which build the fps were measured on. If it was the production build, that is recorded as a deviation from my criterion, and WK-675's first designer slice re-measures pan/zoom on the dev build (N=5, load < 12).

**The pnpm `allowBuilds` prompt trap** goes to a `dev-commands` skill fix as you routed it, with you as owner. CLAUDE.md §12 wants a known skill trap fixed in the same session, so it is filed in a small skill-only PR today, not left for WK-675.

Salvage `a3862e01` and a clean box (no F2, chrome or vite process; load 1.54) are noted.
```

The deputy's dated line on this decision, restating its fps ground on the corrected
figures, is quoted whole from the same file:

```text
## 2026-09-28 12:25:21 BST · deputy · F2 decision: a dated line restating its fps ground on spike-f2's corrected figures. The PASS stands (answers your 12:24:40)

**The line, text of record. #834 appends it after my 12:13:47 quote, fenced:**

> *Amended 2026-09-28 12:25:21 BST by the deputy, on spike-f2's three self-corrections.*
> **(1) Figures:** the decision quoted the earlier N=5 set. **The final gated set (12:13–12:20 BST) governs:** pan-drag **59.2–59.9 fps**, browser `isValidConnection` **max 1.3 ms**. Both remain far inside the criterion.
> **(2) The wheel-zoom ground is restated.** The decision said the blank-page control gives "the same" per-event time. **It does not:** 29.8–29.9 ms per event blank, against 33.3–33.4 ms on the designer, so the designer adds ~3.5 ms per wheel event. The zoom limb of the criterion is met by **programmatic zoom/pan at 59.8–59.9 fps**. Wheel zoom at 29.9–30.0 fps is **input-rate-bound** (one frame per dispatched event, 240 of 240), not render-bound, and the ~3.5 ms the designer adds fits well within a 33 ms frame. It is **not** counted as a ≥ 30 fps measurement in either direction.
> **(3)** WK-675's designer slice re-measures wheel zoom with an input source faster than one event per ~30 ms, or states that the harness cannot, in its "what remains". This joins condition 5's dev-build re-measure only if a production build is ever the one measured.
> **The PASS and conditions 1–5 are unchanged.**

**The clock correction** (`uptime` prints UTC, and the re-run was 12:13–12:20 BST) is noted. Spike-f2's catching its own "the same" is exactly the kind of correction a record should carry.
```

**Condition 5 is answered in the Method section:** the fps were measured on the **Vite
dev build**, so there is no deviation from the criterion.

## What remains

These are WK-675 prerequisites and follow-ups. The deputy's conditions 1–4 take up (a),
(c) and the tab-order finding.

- **(a) The contract gap.** This is a WK-675 prerequisite. `RatingAlgorithm` is defined
  in `packages/model-schema/src/model_schema/rating.py`. The generated OpenAPI
  (`docs/contracts/openapi/generated.json`) has no `RatingAlgorithm` component at
  `df8e5811`: the only rating components are `RatingVersion*` and `TraceStep`. The
  spike's step type (`RatingStepSpike`) is therefore **hand-written, spike-only, and must
  not be carried over.** `RatingAlgorithm` reaches the generated OpenAPI before any
  designer code (the deputy's condition 1; CLAUDE.md §2 and §3).
- **(b) The pnpm `allowBuilds` trap.** When `pnpm add @vue-flow/core` meets a transitive
  dependency with a build script (`vue-demi@0.14.10`), pnpm writes
  `frontend/pnpm-workspace.yaml` with an unanswered `allowBuilds` entry. It prints
  `ERR_PNPM_IGNORED_BUILDS`. After that, `pnpm generate:api` fails its deps-status
  check, and until it runs every `vue-tsc` run shows 143 phantom type errors, because
  `src/api/generated/` is missing. The fix is `vue-demi: false`, which is safe because
  vue-demi's shipped `lib/index.mjs` already targets Vue 3. The lead has routed this as a
  `dev-commands` skill fix in its own PR, and the fix is not in this record's PR.
- **(c) The bundle split.** Following the ECharts precedent in `frontend/vite.config.ts`,
  `@vue-flow` gets its own `manualChunks` entry. The deltas above are WK-675's baseline
  (the deputy's condition 3).
- **The keyboard navigator.** A graph-order or spatial navigation model with a
  jump-to-node, verified by the `accessibility-tester` agent against WCAG 2.2 AA (the
  deputy's condition 2).
- **The tech dependency.** `docs/skills-map.md` and the relevant spec's §8 name Vue Flow,
  with its MIT licence, in the PR that adds it (the deputy's condition 4).
- **Wheel zoom re-measure.** WK-675's designer slice re-measures wheel zoom with an input
  source faster than one event per ~30 ms, or states in its "what remains" that the
  harness cannot (the deputy's dated line of 12:25:21 BST, item 3).
- **Not measured.** fps on a GPU-backed browser. Edge-routing and layout cost for an
  auto-layout, which the spike does not use. Undo and redo. Sub-graph mounting. The
  structural-diff overlay.

## Salvage ref

`refs/salvage/2026-09-28/spike-f2`:

- `a3862e01cbcaa1ba85ffc386bf95c965cc60ca3c` holds the code and the first logs. The lead
  pushed it.
- `a6f41714948dea13b97299ce292f08322a147bdb` is its child and adds the final gated logs
  and the per-process cwd and CPU quotes (`pw/results/final/`). It is the local ref's
  current value, which the lead is asked to push.

Both are based on `df8e5811`.
