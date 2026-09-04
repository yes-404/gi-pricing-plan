# W37-6 — Ruling 105: the `F-W` alias class, the (h1) breakdown, three more instrument shapes, OQ-OVR-18, a §7(f) append, and the migration run's go-ahead (2026-09-03)

**Filed** 2026-09-03 by the lead, recording decisions made under the maintainer's delegation.
**What this is.** Nine decisions arriving in two instructions from the deputy in the lead
channel on 2026-09-03, filed together under one number because neither had been filed when the
second arrived (the deputy's own rule for this case). The first two (A, B) were put to the
maintainer directly by the deputy, with the cell each reads from and the alternative priced, and
were **signed as drafted on 2026-09-03**. The remaining seven (D1–D7) were made by the deputy
itself, exercising the maintainer's own delegation of W37/W37-6 decisions, confirmed to the lead
directly in this session on 2026-09-03: *"your goal is to instruct the team lead to achieve the
target of landing W37, where the first step is land W37-6; make decision on behalf of me as the
maintainer."* Both are recorded here as the maintainer's decisions; the distinction between a
decision the maintainer signed personally and one the deputy made under standing delegation is
kept rather than flattened, because a later reader needs to know which authority chain each rests
on.

**Tree for every citation: `origin/main` = `3dbee20`, `docs` run `33799932699`,** unless a ref
is named beside it. Every figure not re-derived by the lead below is the deputy's own run,
relayed and marked as such.

## Authority

- **An amendment to what a maintainer's own prior ruling required is the maintainer's alone**
  (`CLAUDE.md` §12). Decisions A and B amend Ruling 102 §2/§3's row scope; D1–D3 amend nothing
  written before them (they fill instrument rows Ruling 102 §1 required but left unread); D4 is a
  dated append to Ruling 102 §5; D5 is a dated append to NT-0019 §7(f); D6 closes OQ-OVR-18; D7
  opens what Ruling 102's own text held shut, conditionally, and is itself a maintainer decision
  under the same delegation, not a re-reading of one already made.
- **The frozen records are not edited.** Ruling 102, the delegation record, and NT-0019 stand as
  filed; this record supersedes or appends to the sentences it names, in the pattern Ruling 102
  §3 and Ruling 104 used.
- **The deputy holds no authority to file.** It drafted every reading below, priced the
  alternative for each, and — for A and B — put them to the maintainer with the cell each reads
  from; the maintainer signed those two. For D1–D7 the deputy decided directly, under the
  maintainer's own delegating instruction quoted above. **The lead's role here is the
  recorder's and the merger's**, not the decider's, for any of the nine.

## Ruling 105 — the alias class, the disclosed rows, and the run's conditional window

<!-- Structural note: this heading exists so `_discover_multi_ruling_files`
     (`_RULING_HEADING_RE`, `^##\s+Ruling\s+(\d+)`) discovers this record as an `RL-` draft
     rather than falling through to `_discover_plain_plans`'s `PL- kind: leaf, owner: planner`
     catch-all — the defect F96 (`docs/audit/findings/F96.md`) was filed for. -->

**Ruling number derivation, run by the lead in its own checkout at `3dbee20`:**

```
git grep -ohE '^## Ruling [0-9]+' origin/main -- docs/ | grep -oE '[0-9]+' | sort -n | tail -1
  → 104
git grep -c 'Ruling 105' $(git branch -r | grep -v HEAD) -- docs/ .claude/ scripts/
  → no match
```

**105 is the next free number**, on `main` and on every remote ref, derived rather than assumed.
Both instructions arrived before either was filed, so both are recorded here under this one
number, per the deputy's own stated rule for that case.

### A. `F-W<n>-<n>` finding ids are the same alias class as `F<nn>`

**Sentence amended.** Delegation §8.5, `docs/plans/2026-09-03-w37-6-time-boxed-delegation.md:437`:
*"Every other alternative must return nothing. No further exclusion is granted here."*

**Ruled.** §7(d)'s `F-W[0-9]` alternative joins `\bF[0-9]{2}\b` as **excluded from the zero
requirement with its count disclosed** — a `DISCLOSE` row in `--verify`, printed with denominator
and control, never setting the exit code. It is **W37-11's citation-form item**, resolved by the
alias resolver W37-11 owns.

**Grounds.** §8.5's own deferral one line above, `:433` — *"the essays get ids and paths now;
`F<n>` stays a resolver alias to W37-11"*; the renewed-window handover `:110` and `:199` — the
alias resolver *"cannot be a simple `F<n>` → `FD-<nnnnn>` map"* because three audit eras reused
low `F` numbers. `F-W<n>-<n>` is the same alias with a work prefix: its target is a register row,
not a document that has an id yet. Measured at `3dbee20` (run `33799932699`, relayed): `(d2)`
migrated 220 lines / 70 files, control 217 / 59, companion `\bF-WK-[0-9]` 3 / 3 — the
whole-identifier fix (#693) working, and the residue is the alias class, not corruption.

**Alternative refused.** Rewrite now — builds W37-11's resolver inside W37-6 and puts the run
behind it; the build-ahead `CLAUDE.md` §0 forbids.

**Acceptance — violations.** *`(d2)` recorded as PASS at 0 by any means other than the alias
resolver* · *`(d2)`'s count omitted rather than disclosed* · *the `F-WK` companion non-zero on a
clean run* (that is corruption, not the alias class, and stays a `REGRESSION`) · *W37-11's
closure record without the `(d2)` count it inherited.*

### B. §7(h1) is green with W37-10's residue classes disclosed by count

**Sentence read.** NT-0019 §7(h), `docs/notes/0019-one-id-per-document.md:426`: *"`audit-docs.py`
… green"*; Ruling 102 §3's carve-out — *"Any H row without which `audit-docs.py` finds zero
requirements lands with the run"* — which names **parsers**, not W37-10's content rows.

**Ruled.** **`(h1)` passes when every `audit-docs.py` failure class on the migrated snapshot is
zero except checks 29, 30 and 35**, which the row prints **by count, each labelled `owner:
W37-10`**, and which do not set the exit code. Everything else — checks 32, 36, 1, 31, 27 and any
class not named here — must be zero.

**Grounds.** executor-h's merged record
`docs/plans/2026-09-03-w37-6-row-h-the-named-h-rows.md:143-151` (relayed) — check 35 (79) and
check 30 (77) are NT-0019 §5.1/§5.3/§5.4 **content** rows (stamping charters, skills, root
files), check 29 (11) is §5.2's register merge; all three are W37-10's by the map plan's slice
scope. The rest of the 14 820 (checks 32: 8 711, 36: 2 884, 1: 391 at that record's tree) are rows
(d)/(g)/the script — W37-6's. `NT-0003`: an owner named twice goes stale; the row prints the
owner once.

**Alternative refused.** Literal green — W37-6 absorbs 167 W37-10 items before the run, the
build-ahead `CLAUDE.md` §0 forbids, and the run waits on S3.

**Acceptance — violations.** *`(h1)` green while any class other than 29/30/35 is non-zero* · *a
29/30/35 count omitted rather than printed with its owner* · *a fourth class added to the
disclosed set without a dated ruling* · *`(h2)`'s vacuity probes weakened to make `(h1)` pass*
(the two rows are independent).

### D1. `(i)` is W37-10's and does not set the exit code

Ruling 102 §3 governs §1 (*"eight rows, not nine"*). `--verify` computes `(i)`, prints `owner:
W37-10`, and `(i)` is **non-fatal**. `FATAL_VERDICTS` (`scripts/_docverify.py:91`) keeps
`NOT_MEASURED` for every other row.

**Acceptance — violation.** *`(i)` blocking exit 0; or `(i)` dropped from the table.*

### D2. `(h4)` is measured at the migration PR, not in the snapshot

The snapshot has no venv or pnpm store (`(h4)`'s own note). **`(h4)` is measured by the migration
PR's own CI on its exact head — all four workflows green — plus the executor's local run of
`CLAUDE.md` §11's two halves, both recorded in W37-6's ledger with the head SHA.** In `--verify`,
`(h4)` prints `DISCLOSE` with that sentence, never `NOT MEASURED`.

**Acceptance — violation.** *The run merged with any workflow not green on the head SHA; a
Python-only local gate recorded as `(h4)`.*

### D3. `(h2)`'s OVER-EXEMPT is Ruling 96's ruled outcome and is disclosed, not failed

`(h2)` now reports every denominator non-zero (533 / 111 / 31 / 111 / 437) and fails only on
*OVER-EXEMPT: check 37 exempts 366 of 437 on the `was:` field*. That is Ruling 96's consequence,
accepted with its disclosure at delegation §6.3 — and since #693 the field it keys on carries true
provenance. **The over-exempt probe becomes `DISCLOSE`, printing Ruling 97 §4's four figures
together (0 red · N examined · M exempt by `was:` · the broken-input control); the
zero-denominator probes stay fatal.**

**Acceptance — violation.** *The four figures quoted apart; a zero-denominator probe demoted to
`DISCLOSE`.*

### D4. Dated append to Ruling 102 §5

*"Check 37's exemption currently keys on a substring test"* was false when filed: #661
(`a8b31ab`) keyed it on `_docid.parse_header`'s field earlier that day. §5 attaches to
**provenance**: condition 2 is re-measured on a `--verify` snapshot after #693 — every `was:`
value names a real pre-migration path of the same document — and recorded by the auditor
(Task 6 on the lead's board).

**Acceptance — violation.** *Condition 2 recorded MET on a keying check alone.*

### D5. Dated append to NT-0019 §7(f)

Ruling 103 §2.2's reading becomes the sentence's own text: *"unchanged across the migration on
the snapshot, per file through the routing table; `8f5d57d` is the tree the baseline was taken
at, not the comparand."* **Filed by the decision-maker via `spec-change` as a dated append under
§7, never an edit** — not part of this record's own diff.

**Acceptance — violation.** *`(f)` computed against a hard-coded `8f5d57d`.*

### D6. OQ-OVR-18 closed: the standard's specimens become placeholders

Ruling 103 §1.7 option 1. `docs/process/document-ids.md` and NT-0019 §1.1 rule 3 write their
specimens as `PL-<n>`, `PL-0<n>`, `PL-00<n>` (the shape the ADR examples already use), so no
specimen can ever resolve through `docs/INDEX.md`. OQ-OVR-18 → `closed` citing this ruling.
Measured (relayed): at `3dbee20`, `(e)`'s 33 violations include exactly two specimen hits
(`docs/INDEX.md:314`, `docs/open-questions.md:47`, both `PL-01240`); **the other 31 are padded
citations inside plan bodies and are Task 7's, real.** **Filed by the decision-maker via
`spec-change`**, both directions of `docs/open-questions.md` and the specs' §10 mirror (check 4)
— not part of this record's own diff.

**Acceptance — violation.** *An exemption keyed on the defining document's path instead; a
specimen left resolvable.*

### D7. The run's go-ahead and its conditional window

**Go-ahead.** `doc-id.py migrate --verify` **exits 0 on `main` at a quiet tree** — no open PR
touching `docs/**`, `scripts/doc-id.py`, `scripts/_docverify.py`, `scripts/_docid.py`,
`scripts/audit-docs.py`, `scripts/doc-index.py` — with the `DISCLOSE` rows of A, B, D1–D3
printed. No hand gate, no condition table.

**The window, once.** From the go-ahead tree, 8 hours. One branch; `doc-id.py migrate` against a
real checkout of that branch for the first and only time; the same-commit H rows; PR. Before
merge, all four:

1. CI green on the exact head, every workflow;
2. the auditor's independent `--verify` against a snapshot of the PR head, exit 0 (Task 6's
   role, fresh agent);
3. delegation gate 6 — `git revert` of the migration commit on a snapshot restores the tree
   byte-identical, three ways, as #662 proved;
4. the branch is the only open PR.

Then merge. **Then stop.** Delegation §3's reserved list, §4's halt protocol and §8.3's ordering
(handover committed first) apply unchanged; a second failure inside the window is a halt.
Amendments 2 and 4 bind. Five agents live at most, one fresh per task.

**Dated append, 2026-09-04, under the maintainer's delegation of 2026-09-03 (Authority,
above):** *five agents* means **five executors**; the reporter and watcher own no
worktree and run no gate, so they stand outside the count.

**What does not open.** W37-7…10 and W37-11. Nothing S3 starts without a further instruction
here; `CLAUDE.md` stays the maintainer's and is not delegated to the deputy either.

**Acceptance — violations.** *The run started while `--verify` exits non-zero on `main`; or from
a tree with an open docs/scripts PR; or merged with any of (1)–(4) unrecorded; or any S3 slice
touched inside the window.*

## What happens next, and what does not

- **Task 1's executor (`executor-verify-2`) lands `EXPECTED_VERDICTS` first**, unchanged by this
  ruling. A and D1–D3 are then implemented **as a follow-up in `scripts/_docverify.py`, after
  Task 1 lands and before Task 3 starts** (same file, serialized on the lead's board as Task 14):
  `(d2)` → `DISCLOSE` beside `\bF[0-9]{2}\b` in `D_DISCLOSED`; `(h1)` → per-class breakdown with
  checks 29/30/35 non-fatal and owner-labelled; `(i)` confirmed non-fatal in `FATAL_VERDICTS`;
  `(h4)` → `DISCLOSE` with the CI-on-exact-head sentence, never `NOT_MEASURED`; `(h2)`'s
  OVER-EXEMPT → `DISCLOSE` with Ruling 97 §4's four figures together.
- **D5 and D6 are the decision-maker's**, via `spec-change`, independent of the code follow-up
  above and not blocked by it.
- **D4 needs no code** — it is discharged by Task 6's own re-measurement.
- **Nothing here opens the run's window by itself.** The go-ahead is still the instrument's exit
  0 at a quiet tree; D7 states the condition, it does not satisfy it. The Work close remains the
  maintainer's alone (`CLAUDE.md` §12).

## Acceptance Standard

**This record is accepted when it is merged.** Its nine decisions bind from that point.

**Implementation: owed** (delegation §7.5 — a ruling names its implementing PR or carries
`implementation: owed`). No implementing PR exists for any of the nine at filing time. A and
D1–D3 are implemented by the `scripts/_docverify.py` follow-up named above (Task 14); D5 and D6
by the decision-maker's `spec-change` PRs; D4 by Task 6's re-measurement; D7 by the run itself,
once every other row on the board is green.

### Acceptance — the violation that must become detectable

Every per-decision violation clause above is this record's falsification set, gathered here
rather than restated: A's four, B's four, D1's one, D2's one, D3's one, D4's one, D5's one, D6's
one, D7's four. A reader checking whether this ruling is honoured checks each in place, not a
paraphrase of it.
