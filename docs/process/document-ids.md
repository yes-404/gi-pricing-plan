# Document IDs — one id per governed thing, one sequence, roles per family

Lifted verbatim from [`NT-0019`](../notes/0019-one-id-per-document.md) §1.1 through §1.13,
accepted by the maintainer 2026-09-01 — every rule and decision below is the maintainer's,
not reworded, reordered or improved on the way in. The note also carries what argued for
this standard and is not reproduced here: the decisions (§2), an illustrative numbering
walkthrough (§3), the migration procedure (§4), the impact map (§5), the rituals adopted
(§6), the acceptance items (§7), the sequencing (§8), the relation to NT-0016 and Rulings
55-65 (§9), and the evidence it was measured against (§10). A cross-reference below to one
of those numbers — `§4`, `§10` and so on — points into the note, not into this file.

## 1.1 Four rules

1. **A governed thing's id is `<PREFIX>-<n>`; `n` is an integer from one sequence shared by every family.** `FR-1187` is a requirement, `WK-1201` a work item, `PL-1240` a plan, `RL-1241` the ruling filed after it. No number is used twice. The prefix says what kind of thing; the number says which one, uniquely, project-wide. (Kubernetes: `KEP-1234` is issue #1234 in one global space; Jira: one key sequence per project across every item type.)
2. **Citations write the integer, never padding:** `PL-1240`, `RL-65`, `RFC-16`, `FR-1187` — as PEP 8, RFC 2094 and KEP 1234 are written. A padded id in prose is a lint error. **No exception**: prose, headings (`# RL-1241 — …`), commit messages, PR titles, branch names, code comments, docstrings, test markers, link text.
3. **Filenames pad the integer to the standard's width, currently five:** `PL-01240-<slug>.md`. Padding exists so `ls` sorts; it is not identity. The resolver treats `PL-1240`, `PL-01240` and `PL-001240` as one id. Widening is a rename of files and a rewrite of link targets — one mechanical PR that touches no citation, number, header or body line (§1.8).
4. **Two things are outside the standard, on principle:** a **phase**, which is a milestone label (`P2`), cited as a placement (`phase: P2`), never as a document (§1.3); and a **product identifier** — any id that is stored, transmitted or asserted by an API contract (`VR-DST-1`, artifact ids, job kinds) — which is product data governed by `docs/specs/`, and which this standard never touches.

## 1.2 Families — rows and documents, one sequence

| Kind | Family | Prefix | Lives in | Unit | Mutability | Status subset (§1.2a) | `kind:` |
|---|---|---|---|---|---|---|---|
| **Row** | Requirement | `FR` `NFR` `DEP` | `docs/specs/<module>.md` | one clause | living, append-only ids | active → superseded \| retired | — |
| Row | Open question | `OQ` | `docs/specs/<module>.md` §10, mirrored in `docs/open-questions.md` | one question | living row | active → closed \| retired | — |
| Row | Work | `WK` | `docs/roadmap.md`, under its milestone | one work item | living row | draft → active → closed \| retired | — |
| Row | Slice | `SL` | `docs/roadmap.md`, under its work | one unit of execution | living row | draft → active → closed \| retired | — |
| **Document** | Workflow | `WF` | `docs/workflows/` | one journey | living | draft → active → superseded \| retired | — |
| Document | Decision | `ADR` | `docs/adrs/` | one decision | frozen | draft → active → superseded \| retired | — |
| Document | Proposal | `RFC` | `docs/rfcs/` | one topic | frozen | draft → active → closed \| retired \| superseded | `enhancement` · `process` · `incident` |
| Document | Plan | `PL` | `docs/plans/` | one plan | frozen | draft → active → superseded \| retired | `map` · `leaf` · `review` · `handover` |
| Document | Ledger | `LG` | `docs/ledgers/` | one slice's execution | append-only | active → closed | — |
| Document | Ruling | `RL` | `docs/rulings/` | **one ruling** | frozen | active → superseded \| retired | — |
| Document | Research | `RS` | `docs/research/` | one spike, measurement or audit | frozen | draft → active → closed \| retired | `spike` · `measurement` · `audit` |
| Document | Closure | `CR` | `docs/closures/` | one work, phase or review close | write-once | active | `work` · `phase` · `review` |
| Document | Finding | `FD` | `docs/findings/` (register row + essay) | one finding | living row + frozen essay | active → closed \| retired; `decision:` carries the register disposition | — |
| **Reference** | — | — | `process/`, `contracts/`, every `README.md` anywhere in the tree, `.claude/roles/`, `.claude/skills/*/SKILL.md`, `.claude/agents/` | a living or generated document | living, or `generated: true` | active → retired | — |

### 1.2a One status vocabulary

Five words, with identical meaning in every family; a family uses a subset and never a synonym:

| Status | Meaning | Replaces the words used before |
|---|---|---|
| `draft` | exists, not yet authoritative or accepted | proposed, open (RFC), planned |
| `active` | authoritative, in force, or in progress | accepted, frozen, filed, ruled, living, open (OQ, LG) |
| `closed` | completed its purpose — answered, delivered, sealed, landed, resolved, promoted | landed, sealed, resolved, promoted |
| `retired` | ended without completing — withdrawn, dropped, rejected, deprecated, archived; the reason is in the body | withdrawn, dropped, archived, deprecated |
| `superseded` | replaced by a named successor in `superseded_by:` | — |

Transitions run forward only; `closed`, `retired` and `superseded` are terminal. **Mutability is a family property, not a status** (living · frozen · append-only · write-once · generated), stated once in the table above. A plan's *execution* (§1.7) is a separate, computed axis and is never written in `status:`. A finding's register disposition (`fix before close`, `accept`, `carry forward`, `split verdict`, with qualifiers) lives in its own `decision:` field, so `status:` and `decision:` cannot be confused — NT-0015 P4.

A row family's id resolves to a file *and an anchor* (`docs/specs/02-modelling.md#fr-1187`, `docs/roadmap.md#wk-1201`); a document family's id resolves to a file. Roadmap rows are headings, so their anchors exist; requirement rows are bold ids in tables, so `spec-change` emits `<a id="fr-1187"></a>` before each definition and the migration adds one for every existing clause. `INDEX.md` has one row per number for both.

## 1.3 Phase = milestone

A phase is a named, dated target that Works are attached to — GitHub's Milestone, Kubernetes' `v1.33`, Rust's `2026`. It is a label `P<n>` (`P0`, `P1`, `P2`; `P1b` is legacy, no letters from now on), defined in exactly one place, one section per phase in `docs/roadmap.md`:

```markdown
## P2 — Rating engine live
status: active            # draft → active → closed
opened: 2026-09-15
target: 2026-11-30
gates: plan freeze 2026-10-15 · code freeze 2026-11-15 · docs freeze 2026-11-25
exit criteria: WF-1188 delivered end to end; no open FD- against RATE
works: WK-1201, WK-1207, WK-1215
```

Every record that belongs to the phase carries `phase: P2` in its header — that is the whole attachment mechanism. The phase closes with one `CR- kind: phase` whose body is generated from every record carrying `phase: P2` (§1.10). Optionally mirrored as a GitHub Milestone named `P2 — Rating engine live`; the roadmap section is the source of truth, the milestone a view.

## 1.4 Layout — one directory per document family, the padded id leading every filename

```
docs/
├── README.md              the map: this tree and §1.2's table — nothing that goes stale
├── INDEX.md               generated — one row per id, rows and documents alike
├── REDIRECTS.csv          generated by the migration — every old path and old id → new id → new path
├── _templates/            one file per document family, header pre-filled
├── roadmap.md             phases (milestone sections), WK- and SL- rows, living
├── open-questions.md      OQ- mirror, living
├── specs/                 FR-/NFR-/DEP-/OQ- clauses inside 00-overview.md … 07-platform.md
├── workflows/             WF-01188-dataset-to-model.md
├── adrs/                  ADR-<nnnnn>-pricing-core-is-dependency-free.md
├── rfcs/                  RFC-00164-file-taxonomy-and-custody.md
├── plans/                 PL-01240-batch-frame-contract.md
├── ledgers/               LG-01243-batch-frame-contract.md
├── rulings/               RL-01241-batch-frame-payload-inline.md
├── research/              RS-00088-zen-evaluate-concurrency.md
├── closures/              CR-01310-p2.md · CR-01260-wk-1201.md
├── findings/              register.md · FD-00093-rating-shapes.md   (per-phase views are generated, never files)
├── process/               delivery-process.md · document-ids.md · checklists/ · agent-settings.md
└── contracts/             generated schemas + hand OpenAPI
```

The directory is the family: a file whose name does not parse to its directory's family fails lint; a file under `docs/` in no family directory that is not a `README.md` fails lint; `_templates/` is exempt from check 31 by path. Adding or removing a family requires an `RFC-` and an `RL-`. `docs/audit/` dissolves into `findings/`, `closures/`, `research/` and `process/`.

## 1.5 The header — YAML front matter, closed field set

On every document-family file, every Reference file, and (as a fenced block under the row's heading) every `WK-`/`SL-` row. Requirement rows keep the spec's bold-id convention; their fields are the spec table's columns.

```yaml
---
id: PL-1240                  # document and row families; integer form; the filename pads it
family: plan
kind: leaf
title: Batch frame contract
status: active               # §1.2a vocabulary
created: 2026-09-02
owner: planner               # a filename under .claude/roles/, or `maintainer`
phase: P2                    # every WK, SL, PL, LG, RL, CR, RS
work: WK-1201                # every SL, PL, LG, RL, CR, RS
slice: SL-1242               # PL (leaf), LG, RL where slice-scoped
tree: 8f5d57d
plans: [PL-1240]             # LG only — append-only; a ledger is keyed to its slice, and lists every plan it executed
supersedes: []
superseded_by: ~             # with `status:` (forward only) and `corrected_by:`, the only fields edited after a file freezes
corrected_by: []             # append-only; each entry is the RL-/RFC- that corrects this file (the body is never edited)
corrects: ~                  # on the correcting record: the frozen id it corrects
relates: [RFC-164, RL-65]    # ids only — never paths
was: 2026-08-18-profile-contract.md   # migration only
---
```

A vendored skill (`planning-with-files`, `ui-ux-pro-max`, `graphify`, `systematic-debugging`, the `vue-*` skills — anything shipping its own `LICENSE`) carries `vendored: true` and `origin:` on its `SKILL.md` only; the files beneath are exempt from stamping, citation rewrite and shape checks. Unknown field → lint failure. Family-specific extras (`deliverable`, `lands_in`, `trigger` for RFC; `gates`, `exit_criteria` for a phase section; `prs:` for a ledger) are declared in that family's template and permitted only there.

## 1.6 Roles per family

Principles: the role that writes code never amends the document the code is checked against (`CLAUDE.md` §0); the role that creates a record never accepts its own close; a status is set by the step that causes it, never by hand later (NT-0003); the maintainer is the scope authority and the acceptor, not a routine author.

| Family | Owner — creates & amends | Accepts / decides | Reads & acts | Verifies & closes | Supersedes / retires |
|---|---|---|---|---|---|
| **FR NFR DEP** | decision-maker, via `spec-change` | maintainer for a new module or a scope change | planner (plans against), executor (implements) | auditor — `req-coverage`, cited in `CR-` | decision-maker: `superseded` + new id |
| **OQ** | decision-maker records (anyone raises) | resolved by an `RL-` or `ADR-` | planner — an open OQ blocks the slice that needs it | decision-maker sets `closed` citing the resolver | — |
| **Phase** `P<n>` | maintainer opens the section; lead maintains it | maintainer closes | everyone | auditor files `CR- kind: phase`; lead runs `phase-review` → `CR- kind: review` | — |
| **WK** | maintainer opens (`draft`); planner writes its map plan; maintainer sets `active` | maintainer accepts the close (`closed`, `CLAUDE.md` §12) | lead runs it | auditor files `CR- kind: work` | maintainer withdraws |
| **SL** | planner, cut in the map plan (`draft`) | lead dispatches (`active`) | executor executes | auditor closes: sets the `LG-` `closed`, verifies acceptance | planner re-cuts on replan |
| **WF** | decision-maker, via `spec-change` | maintainer for a new journey | planner (`relates:` the steps a Work delivers); executor delivers and owns `test_wfNN_journey` | auditor in `CR-`; lead reads coverage at phase review | decision-maker |
| **ADR** | decision-maker, via `adr-write` (`draft`) | maintainer: `draft → active` | executor (enforced where possible — `.importlinter`) | auditor checks compliance at close | decision-maker proposes, maintainer accepts |
| **RFC** | maintainer mints and owns; any role drafts on instruction; lead assesses | maintainer: `draft → active`, or `retired` | planner cuts an active RFC into a Work | `closed` set by `close-workstream` when the deliverable ships | a later RFC with `supersedes:` |
| **PL** `map`/`leaf` | planner, via `writing-plans`; `draft` while decision points are open, `active` on freeze | decision-maker rules decision points as `RL-`, never edits the plan | executor works from it | auditor checks acceptance blocks | planner: new `PL-` with `supersedes:` |
| **PL** `review` | auditor | lead adopts/amends/rejects verdicts | executor fixes | terminal | — |
| **PL** `handover` | executor | — | the successor executor | terminal once resumed | — |
| **LG** | executor, appends per task and per PR (`active`) | — | auditor, lead | auditor sets `closed` at slice close | never |
| **RL** | decision-maker; the maintainer may author one on scope or process | — | planner and executor apply it at every site | auditor checks the sites at close | decision-maker: new `RL-` with `supersedes:`; `retired` when overridden with no successor |
| **RS** `spike`/`measurement` | executor (`library-spike`, measurements) | — | planner cites it | executor sets `active` on filing; `closed` only by citing the `FR-`/`ADR-`/`RFC-` target the decision-maker created | executor or lead: `retired` |
| **RS** `audit` | auditor — a bespoke audit's method, evidence and verdicts; files every finding as `FD-` | lead gives each `FD-` its disposition | maintainer requests it as an `SL-`; planner freezes scope in a `PL-` | the Work's `CR-` cites the record and every `FD-` it raised | lead: `closed` once every `FD-` is closed |
| **CR** | auditor (`work`, `phase`); lead (`review`) | maintainer accepts a Work or Phase close | reporter reports it | terminal | — |
| **FD** | auditor (register row + essay) | lead sets `decision:`; decision-maker when contested | executor discharges it through an `SL-` (under the owning Work, or `WK- maintenance`) that names the `FD-` | auditor sets `closed` in place citing the PR; `retired` for `accept`; unowned rows decay to the phase review | never removed |
| Reference — `process/` | maintainer; amendments arrive as `RFC-` + `RL-` | — | everyone | `audit-docs` core-JSON drift | — |
| Reference — charters | maintainer; "a role file that proves insufficient" → `FD-` → maintainer amends | — | the role at spawn | — | — |
| Reference — skills | the five roles already permitted; lead approves | — | tooling | — | lead: `retired` + a `REDIRECTS.csv` row to the successor or the `RL-` that retired it |
| Reference — agents | lead | — | dispatching roles | — | lead |
| Reference — `contracts/` | generated from `model-schema`; `gi-pricing.yaml` executor via `contract-schema` | — | — | drift guard | — |

The reporter and the watcher own no governed document: the reporter reads closures and rulings and writes the external channel; the watcher writes runtime state. Their charters say so, so the generated ownership matrix shows two deliberately empty rows rather than two gaps.

## 1.7 Citation and allocation

Prose cites `<PREFIX>-<n>`; a link carries the padded path as its target and the id as its text; the resolver is `\b(FR|NFR|DEP|OQ|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0*(\d+)\b` with a check that the prefix matches the family the number belongs to. A phase is cited `P2`, always as a placement. Bare numbers never appear in prose (`#1240` autolinks to PR 1240 on GitHub).

`python3 scripts/doc-id.py next` fetches `origin/main`, reads the maximum across every header, every spec bold-id, every roadmap row and `INDEX.md`, prints max + 1. The number is taken by the commit that adds it; a collision at rebase is fixed by renumbering the unmerged item. `doc-id.py check` fails the gate on any duplicate or header/filename mismatch. Switching to GitHub-issue-number allocation later is a policy change inside `doc-id.py`, not a renumbering.

**Reading a plan's state.** A `PL-` file carries only its document lifecycle (`draft → active → superseded | retired`). Whether it was *executed* or *completed* is never written on the file — that would duplicate what the ledger and the closure hold (NT-0003). `doc-index.py` derives it into an `execution` column in `INDEX.md`, and `doc-index.py --show PL-<n>` prints it:

| `execution` | Derived from |
|---|---|
| `not started` | no `LG-` lists `PL-n` in `plans:`; its `SL-` row `draft` |
| `in progress` | that `LG-` is `active`, or the `SL-` is `active` |
| `executed` | that `LG-` is `closed` |
| `closed` | a `CR-` cites the plan's `slice:`/`work:` and the `SL-` row is `closed` |
| `superseded → PL-m` | `status: superseded`, `superseded_by: PL-m` |
| `retired` | `status: retired`; the `SL-` is `retired` |
| `terminal` | `kind: review` or `handover` |

A map plan rolls up from its slices' leaf plans (all `closed` → `closed`; any `in progress` → `in progress`). Check 38 flags write-only plans from this column; check 33 fails when the sources disagree.

**Planning with open questions.** A plan is allocated at draft (`status: draft`), so rulings have an id to cite. Every question the planner cannot answer is a row in the plan's `Decision points` table — question, options, recommendation, **kind**, **blocking?**, **resolved by**. The kind decides who answers and with what: a *decision point* → decision-maker, one `RL-`; a *fact* → executor, `RS- kind: spike`; a *scope* question → maintainer, an `RL-` or an `RFC-`; a *design unknown that outlives the plan* → an `OQ-` the plan cites. A non-blocking row must name the step where it is resolved and the default applied until then, or it is blocking. One sitting resolves the blocking rows; the planner applies each answer at every site (`writing-plans` rule 5) and re-checks open PRs (rule 4). **Freeze is mechanical:** `status: active` is permitted only when every blocking row has a resolver id and every non-blocking row names a step. Questions after freeze never reopen the plan: they become sibling `RL-` records applied at a ledger step, or a replan (`supersedes:`). A map plan's table is the slice-readiness record; an `SL-` may not move `draft → active` while any of its rows is open.

## 1.8 Widening

`doc-id.py widen --to 6` renames every padded file, rewrites every padded link target, appends to `REDIRECTS.csv`, updates the width in `document-ids.md`, regenerates `INDEX.md`; touches no citation, number, header or body line. Trigger: `INDEX.md` passes 90 000.

## 1.9 GitHub alignment — files are the source of truth; GitHub objects are named by the id

| Layer here | GitHub-native object | Convention |
|---|---|---|
| Phase `P2` | Milestone | milestone named `P2 — <title>`; optional mirror |
| `WK-1201` | Issue of type `Feature`/`Epic` | optional mirror, titled `WK-1201: <title>`, its slices as sub-issues |
| `SL-1242` | Issue of type `Task` / sub-issue | branch `sl-1242-<slug>`; PR title `SL-1242: <title>`; the PR template requires it |
| `PL-` / `RL-` | the issue description / decision comments | in the repository, frozen, cited by id |
| `LG-` | the PR list under the sub-issue | the ledger records PR numbers |
| `FD-` | Issue of type `Bug`, label `finding` | optional mirror, titled `FD-93: …` |
| `CR-` | release notes / retrospective | generated |
| `RFC-` | RFC / Discussion | in the repository |

Lint checks that a merged PR's title names the `SL-` it delivered and that the slice's ledger records the PR number. A PR that arrives without one — a hotfix, an external contributor, a dependency bump — gets its `SL-` minted by the lead at triage under the phase's standing `WK- maintenance`; the PR template says so; bot authors are exempt.

## 1.10 Rituals and metrics

Three practices every mature programme runs and this process has only partly: **(a)** a periodic status entry on every active `WK-`, nagged mechanically — the `reporter-cycle` skill pointed at active work rows, fortnightly, in the Rust goals bot's shape; **(b)** dated freeze gates inside a phase (plan → code → docs, as Kubernetes runs enhancements → code → docs), declared in the phase section and checked by `phase-close.md`; **(c)** a phase report generated by `doc-index.py` over every record carrying `phase: P<n>` — Works closed/retired, slices planned vs delivered, plans superseded per Work (replan rate), rulings per Work, findings opened vs discharged and the unowned-decay count, documents with no inbound citation outside `INDEX.md`, days from `PL` `active` to `CR` filed. Never a hand-kept table — Kubernetes' own audit found its per-KEP metadata drifting from the board, which is NT-0003 at scale.

## 1.11 Audit — the id checks fold into `audit-docs.py`

`doc-id.py` writes (allocate, migrate, widen); `doc-index.py` generates; every read-only check is `audit-docs.py` checks 30+ so there is one gate and one report, and `docs-audit` stays the single entry point:

| # | Check |
|---|---|
| 30 | Header present and parseable on every file under `docs/`, every charter, skill and agent; no unknown field; required fields per family |
| 31 | `id` prefix and integer equal the filename's; directory equals family; numbers unique and contiguous across rows and documents; `created` non-decreasing with the number |
| 32 | Every `<PREFIX>-<n>` in prose resolves in `INDEX.md` **and its prefix matches the number's family** (the prefix is a checksum); no padded id outside link targets; every padded link target names the file its text cites; every row id's anchor exists in its file |
| 33 | `supersedes`/`superseded_by` symmetric; every `status:` is in §1.2a and in the family's subset; a ledger's `slice:` resolves and no two `active` ledgers share a slice; every id in a ledger's `plans:` resolves; `work:`, `slice:` resolve to roadmap rows; `phase:` resolves to a milestone section; `relates:` ids exist; an `SL-` row `closed` without a `closed` `LG-`, or a `PL-` `retired` whose `SL-` is not `retired`, fails; a `PL-` `active` with an open blocking decision point, or a non-blocking one naming no step, fails; a `closed` `OQ-` must cite its resolving `RL-`/`ADR-` |
| 34 | Freeze: for a frozen family the diff against the merge-base touches only `status:` (forward only), `superseded_by:`, an append to `corrected_by:`, or — ledgers only — an append to `plans:` (C4 made mechanical); every `corrected_by:` entry is a record whose `corrects:` names this file |
| 35 | `owner:` is a role filename or `maintainer`, and one the directory's `README.md` permits |
| 36 | Redirects: every `was:` has a `REDIRECTS.csv` row; every row's target exists; no pre-migration form survives outside the CSV and `was:` lines |
| 37 | Shape: required sections per family template (the ten-section spec rule, generalised) |
| 38 | Loop signal, warn-only: a `PL-`/`RS-`/`RFC-` cited by nothing outside `INDEX.md`, exempting those a `CR-` covers by `work:` (Ruling 64 as code); a `PL-` still `draft` past its phase's plan-freeze gate; an `active` plan or slice citing a `superseded` or `retired` requirement; a phase gate date passed with a `draft` plan or an `active` slice behind it (the auditor raises an `FD-` against the phase) |
| 39 | `INDEX.md` byte-stable against a fresh run; a merged PR's title names its `SL-`; the slice's ledger records the PR |

## 1.12 Extending the frame

Because the sequence is global and a prefix is a label, adding a family never touches an existing id, file or citation; `INDEX.md` gains rows. Three levers, cheapest first, and a rule for choosing:

| Lever | When | What it takes |
|---|---|---|
| a new **`kind:`** | the new type has the same unit, mutability and owner as an existing family — a post-mortem is `RFC- kind: incident`, a benchmark `RS- kind: measurement`, release notes `CR- kind: phase` | a template variant and one line in the family's kind vocabulary; an `RL-` |
| a new **document family** | a different unit, mutability or owner — e.g. a user guide, `docs/guides/GD-` | an `RFC-` and an `RL-` naming prefix, directory, unit, mutability, status subset (from §1.2a, never a new word), the §1.6 role row, a template; checks 30–39 apply unchanged |
| a new **row family** | the unit is a clause inside a living host — e.g. dataset cards in a data catalogue | as above, plus the host document and its anchor rule (§1.2) |

What never changes on extension: the five status words, the header field set (a family may add fields only via its template), the citation rule, the allocator, the checks. Scratch (`.planning/`, `.superpowers/`, runtime state, chat) is never a family; if it carries a decision, the decision is an `RL-`.

## 1.13 Past practice, mapped

Every governance file at `8f5d57d` classifies under §4's rules (0 unmapped, §10), and every practice named in the plans, process text, skills and charters has a home: `-verified`/`-final-review` → `PL- kind: review`; corrections and ruling addenda → `corrected_by:` + a correcting `RL-`/`RFC-`; reconciliation rulings → one `RL-` each; census and taxonomy draft → `RS- kind: measurement`/`audit`; adoption plans → a `WK-` each; handover → `PL- kind: handover`; slice-map/map-plan → `PL- kind: map`; spike → `RS- kind: spike`; planning readiness → the map plan's `Decision points` table; audit remediation → an `SL-` naming its `FD-`s; plan reviews → `CR- kind: review`; closure proposals → `PL- kind: leaf` with `RL-`s; maintainer decisions and phase pre-decisions → `RL-` with `owner: maintainer`; exit-demo UAT and `phase-0-status.md` → `CR- kind: phase`; retrofit-impossible and security-posture → Reference; nudge, reporter-cycle and runtime state → rituals and watcher state, not documents.
