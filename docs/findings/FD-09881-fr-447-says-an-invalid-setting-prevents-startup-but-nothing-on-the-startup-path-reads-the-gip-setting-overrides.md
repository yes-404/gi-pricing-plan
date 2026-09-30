---
id: FD-9881
family: finding
title: FR-447 says an invalid setting prevents startup, but nothing on the startup path reads the GIP_SETTING_ overrides
status: active
created: 2026-09-30
owner: auditor
tree: 48792023e09cd79c771c2184d6808e378732b76b
corrected_by: []
relates: [WK-674]
---

# FD-9881 — FR-447 says an invalid setting prevents startup, but nothing on the startup path reads the GIP_SETTING_ overrides

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

**What this does not prove.** The `create_app` lifespan was **not run** in this reproduction,
because it needs a database. The claim that the lifespan does not read the overrides rests on
**code reading** (the lifespan body above, and the five-hit grep). The `load_settings` and
first-resolve results are measured.

## Disposition

**Deferred with an owner: WK-674 Slice 3.** Event that discharges it: Slice 3's merge.
Raised by the high-effort decision-maker in #939 (working id 9903) and confirmed by auditor-rl.
The maintainer's decision: the finding is **medium**.

Slice 3's **red-first acceptance** (each written to fail on `origin/main` first):

- an **unknown** override key refuses startup, naming the key;
- an **ill-typed or out-of-range** override value refuses startup with a clear message;
- an **Environment-only key** present as a process override refuses startup (#939's rule 3a);
- the acceptance runs the **real `create_app` lifespan with the database**, not `load_settings()`
  alone, because that is the path FR-447 names and the one this record could not run.

#939's rule 3a startup refusal must be a **new** check: none exists to extend, and
`require_startable` and the lifespan's two checks do not touch overrides.

*Drafted under working id 9881.*
