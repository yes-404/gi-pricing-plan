---
id: RL-1296
family: ruling
title: OQ-1234 decided — FR-429's promotion-skip permission lives on the approval policy's environment-qualified deployment entry
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 7040cf1e5ead768059398d3c2dc02404b1e695f7
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1234, RL-1232, PL-1237, CR-1247, FD-1281]
---

# RL-1296 — OQ-1234 decided: FR-429's promotion-skip permission lives on the approval policy's environment-qualified `deployment` entry

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). That is the
maintainer's raise that `decision-maker.md`'s role line names for a ruling. The session's own
`echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`.

The record was prepared earlier at effort `medium` (PR #935, head `4fc680ed`, "PREPARED, NOT
RULED"), under the maintainer's decision of 2026-09-30 00:42:01 BST that the decision-maker
prepares these rulings on medium and rules them only on high. This pass re-verified the
prepared evidence at the tree below, found one premise the preparation had left open
(the dependency direction, item 2 below) and resolved it, and rules. Minted 2026-09-30 as RL-1296 (`doc-id.py next --ref origin/main` = 1296 at `9f63d0fe`); it
was prepared and ruled under working id 9901.

## Verified first, at 7040cf1e5ead768059398d3c2dc02404b1e695f7

**The question** (`docs/open-questions.md:195`; mirror `docs/specs/07-platform.md:512`):
where does `07` FR-429's *"unless the workspace policy explicitly permits skipping with a
recorded reason"* live, and where is the recorded reason held?

**Why it blocks.** FR-429 as amended by `RL-1232` DP-7 (`07-platform.md:140`): the deploy
route refuses with `PROMOTION_ORDER_VIOLATION`, the `prod` approval submission requires
`uat_deployment` evidence and refuses with `EVIDENCE_INCOMPLETE`, and **both read one
predicate** — a successful `uat` deployment, *or a skip the workspace policy permits, with its
reason recorded*. `PL-1237` puts the decision in Slice 2
(`docs/plans/PL-01237-…md:419-422`, `:795-798`) and holds Slice 2's leaf plan until it is
decided (`:805`). The roadmap §10 gate row is *Before WK-674 Slice 2* (`docs/roadmap.md:1496`).

**Premise, re-checked at this tree** (each command run against `origin/main` = `7040cf1e`):
- `git grep -nE 'class (Deployment|Environment|WorkspacePolicy)\b' -- backend packages` →
  one hit, `backend/src/app/config.py:32`, the runtime-mode enum. No Deployment or
  Environment object exists yet.
- `git grep -n PROMOTION_ORDER_VIOLATION -- backend packages frontend` → only
  `backend/src/app/errors.py:62`. It is raised nowhere.
- `git grep -niE 'skip|promot' -- packages/model-schema/src/model_schema/approvals.py` → rc 1.
  The skip has no schema home.
- `git grep -n -i expedited -- packages backend/src` → rc 1. `06` FR-385 is unbuilt.

**What an answer can build on:**
- `ApprovalPolicy` / `ApprovalPolicyEntry`
  (`packages/model-schema/src/model_schema/approvals.py:111-160`): frozen,
  `extra="forbid"`, keyed per artifact type **and per target environment**
  (`environment: str | None`, `:119-121`). `entry_for(artifact_type, environment)` returns the
  environment-qualified entry first and falls back to the unqualified one (`:146-160`).
  `EVIDENCE_FLOOR["deployment"] = ("rating_version_approval", "uat_deployment")` (`:107`).
- Its write path, `set_policy` (`backend/src/app/platform/approvals.py:137-180`), requires
  `admin:manage_roles`, refuses a policy below the evidence floor
  (`POLICY_BELOW_EVIDENCE_FLOOR`), and writes an audit event. Its docstring gives the reason
  for that gate: *"a policy that drops `approvers_required` to one is a permission change
  written in another table."*
- `06` FR-352 and the glossary's **Evidence Bundle** (`06-governance.md:65`): evidence is a
  set of artifact references *"resolved and pinned at submission time"*. FR-356: the decision
  records the evidence artifact ids.
- `06` FR-385 (`06-governance.md:181`): an `expedited` request needs *"the same evidence"*
  and may only reduce the approver count.

**The dependency direction — the item the preparation left open.** `00` DEP-1
(`00-overview.md:469`): the build order is `PLAT → GOV → DATA → MODEL → RATE → OPT/MON`, and
a module never imports from a module to its right. DEP-537 (`:471-476`) exempts only GOV's
audit sink and permission check, and says *"GOV's approval workflow and its artifact reads
still respect DEP-1 strictly."* Three facts decide what this means here:
- **The deploy route belongs to `03`, not `07`.** `POST /api/v1/environments/{env}/deployments`
  is `03` §5.1's (`03-rating-engine.md:766`, "Deploy an approved version (FR-267)"), and `03`
  §7.1 already consumes `06`'s "Approval workflow, RBAC (Deployer role), audit sink". RATE is
  right of GOV, so the route reading the approval policy is the permitted direction. `07` §7.1
  does not change: `07` states the rule, and `03`'s route and `06`'s submission enforce it.
- **The GOV side must not import rating code.** The code already applies DEP-1 inside `app`
  by injection. `ArtifactResolver` (`backend/src/app/platform/approvals.py:110-126`) is a
  caller-supplied callable because *"DEP-1 forbids `GOV` importing `DATA` through `MON`"*;
  `EvidenceAuthorResolver` (`:283-294`) is *"Supplied by the caller, as `ArtifactResolver`
  is, so governance imports nothing from the rating module (DEP-1)"*. `.importlinter` has no
  contract between `app` modules, so this is held by convention, not by `lint-imports`.
- **So the one predicate reads only its arguments.** DP-7's single predicate cannot live in
  the rating module (GOV could not call it) or in governance code that loads deployments (GOV
  would read RATE). A pure function over the policy entry and caller-supplied facts, placed
  where both sides may import it, satisfies both directions. This holds for every option, not
  only (b), because the "successful `uat` deployment" half is RATE's data whichever home the
  skip gets.

## Options

As prepared, unchanged, because they record what was believed before this pass:

| | Option | For | Against |
|---|---|---|---|
| (a) | **A new workspace-policy object in `model-schema`** (ADR-704 contract change, generated to `docs/contracts/`) | Typed, versioned, validated; route and verifier import one definition; a clean home for future non-approval workspace policy | A new artifact shape, contract, contract guard, write route, permission and audit event — all of which `set_policy` already has for the approval policy; a second policy document beside the one the evidence floor already reads, so the two halves of DP-7's one predicate read two documents |
| (b) | **Approval-policy configuration**: a field on the environment-qualified `deployment` entry of `ApprovalPolicy` (e.g. which predecessor environments may be skipped, and that a reason is required); the per-act reason held on the `uat_deployment` evidence item / the Deployment record the skip produces | The `uat_deployment` floor already reads this document, so route and floor read the same one — DP-7's *a permitted, recorded skip **is** the evidence item* gets a direct home; the write path is already gated, floor-checked and audited; per-environment keying already exists (`entry_for`); §4.2's `expedited` block is precedent for a policy-level exception with `requires_reason` in this same document | A `07` promotion-order rule configured in `06`'s approval policy; the deploy route must read the approval policy (a `07` → `06` read the dependency direction must permit — to be checked by the ruling pass against `07` §7 and `.importlinter`); `admin:manage_roles` gates it, not an environment-scoped permission |
| (c) | **An Environment setting** (`07` FR-431, resolved by FR-446's precedence) on the Environment object Slice 2 creates | Sits with FR-428's promotion order; audited on change | **Its resolution is exactly what `OQ-1235` asks** — FR-446's precedence has no Environment level — and `OQ-1235` is gated *Before WK-674 Slice 3*, so (c) makes Slice 2 wait on Slice 3's gate; a Setting is an untyped value no schema constrains, so the predicate reads configuration rather than a contract |
| (d) | **A field on the Environment record itself** (typed, on the `model-schema` shape Slice 2 creates), e.g. `skippable: bool` on the environment that may be bypassed | Typed and next to the promotion order; no dependency on `OQ-1235` | The evidence floor then reads two documents (policy for the floor, Environment for the skip), which is what DP-7's one predicate was ruled to avoid; the permission is workspace governance, and an Environment edit is not governed by the policy path |

**Correction to (b)'s "Against" column, made by this pass:** the read it names is not a
`07` → `06` read. The deploy route is `03`'s, and RATE → GOV is permitted (verified above).
The cost that remains is that a `07` rule is configured in `06`'s document.

## Ruled

**Option (b).** FR-429's skip permission is a field on the **environment-qualified
`deployment` entry** of the workspace's `ApprovalPolicy`. The reason for a skip is the
predecessor-deployment evidence item of the approval request that uses it.

1. **Where the permission lives.** `ApprovalPolicyEntry` gains one field, which names the
   predecessor environments whose successful deployment a deployment **into this entry's
   environment** may skip. Its default is empty, so no skip is permitted. The field is valid
   only on an entry with `artifact_type == "deployment"` **and** a non-null `environment`. A
   validator refuses it anywhere else, which includes the unqualified fallback entry that
   `entry_for` would otherwise apply to every environment. A skip is a named exception into one
   named environment, never a blanket one. Slice 2 chooses the field's name, and states it in
   `06` §4.2 in the same commit as the model (item 5).
2. **Why this home — the evidence.** The `uat_deployment` floor already reads this document
   (`approvals.py:107`, `effective_evidence`), and DP-7 requires the route and the floor to
   read one predicate. The document the floor already reads is the only home in which both
   halves read one document without a second policy shape. (a) and (d) put the skip in a
   second document. (c) is excluded on its own ground: a Setting is an untyped value no schema
   constrains, so the predicate would read configuration, not a contract. That does not depend
   on how `OQ-1235` is answered.
3. **Where the reason is recorded.** Because the permission exists only on an entry that
   gates deployments into its environment on an approval, every skip is exercised through an
   approval request. The reason is the **predecessor-deployment evidence item** of that
   request (for `prod`, the `uat_deployment` item). It is a skip record naming the skipped
   environment and a non-empty reason, in place of a reference to a deployment. It is pinned
   at submission, as every evidence item is (FR-352, FR-356), and the `03` Deployment record
   references the approval that carries it (`03` FR-267 already requires the approval record
   for `prod`). The reason is written once and is not copied onto the Deployment. A reason is
   always required when a skip is used, and is **not** configurable. FR-429 says "with a
   recorded reason", and a requirement that configuration can switch off is not a requirement
   (the same argument as `submitter_may_approve`, `approvals.py:132-144`).
4. **The one predicate, and the dependency direction.** The predicate is a pure function of
   its arguments: the policy entry for the target environment, the target's predecessor per
   FR-428's promotion order, whether that predecessor has a successful deployment of this
   Rating Version, and the skip record if any. It loads nothing. `03`'s deploy route supplies
   the deployment facts it reads itself. `06`'s approval submission receives them through a
   caller-supplied resolver, as `ArtifactResolver` and `EvidenceAuthorResolver` already do,
   so governance imports nothing from the rating module. The binding constraint is that the
   predicate lives where both `03`'s route and `06`'s submission may import it and reads
   nothing else. `model_schema.approvals`, beside `entry_for` and `effective_evidence`,
   satisfies it. Slice 2 may place it elsewhere only if the same holds.
5. **The §4.2 interaction and the order with FR-385.** `06` §4.2's JSON is the document
   `ApprovalPolicy` round-trips. The new field is written into §4.2 **in the same Slice 2
   commit** as the model change and the regenerated `docs/contracts/`, never before it.
   Writing it now would widen the gap `FD-1281` records (§4.2 shows keys the model refuses).
   This ruling and FR-385's `expedited` are **independent**, and neither waits for the other.
   `expedited` changes the approver count and, by FR-385's own text, requires *"the same
   evidence"*. So an expedited request does not permit a skip, and a skip does not reduce the
   approver count. Whichever lands second extends the same model and §4.2 in its own commit.
6. **Who may grant it, and who may use it.** Granting is a change to the approval policy.
   It goes through `set_policy`, gated on `admin:manage_roles`, floor-checked and audited,
   and no new permission is created. That gate is right for the reason `set_policy`'s
   docstring gives: permitting a skip weakens a control, as dropping an approver count does.
   *Using* a permitted skip needs nothing beyond what the act already needs: submitting the
   approval request and `deployment:promote`, whose environment scoping (`CR-1212` item 4)
   lands in Slice 2 independently of this ruling.

**Not ruled here.** The field's name and the skip record's exact shape (Slice 2, under
items 1 and 3). Whether the unmodelled §4.2 keys (`expedited`, `separation_of_duties`, the
per-entry `escalation`) are modelled or struck: that is `FD-1281`'s, not this question's.

**No `FR-` is appended.** The obligation is FR-429's, as `RL-1232` DP-7 amended it. This
ruling supplies the home, and FR-429 is amended, dated, to name it.

## What it obliges

- **This commit:** `07` FR-429 carries a dated clause naming the home. `OQ-1234` is closed in
  both mirrors (`docs/open-questions.md` and `07` §10), citing this record.
- **The roadmap (the lead's file, not edited here):** the §10 row *Before WK-674 Slice 2*
  strikes `OQ-1234` and recounts to `1 (0 open)`. A decided question keeps its row.
- **WK-674 Slice 2 (`PL-1237` Task 2, whose leaf plan this unblocks):** items 1, 3 and 4
  above. The `ApprovalPolicyEntry` field and its validator, `06` §4.2 and the regenerated
  contract go in one commit (item 5). The predicate follows item 4.

## Acceptance — the violation that must become detectable

The violation: **a Rating Version reaches an environment past a predecessor it never
deployed to, without a permitted and reasoned skip — or the route and the floor disagree
about whether it may.** Slice 2 carries the checks, each shown red on deliberately broken
input:
- *Violation:* a `prod` deployment with no successful `uat` deployment and no skip permitted
  by the `prod`-qualified `deployment` entry. It is refused at the route with
  `PROMOTION_ORDER_VIOLATION` **and** at the approval submission with `EVIDENCE_INCOMPLETE`,
  by the one predicate both call.
- *Violation:* a permitted skip whose evidence item has an empty or whitespace reason. Both
  refuse it.
- *Violation:* the skip field on an unqualified `deployment` entry, or on a non-`deployment`
  entry. `ApprovalPolicy` validation refuses it, so `set_policy` cannot store it.
- *Violation:* the route and the floor diverge. A test that flips the policy field flips both
  refusals together.
- *Violation:* governance code imports the rating module to answer the predicate. Checked at
  the Slice 2 review, since no `lint-imports` contract covers modules inside `app`.
