# W37-6's leaf-plan findings: what only Rulings 66 and 69's author can fix — Rulings 73-78 (2026-09-02)

**What this is.** Six rulings on the findings W37-6's leaf plan filed in its §10 against the
records this role wrote — [Ruling 66](2026-09-02-w37-migration-preconditions-rulings.md) (DP-1,
the creating-instrument set) and [Ruling 69](2026-09-02-w37-migration-preconditions-rulings.md)
(the vendored criterion). Four were routed here because a defect in a ruling's acceptance item
can only be amended by that ruling's author; two were routed as judgement calls that might not
be rulings at all. Both of the latter turned out to be rulings, and both are taken here.

**Authority.** [`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md)
§1 grant 1: the lead may route a technical question to this role and its ruling stands as the
maintainer's. §2 bounds that grant — not a fact only the maintainer holds, not acceptance of a
Work, Phase or Project close, not an amendment to `CLAUDE.md`. Every item below sits inside
those bounds. §7 records what was referred up instead of ruled.

**Ruling numbers, derived rather than relayed.** At `e93e0e4`:

| Derivation | Command | Result |
|---|---|---|
| Highest minted ruling heading | `git grep -oh -E '^#{2,3} Rulings? [0-9]+' origin/main -- .` | max **72** |
| Nothing above it anywhere | `git grep -oh -E 'Ruling 7[3-9]\|Ruling [89][0-9]\|Ruling 1[0-9][0-9]' origin/main -- .` | empty |
| No other branch could hold one | `git for-each-ref refs/remotes/origin` | `origin/main` only |

**73 through 78 are therefore free, and are used in that order.** The two branches that existed
when this work was dispatched — `docs/w37-6-migration-run-leaf-plan` and
`audit/f74-reporter-charter-nudge-signal` — have both merged and been deleted since; the first
merged as `e93e0e4` **while this record was being written**, so W37-6's leaf plan is a filed,
frozen document here rather than an open pull request, and is cited as such.

---

## 1. Verification first — and three things the plan reports that do not hold

Every claim below was checked against the artifact at `39ee30c`/`e93e0e4`, never against the
lead's relay or the plan's description. Three of the plan's own claims did not survive that
check, and each changes a remedy.

| # | Claim under test | Verdict |
|---|---|---|
| V1 | No check in 30-39 examines a branch name or a PR title | **Confirmed, and structurally so.** `scripts/audit-docs.py` contains no `subprocess`, no `os.environ`, no `GITHUB_`, no git invocation of any kind — it cannot read a branch or a PR at all. Check 39's `check_index_stable` states the omission in three places and its PR clause is an unconditional `notes.append`; check 38 has zero `fail(` calls in its body |
| V2 | Reverting a non-member produces an item-(d) hit | **Confirmed and quantified.** 928 of 1447 tracked files carry at least one legacy form. Measured by calling the **shipped** `sweep_legacy_forms` with the shipped `LEGACY_FORM_PATTERNS` on each tracked file (Ruling 67 acceptance item 2: never a re-typed copy of the pattern) |
| V3 | The test also **fails for real members** | **Confirmed — and the plan does not report this direction.** Four of its thirteen members carry **zero** legacy forms. Ruling 73 §1 has the table |
| V4 | `docs/_templates/REFERENCE.md` contradicts Ruling 69 | **Confirmed**, lines 39-49, in the words Ruling 69 rejected |
| V5 | "The template landed in W37-1, **before** Ruling 69" | **Refuted.** Ruling 69 (`#563`) merged `2026-09-02T00:30:56Z`; W37-1 (`#562`) merged `00:38:22Z`, seven and a half minutes **later**, and `9d33c60` is an ancestor of `553bbef`. The PR numbers invert the merge order. Ruling 76 §1 |
| V6 | Ruling 69 §3's obligation list is what let it survive | **Refuted, and the real state is worse.** `scripts/_docid.py`'s `is_vendored` **still implements the rejected rule** at `e93e0e4`; `_VENDORED_SKILLS` does not exist anywhere in the tree. W37-2 (`#567`, merged `01:05:19Z`) was named in that obligation list **by name** and shipped without discharging it. Ruling 76 §1 |
| V7 | `closure-records.md`: "three of its 21 `###` records are marked *in progress, not closed*" | **Refuted. There are ten.** Lines 1862, 1904, 1982, 2014, 2073, 2107, 2160, 2223, 2269, 2343, each carrying `*(in progress, not closed)*` verbatim. Ruling 78 §1 |
| V8 | One of the 21 is a phase rather than a work | **Confirmed** (line 8, `### Phase 1a — exit demo accepted 2026-08-15`) — **and two more are neither a work nor a phase close**: line 1121 `### Independent audit — 2026-08-15, and what it changed` and line 1555 `### W4 mid-workstream scope findings — 2026-08-14`. Only **8** of the 21 are work closure records |
| V9 | `.claude/roles/auditor.md` carries four `docs/audit/` paths in one bullet | **Confirmed as to the bullet, incomplete as to the file.** The file names **six**; the other two — `docs/audit/findings/<F-id>.md` and `docs/audit/findings/README.md` — sit in the next bullet |
| V10 | `NT-0019` D10 calls charters *"the creating instruments"* in as many words | **Confirmed in substance, overstated as a quotation.** D10 reads: *"Charters, skills and agents carry the header \| They are the `owner:` vocabulary and the creating instruments."* The phrase attaches to the three-member group; it does not single charters out. The conclusion survives, the quotation should not be re-cited in its stronger form |
| V11 | Two of `docs/audit/`'s 43 files have no §5.2 destination row | **Confirmed**, and they are the two named. §5.2's eight `docs/audit/` rows cover 41 by exact name or glob |
| V12 | 72 ruling headings across 29 files | **Confirmed** under the `##`/`###` reading. The literal regex returns 87 across 42 — the extra 15 are 12 Python source comments (`#` collides with h1) and 3 single-ruling documents whose own title is the heading |

**On the one number I could not reconcile.** The plan reports **930** files carrying a legacy
form at `39ee30c`; the method above returns **928**. The plan does not state its method, so the
two-file difference cannot be attributed. It bears on no finding here — the discrimination
failure in Ruling 73 §1 holds at either figure — but the executor re-derives it in the running session
rather than inheriting either number, as the plan's own §5.4 already requires for acceptance (f).

---

## Ruling 73 — Ruling 66's acceptance item 2 is withdrawn: it is wrong in both directions and blind to omission, and the replacement tests H content in two limbs

### 1. The defect, measured

Ruling 66 acceptance item 2 reads:

> **Implementation-facing.** For each instrument in the derived set, restoring that one file to
> its merge-base content and re-running W37-6's acceptance sweep must produce at least one hit
> naming that file. **Violation: an instrument whose reversion changes nothing any check can
> see** — it is either out of scope or its edit was cosmetic, and either way the set was derived
> wrong.

Measured at `39ee30c` by calling the shipped `sweep_legacy_forms` on each file:

| Direction | Files | Hits | What item 2 concludes |
|---|---|---|---|
| **False positive** — non-members that pass | `repo-architecture` 13 · `dev-commands` 10 · `git-hygiene` 10 · `CLAUDE.md` 24 · `lead.md` 9 · `watcher.md` 6 · `executor.md` 1 · `reporter.md` 1 | all `>0` | "in scope" — for eight files the plan explicitly excludes, and for the 911 further carriers that are neither |
| **False negative** — members that fail | `decision-maker.md` 0 · `writing-skills/SKILL.md` 0 · `brainstorming/SKILL.md` 0 · `subagent-driven-development/SKILL.md` 0 | all `0` | "out of scope or cosmetic, and either way the set was derived wrong" — **remove them** |

Three defects, not one.

1. **It passes for non-members.** NT-0019 §4 step 6 rewrites citations across *"the whole tree
   — `git ls-files`, nothing exempt"*, so reverting any of the 928 carriers restores a legacy
   form that acceptance item (d)'s tree-wide sweep returns. The test measures *"is this file in
   the migration commit"*, which the **M** row already guarantees for all 928, rather than *"was
   its instruction content corrected"*, which is what DP-1 is about. This is the direction the
   leaf plan's §10 finding 12 reports, and it is correct.
2. **It fails for members — the direction the plan does not report, and the worse one.** Four of
   the thirteen adopted members carry no legacy form at all, so their reversion produces no
   item-(d) hit and item 2's stated verdict is to strike them. One of the four,
   `subagent-driven-development`, is not a marginal addition: it is one of the seven **primary**
   instruments NT-0019 §5.4 names and the map plan's own floor. A false positive wastes a proof;
   a false negative removes an instrument from the single commit DP-1 exists to fill.
3. **It has no under-inclusion limb at all.** Item 2 quantifies over *"each instrument in the
   derived set"*. Ruling 66's whole point was that *"seven is the floor, not the ceiling"* — the
   risk the criterion exists to manage is **omission**, and a test that ranges only over the
   members it is handed can never detect the member it was never handed. The leaf plan's §6.4
   found six additional members by running a second method; item 2 would have reported nothing
   about the absence of any of them.

**The defect does not depend on how "acceptance sweep" is read.** Under the narrow reading it is
acceptance item (d), the legacy-form sweep, and the table above applies. Under a wide reading —
all of (a) through (h) — it is *less* discriminating still, because reverting any tracked file
changes (g)'s diff. Neither reading yields a test that separates a member from a non-member.

### 2. Ruled

**Ruling 66 acceptance item 2 is withdrawn.** Ruling 66 §2 (option (a) chosen; (b) and (c)
rejected), the criterion in its §2 closing paragraph, its §3 obligations and its acceptance item
1 all stand unchanged and unaffected. Only item 2 is replaced.

**Ruling 66 acceptance item 2, as amended 2026-09-02.** The subject of the test is the
instrument's **H content** — the filename, id, directory, header-field or section form it
teaches — never the file, and never its citations.

- **2a — over-inclusion.** For each member of the derived set: revert **only** its H content to
  the merge-base form, leaving its rewritten citations in place; produce the document that
  instrument mints, by following the reverted instruction literally; run
  `python3 scripts/audit-docs.py`. **Violation: no check in 30-39 fires on that document.**
- **2b — under-inclusion, the limb item 2 lacked.** The same proof is run over the plan's
  **explicit exclusion list**, which must be exhaustive rather than a sample. For each excluded
  instrument: revert its H content, produce the document it mints, run the audit. **Violation:
  any check in 30-39 fires** — the exclusion was wrong and the instrument belongs in the commit.
- **2c — neither list.** **Violation: an instrument that appears in neither the adopted set nor
  the exclusion list.** This promotes W37-6's own §6.4 sentence from prose to an acceptance item;
  it is the only limb that can catch a member nobody thought of.

**One exemption, and it is stated here rather than discovered.** A member for which no check
fires under 2a is admitted **only** if the plan already states a non-check ground for it **by
name**. Exactly one such statement exists: `.claude/skills/README.md`, adopted on `CLAUDE.md`
§12 (*"update the README, commit both with the work"*), which mints no document. A ground
discovered while running the proof is a finding against the derivation, not an exemption.

**The plan's second exemption is not adopted.** W37-6's Acceptance Standard item 11 also exempts
`brainstorming`, on the ground that its correction *"removes a `docs/` path rather than replacing
one, so there is no document to produce from the reverted form."* That reason is incorrect: the
reverted H content is an instruction to save a design document at
`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, which is a document, at a path under
`docs/`, and NT-0019 §4 step 5's stamp set — *"every file under `docs/`, `.claude/roles/`,
`.claude/skills/*/SKILL.md`, `.claude/agents/`"* — reaches it once acceptance item 10's flip
lands. 2a therefore applies to `brainstorming` unmodified, and its result is recorded either way.

### 3. Why the H-content form and not something cheaper

DP-1's failure mode is an author following a stale instruction and filing a document the gate
reds. The only faithful test is to **be** that author: follow the stale instruction, produce the
document, run the gate. Every cheaper proxy — is the file in the commit, did its diff change,
does it contain a legacy token — is a shadow of that property, and the three defects measured in
§1 are what that shadow costs. Item 2 chose the proxy because it was cheap to run at the console;
the H-content form costs one produced document per member and is the thing actually in question.

### 4. What it obliges

- W37-6's Acceptance Standard item 11 is the discriminating form and stands as written, with
  `brainstorming`'s exemption removed and 2b and 2c added. The plan's §7.12 sub-item already
  schedules the per-member proof for members 1 to 11; **2b extends it to every entry in the
  exclusion list**, and 2c to the re-run enumeration §7.12 already schedules.
- The ledger records, per instrument, which check fired and on what produced document — not that
  the proof passed. A verdict with no named check is the same silence item 2 produced.

### 5. Acceptance — the violation that must become detectable

1. **The amendment must itself be falsifiable on the corpus that falsified item 2.** Run 2a over
   `.claude/roles/decision-maker.md`, `.claude/skills/writing-skills/SKILL.md` and
   `.claude/skills/subagent-driven-development/SKILL.md` — the three zero-hit members with a
   document to produce. **Violation: any of the three producing a document on which no check in
   30-39 fires.** If one does, that member's ground is wrong and it is re-derived, not waived —
   these are exactly the three item 2 would have struck, so a green result here is the whole
   point of the amendment.
2. **2b must be able to fail.** Run 2b over `git-hygiene`, `dev-commands` and `repo-architecture`
   — the three named exclusions that item 2 wrongly admitted. **Violation: any check in 30-39
   firing on a document produced from their reverted H content.** A limb that has never returned
   a candidate has not been tested, and this is the corpus's own control for it.

---

## Ruling 74 — `git-hygiene` is excluded, the criterion is applied correctly, and the window is narrower and more permanent than the plan discloses

### 1. Verified

Ruling 66 named `git-hygiene` a candidate *"on the strength of check 39's branch and PR-title
grammar"*. That premise is false, and the falsity is structural rather than incidental.

| Claim | Verdict |
|---|---|
| Check 39 does not check the PR-title clause | **Confirmed.** `check_index_stable`'s executable body touches only `docs/INDEX.md` and `_doc_index.build_corpus`. The clause is an unconditional `notes.append`: *"check 39: PR-title/ledger cross-reference needs GitHub PR context this tree-snapshot tool does not have, and `docs/ledgers/` does not exist in scope yet — not checked here"* |
| Check 38 is warn-only | **Confirmed.** Zero `fail(` calls in `check_loop_signal`; its body is one `notes.append` |
| No check in 30-39 reads a branch or a PR | **Confirmed — and no check in the script can.** `scripts/audit-docs.py` has no `subprocess`, no `os.environ`, no `GITHUB_`, no git invocation anywhere in the file. This is not a scoping gap a later slice narrows; the tool has no capability to read either |
| `git-hygiene`'s taught grammar is invalidated by the migration | **Refuted.** Its only branch grammar is `git checkout -b <type>/<short-slug>` with examples `docs/…`, `feat/…`, `chore(…)/…`, `spike/…` — **no work-id component**. Its PR-title material is Conventional Commits plus the rule that the merge API appends no `(#N)` for you. Neither mentions a work key. The `w32-11-certfloors` string elsewhere in the file is a `git stash push -m` tag, not a branch name |

### 2. Ruled

**The exclusion is confirmed.** Under Ruling 66's criterion as ruled — *every instrument whose
output is **checked** by checks 30-39* — `git-hygiene` is not a member. Its output is a branch
name and a PR title, neither of which is a tracked file, and no check in the family reads either.
The plan applied my criterion correctly to a candidate my own premise had misdescribed, and it
disclosed the consequence rather than quietly dropping the candidate. That is the behaviour
Ruling 66 asked for.

**And the exclusion is right on a second, independent ground the plan does not claim: there is
nothing stale in `git-hygiene` to fix.** Its branch and PR grammars are generic and survive the
migration byte-for-byte. An instrument that teaches nothing the migration retires has no H
content to move, so adopting it would add a member with an empty edit — which is the failure
Ruling 66 acceptance item 2 was reaching for and, under Ruling 73's 2a, the correct verdict.

### 3. What happens to the window — and it is not the window the plan describes

The plan discloses: *"between this commit and W37-7 there is no valid instruction for naming a
branch or a PR title, because the work keys the current grammar names (`w37-7-…`) no longer exist
after the roadmap restructure."* **That window does not exist**, because `git-hygiene` states no
work-key-bearing grammar for either. A slug an author happens to build from a work key is a free
choice under `<type>/<short-slug>`, not a taught form, and a branch name is not a tracked file.

**What is real is a different and more permanent gap, and it is worth naming precisely because
it will otherwise be planned as a small task.** NT-0019 §1.11 wants a merged PR's title to name
its `SL-` and the slice's ledger to record the PR. After W37-6 that instruction lives in the note
and in no instrument, and `audit-docs.py` cannot enforce it at any scope. Two consequences:

- It is **not** a W37-6-to-W37-7 window. It opens when the standard lands and stays open until
  some instrument teaches the form — which NT-0019 §5.4 already assigns to `git-hygiene`'s H row
  in W37-7. Nothing about this slice's boundary changes it.
- Making check 39's PR clause live requires giving `audit-docs.py` a capability it does not have
  (git or GitHub access) or moving the check elsewhere. **This is a decision, not an
  implementation detail, and no one has taken it.** It is not W37-6's and this record does not
  take it: it is a later slice's decision point, raised here so it is scheduled rather than
  discovered.

**The sequencing question — whether W37-7 runs immediately after W37-6 with `git-hygiene` first
in its order — is the lead's, not this role's.** The plan says so and is right. This ruling
removes the argument that made it urgent.

### 4. Acceptance — the violation that must become detectable

1. **The exclusion must be re-testable, not asserted.** `git-hygiene` is in the exclusion list, so
   Ruling 73's limb **2b** runs over it: revert its H content, produce the document it mints, run
   the audit. **Violation: any check in 30-39 firing.** If one does, this ruling is wrong and
   `git-hygiene` is adopted. Because its output is a branch name rather than a document, the
   executor records *"no document to produce"* with the reason — which is itself the evidence
   for this ruling, and the ledger carries it in that form rather than as a silent pass.
2. **The gap must not be re-described as closed.** After W37-6, `git grep -n 'SL-' -- .claude/`
   returns no line that teaches an author how to title a PR. **Violation: a closure record, plan
   review or ledger asserting that NT-0019 §1.11's PR-title clause is enforced, satisfied or
   discharged before an instrument teaches it and a check reads it.** A note printed by check 39
   is not enforcement, and the plan's own §7.4 already requires both check 38 and check 39's PR
   clause to be recorded in the ledger as *known non-enforcing*.

---

## Ruling 75 — the three charters are within the planner's delegated derivation and need no ruling; they are confirmed anyway, and `auditor.md` has six paths, not four

### 1. Verified

| Claim | Verdict |
|---|---|
| No skill among the 46 mints a ruling record | **Confirmed.** `git grep -n 'RL\.md\|RL-' -- .claude/ docs/_templates/` returns hits only inside `docs/_templates/`. Zero in any `SKILL.md` or any `.claude/roles/*.md` |
| Nothing routes an author to `docs/_templates/RL.md` | **Confirmed.** `adr-write` — one of `decision-maker.md`'s three mandatory skills — contains no occurrence of "ruling" at all; it covers `docs/adr/` only. `decision-maker.md` has no occurrence of `_templates` |
| `docs/_templates/RL.md` exists and prescribes the post-migration form | **Confirmed:** *"Copy this file to `docs/rulings/RL-<nnnnn>-<slug>.md`"* |
| `docs/rulings/` is empty and every real ruling lives in `docs/plans/` | **Confirmed.** Zero tracked files under `docs/rulings/` at `e93e0e4` |
| The `RL-` window is occupied | **Confirmed.** 72 ruling headings across 29 files, and this record adds six more |
| `planner.md` files the §14 review at a path this commit deletes | **Confirmed**, line 22: *"filed to `docs/audit/plan-reviews.md` as a dated `### Plan review N` section"*, and its Tools bullet names the same path |
| `auditor.md` carries four `docs/audit/` filing paths in one bullet | **Confirmed as to the bullet; the file names six.** §1 V9 |

### 2. Ruled

**This is the planner's delegated derivation, not a decision reserved to this role, and it needed
no ruling to proceed.** Ruling 66 §2 made the set *"a criterion, not a list"* and §3 obliged
*"W37-6's leaf plan carries a section deriving the instrument set from checks 30-39."* Adding a
member the criterion selects is executing that delegation. The plan was right to add the three
and did not need to ask; asking cost nothing and this paragraph is the answer for the next time.

**All three are nevertheless confirmed as members, on the criterion.**

- **`.claude/roles/planner.md`.** Its output is a `CR- kind: review`. Its instruction files that
  document at `docs/audit/plan-reviews.md` under a `### Plan review N` heading — a directory this
  commit deletes and a heading form no template declares. Following it after the flip produces a
  document that reds checks 30, 31 and 37. In scope.
- **`.claude/roles/auditor.md`.** Its output is a `CR- kind: work`/`phase`, an `FD-` and an
  `RS- kind: audit`, and it names six paths into the dissolving tree. In scope, **and the fix
  covers all six.** W37-6's task list says *"all four `docs/audit/…` filing paths in its one
  bullet"*; taken literally that strands `docs/audit/findings/<F-id>.md` and
  `docs/audit/findings/README.md` in the next bullet. Sweep the file, not the reported bullet.
- **`.claude/roles/decision-maker.md`.** Its output is the `RL-` — and it is a member *because* it
  teaches no form, which reads backwards on a first pass and is right. An instrument that teaches
  a wrong form fails loudly at the first document; one that is silent routes the author nowhere,
  and after this commit *"recorded as dated sibling records"* produces a headerless file in
  `docs/plans/` that reds check 30 (no header) and check 31 (directory ≠ family). In scope.

**This record is that defect's own exemplar, and the evidence is free.** It is a ruling. It is
filed at `docs/plans/2026-09-02-<slug>.md`, as a dated sibling of a plan, with no header block —
because that is what the charter says and because `docs/rulings/` does not exist yet. It is
exactly the document Ruling 73's limb 2a asks the executor to manufacture, produced here in the
ordinary course by the role the charter governs. The executor may cite it rather than build one.

**A correction to the plan's supporting quotation, so it is not re-cited in the stronger form.**
NT-0019 D10 reads *"Charters, skills and agents carry the header \| They are the `owner:`
vocabulary and the creating instruments."* The phrase attaches to the three-member group, not to
charters alone; the plan's *"D10 calls charters 'the creating instruments' in as many words"*
overstates it. The conclusion survives on D10's own text — charters are inside the group named —
and does not need the stronger reading, so the weaker and accurate one is what this record uses.

### 3. What it obliges

- The `decision-maker.md` edit is a **routing sentence**, not a rewrite: it names
  `docs/_templates/RL.md` and `docs/process/document-ids.md` §1.6 and replaces *"dated sibling
  records"*. The template already carries the correct instruction and is already migrated.
- The `auditor.md` edit covers **six** paths. The verification is a grep of the merged file for
  `docs/audit/`, returning nothing — not a count of bullets.
- **Add a third party to the dependency check W37-6 already schedules.** The plan asks which of
  `close-workstream` and `auditor.md` ends up holding the `FD-` essay's header and shape.
  Measured: `close-workstream/SKILL.md` does **not** state the `docs/audit/work/<id>/README.md`
  closure-record path — `auditor.md` states it, and so does `.claude/skills/docs-audit/SKILL.md`,
  which the plan excludes to W37-7 as a *reading* instrument. The exclusion may well be right,
  but the executor records where each of the three forms actually ends up, so W37-7 does not
  later remove one from a file on the assumption that another holds it.

### 4. Acceptance — the violation that must become detectable

1. **The `RL-` route must work end to end for a document produced by the charter alone.** After
   W37-6, an author following **only** `.claude/roles/decision-maker.md` files the next ruling
   record, and `python3 scripts/audit-docs.py` runs on it before any hand correction.
   **Violation: check 30, 31, 33 or 37 firing on it.** This is Ruling 66 acceptance item 1's form,
   applied to the family whose window is most occupied.
2. **No `docs/audit/` path may survive in a charter.** **Violation:**
   `git grep -n 'docs/audit/' -- .claude/roles/` returns any line at the merge tree. Stated as a
   grep over the directory rather than over the two files named here, so a third charter that
   acquires one is caught too.

---

## Ruling 76 — Ruling 69's obligation is a class with a sweep, not a list of slices; the template is one member of three, and the obligation re-assigns to W37-6

### 1. Verified — and the plan's mechanism is not the mechanism

The finding is real: `docs/_templates/REFERENCE.md` lines 39-49 state that the vendored set is
decided by *"any directory holding a `LICENSE` that is not the repository's own … **not a
hand-kept list**"* — the rule Ruling 69 rejected, described as the opposite of what Ruling 69
ruled. Two things about **why** it survived are not as the plan reports them.

| Fact | Timestamp | Consequence |
|---|---|---|
| Ruling 69 merged (`#563`, `9d33c60`) | `2026-09-02T00:30:56Z` | — |
| W37-1 merged (`#562`, `553bbef`), adding the template | `2026-09-02T00:38:22Z` | **After** the ruling, not before. `9d33c60` is an ancestor of `553bbef` |
| W37-2 merged (`#567`, `2204ffb`), adding `is_vendored` | `2026-09-02T01:05:19Z` | **34 minutes after** the ruling, still implementing the rejected rule |

The plan's account — *"the template landed in W37-1, before Ruling 69, and Ruling 69 §3's
obligations name W37-2, W37-4 and W37-6 but not the template, which is how it survived"* —
inverts the order. The PR numbers invert it too: `#562` was **opened** at `00:27:16Z`, before the
ruling existed, and merged after it. **The mechanism is a branch open across a ruling's merge
that nobody re-read against the ruling before merging it** — not an obligation list that omitted
a file.

**And the template is the smaller half.** At `e93e0e4`, `scripts/_docid.py`'s `is_vendored` still
walks the tree looking for a `LICENSE`, and its docstring says so: *"Ruled as Ruling 69 (…, PR
`#563`, **not yet merged at the time this was written**) … Apply the ruling once `#563` merges;
until then this implements the rule exactly as published."* `#563` had merged twenty-six minutes
before `#567` did. `_VENDORED_SKILLS` does not exist anywhere in the repository.

**So Ruling 69 §3's first obligation is undischarged on the slice it named by name.** Extending
the obligation list would not have prevented this, and that is the whole point: W37-2 **was** on
the list. What is missing is a violation that can be detected. Ruling 69's own acceptance item 1
— *"Remove one entry from `_VENDORED_SKILLS`, or one skill line from `pyproject.toml`'s ruff
`exclude`, and the gate must red naming which side moved"* — **cannot fire, because its subject
does not exist.** An acceptance item whose subject is absent is not a check that has never failed;
it is a check that was never built, and nothing distinguished the two (`CLAUDE.md` §13).

### 2. Ruled

**Ruling 69 §3's obligation is restated as a class with a sweep.** It is not a list of slices,
and a slice name in it is a schedule, not the obligation's extent.

**The class: every site in the tree that states or implements a criterion for the vendored set.**
At `e93e0e4` it has three live members outside the frozen record set:

| Site | What it does | Disposition |
|---|---|---|
| `scripts/_docid.py`, `is_vendored` | **Implements** the rejected `LICENSE` probe | Replaced by the membership test against `_VENDORED_SKILLS`; signature preserved, per Ruling 69 §2 part 4 |
| `docs/_templates/REFERENCE.md` lines 39-49 | **Teaches** it, and calls the ruled mechanism *"not a hand-kept list"* | Corrected to state the declared constant reconciled against the ruff exclude list |
| `tests/test_doc_id.py` lines 372-430 | **Asserts** it — five tests that pin the rejected behaviour | Re-pointed at the membership test, with a broken-input proof for the reconciliation |

**`docs/notes/0019-one-id-per-document.md` §1.5 and §5.4 are not in the class and are not
edited.** Ruling 69 §3 already says so and it stands: the note is the maintainer's original, §1
stays byte-identical, and a note that records a gloss is not an instrument that teaches one. The
distinction is the whole reason the template is different from the note it paraphrases — a
template is copied by an author, a note is read by one.

**The obligation re-assigns.** W37-2 and W37-4 have both shipped without discharging it, so it
carries to **W37-6** with the W37-6 executor as its named owner. That is a verdict, not silence
(`CLAUDE.md` §13's four).

**The general rule, which is the durable half and applies beyond this ruling: an obligation a
ruling assigns to a slice does not lapse when that slice merges without discharging it. It
re-assigns to the next unshipped slice, and it is stated as the class of sites it must reach, not
as the list of slices expected to reach them.** A list of slices is a schedule; a schedule that
is missed leaves nothing behind. A class plus a sweep leaves a grep.

### 3. What it obliges

- W37-6 discharges all three sites in one commit, and the deviation record Ruling 69 §2 part 3
  requires in `.claude/skills/README.md` lands with them.
- The reconciliation check Ruling 69 §3 assigned to W37-4 carries to W37-6 with it — it is the
  same obligation and it has the same owner. Its broken-input proof is Ruling 69 acceptance item
  1, which becomes runnable for the first time once `_VENDORED_SKILLS` exists.
- **Not this role's, referred to the lead in §7:** whether `docs/process/delivery-process.md`
  gains a step requiring a branch open across a ruling's merge to be re-read against that ruling
  before merging. That is process, and process is the lead's.

### 4. Acceptance — the violation that must become detectable

1. **No instrument or implementation may state the rejected criterion.** **Violation:**
   `git grep -nE "holding a .?LICENSE|ship(s|ping) (its )?own .?LICENSE" -- scripts/ tests/ docs/_templates/ .claude/`
   returns a hit at the merge tree. Frozen records — filed plans, ruling records and
   `docs/notes/` — are outside the pathspec by construction, so the grep needs no allow-list and
   cannot decay into one.
2. **The absent check must become a failing one.** Ruling 69 acceptance item 1 is run at the
   merge tree and **reds**: remove one entry from `_VENDORED_SKILLS`, and separately one skill
   line from `pyproject.toml`'s ruff `exclude`, and the gate must fail naming which side moved.
   **Violation: either edit passing green — including the case where it passes because
   `_VENDORED_SKILLS` still does not exist**, which is how this defect survived two slices.
3. **The re-assignment must be visible.** **Violation:** W37-6's ledger closing without a line
   naming Ruling 69 §3's obligation, the slice it was originally assigned to, and its outcome.

---

## Ruling 77 — the two files with no destination are a derivation this role takes, not an amendment to NT-0019

### 1. The question the lead asked, answered first

**It is a technical decision, and it is taken here.** NT-0019 §5.2 is an **impact map** — a
derived enumeration of what the migration must move — not a normative rule. §1 is the standard,
§2's D0-D14 are the decisions, and neither is touched by assigning a destination to a file §5.2's
hand-built table failed to enumerate. Both destinations follow from rules **already in the note**,
so this is applying §5.2's own logic to two rows it missed. Ruling 69 set the precedent and it is
this role's: *"Nothing in `docs/notes/0019-one-id-per-document.md` is edited."* Nothing is edited
here either.

Had either file required a rule the note does not contain — a new family, a new `kind:`, a change
to §1 — it would have gone to the maintainer. Neither does.

### 2. Verified

`docs/audit/` holds 43 tracked files. §5.2's eight `docs/audit/` rows cover 41 by exact name or
glob. The two uncovered are exactly the two the plan names:

- **`docs/audit/nt-0019-verification-and-impact-sweep.md`** — an auditor sweep record dated
  2026-09-02, filed after NT-0019 merged. It postdates the table that would have to list it,
  which is why no row reaches it.
- **`docs/audit/work/nt-0010-0011-adoption/pilot-findings.md`** — §5.2's work row is
  `audit/work/*/README.md`; this is a sibling non-README file in that same directory and falls
  outside the glob.

`git grep -in 'sweep\|pilot-findings\|nt-0010-0011-adoption' docs/notes/0019-one-id-per-document.md`
returns nothing, confirming neither is named anywhere in the note.

### 3. Ruled

**Both become `RS- kind: audit`, owner auditor**, under NT-0019 §1.2's `RS` `audit` row — *"a
bespoke audit's method, evidence and verdicts; files every finding as `FD-`"* — and D13's owner
assignment (*"research → executor, except `RS- kind: audit` → auditor"*).

- The sweep record: this is the plan's own proposal and it is correct. It is a bespoke audit's
  method, evidence and verdicts, and nothing else in the family set fits it.
- `pilot-findings.md`: it is the method, evidence and verdicts of the `CLAUDE.md` §15 step 6
  pilot run against the role charters — the same shape, produced by the same kind of exercise.
  Its sibling `README.md` becomes a `CR- kind: work` under §5.2's existing row, and §1.2's `RS`
  `audit` row already requires that `CR-` to cite the record, so the pair keeps its structure.

**Rejected: folding either into the `CR-` its neighbour becomes.** Acceptance (g) class 4
requires *"the concatenation of the outputs reproduces the input's body lines in order"*; folding
two documents into one moves body lines between outputs and is exactly what that class exists to
catch.

**Rejected: minting an `FD-` per numbered finding in either.** The `RS` `audit` row's *"files
every finding as `FD-`"* governs a bespoke audit **going forward**; applied retroactively it
would re-key `pilot-findings.md`'s P-numbered findings into a permanent id family, which is a
migration nobody planned and which §5.2 does not contemplate for any other record. **Apply the
whole rule prospectively and the narrow rule retrospectively**: a finding in either document that
is **still open** at the merge tree becomes an `FD-` and the `RS-` cites it; a finding the
document already records as resolved stays a section, and the `RS-` is filed at the status its
own content supports. *Half-applying this rule — the family without the findings clause — is the
failure mode, so the executor records which findings it found open and why.*

**A side finding for the executor, not a ruling.** §5.2's row for `audit/findings/F*.md`
annotates the count as `(5)`; the directory holds **11** `F*.md` files at `e93e0e4`. The row is a
glob, so coverage is unaffected and nothing is stranded — but the annotation has drifted, and a
count in a frozen note is not re-derivable by a later reader
([`NT-0003`](../notes/0003-duplicated-status-goes-stale.md)). Do not inherit it.

### 4. Acceptance — the violation that must become detectable

1. **Every file must land somewhere, and the check already exists.** Acceptance item (a)'s zero
   `none` row over `docs/` catches an unclassified file. **Violation: a positive `none` row, or
   a classified total below `git ls-files docs/ | wc -l`.** Stated here so the executor knows (a)
   is the backstop for this class and does not add a second one.
2. **The two files must be findable afterwards.** **Violation:** `docs/REDIRECTS.csv` lacking a
   row whose source is `docs/audit/nt-0019-verification-and-impact-sweep.md` or
   `docs/audit/work/nt-0010-0011-adoption/pilot-findings.md`, or a row whose target does not
   exist. Named by path, because these two are precisely the files a glob-driven redirect
   generator will miss for the same reason §5.2 missed them.
3. **The findings clause must not be half-applied.** **Violation:** either document reaching the
   merge tree as an `RS- kind: audit` while a finding its own text marks open has no `FD-`.

---

## Ruling 78 — a pre-run predicate is insufficient as the plan states it, and it is also mis-sized by a factor of four; the remedy is an enumerated table whose positive control the corpus already supplies

### 1. The lead's concern is correct, and the measurement makes it concrete

The plan's §10 finding 9 and §7.5 identify the one place a wrong result passes the whole gate:
splitting `docs/audit/closure-records.md` per heading mints a `CR-` for each record, three of
which are *"in progress, not closed"* and one of which is a phase; shape and header are both
correct, so checks 31 and 37 pass, and **no check tests whether a closure record records a
closure.** Its remedy is *"the split rule must exclude them by predicate before the run."*

The concern that a pre-run predicate is a one-time human judgement with no failing case is right.
The measurement makes it sharper than an argument could:

| `closure-records.md` at `e93e0e4` | Count | The plan's figure |
|---|---|---|
| `###` records in total | 21 | 21 |
| Work closes (`W<n> — …: closed <date>`) | **8** | implied 17 |
| Phase close (line 8, `Phase 1a — exit demo accepted`) | 1 | 1 |
| Marked `*(in progress, not closed)*` | **10** | **3** |
| Neither a close nor a slice record — line 1121 `Independent audit`, line 1555 `W4 mid-workstream scope findings` | **2** | not identified |
| `##` headings | 0 | 0 |

**The predicate as stated is wrong about its own population by a factor of more than three, and
misses a further category entirely.** Only 8 of 21 records are work closure records. A predicate
written to exclude three would have left **seven** documents in the tree asserting closures their
sources do not record. That is not a hypothetical failure mode of the predicate approach; it is
the actual state of the predicate the plan proposes.

### 2. Ruled

**A pre-run predicate is not sufficient — but not because predicates are wrong. It is
insufficient because the plan states no expected output for it.** A predicate whose result is
never compared against an independently-stated expectation is a private judgement; the same
predicate whose output is asserted against a stated set is a test with a failing case. The
distinction is the whole of `CLAUDE.md` §13's *"a check that has never printed a failure has not
been tested"*, and the evidence that it bites here is that the unasserted figure was wrong.

**Three parts.**

1. **The split is driven by an enumerated table, not a predicate.** W37-6's ledger carries a
   **21-row table**, one row per `###` heading, giving its line number, its verbatim heading text,
   and its destination family and `kind:`. A table can be read and disagreed with by someone who
   was not there; a predicate cannot.
2. **Nothing is excluded.** Acceptance (g) class 4 requires the outputs' concatenation to
   reproduce the input's body lines in order. Excluding thirteen records is thirteen blocks of
   body lines with no output — either a (g) failure or a carve-out in (g), and a carve-out in (g)
   is what [Ruling 68](2026-09-02-w37-migration-preconditions-rulings.md) closed. Each record gets
   a destination; **a record that is not a close does not become a `CR-`.**
3. **`CR-` cannot express "not closed", and this was checked rather than assumed.** NT-0019 §1.2's
   `CR` row is *"one work, phase or review close"*, mutability *write-once*, status subset
   **`active`** — a single value, with no non-closed member. So the ten in-progress records and
   the two non-closure records are **not `CR-` documents at all**; only the 8 work closes and the
   1 phase close are, the latter as `kind: phase`, which the family already carries. **Which
   family the other twelve take is the planner's derivation under §5.2's own rules, not this
   ruling's** — this ruling fixes that they may not be `CR-`, and that they may not be dropped.

### 3. Why this answers "must something detect it after the fact?" — yes, and two things can

The lead asked whether something must be able to detect the failure after the run. It must, and
the migration's own output supports two independent detectors, neither of which requires re-running
the predicate:

- **Count-facing, readable from the artifacts alone.** After the run, exactly **9** documents
  derived from `closure-records.md` are `CR-` (8 `kind: work`, 1 `kind: phase`), and all 21
  headings have a `REDIRECTS.csv` row. Anyone can check this later without any of the executor's
  context.
- **Check-facing, with a positive control the corpus already contains.** A `CR-` whose body
  carries an in-progress marker is a violation, and the ten marked records are ten real inputs on
  which such a check can be proven to fire. **This is the argument against exclusion that matters
  most:** excluding them removes the only true positives the repository has for this class, and a
  check written afterwards would have nothing to be tested against. Ruling 67 acceptance item 2's
  standard — *"a control that runs a different regex body goes green because of what it misses"* —
  applies to the population as much as to the pattern.

### 4. Acceptance — the violation that must become detectable

1. **The predicate's output is asserted, not trusted.** Before the split, run the in-progress
   predicate over `closure-records.md` and compare its output to the ten line numbers named in §1
   above. **Violation: it returns three (the figure the plan states), returns any of the eight
   work closes, or returns a count the ledger does not state in advance.** This is the item that
   converts a private judgement into a test, and it is the one this ruling exists for.
2. **The result is checkable from the artifacts after the fact.** **Violation:** the post-migration
   tree containing 21 `CR-` documents derived from `closure-records.md`, or any `CR-` whose body
   contains `in progress, not closed`, or fewer than 21 `REDIRECTS.csv` rows sourced from that
   file's headings.
3. **The same defect class must be swept, not just its reported instance.** `plan-reviews.md` has
   14 `###` of which 11 are reviews and 3 sit under `## Pending proposals` with no §5.2
   destination; the same enumerated-table rule applies to it. **Violation: a `CR- kind: review`
   minted from any of the three `Pending proposals` candidates, or any of the three dropped**
   (the marker class is swept, not the reported symbol).

---

## Acceptance Standard

This record is complete when all six of the following hold. Each is stated as a violation, per
`CLAUDE.md` §13.

1. **Every ruling number is unused.** `git grep -oh -E 'Ruling (7[3-8])' origin/main -- .` returns
   nothing at the merge base of this branch. *Violation: any of 73-78 already minted.*
2. **Every amended ruling names what it supersedes, and the superseded text is quoted.** Ruling 73
   quotes Ruling 66 acceptance item 2 verbatim before withdrawing it; Ruling 76 quotes Ruling 69
   §3's obligation before restating it. *Violation: an amendment that states a new position
   without quoting the old one — which leaves both live.*
3. **Every acceptance item in every ruling is a violation, not a description.** *Violation: an
   acceptance item that cannot fail, or that describes correct behaviour rather than the
   observation that would falsify it.*
4. **Every measured figure carries its method and its tree.** *Violation: a count without the
   command that produced it and the SHA it was produced at.*
5. **The gate is green.** `python3 scripts/audit-docs.py` exits 0 on this branch. *Violation: any
   non-zero exit — including check 28 demanding this section, which is honoured here rather than
   evaded, and check 19's `ADR-` resolution, which this record avoids tripping by citing no ADR.*
6. **Nothing outside this role's charter is decided.** *Violation: this record accepting a Work,
   Phase or Project close, amending `CLAUDE.md`, editing a frozen plan, or making a sequencing
   decision — §7 names what was referred up instead.*

---

## 7. What this record does not rule, and where each goes

| Question | Whose | Why not this role's |
|---|---|---|
| Whether W37-7 runs immediately after W37-6, with `git-hygiene` first in its order | **The lead's** | Sequencing. Ruling 74 removes the argument that made it urgent; it does not decide the order |
| Whether `docs/process/delivery-process.md` gains a step requiring a branch open across a ruling's merge to be re-read against that ruling before merging | **The lead's** | Process, and `.claude/roles/lead.md` names that file as the lead's to write. Ruling 76 §2 records the mechanism; the process change is not this role's to impose |
| Which family the twelve non-close records in `closure-records.md` take | **The planner's** | A derivation under NT-0019 §5.2's own rules. Ruling 78 fixes only that they may not be `CR-` and may not be dropped |
| How check 39's PR-title clause is ever enforced, given that `audit-docs.py` cannot read git or GitHub | **A later slice's decision point** | It is a new capability decision, not a W37-6 question. Raised in Ruling 74 §3 so it is scheduled rather than discovered |
| Whether W37-6's disclosure package is sufficient for the maintainer's go-ahead | **The maintainer's** | The delegation record §2 reserves acceptance; a go-ahead on an enlarged commit is the maintainer's to give |
| Whether the two-file divergence between 928 and 930 legacy-form carriers matters | **Deliberately unresolved** | Re-derived in the running session per the plan's own acceptance (f); this record states its own method rather than reconciling a figure whose method is unstated |

---

## 8. One thing that got caught only by reading to the end, recorded because the next reader will not

The lead's brief relayed the leaf plan's finding 12 as *"Ruling 66's acceptance item 2 cannot
discriminate a member from a non-member"* — true, and the plan's evidence for it is correct. What
neither the brief nor the plan reports is that the same item **fails for four real members**, one
of them a primary instrument from the map plan's own floor. The false-positive direction is the
one you find by reasoning about the test; the false-negative direction is the one you find only
by running it against the actual member list. Running it cost one script and eleven seconds, and
it changed the amendment from *"add a sharper test"* to *"withdraw this one, because acting on it
would have removed four instruments from the commit that exists to carry them."*

The transferable rule, and it is the reason this section exists rather than a note: **when a test
is reported as too weak, run it in both directions before amending it.** A test that admits too
much and a test that excludes too much are the same defect seen from two sides, and the second
side is the one that does damage.
