---
id: FD-1936
family: finding
title: A mount output mapped to a blank parent name saves, and a step consuming it resolves, so a value with an empty name reaches the trace
status: closed                  # active → closed | retired (§1.2a)
created: 2026-10-26               # drafted 2026-10-25 under working id 8204
owner: auditor
tree: 8c3d3013c3205fbecd6335e9db182a469426bdb2
corrected_by: []
relates: [WK-675, OQ-1843, RL-1876, PL-1937, LG-1939]
---

# FD-1936 — A mount output mapped to a blank parent name saves, and a step consuming it resolves, so a value with an empty name reaches the trace

## Finding

**LOW; owner WK-675.** Severity and owner from the maintainer's entry "2026-10-23 10:48:01 BST"
(`to-lead.md`), item (B), "Amendment": the found gap is filed as an FD in the follow-on slice's PR.
Found by RL-1876, section "Verified first", item 4 ("The output side has a hole"). Filed by the
slice's auditor under the GO of "2026-10-25 22:52:52 GMT", condition (4), working id 8204.

A `RatingAlgorithm` whose mount maps an output port to `""`, with a step that consumes `""`, passed
every graph invariant and saved. `graph_invariant_issues` counted a mount as a node that produces its
mapped output names, and no rule looked at whether a mapped name was blank. The saved algorithm then
carried a value with an empty name into every trace and explanation that records it. No price moves:
the numbers are the same whatever the name. The consequence is transparency, which `CLAUDE.md` §1
puts first. Before RL-1876 no clause was broken: `03` §4.1 said the mapped output ports are a
non-empty subset and said nothing about a blank parent name.

Out of scope: a **step** that produces `""` is the same hole by another route. RL-1876 "Ruled" item 5
leaves a name rule for every value name undecided. This FD covers the mount-port route only.

## Evidence

Read at `origin/main` 8c3d3013, `packages/model-schema/src/model_schema/rating.py`:

- :486 — `SubGraphRef.outputs: dict[str, str]` has no rule on its values.
- :704 — `if issues: return issues` follows only the duplicate-`step_id` and `mount_point` checks.
- :710 and :716 — `m.outputs.values()` enters `purpose_only` and the `_MountNode` unfiltered, so the
  mount produces `""` and a consumer of `""` resolves.

Executed proof: the slice's red commit 4290018b on the unchanged `rating.py`
(`test_graph_invariant_issues.py`): rc 1, `3 failed, 10 passed`; the output test gets
`assert 0 == 1` (no issue). Green at 0a85d0cb: `13 passed`. With the blank-name check disabled
the same file goes red again, `3 failed, 10 passed` (LG-1939 Build log).

## Remedy

Made by SL-1938 (PL-1937), commits 197a7df4 (spec, `03` §4.1) and 0a85d0cb (code):
`graph_invariant_issues` reports each blank-mapped output port as one `VALIDATION_FAILED` issue
located on the mount, naming the port, and does not count the blank name as produced; an input port
gets `RATING_GRAPH_UNRESOLVED_REF`. No contract change.

## Disposition

**Fix before close with an owner: WK-675**, discharged by SL-1938 (PL-1937). Resolved by this slice;
the auditor sets it `closed` in place, citing the PR, and the register row carries the merge sha
(owed at merge).
