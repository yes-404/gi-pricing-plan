---
id: RL-1140
family: ruling
title: W37-8 DP-8.1 to DP-8.6 — the harness keys need a template licence and a policy-aware check 30, all seven agents are in, and F97 is drafted under lead.md's dated line
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-27
owner: decision-maker
tree: 536d3cc3bda9d1e709bf12118999ce5b09dce399
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1071, PL-939, RFC-937, RL-1138, RL-981, CR-1064, FD-1056, FD-1074]
---

# RL-1140 — W37-8 DP-8.1 to DP-8.6: the harness keys need a template licence and a policy-aware check 30, all seven agents are in, and F97 is drafted under lead.md's dated line

## Verified first, at 536d3cc3bda9d1e709bf12118999ce5b09dce399

This rules the six decision points in `PL-1071` §6 (header row `:1114`, rows `:1116-1121`).
The planner's recommendation in each row is a proposal. Each is ruled on its merits below.

Everything below was read in worktree `dm-w37-8`, branch `w37-8-dp-rulings`, cut from
`origin/main` = `536d3cc3bda9d1e709bf12118999ce5b09dce399` with a clean status. Clock at
ruling: 2026-09-27, about 00:00 BST. `PL-1071` is unchanged since it was filed:
`git log -1 --format=%H origin/main -- <PL-1071's path>` = `2f91e638` (2026-09-18, the draft
filing), header `status: draft`, `tree: a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15`. The plan
measured at `a8b3c39`; every fact below is re-measured at `536d3cc3`, with its command.

**Retired paths are described, not spelled, in this record.** "The audit tree" is the
directory `RFC-937` §1.4 dissolves; its one remaining file is `w37-11-record.md`. "The
retired findings README" is the file `RL-1138` DP-2 folded into `docs/findings/README.md`.
"The stub directory" is the notes directory under `.claude/` that `RFC-937` §5.3 deletes.

### 1. Facts re-measured at `536d3cc3`

| Plan's claim (at `a8b3c39`) | Command | At `536d3cc3` |
|---|---|---|
| DP-8.1: `REFERENCE.md` declares none of the harness keys | `grep -n "^name:\|^description:\|^tools:\|^model:" docs/_templates/REFERENCE.md; echo $?` | no lines, exit **1**. Reproduces. |
| DP-8.1: `scripts/doc-id.py:4718-4731` records the deferral | `sed -n '4710,4740p' scripts/doc-id.py` | Reproduces. The block opens at `:4718` (*"What this slice does NOT stamp"*). At `:4727` it assigns the declaration to W37-6's plan (*"W37-6's, not this slice's"*). W37-6 closed without doing it. |
| DP-8.1: `document-ids.md:136`, *"Unknown field → lint failure"* | read | Reproduces. |
| DP-8.1: W37-7 and W37-8 "run beside each other" (`PL-939:377-380`) | `gh pr list --state all` | **No longer true.** W37-7 merged as #795. It declared nothing (the grep above). `grep -L '^family: reference' .claude/skills/*/SKILL.md \| wc -l` = **46**. `python3 scripts/audit-docs.py \| grep -c 'check 30: \.claude/skills/'` = **43**. |
| DP-8.1: W37-7's acceptance names commits and a sweep, not skill headers (`PL-939:753-757`) | read | Reproduces. |
| DP-8.1: declaring the keys in the template lets a merged header parse | **three probes** in this worktree, reverted after (`git status --porcelain` empty) | **Does not reproduce.** See §2. |
| DP-8.2: seven agent files; `RFC-937` §5.3 names two; §4 step 5 stamps all of `.claude/agents/` | `ls .claude/agents/*.md`; read `RFC-937` | 8 `.md` files: seven agents plus `README.md`. `RFC-937` §5.3's agents row names the README, `ci-watcher.md` and `spec-reconciler.md`. §4 step 5 stamps *"every file under … `.claude/agents/`"*. Reproduces. |
| DP-8.2: acceptance item 1's check-30 count prints `7` | `python3 scripts/audit-docs.py \| grep -c "check 30: \.claude/agents/"` | **7**. Reproduces. Each is *"family '' has no known template"*. Each has a ceiling-1 `h1-check30` row in `w37-11-record.md` (`:192-198`) and a ceiling-1 `h1-check35` row (`:305-311`). |
| DP-8.3: F97's row and the review-13 routing | read `docs/findings/register.md:138`, `CR-1064:154`, `:542` | Reproduces. The row names two remedy shapes and chooses neither. It gives the authority as *"`.claude/roles/lead.md`, whose amendment is the maintainer's (`CLAUDE.md` §12)"*. |
| DP-8.3: `lead.md` has no F97 clause | `grep -n -i 'F97\|copy-then-write' .claude/roles/lead.md` | no lines. |
| DP-8.4: no `SL-` rows, no `slice:` field | `grep -c 'SL-[0-9]' docs/roadmap.md`; `grep -rln '^slice:' docs/plans/ \| wc -l`; `grep -n 'if header.slice_ is not None' scripts/doc-id.py` | **0**, **0**, guard at **`:7374`**. F112 (`FD-1074`, register `:151`) records this gap. |
| DP-8.5: the README's header carries `family: reference` (`:2`) and `owner: lead` (`:6`); the body says neither | `head -8 .claude/agents/README.md`; `grep -n -i 'reference\|owned by\|lead' .claude/agents/README.md` | Only `:2` and `:6` match. Reproduces. `document-ids.md:164` is the *"Reference — agents \| lead"* row. |
| DP-8.6: both further §5.3 rows were discharged in W37-6 | `git ls-files <the stub directory> \| wc -l`; `grep -n statusMessage .claude/settings.json`; `git log --diff-filter=D -1 -- <the stub directory>` | **0** tracked files. The `statusMessage` at `settings.json:12` reads *"Checking retry cap (RFC-895 C2)..."*, the post-migration id form. The deletion and the last `settings.json` edit are both `71f5a220`, W37-6's migration commit. Verified. |
| Riders (a), (e): the charter-path residue | `python3 scripts/audit-docs.py \| grep 'check 36: \.claude/roles'` | Five hits: `auditor.md:26`, `:33`, `:35` and `planner.md:50`, `:53`. All five name the audit tree. They match `w37-11-record.md:469` (auditor, ceiling 3) and `:470` (planner, ceiling 2). **The lead's brief cites this residue as `:620`. That citation did not resolve** in `PL-1071`, `w37-11-record.md`, `CR-1064` or `CR-1065` at this tree. The population is identified from the check-36 output instead. |
| Riders (b), (c): no reachability step and no copy-then-write rule yet | `grep -n 'merge-base\|ancestor\|reachab' .claude/roles/auditor.md`; the `lead.md` grep above | no lines in either. |
| D2 and the W37-8 start | read `~/gi-pricing-plan.local/channel/to-lead.md` (a local handover file, not in the repository) | `:6086-6090`: D2, deputy, 2026-09-26 17:06:12 BST. It asks for **one dated line per edited charter file**. *"The eighth file (`docs/_templates/REFERENCE.md`, if DP-8.1 rules T2 a `process/` amendment) takes the same procedure."* `:6443-6450` (23:54:10 BST) lists riders (a)–(e). Rider (d) is *"DP-8.3's F97 behavioural clause in `lead.md`"*. `:6459` (23:55:47 BST) adds an ACK/audit acceptance item. |

### 2. DP-8.1's premise does not hold: the template alone cannot license a key

The plan says the harness keys must be declared in `docs/_templates/REFERENCE.md` *"before a
merged governed header can parse"*. That is necessary. **It is not sufficient.** Three probes
at `536d3cc3` show it. In each, `.claude/agents/ci-watcher.md` got a merged header: its four
harness keys, plus `family: reference`, `title:`, `status: active`, `created:` and
`owner: lead`. Then `python3 scripts/audit-docs.py` ran:

| Probe | Template state | Result |
|---|---|---|
| 1 | unchanged | `check 30: .claude/agents/ci-watcher.md: unknown field` for each of `name:`, `description:`, `tools:`, `model:`. **Exit 1.** The file's ceiling-1 `h1-check30` row became four hits, which is a regression. |
| 2 | the four keys declared **in the commented block at the template's foot**. This is the style T2 step 3 asks for, *"the same commented style the vendored-skill block at its foot already uses"*. | the same four failures. **Exit 1.** |
| 3 | the four keys declared **in the template's top-level `---` block** | the same four failures. **Exit 1.** |

The cause is in the code, read at the same tree:

- `scripts/_docid.py`, `parse_header`: any key outside the hard-coded `_KNOWN_KEYS` goes
  into `header.extra`. The docstring says whether an extra is *permitted* is *"a
  family-aware policy check (`audit-docs.py` check 30), not this generic parser's to
  enforce"*.
- `scripts/audit-docs.py`, check 30: `for extra_key in header.extra: fail(... unknown field
  ...)`. This is **unconditional**. The family's derived policy is never consulted for an
  extra.
- `derive_field_policies()` at `536d3cc3` gives the reference family
  `permitted = {corrected_by, created, family, owner, relates, status, title, tree}`. It is
  read from the template's top-level block only. So the commented foot licenses nothing:
  probe 2's form cannot work, whatever check 30 does. The same holds for the template's
  `vendored:` and `origin:` lines. Those two pass today only because they are in
  `_KNOWN_KEYS`. That is disclosed here and is not part of this ruling.
- `python3 scripts/doc-id.py check` exits **0** under probe 3. That tool does not police
  extras. The failing instrument is check 30 alone.

This is a `CLAUDE.md` §0 disagreement between code and spec. On one side are
`document-ids.md` §1.5 (*"declared in that family's template and permitted only there"*),
`RL-981` §2 item 1 (*"the permitted set for a family is the set of keys in that family's
template front matter"*) and `parse_header`'s own docstring. On the other is check 30, which
treats every extra as unknown. **Ruled: the code is wrong.** §1.5, `RL-981` and the parser
agree with each other. Check 30's loop is the outlier. It is also the only site where the
template-as-licence rule was never applied. The comment above `_docid.py`'s template readers
says the template is the licensing instrument, *"never a hand-written constant in a
reader"*.

## Ruled

### DP-8.1 — who declares the harness keys: **(a) adopted, amended**

**The prior question first.** Editing `docs/_templates/REFERENCE.md` to declare these keys is
**not** a maintainer amendment. There are three reasons:

1. `CLAUDE.md` §12 reserves to the maintainer *"an amendment to what this file requires"*
   (`CLAUDE.md:236`). "This file" is `CLAUDE.md`. T2 does not touch it.
2. `docs/_templates/` is not `process/`. The Reference family's path list
   (`document-ids.md:49`) names `process/`, `contracts/`, READMEs, charters, skills and
   agents. It does not name `_templates/`. The *"Reference — `process/`"* row
   (`document-ids.md:161`, amendments by `RFC-` + `RL-`) therefore does not reach it.
3. §1.5's operative clause names the template as the place a family's extras are declared.
   Declaring them there **implements** §1.5. It does not change §1.5. Rulings have edited
   templates before: `RL.md` under #661 (`a8b31ab8`) and `CR.md` under #804 (`536d3cc3`).

**The limit.** If T2 needs to change the *text* of `document-ids.md` §1.5, that is a
`process/` amendment. It needs an `RFC-` + `RL-` pair and is outside W37-8. The executor
stops and reports. **Consequence for D2:** D2's conditional eighth file does not arise.
`REFERENCE.md` gets no dated maintainer line, and item 3's count is the edited files under
`.claude/roles/` only.

**Why (a).** (b) is moot: W37-7 merged as #795 and declared nothing. (c) adds a PR in front of
a slice that cannot pass its own acceptance item 1 without the change. (d) is refused for the
reason the plan gives (`CLAUDE.md` §2: a shape defined twice will diverge).

**Amendments, all binding on T2:**

1. **The keys go in the template's top-level `---` block**, not the commented foot. Probe 2
   shows the foot is not read. The template's leading comment gains one sentence. It says
   the four keys are for files the Claude Code harness consumes (`.claude/agents/*.md`,
   `.claude/skills/*/SKILL.md`). It also says they are permitted, never required. That
   already holds by construction: `required = _CORE_HEADER_FIELDS ∩ permitted`, and none of
   the four is core.
2. **T2 also fixes check 30, in the same commit** (`CLAUDE.md` §2: spec, code and tests in
   one commit). An extra fails only when it is **not in the file's family policy**:
   `extra_key not in policy.permitted`. **The four names are not added to
   `_docid._KNOWN_KEYS`.** That would license them for every family, through a hand-written
   constant — the second copy that `RL-981` §2 item 1 refuses.
3. **T2 gains a test**, in the check-30 module of `tests/test_audit_docs_ids.py`, with
   three cases:
   - a Reference file with the declared keys passes;
   - a Reference file with an undeclared key (T2 step 5's `colour: red`) still fails;
   - a non-Reference file (for example an `RL-`) carrying `tools:` still fails, because
     the licence is per family.
   T2's `Files:` gains `scripts/audit-docs.py` and that test module. The executor loads
   `python-test` for T2 as well as `writing-skills`. The full gate's Python half then
   covers T2. Item 4 already requires it.
4. **The ordering is fixed: the harness keys stay first, unchanged, and the governed keys
   follow them.** Each agent file's existing lines stay byte-identical, so the merge is a
   pure insertion. Probe 1 shows `parse_header` reads `ci-watcher.md`'s quoted, colon-bearing
   `description:` without a `HeaderError`. That was checked on that one file only. T3 and T4
   check each file.
5. **The owner is `lead`** on every agent file (`document-ids.md:164`). That also clears
   each file's `h1-check35` row.

**Not verified here, and said so.** No probe showed that the Claude Code harness still loads
an agent whose front matter carries the governed keys. T3 must show that once, on
`ci-watcher.md`, before T4 repeats the merge on six files. For example, a fresh session
lists the agent with its description intact. If it does not, the executor stops and reports.

### DP-8.2 — which agent files: **(a) adopted**

All seven. `RFC-937` §4 step 5's stamp set is the directory. §5.3's two names are the ones
that also need a citation edit, not the whole population. (b) would leave five ceiling-1
`h1-check30` rows owned by no slice. The plan's reason holds, and so does its predicate:
acceptance item 1's `grep -L` runs over the whole directory.

### DP-8.3 — F97's disposition: **(a) adopted — drafted in W37-8, under the lead.md line**

The planner recommended (b), a dated decline. That followed plan review 13's *"disclosed
candidate, not scope"*. The scope authority has since decided otherwise. The deputy, acting
by the maintainer's delegation, listed *"DP-8.3's F97 behavioural clause in `lead.md`"* as
rider (d). The planner adds it as a W37-8 scope row (`to-lead.md:6443-6450`, 23:54:10 BST).
The maintainer is the scope authority (`document-ids.md` §1.6, principles). A ruling that
declined what the scope authority has just scheduled would be the "not decided here, decided
anyway" pattern `CR-1064:154` warns against. So (a) is ruled, with these limits.

**The limit, stated.** `CLAUDE.md` §12 reserves only amendments to `CLAUDE.md` itself.
F97's register row cites §12 for a `lead.md` amendment, and that citation is loose. The
authority for a charter is `document-ids.md:162`: *"Reference — charters | maintainer; 'a
role file that proves insufficient' → `FD-` → maintainer amends"*. `CLAUDE.md` §15 says the
same. So:

1. **A new obligation in a charter is a maintainer amendment.** That covers the F97 clause
   (rider (d)), the copy-then-write rule (rider (c)) and the reachability step (rider (b)).
   `RFC-937` §5.3's role content is different. It implements an RFC the maintainer has
   already accepted (the same reasoning as `RL-1138` DP-6). D2's per-file line is the
   maintainer's line for both kinds.
2. **The line for `lead.md` must name each new obligation by clause.** It approves or
   rejects each one separately: the F97 clause, and the copy-then-write clause. The same
   applies to the reachability step in `auditor.md`'s line. The deputy can approve a file's
   role content and still reject one of its clauses. **The count stays one line per file**,
   so item 3's test is unchanged. A clause that the line names and approves meets item 7's
   *"a drafted `lead.md` clause with its own maintainer line"*.
3. **If the line rejects the F97 clause,** the clause comes out of the diff. Item 7's second
   limb then applies: a dated decline on the PR that names the event carrying F97 forward.
4. **This ruling does not choose between F97's two shapes.** One is a halt-protocol clause
   for the shared checkout. The other is a successor-side precondition check. Choosing is
   the content of a charter amendment, so it is the maintainer's. The executor drafts one
   shape, and the PR body names which one. The clause must not restate or amend `CLAUDE.md`
   (`PL-1071` §1.4; that is W37-9's).
5. **Drafting the clause does not close F97.** F97's row sets its own falsifiable condition:
   a zero-byte `.git/index.lock` planted on a clean tree yields a named report. That
   condition governs the auditor setting F97 `closed`. It is not a W37-8 acceptance item.

### DP-8.4 — no `slice:` field: **(a) adopted**

This follows `RL-1138` DP-4 on the same facts, re-measured: 0 `SL-` rows, 0 `slice:`
fields, guard at `scripts/doc-id.py:7374`. With the field omitted, the header is clean. A
`slice:` value with no `SL-` row would fail at `:7376`. The `SL-` rows for WK-697 belong to
F112's carrier (`FD-1074`), not this plan.

### DP-8.5 — the agents README's body: **(a) adopted, amended**

`RFC-937` §5.3's verb is *"names"*, and a README is read by people. Front matter is state
kept for machines. **Amendment:** the body sentence **cites** `document-ids.md` §1.6's
*"Reference — agents"* row as the authority. It does not state "the lead" as a free-standing
value. The header's `owner:` then records the same row the sentence cites. The sentence is
not a third copy that could fall out of step with the other two (`RFC-756`).

### DP-8.6 — the settings and stub-directory rows: **(a) adopted, verified now**

Both rows were discharged by `71f5a220` (§1). The exclusion may be relied on now. T1
step 3 still runs its check, which takes seconds. If that check disagrees with §1, this row
reopens.

### Interaction with the riders (not ruled here)

- **(a) `auditor.md:35`, and (e) the residue.** Rewriting `:26`, `:33` and `:35` in T7, and
  `planner.md:50` and `:53` in T11, lowers those files' check-36 counts below their ceilings
  (3 and 2). That is the non-fatal `RESIDUE_PROGRESSED` outcome. **W37-8 does not edit
  `w37-11-record.md`.** The shrink belongs to its owner, W37-11 (`RL-1138` DP-1). Any
  legacy-form hit in a charter with no row in that record is a fatal `RESIDUE_REGRESSION`.
  Those charters are `decision-maker.md`, `executor.md`, `lead.md`, `reporter.md` and
  `watcher.md`. Retired paths go into the rewritten charters as descriptions, and the new
  destinations are spelled in full.
- **(b), (c), (d)** are charter amendments under DP-8.3's limit 1. Each is named in its
  file's D2 line (limit 2).
- **The self-referential hazard** (`PL-1071` §2) now includes this role. T8 edits
  `decision-maker.md`. This ruling decides nothing about that file's content.

## What it obliges

- **The planner**, in the activation PR on this branch, writes `RL-1140` into the six
  `Resolved by` cells of `PL-1071` §6. The planner rewrites T2 to DP-8.1's five amendments:
  `Files:`, step 3's location (the top-level block), the check-30 fix and test, the added
  skill, and the ordering. The planner adds T3's harness-load check, the rider rows and the
  deputy's ACK/audit item, and then moves the plan to `active`. Per `document-ids.md`'s `PL`
  row, the decision-maker does not edit the plan.
- **The executor** follows DP-8.1's amendments and DP-8.3's limits 2–4. It edits no
  `.claude/skills/` file and does not edit `w37-11-record.md`. It stops and reports if T2
  needs a change to the text of `document-ids.md` §1.5.
- **The deputy (D2)** writes one line per edited `.claude/roles/` file. The `lead.md` and
  `auditor.md` lines name each new-obligation clause and approve or reject it separately.
  No line is needed for `REFERENCE.md`, the agent files or the agents README, because none
  is a charter.
- **The lead** is told of two things this ruling does not own:
  1. **The 46 unheaded `SKILL.md` files are owned by no slice.** W37-7 has merged. Its
     acceptance never named skill headers. `PL-1071` §1.4 excludes `.claude/skills/`, and
     at `536d3cc3` 43 check-30 lines point at them. The T2 licence will serve them, but
     stamping them needs an owner. That is for the lead and the planner.
  2. **`vendored:` and `origin:` are licensed by `_KNOWN_KEYS`, not by the template.** The
     template's claim *"declared here and nowhere else"* is therefore not what the code
     does (§2).

## Acceptance — the violation that must become detectable

The violation: a merged agent header that passes only because check 30 stopped policing
extras, or a harness key that becomes legal for every family.

- **DP-8.1 (a).** At W37-8's merge tree, `python3 scripts/audit-docs.py | grep -c 'check 30:
  \.claude/agents/'` prints `0`. *Violation: any count above 0.*
- **DP-8.1 (b).** T2's test case 2 reds on a Reference file carrying `colour: red`, and
  case 3 reds on a non-Reference file carrying `tools:`. *Violation: either case passes.*
  The executor shows each case red before the fix, per `CLAUDE.md` §13.
- **DP-8.1 (c).** `grep -n '"tools"\|"model"\|"description"' scripts/_docid.py` has no hit
  inside `_KNOWN_KEYS`. *Violation: a hit there*, which would mean the licence moved into a
  constant.
- **The red half is already shown.** This ruling's probes 1–3 printed the unknown-field
  failure and exit 1 on deliberately broken input (§2). The green half is T2's to show.
- **DP-8.2.** `grep -L '^family: reference' .claude/agents/*.md` prints nothing.
  *Violation: any file named.*
- **DP-8.3.** No mechanical check exists. The lead verifies at the PR that every added
  `lead.md` clause is named in the deputy's `lead.md` line. *Violation: an added
  obligation that no line names.*
- **DP-8.4.** `grep -c '^slice:' <PL-1071's path>` prints `0`, and `python3 scripts/doc-id.py
  check` exits 0. *Violation: a `slice:` field with no `SL-` row*, which fails at
  `scripts/doc-id.py:7376`.
- **DP-8.5.** `sed -n '9,$p' .claude/agents/README.md | grep -c 'Reference — agents'` prints
  at least `1`. *Violation: `0`*, meaning the body names neither the family nor the
  owner's authority.
- **DP-8.6.** `git ls-files <the stub directory> | wc -l` prints `0` at the merge tree.
  *Violation: any tracked file there.*
