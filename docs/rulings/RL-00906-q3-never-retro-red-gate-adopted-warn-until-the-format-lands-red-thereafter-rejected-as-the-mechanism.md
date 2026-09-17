---
id: RL-906
family: ruling
title: Q3: never retro-red-gate — adopted; "warn until the format lands, red thereafter" — rejected as the mechanism
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md
---

## RL-906 — Q3: never retro-red-gate — adopted; "warn until the format lands, red thereafter" — rejected as the mechanism

### 1. Verified first, at `1407e09`

| Claim | Verdict |
|---|---|
| `docs/plans/` holds a large frozen corpus | **Confirmed** — 114 `.md` files besides `README.md` |
| every one carries a `YYYY-MM-DD-` prefix | **Confirmed** — 114 of 114; `README.md` is the only non-conforming name, and it is not a plan |
| the naming is required, not incidental | **Confirmed** — [`../plans/README.md`](../plans/README.md) §Naming: *"`YYYY-MM-DD-<slug>.md`, dated when the file was started"* |
| a filed plan may be edited to agree with today | **No** — [`../plans/README.md`](../plans/README.md): *"Do not edit a filed plan to agree with today's repository"*, one narrow exception for repointing links |
| the acceptance-standard format exists | **No** — impact-matrix row 15 puts it in `.claude/skills/writing-plans`; slice F is not started |
| plans are one of four file kinds | **Confirmed** — [`../plans/README.md`](../plans/README.md) §The four kinds: no suffix (the plan), `-ledger`, `-final-review`/`-verified`, `-handover` |

### 2. Ruled

**The conclusion stands: C1 never red-gates a plan filed before the format existed.** The
lead's framing is adopted as the reason — reddening 114 frozen records would force either an
edit to a record (forbidden) or a permanently-ignored gate, and a gate everyone scrolls past
is worse than no gate because it launders inattention as compliance.

**The proposed mechanism is rejected.** "Warn until the format is in `writing-plans`, red
thereafter" makes a file's verdict a property of **when the check runs**. The same file
passes on Tuesday and fails on Wednesday, a fresh clone cannot reproduce a verdict, and
nothing in the repository records which side of the switch a given run was on.

**Ruled instead: the discriminator is a fact in the file — its own filename date, compared
against a cutoff date written as a constant in the check.** Durable, reproducible in any
clone at any revision, and already mandatory under `docs/plans/README.md`. Four parts:

- **No warn phase at all, because there is nothing to warn about.** C1 and the
  `writing-plans` format land in the **same commit**, so the cutoff is that commit's date and
  **zero** existing plans are in scope on day one. The warn phase in the proposal exists only
  in a world where the validator lands before the format it validates, and it does not have
  to.
- **No per-file warning on legacy plans either — one aggregate note line**, naming the count
  and the cutoff date. The exemption stays visible (a reader can see 114 files are out of
  scope, and it is not a silent skip) without 114 lines of noise training every reader to
  skim the check's output.
- **Red from the first day for plans dated on or after the cutoff.** A check that cannot fail
  on the day it lands is `CLAUDE.md` §13's *"check that has never printed a failure"*.
- **Scope is the plan kind only.** The field is required of the file kind `writing-plans`
  produces — not of `-ledger`, `-handover`, `-final-review` or `-verified` files, which are
  written by other procedures and have no acceptance standard to declare. The check
  discriminates by the documented suffixes; a check that guesses would red on every future
  ledger and be switched off within a week.

**C1 is a check inside `scripts/audit-docs.py`, not a new script**, by RL-920 §2's test:
the acceptance standard is a state written down in a file. Next free number at landing time.

### 3. What it obliges

Slice F. §13's proof needs three cases, not one: a synthetic plan dated after the cutoff with
no acceptance-standard field **reds**; a plan dated before the cutoff **passes**; and a
conforming plan dated after the cutoff **passes** — the third is the control without which
the check can go green by exempting everything, which is the failure mode this ruling is most
exposed to.

**Overridden if** the cutoff is read from the clock or from the git history rather than
written as a constant, if legacy plans emit per-file output, or if the check lands before the
format it validates.

---
