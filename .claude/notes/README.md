# Working notes

Notes from the maintainer to Claude Code: requests, standing intentions, and the assessment
each one got before work started.

**One file per topic**, numbered `NNNN-kebab-title.md` and identified as **`NT-0001`** — the
same convention as [`docs/adr/`](../../docs/adr/README.md), for the same reason. Not per
day: a topic is worked, argued about and closed on its own schedule, so a date-named file
mixing two of them ages into a record where half is stale and half is live, with nothing to
say which. Dates belong in the header block, where they describe the *topic*.

`NT-` follows the short-prefix family the suite already uses — `FR-`, `NFR-`, `OQ-`, `DEP-`
— rather than spelling the word out, and the four digits match `ADR-NNNN`, so the repository
has one padding width for file-per-item series rather than two. The filename carries exactly
the digits the id does: **`NT-0001` lives in `0001-…md`**, one number to read, not two
spellings of it.

The number is the note's permanent identity, and it behaves as an ADR number or an `FR-` id
does under `CLAUDE.md` §5: **assigned once, never renumbered, never reused.** A note that is
dropped or deleted retires its number with it, so a reference written in a commit message or
a roadmap row can never silently come to mean a different topic later.

```bash
# Next number. Same command as adr-write, pointed at this directory.
ls .claude/notes/ | grep -oE '^[0-9]{4}' | sort -n | tail -1
```

**A note is not authoritative.** `docs/` is the contract and `CLAUDE.md` is the working
standard; a note is the raw material that may *become* a spec change, an ADR, an entry in
`docs/open-questions.md`, or a roadmap row. Nothing here decides anything — if a note's
conclusion matters after the session that produced it, it belongs in the suite, and the note
must say where it went.

## Index

| Note | Title | Raised | Status | Deliverable |
|---|---|---|---|---|
| [NT-0001](0001-phase-boundary-plan-review.md) | Plan review at each phase boundary — completion, omission, skills, drift, shape | 2026-08-15 | `landed` | Standard → `CLAUDE.md` §14; trigger → `roadmap.md` |
| [NT-0002](0002-demo-entrance-and-guide.md) | Demo entrance, with a guide to what is testable | 2026-08-15 | `landed` | Spec first (FR-PLAT-53/54), then the code as **W7b** — `scripts/demo.py`, `/demo`, and a guide derived on every request |
| [NT-0003](0003-duplicated-status-goes-stale.md) | Duplicated status in `CLAUDE.md` goes stale — the phase line, the counts, the roadmap restatement, the second skill list | 2026-08-23 | `landed` | Rules → `CLAUDE.md` §0, §2, §9; **no code, no spec change** |
| [NT-0004](0004-a-reference-that-resolves-only-for-the-writer.md) | A reference that resolves only in the writer’s context — ten instances in one day, and one mechanical rule | 2026-08-24 | `landed` | Rule → `CLAUDE.md` §13, fourth bullet; **no code, no spec change** |
| [NT-0005](0005-deferred-items-with-no-durable-custody.md) | Seven deferred items with no durable custody — found during W6b, held only in a session's working memory | 2026-08-24 | `landed` | Filed 2026-08-27 via #276 — five items in place, (c) and (g) recorded discharged in `docs/audit/register.md` |
| [NT-0006](0006-two-rules-for-reading-an-artifact.md) | Two rules for reading an artifact — the tip commit that is not the change set, and the citation that is right about the wrong content | 2026-08-24 | `landed` | Rules → `CLAUDE.md` §13, one bullet; **no code, no spec change** |
| [NT-0007](0007-context-bound-measures-cap-not-discipline.md) | "Zero calls above 200k" measures the compaction cap, not discipline — a boundary metric reads as zero by construction | 2026-08-25 | `landed` | Rule → `CLAUDE.md` §10, third bullet; **no code, no spec change** |
| [NT-0008](0008-project-closure-audit-structure.md) | A closure-audit structure for work items and phases — per-work-item and per-phase records, two registers, conventions | 2026-08-27 | `landed` | Structure filed 2026-08-27 via #276 — `docs/audit/` record layer + `CLAUDE.md` §14 third rule |
| [NT-0009](0009-slim-the-roadmap.md) | Slim the roadmap — split the forward-looking plan from the archive (closure records, plan reviews, retrofit list) | 2026-08-27 | `landed` | Archive moved 2026-08-27 via #274 — historical record in `docs/audit/`, roadmap forward-looking |
| [NT-0010](0010-layered-slice-based-workflow.md) | A layered slice-based workflow — Project → Phase → Work → Slice, gated at every layer | 2026-08-29 | `superseded` | `docs/process/delivery-process.md`, `.claude/roles/*.md`, `CLAUDE.md` §12; **no `docs/specs/` change and no product code**. Reconciled and ruled in `docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md` |
| [NT-0011](0011-per-agent-model-and-skill-settings.md) | Per-agent model, thinking effort and skill bindings for the seven roles | 2026-08-29 | `superseded` | `.claude/roles/*.md`, `docs/process/agent-settings.md` (not `.claude/agents/` — this note's own text named the wrong directory; corrected during implementation) |
| [NT-0012](0012-a-credential-is-borrowed-not-stored.md) | A credential in an ephemeral job directory is borrowed, not stored, and is found by its shape, not its container's name | 2026-08-29 | `open` | Rules only; lands in a role file's credential duty and a search-discipline skill, neither chosen yet |
| [NT-0013](0013-the-lead-is-the-highest-error-node.md) | The lead is the highest-error node — eight relay-error instances evidencing the claim `lead.md` now states, and what actually caught each | 2026-08-29 | `open` | Evidence only; the receiving-half mitigation already landed in `delivery-process.md` §15, "remove the relay" not yet landed anywhere |
| [NT-0014](0014-machine-readable-process-core.md) | A machine-readable core for the delivery process — a JSON extract, a runtime state file and four deterministic scripts, closing three enforcement gaps the process spec names in its own text | 2026-08-30 | `accepted` | **Slices A–D merged 2026-08-30** — the process core is filed at `docs/process/delivery-process.core.json` and citation-checked by `audit-docs` check 26; NT-0012's and NT-0013's rules landed with them. **E, F and G remain.** Rulings 40 and 45–48 settled its four open questions
| [NT-0015](0015-the-register-is-a-ledger-evidence-is-a-file.md) | The register is a ledger; evidence is a file — name the register's decision grammar, give unowned rows a decay rule, lint what is named, split the ledger from its evidence, and generate the owed list a close currently compiles by hand | 2026-08-30 | `open` | Nothing yet — proposed, not adopted. Its §5 impact matrix names 15 targets if adopted; an optional ride-ahead PR (grammar + decay sentence only) may land ahead of the rest |
| [NT-0016](0016-file-taxonomy-reference-coding-and-custody-investigation.md) | File taxonomy, reference coding, and custody investigation — a closed category set with a home-by-consumer boundary rule, a reference standard per category, an ownership map, and a workflow-loop audit of whether every category is genuinely created-read-retired | 2026-08-30 | `open` | Nothing yet — proposed, not adopted. Investigation (census + taxonomy draft) precedes any spec/doc change; §3a proposes moving `.claude/notes/` itself to `docs/notes/` |
| [NT-0017](0017-a-public-repository-needs-a-public-face.md) | A public repository needs a public face — a root README, `SECURITY.md` with private vulnerability reporting, `CONTRIBUTING.md` with issue/PR templates, and one close-checklist line, so the repository has an outward front door, a private disclosure channel and a stated contribution posture | 2026-08-30 | `open` | Nothing yet — proposed, not adopted. Its one real decision (contribution posture) is the maintainer's, at §5 Q1 |
| [NT-0018](0018-a-turn-that-ends-strands-what-it-started.md) | An agent's turn ending strands everything it started — one invariant, two directions, six occurrences in one day, and two merged fixes that each named the mechanism instead | 2026-08-31 | `open` | Nothing yet — proposed, not adopted. No code and no spec change; §6's five options land in `.claude/roles/*.md`, `.claude/skills/dev-commands`, or `docs/process/delivery-process.md`, none chosen. §7 Q3 is the maintainer's |

## What a note must contain

A header block of exactly these fields, then the body.

| Field | Why |
|---|---|
| **Raised** — date and who | An undated intention ages into a false record of what was wanted, and when |
| **Status** — `open` · `accepted` · `landed` · `superseded` · `dropped` | See the verdicts below. There is no "unstated" |
| **Deliverable** — named per `CLAUDE.md` §0's table: code, spec change then code, spec-change-only, or an `OQ-` entry | §0 is the project's rule for what a request produces; a note that skips it invites building ahead of the phase |
| **Owner** — who accepts, who drafts | A proposal with no acceptor never becomes a decision |
| **Lands in** — the paths and sections the outcome will change | The note is the input; the suite is the output |
| **Sequencing / Trigger** — when this becomes workable | Distinguishes "not yet" from "not agreed" |

The body carries: the request in refined form, **Claude's assessment attributed and kept
separate** from the maintainer's words, acceptance criteria, the next step, and the original
wording. That last section is corrected for grammar and punctuation only — never for
wording, structure or meaning — and says so, so that "original" stays a true label rather
than a courtesy. Keeping the two voices apart matters for the same reason `CLAUDE.md` §0
refuses to let code and spec be quietly reconciled — merging them destroys the record of who
believed what.

## What a note must not contain

- **Decisions.** A choice constraining more than one module is an ADR
  (`.claude/skills/adr-write`); an unresolved one is an `OQ-` entry in
  `docs/open-questions.md`. Never settled in a note.
- **Requirements.** `FR-`/`NFR-` IDs are permanent and live in `docs/specs/` only
  (`CLAUDE.md` §5). A note may *propose* one; it may not carry one.
- **Duplicated status.** Workstream and phase state lives in `docs/roadmap.md`. A note that
  restates it will disagree with it within a week.
- **Secrets, credentials, or dataset contents** — `.claude/skills/secret-hygiene`.

## The audit standard

**Half of it runs in CI; the other half cannot.** `scripts/audit-docs.py` checks 16–20 cover
this directory, and `.github/workflows/docs.yml` includes `.claude/notes/**` in its path
filter, so a note-only commit runs them. What the script cannot answer is whether a status is
*true* — that is judgement against the repository, and it stays manual.

**When:** the mechanical half on every commit that touches a note, via CI or
`python3 scripts/audit-docs.py` locally. The judgement half at every workstream close, in
the same pass as `close-workstream`.

**Seven checks. Each note, every time** — the ⚙ ones are enforced by the script, and the
rest are yours:

1. **Status is verified, not remembered.** Check it against `docs/roadmap.md` and the git
   log, not against what you recall doing. This is `CLAUDE.md` §13 step 1's rule — evidence
   before recollection — applied to the notes themselves. *(Manual: the script can see that
   a status is well-formed, never that it is true.)*
2. ⚙ **Every reference resolves.** Relative links, `FR-`/`NFR-` ids, `OQ-` ids and ADRs are
   checked by check 19. Prose references — a spec §, a test name, a symbol — are yours. A
   note pointing at something that no longer exists is a defect in the note, and it is the
   most common way one turns into fiction: the claim still reads true.
3. ⚙ **Every topic has a verdict.** One of the five statuses, never silence — check 16
   enforces the header block and the vocabulary. That `landed` records *where*, and
   `dropped` *why*, is manual: the reasoning is the part worth keeping and no script can
   judge it.
4. ⚙ **The prohibitions hold.** Check 20 refuses a note that *defines* a requirement id.
   Decisions and duplicated roadmap status are manual — they are recognisable only by
   meaning.
5. **The deliverable still matches `CLAUDE.md` §0** for the phase the project is *now* in. A
   topic scoped to code before its phase has started is spec-change-only until then, and a
   note carrying a stale deliverable is an invitation to build ahead of the phase.
   *(Manual — check 16 asserts the field exists, not that it is right.)*
6. ⚙ **Numbers are intact.** Four digits, unique, allocated in sequence from `0001`, and
   matching the `NT-NNNN` in the file's own heading — check 17. No number reused, no note
   renumbered: a deletion leaves a gap, and the gap is correct, so contiguity is deliberately
   *not* asserted. This is what `docs/adr/README.md` calls "never renumbered" and
   `CLAUDE.md` §5 requires of requirement ids; a recycled number is worse than a missing one,
   because every earlier reference to it silently repoints. **Reuse across a deletion is the
   one part no snapshot can catch** — the retired number is gone from the tree — so that
   remains yours.
7. ⚙ **The index above matches the files.** Check 18, both directions: every note listed,
   every listed row backed by a file, and the number, link target and status agreeing in both
   places.

**Verdicts, and what each obliges:**

| Status | Means | Obligation |
|---|---|---|
| `open` | Raised, assessed, not agreed | Nothing is built |
| `accepted` | Maintainer agreed, with a date | Named in a roadmap row before work starts |
| `landed` | The outcome is in `docs/` or the code | Record where; delete the note at the end of the phase, keeping the index line and its number |
| `superseded` | Another note or an ADR replaced it | Link the replacement by number — `NT-NNNN` or `ADR-NNNN` |
| `dropped` | Decided against | Record why — a dropped idea with no reason returns |

**The failure this standard exists to prevent:** a directory of confident-sounding notes
that describe a repository which has moved on. That is worse than an empty directory,
because it is read as current — the same argument `CLAUDE.md` §13 makes about a
silently-passing check being worse than no check.

## Tracking

`.claude/notes/` is not in `.gitignore`, so these files are committable and currently
untracked. Commit a note when its assessment is the record of why something was or was not
built. A `landed` note is deleted at the end of its phase — git keeps the history, and the
index line keeps the pointer.
