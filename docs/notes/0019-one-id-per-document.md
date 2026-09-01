# NT-0019 — One id per governed thing: one sequence, integer identity, a self-describing layout, and roles per family

| | |
|---|---|
| **Raised** | 2026-09-01, by the maintainer, written against `main` at `8f5d57d`. Every count and every file named in §5 was measured at that tree by the commands in §10 |
| **Status** | `accepted` — every decision in §2 is the maintainer's; nothing is left for a ruling sitting. The planner cuts §8 into slices |
| **Deliverable** | Spec/doc change before code, per `CLAUDE.md` §0's table: the standard (§1) lifts verbatim into `docs/process/document-ids.md`; then the two scripts and the `audit-docs.py` checks with their tests; then one migration PR; then the charter, skill and pointer edits in §5 |
| **Owner** | The maintainer accepts. The planner slices §8. The executor runs the migration script and the hand edits. The auditor accepts against §7. This is the last note filed under the `NT-` prefix: the migration renumbers it into the `RFC` family with `was: NT-0019` |
| **Lands in** | Every area in §5 — root governance files, all of `docs/`, `.claude/settings.json`, seven role charters, two agents, twenty-six skills, fourteen scripts, twelve tests, two CI workflows, and every code and test file whose comments, docstrings, test markers or API summaries cite a document or requirement (767 files) |
| **Sequencing / Trigger** | Now, at the next gap with no open branches (F40's lesson). Supersedes NT-0016 §4 and §7 and its constraints C1–C2; Rulings 63 and 65 lapse by their own override clauses (§9). The charter investigation and the create-read-retire audit are downstream Works; §1.6 and §1.10 are the hooks they hang on |

---

**One-line thesis:** every governed thing in this repository — a requirement clause, a work item, a slice, a plan, a ruling, a ledger, a closure, a finding, a proposal, a decision, a journey, a spike — gets one permanent id from **one** project-wide integer sequence, written `<PREFIX>-<n>` in prose and `<PREFIX>-<nnnnn>-<slug>.md` on disk where it is a file, with a machine-readable header, a per-family status machine, a named owner, a generated index and lint in CI. A phase is a **milestone label**, the one deliberate exception, made for the same reason every mature project makes it. The corpus is fifteen days old; the single migration that gets there costs an afternoon now and a quarter in a year, so it is done once, now, and never again.

## 1. The standard

### 1.1 Four rules

1. **A governed thing's id is `<PREFIX>-<n>`; `n` is an integer from one sequence shared by every family.** `FR-1187` is a requirement, `WK-1201` a work item, `PL-1240` a plan, `RL-1241` the ruling filed after it. No number is used twice. The prefix says what kind of thing; the number says which one, uniquely, project-wide. (Kubernetes: `KEP-1234` is issue #1234 in one global space; Jira: one key sequence per project across every item type.)
2. **Citations write the integer, never padding:** `PL-1240`, `RL-65`, `RFC-16`, `FR-1187` — as PEP 8, RFC 2094 and KEP 1234 are written. A padded id in prose is a lint error. **No exception**: prose, headings (`# RL-1241 — …`), commit messages, PR titles, branch names, code comments, docstrings, test markers, link text.
3. **Filenames pad the integer to the standard's width, currently five:** `PL-01240-<slug>.md`. Padding exists so `ls` sorts; it is not identity. The resolver treats `PL-1240`, `PL-01240` and `PL-001240` as one id. Widening is a rename of files and a rewrite of link targets — one mechanical PR that touches no citation, number, header or body line (§1.8).
4. **Two things are outside the standard, on principle:** a **phase**, which is a milestone label (`P2`), cited as a placement (`phase: P2`), never as a document (§1.3); and a **product identifier** — any id that is stored, transmitted or asserted by an API contract (`VR-DST-1`, artifact ids, job kinds) — which is product data governed by `docs/specs/`, and which this standard never touches.

### 1.2 Families — rows and documents, one sequence

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

#### 1.2a One status vocabulary

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

### 1.3 Phase = milestone

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

### 1.4 Layout — one directory per document family, the padded id leading every filename

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

### 1.5 The header — YAML front matter, closed field set

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

### 1.6 Roles per family

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

### 1.7 Citation and allocation

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

### 1.8 Widening

`doc-id.py widen --to 6` renames every padded file, rewrites every padded link target, appends to `REDIRECTS.csv`, updates the width in `document-ids.md`, regenerates `INDEX.md`; touches no citation, number, header or body line. Trigger: `INDEX.md` passes 90 000.

### 1.9 GitHub alignment — files are the source of truth; GitHub objects are named by the id

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

### 1.10 Rituals and metrics

Three practices every mature programme runs and this process has only partly: **(a)** a periodic status entry on every active `WK-`, nagged mechanically — the `reporter-cycle` skill pointed at active work rows, fortnightly, in the Rust goals bot's shape; **(b)** dated freeze gates inside a phase (plan → code → docs, as Kubernetes runs enhancements → code → docs), declared in the phase section and checked by `phase-close.md`; **(c)** a phase report generated by `doc-index.py` over every record carrying `phase: P<n>` — Works closed/retired, slices planned vs delivered, plans superseded per Work (replan rate), rulings per Work, findings opened vs discharged and the unowned-decay count, documents with no inbound citation outside `INDEX.md`, days from `PL` `active` to `CR` filed. Never a hand-kept table — Kubernetes' own audit found its per-KEP metadata drifting from the board, which is NT-0003 at scale.

### 1.11 Audit — the id checks fold into `audit-docs.py`

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

### 1.12 Extending the frame

Because the sequence is global and a prefix is a label, adding a family never touches an existing id, file or citation; `INDEX.md` gains rows. Three levers, cheapest first, and a rule for choosing:

| Lever | When | What it takes |
|---|---|---|
| a new **`kind:`** | the new type has the same unit, mutability and owner as an existing family — a post-mortem is `RFC- kind: incident`, a benchmark `RS- kind: measurement`, release notes `CR- kind: phase` | a template variant and one line in the family's kind vocabulary; an `RL-` |
| a new **document family** | a different unit, mutability or owner — e.g. a user guide, `docs/guides/GD-` | an `RFC-` and an `RL-` naming prefix, directory, unit, mutability, status subset (from §1.2a, never a new word), the §1.6 role row, a template; checks 30–39 apply unchanged |
| a new **row family** | the unit is a clause inside a living host — e.g. dataset cards in a data catalogue | as above, plus the host document and its anchor rule (§1.2) |

What never changes on extension: the five status words, the header field set (a family may add fields only via its template), the citation rule, the allocator, the checks. Scratch (`.planning/`, `.superpowers/`, runtime state, chat) is never a family; if it carries a decision, the decision is an `RL-`.

### 1.13 Past practice, mapped

Every governance file at `8f5d57d` classifies under §4's rules (0 unmapped, §10), and every practice named in the plans, process text, skills and charters has a home: `-verified`/`-final-review` → `PL- kind: review`; corrections and ruling addenda → `corrected_by:` + a correcting `RL-`/`RFC-`; reconciliation rulings → one `RL-` each; census and taxonomy draft → `RS- kind: measurement`/`audit`; adoption plans → a `WK-` each; handover → `PL- kind: handover`; slice-map/map-plan → `PL- kind: map`; spike → `RS- kind: spike`; planning readiness → the map plan's `Decision points` table; audit remediation → an `SL-` naming its `FD-`s; plan reviews → `CR- kind: review`; closure proposals → `PL- kind: leaf` with `RL-`s; maintainer decisions and phase pre-decisions → `RL-` with `owner: maintainer`; exit-demo UAT and `phase-0-status.md` → `CR- kind: phase`; retrofit-impossible and security-posture → Reference; nudge, reporter-cycle and runtime state → rituals and watcher state, not documents.

## 2. Decisions

| # | Decision | Reason |
|---|---|---|
| D0 | One five-word status vocabulary — `draft · active · closed · retired · superseded` — identical in every family; mutability is a family property; register dispositions live in `decision:` | Twenty-one words were in use for five meanings; a synonym per family is how "the same process" stops being the same |
| D1 | One global integer sequence across every row and document family | A bare number resolves anywhere; numbers carry chronology; one allocator; the industry already runs process ids and document ids in one space |
| D2 | Requirement ids join the sequence: `FR-MODEL-45` → `FR-1187` | The module segment encoded the file the clause lives in, which the file already tells you — the argument that retired `F-W9-3`, applied consistently |
| D3 | Work and Slice become row families `WK-`/`SL-` with `phase:`/`work:` fields; `W12-2` retires | Every benchmarked project keeps hierarchy in fields, never in the id; a slice gains stable identity across replans |
| D4 | Phase is a milestone label `P<n>`, not a numbered family | Every benchmarked project names its phases like versions; ~10 will ever exist; a phase is cited as a placement, never as a document |
| D5 | Product identifiers (`VR-*`, artifact ids, job kinds) are out of scope | An id that is stored or transmitted is product data governed by the spec |
| D6 | Citations unpadded, no exception; filenames padded to five; resolver accepts any padding | The PEP/RFC convention; width becomes a filename concern; five because the sequence starts near 1 000 |
| D7 | Notes → `RFC`; findings → `FD-<n>`; workflows → `WF-<n>` | The words GitHub readers know; one form per family |
| D8 | Prefixes are mnemonics of two or three letters | Uniform digits is what makes tools behave; uniform letter-count buys nothing |
| D9 | Legacy multi-ruling records split one per file; `closure-records.md` and `plan-reviews.md` split into `CR-` files | One unit per file |
| D10 | Charters, skills and agents carry the header | They are the `owner:` vocabulary and the creating instruments |
| D11 | Id checks live in `audit-docs.py`; no separate lint script | One gate, one report |
| D12 | Sequential allocation now; issue-number allocation left as a switch | Sequential already works for four families |
| D13 | Owners: research → executor, except `RS- kind: audit` → auditor; RFC → maintainer; workflow → decision-maker (executor delivers); charters → maintainer | §1.6; closes every gap NT-0016 found, including the bespoke audit that `2026-08-29-w11-process-conformance-audit.md` had to file as a plan |
| D14 | Enforcement red from the migration PR | No population to phase in |

## 3. Illustrative numbering

| Today | After |
|---|---|
| `docs/adr/0001-pricing-core-is-dependency-free.md` (2026-08-14) | `docs/adrs/ADR-<nnnnn>-pricing-core-is-dependency-free.md`, cited `ADR-1` |
| `FR-MODEL-45` in `02-modelling.md` | `**FR-nnnn**` in place, cited `FR-nnnn`; `@pytest.mark.req("FR-nnnn")` |
| `W11-3` roadmap row | `SL-nnnn` row under `WK-nnnn`, `phase: P1b` |
| `## Ruling 62` inside a four-ruling file | `docs/rulings/RL-0nnnn-q1-category-set-amended.md`, cited `RL-nnnn`, `was: Ruling 62` |
| `docs/audit/work/W10-2/README.md` | `docs/closures/CR-0nnnn-wk-nnnn.md`, `kind: work` |
| `F27` + `docs/audit/findings/F27.md` | `docs/findings/FD-0nnnn-rating-shapes.md`, register row `was: F27` |
| `Phase 1b` | `## P1b — …` milestone section; every record `phase: P1b` |

## 4. Migration — one scripted PR, once

`scripts/doc-id.py migrate`, deterministic and idempotent, run once and retained as evidence:

1. **Assign** one sequence to every row and document in `created`-date order (header date; filename date for plans; ADR `Date:`; spec module order then clause order for requirements, using the module's first-commit date; git first-commit date otherwise), ties by family order in §1.2 then filename. `was:` and `REDIRECTS.csv` keep every old id and path.
2. **Split.** Multi-ruling files → one per `## Ruling N`; `closure-records.md` → one `CR-` per work heading; `plan-reviews.md` → one `CR-` per review; the two unnumbered rulings files by their `##` headings.
3. **Restructure `roadmap.md`**: phase sections as milestones with `status/opened/target/gates/exit criteria`; each Work a `WK-` row with a fenced header; each slice an `SL-` row under it.
4. **Move** into the family directories; dissolve `docs/audit/`; delete the `.claude/notes/` stubs.
5. **Stamp** the header on every file under `docs/`, `.claude/roles/`, `.claude/skills/*/SKILL.md`, `.claude/agents/`; convert the ADR bullet header and the notes prose table.
6. **Rewrite every citation across the whole tree** — `git ls-files`, nothing exempt: old basenames, paths, `Ruling N`, `NT-`, `F`/`F-W`, `wf-`, `ADR-000n`, every `FR/NFR/OQ/DEP-<MOD>-<n>`, every `W…` work key, `@pytest.mark.req` markers, API `summary=` strings, `.importlinter` names. The rewrite list is an allow-list of prefixes; `VR` is not on it.
7. **Regenerate** `docs/contracts/`, `delivery-process.core.json` and its digest, `INDEX.md`, `REDIRECTS.csv`.
8. **Verify** (§7). Land at a gap; rebase any branch that appears by re-running step 6 on its diff.

Never changed: a body line of any frozen file. Splits preserve every line, stamps add lines, rewrites change reference tokens only.

## 5. Impact — every area that changes

**M** = done by `doc-id.py migrate`; **H** = a hand edit the script cannot know. A plan is complete when every H row is a task and every M row is covered by §7.

### 5.1 Root governance

| File | Change | Kind |
|---|---|---|
| `CLAUDE.md` | §2 layout → §1.4's tree; §4 module map rewritten; §5 gains "document and row ids are `document-ids.md`'s; product identifiers stay the spec's"; §9 roadmap pointer names phases-as-milestones and `WK-`/`SL-`; §12 names the owner table; §13–§15 pointers to `closures/`, `findings/`, `rulings/`; citations rewrite | H + M |
| `README.md` | the tour: new paths; one paragraph "how things are named" → `document-ids.md`; branch and PR-title convention | H |
| `CONTRIBUTING.md` | branch `sl-<n>-<slug>`, PR title `SL-<n>: …`, "a new document has an id from `doc-id.py next`", where findings and proposals go | H |
| `SECURITY.md` | path → `docs/process/security-posture.md` | M |
| `.github/PULL_REQUEST_TEMPLATE.md` | "Plan: `docs/plans/…`" → required `SL-<n>` line and `PL-<n>`; "no slice yet? the lead mints one at triage under `WK- maintenance`" | H |
| `.github/ISSUE_TEMPLATE/*.yml` | optional "related id" field; issue types `Feature`/`Task`/`Bug` if mirrored | H (optional) |
| `.gitignore` | comment block lines 91–108 reworded to the new families | H |
| `.importlinter` | contract names `ADR-0001`/`ADR-0002`/`DEP-3` → `ADR-1`/`ADR-2`/`DEP-n` | M |
| `pyproject.toml` (root), `packages/*/pyproject.toml` | requirement-id citations in comments | M |

### 5.2 `docs/`

| Today | After | Kind |
|---|---|---|
| `README.md` | rewritten as the map (§1.4 tree, §1.2 table, reading order, check commands) | H |
| `INDEX.md`, `REDIRECTS.csv`, `_templates/`, `process/document-ids.md`, `closures/README.md`, `findings/README.md`, `rulings/README.md`, `ledgers/README.md` | new | H / M |
| `specs/*.md` (8) | stay; every `**FR-<MOD>-<n>**` definition renumbered in place; "Highest ids in use / Next free" markers → global next; `00-overview.md` §2 id-scheme text rewritten and points to `document-ids.md`; OQ ids renumbered; all citations rewrite | M + H (§2 text, markers) |
| `open-questions.md` | OQ ids renumbered; mirror check keeps working; citations rewrite | M |
| `roadmap.md` | restructured (§4 step 3): milestone sections, `WK-`/`SL-` rows with headers, `phase:` everywhere; §6 delivery rows → `CR-n`; **H**: the "what a Work produces" paragraph names the families | M + H |
| `phase-0-status.md` | becomes the `P0` milestone section's exit-criteria record → `closures/CR-0nnnn-p0.md`, `kind: phase` | M |
| `skills-map.md` | citations rewrite | M |
| `workflows/wf-0n-*.md` (5) + README | `WF-0nnnn-*.md`, stamped; README table generated | M + H |
| `adr/000n-*.md` (6) + README | `adrs/ADR-<nnnnn>-*.md`; bullet header → front matter (`accepted` → `active`, `deprecated` → `retired`); README generated | M + H |
| `notes/00nn-*.md` (18) + README | `rfcs/RFC-0nnnn-*.md`; prose header → front matter, statuses mapped (`open` → `draft`, `accepted` → `active`, `landed` → `closed`, `dropped` → `retired`, `superseded` unchanged) with `kind:` (`process` 0001, 0003–0010, 0013–0016, 0018; `enhancement` 0002, 0017; `incident` 0012); README rewritten, index table dropped for `INDEX.md` | M + H |
| `plans/2026-*.md` (125) + README | 27 rulings files → `rulings/` split per ruling; 16 `-ledger.md` → `ledgers/`; the rest → `plans/` with `kind:` from suffix (`-final-review`/`-verified` → `review`; `-handover`; `-slice-map`/`-map-plan` → `map`; else `leaf`) and `status:` mapped to §1.2a (every legacy plan `active`; superseded map revisions `superseded`); README: naming and four-kinds table → pointer; the nine writing conventions kept verbatim | M + H |
| `research/*.md` (11) | `RS-0nnnn-*.md`, `status: active`, `kind:` `spike`/`measurement` | M |
| `plans/2026-08-29-w11-process-conformance-audit.md` | `research/RS-0nnnn-w11-process-conformance-audit.md`, `kind: audit`, owner auditor; its two unowned follow-ups become `FD-` rows | M + H (the two rows) |
| `audit/register.md`, `audit/phases/1b/register.md` | one `findings/register.md`; each row gains `status:` (`active`, or `closed` where a **Resolved** annotation exists) and `decision:` (the existing Decision cell); the phase register's rows merge in with `phase: P1b` (NT-0003: no second copy); per-phase views come from `doc-index.py --phase`; Finding-id cells → `FD-n` with `was:`; header prose rewritten | M + H |
| `audit/findings/F*.md` (5) + README | `findings/FD-0nnnn-*.md`; README rewritten | M + H |
| `audit/work/*/README.md` (15), `audit/phases/1b/README.md`, `audit/exit-demo-uat.md` | `closures/CR-0nnnn-*.md`, `kind: work` / `phase` | M |
| `audit/closure-records.md`, `audit/plan-reviews.md` | split into `CR-` files (`work`, `review`); preambles → `closures/README.md` | M + H |
| `audit/checklists/*.md` | → `process/checklists/`; each gains "new record has an id; `audit-docs` green"; "No new id family is minted" → "no family outside `document-ids.md` §1.2"; `phase-close.md` gains the freeze-gate and generated-report lines | M + H |
| `audit/retrofit-impossible.md`, `audit/security-posture.md` | → `process/` | M |
| `audit/file-census*.{md,csv}`, `audit/file-taxonomy-draft.md` | → `research/RS-…` | M |
| `audit/README.md` | deleted; content to `findings/` and `closures/` READMEs | H |
| `process/delivery-process.md` | **H**: §3's Project → Phase → Work → Slice vocabulary now names `P<n>`, `WK-`, `SL-`; what each layer produces names the families; §15 "name the tree" gains "and the id"; the fortnightly status ritual and freeze gates added; citations rewrite | H + M |
| `process/delivery-process.core.json` | path values, `WK`/`SL` vocabulary, regenerated digest | H + M |
| `process/agent-settings.md` | citations rewrite | M |
| `contracts/**` | not moved; **regenerated** after the `model-schema` docstring and API-summary rewrite (`ADR-`, `wf-`, `FR-` ids appear in generated JSON); `gi-pricing.yaml` rewrites | M + regenerate |

### 5.3 `.claude/`

| File | Change | Kind |
|---|---|---|
| `settings.json` | hook `statusMessage` citation | M |
| `notes/*.md` (19 stubs) + README | deleted; `REDIRECTS.csv` rows | H + M |
| `roles/auditor.md` | owns `findings/register.md`, `FD-`, `CR- kind: work\|phase`; sets `LG-` `closed`; checklist path; header | H + M |
| `roles/decision-maker.md` | rulings one per file with an id; owns `specs/`, `adrs/`, `workflows/`; records OQ; header | H + M |
| `roles/executor.md` | works from `PL-n` for `SL-n`; appends `LG-n` per task and PR; owns `RS-` (`library-spike`) and journey tests; never amends `WF-`; branch/PR convention; header | H + M |
| `roles/lead.md` | dispatches `SL-`; maintains milestone sections and `WK-` rows; owns `CR- kind: review` and agents; residual `docs/` clause now enumerated by the generated matrix; header | H + M |
| `roles/planner.md` | `PL-` via `writing-plans` with `doc-id.py next`; cuts `SL-` rows in the map plan; replan = new `PL-` with `supersedes:`; header | H + M |
| `roles/reporter.md`, `roles/watcher.md` | "owns no governed document" stated; reporter's fortnightly `WK-` status entry; `--slice-source` examples → `PL-` paths; header | H + M |
| `agents/README.md`, `ci-watcher.md`, `spec-reconciler.md` | header; citations; README names agents as Reference family owned by the lead | M + H |
| Maintainer authorities | no `roles/maintainer.md` — the maintainer is not a spawned role; the maintainer's authorities are listed once in `document-ids.md` §1.6 and `CLAUDE.md` §12 | H |

### 5.4 `.claude/skills/`

| Skill | Change | Kind |
|---|---|---|
| `README.md` | header; "creates" column per creating skill | H + M |
| `writing-plans` | **primary**: `doc-id.py next` at draft, `_templates/PL.md` with its `Decision points` table, `PL-<nnnnn>-<slug>.md`, `kind:`, `phase:`, `work:`, `slice:`; freeze only when the table is clean; a map plan mints the `SL-` rows and is their readiness record | H + M |
| `subagent-driven-development` + `scripts/task-brief` | **primary**: `LG-` under `ledgers/`, keyed by `slice:`, `plans:` appended on replan, `status: active`, PR numbers appended; hard-coded paths | H + M |
| `close-workstream` | **primary**: `CR- kind: work`; sets the slice's `LG-` and `SL-` to `closed`; files `FD-`; sets the RFC to `closed`; PR-title/ledger check; checklist path; citations | H + M |
| `phase-review` | **primary**: `CR- kind: review`; runs `doc-index.py --phase P<n>` and reads the generated report (which is also the phase's register view); freeze-gate check | H + M |
| `adr-write` | **primary**: `adrs/`, `doc-id.py next`, `ADR-<nnnnn>-<slug>.md`, front matter, `superseded_by:` | H + M |
| `spec-change` | **primary**: requirement ids from `doc-id.py next` (global), bold-id form kept; `WF-` amendments; OQ recording; "for any other document use `document-ids.md`" | H + M |
| `docs-audit` | checks 30–39 described; four-kinds paragraph and `YYYY-MM-DD-` grammar removed; tombstone check → redirects check; citations | H + M |
| `dev-commands` | `doc-id.py next/check/widen`, `doc-index.py --check/--phase`; citations | H + M |
| `git-hygiene` | branch `sl-<n>-<slug>`; PR title `SL-<n>: …`; citations | H + M |
| `reporter-cycle` + scripts | fortnightly `WK-` status entry (§1.10a); citations | H + M |
| `library-spike` | writes `RS- kind: spike` via `doc-id.py next` | H |
| `close-workstream` / `docs-audit` (audit path) | a bespoke audit is an `SL-` whose record is `RS- kind: audit`, owner auditor, every finding an `FD-`; never a plan, never a closure | H |
| `repo-architecture` | annotated `docs/` tree → §1.4 | H + M |
| `python-test`, `testing-strategy` | `@pytest.mark.req("FR-<n>")` form | H + M |
| `brainstorming`, `planning-with-files` | one sentence each: scratch is not a document; the committed record is `PL-`/`LG-` | H |
| `watcher-runtime-state` + script, `secret-hygiene`, `executing-plans`, `requesting-code-review`, `python-package`, `contract-schema`, `fastapi-service`, `vue-frontend`, `graphify/references/update.md` | citations and example paths | M |
| every `SKILL.md` (46) | header stamped; vendored skills get `vendored: true` + `origin:` and their subtrees are skipped by the migration (any directory holding a `LICENSE` that is not the repository's own) | M |

### 5.5 `scripts/`

| Script | Change | Kind |
|---|---|---|
| `doc-id.py` | new: `next`, `check`, `migrate`, `widen` | H |
| `doc-index.py` | new: `INDEX.md` with the derived `execution` column, ownership matrix, `--check`, `--show <id>`, `--phase P<n>` report | H |
| `audit-docs.py` | check 16 → front-matter parser; path roots → new directories; `_FINDING_ID` → `FD-0*\d+`; requirement-id regexes → `(FR\|NFR\|DEP\|OQ)-\d+`; per-module numbering check → global uniqueness; "Next free" exemption on the global next; `check_notes_tombstone` → `check_redirects`; core digest re-pinned; new checks 30–39; docstrings | H + M |
| `register-lint.py`, `register-owed.py` | paths, `FD-` parser, `WK-`/`SL-` in the Work-item column, docstrings | H + M |
| `req-coverage.py` | spec regex `\*\*(FR\|NFR)-\d+\*\*`; marker form; docstrings | H + M |
| `scope-audit.py` | requirement-id regex; docstrings | H + M |
| `file-census.py` | family table read from `document-ids.md`; id-match in `referenced_by`; output to `research/`; docstrings | H + M |
| `graphify-docs-extract.py` | front-matter parsing; requirement regex | H |
| `generate-contracts.py` | re-run after §5.6 | M |
| `revalidate-artifacts.py`, `demo.py`, `bench-*.py` (6), `hooks/retry_cap_hook.py` | docstring citations | M |

### 5.6 Code — comments, docstrings, markers, API summaries; then regenerate and run

| Area | Files | What rewrites | Kind |
|---|---|---|---|
| `backend/src/app/` | ≈200 | `ADR-`, `wf-`, `F<n>`, plan paths, `FR/NFR-<MOD>-<n>` in comments, docstrings and `summary=`/`description=` strings (flow into OpenAPI) | M |
| `backend/tests/` | ≈210 | same + `@pytest.mark.req("FR-…")` markers (1 988 across the tree) | M |
| `backend/migrations/versions/` | 3 | docstring citations | M |
| `packages/pricing-core/` | ≈70 | `ADR-1` (91 occurrences), `wf-`, requirement ids in docstrings and markers | M |
| `packages/model-schema/` | ≈58 | `ADR-2`/`ADR-3`, `wf-`, requirement ids in docstrings and `Field(description=…)` → **then regenerate contracts** | M + regenerate |
| `frontend/src/` | 144 | requirement ids and `wf-01` in comments, test titles and one component doc-comment | M |
| `examples/`, `deploy/`, `packages/README.md` | 8 | requirement citations in comments; every README outside `docs/` is Reference family and gets the header | M |
| **Never touched** | — | `VR-*` catalogue ids, artifact ids, job kinds, any string persisted or asserted as data (D5) | — |

Every touched file is compiled and its suite run (§7 (h)): a rewrite inside an asserted string is the reason.

### 5.7 Tests

| Test | Change | Kind |
|---|---|---|
| `test_audit_docs_notes_tombstone.py`, `test_notes_move_citations.py` | deleted → `test_audit_docs_redirects.py` | H |
| `test_audit_docs_finding_citations.py`, `_plan_acceptance_standard.py`, `_process_core_digest.py`, `_scan_roots.py`, `test_retry_cap_hook.py`, `test_watcher_runtime_state.py`, `test_register_lint.py`, `test_register_owed.py`, `test_file_census.py`, `test_scope_audit.py` | fixture ids and paths → new forms; digest re-pinned | H + M |
| new | `test_doc_id.py` (next/check/widen/migrate idempotence), `test_doc_index.py`, `test_audit_docs_ids.py` (checks 30–39 on `tests/fixtures/docs-ids/`, five broken fixtures), `test_audit_docs_redirects.py` | H |
| code suites | comment/docstring/marker rewrites only | M |

### 5.8 CI

| File | Change | Kind |
|---|---|---|
| `.github/workflows/docs.yml` | `paths:` add `scripts/doc-id.py`, `scripts/doc-index.py`, `.claude/**`; steps `doc-id.py check`, `doc-index.py --check`; comment block replaced | H |
| `.github/workflows/python.yml` | unchanged (`fetch-depth: 0` now also serves `doc-id.py next`); `req-coverage` step keeps working | — |
| `.github/workflows/frontend.yml` | unchanged | — |

## 6. Rituals adopted

Fortnightly `WK-` status entries via `reporter-cycle`; dated plan/code/docs freeze gates per phase checked by `phase-close.md`; the generated phase report as the body of every `CR- kind: phase`; PR titles name the slice.

## 7. Acceptance

At the migration PR's merge tree: **(a)** every tracked file under `docs/` parses to exactly one family, counts per family, zero "none"; **(b)** `doc-id.py check`: zero duplicates, contiguous sequence, every header `id` equals its filename; **(c)** `doc-index.py --check` byte-stable; **(d)** `git grep -E '\b(NT-00|F-W[0-9]|\bF[0-9]{2}\b|wf-0[0-9]|Ruling [0-9]+|ADR-0[0-9]{3}|(FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+|W[0-9]+[a-z]?-[0-9]+|docs/(plans/2026-|audit/|notes/|adr/)|\.claude/notes/)'` over `git ls-files`, excluding `REDIRECTS.csv` and `was:` lines, returns nothing; **(e)** no padded id in prose; **(f)** `git grep -c 'VR-DST-1'` is unchanged from `8f5d57d` — no product identifier moved; **(g)** the migration diff filtered to hunks that are neither header nor citation-token is empty; **(h)** `audit-docs.py`, `req-coverage.py`, `pytest tests/`, `lint-imports`, backend, `pricing-core`, `model-schema` and frontend suites green; `docs/contracts/` drift zero; **(i)** every H row in §5 closed by a named commit; **(j)** one new item per family born through its skill with a number from `doc-id.py next`; **(k)** `doc-index.py --phase P1b` produces the report §1.10 describes.

## 8. Sequencing

**S1 — instruments, no moves:** `document-ids.md`, templates, `doc-id.py next/check/widen`, `doc-index.py`, `audit-docs.py` checks 30–39 on new files only, their tests, `docs.yml` steps. **S2 — the migration PR** (§4) at a gap, with the H rows that must land in the same commit: `audit-docs.py` parsers and roots, `register-*.py`, `req-coverage.py`, `scope-audit.py`, `file-census.py`, the ten fixture tests, `docs.yml` filter, core-JSON digest, `roadmap.md` restructure, `delivery-process.md` vocabulary. **S3 — conventions:** every remaining H row — `CLAUDE.md`, README/CONTRIBUTING/PR template, seven charters, the eleven primary skills, `docs/` READMEs, checklists, rituals. **S4 — prove it:** acceptance (j) and (k). Then the downstream Works: the charter investigation (§1.6 made binding in each charter; directory-level `owner:`) and the create-read-retire audit (the process step per transition in §1.2's state machines).

## 9. Relation to NT-0016 and Rulings 55–65

| Item | Disposition |
|---|---|
| NT-0016 C1, C2 | lifted — the one migration C1 guarded against, done once while cheap |
| C3, C4, C5 | kept; `status:` (forward only) and `superseded_by:` are C4's only post-freeze edits |
| Stage 0 census; Ruling 62 | kept as inputs; §1.2 is those categories with one home each, plus the row families |
| Ruling 63 | superseded via its own override clause |
| Ruling 64 | kept — check 38 is it as code |
| Ruling 65 | superseded via its own override clause — every family has an id |
| Rulings 55–58 | absorbed — matrix generated; notes move into `rfcs/`; tombstone → redirects; id citation universal |
| NT-0016 Stages 2–5 | replaced by §1, §4, §5; Stages 3–4 are the downstream Works |

## 10. Evidence (at `8f5d57d`)

```bash
find docs -name '*.md' | wc -l                                             # ≈ 230 documents in 15 days
git grep -ohE '\b(FR|NFR|OQ|DEP|VR)-[A-Z]+-[0-9]+\b' | sort -u | wc -l     # 710 distinct requirement-family ids
git grep -lE '\b(FR|NFR|OQ|DEP|VR)-[A-Z]+-[0-9]+\b' | awk -F/ '{print $1}' | sort | uniq -c   # 767 files, by area
git grep -c 'pytest.mark.req' -- backend packages | awk -F: '{s+=$2} END {print s}'          # 1988 markers
git grep -n 'VR-DST-1\b' -- packages backend | head -3                     # a persisted catalogue_id — product data
git grep -ohE '\bW[0-9]+[a-z]?(-[0-9]+)*\b' | wc -l                        # 5579 work-key citations in 413 files
git grep -ohE 'ADR-0[0-9]{3}' -- backend packages frontend | sort | uniq -c   # 91 × ADR-0001 in code
git grep -ohE 'ADR-0[0-9]{3}|wf-0[0-9]' -- docs/contracts | sort | uniq -c    # generated contracts embed ids
git grep -hoE '^#+ Ruling [0-9]+' docs/plans | grep -oE '[0-9]+' | sort -n | tail -1   # 65
# classify every governance file by §4's rules → 0 unmapped (script in the migration's test fixtures)
```

## 11. Original wording (maintainer, 2026-09-01; grammar and punctuation only)

> I asked for landing NT-0016 and its plan, but it doesn't fit my expectation. I would like to standardise the current project documentation to a formatted id by family across the whole project, like other large projects on GitHub. Could you base it on my current project but mix in best practices from the others? After the id framework has landed, I will investigate more about the charter for each id, and check and create the loop for each type of file.
>
> Is it possible to rule the id form more standardised — for example move workflow to `WF`; whether I should rename note to proposal; whether an identical finding `<n>` id for all? For the number part `<n>`, `NN` and `NNNN`: do we need to keep one identical practice for all? Because this project is young with limited docs compared with other bigger projects, the cost of overwriting everything is very low; I don't want to sacrifice the project's future by considering the current status. Please propose as a mature GitHub project would, so people quickly understand the docs structure without learning it. Is it possible to use number `<n>` only over the whole project? Is it possible to request the whole project to upgrade from `NNNN` to `NNNNN` in the future? Revise the proposal for option 2.
>
> Keep the name as a note (the last note); accept all your rulings; add descriptions of all areas in the project that need to change, including `CLAUDE.md`, skills, etc. List all the areas that can be impacted to allow a full plan without missing anything; no need to mention previous versions — one final version.
>
> Revise, moving: research — the executor completes the research work and manages it; RFC — the maintainer creates; workflow — it is the work delivered, the executor. Also suggest how to enhance the docs audit to audit ids. The third question is about the cited number: do we need to keep it identical as `<XX>-<n>` (WF)? I need your comments before starting the rewrite. Recommend the owner and other roles working in the workflow area; I may be wrong. For the citation rule, I would like an identical practice for all, therefore `<XX>-<n>` for citation with no exception. Help me refine roles for the other documents; cost is not a core consideration for this project — I plan to spend a long time giving the project better management and structure; a plain yes is short-term, and the benefit is longer-term. Help me research how other projects handle Phase / Work / Slice, and any benchmarking practices. Suggest a practice aligned with milestones, with examples. Benchmark the other parts against GitHub projects and deliver one final work.
