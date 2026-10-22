---
id: RS-8161
family: research
kind: audit
title: SL-1554 (WK-675 Slice 9, Designer III) narrow third re-audit of the import-closure derivation and the b5 log
status: draft
created: 2026-10-22
owner: auditor
tree: 53327067a0639b68cb9cf12330a2d072c4eb16ec
phase: P2
work: WK-675
corrected_by: []
relates: [SL-1554, PL-1546, RL-1835, RS-8159]
---

# RS-8161 — SL-1554 narrow third re-audit

*(Working id 8161, reserved by the lead. Written by `aud-1554d`, 2026-10-22 BST. Check 31 on this id is expected until the mint.)*

## Question

Do points 1 and 2 hold? Narrow, per to-lead "2026-10-22 13:47:41 BST": (1) re-run the import-closure derivation; (2) check b5's log against the head. Completeness beyond that is the slice gate's full vitest. No test, gate or DB was run.

## Method

Object: `origin/sl-1554-wk675-s9` at `beae0dffd007e58a5b00ca41bd59c814dda5f2d6`, tree `53327067a0639b68cb9cf12330a2d072c4eb16ec`. `git diff --stat ada287f3 beae0dff` = 1 file, the LG (+16): the head differs from the b5 head only in the ledger, so b5's `ada287f3` run covers the same `frontend/src`.

## Findings

### 1. Closure re-run: MET

- `closure1554.py` sha256 = `40c76bd2530a6fedb4947fcd393597753bfc5ff924b0967a22ea8f193a556b1b` (matches the LG). I read it: stdlib only (`re`, `os`, `subprocess`), reads files and runs one `git diff`, writes nothing, no network.
- Deviation, disclosed: the script hardcodes the `sl-1554` worktree. I ran a patched copy (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/aud1554d/closure-patched.py`) with two lines changed: `W` = a read-only `git archive beae0dff frontend/src` export, and the changed list = `git diff --name-only f3462d8f...beae0dff -- frontend/src` (origin/main = merge-base = f3462d8f). The regexp, resolver and closure loop are unchanged (`diff` against the original shows only those two lines). `python3 -I`, rc 0.
- Output equals the LG: L0 = the same 13 files; L1 = `StepInspector.vue`, `StepNode.vue`, `router/index.ts`, `QuoteSandboxView.vue`; L2 = `main.ts`; 10 tests direct to changed files; 18 in the closure.
- The 18 = the 12 run (b1–b4's 10, plus `StepInspector.test.ts`, `QuoteSandboxView.test.ts` in b5) + 6 via `router/index.ts`: `router/__tests__/{guard,index,routeGraph}.test.ts`, `views/__tests__/{DiagnosticsView,ModelComparisonView,ModelDetailView}.test.ts` — exactly the 6 the LG names.

### 2. b5 log: MET, with one note

`regfix-b5.log`: first line `ada287f3a1fba7fc1a4faa51c3e16846b755d1a4` (the sha the LG names); `Test Files  2 passed (2)`; `Tests  30 passed (30)`; `files:` line = `src/components/dag/__tests__/StepInspector.test.ts src/views/__tests__/QuoteSandboxView.test.ts`, exactly those two. The LG quotes the summary lines verbatim. Note: the log carries no rc line; the LG's "rc 0" is its own claim and is consistent with 2 passed / 0 failed, but is not in the log.

### 3. The 6 lazy-route-only tests: listed

The LG lists all 6 as "not run here — covered by the slice gate's full vitest" (lead 26's ruling). Confirmed listed only; not judged.

## Verdict

CLEAN on points 1 and 2 only.
