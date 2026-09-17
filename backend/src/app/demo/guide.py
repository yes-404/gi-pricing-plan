"""Derive the demo guide from the repository, at request time (FR-409).

**Derived at request time rather than generated into a committed file.** A stored guide
would need a drift check to stay honest, and a drift check is a promise that someone will
run it; reading the four sources when the page is opened cannot go stale at all.

The four sources, each of which a reader can open and check:

| Section | Source | What it establishes |
|---|---|---|
| Views | each spec's §5.3 table | what the design says exists |
| — routed? | `frontend/src/router/index.ts` | what the frontend actually serves |
| API | `docs/contracts/openapi/generated.json` | the published surface (FR-451) |
| Workstreams | `docs/roadmap.md` phase status tables | what is closed, in its own words |

Nothing here states a capability. Every "yes" is a file agreeing with another file, which
is the only kind of claim that cannot drift away from the repository — and the reason
FR-409 requires the guide to be derived rather than written.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from model_schema import (
    DemoApiGroup,
    DemoEndpoint,
    DemoGuide,
    DemoView,
    DemoWorkstream,
)

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
#: The roadmap heads Phase 1a/1b at `###` and Phases 2 to 4 at `## 7.`-style numbered
#: headings. Matching only one form would have reported "every phase has a status table"
#: by seeing two phases out of five.
_PHASE_HEADING = re.compile(r"^#{2,3} (?:\d+\. )?(Phase [0-9a-z]+) — (.+?)\s*$")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
#: `| `GET`/`PUT` | `/api/v1/datasets` | … |` — a spec's §5.1 interface table. Duplicated
#: from `scripts/scope-audit.py` rather than shared: that is a script and this is the
#: application, and neither may import the other. Two readers of one table is a smell; a
#: backend importing from `scripts/` would be worse.
_SPEC_ENDPOINT = re.compile(r"^\|\s*`?([A-Z]+(?:`?/`?[A-Z]+)*)`?\s*\|([^|]+)\|")
_PATH_IN_CELL = re.compile(r"`([^`]+)`")


class GuideSourceMissingError(RuntimeError):
    """A source the guide is derived from is not present.

    Raised rather than returning a partial guide: a guide missing a section looks like a
    platform missing a capability, and the reader cannot tell the two apart.
    """


def repository_root() -> Path:
    """The checkout this package was imported from.

    `backend/src/app/demo/guide.py` → four levels up. Only ever correct in a checkout,
    which is the only place the demo entrance runs (FR-408 gates it on
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
    """Route paths the router actually declares.

    Comments are stripped first. A `// TODO: { path: "/jobs" }` matched the bare regex and
    rendered a green "built" badge for a view nobody had started — on the page whose only
    job is saying what is worth clicking.
    """
    text = _BLOCK_COMMENT.sub("", router.read_text(encoding="utf-8"))
    lines = [line for line in text.splitlines() if not line.lstrip().startswith("//")]
    return set(_ROUTER_PATH.findall("\n".join(lines)))


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
                    # A spec route cell carries the query the view reads — `?version=`,
                    # `?ids=` — and a router path never does. Comparing the two raw rendered a
                    # red "built" badge for two views that are built and routed: the same defect
                    # as the `// TODO` green badge above, in the other direction, on the page
                    # whose only job is saying what is worth clicking.
                    implemented=route.split("?")[0] in routed,
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


def _normalise_path(path: str) -> str:
    """`/datasets/{slug}` and `/datasets/{dataset_slug}` are one endpoint."""
    return re.sub(r"\{[^}]*\}", "{}", path.split("?")[0].rstrip("/"))


def _unpublished(root: Path) -> tuple[DemoEndpoint, ...]:
    """Endpoints a spec's §5.1 table declares that the published contract does not carry.

    FR-409's "what is present but **not** yet functional" applied to the API. Without
    it the page reported "63 endpoints published" and stopped — true, and silent about the
    105 declared endpoints that do not exist, which is the half a reader is asking about.
    """
    contract = root / "docs" / "contracts" / "openapi" / "generated.json"
    specs = root / "docs" / "specs"
    if not contract.is_file() or not specs.is_dir():
        raise GuideSourceMissingError(f"No contract at {contract} or no specs at {specs}.")

    document = json.loads(contract.read_text(encoding="utf-8"))
    published = {
        (method.upper(), _normalise_path(path))
        for path, operations in document.get("paths", {}).items()
        for method in operations
        if method.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE"}
    }

    missing: list[DemoEndpoint] = []
    for spec in sorted(specs.glob("*.md")):
        module = _MODULES.get(spec.stem)
        if module is None:
            continue
        for line in spec.read_text(encoding="utf-8").splitlines():
            match = _SPEC_ENDPOINT.match(line)
            if not match:
                continue
            for path in _PATH_IN_CELL.findall(match.group(2)):
                if not path.startswith("/"):
                    continue
                for method in re.split(r"`?/`?", match.group(1)):
                    key = (method.strip("`"), _normalise_path(path))
                    if key not in published:
                        missing.append(
                            DemoEndpoint(module=module, method=key[0], path=key[1])
                        )
    return tuple(sorted(set(missing), key=lambda e: (e.module, e.path, e.method)))


def _phases_without_status(root: Path) -> tuple[str, ...]:
    """Phases the roadmap names but does not yet give a status table.

    Stated so the workstream section cannot be read as covering the project: it covered
    Phase 1a alone while the page reported "7/7 closed".
    """
    text = (root / "docs" / "roadmap.md").read_text(encoding="utf-8")
    named = {m.group(1) for line in text.splitlines() if (m := _PHASE_HEADING.match(line))}
    with_status = {m.group(1) for line in text.splitlines() if (m := _STATUS_TABLE.match(line))}
    # "Phase 1" is the umbrella over 1a and 1b and has no status of its own; listing it
    # beside them would report the same work twice under a name nothing tracks.
    umbrellas = {name for name in named if any(o != name and o.startswith(name) for o in named)}
    return tuple(sorted(named - with_status - umbrellas))


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
        unpublished_endpoints=_unpublished(root),
        workstreams=_workstreams(root),
        phases_without_status=_phases_without_status(root),
    )
