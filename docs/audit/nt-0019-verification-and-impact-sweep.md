# NT-0019 verification and impact-sweep — audit record

| | |
|---|---|
| **Date** | 2026-09-01 (filed 2026-09-02) |
| **Auditor** | this session, dispatched by the lead the day NT-0019 (`docs/notes/0019-one-id-per-document.md`) merged as PR #555 |
| **Pin** | `89dd2b1` throughout, except where a section explicitly re-checks a later tip (`bc7bc36`, `d4e094b`) and says so |
| **Why this exists** | Filed only in a chat message to the lead until now — the durable-landing gap CLAUDE.md §12 and this role's own charter both name. `docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md` (PR #557, merged `106e322`) makes this durability load-bearing rather than a formality: **W37-6** (the migration-run slice) lists "the auditor's sweep" as a named precondition alongside DP-1/DP-2/DP-3 and the gap condition, and states outright — "W37-6's leaf plan must be written against that sweep's result, not against this table: the table above sizes the slices, the sweep enumerates the rows" (map plan, after its own evidence table). This record is that result. |
| **Scope not duplicated here** | The map plan ran its own independent verification of NT-0019's §5.1–§5.5, §5.7 and §5.8 populations (docs/plans, docs/notes, `.claude/notes`, docs/audit, docs/research, docs/adr, docs/workflows, docs/specs, `.claude/skills`, `.claude/roles`, `.claude/agents`, scripts) and explicitly declined to duplicate NT-0019's own §5.6 code-citation counts, assigning them here by name. Both sweeps are reported below, cross-checked against each other where they overlap (§4). |

## 1. Transcription claim — verified, holds with one disclosed wrinkle

PR #555's body claimed **"three mechanical adaptations and nothing else"**: the maintainer's
original inbox wording (`~/gi-pricing-plan.local/inbox/0019-one-id-per-document.md`, not under
version control) versus the merged note, differing only in three width-5 ADR filename
examples (§1.4, §3, §5.2) rendered as an `<nnnnn>` placeholder, because `audit-docs.py` check
19's `ADR-(\d{4})` pattern would read a literal five-digit padded ADR filename number as a
reference to a nonexistent ADR — rendered in this record as `ADR-000`+`01` rather than one
unbroken four-digit run, specifically so this sentence does not retrigger the same check it
describes.

**Method:** `diff -u` between the two files, both 468 lines (55438 vs 55475 bytes). Exactly
three hunks, each one line, nowhere else in the 468-line document — meaning §1's four rules
(1.1) and all of §1.2–1.13, and §2's fifteen decisions D0–D14, are **byte-identical** between
the maintainer's source and the merged note. Hunk locations confirmed against the heading
list: line 88 = §1.4, line 264 = §3, line 317 = §5.2 — exactly the three the PR named.

- **§1.4 (line 88)** and **§5.2 (line 317)**: clean digit-run → `<nnnnn>` swaps, nothing else
  changed on either line.
- **§3 (line 264) — the disclosed wrinkle**: original `` `docs/adrs/ADR-000`+`01-…`, cited
  `ADR-1` `` (digits split as above for the same reason; note the ellipsis) → merged
  `` `docs/adrs/ADR-<nnnnn>-pricing-core-is-
  dependency-free.md`, cited `ADR-1` ``. Beyond the digit-to-placeholder swap, the trailing
  "…" was silently expanded into the full literal filename tail
  `-pricing-core-is-dependency-free.md`, text absent from the maintainer's original at that
  spot entirely. It touches no rule and no decision, and does not change what the example
  illustrates — but "three mechanical adaptations and nothing else" is not quite literally
  true: one of the three bundles an unstated fourth edit.

**Independently verified the stated cause, not just trusted it.** `scripts/audit-docs.py`
hard-codes `ADR-(\d{4})` at exactly two sites (`grep -n 'ADR-' scripts/audit-docs.py`):
line 471 (check 19, inside the per-note reference-resolution loop, comment "# 19. every
reference resolves") and line 1117 (the corpus-wide ADR-existence check, "# 5. ADRs"). Swept
**every** `ADR-` occurrence in the merged note (15 total) and confirmed the twelve not
converted are all safe under this exact regex: bare short-form citations (`ADR-1`/`ADR-2`/
`ADR-3`, no 4-digit run), references to real existing ADRs (`ADR-0001`/`ADR-0002`, which
resolve against `docs/adr/`), fewer than four consecutive digits (`ADR-000n` — three digits
then a letter breaks the run), a regex-as-text example (`ADR-0[0-9]{3}`, whose literal
character after `ADR-` is `0` then `[`, not four digits), or an already-placeholder form
(`ADR-<nnnnn>-<slug>.md`, used elsewhere in the maintainer's own original). Exactly three
needed the fix; exactly three got it — the same "two sites" finding the map plan's own,
independent check of this same claim reached (§4).

**Verdict: holds on substance (§1 and §2 are the untouched null result; the right three
locations for the right stated reason) but not on literal completeness.** Report the §3
ellipsis-expansion as a real, disclosed, minor transcription defect against the PR body's
specific wording — separate from, and much smaller than, the substantive null finding above.

## 2. §5 impact-map sweep — every class, pinned at `89dd2b1`

All commands below are reproducible verbatim; none touch the working tree (`git show`,
`git ls-tree`, `git grep <pattern> 89dd2b1 [-- <path>]` throughout — never a working-tree
grep, per the standing trap this repository has hit before). Where NT-0019 §10 gave an exact
evidence command, that exact command was re-run at the pin rather than reinvented, because
that discipline is what surfaced the two material findings in §2.6.

### 2.1 §5.1 — Root governance

| Item | Command (pinned `89dd2b1`) | Measured | Claim | Agrees? |
|---|---|---|---|---|
| `.github/ISSUE_TEMPLATE/*.yml` count | `git ls-tree -r --name-only 89dd2b1 -- .github/ISSUE_TEMPLATE \| grep -cE '\.yml$'` | 2 | (no number claimed) | n/a |
| `packages/*/pyproject.toml` | `git ls-tree -r --name-only 89dd2b1 -- packages \| grep -E 'pyproject\.toml$'` | 2 (`model-schema`, `pricing-core`) | (no number claimed) | n/a |
| `.gitignore` "comment block lines 91–108" | `git show 89dd2b1:.gitignore \| cat -n \| sed -n '88,110p'` | Block runs exactly 91–108 and cites `NT-NNNN in docs/notes/`, which does need rewording after the migration | "reworded to the new families" | Yes — read the full block, not just grepped for the word "family"; a keyword-only search would have missed this |

### 2.2 §5.2 — `docs/`

| Item | Command (pinned) | Measured | Claim | Agrees? |
|---|---|---|---|---|
| `specs/*.md` | `git ls-tree -r --name-only 89dd2b1 -- docs/specs \| grep -cE '^docs/specs/[^/]+\.md$'` | 8 | 8 | Yes |
| `workflows/wf-*.md` | same pattern, `docs/workflows` | 5 | 5 | Yes |
| `adr/*.md` | same pattern, `docs/adr` | 6 | 6 | Yes |
| `notes/*.md` | same pattern, `docs/notes` | **19** | 18 | Close, explained: `git diff --name-status 8f5d57d 89dd2b1 -- docs/notes` shows one addition, `0019-one-id-per-document.md` itself — the note's own evidence predates its own filing. Counting after, as the dispatch required, adds one. The population to migrate is 19, not 18 (NT-0019 migrates itself last, per its own Owner row). |
| `plans/2026-*.md` | same pattern, `docs/plans` | **126** | 125 | Close, explained: `git diff --name-status 8f5d57d 89dd2b1 -- docs/plans` shows one genuine unrelated addition, `2026-09-01-nt-0016-landing-package.md`, from ordinary activity in the 6-commit gap between the note's evidence point and this pin. Population to slice is 126. |
| `research/*.md` | same pattern | 11 | 11 | Yes |
| `audit/findings/F*.md` | same pattern | 5 | 5 | Yes |
| `audit/work/*/README.md` | `grep -cE '/README\.md$'` | 15 | 15 | Yes |

### 2.3 §5.3 — `.claude/`

| Item | Command (pinned) | Measured | Claim | Agrees? |
|---|---|---|---|---|
| Role charters | `git ls-tree -r --name-only 89dd2b1 -- .claude/roles` | 7 (auditor, decision-maker, executor, lead, planner, reporter, watcher) | "seven role charters" | Yes, exact |
| Agents | Per-file `git grep -lE '<citation regex>' 89dd2b1 -- .claude/agents/*.md`, all 8 files individually | `performance-engineer.md` carries two real `NFR-PLAT-4` citations (lines 16, 20), named nowhere in §5.3's agents row or the "two agents" count. `ci-watcher.md` and `spec-reconciler.md` (the two named) do each carry real citations (`ADR-0002` in spec-reconciler; CI path-filter facts in ci-watcher — a different citation *type*, not a false claim). `accessibility-tester.md`, `evidence-collector.md`, `gate-runner.md`, `postgres-pro.md`: clean, correctly unnamed. | "two agents" | **No — undercounts.** Independently corroborated (§4): the map plan's own sweep separately counted **7** non-README files under `.claude/agents/`, agreeing with the raw population here even though it did not check which ones carry citations. |

**Addendum — the same undercount reproduced itself inside the map plan, one step downstream,
after the map plan had already disproved it.** `docs/plans/2026-09-01-nt-0019-id-standard-
map-plan.md` (PR #557, merged `106e322`) carries, at its own evidence table (line 197):
`` `.claude/agents/` (README + 7 agents) | **8** | "two agents" named `` — the same finding as
the row above, reached independently. Two hundred lines later, its **W37-8** slice scope
(line 750) reads: *"the seven charters under `.claude/roles/`, `.claude/agents/README.md`
and **the two agent files §5.3 names**"* — scoping a slice against the exact undercount the
plan's own evidence table had already flagged, in the same merged document. Confirmed by
reading both lines directly, not relayed. The planner's own per-file citation count, run
independently and landing on the same figures this sweep found:

| Agent file | Citations the migration rewrites | Named in §5.3 |
|---|---|---|
| `performance-engineer.md` | 2 | no |
| `ci-watcher.md` | 1 | yes |
| `spec-reconciler.md` | 1 | yes |
| README + 4 others | 0 | README only |

**The generalisation, not just the count.** §5.3's agents row is a description of what
someone noticed while reading NT-0019, and W37-8's scope sentence consumed it as an
enumeration of everything that changes — the same shape already on record here against a
workstream row's NFR clause reading as an exhaustive list rather than an as-noticed sample.

**The exposure is narrower than the scope sentence alone suggests, and it is worth saying
plainly rather than leaving it to read as worse than it is.** NT-0019 §4 step 5 stamps a
header on "every file under... `.claude/agents/`" wholesale, not the two named; step 6
rewrites citations "across the whole tree — `git ls-files`, nothing exempt" (both confirmed
directly against the note's text, not the plan's paraphrase). So the migration script itself
catches `performance-engineer.md` regardless of what W37-8's scope sentence says. The
post-migration check that would catch a miss (check 30, requiring a header on every agent
file) does not exist in the current, pre-migration `scripts/audit-docs.py` — confirmed by its
absence there — so this piece rests on NT-0019's own design rather than on running code.
**The real residual risk is narrower and specific**: an executor reading W37-8's scope
sentence literally, treating "the two agent files" as the slice's hand-edit work list (the
per-role §1.6 content step 5/6 cannot supply mechanically), and being caught by the
post-migration check only after the fact rather than by the scope sentence itself.

**No edit to the frozen plan** — `docs/plans/README.md` is explicit that a filed plan is a
record of what was believed then, not edited to agree with the repository later, and the
planner's own report of this reached the same conclusion. The correction belongs in W37-8's
leaf plan, tracked on the lead's task board; this record is where it is discoverable from in
the meantime.

### 2.4 §5.4 — `.claude/skills/`

| Item | Command (pinned) | Measured | Claim | Agrees? |
|---|---|---|---|---|
| Total `SKILL.md` | `git ls-tree -r --name-only 89dd2b1 -- .claude/skills \| grep -c '/SKILL\.md$'` | 46 | 46 | Yes, exact |
| Named-changing skills | Manual enumeration of every skill name in §5.4's own table | 25 distinct skill names, + the table's own `README.md` row = 26 | "twenty-six skills" | Reconciles (26 = 25 named + the skills-index README row itself) |

### 2.5 §5.5 — `scripts/`

| Item | Command (pinned) | Measured | Claim | Agrees? |
|---|---|---|---|---|
| Total scripts | `git ls-tree -r --name-only 89dd2b1 -- scripts \| grep -cE '\.py$'` | 17 existing (16 top-level + 1 under `scripts/hooks/`) | "fourteen scripts" | **No — unreconciled.** §5.5's own table names 19 distinct identifiers (17 existing + 2 not-yet-created: `doc-id.py`, `doc-index.py`); a citation-bearing subset via `git grep -lE '<citation regex>' 89dd2b1 -- scripts` gives 16. None of raw-file-count (17), named-identifier-count (19), or citation-bearing-file-count (16) equals 14. Flagged as unreconciled rather than forced to fit; independently corroborated by the map plan's own sweep, which separately measured "16 + 1" (scripts + hooks) against the same "fourteen scripts changed" claim (§4). |

### 2.6 §5.6 — Code (the material findings)

Reproduced NT-0019 §10's own evidence command exactly rather than inventing a new regex:
`git grep -lE '\b(FR|NFR|OQ|DEP|VR)-[A-Z]+-[0-9]+\b' 89dd2b1 | sed 's/^[^:]*://' | awk -F/
'{print $1}' | sort | uniq -c`. This is the command that surfaced both findings below — a
per-directory split with the *identical* regex is what makes the two comparable.

| Item | Command (pinned) | Measured | Claim | Agrees? |
|---|---|---|---|---|
| **`backend` aggregate** | evidence command above, `backend` row | **210** | (sum of the two rows below, ≈410) | — |
| `backend/src/app/` | same regex, `-- backend/src/app` | 88 | ≈200 | **No — the headline finding.** |
| `backend/tests/` | same regex, `-- backend/tests` (96 total files exist here; 96 total `.py` files at `backend/src/app` too) | 93 | ≈210 | **No — the headline finding.** |
| `backend/migrations/` | same regex, `-- backend/migrations` (43 total `.py` files exist) | 28 | 3 | **No.** |
| `packages/pricing-core/` | same regex | 70 | ≈70 | Yes |
| `packages/pricing-core/` — the `ADR-1 (91)` detail | `git grep -oE '\bADR-1\b' 89dd2b1 -- packages/pricing-core` = 0; `git grep -oE 'ADR-0001' 89dd2b1 -- packages/pricing-core` = 49 | 49 (padded), 0 (bare) | "ADR-1 (91 occurrences)" | **No, two separate errors** (below) |
| `packages/model-schema/` | same regex | 57 | ≈58 | Yes, within rounding |
| `frontend/src/` | same regex, `-- frontend/src` | 142 | 144 (stated as exact, no `≈`) | **No — see below.** |
| `examples/`, `deploy/`, `packages/README.md` | same regex, three paths combined | 9 | 8 | Close, +1 unexplained (checked whether a `VR-` match, out of scope per D5, accounted for it — it does not; both candidate files also carry an independent, legitimate FR/NFR/OQ/DEP id) |

**The headline finding, stated with its arithmetic.** `88 + 93 + 28 = 209`, matching the
evidence command's own `backend` aggregate (210) almost exactly. The presentation table's two
largest rows — `backend/src/app/ ≈200` and `backend/tests/ ≈210` — each independently claim
roughly the *combined* backend total, summing to about double the real population. The most
plausible mechanical account: the evidence command's single `backend=210` bucket (grouped
only by top-level directory name) was read twice when the table split it into subdirectories,
rather than re-measured at that granularity. **The real combined population is ~209–210, not
~410**, and this is the single biggest number in §5.6 — material to slice sizing.

**`backend/migrations/` — undercounted by roughly 9x, not noise.** The 28 matches are real:
inspected the actual citation tokens (`git grep -o -E '<regex>' 89dd2b1 --
backend/migrations/versions`), finding genuine, repeated requirement citations in migration
docstrings/comments — 9× `FR-DATA-42`, 6× `FR-GOV-22`, 5× `FR-MODEL-45`, and eighteen more
distinct ids at lower counts. "3" may describe something narrower than this filing can
confirm from the table text alone (e.g. top-of-file docstring only, versus anywhere in the
file) — but read as "files containing a citation," it is not 3.

**The `ADR-1 (91)` row — two independent errors, not one.** (1) Pricing-core's code currently
cites the *padded* form `ADR-0001` (49 occurrences), not the bare post-migration form `ADR-1`
(0 occurrences) — the table describes tomorrow's citation convention (D6: "citations
unpadded") as if it were today's. (2) The figure "91" is not pricing-core's own count (49); it
is NT-0019 §10's own evidence command's total for `ADR-0001` across **backend + packages +
frontend combined** (`git grep -ohE 'ADR-0[0-9]{3}' 89dd2b1 -- backend packages frontend`,
reproduced exactly: 91), misattributed in the presentation table to pricing-core alone.

**`frontend/src/` — a smaller instance of the same aggregate-vs-subdirectory conflation.**
The same evidence-command breakdown gives a `frontend` (whole top-level directory) bucket of
**144**, matching the claim exactly — but `frontend/src/` specifically, measured with the
identical regex, is **142**. Two files outside `frontend/src/` (elsewhere under `frontend/`)
account for the difference. The claim is presented as an exact count for `frontend/src/`
specifically; it is actually the whole-directory total.

### 2.7 §5.7 — Tests

All twelve named test files confirmed to exist by name, **at path `tests/` (repository
root)** — not `backend/tests/`, which is a separate directory holding the backend's own
application test suite (§2.6). Two ("`test_audit_docs_notes_tombstone.py`",
"`test_notes_move_citations.py`") are the "deleted →" pair; the other ten are the
to-be-updated set. All twelve sum exactly to the claimed "twelve tests" — the four "new"
files (`test_doc_id.py`, `test_doc_index.py`, `test_audit_docs_ids.py`,
`test_audit_docs_redirects.py`) were confirmed **not yet to exist**, correctly, since "Lands
in" counts existing artifacts affected, not deliverables still to be created.

| Item | Command (pinned) | Measured | Claim | Agrees? |
|---|---|---|---|---|
| Existing test files named in §5.7 | `git ls-tree -r --name-only 89dd2b1` filtered to the twelve named stems | 12 of 12 found, all under `tests/` | "twelve tests" | Yes, exact |

### 2.8 §5.8 — CI

| Item | Command (pinned) | Measured | Claim | Agrees? |
|---|---|---|---|---|
| CI workflow files | `git ls-tree -r --name-only 89dd2b1 -- .github/workflows` | 3 total (`docs.yml`, `frontend.yml`, `python.yml`), matching §5.8's own table by name; only `docs.yml` carries a real Kind = H change, the other two are explicitly marked "—" (unchanged) in that same table | "two CI workflows" | **No — unreconciled.** Doesn't cleanly match "1 actually changes" or "3 are named." Minor; flagged rather than fitted. |

### 2.9 Repo-wide cross-checks (NT-0019 §10's own commands, re-run at the pin)

| Item | Command (pinned, note's own form) | Measured at `89dd2b1` | Note's figure (at `8f5d57d`) | Agrees? |
|---|---|---|---|---|
| Distinct requirement-family ids | `git grep -ohE '\b(FR\|NFR\|OQ\|DEP\|VR)-[A-Z]+-[0-9]+\b' 89dd2b1 \| sort -u \| wc -l` | 710 | 710 | Yes, exact |
| Files matching that pattern, repo-wide | same, `-l \| wc -l` | 770 | 767 ("Lands in" row) | Close (+3, 6-commit-gap drift). **Methodology caveat, separate from the drift**: this pattern includes `VR-` product identifiers, which §5.6's own "Never touched" row places permanently out of scope (D5). The 767/770 figure is not a clean "files the migration touches" count — see §5 below for the corrected, predicate-carrying figure now on the roadmap. |
| `pytest.mark.req` markers | `git grep -c 'pytest.mark.req' 89dd2b1 -- backend packages \| awk -F: '{s+=$NF}'` (note's own command; `$NF` used instead of `$2` because a revision prefix shifts the field) | 1988 | 1988 | **Yes, exact** |
| Work-key citations (occurrences) | `git grep -ohE '\bW[0-9]+[a-z]?(-[0-9]+)*\b' 89dd2b1 \| wc -l` | 5595 | 5579 | Close (+16, drift) |
| Work-key citations (files) | same, `-l \| wc -l` | 415 | 413 | Close (+2, drift) |
| Highest ruling number | `git grep -hoE '^#+ Ruling [0-9]+' 89dd2b1 -- docs/plans \| grep -oE '[0-9]+' \| sort -n \| tail -1` | 65 | 65 | Yes, exact |

## 3. Overall read

The small, enumerable classes — specs, workflows, ADRs, research, findings, audit-work
READMEs, role charters, total `SKILL.md`, tests, and three of the four repo-wide cross-checks
— are accurate to exact or near-exact, with two small, fully-explained drifts (`docs/notes`
18→19, `docs/plans` 125→126) attributable to ordinary repository activity between the note's
own evidence point (`8f5d57d`) and this pin (`89dd2b1`). The two material defects are both in
§5.6: **`backend/src/app` and `backend/tests` each independently claim roughly the combined
backend total** (~410 claimed against ~209–210 measured), and **`backend/migrations` is
undercounted by roughly 9x** (3 claimed against 28 measured, with the citations verified by
hand, not assumed noise). Both are corrections to the note's own evidence — sizing errors a
slice would otherwise inherit — not objections to the migration itself.

## 4. Cross-validation against the map plan's independent sweep

`docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md` (PR #557, merged `106e322`) ran its
own verification of NT-0019's §5.1–§5.5, §5.7 and §5.8 populations, independently of this
sweep and before it was known to have landed. Every item that overlaps agrees, once framing
differences are accounted for:

- `docs/plans/*.md`: the map plan's **107** (suffix-less "plan" kind only) + its own
  **16** (`-ledger.md`) + 3 (review/handover, per its total row) = **126**, exactly this
  sweep's `docs/plans/2026-*.md` figure (§2.2) — different granularity, same population.
- `docs/notes/`: the map plan's **20** = "18 notes + NT-0019 + README"; this sweep's
  **19** excluded the README by pattern (`^docs/notes/[0-9]`) — `19 + 1 = 20`, consistent.
- `docs/adr/`, `docs/workflows/`: the map plan's 7 (6+README) and 6 (5+README) match this
  sweep's 6 and 5 once each README is added back.
- `docs/research/`, `docs/specs/`, `.claude/skills/*/SKILL.md`, `.claude/roles/`: identical
  figures both ways (11, 8, 46, 7).
- **`.claude/agents/`: the map plan independently counted 8 total (README + 7 agents)**,
  agreeing with this sweep's raw population (§2.3), and — reported by the planner after this
  finding landed — its own per-file citation count matches this sweep's exactly
  (`performance-engineer.md` 2, `ci-watcher.md` 1, `spec-reconciler.md` 1, the rest 0). See
  the §2.3 addendum for the further finding this enabled: the map plan's own W37-8 scope
  sentence still names only the two, two hundred lines after its evidence table disproved
  that count.
- **`scripts/`: the map plan independently measured "16 + 1" (scripts + `hooks/`)** against
  the same "fourteen scripts changed" claim — agreeing with this sweep's 17 and leaving the
  same gap unreconciled, from a different measurement.
- **Check 19's two hard-coded sites**: the map plan separately verified this session's Task-1
  finding (`ADR-(\d{4})` at lines 471 and 1117) by the same method, reaching the identical
  count independently.

No overlap between the two sweeps disagrees. This sweep's unique contribution is §5.6 (which
the map plan explicitly declined to duplicate, assigning it here by name) and the smaller
§5.1–§5.4 items the map plan's table did not carry to this level of detail (the agents'
specific citation-bearing subset; the `ADR-1`/91 and `frontend/src` mislabelings).

## 5. Downstream corrections already landed from this sweep

- **`docs/roadmap.md` W37 row** (PR #559, open at filing time) now carries the corrected,
  predicate-qualified population — "771 with `VR-`, 768 without, 3 files matching only via a
  `VR-` id" at `bc7bc36` — replacing a bare figure that did not name its predicate.
  Independently re-verified by this filing at `bc7bc36`: `git grep -lE
  '\b(FR|NFR|OQ|DEP|VR)-[A-Z]+-[0-9]+\b' bc7bc36 | wc -l` = **771**; the same pattern without
  `VR` = **768**. Both confirmed exact.
- **F68** — `audit-docs.py` check 28 has no plan-kind exclusion for a ruling record, shielded
  only by the 2026-08-31 cutoff — filed and merged, `docs/audit/register.md`,
  `docs/audit/findings/F68.md` (PR #558, `d4e094b`).
- **F69** — `write_runtime_state.py cycle` cannot clear a position field; empirically
  reproduced against the shipped script — filed and merged, `docs/audit/findings/F69.md`
  (same PR).

Both findings carry a proposed disposition only; the verdicts were the lead's, adopted as
filed.

## 6. Left unreconciled, deliberately

Per this role's standing practice, an honest unreconciled row is filed as such rather than
fitted to a plausible-sounding subset:

- **"Fourteen scripts."** No reading tried — raw `.py` count (17), named-identifier count in
  §5.5's table (19, including 2 not-yet-created), or citation-bearing-file count (16) —
  equals 14. Independently corroborated as unreconciled by the map plan's own separate
  measurement (§4).
- **"Two CI workflows."** Three workflow files exist and are all named in §5.8's own table;
  only one (`docs.yml`) carries an actual Kind = H change. Neither "1" nor "3" is what the
  summary line says, and no other reading of "two" was found to fit.

## 7. Not verified

- `docs/plans/2026-09-01-maintainer-delegation-and-nt-0019-precedence.md` did not exist in
  this sweep's pinned tree; it now exists on `main` at `bc7bc36` (confirmed) but its content
  is not independently checked by this filing — F68 does not depend on it.
