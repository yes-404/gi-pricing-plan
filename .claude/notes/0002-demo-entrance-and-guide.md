# NT-0002 — Demo entrance, with a guide to what is testable

| | |
|---|---|
| **Raised** | 2026-08-15, maintainer |
| **Status** | `open` — blocked on W6a |
| **Deliverable** | **Spec change first, then code.** The capability is not currently specified (`CLAUDE.md` §0) |
| **Owner** | maintainer |
| **Lands in** | `docs/specs/07-platform.md` beside FR-PLAT-37 · then `frontend/`, `deploy/`, `examples/` |
| **Sequencing** | W7, after W6a completes |

---

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
seed through the real Job path (W7a). What does **not** exist is the one command that starts
all of it together, and the page that says what is worth clicking.

Four things to settle before building it:

- **It is unspecified, so the spec comes first.** No requirement asks for a demo entrance.
  The natural anchor is FR-PLAT-37 — "one command to a working system" — which W7a delivered
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

## Next step

Nothing until W6a closes. Building the guide now would mean writing it against views that do
not exist yet.

## Original wording

As raised by the maintainer. Grammar and punctuation corrected; wording, structure and
meaning are theirs.

> Now that the frontend interface is built, add a user-testing interface that runs as a
> demo, so that the user can reach a web entrance and physically test the functionality that
> has been built. Keep a testing entrance in place, together with a mini guide telling the
> user which parts can be tested.
