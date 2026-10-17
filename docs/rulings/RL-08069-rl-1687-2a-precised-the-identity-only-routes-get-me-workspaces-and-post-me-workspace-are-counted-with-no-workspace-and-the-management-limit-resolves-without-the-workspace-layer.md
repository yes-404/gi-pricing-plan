---
id: RL-8069
family: ruling
title: RL-1687 (2a) precised — the identity-only routes GET /me/workspaces and POST /me/workspace are counted by the management-API limit with no workspace, and its Setting resolves without the workspace layer for them (DP-S4-ME → (A))
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-16
owner: decision-maker
tree: a2f77b2dcad5aaec41a5f10aa664383caf421e8b
phase: P2
work: WK-674
slice: SL-1258
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1687, PL-1666, SL-1258, FR-452, FR-446, FR-397, FR-396, RL-1311, RL-1347]
---

# RL-8069 — RL-1687 (2a) precised: the identity-only routes count with no workspace

*Disclosure: drafted under **working id RL 8069**, reserved by the lead in
`~/gi-pricing-plan.local/handover/eta.md` (line 1968 at the time of writing): "8069 RL (precises
RL-1687 (3a): identity-only routes counted with workspace_id=None, the maintainer 10:31:43;
decision-maker-8069, rl-8069-rl1687-3a-identity-2026-10-16)". [That reservation line, and the
branch name, carry the "(3a)" mislabel that the maintainer corrected at 10:36:38 (see **How this
was ruled**); the branch is not renamed.] The lead mints it; the mint sweep replaces the working
id. First written 2026-10-16 from 10:34:37 BST by the decision-maker (seat decision-maker-8069);
amended before merge from 10:37:56 BST (`TZ=Europe/London date`) by seat decision-maker-8069b
(effort medium, inherited; no raise), on the maintainer's 10:36:38 entry. **No test or code was
run**: every claim about behaviour below is a reading of the code at the named tree,
`origin/main` @`a2f77b2dcad5aaec41a5f10aa664383caf421e8b`.*

## How this was ruled

- **The decision is the maintainer's**, in two entries in
  `~/gi-pricing-plan.local/channel/to-lead.md`. The decision-maker drafts it and rules nothing
  here.
- **The first entry** is "2026-10-16 10:31:43 BST — Maintainer: DP-S4-ME → (A); CORRECTION of my
  10:27:41 Q-a; LG 9810 direct-write table". Its first paragraph, verbatim (its "(3a)" is the
  mislabel the second entry corrects):

  > DP-S4-ME → (A). `/me/workspaces` and `POST /me/workspace` are identity-level, not
  > workspace-scoped, so they count with workspace_id=None and `resolve` skips the workspace layer
  > (Environment → default). (B) leaves users silently uncounted; (C) is arbitrary. PLACEMENT: a
  > new RL in the next D batch. It "precises RL-1687 (3a)" (RL-1687's body is frozen, so this is
  > not an addendum). The decision-maker drafts it from THIS entry verbatim; S4 cites this entry
  > until it is minted. Red per route; the LG states the resolve path.

  The rest of that entry (the re-ruled Q-a, items (1a), (1b), (4), (5), and LG 9810's table) is
  not part of this ruling and is not restated here.
- **The second entry** is "2026-10-16 10:36:38 BST — Maintainer: RL 8069 Q1 + Q2 — both YES;
  CORRECTION of my 10:31:43 label". It answers the two questions this record's first draft
  raised. Verbatim:

  > CORRECTION: my 10:31:43 wrote "precises RL-1687 (3a)" from the lead's label without reading
  > the clause. Read now at origin/main: (3a) (around :186-190) is the Service Account
  > `rate_limit_rps` clause; the scope and resolution clause is (2a) (around :165-173).
  > Q1 YES: RL 8069 "precises RL-1687 (2a)". (3a) is untouched and not cited as changed.
  > Q2 YES: only the WORKSPACE layer is skipped. FR-446's order otherwise holds as `resolve`
  > implements it (`backend/src/app/platform/settings.py` around :384-396: `_env_candidate`
  > process variable, then Environment, then workspace). For an identity-level call: process
  > variable GIP_SETTING_<KEY> → Environment → default.
  > PRECISION, from (2a)'s own text: the Environment layer applies only when the caller presented
  > a key verified for an Environment. For a bearer or development caller, (2a) already skips it,
  > so a typical `/me` call resolves process variable → default. RL 8069 says both cases, citing
  > (2a) for the second, and the per-route reds cover a bearer caller.

  So the maintainer corrected the label of the 10:31:43 entry in their own words: the precised
  clause is (2a), not (3a).
- **Where the mislabel came from.** The lead's entry "2026-10-16 10:36:20 BST — Lead:
  decision-maker-8069 DONE — RL 8069 drafted; a LEAD RELAY ERROR on the locator; two questions
  for the maintainer" in `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md` records it,
  verbatim: *"my DP-S4-ME (10:31:10) said "RL-1687 (3a)", carried from executor-1258g's report
  without reading RL-1687. … The maintainer's 10:31:43 inherited "(3a)" from me."*
- **The decision point it answers** is the lead's "DP-S4-ME", the entry "2026-10-16 10:31:10 BST —
  Lead: executor-1258g STOPPED on Q-c (as 10:27:41 requires); DP-S4-ME + the unstamped direct
  writes, for the maintainer" in `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`. Its
  options, verbatim (its "(3a)" is the same relayed mislabel):

  > **DP-S4-ME:** (A) Identity routes count with workspace_id=None and `resolve` skips the
  > workspace layer (limit = env layer + default), plus a one-line RL-1687 (3a) addendum that
  > workspace overrides do not apply to these two routes; ~30 min, red-first. (B) count only with
  > exactly one membership — leaves multi-workspace users uncounted (the silent exclusion barred).
  > (C) first/any membership — arbitrary. **Recommend (A)**; the addendum would be a dated line by
  > whoever owns RL-1687 amendments (the maintainer's to name).

  The maintainer chose (A) and replaced the "addendum" with this separate record, because
  RL-1687's body is frozen.
- **Why `relates:` and not `corrects:` or `supersedes:`.** `document-ids.md` §1.6's RL row gives
  two linkages: `supersedes:` when a ruling is replaced, and (§1.5) `corrects:` on a record that
  corrects a frozen one. RL-1687 is neither replaced nor wrong: the maintainer calls this a
  precision. So RL-1687 stays `active`, its `corrected_by:` is not appended, and this record only
  `relates:` it. Recent rulings that narrow another without replacing it do the same
  (`RL-1700`, `RL-1712`: `supersedes: []`, `corrects: ~`).

## Verified first, at `a2f77b2d`

- **The two routes take an Identity, not a Caller.** `backend/src/app/api/me.py:180-181` is
  `@router.get("/me/workspaces", …)` and `:215-216` is `@router.post("/me/workspace", …)`; both
  take `identity: IdentityDep` (`:186`, `:222`).
- **An Identity has no workspace.** `backend/src/app/api/deps.py:92` is `class Identity:`, with
  the fields `principal: Principal` and `workspaces: frozenset[UUID]` (`:100-101`): zero or more
  memberships and no selection. Its docstring (`:93-98`) says `require_caller` "resolves a
  selection and refuses rather than defaulting (`FR-397`); this does neither", and that the class
  exists for "the switch endpoints in `me.py`". FR-397 (`docs/specs/07-platform.md:81`) is the
  verified `Workspace-Id` header.
- **The limit's resolution needs a workspace today.** `backend/src/app/platform/rate_limit.py:112-122`
  declares `enforce(…, workspace_id: UUID, environment: str | None, …)`, and
  `backend/src/app/platform/settings.py:369-375` declares `resolve(session, settings,
  workspace_id: UUID, key, environment=None)`. Neither signature accepts `None` at this tree. So
  (A) is a code change in `rate_limit.py` and `settings.py`, which SL-1258 carries.
- **`resolve`'s order.** `settings.py:384-393` reads the three candidates: the process variable
  (`_env_candidate`, `:384`), the Environment row (`_environment_value`, `:385`) and the
  `WorkspaceSettingRow` filtered by `workspace_id` (`:386-393`). `:395` passes them to
  `_resolution`, whose precedence is `:488-495`: process variable, then Environment, then
  workspace, then `definition.default`. `_environment_value` returns `None` when no Environment
  is named (`:358-359`). `_env_candidate` skips the process variable only for an
  Environment-only Setting (`:444-451`), which `platform.default_management_rate_limit_rps` is
  not: RL-1687 (2a) gives it scope workspace or Environment.
- **`counted_caller` is not on `main`.** The lead's 10:31:10 entry cites `me.py:42`
  (`counted_caller`) for `GET /me`. That is on SL-1258's branch (`@37df0a3c`, per the same entry),
  not at `a2f77b2d`. This record does not cite it as a fact at its tree.

## The clause precised: RL-1687 (2a)

In RL-1687
(`docs/rulings/RL-01687-pl-1666-dp-s4-1-decided-fr-452-s-management-api-limit-counts-every-authenticated-api-v1-request-outside-the-score-family-on-its-own-setting-and-rate-limit-rps-stays-the-scoring-limit.md`,
at `a2f77b2d`), the precised clause is (2a)'s scope and resolution, lines 167-173, verbatim:

> type `int`, `default=None`, `constraints={"min": 1}`, scope **workspace or Environment**
> (`SettingScope.WORKSPACE_OR_ENVIRONMENT`), and a description that names FR-452's management
> limit, says it is unset by default and says that with no limit the request is admitted without
> a counter call.
> - **It is resolved by §3.8** (FR-446, `RL-1311`) with the caller's Environment, as the scoring
> Setting is (`rate_limit.py:130-136`): the Environment the presented key was verified for, and
> none for a bearer or development caller, whose resolution then skips the Environment layer.

and RL-1687's **Consequences, stated**, lines 210-213, verbatim:

> - **A per-request Setting read on the management API.** With the Setting unset, each counted
> request still opens a session and runs `settings.resolve` (`settings.py:369-395`: the
> Environment row when an Environment is named, then the workspace row) before it knows there is
> no limit.

RL-1687 (3a), the Service Account `rate_limit_rps` clause (lines 188-190), is untouched by this
record and not changed by it.

## Ruled

*Ruled by the maintainer, 2026-10-16 10:31:43 BST and 10:36:38 BST (`to-lead.md`). The
heading was "Ruled (the maintainer, 2026-10-16 10:31:43 BST and 10:36:38 BST)" until
2026-10-17; check 37 matches the RL template's heading `Ruled` exactly, so the attribution
moved here.*

For the two identity-only routes, `GET /api/v1/me/workspaces` and `POST /api/v1/me/workspace`:

1. **They are counted** by FR-452's management-API limit, as RL-1687 (1a) already requires of
   every authenticated `/api/v1/*` request outside the `/score` family. The maintainer's words
   (10:31:43): *"they count with workspace_id=None"*. Option (B), counting only a principal with
   exactly one membership, is refused: *"(B) leaves users silently uncounted"*. Option (C), the
   first or any membership, is refused: *"(C) is arbitrary"*.
2. **Only the workspace layer is skipped.** The maintainer's words (10:36:38): *"only the
   WORKSPACE layer is skipped. FR-446's order otherwise holds as `resolve` implements it"*. For
   these two routes the Setting `platform.default_management_rate_limit_rps` resolves as
   **process variable `GIP_SETTING_<KEY>` → Environment → default**, which is `_resolution`'s
   precedence (`settings.py:488-495`) with the workspace candidate absent. The Setting keeps the
   levels RL-1687 (2a) declared; only the lookup for these two routes has no workspace to read.
   The two cases:
   - **A caller with an API key verified for an Environment**: process variable → that
     Environment's setting → default.
   - **A bearer or development caller**: RL-1687 (2a) already skips the Environment layer for it
     (*"none for a bearer or development caller, whose resolution then skips the Environment
     layer"*, lines 171-173), so the order is **process variable → default**. This is the
     typical `/me` call.
3. **The test is red per route, and the slice's `LG-` states the resolve path**: *"Red per route;
   the LG states the resolve path."* (10:31:43). The per-route reds cover a bearer caller
   (10:36:38).

## What this means for RL-1687 (2a)'s workspace overrides

- **A workspace-level value of `platform.default_management_rate_limit_rps` does not apply to
  these two routes.** This is the lead's DP (A) clause, *"workspace overrides do not apply to
  these two routes"*, which the maintainer adopted in substance and placed here. A workspace
  override still applies to every other counted route, through the Caller's verified workspace
  (FR-397).
- **The process variable and an Environment value still apply to them**, as item 2 states.
- **The Redis key is unchanged.** RL-1687 (1a)'s key is per (Environment, Principal), with no
  workspace in it, so these routes share the Principal's one management counter with its other
  management requests.

## Consequences, stated (not options)

- **The layers left.** FR-446's four layers (`docs/specs/07-platform.md:172`, amended
  2026-09-30) are the process variable (`GIP_SETTING_<KEY>`), the Environment setting, the
  workspace setting and the platform default. For these two routes the workspace layer is
  removed and the other three keep their order.
- **With nothing set, nothing is limited.** The default is unset (RL-1687 (2a)), so a bearer or
  development caller with no process variable set is admitted without a counter call.
- **The 10:31:43 parenthesis "(Environment → default)" is read with the process variable in
  front of it**, as the 10:36:38 entry rules. It did not name that layer; it did not remove it.

## What it obliges

- **SL-1258** (`PL-1666` DP-S4-1's slice): make the management limb accept no workspace for these
  two routes (`enforce` and `resolve` at the lines above), keeping the process-variable and
  Environment layers, with one red test per route (a bearer caller), and state the resolve path
  in the slice's `LG-`.
- **Until this record is minted**, SL-1258 cites the maintainer's entries "2026-10-16 10:31:43
  BST" and "2026-10-16 10:36:38 BST" (`to-lead.md`).

## Acceptance — the violation that must become detectable

Derived from the two entries' own words, with no new decision: 10:31:43, *"Red per route;
the LG states the resolve path"*; 10:36:38, *"the per-route reds cover a bearer caller"*.

The violation: either identity-only route, `GET /api/v1/me/workspaces` or
`POST /api/v1/me/workspace`, is not counted by FR-452's management-API limit for a caller with
no workspace (the case option (B) was refused for: *"(B) leaves users silently uncounted"*),
or SL-1258's `LG-` does not state the resolve path.

- *Violation: with `platform.default_management_rate_limit_rps` set and a bearer caller over
  it, `GET /api/v1/me/workspaces` is admitted instead of refused by the management limit.*
  One test, red on that input.
- *Violation: the same for `POST /api/v1/me/workspace`.* A second test, red on that input.
- *Violation: SL-1258's `LG-` does not state the resolve path for these two routes — process
  variable → Environment → default for a caller with a key verified for an Environment, and
  process variable → default for a bearer or development caller.* No script checks this; it is
  checked by reading the ledger at SL-1258's audit and at the lead's ACK.

The two tests are SL-1258's to write and to show red (`CLAUDE.md` §13); this record names
them and runs nothing. The entries rule no separate test for item 2's skipped workspace layer
(a workspace-level value not applied to these routes); that is evidenced by the `LG-`'s stated
resolve path, and this record adds no test the entries did not rule.
