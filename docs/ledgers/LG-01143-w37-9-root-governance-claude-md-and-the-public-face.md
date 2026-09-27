---
id: LG-1143
family: ledger
title: W37-9 — root governance, CLAUDE.md and the public face
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-09-27
owner: executor
tree: 823a75efb5da70d8c652c91fd6dc54e5ab966149
phase: P2
work: WK-697
plans: [PL-1072]
corrected_by: []
relates: []
---

# LG-1143 — W37-9 — root governance, CLAUDE.md and the public face

Executed task by task from `PL-1072` (`status: active`, frozen 2026-09-27), under
`RL-1142` (DP-1 (c), DP-2 (b), DP-3 (b), DP-4 (a), DP-5 (a)). Cut from `origin/main` at
`823a75efb5da70d8c652c91fd6dc54e5ab966149` (#816, RL-1142 + PL-1072 activation). **One
PR, one branch (`w37-9-root-governance`)**, per the plan's own Task 9 and the lead's
09:02:53 BST addendum — so every task commit below is pre-squash by construction:
**cited as "pre-squash branch commit of this PR, reachable via `refs/pull/<PR>/head`"**,
never as a squash SHA. This PR's own squash SHA on `main` is recorded once, in the
closing record, the same convention `LG-01141` uses for its final PR.

## Tasks

### Task 1 — `CLAUDE.md` §2 and §4, the layout tree and module map

Fixed the mangled `WF-698…05` range to the five ids individually (`WF-698`…`WF-702`);
added `docs/INDEX.md` and `docs/process/document-ids.md` pointers to §4; added one
sentence to §2 naming `document-ids.md` §1.4 as the `docs/` layout authority. Dated
amendment (F49's CI enforcement) kept verbatim. `python3 scripts/audit-docs.py` →
`EXIT=0`.

Landed in: this PR — pre-squash branch commit `bbd6c567`, reachable via
`refs/pull/<PR>/head`.

### Task 2 — `CLAUDE.md` §5 and the §0 bullet, G2's permanence yield

Both permanence sites (`:27`, `:117`) edited in one commit, each with a dated line
naming RFC-937 D2. DP-1 (c) applied: the third "permanent" hit (§12) left unedited as a
citation of §5. **Corrected in a second commit**, per the deputy's review: both stamps
renamed to name the amending authority — "Amended 2026-09-27 by the maintainer (dated
line by delegation, D3), on RFC-937 D2" — since an amendment to what `CLAUDE.md`
requires is the maintainer's (§12), here by delegation.

Landed in: this PR — pre-squash branch commits `bd5d367b` (both sites) and `67e2e8a3`
(authority-wording correction), reachable via `refs/pull/<PR>/head`.

### Task 3 — `CLAUDE.md` §9, §12 and §13–§15, the pointers

§9 names a phase's rows as `WK-`/`SL-` families (no counts or status added). §12 points
at `document-ids.md` §1.6, the roles-per-family owner table. §13 gains record-destination
pointers (`CR-` `docs/closures/`, `FD-` `docs/findings/` + `register.md`, `RL-`
`docs/rulings/`, `LG-` `docs/ledgers/`); the F85 predicate clause and §14's RFC-711
citation kept unchanged. §15's own mangled `WF-698…05` token (found while auditing Task
1) fixed to the five ids. `python3 scripts/audit-docs.py` → `EXIT=0`; all four
`grep -c` counts (`docs/closures/`, `docs/findings/`, `docs/rulings/`,
`document-ids.md`) `>= 1`.

Landed in: this PR — pre-squash branch commit `3b284d8f`, reachable via
`refs/pull/<PR>/head`.

### Task 4 — `README.md`, the tour and how things are named

DP-5 (a): the closure-record link repointed from the legacy audit directory to
`docs/closures/`. Added the "how things are named" paragraph pointing at
`document-ids.md`; the DP-3 (b) branch/PR-title convention with its dated
not-yet-in-force clause; three new Explore bullets (`docs/plans/`, `docs/rulings/`,
`docs/closures/`).

Landed in: this PR — pre-squash branch commit `e312373c`, reachable via
`refs/pull/<PR>/head`.

### Task 5 — `CONTRIBUTING.md`, ids, and where the work lives

DP-5 (a): register link repointed to `docs/findings/register.md`. Added where findings
(`FD-`), proposals (`RFC-`) and rulings (`RL-`) go, keeping the "issues are intake,
register is truth" framing. Added `doc-id.py next` and the id/family rule. Added the
DP-3 (b) branch/PR-title convention, word-for-word with `README.md` up to the
not-yet-in-force clause, with the triage-mint / maintenance-item / bot-exemption detail
`README.md` points here for.

Landed in: this PR — pre-squash branch commit `a7e0bd3f`, reachable via
`refs/pull/<PR>/head`.

### Task 6 — `.github/PULL_REQUEST_TEMPLATE.md`, the required slice line

`NT-` token removed. Added the required `SL-`/`PL-` line with DP-3 (b)'s dated clause,
the triage mint, the standing `WK-` maintenance item, and the bot-author exemption — all
four clauses present. `## Scope` and `## Evidence` unchanged.

Landed in: this PR — pre-squash branch commit `f7f2552b`, reachable via
`refs/pull/<PR>/head`.

### Task 7 — `.gitignore` and the issue templates

`.gitignore`'s family sentence reworded (`PL-` `docs/plans/`, `LG-` `docs/ledgers/`,
`RL-` `docs/rulings/`, `RFC-` `docs/rfcs/`), replacing the dissolved `docs/notes/` `NT-`
form; reasoning sentences (unaudited-account argument, leading-slash anchoring note)
kept verbatim. Added DP-2 (b)'s optional `related` id field to both issue templates;
example ids (`FR-451`, `ADR-703`, `FD-00894` — the plan's own `FD-93` example was dead,
substituted) verified live. Parsed with `PyYAML` in this worktree's `.venv` (a parser
*is* available here, correcting this plan's own G4 assumption): both templates parse
clean, `bug.yml` body ids `[None, 'version', 'reproduction', 'expected', 'observed',
'context', 'related']`, `question.yml` body ids `['category', 'body', 'related']`.

Landed in: this PR — pre-squash branch commit `a318b280`, reachable via
`refs/pull/<PR>/head`.

### Task 8 — the three `M` rows, verify only

No edit; all three verify clean.

- `SECURITY.md:40` links `docs/process/security-posture.md`; the file exists.
- `.importlinter` (DP-4, fact confirmed unmoved): `grep -n '^name'` → `ADR-703`,
  `ADR-704`, `DEP-3`; both ADR files present under `docs/adrs/`; `uv run lint-imports` →
  `Contracts: 3 kept, 0 broken`, `EXIT=0`.
- `pyproject.toml` + `packages/*/pyproject.toml`: 3 `ADR-` ids (703, 704, 707) and 13
  distinct `FR-` ids cited in comments; every one resolves (`ADR-` under `docs/adrs/`,
  `FR-` bold-defined in `docs/specs/`). No `NFR-` cited, no unresolvable id.

No commit — evidence recorded here and in the PR body's disposition table.

### Task 9 — this ledger, the full gate, the disposition table, the PR

This file. The §2b mitigation re-run (`FD-1066`…`FD-1069`, all filed, all owned by
`W37-11`, none naming a §5.1 file this slice owns). `docs/INDEX.md` regenerated,
byte-stable (`doc-index.py --check` → `EXIT=0`). The full two-half gate, run at this
PR's final head, is recorded below.

Landed in: this PR — the ledger and gate-evidence commits, reachable via
`refs/pull/<PR>/head`; the PR's own squash SHA on `main` is recorded once, in the
closing record.

## PRs

| # | Branch | Squash SHA on `main` | Tasks | State |
|---|---|---|---|---|
| this PR | `w37-9-root-governance` | *recorded in the closing record* | 1–9 | open |

## Gate evidence

*Filled in once the full two-half gate has run at this PR's final head — see the PR
body for the per-command exit-code table, `HEAD.txt`, and `--collect-only` totals.*
