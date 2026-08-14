# Local stack

Brings up the services Phase 1a needs: PostgreSQL 16, Redis 7 and MinIO. No cloud
dependency (NFR-OVR-9).

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml down          # add -v to drop the volumes
```

`--wait` blocks until every healthcheck passes, so a green exit means the stack is
genuinely usable rather than merely started.

## Verified

**2026-08-14, Debian 13 / Docker 26.1.5 / Compose v5.4.0**

| Measure | Result | Requirement |
|---|---|---|
| Cold start, images pulled | **21 s** | NFR-PLAT-4: < 5 min |
| Warm start, images cached | **6 s** | — |
| Memory, all three services | **117 MB** | — |
| Disk, images + volumes | **~1 GB** | — |

Three specification assumptions were tested against the real services rather than assumed:

- **FR-DATA-29** — reference-table validity intervals must not overlap. A `btree_gist`
  exclusion constraint on `(slug =, key =, validity &&)` **rejected** the overlapping insert
  on PostgreSQL 16.15. The constraint the spec relies on is enforceable as written.
- **FR-OVR-7** — money exactness. `bigint` round-trips minor units exactly, and
  `numeric` addition is exact where binary float is not.
- **ID-4** — content-addressed blobs. Put and get round-tripped through MinIO's S3 API.

## Setup gotchas

Two things cost time on Debian 13 and are worth knowing:

- **`docker-compose-v2` is not a package name here.** Debian ships the legacy v1
  `docker-compose`, which does not understand this file's v2 syntax (the top-level `name:`
  key). Install the v2 plugin binary from the Docker releases instead.
- **A plugin in `~/.docker/cli-plugins` is invisible to `sudo docker`**, because root reads
  `/root/.docker`. Install it to `/usr/local/lib/docker/cli-plugins/` so both see it — or
  add your user to the `docker` group and drop `sudo` altogether (needs a new login).
