---
id: PL-1535
family: plan
kind: map
title: WK-1178 — the FD-1374 fix slice, FR-246 enforced (DP-F35-1's limb split out of the F35 plan and kept in P2): single-row Work plan
status: active                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-09  # original date 2026-10-08, set at the draft; minted 2026-10-09
owner: planner
tree: 60e9254c22972c03fb11f10fcce8dae4f1c00dd9
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1374, PL-1371]
---

# PL-1535 — WK-1178: the FD-1374 fix slice, single-row Work plan

> **For agentic workers:** this is WK-1178's **single-row Work plan** under Lean P2 L5. WK-1178,
> the standing maintenance Work, has no map plan, so this is not a delta of one: it is one row,
> the slice `SL-1536`, cut in this file's branch. The slice's task steps are an
> existing, audited plan's Task 1A, quoted by reference below, so no step is restated here; its
> `LG-` quotes this row as its scope and Task 1A as its tasks. REQUIRED SUB-SKILL for the
> executor: subagent-driven-development (recommended) or executing-plans. The executor also
> binds `python-test` (the `req` marker and broken-input proofs), `test-driven-development`
> (every test seen red first, by its cause), `dev-commands` (the gate slot wrapper, the two-half
> gate) and `git-hygiene`; reads [`README.md`](README.md)'s five unchecked conventions; and is
> spawned from `.claude/roles/executor.md`.

Filed under working id 9470; the slice row was working id 9469; both reserved by the lead
(2026-10-08). Minted 2026-10-09 as PL-1535 and SL-1536, in the docs batch D1. Written by the planner (planner-replan). Evidence read at `origin/main` `60e9254c`
(#1242, 2026-10-08T12:40:57+01:00) and on the F35 plan's branch `wk1178-f35-leaf-plan` at
`c7621ca2` (PR #1051, PL-1520, minted in batch B4).

## Authority

- **The split**: the maintainer's entry "2026-10-08 13:00:11 BST — FD-1374 (silent mispricing)
  STAYS IN P2: DP-F35-1 split out as a P2 WK-1178 slice; F35's performance remainder carries; and
  fewer, consolidated status messages": "PL-1520's DP-F35-1 limb (the FD-1374 remedy) becomes a P2
  WK-1178 slice in the money/contract group; it is never on a cut-ladder rung."
- **The carry it corrects**: "2026-10-08 12:55:22 BST — P2 RE-PLAN RULED on the inventory
  (handover/p2-inventory-2026-10-09.md, at 60e9254c): F-1 (a), F-2 (b), F-3 (b), F-4 (a)+(b), F-5
  (a)/(b), F-6 (a)", F-3 (b).
- **One plan per Work**: "2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items 1, 3 and 5
  APPROVED; IN PRACTICE NOW; the files are amended through RFC 9479 P6 (the maintainer's
  amendment, by delegation)", L5. The form — a single-row Work plan, `kind: map`,
  `relates: [FD-1374, PL-1371]`, with the F35 plan and its ruling cited in the body in space form
  until they mint — is the lead's decision (b) of 2026-10-08.

## Goal

Close `FD-1374` (MEDIUM, "a SILENT mispricing path in shipped code"; register row FD-1374): a
rating step reads only names it declares. FR-246 is enforced at save and at compile on every
evaluating step type, an undeclared read is refused with its own code, already-compiled bundles
keep loading, `03`'s FR-246 row and its §4.1 example are corrected verbatim from the ruling, and
the four under-declaring fixtures are fixed. Done when `SL-1536` closes on its `LG-` and register
row FD-1374 carries the fix's merge sha.

## Acceptance Standard

Each item is checked by a command run from the repository root on the slice's merge tree.

1. **FR-246 is enforced** — the F35 plan's Acceptance item 2a, verbatim in substance:
   `uv run pytest -q packages/pricing-core/tests/test_rating_declared_reads.py` exits 0 and
   collects **6** tests: the two refusal tests and the extractor test, each seen red first by its
   cause; the control, proved on broken input; and the two `03` example tests, which extract §4.1's
   example verbatim from `03` and show it passes `RatingAlgorithm.model_validate` in full, then
   `compile_bundle` (stub payloads for its pins), then the declared-reads check. The `LG-` quotes
   each red's printed line; a red with another cause is a plan defect, not a pass.
2. **The compile-touching suites stay green** — Task 1A Step 7's predicate, re-run on the slice's
   base tree and its file list recorded:
   `git grep -l -E 'compile_bundle|validate_algorithm|/api/v1/rating-algorithms|rating\.compile|_run_compile_job|create_rating_algorithm' -- 'backend/tests/*.py'`,
   plus `backend/tests/test_regression_suites.py` by name; then
   `uv run pytest -q packages/pricing-core/tests/ packages/model-schema/tests/ <those files>` exits
   0, run in a gate slot.
3. **FD-1374's predicate prints 0 undeclared reads** over the merge tree (Task 1A Step 8; the
   sweep's tokenizer, `references.py`).
4. **The `03` text is the ruling's, byte for byte**: the `LG-` records `git diff` of
   `docs/specs/03-rating-engine.md` beside RL-1519's text for FR-246's row, the
   corrected §4.1 example and its Invariants note, and the `RATING_STEP_UNDECLARED_READ` owned-codes
   row; `grep -n 'RATING_STEP_UNDECLARED_READ' backend/src/app/errors.py` prints one line.
5. **The release note** (Task 1A, "A compile-time refusal only") is in the squash-commit body and
   the `LG-`.
6. **The gate is green**: the `CLAUDE.md` §11 commands, both halves, each exit 0, against
   `origin/main...<slice branch>`; `python3 scripts/audit-docs.py` prints "All checks passed."
   once the ids are minted.

## Global Constraints

- **Money is integer minor units or `Decimal` in the rating path, never float** (`CLAUDE.md` §7);
  this slice changes which algorithms compile, never a premium (Task 1A Step 7: "The scoring
  results do not change", though each fixture's bundle hash does).
- **`pricing-core` stays importable standalone** (`CLAUDE.md` §2; `.importlinter`):
  `references.py` and the check live in `pricing_core.rating`; the only backend file is the one
  `errors.py` registry line (RL-1519 (iii-a) (b)).
- **Spec and code in one commit** (`CLAUDE.md` §2): the ruled `03` text lands in Task 1A's commit,
  the maintainer's executor carve-out of 2026-10-01; the executor writes nothing of its own into
  `03`.
- **One PR per slice** (L1 (a')): code, tests, the `03` text, `SL-1536`'s status line and one `LG-`.
- **The `compile.py` serial set** (`PL-1371` §5 rule 4): never concurrent with another
  `compile.py` / `compile_bundle` editor.
- **`backend/src/app/errors.py` is a shared path** (the 2026-10-08 deltas audit, LOW): `SL-1472`
  (#1247, `7e1f44d3`, by `git diff --name-only origin/main...7e1f44d3`) also edits it, and WK-674
  Slices 5 and 6 add codes to it (PL-1537). This slice's one registry line is
  rebase-serialised: whichever merges second rebases onto the first.

## Tasks

Under L5 a Work plan's tasks are its slice rows. This row's steps are the F35 plan's **Task 1A
only** ("FR-246 enforced, red first; the four under-declaring fixtures fixed (DP-F35-1 (ii),
FD-1374)", PL-1520 at `c7621ca2`), Steps 1–8, as ruled by RL-1519.

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Lane | Size |
|---|---|---|---|---|---|---|
| 1 | `SL-1536` — WK-1178 fix slice — FD-1374: a rating step reads only the names it declares (FR-246 enforced) | PL-1520 Task 1A, Steps 1–8, as ruled by RL-1519 DP-F35-1 (ii) mechanism (a) refuse, scope (a) every evaluated field with `as_at` named, `consumes` mandatory (a); (iii-a) (b) `RATING_STEP_UNDECLARED_READ`, 422; (iii-b) (b) saved versions refused at next compile, compiled bundles grandfathered at reload. **Out of scope:** everything else in PL-1520 (Tasks 0–7 other than 1A, Spike S1, DP-F35-1 (b) / (i) / (iv), DP-F35-2 to -8), which carries to Phase 3 | `03` §3.5: FR-246; `03` §3.1: FR-212 (fixtures gain the producers FR-212 requires); register FD-1374 | RL-1519 and PL-1520 (working ids) minted (batch B4); the `compile.py` serial set free (below) | the lead's at GO | 1 |

**Three deviations from Task 1A as written**, each because the rest of PL-1520 carries:

- **D1 — no Spike S1.** Task 1A Step 3 says "Use the form Spike S1 verified against the engine. If
  S1 found a binding call …, use that instead of the tokenizer below". S1 is not run in P2, so the
  executor uses **the tokenizer below Step 3**, "the one FD-1374's sweep used", and the `LG-`
  records that choice.
- **D2 — no Task 1 Step 6.** Task 1A Step 8 ends "Then commit … and run Task 1 Step 6" (freeze the
  base corpus for the NFR-490 measurement). That belongs to the carried remainder; it is not run.
- **D3 — the plan's "Written for the recommended answers" branch is the ruled one.** RL-1519
  decided DP-F35-1 (ii) (a)/(a)/(a), (iii-a) (b) and (iii-b) (b), which are Task 1A's recommended
  branches; no dated delta to Task 1A is needed. If RL-1519 as minted differs from #1060's head
  (`758336a1`), the slice stops and reports.

**Sequencing.** The slice edits `compile.py` (`_check_declared_reads`, one `ALGORITHM_CHECKS`
entry) and its one `errors.py` registry line, and so is in the `compile.py` / `_Resolver` serial
set, which for this slice includes `errors.py`, with G2's chain (`SL-1472`, `SL-1387`,
SL 9495, `SL-1462`, `SL-1463`, `SL-1466`) and WK-1250's `SL-1340` / `SL-1341` and WK-675 S3. By the
priority rule (the entry "2026-10-08 12:59:36 BST — USER: VM days follow the weekly allowance (about
4–5 project days after each reset). RE-BASELINE: plan on 4-in-7; a ranked CUT LADDER; pause-proof
scheduling", item 2), **a ready G2 compile-set slice takes the set first; this slice takes it in
the first gap when none is ready, ahead of every non-G2 slice** (money and contract group). It is
**never on a cut-ladder rung** (13:00:11). Its interim guard stays until it merges: exit demo slice
(a)'s acceptance line, "every step's reads ⊆ its declared consumes" (register row FD-1374).

## Decision points

None open. Every branch point Task 1A names is ruled by RL-1519 (#1060); the
form of this plan is the lead's decision (b).

## Hand-off (not this plan's writes)

- The register minter appends R2 of `handover/replan-move-lines-2026-10-08.md` to FD-1374's
  Decision cell in the same batch.
- The lead lists this plan on WK-1178's roadmap row (L5).

## Self-review

- **Spec coverage.** FR-246 (the requirement FD-1374 is against) and FR-212 (the producer rule the
  fixture fix must satisfy) are the only ids; NFR-490, NFR-500, FR-258 belong to the carried
  remainder and are deliberately absent.
- **Placeholders.** None; the task source is named by plan, task and sha.
- **Rulings since the sweep.** #1060 (RL 9770, RL-1519) is the only open record ruling on this
  subject (lead, 2026-10-08: both in batch B4). Re-check at mint.
