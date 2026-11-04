---
id: FD-1978
family: finding
title: input, select and textarea borders outside WK-675 still use the 1.48:1 border-slate-300, so NFR-463's WCAG 2.2 1.4.11 non-text contrast is not met on 53 controls in 13 Phase 1 frontend files
status: active
created: 2026-11-03   # drafted 2026-11-03 under working id 8285
owner: auditor
tree: c807a59d1a26d12e63d88bc395ac3dcc373aa919
corrected_by: []
relates: [FD-1959, FD-1974, RL-1973, OQ-1960, WK-675, WK-1178, WK-690, WK-663, WK-664, SL-1971]
---

# FD-1978 — input, select and textarea borders outside WK-675 still use the 1.48:1 border-slate-300

## Finding

**LOW (proposed by the auditor; the lead rules).** Authority: the lead's "2026-10-29 22:13:59 GMT" R10-DP1 (b), which left the input borders
outside WK-675 as "a candidate finding the auditor files" (owner: the Work that owns each surface; P3 unless a P2 surface), and
FD-1959's Resolved paragraph ("the finding is filed in the next docs batch"). Filed under working id 8285.

At `origin/main` `c807a59d1a26d12e63d88bc395ac3dcc373aa919` (merge 43, #1412; frontend/src last changed by merge 42, #1411), **53 text
inputs, selects and textareas in 13 files carry `border-slate-300`**, #cbd5e1, which is **1.485:1** against white (WCAG 2.2 relative
luminance, recomputed here). WCAG 2.2 1.4.11 (Non-text Contrast, AA) needs 3:1 for the boundary of a control a user must find. SL-1971
fixed the same class on the WK-675 surfaces (FD-1959 F2, moderate, replacement `border-slate-500`, #62748e, 4.764:1); none of the 53
is on a WK-675 surface. `NFR-463` (`specs/00-overview.md`, "the SPA meets WCAG 2.2 AA") is therefore not met on these controls. Its
dated amendment (2026-09-30, OQ-550 / RL-1307) concerns the chart table equivalent and does not narrow the baseline. FD-1959 and
FD-1974 carry the WK-675 limbs; RL-1973 closed FD-1959 on its static limbs and named this input-border residue as not filed there.

## Evidence

**Predicate (verbatim, runnable)** at tree `c807a59d1a26d12e63d88bc395ac3dcc373aa919`:

```
git -C <repo> grep -n 'border-slate-300' c807a59d1a26d12e63d88bc395ac3dcc373aa919 -- frontend/src ':!*__tests__*'
python3 ~/gi-pricing-plan.local/scratch/a11y-aud/classify-v2.py c807a59d1a26d12e63d88bc395ac3dcc373aa919 <repo>
```

The grep gives **102 hits in 29 files**. `classify-v2.py` (a quote-aware forward scan of every template tag, replacing `classify.py`'s
nearest-preceding-`<tag` rule) assigns each hit to the tag whose span contains it: **select 29, input 21** (15 untyped, 5
`type="number"`, 1 `type="date"`), **textarea 3** = **53 input-like**; the other 49 are button 25, th 8, RouterLink 8, section 4, div 3,
ul 1 (not 1.4.11's boundary limb: a labelled button's border is not needed to identify it). 0 hits fall outside a tag (no script
constant). Output: `classify-v2-main.txt` (all 102), `outside-typed-v2.txt` (the 53), beside the script. **The draft's 51 to 53
ambiguity is resolved to 53:** the five inputs within six lines of a `type="button"` (`FactorWorkbenchView.vue:438,639`,
`ReferenceView.vue:276,366`, `RuleSetView.vue:385`) were each read; every one is an `<input` tag of its own (number, number, date, text, text)
and the button is a separate neighbouring element. The count is the same as the draft's 53 at `265a552e`, so merge 42 changed none of them. No
input-like hit sits in the WK-675 files (`components/rating/`, `components/dag/`, `views/Rate*`, `QuoteSandboxView`).

| File (under `frontend/src/`) | select | input | textarea | Total |
|---|---|---|---|---|
| `views/ModelSpecBuilderView.vue` | 12 | 6 | 0 | 18 |
| `components/RuleBuilder.vue` | 3 | 6 | 1 | 10 |
| `views/FactorWorkbenchView.vue` | 5 | 3 | 0 | 8 |
| `components/FactorCreateForm.vue` | 3 | 1 | 1 | 5 |
| `views/DatasetDetailView.vue` | 1 | 1 | 0 | 2 |
| `views/ProfileView.vue` | 2 | 0 | 0 | 2 |
| `views/ReferenceView.vue` | 0 | 2 | 0 | 2 |
| `components/AcknowledgeDialog.vue` | 0 | 0 | 1 | 1 |
| `components/ModelSelector.vue` | 1 | 0 | 0 | 1 |
| `components/ObjectivePicker.vue` | 1 | 0 | 0 | 1 |
| `components/WorkspaceSelector.vue` | 1 | 0 | 0 | 1 |
| `views/PredictionView.vue` | 0 | 1 | 0 | 1 |
| `views/RuleSetView.vue` | 0 | 1 | 0 | 1 |
| **13 files** | **29** | **21** | **3** | **53** |

Lineage: the draft is `~/gi-pricing-plan.local/scratch/a11y-aud/FD-candidate-draft.md` (aud-a11y, 2026-10-29, tree `265a552e`), evidence and not
authority. The accessibility-tester's "about 60" (lead's R10-DP1 (b)) is not reproduced by either predicate; the gap is its own
looser count and is not chased.

## Owner per surface

The roadmap names no frontend file, so a surface is mapped by the Work its first commit built it under (`git log --diff-filter=A`: `w6a` =
Phase 1a Data Workbench frontend, `w6b` and `w5` = Phase 1b Modelling Workbench frontend) read against `docs/roadmap.md`'s `### WK-` sections
and `status:` lines. That is the auditor's reading, not a record.

| Built under | Work, status (`docs/roadmap.md`) | Files (hits) | Hits |
|---|---|---|---|
| `w6a` | **WK-663**, closed, P1a (WK-662 retired, successors WK-663 and WK-664) | `AcknowledgeDialog` 1, `DatasetDetailView` 2, `ProfileView` 2, `ReferenceView` 2, `RuleBuilder` 10, `RuleSetView` 1 | 18 |
| `w6b`, `w5` | **WK-664**, closed, P1b | `FactorCreateForm` 5, `ModelSelector` 1, `WorkspaceSelector` 1, `FactorWorkbenchView` 8, `ModelSpecBuilderView` 18, `PredictionView` 1 | 34 |
| `w6b` | **WK-664**, closed; carried by WK-1178 with the rest (lead ruling, 2026-11-03: one owner per row; WK-690 edited the file in SL-1273, which is provenance only) | `ObjectivePicker` 1 | 1 |

Every Work that built a surface is closed or retired, so none can own a fix. **The open Work that carries them is WK-1178** (P2 standing
maintenance, `status: active`), which already edited `RuleBuilder`, `RuleSetView` (SL-1409, FD-1356 fix) and `ModelSpecBuilderView`
(SL-1860) in P2. **No surface is a P2 surface** in the sense of FD-1959's: none is in WK-675's scope and none is in the rating path. The
one open P2 Work that has edited any of them, WK-690 (`ObjectivePicker`, SL-1273), does not own it: **the lead ruled on 2026-11-03 that `ObjectivePicker` stays under WK-1178 with the other 52** (one owner per row; WK-690 was in its close audit that day), and WK-690's edit is a provenance note only. The lead also ruled that this finding has no due date: a P3 deferral, disposed under G3 at the P2 close.

## Severity

**LOW.** No mispricing and no data loss; only the control boundary fails 1.4.11. The same class FD-1959 rated moderate on the rate-table
path; it is rated lower here on the draft's reading that the accessible-name and message paths of these Phase 1 surfaces are intact,
which this record did **not** re-read. Raise it if a later read finds otherwise.

## Remedy

The same one-class change SL-1971 made: `border-slate-300` to `border-slate-500` on each of the 53 hits, shown by the grep after (0
input-like hits) and the computed ratio (at least 3:1). Not testable in vitest (happy-dom computes no rendered contrast); a rendered
claim is OQ-1960's browser limb, which will re-test these surfaces too.

## Disposition

Proposed (the lead rules): **deferred with an owner: WK-1178**, phase 3 (the R10-DP1 (b) default, because no surface is a P2 surface), no due date. The event that
next confirms or discharges it: **the lead's ruling on this record, then WK-1178's disposition under roadmap G3 at the P2 close**, which
carries it or accepts it by a dated line. Open, filed under working id 8285.

## Relates

FD-1959 (the WK-675 limbs, closed on its static limbs), FD-1974 (the ten carried WK-675 lows), RL-1973 (R10-DP4 (c)), OQ-1960 (the
browser limb), SL-1971 (the fix of the WK-675 half of this class).
