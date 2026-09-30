---
id: RL-1344
family: ruling
title: PL-1254 DP-2 decided — FR-218's purpose mount is a sub-graph mount on the algorithm with a purposes selector, pinned by the Rating Version like any other
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 8cef871d4ec30869dc3ef20559f3cac64e239a5c
phase: P2
work: WK-1250
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1254, RL-1309, RL-1242, FR-212, FR-217, FR-218, FR-219, FR-239, FR-294, OQ-617]
---

# RL-1344 — PL-1254 DP-2 decided: FR-218's purpose mount is a sub-graph mount on the algorithm with a `purposes` selector, pinned by the Rating Version like any other

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-oq1334`. Its first command,
`echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"`, printed `CLAUDE_EFFORT=high`. This is the session's
second ruling. The first was `OQ-1334`, ruled as `RL-1343` (working id 9974). The maintainer ordered it in
`to-lead.md` (a local channel file outside the repository), in the entry headed "2026-09-30
22:33:30 BST — DECISIONS on your 23:05 (WK-1250 S1 blocked; lane re-order; ci-1018)",
Decision 2, which this session read itself: "**DP-2 is ruled now.** Add DP-2 to the
high-effort decision-maker session I asked you to schedule for OQ-1334: two rulings … When
DP-2's RL mints, PL-1254 goes `active` (a status flip), and WK-1250 S1 can dispatch." The
lead's brief addendum, headed "2026-09-30 22:37:11 BST", assigned the working id.

**Minted 2026-09-30 as RL-1344** (`python3 scripts/doc-id.py next --ref 71b672205f7212008d0ff00b5cbc4810b56f12e6`
printed `1342`. The WK-674 Slice 3 leaf plan, filed as PL 9947, takes it as PL-1342, OQ-1334's
ruling takes RL-1343, and the lead allocated 1344 to this record in the mint GO.) It was filed
under working id 9976, hand-assigned by the lead, who is the only allocator (FD-1338).

**The decision point**, verbatim from `PL-1254`'s decision-point table
(`docs/plans/PL-01254-wk-1250-sub-graph-composition-and-mta-cancellation-pricing-map-plan.md:211`):
"Where is FR-218's purpose mount declared, given FR-218's 'declared on the Rating Version and
version-pinned like any other sub-graph'?" It has three options:
- (a) on the algorithm, where `SubGraphRef` gains an optional `purposes` selector and the
  Rating Version's `pins` pin the exact sub-graph version;
- (b) on the Rating Version, as a separate `purpose_mounts` field outside the algorithm;
- (c) both, with (b) overriding (a).

The planner's recommendation is (a). The row marks it blocking for Slice 2 ("its pin and shape
land in Slice 2's spec change") and for Slice 3. `RL-1309` ruled DP-1, DP-3 and DP-4, and its
line 39 says "**DP-2 is not ruled here.**" The plan is frozen, and this record does not edit
it.

## Verified first, at 8cef871d4ec30869dc3ef20559f3cac64e239a5c

`RL-1309` read these at `7c354305`. Each one used below was re-read at `8cef871d`.

| Claim | At `8cef871d` |
|---|---|
| `SubGraphRef` | `packages/model-schema/src/model_schema/rating.py:340-350`: `ref: ArtifactRef` and `mount_point: str`, `extra="forbid"`. |
| An `ArtifactRef` always names a version | `refs.py:37-38`: `^(?P<type>[a-z_]+):(?P<slug>…)@(?P<version>[1-9][0-9]*)$`. So a mount names an exact sub-graph version, just as a `table` step names an exact rate table version (`RatingTableStep.rate_table_ref`, `rating.py:283-285`). |
| The algorithm holds its mounts | `RatingAlgorithm.sub_graphs: list[SubGraphRef]` (`rating.py:390`). |
| A Rating Version has no sub-graph pin | `Pins` (`rating.py:63-77`) has `rate_tables`, `models`, `reference_tables` and `custom_objectives`. `PL-1254` Task 2 adds `sub_graphs`. |
| The interim guard | `_check_purpose_mount` (`packages/pricing-core/src/pricing_core/rating/score.py:393-420`) refuses every `mid_term_adjustment` and `cancellation` quote. `RL-1242` rules this. |
| `purpose` | `QuotePurpose = Literal["new_business", "renewal", "mid_term_adjustment", "cancellation", "what_if"]` (`packages/model-schema/src/model_schema/scoring.py:44`). |
| One bundle per Rating Version | FR-239 (`03:136`): "A Rating Version compiles to a self-contained **Bundle** with a content hash." |
| How a Rating Version names its parts | `03` §4.3 (`03:345-358`): `algorithm_ref` is an exact algorithm version (`rating_algorithm:motor-gb@14`), plus `pins`. |
| The GIPP check re-scores by purpose | `04` FR-294 (`docs/specs/04-optimisation.md:110`): ENBP "is obtained by re-scoring with `purpose = new_business`". FR-297 (`:113`): the verdict passes when "no renewing customer's price exceeds their ENBP". |

**Already ruled, and binding here** (`RL-1309`, read in full at the sections cited):
- **DP-3** (a). A mount is a node in the parent's DAG. Its port map ties the fragment's input
  and output ports to parent names. Every name internal to the fragment is namespaced by
  `mount_point`, and FR-212's save-time invariants count the mount as a node: its mapped
  outputs are produced by it, and its mapped inputs are consumed by it. The port map lands on
  `SubGraphRef` in Slice 2.
- **DP-1 guard G1** (item 6(i)). "`compile_bundle` refuses a `SubGraphRef` whose version is
  not in the Rating Version's `Pins.sub_graphs`, and never inlines it."
- **DP-1 item 2.** FR-219's structural diff lists "each sub-graph mount or pin added, removed or
  re-pointed", and it is computed in Slice 2.

## Ruled

### 1. Option (a): the purpose mount is an ordinary sub-graph mount, on the algorithm

**A purpose mount is a `SubGraphRef` in the algorithm's `sub_graphs`, with one more field: an
optional `purposes` selector. Its exact version is pinned in the Rating Version's
`Pins.sub_graphs`, like every other mount (G1). There is no second declaration site, and no
purpose-specific pin list.**

**Why (a)**, beyond the planner's reading of "like any other sub-graph":
1. **DP-3 decides the site.** A mount's port map names values inside the parent's DAG. FR-212
   checks that DAG at algorithm save, with the mount counted as a node. Under (b), the node
   would live on the Rating Version, and the names it produces and consumes would live in the
   algorithm. Then neither artifact could be validated alone. An algorithm step that consumes a
   value only a purpose mount produces would be refused at save as unresolved. The other way
   to avoid that is for algorithm save to accept names that some future Rating Version might
   supply, and that cannot be checked. (a) keeps the whole DAG in one artifact, where FR-212
   already checks it.
2. **FR-218's "declared on the Rating Version" holds under (a).** A Rating Version is an exact
   `algorithm_ref` plus exact `pins` (`03` §4.3). Everything its pinned algorithm version
   declares is declared by that Rating Version, because the version names one exact algorithm.
   "Which refund rules were in force for this cancellation" is then answered by the pin, as
   FR-218 asks. The dated clause below says this in FR-218 itself, so that a reader does not
   take the words to mean (b).
3. **(b) creates a second path, and (c) states one fact twice.** Under (b), a purpose mount would
   need its own pin, its own diff limb, its own compile resolution and its own trace
   attribution beside the ordinary mount's. (c) adds a precedence rule between two places that
   hold the same fact.

**The cost of (a), accepted.** Changing the refund rules to a new sub-graph version changes the
algorithm version as well as the pins, because the mount names the exact version. A rate table
works the same way today (`RatingTableStep.rate_table_ref` is exact). So this is the existing
rule and not a new cost. The change reaches approval through the new Rating Version's
structural diff (DP-1 item 2).

### 2. The `purposes` selector

1. **Absent means always mounted.** Every existing mount, such as `03` §4.1's
   `sub_graph:ncd-ladder@4`, keeps its meaning, and no stored algorithm changes.
2. **When present, it is a non-empty list with no duplicates.** It admits only
   **`mid_term_adjustment` and `cancellation`**. Any other value, an empty list or a duplicate
   is refused at algorithm save with `VALIDATION_FAILED`. That is the code `RL-1309` DP-S1-3
   uses for a shape refusal. It is also what a `RequestValidationError` already maps to
   (`backend/src/app/errors.py:454-475`), so a model-level refusal needs no new code.
3. **Why only those two.** FR-218 names exactly these ("mounted only when `purpose ∈
   {mid_term_adjustment, cancellation}`"), and it prices every purpose by one risk price. If
   the selector admitted `new_business` or `renewal`, a mounted fragment could price a renewal
   differently from the equivalent new-business quote inside one algorithm. That is the
   difference the GIPP check measures: `04` FR-294 derives ENBP by re-scoring with
   `purpose = new_business`, and FR-297 fails a renewal priced above it. No requirement asks
   for that lever, so the shape does not offer it. `what_if` is a sandbox purpose, and it is
   refused for the same reason. Widening the set is a spec change to FR-218.
4. **The selector is part of the algorithm.** So it is covered by the algorithm's version, by
   the bundle's content hash through `algorithm_ref` (FR-239), and by FR-219's structural diff.
   A change to a mount's `purposes` appears in that diff as a mount change.

### 3. What the shape implies for scoring, and what it leaves open

- **FR-218's refusal is judged from the bundle.** A `mid_term_adjustment` or `cancellation`
  quote is refused with `INPUT_CONTRACT_VIOLATION` unless the bundle inlines at least one mount
  whose `purposes` includes that purpose. This is `RL-1242`'s "real check" (the sub-graph "this
  purpose needs is inlined in the bundle"). Slice 3 builds it in `_check_purpose_mount`.
- **One bundle per Rating Version, as today (FR-239).** It inlines every pinned mount, purpose
  mounts included. A purpose mount contributes to a quote only when the quote's `purpose` is in
  its `purposes`. Other purposes are priced without it: the base graph, with one risk price.
- **FR-212 is checked for each purpose's graph.** The algorithm must satisfy FR-212's
  invariants in three forms: as mounted for any purpose outside the selector's set (every
  unconditional mount), as mounted for `mid_term_adjustment`, and as mounted for
  `cancellation`. So a name that only a purpose mount produces cannot be consumed by a step
  that runs for every purpose.
- **Left open, for Slice 3's leaf plan to raise as its own decision point:** how a purpose
  mount's outputs reach the ladder and the payable (for example, whether a cancellation's
  refund is a new declared output, a ladder rung, or something else), and how the inlined
  nodes are gated by `purpose` at evaluation. This ruling fixes only where the mount is
  declared and pinned, and the invariants above. Either answer must fit inside them.

### 4. Which slice carries what

- **Slice 2** builds the general pin (`Pins.sub_graphs`, G1) and the inliner. Purpose mounts use
  both unchanged. It adds **no** `purposes` field. Until Slice 3, `SubGraphRef` stays
  `extra="forbid"` without the field, so a stored algorithm cannot carry a selector that
  nothing honours. Every mount that Slice 2 inlines is unconditional. `RL-1242`'s interim
  refusal stays in force through Slice 2.
  - **A consequence to state in Slice 2's leaf plan:** in that window, an author who mounts a
    refund fragment without a selector mounts it for every purpose. Nothing but review stops
    that, just as nothing stops a wrongly wired step. The change shows in the Rating Version's
    regression suite and dislocation run (`RL-1309` DP-1 item 2), and every MTA and
    cancellation quote is still refused.
- **Slice 3** adds `SubGraphRef.purposes`, with §2's rules and a red-first case for each
  refused form. It regenerates the contracts, applies FR-212 per purpose (§3), and builds the
  real check. It then strikes `RL-1242`'s interim clause in FR-218 and retires `RL-1242`, as
  `PL-1254` Task 3 already says.
- **So DP-2 does not block Slice 2's shape.** Slice 2 needs to know only that no purpose-specific
  pin exists, and this ruling settles that. The dispatch record for Slice 2 carries this record.

## What it obliges

- **This commit:** `03` FR-218 gains a dated clause with §1 and §2's rules. No other spec is
  edited here, and neither is any plan, contract or roadmap row.
- **WK-1250 Slice 2's dispatch record** carries §4's Slice 2 bullet. The inliner must not
  foreclose §3's per-purpose gating: a mount is inlined as a namespaced unit (DP-3), so Slice 3
  can gate it as one unit.
- **WK-1250 Slice 3's dispatch record** carries §2, §3 and §4's Slice 3 bullet, and the open
  question in §3, to be raised as a decision point in its leaf plan before the slice starts.
- **`PL-1254`'s activation.** With this record minted, DP-2 has a resolver. The maintainer's
  22:33:30 BST entry says PL-1254 then goes `active`.

## Acceptance — the violation that must become detectable

In Slice 3, each case is red first:
1. An algorithm with `purposes: ["renewal"]`, `["what_if"]`, `[]` or
   `["cancellation", "cancellation"]` is refused at save with `VALIDATION_FAILED`.
2. A version whose only purpose mount selects `cancellation` refuses a `mid_term_adjustment`
   quote with `INPUT_CONTRACT_VIOLATION`, and prices a `new_business` quote exactly as the same
   version with that mount removed would.
3. A purpose mount whose version is not in `Pins.sub_graphs` is refused at compile. This is G1,
   the same test as for any mount.
4. An algorithm in which a step outside the purpose mount consumes a name that only the mount
   produces is refused at save.
5. A change to a mount's `purposes` alone appears in FR-219's structural diff and changes the
   bundle's content hash.

## Observed, not ruled (for the lead)

- **FR-218's text still names the Rating Version as the declaration site.** The dated clause
  added by this commit reconciles it. Until Slice 3 lands, the requirement's working rule is
  `RL-1242`'s interim refusal. This ruling does not change that.
- **`PL-1254`:211 marks DP-2 blocking for Slice 2.** Under this ruling, Slice 2 is blocked only
  until this record mints, because §4 gives it nothing to build for purposes.
