# NT-0012 — A credential in an ephemeral job directory is borrowed, not stored, and is found by its shape, not its container's name

| | |
|---|---|
| **Raised** | 2026-08-29, the lead — found sweeping the rest of the W11 handover for durable lessons, the step task #23 itself specifies |
| **Status** | `landed` 2026-08-31 — both rules have durable homes, filed in adoption slice C (`97965be`): the credential-lifetime rule in `.claude/skills/secret-hygiene`, the search-by-shape rule in `.claude/skills/close-workstream`. Closed with the adoption (`docs/audit/work/nt-0012-0013-0014-adoption/README.md`). **Corrected from `open`, which had been false since `97965be`** — the same staleness NT-0014's own row carried and that `NT-0003` exists to name |
| **Deliverable** | Rules only, per `CLAUDE.md` §0's table — no code, no spec change. A later decision names the skill or role file each rule lands in |
| **Owner** | The lead found and assessed both instances; this decision-maker session drafted and files the note; the lead or maintainer accepts where each rule lands |
| **Lands in** | Not yet decided. Candidates: whichever role's charter owns posting to an external channel (the credential-lifetime rule), and a search-discipline note or skill this session's own `CompiledBundle` finding already motivates (the search-by-shape rule) |
| **Trigger** | Before storing any value a session must use again later, and before declaring any credential, file, or fact unrecoverable |

---

## Why this is one note and not two

Both rules come from the same incident, and the incident is one failure with two causes: a
value was placed somewhere that stopped existing, and the search that looked for it afterward
checked the wrong thing. Either rule alone would have prevented the outage this note is
written from; neither was in place, so both fired. **No token value and no transcript
excerpt containing one appears anywhere in this note** — per `docs/notes/README.md`'s own
prohibition on secrets, credentials, or dataset contents, and per the standing rule that
values never enter the repository, memory, or a handover file, only paths and patterns do.

## Rule 1 — A credential in an ephemeral job directory is not stored, it is borrowed

**The instance.** A Slack posting token lived only inside a W10 job directory. That
directory — not merely a file inside it — ceased to exist at ordinary cleanup, and the token
went with it. A different credential, the balance-watch endpoint's token, survived the
identical cleanup event because it had a durable source file outside any job directory from
the start. Same team, same day, same class of cleanup; one credential outlived it and one did
not, and the difference was entirely where each one lived, not how careful anyone was with
either.

**The rule.** A job directory is scratch space for the job that created it, cleaned up on the
job's own schedule, not on the credential's. A value that a session, or a later session, must
be able to use again is not "stored" by placing it in a job directory, a handover file, or
this session's own memory — all three are ephemeral relative to the credential's actual
lifetime. It is **borrowed** for as long as the container survives, and gone the moment the
container is cleaned, with no warning at the point of loss. A credential that must outlive
one job goes to a durable path outside the repository, outside `.claude/jobs/` or any
directory a cleanup routine owns, and outside any handover directory — which is itself
deleted or rewritten at each handover. State the *path* to where a credential durably lives;
never the value, in a note, a handover, or a commit.

## Rule 2 — Search for the value's shape, not the container's name, before declaring it unrecoverable

**The instance.** The first search for the missing token was by filename — the job directory
and the handover section that used to hold it. Both were already gone, so the search found
nothing, and a handover section was written stating the token was gone permanently and only
the maintainer could re-supply it. That statement was wrong for two and a half hours, during
which the credential was in active, successful use elsewhere. A second search, by the value's
own recognisable shape rather than by where it was last known to live — Slack bot and user
tokens both begin with a fixed, documented prefix pattern, `xox[bpasr]-`, which is the
technique worth recording here, never a matched value — found the token intact across
several old session transcripts.

**The rule, generalised past this one token.** A credential, a file, or a fact is not gone
because the container it was last seen in is gone; it is gone only when nothing that ever
held or produced it survives anywhere. Before declaring something unrecoverable, search for
what the thing itself looks like — a value's prefix, a function's signature, a concept's
description — not only for the name of the place it was expected to be. This is the same
substitution behind two other failures from this same day: a signature-sync ruling that
grepped the one-word identifier `CompiledBundle` and missed the concept spelled "Compiled
Bundle" two words apart in the glossary it needed to check, and a file-count check that
trusted a filename list over reading what each file's content actually changed. Naming the
container is convenient exactly where it is least reliable — at the moment the container has
just stopped existing.

## Acceptance criteria

Accepted when the lead or maintainer names where each rule lands — a role file's tools/duties
section for Rule 1 (whichever role is trusted with a channel-posting credential), and either
an existing skill or a new one for Rule 2's search discipline, which is not specific to
credentials and may belong somewhere more general than this note's own trigger. `landed`
records the destination for each rule; they need not land in the same place or on the same
day.

## Next step

Whoever next configures a credential a session must reuse reads Rule 1 before choosing where
it goes. Whoever next needs to declare something unrecoverable reads Rule 2 before writing
that sentence down. Neither rule requires code or a spec change to take effect immediately —
only to become findable by someone who was not in this session, which is this note's whole
purpose per task #23.

## Original wording

There is none in the sense `docs/notes/README.md` means — no maintainer request produced
this note. The lead raised both instances and supplied the assessment in a dispatch to this
session; the wording above is this session's, refined from that dispatch rather than quoted
from it, since the dispatch was addressed to a member of this team rather than written as a
note. The lead's own account is the sole source for the incident narrative (the job directory
identifier, the timing, and the two-and-a-half-hour window) — this decision-maker session had
no independent way to verify an already-deleted job directory's contents, and says so here
rather than presenting the account as independently checked.
