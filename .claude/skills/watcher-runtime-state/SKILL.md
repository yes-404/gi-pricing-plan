---
name: watcher-runtime-state
description: Write and maintain the RFC-895 runtime state file (artifact B) — position and the in-flight expensive-verifications list, re-derived every cycle rather than compared against a separate tally, so a dead or unwired writer cannot masquerade as a healthy zero. Use when standing up a new session's watcher, when a role needs to announce or check an expensive verification in flight (spec §8), or when a role needs the current phase/work/slice without reconstructing it from `docs/roadmap.md` itself.
---

# watcher-runtime-state: the RFC-895 runtime state file, re-derived not compared

`write_runtime_state.py` writes `$RUNTIME_STATE_FILE` (default
`~/gi-pricing-plan.local/handover/runtime-state.json`) — the runtime state file
`.claude/roles/watcher.md` and `docs/process/delivery-process.md` §13 describe as
artifact B, RFC-895 §2. Runtime/ops state lives outside this repository (spec §10); the
**script** is repo content, the **file it writes** is not, and is never committed or
`.gitignore`d — it is not in the repository at all.

## Why this exists, and why its shape changed from RFC-895's original proposal

The note (`docs/rfcs/RFC-00895-a-machine-readable-core-for-the-delivery-process-so-the-rules-a-script-can-check-stop-being-prose.md` §2) proposed B as a
state file the watcher writes and a mismatch detector compares against artifact history.
`docs/rulings/RL-00907-q4-artifacts-win-where-an-artifact-exists-and-nothing-that-blocks-an-action-may-be-counted-in-b-without-one.md`, **RL-907**, rejected that design:
the failure this file will actually have is **agreement by vacancy**, not disagreement —
if the writer is dead or never wired up, the state file reads zero, the artifacts read
zero, a mismatch detector never fires, and every reader is told the process is healthy.
**A mismatch detector cannot detect a dead writer.** So this script **re-derives; it does
not compare two independently-kept tallies.**

## Falsifiability — the four conditions RL-907(c) binds, and how each is met

This repository already withdrew one file of this exact shape:
`~/gi-pricing-plan.local/handover/roster-state.md` was a heredoc emitting a fixed roster
with only its timestamp substituted, withdrawn as register finding **F31** because *"a
freshness indicator that updates while the content it vouches for is frozen is worse than
no indicator, because it converts 'I do not know' into a confident wrong answer."*

1. **No file-level freshness token.** Each top-level section ("block" —
   `position`, `in_flight_expensive_verifications`) carries its own `written_by` /
   `written_at`. A block whose derived content has not changed this cycle is left
   **completely untouched**, timestamp included.
2. **`retry_counters` is absent entirely, never present as an empty or zero value.** As
   written by *this* script (`write_runtime_state.py`), that remains true: `cycle` never
   touches the field. **Corrected 2026-08-31, RFC-895 adoption slice G:** the block is no
   longer absent from the file as a whole — `scripts/hooks/retry_cap_hook.py` (C2) now
   writes it at the moment a fix/replan decision is recorded, independently of this
   script's cycle. The reasoning this condition states still binds C2's own design
   (RL-907(c): a `0` from a counter nothing increments is indistinguishable from a
   true zero — `docs/rfcs/RFC-00789-zero-calls-above-200k-tokens-measures-the-compaction-cap-not-discipline.md`'s
   boundary-metric trap in another dress); only the "does not exist yet" clause was
   superseded.
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
consistently across it: WK-661, WK-664 and WK-671 are all closed in prose while their `#` cells are
never struck. A mechanical parser over that file would confidently write a wrong phase or
work item some fraction of the time, and RL-907's governing principle (an absent field
beats a wrong one) rules that out. So `cycle` takes `--phase VALUE --phase-source "…"`
(and the same pair for `--work` / `--slice`) — the invoking role reads the value from
the named artifact and supplies both together; a field is written only when both are
given, and otherwise keeps whatever was recorded last cycle. **`flow_step` has no CLI
flag at all** — RL-907(c): it has no source artifact, "carried only if slice E can name
its source, and dropped otherwise", and this slice cannot name one.

This does not eliminate the read of `docs/roadmap.md` — it moves it from *every reader,
every time* to *whoever runs a `cycle` with a changed position, once*. Readers thereafter
read `runtime-state.json`, not the roadmap.

## Commands

```bash
export RUNTIME_STATE_FILE=~/gi-pricing-plan.local/handover/runtime-state.json  # optional, this is the default

# Re-derive and write (only touches blocks whose content actually changed):
python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py cycle \
    --phase 2 --phase-source "docs/roadmap.md §6" \
    --work WK-697 --work-source "docs/roadmap.md §6" \
    --slice W37-7 --slice-source "docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md"

# NOTE: every --*-source is validated before anything is written. If the file part does
# not exist in the repository the command refuses, exits non-zero and writes nothing —
# a dangling `read_from` cannot be minted. The `§n` suffix is prose and is NOT resolved:
# it names no addressable thing, so a guard over it could not fail on its own subject.

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
RL-907(d) stated directly: two `cycle` calls with the same position, a real
`time.sleep` between them, must produce byte-identical files. Verified failing against a
deliberately reintroduced F31 shape (a top-level `updated_at` stamped unconditionally on
every write, not committed anywhere in this repository): the same assertion fails with a
one-second-later timestamp as the only diff, at the same byte offset the real
`written_at` field would occupy if it were file-level instead of per-block.

## Not built in this slice

- **`retry_counters`** — not written by *this* script. RFC-895 adoption slice G shipped
  it via a separate writer, `scripts/hooks/retry_cap_hook.py` (C2) — see the correction on
  condition 2 above and that script's own docstring.
- **Hook enforcement** (announcing is not required, checking before starting is not
  enforced) — C2 enforces the retry cap it owns (`scripts/hooks/retry_cap_hook.py`); this
  file's own protocol (announce/check an expensive verification) still has no enforcing
  hook, C3 having been dissolved (RL-920) rather than built. This script remains
  descriptive infrastructure only for the blocks it writes; nothing here blocks an action.
- **Auto-derivation of `position`** — see above. A future slice could attempt one if a
  decision-maker rules the trade-off (a parser that is sometimes wrong) acceptable;
  nothing here forecloses it.

## Verified

2026-09-19 — **`write_runtime_state.py` now refuses a `read_from` locator whose file does
not resolve, and the taught invocation no longer contains one.** W37-7 Task 12,
`PL-1070`; plan review 13's R13-1 (`CR-1064:539`).

Review 13 found artifact B's live `position` block carrying two dangling locators. The
values are **arguments, not literals** — they arrive as `--*-source` and are stored
verbatim — so a repository commit can only fix the instrument, never the live file. Hence a
**fail-closed guard** rather than a one-off correction: validation runs before anything is
loaded or written, and a refusal writes nothing. A guard that refuses and writes anyway is
worse than neither, because it reports a failure the caller may ignore while the bad value
lands regardless.

**Validation stops at the file path.** A `§n` suffix is prose that addresses nothing a
filesystem or parser resolves; a guard over it would have no failing case on its own stated
subject. That boundary is pinned by a test rather than left to a comment, so a later reader
cannot "complete" the guard into a heading check that cannot work.

**Three things this found that were not in the review's scope:**

- **The skill's own taught invocation was wrong**, which review 13 did not measure: its
  `--slice-source` named a plan by a pre-migration dated filename that no longer exists. So
  the skill was teaching a dangling locator to every future watcher, not only to the one
  that ran. The module docstring carried the same defect independently. *(The retired
  spelling is not reproduced here — check 36 fails on a pre-migration path form surviving
  outside `docs/REDIRECTS.csv`, and cannot tell a form named in order to retire it from one
  left behind. That fired on this very entry's first draft.)*
- **The existing test `test_position_fields_carry_their_source` was itself passing a
  dangling locator**, and the new guard refused it. The test asserts the field is
  **non-empty**, never that it **resolves** — so a locator that dangles satisfied it exactly
  as well as one that works. The test written to prove *"position fields name the artifact
  they were read from"* was naming an artifact that was not there. Its locators are
  corrected; its assertion is left as it was, and the new tests cover the half it cannot.
- **The guard is wired to all three source arguments**, with a test that exercises each
  independently — a guard on `--phase-source` alone passes any test that only exercises the
  one the review happened to name.

**DP-7-2's default (a) applies: repository-only.** The live
`~/gi-pricing-plan.local/handover/runtime-state.json` is **not** touched by this slice — it
is outside the repository by design (`delivery-process.md` §10), and rewriting it is an ops
action for the watcher, not something an executor performs from a worktree. **It still
carries its dangling locators until the watcher's next cycle**, which the guard now forces
to supply resolvable ones. Recorded here and in the slice ledger as asked-for rather than
done.

2026-08-31 — corrected condition 2 and "Not built in this slice" now that RFC-895
adoption slice G shipped `retry_counters` via a second writer
(`scripts/hooks/retry_cap_hook.py`, C2) this script does not itself touch. Found while
implementing slice G and checking this skill against the repository before relying on it
(`CLAUDE.md` §15: verify against the primary source).

2026-08-30 — filed for RFC-895 adoption slice E
(`docs/plans/INDEX.md#2026-08-30-nt-0012-0013-0014-adoptionmd` §2), against RL-907
(`docs/rulings/INDEX.md#2026-08-30-nt-0014-q1-q3-q4-rulingsmd`).
