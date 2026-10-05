---
id: FD-1416
family: finding
title: ApprovalRequest is defined three ways that disagree, and a hand-authored contract sits under docs/contracts/
status: active
created: 2026-10-05            # the mint date (check 31); filed 2026-10-01
owner: auditor
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
corrected_by: []
relates: [WK-1178, WK-674, FD-1335, FD-1356, PL-1306, RL-1301, RL-878, ADR-704, FR-451, OQ-649]
---

# FD-1416 — `ApprovalRequest` is defined three ways that disagree, and a hand-authored contract sits under `docs/contracts/`

**Filed under working id 9752; minted `FD-1416` on 2026-10-05.** The `tree:` is `origin/main` at
`1dd5e264`; every locator below was read at that tree. Raised by `PL-1392`'s (working id `PL 9765` when filed) DP-S2-6 (WK-674 Slice 2's superseding plan),
confirmed field by field by the auditor, and ordered by the maintainer's entry headed
"2026-10-01 10:32:26 BST — #1062 DP-S2-6: option (c) ACCEPTED with three conditions; it narrows my item (3) for the 2 CHANGED routes' 2xx only; the three-shape disagreement becomes its own FD"
(`to-lead.md`, a local channel file, so cited by its header).

## Finding

**Proposed severity: MEDIUM; owner WK-1178** (the maintainer sets severity). One concept, an approval request,
has three published definitions that disagree on field names, required fields and an enum's values.
`CLAUDE.md` §2 ("Nobody hand-writes a shape that already exists in `model-schema`… a shape defined twice will diverge")
is broken here three times over. It is a `CLAUDE.md` §0 spec/code disagreement, so which side is right is the
decision-maker's to rule, field by field, and is not this finding's.

The three shapes:

- **S1 — what the API emits.** `to_dict` (`backend/src/app/platform/approvals.py:672-697`, `to_dict` at `origin/main` `caa4e411a9c07a389cf47092a923c7761b2b92dc`; `:663-687` at `ef5dc6e7`, `:648-673` at the filing tree), returned by four routes.
- **S2 — the model.** `ApprovalRequest` (`packages/model-schema/src/model_schema/approvals.py:395`, `:275` at the filing tree; `frozen=True`,
  `extra="forbid"`) with `ApprovalDecision` (`:384`, `:264` at the filing tree).
- **S3 — the hand-authored contract.** `docs/contracts/schemas/approval-request.schema.json`, with `06` §4.3's example
  (`06-governance.md` §4.3, heading `:458` and its JSON example `:460-488` at `caa4e411`; `:447` and `:449-477` at `ef5dc6e7`, `:440-475` at the filing tree) as its prose twin.

> **Amended 2026-10-05 before mint:** citations re-anchored, no HOLD text changed. **`PL 9765` is
> `PL-1392`** (merged) and **`PL 9762` is `PL-1408`** (`status: draft`, activation PR #1112 open); a
> working id inside a quoted maintainer entry (the "Maintainer's decision" section below) stays as
> quoted. **#1104 (`dfddfad8`, `PL-1392`) landed as DP-S2-6 (c) planned:** `ApprovalSubmission` and
> `ApprovalWithdrawal` (`model_schema/approvals.py:355`, `:370`) now type the two request bodies of
> `submit_for_approval` and `withdraw_request`, and every 2xx of the four routes is still
> `dict[str, Any]`, so the owed work here is unchanged; `decide_request`'s body is still the
> hand-written `Decide` (`api/approvals.py:78`), typed by `PL-1408` DP-4 (a). **The three shapes still disagree at `origin/main`
> `ef5dc6e7317281ac9d1840fa61861597e3c1b8b1`:** S1 `to_dict` `approvals.py:663` emits `environment` and no
> `workspace_id`; S2 `ApprovalRequest` `:395`; S3 the hand-authored schema is byte-unchanged since the
> filing tree; `ApprovalRequest` has 0 hits in `docs/contracts/openapi/generated.json`;
> `backend/tests/test_contracts.py:97` still lists `"approval-request": "later-phase — 06 governance"`. Line
> cites below are given at the filing tree with the current one beside them; the field table was
> not re-measured (the fields of `ApprovalRequest`/`ApprovalDecision` are unchanged between the two trees).
>
> **Re-anchored again at mint, 2026-10-05, at `origin/main` `caa4e411a9c07a389cf47092a923c7761b2b92dc`, by symbol; no HOLD text changed.**
> `service.to_dict` is `backend/src/app/platform/approvals.py:672-697` (was `:663-687`; the body is unchanged: it still emits
> `environment`, no `workspace_id`, and the stored decision values). The four call sites in `backend/src/app/api/approvals.py` are
> still `:96`, `:140`, `:254`, `:312`; `Decide` is still `:78`. `ApprovalDecision` `:384`, `ApprovalRequest` `:395`,
> `ApprovalSubmission` `:355` and `ApprovalWithdrawal` `:370` in `packages/model-schema/src/model_schema/approvals.py`, and
> `ApprovalRequestRow.decided_at` (`backend/src/app/db/models.py:678`), `test_contracts.py:97` and the 0 hits of `ApprovalRequest` in
> `docs/contracts/openapi/generated.json` are unchanged. `06` §4.3 moved to `:458` (example `:460-488`; it still writes
> `"decision": "approved"`, at `:483`) because a paragraph was added above it for `RL-1362` DP-S3-4; that paragraph changes
> `approvers_required` for a non-convex Custom Objective at submission and does not touch the decision enum or any field of the table below.

### Field by field

"–" = absent. "req" = required.

| Field | S1 `to_dict` | S2 `ApprovalRequest` | S3 hand-authored schema |
|---|---|---|---|
| `id` | `str` | `UUID`, req | – |
| `workspace_id` | – | `UUID`, req | – |
| `artifact_ref` | `str` | `ArtifactRef` (a string on the wire), req | `$ref common/artifact-ref`, req |
| `artifact_type` | `str` | `str`, req | enum of 10 types, req |
| `environment` | `str \| None`, emitted | – (so S2 cannot hold what S1 emits) | – |
| `submitted_by` | `str` | `UUID`, req | uuid string, req |
| `submitted_at` | ISO string | `datetime`, req | date-time, req |
| `change_summary` | `str` | `str`, req | string, `minLength` 1, req |
| `status` | `str` | `ApprovalStatus`: draft, review, approved, changes_requested, rejected, withdrawn; req | same six values; req |
| `approvers_required` | `int` | `int` ≥ 1, req | `int` ≥ 1, req |
| `approvers_recorded` | `int` (count of `approve`) | `int` ≥ 0, req; a validator ties it to the `approve` decisions | `int` ≥ 0, req |
| `decisions[].approver_id` | `str` | `UUID` | uuid, req |
| `decisions[].decision` | stored value: `approve`, `reject`, `request_changes` | `DecisionKind`: `approve`, `reject`, `request_changes` | enum `approved`, `rejected`, `changes_requested` (`06` §4.3's example also writes `"approved"`) |
| `decisions[].at` | ISO string | `datetime` | date-time |
| `decisions[].comment` | `str \| None` | `str \| None`, default `None` | string, `minLength` 1, **req** |
| `withdrawn_reason` | `str \| None` | `str \| None` | – |
| `withdrawn` | – | – | `{by, at, reason} \| null`; `by` and `at` are stored nowhere |
| `evidence_bundle` | – | – | object, **req** |
| `checklist` | – | – | array, **req** |
| `expedited`, `expedited_reason`, `flags`, `flag_overrides` | – | – | present, optional |

The row `ApprovalRequestRow` (`backend/src/app/db/models.py`) also stores
`decided_at` (`:678` at that tree; `:674` at the filing tree), which no shape emits.

What follows from the table, each by reading it and none by inference:

1. **S1 cannot validate against S2.** S1 lacks the required `workspace_id`, and carries `environment`, which `extra="forbid"`
   rejects. Declaring `ApprovalRequest` as a route's 2xx would make outbound validation fail on every call, or, with
   validation off, would publish a shape the route does not emit. This is why `PL-1392`'s (working id `PL 9765` when filed) DP-S2-6 option (c) leaves the
   2xx of two routes alone.
2. **The decision enum disagrees on its values, not only its presence.** The published contract and the spec example say
   `approved` / `rejected` / `changes_requested`. The code stores and emits `approve` / `reject` / `request_changes`. A
   client written to the contract cannot read a decision the platform produces.
3. **S3 requires fields that no code produces** (`evidence_bundle`, `checklist`). `RL-1301` A.2 keeps evidence off
   `ApprovalRequestRow`, and the evidence lives with the Deployment Request. S3 also requires a non-empty `comment` where
   the model and the API allow `null`.
4. **`environment` is on the wire and in no contract.** It is new with the deployment branch of approvals
   (`PL-1306`'s Slice 2 reads it for `prod`).

## Which routes carry S1

`to_dict` is the return of four routes in `backend/src/app/api/approvals.py`. Each is already in `FD-1335`'s Part B list
of 12 open-object 2xx responses (Evidence §1, the four `approval-requests` lines):

| Route | Handler | `to_dict` call |
|---|---|---|
| `GET /api/v1/approval-requests/{request_id}` | `get_request`, through `_detail` | `:96` (in `_detail`; `:112` at the filing tree) |
| `POST /api/v1/approval-requests` | `submit_for_approval` | `:140` (`:156`) |
| `POST /api/v1/approval-requests/{request_id}/decide` | `decide_request` | `:254` (`:270`) |
| `POST /api/v1/approval-requests/{request_id}/withdraw` | `withdraw_request` | `:312` (`:294`) |

Who types what, as accepted so far:

- **`withdraw` and `POST /approval-requests`** are the 2 routes WK-674 Slice 2 changes. Slice 2 types their **request
  bodies** and leaves their **2xx** untouched (`PL-1392` (working id `PL 9765` when filed), DP-S2-6 option (c), accepted by the maintainer's 10:32:26 entry
  above). Both 2xx therefore stay on `FD-1335`'s temporary exclusion list, and are owned **here**.
- **`decide_request`** (`POST …/decide`): its body is typed in the FD-1356 fix slice (`PL-1408` (working id `PL 9762` when filed), DP-4 (a)). Its 200 comes
  to this finding and `FD-1335` Part B, with a key-set characterisation test (the lead's addendum to this filing).
- **`GET …/{request_id}`** was never anyone's delta. It stays with Part B.

So the remedy below is a **single decision applied to four routes**, and none of the four 2xx is unowned.

## A hand-authored file under `docs/contracts/`: is it sanctioned?

`CLAUDE.md` §2 says `docs/contracts/` is "generated and never hand-edited". `approval-request.schema.json` is
hand-authored, and sits in `docs/contracts/schemas/`, not in `schemas/generated/`.

**Provenance** (`git log --follow --format='%h %aI %s' -- docs/contracts/schemas/approval-request.schema.json`, two commits):
`cb9dd78d` (2026-08-14, "docs: complete contract coverage with the remaining 10 artifact schemas"), where it was written, and
`71f5a220` (2026-09-17, the W37-6 doc-id migration), a mechanical rewrite.

**Sanction.** The file is sanctioned as a Phase 0 draft, in three places:
- `docs/contracts/README.md`'s table: `schemas/` is "**hand-authored, Phase 0**"; only `schemas/generated/` and
  `openapi/generated.json` are "generated — do not edit". Its Status section: the rest "remain the Phase 0 hand-authored
  drafts until the shapes they describe exist in `packages/model-schema`" (ADR-704, FR-9, FR-451), and where both exist, "the
  generated one is authoritative".
- `RL-878` (`QuoteContext.purpose`): editing a hand-authored contract is a §0 matter, and the model is the authority where
  a generated side exists.
- `backend/tests/test_contracts.py`'s `ONE_SIDED_SLUGS`, which lists `"approval-request": "later-phase — 06 governance"`
  under "authored-only".

So `CLAUDE.md` §2's sentence is about `schemas/generated/` and `openapi/generated.json`, and the README states the carve-out.
**What is not sanctioned is its current state.** The README's own condition, "until the shapes they describe exist in
`packages/model-schema`", has been met since `ApprovalRequest` shipped. The `ONE_SIDED_SLUGS` reason "later-phase" is
therefore false, the same class as register finding F27 (`rate-table`, `rating-algorithm`, `rating-version`: "shipped in
model-schema, never compared"). No comparison guard covers this slug, because it has no generated side (it is not in
`GENERATED_SHAPES`, `scripts/generate-contracts.py`). That absence of a guard is how S3 drifted from S2 unseen.

## Remedy (a proposal; the decision-maker rules, per field, and the lead sets the slice)

1. **A DM ruling, per field,** on which side is right: the decision enum values; `workspace_id` on the wire; `environment`
   (add to S2, or stop emitting); `evidence_bundle` and `checklist` (does `06` §4.3 mean to require them on the request
   object, or on the Deployment Request only, `RL-1301` A.2); `comment` nullability; `withdrawn` object versus
   `withdrawn_reason`. The `06` §4.3 example is amended in the same change.
2. **One definition.** `ApprovalRequest` in `model-schema` is the single source of truth (ADR-704). The hand-authored
   file is retired or reduced to a one-line pointer, and the slug gains a generated side, so `test_contracts.py` compares it.
   `ONE_SIDED_SLUGS["approval-request"]` is struck in the same commit (its "later-phase" reason is false).
3. **The four routes' 2xx are typed once**, with the ruled shape, and leave `FD-1335`'s temporary exclusion list in that
   commit: `GET …/{request_id}`, `POST /approval-requests`, `POST …/decide`, `POST …/withdraw`. A key-set characterisation
   test lands first, pinning what `to_dict` emits today, so the change is a deliberate edit and no silent one.
4. **FD-1335 Part B's list names them.** This finding is the owner of those four 2xx; `FD-1335`'s closure condition
   ("the temporary list is empty") cannot be met without it.

## Disposition

Owner **WK-1178** (`FD-1335`'s carrier). **Proposed:** fix before close, with a decision-maker ruling first (`CLAUDE.md` §0),
then the slice the lead cuts, in the order of the Remedy above. Until then `WK-674` Slice 2 and the FD-1356 fix slice
type only request bodies for these routes, and the four 2xx stay on `FD-1335`'s temporary exclusion list under this finding.
The lead gives the verdict and the maintainer sets the severity.

## Evidence

- Field table: read at `1dd5e264` from `backend/src/app/platform/approvals.py:648-673`,
  `packages/model-schema/src/model_schema/approvals.py:264-295` (re-anchored 2026-10-05 at `ef5dc6e7317281ac9d1840fa61861597e3c1b8b1`: `:663-687` and `:384-411`, same fields; at `caa4e411` `to_dict` is `:672-697` and the model `:384-411`) and
  `docs/contracts/schemas/approval-request.schema.json` (its `required` list and `properties`).
- Spec twin: `docs/specs/06-governance.md:440-475` (`:458-488` at `caa4e411`, `:447-477` at `ef5dc6e7`; `06` §4.3, `"decision": "approved"` at the example's decisions entry).
- Provenance: `git log --follow --format='%h %aI %s' -- docs/contracts/schemas/approval-request.schema.json`.
- `ONE_SIDED_SLUGS`: `backend/tests/test_contracts.py`, the `"approval-request"` entry.
- `to_dict` call sites: `git grep -n 'service.to_dict' -- backend/src/app/api/approvals.py` prints four lines (`:112`, `:156`,
  `:270`, `:294` at the filing tree; `:96`, `:140`, `:254`, `:312` at `ef5dc6e7` and at `caa4e411`).
- **Not measured:** whether any client of the published contract exists today; the table is a statement about the three
  definitions, not about a consumer.

## Maintainer's decision (2026-10-01 10:38:52 BST)

Recorded from the maintainer's entry headed "2026-10-01 10:38:52 BST — FD 9752 (#1066 @24933167, the approval request's three disagreeing shapes): MEDIUM, owner WK-1178, deadline BEFORE the P2 exit demo, plus a consumer hold" (`to-lead.md`, a local channel file, so cited by its header). It supersedes the "Proposed severity" and "Proposed: fix before close" wording above, which stays as written and is **struck by this section**, not edited.

- **Severity: MEDIUM; owner WK-1178.** The worst field is the decision enum: the code emits `approve`/`reject`/`request_changes`; the published contract and `06` §4.3's example say `approved`/`rejected`/`changes_requested`. That is a silent misreading of a governance decision for any consumer (so not LOW). No consumer exists (exposure 0, so not HIGH).
- **Deadline: fixed before the P2 exit demo**, not "before close": WF-699's deploy step walks approvals.
- **HOLD:** no slice ships code that reads a response of any of the four `to_dict` routes until a DM rules the enum. Typing the request bodies is unaffected.
- **Discharge, all of:** (1) a DM rules per field which shape is right (`CLAUDE.md` §0), the enum first, with verbatim `06` text if the spec moves; the contract and the spec example agreeing is not proof. (2) One shape: the `model-schema` model, the hand-authored schema retired ("generated wins"), the four routes' 2xx typed by `$ref`. (3) The F27 class: the `ONE_SIDED_SLUGS` reason fixed, and a guard that fails when a listed slug has a `model-schema` class, proven on broken input.
