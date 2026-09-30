---
id: RL-9973
family: ruling
title: OQ-1316 cross-referenced to RL-1329's R0 — an intermediate rounding rung would amend it
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: e20b1e429a2ddd0cb2a9abb04adddfe9b7263f13
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1316, RL-1329, RL-1312]
---

# RL-9973 — OQ-1316 cross-referenced to RL-1329's R0

## How this was ruled

- **Effort and routing.** Filed at effort `medium`, on the maintainer's instruction relayed by
  the lead. The instruction asks for a dated cross-reference line on both of OQ-1316's mirror
  rows: if rounding is allowed elsewhere (option (a)), `RL-1329`'s R0 must be amended.
- **What this record does.** It **decides nothing**. It records the disposition of the two
  identical dated notes it adds, because a spec edit is never made without a ruling record
  naming it (`.claude/roles/decision-maker.md`, *Tools*). The precedent is `RL-1265`, which
  raised `OQ-1266`.
- **Working id 9973.** Reserved by the lead in the reservation table at 19:04:40 BST. It is
  minted at the merge turn. An earlier, different working id 9973 was minted as `RL-1293`,
  and that record's disclosure line still names it. The two are distinct.

## Verified first, at e20b1e429a2ddd0cb2a9abb04adddfe9b7263f13

| Premise | Where | Present? | What the source says |
|---|---|---|---|
| R0's rounding clause | `RL-1329`, its lines `:652-656` | present | "**R0 Shape.** … `round` appears only on the last rung, and `clamp` only on `constraints`." |
| `RL-1329` names the interaction | `RL-1329`, its lines `:953-955` | present | "This ruling interacts with OQ-1316. If OQ-1316 is decided (a) (an intermediate rounding recorded as its own rung), R0's '`round` only on the last rung' must be amended by that ruling." |
| OQ-1316's mirror rows | `docs/open-questions.md:138`; `docs/specs/03-rating-engine.md:1190` | present | Both are open. Option (a) is "rounding recorded as its own rung" |

## Ruled

**Nothing is decided.** Each OQ-1316 mirror row gains the same dated note. It is appended to
the question cell in `docs/open-questions.md`, and to the row's single text cell in `03` §10.
Nothing else in either row changes, so the two mirrors stay in agreement:

> *(Cross-reference added 2026-09-30, `RL-9973`, on the maintainer's instruction: if this
> question is decided (a), rounding recorded as its own rung, `RL-1329`'s R0 ("`round`
> appears only on the last rung") must be amended by that ruling; `RL-1329` says so itself.)*

## What it obliges

- **This commit:** the two notes, and this record.
- **Whoever rules OQ-1316:** under option (a), amend `RL-1329`'s R0 in the same ruling. The
  instrument is a record with `corrects: RL-1329`, or a superseding ruling, whichever that
  ruling's scope needs.

## Acceptance — the violation that must become detectable

None of its own. The note makes the dependency visible where OQ-1316 is read. The
acceptance belongs to the ruling that decides OQ-1316.
