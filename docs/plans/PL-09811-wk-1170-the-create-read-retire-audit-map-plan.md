---
id: PL-9811
family: plan
kind: map
title: WK-1170 — The create-read-retire audit (RFC-937's transition steps, RFC-897 Stage 4, and the instrument rows carried to it): map plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-29
owner: planner
tree: 19c395acad594d1b193da197461bec85201d2248
phase: P2
work: WK-1170
supersedes: []
superseded_by: ~
corrected_by: []
relates: [CR-1164, CR-1167, CR-1183, CR-1212, RFC-937, RFC-897, RL-943, RS-952, FD-1166, FD-1165]
---

# WK-1170 — The create-read-retire audit: map plan

> **For agentic workers:** this is a **map plan**. It cuts WK-1170 into six slices and fixes their scope, order, dependencies and gates. It carries no code steps. Each slice gets its own leaf plan (`kind: leaf`) before it starts, and the executor works from that leaf plan. REQUIRED SUB-SKILL for each leaf plan's executor: subagent-driven-development (recommended) or executing-plans. Slices 1 and 2 also bind `docs-audit` and `spec-change` (they write only under `docs/` and `.claude/`); Slices 3–6 also bind `python-test` (broken-input proofs), `code-quality`, `dev-commands` (the gate) and `docs-audit`; Slice 6 also binds `contract-guard`. Every executor reads `docs/plans/README.md`'s five unchecked conventions before its first step.

## Goal

Give every transition in the state machines of `document-ids.md` §1.2 and §1.2a a named process
step that performs it, and prove the instruments that hold those transitions honest. Concretely:

- **The audit.** For every family, and every `kind:` where §1.2 splits one, name the step that
  **creates** a record, the step that **reads** it, and the step that moves it to each terminal
  status. Give each family one of RFC-897 §6's four verdicts (looped, write-only, read-only-in,
  terminal-by-design). Decompose the unreferenced population into verdict 2 and verdict 4
  (RFC-897 §11 (d)).
- **The steps.** Write each missing step into the skill, charter or process file that owns it.
- **The instruments.** Discharge the thirty open register rows, and the three non-register items,
  that `CR-1164` §10, `CR-1167` and `CR-1212` route to this Work. Most are defects in
  `audit-docs.py`, `doc-id.py`, `_docverify.py`, `register-owed.py`, `register-lint.py` and
  `doc-index.py`.

The Work is done when the Acceptance Standard below holds at the last slice's merge tree.

**Architecture.** A map plan, per `docs/process/delivery-process.md` §5 step 2, in the form of
`PL-1254` (WK-1250's map plan). The Work's subject is WK-1170's roadmap section
(`docs/roadmap.md:816-830` at `19c395ac`): *"the process step for each transition in the state
machines of `document-ids.md` section 1.2, and the register, instrument and verify tooling those
transitions depend on"*, plus its dated 2026-09-28 line carrying RFC-897 §6. RFC-937 names the
Work in §8's closing sentence: *"the create-read-retire audit (the process step per transition in
§1.2's state machines)"*.

**A relay correction, recorded so no reader inherits it.** The brief for this plan cited
"RFC-937 §6" as the section the roadmap row names. RFC-937 §6 is "Rituals adopted". The row's
section is **RFC-897 §6** (Stage 4, the workflow-loop audit), and RFC-937's section is §8. This
plan argues from those two.

**Tech Stack.** Python 3.12 scripts under `scripts/` and their tests under `tests/`; Markdown and
YAML front matter under `docs/` and `.claude/`. **No new dependency is planned.**

**Spec.** The executors read these with their leaf plans:
- [`../process/document-ids.md`](../process/document-ids.md): §1.2 (the family table, `:38-56`),
  §1.2a (the status vocabulary, `:57-72`), §1.6 (roles per family, `:144-174`), §1.7 (the
  `execution` column and the Decision points form, `:175-196`), §1.9 (`:201-215`), §1.11
  (checks 30–39, `:220-236`).
- [`../rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md`](../rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md):
  §6 (Stage 4, `:170-186`), §8 (its dependency line, `:197-214`), §11 (d) and (a) (`:249-262`).
- [`../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md):
  §8 (`:439-441`), §9's last row (`:443-455`).
- [`../closures/CR-01164-wk-697-work-close-the-closure-record.md`](../closures/CR-01164-wk-697-work-close-the-closure-record.md)
  §2, §5, §8 and §10; [`../closures/CR-01183-wk-695-work-close-file-taxonomy-reference-coding-and-custody.md`](../closures/CR-01183-wk-695-work-close-file-taxonomy-reference-coding-and-custody.md)
  (the Stage 4 and census transfers, `:75`, `:81`, `:149-154`, `:169-170`, `:193`);
  [`../closures/CR-01212-plan-review-15-p2-exit-criteria-budget-sequencing-and-the-open-finding-set.md`](../closures/CR-01212-plan-review-15-p2-exit-criteria-budget-sequencing-and-the-open-finding-set.md)
  Proposals 2, 8, 11 and 13.
- [`../findings/register.md`](../findings/register.md): every row the Scope table lists.

## Acceptance Standard

These conditions are for the Work as a whole. Each leaf plan states its own conditions for its
slice. Every command runs on a detached copy of the named tree (`git worktree add --detach`),
never on a working tree.

1. **Every transition has a step.** The Slice 1 audit record (`RS-`, `kind: audit`) carries one
   row per family × transition from §1.2's "Status subset" column and §1.2a's forward-only rule,
   split by `kind:` where §1.2 lists kinds. Each row names the step that performs the transition
   (a skill section, a charter line, a script function or a check number, each with its path) or
   an `FD-` filed for the gap. At the last slice's merge tree, no row names a gap whose `FD-` is
   still open without a resolution in `docs/findings/register.md`.
2. **Every family has a verdict.** The same record gives each family one of RFC-897 §6's four
   verdicts, with its evidence. Verdicts 2 and 3 each carry an `FD-`.
3. **The unreferenced population is decomposed** (RFC-897 §11 (d); `CR-1183:84`). The population
   is check 38's: `python3 scripts/audit-docs.py 2>&1 | grep '^  check 38:'` prints *"161
   PL-/RS-/RFC- document(s) in scope"* at `19c395ac`. Slice 1 re-derives it at its own tree. Every
   member cited by nothing outside `docs/INDEX.md` carries a verdict-2 `FD-` or a declared
   verdict 4, and verdict 4 is derived from a covering `CR-` wherever one exists (RL-943).
4. **The close-tree census is committed** (`CR-1183:81`, §11 (a)'s second half): the output of
   `scripts/file-census.py`, run at the last slice's merge tree, is committed under
   `docs/research/` with the tree in its filename, as `file-census-5ef559d.csv` was.
5. **Check 38 runs its four sub-clauses.** At `19c395ac` it prints that they *"are not implemented
   yet"*. After Slice 3, each sub-clause is proven on a deliberately broken fixture that makes it
   print its warning, and on a clean fixture that makes it print none.
6. **Every carried register row is resolved.** The predicate, runnable at any tree:
   `awk -F'|' 'NF>2 && tolower($(NF-1)) ~ /create-read-retire|wk-1170/' docs/findings/register.md`
   (the Decision column only). At `19c395ac` it prints **32** rows, of which FD-1175 and FD-1181
   already open with "Resolved". At the Work close every row it prints opens with a resolution
   marker `scripts/register-lint.py` accepts, citing a PR or the lead's dated disposition.
7. **The owed-list generator finds this Work's rows by its id.** At `19c395ac`,
   `python3 scripts/register-owed.py WK-1170` prints *"(none)"*, because the cells name the Work
   by phrase, not by id. After Slice 1's register pass, the same command lists every open row
   the item 6 predicate prints, and at the close it lists none.
8. **Every tooling fix is proven on broken input.** Each fix in Slices 3–6 lands with a test that
   fails on the pre-fix code or on a deliberately broken fixture, and the leaf plan names that
   failure by its cause, not by an exit code alone.
9. **Every Decision point has its resolver before the slice it blocks starts**
   (`document-ids.md` §1.7).
10. **Every slice closes on its own clean audit** and its own item 11 (see **Tasks**).
11. **The gate passes on the merged tree of each code slice**, both halves (`CLAUDE.md` §11), and
    `python3 scripts/audit-docs.py`, `python3 scripts/doc-index.py --check` and
    `python3 scripts/doc-id.py check` exit 0 on the merged tree of each docs-only slice.

## Global Constraints

- **Do not build ahead of the phase** (`CLAUDE.md` §0). This Work is P2 governance tooling. It
  adds no product capability, except as DP-2 rules for FR-240's clauses (4)–(6).
- **A frozen record is corrected only as `document-ids.md` §1.5 and check 34 allow**: `status:`
  forward, `superseded_by:`, an append to `corrected_by:`. A frozen plan's error is corrected by a
  new `RL-` or `RFC-` (F114's own cell).
- **`docs/process/` is the maintainer's** (§1.6's `process/` row: *"amendments arrive as `RFC-` +
  `RL-`"*). A slice that amends `delivery-process.md` or `document-ids.md` carries that pair.
- **Charters are the maintainer's** (§1.6's charters row). A charter gap this Work finds is an
  `FD-` routed to WK-1169, never a charter edit here (see Sequencing).
- **One source, never a restated count** (`CLAUDE.md` §0, RFC-756). The audit record cites each
  step by path and line at its tree. It does not copy a skill's text.
- **A count carries its tree, its corpus and its predicate** (`CLAUDE.md` §13). Every count in a
  leaf plan or an audit record names all three.
- **A register write needs a committed tree.** `register-owed.py` refuses a dirty register
  (`_dirty_register`, RL-912 §1). Every register reading in this Work is taken at a commit.
- **Parallelism.** Under `delivery-process.md` §8 as amended by open PR #928 (the parallel-start
  ruling, working id 9760, head `074d7778`, not merged at `19c395ac`): preparation (plans, rulings, audits) is not a
  slice and runs alongside; at most two code slices from different Works run at once, each with a
  gate slot (`.claude/roles/executor.md:110`), and none shares files with the other. If #928 does
  not merge, §8 as it stands at `19c395ac` applies: one slice at a time.

---

## Scope

### The Work's own subject (no register row)

| Source | Obligation | Slice |
|---|---|---|
| RFC-937 §8, closing sentence; roadmap `### WK-1170` | The process step for each transition in §1.2's state machines | 1 (the audit), 2 (the steps) |
| RFC-897 §6 (Stage 4), carried by the roadmap's 2026-09-28 line and `CR-1183:75`, `:149`, `:169`, `:193` | The lifecycle triple and the four verdicts per family | 1 |
| RFC-897 §11 (d), `CR-1183:84`, `:154` | The unreferenced population decomposed into verdict 2 and verdict 4 | 1 |
| RFC-897 §11 (a) second half, `CR-1183:81`, `:151`, `:170` | The census committed at a close tree | 1 (the run), and the last slice (the close-tree run) |
| `CR-1212` Proposal 8 (FD-1190's class) | An audit-docs check that a record's `status:` is valid for its family at filing | 3 |
| `CR-1212` Proposal 11 | Check 2 scans fenced quotations: decide whether it skips fenced blocks, with a broken-input proof | 3 |
| `CR-1212` Proposal 13 | Plan-status staleness: an INDEX-derived check, no hand edit | 3 |
| `CR-1164` §10, C3 | Row (g): the standing FAIL at `classified-by-none=207`, with the LIMIT (45 files) | 5 |
| `CR-1164` §5, C15 | #757's 207 g2 per-file entries, derived and not filed | 5 |

### Carried register rows, each individually

Read at `19c395ac` with the item 6 predicate. "Instrument" names the file the fix lives in, as the
row's own cell states it.

| Row | Subject (short) | Instrument | Slice |
|---|---|---|---|
| FR-240 (F-W9-3), clauses (4)–(6) only | Constraints satisfiable; no `control`-intent factor in a rateable path; no unapproved custom objective reachable | `pricing-core` rating (see DP-2) | 6, subject to DP-2 |
| F27, clause (c) only | 03 rating shapes against their hand-authored contracts (`FD-934`) | `backend/tests/test_contracts.py` | 6 |
| F29 | Error codes across the spec/code boundary | `audit-docs.py` check 10 | 6 |
| F33, the part not moved to WK-1178 | mypy `files` coverage, the gate-coverage remainder | `pyproject.toml` `[tool.mypy]` | 6 |
| F78 | `_discover_roadmap`'s phase-spanning refusal has no fixture | `doc-id.py` | 5, subject to DP-5 |
| F86 | RL-909's decay rule has no faithful check (three limbs) | `register-lint.py` | 4 |
| F90 | Check 37 cannot see a `###`-level ruling heading | `audit-docs.py` | 3 |
| F92, the 18 non-vendored skill manifests | Deferred out of the Reference stamp set | `.claude/skills/*/SKILL.md` headers | 5, subject to DP-7 |
| F94 | The ruling-heading census predicate against the shipped splitter | `doc-id.py` | 5, subject to DP-5 |
| F96 | A ruling without `## Ruling N` migrates as `PL-` | `doc-id.py` | 5, subject to DP-5 |
| F100 | `_discover_findings`' docstring is false | `doc-id.py` | 5 |
| F101 | Row (i)'s limb 1 has no broken-input exit-code proof | `_docverify.py` | 5 |
| F103 | Checks 32 and 36's sentinel population cannot be told from a real per-file gap | `_docverify.py`, `audit-docs.py` | 5 |
| F106 | No ceiling on row (g)'s internal counts | `_docverify.py` | 5 |
| F107 | The literal idempotence proof was not run | `doc-id.py` | 5 (with FD-1152) |
| F108 | Check 35's output shape for a non-markdown file | `audit-docs.py` | 3 |
| F114 | Four frozen plans state row (d) in a superseded form | a correcting `RL-` (docs only) | 1 |
| FD-1149 | The migration sweep reaches files beneath a vendored manifest | `doc-id.py` | 5, subject to DP-5 |
| FD-1150 | A determinism test whose child aborts at interpreter shutdown | `packages/pricing-core/tests/test_rating_score.py` | 5, only if it recurs (its own cell) |
| FD-1152 | A second `migrate` is not idempotent; two classes do harm | `doc-id.py` | 5, subject to DP-5 |
| FD-1154 | `meta.verified_against_tree` carries two meanings | `delivery-process.core.json`, check 27, the verify workflow | 4, unless the next `delivery-process.md` amendment takes it first (its own cell) |
| FD-1155 | `doc-index.py --phase` matches `P1b` where the register writes `1b` | `doc-index.py` | 4 |
| FD-1158 | The reserved FD block; `next` cannot see an unmerged draft | `REDIRECTS.csv`, `doc-id.py next` | 4 |
| FD-1159 | Map item 11's broken-input proofs for checks 32, 36 and 38 | `tests/test_audit_docs_ids.py` and fixtures | 3 |
| FD-1160 | Four RFC-937 §5 H rows open on content; eighteen closed only by the migration commit | docs content read | 1 |
| FD-1163 | (a) `CR-1065` §8's audit scope; (b) check 39's false note; (c) §1.9's non-existent SL- lint | (a) docs; (b), (c) `audit-docs.py` | (a) 1; (b), (c) 3 |
| FD-1165 | `register-owed.py`'s selection predicates miss owed rows and admit disposed ones | `register-owed.py` | 4 |
| FD-1166 | Rows owned by the §14 review decay without a register change | `register-lint.py` | 4 |
| FD-1168 | Check 9 reads a time's minute field as a spec number | `audit-docs.py` | 3 |
| FD-1174 | `register-lint.py` never built RFC-896 P3's owner-existence and id-uniqueness rules | `register-lint.py` | 4 |
| FD-1175 | Adopted RFCs still read `draft` | — | **already resolved** (#855); verified only |
| FD-1181 | `CONTRIBUTING.md` names a `WK-` maintenance item with no row | — | **already resolved** (#840); verified only |

**Rows the predicate does not print, and why they are not here.**
- **FD-1157** (C11). `CR-1212:262` lists it under WK-1170. Its register cell names *"the first
  slice of RFC-937 §8's charter investigation Work"*, which is WK-1169. `CR-1212:215` defines
  "carried" as *"carried with the owner the register names"*, so by that record's own rule the
  register governs. It is in WK-1169's plan.
- **F107, FD-1152, FD-1154.** `CR-1212:267` lists them as carried to *"the lead"*. Their register
  cells name the lead as owner and this Work's first slice as the event (FD-1154: *"or the
  create-read-retire audit's first slice, whichever comes first"*). Owner and event do not
  conflict. They are here.
- **F61.** `CR-1167`'s table routed its counters to the charter investigation, but its acceptance
  line item 3 moved the event to plan review 15. Not here.
- **F112** waits on *"the first `SL-` row cut in that Work's map plan"* for (j), not on this Work.
  Not here.

### Premises, read at `19c395ac`

| # | Premise | Evidence | Status |
|---|---|---|---|
| a | Check 38 enforces RL-943 | `check_loop_signal` (`scripts/audit-docs.py:3434`) prints the population and says the four sub-clauses *"are not implemented yet"* | **does not reproduce** → Slice 3 |
| b | The ownership matrix Stage 4 needs exists | `docs/INDEX.md` `## Ownership matrix` (`:1404`), generated by `doc-index.py`'s `ownership_matrix()` (`:958`) from a hardcoded transcription, `_OWNERSHIP_TABLE` (`:924`), of §1.6's creates column only | **reproduces for the creates column**. The reads and retires columns come from §1.6 itself, in Slice 1 |
| c | The census tool runs post-migration | `scripts/file-census.py` (268 lines) exists; its only committed output is `docs/research/file-census-5ef559d.csv`, recorded in `RS-952` | reproduces; whether its categories still match §1.2's families is Slice 1's first reading |
| d | The owed-list generator finds this Work's rows | `python3 scripts/register-owed.py WK-1170` prints *"(none)"*, rc 0. `register-owed.py "create-read-retire audit"` finds them by phrase | **does not reproduce by id** → FD-1165's class; Slice 1's register pass and Slice 4 |
| e | The migration can run a second time | `migrate` refuses a migrated tree with exit 2 (#821, `47065da5`; `CR-1164` §5, C4) | the harm of FD-1152 is guarded; the defect stands → DP-5 |
| f | The Work is docs-only | `CR-1212:289` (the maintainer's order, quoted) labels WK-1170 and WK-1169 *"(docs-only)"*. Of the thirty open rows above, twenty-seven name a script, a test or the mypy configuration as their instrument; F92, F114 and FD-1160 are the three that do not | **does not reproduce** → DP-1 |

---

## Decision points

The planner rules none of them. The cells stay empty until the resolver's record exists, as the
§1.7 form requires.

| # | Question | Options | Recommendation (the planner's input) | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | `CR-1212` Proposal 2 labels this Work *"docs-only"*. Most of its carried rows are fixes to scripts and tests. Which scope does the maintainer accept? | (a) The Work takes the code slices (3–6), each holding a gate slot; the label is corrected by the maintainer's line; (b) the Work stays docs-only (Slices 1–2); every tooling row is re-dispositioned to WK-1178 (standing maintenance) with the lead's dated line; (c) split: the audit-docs and register instruments here (3, 4), the migration residue (5) and gate coverage (6) to WK-1178 | **(a).** The register names this Work as the event on every one of these rows, accepted by the maintainer's delegate at `CR-1164`'s D7 line and `CR-1167`'s acceptance. Moving twenty-seven rows again is the decay FD-1166 names. The label was written before any plan counted the rows | scope | yes — Slices 3, 4, 5, 6 | *(the maintainer, dated line)* |
| DP-2 | FR-240's clauses (4)–(6) are rating-engine validations in `compile_bundle`, not governance instruments. `CR-1167`'s acceptance item 1 gave the whole *"gate-coverage cluster"* to this Work because *"the cluster is about what the instruments cover"*. Where do these three clauses belong? | (a) Here, in Slice 6; (b) to a rating Work: WK-1178, or a Work the maintainer names; F27 (c), F29 and F33 stay here; (c) carried to P3 by a dated line | **(b).** F27 (c), F29 and F33 are instrument gaps, which is this Work's subject. Clauses (4)–(6) are product behaviour in `compile_bundle`, a file the parallel-start ruling's decision (#928, working id 9760) names as shared by WK-1250, WK-673 and WK-675. A governance slice editing it would have to serialise with three rating Works | scope | yes — Slice 6 | *(the maintainer, dated line)* |
| DP-3 | Every carried row waits on *"the create-read-retire audit's first slice"*. Does that event require every row to be discharged in Slice 1? | (a) Yes: Slice 1 discharges all thirty rows; (b) Slice 1 fires the event by a register pass: each row's cell gains its `SL-` id in this Work, from this plan's Scope table, with the lead's dated line, and closes in that slice; (c) as (b), but the rows keep their text and only the map plan records the slice | **(b).** (a) makes Slice 1 the whole Work. (c) leaves the register naming an event that has fired, which is how rows decayed through reviews 11–14 (FD-1166). (b) also makes `register-owed.py WK-1170` work (Acceptance item 7) | scope | yes — Slice 1 | *(the maintainer, dated line)* |
| DP-4 | Where does the "process step per transition" live once Slice 1 finds it? | (a) A new column in `document-ids.md` §1.6 naming each transition's step (a `process/` amendment: `RFC-` + `RL-`); (b) a table generated by `doc-index.py` from a declared data structure, with a drift check; (c) in the owning skill or charter only, with the Slice 1 record as the evidence and check 38 as the enforcement | **(c).** One source per step (RFC-756). §1.6 already names the role per action. What is missing is the step inside the role's skill. (b) adds a second transcription, which is the defect premise (b) found in `_OWNERSHIP_TABLE`. (a) amends a maintainer-owned file for a fact the skills already carry | decision point | yes — Slice 2 | *(decision-maker, by `RL-`; the maintainer's line too if the answer amends `docs/process/`)* |
| DP-5 | Six rows are defects in `migrate`, a tool that has run once and now refuses a migrated tree (premise e): F78, F94, F96, F107, FD-1149 and FD-1152. Fix them, or accept them with #821's refusal as the control? | (a) Fix all six in Slice 5; (b) accept all six: `decision: accept`, the residual control being #821's exit-2 refusal, with proof 7 cited; (c) fix only what a later tool reuses (FD-1149's sweep, if any non-migrate caller uses it; F78's fixture, since `_discover_roadmap` also serves `doc-index.py`), accept the rest | **(c).** A fix to code that can no longer run buys nothing. A defect in a function another tool still calls is live. Slice 1 reads which functions have a live caller and names them, so this row is answered on evidence | register disposition (`document-ids.md` §1.6, FD row: *"lead sets `decision:`"*) | yes — Slice 5 | *(the lead's dated disposition in the register)* |
| DP-6 | The order between WK-1170 and WK-1169, and between this Work and the code lane | (a) WK-1170's Slice 1 first; WK-1169 starts its binding slices after it (the parallel-start ruling's decision, #928, item 5: *"WK-1169 comes after WK-1170"*); (b) both Works' slices in parallel | **(a)**, re-derived as a real dependency: WK-1169 binds each role's transitions into its charter, and Slice 1 of this Work is where those transitions are named. RFC-897 §8 states the reverse (*"4 needs … 3's matrix"*), but the matrix exists, generated (premise b), so that dependency is already met | sequencing | no — applied at dispatch; default (a) | the activation commit cites the parallel-start ruling (#928) by its minted id |
| DP-7 | F92's 18 non-vendored skill manifests are the same 18 files inside FD-1157's 43 (check 30's skill-manifest failures at `19c395ac`: `python3 scripts/audit-docs.py 2>&1 \| grep '^  - check 30' \| grep -oE '\.claude/skills/[^/]+' \| sort -u` prints 43; the 18 not in `_docid._VENDORED_SKILLS` are F92's residual). FD-1157 is WK-1169's. Which Work stamps them? | (a) WK-1170 Slice 5 stamps the 18; WK-1169 takes the rest of FD-1157; (b) WK-1169 stamps the 18 with the rest of FD-1157, and F92's residual closes on that PR; (c) whichever slice runs first, with the other verifying | **(b).** One slice edits those 18 files once. FD-1157 is the wider row, and its treatment of the 25 vendored manifests needs the same decision (F93, the maintainer's) | scope | yes — Slice 5's F92 limb only | *(the maintainer, dated line; the same line as WK-1169's matching DP)* |

**Slice design, decided here and not a DP.** The audit (Slice 1) comes first: it is the event
every carried row waits on, and it names the gaps that Slices 2 and 3 close. The steps (Slice 2)
follow the audit. Check 38 (Slice 3) enforces the audit's verdicts, so it follows the audit too.
The instrument slices are cut by file, not by row, so that no two slices of this Work edit the
same script:
- Slice 3: `audit-docs.py` and its tests;
- Slice 4: `register-lint.py`, `register-owed.py`, `doc-index.py`, `doc-id.py next` and the core
  JSON key;
- Slice 5: `doc-id.py` (the migrate path), `_docverify.py` and the skill headers;
- Slice 6: the contract guard, check 10 and the mypy configuration.

Slice 3 and Slice 6 both touch `audit-docs.py` (check 10). They run in sequence, never together.

**Slice ids.** No `SL-` row exists for WK-1170. The six `SL-` rows are cut here and minted,
`draft`, with ids the lead issues, when this plan is activated (§1.6's SL row).

## Sequencing

```
Slice 1  the audit + register pass (docs) ─┬─→ Slice 2  the steps (docs)
                                            ├─→ Slice 3  audit-docs checks (code)
                                            ├─→ Slice 4  register and index tooling (code)
                                            ├─→ Slice 5  migrate and verify residue (code)
                                            └─→ Slice 6  gate coverage (code) — after Slice 3
```

- **Slice 1 needs nothing in WK-1170.** It is blocked on DP-3.
- **Slice 2 needs Slice 1**, because its scope is Slice 1's list of transitions without a step.
- **Slice 3 needs Slice 1**, because check 38's sub-clauses encode Slice 1's verdicts.
- **Slices 4 and 5 need Slice 1's register pass**, which confirms their row sets.
- **Slice 6 needs Slice 3**, because both edit `audit-docs.py`.
- **Docs and code in parallel.** Slices 1 and 2 are docs-only and hold no gate slot. Under #928's
  amendment, Slice 2 may run beside one code slice of this Work only if they share no file. Two
  code slices of this Work never run together (the amendment admits two build slices *from
  different Works*).
- **Recommended order:** 1 → 2 and 3 → 4 → 5 → 6.
- **WK-1169's dependency** on this Work is Slice 1's record (DP-6). Nothing else in WK-1169 waits
  on WK-1170.

**Sizing, like for like with the P2 sizing table** (its rates: 0.5 / 0.75 / 1.5 days per slice;
rulings acceptance 0 / 0.25 / 0.5, since this plan is now drafted; the close 0.25 / 0.5 / 1). Six
slices give:
- best 6 × 0.5 + 0 + 0.25 = **3.25**;
- likely 6 × 0.75 + 0.25 + 0.5 = **5.25**;
- worst 6 × 1.5 + 0.5 + 1 = **10.5** working days.

The sizing table's band for this Work is **2 / 4.75 / 12.5**, assumed at 3–7 slices
(`~/gi-pricing-plan.local/scratch/planner-wk674-2/p2-sizing.md`, row WK-1170). Six is inside the
slice range. Best and likely sit above the band's (3.25 against 2, 5.25 against 4.75); worst sits
below it. The rates were measured on code slices. Slices 1 and 2 are docs-only and hold no gate
slot, so the lane cost is four slices: 2.25 / 3.75 / 7.5 on the code lane. If DP-2 moves FR-240
(4)–(6) out and DP-5 accepts the migrate rows, Slice 6 shrinks and Slice 5 halves; the Work does
not drop below five slices.

---

## Tasks

At this level each slice is one task: its scope, its dependency, and an outline of its gate. The
steps are written in its leaf plan. **Item 11 of every slice** is the close condition:

> **The maintainer's MERGE-ACK, naming the PR's full head SHA, is recorded in the lead's channel
> file (`~/gi-pricing-plan.local/channel/to-lead.md`), given by the maintainer or on the
> maintainer's behalf, before the lead merges. It is never posted on the PR.** And the slice's
> clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and the lead's
> merge — no maintainer acceptance line is required for a slice, and none is to be waited on.

### Task 1 — Slice 1: the transition audit and the register pass (docs-only)

- **Scope.**
  - **The audit record**, an `RS-` of `kind: audit`, owned and written by the auditor
    (`document-ids.md` §1.6, RS audit row: *"maintainer requests it as an `SL-`; planner freezes
    scope in a `PL-`"* — this plan is that freeze). For every family in §1.2, and every `kind:`
    where §1.2 lists kinds, one row per transition:
    - creation, into the family's first status;
    - each forward transition of §1.2's "Status subset" column;
    - who reads the record, from §1.6's "Reads & acts" column.

    Each row names the step (skill section, charter line, script function, or check number,
    each with a path and line at the audit's tree) or files an `FD-` for the gap. Each family
    gets one of RFC-897 §6's four verdicts.
  - **The unreferenced population** (Acceptance item 3), with verdict 4 derived from a covering
    `CR-` where one exists (RL-943).
  - **The census run** at the slice's tree with `scripts/file-census.py`. The audit notes where
    its categories differ from §1.2's families. The close-tree run is Acceptance item 4, at the
    last slice.
  - **The register pass** under DP-3: each row in the Scope table gets its `SL-` id and the lead's
    dated line. FD-1175 and FD-1181 are verified resolved and left alone.
  - **FD-1160**: the four content-open H rows and the eighteen migration-only rows of RFC-937 §5
    are read to their content, and each gets a verdict.
  - **FD-1163 (a)**: `CR-1065` §8's audit scope against its write set, read and given a verdict.
  - **F114**: the correcting `RL-` for the four frozen plans, written by the decision-maker.
  - **DP-5's evidence**: for each of F78, F94, F96, F107, FD-1149 and FD-1152, whether the
    function at fault has a live caller outside `migrate`, by `git grep` at the audit's tree.
  - **A charter gap is an `FD-` routed to WK-1169**, never a charter edit here.
- **Depends on:** nothing in WK-1170. Blocked on DP-3.
- **Gate outline.**
  - The audit record passes check 37 (its template's sections) and check 30 (its header).
  - Every `FD-` it files has a register row and an essay (`document-ids.md` §1.6, FD row).
  - The Acceptance item 6 predicate and `register-owed.py WK-1170` are both run at the slice's
    merge tree, and their outputs agree on the open rows.
  - `audit-docs.py`, `doc-index.py --check` and `doc-id.py check` exit 0 at the merge tree.
  - Item 11.

### Task 2 — Slice 2: the missing steps written where they belong (docs-only)

- **Scope.** For every transition Slice 1 finds without a step, the step is written where DP-4
  puts it:
  - in the owning skill under `.claude/skills/` (with `.claude/skills/README.md` in the same
    commit, `CLAUDE.md` §12);
  - or, if DP-4 rules (a), in `document-ids.md` §1.6, through `RFC-` + `RL-`;
  - a charter gap is not written here: it goes to WK-1169 as an `FD-`.

  Each step names the check or script that proves it ran, where one exists.
- **Depends on:** Slice 1. Blocked on DP-4.
- **Gate outline.**
  - For each written step, the audit record's row is re-read at the slice's tree and now names a
    step, not a gap.
  - `audit-docs.py`, `doc-index.py --check` and `doc-id.py check` exit 0.
  - Item 11.

### Task 3 — Slice 3: the audit-docs checks (code)

- **Scope**, all in `scripts/audit-docs.py` and its tests:
  - check 38's four sub-clauses (premise a; RL-943 as code), encoding Slice 1's verdicts;
  - a status-at-filing check (`CR-1212` Proposal 8);
  - a plan-status staleness check derived from the INDEX `execution` column (Proposal 13);
  - check 2 and fenced blocks, decided with a broken-input proof (Proposal 11);
  - F90 (check 37's heading detector), F108 (check 35's output shape), FD-1168 (check 9's minute
    field);
  - FD-1159: the proofs for checks 32, 36 and 38 in item 11's form;
  - FD-1163 (b) check 39's false note, and (c) §1.9's SL- lint: built, or §1.9's sentence
    corrected by `RFC-` + `RL-` (the leaf plan carries that choice as its own DP).
- **Depends on:** Slice 1. Blocked on DP-1.
- **Gate outline.**
  - Each new or changed check is shown red on a deliberately broken fixture and quiet on a clean
    one, each failure named by its cause.
  - A warn-only check is proven by its printed warning, since it cannot fail (`CR-1164` §2's
    check 38 row).
  - The full gate. Item 11.

### Task 4 — Slice 4: the register and index tooling (code)

- **Scope:**
  - `register-lint.py`: F86's three limbs, FD-1166, and FD-1174's owner-existence and
    id-uniqueness rules;
  - `register-owed.py`: FD-1165's four limbs, including matching a Work by its `WK-` id and by
    the phrase the register used before Slice 1's pass;
  - `doc-index.py --phase`: FD-1155;
  - `doc-id.py next` and the reserved block: FD-1158;
  - `delivery-process.core.json`'s key split: FD-1154, unless the next `delivery-process.md`
    amendment took it first. That file is `docs/process/`, so the split carries the `RFC-` +
    `RL-` pair.
- **Depends on:** Slice 1's register pass. Blocked on DP-1.
- **Gate outline.**
  - Each rule red on a broken register fixture built in `tmp_path`, never in the real
    `docs/findings/` (F89's defect).
  - `register-owed.py WK-1170` lists exactly the open rows of the Acceptance item 6 predicate.
  - The full gate. Item 11.

### Task 5 — Slice 5: the migrate and verify residue (code)

- **Scope:**
  - `_docverify.py`: F101 (row (i)'s limb 1 exit-code proof), F103 (the sentinel population),
    F106 (a ceiling on row (g)'s counts);
  - row (g) at `classified-by-none=207` and C15's 207 entries, taken to a cause-attributed
    reading or a dated acceptance;
  - `doc-id.py`: F100 (the docstring); F78, F94, F96, F107, FD-1149 and FD-1152 as DP-5 rules;
  - F92: headers on the 18 non-vendored skill manifests, if DP-7 rules (a);
  - FD-1150, only if it recurs.
- **Depends on:** Slice 1's register pass. Blocked on DP-1 and DP-5.
- **Gate outline.**
  - Each fix red first on broken input.
  - The verify run (`_docverify.py`) at the merge tree, its verdict counts compared with the
    last recorded reading.
  - The full gate. Item 11.

### Task 6 — Slice 6: gate coverage (code)

- **Scope:**
  - F27 (c): a comparison of the three 03 rating shapes against their hand-authored contracts,
    through `contract-guard`;
  - F29: check 10 compares error codes in both directions against `backend/src/app/errors.py`,
    allowing the spec-first case the row names;
  - F33's remainder;
  - FR-240 (4)–(6) only if DP-2 rules (a).
- **Depends on:** Slice 3 (both edit `audit-docs.py`). Blocked on DP-1 and DP-2.
- **Gate outline.**
  - Each comparison red on a deliberately diverged shape or code.
  - The close-tree census (Acceptance item 4), if this is the last slice.
  - The full gate. Item 11.

---

## Activation

When the maintainer (or the session acting on the maintainer's behalf) accepts this plan, the
activation commit:
1. Sets this plan `status: active`. This is permitted only when every blocking Decision point
   row has a resolver id (`document-ids.md` §1.7). Otherwise the plan stays `draft`, and the
   open rows are named in the acceptance line. A slice may start while a later slice's DP is
   open, as `document-ids.md` §1.7's last sentence allows: *"an `SL-` may not move
   `draft → active` while any of its rows is open"*.
2. The lead adds the six `SL-` rows under `### WK-1170`, each `draft`, with ids the lead issues.
   WK-1170 is already `active` (`docs/roadmap.md:822`).
3. `docs/INDEX.md` is regenerated in the final commit only.

## Status

- **Acceptance line:** _pending — the maintainer's dated line, or one given on the maintainer's
  behalf_.
- **Working id 9811.** `PL-9811` is a working id, taken after `git grep` over `origin/main` and
  every `origin/*` branch at `19c395ac` found no document carrying it. The lead mints the real
  id with `python3 scripts/doc-id.py next --ref origin/main` at the merge turn. Until then
  `doc-id.py check` reds this file under check 31, which is expected.
- **Open:** DP-1, DP-2, DP-3 and DP-7 (the maintainer's), DP-4 (the decision-maker's), DP-5
  (the lead's). DP-6 is non-blocking, with its default.

## Self-review

1. **Spec coverage.** RFC-937 §8's subject, RFC-897 §6 and §11 (a) and (d), `CR-1212` Proposals
   8, 11 and 13, `CR-1164`'s C3 and C15, and every row the Acceptance item 6 predicate prints at
   `19c395ac` (32, two already resolved) are each in a Scope table with a slice. FD-1157, F61 and
   F112 are named with the reason each is not here.
2. **Scope boundaries.** No charter is edited (WK-1169's). No `docs/process/` file is amended
   without `RFC-` + `RL-`. FR-240 (4)–(6) is held on DP-2.
3. **Literals.** Every path, line, id and count in the premises and the Scope tables was read at
   `19c395ac`. Every id resolves in `docs/INDEX.md` at that tree, except the parallel-start
   ruling, which is named by its working id 9760 on open PR #928 with its head.
4. **Placeholders.** None. The empty `Resolved by` cells are the §1.7 form for open rows, and
   each names its resolver. There are no code steps; this is a map plan.
5. **Consistency.** The slice numbers in the Scope tables, the DP `Blocking` cells, the
   Sequencing and the Tasks agree (grep "Slice N" across the file).
