---
id: RL-1686
family: ruling
title: PL 9807 decided — a sub-graph mount is derived like a step by its mount_point, a subset carries its own mount changes and their pins, and a mount is a node for dependence (the FD-1660 fix: the guard as its own slice, then the fix; DP-G and its consequence recorded as the maintainer's)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-12
owner: decision-maker
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FD-1660, PL-1267, SL-1387, RL-1449, RL-1309, RL-1344, RL-1571, FR-217, FR-218, FR-219, FR-237, FR-266, FR-1397, FR-1398, FR-1399]
---

# RL-1686 — PL 9807's decision points: how attribution carries a sub-graph mount

*Minted 2026-10-12 as RL-1686 from working id 9852. "RL 9852" below, inside a quoted entry, is
this record's working id.*

*Disclosure: drafted under **working id 9852**, reserved by the lead (team-lead) on 2026-10-12
(`~/gi-pricing-plan.local/handover/eta.md`, the line stamped "2026-10-12 02:43:04 BST":
"RL 9852 = the decision-maker's ruling on PL 9807's DPs"). The plan it rules (working id 9807),
the slices it names (working ids 9850 and 9851) are unminted, so they are cited as "working id
NNNN" in the body and are not in `relates:`; when they are minted, the working ids in this
record are replaced by the minted ids. The finding it fixes was reserved as working id 9804 and
is minted as `FD-1660` (#1290, `249670fe`), so this record cites `FD-1660` except inside
verbatim quotes, which keep "FD 9804".*

## How this was ruled

- **The decision points are PL 9807's** (working id; branch
  `pl-9807-wk673-subgraph-attribution-2026-10-12` at
  `e788950f897dd7093b260a614d1bd689a95c968f`, tree `7d12074f84b76e4899b1a7e6c45ffefe12c1e110`),
  §"Decision points". This record rules them as `document-ids.md` §1.6's PL row requires
  (*"decision-maker rules decision points as `RL-`, never edits the plan"*). It does not edit
  the plan; what the plan must change to follow these rulings is listed under "What it
  obliges".
- **DP-G is not this record's.** The maintainer (by delegation) settled it in the entry of
  `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-12 02:43:49 BST" (quoted whole
  below), and that entry gave the other six to this role: *"DP-S/W/1/2/3/T are the
  decision-maker's. DP-G's scope is settled here, because it is the reading of my own guard."*
  The rulings below are written to agree with it.
- **Written 2026-10-12 from 02:53 BST (by `TZ=Europe/London date`)** by the decision-maker
  seat `dm-wk673-c`. **Every `file:line` below was read at `origin/main`
  `fc4401dcad789692f79f6c3ffc058c1c3921b7b9`** (#1288), in this record's worktree, unless a
  branch or commit is named. **DP-S and DP-W were finalised from 07:48 BST**, after the
  maintainer's entry "2026-10-12 07:44:13 BST" answered the question that held them. The branch
  then merged `origin/main` `50bbdd96b2154cb4eb79ccf91658191e51ab8906` to carry `FD-1660`. The
  journey and test locators in DP-W were read at `50bbdd96` and say so. The two channel files cited are local, so a repository reader
  cannot open them (RFC-777): each entry this record relies on is quoted.
- **Effort.** The role's default is medium; a decision-maker ruling runs at high on the
  maintainer's raise (`.claude/roles/decision-maker.md:13`). The raise was routed by the
  maintainer (by delegation) in the to-lead entry "2026-10-12 02:26:23 BST" (a separate CLI
  process with `--effort high`, verified by the transcript field) and applied to this seat in
  the 02:43:49 BST entry (*"Effort: (ii) HIGH, a separate CLI with transcript verification"*).
  It is in force for this record, on two checks:
  - **the process command line**, read by this seat from its parent process (pid 713943):
    `claude --model opus --effort high --name dm-wk673-c --dangerously-skip-permissions …`;
  - **the transcript** `~/.claude/projects/-home-puzhenhao1989-gi-pricing-plan/ebff3a3d-62b6-49f2-bf90-27393ea72166.jsonl`:
    the lead read `"effort":"high"` ×13 and `"perTurnEffort":"high"` ×13 with `requestedModel`
    `claude-opus-5-5` (from-lead "2026-10-12 02:47:53 BST", sent to this seat), and this seat
    re-read it at 02:48:02 BST: `"perTurnEffort":"high"` ×24, `"effort":"high"` ×24,
    `"requestedModel":"claude-opus-5-5"` ×24, and no other value of either field.
  - **The route that failed first.** Two seats spawned through the Agent tool with its effort
    parameter set read medium: this seat re-read both transcripts at 02:53 BST,
    `92d4dee8-193d-45d7-bd24-bcbec2aff94f.jsonl` (`"perTurnEffort":"medium"` ×19) and
    `7efcf3a0-76e3-491f-93f4-e9a5b446451f.jsonl` (`"perTurnEffort":"medium"` ×40), no `high`
    in either.

### The maintainer's entry that settles DP-G, quoted whole

From `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed **"2026-10-12 02:43:49 BST —
DP-G: exemption (i) REFUSED; it re-opens limb 1. The guard refuses ANY attribution when baseline
and candidate differ in sub-graph mounts, at any K. Code (a) VALIDATION_FAILED is fine.
dm-wk673-c at (ii) HIGH, separate CLI"**:

> Why (i) fails: a group is reported BY ITS MEMBERS. Take limb 1's own case: a ladder re-point @4→@5 plus one rate-table edit. Derived changes = {the rate-table edit}, because the mount is never derived. Exemption (i) admits it as "one group holding every derived change", and the report attributes the total, ladder effect included, to a group whose only member is the rate-table edit. That is exactly the silent misattribution, now with one group. "Effect == true total" is right; the LABEL is wrong.
> The guard, as I mean my 02:35:40 (this supersedes its "K≥2" clause):
> - REFUSE when the derived diff carries ANY sub_graph_mounts difference (add, remove, re-point, re-map), at ANY K, including K=0 and K=1.
> - ALSO refuse when either side mounts a sub-graph and K≥2 (limb 2; loud today, kept consistent).
> - Code VALIDATION_FAILED (FR-1399's refusal, no new code). The message names "sub-graph mount differences are not yet attributable" and FD 9804.
> - In attribute after _check_groups, as planned, so derive_changes, the estimate and D6's dislocation are untouched.
> What that does to the demo: the fork ADDS the ladder mount, so the guard refuses SL-1527's one-group D7. That costs G2 NOTHING, because G2 already waits on Stage B.
> - Order: SL-1527 merges as ruled (one group, "SKIPPED D7 decomposition — FD 9804"), since it is disclosed and temporary.
> - The guard slice, merging after it, changes the journey's D7 to assert the refusal and print "SKIPPED D7 — FD 9804 guard". It is serialised on journey.py / test_wf699_journey.py as planned.
> - Stage B restores the 2-group split from the salvage branch.
> Effort: (ii) HIGH, a separate CLI with transcript verification (the 02:26:23 route), as you recommend. Brief it with this entry. DP-S/W/1/2/3/T are the decision-maker's. DP-G's scope is settled here, because it is the reading of my own guard.

## Locators — read at `fc4401dc`

| Fact | Where |
|---|---|
| The pin kinds attribution reads have no `sub_graphs` | `packages/pricing-core/src/pricing_core/rating/analysis.py` `_PIN_KINDS` `:484-489` |
| `_derive` builds changes from steps (`:575-600`), then pin differences over `_PIN_KINDS` not accounted for by a step's reference (`step_refs` `:603-609`, loop `:612-619`), then contract and output deltas; it never reads `diff.sub_graph_mounts`. A version-level difference no change can carry (`model_reference_mode`) is refused `VALIDATION_FAILED` (`:563-568`) | `analysis.py` `_derive` `:559-674`; `derive_changes` `:685` |
| A partial subset is the baseline with the members' step, contract and output differences applied by `_merged`, keyed by name; `sub_graphs` is not in the update, so it stays the baseline's | `analysis.py` `_merged` `:727-739`; `_subset_algorithm` `:742-765` (update `:757-764`); empty `:748-749`, full `:750-751` |
| A partial subset's pins are rebuilt over `_PIN_KINDS` only, so they carry no `sub_graphs` | `analysis.py` `_subset_pins` `:768-799` (`Pins(**lists)` `:799`) |
| Compile refuses a mount whose version is not in `pins.sub_graphs`; that list is the only source it reads | `packages/pricing-core/src/pricing_core/rating/inline.py` `mounted_fragments` `:190-225` (`pinned` `:201`, refusal `:209-214`) |
| Dependence is checked over steps only: `produced` is the subset's step outputs, the consumer is found by `step_id` | `analysis.py` `_check_dependence` `:816-876` (`produced` `:829`, consumer `:834`) |
| The guard's site: after `_check_groups`, before `_check_dependence` | `analysis.py` `attribute` `:972`, `:986-987` |
| A mount is a node: it consumes the parent values its `inputs` map to and produces the parent names its `outputs` map to | `packages/model-schema/src/model_schema/rating.py` `SubGraphRef` `:446-468` (docstring `:447-454`); `_MountNode` `:472-478` |
| A `mount_point` is unique among the `step_id`s and the other mounts | `rating.py` `:641-654` |
| The diff names each mount added, removed, re-pointed or re-mapped, by `mount_point`, with `before`, `after` and `ports_changed` | `rating.py` `AlgorithmSubGraphChange` `:805-819`; `AlgorithmDiff.sub_graph_mounts` `:860`; `_diff_mounts` `:936-975`; `diff_algorithms` `:978` |
| `Pins.sub_graphs` exists | `rating.py` `Pins` `:70-85` |
| The derived-change kinds, closed | `packages/model-schema/src/model_schema/dislocation.py` `DeltaKind` `:135-143`; `docs/contracts/schemas/dislocation-run.schema.json` `:101` |
| FR-1398, FR-1399, FR-266, FR-218 | `docs/specs/03-rating-engine.md` `:195`, `:196`, `:193`, `:87` |
| The worker runs attribution inside the dislocation Job and fails the Job on `AttributionError`, before anything is persisted | `backend/src/app/worker/dislocation_handlers.py` `:311-321`; `persist` `:325` |
| Submission requires a Dislocation Run against the baseline (FR-257 limb (2)) | `backend/src/app/platform/rating_versions.py` `_dislocation_gate` `:994`; `dislocation_run_verified` `:1253-1259` |

## `CLAUDE.md` §0 — which of spec and code was wrong

The plan says the spec is silent on mounts (PL 9807 §"The spec is silent on mounts"). Read
limb by limb, that is right for the mount and partly wrong for the pins:

- **L2 (pins): the code is short of the spec.** FR-1398 builds a subset *"from the baseline's
  pins"*, and FR-218's 2026-09-30 amendment (`RL-1344`) says a mount's exact sub-graph version
  *"is pinned in the Rating Version's pins like every other mount"*. The baseline's pins
  therefore include its `sub_graphs` pins, and `_subset_pins` drops them (`:799`). The spec is
  right but implicit; T2 makes it explicit.
- **L3 (the mount): the spec is silent.** FR-1399 derives changes from `step_id`s; a mount is
  not a step. Whether a `sub_graphs` pin difference is a `pin` change under FR-1399's pin clause
  is unclear by text (that clause cites FR-237, whose list names no sub-graph). Even if the
  clause were read to cover it, a `pin` change alone would not fix L3: a subset holding the new
  pin with no mount change is the baseline graph, so the mount's effect would still fall on the
  other change. A mount difference is a capability FR-1399 does not specify, so the fix is a
  spec change first (T1), as the plan says.
- **L1 follows from L3.** With no mount change, there is nothing for `_subset_algorithm` to
  apply. FR-1398's *"with that subset's changes substituted"* is right once a mount is a change.
- **The guard (DP-G) does not contradict the spec silently.** Its first limb is FR-1399's
  existing refusal of *"a difference between baseline and candidate that no derived change can
  carry"*: until T1, a mount difference is one. Its second limb refuses runs that FR-1398 says
  must be attributed. That shortfall is `FD-1660`'s, recorded and disclosed, and
  Stage B removes it. Whether Stage A also needs a dated interim note in `03` (precedent:
  FR-218's interim refusal, `RL-1242`) is **not ruled here**. PL 9807 lists no such option. It
  was put to the lead at 02:50:48 BST (`from-dm-wk673-c.md`), and the 07:44:13 entry does not
  answer it. Under (A) it now also covers D6's Job refusing a mount-changing version, so it is
  raised again with this record's report. It stays the lead's.

**Code read, not a test (for the HIGH trigger of 02:34:38).** A partial subset can compile a
mount only if `pins.sub_graphs` names that exact version (`inline.py:201`, `:209-214`), and a
partial subset's pins have no `sub_graphs` (`analysis.py:799`). So at `fc4401dc` no partial
subset can compile a mount against another version: L2 fails loudly. The test in PL 9807's
Task 1 decides this; this record does not rate severity.

## DP-S — one PR or two

**(i): Stage A, the guard, is its own slice, under working id SL 9851 (reserved); Stage B, the
fix, stays SL 9850 (working id) and is gated right after Stage A merges.**

- **The premise is settled.** DP-S waited on whether the guard may fail D6's whole run (see
  "The question put to the lead, and its answer" below). The maintainer (by delegation) ruled
  (A) in the entry "2026-10-12 07:44:13 BST": the guard stays as settled, and D6's Job fails,
  loudly, for a mount-changing version until Stage B. (C), which is DP-S (ii), is refused there
  in terms: *"(C) is refused: it keeps a silent misattribution live for days."* (ii) is
  therefore not open to this record.
- **Why (i) also stands on its own.** Stage A needs no spec text (its refusal is FR-1399's
  existing refusal of *"a difference between baseline and candidate that no derived change can
  carry"*, §0 above), so it does not wait for T1 and T2. It closes `FD-1660`'s silent limb (L3)
  as soon as it merges, the 02:35:40 entry's *"may merge as its own small step ahead of the
  fix"*.
- **Condition (c) of the 07:44:13 entry binds the order:** *"Stage B is planned NOW and gated
  right after Stage A on WK-673's lane, as the G2 item it is."* Stage B is not left to a later
  queue. The planner applies this to PL 9807's sequencing (below).

## DP-W — the write set

**(a) for Stage B, and for Stage A the plan's guard plus the three writes the maintainer's (A)
and its conditions make necessary.** Each part:

- **(a) is adopted for Stage B:** `_derive`, `_subset_pins` and `_PIN_KINDS` join the write
  set, with `_subset_algorithm` and `_check_dependence`, and so do `03`'s FR-1398 and FR-1399
  texts (T1 and T2 as adopted below). Without `_derive`, L3 stays: no mount change exists for a
  subset to carry. Without `_subset_pins` and `_PIN_KINDS`, L2 stays (`:484-489`, `:799`).
  Without the texts, code and spec disagree (`CLAUDE.md` §0). (b) is refused, because it is
  DP-1 (c), refused below.
- **Stage A, write 1: the guard (the plan's row), raised so that its text reaches the Job.**
  Condition (a) of the 07:44:13 entry: *"The Job's refusal names FD-1660 and says attribution
  of sub-graph mount changes is unavailable until SL 9850. It must not fail generically."* As
  planned, it would fail generically:
  - The worker keeps only `safe_error_text(exc)` of an `AttributionError` as the Job's detail
    (`dislocation_handlers.py:319-321`).
  - `safe_error_text` keeps an exception's text only for a `CodedError` or a Pydantic
    `ValidationError` (`packages/pricing-core/src/pricing_core/safe_error.py`
    `safe_error_detail` `:180-185`). Everything else is its type name alone.
  - `AttributionError` is a plain `ValueError` (`analysis.py:493-499`). That is deliberate:
    *"`attribute`'s own message can name a quote id … which is why the raw text is not kept
    (NFR-499)"* (`backend/tests/test_worker_raise_sites.py:210-216`).
  - So a guard raised as a plain `AttributionError` reaches the Job as the title "Validation
    Failed" and the detail "AttributionError", with neither `FD-1660` nor SL 9850 in it.

  **Ruled:** the guard raises an error that is both an `AttributionError` (code
  `VALIDATION_FAILED`, so `attribute`'s callers are unchanged) and a `CodedError`, declared in
  `analysis.py`. Its text is `VALIDATION_FAILED: ` followed by a literal that says three things:
  sub-graph mount differences are not yet attributable (the 02:43:49 entry's words); it names
  `FD-1660`; and attribution of sub-graph mount changes is unavailable until SL 9850 (written
  with the minted id). The text then gives the `mount_point`s. That text is input-free: the
  literal is fixed, and a `mount_point` is an authored identifier held to `_MOUNT_POINT`
  (`model_schema/rating.py` `SubGraphRef.mount_point`, read at `fc4401dc`), never a quote
  value. Stage A adds whatever case the coded-error raise-site enumeration requires
  (`safe_error.py:13-17`).

  **Refused:** making every `AttributionError` coded, which would keep text that can name a
  quote id (NFR-499). Also refused: special-casing the worker, which writes `backend/src/`, a
  path the plan lists as "Not written", for no gain over a fix in the guard's own layer.
  `backend/src/` stays "Not written".

  **Not run here:** that the Job's stored error then carries the text is read from the code
  path above, not run. Stage A's journey assertion (write 2) is the proof.
- **Stage A, write 2: the journey and its test**, `examples/fremtpl2/journey.py` and
  `backend/tests/test_wf699_journey.py`. Under (A), the refusal fires in D6's Job, not at D7.
  - Condition (b): *"The Stage A slice updates every merged test that runs D6 on a
    mount-changing fork (test_wf699_journey's D6/D7, plus any found by grep) to assert that
    exact refusal, with no test deleted."*
  - So D6 asserts the Job's refusal: `VALIDATION_FAILED`, with the text naming `FD-1660` and
    SL 9850.
  - Each later step that needs D6's run, or the approval that run enables, prints a `SKIPPED`
    line naming `FD-1660` instead of running. At `50bbdd96` those are D7 and D8
    (`journey.py:1071-1080`), E4, E6, E8 and E9 (`:966-1006`), and DEP (`deploy_and_score`,
    `:1084-1122`, which deploys `rv3`, the fork). The planner confirms the list against Stage
    A's base.
  - D7's line is the 02:43:49 entry's *"SKIPPED D7 — FD 9804 guard"*, with the minted id. It
    replaces *"SKIPPED D7 decomposition — FD 9804"* (`journey.py:85`;
    `test_wf699_journey.py:49`, at `50bbdd96`).
  - No test is deleted.
  - Activation need 3 (*"Stage A … do[es] not need it"*) is wrong for Stage A. Its journey edit
    needs SL-1527 on `main` (merged: `docs/roadmap.md`'s SL-1527 closure at `50bbdd96`), and
    Stage A serialises with SL-1543 on these two files, as Stage B does.
- **Stage A, write 3: the grep for condition (b)**, run here once at `origin/main`
  `50bbdd96b2154cb4eb79ccf91658191e51ab8906`. The predicate for a test that runs D6 or
  attribution:
  `git grep -l -E 'attribute\(|derive_changes|dislocation-runs|dislocation_run|attribute_' 50bbdd96 -- 'packages/*/tests' backend/tests frontend/src`.
  It matched 6 files. The predicate for a mount in each of them was
  `grep -c -E 'sub_graph|SubGraphRef|mount_point|m_ncd'`, and 2 had one:
  - `backend/tests/test_dislocation_runs.py` (1): `"sub_graphs": []` (`:284`), so no mount.
  - `backend/tests/test_rating_version_dislocation_gate.py` (5): the re-point test (`:290-327`)
    calls `_structural_diff_gate` and runs no Dislocation Job, and its other runs are inserted
    by `record_dislocation_run`, not by D6.

  Neither runs D6 on a mount-changing fork. `test_wf699_journey.py` reaches D6 through
  `journey.py` (`self.dislocation()` `:966`; `POST /dislocation-runs` `:1064`), which the first
  predicate cannot see, so it is named by hand. **The set at `50bbdd96` is
  `test_wf699_journey.py` alone.** Stage A re-runs both predicates at its own base and records
  the result in its LG.

## DP-1 — how a mount difference enters the derived changes (FR-1399)

**Ruled: (a). A mount is derived like a step, by its `mount_point`, with no new `DeltaKind`.**

- **Evidence.** A mount is a node of the parent's graph (`RL-1309` DP-3; `SubGraphRef`,
  `rating.py:447-454`; `_MountNode`, `:472-478`). Its `mount_point` shares one namespace with
  the `step_id`s (`:641-654`), so ordering mount changes and step changes by one id is well
  defined, and no mount change can have the same id as a step change. The diff already gives
  one entry per mount point (`_diff_mounts`, `:936-975`), as it does per `step_id`.
- **Kinds.** Added is `step_added`, removed is `step_removed`, and re-pointed or re-mapped (or
  both) is `step_changed`. **A re-point is not `table_repointed`.** FR-1399 defines that kind
  as *"the only changed field is the step's table or lookup reference"*. A sub-graph is
  neither. A ladder re-point changes rating logic, not a rate table's values. The journey's
  effect split also reads `table_repointed` as a rate-table effect (PL 9807 Task 6 Step 2).
- **Descriptions.** Each one starts with the `mount_point`, as a step change starts with its
  `step_id`, and names every ref, so the artifact's reader can tell a mount from a step without
  a new kind. Exactly: `<mount_point>: mount added (<after>)`,
  `<mount_point>: mount removed (<before>)`, and `<mount_point>: mount <before> → <after>` for
  a re-point. A re-map adds `; ports re-mapped` to the re-point form, or is
  `<mount_point>: mount ports re-mapped (<ref>)` alone. Each `<ref>` is `str(ArtifactRef)`, for
  example `sub_graph:ncd-ladder@4`. PL 9807 Acceptance 12 copies these strings from a real run.
- **Why not (b), a new `sub_graph_mount` kind.** It changes the contract: `DeltaKind`
  (`dislocation.py:135-143`), the authored `dislocation-run.schema.json` (`:101`), the
  generated contracts, OpenAPI and the frontend's generated client. In a P2 fix slice that cost
  buys only what the description already carries. If a client later needs to filter mounts by
  kind, that is its own spec change.
- **Why not (c), no derived change.** It changes the set of changes silently, which FR-1399
  forbids (*"The set of changes is never changed silently"*). A mount-only re-point (L3 with
  K = 0) would have no change at all to attribute to.
- **Implementation constraints** (for the executor; the plan's Task 4 already carries most of
  them):
  - The mount change carries the old and new `SubGraphRef`, not an `old_step`/`new_step`.
  - Wherever `_check_dependence` and `_subset_algorithm` look a change up by `step_id`, they
    must find a mount change by its `mount_point`.
  - A mount change never enters the steps' `applied` map: the mounts get their own map
    (Task 5 Step 2).
  - Its refs join `step_refs` (`:603-609`), so its pin difference is part of it (DP-2).

## DP-2 — what a subset's `sub_graphs` and pins are (FR-1398)

**Ruled: (i).** A subset's `sub_graphs` are the baseline's, with each mount change in the
subset applied by `_merged` keyed on `mount_point`. **`sub_graphs` joins `_PIN_KINDS`.**

- **Evidence.** This is the rule `RL-1449` DP-1 (c) applies to steps, contract and outputs
  (`_merged`, `:727-739`; `_subset_algorithm`, `:757-764`), extended to the fourth list of the
  algorithm. Empty and full stay exact (`:748-751`), so the subset of no changes is the
  baseline and the subset of every change is the candidate.
- **The pins follow the same rule as the other kinds:** the baseline's, less a version the
  candidate no longer pins once no mount in the subset names it, plus each version a mount in
  the subset names (`_subset_pins`, docstring `:776-777`; `kept` and `extra` `:789-798`; the
  `needed` loop `:783-785` gains the algorithm's mounts' refs).
- **In `_derive`:** a sub-graph pin difference that a mount change accounts for, through that
  mount's old or new ref, is part of that change. One that no mount change accounts for is its
  own `pin` change. This is FR-1399's rule for a step's reference, applied to a mount.
- **This also fixes L2 by construction:** a subset's pins now carry the baseline's sub-graph
  pins.
- **Why not (ii)**, the candidate's mounts in every non-empty subset. The isolated view
  (FR-266, *"the change applied alone"*) of an unrelated change would then carry the mount's
  effect, so the mount's effect would appear in every group.
- **T2, as the plan drafted it, is edited for one reason.** Its *"carry the baseline's
  sub-graph pins"* would keep a re-pointed mount's old version in a subset that applies the
  re-point. That is not the rule `_subset_pins` applies to every other kind. The adopted text
  says "formed as its other pins are".

## DP-3 — what `_check_dependence` does with a mount (FR-1399's dependence clause)

**Ruled: (i). A mount is a node in both directions.** In the subset holding a group:

- each subset mount's mapped `outputs` values join `produced`;
- a step that consumes a name only a mount change produces pairs with that mount change;
- a mount whose mapped `inputs` value is produced only by a change outside the group pairs
  with that change;
- the producer search also finds a mount change whose new or old mount maps the name out.

The refusal stays `VALIDATION_FAILED`, before any compile, and its text keeps its form.

- **Evidence.** The graph invariants already count a mount as a consumer and a producer
  (`rating.py:641-646`; `SubGraphRef` docstring `:450-453`). FR-1399 requires dependence to be
  refused **"Before any subset is computed"**, naming the pair.
- **Mounts must be in `produced`.** Without that, a changed step consuming an unchanged
  baseline mount's output would have no producer in the subset (`:829`). No pair is found then
  (no change produces it), so the run is not refused here. But nothing would say the name is
  produced.
- **On the demo's shape** (an input step `s_in_ncd` feeding `m_ncd`, which feeds `s_premium`),
  this rule forces the three into one group, and it is the reason the ladder and the lookup are
  not separable. PL 9807 Acceptance 13's LG line names this.
- **Why not (ii) or (iii).** Each lets a group that is not self-contained reach compile and
  fail there as `BUNDLE_COMPILE_FAILED`, not be refused up front as FR-1399 requires.

## DP-T — the texts

**T1 and T2 are adopted as edited below.** `<RL>` is this record's minted id and `<date>` the
date the applying slice writes them. Each is appended to its requirement as a dated amendment;
nothing in FR-1398 or FR-1399 is rewritten. They are ruling text only: this record makes no
spec edit (`.claude/skills/spec-change`; the applying slice, PL 9807 Task 3, makes it and runs
`audit-docs` once in the gate-2 slot).

- **T1, appended to `03` FR-1399:**

  > *(Amended `<date>`, WK-673, `<RL>`, `FD-1660`.)* **A sub-graph mount is derived like a
  > step.** A mount (FR-217) is a node of the parent's graph, named by its `mount_point`, which
  > is unique among the `step_id`s and the other mounts. Each mount the structural diff (FR-219)
  > reports as added, removed, re-pointed or re-mapped is exactly one derived change, of kind
  > `step_added`, `step_removed` or `step_changed` (a re-point is never `table_repointed`). It is
  > ordered with the step changes by its `mount_point`, and its description starts with the
  > `mount_point` and names the mounted versions. A difference in the Rating Version's
  > sub-graph pins (FR-218's mount pin) that a mount change accounts for, through that mount's
  > reference on either side, is part of that change. One that no mount change accounts for is
  > its own `pin` change. For the dependence clause, a mount consumes the parent names its
  > `inputs` map to and produces the parent names its `outputs` map to, and a mount change is
  > paired like a step change.

- **T2, appended to `03` FR-1398:**

  > *(Amended `<date>`, WK-673, `<RL>`, `FD-1660`.)* A subset bundle's `sub_graphs` are the
  > baseline's with each mount change in the subset applied, and its sub-graph pins are formed
  > as its other pins are: the baseline's, less a version the candidate no longer pins once no
  > mount in the subset names it, plus every version a mount in the subset names. The subset of
  > no changes is the baseline and the subset of every change is the candidate.

- **What changed from the plan's drafts, and why.**
  - T1 says a re-point is never `table_repointed` (DP-1).
  - T1 fixes what the description starts with (DP-1).
  - T1 names the pin by FR-218's mount pin rather than *"(FR-237)"* alone, since FR-237's list
    names no sub-graph (§0 above).
  - T1 says a mount change is paired like a step change (DP-3).
  - T1 and T2 carry the finding's minted id, `FD-1660`, rather than the working id 9804.
  - T2's pin rule is DP-2's.

## The question put to the lead (02:52:33 BST), and its answer

The 02:43:49 entry places the guard *"in attribute after _check_groups, as planned, so
derive_changes, the estimate and D6's dislocation are untouched"*. **At `fc4401dc` the
dislocation is not separable from the attribution in the platform.**

- The worker calls `attribute` inside the dislocation Job for every run that is not an
  exact-mode twin (`dislocation_handlers.py:311-318`).
- On `AttributionError` it raises `PlatformError(code, …, 422)` (`:319-321`) before `persist`
  (`:325`), so the Job fails and no Dislocation Run is stored.
- A submission needs that run (`_dislocation_gate`, `rating_versions.py:994`;
  `dislocation_run_verified`, `:1253-1259`).
- On SL-1527's journey at `bc7695d0`, D6 posts one run (`examples/fremtpl2/journey.py`
  `:1037-1046`), and E4 resubmits citing it (`:944-946`).

With the guard as settled, the demo's fork adds `m_ncd`, so D6's Job fails, and E4 stays
`EVIDENCE_INCOMPLETE`: E4 to E9 are blocked, not D7 alone. Across the product, a Rating
Version that adds, re-points or re-maps a mount gets no Dislocation Run until Stage B, so it
cannot be submitted for approval. The failure is loud, and it never misprices.

The choice was DP-G's, so the maintainer's; this record did not make it, and held DP-S and DP-W
until it was made. The lead's from-lead entry "2026-10-12 07:44:36 BST" relayed the answer to
this seat, and records that the question went unanswered from 02:52:33 to 07:44 BST through a
dropped hand-off. The maintainer's entry, from `~/gi-pricing-plan.local/channel/to-lead.md`, is
headed **"2026-10-12 07:44:13 BST — Three dropped decision-maker hand-offs: (1) RL 9852 = (A),
with 3 conditions; (2) RL 9800's Q1 (i) and Q2 (A) RULED as the decision-maker proposed; (3) RL
9876 ACKED"**. Its opening and its item (1) are quoted whole; items (2) and (3) rule two other
records and are elided here:

> Dropping them for ~4.5 h is a lead miss. Add a standing check: every decision-maker CLI's from-dm file is read at each seat check, and an unanswered STOP older than 30 min is escalated to me.
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
>
> *[Items (2) and (3), on RL 9800 and RL 9876, elided.]*

DP-S and DP-W above are ruled on it. One standing duty falls to this role from it: **if Stage B
slips past G2's need, the decision-maker raises (B) as its own decision point**, in the
maintainer's words above.

## What it obliges

**The planner** applies these to PL 9807 before its mint. PL 9807 is `draft` and unmerged, so
they are the planner's pre-merge edits; this record does not edit the plan.

- **DP-G (the maintainer's):**
  - Task 2 Step 1 loses *"unless DP-G (i)'s exemption holds"*.
  - Acceptance 3 (G3) is inverted: the one-group run is refused, `VALIDATION_FAILED`, naming
    `m_ncd`.
  - The SL 9850 row (working id) loses *"except one analyst group holding every derived change
    (DP-G)"*.
  - Acceptance 12 and Task 6 name the line that is on `main` when Stage B starts:
    *"SKIPPED D7 — FD 9804 guard"* (02:43:49) with the minted id, `FD-1660`, not *"SKIPPED D7
    decomposition — FD 9804"*. It sits beside the other `SKIPPED` lines DP-W's write 2 adds.
- **DP-S (i):** Stage A is cut as its own row under working id SL 9851 (reserved), by the
  planner's dated line on PL 9807's branch before the mint, as the plan's own text provides.
  Stage B stays SL 9850 and is gated right after Stage A merges (condition (c)). Sequencing
  items 1 and 2 merge into one, because this record rules DP-G's context, DP-S, DP-W, DP-1 to
  DP-3 and DP-T together.
- **DP-W:**
  - Stage A's write set is the guard as a coded `AttributionError` (write 1), the journey and
    its test (write 2), and its LG, with write 3's grep result recorded in that LG.
  - `backend/src/` stays "Not written".
  - Acceptance item 5 changes. *"`SL-1527`'s journey test passes unedited"* becomes "passes
    with D6 asserting the refusal and the later steps `SKIPPED`, no test deleted".
  - Acceptance items 1, 2 and 4 add to "After Stage A" that the text names `FD-1660` and SL
    9850, and that `safe_error_text` keeps it.
  - Activation need 3 is corrected for Stage A (SL-1527 on `main`; serial with SL-1543).
  - Stage B's write set is (a), and Stage B also removes write 2's `SKIPPED` lines as it
    re-lands D7's two-group run.
- **DP-1:** Acceptance 12's descriptions are the forms ruled in DP-1.
- **DP-T:** Task 3 applies T1 and T2 as adopted here, not as drafted.

**The decision-maker** has one standing duty from the 07:44:13 entry. If Stage B slips past
G2's need, it raises (B), persisting the run without attribution plus a recorded refusal, as
its own decision point.

**Not decided here:**
- Whether Stage A needs a dated interim note in spec `03`. That is the question the section on
  which of spec and code was wrong raises above (`CLAUDE.md` §0), and it is the lead's.
- (B), which the maintainer refused for now.
- The severity of `FD-1660`, which is the register's and the 02:35:40 entry's.

## Acceptance — the violation that must become detectable

The violation is a Dislocation Run, or a direct `attribute` call, that reports a sub-graph
mount's effect under another change's label. Until Stage B, the related violation is a refusal
that does not say why. Each check below is a slice's own test, written red-first in that
slice. This record is ruling text and adds no check of its own, so none is shown red here.

- *Violation (Stage A, L3): a candidate re-points a mount and edits one rate table, and
  `attribute` returns.* G1 reds on it on the base and, after Stage A, expects
  `VALIDATION_FAILED` naming `m_ncd`.
- *Violation (Stage A, condition (a)): the guard's refusal reaches the Job as a bare
  "AttributionError".* Write 2's D6 assertion on the refusal text (`FD-1660`, SL 9850) reds on
  a guard raised as a plain `AttributionError`, which `safe_error_text` reduces to its type.
- *Violation (Stage A, condition (b)): a merged test that runs D6 on a mount-changing fork is
  deleted, or is left asserting a run.* Stage A's LG records write 3's grep, re-run at its base.
  Every test it names asserts the refusal.
- *Violation (Stage B): a subset over a mount change compiles against the baseline's mount or
  pin, or a mount's consumer is split from it.* R1 to R4 (PL 9807) red on it on the base.

## Ruled

| DP | Ruled | By |
|---|---|---|
| DP-G | the maintainer's: refuse any mount difference at any K, and refuse at K ≥ 2 when either side mounts; `VALIDATION_FAILED` naming the finding (`FD-1660`); in `attribute` after `_check_groups` | the maintainer (by delegation), to-lead 2026-10-12 02:43:49 BST, quoted above |
| DP-G's consequence | (A): the guard fails D6's Job for a mount-changing version until Stage B; (B) and (C) refused; conditions (a) to (c) | the maintainer (by delegation), to-lead 2026-10-12 07:44:13 BST, quoted above |
| DP-S | (i): Stage A its own slice (SL 9851, working id); Stage B (SL 9850, working id) gated right after it | this record |
| DP-W | Stage A: the guard as a coded `AttributionError` so its text reaches the Job; the journey's D6 asserts the refusal and the later steps are `SKIPPED`; the condition (b) grep (`test_wf699_journey.py` alone at `50bbdd96`); `backend/src/` not written. Stage B: (a) | this record |
| DP-1 | (a): a mount is derived like a step by `mount_point`; `step_added` / `step_removed` / `step_changed`; no new `DeltaKind`; the description forms above | this record |
| DP-2 | (i): `sub_graphs` merged by `mount_point` from the subset's own mount changes; `sub_graphs` joins `_PIN_KINDS`; the sub-graph pins follow the other kinds' rule | this record |
| DP-3 | (i): a mount is a node in both directions for dependence; refused `VALIDATION_FAILED` before any compile | this record |
| DP-T | T1 and T2 adopted as edited; ruling text only, no spec edit here | this record |
