"""Derive the demo guide from the repository, at request time (FR-PLAT-54).

**Derived at request time rather than generated into a committed file.** A stored guide
would need a drift check to stay honest, and a drift check is a promise that someone will
run it; reading the four sources when the page is opened cannot go stale at all.

The four sources, each of which a reader can open and check:

| Section | Source | What it establishes |
|---|---|---|
| Views | each spec's §5.3 table | what the design says exists |
| — routed? | `frontend/src/router/index.ts` | what the frontend actually serves |
| API | `docs/contracts/openapi/generated.json` | the published surface (FR-PLAT-48) |
| Workstreams | `docs/roadmap.md` phase status tables | what is closed, in its own words |

Nothing here states a capability. Every "yes" is a file agreeing with another file, which
is the only kind of claim that cannot drift away from the repository — and the reason
FR-PLAT-54 requires the guide to be derived rather than written.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from model_schema import DemoApiGroup, DemoGuide, DemoView, DemoWorkstream

__all__ = ["GuideSourceMissingError", "build_guide", "repository_root"]

#: `docs/specs/01-data-management.md` → `DATA`. The spec file names carry the module.
_MODULES = {
    "00-overview": "OVR",
    "01-data-management": "DATA",
    "02-modelling": "MODEL",
    "03-rating-engine": "RATE",
    "04-optimisation": "OPT",
    "05-monitoring": "MON",
    "06-governance": "GOV",
    "07-platform": "PLAT",
}

_VIEWS_HEADING = re.compile(r"^### 5\.3 Frontend views\s*$")
_NEXT_HEADING = re.compile(r"^#{2,4} ")
_TABLE_ROW = re.compile(r"^\|(?!-)(.+)\|\s*$")
_ROUTE_IN_BACKTICKS = re.compile(r"`([^`]+)`")
_ROUTER_PATH = re.compile(r'path:\s*"([^"]+)"')
_STATUS_TABLE = re.compile(r"^#### (Phase [0-9a-z]+) status\s*$")


class GuideSourceMissingError(RuntimeError):
    """A source the guide is derived from is not present.

    Raised rather than returning a partial guide: a guide missing a section looks like a
    platform missing a capability, and the reader cannot tell the two apart.
    """


def repository_root() -> Path:
    """The checkout this package was imported from.

    `backend/src/app/demo/guide.py` → four levels up. Only ever correct in a checkout,
    which is the only place the demo entrance runs (FR-PLAT-53 gates it on
    `dev_auth_enabled`).
    """
    return Path(__file__).resolve().parents[4]


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _strip_markdown(text: str) -> str:
    """`**Validation report**` → `Validation report`."""
    return text.replace("**", "").replace("~~", "").strip()


def _spec_views(spec: Path) -> list[tuple[str, str, str]]:
    """The `| View | Route | Contents |` rows under §5.3, if the spec has any.

    `00` has a §5.3 that is the error model rather than a view table, which is why the
    heading is matched exactly instead of by number.
    """
    rows: list[tuple[str, str, str]] = []
    inside = False
    for line in spec.read_text(encoding="utf-8").splitlines():
        if _VIEWS_HEADING.match(line):
            inside = True
            continue
        if inside and _NEXT_HEADING.match(line):
            break
        if not inside:
            continue
        match = _TABLE_ROW.match(line)
        if not match:
            continue
        cells = _cells(line)
        if len(cells) < 3 or cells[0] == "View" or set(cells[0]) <= {"-", ":"}:
            continue
        route = _ROUTE_IN_BACKTICKS.search(cells[1])
        if route is None:
            continue
        rows.append((_strip_markdown(cells[0]), route.group(1), _strip_markdown(cells[2])))
    return rows


def _routed_paths(router: Path) -> set[str]:
    return set(_ROUTER_PATH.findall(router.read_text(encoding="utf-8")))


def _views(root: Path) -> tuple[DemoView, ...]:
    specs = root / "docs" / "specs"
    router = root / "frontend" / "src" / "router" / "index.ts"
    if not specs.is_dir():
        raise GuideSourceMissingError(f"No spec directory at {specs}.")
    if not router.is_file():
        raise GuideSourceMissingError(f"No frontend router at {router}.")

    routed = _routed_paths(router)
    views: list[DemoView] = []
    for spec in sorted(specs.glob("*.md")):
        module = _MODULES.get(spec.stem)
        if module is None:
            continue
        for name, route, contents in _spec_views(spec):
            views.append(
                DemoView(
                    spec=spec.stem,
                    module=module,
                    name=name,
                    route=route,
                    contents=contents,
                    implemented=route in routed,
                )
            )
    return tuple(views)


def _api(root: Path) -> tuple[DemoApiGroup, ...]:
    contract = root / "docs" / "contracts" / "openapi" / "generated.json"
    if not contract.is_file():
        raise GuideSourceMissingError(
            f"No published contract at {contract}. "
            "`uv run python scripts/generate-contracts.py` writes it."
        )
    document = json.loads(contract.read_text(encoding="utf-8"))
    grouped: dict[str, list[str]] = {}
    for path, operations in document.get("paths", {}).items():
        for method, operation in operations.items():
            if method.upper() not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            for tag in operation.get("tags") or ["untagged"]:
                grouped.setdefault(tag, []).append(f"{method.upper()} {path}")
    return tuple(
        DemoApiGroup(tag=tag, endpoints=tuple(sorted(set(endpoints))))
        for tag, endpoints in sorted(grouped.items())
    )


def _workstreams(root: Path) -> tuple[DemoWorkstream, ...]:
    roadmap = root / "docs" / "roadmap.md"
    if not roadmap.is_file():
        raise GuideSourceMissingError(f"No roadmap at {roadmap}.")

    rows: list[DemoWorkstream] = []
    phase: str | None = None
    for line in roadmap.read_text(encoding="utf-8").splitlines():
        heading = _STATUS_TABLE.match(line)
        if heading:
            phase = heading.group(1)
            continue
        if phase is None:
            continue
        if _NEXT_HEADING.match(line):
            phase = None
            continue
        if not _TABLE_ROW.match(line):
            continue
        cells = _cells(line)
        if len(cells) < 3 or cells[0] == "WS" or set(cells[0]) <= {"-", ":"}:
            continue
        status = _strip_markdown(cells[2])
        rows.append(
            DemoWorkstream(
                phase=phase,
                workstream=_strip_markdown(cells[0]).replace("✔", "").strip(),
                scope=_strip_markdown(cells[1]),
                # The roadmap's own word, not a re-judgement of it. A guide that decided
                # for itself whether a workstream was closed would be a second status
                # table, and the two would disagree.
                status=status,
                closed="closed" in status.lower(),
            )
        )
    return tuple(rows)


def build_guide(root: Path | None = None) -> DemoGuide:
    """Read the four sources and answer what is worth driving by hand."""
    root = root or repository_root()
    return DemoGuide(
        generated_from=(
            "docs/specs/*.md §5.3",
            "frontend/src/router/index.ts",
            "docs/contracts/openapi/generated.json",
            "docs/roadmap.md",
        ),
        views=_views(root),
        api=_api(root),
        workstreams=_workstreams(root),
    )
