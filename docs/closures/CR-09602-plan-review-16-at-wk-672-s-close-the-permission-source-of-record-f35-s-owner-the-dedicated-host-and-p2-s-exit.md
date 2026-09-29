---
id: CR-9602
family: closure
kind: review
title: Plan review 16 — at WK-672's close — the permission source of record, F35's owner, the dedicated host and P2's exit
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-29
owner: lead
tree: 1c8762d9ed235f80e0f2fff80c44003694828e97
phase: P2
work: WK-672
corrected_by: []
relates: [CR-1212, RL-1232, RL-1236, FD-1194, OQ-1233, OQ-1234, OQ-1235]     # ids only
---

### Plan review 16 — at WK-672's close, 2026-09-29

**Base tree: `1c8762d9ed235f80e0f2fff80c44003694828e97`** (origin/main after #889). **Working
id `CR-9602`.** It is minted at the merge turn with `python3 scripts/doc-id.py next --ref
origin/main`.

**Who does what.** The planner conducts and files this review (`document-ids.md` §1.6, the
CR `review` row; the maintainer's STRUCTURE entry of 2026-09-29 15:26:00 BST, §1 and §3). The
family is the lead's, and the lead gives a verdict on each proposal. **Nothing here binds
until the maintainer dates the acceptance line.** The output is proposals, never a change
(`CLAUDE.md` §14).

**Trigger.** `CLAUDE.md` §14, "at each workstream close". The workstream is **WK-672**
(golden quotes, property assertions, regression runs). Its Slices 3 and 4 merged as #886 and
#901. Its close record is being drafted by the auditor on branch `wk672-close`. This review
is consistent with that record; see *Consistency with the WK-672 close record* below.

**Whether this review is CR-1212's G6 is contested, and Proposal 8 puts it to the maintainer.**
- G6 reads "A plan review 16 is filed after G1–G5 and before the demo". G1–G5 are not met at
  this tree.
- The maintainer's entry of 2026-09-29 16:05:14 BST says this review "is also P2 exit
  criterion G6".
- Both are recorded; neither is chosen here.

**Form.** It follows `CR-1212` (plan review 15): the lead's required inputs as proposals
first, then the five `phase-review` questions, then Output and Verdict.

## Scope

- P2 as `docs/roadmap.md`'s `## P2` section defines it at `1c8762d9`: 17 Works, the exit
  criteria G1–G6 accepted into `CR-1212`, and every register row whose Phase column includes 2.
- The lead's required inputs, items 1–6 of the brief, plus F38 and the dedicated host.
- P2 work merged on 2026-09-29: WK-672 S3 and S4 (#886, #901), #887 (FR-177, FR-178), #889
  (the NFR-499 sanitiser), `RL-1232` (#848) and `RL-1236` (#856).

## Evidence

- **Tree.** Everything under `docs/`, `packages/` and `backend/` was read at `1c8762d9`, in
  the worktree `plan-review-16`.
- **Open PRs, read at their heads, not on main:**
  - #843 is the WK-674 map plan, `PL-1237`, read at head `306e42b9` on branch
    `p2-wk674-map`. It merged after this review's tree, as `6ae8a99a`.
    `git diff --stat 306e42b9 6ae8a99a -- docs/plans/PL-01237-*` prints nothing, so the file
    read is the file on main. It is `status: draft` there.
  - The records PR branch `records-2026-09-29` is at `bc55a975`. It carries two things:
    - the finding "A team member overwrote the user's auto-memory index, and the restore
      missed 27 index lines". It has a working id, which its mint at that PR's merge
      replaces, so this record names it by title. It is called *the memory-overwrite
      finding* below.
    - the lead's P3-carry note (commit `c2db4f72`).
- **GitHub state** was read with `gh pr view` on 2026-09-29 at about 15:00 UTC. It was
  read-only, and nothing was posted.
- **The channel file.** The maintainer's entries are quoted by heading. The file is
  `~/gi-pricing-plan.local/channel/to-lead.md`, which is local and not in the repository.
- **Predicates.** Every count below states the command it was measured with (`CLAUDE.md`
  §13, RFC-777).

## Proposal 1 — N3: the permission catalogue's source of record

**The input.** `RL-1232` DP-6 observed, but did not rule, two naming differences:
- `06` had `model:approve` where the code has `approval:decide`;
- `06` had `rating_version:submit` where the code has `rating:submit`.

`CR-1212` item 3 made the code's coarse names P2's record. It left the general question to
this review: from now on, is `06` or the code the source of record for the catalogue?

**What is already resolved.**
- `RL-1236` row 17 maps `model:approve` to `approval:decide` (DP-C (a)), and `06:62` is amended.
- `RL-1236` row 1 maps `rating_version:submit` to `rating:submit`, and the alias note is at
  `06:279`.
- DP-6's "for an auditor to file as a finding" is therefore discharged by `RL-1236`, and no
  `FD-` is needed for those two names. **Proposed:** the lead records this as the
  disposition of that DP-6 obligation.

**What is not resolved: the vocabulary is defined twice.**
- The code's vocabulary is not in the backend. It is `model_schema.Permission`, a closed
  `StrEnum` in `packages/model-schema/src/model_schema/permissions.py`, with `BUILTIN_ROLES`
  beside it.
- It is generated into `docs/contracts/openapi/generated.json` (the enum at `:8800-8815`).
  Its module docstring says the vocabulary lives there "because both sides need it and
  neither may invent it".
- `06` §2, §4.1 and the Pricing Actuary role block (`06:192-204`) define the vocabulary a
  second time, by hand. That is the shape `CLAUDE.md` §2 forbids: "A shape defined twice will
  diverge". It did diverge: `RL-1236` counted 34 names on one side only.
- **Measured at `1c8762d9`:**
  - The enum has 24 members. The predicate is the regex
    `^\s+[A-Z_]+\s*=\s*"([a-z_]+:[a-z_]+)"` over `permissions.py`, in multiline mode.
  - The Pricing Actuary role block, `06` lines 196–201, names 16 permissions (the regex
    `"([a-z_]+:[a-z_*]+)"`). **12 of the 16 are not enum members.** Eight are `RL-1236`
    maps, and four are its spec-only carries.
  - So a reader who copies that built-in role off the page gets a role that grants 4 of its
    16 names.

**Options.**
- **(a) `06` is the source of record.** The code is renamed to `06`'s names.
  - Cost: it reverses `RL-1236`'s 15 map verdicts, and it migrates role grants and the
    generated contract.
  - It also keeps two definitions, so the drift can recur.
- **(b) The code is the source, and `06` mirrors it by hand.** This is the state after
  `RL-1236`.
  - It needs no work now.
  - It keeps two hand definitions with no check between them, which is how the 34 names
    diverged.
- **(c) Split the two jobs.** Build a check that fails when they disagree.
  - `model_schema.Permission` and `BUILTIN_ROLES` are the **one definition of the names and
    of the built-in role sets**. This is ADR-704's one-way flow, which already holds in the
    code.
  - `06` is the source of record for the **meaning**: what each capability permits and who
    must hold it, as requirements.
  - `06` §4.1's catalogue and the role block cite the generated vocabulary and do not
    restate it.
  - **A check fails the gate** when `06` names a permission token that is not an enum
    member, or when an enum member has no `06` §4.1 row. The check excludes struck text, the
    §4.1 alias notes, and `RL-1236` rows 5–10, which are spec-only with owners. This is the
    two-list comparison that `RL-1236`'s own *Acceptance* proposes. It is proved red on a
    broken input.
  - A new permission lands in **one commit**: the `06` row, the enum member, and the route
    check (`CLAUDE.md` §2).

**Recommendation: (c).** It is the rule `CLAUDE.md` §2 already states for every other shape,
and the code already follows it. It is the only option with a check that the failure cannot
survive; (a) and (b) both rest on care.
- **Owners, if accepted:**
  - The **decision-maker** records the rule (`RL-`, or an ADR if the lead judges it
    cross-module), together with the `06` amendment that replaces the role block's names with
    a reference to `BUILTIN_ROLES`.
  - **WK-1178** builds the check, before the first slice that adds a new name. On the
    current plans that is WK-690's `custom_objective:author` (`RL-1236` row 5).
- Until the check exists, `RL-1236`'s interim rule stands: the table is re-derived at each
  Work close that touches permissions.

**Lead verdict (Proposal 1):** _pending_
**Maintainer acceptance (Proposal 1):** _pending_

## Proposal 2 — #852 and the Dependabot queue

**The premise has moved.** The register row for FD-1194 (`docs/findings/register.md:181`)
says "#852 is held until WK-672 closes". **#852 is closed, not held.** Dependabot closed it at
`2026-09-28T14:05:08Z` with the comment "Looks like these dependencies are updatable in another
way, so this is no longer needed" (`gh pr view 852`: `state CLOSED`, `mergedAt null`). Its
successor is **#857** (the frontend group, 12 minor and patch updates, open). There is nothing
to merge on #852.

**The open Dependabot PRs** (`gh pr list --state all --author app/dependabot`, read at about
15:00 UTC):

| PR | What | CI rollup at its head | Recommendation |
|---|---|---|---|
| #857 | frontend group, 12 minor/patch (vue, vite, eslint, vue-tsc …) | `frontend/check` SUCCESS (updated `2026-09-28T20:48:38Z`) | **Merge now that WK-672 closes**, after a local two-half gate at the PR head merged with current main |
| #881 | python group, 11 minor/patch (ruff 0.16.3→0.16.9, polars 1.43.2→1.44.2, scikit-learn, alembic, pydantic …) | `python` SUCCESS | **Merge after #857**, the same way, **plus WK-672's golden quotes and a regression run**. polars and scikit-learn minors can move numbers, and WK-672 built the instrument that sees it |
| #877, #878, #879 | `actions/checkout` 4→7, `setup-python` 5→7, `setup-node` 4→7 (major; `dependabot.yml` sends majors alone) | SUCCESS on the workflows each touches | **Merge one at a time**, after reading each release's runner and Node requirement |
| #882 | `zen-engine` 0.53.0 → **2.0.2** (major) | `python` SUCCESS | **Do not merge.** See below |

**Why #882 is different.**
- `zen-engine` is the rating evaluator (ADR-706). Its decimal semantics retired OQ-614, and
  its `passThrough` output is F35's cost.
- A major bump of the engine that prices every quote is a governed change. It is not a
  dependency bump.
- The precedent is `hypothesis` (`dependabot.yml`: "RS-1176 F4 condition 1: … moves only as
  a governed change (spike + ruling), never by Dependabot").
- A green `pytest` does not show that decimal semantics are unchanged.

**Recommended for #882:**
- close it;
- add `zen-engine` to `dependabot.yml`'s `ignore` list, the way `hypothesis` is listed;
- file an `FD-` for a governed upgrade, owner WK-1178: a spike, the decision-maker's ruling,
  ADR-706 re-confirmed, and a golden-quote and regression run on both versions.

**Two cautions for every merge above:**
- **A CI SUCCESS here is not a pass.** Each rollup predates today's main.
  `python.yml`'s stage has read SUCCESS over a failing pytest before (the ci-watcher agent's
  traps). The local two-half gate of `CLAUDE.md` §11 is the check.
- **Merging is the user's**, per the STRUCTURE entry §1 ("repo settings and Dependabot, which
  stay with the user"). The maintainer takes these to the user.

**For the register pass (the auditor's):** FD-1194's cell names #852 as held. It should
name
#857 as #852's successor and cite Dependabot's close.

**Resolved 2026-09-29 by the maintainer** (entry `2026-09-29 16:08:24 BST · maintainer
(acting on the maintainer's behalf) · HOST FALLBACK accepted; DEPENDABOT plan approved (the
maintainer)`, §2, quoting the maintainer: "approve Dependabot plan"):
- **#882 is not merged.** A WK-1178 PR adds an ignore rule to `.github/dependabot.yml` for
  zen-engine's major version 2, and files an `FD-` for a governed upgrade under WK-1178 (a
  spike first). Closing #882 is the user's action.
- **#857, then #881.** The lead runs a full local two-half gate on each PR's head, and the
  user merges on green. #881 is re-gated if #857's merge changes its base.
- **FD-1194's stale cell** is updated by the auditor in the next records PR.

**What the entry does not dispose of:** #877, #878 and #879, the three major GitHub Actions
bumps. It names only zen-engine's ignore rule. This review's recommendation for them (merge
one at a time) stands as a proposal, open to the lead's verdict.

**Lead verdict (Proposal 2):** _pending_
**Maintainer acceptance (Proposal 2):** given for the part the 16:08:24 entry states. The
part it does not state (#877–#879) is _pending_.

## Proposal 3 — F35's remedy: its owner, and whether P2 can exit with NFR-490 red

**The inputs.**
- **The maintainer's scope decision** is the entry of 2026-09-29 15:36:43 BST, "SCOPE:
  NFR-490 / F35 in WK-674, option (b)". WK-674 Slice 5 measures NFR-490 and records it red if
  it is red. WK-674 does not build F35's remedy. The remedy is carried, with its owner named
  here.
- **`CR-1212` G4 (b)**, as accepted, sends NFR-489, NFR-490 and NFR-502 to WK-674, "not
  'accepted as failing'".
- **F35** (register L77) records +497 % to +723 % against a 20 % ceiling, across 5 of 5 runs.
  The cost is a 1,119,097-byte payload set by `to_wire(passThrough: True)` in
  `packages/pricing-core/src/pricing_core/rating/runtime.py`.

**Three facts this review adds.**
1. **One lever, three rows.** F55 (register L96) names the same remedy: trim
   `TraceStep.consumed`/`.produced` to the step's own declared `consumes`/`produces`
   (`pricing_core.rating.score._build_trace`). F55 also calls it NFR-500's largest lever
   (F37). `CR-1212` already gave F55 and F37 to **WK-1178**.
2. **F35 is on a P2 deliverable's path.** `POST /api/v1/score/compare` (WK-672 S4) scores
   both Rating Versions with `trace=True` (`backend/src/app/api/score.py:359-362`) and diffs
   the traces. WK-675's Quote Sandbox view is built on it. The traced path is therefore not
   an off-path facility: it is what the sandbox's user waits on.
3. **The remedy changes what `consumed` holds, and `03` §4.10 reads it.** `own_change` is
   derived from `consumed` equality (`03:731`), with a known limit (`03:733`) and `OQ-1231`
   (owner WK-675) open on it. The remedy must be ruled with that interaction in view, and
   WK-672 S4's diff tests must be re-proved on the trimmed trace.

**Options for the owner.**
- **(a) WK-1178, in P2: one slice for the shared lever (F35 + F55).**
  - The decision-maker rules first on what a `TraceStep` records (FR-258; §4.10; `OQ-1231`).
  - The slice is **sequenced before WK-674 Slice 5**, so Slice 5 measures the remedied path
    and NFR-490 can be green on the exit tree.
  - It carries NFR-500's re-measurement (F37; Proposal 11) on the trimmed trace.
  - Cost: one ruling and one slice in P2 under the budget. `score/compare`'s diff
    semantics, merged today, are re-proved.
- **(b) A new P2 Work for scoring-path performance** (F35, F55, F37 and the NFR-489 remedy).
  Cost: a new G1 row to close, and more structure than one lever needs.
- **(c) Carry the remedy out of P2** to a named later Work. The maintainer then amends
  `CR-1212` G4 (b), by a dated line, so that P2 exits with NFR-490 **measured red and
  carried**.
  - Cost: P2 ships the Quote Sandbox on a traced path 5–7× over its budget.
  - G4 (b)'s acceptance chose "WK-674, not 'accepted as failing'", so (c) reverses the
    intent of that line. It does not merely fill a gap in it.

**Whether P2 can exit with NFR-490 red, read against the criteria as written.**
- **G4** reads "measured on the exit tree, or carried with an owner". A red measurement
  satisfies its letter.
- **G3** needs F35 "carried with a named owner", which any of (a)–(c) gives.
- **But `CR-1212` G4 (b)'s accepted disposition** routed NFR-490 to WK-674 *instead of*
  "accepted as failing". The 15:36:43 decision has since taken the remedy out of WK-674.
- **So the answer is: not without a dated line.** Under (a) the remedy lands in P2 and no
  amendment is needed. Under (c) the maintainer amends G4 (b) for NFR-490. This review
  leaves neither unstated.

**Recommendation: (a).** The lever is small and shared by three rows that WK-1178 already
partly owns. It sits on the path a P2 deliverable exposes to its user. And sequencing it
before WK-674 Slice 5 means the exit-tree measurement is of the remedied path. **If the
maintainer's budget cannot carry the slice in P2, (c) with its dated G4 (b) amendment is the
honest fallback, not a silent red.** Until the verdict, F35's register row reads "carried;
owner named by plan review 16" (the 15:36:43 entry), and on acceptance it names WK-1178.

**Lead verdict (Proposal 3):** _pending_
**Maintainer acceptance (Proposal 3):** _pending_

## Proposal 4 — the dedicated host and F38: what P2's exit depends on

**The dependency.**
- `PL-1237` (#843 at `306e42b9`, Acceptance items 5 and 6) makes a **dedicated host, owned by
  the maintainer**, the condition for three kinds of verdict:
  - F1's switchover verdict (the 30 s switch and the zero-drop clause);
  - NFR-489 and NFR-502;
  - NFR-490 and NFR-493's linearity limb, "measured the same way, on the same host".
- A run on the shared VM "claims no verdict near a bound". This follows `RL-921` §4, and
  `RL-1232` DP-3 (b) as noted by QDP-3: "the re-measurement trigger cannot validly fire
  without a dedicated host".
- The STRUCTURE entry §2 and §4 keep the host question with the maintainer, to take to the
  user. **No repository record names a host at `1c8762d9`.**

**F38** (register L80) is NFR-489's without-GBM limb, "measured, verdict unstable across
runs". Two of five runs breached 15 ms, and load widened the spread about fivefold.
`PL-1237` item 6 lets that limb be recorded as "measured, unstable", which is not a pass.
Without a host, no run can settle it.

**How it bears on P2's exit.**
- **G1:** WK-674 cannot meet its own Acceptance items 5 and 6 without the host, so it cannot
  close as planned.
- **G4:** the bound-near NFRs (NFR-489 both limbs, NFR-502, NFR-493's linearity limb and
  NFR-494's switchover) have no valid verdict without it.
- **NFR-490 is the exception.** At +497 % to +723 % against 20 %, it is far from its bound,
  and a shared-VM result settles "red". Only a remedied NFR-490 near 20 % would need the
  host.

**Options.**
- **(a) The user provides a dedicated host before WK-674 Slice 5.** G1 and G4 are then met as
  written.
- **(b) No host in P2.** The maintainer amends two things by dated lines:
  - **G4:** a bound-near NFR measured on the shared VM is recorded "measured, diagnostic;
    verdict carried", with owner the maintainer and event "the dedicated host is available".
  - **`PL-1237`'s items 5 and 6**, the same way. It is a draft plan now, so this is a dated
    amendment; after it freezes, it would be a replan.

  WK-674 can then close under G1 with those verdicts carried.
- **(c) Hold P2's exit until a host exists.**

**Recommendation, as drafted at `42d31bc9`.**
- Take the question to the user **now**. It is the longest-lead dependency in P2, and its
  answer decides between (a) and (b).
- If no host is committed by the time **WK-674 Slice 4 closes**, apply (b) by dated line
  before Slice 5's leaf plan freezes. Do not drift into (c).
- This review does not choose the host. That is the user's decision, and the maintainer
  brings it.

**Resolved 2026-09-29 by the maintainer: (b), now.** This is the entry `2026-09-29 16:08:24
BST · maintainer (acting on the maintainer's behalf) · HOST FALLBACK accepted; DEPENDABOT plan
approved (the maintainer)`, §1, quoting the maintainer: "accept the fallback for the host". No
host is committed. The maintainer took (b) at once, not at Slice 4's close as recommended
above; the recommendation is kept as drafted, beside the decision that replaced it.

**The resolution, recorded here as the entry directs.**
- **What is carried:**
  - F1 (`PL-1237` acceptance item 5);
  - NFR-489 (both limbs, so F38 is included);
  - NFR-502;
  - the NFR-493 linearity limb;
  - NFR-494 (item 6).
- **Its form.** Each is **measured, diagnostic** on the shared VM, and its verdict is
  **carried**:
  - owner: **the maintainer**;
  - discharge event: **a dedicated host available**.

  No near-bound pass or fail is claimed from the shared VM.
- **Who writes it:**
  - G4's roadmap row: the lead, quoting the entry;
  - `PL-1237`: the planner, at #892's turn, in the commit that sets it `active`.
- **NFR-490 is unchanged.** It is far from its bound, and the SCOPE decision of 15:36:43
  stands (Proposal 3).
- **For G1:** WK-674 can close with these verdicts carried.

**Lead verdict (Proposal 4):** _pending_
**Maintainer acceptance (Proposal 4):** given, in the 16:08:24 entry above.

## Proposal 5 — OQ-1233, OQ-1234 and OQ-1235 against P2's exit

**Where they sit at `1c8762d9`:**
- OQ-1233 and OQ-1234 are on the roadmap §10 gate **"Before Phase 2"** (`docs/roadmap.md:1189`,
  note at `:1197`). P2 is already open, so that gate cannot hold them back from anything.
- OQ-1235 is on **"Before WK-674 Slice 3"** (`:1190`).
- `PL-1237` places OQ-1234 in Slice 2: its leaf plan "does not go `active` until OQ-1234 is
  decided". It gates Slice 3 on OQ-1235. It holds OQ-1233 at "no slice until it is decided".

| OQ | Whose decision | What it blocks | Proposed gate | Bearing on P2's exit |
|---|---|---|---|---|
| **OQ-1233** (who owns `07` FR-453's deployment-notification limb) | **Scope** (which Work, which phase), so the maintainer's, on this review's proposal. The OQ's own Owner cell reads "maintainer (at the next plan review)" | FR-272's notification limb, and so WK-674's full FR-272 | Move it from *Before Phase 2* to the gate of the Work that is chosen | G1: WK-674 closes with FR-272's audit limb delivered and its notification limb "deferred with an owner" (a `CLAUDE.md` §13 verdict), unless (a) is chosen. G2 needs no notification |
| **OQ-1234** (where FR-429's skip permission lives) | **Technical**, so the decision-maker's (STRUCTURE §1) | WK-674 Slice 2's leaf plan | Move it from *Before Phase 2* to a new gate row, **Before WK-674 Slice 2** | G1, through Slice 2. G2 deploys `uat` then `prod` in order and needs no skip |
| **OQ-1235** (per-environment configuration vs FR-446) | **Technical**, so the decision-maker's | Slice 3; FR-431, NFR-496's prod-sampling limb, and Slice 6's default-off switches | It stays **Before WK-674 Slice 3**, which is correct as placed | G1 and G4 (NFR-496's limb), through Slice 3 |

**OQ-1233 needs a proposal. Its options are its own (a)–(c):**
- (a) **WK-674**: it builds the signed delivery path for one limb now.
- (b) **WK-688 (P4)**: one delivery path serves both limbs. A P2 deployment sends no
  notification until P4, and FR-272 carries a deferral for two phases.
- (c) **A platform Work** that owns FR-453, with its phase set by its first consumer.

**Recommendation for OQ-1233: (b), with FR-453 (both limbs) named on WK-688's row.** The
reasons:
- G2 and the P2 demo need no notification.
- The Audit Event, which is what `05` consumes, is built in P2 (`RL-1232` DP-4's half, which
  stands).
- WK-688 is where retries, backoff and delivery status are first needed for their own sake
  (`05` FR-336).
- A new platform row, option (c), adds a row and a dependency edge in order to build the
  same thing once. Naming FR-453 on WK-688 builds it once with no new row.
- **Declined limb of the OQ's own recommendation (c):** "If that review needs FR-272's
  notification in Phase 2, the row is scheduled before WK-674's deployment slice." This
  review finds no P2 exit criterion that needs it, so that limb does not fire.

The move of OQ-1233 to *Before Phase 4* and the edit to WK-688's row are the lead's, after
acceptance.

**Recommendation for OQ-1234 and OQ-1235:**
- The decision-maker rules each, in an `RL-` citing the maintainer's recommendations of
  2026-09-29 (STRUCTURE §2).
- OQ-1234 is ruled before WK-674 Slice 2's leaf plan freezes, and OQ-1235 before Slice 3's.
- The gate row edits are the lead's.

**Lead verdict (Proposal 5):** _pending_
**Maintainer acceptance (Proposal 5):** _pending_

## Proposal 6 — the memory-overwrite finding: the write boundary that no charter states

**The finding.** The memory-overwrite finding (branch `records-2026-09-29`) records that on
2026-09-29 the reporter cut the user's auto-memory index, `~/.claude/projects/…/memory/MEMORY.md`,
from 239 lines to 47. The file was since recovered. The finding's own disposition point 2
leaves the rule to be written down: "no team member writes under `~/.claude/`".

**The gap, measured.** `grep -rn '~/.claude\|\.claude/projects\|auto-memory'` over
`.claude/roles/` and `docs/process/delivery-process.md` at `1c8762d9` returns **0 lines**. No
charter says where a role may not write.
- `delivery-process.md` §3 says "Tool scope lives once, in each role's own file".
- The rule has so far lived only in briefs. This review's own brief says "NOTHING under
  ~/.claude/". `CLAUDE.md` §15 forbids exactly that: "a role file that proves insufficient is
  a finding against the file: fix the file, do not paste a brief back in".

**Why a charter line is needed and care is not enough.** The harness's own system prompt
tells **every** session, team members included, that it has a persistent memory directory
and should write to it directly. A team member therefore starts with a standing instruction
to write under `~/.claude/`. Only its charter can say that the instruction does not apply to
it.

**Options.**
- **(a) One line in each of the seven charters.** This follows §3's "tool scope lives in each
  role's own file", but gives seven copies of one rule (RFC-756).
- **(b) One team-wide rule in `delivery-process.md` §3**, with §3's sentence amended to say
  that the write boundary is stated there once. Each charter keeps only its **positive**
  write targets. For example, `reporter.md` gains its one target, per the maintainer's
  ruling relayed in the memory-overwrite finding: `~/gi-pricing-plan.local/handover/eta.md`.
  - `delivery-process.core.json` is re-derived in the same commit, because it is the
    process's machine-readable extract (`CLAUDE.md` §15).
- **(c) (b) plus a mechanical guard**, a `PreToolUse` hook that refuses team-member writes
  under `~/.claude/`. **Not recommended now.** This review found no verified way for a hook
  to tell a team member's session from the maintainer's, and a rule must not rest on a
  mechanism nobody has checked exists. If one is found, it is a WK-1178 item with a
  broken-input proof.

**Recommendation: (b).** Proposed text for `delivery-process.md` §3, for the maintainer to
amend or accept:

> **The write boundary, every role.** A team member writes only inside its own worktree, its
> scratch directory under `~/gi-pricing-plan.local/`, and the targets its charter names. It
> **never writes under `~/.claude/`**: not memory, settings, projects, skills or
> `CLAUDE.md` there. This holds even though the harness offers a memory directory to every
> session: that offer is the user's store, not a team member's. The job tmp directory is
> transient scratch. Anything a record cites goes to `~/gi-pricing-plan.local/`.

**Owners, if accepted:**
- **The maintainer**, for the amendment: charter and `process/` amendments are the
  maintainer's (STRUCTURE §1). It is applied by the lead, in one commit with the core
  extract.
- **The auditor**, who reads it against the memory-overwrite finding's event. That event is the artifact
  merging.

**Lead verdict (Proposal 6):** _pending_
**Maintainer acceptance (Proposal 6):** _pending_

## Proposal 7 — FR-432, FR-433 and FR-438: the carried packaging requirements, and the `07` NFRs that go with them

**The state.**
- **FR-433** (the Helm chart and Kubernetes manifests) is in P3 by `RL-1232` DP-1 (b). Its
  owner is the maintainer, and its event is "the P2 closure record, which names the Work that
  takes it".
- **FR-432** (container images) and **FR-438** (signed images and an SBOM) are carried to P3
  by `CR-1212` P12, with **no owner**. The lead's note on the records branch (`c2db4f72`) says
  so and leaves their owner to this review.
- At `1c8762d9`, `grep -n 'FR-43[238]\b' docs/roadmap.md` prints nothing, and **no P3 Work
  row names any of the three.** P3's Works (WK-676 to WK-682, WK-691) are governance Works.
- **A second gap of the same kind.** `CR-1212` G4 (d) carried NFR-526, NFR-527, NFR-530,
  NFR-533, NFR-536 and `00` NFR-461 to P3 "by a dated line", with **no owner**. But G4 itself
  reads "measured on the exit tree, **or carried with an owner**". As things stand, those six
  fail G4 at the exit.

**Options.**
- **(a) One new P3 Work: production packaging and supply chain.** It owns FR-432, FR-433 and
  FR-438, and NFR-533 (which follows FR-438) and NFR-461. The owner is the maintainer, like
  every WK row. The P2 closure record names it, which is DP-1's event.
- **(b) Assign them to an existing P3 Work.** None fits: each P3 Work is a governance
  capability.
- **(c) Leave them carried to "P3", with no row until P3 opens.** This is the decay
  `RL-909` names: an unowned carry with no event.

**Recommendation: (a).**
- The same row also takes **NFR-530** (RPO and RTO, with a restore exercised in CI), which is
  operational packaging too.
- **NFR-526, NFR-527 and NFR-536** measure paths that are built today: API metadata p95, Job
  submission latency, and trace propagation. They go to **WK-1178** for measurement on the
  exit tree, so that G4 reads "measured".
- Minting the row and its `WK-` id is the lead's roadmap edit, after acceptance. The row's
  `status: active` is the maintainer's (STRUCTURE §1).

**Lead verdict (Proposal 7):** _pending_
**Maintainer acceptance (Proposal 7):** _pending_

## Proposal 8 — G6 names "plan review 16"; restate it without the number

G6 reads: "A plan review 16 is filed after G1–G5 and before the demo" (`CR-1212` Proposal 1;
`docs/roadmap.md` `## P2`, the G6 bullet). **The number was a forecast.** §14's trigger fires
at every workstream close, so WK-672's close produced review 16 before G1–G5 were met. More
Work closes will produce more reviews before the demo.

**The maintainer's entry reads the other way.** `2026-09-29 16:05:14 BST · maintainer (acting
on the maintainer's behalf) · PLAN-REVIEW CADENCE: option C adopted by the maintainer; RFC + RL
+ amendments in one PR` ends: "Plan review 16 proceeds now under the current rule: it is
also P2 exit criterion G6." That entry and G6's own text cannot both hold. G6 says "after
G1–G5", and at this tree G1–G5 are not met. This review does not choose between them. The
lead reads the proposal below against that entry, and the maintainer decides.

**Options.**
- **(a) This review is G6.** G6 is amended by a dated line so that it drops "after G1–G5".
  - The review that follows the finished work is then option C's rule 1, "a full §14 plan
    review before each phase's exit demo", with no exit criterion of its own.
  - Cost: the exit criteria no longer require a review of the plan once the work is real.
    That is the order G6 was written to fix.
- **(b) G6 is restated without a number:** *"The pre-exit-demo plan review (`CLAUDE.md` §14;
  option C rule 1 once its RFC lands) is filed after G1–G5 are met and before the demo."*
  - This review is plan review 16, but it is not the review G6 counts.
  - Cost: the maintainer's 16:05:14 sentence is amended.

**Recommendation: (b).** Option C keeps a full review before every exit demo anyway (its rule
1). So (b) costs no extra review: it only fixes which review G6 counts, and it keeps G6's
ordering, which is G6's point. If the maintainer prefers (a), the dated amendment to G6 is
the lead's roadmap edit, quoting the maintainer.

**Lead verdict (Proposal 8):** _pending_
**Maintainer acceptance (Proposal 8):** _pending_

## Proposal 9 — the register rows that decayed to this review

`python3 scripts/register-owed.py review`, run at `1c8762d9` on this branch with a clean
register, prints **21 owed rows and 5 excluded**. Every row is disposed of below.

- **20 rows keep their current owner, as `CR-1212`'s accepted resolutions and `CR-1167`
  gave them.** The generator matches them because a **superseded opening** kept in the cell
  names "the §14 review". The live owner and event precede it in each cell. The rows are
  FR-240 (F-W9-3), F27, F28, F29, F31, F33, F48, F63, F74, F75, F86, F89, F90, F93, F94, F96,
  F97, F101, F113 and F114.
  - This is a **finding against the generator, not the rows**: it cannot tell a live
    decision from a superseded opening that is kept beneath it. **Proposed:** WK-1170 (the
    create-read-retire audit, which owns the gate-coverage cluster) teaches
    `register-owed.py` to read only the text before a cell's "This supersedes the opening
    kept below" marker, with a broken-input proof.
- **F61** is decided **accept**, and its event is "plan review 15, where it is re-read
  against artifact B's counters if they exist by then". Review 15 did not re-read them
  (`CR-1212` Output). **Re-read here:**
  - `python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py show`
    prints a `position` block and an empty `in_flight_expensive_verifications` list, and
    **no retry-counter entries**.
  - So the counters F61's acceptance waits on still do not exist.
  - **Proposed:** the acceptance stands, and the event moves to the pre-demo review (G6).
- **The 5 excluded rows** (F58, F87, F88, F91 and F92) each open with **Resolved
  2026-09-27** and cite a closing record (`CR-1167` or `CR-1164`). Their opening 330
  characters were read, and none shows a residual. No change.

**Observed, not a finding:** artifact B's `position` block reads `written_at
2026-09-28T16:26:22Z`, at tree `9f6bfed1`, about a day behind. Whether a watcher is running is
the lead's to check.

**Lead verdict (Proposal 9):** _pending_
**Maintainer acceptance (Proposal 9):** _pending_

## Proposal 10 — FR-218's authoring half, and FR-217's inlining, which it rests on

*(Added 2026-09-29, an input of the maintainer's entry `2026-09-29 16:15:10 BST · maintainer
(acting on the maintainer's behalf) · OLDER PLAN-REVIEW ITEMS: four worth doing, the rest
ignored`, item 1.)*

**The facts, re-verified at `1c8762d9`.**
- **FR-218** (`03:87`) prices a mid-term adjustment or a cancellation through a
  separately-versioned sub-graph (FR-217), mounted when `purpose ∈ {mid_term_adjustment,
  cancellation}`, and **declared on the Rating Version and version-pinned**. OQ-617 decided
  it on 2026-08-18 and marks it **Phase 2**.
- **Only the guard is built.** `_check_purpose_mount`
  (`packages/pricing-core/src/pricing_core/rating/score.py:393-413`, from `d6505e94`, #415)
  refuses an MTA or cancellation quote when `algorithm.sub_graphs` is empty. Its tests are at
  `test_rating_score.py:414`, `:425` and `:433`.
- **On the roadmap.** The entry says "git grep docs/roadmap.md: 0". The precise count is
  different: `git grep -n 'FR-218' origin/main -- docs/roadmap.md` prints **one** line,
  `:1280`. That line is the 2026-08-18 prose note of OQ-617's decision, not a Work row.
  **No Work row names FR-218**, so the entry's substance holds.
  - The reason is migration arithmetic. FR-218's pre-migration id was the 63rd of `03`'s
    scoped series (`docs/REDIRECTS.csv:1381`), appended on 2026-08-18.
  - WK-669's row (`docs/roadmap.md:599`) still lists its `03` ids as pre-migration bare
    ranges, which stop at the 59th. So it never reached the 63rd.
  - This is the bare-range defect that review 8 Q4 named.

**A second fact this review adds: FR-217's inlining is not built, although a closed Work
records it as delivered.**
- FR-217 (`03:86`) says sub-graphs are "versioned artifacts referenced by the parent and
  **inlined at bundle time**".
- FR-217's pre-migration id was the 6th of the same series (`docs/REDIRECTS.csv:1375`),
  inside WK-669's first range.
- WK-669's close record, `CR-838` (`docs/closures/CR-00838-*`), gives it **delivered** at
  `:39` ("marker-evidenced").
- What is built is the reference **shape**: `SubGraphRef` and `RatingAlgorithm.sub_graphs`,
  in `packages/model-schema/src/model_schema/rating.py:340`, `:350` and `:390`.
- **The inlining is not built.**
  - `grep -rn 'sub_graphs\|SubGraphRef\|mount_point' packages/pricing-core/src backend/src`
    finds only the guard's own lines in `score.py`. Nothing is in `compile.py`, where
    `compile_bundle` lives.
  - The guard's docstring says so directly: "sub-graph inlining (`SubGraphRef.mount_point`
    resolution, `compile_bundle`'s own TODO) is not built by any slice yet".
- So FR-218 cannot be authored until FR-217's inlining exists.
- Reopening WK-669's verdict is the maintainer's alone (`CLAUDE.md` §13). **Proposed:** the
  auditor files an `FD-` against `CR-838`'s FR-217 verdict ("delivered", on a
  reference-shape marker, for a requirement whose inlining clause is unbuilt). Its remedy
  travels with FR-218's owner, below.

**Why the gap is safe today.** The guard fails closed. An MTA or cancellation quote is
refused, never priced as new business, which is the silent failure FR-218 exists to prevent.
G2's demo is new business (`WF-699`) and needs neither requirement.

**Options.**
- **(a) A new P2 Work: sub-graph composition and MTA/cancellation pricing.**
  - Scope: FR-217's inlining limb (`compile_bundle` resolves `SubGraphRef.mount_point` and
    inlines the pinned sub-graph) and FR-218 (the `purpose` mount declared on the Rating
    Version and version-pinned, with the guard replaced by the real check).
  - Sequencing: after WK-674 and before WK-675, so that the DAG designer can author a
    sub-graph against a backend that inlines one. The designer's sub-graph view stays
    WK-675's.
  - Cost: a new G1 row in a budget-throttled phase.
- **(b) Fold both into WK-675** (the designer). Cost: a frontend Work would carry a compile
  and scoring change. That is scope crossing kinds, the smell the `phase-review` skill names
  from WK-664.
- **(c) Carry both to P3** under a named P3 Work, with the fail-closed guard as the interim.
  - Needs: a dated maintainer line amending OQ-617's "Phase 2" placement, and a dated note
    on FR-218.
  - Cost: P2's DAG designer (WK-675) ships without sub-graph composition, although FR-217
    is a `03` requirement that WK-669 claimed.

**Recommendation: (a).**
- OQ-617 placed FR-218 in P2 by decision.
- FR-217's inlining is P2 scope that a closed P2 Work reported as delivered.
- WK-675's designer depends on it.

If the maintainer's budget cannot carry a new Work, **(c)** is the honest fallback, by a
dated line. In either case the roadmap edit naming FR-217 and FR-218 on a row is the lead's.
The maintainer's item 4 (the spec-change rule "a new FR/NFR names its roadmap row", WK-1178)
is what stops this class recurring.

**Lead verdict (Proposal 10):** _pending_
**Maintainer acceptance (Proposal 10):** _pending_

## Proposal 11 — NFR-500: the branch it turns on, and its owner

*(Added 2026-09-29, an input of the same 16:15:10 entry, item 2.)*

**The facts at `1c8762d9`.**
- `03:1155`, NFR-500: "Trace storage: 1 % sampling of 50 M annual quotes stays under 200
  GB/year **with the sampled-trace schema**."
- It is measured **failing**: 516.07 GB/year, about 2.58× (`CR-926` plan review 10, `:51`).
- `CR-926` (`:72-86`) found that the requirement names **no** schema, and that the result
  turns on which schema is meant. It left the branch undecided:
  - trim the schema under F55 and re-measure; or
  - amend NFR-500 to state the encoding it budgets for.
- **The register row F37 (L79)** records the size figures:
  - one persisted 200-step `Trace` is 1,032,135 B uncompressed;
  - it is 14,523 B under gzip -6, which is 4 % of the budget.

  Its Decision cell reads "Amend NFR-500 to state the storage assumption its budget depends
  on".
- **Ownership.** `CR-1212` G4 (c), as accepted, already **owns** NFR-500's spec defect: F37
  "goes to a WK-1178 spec slice". What is missing is the **decision on the branch**, not an
  owner. No roadmap row names NFR-500 because WK-1178's row lists items by `FD-` and trigger.

**This is a design choice, so it goes to the decision-maker as an `OQ-`** (STRUCTURE §1). The
proposed question:

> **What does NFR-500's "sampled-trace schema" name?** (a) The `Trace` contract after F55's
> trim, measured uncompressed. (b) The persisted encoding, with a named compression, whatever
> the in-memory shape. (c) Both: the trimmed `Trace`, persisted with a named compression, the
> budget stated for the persisted bytes.

**Recommended answer for the decision-maker: (a).** The reasons:
- It lets the budget rest on a shape that `model-schema` defines and a test can measure, not
  on a storage codec that a later infrastructure choice can change silently.
- It is also the remedy Proposal 3 (a) builds anyway: one lever, three rows.
- An extrapolation, not a measurement: F35's minimal per-node entry is about 130 B, against
  a mean of 5,859 B, over 191 entries. So a trimmed trace would be about 25 kB, and 500,000
  traces about 12 GB/year.
- FR-259's 100 % of declines and errors raises the count above 500,000. Even so, that is an
  order of magnitude under 200 GB.
- The slice re-measures it, and **this figure is not a verdict**.

**Placement:**
- the `OQ-` is filed and ruled by the decision-maker **with** Proposal 3's ruling on what a
  `TraceStep` records;
- NFR-500 is re-measured **in the same WK-1178 slice**, on the exit tree;
- its dated `03` amendment, naming the schema by contract path (RFC-777), lands with that
  ruling.

It is not placed in WK-674: it is a trace-size question, not a deployment one.

**Lead verdict (Proposal 11):** _pending_
**Maintainer acceptance (Proposal 11):** _pending_

## 1. Completion — derived, never recalled

- **WK-672**'s four slices have merged:
  - S1: #853, with its ledger `LG-1182` closed by #858;
  - S2: #867, with `LG-1204` closed by #870;
  - S3: #886, with `LG-1225` closed by #898, and #897 for S3's owed item;
  - S4: #901, whose `LG-1230` the WK-672 close record closes. Its §13 scope
  audit and verdicts are the auditor's record on `wk672-close`. See *Consistency with the
  WK-672 close record*. **This review does not re-derive them**: the skill says a fresh audit
  that has just covered the ground is cited, not repeated.
- The `## P2` Works at `1c8762d9`, by the reader `awk 'index($0,"## P2 ")==1{p=1}
  index($0,"## P3 ")==1{p=0} p && /^### WK-/{w=$2} p && /^status:/{print w, $2}'
  docs/roadmap.md`:
  - **closed (9):** WK-668, WK-669, WK-670, WK-671, WK-693, WK-694, WK-695, WK-696, WK-697;
  - **active (8):** WK-672 (closing), WK-673, WK-674, WK-675, WK-690, WK-1169, WK-1170,
    WK-1178.
- **Map plans:** WK-674's is `PL-1237` (#843, merged after this tree as `6ae8a99a`, still
  `draft`), WK-673's is #844 (open, with its ruling #845), and
  WK-690's is #871 (open, with its ruling #847). None is `active`, so no duration band is
  derivable yet. This is the same position as `CR-1212` Proposal 2's "honest bands".

## 2. Omission — what would nobody notice was missing?

Seven omissions:
- **The permission vocabulary's second definition** (Proposal 1), and 12 of 16 names in a
  built-in role that `06` shows a reader but that grant nothing.
- **F35's reach into `score/compare`** (Proposal 3). The traced path is not off-path any
  more.
- **The dedicated host as a P2-exit dependency** (Proposal 4). It is written into `PL-1237`
  as a dependency but into no exit criterion.
- **Six NFRs carried with no owner, against G4's own wording** (Proposal 7).
- **The write boundary** (Proposal 6).
- **FR-218 on no Work row** (Proposal 10). It fell outside a legacy bare range, and FR-217's
  inlining is reported delivered but is not built.
- **NFR-500's undecided branch** (Proposal 11). An owner was named at review 15, but the
  decision the owner needs was not.

## 3. Skills and research — the gap analysis

- **Behind the code:** the harness's memory invitation runs ahead of the charters (Proposal 6).
- **A skill rule proposed for WK-1178's Dependabot handling:** a major bump of a pricing-path
  engine is a governed change, never a bot merge. The `dependabot.yml` ignore list is where
  it binds (Proposal 2). No new skill is proposed. `git-hygiene` is where a bot-PR rule would
  live if the lead wants it written.
- **No other change.**

## 4. Document drift

- **FD-1194's register cell** names #852 as held. #852 has been closed since
  `2026-09-28T14:05:08Z`, and its successor is #857 (Proposal 2).
- **OQ-1233 and OQ-1234 are on a gate already passed** (*Before Phase 2*, Proposal 5).
- **`06`'s Pricing Actuary role block** names 12 permissions that the vocabulary does not
  have (Proposal 1).
- **G6's "plan review 16"**, against the maintainer's 16:05:14 sentence (Proposal 8).
- **`CR-838`'s FR-217 "delivered"** against unbuilt inlining (Proposal 10).
- **NFR-500 names no schema** (`03:1155`; Proposal 11).
- **`CR-1212` G4 (d)'s owner-less carries** against G4's text (Proposal 7).
- **Specs against code**, at the depth this review read: the `RL-1236` amendments are
  present at `06:62`, `:218` and `:279`, and `03` FR-272's amendments agree with `RL-1232`.
  No other disagreement was looked for. `spec-reconciler` was not run for `03`, `06` or
  `07`, and this is said rather than implied.

## 5. Shape — is the cut still right?

- **A new P3 Work** for production packaging and supply chain (Proposal 7).
- **A new P2 Work** for sub-graph composition and MTA/cancellation pricing (Proposal 10),
  placed between WK-674 and WK-675.
- **WK-1178 grows** (Proposals 1, 2, 3 and 11). This is the smell the skill names: "a row nothing
  can be said to have closed". It is mitigated in two ways. WK-1178 is exempt from G1 by
  design. And each item is its own `SL-` with a leaf plan and a slice audit, so each closes
  on its own record. **Proposed:** the F35/F55 lever is cut as a slice with a leaf plan
  (planner) after the decision-maker's ruling. It is not folded into a maintenance PR.
- **The sequence** accepted in `CR-1212` Proposal 2 stands (WK-674, then WK-673, then WK-675;
  WK-690 independent; then WK-1170, then WK-1169). **One insertion:** the F35/F55 slice runs
  before WK-674 Slice 5 (Proposal 3 (a)). `delivery-process.md` §8 stands: one slice at a
  time.
- **The freeze gates.** `CR-1212`'s acceptance has the lead propose three freeze dates and a
  target "after WK-672 closes". That trigger fires now. Proposal 4's host answer is given.
  Proposal 3's slice and Proposal 10's Work still move any date, so the dates are proposed
  after those two verdicts.
- **No existing Work is proposed for a split or a move.**

## Consistency with the WK-672 close record

_Filled after reading the auditor's draft on `wk672-close`._

## Output

- **Retry counters (RFC-895 artifact B):** read with `write_runtime_state.py show`. There
  are no `project`- or `phase`-layer `replan`/`fix` entries, and so still no pilot data for
  question 5. **No change.**
- **Proposals resolved by the maintainer while this review was drafting:**
  - Proposal 2: #882, #857 and #881; not #877–#879;
  - Proposal 4: the host fallback.

  Both come from the entry of 2026-09-29 16:08:24 BST, recorded under each proposal.
- **Proposals that need the maintainer's dated line:** 1, 2 (#877–#879 only), 3, 5, 6, 7, 8,
  9, 10 and 11.
- **Routing, if accepted.** Each proposal, its record and its owner. This is given in the
  form of the maintainer's 16:12:57 entry, Part 2. That entry is future-facing and does not
  bind this review, but the table costs nothing.

  | Proposal | Record | Owner |
  |---|---|---|
  | 1 | `RL-` (or ADR) + `06` amendment; the check | decision-maker; WK-1178 |
  | 2 | `FD-` (zen-engine upgrade); `dependabot.yml` PR | auditor / lead; WK-1178 |
  | 3 | `RL-` (TraceStep contents); `SL-` in WK-1178 | decision-maker; planner |
  | 4 | G4 roadmap row; `PL-1237` amendment | lead; planner (at #892's turn) |
  | 5 | OQ-1233 → WK-688 row and gate move; OQ-1234 and OQ-1235 → `RL-` | lead; decision-maker |
  | 6 | `delivery-process.md` §3 + core extract + `reporter.md` | the maintainer's; applied by the lead |
  | 7 | new P3 `WK-` row; WK-1178 items | lead (the row); the maintainer (`active`) |
  | 8 | G6 dated restatement | lead, quoting the maintainer |
  | 9 | `FD-` against `register-owed.py`; F61's event | auditor; WK-1170 |
  | 10 | new P2 `WK-` row; `FD-` against `CR-838`'s FR-217 verdict | lead / the maintainer; auditor |
  | 11 | `OQ-` then `RL-` + `03` amendment; re-measurement in Proposal 3's slice | decision-maker; WK-1178 |

- **For the lead's roadmap and register edits, after acceptance:**
  - OQ-1233's and OQ-1234's gate moves;
  - FR-453 named on WK-688's row;
  - the P3 packaging Work row;
  - G6's restatement, or its dated amendment (Proposal 8);
  - FR-217 and FR-218 on a Work row (Proposal 10);
  - the host-fallback wording in G4 (Proposal 4);
  - F35's register owner;
  - FD-1194's cell (the auditor's register pass).

## Verdict

- Every input the lead's brief required has a written proposal with options and a
  recommendation: N3 (1), #852 (2), F35 and NFR-490 at exit (3), OQ-1233 to OQ-1235 (5),
  the memory-overwrite finding (6), and FR-432, FR-433 and FR-438 (7). F38 and the dedicated host are Proposal 4.
- The maintainer's two later inputs have one each: FR-218 (10) and NFR-500 (11).
- Every register row decayed to this review has a disposition (9).
- All five questions have a written answer.
- **Nothing here binds** until the lead's verdicts and the maintainer's dated line below.

## Acceptance

**Maintainer acceptance (plan review 16, Proposals 1–11, except the parts of 2 and 4 already
accepted in the 16:08:24 entry):** _pending_ — dated when given.

## Sources

- The maintainer's channel entries of 2026-09-29, quoted by heading: 15:26:00 (STRUCTURE),
  15:36:43 (SCOPE: NFR-490 / F35), 14:15:43, 14:17:56 and 14:20:41 (the WK-674 answers),
  16:05:14 (the plan-review cadence), 16:08:24 (the host fallback and Dependabot), 16:12:57
  (routed outputs) and 16:15:10 (the older plan-review items). The
  channel file is local and is not in the repository.
- `docs/roadmap.md` (`## P2`, §10), `docs/findings/register.md`, `docs/open-questions.md`,
  `docs/specs/03-rating-engine.md`, `06-governance.md` and `07-platform.md`,
  `packages/model-schema/src/model_schema/permissions.py` and `rating.py`,
  `packages/pricing-core/src/pricing_core/rating/score.py` and `compile.py`,
  `backend/src/app/api/score.py`, `docs/REDIRECTS.csv`, `CR-838` and `CR-926`,
  all at `1c8762d9`.
- `PL-1237` at #843's head `306e42b9`, and the memory-overwrite finding and `c2db4f72` on `records-2026-09-29`
  at `bc55a975`.
