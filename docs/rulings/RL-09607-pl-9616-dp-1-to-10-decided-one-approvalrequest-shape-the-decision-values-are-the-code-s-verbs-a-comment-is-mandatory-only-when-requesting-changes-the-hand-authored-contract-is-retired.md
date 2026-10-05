---
id: RL-9607
family: ruling
title: PL 9616 DP-1 to DP-10 decided — one ApprovalRequest shape; the decision values are the code's verbs, a comment is mandatory only when requesting changes, the hand-authored contract is retired, five routes are typed, and a title-plus-$defs guard closes the F27 class
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-05              # the mint date (check 31); ruled 2026-10-05
owner: decision-maker
tree: cdaaa57345cb765f96034ce1ec2733c338f1c3cd
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FD-1416, FD-1335, RL-1301, RL-1263, RL-878, PL-1267, PL-1408, ADR-704, FR-351, FR-352, FR-355, FR-357]
---

# RL 9607 (working id) — PL 9616 DP-1 to DP-10 decided: one `ApprovalRequest` shape

## How this was ruled

- **Who and when.** This record was written on 2026-10-05, starting 15:49:03 BST (by `date`),
  by the decision-maker session `dm-1416`. The maintainer (by delegation) ruled the ten
  decision points of `PL 9616` (working id; draft PR #1168, branch `pl-9616-fd1416-fix`, head
  `0d0ed2273281ae7d58c2bfe4e657f5e42c4b22b5`). The ruling is in the entry headed
  "2026-10-05 15:47:15 BST — PL 9616 (#1168) DPs RULED (the maintainer, by delegation), on
  dm-1416's memo; the FD-1416 HOLD LIFTS at DP-1" in the lead's channel (`to-lead.md`, a local
  file, so cited by its header). DP-7 was ruled earlier, in the entry headed "2026-10-05
  15:43:38 BST". Both are quoted verbatim below.
- **The analysis.** It is the local memo
  `handover/dp-memo-pl9616-fd1416-2026-10-05.md`, which is not in the repository. The facts it
  rests on are re-stated, with their tree, in §"Verified first".
- **Working id.** `RL 9607` was reserved by the lead. Unminted records (`PL 9616`, `PL 9649`)
  are cited in working-id form and kept out of `relates:` (check 32).
- **This record is the HOLD's lift.** `FD-1416`'s HOLD (the maintainer's decision of
  2026-10-01 10:38:52 BST: "no slice ships code that reads a response of any of the four
  `to_dict` routes until a DM rules the enum") **lifts with DP-1's ruling, for all five
  `to_dict` routes**, the list route included (DP-7).
- **Owner of the work:** WK-1178, in the slice `PL 9616` plans. The `06` texts this ruling
  carries land in this commit (§"Spec changes in this commit").

### The ruling, quoted verbatim

From the entry headed "2026-10-05 15:47:15 BST":

> DP-1: (a), the code's verbs `approve` / `reject` / `request_changes`; 06 §4.3's example (:483) amended. Verbs name acts and ApprovalStatus participles name states, so the two value sets stay distinct; 06 §5.1 :561, the glossary :67 and :663 already agree. THE HOLD (FD-1416, 2026-10-01 10:38:52) LIFTS with this ruling, for all five to_dict routes.
> DP-2: (a). DP-3: (a), no migration. DP-4: (a). DP-6: (a) (FR-357 :98 requires "a reason").
> DP-5: (a) nullable for the RESPONSE (stored rows hold NULL; (b) would 500 every read). The REQUEST-side disagreement is DECIDED OUTRIGHT now, not raised as an OQ: FR-355 (06 :96) and the code (platform/approvals.py:441) are right. A comment is mandatory when requesting changes and optional on approve and reject. The glossary :67 ("with a mandatory comment") and §5.3 :640 ("mandatory comment") are amended by dated T-texts to "a comment, mandatory when requesting changes". Owner: WK-1178, in THIS slice (one more 06 edit). Making a comment mandatory on approve or reject would be a NEW requirement; it is not decided here and nobody is asked to build it.
> DP-7: (a), IN scope, as ruled at 15:43:38.
> DP-8: (a), delete the hand-authored approval-request.schema.json (the "reason fixed" decision, superseding FD-1416's Remedy item 2, the 2026-10-03 21:11:06 exemption at to-lead.md:16225). PL 9649 (#1152) re-anchors its Acceptance 9 cite (:53-54) at whichever of the two merges second.
> DP-9: (a) WITH the DM's refinement: the guard's predicate is the authored file's `title` plus its `$defs` keys (it finds 6, including `scoring`, whose $defs QuoteContext/ScoringResult/LadderRung/Trace are model_schema classes). The exemption map holds 5, `scoring` → RL-878 (its field-names test), each entry with its reason. The broken-input proof includes one case that ONLY the new predicate catches (the old PascalCase predicate passes it).
> DP-10: (a), the 2xx is typed. EITHER form is allowed: `response_model=` or the return annotation, the module's own precedent (`get_policy -> ApprovalPolicy`, api/approvals.py:337). The ruling states the outcome (a typed, contract-generated 2xx), not the mechanism.
> FILE the RL `active` with these rulings and the spec T-texts (06 §4.3 example; glossary :67; §5.3 :640), reserving the id now. The PL 9616 edit (once) carries: these rulings, the owed red-first acceptance items (an RV in review plus POST /approval-requests → 409; CHANGES_REQUESTED on an RV → draft), and DP-9's exemption map.

From the entry headed "2026-10-05 15:43:38 BST — PL 9616 (the FD-1416 fix, #1168 @0d0ed227):
noted; DP-7 RULED now (the LIST route is IN scope); the rest at the DP memo":

> DP-7 RULED now, saving a round: the LIST route `GET /approval-requests` is IN SCOPE. It emits the same `to_dict`, which is the defect FD-1416 names (one function, several routes). Fixing the shape on some routes and not this one would ship two shapes for one object, the exact class CLAUDE.md §2 forbids ("A shape defined twice will diverge"). It is not a widening of the finding, only of the plan's first draft. The rest (DP-1..6, 8..10) at dm-1416's memo; the HOLD lifts at DP-1's ruling, as recorded.

## Verified first, at `origin/main` `cdaaa57345cb765f96034ce1ec2733c338f1c3cd`

Each item was read with `git show origin/main:<path>`. Each is anchored by symbol, with the
line at that tree.

- **S1, the API's serialiser.** `backend/src/app/platform/approvals.py` `to_dict` (`:672-697`):
  - It emits 12 top-level keys, including `environment` and `withdrawn_reason`. It emits no
    `workspace_id`.
  - `decision` is the stored string.
  - `approvers_recorded` counts `DecisionKind.APPROVE.value` decisions.
- **S2, the `model-schema` class.** `packages/model-schema/src/model_schema/approvals.py`:
  - `ApprovalRequest` (`:405-431`) is `frozen=True` and `extra="forbid"`. It requires
    `workspace_id` and has no `environment`. `approvers_required` is `Field(ge=1)`. The
    validator `_recorded_matches_decisions` counts `DecisionKind.APPROVE`.
  - `ApprovalDecision` (`:394-402`) has `comment: str | None = None`.
  - `DecisionKind` (`:58-61`) is `approve` / `reject` / `request_changes`.
  - `ApprovalStatus` (`:46-56`) holds the participles.
- **S3, the hand-authored contract.** `docs/contracts/schemas/approval-request.schema.json`:
  - It requires `evidence_bundle` and `checklist`.
  - `decisions[].decision` is `enum ["approved","rejected","changes_requested"]`.
  - `decisions[].comment` is required, with `minLength` 1.
  - It has a `withdrawn` object, and no `id`.
- **Storage.** `backend/src/app/db/models.py`:
  - `ApprovalRequestRow` has `workspace_id` (NOT NULL), `environment` (nullable) and
    `withdrawn_reason` (nullable), and `CheckConstraint("approvers_required >= 1")`.
  - `ApprovalDecisionRow.decision` is `String(32)` with no CHECK. `comment` is nullable.
  - No `withdrawn_by` or `withdrawn_at` column exists.
- **The request-side comment rule.** In `platform/approvals.py`, `:441` refuses
  `request_changes` without a non-blank comment. No other decision kind needs one. This is
  exactly FR-355 (`06` `:96`: "`changes_requested` … requires a comment").
- **The five S1 routes.** In `backend/src/app/api/approvals.py`:
  - `_detail` (`:78-89`) returns `service.to_dict`. `get_request` (`:192`) uses it, and so
    does `list_requests` (`:141-184`, `-> Page[dict[str, Any]]`).
  - `submit_for_approval` (`:133`), `decide_request` (`:244`) and `withdraw_request` (`:329`)
    call `service.to_dict` directly.
  - `get_policy` (`:337`) declares its 2xx by return annotation, `-> ApprovalPolicy`.
- **The F27 class, by the ruled predicate** (the authored file's `title` and its `$defs` keys,
  each run through `git grep -n "^class <Name>\b" origin/main -- packages/model-schema/src`):
  - It finds six slugs, all authored-only in `ONE_SIDED_SLUGS` (`backend/tests/test_contracts.py`):
    - `approval-request` (`ApprovalRequest`, `approvals.py:405`)
    - `dislocation-run` (`DislocationRun`, `dislocation.py:116`)
    - `rate-table` (title `RateTableVersion`, `rating.py:899`)
    - `rating-algorithm` (`RatingAlgorithm`, `rating.py:375`)
    - `rating-version` (`RatingVersion`, `rating.py:138`)
    - `scoring` (`$defs` `QuoteContext` `scoring.py:99`, `LadderRung` `:149`, `Trace` `:187`,
      `ScoringResult` `:204`)
  - It finds no class for `dossier`, `gipp-check`, `monitoring` (`$defs` `Alert`, `Monitor`,
    `MonitoringResult`) or `optimisation-run`.
  - The plan's PascalCase-of-the-slug predicate finds the first five and misses `scoring`.

## Ruled

| DP | Ruled | Which side was wrong (`CLAUDE.md` §0) |
|---|---|---|
| DP-1, the decision enum | **(a)**: the code's verbs `approve` / `reject` / `request_changes`. `06` §4.3's example is amended. No data migration. | The spec, in one example (`06` `:483`) and in S3. `06` §5.1 (`:561`), the glossary (`:67`) and `:663` already agreed with the code. |
| DP-2, `workspace_id` | **(a)**: emitted. The service builds it from the row. | S1, which dropped a field the row stores and S2 requires (precedent: `model_schema/deployments.py` `:105`, `:169`). |
| DP-3, `environment` | **(a)**: added to S2 as `environment: str \| None = None`. No migration (the column exists). | S2, which lacked stored state of a deployment approval request. |
| DP-4, the S3-only fields | **(a)**: `evidence_bundle`, `checklist`, `expedited`, `expedited_reason`, `flags` and `flag_overrides` are not fields of the shape now. `06` §4.3 gains the dated note this option names. | S3 and the example, read as a key list. FR-352's checklist and evidence limbs are WK-677's. A Deployment Request's evidence is on the Deployment Request (`RL-1301` A.2). |
| DP-5, `comment` | **(a)**: nullable in the response. **The request side is decided outright:** a comment is mandatory when requesting changes, and optional on approve and reject. A comment mandatory on approve or reject would be a new requirement. It is not decided here, and nobody is asked to build it. | The spec's glossary (`:67`) and §5.3 (`:640`). FR-355 (`:96`) and the code (`platform/approvals.py:441`) were right. |
| DP-6, withdrawal | **(a)**: `withdrawn_reason`. The actor and the time stay on the withdraw's Audit Event. | S3's `withdrawn` object, which no stored column backs. FR-357 (`:98`) requires "a reason". |
| DP-7, the list route | **(a)**: `GET /api/v1/approval-requests` is in scope, typed `Page[ApprovalRequest]`. This widens the plan's first draft, not `FD-1416`. | — (a scope ruling, the maintainer's (by delegation), quoted above) |
| DP-8, the hand-authored file | **(a)**: `docs/contracts/schemas/approval-request.schema.json` is deleted. The slug becomes generated-only, and `ONE_SIDED_SLUGS["approval-request"]`'s reason is fixed to cite `FD-1416`. The maintainer's decision ("the `ONE_SIDED_SLUGS` reason fixed") supersedes `FD-1416`'s Remedy item 2 ("struck"). The one-key value change is exempt under the 2026-10-03 21:11:06 BST amendment to `RL-1263`. | S3: a second definition, against ADR-704. |
| DP-9, the F27-class guard | **(a), refined.** The guard's predicate is the authored file's `title` plus its `$defs` keys, matched against `model_schema` classes. A named map `SHIPPED_NOT_COMPARED` holds **five** exemptions (below), each with its reason. The guard fails for any other authored-only slug the predicate matches, and for a map entry whose slug no longer matches. | — (a guard design) |
| DP-10, the 2xx | **(a)**: the 2xx is a typed, contract-generated `ApprovalRequest` (`Page[ApprovalRequest]` for the list). FastAPI validates it outbound. **Either form is allowed:** `response_model=`, or the return annotation, which is this module's precedent (`get_policy -> ApprovalPolicy`). | — (an interface form) |

### DP-9's exemption map, as ruled

| Slug | Owning record | Reason |
|---|---|---|
| `dislocation-run` | `PL-1267` | Hand-authored until WK-673 Slice 4 generates and compares it. |
| `rate-table` | register F27 | Shipped in `model-schema` (`RateTableVersion`), never compared. |
| `rating-algorithm` | register F27 | Shipped in `model-schema`, never compared. |
| `rating-version` | register F27 | Shipped in `model-schema`, never compared. |
| `scoring` | `RL-878` | A `$defs`-only bundle. Its field names are compared by `test_generated_and_authored_agree_on_scoring_field_names`, but type and constraint parity waits on the walker rewrite (the comment above `ONE_SIDED_SLUGS["scoring"]`). |

`approval-request` is not in the map: DP-8 makes it generated-only.

**The broken-input proof** includes at least one case that **only** the new predicate catches,
and that the old PascalCase predicate passes. An example: an authored-only slug whose name does
not PascalCase to a class, but whose `title` or one of whose `$defs` keys is a `model_schema`
class. The proof runs the gate's own guard, not a re-assembled copy.

## Acceptance — the violation that must become detectable

Each item is red first on the base tree, by its stated cause, in `PL 9616`'s slice:
- **DP-1:** a stored decision reads back as `approve` / `reject` / `request_changes` on every
  route. A read-back of a participle (`approved`) is the violation.
- **DP-2, DP-3, DP-5, DP-6:** every 2xx body of the five routes passes
  `ApprovalRequest.model_validate`. That includes `workspace_id`, `environment`, a `NULL`
  `comment`, and `withdrawn_reason`. A body that S2 refuses, or a key S2 does not declare, is
  the violation.
- **DP-5, the request side:** `request_changes` without a non-blank comment is refused, and
  `approve` and `reject` without a comment are accepted. A comment demanded on approve or
  reject is the violation.
- **DP-7, DP-10:** in `docs/contracts/openapi/generated.json`, each of the five routes' 2xx
  is a `$ref` to the generated `ApprovalRequest`, and the list's `items` is that `$ref`. An
  open object on any of the five is the violation.
- **DP-8:** `docs/contracts/schemas/approval-request.schema.json` does not exist, and
  `approval-request` is generated-only.
- **DP-9:** the guard fails on deliberately broken input, including the one case that only
  the title-plus-`$defs` predicate catches. A map entry whose slug no longer matches also
  fails it.
- **The texts:** `git diff <base>..HEAD -- docs/specs/06-governance.md` shows exactly the four
  edits in §"Spec changes in this commit", and every other character is byte-identical.
  `grep -cF '"decision": "approved"' docs/specs/06-governance.md` prints `0`.

## What it obliges

1. **`PL 9616`** (planner, one edit before its first merge) aligns to this record:
   - DP-1 to DP-10 as ruled;
   - the T-text targets already landed here;
   - DP-9's predicate, map and broken-input case;
   - the two owed red-first acceptance items: (1) a Rating Version in `review` plus
     `POST /api/v1/approval-requests` gives 409; (2) `CHANGES_REQUESTED` on a Rating Version
     gives `draft`;
   - this record as an activation need, minted before `PL 9616`.
2. **`PL 9649`** (working id, #1152) and `PL 9616`: whichever merges second re-anchors
   `PL 9649`'s Acceptance 9 cite of S3 `:53-54`, which DP-8 deletes.
3. **The executor of `PL 9616`** applies DP-1 to DP-10 to the model, the service and the five
   routes. It applies no further `06` text for DP-1, DP-4 or DP-5, because those texts are in
   this commit.

## Spec changes in this commit

All are in `docs/specs/06-governance.md`. Each find string gave `grep -cF` = 1 at `origin/main`
`cdaaa573` before the edit.

| DP | Find string (`grep -cF` = 1) | Becomes |
|---|---|---|
| DP-1 | `"decision": "approved"` (§4.3 example, `:483`) | `"decision": "approve"` |
| DP-1, DP-4 | after the example's closing fence (the fence follows `"approvers_required": 2, "approvers_recorded": 1`) and before `` ### 4.4 `Dossier` structure `` | a dated note: a decision's value is the act and the request's `status` is the state; the example illustrates FR-352's full submission, and is not a key list; the authoritative shape is `model-schema`'s `ApprovalRequest` (ADR-704) |
| DP-5 | `by an Approver, with a mandatory comment.` (glossary, Approval Decision, `:67`) | `… with a ~~mandatory comment~~ comment, mandatory when requesting changes (FR-355) *(amended 2026-10-05, RL 9607 (working id) DP-5)*.` |
| DP-5 | `decision panel with mandatory comment,` (§5.3, Approval detail, `:640`) | `… decision panel with ~~mandatory comment~~ a comment, mandatory when requesting changes (FR-355) *(amended 2026-10-05, RL 9607 (working id) DP-5)*,` |

No requirement id is added or changed. FR-355 already states the rule that DP-5 makes the
glossary and §5.3 agree with.

## Observed, not ruled (for the lead)

- `06` §5.3's Approval detail row (`:640`) still lists "Evidence bundle, checklist, flags" as
  view contents. Under DP-4 (a), these are not fields of the returned shape until WK-677
  builds FR-352's limbs. The row describes the view WK-677 builds. It is not amended here.
