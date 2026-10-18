#!/usr/bin/env bash
# Health-gated roll of the `api` service to the image named by GIP_BUILD (NFR-531; SL-1258).
#
#   GIP_BUILD=<sha> deploy/roll-api.sh [-t <timeout-seconds>] <project> <compose-file>...
#
# Scales out beside the old replicas (`--no-recreate` leaves them running), waits until both new
# containers report healthy (by container id, bounded, failing loud), then stops and removes the
# old ones one at a time, ending at two replicas on the new image. A plain `up --scale api=2`
# recreates every replica at once, leaving none healthy until the new ones pass their healthcheck.
# It never pulls, builds or prunes, and touches no project but the one given.
set -euo pipefail

REPLICAS=2
timeout=180
if [[ ${1:-} == -t ]]; then
  timeout=${2:?-t needs a number of seconds}
  shift 2
fi
project=${1:?usage: GIP_BUILD=<sha> roll-api.sh [-t seconds] <project> <compose-file>...}
shift
[[ $# -ge 1 ]] || { echo "roll-api: no compose file given" >&2; exit 2; }
: "${GIP_BUILD:?roll-api: GIP_BUILD must name the commit of the new image}"

compose=(docker compose -p "$project")
for f in "$@"; do compose+=(-f "$f"); done
compose+=(--profile app)

api_ids() {
  docker ps -q --filter "label=com.docker.compose.project=$project" \
    --filter "label=com.docker.compose.service=api"
}
say() { echo "roll-api $(date -u +%H:%M:%S.%3N) $*"; }

mapfile -t old < <(api_ids)
say "old api containers: ${old[*]:-none}"

say "scaling out to $((REPLICAS * 2)) beside the old ones"
"${compose[@]}" up -d --no-deps --no-recreate --scale "api=$((REPLICAS * 2))" api >/dev/null

mapfile -t new < <(comm -13 <(printf '%s\n' "${old[@]}" | sort) <(api_ids | sort))
[[ ${#new[@]} -eq $REPLICAS ]] || { say "FAIL: expected $REPLICAS new api containers, got ${#new[@]}: ${new[*]:-none}"; exit 1; }
say "new api containers: ${new[*]}"

deadline=$((SECONDS + timeout))
for c in "${new[@]}"; do
  until [[ $(docker inspect --format '{{.State.Health.Status}}' "$c") == healthy ]]; do
    (( SECONDS < deadline )) || { say "FAIL: $c not healthy within ${timeout}s"; exit 1; }
    sleep 1
  done
done
say "new api containers healthy"

for c in "${old[@]}"; do
  docker stop "$c" >/dev/null
  say "stopped old $c"
  docker rm "$c" >/dev/null
  say "removed old $c"
done

mapfile -t final < <(api_ids)
[[ ${#final[@]} -eq $REPLICAS ]] || { say "FAIL: expected $REPLICAS api containers, got ${#final[@]}"; exit 1; }
for c in "${final[@]}"; do
  image=$(docker inspect --format '{{.Config.Image}}' "$c")
  [[ $image == "gi-pricing-app:$GIP_BUILD" ]] || { say "FAIL: $c runs $image, not gi-pricing-app:$GIP_BUILD"; exit 1; }
done
say "done: ${#final[@]} api containers on gi-pricing-app:$GIP_BUILD"
