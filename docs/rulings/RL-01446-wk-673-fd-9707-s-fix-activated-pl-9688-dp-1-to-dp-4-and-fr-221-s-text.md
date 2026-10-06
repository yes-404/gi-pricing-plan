---
id: RL-1446
family: ruling
title: WK-673 — FD-1420's fix activated, a lookup reads the row in force as at a strict calendar date (PL-1447 DP-1 to DP-4, the order and the severity, and FR-221's text)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-06            # original date 2026-10-05, set at the draft; minted 2026-10-06
owner: decision-maker
tree: 99afcde215c0817c5ac4db55332ab7a69e4752a0
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-221, FR-69, FR-71, FR-255, FR-213, FR-227, FD-1374, RL-1263]   # at the mint, add FD-1420's, PL-1447's and SL-1448's minted ids
---

# RL-1446 — WK-673: FD-1420's fix activated, PL-1447 DP-1 to DP-4 and FR-221's text

*(Minted 2026-10-06 as RL-1446 from working id 9642, in the B1 batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

## How this was ruled

- **Filed under a working id the lead allocates after `SL-1409`'s gate.** `RL-1446` in this
  draft, and `RL-1446` in the texts below, stand for this ruling's minted id. Nothing else is
  a placeholder except `<SL-1448 date>` (T1).
- **The decisions are not this record's.** They are the maintainer's, by delegation, in `~/gi-pricing-plan.local/channel/to-lead.md`, cited below by entry header and
  quoted verbatim. This record carries them as a dated artifact (`CLAUDE.md` §12) and makes
  PL-1447's activation need 2 true. It decides nothing beyond them.
- **Inputs, read at the heads named:** FD-1420, draft #1132, branch `fd-9707` @`473b27e4`;
  PL-1447, draft #1145, branch `pl-9688-fd9707-asat-fix` @`2f3269c8` (planned at
  `caa4e411`). Every spec and code locator below was re-read at `origin/main`
  `99afcde2` on 2026-10-05, and again at `origin/main`
  `809a3794af6d3a6ba688663b0d9b59f951190680` at 2026-10-05 15:08 BST: every locator is at the
  line given (`03` changed between them only at `:136`, FR-239's finding id re-pointed, #1150).
- **Brief:** `brief-dm-9707-2026-10-05.md` (the lead, 2026-10-05).

## Locators — read at `99afcde2`

- `03-rating-engine.md:107`, FR-221: "`lookup` steps evaluate reference data **as at a
  declared date** — normally the policy effective date, never "now" (`01` FR-71). The date
  source is explicit in the step." No dated amendment on the row (`grep -n 'FR-221'
  docs/specs/03-rating-engine.md`: one row hit). The row is at the same line as at the plan's
  tree `caa4e411`.
- `01-data-management.md:176`, FR-69: half-open `[effective_from, effective_to)` validity;
  "Overlapping intervals for the same key are rejected at load time." `01:178`, FR-71.
- `03:928-934`, the owned-codes paragraph of `03`: `RATING_GRAPH_UNRESOLVED_REF`,
  `RATING_TYPE_MISMATCH`, `INPUT_CONTRACT_VIOLATION`, `REFERENCE_LOOKUP_MISS`.
  `REFERENCE_INTERVAL_OVERLAP` is `01`'s (`01:934`), raised at
  `backend/src/app/platform/reference.py:174`.
- `03:844-845`: `RATING_GRAPH_UNRESOLVED_REF` for a consumed name that is no port and no
  step's product; `RATING_TYPE_MISMATCH` for an incompatible declared type (FR-227).
- `packages/pricing-core/src/pricing_core/rating/compile.py:359`, `ALGORITHM_CHECKS`;
  `:366`, `validate_algorithm`, which applies every check in it (`:390`). It runs at save,
  `backend/src/app/platform/rating_algorithms.py:91` (`_issues_to_error`), and again at
  compile, `compile.py:611`, inside `compile_bundle` (`:573`).

## Ruled

1. **DP-1, as decided (option (a)).** Entry "2026-10-05 13:15:53 BST — DECISIONS 17–21
   (PL-1452 DP-S3-2/3/6; FD-1420 DP-1; RL-1428 follow-ups)", item 20:
   "FD-1420 DP-1: OPTION (a). `as_at` may name only `effective_date` or a declared `date`
   input. It is checked at compile (the named input's type is date, else refused naming it)
   AND at run time (the value is a strict ISO calendar date YYYY-MM-DD; an offset or
   datetime string, or a malformed one, is refused, never silently missed). Red first: the
   offset-string and malformed cases are tests."
2. **DP-2, as decided (option (a)).** Entry "2026-10-05 13:20:26 BST — DECISIONS 22–27;
   severity signals for the four gap findings", item 22:
   "PL-1447 DP-2 (FD-1420's window): OPTION (a), in-graph per-rule `date($) >= date(from)
   and date($) < date(to)` (spiked on zen 0.53.0). Conditions: an open-ended window (no
   `to`) is handled and tested; overlapping windows for one key are REFUSED at table save or
   bundle compile (else "first match wins" returns by another door), with a named code and a
   test; boundary tests at `from` and at `to` (half-open), red first."
   The overlap condition is met by the refusal at table save that is already on main,
   `REFERENCE_INTERVAL_OVERLAP` (locators), and pinned by a test (PL-1447 Acceptance 6).
3. **DP-3, as decided (option (a)).** Entry "2026-10-05 13:20:52 BST — DECISION 28 (PL-1447
   DP-3): OPTION (a), with a pinning test":
   "OPTION (a): DP-1's strict run-time check applies to `date` inputs named by `as_at`;
   QuoteContext.effective_date is NOT changed (no model-schema or contract change).
   Condition: the slice adds tests that PIN today's parsing of effective_date on /score: a
   plain YYYY-MM-DD is accepted; a midnight datetime with an offset yields its local calendar
   date (the row chosen is that date's); a non-midnight datetime and a malformed value are
   refused 422. If any of those does not behave as the lead describes, stop and bring it
   back: then (b) is reopened."
4. **DP-4, as recommended by the plan and confirmed.** Entry "2026-10-05 13:39:37 BST —
   PL-1447 / SL-1448 (the FD-1420 fix, #1145 @2f3269c8): noted; FD-1420 goes before PL 9776;
   DP-4 OK; start the RL's DM now", item 3:
   "DP-4 (RATING_TYPE_MISMATCH and RATING_GRAPH_UNRESOLVED_REF checked at save and at
   compile): OK, with a red-first test at each point."
   That is PL-1447's option (i)+(p): the check is appended to `ALGORITHM_CHECKS`, so it runs
   at save and again at compile (locators). No new error code.
5. **The order.** Same entry, item 1: "Serialisation with PL 9776 (#1051, the WK-1178 F35
   remedy for NFR-490 trace overhead, draft): the FD-1420 fix (HIGH, a mispricing) goes
   FIRST; PL 9776's slice waits and rebases onto it. Name this in both dispatch records. The
   03 sharing with SL-1391 and S2 is in distinct sections, named at dispatch with hunks
   listed (my 13:00:09 conditions)."
6. **The severity.** Same entry, item 2: "Exposure (0 lookup algorithms in 93 local DBs; no
   golden or seed lookups, so no price moves): noted. It does NOT lower the severity.
   FD-1420 stays HIGH as ruled 13:11:05: latent in our data, live for any table with
   effective windows. The ledger records the 0 and the predicate that counted it."
   FD-1420 at `473b27e4` already states HIGH, owner WK-673, deadline before the P2 exit
   demo (§Finding). The owner discrepancy PL-1447 raised against `9e51cbe8` is not present
   at that head.

## The spec texts

One text. Placement was read at `origin/main` `99afcde2`. It is applied by SL-1448 (PL-1447
Task 5), in one commit with the code (`CLAUDE.md` §2), and `<SL-1448 date>` is that commit's
date.

**T1 — `03` FR-221, the date source and the window (DP-1 to DP-4).** Proposed by PL-1447
§"Spec text T1" and **adopted with three amendments**, each listed after the text.

Placement: the FR-221 row (`docs/specs/03-rating-engine.md:107`). The text is **appended**
to the end of the second cell, after `The date source is explicit in the step.` and one
space, before the closing ` |`. Nothing is struck. The row stays one physical line. The text
holds no `|`.

Find string, `grep -cF` over `docs/specs/03-rating-engine.md` at `99afcde2` gives **1**, and
again **1** (`:107`) at `809a3794`:

```text
never "now" (`01` FR-71). The date source is explicit in the step. |
```

Append

```text
*(Amended <SL-1448 date>, `RL-1446`, FD-1420.)* **`as_at` names `effective_date` — the quote's stamped date — or a declared `date` input, and nothing else.** Anything else is refused when the algorithm is saved, and again when its bundle is compiled: a declared input of another type with `RATING_TYPE_MISMATCH`, and an undeclared name with `RATING_GRAPH_UNRESOLVED_REF`. **The value read is a calendar date, `YYYY-MM-DD`.** A datetime, an offset, or a malformed value is refused per quote with `INPUT_CONTRACT_VIOLATION`, never treated as a miss. **A row is in force when `effective_from ≤ as_at < effective_to`**: `01` FR-69's half-open interval, where an absent `effective_to` is open-ended. A key with no row in force is a reference miss (FR-255), resolved by the step's `on_miss`. Overlapping rows cannot reach a bundle: FR-69 refuses them when the version is loaded (`REFERENCE_INTERVAL_OVERLAP`).
```

*The amendments to the proposal:*

1. "*(Amended 2026-10-05, FD 9707; DP-1 to DP-3 decided by [the maintainer (by delegation)].)*" → [Elision: the word our records bar for the maintainer's delegate stood in this quoted text and is elided, per the records rule.]
   "*(Amended <SL-1448 date>, `RL-1446`, FD-1420.)*". A spec amendment cites the governed
   record that rules it, as RL-1418's (#1128) texts do; the maintainer's (by delegation) entries live in a local
   channel file a spec reader cannot open, and this record quotes them. The date is the
   applying commit's, as in RL-1418. It also now covers DP-4, which the proposal's marker
   omitted.
2. "refused when the algorithm is validated" → "refused when the algorithm is saved, and
   again when its bundle is compiled". DP-4 as confirmed (Ruled 4): "checked at save and at
   compile". "Validated" named neither point, and DP-1 itself says "checked at compile".
3. The proposal was a blockquote across lines; the text is one physical line, because a
   table cell cannot hold a line break.

No other byte of the proposal changed.

## What it obliges

- **This commit:** this record only. No spec, plan or code file is edited here.
- **PL-1447's activation need 2 is met** by this record once minted. Need 1 (FD-1420 minted,
  #1132) and need 3 (the activation PR's dated line) are not this record's.
- **SL-1448 (PL-1447, the planner's file, not edited here)** applies T1 in Task 5, verbatim
  from this record; where this record and the plan's §"Spec text T1" differ, this record
  wins and the dispatch record names the three amendments above.
- **DP-3's stop condition binds the executor**: if any pin of PL-1447 Acceptance 7 fails at
  the slice's base, the slice stops and reports to the lead; DP-3 (b) is then reopened and
  this record does not cover it.
- **Both dispatch records** (SL-1448's and PL 9776's, #1051) name the order of Ruled 5: the
  FD-1420 fix first, PL 9776's slice rebased onto it. They never run concurrently (shared
  `_decision_table_node`, the `runtime.py` docstring and `ALGORITHM_CHECKS`, per PL-1447
  §"Write set", `RL-1263`).
- **The ledger** records the exposure 0 with the predicate that counted it (Ruled 6; PL-1447
  Task 0's script, run at dispatch).
- **FD-1374's question** (whether an input may carry a stamped name at all) stays with its
  owner, PL 9776. This record does not decide it; T1 refuses only the shadowed value a
  lookup reads.
- **FD-1420** is closed by SL-1448's merge when the acceptance below is met. The verdict is
  the lead's.

## Acceptance — the violation that must become detectable

The violation: **a lookup that prices a quote on a row not in force at its `as_at`, or
reads an `as_at` that is not a calendar date without refusing it.** PL-1447's Acceptance
Standard items 1 to 11 are the tests; each red is seen at the slice's base for its stated
cause. In particular:

- **The window (DP-2):** the boundary cases at each `from`, at the old row's `to`
  (half-open), the open-ended row, and before every row (`REFERENCE_LOOKUP_MISS` under
  `on_miss: error`), red first on pricing-core and on `/score`, `/score/compare` and batch
  (Acceptance 1, 2, 5).
- **The overlap door (DP-2):** loading two overlapping windows for one key is refused with
  `REFERENCE_INTERVAL_OVERLAP` (Acceptance 6; a pin, not a red).
- **The compile half (DP-1, DP-4):** a non-date input, an undeclared name, and a non-date
  declared `effective_date` are each refused with the code T1 names, both at save and at
  compile, red first at each point; the message names the step and the `as_at` value
  (Acceptance 3 covers compile; the red at save is DP-4's condition, Ruled 4, which the
  plan's Acceptance does not yet list and the dispatch record adds).
- **The run-time half (DP-1):** the offset, naive-datetime, unpadded, compact, impossible
  and nonsense values, and an input shadowing `effective_date`, are each refused with
  `INPUT_CONTRACT_VIOLATION`, never a miss, red first (Acceptance 4); the refusal never
  carries the value (Acceptance 11, NFR-499).
- **DP-3's pins** on `/score` (Acceptance 7), with the stop above.
- **No shape changes:** `generate-contracts.py --check` gives no diff (Acceptance 10).

Drafted as working id 9642, 2026-10-05.
