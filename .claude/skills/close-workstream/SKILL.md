---
name: close-workstream
description: Audit a workstream (W1, W2, …) before declaring it closed in docs/roadmap.md. Starts by deriving the expected scope from docs/specs/ with scripts/scope-audit.py and only then looks for evidence — never from recollection of what was built. Also covers running the gate locally, proving new checks fail on broken input, measuring rather than asserting NFRs, and giving every unevidenced requirement a verdict. Use when asked to close, sign off, or confirm a workstream is complete — and before writing any "✔ closed" into the roadmap.
---

# Closing a workstream

`CLAUDE.md` §13 is the standard. This is how to satisfy it.

**This skill closes a workstream against §13; it does not by itself raise `CLAUDE.md`
§14's phase review question.** That trigger is fixed, not discretionary — at each
workstream close, and again before a phase's exit demo — and satisfying §13 here does
not satisfy §14. Confirm with the planner whether a phase review (the
[`phase-review`](../phase-review/SKILL.md) skill) is now due before signing off.

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

**`--extra`'s comma list does not inherit a shared prefix — write every id out in full.**
The parser is a literal `args.extra.split(",")`: `--extra FR-PLAT-47,48` does **not**
expand to `FR-PLAT-47, FR-PLAT-48`. It produces the two tokens `FR-PLAT-47` and `48`, and
`48` alone matches no real requirement — so the intended `FR-PLAT-48` is silently never
added to scope at all, while the report shows a `NO EVIDENCE` row labelled `48` that reads
as if it were about the missing id. It is not: nothing checked `FR-PLAT-48` itself. This is
the same *silent* shape as `req-coverage.py`'s bold-coupling and clause-conflation
failures — a row that looks like a real verdict on the id you meant. The total in-scope
*count* usually still comes out right (one bogus token swapped in for one dropped id), so
the headline number will not tip you off; only the id column will. Verified at
`9891be1` (2026-08-29) by reading `scope-audit.py`'s parser source at that tree and
re-running the command there: `RATE --sections 3.7 --extra
FR-RATE-40,41,42,NFR-RATE-1,13,14` — the command as inherited from the prior audit at
`74b1b10`, a different tree than the one this verification ran against — parses to
`{FR-RATE-40, "41", "42", NFR-RATE-1, "13", "14"}`, not the six ids it reads as.
Re-running with every id spelled out
(`FR-RATE-40,FR-RATE-41,FR-RATE-42,NFR-RATE-1,NFR-RATE-13,NFR-RATE-14`) landed on the same
13-in-scope / 0-evidenced headline only because *nothing* in `RATE` §3.7/§3.8/NFR had any
marker at all that day — the substitution happened to be inert, not proven safe in
general. Confirm any inherited `--extra` string resolves to fully-qualified ids before
trusting its count.

**Fixed 2026-08-29.** `scope-audit.py`'s `_extra_ids` now validates every `--extra` token
against the module's own parsed requirement ids (`requirements_by_section`'s flattened
set) before any of them reaches scope, and refuses the **whole** list — naming every bad
token, with a "did you mean `FR-RATE-41`?" hint whenever a bare number looks like it
dropped the previous token's prefix — rather than silently accepting whichever tokens
happen to look like something. Re-running the incident's own string verbatim,
`--extra FR-RATE-40,41,42,NFR-RATE-1,13,14`, now exits non-zero naming all four bad tokens
instead of quietly parsing to a wrong six with a right-looking count. Deliberately **no**
shorthand syntax was added to auto-expand a bare number against the previous token's
prefix: that would reintroduce a second, silently-successful way to get this wrong, and
the failure here was ambiguity, not verbosity. Validation is scoped to the module under
audit, matching every `--extra` invocation on record including this file's own
`FR-PLAT-47,FR-PLAT-48` example above — none of them cross a module boundary.
`tests/test_scope_audit.py` proves both directions on the real ids: the incident's exact
string refused with the right per-token hints, a fully-qualified version of the same six
ids still accepted with byte-identical output to the pre-fix parser (diffed against the
genuine pre-fix script run in place, not assumed).

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

### A check on a proxy sees only the clauses the proxy has a shadow of

The blind spots above are incidental — a wrong path, a stale fixture. This one is
**systematic**, and it is the reason a check can be perfectly built and still not enforce
the rule it cites. It appears whenever a rule is about **semantics** and the check is
written against a **mechanical stand-in** for them.

Worked example, PR #435 (W11 Slice 2 Task 2A). Ruling 16 clause 4 forbids the bundle slot
four things — **refresh, poll, pub/sub, environment pointer**. The check asserts the
module's own import roots against an allowlist, on the stated ground that "none of the four
can be built without a broker client, a scheduler, a thread, or the metadata store." It
reaches **two**:

| Clause | What the slot itself must acquire | Import check sees it? |
|---|---|---|
| Poll | a clock **and** a scheduler or thread | yes |
| Pub/sub | a broker client | yes |
| Environment pointer | nothing — a `dict[str, str]` | **no** |
| Refresh | nothing — a deploy-time push arrives through the existing `put()` | **no** |

The import allowlist keys on **dependencies**. So it catches exactly the mechanisms that
make the module **reach out**, and misses the ones that only require it to be **reached
into** or to **hold a shape**. The environment pointer is the sharp case: the *permitted*
ref → hash memo and the *forbidden* environment → hash pointer are the same
`dict[str, str]`; the only difference is what the key means, and a dependency check cannot
see meaning. The refresh case is worse — it needs no new surface at all, so no check scoped
to that module can hold it, and the honest design note says so and names where it *is* held
(review of who calls `put()`).

**The diagnostic, one line per clause:** *name the dependency this clause would need.* Where
the answer is "none", the check is blind to it — and that is a fact about the instrument,
not about the code, so it stays true after every fix.

**Why a positive control will not surface this.** The control in that PR was exemplary:
six deliberately broken inputs appended to the *real* module source and run through the
check's own extraction, not a lookalike — the trap in *"prove it fails on broken input"*
avoided completely. But every one of the six was an **import**. A control is assembled from
violations its author can already see, so it confirms the check works **on its own field of
view** and is silent about the field's edge. **Passing a positive control licenses "this
check fires", never "this rule is enforced."** Write both sentences, or the next reader
takes the first as the second and stops looking.

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

### Search for the thing's shape, not its container's name (NT-0012)

The failure one step earlier than a false zero: **the query manufactures the zero.**

Something is not gone because the container it was last seen in is gone. It is gone only when
nothing that ever held or produced it survives anywhere. **Before declaring anything
unrecoverable — a credential, a file, a fact, a requirement's evidence — search for what the
thing itself looks like**: a value's prefix, a function's signature, a concept's description.
Not only the name of the place it was expected to be.

Three instances from one day, all the same substitution:

- A Slack token searched for by its job directory's name — the directory had just been
  cleaned, so the search could only fail. The token was findable by its value's prefix.
- A signature-sync ruling grepped the one-word identifier `CompiledBundle` and missed the
  concept spelled **"Compiled Bundle"**, two words apart, in the glossary it existed to check.
- A file-count check trusted a filename list over reading what each file's content changed.

**Naming the container is most tempting exactly where it is least reliable** — at the moment
the container has stopped existing. That is also the moment the null result is about to become
an argument, which is what the section below is about.

### A false zero argues — and two wrong methods agreeing is not corroboration

Worked example, 2026-08-30, and the rule it breaks is the one directly above, added to this
file the same day by the person who then broke it.

**The question was one of precedent.** A test delivered a requirement whose marker was
missing, and the cheap remedy was to stack a second `@pytest.mark.req` beside the first. Before
recommending it, the auditor asked whether stacked markers were an existing convention.
The sweep returned **none**, so the recommendation flipped to the expensive option: a whole
separate test. The lead's counter-sweep found **69** stacked pairs at `origin/main`, including
a three-deep stack that is itself the centrepiece of a §14 finding.

**Two defects, and finding the harmless one hid the fatal one.**

```bash
# BOTH of these return 0 on a tree with 69 stacked pairs.
git grep -n -A1 'pytest\.mark\.req(' <rev> -- <paths> | grep -cE '^[^:]+-[0-9]+-@pytest\.mark\.req\('
git grep -n -A1 'pytest\.mark\.req(' <rev> -- <paths> | grep -cE '[-:][0-9]+-@pytest\.mark\.req\('
```

- **Cosmetic:** `^[^:]+-` cannot match a line from `git grep <rev>`, whose `origin/main:` prefix
  contains colons. Real, and irrelevant.
- **Fatal:** `git grep -A1` emits **adjacent matches as match lines** (`:`), never as context
  lines (`-`). The context line under a stack is always the `def`. So a pattern hunting for
  *"a match line followed by a context line containing a marker"* **cannot fire on a stack at
  all** — the thing it is looking for does not exist in the output format.

The second command fixes the cosmetic defect and inherits the fatal one. Its zero was
**structurally guaranteed**, so its agreement with the first carried no information — and read
as confirmation. **Two wrong methods agreeing is not corroboration**; when a second attempt
repeats a null, check whether it repaired the part that produced the null.

**Correct detection ignores `-A1` and looks for consecutive line *numbers* within one file:**

```bash
git grep -n 'pytest\.mark\.req(' <rev> -- <paths> \
  | awk -F: '{f=$2; n=$3; if (f==pf && n==pn+1) c++; pf=f; pn=n} END {print c+0}'
```

**Why this class deserves its own rule.** Most null results invite more looking. A null on a
**precedent** question closes the question instead, because *"no precedent exists"* is a
positive claim with a decision attached — it argues, and it argues for the more expensive
option. A false positive gets challenged by the next person to read the artifact; a false zero
is agreed with.

**The control cost one command** — run the pattern against a case known to exist — and it
scored **0 against a three-deep stack sitting in plain view**. It was run only after challenge.

That is the whole argument for running one, and the fact that this file's own author skipped it
hours after writing *"running it and seeing nothing proves nothing"* is recorded deliberately:
a rule its author forgets under load is evidence about the rule's ergonomics, not about the
author. **Bind the control to the act, not to the intention** — a sweep whose answer will change
a recommendation gets a positive control in the same command block, before the answer is read.

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

### A count over a corpus a transform will change must be taken on the side the claim is about

Two people made the same mistake on the same finding within an hour of each other on 2026-09-03,
so this is a shape problem rather than a reader problem.

The claim was *"once this script merges, the acceptance row that counts occurrences of a string
cannot reach zero, because the script's own source contains that string."* The evidence offered
was:

```bash
grep -cE '\b(docs/notes/)' scripts/_docverify.py     # 5
```

**That count is over the un-migrated file. The claim is about the migrated corpus.** The
migration rewrites four of the five occurrences — they are ordinary path citations and rewriting
them is what the migration is *for* — so the real contribution is **1**, not 5. The auditor
published 5; the lead then "verified by structure rather than by a migration run" and reproduced
the same 5. Neither check was wrong about the file it read. Both were about the wrong file.

**The rule.** When a transform (a migration, a codegen step, a formatter) stands between two
trees, a count is evidence for a claim only if it was taken **on the same side of the transform
as the claim**. `CLAUDE.md` §13 already requires a count to carry its tree; this is the case where
carrying the tree is not enough, because *both* trees are real and the wrong one gives a
well-formed answer.

**Make it structural, not a matter of care.** State the side in the sentence that carries the
number, so a reader can see the mismatch without re-deriving anything:

```
# invites the error — "the file" is ambiguous between two trees
the script's source contains the string 5 times, so the row cannot reach zero

# forces the check — the tree is inside the claim
at a MIGRATED snapshot of <sha>, `git grep … -- $FILES | grep -c '_docverify'` is 1
```

**And beware a before/after pair that cannot exist.** The same finding claimed *"118 at a tree
without the instrument and 123 at a tree with it, over the same corpus"* — but the instrument
merged six commits after the tree that produced 118. **A false controlled comparison is more
persuasive than a wrong count**, because it looks like the thing that would settle the question.
If you cannot name one corpus that exists in both states, you do not have a before/after.

### A regex's meaning is not its text, and a string search only sees the text

The second half of the same finding asserted that a literal *had* to stay in the code because
"the acceptance sentence contains it". It does not. The sentence writes the alternatives
**factored**:

```
docs/(plans/2026-|audit/|notes/|adr/)
```

which **matches** everything `docs/notes/` matches while **containing** no such substring. The
verbatim constant therefore did not trip the row at all; only a hand-retyped decomposition of it
did. The consequence was not academic: three remedies were being priced at standard level for
something a code change removed.

**When a claim is about a string appearing in a file, `grep` for that string in that file.** Do
not reason from what the pattern *means*. The counter-example that should have prompted the
check was in the same constant: `\bF[0-9]{2}\b` appears identically in both the factored form and
the decomposition, so it genuinely is unavoidable — the two alternatives were not alike, and the
generalisation came from the one that happened to be open.

### A "verified against tree" field set at authoring time cites a tree that never held the change

`docs/process/delivery-process.core.json`'s `meta.verified_against_tree` exists so a future
digest mismatch can name the exact range to read: `git diff <verified_against_tree>..HEAD --
delivery-process.md`. That only works if the recorded commit is one where the digest and the
markdown were actually reconciled **together** — the tree a human read both artifacts at.

**Setting it to the branch's own base, at authoring time, is the wrong commit by
construction**: a PR's base is the tree *before* that PR's own edits, so a branch that edits
`delivery-process.md` and updates the digest in the same commit cannot correctly cite its own
base — the base is exactly the tree the reconciliation was checking *against*, not the tree it
was performed *at*. NT-0014 adoption slice H set the field to its own base commit when it
first built check 27; slice G rebased onto H, edited `delivery-process.md` again, "re-reconciled"
the digest — and set the field to slice H's base too, one commit further removed from the
actual reconciliation. Neither was caught, because check 27 (`scripts/audit-docs.py`) validates
only the **digest** against the current file bytes — never the SHA against anything — so a wrong
SHA produces no red anywhere. Confirmed live at `9e8783d`: `meta.verified_against_tree` reads
`79991f36c3337b87a2ae788acae3c255d5ae1084`, a tree that predates slice G's own edits to
`delivery-process.md` §6/§7 by one merge; `git diff 79991f3..HEAD -- docs/process/
delivery-process.md` at that point would show a future reader G's own already-reconciled
changes as if they were an unreviewed drift, which is the opposite of what the field exists to
tell them.

**It was harmless here only by accident.** H's own citation of its base was never wrong in
effect, because nothing between H's base and H's own commit touched the spec bytes the digest
covers — the field pointed at a stale-but-content-identical tree. That is not a property of the
mechanism; it is a property of nobody having landed a second `delivery-process.md` edit in
between, which G then did.

**The fix: recompute both fields at the actual merge commit, after merge, not at authoring
time.** The PR author cannot know the eventual merge SHA before GitHub assigns it, so citing a
tree "at authoring time" always means citing something *before* the change — the branch's own
base or an ancestor of it. Either recompute the digest (it will not move, since it is a hash of
content already correct) and set the tree field to the actual merge commit in a small follow-up
once it is known, or — cheaper, and what should become the norm — do not set the field to a
commit at all until the merge is known; leave it pointing at the previous reconciliation's
commit until a follow-up (or the next PR that touches the spec) updates it to the new merge SHA
in the same motion. Never cite the working branch's own base as if it were the point of
reconciliation.

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

## 5a. Every binding plan-review condition has its artifact

**A §14 plan review's maintainer acceptance can put an obligation on this close, and
accepting a recommendation is what puts it in force — it does not discharge it.** Read
[`docs/audit/plan-reviews.md`](../../../docs/audit/plan-reviews.md), find every dated
acceptance whose condition names this workstream's close, and check the artifact each one
demands actually exists. Quote the clause and name the artifact; a date is not evidence.

```bash
grep -n "Maintainer acceptance" docs/audit/plan-reviews.md    # then read each one's clause
```

**Why this is its own step rather than part of §5.** §5 asks what was not delivered, which
is answered from the build. This asks what an earlier decision *promised* would be recorded,
which is answered only from `plan-reviews.md` — and nobody rereads a review at closing time,
because by then it reads as settled. The failure is silent in both directions: the review
looks accepted, and the closure record looks complete.

**The instance this step was written from.** Plan review 8 §5.1 recommended no re-cut of
Phase 2's W11–W14 boundaries and was accepted 2026-08-29. The acceptance says, in the
maintainer's own words, *"Acceptance makes the paragraph above binding. It does not meet
it"* — FR-RATE-34 and FR-RATE-40 must **each** get an explicit, named, dated deferral in
[`register.md`](../../../docs/audit/register.md) when W11 closes, *"not silence, and not a
stub shipped and called done"*, and *"reading this date as having satisfied it would invert
the clause"*.

Two traps that entry also records:

- **A ruling is not a register row.** W11's DP1 and DP2 were both ruled, and the acceptance
  says plainly that this does not write the rows: *"a ruling settles what the code does, a
  register row records what the workstream did not deliver, and those are different
  artifacts."*
- **A mention inside another row is not a row.** Checking the obligation by grepping the id
  returns F-W9-2's prose *"specialises FR-RATE-40's general approval-evidence gate, which W11
  builds"* — the id appears, and the deferral does not exist. Grep for the id, then read
  every hit to see whether it is a row *about* that requirement or a row that merely names it.

**The precedent for taking this seriously:** F-W9-1 carried NFR-RATE-13/14 forward with a
register row that did exist, and the roadmap still lost them for two workstreams — W11's row
records them as *"omitted from this row until now"*. A row is necessary and has not been
sufficient.

## 5b. Generate the owed list, don't recall it

`docs/audit/register.md`'s open rows owed by, or blocking, this close are not a list you
compile by hand while writing the closure record — that is precisely how F41 lost
NFR-RATE-13/14 for two workstreams even though a register row, F-W9-1, existed for them the
whole time (§5a's own precedent quotes the same row). Run it and paste the output verbatim:

```bash
python3 scripts/register-owed.py <work-id>     # e.g. W11
```

**Ruling 52** (`docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md`) binds the result's shape,
and the exact wording is in
[`checklists/work-item-close.md`](../../../docs/audit/checklists/work-item-close.md)'s Owed
list step: the block names the command and the **committed revision** it ran against (the
script itself refuses on an uncommitted register — never a bare date, never a dirty
worktree), it lands verbatim as a fenced, explicitly-generated block, and it is **evidence,
not authority** — it is not a substitute for the hand-written Findings section, which still
carries per-close judgements and findings that name no register row (`FR-RATE-36, 37, 42 not
started` is real and has no row). Reconcile the two in one sentence: every id in the
generated block appears in the Findings section with a resolution, and the Findings section
adds nothing the block does not carry except findings named as having no register row.

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

**Retry counters (NT-0014 artifact B, `~/gi-pricing-plan.local/handover/
runtime-state.json`):** this workstream's final `replan`/`fix` counts per layer, read with
`python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py show` —
`none recorded` is a valid value, not an omission, when the workstream closed clean on
its first pass.

**Requirement coverage:** X of N in-scope requirements carry test evidence (Y %).

**Not delivered by W<n>:** every unevidenced requirement with a verdict — delivered but
untested / deferred with an owner / reassigned / not started — plus the §5 retrofit
mapping.

**Binding plan-review conditions:** each dated acceptance conditioning this close, the
artifact it demanded, and where that artifact now is. *None* is a valid answer only after
looking.
```

## Verified

2026-09-03 — §3 gains two measurement traps, both from W37-6's NT-0019 §7 second measurement
(`docs/research/nt-0019-second-measurement-2026-09-03.md` §14 and §15, and F101). Added because the
first was made independently by two people on the same finding within an hour, which makes it a
property of how the finding was stated rather than of who read it. Tree: `4b9117a`.

2026-08-31 — §5b added, NT-0015 P5 (Ruling 52, `docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md`):
`scripts/register-owed.py` exists and its tests pass (`tests/test_register_owed.py`). Not
yet cited by a real closure record — the first close to use it is this proposal's own
acceptance evidence.

2026-08-31 — added the closure record's retry-counters line, NT-0014 adoption slice G
(impact-matrix row 16: "Closure record includes the layer's final retry counters read
from B"). The field became writable only once `scripts/hooks/retry_cap_hook.py` (C2)
existed to populate it — no closure has cited it yet.

2026-08-30 — §5a, written at W11's close from an obligation that was live and unmet while
this skill had no step that would have found it. Plan review 8 §5.1's acceptance
(`docs/audit/plan-reviews.md:987-1005`) requires named, dated register deferrals for
FR-RATE-34 and FR-RATE-40; `git grep -n "FR-RATE-34\|FR-RATE-40" docs/audit/register.md`
returns exactly one line, F-W9-2's prose about FR-RATE-61, and neither id has a row. The
acceptance had itself verified this and said so — the gap was that nothing in the closing
procedure sends a reader back to it. Same class as the §14 trigger that fired for neither
the W9 nor the W10 close.

2026-08-29 (second entry, the tool fix for the trap immediately below) — `_extra_ids`
validates every `--extra` token against `by_section`'s own flattened id set for the module
under audit before any of them reaches scope, and refuses the whole list naming each bad
token. Confirmed both directions by hand, in `scope-audit.py`'s own worktree: the
incident's own `FR-RATE-40,41,42,NFR-RATE-1,13,14` now exits non-zero naming `41`, `42`,
`13`, `14`, each with a "did you mean" hint against the correct prefix (`FR-RATE-41` etc.);
a version with all six ids spelled out
(`FR-RATE-40,FR-RATE-41,FR-RATE-42,NFR-RATE-1,NFR-RATE-13,NFR-RATE-14`) produces
byte-identical output to the pre-fix parser on the same input — diffed against the genuine
pre-fix script swapped back into its own path (`git checkout --` on a backed-up copy, per
this skill's testing sibling `python-test`'s "never `git checkout --` a file you are
working on"), not assumed from reading the source. `tests/test_scope_audit.py` pins both
directions plus a cross-module id (`FR-PLAT-47`, real but not RATE's) and a leading bare
number with nothing valid before it to guess a prefix from — each proven to fail against
the pre-fix parser before being trusted.

2026-08-29 — the `--extra` comma-prefix trap in §0, found re-deriving W11's own baseline
at tree `9891be1` (`scripts/scope-audit.py RATE --sections 3.7 --extra
FR-RATE-40,41,42,NFR-RATE-1,13,14`, a command inherited verbatim from the prior audit at
`74b1b10` — that SHA names only where the command came from, not where this entry's own
reading and re-run were done). Confirmed at `9891be1` against the parser
(`scope-audit.py`'s `args.extra.split(",")`, a literal split with no prefix inheritance)
and by running both the as-given string and a fully-qualified version side by side, both
also at `9891be1`: same
13-in-scope / 0-evidenced headline, different (and for the as-given string, wrong) token
set underneath. The headline agreeing is what made this easy to carry forward unnoticed —
recorded so the next `--extra` list is written fully qualified from the start rather than
re-discovered.

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

2026-08-31 — the `meta.verified_against_tree` authoring-time habit, found auditing the
NT-0012/0013/0014 adoption's close. Confirmed live at `9e8783d`:
`docs/process/delivery-process.core.json`'s `meta.verified_against_tree` reads
`79991f36c3337b87a2ae788acae3c255d5ae1084`, slice H's own base commit — one merge before
slice G's own edits to the spec bytes the digest covers, both re-set by G to the same wrong
value. `uv run mypy` and `check 27` were both green throughout; check 27 validates the
digest, never the SHA, so the wrong citation produces no failure anywhere. No register row
filed — the digest itself is correct and the citation self-heals whenever `delivery-process.md`
next changes, so this is process guidance for the next author, not an open defect with an
owner.
