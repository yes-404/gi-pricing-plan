#!/bin/bash
# Setup gipricing_template database for test suite.
#
# This script creates a fresh template database and runs migrations on it.
# The template is then used as a base for creating per-worktree test databases.
#
# Usage:
#   docker compose -f deploy/docker-compose.yml up -d postgres
#   ./deploy/setup-template-db.sh
#
# Or from inside the container:
#   docker exec gi-pricing-postgres-1 bash -c '
#     PGPASSWORD=gipricing createdb -U gipricing -T template0 gipricing_template
#     export GIP_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_template"
#     cd /app && uv run alembic upgrade head
#   '

set -e

CONTAINER="gi-pricing-postgres-1"
DB_NAME="gipricing_template"
DB_USER="gipricing"
DB_HOST="localhost"
DB_PORT="5432"

echo "Setting up $DB_NAME database..."

# Check if container is running
if ! docker exec "$CONTAINER" pg_isready -U "$DB_USER" > /dev/null 2>&1; then
    echo "Error: PostgreSQL container '$CONTAINER' is not running."
    echo "Start it with: docker compose -f deploy/docker-compose.yml up -d postgres"
    exit 1
fi

# Drop database if it exists (fresh template)
echo "Dropping existing $DB_NAME if present..."
docker exec "$CONTAINER" bash -c "PGPASSWORD=$DB_USER psql -U $DB_USER -tc \"DROP DATABASE IF EXISTS $DB_NAME;\" || true"

# Create fresh template database from template0
echo "Creating $DB_NAME database from template0..."
docker exec "$CONTAINER" bash -c "PGPASSWORD=$DB_USER createdb -U $DB_USER -T template0 $DB_NAME"

# Run migrations on the template database
echo "Running migrations on $DB_NAME..."
export GIP_DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
uv run alembic upgrade head

echo "✓ Template database $DB_NAME is ready for use"
