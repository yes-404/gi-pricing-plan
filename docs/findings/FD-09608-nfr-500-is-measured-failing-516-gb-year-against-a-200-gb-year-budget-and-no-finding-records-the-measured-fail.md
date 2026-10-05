---
id: FD-9608
family: finding
title: NFR-500 is measured failing, 516.07 GB/year against a 200 GB/year budget, and no finding records the measured fail
status: active
created: 2026-10-05
owner: auditor
tree: cdaaa57345cb765f96034ce1ec2733c338f1c3cd
corrected_by: []
relates: [WK-1178, WK-671, NFR-500, FR-259, F35, F37, F55, OQ-1373, CR-926, CR-927, CR-1247]
---

# FD 9608 (working id) — NFR-500 is measured failing, and no finding records it (WK-1178)

## Finding

**Severity MEDIUM, owner WK-1178, resolved before the P2 close.** All three are the
maintainer's (by delegation), in the entry headed *"2026-10-05 15:37:35 BST — CORRECTION to my
15:33:57 routing (a): REVERSED; the skill, conftest and test move together into PL 9617; NFR-500
finding MEDIUM; WK-1250"* (`channel/to-lead.md`, local). Its NFR-500 paragraph, verbatim:

> NFR-500: NO finding records the MEASURED 516.07 GB/yr against the 200 GB/yr budget (only CR-926/927/1247 carry the figure). FILE one in the next batch: severity MEDIUM, not HIGH. It is a storage-budget NFR (trace storage), not correctness or an exit-demo step, and G4 is met by "measured, carried with a named owner" as well as by a pass. Owner WK-1178, grouped with F37 (no storage format) and F55 (TraceStep carries the full context), since the remedy is shared. Its resolution (fix, or carry with a dated maintainer acceptance) is due before the P2 close.

**The requirement** (`docs/specs/03-rating-engine.md:1341`, NFR-500): *"Trace storage: 1 %
sampling of 50 M annual quotes stays under 200 GB/year with the sampled-trace schema."*

**The measured fail.** WK-671's Task 4D measured real serialised `Trace` bytes at five step
counts (`docs/research/w11-task-4d-nfr-rate-12.md`, `scripts/bench-trace-size.py`, `dc451d5`/#501)
and projected the ~200-step reference structure at NFR-500's own volume: 500,000 sampled quotes
× 1,032,137 B = **516.07 GB/year** (the note's own arithmetic, `:129-130`) against the 200
GB/year budget, **about 2.58× over**. The figure is a lower bound on real volume: it excludes
FR-259's 100 % decline-and-error sampling (`CR-927` §10.3).

**What exists and what does not.**

| Record | What it holds | Records the measured fail as a finding? |
|---|---|---|
| `docs/closures/CR-00926-*.md:51` | one table row, "measured and **failing**, 516.07 GB/year, ~2.58x" | no, a closure record's plan-review table |
| `docs/closures/CR-00927-*.md:324` (§10.3, and the verdict at `:344`) | the measurement table, "PROJECTED OVER, ~2.58×" | no, a closure record |
| `docs/closures/CR-01247-*.md:760` | "It is measured **failing**: 516.07 GB/year, about 2.58×" | no; `:765-771` record the *spec defect's* ownership (`CR-1212` G4 (c): F37 "goes to a WK-1178 spec slice") |
| `docs/findings/register.md` F37 row (`:79`) | the missing storage format: 1,032,135 B uncompressed, 14,523 B under gzip -6 | **no**: it carries the trace *size*, and its decision is "Amend NFR-500", a spec amendment; it never states the 516.07 vs 200 figure or that the NFR fails |
| `docs/findings/register.md` F55 row (`:96`) | `TraceStep` carries the full accumulated context, the largest driver | **partly, in passing**: it calls the cause "the single largest driver" of the projection's "~2.58× the 200 GB/year budget" verdict, but not the 516.07 GB figure, and its own decision is the `TraceStep` trim, not the budget miss |
| `OQ-1373` (`03` `:1369`) | "it is measured failing, about 2.58×", and asks what "sampled-trace schema" names | no, an open question about the wording, not a finding |

The figure therefore lives in three closure records and one OQ, and in no row of the register as a finding of its own (F55's row mentions "~2.58×" only as the size of the overage its cause drives),
which is where `CLAUDE.md` §13 and G4 look for a requirement's verdict. A closure record is
frozen at its date; nothing re-reads it when the phase closes. (Re-confirmed at `cdaaa573`:
`git grep -n -E '516\.07|2\.58' cdaaa573 -- docs/findings` returns one line, `register.md:96` (F55's "~2.58×"), and no line carries `516.07`; and
`git log -S516.07 origin/main -- docs` touches only `dc451d50`, `ba658943`, `18831bda` and the
W37-6 migration run `71f5a220`.)

## Why it matters

1. **G4 asks for measured, or carried with an owner.** A measured fail that sits only in a
   frozen closure table is neither: no owner is named against the fail itself. F37 has an owner
   for the *wording*; nobody owns the *budget miss*.
2. **The two fixes are different decisions.** Amending NFR-500 to name a compressed encoding
   (F37's decision; OQ-1373 options b/c) would turn 516 GB into about 7.3 GB/year at the
   measured 14,523 B/trace (500,000 × 14,523 B, arithmetic from the F37 figure, not re-measured),
   and passes the budget as written. Trimming `TraceStep` (F55) makes the uncompressed trace
   smaller. Either, both, or a dated acceptance of the miss is the maintainer's choice; the
   finding exists so the choice is made on a record.
3. **It is the same lever as F35 and F37.** One trim of `consumed`/`produced` helps NFR-490,
   NFR-500 and F55 together; deciding them separately would repeat that work.

## Requirement

NFR-500 (`03-rating-engine.md:1341`), with FR-259 (`:176`, the sampling policy it sizes).

## Proposed remedy (a proposal, not a decision)

Resolve before the P2 close, one of: **fix** (the F35/F55 trim and/or a named persisted
encoding, with NFR-500 amended per OQ-1373 and the budget re-measured on the persisted bytes),
or **carry with a dated maintainer acceptance** of the measured fail. Either way the
re-measurement uses `scripts/bench-trace-size.py` and the 100 % decline/error floor is stated.
The OQ-1373 decision rules the schema question; this finding is not a second route to it.

## Evidence

1. Requirement: `docs/specs/03-rating-engine.md:1341`, at `cdaaa573`.
2. Measurement: `docs/research/w11-task-4d-nfr-rate-12.md:129-130`; `docs/closures/CR-00927-*.md:320-346`.
3. Records of the figure: `CR-00926-*.md:51`, `CR-00927-*.md:324`, `CR-01247-*.md:760`. The
   brief's `CR-927 :115` is not one: that row reads "not started" and carries no figure.
4. Ownership of the spec defect: `CR-01247-*.md:765-771`; F37 (`register.md:79`).
5. Absence: `git grep -n -E '516\.07|2\.58' cdaaa57345cb765f96034ce1ec2733c338f1c3cd -- docs/findings`
   returns exactly one line, `register.md:96` (F55's row, the "~2.58×" mention above); no essay under
   `docs/findings/` and no other register row carries either figure, and `516.07` itself is in none.
6. Not re-measured in this finding; nothing was run.

## Disposition

Open. Filed by the auditor, 2026-10-05; severity MEDIUM, owner WK-1178 and the deadline are
the maintainer's (by delegation), ruled in the entry named above and noted in the entry headed *"2026-10-05 15:44:00 BST — #1167 check: NO duplicate (accepted); the residual MUST be traced; the coverage test goes to PL 9616; FD 9608 noted"* ("FD 9608 (#1169 @3ded7319; MEDIUM, WK-1178, before the P2 close; my 15:37:35 quoted): noted, in the next batch. The evidence corrections (CR-926 :51, CR-927 :324 with verdict :344, CR-1247 :760; F55 :96's "~2.58×" in passing) are right."). Resolution: fix, or a dated
maintainer acceptance, before the P2 close.

**Re-verified at `origin/main` 137bc817** (2026-10-05 16:58:12 BST): `03-rating-engine.md` :1341 (NFR-500), :176 (FR-259), :1369 (OQ-1373); `w11-task-4d-nfr-rate-12.md:129-130`; `CR-926 :51`, `CR-927 :324` and `:344`, `CR-1247 :760`; `register.md` :79 (F37) and :96 (F55) all resolve as written, and `git grep -n -E '516\.07|2\.58' origin/main -- docs/findings` still returns the one line, `register.md:96`.
