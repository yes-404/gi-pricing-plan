#!/usr/bin/env bash
set -uo pipefail

export RUNTIME_STATE_FILE=/home/puzhenhao1989/gi-pricing-plan.local/handover/runtime-state.json

mkdir -p /tmp/slots
WT=agent-ad0c6140e4c46f6cc
TREE=2bd3f37cb6564a2d411341a5dec4ff88e1d431a0
LOAD=$(awk '{print $1}' /proc/loadavg)
DFREE=$(df -h / | awk 'NR==2{print $4}')

flock -w 7200 /tmp/slots/w37-6-expensive bash -c '
  set -uo pipefail
  python3 "/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-ad0c6140e4c46f6cc/.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py" announce --what "full_test_suite load='"$LOAD"' df_root_free='"$DFREE"'" --by exec-pr-b --tree '"$TREE"' --ttl-seconds 3600
  echo "=== uptime before ==="
  uptime
  flock -w 7200 /tmp/slots/gate-1 bash -c "
    export GIP_GATE_SLOT=/tmp/slots/gate-1
    export POLARS_MAX_THREADS=4 RAYON_NUM_THREADS=4 TOKIO_WORKER_THREADS=4 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
    export GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_'"$WT"'
    echo \"--- ruff ---\"; uv run ruff check .; echo \"ruff_EXIT=\$?\"
    echo \"--- mypy ---\"; uv run mypy; echo \"mypy_EXIT=\$?\"
    echo \"--- lint-imports ---\"; uv run lint-imports; echo \"lintimports_EXIT=\$?\"
    echo \"--- pytest ---\"; uv run pytest -q; echo \"pytest_EXIT=\$?\"
    echo \"--- pytest --collect-only ---\"; uv run pytest --collect-only -q | tail -5; echo \"pytestcollect_EXIT=\$?\"
    echo \"--- audit-docs ---\"; python3 scripts/audit-docs.py; echo \"auditdocs_EXIT=\$?\"
    echo \"--- req-coverage ---\"; uv run python scripts/req-coverage.py; echo \"reqcoverage_EXIT=\$?\"
    echo \"--- contracts (check only) ---\"; uv run python scripts/generate-contracts.py --check; echo \"contracts_EXIT=\$?\"
    echo \"--- pnpm install ---\"; pnpm --dir frontend install --frozen-lockfile; echo \"pnpminstall_EXIT=\$?\"
    echo \"--- pnpm generate:api ---\"; pnpm --dir frontend generate:api; echo \"pnpmgenapi_EXIT=\$?\"
    echo \"--- pnpm lint ---\"; pnpm --dir frontend lint; echo \"pnpmlint_EXIT=\$?\"
    echo \"--- pnpm type-check ---\"; pnpm --dir frontend type-check; echo \"pnpmtypes_EXIT=\$?\"
    echo \"--- pnpm test ---\"; pnpm --dir frontend test; echo \"pnpmtest_EXIT=\$?\"
    echo \"--- pnpm build ---\"; pnpm --dir frontend build; echo \"pnpmbuild_EXIT=\$?\"
  "
  echo "GATE_EXIT=$?"
  echo "=== uptime after gate ==="
  uptime
  echo "--- doc-id.py migrate --verify (standing W37-6 CI docs step) ---"
  python3 /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-ad0c6140e4c46f6cc/scripts/doc-id.py migrate --verify /tmp/w37-6-pr-b-verify-2bd3f37 --ref HEAD > /tmp/w37-6-pr-b-gate.log2 2>&1
  echo "VERIFY_EXIT=$?" >> /tmp/w37-6-pr-b-gate.log2
  echo "=== uptime after verify ==="
  uptime
  echo "GATE_WRAPPER_DONE"
' > /tmp/w37-6-pr-b-gate.log 2>&1
