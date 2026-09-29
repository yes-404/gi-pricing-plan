---
id: RL-9903
family: ruling
title: PREPARED, NOT RULED — OQ-1235, how per-environment configuration resolves against FR-446
status: draft                  # NOT a permitted RL status (§1.2: active → superseded | retired); deliberate, see "Status of this record"
created: 2026-09-30
owner: decision-maker
tree: aa14e90dd77c7461aa35cc6461557b129959463f
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1235, RL-1232, RL-1236, PL-1237, CR-1247]
---

# RL-9903 — PREPARED, NOT RULED: OQ-1235, how per-environment configuration resolves against FR-446

## Status of this record — read this first

**Nothing here is ruled.** This is a *prepared* ruling, written at effort `medium` under the
maintainer's decision by delegation of 2026-09-30 00:42:01 BST (`to-lead.md`, entry headed
"#933 READ BACK; DECISION: the DM PREPARES the blocked rulings on medium now, and RULES only
on effort high"). `OQ-1235` stays **open**, no spec text is amended, the roadmap §10 gate
"Before WK-674 Slice 3" stays open, and **SL-1257 (WK-674 Slice 3) does not start on it**. The
ruling is the later pass at effort `high`.

**`status: draft` is not a status a ruling may carry** (`document-ids.md` §1.2, RL:
`active → superseded | retired`; `scripts/audit-docs.py` check 33). It is kept on purpose so
the gate refuses this file as a ruling; the ruling pass sets `active` and mints the id.
Working id 9903 was checked free on `origin/main` and every `origin/*` branch.

## Verified first, at aa14e90dd77c7461aa35cc6461557b129959463f

**The question** (`docs/open-questions.md:194`; mirror `docs/specs/07-platform.md:513`): how
is per-environment configuration resolved, when `07` FR-446's precedence has no Environment
level?

**The texts in conflict.**
- `07` FR-431 (`07-platform.md:142`): *"Environment configuration (rate limits, sampling
  rates, feature flags) is a Setting resolved by the precedence in §3.8 and is audited on
  change."*
- `07` FR-446 (`:172`): *"Settings resolve by precedence: **environment variable → workspace
  setting → platform default**. The effective value and its source are inspectable by an
  Admin."*
- `RL-1232` DP-2 (deputy's entry quoted at `RL-1232:184`): FR-270 and FR-271 stay *"default
  off per environment. Enabling one is an environment setting with its own audit event."*

**The code at this tree.**
- `SettingDefinition` (`backend/src/app/platform/settings.py:43-52`): `key`, `type`,
  `default`, `description`, `constraints`, `feature_flag` — no scope, no environment field.
- The resolver is three layers (`settings.py:292-310`, `:359-386`); its source enum is
  `SettingSource` = `ENV "env"`, `WORKSPACE "workspace"`, `DEFAULT "default"`
  (`packages/model-schema/src/model_schema/settings.py:27-32`) — a `model-schema` shape, so a
  new layer is a contract change generated to `docs/contracts/` (FR-451's drift check).
- **The "environment variable" layer is process-wide**: it reads
  `settings.setting_overrides[GIP_SETTING_<KEY>]` (`settings.py:278-279`, `:331-335`). It
  cannot vary per Environment object while one process serves several environments — and
  `07` FR-430 plus `PL-1237`'s Slice 3 gate outline (*"a legitimately issued `dev` key is
  refused against `uat`"*, `PL-1237:838`) require exactly that: one deployment, requests
  tagged with their environment. So the word *environment* in FR-446 (an OS variable) and in
  FR-428/FR-431 (the Environment object) name different things, and nothing today resolves
  the second.

**What needs the answer** (`PL-1237` Slice 3, `:840-856`): FR-431's environment settings
guarded by `admin:manage_settings` (`RL-1236` DP-D) with an Audit Event naming environment,
key, old and new value; FR-430's monitoring-configuration limb; NFR-496's prod-sampling rate;
and — later, Slice 6 — DP-2's per-environment FR-270/FR-271 enablement.

## Options

| | Option | For | Against |
|---|---|---|---|
| (a) | **Add an Environment layer to FR-446's precedence**: environment variable → **Environment setting** → workspace setting → platform default; `SettingDefinition` gains a scope saying which keys may vary per environment | Makes FR-446 agree with FR-431, which already calls this "a Setting"; one resolver, one audit path (`set_workspace_setting`'s pattern), one inspectable effective-value-and-source (FR-446's second sentence) for both levels; the scope stops a workspace-only key (e.g. `workspace.currency`) being set per environment; the operator's process override stays on top as an emergency lever | Amends FR-446; a `SettingSource` value is added (contract change, regenerated contract); the resolver needs the request's environment; a naming hazard — `SettingSource.ENV` already means *environment variable*, so the new layer must be named unambiguously |
| (b) | **Configuration on the Environment record**, outside the Settings resolver | Sits with FR-428's object; no resolver change | Contradicts FR-431 ("a Setting … §3.8"), so FR-431 is amended too; a second configuration mechanism whose type checking (FR-447), inspectability (FR-446) and audit-on-change (FR-431) are rebuilt |
| (c) | **One workspace setting per key holding a map keyed by environment name** | No precedence change | No per-environment type or constraint (`SettingDefinition.coerce` checks one scalar); a deleted environment leaves a stale key; the source of an effective value is not inspectable per environment; FR-447's reject-at-write cannot see an unknown environment name |
| (d) | **Environment variables only** — one deployment per Environment, configured through `GIP_SETTING_*` | No change at all | Excluded by the evidence: one process serves several environments (FR-430; `PL-1237:838`), so a process-wide variable cannot differ per environment; and a value set by a deploy is not "audited on change" (FR-431) |

## Provisional recommendation — (a), not ruled

**(a)**, agreeing with `OQ-1235`'s own recommendation: FR-446 becomes *environment variable →
Environment setting → workspace setting → platform default*, `SettingDefinition` gains a
per-key scope (workspace-only, or environment-variable), and the new source is named so it
cannot be read as "environment variable".

**The one piece of evidence that decides it:** FR-431 already defines environment
configuration as *a Setting resolved by §3.8's precedence and audited on change*; the Settings
resolver is the only mechanism at this tree that has typed write-time validation, audit on
change and an inspectable source (`settings.py:292-386`), and its only per-environment-looking
layer is process-wide (`settings.py:331-335`) — so the missing level has to be added there,
or those three properties are built a second time.

**Left for the ruling pass at effort `high`:** (1) the layer's position — below the process
override (recommended here, so an operator can still pin a value in an incident) or above it;
(2) the new `SettingSource` member's name and the FR-446 wording that disambiguates
*environment variable* from *Environment*; (3) whether FR-446's amendment is Slice 3's
spec-change or this ruling's disposition (`spec-change` requires the ruling in the same
commit); (4) whether FR-449's safe-default rule needs a per-environment reading for DP-2's
flags (default off in every environment).

## Ruled

**Nothing.** This heading is present because check 37 requires it of the ruling family. It
records no decision.

## What it obliges

**Nothing, and nobody.** No slice starts on this record; no spec, open-question, roadmap or
plan text is changed by it. `OQ-1235` stays open.

## Acceptance — the violation that must become detectable

*Provisional, for the ruling pass.* If (a) is ruled: a key set for `uat` changes the
effective value in `uat` only, and the resolution reports the Environment layer as its source;
a workspace-only key is refused when written per environment (`SETTING_INVALID`); and a change's
Audit Event names the environment, the key, and the old and new values.
