---
id: RL-1265
family: ruling
title: WK-690 DP-1 to DP-5 — diagnostics to maintenance, continuous bases and expression metrics to P3, the flag liftable only, numeric expression factors refused, rating is not a grammar profile
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-29
owner: decision-maker
tree: ed123cb0fcf91e44872963bf8a8bad32b87c99bc
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-930, PL-1070]
---

# RL-1265 — WK-690 DP-1 to DP-5: diagnostics to maintenance, continuous bases and expression metrics to P3, the flag liftable only, numeric expression factors refused, rating is not a grammar profile

## Verified first, at ed123cb0fcf91e44872963bf8a8bad32b87c99bc

**Decided by the decision-maker, 2026-09-29** — the ruling is `## Ruled`, at the end. Its input is the
deputy's entry on WK-690's DP-1 to DP-5 (by the maintainer's delegation, 28 Sep, extended goal),
written at 14:06:12 BST and relayed by the lead, quoted whole under Input, fenced; with the
maintainer's answers named there, it is a recommendation (STRUCTURE entry, 15:26:00, §2).

**The plan these rule on** is WK-690's map plan, planner-690's local draft at `383ec991`
(`status: draft`, `tree: 6c6f4532…`). Its PR opens after #830 and #840. Its Decision points
table is at `:254-266` there, and its slices are Slice 1 (the parser, brought to the four
profiles), Slice 2 (symbolic derivation and the certificate), Slice 3 (the `expression` kind
behind the flag), Slice 4 (`expression` Factors) and Slice 5 (the authoring view and `WF-702`
Route B).

**Named by PR, not by id, until they merge** (an id that does not resolve fails
`audit-docs.py` check 32):
- the plan (its PR is not yet open);
- the standing maintenance Work, minted by #840;
- the Track E ruling and its E2 open question, both in #830.

That last point is this record's choice, as the lead offered: cite by PR number and push now,
rather than hold the push until #830 merges. The fenced entry quotes its ids whole.

This record was drafted in the decision-maker's worktree, on branch `p2-wk690-rl`, cut from
`origin/main` = `ed123cb0` with a clean root. Clock at drafting: 2026-09-28 14:10:47 BST, read
by `TZ=Europe/London date`. Filed under working id 9202; minted from working id 9202 at #847's merge turn,
`RL-1265` (2026-09-30 01:51:46 BST, `doc-id.py next --ref origin/main` at `843c3495`), and working id 9660 as `OQ-1266`.

**Re-read at `ed123cb0`, the text the entry quotes:**
- `docs/specs/02-modelling.md:273` is FR-178. It reads *"a GBM declaring a \*sparse\* cross
  cannot produce diagnostics at all"*. The entry drops the spec's italic on "sparse", and the
  words match.
- `docs/specs/07-platform.md:175` is FR-449. It contains *"default to the safe value"*.
- `docs/specs/03-rating-engine.md:145` is FR-244. It reads *"the same restricted grammar as
  `02` §4.6, extended with decimal-safe operators and these rating-specific functions"*.
- `docs/specs/02-modelling.md:218` is FR-154: *"Custom eval metrics (`feval`) follow the
  same lifecycle and grammar as objectives, declared separately so that a metric can be
  reused across objectives."*
- The sympy versions: `02-modelling.md:989`, inside §4.6, names `"derivation_version":
  "1.14.0"`, and `:1043`, inside §4.7 (which starts at `:1013`), names `"sympy": "1.13.x"`.

All of these are as the entry states them.

## Input — the deputy's entry of 2026-09-28 (a recommendation)

The deputy's entry, **whole and verbatim**. It is fenced so that the ids it quotes are read as
quotation, not as citations; `audit-docs.py` check 32 skips fenced blocks.

```text
## 2026-09-28 14:06:12 BST · deputy · WK-690 (PL-9103): DP-1 to DP-5 DECIDED (DP-5 with an FR-244 amendment); sympy in S1 confirmed; the sympy version conflict goes to S1

Given by the maintainer's delegation (28 Sep, extended goal). A decision-maker files these as an `RL-` quoting this entry, cited by PL-9103 before its mint. Read at `ed123cb0`.

- **DP-1: (b) ACCEPTED.**
  - **FR-176/177/178** (the GBM interaction diagnostics, delivered for the GLM path) go to **WK-1178, the standing maintenance Work**. **FR-178 is a live defect** (`02` FR-178: *"a GBM declaring a sparse cross cannot produce diagnostics at all"*), so **an auditor files an `FD-` for it now**: owner the lead, event WK-1178's next slice. It is scheduled **ahead of any Dependabot bump** in that Work.
  - **FR-85/86's field and FR-210** (continuous basis types) go to **Phase 3, spec change first**, as **deferred with an owner**: the maintainer, with the event being **the P2 phase closure record, which lists them for P3's first plan**. That record exists to show every carried item (CLAUDE.md §14).
- **DP-2: (b) ACCEPTED.** FR-154's expression half (`feval` metrics in the objective grammar) goes to P3 with the same owner and event. FR-154's non-expression half stays wherever it is already delivered or owned. PL-9103 states which half is which, citing FR-154's text.
- **DP-3: (a) ACCEPTED.** `expression_objectives_enabled` is **made liftable only and stays default-off** (`07` FR-449: *"default to the safe value"*). WK-690 does not switch it on anywhere. **Enabling it for a workspace is a separate, dated maintainer decision after WK-690 closes**, and the close records the flag's state.
- **DP-4 (new): (b) ACCEPTED.** An `expression` factor with a **numeric result is refused by name**. Only categorical or banded results are allowed, because `02` FR-210 requires a continuous term to be rateable and reviewable before any continuous basis is scheduled, and that capability is P3's (DP-1). The refusal message names FR-210.
- **DP-5 (new): the recommendation ACCEPTED, with one addition.**
  - `filter_rows` uses the **`recipe` profile** (it is a data-preparation operation, consistent with my E2 profiles).
  - **Rating is not a §4.6 profile.** `03` FR-244 currently says rating `expression` steps use *"the same restricted grammar as `02` §4.6, extended with decimal-safe operators and these rating-specific functions"*, with availability checked against the engine at compile time (FR-276). **S1 amends FR-244 (dated)** to say that the rating grammar is FR-244's own: ZEN's expression language, restricted to FR-244's function list and verified by FR-276. It shares function *names* with §4.6 where they coincide, but it is not one of its profiles. **§4.6 gets the matching note.** Both edits land in S1's commit, so the two specs never disagree.
- **sympy moving into S1: CONFIRMED** (the FR-144 amendment in #830; E3's "`sympy` with `skills-map`" holds).
- **The sympy version conflict** (`02` §4.6 names 1.14.0, §4.7 names 1.13.x): **S1 pins one exact version in `uv.lock` and amends both sections to cite the pin**, dated. It is not left for a later slice.
- **The other premises are noted for their slices:**
  - `OBJECTIVE_GRAMMAR_VIOLATION` is registered in S3;
  - `06` FR-367's missing permission is added in S3 or S5;
  - the `/derive` refusal that is unconditional under the flag is fixed in S3;
  - FR-165's per-round budget, built for neither kind, is S2 or S3's job, stated in PL-9103.

**I accept PL-9103 as WK-690's map plan** once it cites the RL and has minted (after #830 and #840). The acceptance line follows your request.
```

What the entry recommends, in this record's own words:

- **DP-1: (b).**
  - FR-176, FR-177 and FR-178 go to the standing maintenance Work (#840). FR-178 is a live
    defect, so an auditor files a finding for it now: owner the lead, event the maintenance
    Work's next slice, scheduled ahead of any Dependabot bump.
  - FR-85 and FR-86's field, and FR-210, go to Phase 3, spec change first. They are deferred
    with an owner: the maintainer, with the event being the P2 phase closure record, which
    lists them for P3's first plan.
- **DP-2: (b).** FR-154's expression half goes to Phase 3, with the same owner and event. Its
  non-expression half stays where it is already delivered or owned, and the plan says which
  half is which, citing FR-154's text.
- **DP-3: (a).** `expression_objectives_enabled` is made liftable only and stays default-off.
  WK-690 switches it on nowhere. Enabling it for a workspace is a separate, dated maintainer
  decision after WK-690 closes, and the close records the flag's state.
- **DP-4: (b).** An `expression` factor with a numeric result is refused by name, and the
  refusal names FR-210. Only categorical or banded results are allowed.
- **DP-5: the recommendation, with one addition.**
  - `filter_rows` uses the `recipe` profile.
  - Rating is not a §4.6 profile. Slice 1 amends `03` FR-244 (dated) to say the rating
    grammar is FR-244's own: ZEN's expression language, restricted to FR-244's function list
    and verified by FR-276. `02` §4.6 gets the matching note in the same commit.
- **sympy in Slice 1: confirmed.** The version conflict is settled in Slice 1: one exact
  version pinned in `uv.lock`, with §4.6 and §4.7 both amended to cite the pin, dated.

## What it obliges

The slice numbers are those of WK-690's map plan (`383ec991`).

- **Slice 1 (the parser):**
  - Add `sympy` at one exact version in `uv.lock`, with its `docs/skills-map.md` update (E3,
    already on `main`).
  - Amend `02` §4.6 and §4.7 to cite that pin, dated.
  - Put `filter_rows` on the `recipe` profile.
  - Amend `03` FR-244, dated, so that rating is FR-244's own grammar, not a §4.6 profile, and
    add the matching note to `02` §4.6. Both land in one commit, so the two specs never
    disagree.
- **Slice 2 or 3:** FR-165's per-round budget, built for neither kind. The plan states which
  of the two slices takes it.
- **Slice 3 (the kind, behind the flag):**
  - Make `expression_objectives_enabled` liftable only. Its default stays off (FR-449), and
    nothing switches it on.
  - Register `OBJECTIVE_GRAMMAR_VIOLATION`.
  - Fix the `/derive` refusal that is unconditional under the flag.
  - Add `06` FR-367's missing permission, here or in Slice 5.
- **Slice 4 (`expression` Factors):** refuse a numeric-result factor by name, with the
  message naming FR-210. Only categorical or banded results are allowed.
- **The Work's close:** it records the flag's state. Enabling the flag for any workspace is a
  later, dated maintainer decision.
- **Carried out of WK-690:**
  - FR-176, FR-177 and FR-178 go to the standing maintenance Work (#840). FR-178's finding is
    filed by an auditor now: owner the lead, event that Work's next slice, ahead of any
    Dependabot bump.
  - FR-85 and FR-86's field, FR-210, and FR-154's expression half go to Phase 3, spec change
    first, deferred with an owner: the maintainer, with the event being the P2 phase closure
    record, which lists them for P3's first plan.
- **The plan** states which half of FR-154 is which, cites this record by its minted id, and
  mints after #830 and #840. The input entry states the plan's acceptance on that condition;
  acceptance of a plan is not this record's to give.

## Acceptance — the violation that must become detectable

The violation: **a numeric-result `expression` factor accepted, the flag's default switched
on, or the rating grammar and a §4.6 profile disagreeing about what they are.** This record
builds nothing, so no check can be proven red here, and it forces none. The slices name the
negative tests, each shown red on deliberately broken input:

- *Violation: an `expression` factor with a numeric result is accepted, or refused without
  naming FR-210.* Slice 4.
- *Violation: `expression_objectives_enabled` resolves on in a workspace whose setting is
  unset.* Slice 3.
- *Violation: `uv.lock` holds a sympy version that `02` §4.6 or §4.7 does not cite.* Slice 1.
  It is a check that fails when the pin and the spec's cited version differ.

The FR-244 and §4.6 pairing is prose, and no check holds it. It lands in one commit, so the
review of that commit is where it is read.

## Ruled

First filed 2026-09-28 as working id 9202; `created` re-dated at the reframe so the id sequence stays non-decreasing (check 31).

The decision-maker adopted the maintainer session's recommendations unchanged, on 2026-09-29; each point below was re-verified before adoption. The recommendations are the deputy's entry, under Input, and the maintainer's 14:18:24 and 14:19:05 answers. The table's notes (DP-1 reaching FR-208's clause on auditor-row11's re-check, the sympy pin filed as `OQ-1266` as the 14:19:05 answer directs) apply those recommendations and change no decision.
The deputy's entry of 2026-09-28 14:06:12 BST, above, is input. The maintainer's entry `2026-09-29 15:26:00 BST · maintainer (acting on the maintainer's behalf) · STRUCTURE: routing per document-ids §1.6 and the charters; today's technical answers re-homed` (§2) makes the maintainer's
answers on this record recommendations, and gives the technical points to this role. The
answers are `2026-09-29 14:18:24 BST · maintainer (acting on the maintainer's behalf) · Q847-1/2/3 (row 11, WK-690)` and `2026-09-29 14:19:05 BST · maintainer (acting on the maintainer's behalf) · sympy pin: absent, so an OQ in #847's rebase`. This record's text stays as of `ed123cb0`, with the note below
(Q847-3). Each point below was re-verified at origin/main `ac8ab519`.

*(Noted 2026-09-29: the FR-178 obligation at :74/:96/:143 is discharged — FD-1195 closed by #900; FR-178 delivered by #880 and #887. #830 and #840 now resolve as WK-1178, RL-1184, OQ-1185.)*

The note's line numbers are this file's lines as filed. It is placed here, at the end, so that
those lines do not move.

| Point | Re-verified at `ac8ab519` | Ruling |
|---|---|---|
| **Q847-1:** DP-1 to DP-5 stand as filed | DP-1: `02` FR-85 (`:86`), FR-86 (`:87`) and FR-210 (`:373`) each carry an "Owner WK-690" clause, and FR-176 to FR-178 are WK-1178's (#880, #887). DP-2: FR-154 (`02:218`). DP-3: the flag is `features.expression_objectives_enabled` (`backend/src/app/platform/settings.py:245`, read at `platform/objectives.py:274`). DP-4: FR-210's text requires a continuous term to be rateable first. DP-5: FR-244 (`03:146`). `OBJECTIVE_GRAMMAR_VIOLATION` is declared in `02` §5.1 (`:2056`) | **Adopted.** Each decision rests on a mechanism or a text that exists at `ac8ab519`. None is re-issued |
| **Q847-2:** the "Owner WK-690" clauses of FR-85, FR-86 and FR-210 move to Phase 3 (DP-1) | As above | **Adopted, and done in this commit.** Each row gains a dated amendment: the clause is superseded, and the obligation is deferred to Phase 3, spec change first, with the owner (the maintainer) and the event (the P2 phase closure record) that DP-1 names *(2026-09-29, on auditor-row11's re-check: DP-1 reaches a fourth clause. `02` FR-208 (`:371`) says `spline` and `polynomial` are "gated on FR-210 and owned by WK-690". DP-1 moves FR-210 to Phase 3, and those two arms wait on FR-210, so leaving FR-208's clause would make the spec contradict itself. FR-208 gains the same dated amendment. The arms stay refused.)* |
| **Q847-3:** the text stays as of its tree, with the dated note | The note's facts: FD-1195 is `status: closed`, by #900 (`870ce82b`). FR-178 was delivered in two parts, by #880 (`9fa2b833`) and #887 (`95faf68b`), as FR-178's own amendment says. #830 (`3767b3b4`) filed RL-1184 and OQ-1185, and #840 (`2d20ca4b`) minted WK-1178 | **Adopted.** The note is quoted verbatim above this table |
| **The sympy pin** | `sympy` has 0 hits in `uv.lock` and in all four `pyproject.toml` files. `02:1015` names `"derivation_version": "1.14.0"`, and `02:1069` names `"sympy": "1.13.x"` | **Filed as `OQ-1266`**, open, not a pick. It is mirrored in `02` §10 and `docs/open-questions.md`, and placed at the roadmap §10 gate *Before WK-690 Slice 1*. DP-5's obligation, one exact pin in Slice 1 with both sections citing it, is unchanged. `OQ-1266` asks which version |
