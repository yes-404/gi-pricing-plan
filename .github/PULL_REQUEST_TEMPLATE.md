<!-- One Work = one pull request = one commit per slice, plus any review-fix commits on top.
     Title: a Conventional Commit line, e.g. `feat(frontend): platform administration views`.
     A core pull request of a single slice names its reason under "Commits". -->

Closes #<!-- Work issue number -->. Plan accepted in: <!-- link to the maintainer's "Plan accepted" comment -->

## Commits

Review commit by commit. The squash commit (main plus this branch) must pass the gate; each commit is reviewed on its own.

| # | Commit | Slice | Requirement ids | What it changes |
|---|--------|-------|-----------------|-----------------|
| 1 | `abc1234` | | | |

Changes since the last review round: <!-- per commit, or "first round" -->

Single-slice reason: <!-- core only: one of the four in CONTRIBUTING, "Pull requests", or "Series" -->

## Independent audit

<!-- Every finding of the independent audit, and what was done about each. See CONTRIBUTING, "Review". -->

## Paths

- [ ] Every changed file is inside the Work issue's permitted paths.
- [ ] This pull request touches a high-risk area (see CONTRIBUTING, "Review"): yes / no.
- Exceptions, each with a link to the maintainer's agreement: <!-- or "None" -->

## Gate evidence

Range: `origin/main...<branch>` at head `<sha>`

| Command | Exit code |
|---------|-----------|
| | |

Not run, and why: <!-- or "None" -->

## Changelog

<!-- One line a user would read. Write NONE if there is no user-facing change. -->

## Decisions

<!-- Decisions reached in the Work issue. Each one that binds the product is written to
     docs/adrs/ in this pull request. List them, or write "None". -->

## AI use and accountability

- AI use: <!-- NO, or YES with the tool, the model version and what it did (code, tests, docs) -->
- [ ] A person has read and understood every change in this pull request.
  <!-- Ticked only by that person. No agent ticks it, and it is never ticked to get a pull request through. -->
- Review the change had instead, if the box is unticked: <!-- e.g. the independent audit, the cross-review, the gate; or "Not applicable" -->
- Accountable person: @<!-- the person who answers review questions and owns defects -->

## Notes for the reviewer
