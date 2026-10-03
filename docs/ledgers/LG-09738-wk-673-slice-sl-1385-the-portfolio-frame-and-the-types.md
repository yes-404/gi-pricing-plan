---
id: LG-9738
family: ledger
title: WK-673 slice SL-1385 — the portfolio frame and the types, spec only (PL-1395, RL-1394)
status: active
created: 2026-10-03
owner: executor
tree: 2411060d81b8821193c5e7239a2423c6a9cf1667
phase: P2
work: WK-673
slice: SL-1385
plans: [PL-1395]
corrected_by: []
relates: [RL-1394, RL-1264, RL-1361, RL-1184, RL-1263, PL-1267, FD-1374]
---

# LG-9738 — WK-673 slice SL-1385, the portfolio frame and the types

Executed from `PL-1395` by `executor-1385` (sonnet; `echo $CLAUDE_EFFORT` printed `medium`). Branch
`sl-1385-portfolio-frame-and-types`. Stamps are BST (`TZ=Europe/London date`). The id `LG-9738` is a working id
allocated by the lead (2026-10-03 21:16:24 BST); the lead mints the final id.

The executor charter's Model / effort line, verbatim: "`sonnet` (currently Sonnet 5); medium, inherited from the
lead — the highest-volume role; per-slice gates and the auditor's re-check bound the risk of a cheaper setting."

## Tasks

### Task 0 — preconditions

**Base.** Worktree branched from `origin/main` `8252741cc3849058b6fc6836967448d88ff9821c` (#1087, SL-1377's merge).
Read at 2026-10-03 22:01:59 BST: `git log origin/main` shows #1087 (`8252741c`), #1092 (`fc5ef5ef`, the PL-1395 and
SL-1385 activation) and #1093 (`16a89b15`, the RL-1263 registry amendment) all merged. Activation need 3 (SL-1377
closed) is met at that head.

**Step 1.** `docs/plans/PL-01395-…` front matter `status: active`; `docs/roadmap.md:715` carries SL-1385's dated
activation line; `docs/rulings/RL-01394-pl-1395-dp-s1-1-to-6-decided-each-pass-sees-only-its-own-contract-purpose-and-date-are-stamped-exposure-years-is-fixed-and-a-change-is-one-step.md` resolves RL-1394.

**Step 2.** `uv sync --all-packages` ran clean.

**Step 3.** The four docs checks on the untouched tree (`8252741c`): `python3 scripts/audit-docs.py` rc 0,
"All checks passed." with `DISCLOSED (848, at or under the W37-11 residue ceiling)`; `python3 scripts/doc-id.py check`
rc 0; `python3 scripts/doc-index.py --check` rc 0 ("OK (byte-stable)"); `python3 scripts/register-lint.py` rc 0
("OK (0 violations)").

**Dispatch record, FINAL, quoted verbatim** (`gi-pricing-plan.local/handover/DISPATCH-WK-673-SL1385-2026-10-03.md`,
read 2026-10-03 at the start of this run):

```text
# Dispatch record: WK-673 Slice 1 (SL-1385), the portfolio frame and the types, from PL-1395 (FINAL)

**Status: FINAL** (2026-10-03 21:17:28 BST, the lead, on "2026-10-03 21:17:03 BST — DISPATCH GO: WK-673 Slice 1 (SL-1385 / PL-1395) on lane B; executor-1385 starts after #1087, #1093 and #1092 have merged"). *Earlier status line, kept:* **Status: DRAFT** (the lead, 2026-10-03 21:10:19 BST). **Lane B** after #1087 (SL-1377) merges, under PL-1371 §5 rule 3 (:298), per "2026-10-03 21:08:01 BST — GO: planner-1385act (WK-673 S1 activation PR: PL-1395 → active, SL-1385's dated line, INDEX); WK-673 S1 takes lane B after #1087 merges, under PL-1371 rule 3 (:298)". PL-1395 is frozen from #1091 (86034259); deltas live here.

## Plan and slice status on main 86034259
- PL-1395 `draft`; SL-1385 `draft`; activation PR by planner-1385act (pending).

## Activation needs (PL-1395 :467-480), RUN at main 86034259
1. The ruling minted: RL-1394 (`active`, #1091) resolves DP-S1-1..8 and adopts T1–T9. **Met.**
2. This plan minted (PL-1395, #1091), its DP table carries RL-1394, SL-1385's relates gains PL-1395 (#1091); `status: active` via the activation PR **#1092** (planner-1385act, head 708345cd; placeholders for the lead). **Met at #1092's merge.**
3. SL-1377 merged (the §5.2 and ONE_SIDED_SLUGS serialisation with SL-1377): **PENDING** (#1087, its minted-head gate running).
4. A free gate slot under RL-1263 in PL-1371's G2 order: at dispatch (lane B after #1087).

## Decision points
- DP-S1-1..6 → RL-1394 (active); DP-S1-7 → RL-1264; DP-S1-8 non-blocking. **RL-1394's maintainer conditions (i)–(iv)** (its :234-244) bind the executor: (i) R exact; (ii) the S label names N orders and keeps "order-dependent"; (iii) the grouping path first; (iv) the reading rests on RL-1184 :199-202, not amended.
- PL-1267 acceptance conditions ("2026-10-03 17:53:43 BST — ACCEPTANCE: PL-1267 …"): 2 (the §4.8 undeclared column; ruled by RL-1394 DP-S1-1 (b)) and 3 (Slices 1–4 first). OQ 9739 (the subset input-contract question) stays with SL-1387, not this slice.

## RL-1263 contention, S1 × WK-674 S2 (re-derived per the 21:08:01 GO condition 2: PL-1392's write set PLUS RL-1379's Delta 1)
RL-1263 (main), quoted: ":89 Two concurrent build slices may not both change the same **existing** function, class, method, spec section, or policy table." ":100 **Any other shared path serialises** unless the lead's dispatch record names the path and the check showing that no existing definition is edited by both." `backend/tests/test_contracts.py` and the two spec files are NOT on the registry list (:90-94 as corrected).

| Shared path | S1 (PL-1395 write set) | S2 (PL-1392 :825ff + RL-1379 T1–T4) | Same existing definition? | Verdict |
|---|---|---|---|---|
| `docs/specs/00-overview.md` | §2.3 rows appended | §3, the FR-4 row (00:209; RL-1379 T1) | no: different sections (§2.3 vs §3) | allowed under :100 (sections named) |
| `docs/specs/03-rating-engine.md` | §3.9 (FR-266 amended + 3 rows appended); §4.6, §4.8; §5.2 (the analysis.py lines); §5.1 none (DP-S1-6 (a)) | §3.4 FR-239 row (03:136; T2); §5.1 owned codes (:845; T3) and compile row (:793; T4); a §5.1 row appended; §3.10 notes; a new §4.12 | no: S1 {§3.9, §4.6, §4.8, §5.2} vs S2 {§3.4, §3.10, §4.12, §5.1} are disjoint | allowed under :100 (sections named) |
| `backend/tests/test_contracts.py` `ONE_SIDED_SLUGS` | one existing entry's value (`"dislocation-run"`, test_contracts.py:87; PL-1395 Task 6 Step 2) | entries ADDED to the same dict (PL-1392 C15) | **yes, read strictly**: `ONE_SIDED_SLUGS` is one existing definition that both change | **allowed by the dated amendment below (key-disjoint: S1 touches only `"dislocation-run"`)** |
| (not shared) | analysis.py (S1 edits nothing in pricing-core `score.py`: PL-1395 :120, DP-S1-8 (a), confirmed by RL-1394), dislocation-run.schema.json, open-questions.md | backend/src/app/api/score.py, rating_versions.py, api/models.py, errors.py, bundle_slot.py, generated contract | — | the two score.py are different files |

## Holds (holds-2026-10-01.md), read 2026-10-03 21:16:24 BST
- FD-1335 /score hold: covers WK-675 slices consuming /score routes; S1 edits no route and nothing in score.py (PL-1395 :120). **Not applicable.**
- FD-1366 per-route hold: S1 calls none of the five routes. **Not applicable.** FD 9752 hold: S1 reads no approval response. **Not applicable.**
- FD-1374 (FR-246 undeclared reads): a finding with its remedy in PL 9776 (F35), not a hold; S1 does not touch the engine's consumes. OQ 9739 stays with SL-1387.

## Conditions
1. **Write set:** PL-1395 "Write set" (03 §3.9, §4.6, §4.8, §5.2; 00 §2.3; docs/contracts/schemas/dislocation-run.schema.json; backend/tests/test_contracts.py ONE_SIDED_SLUGS `"dislocation-run"` value only; analysis.py and its tests; open-questions.md; its ledger; INDEX). Nothing in score.py.
2. **Starts only after #1087 (SL-1377) merges** (PL-1395 §5.2 and its ONE_SIDED_SLUGS serialisation with SL-1377) **and after #1093 (the registry amendment) merges** (the 21:11:06 entry).
3. **Lanes:** lane B; lane A = WK-674 S2 (different Work). Shared non-exempt paths as tabled above: spec sections disjoint (RL-1263 :89/:100, accepted 21:11:06); ONE_SIDED_SLUGS key-disjoint under Delta 1. Whichever of S1/S2 merges second re-merges and re-runs its full gate, including `test_every_one_sided_slug_is_declared`. If their gates overlap, a candidate contention pair: both ledgers record both walls.
4. **RL-1394's conditions (i)–(iv)** bind the executor (above). Spec texts T1–T9 from RL-1394 byte for byte (Task 0 Step 4 copies from the ruling, never from the plan's appendix).
5. **Gate evidence** for every suite-level run: clean detached checkout of the named SHA, porcelain empty; `uv sync --all-packages`; `ruff check --no-cache`; `mypy --no-incremental`; the slot wrapper verbatim + `LOKY_MAX_CPU_COUNT=4`; uptime/free start and end; the other holder via flock -n; the test DB first; the stage table, never the exit code. Slot granted by the lead. migrate --verify only in CI's form.
6. Red first on every acceptance item; frozen records untouched; no claude.ai/code link in any commit or PR body.
7. **Ledger:** LG working id **9738** (allocated by the lead 2026-10-03 21:16:24 BST; free-checked). **Executor:** a fresh `executor-1385`, sonnet, from `.claude/roles/executor.md`, a new worktree from origin/main after #1092, #1087 and #1093 have merged.

## Deltas
- **Delta 1, 2026-10-03 21:14:14 BST (lead): the RL-1263 registry amendment, verbatim**, from "2026-10-03 21:11:06 BST — DATED AMENDMENT to RL-1263's registry list (option (b)): ONE_SIDED_SLUGS in backend/tests/test_contracts.py is exempt for key-disjoint edits; WK-673 S1 may run beside WK-674 S2":

> `backend/tests/test_contracts.py`, the `ONE_SIDED_SLUGS` dict only: a new key appended, or one slice's change to the value of one existing key, provided **no key is added, removed or changed by both** concurrent slices. Each slice's dispatch record names the keys it touches. At the second merge, the later slice runs the RL-1263 second-merge steps (merge main, re-run its full gate), and its gate must include `test_every_one_sided_slug_is_declared` passing. No other part of the file is exempt.

  **Keys this slice touches in `ONE_SIDED_SLUGS`: exactly one, `"dislocation-run"` (its value; test_contracts.py:87; PL-1395 Task 6 Step 2). It adds and removes no key.** The spec-file section disjointness (00 §2.3 vs §3; 03 {§3.9, §4.6, §4.8, §5.2} vs {§3.4, §3.10, §4.12, §5.1}) is ACCEPTED in the same entry. The core.json amendment PR merges before executor-1385 starts.
```

**Step 4. T1 to T9 as RL-1394 adopts them.** The texts are copied programmatically from
`docs/rulings/RL-01394-pl-1395-dp-s1-1-to-6-decided-each-pass-sees-only-its-own-contract-purpose-and-date-are-stamped-exposure-years-is-fixed-and-a-change-is-one-step.md`, section "The exact texts" (T1 at ruling line 346, T2 at
355, T3 at 363, T4 at 372, T5 at
381-395 and 402, T6 at 411,
417-458, 476-535 and
539, T7 at 553-560 and 566, T8 at
577-581, T9 at 589). The commits apply them by script from
those lines, so the committed text is the ruling's text with only `<date>` (2026-10-03), `RL-<n>` (RL-1394) and
`PL-<n>` (PL-1395) substituted. `RW1`, `RW2` and `RW3` stay as the working ids (the lead issues the requirement ids
at the mint). The verification is in Acceptance 2 below; the texts themselves are not repeated here.

## Tasks 1 to 6 — evidence

| Task | Commit | Evidence |
|---|---|---|
| 1 `00` §2.3 | a031eafe | Step 1 grep for the five terms printed nothing before; T8's five rows appended after the `**Dislocation**` row; `audit-docs.py` rc 0 |
| 2 `03` §3.9 | 85d9870e | T1 appended inside FR-266's cell, T2 to T4 as three rows (RW1, RW2, RW3) before `### 3.10`; Acceptance 3 and 4 greps below |
| 3 `03` §4.8 | 4eb810a7 | T5's subsection and its dated note appended; sentence map below |
| 4 `03` §4.6 and the contract | 33b413b2 | T6; agreement check prints `OK`; red-first quote below |
| 5 `03` §5.2 | ce7190be | T7 signatures and types paragraph |
| 6 test label | cdeb0cd0 | T9; one removed, one added line; `test_contracts.py` 150 passed, 2 skipped |

### Task 3 Step 3 — the sentence of T5 that carries each ruled answer

- DP-S1-1 (b): "Every other column passes through the reader ... It never reaches the engine. Each scoring pass ... rates a
  frame of the stamped columns, `quote_id`, and exactly the names in that pass's own bundle's `input_contract`".
- DP-S1-2 (c): "`purpose`, `effective_date` and `rating_version_ref` are stamped, never read from the portfolio."
  with `DislocationSpec.purpose` and `as_at`, and "A `mid_term_adjustment`, `cancellation` or `what_if` row therefore
  cannot occur in a run".
- DP-S1-3 (a): the table row "`exposure_years` | decimal | required, non-null and never negative; zero allowed".
- DP-S1-6 (a), amended: "A portfolio that breaks this schema is refused before any rating, with `VALIDATION_FAILED`"
  and "A fault in one row's algorithm inputs is not a frame refusal: it is that row's own error".

### Task 4 — red first

The agreement check (PL-1395 Task 4 Step 3) was run with the schema path as an argument. On the real schema it
printed `OK`, rc 0. On a scratch copy with `properties.job_id` deleted it printed, rc 1:

```text
example keys not in schema: ['job_id']
schema top-level properties not in example: []
```

The plan names the second line as the one to quote; with a property deleted from the schema the failing line is the
first (the example holds a key the schema lacks), and the second prints empty. The failure is real and exits 1. The
scratch copy was deleted. Also confirmed: `common/money.schema.json` defines `$defs` `Currency`, `Decimal`,
`MoneyMinor` and `Rounding`; the edited contract parses with no duplicate key (`object_pairs_hook` check);
`audit-docs.py` reports "68 JSON schemas parsed, $refs checked".

### Task 6 — the diff, and DP-S1-8

```diff
@@ -89 +89 @@ ONE_SIDED_SLUGS: Final[dict[str, str]] = {
-    "dislocation-run": "later-phase — 03 rating",
+    "dislocation-run": "03 §4.6 — hand-authored until WK-673 Slice 4 generates and compares it (PL-1267)",  # noqa: E501
```

Exactly one line removed and one added; no key added or removed (Delta 1: the one key touched is
`"dislocation-run"`). DP-S1-8 (a): `score.py` not edited; the target of RL-1264's docstring obligation was removed by
SL-1345 (#1045, `1dd5e264`).

### Task 7 — RL-1264's three Slice-1 negative tests (verbatim from PL-1395 Task 7)

| `RL-1264` violation | Test name | File | Built by |
|---|---|---|---|
| a subset bundle persisted as a Rating Version, or visible in a version list | `test_dislocation_subset_bundles_never_become_rating_versions` | `backend/tests/test_dislocation_runs.py` | Slice 4 (`SL-1388`): the Job handler is the only code that could write a row |
| a subset that fails to compile and is skipped instead of failing the run by name | `test_attribute_fails_the_run_naming_a_subset_that_does_not_compile` | `packages/pricing-core/tests/test_rating_attribution.py` | Slice 3 (`SL-1387`) |
| a regrouping that leaves a derived change out, or puts one in two groups, and is accepted | `test_attribute_refuses_groups_that_do_not_partition_the_derived_changes` | `packages/pricing-core/tests/test_rating_attribution.py` | Slice 3 (`SL-1387`); Slice 4 adds the route's 422 |

The PR body asks the lead to carry these rows into the dispatch records of SL-1387 and SL-1388.

## Deviations and disclosures

1. **T9 and ruff E501.** T9's line is 106 columns; the repo's ruff limit is 100, so the byte-for-byte line fails
   `ruff check` (E501). The value is kept identical and the line carries a trailing `# noqa: E501`, which keeps the
   diff one line as Task 6 Step 2 requires. The alternative (a split implicit string) would make the diff two lines.
2. **The entry's line number.** The plan and dispatch record say `test_contracts.py:87`; at `8252741c` the entry is at
   line 89 (the file grew). The edit is to the one entry's value, as ruled.
3. **Working ids.** `RW1`, `RW2`, `RW3` are kept as the requirement working ids; the lead's mint replaces them.
   `audit-docs.py` reports no finding for them. Its one remaining finding on the final tree is check 31, "gap in
   the full allocation between 1396 and 9738": this PR's own working id `LG-9738` (acceptable per PL-1395
   Acceptance 13, named here); the lead's mint clears it.
4. **`docs/INDEX.md` (check 39).** From the Task 2 commit onward `audit-docs.py` reports check 39 (INDEX stale
   against a regeneration) until the INDEX is regenerated; PL-1395 Task 8 Step 4 regenerates it in the last commit
   only, and that commit does so.
5. **T7's types paragraph sits directly after the §5.2 code block**, as the ruling says, which places it before the
   existing "Corrected 2026-09-28, RL-1172" blockquote that follows that block.
6. **`ruff format --check` on `test_contracts.py`** reports the file would be reformatted at lines unrelated to this
   slice; it is the same on `origin/main` (the gate runs `ruff check`, not format). Not touched.

## Acceptance self-check

| # | Evidence |
|---|---|
| 1 | RL-1394 id resolves in PL-1395's Decision points table (activation need 1 met, #1091, #1092) |
| 2 | a script that extracts each fenced block under the ruling's "The exact texts" and tests it, with only the three ids substituted, as a substring of the committed file, run at the committed tree: T1, T2, T3, T4, T5 (frame and note), T6 (note, example, contract members, dependentRequired), T7 (block and types), T8 and T9's value each printed "identical after substituting date/RL/PL ids" (14 of 14), rc 0 |
| 3 | FR-266's row: `grep -c` per phrase printed 1 for each of `exact Shapley`, `largest remainder`, `declared change order`, `plain rounding is forbidden`, `isolated`, `cumulative`, `total − Σ isolated`, `order-dependent`, `FR-273` |
| 4 | `grep -c '^. \*\*RW[123]\*\*' docs/specs/*.md` prints 3 in `03-rating-engine.md` only; the three rows sit between FR-266's row and `### 3.10` |
| 5 | `grep -n '^#### The portfolio frame (WK-673' docs/specs/03-rating-engine.md` prints one line (688), inside §4.8; the "does not design that schema now." sentence carries T5's dated note |
| 6 | the agreement check printed `OK`; red-first quoted above |
| 7 | `grep -n 'def dislocate\|def derive_changes\|def attribute'` prints the three lines T7 adopts and no other; the old `attribute(changes: …)` line is gone from the block |
| 8 | each of the five terms is bold-defined once across `docs/specs/` (`grep -rho '\*\*<term>\*\*' docs/specs/` prints exactly one line for each); `git log -S'**Shapley attribution**' origin/main..HEAD -- docs/specs` lists only `a031eafe`, the first commit |
| 9 | `grep -n '"dislocation-run"' backend/tests/test_contracts.py` prints one line (89) inside `ONE_SIDED_SLUGS`, naming `03 §4.6` and `WK-673`; `pytest backend/tests/test_contracts.py -q` 150 passed, 2 skipped |
| 10 | `git diff --stat origin/main...HEAD -- packages backend frontend ':!backend/tests/test_contracts.py'` prints nothing |
| 11 | `git diff --name-only origin/main...HEAD` lists only the write set: `backend/tests/test_contracts.py`, `docs/contracts/schemas/dislocation-run.schema.json`, `docs/specs/00-overview.md`, `docs/specs/03-rating-engine.md`, plus this ledger and `docs/INDEX.md` in the last commit |
| 12 | Task 7's table above; PR body carries the request |
| 13 | see "Gate" below |
| 14 | see "Gate" below; `req-coverage.py` is expected to list RW1 to RW3 as specified with no test (Slices 3 and 4 build their tests) |
| 15 | the maintainer's MERGE-ACK and the auditor's clean audit: not this ledger's |

## PRs

Draft PR "feat(rating): SL-1385 — the portfolio frame and the types (WK-673 Slice 1, PL-1395, LG 9738)" from branch
`sl-1385-portfolio-frame-and-types`; PR #1094.

## Gate

**Gate of record at `a96f7ce43015966c9d664efa0dc759eb0931d464`** (slot granted by the lead 2026-10-03 22:09:33 BST,
"Both slots free; load 1.18; 27Gi available"). Run in this worktree on a detached HEAD at that SHA, porcelain empty
(0 lines), `uv sync --all-packages` clean, test DB `gipricing_agent-ad47e75a4877e6ae8_06fd4d9a` created from the
template and migrated to head first. The slot wrapper is `.claude/skills/dev-commands`' gate body verbatim, with
`ruff check --no-cache`, `mypy --no-incremental`, `LOKY_MAX_CPU_COUNT=4` (and `RUFF_NO_CACHE`, a scratch
`MYPY_CACHE_DIR`), plus the frontend six run sequentially inside the same slot (it took `gate-1`, `slot_i=1`).
Start 22:10:16 BST: load average 1.14, 1.07, 0.86; `free -g` available 26. End 22:33:24 BST (23 min): load 9.05 (1
minute, the suite's own); available 26. The other holder: `flock -n /tmp/slots/gate-2` probed free **after** the
run (22:33+); it was not probed during the run, so a contention pair with executor-1256 is neither shown nor ruled out.

| stage | result | detail |
|---|---|---|
| ruff | pass | exit=0 |
| mypy | pass | exit=0 |
| import_linter | pass | exit=0 |
| audit_docs | FAIL | exit=1 |
| req_coverage | pass | exit=0 |
| contracts | pass | exit=0 |
| pytest | FAIL | exit=1 |
| fe_install | pass | exit=0 |
| fe_generate | pass | exit=0 |
| fe_lint | pass | exit=0 |
| fe_typecheck | pass | exit=0 |
| fe_test | pass | exit=0 |
| fe_build | pass | exit=0 |

`GATE: FAIL — 2 of 13 stages failed: audit_docs pytest`. pytest: 13 failed, 4611 passed, 3 skipped, 1309 s.

**Reading of the two reds (not a pass).** `audit_docs` reports exactly one finding, check 31, "gap in the full
allocation between 1396 and 9738": this PR's own working id `LG-9738`, named above and allowed by PL-1395
Acceptance 13. All 13 pytest failures are tests that run `audit-docs.py`, `doc-id.py check` or `doc-index.py` on the
real tree and receive that one finding: `test_audit_docs_finding_citations` (1), `test_audit_docs_ids` (2:
`test_the_real_tree_passes_all_ten_checks`, `test_doc_id_check_exits_0_on_the_real_tree` — "[noncontiguous] docs/INDEX.md
has a gap between 1396 and 9738"), `test_audit_docs_process_core_digest` (2), `test_audit_docs_w37_11_ceiling` (1),
`test_doc_index` (1: "the live allocation is not contiguous: [(1396, 9738)]"), `test_register_lint` (3),
`test_register_owed` (1), `test_repository_invariants` (2). The audit's other output line,
the check-36 line about a legacy pre-migration requirement id in the custom-objective workflow, is a disclosed note, not a failure. This is
inference from the failure messages, not a re-run: the proof is a re-run at the lead's minted head, where the working
id is replaced by an allocated one and the gap closes. No test outside those docs-audit tests failed; the
backend, pricing-core, model-schema and frontend suites are green.
