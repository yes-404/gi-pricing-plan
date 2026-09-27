---
id: RL-989
family: ruling
title: DP-3: (g) is a property of the script, its filter is a closed enumeration, and it shares check 34's predicate
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-migration-preconditions-rulings.md
---

## RL-989 — DP-3: (g) is a property of the script, its filter is a closed enumeration, and it shares check 34's predicate

### 1. Verified first, at `04ec6bf`

| Claim | Verdict |
|---|---|
| The collision is real | **Confirmed.** §7 (g) requires *"the migration diff filtered to hunks that are neither header nor citation-token"* to be empty. §8's S2 sentence names hand-edited items that *"must land in the same commit"* — `audit-docs.py` parsers and roots, `register-*.py`, `req-coverage.py`, `scope-audit.py`, `file-census.py`, the ten fixture tests, the `docs.yml` filter, the core-JSON digest, the `roadmap.md` restructure, `delivery-process.md`'s vocabulary. Counted: **ten**, as the plan says. None is a header stamp or a citation-token substitution, so over the commit diff (g) cannot be empty |
| A path exclusion could separate them | **Refuted.** Counting §5.2 rows whose Kind cell carries both an M and an H — and excluding the one "H / M" row, which splits a set of *new* files rather than marking one file twice — gives **thirteen**: the specs, the roadmap, the workflows, the ADRs, the notes, the plans, the WK-671 conformance audit, the register, the findings files, the two split records, the checklists, `delivery-process.md` and its core JSON. The same *file* receives script output and a hand edit in the same commit, so excluding those paths would exclude the script's own output for exactly the files (g) most needs to inspect |
| *"(c) is refused by §8's 'same commit'"* | **Not confirmed — the ground does not hold.** `CLAUDE.md` §10 requires squash-merge on every PR, and `origin/main` is a chain of single-parent squash commits (`04ec6bf`, `d4e094b`, `106e322`, each carrying a `(#N)` suffix). A two-commit branch therefore lands on `main` as one commit, so a boundary *inside the branch* does not violate §8's *"same commit"* at all. (c) fails for a different reason, given below. This is recorded because an implementer who reads *"refused by §8"* and then discovers squash-merge will conclude the ruling was wrong and split the merge |
| (g)'s filter is defined | **Refuted.** *"Neither header nor citation-token"* does not classify the script's own remaining steps — the splits of §4 step 2, the `roadmap.md` restructure of step 3, the moves of step 4, or the regenerated artifacts of step 7. Left as worded, an executor invents a filter at the console |

### 2. Ruled

**Chosen: option (a)** — (g) is a property of the **script**, computed over the script's own
output on a clean tree; the H rows are applied afterwards and land in the same commit.

**Rejected: option (b), a path exclusion for the H files** — refuted above: twelve §5.2 rows
put script output and hand edits in the same file.

**Rejected: option (c), split the commit** — but **not** for the reason the plan gives. Under
squash-merge a branch-internal boundary satisfies §8 either way. (c) fails because a commit
boundary is a **one-time observation on a branch that is deleted at merge** (`CLAUDE.md` §10,
branch auto-delete), and `CLAUDE.md` §13 warns against naming a tip rather than a range for
precisely this reason. Option (a) makes (g) re-derivable at any later date from the recorded
merge-base, because §4 states the script is *"deterministic and idempotent"*. **What is not
rejected is the branch structure**: an executor may produce (g)'s evidence by committing the
script's output first and the H rows second, because that is a cheap and mechanical way to
compute the same diff. This ruling settles what (g) *means*, not how many commits the branch
has before it is squashed.

**(g)'s filter is a closed enumeration.** §4's steps 1–7 are the closed list of what `migrate`
is permitted to do, and the filter is that list — a hunk is permitted only where it is:

1. a front-matter block added, together with the legacy prose or bullet header it replaces
   being removed (§4 step 5);
2. a reference token substituted inside a line, from the step-6 allow-list (§4 step 6);
3. a file moved or renamed, detected as a rename, with no content change (§4 step 4);
4. a split, where the concatenation of the outputs reproduces the input's body lines in order
   (§4 step 2);
5. the `roadmap.md` restructure of §4 step 3;
6. a generated artifact regenerated in full — `INDEX.md`, `REDIRECTS.csv`, `docs/contracts/`,
   the core-JSON digest (§4 step 7).

**A hunk the filter cannot classify fails; it is never passed through.** A filter that silently
drops what it does not understand is the same defect as the vanished scan root that once made
five checks skip while the audit printed *"All checks passed"* and exited 0.

**One definition of "reference tokens only", not two.** Where the file belongs to a frozen
family, (g) uses the predicate the plan already disposed of under DP-7 rather than a second
one: *the new bytes, after removing the leading front-matter block and applying the inverse of
every `REDIRECTS.csv` mapping, are byte-identical to the merge-base bytes.* That is stronger
than a hunk filter, it is already being implemented for check 34, and implementing it twice is
how the two drift apart.

### 3. What it obliges

- W37-6's ledger records the merge-base SHA **and** the exact command that computed (g), so the
  result is re-derivable by checking that SHA out and re-running `migrate`.
- (g)'s filter is implemented as code with the six classes named, not as a shell pipeline
  composed at the console.
- The frozen-family branch of the filter calls check 34's DP-7 predicate rather than
  reimplementing it.

### 4. Acceptance — the violation that must become detectable

1. **The filter must fail on a body-line change.** A mutation fixture in W37-5's corpus makes
   `migrate` alter one word of a body line that is neither a header nor a reference token.
   **Violation: (g) is empty on the mutated run** — the filter is wider than the rule, and (g)
   is not testing the script. It must be non-empty *and* name that file.
2. **The filter must fail on what it cannot classify.** Feed it a hunk in none of the six
   classes — a body line reordered within a file. **Violation: an unclassifiable hunk that
   produces no output.**
3. **One predicate, not two.** Mutate check 34's DP-7 allowance. **Violation: (g)'s
   frozen-family branch does not change with it.**

---
