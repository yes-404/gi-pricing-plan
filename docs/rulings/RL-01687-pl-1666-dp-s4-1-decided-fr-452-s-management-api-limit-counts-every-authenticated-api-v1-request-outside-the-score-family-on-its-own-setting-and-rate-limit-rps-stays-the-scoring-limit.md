---
id: RL-1687
family: ruling
title: PL-1666 DP-S4-1 decided — FR-452's management-API limit counts every authenticated /api/v1 request outside the /score family, takes its limit from its own Setting, and a Service Account's rate_limit_rps stays the scoring limit
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-12
owner: decision-maker
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1237, PL-1537, PL-1620, PL-1583, PL-1666, FD-1693, SL-1258, RL-1347, RL-1311, FR-452, FR-446, FR-448, FR-394]
---

# RL-1687 — PL-1666 DP-S4-1: FR-452's management-API limit

*Disclosure: drafted under **working id 9876**, reserved by the lead (team-lead) on 2026-10-12
(`~/gi-pricing-plan.local/handover/eta.md`, the line stamped "2026-10-12 03:12:13 BST":
"RESERVED RL 9876 (free-checked 0/0/0) = DP-S4-1 ruling (FR-452 management limb) by
dm-s4-fr452"). The plan it rules (working id 9865) is unminted, so it is cited as "PL 9865" in
the body and is not in `relates:`. Minted 2026-10-12 as RL-1687 from working id 9876, in D14: "PL 9865"
is now PL-1666 (minted in D13) and the `{RL}`, `{PL}` and `{FD}` placeholders in T1 and T2 are
replaced by RL-1687, PL-1666 and FD-1693. The finding T2 cites (working id 9613, reserved by the
lead in `eta.md`, line stamped "2026-10-12 07:46:27 BST") is minted in D14 as FD-1693. "PL 9865"
and "working id 9876" remain only inside the quoted entries below.*

## How this was ruled

- **The decision point is PL-1666's** (branch `draft/pl-9865` at
  `0c314819d1c5fb1af270ff485d4a29e548f0e749`, the file under `docs/plans/` whose name ends
  `-wk-674-slice-4-fd-9704-round-trip-fr-452-management-limb-and-activation-work-plan-delta.md`;
  its working-id prefix is elided here because it does not resolve before the mint),
  §"Decision points", row DP-S4-1, and its D4.5. This record rules it as `document-ids.md` §1.6's
  PL row requires (*"decision-maker rules decision points as `RL-`, never edits the plan"*). It
  chooses only among the options that row lists: (1a)/(1b), (2a)/(2b), (3a)/(3b).
- **The routing.** The maintainer (by delegation), `~/gi-pricing-plan.local/channel/to-lead.md`
  (a local file, cited by entry header), entry *"2026-10-12 02:53:52 BST — Readiness rulings: GO
  S6 SL-1548 (swap planner-wk673-c out); FD 9862 LOW, owner WK-677; PL 9864 + PL 9865 deltas OK;
  FD 9860 (ii)"*, item 4: *"WK-674 S4: PL 9865 delta with FD 9704's round-trip test, OK. DP-S4-1
  goes to a decision-maker when a seat frees (medium unless it writes spec text)."* This record
  writes spec text (T1, T2), so the raise applies.
- **The raise.** The same file, entry *"2026-10-12 03:08:30 BST — (1) noted, close after the
  SIGINT report; (2) the frontend image is FR-432's THIRD limb, so FD 9860 lists all three and
  FR-432 stays open until all land; (3) integers stay accepted; (4) HIGH, separate CLI: agreed"*,
  item 4: *"Agreed: DP-S4-1 goes to a decision-maker at HIGH, as a separate CLI with transcript
  verification, when a seat frees."* The lead relayed it in `eta.md`, line stamped
  "2026-10-12 03:08:51 BST": *"(4) DP-S4-1 DM at HIGH (separate CLI, transcript-verified) when a
  seat frees"*.
- **Effort.** The role's default is medium; a decision-maker ruling runs at high on the
  maintainer's raise (`.claude/roles/decision-maker.md:13`). It is in force for this record, on
  two checks:
  - **the process command line**, read by this seat from its parent process:
    `claude --model opus --effort high --name dm-s4-fr452 --dangerously-skip-permissions …`; the
    lead read the same (from-lead "2026-10-12 03:12:39 BST", sent to this seat);
  - **the transcript**
    `~/.claude/projects/-home-puzhenhao1989-gi-pricing-plan/c279b2f1-a618-4960-a02d-d50986d17b83.jsonl`:
    the lead read `"perTurnEffort":"high"` ×3 with `requestedModel` `claude-opus-5-5` (the same
    from-lead message), and this seat re-read it at 03:18:06 BST: `"perTurnEffort":"high"` ×107,
    `"effort":"high"` ×107, `"requestedModel":"claude-opus-5-5"` ×107, and no other value of
    any of the three fields.
  - **The route that failed first.** Seats spawned through the Agent tool with its effort
    parameter set read medium. This seat re-read both transcripts at 03:13 BST:
    `92d4dee8-193d-45d7-bd24-bcbec2aff94f.jsonl` (`"perTurnEffort":"medium"` ×19) and
    `7efcf3a0-76e3-491f-93f4-e9a5b446451f.jsonl` (`"perTurnEffort":"medium"` ×40), no `high` in
    either; both carry `"agentName":"dm-pl1454"`, between 01:23:08Z and 01:26:36Z. The route
    rule is the to-lead entry "2026-10-12 02:26:23 BST" (*"a separate CLI process with
    --effort high, verified by the transcript field"*).

## Locators — read at `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9`

- `docs/specs/07-platform.md:183`, FR-452. Its base clause: *"Rate limiting is applied per
  Principal and per environment, with scoring limits configured separately from management-API
  limits, and `429` responses carrying `Retry-After`."* Its 2026-09-30 amendment (`RL-1347`)
  defines the scoring limit only and ends: *"The management-API limit is not delivered by this
  clause and has no owner yet. *(Amended 2026-10-10, WK-674 Slice 3, `PL-1583`, DP-S3E-3 (a):
  the management-API limb is placed in WK-674 Slice 4 (`SL-1258`), `PL-1537` R4.1; …)*
  `RL-1347` lists it for the lead."* So the spec names a management limit and defines nothing of
  it: no route set, no limit source, no rule for `rate_limit_rps`.
- `backend/src/app/platform/rate_limit.py:77-84`, `RateLimiter.key(route, environment,
  principal_kind, principal_id, window)` → `gip:ratelimit:{route}:{environment or ''}:{principal_kind}:{principal_id}:{window}`.
  `:112-123`, `enforce(limiter, database, settings, *, route, default_setting, workspace_id,
  environment, principal, account_limit)`. `:130-140`: the limit is `account_limit` if set,
  else the resolved `default_setting`, else none, and with none it returns before
  `limiter.admit` (no counter call). The module docstring (`:5-7`): *"The module is route-class
  aware (`route`), so that Slice 4 can reuse it for the management API under a separate key and
  limit (`PL-1537` R4.1); this slice passes only `"score"`."*
- `backend/src/app/api/score.py:141-156`, the one caller: `route="score"`,
  `default_setting="scoring.default_client_rate_limit_rps"`,
  `account_limit=caller.rate_limit_rps`, run as a dependency on `ScoreExecuteDep`, so after
  authentication and `score:execute`. The `/score` family is three routes: `POST /score`
  (`:378-379`), `POST /score/compare` (`:460-461`), `POST /score/batch` (`:607-608`).
- `backend/src/app/api/deps.py:60-73`, `Caller`: `rate_limit_rps: int | None` with the comment
  *"The Service Account's own scoring rate limit, `None` for any other caller (FR-452)."*
- `backend/src/app/platform/settings.py:232-242`, the definition of
  `scoring.default_client_rate_limit_rps`: `SettingType.INT`, `default=None`,
  `constraints={"min": 1}`, `scope=SettingScope.WORKSPACE_OR_ENVIRONMENT`, description *"`07`
  FR-452's default rate limit for `POST /api/v1/score` …"*. No registry key starts `platform.`.
- `backend/src/app/main.py:67`, `API_PREFIX = "/api/v1"`. `:141`, `health.router` is included
  **without** the prefix, so `/healthz`, `/readyz` and `/metrics` (`health.py:98`, `:104-105`,
  `:136-137`) are outside `/api/v1`, as are `/version` (`main.py:170-171`) and `/openapi.json`
  (`main.py:122`). `:181-182`, `GET /api/v1/auth/config`, mounted **with** the prefix and
  unauthenticated by design (FR-394, `07:78`; the comment at `main.py:178-180`).
- `backend/src/app/api/deps.py:203-249`, `require_caller`: the bearer, API-key and development
  paths each resolve a `Caller`. Route authorisation is `requires(Permission…)`
  (`backend/src/app/api/authz.py:54`), declared per route (for example `datasets.py:87-88`,
  `models.py:115-117`, `jobs.py:62-63`).
- `RL-1347` §"Ruled" rule 4 (*"The limit runs after authentication and after the `score:execute`
  check, so a 401 or a 403 is never counted"*), rule 5 (fail open, `gip_rate_limit_unenforced_total`
  with one label, `environment`) and rule 2 (*"Otherwise, no limit. The request is admitted and
  **Redis is not called**."*).
- `PL-1537` R4.1 (`PL-1537:165-180`) and its Acceptance item 4 (`:85-88`); `PL-1620` D4.1
  (`PL-1620:144-154`), whose stop condition is a second key that changes the scoring limb's
  behaviour.
- The authored S4 branch `origin/sl-1258-wk674-s4` at `a04ff676`: its ledger (commit
  `1698959d`) marks Task C *"PARKED: it re-derives against S3's limiter, which is not on main"*.
  S3 is on main now (`fe80aec6`, #1280, per PL-1666 D0.4). Nothing of Task C is written on that
  branch, so this ruling replaces no code.

## `CLAUDE.md` §0 — spec and code

There is no disagreement to resolve. The spec names a management limit and leaves it undefined;
the code builds no management limit and has the parameters one needs (`rate_limit.py:5-7`,
`:77-84`, `:112-123`). This is a gap in the spec, which PL-1666 D4.5 orders filled spec-first.

## DP-S4-1 (1) — the routes counted: **(1a)**

**Ruled (1a): every `/api/v1/*` request outside the `/score` family is counted, once it carries
an authenticated Principal.** The `/score` family is `POST /api/v1/score`, `/score/compare` and
`/score/batch`.

- **One counter for the whole management API**, per (Environment, Principal) per fixed
  one-second window, under the route class `"management"`. The key is `RateLimiter.key`'s
  (`rate_limit.py:77-84`) with `route="management"`, so
  `gip:ratelimit:management:{environment}:{principal_kind}:{principal_id}:{window}`. It is not a
  counter per route. The scoring key keeps `route="score"` and is not touched, so `/score` and
  the management API never share a count (`PL-1537` R4.1's second red case).
- **A request is counted by one limit or by none, never by both.** `POST /score` is counted by
  the scoring limit only. `/score/batch` and `/score/compare` stay counted by neither, as
  `RL-1347` rule 6 ruled; this ruling does not reopen that.
- **The probes are already outside.** `/healthz`, `/readyz`, `/metrics`, `/version` and
  `/openapi.json` are not under `/api/v1` (`main.py:141`, `:170-171`, `:122`), so (1a)'s "except
  the health probes" holds by the mount and needs no exclusion list.
- **A request with no Principal is not counted.** FR-452 is "per Principal", and the key needs
  one. That covers `GET /api/v1/auth/config`, which is unauthenticated by design (FR-394), and
  every request refused `401`. The limit never adds authentication to a route that has none.
- **The order is the scoring limit's** (`RL-1347` rule 4, applied unchanged): the count runs
  after authentication and after the route's own permission check where the route declares one,
  and before the route does any work. So a `401` or a `403` is never counted, and a refused
  request does nothing and persists nothing.
- **Why (1a), not (1b).** FR-452's clause is "management-API limits", with no method in it; a
  limit on state-changing methods only would leave the read surface uncounted, and reads are
  most of the management traffic (NFR-526 budgets them). (1a) is also the only option with no
  list for the spec to keep in step with the routes: a route added later under `/api/v1` is
  counted with no edit. (1b) needs a per-method rule that every new route must be checked
  against, and a `POST` that only reads (as `/score/compare` does) shows that method is a proxy
  for "state-changing", not the property itself.

## DP-S4-1 (2) — where the limit comes from: **(2a)**

**Ruled (2a): a new Setting, `platform.default_management_rate_limit_rps`.** The name is PL-1666's
own example, fixed here as the contract name.

- **Its definition** mirrors `scoring.default_client_rate_limit_rps`'s (`settings.py:232-242`):
  type `int`, `default=None`, `constraints={"min": 1}`, scope **workspace or Environment**
  (`SettingScope.WORKSPACE_OR_ENVIRONMENT`), and a description that names FR-452's management
  limit, says it is unset by default and says that with no limit the request is admitted without
  a counter call.
- **It is resolved by §3.8** (FR-446, `RL-1311`) with the caller's Environment, as the scoring
  Setting is (`rate_limit.py:130-136`): the Environment the presented key was verified for, and
  none for a bearer or development caller, whose resolution then skips the Environment layer.
- **Unset by default, so nothing changes for a deployment that sets nothing**: no request is
  refused and Redis is not called (`RL-1347` rule 2's path). The Setting resolution itself does
  run on each counted request (see **Consequences, stated**).
- **`min: 1` means there is no lockout.** An Admin always gets at least one request per second,
  so a value set too low can be raised again through `PUT /api/v1/settings` or `PUT /api/v1/environments/{slug}/settings`
  (`api/settings.py:72-73`, `api/environment_settings.py:51-52`). The process variable (FR-446's first layer) is also an override.
- **Why (2a), not (2b).** FR-452 says scoring limits are "configured separately from
  management-API limits". (2b) puts both limbs on one Setting, which is the configuration the
  clause excludes. It would also change what `scoring.default_client_rate_limit_rps` means,
  whose description and spec text name `POST /api/v1/score` only. That is a change to the
  scoring limb, which is `PL-1620` D4.1's stop condition.

## DP-S4-1 (3) — a Service Account's `rate_limit_rps`: **(3a)**

**Ruled (3a): no. `rate_limit_rps` is the scoring limit only and never applies to the management
counter.** A Service Account's management calls are limited by
`platform.default_management_rate_limit_rps`, like every other Principal's.

- `enforce`'s `account_limit` is passed as `None` for the management limb, so the limit is
  always the resolved Setting or none.
- **Why (3a), not (3b).** The value is already defined as the scoring limit in three places:
  FR-452's 2026-09-30 amendment (*"The limit is the Service Account's own `rate_limit_rps` when it
  is set"*, in the scoring clause), `07` §4.3's `ServiceAccount` example, and `Caller`'s comment
  (`deps.py:71-72`, *"The Service Account's own scoring rate limit"*). (3b) makes one number
  govern both limbs, which is the configuration FR-452's "configured separately" excludes, and
  the magnitudes differ: a Consumer System sized for hundreds of quotes a second has no reason to
  get the same management rate.

## Consequences, stated (not options)

- **Fail open, the metric and the refusal are the scoring limb's, unchanged.** A `RedisError`
  admits the request, logs one warning and counts on `gip_rate_limit_unenforced_total` with its
  one `environment` label (`rate_limit.py:101-108`). No `route` label is added: that would change
  the scoring limb's metric, `PL-1620` D4.1's stop condition. So the series counts outages of both
  limbs together, which is what it measures: the counter was not reachable. The refusal is
  `refusal(limit)` (`rate_limit.py:55-63`): `429 RATE_LIMITED`, `Retry-After: 1`.
- **A per-request Setting read on the management API.** With the Setting unset, each counted
  request still opens a session and runs `settings.resolve` (`settings.py:369-395`: the
  Environment row when an Environment is named, then the workspace row) before it knows there is
  no limit. The scoring limb pays the same on `/score`. On the management API it is every
  authenticated metadata read, which NFR-526 budgets (p95 < 300 ms). This ruling does not add a
  cache; see **Raised to the lead**.
- **The browser is a Principal like any other.** A page load issues several reads at once under
  one bearer Principal, so a management limit set below that burst refuses page loads. That is
  an operator's choice made by setting the value; the unset default avoids it.

## The spec text

T1 and T2 are **ruling text only**. S4's executor applies them in `SL-1258`, before its Task C
code commit (PL-1666 D4.5 and Acceptance item 4), after this record is minted; the ids in the
text are the minted ones (RL-1687, PL-1666, and FD-1693 for the finding drafted under working id
9613). Each find string was counted with
`grep -cF` = 1 in `docs/specs/07-platform.md` at `fc4401dc`.

### T1 — FR-452's cell (`07` §3.9, `07:183`): append after its last sentence

Find:

```
`RL-1347` lists it for the lead. |
```

Replace:

```
`RL-1347` lists it for the lead. **Amended 2026-10-12 (`RL-1687`, `PL-1666` DP-S4-1 (1a), (2a), (3a)): the management-API limit, WK-674 Slice 4.** Every `/api/v1/*` request outside the `/score` family (`/score`, `/score/batch`, `/score/compare`) is counted in a second shared Redis counter, one per (Environment, Principal) per fixed one-second window, separate from the scoring counter. A request is counted by one limit or by none, never by both. The health probes, `/metrics`, `/version` and `/openapi.json` are outside `/api/v1` and are not counted. A request with no Principal is not counted: `GET /api/v1/auth/config` (FR-394) and any request refused `401`. The count runs after authentication and after the route's own permission check, as the scoring limit's does, so a `401` or a `403` is never counted, and before the route does any work. The limit is the Setting `platform.default_management_rate_limit_rps`, resolved by §3.8 with the caller's Environment and declared for workspace or Environment scope (FR-446). It is unset by default, and with no limit the request is admitted without a counter call. A Service Account's own `rate_limit_rps` is the scoring limit only and never applies to this counter. The Environment, the refusal (`429 RATE_LIMITED`, `Retry-After: 1`) and the fail-open rule (admitted, logged, and counted on `gip_rate_limit_unenforced_total` by Environment) are the scoring limit's. The sentence above saying the management-API limit is not delivered by this clause is superseded. |
```

### T2 — FR-448's cell (`07` §3.8): append after its last sentence

Find:

```
RL-889.)* |
```

Replace:

```
RL-889.)* **`platform.default_management_rate_limit_rps` joins the list, unset by default and declared for workspace or Environment scope** *(added 2026-10-12, WK-674 Slice 4, `RL-1687`: FR-452's management-API limit. Unset by default for the reason `scoring.default_client_rate_limit_rps` is (FR-452, `RL-1347`): with no limit the request is admitted without a counter call, so a deployment that sets nothing is unchanged. FR-448's list also omits two existing keys declared for workspace or Environment scope, `scoring.default_client_rate_limit_rps` and `rating.trace_sample_rate`: a LOW finding, `FD-1693`, owner WK-674, not fixed here.)* |
```

**Two choices in the wording, stated.** (1) T1 names no number: the window, the key spelling
and the label set are `RL-1347`'s and the code's, and a figure copied into the spec is the copy
that goes stale ([`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md)).
(2) T2 adds only this record's key. `scoring.default_client_rate_limit_rps` and
`rating.trace_sample_rate` are not in FR-448's list either; that list is not the registry
(`settings.py` is), and widening it is not DP-S4-1's. T2 names the gap and cites its finding
(FD-1693) instead (see **Raised to the lead**, the FR-448 bullet).

## What it does not change

- **The scoring limit**: its key, its Setting, `rate_limit_rps`, its order, its metric and
  `RL-1347` rule 6 (`/score/batch`, `/score/compare` uncounted). `RL-1347` is not superseded.
- **`PL-1537`, `PL-1620` and PL-1666**: no plan is edited. PL-1666 goes `active` by its own dated
  line once this record is minted (PL-1666 §"Decision points", last paragraph).
- **No code is written by this record.** The decision-maker has no write access to a code
  worktree.

## What it obliges

- **`SL-1258`'s executor (Task C):** apply T1 and T2 by content, in a commit before the code
  (PL-1666 D4.5); declare the Setting in `settings.py`'s registry as **DP-S4-1 (2)** says; call
  `enforce` for every counted request with `route="management"`,
  `default_setting="platform.default_management_rate_limit_rps"` and `account_limit=None`, after
  authentication and the route's permission check; leave `score.py:141-156` unchanged. The `LG-`
  quotes where the check is placed and how a route added later under `/api/v1` is counted
  without an edit.
- **At the mint (the minter):** done 2026-10-12: this record's own id is RL-1687 and "PL 9865"
  reads PL-1666; `PL-1666` and `FD-1693` are added to `relates:`.

## Acceptance — the violation that must become detectable

Tests named `test_management_rate_limit_*`, marked `req("FR-452")`, each seen red by its cause
(`PL-1537` Acceptance item 4 requires at least 2; 1 and 2 are R4.1's own cases):

1. **Counted and refused.** With `platform.default_management_rate_limit_rps` = 2 for the
   workspace, a third management read by one Principal inside one fixed window answers `429
   RATE_LIMITED` with `Retry-After: 1`. Red: no limit applied, the third read answers 200.
2. **Separate from scoring.** With the management limit exhausted in a window, `POST /score` by
   the same Principal, under its own limit, is admitted. Red: one shared counter.
3. **(3a).** A Service Account with `rate_limit_rps` = 1 and the management Setting unset makes
   three management calls in one window: all are admitted, and Redis is not called. Red: the
   account's rate applied to the management counter.
4. **No Principal, no count.** `GET /api/v1/auth/config` past the limit is never refused; a
   request refused `401` or `403` leaves the management count unchanged.

The observable breach in the product: with the Setting set, any `/api/v1` route outside the
`/score` family that a Principal can call more than the limit in one second without a `429`.

## Raised to the lead (not ruled here)

- **Whether each counted route's OpenAPI entry declares `429`.** `RL-1347` rule 4 added it to
  `/score`'s entry and regenerated the contract (FR-451). For the management API it is every
  `/api/v1` operation but `/api/v1/auth/config`. Recommendation: declare it by one mechanism on
  the included routers, regenerated in the same commit, so the generated client knows the
  status. It is not in DP-S4-1's options, so it is put, not picked.
- **The per-request Setting read** (above). Recommendation: measure it in S4's harness against
  NFR-526 before deciding anything, as `RL-1347` Acceptance 9 measured the scoring limiter's own
  cost; no cache without a measurement.
- **FR-448's list is not the registry**: two `workspace_or_environment` keys already in
  `settings.py` are not in it. Whether to list them is a spec tidy, not this decision point.
  *Ruled 2026-10-12 by the maintainer (by delegation), to-lead entry "2026-10-12 07:44:13 BST",
  item (3): "a LOW FD (doc drift) in D14, owner WK-674, cited in T2. Not fixed by widening T2."
  The finding was reserved as working id 9613 (the lead, from-lead "2026-10-12 07:46:27 BST") and is
  minted as FD-1693; T2 cites it.*
- **"Before the code" or "one commit".** PL-1666 D4.5 and its Acceptance item 4 put T1/T2 "in a
  commit before the code"; this seat's brief says the executor applies them "in one commit with
  the code, CLAUDE.md §2". Both keep spec and code in one PR; which commit shape `SL-1258` uses
  is the lead's reading, and T1/T2 are the same either way.

## Ruled

DP-S4-1 = **(1a), (2a), (3a)**, PL-1666's recommendation, with the route set made exact (the
`/score` family excluded, a request without a Principal uncounted, `RL-1347` rule 4's order),
the Setting fixed as `platform.default_management_rate_limit_rps` (int, unset, min 1, workspace
or Environment), and `rate_limit_rps` held to the scoring limit. T1 amends FR-452 and T2 amends
FR-448, applied by `SL-1258`.
