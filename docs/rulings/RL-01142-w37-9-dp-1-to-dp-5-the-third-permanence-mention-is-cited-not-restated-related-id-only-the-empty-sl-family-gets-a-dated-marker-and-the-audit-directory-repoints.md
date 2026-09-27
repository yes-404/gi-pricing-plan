---
id: RL-1142
family: ruling
title: W37-9 DP-1 to DP-5 — the third permanence mention is cited not restated, the issue templates take the related-id field only, the empty SL- family gets a dated marker, the .importlinter row is the spec's own staleness, and the public face repoints off the audit directory
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-27
owner: decision-maker
tree: d3fa173fcde7b4815496b0d4440de4b2c41ec443
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1072, PL-939, RFC-937, RL-1140, RL-1138, FD-1074]
---

# RL-1142 — W37-9 DP-1 to DP-5: the third permanence mention is cited not restated, the issue templates take the related-id field only, the empty SL- family gets a dated marker, the .importlinter row is the spec's own staleness, and the public face repoints off the audit directory

## Verified first, at d3fa173fcde7b4815496b0d4440de4b2c41ec443

This rules `PL-1072` §6's five decision points (header row and DP-1…DP-5, `:275-287`).
Read in worktree `dm-w37-9`, branch `w37-9-activation`, cut from `origin/main` =
`d3fa173fcde7b4815496b0d4440de4b2c41ec443` with a clean status. Clock at ruling:
2026-09-27, about 08:22 BST. `PL-1072` is unchanged since it was filed: `status: draft`,
`tree: a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15`, `created: 2026-09-18`. The plan measured
every DP's facts at `a8b3c39`; every fact below is re-measured at `d3fa173f`, with its
command. `d3fa173f` is W37-8's closing merge (`docs(ledger): W37-8 closed`) — later than
`a8b3c39`, so this re-measurement is the one `CLAUDE.md` §13 requires ("verify the claim,
not just the citation") rather than a re-quote of the plan's own numbers.

### Facts re-measured at `d3fa173f`

| Plan's claim (at `a8b3c39`) | Command | At `d3fa173f` |
|---|---|---|
| DP-1: `grep -n 'permanent' CLAUDE.md` returns `:27`, `:110`, `:176`, `:226` | `grep -n 'permanent' CLAUDE.md` | Reproduces exactly: `27`, `110`, `176`, `226`. Unmoved since `a8b3c39`. |
| DP-1: `:226` reads *"a requirement id is still permanent (§5)"* | read `CLAUDE.md:226` | Reproduces verbatim, inside §12's PL/leaf-plan bullet. |
| G2: the two yield sites are `:27` and `:110` | `grep -n 'permanent' CLAUDE.md` | Reproduces; unchanged from the plan's own re-derivation at `a8b3c39`. |
| DP-2: both issue-template files are still at `01ba0bd`, pre-migration | `git log -1 --format=%H -- .github/ISSUE_TEMPLATE/` | Reproduces: `01ba0bd2f16aef26eac3aeefb029f56140fb96b6`, unmoved. Two files: `bug.yml`, `question.yml`. |
| DP-2: neither file has an issue-type mirror today; `gh` cannot read GitHub issue-type configuration | read both files; role's standing memory (§13: "gh token: run data yes, admin settings no") | Reproduces. Neither file declares an issue `type:`. |
| DP-3: zero `SL-` ids exist anywhere | `grep -c 'SL-' docs/roadmap.md` → `0`; `grep -c 'SL-' docs/INDEX.md` | **Moved.** `docs/roadmap.md` still `0`. `docs/INDEX.md` now `1`, not `0` — **drift since `a8b3c39`.** |
| — | `grep -n 'SL-' docs/INDEX.md` | The one hit is `:1211`, `FD-1074`: *"No SL- row exists for any slice, and no PL- carries a slice: field"* — a **finding that states the same absence DP-3 states**, not a minted `SL-` id. No file under `docs/plans/` carries a `slice:` field (`grep -rl '^slice:' docs/plans/` — checked, none) and `docs/roadmap.md`'s count is still `0`. **The substantive premise — no `SL-` family member exists — still holds**; the drift is an alias hit (a finding's prose mentioning the string), the same class RFC-789 and this repo's own alias-count history describe, not a new row. |
| DP-4: `.importlinter` reads `ADR-703`, `ADR-704`, `DEP-3` | `grep -n '^name' .importlinter` | Reproduces exactly. |
| DP-4: both resolve to real files | `ls docs/adrs/ \| grep -E '703\|704'` | `ADR-00703-pricing-core-is-dependency-free-and-owns-all-actuarial-maths.md`, `ADR-00704-model-schema-is-the-single-source-of-truth-for-shared-shapes.md`. Both real. |
| DP-5: two tracked files under the legacy audit directory: `findings/README.md` and `w37-11-record.md` | `git ls-files 'docs/audit/**'` (fixtures under `tests/fixtures/docs-migration/` excluded — a different, deliberately-frozen corpus) | **Moved.** Only `docs/audit/w37-11-record.md` remains tracked. `docs/audit/findings/README.md` no longer exists in the tree — it was folded elsewhere between `a8b3c39` and `d3fa173f` (consistent with `RL-1138`'s DP-2, "the retired findings README … folds into `docs/findings/README.md`", executed in the W37-8/close-record commits this branch now sits on top of). |
| DP-5: `README.md:35` and `CONTRIBUTING.md:28` both route a reader to the legacy audit directory | `grep -n 'docs/audit' README.md CONTRIBUTING.md` | Reproduces: `README.md:35`, `CONTRIBUTING.md:28`, unmoved. |

**Net effect of the drift on the rulings below.** DP-3's premise is unweakened: the one new
`SL-` hit is a finding *describing* the empty family, which if anything corroborates the DP
rather than undermining it. DP-5's premise is strengthened, not reversed: the directory has
gone from two stale-pointer targets to one, but it is still non-empty and both public files
still name it, so the repoint is still live work, now smaller. Neither drift changes which
option is correct; both are recorded here rather than silently folded into "reproduces."

## Ruled

### DP-1 — the third permanence mention at `:226`: **(c) adopted**

`:226` reads *"a requirement id is still permanent (§5)"* — a citation of §5's rule, not a
restatement of it. A citation inherits whatever §5 says after G2's edit lands; nothing at
`:226` needs its own dated RFC-937 line, because nothing at `:226` is being changed. (a)
would add a dated line to a sentence that isn't moving, manufacturing the exact
duplicate-statement failure RFC-756 exists to prevent (a restated status/rule going stale
independently of its source). (b) is the same outcome as (c) minus the record that the
distinction — citation versus restatement — was actually drawn; (c) keeps that record. The
planner does not rule this (`planner.md`: "Never: … rules decision points"), and this
ruling does not ask the planner to; it is recorded here as the ruling and left for the
executor to apply and the PR body to confirm ("`:226` read and classified as a citation;
no edit").

### DP-2 — the issue templates' scope: **(b) adopted**

The "related id" field is taken; the issue-**type** mirror (`Feature`/`Task`/`Bug`) is not.
The field costs one `input` block per template and makes an issue routable to a governed
record — RFC-937 §1.9's whole point for this row. The type mirror depends on a
repository-settings change (GitHub issue types configured on the repo) that no plan in
WK-697 owns and that this role's own tooling cannot verify: `gh`'s token here reads run
data, not admin settings, so a claim that types are mirrored would be asserted, not
evidenced, and `CLAUDE.md` §13 forbids exactly that ("NFRs are measured, not asserted").
(a) is refused for that reason; (c) under-delivers the one piece of the row this slice can
actually close in the same pass DP-2 was raised for. Consequence for Task 7: both
`bug.yml` and `question.yml` gain a `related_id` input; the issue-type block is left
untouched and unclaimed by this slice.

### DP-3 — publishing a convention for an empty `SL-` family: **(b) adopted**

Re-verified at `d3fa173f`: `docs/roadmap.md` still shows zero `SL-` ids, and no
`docs/plans/*` file carries a `slice:` field. The one new `docs/INDEX.md` hit is `FD-1074`,
a finding's prose describing this exact gap — not a counterexample. G1 (RFC-937 outranks
current practice) makes writing the convention now "work in the standard's favour," but
G1's own limit is that nothing changes silently, and adopting (a) here would publish a rule
this slice's own PR cannot satisfy — the "enforced by construction is not enforced" shape
this repository has hit before (`RL-1140`'s DP-8.1, the template-licence probes). (c)
under-delivers a scoped `H` row the map plan requires this slice to take. (b) is ruled:
`CONTRIBUTING.md`'s `sl-<n>-<slug>` branch form and `.github/PULL_REQUEST_TEMPLATE.md`'s
required `SL-<n>:` title line are both written, each carrying a dated clause reading
substantially: *"Not yet in force as of 2026-09-27 — no `SL-` row has been minted
(`docs/roadmap.md` and `docs/INDEX.md` both show zero); a PR names its work as `WK-<n>` /
`W37-n` until the first `SL-` row lands, at which point this note is removed."* The marker
is removable text, not a permanent carve-out, and its removal trigger is the first `SL-`
id, not a date. The planner does not rule this; the same reasoning as DP-1 applies to why
that boundary holds.

### DP-4 — the `.importlinter` row: **(a) adopted, fact confirmed unmoved**

`.importlinter` at `d3fa173f` still reads `ADR-703`, `ADR-704`, `DEP-3`, both ADR numbers
resolving to real files under `docs/adrs/`. §5.1's own written target (two one-character
ADR numbers and a placeholder `DEP-`) was authored before the migration allocated real
sequence numbers, so it names identifiers that resolve to nothing at any tree past the
migration. This is `CLAUDE.md` §0's "spec is stale, not the tree" case, not a code defect:
the file already matches the migration's actual output and the convention `.importlinter`
is required to cite. Task 8 verifies and does not rename. The discrepancy between §5.1's
literal text and the real allocation is raised in the PR body as a one-line finding, per
the plan's own disposition — this ruling does not open a new `FD-` for it, since the plan
already routes it as a disclosed-not-obeyed item and no further decision is needed to act
on that.

### DP-5 — the legacy audit directory's two public-face pointers: **(a) adopted**

Re-verified at `d3fa173f`: the directory now holds one tracked file
(`docs/audit/w37-11-record.md`; `findings/README.md` has already folded into
`docs/findings/README.md` per `RL-1138` DP-2, discharged between `a8b3c39` and this tree),
and both `README.md:35` and `CONTRIBUTING.md:28` still send a reader there. The directory
is not yet empty, so the repoint is still live work, and the standard set by `RFC-937` §1.4
describes the layout the public face should already show a first-time reader — the
residual file being W37-11's business is not a reason to leave two files misdescribing the
layout. `README.md:35` repoints to `docs/closures/`; `CONTRIBUTING.md:28` repoints to
`docs/findings/register.md` (its actual subject — "a register under `docs/audit/`" —
matches what `docs/findings/register.md` now holds). Either link still resolves under (b)
too, so nothing breaks by deferring, but (a) is ruled because deferring buys nothing: the
correct destination already exists at this tree for both files, unlike DP-3 where the
destination convention's own prerequisite (`SL-` existing) is what is missing.

## What it obliges

- **Task 1** confirms both DP-1 and DP-3 (blocking) carry a resolver — this ruling — before
  any later task starts.
- **Task 2** edits only `:27` and `:110` with dated RFC-937 yield lines; `:226` is read,
  confirmed a citation, and left untouched; the PR body states that classification in one
  line.
- **Task 7** adds a `related_id` optional input to `bug.yml` and `question.yml`; no issue
  `type:` field is added to either.
- **Tasks 5/6** write DP-3's dated not-yet-in-force clause into `CONTRIBUTING.md`'s branch
  form and the PR template's required-line text, each with today's date and the two zero
  counts as its evidence; the clause is written to be removed, not edited, once the first
  `SL-` row lands.
- **Task 8** verifies `.importlinter` unchanged and raises DP-4's spec/tree discrepancy in
  the PR body as a one-line finding, citing this ruling.
- **Tasks 4 and 5** repoint `README.md:35` to `docs/closures/` and `CONTRIBUTING.md:28` to
  `docs/findings/register.md`.
- **This ruling decides nothing about** the other four §5.1 rows (`SECURITY.md`, the
  `pyproject.toml` citations, the `CLAUDE.md` layout/module-map rewrite beyond G2, or
  `.gitignore`'s reword) — those are plan text already, not decision points, and remain the
  executor's to carry out per the Tasks section.
- **PL-1072** moves `draft → active`, dated, with each DP's "Resolved by" cell naming this
  ruling (`RL-1142`) — done by the planner in the same PR, per `document-ids.md` §1.6's PL
  row; this ruling does not edit the plan.

## Acceptance — the violation that must become detectable

This ruling answers five scope/fact decision points with no single code check to attach —
each obliges a text edit or a verify-only disposition, not a new enforcement mechanism.
Where a check already exists to catch the violation each DP guards against, it is named
here rather than invented:

- **DP-1's violation** — a duplicated status/rule statement outside §5 going stale
  independently — is the condition `RFC-756` was written against; no new check is added,
  and none is needed since this ruling's disposition is "make no edit" at `:226`.
- **DP-2's violation** — an issue template asserting an issue-type mirror that the
  repository's settings do not actually carry — is guarded by simply not writing that
  claim; there is no gate that could detect an unverifiable assertion of GitHub
  configuration from inside this repository.
- **DP-3's violation** — the PR that introduces the required `SL-<n>:` title convention
  failing to comply with its own new rule — is checkable directly: `git log -1
  --format=%s` on this slice's own PR must **not** match `^SL-\d+:`, confirming the
  not-yet-in-force clause was actually needed and not vacuous; and after the first real
  `SL-` row is minted, `grep -n 'Not yet in force as of 2026-09-27' CONTRIBUTING.md
  .github/PULL_REQUEST_TEMPLATE.md` must be empty (the marker removed) — a check the
  executor of that later slice runs, not this one.
- **DP-4's violation** — `.importlinter` drifting from what the migration actually named —
  is already covered by `uv run lint-imports`, which fails if the contract names do not
  match real `ADR-`/`DEP-` files; Task 8 runs it and records `EXIT=0` as the verify-only
  evidence.
- **DP-5's violation** — a public-face file describing a layout the repository no longer
  has — is checkable by the same sweep the plan's own Acceptance item 5 already runs:
  `grep -nE 'docs/(notes|audit)/|NT-[0-9]' README.md CONTRIBUTING.md …` must return no hit
  for `docs/audit/` after Tasks 4 and 5, given the plan's existing baseline-vs-after
  comparison in that item.
