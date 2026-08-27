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
| F1 | `validate.py` "minor units" strings (`packages/pricing-core/src/pricing_core/data/validate.py:1007`, `:1084`) assert minor units on a statistic (auditor finding 6a) | W6b | resolved 2026-08-27 (#280) — the strings no longer assert minor units |
| F2 | `GET /api/v1/me/workspaces` and `POST /api/v1/me/workspace` routes | W6b-11 | discharged — `me.py:175`, `:210`, `record_switch` at `:263` |
| F3 | Batch C's change set has no test files; the demo postcondition check runs in the exit demo, not in pytest | W7-5 | resolved 2026-08-27 (#280) — `backend/tests/test_demo_postconditions.py` exercises the check in pytest |
| F4 | `RatingVersionView` loading and network-error states untested | W7-5 | resolved 2026-08-27 (#280) — loading test added; the RFC 9457 problem-alert test existed (#273) |
| F5 | NFR-MODEL-14 has no `@pytest.mark.req` marker; measured 0.0480 fits/pass vs 0.06 budget | W7 | resolved 2026-08-27 (#280) — marker added; `req-coverage.py` now reports NFR-MODEL-14 |
| F6 | FR-DATA-57 (`unrun_layers`) — Phase 2 projection | W7-4 | defer — phase boundary; owner the Phase 2 validation-report successor |
| F7 | FR-DATA-52 (exposure-ordered top-20) — trigger-checked, unfired | W7-4 | defer — trigger has not fired; no consumer has asked for the work |
| F8 | The full `03` rating surface (compile, score, rate tables, deployment) | — | defer — phase boundary |
| F9 | The `wf-01` §4 surfaces the demo does not seed (bandings, Peril Structure, reconciliation) | W7-5 | defer — phase boundary (plan review 6 P1) |
| F10 | The `listRules` client gap (backlog #8) | W7 | discharged — `frontend/src/api/rules.ts:114` exports `listRules` with tests |
| F11 | FR-MODEL-63/98 (prediction) delivered-but-untested | W6b-6b | discharged — markers exist in the prediction path |
| F12 | The four frozen-plan items (backlog #103, #87, #127, #131) | — | resolved 2026-08-27 — each shipped by its PR; see the F12 dispositions below |

## F12 — the four frozen-plan items, resolved 2026-08-27

Each of the four items existed only in a frozen plan. Each is resolved by the PR that
shipped it; this section is the durable disposition the frozen plans cannot carry.

| Item | Disposition |
|---|---|
| #103 — the two testing rules the prediction slice found | resolved — shipped by PR #103, merged 2026-08-18 (`.claude/skills/python-test`) |
| #87 — vendored `ui-ux-pro-max` and the invariant its data files tripped | resolved — shipped by PR #87, merged 2026-08-17 (`.claude/skills/ui-ux-pro-max`) |
| #127 — the `ci-watcher` agent | resolved — shipped by PR #127, merged 2026-08-21 (`.claude/agents/ci-watcher.md`) |
| #131 — `python-test`: the test database cannot be truncated | resolved — shipped by PR #131, merged 2026-08-22 (`.claude/skills/python-test`) |

## Scope-audit additions (F13-F22)

The §13 evidence pass caught these unevidenced requirements that the plan's F1-F12 list
did not name. Each states its disposition; the strong-reason deferrals name the boundary.

| Finding id | Concerns | Decision |
|---|---|---|
| F13 | FR-OVR-22 (route reachability) — delivered by #136; enforced by the Vitest reachability suite (`frontend/src/router/__tests__/reachability.test.ts`), which the Python marker instrument cannot see; positive control + mutation verified in the #259 audit | accept — alternative instrument (Vitest), verified |
| F14 | FR-OVR-20 (`_minor` suffix rule) — enforced by `scripts/audit-docs.py` check 12, which cites FR-OVR-20 | resolved 2026-08-27 (#280) — `tests/test_repository_invariants.py:137` names FR-OVR-20; `req-coverage.py` now reports it |
| F15 | FR-OVR-21 (§5.3 cell is prose) — the declared-prose affordance; binding surface is the generated contract | accept — the rule is the contract's declared-prose affordance |
| F16 | FR-PLAT-55 (browser PKCE) — delivered by W6b-10; enforced by the Vitest auth suite (`frontend/src/auth/__tests__/session.test.ts`) | accept — alternative instrument (Vitest) |
| F17 | FR-PLAT-59 (no IdP in prod) — delivered by W6b-14; the provider ships behind the compose `auth` profile; `tests/test_repository_invariants.py:94` names the rule | resolved 2026-08-27 (#280) — `@pytest.mark.req("FR-PLAT-59")` added to the repository-invariant test; `req-coverage.py` now reports it |
| F18 | NFR-PLAT-4 (compose stack to usable state < 5 min) — measured 27 s vs 300 s (roadmap :298); deliberately not a test | accept — measured, recorded |
| F19 | FR-OVR-9 (pseudonymisation) — ingestion enforces the refusal (FR-DATA-13/41 path); the modelling PII guard gap (a `Factor.prohibited` derivation) is a separate roadmap finding with a §14 disposition | accept — enforcement exists; the PII-guard gap is recorded in the roadmap |
| F20 | Cross-cutting OVR without markers — FR-OVR-2 (JSON-serialisable), FR-OVR-4 (audit same-txn), FR-OVR-10 (long-ops are Jobs), FR-OVR-11 (OpenAPI surface), FR-OVR-12 (UTC), FR-OVR-14 (maturity refs), FR-OVR-15/16 (tenant isolation, provenance — ADR-0006), FR-OVR-19 (error-code check — `audit-docs.py` check 10 is the mechanism) | accept — conventions, ADRs and the audit's own checks are the enforcement; a marker pass is out of scope for Phase 1b |
| F21 | Measured NFRs without markers — NFR-DATA-1/2 (ingest/validate budgets, `scripts/bench-data.py`), NFR-MODEL-1..5, 10..13 (fit/diagnostics budgets, `test_model_nfrs.py` docstrings) | accept — measured, not asserted; a timing assertion fails on shared runners for reasons unrelated to the code (W4/W5 close-record reasoning) |
| F22 | Phase 2/3/4 unevidenced requirements — FR-MODEL-6, 40, 82, 115, 121 (W30 / Phase 2 / Phase 3-W31 owners); FR-PLAT-15, 60, 61, 64 (Phase 4 scheduled work), FR-PLAT-23..27 (Phase 2 backups/secrets), FR-PLAT-28, 29, 31 (Phase 2 environments, W14), FR-PLAT-32..36 (Phase 2 deploy), FR-PLAT-49, 50 (Phase 2 rate limit/webhooks), FR-PLAT-56 (W14 tenant deployment); FR-GOV-16, 17, 18, 27..35, 38..45 (Phase 2/3 governance); NFR-OVR-1..8, 10, 11; NFR-PLAT-1, 2, 5, 6, 8, 9, 10; NFR-GOV-1, 3..7 | defer — phase boundary (CLAUDE.md §0 forbids building a later phase's capability now); owners are the later-phase workstreams named in the roadmap |

## Carried to the global register

F6-F9 and F22 defer to later phases with named owners; each is carried to
[`../../register.md`](../../register.md). F13, F15, F16, F18-F21 are accepted with their
stated evidence; the acceptance is recorded here and in the close record.

## Auditor close-confirmation (T9, 2026-08-27)

The auditor reviewed the register and the UAT evidence at `9799947` and confirms Phase 1b
**can go to the close decision**:

- The seven fix-before-close findings (F1, F3, F4, F5, F12, F14, F17) all landed in #280
  and are evidenced (F5, F14, F17 confirmed by `req-coverage.py`; F1, F3, F4 by their
  tests; F12 by the register dispositions).
- The five deferrals (F6-F9, F22) each carry a strong reason — a phase boundary or an
  unfired trigger — and named owners.
- The exit-demo UAT (`docs/audit/exit-demo-uat.md`) shows all seven checklist items
  passing; the seed reached a usable state in **90 s** against the 300 s NFR-PLAT-4
  budget (30 %).

Remaining findings: none blocking. The register's F-rows were updated 2026-08-27 to
reflect the landed fixes. Confirmation recorded.

## UAT findings (F23-F25), recorded 2026-08-27

The hands-on UAT found three defects. Two are fixed; one is documented with its root
cause.

| Finding id | Concerns | Resolution |
|---|---|---|
| F23 | Empty `client_id` — `demo_env()` never set `GIP_OIDC_CLIENT_ID`, so `/api/v1/auth/config` returned `client_id ""` and the browser login threw `Error: client_id` at sign-in | fixed — PR #283 sets `GIP_OIDC_CLIENT_ID: gi-pricing-frontend` and pins it in the demo test |
| F24 | Localhost-only redirect — the SPA client whitelisted only `http://localhost:5173/*`; a browser reaching the demo via a port-forward bound to `127.0.0.1` sends `redirect_uri=http://127.0.0.1:5173/callback`, which the provider rejects | fixed — PR #283 whitelists both `localhost` and `127.0.0.1` in `redirectUris` and `webOrigins` |
| F25 | Seed-wipe — the pytest suite's session-scoped autouse fixture (`backend/tests/conftest_db.py`) truncates the whole shared database after each run, wiping any `scripts/demo.py` seed | re-seeded — `uv run python scripts/demo.py` again; root cause documented in `backend/tests/conftest_db.py` (the fixture's own docstring: "This empties the whole database, including any `scripts/demo.py` seed") and `.claude/skills/python-test` |

## Phase closure — maintainer sign-off, 2026-08-27

Phase 1b is closed by the maintainer on 2026-08-27. The exit criterion (the core `wf-01`
journey over HTTP) is met, the demo UAT is signed off, and every finding F1-F25 has a
disposition. The closure record is [`README.md`](README.md).
