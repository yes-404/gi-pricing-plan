---
id: RL-8142
family: ruling
title: "SL-1260 D1 and D2: date routing is an append-only per-Environment rule written by PUT .../routing under deployment:promote (FR-270 clarified), and the shadow configuration is an append-only per-Environment record behind two Environment-only flags"
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-21   # filed 2026-10-21 under working id 8142
owner: decision-maker
tree: 11bddecb9bcafd315617c2d5d198598c6ecfad33
phase: P2
work: WK-674
slice: SL-1260
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1537, PL-1620, RL-1311, RL-1232, WK-674]
---

# RL-8142 — SL-1260 D1 and D2: date routing is an append-only per-Environment rule written by PUT .../routing under deployment:promote (FR-270 clarified), and the shadow configuration is an append-only per-Environment record behind two Environment-only flags

Filed 2026-10-21 under working id 8142 (a working id until a later seat mints it). It is a
decision-maker draft. The maintainer adopts, amends or rejects it before the mint.

## How this was ruled

The source is the entry "2026-10-21 15:15:40 BST" in `~/gi-pricing-plan.local/channel/to-lead.md`
(local), item 1. Its operative lines, copied from the file by `sed`:

> - **D3 is ruled here, not by the seat: option (i).** […]
> - **D1 and D2 go to the seat.** It rules from the design file and the spec, and I adopt, amend or reject the draft before the mint. The seat must:
>   (a) state whether option B's reading of FR-270's "rejected at deployment time" as "at rule-configuration time" needs a dated clarification on FR-270. If it does, the clarification lands in SL-1260's commit (spec-change skill);
>   (b) give the negative test that no unpromoted version is ever selected;
>   (c) keep scoring with the flag off byte-identical to today's LiveRefs path.

The options are the executor's, in `~/gi-pricing-plan.local/handover/sl1260-design-question-2026-10-21.md`
(72 lines, written at `origin/sl-1260-wk674-s6` @`44248328785b56c848a92c64ff06f012dbb8046a`). They are
evidence, not authority. D3 is not ruled here.

## Verified first, at 11bddecb9bcafd315617c2d5d198598c6ecfad33 (origin/main)

- `docs/specs/03-rating-engine.md:205`, FR-270: "… Overlapping date ranges are rejected at deployment
  time." `:206`, FR-271: "… with results recorded but never returned to the caller …".
  `:1086`: `PUT /api/v1/environments/{env}/shadow` exists in §5.1 with no body. No routing route
  exists in §5.1.
- `03:1098`: `DEPLOY_DATE_RANGE_OVERLAP` is already in "Error codes owned by this module".
  `backend/src/app/errors.py` does not register it (`grep -rn DEPLOY_DATE_RANGE_OVERLAP backend/src`
  prints nothing).
- `03:1026` (§4.12, "Audit actions this Work emits") already names `deployment.routing_changed` and
  `deployment.shadow_configured` (Slice 6), as `PL-1537` R6.2 says.
- `packages/model-schema/src/model_schema/permissions.py:57` `DEPLOYMENT_PROMOTE = "deployment:promote"`;
  `:71` `ADMIN_MANAGE_SETTINGS = "admin:manage_settings"`.
- `packages/model-schema/src/model_schema/deployments.py` holds no routing or shadow shape (its classes:
  `LiveDeployment`, `Environment`, `EnvironmentCreate`, `EnvironmentUpdate`, `Deployment`,
  `SwitchReport`, `DeploymentCreated`, `RollbackCreate`, `DeploymentCreate`, `DeploymentRequest*`).
  `grep -rn -E "RoutingRule|ShadowConfig|ShadowResult|routing_rule|shadow_results" packages backend/src`
  prints nothing.
- `packages/model-schema/src/model_schema/scoring.py:112` `effective_date: date` (the quote's
  effective date); `:209-226` `ScoringResult` carries `rating_version_ref`, `bundle_hash`,
  `premium_ladder`, `outputs`, `decline_reasons`, `trace` and `timing_ms`.
- `packages/pricing-core/src/pricing_core/rating/score.py:297`
  `_SCORING_RESULT_BATCH_EXCLUDED_FIELDS = frozenset({"trace", "timing_ms"})`; `:996` sets `timing_ms`
  from the wall clock, so two calls never agree on it.
- `backend/src/app/api/score.py:213-245` `_serving_ref(live_refs, caller, ctx)` reads this process's
  `LiveRefs` once; an explicit `options.rating_version_ref` is scored as given (`:199-201`).
  `:447` the `score` handler calls it; `:561`, `:588-596` `_maybe_sample_trace` resolves
  `rating.trace_sample_rate` per request through the request's read session (the `RL-1685` pattern).
- `backend/src/app/platform/settings.py:55-60` `SettingScope.ENVIRONMENT` exists; `:75-122`
  `SettingDefinition.coerce` checks type and `min`/`max`/`enum` only, with no database read;
  `:625-627` an Environment setting row is updated in place. `:317-320` `SAFE_DEFAULT` holds the two
  `features.*_enabled` flags.
- `backend/src/app/api/environment_settings.py:51-83`: `PUT /environments/{slug}/settings`, guarded by
  `admin:manage_settings`, writes any declared key and records `setting.updated` with the
  Environment, the key, the old and the new value, in one transaction.
- `backend/src/app/platform/deployments.py:748-754`: a rollback naming a Rating Version that has no
  Deployment row in the Environment is refused 409 `VALIDATION_FAILED` ("… was never deployed to …").
- `docs/plans/PL-01237-*.md:973-998` (Task 6 scope) and `:999-1013` (its gate outline);
  `docs/plans/PL-01537-*.md:242-251` (R6.1 to R6.3) and `:138-149` (the write sets, ":140" the
  "expected … at the path level" sentence); `docs/plans/PL-01620-*.md:26,110-112` leaves Slice 6
  unchanged.
- `RL-1311` item 3 (`docs/rulings/RL-01311-*.md:157-193`): FR-270's and FR-271's flags are
  Environment only; the process layer never supplies one; the resolver reads the stored value per
  request.
- `docs/specs/00-overview.md` has no glossary entry for "routing" or "shadow" (`grep -n -i`).

## Ruled

### D1 — where the date range lives: option B, a per-Environment routing rule

**Ruled: option B.** The date ranges live in a new append-only table `routing_rules`, one row per
write; the latest row of an Environment is its current rule. A new route
`PUT /api/v1/environments/{env}/routing` writes it. Option A and option C are rejected.

**Reason.** A Deployment row is append-only (§4.12), so under option A a range could never be ended
or corrected, and every correction would be refused as an overlap with the row it corrects. Option A
also changes `Deployment`, `DeploymentCreate`, the request pins and the Slice 5 switch path, which a
dated range must then be kept out of. Option B changes none of them. The safeguard of
`PL-1237:994-995` ("selection is only among versions promoted into that environment through
`deployment:promote`") is met by construction: a range may name only a version that has a
Deployment row in that Environment, the predicate `rollback` already uses.

The rule, exactly:

1. **Shapes, in `model-schema`** (CLAUDE.md §2; none exists today, verified above):
   `RoutingRange` (`rating_version_ref`, `effective_from: date`, `effective_to: date | None`, the
   range half-open `[from, to)`, `None` open-ended); `RoutingRuleUpdate` (the body: `ranges`, a list
   of `RoutingRange`, may be empty); `RoutedRange(RoutingRange)` adding `deployment_id`, the id of
   the latest Deployment of that Rating Version in that Environment at write time (server-set,
   the `DeploymentCreated(Deployment)` precedent); `RoutingRule` (the 200 body and the audit
   `after`: `environment` slug, `ranges: list[RoutedRange]`, `written_by`, `written_at`).
   An empty `ranges` is how a rule is cleared. No other route is added: no `GET`, no `DELETE`.
2. **Permission:** `deployment:promote`, with the target Environment as the resource (`06` FR-345,
   as for a Deployment Request). This is `PL-1237:991-992`'s guard on "a deployment carrying a date
   range". The route never reads or writes a flag.
3. **Refusals, in this order**, each writing nothing and no Audit Event:
   unknown Environment 404 `NOT_FOUND`; retired Environment 409 `VALIDATION_FAILED` (as §4.12 for a
   deploy); a reference whose type is not `rating_version` 422 `VALIDATION_FAILED` (§4.12);
   `effective_to` not after `effective_from` 422 `VALIDATION_FAILED`; a Rating Version with no
   Deployment row in this Environment 409 `VALIDATION_FAILED`, naming it and the Environment
   (the rollback wording, `platform/deployments.py:748-754`); two ranges of the rule that overlap
   409 **`DEPLOY_DATE_RANGE_OVERLAP`**, naming both ranges.
4. **Audit:** `deployment.routing_changed`, `entity_ref` `environment:<slug>`, `before` the previous
   `RoutingRule` or `null`, `after` the new one, the writing Principal as actor, **in the same
   transaction as the row** (FR-272, NFR-498).
5. **Selection** applies only to a default-live quote (no `options.rating_version_ref`) when the
   Environment's routing flag (D2 item 1) resolves true. It reads the current rule and the
   Deployment rows it pins through the request's read session, in one read. A range is a
   candidate only if its pinned `deployment_id` is a Deployment row of **this** Environment whose
   `rating_version_ref` equals the range's; any other range is ignored and logged. The quote's
   `effective_date` inside a candidate range selects that range's Rating Version and Deployment;
   outside every range, the quote is scored exactly as `_serving_ref` returns. No per-process
   cache, so a rule write takes effect at the next request.

**(a) FR-270 needs a dated clarification: yes.** Under option B no deploy route ever sees a range,
so FR-270's "at deployment time" would otherwise describe a check that never runs. Silence would
leave the code and the requirement disagreeing (CLAUDE.md §0). The requirement is not reworded.
SL-1260's commit appends this to the FR-270 row of `03-rating-engine.md` §3.10, verbatim:

> *(Clarified 2026-10-21, WK-674 Slice 6, `RL-8142` D1: "deployment time" is the time a date range is assigned to a deployed version. A range is part of the Environment's routing rule, written by `PUT /api/v1/environments/{env}/routing` under `deployment:promote`, not part of a Deployment. A rule whose ranges overlap is refused there with 409 `DEPLOY_DATE_RANGE_OVERLAP` and nothing is written. A range may name only a Rating Version deployed to that Environment. Routing is used only while the Environment's routing flag is on, and only for a quote that names no Rating Version.)*

`RL-8142` in that text becomes this ruling's minted id when it is minted (the standing mint grep).

**(b) The negative test that no unpromoted version is ever selected.** One new file,
`backend/tests/test_routing.py`, marked for FR-270. Fixture: Environments `uat` and `prod` of one
workspace; Rating Version A deployed to `prod` (live); Rating Version B `approved` and compiled,
deployed to `uat` only, and configured as `prod`'s shadow candidate (D2), so it is present in
`prod` in every sense but promotion. The routing flag is on in `prod`.

- **At write:** `PUT /environments/prod/routing` with one range naming B. Assert 409
  `VALIDATION_FAILED`, `routing_rules` has no row for `prod`, and no `deployment.routing_changed`
  event exists.
- **At selection, by cause (selection, not permission; `PL-1237:1002-1004`):** insert a
  `routing_rules` row for `prod` directly, bypassing the route (deliberately broken input), with a
  range naming B, pinned to B's `uat` Deployment id, covering today. `POST /api/v1/score` a
  default-live quote whose `effective_date` is today. Assert the response's `rating_version_ref`
  is A and its `bundle_hash` is A's, and that B's bundle was never loaded for the request (a spy on
  `_compiled_for`'s `ref`). The test is shown red first against a selector that skips the pin
  check.

**(c) Flag off is byte-identical to today's LiveRefs path, and how it is proven.** `_serving_ref`
is not edited (`git diff origin/main -- backend/src/app/api/score.py` shows no hunk inside it).
Routing is a separate step after it, entered only when the flag resolves true and the quote names
no Rating Version. With the flag off the route's result is the one `_serving_ref` gives. Proof, in
`backend/tests/test_routing.py`:

- Fixture: a valid rule in `prod` with a range naming Rating Version D (deployed to `prod` before
  A, so promoted) and covering today; A live.
- Flag off: score a fixed set of quotes (at least one inside and one outside D's range). Each
  response body, parsed and with `timing_ms` removed (the field `pricing_core` itself excludes as
  non-content, `score.py:297`), re-serialised, is byte-equal to the body for the same quote in the
  same fixture with no `routing_rules` row at all. A spy on the routing selector and on the rule
  read records zero calls.
- Flag on (the control that shows the comparison can fail): the quote inside D's range returns
  `rating_version_ref` D.

The flag read is a per-request `settings.resolve` through the request's read session (the
`RL-1685` pattern that `rating.trace_sample_rate` uses, and `RL-1311`'s "the resolver reads the
stored value per request"). It adds one read and no change to the response. Its latency is inside
the p99 check `PL-1237:1010-1011` already owes to the gate on Slice 4's harness; it is not proven
here.

### D2 — the shadow configuration and the shadow results

**Ruled: a variant of option 2b.** The two on/off flags are Environment-only settings (`PL-1537`
R6.1, `RL-1311` item 3). The shadow configuration (candidate and fraction) is an append-only
per-Environment record written only by `PUT /api/v1/environments/{env}/shadow`. Results go to an
append-only `shadow_results` table. Option 2a (the configuration as two more settings) is rejected.

**Reason.** The candidate is a Rating Version reference. It must be checked against the database
(this workspace, compiled, not `draft`). `SettingDefinition.coerce` is type-only and synchronous
(`settings.py:75-122`). The generic `PUT /environments/{slug}/settings` writes any declared key
and records `setting.updated` (`environment_settings.py:51-83`). As a setting, the candidate would
have a second write path that skips the check and records an action other than R6.2's
`deployment.shadow_configured`. Closing that path needs a new exclusion mechanism in the settings
registry. A record written by one route needs none, and its rows keep the history that an in-place
setting row (`settings.py:625-627`) does not. The flags stay settings because `RL-1311` item 3
requires it and the settings route already gives them `PL-1237:1005-1007`'s audit (the
Environment, the key, the old and the new value).

**This is a reading of `PL-1237:989-991`**, which says the shadow configuration is among the
"per-environment settings guarded by `admin:manage_settings`". It is read as per-Environment
configuration under that guard, stored in its own record. The guard and the scope are kept; the
store differs. **The maintainer adopts or amends this reading.** The amendment, if wanted, is
option 2a plus a refusal of the two configuration keys on the generic settings route.

The rule, exactly:

1. **Two settings** in `REGISTRY` (`backend/src/app/platform/settings.py`):
   `features.date_routing_enabled` and `features.shadow_scoring_enabled` (the `features.*_enabled`
   form of `:290,:302`), `BOOL`, default `False`, `feature_flag=True`,
   `scope=SettingScope.ENVIRONMENT`, each in `SAFE_DEFAULT` as `False` (FR-449). They are written by
   the existing `PUT /api/v1/environments/{slug}/settings` under `admin:manage_settings`, which
   records `setting.updated`. **For a flag, that event is FR-272's routing or shadow event** (the
   flag's before and after state, NFR-498); no second event is written for it. R6.1's test
   (`RL-1311:275`) applies: a workspace-level write of either is refused with `SETTING_INVALID`,
   and an Environment-level write enables it in that Environment only.
2. **Shapes, in `model-schema`:** `ShadowConfigUpdate` (the body: `candidate_rating_version_ref`,
   `fraction: float`, `0 < fraction <= 1`); `ShadowConfig` (the 200 body and the audit `after`:
   `environment` slug, `candidate_rating_version_ref`, `candidate_bundle_hash` recorded at write,
   `fraction`, `written_by`, `written_at`). A fraction is a sampling rate, not money.
3. **The route** `PUT /api/v1/environments/{env}/shadow` (§5.1 row exists; its body and responses
   are added): `admin:manage_settings`, Environment as resource. It writes one `shadow_configs` row (append-only, INSERT and SELECT only; the latest row of an Environment is current). Refusals, writing nothing and no
   event: unknown Environment 404 `NOT_FOUND`; retired 409 `VALIDATION_FAILED`; a reference not of
   type `rating_version`, or naming no Rating Version of this workspace, or a `draft` one, 422
   `VALIDATION_FAILED` (a `draft` bundle can still be recompiled, so its results would attach to no
   fixed bundle); no compiled bundle 409 `BUNDLE_COMPILE_FAILED` (§4.12's refusal); `fraction`
   outside `(0, 1]` 422 `VALIDATION_FAILED`. Audit: `deployment.shadow_configured`, `entity_ref`
   `environment:<slug>`, `before` the previous `ShadowConfig` or `null`, `after` the new one, in
   the same transaction as the row. The candidate need not be deployed anywhere: shadow scoring is
   the pre-deployment net (FR-271). It never prices a quote, so `admin:manage_settings` does not
   breach `PL-1237:993-994`'s rule.
4. **Scoring.** For a default-live quote, when `features.shadow_scoring_enabled` resolves true and
   a `ShadowConfig` exists, a draw below `fraction` attaches a background task to the response
   (Starlette's, run after the body is sent). The task scores the same quote against the candidate
   and writes one `shadow_results` row. Its failures are logged, never raised (the
   `_maybe_sample_trace` precedent). The response body is the same with or without it.
5. **`shadow_results`**, append-only (INSERT and SELECT only, as `deployments`): `id`,
   `workspace_id`, `environment_id`, `live_deployment_id` (nullable, as `_serving_ref`'s
   `served_by`), `scored_at`, `live_result` and `candidate_result` as JSONB, each the
   `ScoringResult` of `model-schema` dumped without `trace` and `timing_ms`, so the premiums are
   held exactly as `ScoringResult` holds them (`PL-1237:984-986`). The row holds no `QuoteContext`
   and no quote input, so it is not a quote-input store (NFR-499). It has no new API shape: no route
   reads it in P2. `05` FR-330's reader is Phase-later and owns its read contract.
6. **Tests the gate outline already names** (`PL-1237:999-1013`) apply as written: a shadow result
   never appears in the caller's response; a user without `admin:manage_settings` is refused
   enabling shadow on `prod`, and the companion allowed write records the Environment, the key, the
   old and the new value; a routing change whose transaction commits with no Audit Event is shown
   red on broken input. Flag off: no background task is attached (the response's `background` is
   `None`) and `shadow_results` gains no row.

### Every name these rulings imply, checked at 11bddecb

| Kind | Name | State at origin/main |
|---|---|---|
| Error code | `DEPLOY_DATE_RANGE_OVERLAP` | in `03:1098`; **not** in `errors.py`: SL-1260 registers it |
| Error codes | `VALIDATION_FAILED`, `BUNDLE_COMPILE_FAILED`, `NOT_FOUND`, `SETTING_INVALID` | exist; reused |
| Route | `PUT /api/v1/environments/{env}/routing` | **new**: a §5.1 row |
| Route | `PUT /api/v1/environments/{env}/shadow` | row at `03:1086`; body and responses added |
| Route | `PUT /api/v1/environments/{slug}/settings` | exists (`environment_settings.py:51`); reused for the flags |
| Permission | `deployment:promote`, `admin:manage_settings` | exist (`permissions.py:57,71`) |
| Audit action | `deployment.routing_changed`, `deployment.shadow_configured` | named at `03:1026`; first emitted by SL-1260 |
| Audit action | `setting.updated` | exists (`environment_settings.py:76`) |
| Table | `routing_rules`, `shadow_configs`, `shadow_results` | **new**: one migration |
| Table | `deployments`, `environment_settings` | exist; read only |
| Setting | `features.date_routing_enabled`, `features.shadow_scoring_enabled` | **new**: Environment-only flags |
| Shape | `RoutingRange`, `RoutingRuleUpdate`, `RoutedRange`, `RoutingRule`, `ShadowConfigUpdate`, `ShadowConfig` | **new** in `model-schema`; contracts regenerated |
| Shape | `ScoringResult` | exists; stored, not redefined |

The spec text for the new contracts goes in `03` §4 as a new section after §4.12 (the next free
number at this tree is §4.13), and `03` §5.1 gains the routing row and the shadow row's body. No
new glossary term is needed: the contracts are named by their shapes, and FR-270 and FR-271 already
name the capabilities.

## What it obliges

- SL-1260's commit carries the FR-270 clarification of D1 (a), verbatim, in `03` §3.10, and the
  `03` §4 contracts and §5.1 rows of the table above, by the `spec-change` skill.
- SL-1260 builds D1 items 1 to 5 and D2 items 1 to 6, and registers `DEPLOY_DATE_RANGE_OVERLAP` in
  `backend/src/app/errors.py`. Its `LG-` states the actual write set (D3, option (i)).
- `_serving_ref` in `backend/src/app/api/score.py` is not edited.
- `PL-1237` and `PL-1537` are not edited; this record stands beside them.

## Acceptance — the violation that must become detectable

Each is a test in SL-1260, shown red first on deliberately broken input:

- *Violation: an unpromoted Rating Version prices a quote.* D1 (b)'s two asserts in
  `backend/tests/test_routing.py`, red against a selector without the pin check.
- *Violation: the flag off changes a response.* D1 (c)'s byte comparison and zero-call spy, with
  the flag-on control showing the comparison can fail.
- *Violation: overlapping ranges are stored.* A rule with two overlapping ranges returns 409
  `DEPLOY_DATE_RANGE_OVERLAP` and writes no row, red against a route without the overlap check.
- *Violation: a routing or shadow change commits without its Audit Event.* Red on broken input
  (`PL-1237:1008-1009`).
- *Violation: a shadow result reaches the caller, or a draft or uncompiled candidate is stored.*
  D2 items 3 and 6.

## Not ruled here

- D3 (the write set): the maintainer's, option (i), in the same entry.
- The latency of shadow scoring and of the flag read: measured by the gate item `PL-1237:1010-1011`,
  not ruled.
- `05` FR-330's reader of `shadow_results`: Phase-later, owner unchanged.
