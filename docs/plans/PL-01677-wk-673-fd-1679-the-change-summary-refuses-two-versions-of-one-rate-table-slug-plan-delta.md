---
id: PL-1677
family: plan
kind: map
title: WK-673 — the FD-1679 loud guard, FR-242's drafted change summary refuses a version pinning two versions of one rate-table slug (SL-1678), and the slug-only-map class sweep: a dated delta to PL-1267
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1267, FD-1679, SL-1678, PL-1502, SL-1503, RL-1498, RL-1538, PL-1542, SL-1543, FD-1660]
---

# PL-1677 — WK-673, the FD-1679 loud guard: the drafted change summary refuses two versions of one rate-table slug (delta to PL-1267)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). It adds
> **one slice row**, SL-1678 (working id), under `### WK-673` in [`../roadmap.md`](../roadmap.md),
> to WK-673's Work plan [`PL-1267`](PL-01267-wk-673-dislocation-with-attribution-map-plan.md),
> whose body is frozen and not edited. It also records one **open** decision point for WK-673's
> plan (DP-P1, the real pairing fix), which this slice does not decide.
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds `test-driven-development`
> (every red is seen red **by its cause** on `main` before the code that turns it green),
> `python-test` (the `req` marker; negative tests), `fastapi-service` (the refusal is an RFC 9457
> problem), `spec-change` (Task 1), `dev-commands` (`uv sync --all-packages`; both gate halves)
> and `git-hygiene`. Read [`README.md`](README.md)'s unchecked conventions before the first step.
> The executor is spawned from `.claude/roles/executor.md`.

*(Minted 2026-10-12 as PL-1677 from working id 9896, with its slice row SL-1678 from working id
9897 and its finding FD-1679 from working id 9895, in this plan's early-mint PR, on the
maintainer's (by delegation) entries "2026-10-12 05:57:57 BST" (the ACK to activate and to
early-mint as PL-1677 and SL-1678 after SL-1669's ledger PR) and "2026-10-12 05:58:56 BST" (the finding
mints as FD-1679 in the same PR), in `to-lead.md`. Every
citation of these ids is re-pointed; inside a verbatim quote the minted id stands in brackets,
`[FD-1679]`, where the entry wrote the working id.)*

Filed under a working id (the mint note above); its slice row likewise (`draft`). Both were
reserved by the lead, `~/gi-pricing-plan.local/handover/eta.md` line "2026-10-12 05:45:46 BST"
(free-check run first: index 0, eta 0, branches 0). Written 2026-10-12 by the planner.
**Tree read:** `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a` (#1291,
SL-1548). Every `file:line` below was read at that tree. FD-1679 is minted in the same PR, and its
class-sweep table is this plan's (§Class sweep).

## Context — the entries this delta records

Each entry is quoted from the channel file named, with its author.

1. **The finding and its order constraint** — the maintainer's (by delegation) entry
   "2026-10-12 05:43:54 BST — [FD-1679]: HIGH (not MEDIUM), owner WK-673; a LOUD GUARD merges
   BEFORE SL-1543. Task 0 results noted" (`channel/to-lead.md`), verbatim in its operative lines:

   ```text
   Verified at main: rating_versions.py:1404 `{ref.slug: ref for ref in …rate_tables}` keeps the LAST ref per slug. It feeds FR-242's drafted change summary (:1377-1400, SL-1503's), which an approver reads.
   - With two pinned versions of one slug (RL-1538), the summary silently omits one table's change, or reports a wrong from/to pair.
   ORDER CONSTRAINT: A-4 (SL-1543) is what puts a B1 version into the demo, so a guard MUST merge before SL-1543:
   - the change summary REFUSES with a named code (VALIDATION_FAILED, message naming [FD-1679]) when either side pins two versions of one rate-table slug;
   - red first on main (two versions of one slug → today a silently one-sided summary).
   The real fix (diff keyed by slug with an explicit pairing of versions) is a DP for the WK-673 plan: which old version pairs with which new, when a slug carries two. It is not decided here.
   ```

2. **The vehicle, the permissive create, and the class sweep** — the maintainer's (by
   delegation) entry "2026-10-12 05:44:45 BST — [FD-1679] is LIVE: (a) a standalone tiny WK-673
   row NOW; create stays permissive (RL-1538); PLUS a sweep for the same defect class"
   (`channel/to-lead.md`), verbatim in its operative lines:

   ```text
   (a) YES. Plan the one-row WK-673 delta, then an executor. Write set: the change-summary path in rating_versions.py + its test. Red first through the HTTP create route + change summary on main. Create stays permissive: RL-1538 allows two versions of one slug on purpose; the defect is the consumer, not the input.
   Predicate, verbatim in the plan: `git grep -nE '\{[a-z_]+\.slug *:|\.slug\]? *=|by_slug' -- backend/src packages frontend/src`, and every hit is read, not just counted.
   - Each hit that consumes pins is classified: SAFE (cannot see duplicates), GUARDED by this row (added to its write set if small), or LISTED in [FD-1679]'s text with its own owner.
   - The FD's scope is the class, not only :1404.
   ```

3. **Reachable on `main` today** — the lead's from-lead entry "2026-10-12 05:44:28 BST — [FD-1679]
   REACHABILITY CHECK" (`channel/from-lead-2026-10-09.md`): *"REACHABLE ON MAIN TODAY by
   code reading at 604ea084 — packages/model-schema/src/model_schema/rating.py:70-84 Pins = plain
   list[ArtifactRef] per kind, extra=forbid, NO model_validator against duplicate slugs;
   backend/src/app/platform/rating_versions.py:258+ create_rating_version stores
   pins=pins.model_dump(...) as given (no dedup/refusal) … Not yet proven end-to-end through the
   HTTP create route (the guard slice's red does that)."* Red 1 below is that proof.

4. **Why two versions of one slug is legitimate input** — `RL-1538` (Option B, built as B1):
   each seeded table enters as its ratio to its seed origin, *"two table pins plus an existing
   expression step"*; its item 3 (i) makes "two versions of one table slug pinned and scored end
   to end" A-4's Task 0. So create must keep accepting it, and the consumer must stop collapsing it.

## Goal

`GET /api/v1/rating-versions/{id}/change-summary-draft` never drafts a summary that silently
drops or mis-pairs a rate-table change. When the candidate's pins or its baseline's pins carry
two versions of one rate-table slug, the route refuses with **409 `VALIDATION_FAILED`**, the
detail naming FD-1679 and the slug, until DP-P1's pairing fix
lands. `POST /api/v1/rating-versions` keeps accepting such pins (`RL-1538`).

## Status

The status is the `status:` field in the header, and nothing else. **No decision point blocks
SL-1678.** DP-K is ruled by the lead (§Decision points, and the note under the table). DP-G1
(409) and DP-G2 (the guard inside `_pins_by_slug`) were the planner's design choices, accepted by
the maintainer (by delegation), entry "2026-10-12 05:57:57 BST": *"DP-G1 409: accepted"* and
*"DP-G2 inside _pins_by_slug: accepted. Every consumer of that map is guarded at once."* DP-P1 is
**open**, for WK-673's plan, and does not block this slice. The plan is minted `draft`; the slice
PR's first commit sets it `active`, as for `PL-1502`.

## Activation needs, each with its state at `604ea084`

1. **DP-K answered by the lead.** **MET**: (i), from-lead "2026-10-12 05:48:32 BST".
2. **This delta is ACKed and minted.** **MET at the mint PR's merge**: the ACK is the
   maintainer's (by delegation) entry "2026-10-12 05:57:57 BST"; the mint is this plan's PR.
3. **No in-flight writer on the write set, or the dispatch record names the definitions.**
   Re-checked by the lead at the GO (§Write set lists the paths). **OPEN until the GO.**
4. **A build slot and the single gate** (`RL-1445` item 1). **OPEN.**
5. **Order:** SL-1678 merges **before `SL-1543`** (entry 1's ORDER CONSTRAINT). The lead holds
   SL-1543's reseat on it.

## Scope and requirements, each id individually

- `03` **FR-242** (the change summary, drafted from the structural and rate-table diffs): its
  drafting limb, delivered by `SL-1503` under `PL-1502` / `RL-1498`, gains a refusal where it
  cannot pair. FR-242's text (`03-rating-engine.md:142`) carries no dated amendment at `604ea084`.
- `03` **FR-237** (exact pins): read only; create is not changed.
- FD-1679 (working id; HIGH, owner WK-673): the loud guard for `:1404`, and the class sweep's
  verdict: GUARDED is `:1404` and its two callers only, and nothing is LISTED (§Class sweep).

## Premises, read at `604ea084`

| # | Premise | Locator | What it says |
|---|---|---|---|
| a | Pins is a plain list per kind, no duplicate check | `packages/model-schema/src/model_schema/rating.py:70-84` | `class Pins`: `rate_tables`, `models`, `reference_tables`, `custom_objectives`, `sub_graphs`, each `list[ArtifactRef]`; `extra="forbid"`, no validator |
| b | Create stores pins as given | `backend/src/app/platform/rating_versions.py:258-310` | `pins=pins.model_dump(mode="json") if pins is not None else None`; no dedup, no refusal |
| c | The summary pairs by slug, last ref wins | `rating_versions.py:1404-1408` `_pins_by_slug` | `return {ref.slug: ref for ref in Pins.model_validate(pins).rate_tables}` |
| d | Only the rate-table pins feed the summary | `rating_versions.py:1329-1401` `draft_change_summary_for` | `before`/`after` at `:1377-1378` are the only pin reads; the structural diff (`:1376`) reads the two algorithms, not pins |
| e | No baseline → no pairing | `rating_versions.py:1367-1368` | `if found is None: return draft_change_summary(None, None, [])`, before `_pins_by_slug` is called |
| f | The existing 409 on this route | `rating_versions.py:1344-1351`; `03-rating-engine.md:1052`, `:1124` | `RATING_VERSION_UNPINNED`, 409, for a version with no `algorithm_ref` or no `pins` |
| g | The route | `backend/src/app/api/models.py:1256-1276` | `responses=problems(401, 403, 404, 409, 422)`; 409 is already declared |
| h | The route's tests | `backend/tests/test_rating_version_change_summary_route.py` | `pytestmark = pytest.mark.req("FR-242")`; helpers `_seed_table_version`, `_pins`, `_insert(approved=True)`, `_save_algorithms`, `_url`, `_headers` |
| i | The HTTP create route's tests | `backend/tests/test_rating_version_create_pins.py:38-104` | `_body(...)`, `api_client.post("/api/v1/rating-versions", json=_body(algorithm_ref=…, pins=…))` → 201 |

**What today's code does with duplicates (from c, d).** Candidate pins `[X@2, X@1]` against a
baseline pinning `[X@1]`: `after = {X: X@1}`, `before = {X: X@1}`, `old == new`, so **no entry
for X** — the edited table's change is silently omitted. Candidate `[X@1, X@2]`: `after = {X:
X@2}`, so the summary reports **X 1 → 2** as a replacement, though the candidate still pins X@1.
Baseline `[X@1, X@2]` against candidate `[X@2]`: `before = {X: X@2}`, no entry. Each is a red below.

## Decision points

| DP | Question | Options | Recommendation | Blocking | Who |
|---|---|---|---|---|---|
| DP-K | Which pin kinds trigger the refusal? | (i) `rate_tables` only; (ii) every kind (`models`, `rate_tables`, `reference_tables`, `sub_graphs`, and `custom_objectives`) | **(i).** Entry 1 says *"when either side pins two versions of one **rate-table** slug"*; premise d: the summary reads only `rate_tables`, so a duplicate in another kind cannot make this summary wrong, and (ii) would refuse correct approval evidence for a valid version | — | **Ruled (i)** by the lead, from-lead "2026-10-12 05:48:32 BST" (note below) |
| DP-G1 | Status code of the refusal | (a) 409; (b) 422 | **(a) 409.** The request is well formed; the version's stored state makes it unanswerable, as for `RATING_VERSION_UNPINNED` on the same route (premise f), and `VALIDATION_FAILED` is used at 409 for state refusals elsewhere (`07-platform.md:322`; `02-modelling.md:2265`). 409 is already in the route's `problems(...)` (premise g), so the generated contract does not move | no | the planner (design choice; the lead may overrule) |
| DP-G2 | Where the guard sits | (a) inside `_pins_by_slug`, raising when one slug appears twice; (b) a separate check on `row.pins` before the baseline lookup | **(a).** It refuses exactly where the collapse happens, so every caller of the map is guarded and a first version (no baseline, premise e) still gets its summary, which pairs nothing and is not wrong. (b) would refuse a first version for a defect it does not have. Red 4 pins the first-version behaviour | no | the planner (design choice; the lead may overrule) |
| DP-P1 | **For WK-673's plan, not this slice:** the real fix — how the summary pairs versions when a slug carries two | (a) **pair by the referencing `table` step**: key each pin by the step(s) whose `table` ref names it, and pair across versions through the step pairing `diff_algorithms` already makes; a pin no step references is listed unpaired; (b) **set diff per slug**: report `{old versions} → {new versions}` for the slug, with a cell diff only when each side holds exactly one; (c) **keep the refusal** as the rule: a version pinning one slug twice gets its summary written by hand | **(a).** B1's two pins of one slug are two steps' tables (the seed and the edit, `RL-1538`), so the step is what the actuary means by "this table changed"; the pairing already exists for the structural diff. A renamed step shows as removed + added: loud, not silent. (b) is honest but gives the approver no cell diff for the B1 shape, which is the case that needs one. (c) leaves the demo's B1 version without drafted evidence. Cost of (a): about one executor-day, the summary's `RateTableChange` gaining the step id (a contract change) | no (this slice) | **open** — the decision-maker, as an `RL-` against WK-673's plan |

**Note on DP-K — a brief that disagreed with its authority.** The lead's brief for this seat
(`handover/brief-planner-fd9895-2026-10-12.md`, Do item 3) read: *"the change summary REFUSES
with `VALIDATION_FAILED`, naming [FD-1679], when EITHER side's pins carry two versions of one slug
(any kind: models / rate_tables / reference_tables / sub_graphs)"*. Its authority, the
maintainer's (by delegation) entry 05:43:54 (Context, entry 1), reads: *"the change summary
REFUSES with a named code (VALIDATION_FAILED, message naming [FD-1679]) when either side pins two
versions of one rate-table slug"*. The planner raised the conflict to the lead; the lead ruled,
from-lead "2026-10-12 05:48:32 BST": *"refuse on rate_tables only. You are right, and my brief's
"any kind" was a lead brief error"*, citing the 05:43:54 text and that *"The consumer reads only
pins.rate_tables (rating_versions.py:1329, :1404-1408)"*, and that *"Other kinds, including
custom_objectives, are the class sweep's business: classify each as SAFE / GUARDED / LISTED."*

## Write set

| Path | What changes | Task |
|---|---|---|
| `backend/src/app/platform/rating_versions.py` `_pins_by_slug` (`:1404-1408`) and its two callers' docstring (`:1329-1339`) | the refusal (DP-G2 (a)): a slug seen twice in `rate_tables` raises `PlatformError("VALIDATION_FAILED", …, 409, …)` naming FD-1679 and the slug; the docstring says so | 2 |
| `backend/tests/test_rating_version_change_summary_route.py` | Reds 1–4 (Task 2); the existing tests unchanged | 2 |
| `docs/specs/03-rating-engine.md` §5.1 change-summary-draft row (`:1052`) | a dated clause: **409** `VALIDATION_FAILED` when either side's pins carry two versions of one rate-table slug (FD-1679); create is unchanged | 1 |
| `docs/roadmap.md` SL-1678 row; `docs/ledgers/LG-<working id>` | status lines and the slice ledger (L1 (a')) | 0, 3 |

The class sweep adds nothing to the write set: its GUARDED hits are this row's own lines (§Class sweep). `backend/src/app/api/models.py` is not
in the write set: 409 is already declared on the route (premise g), and
`docs/contracts/openapi/generated.json` does not move (Acceptance 5). No frontend file changes.

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch, cut from
  `origin/main`. `uv sync --all-packages`.
- [ ] Re-read premises a–i at the slice base and record each in the `LG-` with its locator. If
  `:1404` no longer reads as premise c, STOP to the lead.
- [ ] `gh pr list --state open`, and grep `to-lead.md` for entries since 2026-10-12 05:44:45 BST
  that rule on `FD-1679`, `pins_by_slug`, `change summary` or DP-K / DP-G1 / DP-G2. Name the SHA
  and the entries read. Use the ruled answer where one exists.
- [ ] Commit the `LG-` scaffold and the SL row's `active` line (L1 (a')).

### Task 1: Spec — `03` §5.1's change-summary-draft row

- [ ] Append to the row at `03-rating-engine.md:1052`, after its last parenthesis, this dated
  clause (DP-K (i); fill the date):

  ```text
  **409** `VALIDATION_FAILED` when the version's pins or its baseline's pins carry two versions of one rate-table slug (FD-1679): the summary pairs rate tables by slug and cannot pair them; `POST /api/v1/rating-versions` still accepts such pins (RL-1538). (**added <date>, SL-1678, FR-242**)
  ```

- [ ] `python3 scripts/audit-docs.py` in a gate-2 docs check; record the rc in the `LG-`.

### Task 2: The guard, red first

**Files:** Modify `backend/src/app/platform/rating_versions.py:1404-1408` (and `:1329-1339`
docstring); Test `backend/tests/test_rating_version_change_summary_route.py`.

**Interfaces:** `_pins_by_slug(pins: dict[str, Any] | None) -> dict[str, ArtifactRef]` keeps its
signature and raises `PlatformError` on a repeated slug. No new public name.

- [ ] **Step 1: Write Reds 1–4** in the test file, each with `@pytest.mark.req("FR-242")` (module
  marker). Seed two versions of one table slug with `_seed_table_version` (`one`, `two`), save
  `_algorithm(1)` and `_algorithm(2, extra_step=True)` with `_save_algorithms`.

  - **Red 1 — through the HTTP create route (entry 2):** create the baseline with
    `api_client.post("/api/v1/rating-versions", json={"slug": "motor-rv", "dataset_version_id": str(uuid4()), "model_ref": "model:motor-ad-frequency@7", "algorithm_ref": "rating_algorithm:minimal@1", "pins": _pins(X@one)}, headers=headers)` → 201;
    load that row by its returned `id` in a `database.unit_of_work()` and mark it approved with
    `backend.tests.approved_rows.mark_approved` (`approved_rows.py:92`) plus the
    `rating_version.approved` audit event, as `_insert(approved=True)` does (approval over HTTP
    needs the full FR-257 evidence, which is not this slice's subject; say so in a comment).
    Create the candidate the same way with `algorithm_ref` `…minimal@2` and
    `pins=_pins(X@two, X@one)` → **assert 201** (create stays permissive). `GET _url(candidate)`
    → assert **409**, `problem["code"] == "VALIDATION_FAILED"`, and the slug and `FD-1679` in
    `problem["detail"]`.
  - **Red 2 — the other order:** as Red 1 with the candidate pinning `_pins(X@one, X@two)`.
    Today: 200 with one entry `X one→two`. Assert the same 409.
  - **Red 3 — the baseline side:** baseline (via `_insert(approved=True)`) pinning
    `_pins(X@one, X@two)`, candidate pinning `_pins(X@two)`. Today: 200, `rate_tables == []`.
    Assert the same 409.
  - **Red 4 — a first version is answered:** a single version (no approved baseline) created
    over HTTP pinning `_pins(X@one, X@two)` → `GET` → assert **200**, `baseline is None`,
    `rate_tables == []` (premise e; DP-G2 (a)). This passes on `main` today; it pins the
    behaviour, and is not counted as a red.

- [ ] **Step 2: Run them on the base, before any code change:**
  `uv run pytest -q backend/tests/test_rating_version_change_summary_route.py -k "two_versions or first_version"`.
  Expected: Reds 1–3 FAIL, each **by its cause** — Red 1 with `200` and `rate_tables == []`,
  Red 2 with `200` and one `X one→two` entry, Red 3 with `200` and `rate_tables == []`; Red 4
  PASSES. Paste each failure line into the `LG-`. A red failing for another reason (fixture,
  401, 404) is not a red: fix the test first.

- [ ] **Step 3: The minimal code.** Replace `_pins_by_slug`'s body:

  ```python
  def _pins_by_slug(pins: dict[str, Any] | None) -> dict[str, ArtifactRef]:
      """A version's pinned rate tables by slug; a version without pins pins none.

      Refuses a version pinning two versions of one slug (FD-1679): pairing by slug would keep
      one of them and silently drop or mis-pair the other's change. `RL-1538` makes such pins
      valid input, so create accepts them; the pairing rule is WK-673's DP-P1.
      """
      if pins is None:
          return {}
      by_slug: dict[str, ArtifactRef] = {}
      for ref in Pins.model_validate(pins).rate_tables:
          if ref.slug in by_slug:
              raise PlatformError(
                  "VALIDATION_FAILED",
                  "Two versions of one rate table are pinned",
                  409,
                  f"The pins carry rate table {ref.slug!r} at versions "
                  f"{by_slug[ref.slug].version} and {ref.version}; the change summary pairs "
                  "rate tables by slug and cannot pair these (FD-1679).",
              )
          by_slug[ref.slug] = ref
      return by_slug
  ```

  Add one sentence to
  `draft_change_summary_for`'s docstring (`:1336`): *"Two versions of one rate-table slug on
  either side: 409 `VALIDATION_FAILED` (FD-1679)."*

- [ ] **Step 4: Run the file:** `uv run pytest -q backend/tests/test_rating_version_change_summary_route.py`.
  Expected: all pass, the existing tests unchanged.
- [ ] **Step 5: The broken-input proof.** Revert Step 3's `if` block locally; Reds 1–3 fail
  again; restore. Record both runs in the `LG-`.
- [ ] **Step 6: Commit** `fix(rating): the drafted change summary refuses two versions of one rate-table slug — SL-1678 (FD-1679)`.

### Task 3: The gate and the closing acts

- [ ] The full gate, both halves (`CLAUDE.md` §11), in the single gate slot, on
  `origin/main...<branch>`; the rc table goes in the `LG-`.
- [ ] Closing acts in the slice PR's last commit (L1 (a')): SL-1678 `closed` line; the `LG-`'s
  Audit section after the auditor's verdict. FD-1679's register line ("guard landed; DP-P1 open,
  owner WK-673") is the lead's or the minter's, not this slice's.

## Class sweep (the maintainer's predicate, verbatim)

**Authority.** The predicate is the maintainer's (by delegation), entry 05:44:45 (Context, entry
2). The run is the lead's ruling, from-lead "2026-10-12 05:47:19 BST": one `git grep` under
`flock -w 1800 /tmp/slots/gate-2`, the hits then read one file at a time, no tests or checks.

**The run.** Base `604ea084c96efe93f521fb9ba17738e05241e61a` (the planner's worktree HEAD; its
only changes are this file and `docs/roadmap.md`, outside the searched paths). At 2026-10-12
05:51:39 BST, from the repository root:

```bash
git grep -nE '\{[a-z_]+\.slug *:|\.slug\]? *=|by_slug' -- backend/src packages frontend/src
```

**rc 0, 99 hits**, every one read (by one read-only Explore subagent, file reads only; the
verdicts below are the planner's). The hits per file, `cut -d: -f1 | sort | uniq -c` over the
output: `rating_versions.py` 13, `deployments.py` 6, `perils.py` 6, `test_rate_tables.py` 5, and
1–4 in 35 other files.

**The predicate's reach.** `\.slug\]? *=` also matches `==` and `===`, so most hits are
comparisons, not maps. It does not match a TypeScript `new Map(… [r.slug, r])` or a
`reduce` keyed by slug, nor a tuple compare such as `(p.type, p.slug) == …`; the reading found
one such non-matched pin consumer in passing (`compile.py:731`, classified below).

**The lead's supplementary sweep for those forms.** The lead's from-lead entry "2026-10-12
05:57:28 BST" (`channel/from-lead-2026-10-09.md`) records one command, run under
`flock -w 1800 /tmp/slots/gate-2` at `origin/main` `604ea084`, verbatim from that entry:

```text
git grep -nE '\[[a-zA-Z_]+\.slug *,|\.slug\] *:|acc\[[a-zA-Z_]+\.slug\]|Object\.fromEntries' origin/main -- frontend/src backend/src packages (tests excluded by grep -v)
```

It gave **4 hits**, all read, in the entry's words: *"QuoteForm.vue:39 (field.name),
PredictionView.vue:60,:70 (column), RateTableEditorView.vue:60 (cell key) — none slug-keyed,
none pin consumers; plus 'new Map(' in frontend/src: 4 (f.id, step id x2, id) — none slug.
Supplementary result: SAFE, nothing added."* So the TypeScript-form limit is closed as **SAFE**:
the `new Map(` forms in `frontend/src` key on an id or a `step_id`, never a slug. The tuple-compare
form is covered only by the one case read in passing (`compile.py:731`).

### Pin consumers

| Hit | What it does with pins | Verdict | Why / owner |
|---|---|---|---|
| `backend/src/app/platform/rating_versions.py:1404`, `:1408` | `_pins_by_slug`: `{ref.slug: ref for ref in …rate_tables}` | **GUARDED** by SL-1678 | the defect: last ref per slug wins. Task 2 makes it refuse; the pairing fix is DP-P1 (open, owner WK-673) |
| `rating_versions.py:1377`, `:1378` | `before`/`after` in `draft_change_summary_for` | **GUARDED** by SL-1678 | the two callers of `_pins_by_slug`; refused through it |
| `rating_versions.py:616` | `WorkspaceResolver.resolve`, the algorithm branch | SAFE | one SQL lookup per ref on slug **and** version (`:617`); compile stores results under `str(ref)` (`compile.py:1057-1066`) |
| `rating_versions.py:764` | `WorkspaceResolver.resolve`, the factor branch (factor refs of pinned rate tables' keys) | SAFE | slug and version (`:765`) |
| `backend/src/app/platform/rate_tables.py:299` | `_load_table` for a `rate_tables` pin via the resolver (`rating_versions.py:702-707`) | SAFE | the table row by slug, then `_load_version(table_row.id, ref.version)` (`rate_tables.py:1159-1161`) |
| `backend/src/app/platform/reference.py:317` | `_load_table` for a `reference_tables` pin (`rating_versions.py:722-731`) | SAFE | slug, then a version filter (`reference.py:467`, `:498`) |
| `backend/src/app/platform/objectives.py:530` | `resolve_ref` for a `custom_objectives` pin (`rating_versions.py:752-754`) | SAFE | slug and version (`:531`) |
| `backend/src/app/platform/perils.py:491` | `load_structure_by_ref` for a peril-structure `models` pin (`rating_versions.py:777`) | SAFE | slug and version (`:492`) |
| `backend/src/app/platform/sub_graphs.py:168` | `_row` for a `sub_graphs` pin (`rating_versions.py:589` → `sub_graphs.py:226`) | SAFE | slug and version (`:169`) |
| `packages/pricing-core/src/pricing_core/rating/compile.py:820`, `:822` | `by_slug` over one resolved model pin's **factors** (`_refuse_control_factor_model_calls`) | SAFE | the pin is fetched as `resolved_pins[str(model_ref)]` (`:817`); the map is keyed by factor slug inside one model, which has one factor per slug |
| `packages/pricing-core/src/pricing_core/rating/runtime.py:877` | `columns` keyed by factor slug for one GLM's own factors (`_glm_scorer`) | SAFE | scorers are keyed by `str` ref (`:885-897`); the slug map is inside one model |
| *(not a hit)* `compile.py:731` | `check_step_refs_pinned`: after the exact `ref in pinned` test fails, `next(p for p in pinned if (p.type, p.slug) == (ref.type, ref.slug))` | SAFE | the refusal is decided by the exact test (`:729`); the slug match only fills the message's *"(pinned at … instead)"*, which names the first of several pinned versions. True, not complete; no verdict or price depends on it |

**LISTED: none.** No pin consumer outside the change summary keys pins by slug alone. FD-1679's
remaining limb is DP-P1 (the pairing fix), owner WK-673.

### Not pin consumers — one line each

- `backend/src/app/api/approvals.py:450` — SQL: the Rating Version under approval, slug and version (`:451`).
- `backend/src/app/api/score.py:220` — SQL join on the caller's Environment slug.
- `backend/src/app/api/service_accounts.py:200` — SQL uniqueness check on a Service Account slug.
- `backend/src/app/platform/datasets.py:237` — SQL: the one Dataset row of a slug.
- `datasets.py:830` — SQL: Dataset Version for approval, slug and version (`:831`).
- `deployments.py:108` — SQL: the Rating Version being deployed, slug and version (`:109`).
- `deployments.py:150` — SQL: the predecessor Environment by slug.
- `deployments.py:288` — SQL: `max(version)` of a Deployment Request per Environment slug (next number).
- `deployments.py:347` — SQL: Deployment Request ref resolve, slug and version (`:348`).
- `deployments.py:398` — SQL: Deployment Request FOR UPDATE at decision, slug and version (`:399`).
- `deployments.py:596` — SQL: Deployment Request by its named ref, slug and version (`:597`).
- `environments.py:100` — SQL: Environment id by slug.
- `environments.py:143` — SQL: Environment by slug.
- `environments.py:159` — SQL: Environment by slug.
- `environments.py:211` — SQL: Environment slug uniqueness at create.
- `metrics.py:201` — SQL: latest Custom Metric version of a slug (next number).
- `metrics.py:319` — list filter by slug.
- `metrics.py:384` — SQL: Custom Metric ref resolve (`GbmSpec.eval_metrics`), slug and version (`:385`).
- `metrics.py:576` — SQL: Custom Metric FOR UPDATE at decision, slug and version (`:577`).
- `modelling.py:240` — SQL: `max(version)` of a Factor slug (next number).
- `modelling.py:362` — SQL: `load_factor_by_ref` for a rate table key's `factor_ref`, slug and version (`:363`).
- `objectives.py:209` — SQL: latest Custom Objective version of a slug (next number).
- `objectives.py:462` — list filter by slug.
- `objectives.py:823` — SQL: Custom Objective FOR UPDATE at decision, slug and version (`:824`).
- `perils.py:122` — SQL: latest Peril Structure version of a slug (next number).
- `perils.py:419` — list filter by slug.
- `perils.py:463` — SQL: Peril Structure approval resolve, slug and version (`:464`).
- `perils.py:529` — SQL: Peril Structure FOR UPDATE at decision, slug and version (`:530`).
- `perils.py:763` — SQL: earlier approved versions of the same slug (supersede), `version < approved.version`.
- `rate_tables.py:196` — SQL: the one Rate Table row of a slug, at seed.
- `rate_tables.py:272` — `_key_takes_the_seed`: one table's key `factor_ref` slug against the seed's Factor slug, at any version by design (docstring `:252`).
- `rate_tables.py:1549` — SQL: the Rate Table row for a bulk operation, then `_load_version(…, version)` (`:1556`).
- `rating_algorithms.py:242` — SQL: existence check, slug and version (`:243`).
- `rating_algorithms.py:257` — SQL: highest existing version of a slug (the audit `before`).
- `rating_algorithms.py:294` — SQL: `get_algorithm`, slug and version (`:295`).
- `rating_versions.py:214` — SQL: `resolve_rating_version_ref`, slug and version (`:215`).
- `rating_versions.py:287` — SQL: the algorithm at create, slug and version (`:288`).
- `rating_versions.py:295` — SQL: `max(version)` of a Rating Version slug (next number).
- `rating_versions.py:514` — SQL: Rating Version FOR UPDATE at decision, slug and version (`:515`).
- `rating_versions.py:1202` — SQL: `_algorithm_of`, slug and version (`:1203`).
- `rating_versions.py:1297` — `_baseline`: approved versions whose `algorithm_ref` slug is the algorithm's, any version by design; rows keyed `rating_version:slug@version` (`:1301`).
- `rating_versions.py:1488` — `_golden_quote_delta`: the baseline check's suite slug against the suite's, with `suite_ref.version in by_number` (`:1489`).
- `rbac.py:334` — SQL: Role by slug.
- `rbac.py:430` — SQL: Role by slug.
- `regression_suites.py:79` — SQL: the suite registry row of a slug.
- `regression_suites.py:110` — SQL: latest algorithm version for the suite's algorithm slug.
- `settings.py:364` — SQL: Environment slug in a setting lookup.
- `settings.py:424` — SQL: Environment slug in a settings list.
- `settings.py:559` — SQL: Environment id by slug.
- `sub_graphs.py:57` — SQL: `max(version)` of a Sub-graph slug (next number).
- `sub_graphs.py:190` — `list_versions` filter by slug.
- `transformations.py:278` — SQL: `max(version)` of a Banding slug (next number).
- `transformations.py:335` — SQL: `max(version)` of a Grouping slug (next number).
- `transformations.py:423` — SQL: `load_banding_by_ref` for a rate table key's `banding_ref`, slug and version (`:424`).
- `validation_rules.py:241` — SQL: `max(version)` of a Validation Rule slug (next number).
- `validation_rules.py:348` — SQL: Validation Rule approval resolve, slug and version (`:349`).
- `validation_rules.py:526` — SQL: Validation Rule FOR UPDATE at decision, slug and version (`:527`).
- `validation_rules.py:852` — SQL: `max(version)` of a Rule Set slug (next number).
- `frontend/src/views/ModelSpecBuilderView.vue:226` — `find` of the chosen Dataset by slug in a list.
- `frontend/src/views/ReferenceView.vue:35` — `find` of the selected reference table by slug; its version is chosen separately (`:36`).
- `ReferenceView.vue:190` — CSS class for the selected row.
- `packages/pricing-core/src/pricing_core/modelling/ebm.py:176` — a factor by slug within one fit's factors.
- `modelling/factors.py:228` — `terms[factor.slug]`, one spec's design-matrix terms.
- `modelling/factors.py:238` — the same, the other branch.
- `modelling/gbm.py:392` — `by_slug` over one fit's factors (the monotone vector).
- `modelling/gbm.py:395` — `by_slug[slug]` read of the same map.
- `rate_tables/operations.py:206` — seed: one model's Factors whose slug matches; more than one raises (`:212-216`).
- `rate_tables/weights.py:66` — `_find_banding`: a key's `banding_ref`, slug **and** version on the same line.
- `packages/model-schema/tests/test_dataset_version.py:46` — test assertion.
- `packages/model-schema/tests/test_rate_tables.py:55` — test assertion.
- `test_rate_tables.py:72` — test assertion.
- `test_rate_tables.py:224` — test assertion.
- `test_rate_tables.py:233` — test assertion.
- `test_rate_tables.py:401` — test assertion.
- `packages/model-schema/tests/test_rating_algorithm.py:95` — test assertion.
- `packages/model-schema/tests/test_sub_graph.py:48` — test assertion.
- `packages/model-schema/tests/test_validation_catalogue.py:82` — test assertion.
- `packages/pricing-core/tests/test_rate_table_bulk_ops.py:153` — test assertion.
- `packages/pricing-core/tests/test_rate_table_operations.py:152` — test assertion.
- `packages/pricing-core/tests/test_rating_compile_bundle.py:130` — test assertion.
- `test_rating_compile_bundle.py:289` — test assertion.
- `packages/pricing-core/tests/test_testing.py:288` — test assertion.
- `packages/pricing-core/tests/test_validate.py:81` — a dict keyed by `rule_slug` over one validation report's results.
- `test_validate.py:82` — assertion on that dict.
- `test_validate.py:83` — assertion on that dict.

**Tally:** 4 GUARDED + 10 SAFE pin consumers (12 table rows; `compile.py:820`/`:822` share one
row) + 85 not pin consumers = 99.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root.

1. **The refusal, both sides, both orders:** Reds 1–3 pass:
   `uv run pytest -q backend/tests/test_rating_version_change_summary_route.py -k two_versions`
   exits 0, and the `LG-` shows each failing on the base by its cause (Task 2 Step 2) and again on
   the planted reversal (Step 5).
2. **Create stays permissive:** Red 1 asserts the 201 for the candidate pinning one slug twice;
   `git diff origin/main -- backend/src/app/platform/rating_versions.py` touches no line in
   `create_rating_version` (`:258-330` at the base).
3. **A first version is still answered:** Red 4 passes (200, `baseline` null, no rate-table entry).
4. **Existing behaviour holds:** the file's existing tests pass unchanged (`git diff origin/main
   -- backend/tests/test_rating_version_change_summary_route.py` adds lines only).
5. **No contract drift:** `uv run python scripts/generate-contracts.py --check` exits 0, and
   `git diff origin/main --stat -- docs/contracts` prints nothing.
6. **The spec says it:** `grep -n 'FD-1679\|VALIDATION_FAILED' docs/specs/03-rating-engine.md`
   shows the dated clause on the change-summary-draft row; `python3 scripts/audit-docs.py`
   exits 0 with the slice's `LG-` minted.
7. **The gate is green on the merge tree:** the `CLAUDE.md` §11 commands, both halves, each exit 0
   against `origin/main...<slice branch>`.

## Global Constraints

- `CLAUDE.md` §2: no shape written twice; `docs/contracts/` generated, never hand-edited.
- `RL-1538`: two versions of one slug are valid pins; create is not narrowed.
- `pricing-core` stays free of FastAPI/SQLAlchemy; no pandas. This slice does not touch it.
- One PR per slice (L1 (a')): code, tests, spec clause, SL status line, one `LG-`.
- `RL-1445` item 1: one full gate at a time; targeted single-file runs only outside it.
- Order: merges before `SL-1543` (Context, entry 1).

## Hand-off (not this plan's writes)

- **The WK-673 roadmap row** lists this delta as a Work-plan delta; the planner's charter limits
  its roadmap writes to the `SL-` rows it cuts. The line was written in the mint PR by
  delegation of the lead (from-lead "2026-10-12 05:58:38 BST").
- **FD-1679** (minted in the same PR) carries the class-sweep table above and DP-P1 as its
  remaining limb.
- **DP-P1** goes to the decision-maker for WK-673's plan when the lead schedules it; it is not a
  G2 blocker once this guard has merged.

## Self-review

- **Spec coverage.** FR-242's drafting limb refuses where it cannot pair, in code (Task 2) and in
  `03` §5.1 (Task 1). FR-237's create path is unchanged and tested (Red 1's 201).
- **Placeholders.** `<date>` and the `LG-` working id are filled at execution. No other
  placeholder.
- **Type consistency.** `_pins_by_slug` keeps its signature; `PlatformError(code, title, status,
  detail)` is the form used at `:1346-1351`.
- **Literals.** Every `file:line` was read at `604ea084`.
- **The class sweep.** Run once, as one command under the gate-2 flock (the lead's 05:47:19
  ruling); all 99 hits read by one Explore subagent with file reads only; the planner re-read
  `compile.py:722-740` and `:813-823` itself before classifying them. The verdicts are the
  planner's. The bullets of the not-pin list were counted (`85`) against the tally.
- **Convention 4.** The to-lead entries read up to 05:44:45 BST and the from-lead entries up to
  05:48:32 BST on 2026-10-12. The planner did not run `gh pr list`; Task 0 runs it, and the lead
  re-checks open writers at the GO (activation need 3).
