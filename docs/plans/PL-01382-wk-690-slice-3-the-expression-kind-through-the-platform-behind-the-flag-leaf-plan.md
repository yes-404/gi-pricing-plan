---
id: PL-1382
family: plan
kind: leaf
title: WK-690 Slice 3 — the `expression` kind through the platform, behind the flag, with `custom_objective:author`: leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-03
owner: planner
tree: 9b0fb97c9ed1cea743639897351191bc1a862041
phase: P2
work: WK-690
slice: SL-1273
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1268, PL-1295, PL-1327, PL-1348, PL-1279, RL-1265, RL-1305, RL-1263, FD-1349, FD-1336]
---

# WK-690 Slice 3 — the `expression` kind through the platform, behind the flag, with `custom_objective:author`: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `test-driven-development` (every red-first step), `python-package` and `python-test` (every code task), `contract-schema` and `contract-guard` (Tasks 1 and 9), `fastapi-service` (Tasks 3 to 7), `postgres-pro` may be delegated for Task 2's migration review, `spec-change` (every task that edits `02` or `06`), `dev-commands` (the gate, the gate slot and the NFR-480 measurement) and `git-hygiene`, and reads [`README.md`](README.md)'s five unchecked conventions before its first step. The executor is spawned from `.claude/roles/executor.md`, whose Model / effort line it quotes verbatim.

## Goal

Make the `expression` Custom Objective a real, governed artifact in the platform, behind
`features.expression_objectives_enabled`, with its default still off:
- `model-schema`'s `CustomObjective` carries the `expression` arm (`bound_symbols`,
  `parameters`, `loss`, `derived`), and the database stores it;
- `POST /custom-objectives` accepts `kind: expression`, and `POST /custom-objectives/{id}/derive`
  derives and stores the gradient and hessian, both **only while the workspace's flag is on**
  (FR-150, `RL-1265` DP-3 (a));
- `custom_objective:author` lands with its `06` §4.1 row and its checks in one commit (FR-367,
  `RL-1305` "What it obliges");
- certification of an `expression` objective runs as the existing 202 job, and fitting with an
  approved one compiles it (FR-144, FR-146);
- submission refuses an uncertified objective by its own code, and a `convexity: violated`
  certificate needs an extra Approver (FR-146, FR-152, FR-163);
- the four declared objective codes are registered, derivation is audited (NFR-484), and
  NFR-480 is measured.

**Architecture.** Slice 2 delivered `pricing-core`'s middle layer (`derive`, `compile_kernel`,
`compile_expression_objective`, `certify_expression_objective`), reachable from no route. This
slice is the backend and contract layer on top of it. `pricing-core` changes in one place only:
`compile_objective` dispatches an `expression` objective to Slice 2's compiler (DP-S3-1). The
backend stamps `derived_at`, which `pricing-core` may not (ADR-703; `PL-1327` Global
Constraints). The flag check stays in `backend/src/app/platform/objectives.py`'s
`refuse_expression_kind`, which becomes conditional on the resolved setting.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2 (`model-schema`), SQLAlchemy 2 async and
Alembic (one new revision), PostgreSQL 16, SymPy 1.14.0 through Slice 2's API (no direct
import in `backend`), pytest. No new dependency: no `uv.lock` or `pyproject.toml` change.

**Spec:**
- [`../specs/02-modelling.md`](../specs/02-modelling.md) §3.7: **FR-144** (`02:208`), **FR-146**
  (`:210`), **FR-150** (`:214`), **FR-152** (`:216`), **FR-163** (`:227`); §3.10 **FR-207**
  (`:370`); §4.6's `expression` example (`:1026-1068`); §5.1 (`:1833-1840`, the code list
  `:2100-2106` and its note `:2134-2142`); §9 **NFR-480** (`:2916`), **NFR-484** (`:2920`).
- [`../specs/06-governance.md`](../specs/06-governance.md) §3.3 **FR-366** (`06:147`), **FR-367**
  (`06:148`); §4.1's Built table (`06:269-292`) and its Specified table (`06:330-335`).
- [`../specs/07-platform.md`](../specs/07-platform.md) §3.8 **FR-448** (`07:174`) and **FR-449**
  (`07:175`). This slice **cites** `07` and does not edit it (`PL-1268` Status).
- [`../workflows/WF-00702-custom-objective-lifecycle.md`](../workflows/WF-00702-custom-objective-lifecycle.md)
  Route B rows B1.5, B2.1 to B2.6 and B4 (the two Approvers), as reachable over HTTP here; the
  end-to-end Route B file is Slice 5's (`PL-1268` Acceptance 7).
Line numbers are at the tree above.

**What this plan implements.** `PL-1268` Slice 3 (`PL-1268:478-515`) and its row `SL-1273`
(`docs/roadmap.md:943-960`). The rulings it executes: `RL-1265` DP-3 (a) and its Slice 3
obligations (`RL-1265:131-137`), including the violation it names for Slice 3: *"`expression_objectives_enabled` resolves on in a workspace whose setting is unset"*
(`RL-1265:160-161`); and `RL-1305`'s WK-690 Slice 3 obligation: *"moves `custom_objective:author`
from Specified to Built in the commit that adds the member and its `requires()` site"*.

## Status

Filed 2026-10-01 against the tree above, under **working id 9789**, allocated by the lead (the
only allocator, `FD-1338`). The id is minted at this PR's mint turn.
*(Minted 2026-10-03 at `origin/main` `d672f991` as `PL-1382`, filed under working id 9789. Its slice row is `SL-1273`, which already exists. The record is otherwise as filed.)*

**`draft`.** It turns `active` only when every activation need below is met, each shown by its
command at a named `origin/main` SHA in the dispatch record. This paragraph does not change
when they are met.

### Activation needs — each checked by a command, in this order

Each need is a command. The dispatch record pastes the command, its output and the
`origin/main` SHA it ran at. **A need with no pasted output is unmet** (the rule `PL-1348`
set after `PL-1342:70-81`). Run from any checkout after `git fetch -q origin`;
`M=$(git rev-parse origin/main)` is the SHA recorded.

1. **Slice 2 is closed on `main`** (`PL-1268` Slice 3, "Depends on: Slice 2"):
   ```bash
   git show "$M":docs/roadmap.md | grep -A6 '^#### SL-1272 ' | grep -m1 '^status:'
   ```
   Expected: a line beginning `status: closed`. **Met at the tree above.**
2. **The rulings this slice builds from are on `main`:**
   ```bash
   git ls-tree --name-only "$M" docs/rulings/ docs/findings/ | grep -c -E '/(RL-01265|RL-01305|RL-01263|FD-01349)-'
   ```
   Expected: `4`. **Met at the tree above.**
3. **WK-1178's permission-parity check has merged** (`SL-1273`'s Gate, `docs/roadmap.md:959`:
   *"WK-1178's permission-parity check, both merged before the commit that adds
   `custom_objective:author`"*; `RL-1305` D2: a pytest module under root `tests/`):
   ```bash
   git grep -l -E 'STALE_OWNER' "$M" -- tests/
   ```
   Expected: at least one path (the module `PL-1279` builds; its `STALE_OWNER` class is
   `RL-1305` D1 item 4). **No output is unmet. Unmet at the tree above:** the command prints
   nothing, `PL-1279` is `status: draft`, and no `SL-` row in `docs/roadmap.md` cuts it
   (`grep -n -i parity docs/roadmap.md` hits only `SL-1273`'s own row). This is the slice's
   critical-path blocker; the lead sequences it.
4. **This plan is minted on `main`:**
   ```bash
   git grep -l -E '^slice: SL-1273$' "$M" -- docs/plans/
   ```
   Expected: exactly one path, and `basename <that path> | cut -c4-8` prints a number below
   `09000`. A path printing `09789` is this working-id draft: **unmet**.
5. **Every blocking decision point has its ruling minted on `main`.** DP-S3-1 to DP-S3-5 are
   the decision-maker's, one `RL-` each (or one `RL-` ruling several). The dispatch record
   names each minted id and runs, with those ids substituted:
   ```bash
   git ls-tree --name-only "$M" docs/rulings/ | grep -c -E '/(RL-0AAAA|RL-0BBBB)-'
   ```
   Expected: the number of distinct ruling ids named. A ruling file whose id is `09xxx` is a
   working-id draft: **unmet**. Where a minted ruling and a task here differ, **the ruling
   wins**, and the dispatch record names each difference.
6. **DP-S3-6 (FD-1349's follow-up) has the lead's verdict, and the status flip has merged.**
   The lead's verdict on DP-S3-6 is a dated line in the dispatch record. The flip (this plan and
   `SL-1273` to `active`) is its own PR, after needs 1 to 5 are pasted:
   ```bash
   P=$(git grep -l -E '^slice: SL-1273$' "$M" -- docs/plans/ | sed 's/^[^:]*://'); git show "$M":"$P" | grep -m1 '^status:'
   git show "$M":docs/roadmap.md | grep -A6 '^#### SL-1273 ' | grep -m1 '^status:'
   ```
   Expected: both lines begin `status: active`. Then the lead's go, dated, in the dispatch
   record, with the GO-check line ("every activation need of the plan is quoted and shown met,
   and the plan and slice read `active` on main") and the DP-resolver line.

**Not an activation need:** `RL-1265`'s other slices, WK-674, and the ladder. No WK-674 output is
an input here (`PL-1268` Status), and this slice reads no rung value (File contention below).

### Build-start conditions (Task 0, after activation; not activation needs)

- **A free lane under `RL-1263`** (at most two build slices, from different Works). This plan is
  written for lane B, beside lane A's `SL-1345` (`PL-1348`).
- **The file-contention check below is re-run on both slices' actual diffs** and pasted in the
  dispatch record.
- **Task 10 (NFR-480) runs alone** (`RL-1263` item 3): the other gate slot is empty for its
  window, and lane A's `bench-rating.py` run never shares it.

## Acceptance Standard

A fresh reviewer checks each item by the command given, on the slice's final tree. Named single
test files and node ids are exempt from the slot; every suite-level run is slotted (item 13).

1. **The contract carries the `expression` arm, and only that shape** (FR-144; `CLAUDE.md` §2).
   `uv run pytest packages/model-schema/tests/test_objectives.py -q -k expression` passes: §4.6's
   example (`02:1029-1052`) validates as a `CustomObjective`; a template with a `loss`, an
   expression with a `template`, an expression with a `derived` but no `loss`, and an expression
   whose `loss` exceeds 2000 characters are each refused, each test asserting the validator's
   message, not only the exception type. `uv run python scripts/generate-contracts.py --check`
   passes, and `backend/tests/test_contracts.py`'s `DECLARED_AND_UNBUILT["custom-objective"]`
   no longer lists `bound_symbols`, `parameters`, `loss` or `derived`.
2. **The database stores an expression and keeps it immutable**
   (`uv run pytest backend/tests/test_custom_objectives_expression.py -q -k storage`): an
   expression row inserts; a template row without `template` is still refused by the
   replacement CHECK; an `UPDATE` of `loss` is refused by the definition trigger; `derived` is
   written once from NULL while `draft` and a second write is refused. Each refusal names its
   constraint or trigger. `alembic heads` prints exactly one head.
3. **`custom_objective:author` exists, is checked, and is in no built-in role** (FR-367;
   `PL-1268` Acceptance 8). `git grep -n 'custom_objective:author' -- packages/model-schema/src`
   returns the enum member; `06` §4.1's Built table has its row and its Specified table does
   not; WK-1178's parity module passes on the final tree and **was seen red** with the member
   added and the `06` row not yet moved (the ledger quotes it). A caller with `model:fit` and
   without the new permission gets 403 on create (`kind: expression`) and on derive; a caller
   with it and with the flag on succeeds; a test asserts the permission is absent from every
   set in `BUILTIN_ROLES`. Template create stays `model:fit` alone, and submit stays
   `model:submit`.
4. **The flag gates, and its default is off** (FR-150, FR-449, `RL-1265` DP-3 (a) and its named
   violation). `-k flag` passes: in a workspace whose setting is **unset**, create and derive
   answer 409 `OBJECTIVE_KIND_NOT_ENABLED`; with it set `true`, both succeed; with it set
   `false`, 409. The unset case is the red-first test: at the base it passes for the wrong
   reason (the refusal is unconditional), so its red is the **set-true** case, quoted failing
   before Task 4 and passing after. `SettingDefinition`'s default for the key is still `False`
   (`git diff <base> -- backend/src/app/platform/settings.py` is empty).
5. **Derive stores what Slice 2 derives, stamped and audited** (FR-144, NFR-484, WF-702 B2.3).
   `-k derive` passes on §4.6's example: the stored `derived.gradient` and `hessian` equal
   `pricing_core.modelling.expression_objective.derive(...)`'s text exactly; `derivation_version`
   equals `sympy.__version__` (with it patched to `"9.9.9"`, the stored value is `"9.9.9"`,
   `RL-1289`'s rule carried to storage); `derived_at` is set by the backend; one
   `custom_objective.derived` Audit Event carries before (`derived: null`) and after state.
6. **A grammar error is refused by its code, with its position** (FR-145, WF-702 B1.5).
   `-k grammar` passes: `numpy.where(...)` as a `loss` answers `OBJECTIVE_GRAMMAR_VIOLATION`
   with the status and position fields DP-S3-3 rules, the position matching
   `ExpressionError.lineno` and `col_offset`.
7. **Certification of an expression runs as the existing job** (FR-146, FR-151). `-k certify`
   passes: `POST /custom-objectives/{id}/certify` on a derived expression returns 202 and the
   job records a certificate whose battery is `OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC`, `overall`
   `certified_with_findings`, `convexity` `violated`, and `library_versions.sympy` present.
   Certify on an expression that has not been derived is refused as DP-S3-3 rules. A template
   certify is unchanged (its existing tests pass untouched).
8. **Fitting with an approved expression objective compiles it** (FR-144 "compiled at fit
   time"; DP-S3-1). `uv run pytest packages/pricing-core/tests/test_objectives.py -q -k
   compile_dispatch` and the backend fit test named in Task 6 pass: a GBM fit whose
   `spec.objective` names an approved expression objective completes; a gradient that
   overflows surfaces as the job error `OBJECTIVE_NONFINITE_DERIVATIVE`, and a slowed callable as
   `OBJECTIVE_ROUND_BUDGET_EXCEEDED`, each a registered code.
9. **Submission is governed** (FR-146, FR-152, FR-163; DP-S3-3, DP-S3-4). `-k submit` passes: an
   uncertified objective is refused with `OBJECTIVE_NOT_CERTIFIED` (for the kinds DP-S3-3
   rules); a `convexity: violated` objective's approval request carries the approver count
   DP-S3-4 rules, and one non-author approval leaves it in `review`; the second approves it.
10. **The four codes are registered and undeclared in one commit each** (`PL-1268` premise 8).
    `grep -n -E 'OBJECTIVE_(GRAMMAR_VIOLATION|NOT_CERTIFIED|NONFINITE_DERIVATIVE|ROUND_BUDGET_EXCEEDED)' backend/src/app/errors.py`
    prints four lines inside `MODELLING_ERROR_CODES`; `grep -c 'declared, Phase 2' docs/specs/02-modelling.md`
    is four lower than at the base; `python3 scripts/audit-docs.py` check 10 passes.
11. **FR-207 is settled as DP-S3-5 rules**, with `02` FR-207's row amended, dated, and
    `DECLARED_AND_UNBUILT`'s `model` and `model-spec` entries matching it.
12. **NFR-480 is measured, not asserted.** The ledger holds N ≥ 3 runs of the certify job on
    §4.6's example at `default_sampling`'s shape, each with its wall time and one-minute load
    average at start and end, the median and the spread against 180 s, run in a solo window
    (`RL-1263` item 3).
13. **The gate, in a gate slot, with every evidence field** (the form of `PL-1348` Acceptance
    10). For every suite-level run and the full gate, the ledger records: a clean checkout of
    the named SHA with `git status --porcelain` empty; `uv run ruff check --no-cache .` and
    `uv run mypy --no-incremental`; **the dev-commands slot wrapper verbatim**
    (`.claude/skills/dev-commands/SKILL.md:122-171`) with `LOKY_MAX_CPU_COUNT=4
    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2`, in the foreground with a `timeout`; `uptime`
    **and** `free -h` at start and end; the other slot's holder named as gate or not-gate, read
    with `flock -n` on `/tmp/slots/gate-1` and `/tmp/slots/gate-2`; wall and pytest time against
    main's own slotted run recorded at Task 0. The full two-half gate (`CLAUDE.md` §11) exits 0,
    with every rc, the `N passed` line and `HEAD` quoted against main's. After merging a `main`
    that adds a migration, `alembic upgrade head` runs on the per-worktree test database first.
    Docs checks run on a clean detached checkout.
14. **Every refusal was seen red first.** The ledger quotes each test failing before its
    implementation, by its cause (the README's convention 2), or a mutation control on the
    finished code where the intermediate red cannot be staged, each control named by the code it
    disables.
15. **`pricing-core` stays standalone and pandas-free.** `uv run lint-imports` passes;
    `git diff <base> -- packages backend | grep -E '^\+.*import pandas'` prints nothing.

## Global Constraints

- **The flag's default stays `False`** (`07` FR-449; `RL-1265` DP-3 (a)). Nothing in this slice
  switches it on in any workspace, fixture aside; tests set it per workspace.
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2). The `expression`
  arm is declared once, in `model_schema/objectives.py`, and the hand-authored
  `docs/contracts/schemas/custom-objective.schema.json` (which already declares it, `:47-80`) is
  held to it by the guard.
- **Model and objective definitions are declarative JSON, never pickles** (`CLAUDE.md` §2): the
  derived text is stored as text (§4.6), never a SymPy object or compiled function.
- **No string reaches `eval`, `exec`, `compile`, `sympy.sympify` or `sympy.lambdify`** (NFR-483).
  The backend calls Slice 2's API only; it does not import `sympy`.
- **`pricing-core` reads no clock and gains no FastAPI, SQLAlchemy or Redis import** (ADR-703;
  `CLAUDE.md` §2). `derived_at` is the backend's.
- **One commit for a new permission**: its `06` §4.1 row, its enum member and its check (FR-367;
  `RL-1305`). **One commit per code**: its `errors.py` registration and its `02` §5.1 marker
  removal (`PL-1268` premise 8).
- **Frozen records are not edited**: nothing already on `main` in `docs/plans/`, `docs/rulings/`
  or `docs/findings/` (`document-ids.md` §1.5).
- **No build ahead of the phase** (`CLAUDE.md` §9): no authoring view (Slice 5), no
  `expression` Factor (Slice 4), no frontend source change; the generated client is regenerated
  and type-checked only.
- No pandas in new code (`CLAUDE.md` §3). Requirement ids are permanent; spec edits go through
  `spec-change`, dated, in the same commit as their code.

## Scope

### Requirement coverage, each id individually

| Spec section | Id | What this slice owes | Task |
|---|---|---|---|
| `02` §3.7 | FR-144 | Stored derived expressions (the storage clause Slice 2 left); compiled at fit time | 1, 2, 4, 6 |
| `02` §3.7 | FR-146 | Certificate persisted for the `expression` kind; required for submission | 5, 7 |
| `02` §3.7 | FR-150 | The kind gated by the flag: refused only while it is off | 4 |
| `02` §3.7 | FR-152 | `convexity: violated` requires a declared strategy and an additional Approver | 7 |
| `02` §3.7 | FR-163 | Non-author Approver; two Approvers for a violated expression | 7 |
| `02` §3.10 | FR-207 | The two `custom_objective_ref` residuals made live or re-noted | 8 |
| `06` §3.3 | FR-366 | Discharged when FR-367 lands (its first half, `model:fit` for templates, stays) | 3 |
| `06` §3.3 | FR-367 | `custom_objective:author`: enum member, `06` row and check, in no built-in role | 3 |
| `07` §3.8 | FR-448 | The workspace setting is read per workspace (no change to its declaration) | 4 |
| `07` §3.8 | FR-449 | The default stays the safe value, `False` | 4 |
| `02` §9 | NFR-480 | Certification < 3 min, measured | 10 |
| `02` §9 | NFR-484 | An Audit Event for derivation with before and after state | 4 |

**Carried obligations placed here:** `RL-1265`'s Slice 3 list (`RL-1265:131-137`); `RL-1305`'s
WK-690 Slice 3 line; `PL-1268` premise 8's three codes, plus `OBJECTIVE_ROUND_BUDGET_EXCEEDED`
(`PL-1327` Hand-off: "the budget and non-finite errors, which it registers in
`backend/src/app/errors.py`"); `PL-1268` premise 10 (the `/derive` docstring's pre-migration
ids corrected); the `derived_at` stamp `PL-1327` Global Constraints sent here; and, **if the
lead adopts DP-S3-6**, `FD-1349`'s guard comparison.

**Not in this slice:** FR-95 and FR-208's expression arm (Slice 4); `02` §5.3's authoring view
and WF-702 Route B end to end (Slice 5); FR-85, FR-86's field, FR-210 and FR-154's expression
half (Phase 3, `RL-1265`).

### Premises re-derived at `9b0fb97c`

A subagent swept the backend, `model-schema` and `pricing-core` paths; the planner read the
rulings, the roadmap rows and the spec rows directly.

| # | Premise | Evidence | Consequence |
|---|---|---|---|
| a | The refusal is unconditional | `backend/src/app/platform/objectives.py:255-295` (`refuse_expression_kind`): resolves the flag at `:273-276` and raises 409 `OBJECTIVE_KIND_NOT_ENABLED` either way; callers `api/custom_objectives.py:249-252` (create) and `:309-312` (derive) | Task 4 makes it conditional |
| b | Routes and their checks | `api/custom_objectives.py`: create `:229` and derive `:291`, both `FitModels` (`:75-77`); certify `:315`; submit `:381` (`SubmitModels`); `requires()` at `backend/src/app/api/authz.py:54` | Task 3 |
| c | The flag | `backend/src/app/platform/settings.py:244-254`, `default=False`, `feature_flag=True`; `SAFE_DEFAULT` `:272-275`; accessor `resolve(...)` `:292`, read as `.effective_value` | No change to settings |
| d | No `custom_objective:author` | `packages/model-schema/src/model_schema/permissions.py:28` (`Permission`, no such member), `BUILTIN_ROLES` `:131-150`; `06:333-335` lists it under Specified, owner WK-690 | Task 3 |
| e | No parity check exists | swept `scripts/`, `tests/`, `backend/tests`, `packages/*/tests`, `.github/`; `06:262-264` asserts one exists | Activation need 3 |
| f | `CustomObjective` is template-only | `model_schema/objectives.py:439-565`; `_only_templates_are_built` `:481-501`; the validators at `:503`, `:532` assume a template | Task 1 |
| g | The contract already declares the arm | `docs/contracts/schemas/custom-objective.schema.json:10` (kind enum) and `:47-80` (`bound_symbols`, `parameters`, `loss` maxLength 2000, `derived` with `derived_at`); `backend/tests/test_contracts.py:560` `DECLARED_AND_UNBUILT` lists the four fields | Task 1 shrinks the exemption; the hand-authored file is read, and edited only if the guard finds a disagreement |
| h | Slice 2's API | `packages/pricing-core/src/pricing_core/modelling/expression_objective.py`: `Derived` `:91` (no `derived_at`), `derive` `:100`, `compile_expression_objective` `:292`, `certify_expression_objective` `:423`; not re-exported, no caller in `src` | Tasks 4 to 6 import by module path |
| i | Grammar errors carry a position and no code | `pricing_core/data/expressions.py:88` (`ExpressionError`, `lineno`, `col_offset`) | Task 4 maps it (DP-S3-3) |
| j | Slice 2's errors are coded | `pricing_core/modelling/errors.py:65` (`_CodedObjectiveError`), `:77` `NonFiniteDerivativeError`, `:107` `RoundBudgetExceededError` | Task 6 registers their codes |
| k | Three of four codes unregistered | `backend/src/app/errors.py:114` (`MODELLING_ERROR_CODES`) holds only `OBJECTIVE_KIND_NOT_ENABLED` (`:190`) of the five; `02:2102`, `:2104-2106` carry "(declared, Phase 2)"; an unknown code raises `ValueError` | Tasks 4, 6, 7 |
| l | The certify job is template-only | `JobKind.OBJECTIVE_CERTIFY` (`model_schema/jobs.py:51`); `_certify` `backend/src/app/worker/model_handlers.py:1528`, calling `certify_objective` at `:1557`; `default_sampling` `platform/objectives.py:464`; `record_certificate` `:498`; `ObjectiveCertificateRow.payload` is JSONB | Task 5 |
| m | No two-approver rule | `backend/src/app/platform/approvals.py:225` (`submit`) takes `approvers_required` from the policy only (`:286`) | Task 7 (DP-S3-4) |
| n | Submission's stand-in | `submit_for_review` `platform/objectives.py:556`: `VALIDATION_FAILED` 409 at `:577-586`, then `_require_evidence` `:830-859` (`EVIDENCE_INCOMPLETE` 422) | Task 7 (DP-S3-3) |
| o | No derivation audit event | events at `platform/objectives.py:243`, `:541`, `:609`, `:683`; none for derivation | Task 4 |
| p | FR-207's residuals are both absent in code | `GlmSpec` `model_schema/modelling.py:1030`, `Model` `:2043`, neither has `custom_objective_ref`; `DECLARED_AND_UNBUILT` lists it for `model` and `model-spec` | Task 8 (DP-S3-5) |
| q | The DB refuses expression rows | `CustomObjectiveRow` `backend/src/app/db/models.py:1682-1765`; CHECK `custom_objective_is_a_template_in_phase_1` `:1760-1763`; the definition trigger lists its columns in `backend/migrations/versions/d0e1f2a3b4c5_custom_objectives.py:41-50`; head `2f598e89d12c_sub_graph_versions.py` | Task 2: a migration |
| r | Tests that flip | `backend/tests/test_custom_objectives.py:178`, `:647`, `:617` (403; stays or moves per DP-S3-2), `:429`; `backend/tests/test_custom_objectives_api.py:583`; `packages/model-schema/tests/test_objectives.py:101` | Each is rewritten in the task that flips it, quoted before and after |
| s | Marker counts | `git grep -h -E 'req\("(FR-144\|FR-146\|...)"\)' -- ':(glob)packages/*/tests/**' ':(glob)backend/tests/**'` piped to `grep -o \| sort \| uniq -c` (matching lines, as `git grep -c` counts): FR-144 15, FR-146 23, FR-150 5, FR-152 7, FR-163 6, FR-207 4, FR-366 0, FR-367 0, FR-448 3, FR-449 4, NFR-480 0, NFR-484 3 | Task 0 re-counts; FR-366, FR-367 and NFR-480 must be non-zero at the end |
| t | No ladder reader | `LadderRung`, `reconcile_ladder`, `ladder`, `rung` (case-insensitive): zero hits in `api/custom_objectives.py`, `platform/objectives.py`, `worker/model_handlers.py` and `pricing_core/modelling/` | The `FD-1336` hold does not apply |
| u | No frontend reader of the arm | `frontend/src` has no reader of `CustomObjective.kind` or the expression fields (`ObjectivePicker.vue:97` reads the GBM ref's `kind`, a different field) | Generated client regenerated and type-checked only |

The executor re-reads each at its own base and stops on any that no longer holds.

### Decision points

The kinds follow `document-ids.md` §1.7. DP-S3-1 to DP-S3-5 are the decision-maker's, each
blocking activation (need 5). DP-S3-6 is the lead's (need 6). DP-3 of `PL-1268` is resolved
(`RL-1265`) and is not re-opened.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S3-1 | Does this slice make fitting with an approved `expression` objective work, or stop at `approved`? (FR-144 "compiled at fit time"; `PL-1268` Slice 3 registers `OBJECTIVE_NONFINITE_DERIVATIVE` "where the fit job surfaces it", but its scope bullets name no fit change) | **(a)** Yes: `pricing_core.modelling.objectives.compile_objective` dispatches `kind: expression` to `compile_expression_objective`, reading the artifact's `loss`, `parameters` defaults, `derived`, `y_domain`, `hessian_strategy` and `hessian_min`; the GBM fit path is otherwise unchanged. **(b)** No: fitting is a later slice, and `compile_objective` keeps refusing. **(c)** As (a), with the GLM arm too. | **(a).** No later WK-690 slice fits a model (Slices 4 and 5 are factors and the view), so under (b) FR-144's fit-time clause has no owner in the Work. The GBM path already takes any `ObjectiveFns` (`PL-1327` Architecture, "one compiled type"). (c) is FR-207's question (DP-S3-5). | decision point | yes, for activation; applied at Task 6 | decision-maker, its own `RL-` (pending) |
| DP-S3-2 | How is `custom_objective:author` checked on create, where the kind is in the body? (FR-367: authoring, editing or versioning needs it; template selection stays `model:fit`) | **(a)** Create keeps its `model:fit` route dependency and, for `kind: expression`, the handler calls `rbac.require_permission(..., permission=Permission.CUSTOM_OBJECTIVE_AUTHOR)` before the flag check; derive's route dependency becomes `requires(Permission.CUSTOM_OBJECTIVE_AUTHOR)` alone. **(b)** As (a), but derive keeps `model:fit` as well as author. **(c)** A separate `POST /custom-objectives/expression` route with an author dependency. | **(a).** An expression author creates with both, as `PL-1268` Acceptance 8 tests ("a caller with `model:fit` and without the new permission gets 403"); derive is an authoring act on an expression only, so its one dependency is the author permission, which gives `RL-1305`'s route leg a `requires()` site. `RL-1305` counts a service-layer `require_permission(..., permission=…)` as checked. "Editing or versioning" is a create with an existing slug (`02:2266`, "it allocates a version"), so no new route is needed. (c) adds a route `02` §5.1 does not declare. Checks run before the flag, so a caller without the permission gets 403 whatever the flag. | decision point | yes, for activation; applied at Task 3 | decision-maker, its own `RL-` (pending) |
| DP-S3-3 | What statuses and fields do the new refusals carry, and does the template submit path move? | **(a)** `OBJECTIVE_GRAMMAR_VIOLATION` 422 with a `position: {line, column}` problem extension from `ExpressionError`; certify of an underived expression 409 `OBJECTIVE_NOT_CERTIFIED` naming `/derive`; submission without a certificate 409 `OBJECTIVE_NOT_CERTIFIED` **for both kinds**, replacing the `VALIDATION_FAILED` stand-in (`02:2140-2142`), status unchanged. **(b)** As (a), but templates keep `VALIDATION_FAILED`. **(c)** As (a), with certify of an underived expression deriving first. | **(a).** The stand-in note says the code is unbuilt for both, and one code for one condition is what §5.1 declares; the status does not change, so only the code a client reads moves, which the release note states. (b) leaves two codes for one refusal. (c) hides an authoring step the Approver must see (WF-702 B2.4). **`PL-1268` premise 8 requires a DP if the template response changes: this is it.** | decision point | yes, for activation; applied at Tasks 4, 5 and 7 | decision-maker, its own `RL-` (pending) |
| DP-S3-4 | How many Approvers does a `convexity: violated` objective need, and for which kinds? (FR-152: "an additional Approver"; FR-163: "`expression` objectives with `convexity: violated` need two Approvers (FR-152)") | **(a)** `approvers_required = policy + 1`, for any objective whose current certificate has `convexity: violated`, passed as a new keyword to `approvals.submit`. **(b)** `max(policy, 2)`, both kinds. **(c)** As (a) or (b), `expression` only. | **(a), both kinds.** At the default policy (1) it gives FR-163's two; with a stricter policy it still adds one, which is FR-152's word "additional". FR-152 is kind-agnostic, and FR-163 cites it. Applying it to templates may change an existing template's approval count where a template certifies `violated`; Task 7 counts such fixtures at the base and the release note states it. | decision point | yes, for activation; applied at Task 7 | decision-maker, its own `RL-` (pending) |
| DP-S3-5 | FR-207's two `custom_objective_ref` residuals (`GlmSpec`, absent; `Model`, declared and unbuilt): live or re-noted? (`PL-1268` Slice 3: "raises a decision point if the GLM arm's custom objective turns out to be a separate capability") | **(a)** Re-note both, dated: a GBM names its objective through `spec.objective` (`model.schema.json`, as FR-207's 2026-08-25 amendment quotes), the GLM arm's custom loss is a separate capability (`glum` fits a fixed family list), so both residuals move to Phase 3, spec change first, deferred with an owner (the maintainer; event: the P2 phase closure record). **(b)** Make `Model.custom_objective_ref` live as a record of the GBM's `spec.objective.ref`, and re-note `GlmSpec`'s. **(c)** Build both, with a GLM custom-loss path. | **(a).** FR-207's amendment says the `Model` field "records what the `GlmSpec` field declares", so (b) records a declaration that does not exist, and a second copy of `spec.objective.ref` is a second source of truth. (c) is a new capability `02` does not specify. (a) is the map plan's own condition for a DP, met. | decision point | yes, for activation; applied at Task 8 | decision-maker, its own `RL-` (pending) |
| DP-S3-6 | Does `FD-1349`'s follow-up (a contract-guard comparison of the certificate check-name enum, owed before WK-690 closes) land in this slice? | **(a)** Yes, as Task 9: one appended comparison in `backend/tests/test_contracts.py` reading `OBJECTIVE_CERTIFICATE_CHECKS` and `OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC` against the authored enum, with its meta-guard, proved red on `FD-1349` Evidence 1's broken input. **(b)** A separate WK-690 slice after this one, cut by the planner on the lead's word. **(c)** Into Slice 5. | **(a).** This slice already edits `test_contracts.py` (Task 1's `DECLARED_AND_UNBUILT` change) and makes the symbolic battery reachable from a route (Task 5), so the published vocabulary first meets real certificates here. The task is small and independent, adds no spec change, and saves a slice and a gate. (b) costs a full slice cycle for one test; (c) puts a contract guard in a frontend slice. **Recommended, not decided:** scope moved into a slice is the lead's call (`delivery-process.md` §3). If declined, Task 9 is dropped and nothing else changes. | scope | yes, for activation (need 6) | lead, dated line in the dispatch record |

---

## Write set

Measured at `9b0fb97c`. "Existing definitions edited" is what `RL-1263` option (c) compares.

| Path | This slice | Existing definitions edited | Task |
|---|---|---|---|
| `packages/model-schema/src/model_schema/objectives.py` | `ObjectiveParameter`, `DerivedBlock` (new); `CustomObjective`'s four fields; `_only_templates_are_built` replaced by a kind-arm validator | `CustomObjective`, its validators at `:481`, `:503`, `:532` | 1 |
| `packages/model-schema/src/model_schema/__init__.py` | re-export of the two new names, **only if** the module's existing pattern re-exports objective shapes | `__all__` (conditional) | 1 |
| `packages/model-schema/src/model_schema/permissions.py` | `Permission.CUSTOM_OBJECTIVE_AUTHOR` appended | `Permission` | 3 |
| `docs/contracts/schemas/custom-objective.schema.json` (hand-authored) | read; edited only where the guard finds a disagreement | (conditional) | 1 |
| `docs/contracts/openapi/generated.json`, `docs/contracts/schemas/generated/`, `docs/INDEX.md` | regenerated | registry-exempt (`RL-1263`, as corrected 23:20:11) | 1, 11 |
| `backend/src/app/db/models.py` | `CustomObjectiveRow`: four columns; the CHECK replaced | `CustomObjectiveRow` (an existing class: **not** the registry exemption, which covers appended classes only) | 2 |
| `backend/migrations/versions/<new>_custom_objective_expression.py` | **new**: columns, CHECK, trigger | registry-exempt (a new revision) | 2 |
| `backend/src/app/api/custom_objectives.py` | `CreateCustomObjective`'s expression fields; create's author check; derive implemented; docstrings' ids | `CreateCustomObjective`, `create_custom_objective`, `derive_custom_objective`, the module docstring | 3, 4 |
| `backend/src/app/platform/objectives.py` | `refuse_expression_kind` conditional; `derive_objective` (new service); certify dispatch; `default_sampling` for expressions; `submit_for_review`'s code | `refuse_expression_kind`, `default_sampling`, `submit_for_review`, `create` service | 4, 5, 7 |
| `backend/src/app/worker/model_handlers.py` | `_certify` dispatches by kind; fit path surfaces Slice 2's coded errors | `_certify`; the GBM fit handler's error mapping | 5, 6 |
| `backend/src/app/platform/approvals.py` | `submit(..., min_approvers_extra=...)` per DP-S3-4 | `submit` | 7 |
| `backend/src/app/errors.py` | four codes appended to `MODELLING_ERROR_CODES` | `MODELLING_ERROR_CODES` | 4, 6, 7 |
| `packages/pricing-core/src/pricing_core/modelling/objectives.py` | `compile_objective` dispatch (DP-S3-1) | `compile_objective` | 6 |
| `docs/specs/02-modelling.md` | FR-150 dated amendment (liftable, `RL-1265`); §5.1 derive row and code markers; the stand-in note; FR-207 per DP-S3-5; FR-152 and FR-163 notes if DP-S3-4 needs one | those rows | 4 to 8 |
| `docs/specs/06-governance.md` | §4.1: `custom_objective:author` moved from Specified to Built; FR-366 discharge note | the two §4.1 tables | 3 |
| tests: `packages/model-schema/tests/test_objectives.py`; `backend/tests/test_custom_objectives.py`, `test_custom_objectives_api.py`, `test_custom_objectives_expression.py` (**new**), `test_rbac.py` (the no-built-in-role assertion, appended); `packages/pricing-core/tests/test_objectives.py` (appended); the approvals tests (appended); `backend/tests/test_contracts.py` (`DECLARED_AND_UNBUILT` edited; Task 9's function appended) | as named | the flipping tests of premise r; `DECLARED_AND_UNBUILT` | all |
| `scripts/bench-model.py` or a new `scripts/bench-objective-certify.py` | the NFR-480 harness, whichever the executor finds already times certification | (conditional) | 10 |
| the slice ledger (`LG-`, the executor's) | new | — | 0, 11 |

**Not written:** `backend/src/app/platform/settings.py`, `backend/src/app/main.py` (the router
is already registered, `main.py:142`), `docs/specs/07-platform.md`, `docs/open-questions.md`,
`packages/pricing-core/src/pricing_core/__init__.py`, `frontend/src/**`.

## File contention (`RL-1263` option (c)), against lane A's `SL-1345` (`PL-1348`)

`PL-1348`'s write set is its section "Write set, and its contention (`RL-1263`)"
(`PL-1348:525-588`). Compared path by path:

| Path | `PL-1348` | This slice | Registry-exempt? | Rule |
|---|---|---|---|---|
| `backend/src/app/errors.py` | appends `LADDER_CLAMP_UNPLACEABLE` to `RATING_ERROR_CODES` (`:297`) | appends four codes to `MODELLING_ERROR_CODES` (`:114`) | **No** | Shared path, **disjoint definitions**: no existing definition is edited by both. Allowed only if the dispatch record names the path and pastes both diffs' hunks showing different frozensets. Append-only on each side; **the second to merge** merges `main` in and re-runs its full gate |
| `backend/tests/test_contracts.py` | "only if the guard needs a comparison" (an appended function) | edits `DECLARED_AND_UNBUILT` (`:560`); appends Task 9's function (if DP-S3-6 (a)) | **No** | Shared only if `PL-1348` adds a comparison. Each appends its own function; `DECLARED_AND_UNBUILT` is edited by this slice only (the dispatch record checks `PL-1348`'s diff does not touch it; if it does, that row **serialises**). Second to merge re-gates |
| `packages/model-schema/src/model_schema/__init__.py` | not edited by the salvage; "if the executor adds an export, that row serialises" | edited only if the existing pattern re-exports objective shapes | **No** | If both add an export, `__all__` is one existing definition: **serialise** (later slice starts that edit after the first merges) |
| `docs/contracts/openapi/generated.json`, `docs/contracts/schemas/generated/` | regenerated | regenerated | **Yes** | Never hand-merged: the second to merge regenerates and re-gates |
| `docs/INDEX.md` | regenerated | regenerated | **Yes** | Same |
| `backend/migrations/versions/` | none | one new revision | Yes | No sharing now. If any slice adds a revision first, this slice re-points `down_revision` so there is exactly one head (`alembic heads`), and re-gates |
| `backend/src/app/db/models.py` | none | edits `CustomObjectiveRow` | (existing class: not exempt) | No sharing with `PL-1348` |
| `backend/src/app/main.py` | none | none | — | — |
| `docs/specs/` | `03` only | `02`, `06` only | — | Disjoint |
| `docs/open-questions.md` | OQ-1316 row | none | — | — |
| `packages/model-schema/src/model_schema/` other files | `money.py`, `scoring.py` | `objectives.py`, `permissions.py` | — | Disjoint |
| `packages/pricing-core/src/pricing_core/` | `money.py`, `__init__.py`, `rating/*` | `modelling/objectives.py` | — | Disjoint |
| `backend/src/app/api/`, `observability/` | `api/score.py`, `metrics.py` | `api/custom_objectives.py` | — | Disjoint |
| measurements | `bench-rating.py` run | NFR-480 run (Task 10) | — | **Never in one window** (`RL-1263` item 3) |

**The ladder (`FD-1336` hold):** this slice **reads no rung value**. Premise t found no reader of
`LadderRung`, `reconcile_ladder` or any ladder field on its paths, and nothing in its scope
scores a quote. The hold on rung-reader slices (WK-673, WK-675; `FD-1336`, "the FD asks that
those slices read the corrected values") does not bind it.

**Verdict: concurrent with `SL-1345`, with three shared non-exempt paths, all append-only on
disjoint definitions** (`errors.py`, and `test_contracts.py` and `model_schema/__init__.py` only
conditionally). The dispatch record re-checks each on the actual diffs. Whichever merges
second merges `main`, regenerates the generated outputs and `INDEX.md`, and **re-runs its full
gate**; that executor re-gates.

**Beyond lane A (not concurrent now; each later dispatch re-checks):**
- **WK-674 Slice 2 (`SL-1256`, draft)** clears owner cells in `06` §4.1's Built table
  (`RL-1305` D1 item 4), the same policy table Task 3 adds a row to: **serialise** if they are
  ever in flight together.
- **WK-1178's parity slice (`PL-1279`)** must merge **before** this slice's Task 3 (need 3).
- **The WK-1178 slice of #977** (the ruling filed under working id 9907, PR #977, read at `1dfca5c7`, not minted): a
  `Permission` column on every module's §5.1 table. If it lands first, Task 4's `02` §5.1 derive
  row carries `custom_objective:author` in that column, and create's row the DP-S3-2 pair.
- **Slice 4 (`SL-1274`)** never runs beside this slice (two slices of one Work, `RL-1263`).

---

## Tasks

The tasks run in order. Each ends in one commit.

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch, from
  `origin/main`. `uv sync --all-packages`.
- [ ] Quote the dispatch record in the ledger: each activation need's command, output and SHA;
  the DP-S3-1 to DP-S3-5 rulings by minted id; the lead's DP-S3-6 line; the slot grant.
- [ ] Record `uptime`, `free -h`, and main's slotted pytest total and wall time (Acceptance 13).
- [ ] Re-derive premises a to u at the base, with the tree; re-run premise s's counts.
- [ ] `gh pr list --state open`; read anything touching `custom_objectives`, `objectives.py`,
  `permissions.py`, `06` §4.1, `02` §3.7, §5.1 or FR-207, `approvals.py`, `errors.py` or
  `test_contracts.py`. Name the SHA read.
- [ ] Re-run the file-contention table on lane A's current diff; paste it.
- [ ] Create the slice ledger (`LG-`).

### Task 1: The contract's `expression` arm

**Files:** `model_schema/objectives.py`; maybe `model_schema/__init__.py`;
`packages/model-schema/tests/test_objectives.py`; `backend/tests/test_contracts.py`
(`DECLARED_AND_UNBUILT`); regenerated `docs/contracts/` outputs.

- [ ] **Red.** Rewrite `test_an_expression_objective_cannot_be_constructed_in_phase_1`
  (`test_objectives.py:101`) into `test_the_spec_example_expression_objective_validates`, built
  from `02:1029-1052` (minus `derived_at`'s format check, which the field's type carries). Run:
  it fails **because `_only_templates_are_built` raises "Phase 1 ships templates only (FR-150)"**;
  a failure for another reason (a missing field name) is a plan defect to report. Add the four
  refusals of Acceptance 1, each red at the base for its own reason.
- [ ] **Green.** Add `ObjectiveParameter` (`name`, `type: Literal["float"]`, `default`, `min`,
  `max`, with `min <= default <= max`) and `DerivedBlock` (`gradient`, `hessian`,
  `derivation_tool: Literal["sympy"]`, `derivation_version`, `derived_at: AwareDatetime`), field
  names and constraints copied from `custom-objective.schema.json:47-80`, not from this text.
  `CustomObjective` gains `bound_symbols`, `parameters`, `loss`, `derived` (all `None` for a
  template). Replace `_only_templates_are_built` with one validator per arm; keep `:503` and
  `:532`'s template rules on the template arm. `derived` may be `None` on a `draft` expression.
- [ ] `uv run python scripts/generate-contracts.py`; remove the four fields from
  `DECLARED_AND_UNBUILT["custom-objective"]`; run `backend/tests/test_contracts.py`. If the
  guard reports a disagreement with the hand-authored file, read both and record which side is
  wrong before editing either (`CLAUDE.md` §0).
- [ ] Commit: `feat(model-schema): the expression arm of CustomObjective (WK-690 S3)`.

### Task 2: Storage

**Files:** `backend/src/app/db/models.py` (`CustomObjectiveRow`); a new revision under
`backend/migrations/versions/`; `backend/tests/test_custom_objectives_expression.py` (new).

- [ ] **Red.** `-k storage` tests of Acceptance 2, against the migrated test database. At the
  base the expression insert fails **naming `custom_objective_is_a_template_in_phase_1`**.
- [ ] **Green.** Columns `bound_symbols` (JSONB), `parameters` (JSONB), `loss` (Text), `derived`
  (JSONB), all nullable. Replace the CHECK with a kind-arm CHECK: `template` rows need `template`
  and no `loss`; `expression` rows need `loss` and no `template`. Extend the definition trigger
  (`d0e1f2a3b4c5_custom_objectives.py:41-50`) so `loss`, `parameters` and `bound_symbols` are
  immutable, and `derived` may change only from NULL, only while `status = 'draft'`. Downgrade
  restores the old CHECK and refuses if an expression row exists.
- [ ] `alembic heads`, run in the form and with the DSN `.claude/skills/dev-commands` gives, prints
  one head. Upgrade, downgrade, upgrade on the per-worktree test database.
- [ ] Commit: `feat(db): store the expression arm of a custom objective (WK-690 S3)`.

### Task 3: `custom_objective:author`, its `06` row and its checks, in one commit

**Files:** `permissions.py`; `06-governance.md` §4.1 and an FR-366 note; `api/custom_objectives.py`
(create's check, derive's dependency, per DP-S3-2); `backend/tests/test_custom_objectives.py`,
`test_rbac.py`.

- [ ] **Red (the parity check).** Add the member only. Run WK-1178's parity module: it fails
  naming `custom_objective:author` as an enum member with no Built row **and** a Specified name
  that is a member. Quote it. This proves the check sees this slice's change.
- [ ] **Red (the routes).** Tests: a caller with `model:fit` and without the new permission gets
  403 on `POST /custom-objectives` with `kind: expression` and on `/derive`; a test that no set
  in `BUILTIN_ROLES` contains it. The 403 tests fail at the base **because the caller reaches the
  409 refusal**, not because of a 403 for another permission (assert `["code"]`).
- [ ] **Green.** In one commit: move the row to the Built table (Governs: "Authoring, editing or
  versioning an `expression` Custom Objective (FR-367)"; Check owner empty), remove it from
  Specified, add the DP-S3-2 checks, and the FR-366 discharge note, dated. Re-run the parity
  module: green. Re-point `test_deriving_without_model_fit_is_refused` (`:617`) per DP-S3-2,
  quoted before and after. The refusal is still unconditional here: a caller with the
  permission still gets 409.
- [ ] Commit: `feat(governance): custom_objective:author with its 06 row and its checks (FR-367, WK-690 S3)`.

### Task 4: The flag made liftable; create and derive; `OBJECTIVE_GRAMMAR_VIOLATION`; the derivation event

**Files:** `platform/objectives.py`; `api/custom_objectives.py`; `errors.py`; `02` (FR-150 note,
§5.1 derive row, the code marker); `backend/tests/test_custom_objectives*.py`.

- [ ] **Red.** Acceptance 4, 5 and 6's tests. The set-true create and derive cases fail **with
  409 `OBJECTIVE_KIND_NOT_ENABLED`**; the grammar case fails with that same 409, not with a
  grammar code. Rewrite `test_an_expression_objective_is_refused_by_name_whether_the_flag_is_on_or_off`
  (`:178`) into the three flag cases, and `test_deriving_refuses_by_name...` (`:647`) and
  `test_creating_an_expression_objective_is_refused_by_name` (`test_custom_objectives_api.py:583`)
  into flag-off cases, each quoted before and after.
- [ ] **Green.** `refuse_expression_kind` raises only when the resolved `effective_value is not
  True` (an unset key resolves to `SettingDefinition.default`, `False`). Create (kind
  expression) parses `loss` with Slice 1's parser in the `objective` profile, mapping
  `ExpressionError` to `OBJECTIVE_GRAMMAR_VIOLATION` per DP-S3-3, and stores the row with
  `derived = NULL`. A new `derive_objective` service, behind `/derive`: refuses a non-`draft` or
  template objective (409 `VALIDATION_FAILED`, the module's existing transition code); calls
  `derive(loss, parameters=names)`; stores `DerivedBlock(..., derived_at=<transaction time>)`;
  emits `custom_objective.derived` with before and after state; returns the `CustomObjective`.
  Register `OBJECTIVE_GRAMMAR_VIOLATION` and remove its `02` §5.1 marker in this commit. Amend
  FR-150, dated: refused while the flag is off, accepted while on, default off (`RL-1265` DP-3).
  Correct the module and derive docstrings' pre-migration ids (`PL-1268` premise 10).
- [ ] Commit: `feat(modelling): expression objectives behind a liftable flag, with derive (FR-150, FR-144, WK-690 S3)`.

### Task 5: Certification of an expression

**Files:** `platform/objectives.py` (`default_sampling`, the certify guard); `worker/model_handlers.py`
(`_certify`); tests.

- [ ] **Red.** Acceptance 7's tests; the expression certify fails at the base **because `_certify`
  calls the template-only `certify_objective`**, which raises on `objective.template is None`.
- [ ] **Green.** `_certify` dispatches by kind to `certify_expression_objective`, passing the
  stored `loss`, parameter defaults, `derived` (as Slice 2's `Derived`, without `derived_at`),
  `y_domain`, strategy and `default_sampling(objective)`. Certify of an underived expression is
  refused per DP-S3-3, at the route, before a job is enqueued. `record_certificate` stores the
  symbolic battery unchanged (JSONB).
- [ ] Commit: `feat(modelling): certify an expression objective as a job (FR-146, WK-690 S3)`.

### Task 6: Fit-time compilation, and the fit job's coded errors (DP-S3-1)

**Files:** `pricing_core/modelling/objectives.py` (`compile_objective`); `worker/model_handlers.py`;
`errors.py`; `02` §5.1 markers; tests.

- [ ] **Red.** `-k compile_dispatch` in `packages/pricing-core/tests/test_objectives.py`: an
  approved expression objective compiles to an `ObjectiveFns` whose gradient equals Slice 2's
  kernel on a seeded grid; fails at the base **with `OBJECTIVE_KIND_NOT_ENABLED` from
  `compile_objective`** (`objectives.py:740`). A backend GBM fit test with an approved expression
  objective, and two error cases (an overflowing gradient; a callable slowed past a small round
  budget) asserting the job's error code.
- [ ] **Green.** Dispatch in `compile_objective`; the worker maps Slice 2's
  `NonFiniteDerivativeError` and `RoundBudgetExceededError` through the existing `CodedError`
  path. Register `OBJECTIVE_NONFINITE_DERIVATIVE` and `OBJECTIVE_ROUND_BUDGET_EXCEEDED`, removing
  their markers, one code per commit (split the commit if needed). The persisted job error text
  carries no input value (FD-1219; `PL-1327` DP-S2-4).
- [ ] Commit(s): `feat(modelling): fit with an approved expression objective (FR-144, WK-690 S3)`.

### Task 7: Submission — `OBJECTIVE_NOT_CERTIFIED` and the extra Approver

**Files:** `platform/objectives.py` (`submit_for_review`); `platform/approvals.py` (`submit`);
`errors.py`; `02` (§5.1 marker, the stand-in note; FR-152/FR-163 notes if needed); tests.

- [ ] **Red.** Acceptance 9's tests. Count at the base the template fixtures whose certificate
  is `violated`, and record the count (DP-S3-4's template reach). Rewrite
  `test_submission_without_a_certificate_is_refused` (`:429`) per DP-S3-3, quoted before and
  after; the new assertion fails **on `["code"]`, `VALIDATION_FAILED` where
  `OBJECTIVE_NOT_CERTIFIED` is expected**.
- [ ] **Green.** `submit_for_review` raises `OBJECTIVE_NOT_CERTIFIED` for a missing certificate
  before the transition check; `approvals.submit` takes the DP-S3-4 increment; register the code
  and remove its marker and the stand-in sentence, dated.
- [ ] Commit: `feat(governance): an uncertified objective is refused by name, and a violated one needs another Approver (FR-152, FR-163, WK-690 S3)`.

### Task 8: FR-207's residuals (DP-S3-5)

- [ ] Under DP-S3-5 (a): amend FR-207, dated, moving both residuals to Phase 3 with owner and
  event; update `DECLARED_AND_UNBUILT`'s `model` and `model-spec` notes, the `model_schema/objectives.py:108`
  docstring and the contract staging descriptions that quote the owner (FR-207's 2026-08-25
  sweep list). Under another ruling, the ruling's task replaces this one.
- [ ] Commit: `docs(modelling): FR-207's custom_objective_ref residuals re-noted (WK-690 S3)`.

### Task 9: `FD-1349`'s guard comparison (only under DP-S3-6 (a))

- [ ] Per `.claude/skills/contract-guard`: measure first (the authored enum's 11 names against
  the union of the two tuples), name the expected result, append one comparison and its
  meta-guard to `backend/tests/test_contracts.py`.
- [ ] **Red:** `FD-1349` Evidence 1's broken input (five names replaced by `"BOGUS"`) turns the new
  test red; quote it; revert; green.
- [ ] Commit: `test(contracts): compare the certificate check-name enum with the code (FD-1349, WK-690 S3)`.

### Task 10: NFR-480, measured in a solo window

- [ ] Use the harness that already times certification if one exists (Task 0 finds it);
  otherwise a script that enqueues nothing and calls `certify_expression_objective` with
  `default_sampling`'s shape on §4.6's example, timing the whole call including the smoke fit.
- [ ] Ask the lead for the window (`RL-1263` item 3); record the grant. N ≥ 3 runs under the slot
  wrapper and thread caps; each run's time and load at start and end; median and spread; the
  verdict against 180 s, met or not met, never asserted in the script.
- [ ] Commit: `perf(bench): NFR-480 for an expression objective (WK-690 S3)`.

### Task 11: The gate and the ledger

- [ ] The full two-half gate with every field of Acceptance 13; `pnpm --dir frontend
  generate:api` and `type-check` included (the contract changed).
- [ ] `python3 scripts/doc-index.py`, `--check`, and `uv run python scripts/req-coverage.py`;
  quote each id of the coverage table. FR-366, FR-367 and NFR-480 must now be non-zero.
- [ ] The ledger records the dispatch record, each red-then-green quote and mutation control,
  the parity module's red, the flipped tests before and after, the contention re-check, the
  release note (DP-S3-3's code change; DP-S3-4's template reach), NFR-480's runs, and every
  deviation from this plan, named.

## Risks

1. **The parity check is not cut** (need 3). `PL-1279` is `draft` with no `SL-` row. Until it
   merges, Task 3 cannot start, and Tasks 1 and 2 alone are not worth a lane. Mitigation: the
   lead sequences WK-1178's parity slice first; this plan does not activate before it.
2. **The parity module's predicate may not recognise DP-S3-2's handler-level check.** `RL-1305`
   counts `require_permission(..., permission=…)` as checked; if `PL-1279`'s implementation
   differs, derive's `requires()` site still satisfies the route leg. Task 3's red step shows it.
3. **The definition trigger's write-once rule for `derived`** is new SQL. A trigger that allows
   NULL→value also allows it after approval unless it reads `status`. Acceptance 2 tests both.
4. **DP-S3-3 and DP-S3-4 change existing template behaviour** (a response code; possibly an
   approval count). The status is unchanged; Task 7 counts the reach; the release note states it.
5. **`default_sampling` assumes a log or logistic link** (`platform/objectives.py:464`); an
   expression's link is read from its applicability's responses. A response with another link
   is refused at certify, named, rather than sampled wrongly.
6. **NFR-480 may not be met** on this box with the smoke fit; the verdict is recorded as not met
   with its numbers, never relaxed in the script.
7. **Lane A's merge order.** Three shared paths (File contention): the second to merge
   re-gates; a conflict in `errors.py` across two frozensets is textual, never semantic.
8. **#977's `Permission` column** may land mid-slice and red check-level parsing of `02` §5.1;
   Task 0 and Task 4 re-read it.

## Hand-off

Slice 5 (`SL-1275`) consumes: the stored `derived` block (the view displays it), the routes as
built here, the flag's per-workspace behaviour, and `custom_objective:author`. Slice 4 consumes
nothing from this slice. The Work's close records the flag's state (`RL-1265` DP-3); this slice
leaves it off everywhere.

## Self-review

1. **Spec coverage.** Every row of the coverage table names a task: FR-144 Tasks 1, 2, 4 and 6;
   FR-146 Tasks 5 and 7; FR-150 Task 4; FR-152 and FR-163 Task 7; FR-207 Task 8; FR-366 and
   FR-367 Task 3; FR-448 and FR-449 Task 4; NFR-480 Task 10; NFR-484 Task 4. `RL-1265`'s named
   violation is Acceptance 4.
2. **Premises carry file and line** at `9b0fb97c`; premise s's counts carry the predicate.
3. **Rulings at every site.** `RL-1265`: Goal, Acceptance 4, Task 4. `RL-1305`: need 3, Task 3,
   Acceptance 3. `RL-1263`: Build-start, File contention, Task 10, Acceptance 12.
4. **Deviations named.** `PL-1268` Slice 3's scope does not name fit-time compilation (DP-S3-1),
   a migration (premise q) or the approvals change (premise m); each is stated here rather than
   folded in. WF-702 B2.6 (strategy declared after derive) is met by versioning, a create with
   the same slug, since the definition is immutable.
5. **Type consistency.** `ObjectiveParameter`, `DerivedBlock`, `Permission.CUSTOM_OBJECTIVE_AUTHOR`,
   `derive_objective`, `custom_objective.derived` match across Tasks 1 to 7. New names are this
   plan's proposals; every existing name was read at the tree above.
6. **Placeholders.** The ruling ids in need 5, the revision filename, and the DP-dependent
   statuses stand until their rulings, each named with its DP.
