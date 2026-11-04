"""Every published compose port is bound to the loopback interface (PL-1769 Step 1.5).

`deploy/docker-compose.yml` is a dev/demo stack: a bare `"5432:5432"` publishes the
superuser-owned Postgres (and redis, minio, keycloak, the load balancer) on every host
interface. The maintainer's entry "2026-10-25 11:53:23 GMT" rules all six entries bound to
`127.0.0.1`, the load balancer's included. The cases are derived from the file, so a service
added later with a bare port fails here without this test being edited.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

_COMPOSE = Path(__file__).resolve().parents[2] / "deploy" / "docker-compose.yml"


def _published() -> list[tuple[str, str]]:
    services: dict[str, Any] = yaml.safe_load(_COMPOSE.read_text(encoding="utf-8"))["services"]
    return [(name, str(entry)) for name, svc in services.items() for entry in svc.get("ports", [])]


@pytest.mark.req("FR-44")
def test_compose_publishes_ports() -> None:
    # a parametrised test over an empty list passes by not running
    assert len(_published()) >= 6


@pytest.mark.req("FR-44")
@pytest.mark.parametrize(("service", "entry"), _published(), ids=lambda v: v)
def test_published_port_is_loopback_only(service: str, entry: str) -> None:
    # `${GIP_LB_PORT:-8000}:8000` becomes `127.0.0.1:${GIP_LB_PORT:-8000}:8000`
    assert entry.startswith("127.0.0.1:"), f"{service} publishes {entry!r} on every interface"
