---
id: RL-970
family: ruling
title: RL-987's acceptance item 2 is withdrawn: it is wrong in both directions and blind to omission, and the replacement tests H content in two limbs
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-6-leaf-plan-findings-rulings.md
---

# W37-6's leaf-plan findings: what only Rulings 66 and 69's author can fix — Rulings 73-78 (2026-09-02)

**What this is.** Six rulings on the findings W37-6's leaf plan filed in its §10 against the
records this role wrote — [RL-987](RL-00990-rfc-937-1-5-s-vendored-parenthesis-is-a-gloss-not-a-detector-the-set-is-declared-and-reconciled-and-the-exemption-reaches-only-the-blanket-passes.md) (DP-1,
the creating-instrument set) and [RL-990](RL-00990-rfc-937-1-5-s-vendored-parenthesis-is-a-gloss-not-a-detector-the-set-is-declared-and-reconciled-and-the-exemption-reaches-only-the-blanket-passes.md)
(the vendored criterion). Four were routed here because a defect in a ruling's acceptance item
can only be amended by that ruling's author; two were routed as judgement calls that might not
be rulings at all. Both of the latter turned out to be rulings, and both are taken here.

**Authority.** [`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md)
§1 grant 1: the lead may route a technical question to this role and its ruling stands as the
maintainer's. §2 bounds that grant — not a fact only the maintainer holds, not acceptance of a
Work, Phase or Project close, not an amendment to `CLAUDE.md`. Every item below sits inside
those bounds. §7 records what was referred up instead of ruled.

**Ruling numbers, derived rather than relayed.** At `e93e0e4`:

| Derivation | Command | Result |
|---|---|---|
| Highest minted ruling heading | `git grep -oh -E '^#{2,3} Rulings? [0-9]+' origin/main -- .` | max **72** |
| Nothing above it anywhere | `git grep -oh -E 'RL-873[3-9]\|Ruling [89][0-9]\|RL-864[0-9][0-9]' origin/main -- .` | empty |
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
| V2 | Reverting a non-member produces an item-(d) hit | **Confirmed and quantified.** 928 of 1447 tracked files carry at least one legacy form. Measured by calling the **shipped** `sweep_legacy_forms` with the shipped `LEGACY_FORM_PATTERNS` on each tracked file (RL-988 acceptance item 2: never a re-typed copy of the pattern) |
| V3 | The test also **fails for real members** | **Confirmed — and the plan does not report this direction.** Four of its thirteen members carry **zero** legacy forms. RL-970 §1 has the table |
| V4 | `docs/_templates/REFERENCE.md` contradicts RL-990 | **Confirmed**, lines 39-49, in the words RL-990 rejected |
| V5 | "The template landed in W37-1, **before** RL-990" | **Refuted.** RL-990 (`#563`) merged `2026-09-02T00:30:56Z`; W37-1 (`#562`) merged `00:38:22Z`, seven and a half minutes **later**, and `9d33c60` is an ancestor of `553bbef`. The PR numbers invert the merge order. RL-973 §1 |
| V6 | RL-990 §3's obligation list is what let it survive | **Refuted, and the real state is worse.** `scripts/_docid.py`'s `is_vendored` **still implements the rejected rule** at `e93e0e4`; `_VENDORED_SKILLS` does not exist anywhere in the tree. W37-2 (`#567`, merged `01:05:19Z`) was named in that obligation list **by name** and shipped without discharging it. RL-973 §1 |
| V7 | `closure-records.md`: "three of its 21 `###` records are marked *in progress, not closed*" | **Refuted. There are ten.** Lines 1862, 1904, 1982, 2014, 2073, 2107, 2160, 2223, 2269, 2343, each carrying `*(in progress, not closed)*` verbatim. RL-975 §1 |
| V8 | One of the 21 is a phase rather than a work | **Confirmed** (line 8, `### Phase 1a — exit demo accepted 2026-08-15`) — **and two more are neither a work nor a phase close**: line 1121 `### Independent audit — 2026-08-15, and what it changed` and line 1555 `### WK-660 mid-workstream scope findings — 2026-08-14`. Only **8** of the 21 are work closure records |
| V9 | `.claude/roles/auditor.md` carries four `docs/audit/` paths in one bullet | **Confirmed as to the bullet, incomplete as to the file.** The file names **six**; the other two — `docs/audit/findings/<F-id>.md` and `docs/audit/findings/README.md` — sit in the next bullet |
| V10 | `RFC-937` D10 calls charters *"the creating instruments"* in as many words | **Confirmed in substance, overstated as a quotation.** D10 reads: *"Charters, skills and agents carry the header \| They are the `owner:` vocabulary and the creating instruments."* The phrase attaches to the three-member group; it does not single charters out. The conclusion survives, the quotation should not be re-cited in its stronger form |
| V11 | Two of `docs/audit/`'s 43 files have no §5.2 destination row | **Confirmed**, and they are the two named. §5.2's eight `docs/audit/` rows cover 41 by exact name or glob |
| V12 | 72 ruling headings across 29 files | **Confirmed** under the `##`/`###` reading. The literal regex returns 87 across 42 — the extra 15 are 12 Python source comments (`#` collides with h1) and 3 single-ruling documents whose own title is the heading |

**On the one number I could not reconcile.** The plan reports **930** files carrying a legacy
form at `39ee30c`; the method above returns **928**. The plan does not state its method, so the
two-file difference cannot be attributed. It bears on no finding here — the discrimination
failure in RL-970 §1 holds at either figure — but the executor re-derives it in the running session
rather than inheriting either number, as the plan's own §5.4 already requires for acceptance (f).

---

## RL-970 — RL-987's acceptance item 2 is withdrawn: it is wrong in both directions and blind to omission, and the replacement tests H content in two limbs

### 1. The defect, measured

RL-987 acceptance item 2 reads:

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

1. **It passes for non-members.** RFC-937 §4 step 6 rewrites citations across *"the whole tree
   — `git ls-files`, nothing exempt"*, so reverting any of the 928 carriers restores a legacy
   form that acceptance item (d)'s tree-wide sweep returns. The test measures *"is this file in
   the migration commit"*, which the **M** row already guarantees for all 928, rather than *"was
   its instruction content corrected"*, which is what DP-1 is about. This is the direction the
   leaf plan's §10 finding 12 reports, and it is correct.
2. **It fails for members — the direction the plan does not report, and the worse one.** Four of
   the thirteen adopted members carry no legacy form at all, so their reversion produces no
   item-(d) hit and item 2's stated verdict is to strike them. One of the four,
   `subagent-driven-development`, is not a marginal addition: it is one of the seven **primary**
   instruments RFC-937 §5.4 names and the map plan's own floor. A false positive wastes a proof;
   a false negative removes an instrument from the single commit DP-1 exists to fill.
3. **It has no under-inclusion limb at all.** Item 2 quantifies over *"each instrument in the
   derived set"*. RL-987's whole point was that *"seven is the floor, not the ceiling"* — the
   risk the criterion exists to manage is **omission**, and a test that ranges only over the
   members it is handed can never detect the member it was never handed. The leaf plan's §6.4
   found six additional members by running a second method; item 2 would have reported nothing
   about the absence of any of them.

**The defect does not depend on how "acceptance sweep" is read.** Under the narrow reading it is
acceptance item (d), the legacy-form sweep, and the table above applies. Under a wide reading —
all of (a) through (h) — it is *less* discriminating still, because reverting any tracked file
changes (g)'s diff. Neither reading yields a test that separates a member from a non-member.

### 2. Ruled

**RL-987 acceptance item 2 is withdrawn.** RL-987 §2 (option (a) chosen; (b) and (c)
rejected), the criterion in its §2 closing paragraph, its §3 obligations and its acceptance item
1 all stand unchanged and unaffected. Only item 2 is replaced.

**RL-987 acceptance item 2, as amended 2026-09-02.** The subject of the test is the
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
`docs/`, and RFC-937 §4 step 5's stamp set — *"every file under `docs/`, `.claude/roles/`,
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
