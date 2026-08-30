#!/usr/bin/env python3
"""Seed a freMTPL2 workspace, through the platform's own path (`07` FR-PLAT-37).

    uv run python examples/fremtpl2/fetch.py
    uv run python examples/fremtpl2/seed.py            # full 678 013 rows
    uv run python examples/fremtpl2/seed.py --rows 50000

**It drives real Jobs.** Every step goes through `ingest.upload → blob → Job →
execute_job`, the same path a worker takes in production — not through the services
underneath it. A seed that took a shortcut would prove the shortcut works.

The story it tells is Phase 1a's exit criterion, and the failure in the middle is **real**:
571 of freMTPL2's rows carry an exposure above 1.0 — up to 2.01 — which VR-ACT-2 refuses as
implausible for an annual policy. Version 1 fails validation on data nobody tampered with.
Version 2 adds a preparation step, and reaches `validated`.
"""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import sys
import time
from pathlib import Path
from typing import Any
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

from arff import to_csv

DATA_DIR = Path(__file__).parent / "data"

#: The realm `deploy/keycloak-local/realm-gi-pricing.json` imports, and the subject it pins
#: for the demo analyst. These two strings are the join between a browser login and this
#: seed: `authenticate_bearer` keys a user on `(issuer, subject)`, so a realm re-import that
#: changed either would authenticate a *different* user into nothing.
REALM_ISSUER = "http://localhost:8080/realms/gi-pricing"
REALM_SUBJECT = "84eea68e-a19e-46a0-9f35-a27cbd51c795"

#: `IDpol` normalises to `i_dpol`, not `idpol`: the camel-case splitter reads it as
#: `I` + `Dpol`, the same rule that correctly gives `HTTPServer` → `http_server`. No
#: mechanical splitter can know that `ID` is the acronym here. The original header is kept
#: in the version's `source_names` (FR-DATA-5), and this rename is the remedy — which the
#: seed needs anyway, to reach the platform's vocabulary (`CLAUDE.md` §7).
RENAMES = {
    "i_dpol": "policy_id",
    "claim_nb": "claim_count",
    "exposure": "exposure_years",
}

NUMERIC = {
    "exposure_years": "float",
    "claim_count": "int",
    "veh_power": "int",
    "veh_age": "int",
    "driv_age": "int",
    "bonus_malus": "int",
    "density": "int",
    "claim_amount_minor": "int",
}

#: VR-ACT-2's bound. An annual motor policy cannot be on risk for two years.
MAX_EXPOSURE = 1.05


def recipe(*, drop_implausible_exposure: bool) -> list[dict[str, Any]]:
    """The Preparation Recipe, applied during ingestion (FR-DATA-9).

    Version 1 renames and casts and nothing else — the shape a user gets by uploading the
    file and accepting the inferred schema. Version 2 adds the one step that fixes what
    validation found, which is the whole point of the loop.
    """
    steps: list[dict[str, Any]] = [
        {"step": "rename", "table": "policy_exposure", "params": {"columns": RENAMES}},
        # Every column arrives as a string on purpose (FR-DATA-4): a policy id of `007`
        # must not become `7`. Without this step every numeric rule compares a string to a
        # number and errors.
        {"step": "cast", "table": "policy_exposure", "params": {"columns": NUMERIC}},
    ]
    if drop_implausible_exposure:
        steps.append(
            {
                "step": "filter_rows",
                "table": "policy_exposure",
                "params": {"expression": f"exposure_years <= {MAX_EXPOSURE}"},
            }
        )
    return steps


def build_csv(rows: int | None) -> bytes:
    """freMTPL2's two files as one policy-exposure table.

    The claim amounts are joined here rather than by the platform because `ingest_upload`
    accepts **one** table per version, while `01` §4.2's `tables[]` is plural and
    FR-DATA-12's `attach_claims` expects a separate claim table. Multi-table ingestion is a
    gap this seed found; joining first is what an analyst would do today, and it is
    recorded rather than hidden.
    """
    import polars as pl

    print("  reading freMTPL2freq.arff …", flush=True)
    frame = pl.read_csv(io.BytesIO(to_csv(DATA_DIR / "freMTPL2freq.arff")), infer_schema=False)
    print("  reading freMTPL2sev.arff …", flush=True)
    severity = pl.read_csv(io.BytesIO(to_csv(DATA_DIR / "freMTPL2sev.arff")), infer_schema=False)

    # Amounts are euros with at most two decimals — verified against the pinned file — so
    # scaling to integer minor units is exact rather than rounded (FR-OVR-7).
    totals = (
        severity.with_columns(
            (pl.col("ClaimAmount").cast(pl.Float64) * 100).round(0).cast(pl.Int64)
            .alias("claim_amount_minor")
        )
        .group_by("IDpol")
        .agg(pl.col("claim_amount_minor").sum())
    )
    joined = (
        frame.join(totals, on="IDpol", how="left")
        .with_columns(pl.col("claim_amount_minor").fill_null(0))
        .with_columns(pl.col("claim_amount_minor").cast(pl.Utf8))
    )
    if rows is not None:
        # **Not `head`.** The file is ordered by claim count, so the first 50 000 rows are
        # very nearly every claiming policy and almost nothing else — a sample whose
        # frequency is 0.42 against the book's 0.05, which fails a plausibility rule for a
        # reason that is entirely the sampler's fault. Every nth row preserves the mix.
        step = max(joined.height // rows, 1)
        joined = joined.gather_every(step).head(rows)

    buffer = io.BytesIO()
    joined.write_csv(buffer)
    return buffer.getvalue()


DICTIONARY: dict[str, dict[str, Any]] = {
    "policy_id": {
        "description": "Policy identifier, pseudonymous in the public extract",
        "semantic_type": "identifier",
        "pii_class": "pseudonymous_key",
    },
    "exposure_years": {
        "description": "Time on risk",
        "semantic_type": "continuous",
        "unit": "years",
    },
    "claim_count": {
        "description": "Claims incurred in the period",
        "semantic_type": "ordinal",
    },
    "claim_amount_minor": {
        "description": "Total incurred, euro cents",
        "semantic_type": "money",
    },
    "area": {
        "description": "Population-density band of the community",
        "semantic_type": "ordinal",
    },
    "veh_power": {
        "description": "Vehicle power group",
        "semantic_type": "ordinal",
    },
    "veh_age": {
        "description": "Vehicle age at inception",
        "semantic_type": "continuous",
        "unit": "years",
    },
    "driv_age": {
        "description": "Driver age at inception",
        "semantic_type": "continuous",
        "unit": "years",
    },
    "bonus_malus": {
        "description": "French bonus-malus coefficient, 50 to 350",
        "semantic_type": "continuous",
    },
    "veh_brand": {
        "description": "Vehicle brand group",
        "semantic_type": "categorical",
    },
    "veh_gas": {
        "description": "Diesel or regular",
        "semantic_type": "categorical",
    },
    "density": {
        "description": "Inhabitants per square km of the community",
        "semantic_type": "continuous",
    },
    "region": {
        "description": "French administrative region",
        "semantic_type": "categorical",
        "reference_table": "fr-region",
    },
}


#: One rule per layer plus the exposure bound, so FR-DATA-16's four layers are all present
#: and the rule set carries no configuration warning. Real thresholds, not placeholders:
#: motor third-party frequency of 2 to 25 % and a mean severity between €50 and €50 000 are
#: the bands a French motor book is actually judged against.
RULES: list[dict[str, Any]] = [
    {
        "slug": "columns-present", "layer": "structural", "check": "column_presence",
        "severity": "fail", "target": {"table": "policy_exposure"},
        "params": {"columns": ["policy_id", "exposure_years", "claim_count"]},
    },
    {
        "slug": "policy-id-unique", "layer": "structural", "check": "unique_key",
        "severity": "fail", "target": {"table": "policy_exposure"},
        "params": {"columns": ["policy_id"], "key_columns": ["policy_id"]},
    },
    {
        "slug": "region-known", "layer": "referential", "check": "set_membership",
        "severity": "fail", "target": {"table": "policy_exposure", "column": "region"},
        "params": {
            "allowed": [f"R{n}" for n in (11, 21, 22, 23, 24, 25, 26, 31, 41, 42, 43,
                                          52, 53, 54, 72, 73, 74, 82, 83, 91, 93, 94)],
            "key_columns": ["policy_id"],
        },
    },
    {
        "slug": "exposure-positive", "layer": "actuarial_sanity", "check": "range",
        "severity": "fail",
        "target": {"table": "policy_exposure", "column": "exposure_years"},
        "params": {"min_exclusive": 0, "key_columns": ["policy_id"]},
    },
    {
        # VR-ACT-2. This is the one freMTPL2 breaks: 571 rows carry an exposure above 1.0,
        # up to 2.01, which cannot be a year on risk for an annual policy.
        "slug": "exposure-plausible", "layer": "actuarial_sanity", "check": "range",
        "severity": "fail",
        "target": {"table": "policy_exposure", "column": "exposure_years"},
        "params": {"max_inclusive": MAX_EXPOSURE, "key_columns": ["policy_id"]},
    },
    {
        "slug": "claim-count-non-negative", "layer": "actuarial_sanity", "check": "range",
        "severity": "fail",
        "target": {"table": "policy_exposure", "column": "claim_count"},
        "params": {"min_inclusive": 0, "key_columns": ["policy_id"]},
    },
    {
        "slug": "frequency-plausible", "layer": "actuarial_sanity",
        "check": "frequency_plausible", "severity": "warn",
        "target": {"table": "policy_exposure"},
        "params": {"min_frequency": 0.02, "max_frequency": 0.25},
    },
    {
        # VR-ACT-10. freMTPL2's largest incurred is €4 075 400 — a genuine large loss, and
        # it must be flagged for large-loss treatment rather than quietly removed.
        "slug": "severity-outlier", "layer": "actuarial_sanity",
        "check": "severity_outlier", "severity": "warn",
        "target": {"table": "policy_exposure", "column": "claim_amount_minor"},
        "params": {"percentile": 0.995, "key_columns": ["policy_id"]},
    },
    {
        "slug": "vehicle-brand-mix", "layer": "distributional", "check": "psi_column",
        "severity": "warn",
        "target": {"table": "policy_exposure", "column": "veh_brand"},
        "params": {"warn_above": 0.10, "fail_above": 0.25},
    },
]


async def run(rows: int | None) -> int:
    from sqlalchemy import select

    from app.config import load_settings
    from app.db.models import (
        DatasetVersionRow,
        RoleAssignmentRow,
        RoleRow,
        ValidationRuleRow,
    )
    from app.db.session import Database
    from app.platform import datasets as dataset_service
    from app.platform import jobs as job_service
    from app.platform import profiles as profile_service
    from app.platform import rbac, workspaces
    from app.platform import validation as validation_service
    from app.platform.blobs import BlobStore
    from app.worker.data_handlers import register_data_handlers
    from app.worker.tasks import execute_job
    from model_schema import (
        BUILTIN_RULES,
        ActorKind,
        JobKind,
        JobStatus,
        Principal,
        RuleOutcome,
        ScopeType,
        new_uuid7,
    )

    #: Which catalogue entry each of `RULES` configures, where one exists. Four of the nine
    #: — the structural, referential and distributional ones — are freMTPL2's own and map
    #: to nothing; `dict.get` returning `None` for those is the intended answer.
    catalogue_id_by_slug = {
        rule.slug: catalogue_id for catalogue_id, rule in BUILTIN_RULES.items()
    }

    register_data_handlers()
    settings = load_settings()
    database, blob_store = Database(settings), BlobStore(settings)
    await blob_store.ensure_bucket()

    workspace_id = new_uuid7()
    analyst = Principal(kind=ActorKind.USER, id=new_uuid7(), display="analyst@example.fr")
    actuary = Principal(kind=ActorKind.USER, id=new_uuid7(), display="actuary@example.fr")
    # Principal.id is UUID | None at the type level -- "null only for `system`" (jobs.py) --
    # but both of these are ActorKind.USER with an id supplied at construction, and
    # Principal's own validator refuses a non-system principal with no id. Narrow once here
    # rather than at every call site below that needs a bare UUID.
    assert analyst.id is not None
    assert actuary.id is not None

    async def grant(principal: Principal, *slugs: str) -> None:
        async with database.unit_of_work() as session:
            await rbac.seed_builtin_roles(session, workspace_id)
            for slug in slugs:
                role = (
                    await session.execute(
                        select(RoleRow).where(
                            RoleRow.workspace_id == workspace_id, RoleRow.slug == slug
                        )
                    )
                ).scalar_one()
                session.add(
                    RoleAssignmentRow(
                        workspace_id=workspace_id, principal_kind="user",
                        principal_id=principal.id, role_id=role.id,
                        scope_type=ScopeType.WORKSPACE.value,
                    )
                )

    approver = Principal(kind=ActorKind.USER, id=new_uuid7(), display="approver@example.fr")

    await grant(analyst, "analyst")
    await grant(actuary, "pricing_actuary")
    await grant(approver, "approver")

    # A real login through the local provider (FR-PLAT-58) resolves to `analyst`, so it
    # inherits the role assignments granted just above rather than needing its own. The
    # workspace row comes first: `workspace_members.workspace_id` is a foreign key, and
    # nothing has created that row until now -- `RoleRow.workspace_id` has no foreign key,
    # which is why the seed has worked without one. The actuary has no realm user; one demo
    # login is what FR-PLAT-58 asks for.
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(
            session, workspace_id=workspace_id, name="freMTPL2 demo"
        )
        await workspaces.ensure_member(
            session,
            workspace_id=workspace_id,
            user_id=analyst.id,
            issuer=REALM_ISSUER,
            subject=REALM_SUBJECT,
            email=analyst.display,
            display_name="Demo Analyst",
        )

    print(f"\nworkspace {workspace_id}")
    print(f"  analyst  {analyst.display}\n  actuary  {actuary.display}\n")
    # The ids, not only the names: the workspace is what the demo login lands in, and a
    # seed that printed neither left the only way into the UI undiscoverable. The dev
    # proxy needs none of them — it injects no identity (W6b-10) and no workspace
    # (W6b-11); the selector in the app makes the choice.
    # Written as well as printed: `scripts/demo.py` checks this record to confirm the seed
    # ran, and parsing ids back out of stdout would make the seed's print format a
    # contract between two programs — the least visible kind there is.
    (DATA_DIR / "last-seed.json").write_text(
        json.dumps(
            {
                "workspace_id": str(workspace_id),
                "analyst_id": str(analyst.id),
                "actuary_id": str(actuary.id),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("  to open the frontend (it selects this workspace itself):")
    print("    pnpm --dir frontend dev\n")

    payload = build_csv(rows)
    print(f"  {len(payload) / 1e6:.1f} MB CSV, {payload.count(chr(10).encode()) - 1:,} rows\n")

    slug = f"fremtpl2-{new_uuid7().hex[-6:]}"
    async with database.unit_of_work() as session:
        from sqlalchemy import func

        from app.platform import validation_rules as rule_service
        from model_schema import DataDictionaryEntry, RecordGrain

        dataset = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=analyst, slug=slug,
            name="freMTPL2 — French motor TPL", line_of_business="motor",
            territory="FR", currency="EUR",
            default_record_grain=RecordGrain.POLICY_EXPOSURE,
            data_dictionary={
                column: DataDictionaryEntry.model_validate(entry)
                for column, entry in DICTIONARY.items()
            },
        )
        dataset_id = dataset.id

        # `01` §4.4's catalogue arrives with the workspace, exactly as the roles do
        # (FR-DATA-53). It is the shipped *definitions*: names, checks and severities, with
        # no target — §4.4 says what the rule is, and a workspace says which of its tables
        # the rule runs against.
        await rule_service.seed_builtin_rules(
            session, workspace_id, authored_by=analyst.id
        )

        rule_ids: list[str] = []
        for rule in RULES:
            # Five of the nine configure a catalogue entry rather than inventing one, so
            # `version=1` is already taken by the seeded definition. The next version is
            # allocated the way `create_rule` allocates it — §4.5 step 4's ordinary "an
            # edit is a new version", which is exactly what pointing a shipped rule at
            # `policy_exposure` is.
            version = 1 + (
                await session.execute(
                    select(func.coalesce(func.max(ValidationRuleRow.version), 0)).where(
                        ValidationRuleRow.workspace_id == workspace_id,
                        ValidationRuleRow.slug == rule["slug"],
                    )
                )
            ).scalar_one()
            row = ValidationRuleRow(
                workspace_id=workspace_id, slug=rule["slug"], version=version,
                layer=rule["layer"], check=rule["check"], severity=rule["severity"],
                body={"target": rule["target"], "params": rule["params"], "scope": {},
                      "tolerance": {}, "message": "", "rationale": ""},
                status="approved", authored_by=analyst.id, approved_by=actuary.id,
                dry_run_report_id=new_uuid7(),
                # Workspace data, not a shipped row: it carries its own approver and its
                # own dry run. `catalogue_id` records which shipped rule it configures, so
                # the lineage survives the version bump; `builtin` stays false, because the
                # approval exemption belongs to the reviewed definition and not to a
                # workspace's configuration of it.
                catalogue_id=catalogue_id_by_slug.get(rule["slug"]),
            )
            session.add(row)
            await session.flush()
            rule_ids.append(str(row.id))
    # Through the service, not a direct insert: `replace_rule_set` is what points the
    # dataset at its rule set (`01` §4.1's `validation_rule_set_id`), and a seed that
    # bypassed it would produce a workspace the platform itself would not.
    async with database.unit_of_work() as session:
        from app.platform import validation_rules as rule_service

        await rule_service.replace_rule_set(
            session, workspace_id=workspace_id, actor=analyst, dataset_id=dataset_id,
            slug=str(dataset_id),
            members=[rule_service.RuleSetMember(rule_id=UUID(r)) for r in rule_ids],
        )
    print(
        f"  dataset {slug} with {len(RULES)} approved rules across four layers, "
        f"and `01` \u00a74.4's {len(BUILTIN_RULES)}-rule catalogue seeded\n"
    )

    async def ingest(label: str, *, cleaned: bool) -> UUID:
        started = time.perf_counter()
        async with database.unit_of_work() as session:
            ref = await blob_store.put(session, payload, "text/csv")
            job = await job_service.submit(
                session, JobKind.DATASET_INGEST,
                {"workspace_id": str(workspace_id),
                 "actor": analyst.model_dump(mode="json"),
                 "dataset_id": str(dataset_id), "blob": ref.sha256,
                 "filename": "fremtpl2.csv",
                 "recipe": recipe(drop_implausible_exposure=cleaned)},
                analyst, workspace_id=workspace_id,
            )
        status = await execute_job(database, job.id, blob_store)
        if status is not JobStatus.SUCCEEDED:
            raise SystemExit(f"{label}: ingestion job {status.value} — see job {job.id}")
        async with database.session() as session:
            version = (
                await session.execute(
                    select(DatasetVersionRow)
                    .where(DatasetVersionRow.dataset_id == dataset_id)
                    .order_by(DatasetVersionRow.version.desc()).limit(1)
                )
            ).scalar_one()
            profile = await profile_service.latest_profile(
                session, workspace_id=workspace_id, version_id=version.id
            )
        print(f"  {label}: v{version.version}, {profile.row_count:,} rows, "
              f"{len(profile.columns)} columns profiled, {time.perf_counter() - started:.1f}s")
        return version.id

    async def validate(version_id: UUID) -> UUID:
        started = time.perf_counter()
        async with database.unit_of_work() as session:
            job = await job_service.submit(
                session, JobKind.DATASET_VALIDATE,
                {"workspace_id": str(workspace_id),
                 "actor": analyst.model_dump(mode="json"),
                 "dataset_version_id": str(version_id)},
                analyst, workspace_id=workspace_id,
            )
        status = await execute_job(database, job.id, blob_store)
        if status is not JobStatus.SUCCEEDED:
            raise SystemExit(f"validation job {status.value} — see job {job.id}")
        async with database.session() as session:
            report_id = (
                await validation_service.reports_for_version(
                    session, workspace_id=workspace_id, version_id=version_id
                )
            )[0].id
            report = await validation_service.load_report(
                session, workspace_id=workspace_id, report_id=report_id
            )
        verdict = validation_service.overall_outcome(report).value
        print(f"    validation: {verdict} in {time.perf_counter() - started:.1f}s")
        for result in report.results:
            if result.outcome is not RuleOutcome.PASS:
                rows = f", {result.affected_rows:,} rows" if result.affected_rows else ""
                print(f"      {result.outcome.value:<5} {result.rule_slug:<26}"
                      f"{result.detail[:56]}{rows}")
        return report_id

    print("── version 1: the file as uploaded " + "─" * 40)
    first = await ingest("ingest", cleaned=False)
    first_report = await validate(first)

    # No manual transition: `dataset.validate` opens `validating` and closes it. This
    # version's report failed, so it is already `failed` (FR-DATA-43).
    try:
        async with database.unit_of_work() as session:
            await validation_service.promote_using_report(
                session, workspace_id=workspace_id, actor=actuary,
                version_id=first, report_id=first_report,
            )
        raise SystemExit("version 1 was promoted — the gate did not hold")
    except Exception as exc:
        code = getattr(exc, "code", type(exc).__name__)
        print(f"    promotion refused: {code}")
        async with database.session() as session:
            # Named distinctly from the `ValidationRuleRow` bound to `row` above: the same
            # local name across both would let mypy infer `row`'s type from whichever
            # assignment runs first and flag the other as incompatible.
            version_row = await session.get(DatasetVersionRow, first)
            assert version_row is not None, f"dataset version {first} vanished mid-run"
            print(f"    version 1 is {version_row.status} — not left mid-run (FR-DATA-43)\n")

    print("── version 2: one preparation step later " + "─" * 34)
    second = await ingest("ingest", cleaned=True)
    second_report = await validate(second)

    async with database.unit_of_work() as session:
        outstanding = await validation_service.unacknowledged_warnings(
            session, workspace_id=workspace_id, report_id=second_report
        )
        report = await validation_service.load_report(
            session, workspace_id=workspace_id, report_id=second_report
        )
    if outstanding:
        async with database.unit_of_work() as session:
            for result in report.results:
                if result.outcome is RuleOutcome.WARN:
                    await validation_service.acknowledge(
                        session, workspace_id=workspace_id, actor=actuary,
                        report_id=second_report, rule_id=result.rule_id,
                        justification=(
                            "Reviewed against the 2023 French motor market: within "
                            "expectation for this book."
                        ),
                    )
            print(f"    {outstanding} warning(s) acknowledged by {actuary.display}")

    # A passing report leaves the version `validating`; promotion is the actuary's act.
    async with database.unit_of_work() as session:
        promoted = await validation_service.promote_using_report(
            session, workspace_id=workspace_id, actor=actuary,
            version_id=second, report_id=second_report,
        )
    print(f"    version {promoted.version} is {promoted.status}\n")

    async with database.session() as session:
        fittable = await dataset_service.fittable_or_refuse(
            session, workspace_id=workspace_id, version_id=second
        )
    print(f"  a model may be fitted on {slug}@{promoted.version} ({fittable.id})")
    print("  and still may not on @1 — `01` §1.3 has no override\n")

    # W7-1/W7-2: the demo models — factors, GLM and GBM fits, then the comparison and
    # approval. `Path(__file__).parent` is on sys.path (the seed's own import shim), so
    # `model` — not `examples.fremtpl2.model` — is the importable name here.
    from model import compare_and_approve, create_approved_rating_version, fit_demo_models

    fitted = await fit_demo_models(
        database, blob_store, workspace_id, analyst, dataset_id, second
    )
    print(f"  demo models fitted: GLM {fitted['glm']}, GBM {fitted['gbm']}")
    approved = await compare_and_approve(
        database, blob_store, workspace_id, actuary, approver,
        fitted["glm"], fitted["gbm"],
    )
    print(f"  approved model: {approved}")
    await create_approved_rating_version(
        database, workspace_id, analyst, actuary, approver, second, approved
    )
    print()
    await database.dispose()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, help="Seed a sample rather than all 678 013")
    args = parser.parse_args()
    if not (DATA_DIR / "freMTPL2freq.arff").exists():
        raise SystemExit("run examples/fremtpl2/fetch.py first")
    return asyncio.run(run(args.rows))


if __name__ == "__main__":
    sys.exit(main())
