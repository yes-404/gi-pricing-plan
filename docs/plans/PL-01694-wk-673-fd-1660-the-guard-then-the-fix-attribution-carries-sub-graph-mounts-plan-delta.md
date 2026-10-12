---
id: PL-1694
family: plan
kind: map
title: WK-673 — the FD-1660 fix, two slices: Stage A the loud guard (the refusal names FD-1660 and reaches the Job; WF-699 D6 asserts it), then Stage B the fix (a mount is a derived change, a subset carries its mounts and their pins, and WF-699 D7 decomposes): a dated delta to PL-1267
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: 50bbdd96b2154cb4eb79ccf91658191e51ab8906
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1267, FD-1660, RL-1686, PL-1452, SL-1387, SL-1527, RL-1449, RL-1309, RL-1571, PL-1544, PL-1542, SL-1543]
---

# PL-1694 — WK-673, the FD-1660 fix: Stage A the guard, Stage B the fix (delta to PL-1267)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). It adds
> **two** slice rows to WK-673's Work plan
> [`PL-1267`](PL-01267-wk-673-dislocation-with-attribution-map-plan.md), whose body is frozen and
> not edited. **Accepted as a map delta by the lead**, `from-lead-2026-10-09.md` "2026-10-12
> 02:34:17 BST", and by the maintainer (by delegation), to-lead "2026-10-12 02:34:38 BST": *"The
> map form per document-ids §1.6 / Lean P2 L5 is correct; my "leaf" was wrong."*
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by task;
> steps use checkbox (`- [ ]`) syntax. The executor also binds `python-test` (the `req` marker,
> negative tests), `test-driven-development` (every acceptance item is seen red **by its cause**
> before the code that turns it green), `python-package` (no pandas; `pricing-core` stays free of
> FastAPI/SQLAlchemy), `spec-change` (Stage B's T1 and T2 only), `dev-commands` (the two-half
> gate, `uv sync --all-packages`, the demo command) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step. Each executor is
> spawned from `.claude/roles/executor.md`, one per slice.

**Re-cut 2026-10-12 from 08:02 BST (`TZ=Europe/London date`) by the planner
(planner-wk673-recut), on RL-1686 DP-S (i) and DP-W, and
on the maintainer's (by delegation) entry "2026-10-12 07:44:13 BST" item (1).** The plan first
cut one slice row, SL-1696, holding both stages; it is now **two rows**: **SL-1695 — Stage A,
the guard** and **SL-1696 — Stage B, the fix**, gated right after SL-1695 merges. The first cut
was written by planner-wk673-c from 02:35 BST on the branch
`pl-9807-wk673-subgraph-attribution-2026-10-12`, last at `e788950f` (tree `7d12074f`, the
commit RL-1686 rules); this re-cut is filed on a new branch, `pl-9807-recut-2026-10-12`, from
`origin/main` `50bbdd96`, and that branch's history is not carried. **Minted early
2026-10-12** on the lead's from-lead "2026-10-12 08:09:58 BST" and the maintainer's (by
delegation) to-lead "2026-10-12 08:09:39 BST" (*"ACK and early mint as PL-1694/SL-1695/SL-1696
after #1298"*): this plan **PL-1694 from working id 9807**, Stage A's row **SL-1695 from working
id 9851** and Stage B's row **SL-1696 from working id 9850**. The working ids were reserved by
the lead (`handover/eta.md`, 2026-10-12 02:29:39 BST corrected at 02:29:58 BST, *"The WK-673
slice (C) is **PL 9807 + SL 9850**"*; 9851 in RL 9852's disclosure, *"the slices it names
(working ids 9850 and 9851)"*). The ruling is **RL-1686 from working id 9852**, minted in D14
(#1298, which merges before this plan's PR; the lead's from-lead "2026-10-12 07:57:35 BST",
*"D14 ALLOCATED: … RL-1686 (RL 9852)"*). Quoted entries keep the working ids they were written
with ("PL 9807", "SL 9850", "RL 9852", "FD 9804"), resolved by this paragraph. **Tree read:** `origin/main` `50bbdd96` (#1294); every
repository `file:line` below is at that tree unless a branch or commit is named.
`packages/pricing-core/` is unchanged from `fc4401dc` (the first cut's tree and RL-1686's) to
`50bbdd96`: `git diff --stat fc4401dc 50bbdd96 -- packages/pricing-core backend/src/app/worker`
prints nothing. Branch read: `origin/salv-sl1527-d7-2group` @`e14a81e5` (tree `4eb9771e`), the
salvage of SL-1527's authored two-group D7.

## Goal

**Stage A (SL-1695):** attribution **refuses loudly** every run it cannot yet attribute
correctly because of a sub-graph mount, with a refusal whose text names `FD-1660` and says that
attribution of sub-graph mount changes is unavailable until SL-1696, and that text reaches the
Dislocation Job's stored error; the WF-699 journey asserts that refusal at D6. **Stage B
(SL-1696):** attribution (`03` FR-266, FR-1397 to FR-1399) is correct for a Rating Version whose
algorithm mounts a sub-graph (FR-217), the guard is removed, and `WF-699` D7 decomposes the demo's
change into at least two effects that sum.

## Context

**FD-1660** (minted from working id 9804 in D13, #1290 `249670fe`; owner WK-673; **HIGH**,
re-rated by the maintainer (by delegation), to-lead "2026-10-12 02:35:40 BST").
[`../findings/FD-01660-attribution-ignores-sub-graph-mounts-a-partial-subset-drops-the-baseline-s-sub-graph-mounts-and-pins-and-a-mount-difference-is-never-a-derived-change-so-effects-are-silen.md`](../findings/FD-01660-attribution-ignores-sub-graph-mounts-a-partial-subset-drops-the-baseline-s-sub-graph-mounts-and-pins-and-a-mount-difference-is-never-a-derived-change-so-effects-are-silen.md)
carries the three limbs, the evidence and the re-rate trigger. The entries below are the
maintainer's (by delegation), in `~/gi-pricing-plan.local/channel/to-lead.md` (a local file, so
each is quoted; RFC-777), read in full by this planner; a quote keeps "FD 9804" where the entry
wrote it.

**"2026-10-12 02:29:16 BST — SL-1527 D7: (A) ACCEPTED; FD owner WK-673 (not WK-1178), MEDIUM;
(C) gets its OWN WK-673 slice before G2, planned now and run beside SL-1543"**, item 3, verbatim
in part:

> 3. (C) is its OWN slice under WK-673, NOT SL-1543's delta (a different Work, different files;
> A-4 stays focused). Seat a planner now for a small leaf plan:
>    - write set: analysis.py _subset_algorithm (+ _check_dependence if a sub-graph producer must
>      count as a dependency), its tests, and the journey's D7 lines (the 2-group split already
>      authored in the fix batch, plus removing the SKIPPED line);
>    - red first: a 2-group attribution on a candidate that mounts a sub-graph →
>      BUNDLE_COMPILE_FAILED on main;
>    - journey.py is shared with SL-1543, so the two serialise at merge (second-to-merge
>      re-merges).
> […]
> G2's condition gains this slice. PL-1544 is frozen, so record it in the new leaf plan's Context
> AND as a one-line dated delta in D13 ("G2 is met only when SL-1543 AND <this slice> merge").

**G2 is not met until Stage B merges.** `WF-699` D7 is *"attribution decomposing the change into
peril-structure, rate-table, and minimum-premium effects"*
([`../workflows/WF-00699-approved-models-to-approved-rating-version.md`](../workflows/WF-00699-approved-models-to-approved-rating-version.md)
D7). The lead's D13 delta line (`docs/roadmap.md:569`) says **"G2 is met only when `SL-1543`
AND the `WK-673` slice SL-1696 … have both merged"**; under DP-S (i) SL-1696 is Stage B, which
is gated after SL-1695, so G2 needs SL-1543, SL-1695 and SL-1696.

**"2026-10-12 02:35:40 BST — FD 9804 RE-RATED HIGH now (code read), confirmed or reverted by R3;
PL 9807 orders a LOUD GUARD first"**, verbatim in part:

> - PL 9807 Task order:
>   - FIRST, a loud guard: attribution REFUSES (a named code, never a partial report) whenever
>     the diff carries any sub_graph_mounts difference, OR either side mounts a sub-graph and K≥2.
>     Red first via R3/R2.
>   - THEN the real fix (R1–R3 green by derivation).
>   This guard alone closes the silent limb if the fix slips, so the guard may merge as its own
>   small step ahead of the fix if that is faster.
> - It is HIGH on the G2 path and in P2, so §14's rule applies: it needs a resolution before any
>   P3 start.

**"2026-10-12 02:43:49 BST — DP-G: exemption (i) REFUSED; it re-opens limb 1. …"**, the guard's
scope, verbatim in part (RL-1686 quotes it whole):

> The guard, as I mean my 02:35:40 (this supersedes its "K≥2" clause):
> - REFUSE when the derived diff carries ANY sub_graph_mounts difference (add, remove, re-point, re-map), at ANY K, including K=0 and K=1.
> - ALSO refuse when either side mounts a sub-graph and K≥2 (limb 2; loud today, kept consistent).
> - Code VALIDATION_FAILED (FR-1399's refusal, no new code). The message names "sub-graph mount differences are not yet attributable" and FD 9804.
> - In attribute after _check_groups, as planned, so derive_changes, the estimate and D6's dislocation are untouched.

**"2026-10-12 07:44:13 BST — Three dropped decision-maker hand-offs: (1) RL 9852 = (A), with 3
conditions; …"**, item (1), verbatim:

> (1) RL 9852, DP-G's consequence: (A), keep the guard as settled.
> I read dislocation_handlers.py at main: attribute() runs inside the Job (:311-321), and an AttributionError becomes PlatformError 422 before persist(). So the guard fails D6's whole run for any mount-changing version.
> - That is LOUD, and pre-release there is no user to block. G2 waits on Stage B anyway, and the silent K=1 limb closes fastest under (A).
> - (C) is refused: it keeps a silent misattribution live for days.
> - (B) is refused for NOW: persisting a run with attribution absent for a NON-twin run means deciding whether approval evidence may lack attribution. That is an evidence-floor change, not a guard detail. If Stage B slips past G2's need, the decision-maker raises (B) as its own DP.
> Conditions:
> (a) The Job's refusal names FD-1660 and says attribution of sub-graph mount changes is unavailable until SL 9850. It must not fail generically.
> (b) The Stage A slice updates every merged test that runs D6 on a mount-changing fork (test_wf699_journey's D6/D7, plus any found by grep) to assert that exact refusal, with no test deleted.
> (c) Stage B is planned NOW and gated right after Stage A on WK-673's lane, as the G2 item it is.
> I add the temporary regression to the user's summary.

**What Stage A costs the demo, stated so no reader mistakes it for a regression of SL-1527.**
Under (A) the guard fails D6's Job for any Rating Version that adds, removes, re-points or
re-maps a mount, so such a version gets no Dislocation Run and cannot be submitted
(`_dislocation_gate`, `backend/src/app/platform/rating_versions.py:994`). The demo's fork adds
`m_ncd`, so from Stage A's merge until Stage B's the journey stops being able to approve, deploy
and score `rv3`: D6 asserts the refusal, and the steps that need D6's run are `SKIPPED` naming
`FD-1660` (Stage A Task 3). That is loud, disclosed and temporary; Stage B restores them.

### The defect, read at `50bbdd96` (three limbs)

| Limb | Where | What happens | Loud or silent |
|---|---|---|---|
| L1 | `_subset_algorithm` `:742-765` | A partial subset is `base.model_copy(update={steps, input_contract, outputs})`, so it keeps the **baseline's** `sub_graphs`. A step change that consumes a name only the candidate's mount produces fails compile in every partial subset holding it. | loud: `BUNDLE_COMPILE_FAILED` (`:1015-1022`) |
| L2 | `_subset_pins` `:768-799`, `_PIN_KINDS` `:484-489` | `Pins(**lists)` is built over `_PIN_KINDS`, which has no `sub_graphs`, so every partial subset's pins carry **no** sub-graph pin; a baseline that already mounts fails every partial subset at `mounted_fragments` (`inline.py:190-225`). | loud: `BUNDLE_COMPILE_FAILED` |
| L3 | `_derive` `:559-674` | `_derive` never reads `diff.sub_graph_mounts`, so a mount added, removed, re-pointed or re-mapped is **no derived change**; with at most one other change the run reconciles and the mount's whole effect is attributed to the other change. | **silent**: a wrong attribution report |

(Paths: `packages/pricing-core/src/pricing_core/rating/analysis.py` unless named.) RL-1686's §0
records which of spec and code was wrong: for L2 the code is short of the spec (FR-1398 with
FR-218's `RL-1344` amendment); for L3 the spec is silent, so Stage B is a spec change first
(T1, T2); the guard's first limb is FR-1399's existing refusal of *"a difference between
baseline and candidate that no derived change can carry"*, so Stage A needs no new
requirement text (RL-1686 DP-S). **It does carry one dated interim line**, ruled by the
maintainer (by delegation) in the to-lead entry **"2026-10-12 08:09:39 BST — PL 9807 re-cut: ACK
and early mint as PL-1694/SL-1695/SL-1696 after #1298; items 1–3 accepted; item 4 REVERSED:
Stage A DOES carry an interim 03 note"**, item 4, verbatim:

> 4. NO to "no 03 note". While Stage A is on main, the code REFUSES attribution (and fails the dislocation Job) for a class of rating changes that 03 says are decomposed (FR-264 / §4.6). That is code and spec disagreeing for days, the case CLAUDE.md §0 says to resolve, not leave. "The refusal is self-describing" informs the caller but leaves the spec false for every reader of 03.
> - Stage A writes ONE dated interim line under FR-264 (and §4.6 if it carries the Job's behaviour): "(Interim, 2026-10-12, the maintainer's (by delegation) entry "2026-10-12 08:09:39 BST": until SL-1696 merges, attribution — and with it the Dislocation Run's Job — refuses a change that adds, removes or re-points a sub-graph mount, or any attribution with two or more groups where either version mounts a sub-graph, with VALIDATION_FAILED naming FD-1660 (FD-1660, SL-1695).)"
> - Stage B (SL-1696) STRIKES that line in place when it writes T1/T2. This changes activation need 4 from "none" to "the interim line is in Stage A's commit with the code".

The lead relayed it in from-lead "2026-10-12 08:09:58 BST". **§4.6 does carry the Job's
behaviour**: it specifies the Dislocation Run, its attribution (FR-1397 to FR-1399, the
2026-10-03 amendment at `03:647`) and its refusals (`VALIDATION_FAILED` at `:709` and `:711`), so
the same line goes there too. This is the planner's reading of the entry's "if"; the lead may
strike the §4.6 copy.

### Why the guard's text must be a coded error (RL-1686 DP-W, write 1)

The worker keeps only `safe_error_text(exc)` of an `AttributionError` as the Job's detail
(`backend/src/app/worker/dislocation_handlers.py:318-321`), and the Job stores that detail as
`JobError.message` (`backend/src/app/worker/tasks.py:197-230`, `message=exc.detail or
exc.title`). `safe_error_detail` keeps an exception's text only for a `ValidationError` or a
`CodedError` (`packages/pricing-core/src/pricing_core/safe_error.py:180-185`).
`AttributionError` is a plain `ValueError` (`analysis.py:493-499`), deliberately, because
`attribute`'s own text can name a quote id (`backend/tests/test_worker_raise_sites.py:210-216`).
A guard raised as a plain `AttributionError` therefore reaches the Job as "AttributionError"
alone and fails condition (a). **Ruled (RL-1686 DP-W):** the guard raises an error that is both
an `AttributionError` (code `VALIDATION_FAILED`) and a `CodedError`, declared in `analysis.py`,
whose text is input-free. Every `AttributionError` made coded is **refused** (NFR-499), and so is
special-casing the worker (`backend/src/` stays not written).

## Decision points

All ruled.

| DP | Ruled | By |
|---|---|---|
| DP-G | refuse any `sub_graph_mounts` difference at any K (K = 0 and 1 included), and refuse at K ≥ 2 when either side mounts; `VALIDATION_FAILED`, naming FD-1660; in `attribute` after `_check_groups`; exemption (i) (one group holding every derived change) **refused** | the maintainer (by delegation), to-lead "2026-10-12 02:43:49 BST" |
| DP-G's consequence | (A): the guard fails D6's Job for a mount-changing version until Stage B; (B) and (C) refused; conditions (a), (b), (c) | the maintainer (by delegation), to-lead "2026-10-12 07:44:13 BST" item (1) |
| DP-S | **(i)**: Stage A is its own slice, SL-1695; Stage B stays SL-1696, gated right after Stage A merges | RL-1686 |
| DP-W | Stage A: the guard as a coded `AttributionError` so its text reaches the Job (write 1); the journey's D6 asserts the refusal and the later steps are `SKIPPED` naming FD-1660 (write 2); condition (b)'s grep, recorded in the LG (write 3); `backend/src/` not written. Stage B: (a), `_derive`, `_subset_pins`, `_PIN_KINDS`, `_subset_algorithm`, `_check_dependence` and `03`'s FR-1398 and FR-1399 texts | RL-1686 |
| DP-1 | (a): a mount is derived like a step by its `mount_point`; kinds `step_added` / `step_removed` / `step_changed` (a re-point is never `table_repointed`); no new `DeltaKind`; descriptions `<mount_point>: mount added (<after>)`, `<mount_point>: mount removed (<before>)`, `<mount_point>: mount <before> → <after>` (a re-map appends `; ports re-mapped`, or is `<mount_point>: mount ports re-mapped (<ref>)` alone), each `<ref>` being `str(ArtifactRef)` | RL-1686 |
| DP-2 | (i): a subset's `sub_graphs` are the baseline's with the subset's own mount changes applied by `_merged` keyed on `mount_point`; `sub_graphs` joins `_PIN_KINDS`; sub-graph pins follow the other kinds' rule | RL-1686 |
| DP-3 | (i): a mount is a node in both directions for dependence; refused `VALIDATION_FAILED` before any compile | RL-1686 |
| DP-T | T1 (on FR-1399) and T2 (on FR-1398) adopted **as RL-1686 edited them**; applied by Stage B Task 1 | RL-1686 |

The options and recommendations this plan first proposed for each DP are in RL-1686 and in the
first cut at `e788950f`; they are not repeated here. **One standing duty** from the 07:44:13
entry is the decision-maker's, not this plan's: if Stage B slips past G2's need, it raises (B)
as its own decision point.

## The slice rows

Both rows sit under `### WK-673` in [`../roadmap.md`](../roadmap.md), `draft`, cut by the planner.

| | **SL-1695 — Stage A, the guard** | **SL-1696 — Stage B, the fix** |
|---|---|---|
| Closes | FD-1660's silent limb (L3) and the two loud ones by a named refusal | FD-1660 in full (L1, L2, L3); D7 decomposes |
| Requirements, each listed | `03` FR-1399 (its existing refusal of a difference no derived change can carry, applied to a mount difference; no text change), FR-264 and §4.6 (the 08:09:39 interim line only), FR-266 and FR-1398 (read: what the guard refuses until Stage B), FR-217 (read only); `WF-699` D6 (asserted refusal); NFR-499 (the refusal text is input-free) | `03` FR-266, FR-1397 (reconciliation, unchanged and re-proven), FR-1398 (T2), FR-1399 (T1), FR-264 (`WF-699` D7's question), FR-217 (read only) |
| NFRs | NFR-499 (the coded text); no timing NFR | `03` NFR-495, NFR-496 applied as WK-673's row states; no timing NFR |
| Gated | its activation needs below | **right after SL-1695 merges** (condition (c)) |

## Write set

| Path | SL-1695 (Stage A) | SL-1696 (Stage B) | Shared with |
|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/analysis.py` | a new error class, both `AttributionError` and `CodedError`, declared beside `AttributionError` (`:493-499`); the guard in `attribute`, after `_check_groups` (`:986`) and before `_check_dependence` (`:987`). **Not in `_derive`**: `derive_changes` (`:685-691`) feeds the estimate route the journey's D6 calls | **extends Stage A's code in the same file:** removes the guard and its error class; `_PIN_KINDS` gains `sub_graphs`; `_derive` derives mount changes and accounts mount pins; `_Change` carries the mount; `_subset_algorithm` merges `sub_graphs`; `_subset_pins` covers `sub_graphs`; `_check_dependence` treats a mount as a node | none in flight at `50bbdd96` |
| `packages/pricing-core/tests/test_rating_attribution.py` | the mounted fixture and the guard tests G1, G2, G3, G4 and the text test GT; `_candidate_version` (`:106-117`) gains an optional sub-graph pin | **extends Stage A's tests:** G1 and G2 flip to R3 and R2, G4 to R1, G3 to a decomposing one-group run; R4 added; GT deleted with the guard (the planned flip, recorded in the LG). No test that exists at Stage A's base is edited otherwise | none |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` | one `_INPUT_FREE` case for the guard's raise site (and the class name in `_SITE_NAMES` if the enumerator does not already count it; Task 2 Step 4) | the case removed with the guard | none |
| `examples/fremtpl2/journey.py` | D6 asserts the refusal; `SKIPS` gains the FD-1660 lines and D7's line is replaced; the steps that need D6's run skip | **extends Stage A's edit:** the FD-1660 `SKIPS` lines and the skip branch removed; D7's two-group run re-landed from `e14a81e5` | **SL-1543** (serial) |
| `backend/tests/test_wf699_journey.py` | the skip-line list, `test_d7_is_a_skip_that_names_its_finding_and_is_never_recorded_as_ok`, and `test_wf699_journey_runs_end_to_end`'s asserts updated to the refusal; **no test deleted** | **extends Stage A's edit:** the asserts restored; the D7 split test re-landed, fitted to the real derived list | **SL-1543** (serial) |
| `examples/fremtpl2/README.md` | one dated sentence after `:86` saying the journey stops at D6's refusal (FD-1660) until SL-1696 | that sentence struck with a dated line | **SL-1543** if it edits the README |
| `docs/specs/03-rating-engine.md` | **one dated interim line only**, verbatim from the 08:09:39 entry, appended to FR-264's requirement cell (`:191`) and as its own paragraph at the end of §4.6 (after `:711`); no requirement text | **extends Stage A's edit:** strikes both interim lines in place (dated note citing SL-1696), and writes T1 on FR-1399 and T2 on FR-1398 as RL-1686 adopted them | any open `03` edit: re-anchor by content |
| `docs/ledgers/LG-<working id>-….md` | SL-1695's ledger, with condition (b)'s grep re-run at its base | SL-1696's ledger, with the 02:20:32 lines | — |

**Overlap, stated:** the two rows share **no file that Stage B does not extend from Stage A's
state**. The five shared paths (`analysis.py`, `test_rating_attribution.py`,
`test_quote_input_raise_sites.py`, `journey.py`, `test_wf699_journey.py`) and the README are
written by Stage A first and by Stage B after it merges, and Stage B's change there **starts from
and removes or flips Stage A's additions** (the guard and its class, the guard tests, the raise-site
case, the FD-1660 skip lines and asserts, and the interim `03` line). Nothing else overlaps: T1 and T2 in `docs/specs/03` are Stage B's
alone, and Stage A writes no file Stage B leaves untouched except its own LG.

**Not written by either:** `packages/model-schema/` (no new `DeltaKind` under DP-1 (a));
`docs/contracts/`; `frontend/`; `backend/src/` (RL-1686 DP-W). If an executor finds any of them
must change, that is a STOP for the lead, not a widening.

## Activation needs

**SL-1695 (Stage A):**

1. **RL-1686 on `main`** (D14, #1298) **and PL-1694, SL-1695 and SL-1696 minted**: **met by
   this plan's early-mint PR** (the maintainer's (by delegation) entry "2026-10-12 08:09:39 BST",
   item 3), so the guard's literal and the `SKIPPED` lines carry SL-1696 (condition (a); RL 9852
   DP-W: *"written with the minted id"*). This plan set `active` by a dated line (L1: in the slice PR's first commit).
2. SL-1527 on `main`: **met** (`docs/roadmap.md` SL-1527's closure, `:2121`; `journey.py` and
   `test_wf699_journey.py` exist at `50bbdd96`). RL-1686 corrected the first cut's need 3, which
   said Stage A did not need it.
3. **Serialised with SL-1543** on `examples/fremtpl2/journey.py` and
   `backend/tests/test_wf699_journey.py` (and the README if SL-1543 edits it): the second of the
   two to merge re-merges `main` and re-runs the journey test and the journey run before its ACK
   (02:29:16, item 3).
4. **The interim line is in Stage A's commit with the code** (the maintainer's (by delegation)
   entry "2026-10-12 08:09:39 BST", item 4): the guard and the `03` interim line land in one
   commit (`CLAUDE.md` §2: spec and code in one commit).
5. A free build lane and the single gate at the GO (the maintainer's (by delegation) seat cap;
   `RL-1445` item 1).

**SL-1696 (Stage B):**

1. **SL-1695 merged** (condition (c): *"gated right after Stage A"*; Stage B removes the guard
   Stage A adds, so it cannot be built on a base without it).
2. RL-1686 on `main` (D14, #1298), so T1 and T2 cite it.
3. The salvage sha: **met**, `e14a81e5` (the lead, `from-lead-2026-10-09.md` "2026-10-12
   02:31:03 BST": *"git ls-remote origin refs/heads/salv-sl1527-d7-2group =
   e14a81e55c509de5378858dc84a46f6c5fa03c77"*).
4. Serialised with SL-1543, as Stage A's need 3.
5. A free build lane and the single gate at the GO.

## Acceptance Standard

Each item is a command a fresh reviewer can run on the slice branch, `uv run pytest
packages/pricing-core/tests/test_rating_attribution.py -k <name>` unless another is given. Each
red is recorded in the slice's LG with the commit it was seen at, **by its cause**: a matching
code with a differing cause is a plan defect, reported, never accepted. SL-1696 is Stage B's
row, minted from working id 9850 (Stage A activation need 1).

**SL-1695 (Stage A).**

1. **G1 (L3, silent).** `-k guard_mount_difference` — baseline mounted at
   `sub_graph:ncd-ladder@4`; candidate re-points it to `@5` and makes one rate-table edit
   (`_e_table`); no groups. **On the base:** the run returns, and the test proves the
   misattribution **in numbers**: `derived_changes` holds one change and none names `m_ncd`;
   that change's `shapley_minor` equals `total_change_minor`; and the ladder-only effect,
   computed **independently of attribution** (score the baseline bundle and a bundle that is the
   baseline with only the re-point applied, through `compile_bundle` and the same `_score_pass`,
   over the same book), is non-zero and contained in it: the rate-table change's part minus the
   independently computed table-only effect equals the ladder-only effect plus the interaction,
   the interaction computed and shown, never assumed zero. **This confirms HIGH.** If the base
   refuses or derives a mount change instead, **STOP**: L3 is not real, and the rating reverts to
   MEDIUM by a dated line (02:35:40). **After Stage A:** the run raises; the exception is an
   `AttributionError` with `code == "VALIDATION_FAILED"` **and** a `CodedError`; its text names
   `m_ncd`, `FD-1660` and `SL-1696`.
2. **G2 (L2).** `-k guard_baseline_mount_k2` — baseline and candidate both mount `@4`; the
   candidate adds `_e_table` and `_e_instalment`; no groups, K = 2. **On the base:** the exact
   outcome is recorded — `BUNDLE_COMPILE_FAILED` with `RATING_VERSION_UNPINNED` and the mount
   point in its text, **or a successful compile, with the sub-graph version each compiling subset
   resolved** (from the compiled bundle's `resolved_payloads` keys, or a resolver spy recording
   every `sub_graph` ref resolved per subset slug). A partial subset that compiles against a
   sub-graph version other than the baseline's pin is a **STOP**, reported to the lead **at once**
   (HIGH trigger, 02:34:38). **After Stage A:** as item 1's "after", naming `m_ncd`, and the
   compile spy records no compile.
3. **G3 (DP-G, exemption (i) refused).** `-k guard_one_group_refused` — the demo-shaped
   candidate (a mount added with its consumer edited, plus `_e_instalment`) with **one** group
   holding every derived change. **On the base:** the run returns one attribution item whose
   `shapley_minor` equals `total_change_minor` (recorded: the mislabelled lump DP-G refuses).
   **After Stage A:** refused as item 1's "after", naming `m_ncd`; the compile spy records no
   compile. (Inverted from the first cut's G3, per RL-1686 "What it obliges", DP-G.)
4. **G4 (L1 under the guard).** `-k guard_mount_added_two_groups` — baseline without the mount;
   candidate = the mounted fixture plus `_e_instalment`; groups `structure` (every derived change
   but the instalment one) and `instalment`. **On the base:** `BUNDLE_COMPILE_FAILED` (the
   02:29:16 red), recorded with its inner text, and for each partial subset that **did** compile
   before the failing one, the sub-graph version it resolved, recorded as in item 2 (the same
   STOP). **After Stage A:** refused as item 1's "after", before any compile.
5. **GT (condition (a), the text reaches the Job).** `-k guard_text_survives_safe_error_text` —
   `safe_error_text(exc)` of G1's exception contains `VALIDATION_FAILED`, `FD-1660`, `SL-1696`
   and `m_ncd`. **Red first by cause:** with the guard raising a plain `AttributionError` (the
   intermediate commit of Task 2 Step 1), `safe_error_text` returns `"AttributionError"` alone and
   GT fails; the LG records that red and its commit.
6. **The raise-site enumeration counts the guard.** `uv run pytest
   packages/pricing-core/tests/test_quote_input_raise_sites.py` passes with one new `_INPUT_FREE`
   case for the guard's site; **red first:** with the guard committed and the case absent, the
   enumeration fails naming the site (LG records it). If it does **not** fail without the case,
   the enumerator cannot see the guard's construction, and Task 2 Step 4 applies.
7. **WF-699 D6 asserts the refusal; condition (b).** `uv run pytest
   backend/tests/test_wf699_journey.py` passes with: D6 recorded `ok` only because its Job
   **failed** with `error.code == "VALIDATION_FAILED"` and an `error.message` containing
   `FD-1660` and `SL-1696`; D7 recorded `SKIPPED: SKIPPED D7 — FD-1660 guard`; D8, E4, E6, E8,
   E9, DEP and S1 each recorded `SKIPPED: SKIPPED <step>: FD-1660; SL-1696`; E5 and E7 keep
   their existing Phase-3 lines; `result.rating_version_id is None`, `result.bundle_hash == ""`
   and `result.prod_premium_minor == 0`, each with a comment naming FD-1660 and that SL-1696
   restores the original assert; **no test deleted** (`git diff origin/main...HEAD --
   backend/tests/test_wf699_journey.py | grep -c '^-def test_'` prints 0). **Red first:** the
   updated test against the base's `analysis.py` (no guard) fails at D6 because the Job
   succeeds; the LG records it.
8. **Condition (b)'s grep, at the slice's base.** The LG records both predicates of RL-1686
   DP-W write 3, run verbatim at Stage A's base, with every matched file and its mount count:
   `git grep -l -E 'attribute\(|derive_changes|dislocation-runs|dislocation_run|attribute_' <base> -- 'packages/*/tests' backend/tests frontend/src`
   then, per file, `git grep -c -E 'sub_graph|SubGraphRef|mount_point|m_ncd' <base> -- <file>`.
   At `50bbdd96` (re-run by this planner at 2026-10-12 08:05:25 BST) it matches 6 files (`test_approval_guard_decision.py`, `test_dislocation_runs.py`, `test_rating_version_dislocation_gate.py`, `test_rating_version_evidence_floor.py`, `test_rating_versions.py`, `test_worker_raise_sites.py`, all under `backend/tests/`), of which
   `backend/tests/test_dislocation_runs.py` (1) and
   `backend/tests/test_rating_version_dislocation_gate.py` (5) carry a mount term and neither
   runs D6 on a mount-changing fork, as RL-1686 read them; `test_wf699_journey.py` is named by
   hand (it reaches D6 through `journey.py`). Any new file the predicates match at Stage A's base
   that runs D6 on a mount-changing fork is updated to assert the refusal, never deleted.
9. **No regression.** Every test in `test_rating_attribution.py` that exists at the base passes
   unedited (none carries a mount term at `50bbdd96`: the count is 0); `derive_changes` and the
   estimate route answer for a mounted fork as before (the journey's D6 reaches `POST
   /dislocation-runs` through `derived_changes`, so item 7 proves it).
10. **The interim line, and the gate.** `grep -cF '<the line>' docs/specs/03-rating-engine.md`
    prints 2 (FR-264's cell and §4.6), the line being the 08:09:39 entry's text verbatim (Context,
    above), and `git log --format=%H -1 -S 'Interim, 2026-10-12' -- docs/specs/03-rating-engine.md`
    names the same commit as the guard's (`git log -1 -S '_MountNotYetAttributable' --
    packages/pricing-core/src`). Both halves of `CLAUDE.md` §11 at the slice head, in a gate slot, rc 0 each;
    `python3 scripts/audit-docs.py` exit 0 (check 31's working-id gap excepted only if a working
    id remains, which need 1 is meant to prevent).

**SL-1696 (Stage B).**

11. **R1 (L1).** G4's test flipped, `-k mount_added_two_groups`: the run returns;
    `method == "shapley"`; the two `shapley_minor` sum to `total_change_minor`; isolated plus
    residual equals the total.
12. **R2 (L2).** G2's test flipped: the run returns and reconciles; the subset bundles inline the
    baseline's mount at `@4` (asserted on the compiled graph's node ids, as
    `test_rating_compile_bundle.py:371-375` does).
13. **R3 (L3).** G1's test flipped: exactly one derived change names `m_ncd`, kind
    `step_changed`, description `m_ncd: mount sub_graph:ncd-ladder@4 → sub_graph:ncd-ladder@5`,
    carrying the sub-graph pin difference (no separate `pin` change for either ref); its isolated
    part equals item 1's independently computed ladder-only effect, and the rate-table change's
    isolated part equals the independently computed table-only effect; the two Shapley parts
    split the interaction as FR-266's Shapley rule does, and sum to the total.
14. **R4 (DP-3).** `-k mount_and_its_consumer_ungrouped` — the mount change and the step that
    consumes its output in different groups: `VALIDATION_FAILED` naming the pair; the compile spy
    records no compile.
15. **G3 flipped.** The one-group run returns one item equal to the total, and its group's
    members include the `m_ncd` change (the label is now right).
16. **No regression, and the guard gone.** Item 9 again; the derived lists of the no-mount
    fixtures are identical (ids, kinds, descriptions); `git grep -n FD-1660 --
    packages/pricing-core/src` returns nothing; the guard's `_INPUT_FREE` case is gone and the
    raise-site test passes.
17. **Empty and full subsets.** With a mounted candidate, the empty subset's bundle hash equals
    the baseline's and the full subset's the candidate's (the pattern of
    `test_empty_and_full_subsets_hash_equal_baseline_and_candidate`, `:442`).
18. **WF-699 D7 decomposes.** `uv run pytest backend/tests/test_wf699_journey.py` passes with
    every FD-1660 line absent from `journey.SKIPS` and from the skip-line test; D6 to S1 recorded
    `ok` again (E5 and E7 keep their Phase-3 lines); `test_wf699_journey_runs_end_to_end`'s
    `rating_version_id`, `bundle_hash` and `prod_premium_minor` asserts restored to their
    `50bbdd96` form; and the D7 split test built on the **real** derived list (ids, kinds,
    descriptions copied from a run of the fixed code: the salvage's hand-written `c6` row, kind
    `pin`, description `sub_graphs pin sub_graph:ncd-ladder@1 added`, is not what DP-2 (i)
    derives and is replaced; the mount's description is DP-1's `m_ncd: mount added
    (sub_graph:ncd-ladder@1)`). The journey run prints D7 as done with ≥ 2 groups, each present,
    Shapley sum == `total_change_minor`, isolated + residual == total, and the stored
    `change_groups` partition `derived_changes`, each id in exactly one group.
19. **The 02:20:32 lines.** The LG carries, one line each: why ladder vs lookup is not separable
    (`s_premium` consumes both; `_check_dependence`, DP-3), and whether the minimum-premium effect
    is exercised by the fork (a zero-effect group or one line saying so).
20. **Spec and contracts.** Both interim lines are struck in place (`~~…~~`, a dated note
    citing SL-1696), and T1 and T2 appear in `03` exactly as RL-1686 adopted them, `<RL>`
    filled with `RL-1686` and `<date>` with the applying date; `python3 scripts/audit-docs.py`
    and `uv run python scripts/req-coverage.py` exit 0; `uv run python
    scripts/generate-contracts.py --check` exits 0 and `git diff --name-only origin/main...HEAD
    -- docs/contracts` is empty.
21. **Gate.** As item 10, at Stage B's head.

## Global Constraints

- Money is integer minor units; attribution's arithmetic is not changed (FR-1397, NFR-496).
- `pricing-core` imports no FastAPI, SQLAlchemy or Redis (`CLAUDE.md` §2); `lint-imports` passes.
- No pandas (`CLAUDE.md` §3).
- A subset bundle stays ephemeral and is never a `rating_version` row (FR-1398).
- Requirement ids are not renumbered; T1 and T2 are dated appends (`CLAUDE.md` §5).
- The guard refuses; it never returns a partial report (02:35:40).
- The guard's text is input-free: a fixed literal plus `mount_point`s, which are authored
  identifiers held to `_MOUNT_POINT` (`model_schema/rating.py` `SubGraphRef.mount_point`), never a
  quote value (NFR-499; RL-1686 DP-W).

## Tasks

### SL-1695 (Stage A, the guard)

#### Task 1 — the fixtures and the reds, on the base, by cause

**Files:** `packages/pricing-core/tests/test_rating_attribution.py` only.

- [ ] **Step 1.** Build the mounted fixture by mirroring `_compiled_with_a_mounted_sub_graph`
  (`packages/pricing-core/tests/test_rating_score.py:950-990`): the `score-fixture` algorithm
  with an `ncd_years` input, an `s_in_ncd` input step, a mount `m_ncd` of
  `sub_graph:ncd-ladder@4` mapping `ncd_years` in and `ncd_factor` out, `s_office` consuming
  `ncd_factor`, and the fragment payload in the resolver with status `no_maturity_concept` (as
  `test_rating_compile_bundle.py:357-367` does). A second fragment `@5` differs only in its
  constant. Use this file's `_run` (`:148`), `_spec` (`:133`), `_book` (`:119`) and
  `_CompileSpy` (`:169`); `_candidate_version` (`:106-117`) builds `Pins` without `sub_graphs`,
  so extend it with an optional sub-graph pin rather than writing a second helper (README rule
  3). Do not use `_e_office` on a mounted fixture: it rewrites `s_office`'s `expr` and drops
  `ncd_factor`.
- [ ] **Step 2.** Write G1, G2, G3 and G4 with their **base** outcomes asserted (items 1–4, "on
  the base"), plus GT asserting its after-state.
- [ ] **Step 3.** Run them on the base. Record each limb's outcome exactly in the LG: the error
  code and text, or the returned figures, and for **every** partial subset that compiled, the
  sub-graph version it resolved. **STOP and report to the lead at once** if any partial subset
  compiled against a sub-graph version other than the baseline's pin (HIGH trigger, 02:34:38),
  if any limb is green on the base, or if one fails by another cause than the one stated.
- [ ] **Step 4.** Commit (`test(rating): …`).

#### Task 2 — the guard, coded so its text reaches the Job

**Files:** `analysis.py`, the test file, `test_quote_input_raise_sites.py`.

- [ ] **Step 1 (the intermediate red for GT).** Flip G1–G4's assertions to their "after Stage
  A" outcomes. In `attribute`, after `groups = _check_groups(changes, spec.change_groups)`
  (`:986`) and before `_check_dependence(derivation, groups)` (`:987`), add the guard raising a
  **plain** `AttributionError("VALIDATION_FAILED", <text>)`. G1–G4 go green; **GT stays red**
  (`safe_error_text` gives `"AttributionError"`). Record GT's red and its commit in the LG.
- [ ] **Step 2.** Declare the coded class beside `AttributionError` and raise it instead:

  ```python
  class _MountNotYetAttributable(AttributionError, CodedError):
      """FD-1660's guard (RL-1686 DP-W): an `AttributionError` (code `VALIDATION_FAILED`) that is
      also a `CodedError`, so `safe_error_text` keeps its text and the Dislocation Job's error
      names the finding. The text is a fixed literal plus `mount_point`s (authored identifiers),
      never a quote value (NFR-499). SL-1696 removes it."""

      def __init__(self, reason: str, mount_points: Sequence[str]) -> None:
          super().__init__(
              "VALIDATION_FAILED",
              "VALIDATION_FAILED: sub-graph mount differences are not yet attributable (FD-1660); "
              "attribution of sub-graph mount changes is unavailable until SL-1696. "
              f"{reason}: {', '.join(sorted(mount_points))}",
          )
  ```

  `reason` is one of two fixed literals, so the text stays input-free: `"a mount differs"` (the
  first limb: `diff_algorithms(baseline_alg, candidate_alg).sub_graph_mounts` non-empty, its
  entries' `mount_point`s) and `"a sub-graph is mounted and two or more groups are declared"`
  (the second limb: either algorithm has `sub_graphs` and `len(groups) >= 2`, the mounted
  `mount_point`s of both sides). The first limb is checked first. `CodedError` is imported from
  `pricing_core.safe_error` (as `inline.py:48` does). The literal names SL-1696 as written above.
  GT green.
- [ ] **Step 2b (same commit as Step 2's code).** Append the 08:09:39 entry's interim line
  (Context, verbatim, starting `(Interim, 2026-10-12,`) to the end of FR-264's requirement cell
  in `docs/specs/03-rating-engine.md` (`:191`, re-anchor by content), as ` *<line>*` before the
  cell's closing `|`, and as its own paragraph at the end of §4.6 `DislocationRun` (after the
  `exposure_years` paragraph, `:711`). No other `03` text. Run `python3 scripts/audit-docs.py`
  once in the gate-2 slot; commit the guard, GT and the two lines together.
- [ ] **Step 3.** Run `test_quote_input_raise_sites.py` **without** a new case: it must fail
  naming `("rating/analysis.py", <the function holding the raise>)`. Record the red. Add the
  case with a one-line reason (*"FD-1660's guard: a fixed literal and mount points, never a
  value"*). Green.
- [ ] **Step 4 (only if Step 3 did not fail).** The enumerator cannot see a subclass
  construction (`_SITE_NAMES`, `:122`, lists call names). Add `"_MountNotYetAttributable"` to
  `_SITE_NAMES`, see the test fail naming the site, then add the case. A coded error the
  enumeration cannot see is the defect it exists to prevent, so this is not optional.
- [ ] **Step 5.** One comment line at the guard cites FD-1660 and says SL-1696
  removes it. `uv run mypy`, `uv run ruff check`, `uv run lint-imports`; item 9. Commit
  (`fix(rating): …`).

#### Task 3 — the journey asserts the refusal (condition (b))

**Files:** `examples/fremtpl2/journey.py`, `backend/tests/test_wf699_journey.py`,
`examples/fremtpl2/README.md`.

- [ ] **Step 1.** Re-run condition (b)'s two predicates at the slice's base (item 8) and write
  the result into the LG. Update any newly matched file that runs D6 on a mount-changing fork.
- [ ] **Step 2.** In `journey.py`'s `SKIPS` (`:72-86`): replace
  `Skip("D7", "SKIPPED D7 decomposition — FD 9804")` and its comment (`:80-85`) with
  `Skip("D7", "SKIPPED D7 — FD-1660 guard")` (the 02:43:49 entry's line, with the finding's minted id) and a
  comment citing FD-1660, the 07:44:13 entry's (A) and SL-1696; add
  `Skip(step, f"SKIPPED {step}: FD-1660; SL-1696")` for D8, E4, E6, E8, E9, DEP and S1, each a
  literal string. E5 and E7 keep their Phase-3 lines. Update the `_OWNER` comment (`:88`): the
  working-id example `FD 9804` becomes a historical note, the pattern unchanged.
- [ ] **Step 3.** In `dislocation()` (`:1036-1082`): keep the one-group spec and `POST
  /dislocation-runs` (expect 202); replace `job_ok` with `job` and assert the refusal:

  ```python
  job = self.job("D6", "analyst", accepted)
  error = job.get("error") or {}
  message = str(error.get("message", ""))
  if (
      job["status"] != "failed"
      or error.get("code") != "VALIDATION_FAILED"
      or "FD-1660" not in message
      or "SL-1696" not in message
  ):
      raise JourneyStepFailed("D6", "FD_1660_GUARD_NOT_RAISED", detail=message)
  self.done("D6", "refused VALIDATION_FAILED: sub-graph mount changes are not attributable "
            "until SL-1696 (FD-1660); a 20,000-policy sample of the freMTPL2 book")
  self.attribution_refused = True
  self.skip("D7")
  self.skip("D8")
  self.skip("D9")
  ```

  Remove the D7 run read, the movers read, the one-effect log line and `done("D8", …)`; set
  `self.attribution_refused = False` in `__init__`. Replace the `:1045-1057` comment with one
  citing FD-1660, the 07:44:13 entry's (A) and SL-1696.
- [ ] **Step 4.** In `phase_e` after `self.dislocation()` (`:966`): when
  `self.attribution_refused`, skip E4, E5, E6, E7, E8 and E9 **without** their live calls (E5's
  `decide` and E7's `submit` need E4's approval request) and return. In `deploy_and_score`
  (`:1084`): when `self.attribution_refused`, skip DEP and S1 and return. One comment at each
  branch cites FD-1660 and SL-1696.
- [ ] **Step 5.** In `test_wf699_journey.py`: the skip-line list (`:38-55`) loses
  `"SKIPPED D7 decomposition — FD 9804"` and gains the eight FD-1660 lines;
  `test_d7_is_a_skip_that_names_its_finding_and_is_never_recorded_as_ok` (`:462-473`) asserts
  the new D7 line and its docstring cites the 02:43:49 and 07:44:13 entries; in
  `test_wf699_journey_runs_end_to_end` (`:339-394`), the deliberate-failure loop
  (`("B6", "C4", "E3", "D4", "E8")`) becomes `("B6", "C4", "E3", "D4", "D6")` (E8 is now a
  skip; D6 is now an asserted refusal), and the three result asserts become
  `rating_version_id is None`, `bundle_hash == ""`, `prod_premium_minor == 0`, each with a
  comment naming FD-1660 and that SL-1696 restores the original. The `"20,000-policy sample"`
  assert stays (D6's note keeps it). **No test is deleted.**
- [ ] **Step 6.** README: after `:86`, one dated sentence: *"(2026-10-12, FD-1660: until
  SL-1696 merges, attribution refuses a version that changes a sub-graph mount, so the journey's
  D6 asserts that refusal and the steps that need its run — D7, D8, E4 to E9, DEP and S1 — are
  printed `SKIPPED` with the finding.)"*
- [ ] **Step 7.** Item 7's red first (the updated test against the base's `analysis.py`, D6's Job
  succeeds), then green on the guard. `uv run pytest backend/tests/test_wf699_journey.py`; the
  journey run once (`scripts/demo.py --journey wf-699` per `dev-commands`, or the lead's named
  substitute), its D6 line copied into the LG. Commit (`test(journey): …`).

#### Task 4 — gate, LG, PR (Stage A)

- [ ] Full gate in a slot (item 10); the LG names the tree. Before the PR: `gh pr list --state
  open` and a read of anything ruling on attribution, sub-graphs or `journey.py` (README rule 4),
  naming the commit read. The PR closes SL-1695 only; FD-1660 stays open until SL-1696.

### SL-1696 (Stage B, the fix), gated right after SL-1695 merges

#### Task 1 — T1 and T2, spec first

**Files:** `docs/specs/03-rating-engine.md`.

- [ ] Merge `main` (holding SL-1695). Strike both interim lines (FR-264's cell, §4.6) in place
  with `~~…~~` and a dated note citing SL-1696 (the 08:09:39 entry: *"Stage B (SL-1696) STRIKES
  that line in place when it writes T1/T2"*). Append T1 to FR-1399 and T2 to FR-1398 **verbatim as
  RL-1686 §DP-T adopted them** (not the first cut's drafts), `<RL>` = `RL-1686`, `<date>` the
  applying date; run `python3 scripts/audit-docs.py` once in the gate-2 slot (`dev-commands`).
  Commit (`docs(specs): …`).

#### Task 2 — derive the mount (DP-1 (a), DP-2 (i) pins)

**Files:** `analysis.py`, the test file.

- [ ] **Step 1.** Flip G1 to R3 (item 13) and see it red against the guard (`VALIDATION_FAILED`,
  by that cause).
- [ ] **Step 2.** `_PIN_KINDS` gains `"sub_graphs"` (`:484-489`).
- [ ] **Step 3.** In `_derive`, after the step-draft loop (`:576-600`), add one draft per
  `diff.sub_graph_mounts` entry, keyed by `mount_point`, kind `step_added` / `step_removed` /
  `step_changed`, carrying the old and new `SubGraphRef`, with DP-1's description forms; sort the
  drafts by id so a mount sits among the steps (T1). Add each mount draft's refs to `step_refs`
  (`:603-609`) so its sub-graph pin difference is part of it. A mount change never enters the
  steps' `applied` map.
- [ ] **Step 4.** Remove the guard's first limb. R3 green; item 16's no-mount lists. Commit.

#### Task 3 — the subset and the dependence (DP-2 (i), DP-3 (i))

**Files:** `analysis.py`, the test file, `test_quote_input_raise_sites.py`.

- [ ] **Step 1.** Flip G2 to R2, G4 to R1, G3 to item 15; write R4; see each red by its cause
  against the remaining guard limb (`VALIDATION_FAILED`), and R4 also by the absence of the pair.
- [ ] **Step 2.** `_subset_algorithm` (`:742-765`): add `"sub_graphs": _merged(base.sub_graphs,
  cand.sub_graphs, lambda m: m.mount_point, mounts_applied)` to the update, where
  `mounts_applied` maps each member mount change's `mount_point` to its `_APPLIED` value.
- [ ] **Step 3.** `_subset_pins` (`:768-799`): `needed["sub_graphs"]` gains each
  `algorithm.sub_graphs` mount's `ref` (the loop at `:783-785` reads steps only).
- [ ] **Step 4.** `_check_dependence` (`:816-876`): the subset's mounts, merged as in Step 2,
  join `produced` (their `outputs` values) and are checked as consumers (their `inputs` values);
  the producer search also finds a mount change whose new or old mount maps the name out. The
  refusal text is unchanged in form.
- [ ] **Step 5.** Remove the rest of the guard, `_MountNotYetAttributable`, GT and the guard's
  `_INPUT_FREE` case (and its `_SITE_NAMES` entry if Stage A added one). R1, R2, R4, item 15
  green; items 16 and 17; `uv run mypy`, `uv run ruff check`. Commit.

#### Task 4 — D7 decomposes (serial with SL-1543)

**Files:** `examples/fremtpl2/journey.py`, `backend/tests/test_wf699_journey.py`,
`examples/fremtpl2/README.md`.

- [ ] **Step 1.** Merge `main` (and SL-1543 if it merged first). Remove Stage A's FD-1660
  `SKIPS` lines, the `attribution_refused` branches and D6's refusal assertion; restore D6 to
  `job_ok`. Re-land from `e14a81e5`: `run_dislocation`, `split_effects`, `EFFECT_RATE_TABLES`,
  `EFFECT_STRUCTURE`, the two-run D7 block and
  `test_d7_splits_the_derived_changes_into_the_journeys_own_effects`. Remove
  `test_d7_is_a_skip_that_names_its_finding_and_is_never_recorded_as_ok`'s skip assertion by
  turning it into the D7-is-`ok` assertion (no test deleted). Restore
  `test_wf699_journey_runs_end_to_end`'s loop and result asserts to their `50bbdd96` form. Strike
  the README sentence with a dated line. Leave SL-1527's `_OWNER` pattern as merged.
- [ ] **Step 2.** Run the journey once against the fixed code and copy the real
  `derived_changes` into the split test's fixture (item 18). Check that `split_effects` puts the
  mount change in the structure effect (its kind is not `table_repointed`).
- [ ] **Step 3.** Write the two 02:20:32 lines into the LG (item 19).
- [ ] **Step 4.** Run `test_wf699_journey.py` and the journey run; commit.

#### Task 5 — gate, LG, PR (Stage B)

- [ ] Full gate in a slot (item 21); the LG names the tree. Before the PR: `gh pr list --state
  open` and a read of anything ruling on attribution, sub-graphs or `journey.py`, naming the
  commit read. The PR's LG proposes FD-1660's discharge to the auditor.

## NFR clause

No timing NFR is added or touched. **NFR-499** (Stage A): the guard's text is a fixed literal
plus `mount_point`s; GT and the raise-site enumeration (items 5, 6) prove it is kept and counted.
**NFR-495** (determinism, Stage B): a subset bundle with a mount is content-hashed by the same
`compile_bundle`; item 17 re-proves the empty and full hashes. **NFR-496** (money exactness,
Stage B): the allocation and reconciliation code is not edited; items 11–13 re-prove
reconciliation on mounted runs. **Cost:** the guard refuses before any compile, so a refused run
costs the dislocation pass plus one structural diff. Under DP-1 (a) each mount difference is one
more derived change, so an **ungrouped** run's K rises by one per mount difference
(`estimate_attribution_ratings`: 2^K × policies, or (3K − 2) × policies above 6). The demo groups
to two, so D7 rates 4 × the 20,000-policy sample (`PL-1577`); the full-book cost stays FD-1576's.

## Gate and merge order

1. D14 (#1298, holding RL-1686) merges; then this plan's early-mint PR (PL-1694, SL-1695,
   SL-1696) merges after it (Stage A activation need 1).
2. **SL-1695 (Stage A)** is dispatched at once after that, serialised with SL-1543 on
   `journey.py` / `test_wf699_journey.py`: whichever merges second re-merges `main` and re-runs
   the journey test and the journey run before its ACK. Neither waits for the other to start.
3. **SL-1696 (Stage B)** is gated **right after SL-1695 merges** (condition (c)), on WK-673's
   lane, as the G2 item it is; the same serialisation with SL-1543 applies if SL-1543 has not
   merged by then.
4. G2 is declared only after SL-1543, SL-1695 and SL-1696 have merged (the lead's D13 delta line,
   `docs/roadmap.md:569`, names SL-1696; SL-1695 precedes it by need 1). FD-1660, HIGH in P2,
   needs its resolution before any P3 start (the rule of `CLAUDE.md` §14, applied by the 02:35:40 entry); SL-1695 is the interim
   mitigation, SL-1696 the resolution.

## Self-review (before freeze)

- Every `file:line` above was read at `50bbdd96`; `analysis.py` is byte-identical to `fc4401dc`
  (the diff command in the header), so RL-1686's locators hold; the salvage branch at `e14a81e5`.
- RL-1686 "What it obliges" for the planner, item by item: DP-G — Task 2 loses the exemption,
  G3 inverted, the row loses the exemption clause, the D7 line is "SKIPPED D7 — FD-1660 guard"
  (done); DP-S (i) — two rows, Stage B gated after Stage A, sequencing merged into one RL (done);
  DP-W — Stage A's write set is write 1 (coded error), write 2 (journey and test), write 3 (grep in
  the LG), `backend/src/` not written; acceptance 5 of the first cut (journey "unedited") replaced
  by item 7; items 1, 2, 4 name FD-1660 and SL-1696 and item 5 proves `safe_error_text` keeps it;
  activation need 3 corrected (done); DP-1 descriptions in items 13 and 18 (done); DP-T applied
  as adopted (Stage B Task 1, done).
- **The journey's step list, confirmed against `50bbdd96` as RL-1686 asked:** RL-1686 names D7,
  D8, E4, E6, E8, E9 and DEP. **S1 is added** (`deploy_and_score`, `journey.py:1125-1190`, scores
  from `prod`'s live deployment of `rv3`, which DEP no longer makes). E5 and E7 keep their
  existing Phase-3 `SKIPS` lines (one entry per step, `skip()` at `:249-252`), but their live
  calls cannot run, so Task 3 Step 4 skips them without the calls. D9 is already a skip.
- **One design detail chosen here, inside RL-1686 DP-W:** the guard's text carries one of two
  fixed reason clauses (a mount differs; mounted with K ≥ 2) after the ruled three-part literal,
  because limb 2 fires with no mount difference and the literal alone would describe it
  inaccurately. Both are fixed literals, so the text stays input-free. The lead may strike it.
- The rulings' subjects (the guard; sub-graph mounts in attribution; the journey's refusal) were
  grepped across this file's site classes: Context, slice rows, Write set, activation needs,
  Acceptance 1–21, Tasks.
- The interim `03` line: first written "none" (the lead's recommendation), **reversed** by the
  maintainer (by delegation), 08:09:39 item 4; applied in Context, Write set, activation need 4,
  Acceptance 10 and 20, Stage A Task 2 Step 2b and Stage B Task 1.
- Open: none of the plan's DPs. Not this plan's: (B) (the decision-maker's, if Stage B slips). This plan stays `draft` until set `active` at activation.
