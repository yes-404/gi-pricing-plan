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
- `CLAUDE.md` §2 — layout marks; verify all of them against the filesystem, `…` → `✔`
- Any spec the implementation proved wrong — resolve it, don't silently match (§0)

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
