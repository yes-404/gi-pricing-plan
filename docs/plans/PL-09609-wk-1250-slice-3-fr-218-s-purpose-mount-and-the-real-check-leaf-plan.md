---
id: PL-9609
family: plan
kind: leaf
title: WK-1250 Slice 3 — FR-218's purpose mount and the real check (retires RL-1242): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: planner
tree: cdaaa57345cb765f96034ce1ec2733c338f1c3cd
phase: P2
work: WK-1250
slice: SL-1341
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1254, PL-1325, RL-1344, RL-1309, RL-1242, FD-1241, RL-1263, PL-1371]
---

# PL 9609 (working id) — WK-1250 Slice 3: FR-218's purpose mount and the real check, leaf plan

Filed under working id 9609. It is the leaf plan for `SL-1341` (`draft`, minted 2026-09-30, in
[`../roadmap.md`](../roadmap.md) under `### WK-1250`), which is `PL-1254` Task 3. The lead
re-issued the id (`~/gi-pricing-plan.local/handover/eta.md`, row "PL 9609", "RE-ISSUED: WK-1250
S3 leaf plan on SL-1341", 5 Oct 15:34:40). The row is not edited here; its "leaf plan" note is
added at the mint. It builds on Slice 2's leaf plan, **PL 9610** (working id, draft #1170).
Everything below was read at `origin/main` `cdaaa57345cb765f96034ce1ec2733c338f1c3cd` on
2026-10-05, unless a line names a branch. **No test was run at planning time.**

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`;
> - `spec-change` (Task 1: FR-218's strike);
> - `contract-schema` and `contract-guard` (Task 2);
> - `python-package`;
> - `python-test`;
> - `dev-commands`;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

Price a `mid_term_adjustment` or `cancellation` quote with the **same** Rating Algorithm for the
risk price, plus a separately versioned sub-graph mounted only for that purpose (FR-218, `03:87`):
- `SubGraphRef` gains `RL-1344`'s optional `purposes` selector;
- FR-212 holds for each purpose's graph;
- the bundle carries what each purpose evaluates, and its hash covers it;
- `_check_purpose_mount` (`score.py:395-422`) becomes the **real check**: refuse unless the
  bundle inlines a mount for this purpose.

The slice then strikes `RL-1242`'s interim clause in FR-218.

**G2.** No step of PL 9629 (working id, #1164) needs this slice: that plan has no MTA,
cancellation or `purpose` step. `PL-1371:218` places this slice on lane B after Slice 2, in the week
of 24–30 Oct (`PL-1371:305`). It is not on G2's critical path (`to-lead.md` entry headed
"2026-10-05 15:37:35 BST", the WK-1250 line).

## Status

The status is the `status:` field in the header, and nothing else. **It stays `draft` while
DP-S3-1 and DP-S3-2 below are open.** `RL-1344` §3 requires them to be *"raised as a decision
point in its leaf plan before the slice starts"* (`RL-1344:180-181`). They are the
decision-maker's.

**Activation needs, in order** (each with its state at `cdaaa573`):
1. **Slice 2 (`SL-1340`) closed.** `PL-1254:331`: *"Depends on: Slice 2."* Open: PL 9610 is
   `draft`.
2. **DP-S3-1 and DP-S3-2 ruled by an `RL-`.** Open.
3. **The dispatch record carries `RL-1344` §2, §3 and §4's Slice 3 bullet**, and the ruling on
   §3's open question (`RL-1344:180-181`).
4. **The `score.py` and `runtime.py` writers in flight have merged, or the dispatch record names
   the definitions.** At this tree, open plans edit:
   - `score_one` and `_score_context_sync`: the FD 9707 fix (PL 9688, #1145, at `2f3269c8`),
     which adds one call in each;
   - `_build_trace` and `build_scoring_result`: PL 9776 (#1051, at `ecbb82ab`);
   - `load_bundle` and `CompiledBundle`: PL 9776 and Slice 2.

   `RL-1263:89` names `score.py` as a shared file.
5. **A free build slot and the single gate** (RL 9620, working id, #1162). Slice 2 and this slice
   never run together: this slice depends on Slice 2 (RL 9620 (b)).
6. **The lead's dispatch.**

### Dependencies

- **On Slice 2 (PL 9610).** This slice consumes these, by their names at Slice 2's merge (the
  ledger records any rename):
  - `SubGraphRef`'s port map;
  - `inline_mounts`, and the fact that a mount is inlined as one namespaced unit, so it can be
    gated as one unit (`RL-1344:177-179`);
  - `Pins.sub_graphs` and G1;
  - the diff limb;
  - DP-S2-1's answer on where the inlined algorithm lives.
- **No other WK-1250 or WK-674 dependency.** WK-675 S9 (the designer's sub-graph mounting) comes
  after this slice (`PL-1371:387-388`). It is not a dependency of this slice.

### File contention (`RL-1263` option (c), as amended by RL 9620)

| This slice's path | What it does there | Also changed by (in flight at `cdaaa573`) | Under option (c) |
|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/score.py` | `_check_purpose_mount` (`:395-422`) rewritten; its two calls (`:898`, `:1063`) take the bundle; the purpose's decision chosen in `score_one` (`:876`) and `_score_context_sync` | PL 9688 (`score_one`, `_score_context_sync`); PL 9776 (`_build_trace`, `build_scoring_result`) | **Serialises with PL 9688**: the same functions. With PL 9776 they are different definitions, so the dispatch record names them |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | `CompiledBundle` and `load_bundle`: one decision per purpose graph (DP-S3-2) | PL 9776 (`CompiledBundle`, `load_bundle`); PL 9688 (`_decision_table_node`) | **Serialises with PL 9776** |
| `packages/pricing-core/src/pricing_core/rating/compile.py` | `Bundle` (`:505`), `compile_bundle`, `bundle_hash` (`:522-535`) | every `compile_bundle` writer (`PL-1371:291-294`) | **Serialised outright** |
| `packages/pricing-core/src/pricing_core/rating/inline.py` | `inline_mounts` gains a `purpose` argument | Slice 2 only | Not concurrent (RL 9620 (b)) |
| `packages/model-schema/src/model_schema/rating.py` | `SubGraphRef.purposes`; `_graph_invariants` per purpose | PL 9689 (`AlgorithmDiff`), PL 9713 (`RatingAlgorithm`) | **Serialises** where the same class is edited |
| `docs/specs/03-rating-engine.md` FR-218 (`:87`), §4.1, §4.11 | Task 1 | any slice editing those | **Serialises** (`RL-1263:89`) |
| `docs/contracts/schemas/rating-algorithm.schema.json` | `purposes` on the mount | PL 9713, if it edits it | **Not exempt** (`RL-1263:113`) |
| `packages/pricing-core/tests/test_rating_score.py` `:438-507` | the interim tests rewritten (`PL-1254:328-330`) | any slice appending there | **An existing-test edit**, deliberate and named; nothing else in the file is edited |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` `:63` | the count, only if it changes | — | — |

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means the
failing run is quoted in the ledger, with its failing assert line and the cause the step
predicts. A failure for any other cause is a plan defect, reported and not worked around. Every new
test carries `@pytest.mark.req("FR-218")`, and also `FR-217` where it inlines.

1. **Spec** (Task 1).
   - FR-218's `RL-1242` interim clause is struck, dated, in `03:87`, citing this slice (`RL-1242:83-85`:
     *"It retires the interim rule in the same commit, with a dated strike"*).
   - `03` §4.1 shows `purposes` on a mount, and states FR-212 per purpose graph (`RL-1344` §3).
   - `03` §4.11's note says the purpose mount landed. The bundle text in §4 and §5.2 says what the
     bundle carries per purpose (DP-S3-2).
   - FR-217 and FR-258 are not reworded, and FR-218's own text is not reworded beyond the strike.
   - `python3 scripts/audit-docs.py` exits 0.
2. **The selector** (`RL-1344` acceptance 1; §2). Red first, one test per form:
   `purposes: ["renewal"]`, `["what_if"]`, `["new_business"]`, `[]` and
   `["cancellation", "cancellation"]` are each refused at save with `VALIDATION_FAILED`.
   `["mid_term_adjustment"]`, `["cancellation"]` and both together are accepted, and an absent
   selector keeps every existing mount's meaning.
3. **FR-212 per purpose** (`RL-1344` §3; acceptance 4). Red first: an algorithm in which a step
   that runs for every purpose consumes a name only a purpose mount produces is refused at save,
   naming the step and the purpose, with the code DP-S3-1's ruling names.
4. **The real check** (`RL-1344` acceptance 2; `RL-1242:83-85`). Red first, through `pricing-core`
   (`score_one` and the batch path) and through `POST /api/v1/score` and
   `POST /api/v1/score/compare`:
   - a version whose only purpose mount selects `cancellation` refuses a `mid_term_adjustment`
     quote with `INPUT_CONTRACT_VIOLATION`, and the message says no mount for this purpose is
     inlined, not "interim";
   - the same version prices a `cancellation` quote with the mount;
   - it prices a `new_business` quote **exactly** as the same version with that mount removed:
     the same `payable_premium_minor`, the same ladder, and the same trace step ids.
5. **Not bypassable** (`PL-1254` Task 3's gate outline). A version that inlines a sub-graph for
   one purpose does not price the other: the cancellation-only mount's steps are absent from an
   MTA evaluation, and the quote is refused by step 4's check. With the check removed locally, a
   test fails. That edit is never committed.
6. **G1, unchanged** (`RL-1344` acceptance 3): a purpose mount whose version is not in
   `Pins.sub_graphs` is refused at compile with `RATING_VERSION_UNPINNED`. This is Slice 2's G1
   test, re-run with a selector on the mount.
7. **Diff and hash** (`RL-1344` acceptance 5): a change to a mount's `purposes` alone appears in
   `diff_algorithms` as a mount change (Slice 2's limb), and changes the bundle's
   `content_hash`. **A version with no purpose mount keeps the hash it had at Slice 2** (the
   existing hash tests pass unmodified).
8. **The interim tests rewritten** (`PL-1254:328-330`). The tests at
   `test_rating_score.py:438-507` are rewritten to the new rule:
   - "no purpose sub-graph → refused" and "other purposes unaffected" stay, re-pointed to the real
     check;
   - the bogus-reference test (`:465-474`, helper `_compiled_with_bogus_sub_graph` `:453-462`)
     is deleted, because Slice 2's G1 compile refusal now covers that case. The ledger names the
     Slice 2 test that does;
   - `test_the_purpose_guard_would_be_caught_if_removed` (`:495-506`) stays, re-pointed.

   The raise-site count `("rating/score.py", "_check_purpose_mount"): 1`
   (`test_quote_input_raise_sites.py:63`) is unchanged, or the ledger says why it moved.
9. **`RL-1242` retired.** The strike (acceptance 1) is in the slice's final commit, as
   `RL-1242:83-85` requires. `RL-1242`'s `status:` goes `active → retired`, in the same commit.
   That status change is the decision-maker's (`document-ids.md` §1.6, RL row: *"`retired` when
   overridden with no successor"*), so the dispatch record names who writes it. **`RL-1242`'s
   body is frozen and takes no note** (`document-ids.md` §1.5). `PL-1254:316-319`'s *"`RL-1242`
   gets a dated retirement note"* is therefore met by the dated strike and the status change.
   If the decision-maker rules that a body note is required, that is a correcting `RL-`, not an
   edit.
10. **Coverage and verdict.** `uv run python scripts/req-coverage.py` lists the new tests against
    FR-218. The ledger records **FR-218's authoring half delivered** (`PL-1254`'s scope for this
    Work).
11. **The gate.** The full two-half gate exits 0 under the single gate (RL 9620). The ledger
    quotes every rc, the `N passed` line and `HEAD`.
12. **MERGE-ACK**, as Slice 2's acceptance 14. A Slice closes on a clean audit and the lead's
    merge (`CLAUDE.md` §13).

## Global Constraints

- **Spec first** (`CLAUDE.md` §0).
- **One risk price** (FR-218). The selector admits only `mid_term_adjustment` and `cancellation`
  (`RL-1344` §2.3). A `new_business` or `renewal` quote never evaluates a purpose mount.
- **One bundle per Rating Version** (FR-239; `RL-1344` §3, second bullet).
- **One inliner** (Slice 2's), extended, never copied.
- **A shape is defined once, in `model-schema`** (`CLAUDE.md` §2).
- **No new error code** unless DP-S3-1's ruling names one. `VALIDATION_FAILED` and
  `INPUT_CONTRACT_VIOLATION` are registered (`backend/src/app/errors.py`, `RATING_ERROR_CODES`
  `:309`; `INPUT_CONTRACT_VIOLATION` `:355`).
- **Money is integer minor units or `Decimal`.** FR-248's ladder reconciles on every purpose's
  evaluation.
- **Do not build ahead of the phase.** No designer view (WK-675 S9). No APR or schedule
  (FR-252).

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.1 | FR-218 | **The authoring half**: the purpose mount, FR-212 per purpose, the real check, and the interim rule's retirement |
| `03` §3.1 | FR-212 | Checked for each purpose's graph (`RL-1344` §3) |
| `03` §3.1 | FR-217 | Purpose mounts use Slice 2's pin and inliner, unchanged |
| `03` §3.4 | FR-239 | One bundle per Rating Version; the hash covers each purpose's evaluation |
| `03` §3.8 | FR-258 | A purpose quote's trace shows the purpose mount's inlined steps (the Slice 2 form) |

**Not in this slice:** the designer view (WK-675 S9); G3 (WK-674 Slice 2); and any `04` GIPP or
ENBP work (`04` FR-294 is WK-685, Phase 4).

### Premises, read at `cdaaa573`

| # | Premise | Evidence |
|---|---|---|
| a | The interim guard refuses both purposes, whatever is mounted | `score.py:395-422`; message contains "interim" |
| b | It is called on both scoring paths, with the algorithm | `score.py:898` (`score_one`), `:1063` (`_score_context_sync`) |
| c | `QuotePurpose` has five values | `model_schema/scoring.py:44`; `QuoteContext.purpose` `:105` |
| d | `SubGraphRef` has no `purposes` | `model_schema/rating.py:342-352` (Slice 2 adds the port map) |
| e | The interim tests | `test_rating_score.py:438-507`, listed in acceptance 8 |
| f | FR-218's interim clause | `03:87`, *"(Amended 2026-09-29, an interim rule, `RL-1242` …)"* |
| g | The bundle has one graph | `Bundle` `compile.py:505` (`algorithm_ref, graph, resolved_payloads, pins, content_hash, compiled_at`); `bundle_hash(graph, pins)` `:522-535` |
| h | `CompiledBundle` holds one decision | `runtime.py:625-643` (`content_hash`, `decision`, `algorithm`, `boosters`) |

The executor re-reads each premise **at Slice 2's merge tree**, and maps d, g and h to Slice 2's
names.

### Decision points

**Ruled, and binding here:** `RL-1344` §2 (the selector), §3 (the real check from the bundle; one
bundle; FR-212 per purpose) and §4's Slice 3 bullet.

**Open, for the decision-maker.** These are `RL-1344` §3's open question, split in two. Each
answer must fit inside §3's invariants.

| DP | Question | Options | Recommendation | Blocking |
|---|---|---|---|---|
| **DP-S3-1** | **How does a purpose mount's output reach the ladder and the payable?** `RL-1344` §3 asks, for example, *"whether a cancellation's refund is a new declared output, a ladder rung, or something else"* | (a) **Override.** A purpose mount's mapped output names a value that a parent step already produces, upstream of the ladder (for example the annual premium before `payable_premium`). In that purpose's graph, the mount's output replaces the parent's producer of that name. The parent's producer, and any step that feeds only it, is absent from that graph. The chain downstream (the ladder rungs, FR-248's reconciliation, the payable) is unchanged; (b) **new optional outputs.** Purpose mount outputs feed new declared outputs (`required: false`, for example `refund_minor`), present only for that purpose; `payable_premium_minor` stays the annual chain; (c) **a separate result section.** `ScoringResult` gains a `purpose_outputs` map | **(a).** FR-218 prices the MTA or cancellation itself with "pro-rata, refund and charge logic", so the **payable** of such a quote must be the adjusted figure. Under (b) and (c), `payable_premium_minor` on an MTA quote is the annual premium, a silent mispricing of the kind FR-218 exists to prevent. Under (a), each purpose graph still has exactly one producer per name (FR-212, `RL-1344` §3), and a name only a purpose mount produces still cannot be consumed by an always-running step (`RL-1344` acceptance 4), because under (a) every overridden name also has a parent producer. **Codes:** an override of a name no parent step produces, or of an `input` step's name, is refused at save with `RATING_GRAPH_UNRESOLVED_REF`; a consumer outside the mount of a purpose-only name, with the same code (acceptance 3) | Tasks 2–4 |
| **DP-S3-2** | **How are the inlined nodes gated by `purpose` at evaluation?** | (a) **One graph per purpose that has a mount.** `Bundle` gains `purpose_graphs: dict[str, JdmGraph]`, holding only the purposes some mount selects, so it is empty for every version without a purpose mount. `bundle_hash` covers it **only when non-empty**, so every existing hash is unchanged. `CompiledBundle` holds one decision per graph, and scoring chooses by `ctx.purpose`, falling back to the base graph; (b) **one graph with a `purpose` switch node** in `to_jdm`; (c) **scorer-side pruning** of the decision at run time | **(a).** Each purpose graph is a plain DAG, which is exactly what `RL-1344` §3's "FR-212 for each purpose's graph" checks, and the trace of a quote shows only what ran. (b) puts two producers of an overridden name in one graph, against FR-212 within the graph, and adds a node type to the ADR-706 translation layer. (c) evaluates a graph that is not the one that was hashed. One bundle per Rating Version (FR-239) holds under (a): one `Bundle`, several graphs | Tasks 3–4 |

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree, and `git branch --show-current` is the slice branch, cut
  from `main` after Slice 2 merged.
- [ ] `uv sync --all-packages`.
- [ ] Re-derive premises a–h at that tree, mapped to Slice 2's names, and record each one.
- [ ] `gh pr list --state open`, and read anything that rules on FR-218, `purpose`, sub-graphs,
  `score.py`, `runtime.py` or `Bundle`. Name the SHA read.
- [ ] Confirm DP-S3-1 and DP-S3-2's resolutions **by record id**. Stop if either differs from
  **Decision points**.
- [ ] Confirm that the dispatch record carries `RL-1344` §2, §3, §4's Slice 3 bullet and the
  rulings, and names who writes `RL-1242`'s status (acceptance 9).

### Task 1: Spec — FR-218's strike, `03` §4.1, §4.11, and the bundle text

**Files:** `docs/specs/03-rating-engine.md`.

- [ ] **FR-218** (`03:87`). Strike the `RL-1242` amendment, dated, citing `RL-1242:83-85` and this
  slice. The `RL-1344` amendment's last clause, *"the interim rule above stands until WK-1250
  Slice 3 delivers this"*, gets a dated note that Slice 3 delivered it. **This edit lands in the
  slice's final commit** (acceptance 9), not here. Task 1 writes the rest.
- [ ] **§4.1.** The mount example gains `"purposes": ["cancellation"]` on a second mount. The
  invariants gain FR-212 per purpose graph (`RL-1344` §3, third bullet) and DP-S3-1's rule, dated
  and cited.
- [ ] **§4.11** (`03:822`). A dated line: FR-218's purpose mount landed in WK-1250 Slice 3.
- [ ] **The bundle text.** State what the bundle carries per purpose (DP-S3-2) where `03` describes
  `Bundle` and `compile_bundle` (§5.2, `03:1028`; Task 0 finds every other site with
  `grep -n 'resolved_payloads\|content_hash' docs/specs/03-rating-engine.md`).
- [ ] `python3 scripts/audit-docs.py` exits 0.
- [ ] Commit: `docs(specs): 03 §4.1 and §4.11 — FR-218's purpose mount and per-purpose graphs (RL-1344)`.

### Task 2: `model-schema` — `SubGraphRef.purposes` and FR-212 per purpose

**Files:** `packages/model-schema/src/model_schema/rating.py`;
`docs/contracts/schemas/rating-algorithm.schema.json`. Test:
`packages/model-schema/tests/test_rating_algorithm.py` (appended).

**Interfaces:**
- Produces: `SubGraphRef.purposes: list[Literal["mid_term_adjustment", "cancellation"]] | None = None`.
  The `Literal` members are `QuotePurpose`'s (`model_schema/scoring.py:44`), restricted by
  `RL-1344` §2.2. Do not write a second purpose vocabulary: derive the admitted pair from
  `QuotePurpose`, or state it once beside it.

- [ ] **Step 1: Write the failing tests** (acceptance 2 and 3), mirroring the neighbouring algorithm
  builders. One test per refused form; the accepted forms; a step that runs for every purpose
  consuming a purpose-only name; DP-S3-1's override cases.
- [ ] **Step 2: Run them.** Expected: the selector cases fail on `extra="forbid"` (the field does
  not exist), and the FR-212 cases are accepted when they should be refused. Any other cause is a
  plan defect.
- [ ] **Step 3: Implement.**
  - Add the field: non-empty, no duplicates, the admitted pair only. Each violation is a
    `ValueError`, so the route maps it to `VALIDATION_FAILED`, as `RL-1344` §2.2 says.
  - `_graph_invariants` runs once per purpose graph: the base graph with unconditional mounts
    only, then one per selected purpose with its purpose mounts added. Reuse Slice 2's
    mount-as-node code for every pass; never copy it.
- [ ] **Step 4:** the contract (`contract-schema`), `generate-contracts.py --check`, and
  `backend/tests/test_contracts.py`.
- [ ] **Step 5: Run Step 2's command; it passes.**
- [ ] **Step 6: Commit:** `feat(model-schema): SubGraphRef.purposes and FR-212 per purpose (FR-218, RL-1344)`.

### Task 3: The bundle per purpose — `inline_mounts`, `compile_bundle`, `bundle_hash`, `load_bundle`

**Files:** `inline.py`, `compile.py`, `runtime.py` (Slice 2's names). Tests:
`test_rating_inline.py`, `test_rating_compile_bundle.py`, `test_rating_runtime.py` (appended).

- [ ] **Step 1: Write the failing tests** (acceptance 6 and 7; DP-S3-1 and DP-S3-2 as ruled):
  - `inline_mounts(..., purpose=None)` inlines unconditional mounts only;
  - `purpose="cancellation"` adds the cancellation mounts and applies DP-S3-1's override;
  - `compile_bundle` emits `purpose_graphs` for exactly the selected purposes;
  - the hash changes when only `purposes` changes, and is unchanged for a version with no purpose
    mount;
  - `load_bundle` gives one decision per purpose graph.
- [ ] **Step 2: Run them; they fail by cause.** `purpose` is an unexpected keyword, and
  `purpose_graphs` is missing.
- [ ] **Step 3: Implement**, under DP-S3-2 (a):
  - `inline_mounts` gains `purpose: str | None = None`. One function, with the default behaving as
    Slice 2's.
  - `compile_bundle` runs Slice 2's structure checks on **every** purpose's inlined algorithm,
    not only the base one, so a fragment refused for one purpose is refused at compile.
  - `bundle_hash` covers `purpose_graphs` only when it is non-empty.
- [ ] **Step 4: Run** the four `pricing-core` test files named above, then
  `test_quote_input_raise_sites.py`. All pass, and the existing ones are unmodified.
- [ ] **Step 5: Commit:** `feat(pricing-core): per-purpose graphs in the bundle (FR-218, RL-1344 §3)`.

### Task 4: The real check and the purpose's decision in scoring

**Files:** `score.py` (`_check_purpose_mount` `:395-422`, calls `:898` and `:1063`; `score_one`
`:876`; `_score_context_sync`). Tests: `test_rating_score.py` (`:438-507` rewritten; new tests
appended); `backend/tests/test_score.py` for the routes.

- [ ] **Step 1: Rewrite and write the tests** (acceptance 4, 5 and 8). Use `_compiled` (`:137`)
  and `_ctx` (`:143`). Mirror `backend/tests/test_score.py` for `/score` and `/score/compare`.
- [ ] **Step 2: Run them.** Expected: the cancellation quote is refused with the **"interim"**
  message (premise a). That is the cause; any other is a plan defect.
- [ ] **Step 3: Implement.**
  - `_check_purpose_mount(bundle, ctx)` refuses `mid_term_adjustment` and `cancellation` with
    `INPUT_CONTRACT_VIOLATION` unless `ctx.purpose` has a purpose graph in the bundle. The message
    names the purpose and says no mount for it is inlined. The docstring says this is the real
    check and cites `RL-1344` §3. It keeps one raise site.
  - `score_one` and `_score_context_sync` evaluate the purpose's decision when one exists, and the
    base decision otherwise. The trace is built from the algorithm that was evaluated.
- [ ] **Step 4: The broken-input proof** (acceptance 5). This is a local edit, never committed.
- [ ] **Step 5: Run** `uv run pytest packages/pricing-core/tests/test_rating_score.py backend/tests/test_score.py -q`.
- [ ] **Step 6: Commit:** `feat(pricing-core): FR-218's real purpose check replaces the interim refusal (RL-1344, RL-1242)`.

### Task 5: The final commit — FR-218's strike and `RL-1242`'s retirement

- [ ] FR-218's strike (Task 1, first bullet) and `RL-1242`'s `status: retired`, written by whoever
  the dispatch record names (acceptance 9). Nothing else is edited in `RL-1242`.
- [ ] `python3 scripts/doc-index.py`, then `python3 scripts/audit-docs.py`.
- [ ] Commit: `docs(specs,rulings): FR-218's interim rule struck; RL-1242 retired (RL-1242:83-85)`.

### Task 6: The gate and the ledger

- [ ] Run the full two-half gate under the single gate. Quote every rc, the `N passed` line and
  `HEAD`.
- [ ] The ledger records:
  - the tree and the premises;
  - the red-first quotes;
  - `RL-1344` and the DP-S3 `RL-`;
  - the deleted bogus-reference test, and the Slice 2 test that covers it;
  - FR-218's verdict (acceptance 10).
- [ ] The MERGE-ACK.

## Self-review

1. **Against `RL-1344`:**
   - §2 → Task 2 and acceptance 2;
   - §3 → DP-S3-1, DP-S3-2, Tasks 3–4 and acceptance 3–4;
   - §4's Slice 3 bullet → Tasks 1–5;
   - the five *Acceptance* cases → acceptance 2, 4, 6, 3 and 7, in that order;
   - the open question → DP-S3-1 and DP-S3-2, raised here as `RL-1344:180-181` requires.
2. **Against `PL-1254` Task 3** (`:314-339`):
   - the strike → Task 5;
   - the mount in `model-schema` → Task 2;
   - the scorer → Task 4;
   - `_check_purpose_mount` → Task 4;
   - the interim tests → acceptance 8;
   - the gate outline → acceptance 4 and 5;
   - the "dated retirement note" → acceptance 9, with the frozen-body reason stated.
3. **FR-218 read to its clauses** (`03:87`):
   - "same Rating Algorithm for the risk price" → acceptance 4, third bullet;
   - "mounted only when `purpose ∈ {mid_term_adjustment, cancellation}`" → acceptance 2 and 5;
   - "declared on the Rating Version and version-pinned" → acceptance 6;
   - "refuses … rather than pricing it as new business" → acceptance 4.
4. **Literals.** Each was read at `cdaaa573`. Slice 2's names (`inline_mounts`, `Pins.sub_graphs`,
   the port map) are PL 9610's proposals, re-read at Slice 2's merge.
5. **Open:** DP-S3-1 and DP-S3-2, for the decision-maker. Acceptance 9's writer, for the dispatch
   record.
