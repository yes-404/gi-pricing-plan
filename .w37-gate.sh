#!/usr/bin/env bash
cd /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-abaa2a147ef67a50b || exit 99

export RUNTIME_STATE_FILE=/home/puzhenhao1989/gi-pricing-plan.local/handover/runtime-state.json
WT=agent-abaa2a147ef67a50b
mkdir -p /tmp/slots

python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py announce \
  --what full_test_suite --by pr-c-executor --tree "$(git rev-parse HEAD)" --ttl-seconds 3600

echo "=== uptime before ==="
uptime

gate_body='POLARS_MAX_THREADS=4 RAYON_NUM_THREADS=4 TOKIO_WORKER_THREADS=4 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_'"$WT"' uv run ruff check . && uv run mypy && uv run lint-imports && POLARS_MAX_THREADS=4 RAYON_NUM_THREADS=4 TOKIO_WORKER_THREADS=4 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_'"$WT"' uv run pytest -q'

flock -w 7200 /tmp/slots/gate-1 -c "export GIP_GATE_SLOT=/tmp/slots/gate-1; $gate_body"
py_exit=$?

echo "=== uptime after ==="
uptime
echo "PY_HALF_EXIT=$py_exit"

python3 scripts/audit-docs.py
echo "AUDIT_DOCS_EXIT=$?"
uv run python scripts/req-coverage.py
echo "REQ_COVERAGE_EXIT=$?"
uv run python scripts/generate-contracts.py --check
echo "CONTRACTS_CHECK_EXIT=$?"

exit $py_exit
