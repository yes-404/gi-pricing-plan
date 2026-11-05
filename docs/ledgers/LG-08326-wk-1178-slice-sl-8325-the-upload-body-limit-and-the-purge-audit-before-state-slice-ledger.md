---
id: LG-8326
family: ledger
title: WK-1178 slice SL-8325 — FD-1802 the upload body limit, FD-1746 the purge audit's before state (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05
owner: executor
tree: 0000000000000000000000000000000000000000   # set at the last build-log entry
slice: SL-8325
phase: P2
work: WK-1178
plans: [PL-8324]
corrected_by: []
relates: [FD-1802, FD-1746, PL-8324, FR-450, FR-235, NFR-472, FR-81]
---

# LG-8326 — WK-1178 slice SL-8325: the upload body limit and the purge audit's before state

**GO:** to-lead "2026-11-05 10:20:55 GMT" (PLAN A @d7af4f25; DP-A1 64 MiB as a typed setting, nginx = limit + a small margin; DP-A2 dated clause on FR-450 and `PAYLOAD_TOO_LARGE`; DP-A3 XLSX expansion and gzip expand-first out; DP-A4 purge `before` = version ids and statuses).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-8324, "SL 8325 — the upload body limit and the purge before state", R0 to R3 and G. Requirements: `07` FR-450, FR-445 (read); `03` FR-235; `01` NFR-472, FR-81 (read). Register: FD-1802, FD-1746. **Departure from the plan, by the ruling:** the plan's G4 says one constant and no setting; DP-A1 as ruled makes the limit the typed setting `max_upload_body_mib` (`GIP_MAX_UPLOAD_BODY_MIB`, default 64) in `backend/src/app/config.py`, and `backend/tests/test_api_body_limit.py` holds its default. Those two files are outside the plan's Write set and are named here as the brief allows.

### Task list

- R0 spec text: `be64d5d5`.
- R1 the limit: red `ebe2527a`, green `d2490e18`, T4 and the wiring test `a2c45973`.
- R2 the proxy: red `a029e461`, green `0ecf4935`.
- R3 FD-1746: (DB window, pending).

### Gate

(The SOLO gate is the lead's.)

### Audit

(The auditor's.)

### Build log

**2026-11-05 (build, base d7af4f25).** Small runs through `run-small.sh`, each after waiting out rc 66 load refusals.

- Red, `backend/tests/test_api_body_limit.py` at `ebe2527a` (pass-through middleware): `3 failed, 2 passed`; the declared-length and boundary arms `assert 200 == 413`. The chunked arm first failed `assert 400 == 413` (the test's body was not valid multipart, so the parser answered), which is a fault in the test, not a red by cause. Fixed in `d2490e18` and re-proved red with the cap set to 10**9 bytes: `3 failed, 2 passed`, all three `assert 200 == 413`.
- Green at `d2490e18`: `5 passed`. At `a2c45973`: `9 passed`. Break proof of the wiring: with the `add_middleware(BodyLimitMiddleware …)` line commented out, `1 failed, 8 passed` (`test_the_application_caps_its_real_upload_route_before_authentication`); line restored.
- T5 red at `a029e461`: `deploy/lb.conf sets no client_max_body_size`, `1 failed, 32 passed, 1 skipped`. Green at `0ecf4935`: `33 passed, 1 skipped`. The skip is `frontend.nginx.conf`, not on this tree until D merges; the test holds it to the limit once it is.
