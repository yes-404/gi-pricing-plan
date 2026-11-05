---
id: FD-2007
family: finding
title: NFR-476's fit time is unmeasured: the GBM arm did not complete inside a 2400 s wrapper on an 8-vCPU host; the fit's own time unknown; the harness's output was lost at the kill
status: active
created: 2026-11-05   # drafted 2026-11-05 under working id 8350
owner: auditor
tree: 2f108b1eda22a4835279cee9b4c9e305babe3662   # origin/main when read
corrected_by: []
relates: [WK-690, LG-1839, CR-1212, FD-2009]
---

# FD-2007 — NFR-476's fit time is unmeasured: the GBM arm did not complete inside a 2400 s wrapper on an 8-vCPU host; the fit's own time unknown; the harness's output was lost at the kill

## Finding

**MEDIUM, owner WK-690 (provisional: see Disposition), working id 8350.** Wording and authority: the maintainer's entries `to-lead.md` "2026-11-05 10:14:38 GMT" (S1 item A, first reading) and "2026-11-05 11:12:59 GMT" (its correction, which governs, and which re-titles this record and sets MEDIUM).

NFR-476 (`docs/specs/02-modelling.md:3033`) reads: "GBM: 5 M rows × 60 factors × 500 trees fits in < 20 min". On nfr-bench-1 session 1, item A ran `scripts/bench-model.py --only gbm --rows 5000000 --factors 60 --rounds 500` under the seat's own `timeout 2400`. The command was killed at the cap (cmd_rc 124, started 2026-11-05T09:33:06Z, killed 10:13:06Z).

**What the cap wrapped.** `bench_gbm` (`scripts/bench-model.py:388-414`) runs synthesise (5 M rows), `fit_gbm`, `compute_gbm_diagnostics`, `_gbm_passes` and `_artifact_size` inside ONE process, and `timeout 2400` wrapped that whole process. The proven fact is therefore that **the whole bench-model process (synthesis, fit, diagnostics, artifact) did not finish in 2400 s; the fit's own time is unproven**. It is not a reading of the fit against the 1200 s budget, and not "at least twice over".

**What the instrument printed.** The harness prints a `machine:` line and a line per phase. `itemA-fit.log` has none: stdout was block-buffered and lost at the kill, an instrument fault and not evidence. The correction of LG-1839's sentence "printed no harness output (the harness prints at completion)" is the dated line at the foot of LG-1839.

**What the host was.** The VM `nfr-bench-1` is a GCE e2-standard-8: `nproc` 8, 8 vCPU, 32 GB. No thread-cap variable was set (`OMP_*`, `MKL_*`, `OPENBLAS_*`, `POLARS_*`: none) and `bench-model.py` sets none, so XGBoost ran at its default `nthread` of all 8 (the maintainer's "2026-11-05 10:16:39 GMT" facts entry): threads are not the fault. Load1 was about 6 during the run, all 8 cores busy. The spec's host for this class of fit is a **16-core worker** (`02-modelling.md:3032` NFR-475, and `:3223`), not this VM; "environment of record" is the maintainer's phrase of 10:14:38, not the spec's, and the 11:12:59 correction withdraws it. The 8-vCPU result is a lower bound on a non-spec host.

**What the budget rested on.** The spec's own NOTE (`02-modelling.md:3249-3251`) projects 963 s at 5 M rows from ONE 75 000-row point (14.45 s wall) on 4 cores, linearly (about ×66.7), and says "The linearity is assumed, not shown". The 963 s is a projection, not a run, and the budget rested on that unmeasured linear extrapolation. One read-only lead ssh read at 09:49:33Z during the run showed load only.

## Evidence

- Command and times above, `LG-1839` Item A (nfr-bench-1 addendum, 2026-11-05, with its dated correction); logs `itemA-help.log` and `itemA-fit.log` on the VM.
- `scripts/bench-model.py:388-414` read at the tree in the front matter.
- Not run here: the auditor ran no benchmark. The fit's true time is for S2 item L (the maintainer's S2 brief fb6aaa2bb7f8 as accepted at 11:12:59): `python -u`, stdout and stderr captured, phases split (synthesis, fit, diagnostics), the fit read from its own timed line or from trees 500/500, never from a kill, the host stated, the 8-vCPU reading annotated as a lower bound and scaled to 16 cores only as a note, never as pass or fail.

## Severity

**MEDIUM** (the maintainer's re-ruling, "2026-11-05 11:12:59 GMT" ruling (a), overriding the 10:14:38 HIGH). It does not block CR 8314 as an unmet reading. It blocks only as an UNMEASURED NFR limb, if that limb is WK-690's (CLAUDE.md §13: NFRs are measured, not asserted).

## Disposition

Open, owner **WK-690 for now**, pending the ownership read of aud-wk690c, which quotes CR-1212 (e) and CR-754:163 verbatim in CR 8314 (ruling (b)). If CR-754:163 carries NFR-476's fit limb to "the slice with a 16-core worker" (WK-661's line), the fit limb is NOT WK-690's: this record is re-homed to that carrier by a dated line, CR 8314 records "fit limb carried by CR-754:163; its measurement on a 16-core host owed there", and WK-690's own NFR-476 limb is the EXPRESSION limbs, proven or not by S2 item M. If the quotes say otherwise this record stays WK-690's and blocks CR 8314 until item L measures the fit. Remedy paths after L: (a) a config fix if the fit path is mis-set (the S2 executor reads and quotes, before the run, the fit's `tree_method`, `nthread`, `max_bin`, the feature dtypes, and whether the 60 factors are categorical or one-hot); (b) if the configuration is right and the measured number stands, a section 14 proposal amending the spec's NOTE to a measured basis AND the budget, with the user's acceptance; (c) nothing carried silently. The process row "a capped-run finding states exactly what the cap wrapped and what the instrument printed, before any budget comparison" is in `docs/process/process-backlog.md`. Filed as working id 8350; minted FD-2007 in docs batch 11.
