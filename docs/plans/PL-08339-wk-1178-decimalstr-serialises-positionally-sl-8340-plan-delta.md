---
id: PL-8339
family: plan
kind: map
title: WK-1178 — DecimalStr serialises positionally, so a value cannot violate its own schema and a governed hash does not follow spelling (FD-1337), SL-8340 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8339
owner: planner
tree: dae9637ea6f6a56f6502e9db70392cdfb2f3983d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1337, RL-1329, RL-1343, FR-10, FR-21]
---

# PL-8339 — WK-1178: `DecimalStr` serialises positionally (SL 8340, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds one slice row, SL 8340, and edits no filed plan.
> The executor's skills are `superpowers:test-driven-development`, `.claude/skills/python-test`,
> `.claude/skills/python-package`, `.claude/skills/contract-schema`, `.claude/skills/contract-guard`,
> `spec-change` and `git-hygiene`. PL 8339, SL 8340 and LG 8341 are working ids reserved by the lead.

## Authority

- **The user's decision.** The maintainer's entry "2026-11-05 09:58:58 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`: "ALL 24 FIX-BEFORE-FREEZE rows AND FD-1337 (7 h) AND
  FD-1484 (8 h) are coded and merged before Thu 12 — the two are no longer carried"; "then FD-1337 /
  FD-1484" last in the order. This **replaces** item (8) of "2026-11-05 09:51:53 GMT", which carried
  them.
- **The hash rule, closed, verbatim** ("2026-09-30 17:15:31 BST"): "**The zero count sets the fix, not
  the severity:** with 0 committed and 0 stored instances, fix it NOW without a hash-version bump. **The
  fix commit re-measures the count** (tracked blobs, the PostgreSQL DBs, **and MinIO**, which the FD did
  not measure) and records 0 as the reason no migration is needed. If any instance appears at fix time,
  it bumps the `suite_content_hash` version."
- **The second clause, closed, verbatim** ("2026-09-30 17:20:19 BST"): "**Add to the fix commit's
  re-measure:** audit-event writers were spot-checked, not swept. The fix sweeps every DecimalStr write
  path it touches, or states which paths it measured."
- **The severity's two properties** (17:15:31): the serialiser "emits strings its **own published JSON
  Schema pattern rejects**", and "a governed hash (`suite_content_hash` …) depends on spelling, so equal
  values hash differently".
- **The essay leaves two decisions to this plan:** "(a) **whether `DecimalStr` itself changes or a second
  type is kept**" and "(b) **whether to also normalise trailing zeros**". The brief names both.
- **The triage** (`b28ba8e9454c`): "Highest regression risk in this list."

## Goal

No `DecimalStr` value serialises to a string its schema refuses, and equal values in a governed hash have
one spelling. FD-1337 closes, by the rule above on whether the hash version moves.

## Evidence at `dae9637e`

Cites were read at `origin/main` `dae9637ea6f6a56f6502e9db70392cdfb2f3983d`. **Items marked RUN were run by
the planner** on tools-main's venv, read-only (`/tmp/plan-slices/p5.py`).

- `packages/model-schema/src/model_schema/money.py`: `_DecimalStrSchema` with the pattern
  `^-?[0-9]+(\.[0-9]+)?$`; `DecimalStr` with `PlainSerializer(str, …)`; `PositionalDecimalStr` with
  `format(v, "f")`, the same schema, and the comment "`DecimalStr` is left alone". `Relativity` follows.
- **The essay's reach is out of date. It has more than doubled.** `git grep -n -E
  ':\s*(tuple\[|list\[)?(DecimalStr|Relativity)\b' origin/main -- packages/model-schema/src`, without
  `money.py`: **29 lines** at this tree, against the essay's 13: new in `approvals.py`,
  `dislocation.py`, `modelling.py:382-383`, `perils.py:329`, `rating.py:135-137,1389-1407`.
- **What reaches a hash (RUN).** A walk of each root's annotated fields for a `str` `PlainSerializer`:

| Root | `DecimalStr` fields reachable |
|---|---|
| `RegressionSuiteContent` | `MonotoneInInput.lower`, `.upper` |
| `ModelSpec`, `QuoteContext`, `RatingAlgorithm`, `Factor`, `SubGraph`, `AuditEvent` | none |
| `Banding` | `BandingMinimums.min_exposure_per_band`, `OneWayRow.exposure_years` |
| `Grouping` | `OneWayRow.exposure_years` |
| `RatingVersion` | `ApproximationCheck.quantile`, `.observed_abs_change_pct`, `.max_abs_change_pct` |
| `RateTableVersion` | `UpliftTableParameters.percentage`, `UpliftByFilterParameters.percentage`, `FloorAndCapParameters.floor`, `.cap` |
| `PerilStructure` | `LargeLossTreatment.loading_factor`, `.restoration_loading`, `Reconciliation.tolerance`, `.imputed_share` |

  A field reachable from a root is **not** thereby in a hash: the hash sites must be read. `suite_content_hash`
  (`regression.py:220`) takes `model_dump(mode="json")`, so its two are in. `spec_hash`
  (`backend/src/app/platform/modelling.py:161`) hashes `ModelSpec`: none. `version_content_hash`
  (`platform/diff_cache.py:48`) hashes cells, `definition_hash` (`:61`) keys and value: not the
  operation parameters. **Left for R0:** `bundle_hash` (`rating/compile.py:676`), `platform/rate_tables.py:522,1351`,
  `model_schema/audit.py:102,131`, and any `sha256` a new artifact added since `32f3fa92`.
- **The pinned test.** `packages/model-schema/tests/test_money.py:133`: its docstring says "`DecimalStr` gives
  `1E-7`, `1.2E-28` and `1E+1`", the comparison that justified `PositionalDecimalStr`. It changes with this
  fix (A10).
- **The spec.** FR-10, FR-21 (`docs/specs/00-overview.md:234`). `RL-1343` fixes `dp` digits for a declared
  decimal output: those go through `round_to_text`, not `DecimalStr`, and `PositionalDecimalStr` keeps
  trailing zeros on the ladder's fields **on purpose**. A normaliser on that type would break `18.00`.
- **The contract.** `DecimalStr` and `PositionalDecimalStr` publish the same schema, so
  `generate-contracts.py --check` should show **no** diff. If it does, stop: something else changed.
- **The window's predicates are in the essay**, verbatim: `decexp.py`, `decexp2.py`, `decexp_ctl.py` and the
  per-table PostgreSQL predicate. It measured **81 databases, 3841 tables, 0 rows** and 1901 tracked files, on
  2026-09-30. **MinIO was never measured.** Nothing has been re-measured since.

## Decision points

For the maintainer, on the GO. Each is ruled before the slice starts.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-L1 | `DecimalStr` itself, or a second type? | (a) **`DecimalStr` itself:** its serialiser becomes `format(v, "f")`, and `PositionalDecimalStr = DecimalStr` is kept as an alias so no ladder import moves. One serialiser. (b) A second type kept, and every field moved to it: 29 edits for no semantic gain, and `DecimalStr` stays wrong for the next user. | **(a).** The schema promised this all along; RL-1329 kept the old serialiser only because the count was unknown, and this slice is the count. |
| DP-L2 | Normalise trailing zeros? | (a) **No, anywhere.** `66000.440` keeps its spelling. `10` and `1E+1` now agree, `10` and `10.0` still do not: the ruled second property is only partly closed. (b) **Everywhere:** one spelling per value, every positional value with trailing zeros changes bytes, and the ladder's `dp` digits forbid it on the alias. (c) **Only the two hashed fields:** `MonotoneInInput.lower` and `.upper` take a `CanonicalDecimalStr`, `format(v.normalize(), "f")`, so the one governed hash is a function of the value, and every other field keeps its spelling. | **(c).** It closes the ruled property at exactly the fields it names. It moves a stored suite's hash only if a stored `lower` or `upper` has a non-canonical spelling: so the re-measure counts that too (A3), and the ruled rule then decides the bump. |
| DP-L3 | The re-measure's corpus on a box of about 80 scratch databases. | (a) **Every database on the shared cluster, plus every MinIO bucket, read-only,** as the 2026-09-30 run did, with denominators and planted controls, in one single-tenant window. (b) Only the template and the demo database. Faster; not what was ruled. | **(a).** The ruling names the PostgreSQL DBs. About 30 min, plus the box's load. |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's merge
tree. Items 1 and 2 apply to this plan; A1 to A13 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing
   line except check 31 / check 32 lines naming working ids 8339, 8340 or 8341. After the mint,
   `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no
   line that stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only the Write set below.
- **A2. Spec first.** The `00` commit precedes the first code commit.
- **A3. The re-measure, in LG 8341, before the code commit:** tracked blobs (`decexp.py`, `decexp2.py`), the
  PostgreSQL databases and MinIO, at named times, each with its **denominator** (files; databases and tables;
  buckets and objects) and its **planted positive control seen to count** (a zero over an empty corpus is
  not a zero). Two counts: quoted exponent-form values; and, under DP-L2 (c), `lower` or `upper` values
  in `regression_suites` with a non-canonical spelling.
- **A4. The rule is applied.** If both counts are 0: no version bump, and the LG and the commit say so,
  citing A3. If either is above 0: `suite_content_hash` gains a version, on the `spec_hash` precedent, as
  ruled, and the slice stops first to tell the lead what was found.
- **A5. The hash sweep.** LG 8341 lists every `sha256` site in `backend/src` and `packages/*/src`
  (`git grep -n -E 'sha256|_canonical_sha256' -- backend/src packages/model-schema/src
  packages/pricing-core/src`), and whether a `DecimalStr` reaches it. The audit-event writers are
  swept, as ruled: each `audit.record` passing a dumped `DecimalStr`-bearing shape, or a statement of which
  paths were measured.
- **A6. Red first, by cause.** LG 8341 quotes T1's red (`'1E-7'` against the schema's pattern) and T2's (two
  equal values, two hashes).
- **A7. The schema holds.** T1 green: for `0.0000001`, `1.2E-28`, `1E+2`, `Decimal(100).normalize()`, `10`,
  `66000.440`, every field type's dump matches the published pattern. A Hypothesis property over decimals
  if `.claude/skills/testing-strategy`'s form fits; else the table.
- **A8. Spelling and the hash.** T2 green: `10`, `1E+1`, `10.0` give one `suite_content_hash`, and T3: a
  non-hashed `DecimalStr` field keeps `66000.440`.
- **A9. Every other hash is unchanged.** `git diff origin/main...HEAD --stat -- docs/contracts` is empty, and
  `generate-contracts.py --check` rc 0. `backend/tests/test_contracts.py` is green (`contract-guard`).
- **A10. The ladder is unchanged.** Every existing test of `PositionalDecimalStr` passes, unedited.
  `test_money.py:133`'s docstring and any assert that pinned the old exponent form change, and the LG lists
  each. **The lead's adoption of this plan is the OK of common seat brief item 13 for that test only.**
- **A11. No pandas, no float.** `format(v, "f")` on `Decimal` only.
- **A12. The GREEN set and the gate.** `model_schema.money` is under most of the tree, so **the GREEN set is
  the suite: the SOLO full gate at the re-merged head, before the PR**, both halves, every rc quoted. The
  demo stage is part of it. A golden or fixture that moves is a stop, not an update.
- **A13. FD closing act in the FD-1842 form, in the slice's own PR, by the slice's auditor:** FD-1337's
  `status: closed`, `relates:` gaining the slice's ids, a `***Resolved <date>***` paragraph naming the
  remedy, the red, the LG and A3's counts, the same on the register row, and the PR number and squash at
  the merge's date of record. **The LG Audit section, with the lead's
  adoption, lands in the audit's own commit**, and `docs/INDEX.md` is regenerated after the closing acts
  (common seat brief, item 17).

## Global Constraints

- **G1. The hash rule is the maintainer's** and is applied, not reinterpreted.
- **G2. Nothing stored is rewritten** (FR-4). A reader of an old `1E-7` row still parses: `Decimal` accepts it,
  and validation is unchanged. The change is on output only.
- **G3. The input side is unchanged.** A `DecimalStr` still accepts `"1E-7"` on input. The schema's pattern
  governs what is published, and tightening input is not this finding.
- **G4. Contract flows one way** (`CLAUDE.md` §2). `docs/contracts/` is generated, never hand-edited.
- **G5. This slice is last in the chain, and it re-merges after C.** C adds a `refs.py` alias and regenerates
  the contracts. There is no field overlap.
- **G6. Red first, by cause. No test is weakened** beyond A10.

## Needs

- **A read-only measurement window, lead-granted in writing,** about 30 min, single-tenant (nothing else
  touches the shared server until its END line), no gate or timed stage beside it, load1 and `free -g`
  read at start. **No `createdb`, no write:** every session `BEGIN TRANSACTION READ ONLY` with
  `PGOPTIONS='-c default_transaction_read_only=on'`. The template is read and **never named by a URL
  anything writes to**. MinIO by `mc` inside `gi-pricing-minio-1`; a control object goes in a scratch bucket
  named for this slice, removed with `mc rb --force` (common seat brief, item 18), and `mc ls g/` quoted.
- **Redis:** none. db 0 is live and is not touched. **Docker:** `exec` only. **NFR VM:** nothing.

## Tasks

### SL 8340 — positional `DecimalStr`

**The row.** Last-1 in the 09:58:58 order. WK-1178. One `sonnet` executor. Requirements: `00` FR-10, FR-21.
Register: FD-1337 (MEDIUM), closing at the merge (A13). Depends on: DP-L1 to DP-L3 ruled; the GO; the window;
R and C merged. **Size:** 7 h (the triage's), including the window. SOLO gate about 2.5 h, not counted.
Merged before Thu 12 Nov 2026; still red at Wed 11 Nov 12:00 → the exception list.

**R0 — premises and spec.** Re-read every cite at the base. Read the hash sites the Evidence leaves open. Add
a dated clause to FR-21 (`00:234`) under `spec-change`, citing this plan: an exact decimal serialises in
positional notation, with no exponent, so every published value matches the type's pattern; the fields a
governed hash reads serialise one spelling per value. Commit alone.

**R1 — the re-measure (A3, A4, A5), in the window, before any code.** Save the essay's scripts to the slice's
own scratch, unedited but for the ref. Run them at the base. Add the `regression_suites` spelling predicate:
in each database, each `lower` and `upper` under a stored suite's `monotone` check, compare the text with
`format(Decimal(text).normalize(), "f")`. Plant a control for it too, in a `TEMP` table.

**R2 — red first.** `packages/model-schema/tests/test_money.py`, `req("FR-21")`:

- **T1** `test_every_exact_decimal_serialises_inside_its_own_schema`, the table of A7. **Red:** `'1E-7'` does
  not match.
- **T2** `test_equal_bounds_give_one_suite_hash`. **Red:** `sha256:b798…` against `sha256:6085…`, by the
  essay's fixture.
- **T3** `test_a_field_outside_a_governed_hash_keeps_its_spelling`. A control.

**R3 — green.** Under DP-L1 (a) and DP-L2 (c), in `money.py`:

```python
#: An exact decimal that crosses every boundary as a string, always positional, so every value
#: matches the published pattern (FR-21, FD-1337). Spelling is kept: `66000.440` stays. A float
#: is a validation error (`OQ-547`).
DecimalStr = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    PlainSerializer(lambda v: format(v, "f"), return_type=str, when_used="always"),
    _DecimalStrSchema(),
]

#: Kept for the ladder's imports (`RL-1329`): the same type since FD-1337.
PositionalDecimalStr = DecimalStr

#: `DecimalStr` with one spelling per value, for a field a governed hash reads (FD-1337).
#: `normalize` alone would give `1E+2`; `format` keeps it positional.
CanonicalDecimalStr = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    PlainSerializer(lambda v: format(v.normalize(), "f"), return_type=str, when_used="always"),
    _DecimalStrSchema(),
]
```

`Relativity`: the same serialiser line. `__all__` gains `CanonicalDecimalStr`. `regression.py:104-105`:
`lower` and `upper` take it. **Check `Decimal("0").normalize()` and `Decimal("0.00").normalize()`: both `0`,
and a signed zero is `-0`, which the schema's pattern admits.** Delete the "left alone" comment.

**R4 — the full-tree reds.** Fix what A10 names, and nothing else. **G.** A12, SOLO. CI set from the three-dot
diff: `python`, `docs`, `history-policy`, and `frontend` only if a filter matches.

### Write set

- `packages/model-schema/src/model_schema/money.py`, `packages/model-schema/src/model_schema/regression.py`.
- `packages/model-schema/tests/test_money.py`.
- `docs/specs/00-overview.md` (FR-21).
- LG 8341 under `docs/ledgers/`.
- At the mint: the SL 8340 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, FD-1337's essay and
  `docs/findings/register.md` (A13).

### Files shared with other groups

**C:** `packages/model-schema/` (a different file). **R:** `RATE_TABLE` operation parameters serialise through
`DecimalStr`, and R's own write helper is `rate_tables/operations.py`: no file in common. **Serial after R and
C by the order.** The code can be built beside any group; the **window and the gate are serial with all**.

## Hand-off (not this plan's writes)

- DP-L1 to DP-L3 and the GO: the maintainer. The window and the gate: the lead. The LG: the executor. A13: the
  auditor.
- **If A4 finds an instance:** the bump is ruled in advance, but it is a stop, because a stored suite whose hash
  is pinned as evidence (`rating_versions.py`, `evidence.golden_quotes.suite_content_hash`) needs a read
  before the slice carries on.
- **If time runs out,** this is the triage's natural next exception: the maintainer's call at Wed 12:00.

## Self-review

1. **Every cite was read** at `dae9637e`; the marked walk was run. 2. **Requirements by id**, no range. 3. **No
placeholder.** 4. **The rulings are verbatim,** and the 09:58:58 entry's replacement of (8) is stated. 5. **The
essay is corrected:** 29 lines, not 13; two more roots are named for R0's read. 6. **Both open choices are DPs,**
as the brief asks. 7. **Calendar:** 12 Nov 2026 is a Thursday, 11 Nov a Wednesday.
