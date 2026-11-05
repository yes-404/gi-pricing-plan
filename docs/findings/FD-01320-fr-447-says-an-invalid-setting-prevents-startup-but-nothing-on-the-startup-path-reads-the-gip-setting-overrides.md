---
id: FD-1320
family: finding
title: FR-447 says an invalid setting prevents startup, but nothing on the startup path reads the GIP_SETTING_ overrides
status: closed
created: 2026-09-30
owner: auditor
tree: 48792023e09cd79c771c2184d6808e378732b76b
corrected_by: []
relates: [WK-674, SL-1257, LG-1634]
---

# FD-1320 — FR-447 says an invalid setting prevents startup, but nothing on the startup path reads the GIP_SETTING_ overrides

## Finding

**Severity: medium.** FR-447 (`docs/specs/07-platform.md:173`): *"Settings are typed and validated
at startup; an invalid setting prevents startup with a clear message rather than failing at first
use."* No code on the startup path reads the `GIP_SETTING_<KEY>` environment overrides. So an
**unknown** override key is never reported at all, and an **out-of-range or ill-typed** value
fails only at the first resolve of that setting, which is the "failing at first use" FR-447
rules out.

## Evidence

Measured at `origin/main` `48792023e09cd79c771c2184d6808e378732b76b`.

- `load_settings` (`backend/src/app/config.py:270-291`) validates only `Settings`' declared
  fields, then calls `require_startable()`. It never looks at an override.
- `setting_overrides` (`config.py:241-249`) is an `@property` that reads `os.environ` on every
  call. Nothing computes it once at startup.
- The `create_app` lifespan (`backend/src/app/main.py:76-97`) runs only the FR-273 round-trip
  self-check and the FR-436 tenant-binding check (`require_tenant_binding`), registers the two
  probes, and yields.
- `git grep -n 'GIP_SETTING\|setting_overrides' -- backend/src` gives **5 hits**:
  `config.py:242`, `config.py:243`, `config.py:249`, `platform/settings.py:279`,
  `platform/settings.py:332`. `settings.py:279` builds the name (`_env_name`) and `:332` reads it
  inside `_env_candidate`, reached from `resolve` and `resolve_all` (`:292`, `:313`), which run
  per request. None is on a startup path.

**Reproduction** (the repository `.venv`, `PYTHONPATH` at this tree's `backend/src`, confirmed by
`app.__file__`; script is two `GIP_SETTING_*` variables, then `load_settings()`, then
`_env_candidate` on `workspace.currency`):

```
GIP_SETTING_TOTALLY_BOGUS_KEY=x   GIP_SETTING_WORKSPACE_CURRENCY=NOT_A_CURRENCY_
load_settings() succeeded; setting_overrides keys: ['GIP_SETTING_TOTALLY_BOGUS_KEY', 'GIP_SETTING_WORKSPACE_CURRENCY']
REGISTRY has TOTALLY_BOGUS_KEY: False / any bogus: False
first resolve of workspace.currency raised: PlatformError workspace.currency: 'NOT_A_CURRENCY_' is not one of ['GBP', 'EUR', 'USD', 'CHF', 'SEK', 'NOK', 'DKK', 'PLN'].
```

`load_settings()` succeeds with both overrides present; the currency then fails at first
resolve; the bogus key is reported nowhere.

**The lifespan, measured by auditor-plans2 (not re-run by this record's author).** The
`create_app` lifespan was **not run** in the reproduction above, because it needs a database.
auditor-plans2 ran it at `48792023`: a per-worktree database (dev-commands `createdb -T
gipricing`, then `alembic upgrade head`), Postgres and MinIO up, and
`create_app(load_settings()).router.lifespan_context(...)` entered with
`GIP_SETTING_TOTALLY_BOGUS_KEY=x` and `GIP_SETTING_WORKSPACE_CURRENCY=NOT_A_CURRENCY_` set.
Result: **"LIFESPAN STARTED (startup succeeded)"**. Control: with `GIP_TENANT_ID=other-tenant` the
same harness raised `TenantMismatchError … (FR-436)`, so it can fail on a startup check that
exists. The **mechanism** is the code reading above (the lifespan body and the five-hit grep):
nothing in it reads the overrides. The `load_settings` and first-resolve results are this
record's own measurement.

## Disposition

**Deferred with an owner: WK-674 Slice 3.** Event that discharges it: Slice 3's merge.
Raised by the high-effort decision-maker in #939 (working id 9903) and confirmed by auditor-rl.
The maintainer's decision (`~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 10:33:34
BST — DECISION: FR-447 startup validation is an FD, MEDIUM, owner WK-674 Slice 3; #964 and #939
noted"): the finding is **medium**.

Slice 3's **red-first acceptance** (each written to fail on `origin/main` first):

- an **unknown** override key refuses startup, naming the key;
- an **ill-typed or out-of-range** override value refuses startup with a clear message;
- an **Environment-only key** present as a process override refuses startup (#939's rule 3a);
- the acceptance runs the **real `create_app` lifespan with the database**, not `load_settings()`
  alone, because that is the path FR-447 names, and the one whose failure to refuse is measured
  above.

#939's rule 3a startup refusal must be a **new** check: none exists to extend, and
`require_startable` and the lifespan's two checks do not touch overrides.

*Disclosure: this record was drafted under working id 9881 and minted as FD-1320; the working id survives only in this line and in PR #965's history.*

***Resolved 2026-11-05*** — closed in place 2026-11-05 by the auditor (aud-fdclose), on the lead's brief under to-lead "2026-11-05 09:40:57 GMT" item 8 (2), the FD-1842 form. Delivered remedy (the four red-first acceptance cases, through the real `create_app` lifespan with the database, via a new check): WK-674 Slice 3, SL-1257 (LG-1634), PR #1280, squash commit fe80aec625b616adb467d4bca322674882e60f5c, merged 2026-10-11T17:43:37Z. `backend/src/app/platform/settings.py` gains `validate_setting_overrides`, called from the `main.py` lifespan; `backend/tests/test_settings_environment.py` asserts an unknown key (unit :98, lifespan :160), an ill-typed value (unit :107, lifespan :160) and an out-of-range value (unit :116 only) each refuse startup naming the key, and an Environment-only key as a process override refuses startup (unit :125, lifespan :169), using `api_settings`, which is database-backed (`backend/tests/conftest.py:41`). The out-of-range case has no lifespan test of its own; it goes through the same function.
