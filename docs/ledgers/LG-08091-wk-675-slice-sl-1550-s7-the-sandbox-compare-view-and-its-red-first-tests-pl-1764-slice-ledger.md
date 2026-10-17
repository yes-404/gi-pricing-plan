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

### Gate

Owed: the lead's two-half gate on a free slot. Audit: not yet.

## PRs

None yet: the branch `sl-1550-wk675-s7-prep-2026-10-16` is pushed; the lead opens the PR after the gate.
