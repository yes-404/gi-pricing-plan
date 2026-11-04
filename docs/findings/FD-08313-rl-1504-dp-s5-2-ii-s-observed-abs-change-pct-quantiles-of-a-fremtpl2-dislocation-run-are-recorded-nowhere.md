---
id: FD-8313
family: finding
title: RL-1504 DP-S5-2 (ii)'s observed abs_change_pct_quantiles of a freMTPL2 Dislocation Run are recorded nowhere
status: active
created: 2026-11-04   # drafted 2026-11-04 under working id 8313
owner: auditor
tree: db92a7bc0424059ed0aff4e5cebf445661c3be81   # origin/main when read
corrected_by: []
relates: [WK-673, RL-1504, LG-1582, CR-1981, SL-1389]
---

# FD-8313 — RL-1504 DP-S5-2 (ii)'s observed abs_change_pct_quantiles are recorded nowhere

## Finding

**LOW, owner WK-673.** `RL-1504` DP-S5-2 sets the FR-224 default `{quantile: 0.99, max_abs_change_pct: 10}`
on condition (ii): "S5's first freMTPL2 run reports the observed quantiles (DP-S5-4's fixed set) into
its ledger, and the default is re-read against them at the next checkpoint" (the Ruling's item 3
condition (ii), re-stated at item 7 "The re-read (condition (ii))"). SL-1389's ledger row 16
(`LG-1582:84`) reads "OWED: needs the seeded database and a Job". No later record holds the reading:
the maintainer's grep of the WK-1250 fresh gate's `demo.log` found 0 hits and its database was dropped
at END. Authority: the maintainer's entry "2026-11-04 10:00:29 GMT" in `to-lead.md` (a local channel
file), BLOCKER (2), "FD candidate A", from `CR-8310`.

## Evidence

`RL-1504` condition (ii); `LG-1582:84` (row 16, OWED); `CR-8310`'s candidate A; the maintainer's grep
of the gate's `demo.log` (0 hits), recorded in the entry above. No instrument was re-run by the
auditor.

## Severity

**LOW.** The default is a per-workspace policy setting that a stricter book overrides; no price moves
and the gate refuses unset or out-of-bounds deviation. What is missing is the falsification record the
ruling asked for.

## Disposition

Open, owner WK-673, **fix before close with an owner**. Discharge, ruled in the entry above: one
executor database window (single-tenant, a `createdb -T` copy, the guard quoted first and at END,
dead-port URLs elsewhere, nothing beside a timed stage) seeds the freMTPL2 sample, runs one
Dislocation Run by the WF-699 steps and quotes the run's `abs_change_pct_quantiles` with the run id
and the tree, as a dated addendum to `LG-1582` (its `:84` OWED line) and this record's Resolved
paragraph, with the default `{0.99, 10}` re-read against them in one line (stands / to be re-tuned, the
latter an OQ, not a change). If the window cannot run today, the FD is carried with owner WK-673 and
the discharge event the next gate's demo, the gate script's END dumping the quantiles before the
drop: the rehearsal gate Mon 16 Nov 2026 at the latest. Filed under working id 8313.
