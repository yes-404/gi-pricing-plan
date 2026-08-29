# Addendum to Ruling 29 — F30: the table cell was wrong, the outcome survives on other grounds (2026-08-29)

**What this is.** A short addendum to
[`2026-08-29-w11-algorithm-pin-maturity.md`](2026-08-29-w11-algorithm-pin-maturity.md)'s
Ruling 29, filed rather than edited into it because `docs/plans/README.md` permits no such edit.
Raised by the auditor during transcription and confirmed by the lead. Read against `origin/main`
at `3edd75a`.

## Which half is wrong, first sentence

**The table cell at `:180` is wrong and the prose at `:203` is right.** The cell states the
meter's supersession as decided — *"Delete the `ceiling_meter` import … and say in `SKILL.md`
that the maintainer's manual 5-hour relay replaced them"* — while the prose two pages later calls
whether the meter is superseded *"a real question with a likely answer"* and makes the delete
conditional on it. A record cannot both decide a thing and call it open. The cell decided it; it
had no business doing so, because I had not established the premise.

**And the register is wrong, in the direction that matters most.** `3edd75a` transcribed the cell
faithfully and sharpened it — *"Decided, not left conditional"* — so the strong reading is what a
reader now finds. That transcription was correct work on incorrect input.

## Why the premise does not hold

Three distinct signals were conflated into two:

1. **CNY account balance** — what `balance_watch.py` actually polls, with the thresholds
   `SKILL.md` §Relay rules documents (BEGIN CLOSE below 10 CNY, heartbeat every 15 minutes).
2. **Five-hour usage percentage** — the maintainer's manual relay.
3. **Session-limit exhaustion records** — what the dead branch detects. The script's own docstring
   (`balance_watch.py:21-24`) calls `ceiling_meter` a module *"for detecting genuine session-limit
   records"*, and the call site at `:138-146` is commented *"Zero-fallback: genuine session-limit
   records (exhaustion in-session)"*.

(2) is a forecast of usage; (3) is a record of a limit already hit. They are adjacent, not the
same, and **nothing in the repository says one replaced the other** — `SKILL.md` never mentions a
five-hour relay at all; its only `ceiling_meter` text (`:88-90`) is about the env-var arrangement.
The supersession came from my own recollection of a watcher configuration, which is not evidence,
and the prose knew it.

**The concrete harm the merged wording would have caused is not the inconsistency.** It instructs
an executor to write into `SKILL.md` that the manual relay *replaced* limit-event detection. That
sentence would be false in a durable artifact, and `SKILL.md` is exactly where a future watcher
would go to find out what covers this.

## The outcome survives, on a premise that is established

**Ruled: delete the branch — for a different reason, and the reason must travel with it.**
`ceiling_meter` appears in **zero** tracked files (`git ls-files | grep -c ceiling_meter` → `0`),
and its only copy anywhere on disk is
`/home/puzhenhao1989/w6b-handover-2026-08-25/watcher-artifacts/ceiling_meter.py` — the **W6b**
handover, a team two handovers ago. The current W11 handover directory does not carry it. So the
branch cannot be enabled by anyone running this skill today, and the next team will not even
possess the file.

That is `NT-0012`'s borrowed-code shape at its terminal stage, and it is the ephemeral-path defect
this skill's own filing exists to eliminate, reproduced one level up: the script refuses to
hardcode the module's path *because it has none*, which is precisely why the capability is
unreachable. A capability nobody can switch on is not a capability.

**What does not change:** the banner clause. The arm banner must state whether limit-event
detection is active, unconditionally — a guard that degrades silently is the defect regardless of
which branch is right.

## Exact replacement text for the register's F30 decision cell

> carry forward — **owner decided: W11** (Ruling 29, as corrected by
> `docs/plans/2026-08-29-w11-f30-ceiling-meter-addendum.md`). Delete the `ceiling_meter` import,
> `CEILING_METER_DIR` and the `live_limit_events` block — **not** because the maintainer's manual
> five-hour relay superseded them, which is unestablished and was wrongly stated as decided, but
> because `ceiling_meter` is in no tracked file and its only copy is in the W6b handover two teams
> ago, so nothing can enable the branch. `SKILL.md` must say that session-limit detection is
> **performed by nothing**, and that filing a module in the repository is what it would take —
> never that something replaced it. **Unconditionally, independent of that: the arm banner must
> state whether limit-event detection is active** — a guard that degrades silently is the defect
> regardless of which branch is right.

## How it happened, because the mechanism generalises

I wrote the table first, in a decisive register, then wrote the prose and noticed the premise was
soft — and hedged **there** instead of going back to the cell. `docs/plans/README.md` convention 5
is about exactly this and I have quoted it at other people twice this session: *"a claim can be
present in one and absent in the next"*, and *"never re-read the section you just edited"*. A
summary table and its supporting prose are two sites, and the table is the one that gets
transcribed. **When a record carries both, the table is the site to re-derive, not the narrative**
— which is also why the auditor caught it and I did not.
