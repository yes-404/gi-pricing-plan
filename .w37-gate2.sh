#!/usr/bin/env bash
set -uo pipefail
export RUNTIME_STATE_FILE=/home/puzhenhao1989/gi-pricing-plan.local/handover/runtime-state.json
cd /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-abfcd60c8a355efed
WT=$(basename "$PWD")
SHA=$(git rev-parse HEAD)
LOG=/tmp/w37-6-pr-d1-scratch/gate2.log

python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py announce \
  --what full_test_suite --by exec-pr-d1 --tree "$SHA" --ttl-seconds 3600

{
echo "UPTIME BEFORE:"
uptime

flock -w 7200 /tmp/slots/gate-1 -c '
export GIP_GATE_SLOT=/tmp/slots/gate-1
export POLARS_MAX_THREADS=4 RAYON_NUM_THREADS=4 TOKIO_WORKER_THREADS=4 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
export GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_'"$WT"'

echo "--- ruff ---"
uv run ruff check . ; echo "ruff_EXIT=$?"

echo "--- mypy ---"
uv run mypy ; echo "mypy_EXIT=$?"

echo "--- lint-imports ---"
uv run lint-imports ; echo "lintimports_EXIT=$?"

echo "--- pytest ---"
uv run pytest -q ; echo "pytest_EXIT=$?"

echo "--- audit-docs ---"
python3 scripts/audit-docs.py ; echo "auditdocs_EXIT=$?"

echo "--- req-coverage ---"
uv run python scripts/req-coverage.py ; echo "reqcoverage_EXIT=$?"

echo "--- contracts (check only) ---"
uv run python scripts/generate-contracts.py --check ; echo "contracts_EXIT=$?"

echo "--- pnpm install ---"
pnpm --dir frontend install --frozen-lockfile ; echo "pnpminstall_EXIT=$?"

echo "--- pnpm generate:api ---"
pnpm --dir frontend generate:api ; echo "pnpmgenapi_EXIT=$?"

echo "--- pnpm lint ---"
pnpm --dir frontend lint ; echo "pnpmlint_EXIT=$?"

echo "--- pnpm type-check ---"
pnpm --dir frontend type-check ; echo "pnpmtypes_EXIT=$?"

echo "--- pnpm test ---"
pnpm --dir frontend test ; echo "pnpmtest_EXIT=$?"

echo "--- pnpm build ---"
pnpm --dir frontend build ; echo "pnpmbuild_EXIT=$?"
'

echo "UPTIME AFTER:"
uptime
echo "GATE_DONE"
} > "$LOG" 2>&1
