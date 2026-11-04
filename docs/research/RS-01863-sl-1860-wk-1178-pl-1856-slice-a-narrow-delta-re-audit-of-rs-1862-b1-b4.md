---
id: RS-1863
family: research
kind: audit
title: SL-1860 (WK-1178) PL-1856 slice A narrow delta re-audit — RS-1862 B1–B4 only
status: draft
created: 2026-10-22   # drafted 2026-10-22 under working id 8188; minted 2026-10-22 as RS-1863
owner: auditor
tree: 71504d9806e236d419a4f3ed1181462b26ecf0fd
phase: P2
work: WK-1178
corrected_by: []
relates: [RS-1862, SL-1860, LG-1861, PL-1856, FR-89]
---

# RS-1863 — SL-1860 narrow delta re-audit (RS-1862 B1–B4 only)

*(Disclosure: drafted under working id 8188; minted 2026-10-22 as RS-1863 in the slice A PR (SL-1860). Working-id forms of this record, the slice, the ledger and the plan in the body are re-pointed to RS-1862, RS-1863, SL-1860, LG-1861 and PL-1856; branch, path and worktree names are unchanged.)*

*(Working id 8188, written by `aud-8166r` (auditor, sonnet, effort medium), 2026-10-22 17:50 BST, from `brief-aud-8166r-2026-10-22.md` (lead 26). Check 31 on this id is expected until the mint. Slice and ledger are cited by their working ids `SL-1860` and `LG-1861`.)*

## Question

After the remedies, does `eece638c..afdea774` meet RS-1862's four blocking items B1–B4, and is the evidence for each one reachable? Narrow by design (the RE-audit rule): nothing outside B1–B4 is re-opened.

## Method

Object: `origin/sl-8166-wk1178-pl8162-a` = `afdea77451f0c8edcf6a1530ac1677a10c001ecf` (`git ls-remote origin` agrees), tree `71504d9806e236d419a4f3ed1181462b26ecf0fd`. Delta `eece638c..afdea774` is three commits: `480d73ea` (merge of `origin/main` `71e481fa`, #1359), `4885504c` and `afdea774` (both LG-1861 only). `git diff --name-only 480d73ea afdea774` lists only the LG-1861 file. Read by `git show/diff`, `grep`, `sed` only; no test, DB, docker, gate or generator was run by this seat. RS-1862 read at `origin/aud-8166-2026-10-22` (`afa6ffc7`, whose first commit is `cc2f93b2`). Evidence logs read from `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/` and `/tmp/*8166b.out`.

## Findings

### Verdict proposal: NOT-CLEAN on B1–B4 — B1 and B3 MET, B2 and B4 each MET on content with one claim that has no persisted log

Verdict is the lead's. The record text of every remedy is correct; what is missing is durable evidence for three claims (the six frontend runs, the post-merge contract check, the NB count). B2 is the one that RS-1862 asked for by name.

| # | State | Where |
|---|---|---|
| B1 | **MET** | LG-1861 "### Deviation (RS-1862 B1 …)" |
| B2 | **NOT MET on evidence** (wording MET; 1 of 6 frontend logs reachable) | LG-1861 GREEN paragraph and "GREEN additions" |
| B3 | **MET** | LG-1861 "Skips named (RS-1862 B3)"; `exec-b-skips.log` |
| B4 | **MET on content; 2 claims with no persisted log** | LG-1861 front matter, RED paragraph, "Open observation" |

### B1 — the spec-after-code deviation: MET

- LG-1861 `### Deviation (RS-1862 B1, disclosed post hoc 2026-10-22)` names `db41422c` after `e29cefcc` and `53d0433f`, against `PL-1856` acceptance item 3 (spec first), and says history is not rewritten.
- Order checked against git: `e29cefcc` 15:09:34Z, `53d0433f` 15:11:59Z, `db41422c` 15:12:06Z (`git log -1 --format='%h %aI'`).
- No rewrite: `git merge-base --is-ancestor <sha> afdea774` exits 0 for all three.
- The maintainer's ruling (accept the deviation, no reorder) is the authority the brief cites; the LG cites "lead 26 / RS-1862 B1" and not that entry by header. Cosmetic.

### B2 — GREEN relabel and the six frontend files: NOT MET on evidence

Met:
- The GREEN paragraph now reads "text-grep derived set, NOT an import closure (corrected 2026-10-22 on RS-1862 B2 …)", names 312 as RS-1862's static closure and "an upper bound", and states "the gate's FULL suite is the decisive green". Predicate command still quoted verbatim. The tail "this set of 75 is not a subset-proof of it" is weaker than RS-1862 (which found the 75 a subset by `comm -13`); conservative, not wrong.

Not met:
- LG-1861 "GREEN additions" lists six files, each "alone under the item-28 guard … `Test Files  1 passed (1)` shown, all rc 0": `reachability.test.ts` 2 tests, `routeGraph.test.ts` 9, `DemoView.test.ts` 7, `DiagnosticsView.test.ts` 16, `ModelComparisonView.test.ts` 6, `ModelDetailView.test.ts` 20.
- The brief's check is per log: `test -f`, exact path, `Test Files 1 passed`, load1 < 6, first line the sha. **Only one log of the six is reachable**: `/tmp/v8166b.out` (16:42:44, `Test Files  1 passed (1)`, `Tests  20 passed (20)`; the 20 matches `ModelDetailView`). It holds no `test -f` line, no path, no sha and no load1, and `/tmp` is not durable. The five others (2, 9, 7, 16, 6 tests) are in no file I could find (`grep -rl` over `gi-pricing-plan.local` and `/tmp` for each file name, newer than 16:30Z). `scratch/sl-8166/` holds only `exec-a-fe-green.log` and `exec-a-fe-red.log` (the builder view, pre-delta).
- So the six passes are the LG's claim, not evidence a reader can open. Item 28's guard cannot be checked from a claim.
- Cure (the lead's to rule): the executor writes the six guard transcripts (or the one script's single log) into `scratch/sl-8166/` and the LG names the path; or the lead accepts the claim and the gate's full frontend suite ("Test Files N passed" on the MERGE-ACK) as the decisive green.

### B3 — named skips: MET

- Backend: `scratch/sl-8166/exec-b-skips.log` (`HEAD=480d73ea`, load1 3.25, `PYTEST_ADDOPTS=-rs` through `run-small.sh`, own DB `createdb rc=0`, `alembic rc=0`): `SKIPPED [1] backend/tests/test_contracts.py:1341: got empty parameter set for (slug)`, the same at `:2072`; `187 passed, 2 skipped, 1 warning in 23.79s`, `RUN rc=0`. Source at `afdea774`: both lines sit at a `@pytest.mark.req("FR-451")` decorator before a test; a skip with the reason "empty parameter set" is a parametrize over an empty slug list. It is not a database or MinIO skip (those come from `conftest_db.py`, which would say so).
- pricing-core: source at `afdea774`: `test_glm_scalar_predict.py:330` is `pytest.skip("examples/fremtpl2/data is not fetched …")` inside `_demo_modules()`, called by the tests at `:398`, `:408`, `:546` (decorators at those lines); `:438` is `pytest.skip(f"the Factor shape refuses a bare {kind.value!r} …")`, per kind. LG's reasons match the source. The `-rs` output of that run is **not** in `exec-b-skips.log` (backend only); the reasons are verified here from source, not from a run's output. None is a DB/MinIO skip.

### B4 — branch, re-merge, LG fields: MET on content; two claims unlogged

- Pushed: `git ls-remote origin sl-8166-wk1178-pl8162-a` = `afdea77451f0c8edcf6a1530ac1677a10c001ecf`.
- Re-merge: `71e481fa` is an ancestor of the tip; `480d73ea` is the merge. `/tmp/mt8166b.out` shows the `docs/INDEX.md` conflict only (stages 1/2/3), as the LG says. **`generate-contracts.py --check` "54 generated contracts match the models" after the merge: no post-merge log**; the only `54 generated` hit is `exec-a-gen2.log`, pre-merge. Claim not evidenced. (The merge brought `docs/contracts/openapi/generated.json` changes from main, so this check is the one that matters.)
- LG front matter `tree: 31e03c8e…` equals `git rev-parse 480d73ea^{tree}` (`31e03c8ebd3c37b0e42b658b82775339fa95fb19`) and the comment says so. The tip tree is `71504d98…`; the comment says the later edits are under `docs/ledgers` and `docs/INDEX.md`; the tip differs from the merge by the LG file only (INDEX is unchanged). Accurate, "and INDEX" is surplus.
- Red tally: `grep -E "^E  +\w*(Error|Failed)" exec-a-red2.log | sort | uniq -c` gives 9 `DID NOT RAISE ValidationError`, 5 `AttributeError … monotonicity`, 3 `ValueError: The family must be an instance of … ExponentialDispersionModel`, 2 `ImportError … glum_family`, 1 `unit_deviance() … theta`, 1 `DID NOT RAISE ValueError` = 21; the log's summary is `21 failed, 78 passed, 1 warning in 10.66s`. LG now reads 21 = 9+5+3+2+1+1. Matches.
- Overlay: LG states "an UNCOMMITTED overlay of `b08fbef6`'s two test files on the `fc9107a8` tree, not a commit's tree"; the log's second line reads the same (`HEAD=fc9107a8… + overlay of tests from b08fbef6`). Matches.
- NB-draft count: the SQL is quoted verbatim in "Open observation". Statically valid: `models.spec` is JSONB (`backend/src/app/db/models.py:1683`, class `ModelRow`, `__tablename__ = "models"`) and `GlmSpec.family_params` holds θ (`modelling.py:1121`, `:1196`). It reports 0 NB models and 0 without θ in `gipricing` and `gipricing_fd-1838_gate`, the verdict "deferred with owner WK-1178", and it says it speaks of no other deployment. **The query output is in no file** (`grep -rl nb_without_theta` over scratch and `/tmp` finds nothing but this seat's copy of the LG). The 0|0 is the executor's claim; the maintainer's relay (`17:41:48` item 3) accepts the deferral, so the verdict stands, the evidence does not.
- `Audit` section is "Not yet." — correct for an LG whose auditor has not closed it.

### Anything else in the slice's own delta

None. After `eece638c` the slice adds the merge of main and two LG-only commits. Everything else in `git diff --stat eece638c..afdea774` (25 files) is #1359's (`custom_objectives`, `objective_preview`, `ObjectiveEditorView`, WF-702 and its LG), not the slice's; `git diff --name-only 71e481fa afdea774` lists 16 files, all PL-1856 slice A's (as RS-1862 §1) plus the LG. No scope creep.

## Proposed record

NOT-CLEAN, narrow: B1 and B3 MET; B2 not met on one limb (five of six frontend guard logs and the sixth's guard lines are not reachable); B4 met on content, with the post-merge contract check and the NB count asserted without a log. All three are evidence-persistence, not code or maths. The lead's decision: have the executor write the transcripts to `scratch/sl-8166/` and name them in the LG (then one more look at those paths only), or accept the claims on the gate's full run. No file under `docs/specs/` or code was touched by this seat.
