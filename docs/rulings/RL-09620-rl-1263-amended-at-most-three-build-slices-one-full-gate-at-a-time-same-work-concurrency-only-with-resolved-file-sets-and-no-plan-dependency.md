---
id: RL-9620
family: ruling
title: RL-1263 amended — at most three build slices, one full gate at a time; two slices from the same Work run at once only when the dispatch record shows their file sets resolved and no plan dependency either way (process, the maintainer's ruling by delegation, recorded)
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

# RL 9620 (working id) — RL-1263 amended: at most three build slices, one full gate at a time; same-Work concurrency only under two named conditions

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
| The registry amendments' merged diffs | #1093, squash `16a89b151cda22be2ecfbf8761c05678af4fb676`; #1118, squash `ef5dc6e7317281ac9d1840fa61861597e3c1b8b1` (`git show`, both read whole) | each adds one path and one dated note to `registry_exempt_append_only`, and nothing else; neither changes `delivery-process.md` |
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

### Corrected 2026-10-05 15:27:25 BST — one full gate at a time; the registry amendments folded in

*(Clause added 2026-10-05, on #1162 before the mint, on the maintainer's entry below. The
15:15:11 BST quote above is not edited; its item 1's "GATE SLOTS stay 2" is superseded by
this entry.)* Quoted whole from the entry "2026-10-05 15:27:25 BST — RL 9620 (#1162): Q1
SETTLED, ONE full gate at a time (CORRECTION to my 15:15:11 item 1); Q2 folded into RL 9620"
in `~/gi-pricing-plan.local/channel/to-lead.md`:

> Q1, and a CORRECTION: my 15:15:11 item 1 said "GATE SLOTS stay 2". That contradicts my own 13:00:09 (and later) "Gates never run at the same time" and my 12:55:05 "never two at once", and today's evidence: two pytest runs together put load at 15.87–16.01 on 8 CPUs (13:31–13:35) and risk load-sensitive timeouts. SETTLED: on this VM, AT MOST ONE full gate runs at a time; build slices up to 3; a built slice waits for the single gate. RL 9620 and core.json say "1 concurrent full gate" (gate_slots 1, or the field's equivalent), quoting this entry as superseding 15:15:11's "stay 2". Targeted single-file test runs by executors stay allowed outside the gate window as before (never beside a gate or benchmark).
> Q2 (core.json :406-409 holds the ONE_SIDED_SLUGS and `__all__` registry exemptions, the RL-1263 amendments of 2026-10-03 21:11:06 and 2026-10-05 09:44:39, which no RL and no delivery-process.md text states): RIGHT, the extract says more than its authority. FOLD it into RL 9620 rather than a separate finding: one clause recording both amendments verbatim (their entry headers plus the merged PRs #1093 and #1118) and a dated §8 line, so authority, process doc and extract agree in one record. No finding is needed if RL 9620 closes it; if RL 9620's scope objection is raised, file it LOW under WK-1170.
> Everything else in #1162 @f4cf0aac (corrects: RL-1263 on the RL-1383→RL-1361 precedent; §4/§5/§8 dated lines; the same_work_exception block; checks 26/27 clean): checked at its ACK.
> The hook item (planner-hook, SL 9618 + PL 9617, $CLAUDE_PROJECT_DIR, red from a subdirectory cwd) and dm-premint's self-clean (unpushed merge of main, regenerable; remote heads unchanged): noted.

Its last line rules other items and is not part of this record.

**The registry list's two dated amendments, recorded here verbatim (Q2).** Both amend
`RL-1263`'s closed registry list (`RL-1263` :89–100, as corrected by "2026-09-29 23:20:11
BST — DATED CORRECTION to the 22:57:52 option-(c) registry list (two paths)"), and both are
already in the extract (`delivery-process.core.json`, `registry_exempt_append_only`, :406–409
at `809a3794`). This record is their authority from its merge; it adds no path and changes
neither.

1. **`ONE_SIDED_SLUGS`.** Entry "2026-10-03 21:11:06 BST — DATED AMENDMENT to RL-1263's
   registry list (option (b)): ONE_SIDED_SLUGS in backend/tests/test_contracts.py is exempt
   for key-disjoint edits; WK-673 S1 may run beside WK-674 S2"; merged as #1093
   (`16a89b151cda22be2ecfbf8761c05678af4fb676`). The amendment, as the entry gives it:

   > `backend/tests/test_contracts.py`, the `ONE_SIDED_SLUGS` dict only: a new key appended, or one slice's change to the value of one existing key, provided **no key is added, removed or changed by both** concurrent slices. Each slice's dispatch record names the keys it touches. At the second merge, the later slice runs the RL-1263 second-merge steps (merge main, re-run its full gate), and its gate must include `test_every_one_sided_slug_is_declared` passing. No other part of the file is exempt.

2. **`__all__`.** Entry "2026-10-05 09:44:39 BST — DISPATCH GO: FD-1356 fix (SL-1409 /
   PL-1408) on lane B, option (b); executor-1409 starts once the `__all__` registry amendment
   merges (or once WK-690 S3 merges, if that comes first)"; merged as #1118
   (`ef5dc6e7317281ac9d1840fa61861597e3c1b8b1`). The amendment, as the entry gives it:

   > `__all__` in a package `__init__.py`: names appended only; no name added or removed by both concurrent slices; each dispatch record names its names; the second to merge re-gates

   The extract's value for it (`names_appended_only_to_the_import_block_and___all___…`, and
   its note "(with the import lines that bring each name in)") also names the import lines
   that bring each name in. The entry's text does not say so in words; #1118 added it and
   was merged on the maintainer's ACK. This record quotes the entry and does not widen or
   narrow it. The difference is stated here so that a reader does not take the extract's
   wording as the entry's.

**So, from this record's merge, RL-1263 reads as amended** (item 1 as corrected at
15:27:25 BST):

1. **Build slices: at most 3 at once. At most ONE full gate runs at a time on this VM.** A
   built slice waits for the single gate. Targeted single-file test runs stay allowed
   outside the gate window, never beside a gate or a benchmark. This amends `RL-1263` item 2
   ("at most 2 at once"; "Each holds one of the 2 gate slots") and "What it obliges" 4,
   first limb.
2. **Two slices from the same Work may run at once only when the lead's dispatch record
   shows both of these:**
   - **(a) File sets resolved** by the existing contention rules: each shared path is
     registry-exempt (append-only), one-sided or name-disjoint under a dated registry
     amendment (the two recorded above), or serialised. These are `RL-1263`'s rules as
     already amended; this record adds none.
   - **(b) No plan dependency, either way:** neither slice consumes the other's output. The
     dispatch record names this in both directions (slice X does not consume slice Y's
     output; slice Y does not consume slice X's output).
   Otherwise the two slices serialise. This amends "from different Works" in `RL-1263`
   item 2 and "What it obliges" 4, first limb; and it narrows `RL-1263`'s Acceptance
   (:185): two concurrent slices from the same Work are a violation **only** when the
   dispatch record lacks (a) or (b).
3. **Everything else in `RL-1263` stands:** a measurement step runs alone (item 3); no
   shared files (item 4, and the registry list with the two amendments recorded above);
   RL-871 §7's three conditions; the contention check and its step-down.

**Why condition (b) does not reopen RL-871.** `RL-1263` rests on §8's interest, "resource
contention, not plan stability" (§8, :182), and RL-871 refused an exception argued on
plan-independence. This record does not admit a pair *because* it is plan-independent. Box
contention stays bounded by the single full gate and the measurement-runs-alone rule, which
hold for every pair. Condition (b) is an extra bar on a same-Work pair, not a ground for it:
two slices of one Work are the pair most likely to consume each other's output, so a
dependency there must be ruled out, named, before they overlap. Condition (a) is the same
file rule every concurrent pair already obeys, made explicit for a same-Work pair.

## What it obliges

1. **`docs/process/delivery-process.md`** gains a dated amendment line in §8 citing this
   record, and dated lines under §4's and §5's earlier amendment notes (each restates "up to
   2 build slices, from different Works"), in the same commit as this record. The earlier
   lines are not edited. *(Added 2026-10-05, on the 15:27:25 BST correction:)* the §8 line
   says one full gate at a time, and a second dated §8 line lists the two registry
   amendments recorded above on the exempt list.
2. **`docs/process/delivery-process.core.json`** (`meta.authoritative: false`):
   - `hierarchy.children_execution`, `process_children.mode`, `parallelism.rule` and
     `parallelism.build_slices_across_works` record the amended rule: `max_concurrent` 2 → 3,
     `gate_slots: 1` (corrected at 15:27:25 BST from the `2` first written), a built slice
     waiting for the single gate, targeted single-file runs outside the gate window, and the
     same-Work exception with its two conditions;
   - `registry_exempt_append_only` is unchanged: its two amended paths already match the
     entries recorded above (the `__all__` wording difference is stated there); a note names
     this record as their authority;
   - `meta.derived_from_digest` is re-derived against the amended markdown (check 27).
     `meta.verified_against_tree` is **not** changed: it is the recorded pre-migration base
     that `doc-id migrate --verify` reads (`RL-1263` "What it obliges" 2).
3. **The mint turn:** `RL-1263` gains `corrected_by: [RL-<minted id>]`; the working id is
   replaced by the minted one in §4, §5, §8 and the extract.
4. **The lead**, which dispatches every slice:
   - runs at most 3 build slices at once, and never more than 1 full gate at once; a built
     slice waits for it;
   - for a same-Work pair, writes (a) and (b) into the dispatch record before the GO, and
     serialises the pair when either is missing;
   - until this record merges, keeps `RL-1263` as written: lanes A and B do not both run
     WK-673 builds (the maintainer's entry, above).
5. **Not decided here:** no path joins the registry list; nothing about measurement or
   benchmark exclusivity changes. *(Corrected 2026-10-05, on the 15:27:25 BST entry: this
   item first said "the gate-slot count is not changed". It is changed, 2 → 1 full gate.)*
   Not decided either: whether the gate wrapper drops to one slot file. The wrapper in
   `.claude/skills/dev-commands/SKILL.md` (its `for i in 1 2` loop over
   `/tmp/slots/gate-$i`) still offers two slots, and `conftest.py`'s module docstring names
   the same `/tmp/slots/gate-{1,2}`. Until the lead routes that change, the one-gate rule is
   held by the lead's dispatch, not by construction.

**Restatements found outside `docs/process`** (sweep `git grep -n -i -E 'different
Works|at most 2 build|max_concurrent' -- docs/process .claude/roles .claude/skills
CLAUDE.md` at `809a3794`): none in `.claude/roles`, `.claude/skills` or `CLAUDE.md`.
*(Added 2026-10-05, for the gate count:)* a second sweep, `git grep -n -i -E '2 gate
slots|two gate slots|2-slot|gate-1\.\.2|gate-\{1,2\}|gate slots stay|both gate
slots|other gate slot' -- docs/process .claude/roles .claude/skills CLAUDE.md conftest.py`
at `809a3794`, finds `.claude/skills/dev-commands/SKILL.md` :231 and :356 ("2 gate slots, 2
verify slots"), `conftest.py` :20, `delivery-process.core.json` :435
(`rl871_conditions.iii_coordination.enforcing`, the wrapper's two flock files) and
`delivery-process.md` :176 (the 2026-09-29 line's "2-slot gate cap", not edited). This
record changes none of them; the skill's budget line is the lead's to route.

## Acceptance — the violation that must become detectable

The violation: a fourth concurrent build slice; a second concurrent full gate *(corrected
2026-10-05 15:27:25 BST, was "a third concurrent gate")*; or two concurrent
slices from the same Work whose dispatch record does not name both (a) the resolution of
each shared path and (b) the absence of a plan dependency in both directions.

- *Violation: four build slices in flight at once.* Visible in the lead's `eta.md` "In
  flight" grants and the dispatch records.
- *Violation: two full gates at once.* **Not** impossible by construction: the wrapper still
  offers two flock slots (item 5 above). Detectable: `flock -n /tmp/slots/gate-1 true` and
  `flock -n /tmp/slots/gate-2 true` both fail at the same moment.
- *Violation: a same-Work pair dispatched without (a) and (b).* The dispatch record of the
  second slice of the pair lacks the shared-path resolution or either direction of the
  no-dependency statement.
- *Violation: the extract disagrees with §8.* Check 27 reds when `delivery-process.md`
  changes and the extract's digest is not re-derived; it does not compare content, so the
  `max_concurrent` and `gate_slots` values, the same-Work exception and the registry list
  are held by this record's review, not by a check.
