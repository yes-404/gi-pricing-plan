---
id: FD-936
family: finding
title: `get_eta`'s Z-only stamp vs `eta.md`'s GB-local convention
status: active                  # active → closed | retired (§1.2a)
created: 2026-08-31
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F65.md
---

# F65 — `get_eta`'s Z-only stamp vs `eta.md`'s GB-local convention

**Register row:** `docs/findings/register.md`, the row self-naming `(F65)`. This file is the
evidence essay filed alongside that row's Concerns and Decision cells, per RFC-896 P4 and
`docs/audit/findings/README.md`'s naming and compression rules. The row keeps the index —
Finding id, a short Concerns synopsis, Work item, Phase, and Decision compressed to its
disposition — and is the record `register-lint.py`, `register-owed.py` and
`scripts/audit-docs.py` check 25 all read; nothing here is parsed by any of them.

**Filed split from the start, 2026-08-31** — the essay below is already over the
findings-file migration threshold before this row exists, so per
`docs/audit/findings/README.md`:114-116 it is filed as a short register row plus this file
from the outset, never filed long and migrated later.

## Concerns — the divergence

`get_eta` (`.claude/skills/reporter-cycle/scripts/reporter.py:170`) requires a literal
`Z`-suffixed `**Updated:**` stamp — its regex accepts a `YYYY-MM-DD` date, a space or `T`,
an `HH:MM` time, then a literal `Z` and nothing else; the file it reads,
`~/gi-pricing-plan.local/handover/eta.md:8`, mandates the opposite — "**All times are GB
local (BST, UTC+1)** — maintainer instruction 2026-08-29." A real prior snapshot on disk,
`eta.md.prev:14`, carried exactly `**Updated:** 2026-08-30 10:00 BST`, which the parser
cannot match; fed directly through `get_eta`, it returns `stale=None` — the "staleness
unknown" branch (`reporter.py:338`), not an error.

**Verified from Slack directly, not the local log** (`slack-reporter.log` records only
`ok=True`/`ok=False`, never message bodies): queried `#claude-code-update`'s full history
via `conversations.history`, cursor-paginated, **212 messages spanning 2026-08-29 10:30Z to
2026-08-31 13:45Z** — the reporter's entire operating history, matching the local log's own
span and count. Of 190 real-headline ETA posts, **0 ever showed**
`_(STALE — Updated stamp is more than 2h old)_` (`reporter.py:340`); **166 (87%) showed
"staleness unknown" instead** — the degraded branch is the steady state, not an edge case,
and the STALE branch this mechanism exists to raise has never once fired across the
reporter's whole life.

The live rewrite of the stamp to `2026-08-31 14:49Z` (`eta.md:14`) **fixes this one
instance only**: nothing enforces the `Z` format on the human side, `eta.md`'s own header
still instructs GB local time for everything written to it, and the next lead-authored
`**Updated:**` stamp written to that same documented instruction reproduces the identical
silent degrade.

**Same class as F26**: `.claude/skills/reporter-cycle/SKILL.md:155-156` already states
"There is no CI workflow for `.claude/**`... so these local runs are the only gate this
change has" — a skill that documents its own untestedness and then ships this exact defect
through that hole.

## Decision — reasoning

**Carry forward, unowned-pending-authorisation.** A code-side fix (accept the GB-local
convention via stdlib `zoneinfo`, keep `Z` still parseable, regression test) is recommended
over changing the documented convention, on the evidence above (a dated maintainer
instruction that 87% of real posts already follow), not on authority alone. Assigning it a
workstream and owner is the maintainer's or lead's call, not this row's — recorded unowned
rather than guessed.

**Falsifiable, not permanent**: this row is discharged the moment a genuine STALE post
appears in `#claude-code-update` under the current code (refuting "never fired"), or
superseded once a fix lands and is verified against a re-run of the same Slack-history
query.
