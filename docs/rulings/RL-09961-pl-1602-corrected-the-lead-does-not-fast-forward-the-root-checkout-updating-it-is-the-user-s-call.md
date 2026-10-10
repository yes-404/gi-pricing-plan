---
id: RL-9961
family: ruling
title: PL-1602 corrected — the lead does not fast-forward or change the root checkout; updating it is the user's call, and it is not needed for safety
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-10
owner: decision-maker
tree: 31b88780aa52894624a5e08454ce2d5925d04b37
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: PL-1602
relates: [PL-1602, SL-1603, LG-1604, FD-1598]
---

# RL-9961 — PL-1602 corrected: the lead does not fast-forward or change the root checkout

*Disclosure: drafted under working id 9961, reserved by the lead (team-lead) on 2026-10-10;
the id is minted in a later batch mint PR. When it is minted, the working id in this record
is replaced by the minted id.*

## Ruled

- **The decision is not this record's.** It is the maintainer's (by delegation), in the
  "ROOT CHECKOUT, NOT TOUCHED" paragraph of the entry of
  `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-10 16:40:33 BST — DISPATCH GO:
  PL 9617 / SL 9618 (absolute hook path, @10160a3d, ≈0.5 lane-day), effective at the FD-1374
  slice's merge read-back, minted in D8b. DP-3 and DP-4 as recommended; NO fast-forward of the
  root checkout" (`to-lead.md:21477`), quoted in full below. This record decides nothing beyond
  that paragraph.
- **The record is ordered** by the entry headed "2026-10-10 20:59:04 BST — MERGE-ACK #1269
  (PL-1602 / SL-1603, absolute hook path, LG-1604) …" (`to-lead.md:21571`), verbatim:
  "PL-1602's root-FF clause gets its correcting RL next batch; the root checkout stays
  untouched."
- **`corrects: PL-1602` is limited.** It covers two places in `PL-1602` and nothing else,
  both read at `31b88780`: the *Mitigation* (b) of §"The root checkout and the settings
  change" (:515–:518) and *Hand-off* item 6 (:707–:709). Both are quoted verbatim in *What
  this record corrects*, with the plan text that depends on them. `PL-1602`'s front matter
  gains `corrected_by:` naming this record, in the batch that mints it; its body does not
  change by one byte.
- **The corrected statement**, in the words of the 16:40:33 paragraph: the lead does not
  fast-forward or otherwise change the root checkout `/home/puzhenhao1989/gi-pricing-plan`.
  It is the user's working copy; changing it is the user's call. It is also unnecessary for
  safety, for the three reasons the paragraph gives (quoted below).

## The maintainer's entry, verbatim (the ROOT CHECKOUT paragraph, in full)

```text
ROOT CHECKOUT, NOT TOUCHED: the lead does NOT fast-forward or otherwise change /home/puzhenhao1989/gi-pricing-plan (the root checkout, @8f5a8987). It is the user's working copy; my session runs from it; changing it is the user's call. It is also unnecessary for safety:
- each session reads .claude/settings.json from its OWN working tree;
- the new settings and the absolute-path script arrive in the SAME commit, so no tree can have one without the other;
- the root keeps its old relative-path settings with its old script, which work together.
The plan's "fast-forward the root at the read-back" mitigation is struck. I tell the user the root may be updated when they choose.
```

## What this record corrects — `PL-1602`, two places, at `31b88780`

File: `docs/plans/PL-01602-wk-1178-the-pretooluse-hook-runs-by-absolute-path-leaf-plan.md`.

1. `PL-1602` :515–:518, §"The root checkout and the settings change", *Mitigation* (b),
   verbatim: "(b) Hand-off item 6: the lead fast-forwards the root to the merge commit at
   once, and discloses it in the channel (memory `the-root-checkout-is-pinned-to-an-old-branch`,
   "Face, 2026-09-28"), then runs proof (i)'s root-started line." **Corrected:** struck. The
   lead does not fast-forward the root. Mitigations (a), (c), (d) and (e) of the same paragraph
   are not touched.
2. `PL-1602` :707–:709, *Hand-off* item 6, verbatim: "*(Added 2026-10-10.)* **The root
   checkout.** At the merge read-back, the lead fast-forwards the root checkout to the merge
   commit and discloses it in the channel; seats running at the merge are restarted if Task 0
   Step 6 showed a running session keeps the old command. Then Task 3 Step 2." **Corrected:**
   the fast-forward and its disclosure are struck; the lead does not fast-forward or change
   the root checkout, and tells the user the root may be updated when they choose. The rest
   of the item is in *What this record does not decide*.

**Plan text that names the fast-forward as its trigger.** These lines are not corrected by
this record; they are listed so a reader of `PL-1602` knows the event they wait on is now the
user's update of the root, not an act of the lead. All verbatim at `31b88780`:

- :334–:335 (*Acceptance* 5): "One more line records the same from a session started in the root
  checkout after the root is fast-forwarded".
- :497–:499 (§"The root checkout and the settings change", item 1): "**Until the root is
  fast-forwarded,** a session started there still reads the old relative command. … So proof
  (i) in a root-started session waits for the fast-forward (Hand-off item 6)."
- :500 (item 2): "**After the fast-forward,** the command resolves to
  `<root>/scripts/hooks/retry_cap_hook.py`".
- :617–:619 (Task 3 Step 2): "After the merge and the root fast-forward (Hand-off item 6), the
  same three calls in a session started from the root checkout; recorded as a dated line in
  the ledger's build log."
- :699–:700 (*Hand-off* item 4): "after the root fast-forward, Task 3 Step 2's root-started
  line; the lead closes FD-1598 citing both."

## Why it is unnecessary for safety — the facts, checked

Read on 2026-10-10 at 21:01 BST.

- The merge `31b88780` (#1269, parent `bf457938`) changes the hook command in
  `.claude/settings.json` from `python3 scripts/hooks/retry_cap_hook.py hook` to
  `python3 "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"/scripts/hooks/retry_cap_hook.py hook`.
- `scripts/hooks/retry_cap_hook.py` is present at `31b88780` and at the root's HEAD
  `8f5a8987`, and is byte-identical between them (`git diff --quiet 8f5a8987 31b88780 --
  scripts/hooks/retry_cap_hook.py` exits 0). The merge does not change the script. So the
  paragraph's second reason holds in this form: every tree that carries the new command also
  carries the script it names; no tree has the new command without the script.
- The root checkout's HEAD is `8f5a8987`, on `main`: it carries the old relative command and
  the same script, which work together (the paragraph's third reason).
- That a session reads `.claude/settings.json` from its own working tree (the first reason) is
  the paragraph's statement. This record did not test it; `PL-1602` §"The root checkout and the
  settings change" records which copy a worktree-started session loads as not documented
  (Task 0 Step 3).

## The corrected behaviour already happened

`PL-1602`'s slice merged as `31b88780` (#1269) without the root being touched. The lead's
read-back entry headed "2026-10-10 20:59:45 BST — #1269 (PL 9617 slice) read-back VERIFIED …"
(`to-lead.md:21580`) says: "The root checkout HEAD is still 8f5a8987 (untouched, as ruled)."
Checked at 21:01 BST: `git -C /home/puzhenhao1989/gi-pricing-plan rev-parse HEAD` printed
`8f5a8987c3467fa9961f02b2cfd5ceeb2d31411d`.

## What it obliges

- **Acceptance.** `PL-1602` gains `corrected_by:` naming this record, front matter only, in the
  batch that mints this record. No other change.
- Nothing else. This record adds no task, no check and no edit to the root checkout.

## What this record does not decide

- **Whether and when the root is updated**: the user's.
- **What replaces Task 3 Step 2's root-started line**, and whether FD-1598's close needs it.
  The 20:59:04 entry says "FD-1598 (cd slips) closes on this merge with the positive control
  green (16:28:30 item 3)". The close and its verdict are the lead's.
- **The seat-restart clause** of Hand-off item 6 ("seats running at the merge are restarted if
  Task 0 Step 6 showed a running session keeps the old command"). The 16:40:33 paragraph does
  not rule it; this record strikes only the fast-forward that clause follows from.
