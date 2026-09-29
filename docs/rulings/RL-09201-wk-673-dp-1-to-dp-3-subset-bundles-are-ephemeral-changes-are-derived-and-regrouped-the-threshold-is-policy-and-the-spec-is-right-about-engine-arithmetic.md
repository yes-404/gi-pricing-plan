---
id: RL-9201
family: ruling
title: WK-673 DP-1 to DP-3 — subset bundles are ephemeral, changes are derived and regrouped, the threshold is policy, and the spec is right about engine arithmetic
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-28
owner: decision-maker
tree: ed123cb0fcf91e44872963bf8a8bad32b87c99bc
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-881, RL-885, RL-1172]
---

# RL-9201 — WK-673 DP-1 to DP-3: subset bundles are ephemeral, changes are derived and regrouped, the threshold is policy, and the spec is right about engine arithmetic

## Verified first, at ed123cb0fcf91e44872963bf8a8bad32b87c99bc

**This record decides nothing.** It files decisions the deputy made by delegation from the
maintainer (28 Sep, extended goal). They are in the deputy's entry on WK-673's DP-1 to DP-3,
written at 14:05:30 BST and relayed by the lead. The entry is quoted whole under Ruled, in a
fenced block, and this record names the slice each decision obliges. The entry itself asks
for this record, to be filed in Slice 1's PR or before it.

**The plan these rule on** is WK-673's map plan, a draft on PR #844 at
`af3f0518` (`status: draft`, `tree: 6c6f4532…`). It is not on `main`, so this record names
it by PR rather than by id: an id that does not resolve fails `audit-docs.py` check 32, and
this record merges first. The entry under Ruled quotes the id inside its fence, whole.
Its Decision points table is at `:228-239` there. It states that DP-1, DP-2 and DP-3 are the maintainer's,
resolved by the deputy, and that DP-4 is slice design, the planner's own and decided in the
plan. **DP-4 is therefore not ruled here.** The plan cites this record once both are minted
(the lead calls the turns; this record mints first).

This record was drafted in the decision-maker's worktree, on branch `p2-wk673-rl`, cut from
`origin/main` = `ed123cb0` with a clean root. Clock at drafting: 2026-09-28 14:06:22 BST,
read by `TZ=Europe/London date`. **Its id, RL-9201, is a working id.** It is minted with
`doc-id.py next --ref origin/main` at its turn, and renumbered in one commit if it differs.

**Re-read at `ed123cb0`, the facts the entry rests on:**

- `docs/specs/03-rating-engine.md:206` reads *"**Inside the engine, arithmetic is exact.**
  `0.1 + 0.2 == 0.3` evaluates `true`"*.
- `docs/specs/03-rating-engine.md:209-210` reads *"**At the Python binding, there is no
  decimal type at all.** A Python `Decimal` is *rejected* (`TypeError: unsupported type
  Decimal`), and every value returned is a Python `float`"*.
- `packages/pricing-core/src/pricing_core/rating/score.py:527-531` is `_round_minor`'s
  docstring. Lines 529–530 read *"which is what the engine's float64 arithmetic actually
  meant to produce"*.
- `docs/specs/03-rating-engine.md:945` is NFR-493: *"Batch scoring ≥ 1 M risks/hour per
  worker (NFR-455), linear in workers."*
- `docs/specs/03-rating-engine.md:154` is FR-248: each ladder rung records its value and
  operation, *"so the ladder reconciles exactly"*.

All five are as the entry quotes them.

## Ruled

The deputy's entry, **whole and verbatim**. It is fenced so that the ids it quotes are read as
quotation, not as citations; `audit-docs.py` check 32 skips fenced blocks. The deputy accepted
this form for #832.

```text
## 2026-09-28 14:05:30 BST · deputy · WK-673 (PL-9101, #844): DP-1, DP-2 and DP-3 DECIDED; the §3.11-vs-code disagreement RESOLVED (the spec is right; the code docstring is corrected); the Shapley cost gets a feasibility rule

Given by the maintainer's delegation (28 Sep, extended goal). A decision-maker files these as `RL-` records quoting this entry, in S1's PR or before it, since DP-1 and DP-2 block S1. Read at `ed123cb0`.

**DP-1 (how the 2^K subset bundles are built): (a) ACCEPTED, with conditions.** Synthetic bundles are compiled through `compile_bundle` at step granularity, and they are:
- **ephemeral and content-addressed, and never persisted as Rating Versions:** no `VR-` identifier, never approvable, never deployable, never visible in any version list;
- cached per run by content hash, and discarded with the run's scratch;
- surfaced by name if one fails to compile (a subset that cannot compile fails the run with the subset named; it is never silently skipped);
- stated in the run artifact, which records that K + … subset bundles were compiled, with their hashes.

**DP-2 (where a "declared change" comes from): (c) ACCEPTED.** Changes are derived from the structural diff between baseline and candidate. The analyst may regroup them into ≤ 6 groups, and the **server verifies that the groups partition the diff exactly** (no change missing, none duplicated) and refuses otherwise, by name. The derived and regrouped lists are both on the artifact.

**DP-3 (where FR-224's threshold lives): (b) ACCEPTED.** It is the `rating_version` ApprovalPolicy entry: versioned, its every change audited (`06`'s governance path), with **no environment-variable override** (FR-446's mechanism is not applied to it). S5 cites this.

**The disagreement (CLAUDE.md §0), RESOLVED: the spec is right, and the code's docstring is corrected.**
- `03` §3.11 (`03:206–211` at `ed123cb0`) records spike S1's measurement: *"Inside the engine, arithmetic is exact. `0.1 + 0.2 == 0.3` evaluates `true`"* (impossible in float64), and *"At the Python binding … every value returned is a Python `float`"*.
- `_round_minor`'s docstring (`score.py:527–531`) says *"the engine's float64 arithmetic"*. The float64 is the **binding's** return type, not the engine's arithmetic. The rounding function itself is right, and only its sentence is wrong.
- **S1 corrects that docstring sentence** (spec and code in one commit, CLAUDE.md §2) to *"the binding's float64 return values (the engine's own arithmetic is exact, `03` §3.11)"*. No behaviour changes.
- My 13:57:02 F3 correction already reads "float64 **at its boundary**", which is consistent. It stands.

**The Shapley cost: a feasibility rule, amending my F3 decision's item 5 (dated):**
1. **S3 measures first.** The real `score_batch` rate on freMTPL2, N = 5, load < 12. The 43.4M-rating / ~43 worker-hour figure uses NFR-493's **floor** (≥ 1M risks/hour/worker, `03:945`), not a measurement.
2. **S3 evaluates ladder replay as the primary route.** `03` FR-248 requires each ladder rung to record its value and operation so that *"the ladder reconciles exactly"*. Where the declared changes are **step-aligned** (each change replaces steps' inputs, and the step graph is shared), v(S) for each subset is computed by replaying the ladder with each rung taken from baseline or candidate according to S. That is **2 ratings per policy plus integer arithmetic**, not 2^K.
   - **Exactness is proven, not assumed:** replay must equal a true re-rate for every policy on the full portfolio at K ≤ 3, and on a declared verification sample at K = 4–6. Any mismatch falls the run back to re-rates, recorded on the artifact.
   - Structural changes (steps added or removed) are not step-aligned and use re-rates.
3. **Where re-rates are needed:** the run computes and **shows its estimated rating count (2^K × policies) before launch**, and runs as a background Job. **A sampled portfolio is never presented as exact Shapley.** If sampling is ever offered, it is a separately named estimate with its interval, and that is a spec change, not a default.
4. **S3 proposes the dislocation-attribution NFR from the measurement.** If neither replay nor re-rates at K = 4 fit it, S3 brings the figure to me before building any fallback, as item 5 already requires.
5. Exact Shapley over declared changes (K ≤ 6) and largest-remainder allocation **stand** as the method of record.

**The other premises are noted for S1**, which amends them: the contract's `job_id` / `by_ladder_rung` / `errors` missing from §4.6; `attribute`'s §5.2 signature having no baseline; RL-881's stale "06 §4.2 omits rating_version". S6's split (floor wiring after WK-672 S3) is sound slice design. **I accept PL-9101 as WK-673's map plan** once the RL records these DPs and the plan cites it. The acceptance line follows your request.
```

What the entry decides, in this record's own words:

- **DP-1: (a), with conditions.** Subset bundles are compiled through `compile_bundle` at step
  granularity. They are ephemeral and content-addressed, never a Rating Version, never
  approvable, deployable or listed. A subset that fails to compile fails the run by name.
  The run artifact records the bundles compiled and their hashes.
- **DP-2: (c).** Changes are derived from the structural diff. The analyst may regroup them
  into at most 6 groups, and the server checks the groups partition the diff exactly,
  refusing by name otherwise.
- **DP-3: (b).** FR-224's threshold is on the `rating_version` `ApprovalPolicy` entry, with no
  environment-variable override.
- **The disagreement (`CLAUDE.md` §0): the spec is right.** The float64 is the binding's return
  type, not the engine's arithmetic. Slice 1 corrects `_round_minor`'s docstring sentence to the
  entry's wording, with no behaviour change.
- **The Shapley cost: a feasibility rule,** amending item 5 of the deputy's F3 decision, as
  the entry's items 1–5 state it.
- **The plan's other premises** are noted for Slice 1, which amends them.

## What it obliges

The slice numbers are those of WK-673's map plan (PR #844).

- **Slice 1 (spec, contract, types)**, blocked until this record merges:
  - DP-1's conditions become spec text. That covers the ephemeral, content-addressed
    subset bundle; the absent `VR-` identifier; no approval, no deployment and no version
    listing; a compile failure that names the subset; and the compiled-count and hashes on
    the run artifact.
  - DP-2's partition rule becomes spec text: changes derived from the structural diff,
    regrouped into at most 6 groups, the server checking the groups partition the diff
    exactly and refusing by name, and both lists on the artifact.
  - The `_round_minor` docstring sentence is corrected, in one commit with any spec text it
    touches, to the deputy's wording. Behaviour does not change.
  - The noted premises are amended: `job_id`, `by_ladder_rung` and `errors` in `03` §4.6's
    contract, and a baseline in `attribute`'s §5.2 signature.
  - RL-881's stale clause saying `06` §4.2 omits `rating_version` is superseded. `06` §4.2
    now lists `rating_version` (RL-885).
- **Slice 3 (attribution)** takes the cost rule:
  - measure the real `score_batch` rate first (N = 5, load < 12);
  - evaluate ladder replay as the primary route, proven equal to a full re-rate on the whole
    portfolio at K ≤ 3 and on a declared sample at K = 4–6, falling back to re-rates on any
    mismatch;
  - show the estimated rating count before launch, and never present a sample as exact
    Shapley;
  - propose the dislocation-attribution NFR from the measurement, and bring the figure to
    the deputy before any fallback if K = 4 does not fit.
- **Slice 5 (the approval gate, part one)** cites DP-3. FR-224's threshold is a field on
  the `rating_version` `ApprovalPolicy` entry (`06` §4.2), with no environment-variable
  override, so FR-446's resolution order does not apply to it.
- **WK-673's map plan (PR #844)** cites this record by its minted id. The deputy accepts it as WK-673's map
  plan once it does, and the acceptance line follows the lead's request.
- **Not ruled here:** DP-4 (the planner's slice design, decided in the plan) and the F3
  decision itself. Item 5 is amended above, and the method of record stands.

## Acceptance — the violation that must become detectable

The violation: **a subset bundle that escapes its run, or a regrouping that drops or
double-counts a change.** Both are checks for the slice that builds them. This record builds
nothing, so no check can be proven red here, and it forces none. Slice 1's leaf plan names
one negative test for each of the following, each shown red on deliberately broken input:

- *Violation: a subset bundle persisted as a Rating Version, or visible in a version list.*
- *Violation: a subset that fails to compile and is skipped instead of failing the run by
  name.*
- *Violation: a regrouping that leaves a derived change out, or puts one in two groups, and
  is accepted.*
- *Violation: FR-224's threshold resolved from an environment variable.* This one is Slice
  5's.

Slice 3's leaf plan names the replay-exactness check: *Violation: a replayed v(S) that
differs from a true re-rate for some policy, and is not recorded as falling back.*

## Adopted by the decision-maker, 2026-09-29

**Why this section exists.** This record files the deputy's delegated decisions of
2026-09-28 14:05:30 BST. They are technical decision points. The maintainer's entry `2026-09-29 15:26:00 BST · maintainer (acting on the maintainer's behalf) · STRUCTURE: routing per document-ids §1.6 and the charters; today's technical answers re-homed`
(§2) re-homes such points to this role, so each is re-verified here at origin/main `ac8ab519`,
with the mechanism it builds on named by file and line. The body above stays as of `ed123cb0`.

| Point | Re-verified at `ac8ab519` | Ruling |
|---|---|---|
| **DP-1 (a)**: subset bundles compiled through `compile_bundle` at step granularity, ephemeral and content-addressed, never a Rating Version | `compile_bundle` is `packages/pricing-core/src/pricing_core/rating/compile.py:425` (`async def compile_bundle(version: RatingVersion, resolver: ArtifactResolver) -> Bundle`). A bundle carries its content hash (`RL-921`, read in `api/score.py`'s docstring at `:168`) | **Adopted as filed.** One wording point for Slice 1's spec text: the entry says "no `VR-` identifier", but `VR-` is `01`'s validation-rule identifier (`01-data-management.md`, `VR-AC…` and similar). The condition means *no Rating Version identity*: never a `rating_version` row, never approvable, deployable or listed. The spec text should say that |
| **DP-2 (c)**: changes derived from the structural diff, regrouped into at most 6 groups, the server checking the partition | The structural diff exists: `diff_algorithms(old, new) -> AlgorithmDiff` at `packages/model-schema/src/model_schema/rating.py:569` (`AlgorithmDiff` at `:539`). `structural_diff` is the first evidence kind of the `rating_version` floor (`approvals.py:106`) | **Adopted as filed** |
| **DP-3 (b)**: FR-224's threshold on the `rating_version` `ApprovalPolicy` entry, with no environment-variable override | The entry exists: `06` §4.2's default policy and `packages/model-schema/src/model_schema/approvals.py:322`. **The field does not:** `ApprovalPolicyEntry` (`approvals.py:111-122`) has `artifact_type`, `approvers_required`, `approver_roles`, `environment` and `evidence`, and no threshold. FR-224 (`03:110`) says only *"a workspace-declared premium-deviation threshold"* | **Adopted, with a premise note:** the ruling is about where the threshold lives, and the object it lives on exists. The field is new, a `model-schema` shape change (ADR-704, generated to `docs/contracts/`) that Slice 5 makes with the gate it serves. An approval policy is not a Setting, so FR-446's environment-variable layer (`07:172`) does not reach it. "No override" therefore holds by construction, and Slice 5's negative test proves it |
| **The §0 disagreement**: the spec is right, and `_round_minor`'s docstring is corrected | `03` §3.11 still reads *"Inside the engine, arithmetic is exact"* (`03:208`) and *"At the Python binding, there is no decimal type at all"* (`03:211`). The docstring still says *"the engine's float64 arithmetic"* (`packages/pricing-core/src/pricing_core/rating/score.py:532`), not yet corrected | **Adopted.** The correction is a code edit, and it is Slice 1's |
| **The Shapley feasibility rule** (items 1–5) | FR-248 (`03:155`) requires each rung to record its value and operation. NFR-493 (`03:1148`) is the ≥ 1 M risks/hour floor. `score_batch` is `score.py:1004` | **Adopted as filed.** Item 4's "bring the figure to the deputy" now reads: bring it to this role. A changed attribution NFR is a spec change, which this role rules, and the maintainer accepts it if it relaxes a target a Work closes against (`RL-1232`, Q848-3's reading) |

**Spec changes this record obliges, and why none lands in this commit.** Each belongs to a
slice of WK-673's map plan (PR #844), because each is spec text for a shape or behaviour that
the same slice builds. `CLAUDE.md` §2 puts spec, code and tests for one change in one commit.
- DP-1's and DP-2's conditions, and the `03` §4.6 contract fields (`job_id`,
  `by_ladder_rung`, `errors`) and §5.2's `attribute` baseline, describe the Dislocation Run
  artifact and its signature. The artifact's shape is generated from `model-schema` into
  `docs/contracts/`. Writing §4.6 before the shape changes would make the spec and the
  generated contract disagree, so they are Slice 1's.
- DP-3's threshold field is Slice 5's, as above.
- `RL-881`'s stale clause (that `06` §4.2's floor restatement omits `rating_version`; `RL-881`
  at `:156`) is a ruling record, so it is this role's, not a slice's. It is not superseded
  yet: `RL-881` reads `superseded_by: ~` and `corrected_by: []`. **Proposed for the lead:**
  this role files it when #844's Slice 1 lands, citing `RL-885`, or now as its own small
  record, whichever the lead prefers. It changes no behaviour.

