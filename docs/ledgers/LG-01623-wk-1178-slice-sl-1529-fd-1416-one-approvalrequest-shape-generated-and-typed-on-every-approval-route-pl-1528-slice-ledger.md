---
id: LG-1623
family: ledger
title: WK-1178 slice SL-1529 — FD-1416, one ApprovalRequest shape, generated and typed on every approval route (PL-1528 slice ledger)
status: closed
created: 2026-10-11
owner: executor
tree: 31b88780aa52894624a5e08454ce2d5925d04b37
phase: P2
work: WK-1178
slice: SL-1529
plans: [PL-1528]
corrected_by: []
relates: [PL-1528, FD-1416, FD-1335, RL-1522, SL-1409, FR-9, FR-451, FR-351, FR-355, FR-357]
---

# LG-1623 — WK-1178 slice SL-1529: FD-1416, one ApprovalRequest shape

*(LG-1623 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1529` from PL-1528, base `origin/main` `31b88780aa52894624a5e08454ce2d5925d04b37`.
Times are BST (`TZ=Europe/London date`) unless marked.

**GO:** "2026-10-10 21:36:36 BST — DISPATCH GO: SL-1526 (exit demo (a)) and SL-1529 (FD-1416); FD-1573 severity; SL-1575 OFF the G2 serial path (corrects my 21:33:57 items 2 and 4)", item 4 (`to-lead.md`, a local channel file, so cited by its header): need 4 is the executor's Task 0 print, with STOP if non-zero; OP-1529-W1 ADOPTED (`scripts/audit-docs.py` joins the write set for `_CONTRACT_ARTIFACT_PATHS` only; the count comment at `:2612` is updated by a dated clause if the total changes; the SL-1430 precedent is `5351f116`, +2); `generated.json` regenerated on the merge base at merge time. Gate order, item 5 (revised): ready-first among WK-675 S4, WK-675 S3, SL-1600; then SL-1526's proving run alone, SL-1541, SL-1390, SL-1529, SL-1503.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice is `SL-1529` (`docs/roadmap.md`, `#### SL-1529`, WK-1178): *"WK-1178 fix slice — FD-1416: one ApprovalRequest shape, generated and typed on every approval route"*. Its plan is `PL-1528` (leaf plan, Tasks 0 to 7, DP-1 to DP-10 all ruled by `RL-1522`). Requirement ids: FR-9, FR-451, FR-351, FR-355, FR-357. Per Lean P2 L1 (a') the slice's one PR sets `PL-1528` and the `SL-1529` row to `active` in this branch's first commit and closes this ledger and the row at its head.

Write set: `PL-1528` §"Write set, and its contention", plus the ruled `scripts/audit-docs.py` entry (OP-1529-W1: `_CONTRACT_ARTIFACT_PATHS` only). Any other path is a STOP to the lead.

### Task list

- [x] Task 0 Steps 1 to 3 (preconditions, re-measure, data check): see the build log.
- [ ] Task 1: characterisation and Acceptance 12, 13.
- [ ] Task 2: the model (Acceptance 2, red first).
- [ ] Task 3: service and routes (Acceptance 2, 3, 4).
- [ ] Task 4: one definition (Acceptance 6; the ruled `audit-docs.py` entry).
- [ ] Task 5: the F27-class guard (Acceptance 7).
- [ ] Task 6: check `06`'s texts (Acceptance 8).
- [ ] Task 7: the gate and this ledger.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (not yet run) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-10 20:39 to 21:42 BST, Task 0.** Worktree `.claude/worktrees/sl-1529`, branch `sl-1529-fd1416-approval-request`, from `origin/main` `31b88780aa52894624a5e08454ce2d5925d04b37`.

- **Need 4, Step 3 (the data check).** Script: `/tmp/sl1529-scratch/need4.py` (outside the repository). It reads each `approval_requests` row with its decisions through a read-only `SELECT` (`docker exec gi-pricing-postgres-1 psql`), drops `environment` and `decided_at` (the current model lacks the first; Task 2 adds it as `str | None`), recomputes `approvers_recorded` from the approve decisions, and validates with `ApprovalRequest.model_validate`. Output, verbatim:

```text
gipricing: rows=12 unparseable=0
gipricing_sl-1340_fbd0c18e: rows=0 unparseable=0
gipricing_sl-1387_16b0caff: rows=0 unparseable=0
gipricing_sl-1463_2128cef0: rows=0 unparseable=0
gipricing_sl-1466_829eef9f: rows=0 unparseable=0
gipricing_sl-1536_a185ace2: rows=0 unparseable=0
gipricing_sl-1557_99fec5d8: rows=12 unparseable=0
gipricing_sl-1559_a21fe7ac: rows=76 unparseable=0
gipricing_sl-1600_08820bd9: rows=12 unparseable=0
gipricing_sl-9618_6692d8df: rows=0 unparseable=0
TOTAL unparseable=0
```

  (`gipricing_sl-1559_a21fe7ac` read 50 rows in an earlier count query, 76 at the print: another run was writing to it.) `n = 0`, so no STOP.
- **Commit 1:** `PL-1528` `status:` `draft` to `active`, the `SL-1529` row `draft` to `active`, and this file.

**Plan delta D1 (2026-10-10, accepted by the lead in `to-lead.md`-channel message to `executor-sl1529`, before the gate): `SHIPPED_NOT_COMPARED` holds 4 slugs, not PL-1528's 5.** PL-1528 Acceptance 7 and Task 5 list `dislocation-run` among the exempt slugs. At `origin/main` `31b88780aa52894624a5e08454ce2d5925d04b37` it is generated (SL-1387), so it is no longer authored-only, and the guard's own stale-check ("`SHIPPED_NOT_COMPARED` names a slug that is no longer authored-only") would refuse it. Measured at that tree with the predicate (authored-only slug; the authored file's `title` plus its `$defs` keys; a name counts when `model_schema` exports it as a `pydantic.BaseModel` subclass), by this script (kept out of the repository, run as `uv run --directory <worktree> python f27.py <worktree>`):

```python
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
A = root/"docs/contracts/schemas"; G = A/"generated"
import model_schema
from pydantic import BaseModel
gen = {p.name.split(".")[0] for p in G.glob("*.schema.json")}
auth = {p.name.split(".")[0]: p for p in A.rglob("*.schema.json") if G not in p.parents}
for s in sorted(set(auth) - gen):
    d = json.loads(auth[s].read_text())
    names = [d.get("title",""), *d.get("$defs", {})]
    f = [n for n in names if isinstance(getattr(model_schema, n, None), type) and issubclass(getattr(model_schema, n), BaseModel)]
    print(s, f)
```

Output: `approval-request ['ApprovalRequest']`, `dossier []`, `gipp-check []`, `money []`, `monitoring []`, `optimisation-run []`, `provenance []`, `rate-table ['RateTableVersion']`, `rating-algorithm ['RatingAlgorithm']`, `rating-version ['RatingVersion']`, `scoring ['QuoteContext', 'LadderRung', 'ScoringResult', 'Trace']`. So the predicate finds 5 slugs; `approval-request` is fixed by this slice and the map holds the other 4.

**Commits so far** (pushed): `1e0ca169` activation + this ledger; `7691b823` Task 1; `bfb14545` the tests-only red commit (Acceptance 2, 3, 4, 7); `4dc32059` Task 2; `b10b37a2` Task 3; `853cbe4d` Task 4 sources. No test has been run yet: the DB-backed reds and greens run inside this slice's gate-1 slot (the amended RL-1445 of 21:41:05, item (b)), each red at a scratch worktree of the commit that carries only the tests.

- **Slot script (2026-10-11):** `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1529/slot.sh` (local, not in the repository); logs go to `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1529/gatelogs/` (durable, not `/tmp`). It recreates the worktree database (S-14), runs the reds by cause for Acceptance 2, 3, 4, 7 (i to iii), 12 and 13 on base sources or scratch mutations, then the full two-half gate. Merge of `origin/main` `d699a561` done (merge-tree rc 0); contracts regenerated at `d2a720d7`; Acceptance 8's counts 0, 1, 0, 0.

## Gate record (2026-10-11, gate-1, 11:33:47 to 12:23:40 BST)

Run at `origin/main`-merged head `823a617f1be343364d14c932aad780c8f3f82e77` (tree `ee36e4e0efbb2d852eec9d3bb3baae04298178e4`), by `scratch/sl1529/slot.sh`; alembic rc 0. Logs: `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1529/gatelogs/<stage>.log` and `.rc`.

| stage | rc | classification |
|---|---|---|
| red_a234 | 1 | red by cause |
| red_a7i | 1 | red by cause |
| red_a12 | 1 | red by cause |
| red_a13 | 1 | red by cause |
| red_a7ii | 1 | red by cause |
| red_a7iii | 1 | red by cause |
| ruff | 1 | OWN: 5 errors, fixed below |
| mypy | 0 | green |
| import_linter | 0 | green |
| audit_docs | 1 | mint artefact (check 32 on LG-1623 x3; check 39 INDEX stale) |
| req_coverage | 0 | green |
| contracts | 0 | green |
| pytest | 1 | 13 failed, 5466 passed, 4 skipped: the docs/audit tests, mint artefact (lead-accepted) |
| fe_install, fe_generate, fe_lint, fe_typecheck, fe_test, fe_build | 0 | green |

Red causes, quoted from the logs: `red_a234` "Extra items in the right set: 'workspace_id'"; `red_a7i` "authored-only but shipped in model-schema: {'approval-request': ['ApprovalRequest']}"; `red_a7ii` the same with `{'rate-table': ['RateTableVersion']}`; `red_a7iii` the same with `{'scoring': ['LadderRung', 'QuoteContext', 'ScoringResult', 'Trace']}`; `red_a12` "assert 500 == 409" (unhandled `uq_approval_requests_open_artifact`, sqlstate 23505); `red_a13` "assert 'review' == 'draft'". None is the DagDesigner F39 case (WK-675's): the frontend stages are green.

The five ruff errors were `approvals.py:28` F401; `test_approval_request_shape.py` :7 I001, :201 PT018, :272 E501; `test_contracts.py:2687` I001. Fixed after the run (`ruff check` on the three files: all checks passed): the unused import and two import blocks by `--fix`, PT018 split into two asserts (both conditions kept), E501 by a local `content` variable. Test meaning is unchanged; the fix commit is the ledger's head and was not re-gated.

## PRs

(none yet)
