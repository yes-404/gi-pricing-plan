---
id: RS-1890
family: research
kind: audit
title: FD-1887 fix slice SL-1888 (WK-1178) slice audit, the freMTPL2 data guard at 59759536
status: draft
created: 2026-10-25   # drafted 2026-10-23 under working id 8213; minted 2026-10-25 as RS-1890
owner: auditor
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1888, LG-1889, FD-1887, SL-1711]
---

# RS-1890 — FD-1887 fix slice SL-1888, slice audit

*(Working id 8213, written by `aud-8194`, 2026-10-23, from the brief `brief-aud-8194-2026-10-23.md` (lead 27). Check 31/32 on this id and on FD-1887, SL-1888, LG-1889 are expected until the mint.)*

## Question

Does the slice remedy FD-1887 as the maintainer's entry "2026-10-22 18:19:23 BST" (`to-lead.md`) ruled: a STATIC guard test, every test that references `examples/fremtpl2/data` (path literal or the data helper) carries the data-present guard (marker or fixture), red-first by an injected unguarded test, small slice after #1361?

## Method

Range `origin/main...59759536` (`origin/main` `ff976406`, merge-base `4e399fd0`). Read by `git show`, `git diff`, `git grep` and the logs under `~/gi-pricing-plan.local/scratch/fix-8194/`. No test, DB, redis or gate was run. One probe: the guard module, `git show 59759536:tests/test_fremtpl2_data_guard.py`, imported from a copy and its `unguarded_tests()` called on fixture strings (a static function, no pytest, no repository file read beyond `git show` of the example's sources). The slice worktree was not touched.

## Checks

1. **Write set.** `git diff --name-only origin/main...59759536` = `docs/INDEX.md`, the LG, `docs/roadmap.md`, `tests/test_fremtpl2_data_guard.py`. No product code. The roadmap diff is one hunk (`@@ -2926,6 +2926,26 @@`, the `#### SL-1888` row, `relates: [FD-1887, LG-1889]`). **Met.** The guard file's blob is identical at `d66ad2ed` and `59759536` (`463ca77c…`), and `ca2057fb..59759536` touches the LG only, so the `ca2057fb` green run covers the head's code.
2. **The predicate, read.** Per `test_*` function it builds the closure (called helpers, fixtures named as parameters, module level, all inside the one file), then asks Reach (a derived data-reader name, a module-level alias of the data dir, `DATA_DIR`, a `fremtpl2/data` literal, or one expression joining `"data"` to `.arff`/`freMTPL2`) and Guard (an `if …exists…: …skip…`, a `skipif` naming `exists`, or a `setattr` of `DATA_DIR`). Readers are derived from `examples/fremtpl2/*.py` by transitive callers of `DATA_DIR`/`to_csv`. Scan roots: `backend/tests`, `packages/*/tests`, `tests`, `examples/fremtpl2`, non-recursive `test_*.py`. At `59759536` every `test_*.py` under those three trees sits directly in a scanned root (no nested test directory), and `pyproject.toml` `testpaths` has the same roots. **Reach and guard work as claimed on the shapes the LG names.**
3. **Can it miss? Yes. The claim "a static guard that cannot miss" does not hold.** Probed on fixtures, readers derived at `59759536` (`build_csv`, `build_portfolio_csv`, `portfolio_policies`, `a5_a6`, `uat_and_a`). Controls first: a literal `'examples/fremtpl2/data/x'`, an f-string path, a `'data' / 'freMTPL2freq.arff'` join, a class method, an async test and a comprehension all return `['test_a']` (caught). Not caught (returns `[]`):
   - **Path built from parts inside a function:** `ROOT / 'examples' / 'fremtpl2' / 'data'`, `Path('examples','fremtpl2','data')`, `os.path.join(…,'fremtpl2','data',…)`. The join test needs the marker `freMTPL2` (case-sensitive) or `.arff`; lowercase `fremtpl2` is recognised only in a **module-level** alias.
   - **A reader imported under another name** (`from …seed import build_csv as bc; bc(5)`) or fetched by string (`getattr(seed, 'build_csv')`): the check matches the called name.
   - **A reader reached through a subprocess** (`subprocess.run(['python','examples/fremtpl2/seed.py'])`): no name, no `fremtpl2/data` literal.
   - **A reader reached through a fixture in `conftest.py`, or a helper in another file:** the closure stops at the file. (At `59759536` no `conftest.py` and no `deploy_stack_helpers.py` names the data; this is a latent limit, not a live miss.)
   - **A guard that guards something else:** `if not Path('/nope').exists(): pytest.skip(…)` anywhere in the test or any helper in its closure counts as the guard, whatever it tests.
   The LG states two limits (names matched by name; a call into another test file's helper is not followed). It does not state the rest. **None is shown to be a live miss: the green run reports zero offenders, and `backend/tests/conftest.py`, the root `conftest.py`, `packages/pricing-core/tests/conftest.py` and `deploy_stack_helpers.py` name no data reader (`git grep -c -i -E 'fremtpl2/data|\.arff|build_csv|portfolio_policies|DATA_DIR'` is empty for each). LG-1889's six-file enumeration is the executor's and was not re-derived here.** They are the next #1361.
4. **RED first.** `71e481fa-red-injected.log` (the LG's (a)): `F.......`, `AssertionError: reads examples/fremtpl2/data without a data-present guard (CI never fetches it): backend/tests/test_zz_injected.py::test_injected_unguarded`, `1 failed, 7 passed in 9.97s`. The assert text names the injected file, so the injection ran; the injected file's content is not in any log. **Met on content, thin on provenance (B1).**
5. **GREEN.** `71e481fa-green-main.log` `8 passed in 12.84s`; `71e481fa-green-injected-guarded.log` `8 passed in 9.20s` (the injected test with a skip guard); `b0d2580c…-merged-guard.log` line 1 the head, `8 passed in 10.33s`, `rc=0`; `ca2057fb-guard-run-small.log` line 1 `head ca2057fb… tree 0230fad3…`, `8 passed in 10.70s`. `origin/main` has moved to `ff976406`, which touches `docs/INDEX.md`, FD-1713's essay and the register only (`git diff --name-only 4e399fd0 ff976406`): no test file, so `ca2057fb`'s green stands for the code at `ff976406`. **Met.**
6. **Negative controls.** The file's seven fixture tests pin: helper chain flagged; literal and alias flagged; a skip guard (helper or fixture) passes; a `DATA_DIR` redirect passes; a comment, an `.exists()` with no skip, and a skip under an unrelated flag are not guards; a test that reaches nothing is not flagged. They run inside the 8 passed. The `c-proof.log` run feeds `0a6cd6c9:test_wf701_journey.py` to the checker and flags exactly `test_wf701_journey_runs_end_to_end` and `test_c7_fails_naming_the_band_when_the_sample_rate_is_zero`, the two tests the CI run failed. **Met.** Passing these licenses "the guard fires on the shapes its author saw", not "every unguarded read is found" (see Check 3).
7. **The LG's lines against the logs, and the SHAs.** `d66ad2ed`, `b0d2580c`, `ca2057fb`, `7529198e` and `71e481fa` each exit 0 under `git merge-base --is-ancestor <sha> 59759536`. Line-by-line: LG (a) `1 failed, 7 passed in 9.97s`, (b) `8 passed in 12.84s`, guarded variant `8 passed in 9.20s`, (c) the two names, (d) `8 passed in 10.33s` `rc=0`, (e) `8 passed in 10.70s` all equal the logs. Two statements do not: (i) the LG says "the log's first line the head it ran on". The three `71e481fa-*` logs carry the sha only in their file names; line 1 is the `run-small: waiting …` line. (ii) the LG records `rc=0` for (b) and (e) and `rc=1` for (a); none of those three logs contains an `rc=` line (`b0d2580c…` and `c-proof.log` do). The pytest summary lines imply the exit codes; the logs do not record them. **B1.**
8. **Authority and scope.** No requirement id is claimed (`git grep -n -E 'pytest.mark.req|FR-' 59759536 -- tests/test_fremtpl2_data_guard.py` is empty), so `scope-audit.py` has no module to run and `req-coverage` is unaffected. The slice has one file of code, DB-free (no `createdb`, no fixture from `conftest_db`), so item 32's "small run beside a gate" holds. The order the entry set (after #1361, then re-merge main) is met: `ca2057fb` re-merged `4e399fd0` after #1361's merge. The remaining owed items are the LG's own (gate, mint, serial order behind FD 8199's fix).
9. **Not re-verified:** the LG's ruff, format and mypy lines at `d66ad2ed` (tools would have to run), the gate script's hash, audit-docs on the branch (rc 1 on checks 31/32, own ids only, per the LG's executor log). They rest on the executor's record.

## Findings

- **FD-1887** is filed with this record (no record existed on `origin/main` or the branch; the LG's Owed line named it): LOW-MEDIUM, owner WK-1178, remedy SL-1888, the maintainer's rating kept (the auditor reads the product impact as none and the cost as a red CI on a merge candidate). The CI run ids of #1361's red run are not named by the LG, the entry or the PR body draft (`<run id>` placeholder); not invented.
- No new FD against the slice. The Check 3 shapes are limits of a delivered remedy, not a defect in the product; whether to harden the guard is the lead's (proposals H1, H2 below).

## Notes and proposals (not blocking unless the lead says so)

- **B1 (LG text, small).** Correct LG-1889's two statements of Check 7: say the three `71e481fa-*` logs name their head only in the file name and carry no `rc=` line, with the exit codes inferred from the summary, or add the head and rc lines to the logs. The Audit section of the LG is written at the mint anyway.
- **B2 (LG text, small).** Add Check 3's found shapes to the LG's stated limits, or drop "cannot miss" from any PR text; the LG's wording today ("Its limits, stated: …") lists two of the seven.
- **H1 (optional hardening, the lead's call).** Recognise lowercase `fremtpl2` in a join, a `Path(...)` call and `os.path.join` inside a function, and follow `from … import x as y`; both are a few lines in `_names_the_data_path` and `_loaded`. **H2:** require the guard's `.exists()` expression to name the data (`DATA_DIR`, `ARFF`, a `fremtpl2` or `.arff` string, or an alias found in Reach) so an unrelated skip no longer passes. If the lead accepts the limits as recorded, H1 and H2 need no slice.
- LG-1889 front matter `tree: d66ad2ed…` is the guard commit's tree, not the head's; cosmetic.

## Verdict (PROPOSED)

**NOT-CLEAN, two B-items, both LG wording (B1, B2); no code change is required.** If the lead adopts them as LG edits at the mint, or rules the limits accepted, the slice is CLEAN: the guard is real, red-first by an injected test whose failure names it, green at `ca2057fb` and unchanged in code to the head, and it flags exactly the two tests #1361 failed. The verdict is the lead's.
