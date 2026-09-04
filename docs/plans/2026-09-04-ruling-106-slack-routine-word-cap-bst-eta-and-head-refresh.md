# W37-6 — Ruling 106: the Slack routine (2026-09-04)

## Ruling 106 — a 100-word cap, a BST clock time in the ETA, and a refresh on every `origin/main` move

<!-- Structural note: this heading exists so `_discover_multi_ruling_files`
     (`_RULING_HEADING_RE`, `^##\s+Ruling\s+(\d+)`) discovers this record as an `RL-` draft
     rather than falling through to `_discover_plain_plans`'s `PL- kind: leaf, owner: planner`
     catch-all — the defect F96 (`docs/audit/findings/F96.md`) was filed for. -->

**Ruling number derivation, run by the lead in its own checkout at `origin/main` = `ad51906`:**

```
git grep -ohE '^## Ruling [0-9]+' origin/main -- docs/ | grep -oE '[0-9]+' | sort -n | tail -1
  → 105
git grep -c 'Ruling 106' $(git branch -r | grep -v HEAD) -- docs/ .claude/ scripts/
  → only this record's own branch
```

**106 is the next free number**, derived rather than assumed.

## Authority

The maintainer, 2026-09-04, verbatim (relayed by the deputy under the delegation of
2026-09-03): *"request the lead to rule for slack routine in long term: message limited to
100 words, ETA should include BST clock time estimation, update ETA when git head
changes."* Clarified the same day: *"eta update is a work of the lead."*
`~/gi-pricing-plan.local/channel/to-lead.md` carries both instructions (search "Slack
routine" and "clarification of the Slack-routine rule 3"); this record is the filing they
asked for, not a restatement of authority the record does not itself carry.

## The three rules

**1. A routine post is at most 100 words**, counted over the whole message body
(`format_routine_post`'s output — headline, PR list, notes, everything). `reporter.py`
enforces it: over the limit, it truncates the *non-headline* sections first, never the ETA
headline, and appends `(+N words cut)`. The headline is exempt from truncation because a
half-cut ETA is worse than a full one with less context around it.

**2. The ETA headline names a BST clock time**, e.g. *"W37-6 run: earliest 14:30 BST
2026-09-04, on (g) triage landing"* — never a bare duration ("~2 hours", "soon"). `get_eta`
rejects a headline carrying no `HH:MM BST` (or `HH:MM BST YYYY-MM-DD`) token and posts *"ETA
headline malformed — no clock time"* in its place, rather than posting a headline the rule
does not accept. The reporter never computes the time itself — `reporter.md`'s own item (1)
and `eta.md`'s header ("the lead owns this number; the reporter publishes it") stand
unchanged; this rule constrains the *shape* the lead must write it in, not who writes it.

**3. The ETA is refreshed on every change of `origin/main`'s HEAD, and that refresh is the
lead's own work, not the reporter's** (the maintainer's clarification, verbatim above).
Mechanically: `eta.md` carries a `main: <sha>` field beside `Updated:`. Each reporter cycle
compares that recorded sha to `git rev-parse origin/main`; if they differ, the post reads
*"ETA stale — main moved to `<sha>` at HH:MM BST, ETA not yet re-derived"* instead of the
carried-forward headline, until the lead re-derives it. The lead's own obligation: every
merge advances `origin/main`, so every merge is followed — before the next reporter cycle —
by writing a fresh `eta.md` (headline with its BST clock time, `Updated:`, `main: <sha>`) in
the same act as the merge and its ledger line. The `main:` comparison and the stale marker
are the **backstop that makes a missed refresh visible to a reader**, not the mechanism
itself; a post carrying that marker records a lead lapse, not a reporter one. The pre-existing
2-hour clock-staleness check (`get_eta`'s `Updated` age) is a second, independent trigger and
is unchanged by this rule.

## Where this lands

- **This record** — the ruling, dated and frozen at this date per `docs/plans/README.md`.
- **`.claude/skills/reporter-cycle/SKILL.md`** — the HOW: the 100-word enforcement in
  `format_routine_post`, the BST-clock-token requirement and the malformed-headline message
  in `get_eta`, the `main:` field and staleness marker in `get_eta`/`main()`. `Verified` date
  refreshed there in the same PR as the code change, per `CLAUDE.md` §12.
- **`.claude/roles/reporter.md`** — a one-line pointer beneath item (1) of "What goes in",
  naming this ruling as the source of the three constraints, per DP-6's shape for a charter
  edit (a dated maintainer instruction, not a restatement).
- **`eta.md`'s own header** — gains the `main:` field description alongside `Updated:`.

## Acceptance — the violation that must become detectable

*Violation: a routine post over 100 words.* Broken-input proof: a deliberately >140-word
body posts at ≤ 100 with the `(+N words cut)` marker, headline intact.

*Violation: an ETA headline with no BST clock time.* Broken-input proof: a headline with a
bare duration ("in 2 hours") is rejected and replaced with the malformed-headline message,
never posted as given.

*Violation: a post after `origin/main` has moved that still carries the old ETA with no
stale marker.* Broken-input proof: advance a fixture `origin/main` past the recorded
`main:` sha with no accompanying `eta.md` update; the next cycle's post must carry the
stale-ETA line, not the carried-forward headline.

*Violation: the reporter computing an ETA itself* (unchanged from the existing rule;
restated here because this ruling touches the same code path).

## What this does not decide

Whether a post that would read fine under the old (unbounded) format is meaningfully worse
truncated — a matter of taste the maintainer's instruction already settled by naming the
number; not reopened here. The exact wording of the malformed/stale marker strings is the
implementer's within the constraints above, not re-litigated here line by line.

## Acceptance Standard

Discharged when a PR lands implementing all three rules in `reporter-cycle`'s scripts, with
the three broken-input proofs as tests, `SKILL.md`'s `Verified` date refreshed, and
`reporter.md`'s pointer added — one PR, `ci-watcher` on it, merged under `lead.md`. This
ruling record is accepted when the lead (this session, or its successor) merges that PR;
its substance binds from that point, same as any other ruling record in this project.
