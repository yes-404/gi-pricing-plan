# Ruling 60 — Ruling 59 §3 point 2's fetch path is broken against github.com; resolved by
full-history checkout, not by repairing the fetch (2026-09-01)

**What this is.** Ruling 59 (`2026-09-01-nt-0016-slice2-fr-data-32-ruling.md`, merged as
PR #539/`7f1e3c6`, implemented as PR #541/`15eb633`) is **merged and frozen**. This is a new,
citing record superseding its §3 point 2 and §4's cases, not an edit to that file
(`CLAUDE.md` §12).

**What happened.** #537 was rebased onto `main` at `15eb633`, putting a real committed
census and the merged carve-out into one checkout for the first time. CI's `python` job
failed:

```
FAILED backend/tests/test_lineage.py::test_no_reference_rows_are_bundled_in_the_repository -
AssertionError: docs/audit/file-census-5ef559d.csv: names commit '5ef559d' as the tree it
documents, but that commit could not be resolved (local resolution and `git fetch --depth 1
origin <sha>` both failed) — refusing to exempt a file whose provenance cannot be verified
(Ruling 59 §3 point 2)
```

The guard behaved exactly as designed: it failed loudly, named the file and the SHA, and did
not exempt a file it could not verify. Ruling 59 §4's third case (added in that record's own
§7 correction) is why this surfaced as a legible test failure instead of a silent pass. What
failed is the **provenance check's own ability to run**, not the check's logic.

## Acceptance Standard

1. `git grep -c "^## Ruling 60" docs/plans/2026-09-01-ruling-60-census-provenance-checkout-depth.md`
   returns `1`, and `git grep -n "^## Ruling " docs/plans/` shows 60 filling the gap
   immediately after Ruling 59 with no duplicate and no skip.
2. §2 names the chosen and both rejected candidates with the evidence that separated them,
   each verified against the real `github.com` remote or measured directly — never asserted.
3. §3 states precisely what changes and where (one workflow file, one line), leaving
   `resolve_commit`'s existing fetch-fallback in place rather than removing it, with the
   reason stated.
4. §4 confirms all three of Ruling 59 §4's broken-input cases still hold under the amended
   mechanism, case by case.
5. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
6. `git grep -nE '\bFR-[A-Z]+-[0-9]|\bNFR-[A-Z]+-[0-9]|\bOQ-[A-Z]+-[0-9]|\bADR-[0-9]'
   docs/plans/2026-09-01-ruling-60-census-provenance-checkout-depth.md` returns matches only
   to `FR-DATA-32` — no new requirement id, no spec amendment.
7. `git diff --stat <merge-base>..<branch> -- docs/` names exactly this one new file — the
   merged `2026-09-01-nt-0016-slice2-fr-data-32-ruling.md` is not edited.

---

## 1. Verified first, at `15eb633` (`origin/main`, fetched immediately before this record)

| Claim | Verdict |
|---|---|
| The quoted CI failure is real and current | **Confirmed** — `gh run view 33503839903 --log-failed`: `FAILED backend/tests/test_lineage.py::test_no_reference_rows_are_bundled_in_the_repository`, message matches the dispatch verbatim; `1 failed, 2543 passed, 2 skipped, 1 xfailed` |
| PR #541 implemented Ruling 59 as specified — `resolve_commit`, `generated_from_tracked_corpus`, the registry, the header check, the sorted path-list comparison, all three §4 cases | **Confirmed** — read `backend/tests/test_lineage.py` at `origin/main`: `resolve_commit` does local `git rev-parse --quiet --verify "<sha>^{commit}"` then `git fetch --depth 1 origin <sha>` then re-verifies against `FETCH_HEAD`, returns `None` (never raises) on double failure; `generated_from_tracked_corpus` raises `AssertionError` naming the file and SHA when `resolve_commit` returns `None` — exactly Ruling 59 §3 point 2's specified hard-fail, not a regression in the executor's work |
| Root cause: `git fetch` treats a non-40-char argument as a ref name, never reaching object-fetch | **Confirmed, independently, against the real remote** — `git clone --depth 1 https://github.com/yes-404/gi-pricing-plan.git`, then `git fetch --depth 1 origin 5ef559d` (7 chars): `fatal: couldn't find remote ref 5ef559d`, exit 128. Reproduces the dispatch's own manual reproduction exactly |
| A full 40-character SHA reaches the object-fetch path and succeeds against `github.com` | **Confirmed, independently, against the real remote — closes Ruling 59's own flagged caveat, which was correct to flag and is now resolved rather than merely re-asserted.** Same shallow clone, `git fetch --depth 1 origin 5ef559d5f964eba85eeaa4238c71e4eb20e31f4b` (40 chars): succeeds, `FETCH_HEAD` resolves to the exact commit. `uploadpack.allowReachableSHA1InWant`/`allowAnySHA1InWant` is confirmed **on** for this repository, today — the first time this session that policy has been tested against `github.com` rather than a `file://` remote |
| `fetch-depth: 0` is cheap for this repository, measured rather than assumed | **Confirmed** — `git clone --depth 1` vs. plain `git clone` (full history) against the real `github.com` remote: `1.56s` / `6.5M` `.git` vs. `2.02s` / `9.2M` `.git` — a difference of ~0.5s and ~2.7MB. 556 commits total on `main`. Not a proxy for `actions/checkout`'s own internals, but the same network round trip and object count it would fetch |
| `.github/workflows/python.yml` sets no `fetch-depth` anywhere, and there is no documented rationale for the current default | **Confirmed** — `grep -n fetch-depth .github/workflows/python.yml` returns nothing; `grep -rn "fetch-depth\|shallow"` across `.claude/skills/` and `docs/` returns nothing preceding this ruling. The depth-1 behaviour is `actions/checkout@v4`'s unexamined default, not a decision this repository made and is now overriding |
| The `pull_request` trigger exists alongside `push`, both hitting the same single checkout step | **Confirmed** — `.github/workflows/python.yml:38` (`pull_request:`), one `actions/checkout@v4` step at `:106`, no per-trigger override |
| A local full-history clone resolves the abbreviated SHA with no fetch at all | **Confirmed** — inside the full clone, `git rev-parse --quiet --verify 5ef559d^{commit}` exits `0` and prints the full OID, with zero network calls beyond the initial clone |

## 2. Ruled

**Is Ruling 59 §3 point 2's mechanism sound? No** — not in its logic, which behaved exactly
as specified (hard-fail, never silent exemption), but in its binding: it assumed a shallow,
depth-1 checkout could always reach `github.com`'s arbitrary-SHA fetch path with an
*abbreviated* SHA, and that assumption was false, verified now against the real remote
rather than a `file://` stand-in.

**Chosen: (2) — set `fetch-depth: 0` on `python.yml`'s checkout step.** This removes the
dependency rather than repairing it, per the standing preference stated when this amendment
was requested: with full history present in every checkout, `resolve_commit`'s first branch
(`git rev-parse --quiet --verify` against the local repository) always succeeds for any
commit reachable from the tested ref's history — which every registry entry's SHA is, by
the census's own design principle (`docs/audit/file-census.md`: "a concrete,
already-existing, independently checkable commit"). The fetch fallback is never reached in
ordinary operation once this lands, and `github.com`'s SHA-fetch policy — confirmed on
today, but external, unenforced by this repository, and not something a future GitHub
change is obliged to preserve — stops being load-bearing for CI at all.

**Rejected: (1) — carry the full 40-character SHA in the census filename.** Verified to work
mechanically (§1) and it is a smaller, more local change than (2) — but it does not remove
the dependency the amendment was asked to prefer removing; it only makes the abbreviated-ref
failure unreachable while leaving CI's ordinary path for every future registry entry
dependent on `github.com` continuing to permit arbitrary-SHA fetches, a policy this
repository does not control and had verified exactly once, today, before this ruling. It
also requires editing #537 — renaming an artifact a prior, accepted plan already named and
generated at a specific commit (`docs/plans/2026-08-31-nt-0016-investigation.md` §7's
Interfaces section: `file-census-<tree>.csv`, and `<tree>` has been treated as the short form
throughout NT-0016's own text, including this filename in Ruling 59 itself) — churn (2)
avoids entirely. No specific reason was found to prefer it over (2); it is the "repairs the
dependency" limb the standing preference asks to be chosen only with a stated reason, and
none surfaced under measurement.

**Rejected: (3) — deepen on demand (`git fetch --deepen`/`--unshallow` inside the test when
local resolution fails).** Keeps the network dependency (still requires reaching
`github.com` at test time, on every CI run where local resolution first fails — which, under
the *unamended* mechanism, is every run once `main` moves past the checkout's shallow
frontier) and is the most expensive per-run of the three: a full unshallow fetch inside a
pytest call, repeated on every invocation that reaches it, rather than once during the
checkout step itself. (2) achieves the identical end state — full history present before any
test runs — at the point in the pipeline built for exactly that (the checkout step), for a
measured, negligible, one-time-per-run cost, and gives up nothing (3) offers.

## 3. What changes, precisely

One line, in `.github/workflows/python.yml`'s existing `actions/checkout@v4` step (currently
`:106`, no `with:` block):

```yaml
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4
        with:
          fetch-depth: 0
```

**`resolve_commit` and `generated_from_tracked_corpus` in `backend/tests/test_lineage.py`
are unchanged.** The fetch-fallback branch (`git fetch --depth 1 origin <sha>` /
`FETCH_HEAD`) stays in place rather than being deleted, for three reasons stated so the
choice is not mistaken for an oversight: it is what makes Ruling 59 §4's third case
(unresolvable SHA) demonstrable at all against a synthetic fixture, independent of the real
checkout's depth; it is defence in depth for any checkout context this workflow does not
control — a developer running `pytest backend/tests/test_lineage.py` directly against a
shallow local clone, or a future CI configuration regressing the `fetch-depth` this record
adds; and removing working, already-reviewed, already-tested code to chase a marginal
simplification is not this ruling's business — `CLAUDE.md` §12 leaves implementation
judgement calls like this to the executor, and the fallback costs nothing to keep once it is
no longer load-bearing for the one path that matters.

**Revisit trigger, stated rather than left implicit**: if a future measurement of this
repository's full-history checkout cost (`.git` size or checkout wall-clock time on the
runner, not the local proxy measured in §1) becomes material to the gate's own NFR budget,
that is the point to reconsider — not before. No number is set here because none is owed
yet; §1's proxy measurement (0.5s, 2.7MB, 556 commits) is far from any plausible budget.

**Merge-timing note, not a ruling.** Touching `python.yml` triggers the workflow on every
push/PR and is a live-infrastructure change, unlike the docs-only PR #539. F40
(`docs/audit/register.md`) records that concurrent gate runs sharing this repository's test
Postgres can poison each other when one is interrupted mid-run; the lead already owns merge
timing and PR #541's own executor already delivered clean, so this is noted for the lead's
awareness at merge, not a condition this ruling imposes.

## 4. All three of Ruling 59 §4's broken-input cases, re-confirmed under the amended mechanism

Ruling 59 §4 specifies these against a **synthetic fixture git repository**, never the live
one — that design choice is untouched by this amendment and is exactly why none of the three
needs to change:

- **Positive control** (genuine census, resolvable SHA, matching content) — unaffected by
  checkout depth; still passes. Under the amended mechanism it passes via local resolution
  alone in ordinary CI, never needing the fetch branch — a strictly more robust path than
  before, not a weaker one.
- **Mismatched content, resolvable SHA** — unaffected; the divergence is caught by the
  `csv_paths == tree_paths` comparison regardless of how `commit` was resolved.
- **Unresolvable SHA** — unaffected; a synthetic fixture naming a commit absent from its own
  fixture repository and unreachable by fetch still drives `resolve_commit` to `None` and
  `generated_from_tracked_corpus` to raise, exactly as today. **This is the case the amended
  live checkout makes unreachable in ordinary operation for the real registry entry** — with
  `fetch-depth: 0`, the real `docs/audit/file-census-5ef559d.csv` never exercises the
  fetch-then-hard-fail path in CI, because local resolution now always succeeds for it. The
  case still matters and is still required precisely because it protects every *other*
  checkout context §3 names (a developer's shallow local clone, a future regression of this
  setting) — it does not become dead code, it becomes the fallback's own test.

No case is weakened, relaxed, or made to treat "unresolvable" as "exempt" — the specific
failure mode this amendment was warned against reintroducing. `fetch-depth: 0` changes which
path the real artifact takes in ordinary CI; it does not touch what any of the three cases
asserts.

## 5. Spec amendment: not needed

Same finding as Ruling 59 §5, unchanged by this amendment: this is a CI/test-infrastructure
correction to an enforcement mechanism, not a reading of FR-DATA-32's text, which this record
does not revisit.

## 6. Where this amendment differs from the dispatch that requested it, if at all

None found. The dispatch's root-cause diagnosis (abbreviated SHA read as a ref name, never
reaching the object-fetch path) is independently reproduced verbatim in §1, its instruction
to verify option 1 against `github.com` before choosing it was followed and the verification
supports the diagnosis but not the choice, and its stated preference for removing the
dependency over repairing it is what §2 follows. The F40 caution is carried into §3 as a
note for the lead rather than a condition, since setting merge timing is outside this
role's charter either way.
