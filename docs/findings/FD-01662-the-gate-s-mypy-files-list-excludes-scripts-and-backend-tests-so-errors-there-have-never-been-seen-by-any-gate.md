---
id: FD-1662
family: finding
title: The gate's mypy files list excludes scripts/ and backend/tests, so errors there have never been seen by any gate
status: closed
created: 2026-10-12
owner: auditor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
corrected_by: []
relates: [WK-1178, SL-1527, LG-1647, SL-2048, LG-2049, PL-2047]
---

# FD-1662 — two trees the type gate never reads

*(Minted 2026-10-12 as FD-1662 from working id 9861, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Raised as a D13 owed addition: the lead's eta entry "2026-10-12 00:16:48 BST" (a local file), *"the gate's mypy 'files' (pyproject.toml:130-139 …) does NOT cover scripts/ or backend/tests — scripts/demo.py:69-70 carries pre-existing mypy errors on main that no gate has ever seen (found by executor-sl1527, 00:16)"*. Re-measured at `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9` on 2026-10-12, after `uv sync --all-packages` in a fresh worktree (without it, missing-import errors inflate every count).

## Evidence

- `pyproject.toml` `[tool.mypy]` `files` (`:130-139`) is `packages/model-schema/src`, `packages/pricing-core/src`, `backend/src`, `tests`, `examples/fremtpl2` and three skills' `scripts`. It names neither the repository's `scripts/` nor `backend/tests`.
- Predicate and counts (the commands verbatim): `uv run mypy scripts/demo.py` prints `scripts/demo.py:64: error: Incompatible types in assignment (expression has type "_Environ[str] | dict[str, str]", variable has type "dict[str, str] | None")  [assignment]` and `:65: error: Item "None" of "dict[str, str] | None" has no attribute "get"  [union-attr]`, `Found 2 errors in 1 file`. (The entry says `:69-70`; at this tree they are `:64-65`.) `uv run mypy scripts` prints `Found 231 errors in 14 files (checked 27 source files)`. `uv run mypy backend/tests` prints `Found 1983 errors in 128 files (checked 154 source files)`.
- The two trees are therefore not almost-clean: turning them on in one step would red the gate with about 2 200 errors.

## Finding

**Severity LOW (proposed by the executor; ruled LOW, owner WK-1178, by the lead, "2026-10-12 02:57:36 BST").** The fix is `scripts/demo.py` into `files` now, the rest by a per-tree baseline or a declared exclusion. No product behaviour is wrong; the exposure is that `scripts/` includes the demo entrance and the generators, which run against real stacks, and a type error there is found by running, not by the gate. `CLAUDE.md` §3 states `mypy --strict`; the claim is false for these trees.

## Disposition

**Owner proposed: WK-1178** (the P2 fix tail, which owns gate and tooling corrections), or the next toucher of the `[tool.mypy]` block. Fix before close for `scripts/demo.py` (two errors, the demo entrance, add `scripts/demo.py` to `files` once clean) and a decision, by the owner, for the rest: either a per-tree error baseline that may only shrink, or an explicit statement in `.claude/skills/repo-architecture` that `scripts/` and `backend/tests` are outside the gate. Event that next confirms or discharges it: a merged change after which `uv run mypy` covers `scripts/demo.py` and the rest is baselined or declared out of scope. Filed by the executor, 2026-10-12.

***Resolved 2026-11-06*** — closed in place 2026-11-06 by the auditor, as the closing act of the audit of SL-2048 (WK-1178, LG-2049, PL-2047; this PR; its number, squash commit and merge date are written at the merge's date-of-record), on the lead's brief under the GO "2026-11-05 10:31:31 GMT" (plans C and H accepted, DP-H1 to DP-H5 ruled; `to-lead.md`, a local channel file), on the order of "2026-11-05 09:58:58 GMT". Delivered remedy: `scripts/demo.py` is under the gate and the rest is declared outside it. `check_environment` takes `Mapping[str, str] | None` with a local `env` (`48b745f6`) and `"scripts/demo.py"` joins `[tool.mypy] files` in `pyproject.toml`; `uv run mypy` rc 0 over 253 source files. Red: with `scripts/demo.py` in `files` and the base `demo.py`, `scripts/demo.py:77: error: Incompatible types in assignment …` and `:78: error: Item "None" of "dict[str, str] | None" has no attribute "get"`, `Found 2 errors in 1 file`: exactly two, so the CARRY fallback was not taken (re-measured at `dae9637e`, not grown). DP-H4 (a): `.claude/skills/repo-architecture/SKILL.md` carries a dated declaration (`8f3f537b`) that `scripts/` (231 errors) and `backend/tests/` (1983), as the triage measured them at `fc4401dc` by `uv run mypy scripts` and `uv run mypy backend/tests`, are outside the mypy gate, and a Verified line at tree `b4f4f7e24efeea0ebfc84282fe8e94c88492a943`. The auditor checked that tree is `48b745f6^{tree}` (the commit before the skill edit). `test_demo_command.py` at the audit head `33 passed, 2 errors` (DB-backed, owed). Gate evidence: the gate: pytest `13 failed, 7224 passed, 27 skipped, 5 xfailed in 4949.99s` alone, the 13 being the item-31 docs-audit set, every other python and frontend stage rc 0, demo seeded rc 0 (LG-2049).

