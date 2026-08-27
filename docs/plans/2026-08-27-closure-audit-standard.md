# Closure Audit Standard Implementation Plan — docs/audit, §14 rule, NT-0005 custody

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** File the closure-audit standard. It has three parts: a `docs/audit/` structure that records per-work-item and per-phase closures, a third rule in `CLAUDE.md` §14, and durable custody for the seven NT-0005 items.

**Architecture:** A hybrid complement. `close-workstream` and `phase-review` stay the binding procedures. `docs/audit/` already holds the archive (the closure records, plan reviews and retrofit list moved there by NT-0009). This plan adds the record layer: per-work-item and per-phase records, two checklists, and two registers. The checklists point at the skills. No new id family is minted. Work items and findings reuse existing ids.

**Tech Stack:** Markdown, `scripts/audit-docs.py`, `CLAUDE.md`, `docs/specs/00-overview.md`, `docs/open-questions.md`, `docs/roadmap.md`.

**Spec:** `NT-0008` (the structure) · `NT-0005` (the seven items). The maintainer's three rulings on NT-0008's acceptance points, 2026-08-27.

**Highest ids:** This plan mints one id. Next free: `OQ-OVR-17`.

## Global Constraints

- The gate has two halves. Both must pass before a push (CLAUDE.md §11).
- Write prose in ASD-STE100. Code, identifiers and file paths stay unchanged.
- A filed plan stays frozen at its date. The plan file commits on the branch, never copied back.
- Requirement ids are permanent. Append, never renumber (CLAUDE.md §5).
- Every spec change runs `python3 scripts/audit-docs.py` before commit (CLAUDE.md §0).
- `docs/roadmap.md` §6 owns component and workstream status. A register that restates it will drift. The phase register must derive from or point at the roadmap, never repeat it.
- The audit reads `docs/` only. Every new `docs/audit/` file must pass the docs audit: defined requirement ids, resolving relative links, well-formed table rows.
- Evidence is write-once. A record that changes after the fact must say it changed.

---

## The three rulings (maintainer, 2026-08-27)

| Point | Ruling |
|---|---|
| (a) Replace versus complement | Hybrid complement. `close-workstream` and `phase-review` stay binding. `docs/audit/` adds per-work-item records and registers. The checklists point at the skills |
| (b) Id family | Reuse existing ids. No new `WI-###` / `P#` / `F-<parent>-n` family |
| (c) Critical-blocking rule | A third rule in `CLAUDE.md` §14. No severity vocabulary |

---

## Findings (verified 2026-08-27 against origin/main)

**F1. `docs/audit/` exists as the archive, with no record structure.** NT-0009's slim (`#274`) created `README.md`, `closure-records.md`, `plan-reviews.md` and `retrofit-impossible.md`. The record layer — `checklists/`, `work/`, `phases/`, `register.md` — does not exist. The README's closing line says the NT-0008 structure stays open until the three acceptance points are answered. They were answered 2026-08-27, so the line is stale.

**F2. The seven NT-0005 items have no durable home, with two exceptions.** Item (c) expired: `W6b-1b` shipped as `#194` and `W6b-9` shipped its checks. Item (g) is placed: the roadmap §10 note of 2026-08-26 records that all twenty unplaced questions were placed or recorded, including the eight item (g) names. The remaining five — (a) the OQ next-free marker, (b) the §5.3↔§5.6 route check, (d) the two summary lines, (e) the §5.6 authoritative column, (f) the workflow-content OQ — are still unfiled.

**F3. The two summary lines are still unconditional.** `scripts/audit-docs.py:454` appends `{len(in_file)} open questions, all mirrored` and `:585` appends `{len(owner)} error codes, ownership exclusive`, each after its own failure loop. Check 21's pattern is the established fix: the verdict goes in the summary line.

**F4. `docs/open-questions.md` has no next-free marker.** The plans directory has the convention (`docs/plans/README.md:55-56`). The open-questions register does not. Allocating an `OQ-` id still means scanning the file by hand.

**F5. The §5.3↔§5.6 reconciliation does not exist.** No `audit-docs.py` check compares the Route column of a module's §5.3 with the Route column of `00` §5.6. Item (e), which side is authoritative, must be written before the check. Then a failure message can say which side to fix.

---

## Scope

| Deliverable | Where | Task |
|---|---|---|
| The `docs/audit/` structure | `docs/audit/` | T1-T4 |
| The §14 rule text | `CLAUDE.md` §14 | T5 |
| NT-0005 custody | per item | T6 |

---

## Tasks

### T1. `docs/audit/README.md` — the standard

**Files:**
- Modify: `docs/audit/README.md`

- [ ] Update the intro to name both roles: the archive (NT-0009) and the record layer (this plan).
- [ ] Replace the stale closing line with the decided structure. The three acceptance points are answered 2026-08-27.
- [ ] State the hybrid complement: `close-workstream` and `phase-review` are the binding procedures. `docs/audit/` records what they close.
- [ ] Link the two checklists by their paths: `checklists/work-item-close.md` and `checklists/phase-close.md`.
- [ ] State the conventions: existing-id naming, evidence write-once, checklist versioning, ISO dates, secrets redaction, a tag at phase close.
- [ ] Link the global register by its path: `register.md`.
- [ ] Run `python3 scripts/audit-docs.py`.

### T2. `docs/audit/checklists/work-item-close.md`

**Files:**
- Create: `docs/audit/checklists/work-item-close.md`

- [ ] Point at the procedure: follow the [`close-workstream`](../../.claude/skills/close-workstream/SKILL.md) skill. This checklist adds the record, not the audit.
- [ ] Write the record template with the sections the maintainer confirmed: Scope, Checklist, Evidence, Findings, Sign-off.
- [ ] Name a work item by its existing id: a PR number, a slice id, or a workstream id. The record directory is `docs/audit/work/<existing-id>/`.
- [ ] Write the Finding rows: each row names the requirement or artifact id it concerns, states the decision (fix before close, carry forward with an owner, accept), and states the status (`closed` or `closed-with-findings`).
- [ ] State that a carried finding is copied to the phase register and the global register.
- [ ] Run `python3 scripts/audit-docs.py`.

### T3. `docs/audit/checklists/phase-close.md`

**Files:**
- Create: `docs/audit/checklists/phase-close.md`

- [ ] Point at the procedure: follow the [`phase-review`](../../.claude/skills/phase-review/SKILL.md) skill. This checklist adds the roll-up record, not the review.
- [ ] Write the record template with the sections the maintainer confirmed: Scope reconciliation, Finding roll-up, Cross-cutting checks, Retrospective, Evidence, Sign-off.
- [ ] Write the finding roll-up: every carried finding is resolved, accepted with an owner, or re-planned. This is the §13 four-verdict discipline in table form.
- [ ] Name a phase by its existing id (`1a`, `1b`, `2`). The record directory is `docs/audit/phases/<phase>/`.
- [ ] State that the phase register derives from `docs/roadmap.md` §6 and never repeats it.
- [ ] Run `python3 scripts/audit-docs.py`.

### T4. The registers and the example records

**Files:**
- Create: `docs/audit/register.md`
- Create: `docs/audit/work/.gitkeep` or a first example record
- Create: `docs/audit/phases/.gitkeep` or a first example record

- [ ] Write `docs/audit/register.md`: the global list of open findings, one row per finding, keyed by the requirement or artifact id it concerns. Each row names the work item, the phase, and the decision.
- [ ] Create one example work-item record under `docs/audit/work/` as the fill-in-the-blank. Use a real, closed item as the exemplar, for example the W7 plan (`pr-265`).
- [ ] Create one example phase record under `docs/audit/phases/` with a `register.md`. Use a real phase as the exemplar, for example `1b`.
- [ ] Verify every example record passes the docs audit: defined ids, resolving links, well-formed tables.
- [ ] Run `python3 scripts/audit-docs.py`.

### T5. `CLAUDE.md` §14 — the third rule

**Files:**
- Modify: `CLAUDE.md` §14 (the two binding rules)

- [ ] Add the third rule to §14. The rule text:
  > **Nothing starts in the next phase while an open finding from the current phase lacks a resolution.** A finding has a resolution when the close fixes it, carries it forward with a named owner, or accepts it. The phase closure record lists every open finding with its resolution.
- [ ] No severity vocabulary. The rule names the resolution state, not a severity level.
- [ ] Verify the rule reads as binding. It uses `must`-grade language with no hedge.

### T6. NT-0005 custody — the seven items

**T6.1. Item (a): the OQ next-free marker.**

- [ ] Add a next-free marker block to the `docs/open-questions.md` header, mirroring the plans convention. One line per family, for example: `Highest ids in use: OQ-OVR-16, OQ-DATA-15, OQ-MODEL-43, OQ-PLAT-17. Next free: OQ-OVR-17.`
- [ ] Verify the marker names the current ceilings. Item (f) mints `OQ-OVR-17`, so the OVR line must say `Next free: OQ-OVR-17`.

**T6.2. Item (e): the §5.6 authoritative column.**

- [ ] Add a dated note to `docs/specs/00-overview.md` §5.6: the Route column is the canonical route. A module's §5.3 Route cell must agree with it. `00` §5.6 names the canonical views and routes (FR-OVR-22), so it governs.
- [ ] State the counterexample: two named views on one route are two §5.3 rows carrying the same route, not one missing row. A check must diff routes, never view names.
- [ ] Run `python3 scripts/audit-docs.py`.

**T6.3. Item (b): the §5.3↔§5.6 route check.**

- [ ] Add a check to `scripts/audit-docs.py` that diffs the Route column of each module's §5.3 against the Route column of `00` §5.6.
- [ ] The check compares route strings, never view names. A named view appears in §5.3 with the route §5.6 gives it.
- [ ] The failure message names the side to fix: §5.6 is canonical, so a mismatch is a §5.3 error.
- [ ] Prove the check fails on broken input: add a route to a §5.3 table and confirm the check fires. Then remove it.
- [ ] Run `python3 scripts/audit-docs.py`.

**T6.4. Item (d): the two summary lines.**

- [ ] Fix `scripts/audit-docs.py:454` and `:585` with check 21's pattern. The verdict goes in the summary line, not just in the failure list.
- [ ] Each line reads its own failure list and reports the real count or the failure.
- [ ] Prove the fix on broken input: raise an unmirrored open question, run the audit, and confirm the summary line reports the failure instead of `all mirrored`.
- [ ] Run `python3 scripts/audit-docs.py`.

**T6.5. Item (f): the workflow-content OQ.**

- [ ] Next free: `OQ-OVR-17`. File the row in `docs/open-questions.md` under OVR: nothing checks that an `FR-` id cited by a workflow step contains what the step claims.
- [ ] Mirror the row in `docs/specs/00-overview.md` §10. `00` owns FR-OVR-17, the citation audit.
- [ ] State the options and a recommendation: a structural check, a review obligation at each close, or accepting the gap and recording it.
- [ ] Run `python3 scripts/audit-docs.py`.

**T6.6. Items (c) and (g): record the discharge.**

- [ ] Record in the close or the register that item (c) expired: `W6b-1b` shipped as `#194`, and `W6b-9` shipped its checks. No roadmap row is needed.
- [ ] Record that item (g) is placed: the roadmap §10 note of 2026-08-26 names the eight questions among the twenty placed or recorded.
- [ ] Verify the eight names appear in a §10 row or the recorded-decisions note. If any is absent, file it as a finding.

### T7. The gate

- [ ] Run both gate halves:
  - `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
  - `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
- [ ] Confirm the new audit check (T6.3) fires on broken input and is green on the clean tree.
- [ ] Confirm the fixed summary lines (T6.4) report the verdict on broken input.

---

## Verification

- `python3 scripts/audit-docs.py` passes with the new `docs/audit/` files in place.
- The new route check fails on a deliberately wrong §5.3 route.
- The fixed summary lines report a real failure instead of `all mirrored`.
- The §14 third rule reads with no severity vocabulary.
- All seven NT-0005 items have a home: five filed, two recorded as discharged.

---

## Sources

- `.claude/notes/0008-project-closure-audit-structure.md`: the structure and the three acceptance points.
- `.claude/notes/0005-deferred-items-with-no-durable-custody.md`: the seven items and their assessments.
- `.claude/skills/close-workstream/SKILL.md` and `.claude/skills/phase-review/SKILL.md`: the binding procedures the checklists point at.
- `CLAUDE.md` §14: the current two rules.
- `docs/plans/README.md`: the next-free marker convention.
- `scripts/audit-docs.py`: the summary-line defect and check 21's pattern.
- `docs/roadmap.md` §10: the gate table and the 2026-08-26 placement note.
