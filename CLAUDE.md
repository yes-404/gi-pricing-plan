# CLAUDE.md — GI Pricing Platform

Binding rules for every AI session in this repository. Rules live here; procedures live in
`.claude/skills/` and `CONTRIBUTING.md`, which this file cites and does not restate.

## 1. Mission

An open-source general insurance pricing platform for the UK and EU market: data
preparation, risk modelling (GLM and ML), rating, deployment and scoring, monitoring,
governance. Users are pricing actuaries and analysts. Every design choice favours
reproducibility, auditability and transparency of the maths.

## 2. What to deliver

| Request | Deliverable |
|---|---|
| Inside the current milestone's scope | Code, plus any spec change it proves necessary, together |
| A capability not yet specified | The spec change first, then code |
| A later milestone | A spec change only. Never build ahead |
| A design choice the specs leave open | A decision-needed issue with options and a recommendation. Never a silent pick |

- **The specification is the contract.** Read the relevant spec before writing the code that
  implements it. `docs/README.md` indexes the suite.
- **When code and spec disagree, stop and resolve it.** Do not quietly make either match the other.
- **The current milestone and its scope are on GitHub**, not in this file.

## 3. Requirements and specs

- **Requirement ids are permanent.** Append or mark superseded. Never renumber or reuse.
- Every spec keeps its ten sections. The procedure is `.claude/skills/spec-change`.
- A term is defined in `docs/specs/00-overview.md` §2 before its first use.
- Run `python3 scripts/audit-docs.py` before committing any spec change.

## 4. Architecture rules (decided; reopen only with a decision record)

- **One contract, flowing one way:** `model-schema` generates `docs/contracts/`, which
  generates the frontend API client. Generated files are regenerated, never edited.
- **No shape that exists in `model-schema` is written by hand a second time**, in the
  backend, the frontend or a test.
- `pricing-core` stays importable alone: no FastAPI, SQLAlchemy or Redis dependency.
- Models and rating definitions are declarative JSON artifacts, never pickles.
- No pandas in new code. Vue 3 Composition API with `<script setup lang="ts">` only.
- `uv.lock` is committed. The stack and where each part is used: `docs/skills-map.md`.

## 5. Domain rules (breaking one is silent)

- A **Dataset** is a named container. A **Dataset Version** is the immutable snapshot.
  Modelling references a Dataset Version, never a Dataset.
- **Money is integer minor units, or Decimal in the rating path. Never float.**
- A `control` Factor never moves a price (FR-88, FR-240).
- The actuarial defaults are numbered requirements, not conventions: `02-modelling.md`
  FR-MODEL-19, 21, 26, 27, 28 and 33.
- Only public data (freMTPL2). No real policy, claims or exposure data anywhere, including
  in a prompt to an external tool.

## 6. Evidence

- **Scope is derived from the specification, then evidenced.** Never from memory of what was built.
- **Every requirement without evidence gets a verdict:** delivered but untested, deferred
  with an owner, reassigned, or not started. Silence is not one of them.
- **Budgets are measured, not asserted.** A check that has never failed on broken input is untested.
- **A fix is shown failing first.**
- **A count names its commit, its corpus and the command that produced it.**
- **Name the range (`origin/main...branch`), not the tip. Verify the claim, not the citation.**
- **A severity is set by a probe, not by words.**

## 7. How work runs

The rules are in `CONTRIBUTING.md`. In short:

- Work is arranged on GitHub: a milestone per version, one issue per Work, one pull request per Work.
- **Decisions that bind the product are files:** `docs/adrs/`, numbered, superseded and
  never edited. A decision reached in an issue is written there by the pull request that enacts it.
- **Only the maintainer** decides a milestone's scope, accepts a Work, closes a milestone and
  amends this file. The lead merges. A subagent gathers evidence and decides nothing.
- Review follows risk. The high-risk areas are listed in `CONTRIBUTING.md`.
- A possible wrong price or security defect is reported privately: `SECURITY.md`.

## 8. How a session works

- **Run the whole gate before pushing, both halves.** Commands and their traps:
  `.claude/skills/dev-commands`.
- **Skills come first.** `.claude/skills/README.md` is the index. A procedure found to be
  missing or wrong is written or fixed in the same session.
- **Keep context light.** Delegate noisy searches to a subagent. Read bounded ranges, not whole files.
- Conventional Commits. Short-lived branches from `main`.
- **Never bypass a commit hook**: no `--no-verify`, no `core.hooksPath` override. A commit the
  hook refuses is fixed, or reported to the maintainer; it is never worked around.
- **Never** put a session link in a commit, pull request or issue. Never install an external
  skill or agent without the maintainer's approval. Never modify `~/.claude/skills/`.
- AI use is disclosed in every pull request, and a named person is accountable for it.

## 9. History

This file replaced a longer, section-numbered version as decided on 2026-11-13 (decision record ADR-8449).
That version, and the plans, ledgers, rulings and closure records it governed, are frozen
in git history and in `docs/archive/`. A citation of an old section number refers to that version.
