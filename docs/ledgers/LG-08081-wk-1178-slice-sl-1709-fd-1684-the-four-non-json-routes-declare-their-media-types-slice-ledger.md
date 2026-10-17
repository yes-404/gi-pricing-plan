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
**Gate:** accepted at `3b54ec82` — gate-1 14:26:05→15:45:10 BST (pair trial), the FAILED set is the accepted check-31 cascade exactly (only-new 0); see the Audit section for the shared-broker sentence.
**Audit:** written by `auditor-1709`, 2026-10-17 (below); proposed verdict only.

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

## Task 0 and the DB window, 2026-10-17 13:21–13:30 BST (executor-1709db; base `origin/main` 6bdd2571, slice head 35b305c3, tree bc5ddd7c)

**Correction to the Tasks list above (line "Premise k is stale").** Read at 6bdd2571: `git show 6bdd2571:backend/tests/test_api_rate_tables.py` and `…/test_api_audit.py` hold `content-type` asserts only at `:972` (`text/csv`) and `:177` (`text/csv`); `test_export_xlsx_parses_to_the_seeded_cells` (`:982`) and `test_json_export_is_line_delimited` (`:185`) carry none. So premise k holds, as the plan says ("two gain one line each"); the slice added those two lines (`git diff 6bdd2571...HEAD -- backend/tests/`), at `test_api_rate_tables.py:1014-1017` and `test_api_audit.py:202`. The line above is wrong.

**Sweep predicate (FD-1684 §Evidence, verbatim) on `git show 6bdd2571:docs/contracts/openapi/generated.json`**, rc 0, four lines:

```text
GET /api/v1/audit/export 200 application/json
GET /api/v1/jobs/{job_id}/events 200 application/json
GET /api/v1/rate-tables/{slug}@{version}/export/csv 200 application/json
GET /api/v1/rate-tables/{slug}@{version}/export/xlsx 200 application/json
```

**Premises a–o at 6bdd2571** (greps of `git show 6bdd2571:<path>`): a, b hold (`rate_tables.py` `Response`, `media_type` at `:239`, `:261`; decorators with no `response_class`; line numbers moved by +2 to +3 against the plan's `:220-263`); c holds (`audit.py:238`, `:245` pattern, `StreamingResponse` `:248`, `:278-280`, `:306-308`, import `:27`); d holds (`jobs.py:255`, `:264`, `:310`); e holds (`/metrics` 200 `text/plain` `{"type":"string"}` in generated.json); f holds (`health.py:139`); g holds (`uv.lock` fastapi 0.142.2); h not re-spiked (a recorded spike; the DB window's four reds and greens are the evidence on the built routes); i holds, lines moved (`_is_empty` `:3054`, `_walk_bodies` `:3069`, `UNTYPED_2XX_PERMANENT` `:3170`, `_guard_remainder` `:3224`, stale check `:3275-3276`); j holds (`SKILL.md:294`); k holds (above), test starts at `test_api_rate_tables.py:961`, `:982`, `test_api_audit.py:170`, `:185`, `test_api_jobs.py:320`; l holds (`test_api_rate_tables.py:885`); m holds, moved (`03-rating-engine.md:1047-1048`; `06:606`; `07:317`); n holds (`git grep` of 6bdd2571 in `frontend/src` minus generated: no output); o holds (`gi-pricing.yaml:479`).

**DB window** — script `~/gi-pricing-plan.local/scratch/sl1709-dbwin.sh` (small-test slot, load1 < 8, own DB from template, alembic upgrade rc 0, 1 head, `timeout 900` per file, DB dropped on EXIT). First attempt on main at load1 8.14 was REFUSED by design (rc 66), re-run after load fell.

| Run | Tree | Command | Result |
|---|---|---|---|
| green | slice 35b305c3 | `EXPECT_HEAD=35b305c3… bash sl1709-dbwin.sh` 13:23:00–13:25:16 | rate_tables `71 passed, 16 warnings in 84.49s`; audit `13 passed, 1 warning in 12.06s`; jobs `22 passed, 2 warnings in 11.43s`; rc 0 |
| red | detached 6bdd2571 + the 3 test files from 35b305c3, 13:26:11–13:28:53 | `W=…/sl-1709-main OVERLAY=35b305c3… BRANCH_GUARD=0 bash sl1709-dbwin.sh` | rate_tables `2 failed, 69 passed`; audit `1 failed, 12 passed`; jobs `1 failed, 21 passed`; rc 1 |

| Red | Test | Red on main by cause | Green on slice |
|---|---|---|---|
| 1 | `test_api_rate_tables.py::test_export_csv_publishes_text_csv` | `assert {'application/json'} == {'text/csv'}` | pass |
| 2 | `test_api_rate_tables.py::test_export_xlsx_publishes_the_spreadsheetml_type` | `assert {'application/json'} == {'application…heetml.sheet'}` | pass |
| 3 | `test_api_audit.py::test_export_publishes_csv_and_json_lines` | `assert {'application/json'} == {'application/x-ndjson', 'text/csv'}` | pass |
| 4 | `test_api_jobs.py::test_events_publish_text_event_stream` | `assert {'application/json'} == {'text/event-stream'}` | pass |

Exactly those four failed on main; no other test in the three files failed in either run; no timing-sensitive failure, so no alone re-run. The two content-type asserts added to existing tests passed on the slice. The detached worktree `sl-1709-main` was removed. **Still owed:** the full two-half gate incl. frontend `generate:api` and type-check.

## Audit

*(Written by `auditor-1709`, 2026-10-17, on head `3b54ec82a980effe4b23449605635c113a9846c6`, range `origin/main...3b54ec82` (`origin/main` = `9469721d` at fetch). Code read-only; no test run, no DB, no mint; the gate is the lead's.)*

**1. Change set** (`git diff --stat origin/main...3b54ec82`, 15 paths, +218 -50): `api/audit.py`, `api/jobs.py`, `api/rate_tables.py` (decorators only), `06-governance.md` §5.1, `docs/contracts/openapi/generated.json`, `test_contracts.py`, three route test files, `contract-guard/SKILL.md`, the register row, the roadmap SL row, PL-1708 (status), `INDEX.md`, this ledger. Nothing outside PL-1708's write set; `git diff --name-only origin/main...3b54ec82 -- docs/contracts` prints exactly `docs/contracts/openapi/generated.json` (AC 8); `-- packages/model-schema` prints nothing (AC 7, first clause).

**2. Obligations**, derived from PL-1708's Acceptance Standard, FD-1684's Disposition and the 2026-10-14 09:45:05 BST rulings (DP-1..5 as recommended) first, then evidenced:
- **AC 1 (the event):** FD-1684's sweep predicate, verbatim, run on `git show 3b54ec82:docs/contracts/openapi/generated.json`: no output. **Met.**
- **AC 2:** the plan's command on the same blob prints, per route, `text/csv` / spreadsheetml (`schema` `string`+`binary`) / `application/x-ndjson`+`text/csv` / `text/event-stream`, no `application/json` key. **Met.**
- **AC 3:** Reds 1-4 are the DB-window rows above; red on `6bdd2571` by cause (`{'application/json'}` on the left), green on `35b305c3`; the tests' asserts read in the diff (`set(content) == {...}` plus the schema). The tests are request-free `openapi()` reads; the `4`-route set matches the Goal. **Met** (the DB window predates the final head by one docs-only commit, `3b54ec82` touches the ledger only, `git diff 35b305c3..3b54ec82 --stat` is the ledger).
- **AC 4:** `test_api_audit.py:202` `startswith("application/x-ndjson")`, `test_api_rate_tables.py:1014-1017` equals the spreadsheetml type, the CSV assert at `:972` pre-exists; passed in the DB-window green run. The two new lines' planted reds: the red run on `6bdd2571` covers the contract tests; the ledger does not print a planted red for the two new `content-type` lines (they are wire asserts on routes whose wire does not change, so they cannot fail on `main` by cause). **Met, with F2.**
- **AC 5:** `UNTYPED_2XX_PERMANENT` is gone from `test_contracts.py` (list, membership test, stale-list term, reason loop all removed in the diff). The literal command `grep -n UNTYPED_2XX_PERMANENT backend/tests/test_contracts.py .claude/skills/contract-guard/SKILL.md` is NOT empty: it prints `SKILL.md:315`, the new Verified entry that names the removed symbol (F1). The stale-list red (cause quoted in the Tasks list) and the planted `test_no_json_body_is_untyped[response]` red naming the CSV route are quoted in this ledger. **Met in substance; literal command fails (F1).**
- **AC 6:** `git diff --numstat` on the three route test files: 12/0, 10/0, 25/0 (adds only). `git diff -U1` of `backend/src/app/api/*.py` shows `response_class=` and `responses=` lines only, the handler bodies untouched; `Response`/`StreamingResponse` were already imported. **Met.**
- **AC 7:** `generate-contracts.py --check` rc 0 and `pnpm generate:api` rc 0 with `tree after gate: 0 changed path(s)` in the gate log. **Met.**
- **AC 9 (gate):** below.
- **DP-5:** `06:606` carries a dated clause only (diff above), no FR renumbered. **Met.** **Register:** FD-1684's row has the dated 2026-10-17 line and keeps the Decision cell; the FD stays open until merge (the event is "run on main"). `register-lint.py` rc 0 per the ledger; re-run below.
- **Requirements without evidence:** none. No FR is added; FR-451 is the marker on the new tests.

**3. Gate at `3b54ec82`** (`scratch/sl1709-gate/gate.log`, START head `3b54ec82a980effe4b23449605635c113a9846c6`, tree `99e4afdb5e070916579c696c7cad6370d1e31cbc`, clean tree at preflight): ruff, mypy, import_linter, req_coverage, contracts rc 0; frontend install, generate:api, lint, type-check, test, build rc 0; `audit_docs` rc 1 and `pytest` rc 1 (`13 failed, 5869 passed, 6 skipped`). The 13 FAILED names are the `test_audit_docs_*`/`test_doc_index`/`test_register_*`/`test_repository_invariants` cascade, and `sort -u` of them diffs empty against SL-1758's gate list (`scratch/sl8071-gate/pytest.log`). Demo rc 124 is the designed stop (`journey done in 426s`); the one `FAIL` text is the designed `VALIDATION_HAS_FAILURES` refusal.
**Shared-broker sentence (the maintainer's ruling of 2026-10-17 18:00 BST):** this gate ran paired and the broker was found shared at 17:58 BST (Redis db 0 for both gates); the maintainer ruled that earlier verdicts stand, the reds being deterministic and slice-caused and the passes staying passes. Recorded; not re-gated.

**4. Findings.**
- **F1 (LOW):** `.claude/skills/contract-guard/SKILL.md:315` names `UNTYPED_2XX_PERMANENT`, so AC 5's literal grep is not empty. The entry is a dated Verified note about the removal; the symbol itself is gone. Owner: the lead decides whether to reword the note (one line) or accept the grep as stale text of the plan.
- **F2 (LOW):** AC 4 asks for the two new `content-type` lines' planted reds in the ledger; none is printed (the wire is unchanged, so no red on `main` exists). Disclosed; no behaviour is unevidenced since the green run passed them.
- **F3 (LOW):** the Tasks list above still says "Premise k is stale"; the later "Correction" paragraph reverses it. Both stay in place by design (the correction is the record); a reader must take the later one.
- **F4 (observation):** the DB-window evidence is at `35b305c3`, the gate at `3b54ec82`; the difference is the ledger file only (`git diff --stat 35b305c3 3b54ec82`), so no source drift.

**5. Proposed verdict:** all obligations delivered and evidenced; no requirement without a verdict; three LOW findings, none blocking. Proposal only; the lead adopts, amends or rejects. MERGE-ACK: not yet given. Status stays `active`; no mint.
