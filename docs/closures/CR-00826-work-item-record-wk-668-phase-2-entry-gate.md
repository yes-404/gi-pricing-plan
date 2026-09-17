---
id: CR-826
family: closure
kind: work
title: Work-item record — WK-668 (Phase 2 entry gate)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-27
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/work/W8/README.md
---

# Work-item record — WK-668 (Phase 2 entry gate)

Closed 2026-08-27. Scope and evidence audited against origin/main `e2d32ac` (#287 merged).

## Scope

Derived from `docs/plans/PL-00817-wk-668-implementation-plan-spike-s1-s2-resolution-and-adr-706-confirmation.md` first, then evidenced. WK-668 is
the Phase 2 entry gate: it installs the GoRules ZEN engine, re-runs the S1 and S2
verification suites against the installed engine, confirms the requirements the spikes
produced (FR-273/274/275/276, NFR-502/501), and records a dated ADR-706
confirmation. The output is a decision record, not a build.

The plan's tasks T1-T7: T1 install + pin zen-engine; T2 re-run the S1 suite; T3 confirm the
requirements match the engine; T4 re-run the S2 latency suite; T5 confirm ADR-706; T6
record the success or failure decision; T7 close in the closure-audit format.

## Checklist

The `close-workstream` checklist version this close ran against: the 2026-08-24 skill text
(scope-first, evidence across the three axes, NFRs measured, findings with verdicts).
WK-668 is a research/confirmation workstream, so the audit's evidence is the recorded
measurement rather than pytest markers (close-workstream §0a).

## Evidence

| Requirement / deliverable | Evidence | Verdict |
|---|---|---|
| T1 — zen-engine installed + pinned | `docs/research/w8-spike-resolution.md` §T1 — wheel `zen_engine-0.53.0-cp312-...whl`, pinned to 0.53.0 (no delta from S1); `import zen` verified | delivered |
| T2/T3 — S1 suite re-run, requirements confirmed | §T2 — 21 checks, 0 failed: FR-273 (exactness + binding), FR-274 (division guarded), FR-275 (scale cap 28), FR-276 (vocabulary validated). Each result recorded beside its requirement | delivered |
| T4 — S2 latency re-run | §T4 — NFR-501: `nthread=1` p99 1.626 ms (3.3 % of the 50 ms budget), 0.34x all-cores at the tail; NFR-502: design rule confirmed, premise amended | delivered |
| T5 — ADR-706 confirmed at Phase 2 entry | `docs/adrs/ADR-00706-gorules-zen-engine-executes-rating-dags.md` Addendum 2026-08-27 — dated confirmation; "This addendum does not change the decision... WK-669 proceeds" | delivered |
| T6 — success decision recorded | §T4 + the ADR addendum: S1 and S2 resolutions hold; WK-669 proceeds | delivered |
| T7 — closure record + register | this record; no open finding to file in `docs/findings/register.md` (see Findings) | delivered |

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W8-1 | FR-273/274/275/276 and NFR-502/501 remain unevidenced by the pytest marker instrument (RATE: 2 of 78 evidenced) | accept — the requirements are Phase 2, to be built by WK-669-W14; WK-668's evidence is the recorded measurement (`docs/research/w8-spike-resolution.md`), which the close-workstream §0a standard admits | closed |
| F-W8-2 | NFR-502's ~1 ms premise was not reproduced on the verification machine (measured p99 0.070 ms, 0.14 % of budget) | resolved — the requirement is amended with a dated note (`03` NFR-502, #287); the design rule (validate inbound, never outbound) is unchanged | closed |

No open finding is carried to the global register: both findings are resolved or accepted,
and the Phase 2 requirements' unevidenced state is a Phase 2 status the roadmap records,
not a WK-668 defect.

## Sign-off

Owner: the maintainer (the ADR's decider). Auditor close-confirmation: 2026-08-27. WK-668 is
happy-to-close; WK-669 proceeds on the confirmed ADR-706 basis.
