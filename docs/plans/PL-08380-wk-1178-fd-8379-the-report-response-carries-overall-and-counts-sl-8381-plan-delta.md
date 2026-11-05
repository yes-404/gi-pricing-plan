---
id: PL-8380
family: plan
kind: map
title: WK-1178 — FD-8379's fix, GET /validation-reports/{id} carries overall and counts through a response-side shape while the stored body stays byte-identical, SL-8381 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8380
owner: planner
tree: 850cf225797c8a63065130dc9012a2ef31b5ef55
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-8379, SL-8381, LG-8382, FR-42, FR-49, FR-451, NFR-469]
---

# PL-8380 — WK-1178: FD 8379's fix. The report response carries `overall` and `counts`; the stored body does not change (SL 8381, a dated Work-plan delta)

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L1 (a'): a new `PL-` that
> edits no earlier plan. It holds one code slice, SL 8381. **It decides nothing, and no build seat
> starts until the maintainer accepts it.** The executor's skills are
> `superpowers:test-driven-development`, `.claude/skills/python-test`,
> `.claude/skills/contract-schema`, `.claude/skills/contract-guard` and `.claude/skills/spec-change`.
> PL 8380, SL 8381, LG 8382 and FD 8379 are working ids, reserved by the lead. PL 8372, SL 8373 and
> RL 8375 are named in prose only: they are still on draft branches, so `relates:` gains them at
> the mint.

## Authority

- **The finding and the constraint.** The maintainer's entry "2026-11-05 16:31:45 GMT" (1) in
  `~/gi-pricing-plan.local/channel/to-lead.md`, read whole: "FD 8379 CONFIRMED, MEDIUM, OWNER
  WK-1178 … FIX BEFORE FREEZE, own slice, own commits and LG, riding SL 8373's gate: no extra gate;
  if the Wed 11 12:00 line can't hold, it is carried with the P2 closure record by name. THE
  CONSTRAINT, not a preference: the stored body IS the artifact (models.py:1234): stored bytes stay
  unchanged and old bodies still read, proved by a round-trip test on a pre-fix body, red first;
  `overall` stays "derived, never assigned": it is never written into the stored body. So a bare
  @computed_field is refused; a response-side shape in `model-schema` (no hand-written shape) or a
  serialisation mode that keeps the stored form; the seat's plan says which. Contract regen in the
  same commit. The marks in §4.6 follow its landing: until then its row is `illustrative`".
- **The row.** RL 8375 on `draft/rl-1381-2026-11-05` @`61712bd5`, row 5 (`01:550`), and its
  "Noticed, not ruled": `validation-report.schema.json:59` still declares `evidence_blob`, and T3
  does not edit it.
- **The chain this rides.** PL 8372 on `draft/pl-1381-2026-11-05` @`f3094233`, accepted at the
  maintainer's entry "2026-11-05 16:11:50 GMT". Its DP-5 (a): SL 8373 queues behind M and gates before
  Wed 11 Nov 12:00 if the margin shows; otherwise it stays the named exception and merges after the
  code freeze as a tooling-only change.
- **The seating.** The lead's brief `brief-plan-fd8379-2026-11-05.md`. Dates of record: code freeze
  Thu 12 Nov 2026, docs freeze Fri 13 Nov 2026; this finding's line is Wed 11 Nov 2026 12:00.
  Weekdays were read with `date -d <d> +%A`.

## Goal

`GET /api/v1/validation-reports/{report_id}` returns the outcome `01` §4.6 states, `overall` and
`counts`, through one shape defined in `model-schema`. `ValidationReport`, the stored artifact, keeps
its fields and its bytes. The merge discharges FD 8379 and takes `01` §4.6 from `illustrative` to
`schema=`.

## The choice: a response-side shape

**`ValidationReportView` in `model-schema`: a sibling of `ValidationReport` on a shared private
fields base, with `overall` and `counts` as real fields, built only from a report, and refused if
they disagree with `results`.** The maintainer's two options plus the two forms of the first were
tried. The spike was a throwaway script against the root `.venv`'s pydantic 2.13.5, on toy classes
carrying `extra="forbid"`, kept outside the repository.

| Form | Measured | Verdict |
|---|---|---|
| Bare `@computed_field` on `ValidationReport` | The dump gains `overall`; re-reading that dump fails `extra_forbidden` | **Refused by the maintainer.** R1's mutation plants it |
| Serialisation mode on `ValidationReport`: computed, dropped by a context flag or an `exclude=` at each writer | Not run: reasoned from the two writers below | **Rejected.** It fails open. A writer that forgets the flag stores `overall`, which is the forbidden act, and the next `model_validate` at `platform/validation.py:154` or `:308` then answers 500. The safety sits at every writer, and the default is the unsafe one |
| Subclass with `@computed_field` | `model_json_schema(mode="validation")` omits the key. `scripts/generate-contracts.py:255-257` generates in that mode, so the published `generated/validation-report.schema.json` stays wrong; and the subclass refuses the §4.6 block under `extra="forbid"`, so `schema=` could never pass | **Rejected.** It serves the wire and fails the contract and the mark |
| Subclass redeclaring `overall` as a field over the parent property | A shadow warning, and then `view.overall` read `pass_with_warnings` while the dump printed `pass`: the parent property wins attribute access | **Rejected.** Two answers from one object |
| **Sibling with real fields on a shared base** | Dump carries both keys; re-reads as a view; **refused as an artifact** (`extra_forbidden` at `overall`); a disagreeing `overall` is refused; artifact dump has neither key; both validation and serialization schemas list them as required | **Chosen** |

`overall` stays "derived, never assigned" in the sense the constraint needs. It is never stored; on
`ValidationReport` it stays the property it is; and on the view it is checked, so it cannot be set to
anything but the derivation. The shape is one definition: the ten fields move to the base, in their
order, so `ValidationReport`'s dump order, and with it the stored bytes, cannot change.

`counts` is `ReportCounts`, a functional `TypedDict` closed by the model's `extra="forbid"`, because
its key `pass` is a Python keyword and the authored contract closes the object at five required
keys. The repo's other answer, an alias (`datasets.py:298`, `refs.py:186`), makes a plain
`model_dump` print `pass_`. The spike printed `additionalProperties: false` and all keys required.

## Evidence at `bdad1322` (tree `850cf225`), read, spike as stated

Every file:line below was read at `bdad132291fdc05fe233d3ddc946e413dcbd2e1f`, origin/main at
2026-11-05 16:34Z.

- **The defect.** `packages/model-schema/src/model_schema/validation.py:539` `ValidationReport`,
  `extra="forbid"` (`:542`), ten fields (`:544-:553`). `counts` (`:555`) and `overall` (`:566`) are
  plain `@property`. `backend/src/app/api/validation.py:146` declares `-> ValidationReport`, so
  FastAPI's response omits both. `docs/contracts/openapi/generated.json`'s `ValidationReport` lists
  ten properties, neither of them; it is referenced by one path, `/api/v1/validation-reports/{report_id}`.
- **The stored body.** `backend/src/app/db/models.py:1234`: "The report **is** the artifact".
  `backend/src/app/platform/validation.py:114`: `body=report.model_dump(mode="json")`. The row holds
  `overall` as an index column (`models.py`, `validation_reports.overall`), written from
  `overall_outcome` (`validation.py:97`, `:104`), and `api/dataset_versions.py:188` returns it. The
  column is not touched.
- **The reads.** `platform/validation.py:154` (`load_report`) and `:308` (`acknowledge`), both
  `ValidationReport.model_validate(row.body)`. `scripts/revalidate-artifacts.py:103` is the third.
- **The read edge.** `load_report_view` (`platform/validation.py:175`) is the merge point, and its
  docstring states why it exists: the stored artifact "must keep" its bytes while the view folds in
  acknowledgements. Its one caller in `backend/src` is `api/validation.py:150`. That is the place the
  view belongs. Its one test caller is `backend/tests/test_validation_reports.py:426`, which reads
  `presented.results` only (`:433`).
- **The sibling that calls this a defect.** `validation.py:187`, `ValidationRuleSet.empty_layers`:
  "A plain `@property` is not serialised". That class is never stored as a body, so its computed
  field carries no constraint. It is not the pattern here.
- **Every other caller, enumerated.** Run from the repository root at `bdad1322`:

| Pattern, verbatim | Hits that are this class | Effect of the fix |
|---|---|---|
| `git grep -n -E '\b[a-z_]*report[a-z_]*\.model_dump(_json)?\(' -- backend packages scripts` | `platform/validation.py:114`; `backend/tests/dry_run_reports.py:70`; `backend/tests/test_data_nfrs.py:99`; `backend/tests/test_validation_reports.py:116` (both sides) | None: all dump `ValidationReport`, which is unchanged. The other two hits, `platform/blobs.py:645` and `platform/deployments.py:881`, are other report classes (the GC audit `after`, the switch audit `after`) |
| `git grep -n -E 'ValidationReport\.model_validate\|\bload_report(_view)?\(' -- backend/src packages/*/src scripts` | `api/validation.py:150`; `platform/validation.py:154`, `:190`, `:308`; `scripts/revalidate-artifacts.py:103` | `api/validation.py:150` and the return of `load_report_view` change. The rest read `ValidationReport` and do not |
| `git grep -n -E '/validation-reports/' -- frontend/src/api scripts backend/src` | `frontend/src/api/validation.ts:23`, `:39`; `api/validation.py:140`, `:156`, and doc lines | `validation.ts:4` needs its alias re-pointed (next bullet) |
| `git grep -n -E 'report(\.value)?\??\.(overall\|counts)' -- frontend/src` | none | No frontend reads either key on a report, as the maintainer read. **This slice adds no reader** |

- **The frontend seam.** `frontend/src/api/validation.ts:4`:
  `export type ValidationReport = components["schemas"]["ValidationReport"];`. The route's component
  becomes `ValidationReportView`, and `ValidationReport` leaves `generated.json`, so this one line
  moves or `pnpm --dir frontend type-check` goes red. `frontend/src/api/__tests__/validation.test.ts:30`
  casts with `as`, so a fixture without the two new keys still type-checks; the gate's frontend half
  is what proves it.
- **The contract.** `scripts/generate-contracts.py:131` maps the slug to `ValidationReport`. The
  authored `docs/contracts/schemas/validation-report.schema.json:7-8` requires `overall` and `counts`,
  declared at `:21-22`. Read against the generated side at this tree: authored-only `counts`,
  `overall`; generated-only `empty_layers`. Nothing reds on it, because
  `test_an_artifact_shape_carries_exactly_what_its_contract_declares`
  (`backend/tests/test_contracts.py:738`) does not list the slug. **That missing row is how the
  defect stayed green**, while `validation-report` sits in `COMPARED_SLUGS` (`:58`), whose comparisons
  run on the intersection of paths.
- **A second stale statement in the authored file.** `validation-report.schema.json:76` still says
  `pass_with_warnings` requires "every warn result has an acknowledgement", which `01` §4.6 struck on
  2026-08-14 and `validation.py`'s `overall` docstring records as the deadlock it caused.
- **`01` §4.6's block.** `docs/specs/01-data-management.md:550`. Line 559 prints
  `"counts": {"pass": 41, "warn": 3, "fail": 0, "error": 0, "skipped": 1}` beside one result. RL 8375
  row 5 keeps the key, and the view refuses a count that disagrees with `results`, so `schema=` needs
  the counts of the block's own results (R3). T3 changes the other limbs: `id`, literal uuids,
  `evidence_blob` out, `"overall": "pass_with_warnings"`.
- **The tests' lanes.** `backend/tests/test_contracts.py` opens no database: `grep -n -E
  'database|api_client|TestClient|create_app'` on it prints nothing at this tree.
  `backend/tests/test_validation_reports.py` and `backend/tests/test_api_acknowledge.py` need the DB
  fixtures.
- **CI.** The diff reaches `packages/**`, `backend/**`, `scripts/**`, `frontend/**` and `docs/**`, so
  `python.yml`, `frontend.yml`, `docs.yml` and `history-policy` all fire.

## Decision points

For the decision-maker; the GO request carries them to the maintainer. Each is ruled before the
slice starts. The response-side choice above is the plan's, as the maintainer asked; these are what
it leaves open.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-1 (blocking) | How does SL 8381 order against SL 8373, and how does it ride one gate? | (a) **Stacked.** SL 8381's branch starts at SL 8373's S4 head, its work runs before S5, and S5's one SOLO gate runs at SL 8381's head, a superset of SL 8373's. Two PRs: SL 8373's first from its own tip, SL 8381's second. (b) SL 8381 first, from `main`, with TRACK A merged: it then needs a gate of its own. (c) Parallel branches and a gate on a throwaway merge of the two: one gate, on a tree neither PR holds | **(a).** It is the only order with no extra gate on a tree that a PR actually carries. It also leaves SL 8373 whole if the line fails: SL 8373's tip never contains this slice, so PL 8372's G1 ("Nothing under `backend/src/`…") stays true of its diff and its tooling-only exception survives. **Costs, stated.** PL 8372's A14 reads "on the re-merged head", and here that head is SL 8381's: this asks the maintainer to accept that reading. If SL 8381 reds the gate, SL 8373 either waits for the fix or takes its own gate, which is one extra gate on the failure path only. After SL 8373's squash, SL 8381 re-merges `origin/main` and the merged tree is compared with the gated head (A13) |
| DP-2 | The published name. The route's OpenAPI component changes with the class | (a) **`ValidationReportView`**, naming `load_report_view`; `ValidationReport` stays the artifact, and `validation.ts:4` moves. (b) The wire keeps `ValidationReport` and the artifact is renamed: 30-plus sites across `pricing-core`, `backend` and tests, in files the chain is in. (c) `ValidationReportResponse`, as `UploadUrlResponse` (`uploads.py:32`), which avoids reading like `ValidationReportView.vue` | **(a).** `DemoView` (`demo.py:27`) and `load_report_view` are the same word for the same idea. (c) is sound, and only the name differs |
| DP-3 (blocking) | "Red first" on the pre-fix-body test. At the base, nothing is broken: reading and re-dumping a pre-fix body passes, and it must, because the test states what must never change | (a) **Green at the base by design; its red is the refused fix, planted.** R1 applies the bare `@computed_field` as an uncommitted mutation, records the red by cause, reverts, and the LG holds both runs. (b) Force a red at the base by importing `ValidationReportView`: an `ImportError`, which is a red by nothing | **(a).** A test of an invariant cannot be red before the change that threatens it, and A2's rule refuses an import red. (a) also proves the exact thing the maintainer refused is what the test catches. **The maintainer's words were "red first", so this reading needs the ruling and is not assumed** |
| DP-4 | The DB limbs, R1's T4 and T5, need a database | (a) **One short granted DB window** on a `createdb -T` copy, about 15 min, for their red and green before the gate. (b) No window: they first run in the gate | **(a).** Under (b) a defect in them surfaces inside the 2.5 h gate that also carries SL 8373. (b) stays the fallback if no window is free before the line: the DB-free tests still prove the constraint |
| DP-5 | The authored contract's other limbs. Adding the slug to the guard (T1) needs `empty_layers` declared there | (a) **Declare `empty_layers` and correct `:76`** to §4.6's amended rule, each with a dated `$comment`. `evidence_blob` at `:59` stays: nested, outside the guard, and RL 8375 leaves it. (b) Leave the guard row out, and change nothing authored | **(a).** The guard row is what would have caught FD 8379, and T1's red depends on it. `:76` is the same file stating the same field wrongly, and a reader of the new contract meets it first |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's
merge tree. Items 1 and 2 apply to this plan. A1 to A15 apply to the slice.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py` prints no
   failing line except those for the working ids this file uses, and `python3 scripts/doc-index.py
   --check` agrees. After the mint both exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints
   no line that stands for a set of ids.

The slice, SL 8381:

- **A1. The write set.** `git diff --name-only <SL 8373 tip>...HEAD` lists only this plan's Write set.
- **A2. Red first, by its cause.** The LG holds R1's runs. T1 fails with `the contract declares fields
  the model lacks: ['counts', 'overall']`; T2 with an `AssertionError` naming `overall` missing from
  the route's `required`; T4 with `KeyError: 'overall'` on the response body. A fixture, import or
  `NameError` is not the red. A matching status with a differing reason is a plan defect: STOP.
- **A3. The constraint's proof ran red** (on DP-3's ruling). T3 and T5 are green at the base, and the
  LG says so. Under mutation M1, the bare `@computed_field` on `overall` and `counts`, each goes red
  with both keys named, and M1 is reverted with `git diff --stat` empty for
  `packages/model-schema/src/model_schema/validation.py`. Printed failing, per `CLAUDE.md` §13.
- **A4. The fixture is pre-fix, by the record.** `git log --diff-filter=A --format=%h --
  packages/model-schema/tests/fixtures/validation-report-pre-fix.json` names a commit that is an
  ancestor of the first commit touching `packages/model-schema/src/model_schema/validation.py`, and
  the LG quotes the capture command and the base sha.
- **A5. Stored bytes unchanged.** T3 passes at the head:
  `json.dumps(ValidationReport.model_validate(body).model_dump(mode="json"))` equals the fixture's
  stored text exactly, key order included.
- **A6. Old bodies still read, and the view cannot pose as a body.** At the head, the fixture and its
  minimal form read through `ValidationReport.model_validate`, and a dumped `ValidationReportView`
  is refused by it with `extra_forbidden` (T6).
- **A7. Never written.** T5 passes at the head: after `store_report` and `load_report_view`, the
  row's `body` has neither `overall` nor `counts`. `git diff <SL 8373 tip>...HEAD --
  backend/src/app/db/models.py backend/migrations` is empty, and `platform/validation.py:114` is
  unchanged.
- **A8. The response is right.** T4 passes: the route returns `overall` and `counts` agreeing with
  `results`, and **acknowledging a warning changes neither** (`01` §4.6: `overall` is a function of
  the results alone).
- **A9. Derived, never assigned.** T6 passes: a view whose `overall` or `counts` disagrees with
  `results` is refused at construction; `ValidationReportView.of(report)` agrees with the report's
  properties for each of the four verdicts.
- **A10. One shape.** `git grep -n -E 'class ValidationReportView|class ReportCounts'` prints only
  `packages/model-schema/src/model_schema/validation.py`, and `ValidationReportView` is in
  `model_schema.__all__`. `frontend/src/api/validation.ts` takes it from the generated schema.
- **A11. The contract.** The regeneration is in the same commit as the class change (on the branch, before the squash, `git log --format=%h -- docs/contracts/openapi/generated.json` lists
  `validation.py`'s R2 commit).
  `uv run python scripts/generate-contracts.py --check` exits 0. By full path:
  `docs/contracts/openapi/generated.json` has `components.schemas.ValidationReportView` with `overall`
  and `counts` required, and no `components.schemas.ValidationReport`;
  `docs/contracts/schemas/generated/validation-report.schema.json` holds both;
  `docs/contracts/schemas/validation-report.schema.json:7-8` is unchanged and now true.
- **A12. The mark and the counts.** `python3 scripts/audit-docs.py` prints check 40's note with
  **33 schema, 30 illustrative, 0 unmarked**, of 63 blocks: the maintainer's end state of 32 + 31
  with this one block moved. `ILLUSTRATIVE_CEILING` in `tests/test_spec_examples.py` is 30.
  `uv run pytest tests/test_spec_examples.py` passes with the `01` block's id present. Under the
  mutation "the block's `counts.warn` becomes 2", that id fails; reverted.
- **A13. One gate, on the tree that lands.** No gate of this slice's own. S5's SOLO gate on SL 8381's
  head holds every rc, and T1 to T6 are in its passed set by name. After SL 8373's squash and this
  slice's re-merge, `git diff <gated head> HEAD` is empty, or lists only files SL 8373's squash and
  the re-merge account for, read by the auditor. Anything else follows the common seat brief, items
  5 and 21.
- **A14. FD closing act, in the FD-1842 form.** In the slice's own PR, by the slice's auditor at the
  mint: FD 8379's essay is written and minted, with its `status: closed`, its dated `***Resolved
  YYYY-MM-DD***` line naming the slice, LG and plan and the delivered remedy, and its row in
  `docs/findings/register.md`. **The essay is not this plan's and no seat before the auditor writes
  it.**
- **A15. The LG's Audit section.** LG 8382 has its five sections, and its Audit section holds the
  auditor's verdict on A1 to A14 with `origin/main...` ranges named, never a tip alone (`CLAUDE.md`
  §13). The red and green lines are in the LG before the audit.

## Global Constraints

- **G1. The stored body does not change** (`to-lead.md` "2026-11-05 16:31:45 GMT" (1)). `ValidationReport`
  gains no field and no key; `platform/validation.py:114` is not edited; no migration.
- **G2. `overall` is never written into a stored body**, and no `ValidationReportView` reaches a
  `body=` or an audit `after=`.
- **G3. No hand-written shape** (`CLAUDE.md` §2). The frontend type is generated.
- **G4. No frontend behaviour.** One type-alias line; no view reads the new keys. A screen that
  shows them is a later choice.
- **G5. A failing test is never weakened** (common seat brief, item 13).
- **G6. Requirement and section ids are permanent** (`CLAUDE.md` §5). §4.6 keeps its number and heading.
- **G7. No range of ids in any file this plan writes.**
- **G8. Line numbers are re-derived at each base.** This plan's are `bdad1322`'s. SL 8373's base
  holds TRACK A's text, so `01`'s line numbers will differ.
- **G9. Money is untouched.** `counts` are integers of rule outcomes.
- **G10. Redis names its db.** Every Redis use names `-n <db>`, and a seat's db is 11, 12 or 13
  (common seat brief, item 33). **db 0 is LIVE**: an unset `GIP_REDIS_URL` defaults to it, so the
  URL is always set. No bare `FLUSHDB`.
- **G11. A DB window runs on a `createdb -T` copy, never the template** and never a URL naming the
  template. A DB window is single-tenant.

## Needs

- **Seats:** one executor, model per the role file; one auditor. No decision-maker unless the
  maintainer routes the DPs to one.
- **Ids:** PL 8380, SL 8381, LG 8382, FD 8379 are held. No others.
- **DB:** under DP-4 (a), one granted window of about 15 min, on a `createdb -T` copy, for T4 and T5:
  two test files. Under (b), none.
- **Redis:** the window's run sets `GIP_REDIS_URL=redis://localhost:6379/<11|12|13>`. Cleanup is
  `redis-cli -n <db> FLUSHDB`, then `redis-cli -n <db> dbsize` = 0, and `-n 0 dbsize` is read before
  and after as a guard: it must not fall. Nothing else uses Redis.
- **Docker, compose, NFR VM:** nothing else.
- **Gate:** none of its own. It rides SL 8373's S5 (about 2.5 h, PL 8372 Needs), on DP-1 (a).
- **Size:** **about 5 h of executor time**, gate not counted: R1 1 h, R2 1.5 h, the window 0.5 h, R3
  0.5 h, the frontend line and the green set 0.5 h, LG and re-merge 1 h. **Auditor about 1.5 h**,
  with FD 8379's essay and closing act.
- **Earliest start:** SL 8373's S4 head exists, so TRACK A has merged. **The line:** if S5 cannot
  finish before Wed 11 Nov 2026 12:00 with this slice on it, the slice does not ride, and FD 8379 is
  carried with the P2 closure record by name.

## Tasks

### SL 8381: the report response carries `overall` and `counts`. Its row: scope A1 to A15; lane WK-1178; after SL 8373's S4, before its S5

**Files:** see Write set. **Base:** SL 8373's S4 head, on DP-1 (a). Branch `sl-8381-report-response`.
Every literal below was read at `bdad1322`. Where a test sample differs from the neighbouring test,
mirror the neighbour.

**R1: the failing tests, committed before any source change.**

- [ ] **Step 1: capture the pre-fix body at the base.** Build a `ValidationReport` with fixed ids and
  timestamps: one `pass`, one `warn` with `measured`, `threshold`, `offending_sample`, one `fail`, one
  `skipped`, a `reference_dataset_version_id` and an `empty_layers` entry. Write
  `json.dumps(report.model_dump(mode="json"))` to
  `packages/model-schema/tests/fixtures/validation-report-pre-fix.json`, un-sorted and with no
  re-indent. Quote the command and the base sha in the LG (A4).
- [ ] **Step 2: write the tests.**

| Test | File | At the base | Red, by cause |
|---|---|---|---|
| T1 | `backend/tests/test_contracts.py`: add `"validation-report"` to the parametrize list of `test_an_artifact_shape_carries_exactly_what_its_contract_declares` (`:722-:736`) | red, DB-free | `the contract declares fields the model lacks: ['counts', 'overall']` |
| T2 | same file, new `test_the_report_route_publishes_its_outcome`: from `OPENAPI`, resolve `paths["/api/v1/validation-reports/{report_id}"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]`, assert `{"overall", "counts"}` is a subset of its `required` | red, DB-free | `AssertionError`: `overall` and `counts` absent from `required` |
| T3 | new `packages/model-schema/tests/test_validation_report_stored_form.py`: `body = fixture text`; `json.dumps(ValidationReport.model_validate(json.loads(body)).model_dump(mode="json")) == body`; `"overall" not in` and `"counts" not in` the dump; a second, minimal body holding only the six required fields reads | **green, by design** (DP-3) | Under M1 below: the strings differ by the two keys |
| T4 | `backend/tests/test_api_acknowledge.py:102`, extend `test_an_actuary_acknowledges_a_warning_through_the_route`: read the view **before** and after the POST, assert `view["overall"] == "pass_with_warnings"`, `view["counts"]["warn"] == 1`, and the two reads agree | red, DB | `KeyError: 'overall'` |
| T5 | `backend/tests/test_validation_reports.py`, new test beside `test_a_stored_report_reads_back_byte_identical` (`:98`): store, call `load_report_view`, fetch the `ValidationReportRow`, assert `row.body == report.model_dump(mode="json")` and neither key in it | **green, by design** | Under M1: the stored body holds both keys, so `load_report_view` raises `extra_forbidden` at `model_validate`, or, if it is called after the assert, the "neither key" assert fails. Either line names `overall` or `counts` |

  Mark them `@pytest.mark.req("FR-42")`; T3 and T5 also `req("NFR-469")`.

- [ ] **Step 3: run them.** T1 and T2 through
  `run-small.sh <wt> backend/tests/test_contracts.py`; T3 through
  `run-small.sh <wt> packages/model-schema/tests/test_validation_report_stored_form.py`; T4 and T5 in the
  DB window (DP-4). Each failure line goes in the LG verbatim, with the head sha.
- [ ] **Step 4: mutation M1, uncommitted.** On `ValidationReport`, put `@computed_field` on `counts`
  and `overall`. Run T3, and T5 in the window. Record the reds. Revert; quote the empty `git diff
  --stat`. A mutation whose edit does not apply aborts the run.
- [ ] **Step 5: commit** the fixture and the tests, alone: `test(data): the report response and the
  stored form (SL 8381 R1)`. T1, T2 and T4 are red at this commit, so it is not pushed as a PR head.

**R2: green, one commit, regeneration included.**

- [ ] **Step 6: the view's own tests, T6,** in `test_validation_report_stored_form.py`:
  `ValidationReportView.of(report)` for each of `pass`, `pass_with_warnings`, `fail`, `error` agrees
  with `report.overall` and `report.counts`; constructing one with `overall` or `counts` disagreeing
  raises `ValidationError`; `ValidationReport.model_validate(view.model_dump(mode="json"))` raises with
  type `extra_forbidden` at `overall`; `ValidationReportView.model_validate(view.model_dump(mode="json"))`
  round-trips; the view's fields minus `{"overall", "counts"}` equal `ValidationReport.model_fields`,
  in order.
- [ ] **Step 7: `model-schema`.** In `validation.py`:

```python
# Functional because `pass` is a keyword, and the authored contract closes this object at five keys.
ReportCounts = TypedDict(
    "ReportCounts",
    {
        "pass": Annotated[int, Field(ge=0)],
        "warn": Annotated[int, Field(ge=0)],
        "fail": Annotated[int, Field(ge=0)],
        "error": Annotated[int, Field(ge=0)],
        "skipped": Annotated[int, Field(ge=0)],
    },
)


def _counts_of(results: tuple[RuleResult, ...]) -> dict[str, int]:
    ...  # the body of today's `counts`


def _overall_of(results: tuple[RuleResult, ...]) -> OverallOutcome:
    ...  # the body of today's `overall`; the docstring stays on the property


class _ReportFields(BaseModel):
    """The ten fields of `01` §4.6's report, in their stored order. Moving one reorders a body."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    ...  # the ten fields of `ValidationReport`, moved unchanged


class ValidationReport(_ReportFields):
    ...  # docstring and every property kept; `counts` and `overall` delegate to the two helpers


class ValidationReportView(_ReportFields):
    """A report **as presented** (`01` §4.6): the artifact, plus the outcome derived from it.

    Never stored. The stored body is `ValidationReport`, and it stays free of both keys because
    it is the artifact (`ValidationReportRow`); `extra="forbid"` there refuses this shape, so a
    view cannot be read back as a report. `overall` and `counts` are fields so the published
    contract and the `01` §4.6 example hold them, and checked so neither is ever assigned.
    """

    overall: OverallOutcome
    counts: ReportCounts

    @model_validator(mode="after")
    def _derived_never_assigned(self) -> Self:
        if self.overall is not _overall_of(self.results) or self.counts != _counts_of(self.results):
            raise ValueError("overall and counts are derived from results, never assigned (01 §4.6)")
        return self

    @classmethod
    def of(cls, report: ValidationReport) -> Self:
        return cls.model_validate(
            {**report.model_dump(mode="json"), "overall": report.overall, "counts": report.counts}
        )
```

  `model_dump(mode="json")` in `of` is deliberate: it is the form `load_report` already proves
  `model_validate` reads. Add `TypedDict` and `Self` to the imports. Add `ReportCounts` and
  `ValidationReportView` to `__all__` here and in `model_schema/__init__.py`, sorted. `ValidationReport`'s
  dump is unchanged by construction; T3 is what says so.
- [ ] **Step 8: the read edge.** `backend/src/app/platform/validation.py`: `load_report_view` returns
  `ValidationReportView`; both return paths end in `ValidationReportView.of(...)`; add one docstring
  sentence naming §4.6's outcome. `load_report` is untouched. `backend/src/app/api/validation.py:146`:
  `-> ValidationReportView`, and the import at `:56`.
- [ ] **Step 9: the contract.** `scripts/generate-contracts.py:131`:
  `"validation-report": "ValidationReportView"`, with a dated comment naming FD 8379. In the authored
  `docs/contracts/schemas/validation-report.schema.json`, on DP-5 (a): declare `empty_layers`, correct
  the invariant at `:76` to "… and at least one result is `warn`; acknowledgement is checked at
  promotion (FR-46), not here", and add a dated `$comment` saying the document describes the response
  and the stored body is the same object without `overall` and `counts`. `:7-8` do not change. Then
  `uv run python scripts/generate-contracts.py` and commit what it writes, by hand-editing nothing
  under `generated/`. If `test_contracts.py` reds on a path other than T1's, that is a guard speaking:
  read which half it means (`.claude/skills/contract-guard`), and STOP if the fix would touch a
  comparator.
- [ ] **Step 10: the frontend alias.** `frontend/src/api/validation.ts:4`:
  `export type ValidationReport = components["schemas"]["ValidationReportView"];`. The local name
  stays, so no importer changes.
- [ ] **Step 11: green.** `pnpm --dir frontend generate:api` and `pnpm --dir frontend type-check`
  under the load bound, rc quoted. `run-small.sh` on T1, T2, T3, T6's files, then T4 and T5 in the
  window. `uv run ruff check .`, `ruff format --check` on the changed files, `uv run mypy`, each rc
  quoted (item 16). Derive the green set by import closure and quote it (item 29): `validation.py`
  is imported widely, so the closure is run file-by-file where it is DB-free, and the gate is the
  decisive green for the rest.
- [ ] **Step 12: commit** source, tests, regeneration and alias as one:
  `fix(data): the report response carries overall and counts; the stored body is unchanged (FD 8379)`.

**R3: the mark, on landing. Its own commit, after R2.**

- [ ] **Step 13: `01` §4.6.** Change the fence from ` ```json illustrative` to
  ` ```json schema=ValidationReportView`. Set the block's `counts` to its own results, one `warn`:
  `{"pass": 0, "warn": 1, "fail": 0, "error": 0, "skipped": 0}`. Add a dated line under the block
  naming FD 8379: the block is the response, `ValidationReportView`; the stored body is
  `ValidationReport`, the same object without `overall` and `counts`; the example's counts now agree
  with its one result. Follow `.claude/skills/spec-change`.
- [ ] **Step 14: the ceiling.** `tests/test_spec_examples.py`: `ILLUSTRATIVE_CEILING` falls by one, to
  30 (A12), in the same commit. Run `python3 scripts/audit-docs.py`, and `run-small.sh` on the file;
  apply A12's mutation; revert.
- [ ] **Step 15: commit:** `docs(specs): 01 §4.6 validates as ValidationReportView (FD 8379)`.

**G: the gate.**

- [ ] **Step 16: hand-off to S5.** SL 8381's head goes to SL 8373's S5: the re-merge, then the one SOLO
  gate, both halves (`CLAUDE.md` §11). T1 to T6 must be in its passed set by name (A13). The docs
  checks fail only on working ids until the mint (item 31).
- [ ] **Step 17: the landing.** SL 8373's PR merges first, from its own tip. SL 8381 re-merges
  `origin/main`, A13's diff is read, the auditor files the LG's Audit section and FD 8379's essay and
  closing act (A14, A15), the mint runs, and SL 8381's PR opens. `frontend.yml` fires on this PR.

**The ordering if the two come apart.**

| Case | What happens to the mark | What happens to FD 8379 |
|---|---|---|
| SL 8373's S5 runs with this slice, before the line | `illustrative` at S4, flipped by R3 before the gate; on `main` it arrives `schema=` one PR after SL 8373 | Closed in SL 8381's PR |
| This slice is not ready at S5, and the line can still hold | SL 8373 lands with the block `illustrative`, ceiling 31. SL 8381 needs a gate of its own, which the ruling does not grant: **it goes back to the maintainer** | Open until then |
| The line fails | The block stays `illustrative`, naming FD 8379, and the ceiling stays 31 | Carried with the P2 closure record by name |

### Write set

- `packages/model-schema/src/model_schema/validation.py`, `packages/model-schema/src/model_schema/__init__.py`.
- New `packages/model-schema/tests/test_validation_report_stored_form.py` and
  `packages/model-schema/tests/fixtures/validation-report-pre-fix.json`.
- `backend/src/app/platform/validation.py` (`load_report_view` only), `backend/src/app/api/validation.py`.
- `backend/tests/test_contracts.py`, `backend/tests/test_api_acknowledge.py`,
  `backend/tests/test_validation_reports.py`.
- `scripts/generate-contracts.py` (one row).
- `docs/contracts/schemas/validation-report.schema.json`; regenerated
  `docs/contracts/schemas/generated/validation-report.schema.json` and
  `docs/contracts/openapi/generated.json`.
- `frontend/src/api/validation.ts` (one line).
- `docs/specs/01-data-management.md` (§4.6 only), `tests/test_spec_examples.py` (one constant).
- LG 8382 under `docs/ledgers/`; at the mint the SL row under `### WK-1178` in `docs/roadmap.md`,
  `docs/INDEX.md`, this plan's `status:`, and FD 8379's essay and `docs/findings/register.md` (A14).

### Files shared

Measured per worktree: `git diff --stat $(git merge-base HEAD origin/main) HEAD -- <the paths above>`,
at the heads named, 2026-11-05 about 16:39Z. Hunks read with `-U0`.

| Slice | Paths shared | Reading |
|---|---|---|
| SL 8373 | `01` §4.6's fence, `tests/test_spec_examples.py` | **The base, not a clash.** S4 writes the mark and the constant; R3 changes them after it |
| TRACK A, T3 | `01` §4.6's block | Merged before S4. R3's `counts` edit is on T3's text, and a block T3 did not leave as RL 8375 row 5 says is a STOP |
| LAST-2 SL 8343 @`5748acc7`, SL 8370 @`953ac45b` | `backend/tests/test_contracts.py` | `:27` and `:264`. T1 and T2 are at `:722-:736` and a new function. No hunk in common. Both are in SL 8373's chain, so the base holds them or the re-merge does |
| SL 8361 @`7f4ce407`, SL 8370, A SL 8325 @`e75e0f1a` | `01` | Hunks at `:852-:892` and `:856`, §5.1. §4.6 is at `:548-:600`. No hunk in common |
| C SL 8328 @`ccba2207`, SL 8340 @`bb4cf209` | `docs/contracts/openapi/generated.json` | One line each. A conflict is resolved by regenerating, never by hand |
| R2 SL 8345 @`369c43c7`, M SL 8359 @`38459124`, R1 SL 8322, H, F, P, G, D | none | Zero of the listed paths in each diff |
| `docs/INDEX.md`, `docs/roadmap.md` | every slice | By re-merge |

**Not measured:** other seats' unpushed work after these heads. A1 and A13 re-read at the base.

## Hand-off (not this plan's writes)

- **The maintainer:** DP-1 to DP-5, the acceptance, and the GO on the row. DP-1 (a) and DP-3 (a) each
  ask for a reading of words already written: PL 8372's A14 "the re-merged head", and "red first".
- **The lead:** the DB window on DP-4 (a); the ids; adding `sl-8381-report-response` to S5's brief so
  the gate's Object line names SL 8381's head; the SL row and LG id at the mint; a P2 closure carry
  line if the line fails.
- **SL 8373's seat:** S4's marks as PL 8372 has them. The block is `illustrative`, ceiling 31.
- **The executor:** LG 8382.
- **The slice's auditor:** FD 8379's essay, its closing act and register row, at the mint (A14), and
  the LG's Audit section (A15). `relates:` here gains PL 8372's, SL 8373's and RL 8375's minted ids.
- **Not done here, on purpose:** `_counts` at `platform/validation.py:54` restates `report.counts`, a
  small duplicate this slice leaves; no screen reads the new keys (G4); `evidence_blob` at
  `validation-report.schema.json:59` stays, as RL 8375 notes.

## Self-review

1. **The constraint, at every site.** Grepped across this file: narrative (The choice), Files (Write
   set, `models.py` and `:114` absent), Steps (R1 T3 and T5, M1, Steps 7 and 8), Acceptance (A3, A5,
   A6, A7) and Global Constraints (G1, G2). A bare `@computed_field` is only ever M1, a reverted mutation.
2. **Every cite was read** at `bdad1322`, and the entries in `to-lead.md`. RL 8375 and PL 8372 were read
   at the two draft shas named. Their mints may move their line numbers.
3. **The spike's limits are stated.** Toy classes, not the real module; `TypedDict` and the sibling
   shape were run, the serialisation-mode row was reasoned. The generated `ValidationReportView`
   against `test_contracts.py`'s scalar and constraint comparisons has **not** been run. `overall` and
   `counts.*` enter their intersection for the first time, and Step 9 says what to do if one reds.
4. **Every requirement is named by id:** FR-42, FR-49, FR-451, NFR-469, FR-46; no range. No requirement
   states the wire form of the report today; `01` §4.6 does, and the slice leaves it as the statement.
5. **No placeholders** except the `...` in Step 7's sample, each saying which existing body moves.
6. **The reds are by cause.** T1, T2 and T4 by the missing keys. T3 and T5 are stated as green at the
   base, and DP-3 carries that openly rather than presenting them as red.
7. **The calendar is stated once:** the line Wed 11 Nov 2026 12:00, freeze Thu 12, docs Fri 13.
