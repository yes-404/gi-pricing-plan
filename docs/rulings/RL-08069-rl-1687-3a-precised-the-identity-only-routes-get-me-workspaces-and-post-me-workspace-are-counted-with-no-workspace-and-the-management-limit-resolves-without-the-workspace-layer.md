---
id: RL-8069
family: ruling
title: RL-1687 (3a) precised — the identity-only routes GET /me/workspaces and POST /me/workspace are counted by the management-API limit with no workspace, and its Setting resolves without the workspace layer for them (DP-S4-ME → (A))
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

# RL 8069 — RL-1687 (3a) precised: the identity-only routes count with no workspace

*Disclosure: drafted under **working id RL 8069**, reserved by the lead in
`~/gi-pricing-plan.local/handover/eta.md` (line 1968 at the time of writing): "8069 RL (precises
RL-1687 (3a): identity-only routes counted with workspace_id=None, the maintainer 10:31:43;
decision-maker-8069, rl-8069-rl1687-3a-identity-2026-10-16)". The lead mints it; the mint sweep
replaces the working id. Written 2026-10-16 from 10:34:37 BST (`TZ=Europe/London date`) by the
decision-maker (seat decision-maker-8069, effort medium, inherited; no raise). **No test or code
was run**: every claim about behaviour below is a reading of the code at the named tree,
`origin/main` @`a2f77b2dcad5aaec41a5f10aa664383caf421e8b`.*

## How this was ruled

- **The decision is the maintainer's.** The decision-maker drafts it; the decision-maker rules
  nothing here. The entry is "2026-10-16 10:31:43 BST — Maintainer: DP-S4-ME → (A); CORRECTION of
  my 10:27:41 Q-a; LG 9810 direct-write table" in `~/gi-pricing-plan.local/channel/to-lead.md`.
  Its first paragraph, verbatim:

  > DP-S4-ME → (A). `/me/workspaces` and `POST /me/workspace` are identity-level, not
  > workspace-scoped, so they count with workspace_id=None and `resolve` skips the workspace layer
  > (Environment → default). (B) leaves users silently uncounted; (C) is arbitrary. PLACEMENT: a
  > new RL in the next D batch. It "precises RL-1687 (3a)" (RL-1687's body is frozen, so this is
  > not an addendum). The decision-maker drafts it from THIS entry verbatim; S4 cites this entry
  > until it is minted. Red per route; the LG states the resolve path.

  The rest of that entry (the re-ruled Q-a, items (1a), (1b), (4), (5), and LG 9810's table) is
  not part of this ruling and is not restated here.
- **The decision point it answers** is the lead's "DP-S4-ME", the entry "2026-10-16 10:31:10 BST —
  Lead: executor-1258g STOPPED on Q-c (as 10:27:41 requires); DP-S4-ME + the unstamped direct
  writes, for the maintainer" in `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`. Its
  options, verbatim:

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
  workspace_id: UUID, key, environment=None)`. `resolve` reads the process variable
  (`_env_candidate`), then the Environment row, then the `WorkspaceSettingRow` filtered by
  `workspace_id` (`:384-393`). Neither signature accepts `None` at this tree. So (A) is a code
  change in `rate_limit.py` and `settings.py`, which SL-1258 carries.
- **`counted_caller` is not on `main`.** The lead's 10:31:10 entry cites `me.py:42`
  (`counted_caller`) for `GET /me`. That is on SL-1258's branch (`@37df0a3c`, per the same entry),
  not at `a2f77b2d`. This record does not cite it as a fact at its tree.

## The clause precised

The maintainer names **RL-1687 (3a)**. In RL-1687
(`docs/rulings/RL-01687-pl-1666-dp-s4-1-decided-fr-452-s-management-api-limit-counts-every-authenticated-api-v1-request-outside-the-score-family-on-its-own-setting-and-rate-limit-rps-stays-the-scoring-limit.md`,
at `a2f77b2d`), (3a)'s ruled text is lines 188-190:

> **Ruled (3a): no. `rate_limit_rps` is the scoring limit only and never applies to the management
> counter.** A Service Account's management calls are limited by
> `platform.default_management_rate_limit_rps`, like every other Principal's.

**Disclosed, not resolved here: the workspace scope that this precision narrows is written in
RL-1687 (2a), not in (3a).** (3a) is about a Service Account's `rate_limit_rps` and says nothing
about workspaces. The words "workspace or Environment" and the resolution rule are in (2a),
lines 167-173:

> type `int`, `default=None`, `constraints={"min": 1}`, scope **workspace or Environment**
> (`SettingScope.WORKSPACE_OR_ENVIRONMENT`), …
>
> **It is resolved by §3.8** (FR-446, `RL-1311`) with the caller's Environment, as the scoring
> Setting is (`rate_limit.py:130-136`): the Environment the presented key was verified for, and
> none for a bearer or development caller, whose resolution then skips the Environment layer.

and in RL-1687's **Consequences, stated**, lines 210-213: *"each counted request still opens a
session and runs `settings.resolve` (`settings.py:369-395`: the Environment row when an
Environment is named, then the workspace row)"*. The lead's DP and the maintainer's entry both
say "(3a)". This record keeps the maintainer's locator as written and quotes both clauses, so a
reader can see which text the precision acts on. Whether the minted title should say "(2a)" is
the maintainer's to say (see **Raised**).

## Ruled (the maintainer, 2026-10-16 10:31:43 BST)

For the two identity-only routes, `GET /api/v1/me/workspaces` and `POST /api/v1/me/workspace`:

1. **They are counted** by FR-452's management-API limit, as RL-1687 (1a) already requires of
   every authenticated `/api/v1/*` request outside the `/score` family. The maintainer's words:
   *"they count with workspace_id=None"*. Option (B), counting only a principal with exactly one
   membership, is refused: *"(B) leaves users silently uncounted"*. Option (C), the first or any
   membership, is refused: *"(C) is arbitrary"*.
2. **The management-limit Setting's resolution skips the workspace layer for them.** The
   maintainer's words: *"`resolve` skips the workspace layer (Environment → default)"*. The
   Setting `platform.default_management_rate_limit_rps` keeps the levels RL-1687 (2a) declared;
   only the lookup for these two routes has no workspace to read.
3. **The test is red per route, and the slice's `LG-` states the resolve path**: *"Red per route;
   the LG states the resolve path."*

## What this means for RL-1687 (3a), and for (2a)'s workspace overrides

- **(3a) stands unchanged.** A Service Account's `rate_limit_rps` still never applies to the
  management counter. For these two routes, "limited by
  `platform.default_management_rate_limit_rps`, like every other Principal's" means that Setting
  resolved without a workspace.
- **A workspace-level value of `platform.default_management_rate_limit_rps` does not apply to
  these two routes.** This is the lead's DP (A) clause, *"workspace overrides do not apply to
  these two routes"*, which the maintainer adopted in substance and placed here. A workspace
  override still applies to every other counted route, through the Caller's verified workspace
  (FR-397).
- **The Redis key is unchanged.** RL-1687 (1a)'s key is per (Environment, Principal), with no
  workspace in it, so these routes share the Principal's one management counter with its other
  management requests.

## Consequences, stated (not options)

- **The layers left.** The maintainer's parenthesis names "Environment → default". FR-446's
  four layers (`docs/specs/07-platform.md:172`, amended 2026-09-30) are the process variable
  (`GIP_SETTING_<KEY>`), the Environment setting, the workspace setting and the platform default.
  Skipping the workspace layer leaves the other three in that order. The process variable is not
  named in the maintainer's parenthesis and is not excluded by it; `resolve` reads it on every
  call at this tree (`settings.py:384`). This record does not rule on it; see **Raised**.
- **The Environment layer is the caller's, as RL-1687 (2a) says.** With no presented key for the
  Environment (a bearer or development caller), that layer is skipped too, so the limit is the
  process variable or the default. The default is unset (RL-1687 (2a)), so with nothing set the
  request is admitted without a counter call.

## What it obliges

- **SL-1258** (`PL-1666` DP-S4-1's slice): make the management limb accept no workspace for these
  two routes (`enforce` and `resolve` at the lines above), with one red test per route, and state
  the resolve path in the slice's `LG-`.
- **Until this record is minted**, SL-1258 cites the maintainer's entry "2026-10-16 10:31:43 BST"
  (`to-lead.md`), as that entry says.

## Raised (for the lead and the maintainer)

1. **The locator.** The workspace scope is in RL-1687 (2a) (lines 167-173), not (3a) (lines
   188-190). This record keeps "(3a)" as the maintainer wrote it. Should the minted title say
   "(2a)", or "(2a) and (3a)"?
2. **The process-variable layer.** "Environment → default" does not name FR-446's first layer.
   Does it still apply to these two routes? At this tree it would apply unless the slice removes
   it.
