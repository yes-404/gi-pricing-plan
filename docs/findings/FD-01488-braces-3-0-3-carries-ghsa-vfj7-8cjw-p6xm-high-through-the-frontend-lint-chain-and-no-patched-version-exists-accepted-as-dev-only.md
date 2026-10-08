---
id: FD-1488
family: finding
title: braces 3.0.3 carries GHSA-vfj7-8cjw-p6xm (HIGH) through the frontend lint chain and no patched version exists; accepted as dev-only
status: active
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: 83ea509023d6d705d6f78fe74b7124fdf1375739
corrected_by: []
relates: [WK-1178]
---

# FD-1488 — `braces` 3.0.3 (GHSA-vfj7-8cjw-p6xm), dev-only, accepted until a patched version publishes

*Disclosure: drafted under working id 9644; minted as FD-1488 on 2026-10-08, in the T2 batch mint PR.*

Ordered by the maintainer's (by delegation) entry headed
"2026-10-05 13:36:07 BST — braces: no patched release exists; OPTION (C), accepted dev-only risk; Dependabot itself is the watch"
(`to-lead.md`, a local channel file, so cited by its header).

## Finding

**Severity: LOW** (the maintainer's (by delegation) option (C)); **owner WK-1178**; **decision: accepted until a
patched `braces` publishes.** `braces` 3.0.3 has GHSA-vfj7-8cjw-p6xm (advisory severity HIGH,
a stack-exhaustion denial of service through deeply nested patterns). The advisory's
affected range is `introduced 0 … last_affected 3.0.3` with no fixed event (OSV, per the maintainer's (by delegation) entry).

## Why LOW

- **Dev-only.** pnpm marks it `"dev": true`. The path is
  `@vue/eslint-config-typescript` > `fast-glob` > `micromatch` > `braces`.
- **No untrusted input.** The patterns it expands are our own lint globs, from repository
  config. The attack needs an attacker-written glob in our lint config.

## Evidence

Measured 2026-10-05 with `curl -s https://registry.npmjs.org/braces`:

```
{'latest': '3.0.3'} 2024-09-18T05:27:12.449Z ['3.0.1', '3.0.2', '3.0.3']
```

(`dist-tags`, `time.modified`, the last three of `versions`.) The earlier proposal to
override to `>=3.0.4` names a version that does not exist and is withdrawn. pnpm 11 also
ignores `package.json` `pnpm.overrides`, so an override would not apply.

## Disposition

Owner **WK-1178**. **Severity: LOW** (the maintainer's (by delegation) option (C)). **Decision: accepted until a
patched `braces` publishes** (the maintainer (by delegation), 2026-10-05 13:36:07 BST); the lead gives the
verdict. Event that closes it: Dependabot's security PR for a fixed `braces` merges.

## Watch and closure

- **The watch is Dependabot.** Security updates are enabled; a security PR opens when a
  fixed `braces` publishes. Merging it closes this finding, which names that PR.
- **CI.** The WK-1178 CI audit (`pnpm audit` and `pip-audit`) allowlists
  `GHSA-vfj7-8cjw-p6xm` by id, with this finding's id as the reason. Any other advisory fails.
- **Expected read-back:** `pip-audit` 0; `pnpm audit` 1 high (`braces`, accepted under this finding).
