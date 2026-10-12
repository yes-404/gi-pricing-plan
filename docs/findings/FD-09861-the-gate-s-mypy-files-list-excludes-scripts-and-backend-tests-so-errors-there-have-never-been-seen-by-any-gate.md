---
id: FD-9861
family: finding
title: The gate's mypy files list excludes scripts/ and backend/tests, so errors there have never been seen by any gate
status: active
created: 2026-10-12
owner: auditor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
corrected_by: []
relates: [WK-1178, SL-1527]
---

# FD-9861 — two trees the type gate never reads

Raised as a D13 owed addition: the lead's eta entry "2026-10-12 00:16:48 BST" (a local file), *"the gate's mypy 'files' (pyproject.toml:130-139 …) does NOT cover scripts/ or backend/tests — scripts/demo.py:69-70 carries pre-existing mypy errors on main that no gate has ever seen (found by executor-sl1527, 00:16)"*. Re-measured at `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9` on 2026-10-12, after `uv sync --all-packages` in a fresh worktree (without it, missing-import errors inflate every count).

## Evidence

- `pyproject.toml` `[tool.mypy]` `files` (`:130-139`) is `packages/model-schema/src`, `packages/pricing-core/src`, `backend/src`, `tests`, `examples/fremtpl2` and three skills' `scripts`. It names neither the repository's `scripts/` nor `backend/tests`.
- Predicate and counts (the commands verbatim): `uv run mypy scripts/demo.py` prints `scripts/demo.py:64: error: Incompatible types in assignment (expression has type "_Environ[str] | dict[str, str]", variable has type "dict[str, str] | None")  [assignment]` and `:65: error: Item "None" of "dict[str, str] | None" has no attribute "get"  [union-attr]`, `Found 2 errors in 1 file`. (The entry says `:69-70`; at this tree they are `:64-65`.) `uv run mypy scripts` prints `Found 231 errors in 14 files (checked 27 source files)`. `uv run mypy backend/tests` prints `Found 1983 errors in 128 files (checked 154 source files)`.
- The two trees are therefore not almost-clean: turning them on in one step would red the gate with about 2 200 errors.

## Finding

**Severity LOW (proposed by the executor; the lead rules).** No product behaviour is wrong; the exposure is that `scripts/` includes the demo entrance and the generators, which run against real stacks, and a type error there is found by running, not by the gate. `CLAUDE.md` §3 states `mypy --strict`; the claim is false for these trees.

## Disposition

**Owner proposed: WK-1178** (the P2 fix tail, which owns gate and tooling corrections), or the next toucher of the `[tool.mypy]` block. Fix before close for `scripts/demo.py` (two errors, the demo entrance, add `scripts/demo.py` to `files` once clean) and a decision, by the owner, for the rest: either a per-tree error baseline that may only shrink, or an explicit statement in `.claude/skills/repo-architecture` that `scripts/` and `backend/tests` are outside the gate. Event that next confirms or discharges it: a merged change after which `uv run mypy` covers `scripts/demo.py` and the rest is baselined or declared out of scope. Filed by the executor, 2026-10-12.
