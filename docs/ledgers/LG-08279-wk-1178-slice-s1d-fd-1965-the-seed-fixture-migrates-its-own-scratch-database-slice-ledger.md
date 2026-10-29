---
id: LG-8279
family: ledger
title: WK-1178 slice S1d — FD-1965, the seed fixture migrates its own scratch database, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-29
owner: executor
tree: 1e17ec6382de5919b6e3011242b584a59bb880e7   # origin/main at S1d's branch cut (#1407)
slice: SL-8278
phase: P2
work: WK-1178
plans: [PL-1927]
corrected_by: []
relates: [FD-1965, PL-1927, FR-31, FR-32]
---

# LG-8279 — WK-1178 slice S1d: FD-1965, the seed fixture migrates its own scratch database, red first

Working ids (space form in prose): **SL 8278** (this slice), **LG 8279** (this ledger). Executor seat
`exec-s1d`. Nothing is minted here.

**GO:** the lead's brief `brief-exec-s1d-2026-10-30.md`, pulled forward to Thu 2026-10-29 by to-lead
"2026-10-29 18:47:25 GMT"; authority PL-1927 row 6 (S1d), accepted at to-lead "2026-10-29 17:32:19 GMT".
**MERGE-ACK:** pending.

## Tasks

### Scope

PL-1927 "Delta, row 6 (S1d) — FD-1965: the seed fixture migrates its own scratch database (test-only,
red-first)" at `origin/main` `1e17ec63`: Tasks S1d-0 to S1d-7, Evidence E-d1 to E-d6, Acceptance d1 to
d10. The row is the scope; it is not restated here. Requirements: none amended (markers FR-31, FR-32
exist on the three tests). Write set: `examples/fremtpl2/test_seed.py`,
`backend/tests/test_transformations.py` (format only, its own commit), this ledger, the SL row,
FD-1965's close.

### Task list

- [x] **S1d-0. Base.** See the Build log, entry 1.
- [x] **S1d-1. The throwaway checkout.** See the Build log, entry 1.
- [ ] **S1d-2. Reds R1 to R3** (DB window).
- [ ] **S1d-3. The fix** (DP-S1d-1 (a)).
- [ ] **S1d-4. Control C1** and its mutation red.
- [ ] **S1d-5. Greens G1 and G2** (DB window).
- [ ] **S1d-6. The format commit, then the gate** (DP-S1d-2 G2 narrow cover).
- [ ] **S1d-7. Records.**

### Gate

Pending (S1d-6).

### Audit

Pending (the auditor's).

### Build log

1. **2026-10-29, Phase A (DB-free).** Base `origin/main` = `1e17ec6382de5919b6e3011242b584a59bb880e7`
   (merge 38, #1407), read by `git ls-remote origin refs/heads/main`.
   - S1d-0: `git diff --name-only 7ceff4a1..origin/main -- examples/ backend/migrations/` prints
     nothing (rc 0): E-d1 to E-d4 hold as the row states (read at the base: `env.py:31–38`,
     `test_seed.py` `scratch_seed`, `seed.py:448–466`).
   - E-d6 format check at the base, `head=1e17ec63`: `git show origin/main:backend/tests/test_transformations.py
     | uv run ruff format --check --stdin-filename backend/tests/test_transformations.py -` rc=1, so
     S1d-6's format commit is owed.
   - S1d-1: throwaway detached worktree of the base at `~/gi-pricing-plan.local/scratch/s1d/tw`
     (outside the slice worktree), `uv sync --all-packages --frozen` rc=0; the two `.arff` copied into
     **its** `examples/fremtpl2/data/` only, sha256 equal to the pins in `fetch.py`.

## PRs

None yet (the lead opens the PR).
