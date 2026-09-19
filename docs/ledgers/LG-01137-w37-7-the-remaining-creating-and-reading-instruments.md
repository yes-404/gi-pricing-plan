---
id: LG-1137
family: ledger
title: W37-7 — the remaining creating and reading instruments
status: active
created: 2026-09-19
owner: executor
tree: 3344de9c8a4d1e0f5b7c2a9e6d4f8b3c1a5e7d92
phase: P2
work: WK-697
plans: [PL-1070]
corrected_by: []
relates: []
---

# LG-1137 — W37-7 — the remaining creating and reading instruments

**This ledger's id is the first allocation outside the reserved block.** Every governed
document this work item minted before it reused a number reserved in `docs/REDIRECTS.csv` —
fifteen consecutively at `3803331`, sixteen by `a800c57`, seventeen by `a1241a8`.

**Stated with its predicate, because the number alone is not the evidence.** At `3344de9c`,
with Task 16's emission landed:

```
python3 scripts/doc-id.py next --ref HEAD      2>/dev/null   →  1137
python3 scripts/doc-id.py next                 2>/dev/null   →  1079   # reads origin/main
```

1137 is one past the reserved block's top; 1079 is inside it. The same command against the
two refs, one carrying the fix and one not. **And check 31 is green at both** — which is the
half that matters, because every option `RL-1078` refused would have moved `next` past the
block while the index still stopped short, opening the gap check 31 fails on. The fix and
the contiguity clause agree rather than trading off.

So this ledger is both the record of the slice and the first evidence that the slice's own
fix works: **the first id this repository has minted that collides with nothing.**

**The `slice:` field is omitted.** `docs/_templates/LG.md` lists it and says to remove any
field a ledger does not use. **No `SL-` row has ever been minted** — that is `FD-1074`'s
finding — so a `slice:` value here would name an id nobody allocated. `PL-1070`'s own header
omits it on the same precedent.

## Tasks

One entry per task, in plan order. Task 15 is sequenced before 16, and 16 before 14, per the
plan's own append-only numbering.

| Task | Commit | What it discharged |
|---|---|---|
| 1 | `e87b02d4` | `docs-audit` — the RFC-937 filing grammar replaces the retired dated form |
| 1 Step 3 | `1271ed52` | checks 31 and 38 gained a describing clause (`RL-1077`) |
| 2 | `26f3e8cb`, `d72de42a` | `dev-commands` / `doc-id-migration-run` — the `doc-id`/`doc-index` commands and R13-3. The first is a **partial halt** commit, kept |
| 3 | `52b7c5a4` | `git-hygiene` — the `sl-<n>` branch and `SL-<n>` PR-title grammars |
| 4 | `ced41783` | `reporter-cycle` — the fortnightly `WK-` entry, documented as **required and absent** |
| 5 | `c54cca48`, `60698b0d` | `repo-architecture` — the `docs/` tree from `RFC-937` §1.4, and a ceiling fix |
| 6 | `9304a7ee` | the `req` marker form, recorded in the README; `testing-strategy` untouched |
| 7 | `db01af33` | `brainstorming`, `planning-with-files` — scratch is not a governed document |
| 8 | `d933cd5f` | skills `README` — a `Creates` column per creating skill |
| 9 | `1271ed52` | the bespoke-audit rule — full in `close-workstream`, pointer in `docs-audit` |
| 10 | `553744d1` | `writing-plans` — the `PL-<nnnnn>-<slug>` filing grammar |
| 11 | `cedbf713` | `subagent-driven-development` — `LG-` routing and the append rule |
| 12 | `d7bb0aff` | `watcher-runtime-state` — refuse an unresolvable `read_from` locator |
| 13 | `36b339f4` | check 35 — F92's owner of record (`RL-1075`) |
| 15 | `3d4dd7ae` | the salvaged `audit-docs` work reconciled — **all three hunks superseded** |
| 16 | `3344de9c` | emit reserved allocations into `docs/INDEX.md` (`RL-1078`) |
| — | `5696c7b2`, `a7d7f99f`, `9e27d63e` | the planner's three rounds of texts, landed verbatim |
| — | `9cffab69` | the lead's plan-dating commit and freeze-clause breach finding |

**Task 6's `python-test` half is a verification, not a commit**, as the plan requires:
`grep -n 'mark.req' .claude/skills/python-test/SKILL.md` → `16:@pytest.mark.req("FR-10")`,
already correct from W37-6's chain, and `git diff --stat` over that file and
`testing-strategy` is **empty**. An unnecessary edit to a file another slice closed is how a
closed row is reopened.

**Task 15 landed no file change**, and `3d4dd7ae` is deliberately an empty commit carrying
the disposition. A reconciliation whose correct outcome is "nothing to land" has no diff to
carry it, and a finding with no file change is what goes missing from a repository's
history.

## Verdicts

### `PL-939` Acceptance Standard item 4 — the root-restricted legacy sweep

**NOT SATISFIED at this tree. The bar is not lowered.** Restricted to `.claude/skills/`
the sweep returns **31 fatal** hits, and has done since before this slice began.

- **Predicate, by symbol never pasted:** `audit-docs.py`'s own `_sweep_legacy_form_hits` /
  `sweep_legacy_forms` with `LEGACY_FORM_PATTERNS` and `LEGACY_FORM_EXCLUDED_PATHS` as
  shipped, split by `_legacy_form_disclosure_reason`.
- **Corpus:** 400 tracked files under `.claude/skills/`.
- **Split:** 31 fatal, 118 disclosed. **Reported as a split, never a bare zero** — check 36
  carries a standing disclosed class, so a bare zero would report where a threshold sits
  rather than how clean the population is.
- **Attribution by line text at `origin/main`, not by line number**, because this branch
  inserted lines above several: 29 of 31 present verbatim at `origin/main`; the other two
  are README rows whose lines changed only by re-dating and the new `Creates` cell, with
  **tokens unchanged**: a `grep -c` for each of the two legacy tokens those rows carry — one
  a retired working-notes path, one a scoped requirement id — returns **1 at `origin/main`
  and 1 here**. *(The tokens are described rather than spelled: spelling them here would add
  two hits to a pooled class this ledger's own entry below says not to spend. Take them from
  the sweep output, which is the authoritative list.)*

**This branch's net contribution to the fatal population is zero, and it removed one it had
added** (`60698b0d`). The 31 are W37-11's residue.

**Proven non-vacuous.** One retired path reinstated in a scratch copy of
`git-hygiene/SKILL.md`: the sweep went 31 → 32 and named the file and line, and
`audit-docs.py` went `EXIT=0` → `EXIT=1` on the same line through check 36. Both restored
from byte-checked backups; the broken input is in no commit.

### `PL-1070` Acceptance Standard item 5

Its verdict is carried by **Annotation F in the plan itself**, which is the planner's text
and not restated here. **A correction to that annotation's stated ground is in flight** and
lands verbatim when it reaches this executor; this ledger does not anticipate it.

## Findings and rules this slice established

### Routed to W37-11 — not settled here

1. **Predicate (i) stops measuring the harm after Task 16.** It read 17 pre-fix and reads
   **74** post-fix, because the population changed: pre-fix it measured *reuse*, post-fix
   *visibility*. Either retire it with a dated line, or redefine it as **reserved numbers
   carrying a record that is not their own reservation** — which reads 17 on both sides.
2. **`RL-1078` §(vi)'s residue class** still needs a verdict and an owner.
3. **check 39 prints a claim that is false at this tree.** Its note says *"docs/ledgers/
   does not exist in scope yet"*; `docs/ledgers/` holds tracked `LG-` files and is indexed.
   It is a hardcoded literal in a `notes.append(...)`, computed from nothing, and **because
   it is a note rather than a failure nothing will ever red on it.**
4. **`document-ids.md` §1.9 claims a lint that does not exist** — *"Lint checks that a merged
   PR's title names the `SL-` it delivered"*. `grep -c 'SL-' .github/PULL_REQUEST_TEMPLATE.md`
   → 0; `grep -rn 'SL-' .github/workflows/` → nothing; check 39's own docstring concedes the
   PR-title half needs GitHub context the tool lacks.
5. **The migration updated a manifest and missed the file beneath it.**
   `subagent-driven-development/scripts/task-brief` cited two plans by pre-migration dated
   filenames, both **MISSING**, while the README's entry for that same script already cited
   the migrated names. A live instance of `CR-1065:199-202`'s mechanism, not a described risk.
6. **The plan's per-task "refresh `Verified`" step assumes a repo-local skill shape.** For
   the four vendored skills it was **inapplicable four times over** — none has a `Verified`
   section, none of their rows sits in a table with a date column. A finding against the
   plan's template.

### Method rules, established by being violated

- **A test for a check asserts through that check's own predicate, never a reimplementation
  of it.** Task 16's contiguity test first walked `build_corpus`'s records into a **list**
  and reported gaps like `(538, 538)` — duplicates, an artefact of the predicate rather than
  a property of the corpus. Check 31 reads `INDEX.md`'s text with `ID_RE.finditer` into a
  **set**. It caught itself only because the number looked impossible.
- **A table of line numbers in a frozen ruling begins going stale the moment anything above
  them changes.** `RL-1075`'s own citations were stale within hours: its must-not-change
  text moved from `:684` to `:686`, and `:2443` — cited as the helper's definition — became
  a comment line. **Match on text; treat numbers as a starting hint.** The Task 13 guard was
  keyed to `(path, anchor-text)` pairs; keyed to the ruling's line numbers it would now be
  asserting against a blank line and a `-> None:` fragment — **green while protecting
  nothing.**
- **A ruling's occurrence table classifies *meanings*; it is not the population.** Enumerate
  occurrences yourself at your own tree and classify each against it. The enumeration found
  **eleven sites beyond `RL-1075`'s table**, in `scripts/register-lint.py` and
  `scripts/_docverify.py`; all classified as correct and none was touched.
- **Being outside a checker's scope is an accident of scope, not a permission.**
- **`EXIT=0` did not mean "added nothing". It meant "nothing went over a ceiling."** Check
  36's split runs against a **pooled** residue ceiling keyed by `(path, class)`. A hit this
  slice added to `repo-architecture/SKILL.md` was **absorbed silently** because that file had
  headroom. A ceiling is never raised; the correct response is to not spend it, because
  spending another file's headroom flips a later, innocent hit to fatal in a slice that did
  not cause it. This is one of a matched pair with the decision-maker's opposite-direction
  finding: **a green gate is not evidence a change added nothing to a pooled class, and a
  red one is not evidence the change caused it.**
- **A gate result scored against a pooled ceiling carries its tree *and the ceiling reading
  as that run printed it*.** At `3344de9c`: `DISCLOSED (890, at or under the W37-11 residue
  ceiling)`.
- **DP-7-3 reaches the four vendored manifests it enumerates and no others.** Hence
  `brainstorming`, `planning-with-files`, `writing-plans` and `subagent-driven-development`
  edited **and** recorded as deviations; `testing-strategy` recorded in the README with its
  file untouched, because a decision point cannot override `CLAUDE.md` §12 for a file it
  never considered.
- **Where a plan can be read as permitting a paste, `CLAUDE.md` §13 decides it.** Item 4's
  wording admitted both readings; the shipped symbol wins, because a pasted regex is a second
  copy that can drift from the one the gate actually uses.
- **A fragment read gets an invented frame, and a truncating pipe is a fragment read that
  does not announce itself.** Reading `PL-960:648` through `cut -c1-200` supported the
  conclusion that `PL-1070` had cited the wrong line; the quote was the **tail** of that same
  long row. A false finding against a correct citation was one message away.

### One root cause, seven faces — checks answering a narrower question than they appear to

| # | Where | What happened |
|---|---|---|
| 1 | check 32 | a worked example **quoted from the document that defines it** → 3 failures |
| 2 | check 36 | a retired path named **in order to mark it retired** → 4 failures |
| 3 | check 39 | a hardcoded note claiming `docs/ledgers/` does not exist |
| 4 | check 32 | the collision block's endpoints, in the finding **about** unresolvable ids |
| 5 | check 22 | **does not cover `.claude/`** — the plan promised a red that cannot come |
| 6 | §1.9 | claims an `SL-` PR-title lint that does not exist |
| 7 | a **test** | proved *"fields name the artifact they were read from"* while naming one that did not exist |

Faces 1, 2 and 4 fired on input not constructed to suit them, named the right file and line,
and returned to `EXIT=0` as the forms were removed. **Two were produced by doing the careful
thing** — naming a retired path in order to retire it, and quoting a worked example in order
to cite it — so the checks penalise precisely the most conscientious drafting.

**Face 5 is the inverse and the most dangerous**: `PL-1070`'s Risk 2 promises the cell-count
check reds a partly-applied column. It cannot — check 22's population is `docs/` plus
`CLAUDE.md`. Proven both ways: the defect in `.claude/skills/README.md` gives `EXIT=0`, the
same defect in `docs/README.md` gives `EXIT=1` naming the table. **The `Creates` column is
complete only because the edit was applied by a script that refuses a row it has no value
for** — written for an unrelated reason, and the only thing enforcing it.

**Face 7's assertion was left exactly as it was.** Changing it to match would have destroyed
the record of what it actually checked; the gap between what it says it proves and what it
proves *is* the finding.

## Ops actions asked for, not performed here

**DP-7-2 default (a): the live runtime state file is not touched.**
`~/gi-pricing-plan.local/handover/runtime-state.json` is outside the repository by design
(`delivery-process.md` §10) and still carries its dangling `read_from` locators. Rewriting
it is the watcher's, not an executor's. Task 12's guard now **forces** the next cycle to
supply resolvable ones, so the defect cannot be re-minted.

## PRs

| PR | Title | Merge commit |
|---|---|---|
| #795 | W37-7 — the remaining creating and reading instruments | _open, draft_ |
