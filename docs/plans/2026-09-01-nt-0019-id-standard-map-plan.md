# W37 — One id per governed thing: Map Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt NT-0019's document-id standard across the repository — one global integer
sequence, one status vocabulary, a self-describing directory layout, a machine-readable
header, roles per family, and the generated index and lint that hold all of it — in eleven
slices, of which exactly one moves a file.

**Architecture:** A map plan, per [`../process/delivery-process.md`](../process/delivery-process.md)
§3 — it cuts the Work into slices and states each slice's scope, dependencies, executor skill
and acceptance; the task-by-task detail for each slice is a child leaf plan written when that
slice is dispatched, the same relationship `2026-08-31-w12-map-plan.md` has to its own child
plans. The cut follows NT-0019's four stages S1–S4 and says at every point where it departs
from them, and why.

The shape of the work is unusual and drives the cut: **ten of the eleven slices change no
governed document at all.** Nine build or edit *instruments* — two new scripts, ten new audit
checks, seven creating skills, seven charters, the root governance files — and one, W37-6,
is a single supervised run of a deterministic script that renames, splits, stamps and
renumbers the whole corpus at once. That asymmetry is why the parallelism is where it is:
S1's slices fan out, S2's run does not.

**Tech Stack:** Python 3.12 **standard library only** for `scripts/doc-id.py`,
`scripts/doc-index.py` and the `scripts/audit-docs.py` additions — see Global Constraints
G4, which is a verified constraint rather than a preference. `pytest` for their tests. Git
plumbing (`git ls-files`, `git log --diff-filter=A`, `git mv`) for the migration's
provenance and moves. GitHub Actions for the two new gate steps. No new dependency is added
to any `pyproject.toml` by any slice in this plan.

**Spec:** [`../notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md) —
the note is the specification this plan implements, and it is `accepted`, so its §1 standard,
its §2 decisions D0–D14, its §4 migration procedure, its §5 impact map, its §7 acceptance
items (a)–(k) and its §8 sequencing are **fixed inputs planned against, not choices reopened
here**. Executors read both this plan and the note; where they disagree, the note wins and
the disagreement is a finding against this plan.

**Filed:** 2026-09-01 (UTC), against `origin/main` at `89dd2b1`, by the planner. Frozen at this
date — a filed plan is a record, not an instruction ([`README.md`](README.md) in this
directory). A replan is a new dated file that supersedes this one, never an edit to it.

## Acceptance Standard

The Work is complete when every item below passes. Each is a command a fresh reviewer can
run, or a named artifact they can read; none is satisfied by inspection of this plan.

1. `python3 scripts/doc-id.py check` exits 0 against `origin/main`: zero duplicate numbers,
   the sequence contiguous over merged records, and every file's header `id` equal to the
   integer its filename pads. (NT-0019 §7 (b).)
2. `python3 scripts/doc-index.py --check` exits 0 and `git status --porcelain docs/INDEX.md`
   is empty after a fresh `python3 scripts/doc-index.py` run — the index is byte-stable
   against regeneration. (§7 (c).)
3. Every tracked file under `docs/` parses to exactly one family, with zero classified
   "none": `python3 scripts/doc-id.py check --classify` prints a per-family count table whose
   total equals `git ls-files docs/ | wc -l` and whose "none" row is 0. (§7 (a).)
4. The legacy-form sweep of §7 (d) returns nothing over `git ls-files`, under the exclusion
   set fixed in Decision point DP-2 and recorded in `scripts/doc-id.py`'s
   `LEGACY_SWEEP_EXCLUSIONS` constant with a one-line reason per entry.
5. No padded id appears in prose: `python3 scripts/audit-docs.py` check 32 exits 0, and its
   deliberately-broken fixture (a padded id outside a link target) makes it exit 1. (§7 (e).)
6. `git grep -c 'VR-DST-1' | ...` totals the same number at the post-migration tree as at
   `89dd2b1` — no product identifier moved. The number is recorded in W37-6's leaf plan
   before the run and re-derived after it. (§7 (f), D5.)
7. `python3 scripts/audit-docs.py`, `uv run python scripts/req-coverage.py`,
   `uv run ruff check .`, `uv run mypy`, `uv run lint-imports`, `uv run pytest -q`,
   `uv run python scripts/generate-contracts.py --check`, and the frontend half
   (`pnpm --dir frontend lint`, `type-check`, `test`, `build`) all exit 0 at the tree after
   each slice in this plan. (§7 (h); `CLAUDE.md` §11's two-halves rule.)
8. Every **H** row in NT-0019 §5 is named by a merged commit, listed in a table in this
   Work's closure record with the row, the commit and the slice. (§7 (i).)
9. One new item per document family has been created through its own creating skill, with a
   number from `python3 scripts/doc-id.py next`, under the discharge route fixed in Decision
   point DP-4. (§7 (j).)
10. `python3 scripts/doc-index.py --phase P1b` prints a report containing every element
    NT-0019 §1.10 (c) names: Works closed and retired, slices planned versus delivered, plans
    superseded per Work, rulings per Work, findings opened versus discharged with the
    unowned-decay count, documents with no inbound citation outside `INDEX.md`, and days from
    a plan reaching `active` to its closure record being filed. (§7 (k).)
11. Each of checks 30–39 has been shown to exit 1 on a deliberately broken fixture under
    `tests/fixtures/docs-ids/`, one fixture per check, and the ten proofs are listed in the
    closure record with the fixture path and the failure message. (`CLAUDE.md` §13: a check
    that has never printed a failure has not been tested.)
12. `docs/roadmap.md` carries a W37 row recording the close, and the maintainer has accepted
    the Work close with a dated line. (`CLAUDE.md` §12.)
13. The migration script's own diff — a `migrate` run on a clean tree, before the hand-edited
    rows of §8 are applied — filtered to hunks that are neither a front-matter block nor a
    token substitution drawn from the generated `REDIRECTS.csv`, is empty. Proven on the
    fixture corpus in W37-5 before the real run, and re-proven at W37-6's merge tree. (§7 (g),
    in the executable form DP-3 fixes; it is a property of the *script*, which is why it is
    provable before anything moves.)

## Global Constraints

Every task's requirements implicitly include this section. Values are copied verbatim from
the source named beside each.

- **G1 — NT-0019 outranks current practice.** Maintainer ruling, 2026-09-01: *"NT-0019 is
  intended to overwrite current project rules; give it priority where it is against current
  practice."* Where the standard collides with something already written down, the collision
  is **work in NT-0019's favour**, not a blocker and not a reason to narrow a slice. Two
  limits the ruling does not lift: no rule is changed **silently** — every collision lands as
  a visible, dated edit naming which rule yielded to what (`CLAUDE.md` §0) — and the ruling
  does not authorise starting; sequencing is unchanged.
- **G2 — the permanence rule yields, at two sites.** `CLAUDE.md` states *"Requirement IDs and
  section numbers are permanent ... Never renumber"* at **line 27** (the §0 bullet) and again
  at **line 107** (§5's own sentence). D2 renumbers every requirement id. Both sites are
  edited in W37-9, each with a dated line naming NT-0019 as what it yielded to. An executor
  who edits one and not the other leaves the contract self-contradicting.
- **G3 — D0–D14 and §7 (a)–(k) are fixed inputs.** No slice reopens a decision or weakens an
  acceptance item. Where an acceptance item is not executable as written, the plan supplies
  the **executable form** and names it as such (DP-2, DP-3); it never lowers the bar.
- **G4 — the three gate scripts are standard-library only.** `.github/workflows/docs.yml`
  line 38 runs `python3 scripts/audit-docs.py` after `actions/setup-python` v5 with
  `python-version: "3.12"` and **no dependency-install step**; `scripts/audit-docs.py` imports
  only `collections`, `hashlib`, `importlib.util`, `json`, `pathlib`, `re`, `sys`, `types`,
  `datetime.date` and `typing.Final`; `grep -ln 'import yaml' scripts/*.py` returns nothing.
  So `doc-id.py`, `doc-index.py` and the check additions **may not import PyYAML or any other
  third-party package.** The header is YAML *front matter* in form; its parser is hand-rolled
  against the closed field set of NT-0019 §1.5. This is a verified fact about the repository,
  not a style choice — see DP-5.
- **G5 — money and product identifiers are never touched.** D5: an id stored, transmitted or
  asserted by an API contract — `VR-*`, artifact ids, job kinds — is product data governed by
  `docs/specs/`, and no slice rewrites one. The rewrite list in `doc-id.py` is an
  **allow-list** of prefixes; `VR` is not on it.
- **G6 — one commit per spanning change.** `CLAUDE.md` §2: a change spanning spec and code
  lands as one commit — spec, code, tests, any skill update — *"or the audit reports a
  consistency the repository does not have."*
- **G7 — the gate has two halves.** `CLAUDE.md` §11: a Python-only run is not the gate. Both
  halves pass locally before any push.
- **G8 — no `claude.ai` session link reaches GitHub.** `../process/delivery-process.md` §15,
  reaffirmed by the maintainer 2026-09-01. Commit trailer is `Co-Authored-By:` only; the
  product attribution footer stays.
- **G9 — every plan-kind file filed from 2026-08-31 states an acceptance standard.**
  `scripts/audit-docs.py` check 28, cutoff constant `PLAN_ACCEPTANCE_STANDARD_CUTOFF =
  date(2026, 8, 31)`, heading regex `^#{1,6}\s+.*acceptance standard` case-insensitive, with
  at least one non-blank line before the next heading of any level. Every child leaf plan
  under this map plan is in scope.
- **G10 — the local working tree is outside the standard.** Maintainer clarification,
  2026-09-01: *"handover is pure local files and not covered by NT0019, NT0019 focuses on the
  project only."* `~/gi-pricing-plan.local/` in full — `handover/`, `inbox/`, `drafts/`,
  `scratch/`, the state files, the logs, the runtime state — gets no header, no id, no family
  and no `INDEX.md` row. **This is consistent with the note, not an amendment to it**: §1.12
  already says *"Scratch (`.planning/`, `.superpowers/`, runtime state, chat) is never a
  family; if it carries a decision, the decision is an `RL-`"*, and every path in §5's impact
  map is a repository path. Where it bites: §1.2's `PL- kind: handover` and §5.2's
  *"handover → `PL- kind: handover`"* name the **one** `-handover.md` file inside
  `docs/plans/` at `89dd2b1`, not the local directory this team works from. **No slice
  migrates, stamps, renames or lints anything outside the repository, and no population count
  in this plan includes such a file.** The constraint is also enforced by the tool rather than
  only by instruction: §4 step 6 operates over `git ls-files`, which cannot reach outside the
  repository. What the clarification leaves standing is a rule about *where decisions go*, not
  a migration task: **a decision that lives only in a local handover is not governed and
  therefore does not survive** — if a local file carries a decision, the decision becomes a
  repository record.

## Evidence — what was verified, where, and what was not

**Pinned tree: `origin/main` at `89dd2b1`**, working tree clean, verified by
`git fetch --prune origin && git log --oneline origin/main -1` and `git status --porcelain`
returning nothing before this plan was drafted. Every count below was measured at that tree
by the command shown; nothing is recalled.

**NT-0019 was written against `8f5d57d`, seven commits earlier.** Its §5 impact map and §10
evidence therefore describe a tree that no longer exists. The drift is small and measured:
`git diff --name-status 8f5d57d..89dd2b1 -- docs/` returns nine paths — two additions
(`docs/notes/0019-one-id-per-document.md`, `docs/plans/2026-09-01-nt-0016-landing-package.md`)
and seven modifications. **No file was deleted or renamed**, so every §5 row still names a
file that exists; the counts move by small integers and the *classes* are unchanged.

| §10 measure | Note, at `8f5d57d` | Re-derived at `89dd2b1` | Command |
|---|---|---|---|
| Markdown documents under `docs/` | ≈ 230 | **222** | `find docs -name '*.md' \| wc -l` |
| Distinct requirement-family ids | 710 | **710** | `git grep -ohE '\b(FR\|NFR\|OQ\|DEP\|VR)-[A-Z]+-[0-9]+\b' \| sort -u \| wc -l` |
| Files citing a requirement-family id | 767 | **770** | `git grep -lE '\b(FR\|NFR\|OQ\|DEP\|VR)-[A-Z]+-[0-9]+\b' \| wc -l` |
| `pytest.mark.req` markers | 1988 | **1988** | `git grep -c 'pytest.mark.req' -- backend packages \| awk -F: '{s+=$2} END {print s}'` |
| Work-key citations | 5579 | **5595** | `git grep -ohE '\bW[0-9]+[a-z]?(-[0-9]+)*\b' \| wc -l` |
| Files carrying a work key | 413 | **415** | `git grep -lE '\bW[0-9]+[a-z]?(-[0-9]+)*\b' \| wc -l` |
| Highest legacy ruling number | 65 | **65** | `git grep -hoE '^#+ Ruling [0-9]+' docs/plans \| grep -oE '[0-9]+' \| sort -n \| tail -1` |
| Tracked files, whole repository | — | **1355** | `git ls-files \| wc -l` |

Directory populations, measured the same way and used for slice sizing:

| Population | Count at `89dd2b1` | Note's figure |
|---|---|---|
| `docs/plans/*.md`, plan kind (suffix-less, non-README) | **107** | "125" for the whole directory |
| `docs/plans/*-ledger.md` | **16** | 16 |
| `docs/plans/` total, incl. README and three review/handover files | **127** | — |
| `docs/notes/` (18 notes + NT-0019 + README) | **20** | "(18) + README" |
| `.claude/notes/` redirect stubs + README | **19** | "(19 stubs) + README" — **the note over-counts by one**; check 30 requires the README plus exactly 18 stubs |
| `docs/audit/` files | **36** | — |
| `docs/research/` | **11** | 11 |
| `docs/adr/` (6 ADRs + README) | **7** | "(6) + README" |
| `docs/workflows/` (5 journeys + README) | **6** | "(5) + README" |
| `docs/specs/` | **8** | 8 |
| `.claude/skills/*/SKILL.md` | **46** | 46 |
| `.claude/roles/` | **7** | seven charters |
| `.claude/agents/` (README + 7 agents) | **8** | "two agents" named |
| `scripts/*.py` + `scripts/hooks/` | **16 + 1** | fourteen scripts changed |

**What this plan did not verify, and who owns it.** NT-0019 §5's per-row file lists and its
five `≈`-prefixed per-area code counts (§5.6: ≈200 backend/src, ≈210 backend/tests, ≈70
`pricing-core`, ≈58 `model-schema`, 144 frontend, 8 examples/deploy) are **the auditor's
full-class sweep against `89dd2b1`, running in parallel with this plan and not duplicated
here.** W37-6's leaf plan must be written against that sweep's result, not against this
table: the table above sizes the slices, the sweep enumerates the rows. **W37-6 must not be
dispatched until the sweep has landed and its per-row result is attached to W37-6's leaf
plan.** That is a hard precondition, listed again under W37-6.

**Two claims relayed to this plan were checked and one was corrected.**

- Relayed: *"check 19's `ADR-(\d{4})` is the one already known to bite."* Verified partly
  right and incomplete: `grep -n 'ADR-' scripts/audit-docs.py` returns **two** sites —
  line 471, inside the working-notes reference check, and line 1117, in the corpus-wide ADR
  existence check. Both hard-code `ADR-(\d{4})` and both must move to the integer form. An
  executor told about one would leave the other.
- Relayed: *"the `accepted` verdict supplies the acceptance line"* — recorded and derived
  under **Authority** below, not treated as a premise.

## The gap condition — verified, and it holds

NT-0019's Sequencing row requires the migration to land *"now, at the next gap with no open
branches (F40's lesson)."* Verified at `89dd2b1`, 2026-09-01:

- `gh pr list --state open` returns nothing. **Zero open pull requests.**
- `git branch -r` lists exactly one remote branch, `origin/main`. **No branch is in flight.**
- Three local branches survive in the shared checkout — `nt0016-landing-apply`,
  `nt0016-package-superseded-note`, `nt0016-review11-f31-attribution`. Their commit subjects
  match merged PRs #553, #554 and #551, and `git diff origin/main <branch>` is
  deletion-dominated for each: they are **behind** `main`, carrying no content `main` lacks
  beyond pre-#553 revisions of two files. They are leftovers, not open work.

**So the condition holds today.** It is a condition on W37-6 alone, and it is **volatile** —
it can be false an hour from now. W37-6's leaf plan re-derives all three checks in the same
session it runs the migration, and aborts if any has changed. The other ten slices do not
depend on it.

## Authority — what this Work rests on, and who read what

Recorded here rather than left implicit, because a decision travels and its rationale does
not; an implementer who has to reinvent the reason usually reinvents the one that was
rejected.

**The obligation.** [`../notes/README.md`](../notes/README.md) line 136-144's verdict table:
a note with status `accepted` obliges *"Named in a roadmap row before work starts."* NT-0019
is `accepted` (its own header, and its index row at `../notes/README.md` line 56). No roadmap
row names it: `git grep -n -E 'NT-0019|document-ids|doc-id|doc-index' -- docs/roadmap.md
docs/process/ CLAUDE.md` returns nothing at `89dd2b1`. **So the row must exist before W37-1
starts**, and this plan proposes it below rather than writing it — `docs/roadmap.md` is the
lead's file, and a roadmap edit surfaced in a planner's work is a recommendation
(`.claude/roles/planner.md`).

**The acceptance line.** W33, W34 and W36 each rest on *"the reconciliation's dated acceptance
line"* — `docs/roadmap.md` lines 378, 379, 381. NT-0019 has no reconciliation, so the phrase
has no referent here. The question *"does the W37 row need a fresh dated maintainer acceptance
line, or does the note's own `accepted` status supply it?"* was put to the maintainer and
**ruled on 2026-09-01: land the row; the `accepted` verdict supplies it.** The derivation
that makes that coherent, and which a later reader would otherwise have to reconstruct:

1. The verdict table's obligation for `accepted` is *"named in a roadmap row"* — the row is
   the **consequence** of acceptance, not a second acceptance. Requiring a fresh line to
   write the row would make the obligation unsatisfiable without a second maintainer act the
   table does not ask for.
2. The `accepted` status is itself dated and the maintainer's: NT-0019's Status row reads
   *"`accepted` — every decision in §2 is the maintainer's; nothing is left for a ruling
   sitting"*, and its index row carries **2026-09-01**. That is a dated maintainer acceptance
   of the whole note, which is strictly more than a reconciliation line accepts.
3. The reconciliation line exists in W33/W34/W36 because those three notes were **`open`**
   when the reconciliation ran; the line is what moved them to accepted. NT-0019 arrived
   accepted. The instrument differs because the situation differs, not because the standard
   is lower.
4. **W35 is the counter-example that proves the pattern rather than breaking it**: its row
   cites Rulings 55-65 and the note's own §11, and carries **no** "reconciliation's dated
   acceptance line" phrase at all. The register already admits more than one authority form.

**What is still the maintainer's, and is not supplied by any of the above:** the acceptance
of this **Work's close** (`CLAUDE.md` §12), and the dated line on each `CLAUDE.md` and charter
edit in W37-8 and W37-9. Neither is delegated by the note's status.

## Decision points

Kind, blocking status and resolver per NT-0019 §1.7. A blocking row must carry a resolver id
before the slice it blocks may start; a non-blocking row names the step that resolves it and
the default applied until then.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | §8 puts the **creating skills** in S3, after the migration. Any governed document created between W37-6 and W37-7 is filed under the old naming and immediately fails checks 30-32. Where do the seven creating skills land? | (a) fold `writing-plans`, `subagent-driven-development`, `adr-write`, `spec-change`, `close-workstream`, `phase-review`, `library-spike` into W37-6's commit; (b) freeze all document creation between W37-6 and W37-7; (c) accept the window | **(a)** — the migration already lands at a gap, so the marginal cost is one more file class in an already-atomic commit, and (b) is an unbounded freeze on a team whose every artifact is a document | scope — it moves work between NT-0019's own stages | **yes**, W37-6 | maintainer |
| DP-2 | §7 (d)'s legacy-form sweep must return nothing, but `doc-id.py`'s own pattern table, its fixtures, `REDIRECTS.csv` and every frozen record quoting a legacy id **as data** are structural hits. The item as written is unpassable | (a) extend (d)'s stated exclusions from two to a named constant list with a reason per entry; (b) construct every pattern so it cannot self-match; (c) narrow (d) to `docs/` | **(a)** — (b) is unmaintainable obfuscation and (c) drops the code tree, which is where 767 of the citations live. (a) preserves the item's strength: the exclusion set is small, named, reasoned and itself reviewable | scope — it refines an accepted acceptance item | **yes**, W37-6 | maintainer |
| DP-3 | §7 (g) requires *"the migration diff filtered to hunks that are neither header nor citation-token"* to be empty, while §8 requires ten hand-edited script and roadmap changes in the **same commit**. Both cannot hold of one diff | (a) (g) is scoped to the script's own output — computed by running `migrate` on a clean tree and diffing that alone, with the H rows applied afterwards in the same commit; (b) (g) gains a path exclusion for the H files; (c) split the commit | **(a)** — it is what makes (g) a real test of the *script*, which is the thing (g) exists to constrain; (c) is refused by §8's "same commit" | decision point — mechanism, not scope | **yes**, W37-6 | decision-maker, one ruling |
| DP-4 | §7 (j) — "one new item per family born through its skill" — cannot be satisfied by fabricating a ruling or a finding that no work produced | (a) discharge (j) against the two downstream Works named in §8 (the charter investigation and the create-read-retire audit), as a standing condition on their first slices; (b) create one specimen per family now; (c) discharge the families that have real work and record the rest as owed | **(a)** — it tests the instruments on real work, which is the only thing (j) can usefully mean; (b) files thirteen artifacts nobody needed and NT-0019 §1.13 explicitly maps scratch out of the families | scope | no — W37-11 applies (a) as the default and records the residue | maintainer, at W37-11 |
| DP-5 | The header parser cannot use PyYAML (G4). Hand-rolled stdlib parser, or move the gate scripts to `uv run` with a dependency? | (a) hand-rolled parser over NT-0019 §1.5's closed field set; (b) move `docs.yml` to `uv run` and add PyYAML | **(a)** — the field set is closed and flat (scalars plus simple lists), (b) adds a dependency install to the one workflow that currently needs none, and G4 is a repository fact rather than a preference | fact — it is settled by what the workflow file does | no — W37-2 step 1 implements (a); if it proves infeasible the finding reopens this row | executor, W37-2 |
| DP-6 | `CLAUDE.md` §5 and the seven charters must change. §12 reserves *"an amendment to what this file requires"* to the maintainer, while noting that editing it to **point at** something already ruled is not an amendment | (a) executor drafts the diff, the slice's acceptance requires a dated maintainer line on the PR; (b) the maintainer writes the edits; (c) treat all of it as pointer-only | **(a)** — G2's renumbering yield is a real amendment, not a pointer edit, so (c) is false; (b) serialises the whole conventions block behind one person | scope | **yes**, W37-9 | maintainer |
| DP-7 | Check 34 (freeze) forbids any diff to a frozen file beyond `status:`, `superseded_by:`, `corrected_by:` and a ledger's `plans:`. The migration **moves, stamps and rewrites tokens in** every frozen plan, ruling and ADR, and D14 turns enforcement red *from* that PR. §4's closing line asserts the escape in prose — *"rewrites change reference tokens only"* — but a check does not read prose | (a) give check 34 a fourth allowance, mechanically defined: a diff is permitted when applying `REDIRECTS.csv`'s inverse mapping to the new bytes, and removing the front-matter block, reproduces the merge-base bytes exactly; (b) exempt the migration commit by construction, enforcing from the commit after; (c) amend the freeze rule | **(a)**, and see the disposition below — it turns §4's own sentence into code, keeps D14 intact, and is provable on broken input | decision point — mechanism | resolved in this plan; see below | planner, recorded here |
| DP-8 | Check 31 requires numbers *"unique and contiguous"*. Contiguity is much stronger than uniqueness, and an abandoned draft looks like it burns a number | (a) define the sequence over **merged** records only and never delete a merged record; (b) weaken contiguity to monotonicity | **(a)**, and see the disposition below — it is what the note already says, made explicit | decision point — mechanism | resolved in this plan; see below | planner, recorded here |

### DP-7, disposed of here rather than escalated

The collision is real and broader than citations: §4 step 5 **stamps** a header onto every
file, which check 34 forbids on a frozen file just as much as a token rewrite does. So the
migration commit touches every frozen record in three ways check 34 rejects — a move, a
stamp, and a token substitution — at exactly the commit D14 makes the check binding.

It is nonetheless a mechanism question, not a decision the note left open: §4's closing
sentence already states the intent (*"Never changed: a body line of any frozen file. Splits
preserve every line, stamps add lines, rewrites change reference tokens only"*). What is
missing is a machine-checkable definition of "reference tokens only", and supplying that is
what a plan is for.

**Disposition.** Check 34 gains a fourth allowance, implemented and documented in
`scripts/audit-docs.py` rather than written into `docs/process/document-ids.md` — because the
note's Deliverable row requires §1 to lift **verbatim**, and adding a clause to §1.11's check
table would break that. The allowance:

> A diff to a frozen file is permitted when the new bytes, after removing the leading
> front-matter block and applying the inverse of every `REDIRECTS.csv` mapping, are
> byte-identical to the merge-base bytes.

This is stronger than the prose, not weaker: it fails on a single changed word anywhere in a
body line, which is precisely what C4 exists to protect. It is proved on broken input in
W37-4's fixture set — mutate one word of a frozen fixture's body and check 34 must exit 1
while the same fixture with only token substitutions exits 0.

**Named for the maintainer, not acted on:** if the maintainer would rather this allowance live
in §1.11's own text, that is a one-line amendment to the note and to `document-ids.md`, and
this plan's implementation is unaffected either way.

### DP-8, disposed of here rather than escalated

The premise that an abandoned draft burns its number **does not survive reading §1.7's
allocator.** `doc-id.py next` *"fetches `origin/main`, reads the maximum across every header,
every spec bold-id, every roadmap row and `INDEX.md`, prints max + 1."* Three cases:

- **Abandoned before merge.** The number was never on `origin/main`, so `next` hands it out
  again. **No hole.**
- **Merged, then retired.** `retired` is a terminal *status*, not a deletion. Nothing in
  §1.2's mutability column permits removing a merged record; §1.6 says an `FD-` is *"never
  removed"*, and a retired skill keeps its id through a `REDIRECTS.csv` row. The file, its
  header and its `INDEX.md` row survive. **No hole.**
- **Rebase collision.** §1.7 already answers it: *"a collision at rebase is fixed by
  renumbering the unmerged item"* — the merged one keeps the number, the unmerged one moves
  up. **No hole.**

**Disposition.** Contiguity holds, and the rule that makes it hold is written into check 31's
docstring and `doc-id.py check`'s error message so an executor cannot implement it against
branch state by mistake: **the sequence is defined over records reachable from `origin/main`,
and a merged record is never deleted — only `retired`.** Check 31 computes contiguity over
`INDEX.md`, never over the working tree or a branch. A fixture proving the branch-state
reading wrong (a local file with a number above the merged maximum) must **not** fail
check 31.

## Sequencing and parallelism

Four stages, eleven slices. The stage column maps each slice back to NT-0019 §8; the two
departures from §8's own allocation are marked and argued.

| Slice | §8 stage | Title | Executor skill | Depends on | May run beside |
|---|---|---|---|---|---|
| W37-1 | S1 | The standard and the templates | `spec-change` | — | W37-2, W37-3 |
| W37-2 | S1 | `doc-id.py` — `next`, `check`, `widen`, and the shared header parser | `python-package` + `python-test` | — | W37-1, W37-3 |
| W37-3 | S1 | `doc-index.py` — the index, the execution column, the ownership matrix, the phase report | `python-package` + `python-test` | W37-2 (interface only; may not merge first) | W37-1, W37-2 |
| W37-4 | S1 | `audit-docs.py` checks 30-39, path-scoped, with ten broken-input proofs and the CI steps | `docs-audit` + `python-test` | W37-1, W37-2, W37-3 | — |
| W37-5 | S2 | `doc-id.py migrate` and the fixture corpus — built and proven, nothing moved | `python-package` + `python-test` | W37-4 | — |
| W37-6 | S2 | **The migration run** — one supervised PR at a gap | `subagent-driven-development`, supervised | W37-5, DP-1, DP-2, DP-3, the auditor's sweep, the gap condition | **nothing** |
| W37-7 | S3 | The remaining creating and reading instruments | `writing-skills` | W37-6 | W37-8, W37-9, W37-10 |
| W37-8 | S3 | Charters, agents, and their READMEs | `writing-skills` | W37-6 | W37-7, W37-9, W37-10 |
| W37-9 | S3 | Root governance — `CLAUDE.md` and the public face | `spec-change` | W37-6, DP-6 | W37-7, W37-8, W37-10 |
| W37-10 | S3 | `docs/` READMEs, the checklists, and the three rituals | `docs-audit` | W37-6 | W37-7, W37-8, W37-9 |
| W37-11 | S4 | Prove it — acceptance (j) and (k), and the closure evidence | `close-workstream` | W37-7 … W37-10 | — |

**Departure 1 from §8, and why.** §8's S1 is one stage; this plan cuts it into four slices
that fan out. The reason is availability rather than size: W37-1, W37-2 and W37-3 have no
real dependency on each other's *files*, because each reads its authority — the field set,
the family table, the status vocabulary — directly out of NT-0019 §1.2, §1.2a and §1.5, which
is already merged. They may therefore be dispatched together. W37-3 consumes W37-2's parser
and so may not **merge** before it, but it can be written against the signature published
below.

**Departure 2 from §8, and why.** DP-1 proposes moving seven creating skills out of S3 into
W37-6's commit. This is the only change to what lands where, it is marked blocking, and the
maintainer resolves it before W37-6 runs. If the maintainer declines, W37-7 stays where it is
and W37-6's leaf plan gains a document-creation freeze for the interval instead.

**What must not be fanned out.** W37-5 and W37-6 are one script and one supervised run of it.
§4 calls it *"one scripted PR, once"*, deterministic and idempotent. It is **not** parallel
hand-editing across 767 files, and no part of W37-6 may be split across executors: a
partially-applied rename set is a corpus in neither the old shape nor the new one, and the
gate cannot tell the two apart. W37-6 runs with one executor, supervised, at a verified gap.

---

## Slice W37-1 — The standard and the templates

**Executor skill:** `spec-change` (this creates a governed process document; the ten-section
spec rule does not apply to `process/`, but the append-only and both-direction rules do).

**Files:**
- Create: `docs/process/document-ids.md` — NT-0019 §1.1 through §1.13, **lifted verbatim**.
  The note's Deliverable row requires exactly this: *"the standard (§1) lifts verbatim into
  `docs/process/document-ids.md`"*. Not summarised, not reordered, not improved.
- Create: `docs/_templates/` — one file per document family. Thirteen files: `WF.md`,
  `ADR.md`, `RFC.md`, `PL.md`, `LG.md`, `RL.md`, `RS.md`, `CR.md`, `FD.md`, `REFERENCE.md`,
  plus `WK.md` and `SL.md` for the two row families' fenced header blocks, plus `PHASE.md`
  for a milestone section.
- Modify: `docs/README.md` — one line pointing at `document-ids.md`. Its full rewrite as the
  map is W37-10's; this slice adds the pointer only, so nothing between here and there cites
  a standard the index does not mention.

**Scope notes an executor will otherwise get wrong.**
- `_templates/` is **exempt from check 31 by path** (§1.4). The exemption is written in
  W37-4, but the templates are authored here in the shape that requires it: a template's
  `id:` field is a placeholder, not an allocated number.
- `PL.md` carries the `Decision points` table §1.7 requires — question, options,
  recommendation, kind, blocking, resolved by — and the freeze rule *"`status: active` is
  permitted only when every blocking row has a resolver id and every non-blocking row names a
  step."*
- `RFC.md`, `PL.md`, `RS.md` and `CR.md` declare their `kind:` vocabularies from §1.2's
  table and no others.
- Family-specific extra fields are **declared in the template and permitted only there**
  (§1.5): `deliverable`, `lands_in`, `trigger` for RFC; `gates`, `exit_criteria` for a phase;
  `prs:` for a ledger.
- A vendored skill carries `vendored: true` and `origin:` on its `SKILL.md` only. The
  detection rule is stated in `REFERENCE.md` and implemented in W37-2: **any directory holding
  a `LICENSE` that is not the repository's own.**

**Acceptance:** `python3 scripts/audit-docs.py` exits 0; `document-ids.md` §1.1-§1.13 is
byte-identical to NT-0019 §1.1-§1.13 modulo the heading level shift, verified by a diff
recorded in the slice's ledger; thirteen template files exist and each parses under the field
set §1.5 declares.

---

## Slice W37-2 — `doc-id.py`: `next`, `check`, `widen`, and the shared header parser

**Executor skill:** `python-package` for the module conventions, `python-test` for the
traceability markers and the negative-test emphasis.

**Files:**
- Create: `scripts/_docid.py` — the shared header parser and id grammar. **Owned by this
  slice**; W37-3 and W37-4 import it and do not redefine it.
- Create: `scripts/doc-id.py` — subcommands `next`, `check`, `widen`. **`migrate` is not in
  this slice**; it is W37-5.
- Create: `tests/test_doc_id.py`. The script tests live in the **root** `tests/` directory,
  not `backend/tests/` — thirteen modules there at `89dd2b1`, including
  `test_register_lint.py`, `test_scope_audit.py` and `test_file_census.py`. Verified, not
  assumed: `ls tests/*.py`.
- Create: `tests/fixtures/docs-ids/` — the shared fixture root W37-4 also uses, at the path
  NT-0019 §5.7 names.

**Interfaces — Produces.** W37-3 and W37-4 consume exactly this and nothing else:

```python
# scripts/_docid.py
STATUS_WORDS: Final = ("draft", "active", "closed", "retired", "superseded")
FAMILY_PREFIXES: Final = ("FR", "NFR", "DEP", "OQ", "WK", "SL", "WF",
                          "ADR", "RFC", "PL", "LG", "RL", "RS", "CR", "FD")
ID_RE: Final = re.compile(r"\b(FR|NFR|DEP|OQ|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0*(\d+)\b")
PAD_WIDTH: Final = 5

class HeaderError(Exception):
    """Malformed front matter, an unknown field, or a field of the wrong shape.
    Carries the path and the 1-based line number in its message."""

@dataclass(frozen=True)
class Header:
    id: str | None
    family: str
    kind: str | None
    title: str
    status: str
    created: date | None
    owner: str
    phase: str | None
    work: str | None
    slice_: str | None
    tree: str | None
    plans: tuple[str, ...]
    supersedes: tuple[str, ...]
    superseded_by: str | None
    corrected_by: tuple[str, ...]
    corrects: str | None
    relates: tuple[str, ...]
    was: str | None
    vendored: bool
    origin: str | None
    extra: Mapping[str, str]

def parse_header(path: Path) -> Header | None: ...
def canonical(prefix: str, n: int) -> str: ...          # canonical("PL", 1240) -> "PL-1240"
def padded(prefix: str, n: int, width: int = PAD_WIDTH) -> str:  # -> "PL-01240"
def family_of(prefix: str) -> str: ...
def is_vendored(path: Path, repo_root: Path) -> bool: ...
```

**The parser is hand-rolled and stdlib-only** (G4, DP-5). NT-0019 §1.5's field set is closed
and flat — scalars, simple `[a, b]` lists, and `~` for null — so the parser accepts exactly
that grammar and raises `HeaderError` on anything else, including a nested mapping. Rejecting
YAML the standard does not use is a feature: it is what makes the closed field set real.

**Behaviour the tests must pin, each as its own negative case.**
- `next` fetches `origin/main` and reads the maximum across **four** sources: every header
  `id`, every spec bold id, every roadmap row id, and `INDEX.md`. A test that stubs three of
  the four and passes is the defect this bullet exists to prevent.
- `check` fails on a duplicate number, on a header `id` that disagrees with its filename's
  padded integer, and on a non-contiguous sequence — **computed over `INDEX.md`, never over
  the working tree** (DP-8). A fixture carrying a local file numbered above the merged
  maximum must **pass**.
- `check --classify` prints the per-family count table Acceptance Standard item 3 reads.
- `widen --to 6` renames every padded file, rewrites every padded link target, appends to
  `REDIRECTS.csv`, updates the width in `document-ids.md`, regenerates `INDEX.md`, and
  **touches no citation, number, header or body line** (§1.8). The test asserts the last
  clause by diffing the tree with filenames and link targets normalised away.
- `is_vendored` returns true for a directory holding a `LICENSE` that is not the repository's
  own, and the test includes the repository's own `LICENSE` as the case that must return
  false.

**Acceptance:** the new tests pass; `uv run mypy` and `uv run ruff check .` exit 0; the full
gate's two halves are green; `python3 scripts/doc-id.py next` prints an integer against the
current `origin/main`.

---

## Slice W37-3 — `doc-index.py`: the index, the execution column, the ownership matrix, the phase report

**Executor skill:** `python-package` + `python-test`.

**Files:**
- Create: `scripts/doc-index.py` — generates `docs/INDEX.md`; subcommands/flags `--check`,
  `--show <id>`, `--phase P<n>`.
- Create: `tests/test_doc_index.py`.
- Extend: `tests/fixtures/docs-ids/` with a synthetic corpus carrying every family.

**Consumes:** `scripts/_docid.py`'s `parse_header`, `ID_RE`, `canonical`, `padded`,
`STATUS_WORDS` — exactly as published in W37-2. This slice adds no second parser.

**The thing an executor will get wrong.** `doc-index.py` is built here but **cannot be run
against the live corpus until W37-6**, because before the migration there are no ids to index.
Every test in this slice runs against `tests/fixtures/docs-ids/`, and the acceptance below is
fixture-scoped on purpose. Acceptance Standard item 2 — byte-stability against the real tree —
is W37-6's to prove, not this slice's.

**The `execution` column is derived, never stored** (§1.7). Its seven values and their
sources are the note's table, implemented literally: `not started`, `in progress`, `executed`,
`closed`, `superseded → PL-m`, `retired`, `terminal`. A map plan rolls up from its slices'
leaf plans — all `closed` gives `closed`; any `in progress` gives `in progress`. **Nothing
writes an execution value into a file**; a test asserts that no `Header` field carries one.

**The ownership matrix** is generated from §1.6's table, and the reporter and watcher rows are
**deliberately empty rather than absent** — §1.6 says so explicitly, so that two roles owning
no governed document read as a decision and not as two gaps. A test asserts both rows exist
and are empty.

**The phase report** (`--phase P<n>`) prints every element of §1.10 (c), enumerated in
Acceptance Standard item 10. A test asserts each element is present against a fixture phase.

**Acceptance:** tests pass against the fixture corpus; `--check` exits 1 on a fixture index
that is one row stale and 0 on a fresh one; `--show` prints an execution value for each of the
seven cases; the gate's two halves are green.

---

## Slice W37-4 — `audit-docs.py` checks 30-39, path-scoped, with ten broken-input proofs

**Executor skill:** `docs-audit` for the check conventions and the module-docstring list,
`python-test` for the fixtures.

**Files:**
- Modify: `scripts/audit-docs.py` — add checks 30-39 per NT-0019 §1.11's table, extend the
  module docstring's numbered list (and, while there, **add the missing entry 27** — the
  docstring list jumps 26 → 28 while `check_process_core_digest` runs; a real defect found
  while reading, small enough to fix in place and too small for its own finding).
- Create: `tests/test_audit_docs_ids.py` — ten broken fixtures, one per check.
- Modify: `.github/workflows/docs.yml` — `paths:` at lines 16 and 18 currently read
  `['docs/**', 'scripts/audit-docs.py', 'CLAUDE.md', '.github/workflows/docs.yml']`; add
  `scripts/doc-id.py`, `scripts/doc-index.py` and `.claude/**`. Add the two steps
  `python3 scripts/doc-id.py check` and `python3 scripts/doc-index.py --check` after line
  38's existing audit step.

**Check 30 is already taken.** `audit-docs.py`'s docstring numbers the `.claude/notes/`
tombstone check as **30**, and NT-0019 §1.11 also numbers its header check 30. NT-0019 §5.5
resolves it — *"`check_notes_tombstone` → `check_redirects`"* — so the existing 30 is
**replaced**, not renumbered, and the number is not reused for two things. `CLAUDE.md` §5's
"never reuse a number" applies: the tombstone check's number retires with it and the note's
30 takes the slot only because the note's 36 is its successor. **This is the one place in the
plan where a check number's identity changes; it is called out here so nobody does it
silently.** The executor records the substitution in the docstring with a dated line.

**Scoping for S1** (DP-5's sibling, and the mechanism D14 depends on). Checks 30-39 land here
but must not red the un-migrated corpus. The mechanism is a single module-level constant:

```python
#: Roots checks 30-39 apply to. In W37-4 this is the set of paths that exist *after* the
#: standard lands and *before* the migration; W37-6 replaces it with the whole corpus in the
#: same commit that migrates, which is D14's "enforcement red from the migration PR".
_ID_SCOPE_ROOTS: Final = (DOCS / "_templates", DOCS / "process" / "document-ids.md")
```

One constant, one line to flip, and the flip is visible in W37-6's diff. **Not** a date-based
switch and **not** a warn phase: D14 rules both out.

**Ten broken-input proofs, one per check.** Each fixture makes exactly one check exit 1 and
leaves the other nine at 0 — a fixture that trips two checks proves neither. The pairing is
recorded in the test module and repeated in the closure record (Acceptance Standard item 11).
Check 34's pair is the one to write first, because it is the subtlest: **a frozen fixture
whose body has one word changed must fail; the same fixture with only `REDIRECTS.csv` token
substitutions and a front-matter block added must pass** (DP-7).

**Acceptance:** all ten proofs demonstrated; `python3 scripts/audit-docs.py` exits 0 on the
real tree with `_ID_SCOPE_ROOTS` as above; the docs workflow's two new steps run green; the
gate's two halves are green.

---

## Slice W37-5 — `doc-id.py migrate`, built and proven; nothing moved

**Executor skill:** `python-package` + `python-test`.

**Files:**
- Modify: `scripts/doc-id.py` — add the `migrate` subcommand implementing §4 steps 1-7.
- Create: `tests/fixtures/docs-migration/` — a miniature corpus carrying **every legacy shape
  the real tree contains**: a multi-ruling file with `## Ruling N` headings, a
  closure-records file with per-work headings, a plan-reviews file with per-review headings,
  a plans directory holding all four suffixes and one suffix-less file, an ADR with a bullet
  header, a note with a prose-table header, a spec fragment with bold requirement ids, a
  roadmap fragment with phase sections and work rows, a register, and a vendored skill
  directory with its own `LICENSE`.
- Create: the classification script §10's last line names — *"classify every governance file
  by §4's rules → 0 unmapped"* — as a test helper, not a separate script.

**Nothing in the real tree moves in this slice.** Every test runs against the fixture corpus.

**What `migrate` must do, and the ordering that matters.** §4's seven steps in order —
assign, split, restructure the roadmap, move, stamp, rewrite citations, regenerate. Two
properties the tests pin:
- **Deterministic.** Two runs from the same input produce byte-identical output, including
  the number assignment. The assignment order is §4 step 1's: `created`-date order (header
  date; filename date for plans; the ADR `Date:` line; spec module order then clause order
  for requirements, using the module's first-commit date; git first-commit date otherwise),
  ties broken by family order in §1.2 then filename.
- **Idempotent.** Running `migrate` on an already-migrated corpus is a no-op — zero diff.

**Acceptance (a) and (g) are proven here, on the fixture, before the real run.** (a): every
fixture file classifies to exactly one family, "none" is 0. (g), under DP-3's option (a): the
diff of a `migrate` run on a clean fixture, filtered to hunks that are neither a front-matter
block nor a token substitution drawn from the generated `REDIRECTS.csv`, is empty.

**Acceptance:** the fixture corpus migrates deterministically and idempotently; (a) and (g)
pass on it; the gate's two halves are green; **`git status --porcelain docs/` is empty** — the
proof that this slice moved nothing.

---

## Slice W37-6 — The migration run: one supervised PR at a gap

**Executor skill:** `subagent-driven-development`, **single executor, supervised, not fanned
out.** §4: *"one scripted PR, once."*

**Preconditions, all of which are re-derived in the session that runs the migration, not
inherited from this plan:**

- [ ] DP-1, DP-2 and DP-3 each carry a resolver id.
- [ ] The auditor's full-class sweep of NT-0019 §5 against `89dd2b1` has landed, and its
      per-row result is attached to this slice's leaf plan. **The leaf plan's task list is
      written from the sweep, not from this map plan's evidence table.**
- [ ] `gh pr list --state open` returns nothing.
- [ ] `git branch -r` lists only `origin/main`.
- [ ] `git status --porcelain` is empty.
- [ ] The maintainer has given a dated go-ahead for this specific run. It dissolves
      `docs/audit/`, renumbers every requirement id in the repository, and rewrites citations
      in 1355 tracked files; it is not a slice a lead dispatches on standing authority.

**What lands in this one commit** (§8's S2 list, verbatim, plus DP-1's addition if accepted):
the `migrate` run's whole output; `audit-docs.py`'s parsers and path roots including the
`_ID_SCOPE_ROOTS` flip to the whole corpus; `register-lint.py` and `register-owed.py`;
`req-coverage.py`; `scope-audit.py`; `file-census.py`; `graphify-docs-extract.py`; the ten
fixture tests §5.7 names; `docs.yml`'s path filter; the process-core digest; the roadmap
restructure into milestone sections with `WK-`/`SL-` rows; and `delivery-process.md`'s §3
vocabulary. If DP-1 is accepted, the seven creating skills join it.

**The scan-roots guard will fire, and that is the guard working.**
`tests/test_audit_docs_scan_roots.py` exists because a vanished scan root used to make five
checks *skip* while the audit printed "All checks passed" and exited 0 — its docstring:
*"A `git mv` of that
directory for any reason -- not only NT-0016's planned move -- would leave the gate green
while five checks stopped running."* This migration does exactly that twice: `docs/notes/`
becomes `docs/rfcs/`, and `docs/audit/` dissolves into `findings/`, `closures/`, `research/`
and `process/`. **The failure is sharper than a behavioural one**: the test asserts the
literal source string `NOTES = REPO / "docs" / "notes"` is present in `audit-docs.py`, with
the message *"the NOTES constant has moved -- re-derive this test before trusting it"*. So it
trips on the constant's **text**, and it is telling the truth. **The fix is to re-point the
roots and re-derive the test against the moved ones — never to loosen the assertion**, and
the re-run must happen *after* the move, on the test's own stated principle that *"a green
audit after a directory move proves nothing on its own."* This is the mechanism behind §8's
"`audit-docs.py` parsers and roots" landing in this commit; `check_finding_citations`'s
`scan_dirs` is the second root and moves with it.

**Every acceptance item here is stated as a violation that must be detectable, not a property
asserted** — the same standard that test holds itself to. (d) is a grep that must return
nothing and would return something if one legacy form survived; (g) is a diff that must be
empty and would be non-empty if the script touched a body line; (a) is a classification whose
"none" row must be 0 and would be positive if one file failed to parse; item 11's ten proofs
each require a check to *print a failure* on a fixture built to break it. An item that cannot
fail has not been tested (`CLAUDE.md` §13).

**The rebase rule.** §4 step 8: *"Land at a gap; rebase any branch that appears by re-running
step 6 on its diff."* If a branch appears mid-run, the recovery is to re-run the citation
rewrite over that branch's diff — **never** to hand-edit it.

**Never touched** (G5, D5): `VR-*` catalogue ids, artifact ids, job kinds, and any string
persisted or asserted as data. §5.6's closing sentence is the reason every touched file is
compiled and its suite run: *"a rewrite inside an asserted string is the reason."* And
(G10) nothing outside the repository — the run's own input is `git ls-files`, so the local
working tree is out of reach by construction as well as by rule.

**Acceptance:** §7 (a) through (h) all pass at the merge tree, each recorded with its command
and output in the slice's ledger; Acceptance Standard items 1-7 above are the executable form
of them.

---

## Slice W37-7 — The remaining creating and reading instruments

**Executor skill:** `writing-skills`. Every skill touched has its `Verified` date refreshed
in the same commit (`CLAUDE.md` §12).

**Scope:** §5.4's rows, less whatever DP-1 moves into W37-6. In the order they matter:
`docs-audit` (checks 30-39 described, the four-kinds paragraph and the `YYYY-MM-DD-` grammar
removed, the tombstone check replaced by the redirects check); `dev-commands` (`doc-id.py
next/check/widen`, `doc-index.py --check/--phase`); `git-hygiene` (branch `sl-<n>-<slug>`, PR
title `SL-<n>: <title>`); `reporter-cycle` and its scripts (the fortnightly work-item status
entry of §1.10 (a)); `repo-architecture` (the annotated `docs/` tree replaced by §1.4's);
`python-test` and `testing-strategy` (the marker form); `brainstorming` and
`planning-with-files` (one sentence each: scratch is not a family, the committed record is a
plan or a ledger); `.claude/skills/README.md` (a "creates" column per creating skill); and the
bespoke-audit rule that belongs in both `close-workstream` and `docs-audit` — **a bespoke
audit is a slice whose record is a research document of kind `audit`, owner the auditor, every
finding its own finding record; never a plan, never a closure.**

**Acceptance:** every §5.4 row not landed in W37-6 is named by a commit in this slice's
ledger; `python3 scripts/audit-docs.py` exits 0; the gate's two halves are green; no skill
retains a path or an id form the migration retired, verified by the Acceptance Standard item 4
sweep restricted to `.claude/skills/`.

---

## Slice W37-8 — Charters, agents, and their READMEs

**Executor skill:** `writing-skills`.

**Scope:** §5.3's rows — the seven charters under `.claude/roles/`, `.claude/agents/README.md`
and the two agent files §5.3 names, each gaining its header and its §1.6 role content. Plus
the one row that creates nothing: **there is no maintainer charter**, because the maintainer
is not a spawned role; the maintainer's authorities are listed once in `document-ids.md` §1.6
and once in `CLAUDE.md` §12, and nowhere else.

**DP-6 applies.** A charter is the maintainer's (§1.6, Reference — charters row). The executor
drafts each diff; the slice's acceptance requires a dated maintainer line on the PR before
merge. This is a gate, not a blocker: drafting proceeds while the line is pending.

**The reporter and the watcher rows are the ones to get right.** Both charters must state
*"owns no governed document"* explicitly, so W37-3's generated ownership matrix shows two
deliberately empty rows rather than two gaps. An executor who leaves the sentence out makes
the matrix report a defect that does not exist.

**Acceptance:** all seven charters and the agents files carry a valid header; the generated
ownership matrix has no empty cell that is not one of the two declared ones; a dated maintainer
line exists for every charter edit; the gate's two halves are green.

---

## Slice W37-9 — Root governance: `CLAUDE.md` and the public face

**Executor skill:** `spec-change` (the governed-document procedure), with DP-6's maintainer
gate.

**Scope:** §5.1's rows. `CLAUDE.md` — §2's layout replaced by §1.4's tree, §4's module map
rewritten, §5 gaining *"document and row ids are `document-ids.md`'s; product identifiers stay
the spec's"*, §9's roadmap pointer naming phases-as-milestones and the work and slice row
families, §12 naming the owner table, and §13-§15's pointers moved to the closures, findings
and rulings directories. Then `README.md`, `CONTRIBUTING.md`, `SECURITY.md`,
`.github/PULL_REQUEST_TEMPLATE.md`, the issue templates, `.gitignore`'s comment block, and
`.importlinter`'s contract names.

**G2 is this slice's hardest obligation and its easiest miss.** The permanence rule appears
**twice** in `CLAUDE.md` — line 27's §0 bullet and line 107's §5 sentence. Both yield to D2.
Each edit carries a dated line naming NT-0019 as what it yielded to, per G1's no-silent-change
limit. **Editing one and not the other leaves the project contract contradicting itself**, and
the second site is the one an executor working from a §5 checklist never opens.

**The PR template gains a required slice line**, per §1.9: a merged PR's title names the slice
it delivered, and a PR arriving without one — a hotfix, an external contributor, a dependency
bump — gets its slice minted by the lead at triage under the phase's standing maintenance work
item. Bot authors are exempt. The template says so.

**Acceptance:** a dated maintainer line for the `CLAUDE.md` edit; both permanence sites edited
and each carrying its dated line; `python3 scripts/audit-docs.py` exits 0; `uv run
lint-imports` exits 0 after the contract rename; the gate's two halves are green.

---

## Slice W37-10 — `docs/` READMEs, the checklists, and the three rituals

**Executor skill:** `docs-audit`.

**Scope:** §5.2's H rows. `docs/README.md` rewritten as the map — §1.4's tree, §1.2's family
table, the reading order and the check commands, and **nothing that goes stale**. New READMEs
for `closures/`, `findings/`, `rulings/` and `ledgers/`; the `plans/` README's naming and
four-kinds table replaced by a pointer, **the nine writing conventions kept verbatim** —
they are the accumulated cost of nine real failures and none of them is about naming. The
checklists move under `process/checklists/` and each gains *"a new record has an id;
`audit-docs` is green"*; the phase-close checklist additionally gains the freeze-gate and
generated-report lines.

**The three rituals** (§1.10, §6): the fortnightly work-item status entry driven by
`reporter-cycle`; the dated plan/code/docs freeze gates declared in each phase's milestone
section and checked by the phase-close checklist; and the generated phase report as the body
of every closure record of kind `phase` — **never a hand-kept table.**

**Acceptance:** every §5.2 H row is named by a commit; `docs/audit/` no longer exists and
nothing references it (Acceptance Standard item 4's sweep restricted to `docs/`); the phase
close checklist names the freeze gates; the gate's two halves are green.

---

## Slice W37-11 — Prove it, and file the closure evidence

**Executor skill:** `close-workstream`.

**Scope:** acceptance items (j) and (k), and the closure record.

- **(k)** is mechanical: `python3 scripts/doc-index.py --phase P1b` produces the report §1.10
  (c) describes, checked element by element against Acceptance Standard item 10.
- **(j)** is discharged under DP-4's option (a) — as a standing condition on the first slices
  of the two downstream Works §8 names, the charter investigation and the create-read-retire
  audit. This slice records **which families are discharged and which are owed**, with the
  event that will discharge each. A family recorded as owed with no named event is a finding,
  not an acceptance.
- The closure record carries: the H-row table (Acceptance Standard item 8), the ten
  broken-input proofs (item 11), the §7 (a)-(h) evidence from W37-6's ledger, and a verdict
  for every requirement of the note that has no evidence — delivered but untested, deferred
  with an owner, reassigned, or not started. Silence is not a verdict, and the verdict is the
  lead's, never a subagent's (`CLAUDE.md` §13).

**Acceptance:** every item of this plan's Acceptance Standard has a recorded result; the
maintainer has accepted the Work close with a dated line.

---

## Proposal — the roadmap row (the lead's to apply; not written by this plan)

`docs/roadmap.md` is the lead's file. This section is a recommendation, per
`.claude/roles/planner.md`. The row belongs in the table under **Phase 2 — Rating Engine →
Workstreams**, whose header at line 371 is `| # | Workstream | Notes |` — three columns.

**Recommended number: W37.** Derived, not chosen: `grep -oE '\bW[0-9]+' docs/roadmap.md |
grep -oE '[0-9]+' | sort -n | tail -1` returns **36** at `89dd2b1`, and W33-W36 were created
by #553 the same day. W37 is the next free integer, and no lettered variant is appropriate —
this is a new Work, not a split of an existing one.

**Placement:** immediately after the W36 row at line 381, keeping the four reconciliation-born
rows contiguous and ahead of W30's row at line 385.

Paste-ready. **Two mechanical notes for whoever pastes it.** First, the row deliberately
carries **no markdown link**. A roadmap-relative target — the form W35's row uses for
NT-0016, a relative path starting `../docs/notes/` — resolves from `docs/roadmap.md` but not
from `docs/plans/`, so reproducing one inside this file reds `audit-docs.py` check 1. **This
plan hit exactly that on its first audit run**, which is the evidence the warning is real
rather than theoretical. When pasting, wrap the row's first `NT-0019` mention in a markdown
link using the same relative-path form W35's row uses, with `0019-one-id-per-document.md` as
the filename. Second, the row is three cells, matching the table header at line 371.

```
| **W37** | **One id per governed thing — NT-0019, the whole standard** | Adopted 2026-09-01 from NT-0019 by the note's own dated `accepted` status, which the maintainer ruled that day is the acceptance line for this row — NT-0019 arrived accepted rather than being moved to accepted by a reconciliation, so the "reconciliation's dated acceptance line" the three rows above cite has no referent here; the derivation is in the map plan's Authority section. **Scope:** the note's §1 standard in full — one global integer sequence across every row and document family, the five-word status vocabulary, the family-per-directory layout, the YAML header with its closed field set, roles per family, and the generated index, ownership matrix and phase report. Its §4 one-time scripted migration; its §5 impact map — root governance, all of `docs/`, seven role charters, two agents, every skill (twenty-six substantively, a header on all forty-six), fourteen scripts, twelve tests, two CI workflows, and every code and test file citing a document or requirement (767 such files at the note's own tree `8f5d57d`, 770 at `89dd2b1`); and its §7 acceptance items (a)-(k). **Eleven slices** cut from the note's §8 stages S1-S4 by `docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md` — four building the instruments in parallel, one building the migration script against a fixture corpus, **one supervised run that moves the whole corpus and must land at a gap with no open branches**, four applying the conventions, and one proving acceptance (j) and (k). **Supersedes most of W35**: NT-0019 §9 replaces NT-0016 Stages 2 and 5 outright, lifts constraints C1 and C2, and Rulings 63 and 65 lapse by their own override clauses; Stages 3 and 4 survive as the two downstream Works the note's §8 names — the charter investigation and the create-read-retire audit. Ruling 64 is kept, as check 38. Rulings 55-58 are absorbed. **W35's row needs the lead's disposition in the same edit**, or the roadmap will carry two live rows planning the same corpus in incompatible directions — a bulk rename here against W35's "never a bulk rename". **Eight decision points recorded**: two disposed of in the plan with their reasoning, six open, four of those blocking — three block the migration run itself (two the maintainer's, one the decision-maker's) and one blocks the `CLAUDE.md` slice. **Acceptance:** the note's §7 (a)-(k) |
```

**Two things the lead should decide while pasting, which this plan cannot:**

1. **W35's disposition — the one that must not be skipped.** W35 was created 2026-09-01 by
   #553, and NT-0019, merged the same day as #555, supersedes its Stages 2 and 5, lifts the
   C1 constraint its scope rests on, and lapses two of the rulings it cites. Leaving both
   rows live leaves the roadmap planning one corpus twice in opposite directions — a bulk
   rename in W37 against W35's *"legacy migrates opportunistically-on-amendment only, never a
   bulk rename (C1)"*. The options are to mark W35 superseded by W37, carrying Stages 3 and 4
   into the two downstream Works, or to re-cut W35 down to those two stages. Either is the
   lead's; **recording neither is not an option**, because the next planner to read the
   roadmap will plan against whichever row they open first.
2. **Whether the row's markdown link is added**, as the mechanical note above describes.

## Self-review

Run against NT-0019 with fresh eyes, per `writing-plans`.

**Spec coverage.** Every §5 sub-section maps to a slice: §5.1 → W37-9; §5.2 → W37-6 (M rows,
the roadmap restructure, the process vocabulary) and W37-10 (H rows); §5.3 → W37-8; §5.4 →
W37-7 and, if DP-1 is accepted, W37-6; §5.5 → W37-2, W37-3, W37-4, W37-5 and W37-6; §5.6 →
W37-6; §5.7 → W37-2, W37-3, W37-4 and W37-6; §5.8 → W37-4 and W37-6. Every §7 item maps to a
numbered Acceptance Standard entry: (a)→3, (b)→1, (c)→2, (d)→4, (e)→5, (f)→6, (g)→13,
(h)→7, (i)→8, (j)→9, (k)→10. Item 13 was **added during this self-review**: the first pass
mapped (g) to "W37-5's slice acceptance" and claimed in the same sentence that every §7 item
had a numbered entry, which was false of exactly the item the sentence was written to cover.
**One gap found and left open on purpose:** §1.9's lint that *"a merged PR's title names the
`SL-` it delivered and the slice's ledger records the PR number"* is check 39's second half,
and it cannot be proved by this Work — the first PR it can fire on is the first PR after the
standard lands. It is named in W37-11's owed list rather than claimed.

**Placeholder scan.** Zero placeholders. The roadmap row's plan reference held one on the
first pass and now carries the real path. No task says "add appropriate error handling",
"TBD", or "similar to slice N".

**Derived counts, re-derived rather than re-read.** Three numbers in the roadmap row were
wrong on the first pass and are corrected: the skills count conflated the twenty-six changed
substantively with the forty-six getting a header (both true, of different predicates — the
row now says which is which); the scripts count read seventeen from the directory population
rather than fourteen from §5.5's changed set; and the decision-point sentence said "eight
open, six blocking" when the table holds eight recorded, six open and four blocking. A count
in a summary line is the class of claim this plan's own Evidence section exists to discipline,
and it failed first inside the summary rather than inside the evidence.

**Type consistency.** `scripts/_docid.py`'s published names are used identically in W37-3 and
W37-4: `parse_header`, `Header`, `ID_RE`, `canonical`, `padded`, `family_of`, `is_vendored`,
`STATUS_WORDS`, `FAMILY_PREFIXES`, `PAD_WIDTH`. The dataclass field is `slice_` and not
`slice` throughout, because `slice` is a builtin; the header **key** stays `slice:` as §1.5
writes it, and the parser maps between them. `_ID_SCOPE_ROOTS` is named once in W37-4 and
referenced once in W37-6.

**Repository literals.** Every literal in this plan that is a fact about the repository rather
than a choice was verified at `89dd2b1` by a command recorded in the Evidence section or
inline: the workflow's `paths:` list and its line numbers, `audit-docs.py`'s import set, the
two `ADR-(\d{4})` sites at lines 471 and 1117, check 28's cutoff constant and heading regex,
the permanence rule's two line numbers in `CLAUDE.md`, the roadmap table's three-column header
at line 371, the highest workstream number, and every population count. Where a figure is the
auditor's rather than mine, the Evidence section says so and W37-6 is gated on it.

## Execution Handoff

Slices W37-1, W37-2 and W37-3 are unblocked and may be dispatched together. W37-4 follows
them. W37-5 follows W37-4. **W37-6 is gated** on three maintainer resolutions, the auditor's
sweep, and a re-derived gap; it is a single supervised run and is not fanned out. W37-7 through
W37-10 fan out after W37-6. W37-11 closes.

Each slice gets its own leaf plan written when it is dispatched, under `writing-plans`, and
each of those is in check 28's scope (G9).
