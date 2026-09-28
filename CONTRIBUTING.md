# Contributing

## Issues and questions are welcome

Bug reports, questions about the specs or the delivery process, and suggestions are all
welcome — open an issue using one of the templates, or a blank issue if neither fits.

## Pull requests are by invitation, for now

**Issues welcome, PRs by invitation.** This repository is built by a documented agent
team (`docs/process/delivery-process.md`) under a standing rule that only pull requests
authored by the maintainer's own account are merged. Inviting unsolicited pull requests
would set an expectation the process cannot honour: an outside PR cannot enter the
delivery process as it exists today, so it would sit unmerged regardless of quality.

Instead: **open an issue describing the change first.** If it's wanted, you'll be invited
to open a PR for it, or the change will be picked up by the team. This posture will be
revisited once external contributors are a regular thing — code of conduct, code
ownership, and a sign-off requirement are the obvious next steps, deliberately not set up
before there is anyone for them to govern.

The pull request template exists anyway — it's what invited external PRs and the team's
own agents both use.

## Issues are intake, the register is truth

A substantiated issue is triaged into the project's internal tracking (the findings
register at [`docs/findings/register.md`](docs/findings/register.md), an open question, or
a task) by the team. From that point, the issue is a pointer to the internal artifact that
owns the work, not a second place where the same finding is tracked — so don't expect a
running commentary on the issue itself; expect it to link to where the work actually lives,
and to close or be updated when that does.

A finding is filed as an `FD-` document under `docs/findings/`, with a row added to
`register.md`. A proposal that would change a standing decision is filed as an `RFC-` under
`docs/rfcs/`. A decision already made is recorded as an `RL-` ruling under `docs/rulings/`.

## Ids, branches, and PR titles

A new document gets its id from the next free integer in the project's single sequence:

```bash
python3 scripts/doc-id.py next
```

That integer is the document's id for life — it never gets renumbered, only marked
superseded. The filename carries it padded to five digits, and the directory it lives in
names its family (`docs/process/document-ids.md` has the full family table).

Branches and PRs name the slice they deliver: `sl-<n>-<slug>` and `SL-<n>: <title>`. Until the
first `SL-` row is minted, a PR names its `WK-` work item instead. A PR with no slice at all (a hotfix, an external contributor, a
dependency bump) gets one minted by the lead at triage, under the current phase's standing maintenance Work
(`docs/roadmap.md`, the `WK-` row titled "standing maintenance"). Bot-authored PRs are exempt.

## Where to start reading

[`README.md`](README.md) is the front door. `docs/specs/00-overview.md` has the system
context and glossary if you want to understand what a term means before using it in an
issue.
