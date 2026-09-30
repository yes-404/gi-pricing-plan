---
id: FD-1280
family: finding
title: A prepared ruling has no permitted status, so every prepared RL PR fails check 33
status: active
created: 2026-09-30
owner: auditor
tree: 880feb499eddb9e854c525770e95fb19373a2311
corrected_by: []
relates: [WK-1178]
---

# FD-1280 — A prepared ruling has no permitted status, so every prepared RL PR fails check 33

## Finding

**Severity: low.** `document-ids.md` §1.2 gives the Ruling family the status subset
`active → superseded | retired` and no `draft`. The decision-maker's prepared rulings
(PRs #935 to #942, each titled *PREPARED, NOT RULED*) carry `status: draft`, a word §1.2a
defines (*"exists, not yet authoritative or accepted"*) and `RL` does not use. `audit-docs.py`
check 33 refuses it. The refusal is a fail-safe: a `draft` ruling cannot be mistaken for a
ruling in force. It is currently deliberate: the header comment of the records in #935, #937 and #939 says so
(`NOT a permitted RL status`); the other five carry no such comment. It is also undocumented outside those three records: neither §1.2 nor `RL.md` says how a
ruling is prepared before it is made. This record does not decide which side moves: that is
the maintainer's, and `CLAUDE.md` §0 requires the question be raised, not resolved silently.

## Evidence

At `origin/main` `880feb499eddb9e854c525770e95fb19373a2311`, and at each PR head below (`git worktree add --detach` at the
fetched `refs/pull/<n>/head`, then `python3 scripts/audit-docs.py`, rc quoted).

- `docs/process/document-ids.md:38-57`, §1.2, Ruling row: *"Status subset (§1.2a)"* cell
  reads `active → superseded | retired`. The Plan, ADR, Workflow, Research and Work rows carry
  `draft`; the Ruling, Ledger and Closure rows do not.
- `scripts/audit-docs.py:2017` `_STATUS_SUBSET` (the `RL` entry is at `:2029`), read at `:2099-2100`: a header whose status
  is outside the family's subset is a failure.
- All eight prepared-ruling PR heads exit **rc=1**, and the FAILED block of each holds exactly
  two lines, the check 31 working-id gap (expected under `CLAUDE.md`'s working-id convention) and
  one check 33 line per RL file:
  - #935 `aa38bd4f`: `check 33: docs/rulings/RL-[09901]-…: status 'draft' is not in ruling's subset ['active', 'retired', 'superseded']`
  - #936 `58d0284d` (RL-[09852]), #937 `110a7fcb` (RL-[09902]), #938 `f04e50d3` (RL-[09851]),
    #939 `7224cec7` (RL-[09903]), #941 `ca949339` (RL-[09855]), #942 `5c2e55e6` (RL-[09856]):
    the same check 33 line, one file each.
  - #940 `aa67d32f`: the same line twice (RL-[09853], RL-[09854]).
- **Two premises in the request that filed this record did not hold, corrected here.**
  (1) *Check 37 behaves the same way*: it does not. Check 37 appears in none of the eight FAILED
  blocks (`grep -c 'check 37'` over the text from `FAILED` on prints 0 each time).
  (2) *There is no RL template*: `docs/_templates/RL.md` exists (last touched by
  `a8b31ab8`, PR #661). Its `status:` line reads `active   # active → superseded | retired
  (§1.2a) — a ruling opens active`, so the template also has no draft path.

## Disposition

**Carry forward, unowned**, proposed by the auditor on 2026-09-30; the register row's
`decision:` is the lead's. The resolver is the maintainer (an amendment to a
`document-ids.md` status subset, and the family's frozen-on-file rule, are the maintainer's).
Options, with a recommendation and no decision:

- **(a) Add `draft` to the Ruling row's subset** (`draft → active → superseded | retired`), as
  `PL`, `ADR`, `WF` and `RS` already have it, and say in `RL.md` how a prepared ruling
  opens. Cost: a frozen family gains a mutable first state, and check 34's freeze predicate has
  to say whether a `draft` RL is frozen. Gain: the prepared record and the ruling are one
  file, promoted by one status edit.
- **(b) Keep the fail-safe and annotate it** in `open-questions.md`. Cost: every prepared-ruling
  PR is red at check 33 by design until minted, which trains the team to read a red gate as
  expected, the failure mode of a standing-FAIL row hiding its own regression.
- **(c) File prepared rulings in a family that already has `draft`** (a `PL`, `kind: review`
  or `RS`), then mint the `RL` at the ruling. Cost: the prepared text is re-filed at the ruling.

**Recommendation: (a).** The prepared ruling is what the decision-maker rules on, and the
promotion is what dated-ruling provenance needs. Event that discharges it: the maintainer's
ruling on which option, then the `document-ids.md` amendment and a template line under
`spec-change` procedure. If unowned at the next `CLAUDE.md` §14 review, the row decays to
that review.

*Square brackets in `RL-[99nn]` are inserted so this record does not cite the prepared rulings' working ids as live ids under checks 31 and 32; the real ids carry none.*

*Disclosure: this record was drafted under working id 9910 and minted as FD-1280; the working id survives only in this line and in PR #947's history.*
