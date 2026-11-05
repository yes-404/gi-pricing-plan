---
id: LG-8362
family: ledger
title: WK-1178 slice SL-8361 — FD-1482 limb 2 (a), RL-1483 item 1: the Permission column on every §5.1 row (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05            # filed under working id 8362
owner: executor
tree: 2e8a40ca                 # sl-8361-permission-column, the commit of `07`'s spec change (base 2f108b1eda22a4835279cee9b4c9e305babe3662, origin/main)
slice: SL-8361
phase: P2
work: WK-1178
plans: []
corrected_by: []
relates: [FD-1482, RL-1483, FR-343]
---

# LG-8362 — WK-1178 slice SL-8361: the `Permission` column on every §5.1 row

**GO:** to-lead "2026-11-05 12:02:53 GMT" (SEAT GO: docs only; no DB, docker or source; audit-docs via `run-heavy --light`; any spec/code disagreement is a finding; ends unpushed; (b), the pin, waits on LAST-2's `table_rows`). Lead's reading of the enumeration: `04` and `05` are beyond RL-1483's five tables; the widening is named below.
**MERGE-ACK:** none yet (unpushed).

## Tasks

### Scope

`RL-1483` item 1: every §5.1 REST table gains a fourth column `Permission`, filled on every row; a multi-method row splits to one row per method; `06`'s blockquoted `| Route | Requires |` table is folded into `06` §5.1's column.

**Widening, named:** RL-1483 names five tables (`01`, `02`, `03`, `06`, `07`) and 152 rows (157 after the split). At `origin/main` 2f108b1e, `04-optimisation.md` §5.1 and `05-monitoring.md` §5.1 also carry the same `| Method | Path | Purpose |` header, and `FD-1482`'s triage counts seven tables. This slice covers all seven, on the brief's "each §5.1 table" and the lead's reading.

**Enumeration.** Predicate: for each `docs/specs/0{1..7}-*.md`, the lines between the `### 5.1` heading and the next `### ` heading; a row is a line matching `^\|\s*\`?(GET|POST|PUT|PATCH|DELETE)`; a header is `^\|\s*Method\s*\|`; no other pipe line sits in the range. Script `/tmp/enum8361.py` (not committed). At base: 7 tables, one header each; rows `01`=39, `02`=45, `03`=45, `04`=10, `05`=16, `06`=23, `07`=24, **202 in all**. Rows naming two methods (5): `01` `GET`/`PUT` `/datasets/{slug}/rule-set`; `06` `GET`/`POST` `/roles` and `GET`/`PUT` `/approval-policy`; `07` `GET`/`POST` `/environments` and `GET`/`PUT` `/settings`. After the split: **207**, `01`=40, `02`=45, `03`=45, `04`=10, `05`=16, `06`=25, `07`=26 (same predicate, at the head).

**Rows split:** the five above. Each Purpose cell was cut to its own method's half.

**Fold in `06`.** The `Route | Requires` table (six rows, seven operations) is removed; its cells are the `Permission` cells of `POST`/`GET /approval-requests`, `GET /approval-requests/{id}`, `GET`/`PUT /approval-policy`, `decide` and `withdraw`. A dated note (2026-11-05) records the fold; the 2026-08-15 prose that explains the `authenticated` cells stays. The old blockquote also split the table in two (a header-less run of rows from `attestations` on); the rows are now one table.

### Task list

1. Enumerate (reported to the lead).
2. Fill cells spec-side from `06` §4.1 `Governs` text and each module's text; one commit per spec (`01`…`07`); the fold is in `06`'s commit.
3. Check the cells against the route code (read-only) and list disagreements.
4. Reader counts before/after (after RELEASE; see Gate).

### Gate

**Pending: TESTS HOLD.** No `audit-docs.py`, `doc-index.py` or `scope-audit.py` has been run on this branch. After the lead's RELEASE: `run-heavy.sh --light -- python3 scripts/audit-docs.py` and `doc-index.py`, `scope-audit.py --endpoints` before and after, and the route counts quoted here.

**Reader analysis (static, from the regexes; to be confirmed by the measurement above).** `audit-docs.py` `_ENDPOINT_ROW`, `scope-audit.py` `_ENDPOINT` and `backend/src/app/demo/guide.py` `_SPEC_ENDPOINT` each match `^\|\s*\`?([A-Z]+(?:\`?/\`?[A-Z]+)*)\`?\s*\|([^|]+)\|` and read only the first two cells, so the fourth cell is unread. The five split rows give the same `(method, path)` pairs as before. The three `\|` path cells (`01` lineage; `06` dossiers and dependencies) are cut at the escaped pipe by all three readers, before and after (RL-1483's #983 defect, untouched here). Check 22 (cell count) requires header and rows to agree: the header, separator and all 207 rows gained one cell in the same commit.

### Audit

Not yet. The auditor's.

### Build log

- 2026-11-05T12:12Z — commits `d4e1664e` (`01`), `f936700c` (`02`), `fae60ec7` (`03`), `9e1b7d25` (`04`), `5754098a` (`05`), `c51400dd` (`06`, with the fold), `2e8a40ca` (`07`).

#### Cells the spec does not state (provisional; the lead's to rule)

`06` §4.1's vocabulary is closed, and these rows have no permission in any spec text. Each cell is written, with a spec-level note under the table, and listed here.

- `04` (all 10 rows): no module text names a permission. Writes take `optimisation:run` (elasticity, run, gipp-check, disparity-report) and `optimisation:materialise`; the five reads take `authenticated` because §4.1 has no read member. Whether reads need a new member is a design choice for `open-questions.md` (not in this slice's write set).
- `05` (all 16 rows): `monitor:write` for create, run, rebaseline, refit-recommendations and monitoring-packs; `alert:acknowledge`; `alert:resolve` for resolve and suppress; the nine reads `authenticated`. The refit, suppress and pack assignments are guesses from the closest name.
- `06` unbuilt rows with no permission in the spec: `attestations` and `dossiers/{id}/commentary` (`approval:decide`); `audit/anchor`, `dossiers` (POST, GET), `regulatory-exports`, `artifacts/{ref}/history`, `artifacts/{ref}/dependencies` (`audit:read`); `roles` GET and POST, `role-assignments` (`admin:manage_roles`; §4.1 names the write, not the `GET`).
- Built rows where the spec is silent and the cell takes the code's value (TRAP 1: these are the only cells that reflect code): `02` `POST /models/{id}/archive` = `model:submit` (FR-202 and §4.1 name none); `02` `POST /models/{id}/predict` = `model:read`; `03` `POST /rating-versions/{id}/regression-runs` = `rating:compile`. `03` `POST /dislocation-runs/estimate` takes the run's permissions on the row's own text ("the same permissions").

#### Spec/code disagreements

None found on the built rows where the spec states a value. Checked against `backend/src/app/api/*.py` (an AST listing of each route's `requires(...)` dependency, plus `rbac.require_permission(` in `platform/deployments.py` and `platform/shadow.py`) over the 100-odd built routes; the deploy, rollback, routing and deployment-request cells rely on `deployments.py:_authorised_environment` and were not each traced to their call site. `PATCH /datasets/{dataset_id}` is `dataset:read` plus an owner-or-`admin:manage_roles` rule in the handler, as FR-82's 2026-08-23 text says; `POST /validation-rules` is `dataset:write` or `admin:manage_settings` for a `sql` check, as the code docstring and `01` §4.5 step 5 say.

## PRs

None. Ends unpushed.
