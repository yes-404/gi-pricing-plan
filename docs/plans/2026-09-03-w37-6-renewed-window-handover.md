# W37-6 — handover at the halt of the renewed delegated window, 2026-09-03

**Written** 2026-09-03 by the lead, in the shape of
[`2026-08-20-w5-worker-handover.md`](2026-08-20-w5-worker-handover.md). Work item **W37-6**,
phase 2.

**The renewed window opened `2026-09-03T08:43:13Z`** — §6.2 of
[`2026-09-03-w37-6-time-boxed-delegation.md`](2026-09-03-w37-6-time-boxed-delegation.md) —
**and is halted before its `16:43:13Z` expiry on the delegation's own rule: a second gate
failure.** *"One fail → fix, back to Step 3; second fail → halt protocol."*

## 1. The headline

**The migration did not run. The gate caught two real defects before the irreversible write,
and the second is not fixable inside this window.**

**`§7(a)`'s bar was met — `none` is 0.** Every one of the six gate conditions was measured.
Four passed at the final tree. **What stopped the run is a defect the six conditions do not
name**: 36 live markdown links, in 5 surviving files, that resolve to paths the migration
deletes. A broken citation inside a one-way commit is the failure this apparatus exists to
prevent.

**Nothing is half-done. `main` is green, no PR is open, no branch is outstanding, and no
migration was attempted against any real checkout at any point.** Ten PRs merged, all
verified on their exact head SHA.

## 2. Final state

| | |
|---|---|
| **Tree** | `07f1e412ad0080b7b40b44c0f495e4716cec68cf` |
| **Open PRs** | none |
| **Non-`main` branches** | none |
| **Preserved evidence** | tag `evidence/w37-6-reask-v1` → `fcd7068`, confirmed on the remote |
| **`none` (NT-0019 §7(a))** | **0** — buckets summing to 460 = `git ls-files docs/` |
| **CI on `main`** | green at merge for every PR below |
| **Disk** | 6.0 GB free, 79% — was 1.3 GB / 96%; 52 stale worktrees cleared |

## 3. Merged in the window — ten PRs

| PR | Landed | |
|---|---|---|
| #664 | `e56d038` | **the renewal itself** (§6), plus two maintainer rulings: condition 2 accepted with its disclosure, and a tagged evidence ref is not an open branch |
| #665 | `d1cabe1` | **Ruling 98** — maintainer prose rulings migrate as `RL-`, `owner: maintainer`, no `kind:` |
| #666 | `735c828` | register reconciliation — F77 discharged, F90 dispositioned, F92 reassigned to W37-11 |
| #668 | `c039729` | **F95** — nine declared Document families, seven implemented, in two maps |
| #669 | `54a3ee5` | **Ruling 99** — the three undeclared files reach destinations; no halt |
| #670 | `0042957` | Ruling 98's own heading fix, plus **F96** |
| #671 | `2f0467e` | **the freeze commit** — `FD`/`WF` families, fourteen relocations, `none` 110 → 0 |
| #667 | `8d1f9d0` | the go-ahead re-ask re-filled at the frozen tree; §10's signing authority corrected |
| #672 | `07f1e41` | the citation-rewrite fix — six relocation mechanisms |

## 4. The gate, condition by condition, at `07f1e41`

| # | Condition | State |
|---|---|---|
| 1 | Independent instrument, `migrate()` completes, family sum | **Met.** `MigrateResult` returned, `warnings=0`; `ADR 6 · CR 40 · FD 34 · LG 10 · PL 125 · RFC 20 · RL 99 · RS 6 · WF 5` = **345**, zero unfamilied; bucketed total = raw total (1479 = 1479) |
| 2 | `check 37` reds 0 | **Met**, with the disclosure of §5 — measured at `2f0467e` |
| 3 | Every `register-owed.py W37-6` row dispositioned | **Met.** 13 rows, 1 excluded (F76). Full generated output byte-identical to the prior pass but for the header SHA |
| 4 | Re-ask under 300 lines, `SLOT`s 0–3, §9 recommends | **Met.** 288 lines, `SLOT`s 0–3 filled, `SLOT-4` deliberately unfilled, §9 recommends go |
| 5 | No open branches | **Met.** None; the preserved branch deleted only after its tag was re-confirmed on the remote |
| 6 | `git revert` byte-identical | **Met.** Tree-object hash identity, clean status, and an independent sha256 digest identity — all three |

**All six met. The run still did not happen**, for the reason in §6.

## 5. The disclosure that must travel with condition 2

Ruling 97 §4 binds four figures and they must not be quoted apart:

**0 red · 588 examined · 349 exempt by `was:` · and the broken-input proof.**

**The enforced population is 0.** Every document carrying a non-empty required set is exempt
by `was:`. That is Ruling 96's own consequence, not a defect — but the ruling that makes
condition 2 satisfiable is the ruling that empties the population it measures over. **The
evidence is the control, not the zero.** *(531/292 at `e56d038` when §6.3 accepted it; the
figures moved with the corpus, the verdict did not.)*

## 6. Why the run was stopped — the second fail

**36 live markdown links, in 5 surviving files, resolve to paths the migration deletes:**

```
19  docs/notes/README.md      6  docs/adr/README.md       5  docs/audit/README.md
 5  docs/workflows/README.md  1  docs/plans/README.md
```

Found by a **general dangling-link scanner** the auditor built — every `](...)` in the
post-migration tree, resolved relative to its citing file, checked against the full 262-path
deleted set.

**NT-0019 §5.2 says these READMEs are regenerated, and the code does not do it.** Line 317:
*"`adr/000n-*.md` (6) + README … README **generated**"*. Line 318: *"`notes/00nn-*.md` (18)
+ README … **README rewritten**, index table dropped for `INDEX.md`"*. They survive intact,
with their old index tables linking to files that no longer exist.

**This is the sixth decided-but-unimplemented item of the window** (§8), and unlike the
others the remedy is **content generation**, not a token repoint.

**The verification that had closed this class was false.** The executor reported
`grep -c '](' ` returning **0** for all five files. Run directly against `origin/main`, they
return **20, 6, 8, 6, 5**. The lead accepted that claim; the auditor refuted it by running
the command itself. **A third fix round on a rushed clock, resting on a verifier that had
just produced a false negative on this exact question, was not a trade worth making.**

## 7. Findings for the closure record

1. **The dangling-link class** — §6 above. The scanner exists and should be kept.
2. **`F12` and the low-range ambiguity.** Three independent audit eras each minted their own
   low F-range — Track A `F1`–`F15`, the W5 ledger `F1`–`F12`, phase-1b `F1`–`F25`. `F12`
   alone names three different findings across four documents. **W37-11's alias resolver
   cannot be a simple `F<n>` → `FD-<nnnnn>` map.**
3. **The `was:` path corruption — mechanism-scoped.** `_rewrite_citations` cannot distinguish
   a citation from a path component. Reverting the fix rewrites a finding's `was:` provenance
   path to `docs/audit/findings/FD-1010.md`, **a path that never existed**, on **any** finding
   with an essay, every time. The `FD` exclusion fixes findings only; every other prefix runs
   through the same substitution.
4. **F23/F24/F25 structural drift** — three rows of `docs/audit/phases/1b/register.md` split
   into 3 fields where the table declares 4. `register-lint.py` would have reported them had
   it ever been run against that file; that it never was is the more interesting half.
5. **The checklists' undelivered content obligation** — §5.2 `:326`'s "gains" sentences exist
   nowhere in the tree except the map plan restating the instruction. The files moved; the
   prose was deliberately not authored.
6. **§7(d)'s predicate cannot distinguish a stale citation from a live sentence naming the
   correct new path** — `.claude/notes/` redirect stubs count as legacy-form hits. 2332 hits,
   1196 separable as `F<n>`-only, 1136 not.
7. **§7(f) compared against `8f5d57d` conflates migration effect with corpus growth.** Now
   measured pre-versus-post on one snapshot. Third instance of a standard written against one
   tree read literally against a moved one.
8. **§7(g) jumped 60 → 343 violations** between the two quiet trees, unexplained. Evidence-only
   by instruction, but a 5.7× jump immediately after a fix is a signal, not noise. **Not chased.**
9. **F95's register row is stale** — it reads "not started / in progress" while #671 landed both
   halves. Fourth instance of a row overtaken by a later merged decision its own text never
   cites (cf. F77, F90, F92).
10. **The `cp -a .git` worktree-index trap** — a worktree's `.git` is a pointer file, so a copy
    shares the original's per-worktree index and writes in `/tmp` land in the real staging area.

## 8. The structural finding — six decided-but-unimplemented items in one window

**A merged ruling changes no behaviour until code implements it, and nothing in the
repository flags the gap.**

| Decision | State at halt |
|---|---|
| `FD`/`WF` declared families (F95) | **fixed** (#671) |
| Citation-form rewrite | **deferred to W37-11 by ruling**, implemented as a deferral (#671) |
| F96's ruling-heading convention | **fixed** (#670) |
| Ruling 98's substantive rule | **unimplemented** — seven maintainer decisions still migrate as `owner: planner` |
| The six relocation mechanisms' citations | **fixed** (#672) |
| §5.2's README regeneration | **unimplemented** — §6 above, the halt cause |

## 9. Defects caught before the irreversible write

- **The dangling link**, from a single unexplained unit: `MigrateResult.files_deleted` 261
  against `git status` 262 and a traced count of 262 — two independent methods agreeing
  against the run's own self-report. Chasing that one file found no `REDIRECTS.csv` row and a
  dangling link in `docs/roadmap.md`. Then the mechanism, six times larger: **25 files** citing
  paths that would be dead.
- **The `was:` provenance corruption** — deterministic, on every migrated finding.
- **34 findings double-numbered** without an exclusion filter (F71 receiving both `FD-1102`
  and `FD-1067`).
- **Three idempotency bugs**, one class, in the re-run path the revert proof depends on.
- **Disk at 96% with 1.3 GB free** — a fill mid-`migrate()` produces the partial write
  `git revert` cannot recover. Cleared to 6.0 GB.

## 10. Resume — one line per agent

**Every agent is complete or holding; spawn fresh, one per task.**

| Task | How to resume |
|---|---|
| **The README regeneration** | Implement §5.2 lines 317–318 — `docs/{notes,adr,audit,workflows,plans}/README.md` regenerated, not carried. **The acceptance test exists**: the auditor's general dangling-link scanner must return **zero** |
| **Re-run the gate** | All six conditions re-measured at a new quiet tree. The auditor's instrument runs unchanged; only the snapshot ref changes |
| **Ruling 98's implementation** | Seven documents to `RL-`/`owner: maintainer`; `_discover_plain_plans`' catch-all does not do it |
| **§7(g)'s 343** | Explain the 60 → 343 jump before the next go-ahead |

## 11. Hourly lines

- **`08:43`–`10:00`** — renewal filed and merged (#664). Three worktrees dropped after salvage. `evidence/w37-6-reask-v1` tagged and confirmed on the remote. Rulings 98 and 99 filed; F95, F96 filed. `none` diagnosed at 110.
- **`10:00`–`11:00`** — #665, #666, #668, #669, #670 merged. **#671, the freeze commit**, merged `10:53:47Z` — `FD`/`WF` implemented, fourteen relocations, `none` → 0. Freeze in force.
- **`11:00`–`12:00`** — #667 merged `11:16:42Z`; branch deleted; **first quiet tree `8d1f9d0`**. Gate measured — and the one-file deletion discrepancy found, chased to a dangling link, then to a six-mechanism defect. Disk cleared 1.3 GB → 6.1 GB.
- **`12:00`–`12:20`** — #672 merged; **second quiet tree `07f1e41`**; all six conditions met; the Slack cycle restarted after a 14-hour outage; **the 36-link finding**; halt called.

## Acceptance Standard

**This record is accepted when it is committed to `main`** — the delegation's §4 step 3 is the
commit, not the writing: *"a handover written and not committed is the failure the W5 record
exists to prevent."*

### Acceptance — the violation that must become detectable

*Violation: the migration run while §5.2's README regeneration is unimplemented — 36 dangling
links would land inside the irreversible commit.*

*Violation: condition 2 quoted as `0 red` without the enforced-population-0 disclosure and its
control.*

*Violation: a gate condition recorded as met at a tree other than the one the ask is made from.*

*Violation: W37-11's alias resolver built as a simple `F<n>` → `FD-<nnnnn>` map.*

*Violation: this window's work resumed by reviving an agent rather than spawning a fresh one.*
