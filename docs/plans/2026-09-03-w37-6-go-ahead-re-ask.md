# W37-6 — the migration run: the go-ahead re-ask

**Date:** 2026-09-03 · **Tree:** `796cd07` · **Assembled by:** the planner ·
**Status:** awaiting the maintainer's dated line (§10)

**Supersedes `docs/plans/2026-09-02-w37-6-go-ahead-re-ask.md` as the ask, by the maintainer's
own instruction** — *"a new re-ask under 300 lines superseding the old one by id, `SLOT`s 0–3
at a quiet tree and §10 blank"*
([`…-second-withholding-and-standing-rules.md`](2026-09-02-w37-6-second-withholding-and-standing-rules.md)
§5). That document is **evidence, not the interface**: 1,883 lines on branch
`docs/w37-6-go-ahead-reask` (PR #650), unmerged, mined here and not extended. It superseded
[`…-go-ahead-ask.md`](2026-09-02-w37-6-go-ahead-ask.md), whose Addenda A and B are on `main`
and are re-run at §4. **Nothing superseded is retired** — each is correct at the tree it names.
**Dated 2026-09-03 because that is when it was filed**; every instruction it answers is the
maintainer's of 2026-09-02, and the clock crossed midnight UTC mid-assembly.

**The interface is one line, in §10.** Nothing above it authorises the run.

## Acceptance Standard

The violation this record must make detectable: **a W37-6 go-ahead given against a document
that reports the run as able to complete when it cannot, against figures inherited from a tree
the run will not start from, or without disclosing what landing the commit creates.** Each item
is stated as the violation.

1. **`[SLOT-0]`–`[SLOT-3]` are measured at the header's tree; `[SLOT-4]` is not filled here.**
   *Violation:* a figure measured at any tree but `796cd07`, or a value in `[SLOT-4]`, which is
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
   [`W37-5c/README.md`](../audit/work/W37-5c/README.md) chose, the first a paraphrase loses.
5. **§10 is empty until the maintainer writes it.** *Violation:* an approval inferred from §9,
   or a date in §10 in any other hand.
6. **No frozen plan is edited by this branch.** *Violation:* a non-empty
   `git diff --stat origin/main...<this branch> -- docs/plans/` naming any file but the two it
   adds.

---

## 1. What is asked, and the four conditions scored

**Verbatim, from [`…-go-ahead-ask.md`](2026-09-02-w37-6-go-ahead-ask.md) §8**, prefaced by
*"Re-ask when 5c is closed"* and joined by a later instruction that the re-ask names the gap:

> *"§3 and §4 re-derived at that tree, the addendum merged and re-run, F80–F82 shown cleared by
> execution. Then I read one document and write one line."*

| # | Condition | State | Where |
|---|---|---|---|
| 0 | W37-5c is closed | **Discharged at `ac10d30`.** Clean audit plus the lead's merge of #647 as `c888b61`; both records now say so. `grep -c "W37-5c CLOSED" docs/roadmap.md` → 1 at `ac10d30`, 0 at `c888b61` | [`W37-5c/README.md`](../audit/work/W37-5c/README.md) |
| 1 | §3 and §4 re-derived at that tree | **Discharged at `796cd07`** — re-derived once, at the tree the ask is made from | §3 |
| 2 | The addendum merged and re-run | **Discharged at `796cd07`** — merged on `main` inside the superseded ask; re-run here | §4 |
| 3 | F80–F82 shown cleared by execution | **Satisfied literally and not sufficiently** — the closure record's phrase, kept because it is still the true one. Five abort points and a sixth post-write failure are all cleared, and `migrate()` runs to completion | §5 |
| 4 | The re-ask names the gap | Named as a condition with a re-runnable check, never as a date | §6 |

---

## 2. The slot register

**A slot is filled only by a measurement at the tree its class allows, and this table is the
authority on state** — a `[SLOT-` token elsewhere is a mention, not an empty slot.

| Slot | State | Class |
|---|---|---|
| `[SLOT-0]` | **FILLED — `796cd07`.** The tree this ask is made at | Final-tree |
| `[SLOT-1]` | **FILLED — §3.** §3 and §4 of the disclosure re-derived at `796cd07` | Final-tree; condition 1 |
| `[SLOT-2]` | **FILLED — §4.** Addendum A re-run at `796cd07` | Final-tree; condition 2 |
| `[SLOT-3]` | **FILLED — `completes`.** §5 | Final-tree; condition 3 |
| `[SLOT-4]` | **Deliberately unfilled.** The gap checks, run by the executor in the session that cuts the migration branch | Running-session; §6 |
| `[SLOT-5]` | **FILLED — 125.** Files written before `KeyError: 'RS'` at `c888b61` — 125 `write_text` calls, 125 distinct paths, none repeated, none outside `docs/`; by family `rfcs` 19 · `adrs` 6 · `rulings` 95 · `closures` 5 | Historical at `c888b61`; no later tree changes it |

**`796cd07` does not contain this document** — it is `origin/main` at the moment the ask is
put, and this file plus
[`2026-09-03-w37-6-maintainer-decisions.md`](2026-09-03-w37-6-maintainer-decisions.md) are the
branch's only additions. **The tree is quiet in the sense the stopping rule asks for and not in
every sense, disclosed rather than smoothed**: PRs **#656** (F90's amendment) and **#657** (the
shared stamp-set population) were open when the slots were measured; neither is on `main`, so
neither is inside any figure below. §6's gap condition is checked in the session that cuts the
*migration* branch, not here.

---

## 3. Condition 1 — §3 and §4 of the disclosure, re-derived at `796cd07`

**The instrument was checked before the corpus:** `scripts/audit-docs.py` and
`scripts/doc-id.py` are **byte-identical at `32fc63c` and `796cd07`**, so every movement below
is corpus movement. **Every `32fc63c` figure reproduced to the digit before any `796cd07`
figure was trusted** — the positive control that says the predicate is the one the superseded
documents used.

| `[SLOT-1]` — the migration… | `32fc63c` | **`796cd07`** | Predicate |
|---|---|---|---|
| tracked files | 1537 | **1540** | `git ls-tree -r --name-only <sha> \| wc -l` |
| rewrites a citation token in | 997 files · 23 080 lines · 31 361 hits | **1000** files · **23 117** lines · **31 415** hits | the shipped `sweep_legacy_forms` over the `git ls-tree` manifest of a `git archive` snapshot; files/lines/hits are distinct paths, distinct `path:line`, and returned entries |
| stamps a header on | 343 | **345** | `.md` under `docs/` (297) − `docs/_templates/` (13) + `.claude/skills/*/SKILL.md` (46) + `.claude/agents/*.md` (8) + `.claude/roles/*.md` (7) |
| moves, splits or deletes | 261 | **263** | `docs/audit/` 66 · `docs/plans/` 158 · `docs/notes/` 20 · `.claude/notes/` 19 |
| regenerates, never hand-edits | 61 | **61** | `git ls-tree -r --name-only <sha> \| grep -c '^docs/contracts/'` |
| does not touch at all | 540 | **540** | 1540 − 1000 |
| must leave unchanged, by rule | 43 | **43** distinct `VR-` **ids** | `git grep -h -o -E '\bVR-[A-Z]+-[0-9]+\b' <sha> \| sort -u \| wc -l` |
| ruling headings, the plan's predicate | 96 over 40 | **96 over 40** | `^#+\s+Ruling\s+[0-9]+` scoped to `docs/plans/` |
| ruling headings, the shipped splitter | 92 over 37 | **92 over 37** | `doc-id.py`'s `_RULING_HEADING_RE` over `docs/plans/*.md` |

**Both component sums close** (`297 − 13 + 46 + 8 + 7 = 345`, `66 + 158 + 20 + 19 = 263`), and
**all movement is the three files `796cd07` adds** — `docs/audit/findings/F94.md`, one
`docs/plans/` record, `.github/workflows/history-policy.yml`; per-directory the rewrite
population moves `docs` 345→347 and `.github` 3→4 and is flat in the other nine.

**F94 is the last two rows read together, and it is unmoved**: the plan expects the run to touch
**four more ruling documents than the run's own code will find**. Reported, not adjusted —
adjusting would replace the plan's predicate with the code's.

---

## 4. Condition 2 — the addendum, merged and re-run at `796cd07`

**Merged.** Addendum A (*every defective acceptance item in a ruling W37-6 applies*) and
Addendum B (*the run aborts at four points, not three*) are both on `main` inside
[`…-go-ahead-ask.md`](2026-09-02-w37-6-go-ahead-ask.md) at `c888b61`.

**`[SLOT-2]` — re-run at `796cd07`**, `uv run python scripts/ruling-acceptance-item-census.py`,
**exit 0**:

```
w37 30 · w11 20 · standalone 2 · exception 1 · prose_only 10 · none 35 · conflict 0
total classified 98 = total discovered 98 · none grandfathered 35 · post-flag-day violations 0 · PASS
```

**Every bucket is unchanged from `32fc63c`.** The two commits between the pins add no ruling
heading, and the two files this branch adds carry none either.

**The sum is not the check, and that is Addendum A's own lesson applied one level up.**
`total classified == total discovered` validates the **classifier**; both sides come from the
same `_discover_ruling_headings`, so an identity between two numbers from one source cannot
detect what that source never saw. **F94 is exactly that gap measured** — see §7.

---

## 5. Condition 3 — `[SLOT-3]`, by execution

**`[SLOT-3]` — `completes`.** One snapshot `migrate()` run at `796cd07`, on a disposable
`git archive` tree in a scratch directory and never on the repository; `MigrateResult` returns
with no exception and **0 warnings**. **Satisfied literally and not sufficiently** stays the
closure record's phrase for condition 3 — five abort points and the post-write `KeyError: 'RS'`
behind them are all cleared, and *"the abort points are cleared"* was never the same claim as
*"the run completes"*. **This is the first document able to write the second one.**

**The write trace, by call stack — 1,400 write events, and every clause of that matters:**

Bucketed by innermost `scripts/doc-id.py` frame: **`_rewrite_citations` 1085 ·
`_write_document_drafts` 291** — PL 120 · RL 95 · CR 38 · RFC 20 · LG 10 · ADR 6 · RS 2, none
in a no-family bucket — **· `_stamp_reference_targets` 20 · `_restructure_roadmap` 1 ·
`migrate` 1 · `_write_redirects` (`docs/REDIRECTS.csv`) 1 · `_regenerate_index_for_migrate`
(`docs/INDEX.md`) 1 = 1,400.**

**Attribution is by call stack, never by path prefix** — a prefix cannot tell a citation
rewrite from a stamp on the same file, and 305 of the 307 repeated-path writes are that pair.
**The denominator is write events, not distinct paths — and there are three denominators, each
named so a reader meeting them elsewhere does not read a discrepancy.** **Write events 1,400**
(calls; the only additive one, and the only one a per-mechanism or per-family table may use) ·
**distinct paths 1,093** (files touched; 294 created + 799 modified exactly, so no write is a
no-op) · **`MigrateResult.files_written` 1,091** (what the run reports; the union of the paths
a stamping pass wrote with those `_rewrite_citations` wrote, omitting `docs/INDEX.md` and
`docs/REDIRECTS.csv`). Deleted **203**. **Buckets are named, never residual** — the by-writer
total reconciles to the trace total with nothing discarded. **The predicate is every write, not
`write_text` alone**: `Path.write_text` 1,399 + `Path.open("w")` 1 = 1,400, the one being
`_write_redirects`, which no `write_text` call reaches. **Two independent instruments agree
exactly**: a stack-inspecting trace gives 1,400, and a CPython `sys.addaudithook` count of
write-mode `open` events gives 1,403, of which 3 are `importlib` bytecode-cache writes rather
than corpus writes.

**The 1,395-versus-1,396 pair reported against `32fc63c` is the same predicate difference, read
off those documents' own labels** — PR #656's 1,395 is a `write_text` trace, the second
withholding record §5's 1,396 is write events — **and is not something the `796cd07`
measurement establishes.**

**Movement from the `32fc63c` baseline is +4 events and is fully explained**: 1,396 → 1,400 is
+3 `_rewrite_citations` and +1 `PL` draft, the three files `796cd07` adds; `RS` stays 2, and
there is no mechanism-structure movement.

---

## 6. Condition 4 — the gap, as a condition and not a date

**Accepted by the maintainer 2026-09-02**
([`…-second-withholding-and-standing-rules.md`](2026-09-02-w37-6-second-withholding-and-standing-rules.md)
§3). Restated so it is in the one document, and checked in the session that cuts the migration
branch — never here, which is what `[SLOT-4]` being unfilled means:

> **The migration branch is the first branch cut after the last precondition PR merges, with
> `gh pr list --state open` empty, `git ls-remote --heads origin` returning `main` alone, and
> every agent worktree under this `.git` released except the migration's own — each of the
> three recorded with the output of `git rev-parse origin/main` taken in the same command, so a
> sibling worktree advancing `origin/main` between the check and the run is visible rather than
> silent.**

**Recording a gap as *established* is the violation this shape exists to prevent** — it turns a
volatile live condition into a stale claim an executor later reads as satisfied. **The active
leaf plan's missing §1** lands as a dated append under its own `Corrections after filing`
section, on the form F92 set on that file; accepted in the same instruction, not made here.

---

## 7. What a go-ahead lands, disclosed

**Landing this commit *creates* 284 red documents, and that is the disclosure the previous ask
did not have at the right size.** Check 37 (`check_shape`) derives a required body-section set
from each family's template and applies it to documents the migration stamps rather than
authors. Run against a fully migrated disposable snapshot of `32fc63c`, then the real
`check_shape()` with `_ID_SCOPE_ROOTS` widened, check 37 examines **529** documents and reds
**284** — plan 119 · **ruling 95** · closure 38 · proposal 20 · ledger 10 · research 2.

**F90's own figure of 95 across one family is corrected by this measurement** (PR #656,
unmerged at `796cd07`; the amendment is cited to that PR and not to `main`). **And F90's
option 4 does not do what F90 says**: *"the only option of the four that makes Ruling 95 pass
as measured"* is measured at **95 → 95**, because three of the four required sections —
`Question`, `Ruling`, `Rationale` — exist in **0 of 95** documents at any heading depth,
numbered or not. **These documents do not exist until the run creates them**, so a completing
run is precisely what produces the red.

**That is why one thing is reserved and asked separately** (§8), rather than folded into §10.

**The other four disclosures, each already dispositioned and none a condition on this ask.**
**F87** — a disclosure by the maintainer's dated line. Re-measured at `796cd07`:
`audit-docs.py`'s check 33 reports **1 header checked in scope**, so checks 30–39 reach 0 of the
65 exempt files. Landing leaves it as bad as it is and improves it slightly (0 → 3 of 65, the
superseded ask's measurement), fixable without a second irreversible act. **F92** — 53 files deferred out of §4 step 5's Reference stamp set, a
declared deferral stamped in **W37-11** with acceptance item 13. **F94** — the plan's
ruling-heading census uses a looser predicate than the shipped splitter and the two candidates
diverge; not blocking, no acceptance item depends on either figure, carried to the closure
record under the stopping rule. **The Ruling 66 enlargement** — the commit folds in every
instrument whose output checks 30–39 test, which the roadmap's W37 row requires this ask to
disclose; this sentence is that disclosure.

**Accepting this run is not accepting the Work close** — NT-0019 §7's items (i), (j) and (k)
belong to later slices, and a Work close is a separate dated line reserved to the maintainer
(`CLAUDE.md` §12). **A stopping rule is in force**: findings raised after this document's tree
go to **W37-6's closure record**, not to a further precondition slice
([`…-second-withholding-and-standing-rules.md`](2026-09-02-w37-6-second-withholding-and-standing-rules.md)
§5).

---

## 8. What is reserved to the maintainer today, and is not asked here

**One batch, one document**, per the maintainer's standing rule 4:
[`2026-09-03-w37-6-maintainer-decisions.md`](2026-09-03-w37-6-maintainer-decisions.md). **D1** —
*does `check_shape` apply at all to a body the migration carried over verbatim from a
pre-standard file?*, the prior question all four of F90's options answer a narrower version of,
governing all 284. **D2** — whether the F90 slice as ordered on 2026-09-02 still stands, given
that the depth-agnostic remedy the order names is measured at 95 → 95 and cannot make the
rulings *"green on creation"*. **They are there because they are decisions and §10 is an
authorisation**: if §10 is signed before D1 is ruled, the run lands 284 reds and D1 becomes a
question about a red gate rather than about a check's jurisdiction.

---

## 9. Recommendation

**The planner assembles and decides nothing; this is a recommendation, not a conclusion.**

1. **On the run — `[SLOT-3]` reads `completes`, the only state the maintainer accepts as
   fileable, and the recommendation is go ahead conditional on D1 being ruled first.** Not an
   extra demand but §7's own arithmetic: **the better `[SLOT-3]` gets, the sooner F90 bites**,
   because the 284 red documents are created by a run that completes.
2. **On F90 — rule the prior question rather than pick from the four.** The executor who
   measured all four recommends it and the lead concurs; D1 carries the reasoning and the four
   shapes of answer, priced.
3. **On the safe remedy — available with or without D1.** An asymmetric detector plus ordinal
   tolerance leaves all twelve families' required sets byte-identical and can only turn a red
   green — but **it turns no document green today** and is not a discharge of F90.
4. **On the gap — §6 is the accepted condition restated, and `[SLOT-4]` stays unfilled until
   the branch is cut.**

---

## 10. Maintainer's line

**This section is the maintainer's alone.** Nothing above authorises the run. Per `CLAUDE.md`
§14, the acceptance line is explicit and dated.

> **Decision:**
>
> **Date:**

---

## Standing facts

**W37-6 has not run**; everything merged is preconditions. **Rulings 66–95 are filed, all on
`main`**, next free 96. **Full local `uv run pytest -q` is not run by the team** — concurrent
runs OOM-kill each other and `docs/plans/` fixture tests collide with a concurrent
`audit-docs.py` run (F89). CI runs the identical command in a clean environment.
