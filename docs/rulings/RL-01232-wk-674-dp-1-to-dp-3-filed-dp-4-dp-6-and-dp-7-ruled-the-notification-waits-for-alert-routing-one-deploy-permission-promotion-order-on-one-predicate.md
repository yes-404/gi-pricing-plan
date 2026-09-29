---
id: RL-1232
family: ruling
title: WK-674 — DP-1 to DP-3 filed from the deputy's decisions; DP-4, DP-6 and DP-7 ruled — the notification waits for alert routing, one deploy permission, and promotion order checked twice on one predicate
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-29               # drafted 2026-09-28; set to the mint date, as audit-docs check 31 requires
owner: decision-maker
tree: ed123cb0fcf91e44872963bf8a8bad32b87c99bc
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [ADR-710, RL-921, CR-927, PL-930]
---

# RL-1232 — WK-674: DP-1 to DP-3 filed from the deputy's decisions; DP-4, DP-6 and DP-7 ruled

## Verified first, at ed123cb0fcf91e44872963bf8a8bad32b87c99bc

**This record has two halves, kept apart.**
- **Part A files decisions it does not make.** DP-1, DP-2 and DP-3 are the maintainer's,
  decided by the deputy by delegation in the entry on WK-674 written at 14:08:59 BST and
  relayed by the lead. That entry is quoted whole under Part A, in a fenced block. It also
  records the NFR-497 input and endorses the slice order.
- **Part B rules DP-4, DP-6 and DP-7.** The plan's Decision points table assigns these to
  the decision-maker. They are this record's own decisions. Each gives the options, the
  ruling, the rationale and what it obliges. Their spec amendments land in this commit, as
  the charter requires: a spec edit is made with the ruling record that names it.

**The plan these rule on** is WK-674's map plan (PR #843), read on branch `p2-wk674-map` at
`61996320` (`status: draft`, `tree: ed123cb0…`). Its Decision points table is at `:336-360`
there, and its slices are Tasks 1–6 at `:419-588`:
- Slice 1: tenancy and provenance;
- Slice 2: the Environment and Deployment record;
- Slice 3: environment isolation;
- Slice 4: the deployment path;
- Slice 5: switchover, rollback and the measurements;
- Slice 6: date-based routing and shadow scoring.

The plan is not on `main`, so it is named by PR here: an id that does not resolve fails
`audit-docs.py` check 32. The fenced entry quotes its id whole. DP-5 is withdrawn in the plan
and its number is not reused. **Slice design is the planner's and is not ruled here.**

This record was drafted in the decision-maker's worktree, on branch `p2-wk674-rl`, cut from
`origin/main` = `ed123cb0` with a clean root. Clock at drafting: 2026-09-28 14:14:30 BST, read
by `TZ=Europe/London date`. **Its id was a working id**, minted at its turn with
`doc-id.py next --ref origin/main`, and renumbered in one commit if it differs. *(Minted 2026-09-29: `doc-id.py next --ref origin/main` printed 1232 at origin/main
`c9f50232`. The record's working id (9203) became RL-1232, and the two open questions'
working ids (9301, 9302) became OQ-1233 and OQ-1234, in ascending order. `created:` moved from
the drafting date 2026-09-28 to the mint date, because `audit-docs.py` check 31 requires
`created` to be non-decreasing with the number and id 1230 is `created` 2026-09-29. OQ-1235 was filed later the same day, on the maintainer's answer QDP-2, and
minted from `doc-id.py next --ref HEAD` = 1235 at this branch's pushed head `7bcdccc5`,
because `--ref origin/main` still read 1232 while main held none of this branch's ids.)*

**Re-read at `ed123cb0`, for Part B:**
- `docs/specs/03-rating-engine.md:198` *(`:200` at the merged tree, re-read 2026-09-29)* is FR-272: *"Every deployment, rollback, and routing
  change emits an Audit Event and a notification to a configured channel."*
- The same file's line 900 *(`:1103` at the merged tree, re-read 2026-09-29)*, in its §7, lists `05-monitoring` as consuming *"deployment
  events"*.
- `docs/specs/05-monitoring.md:140` is FR-336: *"Alert routing is configurable per Monitor:
  in-app inbox, email, and webhook (Slack/Teams/PagerDuty-compatible). Routing failures are
  themselves logged and surfaced."* It is Phase 4, and its roadmap row is WK-688.
- ~~No `07` requirement defines a notification channel. `07`'s own §7 lists "notification
  channels" among what `05` takes from it, but no FR specifies one (the plan's premise e).~~
  **Superseded 2026-09-29 by the maintainer's entry `2026-09-29 14:15:43 BST · maintainer (acting on the maintainer's behalf) · WK-674 chain: answers to Q856-1/2 and Q848-1/2/3` (Q848-1):** the premise is
  false. `07` FR-453 (`07-platform.md:184`) reads *"Webhooks (alert routing, deployment
  notifications) are signed with an HMAC over the payload, delivered with retries and
  exponential backoff, and their delivery status is observable."* That is the channel. See
  *Amended 2026-09-29* below.
- `docs/specs/06-governance.md:62` (the glossary) gives the example
  `rating_version:deploy_prod`. `:219` says Pricing Actuary lacks `rating_version:deploy_*`.
- `packages/model-schema/src/model_schema/permissions.py:54` defines
  `DEPLOYMENT_PROMOTE = "deployment:promote"`. No `docs/specs/` file names
  `deployment:promote`: `git grep` over `docs/specs` finds 0 hits.
- `06` §4.1's role-assignment `scope` has no environment dimension. FR-345 scopes by
  Datasets, Model Families and Rating Algorithms only.
- `07` FR-428 (`:139`): *"The shipped set is `dev → uat → prod`; additional environments are
  configurable."*
- `07` FR-429 (`:140`) requires promotion order, *"unless the workspace policy explicitly
  permits skipping with a recorded reason"*.
- `06` §4.2's default policy (`:271-273`; *`:272-274` at the merged tree, re-read 2026-09-29*) has a `deployment` entry for `"environment":
  "prod"`, whose evidence is `rating_version_approval` and `uat_deployment`.
- `model_schema/approvals.py:107` puts the same two kinds in `EVIDENCE_FLOOR["deployment"]`.
- `PROMOTION_ORDER_VIOLATION` is registered (`backend/src/app/errors.py:62`; `07:338`).

## Amended 2026-09-29 — the maintainer's answers to Q848-1, Q848-2 and Q848-3

**Source.** The maintainer's entry headed, verbatim:

> `## 2026-09-29 14:15:43 BST · maintainer (acting on the maintainer's behalf) · WK-674 chain: answers to Q856-1/2 and Q848-1/2/3`

These answers are the maintainer's. This record files them and does not re-decide them. Every
amendment below is dated 2026-09-29 and struck in place, and no id is renumbered.

**Q848-1 (DP-4).** The premise *"No `07` requirement defines a notification channel"* is
superseded (struck in place above). DP-4's channel **is `07` FR-453's signed
deployment-notification webhooks**, and `03` FR-272's amendment now cites FR-453. **Which Work
owns FR-453's deployment-notification limb is not picked here.** It is filed as **`OQ-1233`**
(options WK-674, WK-688 or a platform Work, with trade-offs and a recommendation), in
`docs/open-questions.md` and `07` §10, and placed in `docs/roadmap.md` §10. DP-4's Audit Event
half stands: WK-674 emits the Audit Event in the change's transaction. The assignment of
delivery to WK-688 is struck in place, and so is the title's clause *"the notification waits
for alert routing"*, which the title keeps as drafted. DP-4's *Why* argued that retries and
failure surfacing are FR-336's alone. FR-453 also requires retries, backoff and observable
delivery status, so that argument is weaker than it read. It is kept as the record of what was
believed on 2026-09-28.

**Q848-2 (DP-7).** DP-7 **stands as a requirement-level ruling only.** Premise note, read at
the merged tree (origin/main `c9f50232` merged in):
- The Deployment and Environment objects DP-7 names do not exist. The only `Environment` is
  the runtime-mode enum at `backend/src/app/config.py:31`, and there is no Deployment class
  (`git grep -nE 'class (Deployment|Environment)\b' -- backend packages`: that one hit).
- `PROMOTION_ORDER_VIOLATION` is registered (`backend/src/app/errors.py:62`) but raised
  nowhere (`git grep -n PROMOTION_ORDER_VIOLATION -- backend packages frontend`: only
  `errors.py:62`).
- `07` FR-429's *"unless the workspace policy explicitly permits skipping"* has no schema home:
  `packages/model-schema/src/model_schema/approvals.py` has no skip or promotion field
  (`grep -niE 'skip|promot'` on that file: 0 hits).

**The skip-permission's home is `OQ-1234`**, owner WK-674 (which creates Deployment and
Environment), with options (a) a workspace-policy object in `model-schema` (an ADR-704 contract
change) and (b) approvals configuration, or another, each with trade-offs and a
recommendation. It is in `docs/open-questions.md` and `07` §10, and placed in
`docs/roadmap.md` §10. WK-674's map plan (PR #843) places it in a named slice. That is not
this record's edit.

**Q848-3.** The *What Part A obliges* bullet for Slice 5 is corrected in place: the proposal
goes to the maintainer (or the session acting on the maintainer's behalf). The fenced entry
under Part A is a dated quotation and is kept verbatim.

**Two later entries of the same day, also the maintainer's, recorded here.**
- The entry of 2026-09-29 14:17:56 BST (Q843-1), headed verbatim (fenced, because the heading
  carries a padded id):

  ```text
  ## 2026-09-29 14:17:56 BST · maintainer (acting on the maintainer's behalf) · Q843-1/2/3: CR-01212 item 4 stands; DP-6 amended
  ```

  DP-6 is amended in place. See *DP-6 amended 2026-09-29*.
- `2026-09-29 14:20:41 BST · maintainer (acting on the maintainer's behalf) · QDP-1/2/3 (WK-674 DP mechanisms)`: DP-1, DP-2 and DP-3 stand as filed.
  - **QDP-1:** `07` FR-437's dated amendment is in this commit. The Phase 3 roadmap row for
    FR-433 is the lead's, after merge.
  - **QDP-2:** how per-environment configuration resolves is filed as **`OQ-1235`**, an
    open question and not a pick. It is in `07` §10 and `docs/open-questions.md`, and at the
    roadmap §10 gate *Before WK-674 Slice 3*. Premise, read at `c9f50232`: `07` FR-431
    (`07-platform.md:142`) makes environment configuration "a Setting resolved by the
    precedence in §3.8", and FR-446 (`:172`) is *"environment variable → workspace setting →
    platform default"*, with no Environment level. `SettingDefinition`
    (`backend/src/app/platform/settings.py:44-52`) has fields `key`, `type`, `default`,
    `description`, `constraints` and `feature_flag`, and no environment field. DP-2's
    per-environment default-off setting needs that level.
  - **QDP-3:** DP-3 (b) gets a dated note under *What Part A obliges* (the Slice 5 bullet).

**Cites re-read at the merged tree, 2026-09-29.** This branch merged `origin/main` at
`c9f50232`. Every line cite in *Re-read at `ed123cb0`* was re-read there. Three moved and are
annotated in place: `03:198` → `03:200`, `03:900` → `03:1103`, `06:271-273` → `06:272-274`.
The rest hold: `05:140` (FR-336), `06:62`, `06:219`, `permissions.py:54`, `07:139` (FR-428),
`07:140` (FR-429), `approvals.py:107`, `errors.py:62` and `07:338`. The *0 hits* for
`deployment:promote` in `docs/specs` was true at `ed123cb0`. This record's own `06`
amendments now name it. The plan cites (`:336-360`, `:419-588`) are to branch
`p2-wk674-map` at `61996320` and were not re-read here.

## Ruled

Two parts, kept apart: Part A files the deputy's decisions, and Part B is this record's own.

### Part A — the deputy's decisions, filed (DP-1, DP-2, DP-3; NFR-497; the slice order)

The deputy's entry, **whole and verbatim**. It is fenced so that the ids it quotes are read as
quotation, not as citations; `audit-docs.py` check 32 skips fenced blocks.

```text
## 2026-09-28 14:08:59 BST · deputy · WK-674 (PL-9102, #843): DP-1, DP-2 and DP-3 DECIDED; the NFR-497 input noted; the slice order endorsed

Given by the maintainer's delegation (28 Sep, extended goal). dm-e files these in the WK-674 RL (its third), quoting this entry, alongside its own DP-4, DP-6 and DP-7. Read at `p2-wk674-map` `61996320`.

- **DP-1: (b) ACCEPTED, with a spec amendment.**
  - **FR-433's Helm chart / Kubernetes manifests move to Phase 3**, deferred with an owner (the maintainer, named at plan review 15), with the P2 closure record as the event.
  - WK-674's `deploy/` work stops at compose plus FR-437's reference Keycloak.
  - **Because `07` FR-437 says the rest of `deploy/` beyond compose is "Owned by WK-674"**, WK-674's S4 (or S1) carries a **dated amendment to FR-437** naming the move and this entry, so the spec and the plan do not disagree.
  - The F1 acceptance test is measured on the compose path WK-674 builds, which is what my F1 decision requires. Kubernetes is not needed for it.
- **DP-2: (a) ACCEPTED.** Build both **FR-270 and FR-271** in Slice 6. "Optional" is a per-environment runtime option, not an optional deliverable, and FR-271's shadow results are what WK-687's comparison needs; a comparison against results that were never recorded is not deferrable. They stay **default off per environment**. Enabling one is an environment setting with its own audit event.
- **DP-3: (b) ACCEPTED, with one limit.**
  - The measured verdict is recorded at Slice 5, as is. **If RL-921 §4's trigger fires** (the 15 ms without-GBM limb still fails with the blob read removed), the slice files a **proposed NFR-489 amendment** as its own spec change, with the measurement attached.
  - **The limit:** a proposed amendment is a proposal. **Changing a performance target is the maintainer's decision, and it comes to me (by delegation) with the measurement and RL-921 §4 quoted.** WK-674 may close with NFR-489 either passing, or amended by that decision, or carried with a named owner and event. **It never closes with a silent pass, and it never amends its own budget.**
- **NFR-497 (the 99.95 % monthly availability, F41):** this is the lead's verdict at the close, as the planner correctly says (DP-5 withdrawn, with a tombstone). The planner's input, *deferred with an owner: WK-687 (Phase 4)*, is reasonable: a synthetic month measures the harness, not the target. **No objection.** At the close, the degraded-read evidence must be quoted beside the verdict.
- **Slice order endorsed** (planner's slice design): S3 isolation → S4 deployment path (compose `api`/`worker`) → S5 switchover. Running S5 first would repeat F1's loopback limitation, which is exactly why I ruled F1 inconclusive.
- **For plan review 15:** FR-432/433/434/435/438 and NFR-531/533/534 are on **no roadmap row**, and the compose file has no application service. The review assigns each (WK-674, P3, or WK-1178). **With DP-1 decided, FR-433 is P3.** FR-432/434's evidence from S4 counts only for ids the review assigns to WK-674, as the plan says.

**I accept PL-9102 as WK-674's map plan** once dm-e's RL (with these and DP-4/6/7) is cited and the plan has minted. The acceptance line follows your request.
```

**What Part A obliges, per slice:**

- ~~**Slice 4 (or Slice 1)** carries~~ **This commit carries** *(amended 2026-09-29, QDP-1 of the
  maintainer's entry `2026-09-29 14:20:41 BST · maintainer (acting on the maintainer's behalf) · QDP-1/2/3 (WK-674 DP mechanisms)`)* a dated amendment to `07` FR-437, naming FR-433's move to
  Phase 3 and the deputy's entry, so the spec and the plan agree. WK-674's `deploy/` work
  stops at compose plus FR-437's reference Keycloak. The F1 acceptance test is measured on
  that compose path.
- **FR-433 (Helm / Kubernetes)** goes to Phase 3, deferred with an owner: the maintainer,
  named at plan review 15, with the P2 closure record as the event.
- **Slice 6** builds FR-270 and FR-271. Both are default off per environment, and enabling
  one is an environment setting with its own audit event.
- **Slice 5** records NFR-489's measured verdict as it is. If RL-921 §4's trigger fires, it
  files a proposed NFR-489 amendment as its own spec change, with the measurement. The
  proposal goes to ~~the deputy by delegation~~ the maintainer (or the session acting on the
  maintainer's behalf) *(corrected 2026-09-29, Q848-3 of the maintainer's entry `2026-09-29 14:15:43 BST · maintainer (acting on the maintainer's behalf) · WK-674 chain: answers to Q856-1/2 and Q848-1/2/3`;
  the fenced entry above is a dated quotation and is kept verbatim)*, with RL-921 §4 quoted. WK-674 closes with
  NFR-489 passing, amended by that decision, or carried with a named owner and event. It
  never closes on a silent pass or on a budget it amended itself.
  *(Noted 2026-09-29, QDP-3 of the maintainer's entry `2026-09-29 14:20:41 BST · maintainer (acting on the maintainer's behalf) · QDP-1/2/3 (WK-674 DP mechanisms)`: DP-3 (b) — "verdict
  recorded; the re-measurement trigger cannot validly fire without a dedicated host
  (RL-921)". No repo record names a dedicated host, and the host question is with the
  maintainer.)*
- **The close:** NFR-497's verdict is the lead's, with the degraded-read evidence quoted
  beside it.
- **Plan review 15** assigns FR-432, FR-434, FR-435, FR-438, NFR-531, NFR-533 and NFR-534,
  which sit on no roadmap row. FR-433 is already Phase 3.

### Part B — the decision-maker's rulings (DP-4, DP-6, DP-7)

#### DP-4 — FR-272's "notification to a configured channel": ruled (b)

**The question**, as the plan puts it: no `07` requirement specifies a channel. **The
options:**
- (a) A `07` spec change defining a minimal webhook channel through a secret reference, built
  in Slice 2.
- (b) WK-674 writes the durable deployment event, and delivery belongs to WK-688 (alerting,
  Phase 4), with FR-272 amended to say so.
- (c) Build delivery with no spec.

**Ruled: (b), with the durable event narrowed to the Audit Event itself.** WK-674 emits the
Audit Event in the same transaction as the deployment, rollback or routing change. That event
is already append-only and hash-chained, and it is the "deployment event" `03` §7 says `05`
consumes. WK-674 builds ~~no channel,~~ no outbox notification job and no second event store.
~~Delivery to a configured channel is `05`'s alert routing, owned by WK-688.~~ *(Struck
2026-09-29, Q848-1: the channel is `07` FR-453, and which Work delivers it is `OQ-1233`'s.
See* Amended 2026-09-29 *below.)*

**Why.** The obligations that make a notification trustworthy are retries, routing and
surfacing a failed delivery. They are FR-336's, in Phase 4. A channel built now, with none of
them, is a later phase built ahead (`CLAUDE.md` §0), and it would be rebuilt when WK-688
arrives.
- (a) specifies half of FR-336 inside `07`, and makes WK-674 own a delivery path it cannot
  finish.
- (c) is excluded by `CLAUDE.md` §0.
- The planner's (b) proposed an outbox event as well. I narrow it: the outbox (`07` FR-406)
  carries Jobs, and a notification Job needs a handler that only WK-688 would write. The Audit
  Event is already the durable, transactional record that (b) needs.

**What it obliges:**
- **This commit:** `03` FR-272 gains a dated amendment that splits its two halves by phase.
- **Slice 2:** emits the Audit Event for every deployment, rollback and routing change, in
  the change's transaction. It proves this on broken input: *Violation: a deployment whose
  transaction commits with no Audit Event.*
- ~~**WK-688 (Phase 4):** delivers FR-272's notification through FR-336's routing, reading
  deployment Audit Events.~~ *(Struck 2026-09-29, Q848-1: the owner is `OQ-1233`'s.)*

#### DP-6 — the deploy permission's name: ruled (b), without the environment grant

**The question:** `06:62` and `06:219` say `rating_version:deploy_prod` and
`rating_version:deploy_*`, per environment, and the code says `deployment:promote`. **The
options:**
- (a) The spec is right: rename to a per-environment family.
- (b) The code is right: amend `06` to `deployment:promote`, scoped by the environment of the
  grant.
- (c) Keep both.

**Ruled: (b), the code is right about the name~~, and there is no environment-scoped grant~~.**
*(Amended 2026-09-29, Q843-1 of the maintainer's entry of 2026-09-29 14:17:56 BST (heading quoted in the fenced block under *Amended 2026-09-29*): "no environment-scoped
grant" survives only as the Phase 2 state until WK-674's environment slice lands, not as the
design. The design is `CR-1212` item 4's. See* DP-6 amended 2026-09-29 *below.)*
One permission, `deployment:promote`, is amended into `06`'s glossary example and §4.1's
Pricing Actuary sentence, struck in place and dated.

**Why.**
- `07` FR-428 makes environments configurable. A per-environment name
  (`…:deploy_prod`, `…:deploy_staging`) would make the permission vocabulary open-ended, while
  `06` FR-344's custom roles are composed from a fixed one. That rules out (a).
- (c) is two names for one act.
- The planner's rationale for (b) cites FR-430's per-environment scoping. That clause does
  not carry over. FR-430 scopes Service Account **credentials**, and a Service Account can
  never hold a deployment permission (`06` FR-347). A human grant's scope (§4.1, FR-345) has
  no environment dimension. So "scoped by the environment of the grant" names a mechanism
  that does not exist, and this ruling does not create one. *(2026-09-29: still true at
  `c9f50232`. `CR-1212` item 4 creates it, as a `06`/`07` spec change owned by WK-674.)*
- What stops an unprepared `prod` deployment today is FR-267's complete-approval rule and
  FR-429's promotion order (DP-7), not a permission name.
- Restricting which Deployers may deploy to which environment would be a new scope dimension.
  ~~That is `06` FR-345's scoping, which is Phase 3 (WK-676). It is noted here and not built.~~
  *(Struck 2026-09-29, Q843-1: the premise is superseded. The deputy's entry `2026-09-28 14:19:21 BST · deputy · CORRECTION: my 14:18 DP-6 "carried risk" note named FR-345 as the environment-scoped grant mechanism. It is not. No requirement scopes a human deploy grant by environment`
  withdrew it: FR-345 names no environment, and it is not the mechanism. The owner is WK-674,
  per `CR-1212` item 4.)*

**Observed, not ruled:** other names in `06` §2 and §4.1 also differ from the code's
vocabulary. For example, `06` has `model:approve` where the code has `approval:decide`, and
`rating_version:submit` where the code has `rating:submit`. This record amends only the deploy
permission, which DP-6 asks about. The rest is for an auditor to file as a finding, and the
lead is told.

**DP-6 amended 2026-09-29 — the maintainer's answer Q843-1** (entry of 2026-09-29 14:17:56 BST (heading quoted in the fenced block under *Amended 2026-09-29*)):
- **The premise is superseded.** The routing of environment scoping to FR-345, Phase 3,
  WK-676 rested on a premise the deputy withdrew in `2026-09-28 14:19:21 BST · deputy · CORRECTION: my 14:18 DP-6 "carried risk" note named FR-345 as the environment-scoped grant mechanism. It is not. No requirement scopes a human deploy grant by environment`. That entry reads, at
  `ed123cb0`: *"`06` FR-345 reads 'Role assignments are **scoped**: workspace-wide, or
  limited to named Datasets, Model Families, or Rating Algorithms'. It names no
  environment."* It also *"supersedes the 'owner WK-676' part"*.
- **The decision is `CR-1212` item 4's** ("4. The environment-scoping spec gap"; accepted
  by delegation in the deputy's entry of 2026-09-28 18:13:19 BST): *"a `06`/`07` spec change
  that scopes `deployment:promote` to named environments, owned by WK-674 and landed with
  its environment record."* This record does not re-decide it and does not write that spec
  change. It lands with WK-674's environment record.
- **"(b) … no environment-scoped grant" is the Phase 2 state only**, until that WK-674 slice
  lands. The name ruling (one permission, `deployment:promote`, no per-environment family)
  is unchanged. Scoping one permission to named environments is a grant scope, not a second
  name.

**What it obliges:**
- **This commit:** the two `06` amendments.
- **Slice 2:** the deploy route requires `deployment:promote` and refuses without it. It
  proves this on broken input: *Violation: a principal without `deployment:promote` deploys.*

#### DP-7 — where promotion order is checked: ruled (a), one predicate for both

**The question:** a route check (`PROMOTION_ORDER_VIOLATION`, FR-429), or an evidence floor
(`uat_deployment`, FR-364, `EVIDENCE_INCOMPLETE`)? **The options:**
- (a) Both.
- (b) The floor only, with the code removed from the stub.
- (c) The route only, with the floor kind removed.

**Ruled: (a), both checks, reading one predicate.** The predicate is: *this Rating Version has
a successful `uat` deployment, or a skip that the workspace policy permits, with its reason
recorded*. The route refuses the act with `PROMOTION_ORDER_VIOLATION`. The `prod` deployment's
approval submission requires the `uat_deployment` evidence kind and refuses with
`EVIDENCE_INCOMPLETE`. A permitted, recorded skip is the `uat_deployment` evidence item.

**Why.**
- The two specs read together say both (the planner's input). They gate different things: the
  floor gates the **submission** of a `prod` deployment for approval, and the route gates the
  **act**. The route also enforces order for any configured environment (FR-428), which the
  `prod`-only floor does not.
- (c) removes a floor kind, which `06` FR-364 forbids.
- (b) leaves non-`prod` promotion order unenforced.
- The one-predicate clause resolves a conflict the question does not name. FR-429 allows a
  policy-permitted, recorded skip, and FR-364 says a policy may never remove a floor kind.
  Read separately, a permitted skip would pass the route and still fail the floor. Treating
  the recorded skip as the evidence item keeps both: the kind is never removed, and the skip
  FR-429 allows is honoured once, with its reason, in one place.

**What it obliges:**
- **This commit:** `07` FR-429 gains a dated amendment stating the two checks and the one
  predicate.
- **Slice 2:** builds both checks on one shared predicate function, which the route and the
  `uat_deployment` verifier both call. It proves each on broken input: *Violation: a `prod`
  deployment with no successful `uat` deployment and no permitted recorded skip is accepted by
  either check.* It also proves the predicate is shared: *Violation: the two checks disagree
  on the same Rating Version.*

## What it obliges

The obligations are stated per slice under each part above. In summary:
- **This commit:** `03` FR-272 (DP-4), `06`'s glossary and §4.1 (DP-6), and `07` FR-429
  (DP-7), each amended and dated.
- ~~**Slice 1 or Slice 4:** `07` FR-437's dated amendment (DP-1).~~ *(2026-09-29, QDP-1: it is
  in this commit. The Phase 3 roadmap row for FR-433 is the lead's, after merge.)*
- **Slice 2:** the Audit Event in the change's transaction (DP-4); `deployment:promote` on
  the deploy route (DP-6); both promotion-order checks on one shared predicate (DP-7).
- **Slice 5:** NFR-489's measured verdict, and a proposal only if RL-921 §4's trigger fires
  (DP-3).
- **Slice 6:** FR-270 and FR-271, default off per environment (DP-2).
- **The close:** NFR-497's verdict is the lead's, with the degraded-read evidence quoted.
- **Plan review 15:** FR-433's owner, and the unassigned ids the entry lists.
- ~~**WK-688 (Phase 4):** FR-272's channel delivery.~~ *(Struck 2026-09-29, Q848-1: FR-272's
  channel is `07` FR-453, and its owner is `OQ-1233`'s.)* ~~**WK-676 (Phase 3):** any
  environment-scoped deploy grant.~~ *(Struck 2026-09-29, Q843-1: the environment scoping of
  `deployment:promote` is `CR-1212` item 4's `06`/`07` spec change, owned by WK-674 and landed
  with its environment record.)*
- **An auditor:** the other permission-name differences between `06` and the code,
  observed under DP-6 and routed by the lead.

## Acceptance — the violation that must become detectable

The violation: **a deployment the specs forbid, reaching `prod` or going unrecorded.** This
record builds nothing, so it proves nothing red itself. Slice 2's leaf plan names these
negative tests, each shown red on deliberately broken input:
- a deployment committed without its Audit Event (DP-4);
- a deploy by a principal without `deployment:promote` (DP-6);
- a `prod` deployment with neither a successful `uat` deployment nor a permitted recorded
  skip, accepted by the route or by the floor (DP-7);
- the route and the floor verifier disagreeing on one Rating Version (DP-7).

Part A's obligations are proven by the slices the entry names: FR-270 and FR-271 default off
(Slice 6), and NFR-489's verdict recorded as measured (Slice 5).

## Adopted by the decision-maker, 2026-09-29

**Why this section exists.** The maintainer's entry `2026-09-29 15:26:00 BST · maintainer (acting on the maintainer's behalf) · STRUCTURE: routing per document-ids §1.6 and the charters; today's technical answers re-homed` (§2) re-homes the
technical points this record files as "the maintainer's answers". Under `document-ids.md` §1.6
(the FR/NFR/DEP, OQ and RL rows) and the decision-maker charter, a technical decision point is
this role's to rule. Each point below was re-verified at origin/main `9cd179cb` and is
**adopted as this record's own ruling**. None is superseded, so no new `RL-` is minted. The
entries that first gave them stay cited above as their source, now read as recommendations.

| Point | Re-verified at `9cd179cb` | Ruling |
|---|---|---|
| **Q848-1** (DP-4): the channel is `07` FR-453. The owner of its deployment-notification limb is `OQ-1233` | `07-platform.md:184` FR-453 names *"deployment notifications"* among its signed webhooks. `03` FR-272's 2026-09-29 amendment cites it. `OQ-1233` is `open` in `docs/open-questions.md` and `07` §10 | **Adopted.** FR-453 is a platform requirement that already names the limb. Building a second channel would duplicate it, and choosing an owner is a scheduling question with real trade-offs. That is why the owner stays an open question, with the recommendation recorded in `OQ-1233` |
| **Q848-2** (DP-7): stands at requirement level, with the premise note. The skip's home is `OQ-1234` | Commands 1–3 below: the only `Environment` class is `backend/src/app/config.py:31`, and there is no Deployment class. `PROMOTION_ORDER_VIOLATION` appears only at `backend/src/app/errors.py:62`. `approvals.py` has 0 skip or promotion fields. `OQ-1234` is `open` | **Adopted.** A requirement-level ruling on objects that WK-674 has yet to build binds the slice that builds them. It does not claim the objects exist. The skip's schema home is a genuine design choice, so it stays an open question |
| **Q848-3**: the Slice 5 proposal goes to the maintainer | *What Part A obliges*, Slice 5 bullet, as corrected | **Adopted, with its reading stated.** If RL-921 §4's trigger fires, the proposed NFR-489 amendment is a spec change, which this role writes and rules (§1.6, FR/NFR/DEP row, the writer column). It relaxes a numbered target that WK-674 closes against, so this role reads it as a **scope change**. That takes the maintainer's acceptance (§1.6, the same row's acceptance column: *"maintainer for … a scope change"*). "Goes to the maintainer" is that acceptance step. It is not a transfer of the ruling |
| **DP-6**, per `CR-1212` item 4 (Q843-1) | `06:62` and `:218-221` carry `deployment:promote`. Command 4 below: 0 check sites (the route is not built). `06` FR-345 (`:81`) still scopes by Datasets, Model Families and Rating Algorithms only | **Adopted.** The name ruling stands. Scoping one permission to named environments is a grant scope, not a new name, so the two rulings are consistent. WK-674 creates the Environment the scope needs, so it owns the `06`/`07` spec change |
| **QDP-1**: the `07` FR-437 amendment moves FR-433 to Phase 3 | `07-platform.md:153` carries the 2026-09-29 amendment. `deploy/` holds `docker-compose.yml`, `keycloak-local/` and `README.md`, and `git ls-files deploy` has no Helm or Kubernetes file | **Adopted**, and completed in this commit: FR-433 (`07:149`) gains a dated pointer to the move, so its own row says what FR-437 already says |
| **QDP-2**: per-environment configuration is `OQ-1235` | `07` FR-446 (`:172`) has three layers and no Environment. `SettingDefinition` (`backend/src/app/platform/settings.py:44-52`) has no environment field. `OQ-1235` is `open` | **Adopted.** This record filed it. The recommendation (a) is this role's |
| **DP-1 (b), DP-2 (a), DP-3 (b)** stand as filed (Q843-3) | DP-1: as QDP-1. DP-2: `03` FR-270 and FR-271 (`03:198-199`) exist, and their per-environment default-off setting waits on `OQ-1235`. DP-3: the RL-921 blob-read removal has landed (`backend/src/app/api/score.py`, the content-hash check before the blob read, docstring at `:168-175`) | **Adopted**, with the two dependencies named: DP-2's per-environment setting resolves only when `OQ-1235` is decided, and DP-3's trigger is below |
| **QDP-3**: the dedicated host for NFR-489 | No repository record names a dedicated host | **Not this role's.** A host is a resource, not a technical decision point. It is the maintainer's to take to the user (the entry above, §4). DP-3's note (*"verdict recorded; the re-measurement trigger cannot validly fire without a dedicated host (RL-921)"*) stands as recorded, and this role rules nothing on it |

**Commands, run at `9cd179cb` from the repository root:**
1. `git grep -nE 'class (Deployment|Environment)\b' -- backend packages`
2. `git grep -n PROMOTION_ORDER_VIOLATION -- backend packages frontend`
3. `grep -niEc 'skip|promot' packages/model-schema/src/model_schema/approvals.py`
4. `git grep -nE '(Perm|Permission)\.DEPLOYMENT_PROMOTE\b' -- backend/src`
