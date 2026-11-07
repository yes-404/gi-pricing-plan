---
id: LG-2070
family: ledger
title: WK-1178 slice SL-2069 — FD-1484, one table-row parser, table_rows.py (slice ledger)
status: active                 # active → closed (§1.2a)
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

**`audit-docs.py` at the slice tree (before the INDEX regeneration):** `FAILED (3)`: check 31 ×2 (the working-id gaps above) and check 39. `849` DISCLOSED lines, all residue. Journey citations: `34 endpoints, 8 functions, all declared`. DP-P1: no newly visible route fails a check. ~~A9: none surfaced.~~ **Dated line, 2026-11-05 17:12 GMT, correcting "none surfaced" (the auditor's catch, and the reason for the maintainer's 15:55:11 requirement):** the parser surfaces two routes, `GET /api/v1/dossiers/{id}` (`docs/specs/06-governance.md:610`) and `GET /api/v1/artifacts/{ref}/dependencies` (`06-governance.md:614`), declared in the spec and not built. Ruled DP-P1 (a) for both, to-lead "2026-11-05 17:08:30 GMT": surfaced by the parser, owner WK-680 (P3), `docs/roadmap.md` :3801 (WK-680's row, FR-379, the dossier render) and :3803 (its dated line, FR-384, blast radius) — those are `origin/main`'s line numbers; at this branch's tree the same two lines are :3787 and :3789, no new carry. GOV NOT PUBLISHED 10 → 12 and published 57 % → 52 %: the instrument getting more accurate, not a regression (both counts above). T4's docstring said "three published routes"; two are unpublished, corrected at `tests/test_scope_audit_escaped_pipe.py:5`. The third hidden route, lineage (`01` §5.1), is published (DATA 40 of 40).

### Audit

(To be written by the auditor.)

### Build log

- 2026-11-05: worktree `.claude/worktrees/sl-8343` from `c8d85227`; PL-2065's `7b5aa255` merged (`d6481cba`), the only conflict being `docs/INDEX.md`, where both plan rows were kept.
- 2026-11-05: R1–R4, T4 and the ruff fixes as the task list; the SL-2066 commits are in LG-2067.
- 2026-11-05 19:58 GMT: correction to aud-sl8343's "no script or test copies `scripts/` out of the tree" (not in this ledger; it is in the audit's reading): `tests/test_doc_id_migrate.py` does, in two fixtures -- `_migrate_module_with_source_mutation` (`test_class6_keys_on_the_generated_set_not_reproducibility`) and `test_migrate_leaves_no_pycache_in_a_snapshot_carrying_its_own_scripts` -- and exec-sl8370b found both red by `FileNotFoundError` on `table_rows.py`, because `scripts/_docid.py` loads `packages/model-schema/src/model_schema/table_rows.py` by path. Ruling: lead's to-lead "2026-11-05 19:54:56 GMT", option (a): the snapshot fixtures copy the parser too (`_copy_scripts_snapshot`); no fallback in `_docid.py`, no move of the parser.

## PRs

(Added at the PR.)
