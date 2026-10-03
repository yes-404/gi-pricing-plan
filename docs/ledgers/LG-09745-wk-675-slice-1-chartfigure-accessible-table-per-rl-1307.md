---
id: LG-9745
family: ledger
title: WK-675 slice 1 — ChartFigure's accessible table per RL-1307, its 13 call sites migrated, F39 diagnosed (SL-1369, PL-1368, RL-1307)
status: active
created: 2026-10-03
owner: executor
tree: 3915e5d977870da4a084f77243aa036d378972a7
phase: P2
work: WK-675
slice: SL-1369
plans: [PL-1368]
corrected_by: []
relates: [RL-1307, PL-1286, RL-1263, NFR-463]
---

# LG-9745 — WK-675 slice SL-1369, the ChartFigure accessible table

Executed from `PL-1368` by `executor-1369` (sonnet, medium: `echo $CLAUDE_EFFORT` printed `medium`). Branch `sl-1369-chartfigure-accessible-table`, from `origin/main` `2171aab0d9b5ab1bbef29d6023bdc2d33eeddd48` (#1069; tree `3915e5d977870da4a084f77243aa036d378972a7`). The ledger's id `9745` is a working id, allocated by the lead; the lead is the only allocator and mints the final id. Every time is `TZ=Europe/London date`, BST. Append-only: later entries add, none rewrites.

The executor charter's Model / effort line, verbatim: "`sonnet` (currently Sonnet 5); medium, inherited from the lead — the highest-volume role; per-slice gates and the auditor's re-check bound the risk of a cheaper setting."

## Tasks

### Task 0 — preconditions

**Dispatch record, FINAL, quoted verbatim** (`gi-pricing-plan.local/handover/DISPATCH-WK-675-SL1369-2026-10-01.md`, as read 2026-10-03 15:56:16 BST, which includes Delta 3 (the Task 0 reads at 15:36 BST preceded it); each line prefixed `> `):

> # Dispatch record: WK-675 Slice 1 (SL-1369), the ChartFigure accessible table, from PL-1368 (FINAL)
>
> **Status: FINAL** (2026-10-03 15:35:29 BST, the lead, after #1069 merged as 2171aab0; tree 3915e5d9). *Earlier status line, kept:* DRAFT. Drafted 2026-10-01 after #1058 merged at 11:01:11 BST (main 49cd25be). Lane A. It goes FINAL on the maintainer's GO check and the activation PR's merge. PL-1368 is frozen from its first merge (#1058), so it is not edited; every delta lives here.
>
> **The order:** the maintainer's entries on WK-675 S1, 2026-10-01: commission the S1 leaf if only resolved items gate it (met: DP-1 → RL-1307); "S1's dispatch record must state that PL-1286 :240, :249-250 and :415-416 ((b)) are superseded by RL-1307 (c)"; the overrule of the duplicate-key choice (refusal in every build); (X) "#1058 mints first (PL-1368 + SL-1369)"; MERGE-ACK #1058 at 04f3e64c.
>
> ## Plan and slice status on main (the gate check, FIRST)
> - **Main at drafting:** 49cd25be (#1058 merged; read-back parent 92b4e4ac, tree d324ffe7 = the ACK tree).
> - **PL-1368:** `status: draft`. **SL-1369:** `status: draft`. Both flip to `active` in the separate activation PR (planner-675s1, DRAFT, not ready until the GO).
> - **PL-1286** (WK-675's map plan): stays `draft` per its own rule ("leaves activate individually", the maintainer).
>
> ## Activation needs (PL-1368 §"Activation needs", run)
> 1. **The maintainer's agreement**, as a dated line: **MET**, by the entry headed "2026-10-01 11:04:02 BST — GO: WK-675 Slice 1 (SL-1369, PL-1368) on lane A, with ONE correction to the dispatch record (DP-4's label is (b), not (a)); this entry is PL-1368 activation need 1's dated maintainer agreement".
> 2. **The lead's go**, recorded in the activation PR: **MET** — the GO check at 2026-10-03 14:56:02 BST, recorded in #1069's squash body (main 2171aab0).
> 3. **The PL-1286 staleness line, carried here verbatim** (the maintainer): **PL-1286 :240, :249-250 and :415-416 (DP-1 open, recommending (b)) are SUPERSEDED by RL-1307 (c). No executor follows the frozen map's prose.** RL-1307 (active, on main) is the scope authority: items 1, 3, 4 and 5 plus its four violations, as PL-1368 quotes them. **Met by this record.**
> 4. **The holds, read** (holds-2026-10-01.md):
>    - FD-1366 (filed as FD 9779) per-route hold: S1 calls none of the five routes. **Does not apply.**
>    - FD-1335 /score hold (S6, S7, S7b): **does not apply.**
>    - FD 9752 hold (no code READS the four to_dict approval responses): S1 reads none. **Does not apply.**
>    - The FD-1336 rung hold is LIFTED.
>    - **Met.**
> 5. **A free lane under RL-1263:** lane A is free (WK-674 S2 is not yet dispatchable). Lane B holds SL-1360 (WK-1178: tests/test_permission_parity.py, an LG file, INDEX). Different Works, **no shared non-exempt file** (S1 writes frontend/ only, plus its ledger and INDEX, which is registry-exempt). The second to merge re-gates. **Met (to be re-checked at the GO).**
> 6. **Task 0's re-measurement** of the call-site count: the executor runs `git grep -n '<ChartFigure' origin/main -- 'frontend/src/*.vue'` at the dispatch tree (13 lines in 11 files at 92b4e4ac/49cd25be). WK-690 S5 (SL-1275) is not merged, so the count is 13 unless it lands first. **Executor's Task 0.**
>
> ## Decision points: every one has a resolver
> - DP-1 (PL-1286) → RL-1307 (c), active.
> - S1's open method choices are the plan's own (migration order; the empty-state wording; the production error wording `Table unavailable: two columns in "<title>" share the key "<key>" (…)`).
> - The plan's DP-4 (F39 remedy; PL-1368:280: (a) S1 widens / (b) a new FD- with an owner): **the lead's verdict is (b)**: S1 lands the diagnosis either way; a remedy lands in S1 only if it is confined to test code; a cause outside test code goes to a new FD- whose `decision:` the lead sets. *(Corrected 2026-10-01 11:04 BST on the maintainer's GO entry headed "2026-10-01 11:04:02 BST — GO: WK-675 Slice 1 (SL-1369, PL-1368) on lane A, with ONE correction to the dispatch record (DP-4's label is (b), not (a)); this entry is PL-1368 activation need 1's dated maintainer agreement". The draft said "(a)" while describing (b), a mislabel by the lead. It also supersedes the maintainer's earlier "DP-4 (a) accepted" for #1058; the substance accepted is (b).)*
> - The duplicate-key refusal: the maintainer's OVERRULE (every build, role=alert, no DEV gate, red-first CI test), applied in PL-1368.
> - **No task is held.**
>
> ## Conditions
> 1. **Write set:** frontend/src/components/ChartFigure.vue and its test, the 13 call-site components and their tests (3 new test files: CalibrationChart, GbmEvalCurveChart, LineageGraph), frontend/src/chart-table.ts (new), frontend/src/test-tables.ts, possibly frontend/src/test-setup.ts (F39, test code only), frontend/src/components/__typecheck__/ fixtures, its ledger under docs/ledgers/, and the regenerated docs/INDEX.md. Nothing under backend/, packages/ or docs/specs/.
> 2. **Frontend gate, both halves** (CLAUDE.md §11), with the shared-chunk size delta in the PR (PL-1286 Acceptance 7 / PL-1368 Acceptance 10). The four type fixtures are proven on the locked vue-tsc 3.3.11.
> 3. **Gate evidence for EVERY suite-level run:**
>    - a clean checkout of the named SHA, `git status --porcelain` empty;
>    - `uv sync --all-packages`; `ruff check --no-cache`; `mypy --no-incremental`;
>    - the dev-commands slot wrapper verbatim plus `LOKY_MAX_CPU_COUNT=4`;
>    - `uptime` and `free -h` at start and end; the other holder via `flock -n`;
>    - **the test DB created first** (SL-1360's Run 1 failure);
>    - read the stage table, never the exit code.
>    Single-file vitest and pytest runs are slot-exempt.
> 4. **Red first** on every acceptance item, with the outputs pasted (incl. the duplicate-key DEV=false case, Step 5a's gate proof, and the permuted-cell case).
> 5. **Ledger:** LG working id **9745** (allocated by the lead 2026-10-03 15:35:29 BST, free-checked on origin refs, worktrees and handover), allocated by the lead at GO (the lead is the only allocator); append-only; BST stamps; Task 0 quotes this FINAL record verbatim.
> 6. **Frozen records:** nothing in docs/plans/, docs/rulings/ or any frozen body is edited. The executor writes no spec text (S1 has none).
> 7. **Executor:** a fresh `executor-1369` from `.claude/roles/executor.md` with its Model / effort line, in a new worktree from origin/main after the activation PR merges. It never `cd`s.
> 8. **PR:** a draft "feat(frontend): SL-1369 — ChartFigure accessible table per RL-1307 (WK-675 Slice 1, PL-1368, LG <id>)". The slice audit, mint and close follow; the lead allocates ids.
>
> ## Deltas
> - **Delta 1, 2026-10-01 11:04 BST (lead):** the GO is received (above). Contention: if S1's gate overlaps SL-1360's re-gate, it is a CANDIDATE CONTENTION PAIR, so BOTH ledgers record both walls, uptime/free at start and end, and the other holder via flock -n (the maintainer, GO entry).
>
> - **Delta 2, 2026-10-03 15:35:29 BST (lead): FINAL.** The GO is the deputy's "2026-10-03 14:33:44 BST — RESUME (Sat 3 Oct): first GO to the NEW lead …" item 2, and the MERGE-ACK "2026-10-03 15:34:34 BST — MERGE-ACK #1069 …". **Main = 2171aab0** (PL-1368 and SL-1369 `active`). Re-checked at 2171aab0: `<ChartFigure` count 13 (unchanged); **lane B is idle** (SL-1360 merged d8537220; no build slice running), so need 5 holds and no contention pair is possible until lane B dispatches; gate slots gate-1/gate-2 have no holder (`/tmp/slots/` was cleared by the reboot; the wrapper's `mkdir -p` recreates it). The holds file is unchanged since 2026-10-01 10:20:30. **DP-4 = (b)** (stated above). **PL-1371** (the lane-loading plan, accepted 14:56:08) does not change S1's scope. Executor: **executor-1369**, sonnet, from `.claude/roles/executor.md`, a fresh worktree from origin/main 2171aab0. Delta 1's candidate-pair rule now applies to whichever lane-B slice dispatches next.
> - **Delta 3, 2026-10-03 15:50:15 BST (lead): the three "new" test files already exist.** executor-1369 reported, and the lead verified at origin/main 2171aab0 (`git ls-tree`): `frontend/src/components/__tests__/{CalibrationChart,GbmEvalCurveChart,LineageGraph}.test.ts` exist, added by dbb4ea06 (#194, 2026-08-25) and a551469a (#257, 2026-08-26). PL-1368:1087-1088 ("Create:") and Step 1 ("Write the two new test files") were wrong when written; Condition 1's "3 new test files" likewise. **Ruling:** the NFR-463 tests are ADDED to the existing files; every existing test stays unchanged and passing (no deletion, rename or weakened assert); red first per new test. Write set unchanged (same paths). Recorded in LG 9745. Not blocking; a note for the slice audit, not an FD (rule 14).

- **Step 1, the tree.** `git fetch origin`; `git rev-parse origin/main` printed `2171aab0d9b5ab1bbef29d6023bdc2d33eeddd48`. The worktree HEAD was the same SHA, and `git status --porcelain` was empty.
- **Step 2, call sites.** `git grep -n '<ChartFigure' origin/main -- 'frontend/src/*.vue'` printed 13 lines in 11 files, all under `frontend/src/components/`: `AeByFactorChart.vue:86`, `CalibrationChart.vue:92`, `CrossValidationPanel.vue:148`, `CrossValidationPanel.vue:161`, `DoubleLiftChart.vue:150`, `GbmEvalCurveChart.vue:73`, `GbmImportanceCharts.vue:133`, `GbmImportanceCharts.vue:146`, `HistogramChart.vue:111`, `LiftChart.vue:98`, `LineageGraph.vue:122`, `OneWayChart.vue:181`, `PartialDependencePanel.vue:83`. No site beyond the plan's 13.
- **Step 3, holds and RL-1307.** `holds-2026-10-01.md` names WK-675 S1 in no hold (the FD-9779 per-route hold, the FD-1335 `/score` hold: S1 calls none of the routes). `git log --oneline 1dd5e264..origin/main -- docs/rulings/RL-01307-*.md` printed nothing.
- **Step 4, toolchain.** `pnpm --dir frontend install --frozen-lockfile` and `pnpm --dir frontend generate:api` ran clean. `frontend/node_modules/vue-tsc/package.json` says `"version": "3.3.11"`, the locked one.

**Plan defect found in Task 0 (a measured premise that is wrong).** PL-1368 (*Measurements*, Tasks 3 and 5) says `CalibrationChart`, `GbmEvalCurveChart` and `LineageGraph` have no test file, and Tasks 3 and 5 "Create" them. `git ls-tree --name-only 1dd5e264 frontend/src/components/__tests__/` and the same at `2171aab0` both list `CalibrationChart.test.ts`, `GbmEvalCurveChart.test.ts` and `LineageGraph.test.ts`. The files date from #194 (`dbb4ea06`) and #257 (`a551469a`). I reported it to the lead before 15:50:15 BST (Delta 3's stamp). **The lead ruled (Delta 3 of the dispatch record):** add the `NFR-463` tests to the existing files, and leave every existing test unchanged and passing. Done: three tests added (`GbmEvalCurveChart`, `LineageGraph`, and two in `CalibrationChart`), no existing test deleted, renamed or weakened. Where an existing test read a `ChartFigure` table by cell position, the row header shifts the index by one, so the read moved to `cellUnder` by label with the same expected value (Task 3 Step 2, Task 5 Step 2; each such change is listed under its task).

### Task 1 — F39, what opens port 3000

Gate slot: granted by the lead 15:36:56 BST for head `2171aab0` ("full frontend vitest, F39 repro"); taken as `flock -n -E 99 /tmp/slots/gate-1` around `pnpm --dir frontend test`. The slot wrapper's gate body is the Python half's; this was a frontend-only run, so the body was `LOKY_MAX_CPU_COUNT=4 timeout 3000 pnpm --dir frontend test`. At start (15:37:13): `uptime` load average 0.63, 0.46, 0.44; `free -h` 31Gi total, 3.0Gi used, 28Gi available; `flock -n /tmp/slots/gate-2 true` rc 0 (the other slot free). At the end of the first run (15:37:51): load 3.72, 1.26, 0.71; 28Gi available. The test database step of Condition 3 is not applicable to a vitest-only run (no database). Clean tree at 2171aab0 for the first run (`git status --porcelain` empty).

- **Step 1, reproduce.** `pnpm --dir frontend test > /tmp/sl1369-f39-full.txt 2>&1`, rc 0, 97 files, 609 tests. `grep -n -m5 'ECONNREFUSED\|AggregateError'` printed line 7 `AggregateError:`, line 10 `code: 'ECONNREFUSED'`, line 12 `Error: connect ECONNREFUSED ::1:3000`, line 16, line 21 `Error: connect ECONNREFUSED 127.0.0.1:3000`. Reproduced exactly as the register row says, before any test output.
- **Step 2, localise to a file.** One run per file (script `/tmp/sl1369-f39-loc.sh`, Step 2's loop over `git ls-files 'frontend/src/*.test.ts'`: 87 files; the other 10 of the 97 are `*.test-d.ts` type tests that vitest's typecheck mode runs). Output: `HIT src/views/__tests__/ModelSpecBuilderView.test.ts`. One hit.
- **Step 3, localise to the call.** `--reporter=verbose` shows the error printed after test 3 and before test 4 ("keeps the three objective shapes apart when the tab changes"). The view mounts `ObjectivePicker` (GBM tab), whose `onMounted` calls `listObjectives()` (`ObjectivePicker.vue:114`) through `pageThrough` (`api/paging.ts:47`) and `request` (`api/client.ts:64`) into `fetch`. The test mocks `@/api/modelSpecs`, `@/api/datasets`, `@/api/models` and `@/api/versions`, and not `@/api/objectives`.
- **Step 4, the hypothesis.** It held: the call is `fetch` through `client.ts`, unstubbed. With the Step 6 guard installed and a stack trace added temporarily, the failing test printed: `Error: F39: this test called fetch without stubbing it: http://localhost:3000/api/v1/custom-objectives?limit=200` (`src/test-setup.ts:23`), with the stack `request (client.ts:64) < pageThrough (paging.ts:47) < listObjectives (objectives.ts:51) < ObjectivePicker.vue:114`. The stack line was removed before the commit.
- **Step 5, home of the remedy.** The cause is in test code (an unmocked module in one test file), so the remedy lands in S1 (*Choices* 7; DP-4 = (b) does not fire). No FD- is needed for F39's remedy.
- **Step 6, the remedy and the guard proven red.** Guard added to `frontend/src/test-setup.ts` as the plan's block (plain assignment to `globalThis.fetch`, an `afterEach` that throws `F39: this test called fetch without stubbing it: <urls>`). **Red first**, the culprit file with the guard and no stub: `FAIL … > keeps the three objective shapes apart when the tab changes`, `Error: F39: this test called fetch without stubbing it: http://localhost:3000/api/v1/custom-objectives?limit=200`, `Tests 1 failed | 9 passed (10)`. The message is the plan's. Then `ModelSpecBuilderView.test.ts` gained `vi.mock("@/api/objectives", …)` (spreading `importOriginal`, `listObjectives` returning `{ items: [], truncated: false }`), and the file passed 10 of 10. **Full suite with the guard and the stub** (15:43:05, under the same slot grant, a working tree carrying only the Task 1 edits; `/tmp/sl1369-f39-guarded.txt`): rc 0, 97 files, 609 tests (the same counts as Step 1), `grep -c ECONNREFUSED` printed `0`. No further test file turned red, so the three-file stop condition did not arise. End of run: load 5.60, 2.34, 1.24.
- **Step 7.** Committed `bf1cb8fc` (`test(frontend): F39 — diagnose the port-3000 socket (WK-675 S1)`). `docs/findings/register.md` is not edited (Acceptance 9): F39's dated resolution is the auditor's at slice close, citing this PR.

### Task 2 — the generic ChartFigure, its types, tests and fixtures

- **Step 3, red first.** `ChartFigure.test.ts` rewritten as the plan's text; run on the old component (`/tmp/sl1369-t2-red.txt`): `Tests 11 failed (11)`. Causes: nine fail on the arity guard (`Error: ChartFigure "Lift by decile": row 0 has undefined cells but there are 3 columns ([object Object] | [object Object] | [object Object]).`); the empty-state test fails because `No rows — this figure has no data to show.` is absent (`Unable to find an element with the text`); the duplicate-key case "with DEV false" fails with `Unable to find an accessible element with the role "alert"`. The duplicate-key case "as built" fails earlier, on the dev arity guard's throw, which is one of the two causes the plan allows ("a render throws in the arity guard").
- **Step 4/5.** `ChartFigure.vue` rewritten (generic `T`, descriptors, `<th scope="row">` for the first column, the every-build duplicate-key alert, the new empty-state text). One deviation from the plan's sample, to keep Acceptance 4's grep empty: the sample's comment contained the text `import.meta.env.DEV`; the committed comment says "no dev-only gate". The test file passes: `Tests 11 passed (11)`.
- **Step 5a, a DEV gate is caught.** With `if (!import.meta.env.DEV) return null;` added at the top of `duplicateKeyError`: `× refuses two columns that share a key, with DEV false, as in production`, `TestingLibraryElementError: Unable to find an accessible element with the role "alert"`, `Tests 1 failed | 10 passed (11)`. Only the stubbed case failed. Gate removed; `Tests 11 passed (11)`; `grep -c 'import.meta.env.DEV' ChartFigure.vue` prints 0.
- **Step 6, each fixture red twice, on vue-tsc 3.3.11** (`bash /tmp/sl1369-fixtures.sh`, output `/tmp/sl1369-fixtures.out`; the run was repeated after the ESLint comment was added to the fixtures, and the lines below are from that second run):

```text
BadAccessor (a) directive removed:   src/components/__typecheck__/ChartFigureBadAccessor.vue(19,96): error TS2339: Property 'bnad' does not exist on type 'Band'.
BadAccessor (b) fault corrected:     src/components/__typecheck__/ChartFigureBadAccessor.vue(19,3): error TS2578: Unused '@ts-expect-error' directive.
BadCellType (a):                     src/components/__typecheck__/ChartFigureBadCellType.vue(17,94): error TS2322: Type 'string[]' is not assignable to type 'Cell'.
BadCellType (b):                     src/components/__typecheck__/ChartFigureBadCellType.vue(17,3): error TS2578: Unused '@ts-expect-error' directive.
Mismatch (a):                        src/components/__typecheck__/ChartFigureMismatch.vue(22,27): error TS2322: Type 'Band[]' is not assignable to type 'readonly Other[]'.
Mismatch (b):                        src/components/__typecheck__/ChartFigureMismatch.vue(22,3): error TS2578: Unused '@ts-expect-error' directive.
NoAnyLeak (a):                       src/components/__typecheck__/ChartFigureNoAnyLeak.vue(19,96): error TS2322: Type 'string' is not assignable to type 'number'.
NoAnyLeak (b):                       src/components/__typecheck__/ChartFigureNoAnyLeak.vue(19,3): error TS2578: Unused '@ts-expect-error' directive.
```

  Every message is the one Acceptance 3 names. The fixtures were restored after each run. **`type-check` error count after Task 2:** 28 `error TS` lines, all in the 11 unmigrated caller files (`AeByFactorChart` 1, `CalibrationChart` 1, `CrossValidationPanel` 7, `DoubleLiftChart` 1, `GbmEvalCurveChart` 1, `GbmImportanceCharts` 10, `HistogramChart` 1, `LiftChart` 1, `LineageGraph` 1, `OneWayChart` 1, `PartialDependencePanel` 3); none in `ChartFigure.vue`, `chart-table.ts`, `ChartFigure.test.ts` or `__typecheck__/`.
- **Step 7.** `test-tables.ts`'s three statements replaced with the plan's text; the grep of Acceptance 7 prints nothing (rc 1).
- **Step 8, lint.** `pnpm --dir frontend lint` first reported 8 `vue/max-attributes-per-line` warnings in the fixtures (ESLint's `--max-warnings 0`). The plan's fallback (move the directive inside the element) does not work, since a comment cannot sit inside a start tag. Instead each fixture's template starts with `<!-- eslint-disable vue/max-attributes-per-line -- the expect-error directive covers one line only -->`, and the `@vue-expect-error` comment stays on the line directly above the element. Lint then passed, and the fixtures were re-proven (above). A plan defect, resolved inside the fixtures.
- Committed `61801223`.

### Task 3 — Group A, seven sites

- **Step 1, red first.** The two new tests (`GbmEvalCurveChart`, `LineageGraph`, named `NFR-463: …`) and the existing positional reads, run on the unmigrated components (`/tmp/sl1369-t3-red.txt`): `Tests 16 failed | 21 passed (37)`. Causes: `Unable to find an accessible element with the role "table" and name …` for each of the five components (the old components reach the descriptor-only `ChartFigure` and its render fails). Both new tests are among the failures.
- **Step 2, positional reads converted** (same expected values, read by label): `CrossValidationPanel.test.ts` (`cells[1]` → `cellUnder(table, /^0\.01/, "Std score")`), `PartialDependencePanel.test.ts` (`cells[2]` → `cellUnder(table, /0-3/, "Exposure share")`), `GbmImportanceCharts.test.ts` (the permutation `cells[3]`, `cells[4]` → `"Repeats"`, `"Seed"`; the gain `cells[1]` → `"Cover"`). The two other `getAllByRole("cell")` reads in that file read the hand-written monotonicity table and are left alone.
- **Step 3, migrated** per the plan's table. `CrossValidationPanel` row types come from indexed access on the generated type (`CrossValidationDiagnostics["path"][number]`, `["fold_metrics"][number]`), not hand-written. `LineageGraph` defines the component-local `LineageRow`.
- **Step 4.** The five test files pass: `Tests 37 passed (37)`. `type-check` names no Group A file; the remaining list is the six Group B and C files.
- **Step 4a, the fourth violation shown red** (`/tmp/sl1369-t3-4a.txt`). With the `Train` accessor changed to `(p) => p.holdout ?? null`: `× NFR-463: puts each partition's value under its own heading, read by label`, `Error: expect(element).toHaveTextContent()`, `Expected element to have text content: 0.487`, `Received: 0.499` (`GbmEvalCurveChart.test.ts:63`). The fixture's train and holdout differ (0.487 against 0.499). Accessor restored; `Tests 7 passed (7)`. Not committed.
- Committed `92233348` (amended once, to drop a now-unused `within` import that ESLint refused; no review had started).

### Task 4 — Group B, three sites

- **Step 1.** The three existing test files on the Task 3 head: `Tests 16 failed | 14 passed (30)` (`/tmp/sl1369-t4-red.txt`), because the components pass positional rows to the descriptor-only `ChartFigure`.
- **Step 2/3/4.** Migrated per the plan's table (`HistogramChart` and `DoubleLiftChart` keep the conditional Exposure column and the FR-10 decimal-string docstrings; `OneWayChart`'s `columns` is a `computed` reading `props.currency`). The three files pass: `Tests 30 passed (30)`. `type-check` lists only `AeByFactorChart`, `CalibrationChart`, `LiftChart`.
- **Step 5, the two other positional readers.** `GlmDiagnosticsPanel.test.ts` (the `getAllByRole("cell")` reads at lines 30, 42-43 and 51) and `views/__tests__/DiagnosticsView.test.ts` (lines 114, 149-150, 170): neither `GlmDiagnosticsPanel.vue` nor `DiagnosticsView.vue` contains `ChartFigure` (`git grep -n ChartFigure` prints nothing for both), so each reads a hand-written table and is left alone. The two files pass (`Tests 27 passed`).
- Committed `87f82baa`.

### Task 5 — Group C, three sites

- **Step 1, red first.** `CalibrationChart.test.ts` gained two tests (`NFR-463: puts each partition's value under its own heading, read by label`, and the shared-caption case with two partitions both captioned "Train", asserting no alert and five column headers). On the unmigrated components, with the existing tests (`/tmp/sl1369-t5-red.txt`): `Tests 5 failed | 10 passed (15)`; the three new-or-converted `CalibrationChart` tests and the `AeByFactorChart` and `LiftChart` table tests fail with `Unable to find an accessible element with the role "table" and name …`.
- **Step 2.** The whole-row positional reads in `AeByFactorChart.test.ts` and `LiftChart.test.ts` (`getAllByRole("cell").map(…)` against an array of the row's values) read the row header too after the migration, so they moved to `cellUnder` per label, every expected value kept (5 and 7 values).
- **Step 3/4.** Migrated with index-based keys (`p${index}-…`). The three files pass: `Tests 15 passed (15)`. **Step 5:** `pnpm --dir frontend type-check` rc 0.
- Predicate re-run on the branch: `git grep -n '<ChartFigure' HEAD -- 'frontend/src/*.vue'` prints 17 lines, because the pathspec `frontend/src/*.vue` also matches the four `__typecheck__` fixtures; with `| grep -v __typecheck__` it prints the same 13 lines in the same 11 files as Task 0, each touched in Tasks 3 to 5.
- Committed `3fd07379`.

## Acceptance self-check (at `3fd07379`, `bash /tmp/sl1369-accept.sh`)

```text
A1a: 1
A1b:
HEAD:frontend/src/api/models.ts:127:  source_columns: readonly string[];
HEAD:frontend/src/components/FactorCreateForm.vue:38:const props = defineProps<{ datasetId: string; columns: readonly string[] }>();
rc=0
A1c:
10:export type Cell = string | number | null;
12:export interface Column<R> {
A2: lines excluding __typecheck__:
13
4
A4:
rc=1
A6:
rc=1
A7:
rc=1
A5/A8 names:
frontend/src/components/__tests__/GbmEvalCurveChart.test.ts:58:  it("NFR-463: puts each partition's value under its own heading, read by label", () => {
frontend/src/components/__tests__/LineageGraph.test.ts:43:  it("NFR-463: puts each lineage field under its own heading, read by label", () => {
frontend/src/components/__tests__/CalibrationChart.test.ts:50:  it("NFR-463: puts each partition's value under its own heading, read by label", () => {
frontend/src/components/__tests__/CalibrationChart.test.ts:61:  it("NFR-463: renders both columns when two partitions share a caption, since keys use the index", () => {
pkg/lock diff:
```

Notes. Item 1's second command, as the plan wrote it, prints two lines that are not ChartFigure's: `frontend/src/api/models.ts:127` (`source_columns: readonly string[];`, the substring `columns: readonly string[]` inside `source_columns`) and `frontend/src/components/FactorCreateForm.vue:38` (its own `columns` prop). Neither is a `ChartFigure` prop. No line names `checkedRows`, `row.length !== width` or ChartFigure's old prop. Item 2: 13 call-site lines in 11 files plus the 4 fixture lines the pathspec also matches. Items 4, 6, 7: each grep prints nothing (rc 1). `frontend/package.json` and `frontend/pnpm-lock.yaml` are unchanged (the empty `pkg/lock diff`).

## PRs

None yet.

## Gate and bundle (Task 6)

GATE_PLACEHOLDER
