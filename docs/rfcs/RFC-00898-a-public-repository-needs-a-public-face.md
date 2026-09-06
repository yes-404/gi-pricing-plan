---
id: RFC-898
family: proposal
kind: process
title: A public repository needs a public face
status: draft                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-08-30
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this RFC itself corrects a frozen record
relates: []                     # ids only
was: docs/notes/0017-a-public-repository-needs-a-public-face.md
---

# A public repository needs a public face

One-line thesis: the repository went public on 2026-08-30 with no root README, no
security-reporting channel, and no contribution policy — so the first file a visitor
meets is `CLAUDE.md`, the first vulnerability report will arrive as a public issue, and
the first well-meaning external PR will enter a machine whose rules are invisible to its
author. Three files and two settings fix all of it.

## 1. Motivation (measured at `7db62ca`)

- `ls README* CONTRIBUTING* SECURITY* CODE_OF_CONDUCT* CHANGELOG*` → only `LICENSE`
  exists. There is **no root README**; GitHub renders the file list, and the most
  prominent markdown a visitor can click is `CLAUDE.md` — an internal charter, presented
  as a front door.
- `.github/` contains `workflows/` only — no issue templates, no PR template, so external
  intake arrives unstructured or not at all.
- `git ls-remote --tags` → zero tags; no release, changelog, or version signal exists
  (out of scope here — versioning is its own note — but it compounds the "is this
  maintained?" ambiguity a README must answer).
- Precedent for the risk class: F49 — publication converted an unchanged internal
  practice into a disclosure, because "the context moved underneath" the team. The same
  conversion is pending for security reports and external PRs: current practice (register
  intake, maintainer-only merges) is fine and *invisible*, which on a public repo is the
  defect.

## 2. Proposal — three files, two settings, one checklist line

### P1. Root `README.md`

Content, in order: what the platform is (one paragraph, drawn from CLAUDE.md §1's
mission, rewritten for an outside reader, never copied); what state it is in (a single
sentence **pointing at** `docs/roadmap.md` — see C1); how it is built (short, honest:
an AI agent team operating under `docs/process/delivery-process.md`, with the register
and closure records public — this is the repository's most distinctive public feature,
lead with it rather than hedging it); how to explore (`docs/specs`, `docs/adr`,
`docs/findings/register.md` as the tour stops); how to engage (pointer to CONTRIBUTING and
SECURITY); license line.

### P2. `SECURITY.md` + private vulnerability reporting

- Settings: enable **Private vulnerability reporting** (Code security), so reports have
  a non-public path *before* the file advertising it lands.
- File: supported scope (the deployed surface once WK-674 exists; until then, the codebase
  as published), the private-report route as the only route, a response expectation
  stated honestly (acknowledge within N days — §5 Q3 rules N; no bug bounty), and what
  happens next (triaged into the internal process; reporter credited unless they decline).
- Relation to `docs/process/security-posture.md`: SECURITY.md is the outward one-pager;
  the posture doc stays the internal record. One direction of reference — SECURITY.md
  cites the posture doc, never restates it (C1).

### P3. `CONTRIBUTING.md` + `.github` templates

The file is a policy ruling wearing a filename, so the ruling comes first (§5 Q1). The
draft posture, for the maintainer to confirm or overturn:

- **Issues and questions welcome** — bug reports, questions on the specs/process,
  suggestions. Two issue forms: *bug report* (version/tree, reproduction, expected vs
  observed) and *question / suggestion* (freeform with a category dropdown).
- **PRs by invitation for now.** Stated kindly and with the reason: the team operates a
  documented agent process with maintainer-only merges; unsolicited PRs cannot enter it
  yet. Point at the process spec so the statement reads as transparency, not gatekeeping.
  Invite issues instead; note the posture will be revisited (this note's successor when
  contributors are real: CODE_OF_CONDUCT, CODEOWNERS, DCO — deliberately not now, §4).
- **PR template** exists anyway (invited PRs and the agents' own use): scope line,
  work-item id, the §15 evidence discipline in one sentence (name the command, totals,
  tree).
- Intake rule, one paragraph (the anti-RFC-756 clause): **issues are intake, the register
  is truth.** Triage converts a substantiated issue into a register row / OQ / task; the
  issue then links the internal artifact and closes or tracks. One flow direction; no
  second findings ledger.

### Settings (both one-click, both named so the acceptance standard can check them)

1. Private vulnerability reporting: **on** (P2).
2. Issues: **on** with the two templates; blank issues allowed (a template that blocks a
   confused reporter is worse than an untidy issue).

### The checklist line (custody — C2)

`work-item-close.md` gains one line: *"Does this close change what the README's pointers
resolve to (roadmap phase, process spec location)? If yes, update the pointer — never the
copied content, which the README must not contain."* The README is thereby owned by the
close that invalidates it, which is the only time it needs touching.

## 3. Constraints

- **C1 — The README copies nothing.** RFC-756 (duplicated status goes stale) is the
  binding precedent: every fact in the README that exists elsewhere is a *pointer*, not a
  copy. The status sentence names the roadmap; the mission paragraph is a rewrite for a
  different audience (allowed — different artifact, different reader), not an excerpt.
- **C2 — Living files need owners.** README/SECURITY/CONTRIBUTING are living documents in
  a repository of mostly frozen ones; each therefore names its update trigger (README:
  the close checklist line; SECURITY: WK-674's deployment changes scope; CONTRIBUTING: the
  posture ruling's own revisit clause). A living file with no trigger is F31's shape.
- **C3 — Nothing here promises process.** The files describe what the team already does
  (register intake, maintainer merges, private triage). Any sentence that would require
  *new* behaviour to be true is out of scope for this note and belongs to its own ruling.

## 4. Non-goals

Versioning/tags/CHANGELOG (own note — pairs with milestone policy); CODE_OF_CONDUCT,
CODEOWNERS, DCO, Discussions (when external contributors are real, not before); any
change to the merge policy itself (P3 *states* it, C3); a docs site.

## 5. Open questions (maintainer — all three are policy, none mechanical)

- **Q1 — The contribution posture**: confirm "issues welcome, PRs by invitation," or open
  further. This is the note's one real decision; everything else is drafting.
- **Q2 — README status granularity**: pointer-only (recommended, C1), or pointer plus one
  generated badge (CI status is the only fact that self-updates and so cannot go stale).
- **Q3 — SECURITY.md response window**: N days to acknowledge. Recommend 7 — honest for a
  part-time maintainer; an aspirational 48h that slips is worse than a kept week.

## 6. Impact matrix

| # | File / setting | Change | Nature |
|---|---|---|---|
| 1 | `README.md` | P1 | New |
| 2 | `SECURITY.md` | P2 | New |
| 3 | `CONTRIBUTING.md` | P3 | New |
| 4 | `.github/ISSUE_TEMPLATE/bug.yml`, `question.yml` | P3 forms | New |
| 5 | `.github/PULL_REQUEST_TEMPLATE.md` | P3 | New |
| 6 | Repo settings | Private vuln reporting on; issues on | Settings |
| 7 | `docs/process/checklists/work-item-close.md` | C2 pointer-freshness line | Amend |
| 8 | `docs/process/security-posture.md` | One line: SECURITY.md is the public face of this doc | Amend |
| 9 | `docs/roadmap.md` | This Work's row | Amend |

Deliberately unchanged: `CLAUDE.md` (internal charter stays internal — the README now
absorbs the front-door role it was accidentally playing), `LICENSE`, merge policy, all
process documents beyond the one checklist line.

## 7. Adoption

Small enough for the light path: freeze → maintainer rules Q1–Q3 (no full reconcile
needed — flag for the lead to confirm this note qualifies) → one Work, two slices:
**S1** = settings + SECURITY.md (the private channel must exist before anything
advertises the repo — ordering is the slice's one constraint); **S2** = README +
CONTRIBUTING + templates + checklist line. Audit: fresh-context read as an outsider —
the auditor's charter fits naturally ("would it resolve for a reader holding none of
your context" is literally the README's acceptance test). No pilot needed; the first
real external issue is the pilot.

## 8. Acceptance standard (draft)

Complete when: **(a)** all five files exist and every internal link resolves at the close
tree (link-check command named); **(b)** private vulnerability reporting is enabled —
settings-side, so evidenced by a dated maintainer line in the closure record, the same
convention as any human checkpoint; **(c)** a test issue filed through each form renders
with its fields; **(d)** the README contains zero sentences duplicating roadmap or
CLAUDE.md content (checked by the auditor's outsider read, verdict recorded); **(e)** the
close checklist carries the pointer-freshness line. Command, totals, tree per §15.
