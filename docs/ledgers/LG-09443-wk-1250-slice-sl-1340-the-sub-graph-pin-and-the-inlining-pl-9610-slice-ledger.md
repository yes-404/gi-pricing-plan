---
id: LG-9443
family: ledger
title: WK-1250 slice SL-1340 — the sub-graph pin and the inlining (FR-217's pin and inlining limbs; FR-258's inlined steps), PL-1572 slice ledger
status: active
created: 2026-10-09            # working id; the mint date will replace this (check 31)
owner: executor
tree: 61e2a8d9d06087cadd3760e9668b3caff881b85c
phase: P2
work: WK-1250
slice: SL-1340
plans: [PL-1572]
corrected_by: []
relates: [RL-1571, PL-1572, RL-1309, RL-1344, PL-1254, PL-1325, LG-1355, SL-1340, FR-217, FR-258]
---

# LG-9443 (working id) — SL-1340: the sub-graph pin and the inlining

Executed by `executor-sl1340` (sonnet) from **PL-1572** (minted 2026-10-10 from working id 9610; drafted at
`origin/pl-9610-wk1250-s2-leaf` `202d67774c409a9981dcced60e2f97d94955643d`) and **RL-1571** (minted from working id 9586;
drafted at `origin/dm-9586-wk1250-s2` `4f1c8a90fe7e5884031a012975557634a69965a8`). Both are on `main` from 2026-10-10 and
are in `plans:` and `relates:`; the working ids 9610 and 9586 survive only in the branch names. Branch `sl-1340-wk1250-s2`, worktree `.claude/worktrees/sl-1340`, from
`origin/main` `61e2a8d9d06087cadd3760e9668b3caff881b85c` (#1253). The slice runs under L1 (a'):
one PR, this one ledger, no activation PR.

**GO:** `to-lead.md` "2026-10-10 08:57:14 BST — DISPATCH GO: SL-1340 (PL-1572), sequenced after A-2" (authoring first; tests and the merge of `main` wait for A-2 and the lead's word).
**MERGE-ACK:** none yet.

## Tasks

### Scope

**Authority for authoring ahead** (`~/gi-pricing-plan.local/channel/to-lead.md`, local, not in the
repository), headers verbatim: "2026-10-09 15:22:26 BST — USER: 'worrying only one executor runs'. FILL THE VM NOW …";
"2026-10-09 15:18:13 BST — USER: WORK OVERNIGHT TONIGHT …";
"2026-10-09 13:29:49 BST — RULINGS …" (item 2, merge order S3 → S4 → A-1 → FD-1374; item 3, an L1 (a') slice
whose plan is draft sets it active in its first commit and closes its LG and SL at the head).
The brief is `handover/brief-executor-authoring-trio-2026-10-09.md` (local), Section B.

**Work-plan row.** `SL-1340 — Slice 2: the pin and the inlining (FR-217's pin and inlining limbs;
FR-258's inlined steps)`, `docs/roadmap.md` `#### SL-1340` under `### WK-1250`, `status: draft`
at `61e2a8d9`. It is `PL-1254` Task 2. Its leaf plan is PL-1572 (draft, working id).

**Requirement coverage, each id** (PL-1572 §Scope): `03` FR-217 (pin and inlining limbs),
FR-258 (inlined steps), FR-212, FR-216, FR-274, FR-275, FR-276, FR-237; `00` FR-20.

**Not in this slice** (PL-1572): `SubGraphRef.purposes` and the real check (SL-1341); persisting
`structural_diff` (WK-673); G3 (WK-674 Slice 2); any `TraceStep` change (WK-1178); the designer
view (WK-675 S9). `RL-1242`'s interim refusal stays.

**Rulings that bind** (RL-1571, working id, quoting the maintainer's (by delegation) entry
"2026-10-05 16:54:17 BST — CLEANUP NOW … WK-1250 S2 DPs and the DOUBLE-COUNT DP RULED"):
DP-S2-1 (a) re-inline at load, with C1 (`BUNDLE_COMPILE_FAILED` when the graph's node ids and the
re-inlined step ids differ, red first); DP-S2-2 shape (a) (`inputs`, `outputs` dicts), separator
**`__`** (not `/`), `mount_point` `^[A-Za-z][A-Za-z0-9_]*$` with no `__`, renaming by FR-244 token
through a shared `vocabulary._tokenize` helper (`vocabulary.py` joins the write set), codes as
PL-1572's DP row. P1 to P5 of RL-1571 amend PL-1572 and are **not yet applied to the plan text**
(`git grep -c 'mount_point}__'` over the plan at `202d6777` prints 0); where PL-1572 says `/`, the
ruling's `__` is followed, and P5's topological step order (Kahn, list order as tie-break) is the
inliner's order.

**Read-first differences, PL-1572 versus `main` at `61e2a8d9`** (premises re-derived; each named at its site):
- Line numbers moved: `compile_bundle` is now `compile.py:694`, `_MATURITY_CHECK_EXEMPT` `:472`,
  `_compatible` `:126`, `output_type_issues` `:134`, `to_jdm` `:521`, `bundle_hash` `:566`,
  `check_step_refs_pinned` `:586`; `load_bundle` `runtime.py:698`; `to_wire` `runtime.py:481`;
  `Pins` `rating.py:65`, `SubGraphRef` `:390`, `AlgorithmDiff` `:608`, `diff_algorithms` `:638`.
- **PL 9649 has merged as SL-1472 (#1247)**: the transitive check is `_refuse_unapproved_objectives`
  (`compile.py:617`), not `_check_reachable_objectives`. Task 5 step 3.5 and acceptance 9's
  `git grep -c 'def _check_reachable_objectives'` use the merged name.
- `RatingAlgorithm` now derives from `RatingAlgorithmDraft` (`rating.py:423`, `:451`; PL 9713's move
  has landed), so the port-map and invariants edits map to those names.
- **Not yet met on `main`**: no `structural_diff` in `backend/src` (acceptance 7's second test does
  not run); no `_check_declared_reads` in `pricing_core/rating` (PL 9776/PL-1520 not delivered, so
  Task 7 runs order (b)); no plan or ledger on `main` cites `RL-1309` DP-1 item 3 apart from PL-1325
  and LG-1355 (activation need 4's in-repo carrier is unmet; Task 4 and acceptance 7 here carry it
  for `PL-1254` Task 2); `to_wire` wires by dependency order only if SL-1436 (PL-1435, FD-1425) has
  merged. All five recorded for Task 0.

### Task list

- [ ] Task 0 — preconditions and premises a–n at `61e2a8d9` (this entry: partial; pending items listed in Scope)
- [x] Task 1 — spec: `03` §4.1, §4.3, §4.11, §5.2 (T1, T2 verbatim from RL-1571)
- [x] Task 2 — `model-schema`: `Pins.sub_graphs`, the port map, the mount as a node, the two contracts
- [x] Task 3 — `pricing-core/rating/inline.py` and the `vocabulary.py` token helper
- [x] Task 4 — the diff limb (`diff_algorithms`)
- [x] Task 5 — `compile_bundle` and `load_bundle` inline (C1)
- [x] Task 6 — backend: the resolver `sub_graph` branch, G1 objective clause, G2, G4 (c)
- [x] Task 7 — the trace (FR-258), order (b)
- [x] Task 8 — `RL-1242` stays, stated
- [ ] Task 9 — the gate (owed after the Task 7 measurement; not run by the authoring seat)

### Gate

Not run. The authoring seat runs small tests only (one file, `nice -n 19`, `/tmp/slots/small-test`).
The full two-half gate waits for the gate slot and the lead's "gate slot granted" for the head.

### Audit

Not yet run.

### Build log

**2026-10-09, Task 0 (partial).** Worktree made from `origin/main` `61e2a8d9`; `ls-remote` of
`pl-9610-wk1250-s2-leaf` (`202d6777…`) and `dm-9586-wk1250-s2` (`4f1c8a90…`) matched the brief.
PL-1572 (734 lines) and RL-1571 (162 lines) read in full. Premises re-derived by symbol at the new
lines listed in Scope.

**2026-10-09, Task 1.** `03` §4.1 (example per RL-1571 T1, invariants note), §4.3 (pins example, FR-20 restated by class with the struck clause kept), §4.11 (Slice note, T2 namespacing bullet verbatim with date 2026-10-09), §5.2 (`compile_bundle` comment, `inline_mounts` line) edited by script (each find string counted 1 first). FR-217/218/258 not reworded. `audit-docs.py` NOT run: waits for the gate slot (brief, small-test rule). `inline_mounts` is the plan's proposed name.

**2026-10-09, Task 2 (model-schema).** `uv sync --all-packages` rc 0 in the worktree.
- **Red** (before any code), `flock -w 300 /tmp/slots/small-test -c "timeout 150 nice -n 19 uv run --directory <wt> pytest -q -p no:cacheprovider packages/model-schema/tests/test_rating_algorithm.py -k 'mount or pins_default or unmapped'"`: the new mount tests failed by the predicted cause: `sub_graphs.0.inputs / .outputs: Extra inputs are not permitted [type=extra_forbidden]` (the port map is refused by `extra="forbid"`), and `AttributeError: 'Pins' object has no attribute 'sub_graphs'`. A first draft of the five `mount_point` pattern cases passed for the wrong cause (the same `extra_forbidden`); they were tightened to `match="mount_point"` and then failed for it. load1 was 3.2 to 3.4 at launch.
- **Green**: `Pins.sub_graphs`; `SubGraphRef.inputs`/`outputs` (default empty so the existing mount tests at `test_rating_algorithm.py:74` and `test_rating_score.py:466` pass unmodified; completeness against the pinned ports is compile's, Task 5); `mount_point` pattern `^[A-Za-z][A-Za-z0-9_]*$` plus a no-`__` validator; `_graph_invariants` counts each mount as a `_MountNode` (id `mount_point`, consumes its inputs, produces its outputs) through the existing helpers, with mount-point uniqueness beside FR-215. The orphan check stays on real steps. `test_rating_algorithm.py`: 21 passed, rc 0 (load1 3.4). `ruff check packages/model-schema`: clean.
- Contracts: `rating-version.schema.json` (`pins.sub_graphs`), `rating-algorithm.schema.json` (`sub_graphs` items: pattern, `inputs`, `outputs`) hand-edited; `generate-contracts.py` regenerated `generated.json` and `rating-version-create.schema.json`; `--check`: "46 generated contracts match the models". `backend/tests/test_contracts.py`: 152 passed, 2 skipped (load1 4.08 at launch, 0.08 over the cap; no database used, the teardown warning is the unset test DB).
- Not run: whole-tree mypy (waits for the gate slot).

**2026-10-09, Task 3 (inliner).**
- **Red**: `test_rating_inline.py` first run at 14:31 (load1 4.12 at launch, 0.12 over the cap; later runs 3.3 to 3.8): collection `ModuleNotFoundError: No module named 'pricing_core.rating.inline'`, rc 2.
- **Green**: `pricing_core/rating/inline.py` (`inline_mounts`, the proposed name, kept) and `vocabulary.py` (`_scan` with spans; `_tokenize` is now a wrapper over it; new `rename_tokens`). `test_rating_inline.py`: 22 passed (rc 0). `test_rating_vocabulary.py`: 58 passed. `ruff check packages`: clean. Two fixture slips seen red and fixed in the tests (short artifact slugs; a parent that cannot be built with no mapped output).
- **Raise-site register**: `test_quote_input_raise_sites.py` went red ("a `_raise_named` site is not accounted for", the five `inline.py` sites) until `_INPUT_FREE` gained five `rating/inline.py` rows with their input-free reasons; then 19 passed. Plan acceptance 10 allows this only for `compile_bundle`'s own count; this is the new-file case, named here.
- **Deviations from PL-1572 Task 3 (read at `202d6777`)**: (1) the separator is `__` and renaming is by token (RL-1571), not `/`; (2) steps are in RL-1571 P5's Kahn order, not "parent then mounts"; (3) `as_at` is renamed as well as RL-1571's seven fields, because `authored.py` `EXPRESSION_FIELDS` lists it as an evaluated string (additive, no unruled choice); (4) the plan's "nested mount: refused" case is not an inliner case, since `fragments` is already `SubGraph`s; it is Task 5's (the payload is validated into `SubGraph`, whose `extra="forbid"` refuses `sub_graphs`).
- **DP RULED** (see the 15:35:45 entry in the Build log below; the text that follows is the question as first raised): a fragment that re-produces one of its own input ports (the in-place clamp that Slice 1's `SubGraphBody` allows) cannot be inlined faithfully, since the port IS the parent's value and the write would reach the parent. `inline_mounts` refuses it with `VALIDATION_FAILED` (test `test_a_fragment_that_re_produces_its_input_port_is_refused`). No ruling covers it; the refusal is the conservative, reversible default.

**2026-10-09, Task 4 (diff limb).**
- **Red** (`test_rating_algorithm.py -k diff_names`, load1 4.20 at launch; from here a `/proc/loadavg` wait loop holds each run to load1 <= 4.0): `TypeError: diff_algorithms() got an unexpected keyword argument 'fragments'` and `AttributeError: 'AlgorithmDiff' object has no attribute 'sub_graph_mounts'` (3 failed, by the predicted cause).
- **Green**: `AlgorithmSubGraphChange` (`mount_point`, `before`, `after`, `ports_changed`, `steps`) and `AlgorithmDiff.sub_graph_mounts`; `diff_algorithms(old, new, *, fragments=None)`. The step walk was extracted unchanged into `_diff_steps` and the inner fragment diff calls the same helper (no second walk); the fragment is read through a `_FragmentLike` protocol because `sub_graphs.py` imports `rating.py`. One test fixed after a red of its own (the base fixture already mounts `ncd-ladder@4`). `test_rating_algorithm.py`: 24 passed (existing diff tests unmodified). `generate-contracts.py --check`: 46 match (the diff shape is not a generated contract). `ruff check packages`: clean.
- **Broken-input proof** (local edit, restored from a saved copy, never committed): `sub_graph_mounts=[]` in `diff_algorithms` made the limb tests fail (`assert 0 == 1`, `assert [] == ['sub_graph:ncd-ladder@5']`).
- **Acceptance 7's second test** (the persisted `structural_diff`): not run, WK-673's persistence has not merged at `61e2a8d9` (`grep -rln structural_diff backend/src` prints nothing). The limb is therefore carried in this slice by the unit tests; WK-673 owns the re-point case.

**2026-10-09, Task 5 (`compile_bundle` and `load_bundle` inline).**
- **Red (compile)**, `test_rating_compile_bundle.py` appended cases, before any compile code: 15 failed, by the predicted cause (premise c): the mount was silently not inlined (`assert 'm_ncd__s_ladder' in {...parent nodes...}`), every G1/port/type/DP-4/DP-S1-4 case `Failed: DID NOT RAISE ValueError`, and the no-sub-graph hash test `sha256:370a6c… == sha256:a41bf2…` (the new empty `sub_graphs` key changed every bundle's hash).
- **Red (load)**: with `runtime.py` restored to `HEAD` for the run (copy kept, put back; `cmp` equal): `test_a_mounted_fragment_is_scored_into_the_mapped_parent_name_in_isolation` `assert 'm_ncd__s_a' in {'s_in_base', ...}` and `test_c1_a_bundle_whose_graph_and_reinlined_algorithm_disagree_is_refused` `DID NOT RAISE ValueError`.
- **Green**: `inline.mounted_fragments` (type, G1 pin, payload to `SubGraph`; a payload with `sub_graphs` is refused here, DP-4); `compile_bundle` resolves each pinned mount once, inlines, runs `_refuse_mount_port_type_mismatch` (`producer_types` and `_compatible`, no second table), then every existing check over the INLINED algorithm; `*pins.sub_graphs` joins `all_refs` and reuses the mount resolutions; `sub_graph` joins `_MATURITY_CHECK_EXEMPT`; `bundle_hash` drops an empty `sub_graphs` so a version that pins none hashes as before (acceptance 5; independently recomputed by the pre-Slice-2 formula in a test); `load_bundle` re-inlines from `resolved_payloads` and applies C1 (`BUNDLE_COMPILE_FAILED`). `compile_bundle`'s own raise count stays 5. `test_rating_compile_bundle.py` 29, `test_rating_inline.py` 23, `test_rating_runtime.py` 14, `test_rating_compile.py` 45, `test_rating_score.py` 40, `test_rating_authored_fields.py` 40, `test_rating_committed_strings.py` 4, `test_quote_input_raise_sites.py` 19: all passed, no existing test edited.
- **Broken-input proofs**, local edits restored by copy and `cmp` or by the reverse `sed`, never committed: dropping `*pins.sub_graphs` from `all_refs` reds the bundle-carries-the-fragment and G4 tests; `bundle_hash` ignoring `sub_graphs` reds `test_the_hash_covers_the_pinned_fragment`; treating every mount as pinned reds both G1 tests. The G4 (b) exemption proof is the in-test `monkeypatch` of `_MATURITY_CHECK_EXEMPT` (`PIN_NOT_APPROVED`).
- **Findings in flight**: (1) the first inliner refused a text outside FR-244's allow-list itself, which pre-empted the save-time checks' own codes (`now()` gave `VALIDATION_FAILED`, not `EXPRESSION_NON_DETERMINISTIC`); seen red and fixed: `rename_tokens` now returns such a text unchanged and the checks over the inlined algorithm name it. (2) A helper first named `_check_*` was caught by `test_rating_authored_fields.py` (its `_check_` prefix means a registered save-time check); renamed `_refuse_mount_port_type_mismatch`, as the other compile-time helpers are named.
- Not run: whole-tree mypy and `lint-imports` (gate slot).

**2026-10-09, Task 6 (backend and the guards).**
- **Resolver**: `_Resolver.resolve` has a `sub_graph` branch before the `NOT_FOUND` fall-through; it calls Slice 1's `sub_graphs.resolve_ref` and returns `ResolvedArtifact(status="no_maturity_concept", ...)`, the rate-table sentinel and reason (RL-856); `_MATURITY_CHECK_EXEMPT` (Task 5) is what admits it. `ruff check backend`: clean.
- **G1 objective clause** (pricing-core, no database): `test_rating_compile_fr240.py` gained `test_g1_an_unapproved_objective_planted_in_a_pinned_sub_graph_is_refused` (3 statuses) and its approved control. The refusal is the merged `_refuse_unapproved_objectives` (`compile.py`, SL-1472), **called, not copied**: `git grep -c 'def _refuse_unapproved_objectives' -- packages/pricing-core/src` prints 1 (`compile.py:1`). Broken-input proof: with the `await _refuse_unapproved_objectives(...)` call replaced by `pass` locally (restored by copy and `cmp`, never committed), the planted objective compiled and the tests failed `DID NOT RAISE ValueError`. 15 passed with the call.
- **G2 enumeration** at `61e2a8d9`, `git grep -nE '\.pins\s*=[^=]|pins=' -- backend/src`: `backend/src/app/api/models.py:1204` (`pins=body.pins`, the create route forwarding), `backend/src/app/platform/rating_versions.py:117` (`pins=Pins.model_validate(row.pins)`, a READ in `to_schema`) and `:283` (`pins=pins.model_dump(mode="json")`, the WRITE in `create_rating_version`, which inserts a new `draft` row). No path reaches an existing row, so no refusal is added; none exists to test red. The tripwire `test_g2_every_pin_write_path_is_enumerated` (backend, no database) fails on a new writer: proof with a comment line `x.pins = 1` appended to `rating_versions.py` locally: `{'app/platform/rating_versions.py': 3} != {...: 2}` (restored, never committed). PL 9683 (FD 9708), which adds `algorithm_ref`/`pins` writers to the create path, has not merged at this tree; whoever merges second re-runs the enumeration (plan Task 0).
- **G4 (c)**: `test_sub_graph_version_row_has_no_status_column` (backend, no database), in the form of `test_rate_table_version_row_has_no_status_column`; like its siblings it passes at birth. The two sync tripwires ran: `-k 'no_status_column or g2_every'` 4 passed (3 tripwires and the enumerator).
- **NOT RUN, owed after Task 7 (needs Postgres, so outside the small-test rule)**: `test_a_version_mounting_a_stored_sub_graph_compiles_over_http` and `test_a_mount_whose_sub_graph_is_not_pinned_fails_the_compile_job` (acceptance 11), authored by mirroring `test_a_pinned_version_compiles_over_http`'s helpers. They have never run: expect to correct fixtures at the first database run.

**2026-10-09, Tasks 7 and 8 (the trace; `RL-1242` stays).** PL 9776 (PL-1520, the `TraceStep` ruling's delivery) has not merged at `61e2a8d9` (`grep -rn _check_declared_reads packages/pricing-core/src` prints nothing), so order (b) runs: tests only, `TraceStep` and `_build_trace` not edited.
- **Trace test** `test_the_trace_shows_each_inlined_step_attributed_to_its_mount_point` (`test_rating_score.py`, appended): `score_one(trace=True)` on the score fixture with an NCD mount returns a `TraceStep` per inlined step, ids `m_ncd__s_ladder` and `m_ncd__s_cap`, ordered before `s_office`; the premium is the unmounted golden 1_507 (the fragment yields 1); tracing does not change the result. **Red** (premise h confirmed), with `runtime.py` swapped for the Task 4 commit `7ea29503`'s copy for the run and put back by copy and `cmp`: `assert {'m_ncd__s_cap', 'm_ncd__s_ladder'} <= {'s_clamp', ..., 's_office', ...}`, "Extra items in the left set: 'm_ncd__s_cap' 'm_ncd__s_ladder'" (the inlined nodes dropped, as `_build_trace` reads `algorithm.steps`). **Green** with Task 5's `load_bundle`: 1 passed.
- **Plan premise that does not hold**: PL-1572 Task 7 asks for "a batch trace test [that] mirrors the existing one". There is no batch trace: `score_batch` takes no `trace` argument and `grep trace` over its body prints nothing, and no batch trace test exists. None is written; FR-258's "same structure in real-time and batch" has no batch trace to compare at this tree. Reported to the lead.
- **Task 8**: the existing FR-218 interim tests (`test_rating_score.py`, the `test_a_purpose_needing_a_sub_graph...` family) pass unmodified. Appended: `test_a_version_that_mounts_a_sub_graph_still_refuses_mta_and_cancellation` (both purposes, `INPUT_CONTRACT_VIOLATION`, "interim"; it holds because `CompiledBundle.algorithm` is the inlined algorithm, whose `sub_graphs` is empty) and `test_an_unconditional_mount_prices_a_new_business_quote_with_the_fragment` (`new_business` and `renewal`: factor 1 gives 1_507, factor 2 gives more). They pass at birth (Task 5 is in the tree); Slice 3 changes the first on purpose. `test_rating_score.py`: 45 passed (40 existing, unmodified, plus 5 new). `ruff check packages`: clean.

**2026-10-09, rulings after the final report, and the resolver's landing place.**
- **Self-port refusal RULED** by the lead's adoption in `to-lead.md`, header verbatim: "2026-10-09 15:35:45 BST — RULINGS on the lead's 15:35:22 (SL-1340): (1) (a), REFUSE with VALIDATION_FAILED, plus a one-line spec statement; (2) YES, added rows only". Item 1: `inline_mounts` refuses a fragment that re-produces its own input port with `VALIDATION_FAILED`, no new `RATING_ERROR_CODES` entry; one line in `03` §4.11's inlining bullet ("A mount whose fragment writes its own input port is refused (`VALIDATION_FAILED`); revisit if an algorithm needs it", ruled 2026-10-09), in the same commit as this entry; one refusal test (parent value asserted untouched) and one positive control (`test_a_fragment_that_only_reads_its_input_port_still_inlines`). The refusal code was already in `6247dbef`; `test_rating_inline.py`: 24 passed (both tests red-green history: the refusal test was red-before-code at Task 3, `ModuleNotFoundError`).
- **Write set, item 2 of the same entry:** `packages/pricing-core/tests/test_quote_input_raise_sites.py` joins PL-1572's write set for ADDED rows only. At this head the rows added there are the five `inline.py` rows, `mounted_fragments`, `_refuse_mount_port_type_mismatch` and `_check_graph_matches_inlined_algorithm`; the removed row (`_rename_text`) was added and removed inside this branch, so `git diff -U0 origin/main...HEAD -- <that file>` shows no removed or changed line of main's. (To be re-checked at the ACK.)
- **Resolver landing place** (lead's Task 6 instruction): S4's `c31a2bfd` lifts the nested `_Resolver` to module-level `WorkspaceResolver(session, workspace_id, blob_store)` (`resolve` binds `session, workspace_id, blob_store` as locals), and A-1 (`origin/sl-1462-a1-peril-approval`) adds a `peril_structure` branch just before the final `NOT_FOUND` raise, plus an import line. My hunk is therefore: (1) one import `from app.platform import sub_graphs as sub_graphs_service` beside the other `app.platform` imports, (2) the free function `_resolve_sub_graph_pin(session, workspace_id, ref)` above `compile_rating_version`, and (3) a two-line branch `if ref.type == "sub_graph": return await _resolve_sub_graph_pin(session, workspace_id, ref)` directly after the `rating_algorithm` branch of `WorkspaceResolver.resolve` (8-space indent there, 12 here), clear of A-1's end-of-method hunk. Neither branch was fetched into this tree.

## Plan deltas, dated 2026-10-10 (the lead's GO, `to-lead.md` "2026-10-10 08:57:14 BST — DISPATCH GO: SL-1340 (PL-1572) …", decisions 1 to 4)

PL-1572 is frozen from its merge; these are this ledger's deltas against it, not edits to it.

1. **Write-set additions (decision 1: YES), each by file:line at this branch's head before the merge of `main`:**
   - `packages/pricing-core/tests/test_rating_compile_fr240.py`: the appended G1-objective tests, `PLANTED` at line 207 (shifted by the second import line below), `_planted_in_a_sub_graph` and the two `test_g1_…` tests, plus the `RatingVersion` import at line 31.
   - `packages/model-schema/src/model_schema/__init__.py:282` (the import of `AlgorithmSubGraphChange`) and `:445` (its `__all__` entry): two added exports.
   - `backend/src/app/platform/sub_graphs.py:205-206`: the `resolve_ref` docstring, whose "Not wired into compile (Slice 2)" is no longer true.
2. **Acceptance 10 holds as written (decision 2: YES).** `test_rating_compile_fr240.py` keeps its original line `from test_rating_compile_bundle import FakeResolver, _resolver, _version` unchanged (line 14); a SECOND import line (`NCD`, `_fragment_payload`, `_mounted_resolver`, `_mounted_version`) follows it under a `# isort: split` comment, because without the split ruff's `I001` merges the two into one rewritten line. `git diff 61e2a8d9 -- packages/pricing-core/tests/test_rating_compile_fr240.py` shows the original line as context, not as a change.
3. **Task 7's batch-trace item is dropped (decision 3: (a)).** `score_batch` takes no `trace` argument at `main`, so the item cannot be met in this slice's write set; the single-quote trace test `test_the_trace_shows_each_inlined_step_attributed_to_its_mount_point` stays. **The condition (does any FR require a trace for BATCH scoring?):** YES, one clause does.
   - `docs/specs/03-rating-engine.md:177`, FR-258: "Traces are the same structure in real-time and batch."
   - `docs/specs/03-rating-engine.md:178`, FR-259's RL-890 clarification: "A batch run may still produce traces on request under FR-258, and they are written with that Job's own output and never returned by the production traces route."
   - Against it, `docs/specs/03-rating-engine.md:735-737` (the batch output contract) says `trace` is excluded from the batch result ("batch requests no engine trace … so this is always absent"). The three passages do not agree: FR-258 and FR-259 allow a batch trace on request, §735 says none is requested. Batch trace is therefore **unevidenced** at this tree. The lead is told, and one OQ row (owner WK-1250) is for the lead to file, for a §13 verdict at WK-1250's close.
4. **S5's `diff_algorithms` call is not edited (decision 4: YES).** `RL-1309` holds as written. The OQ (owner WK-673: should the persisted structural diff carry fragment inner steps via `fragments=`?) rides the lead's next docs batch; this slice files nothing for it.
5. **Acceptance 7's second test is owed at the merged tree.** At `61e2a8d9` WK-673's persistence had not merged; after the merge of `main` it is written against what the persisted evidence carries (the `sub_graph_mounts`, not the inner steps), per the GO.

## PRs

- [ ] (no PR yet)
