---
id: PL-8205
family: plan
kind: map
title: WK-675 — the blank-mapped-port fix slice (a mount never maps a port to a blank parent name; graph_invariant_issues refuses it on the mount, naming the port; OQ-1843 closed): Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-23
owner: planner
tree: 4e399fd01e8de2fe55d2f128b0e09ee2b2735c6a
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1546, PL-1286, OQ-1843, SL-1554, RL-1309, RL-1474, RL-1835, FR-212, FR-217, FR-1607]
---

# PL-8205 — WK-675: the blank-mapped-port fix slice, Work-plan delta

*Disclosure: drafted under working id 8205 (this plan), reserved by the lead in eta on
2026-10-23, and renumbered at the mint. The ruling it implements is RL 8203, on branch
`draft/rl-8203` @`8cd257f1`; the lead's brief says it mints as RL-1876 at its turn, written
here as "RL 8203 (→ RL-1876)". That minted id is the lead's relay: it was not in `to-lead.md`
at 10:53 BST. The finding the ruling's amendment files is FD 8204 (working id, reserved by
the lead). The slice's `SL-` and `LG-` ids are reserved by the lead at the GO, written below
as "SL <reserved at GO>" and "LG <reserved at GO>". None of the four working ids is in
`relates:`, because a front-matter id must resolve. The minter adds RL 8203's and FD 8204's
minted ids, and the slice's `SL-`, at the mint.*

> **For agentic workers:** this is a **one-row WK-675 Work-plan delta** under Lean P2 L5. It
> adds one fix slice to WK-675 beside the rows of
> [`PL-1546`](PL-01546-wk-675-slices-5-to-11-work-plan-delta.md), which has been frozen since
> its first merge, so a new slice is a new delta (`.claude/roles/planner.md`, Lean P2 (L5, L1)). No leaf
> plan. The slice is one PR under L1 (a'), and its `LG-` quotes the row below as its scope.
> REQUIRED SUB-SKILL for the executor: executing-plans (the slice is small). The executor
> also binds `spec-change` (the spec text goes first), `python-test` (`@pytest.mark.req`
> markers), `test-driven-development` (the red is seen first, by its cause),
> `vue-testing-best-practices` (Task 4 only), `dev-commands` (the two-half gate,
> `uv sync --all-packages` in a fresh worktree) and `git-hygiene`. It reads
> [`README.md`](README.md)'s five unchecked conventions and is spawned from
> `.claude/roles/executor.md`.

Written 2026-10-23 from 10:53 BST (`TZ=Europe/London date`, 10:53:24 BST) by the planner
(planner-8205), on the lead's brief `brief-planner-8205-2026-10-23.md`. Evidence was read at
`origin/main` `4e399fd01e8de2fe55d2f128b0e09ee2b2735c6a` (#1365) unless a line names another
tree. **No test was run at planning time**: every fact below is a read of a named file.

## Authority

- **The ruling, adopted**: the maintainer's entry "2026-10-23 10:48:01 BST — Maintainer: (A)
  SL-1569 may rewrite the SL-1566 test to assert REFUSAL; (B) RL 8203 ADOPTED with one
  amendment; (C) SL 8185 gate-ready ac1dce42 noted; the two breaches logged" in
  `channel/to-lead.md`, item (B), verbatim:
  *"**(B) RL 8203 (OQ-1843) is ADOPTED** (draft/rl-8203 @8cd257f1): a mapped parent name is
  never blank; the refusal lives in `graph_invariant_issues` (rating.py:662) on the mount
  naming the port (input RATING_GRAPH_UNRESOLVED_REF, output VALIDATION_FAILED), reached by
  save/validate/designer via FR-1607; no contract change; the inspector keeps storing "" so the
  server sees the gap. […] **Amendment:** the found gap (an output mapped to "" plus a step
  consuming "" saves today, with a trace value under an empty name) is **FILED AS AN FD** (LOW,
  owner WK-675) in the follow-on slice's PR, not left as prose. **Vehicle:** a follow-on WK-675
  fix slice, red-first in packages/model-schema/tests/test_graph_invariant_issues.py; NOT
  SL-1554. […] **The spec text it lists is owed in that slice** (03 §4.1 mount sentence + the two
  error-code rows), spec first."*
- **The ruling's content**: RL 8203 (→ RL-1876),
  `docs/rulings/RL-08203-a-mount-never-maps-a-port-to-a-blank-name-the-graph-invariants-refuse-it-on-the-mount-and-the-designer-shows-it-through-the-validate-route.md`
  on `draft/rl-8203` @`8cd257f1`. Its sections "Ruled" items 1 to 5, "Spec text owed", "The
  test the implementing slice carries (red first)", "What it obliges" and "Acceptance" are
  this slice's scope. They are cited by section, not restated where a pointer is enough.
- **The question it closes**: `OQ-1843`, `docs/open-questions.md:162` and
  `docs/specs/03-rating-engine.md:1615`, with its gate row at `docs/roadmap.md:3518`
  ("Before WK-675 closes").

## What the code and spec say, at `4e399fd0`

- `SubGraphRef.inputs` and `.outputs` are `dict[str, str]` with no length rule
  (`packages/model-schema/src/model_schema/rating.py:485-486`).
- `graph_invariant_issues` (`rating.py:662`) runs the duplicate `step_id` and `mount_point`
  checks, then returns early if either fired (`:704`). It then builds `purpose_only` from every
  mount's `outputs.values()` (`:710`) and one `_MountNode` per mount from
  `inputs.values()` / `outputs.values()` (`:716`), and runs `_graph_pass_issues` once per
  purpose graph. Nothing filters a blank name. So an input mapped to `""` reads as
  *"step '<mount_point>' consumes undefined value ''"* (`:771`), and an output mapped to `""`
  makes `""` a produced name, so a step consuming `""` resolves and the algorithm saves.
- `RatingAlgorithm._graph_invariants` (`rating.py:606`) raises on the first issue:
  `GraphUnresolvedRefError` for `RATING_GRAPH_UNRESOLVED_REF`, and `ValueError` for anything
  else (so `VALIDATION_FAILED` surfaces as a pydantic `ValidationError`).
- `03` §4.1's mount amendment is `:352`. The `RL-1474` paragraph with the invariant order
  ("located, in this order: a duplicate `step_id` (FR-215) […]; a declared output with no
  output step (FR-214); […]") is `:356`. No row anywhere under `docs/` is keyed by either error
  code. The predicate, verbatim:
  `git grep -n -E '^\| *\*{0,2}`?(RATING_GRAPH_UNRESOLVED_REF|VALIDATION_FAILED)`?' -- docs`
  prints one hit only, a ruling's table cell (`RL-01401-…md:58`). 03's code list (`:1118`) is
  prose and already names `RATING_GRAPH_UNRESOLVED_REF`. `VALIDATION_FAILED` is generic. See
  DP-1 for how "the two error-code rows" is read.
- `packages/model-schema/tests/test_graph_invariant_issues.py` (170 lines, no DB) already has
  the helpers `_mount_draft` (`:129`), `_mount` (`:138`), `_input`, `_output` and `_draft`, and
  three mount tests (`:147-170`).
- **`frontend/src/components/dag/MountInspector.vue` is not on main.** SL-1554 creates it
  (`git diff --diff-filter=A --name-only origin/main...origin/sl-1554-wk675-s9`, at its head
  `4439159e`). There, `setInput` (`:49-51`) stores whatever the field holds, and `setOutput`
  (`:53-58`) deletes the key on `""`. None of SL-1554's eight `MountInspector.test.ts` cases
  asserts that a cleared input stores `""`.

## Goal

A mount that maps a port to a blank parent name is refused by the one graph-invariant
function. The refusal is located on the mount and names the port, so save, the validate route
and the designer all see it (FR-1607). `03` §4.1 says so, and `OQ-1843` is closed in both
mirrors. Done when the slice closes on its `LG-` with the red on base, the green, the
broken-input proof, the spec text and the full two-half gate, and FD 8204's register row
carries the fix's merge sha.

## Acceptance Standard

Each item is a command run from the slice worktree's root, quoted in the `LG-` with its exit
code and the lines it names. "Base" is `origin/main` at the slice's first commit.

1. **Spec first.** `git log --reverse --format=%s origin/main..HEAD` shows the spec commit
   (Task 1) before or in the same commit as the code (Task 3). It is never after it.
2. **Red first, on base, by its cause.** With Task 2's three tests added and `rating.py`
   unchanged, `bash ~/gi-pricing-plan.local/handover/run-small.sh packages/model-schema/tests/test_graph_invariant_issues.py`
   exits 1. The FAILED lines are exactly the input-blank test (both `""` and `"  "`), whose
   issue names `''` rather than the port, and the output-blank test, which gets zero issues.
   The control test passes. Any other failure is not this slice's red.
3. **Green.** After Task 3, the same command exits 0 and lists every test in the file as
   passed, the three new ones included.
4. **The new check is what holds it (broken input).** With Task 3's blank-name check removed
   (uncommitted, reverted at once), the input-blank and output-blank tests fail again with the
   item-2 lines. Restored, they pass.
5. **One issue, not two.** The input-blank test asserts that no issue message contains
   `consumes undefined value ''` (RL 8203 "Ruled" item 2, last sentence).
6. **No contract change.** `uv run python scripts/generate-contracts.py --check` exits 0, and
   `git diff --stat origin/main...HEAD -- docs/contracts frontend/src/api/generated` is empty.
7. **OQ-1843 closed both ways, and the gate row recounted.**
   `git grep -n 'OQ-1843' -- docs/open-questions.md docs/specs/03-rating-engine.md docs/roadmap.md`
   shows the row struck and marked decided by RL 8203's minted id in both mirrors, and the
   `docs/roadmap.md` §10 row's count reads `1 (0 open)`.
8. **No new FR.** `uv run python scripts/req-coverage.py` exits 0, and
   `git diff origin/main...HEAD -- docs/specs | grep -cE '^\+\| \*\*FR-[0-9]+\*\*'` prints 0.
9. **The inspector still stores `""`.** Task 4's single vitest file run (common brief item 28's
   guard) exits 0 and shows `Test Files  1 passed`. With `setInput` changed to delete the key on
   `""` (uncommitted, reverted at once), the new case fails.
10. **The write set.** `git diff --name-only origin/main...HEAD` lists only the files in the
    row's write set below, plus `docs/INDEX.md` and `docs/findings/register.md` (generated or
    appended by the mint).
11. **The full gate is green.** Every `CLAUDE.md` §11 command, both halves, exits 0 against
    `origin/main...<slice branch>`, in gate-1 on the lead's grant. The diff is not docs-only
    (common brief item 30), so this is the full code gate.
12. **Barred word.** `git diff origin/main...HEAD | grep '^+' | grep -ciE 'dep''uty'` prints 0.

## Global Constraints

- **Spec first** (`CLAUDE.md` §0, the 10:48:01 entry): Task 1's spec text lands before or with
  Task 3's code, in the slice's one PR.
- **No contract change** (RL 8203 "Ruled" item 4.4): no `Field(min_length=…)` on
  `SubGraphRef`, and nothing under `docs/contracts/` or `frontend/src/api/generated` changes.
  A model validator on `RatingAlgorithm` is not in the JSON Schema. The check lives in
  `graph_invariant_issues`, which is not a field constraint.
- **One definition** (FR-1607): no rule is added to the frontend, and compile (`inline.py`
  `_port_mapping`) is unchanged.
- **No name rule beyond mount ports** (RL 8203 "Ruled" item 5): `consumes`, `produces`,
  `output_name` and `feature_map` keys are untouched. A step that *produces* `""` is out of
  scope (see Hand-off).
- **One PR per slice** (L1 (a')): spec text, code, tests, the `SL-` status lines, the `LG-` and
  FD 8204, in one PR.
- **Small runs** go only through `run-small.sh` (≤3 files, no DB; common brief items 6, 12 and
  32). The model-schema files named here need no database. **The GREEN set is derived by
  import closure** (common brief item 29) and quoted in the `LG-`. `rating.py` is imported
  widely, so that set is larger than a small run, and the slice's full gate is the decisive
  green.
- **Money and transparency**: no price moves (RL 8203 "Options", last paragraph). The change
  is that a value named `""` can no longer reach a trace.

## Tasks

Under L5 a Work plan's tasks are its slice rows. This row's steps follow the table.

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Lane | Size |
|---|---|---|---|---|---|---|
| after SL-1554 merges (WK-675) | SL <reserved at GO> — WK-675 fix slice — RL 8203 (→ RL-1876): a mount never maps a port to a blank parent name; `graph_invariant_issues` refuses it on the mount, naming the port; OQ-1843 closed; FD 8204 | **Spec text** (Task 1): the two dated clauses in `03` §4.1 (after `:352`, and in the `RL-1474` order paragraph at `:356`), `OQ-1843` closed in `docs/open-questions.md` and `03` §10, and the `docs/roadmap.md` §10 gate row recounted. **Tests** (Task 2): three cases in `packages/model-schema/tests/test_graph_invariant_issues.py` (input blank, output blank, control), red first. **Code** (Task 3): `graph_invariant_issues` in `packages/model-schema/src/model_schema/rating.py` reports each blank-mapped port on its mount and leaves blank names out of the mount node and `purpose_only`. **Designer pin** (Task 4): one case in `frontend/src/components/dag/__tests__/MountInspector.test.ts` asserting that a cleared input emits `inputs: {<port>: ""}`. **Finding** (Task 5): FD 8204 (LOW, WK-675), essay plus register row, discharged by this PR. **Write set**: `docs/specs/03-rating-engine.md`, `docs/open-questions.md`, `docs/roadmap.md` (§10 gate row; this slice's `SL-` status lines), `packages/model-schema/src/model_schema/rating.py`, `packages/model-schema/tests/test_graph_invariant_issues.py`, `frontend/src/components/dag/__tests__/MountInspector.test.ts`, the `LG-` under `docs/ledgers/`, FD 8204's essay under `docs/findings/` and its row in `docs/findings/register.md`. **Out of scope**: `MountInspector.vue` and every other non-test frontend file; `inline.py`; `SubGraphRef`'s fields; `docs/contracts/`; a name rule for other value names | `03` §4.1 (data contract, under existing ids): FR-212, FR-217; `03` §3: FR-1607 (unchanged, its route reports the new issue); `OQ-1843`; no new `FR-` | RL 8203 minted (→ RL-1876) on main; **SL-1554 merged** (Task 4's file and the component it tests exist only on `sl-1554-wk675-s9`); FD 8204's id reserved | at GO | ≈ 0.5 lane-day, derived: one function, one test file of three cases, one vitest case, three spec hunks plus the OQ pair and the gate row, one full gate |

### Task 0: Preconditions (read-only, quoted in the `LG-`)

- [ ] `git -C <wt> grep -n 'id: RL-' -- 'docs/rulings/RL-*a-mount-never-maps-a-port-to-a-blank-name*'`
  on the slice's base prints RL 8203's minted id. Use that id everywhere this plan writes
  RL-1876. If it differs from RL-1876, use the printed id and say so in the `LG-`.
- [ ] `git -C <wt> cat-file -e origin/main:frontend/src/components/dag/MountInspector.vue`
  exits 0 (SL-1554 merged). If it does not, Tasks 1 to 3 and 5 may proceed, but the PR waits
  for Task 4. Report it to the lead; do not edit SL-1554's branch.
- [ ] Re-read `rating.py` at the base. Quote the lines of `def graph_invariant_issues`,
  `if issues:` (the early return), the `purpose_only` loop and the `_MountNode(` construction.
  The line numbers in this plan are at `4e399fd0`.
- [ ] Re-read `03` at the base, and quote the line of the mount amendment ("Every input port
  of the mounted sub-graph is mapped exactly once") and of the `RL-1474` paragraph ("located,
  in this order").

### Task 1: Spec text, first (`spec-change`)

**Files:** `docs/specs/03-rating-engine.md`, `docs/open-questions.md`, `docs/roadmap.md`.

- [ ] **Step 1: the mount clause.** Append, as a new paragraph directly after the mount
  amendment (`03:352` at `4e399fd0`), RL 8203's text verbatim with `<date>` set to the commit
  date and `RL-<minted>` set to Task 0's id:
  > *(Amended <date>, `RL-<minted>`, OQ-1843: a mapped parent name is never blank — empty after
  > stripping whitespace — for an input or an output port; a blank name is not "unmapped". The
  > graph invariants report each such port on the mount: an input as
  > `RATING_GRAPH_UNRESOLVED_REF`, naming the port as unmapped (FR-217); an output as
  > `VALIDATION_FAILED`. The blank name is not counted as consumed or produced.)*
- [ ] **Step 2: the order clause.** In the `RL-1474` paragraph (`03:356`), do not edit the
  sentence. Append a dated clause at the paragraph's end:
  *"(Amended <date>, `RL-<minted>`, OQ-1843: a port mapped to a blank parent name, located on
  the mount, is checked after a duplicate `step_id` and before a declared output with no
  output step.)"*
- [ ] **Step 3: OQ-1843 closed, both mirrors.** In `docs/open-questions.md:162` and
  `03:1615`, use the spec-change form ("Deciding one is the same edit in three places"):
  strike the question; prefix `**DECIDED <date>: …**`; leave the options cell as it was;
  rewrite the recommendation cell as *"decided by `RL-<minted>`: (E), a graph-invariant issue
  on the mount naming the port, not the recommended (a); the clause is `03` §4.1's (FR-212,
  FR-217); no new FR"*; and set the status to **decided**, naming the resolver.
- [ ] **Step 4: the gate row.** `docs/roadmap.md` §10's "Before WK-675 closes" row (`:3518`):
  strike `OQ-1843`, add the decided pointer, and **recount** the cell to `1 (0 open)`. Keep
  the row (spec-change: "A decided question keeps its gate row").
- [ ] **Step 5:** `flock -w 900 /tmp/slots/gate-2 env -C <wt> python3 scripts/audit-docs.py`
  and `uv run --directory <wt> python scripts/req-coverage.py`, each rc quoted. Commit.

### Task 2: Red-first tests

**Files:** `packages/model-schema/tests/test_graph_invariant_issues.py`.

- [ ] Add three tests after `:170`, using `_mount_draft`, `_mount`, `_input` and `_output`.
  Import `ValidationError` from `pydantic` and `RatingAlgorithm` from `model_schema`.
  1. `@pytest.mark.req("FR-217")`, parametrised over `""` and `"  "`:
     `_mount("s_ncd", {"claims": blank}, {"factor": "ncd"})` with steps
     `[_input("s_in", "x"), _output("s_out", "out", "ncd")]`. Assert exactly one issue on
     `s_ncd`: code `RATING_GRAPH_UNRESOLVED_REF`, `step_id == "s_ncd"`, and a message
     containing `'claims'` and `unmapped`. Assert that no issue message contains
     `consumes undefined value`. The fixture is `:157`'s
     (`test_a_broken_mount_is_refused_by_the_invariants`) with `"ghost"` replaced by the blank
     name. That test asserts exactly one issue on the same shape, so `s_in` raises no orphan
     issue.
  2. `@pytest.mark.req("FR-217")`: `_mount("s_ncd", {"claims": "x"}, {"factor": ""})` with
     steps `[_input("s_in", "x"), _output("s_out", "out", "")]`. Assert a `VALIDATION_FAILED`
     issue with `step_id == "s_ncd"` and a message containing `'factor'`. Assert that
     `RatingAlgorithm.model_validate(draft.model_dump(mode="json"))` raises `ValidationError`.
  3. `@pytest.mark.req("FR-212")`: every port mapped to a non-blank name gives `[]` (the
     control; `:147`'s test already covers this case. Add it only if its fixture differs, and
     say which in the `LG-`).
- [ ] Run acceptance item 2's command on the unchanged `rating.py`, and quote the FAILED lines
  and rc 1 in the `LG-`. Commit the tests red, or with Task 3 if the PR policy at the GO says
  so. Either way, the red run is quoted.

### Task 3: The invariant

**Files:** `packages/model-schema/src/model_schema/rating.py`.

- [ ] In `graph_invariant_issues`, after the early return (`:704`) and before `selected = …`,
  loop over `draft.sub_graphs` and, for each port whose mapped name is blank
  (`name.strip() == ""`), append one `ValidationIssue` with `step_id=m.mount_point`. Use RL 8203
  "Ruled" item 2's messages verbatim: for an input, `RATING_GRAPH_UNRESOLVED_REF`, *"mount
  '<mount_point>' leaves input port '<port>' unmapped: its parent name is blank (FR-217)"*;
  for an output, `VALIDATION_FAILED`, *"mount '<mount_point>' maps output port '<port>' to a
  blank name; omit the port to leave it unmapped (FR-217)"*. Do not return early after this
  check: the per-purpose passes still run.
- [ ] Leave blank names out of `purpose_only` (`:710`) and out of each `_MountNode`'s
  `consumes`/`produces` (`:716`), so the input case is reported once and the output case
  produces no `""`.
- [ ] Update the docstring's first paragraph so it names the new check among FR-212/214/215's
  rules. Run acceptance items 3 to 5, then `uv run --directory <wt> ruff check .` and
  `uv run --directory <wt> mypy`, each rc quoted. Commit.

### Task 4: The designer still stores `""` (after SL-1554 merges)

**Files:** `frontend/src/components/dag/__tests__/MountInspector.test.ts`.

- [ ] Add one case: clearing an input-port field emits `update:mount` with
  `inputs: {<port>: ""}` (the key kept, the value empty). This pins RL 8203 "Ruled" item 4.1,
  so a later "tidy" of `setInput` that deletes the key goes red. Use the file's own fixtures
  (`mountFixtures.ts`).
- [ ] Run it with common brief item 28's guard:
  `F=src/components/dag/__tests__/MountInspector.test.ts; [ -f "<wt>/frontend/$F" ] || { echo "NO FILE: $F"; exit 64; }`,
  with load1 < 6 quoted first, then
  `flock -w 3600 /tmp/slots/small-test nice -n 19 ionice -c3 pnpm --dir <wt>/frontend exec vitest run "$F"`.
  The output must show `Test Files  1 passed`. Then run acceptance item 9's broken-input proof.

### Task 5: FD 8204 filed and discharged

**Files:** FD 8204's essay under `docs/findings/`, its row in `docs/findings/register.md`.

- [ ] The FD is filed **in this slice's PR** (the 10:48:01 amendment), severity LOW, owner
  WK-675, decision *fix before close with an owner: WK-675*, discharged by this slice. Under
  `document-ids.md` §1.6's FD row the essay and register row are the **auditor's** to author.
  The planner's draft text is at
  `~/gi-pricing-plan.local/scratch/draft/pl-8205/FD-8204-draft.md`; who files it is the
  lead's to name at the GO (open question 2 in the report).
- [ ] At the slice audit the auditor sets FD 8204 `closed`, citing the PR, and the register
  row carries the merge sha.

### Task 6: Gate and ledger

- [ ] Derive the GREEN set by import closure (common brief item 29), quote the commands and
  the list in the `LG-`, and run its model-schema members through `run-small.sh`, ≤3 files
  per run, no DB: `test_graph_invariant_issues.py`, `test_rating_algorithm.py` and
  `test_input_free_raises.py`.
- [ ] Run acceptance items 1, 6, 7, 8, 10 and 12. At the mint (common brief items 17, 19, 26
  and 34), regenerate `docs/INDEX.md`, run `doc-index.py --check` rc 0, and run `idsweep.sh`.
- [ ] Push, and report "ready to queue @<head>". The full gate (acceptance item 11) runs in
  gate-1 on the lead's grant. Closing acts per L1: the `LG-` and the `SL-` row closed at the
  head, after the audit.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | What are "the two error-code rows" the 10:48:01 entry says are owed? No row under `docs/` is keyed by either code (the predicate in "What the code and spec say"). | (a) The two refusals RL 8203 "Spec text owed" lists, one per port side, each with its code, carried by the mount clause (Task 1 step 1), plus the order clause (step 2); (b) add a code-to-cause line to 03's error-code list (`:1118`) for `RATING_GRAPH_UNRESOLVED_REF` (blank input port) and `VALIDATION_FAILED` (blank output port) | (a): it is the ruling's own list, and 03's code list is prose that names codes, not causes, so (b) would add a convention the list does not have | fact (reading of an entry) | no; (a) applies unless the lead rules otherwise at the GO | the lead, or the maintainer if the lead asks |
| DP-2 | Task 4 needs SL-1554's `MountInspector.test.ts`, which is not on main. | (a) The slice depends on SL-1554 merged, so it serialises after it (RL-1445 item 2); (b) drop Task 4 (RL 8203 says "A frontend test is not required") and run beside SL-1554 | (a): the ruling makes "the inspector keeps storing `""`" what lets the server see the gap (item 4.1), and only a test holds that. SL-1554 is already queued for its gate, so the wait is short | scope | yes, for the GO | the lead, at the GO |

## Contention (RL-1263 item 4, RL-1445 item 2)

Read at the named heads with `git diff --name-only origin/main...origin/<branch>`.

- **vs SL-1554** (`sl-1554-wk675-s9` @`4439159e`; same Work): the code files are disjoint
  (SL-1554 is frontend only). The test file `MountInspector.test.ts` is shared: SL-1554 creates
  it, and this slice adds one case. `docs/roadmap.md` is section-disjoint (SL-1554 changes its
  own `SL-` row, this slice changes its own row and the §10 gate row). **A plan dependency
  exists**: this slice consumes SL-1554's output (Task 4). Under RL-1445 item 2 (b) they
  **serialise**, this slice after SL-1554's merge (DP-2 (a)).
- **vs SL-1569** (`sl-1569-wk1178-decimal-outputs` @`38643ee1`; WK-1178, a different Work):
  **disjoint**. SL-1569 changes `packages/model-schema/src/model_schema/scoring.py`, not
  `rating.py`. It does not touch `03`, `docs/open-questions.md` or
  `test_graph_invariant_issues.py`. Both change `docs/roadmap.md`, in different `SL-` rows, and
  the generated `docs/INDEX.md` (registry-exempt, `delivery-process.core.json` "generated").
  Neither consumes the other's output, so they may build side by side under RL-1445 (at most
  three build slices, one full gate at a time).
- **`03` is a known shared file** (RL-1263 item 4). This slice touches §4.1 (`:352`, `:356`)
  and §10 (`:1615`) only. The lead's dispatch checks every other active slice's write set
  against those sections at the GO. This plan read only the two slices the brief names (no
  all-refs sweep).

## Hand-off (not this plan's writes)

- **The `SL-` row.** The lead reserves the slice's `SL-` and `LG-` ids at the GO. The planner's
  draft row text (status `draft`) is at
  `~/gi-pricing-plan.local/scratch/draft/pl-8205/SL-row-draft.md`, for the minter to place
  under WK-675 in `docs/roadmap.md` with the reserved id. The lead lists this delta on
  WK-675's roadmap row (L5).
- **A name rule for every value name** (RL 8203 "Ruled" item 5: a step that *produces* `""`
  is the same transparency hole by another route) is not this slice's. RL 8203 recommends the
  lead raise it as a new `OQ-` (owner WK-675) in the next docs batch.
- **FD 8204's authorship** is the auditor's under §1.6 (Task 5). The planner's text is a
  draft.

## Self-review

- **Coverage.** Every item RL 8203 "Spec text owed" and "The test the implementing slice
  carries" lists is a step: the mount clause (T1.1), the order clause (T1.2), OQ-1843 both
  ways (T1.3), the gate row recounted (T1.4), no FR with req-coverage rc 0 (acceptance 8), the
  three tests (T2), the one-issue-not-two rule (acceptance 5), and the optional frontend pin
  (T4). The 10:48:01 amendment (FD, LOW, WK-675, in the slice's PR) is T5. Requirement ids are
  listed one by one: FR-212, FR-217, FR-1607, OQ-1843. There is no range.
- **Placeholders.** `<date>`, `RL-<minted>`, "SL <reserved at GO>" and "LG <reserved at GO>"
  are values that do not exist until the commit, the mint and the GO. Task 0 resolves the
  first two. Nothing else is left open.
- **Consistency with the ruling.** The order in Task 3 (after the early return, before the
  per-purpose passes) is "Ruled" item 3. The messages are item 2's, verbatim. Compile, the
  JSON Schema, `setInput`, `setOutput` and `canSave` are unchanged (item 4).
- **Facts re-read, not relayed.** `rating.py` `:485-486`, `:606`, `:662`, `:704`, `:710`,
  `:716` and `:771`; `03` `:352`, `:356`, `:1118` and `:1615`; `open-questions.md:162`; and
  `roadmap.md:3518` were all read at `4e399fd0`. `MountInspector.vue`'s absence from main was
  checked with `git cat-file -e`. "RL-1876" is the lead's relay, and Task 0 checks it.
- **No decision taken.** DP-1 is a reading with a default. DP-2 is the lead's at the GO.
