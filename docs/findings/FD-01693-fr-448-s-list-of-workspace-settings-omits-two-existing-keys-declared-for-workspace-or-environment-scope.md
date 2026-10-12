---
id: FD-1693
family: finding
title: FR-448's list of workspace settings omits two existing keys declared for workspace or Environment scope
status: active
created: 2026-10-12
owner: auditor
tree: 50bbdd96b2154cb4eb79ccf91658191e51ab8906
corrected_by: []
relates: [WK-674, FR-448, FR-446, FR-452, FR-259, RL-1347, RL-1687, SL-1258]
---

# FD-1693 — FR-448's list omits two settings of its own kind

*(Minted 2026-10-12 as FD-1693 from working id 9613, in the D14 batch mint PR. The working id was reserved by the lead in `eta.md`, line stamped "2026-10-12 07:46:27 BST". It remains only in the quoted entries below.)*

Filed from the maintainer's (by delegation) entry "2026-10-12 07:44:13 BST — Three dropped decision-maker hand-offs: (1) RL 9852 = (A), with 3 conditions; (2) RL 9800's Q1 (i) and Q2 (A) RULED as the decision-maker proposed; (3) RL 9876 ACKED" (`~/gi-pricing-plan.local/channel/to-lead.md`, a local file cited by entry header), item (3), verbatim:

> *"FR-448's list omitting two existing settings of this kind: a LOW FD (doc drift) in D14, owner WK-674, cited in T2. Not fixed by widening T2."*

and from `RL-1687`'s T2 note and its "Raised to the lead" bullet on FR-448. Every `file:line` below was read at `origin/main` `50bbdd96b2154cb4eb79ccf91658191e51ab8906` on 2026-10-12.

## Evidence

- `docs/specs/07-platform.md:174`, FR-448's cell: the list of workspace settings names currency, locale and timezone, default validation thresholds, "trace sampling rate", an approval-policy reference, retention windows, the two model-complexity thresholds, and feature flags, then `rating.batch_abort_failure_rate` by a dated line. It names no key for `scoring.default_client_rate_limit_rps`.
- `backend/src/app/platform/settings.py:232-242`: `scoring.default_client_rate_limit_rps` (FR-452's default scoring limit, unset by default), declared with `scope=SettingScope.WORKSPACE_OR_ENVIRONMENT` at `:241`.
- `backend/src/app/platform/settings.py:216-231`: `rating.trace_sample_rate` (FR-259's persisted-trace sampling rate), declared with `scope=SettingScope.WORKSPACE_OR_ENVIRONMENT` at `:230`. FR-448's phrase "trace sampling rate" does not say which of two keys it means: this one, or `observability.trace_sample_rate` (`:209-215`, R4's distributed-tracing rate), which `rating.trace_sample_rate`'s own description says it is not.
- These are the only two `scope=SettingScope.WORKSPACE_OR_ENVIRONMENT` declarations in the file (`grep -n 'scope=SettingScope.WORKSPACE_OR_ENVIRONMENT' backend/src/app/platform/settings.py` prints `:230` and `:241`).
- `RL-1687` (minted from working id 9876) states the gap and does not widen its T2 to close it: "FR-448's list is not the registry: two `workspace_or_environment` keys already in `settings.py` are not in it".

## Finding

**Severity LOW (the maintainer (by delegation), entry "2026-10-12 07:44:13 BST", item (3)): doc drift, no behaviour is wrong.** FR-448's list is not the registry (`settings.py` is). A reader who treats the list as the set of keys declared for workspace or Environment scope misses two of them. The gap pre-dates `RL-1687`, which adds a third key of the same kind (`platform.default_management_rate_limit_rps`) to the list by its T2 and names the other two as this finding.

## Disposition

**Owner WK-674**, the Work whose Slice 4 (`SL-1258`) applies `RL-1687`'s T2 to FR-448. Remedy: a dated clause on FR-448 naming `scoring.default_client_rate_limit_rps` and `rating.trace_sample_rate`, with `rating.trace_sample_rate` distinguished from `observability.trace_sample_rate`, applied through `.claude/skills/spec-change`. It is not part of `RL-1687`'s T2, by the maintainer's instruction. Event that next confirms or discharges it: FR-448's cell naming both keys, checked by `grep -c 'scoring.default_client_rate_limit_rps' docs/specs/07-platform.md` printing at least 1 inside FR-448's cell. Filed by the minter from the entries, 2026-10-12.
