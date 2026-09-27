---
id: RL-987
family: ruling
title: DP-1: the creating instruments land in W37-6's commit, and the set is a criterion rather than a list of seven
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-migration-preconditions-rulings.md
---

# WK-697's migration preconditions — DP-1, DP-2, DP-3 and the vendored-skill criterion, ruled (2026-09-02)

**What this is.** Four questions that must be settled before Slice W37-6 — RFC-937's single
supervised migration run — may start. Three are the `Decision points` rows of
[`../plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`](../plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md)
marked blocking on W37-6; the fourth is a self-contradiction inside
[`RFC-937`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) §1.5, raised by the W37-2 executor and
relayed by the lead. Each is ruled below as Rulings 66 through 69.

**The frozen plan is not edited.** `CLAUDE.md` §2 freezes a filed plan at its date, and this
role's charter forbids editing one. This record is the sibling that supplies the resolver ids
its `Decision points` table asks for; the table's own cells stay as filed.

## Authority — and it was not the maintainer personally

- **DP-3** was assigned to this role by the plan itself (*"decision-maker, one ruling"*).
- **DP-1 and DP-2** are labelled `maintainer` in that table. The lead routed both here under
  the maintainer's delegation of 2026-09-01, recorded at
  [`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md)
  §1: *"I authoris the lead to allocate technical questions to decision-maker to make decision
  on behalf of me."* **A reader must be able to see the maintainer did not rule these
  personally, and this paragraph is that record.** The lead's routing judgement was accepted,
  and for DP-1 the note's own text turns out to make the routing unnecessary — see RL-987's
  §1.
- **The vendored-skill question** (RL-990) is a spec-versus-implementation conflict, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) and
  [`delivery-process.md`](../process/delivery-process.md) §3 already place with this role
  (*"Rules decision points and spec-vs-code conflicts before a plan or slice can proceed"*).
  No delegation is needed for it.
- **Nothing here reopens D0–D14.** RFC-937 §2's fifteen decisions are fixed inputs. D14
  (*"Enforcement red from the migration PR"*) is load-bearing for Rulings 66 and 69 and is
  applied, never questioned.
- **Nothing here was declined.** The boundary that would have made me decline is stated at the
  end, under *What would have gone back to the maintainer*.

**Numbering continues at 66.** Verified rather than relayed:
`git grep -hoE '^#+ Ruling [0-9]+' -- docs/plans` at `04ec6bf` yields a maximum of **65**, and
`git grep -nE 'RL-872[6-9]' -- docs .claude` returns nothing.

**Evidence tree.** Every measurement below was taken at `04ec6bf` — `origin/main`, fetched at
the start of this session — over the corpus `git ls-files`, **1360 tracked files**. Where a
figure is quoted from another document, the tree that document states is named with it.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while its own
docstring disclaims exactly that scope. That disagreement is register finding (F68) — see
[`../findings/register.md`](../findings/register.md) — carried forward with RFC-937's migration as
its trigger. It is honoured here rather than evaded, and the check is not patched from this
branch.

1. `git grep -c '^## RL-872[6-9] —' docs/rulings/INDEX.md#2026-09-02-w37-migration-preconditions-rulingsmd`
   returns `4`, and `git grep -n '^#\+ Ruling ' docs/plans/` shows 66–69 filling the gap
   immediately after RL-944 with no duplicate and no skip.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option** in its
   opening paragraph, with the measured evidence that separated them.
3. Each ruling carries a `### 4.` section stating its acceptance as **a violation that must
   become detectable**, never as a description of correct behaviour.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-dp-rulings-66-68` names exactly this one new file.
   No frozen plan, no note, no roadmap row and no script is edited by this branch.
6. Every numeric claim below names the tree it was measured at and the command that produced
   it, per `CLAUDE.md` §13's reference rule.

---

## RL-987 — DP-1: the creating instruments land in W37-6's commit, and the set is a criterion rather than a list of seven

### 1. Verified first, at `04ec6bf`

| Claim | Verdict |
|---|---|
| The plan's "seven creating skills" is a real class in RFC-937 §5.4 | **Confirmed.** §5.4 marks six rows **primary** — `writing-plans`, `subagent-driven-development`, `close-workstream`, `phase-review`, `adr-write`, `spec-change` — and gives `library-spike` an H row reading *"writes `RS- kind: spike` via `doc-id.py next`"*. Seven instruments that mint a governed document. §8's S3 phrase *"the eleven primary skills"* is that seven plus `docs-audit`, `dev-commands`, `git-hygiene` and `reporter-cycle`; "seven creating" is a correct subset of it, not a different set |
| The window is real | **Confirmed, and the plan's enumeration of it is under-inclusive.** A document created between W37-6 and W37-7 under the retired grammar fails check 30 (a header on every file under `docs/`) and check 31 (id, filename and directory agreement). The plan says *"checks 30-32"*; check 32 governs citation resolution and fires only if the new document also cites a retired id, while **check 36** — *"no pre-migration form survives outside the CSV and `was:` lines"* — fires on the filename alone. Check 33 (`work:`/`slice:` must resolve) and check 39 (a merged PR's title names its `SL-`) are further exposure the plan does not name |
| D14 is what makes the window bite | **Confirmed.** §2, D14: *"Enforcement red from the migration PR"*, reason *"No population to phase in"*. There is no warn phase and no date switch to hide behind; W37-4's own text rules both out |
| The window is empty, so (c) is a survivable bet | **Refuted, from the plan's own text.** W37-6's acceptance requires §7 (a)–(h) *"each recorded with its command and output in the slice's ledger"*, and W37-7's requires *"every §5.4 row not landed in W37-6 is named by a commit in this slice's ledger"*. A ledger is an `LG-` document (§1.2, §1.4) and the instrument that mints one is `subagent-driven-development` — one of the seven. Executing W37-7 at all therefore creates at least two governed documents inside the window (its leaf plan, `PL-`, and its ledger, `LG-`) using instruments that have not been migrated. **The window is occupied by construction** |
| Stage-to-slice allocation is the maintainer's | **Refuted, by RFC-937's own header block.** Status row: *"The planner cuts §8 into slices."* Owner row: *"The maintainer accepts. **The planner slices §8.** The executor runs the migration script and the hand edits."* No decision in §2's D0–D14 concerns sequencing. §8's stage boundaries are not a maintainer decision |
| The plan already exercised that authority | **Confirmed, twice.** *"Departure 1 from §8"* cuts S1 into four slices on the planner's own authority without escalating. And W37-6's *"What lands in this one commit"* list, introduced as *"§8's S2 list, verbatim"*, adds `graphify-docs-extract.py` — an H row in §5.5 that §8's S2 sentence does not name. An H row has already been moved from S3 into S2 without anyone treating it as a maintainer question |
| The marginal cost is small | **Confirmed.** §5.4's final row makes *"every `SKILL.md` (46) — header stamped"* an M row, so W37-6's script already writes to all seven files. Option (a) adds content to files the commit touches regardless |

### 2. Ruled

**Chosen: option (a)** — the creating instruments land in W37-6's single commit.

**Rejected: option (b), freeze all document creation between W37-6 and W37-7.** It cannot
cover the interval it exists to protect: W37-7's own leaf plan and ledger are created inside
that interval, so the freeze would have to exempt the work it is protecting, which is not a
freeze. Independently, a document-creation freeze is a standing instruction to every role on a
team whose every artifact is a document, with no bounded end date — that is a process
direction, not a mechanism, and it is not this role's to impose.

**Rejected: option (c), accept the window.** For the same reason. "Accept" would mean
accepting a red gate on W37-7's own pull request, which contradicts D14 rather than living
within it.

**And the set is a criterion, not a list.** Seven is the floor, not the ceiling. The rule:
**every instrument whose output is checked by checks 30–39 from the migration commit lands in
W37-6.** W37-6's leaf plan derives the set by walking checks 30–39 and asking of each, *which
instrument tells an author how to produce the thing this check tests?*, and records the derived
list with the check each entry answers to. The seven the plan names are the floor;
`git-hygiene` (check 39's branch and PR-title grammar) and `.claude/skills/README.md`
(`CLAUDE.md` §12 requires the index to move with the skills, and §5.4 gives it a *"creates"*
column) are named here as candidates the derivation must dispose of **explicitly — adopted or
excluded with a reason** — not as members asserted by this record. A list of exemplars invites
fixing the exemplars and stranding the rest; a criterion does not
([`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md)).

### 3. What it obliges

- W37-6's leaf plan carries a section deriving the instrument set from checks 30–39, one row
  per instrument naming the check that puts it there. The plan's seven are the floor.
- Every instrument moved into W37-6 has its `Verified` date refreshed in the same commit
  (`CLAUDE.md` §12), and `.claude/skills/README.md` moves with them if the derivation includes
  it.
- W37-7's scope needs no plan edit: it is already worded *"§5.4's rows, less whatever DP-1
  moves into W37-6"*. The two leaf plans carry the split.
- The dated maintainer go-ahead that W37-6's preconditions already require **covers the
  enlarged commit only if the enlargement is disclosed when it is asked for.** It is not
  assumed by this ruling.
- `docs/roadmap.md`'s WK-697 row currently reads *"three block the migration run itself (two the
  maintainer's, one the decision-maker's)"*. After this record none of the three is the
  maintainer's. Amending that row is the lead's, not this role's — flagged, not done.

### 4. Acceptance — the violation that must become detectable

Two, because a mutation proof tests the implementation against the check and never the check
against the requirement.

1. **Requirement-facing, and it costs nothing extra because the artifact must exist anyway.**
   W37-7's own leaf plan and its ledger are created by following **only** the instruments
   merged in W37-6, and `python3 scripts/audit-docs.py` is run on W37-7's branch *before* any
   hand correction. **Violation: any of checks 30, 31, 33 or 36 fires on either of those two
   files.** If one does, DP-1 was not implemented — and hand-correcting the file rather than
   the instrument is the same failure repeating, so the correction is filed as a finding
   against W37-6, never as a quiet edit.
2. **Implementation-facing.** For each instrument in the derived set, restoring that one file
   to its merge-base content and re-running W37-6's acceptance sweep must produce at least one
   hit naming that file. **Violation: an instrument whose reversion changes nothing any check
   can see** — it is either out of scope or its edit was cosmetic, and either way the set was
   derived wrong.

---
