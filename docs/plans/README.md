# Filed plans

The implementation plans this project has worked from, and the ledgers recording what
happened when they were executed. They are committed, so the record outlives the session
that wrote it.

They live under `docs/` rather than in an untracked scratch directory for the reason
`.gitignore` already gave for keeping them out of one: a plan is *"a second account of what
the project is doing"*, and the objection was never to the second account — it was to an
**unaudited** one. Filed here, `scripts/audit-docs.py` reads them like every other document
in the suite, and a plan that cites a requirement which does not exist fails the gate.

## A filed plan is a record, not an instruction

Each file is frozen at its date. It says what was believed, intended and decided *then* —
including the parts that later turned out to be wrong, which are usually the most useful
parts to a reader working out why the code looks the way it does.

**Do not edit a filed plan to agree with today's repository.** That is the same rule
[`CLAUDE.md`](../../CLAUDE.md) §0 applies to a spec and its code: quietly making one match
the other destroys the record of which was believed, which is the thing a governed system
cannot afford to lose. If a plan is wrong, the correction belongs in the document that is
still authoritative — the spec, [`../roadmap.md`](../roadmap.md), or a working note.

The one exception is a change that preserves the claim exactly while fixing how it is
*addressed* — the relative links repointed when these files moved out of `.planning/` are
the whole of it.

## The four kinds of file

| Suffix | Written by | Holds |
|---|---|---|
| *(none)* | `writing-plans` | The plan — goal, architecture, tasks, bite-sized steps |
| `-ledger` | `subagent-driven-development` | What execution actually did, task by task |
| `-final-review`, `-verified` | a review pass | Findings against a finished branch, and their verdicts |
| `-handover` | a session ending mid-work | State a successor session needs to resume |

## Naming

`YYYY-MM-DD-<slug>.md`, dated when the file was started.

**`ls docs/plans/` is the index.** There is deliberately no hand-maintained list of contents
in this file: the date prefix already sorts the directory chronologically, and a list that
nothing enforces goes stale — the lesson `CLAUDE.md` §0 records about counts and §9 records
about restating the roadmap.

## Writing one so it passes the audit

Four conventions, each of them a check that will otherwise fail:

1. **Relative links resolve from `docs/plans/`** — a spec is
   [`../specs/01-data-management.md`](../specs/01-data-management.md), the roadmap is
   `../roadmap.md`, the repository root is `../../`.
2. **Every `FR-`/`NFR-` id you cite must already be defined in a spec.** The exception is
   the id a plan intends to *take*, which the audit accepts only after a `Next free:`
   marker, as in — "Highest ids in use: FR-DATA-52. Next free: `FR-DATA-53`". The exemption
   covers the rest of that line only; an undefined id before the marker, or on any other
   line, still fails.
3. **Markdown table rows must match their header's cell count.** A literal `|` inside a cell
   shifts every column after it while still rendering, so escape it as `\|`.
4. **Every `ADR-NNNN` you cite must have a file** in [`../adr/`](../adr/).

Run `python3 scripts/audit-docs.py` before handing a plan off.

## The conventions the audit cannot check

The four above are enforced; these three are not. The gate reads documents and never the
Python a document quotes, so every literal in a plan is taken on trust by an executor who
has no context to check it against.

1. **Verify every repository literal against the shipped source before it enters sample
   code** — enum members, fixture and factory names, route paths, status codes, model field
   names. Grep each one. They are facts about the repository rather than choices the plan is
   making, which is exactly the class a fresh executor cannot sanity-check. The W6b-13b plan
   posted `"layer": "distribution"` where `ValidationLayer` defines `"distributional"`,
   because the literal was written from memory.

2. **State a predicted failure by its cause, not its status.** "Expected: FAIL with 422" is
   not a test. A status code is a many-to-one projection of causes, so a second fault the
   plan introduced can satisfy the prediction and buy confidence for it — and the test then
   keeps failing after the implementation is correct, pointing at the executor. The same
   step predicted a 422 from `extra="forbid"` and got one, with a second error beside it
   that the status hid. Write the discriminator in: name the mode, and say that a matching
   status with a differing reason is a plan defect.

3. **Run rule 1 against the shipped source, not the plan's own prose.** A plan that quotes
   itself agrees with itself — a literal repeated across two tasks is self-consistent
   whether or not it is right, and re-reading the plan cannot separate the two. Where you
   cannot verify, name the authority instead of supplying a sample: "mirror the neighbouring
   test rather than the sample; do not reinvent the module's fixtures" caught a second
   W6b-13b mismatch the plan's own text could not.

**A missing neighbour is a scope finding.** Rule 3's fallback assumes there is something to
mirror. Before writing sample tests for a module, grep its test file for the verb under
test; a zero means that path has no coverage at all, which is larger than a formatting
detail and belongs in the plan's scope section rather than in its samples.

The gate does reach one of these from the document side, and *how* it did is the useful part,
because the obvious fix was the wrong one. `audit-docs.py` rejected a threshold copied
byte-for-byte out of `pricing-core`: `min_severity_minor` written as `0.0`, a `_minor` field
carrying a fraction, which FR-OVR-7 forbids because money is integer minor units. Rewriting
the plan's value as `0` satisfied the gate.

It was the wrong half. Mean severity is a **ratio**, kept float deliberately — rounding a mean
to whole minor units loses the precision the confidence interval beside it expresses — and
`_minor` is reserved for integer minor units. The value was right; the **name** was the defect.
FR-DATA-46 renamed the profile row's two mean fields for exactly that reason, and its own
**2026-08-19 correction is the same mistake a second time**: the rename "carried the *names*
and left the *types*", so the published contract went on asserting the rounding the requirement
forbids, and nothing caught it because every conformance test compared field names only.

Two rules, then. **Run the gate early enough that its answer can still change the plan** — that
half held, and it is why any of this surfaced. And **when a check fires on something you copied
out of the source, establish which half it is pointing at before you change either one.** An
edit that stops the alarm is not evidence the alarm was about the thing you edited. That is
rule 2 one level up, applied to a check rather than a prediction: a true signal, a plausible
reading of it, and a fix that silences it without touching what it was reporting.


## Live plan state is *not* here

`planning-with-files` keeps an agent's working memory — `task_plan.md`, `findings.md`,
`progress.md` — in `.planning/`, and `subagent-driven-development` keeps its per-plan
workspace in `.superpowers/sdd/`. Both stay git-ignored. They are a running session's
scratch, rewritten every few turns; this directory holds the finished record.
