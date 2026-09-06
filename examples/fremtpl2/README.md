---
family: reference
title: freMTPL2 — the demo seed
status: active                  # active → retired (§1.2a)
created: 2026-08-15
owner: lead
corrected_by: []
relates: []                      # ids only
---

# freMTPL2 — the demo seed

The data half of `07` FR-439, and Phase 1a's exit criterion made runnable.

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
uv run alembic upgrade head
uv run python examples/fremtpl2/fetch.py     # 36 MB, checksum-pinned, git-ignored
uv run python examples/fremtpl2/seed.py      # ~13 s for all 678 013 rows
uv run python examples/fremtpl2/seed.py --rows 50000   # a sample, mix preserved
```

## What it does

Two versions of one dataset, and **the failure in the middle is real**:

1. **v1 — the file as uploaded.** Renamed to the platform's vocabulary and cast, nothing
   else. Validation **fails**: 571 rows carry an exposure above 1.05, up to 2.01, which
   cannot be a year on risk for an annual policy (VR-ACT-2). Promotion is refused with
   `VALIDATION_HAS_FAILURES` — `01` §1.3 has no override.
2. **v2 — one preparation step later.** The recipe drops those rows. Validation passes
   with one warning: 125 claims at or above €35 630 are flagged for large-loss treatment
   and **not removed** (VR-ACT-10, and OQ-557 — capping is a modelling decision). An
   actuary acknowledges it with a justification, and the version reaches `validated`.

Afterwards a model may be fitted on `@2` and still may not on `@1`.

Nothing here is injected. freMTPL2 is a public dataset used in dozens of papers, and the
exposure anomaly is in the file as published.

## The data

[OpenML 41214 / 41215](https://www.openml.org/d/41214) — French motor third-party
liability, 678 013 policy-years and 26 639 claims, ARFF. Checksums are pinned in
`fetch.py`; the files are **not committed**, because 36 MB of third-party data does not
belong in a git history.

## Why it drives Jobs

Every step goes through `blob → Job → execute_job`, the path a worker takes in production.
A seed that called the services underneath would prove the shortcut works.

## What seeding it found

Real data behaves in ways synthetic fixtures do not. Five findings, all fixed or recorded:

| Finding | Where it landed |
|---|---|
| `allowed_values` read `values` where `01` §4.5 names the parameter `allowed` — so its domain was always empty and it **failed every row**, naming as offenders the values the author had allowed | Fixed: both names accepted, and an absent domain now skips |
| The whole-catalogue probe asserted no check *passes* vacuously, never that none *condemns* vacuously — so the above went unseen | Fixed: two tests, one per direction, and the second is proven against the real defect |
| **Seven of the eleven check names `01` §4.5 declares were unregistered** — a custom rule authored exactly as the spec documents produced `unknown_check`. `--catalogue VR` could not see it: that audits the built-in rule *ids*, this is the custom-rule *vocabulary* | Fixed: `regex`, `relationship`, `expression`, `aggregate`, `distribution_compare` implemented; `set_membership` and `uniqueness` aliased |
| `IDpol` normalises to `i_dpol`, not `idpol` — the splitter reads it as `I` + `Dpol`, the same rule that correctly gives `HTTPServer` → `http_server` | Not a defect. No mechanical splitter can know `ID` is the acronym; the original is kept in `source_names` (FR-30) and the recipe renames it |
| `ingest_upload` takes **one** table per version, while `01` §4.2's `tables[]` is plural and FR-38's `attach_claims` expects a separate claim table | Recorded. The seed joins the two files before upload, which is what an analyst does today; multi-table ingestion is a gap |

And one in the seed itself: `head(n)` for `--rows` sampled the first n rows of a
**claim-sorted** file, producing a frequency of 0.42 against the book's 0.05 and failing a
plausibility rule for reasons entirely the sampler's fault. It takes every nth row now.

## Measured, on real data

| | 678 013 rows | Extrapolated to 10 M | Budget |
|---|---|---|---|
| Ingest + prepare + profile (NFR-465, -3) | 2.9 s | 43 s | 900 s |
| Validation, 9 rules (NFR-466) | 0.3 s | 4.4 s | 600 s |
| The whole seed, both versions | 13.4 s | — | — |

Nine rules rather than the ~50 NFR-466 is written against, so the validation figure is
a floor. It replaces nothing in the WK-660 closure record; it corroborates it on data nobody
generated.

## Opening the frontend against the seeded workspace

The seed creates the workspace and its memberships, and the demo sign-in resolves to
them: the local provider's realm user *is* the seeded analyst (`FR-398`), so a real
login lands in the seeded workspace. Nothing needs to be exported — the dev proxy
injects no identity, the workspace travels as the verified `Workspace-Id` header (`07`
FR-397), and the selector in the app makes the choice.

The provider is the extra service behind the compose `auth` profile, and the API must be
pointed at it — `deploy/README.md` has both:

```bash
docker compose -f deploy/docker-compose.yml --profile auth up -d --wait
# then the GIP_OIDC_* exports from deploy/README.md, once per shell
uv run python examples/fremtpl2/seed.py     # prints the workspace and the demo users
GIP_DEV_AUTH_ENABLED=true uv run uvicorn app.main:create_app --factory --app-dir backend/src --port 8000
pnpm --dir frontend dev                     # http://localhost:5173/data
```

Sign in at the provider as **analyst** / **analyst**. The actuary has no realm user —
one demo login is what `FR-398` asks for. `scripts/demo.py` runs fetch, seed and both
servers with one command; it does not start the provider or set the OIDC variables, so
`--profile auth` and the exports belong to the manual flow above.
