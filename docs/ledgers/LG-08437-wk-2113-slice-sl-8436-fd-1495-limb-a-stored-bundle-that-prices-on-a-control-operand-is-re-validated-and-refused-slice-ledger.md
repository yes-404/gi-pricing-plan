---
id: LG-8437
family: ledger
title: WK-2113 slice SL-8436 — FD-1495 limb B1/B2: a stored bundle that prices on a control operand is re-validated and refused (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-13
owner: executor
tree: 5d2189a363b7ec781b772f7fe3d3aae6f2c55385
phase: P3
work: WK-2113
slice: SL-8436
plans: []
corrected_by: []
relates: [SL-8436, FD-1495, SL-8429, LG-8430]
---

# LG-8437 — WK-2113 slice SL-8436: a stored bundle that prices on a control operand is re-validated and refused

Filed 2026-11-13 under working id 8437 (lead-reserved); executed by seat `exec-sl8436`, branch `sl-8436-stored-bundle-guard` stacked on S1 (`origin/sl-8429-fd1495-interaction-operands` @`5d2189a363b7ec781b772f7fe3d3aae6f2c55385`). Working ids in prose are in space form (SL 8436, LG 8437) until the mint; front matter keeps the hyphen form.

**GO:** the maintainer's "2026-11-13 21:17:39 GMT — Maintainer: S3 PLAN READ" (quoted whole below, with the "19:58:03 GMT — S3 RULED" and "21:23:21 GMT — S3 PREP READ" entries it builds on).

**MERGE-ACK:** not yet given.

## Tasks

### Scope

Quoting the slice's row, `docs/roadmap.md` `#### SL-8436` under WK-2113: stored Rating Version bundles that price on a `control`-intent operand (FD-1495, limb B1, aud-intent2 cell B1; and B2, the algorithm save). Design (C)+(B), fail closed, the maintainer's "19:58:03 GMT — S3 RULED"; the build plan is `scratch/pln-s3/S3-plan.md` (sha256 ef6b1adaed39) as amended by "21:17:39 GMT" and "21:23:21 GMT". Requirements: `FR-88` (`02`), `FR-240`, `FR-243`, `FR-267`, `FR-269`, `NFR-489`, `NFR-498` (`03`). Stacked on S1 (`origin/sl-8429-fd1495-interaction-operands` @`5d2189a363b7ec781b772f7fe3d3aae6f2c55385`); the re-merge is the lead's (stacking rule).

### Task list (what was built)

1. **Load-time guard** (S3-a). `refuse_control_in_features` (compile.py) is the ONE definition of "a model's consumed features reach a `control` Factor"; compile's `_refuse_control_factor_features` and the new `refuse_control_in_bundle` (runtime.py, called from `load_bundle` after the scorers are built) both call it, so they cannot drift. It covers a GLM and the model its offset reads.
2. **`hydrate`** (S3-b), `backend/src/app/platform/bundle_hydration.py`: the only caller of `load_bundle` in `backend/src`. It maps the refusal to a 409 `PlatformError` `CONTROL_FACTOR_IN_RATEABLE_PATH` (DP-2), evicts the hash from the slot, writes ONE Audit Event `rating_version.load_refused` per process per hash in its own `unit_of_work` (DP-1; it survives the refusal that raises), and every request is still refused. Callers moved onto it: `_fetch_bundle` (serves /score, /score/compare, shadow, the batch and trace Jobs through `_compiled_for`, the governance gate and switch PREPARE), `rating_handlers` (regression), `dislocation_handlers` (`_compiled` and `_exact_twin`). `_fetch_bundle` and `_compiled_for` gained a required `database=`.
3. **Slot** (condition 3, finding (1)). `BundleSlot` gained `discard`, `first_refusal`, `unrecord_refusal`. A refused hash is evicted, so `_compiled_for`'s "any other exception = metadata store down" branch has nothing refused to serve (planted-held test below).
4. **Re-validation** (S3-c/d). `check_rateable_intent` (compile.py; shares `_inline_pinned` with `compile_bundle`, so the resolution is compile's own, and runs only the two intent guards) and `revalidate` (`bundle_hydration.py`): the stored blob through `hydrate`, then the pins re-resolved for what a Bundle cannot carry. Called at `submit_request`, `deploy` and `rollback` (a required `revalidate=` argument, never defaulted, so a caller cannot skip it silently); PREPARE is `hydrate_for_switch` -> `_fetch_bundle` -> `hydrate`.
5. **B2 (i)**. `_accepted_feature_map_values` (algorithm save) runs the same `refuse_control_in_features`; 422 naming the Factor. The pinned test `test_a_compile_over_a_gbm_fitted_on_a_control_factor_fails_with_its_code` now inserts the algorithm row directly (as a save made before the check would have left it) and still proves compile refuses; `test_a_save_over_a_gbm_fitted_on_a_control_factor_is_refused_with_its_code` is the new save-side test.
6. **Sweep** `scripts/sweep-stored-bundles.py` (condition 4), read-only, one `SET TRANSACTION READ ONLY` transaction; denominators first.
7. **Docs.** `03` FR-240, FR-243, FR-267, FR-269, §4.3 (the audit action), §5.1 (the error code's registration, the save route row) carry dated lines; FD-1495's register row carries the B1 limb; the SL 8436 row; `deploy/README.md` carries the upgrade note.

## Rulings that shaped the build (quoted whole)

> ## 2026-11-13 19:58:03 GMT — Maintainer: S3 RULED (aud-intent2 FINAL scratch/aud-intent2/backend.md 39baf6aae0ce; census re-read by me: gipricing rating_versions = 0, deployments = 0 — the denominator is 0, the census is vacuous here by construction and the record says so). DESIGN: (C) + (B). Reasons: (A) alone leaves a live version pricing on a control operand until someone re-deploys it; (B) follows the precedent load_bundle already sets — it refuses a bundle compiled before the pin check with RATING_VERSION_UNPINNED "so a bundle compiled before that check existed cannot price silently" (runtime.py:1156 docstring, FR-237) — and costs one closure walk per hydrate, not per quote; (C)'s sweep is what tells an operator BEFORE the upgrade which versions (B) will refuse. FAIL CLOSED: a stored bundle with a control operand is refused at load with CONTROL_FACTOR_IN_RATEABLE_PATH. A platform that keeps serving a prohibited price is worse than one that refuses it; the sweep is the operator's warning. This decides a point the specs left open: it is recorded as an OQ row RESOLVED by this ruling in the S3 PR (options A/B/C as priced, the decision, the reasons), mirrored both ways. GO S3 (WK-2113 S3, SL 8436, LG 8437) the moment S1's merge is read back by me; send the one-line census then. CONDITIONS: (1) red first: load_bundle of a pre-fix control-operand bundle does not raise at main (the no-DB probe, instrument proven red), then raises; the DB tests for approval, deploy, rollback and switch PREPARE in the gate window. (2) The refusal on every scoring path (/score, compare, batch, shadow, trace) is an RFC 9457 problem with the named code, plus ONE audit event per refused load naming the version, the hash and the operand — tested; never a 500. (3) The slot: a hash already held by a running worker — state what makes it re-validate (eviction, restart, or a version bump of the guard) and test it; an upgrade note says restart. (4) The sweep is a read-only script under scripts/ printing denominators first (versions with a bundle, versions checked, offenders), with a red-first fixture that plants one offender and one clean risk×risk version; rc non-zero when offenders exist. (5) The table-key half that load cannot see (no Factor payload in the bundle): covered by (A) and the sweep, and the LG says in words that load-time does not cover it — no silent gap. (6) FR-239 and NFR-489: no price or hash changes for a clean bundle; the hydrate cost of the walk measured once on the freMTPL2 bundle and quoted (a number, not "negligible"). (7) An upgrade note in CHANGELOG and the deploy docs: run the sweep before upgrading; what a refusal looks like; the remedy is a NEW version, never a mutation. (8) Dislocation's interim asymmetry (recompiles and fails at prepare while /score prices until S3) is stated in S1's LG as known and closed by S3. B2 (the algorithm save check tests no intent and REQUIRES the control operand as a feature_map input): into S1 if it is one call to the same closure helper in rating_versions.py with a red-first test; otherwise S3 — the lead's recommendation, adopted. B3: covered by (A). B4: is OQ 8431 (S1 condition 6). B1 is filed as a limb of FD-1495, HIGH on the same probe, owner WK-2113, closed by S3.
> 

> ## 2026-11-13 21:17:39 GMT — Maintainer: S3 PLAN READ (scratch/pln-s3/S3-plan.md ef6b1adaed39) — GO NOW, WK-2113 S3 (SL 8436, LG 8437), builder starting on a branch off S1's pushed head. RULINGS: B2 = (i) REFUSE AT SAVE TOO, with the same closure helper, a 422 naming the Factor; compile stays the gate of record; the pinned test test_a_compile_over_a_gbm_fitted_on_a_control_factor_fails_with_its_code is changed to expect the save refusal AND a second test keeps proving compile refuses (a model saved before this change must still be refused at compile); it is a contract change: 03's save route row and FR-240 carry the dated line, CHANGELOG lists it. DP-1 = YES, a per-process memo of refused hashes: one audit event per process per hash, and the event says so ("first refusal in this worker"); every request still gets the refusal response. DP-2 = 409, the stored artifact conflicts with the current rules, problem+json with CONTROL_FACTOR_IN_RATEABLE_PATH; the caller's request is not at fault, so not 422; never a 500. DP-3 = YES, on the shadow path the event is recorded and the live response is untouched. FINDING (1) ACCEPTED AS THE DESIGN: one backend wrapper `hydrate` around load_bundle, mapping the refusal to a PlatformError and writing the audit event; EVERY caller in the 20-path table moves onto it; and the existing "any other exception = metadata store down, serve the held bundle" branch in `_compiled_for` must NOT be able to serve a refused hash from the slot — a test plants a held refused bundle and shows it is not served. The census test (hydrate the only caller of load_bundle; `_fetch_bundle` the only slot.put caller) is required. Condition (3) = RESTART, stated in the upgrade note with the sweep as the pre-flight. Finding (3) in LG words as planned. STACKING RULE (a lesson of 5 Nov): S3's branch is stacked on S1's head; after S1 squash-merges, S3 merges S1's FINAL pre-squash head first, then main, and proves tree equality for S1's files before its gate — never a raw merge of main onto a stale stacked base. S3's gate binds only the head re-merged after BOTH S1 and S2 are on main; its STOPs stand (no merge of S1 with the placeholder hash; CHANGELOG.md on main first). Send the one-line census when the builder is seated.
> 

> ## 2026-11-13 21:23:21 GMT — Maintainer: S3 PREP READ (scratch/s3prep/README.md 7327eaf11946). Findings (1) HASH BLINDNESS and (2) AUDIT SURVIVAL accepted as design facts exactly as bound: no memo or slot state treats a hash as validated; the DP-1 memo de-duplicates audit events only; the slot holds only a bundle that passed the guard; the audit event is written in its own transaction and a test finds it after the refusal rolls the request back. RULINGS: (3) HASH-ONLY VERSIONS (a content_hash and no readable bundle): FAIL CLOSED — refused at submit, deploy, rollback and switch PREPARE with a named error (the bundle cannot be re-validated), never served and never skipped; the sweep lists them as UNREADABLE with rc non-zero. The existing tests in test_deployments.py that build hash-only versions get a REAL blob in their fixture — the fixture is fixed, the rule is not weakened; count how many tests change and say so in the LG. One check first: that no production path can legitimately leave an approved version without a blob (if one can, it comes to me before the rule lands). (4) WHERE APPROVAL SITS: the builder's default accepted — re-validate at submit_request, deploy, rollback and switch PREPARE; the decision itself does not read the bundle. Reason: deploy is the last gate before serving and re-validates whatever changed since submit, including an upgrade of the rules between the two. The LG says in words that a decision approves a request re-validated at submit and that deploy re-validates again.
> 

## Gate

Logs are under `~/gi-pricing-plan.local/scratch/sl-8436/` (local, not in the repository), each opening `head=` and ending `rc=`.

**Red** (S1's head `5d2189a3`, source reverted in my own worktree, tests only; `s3a-red.log`, rc=1): `test_rating_load_bundle_control_guard.py`: `1 failed, 3 passed`; the failure is `Failed: DID NOT RAISE ValueError`. **Green** with the guard (`s3a-green.log`, tree = S1's head plus the uncommitted guard, rc=0): `4 passed`. The three other backend red states are an absent module (`app.platform.bundle_hydration`, `scripts/sweep-stored-bundles.py`: collection errors at S1's head, measured by the preparing seat for the sweep, `run2.log` rc=2) and, for the census, the planted second caller.

| check | head | result | rc |
|---|---|---|---|
| compile regression after extracting `refuse_control_in_features` and `_inline_pinned` (`compile-regress.log`): `test_rating_compile_fr240.py`, `test_rating_compile_bundle.py` | `d2e962f2` + uncommitted refactor | 86 passed | 0 |
| `test_bundle_hydration.py` + `test_sweep_stored_bundles.py` (`sweep-hydration-green.log`) | `d2e962f2` + uncommitted | 12 passed (the census assertion was then corrected to two `slot.put` sites in `_fetch_bundle` and re-run in the batches) | 0 |
| import-closure set, non-DB part: 43 files in 15 `run-small` batches of at most three (`batches.log`, tree `7f802a73`) | `1011785a` | batches 5 to 15 (pricing-core) all rc 0 (e.g. `test_rating_compile*`: 223 passed; `test_rating_load_bundle_control_guard.py` with two others: 21 passed); batch 1 rc 1 (`test_api_authorisation_sweep.py`: 9 errors, no database: `GIP_TEST_DATABASE_URL is not set`, owed to the DB window); batch 2 rc 1 (`test_error_sinks.py`: 1 FAILED, the sink census, below; 4 errors, no database); batch 3 rc 1 (`test_errors.py`, `test_management_429_declared.py`, `test_startup_gc_freeze.py`: 2 errors, no database); batch 4 rc 1 (`test_quote_input_raise_sites.py`: 1 FAILED, the raise-site census, below) | 4 batches rc 1 |
| the two FAILED censuses after listing the new sites (`census-rerun.log`) | `68e04a7e` | `test_error_sinks.py` and `test_quote_input_raise_sites.py`: 28 passed, 4 errors (the four DB-backed tests of `test_error_sinks.py`, no database) | 1 (the 4 errors only) |
| `uv run ruff check .` (`ruff.log`) | `68e04a7e` | All checks passed | 0 |
| `uv run mypy` (`mypy.log`) | `68e04a7e` | no issues, 258 source files | 0 |
| `uv run lint-imports` (`lint-imports.log`) | `68e04a7e` | 4 kept, 0 broken | 0 |
| `ruff format --check` on the 8 new `.py` files | after `HEAD` | all formatted (`bundle_hydration.py` reformatted in its own commit); 13 of the other changed files are unformatted at their base too, not reformatted here | 0 for the new files |

The two FAILED censuses were found by the closure run (common brief items 11 and 45), not by the builder's own tests: the first run of `test_error_sinks.py` named the sinks `refuse_control_in_features` (moved), `_control_refusal` and the save-site `str(error)` as unlisted, and the raise-site census the moved function and `check_rateable_intent`. **S1's head also fails `test_error_sinks.py`** (its `_refuse_control_factor_keys` and `seed_from_model` sinks are unlisted; reported to the lead).

**Docs and static checks:** DOCS_CHECKS

**Owed to the DB window (written, collected, not run):** `test_stored_bundle_revalidation.py` (4 tests), `test_stored_bundle_slot_revalidation.py` (3), `test_score_stored_bundle_refusal.py` (3), `test_fr240_governance.py` (the new save test and the changed compile test), the 26 tests that use `approved_version`, `test_api_authorisation_sweep.py` (9), the DB-backed tests in `test_error_sinks.py` (4), the sweep's CLI read, the hydrate-cost measurement, and the 92 backend test files the closure reaches that need a database (`green-s3-db.txt`). The closure is derived by `closure.py` (sha256 prefix 8d05b394011b): `git diff --name-only origin/sl-8429-fd1495-interaction-operands...HEAD -- packages backend/src > changed-s3.txt` (14 files; against `origin/main` it is 22, because S1 is not on main) then `python3 -I closure.py <wt> changed-s3.txt green-s3.txt`: 130 test files (`green-s3.txt`), 38 non-DB (`green-s3-nondb.txt`) plus the five this slice names, 43 run (`run-set.txt`).

## Condition-by-condition evidence (the eight conditions of "19:58:03 GMT")

1. **Red first.** `test_a_stored_bundle_pricing_on_a_control_operand_is_refused_at_load` at S1's head `5d2189a3`: `DID NOT RAISE ValueError`, 1 failed 3 passed, rc 1 (`s3a-red.log`); with the guard, 4 passed rc 0 (`s3a-green.log`). The three controls pass on both sides: the construction patch is restored, the same construction without the patch is refused at compile, the same bundle with a `risk` operand loads. The DB tests (approval via `submit_request`, deploy, rollback, switch PREPARE) are written (`test_stored_bundle_revalidation.py`), import-checked (collect-only rc 0) and **owed to the DB window**, where each is to be run once at main (red) and at the head (green).
2. **Every scoring path.** `hydrate` maps the refusal to a 409 `PlatformError` (`app.errors` renders it as RFC 9457), never a 500; one event per process per hash. No-DB tests pin the mapping, the once-per-hash count and the retry when the audit write fails (`test_bundle_hydration.py`, 7 passed). The DB test `test_score_stored_bundle_refusal.py` runs `_compiled_for` (the one door of /score, /score/compare, the batch and trace Jobs, the shadow arm) twice and asserts one event.
3. **Slot.** The mechanism is **restart**. `BundleSlot` is process memory (built at `main.py`, `scoring_handlers.py`, `trace_handlers.py`) and after this slice the only `slot.put` callers are the two sites in `_fetch_bundle`, whose second follows `hydrate`: a process on this code holds only a bundle that passed the guard; a process on older code holds what it held until restarted, which the upgrade note says. A refused hash is also evicted (`BundleSlot.discard`), so `_compiled_for`'s store-down degradation cannot serve it: `test_a_held_refused_bundle_is_evicted_and_not_served_when_the_store_is_down` plants a held bundle under the refused hash, refuses, then fails the store and shows nothing is served. The census (`test_hydrate_is_the_only_caller_of_load_bundle_and_fetch_bundle_the_only_slot_put`) is red-proven by a planted second caller in a scratch copy (`test_the_census_sees_a_planted_second_caller`).
4. **Sweep.** `scripts/sweep-stored-bundles.py`; `test_sweep_stored_bundles.py` 5 passed: denominators print first, one offender line naming version, hash, operand and cross, rc 1; clean-only rc 0; empty corpus prints zeros, rc 0; an unreadable bundle rc 2. The fixture is the prepared pair (`fixtures/stored_bundles/`). The sweep's DB read and its keys / GBM half run only in the DB window; the shared template reads `rating_versions = 0`, so a run there is vacuous by construction and the record says so.
5. **In words: load-time does not cover the table-key half.** Load-time (B) does not see a rate-table key's Factor or a GBM's features: the Bundle carries neither. Both are covered by the re-validation at submit, deploy and rollback (A, `check_rateable_intent`) and by the sweep (C).
6. **FR-239 / NFR-489.** `test_fremtpl2_rate_fixture.py` and S1's hash tests are unchanged; the compile regression run (`test_rating_compile*.py`) is green (see the table). The hydrate cost measurement is **owed to the DB window**: the harness is `scratch/sl-8436/measure_hydrate.py` (sha256 prefix 146818f27000); it prints its denominators first (GLMs walked, carried Factors, operand edges) and exits 3 on a zero walk. No number is quoted until it runs.
7. **Upgrade note.** `deploy/README.md` carries it. **CHANGELOG.md is absent on this base (S2 not merged): that half is NOT done and waits for S2.** The entry text is below.
8. **/score and the dislocation run refuse the same offender.** `test_score_and_the_dislocation_run_refuse_the_same_planted_offender` (DB window).

### Words the maintainer asked for

- **Finding (3) of the prep, in words: `bundle_hash` hashes no payload.** `_carry_glm_inputs` puts a GLM pin's Factors into the Bundle and documents that "the Bundle's shape and `bundle_hash` are unchanged"; the hash covers the pins, not the carried Factor payloads. So the forged offender and the clean twin share one `content_hash`, a hash cannot tell a re-validated bundle from an unchecked one, and (design fact 1) no memo or slot state treats a hash as validated; the DP-1 memo de-duplicates the audit event only.
- **A decision approves a request re-validated at submit; deploy re-validates again, which also covers a rules upgrade between the two.** The decision itself does not read the bundle.
- **Hash-only versions (ruling (3)).** `revalidate` refuses a version with a content hash and no readable blob (`BUNDLE_COMPILE_FAILED`, "the bundle cannot be re-validated"); `_fetch_bundle` already refused a version with no blob key. The sweep lists them UNREADABLE (rc 2). **Writer census** (ruling's "one check first"): the only writers of `rating_versions.bundle` are `rating_versions.py:860` (compile, the hash) and `:261` (`record_bundle_blob`, the key), both inside `rating_handlers.py`'s one `unit_of_work` (blob put :68, key :85), so compile cannot commit a hash without its blob; no migration or seed writes it. **A latent path exists:** the bundle blob is stored by `blob_store.put` with `ref_count = 0` (`blobs.py:252`) and `rating_handlers.py:68` never calls `blobs.retain` on it (the structural-diff blob does, `rating_versions.py:1268`), so once OQ-1943 wires FR-420's garbage collector, a bundle blob older than the grace period is collectable and an approved version turns hash-only. Not live today (no caller of `collect_garbage` in `backend/src`; the application role holds no `DELETE` on `blobs`). Reported to the lead; for the maintainer's reading, as a limb of OQ-1943.
- **Tests that changed for the rule (count).** One fixture changed: `approved_version` in `backend/tests/test_deployments.py` now stores the clean fixture bundle as a real blob and `_HASH` is that bundle's own hash. By AST, the tests calling it with the default `compiled=True`: 13 in `test_deployments.py`, 7 in `test_deployment_switch_http.py`, 5 in `test_shadow_write.py`, 1 in `test_routing_write.py` (26), plus one helper site in `test_audit_transitions.py:1585`. Which of them actually reddened is for the DB window to say; none was run.

### Deviations from the plan, for the lead's reading

- The audit actor is the system principal `bundle-guard`, not the request's principal (`hydrate` has no request; threading one through every door was out of proportion). The event's `entity_ref` names the version.
- The plan said no event at approval, deploy or rollback; the load half goes through `hydrate`, so those refusals audit too (once per process per hash). The key / GBM half is audited the same way.
- A version with no declared pins skips only the pin re-resolution (the bundle half still runs): a real compiled version always has pins (FR-237), so only a row that is not one reaches it.
- The prepared slot test (mechanism (B)) was replaced by the restart mechanism's tests.
- `test_error_sinks.py` and `test_quote_input_raise_sites.py` list the new sites; the three sinks S1's head left out of `test_error_sinks.py` are listed too (S1's head fails that census).

## CHANGELOG entry text (waiting for S2's `CHANGELOG.md`)

### Upgrade note: stored Rating Version bundles are re-validated (WK-2113 S3, FD-1495)

A Rating Version compiled before the `control`-intent guards existed can carry a bundle that prices on a
`control`-intent Factor (for example a risk interaction crossing year of account). From this build, such a
bundle is refused wherever it is hydrated (`CONTROL_FACTOR_IN_RATEABLE_PATH`, a 409 problem with one Audit
Event `rating_version.load_refused` per process per bundle), and a deployment request, a deploy and a
rollback of it are refused too. A Rating Algorithm that maps a model fitted on a `control` Factor is now
refused at **save** (422), where it used to save and fail at compile.

1. **Before upgrading, run the sweep**: `uv run python scripts/sweep-stored-bundles.py [--dsn <read-only URL>]`.
   It is read-only, prints its denominators first, lists each stored version the new build will refuse
   (exit 1) and each bundle it could not read (exit 2).
2. **The remedy for an offender is a new version**, never a change to the stored one: a compiled version is
   immutable and compile is draft-only.
3. **Restart every api replica and every worker after the upgrade.** A running process keeps the bundles it
   already hydrated; the guard runs when a process hydrates a bundle, so a process that is not restarted
   keeps serving what it held.

## Audit

Not yet written; the auditor re-checks.

## Build log

- 2026-11-13: `d2e962f2` the load guard, the shared `refuse_control_in_features`, and the red test (red at `5d2189a3`, rc 1; green rc 0).
- 2026-11-13: `05fe7f1f` `hydrate`, the slot's refusal memo, `check_rateable_intent` and `revalidate` at submit, deploy and rollback, the algorithm save refusal (B2), the sweep script, the prepared tests adapted.
- 2026-11-13: `1011785a` the no-DB and DB tests for every hydration door, the hash-only fixture given a real blob, the spec, register and roadmap lines, the `deploy/README.md` upgrade note.
- 2026-11-13: `68e04a7e` the sink and raise-site censuses list the new sites.
- Note: the builder ran `uv run pytest -q backend/tests/test_api_authorisation_sweep.py -x` directly once, outside `run-small` (it failed at database setup, before any test body ran), against the brief's run-small rule; no other direct pytest run.

## PRs

None yet: this seat opens no PR (brief); the lead opens the slice's one PR after the re-merge.
