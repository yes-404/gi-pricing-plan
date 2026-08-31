---
name: watcher-runtime-state
description: Write and maintain the NT-0014 runtime state file (artifact B) — position and the in-flight expensive-verifications list, re-derived every cycle rather than compared against a separate tally, so a dead or unwired writer cannot masquerade as a healthy zero. Use when standing up a new session's watcher, when a role needs to announce or check an expensive verification in flight (spec §8), or when a role needs the current phase/work/slice without reconstructing it from `docs/roadmap.md` itself.
---

# watcher-runtime-state: the NT-0014 runtime state file, re-derived not compared

`write_runtime_state.py` writes `$RUNTIME_STATE_FILE` (default
`~/gi-pricing-plan.local/handover/runtime-state.json`) — the runtime state file
`.claude/roles/watcher.md` and `docs/process/delivery-process.md` §13 describe as
artifact B, NT-0014 §2. Runtime/ops state lives outside this repository (spec §10); the
**script** is repo content, the **file it writes** is not, and is never committed or
`.gitignore`d — it is not in the repository at all.

## Why this exists, and why its shape changed from NT-0014's original proposal

The note (`.claude/notes/0014-machine-readable-process-core.md` §2) proposed B as a
state file the watcher writes and a mismatch detector compares against artifact history.
`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`, **Ruling 47**, rejected that design:
the failure this file will actually have is **agreement by vacancy**, not disagreement —
if the writer is dead or never wired up, the state file reads zero, the artifacts read
zero, a mismatch detector never fires, and every reader is told the process is healthy.
**A mismatch detector cannot detect a dead writer.** So this script **re-derives; it does
not compare two independently-kept tallies.**

## Falsifiability — the four conditions Ruling 47(c) binds, and how each is met

This repository already withdrew one file of this exact shape:
`~/gi-pricing-plan.local/handover/roster-state.md` was a heredoc emitting a fixed roster
with only its timestamp substituted, withdrawn as register finding **F31** because *"a
freshness indicator that updates while the content it vouches for is frozen is worse than
no indicator, because it converts 'I do not know' into a confident wrong answer."*

1. **No file-level freshness token.** Each top-level section ("block" —
   `position`, `in_flight_expensive_verifications`) carries its own `written_by` /
   `written_at`. A block whose derived content has not changed this cycle is left
   **completely untouched**, timestamp included.
2. **`retry_counters` is absent entirely, never present as an empty or zero value.**
   NT-0014 script C2 (the hook that increments it) does not exist yet — adoption slice G
   is blocked on it (`docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` §2). A `0`
   from a counter nothing increments is indistinguishable from a true zero
   (`.claude/notes/0007-context-bound-measures-cap-not-discipline.md`'s boundary-metric
   trap in another dress) — so it is not shipped until C2 can actually write it.
3. **`in_flight_expensive_verifications` entries expire.** This block is genuinely
   underivable from a durable artifact — ephemeral coordination state a role announces
   about itself (spec §8's "announce an expensive verification, check for one already in
   flight" protocol, which had no named home until this file). Every entry carries
   `started_at` and `ttl_seconds`; an entry past its TTL is pruned on the next `cycle`
   and a `show` also treats it as absent live. Stopping an agent does not stop the
   commands it started, so an entry outliving its process is the default, not an edge
   case — this is why every entry must expire on its own rather than waiting for the
   announcer to clear it.
4. **`position` fields name the artifact they were read from.** See below — this script
   does **not** auto-parse `docs/roadmap.md`.

## `position.phase` / `.work` / `.slice` are caller-supplied, not auto-parsed

`docs/roadmap.md`'s own "closed" convention — a struck-through `#` cell — is not applied
consistently across it: W5, W6b and W11 are all closed in prose while their `#` cells are
never struck. A mechanical parser over that file would confidently write a wrong phase or
work item some fraction of the time, and Ruling 47's governing principle (an absent field
beats a wrong one) rules that out. So `cycle` takes `--phase VALUE --phase-source "…"`
(and the same pair for `--work` / `--slice`) — the invoking role reads the value from
the named artifact and supplies both together; a field is written only when both are
given, and otherwise keeps whatever was recorded last cycle. **`flow_step` has no CLI
flag at all** — Ruling 47(c): it has no source artifact, "carried only if slice E can name
its source, and dropped otherwise", and this slice cannot name one.

This does not eliminate the read of `docs/roadmap.md` — it moves it from *every reader,
every time* to *whoever runs a `cycle` with a changed position, once*. Readers thereafter
read `runtime-state.json`, not the roadmap.

## Commands

```bash
export RUNTIME_STATE_FILE=~/gi-pricing-plan.local/handover/runtime-state.json  # optional, this is the default

# Re-derive and write (only touches blocks whose content actually changed):
python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py cycle \
    --phase 2 --phase-source "docs/roadmap.md §7" \
    --work W11 --work-source "docs/roadmap.md §7" \
    --slice W11-S3 --slice-source "docs/plans/2026-08-29-w11-map.md"

# A role announces an expensive verification before starting it (spec §8):
python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py announce \
    --what full_test_suite --by auditor --tree <sha> --ttl-seconds 1800

# Check what's currently in flight (expired entries pruned live, not written):
python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py show
```

`--state-file <path>` overrides `$RUNTIME_STATE_FILE` on any subcommand — this is how
`tests/test_watcher_runtime_state.py` isolates every case to a `tmp_path` rather than
touching the real handover file, which the repository's own outside-the-repo rule
requires just as much of the test suite as of the watcher.

## The acceptance test, and what it looks like to fail it

`tests/test_watcher_runtime_state.py::test_a_cycle_with_no_change_is_byte_identical` is
Ruling 47(d) stated directly: two `cycle` calls with the same position, a real
`time.sleep` between them, must produce byte-identical files. Verified failing against a
deliberately reintroduced F31 shape (a top-level `updated_at` stamped unconditionally on
every write, not committed anywhere in this repository): the same assertion fails with a
one-second-later timestamp as the only diff, at the same byte offset the real
`written_at` field would occupy if it were file-level instead of per-block.

## Not built in this slice

- **`retry_counters`** — ships with C2 (adoption slice G), per condition 2 above.
- **Hook enforcement** (announcing is not required, checking before starting is not
  enforced) — that is C2/C3's job (slices F/G), not this file's. This slice is
  descriptive infrastructure only; nothing here blocks an action.
- **Auto-derivation of `position`** — see above. A future slice could attempt one if a
  decision-maker rules the trade-off (a parser that is sometimes wrong) acceptable;
  nothing here forecloses it.

## Verified

2026-08-30 — filed for NT-0014 adoption slice E
(`docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` §2), against Ruling 47
(`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`).
