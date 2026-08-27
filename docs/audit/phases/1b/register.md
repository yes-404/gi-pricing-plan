# Phase register — 1b (Modelling Workbench)

The open findings Phase 1b carries. The phase register derives from `docs/roadmap.md` §6
and never repeats it: the roadmap owns workstream and phase status; this register records
only the findings a close carried.

Filed 2026-08-27 by the auditor's §13 evidence pass (scope derived from the specs first:
`scripts/scope-audit.py` across OVR, DATA, MODEL, GOV, PLAT at `84e98f5`; 374 requirements
in scope, 276 evidenced, 98 unevidenced). The plan `docs/plans/2026-08-27-phase1b-predecision.md`
enumerated F1-F12; the scope-audit adds F13-F22. Disposition default is FIX (maintainer
2026-08-27); deferrals state their strong reason.

| Finding id | Concerns | Work item | Decision |
|---|---|---|---|
| F1 | `validate.py` "minor units" strings (`packages/pricing-core/src/pricing_core/data/validate.py:1007`, `:1084`) assert minor units on a statistic (auditor finding 6a) | W6b | fix before close (MD1) |
| F2 | `GET /api/v1/me/workspaces` and `POST /api/v1/me/workspace` routes | W6b-11 | discharged — `me.py:175`, `:210`, `record_switch` at `:263` |
| F3 | Batch C's change set has no test files; the demo postcondition check runs in the exit demo, not in pytest | W7-5 | fix before close (MD3) |
| F4 | `RatingVersionView` loading and network-error states untested | W7-5 | fix before close (MD4) |
| F5 | NFR-MODEL-14 has no `@pytest.mark.req` marker; measured 0.0480 fits/pass vs 0.06 budget | W7 | fix before close (MD5) |
| F6 | FR-DATA-57 (`unrun_layers`) — Phase 2 projection | W7-4 | defer — phase boundary; owner the Phase 2 validation-report successor |
| F7 | FR-DATA-52 (exposure-ordered top-20) — trigger-checked, unfired | W7-4 | defer — trigger has not fired; no consumer has asked for the work |
| F8 | The full `03` rating surface (compile, score, rate tables, deployment) | — | defer — phase boundary |
| F9 | The `wf-01` §4 surfaces the demo does not seed (bandings, Peril Structure, reconciliation) | W7-5 | defer — phase boundary (plan review 6 P1) |
| F10 | The `listRules` client gap (backlog #8) | W7 | discharged — `frontend/src/api/rules.ts:114` exports `listRules` with tests |
| F11 | FR-MODEL-63/98 (prediction) delivered-but-untested | W6b-6b | discharged — markers exist in the prediction path |
| F12 | The four frozen-plan items (backlog #103, #87, #127, #131) | — | fix before close (MD6) — resolve each item's work or record its disposition |

## Scope-audit additions (F13-F22)

The §13 evidence pass caught these unevidenced requirements that the plan's F1-F12 list
did not name. Each states its disposition; the strong-reason deferrals name the boundary.

| Finding id | Concerns | Decision |
|---|---|---|
| F13 | FR-OVR-22 (route reachability) — delivered by #136; enforced by the Vitest reachability suite (`frontend/src/router/__tests__/reachability.test.ts`), which the Python marker instrument cannot see; positive control + mutation verified in the #259 audit | accept — alternative instrument (Vitest), verified |
| F14 | FR-OVR-20 (`_minor` suffix rule) — enforced by `scripts/audit-docs.py` check 12, which cites FR-OVR-20 | fix before close — make the enforcement visible to `req-coverage.py` with a test naming FR-OVR-20 |
| F15 | FR-OVR-21 (§5.3 cell is prose) — the declared-prose affordance; binding surface is the generated contract | accept — the rule is the contract's declared-prose affordance |
| F16 | FR-PLAT-55 (browser PKCE) — delivered by W6b-10; enforced by the Vitest auth suite (`frontend/src/auth/__tests__/session.test.ts`) | accept — alternative instrument (Vitest) |
| F17 | FR-PLAT-59 (no IdP in prod) — delivered by W6b-14; the provider ships behind the compose `auth` profile; `tests/test_repository_invariants.py:94` names the rule | fix before close — add a marker to the repository-invariant test |
| F18 | NFR-PLAT-4 (compose stack to usable state < 5 min) — measured 27 s vs 300 s (roadmap :298); deliberately not a test | accept — measured, recorded |
| F19 | FR-OVR-9 (pseudonymisation) — ingestion enforces the refusal (FR-DATA-13/41 path); the modelling PII guard gap (a `Factor.prohibited` derivation) is a separate roadmap finding with a §14 disposition | accept — enforcement exists; the PII-guard gap is recorded in the roadmap |
| F20 | Cross-cutting OVR without markers — FR-OVR-2 (JSON-serialisable), FR-OVR-4 (audit same-txn), FR-OVR-10 (long-ops are Jobs), FR-OVR-11 (OpenAPI surface), FR-OVR-12 (UTC), FR-OVR-14 (maturity refs), FR-OVR-15/16 (tenant isolation, provenance — ADR-0006), FR-OVR-19 (error-code check — `audit-docs.py` check 10 is the mechanism) | accept — conventions, ADRs and the audit's own checks are the enforcement; a marker pass is out of scope for Phase 1b |
| F21 | Measured NFRs without markers — NFR-DATA-1/2 (ingest/validate budgets, `scripts/bench-data.py`), NFR-MODEL-1..5, 10..13 (fit/diagnostics budgets, `test_model_nfrs.py` docstrings) | accept — measured, not asserted; a timing assertion fails on shared runners for reasons unrelated to the code (W4/W5 close-record reasoning) |
| F22 | Phase 2/3/4 unevidenced requirements — FR-MODEL-6, 40, 82, 115, 121 (W30 / Phase 2 / Phase 3-W31 owners); FR-PLAT-15, 60, 61, 64 (Phase 4 scheduled work), FR-PLAT-23..27 (Phase 2 backups/secrets), FR-PLAT-28, 29, 31 (Phase 2 environments, W14), FR-PLAT-32..36 (Phase 2 deploy), FR-PLAT-49, 50 (Phase 2 rate limit/webhooks), FR-PLAT-56 (W14 tenant deployment); FR-GOV-16, 17, 18, 27..35, 38..45 (Phase 2/3 governance); NFR-OVR-1..8, 10, 11; NFR-PLAT-1, 2, 5, 6, 8, 9, 10; NFR-GOV-1, 3..7 | defer — phase boundary (CLAUDE.md §0 forbids building a later phase's capability now); owners are the later-phase workstreams named in the roadmap |

## Carried to the global register

F6-F9 and F22 defer to later phases with named owners; each is carried to
[`../../register.md`](../../register.md). F13, F15, F16, F18-F21 are accepted with their
stated evidence; the acceptance is recorded here and in the close record.
