---
id: FD-9912
family: finding
title: Check 34 does not run its merge-base comparison on the real tree, so a frozen file's body can change with the gate green
status: active
created: 2026-09-30
owner: auditor
tree: 880feb499eddb9e854c525770e95fb19373a2311
corrected_by: []
relates: [WK-1178]
---

# FD-9912 — Check 34 does not run its merge-base comparison on the real tree, so a frozen file's body can change with the gate green

## Finding

**Severity: medium.** `document-ids.md` §1.6's check 34 row says that for a frozen family *"the
diff against the merge-base touches only `status:` (forward only), `superseded_by:`, an append
to `corrected_by:` …"*, and the Ruling header comment says *"the body is never edited"*. The
predicate that states this, `frozen_diff_is_permitted` (`audit-docs.py:2142`), begins with
*"the body … is byte-identical"*. `check_freeze` (`audit-docs.py:2382`) never calls it. A frozen
file's body, or a non-allowed header field, can change and `audit-docs.py` still exits 0.

**A second, wider finding rides with it, and the options below depend on it.** The repository's
own practice does not follow the rule as written: `docs/findings/README.md` says *"An essay file
is write-once, amended in place … a correction is appended and dated"*, and FD-1246's body carries
a *"Lead's decision, 2026-09-29"* paragraph appended after filing. Enforcing the predicate as it
stands would fail those. This record does not decide which side is wrong (`CLAUDE.md` §0).

## Evidence

At `origin/main` `880feb499eddb9e854c525770e95fb19373a2311`, in a scratch `git worktree add --detach` (reverted; `git status --short`
printed nothing afterwards).

- `audit-docs.py:2382-2392`, `check_freeze`'s docstring: *"No in-scope file is ever a
  frozen-family instance during S1 … so the merge-base comparison — `frozen_diff_is_permitted`
  above — finds nothing to run against on the real tree today; it is exercised directly against
  constructed old/new `Header` pairs in `tests/test_audit_docs_ids.py`."* That is stale:
  the check's own note now prints `check 34: 469 frozen-family file(s) in scope`. The body of
  `check_freeze` (`:2395-2425`) runs only the `corrected_by:` / `corrects:` cross-check.
- `grep -n 'frozen_diff_is_permitted' scripts/audit-docs.py` prints the definition (`:2142`),
  the docstring mentions (`:2389`) and no call. `grep -rn 'frozen_diff_is_permitted\|check_freeze\|merge-base'
  .github/workflows` matches only a comment in `docs.yml:113` about a different mechanism
  (`migrate --verify`), so no workflow runs it either.
- **Broken-input proof**, appending one line to `docs/closures/CR-01212-plan-review-15-…md`:

  | Probe | `audit-docs.py` rc | check 34 line |
  |---|---|---|
  | none (baseline) | 0 | `check 34: 469 frozen-family file(s) in scope` |
  | body line appended, uncommitted | **0** | same line |
  | same append committed (`git diff --stat origin/main...HEAD`: 1 file, 2 insertions) | **0** | same line |
  | `status:` changed `active` to `superseded` on the same file | 1 | fails on **check 33** (status outside the closure subset, `superseded_by` empty), not on check 34 |

  So a body edit reaches no check, and the one header edit that does fail is caught by a
  different check.
- Population, for scale only: `git log origin/main --since=2026-09-18 --diff-filter=M
  --name-only --format= -- docs/closures docs/findings docs/rulings docs/plans docs/adrs
  docs/research docs/rfcs`, filtered to `/(CR|FD|RL|PL|ADR|RS|RFC)-[0-9]+-` and de-duplicated,
  prints 39 files (5 of them in two or more commits). It counts modified files whatever the
  hunk, header or body, so it is **not** a count of body edits.

## Disposition

**Carry forward, unowned**, proposed by the auditor on 2026-09-30; the register row's
`decision:` is the lead's. Options, with a recommendation and no decision:

- **(a) Reconcile the rule with practice first**: rule whether a dated appended note is
  permitted on a frozen body (`FD`, `CR`), amend `document-ids.md` and check 34's docstring to
  say so, then enforce that narrower predicate. Cost: a maintainer ruling. Without it, (b)
  and (c) go red on legitimate work or cannot be written.
- **(b) Run the comparison in CI against `origin/main`** (`audit-docs.py --base <ref>`
  calling `frozen_diff_is_permitted` per changed frozen file). Cost: the tool needs the base
  ref, and a shallow CI checkout must fetch it.
- **(c) Make it a pytest invariant** over `git diff origin/main...HEAD`. Cost: the test depends
  on git history, so it is skipped or wrong in a shallow or detached checkout; it must fail
  loudly rather than skip.

**Recommendation: (a) then (b).** (b) alone would enforce a rule the team already breaks.
Whichever lands must be proven on the input above: append a line to a frozen closure and
watch the gate exit 1. Event that discharges it: the maintainer's ruling on (a), then the fix.
If unowned at the next `CLAUDE.md` §14 review, the row decays to that review.
