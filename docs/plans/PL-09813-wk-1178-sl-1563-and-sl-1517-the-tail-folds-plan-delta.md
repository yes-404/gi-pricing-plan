---
id: PL-9813
family: plan
kind: map
title: WK-1178 — the tail folds for SL-1563 (money_minor closed both ways) and SL-1517 (NFR-498 Audit Events): a dated delta to PL-1562 and PL-1516
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-11
owner: planner
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1562, PL-1516, SL-1563, SL-1517, FD-1424, FD-1513, RL-1564, RL-1515, RL-1555, SL-1559, SL-1340, SL-1391]
---

# PL 9813 — WK-1178, the tail folds for SL-1563 and SL-1517 (delta to PL-1562 and PL-1516)

> **For agentic workers:** this is a **dated delta** under Lean P2 L5 (`document-ids.md` §1.6,
> PL row: *"a change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's
> plan"*). WK-1178 has no Work plan, so, as for
> [`PL-1577`](PL-01577-wk-1178-r6-the-exit-demo-dislocation-portfolio-a-20000-policy-sample-built-by-the-seed-plan-delta.md),
> this delta `relates:` the leaf plans it changes. It replaces neither
> [`PL-1562`](PL-01562-wk-1178-money-minor-closed-both-ways-at-save-leaf-plan.md) (SL-1563) nor
> [`PL-1516`](PL-01516-wk-1178-nfr-498-audit-events-on-rate-table-and-algorithm-writes-leaf-plan.md)
> (SL-1517). Their bodies are frozen and are not edited. **Read the leaf plan first, then this
> file's part for that slice. Where they differ, this file is the later statement.** Each
> slice's executor binds the skills its leaf plan's header names (`python-test`,
> `test-driven-development`, `python-package`, `fastapi-service`, `spec-change`,
> `dev-commands`, `git-hygiene`), and is spawned from `.claude/roles/executor.md`.

Filed under working id 9813, reserved by the lead in `handover/brief-wave3-2026-10-11.md`.
Written 2026-10-11 by the planner (planner-9813). It mints in D11 or D12 (the 11:45:03 entry,
item 5). **Tree read:** `origin/main` `02f23b4a` (#1273). Every repository `file:line` below
was read at `d699a561` (#1272), and `git diff --name-only d699a561 02f23b4a` touches none of the
cited code, test, plan or ruling files (only `docs/roadmap.md`, outside the two rows edited
here). Branch heads read: WK-675 S4, `origin/sl-1559-wk675-s4` @`af4f634b` (unmerged).

## The rulings this delta records

Three entries in `~/gi-pricing-plan.local/channel/to-lead.md`, by the maintainer (by
delegation), each read in full by this planner. A repository reader cannot resolve a local
entry (RFC-777), so the parts this delta rests on are quoted verbatim.

**"2026-10-11 11:45:03 BST — WK-1178 tail: GO SL-1566; SL-1563 write-set (a) YES; SL-1517 fold
YES, DP-6 → the decision-maker; ONE delta PL 9813; SL-1569 last"**, items 2, 3 and 5:

> 2. SL-1563: (a) YES. test_rating_glm_model_call.py joins the write set for :463–475 only. The ("money_minor","decimal") pair moves from the LEGAL controls to the REFUSED cases, because closing money_minor at save is exactly this slice's purpose. The other A-2 asserts stay byte-identical (the LG shows a diff of that file limited to those lines). PL-1562 :607 "A-2 tests unedited" is superseded for those lines only, by the delta. The row's stale "Open: DP-1" gets a dated line (DP-1 was ruled; cite where).
> 3. SL-1517 (NFR-498, BOUND before the freeze): the 3-file write-set fold is YES, each file named in the delta. NEW DP-6 (WK-675 S4's manual_edit_confirmed is a fourth version writer with no RL-1515 DP-3 action) goes to a decision-maker, with options incl. your `rate_table_version.edited`, matched against the existing audit action vocabulary (the RL-1515 DP-3 list and the audit-event contract), so the name is consistent. Timing: right after WK-675 S4 merges, latest GO Thu 29 Oct.
> 5. ONE delta, PL 9813, covering PL-1562 and PL-1516 (same Work, L5). It mints in D11 or D12.

**"2026-10-11 11:48:00 BST — MERGE-ACK #1273 …, and SL-1563 DP-7 = (i)"**, its last paragraph.
This planner raised DP-7 to the lead because the range in item 2 does not reach the refused
cases' list (§A1):

> SL-1563 DP-7 = (i): widen the write-set bound to test_rating_glm_model_call.py :456–475 for exactly 3 changed lines: add "decimal" to :456's parametrize list, drop the pair from :469, relax :463. Every other A-2 assert stays byte-identical (the LG shows that file's diff). (ii) is rejected: it duplicates a test body.

**"2026-10-11 11:49:51 BST — DP-6 (SL-1517) RULED (a): a 5th audit action
`rate_table_version.edited`, carried by an ADDITIVE RL 9817; the three fold items into PL 9813
ADOPTED; RL-1515's body is NOT touched"**, items 1 to 4:

> 1. (a) ADOPTED: `rate_table_version.edited` (FR-229; fits ^[a-z_]+\.[a-z_]+$). It maps 1:1 to WK-675 S4's `created_by_edit`, as `.imported` maps to `created_by_import`. `.updated` stays reserved for mutable entities. The rejected options are rejected for the memo's reasons: the fold into `.imported` breaks DP-3's distinct actions; a generic `.created` loses the source; leaving edits out is an NFR-498 gap past the freeze.
> 2. CARRIER: RL 9817 is ADDITIVE (relates: RL-1515; it does not correct it). PRECISION: RL-1515 is a frozen record, and its body is not edited. "The dated note after T-1b" goes in the SPEC text that T-1b inserted (wherever that text lives in docs/specs), as a dated line citing RL 9817. If T-1b's target is anywhere other than a spec, the note goes in RL 9817 only.
> 3. FOLD into PL 9813, adopted:
>    (i) `_stored_version` gains `created_by_edit`;
>    (ii) `manual_edit_confirmed` (WK-675 S4 rate_tables.py :1047) and its route (:172) join the Principal threading;
>    (iii) one new red-first test for the edit event, plus an edit-made version in item 13's comparison.
>    The action vocabulary in the audit-event contract (generated, never hand-edited) regenerates.
> 4. ORDER: SL-1517 merges AFTER WK-675 S4 (it carries the edit path). Latest GO Thu 29 Oct; BOUND before the 4 Nov freeze.

The readiness memo the 11:45:03 entry read (`handover/readiness-wk1178-tail-2026-10-11.md`,
planner-1178tail, §1 and §2) and the DP-6 memo (`handover/dm-dp6-2026-10-11.md`, dm-dp6) are
local files. Every fact this delta takes from them was re-read by this planner at the tree
above, and is cited here by its repository location.

## Status

`draft`. **No decision point is open:** DP-7 is ruled (i) (11:48:00 BST) and DP-6 is ruled (a)
(11:49:51 BST). Neither leaf plan has an open DP. Each slice's activation still waits on its
needs (§A6, §B7). The activation follows the L1 (a′) shape the readiness memo names: the slice
PR flips its leaf plan and this delta's part for it, with ONE `LG-`.

---

## Part A — SL-1563 (PL-1562): money_minor closed both ways at save

### A1. A-2's test file joins the write set: three lines (DP-7 (i))

The file is `packages/pricing-core/tests/test_rating_glm_model_call.py`. At `d699a561`:

| Line | Today | Change | Why |
|---|---|---|---|
| `:456` | `@pytest.mark.parametrize("declared", ["relativity", "percentage", "int"])` | becomes `["relativity", "percentage", "int", "decimal"]` | the pair `("money_minor", "decimal")` is D1 for a `model_call` producer (`:460` fixes the call type `money_minor`), refused "for EVERY producer" (PL-1562 :75) |
| `:463` | `assert "model_call" in issues[0].message` | becomes `assert "money_minor" in issues[0].message` | Task 3 Step 3 removes `model_call_money_issues` (`compile.py:128-152`, called at `:208` and `:238`). The one refusal left is `output_type_issues`'s, whose message (`compile.py:183-185`) reads "… its producing step yields 'money_minor' (FR-227)" and has no "model_call" in it |
| `:469` | `[("decimal", "decimal"), ("money_minor", "money_minor"), ("money_minor", "decimal")],` | becomes `[("decimal", "decimal"), ("money_minor", "money_minor")],` | the pair leaves the legal control. The two that stay are legal under B3 and A1 |

**Every other line of the file is byte-identical**, its other asserts included. The three
changes are made in this order, each shown by its cause:
- **Task 2 (the red commit): `:456` and `:469`.** The new `decimal` case of
  `test_a_money_minor_model_call_feeding_a_non_money_output_is_refused` fails at the base on
  `:462`: `validate_algorithm` returns `[]`, because `_compatible` passes every `_NUMERIC` pair
  (`compile.py:160-165`) and `model_call_money_issues` admits `decimal` (`:151`). That is the
  red. `:469`'s drop is a control that goes legal-to-refused, so it is made in the same commit
  as the move.
- **Task 3 Step 3: `:463`.** Remove A-2's branch first and run the file. The three existing
  cases fail on `:463` ("model_call" not in the general message). Record that line as printed,
  then relax `:463`. The four cases pass, each with exactly one issue (item 5).

**What this supersedes in PL-1562, for these three lines only:** `:607` ("Run A-2's item 15
tests **unedited**"; the 11:45:03 entry, item 2), and the same rule where PL-1562 restates it:
§"Global Constraints" (`:414-415`), the A-2 row of §"Write set" ("A-2's tests stay green
unedited", `:476`), Hand-off 3 ("This plan flips nothing of A-2's", `:645-646`) and Self-review
1 (`:658`). `:609`'s rule stands for everything else: a plan defect is reported, not worked
around.

### A2. The fourth call path: the mount-port check (SL-1340's caller)

SL-1340 merged on 2026-10-10 (`a3572d1a`, #1263). It added a caller of `_compatible` in
`_refuse_mount_port_type_mismatch` (`compile.py:686`, the call at `:702`), which the compile
path calls at `:1034`. PL-1562's Hand-off 4 gave that call's new argument to "PL 9610's
executor"; SL-1340 merged first, so it is **this slice's**:
- **`:702` passes `at_output_step=False`.** A mount port is not an output step. This is DP-1
  (ii)'s convention, "a sub-graph port carries money as decimal; money_minor is produced only at
  an output step" (RL-1564, Ruled item 3, `:152`). So `decimal` → a `money_minor` port is
  refused at mount, as D9 is at an output port.
- **Item 15 (new): the mount path refuses every refused direction (P, appended).**
  `test_a_mount_port_refuses_a_closed_direction`, parametrised over the refused set and D9. A
  parent value of the producer type is mapped to a fragment input port of the declared type.
  `_refuse_mount_port_type_mismatch` raises `RATING_TYPE_MISMATCH` once. The allowed set
  (A1, A3–A7) raises nothing. **Red first:** at the base each refused case raises nothing.
- **Item 12 (c) is owed here.** PL-1562 item 12 (c) is "owed by whichever of SL-1340 … and
  PL-1562 merges SECOND" (the 17:58:03 BST entry, quoted at PL-1562 :169). `git grep -n
  mounted_decimal 02f23b4a -- . ':!docs'` prints nothing, so SL-1340 did not build it.
  `test_a_mounted_decimal_port_rounds_once_at_the_parent_output` goes into the item 12 (b)
  module, `packages/pricing-core/tests/test_rating_decimal_money_rounds_once.py`, which is
  already in the write set.

### A3. Re-anchors and facts moved since PL-1562's tree (`4d3be141`)

The logic of each function is as PL-1562 describes it. Only the lines moved (Task 0 Step 1
re-anchors them by symbol at the dispatch tree):

| Symbol | PL-1562 | At `d699a561` |
|---|---|---|
| `_NUMERIC` | `compile.py:57` | `:65` |
| `producer_types` (now types `model_call` steps too, A-2) | `:95-116` | `:86-111` |
| `model_call_money_issues` (A-2's branch, removed by Task 3 Step 3) | — | `:128-152`; called at `:208` and `:238` |
| `_compatible` | `:124-129` | `:160-165` |
| `output_type_issues` | `:132-155` | `:168` |
| `_check_result_types` | `:158-170` | `:194` |
| `fragment_output_type_issues` | `:173-199` | `:212` |
| `_refuse_mount_port_type_mismatch` | — | `:686`, the call at `:702` |
| `ALGORITHM_CHECKS` | `:359-363` | `:464` |

- **A second `validate_algorithm` consumer exists.** WK-675 S3 added live validation:
  `backend/src/app/platform/rating_algorithms.py:302` (`AlgorithmValidationReport(issues=
  validate_algorithm(algorithm))`). The new refusals therefore also surface in the designer.
  No file of it is written. The sweep (item 7) covers its tests, because they are under
  `backend/tests`.
- **The sweep's population grew.** PL-1562's DP-2 predicate
  (`git grep -n -E '"result_type"\s*:\s*"money_minor"|result_type[^,)\n]*=\s*"money_minor"|result_type:\s*money_minor' d699a561 -- . ':!docs'`,
  the table's `\|` read as `|` under `-E`) prints **63 lines in 31 files** at `d699a561`,
  against 28 in 18 at `5fe56b87`. It is still the same STOP: a hit other than `P:389` is a STOP
  to the maintainer (by delegation) with `file:line` (PL-1562 Task 1 Step 2).
- **Two stale lines in PL-1562, not edited (frozen):** Self-review 1 (`:671-672`) still says
  DP-1 "stays open"; DP-1 is ruled (ii) (RL-1564, `:152`). Task 2's steps are numbered 1, 2, 4;
  no step is missing.

### A4. Write set, as amended

PL-1562 §"Write set" stands, with these changes:

| Path | Change |
|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | as PL-1562, **plus** `_refuse_mount_port_type_mismatch` (`:686`): its `_compatible` call (`:702`) passes `at_output_step=False` (§A2); and Task 3 Step 3 removes `model_call_money_issues` (`:128-152`) and its two calls (`:208`, `:238`) |
| `packages/pricing-core/tests/test_rating_glm_model_call.py` | **edited, `:456`, `:463` and `:469` only** (§A1; DP-7 (i)) |
| `packages/pricing-core/tests/test_rating_compile.py` | as PL-1562, **plus** item 15 (appended) |
| `packages/pricing-core/tests/test_rating_decimal_money_rounds_once.py` | as PL-1562 (item 12 (b)), **plus** item 12 (c) (§A2) |

### A5. Collisions at the dispatch tree

At `02f23b4a`, no unmerged `origin/*` ref this planner read writes `compile.py`,
`test_rating_compile.py`, `test_rating_glm_model_call.py`, `test_sub_graphs_api.py` or
`platform/sub_graphs.py` (the readiness memo's file sets, re-read here for S4 only). The
dispatch record re-reads them by merge-tree at its own tree, because the snapshot ages.

### A6. Activation needs, as amended

PL-1562's needs 1–5 are **met** at `02f23b4a`: FD-1424 minted; OQ-1560 decided with its `03`
§10 mirror; DP-1 (ii) and DP-2 (r) ruled in RL-1564 (`:152`, `:173`); RL-1564 minted (Form A);
SL-1427 merged; the FD-1420 fix (SL-1448) merged. A-2 (SL-1463) merged first (`2edc4d89`,
#1262), so this slice removes A-2's branch (Task 3 Step 3). Need 6, the lead's GO and the
activation, is open. **The GO names:** this delta; DP-7 (i)'s three lines; the STOP on a sweep
hit; and the four call paths.

---

## Part B — SL-1517 (PL-1516): NFR-498 Audit Events, BOUND before the P2 code freeze

### B1. The three-file write-set fold (11:45:03 item 3)

PL-1516 Task 1 changes the four services' `created_by: UUID` to `actor: Principal`. Three test
files call them and are not in PL-1516's write set. Each changes **the call-site argument
only** (Task 1 Step 4):

| File | Calls at `d699a561` | Merged by |
|---|---|---|
| `backend/tests/test_rate_table_diff_portfolio.py` | `:196`, `:201`, `:866`, `:871`, `:1299`, `:1304` (6) | S7, `a9ef6777` (#1206) |
| `backend/tests/test_rating_version_dislocation_gate.py` | `:303` (1) | SL-1340, `a3572d1a` (#1263) |
| `backend/tests/test_rating_algorithms.py` | `:435` (1); PL-1516 lists the file as "read only" (`:643`) | SL-1477, `75f8a7b4` (#1245) |

The predicate, re-run at `d699a561`:
`git grep -n -E '(seed_from_model|import_confirmed|bulk_operation|create_algorithm)\(' d699a561 -- backend examples scripts`,
less the `def` lines and the `pricing_core` pure functions. It prints 36 call sites in 13 files.
Task 1 Step 1 re-runs it at the dispatch tree, and that output, not this table, is the set to
move. **Item 9's command gains the two files it does not run**:
`backend/tests/test_rate_table_diff_portfolio.py backend/tests/test_rating_version_dislocation_gate.py`.

### B2. The test shared with S7: this slice is the second to merge

S7 (`SL-1391`) merged first (`a9ef6777`, #1206). So, by PL-1516 D6, **this slice rebases**
`backend/tests/test_diff_cache.py::test_diff_is_computed_on_miss_and_served_from_the_cache_on_hit`
(now `:136`). Its writer calls are `_seed` at `:153`, imported from
`test_rate_tables_service.py` (`:143-146`, already in the write set), and
`svc.import_confirmed(...)` at `:160`, whose argument at `:163` is `principal.id`. The full gate
runs on the merged tree, as D6 says.

### B3. DP-6, ruled (a): the edit path is the fifth action

WK-675 S4 (`af4f634b`) adds a fourth caller of the single writer: `manual_edit_confirmed`
(S4 `backend/src/app/platform/rate_tables.py:1047`, `created_by: UUID` at `:1050`), which
persists through `_persist_new_version` (the call at `:1066`, the def at `:1328`). Its one
caller is the route at S4 `backend/src/app/api/rate_tables.py:172`. S4 adds
`RateTableVersion.created_by_edit` and the row column (migration
`backend/migrations/versions/d4e81b7a2c95_rate_table_version_created_by_edit.py`). Under
RL-1515 DP-1 (a), every caller of the writer passes an action, so the edit path needs one.
The ruling (11:49:51 items 1 and 3) folds three things in, and the order (item 4) is fixed:

1. **`_stored_version` gains `created_by_edit`.** PL-1516 D3's constructor gains
   `"created_by_edit": version_row.created_by_edit,` beside `created_by_import`. Without it,
   every audit state drops the field, and Task 1b (which routes `_persist_new_version`'s return
   through `_stored_version`) changes the 201 body of S4's edit route. Item 13's STOP would then
   fire.
2. **`manual_edit_confirmed` and its route join Task 1's threading.** `created_by: UUID` →
   `actor: Principal` (Task 1 Step 2's idiom), and the route at S4 `api/rate_tables.py:172`
   passes `caller.principal` (Step 3). In Task 3 Step 1 it passes
   `action="rate_table_version.edited"` and
   `before=_audit_state(_stored_version(base_row, base_cells), base_cells)`, the stored state of
   the version it edits (its `base_version`), as import does. Both files are already in the
   write set.
3. **One new red (item 3b), plus an edit-made version in item 13** (§B6).

**Order: SL-1517 merges after WK-675 S4** (11:49:51 item 4). No reverse order is planned. If S4
has not merged when this slice's GO is due, the GO waits (§B4).

**The contract.** `action` is constrained by pattern, not by an enum:
`docs/contracts/schemas/audit-event.schema.json:22` is `"pattern": "^[a-z_]+\\.[a-z_]+$"`, and
`git grep -n 'rate_table_version\.' 02f23b4a -- docs/contracts packages/model-schema/src` prints
nothing. So `.edited` needs no shape change. The ruling's "regenerates" is honoured by running
the generator: `uv run python scripts/generate-contracts.py --check` exits 0. If it ever does
not, the generated file is regenerated (never hand-edited), and the ledger names it. PL-1516's
"Not written: `docs/contracts/`" holds unless that happens.

**The spec text.** RL 9817 (additive, `relates: RL-1515`; it is not minted yet) carries the
dated note. Task 5 applies RL-1515's T-1a to T-1d byte for byte, then RL 9817's note **in the
spec text T-1b inserted**, as a dated line citing RL 9817 (11:49:51 item 2). If RL 9817 places
it elsewhere, RL 9817 governs.

### B4. Timing and the BOUND

- **GO: right after WK-675 S4 merges. Latest GO: Thu 29 Oct 2026** (11:45:03 item 3; 11:49:51
  item 4). The readiness memo recommends no later than Mon 26 Oct, so that a red re-gate fits.
- **BOUND: merged on `main` on or before Wed 4 Nov 2026** (PL-1516 item 12; roadmap `:584`,
  "Code freeze: Wed 2026-11-04"). The P2 phase closure record lists it (register `:328`). No P2
  phase CR exists yet; that obligation goes into the closing auditor's brief.
- **PL-1516 Task 4 Step 1's date.** "Reports to the lead before 2026-10-28" cannot hold for a GO
  on 27–29 Oct. For a GO after Mon 26 Oct, the GO record names the report date; for an earlier
  GO, 28 Oct stands. In both cases the executor reports at once if the merge date is at risk.

### B5. Re-anchors since PL-1516's tree (`5fe56b87`)

| Symbol | PL-1516 | At `d699a561` |
|---|---|---|
| `seed_from_model` | `rate_tables.py:96` | `:121` |
| `_wire_rows` | `:238` | `:263` |
| `import_confirmed` | `:419` | `:889` |
| `_load_version` | `:528` | `:998` |
| `_persist_new_version` | `:670` | `:1140` |
| `bulk_operation` | `:796` | `:1266` |
| `create_algorithm` | `rating_algorithms.py:94` | `:219` |
| `_write`, `create_sub_graph`, `create_version`, `_row` | `sub_graphs.py:59`, `:104`, `:127`, `:150` | `:63`, `:108`, `:132`, `:156` |
| `audit.record`, `verify_chain` | `audit.py:52`, — | `:52`, `:158` |
| `version_content_hash` | `diff_cache.py:46` | `:48` |

The reds are still red: `grep -n audit` over `platform/rate_tables.py` and
`platform/rating_algorithms.py` prints nothing at `d699a561`, and S4's `rate_tables.py` has 0
matches too (`git grep -c audit af4f634b -- backend/src/app/platform/rate_tables.py`).

### B6. Acceptance Standard changes (PL-1516)

- **Item 3b (new), the edit path, red first.** A confirmed manual edit
  (`manual_edit_confirmed`) on `<slug>@1` leaves exactly one event with
  `action == "rate_table_version.edited"`, `entity_ref == "rate_table:<slug>@2"`,
  `before == <@1's state>`, `after == <@2's state>` and
  `after["created_by_edit"]["edited_cells"] == <the number of cells edited>`. It carries
  `req("NFR-498")` and `req("FR-368")`, in `backend/tests/test_nfr498_audit_events.py`.
  **Red first:** at the base the query returns no row.
- **Item 8** counts the edit event among the events written.
- **Item 9's command** gains the two files of §B1. At Task 1's commit and at Task 3's, the
  only edits to the three fold files are the call-site argument.
- **Item 10's write set** is PL-1516's, plus the three files of §B1, plus
  `manual_edit_confirmed` and its route call in `platform/rate_tables.py` and
  `api/rate_tables.py`.
- **Item 13's set gains `R7`**, an edit-made version: after `R1`, a confirmed manual edit on
  `t-rows@<latest>` through S4's route (`POST /rate-tables/{slug}/versions` with
  `confirm: true`). **Seven** `cmp` exit codes, all 0, and the positive control's `cmp` reports
  a difference for `R7` too. Task 0 Step 2's re-enumeration (PL-1516 E2) still decides the full
  set at the dispatch tree.
- **Item 11** also records `uv run python scripts/generate-contracts.py --check` exit 0 (§B3).

### B7. Activation needs, as amended

PL-1516 D7's needs stand: 1 (FD-1513), 2 (RL-1514), 3 (RL-1515), 4 (SL-1427) and 5 (A-2,
`2edc4d89`) are met at `02f23b4a`. They gain:
- **3a. RL 9817 minted** (DP-6 (a), the additive note).
- **5a. WK-675 S4 (`SL-1559`) merged** (11:49:51 item 4).
- 6, the lead's GO, names: this delta; DP-6's three fold items; the rebase of `test_diff_cache.py`
  (§B2); the latest GO date and the BOUND (§B4).

---

## Acceptance Standard

This delta's own acceptance, checked from the repository root on the slice's merge tree. It
adds to each leaf plan's Acceptance Standard and changes nothing else in it.

**SL-1563** (PL-1562 items 1–13 stand, with these):

1. **A-2's file moves by three lines only.** `git diff -U0 <base>...HEAD -- packages/pricing-core/tests/test_rating_glm_model_call.py | grep -cE '^[-+][^-+]'`
   prints `6` (three `-` lines and three `+` lines), and their hunks start at base lines 456,
   463 and 469. The ledger quotes that diff in full (DP-7 (i)).
2. **The moved pair is red first.** The ledger holds the printed failure of
   `test_a_money_minor_model_call_feeding_a_non_money_output_is_refused[decimal]` at Task 2's
   commit (`[] == ['RATING_TYPE_MISMATCH']`, on `:462`), and of the three other cases on `:463`
   at Task 3 Step 3, before `:463` is relaxed.
3. **Item 15, the mount path, is red first and then green.** `uv run pytest packages/pricing-core/tests/test_rating_compile.py -q -k mount_port_refuses`
   fails at Task 2's commit for every refused case and passes at Task 3's.
4. **The mount-port call passes the flag.** `git grep -n "_compatible(" -- packages/pricing-core/src`
   lists every call with `at_output_step=` given, `:702`'s successor with `False`. The ledger
   names each.
5. **Item 12 (c) exists and passes.** `uv run pytest packages/pricing-core/tests/test_rating_decimal_money_rounds_once.py -q`
   passes, and it includes `test_a_mounted_decimal_port_rounds_once_at_the_parent_output`.
6. **A-2's branch is gone.** `git grep -n model_call_money_issues -- packages backend/src`
   prints nothing.

**SL-1517** (PL-1516 items 1–13 stand, as amended by its two deltas, with these):

7. **Item 3b is red first and then green** (§B6), recorded in the ledger by its printed
   failure line.
8. **The fold files change by their call-site arguments only.** For each file of §B1,
   `git diff <base>...HEAD -- <file>` changes only lines that call the four services.
9. **Item 13 holds seven `cmp` codes**, all 0, plus a non-zero positive control that covers
   `R7`.
10. **The contract is unmoved or regenerated.** `uv run python scripts/generate-contracts.py --check`
    exits 0, and no file under `docs/contracts/` is hand-edited.
11. **Order and BOUND.** The ledger records S4's merge commit before this slice's merge, and the
    merge commit's date is on or before 2026-11-04.

**Both:**

12. `python3 scripts/audit-docs.py` exits 0 on the merge tree.

## Hand-off

1. **To the lead:** mint this delta in D11 or D12. The SL-1563 and SL-1517 rows carry a dated
   line pointing here (this PR). The GO records quote §A6 and §B7.
2. **To SL-1563's executor:** Part A, then PL-1562. The three-line edit is DP-7 (i)'s, and
   nothing more of A-2's file moves.
3. **To SL-1517's executor:** Part B, then PL-1516 and its two dated deltas inside it. The edit
   path's action is `rate_table_version.edited`; the spec note is RL 9817's.
4. **To RL 9817's decision-maker:** this delta names the note's place as "the spec text T-1b
   inserted" (§B3), as ruled; the RL's own placement governs.
5. **To WK-675 S4's executor (`SL-1559`):** nothing changes in S4. SL-1517 merges second and
   carries the edit path's event.

## Self-review

1. **Coverage of the 11:45:03 entry.** Item 2: §A1 (the pair moved, the other asserts
   byte-identical, `:607` superseded for those lines, the LG diff) and the SL-1563 row's dated
   line, which cites where DP-1 was ruled (RL-1564 `:152`). Item 3: §B1 names each of the three
   files; DP-6 is ruled and folded (§B3); the timing is §B4. Item 5: one delta covering both
   plans.
2. **Coverage of 11:48:00 (DP-7 (i)).** The bound is `:456–475` with exactly three changed
   lines (§A1, acceptance 1). (ii) is not used.
3. **Coverage of 11:49:51.** Item 1: the action name (§B3, item 3b). Item 2: RL 9817 is
   additive, RL-1515's body is not touched, and the note goes in the spec text T-1b inserted.
   Item 3 (i)–(iii): §B3 1–3 and §B6. Its contract line: §B3, acceptance 10. Item 4: §B3 and
   §B7 5a.
4. **The readiness memo's F2 and F3** are §A2 and §A3. Its SL-1517 needs table is §B7.
5. **Repository literals.** Every `file:line` was read at `d699a561`, and `02f23b4a` changes
   none of those files. S4 was read at `af4f634b`. No test or script was run. The `git grep`
   counts above were run, each with its command.
6. **What was not decided here:** DP-6 and DP-7 were ruled by the maintainer (by delegation);
   the write-set YESes are the lead's. The `:463` relaxed form (`"money_minor"` in the message)
   and the item 15 and 3b test names are this plan's choices, and an executor who finds that one
   does not run as written reports it as a plan defect.
