---
id: LG-8081
family: ledger
title: WK-1178 slice SL-1709 — FD-1684, the four non-JSON routes declare their real media types, slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-17
owner: executor
phase: P2
work: WK-1178
slice: SL-1709
plans: []
corrected_by: []
relates: [SL-1709, PL-1708, FD-1684]
---

# LG-8081 — WK-1178 slice SL-1709: the four non-JSON routes declare their media types

*(Working id LG 8081, reserved by the lead in `eta.md`, 2026-10-17 13:10 BST.)*

**GO:** the maintainer's entry "2026-10-17 13:09:07 BST — Maintainer: SL-1709 GO CONFIRMED" in `to-lead.md`; the lead dispatched executor-1709. Need 6 (census) accepted by the maintainer, by message to the lead, 2026-10-17 (read 13:10 BST).
**MERGE-ACK:** not yet given.
**Audit:** not yet.

## Census (activation need 6), 2026-10-17 ~13:08 BST, `origin/main` ebe3292c

`git diff --name-only origin/main...origin/<branch>`, filtered to PL-1708's write set and `docs/contracts/`:

| Branch | Overlap |
|---|---|
| sl-8074, sl-8071, sl-1550, sl-1455 | none |
| sl-1543-prep-on-1300 | `generated.json` + 4 schema files |
| sl-1258-wk674-s4 | `generated.json` |
| sl-1722-wk1178-fd1730-upload-404 | `backend/tests/test_contracts.py` (6 lines at `:95`), `generated.json`, schema files |
| sl-1274-wk690-s4-factor-expression | `banding.schema.json`, `diagnostics.schema.json` only (not in write set) |
| sl-1547-wk675-s5 | `backend/tests/test_contracts.py` (34 lines after `:3337`), `generated.json`, schema files |
| sl-1341-wk1250-s3-purpose-mount | `generated.json`, `rating-algorithm.schema.json` |

Dated line, 2026-10-17 13:10 BST: the maintainer, by message to the lead, accepted both overlaps. (1) `generated.json` and the schemas: the later PR regenerates them, never hand-merged. (2) `test_contracts.py`: hunks are disjoint; whichever PR merges later re-merges `main` and re-runs `test_contracts.py` in full.

## Tasks

Branch `sl-1709-wk1178-fd1684-prep-2026-10-16`, worktree `.claude/worktrees/sl-1709`, prep `b52cba46` merged with `origin/main` ebe3292c.

- Activation commit: PL-1708 and the SL-1709 row `active`.
- Task 1: `06` §5.1 audit-export row, dated clause.
- Task 2: decorators on the four routes (`response_class` + a 200 `content` entry); handler bodies unchanged. Reds 1–4 are DB-fixture tests and **cannot run here** (no per-worktree test database): they are owed for a DB window.
- Task 3: `generate-contracts.py` changed only `generated.json`, only the four 200 blocks. `test_every_untyped_body_exclusion_is_still_untyped` was red by its cause ("no longer untyped, remove from the 2xx lists", the four keys) before `UNTYPED_2XX_PERMANENT` was removed; `test_contracts.py` then 171 passed, 2 skipped. Standing guard shown able to fail: with route 1 undeclared and regenerated, `test_no_json_body_is_untyped[response]` failed naming `('response','GET','/api/v1/rate-tables/{slug}@{version}/export/csv','200')`; reverted, `--check` clean. FD-1684's sweep predicate prints no line.
- Premise k is stale: `test_export_xlsx_parses_to_the_seeded_cells` and `test_json_export_is_line_delimited` already assert `content-type` on `main`, so no guard line was added.
- Task 4 register line on FD-1684's row; full gate owed.

## PRs

Not opened; the lead opens the PR.

## Checks (no full gate)

ruff 0; mypy 0; lint-imports 0; `generate-contracts.py --check` 0; `audit-docs.py` 0 (after `doc-index.py` regenerated `docs/INDEX.md`); `register-lint.py` 0.

## Owed

DB window: Reds 1–4 red on `main` and green here; existing export/event tests unchanged; the full two-half gate incl. frontend `generate:api` and type-check. Task 0's premise re-read (a–o) and sweep re-run at the slice base were not done in full; the sweep predicate was run on the regenerated file (no output).
