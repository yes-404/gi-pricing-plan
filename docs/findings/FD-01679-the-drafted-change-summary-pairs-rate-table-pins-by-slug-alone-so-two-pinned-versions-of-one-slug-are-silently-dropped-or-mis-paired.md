---
id: FD-1679
family: finding
title: FR-242's drafted change summary pairs rate-table pins by slug alone, so two pinned versions of one slug are silently dropped or mis-paired
status: closed
created: 2026-10-12
owner: auditor
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
corrected_by: []
relates: [WK-673, SL-1678, PL-1677, PL-1267, SL-1503, FR-242, RL-1498, RL-1538, SL-1543]
---

# FD-1679 — the drafted change summary pairs rate-table pins by slug alone

*(Minted 2026-10-12 as FD-1679 from working id 9895, in the early-mint PR of `PL-1677` and
`SL-1678`, on the maintainer's (by delegation) entry "2026-10-12 05:58:56 BST" (`to-lead.md`).
Inside a verbatim quote the minted id stands in brackets, `[FD-1679]`, where the entry wrote the
working id.)*

Filed by the planner from three entries by the maintainer (by
delegation) in `channel/to-lead.md`: "2026-10-12 05:43:54 BST", "2026-10-12 05:44:45 BST" and
"2026-10-12 05:57:57 BST". It is filed on the lead's instruction, from-lead "2026-10-12 05:58:38
BST". Every `file:line` below was read at `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a`.
The code is `SL-1503`'s (WK-673, WF-699 E1, `RL-1498`).

## Finding

**Severity HIGH, owner WK-673.** The maintainer's (by delegation) entry "2026-10-12 05:43:54
BST — [FD-1679]: HIGH (not MEDIUM), owner WK-673; a LOUD GUARD merges BEFORE SL-1543", verbatim:

```text
Verified at main: rating_versions.py:1404 `{ref.slug: ref for ref in …rate_tables}` keeps the LAST ref per slug. It feeds FR-242's drafted change summary (:1377-1400, SL-1503's), which an approver reads.
- With two pinned versions of one slug (RL-1538), the summary silently omits one table's change, or reports a wrong from/to pair.
- That is silently wrong approval evidence: the same class I rated HIGH for FD-1660 at 02:35:40. Consistency requires HIGH.
Owner WK-673 (SL-1503 delivered FR-242 under it).
```

`03` FR-242 requires a change summary *"generated as a draft from the structural and rate-table
diffs"* (`03-rating-engine.md:142`). `GET /api/v1/rating-versions/{id}/change-summary-draft`
(`backend/src/app/platform/rating_versions.py:1329-1401`, `draft_change_summary_for`) pairs the
baseline's and the candidate's rate-table pins through `_pins_by_slug` (`:1404-1408`):

```python
return {ref.slug: ref for ref in Pins.model_validate(pins).rate_tables}
```

The last ref for a slug wins. Two versions of one slug are **valid** pins: `RL-1538` (Option B,
built as B1) enters each seeded table as its ratio to its seed origin, *"two table pins plus an
existing expression step"*. `Pins` (`packages/model-schema/src/model_schema/rating.py:70-84`) has
no duplicate check, and `create_rating_version` (`rating_versions.py:258-310`) stores the pins as
given. The defect is therefore the consumer, not the input. The maintainer's (by delegation) entry
"2026-10-12 05:44:45 BST — [FD-1679] is LIVE: (a) a standalone tiny WK-673 row NOW; create stays
permissive (RL-1538); PLUS a sweep for the same defect class" says so: *"Create stays permissive:
RL-1538 allows two versions of one slug on purpose; the defect is the consumer, not the input."*

**Reachable on `main` today**, from the lead's from-lead entry "2026-10-12 05:44:28 BST", by code
reading at `604ea084`. `SL-1678`'s Red 1 proves it end to end through the HTTP create route.

## Evidence

The code read at `604ea084` gives three silent outcomes (`PL-1677` §Premises). Each is a red that
`SL-1678` runs on `main` before its fix:

1. **A false pair (Red 2, the strongest proof, per the maintainer's (by delegation) entry
   "2026-10-12 05:57:57 BST": *"Red 2, the FALSE "X one→two", is the strongest proof"*).** The
   baseline pins `[X@1]` and the candidate pins `[X@1, X@2]`. Then `after = {X: X@2}`, so the
   summary reports **X 1 → 2** as a replacement, though the candidate still pins X@1.
2. **A dropped change (Red 1).** The candidate pins `[X@2, X@1]`. Then `after = {X: X@1}` equals
   `before`, and the summary has **no entry for X**: the edited table's change is omitted.
3. **The baseline side (Red 3).** The baseline pins `[X@1, X@2]` and the candidate pins
   `[X@2]`. Then `before = {X: X@2}`, and there is no entry.

The approver reads all three as complete approval evidence (FR-257 requires a change summary).

### The class sweep

The maintainer's (by delegation) entry 05:44:45 makes the finding's scope *"the class, not only
:1404"*. Two sweeps were run, each as **one** command under `flock -w 1800 /tmp/slots/gate-2`,
at base `604ea084c96efe93f521fb9ba17738e05241e61a`. The planner's run followed the lead's ruling,
from-lead "2026-10-12 05:47:19 BST".

**Sweep 1, the maintainer's predicate, verbatim from the 05:44:45 entry.** Run by the planner at
2026-10-12 05:51:39 BST, from the repository root:

```bash
git grep -nE '\{[a-z_]+\.slug *:|\.slug\]? *=|by_slug' -- backend/src packages frontend/src
```

**rc 0, 99 hits, every one read.** One read-only subagent read the hits with file reads only, and
the verdicts are the planner's. Result: **4 GUARDED, 10 SAFE, 0 LISTED, 85 not pin consumers.**

| Hit | What it does with pins | Verdict |
|---|---|---|
| `backend/src/app/platform/rating_versions.py:1404`, `:1408` | `_pins_by_slug`: rate tables keyed by slug alone (the defect) | **GUARDED** by `SL-1678` |
| `rating_versions.py:1377`, `:1378` | `before`/`after` in `draft_change_summary_for`, the two callers | **GUARDED** by `SL-1678` |
| `rating_versions.py:616` | `WorkspaceResolver.resolve`, the algorithm branch: slug and version (`:617`) | SAFE |
| `rating_versions.py:764` | `WorkspaceResolver.resolve`, the factor branch: slug and version (`:765`) | SAFE |
| `backend/src/app/platform/rate_tables.py:299` | `_load_table` for a `rate_tables` pin, then `_load_version(table_row.id, ref.version)` (`:1159-1161`) | SAFE |
| `backend/src/app/platform/reference.py:317` | `_load_table` for a `reference_tables` pin, then a version filter (`:467`, `:498`) | SAFE |
| `backend/src/app/platform/objectives.py:530` | `resolve_ref` for a `custom_objectives` pin: slug and version (`:531`) | SAFE |
| `backend/src/app/platform/perils.py:491` | `load_structure_by_ref` for a peril-structure `models` pin: slug and version (`:492`) | SAFE |
| `backend/src/app/platform/sub_graphs.py:168` | `_row` for a `sub_graphs` pin: slug and version (`:169`) | SAFE |
| `packages/pricing-core/src/pricing_core/rating/compile.py:820`, `:822` | `by_slug` over one resolved model pin's factors; the pin itself is `resolved_pins[str(model_ref)]` (`:817`) | SAFE |
| `packages/pricing-core/src/pricing_core/rating/runtime.py:877` | `columns` keyed by factor slug within one GLM's own factors; scorers keyed by `str` ref (`:885-897`) | SAFE |
| *(not a hit, read in passing)* `compile.py:731` | `check_step_refs_pinned`: the exact `ref in pinned` test decides the refusal (`:729`); the slug match only fills the message's "(pinned at … instead)" | SAFE |

**LISTED: none.** The 85 hits that are not pin consumers are SQL lookups (by slug and version, or
a `max(version)` next-number query by design), Environment, Role and Dataset rows, factor and
banding maps within one model or one table, three frontend list `find`s, and test assertions.
`PL-1677` §Class sweep lists each one on its own line.

**Sweep 2, the lead's supplementary grep for the forms sweep 1 cannot match** (TypeScript
`Map`/`reduce`/`fromEntries`). Recorded in the lead's from-lead entry "2026-10-12 05:57:28 BST",
run at `origin/main` `604ea084`, the command verbatim from that entry:

```text
git grep -nE '\[[a-zA-Z_]+\.slug *,|\.slug\] *:|acc\[[a-zA-Z_]+\.slug\]|Object\.fromEntries' origin/main -- frontend/src backend/src packages (tests excluded by grep -v)
```

It gave **4 hits, 0 keyed by slug, 0 pin consumers**, in the entry's words: *"QuoteForm.vue:39
(field.name), PredictionView.vue:60,:70 (column), RateTableEditorView.vue:60 (cell key) — none
slug-keyed, none pin consumers; plus 'new Map(' in frontend/src: 4 (f.id, step id x2, id) — none
slug. Supplementary result: SAFE, nothing added."*

## Disposition

**Fix before close, owner WK-673**, in two limbs:

- **The loud guard is `SL-1678`** (under `PL-1677`, a dated delta to `PL-1267`). The change
  summary refuses with **409 `VALIDATION_FAILED`**, naming FD-1679 and the slug, when the
  candidate's or its baseline's **rate-table** pins carry one slug twice. Create stays permissive.
  The refusal covers `rate_tables` only, because the summary reads no other kind (the lead's
  ruling, from-lead "2026-10-12 05:48:32 BST"). The maintainer (by delegation) accepted the 409
  and the guard's place inside `_pins_by_slug` in the 05:57:57 entry. **`SL-1678` merges before
  `SL-1543`** (A-4), which puts a B1 version into the demo.
- **The remaining limb is DP-P1, open, owner WK-673:** the real pairing fix, which decides which
  old version pairs with which new one when a slug carries two. `PL-1677` records the options:
  (a) pair by the referencing `table` step, through `diff_algorithms`' step pairing (recommended);
  (b) a set diff per slug; (c) keep the refusal as the rule. It goes to a decision-maker inside
  WK-673's plan when a seat frees (05:57:57: *"Not urgent: the guard makes it loud."*).

Per `CLAUDE.md` §14 it is HIGH in P2 and needs a resolution before any P3 start. The event that
next confirms or discharges the guard limb is `SL-1678`'s merge, with Reds 1 to 3 red on `main`
by their causes and green after.
