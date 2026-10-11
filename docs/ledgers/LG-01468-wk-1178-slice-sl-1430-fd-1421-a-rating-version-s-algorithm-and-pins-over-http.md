---
id: LG-1468
family: ledger
title: WK-1178 slice SL-1430 — FD-1421, a Rating Version's algorithm and pins over HTTP (PL-1429), task ledger
status: closed
created: 2026-10-06            # original date 2026-10-05, set at the draft; minted 2026-10-06
owner: executor
tree: 52c153cd1dcf7eb8a716559216a30b245dd6a7e2
phase: P2
work: WK-1178
slice: SL-1430
plans: [PL-1429]
corrected_by: []
relates: [RL-1428, RL-1263, FD-1421, FD-1425, FR-237, FR-223, WK-1178]
---

# WK-1178 slice SL-1430 — FD-1421, a Rating Version's algorithm and pins over HTTP

Executed from `PL-1429` by `executor-sl1430` (Sonnet 5.5). Branch
`sl-1430-fd-1421-rating-version-algorithm-and-pins`, worktree `.claude/worktrees/sl-1430`, from `origin/main`
`52c153cd1dcf7eb8a716559216a30b245dd6a7e2` (#1220, the activation). This record carried a working id and was minted as LG-1468
on 2026-10-06. The dispatch record is the lead's local file
`gi-pricing-plan.local/handover/DISPATCH-WK-1178-SL1430-2026-10-05.md`; it is not in the repository. Stamps are BST.

FD-1425 is OPEN (its wiring limb is a later slice's). Nothing in this slice bears on an approval.

## Tasks

### Task 0 — preconditions

**Dispatch tree.** `52c153cd1dcf7eb8a716559216a30b245dd6a7e2`, author date `2026-10-05T22:40:59+01:00`.
`uv sync --all-packages` ran. Test database `gipricing_sl-1430_db8a5a62`, made with `docker exec gi-pricing-postgres-1
createdb -U gipricing -T gipricing …` and migrated with `alembic upgrade head`.

**Rows 0.1–0.11** re-run on that tree: all match. Line-number differences only: row 0.7's predicate prints
`rating_versions.py:110` and the two seed lines (`examples/fremtpl2/model.py:396`, `:397`); the plan expected `:113` too.
Row 0.10: the three find strings occur once each (`03:908`, `:436`, `:134`). Row 0.11:
`MODEL_REFERENCE_MODE_INCONSISTENT` is at `03:109` and `03:936` and in no code, so Task 3 Step 5 and Task 5 Step 3 apply.

**RL-1428 against its draft** (`RL 9695` (working id) at `614ad96b`, by `git diff` of the two blobs): id substitutions, the three
amendments the plan names, and the CR-838 correcting-record bullet. The T1–T3 find and replace strings are unchanged.
RL-1428 lines 150 and 166 carry `<date>` and an unbalanced ")" in "RL-1428), FD-1421.)". The lead sent it to the
maintainer (by delegation); **T-texts are not applied until the lead relays the ruling.**

**Trial merge-tree with S7** (Step 5): not yet run for real. A first run at an empty branch (equal to `origin/main`)
against `origin/sl-1391-…` (`386f4d54`) exited 1 on `docs/INDEX.md` only (S7's branch is behind main); `03` auto-merged.
The real trial waits for S7's pushed head and this slice's `03` edits.

### Task 1 — the tests, red first

Module `backend/tests/test_rating_version_create_pins.py`, as PL-1429 Task 1 Step 1 gives it. Literals checked against the
source before the run: `AuditEventRow.action`, `.entity_ref`, `.after` exist (`db/models.py:226-230`); the helpers
`_empty_pins`, `_run_compile_job`, `_minimal_algorithm`, `_headers`, `_table`, `valid_algorithm`, `_fitted_gbm` exist.
No literal was corrected.

Run at the dispatch tree, before any code change (`OMP_NUM_THREADS=1 nice -n 19 uv run pytest -q
backend/tests/test_rating_version_create_pins.py`): **13 failed, 1 passed**.

- Control passes: `test_a_version_created_without_algorithm_or_pins_is_refused_at_compile`.
- `test_the_create_body_is_the_model_schema_type`: `AttributeError: module 'model_schema' has no attribute 'RatingVersionCreate'`.
- `test_model_reference_mode_inconsistent_is_registered_and_owned`: `AssertionError: assert 'MODEL_REFERENCE_MODE_INCONSISTENT' in frozenset({…})`.
- The four `test_a_pin_of_another_type_is_refused[…]` cases and `test_an_algorithm_ref_of_another_type_is_refused`:
  `AssertionError: assert 'EXTRA_FORBIDDEN' == 'VALUE_ERROR'`.
- `test_a_mode_mismatch_is_refused_at_create`: `assert 'VALIDATION_FAILED' == 'MODEL_REFERENCE_MODE_INCONSISTENT'`.
- `test_a_version_created_with_its_algorithm_and_pins_compiles_over_http`, `test_an_unknown_algorithm_is_refused_at_compile`,
  `test_an_unapproved_model_pin_is_refused_at_compile_and_compiles_after_approval`,
  `test_a_peril_structure_pin_is_stored_and_compile_reports_no_resolver`,
  `test_the_creation_event_records_the_declared_pins`: `assert 422 == 201` on the create (a `VALIDATION_FAILED` 422 on
  `algorithm_ref` and `pins`).

### Task 5 (RL-1428's three texts) — MINT-ARTIFACT CORRECTION

RL-1428 lines 150 and 166 (T2 and T3), and line 143's text (T1), carry "RL-1428), FD-1421.)": the mint replaced the
working id "RL 9695" with "RL-1428)" and left the closing ")" of the old parenthesis. The maintainer (by
delegation) ruled, in the `to-lead.md` entry headed `2026-10-05 22:44:21 BST — RL-1428's T-texts: the stray ")" is a MINT ARTIFACT; apply with it removed`, that the ONE stray ")" is removed
when the texts land: "(… <date>, RL-1428, FD-1421.)", with `<date>` the commit date (2026-10-05). Everything else is
byte for byte. RL-1428 itself stays unedited.

The three find strings each occurred once in `docs/specs/03-rating-engine.md` before the edit (a script asserted it).
After the edit, by `grep -cF` over that file: the stray form `RL-1428), FD-1421.)` **0**; `*(Amended 2026-10-05,
RL-1428, FD-1421.)*` **2** (T1 at §5.1's create row, T3 at FR-237); `*(Discharged 2026-10-05, RL-1428, FD-1421.)*` **1**
(T2 at §4.3's note).

### Task 2 — the typed request

`RatingVersionCreate` is added after `RatingVersion` in `model_schema/rating.py` with `_PIN_TYPES` (DP-3 (a)); exported in
`__init__.py`; `GENERATED_SHAPES` and `ONE_SIDED_SLUGS` each gain `rating-version-create`. **Slug narrowing:** `slug` is
`Slug` (as `RatingVersion.slug`), where the route-local class used `str`; a slug the old body took and the stored shape
refuses would already have failed `to_schema` on read, so the boundary now refuses what could never be read back.

**Step 4 red, recorded out of order.** The `ONE_SIDED_SLUGS` entry was written before the run, because gate-1 was held
(S7) and no run was allowed. When the slots freed, the entry was reverted and `uv run pytest -q backend/tests/test_contracts.py
-k one_sided` printed: `AssertionError: a schema present on exactly one side must declare that in ONE_SIDED_SLUGS (OQ-649
(b)): ['rating-version-create']`, `FAILED …::test_every_one_sided_slug_is_declared`, `1 failed, 153 deselected`. The entry
was restored; `generate-contracts.py` wrote `rating-version-create.schema.json` and `openapi/generated.json`;
`generate-contracts.py --check`: `46 generated contracts match the models`; `pytest -q backend/tests/test_contracts.py`:
`152 passed, 2 skipped`.

### Task 3 — the service and the route

Service takes `algorithm_ref`, `pins`, `model_reference_mode`; stores them; the audit `after` carries them. The FR-223
check runs when `algorithm_ref` resolves (DP-1 (a)), after `flush()` and before `audit.record` (it reads the stored row via
`to_schema`; the caller's unit of work rolls the row back on the 422). `MODEL_REFERENCE_MODE_INCONSISTENT` is appended to
`RATING_ERROR_CODES`, the only change to that set, as the corrected STOP (ii) allows. `03:929-936` is untouched. Route-local
`RatingVersionCreate` removed; the handler docstring now says the algorithm and pins are declared and the shape checked here.
`grep -rn RatingVersionCreate backend/src` prints the import and the handler annotation. Per Task 5, RL-1428's T1-T3 land in
this commit.

Green: `pytest -q backend/tests/test_rating_version_create_pins.py`: `14 passed`; `test_rating_versions.py`: `43 passed`;
`test_rating_version_compile.py`: `20 passed`. `ruff check` on the changed files is clean (one `I001` fixed; the new test file
formatted). FR-223's `03:109` is not edited in this commit; RL-1438's T1 lands later (below).

### Task 0 Step 5 — the trial merge-tree with S7 (real, after the 03 edits)

`git merge-tree --write-tree --name-only 19f8842f1a18743a78c0f97f4bb7b21c52e0d259 <this head c7f4956d>`: **exit code 1**,
tree `986a8dc37468accb1349ee70810d86a7d017b867`. The only conflicted path is `docs/INDEX.md`, the generated index
(regenerated, never hand-merged; neither branch's INDEX is final until its mint). `docs/specs/03-rating-engine.md`,
`docs/contracts/openapi/generated.json` and `model_schema/rating.py` auto-merged. So the `03` §5.1 rows do not conflict:
option (b) holds for the `03` text; the INDEX conflict is the exempt generated path.

### Task 4 — the seed through the create path (DP-4 (a))

Red (Acceptance 12), recorded at Task 0 row 0.6 and re-read at the dispatch tree: `grep -rnE "\.(algorithm_ref|pins)\s*=[^=]"
--include=*.py examples/ backend/src/` printed `examples/fremtpl2/model.py:396` and `:397`. After the edit it prints nothing
(grep exit code 1). `save_demo_algorithm` is extracted; `author_demo_rating_evidence` drops the save and the two row writes;
`create_approved_rating_version` saves the algorithm first and passes it and `Pins()` to the service; `_EMPTY_PINS` is
removed (no other reader). `backend/tests/test_demo_rating_evidence.py::_draft` does the same.

Green: `test_demo_rating_evidence.py`: `2 passed`. `examples/fremtpl2/test_seed.py`: first `7 passed, 1 skipped` (the skip,
`test_seed.py:136`, needs the freMTPL2 download). The data directory (35 MB, ignored by `.gitignore:61`, never committed;
the porcelain status stayed clean of it) was then copied from the shared checkout into the worktree's
`examples/fremtpl2/data/`, and the file re-run: **`8 passed in 26.39s`**; `test_the_seed_reruns_against_a_seeded_database`
took 23.91s. That test runs `seed.run` twice against a scratch database, so `create_approved_rating_version` ran end to end:
the version is created with its algorithm and `Pins()` through the service, compiled by the `rating.compile` Job (which
refuses a version with no stored algorithm), and approved. **Acceptance 13's pass clause is evidenced.** Its second clause,
that the seeded version's `rating_version.created` event carries the algorithm ref, is not asserted by that test; the
event's `after` content is asserted at the route by `test_the_creation_event_records_the_declared_pins`, and the seed calls
the same service function.

### Pre-gate: the F83 exemption line pair, and the seed-data run

**`scripts/audit-docs.py` (outside PL-1429's write set; ruled).** `audit-docs` checks 30 and 35 failed on
`docs/contracts/schemas/generated/rating-version-create.schema.json` ("not in the F83 exemption register"). The executor
stopped and reported. The maintainer (by delegation) ruled, in the `to-lead.md` entry headed `2026-10-05 23:05:41 BST — SL-1430 STOP (write set): ONE dated line in audit-docs.py's F83 exemption list ALLOWED, by a dispatch delta; the seed-data evidence run ALLOWED on conditions`, to add ONE line pair in PL-1392's form and
nothing else in that file: the comment `# 2026-10-05, PL-1429 (WK-1178 SL-1430)` and the path line, next to PL-1392's
entries. The diff of that file against `origin/main` is exactly those two added lines. After it, `audit-docs` fails only
check 32 (this ledger's own working id is not in `docs/INDEX.md`) and check 39 (`docs/INDEX.md` stale), both cleared by
`doc-index` in Task 6; checks 30 and 35 are green.

**The Acceptance 13 seed-data run (ruled allowed).** Command: copy the shared checkout's `examples/fremtpl2/data/` into this
worktree's `examples/fremtpl2/data/`, then `OMP_NUM_THREADS=1 nice -n 19 uv run pytest -q examples/fremtpl2/test_seed.py`, one file,
outside any held gate, both slots checked first. Provenance: freMTPL2, the public dataset `examples/` carries; the directory is
ignored by `.gitignore:61` and is not committed. Result: `8 passed in 26.39s`. **CI cannot run it**: CI has no copy of the data,
so `test_seed.py:136` skips there, and the seed path's evidence is this local run only.

### RL-1438's T1 on FR-223 (`03:109`), after the mint

RL 9758 (working id) minted as RL-1438 with #1061 (main `289690ccefabfa0ba87a40ccdefffc741f7cea4b`); this branch merged `origin/main`
(no rebase). T1 is applied byte for byte from the minted record's text block, with its two placeholders resolved as the
record says: `<date>` = the commit date, 2026-10-05, and `RL-<this>` = `RL-1438`. Find string `(`02` OQ-575, decided
2026-08-17.) |`: `grep -cF` **1** before, **0** after (it is replaced by the same text plus the amendment, ending ` |`).
After: `**Amended 2026-10-05 (`RL-1438`): the check runs where` **1**; `RL-<this>` in `03` **0**. FD-1437's S3 re-reads FR-223
and does not re-apply it (the lead's ruling).

### The gate-1 failure at 260ead66 and the (B') fix (2026-10-06)

**Failed gate (evidence, not the gate).** Full gate at `260ead6640ed3a784426f38b0771206ec30ea8a1` (tree
`077077b6d9118173201bffd7f90fb798a1f8ccab`), gate-1, 00:08:43–00:39:45 UTC: ruff, mypy, lint-imports, req-coverage and
`generate-contracts --check` exit 0; `audit-docs` exit 1 (check 31, the unminted working id 9483); pytest exit 1, `15 failed,
4955 passed, 3 skipped`; frontend half all 0 (vitest 97 files, 615 tests). Of the 15: 13 are the unminted-id state; two are real
reds outside the mint state: `test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for` (an unlisted
`str(exc)` sink in `create_rating_version`) and `test_audit_docs_ids.py::test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts` (`82 == 81`, from the F83 exemption line).

**The false premise.** The 01:42:13 BST delta item 1 said to wrap the FR-223 detail with `safe_exception` "as compile_rating_version
does". It does not (its sink is a row-only `_SINKS` entry), and a wrap reduces the plain `ValueError` detail to `ValueError`,
breaking `test_a_mode_mismatch_is_refused_at_create` at the `"s_rp" in detail` assertion. The maintainer (by delegation) re-ruled to
(B') in `to-lead.md` "2026-10-06 01:44:23 BST — SL-1430: RE-RULED (i)–(iii) to (B')".

**(B') applied.** No change to `rating_versions.py`. One `_SINKS` row in `backend/tests/test_error_sinks.py` for
`create_rating_version` / `str(exc)`, in compile's form. `tests/test_audit_docs_ids.py`: 81 → 82 with a dated comment (f05fd208).
Sentinel `test_the_mode_refusal_detail_names_the_step_and_modes_and_nothing_from_the_pins` (NFR-499): the detail names the step
and both modes, and a marker planted in `pins.rate_tables` is absent from the response. The detail text,
`check_model_reference_mode`, names the step id and the two modes; it does **not** name a model ref, so the sentinel asserts the step
and the modes, not the refs. **Red, honestly:** with no code change to make the sentinel red, it passed on first run (19 passed with
the sinks file). Its force was shown by mutation: appending `repr(pins)` to the detail at `rating_versions.py:298` made it fail with
`assert 'marker-zq9x4' not in …`, and the file was restored by `git checkout` (porcelain showed only the two test files). The
`_SINKS` red is the failed gate's own census failure above.

### The full gate at 343ef9bb (2026-10-06) — ACCEPTED by the lead

**Tree.** Head `343ef9bb3bee01b67a2c1de827a1b1e18fd0b34b`, tree `bd69616d74b47404f01810fa6334e187c52e17ae`: the (B') commit
on `56acb6fb830c66a745acc58bdd73c6f94e300a68`, which merged `origin/main` `a9ef677747a98a156c1d4e8b8ae9d2b43c4e3ee5` (a merge, no rebase;
`docs/INDEX.md` was the one conflict, regenerated with `scripts/doc-index.py`; `alembic heads` = 1, `f3a7c1d9e2b4`). Test DB
`gipricing_sl-1430_db8a5a62`, migrated to head before the run. **Slot:** gate-1 (granted by the lead, 01:48:42 BST wording ruling then
grant), single `flock -n` run, both halves; gate-2 free at every snapshot. The failed run at `260ead66` (above) is evidence, not this gate.

| stage | exit |
|---|---|
| ruff | 0 |
| mypy | 0 |
| lint-imports | 0 |
| audit-docs | 1 (one FAILED line: check 31, gap between 1444 and 9483) |
| req-coverage | 0 |
| generate-contracts --check | 0 |
| pytest | 1 — `13 failed, 5052 passed, 3 skipped, 92 warnings in 1969.47s (0:32:49)` |
| frontend install / generate:api / lint / type-check / test / build | 0 / 0 / 0 / 0 / 0 / 0 — vitest `97 passed` files, `615 passed` tests |

**Load and memory.** Python half 00:49:19 → 01:22:25 UTC: load 1.46 → 1.40; used 14975 → 15561 MB, free 11859 → 11023 MB.
Frontend half 01:22:26 → 01:23:54 UTC: load 1.40 → 6.81 (the build's tail); used 15560 → 15690 MB.

**The 13 pytest failures** are the unminted working-id state (this record's working id was not in the allocation, main's allocation ended at 1444), each
message reading `requirement numbering: 0 module-scoped id(s)…` or `live allocation is not contiguous: [(1444, 9483)]`: `test_audit_docs_ids`
×2, `test_doc_index` ×1, `test_register_lint` ×3, `test_register_owed` ×1, `test_repository_invariants` ×2,
`test_audit_docs_process_core_digest` ×2, `test_audit_docs_w37_11_ceiling` ×1, `test_audit_docs_finding_citations` ×1. The lead
matched them by file to the known check-31 set and accepted the gate. That they clear at the mint is expected, not proven here.
**Both earlier real reds are cleared:** `test_error_sinks` census (passes) and `test_widening_the_scope…` (`82`, passes).

**Trial merge-trees** (`git merge-tree --write-tree`, at the pre-fix head `260ead66`): against `origin/main` `8f5a8987`: rc 1, tree
`59a66bce7abfdda84948a0746e963b3b762e248e`; against S7 `origin/sl-1391-…` `89fcb092`: rc 1, tree
`2752bbdec5582831fd328b4481fd471df81243d9`; against SL-1436 `origin/sl-1436-…` `a0ad36be`: rc 1, tree
`8a73d06e8af880747e6d4241f1df4df808dab134`. The only conflicted path in each: `docs/INDEX.md` (generated, exempt). S7 has since
merged: `merge-tree origin/main(a9ef6777) HEAD` before the merge, rc 1, tree `0e648dade8109e1ecb0590b3ecf567a7167f6e09`, conflict
`docs/INDEX.md` only.

## PRs

#1227, a draft. The branch `sl-1430-fd-1421-rating-version-algorithm-and-pins` is pushed; the PR is not merged by the executor.

## Closing note (2026-10-06)

This ledger is closed under the executor charter's mint-step clause (`.claude/roles/executor.md`, "As the mint step…", added
2026-10-04) and `docs/process/document-ids.md` §1.6's 2026-10-04 amendment to the SL and LG close cells: on 2026-10-06 the executor
performed the closing acts in the mint commit on the auditor's behalf, after the slice audit — the front matter `status: closed`,
the roadmap `SL-1430` row `status: closed` with its dated line, `docs/INDEX.md` regenerated, `audit-docs` run. `tree:` stays as filed; `created:` is the mint date, the
original 2026-10-05 kept in the comment, because check 31 requires `created` non-decreasing with the number and the ids 1445 to 1455 (the B1 mint, #1230)
are dated 2026-10-06. The working id this record carried before the mint is replaced by `LG-1468` in the record's `id:` and its provenance
sentence; it remains only inside the verbatim gate outputs of the gate section (`between 1444 and 9483`, `the unminted working id 9483`,
`[(1444, 9483)]`), which are quotations of tool output. `origin/main` was `a9ef677747a98a156c1d4e8b8ae9d2b43c4e3ee5`, the merge-base of the audited head, when the mint began; it then
moved to `c6886bda9ce1c200a921d490530a79cbfb3ca820` (#1230, the B1 mint: docs-only, `git diff --name-status a9ef6777..c6886bda` lists only
`docs/` paths), which the mint merged into the branch (merge-tree rc 1, the one conflict `docs/INDEX.md`, regenerated). It moved again to `f871ee8dad8d670e3576b626546ecf40e37d8569` (the chain mint, with a dependency bump and a skill update,
`uv.lock` and `.claude/skills/` among its paths), which the mint merged the same way on the lead's ruling (merge-tree rc 1, the one conflict `docs/INDEX.md`, regenerated).
The `docs/`-only reading of condition (a) held for this branch's own delta, `343ef9bb` to the merge of `c6886bda`; the later merge of `main` (f871ee8d) brings non-docs paths that are `main`'s own,
among them a `fastapi` 0.142.2 bump under this slice's new route. The maintainer (by delegation) therefore ruled a FULL gate for SL-1430 after that merge, which supersedes the waiver for this slice;
a full two-half gate runs on the merged head after the lead's gate-slot grant, and its result is recorded in a later entry, not here. The register is unchanged by this mint: `FD-1421`'s row
names its own event, "the WK-1178 slice merges … and `03:908` and `RatingVersionCreate` agree", after which the auditor sets it
closed; `FD-1437` stays with WK-675 S3's leaf, since this slice applied only RL-1438's create-time refusal (item 2), not the
compile-site code or the sweep of bare `ValueError` raises.

### The slice audit, quoted (local, not in the repository: `handover/audit-sl1430-2026-10-06.md`)

Verdict summary, verbatim: "No blocking finding. Two LOW observations, both accept. Proposed: **clean slice audit, subject to the
lead's merge**." Audited head `f4dc6f2837f967adbeb3e08094c49a14c96fd90e`, range `origin/main...f4dc6f28`. The findings, verbatim
openings: "**L1 (LOW; accept, or defer to a note)** — Acceptance 13's second clause … is asserted by no test." and "**L2 (LOW;
accept)** — the 13 gate failures are matched to the known check-31 set by file and count, not by node id; the raw pytest log is not in
the repo."

### The lead's verdicts (local: `channel/from-lead-2026-10-06.md`, the entry "2026-10-06 02:28:24 BST")

Verbatim: "**L1 ACCEPT** — Acceptance 13's second clause (the seeded version's created event carries the algorithm ref) has no own test;
the ledger discloses it and rests on the route-level creation-event test (the seed calls the same service function). **L2 ACCEPT** —
the 13 matched by file and count, not node id; the minted-head run clears them. The "refs" disclosure ACCEPTED (your 01:48:42 amended
item 9). The ValueError→code mapping also catching a corrupt stored algorithm's ValidationError: noted, judged unreachable, no action."

### The minted-head gate is WAIVED

Under the maintainer's (by delegation) ruling, entry header verbatim (`to-lead.md`): "2026-10-06 02:28:42 BST — The minted-head gate
(executor.md :42, the SL-1377 order): WAIVED for a DOCS-ONLY mint delta, on conditions; a LOW FD to amend the charter". Its
conditions, verbatim: "(a) git diff --name-status <the gated head>..<the mint head> lists ONLY docs/ paths (INDEX, the register, the
roadmap, the ledger, and the minted record files); (b) CI at the mint head is FULL green, with the python job's pytest totals line READ
from the job log (not just the step status), showing 0 failed; (c) the slice's own full local gate ran at the gated head with only the
known check-31 set failing, as recorded in its ledger." The gated head is `343ef9bb3bee01b67a2c1de827a1b1e18fd0b34b`; condition (a)'s
name-status is in the PR body, and (b) is the lead's to read at the merge ACK.

## The full gate after the merge of main (2026-10-06)

The maintainer (by delegation) ruled a full gate for SL-1430 after main's merge (see the closing note). Run by the executor on the lead's
"GATE SLOT GRANTED gate-1 (lead, 03:58:17 BST …) for 78ca39af3efe4079e754265187a759d45da4a087": the verbatim `dev-commands` gate body,
slot `gate-1`, 02:59–03:30 UTC on the box clock; the test database recreated from the template and `alembic upgrade head` (exit 0) first;
scratch under `/home`. Head `78ca39af3efe4079e754265187a759d45da4a087`.

| stage | exit |
|---|---|
| ruff | 0 |
| mypy | 0 |
| lint-imports | 0 |
| audit-docs | 1 (one FAILED line: `check 31: gap in the full allocation between 1466 and 1468`) |
| req-coverage | 0 |
| generate-contracts --check | 0 |
| pytest | 1 — `13 failed, 5052 passed, 3 skipped, 92 warnings in 1781.25s (0:29:41)` |
| frontend install / generate:api / lint / type-check / test / build | 0 / 0 / 0 / 0 / 0 / 0 — vitest `97 passed` files, `615 passed` tests |

**The 13 pytest failures**, by file: `test_audit_docs_finding_citations` ×1, `test_audit_docs_ids` ×2, `test_audit_docs_process_core_digest` ×2,
`test_audit_docs_w37_11_ceiling` ×1, `test_doc_index` ×1, `test_register_lint` ×3, `test_register_owed` ×1, `test_repository_invariants` ×2.
Twelve read `requirement numbering: 0 module-scoped id(s)…`; the thirteenth, `test_audit_docs_ids::test_doc_id_check_exits_0_on_the_real_tree`,
reads `[noncontiguous] docs/INDEX.md has a gap be…`. All are the unminted allocation gap (`LG-1467` was not on `main` at that head), the same
eight files and counts as the gate at `343ef9bb`; matched by file and message, not by node id. No failure outside that set, so the route
passes under `fastapi` 0.142.2.

### The post-gate merge of main, option (A)

The maintainer (by delegation) ruled, "2026-10-06 04:28:45 BST — SL-1430 after its gate: option (A), merge main without a second full gate, ON CONDITIONS, including the frontend half" (`to-lead.md`). Main had moved past `f871ee8d` by #1228 (SL-1436) and #1234 (`uv.lock`), to `8bc01ae85599de47f2efe94bb7001ddade458fc1`, which the executor merged (merge-tree rc 1, the one conflict `docs/INDEX.md`, regenerated; `docs/contracts/openapi/generated.json` auto-merged, then `generate-contracts.py` printed `46 contracts up to date` and `--check` exited 0 with `46 generated contracts match the models`). Local, behind the slot probe, `nice`, `OMP_NUM_THREADS=1`:
`backend/tests/test_contracts.py`, `test_rating_version_create_pins.py`, `test_demo_rating_evidence.py`, `test_rating_versions.py`, `test_rating_version_compile.py` and `test_traces_api.py`: `240 passed, 2 skipped, 6 warnings in 68.33s (0:01:08)`; frontend `generate:api` 0, `type-check` 0, `build` 0. The CI at the merged head is the lead's to read.
