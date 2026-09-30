---
id: RL-9903
family: ruling
title: OQ-1235 decided — an Environment-setting layer joins FR-446's precedence below the process override, for keys declared per-environment
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 7c354305247236be1a3a50150c9c17b0134c4c5e
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1235, OQ-1234, RL-1232, RL-1236, PL-1237, CR-1247]
---

# RL-9903 — OQ-1235 decided: an Environment-setting layer joins FR-446's precedence below the process override, for keys declared per-environment

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). The session's
own `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`.

The record was prepared at effort `medium` (PR #939, head `1b23ac5d`, "PREPARED, NOT
RULED"), under the maintainer's decision of 2026-09-30 00:42:01 BST. This pass re-verified
its evidence at the tree below, decided the four items it left open, and found one it did
not name: RL-1232 DP-2's flags must not be enabled at workspace level (item 3). It keeps the
working id 9903; the id is minted at the lead's merge turn.

## Verified first, at 7c354305247236be1a3a50150c9c17b0134c4c5e

`git diff --stat 0bc69b5b 7c354305 -- backend/src/app/platform/settings.py
packages/model-schema/src/model_schema/settings.py docs/specs/07-platform.md
docs/plans/PL-01237*` prints nothing, so the prepared record's citations, refreshed at
`0bc69b5b`, hold. Each one used below was re-read at `7c354305`.

**The question** (`docs/open-questions.md:196`; mirror `docs/specs/07-platform.md:513`): how
is per-environment configuration resolved, when `07` FR-446's precedence has no Environment
level?

**The texts in conflict.**
- `07` FR-431 (`07-platform.md:142`): *"Environment configuration (rate limits, sampling
  rates, feature flags) is a Setting resolved by the precedence in §3.8 and is audited on
  change."*
- `07` FR-446 (`:172`): *"Settings resolve by precedence: **environment variable → workspace
  setting → platform default**. The effective value and its source are inspectable by an
  Admin."*
- `RL-1232` DP-2 (`docs/rulings/RL-01232-…md:184`): FR-270 and FR-271 *"stay **default off per
  environment**. Enabling one is an environment setting with its own audit event."*

**The code.**
- `SettingDefinition` (`backend/src/app/platform/settings.py:43-52`): `key`, `type`,
  `default`, `description`, `constraints`, `feature_flag`. It has no scope and no environment.
- `resolve` (`:292-310`) reads three layers, and `_resolution` (`:359-372`) picks the first
  one present: `SettingSource.ENV`, then `WORKSPACE`, then `DEFAULT`. `SettingSource`
  (`packages/model-schema/src/model_schema/settings.py:27-32`) is a `model-schema` enum, so a
  new member is a contract change regenerated into `docs/contracts/` (FR-451).
- **The `ENV` layer is process-wide.** It reads `GIP_SETTING_<KEY>` (`settings.py:278-279`,
  `:331-335`), so it cannot differ between Environment objects that one process serves. FR-430
  and `PL-1237` Slice 3 (*"a legitimately issued `dev` key is refused against `uat`"*,
  `PL-1237:838`) require one process to serve several environments. The word *environment*
  in FR-446 (an OS variable) and in FR-428/FR-431 (the Environment object) name different
  things.
- `set_workspace_setting` (`settings.py:388-416`) validates by `definition.coerce` before it
  writes, and leaves the audit event to its caller, which holds the actor and the
  before-value. Its docstring cites FR-447 for that write-time check. FR-447 (`07:173`) is
  **startup** validation ("typed and validated at startup"), so that docstring citation is
  loose. Correcting it is a Slice 3 fix, not this record's. *(This record cited FR-447 for
  write-time validation until auditor-rl's F2.)*

**What needs the answer** (`PL-1237` Slice 3, `:840-856`): FR-431's environment settings,
guarded by `admin:manage_settings` (`RL-1236` DP-D), each change audited with the
environment, key, old and new value; FR-430's monitoring-configuration limb; and NFR-496's
prod-sampling rate. Later, in Slice 6, RL-1232 DP-2's per-environment FR-270/FR-271
enablement.

### Presence and absence, as verified

*Added after the maintainer's standing rule of 2026-09-30: each presence or absence claim rests
on a reading of the module that owns the concept.* The owning module for settings is
`backend/src/app/platform/settings.py`, with the process configuration in
`backend/src/app/config.py` and the source enum in
`packages/model-schema/src/model_schema/settings.py`.

| Claim | Verdict | How it was verified at `7c354305` |
|---|---|---|
| A scope or environment on a setting definition | **absent** | `SettingDefinition` (`settings.py:43-52`), read: its fields are `key`, `type`, `default`, `description`, `constraints` and `feature_flag`. |
| An Environment layer in resolution | **absent** | `resolve` (`settings.py:292-310`) reads the process candidate and one `WorkspaceSettingRow`. `_resolution` (`:359-372`) chooses `ENV`, then `WORKSPACE`, then `DEFAULT`. `SettingSource` (`packages/model-schema/src/model_schema/settings.py:27-32`) has exactly those three members. |
| The `ENV` layer is process-wide | **present** | `_env_candidate` (`settings.py:331-335`) reads `settings.setting_overrides`. `Settings.setting_overrides` (`backend/src/app/config.py:242-249`) returns every `os.environ` key starting with `GIP_SETTING_`. It is the process's environment, the same for every request the process serves. |
| An audited write path for the process override | **absent** | `setting_overrides` is computed from `os.environ` (`config.py:249`). Nothing writes it. `git grep -n 'setting_overrides' 7c354305 -- backend/src` gives two hits: its definition (`config.py:242`) and its one read (`settings.py:332`). |
| Write-time validation and caller-side audit | **present** | `set_workspace_setting` (`settings.py:388-416`) calls `definition.coerce` before it writes. Its docstring says "The caller audits the change". |
| `SETTING_INVALID` | **present** | `backend/src/app/errors.py:61`, and `SettingDefinition.coerce`'s docstring (`settings.py:55`). |
| The resolve order | **present** | `resolve` (`settings.py:292-310`) and `resolve_all` (`:313-328`) both pass the process candidate first to `_resolution` (`:359-372`). That function returns the process value whenever it is not `None` (`:365-366`), before it looks at the workspace value. The process layer therefore wins for **every** key. |
| The process layer is read at resolve time, not at startup | **present** | `Settings.setting_overrides` (`backend/src/app/config.py:241-249`) is a `@property` that filters `os.environ` on every call. `_env_candidate` (`settings.py:331-335`) calls it, and coerces the value at that moment. A variable present in the process, or set after startup, is seen at the next resolve. |
| Startup validation of `GIP_SETTING_*` overrides | **absent** | The owning modules were read. `load_settings` (`config.py:270-291`) validates `Settings`' declared fields and calls `require_startable`. `create_app` (`backend/src/app/main.py:63`) runs the FR-273 and FR-436 startup checks in its lifespan (`:77-89`). Neither reads `setting_overrides`. `git grep -n 'GIP_SETTING\|setting_overrides' 7c354305 -- backend/src` gives five hits: `config.py:242` (the property), `:243` (its docstring), `:249` (its body), `settings.py:279` (`_env_name`) and `settings.py:332` (the one read). None is a startup path. So an unknown key, or an out-of-range override, surfaces at first resolve, not at startup. This is an observation against FR-447, offered to the lead as a candidate finding and not ruled here. |

## Options

As prepared, unchanged:

| | Option | For | Against |
|---|---|---|---|
| (a) | **Add an Environment layer to FR-446's precedence**: environment variable → **Environment setting** → workspace setting → platform default; `SettingDefinition` gains a scope saying which keys may vary per environment | Makes FR-446 agree with FR-431, which already calls this "a Setting"; one resolver, one audit path (`set_workspace_setting`'s pattern), one inspectable effective-value-and-source (FR-446's second sentence) for both levels; the scope stops a workspace-only key (e.g. `workspace.currency`) being set per environment; the operator's process override stays on top as an emergency lever | Amends FR-446; a `SettingSource` value is added (contract change, regenerated contract); the resolver needs the request's environment; a naming hazard — `SettingSource.ENV` already means *environment variable*, so the new layer must be named unambiguously |
| (b) | **Configuration on the Environment record**, outside the Settings resolver | Sits with FR-428's object; no resolver change | Contradicts FR-431 ("a Setting … §3.8"), so FR-431 is amended too; a second configuration mechanism whose typed validation (the registry's typed validation), inspectability (FR-446) and audit-on-change (FR-431) are rebuilt |
| (c) | **One workspace setting per key holding a map keyed by environment name** | No precedence change | No per-environment type or constraint (`SettingDefinition.coerce` checks one scalar); a deleted environment leaves a stale key; the source of an effective value is not inspectable per environment; the registry's typed validation at write cannot see an unknown environment name |
| (d) | **Environment variables only** — one deployment per Environment, configured through `GIP_SETTING_*` | No change at all | Excluded by the evidence: one process serves several environments (FR-430; `PL-1237:838`), so a process-wide variable cannot differ per environment; and a value set by a deploy is not "audited on change" (FR-431) |

*Two cells of the table above, options (b) and (c), were corrected on auditor-924d's finding, which
completed F2: they had cited FR-447 for write-time validation, and FR-447 is startup validation
(`07:173`). Nothing else in the table changed.*

## Ruled

**Option (a).** An **Environment setting** layer joins FR-446's precedence, for keys that
declare they may vary per environment.

1. **The precedence** (the prepared item (1)). **Process environment variable
   (`GIP_SETTING_<KEY>`) → Environment setting → workspace setting → platform default.** The
   new layer sits **below** the process override, so an operator can still pin one value for
   every environment a process serves during an incident, as they can over a workspace
   setting today. The one exception is an Environment-only key, which the process layer never
   supplies (item 3a). It sits **above** the workspace setting, so an environment can differ from
   its workspace.
   - The deciding evidence: FR-431 already defines environment configuration as *"a Setting
     resolved by the precedence in §3.8 and … audited on change"*.
   - The Settings resolver is the only mechanism at this tree with write-time type
     validation (`coerce`), inspectable source, and a caller-audited write path.
   - Its only environment-looking layer is process-wide.
   - So the level is added there. (b) and (c) would rebuild those three properties a second
     time. (d) is excluded by FR-430.
2. **Names** (the prepared item (2)). The new `SettingSource` member is
   **`ENVIRONMENT_SETTING = "environment_setting"`**, ordered between `ENV` and `WORKSPACE`.
   It is a member of **`model_schema`'s** `SettingSource`
   (`packages/model-schema/src/model_schema/settings.py:27-32`). The backend has a
   **different** enum with the same name, `backend/src/app/config.py:41-46`, whose member
   `ENVIRONMENT = "environment"` names a startup-configuration layer and is used by
   `backend/tests/test_config.py`. The two are distinct, and Slice 3 must not conflate them,
   neither by importing the wrong one nor by reusing `"environment"` for the new layer.
   *(Added on auditor-rl's F1.)*
   `ENV = "env"` keeps its published value and means *process environment variable*. Renaming
   it would break the contract for no behavioural gain. FR-446's text names the first layer
   "process environment variable" and the new one "Environment setting", with a capital E
   for the FR-428 object, so the two words cannot be read as one.
3. **Scope — which layers a key may be set at** (new at this pass). `SettingDefinition` gains
   a scope with three values:
   - **workspace only** — the default, so an undeclared key cannot vary per environment
     (for example `workspace.currency`);
   - **workspace or Environment** — the workspace value applies to every environment, and an
     Environment setting overrides it (FR-431's rate limits and sampling rates, NFR-496's
     prod-sampling rate, FR-430's monitoring configuration);
   - **Environment only** — it can never be set at workspace level.

   **RL-1232 DP-2's FR-270 and FR-271 flags are Environment only.** DP-2 says enabling one
   *"is an environment setting with its own audit event"*. A workspace-level write would
   enable it in every environment at once, `prod` included, with no per-environment event.
   Slice 3 declares the scope of each key it makes per-environment. Slice 6 declares the two
   flags. A write at a level the key's scope does not permit is refused with
   `SETTING_INVALID`.

   **3a. The process layer never supplies an Environment-only key** (added after the
   maintainer's must-check on `c5746ab5`/`49490802`: the scope rule above refused a
   workspace write but not the process layer). Under the precedence in item 1, the process
   layer ranks above the Environment setting, and it is one value for every Environment the
   process serves (the table above), `prod` included. So `GIP_SETTING_<FR-270 flag>=true`
   would turn the flag on in `prod`. That is the same all-environments act that item 3
   forbids at workspace level, and it has no audit event at all. That would break DP-2
   (*"an environment setting with its own audit event"*) and FR-449 (off in every environment
   until one is turned on).

   **Ruled: option (i), in its stronger form.**
   - **At startup, refused.** A `GIP_SETTING_<KEY>` present for an Environment-only key stops
     the process from starting, with a message naming the key and this rule. **This is a new
     startup check.** Nothing reads `GIP_SETTING_*` at startup today (the table above), so
     Slice 3 adds it, in `load_settings` (`config.py:270-291`) or in `create_app`'s lifespan
     (`main.py:77-89`). FR-447 is the
     form: "an invalid setting prevents startup with a clear message rather than failing at
     first use". Refusing is chosen over ignoring, because an ignored override lets an operator
     believe a value is in force that is not.
   - **At resolve, skipped.** The resolver never reads the process layer for an
     Environment-only key, and logs a warning naming the key if one is present. The property
     reads `os.environ` on every call, so a variable set after startup would otherwise be
     seen.
   - **Option (ii) is rejected.** A process-wide value for an Environment-only key cannot be
     reconciled with "Environment-only". There is also no per-environment audit event for it
     to carry, so DP-2's condition cannot be met.
   - **The incident override for such a key** is an Environment setting written for the
     affected Environment, for example turning FR-270's flag off in `prod`. It is guarded by
     `admin:manage_settings` and audited (item 5). It takes effect at the next resolve,
     because the resolver reads the stored value per request. For every other scope, the
     process override stays the operator's lever.
   - **Not ruled here:** startup validation of the other `GIP_SETTING_*` overrides (unknown
     keys, out-of-range values). It is absent (the table above). That is a candidate finding
     against FR-447, for the lead to route.
4. **FR-449, per environment** (the prepared item (4)). No new reading is needed. A flag's
   platform default is its safe value, and it is the default in every environment, because the
   default layer is below the Environment layer. So DP-2's flags are off in every environment
   until an Environment setting turns one on. FR-449 is not amended.
5. **Resolution, writes and audit.**
   - **Resolution.** The resolver takes the request's Environment when there is one. With
     none (a workspace-level context), the Environment layer is skipped.
   - **Inspection.** FR-446's effective-value-and-source inspection takes an optional
     Environment and reports every candidate, the Environment setting included.
   - **Writes.** An Environment setting is written through a path that mirrors
     `set_workspace_setting`. It validates with `coerce` before it writes (the registry's typed
     validation, as for a workspace setting; not FR-447, which is startup), refuses a
     key whose scope does not permit the Environment level, and is guarded by
     `admin:manage_settings` (`RL-1236` DP-D).
   - **Audit.** The caller's Audit Event names the environment, the key, and the old and new
     values (`PL-1237` Slice 3, FR-431).
   - **Rows.** An Environment setting row is keyed by the Environment's identity, not its
     name. An archived Environment (`00` ID-5) keeps its rows as history, and no request can
     resolve them, since no request is tagged with an archived Environment.
6. **What stays out.** The process override is not audited on change, today or after this
   ruling. It is the operator's deployment configuration, outside FR-431's "audited on
   change", which binds the Environment setting. That is acceptable only because the
   process layer never reaches an Environment-only key (item 3a). This ruling does not
   change the absence of an audit event.

**This ruling and OQ-1234's are independent.** OQ-1234's ruling (PR #935, not yet minted
when this record was written, so it is cited by PR) put FR-429's skip permission on the
approval policy and **excluded** an Environment setting as its home. The exclusion
rested on a Setting being untyped, which this ruling does not change: a Setting's value is
still checked only by `coerce`, not by a contract shape. The order in which the two land does
not matter.

**The disposition — amend now, build in Slice 3** (the prepared item (3)). FR-446 is amended
in this commit, dated, because a decided question must land in its requirement. A
requirement ahead of its code is the normal state of a spec. The code, the `SettingSource`
member and the regenerated contract land in WK-674 Slice 3. No `FR-` is appended: FR-431 is
the obligation, and FR-446 is the rule it names.

## What it obliges

- **This commit:** `07` FR-446 carries a dated clause giving the four-layer precedence and the
  scope rule. `OQ-1235` is closed in both mirrors (`docs/open-questions.md` and `07` §10),
  citing this record.
- **The roadmap (the lead's file, not edited here):** the §10 row *Before WK-674 Slice 3*
  strikes `OQ-1235` and recounts to `1 (0 open)`. A decided question keeps its row.
- **WK-674 Slice 3 (`PL-1237` Task 3):** items 1, 2, 3, 3a and 5 above. That means
  `SettingSource.ENVIRONMENT_SETTING` and the regenerated contract, `SettingDefinition`'s
  scope with each Slice 3 key declared, the resolver's Environment argument and inspection,
  the audited write path, and item 3a's startup refusal and resolve-time skip. Slice 3
  builds item 3a with the scope, before any Environment-only key exists, so that Slice 6's
  flags are covered the moment they are declared.
- **The lead:** the startup-validation observation (the table above, and item 3a's "not
  ruled here") is offered as a candidate finding.
- **WK-674 Slice 6:** FR-270's and FR-271's flags declared Environment only (item 3).

## Acceptance — the violation that must become detectable

The violation: **a value set for one Environment changes another's, or a per-environment
change goes unaudited, or a DP-2 flag is enabled everywhere at once.** Each is shown failing on
deliberately broken input (`CLAUDE.md` §13):
- *Slice 3:* a key set for `uat` changes the effective value in `uat` only. The resolution
  reports `environment_setting` as its source, and `prod` still reports `workspace` or
  `default`.
- *Slice 3:* for a workspace-or-Environment key, a process override (`GIP_SETTING_<KEY>`) wins
  over an Environment setting in every environment the process serves.
- *Slice 3, red first:* for an Environment-only key (a test-registered one, until Slice 6
  declares the real flags):
  - a `GIP_SETTING_<KEY>` present at startup stops the process with a message naming the key;
  - a variable set after startup is skipped at resolve, so the effective value's source stays
    `environment_setting` or `default`, and a warning is logged.

  With the refusal and the skip removed, the flag resolves on in every environment, and the
  tests fail.
- *Slice 3:* a workspace-only key written for an Environment is refused with
  `SETTING_INVALID`.
- *Slice 3:* an Environment-setting write whose transaction commits with no Audit Event
  naming the environment, key, and old and new values is shown red.
- *Slice 6:* a workspace-level write of FR-270's or FR-271's flag is refused, and an
  Environment-level write enables it in that Environment only.
