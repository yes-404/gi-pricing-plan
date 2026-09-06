"""Repository-level invariants that no single component owns.

These exist because of what a WK-657 re-audit found: **the traceability record only sees
`@pytest.mark.req` markers**, so a requirement enforced by something else — an
import-linter contract, a database privilege, a recorded measurement — reads as
unevidenced. WK-657 was the extreme case: its whole deliverable is enforcement machinery, so
`scope-audit.py` reported half its scope missing while the enforcement was working
perfectly in CI.

The fix is to make that enforcement visible as evidence rather than to trust it silently.
A test here does not replace the CI step it names; it links the requirement to the
mechanism, so an audit can find it.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.mark.req("FR-8")
def test_pricing_core_is_callable_without_the_backend() -> None:
    """ADR-703, enforced by the import-linter contract rather than by a unit test.

    "All pricing computation lives in `pricing-core` and is callable without the backend"
    is a property of the dependency graph, not of any function. The contract checks the
    whole graph on every run, which is stronger than anything a test could assert about one
    module — but it is invisible to the requirement record without this.
    """
    binary = shutil.which("lint-imports")
    if binary is None:  # pragma: no cover - only when the dev group is not installed
        pytest.skip("lint-imports is not installed; run `uv sync --all-packages --dev`")

    result = subprocess.run([binary], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Contracts: 3 kept, 0 broken." in result.stdout


@pytest.mark.req("FR-9")
def test_the_architecture_contracts_are_configured_and_not_silently_empty() -> None:
    """A contract file that parses but checks nothing reports success for ever.

    That happened here: `root_packages` was comma-separated on one line, the ini parser
    split it into characters, and the ADR-703 contract enforced nothing for a day while
    reporting green. Asserting the count of *kept* contracts is what makes the difference
    between "the checker ran" and "the checker checked something".
    """
    config = (ROOT / ".importlinter").read_text(encoding="utf-8")
    assert "include_external_packages = True" in config
    for package in ("model_schema", "pricing_core", "app"):
        assert f"\n    {package}\n" in config, package
    assert config.count("[importlinter:contract:") == 3


@pytest.mark.req("NFR-462")
def test_the_full_stack_is_declared_for_local_use() -> None:
    """NFR-462: the stack runs locally via `docker compose up` with no cloud dependency.

    Structural only — that the services and their health checks are declared. The timing
    claim (NFR-529, measured at 21 s against a 300 s budget) lives in `deploy/README.md`
    and the roadmap, because starting containers is not something CI should do on every
    push to assert a number that changes with the runner.
    """
    compose = (ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8")
    for service in ("postgres:", "redis:", "minio:"):
        assert service in compose, service
    # No cloud dependency: every image is a public one pinned by name, and nothing
    # references an external endpoint the stack could not reach offline.
    assert "healthcheck:" in compose
    assert compose.count("healthcheck:") >= 3
    assert "amazonaws.com" not in compose


@pytest.mark.req("FR-398")
@pytest.mark.req("FR-437")
def test_the_local_provider_is_declared_behind_an_opt_in_profile() -> None:
    """FR-398 and FR-437: a local OIDC provider ships behind an opt-in profile.

    The profile is the requirement, not a detail of it -- FR-398 says a contributor
    running the test suites starts the same three containers as today. A `keycloak` service
    with no `profiles:` key satisfies the first half of the requirement and breaks the
    second, and the two are one line apart in the file. The same `profiles:` assertion
    discharges FR-437's half: no identity provider starts in the default stack.
    """
    compose = (ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8")
    assert "keycloak:" in compose
    assert "profiles:" in compose, "the provider must not start by default"
    # The realm is imported, not hand-configured -- FR-398's reproducibility half.
    assert "--import-realm" in compose
    # deploy/keycloak-local/ is the reference deployment FR-437 names, left free for
    # WK-674's production reference and never a component the default stack runs.
    assert (ROOT / "deploy" / "keycloak-local" / "realm-gi-pricing.json").is_file()


@pytest.mark.req("FR-398")
def test_the_checked_in_realm_declares_a_public_pkce_client() -> None:
    """FR-398's realm, asserted as a file rather than against a running provider.

    A test needing the container would be one nobody runs -- FR-398 says exactly that --
    so this reads the artifact that is committed. What it cannot check is that Keycloak
    agrees with it; Step 6 does that once, by round-tripping an export.
    """
    realm = json.loads(
        (ROOT / "deploy" / "keycloak-local" / "realm-gi-pricing.json").read_text(
            encoding="utf-8"
        )
    )
    assert realm["realm"] == "gi-pricing"

    spa = {c["clientId"]: c for c in realm["clients"]}["gi-pricing-frontend"]

    # Public client, no secret: FR-393 -- "no client secret exists in it".
    assert spa["publicClient"] is True
    assert "secret" not in spa
    # PKCE, and S256 specifically: `plain` is a code challenge that protects nothing.
    assert spa["attributes"]["pkce.code.challenge.method"] == "S256"
    # The dev server, which scripts/demo.py:49 fixes at 5173.
    assert any("localhost:5173" in uri for uri in spa["redirectUris"])
    # The audience the API verifies (config.py:141). Keycloak does not put a resource server
    # in `aud` unless a mapper says so -- this assertion catches its absence, because every
    # other part of the flow works without it.
    audiences = [
        m["config"]["included.client.audience"]
        for m in spa.get("protocolMappers", [])
        if m["protocolMapper"] == "oidc-audience-mapper"
    ]
    assert "gi-pricing-api" in audiences


@pytest.mark.req("FR-10")
@pytest.mark.req("FR-23")
def test_money_discipline_is_enforced_by_the_docs_audit() -> None:
    """FR-10 and FR-23 are checked in two places, and both must stay.

    The types enforce the value rule in code (`MoneyMinor`, `DecimalStr`); the docs
    audit enforces the name rule — a `_minor` field with a fractional example would
    otherwise pass unnoticed — across the contracts, citing FR-23.
    """
    audit = (ROOT / "scripts" / "audit-docs.py").read_text(encoding="utf-8")
    assert "_minor" in audit, "the money-discipline check is gone from the docs audit"
    assert "FR-23" in audit, "the money check no longer cites FR-23"

    result = subprocess.run(
        ["python3", "scripts/audit-docs.py"], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All checks passed" in result.stdout


@pytest.mark.req("FR-19")
def test_journey_citations_are_audited_in_ci() -> None:
    """FR-19(i): the mechanical citation audit, and the marker that makes it visible.

    The check lives in `scripts/audit-docs.py` (check 21) and `docs.yml` runs that script on
    every `docs/**` change, so the enforcement is real. But `req-coverage.py` reads
    `@pytest.mark.req` markers, and a check enforced only by a script reads as an unevidenced
    requirement — the failure re-auditing WK-657 produced, where half the scope looked missing
    while the enforcement was working perfectly in CI. This test is the link.

    It asserts three things rather than one, because each can rot independently: the check is
    still in the script, CI still runs the script on docs changes, and the audit still passes.

    **What it deliberately does not assert** is FR-19(ii) — one end-to-end test per
    journey. That is not built, and a marker here claiming the whole requirement is precisely
    the "a marker on an existing test is not evidence" failure the requirement's own text
    refuses.
    """
    audit = (ROOT / "scripts" / "audit-docs.py").read_text(encoding="utf-8")
    assert "FR-19" in audit, "check 21 is gone from the docs audit"
    assert "_path_segments" in audit, "the citation path parser is gone"

    workflow = (ROOT / ".github" / "workflows" / "docs.yml").read_text(encoding="utf-8")
    assert "scripts/audit-docs.py" in workflow, "CI no longer runs the docs audit"
    assert "docs/**" in workflow, "the docs audit no longer triggers on a docs change"

    result = subprocess.run(
        ["python3", "scripts/audit-docs.py"], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "journey citations:" in result.stdout, "check 21 did not run"
    assert "undeclared" not in result.stdout, result.stdout


@pytest.mark.req("NFR-525")
def test_the_governance_negative_tests_exist_in_ci() -> None:
    """NFR-525: separation of duties, append-only audit and permission enforcement are
    *covered by explicit negative tests in CI*.

    A requirement about the test suite, so the suite is where it is checked. Asserting the
    marker exists is weak on its own — what makes it meaningful is that each named test
    asserts a refusal, which is why the names are matched rather than counted.
    """
    import re

    suite = "\n".join(
        path.read_text(encoding="utf-8")
        for root in ("backend/tests", "packages", "tests")
        for path in (ROOT / root).rglob("test_*.py")
    )

    required = {
        "separation of duties": r"def test_the_submitter_cannot_approve",
        "distinct approvers": r"def test_two_approvals_must_come_from_distinct_principals",
        "append-only audit": r"def test_update_and_delete_are_rejected_by_the_database",
        "no truncate": r"def test_truncate_is_rejected",
        "permission enforcement": r"def test_a_caller_without_the_role_is_forbidden",
        "no self-elevation": r"def test_a_user_cannot_grant_a_permission_they_do_not_hold",
    }
    missing = [name for name, pattern in required.items() if not re.search(pattern, suite)]
    assert missing == [], f"negative tests missing for: {missing}"


@pytest.mark.req("FR-450")
def test_the_error_code_registry_matches_the_specs() -> None:
    """Every code a module declares it owns is registered, and no code is invented.

    Written after four codes were invented for `01` in one sitting — plausible names for
    conditions the spec had already named differently. `PlatformError` validates against
    the registry, so an unregistered code fails loudly; an *extra* one does not, and would
    reach a client as something no spec documents.
    """
    import re
    import sys

    sys.path.insert(0, str(ROOT / "backend" / "src"))
    from app.errors import DATA_ERROR_CODES, GOVERNANCE_ERROR_CODES, PLATFORM_ERROR_CODES

    registries = {
        "01-data-management.md": DATA_ERROR_CODES,
        "06-governance.md": GOVERNANCE_ERROR_CODES,
        "07-platform.md": PLATFORM_ERROR_CODES,
    }

    for filename, registry in registries.items():
        spec = (ROOT / "docs" / "specs" / filename).read_text(encoding="utf-8")
        marker = "**Error codes owned by this module:**"
        start = spec.index(marker)
        # The declaration runs to the blank line that ends the paragraph.
        block = spec[start : spec.index("\n\n", start)]
        declared = set(re.findall(r"`([A-Z][A-Z0-9_]{2,})`", block))
        assert declared, filename
        assert declared == set(registry), (
            f"{filename}: spec-only {sorted(declared - set(registry))}, "
            f"registry-only {sorted(set(registry) - declared)}"
        )


@pytest.mark.req("FR-450")
def test_every_error_code_pricing_core_raises_is_registered_and_declared() -> None:
    """A code `pricing-core` raises reaches the caller through `PlatformError`.

    **Marker corrected 2026-08-22 (WK-661 audit).** This claimed `FR-16`, which is *"one
    tenant, one deployment"* (`00` §3, ADR-710) and has nothing to do with error codes — so
    `req-coverage.py` counted tenant isolation as evidenced by a test that never mentions it.
    `CLAUDE.md` §13: a marker is a claim, not a proof. `FR-450` is the requirement this
    test actually evidences — *"RFC 9457 problem responses with stable `code`s"* — and it is
    what `test_the_error_code_registry_matches_the_specs` above already carries for the same
    property approached from the specification side.

    Deliberately **not** `FR-22`, which is the closest match by wording: that requirement
    specifies an `audit-docs.py` check that does not exist yet, is owned by the maintainer,
    and is triggered by Phase 1a's exit demo. Marking a passing test with it would claim
    evidence for unbuilt work — the same defect being corrected here.

    The fit handler maps a `GlmFitError`/`GbmFitError` code straight across, and
    `PlatformError` refuses a code it does not know — so an unregistered one turns a named
    refusal into `ValueError: unknown error code` **from inside the error path**, at the
    moment the caller most needs the answer.

    This has now happened twice: `GLM_SEPARATION_DETECTED` was unregistered from the spine
    until the diagnostics slice tripped it, and the GBM slice added eleven more codes that
    no test would have exercised until a real fit failed. Checking the *source* rather than
    waiting for a scenario is what makes the next one impossible rather than unlucky.

    `02-modelling.md` is deliberately absent from the spec-versus-registry test above,
    because §5.1's catalogue declares codes whose slices have not been built — so this
    checks the other direction: everything raised must be declared **and** registered, while
    the catalogue may still run ahead.
    """
    import ast
    import re
    import sys

    sys.path.insert(0, str(ROOT / "backend" / "src"))
    from app.errors import MODELLING_ERROR_CODES

    modelling = ROOT / "packages" / "pricing-core" / "src" / "pricing_core" / "modelling"
    trees = {path: ast.parse(path.read_text(encoding="utf-8")) for path in modelling.glob("*.py")}

    # Derived, not listed. This was a literal set of four names until 2026-08-18, and by then
    # the module defined nine error classes — so `PredictionError` and `ObjectiveError` were
    # invisible to the very check written to make an unregistered code impossible, and four
    # of `predict.py`'s codes had been reachable and unregistered since the prediction slice.
    # A hand-maintained list of what to scan fails the same way as a hand-maintained list of
    # what to register, one release later.
    raisers = {
        node.name
        for tree in trees.values()
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name.endswith("Error")
    }
    raised: dict[str, str] = {}

    for path, tree in trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.id if isinstance(node.func, ast.Name) else None
            if name not in raisers or not node.args:
                continue
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                raised[first.value] = path.name

    assert raised, "no error codes found — the scan is looking in the wrong place"

    unregistered = {
        code: where for code, where in raised.items()
        if code not in MODELLING_ERROR_CODES
    }
    assert not unregistered, (
        f"raised by pricing-core and unknown to PlatformError: {sorted(unregistered)}. "
        "Add them to MODELLING_ERROR_CODES and to `02` §5.1's catalogue."
    )

    spec = (ROOT / "docs" / "specs" / "02-modelling.md").read_text(encoding="utf-8")
    marker = "**Error codes owned by this module:**"
    block = spec[spec.index(marker) : spec.index("\n\n", spec.index(marker))]
    declared = set(re.findall(r"`([A-Z][A-Z0-9_]{2,})`", block))
    undeclared = sorted(code for code in raised if code not in declared)
    assert not undeclared, f"raised and registered but absent from `02` §5.1: {undeclared}"


@pytest.mark.req("FR-417")
def test_the_migration_chain_has_exactly_one_head() -> None:
    """Two branches adding a revision off the same parent merge cleanly and break the deploy.

    Found on 2026-08-23: W32-2 and W32-3 executed concurrently and each added a migration
    parented on `9e4c7b21fa08`. Nothing in the repository objected. Both branches were
    green, both would have squash-merged without conflict — `git` sees two new files in a
    directory, which is not a conflict — and the damage would first have appeared at the
    next `alembic upgrade head` as `Multiple head revisions are present`.

    That combination is the reason this is checked rather than trusted: the defect exists
    from the moment it lands, and it is invisible until somebody migrates. The chain is read
    through Alembic's own `ScriptDirectory`, so this test fails for the same reason and on
    the same data as the deployment it is protecting, rather than on a private re-parse of
    the version files.
    """
    import configparser

    from alembic.script import ScriptDirectory

    ini = configparser.ConfigParser()
    ini.read(ROOT / "alembic.ini", encoding="utf-8")
    location = ROOT / ini["alembic"]["script_location"]
    assert location.is_dir(), f"alembic.ini script_location does not resolve: {location}"

    heads = ScriptDirectory(str(location)).get_heads()

    assert len(heads) == 1, (
        f"the migration chain has {len(heads)} heads: {sorted(heads)}. Two branches each "
        "added a revision off the same parent. Re-parent the later migration's "
        "`down_revision` onto the other head — or, if the divergence was deliberate, record "
        "that with `alembic merge`, which is the documented way to say so."
    )
