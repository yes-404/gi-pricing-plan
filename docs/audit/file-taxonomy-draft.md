# File taxonomy — draft (NT-0016 Stage 1)

**Status: a draft. It rules nothing.** Every category below is a candidate, every home is
today's observed home rather than a proposed one, and the four questions in §5 are stated
as choices between named options for the decision-maker to rule at the gate
[`2026-08-31-nt-0016-investigation.md`](../plans/2026-08-31-nt-0016-investigation.md) §4 defines
(NT-0016 §10). Nothing here amends `docs/plans/README.md`'s four declared kinds, adds a
category, or assigns an owner. Where this document uses the word "finding" it means the
census surfaced something a decision-maker or auditor should look at — never a filed
register row; filing one is outside this role's charter and outside this slice's scope.

**Evidence tree: `main` at `4f95fb3f93f820fc15b3abd416de20427bd8571d`** (PR #537, "the census
script"). Every count below was gathered against the tree tagged `26adb64` on this slice's
now-discarded working branch (`origin/exec-nt-0016-slice2-file-census`, rebased once while
this draft was in flight and superseded outright once #537 squash-merged) — re-derived
rather than assumed at each rebase, per this slice's own dispatch instruction. **That
working-branch tree and `4f95fb3` are verified content-identical**: `git diff 26adb64...
4f95fb3f93f820fc15b3abd416de20427bd8571d --stat` is empty, and `git ls-tree -r <tree> |
wc -l` returns **1328** for both. `26adb64` itself does not resolve on `main` — it was a
private branch commit, discarded by the squash-merge — so every citation below names
`4f95fb3` instead, the tree a reader holding none of this session's context can actually
check out. The committed census CSV's own tree, `5ef559d`, is an ancestor of `4f95fb3`,
seven commits behind it — `5ef559d` is the tree the CSV *describes*
([`file-census.md`](file-census.md)'s own "circularity" note explains why a census cannot
name the commit that first introduces it), not the commit that added the CSV file to the
tree, which is `4f95fb3` itself (PR #537's squash-merge). Two of the seven intervening
commits touch `docs/plans/` (Rulings 59 and 60, both counted in this draft's `docs/plans/`
population below); this draft's own commit is later again, by the same non-circularity
argument. Every count below either cites the committed CSV at `5ef559d`, or was regenerated
by re-running `python3 scripts/file-census.py` per NT-0016 Slice 3 Step 1 — each figure says
which. The corpus for every count is `git ls-files` (`docs/audit/file-census.md`'s corpus
rule), **1328 tracked files at `4f95fb3`** (`git ls-files | wc -l`), against **1319** at
`5ef559d`. One file relevant to this draft landed between the two trees:
`2026-09-01-ruling-60-census-provenance-checkout-depth.md` under `docs/plans/`, folded into
every count below that depends on the `docs/plans/`
population. The committed census content at `5ef559d` is byte-identical across both branch
states — only a CI workflow fix and this one new plan file changed.

---

## 0. Methodology notes — read before the category sections

Two measurement artifacts were found while regenerating the census at `4f95fb3` for this
draft. Both matter to every count below that depends on `referenced_by`, so they are stated
once, here, rather than re-argued in each section.

### 0.1 The census-of-a-census artifact — a standing property of the method, not an incident

**The precise claim, stated narrowly first because it is easy to overstate.** The
`5ef559d` census's own committed values are clean: `docs/audit/file-census-5ef559d.csv`
was not itself a tracked file at `5ef559d` — it was added one commit later — so the
row-by-row `referenced_by` figures inside that CSV measured a tree that did not yet
contain it, and were never contaminated by it. Verified directly:
`grep -c '^docs/audit/file-census' docs/audit/file-census-5ef559d.csv` returns `0` —
the CSV does not even mention itself. **What is affected is every regeneration after the
CSV was committed, not the committed artifact itself.** This is a narrower and more
precise claim than "the census is self-referential," and it is the one this draft makes.

**The mechanism, and why it is a standing property of the method rather than a one-off
defect.** Once a census CSV is committed, it becomes — for every census generated
afterward — a tracked file that is itself a full listing of every path in the corpus it
was taken over. `scripts/file-census.py`'s `referenced_by` rule (unmodified by this slice,
per NT-0016's Global Constraints) counts *tracked files whose content contains the
target's basename*. A committed census CSV satisfies that rule for nearly every file it
lists, **not because any file cites the target, but because the CSV's own data rows are a
literal enumeration of every basename in the corpus.** The census counting the corpus
becomes, once committed, a reference to every file in the corpus it counted — for every
census run after that commit, without exception, for as long as `referenced_by`'s rule
stays a basename-substring match over tracked-file content. **This will happen again**:
this draft's own file, once committed, is itself a tracked file whose prose names dozens
of `docs/plans/` basenames verbatim (§4's table), so the *next* regeneration after this
draft lands will need the same correction, against a three-file exclusion list rather
than two. A future regeneration that skips this correction will report an unreferenced
count that is too low by construction, not because anything started being read, but
because the instrument that measures "unread" was itself read by the next instance of
itself.

Measured directly: regenerating the census at `4f95fb3` and filtering to the 122 plan files
that already existed at `5ef559d` gives **zero** of them with a raw `referenced_by` of 0 —
every one now shows `referenced_by >= 1`, and for **38 of them** the entire increase from
their `5ef559d` count is attributable to exactly one new "referencing" file:
`docs/audit/file-census-5ef559d.csv` itself. Excluding matches that originate solely from
`docs/audit/file-census-5ef559d.csv` and `docs/audit/file-census.md` (the census's own
companion document, which does not enumerate every path but does name a handful as pattern
examples) restores the same 38-file set that carried `referenced_by == 0` in the committed
`5ef559d` CSV before this artifact existed — the two independent readings agree exactly,
which is the check this draft relies on to say the correction recovers the pre-pollution
measurement rather than inventing a new one.

**§4's population is 39, not 38** — two more `docs/plans/` files landed on `main` while this
draft's evidence tree was being fixed (§ "Evidence tree" above), both rulings records
(`2026-09-01-nt-0016-slice2-fr-data-32-ruling.md`, "Ruling 59," and
`2026-09-01-ruling-60-census-provenance-checkout-depth.md`, "Ruling 60"). Ruling 59's file
is genuinely referenced (Ruling 60's own text cites it by name) and is not part of either
population. Ruling 60's file is unreferenced, but for an entirely different, mundane reason
than the 38 above: it postdates the committed `5ef559d` CSV, so it was never one of the
paths that CSV lists, and its zero count is not a pollution artifact at all — it is simply
too new to have been cited by anything yet (§4's own #39 makes this distinction explicit).
**39 = 38 pollution-corrected pre-existing files + 1 genuinely new file**, and §4 decomposes
all 39.

**What this means for §4's count.** The census script's raw output at `4f95fb3`, read
literally, reports **zero** of the 122 pre-existing `docs/plans/` files with
`referenced_by == 0` — which would make §4's decomposition of those 38 vacuous were it taken
at face value. §4 instead uses the corrected count (38, after excluding the two
census-artifact files as spurious "referrers," plus the one genuinely new file), because the
raw number is an artifact of the census having been committed once already, not a
measurement of whether anything reads these files. **This is a real, structural property of
`referenced_by`'s design, not a bug in Slice 2's script** — the script is frozen and this
slice does not touch it (NT-0016 Global Constraints) — and it recurs every time a census is
committed and then re-run: this draft's own file, once committed, will itself become a
polluting artifact for the next regeneration, for the same reason. Whoever re-runs the
census after this draft lands should expect the same correction to be necessary, against a
two-file exclusion list that has grown to three.

### 0.2 Closure records cite by requirement id, slice id or work id — never by plan filename

Independently of §0.1, cross-checking a sample of `docs/plans/` files against
`docs/audit/closure-records.md` and `docs/roadmap.md` shows that a closed workstream's
closure record cites the **requirement id** (`FR-MODEL-78`), the **slice id** (`W6b-10`,
`W32-4`) or the **PR number**, and not, in the cases checked, the plan's own filename. For
example, `docs/audit/closure-records.md`'s W6b delivery table cites `W6b-10 browser auth`
and `#250`; it does not cite `2026-08-25-w6b-10-browser-auth.md`. This means
`referenced_by`'s basename-substring rule **cannot see** the very citation relationship
that closes a slice out — a limitation the census's own companion document already names in
the abstract ("under-counts a file cited only by a fuzzy description... neither is silent,
because the rule is written down") but which is worth stating concretely here, because it is
the single largest source of false "unreferenced" readings in §4's population, corrected
there by reading each file against its closure record rather than by `referenced_by` alone.

### 0.3 Scope of the `name_pattern` clustering below

NT-0016 §8's own text scopes code-file conventions under `backend/`, `packages/` and
`frontend/` out of the investigation ("owned by the language skills and ruff/mypy already —
different mechanism, already enforced"). Clustering `name_pattern` over the full 1328-row
corpus pulls in hundreds of Python module basenames that repeat across `backend/` and
`packages/` sub-packages by coincidence of naming convention (`settings.py`, `models.py`,
`__init__.py`) — not because they represent a document category. §1 below therefore clusters
`name_pattern` only over the `docs` and `.claude` areas — **689 of 1328 rows at `4f95fb3`**
— matching NT-0016 §0's own opening-evidence scope (`docs/` + `.claude/` populations, not the
whole tree).

---

## 1. Candidate categories

Twelve categories carried forward from NT-0016 §3's working hypothesis, each re-measured at
this draft's tree rather than assumed. Home, mutability and id family are the census's own
column definitions (`docs/audit/file-census.md` "Column rules"); "rejected reading" is the
alternative this draft considered and did not adopt, stated so a reader can re-open it.

### 1.1 spec

- **Purpose.** The requirement suite the platform is built against — `FR-`/`NFR-`/`OQ-` ids,
  ten sections each, per `CLAUDE.md` §5.
- **Mutability.** `living` (amended in place, append-only ids) — matches the census's own
  directory rule.
- **Today's home.** `docs/specs/`.
- **Id family.** `FR-`/`NFR-`/`OQ-`, module-prefixed (`FR-MODEL-`, `FR-DATA-`, ...).
- **Census evidence.** `docs/specs/` = **8 files** at `4f95fb3`
  (`00-overview.md` through `07-platform.md`), all `mutability=living`. No `name_pattern`
  with count 2 or more falls in this area — each module file has a distinct basename.
- **Rejected reading.** None considered — this category is the least contested in the
  hypothesis and the census does not disturb it.

### 1.2 plan (map / leaf)

- **Purpose.** The implementation plan — goal, architecture, tasks, steps
  (`docs/plans/README.md`'s declared *(none)* kind).
- **Mutability.** `frozen` at its date (census directory rule and `docs/plans/README.md`).
- **Today's home.** `docs/plans/`.
- **Id family.** None — identified by its dated filename only, never a minted id.
- **Census evidence, at `4f95fb3`, mutually-exclusive classification of all 124
  `docs/plans/` files by filename suffix:**

  | Sub-kind | Count | Example `name_pattern` |
  |---|---|---|
  | leaf plan (no suffix token) | 72 | `DATE-wN-N-diagnostics-view.md`, `DATE-tweedie-profile-likelihood.md` |
  | map / slice-map | 5 (4 `slice-map`, 1 `map-plan`) | `DATE-wNb-slice-map.md`, `DATE-wNb-slice-map-revised-N.md`, `DATE-wN-map-plan.md` |

  The map/leaf split the hypothesis names is real but **inconsistently spelled across two
  eras**: the four W6b-era files use the token `slice-map` (one revised twice more, each a
  distinct filename rather than an edit — `docs/plans/README.md`'s frozen-file rule read
  literally, since a map plan is itself frozen once filed); the one W12-era file uses
  `map-plan` instead. Both name the same underlying object — the note calls it "plan
  (map / leaf)" as one category — and a reader clustering by literal `name_pattern`
  equality alone would miss the relationship, because `slice-map` and `map-plan` do not
  share a `name_pattern`. This is evidence *for* Q1's rebuild-from-census recommendation
  over drafted-as-is: the hypothesis names the right category, but the filenames the
  census actually contains do not yet agree on a grammar for it.
- **Rejected reading.** Treating "map plan" as its own category, separate from "leaf plan."
  Rejected because NT-0016 §3's table names one row, "plan (map / leaf)," and the two are
  the same document type at different scopes (a map plan cuts a Work into slices; a leaf
  plan details one slice) rather than two purposes — the same relationship
  `docs/process/delivery-process.md` §3 already describes for a Work versus a Slice.

### 1.3 rulings record

- **Purpose.** The dated, sibling home for a decision-maker's ruling on a decision point —
  never an edit to the frozen plan it rules on (`.claude/roles/decision-maker.md`: "Owns:
  ...decision-point rulings... recorded as dated sibling records, never edits to a frozen
  plan").
- **Mutability.** `write-once-amend` (NT-0016 §3's own term; the census's directory rule
  reports it as `frozen`, since it lives in `docs/plans/` and the census does not
  distinguish sub-kinds by header).
- **Today's home.** `docs/plans/`, mixed in with leaf plans.
- **Id family.** Sequential `Ruling N` numbers, informally assigned within a document, not a
  registered id family the census or `req-coverage.py` tracks.
- **Census evidence.** **24 files** at `4f95fb3` match a filename ending in `-ruling.md`,
  `-rulings.md`, containing `-rulings-`, or matching a `ruling-<number>-<slug>.md` shape
  (mutually-exclusive classification, §1.2's table method), up from the plan's own
  `b551060` re-run of NT-0016 §9's token sweep ("ruling 10... rulings 11," one family, 21
  files, at a different, earlier tree). The growth (21 to 24) is three files in the days
  between `b551060` and `4f95fb3` — consistent with, not contradicting,
  [`2026-08-31-nt-0016-investigation.md`](../plans/2026-08-31-nt-0016-investigation.md)
  §1a's observation that a citation surface's growth is roughly proportional to how often
  the team is actively ruling things. One of the 24 —
  `2026-09-01-ruling-60-census-provenance-checkout-depth.md`, added while this draft was
  being written — is a **second, distinct filename grammar for the same category**: the
  ruling number leads the slug (`ruling-60-...`) rather than trailing it
  (`...-ruling.md`/`...-rulings.md`). A naive suffix-only classifier misses it entirely (it
  first read as a plain leaf plan); this draft's classification was corrected to catch the
  shape once found. This is the same class of finding as §1.2's map/leaf naming split — a
  second, independently-discovered case of one candidate category with two live filename
  grammars, further evidence for Q1's rebuild-from-census option.
- **Rejected reading.** Splitting "ruling" (singular decisions, e.g. a decision-point
  ruling) from "rulings" (plural, e.g. a batch of several rulings recorded in one sitting)
  as two categories. Rejected: every file in the 24 is the same object — one or more dated
  rulings recorded together — and the singular/plural spelling tracks how many rulings a
  given sitting produced, not a difference in kind.

### 1.4 ledger

- **Purpose.** What execution actually did, task by task (`docs/plans/README.md`'s declared
  `-ledger` kind, written by `subagent-driven-development`).
- **Mutability.** `append-only` (NT-0016 §3's term; census reports `frozen` by directory,
  same caveat as §1.3).
- **Today's home.** `docs/plans/`, mixed in.
- **Id family.** None — filename only, no minted id.
- **Census evidence.** **16 files** at `4f95fb3` match a filename ending in `-ledger.md`
  (mutually-exclusive classification), matching NT-0016 §0's own `7db62ca` figure of 16
  exactly — the ledger count is the one sub-population that has not grown across three tree
  readings (`7db62ca`, `b551060`, `4f95fb3`), consistent with a design where a ledger is
  written once, at the close of a slice already executed, rather than accumulating
  independently of slice cadence.
- **Rejected reading.** That a ledger's zero-growth means the category has stopped being
  used. Rejected — §4 below finds all 16 ledgers among the unreferenced population, every
  one tied to a slice that closed in the same window the ledger was written, which is
  consistent with continued, healthy use of the kind rather than abandonment.

### 1.5 closure / audit record

- **Purpose.** The record that a Work or Phase closed, and on what evidence.
- **Mutability.** `write-once` (NT-0016 §3's term).
- **Today's home.** **Three** homes, not the two NT-0016 §3 names as a "known tension" —
  the census adds a third:
  1. `docs/audit/work/<id>/README.md` — **16 files** at `4f95fb3` (per-work-item closure
     records, the auditor's declared artifact per `.claude/roles/auditor.md`).
  2. `docs/audit/closure-records.md` — **one file**, a single append-only document holding
     every workstream's closure narrative concatenated (4782 lines at `4f95fb3`), distinct
     from the per-item `docs/audit/work/` records above.
  3. `docs/plans/*-closure*.md`-shaped filenames — **3 files** at `4f95fb3`
     (`2026-08-22-w5-closure.md`, `2026-08-23-w32-closure-proposal.md`,
     `2026-08-27-closure-audit-standard.md`), plus the 16 files ending `-ledger.md` whose
     content is itself a closure execution trail even though the filename does not carry
     the token "closure" (e.g. `2026-08-22-w5-closure-ledger.md`, counted under §1.4
     instead, since the `-ledger.md` ending matched first in the mutually-exclusive
     classification).
- **Id family.** Work ids (`W5`, `W6b`, `W32`, `W10`, `W11`...) cited within; no id minted
  by the closure record itself.
- **Rejected reading.** Collapsing the three homes into one count. Rejected — they behave
  differently: `docs/audit/work/` is per-item and structurally uniform (one directory per
  work id); `docs/audit/closure-records.md` is a single running document that has never
  been split even as it grew past 4700 lines; the `docs/plans/`-homed closure documents
  predate the other two mechanisms (`w5-closure.md` and the closure-audit-standard plan
  that built `docs/audit/`'s own structure are both older than most of the
  `docs/audit/work/` entries) and were never migrated forward, consistent with
  `docs/plans/README.md`'s frozen-file rule. NT-0016 §3's "known tension" is confirmed real
  and is, if anything, one home wider than the note recorded it.

### 1.6 register + findings

- **Purpose.** The append-only decision grammar (register) and the per-finding evidence
  essay (findings), split by NT-0015 (`.claude/roles/auditor.md`: "Evidence essays live at
  `docs/audit/findings/<F-id>.md`... Run `python3 scripts/register-lint.py`...").
- **Mutability.** `write-once-amend` (register rows amended in place per their decision
  grammar); findings essays are effectively `frozen` once filed, amended only by explicit
  correction.
- **Today's home.** `docs/audit/register.md` (one file, register rows) and
  `docs/audit/findings/` (essay files, one per finding id).
- **Id family.** `F` + number (`F26`, `F31`, `F62`...).
- **Census evidence.** `docs/audit/findings/` = **5 files** at `4f95fb3`, with a
  `name_pattern` shaped `FN.md` at count **4** (the fifth file is `README.md`, which the
  census's `README.md` `name_pattern` — 26 count across all of `docs` and `.claude` —
  already covers as its own near-universal pattern, §1.11 below). `docs/audit/register.md`
  is a single file, `referenced_by` **72** at `4f95fb3` (the highest of any individual
  file this draft checked outside the `SKILL.md`/`README.md` patterns) — consistent with
  the register being the most-cited single document in the corpus, as its charter implies.
- **Rejected reading.** NT-0016 §3's table names this one row, "register + findings." This
  draft keeps them as one candidate category (since they share an id family and a
  governing charter clause) but records that the census shows two distinct home
  directories and two distinct file-count regimes (one growing file vs. five small ones) —
  a detail Q2 may want when it rules whether "one home per category" means one directory
  or one *governing document*.

### 1.7 research note

- **Purpose.** Working research findings, not yet (or never) promoted to a spec, plan or
  finding.
- **Mutability.** `frozen + correcting annotations` (NT-0016 §3's term); census reports
  `unknown` (`docs/research/` carries no directory-level mutability rule in the census
  script, per `docs/audit/file-census.md`'s column rules — everything outside the four
  named prefixes is `unknown` by design).
- **Today's home.** `docs/research/`.
- **Id family.** None observed — filenames are ad hoc slugs (`track-a-findings.md`,
  `w11-task-1-3-nfr-rate-4.md`, `zen-evaluate-concurrency.md`); several embed an `NFR-RATE-`
  id in the slug but the file itself carries no minted id.
- **Census evidence.** `docs/research/` = **11 files** at `4f95fb3`. One `name_pattern`
  with count 2, shaped `wN-task-Nd-nfr-rate-N.md`, covering two files (the
  `w11-task-1-3-nfr-rate-4.md`-shaped names) — a small but real internal naming convention
  this category has not declared anywhere.
- **Rejected reading.** That this category is redundant with "closure / audit record"
  because both hold performance-measurement evidence. Rejected: the research notes are
  measurement working papers (a "-3d" and "-4d" numbering visible in the `name_pattern`
  above suggests iteration on one measurement across sessions), not verdicts — none of the
  11 states a `CLAUDE.md` §13 verdict the way a closure record does.

### 1.8 ADR

- **Purpose.** An architecture decision record — immutable once accepted, superseded rather
  than edited (`.claude/skills/adr-write`).
- **Mutability.** `immutable, superseded-by`.
- **Today's home.** `docs/adr/`.
- **Id family.** `ADR-NNNN`.
- **Census evidence.** `docs/adr/` = **7 files** at `4f95fb3` (6 numbered ADRs,
  `0001`–`0006`, plus `README.md`). No `name_pattern` with count 2 or more — each ADR has a
  distinct slug after its number.
- **Rejected reading.** None — the smallest, most self-contained category in the
  hypothesis, and the census does not disturb it.

### 1.9 contract (hand vs generated)

- **Purpose.** The JSON Schema + OpenAPI artifact contract `model-schema` generates
  (`CLAUDE.md` §2: "generated and never hand-edited") plus the hand-authored OpenAPI stub.
- **Mutability.** `generated` for the schema tier; the census's own directory rule maps all
  of `docs/contracts/` to `generated`, which is coarser than the true split — the OpenAPI
  YAML stub (`docs/contracts/openapi/gi-pricing.yaml`) is hand-authored per the
  contract-guard convention, while `openapi/generated.json` and every schema file under
  `schemas/` is machine output.
- **Today's home.** `docs/contracts/`.
- **Id family.** None — identified by artifact slug (e.g. a `dataset-version` schema file),
  not a numbered id.
- **Census evidence.** `docs/contracts/` = **61 files** at `4f95fb3`, matching the
  `mutability=generated` total exactly (61) — the directory rule and the actual population
  agree perfectly for this one category, unlike `unknown`'s much larger and noisier bucket.
  11 schema basenames appear in exactly two places each (`schemas/` and
  `schemas/generated/`, or `schemas/common/` and `schemas/generated/`) — a deliberate
  authored/generated pairing, not a duplication defect.
- **Rejected reading.** Treating the coarse `generated` mutability label as evidence the
  whole directory is machine-authored. Rejected — the census script's own documented
  limitation (§ "Column rules," `docs/audit/file-census.md`) is that `mutability` is a
  directory-only guess with no header-marker or content check, and this category is the
  clearest case where that coarseness hides a real internal split (hand vs. generated) the
  directory prefix alone cannot see.

### 1.10 process / charter / skill

- **Purpose.** Three related but distinct things NT-0016 §3 groups as one row: the living
  process document, the seven role charters, and the skill library.
- **Mutability.** `living` for all three sub-kinds.
- **Today's home.** `docs/process/` (process), `.claude/roles/` (charter),
  `.claude/skills/` (skill).
- **Id family.** None for any of the three — process docs, charters and skills are all
  identified by filename/slug, never a minted numeric id.
- **Census evidence, at `4f95fb3`:**
  - `docs/process/` = **3 files** (`agent-settings.md`, `delivery-process.md`,
    `delivery-process.core.json`).
  - `.claude/roles/` = **7 files** — the seven charters this draft's §3 reads against.
  - `.claude/skills/` = **394 files** across all skill subdirectories; the `SKILL.md`
    `name_pattern` alone accounts for **46** of them (one per skill directory) — the single
    highest-count `name_pattern` in the whole `docs`+`.claude` scope.
- **Rejected reading.** Treating "process / charter / skill" as genuinely one category
  because NT-0016 §3 gives it one table row. Rejected for the purposes of §3 of this draft
  (charter-coverage): the three sub-kinds have different homes, different id-family
  answers (none, uniformly) and, most importantly, different **ownership** answers once
  checked against the seven role charters — skill creation is explicitly granted to five of
  the seven roles and explicitly denied (with a redirect) to the other two, while **no**
  charter names authority to create or amend a role charter itself (§3 below). A single
  category row would hide that split.

### 1.11 note (NT)

- **Purpose.** The project's design memory — an investigation, a finding, a proposal not
  yet a spec change.
- **Mutability.** `frozen proposal` (NT-0016 §3's term), amended only by dated correction —
  the same convention this very document (NT-0016) demonstrates in its own "Corrections
  after filing" section.
- **Today's home.** `.claude/notes/` at this draft's tree — **19 files** at `4f95fb3`.
  NT-0016 Slice 4 (blocked on Slice 1 having merged and on Q5/Q6/Q7's notes half being
  ruled, per the investigation plan §9) would move this to `docs/notes/`; that move has not
  happened at this tree, so this draft describes the pre-move state.
- **Id family.** `NT-00NN`.
- **Census evidence.** 19 files, `mutability=unknown` under the census's directory rule
  (neither `.claude/notes/` nor `docs/notes/` is one of the four named prefixes the script
  recognises — another case, like §1.7, where the coarse rule under-classifies a category
  this draft can name precisely by hand).
- **Rejected reading.** None on the category itself — Q5, Q6 and the notes half of Q7 are
  already rulable per the investigation plan §2 and are not reopened here. Worth recording
  precisely because it did not appear in NT-0016 §3's twelve-row table at all: **no role
  charter among the seven grants authority to create an NT note** — see §3 below, where
  this is one of the categories flagged.

### 1.12 workflow journey

- **Purpose.** The cross-module journey — dataset-to-model, model-to-rating-version,
  rate-change impact, deploy-and-monitor, custom-objective lifecycle (`CLAUDE.md` §4).
- **Mutability.** `living`; census reports `unknown` (`docs/workflows/` is not one of the
  four named prefixes).
- **Today's home.** `docs/workflows/`.
- **Id family.** `wf-NN` (`wf-01` through `wf-05`).
- **Census evidence.** `docs/workflows/` = **6 files** at `4f95fb3` (5 numbered journeys
  plus `README.md`). No `name_pattern` with count 2 or more.
- **Rejected reading.** None on the category's existence — but, like §1.11, **no role
  charter among the seven grants authority to create or amend a workflow journey document**;
  see §3.

---

## 2. Findings against NT-0016 §3's own twelve-row table

**Three findings, gathered here because the decision gate will rest on them and they should
not be read as drafting nits buried inside individual category sections.** Each is evidenced
above rather than asserted, and each is cited again from §5 where it bears directly on how
Q1 should be read.

- **NT-0016 §3's "known tension" undercounts by one home.** The note names two homes for
  "closure / audit record" — `docs/audit/work/**` and `docs/plans/*-closure*.md`. §1.5
  finds a **third**: `docs/audit/closure-records.md`, a single 4782-line running document
  that is structurally distinct from both (per-item and directory-uniform on one side,
  one undifferentiated file on the other) and was never migrated into either. The note's
  own scope for this tension is stated as fact ("closure material lives in **two** homes");
  the census shows it is three, and the gate should read Q1 and Q2 against three, not two.
- **Two candidate categories each carry two live, mutually unintelligible filename
  grammars — found independently, in two different categories.** §1.2: the "plan
  (map / leaf)" category's map sub-kind is spelled `slice-map` in four W6b-era files and
  `map-plan` in one W12-era file — the census's own `name_pattern` clustering does not
  group them, because they do not share a pattern. §1.3: the "rulings record" category
  spells the ruling number as a filename *suffix* in 23 files (`...-ruling.md`,
  `...-rulings.md`) and as a filename *prefix* in one (`ruling-60-...md`) — found only
  because the prefix form broke a suffix-only classifier built for this draft. **Two
  independent discoveries of the same shape of defect is stronger evidence than either
  alone**: it means the hypothesis in NT-0016 §3 names the right categories but the
  filenames actually in the corpus have not settled on one grammar for either of the two
  categories checked closely enough to notice. This is direct evidence for Q1's
  rebuild-from-census option specifically (§5), not a general argument for caution.
- **Splitting register from findings by home**, not just by NT-0015's decision-grammar
  argument (§1.6) — one growing document versus five small essay files, a difference Q2 may
  want if "one home per category" is ruled to mean one directory.

One thing the census's `name_pattern` clustering surfaces that this draft does **not** treat
as a thirteenth category: `.claude/agents/` (**8 files** at `4f95fb3`, one `README.md` plus
seven delegable-specialist definitions). `CLAUDE.md` §12 already treats this as a governance
track distinct from the seven roles this draft reads against in §3 ("A delegable specialist
(`.claude/agents/`) gathers or verifies and decides nothing... That directory's README is
its dividing line"), so it is named here for completeness rather than folded into §1's
twelve, and its own ownership question is `.claude/agents/README.md`'s to answer, not this
draft's.

---

## 3. Categories no charter creates

Read against all **seven** files under `.claude/roles/` (`auditor.md`, `decision-maker.md`,
`executor.md`, `lead.md`, `planner.md`, `reporter.md`, `watcher.md`).

**A known failure mode in this exact check, recorded beside the finding below because
anyone re-verifying it will reach for the same tool.** A naive, line-based `grep` for the
phrase "may create or update a skill" across the seven charters returns only four hits —
`auditor.md`, `decision-maker.md`, `executor.md`, `lead.md` — and reads as though
`planner.md` grants no such authority. It does: the phrase is present, but it wraps across
a line break in the source file (`"...applied by the lead or decision-maker. **May create
or\n  update a skill under..."`), so a single-line pattern silently misses it. Caught only
by re-checking with a whitespace-tolerant search (join the file, collapse runs of
whitespace, then match). This is the exact trap the project's own memory record under
"never hardcode a fragment of an identifier" describes, reproduced here rather than
avoided, which is the reason it is worth stating plainly: **the naive grep is the one a
future re-check will reach for first, and it produces a false negative on `planner.md`
specifically** — a re-checker who stops at the naive result would wrongly add "planner" to
a list of roles barred from skill creation. §1.10 and the finding below both rest on the
corrected, whitespace-tolerant search, not the naive one.

**These are findings, not assignments** — NT-0016
C3, restated in the investigation plan's dispatch for this slice: "a category no charter
names is a finding, and assigning it is the decision-maker's, not this investigation's."

- **ledger.** No charter uses the word "ledger" anywhere. `docs/plans/README.md` names
  `subagent-driven-development` as the skill that writes one, but no *role* charter claims
  authority over the category the way `auditor.md` claims closure records or
  `decision-maker.md` claims ruling records.
- **research note.** No charter uses the phrase "research note," and `docs/research/`
  (11 files, §1.7) is not named by any of the seven. It is not swept in by `lead.md`'s
  residual clause either, in principle — that clause **is** scoped to `docs/` content
  ("write to... any `docs/` content no other role's charter names"), so `docs/research/`
  is covered by the catch-all even though no purpose-built clause names it. Recorded as a
  finding regardless, because a catch-all sweep is not the same thing as ownership
  "derived from charters" in C3's sense — C3's own example (`auditor.md`'s quoted line, "a
  role writes the artifacts its own charter names") is about a charter naming a category on
  purpose, not a residual bucket catching whatever nothing else claimed.
- **workflow journey (`docs/workflows/`).** Same shape as research notes: no charter names
  it by path or by phrase; covered only by `lead.md`'s `docs/`-scoped catch-all.
- **note (NT) (`.claude/notes/`, moving to `docs/notes/`).** No charter names authority to
  **create** a new NT note. `lead.md`, `planner.md` and `watcher.md` all *cite* NT ids
  extensively in their own text (evidence the notes are read constantly), but citing an id
  is not the same as owning the category that mints it. `.claude/notes/` is also **not**
  `docs/` content, so — unlike research notes and workflow journeys — `lead.md`'s residual
  clause does not sweep it in either: the clause's own words are "any `docs/` content," and
  `.claude/notes/` sits outside `docs/` at this draft's tree. This is the sharpest gap
  found: an entire category — one this very investigation is itself an instance of — has
  no charter-derived creator at all, under either the specific clauses or the catch-all.
- **role charter (`.claude/roles/*.md` itself).** No charter grants authority to create or
  amend a file under `.claude/roles/`. `lead.md` mentions "role file" and "role's charter"
  twice, both in the context of *dispatching* a fresh agent that reads its role file at
  spawn — never as a write-authority clause. `CLAUDE.md` §12 says "a role file that proves
  insufficient is a finding against the file: fix the file, do not paste a brief back in,"
  which presupposes someone fixes it, but names no one. And `lead.md`'s residual "`docs/`
  content" clause does not reach `.claude/roles/` for the same reason it does not reach
  `.claude/notes/` — it is scoped to `docs/`. Within the combined "process / charter /
  skill" category (§1.10), this means the "skill" sub-kind is fully covered (five roles
  explicitly may create or update a skill; the other two, `reporter.md` and `watcher.md`,
  explicitly redirect skill discoveries through the lead rather than being silent about
  it) while the "charter" sub-kind is not covered by any mechanism this draft could find —
  specific, catch-all, or redirect.

Two categories checked and found **fully covered**, recorded so the negative result is not
mistaken for an oversight: **register + findings** (`auditor.md`, explicit) and **rulings
record** (`decision-maker.md`, explicit, both singular "ruling record" and plural "ruling
records" phrasing present). **spec** (`decision-maker.md`, explicit — "write to... `docs/specs/`
for the spec changes its charter already owns") and **plan** (`planner.md`, explicit — "Owns:
the plan: frozen dated files in `docs/plans/`") are likewise fully covered.

---

## 4. The unreferenced plans: verdict 2 versus verdict 4

**Population.** 124 files under `docs/plans/` at `4f95fb3` (git ls-files corpus). Applying
§0.1's correction — excluding a `referenced_by` count that traces solely to
`docs/audit/file-census-5ef559d.csv` or `docs/audit/file-census.md` as the only "referrer,"
and separately including one file that postdates the `5ef559d` census outright — **39
files** carry no genuine reference from any other tracked file's content at this tree. 38 of
the 39 are the same file set, by path, that the committed `5ef559d` census reports as
`referenced_by == 0` directly (no correction needed at that earlier tree, since the
polluting CSV did not yet exist there) — the two independent readings agree exactly, which
is the check this draft relies on to say the corrected count is not an artifact of the
correction method itself. The 39th (`2026-09-01-ruling-60-census-provenance-checkout-depth.md`)
did not exist at `5ef559d` and carries no pollution correction at all — see §0.1.

**All 39 carry a verdict below.** None is sampled. Verdict 2 (write-only — F31's shape: a
reading step should exist and does not, or the category should be retired) and verdict 4
(terminal-by-design — acceptable, but declared) are NT-0016 §6's two verdicts that apply to
an *unreferenced* file; verdicts 1 (looped) and 3 (read-only-in) do not apply here by
definition, since both describe files that are read by something.

**How each verdict was reached.** Every file's opening lines were read. Where the file names
a requirement id, a slice id or a Work id, that id was checked against
`docs/audit/closure-records.md` and, where relevant, `docs/roadmap.md`, for a closure
narrative that discusses the same id by content — per §0.2, a closure record's citation is
to the id, never to the plan's filename, so `referenced_by` cannot see this relationship and
a fresh check was necessary for each file rather than inferred from the census alone.

| # | File | Kind | Verdict | Reason |
|---|---|---|---|---|
| 1 | `2026-08-19-custom-metrics-final-review.md` | final-review | **4** | Declared final-review kind (`docs/plans/README.md`): "findings against a finished branch, and their verdicts." FR-MODEL-45 is confirmed delivered in the W5 closure narrative by id and prose, not by this filename. |
| 2 | `2026-08-19-custom-metrics-ledger.md` | ledger | **4** | Declared ledger kind. Its own header cites an upstream plan under `.planning/` (git-ignored, never committed) — this ledger is the sole durable record of that work, not a downstream artifact of a committed plan. FR-MODEL-45 confirmed delivered (W5 close). |
| 3 | `2026-08-19-glm-approximation-as-model-ledger.md` | ledger | **4** | Same shape as #2. FR-MODEL-96 confirmed delivered — W5 closure narrative's "Transparency artifacts" row names it directly. |
| 4 | `2026-08-19-psi-comparison-selector-ledger.md` | ledger | **4** | Same shape as #2. FR-DATA-28 / VR-DST-1, upstream plan also `.planning/`-only. |
| 5 | `2026-08-19-paired-quantile-models.md` | leaf plan | **4** | FR-MODEL-78, no sibling ledger exists for this plan. Explicitly narrated as delivered in `docs/audit/closure-records.md` ("the slice... that makes FR-MODEL-78 real") and cited in a `scope-audit.py MODEL --endpoints` line in the same record. |
| 6 | `2026-08-21-ebm.md` | leaf plan | **4** | FR-MODEL-37, no sibling ledger. Confirmed in the W5 closure narrative ("EBM via interpret-core exports terms and bins directly rather than a serialised estimator, FR-MODEL-37"). |
| 7 | `2026-08-21-offset-from-another-model.md` | leaf plan | **4** | FR-MODEL-24, no sibling ledger. Confirmed in the W5 closure narrative ("offsets including offset-from-another-model, GLM-to-GLM, FR-MODEL-24"). |
| 8 | `2026-08-21-tweedie-profile-likelihood.md` | leaf plan | **4** | FR-MODEL-22, no sibling ledger. Confirmed in the W5 closure narrative ("Tweedie with the power estimated by profile likelihood and its 95% interval recorded, FR-MODEL-22"). |
| 9 | `2026-08-22-gbm-weights-and-dropped-eval-metrics.md` | leaf plan | **4** | FR-MODEL-106/107, no sibling ledger. Extensively narrated across `docs/audit/closure-records.md` (multiple dated sub-sections discuss `eval_metrics` being honoured, FR-MODEL-106). |
| 10 | `2026-08-22-w5-audit-remediation-ledger.md` | ledger | **4** | Declared ledger kind, execution record for a W5 remediation pass within W5's own closed window (W5 closed 2026-08-22, same date). |
| 11 | `2026-08-22-w5-closure-ledger.md` | ledger | **4** | Declared ledger kind; its content is literally the execution trail of W5's own close, dated the same day W5 closed. |
| 12 | `2026-08-20-w5-worker-handover.md` | handover | **4** | Declared handover kind: "state a successor session needs to resume." Its own text states the work was already merge-ready when written ("PR #122 merged-ready"); a handover's designed audience is the immediate successor session, not a later citer. |
| 13 | `2026-08-22-slice-6a-verified.md` | final-review/verified | **2** | Declared verified kind: "findings against a finished branch, and their verdicts" (`docs/plans/README.md`). Its own text states the intended next step explicitly and flags it incomplete at time of writing: "Verification is complete; application to `docs/roadmap.md` is **not started**." No later document — closure record, roadmap correction, or otherwise — was found citing this file or its findings. Flagged as write-only rather than terminal because the gap is the file's own stated one, not inferred. |
| 14 | `2026-08-23-w32-3-dataset-list-derived-fields-ledger.md` | ledger | **4** | Declared ledger kind, cites its own upstream plan (`2026-08-23-w32-3-dataset-list-derived-fields.md`, itself referenced and not in this population) by filename. W32 closed 2026-08-24 with a dedicated W32-3 heading in its closure record. |
| 15 | `2026-08-23-w32-4-ebm-predict-arm-ledger.md` | ledger | **4** | Same shape as #14; W32 closure record carries a dedicated W32-4 heading. |
| 16 | `2026-08-23-w32-5-partial-dependence-exposure-ledger.md` | ledger | **4** | Same shape as #14; W32 closure record carries a dedicated W32-5 heading. |
| 17 | `2026-08-23-w32-6-backtest-and-objective-endpoint-tests-ledger.md` | ledger | **4** | Same shape as #14; W32 closure record carries a dedicated W32-6 heading. |
| 18 | `2026-08-24-w32-11-certificate-floors-and-two-generated-sides.md` | leaf plan | **4** | Its own header states it was "allocated on 2026-08-24" from a decision inside `2026-08-23-w32-closure-proposal.md`'s own Part C — i.e., it is itself a product of W32's closure process. W32 closure record carries a dedicated W32-11 heading (one of "12 slice headings — W32-1 ... W32-11 plus W32-1b" the closure record's own acceptance table names). |
| 19 | `2026-08-24-w6b-1b-diagnostics-view.md` | leaf plan | **4** | W6b closed 2026-08-27. Closure record's own text: "Earlier W6b slices (W6b-1..9, W6b-13, W6b-14) merged in prior sessions; their delivery records are in the roadmap §6 slice records" — this slice (W6b-1b) is inside that named range. |
| 20 | `2026-08-24-w6b-2-model-comparison.md` | leaf plan | **4** | Same coverage as #19 (W6b-2 is inside the "W6b-1..9" range). |
| 21 | `2026-08-25-w6b-3-dataset-list-contents.md` | leaf plan | **4** | Same coverage as #19. |
| 22 | `2026-08-25-w6b-4a-model-spec-builder-builtin.md` | leaf plan | **4** | Same coverage as #19. |
| 23 | `2026-08-25-w6b-4b-custom-objective-arm.md` | leaf plan | **4** | Same coverage as #19. |
| 24 | `2026-08-25-w6b-5a-treeshap-holdout-pass.md` | leaf plan | **4** | Same coverage as #19. |
| 25 | `2026-08-25-w6b-5b-suggestion-panel.md` | leaf plan | **4** | Same coverage as #19. |
| 26 | `2026-08-25-w6b-6-backtest-view.md` | leaf plan | **4** | Same coverage as #19. |
| 27 | `2026-08-25-w6b-8-peril-structure-views.md` | leaf plan | **4** | Same coverage as #19. |
| 28 | `2026-08-25-w6b-10-browser-auth.md` | leaf plan | **4** | W6b closure record's own delivery table names this slice directly: "W6b-10 browser auth, PR #250, verified." |
| 29 | `2026-08-25-w6b-11-workspace-selector.md` | leaf plan | **4** | Closure record's delivery table: "W6b-11 workspace selector, PR #252, verified." |
| 30 | `2026-08-26-w6b-15-minor-rename.md` | leaf plan | **4** | Closure record's delivery table: "W6b-15 `_minor` rename, PR #258, verified." |
| 31 | `2026-08-26-w6b-group-a.md` | leaf plan | **4** | Closure record's delivery table: "W6b-17+18+19 Group A, PR #260, verified." |
| 32 | `2026-08-26-w6b-group-b.md` | leaf plan | **4** | Closure record's delivery table: "W6b-20+21+24 Group B, PR #261, verified." |
| 33 | `2026-08-26-w6b-group-c.md` | leaf plan | **4** | Closure record's delivery table: "W6b-22+23 Group C, PR #262, verified." |
| 34 | `2026-08-26-w6b-route-reachability.md` | leaf plan | **4** | Closure record's delivery table: "route reachability (issue #136), PR #259, verified" (cited by issue number rather than slice slug, but the same table row). |
| 35 | `2026-08-28-w10-rate-tables-rulings.md` | rulings record | **4** | Own text: "the plan itself is frozen... and is not amended; this record is the dated home of the rulings." W10 closed 2026-08-28 (`docs/roadmap.md`'s W10 row cites `docs/audit/work/W10/README.md`); a rulings record's declared purpose — the dated record of a decision at the time it was made — matches NT-0016 §6's own verdict-4 example ("frozen records cited only at creation") directly. |
| 36 | `2026-08-29-w11-process-conformance-audit.md` | leaf plan (audit) | **2** | A maintainer-requested independent audit, not tied to a single slice id. Its own "Proposed disposition" section names two follow-ups — a register row for an unassembled-instrumentation finding, explicitly left with "no owner proposed here," and a note that "this record itself stands as the pilot's first §7 data point, pending whoever next revisits the retry-cap numbers." No evidence was found that either follow-up happened. Recorded as write-only on the strength of the document's own unresolved forward references, not asserted as certainly abandoned. |
| 37 | `2026-08-27-closure-audit-standard.md` | closure record | **4** | This plan's own stated goal is to build `docs/audit/`'s structure itself — the closure-record layer, the `CLAUDE.md` §14 rule, and the checklists. Once instantiated, downstream work cites the *artifacts it produced* (e.g. the work-item-close checklist) rather than the plan that built them — the same pattern as any implementation plan whose product replaces the plan as the object of citation. |
| 38 | `2026-08-31-w12-map-plan.md` | map plan | **2**, with a stated caveat | Filed one day before this draft's evidence tree; `docs/roadmap.md`'s W12 row carries no closed marker. The map-plan convention this draft observed directly (§1.2: `2026-08-29-w11-scoring.md`, a map plan, is cited by filename inside three of its own leaf children) predicts this file **will** gain references once its Slices 2–4 are detailed and unblocked — its own text says as much ("the full task-by-task detail for Slices 2–4 is a child slice plan written once each slice is unblocked... the same relationship `2026-08-29-w11-scoring.md` has to `2026-08-29-w11-1-evaluator-core.md`"). Recorded as write-only only in the narrowest, literal sense — no reference exists *yet* — and distinguished explicitly from #13's and #36's write-only readings, which rest on a stated gap rather than on elapsed time. |
| 39 | `2026-09-01-ruling-60-census-provenance-checkout-depth.md` | rulings record | **4** | Landed on `main` while this draft's working branch was in flight, before PR #537 (the census script) squash-merged — see the document header's "Evidence tree" note for the two rebases this required. Own text: "Ruling 59 is merged and frozen. This is a new, citing record superseding its §3 point 2... not an edit to that file." Amends Ruling 59 (item #35's neighbour, its own filename cited directly in this file's own opening lines, which is why Ruling 59's file is *not* in this population). The CI fix it specifies (`.github/workflows/python.yml`'s checkout depth) is already merged into this draft's own evidence tree. Same reasoning as #35: a rulings record's declared purpose is the dated home of a decision at the time it was made, matching NT-0016 §6's verdict-4 example directly — not, like #38, a case argued from elapsed time, since the underlying decision is already implemented. |

**Totals.** Verdict 4: **36**. Verdict 2: **3** (#13, #36, #38 — the last flagged with an
explicit "too new to tell" caveat rather than presented as equivalent in kind to the other
two). 36 + 3 = 39, matching the corrected unreferenced population stated above.

**What this decomposition suggests, stated as an observation rather than a rule.** The
overwhelming majority (36 of 39, 92%) of the unreferenced population is unreferenced
because closure records and roadmap rows cite the underlying *work* by requirement id, slice
id, PR number, or (for #39) by the decision's own "Ruling N" number — never by the plan's
filename — not because the work went undone or the document went unread. This matches
§0.2's methodology note and is the strongest evidence this draft found that a
`referenced_by` count of zero, read alone, would have overstated the "unreferenced plans"
figure as a defect count. The 3 verdict-2 files are qualitatively different from each other
(#13 names its own unresolved follow-up; #36 names two, unowned; #38 is simply too new) and
from the 36 verdict-4 files, and Q3's ruling on how a verdict is declared should have a
place for that difference rather than treating "write-only" as one shape.

---

## 5. The four questions for the gate, as named options

Stated per NT-0016 §10 and the investigation plan §4a item 7. Each is a choice; this draft
recommends nothing and rules nothing.

### Q1 — Is the closed category set ruled as drafted, amended, or rebuilt from the census?

- **Option A — drafted.** Adopt NT-0016 §3's twelve-row table as written, unchanged by
  this draft's findings.
- **Option B — amended.** Keep §3's twelve rows as the base, but apply §2's three findings
  directly: split "closure / audit record" into three homes rather than two; split
  register from findings by home; carry the map/leaf and rulings-record naming
  inconsistencies (§1.2, §1.3) forward as grammar items for Stage 2 rather than as new
  categories.
- **Option C — rebuilt from the census.** Discard the twelve-row table as a starting
  point and construct the closed set fresh from §1's evidence plus §2's three findings, on
  the ground NT-0016 §10 itself already recommends ("rule on the census-clustered set, not
  the hypothesis"). **§2's second finding is the sharpest evidence for this option
  specifically**: two categories, checked independently, each turned out to carry two live
  filename grammars the census's own `name_pattern` column does not group together — not a
  single instance that could be a one-off naming slip, but the same shape of defect found
  twice. A hypothesis drafted before the census existed cannot be expected to have
  anticipated a grammar inconsistency the census itself is what surfaced.

### Q2 — One home per category: do rulings records and ledgers stay in `docs/plans/`?

- **Option A — grammar-in-place.** All of `docs/plans/`'s undeclared sub-kinds (rulings,
  ledger, closure, slice-map/map-plan) stay physically in `docs/plans/`, distinguished by a
  filename grammar Stage 2 defines. NT-0016 §10's own recommendation.
- **Option B — split directories.** Each sub-kind moves to its own directory under
  `docs/plans/` (a `rulings/` subdirectory, a `ledgers/` subdirectory, and so on).
- **Option C — partial split, evidenced by what the census already shows.** §1.5 finds
  closure records already split across three homes in practice, without a rule forcing it;
  Q2 could rule that only categories the census shows have *already* organically split
  (closure records) get a directory of their own, while categories that have stayed
  uniformly in `docs/plans/` (rulings, ledgers) keep the grammar-in-place answer.

### Q3 — Verdict-4 declaration form: an index marker or a category attribute?

- **Option A — index marker.** A verdict-4 declaration lives in a per-directory or
  per-category index file, separate from the file it describes.
- **Option B — category attribute.** The declaration lives on the file itself (a header
  field, per NT-0016 §4's reference-coding stage).
- **Option C — derived, not declared, wherever a closure record already exists.** §4's
  decomposition shows 36 of 39 verdict-4 readings are fully explained by an existing
  closure record's own coverage of the same requirement/slice/work id — Q3 could rule that
  for this majority, verdict-4 status is *read off* the closure record rather than declared
  a second time on the plan file, which would avoid creating a second status that can go
  stale independently of the closure record it duplicates (`CLAUDE.md` §0, NT-0003's own
  precedent). The 3 verdict-2 files, and any future file with no closure record covering
  it, would still need an explicit declaration under either Option A or B.

### Q7 (general half) — Citation grammar for every category: id, path, or mixed?

- **Option A — id-only, universally.** Every category cites another by a minted id,
  extending the notes' NT-id precedent (NT-0016 §1a's own argument: "id citations survived
  this very move; path citations are what made §3a cost 28 files") to every category.
- **Option B — path-only, as today.** Keep full-path citation for every category, the
  status quo this draft's own citations follow.
- **Option C — mixed, split by whether the category has an independent id.** Categories
  that already mint an id (spec: `FR-`/`NFR-`/`OQ-`; ADR: `ADR-NNNN`; note: `NT-00NN`;
  register/findings: `F`-number; workflow: `wf-NN`) cite by id. Categories with no id
  scheme of their own — plan, ledger, rulings record, closure record — are identified only
  by a dated filename, so an id-only rule for them would require minting a new id family,
  which NT-0016 C2 and this draft's own Global Constraints forbid. §4's own evidence is
  relevant here: 36 of 39 "unreferenced" plans are in fact covered, but by an id (a
  requirement, a slice, a PR) rather than a path — an argument that the *existing*
  practice already behaves like Option C for the categories that have one, without having
  named it as a rule.

---

## 6. What this draft does not do

It rules none of §5's four questions. It files no register row for the three verdict-2
findings in §4, the two categories with no purpose-built or catch-all charter coverage in
§3, or the census-of-a-census artifact in §0.1 — under `CLAUDE.md` §13, a verdict on an
unevidenced artifact is the main thread's, never a document's, and this draft is not the
main thread. It mints no `FR-`, `NFR-`, `OQ-` or `ADR-` id. It edits no frozen file.
