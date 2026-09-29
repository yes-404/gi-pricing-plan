#!/usr/bin/env bash
# Create, or check, the clean test-database template `gipricing_template`.
#
#   deploy/setup-template-db.sh           drop and recreate it: empty, at alembic head
#   deploy/setup-template-db.sh --check   read-only: fail unless it is empty and at head
#
# Every per-worktree test database is made with `createdb -T gipricing_template`
# (`.claude/skills/dev-commands/SKILL.md`), so a template that holds rows, or sits behind
# head, hands every tree a database that fails by collision (FD-1218). The shared
# `gipricing` database is the compose/CI database and is never touched here.
#
# `docker exec` and no host client: this box has no `createdb`/`psql` on the host.
# `set -e` with no `|| true` anywhere: a failed DROP must stop the script, not be
# followed by a `createdb` that reports the name is taken.
set -euo pipefail

CONTAINER="${GIP_PG_CONTAINER:-gi-pricing-postgres-1}"
DB_USER="gipricing"
TEMPLATE="gipricing_template"

psql_in() { docker exec -e PGPASSWORD="$DB_USER" "$CONTAINER" psql -U "$DB_USER" -v ON_ERROR_STOP=1 -qtA "$@"; }

check() {
    local rows head_rev db_rev
    rows=$(psql_in -d "$TEMPLATE" -c "
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
          AND table_name <> 'alembic_version'
          AND (xpath('/row/c/text()', query_to_xml(
                format('SELECT count(*) AS c FROM %I.%I', table_schema, table_name),
                false, true, '')))[1]::text::int > 0
        ORDER BY table_name;")
    if [ -n "$rows" ]; then
        echo "FAIL: $TEMPLATE holds rows in: $(echo "$rows" | tr '\n' ' ')" >&2
        return 1
    fi
    db_rev=$(psql_in -d "$TEMPLATE" -c "SELECT version_num FROM alembic_version;")
    head_rev=$(GIP_DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_USER@localhost:5432/$TEMPLATE" \
        uv run alembic heads | awk '{print $1}')
    if [ -z "$head_rev" ] || [ "$(echo "$head_rev" | wc -l)" -ne 1 ]; then
        echo "FAIL: expected exactly one alembic head, got: '$head_rev'" >&2
        return 1
    fi
    if [ "$db_rev" != "$head_rev" ]; then
        echo "FAIL: $TEMPLATE is at $db_rev, the migration head is $head_rev" >&2
        return 1
    fi
    echo "OK: $TEMPLATE is empty and at alembic head $head_rev"
}

if [ "${1:-}" = "--check" ]; then
    check
    exit
fi

docker exec "$CONTAINER" pg_isready -U "$DB_USER" >/dev/null
psql_in -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity
    WHERE datname = '$TEMPLATE' AND pid <> pg_backend_pid();" >/dev/null
docker exec -e PGPASSWORD="$DB_USER" "$CONTAINER" dropdb -U "$DB_USER" --if-exists "$TEMPLATE"
docker exec -e PGPASSWORD="$DB_USER" "$CONTAINER" createdb -U "$DB_USER" -T template0 "$TEMPLATE"
GIP_DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_USER@localhost:5432/$TEMPLATE" \
    uv run alembic upgrade head
check
