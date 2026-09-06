---
id: CR-718
family: closure
kind: work
title: WK-667 — The demo entrance: closed
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-15
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/closure-records.md
---

### WK-667 — The demo entrance: closed 2026-08-15

**Scope, derived from `07` §3.9 before writing anything: two requirements** — FR-408
(one documented command from a clean checkout to an authenticated browser) and FR-409
(a guide to what is testable, derived rather than written). Both were added by `RFC-712`,
accepted 2026-08-15, whose deliverable was *spec change first*; this is the code half.

Split from WK-665 into Phase 1a for the reason WK-666 was: the entrance needs no model, and
Phase 1a's exit demo needs the entrance. What remains in WK-665 is the half that needs a
fitted model.

| Deliverable | Evidence |
|---|---|
| One command | `uv run python scripts/demo.py` — compose, migrations, freMTPL2 seeded through the real Job path, API, frontend, development identity for the seeded workspace, and the URL |
| The entrance | `/demo`, listing what is built, what is not, and the routes that can be opened without an id |
| The derived guide | `GET /api/v1/demo/guide`, built on every request from four files |
| One switch | 404 from the whole surface where `dev_auth_enabled` is false, refused **before** authentication so the answer is "does not exist" rather than "authenticate and retry" |

**Derived, and therefore incapable of going stale.** FR-409 says the guide must not
restate capability from memory. It restates nothing at all: every line is one file agreeing
with another —

| Section | Source | The claim it makes |
|---|---|---|
| Views | each spec's §5.3 table | what the design says exists |
| — built? | `frontend/src/router/index.ts` | the router routes that path |
| API | `docs/contracts/openapi/generated.json` | the published surface (FR-451) |
| Workstreams | this file's phase status tables | the roadmap's own words, not a second judgement |

There is no stored copy, so there is no drift check to remember to run.

> **Corrected 2026-08-15, the day after this record was written.** The sentence that stood
> here — "a renamed heading breaks it silently, and `test_demo_guide.py` is that check, in
> the gate" — **was false.** An auditor renamed `07`'s §5.3 heading and the roadmap's
> status heading: six views and *every* workstream vanished from the guide, with the docs
> audit and the whole suite green. The test asserted that `/data` and `/reference` existed,
> so `01` and `02` were protected by accident and `03` to `07` by nothing.
>
> The check is real now and derived from the files: every spec that declares a view table
> must contribute one, and the roadmap must yield workstreams. Both injections fail loudly.
>
> Two more claims on this page were overstated the same way, and are fixed in the same
> commit: the page reported "**63 endpoints published**" with no denominator while 85
> declared routes did not exist, and "**7/7 workstreams closed**" — a 100 % signal for a
> plan four phases from done, because only Phase 1a has a status table. It now reads 63 of
> 148, names the phases with no status table, and does not count a route inside a `//`
> comment as built.

Today it reports **8 of 51 views built** (the entrance is now declared in `07` §5.3, so it
appears in its own guide), 63 of 148 endpoints published, and Phase 1a's workstreams alone.
Naming what is *not* built is the point: a page showing only what works invites the reader
to assume the rest works too.

**NFRs measured, not asserted** (NFR-529: a usable seeded state in < 5 min).

| Measured | | Budget |
|---|---|---|
| Cold — `compose down` first, images cached | **24 s** | 300 s |
| Warm — containers already up | **19 s** | 300 s |

> **Caveat, added 2026-08-15.** Both numbers were measured before `scripts/demo.py`
> refused a held port, and the measurement path was not self-verifying: `wait_for` returned
> on *any* answer, so a run could time a server the previous run had left behind. One such
> false reading was caught during the work (a "5 s" that was a stale probe); these two were
> taken with the ports verified free first, which is why they stand. The command now
> refuses a held port before starting anything, so a repeat measurement cannot make that
> mistake. NFR-529 remains **measured, not tested**, and `scope-audit` correctly lists
> it among PLAT's unevidenced requirements.

Both include a 60 000-row seed through the real Job path, both versions, the validation
failure loop and the acknowledgement. The full 678 013-row seed adds ~10 s (WK-666's record).

**Three defects, all found by running it rather than by testing it.** This is the whole
argument for FR-408: a passing test and a person driving the thing are different
evidence.

- **Ctrl-C left the frontend running.** `pnpm` spawns `sh -c vite`, so signalling the
  direct child stopped the shell and orphaned the server; the next run then found port 5173
  held and failed for a reason that looked unrelated. Fixed with `start_new_session` plus
  `killpg`, and confirmed by watching both ports go free.
- **Vite silently moved to another port** when 5173 was taken — and the command then
  printed a URL for a server it had not started, with a different identity, answering
  happily. `--strictPort` makes the clash an error.
- **The banner never appeared** when stdout was a file: Python buffers, the subprocesses do
  not, so step headers printed after the output they introduced and the final "open this
  URL" sat in the buffer. Every print is flushed.

**Not delivered by WK-667:**

| Item | Verdict |
|---|---|
| A browser session authenticated by OIDC | **Not started** — FR-393, owned by WK-664. The entrance uses the development identity the dev proxy injects, which is what FR-408 asks for and no more |
| The modelling half of the demo | **WK-665**, where it belongs: a fitted GLM, a rating version, `WF-698` end to end |
| A guide covering more than views, endpoints and workstreams | Deliberate. Each section is a file agreeing with another file; a section without such a source would be the hand-written list FR-409 exists to prevent |
