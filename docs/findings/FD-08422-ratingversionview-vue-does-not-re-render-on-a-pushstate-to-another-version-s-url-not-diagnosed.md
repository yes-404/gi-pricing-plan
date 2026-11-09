---
id: FD-8422
family: finding
title: RatingVersionView.vue does not re-render on a pushState to another version's URL; no watch on the route param and no onBeforeRouteUpdate by grep; not diagnosed
status: active
created: 2026-11-09
owner: auditor                  # DRAFT by the executor for the auditor's sign-off (document-ids §1.6)
tree: 374a22bf33ad
corrected_by: []
relates: [LG-8226, SL-1913]
---

# FD-8422 — RatingVersionView.vue does not re-render on a pushState to another version's URL

## Finding

During row 6b's headless browser check (SL-1913, 2026-11-09, headless Chromium through Playwright 1.55.0), the browser was on `/rating-versions/<K1 id>` and the script moved to `/rating-versions/<K2 id>` with `history.pushState` plus a `popstate` event. The URL changed, but the page's `<h1>` kept reading "fremtpl2-wf701-k1 @1" and a wait for the h1 to contain "k2" timed out (30 s). Reaching K2 through the chip link on `/demo` rendered "fremtpl2-wf701-k2 @1" correctly. **Not diagnosed.** The file reads data only when the component mounts; a route-parameter change on a mounted component would not refetch. This is a suspicion from the grep below, not a proven cause, and a pushState-plus-popstate is a synthetic navigation that may differ from a router push. LOW, owner P3-C (the maintainer's ruling to-lead "2026-11-09 21:10:32 GMT", item (d)). Not on the demo path, which uses chip clicks.

## Evidence

At tree 374a22bf33ad, `grep -nE "watch|onBeforeRouteUpdate|route\.params|useRoute|onMounted" frontend/src/views/RatingVersionView.vue` prints two lines: `2:import { computed, onMounted, ref } from "vue";` and `22:onMounted(async () => {`. No `watch`, no `onBeforeRouteUpdate`, no `useRoute`. The id arrives as the prop `id` (`const props = defineProps<{ id: string }>();`, line 8) and is read once, in `onMounted`. The router entry is `frontend/src/router/index.ts:244`. *(Dated correction, 2026-11-09, by the executor, on the audit N2 in `LG-8226`'s Audit section, adopted by the lead at from-lead "2026-11-09 22:05:11 GMT": the essay said the grep "prints one line" and then listed two, and put `defineProps` at line 6. Re-run at origin/main 2a66ce6388f4 (`git show origin/main:frontend/src/views/RatingVersionView.vue | grep -nE "watch|onBeforeRouteUpdate|route\.params|useRoute|onMounted|defineProps"`, rc=0) it prints `2:import { computed, onMounted, ref } from "vue";`, `8:const props = defineProps<{ id: string }>();` and `22:onMounted(async () => {`; the original five-term grep, without `defineProps`, prints lines 2 and 22 only. The 30 s timeout observation's own output is **not in any retained log**: only the seat's account of it exists. "Not diagnosed" stands.)*

Script and screenshots: `~/gi-pricing-plan.local/scratch/exec-rehprep2/rows-6-6b.v2.mjs`, `~/gi-pricing-plan.local/scratch/exec-sl1913/row6b/`.

## Disposition

Register decision: deferred with an owner, P3-C. The runbook for the Wednesday 11 November demo says to move between versions by the chips, not by URL. First step: reproduce with the router's own navigation (`router.push` from one version to another) before any fix.
