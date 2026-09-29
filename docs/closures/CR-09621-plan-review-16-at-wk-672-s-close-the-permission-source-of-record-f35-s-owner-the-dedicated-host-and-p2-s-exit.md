---
id: CR-9621
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
id `CR-9621`.** It is minted at the merge turn with `python3 scripts/doc-id.py next --ref
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

**This review is not `CR-1212`'s G6.**
- G6 reads "A plan review 16 is filed after G1–G5 and before the demo". G1–G5 are not met,
  so the pre-exit-demo review G6 names is **still owed**.
- The maintainer's entry of 2026-09-29 16:05:14 BST said that this review "is also P2 exit
  criterion G6". The maintainer withdrew that at 16:21:36 BST, in the entry headed "answers
  to the lead's corrections 1–3 and the planner's (a) and (b)", item (b).
- See Proposal 8.

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
  - The branch is rebased onto `6ae8a99a`, so that `PL-1237` resolves. The only commit
    between `1c8762d9` and `6ae8a99a` is #843 itself, so the tree read is otherwise
    unchanged.
  - The records PR, read first at branch `records-2026-09-29` `bc55a975`, merged as #902
    (`49604a31`). This branch merged it in (`git merge origin/main`). #902 carries two things
    this review cites:
    - **`FD-1238`**, "A team member overwrote the user's auto-memory index, and the restore
      missed 27 index lines". It was cited by title before it was minted.
    - the lead's P3-carry note (`docs/roadmap.md`, the note headed "2026-09-29: requirements
      carried into Phase 3 without a Work").
- **The WK-672 close record** was read on branch `wk672-close` at `f7ca1402`, before this
  review was filed. It is a `CR- kind: work`, still under a working id, so this record cites
  it as "the WK-672 close record". The lead substitutes its minted id at this record's merge
  turn.
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

**Lead verdict (Proposal 1), 2026-09-29:** **ADOPTED, (c).** The measurement was re-checked by the lead at `1c8762d9`: the enum has 24 members, and the Pricing Actuary block names 16 permissions, 12 of them not enum members. That is the second definition `CLAUDE.md` §2 forbids, and (c) is the only option with a check the failure cannot survive. The DP-6 finding obligation is recorded as discharged by `RL-1236`, with no `FD-`. The decision-maker writes the `RL-` and the `06` amendment. WK-1178 builds the check before WK-690's `custom_objective:author`.
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
- **#882 is not merged.** A WK-1178 PR (#903) adds an ignore rule to `.github/dependabot.yml`
  for **every semver-major bump of zen-engine**, and files an `FD-` for a governed upgrade
  under WK-1178, with a spike first. Closing #882 is the user's action.
  - The first entry named "major version 2" only. The maintainer's 16:21:36 entry, item 1,
    widened it on this ground: "Any future major (for example 3.0) needs the same governed
    spike, and a 'major 2 only' rule would let it through".
- **#857, then #881.** The lead runs a full local two-half gate on each PR's head, and the
  user merges on green. #881 is re-gated if #857's merge changes its base.
- **FD-1194's stale cell** is updated by the auditor in the next records PR.

**Resolved in full 2026-09-29 by the maintainer, by the user's delegation** (entry `2026-09-29 16:25:49 BST · maintainer (acting on the maintainer's behalf) · BLOCKER DECISIONS by delegation: #882, the Dependabot merges, the Actions majors, FR-217, FD-1238, and the WK-672/PR16 acceptance`, items 1–3):
- **#882 is closed** by the maintainer, with a comment citing #903 and the zen-engine
  upgrade finding.
- **#857, then #881, merge when both of these hold at the PR's exact head:**
  - the lead's local full two-half gate is green, with in-log SHA and RC and archived
    evidence;
  - GitHub CI is success on every workflow.

  The maintainer merges them one at a time, with `--match-head-commit`. #881 is re-checked
  against the main that #857 produces.
  - #857's last CI success was at `2026-09-28T20:48:38Z`. That predates WK-672 S3 and S4's
    changes to `docs/contracts/openapi/generated.json`, which the WK-672 close record also
    notes. So the CI condition means a fresh run at a head on current main.
- **#877, #878 and #879 are removed from this review's proposals.** Each merges only if every
  CI workflow passes on its own head, one at a time, and the maintainer merges it. If one
  fails, the maintainer closes it. The lead then adds that action's major version to
  `dependabot.yml`'s ignore list in a WK-1178 PR, with an `FD-` for a governed upgrade.
  This review's earlier recommendation, "merge one at a time after reading each release's
  runner and Node requirement", is superseded by that rule.

**Lead verdict (Proposal 2), 2026-09-29:** **Resolved by the maintainer's entries of 16:08:24 and 16:25:49; no lead verdict is needed.** The lead recorded the #903 zen-engine rule's scope (all semver-major) as a departure, which the maintainer accepted on the corrected ground (16:21:36).
**Maintainer acceptance (Proposal 2):** given, in the 16:08:24, 16:21:36 and 16:25:49 entries
above. Nothing in Proposal 2 remains open.

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
    The same ruling covers the WK-672 close record's finding that a trace omits the `input`
    and `output` steps (see *Consistency with the WK-672 close record*).
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

**Lead verdict (Proposal 3), 2026-09-29:** **ADOPTED, (a).** The lead re-checked the load-bearing fact at `1c8762d9`: `score_compare` calls `score_one(…, trace=True)` for both sides (`backend/src/app/api/score.py:358-362`), and `own_change` is derived from `consumed` (`03:731`, with its limit at `:733`). F35's remedy is therefore on a P2 deliverable's path and interacts with §4.10. The owner is WK-1178: one slice sequenced before WK-674 Slice 5, after one decision-maker ruling on `TraceStep` contents (F35, F55, the trace input/output finding and Proposal 11's question). Fallback (c) is only by the maintainer's dated G4 (b) line, never silent. On acceptance, F35's register row names WK-1178.
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

**Lead verdict (Proposal 4), 2026-09-29:** **Resolved by the maintainer's 16:08:24 entry.** The lead has applied the G4 row wording, quoting it, on #892 (`69da042e`). PL-1237 carries it (`d7fbf4e0`).
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

**Lead verdict (Proposal 5), 2026-09-29:** **ADOPTED.** OQ-1233: (b), FR-453 (both limbs) named on WK-688's row, with the OQ moved to Before Phase 4. This is a scope question, so the recommendation goes to the maintainer; the roadmap edits are the lead's after acceptance. OQ-1234 and OQ-1235 are the decision-maker's to rule by `RL-`, OQ-1234 on a new gate row, Before WK-674 Slice 2. The declined limb of OQ-1233's own option (c) is noted, correctly, as not firing.
**Maintainer acceptance (Proposal 5):** _pending_

## Proposal 6 — FD-1238: the write boundary that no charter states

**The finding.** `FD-1238` records that on
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
  ruling relayed in `FD-1238`: `~/gi-pricing-plan.local/handover/eta.md`.
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
- **The auditor**, who reads it against `FD-1238`'s event. That event is the artifact
  merging.

**Partly resolved 2026-09-29 by the maintainer, by the user's delegation** (entry `2026-09-29 16:25:49 BST · maintainer (acting on the maintainer's behalf) · BLOCKER DECISIONS by delegation: #882, the Dependabot merges, the Actions majors, FR-217, FD-1238, and the WK-672/PR16 acceptance`, item 5):
- **`.claude/roles/reporter.md` is amended** with a dated line: "Writes only
  `~/gi-pricing-plan.local/handover/eta.md` and the external channel. Never `~/.claude/`
  (memory, settings, projects) nor any governed file; a note worth keeping is proposed to
  the lead, not written".
- The lead drafts it in a WK-1178 PR, the auditor checks it, and the maintainer gives the
  ACK. FD-1238's decision becomes "fixed by the charter amendment".
- That is option (a) for the one role the incident involved.

**What stays a proposal:** option (b), the team-wide boundary for the six other roles, whose
charters still say nothing about `~/.claude/`. The harness offers every session a memory
directory, not only the reporter's, so the gap `FD-1238` found is not closed for them.

**Lead verdict (Proposal 6), 2026-09-29:** **ADOPTED, (b), with evidence the review did not have.** A **second** member (auditor-b-2, 2026-09-29 15:28:47–51Z) wrote into the user's project memory, because the rule had reached it only by brief, and it had not reached it at all. The maintainer removed the entry. That is the gap this proposal names, occurring again within two hours. The team-wide boundary in `delivery-process.md` §3 (the proposed text) and the re-derived core extract are the maintainer's to accept. The lead drafts them as a WK-1178 PR after acceptance. #904 already carries the reporter's line, with the marker file listed and disclosed.
**Maintainer acceptance (Proposal 6):** the reporter's line is given (16:25:49 item 5); the team-wide boundary is _pending_.

## Proposal 7 — FR-432, FR-433 and FR-438: the carried packaging requirements, and the `07` NFRs that go with them

**The state.**
- **FR-433** (the Helm chart and Kubernetes manifests) is in P3 by `RL-1232` DP-1 (b). Its
  owner is the maintainer, and its event is "the P2 closure record, which names the Work that
  takes it".
- **FR-432** (container images) and **FR-438** (signed images and an SBOM) are carried to P3
  by `CR-1212` P12, with **no owner**. The lead's note on the records branch (`c2db4f72`) says
  so and leaves their owner to this review.
- At `1c8762d9`, `grep -n 'FR-43[238]\b' docs/roadmap.md` printed nothing. #902
  (`49604a31`) has since added a prose note that lists them and says: "No Work is created by
  this note. Creating one is a scope decision, and the maintainer's." **No P3 Work row names
  any of the three.** P3's Works (WK-676 to WK-682, WK-691) are governance Works.
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

**Lead verdict (Proposal 7), 2026-09-29:** **ADOPTED, (a).** One new P3 Work, production packaging and supply chain, owns FR-432, FR-433 and FR-438, and NFR-530, NFR-533 and NFR-461. NFR-526, NFR-527 and NFR-536 go to WK-1178 for measurement on the exit tree. Otherwise G4's "carried with an owner" fails for them at exit. The row and its id are the lead's roadmap edit after acceptance; `active` is the maintainer's.
**Maintainer acceptance (Proposal 7):** _pending_

## Proposal 8 — this review is not G6; restate G6 without the number

G6 reads: "A plan review 16 is filed after G1–G5 and before the demo" (`CR-1212` Proposal 1;
`docs/roadmap.md` `## P2`, the G6 bullet). **The number was a forecast.** §14's trigger fires
at every workstream close, so WK-672's close produced review 16 before G1–G5 were met. More
Work closes may produce more reviews before the demo.

**Resolved 2026-09-29 by the maintainer: this review is not G6.**
- The draft at `34c79f64` recorded a conflict. The maintainer's entry of 16:05:14 BST ended
  "it is also P2 exit criterion G6", against G6's "after G1–G5".
- It offered two options:
  - (a) this review is G6, and G6 drops "after G1–G5";
  - (b) G6 is restated to count the pre-exit-demo review.

  It recommended (b).
- The maintainer answered at 16:21:36 BST ("answers to the lead's corrections 1–3 and the
  planner's (a) and (b)", item (b)): "my 16:05:14 statement 'PR16 is also P2 exit criterion
  G6' was WRONG … G6 stays as written: the review before the P2 exit demo, still owed later,
  and still required under Option C's Part 1".
- **So option (a) is withdrawn, and G6 is owed.**

**What remains a proposal, for the user:** restate G6 without the number, as *"The
pre-exit-demo plan review (`CLAUDE.md` §14; option C rule 1 once its RFC lands) is filed
after G1–G5 are met and before the demo."*
- The maintainer said that no restatement is needed on the maintainer's account, and left
  this proposal for the user to accept or decline.
- **The case for it:** "plan review 16" now names a review that is not G6. A reader who
  checks G6 by its number would find this record and read G6 as met.
- The restatement is the lead's roadmap edit, quoting the acceptance.

**Lead verdict (Proposal 8), 2026-09-29:** **ADOPTED, for the user to accept.** Restate G6 without the number. "Plan review 16" now names a review that is not G6, and a reader who checks G6 by its number would read it as met. The roadmap edit is the lead's, quoting the acceptance.
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

**Lead verdict (Proposal 9), 2026-09-29:** **ADOPTED, AMENDED on one point.** The lead re-ran `register-owed.py review` on a clean committed tree: 26 bullets, that is 21 owed and 5 excluded, as stated. The 20 superseded-opening rows keep their owners, and the generator defect goes to an auditor `FD-` for WK-1170. F61's acceptance stands, with its event moved to the G6 review. **The amendment:** two of the 5 "excluded, resolved" rows are F58 ("Artifact B has no live writer") and F91 ("the runtime-state writer has not run since 02:03Z"). Artifact B (`~/gi-pricing-plan.local/handover/runtime-state.json`) was last written `2026-09-28T16:26:22Z`, about a day stale at this verdict. So the condition those resolutions closed has recurred. The auditor re-reads F58 and F91 against that mtime, and a regression is a new `FD-` (the watcher's writer), not silence.
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
- **An `FD-` against `CR-838:39`, ordered by the maintainer.** The entry of 2026-09-29
  16:21:36 BST, item (a), orders the auditor to file it, quoting:
  - FR-217's clause;
  - `CR-838:39`;
  - the `compile.py` and docstring evidence, at a named tree.

  It is being filed after this draft, so this record cites it by its subject, "`CR-838`
  records FR-217 as delivered, but bundle-time inlining is not built", and not by an id.
- **Decided 2026-09-29, WK-669 is not reopened.** This is the entry `2026-09-29 16:25:49 BST ·
  maintainer (acting on the maintainer's behalf) · BLOCKER DECISIONS by delegation: #882, the
  Dependabot merges, the Actions majors, FR-217, FD-1238, and the WK-672/PR16 acceptance`,
  item 4, on the user's delegation. It supersedes the 16:21:36 entry, which had left the
  reopen question to the user.
  - The auditor files the `FD-`.
  - The auditor adds a dated correction note to `CR-838`'s verdict: "guard delivered;
    `sub_graphs` inlining NOT delivered → FD-<n>". The verdict text itself is not rewritten.
- **This review routes the remedy**, bundle-time inlining, to the Work that takes FR-218's
  authoring half. Both concern the same mid-term-adjustment sub-graph. That Work is the
  subject of the options below, and it must carry both.

**~~Why the gap is safe today.~~ Why the gap was believed safe.** ~~The guard fails closed. An
MTA or cancellation quote is refused, never priced as new business, which is the silent
failure FR-218 exists to prevent.~~ G2's demo is new business (`WF-699`) and needs neither
requirement.

*(Corrected 2026-09-29, by the planner, on the lead's instruction. The struck sentences were
false when written.)*
- **What the finding shows.** The finding "`CR-838` marks FR-217 delivered, but its
  versioned-artifact pin and bundle-time inlining are not built" (auditor-a-2, branch
  `fd-fr217-cr838`, not yet minted; cited by subject) demonstrated at `49604a31` that the
  guard accepts **any non-empty** `sub_graphs`. With a reference to a sub-graph that does not
  exist, a cancellation and an MTA were quoted as new business. That is the silent failure
  FR-218 names. It is not a refusal.
- **What this review read, and what it did not check.** It read the guard's condition,
  `… and not algorithm.sub_graphs` (`packages/pricing-core/src/pricing_core/rating/score.py:406`),
  correctly, as refusing only an **empty** list. It then took the docstring's "conservative,
  forward-safe approximation" as the property, without checking the non-empty case. With
  inlining unbuilt, nothing resolves a mount, so a non-empty list proves nothing.
- **What it changes.** Proposal 10's recommendation (a) is unchanged. Fallback (c) loses its
  interim: without a fixed guard, carrying both requirements to P3 leaves FR-218's failure
  live. The lead's verdict below adds the interim fix under WK-1178: refuse every MTA and
  cancellation quote until inlining exists, whatever `sub_graphs` holds, proved with a
  bogus reference.

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
- **(c) Carry both to P3** under a named P3 Work, ~~with the fail-closed guard as the interim~~
  *(corrected 2026-09-29: the guard does not fail closed (see the correction above); the
  interim is the WK-1178 fix in the lead's verdict)*.
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

**Lead verdict (Proposal 10), 2026-09-29:** **ADOPTED, (a), AMENDED: the "safe today" premise is FALSE.** auditor-a-2's finding "`CR-838` marks FR-217 delivered, but its versioned-artifact pin and bundle-time inlining are not built" (branch `fd-fr217-cr838`, not yet minted) demonstrated at `49604a31` that `_check_purpose_mount` accepts ANY non-empty `sub_graphs`. With `sub_graphs=[sub_graph:does-not-exist@1 at s_nowhere]`, a cancellation and an MTA were quoted as new business, payable 1507, at the `pricing-core` level. That is FR-218's named silent failure, not a fail-closed refusal. So, in addition to the new P2 Work, the lead adds an **interim fix now, under WK-1178**: the guard refuses every MTA and cancellation quote until inlining exists, whatever `sub_graphs` holds, with a broken-input proof using a bogus ref. Whether the end-to-end path (save, then compile, then score) accepts such a version is being checked. If it does, the finding is HIGH. The new Work's row and sequencing are as recommended.
**Maintainer acceptance (Proposal 10):** WK-669 not reopened and `CR-838` corrected, both given (16:25:49 item 4); the owning Work is _pending_.

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

**Lead verdict (Proposal 11), 2026-09-29:** **ADOPTED.** NFR-500's branch goes to the decision-maker as an `OQ-`, with the recommended answer (a), the trimmed `Trace` contract measured uncompressed. It is ruled together with Proposal 3's `TraceStep` ruling and re-measured in the same WK-1178 slice. The ~12 GB/yr figure is correctly labelled an extrapolation, not a verdict.
**Maintainer acceptance (Proposal 11):** _pending_

## Proposal 12 — who builds G2's demo: the real freMTPL2 rating algorithm

*(Added on reading the WK-672 close record, on `wk672-close` at `f7ca1402`, and
its FD-1209 row.)*

**The gap.**
- G2 is "`WF-699` end to end on the freMTPL2 seed, with its deploy step". At `1c8762d9` the
  seed's only algorithm is `_demo_algorithm()` (`examples/fremtpl2/model.py:327`), and no
  `WF-699` journey test exists (FD-1209).
- FD-1209 is `deferred with an owner — the lead`, and its event is the real algorithm
  existing before G6's review. **An owner is not a Work.** No roadmap row plans:
  - `WF-699` Phases A to C on the approved models (rate tables seeded from the models, a
    Rating Algorithm composed over them, a Rating Version compiled with pins);
  - nor the journey test.
- Every P2 Work builds a *capability* the demo uses. None builds the demo.

**Options.**
- **(a) An "Exit demo" row under `## P2`,** in Phase 1b's form (`docs/roadmap.md`, the Phase
  1b "Exit demo" row). Owner the lead.
  - Scope: the real freMTPL2 algorithm in the seed, `WF-699` Phases A to E and its deploy step
    as one scripted journey, and the journey test that cites `WF-699` by id.
  - Sequenced after WK-673 and WK-674 (it needs dislocation and deployment). It can be cut
    in parallel with WK-675 where no view is needed, still one slice at a time (§8).
- **(b) A WK-1178 slice.** Cost: the phase's own acceptance artifact would sit in the
  maintenance Work that G1 exempts, so the demo's build would escape the Work-close audit.
- **(c) Fold it into WK-675,** the last feature Work. Cost: a frontend Work would carry the
  seed's pricing content. That is scope crossing kinds.

**Recommendation: (a).** Phase 1b's exit demo was its own row, and it closed with its own
record (`CR-822`). Making G2's build a row gives FD-1209's event a Work to discharge it. It
also gives the two `WF-699` rulings above a concrete consumer.

**Lead verdict (Proposal 12), 2026-09-29:** **ADOPTED, (a).** An "Exit demo" row under `## P2`, in Phase 1b's form, owned by the lead. It is sequenced after WK-673 and WK-674, and it discharges FD-1209's event. The two `WF-699` rulings (D4 against FR-261, E2 against FR-257) go on a new §10 gate, Before the P2 exit demo, for the decision-maker. The row is the lead's roadmap edit after acceptance.
**Maintainer acceptance (Proposal 12):** _pending_

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
- **G2's demo is built by no Work** (Proposal 12; FD-1209, from the WK-672 close record).

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
- **G6's "plan review 16"** names a review that is not G6. The maintainer's 16:05:14
  sentence saying otherwise was withdrawn at 16:21:36 (Proposal 8).
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

**Read:** the auditor's `CR- kind: work` for WK-672, on branch `wk672-close` at `f7ca1402`. It
has a working id, so it is cited here by its branch and head. Its tree is the same
`1c8762d9`. Its three new findings are also working ids, so they are cited by subject:
- the `WF-699` D4 / FR-261 grid disagreement;
- the `WF-699` E2 route / FR-257 disagreement;
- the trace that omits `input` and `output` steps (FR-258).

**Where the two records agree:**
- **FD-1194 / #852.** Both find #852 closed unmerged at `2026-09-28T14:05:08Z`, with #857 as
  its successor, and neither lets the lead or the auditor merge it (Proposal 2).
- **The freeze gates.** Both name the lead's three freeze dates and target, owed after this
  close (its *Binding plan-review conditions* item 1; this review's question 5).
- **G6.** Its FD-1209 row restates the event "before plan review 16" as *before `CR-1212`
  G6's pre-demo plan review*, because "plan review 16" names two things. This review is not
  G6 (Proposal 8), so the two readings agree.
- **The measurements on WK-674.** Its NFR-502 and NFR-499 rate-limit limbs go to WK-674.
  Proposal 4's host fallback governs how NFR-502 is recorded.
- **FR-262.** Its UI limb is reassigned to WK-675. This review's Proposal 3 fact 2 relies on
  the backend limb being the traced `score/compare`.

**What its record adds, and where this review takes it:**
- **FD-1209: the freMTPL2 demo has no real rating algorithm, and so G2 cannot yet run.** The
  close record keeps it `deferred with an owner — the lead`, and it is "not a WK-672
  deliverable". But **no Work row builds that algorithm**: `WF-699` Phases A to C on the
  approved models, and a journey test. This is a G2 risk with an owner and no Work. See
  **Proposal 12**.
- **The two `WF-699` disagreements (D4, E2).** G2 *is* `WF-699` end to end. A demo that
  follows D4 or E2 as written would demonstrate a step the spec does not promise, or a route
  that refuses a draft. So both decision-maker rulings are needed **before the exit demo**.
  **Proposed:** the lead places them on a new roadmap §10 gate row, *Before the P2 exit
  demo*, with FD-1209.
- **The trace that omits `input` and `output` steps, where FR-258 says "every step".** This is
  the same question as Proposal 3's ruling: what a `TraceStep` records.
  **Proposed:** the decision-maker rules on it **in the same `RL-`** as F35/F55's trim and
  Proposal 11's NFR-500 `OQ-`. One ruling on the trace shape, not three.
- **FR-1221's workspace limb** is `fix before close` (test-only), with a WK-1178 fallback.
  That is a Work-close matter and needs nothing from this review.

**No disagreement found.** Nothing in the WK-672 close record contradicts a proposal here, and nothing here
contradicts a verdict there.

## Output

- **Retry counters (RFC-895 artifact B):** read with `write_runtime_state.py show`. There
  are no `project`- or `phase`-layer `replan`/`fix` entries, and so still no pilot data for
  question 5. **No change.**
- **Resolved by the maintainer while this review was drafting:**
  - Proposal 2 in full: #882 closed, #857 then #881 on green gates and CI, #877–#879 on
    their own CI;
  - Proposal 4: the host fallback.

  These come from the entries of 2026-09-29 16:08:24, 16:21:36 and 16:25:49 BST.
- **Partly resolved:**
  - Proposal 6: the reporter's charter line (16:25:49 item 5). The team-wide boundary stays a
    proposal.
  - Proposal 8: this review is not G6 (16:21:36). The restatement stays a proposal.
  - Proposal 10: WK-669 is not reopened, and `CR-838` gets a dated correction (16:25:49
    item 4). The owning Work for FR-217's inlining and FR-218 stays a proposal.
- **Proposals that need the maintainer's dated line:** 1, 3, 5, 6 (the team-wide boundary),
  7, 8 (the restatement), 9, 10 (the owning Work), 11 and 12.
- **Acceptance.** Per 16:25:49 item 6, the maintainer reviews this record once it is filed
  and gives its acceptance line on the user's delegation, after the maintainer's own evidence
  check.
- **Routing, if accepted.** Each proposal, its record and its owner. This is given in the
  form of the maintainer's 16:12:57 entry, Part 2. That entry is future-facing and does not
  bind this review, but the table costs nothing.

  | Proposal | Record | Owner |
  |---|---|---|
  | 1 | `RL-` (or ADR) + `06` amendment; the check | decision-maker; WK-1178 |
  | 2 | resolved: the maintainer merges on the stated conditions; `FD-`s and ignore rules on failure | the maintainer; lead (WK-1178) |
  | 3 | `RL-` (TraceStep contents); `SL-` in WK-1178 | decision-maker; planner |
  | 4 | G4 roadmap row; `PL-1237` amendment | lead; planner (at #892's turn) |
  | 5 | OQ-1233 → WK-688 row and gate move; OQ-1234 and OQ-1235 → `RL-` | lead; decision-maker |
  | 6 | `reporter.md` line (decided); `delivery-process.md` §3 + core extract for the rest (proposed) | lead drafts, auditor checks, the maintainer ACKs |
  | 7 | new P3 `WK-` row; WK-1178 items | lead (the row); the maintainer (`active`) |
  | 8 | G6 restatement (if the user accepts) | lead, quoting the acceptance |
  | 9 | `FD-` against `register-owed.py`; F61's event | auditor; WK-1170 |
  | 10 | new P2 `WK-` row carrying FR-217 inlining and FR-218; the `FD-` and `CR-838`'s dated correction (decided 16:25:49) | lead / the maintainer; auditor |
  | 11 | `OQ-` then `RL-` + `03` amendment; re-measurement in Proposal 3's slice | decision-maker; WK-1178 |
  | 12 | a `## P2` "Exit demo" row; a §10 gate *Before the P2 exit demo* (FD-1209, the D4 and E2 rulings) | lead |

- **For the lead's roadmap and register edits, after acceptance:**
  - OQ-1233's and OQ-1234's gate moves;
  - FR-453 named on WK-688's row;
  - the P3 packaging Work row;
  - G6's restatement without the number, if the user accepts it (Proposal 8);
  - FR-217 and FR-218 on a Work row (Proposal 10);
  - the host-fallback wording in G4 (Proposal 4);
  - F35's register owner;
  - FD-1194's cell (the auditor's register pass).

## Verdict

- Every input the lead's brief required has a written proposal with options and a
  recommendation: N3 (1), #852 (2), F35 and NFR-490 at exit (3), OQ-1233 to OQ-1235 (5),
  `FD-1238` (6), and FR-432, FR-433 and FR-438 (7). F38 and the dedicated host are Proposal 4.
- The maintainer's two later inputs have one each: FR-218 (10) and NFR-500 (11).
- The WK-672 close record was read before filing, and is reconciled in *Consistency with the
  WK-672 close record*. It adds Proposal 12, and it adds a trace-shape finding to Proposal 3's
  ruling.
- Every register row decayed to this review has a disposition (9).
- All five questions have a written answer.
- **Nothing here binds** until the lead's verdicts and the maintainer's dated line below.

## Acceptance

**Maintainer acceptance (plan review 16, Proposals 1–12, except the parts of 2, 4, 6, 8 and
10 already given in the 16:08:24, 16:21:36 and 16:25:49 entries):** _pending_ — dated when given.

## Sources

- The maintainer's channel entries of 2026-09-29, quoted by heading: 15:26:00 (STRUCTURE),
  15:36:43 (SCOPE: NFR-490 / F35), 14:15:43, 14:17:56 and 14:20:41 (the WK-674 answers),
  16:05:14 (the plan-review cadence), 16:08:24 (the host fallback and Dependabot), 16:12:57
  (routed outputs), 16:15:10 (the older plan-review items), 16:21:36 (the answers on G6,
  FR-217, #903 and #877–#879) and 16:25:49 (the blocker decisions). The
  channel file is local and is not in the repository.
- `docs/roadmap.md` (`## P2`, §10), `docs/findings/register.md`, `docs/open-questions.md`,
  `docs/specs/03-rating-engine.md`, `06-governance.md` and `07-platform.md`,
  `packages/model-schema/src/model_schema/permissions.py` and `rating.py`,
  `packages/pricing-core/src/pricing_core/rating/score.py` and `compile.py`,
  `backend/src/app/api/score.py`, `docs/REDIRECTS.csv`, `CR-838` and `CR-926`,
  all at `1c8762d9`.
- `PL-1237` at #843's head `306e42b9`, and `FD-1238` and `c2db4f72` on `records-2026-09-29`
  at `bc55a975`.
