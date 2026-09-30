---
id: RL-9854
family: ruling
title: WK-1169 DP-2 and DP-3 decided — charters point at §1.6, one exact owner table feeds the matrix and each directory's Permitted owners line, and check 35 enforces it
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: eeda8f4ba20d247ac18d6a35d7f81589c8527ed2
phase: P2
work: WK-1169
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1277, PL-1276, WK-1170, FD-1161]
---

# RL-9854 — WK-1169 DP-2 and DP-3 decided — charters point at §1.6, one exact owner table feeds the matrix and each directory's Permitted owners line, and check 35 enforces it

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). The session's
own `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`.

The record was prepared at effort `medium` (PR #940, head `8bfd305a`, "PREPARED, NOT
RULED"). Its evidence and prepared recommendations are kept below as they were prepared.
**The decisions are in "Ruled"**, and both depart from the prepared recommendations, for
reasons found at this pass: §1.6's prose cannot be parsed into owners (item A below), and
check 35 applies a directory's list to that directory's own README and INDEX (item B). It
keeps the working id 9854; the id is minted at the lead's merge turn.

## Evidence

**Trees.**
- The map plan is **PL-1277** (PR #931; first read on `origin/wk1169-map` at
  `19b086ea13f3f85ff15bda2e182b7899ba9fd75c`, before it minted). It is now cited by section
  heading.
- *Refreshed 2026-09-30 at origin/main `0bc69b5b`.* Every premise below was re-checked there.
  `document-ids.md`, `audit-docs.py`, `doc-index.py`, `CLAUDE.md:223-225` and the charters are
  unchanged. The §1.6 citation counts per charter are unchanged (planner 4). No
  `Permitted owners:` line exists yet. The `owner: lead` findings are still exactly FD-1067,
  FD-1068, FD-1069, FD-1074 and FD-1079: the new FD-1280 to FD-1284 are auditor-owned
  (103 auditor, 5 lead).
- Everything else was read at `origin/main` `aa14e90dd77c7461aa35cc6461557b129959463f`.
- *Re-verified 2026-09-30 at `eeda8f4b` for this ruling.* `git diff --stat 0bc69b5b eeda8f4b --
  docs/process .claude scripts docs/plans/PL-01276* docs/plans/PL-01277* CLAUDE.md` prints
  nothing. The facts the ruling adds are in "Presence and absence, as verified".
- The plan read its premises at `19c395ac`. Since then, #926 changed `planner.md` and
  `lead.md`.

**The rows.**
- DP-2 is in PL-1277 §Decision points: *"What form does '§1.6 made binding in each charter' take?"* It blocks
  Slices 2 and 3.
- DP-3 is in the same table: *"What does each directory's `Permitted owners:` line say?"* It blocks
  Slice 2.

**Premises, checked at `aa14e90d`.**

| Premise | Status | Evidence |
|---|---|---|
| Charters cite §1.6, and no charter↔§1.6 check exists | CONFIRMED, with one count stale | `git grep -i charter origin/main -- 'scripts/*.py'` finds only comments. Only one count moved: `planner.md` now cites §1.6 4 times, where the plan says 3 (#926 added `planner.md:74`). |
| (DP-2) "(a) writes seven copies" | **Partly the status quo already** | The charters already restate their §1.6 rows. For example, `.claude/roles/decision-maker.md:19-26` says *"Concretely, per `document-ids.md` §1.6: …"* and quotes the rows. So (b) and (c) imply **striking** these restatements, and the plan does not say so. Charters are `owner: maintainer`. |
| The binding by reference already exists at the top | CONFIRMED | `CLAUDE.md:223-225`: *"`document-ids.md` §1.6 … is the authority on which role may write which document family, complementing this section's own rule that a role writes what its charter names."* |
| A third authority declaration | CONFIRMED, not named in the plan | `docs/process/delivery-process.core.json` has a `roles` block with per-role `authority` lists. They are per action, not per family. |
| (DP-3) only a fixture carries `Permitted owners:` | CONFIRMED | `git grep -n "Permitted owners" origin/main` finds the fixture `tests/fixtures/docs-ids/w37-4-checks/check35-readme-allowlist/README.md:3`, the regex at `scripts/audit-docs.py:2433`, and prose. No `docs/*/README.md` has the line. |
| (DP-3) "`owner:` is the creator (§1.5)" | **DIFFERS** | `document-ids.md:127` (§1.5) says only *"a filename under .claude/roles/, or `maintainer`"*. The creator link comes from §1.6's column header *"Owner — creates & amends"* (`:148`). |
| (DP-3) "§1.2's Reference row does not allow a generated README" | **DIFFERS** | `document-ids.md:55`, the Reference row, covers *"every `README.md` anywhere in the tree"* with mutability *"living, or `generated: true`"*. A generated README is permitted. |
| (DP-3) "verbatim" cell content | **Will not parse** | `readme_owner_allowlist` (`scripts/audit-docs.py:2497-2510`) splits the line on commas. §1.6 cells are prose; for example the RL cell is *"decision-maker; the maintainer may author one on scope or process …"*. |
| Records whose `owner:` lies outside the creator cell | CONFIRMED, not named in the plan | Five `docs/findings/FD-*.md` records carry `owner: lead` (FD-1067, FD-1068, FD-1069, FD-1074, FD-1079). §1.6's FD owner is the auditor. The four `docs/{rulings,findings,closures,plans}/README.md` files checked carry `owner: lead`. `owner:` is immutable on frozen and write-once records (check 34). A strict list would therefore fail check 35 on existing records (`audit-docs.py:2955-2963`). I read this from the code; I did not run it or trace check 35's iteration set, so whether the READMEs themselves are checked is unverified. |

## DP-2: the form of the charter binding

| | Option | For | Against |
|---|---|---|---|
| (a) | Each charter restates its §1.6 rows, and a check compares the two | Each charter reads on its own | Seven copies of one table (RFC-756). This is close to today's state, without the check. |
| (b) | Each charter points at §1.6 with no restatement; the generated matrix is the per-role view | One source; CLAUDE.md:223-225 already binds this way | Nothing catches a charter that grants **more** (FD-1161's case) |
| (c) | (b), plus a check that no charter grants an action §1.6 does not give that role, with the matrix derived from §1.6 | One source, and it checks the direction that has failed | Needs a machine-readable **grant** on both sides: §1.6's prose cells parsed, and a charter grant syntax defined |

**Prepared recommendation (superseded by "Ruled"): (c), as the planner recommends, with three things the ruling must add.**
1. **Define "grant".** State what text in a charter the check reads, for example a fixed
   `Writes:` line naming families. Without a defined grant, (c)'s check has no input.
2. **The restatements are struck.** Striking them is a maintainer MERGE-ACK on each charter,
   and each charter keeps a pointer.
3. **`delivery-process.core.json`'s `roles.authority`.** Say whether it is out of the check's
   scope (it is per action) or reconciled with it.

**Fallback:** if no grant syntax is acceptable to the maintainer, use (b), plus a charter
sweep in the auditor's Work-close checklist.

## DP-3: what the `Permitted owners:` line says

| | Option | For | Against |
|---|---|---|---|
| (a) | The roles in §1.6's Owner cell for that family, verbatim | Simple | Verbatim will not parse. It omits `lead`, which owns every README checked and five FD records. It would fail check 35 on existing immutable records. |
| (b) | (a) plus the Accepts / decides roles | Covers more existing records | Acceptors never write `owner:`, so it permits what §1.6 does not |
| (c) | Generated into each README by `doc-index.py` from §1.6 | One source, consistent with DP-2 (c)'s "derive from §1.6". Its stated blocker (§1.2) is false at this tree (`document-ids.md:55`). | Ten READMEs gain a generated block. The parse of §1.6 is the same dependency as DP-2 (c). |

**Prepared recommendation (superseded by "Ruled"): (c). This departs from the planner's (a).** The planner's two reasons for (a)
do not hold at this tree:
- the §1.5 citation does not carry the owner=creator claim;
- §1.2 permits a generated README.

(a) as written also cannot parse, and it would fail existing records. (c) takes role
**names** extracted from §1.6's Owner cell, as the union over the family's kinds.

Whichever option is ruled, the ruling must also decide what happens to existing records whose
immutable `owner:` falls outside the line:
- (i) exempt records `created:` before the line lands;
- (ii) add each such owner to the list, which widens §1.6 by the back door;
- (iii) file each one as an FD.

The provisional choice is **(i)** with the cutoff date written in the README line, plus
**(iii)** for the one conflicting `kind: work` closure record owned by the lead, if the high
pass confirms it: the evidence agent reported it, and I did not re-verify it here.

If DP-2 is ruled (b), DP-3 (c) loses its shared parser. (a) with names extracted, not
verbatim, plus (i) is then the fallback.

## Ruled

### Presence and absence, as verified at `eeda8f4b`

| Claim | Verdict | How it was verified |
|---|---|---|
| **A.** §1.6's prose can be parsed into owners by role name | **false at this tree** | `ownership_matrix()` (`scripts/doc-index.py:958-969`) counts a role as an owner of a family whenever `role in owner_text`, over `_OWNERSHIP_TABLE` (`:924-947`), a prose transcription of §1.6's Owner column. The generated matrix (`docs/INDEX.md:1445-1456` at `eeda8f4b`) therefore lists the **planner** as an owner of `work (WK)`, from "planner writes its map plan". It lists the **lead** as an owner of `proposal (RFC)`, from "lead assesses", and of `reference: skills`, from "lead approves". §1.6 (`document-ids.md:153`, `:157`, `:169`) makes none of those roles an owner. Any check built on name-matching §1.6's cells inherits this over-inclusion. |
| **B.** Check 35's second clause reaches each directory's own README and INDEX | **present** | `check_owner` (`scripts/audit-docs.py:2920`), read in full. For every document in `_id_scope_documents()`, it reads `path.parent / "README.md"`'s list and fails an owner not in it (`:2956-2963`). It does not exclude the README itself. Loading the module and listing its scope at `eeda8f4b` (the loader is in "Reproducing B and C" below) gives 13 in-scope READMEs, every one `owner: lead`, and `INDEX.md` files in `docs/rulings`, `docs/plans` and `docs/closures`, also `owner: lead`. §1.6 has no row for either kind of navigation file. |
| **C.** Existing records whose owner is outside their family's Owner cell | **six, listed** | The same scope listing, per directory. **Five findings owned by `lead`**, against §1.6's FD owner, the auditor (`document-ids.md:166`): `FD-1067`, `FD-1068`, `FD-1069`, `FD-1074` (all `created: 2026-09-18`) and `FD-1079` (`2026-09-19`). **One closure of `kind: work` owned by `lead`**, `CR-1063` (`2026-09-17`), against §1.6's CR row, where `work` is the auditor's (`:165`). Every other in-scope record's owner is in its family's Owner cell. |
| The parser check 35 uses | **present** | `readme_owner_allowlist` (`audit-docs.py:2497-2508`) splits the one `Permitted owners:` line on commas. A prose cell would not parse. |
| A check that reads charter **content** | **absent** | `scripts/audit-docs.py`'s checks, numbered up to 39 (`document-ids.md:220-236`), do touch the charters: check 35 builds `_VALID_OWNERS` by globbing `.claude/roles/*.md` for their **filenames** (`audit-docs.py:2431-2432`), and check 30 checks each charter's **header** (`document-ids.md:226`). None of them reads what a charter's body grants. *(Corrected after auditor-docs' audit of `561e329d`. This row said "none of them reads `.claude/roles/`", which is false.)* |
| `delivery-process.core.json`'s `roles` | **present, per action** | `docs/process/delivery-process.core.json:38` onward: seven roles, each with `authority` naming process **actions** (for example `lead`: `plan_gate_decision`, `lead_verdict_action`, `merge`), not families. |

**Reproducing B and C.** Run from a checkout of `eeda8f4b`. `scripts/audit-docs.py` is loaded
as a module, with `sys.modules["auditdocs"]` set before `exec_module`, since its dataclasses
need the module registered. Then `_id_scope_documents()` is iterated, and each file's owner
is read with `_docid.parse_header(path).owner`, grouped by `path.parent`. The result, per
directory with a README: `docs/adrs` decision-maker 6, lead 1; `docs/closures` auditor 36,
lead 19; `docs/contracts` lead 1; `docs/findings` auditor 103, lead 6; `docs/ledgers`
executor 20, lead 1; `docs/plans` planner 133, executor 4, auditor 2, lead 2; `docs/research`
executor 6, auditor 4, lead 1; `docs/rfcs` maintainer 21, lead 1; `docs/rulings`
decision-maker 135, maintainer 11, lead 2; `docs/workflows` decision-maker 5, lead 1. The
`lead` counts are the navigation files, the 16 `kind: review` closures (the lead's by §1.6),
and the six records of C.

### The one decision under both DPs: an exact owner table

`_OWNERSHIP_TABLE`'s second column becomes **an explicit tuple of owner roles** per family
and `kind`, in place of prose. For each row it also gets an explicit tuple of the roles
its §1.6 cell *mentions* without making owners. A drift check (Slice 3) fails when:
- a role in either tuple no longer appears in the §1.6 cell;
- a role name appears in the cell and is in neither tuple.

A change to §1.6's prose therefore fails the gate until the table classifies it. There is
**one** table, used by `ownership_matrix()`, by DP-3's check and by any later check, and
never copied. That satisfies PL-1277's Acceptance item 4 ("derived from §1.6 rather than a
hand transcription"): the transcription is now a classified one that §1.6's own text
checks.

It needs no `docs/process/` amendment. If the maintainer later wants the roles written into
§1.6 itself, that is an `RFC-` + `RL-` of their own. This record does not require it.

### DP-2 — option (b): each charter points at §1.6 and restates none of it; the per-role view is the corrected matrix

1. **The form.** Each of the seven charters replaces its restatement of §1.6 rows (for example
   `decision-maker.md:19-34`, "Concretely, per `document-ids.md` §1.6: …") with one fixed
   pointer line naming §1.6 as the authority for the families it writes. **The line, exactly,
   as its own paragraph:**

   > `**Document families.** This role writes only the families that docs/process/document-ids.md §1.6 gives it; this file restates none of them.`

   (The text between the backticks is the whole line, with the markdown bold as shown.) It
   is the same in all seven charters, and it is what DP-2.4's check reads. The charter keeps everything
   §1.6 does not say: tools, "never" rules, effort. The reporter's and the watcher's charters
   keep their declared empty rows. Each charter edit is a maintainer MERGE-ACK naming the file
   (PL-1277 DP-4 (a)).
2. **Why not (c).** Once the exact owner table exists, §1.6's **Owner** side is
   machine-readable. The objection that "§1.6's cells cannot be parsed" no longer stands
   against (c) *(re-argued after auditor-docs' audit of `561e329d`)*. What remains is the
   **charter** side. (c) needs a machine-readable grant in each charter, and none exists.
   - **The only candidate is the prepared record's fixed `Writes:` line**, naming the
     families. It was not adopted, for three reasons:
     - it is a copy of the role's §1.6 rows in seven files, the restatement (b) exists to
       remove (RFC-756);
     - nothing consumes it. The README line of DP-3 is check 35's runtime input, whereas a
       charter `Writes:` line would be read only to be compared with its own source, which
       proves the copy and not the binding;
     - it would not catch the failure (c) is aimed at. An over-grant is written in a
       charter's **prose** (a "never" rule loosened, a duty added), not in a line that
       declares itself a grant. A `Writes:` check passes a charter whose prose grants more.
   - **FD-1161's own case is a plan's Roles table** granting tasks. A task's family is
     readable only from its prose file line, so neither (c) nor a `Writes:` line reads it.
3. **What catches FD-1161's harm instead** (a record written by a role §1.6 does not
   permit):
   - **At the record, mechanically:** check 35's second clause, made non-vacuous by DP-3,
     refuses an owner outside the directory's list at the gate. It is family-level. So it
     would refuse an executor-owned closure, which was FD-1161's case, but not a lead-owned
     `kind: work` closure. Kind-level precision is not ruled here (item 7).
   - **At plan activation, by reading:** FD-1161 asked whether the planner's charter needs
     *"check the Roles table against §1.6 before activation"*. It does. WK-1169 Slice 2 adds
     that line to `planner.md`, under maintainer MERGE-ACK. This is a charter content item
     already in WK-1169's scope.
4. **The binding check, and the over-grant sweep.**
   - **Mechanical:** Slice 3 adds a check that each of the seven charters carries DP-2.1's
     line exactly once, shown red on a charter fixture without it.
   - **By reading — a new `close-workstream` step, which WK-1169 Slice 2 writes.**
     - **When:** at every Work close, **and at every phase close**. The phase close covers
       standing work that never closes. WK-1178 is `active` maintenance and amended
       `planner.md` and `lead.md` in #926, and a per-Work sweep would never read those edits.
       *(Added on auditor-docs' F-6.)*
     - **Over what:** each file under `.claude/roles/` changed **since the last sweep**. Each
       sweep records its end commit in the closure record that carries it, and the next sweep
       starts there: `git diff --name-only <last-swept>..<head> -- .claude/roles`. The first
       sweep starts at this record's tree.
     - **What is read:** every changed line that has the role write, create, amend, decide or
       close something.
     - **Against what:** **§1.6's cells, read directly, until WK-1169 Slice 3's exact owner
       table lands, then that table** (`ownership_matrix()` over it), and §1.6's other four
       columns throughout. Before Slice 3, `ownership_matrix()` is still the name-matching one
       of item A. It would accept an over-grant such as "the planner opens a Work", so the
       step must not name it as its reference until then. *(Corrected on auditor-docs'
       F-7.)*
     - **Outcome:** a grant §1.6 does not give that role is filed as an `FD-`.
   - The sweep is reading-based and is stated as such. **A mechanical check is not viable**,
     for the reason in item 2: an over-grant is prose, with no syntax a check could read.
     *(Corrected after auditor-docs' audit of `561e329d`. This item said that `RL-9853` item
     3's sweep reads charters. It does not: that sweep is per §1.2 transition, and a charter
     is not a §1.2 family.)*
5. **The per-role view** is `ownership_matrix()` over the exact table. The over-inclusions of
   item A disappear, and Slice 3's drift check is its proof.
6. **`delivery-process.core.json`'s `roles.authority`** is per process action, not per
   family. It is **out of this binding's scope** and is not reconciled with it here.
7. **Not ruled:** a kind-level owner check (for example, CR `work` only by the auditor). It
   needs check 35 to read a record's `kind:` against the exact table's per-kind rows. If
   wanted, it is proposed as an `FD-` against check 35.

### DP-3 — the line is hand-written role names, equal by check to the exact table; navigation files are outside the second clause; five named records are exempt

1. **What the line says.** Each of the ten `docs/*/README.md` files carries `Permitted
   owners:` followed by the **role names** (comma-separated, as check 35 parses them) in the
   union of the exact table's owner tuples over the kinds that directory holds. It never
   copies a prose cell verbatim. Derived by this record from §1.6's Owner cells at
   `eeda8f4b`, by reading each cell's owner clause, not by name-matching:

   | Directory | Permitted owners |
   |---|---|
   | `docs/adrs` | decision-maker |
   | `docs/closures` | auditor, lead |
   | `docs/contracts` | executor |
   | `docs/findings` | auditor |
   | `docs/ledgers` | executor |
   | `docs/plans` | planner, auditor, executor |
   | `docs/research` | executor, auditor |
   | `docs/rfcs` | maintainer |
   | `docs/rulings` | decision-maker, maintainer |
   | `docs/workflows` | decision-maker |

   Slice 3's exact table must reproduce this table. A disagreement is a finding against one
   or the other, never a silent pick.
2. **Hand-written, held equal by a check — not generated.** A README stays a living document
   (`document-ids.md:55`). Slice 3's check compares each README's line with the exact table's
   union, and fails on any difference. This departs from both the planner's (a) (verbatim
   prose, which cannot parse) and the prepared (c) (generation into README). The line is one
   short list, and the check is the single source's enforcement.
3. **Navigation files are outside the second clause.** A directory's `README.md` and
   `INDEX.md` are Reference documents (`document-ids.md:55`), not records of the directory's
   family. Check 35's second clause stops applying the family list to them. They remain
   subject to the first clause (a valid role or `maintainer`). Without this, every README
   fails the line it carries (item B).
4. **Five records are exempt, by name, not by date.** A closed, named exemption in check 35
   lists exactly `FD-1067`, `FD-1068`, `FD-1069`, `FD-1074` and `FD-1079`, with a comment
   citing this record. **`CR-1063` is not on it.** It passes the family-level line, since the
   lead is a closures owner, so it needs no exemption, and a list entry that changes nothing
   could not be tested. *(Corrected after auditor-docs' audit of `561e329d`, which also
   computed independently that exactly these five, and no other record, fail the ruled lines
   without an exemption.)* The exemption's test has two limbs:
   - **per entry:** each of the five exists, and fails the second clause when the exemption
     is removed;
   - **pinned:** the test holds the five ids as a literal, and fails on any exemption entry
     not in that literal. The list can therefore only shrink. A new lead-owned finding that
     would also fail passes limb 1, but it fails limb 2 unless the literal, and so this
     ruling, is changed.

   A `created:` cutoff (the prepared option (i)) is rejected. It exempts any record whose
   author writes an earlier date, and `created:` is author-written. Adding each owner to the
   list (option (ii)) widens §1.6 by the back door.
5. **All six of item C are filed.** WK-1169 Slice 1's audit record files them as **one
   `FD-`**, which its scope already covers ("every role charged with something its charter
   does not name"). The five findings are recorded as exempt by item 4. `CR-1063` is recorded
   as the one known kind-level case, the starting set for item 7's check if one is built.
   The disposition proposed is `accept`, because `owner:` is immutable on these records
   (check 34).
6. **Ordering — no line before its exemptions.** Check 35 enforces a line the moment it
   exists. So **no `Permitted owners:` line lands before item 3's scoping and item 4's
   exemption are in check 35.** Those are code, and PL-1277 has Slice 2 docs-only with Slice 3
   as the code slice. The planner either moves the ten lines into Slice 3, or moves those two
   code changes into Slice 2. Either satisfies this ruling; the cut is the planner's.

## What it obliges

- **This commit:** this record only.
- **PL-1277 (the planner's file, not edited here):**
  - the "Resolved by" cells of DP-2 and DP-3 cite this record once it is minted;
  - Task 3's charter-grant check becomes item DP-2.4's pointer check;
  - the exact owner table and its drift check are added to Task 3;
  - DP-3.6's ordering constraint is applied in the cut.
- **WK-1169 Slice 1:** the one `FD-` of DP-3.5. The transcription check by hand, already in
  its scope, records item A's over-inclusions.
- **WK-1169 Slice 2:** DP-2.1's pointer line in each charter (maintainer MERGE-ACK per file),
  DP-2.3's `planner.md` line, DP-2.4's over-grant sweep step in `close-workstream`, and the
  ten README lines, subject to DP-3.6.
- **WK-1169 Slice 3:** the exact owner table and its drift check, `ownership_matrix()` over it,
  DP-2.4's pointer check, DP-3.2's equality check, DP-3.3's navigation-file scoping, and
  DP-3.4's named exemption.

## Acceptance — the violation that must become detectable

Each is shown failing on deliberately broken input (`CLAUDE.md` §13):
- A §1.6 Owner cell that names a role in neither of the exact table's tuples for its row fails
  the drift check. So does a tuple role that the cell no longer names.
- `ownership_matrix()` no longer lists the planner under `work (WK)` or the lead under
  `proposal (RFC)` or `reference: skills`.
- A README whose `Permitted owners:` line differs from the exact table's union fails the
  equality check.
- A record created after this ruling, in any of the ten directories, whose `owner:` is outside
  its directory's line fails check 35. A scratch copy of a real record with a wrong owner is
  shown red. A README or `INDEX.md` with `owner: lead` passes.
- For each of the five: removing its name from the exemption makes that record fail the second
  clause.
- Adding any name not in the test's pinned literal fails the exemption's test. A planted new
  lead-owned finding shows this: it would fail without an exemption, so limb 1 alone would
  pass it.
- A charter fixture without DP-2.1's line, or with it twice, fails the pointer check.
- The over-grant sweep (by reading, WK-1169 Slice 2): a scratch copy of a charter with a
  **planted over-grant that only §1.6 catches** is put through the sweep's procedure, and the
  sweep reports it. The plant is **"the planner opens a Work"** in `planner.md`: the
  name-matching `ownership_matrix()` of item A lists the planner under `work (WK)` and would
  accept it, while §1.6's WK row gives opening to the maintainer (`document-ids.md:153`).
  The result is recorded in the slice's evidence. *(The earlier plant, "the executor writes
  the Work's closure record", was replaced on auditor-docs' F-7. Even the over-inclusive
  matrix catches that one, so it could not show the reference is sound.)*
