---
id: FD-9029
family: finding
title: zen-engine (the rating evaluator) has a pending major upgrade (0.53.0 to 2.0.2, Dependabot #882) that needs a governed upgrade, spike first
status: active
created: 2026-09-29
owner: auditor
tree: 46414450bca18999d43addf0ae5530ebf9d14cc1
corrected_by: []
relates: [WK-1178, ADR-706]
---

# FD-9029 — zen-engine (the rating evaluator) has a pending major upgrade (0.53.0 to 2.0.2, Dependabot #882) that needs a governed upgrade, spike first

## Finding

**Severity: medium.** `zen-engine` is the engine that executes every Rating Version (`ADR-706`). The repository pins it exactly at `0.53.0`, and everything it verified about the engine was verified against that version. Dependabot opened PR #882 to move the pin to `2.0.2`, which crosses the whole 1.x line (PyPI lists only `1.0.0b9` to `1.0.0b13`, then `2.0.0`). A blind merge would change the evaluator behind every quote without a spike, a ruling or an audit of the assumptions the code and specs make about it. The decision, given by the user through the maintainer and relayed by the lead, is **not to merge #882, to ignore major bumps in `.github/dependabot.yml` (this branch), and to upgrade under WK-1178 with a spike first.** This record fixes the facts the spike starts from. It does **not** say the upgrade is unsafe or safe: whether any API we call changed is **unverified**.

Filed under a **working id** (`FD-9029`); the lead mints it at its merge turn.

## Evidence

All facts below were read on 2026-09-29 from the tree at `46414450bca18999d43addf0ae5530ebf9d14cc1` (branch `wk1178-zen-engine-ignore`, one commit on `origin/main` `6ae8a99a3786b364700af801cf61fecd6a6f60c2`) and from the sources named.

**The pin.** `packages/pricing-core/pyproject.toml:58` reads `"zen-engine==0.53.0"` (exact); `uv.lock` resolves `zen-engine` `version = "0.53.0"` (at `:2705-2707`), with an sdist and `cp312`, `cp313`, `cp313t`, `cp314` and `cp314t` wheels per platform. It is a `pricing-core` runtime dependency, so `pricing-core` importing it is by design; `backend/pyproject.toml` does not name it.

**#882** (`gh pr view 882`): "chore(deps): bump zen-engine from 0.53.0 to 2.0.2", author `app/dependabot`, state OPEN, created 2026-09-28T20:52:02Z, branch `dependabot/uv/zen-engine-2.0.2`, head `f9dbeb7ed59c163b511639f5351180ee842711e3`, 2 files (`packages/pricing-core/pyproject.toml`, `uv.lock`), +11/−23. `gh pr diff 882` changes `"zen-engine==0.53.0"` to `"zen-engine==2.0.2"` in the `pyproject.toml`, the lock's specifier, and the lock package entry: the 2.0.2 entry has an sdist and five `cp38-abi3` wheels (`macosx_10_12_x86_64`, `macosx_11_0_arm64`, `manylinux_2_28_aarch64`, `manylinux_2_28_x86_64`, `win_amd64`), where 0.53.0 had per-interpreter wheels. It touches no source, test or spec.

**Where it is used.** `git grep` for `zen` under `packages/pricing-core/src` and `backend/src` finds `import zen` in exactly two modules and these calls (comments and docstrings excluded):
- `packages/pricing-core/src/pricing_core/rating/compile.py:24` imports it; `:245` calls `zen.compile_expression(step.expr)` to validate a step's expression against the engine's vocabulary (FR-276).
- `packages/pricing-core/src/pricing_core/rating/runtime.py:45` imports it; `:583` builds `zen.ZenEngine({"customHandler": handler})` and `:584` calls `engine.create_decision(json.dumps(wire))`.
- `packages/pricing-core/src/pricing_core/rating/score.py:793` calls `await bundle.decision.async_evaluate(context, {"trace": trace})` and `:943` calls `bundle.decision.evaluate(context)`.
Nothing outside `pricing_core/rating/` imports it. Test files under `packages/pricing-core/tests` that mention `zen` include (the first eight of a `git grep -c` listing I cut off there; the list may be longer) `test_gbm.py`, `test_objectives.py`, `test_progress.py`, `test_rate_table_operations.py`, `test_rating_compile_bundle.py`, `test_rating_runtime.py`, `test_rating_score.py` and `test_testing.py`. I did not read them for what each depends on.

**What the code and the specs say was verified against 0.53.0.** These are version-sensitive claims the code carries as comments or the docs carry as records:
- The wire shape: "a node **list** plus an explicit **edge list**, verified live against `zen.ZenEngine`" (`runtime.py:18`, `:344-348`, `compile.py:341-345`).
- No `if(cond, a, b)` function exists; a ternary is used (`runtime.py:280`); table keys translate as an exact key match only (`runtime.py:28`).
- The binding swallows whatever a `customHandler` raises into a generic error, which is why `score.py:15` and `runtime.py:86` recover the reason through a slot; `passThrough` merges a node's whole returned dict forward (`score.py:20`).
- Concurrency behaviour of `async_evaluate` on one shared decision (`score.py:26`; `docs/research/zen-evaluate-concurrency.md`, "zen-engine 0.53.0").
- The Phase 2 entry re-verification: "the S1 suite re-ran against the installed `zen-engine` 0.53.0 and all four boundary requirements hold — FR-273 … FR-274 … FR-275 … FR-276" (`docs/adrs/ADR-00706-…md`, addendum 2026-08-27), and the residual risks in its table: `rust_decimal` serialisation (FR-273), `maths-nopanic` returning `0` on invalid input (FR-274), decimal scale capped at 28 (FR-275).

**What upstream says, and what I did not verify.** PyPI (`https://pypi.org/pypi/zen-engine/json`, HTTP 200) and the GitHub releases API for `gorules/zen` (`https://api.github.com/repos/gorules/zen/releases`, pages 1 to 4, 231 entries) were reachable. `docs.gorules.io` and the source tree were not read.
- PyPI releases after 0.53.0 (2026-03-15): `1.0.0b9` to `1.0.0b13` (2026-07-22 to 2026-08-07), `2.0.0` (2026-08-20), `2.0.1` (08-22), `2.0.2` (08-24), and **`2.1.0` (2026-09-29, the day of this record)**. So #882's target is not the latest release, and the jump from 0.53.0 skips the 0.54.x and 0.55.x lines and the whole 1.0.0 beta series (`zen-engine-v1.0.0-beta.0`, 2026-06-25, compares against `zen-engine-v0.55.1`). I did not read the 0.54.x and 0.55.x notes.
- Release notes name **no formal "BREAKING CHANGES" section** in any of the 69 engine, expression, types and Python entries I filtered from 0.53 onward. That is not evidence of compatibility: the 1.0.0 beta.0 note is a long list of features and fixes. Items whose subject overlaps what this repository relies on (listed as **candidates for the spike only**, not as findings about behaviour): "implement serializable errors; improve binding error transparency" (the swallowed-handler-error assumption above); "improve trace", "compact trace", "add order to trace", "function trace format" (the `trace` option at `score.py:793`); "python asyncio" and "binding variable conversion (python and nodejs)"; "number serialization", "normalize number during serialization", "number serde" and "configurable arbitrary precision" (FR-273 and the `rust_decimal` risk); "zen expression rewrite", "expression function system" and "add regular expression functions" (FR-276's vocabulary check); "passthrough nodes" and "node merge strategy" (the `passThrough` assumption). In the 2.0 line: "number out of range panics" and "panic hardening" (FR-274's `maths-nopanic` assumption), "nested scopes and any cascade", "end of week boundary" (2.0.0), and in 2.1.0 "keep decimal fractions when serializing numbers without arbitrary precision" and "return errors instead of panicking in memory loader and v1 functions".
- **Whether any API this repository calls changed (`compile_expression`, `ZenEngine({"customHandler": …})`, `create_decision`, `async_evaluate`, `evaluate`, the node-and-edge wire shape, the handler contract) is unverified.** I did not install or run 2.0.2, and did not read the bindings' documentation or source.

**The decision.** The maintainer's entry "2026-09-29 16:08:24 BST · maintainer (acting on the maintainer's behalf) · HOST FALLBACK accepted; DEPENDABOT plan approved (the maintainer)" (`~/gi-pricing-plan.local/channel/to-lead.md`, line 11471) records for #882: "**not merged**"; a WK-1178 PR adds "an ignore rule for zen-engine's major version 2" to `.github/dependabot.yml`; and it "files an FD (working id, minted at its turn) for a governed upgrade under WK-1178: a spike first, since it is the rating evaluator"; closing #882 is the user's action. The lead relayed it as the user's decision through the maintainer.

**The ignore rule as written.** The branch adds `update-types: ["version-update:semver-major"]` for `zen-engine` (`.github/dependabot.yml`, three added lines), so it ignores every major bump, not only 2.x. Minor and patch updates are still proposed. Because the pin is exact, what Dependabot proposes next from `0.53.0` (for example a 0.54 or 0.55 minor) is **unverified**; how Dependabot classifies a `0.x` minor step is not something I checked.

## Disposition

**Proposed by the auditor; the decision is the lead's.**

**deferred with an owner — WK-1178.** Event that confirms or discharges it: a spike (the `library-spike` skill's method) runs the candidate version, and one exact version, against the tests that name `zen` and the FR-273 to FR-276 boundary suite the `ADR-706` addendum used, and against the assumptions listed above; a ruling or an `ADR-706` addendum records the result; then the pin moves as a governed change with `docs/skills-map.md` and `03` §8 updated together. Until then #882 stays unmerged and closed by its owner, and the `ignore` rule stays. The spike names its target version (2.1.0 was released today).

Ownership shape: event.
