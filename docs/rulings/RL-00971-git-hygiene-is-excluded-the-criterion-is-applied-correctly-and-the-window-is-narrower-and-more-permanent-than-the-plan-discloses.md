---
id: RL-971
family: ruling
title: `git-hygiene` is excluded, the criterion is applied correctly, and the window is narrower and more permanent than the plan discloses
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-6-leaf-plan-findings-rulings.md
---

## RL-971 — `git-hygiene` is excluded, the criterion is applied correctly, and the window is narrower and more permanent than the plan discloses

### 1. Verified

RL-987 named `git-hygiene` a candidate *"on the strength of check 39's branch and PR-title
grammar"*. That premise is false, and the falsity is structural rather than incidental.

| Claim | Verdict |
|---|---|
| Check 39 does not check the PR-title clause | **Confirmed.** `check_index_stable`'s executable body touches only `docs/INDEX.md` and `_doc_index.build_corpus`. The clause is an unconditional `notes.append`: *"check 39: PR-title/ledger cross-reference needs GitHub PR context this tree-snapshot tool does not have, and `docs/ledgers/` does not exist in scope yet — not checked here"* |
| Check 38 is warn-only | **Confirmed.** Zero `fail(` calls in `check_loop_signal`; its body is one `notes.append` |
| No check in 30-39 reads a branch or a PR | **Confirmed — and no check in the script can.** `scripts/audit-docs.py` has no `subprocess`, no `os.environ`, no `GITHUB_`, no git invocation anywhere in the file. This is not a scoping gap a later slice narrows; the tool has no capability to read either |
| `git-hygiene`'s taught grammar is invalidated by the migration | **Refuted.** Its only branch grammar is `git checkout -b <type>/<short-slug>` with examples `docs/…`, `feat/…`, `chore(…)/…`, `spike/…` — **no work-id component**. Its PR-title material is Conventional Commits plus the rule that the merge API appends no `(#N)` for you. Neither mentions a work key. The `w32-11-certfloors` string elsewhere in the file is a `git stash push -m` tag, not a branch name |

### 2. Ruled

**The exclusion is confirmed.** Under RL-987's criterion as ruled — *every instrument whose
output is **checked** by checks 30-39* — `git-hygiene` is not a member. Its output is a branch
name and a PR title, neither of which is a tracked file, and no check in the family reads either.
The plan applied my criterion correctly to a candidate my own premise had misdescribed, and it
disclosed the consequence rather than quietly dropping the candidate. That is the behaviour
RL-987 asked for.

**And the exclusion is right on a second, independent ground the plan does not claim: there is
nothing stale in `git-hygiene` to fix.** Its branch and PR grammars are generic and survive the
migration byte-for-byte. An instrument that teaches nothing the migration retires has no H
content to move, so adopting it would add a member with an empty edit — which is the failure
RL-987 acceptance item 2 was reaching for and, under RL-970's 2a, the correct verdict.

### 3. What happens to the window — and it is not the window the plan describes

The plan discloses: *"between this commit and W37-7 there is no valid instruction for naming a
branch or a PR title, because the work keys the current grammar names (`w37-7-…`) no longer exist
after the roadmap restructure."* **That window does not exist**, because `git-hygiene` states no
work-key-bearing grammar for either. A slug an author happens to build from a work key is a free
choice under `<type>/<short-slug>`, not a taught form, and a branch name is not a tracked file.

**What is real is a different and more permanent gap, and it is worth naming precisely because
it will otherwise be planned as a small task.** RFC-937 §1.11 wants a merged PR's title to name
its `SL-` and the slice's ledger to record the PR. After W37-6 that instruction lives in the note
and in no instrument, and `audit-docs.py` cannot enforce it at any scope. Two consequences:

- It is **not** a W37-6-to-W37-7 window. It opens when the standard lands and stays open until
  some instrument teaches the form — which RFC-937 §5.4 already assigns to `git-hygiene`'s H row
  in W37-7. Nothing about this slice's boundary changes it.
- Making check 39's PR clause live requires giving `audit-docs.py` a capability it does not have
  (git or GitHub access) or moving the check elsewhere. **This is a decision, not an
  implementation detail, and no one has taken it.** It is not W37-6's and this record does not
  take it: it is a later slice's decision point, raised here so it is scheduled rather than
  discovered.

**The sequencing question — whether W37-7 runs immediately after W37-6 with `git-hygiene` first
in its order — is the lead's, not this role's.** The plan says so and is right. This ruling
removes the argument that made it urgent.

### 4. Acceptance — the violation that must become detectable

1. **The exclusion must be re-testable, not asserted.** `git-hygiene` is in the exclusion list, so
   RL-970's limb **2b** runs over it: revert its H content, produce the document it mints, run
   the audit. **Violation: any check in 30-39 firing.** If one does, this ruling is wrong and
   `git-hygiene` is adopted. Because its output is a branch name rather than a document, the
   executor records *"no document to produce"* with the reason — which is itself the evidence
   for this ruling, and the ledger carries it in that form rather than as a silent pass.
2. **The gap must not be re-described as closed.** After W37-6, `git grep -n 'SL-' -- .claude/`
   returns no line that teaches an author how to title a PR. **Violation: a closure record, plan
   review or ledger asserting that RFC-937 §1.11's PR-title clause is enforced, satisfied or
   discharged before an instrument teaches it and a check reads it.** A note printed by check 39
   is not enforcement, and the plan's own §7.4 already requires both check 38 and check 39's PR
   clause to be recorded in the ledger as *known non-enforcing*.

---
