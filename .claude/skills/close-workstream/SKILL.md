---
name: close-workstream
description: Audit a workstream (W1, W2, …) before declaring it closed in docs/roadmap.md. Starts by deriving the expected scope from docs/specs/ with scripts/scope-audit.py and only then looks for evidence — never from recollection of what was built. Also covers running the gate locally, proving new checks fail on broken input, measuring rather than asserting NFRs, and giving every unevidenced requirement a verdict. Use when asked to close, sign off, or confirm a workstream is complete — and before writing any "✔ closed" into the roadmap.
---

# Closing a workstream

`CLAUDE.md` §13 is the standard. This is how to satisfy it.

The failure this guards against is not "we forgot a task". It is a roadmap that reports
progress the repository does not have — which is worse than no roadmap, because the next
workstream is planned against it.

## 0. Derive the scope from the specs first — then go looking for evidence

Do this **before** opening any source file or recalling anything you built. The order is
the method: enumerate what the specification requires, then search for evidence of each
item. Reversed, an audit can only confirm what exists and is silent about what is missing —
which is the half a closure record is for.

```bash
sed -n '/^## 6/,/^## 7/p' docs/roadmap.md          # the workstream's named areas
uv run python scripts/scope-audit.py PLAT --sections 3.1,3.2,3.3,3.7,3.8 \
    --extra FR-PLAT-47,FR-PLAT-48
```

`scope-audit.py` reads requirements from `docs/specs/` and evidence from
`@pytest.mark.req` markers. Both are documents; neither is your memory. It exits non-zero
while anything in scope lacks evidence.

**Map the workstream's named areas to spec sections yourself.** "Platform core: jobs, blobs,
settings, OIDC auth, health, tracing" is `07` §3.1, §3.2, §3.3, §3.7, §3.8 — 33
requirements — plus FR-PLAT-47/48 for the API conventions and the generated contract, which
is 35, and 35 is what the roadmap's "~35" meant. Getting to that number *from the spec* is
what makes the next step meaningful.

**Then check for requirements assigned elsewhere**, so you neither claim nor blame them:

```bash
grep -nE '\| \*\*W[0-9]+' docs/roadmap.md | grep PLAT     # e.g. FR-PLAT-28..31 → W14
```

**Reconcile against the roadmap's own count.** A disagreement is a finding: W2's row said
"of 60" where the spec now holds 61, because FR-PLAT-51 was appended afterwards.

**Requirement coverage is not interface coverage, nor catalogue coverage.** Run all three
axes; each answers a different question and a green one says nothing about the others:

```bash
uv run python scripts/scope-audit.py <MOD> --endpoints    # §5.1 table vs the contract
uv run python scripts/scope-audit.py <MOD> --catalogue VR # a spec's named-item catalogue
```

W4 stood at **49 of 50 requirements with 0 of 28 endpoints published**, and nothing said so.

**Give every unevidenced requirement a verdict** — delivered but untested, deferred with an
owner, reassigned, or not started. Silence is not one of the options, and it was the
default for four of W2's six gaps until an audit went looking.

## 0a. Evidence is not only markers

`scope-audit.py` sees `@pytest.mark.req` and nothing else. A requirement enforced by an
import-linter contract, a database privilege, a migration or a recorded measurement reads
as unevidenced. Before writing a gap into a closure record, ask **how else this could be
enforced** — and then make that enforcement visible, in a test that runs the check and
names the requirement, rather than leaving the audit to rediscover it next time.

W1's re-audit reported half its scope missing while every one of those mechanisms was
working. The mechanisms were fine; the record could not see them.

Where a test is genuinely the wrong instrument, say so and keep the measurement: NFR-PLAT-4
would otherwise have CI start containers on every push to assert a number that varies with
the runner.

## 0b. Read the markers that matter

A marker is a *claim* that a test asserts something about a requirement, not proof that it
covers it. For anything load-bearing — an authorisation boundary, an immutability rule —
open the test and check the assertion is exact. W2 had a test accepting *either* of two
error codes, which would have passed whether or not the environment check it named
existed.

## 1. Each deliverable: exists *and* works

Two different claims. Record which one you checked.

| Deliverable kind | "Exists" | "Works" |
|---|---|---|
| Package | directory present | `uv run pytest` covers it, imports resolve |
| CI workflow | file committed | a run is green on the merge commit |
| Config that enforces a rule | file committed | **§3** — it fails on broken input |
| Compose / deploy file | file committed | brought up, healthy, timed |
| Type or schema | class defined | round-trip test, and a rejection test |

W1's `docker-compose.yml` sat committed and unrun for days. It worked — but nobody knew
that, and NFR-PLAT-4 was unverified the whole time. "Committed" is not evidence.

## 2. The full gate, locally

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
```

**Both halves.** The frontend half is a separate workflow and has been red while this one
was green — [`dev-commands`](../dev-commands/SKILL.md) has it, with the `--frozen-lockfile` and
generated-client traps.

Locally, not just "CI is green" — see `reproducing-ci-locally`. Paste the real output into
the closure record; a summary you typed from memory is not evidence either.

## 3. Prove every new check is non-trivial

For each check the workstream added, break something on purpose and confirm it fails:

```bash
# example: is the import-linter contract actually enforcing ADR-0001?
echo "import fastapi" >> packages/pricing_core/src/pricing_core/money.py
uv run lint-imports          # MUST report a broken contract
git checkout -- packages/pricing_core/src/pricing_core/money.py
```

**Restore by the method that matches the file's state.** `git checkout -- <path>` silently
fails on an **untracked** file — a new module in the slice you are testing — and prints an
error that is easy to skim past while the sabotage stays in place. Copy the file aside
first, or check `git status` after restoring rather than trusting the command.

This is not paranoia. `.importlinter` was silently dead for a day: `root_packages` was
comma-separated on one line, so the ini parser split it character by character and looked
for a package named `m`. It reported success while enforcing nothing.

The same discipline applies to your own verification one-liners. Ones that have produced
false positives here: a `✓` echoed on `head`'s exit code rather than the command's; a
`\echo` in `psql` that printed unconditionally and read as success when the `ERROR` line
above it proved the opposite. **If a check has never printed a failure, you have not tested
the check.**

### The injection must break what the check *claims* to measure

A proof can pass for the wrong reason. `--catalogue VR` was shown to fail on broken input —
an id was deleted and the count dropped — and the check was counting **docstrings** the
whole time. The injection proved the counter could count; it never tested *what* was being
counted. An independent audit later found all 38 "implemented" rules were prose mentions,
two of them expanded from a single `VR-ACT-1/2/8` comment, and the honest count was 1.

Before trusting an injection, ask **which claim it falsifies**. If the check says "this rule
is implemented", break the *implementation* — not a comment that happens to name it.

### A check's design note must say which part fails open and which fails closed

Proving a check fires is not enough if the note beside it misattributes *why*. The W32
closure tripwire is `^#+ W32[a-z]?([ —].*)?: closed <date>`, and its design note credited
`[a-z]?` with keeping slice headings out. It does not. `^#+ W32[a-z]?.*: closed …` fires on
`W32-7` and `W32-11` — **the whole exclusion lives in the constrained separator group**,
`([ —].*)?`, and the letter class only buys coverage of a split-then-letter `W32a` (`\b`
loses that form outright: `2` and `a` are both word characters, so there is no boundary).

| Token | Job | If weakened |
|---|---|---|
| `([ —].*)?` | **Safety** — excludes slices | Reports the *workstream* closed when a *slice* closed |
| `[a-z]?` | **Coverage** — admits `W32a` | Goes silent on the split-then-letter form |

**The safety token is always the one that looks over-engineered**, so a note saying only
*what* the pattern matches invites the next maintainer to simplify exactly the half that
must not move — and the failure is silent in the direction that matters. Name the two roles.
This generalises past regexes to any validator with a permissive and a restrictive half.

`W32\b.*` **is** that simplification — the obvious tightening of the permissive form, and
one that reads as strictly safer than `[a-z]?`. It fires on `W32-7` and `W32-11`. It was
proposed, defended and nearly adopted here across four sessions before a fixture run settled
it. *Who* proposed it went through three reversals while that verdict never moved once,
which is the argument for writing a design note about what a check **does** rather than
about where it came from.

**Say also what the check cannot see at all.** Fail-open and fail-closed both describe cases
the check *reaches*; the more expensive defects are outside its field of view entirely. Every
instrument defect in this thread was a blind spot rather than a wrong answer — a search
reading an inert file, a fixture that drifted from the tree under test, a bold-coupled
anchor, a conflated clause. A design note that lists only match and non-match implies the
field of view is the world.

### A gate whose passing state is empty output cannot be tested on the live tree

This is the shell case, and it is not covered by "prove it fails on broken input" — there is
nothing to break. A closure tripwire passes by printing **nothing**, and on a tree where the
answer is already *no match* an empty result is indistinguishable from a gate that is
misspelt, pointed at the wrong ref, or silently erroring. **Running it and seeing nothing
proves nothing.** Validate it against a copy of the real artifact with controls injected:

```bash
git show origin/main:docs/roadmap.md > live.md      # pin the REF, not the working tree
P='<the gate pattern, verbatim>'
grep -cE "$P" live.md                                # live       — expect 0
cp live.md pos.md; printf '\n<a real closure heading>\n' >> pos.md
grep -cE "$P" pos.md                                 # positive   — expect 1
cp live.md neg.md; printf '\n<the near-miss it must ignore>\n' >> neg.md
grep -cE "$P" neg.md                                 # negative   — expect 0
grep -cE '<the tempting simplification>' neg.md      # must be > 0 = the bug it avoids
```

Four rules, each learned by getting it wrong here:

- **Pin the ref.** Both halves must read `git show <ref>:path`, never the working tree.
  Parallel sessions run in worktrees routinely a commit apart, and a gate that reads whatever
  tree it lands in makes a claim about the wrong thing. That confusion misread a W32
  attribution line once already.
- **The positive control must run the gate's own pattern, verbatim.** A control that
  substitutes an equivalent-looking regex body tests a pattern nobody ships. That is exactly
  how a correct false-positive charge came to be wrongly retracted here: the check substituted
  a *constrained* separator into a proposal that used a *permissive* one, and the constrained
  form passed — so the retraction absolved a real bug.
- **The positive control must be a hard case, not an easy one.** Three of the five real
  closure records in this repository carry a suffix after the workstream name; a control using
  the bare form goes green because of everything it never exercises.
- **Add the fourth line.** Scoring the *tempting simplification* against the same negative
  input turns the safety token's necessity into a number rather than an argument, which is what
  a future maintainer weighing "this looks over-engineered" actually needs.

Keep the script. When the gate is discharged, keep its design note too — delete the gate, not
the reasoning, or the next person writing one starts from nothing.

### Do not re-derive a metric a script already computes — run the script

Auditing `req-coverage.py` by reimplementing its walk returned **261** against the script's
**266**: `testpaths` carries **two** repository-level roots beyond `backend/` and
`packages/` — `tests` and `examples/fremtpl2` — and both contribute markers, 11 and 7. The
hand-rolled walk missed both. A 2 % reimplementation error — larger than most defects such
an audit is looking for, and indistinguishable from a real finding.

A second implementation of a metric is a **second thing to be wrong**, not a check on the
first. If the script's *definition* is what is in doubt, read its source and say so; if the
*number* is what is wanted, run it and cite the SHA it was run at.

**Where you must count the repository yourself, count it with `git grep`, not `grep -r`.**
The index holds tracked files only, so generated and ignored output is excluded *by
construction* rather than by remembering to exclude it. Two sessions measured the same
population here and got 143 against 32; the larger number had swept
`frontend/src/api/generated`, which `.gitignore:38` excludes and which `git grep` therefore
never sees. A rule that says *state your exclusions* relies on discipline at the moment
discipline is scarcest; choosing the tool whose default is right does not.

### Verify a retraction against the artifact it retracts

Review pressure falls off along a chain. **Original text gets a reader. A correction gets
less, because it arrives labelled as a fix and so reads as already-checked. A retraction
gets least of all, because the party best placed to check it is the party it absolves.**

That last step is the dangerous one, and it produced three inversions in a single day here.
A correct charge against this repository's closure gate was withdrawn after the accused
tested a pattern *nobody had proposed* — a substitution neither party caught, because the
one who could have was the one being cleared. The retraction then licensed a **strike
order** against the skill text you are reading: delete anything certifying `W32\b.*` safe.
No such text existed. It was stopped only because a third session opened the file.

Two rules, both cheap:

- **Check a retraction against the thing retracted, never against the retractor's account
  of it.** An exoneration is the one correction its recipient has no incentive to check.
- **"Strike anything that says X" is a check when the sender has read the document and a
  guess in imperative grammar when they have not.** Against a green, mergeable PR the two
  are indistinguishable from the receiving end — so open the file before acting, and say in
  the instruction which one you are issuing.

The corollary is the reassuring half: across all three reversals **not one regex verdict
moved**. Every reversal was about attribution. Notes that record behaviour survived the
entire dispute untouched; notes that recorded provenance did not.

### A generated artifact matching its source proves neither is correct

W2's contract drift check passed while the published OpenAPI advertised an error model the
platform never emits and omitted the one it does. The contract faithfully described the
code; both were wrong together, and no amount of comparing them would have said so.

Check generated output against the **requirement** — open the spec clause and read the
document — not only against the thing it was generated from.

## 4. Measure NFRs, don't assert them

Record the number and the budget it is measured against:

> Cold start 21 s, warm 6 s, against NFR-PLAT-4's 300 s budget.

not "the stack starts quickly". An unmeasured NFR is an opinion with an ID.

## 5. Write down what was *not* delivered

Add a table mapping `docs/roadmap.md` §5 (the retrofit-impossible list) to where each item
actually lands — delivered here / type-level only / owned by a later workstream.

This is the section most worth writing, because "W1 closed" reads as "the retrofit list is
handled" unless something says otherwise, and that list is the one thing this project
cannot fix cheaply later.

## 6. Update the plan docs in the same commit

- `docs/roadmap.md` — status table, closure evidence with dates, the §5 mapping
- **Component status is `docs/roadmap.md` §6's alone.** `CLAUDE.md` §2 carried layout marks
  until the 2026-08-23 restructure and no longer does
  ([`NT-0003`](../../notes/0003-duplicated-status-goes-stale.md)) — verify the roadmap's
  marks against the filesystem, and do not reintroduce a second copy anywhere
- Any spec the implementation proved wrong — resolve it, don't silently match (§0)

The demo guide (FR-PLAT-54) is **derived, not written**, so there is nothing to update —
but check that it still derives:

```bash
uv run pytest backend/tests/test_demo_guide.py     # also runs in the gate
```

## 7. Clean up

```bash
gh pr list --state open                       # none left for this workstream
git status --short                            # no tracked build artifacts
git diff --stat main <branch>                 # empty ⇒ safe to delete
git branch -D <branch>                        # -d refuses after squash-merge
```

`git branch -d` refuses even when the work is fully merged, because squash-merge rewrote
the history. Verify by content, not by what git says about ancestry — see `git-hygiene`.

## Tests that must exist before you close

- **A negative test for every invariant the workstream introduced.** In a governed system
  the suite must prove the wrong thing *cannot* happen. `ArtifactRef` accepting `@0` got
  through because the tests only asserted that valid refs parsed.
- A `@pytest.mark.req` marker on each test — `req-coverage.py` fails on a requirement ID
  that does not exist, so the marker is checked, not decorative.
- A round-trip or property test wherever the workstream persists or transforms data.

## Closure record template

```markdown
### W<n> — <name>: closed <YYYY-MM-DD>

**Scope**, derived from `<spec>` §… rather than from the build log: N requirements.
Reconciles with the roadmap's claim of "~N" / *differs, because …*

| Deliverable (roadmap §6) | Evidence |
|---|---|
| … | … |

**Gate:** ruff clean · mypy --strict clean · N contracts kept, 0 broken · N tests pass ·
docs audit 15/15 · req-coverage N requirements

**Requirement coverage:** X of N in-scope requirements carry test evidence (Y %).

**Not delivered by W<n>:** every unevidenced requirement with a verdict — delivered but
untested / deferred with an owner / reassigned / not started — plus the §5 retrofit
mapping.
```

## Verified

2026-08-24 (second entry, at W32's close) — the empty-output gate section. Written from the
control script actually run before the closure record was accepted: live **0**, positive
control **1**, negative control **0**, and the tempting simplification **2** on the same
negative input. Filed as gap (a) of plan review 4's Q3, which found the shell case stated
nowhere — the nearest cousin was `contract-guard:91-95` on two empty maps intersecting green.

2026-08-24 — the four §3 subsections on instruments were added from the W32 closure gate's
own defects and each is verified from an artifact, not from an account of one: the four
regex verdicts re-run on a constructed fixture, `testpaths` read from `pyproject.toml:89`,
the `git grep` rule reproduced against `.gitignore:38`, and the retraction chain checked
against the diff it concerned.

2026-08-23 — the three scope-audit axes, the demo-guide derivation check and the
both-halves gate note moved here from `CLAUDE.md` §13 when that section was cut to its
binding rule. No procedure changed. Step 6's `CLAUDE.md` §2 layout-marks line was corrected
in the same pass: those marks no longer exist, and `docs/roadmap.md` §6 owns the status
outright.

2026-08-15 — the injection lesson above came from plan review 2, after an independent
audit found that this skill's own worked example had passed for the wrong reason.
