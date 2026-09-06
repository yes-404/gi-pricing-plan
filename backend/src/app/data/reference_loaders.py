"""Loaders for the common UK reference sets (FR-72, OQ-561).

> The platform ships **loaders** for … ONS postcode directory, ABI vehicle group tables,
> occupation/industry code lists, and a bank-holiday calendar. **Actual rows are shipped
> only where the licence is unambiguously permissive**; **ABI vehicle group tables are
> never shipped.**

A loader is a parser plus a documented fetch step, never bundled data — except where the
licence says otherwise. That distinction is a legal one, not a convenience one: bundling
ABI group tables would put a licence breach in every clone of this repository, and a
workspace that obtains them under its own licence is in a completely different position
from one that received them from us.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Final

__all__ = ["LOADERS", "Licence", "ReferenceLoader", "loader_for", "shippable_loaders"]


class Licence(enum.StrEnum):
    """Whether the data itself may travel with the platform."""

    #: Open Government Licence — ONS and gov.uk data. Rows may ship.
    OGL = "ogl"
    #: Licensed to the customer, not to us. Loader ships; rows never do.
    PROPRIETARY = "proprietary"
    #: Public but with terms we have not reviewed. Treated as proprietary until someone has.
    UNREVIEWED = "unreviewed"


@dataclass(frozen=True)
class ReferenceLoader:
    """How to obtain and parse one reference set."""

    slug: str
    description: str
    licence: Licence
    fetch_url: str
    fetch_note: str
    key_columns: tuple[str, ...]
    payload_columns: tuple[str, ...]

    @property
    def may_ship_data(self) -> bool:
        """OQ-561: rows travel only under an unambiguously permissive licence."""
        return self.licence is Licence.OGL


LOADERS: Final[dict[str, ReferenceLoader]] = {
    loader.slug: loader
    for loader in (
        ReferenceLoader(
            slug="ons-postcode-directory",
            description="ONS National Statistics Postcode Lookup — postcode to geography.",
            licence=Licence.OGL,
            fetch_url="https://geoportal.statistics.gov.uk/",
            fetch_note=(
                "Released quarterly. Pin the release in the Reference Table Version's "
                "source note: geography boundaries change between releases, and a policy "
                "rated on one release must stay reproducible against it."
            ),
            key_columns=("postcode",),
            payload_columns=("output_area", "lsoa", "local_authority", "region"),
        ),
        ReferenceLoader(
            slug="uk-bank-holidays",
            description="gov.uk bank-holiday calendar, used for working-day calculations.",
            licence=Licence.OGL,
            fetch_url="https://www.gov.uk/bank-holidays.json",
            fetch_note="Published as JSON per nation; small enough to ship.",
            key_columns=("date", "division"),
            payload_columns=("title", "bunting"),
        ),
        ReferenceLoader(
            slug="abi-vehicle-groups",
            description="ABI vehicle group ratings by ABI code.",
            # The reason this file exists. See OQ-561.
            licence=Licence.PROPRIETARY,
            fetch_url="https://www.thatcham.org/",
            fetch_note=(
                "NOT REDISTRIBUTABLE. The workspace must obtain this under its own licence "
                "and load it; the platform ships the parser only. Bundling these rows would "
                "put a licence breach in every clone of the repository (OQ-561)."
            ),
            key_columns=("abi_code",),
            payload_columns=("group_1_50", "group_1_20", "security_rating"),
        ),
        ReferenceLoader(
            slug="soc-occupation-codes",
            description="Standard Occupational Classification code list.",
            licence=Licence.OGL,
            fetch_url="https://www.ons.gov.uk/methodology/classificationsandstandards/",
            fetch_note="ONS publication; OGL, so the code list may ship.",
            key_columns=("soc_code",),
            payload_columns=("title", "major_group"),
        ),
    )
}


def loader_for(slug: str) -> ReferenceLoader:
    if slug not in LOADERS:
        raise KeyError(
            f"no loader for {slug!r}; shipped loaders are {sorted(LOADERS)} (FR-72)"
        )
    return LOADERS[slug]


def shippable_loaders() -> tuple[ReferenceLoader, ...]:
    """The sets whose rows may travel with the platform (OQ-561)."""
    return tuple(loader for loader in LOADERS.values() if loader.may_ship_data)
