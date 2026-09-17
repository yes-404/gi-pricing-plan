---
id: PL-1031
family: plan
kind: leaf
title: W37-6 — the migration run: the go-ahead re-ask
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-03
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-09-03-w37-6-go-ahead-re-ask.md
---

# W37-6 — the migration run: the go-ahead re-ask

**Date:** 2026-09-03 · **Tree:** `2f0467e` · **Assembled by:** the planner ·
**Status:** awaiting the maintainer's dated line (§10)

**Supersedes `docs/plans/2026-09-02-w37-6-go-ahead-re-ask.md` as the ask, by the maintainer's
own instruction** — *"a new re-ask under 300 lines superseding the old one by id, `SLOT`s 0–3
at a quiet tree and §10 blank"*
([`…-second-withholding-and-standing-rules.md`](../rulings/RL-00976-w37-6-withheld-a-second-time-and-five-standing-rules-on-method-the-maintainer-s-2026-09-02.md)
§5). That document is **evidence, not the interface**: 1,883 lines, preserved as the annotated
tag `evidence/w37-6-reask-v1` (dereferences to `fcd7068e`, PR #650's tip; the branch itself is
deleted so gate condition 5 reads clean — Ruling, `…-time-boxed-delegation.md` §6.4), mined here
and not extended. It superseded [`…-go-ahead-ask.md`](PL-00958-w37-6-the-migration-run-the-go-ahead-ask-with-condition-6-discharged.md), whose
Addenda A and B are on `main` and are re-run at §4. **Nothing superseded is retired** — each is
correct at the tree it names. **This revision re-fills the same file** rather than adding a new
one — it carries no `id:`/`family:` header, is not yet migrated, and the maintainer's own
instruction names refilling `SLOT`s, not re-dating. Every instruction it answers is the
maintainer's of 2026-09-02, amended 2026-09-03 by the renewed delegation
([`…-time-boxed-delegation.md`](../rulings/RL-01049-w37-6-the-maintainer-s-time-boxed-delegation-2026-09-03.md) §6).

**The interface is one line, in §10.** Nothing above it authorises the run.

## Acceptance Standard

The violation this record must make detectable: **a W37-6 go-ahead given against a document
that reports the run as able to complete when it cannot, against figures inherited from a tree
the run will not start from, or without disclosing what landing the commit creates.** Each item
is stated as the violation.

1. **`[SLOT-0]`–`[SLOT-3]` are measured at the header's tree; `[SLOT-4]` is not filled here.**
   *Violation:* a figure measured at any tree but `2f0467e`, or a value in `[SLOT-4]`, which is
   the executor's in the session that cuts the branch (§6).
2. **Every figure carries its tree, its corpus and the predicate it counted with**
   (`CLAUDE.md` §13, amended 2026-09-02) — **and a reconstructed predicate says so.**
   *Violation:* a count a reader holding none of the author's context cannot re-run, or a
   predicate presented as quoted when it was inferred to fit the number.
3. **The disclosure states what landing *creates*, not only what it fails to fix.**
   *Violation:* §7 omitting the documents check 37 reds on because the run brought them into
   existence.
4. **Condition 3 keeps the closure record's own words.** *Violation:* "the abort points are
   cleared" without `satisfied literally and not sufficiently` attached — the phrase
   [`W37-5c/README.md`](../closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md) chose, the first a paraphrase loses.
5. **§10 is empty until the maintainer writes it.** *Violation:* an approval inferred from §9,
   or a date in §10 in any other hand.
6. **No other frozen plan is edited by this branch.** *Violation:* a non-empty
   `git diff --stat origin/main...<this branch> -- docs/plans/` naming any file but this one —
   not frozen while its `Status` line reads "awaiting", per its own §2.

---

## 1. What is asked, and the four conditions scored

**Verbatim, from [`…-go-ahead-ask.md`](PL-00958-w37-6-the-migration-run-the-go-ahead-ask-with-condition-6-discharged.md) §8**, prefaced by
*"Re-ask when 5c is closed"* and joined by a later instruction that the re-ask names the gap:

> *"§3 and §4 re-derived at that tree, the addendum merged and re-run, F80–F82 shown cleared by
> execution. Then I read one document and write one line."*

| # | Condition | State | Where |
|---|---|---|---|
| 0 | W37-5c is closed | **Discharged at `ac10d30`.** Clean audit plus the lead's merge of #647 as `c888b61`; both records now say so. `grep -c "W37-5c CLOSED" docs/roadmap.md` → 1 at `ac10d30`, 0 at `c888b61` | [`W37-5c/README.md`](../closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md) |
| 1 | §3 and §4 re-derived at that tree | **Discharged at `2f0467e`** — re-derived at the quiet tree, superseding every earlier pass's figures | §3 |
| 2 | The addendum merged and re-run | **Discharged at `2f0467e`** — merged on `main`; re-run here | §4 |
| 3 | F80–F82 shown cleared by execution | **Satisfied literally and not sufficiently** — the closure record's phrase, kept because it is still the true one. Five abort points and a sixth post-write failure are all cleared, and `migrate()` runs to completion | §5 |
| 4 | The re-ask names the gap | Named as a condition with a re-runnable check, never as a date | §6 |

---

## 2. The slot register

**A slot is filled only by a measurement at the tree its class allows, and this table is the
authority on state** — a `[SLOT-` token elsewhere is a mention, not an empty slot.

| Slot | State | Class |
|---|---|---|
| `[SLOT-0]` | **FILLED — `2f0467e`.** The quiet tree this ask is re-made at, superseding `796cd07` | Final-tree |
| `[SLOT-1]` | **FILLED — §3.** §3 and §4 of the disclosure re-derived at `2f0467e` | Final-tree; condition 1 |
| `[SLOT-2]` | **FILLED — §4.** Addendum A re-run at `2f0467e` | Final-tree; condition 2 |
| `[SLOT-3]` | **FILLED — `completes`.** §5, re-run at `2f0467e` | Final-tree; condition 3 |
| `[SLOT-4]` | **Deliberately unfilled.** The gap checks, run by the executor in the session that cuts the migration branch | Running-session; §6 |
| `[SLOT-5]` | **FILLED — 125.** Files written before `KeyError: 'RS'` at `c888b61` — 125 `write_text` calls, 125 distinct paths, none repeated, none outside `docs/`; by family `rfcs` 19 · `adrs` 6 · `rulings` 95 · `closures` 5 | Historical at `c888b61`; no later tree changes it |

**`2f0467e` is `origin/main` under freeze** — PR #671's merge commit (the `FD`/`WF`
implementation), with no open PR behind it; **nothing lands in W37-6 scope after this tree**,
per the maintainer's freeze instruction, so this is the last re-derivation, not one of a
series. This document's own edit lands on top of it as the only addition, per condition 4's
own violation clause: *"a gate condition recorded as met at a tree other than the one the ask
is made from."* Between `796cd07` and `2f0467e` landed, in order: Rulings 96/97 (`a8b31ab`
#661), RL-1047 (`d1cabe1` #665), the renewed delegation and its two rulings (`e56d038` #664,
quoted at §7), the register reconciliation (`735c828` #666), F95 (`c039729` #668), RL-1048
(`54a3ee5` #669), the Ruling-98/99 heading fix and F96 (`0042957` #670), and the `FD`/`WF`
implementation (`2f0467e` #671). **One branch remains, by design, not left over**:
`docs/w37-6-go-ahead-reask` stays until *this* PR merges and its citation (§1's supersession
paragraph) repoints to the tag, so `main` never carries a dangling reference — deletion is
delegation §6.4's act, not this ask's. §6's gap condition is checked in the session that cuts
the *migration* branch, not here.

---

## 3. Condition 1 — §3 and §4 of the disclosure, re-derived at `2f0467e`

**Predicate identical to PR #659 §3** (on `main`, citable rather than re-derived); only the
figures move. Code moved too, not only corpus: `#657`/`#660`/`a8b31ab` (as before) plus
`0042957` (RL-1047/1048 heading fix) and `2f0467e` (`FD`/`WF` implementation, `#671`).

| `[SLOT-1]` — the migration… | `796cd07` (PR #659) | **`2f0467e`** |
|---|---|---|
| tracked files | 1540 | **1555** |
| rewrites a citation token in | 1000 files · 23 117 lines · 31 415 hits | **1012** files · **23 481** lines · **31 925** hits |
| stamps a header on | 345 | **355** = 307 − 13 + 46 + 8 + 7 |
| moves, splits or deletes | 263 | **273** = `docs/audit/` 68 · `docs/plans/` 166 · `docs/notes/` 20 · `.claude/notes/` 19 |
| regenerates, never hand-edits | 61 | **61** |
| does not touch at all | 540 | **543** = 1555 − 1012 |
| must leave unchanged, by rule | 43 `VR-` ids | **43** |
| ruling headings, plan predicate | 96 over 40 | **100 over 43** |
| ruling headings, shipped splitter | 92 over 37 | **96 over 40** |

**Movement since `735c828`** (my prior, superseded pass): +2 tracked-file additions
(`F95.md`, `F96.md` under `docs/audit/`) + 1 (RL-1048's own file) = +3 real corpus growth,
plus 5 test-fixture-only additions under `tests/` that do not touch any `docs/` count. Ruling
headings +2/+2: RL-1047's own file gained its heading (F96's fix) and RL-1048 is new — **not
the seven documents RL-1047's rule names (§5)**, which carry no `## Ruling N` heading by
design and were never in this census. **F94 is unmoved**: the plan expects **4** more ruling
documents than the shipped splitter finds (100 − 96), the same gap at every tree measured.

---

## 4. Condition 2 — the addendum, merged and re-run at `2f0467e`

**Merged**, unchanged since PR #659 (`c888b61`).

**`[SLOT-2]` — re-run at `2f0467e`**, `uv run python scripts/ruling-acceptance-item-census.py`,
**exit 0**:

```
w37 34 · w11 20 · standalone 2 · exception 1 · prose_only 10 · none 35 · conflict 0
total classified 102 = total discovered 102 · none grandfathered 35 · post-flag-day violations 0 · PASS
```

**+2 from my prior pass's 100, both `w37`**: Rulings 98 and 99, both now carrying their own
`## Ruling N` heading and `Acceptance — …` section, so neither trips a violation.
`total classified == total discovered` validates the classifier, not the corpus — **F94 is
that gap, measured in §3.**

---

## 5. Condition 3 — `[SLOT-3]`, by execution

**`[SLOT-3]` — `completes`.** Re-run at `2f0467e` on a disposable snapshot, never the
repository: `MigrateResult` returns, no exception, **0 warnings**, **65** deferred reference
stamps.

**Write trace — 1,466 events**, by innermost `doc-id.py` frame: `_rewrite_citations` **1091** ·
`_write_document_drafts` **345** (ADR 6 · CR 40 · **FD 34** · LG 10 · PL 125 · RFC 20 · RL 99 ·
RS 6 · **WF 5**, none unfamilied) · `_stamp_reference_targets` 20 · `_write_reference_moves` 4 ·
`_merge_phase1b_register`, `_move_unstampable_research_files`, `_restructure_roadmap`,
`migrate`, `_write_redirects`, `_regenerate_index_for_migrate` 1 each. **Distinct paths 1,102**
· **`files_written` 1,099** · **deleted 261** (255 draft-writer, 4 `_write_reference_moves`,
1 `_merge_phase1b_register`, 1 `_move_unstampable_research_files`, 1 `migrate`).

**Two new families, both verified, not asserted.** `FD` **34** = 33 `docs/audit/findings/F*.md`
(`git ls-files`, this tree) + F28's essay, no standalone file. `WF` **5** = the five
`docs/workflows/wf-0*.md` files (`README.md` excluded, `reference` instead). **`none` = 0**,
but only measured correctly *after* `git add -A` on the migrated snapshot — `git ls-files`
undercounts an unstaged write. Verified both ways: pre-add, `check --classify` reads the old
tree and reports `none` 74 of 369; post-add, 12 real families sum to **460 = `git ls-files
docs/`**, `none` absent from the output. **Three new write mechanisms since PR #659**
(`_write_reference_moves`, `_merge_phase1b_register`, `_move_unstampable_research_files`) are
the fourteen relocations and the phase-1b register merge, run inside `migrate()`, not a
separate landed commit.

**RL-1047: one half moved, one did not — stated separately because a reader needs to know
which.** `FD`/`WF` are **implemented and verified above**. **RL-1047's own substantive rule
is not**: its §1 names **seven** maintainer-prose documents that should migrate `RL-`,
`owner: maintainer`; re-traced by `was:` in this snapshot, **all seven still land `PL-`**
(one is `…-time-boxed-delegation.md`; six predate `796cd07`, unrelated to this ask's own
files). Only RL-1047's *own* document now classifies correctly — F96's heading-fix (self-
referential: a ruling missing its own `## Ruling N` heading) is a different defect that
happens to share this window, not the rule RL-1047 states. **Consequence, stated plainly: a
run at this tree stamps those seven `owner: planner`, the exact misattribution RL-1047 was
written to prevent.** Disclosed, not a blocker — `§7(a)`'s `none = 0` bar is met regardless,
and the freeze forecloses implementing it inside this ask.

**Citation-form deferral is implemented, not only ruled**: `FD` is excluded from
`_rewrite_citations`'s token map (`was:` carries the bare `F<n>` instead), so **bare `F<n>`
citations survive migration by design** — nothing here rewrites a finding citation.

---

## 6. Condition 4 — the gap, as a condition and not a date

Unchanged from PR #659 §6, accepted by the maintainer 2026-09-02
([`…-second-withholding-and-standing-rules.md`](../rulings/RL-00976-w37-6-withheld-a-second-time-and-five-standing-rules-on-method-the-maintainer-s-2026-09-02.md)
§3), checked in the session that cuts the migration branch, never here — which is what
`[SLOT-4]` unfilled means:

> **The migration branch is the first branch cut after the last precondition PR merges, with
> `gh pr list --state open` empty, `git ls-remote --heads origin` returning `main` alone, and
> every agent worktree under this `.git` released except the migration's own — each of the
> three recorded with the output of `git rev-parse origin/main` taken in the same command, so a
> sibling worktree advancing `origin/main` between the check and the run is visible rather than
> silent.**

**Recording a gap as *established* is the violation this shape exists to prevent.**

---

## 7. What a go-ahead lands, disclosed

**Landing this commit creates `0` red documents on check 37 — not `284`, because Rulings 96
and 97 are on `main`.** Re-run at `2f0467e` on the fully migrated snapshot: check 37 examines
**588**, exempt **349** by `was:`, shape-checks 239, **enforced population 0**, **RED 0**.

**The four figures are not quotable apart — RL-1040 §4, and the maintainer's own ruling on
this exact question** (`…-time-boxed-delegation.md` §6.3, `e56d038`):

> **It is accepted as met.** The arithmetic is RL-1039's own consequence, and the
> broken-input control proves the check fires on the first document to enter scope. …
> **0 red · 531 examined · 292 exempt by `was:` · and the broken-input proof.**

(§6.3's own **531**/**292** are RL-1040's `15ed00d` figures; this ask's larger **588**/**349**
are the same measurement at a later, corpus-grown tree — §3's movement.) **The enforced
population is 0 because every non-exempt document's required set is empty** — the ruled
outcome, not a defect: **the evidence is the control, not the zero** (RL-1040 §3, proofs 1/2;
`CLAUDE.md` §13 — *"a check that has never printed a failure has not been tested"*).

**Other disclosures, none a condition here.** **F87** — check 33 at **1** header in scope,
landing improves it 0→3 of 65. **F92** — 53 files deferred to **W37-11**. **F94** — §3's
measured gap, carried to the closure record. **F95/F96** — the `FD`/`WF` and heading-fix
gaps §5 already discloses in full; not repeated here. **The tag `evidence/w37-6-reask-v1`**
replaces `docs/w37-6-go-ahead-reask` as this document's own superseded-evidence citation
(delegation §6.4) — the branch is deleted once this citation lands.

**Accepting this run is not accepting the Work close** (`CLAUDE.md` §12). Findings after this
tree go to **W37-6's closure record**, not a further precondition — the freeze now in force
makes this the last such tree.

---

## 8. D1 and D2 — resolved, not reserved

**Both ruled 2026-09-03**, filed as dated sibling records:
[`../rulings/RL-01040-rl-md-s-body-shape-becomes-rl-984-s-four-sections-the-detector-is-asymmetric-and-excludes-placeholder-headings.md`](../rulings/RL-01040-rl-md-s-body-shape-becomes-rl-984-s-four-sections-the-detector-is-asymmetric-and-excludes-placeholder-headings.md), **RL-1039** (D1 —
`check_shape` does not govern a verbatim-migrated body; `was:` marks it) and **RL-1040** (D2
— the F90 slice folds into D1's remedy; the symmetric depth-agnostic detector is struck,
priced against the unsatisfiable `SL-`/`WK-` requirement it would add). §7's `0` red is their
measured consequence, not an argument for it.

---

## 9. Recommendation

**The planner assembles and decides nothing; this is a recommendation, not a conclusion.**

1. **Go ahead.** Unconditional, superseding PR #659's D1-conditional text: `[SLOT-3]` reads
   `completes`; condition 2 is met with its disclosure (§7); D1/D2 are ruled (§8); no reserved
   item blocks the path.
2. **On the gap — §6 is the accepted condition restated; `[SLOT-4]` stays unfilled until the
   branch is cut.**
3. **On RL-1047 — disclosed, not a condition** (§5): the run will misattribute seven
   documents' `owner:` against a ruling already on `main`. Whether that blocks is not this
   ask's to weigh; it is stated so §10 is signed with it in view, not discovered after.
4. **On the citation — already repointed here** (§1): `evidence/w37-6-reask-v1` is on the
   remote; deleting `docs/w37-6-go-ahead-reask` after this document merges is delegation
   §6.4's act, not this ask's.

---

## 10. The signing line

**Signed by the maintainer, or by the lead on delegated authority** under
[`…-time-boxed-delegation.md`](../rulings/RL-01049-w37-6-the-maintainer-s-time-boxed-delegation-2026-09-03.md) §2 — *"If all six
hold: sign §10 of the re-ask `on delegated authority, 2026-09-03, gate 1–6 verified at
<tree>`"* — and only once all six conditions there hold. Nothing above authorises the run by
itself; this line does, in whichever of those two forms it is written.

> **Decision:**
>
> **Date:**

---

## Standing facts

**W37-6 has not run**; everything merged is preconditions. **Rulings 66–99 are filed, all on
`main`**, next free 100. **Full local `uv run pytest -q` is not run by the team** — concurrent
runs OOM-kill each other and `docs/plans/` fixture tests collide with a concurrent
`audit-docs.py` run (F89). CI runs the identical command in a clean environment.
