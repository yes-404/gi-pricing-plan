---
id: FD-1007
family: finding
title: `write_runtime_state.py cycle` cannot clear a field; "no active slice" is inexpressible
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F69.md
---

# F69 — `write_runtime_state.py cycle` cannot clear a field; "no active slice" is inexpressible

Evidence essay for the register row self-named `(F69)` in `docs/findings/register.md`. The
finding: `.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py`'s `cycle`
command merges new position fields onto the *existing* content and only overwrites a field
whose flag was actually passed. Omitting `--slice` does not clear a stale slice — it leaves
the previous value standing, silently. The artifact's stated design (`spec §8`) is that
position is re-derived every cycle *so a dead or unwired writer cannot masquerade as a
healthy zero*; silent field preservation defeats exactly that guarantee for this one field.

## Provenance

Relayed by the lead from the watcher, who hit this live while re-deriving position for a
cycle where no slice was active under `WK-695`, could not express that state, and reported
writing a knowingly-stale value rather than hiding the gap. The watcher also proposed the
fix shape (an explicit clear flag, or treating omission as absence) — a proposal, and the
disposition is not the watcher's, the lead's, or this row's to pre-empt.

A second, separate claim travelled with the same report and was **retracted by the lead
before this filing**: that the same script re-stamps `written_at` on every cycle regardless
of content change ("F31 rebuilt"). That claim is independently checked below and confirmed
false; it is not part of this finding and is not carried into the Decision.

## Verification — read, then run, both against `89dd2b1`

**Code** (`.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py`):

```python
def _position_block_content(
    existing_content, phase, phase_source, work, work_source, slice_, slice_source,
) -> dict[str, Any]:
    merged = dict(existing_content)
    if phase is not None:
        merged["phase"] = {"value": phase, "read_from": phase_source}
    if work is not None:
        merged["work"] = {"value": work, "read_from": work_source}
    if slice_ is not None:
        merged["slice"] = {"value": slice_, "read_from": slice_source}
    return merged
```

`merged` starts as a copy of whatever was already in the file. `slice_` (from `--slice`,
`argparse` default `None`) is only written when it is not `None`; the CLI has no separate
"clear" flag. A field's absence from the command line is indistinguishable, in this
function, from "the cycle looked at this and it is unchanged" — the exact confusion the
artifact exists to prevent (`.claude/skills/watcher-runtime-state/SKILL.md`).

**Empirically reproduced** (2026-09-01, against the shipped script, not a paraphrase of it):
a state file seeded with `position.slice = {"value": "old-value", "read_from":
"roadmap.md"}`, then `write_runtime_state.py cycle --work WK-695 --work-source manual-test`
(omitting `--slice` entirely). Result: `work` updated to `WK-695` as expected; `slice`
**remained `old-value`**, byte-identical to the seeded value, in the written file. The
`position` block was reported changed (because `work` changed) and `written_at` advanced —
correctly, since content did change; the slice field's silent survival is the defect, not
the timestamp.

**Mutation that must become detectable** (stated as the report asked): seed a state file
with a slice value, run `cycle --work <W>` omitting `--slice`, and observe the old slice
persist in the output. Today that passes silently — the script exits 0 and prints "runtime
state written" with no indication that a field neither confirmed nor cleared was carried
forward. It should be visible as either a cleared field (no `slice` key, or an explicit
`null`/absent marker) or a refusal demanding the caller state the field one way or the
other.

## The retracted claim, checked directly rather than carried forward

Reproduced independently: two `cycle` calls with identical arguments, seconds apart, against
the same file. First call: `position` reported changed (a real content change from the
seed), `written_at` set to the call's timestamp. Second, identical call: script reports
"runtime state unchanged," and `written_at` on both the `position` and
`in_flight_expensive_verifications` blocks is confirmed unmoved. This matches `cycle`'s own
logic directly: `_block_content` strips `written_by`/`written_at` before comparison, and
`new_position_block = old_position_block` (the whole old block, stamps included) whenever
the stripped content compares equal — a fresh block, and a fresh `written_at`, are only
constructed on an actual content change. The "re-stamps every cycle" claim does not hold
against this script, confirming the lead's own retraction; this essay does not raise it as a
separate concern.

## Scope of this finding

- **Not fix-before-close.** Nothing downstream is reported broken by this today; the
  watcher's own report is that it noticed the gap and wrote the stale value openly rather
  than being fooled by it.
- **Two fix shapes are live, choice not made here**: an explicit `--clear-slice`-style flag
  per field, or redefining omission-at-the-CLI-boundary as "leave to `cycle`'s own
  re-derivation, which found nothing" versus "not asked about" — the second requires the
  *caller* (whatever re-derives phase/work/slice from `docs/roadmap.md` before invoking
  `cycle`) to always pass an explicit empty value when its own derivation finds no active
  slice, rather than simply not passing the flag. Both are proposals; this row does not
  choose between them.
- **Consumers of the field are out of scope for this filing.** Whether a downstream reader
  of `position.slice` already treats some sentinel (e.g. an explicitly empty `value`) as "no
  active slice" is not established here and would bear on how urgent the fix is.
