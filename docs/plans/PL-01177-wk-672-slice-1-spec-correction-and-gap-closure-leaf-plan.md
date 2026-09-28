---
id: PL-1177
family: plan
kind: leaf
title: WK-672 Slice 1 — Spec correction and gap closure: leaf plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-28
owner: planner
tree: 62d5fbae554be573ff4801d1bce45c575161c90d
phase: P2
work: WK-672
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-930, RL-1172, CR-932, CR-925]
---

# WK-672 Slice 1 — Spec correction and gap closure: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `python-test` (requirement markers, negative tests) and `dev-commands` (the gate and its traps), and reads `docs/plans/README.md`'s five unchecked conventions before its first step.

## Goal

Open WK-672 by making its roadmap charter name what its three ids cover, declaring
`RegressionRun` in `03` §4, registering `GOLDEN_QUOTE_MISMATCH`, and correcting one wrong
scope-out label — the spec-change slice every later WK-672 slice builds against.

**Architecture:** This is the leaf plan for Slice 1 of the map plan `PL-930`
(`docs/plans/PL-00930-wk-672-testing-map-plan.md`), which stays the map (the lead's ruling:
proceed, not replan). `PL-930` is frozen, so its stale Slice 1 text is not edited: this plan
re-derives every locator at the tree in its header and applies the sibling ruling `RL-1172`
(`docs/rulings/RL-01172-wk-672-opening-rulings-f60-and-f59-are-spec-defects-the-regression-executor-lives-in-pricing-core-and-fr-257-limb-1-is-slice-3-s.md`,
merged by #829) at every site it operates. No `SL-` row exists in the roadmap
(`grep -c 'id: SL-' docs/roadmap.md` prints 0 at this tree), so this plan carries no
`slice:` field — the precedent is `PL-1070` and `PL-1144`.

**Tech Stack:** Markdown specs and roadmap; Python 3.12 backend (`backend/src/app/errors.py`),
pytest with the `req` marker. No new dependency.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) — §3.8 (FR-260,
FR-261, FR-262 at `03:176-178`), §4.7 (`RegressionSuite`/`GoldenQuote`, `03:483`), §4.8
(`03:503`), §5.1 (the route table: `score/compare` at `03:603`, `regression-runs` at
`03:604`; the error-code list at `03:612-622`). Executors read this plan, `RL-1172` and the
spec sections their task cites.

## Status

**Activated 2026-09-28 13:39:55 BST (planner, on RL-1172 and the deputy's decisions by delegation).**
This plan was drafted at `62d5fbae` and merged `draft` by #838 (`6c6f4532`). What changed:

- **Every decision point has a resolver.** This plan opened no decision point of its own;
  the questions Slice 1 depends on are ruled in `RL-1172`, merged by #829 (`62d5fbae`), which
  also quotes the deputy's DP1 decision by delegation, option A. So this plan moves
  `draft → active` in this commit, under `document-ids.md` §1.7. `created:` does not change.
  **Frozen / dated: 2026-09-28.** Where this text and `RL-1172` disagree, the ruling governs.
- **The F4 research record has merged** as `RS-1176` (#832); the carried Slice 3 item now
  names it.

## Acceptance Standard

Every command runs in the executor's own worktree (`env -C <worktree> …`, the team's
process-cwd rule), against the range `origin/main...HEAD`, never a tip SHA alone.

1. **The WK-672 roadmap section names each of its ids' coverage, and the FR-262 split.**
   `grep -n 'score/compare' docs/roadmap.md` prints exactly two hits: one inside the
   `### WK-672` section and one inside the `### WK-675` section (each hit's line number lies
   between that section's heading and the next `###` heading). A re-read of the WK-672
   paragraph against `03:176-178` finds FR-260, FR-261 and FR-262 each covered by a phrase,
   and FR-262 typed as the backend limb only.
2. **`03` §4.9 declares `RegressionRun`, field for field with the hand-authored contract.**
   `grep -n '^### 4\.9' docs/specs/03-rating-engine.md` prints exactly one line, and it lies
   after `### 4.8` and before `## 5. Interfaces`. A side-by-side read of the §4.9 JSON block
   against `docs/contracts/schemas/regression-suite.schema.json:63-99` finds every property
   name in both, and no other: top level `suite_slug`, `rating_version_ref`, `bundle_hash`,
   `job_id`, `started_at`, `finished_at`, `overall`, `golden_results`, `property_results`;
   `golden_results[]` `name`, `status`, `expected_minor`, `actual_minor`, `difference_minor`;
   `property_results[]` `name`, `status`, `cases_run`, `counterexample`. (This tier has no
   drift guard — `contract-guard` compares only `model-schema`-generated contracts — so this
   manual read is the check, stated here because nothing else runs it.) The block names no
   property-generation library.
3. **`GOLDEN_QUOTE_MISMATCH` is registered, test-first.**
   `uv run pytest backend/tests/test_errors.py -k golden_quote_mismatch -v` passes, and the
   ledger quotes the same command's run **before** the registration failing with an
   `AssertionError` on the membership line (a `ValueError` or an `ImportError` there is a
   plan defect, not the predicted failure). `git diff origin/main...HEAD -- backend/src/app/errors.py`
   adds exactly one quoted code string, `"GOLDEN_QUOTE_MISMATCH"` — in particular it does
   **not** add `PROPERTY_ASSERTION_FAILED` (Slice 3's, see "Carried").
4. **The `regression-suite` scope-out label is corrected.**
   `grep -n '"regression-suite"' backend/tests/test_contracts.py` prints one line whose label
   names `03` and WK-672 and contains neither `later-phase` nor `04 optimisation`; the slug is
   still a key of `ONE_SIDED_SLUGS` (the scope-out itself stays until the slice that builds the
   shape), and `uv run pytest backend/tests/test_contracts.py -q` passes.
5. **The change set is exactly the slice's.** `git diff --stat origin/main...HEAD` lists
   `docs/roadmap.md`, `docs/specs/03-rating-engine.md`, `backend/src/app/errors.py`,
   `backend/tests/test_errors.py`, `backend/tests/test_contracts.py`, the slice's `LG-`
   ledger under `docs/ledgers/`, and `docs/INDEX.md` — and nothing else.
6. **The full two-half gate exits 0** on the committed tree, each command's exit code
   recorded in the ledger beside the `HEAD` it ran on: the six lines of `CLAUDE.md` §11
   (`ruff`, `mypy`, `lint-imports`, `pytest`; `audit-docs.py`, `req-coverage.py`;
   `generate-contracts.py --check`; the frontend install, `generate:api`, `lint`,
   `type-check`, `test`, `build`), run as `dev-commands` gives them. The DB stack is checked
   up before `pytest`, never asserted.
7. **The four docs checks pass on a detached copy of the committed tree:**
   `python3 scripts/audit-docs.py`, `python3 scripts/doc-id.py check`,
   `python3 scripts/doc-index.py --check`, `python3 scripts/register-lint.py` — rc, the
   `FAILED (n)` line or "All checks passed.", and the `DISCLOSED (…)` line quoted.
8. **The deputy's merge acknowledgement is recorded** on the PR before the lead merges, and
   the slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and
   the lead's merge — no maintainer acceptance line is required for this slice, and none is
   to be waited on.

## Global Constraints

- **Money is integer pence/cents, or `Decimal` in the rating path, never float**
  (`CLAUDE.md` §7). §4.9's example writes every money field as an integer `_minor` value.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2).
  `RegressionRun` does not exist in `model-schema` at this tree (`grep -rn RegressionRun packages backend/src`
  prints 0 hits outside the generated client), so §4.9 documents the hand-authored Phase 0
  contract; RL-1172 item 3c moves the shape into `model-schema` in Slice 3, and §4.9 says so.
- **Requirement ids are permanent** (`CLAUDE.md` §5). This slice mints no `FR-`/`NFR-` id.
- **`PL-930` is frozen** (`document-ids.md` §1.7). Its stale Slice 1 text is superseded by
  this plan's re-derived text, not edited.
- **Spell no retired legacy path** (RL-1140; `audit-docs.py` check 36). `PL-930`'s Global
  Constraints cite one, split across a line break; it resolves to `CR-932` (plan review 11)
  and is cited here by that id only.
- **Every id is cited individually**, never as a bare numeric range (`.claude/roles/planner.md`).

---

## Scope

### Requirement coverage — `03` §3.8, each id individually

- **FR-260** (Golden Quote, promotion re-scoring): Task 1 names it in the charter; Task 2's
  §4.9 documents the run record its promotion check reads; Task 3 registers its refusal code,
  with a `req("FR-260")` marker. Its raiser and store are Slice 2's.
- **FR-261** (property assertions over generated contexts): Task 1 names it; Task 2's §4.9
  documents `property_results`. Generation, the five classes and the route are Slice 3's.
- **FR-262** (Quote Sandbox): Task 1 names `POST /api/v1/score/compare` as WK-672's
  backend limb and WK-675's view as its consumer (RL-1172 item 5, the deputy's DP1 decision,
  option A). The endpoint is Slice 4's.
- **FR-257 limb (1)** (the passing-Regression-Suite approval check): named in Task 1's
  charter text as this Work's (RL-1172 item 4); built in Slice 3.

### Already discharged by RL-1172 — the executor does not redo these

RL-1172's own commit amended `03` §5.2 (now `03:696-780`). Each item below was a candidate
for this slice and is **done at this tree**:

- F60 (1) `to_wire` declared in the `runtime.py` block (`03:709`).
- F60 (2) the six `operations.py` functions declared (the block annotated at `03:752`).
- F60 (3) `assert_integer_minor_round_trip` declared in the `compile.py` block (`03:704`).
- F60 (4) `build_scoring_result` given a signature line in the `score.py` block (`03:716`).
- F59: `KeyFilter` shown as imported from `model_schema.rating` (`03:740`).
- RL-1172 item 3b: `generate_contexts`'s parameter corrected to
  `Sequence[InputContractField]` (`03:731`).
- The dated correction of `PL-930`'s stale `03` citations (RL-1172, "A correction to
  `PL-930`").

None of `PL-930`'s own three Slice 1 tasks (1.1 roadmap, 1.2 §4.9, 1.3 the error code) was
discharged by RL-1172; all three are Tasks 1–3 below. Task 4 is RL-1172 item 3c's addition.

### Premises re-derived at this tree

| # | `PL-930` said | At `62d5fbae` | Status |
|---|---|---|---|
| a | WK-672 is a table row at `docs/roadmap.md:377` | a section: heading `:623`, YAML `id: WK-672` `:626`, the migrated "From Workstreams" line `:634` | stale; Task 1 rewritten |
| b | WK-675's row at `:381` | a section: heading `:668` | stale; Task 1 uses `:668` |
| c | §4.8 "at line 520", insert after 519 | `### 4.8` at `03:503`; `## 5. Interfaces` at `03:583`; no §4.9 | stale; Task 2 inserts before `:583`'s preceding `---` |
| d | `GOLDEN_QUOTE_MISMATCH` declared at `03:611` | in the §5.1 error list at `03:618` | stale line; fact holds |
| e | `RATING_ERROR_CODES` at `errors.py:275-341`, `TRACE_NOT_PENDING` at `:339`, `PlatformError.__init__` at `:369` | unchanged; the set closes at `:341` | reproduces |
| f | `RegressionRun` at `regression-suite.schema.json:63-99` | `"RegressionRun"` at `:63`; fields as listed in acceptance item 2 | reproduces |
| g | `test_errors.py` imports `PLATFORM_ERROR_CODES, PlatformError, install_error_handlers` | `backend/tests/test_errors.py:10`, unchanged; `RATING_ERROR_CODES` is in `errors.py`'s `__all__` (`:29`) | reproduces |
| h | (not in `PL-930`) `test_contracts.py:89` labels `regression-suite` `"later-phase — 04 optimisation"` | `backend/tests/test_contracts.py:89`, in `ONE_SIDED_SLUGS` (`:67`) | reproduces; Task 4 |
| i | §4.9's counterexample "produced by `hypothesis`'s own shrinking" | the library is Slice 3's decision (RL-1172 item 3c; see "Carried") | superseded; Task 2 is generator-neutral |

### Noted, not WK-672's

Comparing `03` §5.1's error list (`03:612-622`) with `RATING_ERROR_CODES` at this tree finds
seven `03` codes absent from that set. `EVIDENCE_INCOMPLETE` is registered elsewhere
(`errors.py:254`, `06`'s set) and is not a gap. `GOLDEN_QUOTE_MISMATCH` is Task 3.
`PROPERTY_ASSERTION_FAILED` is FR-261's and is carried to Slice 3. The remaining four —
`CONTROL_FACTOR_IN_RATEABLE_PATH`, `DEPLOY_REQUIRES_APPROVAL`, `DEPLOY_DATE_RANGE_OVERLAP`,
`MODEL_REFERENCE_MODE_INCONSISTENT` — are not WK-672's and fall under the gate-coverage
cluster `CR-932` ruled out of this Work. This plan records them and does nothing about them.

### Carried to later slices — named, not planned here

- **Slice 2:** `RegressionSuite` and `GoldenQuote` as `model-schema` artifacts; the store
  honours NFR-499's access-controlled-artifact clause (RL-917); the `GOLDEN_QUOTE_MISMATCH`
  raiser on the promotion path (FR-260); removal of the `regression-suite` scope-out when the
  shape lands (RL-1172 item 3c).
- **Slice 2 or 3, whichever builds `RegressionSuite` in `model-schema`:** correct `03` §4.7's
  free-text `assertion` strings to the structured union of FR-261's five classes (RL-1172
  item 3c, the deputy's assertion-language ruling).
- **Slice 3:** `run_regression`/`generate_contexts` in `pricing-core` `rating/testing.py`,
  plain `def` on the synchronous engine path (RL-1172 items 3a, 3c); `RegressionRun` as a
  `model-schema` artifact; FR-257 limb (1) on `submit_for_review`, refusing with
  `EVIDENCE_INCOMPLETE`, with a limb-(1)-only marker (RL-1172 item 4); registration of
  `PROPERTY_ASSERTION_FAILED` together with its raiser (this plan's slice design, endorsed by
  the lead). **The generator is `hypothesis`**, as a `pricing-core` runtime dependency under
  six conditions — the deputy's spike F4 decision by delegation, dated 2026-09-28 and
  corrected the same day on its first condition (the exact pin is *added* to
  `packages/pricing-core/pyproject.toml` and the root dev-group entry aligned to it), filed in
  the F4 research record, RS-1176 (#832). Slice 3's leaf plan applies all six conditions and updates
  `03` §8 and `docs/skills-map.md` in the same PR (`CLAUDE.md` §10).
- **Slice 4:** `POST /api/v1/score/compare`, two `score_one` calls on the shared
  `build_scoring_result` tail (RL-858) with the traces diffed step by step, the diff-shape
  tests and the broken-input proof; no frontend (RL-1172 item 5).
- **WK-672's closure record:** FR-262 typed "backend limb delivered and tested (WK-672); UI
  limb reassigned to WK-675" (RL-1172 item 5).

### Decision points

None open. Where `PROPERTY_ASSERTION_FAILED` is registered is slice design, the planner's
own (`.claude/roles/planner.md`), decided above and endorsed by the lead; no row is owed.

### Sequencing

Slice 1 → 2 → 3 → 4, one at a time (`delivery-process.md` §8; RL-1172 item 6 supersedes
`PL-930`'s "may run in parallel"). Within this slice, Tasks 1–4 are independent of each
other and run in the order written, each with its own commit.

---

## Tasks

### Task 1: Correct the WK-672 and WK-675 roadmap sections

**Files:**
- Modify: `docs/roadmap.md` (the `### WK-672` section, heading at `:623`; the `### WK-675`
  section, heading at `:668`)

**Interfaces:**
- Consumes: RL-1172 item 5 (the deputy's DP1 decision, option A) and item 4.
- Produces: the charter text every later WK-672 leaf plan cites.

- [ ] **Step 1: Read both sections at your tree**

Run: `grep -n '^### WK-672\|^### WK-673\|^### WK-675\|^### WK-690' docs/roadmap.md` and
`sed -n '623,636p;668,681p' docs/roadmap.md` (adjust to the printed lines if they moved).
Expected: WK-672's section ends with the migrated line
`From “Workstreams” (line 377): Testing: golden quotes, property assertions, regression runs | FR-260, FR-261, FR-262`;
WK-675's ends with its own migrated line. **Do not edit either migrated line** — it records
where the row came from. The new text is appended below it, the form `WK-690`'s section uses
for its dated 2026-09-28 paragraph.

- [ ] **Step 2: Append the WK-672 paragraph**

After WK-672's migrated line, leave one blank line and add this paragraph (one paragraph; it
contains no `|`):

```markdown
**2026-09-28 — the charter, named against its own ids** (WK-672 Slice 1, `PL-1177`; `RL-1172` items 4 and 5, the latter quoting the deputy's DP1 decision by delegation, option A). **FR-260:** golden quotes, and the promotion re-scoring that refuses on a mismatch beyond the declared tolerance. **FR-261:** property assertions over generated quote contexts, and the regression runs that execute a suite (`POST /api/v1/rating-versions/{id}/regression-runs`, recorded as `03` §4.9 `RegressionRun`). **FR-262: the backend limb only** — `POST /api/v1/score/compare`, one quote scored against two Rating Versions with the step-level diff; the Quote Sandbox view over it is WK-675's, and FR-262 is delivered only when both limbs have landed. **FR-257 limb (1)** — the approval gate's passing-Regression-Suite check — is also this Work's (`RL-1172` item 4). Slices run 1 → 2 → 3 → 4, one at a time.
```

- [ ] **Step 3: Append the WK-675 paragraph**

After WK-675's migrated line, leave one blank line and add:

```markdown
**2026-09-28 — the Quote Sandbox's backend is WK-672's** (`RL-1172` item 5, the deputy's DP1 decision by delegation, option A). The quote sandbox view in this Work consumes `POST /api/v1/score/compare`, which WK-672 builds and tests; this Work builds the view only. FR-262 is delivered only when both limbs have landed.
```

- [ ] **Step 4: Check the placement**

Run: `grep -n 'score/compare' docs/roadmap.md`
Expected: exactly two hits, one between the `### WK-672` and `### WK-673` headings and one
between the `### WK-675` and `### WK-690` headings (acceptance item 1). A third hit, or a hit
elsewhere, means a paragraph landed in the wrong section.

- [ ] **Step 5: Run the docs audit**

Run: `python3 scripts/audit-docs.py`
Expected: no new failure from `docs/roadmap.md` (no id is minted; FR-257, FR-260, FR-261 and
FR-262 are all defined in `03`); any new failure row is a defect in this task's text.

- [ ] **Step 6: Commit**

```bash
git add docs/roadmap.md
git commit -m "docs(roadmap): WK-672 charter named against FR-260, FR-261, FR-262; WK-675 consumes score/compare (RL-1172)"
```

### Task 2: Declare `RegressionRun` in `03` §4.9

**Files:**
- Modify: `docs/specs/03-rating-engine.md` (new `### 4.9`, after §4.8's last paragraph and
  before the `---` rule that precedes `## 5. Interfaces` at `:583`)

**Interfaces:**
- Consumes: `docs/contracts/schemas/regression-suite.schema.json:63-99`, the hand-authored
  `RegressionRun` definition. The fields below are copied from it, not invented.
- Produces: the declared run record Slice 3 implements (as a `model-schema` artifact) and
  Slice 2's promotion check and Slice 3's FR-257 limb (1) check read.

- [ ] **Step 1: Find the insertion point**

Run: `grep -n '^### 4\.8\|^## 5\. Interfaces' docs/specs/03-rating-engine.md` and
`sed -n '574,583p' docs/specs/03-rating-engine.md`.
Expected: `### 4.8` at `:503`, `## 5. Interfaces` at `:583`, and a `---` line two lines
above it. The new subsection goes after §4.8's last paragraph (ending "…reading
`error_code` off this column.") and before that `---`.

- [ ] **Step 2: Write the subsection**

````markdown
### 4.9 `RegressionRun`

*(Added 2026-09-28, WK-672 Slice 1, `PL-1177`. Mints no requirement id: it documents the
execution record that FR-260's promotion check and FR-261's property run produce, matching
`docs/contracts/schemas/regression-suite.schema.json`'s `RegressionRun` definition, which
predates this text. That contract is the hand-authored Phase 0 draft; `RL-1172` item 3c
makes `RegressionRun` a `model-schema` artifact in the slice that first builds it, WK-672
Slice 3, and this subsection then describes the generated shape.)*

```json
{
  "suite_slug": "motor-gb-core",
  "rating_version_ref": {"…artifact-ref…"},
  "bundle_hash": "sha256:…",
  "job_id": "…uuid…",
  "started_at": "2026-09-28T09:00:00Z",
  "finished_at": "2026-09-28T09:00:04Z",
  "overall": "fail",
  "golden_results": [
    {"name": "young-driver-london", "status": "fail",
     "expected_minor": 112480, "actual_minor": 112900, "difference_minor": 420}
  ],
  "property_results": [
    {"name": "premium_positive", "status": "pass", "cases_run": 5000},
    {"name": "monotone_in_age", "status": "pass", "cases_run": 5000, "counterexample": null}
  ]
}
```

`overall == "fail"` blocks promotion (FR-260). A `golden_results` entry's `status` is
`"fail"` when `difference_minor` exceeds the golden quote's declared tolerance (default:
exact — zero — for money, FR-260's own text). A `property_results` entry's
`counterexample`, when present, is the failing case reduced to a minimal one an actuary can
read, as the contract's own description states; how it is generated and reduced is
`pricing-core`'s `rating/testing.py` (§5.2), built in Slice 3. A Rating Version's approval
evidence reads the run whose `bundle_hash` equals the version's current bundle hash
(`RL-1172` item 4).
````

- [ ] **Step 3: Verify the shape against the contract, side by side**

Run: `sed -n '63,99p' docs/contracts/schemas/regression-suite.schema.json`
Compare every property name against the JSON block just written, using acceptance item 2's
list. Then run `grep -n -i 'hypothesis' docs/specs/03-rating-engine.md` and confirm no hit
falls inside the new §4.9 (the generator is Slice 3's). A field in one and not the other is
a defect in this step, never in the contract — the contract is the source this step copies.

- [ ] **Step 4: Run the docs audit**

Run: `python3 scripts/audit-docs.py`
Expected: no new failure from `03` — §4.9 cites FR-257, FR-260 and FR-261, all defined, and
mints nothing; the spec keeps its ten `##` sections.

- [ ] **Step 5: Commit**

```bash
git add docs/specs/03-rating-engine.md
git commit -m "docs(spec): declare RegressionRun in 03 section 4.9, matching its hand-authored contract"
```

### Task 3: Register `GOLDEN_QUOTE_MISMATCH`, test-first

**Files:**
- Modify: `backend/src/app/errors.py` (inside `RATING_ERROR_CODES`, `:275-341`; after
  `"TRACE_NOT_PENDING",` at `:339`)
- Test: `backend/tests/test_errors.py` (import at `:10`; new test beside
  `test_no_live_rating_version_is_registered_at_409`)

**Interfaces:**
- Consumes: `PlatformError.__init__(self, code: str, title: str, status_code: int, detail: str | None = None, *, errors: tuple[FieldError, ...] = ())`
  (`errors.py:369`), which raises `ValueError("unknown error code …")` for a code outside
  `_KNOWN_CODES` — unchanged.
- Produces: `"GOLDEN_QUOTE_MISMATCH"` as a constructible code for Slice 2's promotion-refusal
  raiser. This task adds no raiser and chooses no HTTP status — the raiser's slice does.

- [ ] **Step 1: Write the failing test**

Extend the import at `backend/tests/test_errors.py:10` to
`from app.errors import PLATFORM_ERROR_CODES, RATING_ERROR_CODES, PlatformError, install_error_handlers`
(keep `ruff`'s isort order), and add, after `test_no_live_rating_version_is_registered_at_409`:

```python
@pytest.mark.req("FR-260")
def test_golden_quote_mismatch_is_registered() -> None:
    """`03` §5.1 declares this code; Slice 2's promotion refusal raises it.

    Asserted by literal name, never by iterating `RATING_ERROR_CODES`: a test that iterates
    the collection it checks passes for every member by construction.
    """
    assert "GOLDEN_QUOTE_MISMATCH" in RATING_ERROR_CODES
    error = PlatformError("GOLDEN_QUOTE_MISMATCH", "Golden quote mismatch", 409)
    assert error.code == "GOLDEN_QUOTE_MISMATCH"
```

(The `409` only makes the constructor call well-formed; the test asserts no status, because
the status is Slice 2's choice.)

- [ ] **Step 2: Run it to verify it fails, for the predicted cause**

Run: `uv run pytest backend/tests/test_errors.py -k golden_quote_mismatch -v`
Expected: FAIL with `AssertionError` on the `in RATING_ERROR_CODES` line. An `ImportError`
means the import edit is wrong; a `ValueError("unknown error code …")` means the membership
line was skipped or reordered. Either is a defect in Step 1, not the predicted failure.
Quote the failing line into the ledger (acceptance item 3).

- [ ] **Step 3: Add the code**

In `backend/src/app/errors.py`, inside `RATING_ERROR_CODES`, after `"TRACE_NOT_PENDING",`:

```python
        # Golden quotes (WK-672 Slice 1, FR-260). Registered ahead of its raiser: Slice 2
        # builds the promotion-refusal path that raises it. PROPERTY_ASSERTION_FAILED,
        # FR-261's code, is registered by Slice 3 together with its raiser.
        "GOLDEN_QUOTE_MISMATCH",
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest backend/tests/test_errors.py -v`
Expected: every test passes, including `test_golden_quote_mismatch_is_registered` and the
unchanged `test_spec_error_codes_are_all_constructible` (it iterates `PLATFORM_ERROR_CODES`,
a disjoint set).

- [ ] **Step 5: Type-check and lint the two files**

Run: `uv run mypy && uv run ruff check backend/src/app/errors.py backend/tests/test_errors.py`
Expected: exit 0 — the new member is a `str` literal in a `frozenset[str]`.

- [ ] **Step 6: Commit**

```bash
git add backend/src/app/errors.py backend/tests/test_errors.py
git commit -m "feat(rating): register GOLDEN_QUOTE_MISMATCH ahead of its Slice 2 raiser (FR-260)"
```

### Task 4: Correct the `regression-suite` scope-out label

**Files:**
- Modify: `backend/tests/test_contracts.py:89` (`ONE_SIDED_SLUGS`, opened at `:67`)

**Interfaces:**
- Consumes: RL-1172 item 3c — the label is wrong: the shape is `03`'s and belongs to WK-672.
- Produces: a label that states the slug's real status; the slug stays scoped out until the
  slice that builds the shape removes it.

- [ ] **Step 1: Confirm the line**

Run: `grep -n '"regression-suite"' backend/tests/test_contracts.py`
Expected: one hit, `:89`, reading `"regression-suite": "later-phase — 04 optimisation",`.

- [ ] **Step 2: Replace the label**

```python
    # Corrected 2026-09-28 (WK-672 Slice 1, RL-1172 item 3c): the label said "04 optimisation";
    # the shape is 03's and WK-672's. Slices 2-3 move it into model-schema and remove this key.
    "regression-suite": "authored-only until WK-672 builds it — 03 §4.7 and §4.9",
```

- [ ] **Step 3: Run the contract tests**

Run: `uv run pytest backend/tests/test_contracts.py -q`
Expected: pass, with the same passed count as at the base tree (a label change must not move
the count; a moved count means the dict key changed, not only its value).

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_contracts.py
git commit -m "test(contracts): correct the regression-suite scope-out label to 03 and WK-672 (RL-1172)"
```

### Task 5: The slice gate and the ledger

- [ ] **Step 1:** Run the full two-half gate per `dev-commands` (acceptance item 6), each
  process started with `env -C <worktree>`; record every exit code and the `HEAD` in the
  slice's `LG-` ledger (id from the lead).
- [ ] **Step 2:** Run the four docs checks on a detached copy of the committed tree
  (acceptance item 7); quote rc, `FAILED`/"All checks passed." and `DISCLOSED`.
- [ ] **Step 3:** `git diff --stat origin/main...HEAD` (acceptance item 5) into the ledger.
- [ ] **Step 4:** Open the PR; the auditor's pass and the deputy's acknowledgement follow
  (acceptance item 8).

---

## Self-review

**1. Spec coverage.** FR-260 → Tasks 1, 2, 3. FR-261 → Tasks 1, 2. FR-262 → Task 1 (the
split; the endpoint is Slice 4's). FR-257 limb (1) → Task 1 (named; built in Slice 3).
RL-1172's Slice 1 row ("the WK-672 and WK-675 roadmap text … `03` §4.9 … the
`GOLDEN_QUOTE_MISMATCH` registration … the `test_contracts.py:89` label correction") → Tasks
1, 2, 3, 4, each in Files, Steps and Acceptance. RL-1172's `hypothesis` condition reaches
Task 2's text (generator-neutral), its Step 3 check and acceptance item 2.

**2. Placeholder scan.** Every step carries a literal path, the literal text to insert and a
command with its expected result stated by cause. `PL-1177` in Tasks 1 and 2's inserted
text is this plan's own minted id (drafted as a working id and renumbered at its mint turn,
the team's id rule), so the executor copies it as written.

**3. Type and literal consistency.** Checked against the shipped source at the header's tree,
not this plan's prose: `RATING_ERROR_CODES` exported at `errors.py:29`; the neighbour test's
name `test_no_live_rating_version_is_registered_at_409`; `ONE_SIDED_SLUGS` at
`test_contracts.py:67`; the §4.9 field names against the contract lines `63-99`; the `req`
marker form against `test_errors.py:101`.

**4. Rulings between sweep and PR.** Open PRs read at this plan's commit: #830 (Track E, no
`03` §3.8/§4 or WK-672 content by title), #832 (the F4 research record, cited under
"Carried"), #833–#837 (other tracks). None rules on this slice's subject.
