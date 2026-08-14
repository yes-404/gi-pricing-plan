---
name: close-workstream
description: Audit a Phase 1a/1b workstream (W1, W2, …) before declaring it closed in docs/roadmap.md. Covers re-verifying deliverables against their roadmap definition, running the full local gate, proving new checks fail on broken input, measuring rather than asserting NFRs, stating what was not delivered, and updating the plan docs in the same PR. Use when asked to close, sign off, or confirm a workstream is complete — and before writing any "✔ closed" into the roadmap.
---

# Closing a workstream

`CLAUDE.md` §13 is the standard. This is how to satisfy it.

The failure this guards against is not "we forgot a task". It is a roadmap that reports
progress the repository does not have — which is worse than no roadmap, because the next
workstream is planned against it.

## 0. Re-read the definition first

```bash
sed -n '/^## 6/,/^## 7/p' docs/roadmap.md   # the workstream table
```

Audit against **what the roadmap said the workstream would deliver**, not against what you
remember building. These drift, and memory drifts toward "done".

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

This is not paranoia. `.importlinter` was silently dead for a day: `root_packages` was
comma-separated on one line, so the ini parser split it character by character and looked
for a package named `m`. It reported success while enforcing nothing.

The same discipline applies to your own verification one-liners. Ones that have produced
false positives here: a `✓` echoed on `head`'s exit code rather than the command's; a
`\echo` in `psql` that printed unconditionally and read as success when the `ERROR` line
above it proved the opposite. **If a check has never printed a failure, you have not tested
the check.**

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

| Deliverable (roadmap §6) | Evidence |
|---|---|
| … | … |

**Gate:** ruff clean · mypy --strict clean · N contracts kept, 0 broken · N tests pass ·
docs audit 14/14 · req-coverage N requirements

**Not delivered by W<n>:** <the §5 mapping table>
```
