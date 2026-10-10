---
id: RL-1605
family: ruling
title: PL-1602 corrected — the lead does not fast-forward or change the root checkout; updating it is the user's call, and it is not needed for safety
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
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

# RL-1605 — PL-1602 corrected: the lead does not fast-forward or change the root checkout

*Disclosure: drafted under working id 9961, reserved by the lead (team-lead) on 2026-10-10;
minted as RL-1605 on 2026-10-10, in the D9 batch mint PR. The working id still appears in
verbatim quotes of channel entry headers and bodies, which keep it as written.*

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
- **The record is widened** by the entry headed "2026-10-10 21:03:35 BST — RL 9961 scope: (1)
  YES, the "restart running seats" clause is struck too; (2) YES, the root-started proof is not
  owed. RL 9961 widens to those lines" (`to-lead.md:21582`), verbatim: "(1) Hand-off item 6's
  "restart running seats" is struck. It belonged to the root fast-forward hand-off. With the
  root untouched, no restart is needed: seats spawned from main after #1269 read the
  absolute-path settings from their own worktree, and running seats keep their old, matching
  relative-path settings plus script until they end naturally. A mid-work restart would only
  disrupt live seats. (2) The "root-started proof line" (Task 3 Step 2, Acceptance 5) is NOT
  owed. It presupposed a root on the new settings, which my 16:40:33 ruling removed. Proof (i)
  in a throwaway seat (green) plus (ii) red at main discharge the fix, and FD-1598 closes on
  them (20:59:04). RL 9961 (corrects: PL-1602) widens to quote and correct those lines too
  (Hand-off item 6's restart clause; Task 3 Step 2's and Acceptance 5's root-started proof),
  each verbatim, citing 16:40:33 and this entry."
- **`corrects: PL-1602` is limited.** It covers the places in `PL-1602` listed in *What this
  record corrects* and nothing else, all read at `31b88780`: *Mitigation* (b) of §"The root
  checkout and the settings change" (:515–:518); *Hand-off* item 6 (:707–:709), including its
  restart clause; *Acceptance* 5's root-started sentence (:334–:335); *Task 3* Step 2
  (:617–:619); and, because their only content is the root fast-forward or the root-started
  proof, the closing sentence of item 1 of the same section (:498–:499) and the root-started
  clause of *Hand-off* item 4 (:699–:700). Each is quoted verbatim. `PL-1602`'s front matter
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

## What this record corrects — `PL-1602`, six places, at `31b88780`

File: `docs/plans/PL-01602-wk-1178-the-pretooluse-hook-runs-by-absolute-path-leaf-plan.md`.

1. `PL-1602` :515–:518, §"The root checkout and the settings change", *Mitigation* (b),
   verbatim: "(b) Hand-off item 6: the lead fast-forwards the root to the merge commit at
   once, and discloses it in the channel (memory `the-root-checkout-is-pinned-to-an-old-branch`,
   "Face, 2026-09-28"), then runs proof (i)'s root-started line." **Corrected:** struck. The
   lead does not fast-forward the root (16:40:33). Mitigations (a), (c), (d) and (e) of the
   same paragraph are not touched.
2. `PL-1602` :707–:709, *Hand-off* item 6, verbatim: "*(Added 2026-10-10.)* **The root
   checkout.** At the merge read-back, the lead fast-forwards the root checkout to the merge
   commit and discloses it in the channel; seats running at the merge are restarted if Task 0
   Step 6 showed a running session keeps the old command. Then Task 3 Step 2." **Corrected:**
   the fast-forward and its disclosure are struck (16:40:33); the restart clause "seats
   running at the merge are restarted if Task 0 Step 6 showed a running session keeps the old
   command" is struck (21:03:35 (1)); "Then Task 3 Step 2" is struck with Step 2 (item 4
   below). The lead does not fast-forward or change the root checkout and tells the user the
   root may be updated when they choose; no seat is restarted, because seats spawned from main
   after #1269 read the absolute-path settings from their own worktree, and running seats keep
   their old, matching relative-path settings and script until they end.
3. `PL-1602` :334–:335, *Acceptance* 5, the last sentence of the clause, verbatim: "One more
   line records the same from a session started in the root checkout after the root is
   fast-forwarded (§"The root checkout and the settings change")." **Corrected:** not owed
   (21:03:35 (2)). Acceptance 5's seat line, from the throwaway seat, is the whole of 5.
4. `PL-1602` :617–:619, *Task 3* Step 2, verbatim: "*(Added 2026-10-10.)* After the merge and
   the root fast-forward (Hand-off item 6), the same three calls in a session started from the
   root checkout; recorded as a dated line in the ledger's build log. This is the line
   FD-1598's close reads (Hand-off item 4)." **Corrected:** struck; not owed (21:03:35 (2)).
   FD-1598's close does not read it; it reads proof (i) in a throwaway seat and proof (ii)
   red at `main` (20:59:04).
5. `PL-1602` :498–:499, §"The root checkout and the settings change", the closing sentence of
   item 1, verbatim: "So proof (i) in a root-started session waits for the fast-forward
   (Hand-off item 6)." **Corrected:** there is no such proof (21:03:35 (2)). The rest of item
   1 ("Until the root is fast-forwarded, a session started there still reads the old relative
   command. Nothing new can lock it, but nothing is fixed for it either: a `cd` still locks
   it as today.") describes what a root-started session reads; it stays true for whoever
   later updates the root, and is not corrected.
6. `PL-1602` :699–:700, *Hand-off* item 4, the clause, verbatim: "and, after the root
   fast-forward, Task 3 Step 2's root-started line; the lead closes FD-1598 citing both."
   **Corrected:** the root-started line is not owed (21:03:35 (2)); the lead closes FD-1598
   citing Acceptance 5's seat line (Task 3 Step 1) and proof (ii), per 20:59:04.

**Plan text read and left uncorrected.** :500 (§"The root checkout and the settings change",
item 2), verbatim: "**After the fast-forward,** the command resolves to
`<root>/scripts/hooks/retry_cap_hook.py`, which the root has carried since #516. No lock-out."
It states what happens whenever the root is next updated, by whoever updates it; it names no
act of the lead and orders none, so it stays true. Two more hits of `grep -n -i -E
'fast-forward|root-started|restart'` over the file at `31b88780` are read and left: :513
(item 4, "assume the old command stays in force for a running session until it restarts"), a
statement about running sessions that orders nothing; and :572 (Task 0 Step 6, whose last
sentence says the step "fixes Hand-off item 6's instruction (restart the seats, or not)
after the merge"). Step 6's measurement stands; its last sentence names an instruction this
record has struck, so it is moot, not corrected. No other line of the file matches.

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

## Acceptance — the violation that must become detectable

- `PL-1602`'s `corrected_by:` names a record that does not correct it. *Detected by*
  `scripts/audit-docs.py`: every `corrected_by:` entry must be a record whose `corrects:`
  names the file (the module docstring's DP-7 line, `scripts/audit-docs.py:83`).
- `PL-1602`'s front matter lacks `corrected_by: [RL-1605]`. *Detected by*
  `git -C <worktree> diff -U0 origin/main HEAD -- docs/plans/PL-01602-*`, which shows the
  one front-matter line and nothing else; the audit does not report the absence.
- `PL-1602`'s body changes. *Detected by* the frozen-file rule that refuses a body that is not
  byte-identical (`scripts/audit-docs.py:2170`, "a frozen file's body never changes").
- The lead fast-forwards or otherwise changes the root checkout. *Detected by*
  `git -C /home/puzhenhao1989/gi-pricing-plan rev-parse HEAD`, which prints
  `8f5a8987c3467fa9961f02b2cfd5ceeb2d31411d` until the user chooses to update it.

## What this record does not decide

- **Whether and when the root is updated**: the user's.
- **FD-1598's close and its verdict**: the lead's (20:59:04); this record only removes the
  root-started line from what the close was to read.
