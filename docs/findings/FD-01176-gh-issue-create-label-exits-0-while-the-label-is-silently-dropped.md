---
id: FD-1176
family: finding
title: gh issue create --label exits 0 while the label is silently dropped
status: active
created: 2026-09-28
owner: auditor
tree: df8e5811a151a99c7317690faf9278a6dc3400be
corrected_by: []
relates: [CR-1174, WK-696]
---

# FD-1176 — gh issue create --label exits 0 while the label is silently dropped

The auditor filed this finding on 2026-09-28 in the WK-696 closure record's PR, on the lead's
instruction. It was found while filing the (c) test issues that `CR-1174` records. The deputy
accepted it the same day, as the lead relayed.

## Finding

The acceptance item is RFC-898 §8 (c), one test issue through each form. `gh issue create
--label <name>` exited 0 on both test issues, but GitHub applied no label. The personal access
token this team uses can create an issue. It cannot label, comment on or close one: each of
those returns HTTP 403. `gh api repos/yes-404/gi-pricing-plan --jq .permissions` reports
`admin: true`, but that field describes the user's role on the repository, not the token's
scope. It is therefore no evidence that a write will land.

This belongs to the class the auditor charter names: *"verify a `gh` write against the
artifact it claims to have changed, never against its exit code"*. Here the exit code is 0 on
a create that half-landed. The issue exists, and its label does not.

## Evidence

**Reproduction.** These were run on 2026-09-28 with gh 2.46.0 and the `yes-404` token. The
body files are the ones `CR-1174` §(c) describes.

1. `gh issue create --repo yes-404/gi-pricing-plan --title "[test] WK-696 acceptance (c):
   bug.yml (Bug report)" --label bug --body-file issue-bug.md` printed the URL of issue #825
   and exited 0. The same command with `--label question` created #826 and also exited 0.
2. `gh api repos/yes-404/gi-pricing-plan/issues/825 --jq '[.labels[].name]'` returned `[]`.
   The GraphQL `issue(number:825){labels{nodes{name}}}` query returned `[]`, and
   `…/issues/825/events` returned `[]`. The reads for #826 were the same.
3. `gh api -X POST repos/yes-404/gi-pricing-plan/issues/825/labels -f 'labels[]=bug'` failed
   with HTTP 403, *"Resource not accessible by personal access token"*. The same call on #826
   gave the same result.
4. `gh issue close 825 --repo yes-404/gi-pricing-plan --comment "…"` exited 1 with *"GraphQL:
   Resource not accessible by personal access token (addComment)"*. The same call on #826 gave
   the same result. When the issues were re-read, both were `OPEN`, with 0 comments and
   `labels: []`.
5. `gh api repos/yes-404/gi-pricing-plan --jq .permissions` returned
   `{"admin":true,"maintain":true,"pull":true,"push":true,"triage":true}`.

**The lead's session holds the same token.** The lead confirmed this, so the result does not
depend on which session made the calls.

## Disposition

**Deferred with an owner — the lead.** The deputy accepted this on 2026-09-28, and the lead
relayed it. Event: the next edit to the `git-hygiene` skill.

That edit should record two rules:

- read back every `gh` write, labels included, and never trust the exit code;
- `/repos` `permissions` states the user's role, not the token's scope.

The maintainer's decision to grant issue-write scope to the token discharges the operational
half, which is labelling and closing #825 and #826. It does not discharge the skill half.
