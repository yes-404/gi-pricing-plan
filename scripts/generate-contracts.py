#!/usr/bin/env python3
"""Generate the committed contracts from the code (FR-PLAT-48, ADR-0002).

`packages/model-schema` is the single source of truth for every shape crossing a boundary.
This script is what makes that claim checkable rather than aspirational: it writes the
OpenAPI document and the JSON Schemas from the models, and `--check` fails when the
committed copies no longer match.

Two files matter and they are not the same kind of thing:

* ``docs/contracts/openapi/generated.json`` — **generated**, the API as it is today.
* ``docs/contracts/openapi/gi-pricing.yaml`` — the Phase 0 **design stub**, describing the
  whole intended surface. It is not overwritten. Replacing a design document that covers
  eight modules with generated output covering the routes built so far would delete the
  specification to make the tooling tidy. The generated file grows toward the stub as
  routes land, and the stub retires when it is reached.

Run ``scripts/generate-contracts.py`` to write, ``--check`` to verify.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend" / "src"))

OPENAPI_PATH = ROOT / "docs" / "contracts" / "openapi" / "generated.json"
SCHEMA_DIR = ROOT / "docs" / "contracts" / "schemas" / "generated"

#: Shapes model-schema owns. Each is written to `<slug>.schema.json`; the slug matches the
#: hand-authored Phase 0 contract where one exists, so conformance is a file-to-file
#: comparison rather than a guess about which schema describes what.
GENERATED_SHAPES: dict[str, str] = {
    "job": "Job",
    "audit-event": "AuditEvent",
    "problem-detail": "ProblemDetail",
    "blob-ref": "BlobRef",
    "artifact-ref": "ArtifactRef",
    "artifact-envelope": "ArtifactEnvelope",
    # Added 2026-08-15 (W5). Both had hand-authored Phase-0 contracts and no generated
    # counterpart, so nothing compared the shape the code produces against the shape the
    # contract promises — and three divergences went unnoticed until `main` moved.
    "banding": "Banding",
    "grouping": "Grouping",
    # Added 2026-08-16 (W5, diagnostics). Same reason as the two above, learned from them:
    # `diagnostics.schema.json` is a hand-authored Phase-0 contract, and until there is a
    # generated counterpart nothing compares it against the shape the code actually emits.
    "diagnostics": "Diagnostics",
    "dataset-split": "DatasetSplit",
    # Added 2026-08-17 (W5, model comparison). **No hand-authored Phase-0 counterpart** —
    # `02` §5.2 named `ModelComparison` as a return type and no document defined it, so this
    # is the shape's first written form rather than a check on an existing one.
    "model-comparison": "ModelComparison",
    # Added 2026-08-17 (W5, the GBM arm). `model-spec` is a **union**, not a model class —
    # `02` §4.4's tagged union acquired its second arm here, and the published contract is
    # the only place a consumer can see both. `model` follows it because the union is what
    # a Model carries; generating one without the other publishes a spec shape no artifact
    # references. Both have hand-authored Phase-0 counterparts, so this is the first thing
    # to compare them against.
    "model-spec": "MODEL_SPEC_ADAPTER",
    "model": "Model",
    # Added 2026-08-17 (W5, transparency). `transparency-artifact.schema.json` is a
    # hand-authored Phase-0 contract that nothing has ever compared against code, and R3
    # makes this the artifact a Rating Version's approval hangs from.
    "transparency-artifact": "TransparencyArtifact",
    # Added 2026-08-18 (W5, peril structures), and **superseded 2026-08-24 (W32-11)**: the
    # slug has an authored side now (added by #133's audit remediation), so it is two-sided
    # and compared like any other. The "No hand-authored Phase-0 counterpart" sentence that
    # once stood here went stale silently for six days — the worked instance behind
    # `OQ-PLAT-10`. One-sidedness is now declared in `ONE_SIDED_SLUGS` in
    # `backend/tests/test_contracts.py` and checked against the corpus in both directions;
    # this comment no longer narrates it (2026-08-27, W6b-22).
    "peril-structure": "PerilStructure",
    # Added 2026-08-18 (W5, backtests). No hand-authored Phase-0 counterpart: FR-MODEL-57
    # named the operation and no document defined what it produces, so this is the shape's
    # first written form. It is also the artifact `05-monitoring.md` reads as its evidence
    # bridge, which makes publishing it the point rather than a side effect.
    "backtest": "Backtest",
    # Added 2026-08-18 (W5, custom objectives). Both have hand-authored Phase-0 contracts
    # and, until now, no generated counterpart — the position `banding` and `grouping` were
    # in when four divergences had accumulated unseen. `custom-objective` is also the shape
    # an approver's evidence hangs from (FR-MODEL-42), so a field the contract promises and
    # the model does not carry is a governance gap rather than a documentation one.
    "custom-objective": "CustomObjective",
    "objective-certificate": "ObjectiveCertificate",
    # No hand-authored counterpart: FR-MODEL-47 named the blast-radius query and no document
    # defined what it returns. This is the shape's first written form, and it is the one
    # `03 — Rating Engine` fills in — `rating_versions` and `deployments` are published
    # empty on purpose (FR-MODEL-87), which is only legible if the shape is published.
    "objective-usage": "ObjectiveUsage",
    # Added 2026-08-19 (W5, custom metrics, Task 2 of the custom-metrics slice). No
    # hand-authored Phase-0 counterpart: `02` §4.13 printed an example and defined no
    # contract, so this is the shape's first written form. It is the artifact a GBM fit's
    # early stopping reads (FR-MODEL-103/104), so a field the contract promises and the
    # model does not carry is a training-time defect, not a documentation one.
    "custom-metric": "CustomMetric",
    # Added 2026-08-19 (W5, custom metrics, Task 2 of the custom-metrics slice, fix
    # round 2). `ObjectiveCertificate` is published (line 87); leaving its sibling
    # unpublished would have FR-MODEL-108's `GET .../certificate` cross the API
    # boundary as a hand-written frontend type instead of a generated one — the
    # divergence ADR-0002/FR-PLAT-48 exist to prevent.
    "metric-certificate": "MetricCertificate",
    # Added 2026-08-18 (W5, the profile contract). `profile.schema.json` is a hand-authored
    # Phase-0 contract that nothing has ever compared against code — the position `banding`
    # and `grouping` were in when four divergences had accumulated unseen. It is also the
    # artifact `02`'s factor workbench reads and never recomputes (FR-DATA-27), so a field
    # the contract promises and the model does not carry is a wrong number on a screen
    # rather than a documentation defect.
    "profile": "Profile",
    # Added 2026-08-23 (W32-2, the built-in rule catalogue). `validation-rule.schema.json`
    # is a hand-authored Phase-0 contract with no generated counterpart, so nothing has ever
    # compared it against `ValidationRule` — and it had drifted three ways: a `severity`
    # enum containing `"info"`, which `Severity` has never had; a `check` enum missing most
    # of the registry; and two fields the model does not carry (`owner`,
    # `dry_run_result_id`). Patching those would leave the mechanism that produced them in
    # place, which is what FR-PLAT-48 exists to remove.
    "validation-rule": "ValidationRule",
    # Added 2026-08-24 (W32-11). The last two of the three Phase-1a shapes `contract-guard`
    # names as a genuine gap in the guard's reach — `validation-rule` was the first and was
    # closed by W32-2. Both have hand-authored Phase-0 contracts
    # (`dataset-version.schema.json`, `validation-report.schema.json`) that nothing has ever
    # compared against code, which is the position `banding` and `grouping` were in when
    # four divergences had accumulated unseen. With these published, no shape in the
    # contract corpus is a hand-authored promise no code is checked against.
    "dataset-version": "DatasetVersion",
    "validation-report": "ValidationReport",
    # Added 2026-08-25 (W6b-10, browser auth). No hand-authored Phase-0 counterpart —
    # FR-PLAT-66 names the shape's contents, so this is its first written form.
    "oidc-auth-config": "OidcAuthConfig",
    # Added 2026-08-26 (W6b-12). **No hand-authored Phase-0 counterpart** — `01` §4.9 is
    # the shape's first written form, defined in the spec before any code, and the
    # generated file is the only place a consumer can see the wire form.
    "dataset-lineage": "DatasetLineage",
}


def _render(document: dict[str, Any]) -> str:
    """Serialise deterministically.

    Sorted keys and a fixed indent, because the whole point is a byte comparison in CI. A
    document that re-serialises differently on every run reports drift that is not drift,
    and a check that cries wolf is turned off.
    """
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def build_openapi() -> dict[str, Any]:
    from app.config import Environment, Settings
    from app.main import create_app

    # A fixed settings object: the document must not depend on the environment that
    # generated it, or CI and a developer machine produce different bytes.
    # log_level ERROR: this script writes files, and a JSON log line on stdout makes
    # its output harder to read in CI than the result it is reporting.
    app = create_app(
        Settings(environment=Environment.LOCAL, version="0.1.0", log_level="ERROR")
    )
    document: dict[str, Any] = app.openapi()
    return document


def build_schemas() -> dict[str, dict[str, Any]]:
    import pydantic

    import model_schema

    out: dict[str, dict[str, Any]] = {}
    for slug, name in GENERATED_SHAPES.items():
        model = getattr(model_schema, name)
        # Validation mode, deliberately. The hand-authored contracts describe documents
        # to be *validated*, and — more importantly — research F7's hazard only appears
        # here: a bare `Decimal` renders as `anyOf: [number, string]` in validation mode
        # and as a plain string in serialization mode. Generating the serialization schema
        # would produce a contract that looks compliant while the request side accepts the
        # lossy float FR-OVR-7 forbids.
        # A discriminated union has no `model_json_schema` — it is not a class. Its
        # `TypeAdapter` answers the same question, in the same mode, and is the only way
        # the union's arms reach a published contract at all.
        out[slug] = (
            model.json_schema(mode="validation")
            if isinstance(model, pydantic.TypeAdapter)
            else model.model_json_schema(mode="validation")
        )
    return out


def _targets() -> dict[pathlib.Path, str]:
    files = {OPENAPI_PATH: _render(build_openapi())}
    for slug, schema in build_schemas().items():
        files[SCHEMA_DIR / f"{slug}.schema.json"] = _render(schema)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail instead of writing when a committed file is out of date.",
    )
    args = parser.parse_args()

    files = _targets()
    stale: list[pathlib.Path] = []

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        if args.check:
            stale.append(path)
        else:
            path.write_text(content, encoding="utf-8")
            print(f"  wrote {path.relative_to(ROOT)}")

    if args.check:
        if stale:
            print("  FAIL: committed contracts are out of date with the models:")
            for path in stale:
                print(f"      {path.relative_to(ROOT)}")
            print("\n  Run `uv run python scripts/generate-contracts.py` and commit the result.")
            print("  ADR-0002: the models are the source of truth, so the contract follows")
            print("  the code — never the other way round.")
            return 1
        print(f"  {len(files)} generated contracts match the models")
        return 0

    print(f"  {len(files)} contracts up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
