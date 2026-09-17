---
id: CR-719
family: closure
kind: work
title: WK-663 — Frontend Data Workbench: closed
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-15
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/closure-records.md
---

### WK-663 — Frontend Data Workbench: closed 2026-08-15

**Scope, derived from `01` §5.3 before opening any frontend file: seven views**, plus the
one seam `CLAUDE.md` §2 defines — `model-schema` → `docs/contracts/` → generated client —
and the API conventions `00` §5 requires every caller to honour (the single error shape,
cursor pagination, `202`-plus-Job, the idempotency key).

WK-663 owns no `FR` of its own: the frontend is where other modules' requirements become
visible, so its evidence is the views and their tests rather than markers. That is also why
the closure below leans on the two audits that *are* derivable — endpoints and catalogue —
and on what building the screens found in the API beneath them.

> **This table was rewritten on 2026-08-15**, after an independent auditor read `01` §5.3's
> **Contents** column against the components. The version it replaces listed seven views
> and, as their "evidence", restated the Contents column — including four items that are
> not built. Every view is routed and none is a stub; that is a fact about the router, and
> the record reported it as a fact about the screens.
>
> **Six of the twenty-seven Contents items are missing**, and three of the six have a
> working backend endpoint and a dead client wrapper.

| Deliverable (`01` §5.3) | Route | Built | Not built |
|---|---|---|---|
| App shell + generated client | — | client generated from the committed contract; no hand-written shape in `src/` | the CI drift check was inert until 2026-08-15 — it diffed a git-ignored path. `type-check` against the fresh client is the check now |
| Dataset list | `/data` | name, line of business, territory, currency, latest version | **status badge**, **last validated**, **owner** — and `Dataset` carries none of the three, so §4.1 never defined what §5.3 asks to display |
| Dataset detail | `/data/:slug` | version timeline (newest first, tested), rule set link in both states, data dictionary editor for `description` and `pii_class`, **lineage graph — delivered 2026-08-26 (W6b-12)**: `getLineage()` is typed by `01` §4.9's `DatasetLineage` and called by the detail view; the handler serves the four-arm object, the direction filter empties the excluded arm, and the graph renders for the newest version | `semantic_type` is read-only; `unit` and `reference_table` are not rendered |
| Version detail | `/data/:slug/v/:version` | all five: table inventory, row counts, totals, schema viewer, rejected-rows drawer | — (the drawer's populated branch is untested: both fixtures have zero rejects) |
| **Validation report** | `…/validation` | all six, and the interaction requirement genuinely holds — DOM order asserted, not presence | the offending sample is a `<ul>`, not the table §5.3 names; `empty_layers` is surfaced on the rule-set screen and not on this one |
| Profile | `…/profile` | per-column cards; one-way charts with exact Poisson CI whiskers (ECharts); **histograms** — delivered 2026-08-19 by the profile-contract slice, which added `ColumnProfile.histogram` as **FR-65** and wired `HistogramChart.vue`; the **top-levels chip list now shows exposure per level** — delivered 2026-08-19 by the `top_levels` slice (FR-66) | **PSI comparison selector — built 2026-08-19.** `compareProfiles()` has its caller; the reference-version picker lives in the route query (**OQ-556**), and each column card carries a `ColumnDrift` block banded against `VR-DST-1`. |
| Rule set editor | `/data/:slug/rules` | rules by layer, enable/disable (full-membership round-trip tested), severity override, custom-rule builder with dry-run | **threshold editing** — thresholds render read-only; changing one means retyping the whole rule into the builder. **Delivered 2026-08-25 (W6b-13), as versioning rather than set-level editing** — per `FR-56` the capability is relocated: each rule row's "New version" action opens the builder pre-filled with the current rule, and the threshold change travels `FR-50`'s reviewed path. See [the W6b-13 plan](../plans/PL-00792-w6b-13-rule-set-rule-versioning-screen-implementation-plan.md) |
| Reference tables | `/reference` | all four: table list, version timeline, effective-date viewer, lookup debugger | — **nothing wrong found in this view** |

**Gate (local, 2026-08-15):** ruff clean · mypy --strict on 84 source files · import-linter
3 kept / 0 broken · **591 python tests** · 7 generated contracts match · docs audit 20/20 ·
req-coverage · eslint `--max-warnings 0` · `vue-tsc --build` · **75 frontend tests** ·
`pnpm build`.

| `scope-audit.py DATA …` | At WK-660's close | Now |
|---|---|---|
| requirements | 48 / 50 | **48 / 50** (NFR-465/466 measured, not tested — WK-660's verdict stands) |
| `--endpoints` | 28 / 28 | **33 / 33** |
| `--catalogue VR` | 38 / 38 | **38 / 38** — *was 1 / 38, corrected 2026-08-19; resolved 2026-08-23*. Not a regression: `scope-audit.py`'s catalogue check was fixed on 2026-08-15 (`d4a90c7`) to count ids the code carries **as data** rather than mentions in prose, and this row was left quoting the pre-fix instrument. The number the fixed check reports is recorded in the WK-666 record below, and has been since that day. Only `VR-STR-5` reached the code as a string constant at all, and incidentally — inside another rule's error message (`validate.py:1176`); the other 37 rules were implemented but unnameable, which is what `01` §4.4's "rule IDs here are stable and referenced by workflows and by the UI" asked for and did not have. Owner was **WK-664**, alongside the rule set editor's threshold editing, which is the first screen that must reference a rule by id. **Resolved 2026-08-23 (W32-2) under FR-68**: the catalogue is `BUILTIN_RULES` in `model-schema`, seeded into every workspace and served by `GET /api/v1/validation-rules`. The single prior hit was one rule's id inside another rule's skip message, so the true starting count was zero. **Not resolved by this slice:** `frontend/src/api/profiles.ts:42` still hard-codes `VR-DST-1`'s PSI bands — a threshold written twice, which `CLAUDE.md` §2 forbids. The endpoint that lets the frontend ask now exists; changing the view is **W6b-13's**. Owner: W6b-13. FR-55, FR-82, FR-67, NFR-465 and NFR-466 remain without evidence and are untouched here — the first two are W32-3's, the last two are budgets needing a measurement rather than a marker |

**What building the screens found in the API — six defects, none in a view.** This is the
workstream's most useful output and the reason a frontend is not merely a rendering of a
finished backend:

| Found | Was |
|---|---|
| `GET /datasets/{slug}/versions` | §5.3 requires a version timeline; §5.1 offered only `latest_version`, so a client drew it one request per version |
| `source_names` on `DatasetTable` | The table inventory could not name its sources |
| `empty_layers` on `ValidationRuleSet` | A plain `@property`, so it never reached the contract — FR-45's warning had nothing to surface, while `ValidationReport` beside it carried the same list as a field |
| `POST /validation-rules/{id}/approve` | Absent. A rule could be authored, dry-run and submitted, then sit in `review` for ever — and a Rule Set refuses anything not `approved`, so nothing authored through the API could ever be used |
| `rules` in the rule-set replace body | Took bare ids, so `enabled` and `severity_override` were unreachable and the "an override may only raise" invariant guarded something no caller could attempt |
| Three reference read routes | The surface was write-plus-lookup; §5.3's table list, timeline and effective-date viewer had nothing to call |

Each landed as a spec change **and** the code, in one commit, with the amendment dated in
`01` §5.1 — because which of the two was wrong is the thing a governed system cannot
afford to lose (`CLAUDE.md` §0).

**Enforcement proven, not assumed** (§13 rule 4). Every claim a test makes was broken on
purpose first:

- the rule-set editor's carry-through — rebuilding the replace body from ids alone
  re-enables every other disabled entry; the test goes red
- `waitForJob` — returning the first poll instead of looping makes the builder submit a
  rule whose dry run had not finished
- the severity-downgrade guard — removing it turns a 409 into a 500 from
  `RuleSetEntry`'s own validator, which is *why* the service-level refusal exists
- `covers_to` — computed as `max(effective_to)` it reports a table that never expires as
  expiring in July
- the reference view's opening version — the newest rather than the newest **published**
  shows a draft no quote can have used

**The one thing that had never been exercised: the browser could not authenticate.** The
SPA sends no credential, and the platform refuses an unauthenticated request (`07` §3.7),
so a real browser got 401 on every request while all seven views and their tests passed —
the tests stub `fetch`, and nothing touched the transport. Confirmed against a live server
(`401` direct), fixed for the dev loop by injecting the development identity headers in the
**Vite proxy** — never in `client.ts`, because a header the browser sets is a credential the
user can edit in devtools and a code path that would ship in the production bundle
(`grep` of `dist/`: zero occurrences). The seed now prints the two ids. Real browser
authentication is **OQ-644**, open, recommendation recorded.

**Not delivered by WK-663:**

| Item | Verdict |
|---|---|
| Browser authentication | **Not started, and correctly so.** OQ-644 was open when WK-663 closed; it was decided the same day — PKCE in the SPA, **FR-393**, owned by WK-664. The dev proxy remains a dev loop, named so it cannot be mistaken for a mechanism |
| Playwright E2E | **Deferred to WK-665.** `01` §5.3's journeys are worth one E2E each *once the demo entrance exists*; before that an E2E asserts a fixture |
| Pinia stores | **Registered, still unused — and the predicted trigger did not fire.** This row named the PSI comparison selector as the first thing that would need state to outlive a route. When that slice was built (2026-08-19) the premise did not hold: nothing requires the reference version to survive navigation, and the route query gives the selection reload-survival and shareability a store cannot. Recorded as **OQ-556**. The next candidate is the workspace selector WK-664 carries, and that one should be checked the same way rather than assumed. |
| TanStack Table, Vue Flow | **Later phases** (`03` §5.3). Declared in `skills-map.md`, not installed |
| Accessibility beyond semantics | **Partial.** Tables carry `aria-label`, alerts carry `role`, and every test queries by role or label — which keeps the semantics honest. NFR-463's tabular fallback for charts is **not** built; owner WK-664 |
| `07` §5.1's six `PLAT` endpoints | Unchanged from WK-658's record — still owned by WK-674 |
| **Six §5.3 Contents items** | **Added 2026-08-15.** Dataset status badge, last validated, owner; lineage graph; histograms; PSI comparison selector. Plus threshold editing in the rule set editor. The original record did not list them because it audited routes and not Contents. Owner: **WK-664**, except the two blocked by a model/contract divergence (owner/status/validated, and `histogram`), which need a spec decision first — recorded as unresolved in `01`, not silently designed around. **Two of the six delivered 2026-08-19** — histograms, via FR-65, and the PSI comparison selector, whose `compareProfiles()` now has a caller; four remain. **Threshold editing of the six delivered 2026-08-25 (W6b-13), under `FR-56`'s semantics** — a threshold is changed by authoring the rule's next version from the rule set editor, not by set-level editing; see [the W6b-13 plan](../plans/PL-00792-w6b-13-rule-set-rule-versioning-screen-implementation-plan.md). **All six delivered 2026-08-26, the lineage graph last (W6b-12)** — the arithmetic, because a bare count has been the stale thing twice: status badge, last validated and owner (**W6b-3**, fields via `FR-55`/`FR-82`), histograms (**WK-661**), PSI selector (**WK-661**), lineage graph (**W6b-12**), plus threshold editing (**W6b-13**). |
| **Two unresolved model/contract divergences** | **Added 2026-08-15.** `Dataset` has no status, validated-at or owner while §5.3 asks to display all three; `ColumnProfile` has no `histogram` while `01` §4.7 *and* `docs/contracts/schemas/profile.schema.json` both define one. Four other divergences from the same fortnight got dated amendment notes; these two were built around in silence, which is the `CLAUDE.md` §0 failure the notes exist to prevent. **Both owned 2026-08-18.** The `ColumnProfile` half is **resolved 2026-08-19** by the profile-contract slice (WK-661): the contract was right and the requirement was incomplete, so `01` gained **FR-65**, both profiling engines compute the histogram, and the Profile view renders it. The `Dataset` half is not a slice task: it has two defensible answers, so it is recorded as **OQ-565** rather than picked. **Decided 2026-08-19, and the row closes with it:** two of the three are projections the list endpoint derives from the Dataset's versions (`FR-55`) and the third is a new explicit `Dataset.owner_id` (`FR-82`). Neither is built — the decision moved the divergence from *unanswerable* to *unbuilt*, owner WK-664 **Both built 2026-08-23 (W32-3), and the decision's field count was one short.** `FR-55` landed as **three** derived fields, not two: "where the two refer to different versions the list states which" cannot be satisfied by a bare `last_validated_at`, so `last_validated_version` travels with it and a validator refuses either alone. `FR-82`'s `owner_id` is a non-null column backfilled from the audit chain, with `PATCH /api/v1/datasets/{dataset_id}` as the Admin-or-owner change path the requirement implies and `01` §5.1 had nowhere to put. **The three view columns are still not rendered** — that half of this row stands, and is W6b-3's; this slice delivered the fields the columns need, not the columns |

**Retrofit list (`docs/roadmap.md` §5):** unchanged by WK-663. The frontend consumes the
contract; it does not touch audit-in-transaction, artifact immutability, integer money or
the Job model. Money crossing into TypeScript is handled the one way `vue-frontend`
records: minor units are integers formatted at the edge, exact decimals stay strings and
are never parsed, and the two `_minor` fields that are float **ratios** are rendered as
statistics rather than currency — with a type-level test, because `expectTypeOf` erased at
runtime and passed while asserting the wrong thing.
