---
id: PL-9812
family: plan
kind: map
title: WK-1169 — The charter investigation (RFC-937's binding charters, RFC-897 Stage 3, and the charter rows carried to it): map plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-29
owner: planner
tree: 19c395acad594d1b193da197461bec85201d2248
phase: P2
work: WK-1169
supersedes: []
superseded_by: ~
corrected_by: []
relates: [CR-1164, CR-1167, CR-1183, CR-1212, RFC-937, RFC-897, RFC-928, RL-945, FD-1161, FD-1157]
---

# WK-1169 — The charter investigation: map plan

> **For agentic workers:** this is a **map plan**. It cuts WK-1169 into four slices and fixes their scope, order, dependencies and gates. It carries no code steps. Each slice gets its own leaf plan (`kind: leaf`) before it starts, and the executor works from that leaf plan. REQUIRED SUB-SKILL for each leaf plan's executor: subagent-driven-development (recommended) or executing-plans. Slices 1, 2 and 4 also bind `docs-audit` and `writing-skills` (Slice 2 edits skills and charters); Slice 3 also binds `python-test` (broken-input proofs), `code-quality`, `dev-commands` (the gate) and `docs-audit`. Every executor reads `docs/plans/README.md`'s five unchecked conventions before its first step.

## Goal

Make `document-ids.md` §1.6 binding in each of the seven role charters, and give every governed
directory an `owner:` rule a check can read. Concretely:

- **The map.** For every family in §1.6 and every one of its five actions (creates and amends;
  accepts or decides; reads and acts; verifies and closes; supersedes or retires), find the
  charter line that grants it. File every family no charter owns, and every role charged with
  something its charter does not name (RFC-897 §5, §11 (c)).
- **The charters.** Amend each charter once, so that it binds its §1.6 rows, and discharge the
  charter-clause rows carried to this Work in the same amendment.
- **The directories.** Give each `docs/<family>/README.md` the `Permitted owners:` line that
  check 35's second clause already reads, so that the clause stops being vacuous.
- **The instruments.** Prove the binding with a check, and derive the generated ownership matrix
  from §1.6 rather than from a hand transcription.

The Work is done when the Acceptance Standard below holds at the last slice's merge tree.

**Architecture.** A map plan, per `docs/process/delivery-process.md` §5 step 2, in the form of
`PL-1254` (WK-1250's map plan). The Work's subject is WK-1169's roadmap section
(`docs/roadmap.md:800-815` at `19c395ac`): *"the ownership table of `document-ids.md` section 1.6
made binding in each role charter, with a directory-level `owner:`"*, plus its dated 2026-09-28
line carrying RFC-897 §5. RFC-937 names the Work in §8's closing sentence: *"the charter
investigation (§1.6 made binding in each charter; directory-level `owner:`)"*.

**A relay correction, recorded so no reader inherits it.** The brief for this plan cited
"RFC-937 §5" as the section the roadmap row names. RFC-937 §5 is "Impact — every area that
changes". The row's section is **RFC-897 §5** (Stage 3, the ownership map), and RFC-937's is §8.

**Tech Stack.** Markdown charters under `.claude/roles/`, skills under `.claude/skills/`, READMEs
under `docs/`; Python 3.12 scripts under `scripts/` and their tests (Slice 3 only). **No new
dependency is planned.**

**Spec.** The executors read these with their leaf plans:
- [`../process/document-ids.md`](../process/document-ids.md): §1.6 (roles per family,
  `:144-174`, including its 2026-09-29 amendments to the Phase and CR rows), §1.11 check 35
  (`:220-236`).
- [`../rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md`](../rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md):
  §5 (Stage 3, `:161-168`), §11 (c) (`:249-262`).
- [`../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md):
  §8 (`:439-441`), §9 (`:443-455`: *"Rulings 55–58 — absorbed — matrix generated"*).
- [`../closures/CR-01183-wk-695-work-close-file-taxonomy-reference-coding-and-custody.md`](../closures/CR-01183-wk-695-work-close-file-taxonomy-reference-coding-and-custody.md)
  (Stage 3 and §11 (c), `:74`, `:83`, `:148`, `:153`, `:168`, `:192`);
  [`../closures/CR-01164-wk-697-work-close-the-closure-record.md`](../closures/CR-01164-wk-697-work-close-the-closure-record.md)
  §8 and §10 (the `executor.md` rider); [`../closures/CR-01167-plan-review-14-the-wk-697-close-the-register-rows-decayed-to-it-and-the-two-downstream-works.md`](../closures/CR-01167-plan-review-14-the-wk-697-close-the-register-rows-decayed-to-it-and-the-two-downstream-works.md).
- The seven charters, `.claude/roles/{auditor,decision-maker,executor,lead,planner,reporter,watcher}.md`,
  and [`../findings/register.md`](../findings/register.md): every row the Scope table lists.

## Acceptance Standard

These conditions are for the Work as a whole. Each leaf plan states its own conditions for its
slice. Every command runs on a detached copy of the named tree (`git worktree add --detach`),
never on a working tree.

1. **Every §1.6 cell has a charter line or an `FD-`.** The Slice 1 audit record (`RS-`,
   `kind: audit`) carries one row per §1.6 family × action. Each row cites the charter line that
   grants the action (path and line at the record's tree), or names the maintainer where §1.6
   does, or files an `FD-` for the gap. At the last slice's merge tree no such `FD-` is open
   without a resolution in `docs/findings/register.md`.
2. **No unfiled empty row or column** (RFC-897 §11 (c); `CR-1183:83`). A family no charter owns,
   and a role charged with an action its charter does not name, each carry an `FD-`. The
   reporter's and the watcher's empty rows are declared by their charters, as §1.6's closing
   paragraph requires (`document-ids.md:173`), and are not gaps.
3. **Each charter binds its §1.6 rows**, in DP-2's form, and a check proves it: the check reds on
   a deliberately broken charter fixture that grants a family §1.6 does not give that role, and
   is quiet on the real charters.
4. **The generated ownership matrix derives from §1.6.** At `19c395ac`, `doc-index.py`'s
   `ownership_matrix()` (`scripts/doc-index.py:958`) inverts `_OWNERSHIP_TABLE` (`:924`), a
   hardcoded transcription of §1.6's first column. After Slice 3, either the matrix is parsed
   from §1.6 itself, or a test reds when the transcription and §1.6 disagree, proven on a
   deliberately diverged fixture.
5. **Every governed directory has a directory-level owner.** At `19c395ac`,
   `git grep -l -E '^Permitted owners:'` prints one file, a test fixture
   (`tests/fixtures/docs-ids/w37-4-checks/check35-readme-allowlist/README.md`), and none of the
   ten `docs/*/README.md` files. After Slice 2, each of them carries the line DP-3 rules, and
   check 35's second clause is shown red on a real record whose `owner:` the line excludes.
6. **Every carried register row is resolved.** The predicate, runnable at any tree:
   `awk -F'|' 'NF>2 && tolower($(NF-1)) ~ /charter investigation|wk-1169/' docs/findings/register.md`
   (the Decision column only). At `19c395ac` it prints **14** rows. At the Work close every row
   it prints opens with a resolution marker `scripts/register-lint.py` accepts, citing a PR or
   the lead's dated disposition. `python3 scripts/register-owed.py WK-1169` lists the open ones
   after Slice 1's register pass, and none at the close.
7. **Every charter amendment carries the maintainer's line** (§1.6, charters row), in DP-4's
   form.
8. **Every Decision point has its resolver before the slice it blocks starts**
   (`document-ids.md` §1.7).
9. **Every slice closes on its own clean audit** and its own item 11 (see **Tasks**).
10. **The gate passes on Slice 3's merged tree**, both halves (`CLAUDE.md` §11), and
    `python3 scripts/audit-docs.py`, `python3 scripts/doc-index.py --check` and
    `python3 scripts/doc-id.py check` exit 0 on the merged tree of each docs-only slice.

## Global Constraints

- **Charters are the maintainer's** (`document-ids.md` §1.6, charters row: *"maintainer; 'a role
  file that proves insufficient' → `FD-` → maintainer amends"*). No charter changes without the
  line DP-4 rules.
- **`docs/process/` is the maintainer's** (§1.6, `process/` row: *"amendments arrive as `RFC-` +
  `RL-`"*). This Work reads §1.6. It changes §1.6 only through that pair, if Slice 1 finds §1.6
  itself wrong.
- **One source, never a restated list** (`CLAUDE.md` §0, RFC-756). A charter that restates its
  §1.6 rows restates a copy that can go stale. DP-2 weighs this.
- **A role file that proves insufficient is fixed, not briefed around** (`CLAUDE.md` §15).
- **Skills.** A skill edited here updates `.claude/skills/README.md` in the same commit
  (`CLAUDE.md` §12). A vendored skill is not edited (`CLAUDE.md` §12).
- **A count carries its tree, its corpus and its predicate** (`CLAUDE.md` §13).
- **Parallelism.** Under `delivery-process.md` §8 as amended by open PR #928 (the parallel-start
  ruling, working id 9760, head `074d7778`, not merged at `19c395ac`): preparation (plans,
  rulings, audits) runs alongside; at most two code slices from different Works run at once,
  each with a gate slot (`.claude/roles/executor.md:110`), with no shared files. That decision
  also states *"WK-1169 comes after WK-1170"* (item 5); see DP-9. If #928 does not merge, §8 as
  it stands at `19c395ac` applies: one slice at a time.

---

## Scope

### The Work's own subject (no register row)

| Source | Obligation | Slice |
|---|---|---|
| RFC-937 §8, closing sentence; roadmap `### WK-1169` | §1.6 made binding in each charter | 1 (the map), 2 (the charters), 3 (the check) |
| Same | A directory-level `owner:` | 2 (the README lines), 3 (check 35 proven on them) |
| RFC-897 §5 (Stage 3), carried by the roadmap's 2026-09-28 line and `CR-1183:74`, `:148`, `:168`, `:192` | The category × role matrix, each cell citing its charter line; empty rows and columns filed | 1 |
| RFC-897 §11 (c), `CR-1183:83`, `:153` | No unfiled empty matrix row | 1 |
| `CR-1164` §10, "Rider proposal for `executor.md`" | *"the docs checks a request quotes are measured on a detached copy of the committed tree … never on a working tree"*; no finding row, by the lead's ruling of 2026-09-27 14:58:11 BST | 2 |

### Carried register rows, each individually

Read at `19c395ac` with the item 6 predicate.

| Row | Subject (short) | Where it lands | Slice |
|---|---|---|---|
| F28, residuals P5, P7 and P1b only | P5: no document owns the stand-down procedure (`FD-894:648`); P7: the writer's half, *"do not move a branch someone is reading"* (`:650`); P1b: its working-note half (`:644`). `CR-1167` asks this Work to verify P7 and P1b first | a charter or skill, per Slice 1 | 1 (verify), 2 (write) |
| F31 | `watcher.md:26-28` claims a roster derivation; `:32` marks it UNIMPLEMENTED | `watcher.md`: the live-roster claim struck (DP-5 (b)) | 2 |
| F73 | `nudge.py`'s three-signal conjunction cannot tell a long wait from a dead lead | the roster claim struck (DP-5 (b)); the limit accepted by the lead's dated line | 2 |
| F74 | `reporter.md`'s "Mechanism: Lead freshness nudge" (`:104-107`) still describes one signal | `reporter.md` | 2 |
| F75 | The end-turn rule is in one charter of seven (`executor.md:69`) | the other five spawned charters | 2 |
| F97 | The `lead.md` clause landed (W37-8); the row's broken-input test is unmet | a test, or the lead's acceptance (Slice 3's leaf plan) | 3 |
| FD-1151 | `watcher.md:64-67`'s "Re-derives, does not compare" names no input | `watcher.md` | 2 |
| FD-1153 | `auditor.md:46` names an essay path the `FD-` template contradicts; `docs/findings/README.md` says the same | `auditor.md`, `docs/findings/README.md` | 2 |
| FD-1156 | The `RL-` family has no creating skill | a `Creates` row in `.claude/skills/README.md` naming `decision-maker.md` (DP-7 (b)) | 2 |
| FD-1157 | 70 files fail check 30: 43 skill manifests, 27 docs files | headers; the 18 non-vendored manifests here (DP-8 (b)); the 25 vendored disclosed until F93 | 4 |
| FD-1161 | Nothing checks a plan's Roles table against §1.6 | a check | 1 (reading), 3 (the check) |
| FD-1162 | The reporter's cycle heading time is composed before the write | `reporter.md` or the `reporter-cycle` skill | 2 |
| FD-1191 | A stopped agent's work is stranded; recovered only by manual salvage | RFC-928 option D only (`RFC-928:218-222`), per DP-6 (a): `lead.md` and the dispatching skill's local rule, at the location DP-6 fixes | 2 |
| FD-1192 | `CR-926` Proposal 3.5 (a delegated evidence request names the direct command; the dispatcher runs it) was accepted and never landed | `lead.md` or `dispatching-parallel-agents`' local rule | 2 |

**Rows near this Work that are not here, and why.**
- **F61.** `CR-1167`'s table routed its retry counters to *"the charter investigation's first
  slice"*, but that record's acceptance line, item 3, moved the event to plan review 15. The
  register cell follows the acceptance line.
- **FD-9640** (open PR #909, `aud-row11-p9-artifact-b`) reopens F58 and F91, the runtime state
  writer, with owner WK-1178. FD-1151 is the charter clause only; the writer is not this Work's.
  If #909 merges first, Slice 2's FD-1151 clause names the input the writer then uses.
- **F92's 18 skill manifests** are WK-1170's row, but the same 18 files are inside FD-1157's 43
  (DP-8, matching `PL-9811`'s DP-7).

### Premises, read at `19c395ac`

| # | Premise | Evidence | Status |
|---|---|---|---|
| a | A generated ownership matrix exists | `docs/INDEX.md` `## Ownership matrix` (`:1404`), from `ownership_matrix()` (`scripts/doc-index.py:958`) over `_OWNERSHIP_TABLE` (`:924`), the creates column only | **reproduces for one column of five**; a hand transcription → Slice 3 |
| b | Charters cite §1.6 | `grep -c '1\.6'` per charter: auditor 3, decision-maker 7, executor 6, lead 3, planner 3, reporter 1, watcher 1 | citations exist; whether each grant matches §1.6 is Slice 1's reading |
| c | Directories declare their owners | no `docs/*/README.md` carries `Permitted owners:` (Acceptance item 5); check 35's reader exists (`_PERMITTED_OWNERS_RE`, `scripts/audit-docs.py:2433`) | **does not reproduce** → Slice 2 |
| d | The owed-list generator finds this Work's rows | `python3 scripts/register-owed.py WK-1169` prints the rows whose cells name `WK-1169` (FD-1191 and FD-1192), not the twelve that name the Work by phrase | partial → Slice 1's register pass; the generator's defect is FD-1165, WK-1170's |
| e | The Work is docs-only | `CR-1212:289` labels WK-1170 and WK-1169 *"(docs-only)"*. Acceptance items 3 and 4 need a check and a change to `doc-index.py`; F73 names `nudge.py` | **does not reproduce for Slice 3** → DP-1, (a) accepted |
| f | The skill-manifest headers are one set | check 30's skill-manifest failures, `python3 scripts/audit-docs.py 2>&1 \| grep '^  - check 30' \| grep -oE '\.claude/skills/[^/]+' \| sort -u`, print 43; 25 are in `_docid._VENDORED_SKILLS`, 18 are not, and the 18 are F92's residual | overlap with WK-1170 → DP-8, (b) accepted: stamped here |

---

## Decision points

The planner rules none of them. The cells stay empty until the resolver's record exists, as the
§1.7 form requires.

| # | Question | Options | Recommendation (the planner's input) | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | `CR-1212` Proposal 2 labels this Work *"docs-only"*. Slice 3 is code. Which scope does the maintainer accept? | (a) The Work takes Slice 3, holding one gate slot; (b) docs-only: the check and the matrix derivation go to WK-1178 with the lead's dated line; (c) as (b), and the binding is declared without a check | **(a).** FD-1161's title is *"nothing checks a Roles table against `document-ids.md` §1.6"*. A binding with no check is the state the Work exists to end. It is one small code slice | scope | yes — Slice 3 | **(a) accepted:** the maintainer, by delegation, 2026-09-29, entry 'DECISIONS: WK-1169 map plan #931' (the lead's channel file, 23:05:29 BST). `CR-1212`'s "docs-only" label is corrected by the same dated note as `PL-9811`'s DP-1; it is not this plan's to write |
| DP-2 | What form does "§1.6 made binding in each charter" take? | (a) Each charter restates its §1.6 rows, and a check compares the two; (b) each charter points at §1.6 (*"the families §1.6 gives this role"*) with no restatement, and the generated matrix is the per-role view; (c) (b), plus a check that no charter grants an action §1.6 does not give that role, and the matrix derived from §1.6 itself | **(c).** (a) writes seven copies of one table (RFC-756). (b) binds by reference, but nothing catches a charter or a plan's Roles table granting more (FD-1161's case). (c) keeps one source and checks the direction that has failed | decision point | yes — Slices 2 and 3 | *(decision-maker, by `RL-`)* |
| DP-3 | What does each directory's `Permitted owners:` line say? | (a) The roles in §1.6's "Owner — creates & amends" cell for the family that directory holds, verbatim; (b) (a) plus every role in the "Accepts / decides" cell; (c) generated into each README by `doc-index.py` from §1.6 | **(a).** Check 35 tests `owner:`, which is the creator (`document-ids.md` §1.5). Acceptors never write `owner:`. (c) makes ten READMEs generated files, which §1.2's Reference row does not allow for a README | decision point | yes — Slice 2 | *(decision-maker, by `RL-`)* |
| DP-4 | Charter amendments are the maintainer's. What line authorises Slice 2's? | (a) Item 11's MERGE-ACK, naming each charter the PR amends; (b) a separate dated line per charter, before the PR opens; (c) an `RL-` authored by the maintainer | **(a).** One line, on the exact head, naming each file. (b) authorises text not yet written. (c) adds a record for what a MERGE-ACK already records | scope | yes — Slice 2 | **(a) accepted:** the maintainer, by delegation, 2026-09-29, entry 'DECISIONS: WK-1169 map plan #931' (the lead's channel file, 23:05:29 BST). A charter edit is authorised only by a MERGE-ACK naming each charter file the PR amends; an ACK that does not name one does not authorise that edit, and the lead re-requests it |
| DP-5 | F31 and F73 need a live roster, which does not exist (`watcher.md:32`). Build it, or stop claiming it? | (a) Build the roster derivation in the watcher's tooling, and add it to `nudge.py` as the fourth signal; (b) strike the roster claim from `watcher.md` and `reporter.md`, and accept F73's limit with a dated line; (c) (b) now, and (a) as a WK-1178 item | **(b).** The runtime state writer the roster would sit on is itself reopened by FD-9640 (#909, owner WK-1178). A fourth signal built on it inherits that defect. (b) makes the charters true now | scope | yes — Slice 2's F31 and F74 limbs; Slice 3's F73 limb | **(b) accepted:** the maintainer, by delegation, 2026-09-29, entry 'DECISIONS: WK-1169 map plan #931' (the lead's channel file, 23:05:29 BST). Strike the live-roster claim for F31 and F73; the roster is not built. #909 (FD-9640) owns the runtime-state writer |
| DP-6 | FD-1191's remedy is RFC-928 option D (durable output for delegated work). RFC-928 is `draft`. May a charter rule adopt one option of a draft RFC? | (a) The maintainer accepts RFC-928 option D in part, by a dated line; Slice 2 writes it into `lead.md` and the dispatching skill, with an agreed location; (b) wait for RFC-928 as a whole; FD-1191 stays deferred; (c) accept FD-1191 as disclosed | **(a).** Five salvages in one day (the row's own count) is a recurring cost. Option D is the only one the RFC says touches direction B. The location is the one choice left, and it is small | scope | yes — Slice 2's FD-1191 limb only | **(a), in part, accepted:** the maintainer, by delegation, 2026-09-29, entry 'DECISIONS: WK-1169 map plan #931' (the lead's channel file, 23:05:29 BST). **Option D only**: a delegated result is written to a durable file, or committed on the delegate's branch, never returned only through the report channel. Options A, B, C and E stay open, and RFC-928 stays `draft`. **Location (binding):** the delegate's branch when it has one; otherwise `~/gi-pricing-plan.local/delegated/<dispatcher>/<yyyy-mm-dd>-<task>.md`; never a job dir or `/tmp` |
| DP-7 | FD-1156: an `RL-` creating skill, or a declared `Creates` row naming the charter? The row says *"Fix is the owner's choice"* | (a) A new `.claude/skills/ruling-write` skill; (b) a `Creates` row in `.claude/skills/README.md` naming `.claude/roles/decision-maker.md` as the `RL-` creating instrument | **(b).** RFC-937 §7 (j)'s Ruling row was already discharged in substance with the charter as the instrument (option (b)). A skill that restates the charter is a second copy | register disposition (the row's owner, the lead) | yes — Slice 2's FD-1156 limb only | **(b), the lead's** (the 23:05:29 BST entry: *"DP-7 (b) and DP-9 (a) are yours: noted"*; the lead's message to the planner, 2026-09-29). The register disposition is written at Slice 1's register pass |
| DP-8 | Which Work stamps F92's 18 non-vendored skill manifests, which are inside FD-1157's 43? And the 25 vendored ones? | (a) WK-1170 stamps the 18; (b) this Work's Slice 4 stamps the 18, and F92's residual closes on that PR; the 25 vendored stay disclosed until F93's dated RFC-937 amendment (owner the maintainer) rules their header; (c) whichever slice runs first | **(b).** One slice edits the 18 files once. The vendored manifests cannot be stamped under `CLAUDE.md` §12 until F93 says how | scope | yes — Slice 4 | **(b) accepted:** the maintainer, by delegation, 2026-09-29, entry 'DECISIONS: WK-1169 map plan #931' (the lead's channel file, 23:05:29 BST), the same line as WK-1170's map plan's DP-7 (#930, working id 9811). Slice 4 stamps the 18 once and F92's residual closes on that PR. The 25 vendored manifests stay disclosed until F93, which is the maintainer's own RFC-937 amendment and is not ruled by this line. Slice 4 is serialised against WK-1170's Slice 2 |
| DP-9 | The order against WK-1170 | (a) Slice 1 starts after WK-1170's Slice 1 record exists; Slices 2–4 follow this Work's own order; (b) independent | **(a)**, re-derived as a real dependency: Slice 1's "verifies and closes" and "supersedes / retires" columns are the transitions WK-1170's Slice 1 names. #928's decision, item 5, states the same order. Slice 4 depends on nothing in WK-1170 except DP-8 | sequencing | no — applied at dispatch; default (a) | **(a), the lead's** (the 23:05:29 BST entry, *"noted"*); the activation commit cites the parallel-start ruling (#928) by its minted id |

**Slice design, decided here and not a DP.** The map (Slice 1) comes first because every charter
edit needs to know what the charter is missing. The charters are amended once, in one slice
(Slice 2), because the seven files are shared by every limb: splitting the §1.6 binding from the
charter-clause rows would edit each charter twice. The check (Slice 3) follows the amendment,
because a check landed before it would red on the charters it is meant to accept. The headers
(Slice 4) touch no charter and can run whenever DP-8 is ruled, but they edit skill manifests,
which WK-1170's Slice 2 also edits, so the two are serialised.

**Slice ids.** No `SL-` row exists for WK-1169. The four `SL-` rows are cut here and minted,
`draft`, with ids the lead issues, when this plan is activated (§1.6's SL row).

## Sequencing

```
WK-1170 Slice 1 ─→ Slice 1  the ownership map (docs) ─→ Slice 2  the charters and READMEs (docs) ─→ Slice 3  the checks (code)
                   Slice 4  the headers (docs) — after DP-8, never beside WK-1170 Slice 2
```

- **Slice 1 needs WK-1170's Slice 1 record** (DP-9). It is blocked on nothing else.
- **Slice 2 needs Slice 1**, and is blocked on DP-2 and DP-3.
- **Slice 3 needs Slice 2**, and is blocked on DP-2.
- **Slice 4** (DP-8 resolved) is serialised against WK-1170's Slice 2 (shared skill manifests).
- **Docs and code.** Slices 1, 2 and 4 are docs-only and hold no gate slot. Slice 3 holds one.
- **Recommended order:** 1 → 2 → 3, with 4 in any gap that WK-1170's Slice 2 is not using.

**Sizing, like for like with the P2 sizing table** (its rates: 0.5 / 0.75 / 1.5 days per slice;
rulings acceptance 0 / 0.25 / 0.5, since this plan is now drafted; the close 0.25 / 0.5 / 1).
Four slices give:
- best 4 × 0.5 + 0 + 0.25 = **2.25**;
- likely 4 × 0.75 + 0.25 + 0.5 = **3.75**;
- worst 4 × 1.5 + 0.5 + 1 = **7.5** working days.

The sizing table's band for this Work is **1.5 / 3.25 / 9.5**, assumed at 2–5 slices
(`~/gi-pricing-plan.local/scratch/planner-wk674-2/p2-sizing.md`, row WK-1169). Four is inside the
slice range. Best and likely sit above the band's (2.25 against 1.5, 3.75 against 3.25); worst sits
below it. Only Slice 3 holds a gate slot, so the code lane carries one slice: 0.5 / 0.75 / 1.5.

---

## Tasks

At this level each slice is one task: its scope, its dependency, and an outline of its gate. The
steps are written in its leaf plan. **Item 11 of every slice** is the close condition:

> **The maintainer's MERGE-ACK, naming the PR's full head SHA, is recorded in the lead's channel
> file (`~/gi-pricing-plan.local/channel/to-lead.md`), given by the maintainer or on the
> maintainer's behalf, before the lead merges. It is never posted on the PR.** And the slice's
> clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and the lead's
> merge — no maintainer acceptance line is required for a slice, and none is to be waited on.

### Task 1 — Slice 1: the ownership map (docs-only)

- **Scope.**
  - **The audit record**, an `RS-` of `kind: audit`, written by the auditor (§1.6, RS audit
    row). One row per §1.6 family × action, five actions per family. Each row cites the charter
    line that grants it, at the record's tree, or files an `FD-`. The "verifies and closes" and
    "supersedes / retires" columns are read against WK-1170's Slice 1 transition record.
  - **Empty rows and columns** (Acceptance item 2), each filed as an `FD-`.
  - **The transcription check by hand**: `_OWNERSHIP_TABLE` against §1.6 at the record's tree,
    including §1.6's two 2026-09-29 amendments (the Phase row and the CR row). Each disagreement
    is an `FD-` for Slice 3.
  - **FD-1161**: every `active` or `draft` plan's Roles table, if it has one, read against
    §1.6. The reading is evidence for Slice 3's check; no frozen plan is edited.
  - **F28**: P7 and P1b verified first, as `CR-1167` asks; then P5, P7 and P1b each placed in
    the charter or skill Slice 2 writes.
  - **The register pass**: each row in the Scope table gets its `SL-` id and the lead's dated
    line, as `PL-9811`'s DP-3 recommends for the same event wording. If the maintainer rules that
    DP differently, this pass follows the ruling.
- **Depends on:** WK-1170's Slice 1 record (DP-9).
- **Gate outline.**
  - The record passes check 37 and check 30.
  - Every `FD-` it files has a register row and an essay.
  - `register-owed.py WK-1169` at the merge tree lists every open row the item 6 predicate
    prints.
  - `audit-docs.py`, `doc-index.py --check` and `doc-id.py check` exit 0. Item 11.

### Task 2 — Slice 2: the charters and the directory owners (docs-only)

- **Scope.** Each charter is amended once:
  - **The binding**, in DP-2's form, for all seven charters. The reporter's and the watcher's
    charters keep their declared empty rows.
  - **The charter rows:** F74 and FD-1162 (`reporter.md`, or the `reporter-cycle` skill for
    FD-1162); F31 and FD-1151 (`watcher.md`; F31's live-roster claim struck, DP-5 (b)); F75 (the five spawned charters
    without the end-turn rule); FD-1153 (`auditor.md`, and `docs/findings/README.md`'s naming
    paragraph); FD-1192 and FD-1191 (`lead.md` and `dispatching-parallel-agents`' local rule; FD-1191 is RFC-928 option D at DP-6's location, and RFC-928 gains the dated note *"option D adopted 2026-09-29 via PL-9812 DP-6; A, B, C and E remain open"*); F28's
    P5, P7 and P1b where Slice 1 placed them; `CR-1164`'s `executor.md` rider.
  - **FD-1156** per DP-7 (b): a `Creates` row in `.claude/skills/README.md` naming
    `.claude/roles/decision-maker.md`.
  - **The directory owners**: the `Permitted owners:` line in each of the ten `docs/*/README.md`
    files, per DP-3.
  - **F73** (DP-5 (b)): the roster claim struck from `reporter.md`, and the lead's dated
    acceptance of the limit in the register.
  - Any §1.6 defect Slice 1 found is not fixed here. It goes to the maintainer as an `RFC-` +
    `RL-` proposal.
- **Depends on:** Slice 1. Blocked on DP-2 and DP-3; DP-4, DP-5, DP-6 and DP-7 are resolved.
- **Gate outline.**
  - For each audit-record row that named a gap, the row is re-read at the slice's tree and now
    cites a charter line.
  - Check 35 is run at the merge tree, and a deliberately wrong `owner:` on a scratch copy of a
    real record in one directory is shown red by the second clause (Acceptance item 5).
  - The MERGE-ACK names each charter file the PR amends (DP-4 (a)). An ACK that omits one does
    not authorise that edit; the lead re-requests it.
  - `audit-docs.py`, `doc-index.py --check` and `doc-id.py check` exit 0. Item 11.

### Task 3 — Slice 3: the checks (code)

- **Scope:**
  - The binding check, per DP-2: no charter grants an action §1.6 does not give that role. It
    also reads a plan's Roles table (FD-1161).
  - The ownership matrix derived from §1.6 itself, or a drift test against `_OWNERSHIP_TABLE`
    (Acceptance item 4).
  - F97: the broken-input test the row names, if the `lead.md` clause is backed by a script;
    otherwise the leaf plan puts the residual to the lead as a dated acceptance.
  - No `nudge.py` change: DP-5 (b) struck the roster claim.
- **Depends on:** Slice 2. Blocked on DP-2; DP-1 is resolved.
- **Gate outline.**
  - Each check red on a deliberately broken charter or Roles-table fixture built in `tmp_path`,
    each failure named by its cause, and quiet on the real tree.
  - The matrix drift test red on a deliberately diverged transcription.
  - The full gate. Item 11.

### Task 4 — Slice 4: the headers (docs-only)

- **Scope:** FD-1157's population re-derived at the slice's tree with the premise (f) command and
  `grep -c '^  - check 30'`:
  - headers on the 27 docs files;
  - headers on the 18 non-vendored skill manifests (DP-8 (b)), closing F92's residual on this PR;
  - the 25 vendored manifests left disclosed until F93, the maintainer's own RFC-937 amendment,
    and named as such.

  If check 30 has no template a skill manifest can match, the leaf plan says so before its first
  step, and the slice becomes code (the template registry), taking a gate slot.
- **Depends on:** nothing; DP-8 is resolved. Serialised against WK-1170's Slice 2.
- **Gate outline.**
  - `grep -c '^  - check 30'` at the merge tree, against its reading at the slice's base, with
    the difference accounted for file by file.
  - `audit-docs.py`, `doc-index.py --check` and `doc-id.py check` exit 0. Item 11.

---

## Activation

When the maintainer (or the session acting on the maintainer's behalf) accepts this plan, the
activation commit:
1. Sets this plan `status: active`. This is permitted only when every blocking Decision point
   row has a resolver id (`document-ids.md` §1.7). Otherwise the plan stays `draft`, and the
   open rows are named in the acceptance line. A slice may start while a later slice's DP is
   open (§1.7's last sentence).
2. The lead adds the four `SL-` rows under `### WK-1169`, each `draft`, with ids the lead issues.
   WK-1169 is already `active` (`docs/roadmap.md:806`).
3. `docs/INDEX.md` is regenerated in the final commit only.

## Status

- **Acceptance line:** _pending — the maintainer's dated line, or one given on the maintainer's
  behalf_.
- **Working id 9812.** `PL-9812` is a working id, taken after `git grep` over `origin/main` and
  every `origin/*` branch at `19c395ac` found no document carrying it. The lead mints the real
  id with `python3 scripts/doc-id.py next --ref origin/main` at the merge turn. Until then
  `doc-id.py check` reds this file under check 31, which is expected. `PL-9811` (WK-1170's map
  plan, draft PR #930) is cited by its working id for the same reason.
- **Resolved 2026-09-29:** DP-1 (a), DP-4 (a), DP-5 (b), DP-6 (a) in part (option D only) and
  DP-8 (b), the maintainer's by delegation at the 23:05:29 BST entry; DP-7 (b) and DP-9 (a), the
  lead's.
- **Open:** DP-2 and DP-3 (the decision-maker's, awaiting its ruling).
- **Revised 2026-09-29**, while `draft`, to record those resolutions at every site (Scope, the DP
  table, Sequencing, Tasks, Status). `created:` stays 2026-09-29, the day the plan was drafted.

## Self-review

1. **Spec coverage.** RFC-937 §8's subject, RFC-897 §5 and §11 (c), `CR-1164`'s `executor.md`
   rider, and every row the Acceptance item 6 predicate prints at `19c395ac` (14) are each in a
   Scope table with a slice. F61, FD-9640 and F92 are named with the reason each is not here.
2. **Scope boundaries.** §1.6 is read, not amended, except through `RFC-` + `RL-`. No writer
   code for artifact B (WK-1178's, via #909). No vendored skill is edited.
3. **Literals.** Every path, line, id and count in the premises and the Scope tables was read at
   `19c395ac`. Every id resolves in `docs/INDEX.md` at that tree, except the working ids
   `PL-9811` and the parallel-start ruling's 9760, each named with its open PR.
4. **Placeholders.** None. The empty `Resolved by` cells are the §1.7 form for open rows, and
   each names its resolver. There are no code steps; this is a map plan.
5. **Consistency.** The slice numbers in the Scope tables, the DP `Blocking` cells, the
   Sequencing and the Tasks agree (grep "Slice N" across the file).
