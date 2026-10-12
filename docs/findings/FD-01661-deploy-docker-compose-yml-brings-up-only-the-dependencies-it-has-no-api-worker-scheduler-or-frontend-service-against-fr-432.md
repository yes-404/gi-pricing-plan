---
id: FD-1661
family: finding
title: deploy/docker-compose.yml brings up only the dependencies: it has no api, worker, scheduler or frontend service, against FR-432
status: active
created: 2026-10-12
owner: auditor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
corrected_by: []
relates: [WK-674, FR-432, FR-413, SL-1527, LG-1647]
---

# FD-1661 — the compose stack does not run the platform

*(Minted 2026-10-12 as FD-1661 from working id 9860, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Raised as a D13 owed addition: the lead's eta entry "2026-10-11 23:26:41 BST" (a local file) records *"D13 OWED ADD: FD (compose gap: deploy/docker-compose.yml has no Celery worker/beat service vs 07 FR-432) — owner WK-674, severity from the auditor"*, from the maintainer's entry "2026-10-11 23:25:46 BST" (`to-lead.md`). Every line was re-read at `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9` on 2026-10-12. **The gap is wider than the entry says.**

## Evidence

- `07-platform.md` FR-432: *"The platform ships as container images: `api`, `worker`, `scheduler` (the beat tick, FR-413), `frontend`, plus dependencies (PostgreSQL, Redis, MinIO, an OIDC provider for local use). `deploy/docker-compose.yml` brings up a working stack with seeded demo data (R2)."*
- `deploy/docker-compose.yml` at `fc4401dc` defines four services, all dependencies: `postgres` (`:10`), `redis` (`:24`), `minio` (`:36`), `keycloak` (`:60`). `git grep -n -i celery -- deploy` prints nothing. There is no `api`, no `worker`, no `scheduler` (the Celery beat tick) and no `frontend`, and `deploy/` holds no Dockerfile.
- The file's own header (`:1-5`) says the omission was deliberate for Phase 1a: *"Services arrive as the workstreams that use them do — an unused container in the compose file is a claim the platform does not yet support."* The platform now has a Celery worker and Jobs, and the header has not moved.

## Finding

**Severity MEDIUM (proposed by the executor; ruled by the lead, "2026-10-12 02:57:36 BST").** FR-432 is a stated requirement and its "working stack" clause is false today. Nothing is mispriced. But without a `worker` no 202 Job ever completes in a compose stack, and without `scheduler` no periodic tick runs. The platform's HTTP surface, the journey and the exit demo run from the repository's own scripts, not from compose, which is why this is not on the G2 path and is not HIGH.

## Disposition

**Owner: WK-674 (platform and deployment).** Fix before close, or accept at the P2 close with a dated line: add `api`, `worker`, `scheduler` and `frontend` services (and the image build they need), or amend FR-432 and the compose header to say which Phase ships them. Placement, ruled by the maintainer (by delegation), entry "2026-10-12 02:53:52 BST" (`to-lead.md`), option (ii), and the lead's "2026-10-12 02:57:36 BST" (severity MEDIUM, owner WK-674):  on SL-1258's branch, Slice 4 (WK-674) adds `api`, `worker` and `lb` under the `app` profile, but **not** `scheduler`/beat or `frontend`; the beat gets its own row after Slice 4, serialised on `deploy/docker-compose.yml`. **FR-432 has three unmet limbs** (the maintainer's (by delegation) entry "2026-10-12 03:08:30 BST" item 2, `to-lead.md`; `07-platform.md` FR-432): (1) the `worker` (SL-1258, WK-674 Slice 4, with `api` and `lb` under the `app` profile); (2) the `scheduler`/beat, its own row after Slice 4, serialised on compose; (3) the `frontend` image, a third row, where whether it is Phase 2 or carried is a decision point in WK-674's plan. **FR-432 and this finding stay open until all three merge.** The `api` and `frontend` services are the owner's to place; if the spec moves, that is the decision-maker's. Event that next confirms or discharges it: a merged change after which `docker compose -f deploy/docker-compose.yml config --services` prints the FR-432 services, or a dated ruling moving FR-432. Filed by the executor, 2026-10-12.
