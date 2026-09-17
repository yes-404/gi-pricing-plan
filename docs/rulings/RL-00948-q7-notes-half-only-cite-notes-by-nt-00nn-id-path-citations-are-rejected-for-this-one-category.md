---
id: RL-948
family: ruling
title: Q7, notes half only: cite notes by `NT-00NN` id; path citations are rejected for this one category
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-01
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md
---

## RL-948 — Q7, notes half only: cite notes by `NT-00NN` id; path citations are rejected for this one category

**This ruling covers the notes-family citation grammar only.** The general citation grammar
for every other category §7 also names is Stage 2's and presupposes Q1's closed category set;
it is deliberately left to the decision gate after Slice 3, per the plan's §2 and this
record's own preamble.

### 1. Verified first, at `b2fb122`

| Claim | Verdict |
|---|---|
| tracked files containing the literal `.claude/notes` at `b551060` | **35**, per the plan's §1a, in four classes: 11 frozen plans, 8 intra-notes, 3 mechanism, 13 other living |
| the same count at `b2fb122` | **39** — `git grep -l "\.claude/notes" -- .` lists 39 files. **This moved**, and the growth is entirely in classes the plan's own §1a argument predicts are cheap: **12 frozen plans** (the new RFC-897 plan itself now cites the note's path, +1) and **16 other living** (+3: `docs/audit/findings/README.md`, `docs/closures/CR-00933-audit-record-nt-0012-0013-0014-adoption-docs-audit-checklists-work-item-close-md.md`, `scripts/register-owed.py`). Intra-notes stays at 8, mechanism stays at 3. No new file class appears |
| `tests/test_audit_docs_finding_citations.py` names `.claude/notes/` once, in its module docstring, never in executable code | **Confirmed, unchanged** — `tests/test_audit_docs_finding_citations.py:5`, inside the module docstring; no reference in any function body or assertion |
| the mechanism surface is three files, two enforcing (`docs.yml`, `audit-docs.py`) and one documentation-only (the test's docstring) | **Confirmed, unchanged** |
| `NT-00NN` ids already exist and are already cited independently of path, e.g. in the register | **Confirmed** — `docs/findings/register.md` cites 8 distinct `NT-00NN` ids by number; `.claude/rfcs/README.md` already states the id is "the note's permanent identity," "assigned once, never renumbered, never reused," under the same rule as `ADR-NNNN` and `CLAUDE.md` §5 |
| an id-resolution index already exists to resolve a bare id to a path | **Confirmed** — `.claude/rfcs/README.md`'s own numbering convention and its `ls .../ \| grep -oE '^[0-9]{4}'` idiom is exactly the resolver Q7's recommendation calls "the Stage-2 index"; nothing new needs to be built for id citations to already resolve today |

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
append-only, never-renumbered rule as `CLAUDE.md` §5's other id families, and `docs/findings/register.md`'s
own practice (8 ids already cited this way, unaccompanied by a path in the citing text) is a
live precedent, not a proposal. A path citation is exactly the opposite: every one of the
files that cites `.claude/rfcs/NNNN-....md` by its literal path breaks the moment the
directory moves, which is the entire cost §1a of the plan measures.

This is deliberately narrower than "cite by id" as a project-wide rule. The 12 frozen plans
in the current surface are not being converted to id citations by this ruling — they are not
edited at all, per C4, and the tombstone exists precisely so a path citation inside one of
them keeps resolving. This ruling governs **new and living** citations to the notes family
going forward, not a retrofit of the frozen corpus.

### 3. What it obliges

Slice 4's living-citation edits (§9 Step 5) should, where a rewritten sentence needs to name a
note, prefer `NT-00NN` over a `docs/rfcs/NNNN-....md` path where the surrounding prose
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
| RFC-897/RFC-898 README dependency exists | Does not exist | Does not exist | No — unchanged |
| `audit-docs.py:249` notes glob (Q6) | Present at `:249` | Present at `:295`, same behaviour | No — line number only |
| `NOTES` constant, `check_notes`, `scan_dirs` (§1b) | `:52`, `:235-236`, `:505-506` | `:66`, `:281-282`, `:551-552` | No — line numbers only; the silent-skip defect is still live at `b2fb122`, confirmed by `python3 scripts/audit-docs.py` still printing `no .claude/notes/ directory` as the guarded branch and exiting 0 when tested |
| `test_audit_docs_finding_citations.py` pins `.claude/notes/` only in its docstring (§1b) | Confirmed | Confirmed, unchanged | No |
| citation surface, `.claude/notes` literal (§1a, Q7) | 35, in 4 classes (11/8/3/13) | 39, in 4 classes (12/8/3/16) | No — growth is confined to the two classes the plan's own §1a argument already predicts are cheap (frozen, living); no new class appeared |

No evidence claim this record depends on reversed direction or contradicted the plan's
reasoning. Every discrepancy found is ordinary drift of the kind `CLAUDE.md` §13 requires a
citation to carry its own tree for — which the plan already does, and which this record now
also does for its own tree.
