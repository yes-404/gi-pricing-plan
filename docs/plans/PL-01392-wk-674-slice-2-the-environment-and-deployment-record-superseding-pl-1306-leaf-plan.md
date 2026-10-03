---
id: PL-1392
family: plan
kind: leaf
title: WK-674 Slice 2 — The Environment and Deployment record (FR-267, FR-428, FR-429, FR-272 audit and NFR-498 for deploy), superseding PL-1306 — routes typed both ways, Branch A, order (b): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-03
owner: planner
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-674
slice: SL-1256
supersedes: [PL-1306]
superseded_by: ~
corrected_by: []
relates: [PL-1237, RL-1296, RL-1301, RL-1305, PL-1303, PL-1359, RL-1232, RL-1236, RL-1263, RL-880, RL-886, RL-888, RL-916, CR-1212, FD-1197, FD-1281, FD-1335, FD-1356]
---

# WK-674 Slice 2 — The Environment and Deployment record: leaf plan (supersedes PL-1306)

**This plan supersedes `PL-1306`** (filed under working id 9765; a planner's replan on the
lead's commission, `document-ids.md` §1.6 PL row). In the same commit, `PL-1306` takes
`status: superseded` and `superseded_by: PL-1392`, the only fields a frozen plan may still
take (`document-ids.md` §1.5). Nothing else in `PL-1306` changes. At the mint, the working id
becomes the minted id in both files.

**Why a superseding plan, not a dispatch note.** The maintainer's entry headed
`2026-10-01 10:10:32 BST — WK-674 S2 currency audit: ORDER AMENDED to (b) S2 → FD-1356 fix; a superseding PL for S2; lane-B order SL-1360 → FD-1357 fix → FD-1356 fix; batch C re-cut`
(`~/gi-pricing-plan.local/channel/to-lead.md`), fourth bullet, says "**S2: a SUPERSEDING PL,
yes** (acceptance changes)". The changes come from the WK-674 S2 currency audit at
`origin/main` `1dd5e264` (auditor-wk674s2, read-only; the lead's verdicts in
`~/gi-pricing-plan.local/handover/wk674s2-currency-audit-adopted-2026-10-01.md`), and from that
entry and the entry headed
`2026-10-01 10:10:46 BST — S2 addendum (F-B2 confirmed): the three acceptance items accepted; need 3 text for the superseding PL`.
The content of `PL-1306` is carried forward unchanged except where **Changes from PL-1306**
lists a change.

### Changes from PL-1306

Each change is marked *(PL-1392)* where it stands in the body.

| # | Section | Change | Source |
|---|---|---|---|
| C1 | Acceptance 14, 15, 16 (new); Task 4, Task 5, Task 6; **Route table** (new, under Scope) | **The routes are typed both ways.** The 7 new routes are enumerated, each with a named `model-schema` request type (or none) and a named 2xx type. Three new acceptance items, each red first: request bodies are `model-schema` types (AST walk and OpenAPI); every new 2xx is a `$ref` to a shape published under `docs/contracts/schemas/generated/`, never `{}` or an open object; and S2's deltas on the 2 changed existing routes are typed the same way (their bodies here; their 2xx left untyped by DP-S2-6 (c), C12–C13) | F-B2; the 10:10:46 entry, first bullet; the entry headed `2026-10-01 10:03:41 BST — Lane A: WK-674 S2 (SL-1256, PL-1306) AGREED as the pick; …`, "Add (a)" |
| C2 | Acceptance 8; Tasks 0, 4, 5; premise q | **Branch A only.** `RL-1305` has merged, so `06` §4.1 has the `Check owner` column (`06:269`), with `WK-674` on `deployment:promote` (`06:283`) and `admin:manage_environments` (`06:294`). Branch B is struck. `PL-1359:372-376`: once `SL-1360` merges, `STALE_OWNER` fails a commit that adds a check and leaves its cell | the audit's `RL-1305` D1 item 4 row; the 10:10:32 entry, fourth bullet |
| C3 | Task 6; Acceptance 17 (new); Write set | **F-B1.** `_fetch_bundle` is also called by the governance gate (`backend/src/app/api/models.py:1215`), and `_compiled_for` is reused by `backend/src/app/worker/scoring_handlers.py:85`/`:208` and `backend/src/app/worker/trace_handlers.py:30`/`:82`. All are read-only to this slice. The Deployment is resolved in the score handler, beside the ref, **without changing `_fetch_bundle`'s or `_compiled_for`'s signature or return type** | F-B1 (METHOD); the 10:10:32 entry, fourth bullet |
| C4 | Task 1; Write set; premise p | **`03` §4.12** for the `Deployment` subsection (§4.11 is `SubGraph`, `03:743`), in place of "the next free number at merge" | the 10:10:32 entry, fourth bullet |
| C5 | Acceptance 3; Task 3; premise o | **Alembic head `2f598e89d12c`** (`backend/migrations/versions/2f598e89d12c_sub_graph_versions.py`), in place of `d7e2a9b5c418` | the same |
| C6 | Acceptance 12 (a); premise n | **141 operations**, re-measured with the predicate stated verbatim, in place of "137 at the finding's tree" | the same |
| C7 | Status (activation need 3); Write set; Global Constraints | **Order (b): S2 → the FD-1356 fix.** Need 3 becomes "S2a (`SL-1302`) and the fix slice `SL-1300` are closed" (both are). The FD-1356 fix is **not** a need of this slice; that fix's plan carries "WK-674 S2 merged" as its own activation need | the 10:10:32 entry, first bullet; the 10:10:46 entry, second bullet |
| C8 | Write set; Global Constraints; Status (dispatch needs) | **Never concurrent with `SL-1367`** (`PL-1364`, FD-1335 Part A, also edits `backend/src/app/api/score.py`); the dispatch records say so | F-B4; the maintainer's quoted decision of 2026-10-01 ~10:10 BST |
| C9 | Status; DP table; Acceptance 7 | **DP-S2-1** cited as "RL-1380 (#974)", read at head `6bc51cf0`; kept out of `relates:`; "#974 merged and minted" stays an activation need | the lead's commission |
| C10 | Premises; every locator | Re-derived at the tree above (`1dd5e264`) | the 10:10:32 entry ("refreshed locators") |
| C11 | Acceptance 4 (FR-357); Task 6 | **A correction found in carrying forward.** `PL-1306` said a client *sending* `artifact_is_live: false` is refused with 409. Once the field is removed and `Withdraw` keeps `extra="forbid"`, sending it is refused with **422** `VALIDATION_FAILED`, and omitting it gives the 409. Both cases are now tested | this planner, on the carry-forward self-review |
| C12 | DP table (DP-S2-6, new, blocking); Acceptance 16; Route table rows 8–9; activation need 2 | **The 2xx half of item 16 is a decision point.** Read at the tree above, `service.to_dict` (what both changed routes return) disagrees with `ApprovalRequest` and with the hand-authored `approval-request.schema.json`, so no existing shape can be declared without a §0 reconciliation. Options and a recommendation, not a pick | this planner, measuring item 16 before writing it |
| C13 | DP-S2-6 row; Acceptance 16, 18 (new); Route table rows 8–9; Tasks 5, 6; activation need 2 *(2026-10-01, pre-merge)* | **DP-S2-6 decided (c)** by the maintainer; the two 2xx stay untyped, owned by FD 9752 (working id); **new Acceptance 18**, red first: S2 does not widen the untyped surface (exact key sets pinned) | the maintainer's entry headed `2026-10-01 10:32:26 BST — #1062 DP-S2-6: option (c) ACCEPTED with three conditions; it narrows my item (3) for the 2 CHANGED routes' 2xx only; the three-shape disagreement becomes its own FD` (`~/gi-pricing-plan.local/channel/to-lead.md`); the lead's message of 10:33 BST |
| C14 | DP table (DP-S2-7, new, blocking); Acceptance 19; Task 5A (placeholder); activation need 3a; Write set *(2026-10-01, pre-merge)* | **Compiling a non-draft Rating Version** (FD-1393): S2 does not merge unless it is handled as RL-1379 rules, red first | the maintainer's entry headed `2026-10-01 10:34:45 BST — FD 9754 (#1064, a non-draft rating version can be recompiled and its bundle rewritten): MEDIUM, owner WK-674 S2, and **S2 does not merge without the guard**; the option choice goes to a DM now`; the lead's message of 10:35:31 BST |
| C15 | Acceptance 2; Task 2; Write set *(pre-merge)* | Every new generated-only slug in `ONE_SIDED_SLUGS`; `test_contracts.py` and the FD-1357 fix (PL-1376; #1057), PL 9788, `PL-1364` and WK-1250 named as overlappers | auditor-1062 F1 (MED), adopted |
| C16 | Acceptance 17; Acceptance 15 *(pre-merge)* | Acceptance 17's second check is an AST comparison of `args` and `returns` (the `grep` was blind to an added parameter); "13 existing `Page_*_`" corrected to 12 typed plus the open `Page_dict_str__Any__` | auditor-1062 F2 (LOW-MED) and its note, adopted |
| C17 | `relates:`; Global Constraints *(disclosed pre-merge)* | Two changes made in the first filing and not announced there: (a) `relates:` gained `PL-1359`, `FD-1335`, `FD-1356`; (b) the dated note that WK-690 Slice 1 is `SL-1271`, closed, so PL-1306's two RL-1263 conditions against it no longer bind | auditor-1062's notes, adopted |
| C18 | Acceptance 2; Task 2; Write set *(pre-merge)* | Every new generated schema registered in `_CONTRACT_ARTIFACT_PATHS` and the `non_markdown` count bumped, else checks 30 and 35 fail; serialised with the FD-1357 fix | auditor-1065's cross-finding (on the FD-1357 fix), relayed by the lead; the maintainer's addendum (second to merge re-bumps; first to merge writes the `contract-schema` skill step) |

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` (Tasks 2–6), `python-test` (every task), `fastapi-service` (Tasks 4–6) and `dev-commands` (the gate and the migration), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make an **Environment** a real object and a **Deployment** a recorded, audited act: a
Deployer binds an `approved` Rating Version to an Environment, the platform refuses the act
when promotion order, approval, permission or reference type says no, and `/score` then
serves the version that is live in the caller's environment instead of refusing.

**Architecture.** `model-schema` gains the `Environment` and `Deployment` shapes, a skip
field on `ApprovalPolicyEntry`, and one pure promotion-order predicate beside `entry_for`.
The backend gains an `environments` table (seeded `dev → uat → prod`), an append-only
`deployments` table, an environments router and a deployments router, and a nullable
Deployment reference on `scoring_traces`. The deploy route and the `prod` approval
submission both call the one predicate. The route writes its Audit Event in its own
transaction. The switch itself is **not** built here: a Deployment takes effect through
the existing per-request resolution, which Slice 5 replaces (`PL-1237` Task 2).

**Tech Stack:** Pydantic v2, FastAPI, SQLAlchemy 2.x async, Alembic, pytest. **No new
dependency**: this slice touches neither `uv.lock` nor any `pyproject.toml` (see **Write set**).

**Spec:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3.10 — **FR-267** (`03:195`
  at the tree above), **FR-272** (`03:200`, its Audit Event limb only, as `RL-1252` leaves it);
  §9 **NFR-498** (`03:1202`, the deploy limb only); §5.1 (`03:775`, deployment rows `:805-807`);
  **FR-238** (`03:135`) and **FR-250** (`03:162`), read for the default-live path.
- [`../specs/07-platform.md`](../specs/07-platform.md) §3.5 — **FR-428** (`07:139`), **FR-429**
  (`07:140`, as amended by `RL-1232` DP-7 and by RL-1296); §4.2 `Environment`
  (`07:245-259`); §5.1 (`07:297`, environment rows `:306-307`).
- [`../specs/06-governance.md`](../specs/06-governance.md) — §3.3's "Deployment to `prod`" row
  (`06:121`); **FR-364**'s floor (`06:381-387`); §4.1 (`06:188`); §4.2 (`06:342`, JSON
  `:344-370`, the `deployment` entry `:362-364`); **FR-347** (`06:83`); **FR-357** (`06:98`);
  **FR-368** (`06:154`, read-only: WK-679's).
- [`../specs/00-overview.md`](../specs/00-overview.md) §2 (Deployment, Environment) and §4's ER
  line `Deployment ──< ScoringTrace` (`00:264`).

**What this plan implements.** WK-674's map plan, **PL-1237**, **Task 2 — "Slice 2: the
Environment and Deployment record"** (`PL-1237:768-826` at the tree above), with its carried
obligations (`:362-444`) and the Slice 2 rows of its permission table (`:481-484`). The
slice row is **SL-1256** in `docs/roadmap.md`.

## Status

**Draft**, filed 2026-10-01 against the tree above, under working id 9765. *(PL-1392.)* The
superseded plan's history, carried forward: `PL-1306` was filed under working id 9920 and
minted on 2026-09-30 in the lead's mint batch 2. #971 is `RL-1301`, #942 is `RL-1305`, and
Slice 2a's plan (#984) is `PL-1303` with its row `SL-1302`. #978's finding is minted as
`FD-1356`. **#974** (DP-S2-1) is not minted at the tree above; it is cited as **"RL-1380
(working id; #974)"**, read at its head `6bc51cf099427d3605ad846f8cec2a3c8dcd7cb7`, and kept out
of `relates:` until it mints (in batch C, by the 10:10:32 entry's fifth bullet). #977
(DP-S2-4) is not minted either and stays cited by PR number. The slice row already exists
(**SL-1256**), so this PR cuts no `SL-` row. It appends one dated line to that row naming
this plan.

**Activation needs, in order** *(PL-1392: need 2 re-cited, need 3 replaced by order (b))*:
1. **OQ-1234 decided** — done by **`RL-1296`** (#935, working id 9901; read at its head
   `75f6ca2ef22f29f95528c6f197345588bbd3803d`, merged to `main` as `65b33479`). *(Revised
   2026-09-30 after the merge: the PR-number citations are replaced by the id throughout, and
   the id is added to `relates:`. RL-1301 C amends its item 3; that pair is the lead's to set at
   RL-1301's mint.)*
2. **DP-S2-1, DP-S2-2, DP-S2-3 and DP-S2-5 below resolved, and #974 merged and minted** —
   the four are ruled: DP-S2-1 by RL-1380 (#974, head `6bc51cf0`), DP-S2-2 and
   DP-S2-3 by RL-1301 A–B, DP-S2-5 disposed by RL-1301 A.6 (head `80afeb40`; A.6 is unchanged since `327e1179`).
   **#974 is not yet merged and minted** (batch C): this need is open until it is.
   *(PL-1392, C12.)* **And DP-S2-6 resolved** (new in this plan, blocking the 2xx half of
   Acceptance 16). **Done 2026-10-01: (c), by the maintainer's entry headed `2026-10-01 10:32:26 BST — #1062 DP-S2-6: option (c) ACCEPTED with three conditions; it narrows my item (3) for the 2 CHANGED routes' 2xx only; the three-shape disagreement becomes its own FD` (`~/gi-pricing-plan.local/channel/to-lead.md`).** Condition 3 of that entry: auditor-1062 verifies the three-shape premise field by field before this plan mints; if the premise is wrong, (c) falls and DP-S2-6 goes to a decision-maker.
   **DP-S2-4 does not block this slice** (the maintainer's entry headed
   `2026-09-30 11:17:35 BST — DATED CORRECTION to my A1 entries (12:0x "pin each route's permission against the spec's declared permission (06/03 §5.1 permission column, or the contract)"); DP-S2-4 routing`).
   *(2026-09-30: DP-S2-2 and DP-S2-3 are ruled by RL-1301, working id 9906, read at its head
   `5fb440fb9b29c335eddb714fa5cea51705e8e0af`, dm-effort-high. RL-1301 was ruled from the lead's
   relay before this plan was pushed; this revision aligns the plan to it at every site class,
   each marked *(RL-1301)*. A later revision applies RL-1301's A.6 at head
   `324ea1659ca1542db4b1e362dc3864da6a476bbb` and #974.)*
3. **"S2a (`SL-1302`) and the fix slice `SL-1300` are closed"** — the text the 10:10:46 entry
   gives, verbatim. **Both hold at the tree above:** `docs/roadmap.md`, `#### SL-1302`,
   closed 2026-09-30 at #997's merge; `#### SL-1300`, `status: closed`. *(PL-1392: replaces
   PL-1306's need 3, "Slice 2a closed, and then the validation-rule fix slice closed", in the
   order S2a → the fix → S2.)* **The order is now (b): S2 → the FD-1356 fix**, by the
   10:10:32 entry's first bullet, which supersedes item 1 of the maintainer's entry headed
   `2026-09-30 11:56:33 BST — DECISIONS: slice order after the split; FR-384 confirmed; FR-383 and FR-385 owners`.
   **The FD-1356 fix is not a need of this slice.** That fix's own plan carries "WK-674 S2
   merged" as its activation need (the 10:10:46 entry, second bullet). The two never run
   concurrently: both edit `backend/src/app/platform/approvals.py` and `_carry_to_the_artifact`
   in `backend/src/app/api/approvals.py` (**Write set**).
3a. **RL-1379 ruled and minted** *(PL-1392, C14)*: DP-S2-7 below, the decision-maker
   dm-s2c7's ruling, in progress at the tree above. Open.
4. **The lead's go.**

**The split, as a dated delta to the map plan** *(2026-09-30)*. The maintainer's entry headed
`2026-09-30 11:48:28 BST — DECISION + ACCEPTANCE (maintainer by delegation): WK-674 S2 split, option (b), S2a = the approval guard`
accepts it, in the line the entry gives for the map plan, verbatim:

> 2026-09-30 — the maintainer (by delegation) accepts the split of WK-674 Slice 2 into S2a (the approval guard, first) and S2 (deployment), per #973's self-review option (b).

`PL-1237` is `active` and frozen (`document-ids.md` §1.5; `scripts/audit-docs.py` check 34
refuses any other change), so the delta is recorded here and in Slice 2a's leaf plan, as
`PL-1239` recorded its map-plan deviation; `PL-1237` is not edited. **Moved out of this
plan:** Task 3A and the guard half of Acceptance 13 (to Slice 2a). **Kept:** everything else,
including Task 0A and the deployment-request plant (Acceptance 13 as re-cut). Sites that
named Task 3A are marked where they stand.

**Dispatch needs** (the lead's, not activation conditions — listed so the dispatch record
can cite them):
- **#960 (the OQ-1234 roadmap strike) merged before dispatch**, and the dispatch record cites
  it. Set by the maintainer's entry headed
  `2026-09-30 10:07:37 BST — #935 CLEAN noted; DECISION: roadmap strike goes in a follow-up PR`
  (`~/gi-pricing-plan.local/channel/to-lead.md`), first bullet.
- **The RL-1263 write-set check** against every build slice in flight at dispatch (see
  **Write set**), and the contention measurement if this is the first overlap (see **Global
  Constraints**).
- **Never concurrent with `SL-1367`** *(PL-1392, F-B4)*: `PL-1364` (FD-1335 Part A) edits the
  route decorators in `backend/src/app/api/score.py`, which Task 6 also edits. The dispatch
  record of this slice, and of `SL-1367`, each say so and name the order. Under the lane-B
  order of the 10:10:32 entry (third bullet), `SL-1367` comes later anyway.
- **Serial with the FD-1356 fix, this slice first** *(PL-1392, order (b))*: the dispatch
  record names it.

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means
the failing run is quoted in the ledger with its failing assert line **and the cause the
step predicts**; a failure for any other cause is a plan defect, reported, not worked around.
"Red on broken input" means the guard is green, then deliberately disabled (the named line
deleted or the named call patched to a no-op), the test is shown red with the predicted
cause, and the guard is restored; the ledger quotes both runs.

1. **Spec.** Task 1's edits are made through `spec-change`, before any code that implements
   them, and `python3 scripts/audit-docs.py` exits 0 on the commit. `03` §3.10's FR-267..FR-272
   rows are **not** reworded; each spec change is a dated note or an appended row, section or
   contract. If the executor believes an existing requirement needs rewording, it stops and
   reports.
2. **Contract.** `uv run python scripts/generate-contracts.py --check` exits 0 after
   regeneration. The regenerated schemas under `docs/contracts/schemas/generated/` include
   `environment` and `deployment`, and `approval-policy`'s schema carries the skip field. Each
   new shape is declared once, in `model-schema`, checked by count:
   `git grep -n -E '^class (Environment|Deployment)\b' -- packages backend/src frontend/src`
   prints **exactly three** lines: two in `packages/model-schema/src/model_schema/deployments.py`,
   and the runtime-mode enum `backend/src/app/config.py:32` (`class Environment(enum.StrEnum)`),
   which the pattern also matches. `EnvironmentRow` and `DeploymentRow` do not match (`\b`).
   Any other count fails this item. *(PL-1392, C1.)* The Route table's shapes are counted the
   same way:
   `git grep -n -E '^class (EnvironmentCreate|EnvironmentUpdate|DeploymentRequest|DeploymentRequestCreate|DeploymentCreate|PromotionSkip|ApprovalWithdrawal|ApprovalSubmission)\b' -- packages backend/src frontend/src`
   prints **exactly eight** lines: five in `deployments.py` and three in
   `packages/model-schema/src/model_schema/approvals.py`. The regenerated
   `docs/contracts/schemas/generated/` holds a file for each slug in the Route table. The
   contract guard (`contract-guard`) passes, quoted. *(PL-1392, C15; auditor-1062 F1.)* Every new
   generated-only slug is declared in `ONE_SIDED_SLUGS` (`backend/tests/test_contracts.py:69`)
   with a "first written form" reason, as the `sub-graph*` entries are (`:77-79`):
   `environment`, `environment-create`, `environment-update`, `deployment`,
   `deployment-create`, `deployment-request`, `deployment-request-create`,
   `approval-withdrawal`, `approval-submission`, and `promotion-skip` if it is registered. The
   guard's own check (`:2648-2661`) fails on an undeclared one-sided slug, so the red first is
   the guard run after registration and before the entries are added, naming each slug.
   *(PL-1392, C18; auditor-1065's cross-finding, relayed by the lead.)* Each new generated
   schema file is also registered as a literal path in `_CONTRACT_ARTIFACT_PATHS`
   (`scripts/audit-docs.py:2620`; the new paths go after `:2667`), and `tests/test_audit_docs_ids.py:2117`'s `assert len(non_markdown) == 70` is
   bumped by the number of files added (70 at the tree above; +9, or +10 with
   `promotion-skip`). Without both, `python3 scripts/audit-docs.py` fails check 30 (no front
   matter) and check 35 (not in the F83 register) on each new file. **Check:** with the new
   files present, `python3 scripts/audit-docs.py` reports no check 30 or check 35 failure, and
   `uv run pytest tests/test_audit_docs_ids.py -q` passes. **Red first:** regenerate the
   contracts before registering the paths, and quote the check 30 and check 35 failures naming
   the new files.
   **Shared with the FD-1357 fix** (PL-1376; +2) under RL-1263 (`:89`), and with any
   other slice adding generated schemas. A count bump is not append-only, so **the second of
   the two to merge re-bumps on the merged count and re-runs its gate**; it never adds to a
   number read earlier (the maintainer's addendum, relayed by the lead, 2026-10-01).
   Precedent: `SL-1339` (#1034, plan `PL-1325`, the sub-graph slice) moved it 67 → 70
   (`git log -S'len(non_markdown) == 70' -- tests/test_audit_docs_ids.py` prints `9b0fb97c`).
3. **Migration (FR-417).** One new Alembic revision, whose `down_revision` is the head at
   the executor's tree (`2f598e89d12c` at the tree above, *(PL-1392)* the one revision no
   `down_revision` names, in `backend/migrations/versions/2f598e89d12c_sub_graph_versions.py`;
   re-pointed at merge per RL-1263).
   `uv run alembic upgrade head`, `downgrade -1`, `upgrade head` all exit 0 against a scratch
   database, and `uv run pytest tests/test_repository_invariants.py -q` passes. A migration
   test asserts: the `environments` table holds `dev`, `uat`, `prod` with promotion orders 1,
   2, 3 and `requires_prior_environment` null, `dev`, `uat`; **pre-existing `scoring_traces`
   rows keep their `environment` string and get a null Deployment reference** (there was no
   Deployment to serve them; see DP-S2-1's premise), tested on rows inserted before the
   upgrade (`PL-1237` Task 2 gate: "tested on existing rows"). A `scoring_traces.environment`
   value outside the seeds (for example `staging`) is kept unchanged, with a null Deployment
   reference: the column stays a string and is never a foreign key, so it cannot dangle.
   **Existing credentials (auditor-plans V2):** the upgrade **refuses to run** while any
   unrevoked API key's `environment` (`backend/src/app/db/models.py:462`; `revoked_at`
   `:468`) or any non-archived Service Account's `environments` list (`:430`; `archived_at`
   `:437`) names an environment other than `dev`, `uat` or
   `prod`. **An expired but unrevoked key does not block it** (auditor-plans, on V2): such a
   key is refused at authentication (`backend/src/app/auth/service.py:205`, `expires_at`
   `models.py:467`), so it can never produce a `Caller.environment`, and nothing makes it
   valid again — rotation mints from the account's `environments` list
   (`backend/src/app/api/service_accounts.py:246`), never from the old key, and only
   shortens the old key's expiry (`:243-244`). The account's list is checked on its own, so
   a stray name there still blocks. It stops before any change, with an error naming each key id or account id and
   the name it carries, and telling the operator to revoke the key, or narrow or archive the account, first (see
   **Decided in this plan** for why). Tested on rows inserted before the upgrade: a key
   naming `staging` makes `upgrade head` fail and leaves the database at the previous
   revision; after the key is revoked, the upgrade succeeds; a key naming `uat` does not
   block it.
4. **The refusals, each by its cause, each red first or red on broken input.** In
   `backend/tests/test_deployments.py` and `backend/tests/test_environments.py`, each test
   marked with its requirement:
   - **(FR-267)** a `prod` deployment with no complete approval record → 409
     `DEPLOY_REQUIRES_APPROVAL`;
   - **(FR-267, FR-238)** a Rating Version in `draft` or `review` → refused, naming its
     status; only `approved` deploys;
   - **(G3)** a deploy request naming a `sub_graph` reference, and one naming each other
     non-`rating_version` type in `ARTIFACT_TYPES` (`refs.py:21-31`, parametrised over the
     set minus `rating_version`), is refused with 422 `VALIDATION_FAILED` naming the type,
     **before** any row is read. Red on broken input: with the type check deleted, the
     `sub_graph` case is shown to reach the Rating Version loader;
   - **(FR-429, the one predicate)** a `prod` deployment with no successful `uat` deployment
     and no permitted skip → refused at the route with 409 `PROMOTION_ORDER_VIOLATION`
     **and** at the `prod` approval submission with 422 `EVIDENCE_INCOMPLETE`. A test flips
     the policy's skip field and shows **both** refusals flip together;
   - **(FR-429)** a permitted skip whose reason is empty or whitespace → refused by both;
   - **(FR-429, the blanket skip — condition 1)** the skip field on an **unqualified**
     `deployment` entry (`environment` null), and on a **non-`deployment`** entry, is
     refused by `ApprovalPolicy` validation, so `set_policy` cannot store it. **The fallback
     path**: with a policy holding only an unqualified `deployment` entry, `entry_for("deployment",
     "prod")` falls back to it (`approvals.py:146-162`) and the predicate grants **no** skip,
     so the `prod` deployment without `uat` is refused. Each red on broken input, with the
     validator's check deleted;
   - **(FR-428)** the route enforces order for a configured fourth environment, which the
     `prod`-only floor does not cover (`07:140`, last amended clause);
   - **(FR-267)** a caller without `deployment:promote` → 403 `PERMISSION_DENIED`;
   - **(`CR-1212` item 4; RL-1301 B.5, each red first)** a Deployer assigned only to `uat`
     deploys in `uat` and is refused on `prod` with 403; a workspace-wide Deployer deploys to
     both; **with the handler's `resource=` argument removed**, the `uat`-only Deployer is
     refused in `uat` as well, and the test fails; a Service Account is still refused (FR-347);
   - **(RL-1301 A.4, the FD-1200 class, each red first on broken input)** a deployment request
     whose row lacks either floor item (`rating_version_approval`, or the `uat_deployment`
     predecessor item), or is stripped of it by a fixture, is refused at submission with 422
     `EVIDENCE_INCOMPLETE`, **and** a decision on such a row is refused; with the check
     removed, the fixture is approved and the test fails. An attempted update of a submitted
     request's evidence or pins through the module's functions is refused;
   - **(RL-1301 audit advisory A2; auditor-plans F3, red first)** a generic
     `POST /api/v1/approval-requests` naming `deployment:…` is refused when no row exists,
     when the row is not in `review`, and when a fixture has stripped a floor item from its
     `evidence`; so no approvable deployment request exists without pinned evidence (Task 5
     step 6 gives the reason);
   - **(auditor-plans F4, red first)** a decision on a deployment request that is not in
     `review` is refused by `require_in_review` in the deployment module's
     `apply_approval_decision`, not only by the route;
   - **(auditor-plans F5, red first)** two concurrent deploys naming one approved Deployment
     Request produce **exactly one** Deployment row and one `deployment.created` event; the
     other is refused with 409 `DEPLOY_REQUIRES_APPROVAL`. Red on broken input: with the
     `WHERE status = 'approved'` condition removed, two Deployments are written;
   - **(A3; RL-1301 A.6, each red first)** changing `prod`'s display `name` leaves it gated: a
     deploy to it still requires its approved Deployment Request (with resolution keyed on
     the display name, this test fails); a request to change `prod`'s **slug** is refused
     with 422 `VALIDATION_FAILED` naming the slug as immutable; `set_policy` refuses a
     `deployment` entry naming `prd`, a slug no Environment has, with 422
     `VALIDATION_FAILED`; **retiring an Environment that a policy entry names is refused**
     with 409 naming the entry (this plan's choice, below), until the entry is removed;
   - **(auditor-plans N1–N3, each red first)** `POST /api/v1/environments` refuses a slug
     that does not match `_SLUG` (`refs.py:33`) — a one-character slug and an upper-case
     slug — with 422 `VALIDATION_FAILED` (N2); creating an Environment with the slug of a
     **retired** one is refused, because a slug is never reissued (N1: otherwise an old
     `deployment:<slug>@n` reference would come to mean a different Environment); after
     `uat` is retired, `set_policy` refuses a `deployment` entry naming `uat`, and a Service
     Account key naming `uat` is refused (N3: "an existing Environment slug" means a
     **non-retired** one);
   - **(RL-1301 A.6 at `80afeb40`, credentials, each red first)** creating or rotating a Service
     Account key whose `environments` names `prd`, a slug no Environment has, is refused with
     422 `VALIDATION_FAILED` naming it; retiring `uat` while an unrevoked key names it is
     refused with 409, until the key is revoked or its environments are narrowed;
   - **(RL-1301 A.5)** a deploy to an approval-gated target naming no **approved** Deployment
     Request is refused with 409 `DEPLOY_REQUIRES_APPROVAL`; a request whose **pinned**
     predecessor item no longer satisfies FR-429's predicate is refused at the route with 409
     `PROMOTION_ORDER_VIOLATION`;
   - **(FR-347)** a Service Account caller (API key) is refused on the deploy route;
   - **(RL-886)** with a policy that has no `deployment` entry, the `prod` approval submission
     is refused with 422 "No approval policy for this artifact type"
     (`backend/src/app/platform/approvals.py:260-267`), **before** any evidence is read;
   - **(FR-272, NFR-498, `RL-1232` DP-4)** every Deployment row has exactly one Audit Event
     with before/after state, written in the same transaction. Red on broken input: with the
     `audit.record` call patched to a no-op, the test is red because the Deployment committed
     with no event;
   - **(FR-428, `RL-1236` DP-B)** a caller without `admin:manage_environments` creating,
     renaming or retiring an Environment → 403 `PERMISSION_DENIED`;
   - **(FR-357)** withdrawing the approval of a Rating Version that has a Deployment →
     409 `WITHDRAW_AFTER_DEPLOY_FORBIDDEN`, **with liveness derived by the server** (Task 6),
     not taken from the request body. *(PL-1392, C11.)* A body that omits `artifact_is_live`
     gets the 409; a body that still sends it gets 422 `VALIDATION_FAILED` naming the field,
     because the field is gone and the body keeps `extra="forbid"`. Neither withdraws;
   - positive controls: a Deployer deploys an approved version to `dev`, then `uat`, then
     (with the `prod` approval) `prod`; a permitted, reasoned skip deploys to `prod`.
5. **The dependency direction (DEP-1, RL-1296 item 4).** The predicate lives in
   `packages/model-schema/src/model_schema/approvals.py`, reads only its arguments, and loads
   nothing. `git grep -n -E 'from app\.(platform|api)\.(deployments|rating)' --
   backend/src/app/platform/approvals.py` prints nothing. (Environments are `07`'s, so PLAT,
   left of GOV in DEP-1's order: `set_policy`'s existence check of RL-1301 A.6 may read them.) (No `lint-imports` contract covers
   modules inside `app`, so this command and the review are the check.)
6. **Default-live scoring (RL-880, register F43 L1).** In `backend/tests/test_score.py`:
   an API-key caller scoped to an environment with a Deployment, posting no
   `rating_version_ref`, is scored against that Deployment's Rating Version; an environment
   with no Deployment still gets 409 `NO_LIVE_RATING_VERSION`; a bearer caller (no
   environment) with no ref gets the same 409. Each red first: before Task 6, the first case
   gets the 409.
7. **The trace link (RL-888, RL-916; DP-S2-1 ruled (a) by RL-1380 (#974), read
   at head `6bc51cf099427d3605ad846f8cec2a3c8dcd7cb7`).** *(PL-1392: PL-1306 read `849dce65`.)* In `backend/tests/test_traces.py`, each
   red first: a default-live score's sampled trace carries the serving Deployment's id; an
   explicit ref **equal** (type, slug and version) to the live Deployment's Rating Version
   carries that Deployment's id; an explicit ref to a non-live version, or another version of
   the same slug, carries null; an explicit ref in an environment with no live Deployment
   carries null; **the switchover case**: a Deployment recorded between the bundle's
   resolution and the trace write does not relink the trace (the id resolved with the bundle
   is the one written, `03` FR-268); **the completion case** (#974 F1): after
   `complete_pending_trace` deletes and re-inserts the row, the Deployment id is still
   there. The `environment` string is written exactly as today.
8. **The `STALE_OWNER` obligation (RL-1305 D1 item 4) — Branch A** *(PL-1392, C2)*. `RL-1305`
   has merged: at the tree above `06` §4.1 carries the `Check owner` column (header row
   `06:269`), and the cells read `WK-674` on `deployment:promote` (`06:283`) and on
   `admin:manage_environments` (`06:294`). Each cell is **emptied in the commit that adds its
   check**: Task 4's commit for `admin:manage_environments`, Task 5's for
   `deployment:promote`. The predicate, verbatim:

   ```bash
   grep -c -E '^> \| `(deployment:promote|admin:manage_environments)` \|.*\| WK-674 \|$' docs/specs/06-governance.md
   ```

   It prints **2** at the tree above (measured), **1** on Task 4's commit and **0** on Task
   5's commit; on each, the emptied row still exists, with an empty last cell. Once `SL-1360` (`PL-1359`) has merged, its parity test
   (`tests/test_permission_parity.py`) also passes on each commit; before then the ledger
   says it was not yet on `main`. Red first: on the commit that adds the check, with the
   cell left as `WK-674`, the parity test (if merged) fails with `STALE_OWNER` naming the
   permission (`PL-1359:372-376`: "If the cells were not cleared, `STALE_OWNER` fires on the
   first run"); if `SL-1360` has not merged, the ledger records that this red cannot be shown
   and why. ~~Branch B — RL-1305 has not merged: the slice does not touch those cells, and the
   ledger records that RL-1305's mint turn clears them in its own PR.~~ *(Struck 2026-10-01:
   `RL-1305` has merged, so the fallback set by the maintainer's entry headed
   `2026-09-30 10:59:49 BST — DECISION: WK-674 S2 vs #942's STALE_OWNER: option (a), placed after the fix pair, with (b) as automatic fallback`
   cannot arise.)* The ledger names the `origin/main` SHA it read.
9. **Coverage.** `uv run python scripts/req-coverage.py` lists tests against FR-267, FR-428,
   FR-429, FR-272, NFR-498, FR-347 and FR-357. FR-272's notification limb is recorded as
   *deferred with an owner — WK-688* (`RL-1252`), not claimed.
10. **The gate.** Every full `pytest`, full gate or multi-database sweep, by the executor or
    the auditor, runs inside a gate slot — `flock -w 1800 -E 99 /tmp/slots/gate-1 <cmd>` or
    `gate-2`, **with no `--`** — and `uptime` is reported with each slot grant (the
    maintainer's entry headed
    `2026-09-30 11:42:08 BST — two decisions: the escaped-pipe checker blindness → a LOW FD; box load → heavy audit runs take a gate slot`).
    **Tightened** by the entry headed
    `2026-09-30 11:43:28 BST — the slot rule, tightened: suite-level runs count`: any run of a
    whole test directory or package suite (pytest over a directory, `-k` over a suite) also
    takes a slot, and slotted runs set `LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2
    OPENBLAS_NUM_THREADS=2`. Only named single test files or node ids, and the docs checks,
    are exempt. This is also a dispatch condition.
    The full two-half gate (`CLAUDE.md` §11) exits 0 on the committed tree,
    with every command's rc, the `N passed` line and `HEAD` quoted in the ledger, against
    main's `N passed`.
11. **Item 11** (`PL-1237` Tasks preamble): before the lead merges, the maintainer's
    **MERGE-ACK**, naming the PR's full head SHA, is recorded in the lead's channel file
    (`~/gi-pricing-plan.local/channel/to-lead.md`), given by the maintainer or on the
    maintainer's behalf, **never posted on the PR**; and the slice's clean audit is filed. A
    Slice closes on a clean audit and the lead's merge (`CLAUDE.md` §13).
12. **The authorisation sweep sees every route (Task 0A — the first build task, before any
    new route).** Source: auditor-922's A1 finding, **MEDIUM**, owner this task (cited as
    prose until it is filed), and the maintainer's entries headed
    `2026-09-30 11:01:50 BST — DECISION: candidate A1 (vacuous authorisation sweep): evidence, severity rule, owner WK-674 S2`,
    `2026-09-30 11:06:50 BST — A1 reproduced: decisions pending switch_workspace; the fix's shape`,
    `2026-09-30 11:08:22 BST — A1 = MEDIUM, conditional on the behavioural switch_workspace confirmation`
    and `2026-09-30 11:09:37 BST — A1 MEDIUM confirmed behaviourally; the condition is met`.
    In `backend/tests/test_api_authorisation_sweep.py`, each red first:
    - **(a) flattened:** the static sweep walks included routers (FastAPI's
      `_IncludedRouter.original_router.routes`, as the finding records it for 0.141.1),
      and asserts the number of `(method, path)` operations it iterated **equals** the number
      of operations in `app.openapi()["paths"]`. *(PL-1392, C6: re-measured at the tree above
      as **141**, over the committed `docs/contracts/openapi/generated.json`, with this
      predicate, verbatim:
      `python3 -c "import json; d=json.load(open('docs/contracts/openapi/generated.json')); print(sum(1 for p in d['paths'].values() for m in p if m in {'get','put','post','delete','options','head','patch','trace'}))"`
      — 141 operations over 120 paths, methods present `delete`, `get`, `patch`, `post`,
      `put`. The finding's own tree gave 137. This slice adds 7, so the figure at its merge is
      148 plus whatever else has merged; the test reads `app.openapi()` live and never pins a
      number.)* Red first: at `PL-1306`'s tree the loop iterated the 2 open routes; the
      executor quotes the iterated count at its own tree, and the equality fails naming both
      counts;
    - **(b) a guard removed is seen:** with `requires()` removed from one real guarded route
      in the test's setup, the static sweep fails naming that route;
    - **(c) moved out of this slice** (the 11:17:35 entry): pinning each route's permission
      against a spec declaration goes to the WK-1178 slice #977 (DP-S2-4 (a), a Permission
      column on every §5.1 row) names, with its red first
      on the `AUDIT_READ → JOB_READ` swap (`backend/src/app/api/audit.py:52`). **This slice's
      new routes** (the environments, deployment-request and deploy routes) get their
      permission declared in that mechanism by **whichever of this slice and that one lands
      second**, and the later one checks the earlier's routes;
    - **(d) the no-roles behavioural sweep asserts 401 or 403, with a valid body per route.**
      A 422 is not a refusal. Red first on `POST /api/v1/me/workspace`, which passes today
      only because an empty body is refused with 422;
    - **(e) a named allow-list, with file:line, of the handler-guarded routes**, each checked
      by the test to still contain its `require_permission(` (or membership refusal) at the
      named site, so the list cannot rot silently: `POST /api/v1/validation-rules`
      (`backend/src/app/platform/validation_rules.py:200` and `:207`); `POST /api/v1/me/workspace`
      (`backend/src/app/api/me.py`, three `WORKSPACE_SCOPE_DENIED` refusals, each cited at
      its code line: `:241`, the malformed `Workspace-Id` header (`UUID(workspace_id)` at
      `:238`, raised at `:240-241`); `:251`, the membership check of the workspace entered
      (`if` at `:249`); `:260`, the membership check of the workspace left (`if` at `:258`) —
      the last two being `00` FR-396 and FR-397's membership check; not the decorator at
      `:215`; **no permission needed**, per the 11:08:22 entry); and, as Task 5
      adds each, **both new handler-guarded routes** — `POST /api/v1/environments/{env}/deployments`
      and `POST /api/v1/environments/{env}/deployment-requests` — each at the line of its
      handler's `require_permission(` (RL-1301 B.2: `deployment:promote` with the Environment as
      the resource, so neither carries `PERMISSION_ATTRIBUTE`; RL-1301 audit advisory A4);
    - **(f) siblings:** every other test iterating `app.routes` the same way is fixed in the
      same task. At the tree above `git grep -n 'app.routes' -- backend/tests` names only
      `test_api_authorisation_sweep.py:189`; the executor re-runs it and fixes each hit;
    - **(g) all routes accounted for:** each of the operations is guarded by a declared
      permission, by a named allow-list entry, or is in `OPEN_BY_DESIGN` /
      `NO_PERMISSION_REQUIRED` (`:28`, `:43`), and the three sets plus the guarded set
      partition the operation count exactly.
13. **`deployment_requests` joins the guarded set, evidence-only** — the approval guard
    itself is **Slice 2a's** (PL-1303, slice SL-1302; the split below). This item is RL-1301 A.4
    sub-item 9's Slice 2 half, read at head `3de69560643b2abc8d20afc923416a4ef66104a1` (the
    evidence-based trigger; still under audit by auditor-close1255): the creating migration
    installs Slice 2a's trigger function on the new table with the arguments
    `('deployment', <its slug column>)` and **no `'flag'` argument**, so the decision flag
    never satisfies it, and declares the table's `status_vocabulary`. The composed ref is
    `deployment:<environment slug>@<n>`, the reference form of **Decided in this plan**.
    Each red first:
    - Slice 2a's `pg_trigger` presence test (it connects to `test_database_url()` directly)
      names `deployment_requests` too, and fails with this revision's trigger removed;
    - **the deployment-request plant:** a direct `approved` write on `deployment_requests`
      with no matching approved `approval_requests` row, by ORM, Core and raw SQL, is
      refused; and so is the **forgery**, `set_config('app.approval_decision', 'on', true)`
      followed by that write;
    - an approved write whose only approved request names **another version** of the same
      slug (another request into the same Environment), another workspace's ref, or a
      request still in `review`, is refused;
    - **the ref pin:** Slice 2a's pin test gains `deployment_requests`: the trigger's
      composed ref equals `str(ArtifactRef(type="deployment", slug=…, version=…))`;
    - **positive control:** a deployment request approved through `decide` and the new
      deployment branch of `_carry_to_the_artifact` reaches `approved`, read back in the
      database. `deployment_requests` takes no allowance.

*(PL-1392, C1.)* Items 14–16 are the three acceptance items the 10:10:46 entry accepts, each
red first. They are checked by one new test module,
`backend/tests/test_deployment_route_types.py`, over the **Route table** (under Scope). In it,
**"published shape"** means a class name that is a value in `GENERATED_SHAPES`
(`scripts/generate-contracts.py:38`), so that
`docs/contracts/schemas/generated/<its slug>.schema.json` exists. The test reads `app.openapi()`
live, and `uv run python scripts/generate-contracts.py --check` (Acceptance 2) holds the
committed `docs/contracts/openapi/generated.json` to it. In `generated.json` every `$ref` is
an internal `#/components/schemas/<Name>` reference (measured at the tree above: no `$ref` names
a file), so "a `$ref` into `docs/contracts/schemas/generated/`" is tested as "a `$ref` to a
component whose name is a published shape".

14. **Every request body of the 7 new routes is a `model-schema` type — AST and OpenAPI.**
    - **The route set is pinned:** the `(method, path)` operations under `/api/v1/environments`
      in `app.openapi()["paths"]` equal the 7 rows of the Route table, exactly. The test
      fails naming any extra or missing operation, so a route cannot be added unchecked.
    - **AST:** the test parses `backend/src/app/api/environments.py` and
      `backend/src/app/api/deployments.py` with `ast`. For each of the 4 body-taking handlers,
      the `body` parameter's annotation is a bare name that the module imports in an
      `ImportFrom` whose module is `model_schema` or starts with `model_schema.`, and that
      name is the request type the Route table names. It is never `dict[...]`, `Any`, or a
      class the backend module defines. The 3 no-body handlers (`GET /api/v1/environments`,
      `POST /api/v1/environments/{slug}/retire`, `GET /api/v1/environments/{env}/deployments`)
      take no `body` parameter.
    - **OpenAPI:** for each body-taking operation,
      `requestBody.content["application/json"].schema` is exactly
      `{"$ref": "#/components/schemas/<Name>"}`, where `<Name>` is the table's request type and
      a published shape. Each no-body operation has no `requestBody`.
    - **Red first, on broken input, each quoted with the predicted cause:** with one handler's
      body re-annotated `dict[str, Any]` (the form `backend/src/app/api/sub_graphs.py:46` uses
      today), the AST assert **and** the OpenAPI assert both fail naming that route (the
      OpenAPI body becomes an object with `additionalProperties: true`); with the body class
      defined in the API module as a local `BaseModel` subclass, the AST assert fails naming
      it, and the OpenAPI assert fails because the name is not a published shape. Restore.
15. **Every 2xx of the 7 new routes is a `$ref` to a published shape — never `{}` and never an
    open object.** For each operation, every 2xx response's
    `content["application/json"].schema` is exactly `{"$ref": "#/components/schemas/<Name>"}`
    with `<Name>` the table's 2xx type and a published shape. For the 2 list routes it is
    `{"$ref": "#/components/schemas/Page_<Name>_"}`, and that component's
    `properties.items.items` is `{"$ref": "#/components/schemas/<Name>"}` with `<Name>` a
    published shape. `Page` is the backend's cursor envelope
    (`backend/src/app/api/pagination.py:48`, `extra="forbid"`, declared properties), which the
    12 typed `Page_*_` components at the tree above use (13 exist; the thirteenth,
    `Page_dict_str__Any__`, has open-object items and is exactly what item 15 refuses). It is not an open object, and it
    is not hand-written per shape. FD-1335's two forms are each refused by name: form 1, a
    schema equal to `{}`; form 2, an `object` with no `properties`. **Red first, on broken
    input:** with one handler's return annotation removed, the test fails naming the route
    and form 1; with it set to `dict[str, Any]`, the test fails naming form 2; with a list
    route returning `Page[dict[str, Any]]` (the `Page_dict_str__Any__` component that
    `GET /api/v1/approval-requests` uses today), the items assert fails. Restore.
16. **S2's deltas on the 2 changed existing routes are typed the same way** (the 10:10:46
    entry: "the method deltas on Withdraw and POST /approval-requests' deployment branch,
    typed the same way"). At the tree above both bodies are classes the backend defines
    (`Withdraw`, `backend/src/app/api/approvals.py:90`; `SubmitApproval`, `:75`), not
    `model-schema` types, and both 2xx are open objects (`additionalProperties: true`):
    FD-1335's form 2, two of the 12 routes of its Part B. After this slice, as the
    **Route table**'s last two rows give:
    - each body is a `model-schema` type, **moved, not duplicated**: `git grep -n -E '^class (Withdraw|SubmitApproval)\b' -- backend/src`
      prints nothing, and the AST and OpenAPI asserts of item 14 pass on both handlers;
    - **each 2xx is left as it is: DP-S2-6 is decided (c)** *(2026-10-01, by the maintainer's entry headed `2026-10-01 10:32:26 BST — #1062 DP-S2-6: option (c) ACCEPTED with three conditions; it narrows my item (3) for the 2 CHANGED routes' 2xx only; the three-shape disagreement becomes its own FD` (`~/gi-pricing-plan.local/channel/to-lead.md`))*.
      Both 2xx stay open objects, keep their place in FD-1335 Part B (with the marker
      `pending FD-1335 part B` if Part A's guard has merged), and are owned by **FD 9752
      (working id)**, which names both routes. Acceptance 18 pins that S2 does not widen
      them. For these two routes' 2xx only, this supersedes item (3) of the maintainer's entry
      headed `2026-10-01 10:10:46 BST — S2 addendum (F-B2 confirmed): the three acceptance items accepted; need 3 text for the superseding PL`;
      the bodies half of item (3) stands.
    - **Red first:** before the change, the test is run over these two operations and fails
      naming `Withdraw` and `SubmitApproval` as unpublished.
    - **Why the 2xx half was a decision point, measured by reading the code at the tree above.**
      Both routes return `service.to_dict(row, [])` (`backend/src/app/api/approvals.py:156`
      submit, `:294` withdraw; `to_dict` at `backend/src/app/platform/approvals.py:648-673`).
      *(Corrected 2026-10-03 before mint: this read `service.to_dict(row, decisions)`, which
      is `decide`'s call, `:270`, not these two routes'.)* That output carries `environment`
      (`:654`) and has no `workspace_id`. `ApprovalRequest`
      (`packages/model-schema/src/model_schema/approvals.py:275`) is `extra="forbid"`, has no
      `environment` field, and requires `workspace_id`. So declaring `ApprovalRequest` as the
      2xx would make outbound validation fail on every call, or, declared without validation,
      would publish a shape the route does not emit. Publishing `ApprovalRequest` under slug
      `approval-request` would also make it two-sided against the hand-authored
      `docs/contracts/schemas/approval-request.schema.json`, which requires `evidence_bundle`
      and `checklist`. Neither the model nor the API carries those (RL-1301 A.2 keeps evidence
      off `ApprovalRequestRow`). That is a three-way spec/code disagreement (`06` §4.3, the
      model, the API) under `CLAUDE.md` §0. It is the decision-maker's to resolve, not this
      plan's and not the executor's. The same `to_dict` serves `decide` and
      `GET /api/v1/approval-requests/{request_id}`, which are FD-1335 Part B's (carrier
      WK-1178).
    - **FD-1335's list.** All four approval-request routes that share `to_dict` keep their
      2xx in Part B: `decide` and `GET /api/v1/approval-requests/{request_id}` because they are
      not this slice's deltas, and the two changed routes by DP-S2-6 (c), with FD 9752
      (working id) as the owner of their 2xx. This slice removes nothing from Part B's
      temporary exclusion list.
17. **F-B1: the other callers stay read-only, and the bundle functions keep their shape**
    *(PL-1392, C3; second check replaced by C16, auditor-1062 F2)*. Two checks, each quoted
    with its output in the ledger:
    - `git diff --stat origin/main...HEAD -- backend/src/app/api/models.py backend/src/app/worker/scoring_handlers.py backend/src/app/worker/trace_handlers.py`
      prints nothing;
    - ~~a `git diff -U0 … | grep` over the `def` lines~~ *(struck 2026-10-01: blind to an added
      parameter, because both signatures span several lines, `score.py:163-170` and
      `:230-237`)*. Instead, this script, run from the worktree root, compares each
      function's `args` and `returns` nodes at `origin/main` and at `HEAD`, and prints
      nothing when they are equal (measured: nothing, rc 0, at the tree above against
      itself):

      ```python
      import ast
      import subprocess

      NAMES = ("_fetch_bundle", "_compiled_for")


      def signatures(ref: str) -> dict[str, tuple[str, str]]:
          src = subprocess.run(
              ["git", "show", f"{ref}:backend/src/app/api/score.py"],
              capture_output=True, text=True, check=True,
          ).stdout
          tree = ast.parse(src)
          return {
              n.name: (ast.dump(n.args), ast.dump(n.returns) if n.returns else "")
              for n in ast.walk(tree)
              if isinstance(n, ast.AsyncFunctionDef) and n.name in NAMES
          }


      base, head = signatures("origin/main"), signatures("HEAD")
      assert set(base) == set(NAMES), f"not found at origin/main: {set(NAMES) - set(base)}"
      for name in NAMES:
          if base[name] != head.get(name):
              print(f"{name}: signature or return annotation changed")
      ```

      **Red on broken input:** with a dummy keyword parameter (`unused: int = 0`) added to
      `_fetch_bundle` in a scratch commit, the script prints
      `_fetch_bundle: signature or return annotation changed`; the commit is dropped. Quoted.
    The governance gate's call (`backend/src/app/api/models.py:1215`, which uses
    `_fetch_bundle` and never `_compiled_for`, `:1212-1214`) and the two workers'
    `_compiled_for` calls (`backend/src/app/worker/scoring_handlers.py:85` import, `:208`
    call; `backend/src/app/worker/trace_handlers.py:30` import, `:82` call) keep passing
    their existing tests in the full gate (Acceptance 10). Acceptance 6 and 7 carry the
    behaviour's reds.
18. **S2 does not widen the untyped surface of the 2 changed routes** *(PL-1392, C13; the
    lead's message of 2026-10-01 10:33 BST, on DP-S2-6 (c))*. Their 2xx stay open objects
    (owner FD 9752, working id), so nothing in the OpenAPI holds their content. A
    characterisation test in `backend/tests/test_deployment_route_types.py` does instead.
    - **What it pins:** for `POST /api/v1/approval-requests` (201) and
      `POST /api/v1/approval-requests/{request_id}/withdraw` (200), the **exact** set of
      top-level response keys, compared with `==` (not a subset), and `decisions == []`. Any
      undeclared add, drop or rename is red, naming the key.
    - **The key set at the tree above**, read from `service.to_dict`
      (`backend/src/app/platform/approvals.py:648-673`), which both routes call as
      `service.to_dict(row, [])` (`backend/src/app/api/approvals.py:156` submit, `:294`
      withdraw): `id`, `artifact_ref`, `artifact_type`, `environment`, `submitted_by`,
      `submitted_at`, `change_summary`, `status`, `approvers_required`,
      `approvers_recorded`, `decisions`, `withdrawn_reason` (12 keys). Because both routes
      pass `[]`, `decisions` is always `[]` on them, so no `decisions` element key set is
      pinned here. *(Corrected 2026-10-03 before mint: this item also pinned a 4-key element
      set and a non-empty `decisions` on withdraw, which neither route can emit.)*
    - **Keys this slice adds: none.** Neither Task 5 nor Task 6 changes `to_dict` or what the
      two routes return. The test's expected sets are therefore the sets above, before and
      after. If the executor finds it must add, drop or rename a key, it **stops and
      reports**: the key goes into this list with its type by a dated delta first, never
      into the test alone.
    - **Before and after:** the test is written and run green against the tree before
      Tasks 5 and 6 change either route (it characterises today's output), and it stays green,
      unchanged, after them. Exercised for the deployment branch of `POST
      /api/v1/approval-requests` (a Deployment Request in `review`) and for a `rating_version`
      ref, and for the withdraw route; on every case `decisions == []`.
    - **Red first, on broken input:** with `to_dict` patched to add a key (`"extra": 1`), to
      drop `withdrawn_reason`, and to rename `environment` to `env`, each run is red naming
      the key and the route. Restore. Quoted in the ledger.
19. **A compile of a non-draft Rating Version is handled as RL-1379 rules — BLOCKING: S2 does
    not merge without it** *(PL-1392, C14; FD-1393; the maintainer's entry headed
    `2026-10-01 10:34:45 BST — FD 9754 (#1064, a non-draft rating version can be recompiled and its bundle rewritten): MEDIUM, owner WK-674 S2, and **S2 does not merge without the guard**; the option choice goes to a DM now`)*. `compile_rating_version`
    (`backend/src/app/platform/rating_versions.py:395-542`) and its route
    (`POST /api/v1/rating-versions/{rating_version_id}/compile`, `backend/src/app/api/models.py:1233`,
    handler `:1237`) read no status, so an approved version's bundle and `content_hash` can be
    rewritten after approval. The first Deployment, which this slice creates, is the trigger
    for real exposure. **The behaviour is DP-S2-7's, as RL-1379 rules it**; this
    item is completed by a dated delta once the ruling lands, naming its cases. Whatever it
    rules, each case is **red first** in `backend/tests/test_rating_versions.py` (or the file
    the ruling names), run, not reasoned: the audit's red was reasoned from code. Under
    option (1), for example, a compile of a `review`, `approved` or `archived` version is
    refused, and the version's `bundle` metadata is unchanged after the refusal.

## Global Constraints

- **Money is integer minor units, or `Decimal` in the rating path** (`CLAUDE.md` §7). This
  slice adds no money field.
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2):
  `Environment`, `Deployment` and the skip record are declared once, there.
- **The Audit Event is written in the same transaction as the change** (`06` FR-368;
  `audit.record` joins the caller's transaction, `backend/src/app/platform/audit.py:52-70`).
- **A Deployment row is never updated in place** (`06` FR-382 needs what was live over a
  date range; `PL-1237:521-523`). A later Deployment supersedes an earlier one by being later.
- **The skip reason is always required when a skip is used, and is not configurable** (RL-1296, item 3).
- **The skip field, `06` §4.2 and the regenerated contract land in one commit** (RL-1296, item 5), never the §4.2 text before the model.
- **Governance imports nothing from the rating module** (`00` DEP-1, `00:470`; DEP-537
  `:472-477`). Deployment facts reach the approval submission through a caller-supplied
  resolver, as `ArtifactResolver` (`backend/src/app/platform/approvals.py:143-159`) and
  `EvidenceAuthorResolver` (`:316-327`) already do.
- **The migration chain has exactly one head** (`07` FR-417).
- **`NO_LIVE_RATING_VERSION` is permanent** (RL-880; `backend/src/app/api/score.py:138-160`):
  the slice narrows its trigger to "no Deployment in this environment, or no environment",
  and does not delete it.
- **Build ahead of the phase is forbidden** (`CLAUDE.md` §9): no Monitor creation (`05`
  FR-310), no notification (FR-272's second limb), no switch (Slice 5), no routing or shadow
  (Slice 6). The deploy transaction leaves the boundary where WK-687's Job submission can be
  added (FR-413's outbox rule; `PL-1237:538-541`).
- **FD 9881 (FR-447) is Slice 3's, not this slice's** — the maintainer's entry headed
  `2026-09-30 10:56:21 BST — #942 (ruling 7 of 7): auditor approved; D3 = RL; dm-effort-high kept through the fix rounds; WK-674 S2 plan`,
  last bullet.
- **RL-1263 concurrency.** This slice runs beside WK-690 Slice 1 (lane B), each holding a
  gate slot. The maintainer's entry headed
  `2026-09-30 10:05:40 BST — ETA read (maintainer "check ETA"); two dispatch reminders`
  sets two conditions: **if this slice's diff touches `uv.lock` or any `pyproject.toml`, it
  serialises behind WK-690 Slice 1's dependency change**, and the dispatch record states the
  `uv.lock` check; and **the first overlap of this slice's gate with WK-690 Slice 1's
  triggers the three-pair contention measurement**, run alone first. *(PL-1392: WK-690
  Slice 1 is `SL-1271`, `status: closed` at the tree above, so these two conditions no longer
  bind against it. The dispatch record applies the same two checks to whichever slice holds
  lane B at dispatch.)*
- **Never concurrent with `SL-1367`** *(PL-1392, C8; F-B4)*. `PL-1364` (FD-1335 Part A)
  edits the route decorators of `backend/src/app/api/score.py`, and Task 6 edits the same
  file. `score.py` is shared and not registry-exempt, so the two serialise (RL-1263). The
  dispatch records of both slices state it and name the order.
- **Serial with the FD-1356 fix, this slice first** *(PL-1392, C7; order (b))*. Both edit
  `backend/src/app/platform/approvals.py` and `_carry_to_the_artifact`
  (`backend/src/app/api/approvals.py:488`), so they never run concurrently. The FD-1356 fix
  plan's activation need is "WK-674 S2 merged"; this slice has no need on that fix.

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.10 | FR-267 | Whole: Deployment binds an `approved` RV to an Environment; who, when, why, bundle hash; Deployer only; `prod` needs the complete approval record |
| `03` §3.10 | FR-272 | The Audit Event limb for **deploy**. Rollback's is Slice 5's; routing and shadow configuration's are Slice 6's (`PL-1237:293`). The notification limb is WK-688's (`RL-1252`) |
| `03` §9 | NFR-498 | The **deploy** limb, riding with FR-272 (`PL-1237:298`) |
| `07` §3.5 | FR-428 | Whole: Environment as a first-class object, seeded `dev → uat → prod`, more configurable, create / rename / retire |
| `07` §3.5 | FR-429 | Whole: both checks on one predicate, with the skip's home as RL-1296 gives it |
| `06` §3.1 | FR-347 | The negative test only (`PL-1237:529-531`); the rest is WK-676's |
| `06` §3.2 | FR-357 | The deployment state it needs, and the server-derived liveness of Task 6; the rest is WK-677's |

**Carried obligations placed here** (`PL-1237:362-444`, each re-read at the tree above):
RL-880 and register F43 limb L1 (Task 6); RL-886 (Task 2); RL-888 and RL-916 (Task 6,
DP-S2-1); `CR-1212` item 4 (Task 1 and Task 2, DP-S2-3); OQ-1234 as RL-1296
decides it (Tasks 1, 2 and 5); **G3** of the ruling of #938 (working id 9851, "WK-674
Slice 2: G3", its §What it obliges) — set on this slice by the maintainer's entry headed
`2026-09-30 10:02:08 BST — DECISION: section-disjoint spec edits under RL-1263; #938 must-checks`,
Must-check A ("Name one owner"); **`STALE_OWNER`** of the ruling of RL-1305 (Acceptance 8).

**Not in this slice**, each with where it goes: FR-268 and FR-269 (and rollback's audit limb)
→ Slice 5. FR-270 and FR-271 → Slice 6. FR-430, FR-431, register F48 and F54 → Slice 3.
FR-453 / FR-272's notification → WK-688. FR-368's general obligation → WK-679. FR-382 and
FR-384 read what this slice writes, and are not built. The Environment's `settings` object
(`07:245-259`, the `settings` key) → Slice 3, gated by `OQ-1235`; this slice's `Environment`
shape omits it, with a dated `07` §4.2 note saying so (Task 1).

**One map-plan deviation, dated 2026-09-30, stated rather than folded in.** `PL-1237` Task 2 says the slice
"declares the `Environment` data contract alongside" the new `03` Deployment contract. At the
tree above `07` §4.2 **already declares `Environment`** (`07:245-259`). Declaring it a
second time in `03` would be a shape defined twice (`CLAUDE.md` §2), so this slice declares
only `Deployment` in `03` and aligns `07` §4.2 by a dated note.
**Recorded as a dated delta to the map plan, in this leaf plan** *(2026-09-30)*. `PL-1237` is
`active` and frozen, so it takes only `status:`, `superseded_by:` and `corrected_by:`
(`document-ids.md` §1.5); a delta note here is the planner's form, as `PL-1239` recorded its
own map-plan deviation. No separate map-plan record is filed. **Agreed** by the maintainer's
entry headed `2026-09-30 11:12:45 BST — #973 (WK-674 S2 plan): (a) agreed; (b) its own FD, plus a class sweep`,
item (a).

### Route table — the 7 new routes and the 2 changed ones *(PL-1392, C1)*

The 7 new routes are F-B2's list (the audit addendum): Task 4 owns rows 1–4, Task 5 rows 5–7.
Every request type and 2xx type is a `model-schema` class registered in `GENERATED_SHAPES`
(`scripts/generate-contracts.py:38`) under the slug given, so its schema is published at
`docs/contracts/schemas/generated/<slug>.schema.json`. **Verified at the tree above:**
`ArtifactRef` (`packages/model-schema/src/model_schema/refs.py`, slug `artifact-ref`, already
published), `Slug` (`refs.py:41`), `ApprovalRequest` (`approvals.py:275`, not yet published)
and `Page` (`backend/src/app/api/pagination.py:48`, the cursor envelope, not a `model-schema`
class and not needed there: see Acceptance 15) exist. `Environment`, `Deployment`,
`DeploymentRequest` and `PromotionSkip` **do not exist yet** (premise u): Task 2 adds them. The
other new names below are request shapes this slice adds. Like every name the executor adds,
each is named once here and used as named.

| # | Method and path | Request type (module, slug) | 2xx type | Task |
|---|---|---|---|---|
| 1 | `GET /api/v1/environments` | none (no body) | 200 `Page[Environment]` (items: `Environment`, `deployments.py`, slug `environment`) | 4 |
| 2 | `POST /api/v1/environments` | `EnvironmentCreate` (`deployments.py`, slug `environment-create`): `slug: Slug`, `name`, `description`, `promotion_order`, `requires_prior_environment` | 201 `Environment` | 4 |
| 3 | `PATCH /api/v1/environments/{slug}` | `EnvironmentUpdate` (`deployments.py`, slug `environment-update`): `name` and `description` only, `extra="forbid"`, so a body naming `slug` is refused with 422 naming the field (Acceptance 4, A3) | 200 `Environment` | 4 |
| 4 | `POST /api/v1/environments/{slug}/retire` | none (no body) | 200 `Environment` (with `retired_at` set) | 4 |
| 5 | `POST /api/v1/environments/{env}/deployment-requests` | `DeploymentRequestCreate` (`deployments.py`, slug `deployment-request-create`): `rating_version_ref: ArtifactRef`, `change_summary`, `skip: PromotionSkip \| None` (`PromotionSkip` in `approvals.py`, reached through the body's `$defs`) | 201 `DeploymentRequest` (`deployments.py`, slug `deployment-request`) | 5 |
| 6 | `POST /api/v1/environments/{env}/deployments` | `DeploymentCreate` (`deployments.py`, slug `deployment-create`): `rating_version_ref: ArtifactRef`, `reason`, `deployment_request_ref: ArtifactRef \| None`, `extra="forbid"` (no `skip`, RL-1301 A.5) | 201 `Deployment` (`deployments.py`, slug `deployment`) | 5 |
| 7 | `GET /api/v1/environments/{env}/deployments` | none (no body) | 200 `Page[Deployment]` | 5 |
| 8 *(changed)* | `POST /api/v1/approval-requests/{request_id}/withdraw` | **today** `Withdraw` (`backend/src/app/api/approvals.py:90`, backend class; `reason`, `artifact_is_live`). **After:** `ApprovalWithdrawal` (`approvals.py`, slug `approval-withdrawal`): `reason` only, `min_length=1`, `extra="forbid"` | **today** 200 open object (FD-1335 form 2). **After:** unchanged (DP-S2-6 (c)); owner FD 9752 (working id), in FD-1335 Part B; pinned by Acceptance 18 | 6 |
| 9 *(changed)* | `POST /api/v1/approval-requests` (its deployment branch, Task 5 step 6) | **today** `SubmitApproval` (`backend/src/app/api/approvals.py:75`, backend class). **After:** `ApprovalSubmission` (`approvals.py`, slug `approval-submission`), the same three fields unchanged | **today** 201 open object (FD-1335 form 2). **After:** unchanged, as row 8 | 5 |

Status codes follow the neighbouring routes (`201` for a create). The 2xx of rows 8 and 9 stay
untyped by DP-S2-6 (c): no shape that exists today matches what those routes emit (Acceptance
16), and FD 9752 (working id) owns them. Acceptance 18 pins their exact key sets.

### Premises re-derived at the tree above

| # | Premise | Evidence | Status |
|---|---|---|---|
| a | No Environment or Deployment object exists | `git grep -n 'class .*Environment' -- backend/src packages` prints only `backend/src/app/config.py:32` (the runtime-mode enum); `git grep -n -i live_deployments -- packages backend/src docs/specs` prints only `docs/specs/07-platform.md:253` | greenfield |
| b | `DEFAULT_POLICY` has no `deployment` entry; the floor has one | `packages/model-schema/src/model_schema/approvals.py:107` (`"deployment": ("rating_version_approval", "uat_deployment")`); `DEFAULT_POLICY` `:202-261` holds `validation_rule`, `custom_objective`, `custom_metric`, `model`, `peril_structure`, `rating_version` | reproduces RL-886 |
| c | `ApprovalPolicyEntry` is keyed per artifact type and environment, with fallback | `approvals.py:111-122` (`environment: str \| None`, `:119-121`); `entry_for` `:146-162` returns the exact match, then the `environment is None` entry; the only validator is `_separation_of_duties_is_not_configurable` (`:137-144`) | reproduces |
| d | Nothing checks `uat_deployment` | `git grep -n -i uat_deployment -- backend packages` prints only `approvals.py:107` | reproduces |
| e | Neither Slice 2 permission is checked | `git grep -n -E "(Perm\|Permission)\.(DEPLOYMENT_PROMOTE\|ADMIN_MANAGE_ENVIRONMENTS)\b" -- backend/src` exits 1. Declared at `permissions.py:54` and `:69`; `deployer` holds `DEPLOYMENT_PROMOTE` (`:140`), `admin` holds `ADMIN_MANAGE_ENVIRONMENTS` (`:146`) | reproduces (the ruling of RL-1305's evidence 5) |
| f | A grant's scope is one resource, or the workspace | `RoleAssignmentRow.scope_type` / `scope_id` (`backend/src/app/db/models.py:590-640`, constraint `scope_id_iff_scoped` `:631-634`); `rbac._covers` (`backend/src/app/platform/rbac.py:205-217`): a workspace-wide assignment covers every resource; `ScopeType` (`permissions.py:91`) has no `environment` member | the base for DP-S2-3 |
| g | `sub_graph` is a valid reference type, and nothing names a deployment | `ARTIFACT_TYPES` (`packages/model-schema/src/model_schema/refs.py:21-31`) includes `sub_graph` and `rating_version`, and has **no** `deployment`; `REF_PATTERN` is built from it (`:51-53`) | the base for G3 and DP-S2-2 |
| h | An approval request holds no evidence; the owning module's row does | `ApprovalRequestRow` (`models.py:643-688`) has `artifact_ref`, `artifact_type`, `environment` and no evidence column; `rating_versions.submit_for_review` writes `row.evidence` then calls `approvals.submit` (`backend/src/app/platform/rating_versions.py:250-309`); `submit` (`platform/approvals.py:225-313`) checks no evidence, and `EVIDENCE_INCOMPLETE` is raised by owning modules (raised at `rating_versions.py:635`, `:645`, `:651` through the helper `_evidence_incomplete`, `:658-661`) | the base for DP-S2-2 |
| i | `DEPLOY_REQUIRES_APPROVAL` is not registered; `PROMOTION_ORDER_VIOLATION` is | `git grep -n DEPLOY_REQUIRES_APPROVAL -- backend` exits 1; `PROMOTION_ORDER_VIOLATION` at `backend/src/app/errors.py:70`, raised nowhere; `03`'s catalogue names `DEPLOY_REQUIRES_APPROVAL` (`03:817`, in the catalogue `03:810-845`) and `07`'s names `PROMOTION_ORDER_VIOLATION` (`07:344`) *(PL-1392: PL-1306 cited `03:778` for the second, which was wrong at its own tree)* | Task 5 registers the first |
| j | `/score` resolves only an explicit ref | `backend/src/app/api/score.py:138-160` (`_required_ref`, 409 `NO_LIVE_RATING_VERSION`); the ref reaches `resolve_rating_version_ref` in `_fetch_bundle` (`:192`) | reproduces RL-880 |
| k | A trace's environment is a plain string | `ScoringTraceRow` (`models.py:2205`, table `scoring_traces` `:2251`, `environment` `:2264`; docstring `:2216-2217`: "a plain string, not a Deployment FK … Deployment does not exist before WK-674"); the value is `Caller.environment` (`backend/src/app/api/deps.py:66-69`, RL-916), `None` for a bearer caller | reproduces RL-888 / RL-916 |
| l | Withdrawal liveness is supplied by the HTTP client | `Withdraw.artifact_is_live` (`backend/src/app/api/approvals.py:90-98`), passed through at `:288`; `service.withdraw` raises at `platform/approvals.py:486-494` | **a defect Slice 2 closes** (Task 6): a client can assert "not live" |
| m | No environments or deployments router | `ls backend/src/app/api/` has neither; routers are registered at `backend/src/app/main.py:126-149`, `API_PREFIX = "/api/v1"` (`:61`); `requires` at `backend/src/app/api/authz.py:54` | greenfield |
| n | The OpenAPI stub has the deploy path, no `/environments` path; the generated document has 141 operations *(PL-1392)* | `docs/contracts/openapi/gi-pricing.yaml:284-293`; `grep -c '"/api/v1/environments' docs/contracts/openapi/generated.json` prints 0; the operation count is 141 over 120 paths, by the predicate quoted verbatim in Acceptance 12 (a) | reproduces |
| o | The Alembic head *(PL-1392)* | `2f598e89d12c` (`backend/migrations/versions/2f598e89d12c_sub_graph_versions.py`), the one revision of the 50 under `backend/migrations/versions/` that no `down_revision` names (measured by reading each file's `revision` and `down_revision`; PL-1306's `d7e2a9b5c418` is no longer the head) | reproduces |
| p | `03` §4 ends at §4.11 *(PL-1392)* | `grep -n -E '^### 4\.[0-9]+' docs/specs/03-rating-engine.md` prints §4.1 (`:231`) … §4.10 `ScoreComparison` (`:703`), §4.11 `SubGraph` (`:743`); no Deployment contract | the new contract is **§4.12** (C4) |
| q | `06` §4.1 has the `Check owner` column, with `WK-674` on both Slice 2 permissions *(PL-1392; PL-1306 read 0)* | `grep -c 'Check owner' docs/specs/06-governance.md` prints 2 (`06:265`, the note; `06:269`, the header row); the predicate of Acceptance 8 prints 2 (`06:283`, `06:294`) | Acceptance 8 is Branch A |
| r | Slice 1 is closed | `docs/roadmap.md`, `#### SL-1255`, `status: closed` (#933, #934) | the dependency holds |
| s | Slice 2a and `SL-1300` are closed *(PL-1392)* | `docs/roadmap.md`, `#### SL-1302`, closed 2026-09-30 at #997's merge; `#### SL-1300`, `status: closed` | activation need 3 holds |
| t | `_fetch_bundle` and `_compiled_for` have other callers *(PL-1392, F-B1)* | `git grep -n -E '_fetch_bundle\|_compiled_for' -- backend/src`: `backend/src/app/api/models.py:1215` (the governance gate calls `_fetch_bundle`); `backend/src/app/worker/scoring_handlers.py:85`, `:208` and `backend/src/app/worker/trace_handlers.py:30`, `:82` (`_compiled_for`); in `score.py`, `_fetch_bundle` `:163`, `_compiled_for` `:230`, called at `:326` and `:394` | read-only to this slice (Acceptance 17) |
| u | No route-type shape for this slice exists, and the 2 changed routes are untyped *(PL-1392)* | `git grep -n -E '^class (Environment\|Deployment\|DeploymentRequest\|PromotionSkip)\b' -- packages/model-schema/src` exits 1; `Withdraw` (`backend/src/app/api/approvals.py:90`) and `SubmitApproval` (`:75`) are backend classes; in `generated.json` both routes' 2xx are objects with `additionalProperties: true`; `ApprovalRequest` exists (`packages/model-schema/src/model_schema/approvals.py:275`) and is not in `GENERATED_SHAPES` | the base for Acceptance 14–16 |

The executor re-reads each at its own tree and stops on any that no longer holds
([`README.md`](README.md) convention 4).

### Write set, for the RL-1263 dispatch check

Registry-exempt paths are RL-1263's list as corrected by the maintainer's dated line of
2026-09-29 23:20:11 BST (`RL-1263`, "Registry list, as corrected"). Every other path is
named with the slices that may also touch it.

| Path | What this slice does | Also touched by | RL-1263 |
|---|---|---|---|
| `uv.lock`, any `pyproject.toml` | **nothing** | WK-690 S1 (the sympy pin) | not shared; the dispatch record states `git diff --stat origin/main...HEAD -- uv.lock '*pyproject.toml'` prints nothing |
| `docs/specs/03-rating-engine.md` §3.10 | dated notes under FR-267/FR-272 only | none found | section-disjoint from WK-690 S1 (§3.5 FR-244 only) |
| `docs/specs/03-rating-engine.md` §4 | **a new subsection, §4.12** (`Deployment`) after §4.11 `SubGraph` (`03:743`) *(PL-1392, C4)* | WK-1250 later slices, WK-674 S6 | §4.11 is taken (WK-1250 S1 has merged it), so this slice's number is fixed as **§4.12** by the 10:10:32 entry. If another slice has taken §4.12 by this slice's merge, the executor **stops and reports**; it does not renumber on its own |
| `docs/specs/03-rating-engine.md` §5.1 | one row appended to the REST table (the deployment-history `GET`, `PL-1237:773-774`) | WK-1250 S1 (four rows), WK-1178 fix slice (**amends the error-code catalogue line**, `03:810-845`) | this slice **does not edit the catalogue lines** (`03:810-845`); a route-table append against a catalogue amendment is not the same definition, decided at dispatch against both diffs (the maintainer's entry headed `2026-09-30 10:24:00 BST — DATED CORRECTION to my 10:15:07 entry (the unpinned-step FD: "It covers the `coalesce(` path as well as `??`")`, last bullet). If the executor finds it must add a code to the catalogue, it stops and reports |
| `docs/specs/06-governance.md` §4.1, §4.2, and the §4.1 scope example | the skip field (§4.2), RL-886's note (§4.2), the environment scope (FR-345, RL-1301 B.4), `Check owner` cells (branch A) | RL-1305 (§4.1, D4), WK-690 S3 (a §4.1 row), WK-1250 S1 (§3.3 under its DP-1) | §4.1 **serialises with RL-1305** unless RL-1305 has merged (then branch A edits two cells of the merged table) |
| `docs/specs/07-platform.md` §4.2, §5.1 | a dated note on `Environment`; rename / retire rows appended | none found | not shared |
| `docs/contracts/schemas/*.json` (hand-authored) | none: RL-1301 A.2 keeps evidence off `ApprovalRequestRow`, so `approval-request.schema.json`'s `evidence_bundle` (`:25-35`) is not touched | none found | **not exempt**; serialises if touched by another slice |
| `packages/model-schema/src/model_schema/approvals.py` | the `deployment` `DEFAULT_POLICY` entry, the skip field and validator, the predicate | WK-673, WK-1250 (if its DP-1 is (a)) — named in RL-1263 item 4 | **serialises** with any in-flight slice editing `EVIDENCE_FLOOR`/`DEFAULT_POLICY` |
| `packages/model-schema/src/model_schema/permissions.py` | `ScopeType.ENVIRONMENT` (RL-1301 B.1) | WK-690 S3 (`custom_objective:author`) | an added enum member is an edit to an existing class: serialises unless the dispatch record shows no shared member |
| `packages/model-schema/src/model_schema/refs.py` | `"deployment"` in `ARTIFACT_TYPES` (RL-1301 A.1) | WK-1250 (`sub_graph` already present) | serialises if another slice edits the set |
| `packages/model-schema/src/model_schema/__init__.py`, `scripts/generate-contracts.py` | exports and slug-map entries for the new shapes | WK-1250 S1, WK-673 S4 (`PL-1278:178-179`) | not on the registry list; serialises unless the dispatch record names the path |
| `backend/src/app/errors.py` | `DEPLOY_REQUIRES_APPROVAL` registered in the rating set | WK-1178 fix slice (new codes, likely) | an added member of an existing frozenset: serialises unless the dispatch record shows the two diffs add different members only |
| `backend/src/app/db/models.py` | `EnvironmentRow`, `DeploymentRow` appended (exempt); **`ScoringTraceRow` gains a column** (an edit to an existing class) | WK-1250 S1 (appends) | the appends are exempt; the `ScoringTraceRow` edit serialises with any slice editing that class |
| `backend/src/app/main.py` | two router registrations | WK-1250 S1 | exempt (append only) |
| `backend/migrations/versions/` | one new revision | WK-1250 S1, WK-690 S1 (none planned) | exempt; re-point `down_revision` at the second merge |
| `backend/src/app/api/score.py` (`_required_ref` and the `score` handler; **not** `_fetch_bundle` or `_compiled_for`, whose signatures and return types do not change, Acceptance 17), `backend/src/app/platform/traces.py` | default-live resolution; the trace's Deployment reference *(PL-1392, C3)* | **`SL-1367`** (`PL-1364`, FD-1335 Part A: the route decorators), WK-1250, WK-673, WK-675 S7b (RL-1263 item 4 names `score.py`) | **serialises** with any in-flight slice editing `score.py`; **never concurrent with `SL-1367`**, and the dispatch records of both say so (C8) |
| `backend/src/app/api/models.py` (the governance gate's `_fetch_bundle` call, `:1215`), `backend/src/app/worker/scoring_handlers.py` (`:85`, `:208`), `backend/src/app/worker/trace_handlers.py` (`:30`, `:82`) | **nothing: read-only** *(PL-1392, C3, F-B1)* | — | not touched; Acceptance 17's `git diff --stat` prints nothing |
| `backend/src/app/api/service_accounts.py` (`:63`, `:180`, `:246`) | the Environment-slug check at creation and rotation (RL-1301 A.6) | WK-674 S3 (per-environment keys, register F54: the same lines) | an edit to existing functions: serialises with any in-flight slice editing them; S3 follows this slice anyway |
| `backend/src/app/platform/approvals.py` (`set_policy`, `:170-222`) | the existence check of RL-1301 A.6 (the guard's `decide` change is Slice 2a's) | any slice editing `set_policy` | an edit to an existing function: serialises unless the dispatch record shows no other in-flight slice edits it |
| Slice 2a's shared paths (`approvals.py` in `platform/` and `api/`, `models.py`, the migrations registry) | this slice follows Slice 2a in lane A | Slice 2a (PL-1303, closed), the FD-1356 fix | Slice 2a has closed. Against the FD-1356 fix: **this slice first, then the fix, never concurrently** (both edit `_carry_to_the_artifact` and `platform/approvals.py`), by order (b) of the 10:10:32 entry *(PL-1392, C7; PL-1306 had S2a → the fix → S2)* |
| `backend/src/app/api/approvals.py` (`Withdraw` and `SubmitApproval` moved out; `withdraw_request` and `submit_for_approval` typed) | server-derived liveness; both bodies become `model-schema` types; both 2xx unchanged, pinned by Acceptance 18 (DP-S2-6 (c)) *(PL-1392, C1)* | the FD-1335 Part B slice (carrier WK-1178: these two routes are 2 of its 12), the FD-1356 fix | an edit to existing functions: serialises with each. The two routes' 2xx stay on Part B's list (DP-S2-6 (c); owner FD 9752, working id) |
| `packages/model-schema/src/model_schema/deployments.py` (new), `approvals.py` (`PromotionSkip`, `ApprovalWithdrawal`, `ApprovalSubmission`), `scripts/generate-contracts.py` (`GENERATED_SHAPES`: the Route table's slugs) | the Route table's shapes *(PL-1392, C1)* | WK-1250, WK-673 S4 (`GENERATED_SHAPES` appends); **the FD-1357 fix (PL-1376; #1057)**, which also edits `packages/model-schema/src/model_schema/__init__.py`, `scripts/generate-contracts.py`, `backend/tests/test_contracts.py` and `03` §5.1 rows *(PL-1392, C15)* | appends to a dict: serialises unless the dispatch record shows different keys only. `approval-request` is not registered (DP-S2-6 (c)) |
| `backend/tests/test_contracts.py` (`ONE_SIDED_SLUGS`, `:69`) *(PL-1392, C15)* | one entry per new generated-only slug | the FD-1357 fix (PL-1376; #1057), PL 9788 (working id) and `PL-1364` (their guard lists), WK-1250 | an edit to an existing dict: serialises with each unless the dispatch record shows different keys only |
| `scripts/audit-docs.py` (`_CONTRACT_ARTIFACT_PATHS`, `:2620`), `tests/test_audit_docs_ids.py` (`:2117`, the `non_markdown` count) *(PL-1392, C18)* | one literal path per new generated schema; the count bumped | the FD-1357 fix (PL-1376; +2), any slice adding generated schemas, WK-1170 and WK-1169 slices (`audit-docs.py`) | **serialises** (RL-1263 `:89`): the count is one shared number and its bump is not append-only, so the second to merge re-bumps on the merged count and re-runs its gate |
| `.claude/skills/contract-schema/SKILL.md` (and, if apt, a pointer in `.claude/skills/docs-audit/SKILL.md`'s check 35 text) *(PL-1392, C18)* | **conditional:** the registration step and a refreshed `Verified` date, **only if this slice merges before the FD-1357 fix** | the FD-1357 fix (PL-1376), the same conditional step | whichever lands first writes it; the other skips it |
| `backend/src/app/platform/rating_versions.py` (`compile_rating_version`, `:395-542`), `backend/src/app/api/models.py` (the compile route, `:1233`, only if RL-1379 needs it) *(PL-1392, C14)* | the compile guard, as RL-1379 rules | any in-flight slice editing either function; the FD-1357 fix if it touches them | an edit to existing functions: serialises. `models.py:1215` (the governance gate) stays read-only (Acceptance 17) |
| `backend/tests/test_api_authorisation_sweep.py` (and any sibling Acceptance 12 (f) finds) | Task 0A: flattening, the count equality, the spec pin, the valid-body sweep, the named allow-list | none found | test-only; **no RL-1263 overlap with WK-690 S1 and no third slot** (the 11:01:50 entry) |
| the five modules' §5.1 REST tables (`01`, `02`, `03`, `06`, `07`) | **nothing in this slice**: Task 0A (c) moved out (the 11:17:35 entry); #977 (a) puts the column in a WK-1178 slice. **If that slice lands first**, this slice fills the column for its own new rows (`03` and `07` §5.1) | WK-1250 S1 (`03` §5.1 rows), WK-1178 fix slice (`03:810-845`), any slice appending §5.1 rows | **serialises** with each: a new column edits every existing row of the table |
| `backend/src/app/api/approvals.py` (`_carry_to_the_artifact`) | one call added, to the deployment module's `apply_approval_decision` (RL-1301 A.4) | any slice adding an approvable type | an edit to an existing function: serialises unless the dispatch record shows the two diffs add different calls only |
| `docs/contracts/schemas/common/artifact-ref.schema.json` | regenerated with `deployment` in the type list (RL-1301 A.1); if the guard shows it is hand-authored, edited to match | WK-1250 | **not exempt** if hand-authored (`RL-1263`, "Registry list, as corrected") |
| new: `backend/src/app/api/environments.py`, `backend/src/app/api/deployments.py`, `backend/src/app/platform/environments.py`, `backend/src/app/platform/deployments.py`, their tests | created | — | not shared |

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S2-1 | When a quote is scored with an **explicit** `rating_version_ref`, which Deployment does its sampled trace reference? `00`'s ER line makes every trace a child of a Deployment (`00:264`); RL-916 made the environment string reconcilable to "the Deployment that actually served the quote"; an explicit ref may name a version that is not live anywhere | (a) The environment's live Deployment if its Rating Version equals the ref, else null; (b) always null for an explicit ref; (c) refuse an explicit ref outside `local`, so every served quote has a Deployment | **(a).** It records the truth in both cases: a quote served by the live version is attributable to its Deployment, and a what-if quote against another version is not pretended to be. (c) breaks every caller that pins a version today (RL-880 made the explicit ref the only path until now). Pre-existing rows get null under every option: no Deployment existed to serve them | decision point | yes — Task 6 | **RL-1380 (#974), read at head `6bc51cf0` (*PL-1392*: PL-1306 read `849dce65`), the decision-maker at medium effort — (a)**: the live Deployment only if it serves exactly the ref's Rating Version (type, slug, version), else null; resolved once with the bundle and never re-read; the `environment` string unchanged, the link additive |
| DP-S2-2 | **What does a `deployment` approval request name, and where is its evidence pinned?** The policy and the floor are keyed `deployment` (premise b) and `submit` looks up `entry_for(artifact_ref.type, environment)` (`platform/approvals.py:259`), but no `ArtifactRef` can name a deployment (premise g), and an approval request holds no evidence (premise h). RL-1296 (item 3) puts the skip reason in "the predecessor-deployment evidence item of that request", which therefore has no home yet | (a) Add `deployment` to `ARTIFACT_TYPES`; the rating module creates a **deployment request** row (Rating Version, target environment, the pinned evidence: the RV's approval request id, and the `uat` Deployment id **or** the skip record), and submits it through the unchanged `approvals.submit`, as every other owning module does; the Deployment row that the route writes references the approved request; (b) the request names the **Rating Version** ref with `environment="prod"`, and `approvals.submit` gains a policy-key override (`"deployment"`); evidence is held in a new table keyed by request id; (c) give `ApprovalRequestRow` an evidence column (the `06` §4.3 `evidence_bundle` made real) for every artifact type | **(a).** It is the existing pattern (premise h): the owning module holds and pins the evidence, governance reads the policy by the reference's type, and `submit`'s signature does not change. (b) makes governance's lookup key differ from the thing approved, and the open-request uniqueness constraint (`uq_approval_requests_open_artifact`, `models.py:680`) would then collide an RV's own review with its deployment review. (c) changes every module's evidence path, which is wider than this slice | decision point | yes — Tasks 1, 2, 3 and 5 | **RL-1301 (working id 9906) A — (a)**: a Deployment Request row owned by the deployment module, `deployment` in `ARTIFACT_TYPES`, evidence pinned on the row at submission, the deploy route executing only an approved request and re-evaluating FR-429 from the pinned evidence. RL-1301 C amends the OQ-1234 ruling's item 3: the skip record is pinned on the Deployment Request row |
| DP-S2-3 | **The shape of `CR-1212` item 4's environment scope on `deployment:promote`.** The test is fixed ("a Deployer whose grant names only `uat` is refused on `prod`", `PL-1237:810-811`); the mechanism is not. A grant's scope today is one resource or the workspace (premise f) | (a) Add `ScopeType.ENVIRONMENT`, with `scope_id` the Environment's id; the deploy route checks `deployment:promote` against `ResourceRef(ENVIRONMENT, env.id)`, so `_covers` is reused unchanged and a workspace-wide Deployer still covers every environment; (b) as (a), but `deployment:promote` is honoured **only** through an environment-scoped grant, so a workspace-wide Deployer deploys nowhere; (c) a list of environment names on the assignment | **(a).** It reuses the one scope mechanism and its one check (`rbac.py:205-217`), keeps today's workspace-wide Deployer working, and satisfies the test. (b) is stricter and makes every existing grant useless at once. (c) adds a second scope mechanism beside `scope_type` | decision point | yes — Tasks 1, 2 and 5 | **RL-1301 (working id 9906) B — (a)**: `ScopeType.ENVIRONMENT`, checked **in the handler** with `resource=ResourceRef(ScopeType.ENVIRONMENT, <environment id>)`, never by a bare `requires(Permission.DEPLOYMENT_PROMOTE)`; `06` FR-345 gains "or Environments" in the spec-first commit |
| DP-S2-4 | **Where is "the spec's declared permission" for a route?** Acceptance 12 (c) must pin each route's permission against the spec, never a hand-written map (the 11:06:50 entry). At the tree above **no spec declares one per route**: every module's §5.1 REST table has the columns `Method \| Path \| Purpose` only (`01`, `02`, `03`, `06`, `07`), and `docs/contracts/openapi/generated.json` carries no `x-` extension at all (`grep -o '"x-[a-z-]*"' docs/contracts/openapi/generated.json` prints nothing) | (a) A `Permission` column on each module spec's §5.1 REST table, filled for every route (the spec is where a route is declared), and a parser in the test; (b) a routes cell on each Built row of `06` §4.1's permission table (RL-1305's D4), one place beside the catalogue WK-1178 checks; (c) an `x-permission` extension emitted into the generated OpenAPI from `requires()` | **(a).** The route's row is the one place a reader looks for what a route requires, and a missing cell is visible there. (b) puts routes into a permission catalogue whose rows are keyed by permission, so a route guarded by two permissions or none has no natural row, and it couples this task to RL-1305's table. (c) is circular: the "spec" would be generated from the code under test, so the `AUDIT_READ → JOB_READ` swap would change both sides and stay green. **Cost of (a):** a spec edit to five modules' §5.1 tables, which serialises with every in-flight slice appending §5.1 rows (**Write set**) | decision point | **no** — Task 0A (c) moved out of this slice (the 11:17:35 entry) | **#977 (working id 9907, head `070a83fe` as PL-1306 read it; `1dfca5c7` at the tree above, dm-effort-high) — (a)**: a Permission column on all 152 §5.1 rows (*PL-1392*: the audit's F-A2 measured 156 at the tree above; the WK-1178 pin slice re-derives the population at its dispatch), carried by a WK-1178 slice **serialised with this one**; this slice's new routes are declared by whichever of the two lands second, and the later checks the earlier's |
| DP-S2-5 | **The policy is keyed by environment *name*, and FR-428 lets an Environment be renamed** (RL-1301 audit advisory A3). `ApprovalPolicy.entry_for(artifact_type, environment)` matches a string (`packages/model-schema/src/model_schema/approvals.py:146-162`) and `ApprovalRequestRow.environment` is `String(32)` (`backend/src/app/db/models.py:659`). RL-1301 A.1 pins the Environment's identity on the request row but not on the policy key, so renaming `prod` would leave the `prod` entry matching nothing, and by RL-1301 A.5 a target with no entry needs no request: a rename makes a gated target look ungated | (a) Key the policy by Environment identity, and refuse a rename that would change any entry's resolution; (b) refuse any rename of an Environment named by a policy entry; (c) re-key the policy's entries in the rename's transaction | **(a)**, the maintainer's steer (the 11:14:48 entry, last bullet). It closes the hole at its cause, since the key stops being renamable. (b) leaves the key renamable and relies on every rename path remembering the check. (c) edits governance's policy from `07`'s rename route, a second writer of the policy beside `set_policy` | decision point | yes — Tasks 2, 4 and 5 | **Disposed by RL-1301 A.6 (head `80afeb40`, text unchanged since `327e1179`: "This item disposes of the leaf plan's DP-S2-5") — an immutable Environment slug**: policy, `ApprovalRequestRow.environment`, `{env}` and every reference key on the slug; FR-428's rename changes the display name only; a slug change is refused; `set_policy` refuses an entry naming no existing slug. Retiring a policy-named Environment is left to this plan (refused, **Decided in this plan**; RL-1301 A.6 at `80afeb40` confirms both this and the request slug) |
| DP-S2-6 *(PL-1392)* | **What 2xx type do the 2 changed approval-request routes declare?** The 10:10:46 entry accepts "the method deltas on Withdraw and POST /approval-requests' deployment branch, typed the same way". The bodies can be (Acceptance 16). The 2xx cannot be typed as any shape that exists today without resolving a disagreement first: `service.to_dict` (`backend/src/app/platform/approvals.py:648-673`) emits `environment` and no `workspace_id`; `ApprovalRequest` (`packages/model-schema/src/model_schema/approvals.py:275`, `extra="forbid"`) requires `workspace_id` and has no `environment`; the hand-authored `docs/contracts/schemas/approval-request.schema.json` requires `evidence_bundle` and `checklist`, which neither carries (RL-1301 A.2) | (a) **Reconcile, then type:** a dated `06` §4.3 amendment and `ApprovalRequest` gains `environment`; `to_dict` emits `workspace_id`; the hand-authored contract is ruled on (amended, or declared one-sided); both routes' 2xx become `$ref ApprovalRequest`. (b) **A view shape:** a published `ApprovalRequestView` in `model-schema` that matches what `to_dict` emits, as the backend's `AuditEventView` (`backend/src/app/api/audit.py:63`) and `TraceView` (`backend/src/app/api/traces.py:100`) are views; `06` §4.3 and `ApprovalRequest` untouched, the disagreement filed as a finding. (c) **Bodies only in S2:** this slice types the two bodies and leaves both 2xx in FD-1335 Part B, asserted unchanged; the disagreement is resolved once, for all four routes that share `to_dict`, by Part B's slice (WK-1178) | **(c).** The disagreement is one defect across four routes. Resolving it for two of them in S2 splits one fix across two Works, and puts a §0 reconciliation, which needs a ruling, on G2's critical path (the 10:10:32 entry: S2 is "on G2's critical path"). (a) is the right end state, but it is a spec change plus a contract ruling; it belongs with Part B, which must make it for `decide` and `GET` anyway. (b) adds a second shape for one concept beside `ApprovalRequest`, close to what `CLAUDE.md` §2 forbids ("a shape defined twice will diverge"). **Cost of (c):** it narrows the 2xx half of the acceptance the maintainer accepted, so it needs the maintainer's confirmation, not only a ruling | decision point | **yes** — Acceptance 16's 2xx half, Tasks 5 and 6 (rows 8 and 9) | **(c), decided 2026-10-01 by the maintainer's entry headed `2026-10-01 10:32:26 BST — #1062 DP-S2-6: option (c) ACCEPTED with three conditions; it narrows my item (3) for the 2 CHANGED routes' 2xx only; the three-shape disagreement becomes its own FD` (`~/gi-pricing-plan.local/channel/to-lead.md`)**. Supersedes, for these two routes' 2xx only, item (3) of the 10:10:46 entry. The 2xx are owned by **FD 9752 (working id)**, which names both routes; Acceptance 18 pins that S2 does not widen them. Condition 3 of that entry: auditor-1062 verifies the three-shape premise field by field before this plan mints; if the premise is wrong, (c) falls and DP-S2-6 goes to a decision-maker. |
| DP-S2-7 *(PL-1392, C14)* | **Can a non-draft Rating Version be compiled?** FD-1393 (#1064): `compile_rating_version` (`backend/src/app/platform/rating_versions.py:395-542`) and its route (`backend/src/app/api/models.py:1233`) read no status, so an approved version's bytes can move after approval | (1) refuse compile unless `draft`, in the service; (2) allow, but bind the compiled bundle immutably (RL-915 §4's deferred which-bundle-is-live policy); (3) intended, and documented | none from this plan: the maintainer sent it straight to a decision-maker, with a lean to (1) "for the DM to test, not a ruling" (the 10:34:45 entry) | decision point | **yes — S2 does not merge without it**: Acceptance 19, Task 5A | open: decision-maker dm-s2c7, RL-1379, in progress; the maintainer's entry headed `2026-10-01 10:34:45 BST — FD 9754 (#1064, a non-draft rating version can be recompiled and its bundle rewritten): MEDIUM, owner WK-674 S2, and **S2 does not merge without the guard**; the option choice goes to a DM now` |

**Decided in this plan, as slice design, not decision points** (RL-1296 leaves
them to "Slice 2", its "Not ruled here"):
- **The skip field's name**: `skippable_predecessors: tuple[str, ...] = ()` on
  `ApprovalPolicyEntry` — the environment names whose deployment a deployment into this
  entry's environment may skip.
- **The skip record's shape**: `PromotionSkip(skipped_environment: str, reason: str)`, frozen,
  `extra="forbid"`, `reason` refused when empty after `strip()`. It is pinned on the
  Deployment Request row (RL-1301 A.2, and RL-1301 C's amendment of the OQ-1234 ruling's item 3).
- **Environment scope**: an Environment is a **deployment-wide** (tenant) object, not a
  workspace one — **confirmed by RL-1301 A.6 at `80afeb40`** ("Environments are
  deployment-wide, not per workspace"; its earlier "the workspace's Environments" was loose
  wording, not a design difference). `07` §4.2 has no workspace field (`07:245-259`), API keys carry environment
  names with no workspace (`models.py:462`), and ADR-710 makes the deployment the tenant
  boundary. A Deployment row carries the `workspace_id` of its Rating Version, so "live in
  environment E" is read per workspace.
- **Predecessor**: the Environment's `requires_prior_environment` (`07:252`), as the §4.2
  contract already declares it, seeded `null`, `dev`, `uat`.
- **Environment slug and display name** (RL-1301 A.6): every Environment has an **immutable
  `slug`** (`_SLUG`'s grammar, `refs.py:33`) and a mutable display `name`. The seeds are slugs
  `dev`, `uat`, `prod`. The policy's `environment`, `ApprovalRequestRow.environment`, every
  `{env}` path parameter and every Environment reference name the slug; FR-428's rename
  changes the `name` only. **A slug is never reissued**: a retired Environment keeps its
  row and its slug (auditor-plans N1), and "an existing Environment" means a non-retired one
  wherever it is checked (N3).
- **The Deployment Request slug scheme** (RL-1301 A.1 leaves it to this plan, "the slug must not
  be a renamable name"): **the target Environment's slug**, e.g. `deployment:prod@3` — the
  third request into `prod`. *(Revised 2026-09-30: the first draft used the Environment's id
  in hex because the name was renamable; RL-1301 A.6 makes the slug immutable, so the readable
  form now meets the same constraint.)* ID-2's "monotone per parent" reads as per
  Environment. The Environment is pinned on the row by its id as well, and the Rating Version
  is pinned on the row, not in the slug.
- **Existing credentials naming an environment that is not seeded** (auditor-plans V2): the
  migration **refuses to upgrade** and names them. It is not allowed to guess. Seeding an
  Environment for each stray name would create Environments with no promotion order and no
  policy entry, so each would be an ungated target the operator never chose. Leaving the key
  and refusing only at rotation would break RL-1301 A.6's "`Caller.environment` then always
  names a real, unrenamable Environment" for every request until the rotation. Refusing the
  upgrade is loud, changes nothing, and leaves the choice (revoke, narrow, or create the
  Environment through the route afterwards) to the operator. There is no production
  deployment yet, so the cost is at most a revocation on a development database. Historical
  trace strings are left as they are (Acceptance 3), since nothing resolves them.
- **Retiring an Environment that a policy entry names** (RL-1301 A.6 leaves it to this plan):
  **refused**, with 409 naming the entry, until `set_policy` removes it. Otherwise the policy
  would hold an entry for an Environment that no longer resolves, which is the silent
  ungating RL-1301 A.6 exists to prevent.
- **Who may submit a deployment request**: the same handler check as the deploy itself,
  `deployment:promote` with the target Environment as the resource (RL-1301 B.2). Submitting is
  the Deployer's act of asking to deploy.

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch.
- [ ] `uv sync --all-packages` (a fresh worktree without it reports hundreds of phantom mypy
  errors — `dev-commands`).
- [ ] Confirm, naming the `origin/main` SHA read: `RL-1296` is on `main`; #960 is merged; RL-1301 is merged and minted; #974 is merged and minted (RL-1380's minted id, cited by it from here on); `SL-1302` and `SL-1300` are closed. **Stop if any does not hold.**
- [ ] *(PL-1392, C2.)* Run Acceptance 8's predicate at `origin/main` and record its output
  (2 at the tree above). Record whether `SL-1360` (`PL-1359`) has merged, which decides
  whether Acceptance 8's `STALE_OWNER` red can be shown.
- [ ] *(PL-1392, C8.)* Confirm `SL-1367` is not in flight, and that no other in-flight slice
  edits `backend/src/app/api/score.py`; name the SHA read. **Stop if one does.**
- [ ] Re-derive premises a–u; record the tree and each result in the ledger.
- [ ] Note the gate-slot rule of Acceptance 10 (the 11:42:08 entry) for every full run
  this slice makes.
- [ ] Run the **Write set** check against every build slice in flight (`gh pr list --state
  open`, and the lead's `eta.md` "In flight"), and read anything that rules on FR-267,
  FR-428, FR-429, the approval policy, `ScopeType` or `score.py`. Name the SHA read.
- [ ] Create the slice ledger (`LG-`, the executor's; `document-ids.md` §1.6), with a working
  id.

### Task 0A: The authorisation sweep sees every route — first, before any new route

**Files:** Modify `backend/tests/test_api_authorisation_sweep.py` (`_operations` `:68-76`,
`test_every_operation_refuses_a_caller_holding_no_roles` `:103`,
`test_every_operation_declares_the_permission_it_enforces` `:175-202`,
`test_the_sweep_covers_the_whole_published_surface` `:205-211`); each sibling Acceptance 12 (f)
finds. **Step (c) is not in this slice** (the 11:17:35 entry); nothing here waits on DP-S2-4.

**Interfaces — Produces** (a test-module helper; later tasks' routes are checked by it):
```python
def _flattened_routes(routes: Sequence[BaseRoute]) -> Iterator[APIRoute]:
    # Every APIRoute, descending into included routers (the A1 finding's shape).
    ...

HANDLER_GUARDED: Final[dict[tuple[str, str], tuple[str, int]]]
    # (METHOD, path) -> (file, line) of the handler's require_permission( / membership check
```

- [ ] **Red first, (a):** replace the `api_client.app.routes` loop at `:189` with
  `_flattened_routes(...)` **only after** adding the equality assert between the iterated
  operation count and `len(_operations(...))` without `OPEN_BY_DESIGN` filtering — first run
  the equality against the unchanged loop and quote the red (2 iterated against the OpenAPI
  count). Predicted cause: the loop does not descend into `_IncludedRouter`. A red for any
  other cause is a plan defect. Before relying on `original_router`, confirm the attribute
  name at the installed FastAPI (`uv run python -c "import fastapi; print(fastapi.__version__)"`
  and a one-line probe), and name what the probe printed in the ledger.
- [ ] **Red first, (b):** in the test's setup, build the app with `requires()` removed from
  one real guarded route (monkeypatch its `dependant`), and show the static sweep fails naming
  it. Restore.
- [ ] **(e):** the named allow-list `HANDLER_GUARDED`, with the two routes and their file:line
  from Acceptance 12 (e). A companion assert reads each named file and line and fails if it no
  longer holds `require_permission(` (or, for `me.py`, the `WORKSPACE_SCOPE_DENIED` refusal).
  The static sweep treats an allow-listed route as guarded; nothing else is skipped.
- [ ] **Red first, (d):** the no-roles behavioural sweep builds a **valid** body for each
  operation from its schema in `app.openapi()`, and fills **every required path and query
  parameter** from that parameter's own schema (not `_concrete`'s blanket UUID, `:78-90`,
  which a slug-typed parameter would refuse with 422). The builder covers, for required
  properties only: `$ref` resolved; enums → the first member; **`format`** → `uuid` a fresh
  UUID7, `date` `2026-01-01`, `date-time` `2026-01-01T00:00:00Z`; **`anyOf`/`oneOf`** → the
  first branch it can satisfy; **`allOf`** → the branches merged; `pattern` → a value from
  the schema's `examples` when present; strings → a `minLength`-long filler; numbers →
  `minimum` or 1. (auditor-plans counted, at the tree above, 38 `format: uuid` nodes, 116
  `anyOf`/`oneOf`/`allOf` nodes and 59 UUID path parameters; without these the unsatisfiable
  list would hold most routes.) The sweep asserts 401 or 403 exactly. An operation whose schema the builder cannot satisfy is
  named in a constant with its reason, and that constant's size is asserted, so it cannot
  grow silently. Red first: `POST /api/v1/me/workspace` with a valid body — its
  `workspace_id` is `format: uuid`, filled with a workspace the caller is not a member of —
  where the current sweep passes it only on 422.
- [ ] **(f), (g):** fix each sibling; assert the partition of Acceptance 12 (g).
- [ ] Green; quote the iterated count and the OpenAPI count in the ledger. Commit:
  `test(api): the authorisation sweep flattens included routers and pins every route (A1, WK-674 S2)`.

### Task 1: Spec — `03`, `07`, `06`

**Files:** Modify `docs/specs/03-rating-engine.md` (§3.10 notes, a new §4 subsection, one
§5.1 row), `docs/specs/07-platform.md` (§4.2 note, §5.1 rows), `docs/specs/06-governance.md`
(FR-345 and the §4.1 scope example, RL-1301 B.4; §4.2 RL-886 note). **Not** the skip field — it lands in
Task 2's commit (RL-1296, item 5).

- [ ] `03` §4: a new subsection **`Deployment`**, numbered **§4.12** *(PL-1392, C4)*, after
  §4.11 `SubGraph` (`03:743`). If §4.12 is taken at the executor's tree, stop and report. It gives the shape (id, workspace, environment, Rating
  Version ref, bundle hash, deployed by, deployed at, reason, the approval request it rests
  on: the executed Deployment Request, RL-1301 A.5), the invariants (append-only, never updated in place; `approved` versions
  only, FR-238; a `sub_graph` or any non-`rating_version` reference is refused, G3), an
  example, and the audit actions this Work emits: `deployment.created` (this slice),
  `deployment.rolled_back` (Slice 5), `deployment.routing_changed` and
  `deployment.shadow_configured` (Slice 6), each named here once so Slices 5 and 6 append
  nothing to the catalogue.
- [ ] `03` §5.1: append `| GET | /api/v1/environments/{env}/deployments | Deployment history for an environment (FR-267; read by `06` FR-382) |`. Do not touch `03:810-845`.
- [ ] `03` §3.10: a dated note after FR-267 naming the new contract and this slice, and after
  FR-272 naming the Audit Event limb's delivery for deploy.
- [ ] `07` §4.2: a dated note after the `Environment` example: `live_deployments` is derived
  from Deployment rows (never stored twice), `settings` lands in Slice 3 (`OQ-1235`), and
  `requires_prior_environment` is FR-429's predecessor.
- [ ] `07` §5.1: append `| PATCH | /api/v1/environments/{slug} | Change an environment's display name or description; the slug is immutable (`admin:manage_environments`) |` and `| POST | /api/v1/environments/{slug}/retire | Retire an environment that has no live Deployment and that no policy entry names |`. `07` §4.2's `Environment` gains `slug` beside `name`, in a dated note citing RL-1301 A.6.
- [ ] `06` FR-345: its list of scopes gains "or Environments", dated, citing RL-1301 (by id
  once minted) and `CR-1212` item 4 (RL-1301 B.4); the scope kind is the `ScopeType` value
  `environment`, which Task 2 adds to the enum (so the contract regenerates there). `06` §4.1's assignment example may show an
  `environments` scope, with a dated note citing `RL-1232` DP-6 as amended.
- [ ] Wherever `ARTIFACT_TYPES`' list is stated as a spec (`refs.py:18-19` names it a spec
  change, RL-1301 A.1): `deployment` joins it, with the Deployment Request's meaning and its slug
  scheme (**Decided in this plan**).
- [ ] `06` §4.2: a dated note after the JSON: the `deployment` entry is now in
  `DEFAULT_POLICY` (RL-886).
- [ ] `03`'s new §4 subsection also declares the **Deployment Request** (RL-1301 A.1–A.2): its
  reference form `deployment:<environment slug>@<n>`, the pinned Rating Version and
  Environment identity, the two pinned evidence items (`rating_version_approval`: the
  decided approval request of the pinned version; `uat_deployment`: the predecessor
  Deployment's id **or** a `PromotionSkip`), written once at submission and never updated
  (FR-356, `00` FR-4). `03` §5.1 also gains
  `| POST | /api/v1/environments/{env}/deployment-requests | Submit a deployment request for approval (FR-267, FR-429) |`.
- [ ] `python3 scripts/audit-docs.py`; quote the rc. Commit:
  `docs(specs): 03 Deployment contract, 07 Environment note and routes, 06 scope and RL-886 note (WK-674 S2)`.

### Task 2: `model-schema` — shapes, the policy entry, the skip field and the predicate

**Files:** Create `packages/model-schema/src/model_schema/deployments.py` (`Environment`,
`Deployment`); modify `approvals.py` (`ApprovalPolicyEntry`, `DEFAULT_POLICY`, the predicate),
`permissions.py` (`ScopeType.ENVIRONMENT`, RL-1301 B.1), `refs.py` (`"deployment"` in
`ARTIFACT_TYPES`, RL-1301 A.1), `__init__.py`;
`scripts/generate-contracts.py` (slug map); `docs/specs/06-governance.md` §4.2 (the skip
field — **this commit**); regenerate `docs/contracts/`; tests under
`packages/model-schema/tests/`.

**Interfaces — Produces:**
```python
class PromotionSkip(BaseModel):          # frozen, extra="forbid"
    skipped_environment: str
    reason: str                           # refused when reason.strip() == ""

class ApprovalPolicyEntry(BaseModel):     # existing; one field added
    skippable_predecessors: tuple[str, ...] = ()

def promotion_order_refusal(
    entry: ApprovalPolicyEntry | None,
    *,
    target: str,
    predecessor: str | None,
    predecessor_deployed: bool,
    skip: PromotionSkip | None,
) -> str | None:
    """None when the order is satisfied; otherwise why not. Reads only its arguments."""
```

- [ ] **First commit — the `deployment` `DEFAULT_POLICY` entry (RL-886).** Red first: a test
  that `DEFAULT_POLICY.entry_for("deployment", "prod")` is not `None`. Predicted failure: it
  returns `None` (premise b). Add the entry exactly as `06:362-364` shows it (`prod`, 1
  approver, role `deployer`, evidence the two floor kinds). Commit.
- [ ] **Second commit — the skip field, its validator, `06` §4.2 and the contract, together
  (RL-1296, item 5).**
  - Red first, in `packages/model-schema/tests/test_approvals.py` (append; mirror its
    existing tests): an `ApprovalPolicy` whose entry sets `skippable_predecessors` with
    `environment=None`, and one with `artifact_type="rating_version"`, each raise
    `ValidationError` naming the field. Predicted failure: `extra="forbid"` rejects the
    unknown field — a different error is a plan defect. After adding the field, the
    predicted red becomes "no error raised"; quote both.
  - Add the field and an `@model_validator(mode="after")` on `ApprovalPolicyEntry` refusing
    a non-empty value unless `artifact_type == "deployment"` and `environment is not None`.
  - `06` §4.2: add `"skippable_predecessors": []` to the `prod` `deployment` entry and a
    dated note citing `RL-1296`.
  - Regenerate contracts; `generate-contracts.py --check` exits 0; commit all of it at once.
- [ ] **The predicate**, red first over a table of cases (the one predicate every caller
  uses: the route, the request's submission, and the route's re-evaluation from pinned
  evidence, RL-1301 A.5): satisfied when the target has no
  predecessor, or the predecessor is deployed; otherwise satisfied only when `skip` names
  the predecessor, `skip.reason.strip()` is non-empty, and `entry` is not `None`, **names the
  target (`entry.environment == target`)**, and lists the predecessor in
  `skippable_predecessors`. The target check is hardening (auditor-plans F8): the fallback's
  no-skip then rests on the predicate as well as on the validator, so an unqualified entry
  that somehow carried the field still grants nothing. Red first: an unqualified entry
  constructed with `model_construct` (bypassing the validator) and carrying the field grants
  no skip. Every other case returns a reason naming the
  target and the predecessor. Add `PromotionSkip` and the function to `approvals.py`.
- [ ] `Environment`, `Deployment` and `DeploymentRequest` shapes in `deployments.py`,
  matching Task 1's contract and `07` §4.2 (without `settings`). `ScopeType.ENVIRONMENT`
  (RL-1301 B.1); `"deployment"` in `ARTIFACT_TYPES` (RL-1301 A.1), with
  `docs/contracts/schemas/common/artifact-ref.schema.json` regenerated. Export, register the slugs, regenerate, run the
  contract guard, quote its result. Commit.
- [ ] *(PL-1392, C1.)* **The Route table's request shapes**, in the same commit as the shapes
  above: `EnvironmentCreate`, `EnvironmentUpdate`, `DeploymentRequestCreate` and
  `DeploymentCreate` in `deployments.py`, each `extra="forbid"`, with the fields the Route
  table gives (`slug` typed `Slug`, `refs.py:41`; references typed `ArtifactRef`, never `str`).
  `GENERATED_SHAPES` (`scripts/generate-contracts.py:38`) gains `environment`,
  `environment-create`, `environment-update`, `deployment`, `deployment-create`,
  `deployment-request` and `deployment-request-create`. Red first: a model-schema test that
  each class validates its example and refuses an unknown key; predicted red, `ImportError`.
  Acceptance 2's two counts are quoted. Each new slug gets its `ONE_SIDED_SLUGS` entry in
  `backend/tests/test_contracts.py` in the same commit (C15), red first as Acceptance 2 says;
  `approval-withdrawal` and `approval-submission` get theirs in Tasks 6 and 5. *(C18.)* In the
  same commit, each new `docs/contracts/schemas/generated/<slug>.schema.json` path goes into
  `_CONTRACT_ARTIFACT_PATHS` (`scripts/audit-docs.py:2620`, after `:2667`), and the count at
  `tests/test_audit_docs_ids.py:2117` is re-derived, red first as Acceptance 2 says; Tasks 6
  and 5 do the same for their two slugs. If the FD-1357 fix has merged first, the count is
  re-derived on the merged tree and the gate re-run. `ApprovalWithdrawal` and
  `ApprovalSubmission` land in Tasks 6 and 5, with the routes that use them; those routes'
  2xx stay untyped (DP-S2-6 (c), FD 9752 working id).
- [ ] **Conditional: only if this slice merges before the FD-1357 fix (PL-1376)**
  *(C18; `CLAUDE.md` §12)*. Write the step into `.claude/skills/contract-schema/SKILL.md`:
  "a new generated schema → register its literal path in `scripts/audit-docs.py`
  `_CONTRACT_ARTIFACT_PATHS` and bump `tests/test_audit_docs_ids.py`'s `non_markdown`
  count", and refresh that skill's `## Verified` date with the tree. If apt, add a one-line
  pointer from `.claude/skills/docs-audit/SKILL.md`'s check 35 text (the paragraph on adding
  a file that cannot carry a header, `:363-368`). Same commit as the registration. If the
  FD-1357 fix merged first, it wrote the step: the ledger says so and this step is skipped.

### Task 3: The migration

**Files:** Create one revision under `backend/migrations/versions/`; modify
`backend/src/app/db/models.py` (append `EnvironmentRow`, `DeploymentRequestRow`,
`DeploymentRow`; add the nullable `deployment_id` to `ScoringTraceRow`); test
`backend/tests/test_migration_deployments.py`.

- [ ] Red first: the Acceptance 3 migration test, on a scratch database upgraded to
  `2f598e89d12c` *(PL-1392, C5)* (mirror `scratch_database` (`:359`) and `_upgrade(cfg, revision)` (`:403`) in
  `backend/tests/test_migration_dataset_owner.py`; do not invent new fixtures), with two
  `scoring_traces` rows inserted before the upgrade. Predicted failure: the `environments`
  table does not exist.
- [ ] The revision: `environments` (UUID id, immutable `slug` unique across **all** rows, retired included (N1), display `name`, description, `promotion_order`,
  `requires_prior_environment` nullable, `retired_at` nullable), seeded `dev`/`uat`/`prod`;
  `deployments` (UUID id, `workspace_id`, `environment_id` FK, `rating_version_ref`, `bundle_hash`,
  `deployed_by`, `deployed_at`, `reason`, and the Deployment Request id it executed, nullable
  for a target with no `deployment` policy entry, RL-1301 A.5), with no update path in the
  application; `deployment_requests` (UUID id, `workspace_id`, `slug`, `version`, unique
  `(workspace_id, slug, version)`, `environment_id` FK, `rating_version_ref`, `status`
  (`draft`/`review`/`approved`/`rejected`/`withdrawn`/`executed`), `approval_request_id`,
  `evidence` JSONB written once — RL-1301 A.4 permits a database trigger to refuse an update;
  if the executor adds one, its test is red first too); `scoring_traces.deployment_id` nullable FK. Downgrade drops
  all three in reverse.
- [ ] **`deployment_requests` joins Slice 2a's guard, evidence-only (Acceptance 13)**, in
  this same revision: the trigger on the new table with arguments `('deployment', <slug
  column>)` and no `'flag'`, and its `status_vocabulary` declaration. Red first:
  Slice 2a's `pg_trigger` presence check fails naming `deployment_requests` until the clause
  is in.
- [ ] **The credential pre-check (V2)**, first in the revision's `upgrade()`: select unrevoked
  `api_keys` whose `environment`, and non-archived `service_accounts` whose `environments`,
  name anything
  outside `dev`/`uat`/`prod`; if any, raise with their ids and names before any DDL. Red first:
  Acceptance 3's `staging` key.
- [ ] Round trip (`upgrade`, `downgrade -1`, `upgrade`) and `tests/test_repository_invariants.py`;
  quote each rc. Commit.

### Task 3A: moved to Slice 2a

*(2026-09-30, the split below.)* The approval guard — the trigger, its test-database check,
the declarations on the existing approval tables, the named seed writers, the validation
allowance and the 17 fixture moves — is Slice 2a's (PL-1303, slice SL-1302). This slice
starts after Slice 2a closes. What stays here is Acceptance 13: `deployment_requests` added
to the guarded set, in Task 3's migration and Task 5's tests.

### Task 4: Environments — the entity and its routes (FR-428)

**Files:** Create `backend/src/app/platform/environments.py`, `backend/src/app/api/environments.py`;
modify `backend/src/app/main.py` (one registration), `docs/specs/06-governance.md` (`06:294`, Branch A); test `backend/tests/test_environments.py`; create `backend/tests/test_deployment_route_types.py` (Acceptance 14–16) *(PL-1392)*.

- [ ] Red first: the Acceptance 4 `admin:manage_environments` refusals and a positive
  create / rename / retire by an Admin. Predicted failure: 404 on `/api/v1/environments`
  (no router) — the ledger quotes it; after the router exists without the check, the
  predicted red is "the non-Admin call succeeds".
- [ ] **The slug and the rename (RL-1301 A.6)**, red first on Acceptance 4's A3 cases: `PATCH
  /api/v1/environments/{slug}` changes `name` and `description` only, and a body naming a
  different `slug` is refused; `POST /api/v1/environments/{slug}/retire` is refused while a
  policy entry names the slug. `set_policy` (`backend/src/app/platform/approvals.py:170-222`)
  refuses a `deployment` entry whose `environment` is not an existing Environment slug,
  reading the environments platform module (permitted by DEP-1, Acceptance 5).
- [ ] **Slug validity and permanence (auditor-plans N1, N2).** `POST /api/v1/environments`
  validates the new `slug` with `model-schema`'s `Slug` type (`refs.py:41`, built from
  `_SLUG` at `:33`), never a second copy of the pattern. A retired Environment keeps its row
  (`retired_at` set) and its slug, and the `environments` table's unique constraint on `slug`
  covers retired rows, so a slug is never reissued. Red first: Acceptance 4's N1 and N2 cases.
- [ ] **"Existing" means non-retired (N3).** The existence checks of `set_policy` and of the
  credential step below both read `retired_at IS NULL`. Red first: Acceptance 4's N3 cases.
- [ ] **Credentials name only existing Environments (RL-1301 A.6 at `80afeb40`).** In
  `backend/src/app/api/service_accounts.py`, each name in `environments` (`:63`, a free
  `list[str]` today) is checked against the Environment slugs at creation and at rotation —
  the two places a key is minted from `environments[0]` (`:180`, `:246`) — and refused with
  422 `VALIDATION_FAILED` naming it. Red first: a key for `prd` is refused.
- [ ] `GET`/`POST /api/v1/environments`, `PATCH /api/v1/environments/{slug}`,
  `POST /api/v1/environments/{slug}/retire` (refused while any Deployment in it is live, while
  a policy entry names it, or while an unrevoked Service Account key names it),
  each writing its Audit Event; the three writes use
  `Depends(requires(Permission.ADMIN_MANAGE_ENVIRONMENTS))`.
- [ ] **Acceptance 8, this permission (Branch A)** *(PL-1392, C2)*: empty the
  `admin:manage_environments` `Check owner` cell in `06` §4.1 (`06:294`) **in this commit**, the
  one that adds `Depends(requires(Permission.ADMIN_MANAGE_ENVIRONMENTS))`. Acceptance 8's
  predicate prints 1; if `SL-1360` has merged, its parity test passes on this commit, and the
  `STALE_OWNER` red (cell left as `WK-674`) is quoted first.
- [ ] **Route types, rows 1–4** *(PL-1392, C1)*: red first, Acceptance 14 and 15 over rows
  1–4 (the test module is created in this commit, with the route-set pin, which fails until
  Task 5 adds rows 5–7: the pin is asserted over rows 1–4 here and widened to all 7 in Task
  5's commit). Each handler's body is the Route table's `model-schema` type, and each handler
  returns the Route table's 2xx type (a return annotation, as `backend/src/app/api/sub_graphs.py:47`
  does). The broken-input runs of items 14 and 15 are quoted.
- [ ] Green; commit.

### Task 5: The deploy route and the `prod` approval (FR-267, FR-429, FR-272, NFR-498, G3, FR-347)

**Files:** Create `backend/src/app/platform/deployments.py`, `backend/src/app/api/deployments.py`;
modify `backend/src/app/main.py` (one registration), `backend/src/app/errors.py`
(`DEPLOY_REQUIRES_APPROVAL` in the rating module's set), `docs/specs/06-governance.md` (`06:283`, Branch A), `backend/src/app/api/approvals.py` (`SubmitApproval` moved out; `_resolve_the_artifact`; `_carry_to_the_artifact`), `packages/model-schema/src/model_schema/approvals.py` (`ApprovalSubmission`), `scripts/generate-contracts.py` (`approval-submission`); tests `backend/tests/test_deployments.py`, `backend/tests/test_deployment_route_types.py` *(PL-1392)*.

- [ ] Red first: every Acceptance 4 case not covered by Task 4, each with its predicted
  cause written in the test's docstring before the code exists.
- [ ] **The Deployment Request (RL-1301 A)**, `POST /api/v1/environments/{env}/deployment-requests`,
  body `{rating_version_ref, change_summary, skip?: PromotionSkip}`:
  1. G3 as below; `deployment:promote` checked in the handler with the Environment as the
     resource (RL-1301 B.2); add the route to `HANDLER_GUARDED` with its file:line in this commit.
  2. Load the Rating Version (must be `approved`) and its decided approval request; find the
     predecessor's successful Deployment of that version, or take the `skip`.
  3. Call `promotion_order_refusal` with the target's environment-qualified entry; a reason
     → 422 `EVIDENCE_INCOMPLETE`. A missing floor item → the same.
  4. Write the row with its `evidence` **once**, then call the unchanged `approvals.submit`
     with `artifact_ref=deployment:<environment slug>@<n>` and `environment=<slug>`, as
     `rating_versions.submit_for_review` does (`backend/src/app/platform/rating_versions.py:299-305`).
     `backend/src/app/platform/approvals.py` imports nothing from the rating or deployment
     modules (Acceptance 5).
  5. `apply_approval_decision` in the deployment module loads the row **locked**
     (`with_for_update()`, as `rating_versions.py:337` does), calls
     `approvals.require_in_review(ref, row.status)` on it (`backend/src/app/platform/approvals.py:118`),
     as `rating_versions.py:358` does, and only then moves the row to `approved` (or back),
     called from a **new deployment branch of `_carry_to_the_artifact`**
     (`backend/src/app/api/approvals.py:488`, beside the four at `:500-523`, inside `service.approval_decision(session)` at `:499`; RL-1301 audit
     advisory A5) — the **only** writer of `approved` (Acceptance 13). It refuses a row whose
     evidence lacks a floor item.
  6. **The generic route (RL-1301 audit advisory A2).** Once `deployment` is in
     `ARTIFACT_TYPES`, `POST /api/v1/approval-requests` (authenticated only, `06` §5) must not
     become a way around the owning module. `_resolve_the_artifact`
     (`backend/src/app/api/approvals.py:425-485`) fails closed today with
     `ARTIFACT_TYPE_NOT_RESOLVABLE`; it gains a deployment branch that accepts **only** a
     Deployment Request row in `review` whose `evidence` holds both floor items, and refuses
     every other deployment reference (auditor-plans F3). **Why this cannot create an
     approvable request without pinned evidence (the FD-1200 class):** a Deployment Request
     row exists only through the owning module's submission (step 4), which writes the
     evidence and the approval request in one transaction; the generic route cannot create a
     row, and a row it could name in `review` already holds its open request, so a second
     one is refused by `uq_approval_requests_open_artifact` (`backend/src/app/db/models.py:645`).
     Red first (Acceptance 4): the generic route naming a reference with no row, a row not in
     `review`, and a row stripped of a floor item by a fixture, each refused.
- [ ] `POST /api/v1/environments/{env}/deployments`, body `{rating_version_ref, reason,
  deployment_request_ref?}` (`extra="forbid"`):
  1. **G3 first**: parse the ref; refuse any type other than `rating_version` with 422
     `VALIDATION_FAILED` naming the type, before reading any row.
  2. `rbac.require_permission(..., permission=Permission.DEPLOYMENT_PROMOTE,
     resource=ResourceRef(ScopeType.ENVIRONMENT, env.id))` **in the handler**, never a bare
     `requires(...)` (RL-1301 B.2). Add this route to Task 0A's `HANDLER_GUARDED` with its
     file:line **in this commit**, so the sweep stays green by knowing it, not by skipping it.
  3. Load the Rating Version; refuse unless `approved`.
  4. **Approval-gated target** (it has a `deployment` policy entry; `prod` by default):
     require `deployment_request_ref` naming an **approved** request for this version and this
     Environment's identity, else 409 `DEPLOY_REQUIRES_APPROVAL`; re-evaluate
     `promotion_order_refusal` from the request's **pinned** evidence, never a re-read source;
     a reason → 409 `PROMOTION_ORDER_VIOLATION`. **The skip, if any, is the one pinned on the
     approved request; the deploy body takes no `skip`** (RL-1301 A.5). **Mark the request
     `executed` exactly once** (auditor-plans F5): a conditional `UPDATE deployment_requests
     SET status = 'executed' WHERE id = :id AND status = 'approved' RETURNING id` in the
     deploy's transaction; no row returned → 409 `DEPLOY_REQUIRES_APPROVAL` ("the request is
     not approved, or has been executed"), and no Deployment is written.
     **Ungated target:** no request; the predicate reads the predecessor's successful
     Deployment directly, and no skip is possible (RL-1301 A.5); a reason → 409
     `PROMOTION_ORDER_VIOLATION`.
  5. Insert the Deployment row and `audit.record(... action="deployment.created",
     before=<the previous live Deployment or None>, after=<this one>)` in **one**
     transaction.
- [ ] `GET /api/v1/environments/{env}/deployments`: history, newest first, cursor-paginated
  as the neighbouring list routes are.
- [ ] **Acceptance 8, this permission (Branch A)** *(PL-1392, C2)*: empty the
  `deployment:promote` `Check owner` cell (`06:283`) **in this commit**, the one that adds the
  handler's `rbac.require_permission(..., permission=Permission.DEPLOYMENT_PROMOTE, ...)`.
  Acceptance 8's predicate prints 0; as Task 4, the parity test and its red if `SL-1360` has
  merged.
- [ ] **Route types, rows 5–7 and row 9** *(PL-1392, C1)*: red first, Acceptance 14 and 15
  over rows 5–7, with the route-set pin widened to all 7; and Acceptance 16 for row 9
  (`POST /api/v1/approval-requests`): `SubmitApproval` moved to `model-schema` as
  `ApprovalSubmission` (slug `approval-submission`); the 2xx unchanged (DP-S2-6 (c)), with
  Acceptance 18's characterisation test red first.
- [ ] The red-on-broken-input runs: G3 type check, blanket-skip validator, audit call, the
  handler's `resource=` argument (RL-1301 B.5), the floor-item check (RL-1301 A.4), and the
  deployment-request plant (Acceptance 13), each against Slice 2a's trigger.
- [ ] Green; commit.

### Task 5A: The compile guard, as RL-1379 rules (FD-1393; DP-S2-7) — placeholder *(PL-1392, C14)*

**Files:** Modify `backend/src/app/platform/rating_versions.py` (`compile_rating_version`,
`:395-542`) and, if the ruling needs it, `backend/src/app/api/models.py` (the compile route,
`:1233`; not the governance gate's `_fetch_bundle` call at `:1215`, which stays read-only,
Acceptance 17); tests as the ruling names.

- [ ] **Not executable until RL-1379 is ruled and minted** (activation need 3a).
  The lead fills this task by a dated delta naming the ruled option and its cases.
- [ ] Red first, run: each case of Acceptance 19, with its predicted cause.
- [ ] Green; commit. **S2 does not merge without this task's commit.**

### Task 6: Default-live scoring, the trace link, and server-derived liveness (RL-880, RL-888, RL-916, FR-357)

**Files:** Modify `backend/src/app/api/score.py` (`_required_ref`, the `score` handler `:307`
and `_maybe_sample_trace` `:420`; **not** `_fetch_bundle` or `_compiled_for`, *(PL-1392, C3)*),
`backend/src/app/platform/traces.py`, `backend/src/app/api/approvals.py` (`Withdraw` moved out,
`withdraw_request`), `packages/model-schema/src/model_schema/approvals.py` (`ApprovalWithdrawal`),
`scripts/generate-contracts.py` (`approval-withdrawal`); tests `backend/tests/test_score.py`,
`backend/tests/test_traces.py`, `backend/tests/test_api_approvals.py`,
`backend/tests/test_deployment_route_types.py`. **Read-only:** `backend/src/app/api/models.py`
(`:1215`), `backend/src/app/worker/scoring_handlers.py`, `backend/src/app/worker/trace_handlers.py`
(Acceptance 17).

- [ ] Red first: Acceptance 6's three cases and Acceptance 7's trace cases.
- [ ] `_required_ref`: with no ref and a caller environment, resolve that environment's live
  Deployment for the caller's workspace; with none, or with no caller environment, keep the
  409. Update its docstring's "until then" sentence with a dated note, not by deletion.
- [ ] **Trace (RL-1380; #974):** resolve the Deployment **once**, together with
  the ref and before the bundle, "when the ref and bundle are resolved, before scoring"
  (RL-1380's Mechanics, first bullet): for a default-live quote, the Deployment that served
  it; for an explicit ref, the caller environment's live Deployment if its Rating Version
  equals the ref exactly, else null. *(PL-1392, C3, F-B1.)* **Where:** in the `score` handler
  (`backend/src/app/api/score.py:307`), at the step where `_required_ref` is called today
  (`:325`), by a new helper beside `_required_ref` that returns the ref and the Deployment id
  (or null) together. `_compiled_for` (`:326`) is then called with that ref, unchanged.
  **Never inside `_fetch_bundle`** (`:163`): its signature and its `CompiledBundle` return stay
  as they are, because the governance gate (`backend/src/app/api/models.py:1215`, which
  deliberately calls `_fetch_bundle` and not `_compiled_for`, `:1212-1214`) and, through
  `_compiled_for` (`:230`, which calls `_fetch_bundle` at `:252`), the two workers
  (`backend/src/app/worker/scoring_handlers.py:208`, `backend/src/app/worker/trace_handlers.py:82`)
  would otherwise change with it. Those three files are read-only (Acceptance 17).
  `/score/compare` (`:371`) and `/score/batch` (`:511`) keep the explicit ref only: default-live
  scoring is Acceptance 6's `/score` case and nothing wider.
  Pass that value to the trace write in `backend/src/app/platform/traces.py`; never re-read
  it at write time. Written with the pending row, never back-filled (`UPDATE` is revoked on
  `scoring_traces`, #974).
- [ ] **Carry the link across completion (#974 F1).** `complete_pending_trace`
  (`backend/src/app/platform/traces.py:198-271`) deletes the pending row (`:266`) and
  inserts the finished one at the same id; the insert copies `deployment_id` from the
  pending row. Red first (Acceptance 7): a sampled default-live trace, completed, still
  carries its Deployment id. Predicted red: the completed row's `deployment_id` is null
  because the re-insert does not copy it.
- [ ] `withdraw_request` — **the owner of auditor-928's client-supplied-liveness finding**
  (cited as prose until it is filed; the maintainer's entry headed
  `2026-09-30 11:12:45 BST — #973 (WK-674 S2 plan): (a) agreed; (b) its own FD, plus a class sweep`,
  item (b)). If that finding's class sweep places further instances here, the lead adds them
  by a dated delta. Derive liveness from Deployment rows for a `rating_version` ref.
  Remove `Withdraw.artifact_is_live`; update `test_api_approvals.py:520` (`test_withdrawing_after_deployment_is_refused`; its payload `:535`) to plant a real
  Deployment instead of sending the flag. **Red first:** a client omitting
  `artifact_is_live` for a version with a Deployment is refused with 409
  `WITHDRAW_AFTER_DEPLOY_FORBIDDEN`; a client still sending `artifact_is_live: false` is
  refused with 422 `VALIDATION_FAILED` naming the field *(PL-1392, C11: PL-1306 said 409 for
  both)*. Predicted red before the change: both withdrawals **succeed**, because the route
  trusts the body.
- [ ] **Route types, row 8** *(PL-1392, C1)*: Acceptance 16 for
  `POST /api/v1/approval-requests/{request_id}/withdraw`. The body becomes `ApprovalWithdrawal`
  in `model-schema` (`reason` only, slug `approval-withdrawal`), the backend `Withdraw` class
  is removed, and the 2xx is unchanged (DP-S2-6 (c)). Red first, as Acceptance 16 and 18
  state.
- [ ] Green; commit.

### Task 7: The gate and the ledger

- [ ] `tests/test_repository_invariants.py`, the migration round trip, then the full two-half
  gate on the committed tree, **inside a gate slot** (`flock -w 1800 -E 99 /tmp/slots/gate-1
  <cmd>` or `gate-2`, no `--`; Acceptance 10), with `uptime` recorded at the grant. Quote every rc, the `N passed` line and `HEAD` against main's
  `N passed` (a total that did not move means the new tests were never collected).
- [ ] The ledger records: the tree; premises a–u; the red-first and broken-input quotes; DP
  resolutions with their record ids; Acceptance 8's predicate outputs and the SHA it read;
  Acceptance 14–16's reds; Acceptance 17's two commands and their output; the Write set
  check as run at dispatch; FR-272's notification carried to WK-688.
- [ ] Item 11 (Acceptance 11).

## Hand-off

Slice 3 (environment isolation) starts after this slice closes and is gated by `OQ-1235`. It
reads this slice's `EnvironmentRow` for per-environment keys and settings. Slice 5 replaces
Task 6's per-request resolution with the switch, and reuses Task 5's route shape for rollback.

## Self-review

- **Slice size — ACCEPTED as option (b)** by the maintainer's entry headed
  `2026-09-30 11:48:28 BST — DECISION + ACCEPTANCE (maintainer by delegation): WK-674 S2 split, option (b), S2a = the approval guard`;
  applied by the dated delta in **Status**, with Slice 2a filed as PL-1303 (working ids SL 9922,
  PL 9923). The assessment as filed follows (auditor-plans' note on `39d94efe`). Task 3A (the approval guard, its session registration or
  trigger migration, the vocabulary declarations, 17 fixture files and the demo seed) is
  cross-cutting: it touches every approval-capable table and most of the backend test suite,
  and is independent of Environments and Deployments except that `deployment_requests` joins
  its population. With it, this slice is well beyond `PL-1237`'s slice band. Options:
  - **(a) Keep it in S2.** One slice, one audit; the deployment-request plant is proved
    where the table is born. Cost: the largest diff of the Work, and the widest serialisation
    footprint (the 17 test files and `session.py` against every in-flight slice), for the
    whole of S2's build.
  - **(b) Split out S2a, the approval guard, landing before S2** (Task 3A plus the
    validation `StrEnum` and the exemption; the deployment-request plant stays S2's,
    proved when S2 declares that table's vocabulary). S2a is independent of RL-1301's
    deployment items and can build while S2's remaining questions settle; S2 shrinks to the
    Environment and Deployment record. Cost: one more slice row, leaf plan and audit, and
    S2's Acceptance 13 reduces to "`deployment_requests` joins the population and is
    refused", red first.
  - **(c) Split S2a as the guard plus Task 0A** (the authorisation sweep). Both are
    cross-cutting test-and-guard work with no new route, and both must precede S2's routes.
    Cost: as (b), and it moves the maintainer's "S2's first task" (the 11:01:50 entry) into a
    different slice, which the maintainer would have to accept.
  - **Recommendation: (b).** It separates the one piece of S2 that is not about Environments
    and Deployments, keeps Task 0A where the maintainer placed it, and shortens S2's
    serialisation window. The maintainer leans yes (the entry headed
    `2026-09-30 11:45:55 BST`, item 1): the guard hardens the 7 existing approval tables, and
    the validation-rule fix depends on it, so it lands first and S2 then adds
    `deployment_requests` to the guarded set.
    - **Owner: WK-674 S2a**, not WK-1178. Under RL-1263 two build slices may run together
      only from different Works, so a WK-1178 owner would queue the guard behind, or ahead
      of, WK-1178's own two slices (#977's §5.1 Permission column and the validation-rule
      fix), which then run one at a time. As WK-674 S2a, the guard and #977's column slice
      are in different Works and share no file (the guard touches no spec table; the column
      slice touches only `docs/specs/*` §5.1), so they may hold the two slots together once
      a slot is free.
    - **Slots:** S2a takes lane A, the slot S2 would have taken. WK-690 S1 holds lane B and
      touches `packages/pricing-core`, `02`, `03` FR-244, the pyprojects and `uv.lock`; S2a
      touches none of those, so the two may overlap. The first overlap triggers the
      three-pair contention measurement (the 10:05:40 entry), and every full run takes a
      gate slot (the 11:42:08 entry). S2 follows S2a in lane A.
    - **Serialisation, path by path:**
      - `backend/src/app/db/session.py` (listener registration): S2a only;
      - `backend/src/app/db/models.py` (the `status_vocabulary` declarations on existing
        classes): S2a; S2 then only appends classes, which is registry-exempt;
      - `backend/src/app/api/approvals.py` (`_carry_to_the_artifact`): S2a enters the
        context there, S2 adds the deployment branch, and the validation-rule fix adds the
        validation branch — **three slices on one function, strictly in sequence**: S2a,
        then S2 and the fix in the order the lead sets (the 11:23:26 entry puts the fix after
        S2) *(2026-09-30: decided as S2a → the fix → S2 by the 11:56:33 BST entry; see
        **Status**)*;
      - `backend/src/app/platform/approvals.py`: S2a (`approval_decision()`, `decide`), S2
        (`set_policy`'s Environment check), the fix (routing rule approval through
        `submit`/`decide`) — the same sequence;
      - the 17 fixture files: S2a only. Any in-flight slice editing one of them serialises
        with S2a; S2's own tests are new files, apart from `test_api_approvals.py`, which is
        not among the 17;
      - `backend/migrations/versions/`: S2a's trigger revision and S2's revision are both
        appends. The later one re-points `down_revision` at its merge, and **S2's revision
        extends the trigger to `deployment_requests`** in the same migration that creates
        the table;
      - #977's column slice: no overlap with S2a; it serialises with S2, and S2's new routes
        are declared by whichever lands second. A split is a replan: the lead decides it, and if chosen the planner
    cuts the new `SL-` row (`draft`) and files S2a's leaf plan, with this plan re-cut by a
    dated delta.

- **Scope against the map plan and the spec.** FR-267, FR-428, FR-429, FR-272 (deploy audit
  limb), NFR-498 (deploy limb), FR-347 (negative test), FR-357 (the state it needs) are each
  listed individually. `PL-1237` Task 2's gate outline maps to Acceptance 4 item by item:
  missing approval, skipping `uat` on one predicate, non-Deployer, `uat`-only Deployer, no
  Audit Event on broken input, non-Admin environment lifecycle, Service Account, absent
  policy entry; `generate-contracts.py --check` (Acceptance 2); the trace relationship on
  existing rows (Acceptance 3); the full gate (10); item 11 (11).
- **The five conditions the lead relayed**, each at every site class (narrative, Files,
  Steps, Acceptance):
  1. blanket skip and fallback — Global Constraints, Task 2 second commit, Task 5, Acceptance 4;
  2. `STALE_OWNER`, both branches — Scope, Tasks 0, 4 and 5, Acceptance 8;
  3. G3 — Scope, Task 1, Task 5 step 1, Acceptance 4;
  4. RL-1263 write set, `uv.lock`, `03` §5.1, contention — Global Constraints, Write set, Task 0;
  5. #960 before dispatch — Status.
  6. A1, the authorisation sweep, first — Task 0A, Write set, Acceptance 12; and the
     single writer of `approved` over every approvable table — Acceptance 13, Task 5.
- **auditor-plans' audit of `fdde72a2`, F1–F9**, each closed at its sites: F1 by RL-1301 A.6
  (Task 4, Acceptance 4); F2 Acceptance 13; F3 Task 5 step 6 and Acceptance 4; F4 Task 5
  step 5 and Acceptance 4; F5 Task 5 deploy step 4 and Acceptance 4; F6 Task 0A (d); F7
  Acceptance 12 (e); F8 the predicate (Task 2); F9 the dated deviation paragraph and `RL-1296`.
- **RL-1301 at `327e1179` and #977**, applied at their sites: A.4 restated (~~Acceptance 13, Task 3
  vocabulary step, Write set~~ — superseded by the `80afeb40` guard, below); A.6's credentials (Task 4, Acceptance 4, Write set); the
  deployment-wide confirmation (Decided in this plan); DP-S2-5 closed; DP-S2-4 ruled (a) by
  #977 (DP table, Acceptance 12 (c), Write set).
- **RL-1301 at `80afeb40` (A.4 as a runtime guard; still under audit)**: ~~Acceptance 13, Task 3A,
  Write set~~ — moved to Slice 2a (PL-1303) by the split; this plan keeps only Acceptance 13's
  `deployment_requests` item. The AST attribution, the value widening and the per-site rows of earlier
  revisions are removed. auditor-plans' V1 dissolves under it, and V3 is this re-citation.
  Written to hold under auditor-close1255's M1 (the module-independent required set, with
  `peril_structures` guarded) and M2 (the context spans the write and its flush), which the
  decision-maker is carrying into RL-1301's next head; this plan cites that head when it lands.
- **The gate-slot rule** (the 11:42:08 entry, tightened at 11:43:28): Acceptance 10, Task 0,
  Task 7 (Task 3A's site moved to Slice 2a).
- **auditor-plans N1–N3** (its audit of `a79fc6b4`): N1 and N2 Task 4 and Acceptance 4, with
  the Task 3 constraint; N3 Task 4 and Acceptance 4. Its G1 is Acceptance 13's declared
  vocabulary, now RL-1301 A.4 at `80afeb40`: declared on the approval-capable tables only, which
  is what links a `String` status column (`models.py:667-670`, `:1242-1245`, `:1960-1963`) to its enum.
- **Each ruling applied where it operates.** RL-1296 items 1 (Task 2 validator), 3
  (`PromotionSkip`, pinned on the Deployment Request as RL-1301 C amends it), 4 (the predicate's place, Acceptance 5), 5 (one commit, Task 2),
  6 (no new permission: `set_policy` stays the grant path, nothing added); its Acceptance
  bullets are Acceptance 4's FR-429 cases and Acceptance 5.
- **Literals** were checked against the tree above (premises); names the executor adds
  (`skippable_predecessors`, `PromotionSkip`, `promotion_order_refusal`, the modules and
  tables) are proposals, named once.
- **RL-1301 applied at every site class** (the 2026-09-30 revision): A.1 (Task 1 spec, Task 2
  `refs.py`, Task 3 table, Decided-in-plan slug), A.2 (Task 1, Task 3 `evidence`, Task 5
  submission), A.4 (Acceptance 4 and 13, Task 5), A.5 (Acceptance 4, Task 5 deploy step 4),
  B.1–B.5 (Task 2, Task 1 FR-345, Task 5 step 2, Task 0A allow-list, Acceptance 4), C
  (`PromotionSkip`'s home). The DM's check-back on this revision ("consistent" or a dated
  delta) is the 11:11:25 entry's condition; its answer on `22cb24b3` was "consistent", with
  four wording gaps (the pinned skip at the route, the request row's slug and identity, the
  model-derived one-writer check with its baseline, and Task 1's FR-345 amendment), each
  closed in the revision after it, with RL-1301's audit advisories A2–A5.
- **Open: none that blocks this slice** *(as PL-1306 filed it; PL-1392 adds DP-S2-6, blocking)*. DP-S2-1 (#974), DP-S2-2 and DP-S2-3 (RL-1301 A–B) and
  DP-S2-5 (disposed by RL-1301 A.6 at `80afeb40`) are settled; DP-S2-4 is ruled by #977 (working id 9907) and, by the 11:17:35
  entry, does not block this slice. The plan goes `active` on the lead's go once
  RL-1301 and #974 are minted. *(PL-1392: RL-1301 is minted; #974 is not; and DP-S2-6 is new
  and open, so activation need 2 is the one open need.)*
- **Placeholder scan**: no step says "per DP-S2-n" any more; nothing is deferred except
  Task 0A (c), which is another slice's.

### Self-review of this superseding plan (PL-1392, 2026-10-01)

- **Every change has a source and a site.** C1–C18 (**Changes from PL-1306**) each name the
  maintainer's entry or audit finding behind them and the sections they touch. Each site is
  marked *(PL-1392)* in the body. Nothing else in `PL-1306`'s content was changed.
- **The three accepted acceptance items are 14, 15 and 16**, each red first on broken input
  with its predicted cause. The 7 routes are enumerated with method and path (**Route
  table**), as the 10:10:46 entry requires. Each route names its request type (or none) and
  its 2xx type. Rows 8 and 9 give what the 2 changed routes declare today and after.
- **A disagreement found, not hidden, and not picked** (C12). Writing Acceptance 16's 2xx
  half, I read what the two changed routes return (`service.to_dict`,
  `backend/src/app/platform/approvals.py:648-673`) against `ApprovalRequest` and the
  hand-authored `approval-request.schema.json`. The three disagree, so the literal item ("typed
  the same way") cannot be met without a §0 reconciliation. DP-S2-6 records three options and
  recommends (c), bodies only in S2. That recommendation narrows what the maintainer accepted,
  so it is flagged for the maintainer, not assumed. The reading is static (no environment was
  run at the root); the executor's red-first run is what confirms it. *(2026-10-01: the
  maintainer accepted (c); C13 applies it, with Acceptance 18.)*
- **F-B1 is a constraint with a check** (Acceptance 17), not prose: two `git diff` commands
  whose expected output is empty.
- **Branch A is checked by a predicate that was run** at the tree above (it printed 2), not
  by a description of the table.
- **Every count carries its predicate** (`CLAUDE.md` §13): the 141 operations (Acceptance 12
  (a)), the `Check owner` cells (Acceptance 8), the class counts (Acceptance 2), the Alembic
  head (premise o), the §4 numbering (premise p).
- **Locators re-derived at `1dd5e264`**, by a read-only sweep of every locator `PL-1306`
  cites. Two were already wrong at `PL-1306`'s own tree and are corrected, not treated as
  drift: `PROMOTION_ORDER_VIOLATION` is `07`'s (`07:344`), not `03:778`; and the
  `require_in_review` call is `rating_versions.py:358`, not `:357`. Locators inside quoted
  history (dated notes and the self-review of `PL-1306` above) are left as written, except
  where a line names current code.
- **Still open:** activation need 2 (#974 merged and minted, batch C) and need 4 (the lead's
  go), and **need 3a, RL-1379 (DP-S2-7, blocking the merge)**. Need 1 and need 3 hold. DP-S2-6
  is decided (c) (C13, applied pre-merge).
