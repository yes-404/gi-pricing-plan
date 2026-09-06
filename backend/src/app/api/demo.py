"""The demo entrance's guide (FR-408, FR-409).

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/demo/guide` | What is worth driving by hand, derived from the repository |

**Present only when `dev_auth_enabled` is true**, which `07` §3.8 makes `False` by default
and which *refuses to start* in a deployed environment. There is no second switch, because
a second switch is one more thing that can be left on: a page listing every route next to a
pre-authenticated session is a genuine hole if it ever ships.

The route is registered unconditionally and answers 404 when the flag is off — rather than
being left out of the router — so the contract describes one API rather than two, and the
refusal is a tested behaviour instead of an absence nobody can test.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.deps import Caller, require_caller
from app.api.responses import problems
from app.config import Settings
from app.demo.guide import GuideSourceMissingError, build_guide
from app.errors import PlatformError
from model_schema import DemoGuide

__all__ = ["router"]

def demo_enabled(request: Request) -> None:
    """Refuse the whole surface where development identity is not enabled.

    A **router-level** dependency, so it is solved before the caller is: with the flag off
    the answer is 404 whatever credential is presented, because the surface does not exist
    there. Checked inside the handler instead, an anonymous request would get 401 first —
    and 401 says "authenticate and try again", which is the opposite of what is true.
    """
    settings: Settings = request.app.state.settings
    if not settings.dev_auth_enabled:
        raise PlatformError(
            "NOT_FOUND",
            "The demo entrance is not enabled",
            404,
            "The demo entrance exists only where development identity does "
            "(FR-408), and `dev_auth_enabled` is false here.",
        )


router = APIRouter(prefix="/demo", tags=["demo"], dependencies=[Depends(demo_enabled)])

AnyCaller = Annotated[Caller, Depends(require_caller)]


@router.get(
    "/guide",
    summary="What is testable today, derived from the repository (FR-409)",
    responses=problems(401, 403, 404),
)
async def get_guide(caller: AnyCaller) -> DemoGuide:
    """Derived on every request from the specs, the router, the contract and the roadmap.

    Never stored: a stored guide needs a drift check to stay honest, and a drift check is a
    promise that somebody will run it. The guide's purpose is telling a person what to
    trust, so it must not be capable of being wrong.
    """
    try:
        return build_guide()
    except GuideSourceMissingError as exc:
        # A partial guide would look like a platform missing a capability, and the reader
        # could not tell the two apart.
        raise PlatformError(
            "NOT_FOUND",
            "The guide cannot be derived here",
            404,
            f"{exc} The demo entrance reads the checkout it runs from.",
        ) from exc
