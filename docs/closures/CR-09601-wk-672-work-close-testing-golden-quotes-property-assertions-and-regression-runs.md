---
id: CR-9601
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-672 Work close — testing, golden quotes, property assertions and regression runs
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-29
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: 1c8762d9ed235f80e0f2fff80c44003694828e97
phase: P2
work: WK-672
corrected_by: []
relates: [FD-1208, FD-1209, FD-9602, FD-9603, FD-9604]
---

# CR-9601 — WK-672 Work close: testing, golden quotes, property assertions and regression runs

**What this record is.** The auditor's closure record for WK-672, `kind: work`
(`document-ids.md` §1.6, CR row). **Every verdict and every finding decision in it is a
proposal.** The lead adopts, amends or rejects each one in writing (`CLAUDE.md` §12, §13), and
the maintainer accepts the Work close with a dated line under *Sign-off*. `CR-9601` is a
working id; it is minted at this PR's merge turn with `python3 scripts/doc-id.py next --ref
origin/main`, as are `FD-9602`, `FD-9603` and `FD-9604`.

**The tree.** Everything was measured at `origin/main`
`1c8762d9ed235f80e0f2fff80c44003694828e97` (#889), fetched 2026-09-29. `main` then moved to
`6ae8a99a` (#843), which adds the WK-674 map plan and one `docs/INDEX.md` line
(`git diff --stat 1c8762d9 6ae8a99a`: 2 files, 1118 insertions), neither in this close's scope.
The logs cited as `NN-*.log` are local, under
`~/gi-pricing-plan.local/evidence/wk672-close/`, each with `SHA:` as its first line and `RC=` as
its last, hashed in that directory's `SHA256SUMS`.

## Scope

Derived from the specification and the plans first, then evidenced (`CLAUDE.md` §13). Three
lists, each with its predicate.

### A. The roadmap's charter

Predicate: the `### WK-672` section of `docs/roadmap.md` at `1c8762d9` (heading `:632`), its
row line *"From “Workstreams” (line 377): … | FR-260, FR-261, FR-262"* and its paragraph
*"2026-09-28 — the charter, named against its own ids"* (`:646`).

**FR-260**, **FR-261**, **FR-262 (the backend limb only)**, and **FR-257 limb (1)**.

### B. The plans' Scope sections

Predicate: the ids written in each plan's own Scope text, read in full. The leaf plans have a
`## Scope` heading; the map plan has none, so its predicate is its **Goal**, **Spec** line and
the four `## Slice N` sections (`PL-930` lines 20-40 and 359-390). `git grep -oE
'\b(FR|NFR)-[0-9]+' <plan>` lists more ids than this (for example `FR-386` in `PL-1189`, `FR-219`,
`FR-255`, `FR-263`, `FR-346` and `NFR-454` in `PL-1213`); those sit outside the Scope text and
are not scope.

| Plan | Ids its Scope names | The plan's own disposition |
|---|---|---|
| `PL-930` (map) | FR-260, FR-261, FR-262 (its Spec line writes these three in their pre-migration `RATE`-scoped form), NFR-499 (the Golden-Quote carve-out), FR-248 (a property class) | the Work |
| `PL-1177` (S1) | FR-260, FR-261, FR-262, FR-257 limb (1); NFR-499 carried to S2 | spec correction |
| `PL-1189` (S2) | FR-260; FR-261 (stored only); FR-273; FR-257 (not built here); NFR-499; `06` FR-353, FR-364, FR-368 | FR-353 *"#861's, consumed and not changed"*; FR-364 *"unchanged"*; FR-368 built |
| `PL-1205` (S3) | FR-261; FR-257 limb (1); FR-260 (composed); FR-248; FR-273; NFR-499; `06` FR-364 (*"fed by `evidence.regression_suite_run_id`"*) | built |
| `PL-1213` (S4) | FR-262 backend limb; FR-258 and FR-251 (consumed); NFR-499 and NFR-502 (enforced); FR-248 and FR-273 (untouched) | built |

### C. Owner clauses in the spec, the open questions and the register

Predicate, verbatim: `git grep -n 'WK-672' 1c8762d9 -- docs/specs docs/open-questions.md
docs/findings/register.md`. **32 hits**: `03` 19, `06` 1, `07` 1, `open-questions.md` 4,
`register.md` 7. Each was read in context, with its dated amendments; the list is not filtered
to A ∪ B.

| Hit | What it is | Carries |
|---|---|---|
| `03:174` FR-257 | clarified 2026-09-28, WK-672 S3 (DP-S3-1) | a passing suite has at least one golden quote |
| `03:177` FR-260 | amended 2026-09-28 (DP-S2-1, DP-S2-2) | the check at `submit`, the pin, the delta, `regression_suite: "none"` |
| `03:178` FR-261 | amended and clarified 2026-09-28, WK-672 S3 | the case store is `FR-1221`; the `monotone` grid |
| `03:179` FR-262 | clarified 2026-09-29, WK-672 S4 | the backend limb; the view is WK-675's |
| `03:180` **FR-1221** | added 2026-09-28, WK-672 S3 (DP-S3-4 (i)); minted in #886 | the case store: canonical content-addressed blob, replay never regenerates, `rating:read` in its workspace, never logged |
| `03:1154` NFR-499 | clarified 2026-08-30 (*"settled before WK-672 builds it"*) and 2026-09-28 (DP-S3-4 (ii)) | the third quote-input store |
| `06:145` FR-364 | amended 2026-08-29 | *"`regression_run` becomes verifiable in **WK-672** (`03` FR-261)"*; wiring the rating-version check is WK-673's (RL-885, `RL-1184` E4) |
| `07:307` `GET /api/v1/blobs/{sha256}` | amended 2026-09-28 (WK-1178) | never serve a blob a quote-input store references, *"WK-672 Slice 3's case store when it lands"*; an interface row, no requirement id |
| `03:546, 643, 647, 649, 680, 698, 777, 896, 901, 960, 967, 977, 1127` | dated section notes (§4.7, §4.9, §4.10, §5.1's error list, §5.2, §8) | no requirement id beyond those above |
| `open-questions.md:132-135` | OQ-1222 (WK-1178), OQ-1223 (WK-675), OQ-1224 (WK-1178), OQ-1231 (WK-675), all open, raised by WK-672 slices | owned elsewhere |
| `register.md:85` F44 | FR-257 limb (1) re-pointed to WK-672 S3; delivered 2026-09-29 (#886) | — |
| `register.md:101` F60 | Resolved 2026-09-28 by RL-1172 | — |
| `register.md:181` FD-1194 | Resolved; *"#852 is held until WK-672 closes"* | the Dependabot hold; see *Findings* |
| `register.md:187` FD-1199 | the lead's; conditional on WK-672 S2's N=5 run | not WK-672's |
| `register.md:190` FD-1203 | Resolved by #868; *"WK-672 Slice 3's case-store code waits for it"* | — |
| `register.md:193` **FD-1208** | carry forward, unowned; Work item WK-672 | a decision now |
| `register.md:194` **FD-1209** | deferred with an owner (the lead); Work item WK-672; due *"before plan review 16"* | a decision now |

### The union, and what is in C only

**14 requirements:** FR-248, FR-251, FR-257 (limb (1)), FR-258, FR-260, FR-261, FR-262 (backend
limb), FR-273, FR-353, FR-364 (the `regression_run` clause), FR-368, **FR-1221**, NFR-499,
NFR-502.

- **In C only: FR-1221.** No plan's Scope names it; `PL-1205`'s DP-S3-4 row decided that
  *"the store needs its own requirement"*, and the id was appended in #886. It is also absent
  from list A: the roadmap's charter paragraph predates it. **The lead may add it to the WK-672
  section** when the section is marked closed (the roadmap is the lead's, `document-ids.md`
  §1.6 WK row).
- **In C only, not requirements:** the `07:307` blob-route obligation, FD-1208, FD-1209 and the
  FD-1194 hold.
- **Reconciliation with the roadmap.** The roadmap row names three ids and the charter a
  fourth limb. The other ten are ids the Work composed, consumed or enforced; none is a missing
  deliverable. The lead's local starting draft (`~/gi-pricing-plan.local/drafts/wk672-close/scope-and-evidence.md`, not in the repository, measured at `40af56a9`) listed the same 14; this record re-derived them.

## Checklist

Run against `.claude/skills/close-workstream/SKILL.md` at `1c8762d9` (latest *Verified* entry
2026-09-28, §5c) and `docs/process/checklists/work-item-close.md` at the same tree.

| Step | Result |
|---|---|
| §0 scope from the spec | lists A, B, C above |
| §0 three axes | requirements, endpoints and catalogue, below |
| §0a evidence beyond markers | FR-1221 and FR-364, below |
| §0b load-bearing markers read | FR-257 limb (1), FR-260, FR-262, FR-1221 and NFR-499, below |
| §1 exists and works | each slice's ledger, and CI on `main` |
| §2 gate | CI on `main` cited (below). The auditor ran no full gate, on the lead's instruction. |
| §3 new checks fail on broken input | the checks this Work added were proven by mutation in the slice ledgers (`LG-1204`, `LG-1225` *The reds*, `LG-1230` *Task 3 mutations* and *Plan deviations*, #897's body); the auditor re-ran none |
| §4 NFRs measured | below |
| §5 not delivered, and the retrofit mapping | below |
| §5a binding plan-review conditions | below |
| §5b owed list | below; `python3 scripts/register-lint.py` on this branch: `OK (0 violations)` |
| §5c workflow citations | below |
| §6 plan docs | the roadmap edits are the lead's: `### WK-672` `status: closed` once accepted, and FR-1221 in the section |
| §7 clean-up | `gh pr list --state open` (15 open PRs at 15:28 UTC, 2026-09-29): none names WK-672 or a `p2-d-s*` branch |
| §14 question | plan review 16 is the planner's, conducted and filed as `CR- kind: review` (the maintainer's structure entry of 2026-09-29 15:26:00 BST, §3) |
| root `README.md` pointers | `README.md:23-24` and `:55` point at `docs/roadmap.md`; they copy no status, so this close changes nothing there |
| retry counters (RFC-895 artifact B) | **none recorded.** `write_runtime_state.py show` prints no replan or fix counter; the file was last written `2026-09-28T16:26:22Z` and still reads WK-672 slices as "not started" |

## Evidence

### The slices

| Slice | Plan | Work PR (squash on `main`) | Slice close | Ledger |
|---|---|---|---|---|
| S1 spec correction | `PL-1177` | #853 `50e5271c` (2026-09-28) | #858 `ea6162b9` | `LG-1182` closed |
| S2 golden quotes, promotion re-scoring | `PL-1189` | #867 `109cd065` (2026-09-28) | #870 `f91af639` | `LG-1204` closed |
| S3 property assertions, regression runs | `PL-1205` | #886 `6a8b8e70` (2026-09-29) | #898 `f2ef3b9a`; owed item (1) by #897 `1a10effa` | `LG-1225` closed |
| S4 compare endpoint | `PL-1213` | #901 `c9f50232` (2026-09-29) | **this PR** | `LG-1230` closed here |

Dates are author dates from `git log --format='%h|%aI|%s' 1c8762d9 --grep='WK-672'`. Every SHA
in this table is an ancestor of `1c8762d9` (`git merge-base --is-ancestor`, all rc 0).

### Requirements axis

`uv run python scripts/scope-audit.py RATE --sections 3.8 --extra FR-248,FR-251,FR-273,NFR-499,NFR-502`
(`01-scope-rate-3.8.log`): **rc 1; in scope 12, with evidence 11 (92 %); NO EVIDENCE for 1:
FR-1221.** §3.8 is FR-257 to FR-262 and FR-1221; every `--extra` id is written in full.

`uv run python scripts/scope-audit.py GOV --sections 99.9 --extra FR-353,FR-364,FR-368`
(`03-scope-gov.log`; `99.9` names no section, so only the three ids are in scope): **rc 0; 3 of
3 evidenced.**

### Endpoints axis

`uv run python scripts/scope-audit.py RATE --sections 3.8 --endpoints` (`02-scope-rate-endpoints.log`):
26 declared, 20 published. The six not published are two `dislocation-runs` rows (WK-673), three
deployment and shadow rows (WK-674) and `POST /api/v1/rate-tables/{}/versions`; none is
WK-672's. The seven rows WK-672 built or amended are all in
`docs/contracts/openapi/generated.json`: `POST …/rating-versions/{id}/submit`,
`POST /api/v1/regression-suites/{slug}/versions`, `GET /api/v1/regression-suites/{slug}@{version}`,
`POST /api/v1/score/compare`, `POST …/rating-versions/{id}/regression-runs`, and the two
`GET …/regression-runs/{run_id}` and `…/cases` reads.

### Catalogue axis

None applies. `scope-audit.py`'s `_CATALOGUE` pattern (`scripts/scope-audit.py:114`, a
backtick-quoted `XX-YY-n` id followed by a slug, at the start of a table row) matches 0 lines in `03` and 0 in `06`; positive control, the same pattern on `01`: 38 lines.

### req-coverage, and what its number counts

`uv run python scripts/req-coverage.py` (`04-req-coverage.log`): rc 0, 536 specified, 343 marked.
**Its "N test file(s)" column counts marker occurrences, not files and not tests**
(`scripts/req-coverage.py:55-59` appends one path per `@pytest.mark.req("…")` match; register row
**F36** already records this). Both figures, by
`git grep -c '@pytest\.mark\.req("<id>")' HEAD -- backend packages tests examples/fremtpl2`
(`05-marker-occ-vs-files.log`):

| Requirement | req-coverage prints | Marker occurrences / distinct files |
|---|---|---|
| FR-248 | 2 | 2 / 1 |
| FR-251 | 1 | 1 / 1 |
| FR-257 | 15 | 15 / 4 |
| FR-258 | 2 | 2 / 2 |
| FR-260 | 49 | 49 / 7 |
| FR-261 | 60 | 60 / 6 |
| FR-262 | 8 | 8 / 1 |
| FR-273 | 4 | 4 / 3 |
| FR-353 | 16 | 16 / 5 |
| FR-364 | 6 | 6 / 2 |
| FR-368 | 8 | 8 / 6 |
| FR-1221 | (no row) | 0 / 0 |
| NFR-499 | 60 | 60 / 16 |
| NFR-502 | 1 | 1 / 1 |

### The load-bearing markers, read (§0b)

- **FR-257 limb (1).** `backend/tests/test_rating_versions.py`: each refusal asserts
  `refused.value.code == "EVIDENCE_INCOMPLETE"` and the version stays `draft`, for no suite, a
  suite with no golden quote, no run, a failing run, a stale `bundle_hash` and another suite
  version; `test_an_earlier_pass_does_not_count_once_a_later_run_failed` asserts the refusal,
  then a later pass reaching `status == "review"`. Exact.
- **FR-260.** `test_golden_mismatch_refuses_submission_and_leaves_the_version_draft` asserts
  `GOLDEN_QUOTE_MISMATCH`, status 409, `draft`, no `golden_quotes` evidence and no approval
  request. `test_a_passing_run_is_recorded_and_golden_evidence_is_untouched` asserts the pinned
  value byte-identical to a snapshot taken at the gate (#897, shown red under a mutation that
  writes `golden_quotes`). Exact.
- **FR-262.** `backend/tests/test_score_compare.py::test_exactly_one_step_is_the_own_change_at_the_http_layer`
  asserts `own == ["s_expr"]`. Exact. `packages/pricing-core/tests/test_trace_diff.py`'s two
  one-step tests and its known-limit test ran at `1c8762d9`: `3 passed`, rc 0 (`07-trace-diff-named.log`).
- **FR-1221 and NFR-499**, below.

### FR-1221, read clause by clause (§0a)

No `req("FR-1221")` exists. Each clause, and the test that asserts it under another marker:

| FR-1221 clause | Code | Test and assert |
|---|---|---|
| one content-addressed canonical JSON blob, referenced from the run | `model_schema/regression.py:259-268` `cases_log_bytes` (sorted keys, no whitespace) and `cases_log_sha256`; the handler stores `cases_log_bytes(log)` (`worker/rating_handlers.py:194`) | `backend/tests/test_regression_runs.py::test_a_regression_run_is_a_202_job_that_persists_the_run_and_its_case_blob` (`FR-261`, `FR-260`): reads the blob by `row.cases_blob_sha256`, parses it, `assert cases_log_sha256(log) == row.cases_blob_sha256`; `test_the_scalar_blob_digest_equals_the_runs_cases_blob` (`FR-261`, `NFR-499`) |
| replayed by re-scoring, never regenerated | `pricing_core/rating/replay.py`; `.importlinter` `replay-never-generates` forbids `hypothesis` and `pricing_core.rating.testing`, `allow_indirect_imports = false` | `packages/pricing-core/tests/test_replay.py::test_a_replay_re_scores_the_persisted_cases_and_never_generates` and `test_replay_module_does_not_import_hypothesis_or_testing` (`FR-261`); `tests/test_repository_invariants.py` pins 4 contracts (`FR-9`) |
| read only with `rating:read` | `api/models.py` `get_regression_run` and `get_regression_run_cases`, `requires(Perm.RATING_READ)` | `test_the_case_blob_and_the_run_row_are_refused_without_rating_read_or_across_workspaces` (`NFR-499`, `FR-261`): 403 on both routes for a member with no role |
| … in its workspace | `platform/regression_runs.py:51-60` `fetch_run` filters `RegressionRunRow.workspace_id == workspace_id` | **no test fails if that filter is dropped** (established by reading the tests; not mutation-proven, since the auditor ran no database test). The same test's cross-workspace limb uses a principal who is not a member of the other workspace and asserts `status_code in (403, 404)`, so the membership check answers before `fetch_run` runs. `test_the_lookup_is_scoped_to_the_workspace` covers `latest_run`, not `fetch_run`. |
| the generic blob route refuses it (the `07:307` obligation) | `platform/blobs.py` `QUOTE_INPUT_BLOB_COLUMNS` holds `RegressionRunRow.cases_blob_sha256` | the same test, limb 2: the digest is made ownable by a Job in the caller's workspace, and `/api/v1/blobs/{digest}` still answers the same 404 and code as a missing blob. `LG-1225` records the mutation: removing the column turns it red |
| never logged | `worker/rating_handlers.py` sanitiser (#889) | `test_a_failed_run_puts_no_quote_input_in_the_job_error` and `test_a_validation_error_inside_a_run_never_puts_a_quote_input_in_the_job_error_or_the_logs` (`NFR-499`): a sentinel input is absent from the stored error and from the captured logs |

### FR-364's WK-672 clause (§0a)

`06:145`: *"`regression_run` becomes verifiable in WK-672 (`03` FR-261)"*. At `1c8762d9` it is:
`rating_versions.py:297` writes `"regression_suite_run_id"` into the evidence, and the limb-(1)
gate refuses a submission without a passing run. The tests assert it under `FR-257`
(`test_a_passing_run_is_recorded_and_golden_evidence_is_untouched` asserts
`evidence["regression_suite_run_id"] == str(run_id)`). **`effective_evidence("rating_version")`
still has no caller** (`git grep -n 'effective_evidence' -- backend/src` lists `metrics.py`,
`modelling.py` and `objectives.py` only). That is FR-364's own recorded state: *"Wiring the
rating-version check is WK-673's"* (RL-885; `RL-1184` E4).

### NFRs, measured (§4)

Two NFRs are in the union. Neither has a numeric budget that WK-672 owns.

- **NFR-499** (security; the quote-input stores). WK-672's limbs are measured as enforcement on
  broken input: the golden-quote store (S2, `LG-1204` G3: the route-level no-logging test with
  a non-empty capture and a positive control); the case store (S3: the deny-tuple mutation
  above, `LG-1225`); the compare route (S4: the `_maybe_sample_trace` spy goes red under the
  copied-sampler mutation, and the logging mutation turns `test_compare_logs_no_input_value`
  red, `LG-1230` *Plan deviations* 1); Job errors and logs (#889, WK-1178, on `main` in this
  tree). **The rate-limit limb is WK-674's** (`CR-1212` G4 (a), accepted by delegation).
- **NFR-502** (no outbound `response_model` on scoring). The compare route returns a raw
  `Response`; `grep -nE '^\s+response_model=|\) -> (ScoreComparison|ScoringResult)'
  backend/src/app/api/score.py` prints nothing (rc 1) at `1c8762d9`, and the same pattern on a
  two-line positive control counts 2 (`06-s4-acceptance-greps.log`). Its one marker is WK-671's
  `/score` test (`test_score.py:341`); the compare route has no NFR-502 marker. **Its latency
  measurement is WK-674's** (`CR-1212` G4 (b)).

### The gate

The auditor ran no full gate (the lead's instruction). `main`'s CI at the audited tree:
**python run `36584757193`, `headSha 1c8762d9…`, `success`**. Its log reads
`3827 passed, 3 skipped, 46 warnings in 557.66s (0:09:17)` and `GATE: pass — 8 of 8 stages passed`.
The frontend workflow did not run at `1c8762d9` (path-filtered); its last run on `main` is
`36572736840` at `c9f50232`, `success`, and `git diff --name-only c9f50232 1c8762d9 -- frontend
docs/contracts pnpm-lock.yaml` is empty. The docs workflow's last run is `36581460367` at
`9cd179cb`, `success`. The four docs checks on this branch are in the PR body.

### Retrofit-impossible list (§5)

Mapped against `docs/process/retrofit-impossible.md` at `1c8762d9`. **All eight landed in
Phase 1a; WK-672 preserved each, and regressed none that this audit read.**

| Item | WK-672 |
|---|---|
| Audit log in the caller's transaction (`06` FR-368) | a suite version's creation event; the delta's author is read from it (`test_every_version_has_one_creation_event_and_no_context_is_logged`, `test_golden_a_suite_version_with_no_creation_event_refuses_submit`) |
| Artifact immutability and versioning | Regression Suites are versioned (`/regression-suites/{slug}/versions`); a submission pins the suite by content hash (`test_golden_a_later_suite_version_does_not_change_what_was_pinned`) |
| `model-schema` as the single source | every new shape is in `model_schema` (`regression.py`, `scoring.py`); `generate-contracts.py --check` rc 0; no compare shape outside it (`LG-1230` item 4) |
| The Job model | a regression run is a 202 Job with cancellation (`test_a_cancelled_run_ends_the_job_cancelled_not_failed`) |
| Decimal money | golden quotes compare integer minor units and refuse a float (`test_money_and_tolerance_refuse_a_float`, FR-273) |
| `trace_id` propagation | not touched; the regression Job runs on the existing Job path |
| RBAC from the first endpoint | every new route declares its permission and has a 403 test |
| Content-addressed blob store | the case log is a content-addressed blob (FR-1221) |

### Binding plan-review conditions (§5a)

Predicate: every "Maintainer acceptance" section and acceptance entry under `docs/closures/`,
searched from its first occurrence to the file's end for `WK-672`, each hit read. Only
`CR-1212` (plan review 15) conditions this close:

1. **Proposal 1, amendment 1** (accepted 2026-09-28 19:05:44 BST): *"**`gates:` and `target:`
   stay `~`** until the lead proposes three freeze dates and a target after WK-672 closes. They
   are declared before the first of them passes."* **The artifact it demands:** the lead's
   proposal of three dated freeze gates (plan, code, docs) and a target for `## P2`, put to the
   maintainer. **Owed after this close**, owner the lead; it does not exist yet, and cannot
   before the close is accepted.
2. **Proposal 2, the budget instruction** (quoted in `CR-1212`, accepted): *"No slice of WK-673,
   WK-674 or WK-690 starts, and no WK-675/1170/1169 planner is spawned, before WK-672 closes."*
   A gate, not an artifact: the maintainer's acceptance of this close lifts it.
3. **G6** (Proposal 1): *"A plan review 16 is filed after G1–G5 and before the demo."* It does
   not name WK-672's close. It is listed because FD-1209's event cites "plan review 16", and the
   maintainer's structure entry of 2026-09-29 also calls the §14 review at **this** close "plan
   review 16". See FD-1209 under *Findings*.

`CR-830` (plan review 8) and `CR-932` (plan review 11) name WK-672 in their acceptance
sections, but only about WK-671's boundary and WK-672's opening; neither conditions its close.

### Workflow steps citing in-scope requirements (§5c)

Predicate, verbatim: `git grep -n -E '\b(FR-(248|251|257|258|260|261|262|273|353|364|368|1221)|NFR-(499|502))\b'
1c8762d9 -- 'docs/workflows/WF-*.md'`: **20 lines** (WF-698 3, WF-699 9, WF-700 2, WF-701 4,
WF-702 2). Each was opened and read against the requirement's current text, including its dated
amendments, at `1c8762d9`. Coverage rows, which list a phase's ids and make no claim, are marked
as such.

| Journey | Step | Id | Reading |
|---|---|---|---|
| WF-698 | B11 | FR-368 | still says it |
| WF-698 | E9 | FR-353 | still says it |
| WF-698 | E — coverage row | FR-353, FR-368 | coverage row; no claim |
| WF-699 | D1 | FR-260, FR-261 | still says it (`run_regression` composes the golden quotes and the properties) |
| WF-699 | D2 | FR-260 | still says it |
| WF-699 | D3 | FR-260 | still says it (`GoldenQuote.note` exists; an update is a new suite version) |
| WF-699 | **D4** | FR-261 | **disagrees.** FR-261: *"the compiled bundle pins no Banding, so no band edge is in the grid, and an inversion narrower than the spacing … may not be detected until `OQ-1224` lands"*; *"A counterexample is the base context and the two adjacent grid values"*. D4 has the run find a break *"between 63 and 64"*, a band edge. **FD-9602** |
| WF-699 | D5 | FR-261 | still says it, given D4 |
| WF-699 | **E2** | FR-257 | **disagrees on the route.** E2: *"`POST /approval-requests`. Evidence completeness is checked at submission"*. FR-257 applies *"at submit"*, FR-260 (1) puts the check at `POST /api/v1/rating-versions/{id}/submit`, and the generic route refuses a draft Rating Version (`APPROVAL_SUBJECT_NOT_IN_REVIEW`). **FD-9603** |
| WF-699 | E8 | FR-353 | still says it |
| WF-699 | Golden quote mismatch (failure table) | FR-260 | still says it |
| WF-699 | D — coverage row | FR-257, FR-258, FR-260, FR-261, FR-262 | coverage row; no claim |
| WF-700 | F4 | FR-368 | still says it |
| WF-700 | F — coverage row | FR-353, FR-368 | coverage row; no claim |
| WF-701 | preconditions | FR-257 | still says it |
| WF-701 | A5 | FR-262 | still says it. FR-262 compares against *"a comparison version"*; "live" is resolved by naming the live version's ref until WK-674 (`PL-1213` *Carried out*) |
| WF-701 | A6 | FR-258 | still says it (the trace shows the step; see FD-9604 for `input` and `output` steps) |
| WF-701 | H6 | FR-260 | still says it |
| WF-702 | E6 | FR-368 | still says it |
| WF-702 | E — coverage row | FR-368 | coverage row; no claim |

Two disagreements, filed as FD-9602 and FD-9603. Neither is a verdict on this close; which side
moves is `CLAUDE.md` §0's question, for the decision-maker.

## Owed list

**Generated, verbatim** — `python3 scripts/register-owed.py WK-672` at the committed revision
`1c8762d9ed235f80e0f2fff80c44003694828e97` (`origin/main`, clean worktree; `08-register-owed-wk672.log`,
rc 0). It ran before this PR's register edits.

```text
Generated by `python3 scripts/register-owed.py WK-672` against `1c8762d9 (`wk672-close`)`.
Mode: work item 'WK-672'. 4 owed row(s), 3 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).

- **FR-257 (F44)** (work item: 'W11-2', phase: '2') — **carry forward with owners, per limb — limb (1) re-pointed to WK-672 Slice 3**, dated 2026-09-28, by `RL-1172` (#829, `62d5fbae`) item 4 and its obligations table (`RL-1172:315`, the auditor's row). Slice 3 owns FR-257 limb (1) on `submit_for_review`, with a limb-(1)-only marker. Limbs (2)–(4) are unchanged. Supersedes: carry forward with owners, per limb. **(3) delivered and, with Task 2C, attributed.** **(1) Regression Suite — WK-672**, the testing workstream that builds it. **(2) Dislocation Run — WK-673**, which builds FR-263; F-W9-2 already carries the FR-224 gate that specialises this limb, and the two resolve together. **(4) GIPP check — the optimisation workstream that owns `04`**, and it stays untestable until insurer enablement exists to condition it on. The WK-671 close must not read a single FR-257 marker as evidence of the gate: the marker Task 2C adds names limb (3) alone. **Limb (1) delivered 2026-09-29 by WK-672 Slice 3** (#886, squash `6a8b8e7011e472586be559587561dde0479d491f`): `submit_for_review` refuses with `EVIDENCE_INCOMPLETE` for no run, a failing run, a stale `bundle_hash`, another suite version, or an earlier pass followed by a later failure, and for a suite with no golden quote; the tests carry a limb-(1)-only `req("FR-257")` (`backend/tests/test_rating_versions.py`, from `test_no_regression_run_refuses_submission`), and `LG-1225`'s *Slice close* section names each. Limbs (2) and (4) are unchanged. Not read as evidence of limbs (2) to (4)
- **An intermittent native abort in pricing-core's cross-process determinism test (FD-1199)** (work item: 'WK-1178', phase: '2') — **deferred with an owner — the lead**, 2026-09-28, until triaged. Event: the triage (reproduce under load with N repeats), on plan review 15's risk list. If WK-672 Slice 2's N=5 gate run aborts, the triage moves ahead of Slice 2. Ownership shape: event
- **PL-1205 Task 0's precondition for PR 868 self-matches the plan's own squash commit body (FD-1208)** (work item: 'WK-672', phase: '2') — **carry forward, unowned**, proposed 2026-09-28; needs the deputy to rule on a dated correction to `PL-1205` Event: that ruling, or #868's merge with Task 5 Step 0 run in the subject-plus-symbol form. Ownership shape: event
- **The freMTPL2 demo has no real rating algorithm, and Slice 3's demo fixture does not satisfy G2 (FD-1209)** (work item: 'WK-672', phase: '2') — **deferred with an owner — the lead**, 2026-09-28 (the deputy's DP-S3-8 ruling). Event: the real freMTPL2 algorithm exists in the seed and `WF-699` runs end to end on it, due before plan review 16, not WK-674. Ownership shape: event

Excluded as opening with a resolution marker — verify:
- `03` §5.2's rating-engine signature blocks omit four live exports (F60)
- Dependency and workflow hardening (S2 version updates, S3, S4) (FD-1194)
- The blob download route serves trace quote inputs to any dataset-read holder, with no workspace scope (FD-1203)
```

**Reconciliation.** Every id in the generated block appears in *Findings* with a resolution, and
of the three excluded rows FD-1194 carries a residual item (the #852 hold), which *Findings*
resolves. *Findings* adds only FR-1221's marker gap and the S4 audit report's durability, which
have no register row, and FD-9602, FD-9603 and FD-9604, which this PR files.

## Findings

Every decision below is **proposed**; the lead sets each `decision:` (`document-ids.md` §1.6, FD
row).

| Finding id | Concerns | Proposed decision | Status |
|---|---|---|---|
| F44 | FR-257 limb (1) | limb (1) delivered (#886); limbs (2) WK-673, (3) delivered by WK-671, (4) the optimisation Work: unchanged *(open for limbs (2) and (4); nothing owed by WK-672)* | `closed-with-findings` |
| FD-1199 | the native abort in the determinism test | not WK-672's: its condition (S2's N=5 run aborting) did not fire (`LG-1204`); every S4 N=5×2 run passed, 20 of 20 *(unchanged, the lead's)* | `closed-with-findings` |
| **FD-1208** | `PL-1205`'s `git log --grep` precondition | **closed**: its own event (b) happened. #868 merged as `5ec47dc4` before S3's Task 5, and S3 ran the check in the subject-plus-symbol form (`LG-1225`, #886). No dated correction to the executed, frozen plan *(closed in this PR, row and essay)* | `closed` |
| **FD-1209** | the demo has no real freMTPL2 algorithm (G2) | **keep `deferred with an owner — the lead`**, and restate the event by role: *before `CR-1212` G6's pre-demo plan review*. Its event has **not** happened at `1c8762d9` (the seed's only algorithm is `_demo_algorithm()`, `examples/fremtpl2/model.py:327`; no `WF-699` journey test). "Plan review 16" now names both G6's review and the §14 review at this close; read as the latter, the event falls due at once and cannot be met, because the real algorithm is `WF-699` Phases A to C on the approved models and no WK-672 slice planned it. **Not a WK-672 deliverable; it does not block this close.** If the lead reads it the other way, it blocks plan review 16, not this close *(open, row and essay annotated)* | `closed-with-findings` |
| FD-1194 | the Dependabot hold: *"#852 is held until WK-672 closes"* | **the hold is moot.** Dependabot closed #852 unmerged at `2026-09-28T14:05:08Z` (*"Looks like these dependencies are updatable in another way, so this is no longer needed."*). The frontend dependency group now sits in **#857** (open; `frontend/package.json`, `frontend/pnpm-lock.yaml`), whose frontend CI (`success` at `7962b866`, 2026-09-28) predates S3's and S4's regeneration of `docs/contracts/openapi/generated.json`, so its gate should run on a merge with current `main` first. **Merging #857 is the user's, through the maintainer**; never the lead's or the auditor's. Nothing is recommended for #852 *(resolved row; its stale cell gets a dated note in #903 (auditor-a-2), not here)* | `closed` |
| FR-1221 (no row) | no `req("FR-1221")`; the workspace limb unproven | see *Verdict* *(proposed `fix before close`)* | `closed-with-findings` |
| S4 audit report (no row) | the independent S4 audit's report is not durable; only its verdict line is, in the squash body of `c9f50232` | **accept**, with a note for later slices: file the audit report, or its findings, where the ledger can cite it | `closed` |
| **FD-9602** | `WF-699` D4 vs FR-261's grid | **carry forward, unowned**; event: the decision-maker's ruling or `OQ-1224` *(filed in this PR)* | `closed-with-findings` |
| **FD-9603** | `WF-699` E2's route vs FR-257 / FR-260 | **carry forward, unowned**; event: the decision-maker's ruling *(filed in this PR)* | `closed-with-findings` |
| **FD-9604** | the trace omits `input` and `output` steps, FR-258 says every step | **carry forward, unowned**; event: the decision-maker's ruling *(filed in this PR)* | `closed-with-findings` |

**Status column.** The vocabulary is `work-item-close.md`'s: `closed` for a finding this close discharges, `closed-with-findings` for one carried past it. **Why FD-9602, FD-9603 and FD-9604 name WK-1178 in the register's Work item column:** WK-672 closes, and none of the three is WK-672's to fix (two are journey-versus-requirement questions, one is WK-671's FR-258); WK-1178 is P2's standing maintenance Work, so `register-owed.py WK-1178` lists them until the decision-maker rules. The routing is proposed; the lead may re-point it.

**FD-1208 and FD-1209: essays and rows.** Written by the auditor as they stand: FD-1208's essay
gains a *Resolution* section and `status: closed`; FD-1209's gains *Status at the WK-672 Work
close* and stays `active`; both register rows carry the dated text. The `decision:` in each row
is the lead's to adopt or amend before this PR merges.

## Verdict

Proposed verdicts for each requirement in the union. The four `CLAUDE.md` §13 verdicts apply to
a requirement without evidence; FR-1221 is the only one.

| Requirement | Proposed verdict | Evidence |
|---|---|---|
| FR-260 | delivered, tested | 49 markers in 7 files; the submit gate, the pin, the delta, the mismatch refusal |
| FR-261 | delivered, tested | 60 markers in 6 files; five property classes, the `monotone` grid, generation, replay |
| FR-262 | **backend limb delivered and tested (WK-672); UI limb reassigned to WK-675** (`RL-1172` §5) | 8 markers in `test_score_compare.py`; `PL-1213` items 1–12 (`LG-1230` *Slice close*) |
| FR-257 limb (1) | delivered, tested | 15 markers in 4 files. Limbs (2) to (4) are not WK-672's (F44) |
| FR-248 | delivered, tested (as a property class) | `test_property_ladder_reconciles`, `test_run_ladder_reconciles_fails_when_the_ladder_has_no_risk_premium_rung` |
| FR-273 | delivered, tested | `test_one_minor_unit_over_a_zero_tolerance_fails` |
| FR-364 (the `regression_run` clause) | delivered; evidenced under `FR-257` markers | *FR-364's WK-672 clause* above; the rating-version wiring is WK-673's |
| FR-368 | delivered, tested | `test_every_version_has_one_creation_event_and_no_context_is_logged` |
| FR-251, FR-258, FR-353 | consumed, unchanged; their markers predate WK-672 | FD-9604 is raised on FR-258 and does not change this verdict |
| NFR-499 | WK-672's limbs delivered and tested; the rate-limit limb is WK-674's | *NFRs, measured* |
| NFR-502 | the compare route conforms (grep with a positive control); the measurement is WK-674's | *NFRs, measured* |
| **FR-1221** | **delivered but untested**, under its own id | see below |

**FR-1221.** Its five clauses, and the `07:307` blob-route obligation, make the six rows of the clause table. Five of the six rows are asserted, exactly, by tests that carry `FR-261`,
`FR-260` or `NFR-499` markers (the clause table above). The sixth, the **workspace** limb of
*"read only with `rating:read` in its workspace"*, is delivered in `fetch_run` and asserted by
nothing that would fail if the filter were dropped. **Proposed decision: `fix before close`**, a
test-only PR in the pattern of #897:

1. stack `@pytest.mark.req("FR-1221")` on
   `test_a_regression_run_is_a_202_job_that_persists_the_run_and_its_case_blob`,
   `test_the_case_blob_and_the_run_row_are_refused_without_rating_read_or_across_workspaces`,
   `test_a_validation_error_inside_a_run_never_puts_a_quote_input_in_the_job_error_or_the_logs`
   and `packages/pricing-core/tests/test_replay.py::test_a_replay_re_scores_the_persisted_cases_and_never_generates`
   (stacked markers are an existing convention);
2. replace the cross-workspace `in (403, 404)` assert with a principal who holds `rating:read`
   in **both** workspaces, asserting 404 on the run and on `/cases`, and show it red under a
   mutation that drops `fetch_run`'s `workspace_id` filter.

**The fallback**, if the lead does not hold the close for it: `carry forward with an owner —
WK-1178`, with an `FD-` filed for it in this PR before the merge. Either way `scope-audit.py`
keeps exiting 1 on FR-1221 until the marker lands.

**The close, proposed.** WK-672 delivered its four charter items (FR-260, FR-261, FR-262's
backend limb, FR-257 limb (1)) and every requirement it composed or enforced, each evidenced at
`1c8762d9`. One requirement, FR-1221, is delivered but untested under its own id, with a
proposed pre-close fix. No finding owed by WK-672 is left without a proposed resolution. The
auditor proposes the Work close, subject to the lead's decisions above and the maintainer's
acceptance.

## Sign-off

- **The lead's decisions** on each proposed verdict and each `decision:`: *(to be written by the
  lead before the merge)*.
- **Maintainer acceptance of the Work close:** *(the maintainer's dated line)*.
