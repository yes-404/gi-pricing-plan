---
id: FD-1975
family: finding
title: the Start MinIO guard pins the image config Id, which the containerd store reports as the manifest digest, so every python.yml run fails
status: closed
created: 2026-11-03               # drafted 2026-11-03 under working id 8293
owner: auditor                  # DRAFT by the executor for the auditor's sign-off at the slice audit (document-ids §1.6)
tree: a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe   # origin/main when read
corrected_by: []
relates: [WK-1178, SL-1976, LG-1977]
---

# FD-1975 — the Start MinIO guard pins the image config Id, which the containerd store reports as the manifest digest, so every python.yml run fails

## Finding

**HIGH, owner WK-1178; blocks work today** (`CLAUDE.md` §13's FD test). Authority: the maintainer's
"2026-11-03 15:56:18 GMT" entry (GO, option (a)). Drafted by the executor under working id 8293 for the
auditor's sign-off. No mispricing and no data loss: the failure is in CI, but it makes `python.yml` red on
`main` and on every `docs/` or `backend/` PR, so nothing merges on a green gate.

`.github/workflows/python.yml`, step `Start MinIO` (`id: minio`), at `a8ef6f19` (lines 247-276), restores the
release asset `ci-images-2026-09-26` / `minio-*.tar.gz`, runs `docker load`, then requires
`docker image inspect minio/minio:latest --format '{{.Id}}'` to equal the image **config** digest
`sha256:69b2ec208575b69597784255eec6fa6a2985ee9e1a47f4411a51f7f5fdd193a9`. On the runner image
`ubuntu-26.04` (20261025.179.1) Docker uses the containerd image store and reports `.Id` as the
**manifest** digest `sha256:a16cad481969d7ddb6fcd2f1c58284af3d1266190b9bedc3ef0801aeb05a93a9`. The guard was
pinned to a store-dependent identifier.

## Evidence

- Failing runs of `python.yml`, stage `minio`: `41664932828` (push to `main`, merge 43), `41667830664`,
  `41668093472` (#1414). The three earlier `main` runs (d549b8d2, 9c00b9f7, aad4fd58) succeeded on 29 Oct.
- The asset is unchanged. Re-derived by the executor from a fresh download in an empty directory
  (`~/gi-pricing-plan.local/scratch/cifix/dl`, extracted under `.../x`): tarball
  `sha256sum` = `f68ed783300026c322889f4de2300647ab4056544798574f97a0390e35560476`; its `index.json`
  names manifest `sha256:a16cad48…`; that manifest's `config.digest` is `sha256:69b2ec20…`; each blob's
  sha256 equals its file name (`python3 -I`, `hashlib`).
- Local red with the step's script under a stub `docker`/`gh` (LG-1977 Gate section): the old guard prints
  `::error::loaded minio/minio:latest has Id sha256:a16cad48…, expected sha256:69b2ec20…` and exits 1.

## Disposition

Open, owner WK-1178, HIGH, `fix before close with an owner`: SL-1976 discharges it (see Fix). Filed under working id 8293.

## Fix

SL-1976, `python.yml` only: check the tarball sha256 before `docker load`; accept the loaded Id if it equals
either derived digest; otherwise fail naming all three. Discharged when that slice merges and its own
`python.yml` run is green on the minio stage and the full suite.


***Resolved 2026-11-03*** — closed in place 2026-11-03 by the auditor, on the maintainer's entry "2026-11-03 17:29:18 GMT" (`to-lead.md`, a local channel file): fixed by SL-1976 (WK-1178, LG-1977), PR #1417, squash `5a9e47c5d72bb9e7e03438b93fbf269c8015322c` (merge 45). Close evidence: main's push `python` run **41679694232** at `5a9e47c5` completed `success` (job `ruff · mypy · import-linter · pytest` success; re-read by the auditor with `gh run view 41679694232 --json conclusion,headSha`: `success`, `5a9e47c5d72bb9e7e03438b93fbf269c8015322c`), the first green on `main` since 15:32 GMT; the red window ran 15:32 to 17:29 GMT (merge 43 to merge 45). The fix at `55bddaf2`: `.github/workflows/python.yml` `Start MinIO` checks the tarball sha256 `f68ed783…` (:257-258) before `docker load` and accepts the loaded Id if it equals either the config digest `69b2ec20…` or the manifest digest `a16cad48…` (:277-278). *Auditor's sign-off (front matter `owner: auditor`): the essay's finding, evidence and fix are confirmed against `python.yml` at `55bddaf2` and the run above; the asset's digests were re-derived by the executor and are not re-derived here. Date of record: 2026-11-03 — #1417, squash 5a9e47c5.*
