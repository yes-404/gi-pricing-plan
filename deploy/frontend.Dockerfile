# The built SPA behind the stack's one static server (FR-432, PL-1688 Task 2).
#   build stage   node + pnpm: install (frozen), generate the API types from the committed
#                 OpenAPI contract, build. Nothing generated is copied in from a developer's tree
#                 (CLAUDE.md §3: no hand-written API type).
#   serve stage   the same nginx image `lb` uses, so the stack gains no second server image.
#
# Build from the repository root (the context needs `frontend/` and
# `docs/contracts/openapi/generated.json`; `deploy/frontend.Dockerfile.dockerignore` admits only
# those, so the backend image's `.dockerignore` is not widened):
#   docker build -f deploy/frontend.Dockerfile -t gi-pricing-frontend:local .
# BuildKit reads the Dockerfile-specific ignore file in place of the root `.dockerignore`.
FROM node:22-alpine AS build

# frontend/package.json "packageManager": "pnpm@11.21.0"
RUN corepack enable && corepack prepare pnpm@11.21.0 --activate

WORKDIR /repo
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml frontend/
RUN pnpm --dir frontend install --frozen-lockfile

COPY frontend frontend
COPY docs/contracts/openapi/generated.json docs/contracts/openapi/generated.json
RUN pnpm --dir frontend generate:api && pnpm --dir frontend build

FROM nginx:1.27-alpine
COPY deploy/frontend.nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /repo/frontend/dist /usr/share/nginx/html
EXPOSE 80
