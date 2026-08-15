"""The demo entrance's guide (FR-PLAT-53, FR-PLAT-54).

**Every field here is derived** — from the published contract, the specs' §5.3 view tables,
the frontend router, and the roadmap's status table. Nothing in this module is a place to
write down what the platform can do: a hand-written capability list goes stale the week it
is written, and the guide's whole purpose is telling a person what to trust.

That is why `implemented` is a fact about the router rather than a field someone sets, and
why `not_functional` is derived from the same comparison rather than maintained beside it.
A guide that could disagree with the repository would be worse than no guide, because it
would be believed.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "DemoApiGroup",
    "DemoGuide",
    "DemoView",
    "DemoWorkstream",
]


class DemoView(BaseModel):
    """One view a spec's §5.3 declares, and whether the frontend actually routes it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    spec: str = Field(description="The spec that declares it, e.g. `01-data-management`.")
    module: str = Field(description="Its requirement prefix, e.g. `DATA`.")
    name: str
    route: str
    contents: str
    implemented: bool = Field(
        description="The route pattern appears in the frontend router. A fact, not a claim."
    )


class DemoApiGroup(BaseModel):
    """Published endpoints under one OpenAPI tag, from `docs/contracts/` (FR-PLAT-48)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tag: str
    endpoints: tuple[str, ...] = ()


class DemoWorkstream(BaseModel):
    """A row of the roadmap's phase status table, as written there."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    phase: str
    workstream: str
    scope: str
    status: str
    closed: bool


class DemoGuide(BaseModel):
    """What is worth driving by hand today, and — the half that matters — what is not."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    generated_from: tuple[str, ...] = Field(
        default=(),
        description="The files this was derived from. Named so a reader can check it.",
    )
    views: tuple[DemoView, ...] = ()
    api: tuple[DemoApiGroup, ...] = ()
    workstreams: tuple[DemoWorkstream, ...] = ()

    @property
    def implemented_views(self) -> tuple[DemoView, ...]:
        return tuple(view for view in self.views if view.implemented)

    @property
    def not_functional(self) -> tuple[DemoView, ...]:
        """Declared in a spec, not routed by the frontend.

        The valuable half. A demo that showed only what works invites the reader to assume
        everything else works too.
        """
        return tuple(view for view in self.views if not view.implemented)
