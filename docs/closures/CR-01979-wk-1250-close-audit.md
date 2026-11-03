---
id: CR-1979
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-1250 Work close audit — sub-graph composition and MTA/cancellation pricing, FR-217's three limbs and FR-218's authoring half
status: active                  # write-once; this is the only value this family ever takes
created: 2026-11-03   # drafted 2026-11-03 under working id 8290
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: c807a59d1a26d12e63d88bc395ac3dcc373aa919
phase: P2
work: WK-1250
corrected_by: []
relates: [PL-1254, PL-1325, PL-1572, PL-1629, RL-1242, RL-1309, RL-1344, RL-1571, RL-1628, CR-1247, CR-1907, CR-838, FD-1241, FD-1317, FD-1326, FD-1768, FD-1297]
---

# CR-1979 — WK-1250 Work close audit

*Working id CR 8290, reserved by the lead; minted as CR-1979 at the lead's id turn. The auditor seat
aud-wk1250 (`opus`, Claude Opus 5.5) wrote this record on 2026-11-03 from 15:40 GMT, on the
lead's brief `~/gi-pricing-plan.local/handover/brief-aud-g1close-2026-11-03.md`, under the
maintainer's entry "2026-11-03 15:36:59 GMT" item (5) and the entry "2026-11-03 15:46:13 GMT"
in `~/gi-pricing-plan.local/channel/to-lead.md`. It follows `.claude/skills/close-workstream`,
`CLAUDE.md` §13 and §14, and takes its section shape from CR-1952.*

**What this record is.** It gathers evidence and **proposes**. Every §13 verdict below is
written "PROPOSED" and is the lead's to give. **The close is the user's dated acceptance line.**
This record does not close WK-1250. The roadmap section it edits says "close audit filed,
acceptance owed".

**Object.** `origin/main` at `c807a59d1a26d12e63d88bc395ac3dcc373aa919` (read by `git ls-remote
origin refs/heads/main` at the start; tree `10b01c900d7303394ca514dcc7c631a85e699508`). Every
`file:line` and every count below is at that tree unless it names another. Branch
`docs/wk1250-close-audit-2026-11-03`, cut from that commit.

## Scope

### §0. The requirement set, derived from the documents before any evidence

**Predicate** (runnable from the repository root at `c807a59d`). The WK-1250 roadmap section is
`docs/roadmap.md:3345`, up to the next `###` heading at `:3433` (`### RFC-895 … RFC-898`; the
next `### WK-` heading is `:3517`, but `:3433`–`:3516` is the phase's notes and coverage text, not
this Work's). The Work's plans are the five files whose front matter reads `work: WK-1250`:
`PL-1254` (map, `active`), `PL-1278` (leaf, `superseded`), `PL-1325`, `PL-1572` and `PL-1629`
(leaf, `active`).

```bash
git grep -l -E '^work: WK-1250\b' -- docs/plans          # the five plans
( sed -n '3345,3432p' docs/roadmap.md
  cat docs/plans/PL-01254-*.md ) | grep -ohE '\b(FR|NFR)-[0-9]+\b' | sort -u -V
cat docs/plans/PL-01325-*.md docs/plans/PL-01572-*.md docs/plans/PL-01629-*.md \
  | grep -ohE '\b(FR|NFR)-[0-9]+\b' | sort -u -V
```

The first prints 10 ids: FR-16, FR-20, FR-217, FR-218, FR-258, FR-343, FR-345, FR-368, FR-417,
FR-1186. The second prints 26: FR-4, FR-16, FR-20, FR-212, FR-214, FR-215, FR-216, FR-217,
FR-218, FR-219, FR-227, FR-237, FR-239, FR-240, FR-244, FR-248, FR-252, FR-258, FR-274, FR-275,
FR-276, FR-294, FR-343, FR-345, FR-368, FR-417. The union is **27 ids**. No NFR id is printed.
The superseded `PL-1278` adds FR-366 and FR-367 only; it was replaced by `PL-1325` and its ids
are not this Work's.

**Each id classified from the plans' own coverage tables** (`PL-1254:141-151`,
`PL-1325:417-437`, `PL-1572:317-340`, `PL-1629:241-253`):

| Class | Ids | Source |
|---|---|---|
| **Deliverable** (a row in a coverage table) | FR-217 (three limbs), FR-218 (authoring half), FR-258 (inlined-step limb), FR-227 (fragment output ports at create), FR-212 (mount as node; per purpose), FR-216, FR-274, FR-275, FR-276 (on the inlined algorithm), FR-237 (G1), FR-20 (restated by class, G4), FR-239 (per-purpose hash), FR-219 (the diff limb, `PL-1572` Task 4) | 13 ids |
| **Honoured, not owned** | FR-4, FR-16, FR-343, FR-345, FR-368, FR-417 (`PL-1325:425-426`); FR-214, FR-215, FR-240, FR-244, FR-248, FR-252 (constraints named in task text) | 12 ids |
| **Not this Work's** | FR-294 (`PL-1629:252`: WK-685, Phase 4); FR-1186 (cited at `PL-1254:210` as the Rate Table Version precedent for DP-1 (b); owned in WK-675's section, `docs/roadmap.md:1449`) | 2 ids |

**Reconciled against the roadmap.** The WK-1250 section carries no count. Its scope line reads
"FR-217's inlining limb … and FR-218" (`docs/roadmap.md:3357`), narrower than the three FR-217
limbs `PL-1254:149-157` takes. `PL-1254:157` says "The lead aligns the roadmap's scope line in a
later roadmap PR". That PR has not landed (the line is unchanged at this tree). Recorded in the
replan check, Q1. The `:3487` "≈ 67 `RATE`" line is the phase's planning figure, not this Work's.

**Requirements axis.** `scope-audit.py` takes one module per run. It is stdlib-only (its imports
are `argparse`, `ast`, `json`, `pathlib`, `re`, `sys`, `tomllib`, `collections`), and
`run-heavy.sh --light` refuses anything but `audit-docs.py` and `doc-index.py` (rc 78, header
line 18), so it ran directly, niced, with load1 2.99 and gate-1 / gate-1b free:

```bash
nice -n 19 python3 <wt>/scripts/scope-audit.py RATE --sections NONE --extra FR-212,FR-216,FR-217,FR-218,FR-219,FR-227,FR-237,FR-239,FR-258,FR-274,FR-275,FR-276,FR-214,FR-215,FR-240,FR-244,FR-248,FR-252,FR-1186
nice -n 19 python3 <wt>/scripts/scope-audit.py OVR  --sections NONE --extra FR-4,FR-16,FR-20
nice -n 19 python3 <wt>/scripts/scope-audit.py GOV  --sections NONE --extra FR-343,FR-345,FR-368
nice -n 19 python3 <wt>/scripts/scope-audit.py PLAT --sections NONE --extra FR-417
```

| Run | In scope | With a `@pytest.mark.req` marker | No marker | rc |
|---|---|---|---|---|
| RATE | 19 | 18 (95%) | FR-1186 | 1 |
| OVR | 3 | 3 | — | 0 |
| GOV | 3 | 3 | — | 0 |
| PLAT | 1 | 1 | — | 0 |
| **Total** | **26** | **25** | **1** | |

FR-294 was not run: it is a Phase 4 id (`04`), named by `PL-1629` only to exclude it. The one
unmarked id, FR-1186, is not this Work's (above).

**Endpoints axis.** `scope-audit.py RATE --endpoints`: "declared: 45 … every declared endpoint
is published in the contract" (rc 1 comes from the requirements half, whose whole-module
unevidenced list is FR-1186, FR-1903, NFR-492, NFR-493, NFR-1443, none of them WK-1250's).

**Catalogue axis.** `03` declares no catalogue in the form the script reads: `grep -cE '^\|
`[A-Z]{2,4}-[A-Z]{2,4}-[0-9]+` [a-z0-9-]+' docs/specs/03-rating-engine.md` prints `0`.

**§0a and §0b.** A marker is a claim. For each deliverable, §1 reads the asserts, not the names.

## Evidence

### §1. Each deliverable: exists and works

The three slices, each a squash on `main` (`git merge-base --is-ancestor <sha> c807a59d` rc 0
for all three):

| Slice | PR | Squash | Date | Diffstat |
|---|---|---|---|---|
| SL-1339 (S1, the artifact) | #1034 | `9b0fb97c9ed1cea743639897351191bc1a862041` | 2026-10-01 | 35 files |
| SL-1340 (S2, the pin and the inlining) | #1263 | `a3572d1a9182fea68d1322267e3866bdd2ed0dee` | 2026-10-10 | 29 files |
| SL-1341 (S3, FR-218's purpose mount) | #1340 | `d0d6a26531fa20eba632486d6847b49198b8d5f1` | 2026-10-18 | 22 files |

Read against `PL-1254`'s Work acceptance standard (`:61-102`), item by item:

| `PL-1254` item | Evidence (asserts read) | Reading |
|---|---|---|
| 1. FR-217 and FR-218 evidenced by a test this Work adds | the rows below; every test named is in a file a squash above adds or changes | met |
| 2(a). A sub-graph is a stored, versioned artifact with routes | `backend/tests/test_sub_graphs_api.py:164` (create, revise, read, list); `backend/tests/test_sub_graphs_service.py:55` asserts `(slug, version) == ("ncd-ladder", 1)`, one row and one audit event, `event.action == "sub_graph.created"`, `entity_ref == "sub_graph:ncd-ladder@1"`; `:134` a refused write leaves `(0, 0)` rows and events; `backend/tests/test_migration_sub_graphs.py` (module marker FR-217) | met |
| 2(b). `Pins` carries sub-graphs; `bundle_hash` moves with the pinned version | `packages/model-schema/src/model_schema/rating.py:85` (`sub_graphs: list[ArtifactRef]`); `packages/pricing-core/tests/test_rating_compile_bundle.py:497` asserts `first.content_hash == again.content_hash` and `moved.content_hash != first.content_hash` when only the pin moves; `:511` a version pinning none hashes as before | met |
| 2(c). `compile_bundle` inlines at the mount point; a missing ref refused at compile | `test_rating_compile_bundle.py:369` asserts `"m_ncd__s_ladder" in bundle.graph.nodes`, its `produces == ["ncd_factor"]`, `bundle.pins.sub_graphs == [ArtifactRef.parse(NCD)]`; `:383` an unpinned mount raises `RATING_VERSION_UNPINNED` naming `m_ncd`; `backend/tests/test_rating_version_compile.py:1051` and `:1068` (over HTTP and the compile job) | met |
| 3. FR-218 prices MTA/cancellation through the mount and still refuses | `packages/pricing-core/tests/test_rating_purpose_mount.py:189` asserts `outcome == "quoted"`, `0 < payable < _NEW_BUSINESS_PAYABLE`, `ladder_reconciled is True`, `"m_cancel__s_prorata"` in the trace; `:202` new business with the mount has `outputs == without.outputs` and the same trace step ids; `:162` an unconditional-only mount refuses both purposes with `INPUT_CONTRACT_VIOLATION`, the message has no "interim", names the purpose, says "no mount" and "inlined"; `:178` a cancellation-only mount refuses an MTA; `:256` with `_check_purpose_mount` neutralised the MTA is quoted (the check is load-bearing). Platform route: `backend/tests/test_score_purpose_mount.py:136`, `:148`, `:158` (`/score`), `:172`, `:185` (`/score/compare`) | met |
| 4. `RL-1242` retired; FR-218's interim text struck; docstring rewritten | `RL-1242` front matter `status: retired` (changed by `d0d6a265`); `03-rating-engine.md:87` carries the interim rule inside `~~…~~` and "*(Struck 2026-10-16, WK-1250 Slice 3 (`SL-1341`), as `RL-1242:83-85` requires … `RL-1242` is retired by `RL-1628`.)*" | met, **as amended**: `PL-1254` item 4 asks for "a dated note on `RL-1242`". `RL-1628:159-166` ruled instead that `RL-1242`'s body is frozen and takes no note, and that the status line alone changes. The ruling governs |
| 5. The trace shows inlined steps, attributable to the mount | `packages/pricing-core/tests/test_rating_score.py:992` asserts `{"m_ncd__s_ladder", "m_ncd__s_cap"} <= set(ids)`, their order before `s_office`, `ladder_reconciled`, the payable `1_507`, and that tracing does not change the result | met |
| 6. Every decision point resolved before its slice | DP-1, DP-3, DP-4 by `RL-1309`; DP-2 by `RL-1344` (roadmap `:3367`); S2's by `RL-1571`; S3's by `RL-1628` | met |
| 7. Every slice closed on its own clean audit | SL-1339 `closed` (roadmap `:3375`, `:3387`, audit CLEAN at `04e8e53e`); SL-1340 `closed` (`:3395`, `:3409`); SL-1341 `closed` (`:3417`, `:3429`, `LG-1808` "## Audit" and the delta audit at `:358`) | met |
| 8. The full gate, both halves, on the merged tree of the last slice | §2 | gate of record per slice; fresh gate OWED |

The other deliverable rows:

| Id | Evidence | Reading |
|---|---|---|
| FR-227 (fragment ports at create) | `packages/pricing-core/tests/test_rating_compile.py:135`, `:141`, `:345`, `:387`, `:397`, `:407`, `:421`, `:520` (marker FR-227; file changed by `9b0fb97c`); `test_sub_graphs_service.py:134` (`RATING_TYPE_MISMATCH`, no row, no event) | delivered |
| FR-212 (mount as node; per purpose) | `packages/model-schema/tests/test_rating_algorithm.py:398`, `:416`, `:427`, `:436`; per purpose `:603`, `:620`, `:628`, `:670` | delivered |
| FR-216, FR-274, FR-275, FR-276 on the inlined algorithm | `test_rating_compile_bundle.py:473` (`test_the_save_time_checks_run_over_the_inlined_algorithm`, parametrised over expression and code) | delivered |
| FR-237 (G1) | `test_rating_compile_bundle.py:383`, `:391`, `:407` (purpose mount), `:432` (fragment reference) | delivered |
| FR-20 (by class; G4) | `03-rating-engine.md:558` restated by class; `test_rating_compile_bundle.py:539` (`test_g4_a_sub_graph_pin_compiles_regardless_of_status_and_the_exemption_is_declared`); `test_rating_version_compile.py:945` (no status column) | delivered |
| FR-239 (per purpose) | `test_rating_purpose_mount.py:272` (`set(bundle.purpose_graphs) == {"cancellation"}`, empty for an unconditional mount), `:284` (purposes alone change the hash), `:292` (no purpose mount keeps the Slice 2 hash), `:348` (the key is omitted from the bytes) | delivered |
| FR-219 (the diff limb) | `test_rating_algorithm.py:489`, `:511`, `:522`, `:682` (a purposes-only change appears as a mount change); persisted: `backend/tests/test_rating_version_dislocation_gate.py:290` (`test_the_persisted_structural_diff_carries_a_sub_graph_re_point`), which closes the limb `LG-1588:126` carried to WK-673 | delivered; see FD-1768 in §5b for its attribution wording |
| FR-16 | `test_sub_graphs_api.py:304` (another workspace's sub-graph is 404 and absent from the list) | delivered |
| FR-343 | `test_sub_graphs_api.py:264` (403 without the role) | delivered |
| FR-345 | `test_sub_graphs_api.py:278` asserts 403 for a caller whose role is scoped to a different rating algorithm; its marker names FR-343 only | delivered; the marker undercounts it (no finding: FR-345 is evidenced elsewhere and is honoured, not owned) |
| FR-368 | `test_sub_graphs_service.py:55` and `:134` (one event with the row, none without); no FR-368 marker on either | delivered |

### §2. The gate

Gate of record per slice:

| Slice | Gate of record | PR head | CI on the PR head (run ids) |
|---|---|---|---|
| SL-1339 | run 4, head `44bd29e08e7d586b84eace454b78b3fb3cab526b`, "GATE: pass — 7 of 7 stages passed", pytest "4488 passed, 3 skipped", frontend "97 files, 609 tests passed" (`LG-1355:323-335`) | `51074fcc7f8ec358ef104ee13d5c3098ac09865c` | python 36821667402, docs 36821667406, frontend 36821667417, history-policy 36821667457 — all `success` |
| SL-1340 | gate 1 at `806740efaeee0cb1583586544e0e45d8eceabecd` red (mypy 1, audit-docs 1, pytest "17 failed"), each red classed and fixed, then the lead's 11:07:35 targeted re-gate form with CI as the full Python run (`LG-1588:92-94`, `:198-215`) | `1528231663171f53d2d0b334197f54c12a06f901` | python 38044755040, docs 38044755037, frontend 38044755029, history-policy 38044755030 — all `success` |
| SL-1341 | `880c2fc0cd0ff31104e2d42c0b1fa6882d1423ef` GREEN (the squash body of `d0d6a265`, "Gate of record 880c2fc0 GREEN (the maintainer, 2026-10-18 11:53:26 BST)"; `LG-1808:360`) | `fa2a0071fe936f26ee052e489c98ed61816a939f` | python 39125347914, docs 39125347827, frontend 39125347860, history-policy 39125347826 — all `success` |

The PR heads and run ids were read with `gh pr view <n> --json mergeCommit,headRefOid` and
`gh run list --commit <head>`, read-only.

**SL-1340 has no full local gate of record**: its gate 1 was red and the re-gate was targeted
by the lead's ruling, with CI as the full Python run. The CI runs above are green.

**Fresh full gate: OWED — the lead schedules it; head = the CR branch head at that time.** This
seat ran no gate and no test.

### §3. New checks proven on broken input

| Check | Red proof | Ancestry |
|---|---|---|
| FR-218's real check (`_check_purpose_mount`) | red-first tests committed at `77cbf5225f2b08476bdd1c1c003d48e789636e69` ("test(rating): red-first tests for FR-218's purpose mount (SL-1341 prep …)", `test_rating_purpose_mount.py` +321, `test_rating_algorithm.py` +145); re-proved by cause at the gate's Step 0 (`LG-1808:196-199`); `test_rating_purpose_mount.py:256` keeps a standing proof that neutralising the check prices the MTA | `git merge-base --is-ancestor 77cbf522 fa2a0071` rc 0 (PR #1340's head). Against `main` rc 1, as expected: the PR was squashed into `d0d6a265` |
| The inliner, G1, the hash, `load_bundle` | `LG-1588:129-133`: "15 failed, by the predicted cause" before any compile code; `load_bundle` red with `runtime.py` restored; broken-input proofs (drop `*pins.sub_graphs` from `all_refs`; `bundle_hash` ignoring `sub_graphs`; every mount treated as pinned), each named test red | local edits, restored by copy and `cmp`, never committed: **no commit to prove ancestry of**. The proof is the ledger's quoted output |
| The diff limb | `LG-1588:125`: `sub_graph_mounts=[]` in `diff_algorithms` reds the limb tests (`assert 0 == 1`) | local edit, not committed |
| The reproducibility condition | `LG-1588:212`: `test_a_bundle_that_pins_no_sub_graph_serialises_without_the_key` red first | in the slice's commits; squashed |
| SL-1339's artifact, migration, FR-227, routes, FD-1326 | `LG-1355:120-185`: each task's red (collection errors, `ImportError`, `assert (404, 'NOT_FOUND') == (422, 'RATING_GRAPH_CYCLIC')`) | recorded per task; the red runs are pre-implementation runs, not commits |

**What these proofs license.** Each says its check fires on the input it was given. None was
re-run by this seat (no tests, per the brief).

### §4. NFRs

**No NFR id is in the derived scope** (§0: the predicate prints none). Two notes:

- `test_rating_score.py:992` asserts that tracing does not change the result on a mounted bundle
  (the NFR-490 property), as a functional assert, not a measurement.
- **NFR-489 (p99 latency) on a bundle with a mount or a purpose graph is measured nowhere.** The
  rating benchmarks pin no sub-graph: `scripts/bench-rating.py:317`, `scripts/bench-score-batch.py:90`
  and `scripts/bench-compiled-for.py:91` each set `"sub_graphs": []`. **PROPOSED: deferred with an
  owner to nfr-bench-1 (Thu 5 – Fri 6 Nov 2026)** as one extra case (a mounted bundle, and a
  cancellation quote against a purpose graph), owner the lead's to name. If the lead rules it out
  of G4's per-id list, the record is "not this Work's".

### §5. Not delivered: every requirement without evidence, with a PROPOSED verdict

| Id | PROPOSED verdict | Evidence |
|---|---|---|
| FR-1186 | **PROPOSED: reassigned — not WK-1250's.** | Cited only as DP-1 (b)'s precedent (`PL-1254:210`); owned in WK-675's section (`docs/roadmap.md:1449`); CR-1952 gives it its verdict |
| FR-294 | **PROPOSED: reassigned — WK-685, Phase 4.** | `PL-1629:252` |
| FR-219's attribution wording (FD-1768) | **PROPOSED: not started — fix before close, owner WK-1250**, as the row already reads | §5b |

Every one of the 13 deliverable ids has evidence read by assertion in §1.

### §5a. Binding plan-review conditions

| Review | Condition naming WK-1250 | Artifact | State |
|---|---|---|---|
| `CR-1247` (plan review 16) Proposal 10, accepted 2026-09-29 (roadmap `:3357`) | a new P2 Work for FR-217's inlining and FR-218's authoring half; WK-669 not reopened; `CR-838` corrected | WK-1250 (`docs/roadmap.md:3345`); `PL-1254`; `CR-838:46` ("Dated correction, 2026-09-29 … guard delivered; `sub_graphs` inlining NOT delivered → FD-1241") | met |
| `CR-1907` (plan review 17) row 10 (`:46`) | the tracking of P10: "FD-1241's register cell (:209) does not name WK-1250" | `register.md:209` Decision cell now reads "***Resolved 2026-10-25***: closed by the merged WK-1250 slices, PR #1034 … PR #1263 … PR #1340" | met in the Decision cell; the Work-item cell still reads `WK-669`, which is the row's origin, not its owner |
| `CR-1907` E1–E7 (`:133-146`) | none names WK-1250 | — | nothing owed |

`grep -c WK-1250` over every `kind: review` record under `docs/closures/` finds `CR-1907` only.

### §5b. The owed list, generated

```text
Generated by `python3 scripts/register-owed.py WK-1250` against `c807a59d (`docs/wk1250-close-audit-2026-11-03`)`.
Mode: work item 'WK-1250'. 4 owed row(s), 1 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).

- … (FD-1241) (work item: 'WK-669', phase: '2') — **not started** … ***Resolved 2026-10-25***: closed by the merged WK-1250 slices …
- … (FD-1317) (work item: 'WK-1178', phase: '2') — **deferred with an owner — WK-1178** … ***Resolved 2026-10-25***: closed by the merged fix, PR #1012 …
- … (FD-1326) (work item: 'WK-1250', phase: '2') — **carry forward with an owner** (WK-1250 Slice 1, fixed by its merge …) …
- … (FD-1768) (work item: 'WK-1250', phase: '2') — **fix before close with an owner: WK-1250**, a follow-up slice after SL-1341 merges …

Excluded as opening with a resolution marker — verify:
- `compile_bundle` does not check step table, lookup and model refs against the pin set (FR-237) (FD-1297)
```

*(Each row's text is elided at "…"; the run printed each Decision cell whole. rc 0.)*

**The script's ids:** FD-1241, FD-1317, FD-1326, FD-1768 (owed); FD-1297 (excluded).

**Read by hand against `docs/findings/register.md`:**

| Row | Line | Hand reading | Owed? |
|---|---|---|---|
| FD-1241 | `:209` | The Decision cell carries "***Resolved 2026-10-25***" mid-text, after the earlier decision. The script's known defect (to-lead "2026-11-03 15:36:59 GMT") counts it | **removed** — resolved |
| FD-1317 | `:221` | Same defect: "***Resolved 2026-10-25***: closed by the merged fix, PR #1012" mid-text. A WK-1178 row | **removed** — resolved, and not WK-1250's |
| FD-1326 | `:224` | Open: "carry forward with an owner (WK-1250 Slice 1, fixed by its merge …)". The fix **is on main**: `backend/src/app/platform/rating_algorithms.py:57-92` picks the code from the typed class in `exc.errors()` (`GraphCycleError`, `GraphUnresolvedRefError`), never from `str(exc)`; `packages/model-schema/tests/test_graph_errors.py` was added by `9b0fb97c`; the `cycle_note` case `backend/tests/test_rating_algorithms.py:264-272` asserts `VALIDATION_FAILED` with no `xfail` left (`git grep -n xfail` over that file and `test_graph_errors.py` prints nothing) | **owed: the register closing act only** — set the row closed citing #1034, `9b0fb97c` |
| FD-1768 | `:392` | Open: "fix before close with an owner: WK-1250, a follow-up slice after SL-1341 merges". **The defect is live at this tree:** `packages/model-schema/src/model_schema/rating.py:1093-1095` emits a mount change with `before == after`, `ports_changed=False`, `purposes_changed=True` for a purposes-only change, and `packages/pricing-core/src/pricing_core/rating/analysis.py:662-664` words every `before == after` change "`{point}: mount ports re-mapped ({mount.after})`" without reading either flag. No slice row, plan or branch exists for the fix (`git grep -n 'FD-1768'` over `docs/` outside `INDEX.md` hits only the essay and the register row). No test crosses the two: `git grep -ln 'mount ports re-mapped'` prints `analysis.py` and `test_rating_attribution.py`, and `git grep -n purposes` over `packages/pricing-core/tests` finds no attribution case | **owed: a code fix before the close** (wording only, no pricing effect — the row's own MEDIUM) |
| FD-1297 | `:219` | Excluded correctly: "**Resolved 2026-09-30** by #988". Its WK-1250 mentions are history ("replacing WK-1250 Slice 2", "before the WK-1250 Slice 1 dispatch"); no residual item | not owed |

**Corrected owed list: FD-1768 (a code fix) and FD-1326 (a register close act).** Every id in
the generated block appears above with a resolution.

### §5c. Workflow steps that cite this close's requirements

```bash
git grep -n -E '\b(FR)-(212|216|217|218|219|227|237|239|258|274|275|276|20)\b' -- 'docs/workflows/WF-*.md'
```

Each hit read to its step, and each cited requirement read to its end with its dated
amendments, at `c807a59d`:

| Journey | Step | Id | Reading |
|---|---|---|---|
| WF-698 | E10 | FR-20 | still says it (approved models become referenceable) |
| WF-699 | B6 | FR-212 | still says it (an unresolved consume cannot be saved) |
| WF-699 | B7 | FR-217 | still says it ("Mounts the reusable `sub_graph:ncd-ladder@4`") — but see C1 |
| WF-699 | B9 | FR-227 | still says it (amended 2026-10-26, RL-1958) |
| WF-699 | C1 | FR-237 | **disagrees by omission.** C1 reads "declares the algorithm version and every pin: rate tables, peril structure, reference tables". Since SL-1340, a mount resolves only against the version's own sub-graph pins (G1, `test_rating_compile_bundle.py:383`), so the B7 mount compiles only if C1 pins `sub_graph:ncd-ladder@4`. FR-237's own enumeration (`03-rating-engine.md:137`) also lists no Sub-graph Version, although `03` §4's Pins example carries `"sub_graphs": ["sub_graph:ncd-ladder@4"]` (`:514`) and `Pins.sub_graphs` exists (`rating.py:85`). The C1 list also omits models, which C4 relies on, so it reads as illustrative; FR-237's does not |
| WF-699 | C4 | FR-20 | still says it (`PIN_NOT_APPROVED` for a `review` model; FR-20 is restated by class at `03:558`, and a model still has a lifecycle) |
| WF-699 | C6 | FR-239 | still says it |
| WF-699 | coverage rows `:111`, `:139`, `:140` | FR-212, FR-237, FR-239, FR-20, FR-258 | still say it |
| WF-701 | `:29`, A6 | FR-239, FR-258 | still say it |
| WF-702 | C7, `:207` | FR-20 | still says it |

No step cites FR-218: no journey prices an MTA or a cancellation.

**The C1 / FR-237 omission, resolved by the maintainer's entry "2026-11-03 15:58:45 GMT" item
(3)**: "if compile REFUSES an unpinned sub-graph on main (the auditor cites the test), it is a
spec/workflow omission → a dated clause in 03 FR-237 and a WF-699 C1 line in the CR's PR, no
FD". **Compile on `main` refuses it**, at two levels:

- `backend/tests/test_rating_version_compile.py:1066-1077`
  (`test_a_mount_whose_sub_graph_is_not_pinned_fails_the_compile_job`, markers FR-217 and
  FR-237): the version mounts a stored sub-graph with `pinned=False`; after the compile job,
  `assert job_row.status is JobStatus.FAILED` and
  `assert job_row.error["code"] == "RATING_VERSION_UNPINNED"`.
- `packages/pricing-core/tests/test_rating_compile_bundle.py:379-384`
  (`test_g1_a_mount_whose_version_is_not_pinned_is_refused_with_no_steps`):
  `with pytest.raises(ValueError, match="RATING_VERSION_UNPINNED")` around
  `compile_bundle(_mounted_version(pinned=()), …)`, and `assert "m_ncd" in str(raised.value)`;
  `:387-394` refuses a mount pinned at another version the same way.

So the code is right and the text was short. **This record's branch appends a dated clause to
`03` FR-237** (`docs/specs/03-rating-engine.md:137`, append-only, the row's earlier text
unchanged) **and a dated line to WF-699 C1** (`docs/workflows/WF-00699-…:70`, which now also
cites FR-217). **No FD.**

## Findings

- **FD-1768** (open, owner WK-1250): fix before close; the code fix is owed (§5b).
- **FD-1326** (open in the register, discharged in code by #1034, squash `9b0fb97c`): the
  register close act is owed. **It lands in docs batch 6, not in this record's PR** (the lead's
  verdict on the maintainer's entry "2026-11-03 15:58:45 GMT" item (2)).
- **FD-1241** and **FD-1317**: resolved 2026-10-25; listed by the script through its mid-cell defect.
- **FD-1297**: resolved 2026-09-30; correctly excluded.
- **FR-237 and WF-699 C1**: a spec and workflow omission, not a finding; amended in this branch (§5c).
- **Observations, not findings:** the roadmap's WK-1250 scope line is narrower than the work
  `PL-1254` took, and `PL-1254:157`'s promised alignment PR has not landed; the SL-1341 row
  (`docs/roadmap.md:3429`) still says "MERGE-ACK: pending" although #1340 merged 2026-10-18 with
  the maintainer's MERGE-ACK quoted in its squash body; the WK-1250 section's "Goal" and
  "Demo-able outcome" lines (`:3359-3363`) are the phase's text, not this Work's. None is edited
  here: the brief limits the roadmap edit to one line.

## Replan check (`CLAUDE.md` §14, `RFC-1248`)

1. **Completion — yes.** The scope audit's FR-217 is three limbs; the roadmap row says the
   inlining limb (`:3357`). `PL-1254:149-157` took the wider scope knowingly at activation, so
   nothing moves.
2. **Omission — yes.** FD-1768 is owned by WK-1250 as "fix before close", and no slice row or
   plan carries the fix. It adds a small slice inside this Work; it moves no phase.
3. **Skills and research — yes.** `register-owed.py` counts a row whose Decision cell carries
   "Resolved …" mid-text as owed (FD-1241, FD-1317 here). Already known (to-lead "2026-11-03
   15:36:59 GMT"). It moves nothing.
4. **Drift — yes.** FR-237's enumeration and WF-699 C1 omitted the sub-graph pin the code
   requires (§5c; amended in this branch), and the roadmap's scope and SL-1341 lines are stale.
   None moves a slice or a phase.
5. **Shape — no.** No phase boundary or Work scope moved since CR-1907 (2026-10-25).

`register-owed.py review` at `c807a59d`: **29 owed rows** (11 excluded as opening with a
resolution marker); rc 0.

**Triggers:**

- A phase boundary or Work scope moved: **not fired**.
- An exit criterion at risk: **fired, borderline.** G1 needs WK-1250 closed by a dated
  acceptance line before the exit demo (Wed 18 Nov 2026), and FD-1768 is "fix before close" with
  no slice cut. Code freeze is Tue 10 Nov 2026. The fix is wording plus one test, so the risk is
  one of scheduling, not of size.
- A replan decided: **not fired**.
- A finding that moves a slice or a phase: **not fired.** FD-1768's fix slice was decided at
  filing (2026-10-17), inside this Work.

**PROPOSED:** no full review now. The exit-criterion line is carried to the full review before
the P2 exit demo, on one condition: the lead names an owner and a date before Tue 10 Nov for
FD-1768's fix slice. **The verdict is the lead's.**

**Replan check, RULED** (the maintainer's entry "2026-11-03 15:58:45 GMT" item (4), and the
lead's verdict on it): **the trigger FIRED** — "an exit criterion at risk": G1 needs WK-1250
closed by the user's line, and FD-1768's "fix before close" had no slice. **No full §14 review
now**: the pre-demo review, Mon 16 – Tue 17 Nov 2026, absorbs it. The owner and date are item
(1) of the same entry: FD-1768's fix is SL 8296 / LG 8297 (working ids), planned by
plan-fd1768, red-first, merge target Fri 6 Nov 2026.

## Verdict

**NOT CLOSE-READY.** *(The maintainer's entry "2026-11-03 15:58:45 GMT" item (5): "CR 8290
files as the audit of record with verdict NOT CLOSE-READY and the owed list"; the auditor
proposed "not yet ready for acceptance".)* Every deliverable of `PL-1254`'s acceptance standard
is evidenced by assertion (§1), each slice closed on its own audit with green CI (§2), and every
binding plan-review condition is met (§5a). **The owed list**, before the user's acceptance line:

1. **SL 8296** (working id; ledger LG 8297): FD-1768's code fix, a gated code slice planned by
   plan-fd1768 as a dated WK-1250 delta row. Red first on `rating.py:1093-1095` (a
   purposes-only change gives `before == after`) and the `analysis.py:662-664` wording, with a
   test that changes `purposes` alone. Merge target Fri 6 Nov 2026 (before code freeze, Tue 10 Nov).
2. **FD-1326's register close act** (docs only), citing #1034, `9b0fb97c`: in **docs batch 6**.
3. **The fresh full gate**, both halves, at the head after SL 8296 merges: OWED, the lead schedules it.

**WK-1250's close verdict and the user's line come after SL 8296 merges and that gate runs**
(target Fri 6 / Mon 9 Nov 2026, the lead's to state).

Proposed, with no effect on acceptance: NFR-489 on a mounted bundle at nfr-bench-1 (§4); the
roadmap's scope-line and SL-1341 line alignment.

Every §13 verdict above is PROPOSED and is the lead's. **The close is the user's dated
acceptance line.**
