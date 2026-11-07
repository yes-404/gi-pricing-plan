---
id: LG-2070
family: ledger
title: WK-1178 slice SL-2069 — FD-1484, one table-row parser, table_rows.py (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-07   # original date 2026-11-05, working id 8344, minted 2026-11-07
owner: executor
tree: 966f817fa707322b32e6e733e9cc88bc6318511d   # the tree of commit afe1ee99 (sl-8343-table-row-parser, the code head this was written against; base c8d8522758859d23fac5542815ccaa59c5a4b087). Corrected 2026-11-05 17:12 GMT: the field held the commit id.
slice: SL-2069
phase: P2
work: WK-1178
plans: [PL-2068]
corrected_by: []
relates: [FD-1484, PL-2068, PL-2065, LG-2067]
---

# LG-2070 — WK-1178 slice SL-2069: one table-row parser

*(Minted 2026-11-07 as LG-2070 from working id 8344, in the SL-2069 batch (T folded: SL-2066 with SL-2069), with the mint tool of record `mint-repoint.py`. Plans PL-2065 (8330) and PL-2068 (8342), slices SL-2066 (8331) and SL-2069 (8343), ledgers LG-2067 (8332) and LG-2070 (8344) minted together, in that order.)*

**GO:** to-lead "2026-11-05 09:58:58 GMT" (FD-1484 coded and merged before Thu 12 Nov); "2026-11-05 10:36:35 GMT" (all nine plans accepted; DP-P1 (a) row by row; DP-P2 (a) keep `\|` as written; T folded onto this branch and gate).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-2068, "SL-2069 — one row parser". No requirement id: tooling. Register: FD-1484. The slice also carries PL-2065's commits (SL-2066, LG-2067), folded onto this branch and gate by the 10:36:35 entry. The branch is `sl-8343-table-row-parser`; its base is the PL-2068 head `c8d85227`, and the PL-2065 draft head `7b5aa255` was brought in as a merge (`d6481cba`), never a rebase.

### Task list

1. **R1 — red first.** `1618a806`: `packages/model-schema/tests/test_table_rows.py`, T1–T3 (split table, stdlib-only AST walk, bare load by path) plus an `endpoint_row` test. Committed alone, before the module.
2. **R1 — green.** `9501791d`: `packages/model-schema/src/model_schema/table_rows.py`: `split_row` (the placeholder form of `register-lint.py`'s `_split_row`), `cell_count`, `is_table_row`, `endpoint_row`, `UNESCAPED_PIPE`. Stdlib only.
3. **R2.** `e57cc671`: `scope-audit.py`, `audit-docs.py` and `guide.py` read a §5.1 row through `endpoint_row`. The three `([^|]+)` regexes and the comments at `audit-docs.py:295-298` and `guide.py:60-63` are gone. Scripts load the module by path (`scope-audit.py` and `register-lint.py` each once; `_docid.py` once, exposing it as `_docid.table_rows` to `audit-docs.py` and `doc-index.py`). `guide.py` imports it normally.
4. **R3.** `96300754`: `doc-index.py` (`:477` constant and `:1061` split) and `register-lint.py` (`_split_row` and `_UNESCAPED_PIPE` delegate, names kept).
5. **R4.** `c16eb280`: `audit-docs.py` cell splits, check 22's count and offender search, `_docid.py:1611`, `guide.py` `_cells`, and the five test sites (`tests/test_audit_docs_ids.py` ×2, `tests/test_findings_ids.py`, `tests/test_permission_parity.py`, `backend/tests/test_contracts.py`).
6. **T4.** `6f2f583b`: `tests/test_scope_audit_escaped_pipe.py`. **Departure from the brief:** T4 was committed together with the code commits, not alone before them. Its red is proved on base below instead.
7. `afe1ee99`: ruff fixes (two import blocks, two long lines).

### Gate

The full code gate, both halves, SOLO, belongs to the lead and is not run by the executor. Runs by the executor on its own tree, all through `run-heavy.sh --over-load "2026-11-05 13:58:21 GMT"`, one file per call; `df -h /` read 14G free (77%) before the `uv sync --all-packages --frozen` (rc 0).

**Red first, by cause, from base `c8d85227`:**

- `python3 scripts/doc-index.py --phase P2` (bare `env -i PATH=/usr/bin:/bin python3 -I`): `ValueError: findings/register.md: parsed 352 of 362 data row(s) — coverage mismatch (RL-982 acceptance item 2)`.
- `declared_endpoints("DATA")` 39 and `declared_endpoints("GOV")` 23 (A7's base).
- The demo guide's declared-but-unbuilt list, `build_guide(...).unpublished_endpoints` (A2; added 2026-11-05 17:12 GMT on the auditor's catch): **40** at base (GOV 10). `scope-audit.py GOV --endpoints` at base: `published 13 (57%)`, `NOT PUBLISHED — 10`.
- T1–T3, with `table_rows.py` moved aside on the slice tree: `ImportError: cannot import name 'table_rows' from 'model_schema'`.
- T2 with a planted `import pydantic` (not committed): `AssertionError: {'pydantic'}`.
- T4 on base (the test file copied into a detached worktree of `c8d85227`, `/tmp/sl8343/base`): `AssertionError: assert ('GET', '/api/v1/dataset-versions/{}/lineage') in {...}`, `1 failed in 0.30s`.

**Green, at the slice tree:**

- `packages/model-schema/tests/test_table_rows.py`: `12 passed in 3.38s`.
- `tests/test_scope_audit_escaped_pipe.py`: `1 passed in 0.62s`.
- `declared_endpoints("DATA")` 40 and `("GOV")` 25 (A7).
- The demo guide's unbuilt list (A2), re-read 2026-11-05 17:10 GMT at `5748acc7` by `build_guide(...).unpublished_endpoints` through `run-heavy.sh`: **42** (MON 18, GOV 12, OPT 11, PLAT 1); 40 at base, so +2, both in GOV. `scope-audit.py GOV --endpoints` at head: `published 13 (52%)`, `NOT PUBLISHED — 12`. The two added rows are the two routes of A9 below. GOV NOT PUBLISHED 10 → 12 and 57 % → 52 % (13 of 23 → 13 of 25): the published count is unchanged at 13; the instrument now sees two declared routes it could not see, so it is more accurate, not a regression.
- `python3 scripts/doc-index.py --phase P2`: rc 0, the report prints (`11 closed`, `122 planned, 103 delivered`); `register-lint.py`: rc 0, `0 violations`.
- `ruff check .`: `All checks passed!`.
- A5, bare environment: `env -i PATH=/usr/bin:/bin python3 -I` loads `scope-audit.py` (the figures above) and `scripts/scope-audit.py --help` prints; `audit-docs.py`, `doc-index.py` and `register-lint.py` ran under `run-heavy.sh` (inherited environment). *Dated line, 2026-11-05 17:12 GMT, the auditor's A5 finding:* `doc-id.py check` under `-I` fails `No module named '_docid'` at base `c8d85227` too (`-I` drops the script's directory from `sys.path` and `doc-id.py` does `import _docid`, `scripts/doc-id.py:61`); without `-I` it loads. That is a wording fault in the plan's "same for … `doc-id.py check`", not the slice's; the maintainer accepted it as a plan wording, to-lead "2026-11-05 17:08:30 GMT".
- A6: `git grep -n -E '\.split\(.\|.\)|\(\[\^\|\]\+\)|\(\?<!\\\\\)\\\|' -- scripts backend/src packages tests backend/tests` prints only `table_rows.py:20` (`UNESCAPED_PIPE`) and `:36` (`split_row`'s own split). The exception list is empty. *Dated line, 2026-11-05 17:12 GMT, the auditor's A6 correction:* the same predicate also prints `tests/test_scope_audit_escaped_pipe.py:4`, a docstring line naming the old `([^|]+)` capture. It is prose, not a splitter, so the exception list stays empty.

**Tests by import closure (slice tree, `pytest -q <file>`):**

| File | Result |
|---|---|
| test_audit_docs_plan_acceptance_standard | 4 passed |
| test_audit_docs_scan_roots | 1 passed |
| test_audit_docs_check_32_disposition | 5 passed |
| test_scope_audit | 7 passed |
| test_findings_ids | 8 passed |
| test_audit_docs_check_prefixes | 8 passed |
| test_permission_parity | 16 passed |
| test_doc_index | 1 failed, 53 passed |
| test_audit_docs_ids | 6 failed, 112 passed |
| test_audit_docs_w37_11_ceiling | 1 failed, 22 passed |
| test_repository_invariants | 2 failed, 9 passed |
| test_register_lint | 3 failed, 30 passed |
| test_audit_docs_finding_citations | 1 failed, 1 passed |
| test_audit_docs_process_core_digest | 2 failed, 2 passed |

Every one of the 16 failures is the same cause, named by the assert text: `audit-docs.py` exits 1 on check 31 (`gap in the full allocation between 2006 and 8330` and `between 8331 and 8342`) and check 39 (`docs/INDEX.md is stale against a fresh regeneration`), and `test_doc_index` asserts `the live allocation is not contiguous: [(2006, 8330), (8331, 8342)]`. These are the working-id reds the brief allows; they clear at the mint. `test_check_29_wiring_is_undisturbed` (`tests/test_register_owed.py`) is red on base for the same reason. Not yet run (the batch was stopped by the lead's HOLD): test_double_stamp_scan, test_template_headers, test_file_census, test_doc_id, test_doc_id_verify, test_d5_h1_ruling_heading, backend test_demo_guide, test_demo_command, test_contracts.

**`audit-docs.py` at the slice tree (before the INDEX regeneration):** `FAILED (3)`: check 31 ×2 (the working-id gaps above) and check 39. `849` DISCLOSED lines, all residue. Journey citations: `34 endpoints, 8 functions, all declared`. DP-P1: no newly visible route fails a check. ~~A9: none surfaced.~~ **Dated line, 2026-11-05 17:12 GMT, correcting "none surfaced" (the auditor's catch, and the reason for the maintainer's 15:55:11 requirement):** the parser surfaces two routes, `GET /api/v1/dossiers/{id}` (`docs/specs/06-governance.md:610`) and `GET /api/v1/artifacts/{ref}/dependencies` (`06-governance.md:614`), declared in the spec and not built. Ruled DP-P1 (a) for both, to-lead "2026-11-05 17:08:30 GMT": surfaced by the parser, owner WK-680 (P3), `docs/roadmap.md` :3801 (WK-680's row, FR-379, the dossier render) and :3803 (its dated line, FR-384, blast radius) — those are `origin/main`'s line numbers; at this branch's tree the same two lines are :3787 and :3789, no new carry. *Dated 2026-11-07, at the merged head of the mint: the same two lines read :4090 (WK-680's row, FR-379) and :4092 (its dated line, FR-384), under `## P3 — Governance` at :3989.* GOV NOT PUBLISHED 10 → 12 and published 57 % → 52 %: the instrument getting more accurate, not a regression (both counts above). T4's docstring said "three published routes"; two are unpublished, corrected at `tests/test_scope_audit_escaped_pipe.py:5`. The third hidden route, lineage (`01` §5.1), is published (DATA 40 of 40).

### Gate, the lead's SOLO run, the fix and the disclosure comparison (appended at the mint, 2026-11-07)

*(Written by the mint executor from the logs named, read, not recalled. Heads and trees are as of the gate and of the fix, before the merge of `origin/main` and the mint.)*

**The full code gate, both halves, SOLO, gate-1** (`~/gi-pricing-plan.local/scratch/sl8343-gate/gate/gate.log`, START 2026-11-06 09:45:23 GMT, END 2026-11-06 11:45:10 GMT, `rc=1`): head `1208ba28326774a0b1044980207b963a16d9d8fa`, tree `8f6dab4f98ef562f47791ef2688fbb18ad954256`, branch `sl-8343-table-row-parser`, range `origin/main...sl-8343-table-row-parser` (21 paths, `.github/` none). `END rc parts`: `python max=1 fe max=0 demo=0 restore rc_kc=0 role rc_role=0 skip rc_skip=0 infra rc_infra=0 template rc_tg=0 db0 rc_db0=0`.

| Stage | rc | Line |
|---|---|---|
| ruff | 0 | |
| mypy | 1 | `tests/test_audit_docs_ids.py:2451: error: Returning Any from function declared to return "str"  [no-any-return]` and `... "FixtureFunctionDefinition" has no attribute "_docid"  [attr-defined]`, `Found 2 errors in 1 file (checked 255 source files)` |
| import-linter | 0 | |
| audit-docs | 1 | `FAILED (3)`: check 31 gap `2054..8330`, check 31 gap `8332..8342`, check 31 `created:` order line (id 8330, 2026-11-05, earlier than id 2054's 2026-11-06): the working-id class, cleared at the mint |
| req-coverage | 0 | |
| generate-contracts --check | 0 | |
| pytest | 1 | `15 failed, 7324 passed, 27 skipped, 5 xfailed, 153 warnings in 4973.79s (1:22:53)`; skipped 27 equals the 27 baseline |
| pnpm install --frozen-lockfile, generate:api, lint, type-check, test, build | 0 each | `Test Files  138 passed (138)`, `Tests  919 passed (919)`, `Type Errors  no errors` |
| demo `wf-699` | 0 | PASS, 1728 s; dislocation #1 644 s |

The 15 pytest failures, BY NAME (`grep -E '^FAILED' scratch/sl8343-gate/gate/pytest.log`), against item 31's set (the eight docs-audit files, with `audit-docs` failing only on check 31 for this slice's own working ids): all fifteen are in those eight files, none outside them.

  - `tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`
  - `tests/test_audit_docs_ids.py::test_a_disagreeing_register_cell_is_detected`
  - `tests/test_audit_docs_ids.py::test_check_35_owner_tag_and_f92_register_cell_agree`
  - `tests/test_audit_docs_ids.py::test_doc_id_check_exits_0_on_the_real_tree`
  - `tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`
  - `tests/test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`
  - `tests/test_audit_docs_process_core_digest.py::test_the_committed_digest_currently_matches_the_committed_spec`
  - `tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`
  - `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`
  - `tests/test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`
  - `tests/test_register_lint.py::test_check_29_note_carries_the_residue_line`
  - `tests/test_register_lint.py::test_phase1b_residue_count_matches_check_29s_own_count`
  - `tests/test_register_owed.py::test_check_29_wiring_is_undisturbed`
  - `tests/test_repository_invariants.py::test_journey_citations_are_audited_in_ci`
  - `tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`

**The two tests this slice itself caused, and the fix.** Two of the 15, `test_a_disagreeing_register_cell_is_detected` and `test_check_35_owner_tag_and_f92_register_cell_agree`, are not the working-id class: they fail at `tests/test_audit_docs_ids.py:2451` with `AttributeError`, and `mypy` reds at the same line. Cause: `_f92_work_item_cell` is a module-level helper in a test file whose fixture is also named `audit`, so `audit` there named the pytest fixture function, not the module; `audit._docid.UNESCAPED_PIPE` read an attribute of a `FixtureFunctionDefinition`. Fix, `723e5fca8912d912808942ba3b3e494ede50aedb` (tree `8570b813c8d6162f7b1107df311c38a999343603`), two lines in `tests/test_audit_docs_ids.py`: the import `from model_schema.table_rows import UNESCAPED_PIPE` (the module `_docid.table_rows` loads by path, FD-1484) and its use at `:2451`. Red at `1208ba28` (`scratch/sl8343-fix/red.log`, `rc=1`): `2 failed, 116 deselected in 0.55s`, both at `:2451`. Green at `723e5fca`: the same two tests pass in the eight-file run below. `uv run mypy` at `723e5fca`: `Success: no issues found in 255 source files`, `rc=0` (`scratch/sl8343-fix/mypy.log`); `uv run ruff check .`: `All checks passed!`, `rc=0`. The eight docs-audit files at `723e5fca`, three runs (`scratch/sl8343-fix/docsfull-1.log` to `-3.log`, each with `head=723e5fca8912d912808942ba3b3e494ede50aedb` first): 13 failures in all, every one in the gate's 15 above by name, none new, and the two fixed tests absent: the gate's 15 minus those two is 13. This is item 31: the failures stand for the code, and the mint clears the working-id class (audit-docs rc 0 at the minted head, the eight files re-run on it, below). The gate's demo (PASS, 1728 s) and frontend readings from the 11:45:10 END stand as ruled by the maintainer (to-lead "2026-11-06 11:13:42 GMT"); the change after the gate head is a test helper only (two lines), so no full re-gate (the ruling's 14th form).

**D7.** The demo's D7 line at this gate, `D7 | ok  19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units (full-book attribution cost: FD-1576)`, is equal to the same line in every other gate log that carries one under `scratch/` (26 lines in all, `grep -h "| D7 " scratch/*/gate/gate.log`, one distinct value): D7's total and both attribution limbs equal on the 19985-policy sample.

**Item 42 (a merged slice's `SL-` row and LG do not stay `active`).** Found at `origin/main` `3c3ee5cb`: no `SL-` row for either slice exists in `docs/roadmap.md` (the plans said the mint adds them), and the two ledgers sit in this branch only. The mint commit added `SL-2066` and `SL-2069` as `active`; the audit commit that carries this section sets both `SL-` rows and both LGs (`LG-2067`, `LG-2070`) to `closed`, with dated lines, so no row reads `active` after the merge.

**The disclosure comparison (the maintainer's four owed items, to-lead "2026-11-06 09:57:47 GMT", accepted "2026-11-06 10:05:16 GMT"), whole in substance.** The comparison file is `scratch/sl8343-gate/disclosure-compare.txt`, run by exec-gated during the gate's pytest, DB-free and read-only. Its readings, in the order of the four items: (1) `scope-audit.py <module> --endpoints` for all eight modules, base scripts against HEAD scripts on base docs: DATA +1 (`GET /api/v1/dataset-versions/{}/lineage`, T4's route, declared 39 to 40, published 39 to 40), GOV +2 (`GET /api/v1/artifacts/{}/dependencies` and `GET /api/v1/dossiers/{}`, declared 23 to 25, published 13 unchanged, 57 % to 52 %, NOT PUBLISHED 10 to 12, declared in `06-governance.md`, not built; DP-P1 ruled (a) for both, owner WK-680, by the maintainer's entry to-lead "2026-11-05 17:08:30 GMT"), the other six modules 0 differing lines, `--catalogue` for DATA identical; (2) the failing control, on a throwaway copy with `split_row` broken, BOTH breaks recorded (the last cell dropped; the escaped pipe unprotected): `audit-docs.py` rc 1, 676 differing lines against 882 (`DISCLOSED (849` becomes `FAILED (1515)`), and `scope-audit.py --endpoints` DATA 40 to 39 and GOV 25 to 23, so the compare differs on both audit-docs and scope-audit when the splitter is broken, and the first control, which moved only audit-docs, is why both are recorded; (3) `DISCLOSED 849 = 849`: the `DISCLOSED (N,` header and the count of its `  - ` lines agree at base, at HEAD scripts on base docs, and at the gated tree, delta 0; (4) `register-owed.py review`: base **34 owed / 11 excluded**, HEAD scripts and gated tree **14 owed / 1 excluded**, the ruled tree `5748acc7` reads **11 owed / 1 excluded**; the 20 rows that leave the owed list, the 10 that leave the excluded section and the 3 by which 14 exceeds the ruled 11 are each named, with why, in the text below (the 20: `§14` occurs only after the superseded-opening marker; the 10: the same, and they opened with a resolution marker; the 3: `§14` in the live text, rows that exist in the register at the base and not at the ruled tree). The file, repointed to the minted ids and otherwise verbatim:

~~~~text
DISCLOSURE COMPARISON for LG-2070's gate line (exec-gated, 2026-11-06, run during LAST-2's pytest, DB-free, read-only; PYTHONDONTWRITEBYTECODE=1)
Gate: scratch/sl8343-gate/gate (pytest START 2026-11-06T09:49:14Z). Head under test: 1208ba28326774a0b1044980207b963a16d9d8fa (tree 8f6dab4f98ef). Base: 9852f004 (tools-main was at 9852f004, clean, when the base run was made at ~09:52Z; it has since followed origin/main to 9b18810a, so the other base runs below use `git archive 9852f004`).

1. audit-docs.py, the four combinations (outputs in /tmp/disc_*.txt):
   A base scripts, base docs (tools-main @9852f004): rc 0, 882 lines, "All checks passed."
   B HEAD scripts, base docs (git archive 9852f004 + HEAD's scripts/ + table_rows.py, tmp git index): rc 0, 882 lines. diff A vs B: 0 differing lines.
   C HEAD scripts, HEAD docs (the gated tree): rc 1, 885 lines.
   D base scripts, HEAD docs (git archive HEAD + base's scripts/): rc 1, 885 lines. diff C vs D: 0 differing lines.
   => the parser change moves NO line of the audit output on either corpus. Every difference between A and C is the corpus: the 4 documents the branch adds (PL-2065, LG-2067, PL-2068, LG-2070).
   A vs C line differences, all counts: check 30 1169->1173 docs; 31 1088->1092 ids; 32 1233->1237 files, 2055->2061 indexed ids; 33 1169->1173 headers; 34 936->938 frozen-family files; 35 1125->1129 owners; 36 8410->8419 legacy-form hits = 497 fatal + 7913 disclosed -> 497 fatal + 7922 disclosed (+9 disclosed, fatal unchanged); 37 1169->1173 docs, shape-checked 797->801; 38 319->321 PL/RS/RFC docs; 39 2243->2247 records; 25 745->749 files scanned; 28 154->156 plans checked. NO count falls. The +9 disclosed legacy-form hits belong to the added documents: B (HEAD parser, base docs) reads 7913, same as A; D (base parser, HEAD docs) reads 7922, same as C.
   C's tail: FAILED (3): check 31 gap 2054..8330; check 31 gap 8332..8342; check 31 `created:` order line (id 8330 2026-11-05 < id 2054 2026-11-06). Working-id class, as for the earlier gates.
   Per-check line tally (header counts): identical in A, B, C, D.
   "849": no figure 849 appears in any of the four outputs; the figures I could recount are check 36's parts above (8410 = 497 + 7913; 8419 = 497 + 7922).

2. doc-index.py: `--check` on B's tree (HEAD parser, base docs): "OK (byte-stable)": the HEAD parser regenerates the base INDEX.md byte for byte. On the gated tree: "OK (byte-stable)". Record counts from audit check 39: 2243 (base) and 2247 (HEAD): +4 = the 4 added documents. IDs only in the HEAD index vs the base index: LG-2067, LG-2070, PL-2065, PL-2068.

3. scope-audit.py by module (DATA MODEL RATE OPT MON GOV PLAT OVR), three trees: base scripts on base docs; HEAD scripts on base docs; HEAD scripts on HEAD docs. Every module: 0 differing lines between base and HEAD-scripts-on-base-docs, and 0 differing lines between base and the HEAD tree. Line counts per module: DATA 23, MODEL 33, RATE 28, OPT 53, MON 63, GOV 42, PLAT 38, OVR 30. All rc 1 in all three trees (an existing property).

VERDICT of the comparison: no output differs except the corpus-driven counts, none falls, no row is dropped or newly read; a named-row list is empty because there is no changed row.

=== ADDENDUM 2026-11-06 (exec-gated), the four owed items of to-lead "2026-11-06 09:57:47 GMT" and the additions; DB-free, read-only, before LAST-2's frontend stages. The first section's scope-audit comparison ran WITHOUT --endpoints, where the parser's effect lives; this addendum supersedes its "no row newly read" for scope-audit. Trees: A = base scripts on base docs (git archive 9852f004); B = HEAD scripts on BASE docs (the parser's effect on the same corpus); C = the gated tree 1208ba28. (tmp trees are git-init'ed copies, committed so register-owed accepts them; the real sl-8343 stayed at 0 changed paths.)

(1) scope-audit.py <M> --endpoints, all eight modules (DATA MODEL RATE OPT MON GOV PLAT OVR), A vs B and A vs C:
    MODEL, RATE, OPT, MON, PLAT, OVR: 0 differing lines in both comparisons.
    DATA: declared 39 -> 40, published 39 -> 40 (100%); the added row: GET /api/v1/dataset-versions/{}/lineage (T4's lineage route; its path cell carries an escaped pipe).
    GOV: declared 23 -> 25, published 13 -> 13 (57% -> 52%), NOT PUBLISHED 10 -> 12; the added rows: GET /api/v1/artifacts/{}/dependencies and GET /api/v1/dossiers/{} (declared in 06-governance.md, not built).
    Named by calling declared_endpoints() in A and B: the only differences in any module are those three rows (only in HEAD's parser; nothing only in base's).
    --catalogue: DATA --catalogue VR (the only catalogue prefix the tool is given here): A, B and C identical, 31 lines, 0 differing lines, rc 1 in all (as before).
    Expected by the lead: GOV's two and T4's lineage route if DATA moves: exactly these; nothing else moved.

(2) FAILING CONTROL (a plant on a THROWAWAY copy of B, /tmp/disc_ctl.*, never sl-8343): two breaks in packages/model-schema/src/model_schema/table_rows.py: split_row drops the last cell of every row, and the escaped pipe is no longer protected (the placeholder line removed).
    audit-docs.py on the control: rc 1, 1546 lines against B's 882; 676 differing lines; e.g. "177 of 177 §10 mirror rows carry their register status" -> "62 of 177", "check 29: register grammar - 0 violation(s)" -> "374 violation(s)", "DISCLOSED (849, ...)" -> "FAILED (1515):".
    scope-audit.py --endpoints on the control: DATA declared 40 -> 39 (missing: GET /api/v1/dataset-versions/{}/lineage); GOV declared 25 -> 23, NOT PUBLISHED 12 -> 10 (missing: GET /api/v1/artifacts/{}/dependencies and GET /api/v1/dossiers/{}). So the compare differs on BOTH instruments when the splitter is broken, and the unbroken compare differs only on the named rows. A first control with only the drop-last-cell break moved audit-docs but NOT scope-audit (scope-audit reads only a row's first two cells): which is why the second break was added; that first result is kept here as a finding about the instrument.

(3) DISCLOSED count. Predicate (LG-2070:83's): the figure in audit-docs.py's own header line `DISCLOSED (N, at or under the W37-11 residue ceiling):`, checked by counting the `  - ` lines under that header (awk '/^DISCLOSED/{p=1;next} p&&/^  - /{c++}' ). Result: A header 849 (849 lines); B header 849 (849); C header 849 (852 indented lines: the 849 plus the 3 lines of the FAILED (3) section that follows); D (base scripts on HEAD docs) 849. Delta = 0, so there is nothing to reconcile to named rows; the 849 are the same set at base and at HEAD, and the 3 extra indented lines at HEAD are the check-31 FAILED lines (gap 2054..8330, gap 8332..8342, `created:` order for id 8330).

(4) register-owed.py review (the tool refused my uncommitted tmp trees under RL-912, so the tmp trees were committed first):
    A (base scripts, base docs): 34 owed row(s), 11 matched but excluded as opening with a resolution marker.
    B (HEAD scripts, base docs): 14 owed row(s), 1 excluded. C (gated tree): 14 owed row(s), 1 excluded; B's 14 items equal C's 14 (0 differing); no row appears in B that is not in A.
    The delta A -> B is -20 owed rows (34 -> 14; the lead's "31 -> 11" is also -20; my base count is 34 and not 31, and my excluded count falls 11 -> 1). The 20 rows A reads and the HEAD reader does not, by title: 1 "03 rating shapes vs hand-authored contracts (F27)"; 2 "A filed ruling that omits the `## Ruling N` heading migrates as PL-, owner: planner, and nothing catches it (F96)"; 3 "A guard disarmed by the very event it was written to survive (F101)"; 4 "A session ends leaving the shared checkout in a state its successor cannot fast-forward, and nothing announces it (F97)"; 5 "Check 37 reds on 95 of 95 post-migration rulings ... cannot see a ###-level heading (F90)"; 6 "Error codes across the spec/code boundary (F29)"; 7 "FR-240 (F-W9-3)"; 8 "Five test fixtures are written into the real docs/plans/ ... (F89)"; 9 "Four frozen plans state row (d)'s criterion in a superseded form (F114)"; 10 "NFR-499 rate limits (F48)"; 11 "RFC-840/841 adoption pilot (F28)"; 12 "RFC-937 §1.5 requires the vendored manifest to carry vendored: true + origin: ... (title cut at 150 chars in my list)"; 13 "RL-909's decay rule has no faithful check ... (F86)"; 14 "Roster publishing emits a constant (F31)"; 15 "The 'never end your turn with outstanding background work' rule lives in one of seven role charters ... (title cut)"; 16 "The plan's ruling-heading census uses a looser predicate than the shipped splitter ... (F94)"; 17 "Two freeze-clause breaches on PL-1070 ... (F113)"; 18 ".claude/roles/reporter.md's Mechanism section describes a single-signal lead-staleness nudge ... (F74)"; 19 "register-owed.py WK-671 finds 10 open rows the closure record's owed-list sections never name ... (F63)"; 20 "mypy files coverage (F33)". These are rows that named the §14 review only in a superseded opening kept below the live text; the slice's FD-1916 change reads the live text only. Titles 12 and 15 are cut in my extraction; full text in /tmp/ro_A.txt (A) and /tmp/ro_B.txt (B) (tmp files).

=== ADDENDUM 2 2026-11-06 (exec-gated), register-owed review: (a)(b)(c) named with full titles, per to-lead 2026-11-06 10:05:16 GMT. Method: the review's own output on three trees, plus each row read from docs/findings/register.md at 9852f004 (columns: Finding id/title | Concerns | Work item | Phase | Decision). Both breaks of the failing control stay recorded in item (2) above.
Counts: ruled tree 5748acc7 (the plan head the maintainer read; its own scripts): 11 owed rows, 1 excluded. Base 9852f004 with base scripts (A): 34 owed, 11 excluded. HEAD scripts on the base docs (B) and the gated tree (C): 14 owed, 1 excluded. B's excluded section equals the ruled tree's (the sub-graph-mounts row). Of B's 14, 11 are the ruled 11 and 3 are not (c). A's 34 = B's 14 + the 20 of (a); A's 11 excluded = B's 1 + the 10 of (b).

(a) THE 20 OWED ROWS THAT LEAVE (in A's owed list, not in B's). Why, for all 20: the row's Decision cell carries the superseded-opening marker ("supersedes ... opening kept below"), '§14' occurs only AFTER the marker (in the superseded opening) and NOT before it (the live text); the base reader searched the whole cell, the HEAD reader reads the live text only (FD-1916), so they no longer match the §14 review. Each row is present in the register at the ruled tree.
  1. 03 rating shapes vs hand-authored contracts (F27)  [work item: WK-671 Slice 1]
  2. A filed ruling that omits the `## Ruling N` heading migrates as `PL-`, `owner: planner`, and nothing catches it (F96)  [work item: W37-6]
  3. A guard disarmed by the very event it was written to survive (F101)  [work item: W37-6]
  4. A session ends leaving the shared checkout in a state its successor cannot fast-forward, and nothing announces it (F97)  [work item: W37-6]
  5. Check 37 reds on 95 of 95 post-migration rulings, including ones written to comply — its detector cannot see a `###`-level heading (F90)  [work item: W37-6]
  6. Error codes across the spec/code boundary (F29)  [work item: WK-671 Slice 1]
  7. FR-240 (F-W9-3)  [work item: W9-3]
  8. Five test fixtures are written into the real `docs/plans/`, so one run's fixture reds another run's gate (F89)  [work item: —]
  9. Four frozen plans state row (d)'s criterion in a superseded form (F114)  [work item: W37-7]
  10. NFR-499 rate limits (F48)  [work item: WK-671 Slice 2]
  11. RFC-840/841 adoption pilot (F28)  [work item: `nt-0010-0011-adoption` §15 step 6]
  12. RFC-937 §1.5 requires the vendored manifest to carry `vendored: true` + `origin:`; the maintainer's 2026-09-02 exemption ruling exempts it, and neither document names the other (F93)  [work item: —]
  13. RL-909's decay rule has no faithful check, the wrong population, and a backstop that cannot express the shape it exists for (F86)  [work item: —]
  14. Roster publishing emits a constant (F31)  [work item: WK-671 restart cleanup]
  15. The "never end your turn with outstanding background work" rule lives in one of seven role charters (`executor.md`) and the one skill it alone cites; the other five spawned roles have no version of it, including this one (F75)  [work item: —]
  16. The plan's ruling-heading census uses a looser predicate than the shipped splitter, and the two candidate predicates diverge at `32fc63c` (F94)  [work item: —]
  17. Two freeze-clause breaches on `PL-1070`, and nothing catches a spawn against a `draft` plan (F113)  [work item: W37-7]
  18. `.claude/roles/reporter.md`'s Mechanism section describes a single-signal lead-staleness nudge; the shipped detector is a three-signal conjunction (F74)  [work item: —]
  19. `register-owed.py WK-671` finds 10 open rows the closure record's owed-list sections never name — possible F41 recurrence at scale (F63)  [work item: —]
  20. mypy files coverage (F33)  [work item: WK-671 Task 1.3 audit]

(b) THE 10 THAT LEAVE THE EXCLUDED SECTION (in A's "excluded as opening with a resolution marker" list, not in B's). Why, for all 10: the Decision cell opens with a resolution marker ("Resolved <date> ...") and carries the superseded-opening marker, with '§14' only in the superseded opening; the base reader matched them on §14 and then excluded them as resolved openings; the HEAD reader no longer matches them at all, so they appear in neither the owed list nor the excluded list.
  1. 53 files are deferred out of §4 step 5's Reference stamp set, and the deferral lives only in a squash-commit body (F92)  [work item: W37-11]
  2. A failed API-key authentication writes its audit row and then raises inside the unit of work that discards it: `require_caller` wraps `authenticate_api_key` in `database.unit_of_work()` (`deps.py:240-242`), the failure audit is flushed (`service.py:85-110`, `audit.py:139-142`) and the raise rolls it back (`session.py:69-78`), so a revoked, expired, archived-account or environment-denied key leaves NO `audit_events` row (three HTTP runs at `8eaf6d5f`: 401 each, rows 0 → 0, table 576 → 576) and FR-392's "failed authentication … audited" is unmet; the only other record is one `4xx` tick of `gip_http_requests_total` (status is `status_code // 100`, `metrics.py:121`; no 401 series, no auth-failure counter), and a malformed or unknown key (no workspace) gets a WARNING log line only (`service.py:96`). `test_auth_keys.py:205-212` is green by construction: `pytest.raises` sits inside the `unit_of_work`, so the exception is swallowed and the transaction commits, unlike production. FR-392 cites `06` FR-368, which names no failed authentication (FD-1727)  [work item: WK-1178]
  3. Artifact B has no live writer; the watcher charter's "each cycle" claim does not hold (F58)  [work item: —]
  4. C2's `PreToolUse` layer is bypassable exactly as C3's dissolved git hook was, and unlike C3 it has no CI-equivalent backstop (F61)  [work item: RFC-895 adoption slice G]
  5. Discovery does not reach two populations §5.2 routes: one aborts every real run, one is silent (F88)  [work item: W37-6]
  6. FR-242's drafted change summary pairs rate-table pins by slug alone: `_pins_by_slug` (`rating_versions.py:1404-1408`, `{ref.slug: ref for ref in …rate_tables}`) keeps the last ref per slug, so with two pinned versions of one slug (valid under RL-1538) `draft_change_summary_for` (`:1377-1378`) silently drops one table's change or reports a false from/to pair, such as "X 1→2" while X@1 is still pinned (FD-1679)  [work item: WK-673]
  7. Ten artifact tables declared immutable (`03` R1 `:41`, FR-229 `:122`) can be UPDATEd, DELETEd and TRUNCATEd in place by the owner: `rate_tables`, `rate_table_versions`, `rate_table_cells`, `rating_algorithms`, `sub_graph_versions`, `regression_suites`, `regression_suite_versions`, `reference_tables`, `reference_table_versions`, `reference_rows` carry no row trigger, no TRUNCATE trigger, no `gip_app` grant and no `APPEND_ONLY_TABLES` entry (`test_artifact_immutability.py:38-52`, thirteen names); owner `UPDATE` and `DELETE` succeeded on nine of them and `TRUNCATE` on eight (`regression_suites` refused by a foreign key only; `reference_tables` was not exercised, catalog only), so an approved Rating Version's cells and algorithm change with no new version; FR-44's grants-derived test (`test_artifact_immutability.py:~420-439`) is blind to a table with no `gip_app` grant (FD-1728)  [work item: WK-1178]
  8. The RFC-895 runtime-state writer has not run since 02:03Z, and `written_at` cannot say so (F91)  [work item: —]
  9. The freMTPL2 demo has no real rating algorithm, and Slice 3's demo fixture does not satisfy G2 (FD-1209)  [work item: WK-672]
  10. Widening `_ID_SCOPE_ROOTS` reaches no non-markdown file, so 62 of the 65 F83-exempt files stay invisible to checks 30-39 (F87)  [work item: W37-6]

(c) THE 3 BY WHICH 14 EXCEEDS THE RULED 11 (in B's owed list, not in the ruled tree's). Why: all three have '§14' in the LIVE text of the Decision cell (no superseded-opening marker), so the HEAD reader correctly keeps them owed; the ruling's 11 predates them:
  1. A rate-table value whose `Decimal` text is in exponent form (a magnitude under 1e-6, e.g. `'1.36E-7'`) is written and accepted at save and compile, then rejected by the ZEN engine at scoring, and the refusal is reported as `RATE_TABLE_MISS` (FD-1648)  [work item: WK-1178; row present at the ruled tree, but its Decision cell was 558 characters without '§14' there; at 9852f004 it is 5068 characters and now reads "... FD-2028 (no stated dp or rounding policy for a rate cell; arithmetic runs at the ambient context; OQ and the Mon 16 Nov §14 review, the user's to accept) ...", so it joined the owed list after the ruling]
  2. The bulk rate-table operations run at the ambient 28 digits and no spec clause states a decimal-places or rounding policy for a rate cell (FD-2028)  [work item: WK-1178; row ABSENT at the ruled tree (FD-2028, filed after the 15:55:11 read); Decision "deferred with an owner: WK-1178; ..." with '§14' in its live text]
  3. `virtio_balloon` cycling on an e2 machine reclaims 9 to 13 GB of guest memory on an 11-minute cycle, so timed readings carry an unmeasured stall (FD-2033)  [work item: WK-1178; row ABSENT at the ruled tree (FD-2033, filed after it); Decision "deferred with an owner: WK-1178; goes to the §14 ..."]
Reconciliation: A 34 -> B 14 is -20 = (a); the ruled 31 -> 11 was also -20; the base is 3 higher than the ruled one (34 vs 31) and the head is 3 higher (14 vs 11) for the same three rows of (c), which exist in 9852f004's register and not at the ruled tree. No row of the ruled 11 left; no row of B is outside (ruled 11 + (c)).
~~~~

### Audit

~~(To be written by the auditor.)~~

*(Written 2026-11-05 17:06 GMT by aud-sl8343 (sonnet, 5.5), adopted by the lead in from-lead "2026-11-05 17:08:05 GMT" ("aud-sl8343 FINAL ADOPTED"), committed 2026-11-07 in this slice's audit commit, as the slice audit of SL-2069, proposed to the lead, whose verdict it is. Scope derived from PL-2068 first (its Acceptance Standard items 1–2 and A1–A11, its Goal, the FD-1484 essay's *Acceptance*), then evidenced. Object: a detached worktree of the auditor's at `5748acc7` (tree `861047d3`), range `origin/main...5748acc7` (merge-base `dae9637e`; `origin/main` has since moved to `bdad1322`, a docs-only move whose one overlap with the slice is `docs/INDEX.md`). Base for every "base" figure: `c8d85227`, a second detached worktree of the auditor's. Every claim below was run by the auditor on those trees, not copied from the build log; logs and heads in `~/gi-pricing-plan.local/scratch/aud-sl8343/`.)*

**The parser, the point of the slice.** `doc-index._parse_register(docs/findings/register.md)`: base `c8d85227` **parsed 352 of 362**; head `5748acc7` **parsed 362 of 362**. `python3 scripts/doc-index.py --phase P2`: base rc 1, `ValueError: findings/register.md: parsed 352 of 362 data row(s) — coverage mismatch (RL-982 acceptance item 2)`; head rc 0, the report prints (`11 closed`, `122 planned, 103 delivered`), the coverage assertion intact. The plan's "352 of 362" holds exactly.

**Scope and verdicts, PL-2068 (A-item by A-item).**

| Item | Verdict | Evidence (auditor-run) |
|---|---|---|
| Plan 1 (plan passes the docs checks) | MET | `audit-docs.py` at `5748acc7`: `FAILED (2)`, both check 31 gaps on working ids (`2006` to `8330`, `8332` to `8342`); nothing else. After the mint it must exit 0 (OWED-TO-GATE, the mint). |
| Plan 2 (no requirement range) | MET | the plan's grep prints nothing on PL-2068 and PL-2065. |
| A1 write set | MET | `git diff --name-only origin/main...5748acc7`: 15 non-docs files, all in the Write sets of PL-2068 and PL-2065; `.github/` count 0; docs files are the two plans, two LGs and `INDEX.md`. 21 commits; 0 `Claude-Session` strings. |
| A2 red first, by cause | **NOT MET (one limb)** | Reproduced: 352 of 362; `declared_endpoints` DATA 39, GOV 23 at base; T4 red at base (copied into the base worktree: `assert ('GET', '/api/v1/dataset-versions/{}/lineage') in {...}`, `1 failed`); T1–T3 red by the module's absence (`ImportError`). **Missing from the LG: the demo guide's declared count.** Auditor figure: `build_guide(...).unpublished_endpoints` base 40, head 42 (GOV 10 to 12). To be added to the LG's *Red first* list. |
| A3 the parser | MET | `packages/model-schema/tests/test_table_rows.py` T1 is eight rows (escaped pipe in first, middle and last cell, a trailing `\|`, a code span, an empty cell, no trailing pipe): `12 passed in 1.64s` at `5748acc7`. |
| A4 stdlib only | MET | The AST test passes; with `import pydantic` planted in `table_rows.py` (auditor-run, uncommitted, reverted, tree clean) it fails: `Extra items in the left set: 'pydantic'`, `1 failed`. |
| A5 the bare gate | MET (by the auditor's run; the LG's evidence was thin) | The LG ran only `scope-audit.py` bare; `audit-docs`, `doc-index` and `register-lint` ran in the inherited environment. Auditor, `env -i PATH=/usr/bin:/bin /usr/bin/python3 -I`: `audit-docs.py` reaches its checks, 0 `ModuleNotFoundError`, rc 1 on the two check-31 working-id lines only; `doc-index.py --check` rc 0 (`byte-stable`); `scope-audit.py DATA --endpoints`, `register-lint.py` (0 violations), `register-owed.py review` run, 0 `ModuleNotFoundError`. **Exception, not the slice's:** `doc-id.py check` under `-I` fails `No module named '_docid'` at base `c8d85227` too (`-I` drops the script's directory from `sys.path`, and `doc-id.py` does `import _docid`); without `-I` it loads and fails only on the working-id gaps. The plan's "Same for … `doc-id.py check`" cannot be met with `-I`; process note, not an FD. |
| A6 one logic | MET, with an LG correction | `git grep -n -E '\.split\(.\|.\)\|\(\[\^\|\]\+\)\|\(\?<!\\\\\)\\\|' -- scripts backend/src packages tests backend/tests` prints `table_rows.py:20` and `:36` **and** `tests/test_scope_audit_escaped_pipe.py:4` (a docstring naming the old `([^\|]+)`). The LG says it prints only the first two: correct the sentence to name the third and why (prose). `register-lint.py`'s `_split_row` delegates, name kept; `doc-id.py:3202` calls `register_lint._split_row` and is unaffected (same name, same output). Wider idioms outside the predicate (`doc-index.py:461` `[^\|]*` in a requirement-row regex, `doc-id.py:2920` a tail strip, `graphify-docs-extract.py:41`) are not row splitters. |
| A7 the figures | MET | `declared_endpoints` DATA **40**, GOV **25**; `scope-audit.py GOV --endpoints`: published 13 of 25 (was 13 of 23); `doc-index.py --phase P2` rc 0, 362 of 362; `docs/closures/` untouched (`CR-718` not edited); the other six modules' `scope-audit --endpoints` outputs byte-identical to base. The guide's unpublished list 40 to 42 (see A2). |
| A8 nothing else moved | MET | `docs/INDEX.md` diff is four rows, `PL-2065`, `LG-2067`, `PL-2068`, `LG-2070`; `register-lint.py` prints the same `0 violations` at base and head; `register-owed.py review` at `6f2f583b` (the last SL-2069 code commit, before SL-2066's) prints rows identical to base (diff: the generated-against line only). `register-owed.py review` at the folded head differs by design (SL-2066): see LG-2067. Disclosure comparison (LAST-2's gate row, brief amendment 15:55:26): `audit-docs.py` full output base against head, `DISCLOSED (849, …)` block **byte-identical**; the only differing lines are the population counts of checks 25, 28, 30–39 (+3 or +4 governed documents, the slice's own), check 36's disclosed legacy-form hits 7908 to 7917 (+9, all in the four new records' prose), and the check-31 line. No disclosed count fell. |
| A9 the surfaced routes | **NOT MET** | The LG says "no newly visible route fails a check, so nothing is stopped (A9: none)". Two do surface: `GET /api/v1/dossiers/{id}` (`06-governance.md:610`) and `GET /api/v1/artifacts/{ref}/dependencies` (`:614`) are now declared and **unbuilt**: `scope-audit.py GOV --endpoints` `NOT PUBLISHED — 12` (was 10), `published 13 (52%)` (was 57%); the demo guide lists them. No enforced check turns red on them (`scope-audit` exits 1 at base and head for the pre-existing unevidenced requirements; `audit-docs` has no published-axis check), so DP-P1's stop is the lead's to read. The plan's own Evidence predicted them ("`dossiers` and `dependencies` unpublished"). **Proposal: the lead rules the two rows under DP-P1 (a), row by row** (accept as the finding working, a dated line, no spec change; the demo guide and `scope-audit` now say truthfully that they are declared and not built); the LG records the ruling. The third hidden route, lineage (`01:878`), is published: DATA 40 of 40. |
| A10 GREEN set and the gate | **OWED-TO-GATE** | Import closure over the changed modules (`table_rows.py`, `_docid.py`, `audit-docs.py`, `doc-index.py`, `scope-audit.py`, `register-lint.py`, `register-owed.py`, `guide.py`, `test_contracts.py`) by path loaders: more than 15 test files. The LG's table names 14 run and 9 not run; the auditor's text-grep over `tests/`, `backend/tests/` and `packages/*/tests` found 56 files, of which the genuine loaders add `test_doc_id_migrate`, `test_long_path_literal_concatenation`, `test_notes_move_citations` (they load `_docid.py`, now path-coupled to `packages/model-schema/`) to the LG's 23. Not looped. The SOLO gate is the decisive green. Auditor-run: `ruff check .` rc 0 (`All checks passed!`) at `5748acc7`; `mypy` on `table_rows.py` and `guide.py` rc 0; `test_table_rows.py` 12 passed; `test_scope_audit_escaped_pipe.py` 1 passed (base: 1 failed); `test_register_owed.py` 15 passed, 1 failed (`test_check_29_wiring_is_undisturbed`, the check-31 working-id cause, asserted by its own output). The 16 + 4 failures: the 16 against item 31's eight files + any new file named; the 4 demo fixture errors in a DB env (gate row of `brief-exec-gate-chain-2026-11-05.md`). `ruff format --check` flags `guide.py` and two others, **at base too**, and no workflow runs it: not the slice's. |
| A11 FD closing act | landed in this commit | `~/gi-pricing-plan.local/scratch/aud-sl8343/drafts/` (`resolved-FD-1484.txt`, `closing-acts.patch`). Lands in the audit's own commit, INDEX regenerated after. |

**Callers of a changed shape outside the Write set (the early flag).** None broken. `scripts/doc-id.py:3202` calls `register_lint._split_row` (kept, same output). `scripts/double-stamp-scan.py:105`, `tests/test_lineage.py:589`, `test_template_headers.py`, `test_doc_id.py` load `_docid.py` by path from the real repo, which now loads `packages/model-schema/.../table_rows.py` by a repo-relative path: a copy of `scripts/` without `packages/` would raise `FileNotFoundError` at import. No test or script makes such a copy (`doc-id.py widen` shells out to `doc-index.py` in the repo root; its test uses a stand-in). `test_demo_guide.py` asserts only `{"OPT"} <= modules`, so +2 unpublished routes break nothing. `docs.yml`'s `paths` omit `table_rows.py`, `register-lint.py`, `scope-audit.py` and `register-owed.py` (the plan named the first; the others pre-date the slice).

**Corrections owed in the executor's sections (before the PR).** (1) Header `tree:` holds `afe1ee99…`, a **commit**; its tree is `966f817f…` (also LG-2067). (2) *Gate*: add the guide's declared count (A2); correct the A6 sentence (A6); add the three bare-environment runs (A5, auditor's). (3) *Gate* A9: replace "none" with the two GOV routes and the lead's ruling. (4) `tests/test_scope_audit_escaped_pipe.py:5` says "the three published routes": two are not published (A9); a docstring edit is a `.py` edit and needs `ruff check .` rc quoted (item 16). (5) T4 was committed with the code, not alone (LG discloses; its red is proved on base, and the auditor re-ran it).

**Re-merge.** `origin/main` moved docs-only (`2f108b1e`, `bdad1322`); the slice's one overlap is `docs/INDEX.md` (take theirs, regenerate, item 17). The register changed on main (`FD-1333` closed): the 362 of 362 and the `register-owed` counts above are to be re-read at the re-merged head (the gate's and the mint's), not carried.

**Gate and merge.** OWED-TO-GATE: the SOLO gate at the re-merged head, both halves, every rc quoted; the audit-docs-against-base disclosure comparison above, re-run on the re-merged head (its result: block identical but named rows); MERGE-ACK; CI by id (`python`, `docs`, `history-policy`).

**Proposed verdict (the lead's to adopt):** slice substantively delivered and evidenced; **two items NOT MET as the LG stands** (A2 guide count, A9 the two GOV routes), both closable by the lead's DP-P1 ruling and an LG edit, no code change; A10 OWED-TO-GATE. Nothing unowned.

- 2026-11-05 20:02 GMT (correction, exec-sl8343c, on the lead's to-lead "2026-11-05 19:54:56 GMT" ruling, option (a)): this section's "no script or test copies `scripts/` out of the tree" was wrong. `tests/test_doc_id_migrate.py` copies the whole `scripts/` tree in two fixtures (`_migrate_module_with_source_mutation`; `test_migrate_leaves_no_pycache_in_a_snapshot_carrying_its_own_scripts`); exec-sl8370b found both red by `FileNotFoundError` on `packages/model-schema/src/model_schema/table_rows.py`, which `scripts/_docid.py:33–43` loads by path. Fixed at `35562d5f` by one helper, `_copy_scripts_snapshot`, copying the parser to its real relative path; no fallback in `_docid.py`. Predicate: `git grep -nE 'copytree|shutil\.copy|"scripts"' -- tests backend/tests 'packages/*/tests'`, each hit read; whole-`scripts/` copies: those two only.

### Build log

- 2026-11-05: worktree `.claude/worktrees/sl-8343` from `c8d85227`; PL-2065's `7b5aa255` merged (`d6481cba`), the only conflict being `docs/INDEX.md`, where both plan rows were kept.
- 2026-11-05: R1–R4, T4 and the ruff fixes as the task list; the SL-2066 commits are in LG-2067.
- 2026-11-05 19:58 GMT: correction to aud-sl8343's "no script or test copies `scripts/` out of the tree" (not in this ledger; it is in the audit's reading): `tests/test_doc_id_migrate.py` does, in two fixtures -- `_migrate_module_with_source_mutation` (`test_class6_keys_on_the_generated_set_not_reproducibility`) and `test_migrate_leaves_no_pycache_in_a_snapshot_carrying_its_own_scripts` -- and exec-sl8370b found both red by `FileNotFoundError` on `table_rows.py`, because `scripts/_docid.py` loads `packages/model-schema/src/model_schema/table_rows.py` by path. Ruling: lead's to-lead "2026-11-05 19:54:56 GMT", option (a): the snapshot fixtures copy the parser too (`_copy_scripts_snapshot`); no fallback in `_docid.py`, no move of the parser.

- 2026-11-07: closed by the audit commit of the slice's PR (the audit of 2026-11-05 adopted by the lead, from-lead "2026-11-05 17:08:05 GMT"); the status was `active` through the mint (item 42).

## PRs

(Added at the PR.)
