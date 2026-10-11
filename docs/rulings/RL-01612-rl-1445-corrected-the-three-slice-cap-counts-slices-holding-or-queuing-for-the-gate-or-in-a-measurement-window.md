---
id: RL-1612
family: ruling
title: RL-1445 corrected — the three-slice cap counts slices that hold or queue for the full gate or are in a measurement window, not every build slice; authoring and executor seats count against the seat cap, with guard rails (process, the maintainer's ruling by delegation, recorded)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-11
owner: maintainer               # a process ruling, recorded on the maintainer's behalf, as RL-1445 and RL-1263 are (§1.6 RL row)
tree: 99f22479a20e7fa64f8b6654e0d371c595b1e35a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1445
relates: [RL-1445, RL-1263]
---

# RL-1612 — RL-1445 corrected: the three-slice cap counts gate holders, gate queuers and measurement windows

*Disclosure: drafted under working id 9915 (minted as RL-1612 on 2026-10-11, in the D10 batch mint PR), reserved by the lead (team-lead) on 2026-10-11
(`~/gi-pricing-plan.local/handover/brief-wave1b-2026-10-11.md`, "Reserved working ids");
the id is minted in the D10 batch mint PR. When it is minted, the working id in this record
is replaced by the minted id.*

## How this was ruled

- **The ruling is not this record's.** It is the maintainer's (by delegation), item 1 of the
  entry of `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-10 21:41:05 BST —
  RL-1445 CAP: AMENDED by dated line (counting unit = gate or measurement, with guard rails);
  GO SL-1541 (WS-1 (a)); OP-1503-1 (a); SL-1575 noted" (`to-lead.md:21683`). That file is
  local, so a repository reader cannot open it (RFC-777): item 1 is quoted whole below. This
  record decides nothing beyond it. Items 2–4 of the entry rule other questions and are not
  part of this record.
- **The record is ordered** by the same entry, item 1(e), verbatim: "RECORD: a correcting RL
  (corrects: RL-1445) rides D10, with the delivery-process.md §8 dated line and the core.json
  extract bumped, so RL, process doc and extract agree (CLAUDE.md §15). Until it merges, this
  entry governs. No seat pauses."
- **RL-1445 is frozen and is not edited.** It is corrected by this record. At the mint turn,
  `RL-1445`'s header gains this record's minted id in `corrected_by:` (front matter only), as
  `RL-1263` gained `RL-1445`. `RL-1445`'s `status:` stays `active` and `superseded_by:` stays
  `~`: this record amends what its item 1 counts and leaves the rest of it in force, so it is
  a correction, not a supersession.
- **Owner.** It is owned by the maintainer, as `RL-1445` is, because it amends a process
  ruling. The decision-maker seat `dm-d10` wrote it.

## Verified first, at 99f22479a20e7fa64f8b6654e0d371c595b1e35a

The entry read `RL-1445` at `31b88780`. `git diff --stat 31b88780 99f22479` over the `RL-1445`
file, `docs/process/delivery-process.md` and `docs/process/delivery-process.core.json` is
empty, so the line numbers below hold at both trees.

| Premise | Where | What the source says |
|---|---|---|
| The interest the cap protects | `RL-1445` :89, quoting the 15:27:25 BST entry | "two pytest runs together put load at 15.87–16.01 on 8 CPUs (13:31–13:35) and risk load-sensitive timeouts. SETTLED: on this VM, AT MOST ONE full gate runs at a time; build slices up to 3; a built slice waits for the single gate." |
| The clause this record corrects | `RL-1445` :127–131, item 1 | "**Build slices: at most 3 at once. At most ONE full gate runs at a time on this VM.** A built slice waits for the single gate. Targeted single-file test runs stay allowed outside the gate window, never beside a gate or a benchmark." |
| The same-Work conditions | `RL-1445` :132–144, item 2 | "Two slices from the same Work may run at once only when the lead's dispatch record shows both of these: (a) File sets resolved … (b) No plan dependency, either way" |
| The detectable violation | `RL-1445` :210–213 | "a fourth concurrent build slice; a second concurrent full gate …; or two concurrent slices from the same Work whose dispatch record does not name both (a) … and (b) …" |
| The lead's obligation | `RL-1445` :181–182, "What it obliges" 4 | "runs at most 3 build slices at once, and never more than 1 full gate at once; a built slice waits for it;" |
| §8's text for `RL-1445` | `delivery-process.md` :202–211 | "*(Amended 2026-10-05 by the maintainer, dated line by delegation: at most 3 build slices at once; at most ONE full gate runs at a time on this VM, and a built slice waits for it …)*" |
| The extract's fields | `delivery-process.core.json` :125, :224, :380, :393–407 | `children_execution` `sequential_within_a_work_max_3_build_slices_same_work_pair_only_under_conditions`; `process_children.mode` `sequential_except_build_slices_max_3_same_work_pair_only_under_conditions`; `parallelism.rule` `no_two_children_of_same_layer_concurrently_except_build_slices_max_3_same_work_pair_only_under_conditions`; `build_slices_across_works`: `max_concurrent: 3`, `gate_slots: 1`, `built_slice_waits_for_the_single_gate: true`, `same_work_exception` |
| The seat cap item 1(b) names | `to-lead.md:21631`, the entry headed "2026-10-10 21:30:03 BST — USER: keep working in PARALLEL. …" | the header: "Fill up to 6 authoring seats in value order beside the gate queue" |

## Ruled

**The maintainer's decision, by delegation, quoted whole:** item 1 of the 21:41:05 BST entry
(`to-lead.md:21685`–`21690`), with its "Read before ruling" line (`to-lead.md:21684`):

> Read before ruling: RL-1445 @31b88780 :72 (the interest: box contention), :86–90 (SETTLED: one full gate at a time), :127–131 (item 1: "Build slices: at most 3 at once. At most ONE full gate runs at a time on this VM. A built slice waits for the single gate. Targeted single-file test runs stay allowed outside the gate window, never beside a gate or a benchmark."), :132–140 (item 2, the same-Work conditions).
> 1. YOUR READING IS NOT WHAT RL-1445 SAYS: item 1 counts build slices, not gate holders. Read as you propose, it would be an unrecorded amendment. I AMEND it now, by delegation, because the interest it protects (box contention) is held by the gate rule, and the user asked for parallel work (21:30:03):
>    a. The 3-cap counts slices that HOLD or QUEUE for the full gate, or that are in a measurement window (SL-1455's sweep, SL-1526's proving run), from that point until merge or release.
>    b. Authoring and executor seats count against the 6-seat cap (21:30:03), not the 3-cap. Their local test runs stay "targeted single-file", one at a time through your small-test slot, never beside a gate or a measurement window. A seat needing a full-suite run is a gate holder (a).
>    c. Item 2's same-Work conditions apply from DISPATCH, not from the gate: each dispatch record shows file sets resolved and no plan dependency both ways. This covers SL-1526 and SL-1541 (both WK-1178) and WK-675 S3/S4.
>    d. Each executor's per-worktree DB counts toward disk. If df / shows < 15% free, STOP new seats and report.
>    e. RECORD: a correcting RL (corrects: RL-1445) rides D10, with the delivery-process.md §8 dated line and the core.json extract bumped, so RL, process doc and extract agree (CLAUDE.md §15). Until it merges, this entry governs. No seat pauses.

Two notes on the quote, neither a decision:

- **The entry's line numbers for `RL-1445`.** It cites ":72 (the interest: box contention)"
  and ":86–90". At `31b88780` and at `99f22479`, :72 is the 15:15:11 BST item 1 quote ("GATE
  SLOTS stay 2: a third build waits for a free slot to gate, since box contention is the
  interest"), which :89's 15:27:25 BST correction supersedes for the gate count; the
  "box contention" interest it names is the same. :86–90 hold the 15:27:25 BST entry's
  header (:85–87) and its Q1 quote (:89), as cited.
- **The seat cap.** Item 1(b) names "the 6-seat cap (21:30:03)". That cap is the lead's
  seat count from the user's 21:30:03 BST request, and no governed record states it. It was
  raised to 9 by the entry headed "2026-10-11 10:41:33 BST — USER: work MORE in parallel …
  SEAT CAP 6 → 9; three seats now" (`to-lead.md:21838`), whose item 1 says: "Gate rules
  UNCHANGED: ONE full gate at a time; one docs check may run beside it (the gate-2 standing
  rule); measurement windows run ALONE; RL-1445's 3-cap as amended." This record records
  item 1(b)'s rule, that authoring and executor seats count against the seat cap and not the
  3-cap. It does not record a seat-cap number, which stays the lead's.

**So, from this record's merge, `RL-1445` item 1 reads as amended:**

1. **The 3-cap counts slices that hold or queue for the full gate, or that are in a
   measurement window, from that point until merge or release. At most ONE full gate runs at
   a time on this VM.** A built slice waits for the single gate. A slice in authoring or
   execution that has not yet queued for the gate does not count against the 3-cap. This
   replaces item 1's "Build slices: at most 3 at once" (`RL-1445` :127) as the counting unit,
   and "What it obliges" 4's first limb (:181).
2. **Authoring and executor seats count against the lead's seat cap, not the 3-cap.** Their
   local test runs stay targeted single-file runs, one at a time through the lead's
   small-test slot, never beside a gate or a measurement window. This replaces `RL-1445`
   item 1's "Targeted single-file test runs stay allowed outside the gate window, never beside
   a gate or a benchmark" with a narrower form: one at a time, and never beside a measurement
   window either. **A seat that needs a full-suite run is a gate holder under 1.**
3. **`RL-1445` item 2's same-Work conditions apply from dispatch, not from the gate.** Each
   dispatch record of a same-Work pair shows (a) the file sets resolved and (b) no plan
   dependency, both ways, before the GO. The entry names SL-1526 and SL-1541 (both WK-1178)
   and WK-675 S3/S4 as covered.
4. **Disk is a guard rail.** Each executor's per-worktree database counts toward disk. If
   `df /` shows less than 15% free, no new seat starts and the lead is told.
5. **Everything else in `RL-1445` stands:** one full gate at a time; a measurement step runs
   alone (`RL-1263` item 3); no shared files and the registry list with its two recorded
   amendments; item 2's conditions (a) and (b) as written.

**Why this does not weaken the interest.** `RL-1445` rests on box contention (:89). The
load that contention measured came from full suites running together, and the single full
gate and the measurement-runs-alone rule still bound that for every slice. A slice that is
authoring holds no gate, and its test runs are single-file, serialised through one slot and
never beside a gate or a measurement. So counting gate holders, gate queuers and measurement
windows counts the slices that make contention, which the old unit counted only by proxy.

## What it obliges

The minter of the D10 batch (`minter-d10`) applies items 1 and 2 in the same PR as this
record (the entry's item 1(e)). This record names them; it does not apply them.

1. **`docs/process/delivery-process.md` §8** gains a dated amendment line after the
   2026-10-05 `RL-1445` line (:202–211), citing this record, that states items 1–4 above.
   The 2026-10-05 line is not edited. The 2026-10-05 lines in §4 (:55–56, "up to 3 build
   slices may run at once, and two from the same Work only under §8's conditions; RL-1445")
   and §5 (:101–102, "up to 3 build slices, and two from the same Work only under §8's
   conditions; RL-1445") state the count as build slices; whether each needs its own dated
   line naming the counting unit is the minter's check, reported at the ACK.
2. **`docs/process/delivery-process.core.json`** (`meta.authoritative: false`) records the
   amended counting unit, so the extract does not still say the cap counts every build slice:
   - `parallelism.build_slices_across_works` (:393–407) states what `max_concurrent: 3`
     counts (slices holding or queuing for the full gate, or in a measurement window); that
     authoring and executor seats are outside it; the single-file runs one at a time through
     the small-test slot, never beside a gate or a measurement window; and a note naming this
     record. Its `each_holds_gate_slot: true` reads as if every counted slice holds the slot;
     under item 1, a counted slice holds **or queues for** the single gate, so the minter
     checks whether that field needs the same note.
   - `hierarchy.children_execution` (:125), `process_children.mode` (:224) and
     `parallelism.rule` (:380) carry `max_3_build_slices` in their values; the minter states
     whether each needs a change or a note to name the counting unit.
   - `meta.derived_from_digest` is re-derived against the amended markdown by the
     repository's tooling (check 27). `meta.verified_against_tree` is **not** changed: it is
     the recorded pre-migration base that `doc-id migrate --verify` reads (`RL-1445` "What it
     obliges" 2).
3. **The mint turn:** `RL-1445` gains `corrected_by: [RL-<minted id>]`; the working id 9915 is
   replaced by the minted id in this record, in §8's dated line and in the extract.
4. **The lead**, which dispatches every slice:
   - counts against the 3-cap only slices that hold or queue for the full gate, or are in a
     measurement window, and never runs more than 1 full gate at once;
   - routes every seat's local test run through one small-test slot, one at a time, never
     beside a gate or a measurement window;
   - writes a same-Work pair's (a) and (b) into the dispatch record before the GO;
   - starts no new seat when `df /` shows less than 15% free.
5. **Not decided here:** the seat-cap number (the lead's, above); any change to the gate
   wrapper's two slot files (`RL-1445` "What it obliges" 5, unchanged); whether the
   small-test slot is held by construction. At this record's tree the slot is named only in
   the lead's local briefs (`brief-wave1b-2026-10-11.md` rule 4, `flock -w 300
   /tmp/slots/small-test …`), and this record does not assert that any repository file
   creates or names it.

## Acceptance — the violation that must become detectable

The violation: a fourth slice holding or queuing for the full gate or in a measurement window
at once; a second concurrent full gate; a seat's local test run beside a gate or a
measurement window, or beside another seat's run; a same-Work pair dispatched without (a) and
(b); a new seat started with `df /` under 15% free.

- *Violation: four counted slices at once.* Visible in the lead's `eta.md` gate queue and
  measurement bookings, and the dispatch records.
- *Violation: two full gates at once.* As in `RL-1445`: `flock -n /tmp/slots/gate-1 true` and
  `flock -n /tmp/slots/gate-2 true` both fail at the same moment.
- *Violation: a seat's test run beside a gate, a measurement or another seat's run.* Held by
  the small-test slot and the dispatch brief, not by a repository check.
- *Violation: a same-Work pair dispatched without (a) and (b).* The second slice's dispatch
  record lacks either.
- *Violation: the extract disagrees with §8.* Check 27 reds when `delivery-process.md`
  changes and the extract's digest is not re-derived. It does not compare content, so the
  counting unit in the extract is held by this record's review, not by a check.
