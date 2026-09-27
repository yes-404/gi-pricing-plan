---
id: FD-1008
family: finding
title: the ledger convention has lapsed; a frozen plan requires it anyway, and nothing detects the disagreement
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F70.md
---

# F70 — the ledger convention has lapsed; a frozen plan requires it anyway, and nothing detects the disagreement

Evidence essay for the register row self-named `(F70)` in `docs/findings/register.md`. The
finding: three governing sources disagree about whether a per-slice ledger file is part of
this project's process, the practice behind it has visibly stopped, and a currently-merged,
frozen plan still writes its acceptance line against the lapsed convention — with no check
anywhere that would catch the gap.

## Provenance

Relayed by the lead, self-flagged as measured under pressure ("I have been wrong six times
tonight and you have caught several"). Verified independently below in two rounds: this
essay's first reading rejected one detail of the relay for lack of a findable artifact,
which was itself a real error, corrected in its own section below once a later,
independently-discovered artifact (a squash-merge commit message) corroborated the relay's
substance. Both the original claim and the correction are kept, dated, rather than the
first quietly replaced by the second.

## The three sources, each verified directly

**1. Sixteen ledger files exist, and the practice stopped nine days ago.**

```
$ git ls-tree -r --name-only origin/main -- docs/plans | grep -cE '\-ledger\.md$'
16
$ git ls-tree -r --name-only origin/main -- docs/plans | grep -E '\-ledger\.md$' | sort | tail -1
docs/plans/PL-00780-w32-11-ledger-certificate-floors-and-two-generated-sides.md
$ git log origin/main --format="%ad %s" --date=short -- docs/plans/*-ledger.md | sort -r | head -1
2026-08-24 test(w32-10): give three shipped behaviours the ability to fail (#154)
```

Sixteen files, newest dated and last touched 2026-08-24 — confirmed both by filename and by
the commit history of every `-ledger.md` path. That span covers the entire post-2026-08-29
process adoption (RFC-840/841) and all of WK-693 through WK-696.

**2. `docs/process/delivery-process.md` — CLAUDE.md §15's named authority for "the process"
— does not contain the word, in any case.**

```
$ git grep -ci "ledger" origin/main -- docs/process/delivery-process.md
(no output, exit 1 — zero matches, case-insensitive)
```

**3. The currently-merged map plan uses it ten times, including inside a frozen slice's own
acceptance line.**

```
$ git grep -oi "ledger" origin/main -- docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md | wc -l
10
```

The load-bearing instance, `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`, Slice
W37-1:

> **Acceptance:** `python3 scripts/audit-docs.py` exits 0; `document-ids.md` §1.1-§1.13 is
> byte-identical to RFC-937 §1.1-§1.13 modulo the heading level shift, **verified by a diff
> recorded in the slice's ledger**; thirteen template files exist and each parses under the
> field set §1.5 declares.

This plan is frozen (merged as PR #557, `106e322`) and W37-1 is dispatched against it
verbatim — the acceptance line names an artifact the executor has no ledger convention
active to produce.

**A fourth source, not in the original relay, makes the disagreement sharper.**
`.claude/skills/subagent-driven-development/SKILL.md` — the executor skill W37-1 actually
runs under — treats the ledger as the central, load-bearing artifact of its whole method:
"the ledger is what survives compaction," "trust the ledger and `git log` over your own
recollection," "every adjudication is a ledger entry," with an explicit anti-pattern entry
rejecting "ledger bookkeeping is overhead" as an excuse. This is not a document that treats
the ledger as optional or legacy; it is the one place the convention is described as
mandatory and still fully alive in text, while the sixteen files on disk say the practice
stopped nine days ago and the authoritative process document never adopted the word at all.

## What the W37-1 execution actually did — two readings, taken in the order they were verified

**First reading (2026-09-02, PR #562 still open).** PR #562 created no `docs/plans/
*-ledger.md` file (`gh pr view 562 --json files` listed 14 files, all under
`docs/_templates/`, `docs/process/document-ids.md` and `docs/README.md` — none a ledger),
and its Summary and Verification sections carried the diff-verification substance the
acceptance line asks for. **Searched directly and found nothing**: PR #562's body (`gh api
repos/.../pulls/562 --jq '.body'`, grepped case-insensitively for "ledger", "dead
convention", "lapsed", "declined" — zero matches), its one commit message (same search,
zero matches), and its comments (`gh pr view 562 --json comments` — empty). On that
evidence alone, this essay first concluded the gap had been "worked around, silently."

**That conclusion was wrong, and corrected below on two independent grounds — the
lead's relayed evidence, and this review's own later re-check of the same PR after it
merged.**

**Corrected 2026-09-02.** The lead reports the executor's session report read, in part:
*"the plan's acceptance line asks for the byte-identity diff 'recorded in the slice's
ledger.' I checked: delivery-process.md (the current, authoritative process doc) never
mentions ledgers at all, and no `docs/plans/*-ledger.md` has been filed since 2026-08-24 —
nine days of silence... Reviving that file convention unilaterally seemed likely wrong, so I
recorded the diff verification in the PR body instead and I'm flagging this rather than
guessing."* **This specific quotation is not independently verifiable by this review** — it
comes from a session-level report this review has no tool access to, which is itself the
crux of what follows.

**But it is now corroborated by a durable artifact this review found independently, not
relayed.** PR #562 merged at `553bbef`, 2026-09-02T00:38:22Z, *after* this essay's first
reading. Its squash-merge commit message — read directly via `git show --format="%B"
553bbef`, not taken from any PR body — states:

> "Two findings from the executor, both adopted. ... Second, the plan's acceptance line asks
> for the byte-identity diff 'recorded in the slice's ledger', but 16 ledger files exist with
> the newest at 2026-08-24 and delivery-process.md contains the word 'ledger' zero times —
> the convention lapsed nine days ago, spanning the whole post-2026-08-29 adoption. The
> executor declined to revive it unilaterally and recorded the diff in the PR body instead.
> Ruled by the lead: proceed without a ledger, because reviving a lapsed convention inside
> the very work that is about to define `LG-` as a first-class family would create files in
> a form RFC-937 immediately replaces. The underlying gap — process document, skill and
> filed plans disagreeing about whether ledgers exist — is routed to the auditor as a
> finding."

Independently checked: the two facts this row verified itself (16 files, newest 2026-08-24;
`delivery-process.md` zero mentions) match the merge commit's own restatement exactly, and
the merge commit's third-person summary is consistent in substance with the executor's
first-person report the lead quoted, though phrased differently — the kind of independent
consistency a single copy-pasted source would not need to produce.

**The corrected shape, precisely.** The executor did flag it, correctly and in detail. That
flag reached the lead through a channel this review cannot check — a session report, not a
committed artifact — exactly the gap this project already filed a record about once tonight
(the maintainer's precedence ruling existing only in a live conversation until refused as
unverified; see this session's own exchange on that point). **Between the executor's report
and 2026-09-02T00:38:22Z, the flag existed nowhere this review, or any future reader, could
check.** It became durable specifically at squash-merge time, in the commit message — which
means its durability depended on whoever merged the PR choosing to write a fuller commit
message, not on anything structural. A different merge, with a shorter message, would have
left the same correct, well-reasoned flag exactly as unrecoverable as this essay's first
reading found it. **The gap this finding is actually about is not "the executor was
silent" — confirmed false — it is "a correct escalation's durability was one commit message
away from being lost," which is the lead's exposure, not the executor's, and the lead asked
that this row say so plainly.**

## The lead's disposition (recorded here so this row cites it rather than reopening it)

The lead ruled *proceed without a ledger* for WK-697's slices, under the replan-vs-proceed call
(`delivery-process.md` §5 step 4). Reasoning, as given: hand-reviving a lapsed convention in
the middle of the work that is about to define `LG-` as a first-class family (its own
directory, its own lint, an owner in §1.6) would create files in a form RFC-937 is about to
replace, and what a ledger is *for* — a record of what was checked and decided — is already
durable in the PR body and the eventual squash commit. **The convention returns when
RFC-937 lands it as a family.** This is a disposition on *this slice's* instance, not a fix
to the underlying disagreement, and the lead was explicit that it should not be read as one.

## Why this is F58's shape, checked rather than asserted by analogy

F58 (`docs/findings/register.md`): `.claude/roles/watcher.md` states the watcher writes runtime
state "each cycle"; verified directly that no process anywhere invokes the script; disposal
text: "a reader of `watcher.md` alone believes a mechanism runs that does not." The same
predicate holds here on the same kind of check: a reader of `subagent-driven-development`
alone believes ledgers are a live, mandatory, currently-practiced artifact. They are not —
not for nine days, across two full workstreams and the current one — and the document
holding the currently-adopted process (`delivery-process.md`) does not mention them at all,
so there is no single place a reader could go to discover the practice had stopped. F58's
gap is a wiring failure (a script exists, nothing schedules it); this one is a convention
drift (a skill still asserts the practice, the authoritative process document never adopted
it, and recent plans keep citing it) — different mechanism, same reader-facing failure: the
governing text and the world disagree, and nothing routinely says so.

## The mutation that must become detectable

Checked directly, not assumed: none of `scripts/audit-docs.py`, `scripts/register-lint.py`,
`scripts/register-owed.py` or `scripts/scope-audit.py` contains any check that reads a
plan's acceptance-line prose and confirms a ledger it names actually exists.
`audit-docs.py`'s only awareness of the word is `_PLAN_KIND_EXCLUDED_SUFFIXES` recognising
the `-ledger.md` filename *suffix* so check 28 does not wrongly demand an Acceptance
Standard heading from a ledger file that has one — a filename-shape check with no bearing on
whether a *named* ledger exists.

**Today**: a plan filed with an acceptance line naming a ledger, with no ledger ever
produced anywhere in the tree, passes every check in the gate — `audit-docs.py` exits 0,
`register-lint.py` has no cell to check, `scope-audit.py` has no requirement id to attach it
to. W37-1 is not a hypothetical demonstrating this; it is the live instance.

## Scope of this finding

- **Not fix-before-close.** The lead's disposition already resolves WK-697's own exposure; this
  row is the underlying gap the disposition explicitly does not fix.
- **Not a criticism of the W37-1 executor.** Corrected above: the executor identified the
  exact same three-source disagreement this row independently verified, declined to revive
  a lapsed convention unilaterally, recorded the substantive diff verification in the PR
  body, and escalated the deviation rather than guessing — precisely the right call on all
  four points. Nothing in this row is against that judgment.
- **The exposure named is the lead's, at their own request.** A correct, well-reasoned
  escalation reached the lead through a channel this review cannot check (a session report)
  and, for a period ending only at PR #562's squash-merge (`553bbef`,
  2026-09-02T00:38:22Z), existed nowhere any future reader could verify it. It became
  durable because that merge commit's message happened to be written in full; a terser one
  would have left it exactly as unrecoverable as this essay's first reading found it. That
  is not a property of the ledger convention — it is a property of how this team's
  escalations reach the written record, and the lead identified it as their own gap rather
  than the executor's.
- **Proposed disposition** (a proposal, not a verdict — CLAUDE.md §13's four verdicts and the
  merge stay the lead's): **carry forward with a trigger**, most plausibly discharged when
  RFC-937 lands `LG-` as a first-class family with its own directory, lint and §1.6 owner —
  at which point "does a named ledger exist" becomes a mechanically checkable predicate the
  same way check 28 already checks for an Acceptance Standard heading. Until then, the
  narrower, cheaper interim option is a `scripts/scope-audit.py`- or `audit-docs.py`-level
  warn-only check: any *frozen* plan's acceptance text naming "ledger" gets a note (not a
  failure) if no `docs/plans/<matching-slug>-ledger.md` exists — surfacing exactly this
  drift the next time it happens, without inventing enforcement for a convention already
  admitted to be mid-supersession. Which of the two (wait for RFC-937, or a cheap interim
  warn-only check) is worth doing now is the lead's call, not filed here as a decision.
