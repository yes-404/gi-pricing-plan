---
id: PL-8181
family: plan
kind: map
title: WK-1178 — FD 8177, a dataset-scoped grant reaches the three writes whose handler checks the Dataset (dictionary, rule set, acknowledgement), and a permanent guard against the pattern — a dated Work-plan delta cutting one slice
status: draft                  # draft → active → superseded | retired (§1.2a) — draft: DP-1, DP-2 and DP-3 are blocking and open
created: 2026-10-22
owner: planner
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1301, RL-1687, FR-343, FR-345, FR-46, FR-51, FR-452]
---

# PL-8181 — WK-1178: FD 8177, a dataset-scoped grant reaches its three scoped writes

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md`
> §1.6, PL row). It cuts **one fix slice** (its `SL-` id and its `LG-` id are not reserved
> yet; this draft calls the slice **"the slice"**). The executor is spawned from
> `.claude/roles/executor.md` and binds `test-driven-development`, `python-test`,
> `python-package`, `fastapi-service`, `spec-change`, `dev-commands` and `git-hygiene`. The
> ledger is filed by the executor at build; this plan names it and does not create it.
> Written by planner-8177 (Claude Opus 5.5), 2026-10-22, at tree `71e481fa` (origin/main).

## The ruling this plan carries out

The maintainer's entry "2026-10-22 17:27:15 BST — Maintainer: FD 8177 CONFIRMED HIGH; planner
GO for the fix slice; the FR-345 spec question goes to a decision-maker in parallel" in
`to-lead.md`, verbatim (the binding conditions):

> - **No objection to the route:** release exec-8177, then seat a planner (opus) to cut ONE fix slice covering the 3 swept routes (api/datasets.py:88; api/validation.py:68 and :70) and to name the owner Work. Conditions:
>   - **red-first for ALL THREE routes** (the 2 unprobed ones get their own failing tests at base);
>   - the control on dataset Y must assert **SCOPE_DENIED** from the handler, not the route's PERMISSION_DENIED (the caveat raised);
>   - **a regression guard:** a test that FAILS if any route pairs a scope-less route-level `requires()` with a handler-level scoped check (the sweep's predicate, made permanent), red-first via an injected route;
>   - **sequenced around SL-1736's Task 1** edits to validation_rules.py (no shared-file overlap in flight).

And from the entry "2026-10-22 17:21:38 BST" item 4: severity **HIGH**, "owner = the Work owning
datasets RBAC", "The fix is a slice cut by a planner". FD 8177 is a P2 HIGH, "resolved before
P2's close (§14)" (17:27:15).

## Verified first, at `71e481fa`

Each fact read in the source at the tree above (my own reads, not the relay):

1. **The route gate.** `backend/src/app/api/authz.py`:170 `def requires(permission, *,
   keep_session=False, management_counted=True)` calls `rbac.require_permission(...)` with **no
   `resource`**, then counts the request (`:205`–`:206`), and tags the dependency with
   `PERMISSION_ATTRIBUTE` and `MANAGEMENT_COUNTED_ATTRIBUTE` (`:211`–`:212`).
2. **Why a scoped grant fails it.** `backend/src/app/platform/rbac.py`:205 `_covers`: a
   non-workspace assignment with `resource is None` returns `False` (`:208`–`:211`).
3. **The three affected routes** (exec-8177's sweep, `scratch/fd-8177/result.md`, re-read here):
   - `PUT /api/v1/datasets/{slug}/dictionary` — `api/datasets.py`:88 `WriteDatasets =
     ...requires(Perm.DATASET_WRITE)`, route `:495`, handler `:499`; the scoped check is
     `platform/datasets.py`:282–288 (`update_dictionary`, def `:266`), load first (`:281`).
     **Probed, refused**: probe `f4c0832f`, `assert 403 == 200`, `PERMISSION_DENIED`.
   - `PUT /api/v1/datasets/{slug}/rule-set` — `api/validation.py`:68 `WriteDatasets`, route
     `:430`, handler `:434`, loads the dataset then calls `rule_service.replace_rule_set` at
     `:446`; the scoped check is `platform/validation_rules.py`:824–830 (def `:808`). Unprobed.
   - `POST /api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge` —
     `api/validation.py`:70 `AcknowledgeWarnings = ...requires(Perm.DATASET_ACKNOWLEDGE_WARNING)`,
     route `:155`, handler `:160`, calls `service.acknowledge` at `:169`; the scoped check is
     `platform/validation.py`:258–266 (`has_permission`, resource the version's dataset), def
     `:226`. Unprobed. **On refusal it raises `ACKNOWLEDGE_FORBIDDEN_ROLE`** (`:274`–`:280`),
     never `SCOPE_DENIED` — see DP-3.
4. **`rbac.holds_anywhere` exists** (`rbac.py`:219): "Does the principal hold this permission
   under any scope?" It reads role assignments only; it does not take `credential_permissions`.
5. **The handler-counted pattern exists.** `authz.py`:155 `management_counter` returns the count
   unrun; the service awaits it right after its own permission check, "so a `403` is never
   counted". Used by `platform/validation_rules.py`:200/`:230` (`count_management`) and
   `platform/deployments.py`:139. The rule is `07` FR-452 as amended by `RL-1687` (1a): "The
   count runs after authentication and after the route's own permission check ... so a `401`
   or a `403` is never counted, and before the route does any work."
6. **The sweep tests.** `backend/tests/test_api_authorisation_sweep.py`:
   `HANDLER_GUARDED` (`:83`), `RESOURCE_BACKED` (`:299`, Environment paths only), the no-role
   test `:367` (asserts 403 **and** `PERMISSION_DENIED` for every route outside
   `HANDLER_GUARDED`). `backend/tests/test_management_429_declared.py`:107 `_counts` treats a
   route as counted if any dependency carries `MANAGEMENT_COUNTED_ATTRIBUTE` or is
   `management_counter`.
7. **RL 8176 (adopted, not minted; `draft/rl-8176` @`aab1b741`)** writes into `06` FR-343:
   "a route's permission check precedes any lookup of an id its path names, so a caller without
   the permission is refused with 403 whether or not the id exists. **One exception:** ... an
   **Environment**". Its reason (A) item 1: the order rule "protects ids whose existence is
   itself access-controlled, such as datasets and models". The maintainer's 17:21:38 item 2
   rules a test: **`RESOURCE_BACKED` may hold only `/api/v1/environments/{env}/` paths.**
8. **The built-in roles.** `packages/model-schema/src/model_schema/permissions.py`:137–144:
   `dataset:acknowledge_warning` is held by `pricing_actuary`, not `analyst`.

## Owner Work — **WK-1178** recommended; DP-0 confirms

Two candidates, with evidence:

| Candidate | For | Against |
|---|---|---|
| **WK-676** "Full scoped RBAC, custom roles, break-glass" (`docs/roadmap.md`:3098) | Its row lists `06` FR-342 … FR-349, **FR-345 included** (`:3110`); it is the spec owner of scoped RBAC. | `phase: P3` (`:3107`). FD 8177 is a **P2** HIGH that must be resolved before P2's close; a P3 Work cannot carry a P2 close obligation, and `CLAUDE.md` §0 forbids building ahead of the phase. |
| **WK-1178** "P2 standing maintenance: hotfixes, dependency bumps and security findings" (`docs/roadmap.md`:1916) | `phase: P2`, `status: active`; scope "work that belongs to no other Work; each item names its `FD-`". The dataset routes and their scoped checks were delivered by **WK-659** (P1a, closed 2026-08-14, `:248`), so no open P2 Work owns them. RL 8176 (adopted) puts FD 8175's sibling fix in a WK-1178 delta row. | It is not the spec owner of FR-345; the slice changes no FR-345 *scope*, only the order and the gate, so this costs nothing. |

**Recommendation: WK-1178**, with WK-676 named in the FD as the spec owner of FR-345 for any
later scoped-RBAC work. Ambiguous enough that the maintainer confirms it (DP-0).

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-0 | Which Work owns the fix? | WK-1178 · WK-676 | **WK-1178** (table above) | scope | yes | |
| DP-1 | How does a route admit a scoped grant and still refuse a caller with no grant first? | (a) B.2 pattern · (b) "held anywhere" route gate + the existing scoped check · (c) other | **(b)** (below) | decision point | yes | |
| DP-2 | `06` text: the order for a permission that can be held on a named Dataset | (i) held-anywhere counts as "holding it" for FR-343's order; a holder on another Dataset sees 404 for an unknown slug and `SCOPE_DENIED` for an existing one · (ii) a scoped holder gets 403 for an unknown slug too | **(i)** (below) | decision point | yes | |
| DP-3 | The acknowledge refusal for a holder whose grant is on another Dataset | `SCOPE_DENIED` (`06` §5.1) · keep `ACKNOWLEDGE_FORBIDDEN_ROLE` (`01` §5.1) | **`SCOPE_DENIED`** when held elsewhere; `ACKNOWLEDGE_FORBIDDEN_ROLE` kept when held nowhere | decision point | yes | |

### DP-1 — the design options

| | (a) RL-1301 B.2 pattern: drop the route `requires()`, guard in the handler with the resource | (b) `requires(..., held_anywhere=True)` route gate + the handler's scoped check | (c) a route dependency that loads the Dataset by slug and checks with the resource |
|---|---|---|---|
| **Order** | load → 404 → scoped 403. A **no-grant** caller learns whether a dataset slug or a report id exists. | held anywhere? else 403 `PERMISSION_DENIED` → load → 404 → scoped 403 `SCOPE_DENIED` | as (b), but inside the dependency |
| **RL 8176 (adopted)** | **Breaks its FR-343 order rule**: the one exception is Environments, and its reason (A) item 1 names datasets as ids whose existence is access-controlled. | Kept: a caller with no grant is refused 403 whether or not the id exists. This is exactly RL 8176's option (C) form, applied where its reason says it belongs. | Kept |
| **Sweep lists** | All three routes need `HANDLER_GUARDED` entries **and** `RESOURCE_BACKED` entries (the no-role test fills an unknown id and would get 404). The second is **forbidden** by the guard the maintainer ruled on 17:21:38 item 2. | **No change.** The route still declares its permission (`_declares_a_permission`), and a no-role caller still gets `PERMISSION_DENIED` from the route. | No change |
| **FR-452 count** | Count via `management_counter`, awaited in the service after the check. | Same: the gate must **not** count (a `SCOPE_DENIED` would then be counted, against FR-452's "a 403 is never counted"); the handler takes `management_counter` and the service awaits it after its scoped check. | The dependency counts after its own scoped check; the service's check becomes a duplicate. |
| **Churn** | three services, two sweep lists (in a file SL-1260 and FD 8175's vehicle also edit), the order clause | `authz.py` (one keyword), three route aliases, three services gain `count_management`, one service's refusal code (DP-3) | a new resolver per route kind; the acknowledge route has no slug (report → version → dataset), so a second resolver; a double load and a double check |

**Recommendation: (b).** It is the only option that keeps RL 8176's order rule without a new
exception, it needs no change to either sweep list (so no overlap with SL-1260 or the FD 8175
vehicle), it reuses `rbac.holds_anywhere` and the established `count_management` pattern, and
the scoped check stays where it is. (a) is ruled out by the adopted RL 8176 and its guard; (c)
duplicates the check.

**Shape of (b), for the executor** (not a ruling on names): `requires(permission, *,
held_anywhere=False, ...)`. With `held_anywhere=True` the dependency (1) admits if
`permission.value in caller.permissions` (credential grants, as `:203` passes them today) or
`rbac.holds_anywhere(...)`; (2) otherwise raises `PermissionDeniedError(permission, None,
held_elsewhere=False)` (`PERMISSION_DENIED`); (3) **never counts**, and refuses construction
with `management_counted=True` (a `ValueError` at import, so the combination cannot be
written); (4) sets `PERMISSION_ATTRIBUTE` and a new attribute marking the resource check as the
handler's (e.g. `RESOURCE_CHECKED_IN_HANDLER_ATTRIBUTE`), which the guard reads.

### DP-2 — the order clause (spec first)

Under (b) a principal holding `dataset:write` on Dataset X sees 404 for an unknown slug and
`SCOPE_DENIED` for an existing Dataset Y, so it learns whether a slug exists. The maintainer's
condition already requires `SCOPE_DENIED` on Y, which implies this; the spec should say it.

- **(i), recommended:** "held on some scope" counts as holding the permission for FR-343's
  order. The answer reaches only a principal the workspace has already granted the permission
  on a named Dataset, never a caller with no grant.
- **(ii):** a scoped holder gets 403 for an unknown slug too. It needs a refusal that names no
  resource, and it turns a typo by a legitimate user into a misleading 403.

The text goes into **`06` FR-345** as a dated clause, not FR-343, so it does not share a row
with RL 8176's FR-343 clause in flight. Draft wording, the executor's first hunk (spec first,
same commit as nothing else):

> *(Amended <date>, <SL id>, FD-<n>.)* **A permission held on a named resource is checked in
> two steps.** A route whose permission may be held on a named Dataset first checks that the
> caller holds it **on some scope**, and refuses with 403 `PERMISSION_DENIED` otherwise, whether
> or not the id exists (FR-343's order). The handler then loads the resource (404 `NOT_FOUND`
> if unknown) and checks the permission **on that resource**, refusing with 403 `SCOPE_DENIED`.
> A route-level check that names no resource refuses every scoped grant, which is the failure
> `RL-1301` B.2 item 2 names; FD-<n> found it on three Dataset writes. A principal holding the
> permission on another Dataset therefore learns whether a slug exists; that is accepted.

### DP-3 — the acknowledge refusal

`platform/validation.py`:274 raises `ACKNOWLEDGE_FORBIDDEN_ROLE` ("requires the Pricing Actuary
role") for any refusal. Under (b) the route already refuses a principal who holds the
permission nowhere (`PERMISSION_DENIED`, as today), so the service's refusal is reached by an
actuary whose grant is on another Dataset, and "requires the Pricing Actuary role" is false for
them. **Recommendation:** the service raises `SCOPE_DENIED` (via `require_permission` with the
resource, or `PermissionDeniedError(..., held_elsewhere=True)`) when `holds_anywhere` is true,
and keeps `ACKNOWLEDGE_FORBIDDEN_ROLE` when it is false. `test_validation_reports.py`:134
(an analyst calling the service directly, held nowhere) keeps asserting
`ACKNOWLEDGE_FORBIDDEN_ROLE` unchanged. No `01` text changes (`06` §5.1 owns `SCOPE_DENIED`;
`01` §5.1 keeps its code).

## Goal

A principal whose `dataset:write` or `dataset:acknowledge_warning` grant is scoped to Dataset X
can use the three routes on X; on Dataset Y it is refused with `SCOPE_DENIED` by the handler; a
principal holding the permission nowhere is still refused 403 `PERMISSION_DENIED` by the route
before any lookup; no `403` is counted; and a permanent test fails if any route pairs a
scope-less route-level `requires()` with a scoped check reached from its handler.

## The slice (one row under WK-1178)

- **Title:** WK-1178 fix slice — FD 8177: a dataset-scoped grant reaches the dictionary, rule-set
  and acknowledge writes (held-anywhere route gate), and a permanent guard against a scope-less
  route gate over a scoped handler check.
- **Requirements:** `06` FR-343, FR-345 (dated clause, DP-2); `01` FR-46, FR-51 (the routes'
  own FRs, behaviour unchanged for workspace-wide grants); `07` FR-452 (no 403 counted).
- **Dependencies:** RL 8176's docs batch merged to main before the spec commit (both amend the
  `06` §3.1 table); **SL-1736 merged to main before Task 4** (below).
- **Lane / order:** backend, one executor; any lane free of SL-1736's files. Severity HIGH:
  dispatch next after the GO.
- **Write set:** `docs/specs/06-governance.md` (FR-345 row only); `backend/src/app/api/authz.py`;
  `backend/src/app/api/datasets.py`; `backend/src/app/api/validation.py`;
  `backend/src/app/platform/datasets.py`; `backend/src/app/platform/validation.py`;
  `backend/src/app/platform/validation_rules.py` (Task 4 only, `replace_rule_set`'s signature
  and its count line); new `backend/tests/test_dataset_scoped_writes.py`; new
  `backend/tests/test_route_scope_guard.py`. **Not** in the write set:
  `test_api_authorisation_sweep.py` (SL-1260 and the FD 8175 vehicle edit it), `rbac.py`'s
  `_covers` (unchanged), `docs/specs/01-data-management.md` (SL-1736 edits it).

## Tasks

Test-first: each red is shown at base before its fix, with the rc in the LG. DB-backed tests run only through `run-small.sh` (≤3 files), in a DB window the lead grants.

1. **Spec first.** Re-merge main (RL 8176's batch present). Add DP-2's clause to `06` FR-345 as
   ruled. `audit-docs.py` under the gate-2 flock; rc quoted.
2. **Red tests for all three routes** — `backend/tests/test_dataset_scoped_writes.py`, built from
   probe `f4c0832f`'s `test_dataset_scoped_write_probe.py` (its `world` fixture). For each route
   R ∈ {dictionary, rule-set, acknowledge}, with Datasets X and Y in one workspace:
   - **R-in-scope:** a principal whose grant is scoped to X only (`analyst` for the two writes,
     `pricing_actuary` for acknowledge, on a report of X's version with a `warn` result) →
     2xx. **Red at base:** 403 `PERMISSION_DENIED`.
   - **R-out-of-scope (the control the maintainer required):** the same principal on Y →
     403 with `code == "SCOPE_DENIED"`. **Red at base:** `PERMISSION_DENIED` from the route.
     For acknowledge, red until DP-3's change too.
   - **R-workspace:** a workspace-wide holder on X → 2xx. Green at base; must stay green.
   - **R-no-grant-unknown-id:** a member with no role, unknown slug / report id → 403
     `PERMISSION_DENIED` (FR-343 order, RL 8176). Green at base; must stay green.
   - **Count (dictionary only):** with a management limit set, an out-of-scope `SCOPE_DENIED`
     leaves the count unchanged (`07` FR-452). Green at base; it fails if the gate counts.
   Show the six R-in-scope / R-out-of-scope tests red at base (rc 1, each `FAILED` line
   quoted), the rest green.
3. **The gate keyword.** `requires(..., held_anywhere=True)` per DP-1's shape. Switch
   `api/datasets.py` `put_dictionary` and `api/validation.py` `acknowledge` to a held-anywhere
   alias plus `management_counter`; `update_dictionary` and `acknowledge` take
   `count_management` and await it right after their scoped check. DP-3's refusal change in
   `acknowledge`. **Do not** change `WriteDatasets` for the other routes using it
   (`datasets.py`:178, `:213`, `:281`, `:524`, `:760`): they create or act without a named
   Dataset check, and the FR-345 spec question (below) owns them.
4. **The rule-set route — starts only after SL-1736 has merged to main and the slice has
   re-merged main.** Same switch for `put_rule_set` (`api/validation.py`:434);
   `replace_rule_set` takes `count_management` and awaits it after its check.
5. **The permanent guard** — `backend/tests/test_route_scope_guard.py`:
   - **Predicate.** A route is *gated without scope* when one of its dependencies (recursively)
     carries `PERMISSION_ATTRIBUTE` and not the held-anywhere attribute. A route *reaches a
     scoped check* when its endpoint's AST calls a function of an `app.platform` module (by
     the endpoint module's import alias), and that function — or a function of the same module
     it calls, to depth 3, cycle-safe — contains a call to `require_permission` or
     `has_permission` with a `resource=` keyword that is not the constant `None`. The guard
     fails, naming route and site `file:line`, on every route that is both.
   - **Coverage control (it cannot go blind):** the set of scoped-check functions the AST finds
     equals the set of functions enclosing the hits of exec-8177's predicate 2, run in the
     test verbatim: `grep -rn "ResourceRef(" backend/src/app --include=*.py`, excluding
     `platform/rbac.py`. At `71e481fa` those are `platform/validation.py`:264,
     `platform/deployments.py`:136, `platform/datasets.py`:287,
     `platform/validation_rules.py`:829.
   - **Red first, twice:** (i) at base, before Task 3, the guard fails naming exactly the three
     routes (quoted in the LG); (ii) a permanent test feeds the guard a synthetic route (a
     test-local `APIRouter` whose endpoint carries a scope-less `requires(DATASET_WRITE)` and
     calls `platform.datasets.update_dictionary`) and asserts it is flagged.
   - **Negative control:** the deployment routes (handler-guarded, no route `requires`) are not
     flagged; after Tasks 3–4 the guard is green on the whole app.
6. **Green.** The GREEN set by import closure (common brief item 29: changed modules from
   `git diff --name-only origin/main...HEAD -- backend/src`, their importers, one more level,
   then every test file importing the closure), each through `run-small.sh`, including
   `test_api_authorisation_sweep.py`, `test_management_429_declared.py`, `test_rbac.py` and
   `test_validation_reports.py`. Then the slice gate, on the lead's grant.

## Acceptance Standard

1. At base (`origin/main` + Task 2's file only), `run-small.sh` on
   `backend/tests/test_dataset_scoped_writes.py` exits 1 with exactly the six R-in-scope /
   R-out-of-scope tests `FAILED`; at the slice head it exits 0.
2. At base + Task 5's file only, `test_route_scope_guard.py`'s app-wide test exits 1 and names
   exactly `PUT /api/v1/datasets/{slug}/dictionary`, `PUT /api/v1/datasets/{slug}/rule-set` and
   `POST /api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge`; at the slice head
   the whole file exits 0, including the synthetic-route test that asserts the injected route
   is flagged.
3. `test_api_authorisation_sweep.py` and `test_management_429_declared.py` exit 0 at the slice
   head **with no diff to either file** (`git diff --stat origin/main...HEAD --` both paths is
   empty).
4. `git diff origin/main...HEAD -- docs/specs/06-governance.md` touches the FR-345 row only and
   carries DP-2's clause as ruled; `python3 scripts/audit-docs.py` (gate-2 flock) exits 0.
5. The slice gate (both halves, `dev-commands`), on the lead's grant, is green at the slice head;
   the MERGE-ACK quotes its `passed` line.

## Clashes and sequencing

- **SL-1736** (`sl-1736-wk1178-nfr-sweep` @`ef1d0efb`) edits
  `platform/validation_rules.py` hunks `@@ -805,6 +805,21 @@`, `@@ -852,14 +867,18 @@`,
  `@@ -905,15 +924,8 @@` — inside `replace_rule_set` — and `docs/specs/01-data-management.md`.
  Only Task 4 touches `validation_rules.py`; it starts after SL-1736 merges. The slice never
  touches `01`.
- **SL-1260** (`sl-1260-wk674-s6` @`c55410d6`) edits `test_api_authorisation_sweep.py`
  (`HANDLER_GUARDED`, `RESOURCE_BACKED`) and `api/score.py`; none of those are in this write set.
- **FD 8175's close vehicle** (the `RESOURCE_BACKED` guard, a WK-1178 test-only delta row) edits
  `test_api_authorisation_sweep.py`; not in this write set. This slice's guard is a separate
  file for that reason.
- **RL 8176's docs batch** amends `06` FR-343 (`:79`); this slice amends FR-345 (`:81`) after
  that batch merges.

## Out of scope — a pointer

The FR-345 spec question (the maintainer's 17:27:15 entry: `DATASET_*` route gates with no
handler scoped check, `api/blobs.py`:50–52, `api/dataset_versions.py`:60–62,
`api/reference_tables.py`:50) is a decision-maker's RL draft in parallel. This slice does not
wait for it. If it rules "honoured", those routes join or follow this slice by a further delta.

## Self-review before freeze

- Every route, line and code above re-read at `71e481fa` by this planner, not taken from the
  relay; exec-8177's `rbac.py`:209–212 cite is `_covers` at `:205`–`:216`.
- The three maintainer conditions map to Task 2 (red for all three, `SCOPE_DENIED` control),
  Task 5 (guard, injected red) and Task 4's ordering (SL-1736).
- Blocking DPs 0–3 are open, so `status: draft`. On the maintainer's ruling the plan is minted
  with resolver ids in the table and set `active`.
