---
id: LG-8344
family: ledger
title: WK-1178 slice SL-8343 — FD-1484, one table-row parser, table_rows.py (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05            # filed under working id 8344
owner: executor
tree: afe1ee999f91cd0959609c8a0c146e2daeecd178   # sl-8343-table-row-parser, the code head this was written against (base c8d8522758859d23fac5542815ccaa59c5a4b087)
slice: SL-8343
phase: P2
work: WK-1178
plans: [PL-8342]
corrected_by: []
relates: [FD-1484, PL-8342, PL-8330, LG-8332]
---

# LG-8344 — WK-1178 slice SL-8343: one table-row parser

**GO:** to-lead "2026-11-05 09:58:58 GMT" (FD-1484 coded and merged before Thu 12 Nov); "2026-11-05 10:36:35 GMT" (all nine plans accepted; DP-P1 (a) row by row; DP-P2 (a) keep `\|` as written; T folded onto this branch and gate).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL 8342, "SL 8343 — one row parser". No requirement id: tooling. Register: FD-1484. The slice also carries PL 8330's commits (SL 8331, LG 8332), folded onto this branch and gate by the 10:36:35 entry. The branch is `sl-8343-table-row-parser`; its base is the PL 8342 head `c8d85227`, and the PL 8330 draft head `7b5aa255` was brought in as a merge (`d6481cba`), never a rebase.

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
- T1–T3, with `table_rows.py` moved aside on the slice tree: `ImportError: cannot import name 'table_rows' from 'model_schema'`.
- T2 with a planted `import pydantic` (not committed): `AssertionError: {'pydantic'}`.
- T4 on base (the test file copied into a detached worktree of `c8d85227`, `/tmp/sl8343/base`): `AssertionError: assert ('GET', '/api/v1/dataset-versions/{}/lineage') in {...}`, `1 failed in 0.30s`.

**Green, at the slice tree:**

- `packages/model-schema/tests/test_table_rows.py`: `12 passed in 3.38s`.
- `tests/test_scope_audit_escaped_pipe.py`: `1 passed in 0.62s`.
- `declared_endpoints("DATA")` 40 and `("GOV")` 25 (A7).
- `python3 scripts/doc-index.py --phase P2`: rc 0, the report prints (`11 closed`, `122 planned, 103 delivered`); `register-lint.py`: rc 0, `0 violations`.
- `ruff check .`: `All checks passed!`.
- A5, bare environment: `env -i PATH=/usr/bin:/bin python3 -I` loads `scope-audit.py` (the figures above) and `scripts/scope-audit.py --help` prints; `audit-docs.py`, `doc-index.py` and `register-lint.py` ran under `run-heavy.sh` (inherited environment).
- A6: `git grep -n -E '\.split\(.\|.\)|\(\[\^\|\]\+\)|\(\?<!\\\\\)\\\|' -- scripts backend/src packages tests backend/tests` prints only `table_rows.py:20` (`UNESCAPED_PIPE`) and `:36` (`split_row`'s own split). The exception list is empty.

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

**`audit-docs.py` at the slice tree (before the INDEX regeneration):** `FAILED (3)`: check 31 ×2 (the working-id gaps above) and check 39. `849` DISCLOSED lines, all residue. Journey citations: `34 endpoints, 8 functions, all declared`. DP-P1: no newly visible route fails a check, so nothing is stopped (A9: none).

### Audit

(To be written by the auditor.)

### Build log

- 2026-11-05: worktree `.claude/worktrees/sl-8343` from `c8d85227`; PL 8330's `7b5aa255` merged (`d6481cba`), the only conflict being `docs/INDEX.md`, where both plan rows were kept.
- 2026-11-05: R1–R4, T4 and the ruff fixes as the task list; the SL 8331 commits are in LG 8332.

## PRs

(Added at the PR.)
