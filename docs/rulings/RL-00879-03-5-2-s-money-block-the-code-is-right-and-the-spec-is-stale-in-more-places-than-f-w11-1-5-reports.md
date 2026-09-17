---
id: RL-879
family: ruling
title: `03` §5.2's money block: the code is right and the spec is stale, in more places than `F-W11-1-5` reports
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slice1-rulings.md
---

## RL-879 — `03` §5.2's money block: the code is right and the spec is stale, in more places than `F-W11-1-5` reports

**Raised as `F-W11-1-5`** in the Slice 1 plan (`2026-08-29-w11-1-evaluator-core.md`, PR #370),
which routed it here correctly: *"it is a spec-vs-code conflict, which `delivery-process.md`
§3 makes theirs."* It is `CLAUDE.md` §0's question — which of spec and code is wrong — and
this record answers it.

**The finding as reported understates its own scope.** `F-W11-1-5` says *"Both the module
path and the third parameter's name differ."* Checked against `002f4d8`, the table below is
the finding; **it carries no total, deliberately** — see the correction beneath it. Every row
marked *no* in the last column is a divergence the report does not mention:

| # | Spec, `../specs/03-rating-engine.md` §5.2 | Shipped code | Reported? |
|---|---|---|---|
| 1 | module `pricing_core/rating/money.py` (`:619`) | `packages/pricing-core/src/pricing_core/money.py`; **no `rating/money.py` exists** | yes |
| 2 | `apply_factor(..., rounding: Rounding)` (`:621`) | `apply_factor(..., mode: RoundingMode)` (`money.py:33`) | the name, yes |
| 3 | the type `Rounding` | `RoundingMode = Literal["half_even", "half_up", "ceiling", "floor", "down"]` (`money.py:20`); **`Rounding` exists nowhere in the codebase** | **no** |
| 4 | declares `to_minor` here (`:620`) | `to_minor` is not in `pricing-core` at all — it is `model_schema/money.py:105`, a different package | **no** |
| 5 | `to_minor(value: Decimal, currency: str) -> int` (`:620`) | `to_minor(value: Decimal, *, places: int = 2) -> int` — keyword-only `places`, not positional `currency` | **no** |
| 6 | does **not** declare `reconcile_ladder` | `reconcile_ladder(risk_premium_minor: int, steps: list[tuple[str, int]]) -> bool` ships (`money.py:55`) and is re-exported | **no** |

**Corrected twice before merge, and the second correction removed the number rather than
fixing it a third time.** The first filing said *"four"*: rows 4–6 were bundled into one row
while rows 1–3 each held one defect, so the total under-reported at the table's own
granularity — the same defect this ruling opens by naming in `F-W11-1-5`, committed in the
act of naming it. Splitting the row gave *"six"*. The planner then made the argument that
settles it: **six is right only at this table's granularity, and that granularity is a choice
rather than a fact** — rows 5 and 6 could themselves be split or merged, and a reader
quoting "six" would be quoting how the table was drawn, not what the repository contains.

**So the total is gone, not corrected**, following this suite's own precedent for exactly
this situation: `2026-08-29-w11-scoring.md:570-571` — *"every bare count in this section is
removed rather than corrected a third time, replaced by the enumerated list above"* — and
`:93`, where prerequisites are *"named individually, because … a bare count of them is not
load-bearing anywhere in this document."* Nothing was ever missing from the text; only the
number moved. **The list is the artifact; the total was the liability**, and this is the
fourth instance in this area, which is what makes it a convention rather than a preference.

Rows 4–6 point in opposite directions: two are a declared function that is in a different
*package* with a different *signature*, and one is an undeclared function that ships. Row 6
matters for this slice — `reconcile_ladder` is what `NFR-496`'s ladder-reconciliation test
exercises, and Task 1.4's Step 12 is that test, so the plan depends on a function §5.2 does
not list.

**Ruled: the code is right; §5.2 is stale.** Grounds:

- **`pricing_core.money` is public surface, not an internal path.**
  `packages/pricing-core/src/pricing_core/__init__.py:13` re-exports
  `ROUNDING_MODES, RoundingMode, apply_factor, reconcile_ladder` from it. Moving the module
  to match the spec would break `pricing-core`'s published API for a naming preference,
  which is the tail wagging the dog.
- **The parameter name is deliberate and requirement-grounded**, not incidental.
  `money.py:36-37`: *"`mode` has no default. FR-226 requires rounding to be declared per
  step; a default here would silently satisfy the type checker while defeating the
  requirement."* A spec correction costs nothing; a rename to `rounding` would gain nothing
  and lose that reasoning's anchor.
- **`Rounding` never existed.** This is not a rename that drifted — the spec names a type the
  repository has never had, so there is no code side to prefer.

**Disposition — applied to `../specs/03-rating-engine.md` §5.2 in this commit**, following
the correction convention that block already uses (`bundle_hash` carries *"corrected
2026-08-27 (F-W9-3-2)"*, `compile_bundle` was corrected to `async def` by RL-866):

- the module comment becomes `pricing_core/money.py`;
- `apply_factor`'s third parameter becomes `mode: RoundingMode`;
- `reconcile_ladder` is added, because it ships and `NFR-496` depends on it;
- `to_minor`'s line is replaced by a pointer comment naming where it actually lives.

**Deliberately not decided here, and flagged rather than folded in: which spec should declare
`model_schema.money.to_minor`.** It is declared in exactly one place in the whole suite today
— `03` §5.2, wrongly — and removing it from there without a home elsewhere loses the reader's
path, which is why a pointer comment replaces it rather than a deletion. But `to_minor` is
`model-schema`'s, so its §5.2 home is `00`'s or `02`'s surface, not `03`'s, and choosing
between them is a different module's interface question rather than this conflict's
resolution. Queued below.

**`F-W11-1-5`'s "not a blocker" assessment is confirmed**, and it was the planner's to make
rather than mine to accept on trust: Task 1.4 imports from the real path either way, and the
plan states the real path in its Global Constraints, so no executor reads §5.2 for it. The
correction is filed because a stale interface list is a trap for the *next* reader, not
because it blocks this one.

---

## Dispositions applied to `../specs/03-rating-engine.md`

*("this commit" in the first filing; the record has since grown across three PRs — #368, #373 and
the one carrying RL-879 — so each row names its own.)*

| Ruling | Edit | Section |
|---|---|---|
| 7 | Add the `rating/runtime.py` block with `def load_bundle(bundle: Bundle) -> CompiledBundle` | §5.2 |
| 9 | Dated amendment to `FR-256` — full evaluation, all firing codes collected, ladder always populated | §3 |
| 11 | Append `MODEL_CALL_FAILED` to the owned-code block | §5.1 |
| 13 | Money block corrected: module path, `apply_factor`'s third parameter, `reconcile_ladder` added, `to_minor` repointed | §5.2 |

Rulings 6, 8, 10 and 12 apply no spec edit. RL-874's spec change is owed by the PR that
builds the seam, and RL-878's contract correction by the PR that builds `QuoteContext`,
each for the reason its own disposition gives.

## Queued, not ruled — decision points whose slices have not started

Listed so that nothing here reads as overlooked. Each is ruled before its own slice, per the
same standard this record follows.

| Item | Slice | Why not now |
|---|---|---|
| **DP1** — default-live resolution for `POST /api/v1/score` | 2 | Plan recommends (b), defer to WK-674 as a named register deferral. Task 2.1 is not blocked by it |
| **DP2** — `FR-257`'s approval gate ahead of WK-672/WK-673 | 2 | Plan recommends (a), build the mechanism now. Blocks Task 2.3 only |
| **`FR-255`'s batch abort threshold — where it is configured** | 3 | The requirement says *"unless the failure rate exceeds a declared threshold"* and names no home. Recovery item 4 recommends a workspace setting on `FR-448`'s precedent with a per-request override. It reaches into `07`, and Slice 3's exit criteria are where it becomes real |
| **Trace persistence — thin Postgres row + blob body, GC-based retention** | 4 | Recovery item 2's recommendation (b). Slice 4's own scope |
| **Which spec declares `model_schema.money.to_minor`** | — | RL-879 removed it from `03` §5.2, where it was wrong on package and signature alike, and left a pointer comment. Its correct §5.2 home is `00`'s or `02`'s surface, not `03`'s. Not urgent; it is declared nowhere correct today |
| **`FR-258`/`42` state no **batch** sampling default** | 4 | A spec silence, not a choice inside an existing requirement — recovery item 2 flags it as needing an `OQ-` or a spec change. Raised properly it is an `OQ-RATE`, which per `.claude/skills/spec-change` also takes a `../roadmap.md` §10 decision-gate row and a recount of that row's `N (M open)` count. Owed before Slice 4 |

## Findings reported, not ruled

Neither is a decision; both are reported to the lead rather than acted on here.

1. **Nothing checks error codes across the spec/code boundary, in either direction.** Check
   10 of `../../scripts/audit-docs.py` (`:574-598`) reads only `docs/specs/*.md` and only
   tests that no code is claimed as owned by two modules. It never opens
   `backend/src/app/errors.py`. So a code can be listed as owned and exist nowhere (three do
   today — see RL-877), and a code could exist in `errors.py` owned by no spec, and the
   gate stays green either way. `PlatformError.__init__` catches the second direction at
   runtime, on the first raise; nothing catches the first.
2. **The frozen plan's Task 1.5 dependency tag is over-broad**, and its Task 1.3 instruction
   contains one claim about shipped code that does not hold (Rulings 6 and 8 respectively).
   Recorded as a finding against the plan, **not** as a request to edit it — a frozen plan
   is frozen (`docs/plans/README.md`), and this record is where its corrections live. Both
   belong in the §14 plan review at this workstream's close, as evidence about how a plan's
   literals age, alongside `docs/plans/README.md`'s own "conventions the audit cannot check".

## Verification

- Tree: `origin/main` at `7b8473a`, fetched and confirmed equal to local `HEAD` before this
  record was started. Every line number cited above was read at that tree; a line number is
  only as good as its revision.
- `python3 scripts/audit-docs.py` — clean after the three `03-rating-engine.md` edits.
- **The `MODEL_CALL_FAILED` edit was proven to register, not assumed to.** Two controls, both
  run in the worktree that produced this commit. *Positive:* the audit's own summary line
  goes `157 error codes, ownership exclusive` on the stashed tree to `158 error codes,
  ownership exclusive` with the edit applied — so check 10's regex genuinely parsed the new
  code out of §5.1's block rather than skipping over it. *Broken input:* the same code was
  temporarily also claimed in `02-modelling.md`'s owned block, and the audit printed
  `158 error codes, **1 conflicts**` with `error code MODEL_CALL_FAILED claimed by both
  02-modelling.md and 03-rating-engine.md`, then went clean again on revert (`git checkout --
  docs/specs/02-modelling.md`, working tree confirmed back to the two intended files). A
  check that has only ever printed a pass has not been tested — `CLAUDE.md` §13. Note the
  limit of what this proves: that check 10 sees this code and rejects a double claim. It
  proves nothing about whether the code is ever raised, because nothing in the gate reads
  `backend/src/app/errors.py` at all — finding 1 below.
- The three edits touch one spec and mint no `FR-`/`NFR-`/`OQ-` id, so no
  `docs/open-questions.md` mirror row and no `../roadmap.md` §10 gate row is owed by this
  commit. The one item that *will* owe both is the `FR-258`/`42` batch-sampling gap,
  queued above.
