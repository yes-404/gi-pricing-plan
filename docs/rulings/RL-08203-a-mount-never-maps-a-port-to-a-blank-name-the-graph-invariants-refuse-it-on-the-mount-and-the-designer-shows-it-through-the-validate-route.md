---
id: RL-8203
family: ruling
title: "OQ-1843 decided — a mount never maps a port to a blank parent name; the one graph-invariant function refuses it, located on the mount and naming the port, so save, the validate route and the designer all see it; no contract change and no rule in the inspector (draft for the maintainer to adopt or amend)"
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-23   # drafted 2026-10-23 under working id 8203; not minted
owner: decision-maker
tree: 40aa993134a9c2c88e474d925ea6fc844f638e68
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [OQ-1843, RL-1309, RL-1835, RL-1474, FR-212, FR-217, FR-1607, SL-1554, WK-675]
---

# RL-8203 — OQ-1843 decided: a mount never maps a port to a blank parent name, and the graph invariants refuse it on the mount

Drafted 2026-10-23 under working id 8203 on branch `draft/rl-8203`. **This is a draft for the
maintainer to adopt, amend or reject.** It rules nothing until the maintainer adopts it with a
dated line. It is not minted here; its INDEX row is the working id, renumbered at the mint.

**The question.** `OQ-1843` (`docs/open-questions.md:162`, mirrored at
`docs/specs/03-rating-engine.md:1615`, both at `origin/main` `4e399fd0`): *"May a mounted
sub-graph's input port be mapped to an empty parent name (`""`), and if not, which layer
refuses it?"* It was raised on the maintainer's entry "2026-10-22 13:26:06 BST — Maintainer:
SL-1554 re-audit CLEAN noted; the negative-control condition is endorsed; the empty port name
goes to an OQ" in `~/gi-pricing-plan.local/channel/to-lead.md` (local), whose item reads:
*"it is a design choice the spec leaves open (refuse an empty mapped name, or allow it). Under
CLAUDE.md §0 / §10, file it as an **OQ** in the next docs batch, with options, trade-offs and a
recommendation (owner WK-675). It is NOT a silent pick either way, and NOT built in this
slice."* The observation is RS 8158 (its file under `docs/research/` on branch
`aud-1554b-2026-10-22` @`cf0fb018`, section "The empty-string observation: not a defect against
a named clause").

**Provenance.** Seat dm-8203, spawned from `.claude/roles/decision-maker.md` by lead 27; model
Opus 5.5; `$CLAUDE_EFFORT` read in the seat's own shell as `medium`. The role file's line gives
`high` for a decision-maker ruling on the maintainer's raise; the lead cannot set effort per
spawn, so this ruling ran at `medium`, stated here rather than smoothed over.

## Verified first

At `origin/main` `4e399fd01e8de2fe55d2f128b0e09ee2b2735c6a` (tree `40aa9931…`), read, not run,
unless stated:

1. **`03` §4.1's mount amendment** (`03-rating-engine.md:352`, `RL-1309` DP-3 items 2 to 4):
   *"Every input port of the mounted sub-graph is mapped exactly once, and the mapped output
   ports are a non-empty subset; an unmapped output port is legal, and a parent step that
   consumes one is refused by FR-212."* No clause says a mapped parent name is non-empty.
2. **The shape.** `SubGraphRef.inputs` and `.outputs` are `dict[str, str]` with no length rule
   (`packages/model-schema/src/model_schema/rating.py:485-486`). No value name in the module has
   one: a step's `consumes`/`produces` (`:370-371`) and `output_name` (`:445`) carry none; the
   only name rules are `step_id` `min_length=1` (`:367`) and `mount_point`'s pattern (`:484`).
3. **The one definition of the graph rules.** `graph_invariant_issues` (`rating.py:662`) is what
   `RatingAlgorithm._graph_invariants` (`:606`) raises on and what the validate route reports
   (FR-1607). A mount is a node whose consumed names are `inputs.values()` and produced names are
   `outputs.values()` (`:716`), so an input mapped to `""` is reported as
   `RATING_GRAPH_UNRESOLVED_REF` *"step '<mount_point>' consumes undefined value ''"* (`:771`),
   located on the mount — unless some node produces `""`.
4. **The output side has a hole.** Nothing refuses a mount output mapped to `""` (or a step
   producing `""`). A mount with `outputs: {"p": ""}` produces the parent name `""`
   (`_produced_by` over the mount nodes, `:745`), so a step consuming `""` resolves and the
   algorithm saves, carrying a value whose name is empty into every trace that records it.
5. **Compile** (`packages/pricing-core/src/pricing_core/rating/inline.py:77-102`,
   `_port_mapping`) refuses a port *absent* from `mount.inputs` (FR-217, naming the port) but
   compares key sets only; a key mapped to `""` passes it. It runs only on saved algorithms.
6. **FR-1607** (`03-rating-engine.md:89`): *"The rules are defined once: the route and save run
   the same functions, and the frontend re-implements none of them."* The designer calls the
   validate route as the graph changes and shows each located issue on its node.
7. **The inspector**, read at `origin/sl-1554-wk675-s9` @`059af1a54c127c4d691cacfd7ea6129acbb8c4f1`
   (2026-10-23T09:15:57Z; the branch has moved since the audited `ab48b63e`):
   `frontend/src/components/dag/MountInspector.vue:49-51` (`setInput`) stores whatever the field
   holds, so clearing it stores `""`; `:53-58` (`setOutput`) deletes the key on `""`. The
   designer places issues on a mount by `mount.mount_point` (`DagDesigner.vue:107`). Its save
   gate `canSave` (`RatingDesignView.vue:72-74`) reads only `stepProblems` (`problems.ts:8-24`,
   required fields of steps), not server issues; save itself refuses on the first issue.
8. **`RL-1835`** (ii) 4: `validate_draft` does not read the fragment, so the designer cannot
   report a port *absent* from the map before save; the inspector's one-row-per-port layout is
   the stated prevention. A port stored as `""` is therefore the one unmapped case the server can
   see before compile — but only if the inspector keeps storing it.

## Options

| | Option | For | Against |
|---|---|---|---|
| A | **Refuse at the schema field**: `SubGraphRef.inputs`/`outputs` values take `min_length=1` | One rule at the shape; refused at parse on every path | A JSON-Schema change (`docs/contracts/` and the frontend client regenerated, ADR-704); a field error from parse, not a located `ValidationIssue`, so the validate route — which parses a `RatingAlgorithmDraft` with the same field — answers 422 instead of a report and the designer loses the issue on the node (FR-1607's shape); and a length rule on mount names alone is a partial name rule |
| B | **Refuse at compile**: `_port_mapping` treats a blank value as unmapped | Message names the port; pricing-core only | Too late: save already refuses the input case with a worse message, and the output case is saved and only then refused; a second definition of a graph rule outside the one function |
| C | **Allow with a defined meaning**: a blank mapped name means "unmapped" | No refusal; matches what `setOutput` does | Two encodings of one meaning in a content-hashed artifact (`{"p": ""}` and `{}` hash differently and mean the same); for inputs "unmapped" is still illegal, so the meaning only moves the refusal from save to compile (`validate_draft` cannot see an absent port, item 8) |
| D | **Refuse in the inspector only** (`OQ-1843`'s recommended (a)) | Cheap; frontend only | FR-1607 forbids the frontend re-implementing a graph rule; a non-UI author still meets the `''` message; the output hole (item 4) stays |
| E | **Refuse in the graph invariants** — `graph_invariant_issues` reports a blank mapped name as its own issue, located on the mount, naming the port | One definition (FR-1607): save, the validate route and the designer all get it; no JSON-Schema change (a model validator is not in the schema); closes the output hole; the inspector keeps its current code | A backend change to the one function and a new place in §4.1's issue order |
| F | **Leave as is** | Input case already refused at save | Message names `''`, not the port; output hole stays open |

**Money and transparency.** No option moves a price: the input case never saves today (item 3),
and the output case computes the same numbers whatever the name. The consequence is
transparency — an algorithm saved through the output hole carries a value named `""` into its
trace and explanation, which no reader can attribute. That is the outcome E changes, beyond the
message.

## Ruled

1. **A mapped parent name is never blank**, for an input port or an output port. *Blank* means
   empty after stripping whitespace (`name.strip() == ""`), the same test `problems.ts` applies
   to a step's required text. A blank name has no meaning: it is not "unmapped" (option C is
   refused — one meaning, one encoding).
2. **The layer is the graph invariants (option E)**, and only there. `graph_invariant_issues`
   reports, for each mount and each port mapped to a blank name, one issue located on the mount
   (`step_id` = the `mount_point`):
   - an input port: `RATING_GRAPH_UNRESOLVED_REF`, *"mount '<mount_point>' leaves input port
     '<port>' unmapped: its parent name is blank (FR-217)"* — the code compile already uses for
     an unmapped port, so the existing refusal keeps its code;
   - an output port: `VALIDATION_FAILED`, *"mount '<mount_point>' maps output port '<port>' to a
     blank name; omit the port to leave it unmapped (FR-217)"*.
   The blank name is then not counted as consumed or produced by that mount, so the input case
   is reported once, by the port, and not again as *"consumes undefined value ''"*.
3. **Order.** The check runs after the duplicate-`step_id` check and before the per-purpose
   passes (it does not depend on purpose), so in §4.1's order it sits between *"a duplicate
   `step_id` (FR-215)"* and *"a declared output with no output step (FR-214)"*.
4. **The other layers, in order, and what each does:**
   1. *Designer* — no rule of its own (FR-1607). The inspector **keeps** storing `""` for a
      cleared input field: that is what lets the validate route show the port on the mount node
      before save; deleting the key would hide it until compile (item 8). `setOutput` is
      unchanged. `canSave` is unchanged.
   2. *Save and the validate route* — refuse/report by item 2, on every path (UI, API, import).
   3. *Compile* — unchanged; it never sees a blank name, because a saved algorithm cannot carry
      one. `_port_mapping` keeps refusing an absent port (FR-217).
   4. *JSON Schema / contracts* — unchanged (option A refused).
5. **Not ruled here: a name rule for every value name** (`consumes`, `produces`,
   `output_name`, `feature_map` keys). A step producing `""` is the same transparency hole as
   item 4 by another route. It is a wider question across FR-212's whole graph; this record
   recommends the lead raise it as a new `OQ-` (owner WK-675) in the next docs batch, and does
   not decide it.

## Spec text owed (by the implementing slice, under `.claude/skills/spec-change`)

Not edited in this PR (the brief, and the role file: a spec edit is made with its ruling in the
same commit). The implementing slice writes, citing this record by its minted id:

- **`03` §4.1, after the mount amendment at `:352`**, a new dated line:
  > *(Amended <date>, `RL-<minted>`, OQ-1843: a mapped parent name is never blank — empty after
  > stripping whitespace — for an input or an output port; a blank name is not "unmapped". The
  > graph invariants report each such port on the mount: an input as
  > `RATING_GRAPH_UNRESOLVED_REF`, naming the port as unmapped (FR-217); an output as
  > `VALIDATION_FAILED`. The blank name is not counted as consumed or produced.)*
- **`03` §4.1, the invariant order** (the `RL-1474` paragraph, "located, in this order"), a dated
  clause inserting *"a port mapped to a blank parent name, located on the mount"* after the
  duplicate `step_id` and before the declared output with no output step.
- **`OQ-1843` closed, mirrored both ways** — `docs/open-questions.md:162` and `03` §10 `:1615` —
  status *closed*, resolution *"decided by `RL-<minted>`: (E), not the recommended (a)"*, citing
  the resolver; and `docs/roadmap.md` §10's decision-gate row (`:3518`) moved to `1 (0 open)` in
  the same commit (`spec-change`).
- No `FR-` is added: the clause is §4.1's data-contract rule, enforced under FR-212/FR-217's
  existing ids. `req-coverage` rc 0 is quoted.

## The test the implementing slice carries (red first)

In `packages/model-schema/tests/test_graph_invariant_issues.py` (an existing file; no DB):

1. **Input blank.** A draft whose mount maps input port `x` to `""` (and a second case, `"  "`).
   Assert exactly one issue on the mount: code `RATING_GRAPH_UNRESOLVED_REF`, `step_id` = the
   `mount_point`, message containing `'x'` and `unmapped`; and no issue whose message contains
   `consumes undefined value ''`. **Red today**: the issue's message names `''`, not `x`.
2. **Output blank.** A draft whose mount maps output port `y` to `""` and a step consuming `""`.
   Assert a `VALIDATION_FAILED` issue on the mount naming `'y'`, and that `RatingAlgorithm`
   refuses it. **Red today**: zero issues — it saves (Verified item 4).
3. **Unchanged control.** A mount with every port mapped to a non-blank name reports no issue.

The red is quoted from a run on the slice's tree before the fix (`run-small.sh`, one file), and
the green after. A frontend test is not required: the designer's path is FR-1607's existing
issue-on-node rendering. If the slice adds one, it asserts that clearing an input field still
emits `inputs: {<port>: ""}` (so a later "tidy" to `setInput` that deletes the key goes red).

## The vehicle (recommended; the dispatch is the lead's)

**A follow-on fix slice of WK-675, not SL-1554.** SL-1554 is built, audited CLEAN on its object
and awaiting its gate; the maintainer's entry said the empty name is *"NOT built in this
slice"*; and the fix lies in `packages/model-schema` plus `03`, outside SL-1554's frontend write
set, so riding it would void its audit. The new slice is small (one function, one test file,
three spec hunks, the OQ mirror pair and the roadmap gate row) and needs the full code gate,
because its diff is not docs-only (seat-brief item 30). It should land before WK-675 closes —
the gate `OQ-1843`'s roadmap row names.

## What it obliges

- The implementing slice's `LG-` cites this record at each task, writes the spec text above in
  the same commit as the code, and closes `OQ-1843` in both mirrors.
- The auditor checks: the issue is located on the mount and names the port; the input case
  yields one issue, not two; the inspector's `setInput` still stores `""`; no JSON-Schema file
  under `docs/contracts/` changed.

## Acceptance — the violation that must become detectable

A `RatingAlgorithm` whose mount maps an output port to `""` and a step consuming `""` is
accepted today. After the slice, parsing it raises, and `POST /api/v1/rating-algorithms/validate`
reports the port by name on the mount.
