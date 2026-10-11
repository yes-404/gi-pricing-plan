---
id: FD-1510
family: finding
title: The approval withdraw route takes artifact_is_live from the request body, so the client asserts a fact the server must derive
status: closed
created: 2026-10-08            # original date 2026-09-30, set at the draft; minted 2026-10-08
owner: auditor
tree: 65b334792e65704206d2c21015690d7c613092cc
corrected_by: []
relates: [WK-674]
---

# FD-1510 — The approval withdraw route takes artifact_is_live from the request body, so the client asserts a fact the server must derive

## Amendment before mint (2026-10-05)

Amended 2026-10-05 before mint, at `47d770e8`: **the main defect is fixed** by `dfddfad8` (#1104, SL-1256, PL-1392 Task 6; ledgered in `LG-1405`). `withdraw_request` derives liveness server-side through `_is_deployed` (`backend/src/app/api/approvals.py:257`, called at `:299`); `artifact_is_live` is no longer a request-body field and remains only as the service's keyword argument (`backend/src/app/platform/approvals.py:500`); `backend/tests/test_api_approvals.py:565-576` shows a body carrying it refused 422. **Still open, owner WK-1178:** the class-sweep table below (the only enumerated record of client-asserted fields) and the LOW service-account residual — `ALLOWED_PERMISSIONS` (`backend/src/app/api/service_accounts.py:44`) and `_check_permissions` (`:141`) are unchanged at main, so a custom role with `admin:manage_service_accounts` and without `admin:manage_roles` can still mint a scoring service account. Every `file:line` cite in the sections below is to tree `65b334792e65`, before #1104 moved them; read them by symbol (`Withdraw`, `withdraw_request`, `platform.approvals.withdraw`), not line.

**Closed 2026-10-08, re-measured at `origin/main` `d10420df`** (`git merge-base --is-ancestor dfddfad8 origin/main` exits 0; `dfddfad8` = #1104, merged 2026-10-04 15:48:09Z). Cites at that tree: `_is_deployed` `backend/src/app/api/approvals.py:274`, called at `:316` and passed at `:323`; the body model is `ApprovalWithdrawal` (`packages/model-schema/src/model_schema/approvals.py:380`, reason only); the service keyword is `backend/src/app/platform/approvals.py:500`; the refusal test is `backend/tests/test_api_approvals.py:565` (`test_a_client_can_no_longer_assert_that_the_artifact_is_not_live`). The earlier cites in this essay (`:257`, `:299`) were read at `caa4e411` and have since moved. **The LOW service-account residual is not closed by this**: it stays open in the register row, owner WK-1178 (`ALLOWED_PERMISSIONS` `backend/src/app/api/service_accounts.py:44`, `_check_permissions` `:141`, unchanged at `d10420df`).

## Finding

**Severity: medium** (a latent trust-boundary defect; **not high**, because nothing can be "live" or
in use behind a withdrawable approval today; see "Severity test"). The withdraw route
(`POST /api/v1/approval-requests/{id}/withdraw`) takes `artifact_is_live` from the HTTP request
body (`backend/src/app/api/approvals.py:90-98`, passed at `:288`), and the service refuses the
withdrawal only when that flag is `true` (`backend/src/app/platform/approvals.py:435-460`, the
`WITHDRAW_AFTER_DEPLOY_FORBIDDEN` refusal). **The client therefore asserts liveness**, the one fact
FR-357 makes the guard (*"it cannot be withdrawn after the artifact is live"*), and the flag's
default is `false`. The server derives nothing. Found by planner-924 while writing the WK-674
Slice 2 leaf plan (#973, PL working id 9920), and filed on the maintainer's entry
`to-lead.md` "2026-09-30 11:12:45 BST — #973 (WK-674 S2 plan): (a) agreed; (b) its own FD, plus a
class sweep".

## Evidence

Measured at `origin/main` `9f63d0fe`; `git diff --stat 9f63d0fe 65b33479 -- backend/src
packages/model-schema/src` is empty, so the same code is at `65b33479`, this record's tree.

**1. The route and what the service does with the flag.** `withdraw_request`
(`api/approvals.py:278-299`) calls `service.withdraw(..., artifact_is_live=body.artifact_is_live)`
inside a unit of work, then `_carry_to_the_artifact`. `service.withdraw`
(`platform/approvals.py:435-490`) loads the request, raises `WITHDRAW_AFTER_DEPLOY_FORBIDDEN` (409)
if the flag is `true`, checks the reason and the `APPROVAL_DECIDE` permission, then
`_require_transition(status, WITHDRAWN)`. `VALID_APPROVAL_TRANSITIONS`
(`packages/model-schema/src/model_schema/approvals.py:62-76`) lets both `review` and `approved`
move to `withdrawn`. So **an approved request can be withdrawn**, and the flag is the only
liveness input. The flag can only make the route stricter: `true` refuses (the existing test
`backend/tests/test_api_approvals.py::test_withdrawing_after_deployment_is_refused`), `false`, the
default, does not.

**2. Severity test: what withdraw does to an approved request, with `artifact_is_live: false`,
per approvable type.** A throwaway test (not committed) drove the real routes with `TestClient` on
a per-worktree database (`gipricing_auditor-fd_35f4ea9e`, migrated to head): create the artifact in
its review state, submit, approve, then withdraw with `artifact_is_live: false`. For `model` the
fixture model `model:motor-ad-frequency@7` was used, with an approved rating version pinning it
(`model_ref`).

| Type | Withdraw of the approved request | Request afterwards | Why |
|---|---|---|---|
| `model` (approved, pinned by a rating version) | **409** `VALIDATION_FAILED` | stays `approved` | the model's decision hook cannot move `approved` to `fitted` |
| `custom_objective` | **409** `VALIDATION_FAILED` | stays `approved` | the same, in `objectives.apply_approval_decision` |
| `custom_metric` | **409** `VALIDATION_FAILED` | stays `approved` | the same, in `metrics.apply_approval_decision` |
| `rating_version` | **409** `APPROVAL_SUBJECT_NOT_IN_REVIEW` | stays `approved` | `rating_versions.apply_approval_decision` calls `approvals.require_in_review` (`:358`) on the locked row |
| `peril_structure` | **200** | `withdrawn` | no decision hook; the artifact is untouched (it stayed `review`) |
| `validation_rule` | **200** | `withdrawn` | no decision hook; the artifact is untouched |
| `dataset_version` | **200** | `withdrawn` | no decision hook; the artifact stays `validated` |

**Reading it.** For the four types with a decision hook, the owning module's own state refuses the
withdrawal of an approved request **whatever the flag says**, so the flag is not what protects a
pinned model or an approved rating version today. For the three types without a hook, a client
can withdraw an approved request and **only the approval record changes**: nothing reads an
approval request's status to decide whether an artifact may be used (`git grep ApprovalRequestRow`
outside `platform/approvals.py` and `api/approvals.py` finds only the four hooks and the
submit-side helpers). **Nothing can be live today**: `RatingVersionStatus.LIVE` is declared but its
transitions belong to WK-674 (`packages/model-schema/src/model_schema/rating.py:31-41`), and there
is no Deployment. So **no client can withdraw an approval that governs something live or
in use today**, and the severity is **medium, not high**. This is not measured after S2: once a
Deployment exists, liveness must be derived by the server, because for a type with no hook the
flag is the only guard and its default is off.

**3. Class sweep, same record.** *Question:* which request bodies accept a field the server must
derive: liveness, status, approval state, owner or `created_by`, `workspace_id`, timestamps?

*Predicate, runnable* (from the repository root at `65b33479`, `python3 script.py`; the request
models are the parameters of every route function, decorated `.get`, `.post`, `.put`, `.patch` or
`.delete`, in `backend/src/app/api/*.py` whose annotation names a class defined in
`backend/src/app` or `packages/model-schema/src`, excluding `Query`, `Path`, `Header`, `Depends`,
`Request` and `Caller` parameters; nested classes are followed; a hit is a field whose name
matches the `DERIVED` pattern):

```python
import ast
import re
import subprocess

roots = ["backend/src/app", "packages/model-schema/src"]
files = [f for f in subprocess.run(["git", "ls-files", *roots], capture_output=True, text=True, check=True).stdout.split("\n") if f.endswith(".py")]
classes, trees = {}, {}
for f in files:
    try:
        tree = ast.parse(open(f, encoding="utf-8").read())
    except SyntaxError:
        continue
    trees[f] = tree
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            fields = {st.target.id: (st.lineno, ast.unparse(st.annotation)) for st in node.body
                      if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name)}
            classes.setdefault(node.name, []).append((f, node.lineno, fields))
DERIVED = re.compile(
    r"^(status|state|is_live|live|artifact_is_live|approved|approval_state|approved_by|approvers?|owner|owner_id|created_by|"
    r"authored_by|author|submitted_by|decided_by|actor|principal_id|user_id|workspace_id|tenant_id|created_at|updated_at|"
    r"decided_at|submitted_at|withdrawn_at|deployed_at|at|id|hash|content_hash|spec_hash|checksum|role|roles|permissions|"
    r"is_admin|admin|superseded_by|retired|is_active|active|version|slug|deleted|deleted_at|source|kind)$")
ROUTE = {"get", "post", "put", "patch", "delete"}
request_models = {}
for f, tree in trees.items():
    if not f.startswith("backend/src/app/api/"):
        continue
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(
                isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr in ROUTE
                for d in node.decorator_list):
            for a in node.args.args + node.args.kwonlyargs:
                if a.annotation is None:
                    continue
                src = ast.unparse(a.annotation)
                if any(k in src for k in ("Query(", "Path(", "Header(", "Depends", "Request", "Annotated[Caller", "Cookie(")):
                    continue
                for name in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", src):
                    if name in classes and name not in ("Annotated", "Field"):
                        request_models.setdefault(name, []).append((f, node.name, node.lineno))
seen = set()
def walk(name, path):
    if name in seen or name not in classes:
        return
    seen.add(name)
    for f, ln, fields in classes[name]:
        for fld, (l, ann) in fields.items():
            if DERIVED.match(fld):
                print(f"{f}:{l}  {name}.{fld}: {ann}   [via {path}]")
            for nested in re.findall(r"[A-Z][A-Za-z0-9_]*", ann):
                if nested in classes and nested != name:
                    walk(nested, path + ">" + name)
print("request models:", len(request_models))
for name, uses in sorted(request_models.items()):
    walk(name, f"{name} ({uses[0][0].split('/')[-1]}:{uses[0][2]} {uses[0][1]})")
```

Result: **39 request models, 25 hits.** No request model has a `workspace_id`, `created_by`,
`author`, timestamp (`created_at`, `decided_at`, …), `status` or approval-state field. Triage,
each with file:line:

| Hit | Triage |
|---|---|
| `api/approvals.py:94` `Withdraw.artifact_is_live` | **has an effect** (this record) |
| `model_schema/modelling.py:354, 357` `Banding.id`, `.version`; `:507, :510` `Grouping.id`, `.version` | **server-derived and ignored**: `create_banding` and `create_grouping` (`platform/transformations.py:258-380`) allocate the version themselves (`1 + max(version)`) and dump the body with `exclude={"id", "version", "dataset_id"}` |
| `modelling.py:355, 508`, `custom_metrics.py:91`, `custom_objectives.py:98`, `peril_structures.py:80`, `service_accounts.py:61`, `datasets.py:128`, `models.py:207, 274`, `validation.py:85`, `datasets.py:104`, `reference_tables.py:65`, `refs.py:71-72` `slug`, `version` | **client-chosen names and references by design** (the artifact's own name, or the ref it pins) |
| `custom_metrics.py:92`, `custom_objectives.py:99`, `datasets.py:105`, `perils.py:151` `kind` | **client-chosen type by design** |
| `datasets.py:147` `OwnerUpdate.owner_id` | **has an effect, gated**: the client names the new owner, and `set_owner` applies FR-82's rule (Admin or the current owner; `api/datasets.py:459-` docstring) |
| `service_accounts.py:64` `CreateServiceAccount.permissions` | **client-chosen, gated; no escalation for the built-in roles; a LOW residual for a custom role** (analysis below the table) |

**`CreateServiceAccount.permissions`, analysed** (the maintainer's entry `to-lead.md`
"2026-09-30 11:25:33 BST — #976's service-account item: LOW (recorded); perils: LOW FD with a
named owner and a tripwire"; each premise read on code):

- **Creation requires `ADMIN_MANAGE_SERVICE_ACCOUNTS`** (`api/service_accounts.py:40`;
  `model_schema/permissions.py:70`).
- **Grants are capped** at `ALLOWED_PERMISSIONS`, the fixed frozenset `{"score:execute",
  "score:batch"}` (`:44`); `_check_permissions` (`:128-137`) refuses anything else with 422 before
  the row is written.
- **No built-in role holds either scoring permission.** `SCORE_EXECUTE` and `SCORE_BATCH`
  (`permissions.py:58-59`) appear in no `BUILTIN_ROLES` entry (`:124-149`) and not in
  `READ_PERMISSIONS` (`:79-87`): scoring is service-account-only by design (FR-389, `07:73`;
  FR-347, `06:83`).
- **The built-in `admin` role holds `ADMIN_MANAGE_ROLES`** (`:144`) beside
  `ADMIN_MANAGE_SERVICE_ACCOUNTS` (`:147`), so it already controls who holds what: **no real
  escalation for the built-in roles.**
- **Measured by auditor-924d** at `65b33479` with the built-in admin role: a service account
  requesting `score:execute` gives **201**, `score:batch` gives **201** (Admin holds neither),
  `audit:read` gives **422** (Admin holds it) and `approval:decide` gives **422**. **Admin can
  mint a scoring credential it cannot use itself**: by design under FR-389 and `06` FR-347, and
  capped by `ALLOWED_PERMISSIONS`. Not re-run by this record's author.
- **Residual, LOW, recorded here, owner WK-1178:** a **custom role** holding
  `admin:manage_service_accounts` but not `admin:manage_roles` could mint a scoring service
  account, a power it lacks itself. Narrow, no governance effect, and it needs a deliberate
  custom role. It is recorded, and it is not stated as "not escalation".

**By eye, from the full field list of the 39 models** (not matched by the pattern):

- `Banding.band_stats`, `Banding.derived_on_dataset_version_id`, `Grouping.evidence`
  (`GroupingEvidence`: deviance, `chi2_p_value`, credibility components) and
  `LargeLossTreatment.evidence_blob`: **client-supplied evidence persisted as supplied**
  (`transformations.py:287` and `:345` store `model_dump` of the body), not recomputed
  or verified. `git grep` finds no reader that gates a decision on them; the effect is on the
  record and the generated model document, not on an approval or a price. **Not this record's
  fix**, listed for the maintainer's eye.
- `QuoteContext.quoted_at`, `effective_date`, `quote_id` and `options.rating_version_ref`
  (`model_schema/scoring.py:78-95`): **client inputs by design** (FR-216: "a quote timestamp is
  an input"). The client also **selects the rating version** it scores against, and the score route
  does not check `approved` or `live`: documented at `api/score.py:296-300` (WK-671 imposes
  neither of FR-251's restrictions; RL-880 clause 3). That is S2's default-live resolution, not a
  new defect.

**Second instance with an effect, on liveness, status, approval state, owner, workspace or
timestamps: none found.** The three "has an effect" rows above are the one in this record's title
and two client-named, service-gated values.

**Limits of the sweep:** it reads request models reachable from a route parameter's annotation, so
a body typed `dict` or `Any` (`UpdateSettings.values`, `VersionCreate.recipe`) is not analysed,
multipart and non-Pydantic inputs are not covered, and the `DERIVED` pattern is a name match: a
server-derived field with an unlisted name is missed (hence the by-eye pass). It is a listing at
one tree, not a proof for later commits.

## Disposition

**Deferred with an owner: WK-674 Slice 2, Task 6.** Event that discharges it: that task's merge.
Per the maintainer's entry: **server-derived liveness**, the `artifact_is_live` body field
removed (`api/approvals.py:90-98`; the field is also in the generated
`docs/contracts/openapi/generated.json`, which regenerates), and a **red-first test that a client
claiming "not live" on a live artifact is refused**. The measured table above is the starting
input: the same routes, for each type, must refuse a withdrawal of an approved request whose
artifact is live, whatever the body says, including the three types with no decision hook.

*Drafted under working id 9890.*

Re-anchored 2026-10-05 at main `caa4e411`: the main defect is fixed at main, by `dfddfad8`
(#1104; `git merge-base --is-ancestor dfddfad8 origin/main` exits 0). Read at that tree:
`withdraw_request` (`backend/src/app/api/approvals.py`) opens its unit of work with
`artifact_is_live = await _is_deployed(session, caller.workspace_id, request_id)` (`:299`) and
passes it to `service.withdraw(..., artifact_is_live=artifact_is_live)`; `_is_deployed` (`:257`)
returns true only for a `rating_version` request whose artifact has a `DeploymentRow`; the
body model is `ApprovalWithdrawal` (`packages/model-schema/src/model_schema/approvals.py:370`; reason only, `extra="forbid"`), and
`test_a_client_can_no_longer_assert_that_the_artifact_is_not_live`
(`backend/tests/test_api_approvals.py:565-576`) refuses a body carrying `artifact_is_live` 422.
`artifact_is_live` survives only as `service.withdraw`'s keyword argument
(`backend/src/app/platform/approvals.py:500`; the cite read `:491` at `47d770e8`). The LOW
residual is unchanged at main: `ALLOWED_PERMISSIONS` (`backend/src/app/api/service_accounts.py:44`)
and `_check_permissions` (`:141`). `PL-1408` (line 510) still cites this finding by working id 9890.
