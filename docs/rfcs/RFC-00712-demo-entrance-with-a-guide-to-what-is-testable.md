---
id: RFC-712
family: proposal
kind: process
title: Demo entrance, with a guide to what is testable
status: closed                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-08-15
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this RFC itself corrects a frozen record
relates: []                     # ids only
was: docs/notes/0002-demo-entrance-and-guide.md
---

# Demo entrance, with a guide to what is testable

## The request

The frontend shell and the `/data` views exist, but there is no single place a person can
open to exercise what has been built by hand. Add one:

1. **An entrance** — a documented, single-command path from a clean checkout to a browser
   window authenticated against a seeded workspace.
2. **A short in-app guide** on that entrance page, stating what can be tested today, the
   route that tests it, and — equally — what is present but not yet functional.

The audience is the maintainer doing manual acceptance, not an end user.

**Why:** Phase 1a's exit criterion currently passes headless, in
`backend/tests/test_data_jobs.py::test_the_failure_loop_then_validated`. A passing test and
a person driving the screen are different evidence, and only the second one finds the things
a test was never told to look for.

## Assessment — Claude, 2026-08-15

**Most of the parts already exist; the missing piece is smaller than the note implies, and
sharper.** Present today: the compose stack, `GIP_DEV_AUTH_ENABLED=true` on the API, the
generated client and app shell (#49), the validation report view (#50), and the freMTPL2
seed through the real Job path (WK-666). What does **not** exist is the one command that starts
all of it together, and the page that says what is worth clicking.

Four things to settle before building it:

- **It is unspecified, so the spec comes first.** No requirement asks for a demo entrance.
  The natural anchor is FR-439 — "one command to a working system" — which WK-666 delivered
  only the data half of. Read it as extending that requirement rather than inventing a new
  surface, or the entrance becomes an unowned page nobody maintains.
- **A hand-written capability list goes stale immediately, and stale is worse than absent
  here** — the guide's whole purpose is telling the maintainer what to trust. Bind it to
  something: link the route table to the published contract in `docs/contracts/`, and make
  "update the demo guide" an item in `CLAUDE.md` §13 step 7, so a workstream cannot close
  while the guide still describes the previous state. It must not restate capability from
  memory — the same rule as `CLAUDE.md` §2's seam: nothing hand-writes a shape that already
  exists.
- **Gate it on the refusal that already exists.** `Settings.dev_auth_enabled`
  (`backend/src/app/config.py`) is `False` by default and *raises* if set in a deployed
  environment, so the entrance should hang off that flag rather than invent a second switch.
  A page that lists routes and pre-authenticates a session is a genuine hole if it ever
  ships.
- **Phase honesty.** The guide's "not yet functional" column is the valuable half. It should
  be derived from the roadmap's status table, not written freehand, or it will quietly claim
  more than the repository has — precisely the failure `CLAUDE.md` §13 exists to prevent.

## Acceptance criteria

- One documented command brings up the stack, API and frontend with freMTPL2 seeded.
- The entrance page lists each testable route with its current state.
- The whole path is refused when `GIP_DEV_AUTH_ENABLED` is unset.
- Phase 1a's exit criterion — including the validation-failure loop — is drivable by hand,
  start to finish, from that page.

## Where it went

Accepted by the maintainer 2026-08-15. The deliverable was **spec change first**, and that
half is done:

| Outcome | Landed in |
|---|---|
| The entrance, extending FR-439 and gated on `dev_auth_enabled` | `07` FR-408 |
| The guide, derived from the contract and the roadmap rather than written | `07` FR-409 |
| Keeping the guide current as a closure step | `CLAUDE.md` §13 step 7 |
| The work itself, sequenced | `docs/roadmap.md`, WK-665 |

All four points from the assessment are carried by the requirements rather than left here:
it extends FR-439 instead of inventing a surface, the capability list is derived from
`docs/contracts/` and the roadmap, the whole path hangs off the refusal that already exists,
and the "not yet functional" column comes from the status table.

## Where the code went — WK-667, 2026-08-15

WK-663 closed, so the block lifted. Split from WK-665 into Phase 1a for the reason WK-666 was: the
entrance needs no model, and Phase 1a's exit demo needs the entrance.

| Outcome | Landed in |
|---|---|
| One command to a browser | `scripts/demo.py` |
| The entrance | `frontend/src/views/DemoView.vue`, routed at `/demo` |
| The guide, derived on every request | `backend/src/app/demo/guide.py`, `GET /api/v1/demo/guide` |
| The shapes it returns | `packages/model-schema/src/model_schema/demo.py` (ADR-704) |

All four points of the assessment held. The guide restates nothing: every line is one file
agreeing with another, so there is no stored copy to drift and no drift check to remember.
Measured 24 s cold against NFR-529's 300 s.

The note's own prediction was right in an unexpected way — building it *did* find things,
but not in the guide. Three defects came out of running the command rather than testing it:
Ctrl-C orphaned the frontend, Vite silently moved ports and the command advertised a server
it had not started, and buffered output hid the final banner. The closure record has them.

## Original wording

As raised by the maintainer. Grammar and punctuation corrected; wording, structure and
meaning are theirs.

> Now that the frontend interface is built, add a user-testing interface that runs as a
> demo, so that the user can reach a web entrance and physically test the functionality that
> has been built. Keep a testing entrance in place, together with a mini guide telling the
> user which parts can be tested.
