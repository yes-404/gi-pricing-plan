---
id: RL-9670
family: ruling
title: OQ-1233 decided (b) — FR-453, both limbs, on WK-688, and FR-272's notification limb deferred to Phase 4 (scope, on the maintainer's behalf)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-29
owner: maintainer               # a scope ruling, recorded on the maintainer's behalf (§1.6 RL row)
tree: f0c3d197f5d89863efc647a2d7c1a6994b74dd63
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1233, CR-1247, RL-1232, WK-688]
---

# RL-9670 — OQ-1233 decided (b): FR-453, both limbs, on WK-688, and FR-272's notification limb deferred to Phase 4

## Verified first, at f0c3d197f5d89863efc647a2d7c1a6994b74dd63

**Why this record exists.** `OQ-1233` asks which Work owns `07` FR-453's
deployment-notification limb. The maintainer answered it by accepting plan review 16's
Proposal 5, recorded in `CR-1247`. The answer lives in the review's acceptance line, but
`docs/process/document-ids.md` §1.6's OQ row says an OQ is *"resolved by an `RL-` or `ADR-`"*,
and `CLAUDE.md` §13 files *"a decision already made"* as an `RL-`. A review record is neither,
so it cannot close the OQ by itself. This record is the resolver. The decision is a **scope**
question (which Work, which phase), and §1.6's RL row lets the maintainer author one *"on scope
or process"*. The decision-maker records it on the maintainer's behalf and decides nothing
here.

**RL-9670 is a working id**, minted at its merge turn with `doc-id.py next --ref origin/main`.
It was checked free on all 104 remote branches before use.

**What was read:**
- `CR-1247` (`docs/closures/CR-01247-…md`), Proposal 5 (`:385-429`). It gives the
  options (a) WK-674, (b) WK-688 (P4) and (c) a platform Work, and recommends (b), *"with FR-453
  (both limbs) named on WK-688's row"*. The lead's verdict is **ADOPTED** (`:428`), and it states
  *"This is a scope question, so the recommendation goes to the maintainer"*.
- The maintainer's acceptance (`CR-1247:429`), quoting the entry `2026-09-29 17:27:28 BST ·
  maintainer (acting on the maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and
  plan review 16 (#905), per proposal`: *"Accepted. OQ-1233 → (b): FR-453 (both limbs) is named
  on WK-688's row, and the OQ moves to Before Phase 4. FR-272's notification limb is deferred to
  P4."*
- The roadmap already carries it at `f0c3d197`: FR-453, both limbs, on WK-688's row
  (`docs/roadmap.md:1202`), and `OQ-1233` on the *Before Phase 4* gate (`:1248`), reading
  `14 (1 open)`.
- The specs do not carry it yet. `03` FR-272 (`03-rating-engine.md:200`) says *"Which Work
  delivers FR-453's deployment-notification limb is open (`07` §10, `OQ-1233`)"*, and `07`
  FR-453 (`07-platform.md:184`) says *"No Work owns the deployment-notification limb yet"*.

## Ruled

**`OQ-1233` is decided (b), as the maintainer accepted it.**
- `07` FR-453, both limbs (alert routing and deployment notifications), is WK-688's, in
  Phase 4. One signed-delivery mechanism serves both limbs.
- `03` FR-272's notification limb is **deferred to Phase 4, with WK-688 as its owner**. Its
  Audit Event limb stays WK-674's, in Phase 2 (`RL-1232` DP-4). Until WK-688 delivers the
  notification, no channel is configured and none is claimed.
- Options (a) and (c) are not chosen. `CR-1247` Proposal 5 gives the reasons: no Phase 2 exit
  criterion needs a notification, and (c) adds a row and a dependency edge to build the same
  thing once.

## What it obliges

- **This commit:**
  - `OQ-1233` is closed in both mirrors (`docs/open-questions.md` and `07` §10), dated, citing
    this record.
  - `03` FR-272 and `07` FR-453 gain dated amendments that replace "open" with the decision.
  - The *Before Phase 4* gate row strikes `OQ-1233` and is recounted to `14 (0 open)`. A
    decided question keeps its gate row.
- **WK-674's close:** FR-272's notification limb carries the verdict *deferred with an owner*
  (WK-688, Phase 4), which is a `CLAUDE.md` §13 verdict, not an omission.
- **WK-688:** delivers FR-453 for both limbs, with FR-336's routing and failure surfacing.

## Acceptance — the violation that must become detectable

The violation: **a Phase 2 or Phase 3 record that claims FR-272's notification is delivered, or
a spec text that still calls OQ-1233's answer open.** This is a scope ruling with no behaviour
to test. It is detected by review, and this record does not claim a mechanical check:
- `audit-docs.py` checks that the OQ's two mirrors agree on status. It does not check the
  FR-272 or FR-453 prose.
- WK-674's close audit applies §13's verdicts, and a claimed-delivered notification limb is a
  verdict error that the audit exists to catch.
