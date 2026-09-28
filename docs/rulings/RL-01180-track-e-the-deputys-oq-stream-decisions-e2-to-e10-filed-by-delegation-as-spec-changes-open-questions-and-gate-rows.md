---
id: RL-1180
family: ruling
title: Track E — the deputy's OQ-stream decisions E2 to E10, filed by delegation as spec changes, open questions and gate rows
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-28
owner: decision-maker
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-550, OQ-554, OQ-620, OQ-1181, OQ-1182, RL-856, RL-881, RL-885, WK-673, WK-674, WK-675, WK-690]
---

# RL-1180 — Track E: the deputy's OQ-stream decisions E2 to E10, filed by delegation as spec changes, open questions and gate rows

## Verified first, at df8e5811a151a99c7317690faf9278a6dc3400be

**This record decides nothing new.** Each item below was decided by the deputy, by delegation.
The deputy's entry is headed "THE OQ STREAM", is dated 2026-09-28 at 11:33:12 BST, and was relayed
by the lead. This record quotes the deputy's words for each item and names the spec edit that
applies it, as the decision-maker charter requires: *"A spec edit is never made without a
ruling record in the same commit naming it as that ruling's disposition."* Each decision is
attributed in the edits as: Maintainer decision by delegation (deputy, on the maintainer's
instruction of 2026-09-28 11:24 BST), 2026-09-28 11:33:12 BST.

**Not in this record:** E1 is Track D's, in its own ruling. E3 (WK-690's start gate) and E11
(the P1a/P1b headers and the "Where the project is" row) are roadmap-only, and go in Track E's
second PR (`p2-e-roadmap`), on the lead's routing.

This record was drafted in the decision-maker's worktree, on branch `p2-e-spec`, cut from
`origin/main` = `df8e5811` (#823) with a clean status. Clock at drafting: 2026-09-28 11:45:11
BST, read by `TZ=Europe/London date`.

**Re-read at `df8e5811` before writing** (spec `file:line`, with the pre-edit text):

- `docs/open-questions.md:41` holds OQ-550, struck, with the status "Deferred with an owner".
  Line 46 holds OQ-554, **open**. Line 128 holds OQ-620, **open**. The file's allocation
  marker still reads `Next free: OQ-OVR-19`. That is the pre-migration form and is not used
  here: the ids come from the lead, then from `doc-id.py next --ref origin/main` at the mint.
- `docs/roadmap.md` §10, the decision-gate table. Before Phase 2 reads `13 (0 open)`. Before
  Phase 3 holds `**OQ-620**` unstruck and reads `9 (1 open)`. The Deferred row's id cell reads
  `~~OQ-550, OQ-551, OQ-552, OQ-553~~ ✔` and its count `34 (0 open)`. **OQ-554 is on no row**,
  which the roadmap's 2026-09-03 notes record twice. At `df8e5811`, the coverage check prints
  `missing` = OQ-538, OQ-539, OQ-549, OQ-554, OQ-602, OQ-603, OQ-604, OQ-652 and OQ-656. Eight
  of those are the "recorded rather than placed" ids of the 2026-08-26 note. The ninth is
  OQ-554.
- `docs/specs/02-modelling.md:915` is §4.6. Its 2026-08-22 note (lines 946–971) records the
  parser diverging three ways and leaves the choice to WK-690. The parser is
  `pricing_core.data.expressions`, built for `01` FR-36. `02` FR-95 (`:96`) puts `expression`
  factors on "the same grammar".
- `docs/specs/06-governance.md:145` is FR-364. Its 2026-08-29 amendment reads
  "`structural_diff` carries a **trigger rather than an owner**" (from `RL-885`). `RL-881` is
  FR-257's four-limb split.
- `docs/specs/03-rating-engine.md:591` already holds `POST /api/v1/rate-tables/{slug}/versions`,
  "New Rate Table Version with change note". The gap in register row F-W10-3
  (`docs/findings/register.md:67`) is that no *route implements* it; it is not missing from
  the spec.
- `docs/specs/07-platform.md:141` is FR-430. Register row F54 (`register.md:95`) records that
  key issuance mints only for `environments[0]`.
- `docs/specs/06-governance.md:64` (the Governed Artifact list) and `:119` (the §3.3 evidence
  row) both name Rate Table Version.
  `packages/pricing-core/src/pricing_core/rating/compile.py:313` is `_MATURITY_CHECK_EXEMPT`.
  Its comment calls the `rate_table` exemption "provisional", pending OQ-620.
- **OQ-550's call sites, re-counted:** `git grep -n '<ChartFigure' df8e5811 -- 'frontend/src/*.vue'`
  prints **13 lines in 11 files**. `#257` is `a551469a` ("feat(w6b-12): dataset lineage"), and
  its diff adds `<ChartFigure` in `frontend/src/components/LineageGraph.vue`. The deputy's
  figure of 13 holds.

## Ruled

Each item applies the deputy's decision as the deputy wrote it.

**E2 — OQ-1181, new, decided (a).** The deputy's words: *"the spec is right for the objective
grammar. The parser is to gain `where()` (SymPy `Piecewise`, evidenced), refuse bare
comparisons, `%` and ternaries outside `where`, and enforce the node-count and depth limits.
File it as a new OQ with (a) spec right / (b) parser right, recommendation (a), decided (a).
The fix is WK-690's first slice, not today's."*
**The scope was ruled by the deputy by delegation**, in the entry of 2026-09-28 headed "E2
scope RULED", at 11:40:40 BST. That entry answers the consequence first flagged here: the same
parser serves FR-95 factors, `01` FR-36 recipes and `01` §4.5 checks. The deputy's words:
- *"One parser, one allow-list walk, one security review, with a named profile per context.
  This is not a parser split."*
- *"The `objective` and `factor` profiles are §4.6 as written. Comparisons appear only inside
  `where(cond, a, b)`. Bare comparisons, `%`, ternaries and boolean operators are refused. The
  function set is §4.6's ten."*
- *"The `recipe` (`01` FR-36) and `check` (`01` §4.5) profiles keep the operators they accept
  today."* They gain `where` and the other functions. `ceil coalesce floor round` *"stay
  recipe/check-only"*.
- *"The node-count ≤ 200 and depth ≤ 20 limits (configurable) apply to all four profiles"*.
  *"The WK-690 slice first measures the repo's recipe and check corpus"* against them, and if
  any real expression exceeds a limit, it *"reports to me before enforcing, rather than raising
  the limit silently."*
- The decision line: *"strict for objectives and factors; recipes and checks by profile
  (deputy, 2026-09-28)"*.

Disposition:
- A new OQ-1181 row in `docs/open-questions.md` (MODEL) and in `02` §10, marked decided. Both
  carry the decision line verbatim.
- At the head of `02` §4.6, a dated amendment: *"One parser and one security review; the
  grammar is per-context profiles of it"*. Below it, the profile table (context → bound
  symbols, operators, functions). Nothing is struck.
- A dated note under §4.6's 2026-08-22 note.
- A dated amendment on `02` FR-144, naming the `objective` profile and WK-690's first slice.
- `01` FR-36's "minus statistical functions" is pointed at the `recipe` profile, and `01`
  §4.5's `expression` check at the `check` profile.
- The gate table's Before Phase 2 row gains OQ-1181, struck.

**No new requirement:** §4.6 already states the grammar. The obligation is a profile table and
an owner on the requirements that cite it. All of this is spec text; the code is WK-690's.

**E4 — `structural_diff`'s owner is WK-673.** The deputy's words: *"the owner is **WK-673**. At
submission it persists FR-219's diff as a blob and registers the verifier, before WK-673 wires
FR-257's gate (RL-881). This is a spec change in `06` naming the owner and the mechanism."*
Disposition: a 2026-09-28 amendment at the end of `06` FR-364. The 2026-08-29 "trigger rather
than an owner" clause is marked superseded in place, not deleted. **This supersedes `RL-885`'s
spec change 1 for `structural_diff` only.** Its owners for `regression_run` and
`dislocation_run`, and its invariant, stand.

**E5 — the manual-edit route.** The deputy's words: *"add the route to `03` §5.1 now,
following the existing create paths (a change note is required; confirm, then create). Owner
WK-675's editor slice. Spec change first, as the row demands."* The route row already
existed, so this amends it rather than adding a second (lead, 2026-09-28, answer 7).
Disposition: `03` §5.1's `POST /api/v1/rate-tables/{slug}/versions` row now carries a request
shape that follows the import route (edited cells against a named base, a diff for
confirmation, `confirm: true` creates), the FR-229 change note, and the owner.

**E7 — one key per granted environment.** The deputy's words: *"the owner is **WK-674**, and
the shape is **one key per granted environment**. That shape isolates a leaked key to its
environment and matches ADR-710's boundary. A spec change in `07` (FR-430) comes first."*
Disposition: a 2026-09-28 amendment on `07` FR-430.

**E8 — OQ-620 decided (b).** The deputy's words: *"decided, option (b) as recommended. Nothing
contradicts it, and its deciding test cannot be measured in Phase 2. The decision is taken now
so that WK-675's editor slice does not inherit it."* Disposition:
- `03` gains **FR-1183**: a Rate Table Version has no lifecycle and no status, it is governed
  through the pinning Rating Version, and RL-856's exemption is permanent. It carries a revisit
  trigger, which is OQ-620's unmeasured deciding test.
- `06` §2 and `06` §3.3 strike Rate Table Version in place.
- OQ-620 is struck and decided in the register and in `03` §10.
- The Before Phase 3 row strikes OQ-620 but keeps it there for the revisit, and recounts to
  9 (0 open).

**E9 — OQ-554 decided (b).** The deputy's words: *"decided, option (b), a review step at each
close. Put it on the gate table's 'Deferred / any time' row as decided."* Disposition:
- `00` gains **FR-1184**: the per-close review of cited requirements.
- `.claude/skills/close-workstream` gains §5c, the procedure, with its `Verified` entry
  (lead, 2026-09-28, answer 6).
- OQ-554 is struck and decided in the register and in `00` §10.
- It is placed on the Deferred row, struck.

**E10 — OQ-550 re-opened.** The deputy's words: *"its trigger fired (#257 added a `ChartFigure`
caller; there are now 13 call sites). **Re-open it as a WK-675 entry decision**, due at
WK-675's map plan, and fix the gate-table cell that shows it struck."* Disposition:
- OQ-550 is un-struck, owned by WK-675 at its map plan, and set to status **open**, in the
  register and in `00` §10. The 2026-08-25 and 2026-08-26 records stay as they were believed.
- On the Deferred row, OQ-550 is un-struck and split out of its range, with its trigger in
  the italics.
- The Deferred row recounts to 35 (1 open).

**F3's OQ — OQ-1182, open.** The deputy's words: *"file the OQ first, with options (a) isolated
plus cumulative in a declared step order, with an explicit interaction-residual line so the
parts reconcile to the total; (b) Shapley over steps; (c) cumulative only. Recommendation (a).
The spike runs on freMTPL2 and measures the size of the residual and how much the order
changes the result. I decide on the record."* Disposition:
- OQ-1182 is added to the register (RATE) and to `03` §10, with status **open**.
- It is placed on the Before Phase 2 row, unstruck. WK-673 is Phase 2 work, so the method is
  a Phase 2 entry decision (lead, 2026-09-28, answer 4).
- The options are the deputy's words. The trade-offs are the decision-maker's, labelled as
  such in the row.
- **The pass criterion, ruled by the deputy by delegation**, is in the entry of 2026-09-28
  headed "F3 pass criterion RULED", at 11:39:35 BST. It is quoted in the options cells of (a)
  and (b) (lead, 2026-09-28):
  - *"Hard gate for any method: exact reconciliation. The parts plus the residual line sum to
    the total exactly, in Decimal on the rating path (CLAUDE.md §7), per policy and at
    portfolio level."*
  - *"(a) passes if S ≤ 0.10 and R ≤ 0.10 on every change set measured. There are at least
    four sets: K = 3, 4, 5, 6. At least one must contain a non-linear step such as a minimum
    premium or a cap"*.
  - *"If (a) fails on any set, the record recommends (b) exact Shapley, capped at K ≤ 6."*
  - *"(c) is not chosen in either case"*.
  - Both S and R are taken over D = Σᵢ |isolatedᵢ|.
  - The status stays **open**, with recommendation (a), decided on the F3 research record.

**The gate table.** Every count was recounted by the `docs-audit` snippets, not incremented.
Those snippets were rewritten in this PR, because their pre-migration pattern matched no id.
The counts are: Before Phase 2, 15 (1 open); Before Phase 3, 9 (0 open); Deferred, 35 (1 open).
A dated note beneath the table records the five edits.

## What it obliges

- **Owed to the register, routed by the lead to an auditor** (`docs/findings/register.md` is
  the auditor's file). This record touches none of these rows:
  - **E6, row F48** (`register.md:89`). Record the decision there. The deputy's words: *"a
    **shared Redis counter, per tenant** (ADR-710 makes Redis per-tenant; an in-process limiter
    'is not a limit'). Record the decision on the F48 row now; WK-674's map plan builds it."*
  - **Row F54** (`:95`), which reads "not started … unowned". Its owner is now WK-674, and its
    shape is `07` FR-430's 2026-09-28 amendment.
  - **Row F-W10-3** (`:67`). The spec half is now done in `03` §5.1, and the route remains
    WK-675's editor slice.
- **Owed in code, by the slice that next touches the file.** No code is written here: the
  decision-maker has no write access to code.
  - The comment at `packages/pricing-core/src/pricing_core/rating/compile.py:313` calls the
    `rate_table` exemption "provisional" pending OQ-620. It is now permanent under FR-1183.
  - `test_rate_table_version_row_has_no_status_column` in
    `backend/tests/test_rating_version_compile.py` is FR-1183's evidence and carries no marker
    for it.
  - Neither of these is a defect in behaviour: the tripwire stays correct.
- **WK-690's first slice** brings the parser to §4.6 for objectives (FR-144's amendment).
- **WK-673** owns `structural_diff` (FR-364's amendment). It also takes OQ-1182's decision
  from the F3 spike's research record.
- **WK-674** builds one key per environment (FR-430's amendment) and the F48 counter.
- **WK-675** takes OQ-550 at its map plan and builds the manual-edit route (`03` §5.1).
- **Every close** from now runs `close-workstream` §5c (FR-1184).
- **WK-690's slice** first measures the recipe and check corpus against the limits. It
  reports any real expression over a limit to the deputy before enforcing.
- **Not decided here:** OQ-1182 (the deputy's, on the spike's record). `docs/process/checklists/work-item-close.md` is the
  process checklist, and it does not yet carry §5c's step. Whether it should is the lead's
  call: it is not a decision-maker file.

## Acceptance — the violation that must become detectable

The violation: **an open question that sits on no decision-gate row, or on a row whose stated
count disagrees with its struck and unstruck ids.** OQ-554 was on no row for a month, and the
`docs-audit` coverage snippet could not see it. Its pre-migration pattern
(`OQ-[A-Z]+-\d+`) found 0 ids in `docs/open-questions.md` at `df8e5811`, so it printed `none`
three times on any tree.

- *Violation: an OQ in `docs/open-questions.md` that no gate row names.* The rewritten coverage
  snippet lists it under `missing`. It was shown red on the tree before this PR, where it
  listed OQ-554 beside the eight recorded ids. On deliberately broken input (OQ-1182 deleted from the Before Phase 2 cell of a scratch
  copy of this PR's tree), it listed `OQ-1182` first under `missing`. This was run before filing.
- *Violation: the id pattern stops matching the register.* The coverage snippet now asserts a
  non-empty id set, so a pattern that matches nothing fails loudly instead of printing `none`. This was run on a
  scratch copy with every id rewritten to the pre-migration form: exit 1, `AssertionError: no OQ
  ids found: the id pattern no longer matches the register`.
- *Violation: a row's stated `N (M open)` differs from its ids.* The recount snippet prints the
  stated and actual counts side by side. It was shown red on the same scratch copy.
  The Deferred row, restored to `34 (0 open)`, printed `actual 35 (1 open)  stated 34 (0 open)`.
  The Before Phase 2 row, minus OQ-1182, printed `actual 14 (0 open)  stated 15 (1 open)`.

The spec edits themselves are prose, and no check can hold them to the deputy's words. That is
what the quotations above are for.
