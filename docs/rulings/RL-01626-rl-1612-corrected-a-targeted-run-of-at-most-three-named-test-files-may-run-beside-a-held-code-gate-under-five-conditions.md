---
id: RL-1626
family: ruling
title: RL-1612 corrected — a seat's targeted test run of at most three named files may run beside a held code gate, under five conditions; never beside an ALONE window or a measurement, never a full suite (process, the maintainer's ruling by delegation, recorded)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-11
owner: maintainer               # a process ruling, recorded on the maintainer's behalf, as RL-1612, RL-1445 and RL-1263 are (§1.6 RL row)
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1612
relates: [RL-1612, RL-1445, RL-1263]
---

# RL-1626 — RL-1612 corrected: a targeted run of at most three named test files may run beside a held code gate

*Disclosure: drafted under working id 9818, reserved by the lead (team-lead) on 2026-10-11
(`~/gi-pricing-plan.local/handover/eta.md`, the line stamped "2026-10-11 11:48:45 BST": "RL
9818 RESERVED for D11 + §8 line"). Minted 2026-10-11 as RL-1626 from working id 9818, in the D12 batch mint PR (drafted for D11; the D11/D12 split of the lead's 11:58:45 entry moved it). The working id in this record was replaced by the minted id.*

## How this was ruled

- **The ruling is not this record's.** It is the maintainer's (by delegation), the
  "RL-1445 ITEM 1 AMENDED" paragraph of the entry of
  `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-11 11:48:00 BST — MERGE-ACK
  #1273 (SL-1600, LG-1609): head 71d578ae4d15fe9243697c61d1a8aae8e3714540, expected tree
  7dec870a94a8abfa8a0fdad607bf3e7b1c4aad68. Plus RL-1445 item 1 AMENDED (small tests beside a
  code gate), and SL-1563 DP-7 = (i)" (`to-lead.md:22158`; the paragraph at
  `:22165`–`:22170`). That file is local, so a repository reader cannot open it (RFC-777): the
  paragraph is quoted whole below. The rest of the entry (the #1273 MERGE-ACK and SL-1563's
  DP-7) rules other questions and is not part of this record. This record decides nothing
  beyond the paragraph.
- **What it corrects: `RL-1612`.** The paragraph orders, verbatim: "RECORD: the correcting RL
  in D11 (corrects RL-1612's restatement of item 1)". `RL-1612` (`corrects: RL-1445`) restated
  `RL-1445` item 1's test-run clause as its own item 2, and that restatement is the text in
  force. So this record's `corrects:` is `RL-1612`. The lead's brief for this seat
  (`~/gi-pricing-plan.local/handover/brief-dm-rls-2026-10-11.md`) said `corrects: [RL-1445]`;
  the entry is the primary source and this record follows it. The difference was reported to
  the lead before this record was committed.
- **`RL-1612` is frozen and is not edited.** At the mint turn, `RL-1612`'s header gains this
  record's minted id in `corrected_by:` (front matter only), as `RL-1445` gained `RL-1612`.
  `RL-1612`'s `status:` stays `active` and `superseded_by:` stays `~`: this record amends one
  clause of its item 2 and leaves the rest in force, so it is a correction, not a
  supersession. `RL-1445`'s header is not changed by this record.
- **`RL-1612` is not on `main` at this record's tree.** It is minted on the D10 branch
  `docs-d10-2026-10-11` (PR #1274, OPEN at head `80e467733fb6f1a962c4db3384011aa9d63b03ea`
  when read, 2026-10-11 11:5x BST). This record's citations of `RL-1612` are to that head.
  D12, which carries this record (drafted for D11), mints after D10 and D11 merge; the minter re-checks the lines cited here (done at the D12 mint: see the PR body).
- **Owner.** It is owned by the maintainer, as `RL-1612` is, because it amends a process
  ruling. The decision-maker seat `dm-rls` wrote it.

## Verified first

| Premise | Where | What the source says |
|---|---|---|
| The clause this record corrects | `RL-1612` :101–105 at `80e46773`, "So, from this record's merge, `RL-1445` item 1 reads as amended", item 2 | "**Authoring and executor seats count against the lead's seat cap, not the 3-cap.** Their local test runs stay targeted single-file runs, one at a time through the lead's small-test slot, never beside a gate or a measurement window." |
| The lead's obligation it states | `RL-1612` :157 at `80e46773`, "What it obliges" 4 | "routes every seat's local test run through one small-test slot, one at a time, never beside a gate or a measurement window;" |
| Its detectable violation | `RL-1612` :172 at `80e46773`, "Acceptance" | "a seat's local test run beside a gate or a measurement window, or beside another seat's run" |
| §8's text for `RL-1612` | `docs/process/delivery-process.md` :213 at `80e46773` | "their local test runs are single-file, one at a time through one small-test slot, never beside a gate or a measurement window" |
| The extract's field | `docs/process/delivery-process.core.json` :411 at `80e46773`, `parallelism.build_slices_across_works.authoring_and_executor_seats` | `count_against_the_seat_cap_not_the_3_cap_their_test_runs_are_single_file_one_at_a_time_through_the_small_test_slot_never_beside_a_gate_or_measurement_window` |
| The origin of the clause | `RL-1445` :128–129 at `02f23b4a` | "Targeted single-file test runs stay allowed outside the gate window, never beside a gate or a benchmark." |
| The interest | `RL-1445` :89 at `02f23b4a`, quoting the 2026-10-05 15:27:25 BST entry | "two pytest runs together put load at 15.87–16.01 on 8 CPUs (13:31–13:35) and risk load-sensitive timeouts" |

## Ruled

**The maintainer's decision, by delegation, quoted whole** (`to-lead.md:22165`–`:22170`):

> RL-1445 ITEM 1 AMENDED (two seats today ran single-file tests beside a held gate; with gates back to back all day, the rule as written leaves executors no time to test, so the rule is wrong, not the seats): a TARGETED single-file test run (or ≤ 3 named files) MAY run beside a held CODE gate when ALL hold:
> - `nice -n 19 ionice -c3`, through the small-test flock (one at a time);
> - load1 < 6 at start;
> - no DB-schema migration;
> - NEVER beside an ALONE window or measurement, and never a full-suite run (that is a gate).
> Both disclosed instances fall inside this and are closed. RECORD: the correcting RL in D11 (corrects RL-1612's restatement of item 1) and a dated §8 line, quoting this entry. Until it mints, this entry governs.

**So, from this record's merge, `RL-1612` item 2's test-run clause reads as amended:**

1. **A seat's targeted test run of one named test file, or of at most three named files, MAY
   run while another seat holds a code gate (a full gate), only when all of these hold:**
   - (a) it runs under `nice -n 19 ionice -c3`;
   - (b) it runs through the small-test flock, one run at a time;
   - (c) load1 is below 6 when it starts (`uptime`);
   - (d) it makes no database-schema migration;
   - (e) it is never beside an ALONE window or a measurement window, and it is never a
     full-suite run: a seat that needs a full-suite run is a gate holder (`RL-1612` item 1).
2. **This replaces "never beside a gate"** in `RL-1612` item 2 (:101–105), in "What it
   obliges" 4 (:157) and in "Acceptance" (:172), **for a code gate only**. "One at a time
   through the small-test slot" and "never beside a measurement window" stand as written.
3. **The two disclosed instances are closed.** The entry says both "fall inside this and are
   closed". It does not name them, and this record does not.
4. **Everything else in `RL-1612` stands:** the 3-cap's counting unit (its item 1), seats
   counted against the seat cap (item 2's first sentence), item 2's same-Work conditions from
   dispatch (item 3) and the disk guard rail (item 4).

**How this reads with `RL-1612`.** Both correct the same line of descent from `RL-1445`
item 1, at different limbs. `RL-1612` fixed **what the 3-cap counts** (slices that hold or
queue for the full gate, or are in a measurement window) and **where a seat's test runs go**
(single-file, one at a time through the small-test slot, never beside a gate or a
measurement). This record changes only the last of those: beside a held **code** gate, a
small targeted run is now allowed under the five conditions above. It does not change the
counting unit, and a run under this record does not count against the 3-cap, because it
neither holds nor queues for the full gate.

**Why this does not weaken the interest.** `RL-1445` rests on box contention (:89): the load
that broke timing tests came from two full pytest runs together. A run under this record is at
most three files, at the lowest CPU and I/O priority, one at a time, started only below load 6,
with no migration, and never beside an ALONE window or a measurement, where timing is what is
measured. The full suite stays a gate.

## What it obliges

The minter of the D12 batch (`minter-d11`; the record was drafted for D11) applies items 1 and 2 in the same PR as this record
(the entry: "the correcting RL in D11 … and a dated §8 line, quoting this entry"). This record
names them; it does not apply them.

1. **`docs/process/delivery-process.md` §8** gains a dated amendment line after the
   2026-10-11 `RL-1612` line (:213 at `80e46773`), citing this record and quoting the entry,
   that states Ruled 1 (a)–(e) and that it applies beside a code gate only. The `RL-1612`
   line is not edited.
2. **`docs/process/delivery-process.core.json`** (`meta.authoritative: false`):
   `parallelism.build_slices_across_works.authoring_and_executor_seats` (:411 at `80e46773`)
   says "never_beside_a_gate_or_measurement_window", which this record makes false for a code
   gate. The minter records the amended clause (a field, or a note naming this record) so the
   extract does not contradict §8, and re-derives `meta.derived_from_digest` by the
   repository's tooling (check 27). `meta.verified_against_tree` is not changed (`RL-1445`
   "What it obliges" 2).
3. **The mint turn:** `RL-1612` gains `corrected_by: [RL-<minted id>]`; the working id 9818 is
   replaced by the minted id in this record, in §8's dated line and in the extract.
4. **The lead**, which grants every test run: lets a seat's targeted run of at most three
   named files go beside a held code gate only under Ruled 1 (a)–(e), and never beside an
   ALONE window or a measurement.

## What this record does not decide

- **A gate other than a code gate.** The entry amends the rule beside "a held CODE gate". A
  docs check under the gate-2 slot is not named; this record does not extend the amendment to
  it.
- **Whether the small-test flock is held by construction.** As `RL-1612` "What it obliges" 5
  records, the slot is named in the lead's local briefs, not in a repository file; this record
  does not assert that any repository file creates or names it.
- **The instances the entry closes.** Not named in the entry; not named here.

## Acceptance — the violation that must become detectable

The violation: **a seat's test run beside a held code gate that breaks any of Ruled 1
(a)–(e)** — more than three files, a full suite, not under `nice -n 19 ionice -c3`, not
through the small-test flock or beside another seat's run, started at load1 ≥ 6, making a
schema migration, or beside an ALONE window or a measurement.

- *Violation: a run beside a code gate without the conditions.* Held by the small-test flock
  and the dispatch brief, not by a repository check. The lead's `eta.md` and the seat's
  report name the command, its flock and its start load.
- *Violation: the extract disagrees with §8.* Check 27 reds when `delivery-process.md`
  changes and the extract's digest is not re-derived. It does not compare content, so the
  amended clause in the extract is held by this record's review, not by a check.
