---
id: LG-8091
family: ledger
title: WK-675 slice SL-1550 — S7, the sandbox compare view and its red-first tests (PL-1764), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-17
owner: executor
tree: 6c5278b558e9b8015788c1e08037ef02c57d9afd
phase: P2
work: WK-675
slice: SL-1550
plans: [PL-1764]
corrected_by: []
relates: [PL-1764, PL-1546, PL-1286, SL-1550, SL-1548, SL-1549, SL-1367, RL-1261, RL-1765, FR-262]
---

# LG-8091 — WK-675 slice SL-1550: S7, the sandbox compare view

*(Working id 8091, reserved 2026-10-17 16:36:43 BST. Quoted entries and command output keep the form they were written under.)*

**GO:** the maintainer's `to-lead.md` entry "2026-10-17 16:35:35 BST — Maintainer: #1325 read-back VERIFIED; GO SL-1550 (PL-1764)", with the 2026-10-16 09:49:25 BST confirmation of RL-1765 (conditions (1)–(3)). `RL-1765` is on `origin/main` at `1959b861`.
**MERGE-ACK:** not yet given.

## Tasks

### Red-first record (prep `8bcddabe`, `b9ef0bd6`)

Source: the executor-1550c, -1550d and -1550e entries in the local scratch file `sl1550-prep.md` (not in the repository); summarised here.

- **Acceptance 6, reds by cause** (`8bcddabe`; `vitest run QuoteComparison.test.ts QuoteSandboxView.test.ts`, rc 1): 11 failed | 14 passed. All 11 fail by `AssertionError: expected null not to be null`, the right cause (absent UI): B1–B5 (`QuoteComparison.test.ts:91/101/111/123/133`), B6 (`:145`), C1 (`QuoteSandboxView.test.ts:228`), C2–C4 (`:113`, `pickComparison`), C6 (`:289`). Wrong-cause failures: none.
- **Table A1–A6** (`stepChange` label): reds pre-existed at `d417040e`, none missing; with a stub, 6 failed at the label assert (`'' vs label`). Broken-input proof: row 5 → "Not edited" reds A5 and A6 (A6 at `not.toMatch`).
- **Table B1–B6, C1–C6**: 31 tests in the 3 files pass after the green code (`b9ef0bd6`).
- **Broken-input proofs, each mutation reverted** (`b9ef0bd6`): C1 (`v-for in comparable` → `in versions`) reds at `QuoteSandboxView.test.ts:230`, options-text assert; **C5 variant (b)** (`scoreCompare` called alongside `scoreQuote`) reds C5 at `:281` `expect(scoreCompare).not.toHaveBeenCalled()`, the plan's named assert (variant (a) reds at the first assert `:280`, so (b) is the proof); B5(i) (extra tbody row) reds at `QuoteComparison.test.ts:135`; B5(ii) (caption without "for this quote") reds at `:133`.
- **T1**: the §5.1 row in `03-rating-engine.md` landed in the same commit as the first `listRatingVersions` call.

### Activation (`9ac9620e`)

PL-1764 and the SL-1550 roadmap row `draft` → `active`, status lines and a dated roadmap line only, citing the GO stamp above and 2026-10-16 09:49:25 BST.

### Re-points (`2954b6fe`)

"RL 8057" / "PL 8054" → `RL-1765` / `PL-1764` at `docs/specs/03-rating-engine.md` §5.1 (the rating-versions list row) and six frontend lines: `QuoteComparison.vue:6`, `QuoteComparison.test.ts:9`/`:130`, `stepChange.test.ts:7`, `QuoteSandboxView.test.ts:111`/`:223`/`:224`. Comments and test titles only. Single-file vitest after the change: `stepChange.test.ts` 6 passed, `QuoteComparison.test.ts` 6 passed, `QuoteSandboxView.test.ts` 19 passed. `generate:api`: `git status --porcelain frontend/src/api` empty.

### Fixture step kinds and the red-first re-proof (executor-1550g, 2026-10-17, on `1ab31bca`)

The two test files' fixture step kinds were not in the generated `TraceStepType` union. The engine emits the algorithm step's declared type (`packages/pricing-core/src/pricing_core/rating/score.py:846-849`, `type=step.type`), and `docs/specs/03-rating-engine.md` §3.2 (lines 92-104) names exactly seven; `packages/model-schema/src/model_schema/scoring.py:79` mirrors them.

| Fixture kind | Now | Citation |
|---|---|---|
| `rate_table` | `table` | 03 §3.2 `table` row; FR-220 |
| `arithmetic` | `expression` | 03 §3.2 `expression` row |
| `cap` | `constraint` | 03 §3.2 `constraint` row (`on_violation` clamp) |
| `loading` | `expression` | ruled by the maintainer via the lead, 2026-10-17 ~18:40 BST: it consumes `{}` and produces a constant, and a `table` step needs a key (03 §3.2); the other three mappings were accepted as cited |

Every fixture step also gained `elapsed_us: 0` (required by the generated `TraceStep`). Test files only.

Red-first re-proof: with `src/api/score.ts`, `QuoteComparison.vue`, `stepChange.ts` and `QuoteSandboxView.vue` set back to their `8bcddabe` (stub) content and the fixed tests kept, vitest on the three slice test files gave 17 failed, 14 passed. A1-A6 fail on `AssertionError: expected '' to be 'Added in comparison'` (and the like); B1-B6, C1, C4 and C6 on `AssertionError: expected null not to be null` (no "Step differences" table). At the head the whole suite passes (118 files, 748 tests). The files were restored; nothing from the scratch state was committed.

The broker re-run (`backend/tests/test_celery_broker.py`, Redis db 5): 3 passed. `redis-effective.py` prints the Settings default bucket `gip-blobs` because only the test reads `GIP_TEST_BUCKET`.

### Gate

Gate run by the lead at `1ab31bca` (tree `d2db18d3786a251ee99a7fb973eb465987d1ed8c`), gate-1, 2026-10-17 16:32:36Z to 17:34:31Z; the maintainer accepted it as recorded (see Audit §4). Audit: written below, proposal only.

## PRs

None yet: the branch `sl-1550-wk675-s7-prep-2026-10-16` is pushed; the lead opens the PR after the gate.

## Audit

*(Written by `auditor-1550`, 2026-10-17, on head `d96191398985c228fb34e6df3e17c92d064c157d`, range `origin/main...d9619139`. Code read-only; no test run by the auditor; the gate is the lead's. The worktree carried one uncommitted edit to this ledger's `loading` row (the maintainer's ruling), committed with this audit.)*

**1. Change set** (`git diff --stat origin/main...d9619139`, 12 paths, +651 -16): `api/score.ts`, `QuoteComparison.vue`, `stepChange.ts`, `QuoteSandboxView.vue`, three test files (`stepChange.test.ts`, `QuoteComparison.test.ts`, `QuoteSandboxView.test.ts`), `03-rating-engine.md` (+1, the T1 row), `roadmap.md`, `INDEX.md`, `PL-1764` (status line), this ledger. Nothing outside scope; `router/` and `package.json` untouched.

**2. Obligations, derived from PL-1764's Acceptance Standard (items 1-10) and RL-1765 first, then evidenced:**
- **1, label rule held by test:** `stepChange.test.ts` A1-A6 assert the exact strings (`toBe("Added in comparison")` ... `"Changed through its inputs"`) and A6 `not.toMatch(/unchanged|not edited/i)` over all 12 combinations; `stepChange.ts:9-15` implements it. Broken-input run (row 5 to "Not edited" reds A5 and A6) recorded in the Red-first record. **Met.**
- **2, item 8 at the component:** B1 and B2 assert the two labels and `queryByText(/unchanged|not edited/i)` is null in the row. `git grep -nE "unchanged|not edited" frontend/src/components/sandbox/stepChange.ts` prints only `:4`, in the doc comment. **Met.**
- **3, each test names its FR:** `git grep -lE 'FR-262[^0-9]'` over the test files prints the three files. **Met.**
- **4, no hand-written API shape:** the `^(export )?(interface|type) (ScoreComparison|StepChange|TraceDiff|ScoreCompareRequest)` grep prints only `score.ts:12,13,15`, three `components[...]` aliases. The generated-drift limb (`generate:api` leaves `src/api/generated` empty) rests on the ledger's Re-points record, not re-run by the auditor; the PR's frontend CI re-runs it. **Met, drift limb on CI.**
- **5, no version in `context`:** C2 asserts `body.base`, `body.comparison`, `context.purpose`, `context.inputs` and `expect(context).not.toHaveProperty("options")`, plus `scoreQuote` not called. `QuoteSandboxView.vue` omits `options` on the compare call (comment cites 03:1060). **Met.**
- **6, every red seen at its assert:** the Red-first record lists B1-B6, C1, C2-C4, C6 (11 reds, all `expected null not to be null`) and A1-A6 (label asserts); C5 is a guard with broken-input variant (b) at `QuoteSandboxView.test.ts:281`. The re-proof on `1ab31bca` gives 17 failed, 14 passed, which is 6 (A) + 6 (B) + 5 (C1-C4, C6). **Met.**
- **7, no new route or dependency:** `git diff --stat origin/main...d9619139 -- frontend/src/router frontend/package.json` prints nothing, rc 0. **Met.**
- **8, gate green on the merge tree:** NOT yet met as written. The Python half ran at `1ab31bca` and stands for `d9619139` (diff `1ab31bca..d9619139` is this ledger and two test files only). The frontend half failed in the gate (fixtures), was fixed test-only at `d9619139` and the seat's FE half then gave rc 0 (748 tests); the lead's frontend gate was not re-run on `d9619139`. The PR's frontend CI is the independent full run. **Verdict: delivered, gate evidence for the FE half is the seat's plus pending CI.**
- **9, T1 is one row, with the first call:** `git grep -nE '^\| `GET` \| `/api/v1/rating-versions` \|'` prints exactly one line (`03-rating-engine.md:1051`). Both `git log --reverse -S` commands print `b9ef0bd6` first, the same commit. `audit-docs.py` rc 0 on that commit: not re-run by the auditor (see §4 for the head). **Met.**
- **10, RL-1765's breakers recorded:** C1 (unfiltered picker reds the options-text assert), B5(i) (extra row, `QuoteComparison.test.ts:135`), B5(ii) (caption, `:133`) are in the Red-first record. B5 asserts `name: /11 steps unchanged for this quote/` and `toHaveLength(5)` in fixture order; C1 asserts `["No comparison", "motor-gb@2 · approved"]`. **Met.**
- **FR-262 view limb (03:183, "the Quote Sandbox view is WK-675's"):** picker, one-quote-two-versions call, side-by-side summary (B6), step differences (B1-B5), per-quote error naming the side (C3), refused list leaves the sandbox usable (C6). **Met.**

**3. Fixture kinds (d9619139).** The `loading` to `expression` row now cites the maintainer's ruling; the other three cite 03 §3.2 and `score.py:846-849`, which I checked name the emitted `step.type`. Test files only; the `1ab31bca..d9619139` diff confirms.

**4. Gate at `1ab31bca`.** ruff, mypy, import_linter, req_coverage, contracts rc 0 (`scratch/sl1550-gate/*.rc`). `audit_docs` rc 1 with one FAILED block, verbatim: `FAILED (1):  - check 31: gap in the full allocation between 1771 and 8091` (a working-id artefact until LG 8091 is minted). pytest rc 1, `14 failed, 5929 passed, 6 skipped`: 13 are the `test_audit_docs_*`, `test_doc_index`, `test_register_*`, `test_repository_invariants` cascade of check 31; the 14th, `backend/tests/test_celery_broker.py::test_publisher_puts_a_readable_message_on_the_named_queue`, passes isolated on Redis db 5 (`scratch/sl1550g/broker.log:14`, `3 passed`): the shared-broker mechanism, environmental, not a slice file. Demo: `grep -c 'job not found'` = 0.

**5. Findings.**
- **A1 (LOW, fixed here):** the Gate line read "Owed ... Audit: not yet" after the gate was accepted; updated above. MERGE-ACK left "not yet given".
- **A2 (LOW, observation):** acceptance 8's frontend half has no lead-run gate on `d9619139`; the PR CI must be read before the lead's merge, and the quote-form re-merge rule (PL-1764 Global Constraints) needs `origin/main` re-merged and the sandbox tests re-run if main moved the quote form since `1ab31bca`.
- **A3 (LOW, observation):** the Red-first record's re-proof prose names C1, C4, C6 for the 17 reds; C2 and C3 are the other two (they fail at `pickComparison`, `:113`). The count adds up; the prose is partial.
- **A4 (LOW, observation):** front matter `tree:` is `6c5278b5...`, a pre-gate tree; it is the executor's stamp and not re-derived here.

**6. Proposed verdict:** every requirement of FR-262's view limb and every Acceptance item has evidence; none undelivered, none deferred, none reassigned. Item 8's frontend half is delivered-but-awaiting-CI (verdict "delivered, evidence pending the PR run"). Proposal only; the lead adopts, amends or rejects. MERGE-ACK: not yet given.
