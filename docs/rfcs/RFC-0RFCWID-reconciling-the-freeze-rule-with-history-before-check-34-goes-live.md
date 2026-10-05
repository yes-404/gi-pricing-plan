---
id: RFC-RFCWID
family: proposal
kind: process
title: Reconciling the freeze rule with history before check 34's merge-base comparison goes live
status: draft                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-10-05
owner: maintainer
tree: 99afcde215c0817c5ac4db55332ab7a69e4752a0
deliverable: RL-9654 applied — document-ids.md :158, §1.5 and §1.11 row 34 amended, findings/ and closures/ READMEs reconciled, and check 34 live with the cut as its lower bound
lands_in: docs/process/document-ids.md, docs/findings/README.md, docs/closures/README.md, scripts/audit-docs.py (check 34)
trigger: check 34's merge-base comparison going live (FD-1282 option (b), PL 9662)
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-9654, FD-1282, FD-1323, WK-1170]
---

# RFC-RFCWID — Reconciling the freeze rule with history before check 34's merge-base comparison goes live

*Working id RFCWID; drafted 2026-10-05 by the decision-maker on instruction (`document-ids.md`
§1.6 RFC row: "any role drafts on instruction"), on the deputy's entry `2026-10-05 13:32:57
BST — 34: SPAWN the DM for the freeze-rule RFC + RL; my leaning stated, not ruled`
(`~/gi-pricing-plan.local/channel/to-lead.md`, a local file). Its ruling is RL-9654.*

## Problem

The freeze rule says a frozen family's body never changes after merge (`document-ids.md`
§1.5 :134-:135, §1.11 row 34 :230). Check 34 does not enforce it (FD-1282, FD-1323), and the
repository's practice did not follow it: three passages instruct the opposite —
`docs/findings/README.md` :60-:61 (*"amended in place … A correction is appended and dated"*)
and :72-:73, `docs/closures/README.md` :33 — and §1.6's PL row :158 (*"`active` on freeze"*)
reads as though a plan freezes at activation. FD-1282 ordered **(a) reconcile, then (b)
enforce**: enforcing first would red on legitimate work or on history.

## Population

**Predicate, verbatim** (`measure.py`, run as `python3 measure.py <BASE> <TIP>` from the
repository root):

```python
"""Body edits to existing frozen-family files on origin/main's first-parent line since a base.

Predicate: a commit C on `git rev-list --first-parent --reverse BASE..origin/main` whose
`git diff-tree -r --no-renames --diff-filter=M C^ C` lists a path matching FROZEN_RE, and
whose body (text after the second `---` line) differs between C^:path and C:path.
"""
import re
import subprocess
import sys

BASE = sys.argv[1]
TIP = sys.argv[2] if len(sys.argv) > 2 else "origin/main"
FROZEN_RE = re.compile(
    r"^docs/(adrs/ADR|rfcs/RFC|plans/PL|rulings/RL|research/RS|closures/CR|findings/FD)-\d+-[^/]+\.md$"
)


def git(*a: str) -> str:
    return subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout


def body(text: str) -> str:
    lines = text.split("\n")
    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i] == "---":
                return "\n".join(lines[i + 1 :])
    return text


for c in git("rev-list", "--first-parent", "--reverse", f"{BASE}..{TIP}").split():
    paths = git("diff-tree", "-r", "--no-renames", "--diff-filter=M", "--name-only", "--no-commit-id", f"{c}^", c).split("\n")
    for p in paths:
        if not FROZEN_RE.match(p):
            continue
        old, new = body(git("show", f"{c}^:{p}")), body(git("show", f"{c}:{p}"))
        if old != new:
            meta = git("log", "-1", "--format=%aI%x09%s", c).strip()
            stat = git("diff", "--numstat", f"{c}^", c, "--", p).split()[:2]
            print(f"{c}\t{p}\t+{stat[0]}/-{stat[1]}\t{meta}")
```

The family directories are `_FROZEN_FAMILIES` (`scripts/audit-docs.py:2130-:2132`) mapped
through §1.4's layout. Runs at `99afcde215c0817c5ac4db55332ab7a69e4752a0`:

| Range | Rows |
|---|---|
| `71f5a2208c7a92bad486ae128775a4a42c7ebc63..99afcde2…` (since the W37-6 migration) | **42** — FD 17, PL 15, CR 5, RL 4, RFC 1 |
| `e9263283177e5e1c1205ba48d0e41c2a1483f83c..99afcde2…` (since the cut) | **0** |

A second predicate — header fields other than `status:`, `superseded_by:`, `corrected_by:`
changed on the same files and range — prints one row before the cut (`97b15726…`, PL-1239:
`relates`, `slice`, a row already below) and **0** after it.

Classes, read from each diff's added lines: **C** a correction or amendment of content;
**R** an FD resolution or progress note; **V** a plan's activation; **A** an acceptance line
filled after merge; **M** a working id rewritten to its minted id; **L** a merge or run log
appended to a plan.

| # | Commit | Date | File | Dir | ± | Class |
|---|---|---|---|---|---|---|
| 1 | `1cd489c870f9f117c19f009f0a096dc8ac748929` | 2026-09-17 | PL-1058 | `plans/` | +105/-0 | L |
| 2 | `d63f765085fe6eb1c594177c5779ecfc3caf7ae8` | 2026-09-18 | PL-1058 | `plans/` | +77/-0 | C |
| 3 | `7d5d6e0a3730bfd790dace3a95c63a0ea71ec031` | 2026-09-18 | CR-1065 | `closures/` | +58/-0 | C |
| 4 | `a6173364409e57fb607e809388ef050a66646762` | 2026-09-19 | RL-1075 | `rulings/` | +90/-0 | C |
| 5 | `73a40a60efd43c3e6d2f744dbe1381171e54c4f8` | 2026-09-19 | CR-1065 | `closures/` | +132/-0 | C |
| 6 | `9f887b68340daf587fc1394cfe1b76466b28f4fb` | 2026-09-19 | RL-1078 | `rulings/` | +256/-0 | C |
| 7 | `4ed1f88ee89deeddca04565cc1f07cdbaf02dba4` | 2026-09-26 | PL-1070 | `plans/` | +602/-2 | C |
| 8 | `4ed1f88ee89deeddca04565cc1f07cdbaf02dba4` | 2026-09-26 | RFC-937 | `rfcs/` | +2/-0 | C |
| 9 | `20d922dd3ac40678ecd003787fbc27360a77c688` | 2026-09-26 | PL-1073 | `plans/` | +348/-7 | C |
| 10 | `536d3cc3bda9d1e709bf12118999ce5b09dce399` | 2026-09-26 | CR-1050 | `closures/` | +5/-1 | A |
| 11 | `536d3cc3bda9d1e709bf12118999ce5b09dce399` | 2026-09-26 | CR-1064 | `closures/` | +6/-1 | A |
| 12 | `536d3cc3bda9d1e709bf12118999ce5b09dce399` | 2026-09-26 | PL-1070 | `plans/` | +29/-0 | C |
| 13 | `536d3cc3bda9d1e709bf12118999ce5b09dce399` | 2026-09-26 | PL-1073 | `plans/` | +22/-0 | C |
| 14 | `7a519fce5673f7b494ed0304daf27ee013da58c9` | 2026-09-27 | PL-1071 | `plans/` | +311/-7 | C |
| 15 | `a24c0a28c80762599671f1c7128979d3d1546f30` | 2026-09-27 | PL-1071 | `plans/` | +3/-0 | C |
| 16 | `5429c397d2ad5672ed31734bc07b946ea5a9b8df` | 2026-09-27 | PL-1071 | `plans/` | +1/-0 | C |
| 17 | `823a75efb5da70d8c652c91fd6dc54e5ab966149` | 2026-09-27 | PL-1072 | `plans/` | +31/-6 | C |
| 18 | `df8e5811a151a99c7317690faf9278a6dc3400be` | 2026-09-27 | FD-1152 | `findings/` | +25/-0 | C |
| 19 | `ed123cb0fcf91e44872963bf8a8bad32b87c99bc` | 2026-09-28 | PL-1177 | `plans/` | +15/-2 | V |
| 20 | `9f6bfed1a94838d92bdc76475e03f8b5b078527a` | 2026-09-28 | FD-1175 | `findings/` | +22/-1 | R |
| 21 | `9f6bfed1a94838d92bdc76475e03f8b5b078527a` | 2026-09-28 | FD-1180 | `findings/` | +7/-1 | R |
| 22 | `4fb07b6cb17cacb2f6f578f264a36a455143c45f` | 2026-09-28 | FD-1200 | `findings/` | +26/-1 | R |
| 23 | `1ad2a131e24396a9b47340739456bd688d53df9d` | 2026-09-28 | FD-1203 | `findings/` | +14/-1 | R |
| 24 | `bb2aa935dbdf207a7073df85f8fde143e1cee77b` | 2026-09-29 | FD-1195 | `findings/` | +21/-0 | R |
| 25 | `bb2aa935dbdf207a7073df85f8fde143e1cee77b` | 2026-09-29 | FD-1206 | `findings/` | +21/-1 | R |
| 26 | `bb2aa935dbdf207a7073df85f8fde143e1cee77b` | 2026-09-29 | FD-1207 | `findings/` | +18/-1 | R |
| 27 | `bb2aa935dbdf207a7073df85f8fde143e1cee77b` | 2026-09-29 | FD-1210 | `findings/` | +8/-0 | R |
| 28 | `d7ed822ec238a3344a04215240a67bff4994fed9` | 2026-09-29 | FD-1214 | `findings/` | +41/-8 | C |
| 29 | `870ce82b48736db7e2cfcb6f81a5fbb985060c17` | 2026-09-29 | FD-1195 | `findings/` | +33/-1 | R |
| 30 | `49604a31785c8e7709e9b87c3926e27ea1c0f7f2` | 2026-09-29 | RL-1232 | `rulings/` | +26/-0 | C |
| 31 | `49604a31785c8e7709e9b87c3926e27ea1c0f7f2` | 2026-09-29 | RL-1236 | `rulings/` | +22/-0 | C |
| 32 | `1b45586cb9ba9964e5a6426fb3b4ff47beaa71fc` | 2026-09-29 | PL-1237 | `plans/` | +64/-3 | V |
| 33 | `ac8ab519c8e46141e81cb5ca6f48da9afaa35075` | 2026-09-29 | FD-1238 | `findings/` | +13/-0 | C |
| 34 | `40739df04087d3e28c1dcb1fa92e581db26603da` | 2026-09-29 | CR-838 | `closures/` | +2/-0 | C |
| 35 | `5638f69120e0f4d9c958dc1bf4a07f589b42f080` | 2026-09-29 | FD-1208 | `findings/` | +11/-1 | R |
| 36 | `5638f69120e0f4d9c958dc1bf4a07f589b42f080` | 2026-09-29 | FD-1209 | `findings/` | +8/-0 | R |
| 37 | `97b15726b1dd60ba407c6aba44735ad5cbe207ed` | 2026-09-29 | PL-1239 | `plans/` | +82/-24 | V |
| 38 | `95639d87c57c02a2f4da04477744cf82ff053d9d` | 2026-09-30 | PL-1268 | `plans/` | +37/-8 | V |
| 39 | `159afa76c03c9d75199a29dadd3efd93565f01af` | 2026-09-30 | FD-1283 | `findings/` | +13/-11 | M |
| 40 | `159afa76c03c9d75199a29dadd3efd93565f01af` | 2026-09-30 | FD-1284 | `findings/` | +4/-2 | M |
| 41 | `14e9b9d59bc9f2b7b951be0e2c4e3cf72f8cdd19` | 2026-09-30 | FD-1282 | `findings/` | +27/-0 | C |
| 42 | `22fe674b4a590c47095c6ba608fe974264581139` | 2026-09-30 | PL-1299 | `plans/` | +16/-2 | V |

Totals: C 21, R 11, V 5, A 2, M 2, L 1. The examples the brief names: CR-838 is row 34
(`40739df0…`, *"Dated correction, 2026-09-29"*). **FD-1246 is not in the population**:
`git log --first-parent --diff-filter=M 71f5a220..99afcde2 -- docs/findings/FD-01246-*` prints
nothing: the file was added by `5638f69120e0f4d9c958dc1bf4a07f589b42f080` (2026-09-29) with its *"Lead's decision,
2026-09-29"* paragraph (FD-1282 cites it) already in it — not a post-merge edit, and nothing for check 34 to see.

## The deputy's leaning, tested

The leaning: grandfather the historical notes by an enumerated list (file and commit) that
becomes check 34's allowlist, and add **no** dated-note exemption, so every later body change
is a correcting record. It was tested on two questions.

**1. Is a correcting record unworkable for any class?** No. Each class has a destination that
leaves the frozen body unchanged:

- **C (21).** A correcting `RL-` with `corrects:` — the form RL-1290 (`corrects: RL-881`) and
  RL-1287 (`corrects: CR-1212`) already use on `main`.
- **R (11).** A resolution corrects nothing, so `corrects:` would be false. It goes to the
  register row, which is living (§1.2: *"living row + frozen essay"*), and `status:` moves
  forward. §1.6's FD row (*"auditor sets `closed` in place citing the PR"*) is satisfied by the
  row and the header.
- **V (5).** Already decided by the deputy's entry `2026-09-30 14:48:52 BST`, item (3): the
  `status:` flip only, the facts in the dispatch record quoted in the ledger's Task 0. Row 37
  (PL-1239) also added `slice:` and `relates:` at activation; both can be set at mint, since the
  map plan cuts the `SL-` first (§1.6 SL row) and the later `RL-` carries the link in its own
  `relates:`.
- **A (2).** CR-1050 and CR-1064 merged with *"Maintainer acceptance: _pending_"*. The
  acceptance can land in the PR before merge (the deputy's ACK precedes the lead's merge), or
  after merge as a maintainer-authored `RL-` (§1.6 RL row: *"the maintainer may author one on
  scope or process"*) that `relates:` the record.
- **M (2).** FD-1283 and FD-1284 cited a sibling plan by working id 9681 and were rewritten to
  PL-1286. FD-1283's own text already carried *"PR #920"*; a PR number resolves for ever, so
  nothing needs a rewrite at mint.
- **L (1).** A merge log is a ledger's or a closure's content.

So the leaning's **substance stands**: no dated-note exemption form.

**2. Does check 34 need the allowlist?** Not as a file. §1.11 row 34 compares against the
merge-base. Each of the 42 is an ancestor of every future merge-base, so that comparison never
sees one: a list it read would never match. A list matters only if check 34 also reads history
— and then the list equals "every body edit before the cut", a set the check derives from one
constant. Two copies of one set is the duplication RFC-756 records going stale.

## Options

| Option | What grandfathers history | What a later body edit meets | Cost | Weakness |
|---|---|---|---|---|
| **A — the leaning as relayed** | a data file of 42 (commit, file) pairs, read by check 34 | refusal | a file, its parser, a guard that it cannot grow | under a merge-base comparison the file is never consulted; under a history leg it duplicates a derivable set; it can still be appended to in a reviewed diff |
| **B — cut commit (recommended)** | one constant, `e9263283177e5e1c1205ba48d0e41c2a1483f83c`: no comparison reads at or before it; the 42 enumerated in this RFC | refusal | one constant; this table | the enumeration lives in a record, not in the check — by design |
| **C — a dated-note exemption form** | a recognised appended-note shape | admitted if it copies the shape | a parser for the shape | any rewrite can wear the shape; the check cannot tell a correction from a change |
| **D — merge-base only, nothing said** | the scope of the comparison | refusal on a PR | none | the grandfathering is accidental and unrecorded; a push to `main` or an edit merged with the gate red is never seen |

## Proposal

**Recommendation: B**, with no dated-note exemption (the leaning's substance). The cut is
`e9263283177e5e1c1205ba48d0e41c2a1483f83c` — `origin/main` when the deputy ruled at
`2026-09-30 14:48:52 BST`, and FD-1323's measurement tree. Nothing after it needs
grandfathering (0 rows). RL-9654 rules it, with the T-texts for `document-ids.md` :158, §1.5
and §1.11 row 34, `docs/findings/README.md` and `docs/closures/README.md`.

Recommended to PL 9662, for the planner to decide: a **history leg** that runs
`frozen_diff_is_permitted` on each first-parent commit in `<cut>..HEAD`, beside the merge-base
leg. The merge-base leg is empty on a push to `main`, so only a history leg sees an edit that
reached `main` with the gate red or bypassed. Cost, measured here: the predicate above took
4.2 s over every first-parent commit since `71f5a220`; `docs.yml:45` already checks out with
`fetch-depth: 0`.

## Deliverable

RL-9654 applied by WK-1170 (PL 9662 names RL-9654 as its precondition): T1-T5 landed, and
check 34 live with the cut as the lower bound of every range it reads, proven red on a body
line appended to a merged closure and on a `slice:` change to a merged plan.
