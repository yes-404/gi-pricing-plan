---
id: LG-9443
family: ledger
title: WK-1250 slice SL-1340 — the sub-graph pin and the inlining (FR-217's pin and inlining limbs; FR-258's inlined steps), PL 9610 slice ledger
status: active
created: 2026-10-09            # working id; the mint date will replace this (check 31)
owner: executor
tree: 61e2a8d9d06087cadd3760e9668b3caff881b85c
phase: P2
work: WK-1250
slice: SL-1340
plans: []
corrected_by: []
relates: [RL-1309, RL-1344, PL-1254, PL-1325, LG-1355, SL-1340, FR-217, FR-258]
---

# LG-9443 (working id) — SL-1340: the sub-graph pin and the inlining

Executed by `executor-sl1340` (sonnet) from **PL 9610** (working id, mints in D5; read at
`origin/pl-9610-wk1250-s2-leaf` `202d67774c409a9981dcced60e2f97d94955643d`) and **RL 9586**
(working id, mints in D5; read at `origin/dm-9586-wk1250-s2` `4f1c8a90fe7e5884031a012975557634a69965a8`).
Neither is on `main`, so neither is in `plans:` or `relates:` (check 32); they are cited here in
working-id form. Branch `sl-1340-wk1250-s2`, worktree `.claude/worktrees/sl-1340`, from
`origin/main` `61e2a8d9d06087cadd3760e9668b3caff881b85c` (#1253). The slice runs under L1 (a'):
one PR, this one ledger, no activation PR.

**GO:** none yet. This is authoring ahead of a GO, at the user's order.
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
at `61e2a8d9`. It is `PL-1254` Task 2. Its leaf plan is PL 9610 (draft, working id).

**Requirement coverage, each id** (PL 9610 §Scope): `03` FR-217 (pin and inlining limbs),
FR-258 (inlined steps), FR-212, FR-216, FR-274, FR-275, FR-276, FR-237; `00` FR-20.

**Not in this slice** (PL 9610): `SubGraphRef.purposes` and the real check (SL-1341); persisting
`structural_diff` (WK-673); G3 (WK-674 Slice 2); any `TraceStep` change (WK-1178); the designer
view (WK-675 S9). `RL-1242`'s interim refusal stays.

**Rulings that bind** (RL 9586, working id, quoting the maintainer's (by delegation) entry
"2026-10-05 16:54:17 BST — CLEANUP NOW … WK-1250 S2 DPs and the DOUBLE-COUNT DP RULED"):
DP-S2-1 (a) re-inline at load, with C1 (`BUNDLE_COMPILE_FAILED` when the graph's node ids and the
re-inlined step ids differ, red first); DP-S2-2 shape (a) (`inputs`, `outputs` dicts), separator
**`__`** (not `/`), `mount_point` `^[A-Za-z][A-Za-z0-9_]*$` with no `__`, renaming by FR-244 token
through a shared `vocabulary._tokenize` helper (`vocabulary.py` joins the write set), codes as
PL 9610's DP row. P1 to P5 of RL 9586 amend PL 9610 and are **not yet applied to the plan text**
(`git grep -c 'mount_point}__'` over the plan at `202d6777` prints 0); where PL 9610 says `/`, the
ruling's `__` is followed, and P5's topological step order (Kahn, list order as tie-break) is the
inliner's order.

**Read-first differences, PL 9610 versus `main` at `61e2a8d9`** (premises re-derived; each named at its site):
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
- [x] Task 1 — spec: `03` §4.1, §4.3, §4.11, §5.2 (T1, T2 verbatim from RL 9586)
- [x] Task 2 — `model-schema`: `Pins.sub_graphs`, the port map, the mount as a node, the two contracts
- [x] Task 3 — `pricing-core/rating/inline.py` and the `vocabulary.py` token helper
- [x] Task 4 — the diff limb (`diff_algorithms`)
- [x] Task 5 — `compile_bundle` and `load_bundle` inline (C1)
- [x] Task 6 — backend: the resolver `sub_graph` branch, G1 objective clause, G2, G4 (c)
- [ ] Task 7 — the trace (FR-258), order (b)
- [ ] Task 8 — `RL-1242` stays, stated
- [ ] Task 9 — the gate (owed after the Task 7 measurement; not run by the authoring seat)

### Gate

Not run. The authoring seat runs small tests only (one file, `nice -n 19`, `/tmp/slots/small-test`).
The full two-half gate waits for the gate slot and the lead's "gate slot granted" for the head.

### Audit

Not yet run.

### Build log

**2026-10-09, Task 0 (partial).** Worktree made from `origin/main` `61e2a8d9`; `ls-remote` of
`pl-9610-wk1250-s2-leaf` (`202d6777…`) and `dm-9586-wk1250-s2` (`4f1c8a90…`) matched the brief.
PL 9610 (734 lines) and RL 9586 (162 lines) read in full. Premises re-derived by symbol at the new
lines listed in Scope.

**2026-10-09, Task 1.** `03` §4.1 (example per RL 9586 T1, invariants note), §4.3 (pins example, FR-20 restated by class with the struck clause kept), §4.11 (Slice note, T2 namespacing bullet verbatim with date 2026-10-09), §5.2 (`compile_bundle` comment, `inline_mounts` line) edited by script (each find string counted 1 first). FR-217/218/258 not reworded. `audit-docs.py` NOT run: waits for the gate slot (brief, small-test rule). `inline_mounts` is the plan's proposed name.

**2026-10-09, Task 2 (model-schema).** `uv sync --all-packages` rc 0 in the worktree.
- **Red** (before any code), `flock -w 300 /tmp/slots/small-test -c "timeout 150 nice -n 19 uv run --directory <wt> pytest -q -p no:cacheprovider packages/model-schema/tests/test_rating_algorithm.py -k 'mount or pins_default or unmapped'"`: the new mount tests failed by the predicted cause: `sub_graphs.0.inputs / .outputs: Extra inputs are not permitted [type=extra_forbidden]` (the port map is refused by `extra="forbid"`), and `AttributeError: 'Pins' object has no attribute 'sub_graphs'`. A first draft of the five `mount_point` pattern cases passed for the wrong cause (the same `extra_forbidden`); they were tightened to `match="mount_point"` and then failed for it. load1 was 3.2 to 3.4 at launch.
- **Green**: `Pins.sub_graphs`; `SubGraphRef.inputs`/`outputs` (default empty so the existing mount tests at `test_rating_algorithm.py:74` and `test_rating_score.py:466` pass unmodified; completeness against the pinned ports is compile's, Task 5); `mount_point` pattern `^[A-Za-z][A-Za-z0-9_]*$` plus a no-`__` validator; `_graph_invariants` counts each mount as a `_MountNode` (id `mount_point`, consumes its inputs, produces its outputs) through the existing helpers, with mount-point uniqueness beside FR-215. The orphan check stays on real steps. `test_rating_algorithm.py`: 21 passed, rc 0 (load1 3.4). `ruff check packages/model-schema`: clean.
- Contracts: `rating-version.schema.json` (`pins.sub_graphs`), `rating-algorithm.schema.json` (`sub_graphs` items: pattern, `inputs`, `outputs`) hand-edited; `generate-contracts.py` regenerated `generated.json` and `rating-version-create.schema.json`; `--check`: "46 generated contracts match the models". `backend/tests/test_contracts.py`: 152 passed, 2 skipped (load1 4.08 at launch, 0.08 over the cap; no database used, the teardown warning is the unset test DB).
- Not run: whole-tree mypy (waits for the gate slot).

**2026-10-09, Task 3 (inliner).**
- **Red**: `test_rating_inline.py` first run at 14:31 (load1 4.12 at launch, 0.12 over the cap; later runs 3.3 to 3.8): collection `ModuleNotFoundError: No module named 'pricing_core.rating.inline'`, rc 2.
- **Green**: `pricing_core/rating/inline.py` (`inline_mounts`, the proposed name, kept) and `vocabulary.py` (`_scan` with spans; `_tokenize` is now a wrapper over it; new `rename_tokens`). `test_rating_inline.py`: 22 passed (rc 0). `test_rating_vocabulary.py`: 58 passed. `ruff check packages`: clean. Two fixture slips seen red and fixed in the tests (short artifact slugs; a parent that cannot be built with no mapped output).
- **Raise-site register**: `test_quote_input_raise_sites.py` went red ("a `_raise_named` site is not accounted for", the five `inline.py` sites) until `_INPUT_FREE` gained five `rating/inline.py` rows with their input-free reasons; then 19 passed. Plan acceptance 10 allows this only for `compile_bundle`'s own count; this is the new-file case, named here.
- **Deviations from PL 9610 Task 3 (read at `202d6777`)**: (1) the separator is `__` and renaming is by token (RL 9586), not `/`; (2) steps are in RL 9586 P5's Kahn order, not "parent then mounts"; (3) `as_at` is renamed as well as RL 9586's seven fields, because `authored.py` `EXPRESSION_FIELDS` lists it as an evaluated string (additive, no unruled choice); (4) the plan's "nested mount: refused" case is not an inliner case, since `fragments` is already `SubGraph`s; it is Task 5's (the payload is validated into `SubGraph`, whose `extra="forbid"` refuses `sub_graphs`).
- **OPEN DP (reported to the lead, not picked)**: a fragment that re-produces one of its own input ports (the in-place clamp that Slice 1's `SubGraphBody` allows) cannot be inlined faithfully, since the port IS the parent's value and the write would reach the parent. `inline_mounts` refuses it with `VALIDATION_FAILED` (test `test_a_fragment_that_re_produces_its_input_port_is_refused`). No ruling covers it; the refusal is the conservative, reversible default.

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

## PRs

- [ ] (no PR yet)
