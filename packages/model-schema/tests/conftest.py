from datetime import UTC, datetime
from uuid import uuid4

import pytest


@pytest.fixture
def envelope_kwargs():
    return {
        "id": uuid4(),
        "workspace_id": uuid4(),
        "slug": "motor-gb",
        "version": 1,
        "status": "draft",
        "created_at": datetime.now(UTC),
        "created_by": uuid4(),
    }
