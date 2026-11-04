---
id: RS-1866
family: research
kind: audit
title: SL-1260 (WK-674 Slice 6) delta audit of the slice's own commits, 57b7fa04..fbf092a9
status: draft
created: 2026-10-22   # drafted 2026-10-22 under working id 8198; minted 2026-10-23 as RS-1866
owner: auditor
tree: 6015217016a6c4d0c7175afe304a73e14b1c4a4d
phase: P2
work: WK-674
corrected_by: []
relates: [SL-1260, LG-1859, RS-1864, RS-1865, RL-1834]
---

# RS-1866 — SL-1260 delta audit, 57b7fa04..fbf092a9

*Minted 2026-10-23 as RS-1866 from working id 8198, in the SL-1260 audit-records docs PR. Prose below that calls this record or another id "unminted" or names a working id describes the draft state at filing, not the tree at the mint.*

*(Working id 8198, lead-allocated. Written by `aud-1260c`, 2026-10-22, from `brief-aud-1260c-2026-10-22.md` (lead 26). Check 31 on this id is expected until the mint. The audited tree is the slice head `fbf092a9b7017922c956ea4fe82525e7739164d7`, tree `6015217016a6c4d0c7175afe304a73e14b1c4a4d`; nothing on the slice branch was edited.)*

**Verdict (PROPOSED, the lead's to adopt): CLEAN, with one non-blocking item (N1) and two labelling notes (N2, N3).** No B-item.

## Question

Does the delta 57b7fa04..fbf092a9 meet the brief's scope? The proposed verdict is at the top; the headings Question, Method and Findings were added at the mint so the record carries the RS template's required sections.

## Method

### Scope: the delta, re-derived

`git log --no-merges --first-parent 57b7fa04..fbf092a9` gives exactly the 15 commits the brief names (eb3daf87 … fbf092a9). The three merge commits on the first-parent line (7fdc9e24 = e202f28b, cf2eedfa = 75f5f401, 00174d02 = 0dfb4a05) bring main's commits; `git merge-base --is-ancestor` exits 0 for e202f28b, 6753c495, 75f5f401 and 0dfb4a05 against origin/main. Code changed in the delta: 8 test files only (no `backend/src` change from the slice's own commits; the `main.py`/`deployment_switch.py` change in the range is main's).

## Findings

### Per commit

| Commit | Claim in LG-1859 | Result |
|---|---|---|
| eb3daf87, de7e2e78 | `_routed` test parametrised on `select_range`/`resolve`; asserts the ERROR "request failed" record, class, frames | Matches `backend/tests/test_routing.py` diff. Two red controls with logs 29/30 (`assert 200 == 500`; `assert 'select_range' in [...frames]`), green 28 (`9 passed`), reverted, never committed. Both limbs of 17:43:37 (b) pinned. |
| bf27b0be → e9e784a9 | 07 §5.1 entry added, then reverted | `git diff bf27b0be~1 e9e784a9 -- docs/specs/07-platform.md` is empty: an exact revert, no residue. |
| 33680bb0 | 00 §5.3 catalogues INTERNAL_ERROR as a generic code | Ruled form of 19:52:20 item 3 (B): row in 00 §5.3, 07 reverted, "no module's Error-codes block lists it", `errors.py` unchanged. `audit-docs.py` (one run under the gate-2 flock): only FAILED line is check 31 (gap 1855→1859). |
| 6e2707a7 | four guard tables | See guard table below. |
| fffff45e | two shadow sinks listed in `_SINKS` with sentinel tests | Entries are exactly `score.py` `_shadow_task` and `_shadow_score`, `exc_info`, count 1 each, each naming its own test. Red-first: log 34, both sentinels fail by name when `safe_job_exc_info(exc)` becomes `exc`; green log 33 (`2 passed`). |
| c274c53d, 4a9c5200, 72a05338 | gate-red table; item 5 resolved (B); DB-lane runs; re-merges | Table rows 1–6 match the six FAILED lines of the red gate (see below). DB-lane logs 37/38/39 record `23 passed`, `25 passed`, `35 passed`. |
| 5d79bbf4, b349bbd4, fbf092a9 | mint of LG 1859 as LG-1859 | See mint check. |
| 605fae23, eaf045d2 | migration round trip; V2b/V2c; INTERNAL_ERROR catalogued | Round trip table consistent (head → `-1` → head, tables absent then present). V2b/V2c diffs now inline. eaf045d2 text on 07 §5.1 is superseded by (B); the history stands. |

### Guard-table extensions: widened only for this slice's additions

| Guard | Before → after | Weakening? |
|---|---|---|
| `ONE_SIDED_SLUGS` (`test_contracts.py`) | +4 entries: `routing-rule`, `routing-rule-update`, `shadow-config`, `shadow-config-update`, each with a first-written-form reason | No. `docs/contracts/schemas/generated/` holds exactly those four `routing*`/`shadow*` schemas. |
| demo-guide RATE→OPT (`test_demo_guide.py`) | `{"RATE"} <= modules` → `{"OPT"} <= modules` | Same strength (one module required unbuilt), dated comment with reason; passes in log 38 (`25 passed`). RATE's drop-out rests on the slice building the last RATE endpoints, which the test itself now proves only by not failing; accepted. |
| ENVIRONMENT-scope sibling (`test_settings_environment.py`) | selector `is not WORKSPACE` → `is WORKSPACE_OR_ENVIRONMENT` (3-key assert unchanged); new test asserts the ENVIRONMENT-scope set equals the two flags | No. Union of the two tests covers every non-workspace key as before. `SettingScope.ENVIRONMENT` is declared by exactly two definitions in `settings.py` (lines 323, 333), so the exact-set assert matches. See N1. |
| `_SINKS` +2 with sentinel | see fffff45e | No: census entries each have a red-first test. |
| `test_audit_docs_ids.py` count | 89 → 93 with a dated comment naming the four schemas | No; ties to the four `ONE_SIDED_SLUGS` schemas (same four files exist). |

Red gate (`scratch/sl1260-gate.red-2026-10-22-605fae23/pytest.log`): `19 failed, 6702 passed, 19 skipped`. Removing the 13 docs-audit names leaves six: `test_every_one_sided_slug_is_declared`, `test_the_guide_names_the_endpoints…`, `test_every_failure_sink_on_a_quote_input_path…`, `test_scope_defaults_to_workspace_only…`, `test_widening_the_scope_roots…`, `test_the_error_code_registry_matches_the_specs` = LG rows 1–6, each extended or resolved in the delta.

### Spec text (INTERNAL_ERROR)

00 §5.3 carries the row; 07 §5.1 has none (empty reverse diff above); `errors.py` is unchanged by the slice and already lists it in `_GENERIC_ERROR_CODES`. The log condition (17:43:37 (b)) holds in `middleware.py:56` ("request failed") and is pinned by the test. N1 below on condition (a).

### Re-gate at 72a05338 (`scratch/sl1260-gate/`)

`START head: 72a05338b7fc573c1ca5b6e4a1c72251ea18f9ef`, tree `418ad03d…` (matches `git rev-parse 72a05338^{tree}`), `END 2026-10-22T21:31:33+00:00`; rc: audit_docs 1, contracts 0, import_linter 0, mypy 0, pytest 1, req_coverage 0, ruff 0; `13 failed, 6742 passed, 13 skipped`. The 13 FAILED names are exactly the docs-audit set (ids 2, finding-citations 1, process-core-digest 2, w37-11-ceiling 1, doc-index 1, register-lint 3, register-owed 1, repository-invariants 2 = 13), and equal the 13 re-run in LG-1859 logs 40–43 (2+4+5+2). Matches the maintainer's 22:32:13 reading. Note: the gate predates 7fdc9e24 (main's e202f28b merge); that is the maintainer's 1(f) call, which that entry scopes to the code of 72a05338.

### Mint (22:32:13 form)

`created: 2026-10-22  # drafted 2026-10-21 under working id 8139; minted 2026-10-22 as LG-1859`; H1 disclosure line present; `git grep -nE '\bLG[ -]0?8139\b' fbf092a9` = 0 hits; bare `8139` appears only in the ledger's own disclosure/comment lines and prose. fbf092a9 only rewords the elided quote. `audit-docs.py`: single FAILED, check 31 gap 1855→1859 (the unmerged 1856–1858 of #1364), as the ledger says; the chronology line is clear.

## Items

- **N1 (non-blocking, no spec edit proposed).** 17:43:37 condition (a) asks that the catalogue definition cover "a server-side failure the caller cannot fix". 00 §5.3 (33680bb0) says "An unhandled exception … a module that can name a refusal raises its own code". Semantically covered; the exact phrase is absent. The lead may rule it met or ask for the phrase. Also, test `test_the_routing_and_shadow_flags_are_environment_only` has no recorded red/negative control (LG row 4 argues "no weaker" only). Its assert is exact-set equality over two declarations, so it fails if a third ENVIRONMENT key appears; a one-line control in the ledger would close it.
- **N2 (labelling).** LG-1859 names three commit shas as "tree": `eaf045d2c2c1…` (605fae23 section), `4a9c5200c8…` (72a05338 section) and `5d79bbf463da…` (mint section). Each is a commit; the trees are distinct objects (`eaf045d2^{tree}`, `4a9c5200^{tree}` = `7da0fc98…`, `5d79bbf4^{tree}` = `e592cd85…`). The commits are reachable, so no evidence is lost; the label is wrong (name-the-object rule).
- **N3 (observation).** `ruff format --check` drift in four edited test files is recorded as pre-existing and not touched; not re-measured here.

## Not done

No pytest, DB, or gate was run by this seat. One `audit-docs.py` run under the gate-2 flock (docs-check standing rule; gate-1 was held by another gate, gate-2 free). No GitHub posts.
