---
id: FD-9945
family: finding
title: Check 34 is vacuous on real trees — a frozen-family file's body changes with the gate green, and a plan's activation does it
status: active
created: 2026-09-30
owner: auditor
tree: e9263283177e5e1c1205ba48d0e41c2a1483f83c
corrected_by: []
relates: [FD-1282, WK-1170]
---

# FD-9945 — Check 34 is vacuous on real trees

**Working id 9945.** Filed as a working id; minted at the lead's merge turn. It is cited by its number,
not as a token, until then, and the two places that carry it are this file and its register row.

## Finding

**Severity: medium.** `document-ids.md` §1.6's check 34 row and `frozen_diff_is_permitted`
(`scripts/audit-docs.py:2142-2190`) state the freeze rule: for a frozen family the body is
byte-identical against the merge-base, `status:` moves forward only, `superseded_by:` may change
and `corrected_by:` may only gain entries. `check_freeze` (`scripts/audit-docs.py:2382-2430`) enforces
none of it. Its only live test is the `corrected_by:` → `corrects:` pairing (`:2413-2419`). It never
diffs against a merge-base and never calls `frozen_diff_is_permitted`. On a real tree, a frozen
file's body can change, and `audit-docs.py` exits 0.

Medium, not high: every such edit still passes PR review and stays in git history. It is unflagged,
not invisible.

This is the same gap as FD-1282's main finding. It is filed separately at the maintainer's
direction because the measurement below is new and covers the family that is edited most: **plans**.
It corrects nothing in FD-1282; it adds the evidence, and a fact about practice (item 3).

## Evidence

Every measurement is at `origin/main` `e9263283177e5e1c1205ba48d0e41c2a1483f83c`, in a scratch
`git worktree add`, reverted afterwards. `git status --short` printed nothing.

**1. The check never reads a body.** `check_freeze`'s docstring (`:2383-2392`) says the merge-base
comparison "finds nothing to run against on the real tree today". That is stale: the check's own note
prints `check 34: 492 frozen-family file(s) in scope` at this tree. `_FROZEN_FAMILIES`
(`:2130-2132`) is `decision`, `proposal`, `plan`, `ruling`, `research`, `closure` and `finding`.
`git grep -n frozen_diff_is_permitted -- scripts` gives two hits, the definition (`:2142`) and the
docstring's mention (`:2389`). The tests call it on constructed headers only.

**2. Positive controls, each one sentence edited, each reverted.** Baseline `python3
scripts/audit-docs.py` is rc 0.
- The first body line beginning `The ` in the plan PL-1295 (its file under `docs/plans/`) (an `active` plan), by `sed -i
  '0,/^The /s//The (EDITED BY AUDITOR PROBE) /'`: `The tasks run in order. …` became `The (EDITED BY
  AUDITOR PROBE) tasks run in order. …`. `git diff --stat`: 1 file, 1 insertion, 1 deletion. `audit-docs.py` rc **0**; the check-34 line is unchanged.
- One word inserted after the first `The ` of the body of the closure CR-1212 (its file under `docs/closures/`) (a
  write-once closure), by `sed -i '0,/^The /s//The (EDITED BY AUDITOR PROBE) /'`. 1 file, 1
  insertion, 1 deletion. `audit-docs.py` rc **0**; check-34 line unchanged.

Check 34 can fire: blanking `RL-1290`'s `corrects: RL-881` at an earlier tree gave rc 1
(`corrected_by entry RL-1290 does not corrects: back to RL-881`, FD-1282's amendment). It fires on
the pairing and on nothing else.

**3. The one real on-main plan body edit, and what the predicate says of it.** the plan PL-1299 (its file under `docs/plans/`)
was `status: draft` at `22fe674b~1` and `active` at `22fe674b` (`docs(rulings,plans,roadmap): RL-1301,
SL-1302, PL-1303 … PL-1299 and PL-1303 activated (batch: #971 + #984) (#984)`). `git diff --stat
22fe674b~1 22fe674b -- docs/plans/PL-1299*`: 16 insertions, 2 deletions. The edit rewrites the
Status paragraph (`**Draft.**` → `**Active** (see **Activation**, below).`) and adds an `**Activation.**`
block. Running `frozen_diff_is_permitted` on the two parsed headers and bodies returns
`(False, "the body changed — a frozen file's body never changes")`. `audit-docs.py` passed at
`22fe674b~1` (rc 0, 487 frozen-family files) and at `22fe674b` (rc 0, 489).
- `PL-1303` is **not** an edit on main: `git cat-file -e 22fe674b~1:<its path>` fails, and it
  exists with `status: active` at `22fe674b`. It was born active in that squash.
- `PL-1295` is **not** an edit on main either: one commit touches it, `9f63d0fe` (#954), and
  `status: active` is already in that commit (`git log -S'status: active' -- <its path>`).

A merge-base comparison on those PRs would have seen a new file for `PL-1303` and `PL-1295`, and
a real body change only for `PL-1299`.

**4. The practice is not a one-off.** Corpus: every `docs/plans/PL-*.md` at the tree. Predicate: for each, walk the
first-parent commits on `main` after the W37-6 migration `71f5a220` (2026-09-17, an ancestor of `origin/main`),
and count the plans whose body, defined as the text after the first `\n---\n`, differs between
consecutive commits.

```python
# run in a worktree at e9263283; base = the migration commit
import subprocess, glob
def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout
def body(t): p = t.split("\n---\n", 1); return p[1] if len(p) > 1 else t
base = "71f5a22"
touched = edited = 0; out = []
for f in sorted(glob.glob("docs/plans/PL-*.md")):
    revs = sh("git","log","--format=%h","--first-parent",f"{base}..HEAD","--follow","--",f).split()[::-1]
    if not revs: continue
    touched += 1
    prev = sh("git","show",f"{base}:{f}")
    if not prev: prev = sh("git","show",f"{revs[0]}:{f}"); revs = revs[1:]
    c = 0
    for r in revs:
        cur = sh("git","show",f"{r}:{f}")
        if cur and body(cur) != body(prev): c += 1
        if cur: prev = cur
    if c: edited += 1; out.append((f.split("/")[-1][:8], c))
print(touched, edited, out)
```

Result: **24** plans touched after the migration, **10** with a later body change: `PL-1058` (2
commits), `PL-1070` (2), `PL-1071` (3), `PL-1072` (1), `PL-1073` (2), `PL-1177` (1), `PL-1237`
(1), `PL-1239` (1), `PL-1268` (1), `PL-1299` (1). The count is body changes, not violations: the
edits were not classified as activation notes or other corrections. Counting from before the migration
is meaningless, because the migration rewrote every id (129 of 143 plans show a change). The figure is
`first-parent, body text, plans, after 71f5a220`; a different predicate would give a different count.

## Decisions on record

- **The maintainer** (`to-lead.md`, "2026-09-30 14:48:52 BST — DECISIONS: check 34 is vacuous on real
  trees → a new FD (MEDIUM, WK-1170); PL-1299 accepted; the activation practice from now on", a local
  channel file):
  - this FD, MEDIUM, owner WK-1170, `relates: [FD-1282]`;
  - **`PL-1299`'s merged activation body is accepted as pre-ruling practice**, "content right,
    location against the rule", recorded here, with no correcting record;
  - the order stands: **(a) reconcile the rule and the practice, then (b) enforce**. The maintainer's
    direction for (a): **plan activation is the `status:` flip only**, which check 34 permits.
    Activation facts (gates met, grant time, dispatch record) live in the dispatch record, quoted in
    the slice ledger's Task 0. **From now on no prose is added to a plan already on main.** WK-1170 writes
    the reconciling rule as a dated amendment (process), then the CI comparison;
  - **the interim guard:** the maintainer's ACKs diff every frozen-family file in a PR against main and
    refuse any body change other than `status:` forward, `superseded_by:` or a `corrected_by:` append.

## Disposition

`carry forward with an owner`, **WK-1170**, serialised on `scripts/audit-docs.py` with FD-1282 and
FD-1280's guard. Event: (a)'s amendment merged, then (b) merged.

**(b)'s acceptance, so the fix is not a green stamp.** `check_freeze` calls `frozen_diff_is_permitted`
against `origin/main`, and is shown red on each of:
- a body sentence edited in an `active` plan (the `PL-1295` control above);
- a body word edited in a closure (the `CR-1212` control);
- a **`draft`** plan on main, body-edited (`document-ids.md` :69 says mutability is a family property,
  not a status, so the check must not use `status` as its gate);
- a blanked `corrected_by:` back-link (FD-1282's amendment).

**(a) names `document-ids.md`'s two statements and resolves them toward :69.** :69 says "Mutability is a
family property, not a status", so a plan is frozen by family from the day it is on main. :158 says a plan is
`draft` "while decision points are open" and `active` "on freeze", which reads as if freezing happens at
activation and a draft may still be edited. The maintainer's direction (activation is the `status:` flip only,
no prose added to a plan on main) resolves it toward :69. **:158's "active on freeze" wording is therefore part
of WK-1170's reconcile step (a)**, to be amended with the rule, not left to disagree with it.

It must stay green on a status flip alone, and on a file that is new in the PR. **Ordering matters:** if
(b) lands before (a), the comparison, correct as written, refuses the routine plan activation block.
