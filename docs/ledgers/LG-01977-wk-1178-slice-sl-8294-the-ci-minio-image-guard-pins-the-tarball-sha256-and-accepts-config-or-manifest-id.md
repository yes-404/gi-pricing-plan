---
id: LG-1977
family: ledger
title: WK-1178 slice SL-1976 — the CI MinIO image guard pins the tarball sha256 and accepts the config or the manifest Id (hotfix ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-03               # drafted 2026-11-03 under working id 8295
owner: executor
tree: a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe   # origin/main at the branch cut
phase: P2
work: WK-1178
slice: SL-1976
plans: []
corrected_by: []
relates: [FD-1975, WK-1178]
---

# LG-1977 — WK-1178 slice SL-1976: the CI MinIO image guard (hotfix)

**GO:** to-lead "2026-11-03 15:56:18 GMT" — "Maintainer: MAIN RED on python.yml — GO for the hotfix, option (a) (FD 8293, SL 8294 / LG 8295, WK-1178)" (minted as FD-1975, SL-1976, LG-1977): (1) sha256 of the downloaded tarball checked against the release digest f68ed783… BEFORE `docker load`; (2) after load, the Id accepted if it equals EITHER the config Id 69b2ec20… OR the manifest digest a16cad48…, both derived in the comment, dated today, run 41664932828 named; (3) nothing else in python.yml changes; (4) enforcement proven on broken input locally, no throwaway commit; (5) green = the PR's own python run by id, minio stage plus the full suite. Option (b) refused.
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

A hotfix with no plan row (`plans: []`). Fixes FD-1975 in `.github/workflows/python.yml`, step `Start MinIO`, only. No requirement id is covered. No roadmap row until the mint.

### Task list

- [x] T1. Re-derive the digests from a fresh download (Build log).
- [x] T2. Red: the old step's script under a stub `docker`/`gh` (Gate).
- [x] T3. The fix, `python.yml` only (commit `8ecc9617`).
- [x] T4. Four local cases (Gate).
- [ ] T5. The PR's own `python.yml` run: the lead reads it by run id.

### Gate

Workflow-only change: CI is the gate (no pytest, no frontend). Harness: `~/gi-pricing-plan.local/scratch/cifix/` (`harness.py` extracts the `minio` step's `run:` script; `bin/` holds stub `gh` (copies the real tarball to the `-O` path, optionally appending one byte), stub `docker` (`image inspect` prints `$STUB_ID`) and stub `curl`; `run1.sh` runs one case in a fresh directory). Logs: `red.log`, `green.log` there (head= first line, rc= last).

**Red** — old step, `origin/main` `a8ef6f19`, Id = manifest digest:

```
::error::loaded minio/minio:latest has Id sha256:a16cad481969d7ddb6fcd2f1c58284af3d1266190b9bedc3ef0801aeb05a93a9, expected sha256:69b2ec208575b69597784255eec6fa6a2985ee9e1a47f4411a51f7f5fdd193a9
rc=1
```

CI reds: `python.yml` runs 41664932828, 41667830664, 41668093472.

**Cases** — new step, fix commit `8ecc961775a45024cd252c77c74ffab0c88b1716`:

| Case | Stub Id / tarball | Output | rc |
|---|---|---|---|
| (a) Id = manifest | `sha256:a16cad48…`, real tarball | passes the guard | 0 |
| (b) Id = config | `sha256:69b2ec20…`, real tarball | passes the guard | 0 |
| (c) planted wrong tarball | one byte appended | `::error::minio-image.tar.gz has sha256 42a02c55e3738c6800e19e3be82674f17222cff410bbbb4710ecebee85e37652, expected f68ed783300026c322889f4de2300647ab4056544798574f97a0390e35560476` | 1 |
| (d) planted third Id | `sha256:deadbeef` | `::error::loaded minio/minio:latest has Id sha256:deadbeef, expected sha256:69b2ec20… (config) or sha256:a16cad48… (manifest)` | 1 |

Other checks are in the Build log.

**Dated line, 2026-11-05 (docs batch 10), by the auditor, the gate of record:** CI was the gate (FD-1975 hotfix form). No gate ruling exists. The PR's python run (minio stage plus the full suite) was green per to-lead "2026-11-03 15:56:18 GMT"; the grant is "2026-11-03 16:26:15 GMT"; the ACK is "2026-11-03 16:58:06 GMT" (python 41674256256, docs 41674256251, history-policy 41674256228). No audit is recorded: SL-1976 stays a close-audit input. Authority: to-lead "2026-11-04 20:56:54 GMT" item 7 (f), stamps staged by lead 30 at 2026-11-04 20:59:03 GMT.**

### Audit

(Written by the auditor.)

### Build log

#### 2026-11-03 T1 — digests re-derived

Fresh `gh release download ci-images-2026-09-26 -p 'minio-*.tar.gz'` into an empty directory (read-only; no release was touched): `sha256sum` = `f68ed783300026c322889f4de2300647ab4056544798574f97a0390e35560476`. Extracted into a second empty directory; `python3 -I` read `index.json` → manifest `sha256:a16cad481969d7ddb6fcd2f1c58284af3d1266190b9bedc3ef0801aeb05a93a9` (its blob hashes to its name) → `config.digest` `sha256:69b2ec208575b69597784255eec6fa6a2985ee9e1a47f4411a51f7f5fdd193a9` (its blob hashes to its name). `manifest.json` `Config` names the same config blob.

#### 2026-11-03 T3 — the fix, commit `8ecc9617`

`python.yml` +20 −6: `sha256sum` check before `docker load`; two accepted Ids; the comment re-written and dated. `continue-on-error: true` and `id: minio` unchanged. `actionlint` is not installed (rc 1 from `which`); the YAML parses (`yaml.safe_load`, rc 0).

#### 2026-11-03 T5 — records

FD-1975 (draft for the auditor's sign-off, `owner: auditor`) and its register row. At the pre-commit tree on `8ecc9617`: `doc-index.py --check` rc 0 (`OK (byte-stable)`); `audit-docs.py` via `run-heavy.sh --light` rc 1 with exactly one failure, `check 31: gap in the full allocation between 1974 and 8293` (the working ids' own lint, expected until the mint); `register-lint` not run (not named in the brief).

## PRs

(None yet.)
