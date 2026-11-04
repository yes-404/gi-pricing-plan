---
id: RS-1904
family: research
kind: audit
title: SL-1552 (WK-675 S10) slice audit — the Rating version list at /rating (FR-1903), DP-S10-4 order, test (f) assert map, accessibility fixes
status: draft
created: 2026-10-25   # drafted 2026-10-25 under working id 8232; minted 2026-10-25 as RS-1904
owner: auditor
tree: 22e2c22b7fcd4a63436721aa33d110e57e983c0e
phase: P2
work: WK-675
corrected_by: []
relates: [SL-1552, LG-1902, PL-1286, PL-1546, RL-1900, FR-1531, FR-241, FR-25]
---

# RS-1904 — SL-1552 slice audit (WK-675 S10, the Rating version list)

*(Working id 8232, written by `aud1552` (auditor, sonnet, effort medium), 2026-10-25, from `brief-aud1552-2026-10-25.md` (lead 28). Check 31/32 on this id and on the slice's own working ids (SL-1552's FR-1903, OQ-1901, RL-1900, LG-1902) are expected until the mint. No test, DB, docker or gate was run by this seat.)*

## Question

Does `origin/main...origin/sl-1552-wk675-s10` meet the scope of the `PL-1286` S10 row and LG-1902's acceptance, the maintainer's entries of 2026-10-23 11:14:56 BST, 2026-10-25 11:32:17 GMT (line 4) and 2026-10-25 14:34:34 GMT, and is the evidence for each item reachable and honest?

## Method

Range `origin/main...origin/sl-1552-wk675-s10`. Slice head `8c620af94bcad12a2561a53bb77fdbaa9dff1efb`, tree `22e2c22b7fcd4a63436721aa33d110e57e983c0e`; merge-base with `origin/main` = `01a28e6d5571ed8f8d478760fc11aa2015326840` (the slice already carries main). 12 files, +968/−5 (`git diff --stat origin/main...<head>`): 03 spec, OQ mirror, roadmap, INDEX, RL-1900, LG-1902, `App.vue`, `router/index.ts`, `reachability.test.ts`, `api/environments.ts`, the view and its test. Read by `git show/diff/grep` only. **Ledger reachability (two-way):** the 17 SHAs LG-1902 cites (`4e399fd0`, `034781b3`, `c8be222b`, `01a28e6d`, `1c6c2e4a`, `3384934c`, `b657386f`, `6968bba2`, `5cb21f6b`, `be2436b3`, `cd855d65`, `05c151f2`, `7164a61e`, `fff804c9`, `06303cda`, `697a92f8`, and the draft `d4258b95`, which is on `origin/draft/rl-8163` and was not tested) exit 0 under `git merge-base --is-ancestor <sha> origin/sl-1552-wk675-s10`, except two: `d4258b95` (not tested) and `c8be222b`, SL-1551's pre-squash PR head cited as context (rc 1; its squash `034781b3` is an ancestor, rc 0), so it is not evidence for this slice. In the other direction, the range holds 16 non-merge commits; 11 are cited by SHA; the five not cited are `95d7eac7` (activation, named in the log without a SHA), `6cdec296` (OQ fold, no log line), `1a9cf5cd` and `9a001efe` (the accessibility test and fix: the log gives only their base `3384934c`) and `8c620af9` (the head, which adds the LG line itself). All five are also ancestors of the head (rc 0). See B6. **Gate: OWED** (its ~17:35 paired slot, SL-1552 with SL-1569; the accepted gate head 697a92f8, to-lead 2026-10-25 14:34:34 GMT, is an ancestor of the audited head, and the delta since is the `01a28e6d` INDEX-only re-merge plus the LG line `8c620af9`). The frontend suite and the build log's red/green lines were read from the LG, not re-run.

## Scope (derived first)

From `PL-1286` row S10 (`docs/plans/PL-01286-…-map-plan.md:313`): spec first (a new `03` FR and the amended §5.1 list row), then the view — versions by status, live-in-environment badges, effective dates, each row linking to the version's `:slug/v/:version` routes, removing the interim FR-25 path. From LG-1902 Scope: FR-1903, OQ-1901 mirrored both ways, DP-S10-1 to -4 (RL-1900), the link cite `RatingVersionView.vue:100-107`, router/App.vue held until SL-1551, accessibility review, GREEN by import closure. From the maintainer's entries: (D) of 11:14:56 (GO, RL-1900 adopted, held files), (B) DP-S10-4, line 4 of 11:32:17 (OQ-1901 joins the existing "Before the P2 exit demo" row), 14:34:34 (item 13 for test (f)).

## Evidence per criterion

| # | Criterion | Evidence | Result |
|---|---|---|---|
| 1 | Spec first: FR-1903 in `03` §3.4, §5.1 row amended in place (no second row), OQ-1901 both ways | `03-rating-engine.md` FR-1903 row after FR-1531; §5.1 `GET /api/v1/rating-versions` row amended in place ("there is no second row"); OQ-1901 in `03` §10 and `open-questions.md:163`; spec commit `b657386f` precedes RED `6968bba2` and GREEN `5cb21f6b` (ancestor order) | met |
| 2 | RL-1900 folded with the adoption line, active | `docs/rulings/RL-…8163…md` front matter `status: active`; line 247 "Adopted as drafted on 2026-10-23 … to-lead 2026-10-23 11:14:56 BST item (A)"; fold commit `cd855d65` | met |
| 3 | Activation: SL-1552 `draft→active`, dated line | `roadmap.md` SL-1552 row, `status: active`, "(Activated 2026-10-23 … item (D); ledger LG-1902 …)"; commit `95d7eac7` | met |
| 4 | DP-S10-1 `RatingVersionView` stays; `/rating` is the entry | `router/index.ts` adds `/rating` (name `rating-versions`) after `/rating-versions/:id`, which is untouched; `App.vue` nav link "Rating"; `reachability.test.ts` new case asserts `/rating` registered, linked from shell, and `/rating-versions/:id` still reachable | met |
| 5 | DP-S10-2 live badges: client-side join over every page of `GET /api/v1/environments`, key `rating_version:{slug}@{version}`; any 403, failed page or truncation → "unavailable" on every row, never "not live" | `api/environments.ts` (`ENVIRONMENT_PAGE_CAP = 5`, `ratingVersionRef`); view `readEnvironments()` returns `null` on throw or `truncated`; template shows "unavailable" for every row when `null`; tests (b) two, (c) page 2, (d) 403 / failing 2nd page / page cap | met |
| 6 | DP-S10-3 unpaginated, filter and group in the view | `groups` computed filters by `statusFilter` and groups by slug; no route change (no `backend/` or `docs/contracts/` file in the diff stat) | met |
| 7 | DP-S10-4 order, pinned by a test | See "DP-S10-4" below | met |
| 8 | Links by `slug@version`, no second lookup; link cite | view `<RouterLink :to="`/rating/${slug}/v/${version}/design`">` etc. as literal templates; test (f) asserts the five hrefs and that only `/api/v1/rating-versions` and `/api/v1/environments` are called; the cited `RatingVersionView.vue:100-107` is quoted in LG Scope | met |
| 9 | Effective dates (FR-241) | view `day()` renders the date part of `effective_from` / `effective_to`, "—" when absent; test (e) | met |
| 10 | OQ-1901 joins the existing "Before the P2 exit demo" row, count +1 | `roadmap.md:3590` row gains **OQ-1901** with the "(OQ-1901 joined 2026-10-25, to-lead 2026-10-25 11:32:17 GMT line 4)" tag; count `11 (11 open)` → `12 (12 open)` with the before-line kept; no separate §14 row remains (the roadmap diff vs main touches that one row only) | met |
| 11 | Held files re-merged after SL-1551 | merge `1c6c2e4a` brings #1372 (034781b3); `fff804c9` RED then `06303cda` GREEN for the route; LG build log has the RED (`1 failed \| 2 passed`) and GREEN (`3 passed`) lines | met |
| 12 | Accessibility review: 4 should-fix fixed in-slice | See "Accessibility" below | met |
| 13 | GREEN by import closure (item 29) | LG build log: changed modules by `git diff --name-only origin/main...HEAD -- frontend/src`, closure script, 9 test files in three runs of 3, all passed; `generate:api`, `type-check`, `lint` rc 0. Not re-run here | met on the LG's evidence; **gate owed** |
| 14 | Item 13 (test change) authorised | Test (f) is the one existing assert set changed; grant quoted in LG Scope build log (the 14:34:34 line) — see map below | met |

## Test (f) — the assert map

Command: `git -C <aud-1552 worktree> diff 3384934c~1..8c620af9 -- frontend/src/views/__tests__/RatingVersionListView.test.ts`. One commit touches the file in that range, `1a9cf5cd`. The hunk starts at line 260, inside test `(f) links each row by its own slug@version, with no second lookup (FR-1531)`. All of (f)'s asserts, before and after:

| # | Before (`3384934c~1`) | After (`8c620af9`) | Verdict |
|---|---|---|---|
| f1 | `expect(href("Design")).toBe("/rating/fremtpl2-demo/v/2/design")` | `expect(href("Design fremtpl2-demo@2")).toBe("/rating/fremtpl2-demo/v/2/design")` | kept; same `toBe` on the same href; only the lookup name changed to the new accessible name |
| f2 | `expect(href("Sandbox")).toBe("/rating/fremtpl2-demo/v/2/sandbox")` | `expect(href("Sandbox fremtpl2-demo@2")).toBe(…/sandbox)` | kept, same |
| f3 | `expect(href("Dislocation")).toBe("/rating/fremtpl2-demo/v/2/dislocation")` | `expect(href("Dislocation fremtpl2-demo@2")).toBe(…/dislocation)` | kept, same |
| f4 | `expect(href("area@3")).toBe("/rating/fremtpl2-demo/v/2/tables/area")` | unchanged | kept |
| f5 | `expect(href("band@2")).toBe("/rating/fremtpl2-demo/v/2/tables/band")` | unchanged | kept |
| f6 | `expect(within(none).queryByRole("link", { name: /@\d+$/ })).not.toBeInTheDocument()` | `… { name: /^\S+@\d+$/ } …` | kept; **pattern changed** (below) |
| f7 | `expect(new Set(calls.map((u) => u.pathname))).toEqual(new Set(["/api/v1/rating-versions", "/api/v1/environments"]))` | unchanged | kept |

7 asserts before, 7 after, none dropped. The `getByRole("link", { name })` lookups inside f1–f3 stay strict: a string `name` matches the whole accessible name, so each still fails if the link is missing or its name differs. The `toBe` target is unchanged.

**Pattern change, quoted:** `/@\d+$/` → `/^\S+@\d+$/`. The loosened old pattern could not stay: the row-link names now read `Design fremtpl2-demo@1` and end in `@\d+`, so the old pattern would find three links in the "none" row and fail for the wrong reason. The new pattern keeps the intent (no link named like a pinned table, `slug@n`, in a row that pins none). Strictness: it still matches every name the old pattern was written for (`area@3`, `band@2`: no whitespace). **It no longer matches a pinned-table link whose name contains a space** (e.g. `Table area@3`), which the old pattern would have caught — see B1. For the case the test exists for (row `fremtpl2-demo@1` pins no tables) the assert is at least as strict, and it is not vacuous: row `fremtpl2-demo@2`, which pins two tables, has links `area@3`/`band@2` that the pattern does match (f4/f5 prove those links exist and have those names). Five new `(g)` tests were added in the same commit and none replaces an (f) assert.

The maintainer's grant (14:34:34 GMT) says "adopts the new accessible link names and tightens its 'no pinned-table links' pattern to `/^\S+@\d+$/`; no assertion dropped or weakened". Findings: **no assertion dropped (7 → 7); one pattern narrowed in scope, which the grant names; no weakening for the cases the test is written for.** One residual narrowing is recorded as B1.

## DP-S10-4 — order pinned by a test

Entry (B), 2026-10-23 11:14:56: groups by slug; `version` desc within a slug; groups ordered by the newest version's `effective_from` desc, a group whose newest version has `effective_from = None` LAST, ties by slug asc. View: `groups` computed — `rows` sorted `b.version - a.version`; group key `from = byVersion[0].effective_from` (the newest version); comparator returns null-last then `b.from - a.from`, then `a.slug.localeCompare(b.slug)` (ties, and null-vs-null, by slug). Test `(a) orders groups by the newest version's effective_from desc, none last, ties by slug (DP-S10-4)` (test file line 139), quoted:

```
zeta  v1 live 2026-03-01; alpha v1 live 2026-03-01; mid v1 live 2026-06-01;
nodate v1 live 2026-12-01 + nodate v2 draft (no effective_from); beta v1 draft (none)
expect headings → ["mid", "alpha", "zeta", "beta", "nodate"]
```

It pins all three keys at once: date desc (mid first), the tie by slug (alpha before zeta), null-last, and the *newest version* rule (nodate has an older v1 dated 2026-12-01 yet sorts last because its newest, v2, has none), plus null-vs-null by slug (beta before nodate). The entry asks for "one view test asserts the null-last and the tie-break": met. Case (a)'s heading and ref order (`motor-gb`, `fremtpl2-demo`; refs `motor-gb@27, fremtpl2-demo@2, fremtpl2-demo@1`) pins version-desc within a slug.

## FR-1903 text vs the view

| FR-1903 clause | View | Match |
|---|---|---|
| (1) filter by `status` (five values), group by `slug`, no route param | `STATUSES` five values; `groups` | yes |
| (1) display order | as above | yes |
| (2) one badge per environment whose `live_deployments` holds the row's `rating_version_ref`; several shown | `liveIn()` filters on `rating_version_ref === ref_`, no `id` join; `v-for` over every match | yes |
| (2) every page; "unavailable" on every row for 403 / failed page / page cap; "an empty badge cell means the whole live set was read and the version is live nowhere" | `null` → "unavailable"; **live-nowhere renders the text "none", not an empty cell** | **differs, B2** |
| (3) `effective_from` and, when set, `effective_to` | both columns; "—" when unset | yes |
| (4) links to design / sandbox / dislocation, and `/tables/:tableSlug` per pinned rate table | as listed | yes |
| (5) `RatingVersionView` stays; `/rating` reached from navigation | route and nav link | yes |

## Accessibility — the four should-fix items (from-lead 2026-10-25 ~14:30 GMT: 0 blockers, 4 should-fix, fixed at 697a92f8)

The review text itself is in the lead's message, not a file; the four items are read from LG-1902's build log ("Fixes: …"), which lists them, and checked against the view and tests.

| Should-fix | View (8c620af9) | Test | Result |
|---|---|---|---|
| each per-slug table has a name | `<caption class="sr-only">{{ slug }} versions</caption>` | `(g) names each per-slug table` (`getByRole("table", { name: "motor-gb versions" })`, same for `fremtpl2-demo`) | fixed |
| loading and empty states announced | `role="status"` on "Loading…" and "No rating versions." | `(g) announces the loading and the empty states as status` | fixed |
| row links' accessible names carry the version, visible text first (SC 2.5.3), padded targets | `:aria-label="`Design ${slug}@${version}`"` etc.; `inline-block py-1` | `(g) a row link's accessible name carries its version, visible text first` (asserts name and visible text and the `inline-block` class) | fixed; the padded target is checked by class only, not measured |
| a version live nowhere reads "none"; unread stays "unavailable" | `v-else-if="liveIn(version).length === 0"` → "none" | `(g) a version live in no environment reads "none"…`, `(g) a 403 … never reads "none"` | fixed (but see B2) |
| (also in the commit) shared focus-visible outline on select and links | `focus-visible:outline …` classes on select and all links | no test (a style) | applied |

Test (f)'s name updates (f1–f3) and pattern (f6) follow from the third item.

## Findings

| # | Severity | Finding | Proposed disposition |
|---|---|---|---|
| B1 | LOW | Test (f6)'s new pattern `/^\S+@\d+$/` no longer catches a pinned-table link whose accessible name contains whitespace. A future change that gave table links a prefixed `aria-label` (as the Design/Sandbox/Dislocation links now have) could leak links into a "pins nothing" row unnoticed. Granted by the maintainer in terms; no assertion is dropped. | accept; or tighten later by asserting `getAllByRole("link")` in the "none" row equals exactly the three named links |
| B2 | LOW (spec/view disagreement) | `03` FR-1903 clause (2) says "an empty badge cell means the whole live set was read and the version is live nowhere". The accessibility fix at `9a001efe` renders the text "none" in that case, and test `(g)` pins it. The FR text was not amended; the LG Scope does not mention "none". CLAUDE.md §0: when code and spec disagree, resolve it. | before merge: one dated line in FR-1903 clause (2) ("renders 'none'", citing the 14:30 accessibility review and `9a001efe`) and a line in the LG Scope; the audit proposes this, the lead rules |
| B3 | INFO | LG-1902 sections not yet closed: Task list item 6 still says "Held…", `### Gate` says "Not run (held)", `### Audit` says "Not yet", `MERGE-ACK: not yet`, `## PRs` says "None yet". Expected at this point (gate owed, audit in progress). | at the mint: Audit section cites RS-1904 and its verdict; Gate section gets the paired-slot result; remove "Held" |
| B4 | INFO | Padded-target claim (`inline-block py-1`) is asserted by CSS class presence only; no layout measurement exists in the jsdom suite. Same for the focus-visible outline. | accept; a class assert is the available instrument |
| B6 | INFO | LG-1902's build log does not cite `1a9cf5cd` (accessibility RED test) or `9a001efe` (fix) by SHA, only their base; `6cdec296` has no log line. The two-way match is incomplete by name, though all are reachable. | at the mint add the three SHAs to the build log |
| B5 | INFO | Gate owed. The audit used the LG's logged red/green lines (`Tests 5 failed \| 11 passed (16)`, then `16 passed (16)`, reachability `3 passed`) and did not re-run them. The accepted gate head 697a92f8 is an ancestor of the audited head; the delta is INDEX-only plus the LG line. | gate result of record decides the frontend half |

No blocker. No product defect (`FD-`) finding. Process note: the `5 failed | 11 passed` RED line was logged with its rc hidden by a pipe — already routed by the maintainer (14:34:34) to a process-backlog row; not re-filed here.

## Proposed verdict

**CLEAN, with B2 to be resolved before merge (a one-line dated spec amendment) and the gate owed.** Delivered and tested: all FR-1903 clauses except the "empty cell" wording (met in substance, differing in wording); DP-S10-1 to DP-S10-4; OQ-1901 mirrored and placed in the ruled gate row; the four accessibility items; test (f) lost no assertion (7 → 7) and its one pattern change is the one granted. Unevidenced requirements: none open in this slice's scope; NFRs: none declared for this slice (the view adds no route and no budget; OQ-1901 carries the size bound). The verdict is the lead's.

*Checks:* `python3 scripts/audit-docs.py` and `doc-index.py --check` on this record: see the commit message and the report.
