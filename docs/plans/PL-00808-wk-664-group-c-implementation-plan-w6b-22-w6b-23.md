---
id: PL-808
family: plan
kind: leaf
title: WK-664 Group C Implementation Plan — W6b-22 + W6b-23
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-26
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-26-w6b-group-c.md
---

# WK-664 Group C Implementation Plan — W6b-22 + W6b-23

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the two decided open-question slices the manager batched as Group C — W6b-22 (OQ-649 (b)), W6b-23 (OQ-650 (c)) — on one branch, into one PR, with one CI pass.

**Architecture:** Two independent guard additions. W6b-22 makes one-sidedness *declared*: a slug present on exactly one of the authored/generated sides must be registered with a reason, and a compared constraint keyword present on one side at a shared field path must be registered too — anything one-sided and undeclared fails. The stale `peril-structure` comment is corrected. W6b-23 adds a revalidation sweep: a script that parses every stored artifact against today's models and reports what no longer reads, plus the `07` rule that a narrowing shape change is a migration event, not a model edit. Each slice lands as one commit — spec, code, tests and any contract regen together (`CLAUDE.md` §2).

**Tech Stack:** Python (`scripts/`, `backend/tests/test_contracts.py`), the JSON-Schema corpus under `docs/contracts/schemas/`, FastAPI + SQLAlchemy (the sweep reads the DB), `audit-docs.py` for the docs half.

**Spec:** Two decided open questions:
- `OQ-649` — **DECIDED 2026-08-26: (b)** — one-sidedness declared in a registry; anything one-sided and undeclared fails. The stale `peril-structure` comment fixes. F2 subsumes (the authored-keyword completeness check lands with the registry).
- `OQ-650` — **DECIDED 2026-08-26: (c) now** — a revalidation sweep parses every stored artifact against today's models and reports what no longer reads. 07 records the rule that a narrowing change to a stored shape is a migration event, not a model edit.

**Slice source:** `docs/plans/PL-00811-wk-664-the-slice-map-revised-a-third-time.md` §3 rows for W6b-22 and W6b-23; the manager's batching direction (Group C = W6b-22 + W6b-23, one branch, one PR).

**Highest ids:** No new requirement id is filed. W6b-22 amends no FR (the registry lives in the guard's tests and the `generate-contracts.py` comments). W6b-23 records a dated rule under `07` §3.3 Storage beside FR-416.

## Global Constraints

- `docs/contracts/` is generated and never hand-edited — except the **authored** tier under `docs/contracts/schemas/` (the specification tier) and the **hand-authored** `generate-contracts.py` comments, which this slice edits.
- The registry is **derived against the corpus, not narrated**: a declared slug that is no longer one-sided must fail (the `peril-structure` drift, in reverse), and a one-sided slug without a declaration must fail.
- OQ-651 (c) binds the `metric-certificate` entry: it is one-sided because nobody wrote the authored side, **not** because it is deliberate. Its registry entry records the OQ-651 trigger, never a claim of intent.
- The F2 keyword check compares only `_COMPARED_CONSTRAINTS` at paths where the **field** exists on both sides; a keyword on one side only is declared or fails.
- The revalidation sweep is read-only: it parses and reports, it never mutates a stored artifact.
- Both gate halves pass before a push. This PR touches `scripts/`, `backend/`, `docs/`; the Python, docs and frontend workflows run (frontend only because the generated client regenerates identically).
- ASD-STE100 prose. Code, identifiers and file paths stay unchanged.

---

## Findings (verified 2026-08-27 against origin/main 8b0977f)

**F1 (W6b-22). One-sidedness is narrated in unchecked comments, and one has already gone stale.** Five `generate-contracts.py` comments declare a slug generated-only on purpose; `peril-structure`'s (`scripts/generate-contracts.py:71-81`) is superseded — it gained an authored side in #133, and the comment records the drift as the worked instance behind OQ-649. The comment corpus is also incomplete: `dataset-split` and `problem-detail` are generated-only with no comment.

**F2 (W6b-22). The current one-sided slug census.** Measured at 8b0977f: **13 authored-only** (`approval-request`, `dislocation-run`, `dossier`, `gipp-check`, `money`, `monitoring`, `optimisation-run`, `provenance`, `rate-table`, `rating-algorithm`, `rating-version`, `regression-suite`, `scoring`) and **9 generated-only** (`backtest`, `custom-metric`, `dataset-lineage`, `dataset-split`, `metric-certificate`, `model-comparison`, `objective-usage`, `oidc-auth-config`, `problem-detail`). All 11 later-phase authored-only are deliberately one-sided; the 9 generated-only are first written forms, except `metric-certificate` (OQ-651 (c): authored by the next certificate workstream — a known gap, recorded as such).

**F3 (W6b-22, F2's keyword surface). 36 one-sided constraint keywords at 31 shared field paths.** Measured with a field-path walker that descends exactly as the suite's comparison does (cross-checked against `_constraint_map` output: 0 mismatches). All 18 `COMPARED_SLUGS` walked; no slug skipped. Representative rows: `banding.slug`/`grouping.slug`/`model.spec_hash` (`pattern`, contract only); `job.error.code`/`job.result.kind` (`pattern`, model only); `validation-report.results.[].offending_sample` (`maxItems`, contract only); `grouping.evidence.*_ci` (`minItems`+`maxItems`, model only). The five examples named in the OQ-649 finding all reproduce. The 2026-08-24 historical count was 18 over 15 slugs; the corpus has since grown to 18 slugs.

**F4 (W6b-23). Stored artifacts are whole JSONB columns, parsed back into model-schema models.** `validation_reports.body` → `ValidationReport`, `profiles.body` → `Profile`, `bandings.body`/`groupings.body` → `Banding`/`Grouping`, `transparency_artifacts.payload` → `TransparencyArtifact`, `diagnostics.payload` → `Diagnostics`, `peril_structures.perils`/`excluded_perils`/`reconciliation` → `PerilStructure`, `models.spec`/`models.fit_result` → the model-spec and fit-result adapters. The read paths already exist (`backend/src/app/platform/validation.py:153`, `profiles.py:86`, `transformations.py:71`, `transparency.py:37`, `diagnostics.py:33`, `perils.py:71`, `worker/model_handlers.py:199,661`). The sweep reuses each parse path.

**F5 (W6b-23). The 07 rule has a home.** `07` §3.3 Storage (`07-platform.md:106-117`) owns artifact bodies (JSONB) and the Alembic migration obligation (FR-416 at `:110`); the migration-event rule belongs beside it.

---

## Tasks

### Slice W6b-22 — the one-sidedness registry

**T1. The slug registry and its guard.**
- [ ] In `backend/tests/test_contracts.py`, add `ONE_SIDED_SLUGS: Final[dict[str, str]]` — all 22 one-sided slugs, each with a reason. Generated-only entries name the first written form (and `metric-certificate` names OQ-651 (c), not a claim of intent); authored-only entries name the later phase (Phase 2+).
- [ ] Add `test_every_one_sided_slug_is_declared`: compute `authored_only` and `generated_only` from the corpus (reusing the eligibility discovery — `_authored` plus a generated glob); assert `one_sided - declared == ∅` and `declared - one_sided == ∅` (a declared slug that gained the other side is stale, the `peril-structure` case in reverse).
- [ ] Add a mutation proof: a slug deleted from one side (or a declared slug given a fake other side) makes the new test fail.

**T2. The `peril-structure` comment correction.**
- [ ] In `scripts/generate-contracts.py:71-81`, replace the superseded "No hand-authored Phase-0 counterpart" sentence with a dated note: the slug is two-sided since #133 and is compared like any other; the declaration mechanism is now the registry in `backend/tests/test_contracts.py`, not these comments.

**T3. The F2 keyword check.**
- [ ] Add a field-path walker helper `_field_paths(document, node, base)` to `backend/tests/test_contracts.py` that returns `dotted path → compared-constraint-keyword set`, resolving allOf/if-then/`$ref` the way `_constraint_map` does (reuse `_variants`).
- [ ] Add `ONE_SIDED_KEYWORDS: Final[dict[tuple[str, str], frozenset[str]]]` — the 36 measured rows, keyed `(slug, dotted_path)`, values the one-sided keywords. A module comment records that the entries are deliberate one-sided bounds the corpus carried at 8b0977f; a side converging deletes the entry.
- [ ] Add `test_a_constraint_keyword_on_one_side_is_not_silent`: for every `COMPARED_SLUGS` slug, walk both sides; for every shared field path, a compared keyword on exactly one side must be in `ONE_SIDED_KEYWORDS`, else fail. The reverse direction also fails: an entry no longer one-sided is stale.
- [ ] Mutation proof: removing a keyword from one side of a both-sided schema (or adding a fresh one-sided keyword) fails the new test.

**T4. Gate.**
- [ ] `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q backend/tests/test_contracts.py` then the full Python half.

### Slice W6b-23 — the revalidation sweep

**T1. The sweep script.**
- [ ] Add `scripts/revalidate-artifacts.py` following the scripts' conventions (`ROOT`, `main() -> int`, `uv run python scripts/revalidate-artifacts.py`). It connects through the app's `Settings`/`Database`, reads every stored artifact table/column, parses each row against today's model-schema model via the existing read-path adapter, and prints a per-table report: rows read, rows that fail, and the first failures' `entity_ref`-identifiable key + `ValidationError` excerpt. Exit non-zero when any row fails to parse.
- [ ] Cover the tables the read paths already parse: `validation_reports.body`, `profiles.body`, `bandings.body`, `groupings.body`, `transparency_artifacts.payload`, `diagnostics.payload`, `peril_structures` (the three JSONB columns), `models.spec` + `models.fit_result` (via the adapters).
- [ ] Run the script against the seeded compose DB; it must report 0 failures on the seeded corpus.
- [ ] Add a test that proves the sweep fails on deliberately broken input: a synthetic stored row that violates today's model must be reported (the parse path is the unit; the §13 broken-input discipline).

**T2. 07 spec: the migration-event rule.**
- [ ] Under `07` §3.3 Storage (`07-platform.md`, beside FR-416), add a dated rule sentence (OQ-650, decided 2026-08-26 (c)): a narrowing change to a stored artifact shape is a migration event, not a model edit — the revalidation sweep (`scripts/revalidate-artifacts.py`) is the on-demand answer to "is anything stored unreadable?", run on the committer's clock rather than the user's.
- [ ] Run `python3 scripts/audit-docs.py`.

**T3. Gate.**
- [ ] `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q` then the full Python/docs half.

---

## Verification

- Both gate halves pass locally before the push (the frontend half regenerates the client identically — verify with `gh pr diff --name-only` that the frontend workflow is not skipped).
- `test_every_one_sided_slug_is_declared` fails when a one-sided slug is undeclared AND when a declared slug is no longer one-sided.
- `test_a_constraint_keyword_on_one_side_is_not_silent` fails when a fresh one-sided keyword appears at a shared field path, and when a registered entry is no longer one-sided.
- The revalidation sweep reports 0 failures on the seeded corpus and ≥1 failure on a deliberately broken synthetic row.
- `audit-docs.py` is green.

## Expected file changes

**W6b-22:** `backend/tests/test_contracts.py` (registry, guard, keyword check, walker) · `scripts/generate-contracts.py` (comment correction).

**W6b-23:** `scripts/revalidate-artifacts.py` (new) · `backend/tests/` (sweep test) · `docs/specs/07-platform.md` (§3.3 rule).

## Drift records

1. **The F2 keyword surface is 36 rows, not the historical 18.** `COMPARED_SLUGS` has grown from 15 to 18 since the 2026-08-24 measurement, and the W6b-17..19 commit moved the surface. The registry declares all 36 at 8b0977f; a side converging deletes an entry rather than leaving it.
2. **`metric-certificate` is registered as a known gap, not a deliberate one-sidedness.** OQ-651 (c) binds: recording it as intentional would convert an oversight into a decision. Its registry entry carries the OQ-651 trigger.
3. **The sweep reads only the tables the read paths already parse.** A stored artifact whose read path is not yet written is out of scope; the report names the covered tables.
