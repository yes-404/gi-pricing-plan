---
id: RL-9633
family: ruling
title: WK-673 — the FR-240 family fix activated, model approval and compile refuse an unapproved custom objective and compile and seed refuse a control-intent factor (PL 9649 DP-1 to DP-6, the lane, and texts T1 to T4)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-05              # the mint date (check 31); ruled 2026-10-05
owner: decision-maker
tree: 83ea509023d6d705d6f78fe74b7124fdf1375739
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-240, FR-230, FR-88, FR-359, FR-20, OQ-609, RL-1263, RL-1329, RL-1361]   # at the mint, add FD 9697's, FD 9659's, FD 9639's, PL 9649's, SL 9647's and OQ 9630's minted ids
---

# RL 9633 (working id) — WK-673: the FR-240 family fix activated, PL 9649 DP-1 to DP-6 and texts T1 to T4

## How this was ruled

- **Filed under a working id the lead reserved.** `RL 9633` in this draft, and `RL-9633` in
  the texts below, stand for this ruling's minted id. `FD 9639`, `FD 9659`, `FD 9697` and `FD 9995` in
  the texts are working ids, re-pointed to their minted ids in the same mint PR as each
  finding (the maintainer's (by delegation) 14:26:28 BST entry, item 3). Nothing else is a placeholder except
  `<SL 9647 date>` (§"The spec texts").
- **The decisions are not this record's.** They are the maintainer's (by delegation), in `~/gi-pricing-plan.local/channel/to-lead.md`, cited below by entry header and
  quoted verbatim. This record carries them as a dated artifact (`CLAUDE.md` §12) and makes
  PL 9649's activation need 2 true. It decides nothing beyond them.
- **Inputs, read at the heads named:** PL 9649, draft #1152, branch `pl-9649-fr240-fix`
  @`982ab531` (planned at `83ea5090`); FD 9697, draft #1136 @`1649e360`; FD 9659, draft
  #1142 @`52a68d0f`; FD 9995, draft #980 (open, not on main). Every spec and code locator
  below was re-read at `origin/main` `83ea5090` on 2026-10-05. `origin/main` then moved to
  `c37bf921`; `git diff --stat 83ea5090 c37bf921 -- docs/specs backend packages` is empty,
  and each find string below was re-counted at `c37bf921` with the same result.
- **Updated for Ruled 8, 2026-10-05.** Input: FD 9639, draft #1156 @`ca152d5f`.
  `origin/main` had moved to `bc92bb7e`; `git diff --stat c37bf921 bc92bb7e -- docs/specs
  backend packages` touches `03-rating-engine.md` only, at `:136` (FR-239, an FD id
  re-pointed), so FR-240 stays at `:137`. Every find string below was re-counted with
  `git show bc92bb7e:<file> | grep -cF -- '<find string>'` and gives **1**. The model_call
  locators were read at `bc92bb7e`: `packages/pricing-core/src/pricing_core/rating/runtime.py:565`
  calls `predict_gbm(gbm_result, booster, frame, factors=(), nthread=1)`, and
  `packages/pricing-core/src/pricing_core/modelling/gbm.py:1290-1297` requires every slug of
  `result.feature_order` on the frame (`SCORING_FEATURES_MISMATCH`); `grep -n intent
  packages/pricing-core/src/pricing_core/rating/*.py` prints nothing.
- **Updated for Ruled 9, 2026-10-05.** Input: the decision entry quoted in Ruled 9, and the
  draft `~/gi-pricing-plan.local/handover/OQ-draft-control-in-scoring-2026-10-05.md` it decides.
  `origin/main` was `809a3794`; Ruled 1 to 8, the texts and the locators are unchanged.
- **Pre-mint correction, 2026-10-05.** "What it obliges", the rateable-path item, said the
  plan's Acceptance did not list a `rateable: false` case and the dispatch record would add
  it. That was stale: PL 9649 Acceptance 5 at `2b5bf12d` (#1152) already has it as a red-first
  parametrised case. The item now says so. The maintainer (by delegation) set this fix in the
  entry "2026-10-05 15:15:11 BST — F2 (RL-1263's "from different Works"): OPTION (i), amend
  RL-1263 by a dated RL, with conditions; F1, F3 and the stale RL 9633 sentence as you set
  them". No ruling changes.
- **Brief:** the lead's spawn message to this decision-maker, 2026-10-05.

## Locators — read at `83ea5090`

- `03-rating-engine.md:137`, FR-240: "… no `control`-intent factor in a rateable path (`02`
  FR-88), no unapproved custom objective transitively reachable." One dated amendment
  (`RL-1329`), ending `The message names the step and the rung.)* |`.
- `03:121`, FR-230: the seed-from-model row, with `RL-1361`'s clarification, ending
  `A hand-authored table may still have several keys (FR-228). |`.
- `03:902`, the `POST /api/v1/rate-tables/{slug}/seed-from-model` route row; its 422 list is
  `VALIDATION_FAILED` only.
- `03:928-940`, the owned-codes paragraph: `CONTROL_FACTOR_IN_RATEABLE_PATH` is already
  listed (`:933`) with no note.
- `02-modelling.md:49-50`, R4: "**R4 — A Model using a Custom Objective can only reach
  `approved` if that objective is itself `approved`** (FR-20)." It sits in a blockquote.
- `02` FR-88: a `control` factor reaching a "rate table is a validation error in `03`".
- `02:3303`, OQ-609, struck (decided).
- `06-governance.md:100`, FR-359: "unapproved custom objective (`02` R4) … A flagged artifact
  cannot be approved until the flag is cleared or explicitly overridden by an Admin with a
  recorded justification." `ARTIFACT_FLAGGED` is `06`-owned (`06:604`).
- `docs/contracts/schemas/approval-request.schema.json:54`: the flags enum carries
  `custom_objective_not_approved`.
- `packages/pricing-core/src/pricing_core/rating/compile.py:404`,
  `_APPROVED_OR_BETTER = frozenset({"approved", "live", "retired"})`; `PIN_NOT_APPROVED` at
  `:606` and `:629`. `backend/src/app/platform/modelling.py:1049`, `flags_for`.

## Ruled

1. **DP-1, as decided (option (a)).** Entry "2026-10-05 14:21:22 BST — DECISIONS 35–38 (PL
   9649, the FR-240 family fix); file the model_call candidate; FD 9641 noted", item 35:
   "DP-1: OPTION (a), the computed flag `custom_objective_not_approved` in flags_for, giving
   the existing ARTIFACT_FLAGGED 409. Verified: the spelling is already in
   docs/contracts/schemas/approval-request.schema.json's flags enum, whose description reads
   "a flagged artifact cannot be approved until cleared or overridden by an Admin with a
   recorded justification (FR-359)". So the spec designed this block as an Admin-overridable
   flag. CONDITION: the override must NOT reach compile. FR-240's compile refusal is absolute
   and independent of approval state, so a red-first test: flag → Admin override with
   justification → the model approved → compile_bundle still REFUSES. ModelFlag,
   model.schema.json and the contracts are regenerated in the same commit."
2. **DP-2, as decided (option (a)).** Same entry, item 36:
   "DP-2: OPTION (a), one hop: each pinned model's own `spec.objective` of custom kind,
   refused with PIN_NOT_APPROVED naming model → objective. FR-240's T-text states the bound
   verbatim, and states the exclusion: peril structures, unresolvable at compile until FD
   9995 is fixed, are named as a known gap with FD 9995 as its owner, not silently out of
   scope. Custom evaluation metrics are excluded: they do not reach a price."
3. **DP-3, as decided (option (a)).** Same entry, item 37:
   "DP-3: OPTION (a). Refuse at SEED and at COMPILE with CONTROL_FACTOR_IN_RATEABLE_PATH
   (422, 03-owned, registered in this slice), plus a dated FR-230 amendment as a T-text. That
   matches FR-88 ("reaching a rate table" is an error). (b) would create the table FR-88
   forbids, just labelled differently."
4. **DP-4, as decided (option (a)).** Same entry, item 38:
   "DP-4: OPTION (a), every pinned rate table's key factor_ref, whatever its `rateable`. The
   flag is declarative, so the check does not trust it. With 37 (a), no seeded table can carry
   a control factor anyway; this catches hand-built ones."
   The plan's option (c) is not this record's. Same entry: "CANDIDATE (c), a model_call whose
   model was fitted with a control factor: YES, file it as a finding. … Owner WK-673."
5. **DP-5, as recommended by the plan and confirmed (option (i)).** Entry "2026-10-05
   14:28:35 BST — PL 9649 / SL 9647 (the FR-240 fix, #1152 @dc13400e): DP-5 OK; DP-6 scoped;
   lane placement", item 39:
   "DP-5 (`deprecated` refused at compile too, OQ-609): OK, with a red test."
   That is PL 9649's option (i): compile admits `_APPROVED_OR_BETTER` (locators), so
   `deprecated` is refused; the flag is raised for any status other than `approved`.
6. **DP-6, as decided (option (a)), amended.** Same entry, item 40:
   "DP-6, AMENDED: Task 0 counts bad rows (a control-intent factor in a pinned table key; an
   unapproved custom objective behind an approved model) in `gipricing` (the demo DB) and in
   the slice's own per-worktree test DB ONLY, not "gipricing*". Measured at 14:28: 92
   databases match `gipricing_%` (1240 MB), nearly all scratch left by ended agents; their
   contents are disposable and would stop the slice for nothing. If gipricing has any bad row,
   STOP and report to me with the ids (no reset, no delete), as proposed."
7. **The lane.** Same entry, "LANE":
   "it is a HIGH G2 blocker (FD 9697, FD 9659), so under my 13:12:56 rule it takes the first
   build lane free once its plan is active, ahead of any slice G2 does not need. Concretely:
   after whichever of the FD 9707 fix (lane B) or the FD 9708 fix (lane C) finishes first, it
   goes BEFORE PL 9728 (NFR-489, a G4 item) in lane B, or BEFORE WK-675 S2 (off G2's path) in
   lane C. WK-673 S3 in lane A is NOT displaced (G2 needs "a dislocation run with
   attribution")."
8. **DP-7 (PL 9649 @`2b5bf12d`), the model_call case of DP-4 (c): refused now,
   neutralisation left open.** Entry
   "2026-10-05 14:46:53 BST — FD 9639 (a control factor's coefficient reaches scoring): HIGH
   provisional; PL 9649 takes the REFUSAL now; neutralisation is an open question first",
   item 2:
   "Scope: PL 9649 takes the SAFE MINIMUM now: compile_bundle refuses a model_call whose
   pinned model's feature_order contains a `control`-intent factor, with
   CONTROL_FACTOR_IN_RATEABLE_PATH, red first (the same code as decision 37). That stops any
   price depending on a control factor today, and fits PL 9649's FR-240 T-text ("no
   control-intent factor in a rateable path")."
   Item 3 of the same entry is not ruled here: neutralisation is an open question, drafted
   for the lead to file, and "If (b) or (c) is chosen, it is a spec change first (02 FR-88
   and 03), then its own slice under WK-673, not part of PL 9649."
   T1 and T4 below carry this item.
9. **OQ 9630 (the model_call case, how a control-fitted model is scored), as decided (option
   (c)), with both conditions.** Entry "2026-10-05 14:54:40 BST — READ-BACK VERIFIED #1144; OQ
   (control factor in scoring) DECIDED: option (c) with the DM's two conditions; file it as a
   decided row":
   "OPTION (c). A model fitted with a `control`-intent factor may be scored in a priced Rating
   Version only if a versioned artifact DECLARES the reference value at which each control
   factor is HELD. Otherwise compile refuses it, with RL 9633 Ruled 8's refusal as the
   default. Both of the DM's conditions are part of the decision:
    (1) the spec says the factor is "held at" the declared reference, never "removed" (a GBM's
   interactions with it remain, so removal would be false);
    (2) every held factor and its value appear in the quote's explanation and in the
   transparency artifact ([02 FR-132]), so the price shows what it was held at."
   One change to the quote: the entry cites the Transparency Artifact requirement by its
   pre-W37-6 scoped id, which check 36 refuses, so `[02 FR-132]` replaces it with the id
   `docs/REDIRECTS.csv` row 707 maps it to (`02-modelling.md:191` at `809a3794`).
   - **Ruled 8's refusal stays the default until the declared-reference capability lands.**
     Same entry: "Until it lands, Ruled 8's refusal holds." Nothing in Ruled 8, T1 or T4
     changes, and SL 9647 builds Ruled 8 as written; (c) adds only the "unless declared"
     branch, later.
   - **A spec change first, then its own slice.** Same entry: "Consequences: a spec change
     FIRST (02 FR-88 and 03 FR-240, dated amendments, a DM's T-texts), then its own WK-673
     slice." This record writes no T-text for it; FR-88 and FR-240 are not amended by this
     item.
   - **Not a G2 blocker.** Same entry: "It is NOT a G2 blocker (the seed and goldens use risk
     factors only), so it sits in WK-673's queue after the HIGH fixes, owner WK-673."
   - **FD 9639's severity is not set here.** Same entry: "FD 9639's measurement still fixes
     its own severity at its mint, independently of this."
   The question is filed as a decided row, OQ 9630 (working id), in `docs/open-questions.md`
   and its `02` §10 mirror, in its own PR, citing this record.

## The spec texts

Four texts, PL 9649 §"Spec texts" T1 to T4, with T5 folded into T1 (Ruled 8). Placement was read at `origin/main` `83ea5090`.
They are applied by SL 9647 (PL 9649 Task 6), in one commit with the code (`CLAUDE.md` §2),
and `<SL 9647 date>` is that commit's date. Each find string below was counted with
`git show 83ea5090:<file> | grep -cF -- '<find string>'` and gives **1**.

**Amendments common to all four**, each applied below and not repeated per text:

1. **The marker.** "*(Amended 2026-10-05, FD …)*" → "*(Amended <SL 9647 date>, `RL-9633`,
   FD …)*", and T4's "*(registered 2026-10-05, FD 9697: …" → "*(registered <SL 9647 date>,
   `RL-9633`, FD 9697: …". A spec amendment cites the governed record that rules it and is
   dated by the commit that applies it, as RL 9642 (#1148) and RL 9710 (#1128), both unminted, do; the maintainer's (by delegation) entries
   live in a local channel file a spec reader cannot open, and this record quotes them.
2. **The layout.** The proposals are blockquotes across lines. T1, T2 and the seed route
   addition go into table cells, and T4 into a running paragraph, so each is one physical
   line holding no `|`. T3 goes into `02`'s R-rules blockquote, so it is one line prefixed
   `> `.

No other byte of any proposal changed, except where a text below says so.

**T1 — `03` FR-240, the transitive bound and the rateable path (DP-2, DP-4, DP-5, Ruled 8).**
Proposed by PL 9649 §"Spec texts" T1 and **adopted verbatim** (common amendments only),
**extended for Ruled 8 by folding in PL 9649's T5** (branch `pl-9649-fr240-fix`
@`2b5bf12d`, which offers "the ruling may fold it into T1"): the marker adds `FD 9639`, and
the last two sentences (from "A `control`-intent factor is also in a rateable path") are T5's
body verbatim. T5's own marker, "*(Amended 2026-10-05, FD 9639.)*", is dropped, as T1's
marker now carries it. T5 is not applied separately.

Placement: the FR-240 row (`docs/specs/03-rating-engine.md:137`). The text is **appended** to
the end of the second cell, after the `RL-1329` amendment's closing `)*` and one space,
before the closing ` |`. Nothing is struck.

Find string (1 hit):

```text
The message names the step and the rung.)* |
```

Append

```text
*(Amended <SL 9647 date>, `RL-9633`, FD 9659, FD 9697 and FD 9639.)* **"Transitively reachable" means through a pinned model**: a pinned model whose spec names a custom objective (a GBM's `spec.objective` with `kind: custom`) reaches that objective, and compilation refuses it with `PIN_NOT_APPROVED` unless it is approved or better, exactly as if it were pinned. The message names the model and the objective. A `deprecated` objective is refused, as a new specification may not select one (`02` OQ-609). The bound is one hop. **Known gap:** a peril structure's models are not reached, because a peril structure cannot be resolved at compile; FD 9995 owns that gap, and this clause reaches them when it is fixed. Custom evaluation metrics are not objectives and do not reach a price, so they are outside this clause. **A `control`-intent factor is in a rateable path when a pinned rate table has a key bound by `factor_ref` to it**, whatever the table's `rateable` flag; compilation refuses it with `CONTROL_FACTOR_IN_RATEABLE_PATH` (422), naming the table, the key and the Factor. **A `control`-intent factor is also in a rateable path when a pinned model scored by a `model_call` was fitted on it**: compilation refuses the version with `CONTROL_FACTOR_IN_RATEABLE_PATH` (422), naming the model, the feature and the Factor, because scoring applies every fitted feature's effect and `02` FR-88 lets Rating Versions use only `risk` factors. Scoring at a declared reference level for a `control` factor is an open question (FD 9639), not a permission.
```

**T2 — `03` FR-230 and the seed route, the refusal at seed (DP-3).** Proposed by PL 9649
§"Spec texts" T2 and **adopted verbatim** for the FR-230 cell (common amendments only). T2
also adds "the same refusal … to the seed route's 422 list (`:902`)" and gives no text for
it; the route text below is that refusal restated in the row's own form, with T2's trigger
and code and nothing added.

Placement 1: the FR-230 row (`03:121`). The text is **appended** to the end of the second
cell, after `(FR-228).` and one space, before the closing ` |`.

Find string (1 hit):

```text
A hand-authored table may still have several keys (FR-228). |
```

Append

```text
*(Amended <SL 9647 date>, `RL-9633`, FD 9697.)* A seed request naming a `control`-intent Factor is refused with **422** `CONTROL_FACTOR_IN_RATEABLE_PATH` (`02` FR-88): a `control` factor is fitted to absorb variance and is never rated on, so no rate table is seeded from it.
```

Placement 2: the seed route row (`03:902`). The text is **appended** at the end of the third
cell, after `sections A and D**)` and before the closing ` |`, with no space before its `;`.

Find string (1 hit):

```text
workspace (`load_factors`) (**amended 2026-10-03, `RL-1361` sections A and D**) |
```

Append

```text
; **422** `CONTROL_FACTOR_IN_RATEABLE_PATH` for a `factor` that names a `control`-intent Factor (FR-230, `02` FR-88) (**amended <SL 9647 date>, `RL-9633`, FD 9697**)
```

**T3 — `02` R4, where the rule is enforced (DP-1, DP-5).** Proposed by PL 9649 §"Spec
texts" T3 and **adopted verbatim** (common amendments only).

Placement: `docs/specs/02-modelling.md`, after the R4 line (`:50`), as a new paragraph of the
same blockquote: insert two lines after the find string's line, a bare `>` and then the text,
so the existing `>` line before R5 still separates it from R5.

Find string (1 hit):

```text
itself `approved`** (FR-20).
```

Insert after that line

```text
>
> *(Amended <SL 9647 date>, `RL-9633`, FD 9659.)* R4 is enforced at the approval transition by a computed flag, `custom_objective_not_approved`: a model whose GBM `spec.objective` names a custom objective that is not `approved` carries it, and `06` FR-359 refuses `approved` with `ARTIFACT_FLAGGED` (409). Compilation re-checks the objective (`03` FR-240), so an objective deprecated after the model's approval is caught there. An Admin override of the flag (FR-359) never reaches compilation: FR-240's refusal is independent of approval state.
```

**T4 — `03` §5.1's owned codes, the code's note (DP-3, DP-4, Ruled 8).** Proposed by PL 9649
§"Spec texts" T4 and **adopted verbatim** (common amendments only), **extended for Ruled 8**:
"and FD 9639" and the closing clause from "or for a `model_call`" are this record's, naming
what T5 names.

Placement: the owned-codes paragraph (`03:933`), immediately after
`` `CONTROL_FACTOR_IN_RATEABLE_PATH` `` and one space, before the `,` that precedes
`` `PIN_NOT_APPROVED` ``.

Find string (1 hit; the text goes between its first backtick-closed code and the comma):

```text
`RATE_TABLE_KEY_DUPLICATE`, `CONTROL_FACTOR_IN_RATEABLE_PATH`, `PIN_NOT_APPROVED`,
```

Insert

```text
*(registered <SL 9647 date>, `RL-9633`, FD 9697 and FD 9639: **422** at `seed-from-model` (FR-230) and at bundle compile (FR-240); the message names the table, the key and the Factor, or for a `model_call` the model, the feature and the Factor)*
```

## What it obliges

- **This commit:** this record only. No spec, plan or code file is edited here.
- **PL 9649's activation need 2 is met** by this record once minted. Need 1 (FD 9697 and
  FD 9659 minted, #1136 and #1142), need 3 (the activation PR's dated line) and need 5 (the
  dispatch GO) are not this record's.
- **SL 9647 (PL 9649, the planner's file, not edited here)** applies T1 to T4 in Task 6,
  verbatim from this record. Where this record and the plan's §"Spec texts" differ — the
  common amendments, and T2's route text, which the plan names but does not write — this
  record wins and the dispatch record names each difference at every site it operates
  (PL 9649 activation need 2; `docs/plans/README.md` rule 5).
- **DP-1's condition binds the slice:** `ModelFlag`, `model.schema.json` and the generated
  contracts change in the same commit (Ruled 1); the override-to-compile red is in the
  acceptance below.
- **DP-6's stop binds the executor:** a bad row in `gipricing` stops the slice with the ids,
  no reset and no delete (Ruled 6). The scratch `gipricing_%` databases are not counted.
- **The dispatch record** names the lane of Ruled 7 and the serialisation with the FD 9707
  fix (PL 9688) on `compile.py` that PL 9649 §"Write set" records (`RL-1263`).
- **DP-4 (c)** is a separate finding, FD 9639, owner WK-673 (Ruled 4). This record covers
  only its refusal (Ruled 8, PL 9649's DP-7), which SL 9647 builds (Task 3b). FD
  9639's severity and closure are not this record's. Neutralisation is an open question the
  lead files; if it is decided (b) or (c), that is a spec change to `02` FR-88 and `03`
  first, then its own WK-673 slice, and T1's last sentence is amended then.
- **FD 9995** owns the peril-structure gap T1 names; when it is fixed, T1's clause reaches
  a peril structure's models without a further amendment to its bound.
- **FD 9697 and FD 9659** are closed by SL 9647's merge when the acceptance below is met.
  The verdict is the lead's.

## Acceptance — the violation that must become detectable

The violation: **a bundle that compiles, or a model that is approved without an override,
while an unapproved custom objective sits behind a pinned model, or while a pinned rate
table has a key bound to a `control`-intent Factor, or while a `model_call` step's pinned
model holds a `control`-intent Factor in its `feature_order`; or a rate table seeded from a
`control`-intent Factor.** PL 9649's Acceptance Standard items are the tests; each red is seen
at the slice's base for its stated cause. In particular:

- **Approval (DP-1, DP-5):** approving a model whose custom objective is in `review` is
  refused with `ARTIFACT_FLAGGED` (409), naming `custom_objective_not_approved` and the
  objective, red first; `flags_for` returns the new `ModelFlag` member (Acceptance 1, 2).
- **The override never reaches compile (DP-1's condition):** flag → `approved` as an Admin
  override would leave it → compile, and the compile Job fails with `PIN_NOT_APPROVED`, red
  first (Acceptance 4). FR-359's override is not built for any flag at `83ea5090` (PL 9649
  Acceptance 4 reads `modelling.py:1339-1351`), so the test reaches `approved` through the
  test helper the plan names; this record does not oblige building the override.
- **The transitive check (DP-2, DP-5):** a pinned model over a `certified`, `review` and
  `deprecated` objective is each refused at compile with `PIN_NOT_APPROVED`, naming the model,
  the objective and its status, red first; an `approved` objective compiles (Acceptance 3).
- **The rateable path (DP-3, DP-4):** a pinned rate table with a key bound to a
  `control`-intent Factor is refused at compile with `CONTROL_FACTOR_IN_RATEABLE_PATH`,
  naming the table, the key and the Factor, red first (Acceptance 5, 7). DP-4's "whatever its
  `rateable`" needs the case of a table with `rateable: false`: PL 9649 Acceptance 5
  (@`2b5bf12d`) parametrises the test over `rateable` `[True]` and `[False]`, with `[False]`
  red first by the same cause.
- **The model_call case (Ruled 8):** a bundle whose `model_call` step pins a GBM model with a
  `control`-intent Factor in its `feature_order` is refused at compile with
  `CONTROL_FACTOR_IN_RATEABLE_PATH`, naming the model, the feature and the Factor, red first
  (the base compiles it); the same bundle over a model fitted on `risk` factors only
  compiles; and through the compile Job the version fails with that code (PL 9649
  Acceptance 13 and Task 3b, @`2b5bf12d`).
- **At seed (DP-3):** `POST /api/v1/rate-tables/{slug}/seed-from-model` naming a
  `control`-intent Factor gets 422 `CONTROL_FACTOR_IN_RATEABLE_PATH` where the base gave 201,
  red first (Acceptance 6).
- **Task 0 (DP-6):** the counts over `gipricing` and the slice's own test DB, with the
  query verbatim, are in the ledger (Acceptance 10).

Drafted as working id 9633, 2026-10-05.
