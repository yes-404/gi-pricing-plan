---
id: LG-1396
family: ledger
title: WK-1178 slice SL-1377 — the FD-1357 fix, one seeded rate table per Factor (RL-1361), the seed request and 201 typed, a re-seed's own origin, the factor reference's slug grammar (RL-1383) (PL-1376)
status: closed
created: 2026-10-03
owner: executor
tree: fa151110e1ba751d5593bfc24809918ef3377013
phase: P2
work: WK-1178
slice: SL-1377
plans: [PL-1376]
corrected_by: []
relates: [RL-1361, RL-1375, RL-1383, FD-1357, FD-1384, RL-1263, FR-9, FR-228, FR-229, FR-230, FR-234, FR-451]
---

# LG-1396 — WK-1178 slice SL-1377, the FD-1357 fix

Executed from `PL-1376` by `executor-1377b` (sonnet, medium: `echo $CLAUDE_EFFORT` printed `medium`), resuming
the first executor's WIP `f08fa07e` (Tasks 1 and 2) after it stopped on a premise defect that `RL-1383` ruled
(option A). Branch `sl-1377-fd-1357-multi-factor-seed`. Stamps are BST (`TZ=Europe/London date`).

The executor charter's Model / effort line, verbatim: "`sonnet` (currently Sonnet 5); medium, inherited from the
lead — the highest-volume role; per-slice gates and the auditor's re-check bound the risk of a cheaper setting."

## Tasks

### Task 0 — preconditions

**Bases.** Resumed 2026-10-03 at about 19:00 BST. `origin/main` was `cf074d20` (#1084, RL-1383 and FD-1384
minted) when the WIP branch took it in (merge `e786ef60`, no conflict). `origin/main` then moved to `7b7757b3`
(#1085, docs only: PL-1267 activation, roadmap) and was merged in the same way (no conflict). Base tree at the
last merge: `fa151110e1ba751d5593bfc24809918ef3377013`.

**Dispatch record, FINAL, quoted verbatim** (`gi-pricing-plan.local/handover/DISPATCH-WK-1178-SL1377-2026-10-03.md`,
as read 2026-10-03 at the start of this resume; it includes Delta 3):

```text
# Dispatch record: WK-1178 slice SL-1377, the FD-1357 fix (multi-factor seeding per RL-1361, the seed route typed), from PL-1376 (FINAL)

**Status: FINAL** (2026-10-03 17:20:27 BST, the lead, after #1080 merged as d672f991; tree 33cbff79). *Earlier status line, kept:* DRAFT (the lead, 2026-10-03). Lane B. It goes FINAL on the maintainer's GO check and the activation PR's merge. PL-1376 is frozen from its first merge (#1078, 58c7f5e8), except its status line; every delta lives here.

**The order:** PL-1371 §5 (lane B: "FD-1357 fix" first, G2's chain); the maintainer's lane-B order ("SL-1360 → FD-1357 fix → FD-1356 fix → …", entry "2026-10-01 10:10:32 BST — WK-674 S2 currency audit: ORDER AMENDED to (b) …"); the preparation GO "2026-10-03 16:53:10 BST — GO planner-1376act …", which lists what this record must include.

## Plan and slice status on main (the GO check, FIRST)
- Main at drafting: 58c7f5e8 (#1078). PL-1376 `draft`, SL-1377 `draft`; both flip to `active` in the activation PR (planner-1376act, draft).

## Activation needs (PL-1376 "Activation needs, in order"), run
1. SL-1360 merged: `git log --oneline origin/main | grep -m1 SL-1360` → `d8537220 … (#1049)`. **Met.**
2. RL-1375 (DP-1 to DP-4) minted, `status: active`. **Met.**
3. DP-5 (a) and DP-6 (a) decided: the maintainer's entry "2026-10-01 10:24:27 BST — The clock correction acknowledged …", item (4). **Met.**
4. PL-1376 and SL-1377 minted; no working ids 9757/9764/9763 left in PL-1376 (grep count 0). **Met.**
5. Task 0 premises (a)–(m) and the RL-1361 find-string counts at 58c7f5e8: **MET** — premises (a)–(m) all hold; every RL-1361 find block counts 1 and every replacement 0 (planner-1376act, handover/activation-needs-1376-2026-10-03.md; re-run by the lead with handover/activation-needs-1376-findcount.py, same counts). The executor re-runs them in Task 0 at its own base.
6. PL-1364 is `draft` at 58c7f5e8, so **Acceptance 10 Case A** applies (planner-1376act, same file). File overlap with FD-1335 Part A (PL-1364): `backend/tests/test_contracts.py` (different definitions) and `docs/specs/03-rating-engine.md` (different rows); PL-1364 comes after this slice in lane B, and the second to merge re-gates.
7. The maintainer's agreement and the lead's go, in the activation PR: **MET** — "2026-10-03 16:59:11 BST — DISPATCH GO: the FD-1357 fix (SL-1377, PL-1376; WK-1178) on lane B; this entry is PL-1376 activation need 7's maintainer agreement"; the lead's go 2026-10-03 16:59:55 BST in #1080's squash body (main d672f991).

## Decision points: every one has a resolver
- DP-1 to DP-4 → RL-1375 (active). DP-1 (a2): the seed baseline resolves to the seed origin.
- DP-5 (a): this slice lands `factor_ref` (and T1, T5) before WK-673 Slice 7. DP-6 (a): the hardening is in, 422 `VALIDATION_FAILED`, no `UPPER_SNAKE:` prefix.
- **No task is held.**

## Holds (holds-2026-10-01.md)
- **FD-1366 per-route hold: case (ii).** This slice EDITS the seed-from-model handler, so it types the body in the same slice (`SeedFromModelRequest`, Acceptance 6) and removes the route's `UNTYPED_REQUEST_PENDING` entry in the same commit. Its merge lifts rule (i) for `POST /rate-tables/{slug}/seed-from-model`.
- FD-1335 /score hold: not applicable (no /score route). FD 9752 hold: not applicable (no approval response read).

## Conditions
1. **Write set:** exactly PL-1376 "Write set" table (model-schema rating.py + __init__.py; pricing-core rate_tables/operations.py; backend platform/rate_tables.py + api/rate_tables.py; scripts/generate-contracts.py; regenerated docs/contracts/; docs/contracts/openapi/gi-pricing.yaml (T8); docs/specs/03-rating-engine.md (T1, T2, T4, T5, T7, T9 and RL-1375's texts); backend/tests/test_contracts.py; the four test files; scripts/audit-docs.py registry; tests/test_audit_docs_ids.py count; conditionally .claude/skills/contract-schema/SKILL.md; its ledger; INDEX). Nothing under frontend/.
2. **Lanes (RL-1263):** lane A runs WK-675 (frontend/ + its ledger + INDEX); no shared non-exempt file. Different Works. If lane A's gate overlaps this slice's gate, it is a candidate contention pair: both ledgers record both walls, uptime/free at start and end, and the other holder via flock -n.
3. **The F1 contract-registry serialisation with WK-674 S2 (PL 9765):** `_CONTRACT_ARTIFACT_PATHS` in scripts/audit-docs.py and `tests/test_audit_docs_ids.py`'s count are shared. Whichever merges second re-bumps (N measured at its own base, recorded with the SHA in its ledger). Whichever merges first writes the contract-schema skill step (PL-1376 write-set row, conditional).
4. **RL-1375 DP-1 (a2) order versus WK-673 Slice 7:** this slice first. Slice 7 is not dispatched while this slice is open (shared: RateTableKey, operations.py, platform/api rate_tables.py, the test files).
5. **Typed both ways:** `SeedFromModelRequest` (request) and the 201 `RateTableVersion` (response, generated slug per DP-4) are generated `model-schema` shapes; the maintainer checks request AND response typing at the ACK.
6. **Spec texts byte for byte** (Acceptance 9): every find string and count copied from RL-1361's and RL-1375's fenced blocks; red before the edit, the counts pasted.
7. **Gate evidence for every suite-level run:** clean checkout of the named SHA, porcelain empty; `uv sync --all-packages`; `ruff check --no-cache`; `mypy --no-incremental`; the dev-commands slot wrapper verbatim plus `LOKY_MAX_CPU_COUNT=4`; uptime and free -h at start and end; the other holder via flock -n; the test DB created first; read the stage table, never the exit code. A gate slot is granted by the lead.
8. **migrate --verify**, if run, only in CI's form (`--ref <meta.verified_against_tree> --record-ref HEAD`).
9. **Red first** on every acceptance item, outputs pasted.
10. **Ledger:** LG working id **9744** (allocated by the lead 2026-10-03 17:20:27 BST; free-checked on origin refs, worktrees and handover), allocated by the lead at GO; append-only; BST stamps; Task 0 quotes this FINAL record verbatim.
11. **Frozen records:** nothing in docs/plans/, docs/rulings/ or any frozen body edited; spec text only as RL-1361/RL-1375 carry it verbatim with placement, in the enforcing commit.
12. **Executor:** a fresh `executor-1377` from `.claude/roles/executor.md`, sonnet, in a new worktree from origin/main after the activation PR merges. It never `cd`s.

## Deltas
- **Delta 1, 2026-10-03 16:58:23 BST (lead): PL-1364 :140 is wrong as written.** It says PL-1364 and this slice "share no file this slice edits"; both write sets edit `backend/tests/test_contracts.py` and `docs/specs/03-rating-engine.md` (found by planner-1376act at 58c7f5e8). PL-1364 is frozen, so the correction lives here: the overlap is definition- and row-disjoint, PL-1364 follows this slice in lane B, and the second to merge re-gates. Not blocking.
- **Delta 2, 2026-10-03 17:20:27 BST (lead): FINAL.** GO "2026-10-03 16:59:11 BST — DISPATCH GO …"; MERGE-ACK "2026-10-03 17:19:33 BST — MERGE-ACK #1080 …". **Main = d672f991** (PL-1376, SL-1377 `active`). Lane A at this moment: executor-1369m re-gating SL-1369 (WK-675) on a gate slot; this slice builds first, and its gate slot is granted by the lead with the other holder recorded (candidate contention pair if they overlap). Executor: **executor-1377**, sonnet, from `.claude/roles/executor.md`, a fresh worktree from origin/main d672f991. Note for new rows (the maintainer, 17:19:33): no status word restated in row prose (RFC-756).
- **Delta 3, 2026-10-03 17:59:12 BST (lead): RL-1383 (RL 9743) — the factor_ref slug grammar; executor-1377 STOPPED on it (f08fa07e WIP).** The ruling's own delta text follows verbatim (RL-1383 §"The effect on PL-1376", at #1084 @ea20e3d3, lines 294-354), with only its two placeholders filled (`<date of append>` → 2026-10-03; `RL-NNNN` → RL-1383). It takes effect when #1084 merges; executor-1377b resumes from f08fa07e after main is merged in. FD-1384 (Factor.slug grammar) is NOT discharged by this slice (option (a), a later WK-1178 item).

    **Delta 2026-10-03 — RL-1383 (the factor_ref slug grammar; filed as RL 9743).**
    Write set, added:
    - packages/model-schema/src/model_schema/refs.py — `_FACTOR_SLUG`; `REF_PATTERN`, `_REF_RE`
      and the per-type slug check; the `mode="after"` check on `ArtifactRef` (RL-1383 Ruled
      items 1–2). Shared with: any slice editing refs.py (none found at d672f991). Serialises.
    - docs/contracts/schemas/common/artifact-ref.schema.json — T-F. Hand-authored, not
      registry-exempt: serialises.
    - docs/specs/00-overview.md — T-C (ID-3 row), T-D (§4.3 note). Serialises with any slice
      editing ID-3 or §4.3.
    - docs/specs/02-modelling.md — T-E (§4.1). Serialises with any slice editing §4.1.
    - packages/model-schema/tests/test_refs.py — Acceptance 18 appended.
    Write set, widened:
    - backend/tests/test_contracts.py — the parametrize list of
      test_authored_pattern_accepts_exactly_what_the_parser_accepts gains Acceptance 17's
      cases (an edit to an existing definition: serialises, as the ONE_SIDED_SLUGS edit does).
    - packages/model-schema/tests/test_rate_tables.py — Acceptance 16 appended.
    - backend/tests/test_api_rate_tables.py — Acceptance 19; Acceptance 4's Factor slug
      contains `_`.
    - packages/pricing-core/src/pricing_core/rate_tables/operations.py — the seed refuses an
      out-of-grammar Factor slug (RL-1383 Ruled item 3).
    - docs/contracts/ generated files — regenerated (already in the write set).
    Acceptance, added (each red first, as the plan's standard requires):
    16. A key bound to an underscore Factor survives a re-read (FR-228). In
        test_rate_tables.py, test_a_factor_ref_with_an_underscore_slug_round_trips: a
        RateTableKey with factor_ref factor:veh_brand@1, and a RateTable holding it, each equal
        their own model_validate(model_dump(mode="json")). Red on f08fa07e: ValidationError,
        "not a valid artifact reference".
    17. The published pattern and the parser agree per type (FR-9). The parametrize list gains
        ("factor:veh_brand@1", True), ("factor:driver_age_banded@3", True),
        ("model:motor_gb@1", False), ("banding:driver_age@1", False),
        ("factor:Veh_brand@1", False), ("factor:x@1", False). Red on d672f991: the two True
        cases fail.
    18. A reference that can be built can be re-read (FR-9). In test_refs.py, after a positive
        control (ArtifactRef(type="factor", slug="veh_brand", version=1) constructs, and
        ArtifactRef.parse(str(ref)) equals it), each of ArtifactRef(type="model",
        slug="motor_gb", version=1), ArtifactRef(type="factor", slug="veh brand", version=1)
        and ArtifactRef(type="widget", slug="x-y", version=1) raises ValidationError. Red on
        d672f991: all three construct.
    19. Through the route, nothing 500s on an underscore Factor (FR-230). After a seed of
        Factor driver_age_band, GET /api/v1/rate-tables/{slug}@1/export/csv answers 200, and
        Acceptance 4's re-seed into that lineage answers 201 with factor_ref
        factor:driver_age_band@2. A seed binding a Factor whose slug is outside the factor
        grammar (`Region`) answers 422 VALIDATION_FAILED naming the slug. Red with Tasks 1–3
        and no refs.py change: the export answers 500 (_to_version,
        platform/rate_tables.py:557), and the `Region` seed answers 201.
    Acceptance 9 covers T-C, T-D and T-E as append/insert texts (anchor 1, text 1 after; text
    0 before) and T-F as a replace text (find 1→0, replacement 0→1), counted with grep -cF
    over the named file. Placeholders filled: <fix date>, <RL id> = RL-1383, <FD id> = FD 9742's
    minted id.
    Unchanged: Acceptance 1–15; RL-1361 T1–T12 and RL-1375 T-A/T-B, byte for byte.
```

**Premises (a) to (m), re-run** with `python3 /tmp/sl1377_premises.py` (`git show origin/main:<path>` plus a
line match) at `7b7757b3`; the three source files it reads are unchanged since `cf074d20`:

- (a) `operations.py:232`, `:289`, `:327` index `row[key]` for every declared key: reproduces FD-1357 (the base
  red below answers 500 with `KeyError`).
- (b) `api/rate_tables.py:57` `_seed_body(body: dict[str, Any])`, `:120`/`:157` `body: dict[str, Any]`, `:145`
  `return version.model_dump(mode="json")`: reproduces.
- (c) `platform/rate_tables.py:162` `seeded_from=result.seeded_from`, `:150` `current_version + 1`: reproduces.
- (d) `git grep -n "seed-from-model\|seedFromModel" origin/main -- frontend/src`, generated excluded: prints nothing.
- (f) `RateTableKey` at `rating.py:662-669`: `extra="forbid"`, `name`, `type`, `banding_ref` only. Reproduces.
- (h) `test_contracts.py:92` `"rate-table": "shipped in model-schema, never compared — register F27"`. Reproduces.
- (j) `load_factors` at `platform/modelling.py:284`. (k) `Factor.slug: str` at `modelling.py:133`.
- (m) `platform/rate_tables.py:440` `RateTableVersionRow.seeded_from.is_not(None)` in the seed branch. Reproduces.
- (g), (i), (l), (e): (g) `ls docs/contracts/schemas/generated` printed 33 schema files before this slice and 35 after;
  (i) is the count table under Task 4; (l) is fixed by the fixture change below; (e) every seed call is migrated (item 11).

**Acceptance 10 case.** Case A: `PL-1364` is `draft` (`status:` line 6 of its file) and `grep -rn UNTYPED_REQUEST_PENDING
backend/tests scripts | wc -l` prints 0, so this slice adds no guard entry and removes none. After this slice merges,
`PL-1364`'s Task 0 drops the seed-from-model entries (the lead carries that to its dispatch record).
**DP-5 outcome:** (a) as ruled. This slice lands `factor_ref`, so it applies `T1` and `T5`.

**Contract registry (Condition 3).** `PL 9765` (WK-674 S2) has not merged on `origin/main` (`git log origin/main --oneline |
grep -i "9765\|WK-674 Slice 2"` shows only WK-674 Slice 2a and a roadmap commit, neither adding a generated schema). So this slice
merges first and writes the `contract-schema` skill step (below).

### Task 1 — model-schema (the WIP's Task 1, plus RL-1383)

`RateTableKey.factor_ref`, its validator and `SeedFromModelRequest` were the first executor's WIP and are unchanged.
**Re-verified against `RL-1383`:** the WIP's model-schema tests used hyphenated Factor slugs (`driver-age-banded`), which
dodged the defect. They now use the real underscore slugs (`driver_age_banded`, `driver_age`). New, red first:

- Acceptance 16, `test_rate_tables.py::test_a_factor_ref_with_an_underscore_slug_round_trips`. Red on `f08fa07e`'s refs.py
  (the unmodified `origin/main` one): `ValidationError`, "not a valid artifact reference".
- Acceptance 18, `test_refs.py::test_a_reference_that_can_be_built_can_be_re_read`. Red on the unmodified refs.py: it fails
  at the positive control, `ArtifactRef.parse("factor:veh_brand@1")` -> `ValueError: 'factor:veh_brand@1' is not a valid
  artifact reference`, before the three construct-and-expect-refusal cases run (those three construct today, as the
  delta says; they are not reached). Green after the change: the three raise `ValidationError`.
- Acceptance 17, `backend/tests/test_contracts.py::test_authored_pattern_accepts_exactly_what_the_parser_accepts`: the six
  cases appended. Red before the change: the two True cases fail (`factor:veh_brand@1`, `factor:driver_age_banded@3`).
  The three red tests together printed `4 failed, 11 passed` (one each for Acceptance 16 and 18, two for 17).

`refs.py` (RL-1383 Ruled items 1 and 2): `_FACTOR_SLUG`, `REF_PATTERN` built from the two slug constants (its value is the
ruling's pattern, `grep -F` of T-F's replacement against the generated schema below), the per-type slug check (a public
`slug_is_admitted`, added to `__all__`: the pricing-core seed needs the same predicate and must not copy the regex), and a
`mode="after"` validator on `ArtifactRef`. T-F is applied to the hand-authored `artifact-ref.schema.json`
(find 1 -> 0, replacement 0 -> 1, counted with `grep -cF` over the file; printed `1 0` before the edit).

**Blast radius (RL-1383 Ruled item 2).** The ruling measured 51 `ArtifactRef(` sites with no literal slug containing `_`,
an upper-case letter or a space. The first run after the change found **one test site** that built an invalid reference:
`packages/model-schema/tests/test_rate_tables.py::TestRateTableShape::test_rate_table_key_with_banding_ref` built
`ArtifactRef(type="Banding", ...)` (capital `B`, not an artifact type), which the new check refuses. It is a test, not a
source site, so the ruling's stop condition ("outside the tests") does not fire. Fixed in the test (`type="banding"`); the
check is not weakened. No source site failed (the source sites build from stored slugs and constants; listed by
`grep -rn "ArtifactRef(" --include=*.py backend/src packages/*/src examples scripts`).

### Task 2 — pricing-core (the WIP's Task 2, plus RL-1383 Ruled item 3)

The pure seed per Factor, the hardening (`row N lacks declared key 'k'`) and their tests were the first executor's WIP and
are unchanged; its tests already used underscore slugs for the pure `Factor`. New, red first:
`test_rate_table_operations.py::test_a_pinned_factor_slug_outside_the_factor_grammar_is_refused_by_name` (`Region`, `x`,
`veh brand`, after a positive control with `veh_brand`). Red: 3 failed (a `ValidationError` whose text does not contain
"outside the factor slug grammar"). The seed now raises a plain-prose `ValueError` naming the slug before it builds the key.

### Task 3 — platform and route

Reds were taken against the unmodified `origin/main` source (`git checkout origin/main -- backend/src packages/*/src
docs/contracts`, run, then `git checkout HEAD -- …` to restore), with the new tests and fixtures in place:
`17 failed, 29 passed` in `test_api_rate_tables.py`. The failing tests:

- `test_a_two_factor_model_seeds_one_table_per_factor`
- `test_a_factor_that_names_no_relativity_entry_is_a_422`
- `test_a_model_factor_id_that_resolves_nowhere_is_a_404`
- `test_a_seed_into_a_table_the_rule_refuses_is_a_422_naming_it[bound-to-other-factor]`
- `test_a_seed_into_a_table_the_rule_refuses_is_a_422_naming_it[unbound-other-name]`
- `test_a_seed_into_a_table_the_rule_refuses_is_a_422_naming_it[banding-ref]`
- `test_a_seed_into_a_table_the_rule_refuses_is_a_422_naming_it[two-keys]`
- `test_a_seed_into_a_table_the_rule_accepts_binds_the_key[unbound-same-name]`
- `test_a_seed_into_a_table_the_rule_accepts_binds_the_key[bound-to-same-slug]`
- `test_a_reseed_with_a_newer_version_of_the_same_factor_is_accepted`
- `test_a_factor_outside_the_factor_slug_grammar_is_a_422_naming_the_slug`
- `test_the_seed_route_publishes_a_typed_request_and_201`
- `test_the_seed_request_refusals_are_422_with_a_field_error[blank-note]`
- `test_the_seed_request_refusals_are_422_with_a_field_error[non-model-ref]`
- `test_the_seed_request_refusals_are_422_with_a_field_error[empty-factor]`
- `test_the_seed_request_refusals_are_422_with_a_field_error[unknown-field]`
- `test_against_seed_resolves_to_the_versions_own_seed_origin`

- **Acceptance 1:** `assert 500 == 201`; the request log carries `SanitisedError: KeyError` (FD-1357).
- **Refusal-order test** `test_approval_is_checked_before_the_factors_are_loaded` is green on the base for the wrong reason
  (nothing loads Factors there), so its red is shown on broken input: with `load_factors` moved before the approval check,
  `assert 404 == 422`. Restored.
- **Acceptance 14:** the old origin test's body, re-seeding v2 and v3, run under the new resolver (a temporary
  `backend/tests/test_tmp_a14.py`, deleted): `assert 0 == 2`. It is rewritten with derived v2 and v3 (`floor_and_cap`
  bulk operations; v1 1.92/1.41/1.12, v2 1.84/1.41/1.20, v3 1.84/1.50/1.20) under the same name and the same assertions
  (`@3`: 1 changed cell against `previous`, 2 against `seed`).
- **Acceptance 13** (`test_against_seed_resolves_to_the_versions_own_seed_origin`) is in the red list above.
- **Acceptance 15, the sweep.** `grep -n '"against": "seed"' backend/tests/test_api_rate_tables.py` now prints `:326`,
  `:559`, `:706` and the two new tests' `:1520`, `:1532` (line numbers moved with the helper block). `:326` is the rewritten
  origin test (updated). `:559` is `test_diff_seed_without_a_seed_origin_404s`: a direct-insert table with no seed,
  404 `RATE_TABLE_MISS` "No seed origin": **kept as it is**. `:706` seeds once: kept. `grep -n 'against="seed"'
  backend/tests/test_rate_tables_service.py` prints `:561`: seeds once and derives by import: kept.

**The platform.** `seed_from_model` takes `factor`, checks approval, then `load_factors`, then the pure seed, then
`RL-1375` DP-2's lineage rule (`_check_reseed_lineage`: 422 `VALIDATION_FAILED` naming the table slug and key names). It
reads the stored definition's raw `keys` (not `RateTable.model_validate`) so a legacy row cannot 500 the check. The route
takes `body: SeedFromModelRequest`, `_seed_body` is deleted, `response_model=RateTableVersion`, and the handler returns the
instance. **Acceptance 7's stop** (a suffixed component name): none. `grep -o '"#/components/schemas/RateTable[A-Za-z-]*"'
docs/contracts/openapi/generated.json` prints `RateTableVersion` once, with no suffix. The resolver's seed branch is
`RL-1375` DP-1 item 2.

**Fixtures.** `_seed_approved_model` (both test modules) inserts a `FactorRow` per relativity entry (get-or-create by
`(workspace, slug, version)`) and pins the ids in `GlmSpec.factors`; `_seed_body` gains `factor`. Every seed call names a
`factor`; `grep -rn "seed-from-model" backend/tests` shows no seed call without one except the two tests that omit or
corrupt it on purpose (item 6 and 6b).

**Generated shapes (RL-1375 DP-4).** `GENERATED_SHAPES` gains `rate-table-version` and `seed-from-model-request`;
`ONE_SIDED_SLUGS` gains the two reason strings, verbatim (the first needs `# noqa: E501`, since the ruling's string is
148 columns). `generate-contracts.py` wrote both schemas; `--check` exits 0 ("36 generated contracts match the models").
**F27(c) divergence note (DP-4 (a)):** the authored `docs/contracts/schemas/rate-table.schema.json` is not edited and not
compared; the generated `rate-table-version` now carries `factor_ref` on the generated side only. Owner: the
create-read-retire audit Work (register F27, CR-1167).

**The audit registry (RL-1375 amendments F1 and 10:45).** Red: `python3 scripts/audit-docs.py` with the two generated files
present and unregistered printed `FAILED (4)`, checks 30 and 35 on both files. Base count N: the unmodified
`tests/test_audit_docs_ids.py::test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts` passed on
the slice's tree before the registry edit (base `cf074d20` plus this slice's files, the two new schemas unregistered) with
the assert at `== 70` (so N = 70, and the unmodified test passes: LOW-b's stop does not fire). The
three `_CONTRACT_ARTIFACT_PATHS` lines were inserted after the `sub-graph-body` anchor (count 1), and the assert is now `== 72`.
Green: `audit-docs.py` "All checks passed", `uv run pytest -q tests/test_audit_docs_ids.py` 118 passed. (The new files must be
`git add`ed before the audit: untracked, the register entries read as stale. Written into the skill.)

**The skill step (Condition 3, conditional row).** This slice merges first, so it wrote the step into
`.claude/skills/contract-schema/SKILL.md` ("A new generated schema is a new file the audit must be told about", with a
`Verified` entry) and a pointer in `.claude/skills/docs-audit/SKILL.md`'s check-35 text, and refreshed the
`contract-schema` row of `.claude/skills/README.md`.

### Task 4 — the spec texts (Acceptance 9)

Every text was read from its ruling's fenced block by `python3 /tmp/sl1377_specs.py` (modes `count`, `apply`) and never
retyped; placeholders filled: `<fix date>` and `<first date>` = 2026-10-03, `<RL id>` = RL-1375 (T-A, T-B) or RL-1383
(T-C to T-E), `<FD id>` = FD-1384. `count` before the edit printed, for every text, anchor or find count 1 and text count 0
(T-A's first replacement line also counts 1 before, the heading line it keeps, as RL-1375's amendment LOW-a says; T-F's count
printed `1 0` before the edit, taken when it was applied with `refs.py`). After the edit: replace texts (T4a, T4b, T7, T8,
T9, T-A, T-F) find 0 and replacement 1; append and insert texts (T1, T2, T5, T-B, T-C, T-D, T-E) anchor 1 and text 1. A first
run of the script dropped each append anchor's own sentence (T1, T2, T-C); it was reverted (`git checkout` of the four spec
files) and fixed before anything was committed, so no committed text lacks its anchor.

| Text | File | Kind | Before (find or anchor / text) | After |
|---|---|---|---|---|
| T1 | `03` FR-228 row | append | 1 / 0 | anchor 1, text 1 |
| T2 | `03` FR-230 row | append | 1 / 0 | anchor 1, text 1 |
| T4 (two blocks) | `03` §4.2 JSON | replace | 1 / 0, 1 / 0 | 0 / 1, 0 / 1 |
| T5 | `03` §4.2 | insert | 1 / 0 | anchor 1, text 1 |
| T7 | `03` §5.1 | replace | 1 / 0 | 0 / 1 |
| T8 | `gi-pricing.yaml` | replace | 1 / 0 | 0 / 1 |
| T9 | `03` §5.2 | replace | 1 / 0 | 0 / 1 |
| T-A | `03` §4.2 | replace | 1 / 0 | 0 / 1 |
| T-B | `03` §4.2 | insert | 1 / 0 | anchor 1, text 1 |
| T-C | `00` ID-3 row | append | 1 / 0 | anchor 1, text 1 |
| T-D | `00` §4.3 | insert | 1 / 0 | anchor 1, text 1 |
| T-E | `02` §4.1 | insert | 1 / 0 | anchor 1, text 1 |
| T-F | `artifact-ref.schema.json` | replace | 1 / 0 | 0 / 1 |

`T3`, `T6`, `T10`, `T11` are Slice 7's and `T12` is a decision-maker's: not applied.

## Acceptance self-check

| # | Where | Result |
|---|---|---|
| 1 | `test_a_two_factor_model_seeds_one_table_per_factor` | red `500` (`KeyError`), green |
| 2, 3(a)-(d), 8 | pure tests in `test_rate_table_operations.py` (WIP) | green |
| 3(a), (b) route | `test_a_factor_that_names_no_relativity_entry_is_a_422` | red, green |
| 3(e), (e') | `test_a_seed_into_a_table_the_rule_refuses_is_a_422_naming_it` (4 shapes), `…_accepts_binds_the_key` (2) | red, green |
| 3(f) | `test_a_model_factor_id_that_resolves_nowhere_is_a_404` | red, green |
| 4 | `test_a_reseed_with_a_newer_version_of_the_same_factor_is_accepted` | red, green |
| 5 | `test_rate_tables.py` (WIP) | green |
| 6, 6b, 7 | `test_the_seed_route_publishes_a_typed_request_and_201`, `test_the_seed_request_refusals_are_422_with_a_field_error`, `test_the_seed_request_refuses_bad_bodies` (model-schema) | red, green |
| 9 | Task 4 table | counts as above |
| 10 | Case A | above |
| 11 | no seed call without `factor` | above |
| 13, 14, 15 | resolver | red (13, 14), green; sweep above |
| 16, 17, 18 | `RL-1383` delta | red, green |
| 19 | `test_a_reseed_with_a_newer_version…` (export 200, `factor_ref` `@2`), `test_a_factor_outside_the_factor_slug_grammar_is_a_422_naming_the_slug` | red (no export 500 observed on the unmodified base: the route 500s earlier, at the `KeyError`; the `Region` seed on the base is also a 500, not the delta's 201, because the base seed does not take `factor`), green |

On Acceptance 19's red: the delta says "Red with Tasks 1-3 and no refs.py change: the export answers 500 and the `Region` seed
answers 201". That configuration was not run as a separate state (the refs.py change was made before the route tests were
written). The two facts it names are covered by tests that pass now and by the Task 1 reds: the export read-back is
`RateTable.model_validate(version_row.definition)` (`_to_version`), the call that Acceptance 16 shows failing on an underscore
`factor_ref` before the change, and `Region` is outside `_FACTOR_SLUG` by the pricing-core red above.

## PRs

#1087 (draft), opened 2026-10-03 at head `6c86fb04`. Title: `fix(rating): SL-1377 — one seeded rate table per Factor, typed
seed request and 201 (WK-1178, PL-1376, LG 9744)`. Body carries the `BREAKING CHANGE:` text.

## Gate (Task 5), attempt 1 at `6c86fb04`

Slot granted by the lead 2026-10-03 19:39:38 BST (both `/tmp/slots/gate-*` free by `flock -n`, load 0.54, 28Gi available,
lane A running no build). Tree: `git rev-parse HEAD` = `6c86fb0489783176c927f51c9b413d919382a208`, tree
`1f9c5e77b46eb8ff9a5a077e357d2fca99070434`, `git status --porcelain` empty (the executor's own worktree on the branch at that
head, not a separate detached checkout). `uv sync --all-packages` ("Checked 116 packages"). Test database dropped and recreated
from the template (`createdb -T gipricing`), then `alembic upgrade head`, before the run. The dev-commands body, verbatim, with
`ruff check --no-cache`, `mypy --no-incremental` and `LOKY_MAX_CPU_COUNT=4` added, under `flock -n -E 99` and `timeout 3600`
(`/tmp/sl1377_gate.sh`). Start 19:40:19 BST, uptime load average 0.99, 1.10, 1.02; `free -h` 28Gi available. End 20:04:15 BST,
load average 1.82, 1.88, 1.60; 27Gi available. The other holder: none (the gate took the first slot, which `flock -n` had
reported free). Wall 23 m 56 s; pytest alone 1421 s.

| stage | result | detail |
|---|---|---|
| ruff | pass | exit=0 |
| mypy | pass | exit=0 |
| import_linter | pass | exit=0 |
| audit_docs | FAIL | exit=1 |
| req_coverage | pass | exit=0 |
| contracts | pass | exit=0 |
| pytest | FAIL | exit=1 |

`GATE: FAIL — 2 of 7 stages failed: audit_docs pytest`. pytest: 14 failed, 4610 passed, 3 skipped.

- **audit_docs** printed two findings. Check 31 (`gap in the full allocation between 1391 and 9744`) is the working id: it is red
  by design until the lead mints LG 9744. Check 32 (an unresolved slice id cited in the grep text) was this ledger's own
  defect, a citation of an id that is not a governed record, in the Task 0 `git log` grep text; fixed in the next commit
  (the grep now reads `WK-674 Slice 2`).
- **pytest:** 13 of the 14 are tests that run `audit-docs.py` over the real tree (`test_the_real_tree_passes_all_ten_checks`
  and 12 others in `tests/test_audit_docs_*.py`, `test_doc_index.py`, `test_register_lint.py`, `test_register_owed.py`,
  `test_repository_invariants.py`), and fail on the same check 31 and 32 findings. They cannot be green before the mint.
  The 14th is a real defect of this slice:
  `backend/tests/test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for`. Its `_SINKS` list
  names `("backend/src/app/api/rate_tables.py", "_seed_body", "str(exc)")`, and this slice deletes `_seed_body`
  (the typed `SeedFromModelRequest` replaces it). The assertion says "a sink that stores or logs an exception's text was
  added, moved or removed". The sink was removed, with its function; no sink replaced it (the refusals now come from
  FastAPI's request validation). Removed the three-line `_SINKS` entry. **This file is outside PL-1376's named write set**
  (Condition 1); it is a mechanical consequence of the deletion the plan orders, and is disclosed here for the lead.
  After the edit the file passes alone: `uv run pytest -q backend/tests/test_error_sinks.py` (rerun below).
- **Frontend half** (Condition 1: nothing under `frontend/`; the plan's Acceptance 12 lists it): not run in this attempt. The
  slice touches nothing under `frontend/`; `generate:api` would regenerate from the OpenAPI that changed, so the half is
  still owed on the final head.

Next: a new head (the two fixes above) needs a new grant, per S-13.

## Mint and close (2026-10-03, 20:16 BST)

Opened as working id 9744; minted 2026-10-03 as LG-1396, by the lead's GO-mint ("2026-10-03 20:15:00 BST — GO-MINT: SL-1377 (#1087 @b0203bca)"). `origin/main` was `ee584dccb89bbf8d34cf40ef9ec52e10a4145598` (#1086) at the mint; `python3 scripts/doc-id.py next` printed `1394` there. **Ids 1394 and 1395 are held by the WK-673 Slice 1 mint batch PR (draft, unmerged; its ruling and plan take them), so this ledger takes 1396**, as the lead ordered; `doc-id.py next` printed nothing above 1396. Until that batch merges, check 31 reports a gap at 1394 to 1395 on this branch alone (expected, not a defect of this slice). `origin/main` was merged into the branch (`docs/INDEX.md` regenerated with `python3 scripts/doc-index.py`, not hand-resolved). The ledger file was renamed from its working-id file name to its minted-id file name, its `id` and heading set to LG-1396, its status set to `closed`. The earlier text of this ledger that names working id 9744 or `LG 9744` is kept as written (the ledger is append-only).

Closed on the slice audit `audit-1377-2026-10-03.md` (the auditor's local handover file; verdict CLEAN, three non-blocking carried notes, range `origin/main...b0203bca`), adopted by the lead's verdict "2026-10-03 20:14:41 BST — LEAD VERDICT: SL-1377 slice audit CLEAN, adopted", and on the dispatch record `DISPATCH-WK-1178-SL1377-2026-10-03.md`, Deltas 1 to 5. SL-1377's roadmap row is set to `closed` in the same commit.

**Carry-forward, owner the lead (audit item (f), Case A):** the seed route's untyped request body (its `UNTYPED_REQUEST_PENDING` entry) is NOT removed by this slice, because `UNTYPED_REQUEST_PENDING` does not exist on `origin/main` until PL-1364. Its removal is deferred to PL-1364's slice and carried in that dispatch record. The slice does not close silently over it.
