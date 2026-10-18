# One image, three roles (NFR-535, 07 §3.9): the role is the command, not the image.
#   api      uvicorn app.main:app           (scoring and management API)
#   worker   celery -A app.worker.entrypoint worker
#   migrate  alembic upgrade head           (FR-435: its own pre-deploy step, never `api` start)
#
# Build from the repository root:
#   docker build -f deploy/Dockerfile --build-arg GIP_BUILD=$(git rev-parse HEAD) .
# GIP_BUILD must be the full 40-hex commit SHA: `Settings.require_startable` refuses any other
# value outside `local` (FR-18), so an image cannot be built that records no platform version.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.4 /uv /bin/uv

ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first, so a source-only change reuses the cached layer. `--all-packages` is not
# optional in this workspace (`.claude/skills/dev-commands`).
COPY pyproject.toml uv.lock ./
COPY packages/model-schema/pyproject.toml packages/model-schema/pyproject.toml
COPY packages/pricing-core/pyproject.toml packages/pricing-core/pyproject.toml
COPY backend/pyproject.toml backend/pyproject.toml
RUN uv sync --frozen --all-packages --no-dev --no-install-workspace

COPY packages packages
COPY backend backend
COPY alembic.ini ./
RUN uv sync --frozen --all-packages --no-dev

ARG GIP_BUILD
RUN test -n "$GIP_BUILD" && echo "$GIP_BUILD" | grep -Eq '^[0-9a-f]{40}$' \
    || (echo "GIP_BUILD must be the full 40-hex commit SHA (FR-18)" >&2; exit 1)
ENV GIP_BUILD=$GIP_BUILD \
    PATH="/app/.venv/bin:$PATH"

RUN useradd --system --uid 10001 gip
USER gip

EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
