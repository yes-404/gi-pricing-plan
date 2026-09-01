# NT-0016's Q4, Q5, Q6 and Q7's notes half, ruled (2026-09-01)

**What this is.** Four of the seven open questions in
[`../../.claude/notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md`](../../.claude/notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md)
§10 — Q4, Q5, Q6, and the notes half of Q7 — which
[`2026-08-31-nt-0016-investigation.md`](2026-08-31-nt-0016-investigation.md) §2 finds
**rulable now**, over evidence that plan re-measured at its pinned tree `b551060`. Each
recommendation arrived from the note carrying a proposal; a note decides nothing
([`../../.claude/notes/README.md`](../../.claude/notes/README.md)), so each is re-verified
below rather than adopted on the strength of being the only text on the table.

**Q1, Q2, Q3 and Q7's general half are NOT ruled here.** The plan's §2 finds the evidence to
rule them does not exist yet — they presuppose a closed category set the census (Slice 2)
and taxonomy draft (Slice 3) have not yet produced, and §4 names the decision gate after
Slice 3 as their trigger. This record does not pre-empt that gate. Independent re-check
against this plan's own reasoning (not against a fresh read of the underlying evidence, which
does not exist yet to check against) found no ground to disagree: ruling any of the four
today would be a ruling on the note's hypothesis rather than on data, which is exactly the
outcome §10's authors wrote the split to avoid.

**This ruling is what unblocks Slice 4.** §9 of the plan blocks the notes move on "Slice 1
merged, and Q5, Q6 and Q7's notes half ruled by the decision-maker." Slice 1 is a separate,
independent PR; this record discharges the second half of that gate. Q4 is included because
the plan finds it rulable and ruling it in the same record costs nothing additional.

**Numbering continues at 55.** Verified rather than relayed: every `## Ruling N` heading
under `docs/plans/` at `b2fb122` (`origin/main`, fetched immediately before this record was
written) yields a maximum of 54, in
[`2026-08-31-f62-timing-ms-ruling.md`](2026-08-31-f62-timing-ms-ruling.md).

**Everything measured here was measured at `b2fb122`.** The plan pins its own evidence to
`b551060`, five commits behind. Where a figure moved between the two trees, both are stated;
none of the plan's five load-bearing evidence claims changed in substance between them — see
each ruling's §1 and the summary at the foot of this record.

**This record's own dependence on the plan.** Every claim in the plan's §1, §1a, §1b and §2
that this record's four rulings rest on re-verified true, at its own stated tree, with no
defect found in that reasoning — only ordinary drift in line numbers and citation-surface
counts, which the plan's own framing anticipates (`CLAUDE.md` §13: "a count carries the tree
and the corpus it counted over"). **One defect was found elsewhere in the plan** — in Slice
1's own Step 1 test code, unrelated to any of the four questions ruled here — and is recorded
as a correction appended to the plan's own *Corrections after filing* section, per this
role's charter and NT-0016 C4, rather than edited into the frozen text. See that section for
detail; it does not change any ruling in this record.

## Acceptance Standard

The testable definition of "done" for this ruling record, each item checkable by a command a
fresh reviewer can run:

1. `git grep -c "^## Ruling 5[5-8] —" docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`
   returns `4`, and `git grep -n "^## Ruling " docs/plans/` shows 55–58 filling exactly the
   gap after Ruling 54 with no duplicate and no skip.
2. Each of the four `### 2. Ruled` subsections names both the chosen option and the rejected
   option in its opening sentence.
3. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
4. `git grep -nE '\bFR-[A-Z]+-[0-9]|\bNFR-[A-Z]+-[0-9]|\bOQ-[A-Z]+-[0-9]|\bADR-[0-9]' docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`
   returns zero matches — no requirement or ADR identifier is minted, per NT-0016 C2 and the
   parent plan's own scope.
5. `git diff --stat <merge-base>..<branch> -- docs/plans/` names exactly two files: this
   record, and the *Corrections after filing* append to
   [`2026-08-31-nt-0016-investigation.md`](2026-08-31-nt-0016-investigation.md) — no other
   file under `docs/plans/` changes, and the append is additive only (`git diff` on that file
   shows only inserted lines).
6. Q1, Q2, Q3 and Q7's general half are named in this record only inside the preamble's "NOT
   ruled here" paragraph and Ruling 58's scope note — never inside a `### 2. Ruled` verdict —
   confirmed by `grep -n "### 2. Ruled" -A2` on each of the four rulings naming no other `Q`
   than its own.

---

## Ruling 55 — Q4: the ownership matrix lands in `docs/process/`; a note appendix is rejected

### 1. Verified first, at `b2fb122`

| Claim | Verdict |
|---|---|
| C3 — "ownership is derived from charters, not invented" — is a design constraint the note states and does not re-litigate | **Confirmed** — `.claude/notes/0016-…md:58-61` |
| `CLAUDE.md` §12 grounds the same principle, and `.claude/roles/auditor.md` quotes it | **Confirmed** — `CLAUDE.md:222`: *"writes the artifacts its charter names, including under `docs/`"*; `.claude/roles/auditor.md:50`: *"a role writes the artifacts its own charter names"* |
| seven role charters exist, each independently amendable | **Confirmed** — `.claude/roles/{auditor,decision-maker,executor,lead,planner,reporter,watcher}.md`, 7 files |
| `docs/process/` today holds only living documents, none frozen | **Confirmed** — `agent-settings.md`, `delivery-process.md`, `delivery-process.core.json`; no dated/write-once file among them |
| the note's own recommendation is "living, in `docs/process/` — it must track charter amendments" | **Confirmed** — `.claude/notes/0016-…md:230-231` |
| no ownership-matrix file exists yet at either candidate location | **Confirmed** — `git grep -il "ownership matrix"` returns only the note and the plan themselves |

### 2. Ruled

**Chosen: `docs/process/`, as a living document. Rejected: an NT note appendix, frozen.**

A note appendix is frozen by the same convention every note obeys — see Ruling 56 below and
`.claude/notes/README.md`'s own custody rule. An ownership matrix's content is a cross-cutting
read of all seven role charters' `Owns`/`Never` clauses, and those charters are themselves
living — `.claude/roles/decision-maker.md`, this record's own charter, was itself amended
mid-project (its own text names two incidents that changed it). A frozen appendix could not
track the next such amendment without either going stale silently or being edited in
violation of the freeze it lives under — the exact duplicated-status decay
`.claude/notes/0003-duplicated-status-goes-stale.md` catalogues, reproduced one level down. A
living document in `docs/process/`, alongside `delivery-process.md` and
`agent-settings.md` — which already track process facts that change as the team's charters
and settings change — has no such failure mode: it is amended in the same commit as the
charter change that motivates it.

This question does not depend on Q1. The matrix cross-references existing charters; nothing
about *which* file-category taxonomy the census yields changes where the cross-reference of
charters to categories should live.

### 3. What it obliges

Whichever future slice files the ownership matrix (Stage 2/3, unscoped by this plan) creates
it as a living file under `docs/process/`. This ruling fixes the directory and the mutability
class only — not a filename, which is that slice's to choose and outside this record's scope.

**Overridden if** a future slice files the matrix as a note appendix, or as any other frozen
artifact under `docs/plans/` or `.claude/notes/`.

---

## Ruling 56 — Q5: destination is `docs/notes/`; folding into an existing `docs/` family is rejected

### 1. Verified first, at `b2fb122`

| Claim | Verdict |
|---|---|
| `README.md` is 48 lines and contains no occurrence of `.claude` | **Confirmed, unchanged from `b551060`** — `git diff --stat b551060 HEAD -- README.md` is empty; read in full, 48 lines, zero `.claude` matches |
| its *Explore the project* tour lists five destinations, all under `docs/` | **Confirmed** — `docs/specs/`, `docs/adr/`, `docs/workflows/`, `docs/audit/register.md`, `docs/roadmap.md`; no notes entry |
| `CONTRIBUTING.md` and `SECURITY.md` likewise contain no `.claude` occurrence | **Confirmed, unchanged** |
| the NT-0016/NT-0017 dependency — "the landed README carries a `.claude/notes/` citation for a later slice to update" — does not exist | **Confirmed absent, as the plan states** — there is nothing to update; the front door already points into `docs/` only |
| C5 — "home is determined by consumer... notes are consumed by readers and citations, never by the runtime, so they belong under `docs/`" | **Confirmed as stated** — `.claude/notes/0016-…md:64-67` |
| the alternative limb (fold into `docs/adr/`) imports supersede semantics notes lack | **Confirmed as the note's own stated reason** — `.claude/notes/0016-…md:232-234`; ADRs supersede one another explicitly, notes do not |
| `scripts/audit-docs.py`'s own check-25 scan already treats `docs/plans` and the notes root as siblings in one list | **Confirmed** — `scan_dirs = [ROOT / "research", ROOT / "plans", NOTES]` at line 551 (current tree; `:505` at `b551060`) — the mechanism already reasons about the notes root as a peer of two `docs/` directories, not as something structurally bound to `.claude/` |

### 2. Ruled

**Chosen: `docs/notes/`, keeping the family's own name and its README. Rejected: folding
into an existing `docs/` family (`docs/adr/` named specifically, and by extension any other
existing family).**

C5 alone decides this, and nothing else needs to: `.claude/` is for what the agent runtime
consumes (skills Claude Code discovers, role charters that spawn members, settings), and
`docs/` is for what a human reader or the process consumes. The notes are read, cited by id,
and correct or extend one another over time — never read by any runtime component — so C5
places them under `docs/` on the same test that keeps roles and skills in `.claude/`.

The evidence this record adds beyond the note's own text is that the public-facing case for
the move is stronger than assumed, not weaker: `README.md`'s tour was already `docs/`-only
before this question was ever raised, and the claimed NT-0017 dependency that would have made
the move's timing depend on another Work does not exist. There is no coupling left to wait
on. Folding into `docs/adr/` is rejected on the note's own stated ground — an ADR's
`Superseded-by` semantics do not fit a note, which corrects itself in place — and no other
existing family (`docs/specs/`, `docs/workflows/`, `docs/audit/`) is offered or fits: none of
them share the notes' write-once-then-annotate mutability class.

This question does not depend on Q1: whatever category set the census yields, `note` survives
as a category (the note proposing the taxonomy cannot cluster itself out of existence), so its
home does not wait on the shape of the rest of the taxonomy.

### 3. What it obliges

Slice 4 moves `.claude/notes/` to `docs/notes/` via `git mv`, exactly as its steps describe.

**Overridden if** a future slice lands the notes under any path other than `docs/notes/`, or
merges the family into an existing `docs/` directory rather than keeping its own name and
README.

---

## Ruling 57 — Q6: tombstone form is a README mapping; symlinks are rejected

### 1. Verified first, at `b2fb122`

| Claim | Verdict |
|---|---|
| `check_notes` (checks 16–20) guards on `NOTES.is_dir()` and globs `NOTES.glob("*.md")` | **Confirmed** — `scripts/audit-docs.py:281` and `:295` (`:235`/`:249` at `b551060`; the constant itself moved from `:52` to `:66` — line numbers only, no behaviour change) |
| a `pathlib.Path.is_dir()` / `.glob()` call resolves through a symlink | **Confirmed by inspection of the code path** — nothing in `check_notes` or `check_finding_citations`'s `scan_dirs` (`:551-552`, current tree) distinguishes a real directory from a symlinked one; both satisfy `is_dir()` and both glob successfully |
| `scan_dirs` at check 25 already lists the notes root alongside two `docs/` directories in one list | **Confirmed** — see Ruling 56 §1, same line |
| the note's own text names the same disqualification independently | **Confirmed** — `.claude/notes/0016-…md:236-237`: symlinks "render poorly on github.com, and a symlinked directory would silently re-include notes under `.claude/` for path-scanning tools" |

### 2. Ruled

**Chosen: a `README.md` mapping at the vacated `.claude/notes/` path. Rejected: a git
symlink.**

The disqualification is mechanical, not stylistic. A symlinked `.claude/notes` pointing at
`docs/notes/` would keep resolving for every tool in this repository that checks directory
existence and globs for `*.md` — which is exactly what `audit-docs.py` does, at both the
checks-16–20 root and the check-25 scan. That means both paths would go on being "real" to
every consumer indefinitely: the old path never stops working, so nothing forces the 13
living citations (§1a of the plan) to ever migrate, and a future contributor citing either
path is equally correct. That is the two-homes ambiguity the move exists to end, recreated by
the tombstone meant to close it. A plain-text `README.md` has no such property: it is not a
directory, so `is_dir()` on the old path returns false, `check_notes` correctly reports
absence (and, once Slice 1 lands, fails loudly rather than skipping silently — see the
plan's §1b and §6), and a reader or tool landing on the old path gets one paragraph and an
explicit old→new mapping rather than a second live copy of the directory.

This question is purely mechanical and does not depend on Q1.

### 3. What it obliges

Slice 4 Step 6 writes `.claude/notes/README.md` as a tombstone: one paragraph plus the
old-to-new mapping, exactly as the plan's §9 describes. No symlink is created at any point in
the slice.

**Overridden if** a future slice creates a symlink, junction, or any other mechanism that
makes the old path continue to resolve as a directory.

---

## Ruling 58 — Q7, notes half only: cite notes by `NT-00NN` id; path citations are rejected for this one category

**This ruling covers the notes-family citation grammar only.** The general citation grammar
for every other category §7 also names is Stage 2's and presupposes Q1's closed category set;
it is deliberately left to the decision gate after Slice 3, per the plan's §2 and this
record's own preamble.

### 1. Verified first, at `b2fb122`

| Claim | Verdict |
|---|---|
| tracked files containing the literal `.claude/notes` at `b551060` | **35**, per the plan's §1a, in four classes: 11 frozen plans, 8 intra-notes, 3 mechanism, 13 other living |
| the same count at `b2fb122` | **39** — `git grep -l "\.claude/notes" -- .` lists 39 files. **This moved**, and the growth is entirely in classes the plan's own §1a argument predicts are cheap: **12 frozen plans** (the new NT-0016 plan itself now cites the note's path, +1) and **16 other living** (+3: `docs/audit/findings/README.md`, `docs/audit/work/nt-0012-0013-0014-adoption/README.md`, `scripts/register-owed.py`). Intra-notes stays at 8, mechanism stays at 3. No new file class appears |
| `tests/test_audit_docs_finding_citations.py` names `.claude/notes/` once, in its module docstring, never in executable code | **Confirmed, unchanged** — `tests/test_audit_docs_finding_citations.py:5`, inside the module docstring; no reference in any function body or assertion |
| the mechanism surface is three files, two enforcing (`docs.yml`, `audit-docs.py`) and one documentation-only (the test's docstring) | **Confirmed, unchanged** |
| `NT-00NN` ids already exist and are already cited independently of path, e.g. in the register | **Confirmed** — `docs/audit/register.md` cites 8 distinct `NT-00NN` ids by number; `.claude/notes/README.md` already states the id is "the note's permanent identity," "assigned once, never renumbered, never reused," under the same rule as `ADR-NNNN` and `CLAUDE.md` §5 |
| an id-resolution index already exists to resolve a bare id to a path | **Confirmed** — `.claude/notes/README.md`'s own numbering convention and its `ls .../ \| grep -oE '^[0-9]{4}'` idiom is exactly the resolver Q7's recommendation calls "the Stage-2 index"; nothing new needs to be built for id citations to already resolve today |

### 2. Ruled

**Chosen: cite notes by `NT-00NN` id, resolved via the notes directory's own index/README.
Rejected: continue citing by full path, for the notes family.**

The evidence is the citation surface itself, re-measured rather than assumed: of the 39 files
now touching the literal string `.claude/notes`, only the frozen-plan and mechanism classes
would break under a path-based citation scheme surviving Slice 4's move — and Slice 4 does
not edit frozen plans (C4) or leave the mechanism unrepaired (Slice 1, and Slice 4's own Step
4). Every one of the 16 living-other files and the 8 intra-notes files that cite a note by its
`NT-00NN` id rather than its path continues to resolve correctly the instant the move lands,
because the id is path-independent by construction — it is already governed by the same
append-only, never-renumbered rule as `CLAUDE.md` §5's other id families, and `docs/audit/register.md`'s
own practice (8 ids already cited this way, unaccompanied by a path in the citing text) is a
live precedent, not a proposal. A path citation is exactly the opposite: every one of the
files that cites `.claude/notes/NNNN-....md` by its literal path breaks the moment the
directory moves, which is the entire cost §1a of the plan measures.

This is deliberately narrower than "cite by id" as a project-wide rule. The 12 frozen plans
in the current surface are not being converted to id citations by this ruling — they are not
edited at all, per C4, and the tombstone exists precisely so a path citation inside one of
them keeps resolving. This ruling governs **new and living** citations to the notes family
going forward, not a retrofit of the frozen corpus.

### 3. What it obliges

Slice 4's living-citation edits (§9 Step 5) should, where a rewritten sentence needs to name a
note, prefer `NT-00NN` over a `docs/notes/NNNN-....md` path where the surrounding prose
already supports an id reference; this is a style preference in the same edit already
required by the move, not additional scope. Any future document that cites a note for the
first time cites it by `NT-00NN` id, not by path.

**Overridden if** a future document introduces a new path-only citation to the notes family
where an id citation would have resolved equally well, or if the notes directory's index is
removed without a replacement resolver.

---

## Summary — what moved between `b551060` and `b2fb122`, and what did not

| Evidence claim (plan reference) | At `b551060` | At `b2fb122` | Changed the ruling? |
|---|---|---|---|
| `README.md`/`CONTRIBUTING.md`/`SECURITY.md` contain no `.claude` | 0 occurrences | 0 occurrences, byte-identical file | No — unchanged |
| NT-0016/NT-0017 README dependency exists | Does not exist | Does not exist | No — unchanged |
| `audit-docs.py:249` notes glob (Q6) | Present at `:249` | Present at `:295`, same behaviour | No — line number only |
| `NOTES` constant, `check_notes`, `scan_dirs` (§1b) | `:52`, `:235-236`, `:505-506` | `:66`, `:281-282`, `:551-552` | No — line numbers only; the silent-skip defect is still live at `b2fb122`, confirmed by `python3 scripts/audit-docs.py` still printing `no .claude/notes/ directory` as the guarded branch and exiting 0 when tested |
| `test_audit_docs_finding_citations.py` pins `.claude/notes/` only in its docstring (§1b) | Confirmed | Confirmed, unchanged | No |
| citation surface, `.claude/notes` literal (§1a, Q7) | 35, in 4 classes (11/8/3/13) | 39, in 4 classes (12/8/3/16) | No — growth is confined to the two classes the plan's own §1a argument already predicts are cheap (frozen, living); no new class appeared |

No evidence claim this record depends on reversed direction or contradicted the plan's
reasoning. Every discrepancy found is ordinary drift of the kind `CLAUDE.md` §13 requires a
citation to carry its own tree for — which the plan already does, and which this record now
also does for its own tree.
