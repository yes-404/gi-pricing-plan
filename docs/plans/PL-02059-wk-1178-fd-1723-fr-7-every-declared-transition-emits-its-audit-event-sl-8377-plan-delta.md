---
id: PL-2059
family: plan
kind: map
title: WK-1178 — FD-1723's FR-7 limb, the misnamed audit events first, then every declared transition emits its event, SL-2060 — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-06             # original date 2026-11-05, set at the draft; filed under working id 8376, minted 2026-11-06
owner: planner
tree: 850cf225797c8a63065130dc9012a2ef31b5ef55
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1856, FD-1723, FD-2007, FR-7, FR-368, FR-369, FR-349, FR-350, FR-351, FR-353, FR-355, FR-146, FR-157, FR-154, FR-163, FR-238, FR-370]
---

# PL-2059 — WK-1178: FD-1723's FR-7 limb. The misnamed events first, then every declared transition (SL-2060, a dated Work-plan delta)

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L1 (a'): it `relates:` `PL-1856` and
> leaves it unedited. It replaces that plan's Slice D, never seated. One slice row, SL-2060. **All fifteen
> decision points are ruled and closed, and this text carries the rulings.** The status stays `draft` until
> the mint, and the slice GO stays the maintainer's. The executor's skills are
> `superpowers:test-driven-development`, `.claude/skills/python-test` and `.claude/skills/spec-change`.
> PL-2059, SL-2060 and LG-2061 were working ids 8376, 8377 and 8378 (reserved by the lead), minted 2026-11-06.

## Authority

- **The limb.** `FD-1723` row FR-7, `:78`: MEDIUM, "Fix in P2, test only (corrected 13:55:54)"; "takes its
  transition list from the SPEC and the declared lifecycles … NOT from the 79 `audit.record(` call sites"; "a
  transition with no audit is the red"; the census printed; "any site matching no declared transition is
  listed". Essay `:84`: "A list derived from the call sites certifies only that the code audits what it
  already audits."
- **The parent.** `PL-1856` Slice D (`:529-538`), Acceptance 16 (`:381`), DP-C ruled TESTS (the entry
  "2026-10-22 16:02:49 BST"). Its Task D0 is done: the evidence below.
- **This seat.** To-lead "2026-11-05 16:21:19 GMT" item (2): D0 accepted as read-only evidence; a plan seat, no
  build; "Exception stands until the plan". Item (2b): "'Whether FR-7 covers creation events is open' = an OQ
  candidate in that plan, not a seat's pick"; "the plan puts those 3 first". Item (2), on revocation:
  "'no audit writer' understates it: role revocation is NOT BUILT on this surface." Item (2a): each listed item
  takes one of §13's four verdicts at the §14 draft, none silent.
- **The rulings.** To-lead "2026-11-05 16:39:14 GMT", all fifteen, quoted under **Decision points** below. It accepts
  the behaviour change in a limb ruled "test only": "The behaviour change is accepted against 'test only'."
- **The freeze.** Register `:373` dated line of 2026-11-05 and the entry "2026-11-05 10:31:31 GMT" item (5): FR-7,
  about 12 h, is one of three named freeze exceptions. Dates of record: code freeze Thu 12 Nov, docs freeze Fri 13
  Nov, exit demo Wed 18 Nov ("2026-11-05 09:58:58 GMT"). Chain order: "D, F, run 3, A, C, H, R2, LAST-1,
  LAST-2 + T, G, M, then additions" ("2026-11-05 15:55:35 GMT").

## Goal

An audit-trail reader is no longer told a failed certification "certified". Then every declared transition of a
governed Artifact has a test that fails if its Audit Event goes missing or leaves its transaction, and every
declared edge either has that test or a named reason, so a new edge cannot arrive unnoticed.

## Evidence at `bdad1322` (tree `850cf225`), read-only

Source: `~/gi-pricing-plan.local/handover/fd1723-d0-enumeration-2026-11-05.md`, sha256 prefix `16fbc1666b30`,
written by exec-d0 from the spec first and then the code. Each cite used here was re-read at `origin/main`
`bdad132291fdc05fe233d3ddc946e413dcbd2e1f`. Line numbers hold at this tree only. A `:N` with no path is the
file the row names.

**D0 reproduces.** `git grep -n -F 'audit.record(' origin/main -- backend packages ':!*/tests/*'` prints 83 lines; with
tests, 95. D0's 82 AST sites are the same set: `comm` against `scratch/d0/census_parsed.txt` leaves one line,
`platform/audit.py:73`, the `RuntimeError` text. Eight maps, by the `VALID_.*TRANSITIONS\s*[:=]` predicate. Their
edges, enumerated by importing the maps at this tree: approval 7, dataset 9, job 6, metric 8, model 8, objective 8,
peril 8, rating 3, **total 57**.

**Five corrections to D0 and its brief, found by that re-read.**

1. **`06:154` and `:155` hold FR-368 and FR-369**, not `:152` and `:153`. The clauses D0 quotes are right.
2. **The third "misnamed" event is a decision verb, not a state.** The action is
   `f"approval_request.{decision.value}"` (`approvals.py:481-486`), and `DecisionKind.APPROVE = "approve"`
   (`model_schema/approvals.py:66`), so the string is `approval_request.approve`, pinned at
   `backend/tests/test_approvals.py:501`. D0 read this row as "defensible, record only"; the string it would be
   compared with, `approval_request.approved`, is emitted by nothing. The other two say a state that did not
   happen. This one says a decision that did happen. See DP-2.
3. **U3 resolved: `certified → draft` happens, at the misnamed site.** `certifiable_or_refuse`
   (`objectives.py:559`, and the metric's route `custom_metrics.py:284`) admits `draft` and `certified`. So a failed run is
   `draft → draft` (no edge: a certificate is recorded and nothing moves) or `certified → draft` (edge O5), and
   both write `custom_objective.certified`. The same holds for the metric. **The misnamed site is therefore one row
   of D0's "unclassified" as well as O1b.**
4. **D0's 12 and 13 are both right, for different sets.** §2's 12 GAP-B edges are 11 map edges plus `live →
   retired`, which is in no map. §6's 13 adds R4 (`draft → approved`), a map edge with no reachable writer. Of the
   57 map edges, 12 have no writer: 11 + R4. In §1.8 "DIS (F3)" on R5 points at a label §4(c) uses for `00:128`;
   R5's disagreement is FR-238 against the map.
5. **U4 understated, as the entry says.** `RoleAssignmentRow.revoked_at` has readers (`rbac.py:183`, `:245`,
   `approvals.py:663`, `me.py:133`) and no app writer; `06` §5.1 `:568-570` has `POST /role-assignments` and no
   revoke route. Role revocation is not built on this surface. Only a Service Account key revocation is
   (`service_accounts.py:362-363`, audited). Break-glass expiry is a read: `rbac.py:190` compares `expires_at`
   with now, and nothing changes at expiry, so no state transition exists to audit.

**Two of D0's other open rows close by reading.** U6: `schema_corrected` is `draft`-only, checked by its caller
(`api/datasets.py:781`), so FR-4 holds; its `entity_ref` form stays DP-13. U7: `api/dataset_versions.py:208` reaches
`promote_using_report` and `archive_version`; the rows are service calls either way.

**One new observation, by reading only, not proved by a run.** `record_certificate` writes `row.status` from
whatever the row holds (`objectives.py:670`, `metrics.py:459`), and neither it nor the worker
(`model_handlers.py:1655`, `:1703`) re-checks status. The route's refusal (`objectives.py:559`) runs before the
Job exists. So a run queued at `certified`, then `submit_for_review`, then a result, moves a version in `review`
to `draft` or `certified` while an approver reads it. `review → draft` is in no map. That is what the
route's docstring says must not happen. The maintainer's read agrees on the code: "record_certificate
(objectives.py:636) has no status check, by my read, and the docstring's 'leaves the objective in draft' assumes a
start it doesn't verify". T1's red is the first run. See DP-3.

**The row table.** The expected `action` is the spec's where a spec names it, else the module's existing string;
`06` §4.5 `:534` keeps no table of names. Under the rulings. **Bold** = changes in this slice.

| Lifecycle | Edges and action | Performer, `backend/src/app/` | Rows |
|---|---|---|---|
| Custom Objective | `draft>certified` `.certified`; **`draft>draft`, `certified>draft` `.certification_failed`**; `certified>review` `.submitted`; `review>approved` `.approved`; `review>certified` `.certified` | `platform/objectives.py` 670, 786, 861 | 6 |
| Custom Metric | the same six, `custom_metric.` | `platform/metrics.py` 459, 543, 620 | 6 |
| Approval Request | `review>approved` etc. `approval_request.approve`, `.reject`, `.request_changes`; first of two, status stays `review`, `.approve`; `review>withdrawn`, `approved>withdrawn` `.withdrawn` | `platform/approvals.py` 476, 535 | 6 |
| Rating Version | **`draft>review` `rating_version.submitted`**; `review>approved` `.approved`; `review>draft` `.returned_to_draft` | `platform/rating_versions.py` 486, 540 | 3 |
| Deployment Request | `review>approved`, `>rejected`, `>withdrawn` `deployment_request.<target>`; **`approved>executed` `deployment_request.executed`** | `platform/deployments.py` 475, 609 | 4 |
| Dataset Version | the 9 map edges, `dataset_version.<target>` | `platform/datasets.py` `_transition` 595 | 9 |
| Model | `draft>fitted` `model.fitted`; `fitted>review` `.submitted`; `review>approved` `.approved`; `review>fitted` `.fitted`; `approved>superseded` `.superseded`; three `>archived` `.archived` | `platform/modelling.py` 949, 1298, 1495, 1558, 1593 | 8 |
| Peril Structure | `draft>reconciled` `.reconciled`; `reconciled>review` `.submitted`; `review>approved` `.approved`; `review>reconciled` `.reconciled`; `approved>superseded` `.superseded` | `platform/perils.py` 266, 348, 557, 772 | 5 |
| Validation Rule | `draft>review` `.submitted`; `review>approved` `.approved`; `review>draft` `.draft` | `platform/validation_rules.py` 475, 561 | 3 |
| Reference Table Version | `draft>published` `.published` | `platform/reference.py` 229 | 1 |
| Job | the 6 map edges, `job.<target>` | `platform/jobs.py` 228 | 6 |
| **Sum, transition rows** | 45 map edges + 12 others: the Rating Version return, three rule edges, one reference edge, four request edges, the two `draft>draft` and the first of two | | **57** |
| Creation rows, under DP-4 (a) | `dataset_version.created`, `validation_report.created`, `model.reserved`, `custom_objective.created`, `custom_metric.created`, `peril_structure.created`, `validation_rule.created`, `rating_version.created`, `approval_request.submitted`, `deployment_request.created`, `job.submitted`, and the four `rate_table_version.` strings of `03:488-501` | D0 §1 | **15** |

Parts sum: 6 + 6 + 6 + 3 + 4 + 9 + 8 + 5 + 3 + 1 + 6 = 57. Separately, 45 of the 57 map edges have a writer and 12 do not.

**No consumer breaks.** Readers of the `action` column in app code: `api/audit.py:138`, `:150` (filter and search),
`rating_versions.py:1309` (`rating_version.approved`), `approvals.py:586` (creation actions). Neither `.certified` nor
`approval_request.*` is read. The only test pin on `.certified` is a success path, `test_model_nfrs.py:186`. No spec,
workflow, contract or frontend file names `custom_objective.certified`, `custom_metric.certified` or
`deployment_request.executed`, by `git grep` over `backend packages frontend/src scripts docs/specs docs/contracts
docs/workflows`. `ACTION_PATTERN` (`model_schema/audit.py:40`, `^[a-z_]+\.[a-z_]+$`) admits every new name, and
`action` is a `str`, so **no contract changes**. `_decision_moves` (`test_api_approvals.py:1130`) already excludes
`f"{artifact_type}.submitted"`, so `rating_version.submitted` breaks nothing there. Exact action-list pins:
`test_datasets.py:510`, `test_worker.py:153`, `test_blobs.py:255`; none meets a changed site.

**Stored rows stay as they are.** FR-370 makes the table append-only, and each event is in a hash chain. A
pre-merge `.certified` row with `after.status = draft` stays. Its `after.overall` says `failed`, so a reader can
still tell, and the `02` clause says so.

### The chain's collisions

Measured for each of 15 local chain branches: `git diff --name-only $(git merge-base <b> origin/main) <b>`, and
`git diff -U0` for spec hunks, against this write set.

| Slice | Shared | Reading |
|---|---|---|
| A SL 8325 @`e75e0f1a` | `platform/datasets.py`, read only | D1's Dataset rows name `_transition`. Re-read at base. |
| SL 8368 @`1fedb56f` | `platform/modelling.py`, read only; `02:1920` | The archive route's permission. D1 calls the service, so no row moves. |
| H SL 8334 @`ca63dd15` | `backend/tests/conftest_db.py`, read only | +56 lines of guards. D1's fixtures take them at the re-merge. |
| R1 SL 8322, R2 SL 8345, LAST-1 SL 8340 | `platform/rate_tables.py`, read only | The four `rate_table_version.` rows. Re-read at base. |
| R2 SL 8345 @`e6d141ba` | `03:139` | FR-239's row, the line after this plan's FR-238 clause at `:138`. **An adjacent-line merge conflict is likely**; mechanical. |
| SL 8361, SL 8370 | `06` `:284`, `:563-:604`, `:764`; `02:1895`; `03:1089` | Clear of `06:85`, `:92`, `:154`. |
| M SL 8359 | `02` `:303`, `:315`, `:3417` | Clear of `02:246`, `:257`. |
| LAST-1 SL 8340 | `00:234` | Clear of `00:128`. |
| FD-1381 TRACK A, SL-2085 | `docs/specs/` §4 sections and fence lines | Two of this plan's lines share a §4 section with TRACK A's blocks: `02:1664` in §4.10 (between fences `:1596` and `:1683`) and `03:1044` in §4.12 (after fence `:1006`). Different lines, no fence touched here. Whichever merges second re-reads. TRACK A has no branch to measure yet, so this is read from PL 8372's block list. |
| M SL 8359, SL 8361 | `docs/open-questions.md` | Added at the fold: each writes OQ rows there (`913b4674`, `19b87d07`), and DP-4's and DP-11's OQs land after them. **An append-position conflict is possible**; mechanical. `00` §10, `03` §10 and `docs/roadmap.md` §10 were not measured at the fold and are re-read at the re-merge. |
| D, F, G, LAST-2 + T, P | none | No path in common. |

`docs/INDEX.md` and `docs/roadmap.md` are shared with every slice, by re-merge. No chain branch writes any of the five
platform files this slice edits, `model_schema/rating.py`, `model_schema/approvals.py`, or a new test file. **So
the predicted conflicts are `03:138-139` and the tail of `docs/open-questions.md`.**

## Decision points

All fifteen are closed, by the maintainer's entry "2026-11-05 16:39:14 GMT". Each row states the question, quotes the ruling
verbatim, and says what it fixes. Options that were not taken are in this file's history at `80e6448a`.

**Carries, the one change to the recommendations.** The ruling: "'a later phase names the owner' is refused: §14:
'unowned' is not a permitted state: each carry is OWNED BY THE P2 CLOSURE RECORD's carry-forward list now, as FD-2007, and the
§14 review proposes the P3 Work. Same for DP-8's rename, DP-13's F5, DP-14's items." The six carries are in the table after DP-15.

- **DP-1: the failed certificate's name.** "DP-1 (a) `.certification_failed`, spec clauses at FR-146, FR-157." So
  `<type>.certification_failed` on every failed run, `draft → draft` or `certified → draft`; `before.status` and `after.status` tell them apart.
- **DP-2: `approval_request.approve` on the first of two.** "DP-2 (a): the event is true and FR-368 lists decisions; the §14 list reads
  2 misnamed + 1 decision name, by dated line: my '3 misnamed' was D0's count, corrected." So the string stays. T1 pins `after.status = review` and
  `approvers_recorded`, and a dated clause at FR-368 says `approval_request.<decision kind>` names a decision, not a state.
- **DP-3: the unguarded certificate write.** "DP-3 (a), AMENDED: red first; a green red withdraws it. On a run that ends after submission: the
  certificate row is kept, status moves NOTHING and `certificate_id` is NOT repointed (an approver reviews what was submitted), and
  `<type>.certificate_recorded` carries the result, passed or FAILED, in `after`: a failed run landing under a review must be readable, so it
  cannot be swallowed as 'moved nothing'. Whether it should halt the review is the OQ candidate of the same row, not this slice. The behaviour
  change is accepted against 'test only'." So "after submission" reads as any status outside `draft` and `certified`: `review` and `approved` are the two A4 tests.
  The Job does not fail. **A green red withdraws the guard, `.certificate_recorded` and their clause, and LG-2061 says so.**
- **DP-4: does FR-7 cover creation?** "DP-4 (a), dated clause at FR-7, recorded as the OQ's resolution, mirrored; the rest stay census-only." So
  yes, for each type in `00:200` and FR-353's seven, and for the entry into the Approval Request, Deployment Request and Job lifecycles: 15 rows. Question of
  record: *"Does FR-7's 'state transition' include the event that brings a governed Artifact into existence?"* The other creation and recording sites
  (`backtest.recorded`, `profile.created` and others in D0 §3) stay in the census, unasserted.
- **DP-5: a catalogue of action names.** "DP-5 (a)." No table: each module names its strings, as `06:534`'s dated note says, and this plan adds its names beside their requirements.
- **DP-6: the two built transitions.** "DP-6 (a); my acceptance is the dated clause `03:1044` needs." A writer each: `rating_version.submitted`
  (`rating_versions.py:486`) and `deployment_request.executed` (`deployments.py:609`).
- **DP-7: scope of the rows.** "DP-7 (a)." FR-7 only: the eleven lifecycles above, Job included. FR-368's other classes (D0 §1.15) stay census-only;
  `deployment.*` keeps its own tests, e.g. `test_deployments.py:542`.
- **DP-8: the four shared names (COLL: M4, O4, the metric return, P4).** "DP-8 (a), P3 carry below." Keep them; each row asserts `before` and `after`. The rename to `<type>.returned` is carry C1.
- **DP-9: Custom Objective and Custom Metric `→ deprecated`, 6 edges.** "DP-9 (b), DP-10 (b) ACCEPTED ON ONE CHANGE", the carry paragraph above. Spec, not writer: a dated clause at FR-163 and FR-154 that no
  P2 path performs it, and that the carry's owner is the P2 closure record's carry-forward list. The edges stay in `NOT_BUILT`, under T3's guard. Carry C2.
- **DP-10: Peril Structure `→ archived`, 3 edges.** The same ruling: a dated clause at `02:1664`, as DP-9. Carry C3.
- **DP-11: Rating Version, F2, R4, R5, R6.** "DP-11 (a), new OQ for `retired`." A clause at FR-238 that `live` and `retired` are never stored, `live` being a
  Deployment's property, evidenced by `deployment.*`. Correct `VALID_RATING_VERSION_TRANSITIONS`: add `review → draft`, drop `draft → approved`, fix the comment.
  Nothing else moves. T3's completeness test is then the map's reader. What `retired` means goes to the new OQ, drafted under Needs.
- **DP-12: Approval Request `draft → review`, `changes_requested → draft`, 2 edges.** "DP-12 (a)." A clause at FR-351, drop both edges, fix the comment at `model_schema/approvals.py:80`.
- **DP-13: the spec-only rows.** "DP-13: clause, pointer, carry: the spec sides are accepted as the plan states them." F1: a dated clause at FR-351 that `peril_structure` has a decision hook,
  `perils.py:498`, wired at `api/approvals.py:566`, tested at `test_api_approvals.py:1051-1053` (FD-1456); `dataset_version` has none, so that half stands. F3: a dated pointer at `00:128` to `01:262`.
  F5: FR-369's form is missed by `ingestion.py:492` and others in D0 §4(c): carry C4; each row pins the `entity_ref` it finds. **No RL and no decision-maker seat: this entry is the ruling.**
- **DP-14: what is not built.** "DP-14: (a) verdict 'not started', role revocation, carried: `revoked_at` is honoured on read and has no writer; the record says both. (b) by clause, citing rbac.py:190, plus the test
  that proves an expired grant confers nothing, named by the seat; if none exists, T adds it. (c) carried, one line."
  (a) is carry C5. (b): **the test exists, so no task adds it:** `backend/tests/test_rbac.py::test_break_glass_is_time_boxed_and_expires` (`:343`, marked FR-349). After the expiry
  edit it asserts `Permission.APPROVAL_DECIDE not in held`. That is one permission, not `held == frozenset()`; what covers the rest is `rbac.py:190-191`, whose `continue` skips the whole assignment. A12's
  mutation is the proof that the line carries the assert, since this test has not been shown red. The clause at FR-349 says expiry is a read, nothing changes at expiry, so no state transition exists to audit,
  and the grant's event records `expires_at`. `grant_break_glass` has no application caller (OQ-1944), so the test runs as the owner. (c) is carry C6.
- **DP-15: ordering against the freeze.** "DP-15 (a)." "SEATING: a build seat after M in the additions, T1 + T2 first; 2 DB windows under 14:40:19 + (j)." One slice, one gate. T1 and T2 commit first. If T3 is not
  done by the re-baseline before Wed 11 Nov 12:00, the head at T2 gates alone, T3 stays the named exception, and the lead reserves a second `SL`. "Freeze: ~14 h + gate fits on today's picture; if not, DP-15's fallback fires: named, not silent."
  The recomputed figure under Needs is above that ~14 h.

**The carries. Each is owned now by the P2 closure record's carry-forward list, as FD-2007, and the §14 review proposes the P3 Work.**

| Carry | What | Ruled by |
|---|---|---|
| C1 | The rename of the four shared names to `<type>.returned` | DP-8 |
| C2 | Custom Objective and Custom Metric `→ deprecated`: 6 edges, two routes, and OQ-609's selection refusal | DP-9 |
| C3 | Peril Structure `→ archived`: 3 edges, one route | DP-10 |
| C4 | FR-369's `entity_ref` form, missed by `ingestion.py:492` and the others in D0 §4(c) | DP-13 F5 |
| C5 | Role revocation, verdict "not started": `revoked_at` is honoured on read and has no writer, with FR-350 | DP-14 (a) |
| C6 | `traces.py:297`: no caller outside `test_traces.py`, and the first route to call it owes an event | DP-14 (c) |

**P2 or carried, as ruled. The §13 verdict on each stays the lead's at the §14 draft, except where the row quotes one.**

| 16:21:19 (2a) item | Disposition | DP |
|---|---|---|
| 2 misnamed + 1 decision name | 2 fixed, 1 pinned, P2 | 1, 2 |
| The 2 built with no event | fixed, P2 | 6 |
| The 12 edges | 9 carried (C2, C3); 2 approval, removed; `live → retired`, clause; plus R4, removed | 9 to 12 |
| FR-351 vs `perils.py:557` | clause, P2 | 13 |
| `VALID_RATING_VERSION_TRANSITIONS` | corrected, P2 | 11 |
| `00:128` | pointer, P2 | 13 |
| Role revocation | carried, C5, verdict "not started" | 14 |
| Break-glass expiry | clause + named test, P2 | 14 |
| `traces.py:297` | carried, C6 | 14 |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's merge tree. Items 1 and 2 apply
to this plan; A1 to A14 apply to the slice, as ruled on 2026-11-05.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing line except check 31 / check 32
   lines naming working ids 8376, 8377 or 8378. After the mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no line that stands for a set of ids.

The slice:

- **A1. The misnamed events go first.** `git log --reverse --format=%s origin/main..HEAD --no-merges`: the first code commit is T1.
- **A2. A failed certificate says so.** `backend/tests/test_audit_transitions.py -k certification_failed`: `test_a_failed_certificate_says_so`, four cases, and the rows named for that action. Each failed case has action
  `<type>.certification_failed`, the true `before.status` and `after.status`, and `after.overall = failed`. Red at base by its cause; red
  under the mutation that restores the old string.
- **A3. The first of two is pinned.** The row asserts `approval_request.approve`, `after.status = review`, `approvers_recorded = 1`.
- **A4. A late certificate moves nothing and is readable (DP-3).** `-k certificate_recorded` collects 8 cases: `review`, `approved` × passed, failed × objective, metric. Each: the certificate
  row exists, status and the row's `certificate_id` are unchanged, and exactly one event `<type>.certificate_recorded` has `before.status == after.status` and `after.overall` equal to the run's result.
  Red at base. If they are green at base, the row is withdrawn and LG-2061 says so.
- **A5. The two built transitions have events.** `rating_version.submitted` and `deployment_request.executed`: each red at base, with `entity_ref` the
  version's and the request's own ArtifactRef, and a query by that `entity_ref` returns it.
- **A6. Every row, two legs.** One case per row of the table above, × `commit` (exactly one event with the row's `action`, `before.status`, `after.status`) and
  `rollback` (a raise inside the same `unit_of_work` leaves the status at `before` and no event). `pytest --collect-only -q
  backend/tests/test_audit_transitions.py -k test_a_declared_transition_writes_its_event_in_its_transaction` shows 144.
- **A7. Every declared edge is accounted for.** `test_every_declared_edge_has_a_row_or_a_reason` is DB-free and reads the eight maps by
  import. Mutation: add a planted edge to a copy of one map, and it reds naming the edge. `test_a_not_built_edge_has_no_writer` reds on a planted
  `row.status = ObjectiveStatus.DEPRECATED.value` under `backend/src`.
- **A8. A deleted event fails its row.** One mutation per writer module: `objectives`, `metrics`, `approvals`, `rating_versions`, `deployments`, `datasets`,
  `modelling`, `perils`, `validation_rules`, `reference`, `jobs`, deleting one `audit.record(` call. LG-2061 quotes each red, `git diff --quiet -- backend/src`
  rc 0 after each. Eleven mutations.
- **A9. The census is printed, by its predicate.** LG-2061 carries `git grep -n -F 'audit.record(' <head> -- backend packages ':!*/tests/*'`, its
  count, the AST count and each site matching no row, with the reason. The list of rows is the table's, and is never derived from this.
- **A10. A case red with no mutation is a STOP** (`PL-1856` constraint; seat brief item 13), other than A2, A4 and A5's reds at base, which are expected and named.
  Any other: stop, quote it, no assert softened.
- **A11. Spec and code in one commit.** Each new action name and clause lands in the commit of its code. `git diff --name-only origin/main...HEAD -- docs/contracts
  frontend deploy` prints nothing. `uv run python scripts/generate-contracts.py --check` rc 0.
- **A12. An expired grant confers nothing (DP-14 (b)).** The clause at FR-349 cites `rbac.py:190` at the slice's base and names `test_break_glass_is_time_boxed_and_expires`. Mutation: delete the two lines of the `expires_at` check
  in `effective_permissions`, and `-k test_break_glass_is_time_boxed_and_expires` reds on its last assert. LG-2061 quotes the red, `git diff --quiet -- backend/src` rc 0 after. This test run is DB-backed: window 2, both URLs on the copy.
- **A13. The OQs are mirrored (DP-4, DP-11).** For each of the two ids, `git grep -l <id> -- docs/open-questions.md docs/specs/` names `docs/open-questions.md` and its spec, `00` or `03`. DP-11's is also in `docs/roadmap.md` §10. DP-4's row reads decided and cites the clause at FR-7.
- **A14. Each carried clause names its owner.** `git grep -n 'carry-forward list' -- docs/specs/02-modelling.md` prints the clauses at FR-154, FR-163 and `02:1664`. `NOT_BUILT` has 9 entries, each with a non-empty reason.

## Global Constraints

- **The list comes from the spec and the maps, never from the sites** (`FD-1723`, 13:55:54). Rows are written from the table above, and a site read is a check.
- **`audit.record` stays in the caller's transaction** (`06` R2, `platform/audit.py:52`). No writer gets its own commit.
- **Requirement ids are permanent** (`CLAUDE.md` §5). Clauses are dated and appended in the row; no new FR id is needed. A new term goes in `00` §2 first.
- **No stored event is rewritten** (FR-370).
- **Nobody hand-writes a shape in `model-schema`** (`CLAUDE.md` §2); no new shape here. `backend/tests/` imports the maps; it never restates them.
- **No id range in any file this slice writes.** Requirements are named one by one.
- **A window's conditions are the grant's**, quoted under Needs. A condition that cannot be met is a STOP, never a substitute.
- **The barred word.** Write "the maintainer (by delegation)". Commit trailer per the common seat brief, item 7.

## Needs

- **Seats:** one executor, seated after M in the additions, T1 + T2 first; one auditor. DP-13 needs no decision-maker. Audits take precedence when the cap binds.
- **Ids, not reserved:** one `FD-` the lead routes for the two misnamed events, the two unevented transitions and, if DP-3's red holds, the certificate write (`PL-1856`: "STOP to the lead, who routes a new FD"; the reds are known in
  advance, so the FD can precede the slice). The six carries need a record with FD-2007's owner line; the proposal is one `FD-` with six limbs and one register row, and the routing is the lead's. Two `OQ-` ids, both below. PL-2059, SL-2060 and LG-2061 are held.
- **The two OQs, both in the Write set.** Each is mirrored in `docs/open-questions.md` and its spec's §10.
  - **DP-4's, raised and decided at once, `00` §10.** *"Does FR-7's 'state transition' include the event that brings a governed Artifact into existence?"* Decided by DP-4 (a); the resolution is the dated clause at FR-7, which it cites.
  - **DP-11's, open, `03` §10.** Draft: *"What does a Rating Version's `retired` mean, given that neither `live` nor `retired` is stored and no trigger for `retired` is specified?"* Proposed owner the P2 closure record's carry-forward list, with a row in the `docs/roadmap.md` §10 "Before Phase 3" gate. The ruling names neither; both are the lead's to confirm.
  - **Not in this slice: DP-3's candidate.** *"Should a failed certificate landing under a review halt the review?"* The ruling calls it an OQ candidate, so it gets no id and no row here. It goes to the lead with the §14 list, and if raised it belongs in `02` §10.
- **Gate cost: one SOLO full gate, about 2.5 h, no compose build, no timed path changed.** `audit.record` is added to two non-scoring writes, and to no scoring path. `deployment_request.executed` adds one insert to the deploy transaction that NFR-494's 30 s covers. No reading is proposed for it; that is the auditor's to confirm. **No frontend, contract or migration change.**
- **DB windows: two, under to-lead "2026-11-05 14:40:19 GMT" and (j) of "2026-11-05 15:49:09 GMT".** Window 1, T1 and T2's reds and greens, about 30 min. Window 2, T3's run, A8's eleven mutations and A12's, about 90 min, one test file per run. The estimate is D0's fixture count; nothing here has been run. One at a time, each beside a gate's PYTEST stage only, so never START's createdb, frontend's end, the demo block, the runtime stages or END. Each window's brief carries:
  (a) a `-T` copy with both URLs on it, name unique to the window, createdb with mkdb's retry, template guard 1/3/1 at both ends; (b) the END check reads the window's own named DB gone and the gate's DB still there;
  (c) own redis db from 11, 12 or 13, every command `-n <db>`, dbsize 0 at both ends, db 0 = 56 quoted at both ends; (d) own MinIO bucket names, `GIP_GATE_SLOT=/tmp/slots/window-sl8377` quoted from the process environ, `gip:switch` channels read at START, and any fixture that ignores the slot is a stop;
  (e) no compose up or restart, no shared-service restart, no fixed-port serve; (f) run-heavy, nice 10, the cap's ONE, the memory guard; (g) it opens only with the gate's pytest expected to outlast it by 30 min, by the gate's own progress line, quoted, and it ends before the gate leaves pytest;
  (h) START and END lines name the gate and its stage, and the gate's END read lists the window; (i) the ATTRIBUTION read, both ways; **(j) no window runs `test_deployment_switch*.py`.** The `deployment_request.executed` rows call `deploy_and_switch` with `switch=None`, so `_prepare` returns before any PUBLISH (`deployments.py:505`).
- **Hours, gate not counted, an estimate, recomputed on the rulings:** T1 3 h (+0.5: DP-3's cases go from 2 to 8, plus the two docstrings), T2 1.5 h, T3 8 h (+1: the clauses for DP-9, DP-10, DP-13 and DP-14, which no task carried, and the two OQs in their mirrors), T4 1.75 h (+0.25: A12), **about 14.25 h**, and about 1.5 h audit, **about 15.75 h with the audit**, plus the gate. The ruling's "~14 h" is the earlier 12.5 + 1.5, so this is about 1.75 h above it.
- **Docker, NFR VM:** nothing. Network: nothing.

## Tasks

### SL-2060: the row. Scope: A1 to A14; `00` FR-7, `06` FR-368, FR-349, FR-351, `02` FR-146, FR-157, FR-154, FR-163, `03` FR-238; lane WK-1178; after M, with the chain's additions

Worktree `sl-8377-fr7`, from `origin/main` at its seat, not this tree: every line number above is re-derived. The base is re-read first against
`~/gi-pricing-plan.local/handover/fd1723-d0-enumeration-2026-11-05.md` with the predicate in Evidence.

- [ ] **T1. The misnamed events.** Red first, then green, in a new `backend/tests/test_audit_transitions.py`. The reds: `test_a_failed_certificate_says_so`, both `before`s, both types; `test_a_late_certificate_moves_nothing` under `-k certificate_recorded`, A4's eight. If those eight are green at base, DP-3's limb is withdrawn: drop `moved` and `.certificate_recorded`, and record it in LG-2061.

```python
# platform/objectives.py record_certificate; the same in platform/metrics.py
failed = result.overall is CertificateOutcome.FAILED
# Re-checked here: the route's refusal ran before the Job existed (DP-3).
moved = before in {ObjectiveStatus.DRAFT.value, ObjectiveStatus.CERTIFIED.value}
if moved:
    row.status = (ObjectiveStatus.DRAFT if failed else ObjectiveStatus.CERTIFIED).value
    row.certificate_id = None if failed else certificate.id
await session.flush()

outcome = "certification_failed" if failed else "certified"
await audit.record(
    ...,
    action=f"custom_objective.{outcome if moved else 'certificate_recorded'}",
    ...,
)
```

  `after` keeps its keys, so `overall` and `findings` carry the result, passed or failed, and `after.certificate_id` names the run's certificate. The row's own `certificate_id` stays, and the approver reviews what was submitted. Correct both docstrings: "leaves the objective in `draft`" holds only from `draft` or `certified`.
  Clauses, dated, citing this plan: FR-146 and FR-157 name the three actions and say a pre-merge row reads by `after.overall`; FR-368 says `approval_request.<decision kind>` names a decision. Pin the first-of-two row. Commit.
- [ ] **T2. The two built transitions.** Red first, then, after the status write in `submit_for_review`, in `objectives.py:790`'s form:

```python
await audit.record(
    session,
    workspace_id=workspace_id,
    actor=actor,
    source=JobSource.API,
    action="rating_version.submitted",
    entity_ref=f"rating_version:{ref.slug}@{ref.version}",
    before={"status": RatingVersionStatus.DRAFT.value},
    after={"status": RatingVersionStatus.REVIEW.value, "approval_request_id": str(request.id)},
    justification=change_summary,
)
```

  and in `deployments.py`, directly after `executed` is proved not `None`, `entity_ref=str(_request_ref(request_row))`, `action="deployment_request.executed"`, `before={"status": "approved"}`,
  `after={"status": "executed"}`. `test_deployments.py:567` patches on `deployment.created`, so its rollback still covers this. The row's `deploy_and_switch` call passes `switch=None`. Clauses at FR-238 and `03:1044`. Commit.
- [ ] **T3. The table.** First the spec side: the maps (DP-11, DP-12) and their clauses; the clauses of DP-9, DP-10, DP-13 and DP-14 (b), the last by A12's wording; DP-4's clause at FR-7; the two OQs in their mirrors. Then the rows. Reuse, by import, as `test_nfr498_audit_events.py` does: `_create_authored` and `_create_artifact`
  (`test_api_approvals.py:884`, `:151`), `_events` (`test_model_nfrs.py:89`). Set-up per artifact type, about 11 fixtures, D0 §6. Rows call the service function inside
  `database.unit_of_work()`. **A writer that opens its own transaction cannot take the rollback leg: STOP.** Shape:

```python
@dataclass(frozen=True)
class Row:
    lifecycle: str
    before: str | None          # None: a creation row (DP-4)
    after: str
    action: str
    setup: Setup                # brings a fresh artifact to `before`
    perform: Perform            # (session, Ctx) -> entity_ref; never commits

MAPS = {
    "approval_request": VALID_APPROVAL_TRANSITIONS, "dataset_version": VALID_DATASET_TRANSITIONS,
    "job": VALID_TRANSITIONS, "custom_metric": VALID_METRIC_TRANSITIONS,
    "model": VALID_MODEL_TRANSITIONS, "custom_objective": VALID_OBJECTIVE_TRANSITIONS,
    "peril_structure": VALID_PERIL_STRUCTURE_TRANSITIONS, "rating_version": VALID_RATING_VERSION_TRANSITIONS,
}

#: Declared, no writer: the reason is the ruling that carried it. Never an empty reason.
NOT_BUILT: dict[tuple[str, str, str], str] = {
    ("custom_objective", "draft", "deprecated"): "PL-2059 DP-9",
    # one line per edge: 9, the carries C2 and C3
}

def test_every_declared_edge_has_a_row_or_a_reason() -> None:
    declared = {(n, a.value, b.value) for n, m in MAPS.items() for a, to in m.items() for b in to}
    rowed = {(r.lifecycle, r.before, r.after) for r in ROWS if r.lifecycle in MAPS}
    assert declared - rowed == set(NOT_BUILT)
    assert not set(NOT_BUILT) & rowed
```

```python
@pytest.mark.req("FR-7")
@pytest.mark.req("FR-368")
@pytest.mark.parametrize("leg", ["commit", "rollback"])
@pytest.mark.parametrize("row", ROWS, ids=_row_id)
async def test_a_declared_transition_writes_its_event_in_its_transaction(row, leg, ...) -> None:
    ctx = await row.setup(database, workspace_id, actor)
    if leg == "rollback":
        with pytest.raises(_Rollback):  # noqa: PT012
            async with database.unit_of_work() as session:
                ref = await row.perform(session, ctx)
                raise _Rollback
        assert await _status(database, ctx) == row.before
        assert await _events_on(database, workspace_id, row.action, ctx.entity_ref, since=ctx.sequence) == []
        return
    async with database.unit_of_work() as session:
        ref = await row.perform(session, ctx)
    (event,) = await _events_on(database, workspace_id, row.action, ref, since=ctx.sequence)
    assert (event.before or {}).get("status") == row.before
    assert (event.after or {}).get("status") == row.after
```

  `test_a_not_built_edge_has_no_writer` reads `backend/src/**/*.py` with `pathlib` for `ObjectiveStatus.DEPRECATED`, `MetricStatus.DEPRECATED` and `PerilStructureStatus.ARCHIVED`. A hit fails it, naming the
  file: a writer built later owes its event. Markers on `test_audit.py:62` and `test_deployments.py:542` stay. Commit.
- [ ] **T4. Prove it.** The eleven mutations, A12's and A7's two plants, each red quoted, reverted, `git diff --quiet` rc 0. The census (A9). Closure-derived GREEN (seat brief item 29), in LG-2061. The docs check. Commit.
- [ ] **T5. Close** as `PL-1856` B3, on the lead's gate grant. Each DP's ruling is cited in the LG, by the entry "2026-11-05 16:39:14 GMT".

### Write set

`backend/src/app/platform/objectives.py`, `metrics.py`, `rating_versions.py`, `deployments.py`; `packages/model-schema/src/model_schema/rating.py`, `approvals.py`; new
`backend/tests/test_audit_transitions.py`; `docs/specs/00-overview.md` (`:128`, FR-7, §10), `02-modelling.md` (FR-146, FR-154, FR-157, FR-163, `:1664`), `03-rating-engine.md` (FR-238, `:1044`, §10),
`06-governance.md` (FR-349, FR-351, FR-368); `docs/open-questions.md` (DP-4's OQ and DP-11's); LG-2061; `docs/roadmap.md` (the SL row, and the §10 gate row of DP-11's OQ); this plan (`status:` only); `docs/INDEX.md`. The FD records are their owners'.

**Dated delta, 2026-11-06 (ruling to-lead "2026-11-06 02:27:13 GMT", after A10 stopped `SL-2060` on `model.fitted`):** `backend/src/app/platform/modelling.py` (`record_fit`'s event) and `backend/tests/test_model_nfrs.py` join this Write set; `docs/specs/02-modelling.md` is already in it and gains a dated correction at §9 and a dated amendment on NFR-484. The Evidence table's reference "949" for the `model.fitted` writer is re-read at `ac123679`: `modelling.py:949` is the `row.status = FITTED` assignment inside `record_fit`; the `audit.record` of `model.fitted` is at `:986`. Row `draft>fitted` of the table now asserts `before.status == "draft"`, as every other transition row does. No status guard is added (out of this slice).

### Files shared

Named row by row under **The chain's collisions**. In short: `03:138-139` with R2, an adjacent line; `docs/open-questions.md` with M and SL 8361, by append; every other chain path is read-only here or clear; `docs/INDEX.md` and `docs/roadmap.md` by re-merge.

## Hand-off (not this plan's writes)

- **The maintainer:** the slice GO. The rulings are in. The FR-7 exception reads on the ruling's Freeze sentence, against the 15.75 h above.
- **The lead:** the ids in Needs; the FD routing, carries included; the owner and gate of DP-11's OQ; the gate slot; the two windows' briefs; a seat after M; the §14 draft's list with one of §13's four verdicts each, reading 2 misnamed + 1 decision name by dated line, taking the new observation and DP-3's OQ candidate into it.
- **The auditor:** `FD-1723`'s row FR-7, by dated line, on merge: its 79 is 83 by this predicate at `bdad1322`, and D0's cite corrections.
- **The P2 closure record's carry-forward list:** C1 to C6, owner now. The §14 review proposes the P3 Work.

## Self-review

1. **Spec coverage.** `FD-1723` row FR-7: list from the spec and maps, T3 with A7; one case per transition, A6; same transaction, the rollback leg; a transition with no audit is the red, A5; census, A9. `PL-1856` Acceptance 16: every clause, and its mutation is A8.
   The first brief: the 3 misnamed first (T1, A1); revocation stated as not built (correction 5, DP-14); the OQ (DP-4); `PL-1856` Slice D as parent, unedited; collisions named; gate, windows and P2-or-carried stated.
   The rulings, each of the 15 quoted under its DP: DP-3 (A4, T1), DP-4 (A13, Write set), DP-11 (A13, Write set), DP-14 (b) (A12), the carries (C1 to C6).
2. **Every cite read** at `bdad1322`, and five of D0's corrected. New at this fold, read at the same tree: `rbac.py:190-191`, `test_rbac.py:343`, `deployments.py:505`, `objectives.py:636`, `metrics.py:430`, FR-349, FR-350, OQ-1944. Not opened: D0's U8 reads at `shadow.py:88` and `outbox.py:133`, which neither write a governed status by D0's reading; `rating_versions.py:744` was read and is a read-side mapping.
3. **Placeholder scan.** `Setup`, `Perform` and `_events_on` are the executor's to fill from the named helpers, by design; each row is in the table.
4. **Names.** `certification_failed`, `certificate_recorded`, `test_a_failed_certificate_says_so`, `test_a_late_certificate_moves_nothing`, `NOT_BUILT`, `ROWS`, `MAPS` agree across DPs, Acceptance and Tasks.
5. **Sums.** 45 + 12 = 57 map-derived; 57 + 15 = 72 rows; 72 × 2 = 144 cases. Map edges 57: 45 written + 12 unwritten, of which 9 stay in `NOT_BUILT`, 3 are removed by DP-11 and DP-12. A4: 2 × 2 × 2 = 8. Hours: 3 + 1.5 + 8 + 1.75 = 14.25; + 1.5 = 15.75.
6. **Calendar**, from `date`: Wed 11, Thu 12, Fri 13, Wed 18 Nov.
7. **No range of requirement ids**, and nothing estimated is stated as measured: hours, window lengths and the DP-3 fault are marked.
8. **The plan rules nothing:** fifteen DPs, closed by the maintainer's entry, each quoted. Two readings are the planner's and are marked: "after submission" as any status outside `draft` and `certified`, and the proposed owner and gate of DP-11's OQ.

*(Dated note, 2026-11-07, docs batch 16, by the executor: the row at line 146, `A SL 8325 @e75e0f1a`, names the slice minted as **SL-2075** (PL-2074, LG-2076, #1456). The plan is frozen at its date and line 146 is not edited.)*
