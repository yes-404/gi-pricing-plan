---
id: RL-1138
family: ruling
title: W37-10 DP-1 to DP-6 — the audit tree splits with W37-11, its findings README folds, and the rituals land as implementation
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-26
owner: decision-maker
tree: 4ed1f88ee89deeddca04565cc1f07cdbaf02dba4
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1073, PL-1071, RL-1046, RL-1048, RL-940, RFC-937, CR-1064]
---

# RL-1138 — W37-10 DP-1 to DP-6: the audit tree splits with W37-11, its findings README folds, and the rituals land as implementation

## Verified first, at 4ed1f88ee89deeddca04565cc1f07cdbaf02dba4

This rules the six decision points in `PL-1073` §4 (`:268-273`). The planner's
recommendation in each row is a proposal; each is ruled on its own merits below.

Everything below was read in worktree `dm-w37-10`, branch `w37-10-dp-rulings`, cut from
`origin/main` = `4ed1f88ee89deeddca04565cc1f07cdbaf02dba4` with a clean status. Clock at
ruling: 2026-09-26, about 17:50 BST. `git diff --stat 9f887b6 4ed1f88 -- 'docs/plans/PL-01073*'`
is empty, so the plan is the one filed at its own `tree: d63f765`. Where a count is given, its
tree and its command are given beside it. Where the plan's figure did not reproduce, that is
said and the measured figure is used instead.

**Retired paths are described, not spelled, in this record.** The audit tree is the
directory `RFC-937` §1.4 dissolves; its two remaining files are called "the findings README"
and "`w37-11-record.md`". Spelling the path would add a fatal check-36 hit to a shared,
pooled count.

### 1. Facts re-measured at `4ed1f88`

| Plan's claim (at `d63f765`) | Command | At `4ed1f88` |
|---|---|---|
| DP-1: the audit tree holds 2 tracked files | `git ls-files <audit tree> \| wc -l` | **2** — the findings README and `w37-11-record.md`. Reproduces. |
| DP-1: `W37_11_RECORD_PATH` defined at `scripts/_docid.py:259`, re-exported at `scripts/_docverify.py:3960`, exempted at `scripts/audit-docs.py:1369` | `grep -n W37_11_RECORD_PATH scripts/_docid.py scripts/_docverify.py scripts/audit-docs.py` | All three reproduce at the same lines. **The plan's list is incomplete:** `scripts/doc-id.py:665` also reads it (`if rel == _docid.W37_11_RECORD_PATH:`). |
| DP-1: four test modules read it | `grep -rln 'W37_11_RECORD_PATH\|w37-11-record' tests` | **4** — `test_doc_id.py`, `test_doc_id_verify.py`, `test_audit_docs_ids.py`, `test_findings_ids.py`. Reproduces. |
| DP-1: the record was created after the migration by `ea3704d` (#756) | `git log --diff-filter=A --format='%h %aI %s' -- <the record>` | `ea3704dd 2026-09-05T20:04:36+01:00 feat(scripts): W37-11 residue ceiling … (#756)`. Reproduces. |
| DP-1: the review-13 boundary at `CR-1064:373-379` | read | The check-35 owner-literal paragraph runs `:373-378` at `4ed1f88` (*"aligning it is a code edit in a slice that does not exist yet"*). Reproduces. |
| §7.1 note 2: "220 references remain, 74 files' worth" | the plan does not state its predicate | **Does not reproduce** with `git grep -c '<audit tree path with trailing slash>' <tree>`: **188 files / 1065 lines** at `4ed1f88`, **182 / 1053** at `d63f765`; restricted to `-- docs`, **160 / 752** at `4ed1f88`. The plan's figure is not used below. |
| DP-2: the findings README is cited by `.claude/roles/auditor.md` | `grep -n` for the findings README path in that file | `:33` (the essay path pattern) and `:35` (the README itself). Reproduces. |
| DP-2: "5 frozen `FD-` essays" cite it | `git grep -l 'audit/findings/README' <tree> -- 'docs/findings/FD-*'` | **4** at both `d63f765` and `4ed1f88`: `FD-934`, `FD-935`, `FD-936`, `FD-954`. **Does not reproduce.** The plan's predicate is not stated. Non-`FD` citers at `4ed1f88`: `CR-1065`, `PL-965`, `RS-1003`, `RL-913`, `RL-948`, `RL-970`, `RL-972`, `w37-11-record.md` and the file-census CSV. |
| DP-2: the precedent redirect | read `docs/REDIRECTS.csv` | `:3` redirects the audit tree's top-level README to `docs/findings/README.md`, with empty id cells. |
| DP-2: the destination's residue governance | `grep -n '^\| docs/findings/README.md' w37-11-record.md` | **no row.** The retiring file has one: `w37-11-record.md:479`, class `h1-check36`, count 4. |
| DP-3: `register-lint.py` and `register-owed.py` exist and run | `python3 scripts/register-lint.py; echo $?` and `register-owed.py --help` | lint exits **0** (`OK (0 violations)`); `register-owed.py` takes one positional `target`, *"a work-item id, a phase id, or the literal 'review'"*. |
| DP-4: `grep -c 'SL-[0-9]' docs/roadmap.md` = 0; `grep -rn '^slice:' docs/plans/ \| wc -l` = 0 | same | **0** and **0**. Reproduces. |
| DP-4: the guard at `scripts/doc-id.py:7373`, the resolve check at `:7376` | `sed -n '7370,7380p'` at both trees | The guard `if header.slice_ is not None:` is at **`:7374`** at both `d63f765` and `4ed1f88`; `:7373` is the enclosing `for`. The resolve check is at `:7376`. Off by one; the substance holds. |
| DP-4: `document-ids.md:148` | read | The `SL` row: *"planner, cut in the map plan (`draft`) \| lead dispatches (`active`)"*. Reproduces. |
| DP-5: §13 carries the reporter; §10 lists the roadmap; §§ are cited by the core extract | `grep -n '^## ' docs/process/delivery-process.md`; `grep -o '"§[0-9.]*' docs/process/delivery-process.core.json` | §13 is *"Monitoring & comms loop (watcher / reporter / lead)"* (`:278`); §10 *"Required artifacts"* names the roadmap at `:209`. The extract cites §2–§9, §6.4, §13, §15. Check 27 holds `meta.derived_from_digest` (sha256 of the spec's bytes). Reproduces. |
| DP-5: the spec's own residue ceilings | `grep -n '^\| docs/process/delivery-process.md' w37-11-record.md` | four rows: `h1-check30` 1 (`:247`), `h1-check32` 3 (`:287`), `h1-check35` 1 (`:360`), `h1-check36` 2 (`:548`). |
| DP-6: RFC-937 §6 and `document-ids.md` §1.10 state the rituals; `RL-940` §4 is the acceptance | read | RFC-937 §6 at `:429-431`; `document-ids.md` §1.10 at `:210`; `RL-940` §4 at `:126-133`. RFC-937's header now reads `status: active`, the post-migration word for the `accepted` status that `RL-940` §4 ruled to be its acceptance line. |
| DP-6: the deputy's statement and the delegation | read `~/gi-pricing-plan.local/channel/to-lead.md` (local handover file, not in the repository) | `:6074` — the maintainer's delegation to the deputy, 2026-09-26 17:02:52 BST, quoted verbatim there as *"plz make decision on behalf of me from your best"*. `:6180` — the deputy, 17:44:51 BST: *"DP-6 (A) with its stated limit is consistent with the delegation of 17:02:52 and needs no maintainer line."* |

## Ruled

### DP-1 — the audit tree: **(A) adopted, amended**

**W37-10 retires only the findings README. `w37-11-record.md`, the `W37_11_RECORD_PATH`
constant and every reader of it stay where they are and move with W37-11**, which owns the
instrument.

(B) is refused on the grounds the plan gives, and they are stronger than it states. The
record is read at runtime by the gate that must stay green through the edit. At `4ed1f88`
that gate has **five** script readers, not the three the plan names — `scripts/doc-id.py:665`
is the fifth call site — and four test modules. W37-10's executor skill is `docs-audit`; its
scope has no code. Review 13 drew this same boundary for a smaller case (`CR-1064:373-378`).
(C) is refused: the findings README has no other owner, so deferring it abandons a row.

**Amendments:**

1. **The carrier is W37-11, named.** Under (A), `PL-1073` Acceptance Standard item 6 reads
   **1**, not 0.
2. **The reference limb goes with the file.** §7.1's clause also asks that nothing reference
   the directory. The constant is itself such a reference and cannot go before the file.
   So the reference limb has the same carrier. **The plan's 220 / 74 figure is not
   adopted,** because it did not reproduce (§1). W37-11 re-measures with a stated predicate
   when it moves the file.
3. **This rules the scope only.** It says which slice owns the file. Which of `CLAUDE.md`
   §13's four verdicts the W37-10 close records is still the lead's decision. "Reassigned,
   to W37-11" is the verdict this scope supports.

### DP-2 — the findings README: **(A) adopted, with four binding conditions**

Fold its live content into `docs/findings/README.md`, delete it, and add a
`docs/REDIRECTS.csv` row of the same shape as `:3` (empty id cells, old path, new path).
(B) keeps a file in a directory RFC-937 §1.4 dissolves. (C) would leave the frozen `FD-`
essays' citations with nowhere to resolve. `RL-1048` §1(d) and its §4 table give the
principle: a cited file is placed, not just removed.

**Correction:** the plan says 5 frozen `FD-` essays; the measured count is **4** (§1).
Nothing in the ruling turns on the difference.

**Conditions:**

1. **The fold brings no legacy-form hit.** `docs/findings/README.md` has no row in
   `w37-11-record.md` at `4ed1f88`. The retiring file has four `h1-check36` hits. If any of
   them reaches the destination, `check_residue_ceiling` (`scripts/_docid.py`, by symbol)
   reports a fatal `RESIDUE_REGRESSION` for *"a file the W37-11 record does not name"*.
   Retired paths and legacy ids are described in the folded text, not spelled.
2. **W37-10 does not edit `w37-11-record.md`.** When the file is deleted, its `:479` row
   (ceiling 4) measures zero. That is the non-fatal `RESIDUE_PROGRESSED` outcome, and a
   shrink is never a failure (same function's docstring). The shrink belongs to the
   record's owner — W37-11 and the deputy (DP-1) — not to this slice.
3. **W37-10 may not change `.claude/roles/auditor.md` at all.** That file is `PL-1071`'s
   row 1 (task T7) — W37-8's. Its `:33` and `:35` are code-span path mentions, not links,
   so deleting the README does not break check 1, and the charter's check-36 count (ceiling
   3, `w37-11-record.md:469`) does not move. What W37-10 **must** do: tell the lead in the
   task's report that `:35` now names a retired file, that `docs/findings/README.md` is its
   destination, and that the new `REDIRECTS.csv` row is the interim resolution until W37-8
   rewrites the charter. Recording the rewrite in `PL-1071` is the planner's job, routed
   through the lead.
4. **Line-anchored citations stay resolvable.** `FD-935:23`, `FD-936:24` and `FD-954:24`
   cite the retiring file by line range. A redirect maps a path, not a line. The commit that
   deletes the file names, in its body, the last tree at which the file existed, so that
   `git show <tree>:<path>` still resolves those ranges. The frozen essays are not edited.

### DP-3 — a register-currency line: **(A) adopted, amended**

Both checklists gain the line, written as a command. Review 13's diagnosis (`CR-1064:390`:
*"schedule goes stale by default"*) is that an unscheduled reminder is the failure itself,
so a command is the right form. Both instruments run at `4ed1f88` (§1).

**Amendment:** the target in the `register-owed.py` argument depends on the checklist.
`work-item-close.md` passes the `WK-` id being closed. `phase-close.md` passes the phase id.
`<id>` in Task 4 step 4 is filled that way. The script accepts nothing else, apart from the
literal `review`.

### DP-4 — no `slice:` field: **(A) adopted, citation corrected**

Omit `slice:` and cite the slice in prose. The guard is at **`scripts/doc-id.py:7374`**
(the plan says `:7373`; §1). With the guard there, omitting the field is clean, and a
`slice:` value with no `SL-` row fails at `:7376`. There are no `SL-` rows (0 in the
roadmap, 0 `slice:` fields in the plans), so (B) would block on something no one in this
slice's path can create now.

**Two limits:**

1. Task 8b's `SL-` rows are a **proposal the lead applies** (`PL-1073:116`; the roadmap is
   the lead's file). This ruling does not adopt their content.
2. Any id Task 8b uses comes from `python3 scripts/doc-id.py next` at the time of filing,
   with its base and range recorded (the plan's Risk 4). Until `SL-` rows exist on `main`,
   branches keep the `<type>/<short-slug>` form (`git-hygiene`, *"The slice grammar"*).

### DP-5 — where rituals (a) and (b) land: **(A) adopted, with binding constraints**

Ritual (a) goes in §13, next to the reporter mechanism that performs it. Ritual (b) goes in
§10 (required artifacts), plus one sentence in §5. (B) is refused: a new rituals section
would copy `document-ids.md` §1.10, the second-copy failure that `RFC-756` records.

**Constraints on the executor:**

1. **No renumbering.** The core extract cites §§ by number.
2. **Regenerate the core extract's digest in the same commit.** Check 27 compares
   `meta.derived_from_digest` against the spec's bytes.
3. **No new legacy-form hit in `delivery-process.md`.** Its four W37-11 ceilings are at
   their measured counts (§1), so one more hit in a governed class is a fatal regression.

### DP-6 — maintainer acceptance line: **(A) adopted, with its limit binding**

The ritual edits to `delivery-process.md` need no dated maintainer line. RFC-937 §6 adopted
the rituals. The maintainer ruled RFC-937's filed status to be its acceptance line
(`RL-940` §4). So writing §6 into the artifact that enforces it is implementation, not an
amendment. The deputy states that (A) with its limit is consistent with the maintainer's
delegation of 2026-09-26 17:02:52 BST and needs no maintainer line (`to-lead.md:6180`,
17:44:51 BST; the delegation is at `:6074`). This ruling relies on that statement and does
not substitute for it. `CLAUDE.md` §12 reserves amendments to **`CLAUDE.md`** for the
maintainer. No task in `PL-1073` lists `CLAUDE.md` among its files (`grep -n
'^\*\*Files:\*\*'` over the plan: seven tasks, none of them `CLAUDE.md`).

**The limit is binding, not advisory.** An executor who finds it must write an obligation
that neither RFC-937 §6 nor `document-ids.md` §1.10 states stops and reports to the lead.
That text is an amendment and is outside this ruling.

## What it obliges

- **The planner** writes `RL-1138` into all six `Resolved by` cells of `PL-1073` §4 and
  moves the plan to `active`, in a later commit on this branch (`document-ids.md`, `PL`
  row: the decision-maker never edits the plan). The planner also adds DP-3's argument
  amendment and DP-4's line correction if Task 4 or DP-4's text is to carry them.
- **The executor** follows DP-2's four conditions and DP-5's three constraints. It edits no
  file under `scripts/` or `tests/`, does not edit `w37-11-record.md`, and does not edit
  `.claude/roles/auditor.md`.
- **The lead** passes W37-8 the notice about `auditor.md:35` (DP-2 condition 3) and
  records the DP-1 verdict at the W37-10 close.
- **A disclosure, not ruled here — the lead's and the planner's.** `RL-1046` §B labels the
  count of three check classes `owner: W37-10`: check 29 (§5.2's register merge), check 30
  and check 35. At `4ed1f88`, `register-lint.py` still prints *"residue class 2 — 11 of 20
  phase-1b row(s) … fail a grammar rule (RL-1046 check 29, owner W37-10)"*. `grep -n 'check
  29\|phase-1b\|RL-1046'` over `PL-1073` returns nothing. **No scope row in the plan claims
  or reassigns that class.** Check 35's owner literal is covered separately by R-3. That
  gap is outside DP-1 to DP-6. It is reported here because a W37-10 close measured
  against the plan alone would say nothing about it.

## Acceptance — the violation that must become detectable

- **DP-1 / DP-2:** at the W37-10 merge tree, `git ls-files <audit tree> | wc -l` returns 1,
  and that file is `w37-11-record.md`. *Violation:* 0 (the record moved inside a docs-only
  slice) or 2 (the findings README was not retired). A `git diff --stat
  origin/main...<branch> -- scripts tests` that is not empty is also a violation of DP-1.
- **DP-2 condition 1:** `python3 scripts/audit-docs.py` exits 0 and prints no
  `RESIDUE_REGRESSION` for `docs/findings/README.md`. This is already enforced by a
  shipped check. It fires on the defect class by construction of `check_residue_ceiling`
  (a hit in an unnamed file, for a governed class, is fatal). This ruling did not run a
  broken-input proof of it, and says so.
- **DP-2 condition 3:** `git diff --stat origin/main...<branch> -- .claude/roles/auditor.md`
  is empty.
- **DP-5:** check 27 green at the merge tree. No script checks the no-renumbering
  constraint; the reviewer compares the `^## ` heading list before and after.
- **DP-6:** no mechanical check exists or is added. The limit is enforced when the lead
  reviews each process-spec diff against RFC-937 §6 and §1.10.
