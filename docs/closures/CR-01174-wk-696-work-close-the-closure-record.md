---
id: CR-1174
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-696 Work close — the closure record (RFC-898, a public face for a public repository)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-28
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
work: WK-696
corrected_by: []
relates: []                     # ids only
---

# CR-1174 — WK-696 Work close: the closure record

## Scope

**What closes.** WK-696 is the residue of RFC-898
([`RFC-898`](../rfcs/RFC-00898-a-public-repository-needs-a-public-face.md)), which asks for a
public face for a public repository. The content landed on 2026-08-30. This record is what the
deputy reads to decide the Work close. The maintainer delegated that decision, and the row-6
settings line, to the deputy until the end of this goal. This record is not that decision.

**Where the scope comes from.** It is derived from the specification, never from what was
built (`CLAUDE.md` §13). There are two sources:

- the WK-696 row in [`docs/roadmap.md`](../roadmap.md) at `df8e5811`. Its acceptance reads
  *"the note's §8 (a) and (c)–(e)"*. Its residue is *"two impact rows"*: row 9, which the row
  itself discharges, and row 6, the two repository settings;
- RFC-898's acceptance standard, with its (b) = impact row 6, and its impact matrix, rows 1–9.

The lead's brief named (a), (c) and (d). The roadmap row governs, and it also names (e). The
lead confirmed this scope in his "GO" message to this auditor on 2026-09-28. RFC-898's own
wording for (d) is narrower than a general read. It is *"the README contains zero sentences
duplicating roadmap or CLAUDE.md content"*. That predicate gets its own verdict below, and the
wider outsider read follows it.

**Where the content came from.** These commits are all on `origin/main`:

| Commit | PR | What |
|---|---|---|
| `76e1ecf9` | #494 | The three policy decisions of RFC-898, now [`RL-914`](../rulings/RL-00914-rfc-898-the-maintainer-s-three-policy-decisions-recorded-2026-08-30.md) |
| `01ba0bd2` | #495 | `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, both issue forms, the PR template, the checklist line and the security-posture line |
| `595ae4f7` | #497 | Removes a competitor's product names from the public files |
| `49c06ad7` | #817 | W37-9: rewrites the public face for the id standard (RFC-937) |

**Authorship and verdicts.** `document-ids.md` §1.6 gives the `CR` family, `kind: work`, to
the auditor. **Every verdict below is proposed, not issued.** The verdicts are the lead's
(`CLAUDE.md` §12). The acceptance line is the deputy's, by delegation.

## Evidence

### (a) All five files exist, and every internal link resolves

The impact matrix counts five files, and row 4 holds two forms, so six paths are checked. All
six exist at `df8e5811`: `README.md`, `SECURITY.md`, `CONTRIBUTING.md`,
`.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/bug.yml` and
`.github/ISSUE_TEMPLATE/question.yml`.

The repository ships no link checker. The checker below is the command the acceptance standard
asks to be named. Its predicate is in its docstring, and it is reproduced here in full so that
a reader holding none of this record's context can run it:

```python
"""WK-696 acceptance (a): every internal link in RFC-898's five public-face files resolves.

Usage: python3 linkcheck.py <tree>
Predicate: every markdown link (bracketed text, then a parenthesised target) not http(s)/mailto is
resolved relative to the linking file's directory; the path must exist in the tree, and
a `#fragment` on a .md target must match a GitHub-style heading slug in that file.
Backticked repo paths (`docs/...`, `.github/...`, `*.md`) are also checked for existence
and reported on a separate line. External links are listed, not fetched.
Exit 0 iff zero broken internal links. Backticked-path misses are advisory (a shorthand in
prose, not a link) and are printed for the reader to judge.
"""
import re
import sys
from pathlib import Path

FILES = [
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/question.yml",
]
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
TICK = re.compile(r"`([A-Za-z0-9_./-]+)`")


def slugs(md: Path) -> set[str]:
    out = set()
    for line in md.read_text(encoding="utf-8").splitlines():
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m:
            s = re.sub(r"[^\w\- ]", "", m.group(1).strip().lower()).replace(" ", "-")
            out.add(s)
    return out


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    links = broken = ext = ticks = tick_missing = 0
    for rel in FILES:
        f = root / rel
        if not f.exists():
            print(f"MISSING FILE {rel}")
            broken += 1
            continue
        text = f.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                ext += 1
                print(f"external {rel} -> {target}")
                continue
            links += 1
            path, _, frag = target.partition("#")
            dest = (f.parent / path).resolve() if path else f
            ok = dest.exists()
            if ok and frag and dest.suffix == ".md":
                ok = frag.lower() in slugs(dest)
            if not ok:
                broken += 1
                print(f"BROKEN {rel} -> {target}")
        for t in TICK.findall(text):
            if "/" in t or t.endswith(".md"):
                ticks += 1
                if not (root / t).exists() and not (f.parent / t).exists():
                    tick_missing += 1
                    print(f"TICK-MISSING {rel} -> `{t}`")
    print(f"files={len(FILES)} internal_links={links} broken={broken} external={ext}")
    print(f"backticked_paths={ticks} missing={tick_missing}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
```

**Result at `df8e5811`**, from `python3 linkcheck.py <tree>`:

```text
TICK-MISSING CONTRIBUTING.md -> `register.md`
files=6 internal_links=22 broken=0 external=0
backticked_paths=32 missing=1
```

The exit code was 0. The one advisory line is `CONTRIBUTING.md:35`. It uses a bare
`register.md` as prose shorthand for `docs/findings/register.md`, which is linked seven lines
earlier. That is not a link, and it is not broken.

**The check fails on broken input.** The six files were copied into an empty directory, so
none of their targets existed. The run reported `internal_links=22 broken=19`. The three links
that still resolved point at the copied files themselves (`CONTRIBUTING.md`, `SECURITY.md` and
`README.md`).

**Re-run at the close tree.** The final gate records the run on this record's own committed
tree, in the PR body and in the lead's report. Nothing in the six files changes on this
branch, so the result cannot differ from the result above.

### (b) Impact row 6: the two repository settings

This item is settings-side. RFC-898 says it is evidenced by a dated line, and that line is now
the deputy's by delegation. **The line is pending: the deputy's dated line by delegation.**

Evidence the line may quote was read with the `gh` CLI (`yes-404` token) on 2026-09-28:

- `gh api repos/yes-404/gi-pricing-plan/private-vulnerability-reporting` returned
  `{"enabled":true}`;
- `gh repo view yes-404/gi-pricing-plan --json hasIssuesEnabled,visibility` returned
  `{"hasIssuesEnabled":true,"visibility":"PUBLIC"}`;
- `.github/ISSUE_TEMPLATE/config.yml` does not exist, so blank issues stay allowed, as RFC-898
  §2 "Settings", item 2 asks.

The deputy's own read of the settings, from the 11:19:17 BST entry, is separate evidence that
the lead quotes.

### (c) One test issue filed through each form

**Leg 1: the two issues.** Both were filed on 2026-09-28 at 11:26:29 BST with the `gh` CLI
(gh 2.46.0). Each body reproduced what the web form produces: one `### <field label>` section
for each field, in the form's order.

| Form | Issue | Title | Filed with |
|---|---|---|---|
| `bug.yml` ("Bug report") | [#825](https://github.com/yes-404/gi-pricing-plan/issues/825) | `[test] WK-696 acceptance (c): bug.yml (Bug report)` | `gh issue create --repo yes-404/gi-pricing-plan --title … --label bug --body-file issue-bug.md` |
| `question.yml` ("Question or suggestion") | [#826](https://github.com/yes-404/gi-pricing-plan/issues/826) | `[test] WK-696 acceptance (c): question.yml (Question or suggestion)` | `gh issue create --repo yes-404/gi-pricing-plan --title … --label question --body-file issue-question.md` |

Each issue was then read back.

- **Body.** `gh issue view <n> --json body` was diffed against its body file. The only
  difference is a trailing newline, on both issues.
- **Render.** The `h3` headings of the rendered HTML (`gh api repos/yes-404/gi-pricing-plan/issues/<n>
  -H "Accept: application/vnd.github.html+json"`) match each form's field labels, in order.
  - #825: *Version / tree, Steps to reproduce, Expected behaviour, Observed behaviour,
    Additional context, Related id (optional)*.
  - #826: *Category, Details, Related id (optional)*.
- **Labels: not applied.** `gh issue create --label` exited 0 on both issues, yet REST and
  GraphQL both read `labels: []`, and the issue events list is empty. The labels were then
  added by hand with `gh api -X POST repos/yes-404/gi-pricing-plan/issues/<n>/labels`, which
  returned **HTTP 403** *"Resource not accessible by personal access token"*. The token can
  create issues, but it cannot label them, comment on them or close them. The repository's
  `permissions` field reads `admin: true`, but that is the user's role, not the token's scope.
- **Close: not done.** The planned close was `gh issue close <n> --comment "WK-696 acceptance
  (c) test issue; recorded in the WK-696 closure record."`. It failed on both issues with
  *"Resource not accessible by personal access token (addComment)"*, exit 1. When re-read, both
  issues were `OPEN`, with 0 comments.

Labelling and closing #825 and #826 is therefore left to whoever holds a session with issue
write access. They are reported to the lead as pending, not done.

**Leg 2: the form structure GitHub's renderer needs.** No CLI can render an issue form, so
each form's YAML was validated against the fields the renderer reads. The checker is
`formcheck.py`. Its predicate, as stated in its docstring:

- each form parses to a mapping;
- `name` and `description` are non-empty strings, `labels` is a list of strings, and `body` is
  a non-empty list;
- every `body` item has a `type` in GitHub's set (`markdown`, `input`, `textarea`, `dropdown`,
  `checkboxes`);
- every item other than `markdown` has a unique `id` and a non-empty `attributes.label`;
- a `markdown` item has `attributes.value`, and a `dropdown` has `attributes.options`;
- `validations.required`, where present, is a boolean, and at least one field is required.

The run was `uv run python formcheck.py <tree>` at `df8e5811`, exit 0:

```text
bug.yml: name='Bug report' labels=['bug']
  [0] markdown
  [1] input     id=version       required=True  label='Version / tree'
  [2] textarea  id=reproduction  required=True  label='Steps to reproduce'
  [3] textarea  id=expected      required=True  label='Expected behaviour'
  [4] textarea  id=observed      required=True  label='Observed behaviour'
  [5] textarea  id=context       required=False label='Additional context'
  [6] input     id=related       required=False label='Related id (optional)'
question.yml: name='Question or suggestion' labels=['question']
  [0] dropdown  id=category      required=True  label='Category'
  [1] textarea  id=body          required=True  label='Details'
  [2] input     id=related       required=False label='Related id (optional)'
forms=2 violations=0
```

**Broken-input control.** Four faults were planted in copies of the forms:

- `labels` changed to a bare string;
- a duplicate `id`;
- `description` deleted;
- `type: select`, a type GitHub does not have.

The checker reported `violations=4`, exit 1, one line for each fault. It is stricter than
GitHub in one place: GitHub also accepts `labels` as a comma-separated string. That difference
cannot pass a bad form, so it does not weaken the check.

**The limit, stated.** Leg 1 proves that bodies in the forms' shape render with every field,
and that both labels exist on the repository. Leg 2 proves the forms carry what the renderer
needs. **The web form itself was never exercised.** The CLI does not run a YAML form and does
not apply a form's `labels:`. So neither leg shows that submitting through
`https://github.com/yes-404/gi-pricing-plan/issues/new/choose` renders these fields and applies
the label. Whether this proxy satisfies (c) is the deputy's call, by delegation. The other
option is a single submission through the web UI.

### (d) The README duplicates no roadmap or CLAUDE.md content

**The narrow predicate, RFC-898's wording for (d).** `README.md` at `df8e5811` was read line by
line against `CLAUDE.md` §1 and `docs/roadmap.md`.

- **`README.md:13-14` copies `CLAUDE.md` §1's first sentence word for word.** The README reads
  *"An open-source general insurance pricing platform for the UK/EU market — an open
  alternative to the established commercial pricing suites."* `CLAUDE.md` §1 opens with the
  same sentence, word for word (`CLAUDE.md:41-42` at `df8e5811`). RFC-898's constraint C1 allows the mission paragraph as *"a rewrite for a
  different audience … not an excerpt"*. This sentence is an excerpt.
- `README.md:14-19` is the rest of the paragraph. It restates the same mission in new prose,
  with the lifecycle list and the users and principles written as sentences. C1 allows this
  rewrite.
- `README.md:21-25` is the status section. It is a pointer to `docs/roadmap.md` and restates
  no status, so it is compliant.
- **`README.md:42-44` makes a dated status claim:** *"Not yet in force as of 2026-09-27 — no
  `SL-` row has been minted"*. It is true at `df8e5811`: `grep -c "^id: SL-" docs/roadmap.md`
  returns `0`. But it is a status fact whose home is the roadmap, and it goes stale on the
  first `SL-` mint. It is RFC-756's failure mode, and C1 forbids it. The same sentence appears
  in `CONTRIBUTING.md:50-52` and in `.github/PULL_REQUEST_TEMPLATE.md:14-15`, so one fact has
  three copies.

**Proposed verdict on the narrow predicate: not met, on two sentences.** Both fixes are
one-line edits with no design question:

- rewrite `README.md:13-14` rather than excerpt it;
- replace the dated `SL-` clause with a pointer.

### (d) The wider outsider read

These files were read as someone arriving from a search engine would read them, knowing
nothing of the team: `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, the PR template and both
forms.

**What works.** The README answers the outsider's four questions in order: what the project
is, where it stands, how it is built, and how to engage.

- It leads with the fact that an agent team builds the project, as RFC-898 P1 asks, and it
  does not hedge that fact.
- The tour stops all resolve.
- `SECURITY.md` is plain, honest and complete:
  - the scope is the codebase, with no deployment;
  - there is one private channel;
  - the 7-day acknowledgement matches [`RL-914`](../rulings/RL-00914-rfc-898-the-maintainer-s-three-policy-decisions-recorded-2026-08-30.md);
  - there is no bounty;
  - reporters are credited;
  - it refers to `docs/process/security-posture.md` in one direction only, as RFC-898 P2
    requires.
- `CONTRIBUTING.md` states "PRs by invitation" with its reason, which reads as transparency and
  not as gatekeeping. Its "issues are intake, the register is truth" paragraph is clear.
- Both forms are short, and their required fields are the minimum a triager needs.

**What an outsider trips on.** None of these blocks the close. Each is proposed to the lead
for a verdict.

1. **The README opens with the repository's metadata block.** GitHub renders a README's YAML
   front matter (`family: reference`, `status: active`, `owner: lead`, `relates: []`) as a
   table above the title. The outsider's first sight of the project is internal bookkeeping.
   The block came with the W37-6 migration (`71f5a220`, #782), which applied RFC-937's header
   convention to the root.
2. **Internal jargon reaches the public text unexplained.**
   - `W37-n` appears in `README.md:44`, `CONTRIBUTING.md:52` and the PR template.
   - `SL-`, `WK-`, `FD-`, `RFC-` and `RL-` appear in `CONTRIBUTING.md:34-36` and `:50-54`.
   - A newcomer who only wants to file an issue meets id grammar that `CONTRIBUTING.md` does
     not need.
3. **The public text describes as current a mechanism that has no instance.**
   `CONTRIBUTING.md:52-54` and the PR template's *"Work item"* comment say a PR with no slice
   *"gets one minted by the lead at triage, under the phase's standing `WK-` maintenance
   item"*. `document-ids.md` specifies that standing item (the paragraph after its §1.9 family
   table), but `docs/roadmap.md` has no such row at `df8e5811`. RFC-898's constraint C3 says
   nothing in these files may promise process the team does not already run.
4. **`CONTRIBUTING.md:43` shows `python3 scripts/doc-id.py next`,** which reads `origin/main`
   and not the contributor's tree. For an outside contributor on a fork, the command gives an
   id that can collide. For a public reader this is a low-stakes detail, and it is recorded
   rather than weighted.
5. **`SECURITY.md:8` names *"Phase 2's `WK-674`"*.** This copies roadmap membership, and it is
   true at `df8e5811` (the WK-674 row reads `phase: P2`). It is a pointer with a status fact
   attached. The file's update trigger, RFC-898's constraint C2, is WK-674's deployment, so the
   trigger and the copied fact go stale together. That is acceptable, and it is noted only
   because (d)'s spirit is "no copies".

**Proposed verdict, wider read: met, with observations 1–5 for the lead.** The files would
serve an outsider. Only the two (d) sentences above breach a stated acceptance predicate.

### (e) The close checklist carries the pointer-freshness line

`docs/process/checklists/work-item-close.md:34-36` at `df8e5811` reads *"Every close also checks
root `README.md`'s pointer freshness. Does this close change what the README's pointers resolve
to (roadmap phase, process spec location)? If yes, update the pointer — never the copied
content, which the README must not contain."* It was introduced by #495 (`01ba0bd2`), in the
checklist's pre-migration directory, and it survived the W37-6 move.

**Applied to this close:** closing WK-696 changes neither the phase nor any process-spec
location. The README's pointers therefore stay correct, and no pointer edit is owed.

### Impact matrix rows 7–9

- **Row 7** is item (e) above.
- **Row 8** is met. `docs/process/security-posture.md:25` opens *"**Public face.**
  [`SECURITY.md`](../../SECURITY.md) at the repository root is the outward …"*.
- **Row 9** is discharged by the WK-696 row itself, as that row says.

### Gate, register and counters

- **Gate.** This is a docs-only record. The docs checks (audit-docs, `doc-id.py check`,
  `doc-index.py --check`, `register-lint.py`) run on a detached copy of the committed tree. The
  rc and summary lines are in the PR body.
- **Register.** `grep -nE "WK-696|RFC-898|00898" docs/findings/register.md` at `df8e5811`
  returns nothing, so no open register row is filed against this Work.
- **Retry counters.** Read with `python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py
  show`, the counters have no WK-696 entry: none recorded.

## Verdict

**Proposed by the auditor. The lead adopts, amends or rejects each row.**

| Item | Proposed verdict | Owner | Event |
|---|---|---|---|
| (a) files and links | evidenced | — | — |
| (b), row 6, settings | pending: the deputy's dated line by delegation | the deputy | this record's follow-up commit |
| (c) test issues | **met by proxy, limit stated.** Legs 1 and 2 are evidenced, but the web form itself was not exercised. #825 and #826 are **not yet labelled or closed** (HTTP 403 on the token). | the deputy rules on the proxy; a holder of issue-write access labels and closes both issues | before this record's follow-up commit |
| (d) narrow predicate | **not met, on two sentences**: `README.md:13-14`, an excerpt of `CLAUDE.md` §1; `README.md:42-44`, a dated `SL-` status copy that recurs in two more files. The proposal is **fix before close**, by one-line edits. | the lead | this Work's closing PR, or a verdict of accept |
| (d) wider read | met; observations 1–5 go to the lead for a verdict | the lead | — |
| (e) checklist line | evidenced; no pointer edit is owed by this close | — | — |
| Rows 7, 8, 9 | evidenced | — | — |

The lead's reply decides whether these observations become register findings (`FD-`, ids from
the lead):

- (d)'s two sentences, if the verdict is accept rather than fix;
- observation 3, the promised maintenance item with no roadmap row;
- the CLI's silent label drop under an issue-create-only token. `gh issue create --label`
  exited 0 on a write that never landed. This is the auditor charter's trap: a `gh` write
  verified by its exit code and not by its artifact.

**Acceptance line:** _pending_
