---
id: PL-8376
family: plan
kind: map
title: WK-1178 — FD-1723's FR-7 limb, the misnamed audit events first, then every declared transition emits its event, SL-8377 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8376
owner: planner
tree: 850cf225797c8a63065130dc9012a2ef31b5ef55
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1856, FD-1723, FR-7, FR-368, FR-369, FR-349, FR-351, FR-353, FR-355, FR-146, FR-157, FR-154, FR-163, FR-238, FR-370]
---

# PL-8376 — WK-1178: FD-1723's FR-7 limb. The misnamed events first, then every declared transition (SL 8377, a dated Work-plan delta)

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L1 (a'): it `relates:` `PL-1856` and
> leaves it unedited. It replaces that plan's Slice D, never seated. One slice row, SL 8377. **It decides
> nothing, and no build seat starts until the maintainer accepts it.** The executor's skills are
> `superpowers:test-driven-development`, `.claude/skills/python-test` and `.claude/skills/spec-change`.
> PL 8376, SL 8377 and LG 8378 are working ids, reserved by the lead.

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
route's docstring says must not happen. See DP-3.

**The row table.** The expected `action` is the spec's where a spec names it, else the module's existing string;
`06` §4.5 `:534` keeps no table of names. Under this plan's recommendations. **Bold** = changes in this slice.

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
| FD-1381 TRACK A, SL 8373 | `docs/specs/` §4 sections and fence lines | Two of this plan's lines share a §4 section with TRACK A's blocks: `02:1664` in §4.10 (between fences `:1596` and `:1683`) and `03:1044` in §4.12 (after fence `:1006`). Different lines, no fence touched here. Whichever merges second re-reads. TRACK A has no branch to measure yet, so this is read from PL 8372's block list. |
| D, F, G, LAST-2 + T, P | none | No path in common. |

`docs/INDEX.md` and `docs/roadmap.md` are shared with every slice, by re-merge. No chain branch writes any of the five
platform files this slice edits, `model_schema/rating.py`, `model_schema/approvals.py`, or a new test file. **So
the only predicted conflict is `03:138-139`.**

## Decision points

No DP is the planner's to rule. **DP-1 to DP-4 are blocking**, each changing what the executor builds. Each of the others has a
default the executor can build against, and the plan stays `draft` until all are answered. A row where a
declared edge has no writer says whether its fix is a writer or a spec change.

- **DP-1 (blocking): the failed certificate's name.** (a) `<type>.certification_failed` on every failed run, whether
  `draft → draft` or `certified → draft`; `after.status` and `before.status` tell them apart. (b) Split:
  `.certification_failed` on `draft → draft`, `.draft` on `certified → draft`, the `<type>.<target>` pattern D0 expected.
  (c) No rename: state that `.certified` means "a certification ran", and pin `after`. **Recommendation (a).** The reader's
  question is "did it pass?". (b) gives the same run two names by a state the reader did not ask about. (c) leaves the
  trail misleading. One expression at each site, and spec clauses at FR-146 and FR-157.
- **DP-2 (blocking): `approval_request.approve` on the first of two.** (a) Keep it, because it records the decision
  FR-368 lists, and it is true. Pin `after.status = review` and `approvers_recorded`; a dated clause at FR-368 says
  `approval_request.<decision kind>` names a decision, not a state. (b) A new `approval_request.approval_recorded` when the
  status stays `review`. (c) Rename all three to `.approved`, `.rejected`, `.changes_requested`.
  **Recommendation (a).** It is still dealt with first, in T1. The §14 input then reads two misnamed events and one
  decision name, on correction 2 above. (b) gives one decision two names and breaks no reader, at 0.5 h more. (c)
  would claim a state on the first of two: the fault this plan removes.
- **DP-3 (blocking): the unguarded certificate write, a `CLAUDE.md` §0 question.** (a) In T1: `record_certificate`
  moves the row only from `draft` or `certified`; a run that ends after submission either keeps its certificate, moves
  nothing and writes `<type>.certificate_recorded`, or fails the Job. Red first. About 1 h. Which of those two is a sub-choice for the ruling.
  (b) A new FD, carried, and D1's rows do not cover it. **Recommendation (a), keeping the certificate and moving nothing.**
  It is the site T1 opens anyway, and the fault is the one the route's docstring refuses, but it is a behaviour change in a
  limb ruled "test only", so it needs the word. **This row is unproved by a run**: T1's red is its proof, and a green red
  test withdraws it.
- **DP-4 (blocking, OQ candidate): does FR-7 cover creation?** Per 16:21:19 (2b), for the maintainer, not a seat.
  Draft question: *"Does FR-7's 'state transition' include the event that brings a governed Artifact into existence?"*
  (a) Yes for each type in `00:200` and FR-353's seven, and for the entry into the Approval Request, Deployment Request and Job lifecycles: 15 rows, about 1.5 h. FR-353 already makes the
  creation event the Author's one source, so a missing one fails closed at approval, and an Artifact with no birth event
  has a gap at the start of its history. (b) No: FR-7 is edges only; creation sits under FR-368's "governed state change",
  and FD-1723's census lists it. 57 rows. (c) Every `*.created` and recording site: roughly 20 rows more by D0 §3's table, not counted, covering
  `backtest.recorded`, `profile.created` and others that no spec names and `00:200` does not list.
  **Recommendation (a), with a dated clause at FR-7.** The other creation and recording sites stay listed in the census, unasserted.
- **DP-5: a catalogue of action names (D0's U1).** (a) No table: each module names its strings, as `06:534`'s dated note
  says, and this plan adds its names beside their requirements. (b) A table in `06`, reversing that note: 74 strings of
  which 50 no spec names, about 3 h, and a second copy of what the rows list. **Recommendation (a).**
- **DP-6: Do the two built transitions get events (D0's U2)?** (a) A writer each: `rating_version.submitted`
  (`rating_versions.py:486`) and `deployment_request.executed` (`deployments.py:609`). (b) Rule that
  `approval_request.submitted` discharges FR-7 for R1, which carries the same `entity_ref`; DR3 gets a writer. (c) Rule
  both discharged. **Recommendation (a).** Five of the six other types write both, and a query by the request's
  `entity_ref` never sees its execution, because `deployment.created` is on the Environment. `03:1044` says no later
  slice appends to its catalogue, so the name needs a dated clause there, which the maintainer's acceptance of this DP gives.
- **DP-7: scope of the rows.** (a) FR-7 only: the eleven lifecycles above, Job included because the map is declared and the
  rows are cheap, though a Job is not in `00:200`. FR-368's other classes (D0 §1.15) stay census-only; `deployment.*` keeps
  its own tests, e.g. `test_deployments.py:542`. (b) Add those classes, about 12 rows, 2 h: closes more, but outside the
  limb's scope. **Recommendation (a).**
- **DP-8: the four shared names (COLL: M4, O4, the metric return, P4).** They satisfy FR-7: an event exists. (a) Keep; each
  row asserts `before` and `after`. (b) `<type>.returned`, as `rating_version.returned_to_draft` does, about 1 h and four
  more spec names. **Recommendation (a)**, for the freeze; a carry to P3 under (b)'s name. A reader counting `model.fitted`
  counts returns, and the row's pin makes that visible.
- **DP-9: Custom Objective and Custom Metric `→ deprecated`, 6 edges. Writer or spec?** The state is declared
  (`02:263`, `:254`) and OQ-609 decided what it means; no route is specified, `DEPRECATED` appears nowhere in `backend/src`,
  and the OQ-609 selection refusal does not exist. (a) **Writer:** two routes, §5.1 rows with their Permission cells
  (SL 8361's column, SL 8370's pin), the event, the selection refusal, openapi and the generated client: about 10 h and a
  frontend-touching gate. (b) **Spec:** a dated clause at FR-163 and FR-154 that no P2 path performs it, carried with an
  owner. The edges stay in `NOT_BUILT`, with the guard T3 gives. **Recommendation (b).** Nothing can reach these states, so no event
  is missing, and a P2 close does not depend on it. A later phase names the owner.
- **DP-10: Peril Structure `→ archived`, 3 edges. Writer or spec?** (a) **Writer:** one route on the Model archive's pattern, about 4 h.
  (b) **Spec:** a dated clause at `02:1664`, as DP-9. **Recommendation (b)**, same reasons.
- **DP-11: Rating Version, F2, R4, R5, R6. Writer or spec?** (a) **Spec and map:** a clause at FR-238 that `live` and `retired` are never stored,
  `live` being a Deployment's property, evidenced by `deployment.*`; correct `VALID_RATING_VERSION_TRANSITIONS`: add
  `review → draft`, drop `draft → approved`, fix the comment. Nothing else moves, about 0.5 h. What `retired` means goes to a new OQ.
  (b) Consult the map too, as the six others are, 0.5 h more: a dead check, since `require_in_review` runs first. (c) **Writer:** build
  `retired`, which has no specified trigger. **Recommendation (a):** T3's completeness test is then the map's reader.
- **DP-12: Approval Request `draft → review`, `changes_requested → draft`, 2 edges. Writer or spec?** A request is written in `review`
  (`approvals.py:311`), and a resubmission opens a new request. (a) **Spec and map:** a clause at FR-351, and drop both edges and fix the comment
  at `model_schema/approvals.py:80`. (b) Keep both in `NOT_BUILT`, carried. (c) **Writer:** add a `draft` stage with no caller. **Recommendation (a)**, 0.5 h.
- **DP-13: the spec-only rows.** F1: FR-351 says `peril_structure` has no decision hook, and `perils.py:498` is one, wired at `api/approvals.py:566`,
  tested at `test_api_approvals.py:1051-1053` (FD-1456). Code and test agree, so a dated clause; `dataset_version` has none,
  so that half stands. F3: `00:128` against `01:262`: a dated pointer, or leave and record. F5: FR-369's form is missed by
  `ingestion.py:492` and others in D0 §4(c): carry; each row pins the `entity_ref` it finds. **Recommendation: clause, pointer, carry.**
  Each side is the decision-maker's by `CLAUDE.md` §0, so these go to one ruling rather than the executor.
- **DP-14: what is not built. No code in this slice.** (a) **Role revocation, not built on this surface:** carry to P3 with FR-350, which makes
  membership the identity provider's. The verdict is "not started", not "no writer". (b) **Break-glass expiry:** a dated clause at FR-349 that
  expiry is a read and the grant's event records `expires_at`; or a sweep Job with `break_glass.expired`, about 3 h, for a reader of the
  trail who wants a stated end. (c) **`traces.py:297`:** no caller outside `test_traces.py`, and a trace is not in `00:200`.
  Carry, with one line that the first route to call it owes an event. **Recommendation: all carried, (b) by clause.**
- **DP-15: ordering against the freeze.** (a) One slice, one gate, joining the chain's additions after M. T1 and T2 commit first. If T3 is not
  done by the re-baseline before Wed 11 Nov 12:00, the head at T2 gates alone, and T3 stays the named exception. (b) Two slices now, T1 + T2 then T3:
  two gates, +2.5 h, a second id. **Recommendation (a):** the fallback costs nothing unless it fires, when the lead reserves a second `SL`.

**P2 or carried, as proposed; each verdict is the lead's (`CLAUDE.md` §13) at the §14 draft.**

| 16:21:19 (2a) item | Proposal | DP |
|---|---|---|
| The 3 misnamed | 2 fixed, 1 pinned, P2 | 1, 2 |
| The 2 built with no event | fixed, P2 | 6 |
| The 12 edges | 9 carried (objective, metric, peril); 2 approval, removed; `live → retired`, clause; plus R4, removed | 9 to 12 |
| FR-351 vs `perils.py:557` | clause, P2 | 13 |
| `VALID_RATING_VERSION_TRANSITIONS` | corrected, P2 | 11 |
| `00:128` | pointer, P2 | 13 |
| Role revocation | carried: not built | 14 |
| Break-glass expiry | clause, P2 | 14 |
| `traces.py:297` | carried | 14 |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's merge tree. Items 1 and 2 apply
to this plan; A1 to A11 apply to the slice, under the recommendations. A ruling that differs re-words its item at activation by a dated line.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing line except check 31 / check 32
   lines naming working ids 8376, 8377 or 8378. After the mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no line that stands for a set of ids.

The slice:

- **A1. The misnamed events go first.** `git log --reverse --format=%s origin/main..HEAD --no-merges`: the first code commit is T1.
- **A2. A failed certificate says so.** `backend/tests/test_audit_transitions.py -k certification_failed`: each failed case has action
  `<type>.certification_failed`, the true `before.status` and `after.status`, and `after.overall = failed`. Red at base by its cause; red
  under the mutation that restores the old string.
- **A3. The first of two is pinned.** The row asserts `approval_request.approve`, `after.status = review`, `approvers_recorded = 1`.
- **A4. A late certificate moves nothing (DP-3).** A certificate recorded on a version in `review` leaves it in `review`, red at base. If that
  test is green at base, the row is withdrawn and LG 8378 says so.
- **A5. The two built transitions have events.** `rating_version.submitted` and `deployment_request.executed`: each red at base, with `entity_ref` the
  version's and the request's own ArtifactRef, and a query by that `entity_ref` returns it.
- **A6. Every row, two legs.** One case per row of the table above, × `commit` (exactly one event with the row's `action`, `before.status`, `after.status`) and
  `rollback` (a raise inside the same `unit_of_work` leaves the status at `before` and no event). `pytest --collect-only -q
  backend/tests/test_audit_transitions.py` shows 144 such cases under DP-4 (a), 114 under (b), plus the two tests of A7 and A4's two.
- **A7. Every declared edge is accounted for.** `test_every_declared_edge_has_a_row_or_a_reason` is DB-free and reads the eight maps by
  import. Mutation: add a planted edge to a copy of one map, and it reds naming the edge. `test_a_not_built_edge_has_no_writer` reds on a planted
  `row.status = ObjectiveStatus.DEPRECATED.value` under `backend/src`.
- **A8. A deleted event fails its row.** One mutation per writer module: `objectives`, `metrics`, `approvals`, `rating_versions`, `deployments`, `datasets`,
  `modelling`, `perils`, `validation_rules`, `reference`, `jobs`, deleting one `audit.record(` call. LG 8378 quotes each red, `git diff --quiet -- backend/src`
  rc 0 after each. Eleven mutations.
- **A9. The census is printed, by its predicate.** LG 8378 carries `git grep -n -F 'audit.record(' <head> -- backend packages ':!*/tests/*'`, its
  count, the AST count and each site matching no row, with the reason. The list of rows is the table's, and is never derived from this.
- **A10. A case red with no mutation is a STOP** (`PL-1856` constraint; seat brief item 13), other than A2, A4 and A5's reds at base, which are expected and named.
  Any other: stop, quote it, no assert softened.
- **A11. Spec and code in one commit.** Each new action name and clause lands in the commit of its code. `git diff --name-only origin/main...HEAD -- docs/contracts
  frontend deploy` prints nothing. `uv run python scripts/generate-contracts.py --check` rc 0.

## Global Constraints

- **The list comes from the spec and the maps, never from the sites** (`FD-1723`, 13:55:54). Rows are written from the table above, and a site read is a check.
- **`audit.record` stays in the caller's transaction** (`06` R2, `platform/audit.py:52`). No writer gets its own commit.
- **Requirement ids are permanent** (`CLAUDE.md` §5). Clauses are dated and appended in the row; no new FR id is needed. A new term goes in `00` §2 first.
- **No stored event is rewritten** (FR-370).
- **Nobody hand-writes a shape in `model-schema`** (`CLAUDE.md` §2); no new shape here. `backend/tests/` imports the maps; it never restates them.
- **No id range in any file this slice writes.** Requirements are named one by one.
- **The barred word.** Write "the maintainer (by delegation)". Commit trailer per the common seat brief, item 7.

## Needs

- **Seats:** one decision-maker for DP-13's ruling, unless the maintainer rules it with this plan; one executor; one auditor. Audits take precedence when the cap binds.
- **Ids, not reserved:** one `RL-` for DP-13; one `FD-` the lead routes for the two misnamed events, the two unevented transitions and, if DP-3's
  red holds, the certificate write (`PL-1856`: "STOP to the lead, who routes a new FD"; here the reds are known in advance, so the FD can precede the slice); one
  `OQ-` each for DP-4 and for what `retired` means, each mirrored in `open-questions.md`, its spec's §10 and the `docs/roadmap.md` §10 gate table. PL 8376, SL 8377 and LG 8378 are held.
- **Gate cost: one SOLO full gate, about 2.5 h, no compose build, no timed path changed.** `audit.record` is added to two non-scoring writes, and to no scoring path. `deployment_request.executed` adds one insert to the deploy transaction that NFR-494's 30 s covers. No reading is proposed for it; that is the auditor's to confirm. **No frontend, contract or migration change** under the recommendations; DP-9 (a) or DP-10 (a) would change that.
- **DB windows: two, the lead's to grant.** One for T1 and T2's reds and greens, about 30 min. One for T3's run and A8's eleven mutations, about 90 min, one test file per run. Each
  with its own DB, redis db 11, 12 or 13, and the two quoted zeros at the end. The estimate is D0's fixture count; nothing here has been run.
- **Hours, gate not counted, an estimate:** T1 2.5 h, T2 1.5 h, T3 7 h, T4 1.5 h, about 12.5 h, and about 1.5 h audit. The triage's ~12 h. Under DP-4 (b), about 1.5 h less. Writers, if ruled, on top: DP-9 (a) 10 h, DP-10 (a) 4 h, DP-14's sweep 3 h.
- **Docker, NFR VM:** nothing. Network: nothing.

## Tasks

### SL 8377: the row. Scope: A1 to A11; `00` FR-7, `06` FR-368, FR-349, FR-351, `02` FR-146, FR-157, FR-154, FR-163, `03` FR-238; lane WK-1178; after M, with the chain's additions

Worktree `sl-8377-fr7`, from `origin/main` at its seat, not this tree: every line number above is re-derived. The base is re-read first against
`~/gi-pricing-plan.local/handover/fd1723-d0-enumeration-2026-11-05.md` with the predicate in Evidence.

- [ ] **T1. The misnamed events.** Red first, then green, in a new `backend/tests/test_audit_transitions.py`. Failed certificate, both `before`s, both types:

```python
# platform/objectives.py record_certificate; the same two lines in platform/metrics.py
action="custom_objective.certification_failed" if failed else "custom_objective.certified",
```

  Clauses, dated, citing this plan: FR-146 and FR-157 name both actions and say a pre-merge row reads by `after.overall`; FR-368 says `approval_request.<decision kind>` names a
  decision. Pin the first-of-two row. DP-3's guard, the same in both modules, before the status write:

```python
# Re-checked here: the route's refusal ran before the Job existed (DP-3).
moved = before in {ObjectiveStatus.DRAFT.value, ObjectiveStatus.CERTIFIED.value}
if moved:
    row.status = (ObjectiveStatus.DRAFT if failed else ObjectiveStatus.CERTIFIED).value
    row.certificate_id = None if failed else certificate.id
```

  When not `moved`, the certificate row stays and the event is `<type>.certificate_recorded`, `before == after` on status: a recorded run keeps an event, and the name claims no move. Commit.
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
  `after={"status": "executed"}`. `test_deployments.py:567` patches on `deployment.created`, so its rollback still covers this. Clauses at FR-238 and `03:1044`. Commit.
- [ ] **T3. The table.** Maps first (DP-11, DP-12), their clauses, then the rows. Reuse, by import, as `test_nfr498_audit_events.py` does: `_create_authored` and `_create_artifact`
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
    ("custom_objective", "draft", "deprecated"): "PL 8376 DP-9",
    # one line per edge: 9 under the recommendations
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
  file: a writer built later owes its event. It stands only under DP-9 (b) and DP-10 (b). Markers on `test_audit.py:62` and `test_deployments.py:542` stay. Commit.
- [ ] **T4. Prove it.** The eleven mutations and A7's two plants, each red quoted, reverted, `git diff --quiet` rc 0. The census (A9). Closure-derived GREEN (seat brief item 29), in LG 8378. The docs check. Commit.
- [ ] **T5. Close** as `PL-1856` B3, on the lead's gate grant. Each DP's ruling is cited in the LG.

### Write set

`backend/src/app/platform/objectives.py`, `metrics.py`, `rating_versions.py`, `deployments.py`; `packages/model-schema/src/model_schema/rating.py`, `approvals.py`; new
`backend/tests/test_audit_transitions.py`; `docs/specs/00-overview.md` (`:128`, FR-7), `02-modelling.md` (FR-146, FR-154, FR-157, FR-163, `:1664`), `03-rating-engine.md` (FR-238, `:1044`),
`06-governance.md` (FR-349, FR-351, FR-368); LG 8378; `docs/roadmap.md` (the SL row); this plan (`status:` only); `docs/INDEX.md`. The FD, RL and OQ records are their owners'.

### Files shared

Named row by row under **The chain's collisions**. In short: `03:138-139` with R2, an adjacent line; every other chain path is read-only here or clear; `docs/INDEX.md` and `docs/roadmap.md` by re-merge.

## Hand-off (not this plan's writes)

- **The maintainer:** DP-1 to DP-15, the acceptance, and whether the FR-7 exception stands after it (16:21:19: "until the plan").
- **The lead:** the ids in Needs; the FD routing; the two DB grants and the gate slot; a seat when the chain has room; the §14 draft's list with one of §13's four verdicts each, taking correction 2 and the new observation into it.
- **The auditor:** `FD-1723`'s row FR-7, by dated line, on merge: its 79 is 83 by this predicate at `bdad1322`, and D0's cite corrections.
- **A later Work:** the carries in DP-8 to DP-10 and DP-14, each owner named by the lead at §14.

## Self-review

1. **Spec coverage.** `FD-1723` row FR-7: list from the spec and maps, T3 with A7; one case per transition, A6; same transaction, the rollback leg; a transition with no audit is the red, A5; census, A9. `PL-1856` Acceptance 16: every clause, and its mutation is A8.
   The brief: the 3 misnamed first (T1, A1); revocation stated as not built (correction 5, DP-14); the OQ candidate (DP-4); `PL-1856` Slice D as parent, unedited; collisions named; gate, windows and P2-or-carried stated.
2. **Every cite read** at `bdad1322`, and five of D0's corrected. Not opened: D0's U8 reads at `shadow.py:88` and `outbox.py:133`, which neither write a governed status by D0's reading; `rating_versions.py:744` was read and is a read-side mapping.
3. **Placeholder scan.** `Setup`, `Perform` and `_events_on` are the executor's to fill from the named helpers, by design; each row is in the table.
4. **Names.** `certification_failed`, `certificate_recorded`, `NOT_BUILT`, `ROWS`, `MAPS` agree across DPs, Acceptance and Tasks.
5. **Sums.** 45 + 12 = 57 map-derived; 57 + 15 = 72 rows; 72 × 2 = 144 cases; 57 × 2 = 114. Map edges 57: 45 written + 12 unwritten.
6. **Calendar**, from `date`: Wed 11, Thu 12, Fri 13, Wed 18 Nov.
7. **No range of requirement ids**, and nothing estimated is stated as measured: hours, window lengths and the DP-3 fault are marked.
8. **The plan decides nothing:** fifteen DPs, open.
