---
id: RS-8231
family: research
kind: audit
title: SL-1554 (WK-675 Slice 9, Designer III) written delta audit of the gate head 11c3db18 and its gate evidence
status: draft
created: 2026-10-25
owner: auditor
tree: b6c06684ce69aa183f1617e49fa7a1c776f39be4
phase: P2
work: WK-675
corrected_by: []
relates: [SL-1554, PL-1546, RL-1835, RS-8156, RS-8158, RS-8159, RS-8161]
---

# RS-8231 — SL-1554 delta audit of the gate head

*(Working id 8231, reserved by the lead. Written by `aud1554d`, 2026-10-25 GMT. Check 31 on this id is expected until the mint.)*

## Question

The gate of record ran on `11c3db18b3bef3f13aff50b7778b4dacc8e8a5a5` (tree `b6c06684ce69aa183f1617e49fa7a1c776f39be4`, `origin/sl-1554-wk675-s9`). The lead ruled that gate stands under the maintainer's standing 1(f) (to-lead "2026-10-25 14:19:54 GMT"), with this written audit owed before the ACK. Is the delta from the last audited head to that head what was expected (re-merges of main plus docs folds), did the slice's own code change, and does the gate evidence read as claimed? Read-only: no test, gate or DB was run.

## Method

Scope first, from the four earlier audit records and the lead's brief; evidence second, from `git` (`diff --stat`, `log ... ^origin/main`, `rev-parse` blob comparison, `patch-id --stable`) and from the gate's own files, read directly. Every git command above ran with `git -C` against `origin/main` at `034781b3`.

## Scope

**Last audited head: `beae0dffd007e58a5b00ca41bd59c814dda5f2d6`.** RS 8161 names it: "Object: `origin/sl-1554-wk675-s9` at `beae0dffd007e58a5b00ca41bd59c814dda5f2d6`, tree `53327067a0639b68cb9cf12330a2d072c4eb16ec`" (RS 8156 audited `ce22af6e`, RS 8158 `ab48b63e`, RS 8159 `ada287f3`; each is an ancestor of `beae0dff`, and RS 8161 is the newest). RS 8161's verdict is "CLEAN on points 1 and 2 only" (import-closure derivation and the b5 log).

Delta: `git diff beae0dff..11c3db18 --stat` = 117 files, +12297 −331. Non-docs: `git diff --name-only beae0dff..11c3db18 -- . ':!docs'` = 69 files.

## 1. Whose is each non-docs file

`git log --no-merges --format=%h beae0dff..11c3db18` lists 21 commits. Of them, `git log --no-merges --format='%h %s' beae0dff..11c3db18 ^origin/main` (the ones not reachable from `origin/main` at `034781b3`) lists 10, **all `docs(...)` commits** (LG 8141 entries, the INDEX regenerations, `0e51caf7` which folds the four RS). `git log --no-merges --format= --name-only beae0dff..11c3db18 ^origin/main | sort -u` names six files: `docs/INDEX.md`, the LG, RS 8156, 8158, 8159, 8161. **No non-docs file is the slice's in this delta.**

The other 11 non-merge commits are main's (reachable from `origin/main`), brought in by the two re-merges `d05de366` (second parent `ff976406`) and `11c3db18` (second parent `3cd5fcf7`). Cross-check on content: for all 69 non-docs files, `git rev-parse 11c3db18:<f>` equals `git rev-parse 3cd5fcf7:<f>` (main at the last re-merge) — 69 of 69 identical, 0 differ. So every one is main's re-merged content (slice A, vitest bump, SL-1711 close, #1371 among them, as expected; examples, model-schema, pricing-core, scripts, frontend objective editor).

## 2. Did the slice's own code change since the audit

Slice-only delta = the non-docs diff from the main parent of each head's last merge to the head: `git diff <main-parent> <head> -- . ':!docs' | git patch-id --stable`.

| Head | Last-merged main parent | patch-id | shape |
|---|---|---|---|
| `beae0dff` | `f3462d8f` | `7638106bc07d14e7c38f9b6e3f88240c0a6b0566` | 13 files, +953 −65 |
| `11c3db18` | `3cd5fcf7` | `7638106bc07d14e7c38f9b6e3f88240c0a6b0566` | 13 files, +953 −65 |

**Identical.** The slice's non-docs change is byte-for-byte what RS 8156–8161 audited. (Note, not a defect: `origin/main` has since moved to `034781b3`, so `git diff origin/main 11c3db18 -- frontend` now shows 25 files — main's #1372 files. The slice's own diff against its merged parent is unchanged.)

## 3. Gate evidence (read from `~/gi-pricing-plan.local/scratch/sl1554-gate1b/`)

`gate.log` line 1: `START head: 11c3db18b3bef3f13aff50b7778b4dacc8e8a5a5 tree: b6c06684ce69aa183f1617e49fa7a1c776f39be4 branch: sl-1554-wk675-s9` at 2026-10-25T13:15:59Z, END 14:18:47Z; the same tree as this audit's `tree:`. "tree after gate: 0 changed path(s)".

| Row | Result (file) |
|---|---|
| ruff | rc 0 (`ruff.rc`; "All checks passed!") |
| mypy | rc 0 ("Success: no issues found in 249 source files") |
| import_linter | rc 0 |
| req_coverage | rc 0 |
| contracts | rc 0 ("58 generated contracts match the models") |
| audit_docs | rc 1 (`audit_docs.rc`) — `FAILED (5)`, all **check 31**: gaps 1863→8141, 8141→8156, 8156→8158, 8159→8161, and "id 8141 is `created:` 2026-10-21, earlier than id 1863's 2026-10-22". Nothing else failed (check 32 absent). These are the slice's own working ids. |
| pytest | rc 1 (`pytest.rc`); summary line `13 failed, 6764 passed, 21 skipped, 147 warnings in 2376.32s (0:39:36)` |
| FE install / generate:api / lint / type-check / test / build | rc 0 each; `Test Files  133 passed (133)`, `Tests  847 passed (847)` |
| demo wf-699 | rc 0, 1146 s, "designed stop … (both lines seen)"; D7 ok (19985 policies); keycloak restored, bind source under tools-main |
| zeros | `own-DB count=0 redis RT db 2 dbsize=0 redis RD db 4 dbsize=0` |

The 13 pytest failures by file (`grep '^FAILED' pytest.log | sed 's/::.*//' | sort | uniq -c`, total 13): finding_citations 1, audit_docs_ids 2, process_core_digest 2, w37_11_ceiling 1, test_doc_index 1, test_register_lint 3, test_register_owed 1, test_repository_invariants 2. That is **exactly the 8 files of 1(f)** (seat-brief item 31), no other file. Redis dbs used: 2 and 4 (gate-1b's, item 33). The one `VALIDATION_HAS_FAILURES` line in `demo.log` is the demo's designed refusal output, in a run that exited 0.

1(f) conditions still owed before the ACK (the lead's, listed not judged): the mint at its turn, audit-docs rc 0, the 8 tests re-run via run-small on the minted head, CI incl. python, the FAILED lines quoted by file at the ACK.

## Findings

| # | Severity | Finding |
|---|---|---|
| B1 | Low, non-blocking | `pytest.log` does not open with `head=<sha>` / close with `rc=` (item 37); it opens with a progress line. The head and rc are carried by `gate.log` line 1, `pytest.rc` and the summary line, which agree, so the verdict is readable. Process note only (`docs/process/process-backlog.md` class). |
| B2 | Informational | `audit_docs.log` quotes `rc` only in `audit_docs.rc`; check 36 "legacy form survives" lines are warnings of main's content (WF-00702), not failures. |

No blocking finding. No `FD-` is proposed.

## Verdict (proposal; the lead's to issue)

**CLEAN.** The delta `beae0dff..11c3db18` is main's re-merge (69 of 69 non-docs files identical to main `3cd5fcf7`) plus docs folds; the slice's own non-docs patch is unchanged (patch-id `7638106b…` at both heads); the gate lines read as claimed (13 failed = the 1(f) set, audit-docs failing only check 31, FE 133/847, demo rc 0, zeros). The 1(f) pre-ACK conditions remain the lead's.

## Breach disclosure (this seat)

None. No `cd`, no test, gate, DB or GitHub action. `tools-main` was not touched.
