---
id: PL-2025
family: plan
kind: map
title: WK-1178 — FactorCreate.slug takes the Factor grammar at the write boundary (FD-1384), SL-2026 — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8327
owner: planner
tree: dae9637ea6f6a56f6502e9db70392cdfb2f3983d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1384, FD-1799, RL-1383, SL-1806, FR-4, FR-83, FR-96, FR-209]
---

# PL-2025 — WK-1178: `FactorCreate.slug` takes the Factor grammar (SL-2026, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds one slice row, SL-2026, and edits no filed plan.
> The executor's skills are `superpowers:test-driven-development`, `.claude/skills/python-test`,
> `.claude/skills/python-package`, `.claude/skills/contract-schema`, `spec-change` and `git-hygiene`.
> PL-2025, SL-2026 and LG-2027 were drafted under working ids 8327, 8328 and 8329, reserved by the lead, and
> minted on 2026-11-05 (`mint-repoint.py`). FD-1337, the group's other row,
> is split out to PL 8339 by the entry "2026-11-05 09:58:58 GMT".

## Authority

- **The order.** The maintainer's entry "2026-11-05 09:58:58 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`: all FIX rows "coded and merged before Thu 12".
- **FD-1384's remedy.** "**Refuse at the write boundary** (named 422s, spec text first).
  `FactorCreate.slug` takes the Factor pattern, and the Banding and Grouping create bodies take theirs.
  Sweep Banding, Grouping and `RatingVersionCreate` in the same item, or file each that it confirms."
  Its limit: "**Do not refuse on read until stored rows are swept.**" Its event: "refuses out-of-grammar
  Factor, Banding and Grouping slugs at the write boundary with a named 422 each (or the sweep files the
  residue), citing that PR."
- **RL-1383** rules the pattern, `^[a-z0-9][a-z0-9_-]{1,62}$`. `00` §4.3 already states it.
- **The brief.** "FD-1384's spec text first".
- **The triage** (`b28ba8e9454c`) §3, Slice C. Corrected below: the Banding and Grouping fix was SL-1806,
  not SL-1758.

## Goal

`POST /api/v1/factors` refuses a slug outside the Factor grammar with a 422 naming `slug`, so the
sweep's last open member closes and FD-1384 with it. The read path stays tolerant.

## Evidence at `dae9637e`

- **The open member.** `backend/src/app/api/models.py:208` `class FactorCreate`, `:211` `slug: str`.
- **The sweep the essay asked for.** Banding and Grouping: `8db3e1e1` (2026-10-18, "SL-1806 Banding
  and Grouping slugs typed Slug, refused 422 at POST — FD-1799") gives `BandingProposalRequest.slug:
  Slug` (`api/models.py:256`) and `GroupingProposalRequest.slug: Slug` (`:260`). `RatingVersionCreate`
  (`packages/model-schema/src/model_schema/rating.py:210`) has `slug: Slug` (`:221`). **So one of
  four remains.**
- **The grammar exists, unexported.** `model_schema/refs.py:42` `_FACTOR_SLUG =
  r"[a-z0-9][a-z0-9_-]{1,62}"`; `:62` `Slug = Annotated[str, Field(pattern=rf"^{_SLUG}$")]`, built
  the same way, and that is the type to copy. `refs.py:19` `__all__`.
- **The read model is `str`,** on purpose: `Factor.slug` (`modelling.py:134`). It stays: the essay's
  second bullet, FR-209.
- **The spec.** `docs/specs/00-overview.md:337` states the pattern. `02-modelling.md:1897` is the
  `POST /api/v1/factors` row, and FR-83 (`02:86`) defines a Factor. Neither says a create is refused.
- **The refusal's shape.** Pydantic's pattern failure reaches `_handle_validation_error`
  (`backend/src/app/errors.py`) as 422 `VALIDATION_FAILED` with field-level errors. That is what
  SL-1806 delivered for Banding and Grouping: `VALIDATION_FAILED` with the field is the "named 422".
- **Who posts today.** A sweep of `/factors"` in `backend/tests`, `scripts` and
  `examples/fremtpl2/*.py` finds slugs like `driver-age-<hex>`, all inside the grammar, and helper
  arguments (`_factor`-style, eight files) that the executor reads at R0. The grammar's `{1,62}` means
  **a minimum of two characters**: a one-character slug in a fixture would go red. The SPA's
  form, `frontend/src/components/FactorCreateForm.vue:42,66`, is free text with no default, so a bad
  slug there becomes this 422, which the form shows.
- **The contract moves.** A `pattern` on a request body changes `docs/contracts/openapi/generated.json`;
  `.github/workflows/frontend.yml` fires on `docs/contracts/openapi/**`. Regenerate with
  `uv run python scripts/generate-contracts.py`; never hand-edit.

## Decision points

No decision point is open. The pattern is RL-1383's, the code is SL-1806's precedent, and the tolerant
read is the essay's. The brief's "spec text first" is R0's clause below; its wording is the
executor's under `spec-change`, on the sentence given. **This plan can go `active` at its mint with no
ruling.**

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's
merge tree. Items 1 and 2 apply to this plan; A1 to A9 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no
   failing line except check 31 / check 32 lines naming working ids 8327, 8328 or 8329. After the
   mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints
   no line that stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only the Write set below.
- **A2. Spec text first.** The `02` commit precedes the first code commit.
- **A3. Red first, by cause.** LG-2027 quotes T1's red: a `201` (or the route's success status) for
  `""`, `"Veh Brand"`, `"a:b@1"`, a 65-character slug and a one-character slug. T1 reaches the route,
  so it runs in the DB window or the gate; T2 is DB-free.
- **A4. Green.** T1: each is 422 `VALIDATION_FAILED` and the error's field is `slug`; `veh_brand` and
  `driver-age-1a2b` succeed. T2: the type admits and refuses exactly as `_FACTOR_SLUG_RE` does.
- **A5. One grammar.** `git grep -n '\[a-z0-9\]\[a-z0-9_-\]' -- packages backend/src` prints only
  `refs.py:42`.
- **A6. The read stays tolerant.** T3: `Factor.model_validate` of a payload with slug `"Veh Brand"`
  still succeeds, and `git diff origin/main...HEAD -- packages/model-schema/src/model_schema/modelling.py`
  is empty.
- **A7. The contract.** `generate-contracts.py --check` rc 0, and the `generated.json` diff is the one
  `pattern`, on `FactorCreate.slug`. `pnpm --dir frontend generate:api` and `type-check` rc 0 in the
  gate's frontend half.
- **A8. The GREEN set and the gate.** The GREEN set by import closure (common seat brief, item 29),
  commands and list in the LG. **The full code gate, both halves, SOLO**, green at the re-merged
  head, every rc quoted. A fixture slug that goes red is corrected to the grammar and listed in the LG;
  no test is weakened.
- **A9. The closing act and the audit.** **FD closing act in the FD-1842 form, in the slice's own PR,
  by the slice's auditor:** FD-1384's `status: closed`, `relates:` gaining the slice's ids, a
  `***Resolved <date>***` paragraph naming SL-1806 for Banding and Grouping, this slice for Factor, and
  `RatingVersionCreate` as found typed, the same on the register row, and the PR number and squash at
  the merge's date of record. **The LG Audit section, with the lead's adoption, lands in the audit's own
  commit**, and `docs/INDEX.md` is regenerated after the closing acts (common seat brief, item 17).

## Global Constraints

- **G1. `model-schema` is the one definition** (`CLAUDE.md` §2). `FactorSlug` lives in `refs.py`, built
  from `_FACTOR_SLUG`, not retyped.
- **G2. Reads are unchanged** (FR-4, FR-96, FR-209). No stored row is rewritten, and `Factor.slug`
  stays `str`.
- **G3. No new error code.** FD-1384's event asks for "a named 422"; `VALIDATION_FAILED` with the
  field is that, as for Banding.
- **G4. `FactorCreate` is the one body changed.** Red first, by cause. No test is weakened
  (common seat brief, item 13).

## Needs

- **DB / Redis.** T1 is route-level. Either the gate proves it, with its red taken in a **DB window**
  (lead-granted, single-tenant, about 15 min, on a `createdb -T` copy, **never the template**, Redis
  `-n 11`, `12` or `13`, never db 0, which is live, ending with the two quoted zeros), or T1's red is
  taken DB-free through FastAPI's validation with `model_validate` on `FactorCreate` (T2's form) and
  T1 is green-only. **The plan's choice: the DB-free red**, to spend no window. A3 then quotes T2's red
  and the gate's T1 green.
- **Docker, NFR VM:** nothing.

## Tasks

### SL-2026 — `FactorCreate.slug`

**The row.** WK-1178 fix slice. One `sonnet` executor. Requirements: `02` FR-83; `00` §4.3 (read);
FR-209 (read). Register: FD-1384 (MEDIUM), closing at the merge (A9). Depends on: the maintainer's GO; a
gate slot. **Size:** 1.5 h (triage 3 h: three of four members were done). SOLO gate about 2.5 h, not
counted. Merged before Thu 12 Nov 2026; still red at Wed 11 Nov 12:00 → the exception list.

**R0.** Re-read every cite at the base. Sweep the helper arguments for a slug outside the grammar.
Add to `02`'s `POST /api/v1/factors` row, under `spec-change`, dated, citing this plan: "A slug outside
the Factor pattern (`00` §4.3) is refused: 422 `VALIDATION_FAILED` naming `slug` (FD-1384). A stored
slug is never re-validated on read (FR-209)." Commit alone.

**R1 — red first.**

- **T2**, `packages/model-schema/tests/` beside the `Slug` tests (`git grep -n 'Slug' --
  packages/model-schema/tests` finds the file), `req("FR-83")`:
  `test_a_factor_create_refuses_a_slug_outside_the_factor_grammar`, parametrised on the five bad
  slugs and the two good ones, on a `TypeAdapter(FactorSlug)`. **Red:** `ImportError` is not the red,
  so first add the alias as plain `str`, see the bad slugs admitted, and quote that.
- **T1**, `backend/tests/test_api_models.py`, `req("FR-83")`:
  `test_a_factor_slug_outside_the_grammar_is_a_422_naming_the_field`.
- **T3**, same model-schema file: `test_a_stored_factor_slug_is_not_revalidated_on_read`, a guard.

**R2 — green.** `refs.py`: `FactorSlug = Annotated[str, Field(pattern=rf"^{_FACTOR_SLUG}$")]`, added to
`__all__`. `api/models.py:211`: `slug: FactorSlug`. Regenerate the contracts, one commit with the code.

**G.** Full code gate, both halves, SOLO. CI set from the three-dot diff: `python`, `docs`, `frontend`
(the contract path), `history-policy`. No migration.

### Write set

- `packages/model-schema/src/model_schema/refs.py`, `backend/src/app/api/models.py`.
- `packages/model-schema/tests/` (one file), `backend/tests/test_api_models.py`, any fixture A8 names.
- `docs/specs/02-modelling.md` (the one row), `docs/contracts/openapi/generated.json` (generated),
  and any generated file `generate-contracts.py` writes for the same change.
- LG-2027 under `docs/ledgers/`.
- At the mint: the SL-2026 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, FD-1384's
  essay and `docs/findings/register.md` (A9).

### Files shared with other groups

**LAST-1 (FD-1337):** `docs/contracts/` and `packages/model-schema`. Serial: C before LAST-1 by the
order; the second re-generates, never merges generated text by hand. **Safe in parallel with D, R, A,
T, H, F.**

## Hand-off (not this plan's writes)

The GO: the maintainer. The row, the mint, the gate slot: the lead. The LG: the executor. A9: the
auditor. **For the lead:** FD-1799's register row is the source for the essay's closing paragraph.

## Self-review

1. **Every cite was read** at `dae9637e`. 2. **Requirements by id**, no range. 3. **No placeholder.**
4. **The triage is corrected:** SL-1806 did Banding and Grouping (`8db3e1e1`), `RatingVersionCreate` is
typed, so the row is 1.5 h. 5. **The brief's "spec text first"** is R0. 6. **The red is by cause**, DB-free,
and A3 says which test carries which half. 7. **Calendar:** 12 Nov 2026 is a Thursday, 11 Nov a Wednesday.
