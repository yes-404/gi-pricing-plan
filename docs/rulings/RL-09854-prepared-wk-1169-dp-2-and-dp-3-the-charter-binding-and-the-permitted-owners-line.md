---
id: RL-9854
family: ruling
title: PREPARED, NOT RULED — WK-1169 map plan DP-2 and DP-3, the charter binding and the `Permitted owners:` line
status: draft                  # PREPARED, NOT RULED — see the banner; RL's §1.2 subset has no draft (reported to the lead)
created: 2026-09-30
owner: decision-maker
tree: aa14e90dd77c7461aa35cc6461557b129959463f
phase: P2
work: WK-1169
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [WK-1170, FD-1161]
---

# RL-9854 (working id) — PREPARED, NOT RULED: WK-1169 DP-2 and DP-3

> **Nothing in this record is ruled.** It was prepared at medium effort, under the
> maintainer's decision by delegation (lead channel, 2026-09-30 00:42 BST). It carries
> evidence, options and **provisional** recommendations only. Do not rely on it. No slice
> may activate on it, the plan's rows are not resolved by it, and no charter, README, check
> or `docs/process/` file is amended by it. The ruling is a later pass at effort high.

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

**Provisional: (c), as the planner recommends, with three things the ruling must add.**
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

**Provisional: (c). This departs from the planner's (a).** The planner's two reasons for (a)
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

**Nothing.** This section is held for the high-effort pass.

## What it obliges

**Nothing yet.** Under the provisional answers, it would oblige:
- a grant syntax and a check in Slice 3;
- charter restatements struck, by maintainer MERGE-ACK;
- a generated `Permitted owners:` block in the `docs/*/README.md` files, in Slice 2;
- a dated exemption rule for existing records, written into check 35's docstring and
  `document-ids.md` §1.11 through the `process/` route (RFC- + RL-).

## Acceptance — the violation that must become detectable

**Not set, because nothing is ruled.** Under the provisional answers:
- A charter fixture granting a family §1.6 does not give that role fails the new check.
- A record created after the cutoff whose `owner:` is outside its directory's generated line
  fails check 35.

Both must be shown failing on deliberately broken input.
