---
id: CR-1212
family: closure
kind: review
title: Plan review 15 — P2's exit criteria, the extended goal's sequencing under the budget, and the open-finding set
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-28
owner: lead
tree: 9f6bfed1a94838d92bdc76475e03f8b5b078527a
phase: P2
work: WK-1178
corrected_by: [RL-1263, RL-1287, RL-1514]
relates: [FD-1190, FD-1196, FD-1197, FD-1198, FD-1199, FD-1200]     # ids only
---

### Plan review 15 — P2's exit criteria and the budget, 2026-09-28

**Base tree: `9f6bfed1a94838d92bdc76475e03f8b5b078527a`** (origin/main after #862, PL-1189).
**Drafted by the planner** (`CLAUDE.md` §12: the review is the planner's to write). The lead
adopts and files it. **Nothing here binds until each proposal's acceptance line carries a
date.** The deputy shows the exit criteria (Proposal 1) to the maintainer before dating it.

**Trigger.** This is `CLAUDE.md` §14, "before a phase's exit demo". Proposal 1 creates the
exit demo, so the review must precede it. The trigger also covers the workstream closes since
review 14: WK-695 (#839) and WK-696 (#849). The agenda of record is the deputy's entry of
2026-09-28 17:18:55 BST (the MERGE-ACK of #855), "After it" block. Its substance is carried
in full below, because a reader cannot open the channel file.

**Form.** This follows `CR-1167` (plan review 14): the five `phase-review` questions, then
Output and Verdict. Its proposals lead, as the brief orders.

## Scope

The P2 phase as `docs/roadmap.md`'s `## P2` section defines it at `9f6bfed1`: its 17 Works, the
specs their FRs cover, and every register row whose Phase column includes 2.

## Evidence

- **Tree.** Everything was read at `9f6bfed1`. The merged PRs of 2026-09-28 read there are:
  #853 and #858 (WK-672 Slice 1), #839 (WK-695), #849 (WK-696), #830, #855, #860, #861 and
  #862 (PL-1189). The open PRs are cited by number: #833, #834, #837, #843, #844, #845, #847,
  #848 and #856.
- **Predicates.** Every count below states the predicate it was measured with (`CLAUDE.md`
  §13, RFC-777). The roadmap was read with this per-Work section reader:
  `awk -v h="### WK-$w " 'index($0,h)==1{p=1;next} /^### /{p=0} p' docs/roadmap.md`.

## Proposal 1 — P2's exit criteria and gates

**The gap.** `docs/roadmap.md:559-560` reads `gates: ~` and `exit criteria: ~` under
`## P2 — Rating Engine`. P2 has no stated exit. Of its 17 Works (`:561`), 8 are
`status: active`: WK-672, WK-673, WK-674, WK-675, WK-690, WK-1169, WK-1170 and WK-1178. The
predicate is the `status:` line in each `### WK-` section inside `## P2`.

**The proposed gates.** Each is checkable by a named command or record.

- **G1. Every P2 Work is resolved.** Each is closed by a `CR- kind: work` carrying the
  maintainer's dated acceptance line, or moved out of P2 by a dated maintainer line. The
  exception is WK-1178, the standing maintenance Work, which "never closes inside the phase"
  (the deputy's 13:51:08 entry). WK-1178 needs no close: its open rows are dispositioned
  under G3. Check: every `### WK-` section in `## P2` reads `status: closed`, or is
  WK-1178, or is named in a dated move line.
- **G2. The exit demo is `WF-699` end to end on the freMTPL2 seed, with its deploy step.**
  - It runs through approved models, a Rating Version compiled with pins, and golden quotes.
  - Then comes a regression run (the Regression Suite), a dislocation run with attribution,
    and submission.
  - Then approval by a principal who is neither submitter nor author (#861, FR-353), then
    deployment to `uat` and then `prod` (`07` FR-429 promotion order).
  - It runs from one command to a served page, in Phase 1b's form (`docs/roadmap.md:350`).
    It is recorded in a `CR- kind: phase` with the maintainer's acceptance.
- **G3. Every open P2 finding has a resolution:** fixed, carried with a named owner, or
  accepted by a dated line (`CLAUDE.md` §14: "Nothing starts in the next phase while an open
  finding from the current phase lacks a resolution"). There are two named conditions:
  - FD-1200 (critical) is fixed on main. **Amended at acceptance:** it is fixed by #864
    (squash `e6a9ca71`, FR-351), so this limb is met once #865's register row closes it;
  - FD-1199 is triaged, with a root cause or a dated acceptance.

  The set is under "The open P2 finding set" below.
- **G4. Every P2 NFR is measured on the exit tree, or carried with an owner.** The per-id
  list is under "G4: the P2 NFRs, one by one" below.
- **G5. The gate is green on the exit tree.** That means the two-half gate of `CLAUDE.md`
  §11, and the four docs checks with DISCLOSED no higher than main's baseline (851 at
  `9f6bfed1`). *(Restated at acceptance by symbol, not by the pasted number; see the line below.)*
- **G6. A plan review 16 is filed** after G1–G5 and before the demo (`CLAUDE.md` §14).

**Recommendation:** adopt G1–G6 and write them into the `## P2` header's `gates:` and
`exit criteria:` fields. *(Amended at acceptance: into `exit criteria:` only; see the line below.)* That edit is applied by the lead or decision-maker on acceptance,
never by this review.

**Maintainer acceptance (Proposal 1): ACCEPTED by the maintainer, with two amendments** (the deputy's entry of 2026-09-28 19:05:44 BST, quoted whole under "Acceptance" at the foot):
1. **G1–G6 go into `exit criteria:` only.** The milestone's `gates:` field holds the three **dated freeze gates**, plan, code and docs
   (`document-ids.md` §1.3 and §1.10(b)), and `docs/process/checklists/phase-close.md:75-77` fails a phase whose freezes were not declared with dates.
   **`gates:` and `target:` stay `~`** until the lead proposes three freeze dates and a target after WK-672 closes. They are declared before the first of them passes.
2. **G5 reads by symbol:** on the exit tree, `audit-docs.py` exits 0 with "All checks passed.", its ceiling being the governed record at `_docid.W37_11_RECORD_PATH`
   (`docs/process/residue-ceiling-record.md`), plus the other three docs checks at rc 0, plus the two-half gate of `CLAUDE.md` §11. The pasted "851" is not the criterion.

### G4: the P2 NFRs, one by one

**How the list was built.** No P2 row carries an NFR clause or exception list. Only WK-671's
row names NFR ids: NFR-489, NFR-493, NFR-500, NFR-501 and NFR-502. So the list is derived
from the FRs each P2 Work covers. The spec §9s are `03` (WK-669 to WK-675), `07` and `00`
(WK-674: FR-428 to FR-431, FR-436, FR-18) and `02` (WK-690).
- **NFR ids** come from `grep -oE '\*\*NFR-[0-9]+\*\*'` between `^## 9\.` and `^## 10\.`.
- **Evidence** comes from `grep -rnE "NFR-nnn([^0-9]|$)"` over `backend/tests`,
  `packages/*/tests`, `frontend/src`, `scripts/bench*.py` and `docs/closures`. Each hit was
  opened before it was counted.

**`03` §9 (all 14):**

| NFR | Owner | Measured where | Status at `9f6bfed1` |
|---|---|---|---|
| NFR-489 | WK-671 (closed) | `CR-927`:103, :130-131; `scripts/bench-rating.py:1031` | **failing** (fetch p99 66.294 ms vs 50 ms). Remedy owner: "a ruling before WK-674" (F-W9-1), not a Work |
| NFR-490 | WK-671 (closed) | correctness `pricing-core/tests/test_rating_score.py:495`; latency `CR-927`:132 | latency **failing** (+723 %). F35 remedy has no Work |
| NFR-491 | WK-669/671 (closed) | `test_rating_score.py:528-542` | measured |
| NFR-492 | WK-669 (closed) | `docs/research/w11-task-1-3-nfr-rate-4.md:37` | measured (no CR records it) |
| NFR-493 | WK-671 (closed) | throughput `CR-927`:355 (5.09×) | throughput passes; **linearity limb not measured, no owner** (F52) |
| NFR-494 | WK-674 | none | open, owned |
| NFR-495 | WK-669/671 (closed) | `test_rating_score.py:551`, :560 | measured |
| NFR-496 | WK-671 (closed) | `test_rating_score.py:189`; `test_rating_runtime.py:212` | **prod-sampling limb has no owner** |
| NFR-497 | WK-671 / WK-674 | degradation `test_bundle_slot.py:174-228`, `CR-927`:112 | 99.95 % availability open, WK-674 (F41) |
| NFR-498 | WK-669/670/671/674 | compile `test_rating_version_compile.py:658` | deploy, rollback and routing limbs open, WK-674 |
| NFR-499 | WK-671 / WK-674 | `backend/tests/test_score.py:229`, :246, :578 | rate-limit limb open, WK-674 (F48) |
| NFR-500 | WK-671 (closed) | `CR-927`:324; `bench-trace-size.py` | **failing** (~2.58×). F37 spec fix has no Work |
| NFR-501 | WK-671 (closed) | `CR-927`:105, :133 | measured |
| NFR-502 | WK-671 (closed) | `CR-927`:104 "owed, not delivered" | owner is a ruling (F-W9-1), not a Work |

**`07` §9 and `00` §9 (through WK-674):**
- NFR-526, NFR-527, NFR-530, NFR-531, NFR-533, NFR-534 and NFR-536 have **no measurement
  and no owning Work**. NFR-531 follows FR-435, and NFR-534 follows FR-434. Neither FR is on
  any roadmap row (see item 12).
- NFR-528 is measured (`backend/tests/test_worker.py:419`), and so are NFR-532 and NFR-535.
- NFR-529 is accepted (F18, 27 s).
- In `00`: NFR-459 is measured (`test_traces.py:257`), and NFR-461 has none.

**`02` §9 (WK-690's expression kind):**
- NFR-476 has an expression limb with no measurement (`CR-754`:163 covers the builtin only).
- NFR-480, NFR-483 and NFR-484 have markers or CR evidence for existing kinds, and WK-690
  owns their expression limbs.
- `06` NFR-518 to NFR-525 are P3's, since WK-690 carries only FR-367.

**Proposed dispositions (G4):**
- (a) **WK-674 owns NFR-494, NFR-497 (availability), NFR-498 (deploy limbs), NFR-499 (rate
  limit), the NFR-493 linearity limb and the NFR-496 prod-sampling limb.** Its map plan
  (#843) cites each.
- (b) **NFR-489, NFR-490 and NFR-502 go to WK-674** as the serving-path ruling F-W9-1
  requires, or are **accepted as failing** by a dated maintainer line. Recommend WK-674.
- (c) **NFR-500's spec defect (F37) goes to a WK-1178 spec slice.**
- (d) **The seven unowned `07` NFRs and NFR-461 are carried to P3** by a dated line, since
  they are not P2 FRs' NFRs. The exceptions are NFR-531 and NFR-534, which travel with item
  12's FRs.
- (e) **WK-690 owns NFR-476, NFR-480, NFR-483 and NFR-484's expression limbs.**

**Acceptance (G4 dispositions): accepted by delegation** (the deputy's entry of 2026-09-28 19:05:44 BST, quoted whole under "Acceptance" at the foot). Under (b), NFR-489, NFR-490 and NFR-502 go to **WK-674**, not "accepted as failing".

### The open P2 finding set (G3 and item 10)

**Predicate, runnable at `9f6bfed1` from the repository root.** The register's rows are
`| Finding id | Concerns | Work item | Phase | Decision |`. There is no status, severity or
owner column, so the owner is read from the Decision cell. **The resolved test reuses
`scripts/register-lint.py`'s own vocabulary**, not a second regex. That is its
`_opens_with_status` (the `STATUS_PREFIXES` "resolved" and "fixed" at the cell's opening)
together with its `_STATUS_MARKER` (an emphasised `resolved` or `fixed` anywhere in the
cell). An `accept` opening is also excluded.

```python
import importlib.util, pathlib, re
spec = importlib.util.spec_from_file_location("rl", "scripts/register-lint.py")
rl = importlib.util.module_from_spec(spec); spec.loader.exec_module(rl)
rows, problems = rl.parse_register(pathlib.Path("docs/findings/register.md"))
assert not problems
def closed(d):
    return (rl._opens_with_status(d) or bool(rl._STATUS_MARKER.search(d))
            or rl._strip_emphasis(d).lower().startswith("accept"))
p2 = lambda ph: bool(re.search(r"(^|[^0-9])2([^0-9]|$)", ph))
open_rows = [r for r in rows if p2(r.fields[3]) and not closed(r.fields[4])]
print(len(rows), len(open_rows))
```

**Output: `155 91`.**

**Controls, run with the same functions:**
- **FD-1198** (register line 185, "**Resolved 2026-09-28** by #861") reads **resolved**.
- **FD-1180** (line 175, "**Resolved 2026-09-28** by #851") reads **resolved**.
- **FD-1200** (line 188, "**fix before close**") reads **open**.

**The cross-check against each FD file's `status:`.** Every P2 row whose Finding-id cell
ends in `(FD-n)` was compared with `docs/findings/FD-0nnnn-*.md`'s `status:` line. Two
disagree, and both are listed for the register pass rather than edited here:
- FD-1190 (line 177): the register says `accept` ("fixed by PR #855"), and the file says
  `status: active`.
- FD-1194 (line 181): the register says `Resolved 2026-09-28` by #841, and the file says
  `status: active`.

**What moved between the first draft and this predicate:**
- **The count went from 92 to 91.** One row left the set, **F28** (line 70). It opens
  "**deferred with an owner — the lead**, for the residuals only", and it carries an
  emphasised `**Fixed** — P8 …` for its already-fixed items. `register-lint`'s
  `_STATUS_MARKER` therefore reads the whole row as resolved. F28's residuals are
  **carried to the lead** all the same (Proposal 13's register pass). The cell is listed
  there as ambiguous, because one row carries both a live deferral and a fixed marker. No row
  entered the set.
- **FD-1198 was never in the set.** The first draft's row labelled "L186 FD-1198" was
  mislabelled. Line 186 is the **carry row** "FR-353 component authors are not separated
  from the approver — carried from FD-1198", which is deferred to WK-677 and has no FD id of
  its own. FD-1198 itself (line 185) is resolved by #861, and the corrected table below says
  so.

**Other facts about the register:**
- It has 155 data rows. Its Phase column reads `2` 134 times, `1b` 20 times and `2/3/4`
  once.
- No severity is recorded in it.
- **Stale cell, F34 (line 76):** "in flight on PR #416". At `9f6bfed1`,
  `gh pr view 416` reads `MERGED 2026-08-30T01:43:51Z` (the W11 Task 1.5 latency-harness PR, which also added the rating-algorithm maturity check). This is listed for the register pass and not
  edited here.

**Resolutions.** "Carried" means carried with the owner the register names. "Proposed" is a
resolution this review asks the maintainer to date. Rows cite their register line at
`9f6bfed1`.

**Rating-engine and product (28):**

| Line | Id | Register owner | Resolution |
|---|---|---|---|
| L45 | F6 | "Phase 2 validation-report workstream" (not a WK) | **Proposed:** carried to WK-1178 |
| L46 | F7 | unowned by design, with a trigger | **Proposed:** accepted, the trigger stands |
| L47 | F8 | phase boundary | **Proposed:** discharged by G1 (the P2 Works deliver `03`); re-checked at review 16 |
| L48 | F9 | phase boundary | **Proposed:** discharged by G2 (`WF-698` §4 surfaces in the demo) |
| L49 | F22 | "later-phase workstreams", none named | **Proposed:** replaced by G4's per-NFR dispositions |
| L59 | F-W9-1 | a ruling before WK-674 | **Proposed:** WK-674 (G4 b) |
| L60 | F-W9-2 | WK-673 | carried |
| L61 | F-W9-3 | WK-1170 | carried |
| L62 | F-W10-1 | W10-3, half resolved | **Proposed:** WK-675 (the rate-table editor slice) |
| L64 | F-W10-2 | portfolio-dataset integration | **Proposed:** WK-673 (it reads the portfolio) |
| L67 | F-W10-3 | WK-675 | carried |
| L76 | F34 | "PR #416", stale: merged 2026-08-30 | **Proposed:** the register pass checks whether #416 discharged it; until then carried to WK-1178 |
| L77 | F35 | none | **Proposed:** WK-674 (G4 b) |
| L79 | F37 | none | **Proposed:** WK-1178 (G4 c) |
| L80 | F38 | WK-671 (closed) | **Proposed:** WK-674 (G4 b) |
| L83 | F41 | WK-674 | carried |
| L84 | F43 | WK-674 | carried |
| L85 | F44 | WK-672 Slice 3 | carried |
| L89 | F48 | WK-674 | carried |
| L93 | F52 | unowned | **Proposed:** WK-674 (G4 a) |
| L94 | F53 | delivered but untested | **Proposed:** WK-1178 test slice |
| L95 | F54 | WK-674 | carried |
| L96 | F55 | unowned | **Proposed:** WK-1178, weighed against NFR-499 |
| L182 | FD-1195 | lead; WK-1178 | carried |
| L184 | FD-1197 | lead; next permissions slice | carried; see Proposal 3 |
| L186 | the FD-1198 carry row (FR-353 component authors; no FD id of its own) | WK-677 (P3) | carried. FD-1198 itself, line 185, is **resolved** by #861 |
| L187 | FD-1199 | lead | carried; **G3 condition**: triage before exit |
| L188 | FD-1200 | lead; WK-1178 | **fixed** by #864 (`e6a9ca71`), after this review's tree; met once #865's register row closes it (the P10 amendment) |

**Test and infrastructure (10):**
- carried to the named owner: F39 (the frontend Work, WK-675), F33 (lead) and FD-1196 (lead;
  WK-1178);
- **Proposed** WK-1178: F26 (a fresh owner was asked for), F30 (WK-671 is closed), F36, F45,
  F46 and F47;
- **Proposed** accepted, as the register itself says "fix not required": F40.

**Process and tooling (53).** Each row names the lead with WK-1170 (the create-read-retire
audit), the lead with WK-1169 (the charter), the lead alone, or the maintainer. All are
**carried** except the eight unowned ones:
- Carried to WK-1170: F27, F29, F78, F86, F90, F94, F96, F100, F101, F103, F106, F108, F114,
  FD-1149, FD-1150, FD-1155, FD-1157, FD-1158, FD-1159, FD-1160, FD-1163, FD-1165, FD-1166,
  FD-1168 and FD-1174.
- Carried to WK-1169: F31, F73, F74, F75, F97, FD-1151, FD-1153, FD-1156, FD-1161, FD-1162,
  FD-1191 and FD-1192.
- Carried to the lead: F89, F107, F112, F113, FD-1152 and FD-1154. F28 left the set (see "What moved"), and its residuals stay the lead's.
- Carried to the maintainer: F63, F93 and FD-1193.
- **Proposed** WK-1178: F57, F65, F66, F68, F69, F72 and F79, the rows naming no owner or
  only a trigger.

**Counts.** 28 + 10 + 53 = 91. Every row whose register owner is none, a trigger only, a
phase boundary or a closed Work carries a **Proposed** resolution above.

**Acceptance (the finding resolutions): accepted by delegation as proposed, 91 rows** (the deputy's entry of 2026-09-28 19:05:44 BST, quoted whole under "Acceptance" at the foot).

## Proposal 2 — the extended goal's sequencing under the budget

**The maintainer's order, verbatim.** The deputy's entry of 2026-09-28 13:51:08 BST quotes
the maintainer, "yes plz go ahead for the exit criteria and add the outstanding works to
your tasklist by the suggested order, extend your goal to all the listed works landed", and
records the order:

```text
**The extended goal, in the maintainer's order** (all are `status: active` at `6c6f4532`; **none has a map plan**: `git grep -l '^work: WK-<n>' origin/main -- docs/plans` returns nothing for each):
1. **WK-673** (dislocation with attribution) **and WK-674** (deployment, switchover, rollback, shadow, tenancy per ADR-710), **in parallel**;
2. **WK-675** (frontend: Vue Flow designer, rate-table editor, quote sandbox, dislocation views), after WK-672 Slice 4's `score/compare` and WK-673's views;
3. **WK-690** (`expression` custom objectives), an independent track at any time, after #830 merges;
4. **WK-1170, then WK-1169** (docs-only), in gaps;
5. **The P2 standing maintenance Work** (#840), which never closes inside the phase. It is "landed" when it is minted and #841 is merged.
```

**The budget instruction, verbatim** (the deputy's entry of 2026-09-28 16:18:50 BST,
items 1–2):

```text
1. **Priority order for the budget:** (a) **WK-672 to closure** (S2 → S4 → CR); (b) **the two governance fixes**, #861 and the approval-status PR; (c) **plan review 15** and the P2 exit criteria; (d) merging what is already queued (#855, #862, the RS records #833/#834/#837, #843/#844/#845/#847/#848/#856, the map plans and RLs).
2. **The extended goal is throttled until the reset:** the three map plans already drafted (WK-673/674/690) finish and are accepted, since they are docs and nearly done. **No slice of WK-673, WK-674 or WK-690 starts, and no WK-675/1170/1169 planner is spawned, before WK-672 closes.** After that, only if the remaining budget allows, and I will say so. The maintainer may override.
```

**A tension to rule on.** "WK-673 and WK-674, in parallel" meets `delivery-process.md` §8:
*"no two Slices run at once, at any layer"*, and *"The interest §8 protects is resource
contention, not plan stability"* (`delivery-process.md:156`, :164). Under §8, "in parallel"
can mean at most that their slices are interleaved one at a time, which saves no time. Only
the maintainer can set §8 aside.

**Proposed change: WK-674 first, then WK-673.** The reasons:
- G2's deploy step (`uat` → `prod`) and the NFR dispositions G4 (a) and (b) all land in
  WK-674.
- WK-674 carries the tenancy mechanics ADR-710 requires.
- WK-673's dislocation is needed for the demo, but its views gate only WK-675.

**The cost of each order under the budget:**
- **The budget.** The week is at 71 % and runs out tomorrow evening, before Saturday's
  03:00 reset. The deputy's throttle means no slice of WK-673, WK-674 or WK-690 starts before
  WK-672 closes.
- **Either order, up to the reset.** Neither WK-673 nor WK-674 starts before the reset
  unless WK-672 closes with budget left. Up to the reset the two orders cost the same.
- **After the reset:**
  - The maintainer's order interleaves WK-673 and WK-674. Each is then about half done at
    any point, and the deploy step G2 needs arrives last.
  - WK-674 first delivers the deploy step and the NFR owners first, and delays WK-673 by
    WK-674's length.
  - WK-675 waits for WK-673's views under both orders.
- **Honest bands.** None of WK-673, WK-674 or WK-690 has an accepted map plan yet (#843,
  #844 and the WK-690 plan are open), so their slice counts, and any duration band, are not
  derivable at `9f6bfed1`. The band is re-derived when each map plan is accepted.

**Recommendation:** WK-672 closes, then the approval-status fix, review 15 and the queued
merges, all up to the reset. After the reset: WK-674 → WK-673 → WK-675, with WK-690
independent as the maintainer ordered, then WK-1170 → WK-1169, with WK-1178 standing.

**Maintainer acceptance (Proposal 2): ACCEPTED by the maintainer**: WK-674, then WK-673, then WK-675; WK-690 independent; then WK-1170, then WK-1169; `delivery-process.md` §8 stands. The deputy's entry of 2026-09-28 19:05:44 BST is quoted whole under "Acceptance" at the foot.

## Proposals 3–12 — the rest of the agenda

- **3. The permission catalogue's source of record** (FD-1197; #856, open).
  **Recommendation:** the code's coarse names are P2's record (the deputy's DP-A (c) on #856),
  with `06` amended to follow, and the fine split carried to WK-676 (P3). Plan review 16
  decides the general source-of-record question going forward.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **4. The environment-scoping spec gap** (#848, open).
  A human deploy grant is not scoped by environment.
  **Recommendation:** a `06`/`07` spec change that scopes `deployment:promote` to named
  environments, owned by WK-674 and landed with its environment record.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **5. Approval hooks never tested against their state machine, and tests that passed for the
  wrong reason.** #861's fixtures submitted drafts, and
  `test_create_submit_approve_a_rating_version` passed only because of FD-1200's second
  defect (the false audit before-state).
  **Recommendation:** a WK-1178 slice of per-type state-machine tests over all seven
  approvable types. It covers real create paths for the four types with no author column
  (#861 audit observation 2) and the three types whose approval hook moves nothing (FR-351's
  new clause). Each test is red first against the pre-fix tree.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **6. Harness and working-directory findings.**
  - The isolation worktree is auto-removed after a plan-only first turn.
  - The team's PROCESS CWD rule: every process is started with `env -C <own worktree>`.
  - FD-1196, the test-DB name collision.
  - The heredoc-backtick incident: an unquoted heredoc executes backticks.

  **Recommendation:** fold the first, second and fourth into `dev-commands` and
  `git-hygiene` as skill rules (`CLAUDE.md` §12). FD-1196 stays WK-1178's.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **7. The spike-brief guardrail** (the F1 and F3 load breaches).
  **Recommendation:** a spike brief states resource caps on the command line, and a stop
  kills the agent's own process first, then its children, by PID. Killing only the children
  let the agent relaunch them. Write it into the executor charter and the spike brief
  template.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **8. The status-at-filing check gap** (FD-1190).
  **Recommendation:** add an audit-docs check that a governed record's `status:` is valid for
  its family at filing, owned by WK-1170.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **9. The example-id incident.** An id-standard example integer collided with the live
  sequence on #830's mint. It was fixed by #860, whose guard makes `doc-id next` refuse an
  example integer. **Recommendation:** record it as closed, with no further action.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **10. FD-1200 (critical) and FD-1199 as open P2 risks with owners.**
  - FD-1200: **fixed** by #864 (squash `e6a9ca71`, FR-351), the WK-1178 approval-status PR,
    after this review's tree. G3's FD-1200 limb is met once #865's register row closes it
    (amended at acceptance, the P10 line).
  - FD-1199: the lead owns it. Its triage goes ahead of any slice on the scoring path if an
    abort recurs (PL-1189 acceptance item 9). It is a G3 exit condition.

  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **11. audit-docs check 2 scans fenced quotations.** A quoted channel entry inside a
  `text` code fence is parsed as live text. **Recommendation:** WK-1170 decides whether
  check 2 skips fenced blocks, with a broken-input proof.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **12. FR-432, FR-433, FR-434, FR-435 and FR-438 are on no roadmap row.**
  `grep -c 'FR-43[2-5]\|FR-438' docs/roadmap.md` prints 0 at `9f6bfed1`.
  **Recommendation:** assign FR-434 and FR-435, with NFR-534 and NFR-531, to WK-674 if they
  are deployment-platform FRs. Otherwise carry them to P3 by a dated line. Either way a row
  names each.
  **Resolved at acceptance (the P12 line):**
  - All five are `07-platform.md` §3 deployment and packaging rows.
  - FR-434 and FR-435, with NFR-534 and NFR-531, go to **WK-674**.
  - FR-432, FR-433 and FR-438 are **carried to P3**, subject to the maintainer's P1 ruling on G2. **Resolved by that ruling:** G2's `prod` is the platform's environment (FR-429), not production packaging, so they stay carried to P3 (the 19:05:44 entry).
  - The roadmap edit naming each row is the lead's, after acceptance.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **13b. A register pass** (the auditor's, not this review's) for the four cells found above:
  - F34's stale PR #416 (line 76);
  - F28's mixed deferral and fixed marker (line 70);
  - FD-1190's and FD-1194's `status: active` files against their closed register cells (lines 177 and 181).

  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot
- **13. Plan-status staleness.** A plan's `status:` and the INDEX execution column lag its
  real state (for example, `PL-930` stays `active` as the map while its leaf plans execute).
  **Recommendation:** WK-1170 owns an INDEX-derived check. No hand edit.
  **Acceptance:** accepted by delegation — the deputy's entry of 2026-09-28 18:13:19 BST, quoted whole under "Acceptance" at the foot

## 1. Completion — derived, never recalled

Since review 14:
- WK-695 (#839, `CR-1183`) and WK-696 (#849, `CR-1179`) closed with acceptance lines.
- WK-672 Slice 1 closed (`LG-1182`), and Slice 2's plan is active (`PL-1189`).

The 8 open Works are listed under Proposal 1. **No change** beyond G1.

## 2. Omission — what would nobody notice was missing?

Four omissions:
- the P2 exit criteria (Proposal 1);
- the NFR owners (G4);
- FR-432 to FR-438's missing row (item 12);
- per-type state-machine tests (item 5).

## 3. Skills and research — the gap analysis

- The working-directory and heredoc rules are not yet in a skill (item 6).
- The spike guardrail is not in a charter (item 7).
- The research records for spikes F1, F2 and F3 are open PRs (#837, #834, #833), and F4 is
  `RS-1176`. **No other change.**

## 4. Document drift

- The register row F34 cites a stale "PR #416" (L76).
- F-W9-1 still names "a ruling before WK-674" (L59), and G4 (b) resolves it.
- `PL-930`'s "may run in parallel" was superseded by RL-1172 item 6.
- The roadmap's `## P2` header fields are empty (Proposal 1).

## 5. Shape — is the cut still right?

- WK-677 (P3) now receives FD-1198's component-author limb.
- **The one shape proposal is Proposal 2's order.** No Work is proposed for a split or a
  move to P3, other than the dated carries in G4 (d) and item 12.

## Output

- **Retry counters:** not re-read in this pass. **No change** is proposed on them.
- **Proposals needing the maintainer's line:** 1 (exit criteria, G1–G6), the G4
  dispositions, the finding resolutions, 2 (sequencing), and 3 to 13.

## Verdict

- Every agenda item of the deputy's 17:18:55 entry and of the lead's brief has a written
  proposal.
- The open P2 finding set is stated by predicate: 91 rows, each with a resolution or a
  proposed one.
- Every P2 NFR has an owner or a proposed one.

**Every proposal now binds, as amended.** Proposals 1 and 2 are accepted by the maintainer, with P1's two amendments. The G4 dispositions, the finding resolutions and Proposals 3 to 13b are accepted by delegation (the foot).

## Acceptance

**Proposals 1 and 2, the G4 dispositions and the finding resolutions:** the deputy's entry, with the maintainer's words verbatim, quoted whole with its heading time:

```text
## 2026-09-28 19:05:44 BST · deputy · PLAN REVIEW 15: MAINTAINER ACCEPTS P1 (G1–G6) and P2 (WK-674 first), with two standard-conformance amendments; G4 and finding resolutions accepted by delegation

**The maintainer's words, verbatim** (given to the deputy in this session at the time in the heading): *"accept G1–G6 and WK-674 first, one small issue does the gate created satisfied the docs standard created."*

**P1 is accepted by the maintainer. P2 is accepted by the maintainer:** WK-674, then WK-673, then WK-675; WK-690 independent; then WK-1170, then WK-1169. §8 stands.

**The maintainer's question, answered by the deputy.** Read at origin/main 4fb07b6c, it becomes two amendments to P1, which go into the acceptance line (the CR text stays as filed):
1. **G1–G6 are exit criteria, not gates.**
   - `document-ids.md` §1.3 and §1.10(b) define the milestone's `gates:` field as the three **dated freeze gates**: plan, code and docs.
   - `docs/process/checklists/phase-close.md:75–77` fails a phase whose freezes were not "declared with dates" and passed on time.
   - P1's "write them into … `gates:` and `exit criteria:`" is therefore amended: **G1–G6 go into `exit criteria:` only**, citing this CR.
   - **`gates:` and `target:` stay `~` until dated.** After WK-672 closes, the lead proposes three freeze dates and a target from the ETA. The deputy puts them to the maintainer; this is P2's exit, which the deputy promised to show before dating. They must be declared **before** the first of them passes.
2. **G5 is restated without the pasted number.** "DISCLOSED no higher than … 851 at 9f6bfed1" pastes a value (CLAUDE.md §13: a constant is cited by symbol, never pasted). G5 now reads: **on the exit tree, `audit-docs.py` rc 0 with "All checks passed."**, where the ceiling is the governed record at `_docid.W37_11_RECORD_PATH` (`docs/process/residue-ceiling-record.md`), plus the other three docs checks rc 0, plus the two-half gate of §11.

**Conforming as written:**
- G3's predicate carries its tree, corpus, runnable code and three controls (CLAUDE.md §13).
- G4's list carries its greps and tree.
- G2's `07` FR-429 citation is verified at `07-platform.md:140`.

**By delegation (deputy):**
- **The G4 dispositions (a)–(e) are accepted.** Under (b), NFR-489, NFR-490 and NFR-502 go to **WK-674**, not "accepted as failing".
- **The finding resolutions are accepted as proposed,** 91 rows.
- **The P12 condition is resolved by G2 as accepted:** G2's `prod` is the platform's environment (FR-429), not production packaging. So FR-432, FR-433 and FR-438 **stay carried to P3**.

**Follow-up commit on #863:**
- the acceptance lines for P1 and P2 quote this entry whole;
- P3–P13b quote the 18:13:19 entry, with the id note from the 18:13:57 ruling;
- then re-mint at its turn and request a fresh ACK.

The roadmap `## P2` edit (`exit criteria:` only) is the lead's, after the merge.
```

**Proposals 3–13b:** the deputy's entry, quoted whole with its heading time:

```text
## 2026-09-28 18:13:19 BST · deputy · #863 / CR-1202: HOLD the merge until every acceptance line exists; P3–P13b ruled below for the follow-up commit

**Hold.** A closure record is frozen when it files. `document-ids.md:134` lets only `status:`, `superseded_by:` and `corrected_by:` be edited after that, so a CR merged with blank lines can never carry them. The precedent is review 14: CR-1167 went in as one squash (df8e5811, #823) with its line in the body (`:199`). Do the same here. Add one follow-up commit on #863 with all the lines, then request a fresh ACK at that head.

**P1 and P2** are the maintainer's. They have been put to the maintainer and are not yet answered; do not write anything in their place.

**P3–P13b: accepted by delegation** (the deputy, on the maintainer's instruction of 2026-09-26 17:02:52 BST, and the extension of 2026-09-28 ~13:50) with these amendments:
- **P3, P4, P5, P6, P7, P8, P9, P11, P13, P13b**: accepted as written.
- **P10**: accepted, amended. FD-1200 is **fixed** by #864, squash e6a9ca71 (FR-351). G3's FD-1200 limb is therefore met once #865's register row closes it. The CR must say so, citing e6a9ca71, and must not read as open. FD-1199 stays as written.
- **P12**: accepted, with its condition resolved. All seven FRs are `07-platform.md` §3 deployment/packaging rows (origin/main e6a9ca71, `:148–154`).
  - FR-434 and FR-435, with NFR-534 and NFR-531, go to **WK-674**.
  - FR-432, FR-433 and FR-438 (images, Helm, signed images and SBOM) are **carried to P3**, subject to the maintainer's P1 ruling: if G2 (the exit demo "to prod") needs any of them, that ruling moves it back into P2.
  - FR-436 and FR-437 are not in P12's list and not ruled here.
  - The roadmap edit naming each row is the lead's, made after acceptance, not in this CR.

Paste this entry verbatim into CR-1202's foot as the P3–P13b line, with its heading time. Quote the maintainer's P1 and P2 lines the same way once they are given.
```

The quoted entry names this record by its first-minted number, 1202, released 2026-09-28 before merge and since minted as FD-1202; its id is the one in this file's front matter.

## Sources

- The deputy's channel entries of 2026-09-28, quoted or carried in substance: 13:51:08 (the
  maintainer's order), 16:18:50 (the budget), 17:18:55 (the agenda). The channel file is
  local and is not in the repository.
- `docs/roadmap.md` (`## P2` at :555), `docs/findings/register.md` and
  `docs/process/delivery-process.md` §8, at `9f6bfed1`.
- `CR-927` (WK-671's record) and `CR-754`, for the NFR measurements.
