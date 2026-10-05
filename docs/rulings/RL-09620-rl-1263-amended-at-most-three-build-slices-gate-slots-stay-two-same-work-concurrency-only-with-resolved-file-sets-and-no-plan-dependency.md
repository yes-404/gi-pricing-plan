---
id: RL-9620
family: ruling
title: RL-1263 amended — at most three build slices, gate slots stay two; two slices from the same Work run at once only when the dispatch record shows their file sets resolved and no plan dependency either way (process, the maintainer's ruling by delegation, recorded)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-05              # the mint date (check 31); ruled 2026-10-05
owner: maintainer               # a process ruling, recorded on the maintainer's behalf, as RL-1263 is (§1.6 RL row)
tree: 809a3794af6d3a6ba688663b0d9b59f951190680
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1263
relates: [RL-1263, RL-871, CR-1212]
---

# RL 9620 (working id) — RL-1263 amended: at most three build slices, gate slots stay two; same-Work concurrency only under two named conditions

## How this was ruled

- **Filed under a working id the lead reserved.** `RL 9620` in this draft stands for this
  record's minted id (`~/gi-pricing-plan.local/handover/eta.md`, the `RL 9620` row). It mints
  **before** the lane GOs that need it: the maintainer's entry names lane B's FD 9707 fix
  beside S7, and later PL 9649.
- **The mint turn's one header change.** In the minting commit, `RL-1263`'s header gains this
  record's minted id in `corrected_by:` (the append check 34 allows), as `RL-1361` gained
  `RL-1383` when `RL-1383` (`corrects: RL-1361`) minted. `RL-1263`'s `status:` stays
  `active` and `superseded_by:` stays `~`: this record amends two of its clauses and leaves
  the rest of it in force, so it is a correction, not a supersession. `RL-1263`'s body is not
  edited.
- **The ruling is not this record's.** It is the maintainer's (by delegation), in
  `~/gi-pricing-plan.local/channel/to-lead.md`. That file is local, so a repository reader
  cannot open it (RFC-777). This record quotes the entry verbatim, re-reads its sources at
  `origin/main` `809a3794`, and carries the dispositions the entry orders. It decides
  nothing beyond them. It is owned by the maintainer, as `RL-1263` is, because it amends a
  process ruling; the decision-maker session `dm-rl1263` wrote it.

## Verified first, at 809a3794af6d3a6ba688663b0d9b59f951190680

| Premise | Where | What the source says |
|---|---|---|
| The count and the same-Work clause | `RL-1263` :54–55 (the maintainer's 22:46:27 entry, item 2, quoted there) | "**Build slices:** **at most 2 at once, from different Works**. Each holds one of the 2 gate slots (#925). A third waits for a slot." |
| The same clause, as the lead's obligation | `RL-1263` :177 ("What it obliges" 4) | "runs at most 2 build slices at once, from different Works;" |
| The same clause, as the detectable violation | `RL-1263` :185 | "A third concurrent build slice, two concurrent slices from the same Work, or a measurement step with the other gate slot held." |
| The existing contention rules | `RL-1263` :89–100 | existing definitions not changed by both; the closed registry list, append-only; "**Any other shared path serialises** unless the lead's dispatch record names the path and the check showing that no existing definition is edited by both." |
| The registry list's later amendments | `docs/process/delivery-process.core.json` :406–409 | `ONE_SIDED_SLUGS` in `backend/tests/test_contracts.py` exempt for key-disjoint edits (2026-10-03 21:11:06 BST); `__all__` in a package `__init__.py` exempt for name-disjoint appends (2026-10-05 09:44:39 BST) |
| The interest the rule protects | `RL-1263` :25–26, quoting `docs/process/delivery-process.md` §8 | "The interest it protects is "resource contention, not plan stability"." §8 itself, :182: "**The interest §8 protects is resource contention, not plan stability.**" |
| §8's text before this ruling | `delivery-process.md` :172–179 | "at most 2 build slices from different Works at once, each holding a gate slot, no shared files" |
| The extract before this ruling | `delivery-process.core.json` :125, :224, :372, :385–387 | `children_execution`: `sequential_within_a_work_max_2_build_slices_across_works`; `process_children.mode`: `sequential_except_build_slices_across_works_max_2`; `parallelism.rule`: `no_two_children_of_same_layer_concurrently_except_build_slices_across_works`; `max_concurrent: 2`, `from_different_works: true` |
| The third lane | `to-lead.md`, entry "2026-10-05 12:55:05 BST — DECISIONS (the maintainer, live): THIRD BUILD LANE APPROVED; usage is the maintainer's to track", item 1 | quoted below |

**The third-lane approval, item 1, verbatim:**

> 1. Third build lane (lane C-build): APPROVED by the maintainer ("Yes, open it now"). Conditions: a READY slice under PL-1371 whose write set is disjoint from lanes A and B (state the three write sets in the dispatch record); gates still serialised through the RL-1263 slots, never two at once, and never beside a benchmark; the same ACK checklist. Stream C (docs-only) continues alongside. Live cap 8 besides you stands.

That approval raised the count. It did not lift the same-Work clause, and it was not
recorded in a governed record. The 15:15:11 BST entry below states both.

## Ruled

**The maintainer's decision, by delegation, quoted whole** from the entry "2026-10-05
15:15:11 BST — F2 (RL-1263's "from different Works"): OPTION (i), amend RL-1263 by a dated RL,
with conditions; F1, F3 and the stale RL 9633 sentence as you set them" in
`~/gi-pricing-plan.local/channel/to-lead.md`:

> Verified at main: RL-1263 (owner: maintainer, a process ruling) :54 "Build slices: at most 2 at once, from different Works", :185 lists "two concurrent slices from the same Work" as a breach. Its basis is delivery-process.md §8 ("no two Slices run at once, at any layer"), and it names the interest that rule protects: "resource contention, not plan stability". My 12:55:05 third-lane approval raised the count but did not lift the same-Work clause. Your F2 is right.
> DECISION (the maintainer, by delegation): OPTION (i). A DM writes ONE RL amending RL-1263 (dated, corrects/amends as document-ids allows; RL-1263's body is not edited):
>  1. Build slices: at most 3 at once (the maintainer's 2026-10-05 approval, recorded). GATE SLOTS stay 2: a third build waits for a free slot to gate, since box contention is the interest.
>  2. Two slices from the SAME Work may run at once ONLY when the dispatch record shows (a) the file sets resolved by the existing contention rules (exempt / one-sided / name-disjoint / serialise) and (b) NO plan dependency: neither slice consumes the other's output (named, both ways). Otherwise they serialise.
>  3. delivery-process.md §8 and its core.json extract are brought into line (max_concurrent 2→3; the same-Work exception stated; the digest bumped), so RL, process doc and extract do not disagree (CLAUDE.md §15).
>  Spawn the DM now (a slot is free), under a reserved working id. It mints AHEAD of the lane GOs that need it: lane B's FD 9707 fix beside S7, and later PL 9649.
> Until it merges, the rule stands as written: lanes A and B must not both run WK-673 builds. If the GOs come before the RL, lane B takes a non-WK-673 item (the FD 9708 fix, WK-1178) and lane C waits.

The rest of the entry (F3, F1, RL 9633, OQ-1316/OQ-1373, RL 9623, #1157) rules other
questions and is not part of this record.

**So, from this record's merge, RL-1263 reads as amended:**

1. **Build slices: at most 3 at once.** **Gate slots stay 2** (`/tmp/slots/gate-1..2`). A
   third build slice may run, but it waits for a free slot before it gates. This amends
   `RL-1263` item 2 ("at most 2 at once") and "What it obliges" 4, first limb.
2. **Two slices from the same Work may run at once only when the lead's dispatch record
   shows both of these:**
   - **(a) File sets resolved** by the existing contention rules: each shared path is
     registry-exempt (append-only), one-sided or name-disjoint under a dated registry
     amendment, or serialised. These are `RL-1263`'s rules as already amended; this record
     adds none.
   - **(b) No plan dependency, either way:** neither slice consumes the other's output. The
     dispatch record names this in both directions (slice X does not consume slice Y's
     output; slice Y does not consume slice X's output).
   Otherwise the two slices serialise. This amends "from different Works" in `RL-1263`
   item 2 and "What it obliges" 4, first limb; and it narrows `RL-1263`'s Acceptance
   (:185): two concurrent slices from the same Work are a violation **only** when the
   dispatch record lacks (a) or (b).
3. **Everything else in `RL-1263` stands:** a measurement step runs alone (item 3, with the
   other gate slot held empty); no shared files (item 4, and the registry list); RL-871 §7's
   three conditions; the contention check and its step-down.

**Why condition (b) does not reopen RL-871.** `RL-1263` rests on §8's interest, "resource
contention, not plan stability" (§8, :182), and RL-871 refused an exception argued on
plan-independence. This record does not admit a pair *because* it is plan-independent. Box
contention stays bounded by the 2 gate slots and the measurement-runs-alone rule, which
hold for every pair. Condition (b) is an extra bar on a same-Work pair, not a ground for it:
two slices of one Work are the pair most likely to consume each other's output, so a
dependency there must be ruled out, named, before they overlap. Condition (a) is the same
file rule every concurrent pair already obeys, made explicit for a same-Work pair.

## What it obliges

1. **`docs/process/delivery-process.md`** gains a dated amendment line in §8 citing this
   record, and dated lines under §4's and §5's earlier amendment notes (each restates "up to
   2 build slices, from different Works"), in the same commit as this record. The earlier
   lines are not edited.
2. **`docs/process/delivery-process.core.json`** (`meta.authoritative: false`):
   - `hierarchy.children_execution`, `process_children.mode`, `parallelism.rule` and
     `parallelism.build_slices_across_works` record the amended rule: `max_concurrent` 2 → 3,
     `gate_slots: 2`, and the same-Work exception with its two conditions;
   - `meta.derived_from_digest` is re-derived against the amended markdown (check 27).
     `meta.verified_against_tree` is **not** changed: it is the recorded pre-migration base
     that `doc-id migrate --verify` reads (`RL-1263` "What it obliges" 2).
3. **The mint turn:** `RL-1263` gains `corrected_by: [RL-<minted id>]`; the working id is
   replaced by the minted one in §4, §5, §8 and the extract.
4. **The lead**, which dispatches every slice:
   - runs at most 3 build slices at once, and never more than 2 gates at once;
   - for a same-Work pair, writes (a) and (b) into the dispatch record before the GO, and
     serialises the pair when either is missing;
   - until this record merges, keeps `RL-1263` as written: lanes A and B do not both run
     WK-673 builds (the maintainer's entry, above).
5. **Not decided here:** no path joins the registry list; the gate-slot count is not
   changed; nothing about measurement or benchmark exclusivity changes.

**Restatements found outside `docs/process`** (sweep `git grep -n -i -E 'different
Works|at most 2 build|max_concurrent' -- docs/process .claude/roles .claude/skills
CLAUDE.md` at `809a3794`): none in `.claude/roles`, `.claude/skills` or `CLAUDE.md`.

## Acceptance — the violation that must become detectable

The violation: a fourth concurrent build slice; a third concurrent gate; or two concurrent
slices from the same Work whose dispatch record does not name both (a) the resolution of
each shared path and (b) the absence of a plan dependency in both directions.

- *Violation: four build slices in flight at once.* Visible in the lead's `eta.md` "In
  flight" grants and the dispatch records.
- *Violation: three gates at once.* Impossible by construction while the gate wrapper's
  flock slots stay at two (`/tmp/slots/gate-1..2`); a third build waits for a slot.
- *Violation: a same-Work pair dispatched without (a) and (b).* The dispatch record of the
  second slice of the pair lacks the shared-path resolution or either direction of the
  no-dependency statement.
- *Violation: the extract disagrees with §8.* Check 27 reds when `delivery-process.md`
  changes and the extract's digest is not re-derived; it does not compare content, so the
  `max_concurrent` value and the same-Work exception are held by this record's review, not
  by a check.
