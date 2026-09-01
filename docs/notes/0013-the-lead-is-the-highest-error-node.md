# NT-0013 — The lead is the highest-error node: the evidence behind a claim `lead.md` now states with none

| | |
|---|---|
| **Raised** | 2026-08-29, the lead — the primary source for its own observed failures, dispatched to this decision-maker session to file |
| **Status** | `landed` 2026-08-31 — the "remove the relay" half landed in `docs/process/delivery-process.md` §15 in adoption slice D (`97965be`); the receiving half already had a home. Closed with the adoption (`docs/audit/work/nt-0012-0013-0014-adoption/README.md`). **Corrected from `open`, which had been false since `97965be`.** The note's own thesis was borne out during the W11 reopen: the lead's relayed claims were corrected by members thirteen times, every one correctly |
| **Deliverable** | Evidence only, per `CLAUDE.md` §0's table — no code, no spec change. `.claude/roles/lead.md` already carries the claim this note evidences; a later decision may fold the mitigations into `delivery-process.md` or `lead.md` directly |
| **Owner** | The lead is the author and the primary source; this decision-maker session verified what it could independently and files the note |
| **Lands in** | Partially landed already: `docs/process/delivery-process.md` §15's third bullet. Not yet landed: the "remove the relay" standing-practice change |
| **Trigger** | Before instructing a role-file clause, a fix, or a count based on a fact the instructing session has not re-derived from the primary source; before a recipient treats a lead-supplied fact as pre-verified |

---

## Why this note exists

`.claude/roles/lead.md` states, in a governing artifact every respawned lead session will
read: *"The lead is the highest-error node on this team, structurally, not by chance: it is
the only role that mostly relays rather than derives — a fact arriving from the lead reads
as already-checked and gets LESS scrutiny for it, backwards from what its provenance
deserves."* Verified verbatim against the live file before this note was written. That
sentence is a behavioural claim inside a governing document, and until now the evidence for
it existed only in inboxes — teammate messages, not a durable artifact. A governing claim
with no durable evidence is exactly what the rest of this repository does not tolerate
elsewhere (`CLAUDE.md` §13's own standard: a verdict needs evidence, never recollection).

## The mechanism

The lead reads everything and derives nothing (`docs/process/delivery-process.md` §3: the
lead "explores project context," "reviews," "decides replan vs. proceed" — never "writes"
or "implements"). It is therefore the only role that mostly *restates* facts it did not
establish. A restatement routinely drops the qualifier that made the original true, and a
fact arriving from the lead reads as already-checked — Claude Code's own default heuristic
treats seniority and centrality as proxies for correctness — so it gets **less** scrutiny
than a member's own derived work, not more. This is structural: it follows from the role
itself, and would afflict whoever held it, not a property of this particular session.

## The instances, 2026-08-29, roughly six hours, one session

**Count carries its corpus** (`CLAUDE.md` §13): these eight are the lead's own count from
its own vantage. The auditor independently counted five from a narrower vantage — a subset
of these eight, not a disagreement with them.

1. **Instructed a `decision-maker.md` clause reserving `CLAUDE.md` §0's spec-versus-code
   decision to the lead** — contradicting the reconciliation record's own "Record what
   moved" section, which the lead had itself drafted and filed hours earlier and had been
   citing to others as authoritative. *Caught by:* the decision-maker declined to write a
   clause it doubted and asked rather than comply; the executor then verified both halves
   independently.
2. **Quoted `CLAUDE.md` §12's superseded "verdict stays in the main thread" paragraph as
   current**, twelve minutes after a merged PR had replaced it. The decision-maker quoted
   the same superseded text back in the same exchange, so both sides reasoned from a
   paragraph neither had re-read live. *Caught by:* reading the live file directly rather
   than either party's memory of it. **Independently verified in this session**: the
   replacement commit (`#335`) is real, and the current `lead.md`/`CLAUDE.md` §12 text
   matches what superseded it, checked directly against `origin/main` before this note
   was written, not taken from either account.
3. **Drafted `auditor.md` granting the auditor write access to `docs/audit/plan-reviews.md`**
   minutes after ruling, in the same conversation, that §14's proposals belong to the
   planner. *Caught by:* the auditor ran `git log` on the file and found every commit on it
   was already a plan review, pulling the item from the draft. **Independently verified in
   this session**: `git log --oneline -- docs/audit/plan-reviews.md` returns exactly two
   commits (`f584e35`, `f0c1536`), both plan-review commits, confirmed against
   `origin/main` immediately before this note was written.
4. **Stated that one of two W10 worktree-destruction incidents happened in the executor's
   worktree.** Both did, by two different roles. *Caught by:* the executor reading both
   source files. The corrected fact is the stronger one — two incidents in the same
   worktree, by different roles, is a structural hazard; one incident there is bad luck.
   Not independently re-verified here — rests on the executor's own account, as the lead's
   dispatch itself frames it.
5. **Contradicted a correct audit finding using a thirteen-commit-stale working tree.**
   Reported role-file line counts of 24/19/11/18/20/11/12 against the auditor's real
   38/38/32/36/41/36/29. `git fetch` had run all afternoon without ever being merged, so
   `git log origin/main` read current while every file on disk was an afternoon old.
   *Caught by:* the lead itself, before publishing, only because the planner had caught
   itself the identical way an hour earlier. This session witnessed the report of this
   incident directly and used it, with the lead's permission, as the worked example in
   `.claude/skills/git-hygiene/SKILL.md`'s "fetch updates a ref, never your working tree"
   entry — that entry's own existence is corroborating evidence, not merely a citation of
   this note.
6. **Supplied `--date=iso-strict` as the fix for a date-rendering bug that reads a
   commit's day one calendar day wrong near a UTC boundary.** The supplied fix prints the
   commit's own recorded offset under every `TZ` — it would have reproduced the exact bug
   it was written to fix. *Caught by:* this decision-maker session, directly, testing the
   command under three timezones against a real commit straddling midnight rather than
   transcribing it into a skill file. First-hand: this is this session's own verification,
   not a relayed account.
7. **Gave `audit-docs.py`'s own check count as 24, from a grep for the highest numeral in
   the script.** *Caught by:* the executor re-deriving it by reading each check's actual
   logic (task #22, `#345`) — the same answer this time, but the lead's route would have
   been silently wrong had any single check number been skipped in the script's own
   enumeration. Not independently re-verified here — rests on the executor's account.
8. **Specified `delivery-process.md` §13 as the home for the maintainer's 50-word message
   rule**, having authored `delivery-process.md` §15 ("Correction and message discipline")
   itself an hour earlier and not connected the two. *Caught by:* the executor flagging the
   overlap without resolving it, since placement was the lead's call to make. Not
   independently re-verified here — rests on the executor's account.

Of the eight, this session independently re-verified three (2, 3, 6) against the
repository directly, corroborates one (5) from direct participation, and files four (1, 4,
7, 8) on the lead's and executor's own accounts as the primary sources for events this
session did not itself witness — consistent with `docs/notes/README.md`'s own
instruction to keep attribution honest rather than presenting a relayed account as
independently checked.

## What actually caught them — the load-bearing finding

Not one of the eight was caught by a check, a gate, or CI. **Every one was caught by a
member declining to accept something**: refusing to write a doubted clause, testing a
supplied command instead of transcribing it, reading a cited file instead of trusting the
citation, re-deriving a supplied count instead of repeating it, flagging an unresolved
overlap instead of silently landing it. The mitigations that work here are social, not
mechanical, and so they must be instructed explicitly rather than assumed to follow from
good intentions.

## The mitigations, in the order they were discovered

- **Weak, tried first:** put "verify against the primary source, do not implement against
  my relay" in every dispatch. This is `lead.md`'s current line (verified above) and
  `delivery-process.md` §15's third bullet. It states the sending half; instance 1 above
  shows the *receiving* half — a recipient's own doubt, voiced rather than swallowed — is
  what actually caught the sharpest instance, and that half is what §15 now states.
- **Strong, adopted mid-session, not yet landed anywhere durable:** remove the relay.
  Members send artifacts directly to whoever needs them; the lead is addressed only for a
  decision or a verdict, the one thing that cannot be delegated. The dispatch that raised
  this note states plainly that this decays within the hour unless announced as standing
  practice — which is exactly the kind of institutionalisation a note in `docs/notes/`
  exists to trigger, and exactly why this note's own `Status` is `open` rather than
  `landed`: the practice has been *tried*, not yet *written down* anywhere a fresh session
  would read it.
- **When a member questions a fact you supplied, check it before defending it.** Three of
  the eight instances above (2, 5, 6) were resolved this way, each time weakening rather
  than confirming the lead's original claim.

## Related

- [`NT-0003`](0003-duplicated-status-goes-stale.md) — the same class of failure (a fact
  restated loses the qualifier that made it true) applied to status fields rather than to
  a relayed instruction.
- [`NT-0012`](0012-a-credential-is-borrowed-not-stored.md) — the same day's other note on
  search-by-shape rather than by container; instance 6 above is a third occurrence of that
  exact substitution (checking what a command's name promises rather than what it actually
  does), named in `NT-0012` itself as "the same substitution... searching the identifier
  instead of the concept."
- `docs/process/delivery-process.md` §15's third bullet is this note's own evidence,
  landed before the evidence that justified it — recorded rather than smoothed over, since
  a rule landing ahead of its evidence is itself a minor instance of the pattern this note
  describes.

## Acceptance criteria

Accepted when the lead or maintainer decides where the still-unlanded mitigation — "remove
the relay," announced as standing practice — actually goes: a `lead.md` bullet, a
`delivery-process.md` §15 addition, or both. `landed` records the destination once chosen;
until then this note is the only durable record that the practice was tried at all.

## Next step

Whoever next drafts a `lead.md` or `delivery-process.md` amendment touching dispatch
practice reads this note first, so "remove the relay" is decided rather than re-discovered.

## Original wording

There is none in `docs/notes/README.md`'s sense — no maintainer request produced this
note. The lead supplied the mechanism, the eight instances, and the mitigations in a
dispatch to this session; the wording above is this session's, refined from that dispatch
rather than quoted verbatim, since the dispatch was addressed to a teammate rather than
written as a note. Every claim not marked "independently verified" or "corroborates" above
rests on the lead's own account, or the account of whichever role the lead names as having
caught the instance, and is presented as such rather than as independently checked.
