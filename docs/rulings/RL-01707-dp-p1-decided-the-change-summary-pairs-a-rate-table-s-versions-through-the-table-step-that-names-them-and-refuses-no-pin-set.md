---
id: RL-1707
family: ruling
title: PL-1677 DP-P1 decided — the drafted change summary pairs a rate table's versions through the `table` step that names them, pairs a pin difference no step names by slug only where it is the one such ref on each side, and refuses no pin set; SL-1678's guard is removed by the fix slice (FD-1679)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-14
owner: decision-maker
tree: 36e2610ab8135bc3b3563464e7f5f719713b168b
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FD-1679, PL-1677, PL-1267, SL-1678, LG-1681, RL-1498, RL-1538, FR-242, FR-219, FR-231, FR-237, FR-1399]
---

# RL-1707 — PL-1677 DP-P1: how the drafted change summary pairs two versions of one rate table

*(Minted 2026-10-14 as RL-1707 from working id 9996, in the D15 batch mint PR.)*

*Disclosure: drafted under **working id RL 9996**, reserved by the lead (team-lead) on
2026-10-14 (`~/gi-pricing-plan.local/handover/eta.md`, the line stamped "2026-10-14 09:24:15
BST": "RESERVED working id RL 9996 = the DP-P1 ruling (WK-673; FD-1679 real per-slug pairing
fix; PL-1677 :157 options), seat dm-dpp1"). The lead mints it. The fix slice this record
obliges has no id yet; it is called "the fix slice" below. Two neighbours are on unmerged
branches at this record's tree and are cited by branch and commit, not by id (see
Interactions).*

*Confirmed: dated 2026-10-14, on the maintainer's (by delegation) entry "2026-10-14 09:42:05 BST
— RL 9996 (DP-P1) CONFIRMED as drafted" (`to-lead.md`) item 1: "CONFIRMED, no amendment", read
at `0d8f1288`.*

*Read: dated 2026-10-14, on the maintainer's (by delegation) entry "2026-10-14 10:00:17 BST"
(`to-lead.md`), DP-5 (a), as a reading of pass 2 and not an extension (no sibling `RL-`): a pin
difference is a set-membership predicate, so "exactly one ref removed and one added" counts
distinct refs. `[X@1, X@1]` against `[X@1]` is no difference, and `[X@1, X@1]` → `[X@2]` is one
entry X 1 → 2 with the cell diff. Recorded in `PL-1701` DP-5.*

## How this was ruled

- **The decision point is `PL-1677`'s DP-P1** (`docs/plans/PL-01677-…-plan-delta.md:157`),
  which the plan leaves **open** for *"the decision-maker, as an `RL-` against WK-673's plan"*.
  This record rules it as `document-ids.md` §1.6's PL row requires (*"decision-maker rules
  decision points as `RL-`, never edits the plan"*). It does not edit `PL-1677`.
- **It is an `RL-` and not an `LG-` entry** (Lean P2 L1, `.claude/roles/decision-maker.md:35-42`
  at this tree: *"a separate `RL-` only when it corrects or reverses an earlier ruling or binds
  beyond the slice"*): it binds before its slice is cut, it carries `03` text, and it extends
  `RL-1498` DP-E1-5's shape. The lead confirmed the reading (cross-session message to dm-dpp1,
  logged from-lead "2026-10-14 09:25:48 BST").
- **The authority, each entry quoted with its author** (both channel files are local, so a
  repository reader cannot open them; RFC-777):
  - the maintainer's (by delegation) entry "2026-10-12 05:43:54 BST" in
    `~/gi-pricing-plan.local/channel/to-lead.md`, its last operative line: *"The real fix (diff
    keyed by slug with an explicit pairing of versions) is a DP for the WK-673 plan: which old
    version pairs with which new, when a slug carries two. It is not decided here."*
  - the maintainer's (by delegation) entry "2026-10-12 05:57:57 BST", same file, its DP-P1
    line: *"DP-P1 (the real pairing fix) is for a decision-maker inside WK-673's plan when a seat
    frees. Not urgent: the guard makes it loud."*
  - the maintainer's (by delegation) entry "2026-10-14 09:23:02 BST", same file, item 1: *"The
    decision-maker for DP-P1 runs at medium unless its ruling writes spec text; if it does, it is
    a separate CLI at --effort high, verified by its transcript's perTurnEffort."*
- **Written 2026-10-14 from 09:35 BST (by `TZ=Europe/London date`)** by the decision-maker seat
  `dm-dpp1`, in the worktree `.claude/worktrees/rl-9996`. **Every `file:line` below was read at
  `origin/main` `36e2610ab8135bc3b3563464e7f5f719713b168b`** (#1296, SL-1678), unless a branch
  or commit is named.
- **Effort.** This record writes spec text, so 09:23:02 item 1 sets it at high. Two checks:
  the lead read the transcript `dacca02e-0e11-4703-9f8f-f8df4fc8aa70.jsonl` as
  `"perTurnEffort":"high"` ×17 and `"medium"` ×0, `requestedModel` `claude-opus-5-5` ×17
  (from-lead "2026-10-14 09:25:48 BST"); this seat re-read it at 09:33:54 BST with
  `grep -o '"perTurnEffort":"[a-z]*"' <transcript> | sort | uniq -c`: `"perTurnEffort":"high"`
  ×137 and no other value; `"requestedModel":"claude-opus-5-5"` ×137.

## Locators — read at `36e2610a`

| What | Locator | What it says |
|---|---|---|
| The guard | `backend/src/app/platform/rating_versions.py:1405-1426` `_pins_by_slug` | refuses a repeated slug in `rate_tables`: `if ref.slug in by_slug:` (`:1416`) raises `PlatformError("VALIDATION_FAILED", …, 409, …)` naming FD-1679 |
| Its callers | `rating_versions.py:1378-1379` | `before = _pins_by_slug(baseline_row.pins)`, `after = _pins_by_slug(row.pins)`, the only pin reads in `draft_change_summary_for` (`:1329`) |
| The pairing | `rating_versions.py:1381-1401` | `for slug in sorted(before.keys() \| after.keys())`: one entry per slug; a cell diff when both sides pin it at different versions |
| No baseline | `rating_versions.py:1368-1369` | `if found is None: return draft_change_summary(None, None, [])`, before any pin read |
| The structural diff | `rating_versions.py:1377` | `diff_algorithms(previous, candidate)`, with no `fragments`: the top-level steps and mounts only |
| The entry shape | `packages/model-schema/src/model_schema/rating.py:1174-1190` `RateTableChange` | `slug`, `from_ref`, `to_ref`, `diff`, `pending`; `frozen=True, extra="forbid"` (`RL-1498` DP-E1-5) |
| A `table` step's ref | `rating.py:368-374` `RatingTableStep` | `rate_table_ref: ArtifactRef`, an exact `slug@version` |
| The step pairing | `rating.py:896` `_diff_steps` | pairs steps by `step_id`; a `table` step on both sides whose `rate_table_ref` differs is an `AlgorithmTableRepoint` |
| A pin no step names | `packages/pricing-core/src/pricing_core/rating/compile.py:716` | *"A pin no step names is allowed (FD-1297, DP-F3 (a))."* |
| FR-1399's pin accounting | `packages/pricing-core/src/pricing_core/rating/analysis.py:602-620` | a pin difference is an exact ref on one side only; one that no changed step's ref accounts for is its own `pin` change |
| Sub-graph steps | `pricing_core/rating/inline.py:8-10` | inlined fragment steps are renamed `<mount_point>__<step_id>`; the change summary never inlines (`:1377` above) |
| The drafting | `backend/src/app/platform/change_summary.py:30`, `:86` | entries sorted by `slug` only; `_table_line` renders one entry per line |
| The tests | `backend/tests/test_rating_version_change_summary_route.py:150-204` (E1), `:455-515` (SL-1678's three guard tests and the first-version test) | every rate-table pin in this file is named by no step: `_minimal_algorithm` (`backend/tests/test_rating_version_compile.py:53-75`) has no `table` step |
| The B1 shape | `docs/rulings/RL-01538-….md:73-79` | *"two `table` steps (the pinned version and its seed origin, both in `pins.rate_tables`) and one `expression` step"* |
| The spec | `docs/specs/03-rating-engine.md:142` (FR-242), `:196` (FR-1399), `:1052` (the §5.1 row, with SL-1678's dated 409 clause) | FR-242: *"generated as a draft from the structural and rate-table diffs"*; it says nothing about pairing |

## `CLAUDE.md` §0 — which of spec and code was wrong

- **The spec is silent; the code chose, and chose wrongly for valid input.** FR-242 says the
  draft is *"generated … from the structural and rate-table diffs"* and the §5.1 row says
  *"each re-pinned rate table's diff"*. Neither says how two versions are paired. `SL-1503`
  paired by slug (`RL-1498` DP-E1-5 fixed the shape, not the pairing). `RL-1538` then made two
  pinned versions of one slug valid input, and slug pairing drops or mis-pairs them (FD-1679).
  So this is a capability the spec does not specify. The fix is a spec change first (T1 and T2
  below), then code.
- **SL-1678's 409 clause is a disclosed interim**, not a contradiction. It stays true until
  the fix slice strikes it (T2).

## DP-P1 — ruled: (a), with a stated variant for pins no step names

**Ruled (a′).** The draft pairs a rate table's versions **through the `table` step that names
them**, as PL-1677's option (a) recommends, with one change to (a)'s last clause. **A pin
difference that no step entry names is paired by slug when it is the one such ref on each side**,
and is listed on its own otherwise. It is not always listed unpaired, as (a) drafted it. **No pin
set is refused.**

### The rule

The draft derives its rate-table entries from the two versions' algorithms and
`pins.rate_tables`, in two passes:

1. **An entry for a step.** For each `step_id` that is a `table` step in either algorithm,
   compare its `rate_table_ref` on the two sides. A step absent on one side, or not a `table`
   step there, has no ref there.
   - Same ref on both sides: no entry.
   - Both refs name the same rate table at different versions: **one entry** carrying the
     `step_id`, both refs, and the cell diff (FR-231), or `pending` under FR-232, as today.
   - The refs name different rate tables, or the step has a ref on one side only: **one entry
     per named table**, each carrying the `step_id`, the ref on its side, the other side null,
     and no cell diff.
   - Steps are paired by `step_id` only, as FR-219's diff pairs them (`_diff_steps`). A step
     whose id changed is removed and added. It is never paired across ids.
2. **An entry for a pin.** A pin difference is a ref in `pins.rate_tables` on one side and not
   on the other (exact `slug@version`, as FR-1399 compares, `analysis.py:612-619`). A pin
   difference that some step entry names, on either side, is part of that entry and gets no
   entry of its own. For each remaining slug:
   - exactly one ref removed and exactly one added: **one entry**, `step_id` null, with the
     cell diff, which is today's behaviour;
   - any other count: **one entry per ref**, `step_id` null, the other side null, no cell diff.
3. **Without both algorithms there is no entry for a step.** If `_algorithm_of` returns `None`
   for the baseline (`RL-1498` DP-E1-5's *"the baseline has no algorithm"*, `structural_diff`
   null), every pin difference goes to pass 2. A first version (no baseline) has no entries,
   as today (`:1368-1369`).
4. **Order.** Entries are sorted by slug, then entries for a step before entries for a pin, then
   by `step_id`, then by the `from_ref` and `to_ref` strings. This replaces `change_summary.py:30`'s
   sort by slug alone, which stops being a total order once one slug can have two entries.
5. **The text.** An entry for a step renders as today's line with ` (step <step_id>)` after the
   slug: `- <slug> (step <step_id>): version 1 -> 2, …`. An entry for a pin renders exactly as
   today.

The entries name **what the steps name and what the pins carry**. Whether each step's ref is
pinned is compile's to refuse (FR-237, `RATING_VERSION_UNPINNED`), not the draft's.

### Why (a′)

- **The step is what the actuary means by "this table changed".** In B1 (`RL-1538` item 1),
  the two pins of one slug are two steps' tables: the edited version and its seed origin. A
  re-edit moves one step's ref and leaves the seed step's alone. Pairing by step gives that
  step's cell diff and nothing for the seed, which is the evidence an approver needs.
- **The pairing already exists, twice.** FR-219's diff pairs steps by `step_id`
  (`_diff_steps`, `rating.py:896`), and FR-1399 already accounts a pin difference to the step
  whose ref names it (`03:196`: *"A pin difference (FR-237) that a derived step change accounts
  for, through that step's table, lookup or model reference, is part of that change, never a
  second one; a pin difference no step change accounts for is its own derived change"*). The
  draft and the Dislocation Run's derived changes then account the same version pair the same
  way, for the same approver.
- **It is what the authority asked for.** The 05:43:54 entry describes the fix as *"diff keyed
  by slug with an explicit pairing of versions"*. Each entry is still keyed by slug, and the
  pairing is explicit: the `step_id` on the entry, or the uniqueness of the ref.
- **Why the variant in pass 2.** (a) as drafted lists every pin no step references unpaired.
  At this tree that breaks a delivered behaviour: every rate-table pin in the route's test file
  is named by no step (`_minimal_algorithm` has no `table` step), and the E1 test
  (`test_rating_version_change_summary_route.py:150-204`) asserts a paired entry with a cell diff
  for exactly that shape. A rate table that only a mounted sub-graph's step reads is in the same
  position, because the draft never inlines (`:1377`). Pairing by slug is wrong only when a slug
  has two candidates on a side, which is FD-1679's case. Pass 2 keeps slug pairing exactly where
  it is unambiguous and lists every ref where it is not. So no ref is dropped and no pair is
  guessed.
- **Why the guard can go.** Every case below is answered by an entry that names each version.
  No residual case needs a refusal, so a refusal would only withhold correct evidence.

### Rejected

- **(b) set diff per slug** (`{old versions} → {new versions}`, a cell diff only when each side
  holds one). It is honest, but it gives no cell diff for the B1 shape, which is the case that
  needs one (PL-1677 :157 says so). A variant that cancels the versions common to both sides
  first gives B1 its diff but guesses on `{X@1, X@2} → {X@3, X@4}`, and it pairs by a property
  of the version numbers, not by anything the actuary authored.
- **(c) keep the refusal as the rule.** It leaves every B1 version without drafted evidence
  (PL-1677 :157), and the WF-699 E1 step (`examples/fremtpl2/journey.py:953-959`, `expect=200`)
  could not draft for one. It also keeps a 409 on input `RL-1538` makes valid.
- **Pairing through inlined sub-graph steps** (`<mount_point>__<step_id>`). It would need the
  draft to resolve every mounted fragment on both sides. The FR-219 diff in the same response
  does not (`:1377`), so the two halves of the draft would then pair different step sets. Pass 2
  already answers a sub-graph's tables correctly wherever a slug is unambiguous, and lists them
  where it is not.

## The cases — the observable behaviour

`X` and `Y` are rate-table slugs; `t`, `t_seed` and `u` are `table` step ids. "Main" is the
answer at `36e2610a`.

| # | Case | Baseline | Candidate | Entries after the fix (`step_id`, slug, from → to, diff) | Main |
|---|---|---|---|---|---|
| C1 | **two versions on one side only** (a version becomes B1) | `t`→X@1; pins `[X@1]` | `t`→X@2, `t_seed`→X@1; pins `[X@2, X@1]` | (`t`, X, 1 → 2, cell diff); (`t_seed`, X, — → 1, none) | 409 `VALIDATION_FAILED` (the guard) |
| C2 | **two versions on both sides** (B1 re-edited) | `t`→X@2, `t_seed`→X@1; pins `[X@2, X@1]` | `t`→X@3, `t_seed`→X@1; pins `[X@3, X@1]` | (`t`, X, 2 → 3, cell diff) only | 409 |
| C3a | **pins no step references**, one each side | pins `[X@1]` | pins `[X@2]` | (null, X, 1 → 2, cell diff), unchanged | 200, the same entry without `step_id` |
| C3b | the same, two on one side (SL-1678's Reds 1 and 2) | pins `[X@1]` | pins `[X@2, X@1]`, either order | (null, X, — → 2, none) | 409 |
| C3c | the same, on the baseline (SL-1678's Red 3) | pins `[X@1, X@2]` | pins `[X@2]` | (null, X, 1 → —, none) | 409 |
| C3d | the same, ambiguous | pins `[X@1, X@2]` | pins `[X@3]` | (null, X, 1 → —); (null, X, 2 → —); (null, X, — → 3); no diff | 409 |
| C3e | a stray pin beside a step's version of the same slug | `t`→X@1; pins `[X@1]` | `t`→X@2; pins `[X@2, X@5]` | (`t`, X, 1 → 2, cell diff); (null, X, — → 5, none) | 409 |
| C4a | **a slug renamed across versions**: no route renames a rate table (below), so it is a step re-pointed to another table | `t`→X@1; pins `[X@1]` | `t`→Y@1; pins `[Y@1]` | (`t`, X, 1 → —, none); (`t`, Y, — → 1, none) | 200, the same two entries without `step_id` |
| C4b | a **step** renamed, its table edited | `t`→X@1; pins `[X@1]` | `u`→X@2; pins `[X@2]` | (`t`, X, 1 → —, none); (`u`, X, — → 2, none) | 200, one entry X 1 → 2 with a cell diff |
| C5 | a first version | none approved | pins `[X@1, X@2]` | none; `baseline` null | 200, the same |

- **No rate-table rename exists at this tree.** `03` §5.1 has no `PATCH` or `PUT` row on
  `/api/v1/rate-tables`, and `grep -n '"/rate-tables[^"]*"' backend/src/app/api/*.py | grep -i
  'patch\|put\|rename'` prints nothing. A slug is a table's identity, so "renamed" can only mean
  a step now names another table (C4a). C4b is the step-id reading of the same words.
- **C4b loses a cell diff that main gives.** That is the cost of (a′), accepted: main's "X 1 → 2"
  there is a guess across two steps that FR-219 reports as removed and added. Under FD-1679 a
  guess is the defect. The approver still sees both versions and the structural lines
  "Step removed: t." and "Step added: u.", and can call the diff route.
- **The structural diff is unchanged** in every case. C4a's step also appears there as
  "Step t re-pointed from rate_table:X@1 to rate_table:Y@1." (`change_summary.py:67`).

## SL-1678's guard — removed by the fix slice

**Removed, with no residual case kept.** Every case above is answered (C1 to C5), so the fix
slice deletes `_pins_by_slug`'s refusal (`:1416-1424`) with the slug map itself, since pairing
no longer goes through a slug-keyed map. It also removes the docstring sentence at `:1336-1337`,
and strikes the `03` §5.1 clause (T2). SL-1678's three guard tests flip to C3b (both orders)
and C3c: same fixtures, new asserts. This is the planned flip, recorded in the fix slice's
`LG-`, as the FD-1660 re-cut's Stage B (#1299) does for its guard (see Interactions). The first-version test (C5)
stays as it is. After the fix, `git grep -n 'FD-1679' -- backend/src` prints nothing.

## DP-T — the texts

`<RL>` is this record's minted id, `<SL>` the fix slice's, and `<date>` the date the fix slice
writes them. Each is ruling text only. **This record makes no spec edit**
(`.claude/skills/spec-change`). The fix slice applies T1 and T2 and runs `audit-docs` once in
the gate-2 slot.

- **T1, appended to `03` FR-242's requirement cell (`:142`):**

  > *(Amended `<date>`, WK-673, `<RL>`, `FD-1679`.)* **How the draft pairs rate tables.** The
  > drafted summary has one entry per rate-table change. For each `step_id` that is a `table`
  > step in the baseline's algorithm or the version's, where its rate-table reference differs
  > between the two: if both references name the same rate table, one entry carries the
  > `step_id`, both references and their cell diff (FR-231). Otherwise each named table is its
  > own entry with the `step_id` and its one reference. Steps are paired by `step_id` only, as
  > FR-219 pairs them. A rate-table pin on one side only that no such entry names is an entry
  > without a `step_id`. Where a rate table has exactly one such pin removed and one added, they
  > are one entry with their cell diff; otherwise each pin is its own entry, without a cell diff.
  > Without the baseline's algorithm, every entry is of the second kind. Two versions of one rate
  > table pinned on either side are valid (`RL-1538`): every version is named, none is dropped,
  > and the draft is never refused for its pins.

- **T2, the `03` §5.1 `change-summary-draft` row (`:1052`).** Strike SL-1678's clause in place,
  from `**409** \`VALIDATION_FAILED\` when the version's pins` through `(**added 2026-10-12,
  SL-1678, FR-242**)`, with `~~…~~`. Append after it:

  > (**struck `<date>`, `<SL>`, `<RL>`, `FD-1679`:** the draft pairs rate tables through the
  > `table` step that names them, FR-242's `<date>` amendment, and is refused for no pin set.
  > Each rate-table entry carries a `step_id`, null for a pin no step entry names.)

- **T3, the shape** (code and the generated contract, not spec text). `RateTableChange`
  (`rating.py:1174`) gains `step_id: str | None = None`, with its docstring saying what null
  means. This extends `RL-1498` DP-E1-5's shape by one optional field. `from_ref` and `to_ref`
  keep their names, as DP-E1-5 requires. `RL-1498` otherwise stands, so this is not a
  supersession. `docs/contracts/openapi/generated.json` is regenerated
  (`generate-contracts.py`), never hand-edited. No frontend file reads the draft at this tree
  (`grep -rn 'change-summary-draft\|ChangeSummaryDraft\|RateTableChange' frontend/src` outside
  `generated` prints nothing). So the frontend change is the regenerated client only.

## Red tests — each red on `main` by its cause

The route tests go in `backend/tests/test_rating_version_change_summary_route.py` (module marker
`req("FR-242")`), through `GET …/change-summary-draft`. They need algorithms with `table` steps,
which the file's `_algorithm` does not build: the fix slice adds a fixture that does, from an
existing table-step fixture, without editing `_minimal_algorithm`. The unit tests go in
`backend/tests/test_change_summary_draft.py`.

| Test | Case | Asserts after the fix | Red on `36e2610a` by |
|---|---|---|---|
| R1 | C1 | 200; the two entries of C1, with `step_id` `t` and `t_seed`; `t`'s `diff` equals the diff route's answer for X@2 against X@1 | the guard: `409` `VALIDATION_FAILED`, detail naming FD-1679 |
| R2 | C2 | 200; exactly one entry, `t`, X 2 → 3, with the cell diff | the guard: `409` |
| R3 (flips SL-1678's three tests) | C3b both orders, C3c | 200; C3b one entry (null, — → X@2) and no diff; C3c one entry (null, X@1 → —) | the guard: `409` |
| R4 | C3d | 200; three entries, each with no diff | the guard: `409` |
| R5 | C3e | 200; (`t`, 1 → 2, diff) and (null, — → X@5) | the guard: `409` |
| R6 | C4b | 200; two entries, `t` and `u`, no diff | slug pairing: one entry `X 1 → 2` with a cell diff (`assert 1 == 2` on `len(rate_tables)`) |
| R7 | C4a | 200; both entries carry `step_id` `t` | the missing field: each entry has no `step_id` (`KeyError` or `None != "t"`). **Red only by the new field**: main's two entries are otherwise right |
| U1 | the text line | `_table_line` of an entry with `step_id="t"` reads `- X (step t): version 1 -> 2, …`; an entry without one reads as today | `RateTableChange(step_id=…)` raises a pydantic `ValidationError` (`extra="forbid"`) |
| U2 | the order | two entries of one slug, a step entry and a pin entry, given in reverse, come back step entry first | the same `ValidationError` (they cannot be built on main) |
| G1 (guard, not a red) | C3a | the E1 test at `:150-204` passes **unedited** | passes on main |
| G2 (guard, not a red) | C5 | the first-version test at `:498-515` passes unedited | passes on main |

**Broken-input proof:** in the fix slice, with pass 1 disabled locally (every difference sent to
pass 2), R1, R2, R5 and R6 fail, and G1 still passes; then restore it. A red that fails for
another reason (a fixture, 401, 404, a save refusal of the new algorithm) is not a red: fix the
test first.

## Interactions — the two neighbours and the demo

- **The sub-graph attribution ruling** (working id RL 9852, branch
  `rl-9852-pl9807-dps-2026-10-12` at `9035e6510d5f0bc8ec5bd7d60ef5e30dbeea0ec1`, to merge in D14,
  #1298), read at that commit, DP-1 to DP-T. **No contradiction.** It amends FR-1399 so that a
  mount is derived like a step by its `mount_point`, and a mount accounts for differences in the
  **sub-graph** pins. The draft reads only `pins.rate_tables` (PL-1677 DP-K (i)). A mount change
  is already in the draft's `structural_diff.sub_graph_mounts`, and it accounts for no rate-table
  pin in either ruling. This record's T1 applies FR-1399's pin clause to rate tables; RL 9852's T1
  extends the same clause to sub-graph pins. Both say "accounts for … through that reference",
  so the two read alike.
- **The FD-1660 re-cut, #1299** (branch `pl-9807-recut-2026-10-12` at
  `f5fe5412d9a485916325b2b7a25ff0589ec0a2bd`, a plan delta with Stage A and Stage B slice rows).
  **No shared code file and no shared `03` row.** Its write set (§"Write set" of the plan file on
  that branch) is `analysis.py`, `test_rating_attribution.py`, `test_quote_input_raise_sites.py`,
  `journey.py`, `test_wf699_journey.py`, the fremtpl2 README, its LGs, and `03` FR-264, §4.6,
  FR-1398 and FR-1399. It says *"Not written by either: `packages/model-schema/`;
  `docs/contracts/`; `frontend/`; `backend/src/`"*. The fix slice writes `backend/src/`,
  `packages/model-schema/`, `docs/contracts/` and `03` FR-242 and the §5.1 row. It does not write
  `journey.py`. Both edit `03`, on different rows: re-anchor by content at the second merge.
- **SL-1543 and WF-699 E1 (stated, not verified).** `SL-1543` (draft at this tree) puts a B1
  version into the demo (PL-1677 Context, entry 1). The journey's E1 calls the draft route with
  `expect=200` (`journey.py:953-959`). If the version E1 drafts pins two versions of one slug
  **and** has an approved baseline of its algorithm by then, the guard answers 409 and E1
  fails. Neither `PL-1542` nor SL-1543's roadmap row names FD-1679 or E1 (a grep for
  `FD-1679\|change-summary\|E1\b` over both prints nothing). This record did not run the journey
  or trace which version is E1's baseline. Sequencing the fix slice against SL-1543 is the
  lead's.

## What it obliges

- **The planner** cuts the fix slice as one dated Work-plan delta to `PL-1267` (Lean P2 L5), with
  this record as its decision. Its write set: `backend/src/app/platform/rating_versions.py`
  (`draft_change_summary_for` `:1329-1402`, `_pins_by_slug` deleted);
  `backend/src/app/platform/change_summary.py` (the pure pairing, per `RL-1498` DP-E1-4's
  placement, the sort and `_table_line`); `packages/model-schema/src/model_schema/rating.py`
  (`RateTableChange.step_id`); `docs/contracts/openapi/generated.json` (regenerated); the two test
  files; `03` (T1, T2); the slice's `LG-`. The executor binds `test-driven-development`,
  `python-test`, `spec-change`, `contract-schema`/`contract-guard` if the regenerated contract is
  guarded, `dev-commands` and `git-hygiene`.
- **The fix slice** applies T1 and T2 verbatim, shows R1 to R7 and U1 and U2 red by the causes
  above before the code, keeps G1 and G2 green unedited, and runs the broken-input proof.
- **FD-1679**: the fix slice's merge discharges its remaining limb, DP-P1. The finding closes
  then. Its register line is the lead's or the minter's, not this record's.
- **PL-1677** stays `active` until the fix slice's plan delta records DP-P1 as ruled here. It is
  not edited.

## Not decided here

- Whether the draft should later inline mounted sub-graphs to pair their tables by namespaced
  step. Refused for now (Rejected, last item). A change to it would be its own decision point.
- Sequencing against SL-1543 (Interactions): the lead's.
- The fix slice's id, size and position in the gate queue. PL-1677 :157 estimated about one
  executor-day for (a), including the contract change.

## Acceptance — the violation that must become detectable

The violation is a drafted summary that **drops a rate-table version** one side pins and the
other does not, or **pairs two versions that no step pairs while either is still pinned on the
other side**, or **refuses** a version for its pin set. After the fix, for every case above:

1. every ref in `pins.rate_tables` on one side only appears in an entry, and in an entry
   without a `step_id` only when no entry for a step names it (R1 to R6);
2. an entry with a cell diff and no `step_id` is formed only from the one removed and the one
   added ref of its slug (R3, R4, R5, G1);
3. the route answers 200 for any pin set on a version with an algorithm and pins (R1 to R5).

Each is a slice test, written red first in the fix slice. This record is ruling text and adds no
check of its own, so none is shown red here.

## Ruled

| DP | Ruled | By |
|---|---|---|
| DP-P1 | (a′): pair a rate table's versions through the `table` step that names them, by `step_id`; a pin difference no step entry names is paired by slug only when it is the one such ref on each side, else listed alone; no pin set refused; `RateTableChange` gains `step_id` | this record |
| The guard | removed by the fix slice, no residual case kept; SL-1678's three tests flip to C3b and C3c | this record |
| DP-T | T1 on FR-242, T2 on the §5.1 row, T3 the shape; ruling text only, no spec edit here | this record |
