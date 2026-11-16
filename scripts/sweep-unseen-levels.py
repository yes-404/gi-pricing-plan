#!/usr/bin/env python3
"""Read-only sweep of stored Rating Versions for GLM quotes that can be refused on an unseen level.

    uv run python scripts/sweep-unseen-levels.py [--dsn DSN] [--workspace UUID]

Run it BEFORE upgrading to the build that applies `unseen_level_behaviour` (`02` FR-2143). A GLM
`model_call` refuses a quote carrying a level of a categorical Factor that the model's fit never
saw, unless that Factor declares `map_to_base`. A version this sweep lists will refuse the quotes it
names until a new model is approved (a compiled version is never mutated: a Factor's declaration
changes only by a new Factor version, a refit and a new Rating Version). A batch carrying many such
rows can also abort above `rating.batch_abort_failure_rate`. The sweep recomputes everything from
each stored fit and the Factors, Bandings and Groupings its Bundle carries, so it needs nothing a
fit did not store. It reads one READ ONLY transaction and writes nothing. It prints **version
references and counts only**: never a level value, a hash or a quote value.

Output, in this order (a zero over an empty corpus is vacuous, so the denominators come first):

    versions: N            every Rating Version read
    with a bundle: M       those whose row names a bundle
    checked: K             those whose bundle was read and checked (M minus unreadable)
    unreadable: U
    glm refs read: G       GLM models read across the checked bundles
    <CLASS> <ref>          one line per version and class (below)
    UNREADABLE <ref> (<reason>)   one line per unreadable version (below)
    plain: .. not-reachable: .. null-level-unfitted: .. grouping-unfitted: ..
    interaction-unfitted: ..
    interaction-unfitted-lower-bound: .. no-relativities: .. not-examined-interaction: ..
    not-examined-other-family: n (families: ..)   versions pinning a model of another family
    NOTEXAMINED-CONTRACT n / NOTEXAMINED-GROUPING-SOURCE n   (what the sweep did not classify)

Each `model:` payload of a Bundle is classified by its `fit_result.model_type`:

    glm             validated with the GLM schema and examined as the classes below; a GLM payload
                    that fails validation makes its version UNREADABLE.
    another family  a family the fit-result union names (read from model-schema, not listed here):
                    not examined and counted on `not-examined-other-family`, never a finding. It
                    keeps FR-131's refusal whatever a Factor declares.
    anything else   an unknown `model_type`, a payload with no `fit_result` or with no
                    `model_type`: UNREADABLE.

Every UNREADABLE line carries the version reference and either the exception TYPE (for example
`ValidationError`) or a fixed reason word (`bundle-unparseable`, `no-fit-result`, `no-model-type`,
`unknown-model-type`): never the exception's text, a level or a value.

Classes (each counts versions; a version can carry several):

    PLAIN                   an IDENTITY categorical Factor with fitted relativities, declaring
                            nothing, that a quote can reach with a level the fit lacks, or that the
                            sweep cannot show it cannot (NOTEXAMINED-CONTRACT counts these).
    NOTREACHABLE            a version whose every such Factor is one no quote can bring an unseen
                            level to, each listed with a reason word; not a finding, not reachable:
                            `closed-input` = every model_call that scores the GLM is exact and
                            feeds the Factor only from a non-nullable enum input, read with
                            on_missing = error, produced by that one input node, whose domain lies
                            within THAT GLM's own fitted levels (checked per GLM, in every graph the
                            Bundle carries); `not-scored` = no model_call scores the GLM. Another
                            input type, a nullable input, an approximation call, a value from a step
                            or a second input stays PLAIN. A Peril Structure's components count as
                            scored by its call.
    NULLLEVEL               a Banding Factor whose Banding names a `null_level` the fit has no
                            relativity for: a missing or out-of-range quote reaches it.
    GROUPING                a Grouping Factor with a target level the fit has no relativity for.
    INTERACTION             an interaction with a producible cell the fit has no relativity for
                            (exact count: every operand's levels are listed).
    INTERACTION-LOWERBOUND  the same for an interaction with an IDENTITY operand: a floor, counting
                            only pairings of levels the fit saw separately and never together.
    NORELATIVITIES          a GLM with `slug[level]` terms whose slug has no `relativities` entry.
    NOTEXAMINED-INTERACTION an interaction the sweep cannot compute (a nested interaction, an
                            artifact not carried, a level holding the cell separator).
    NOTEXAMINED-NUMERIC-TERMS  an IDENTITY Factor with a dummy level that starts like a number or
                            that `float()` accepts after `strip()`, ANY such label (`3`, `3.0`,
                            `007`, `1.50`, `-.5`, `nan`, `inf`, `3+`, `25-39`). Whether a numeric
                            quote input can produce the label depends on that input's type (an int
                            produces `3` and not `3.0`; a float the reverse; neither produces `3+`):
                            a numeric input that cannot produce it refuses EVERY quote
                            (`MODEL_TERM_UNRESOLVED`). The input's type is carried by the Bundle
                            (`graph.input_contract`, with the `model_call`'s `feature_map`) but is
                            not classified here. So the count is a FLOOR on what the tool examined,
                            not a count of faults: these versions are COUNTED and listed, never
                            called clean or reachable.

A Factor declaring `map_to_base` is not a finding. NOTEXAMINED-GROUPING-SOURCE counts versions with
a Grouping Factor: how an unseen SOURCE level maps is the Grouping's own declared behaviour.

Exit code (a distinct non-zero for each condition; the first that applies wins):

    0   every version with a bundle was read, there is at least one, and none is reachable
    1   at least one version is reachable (any class above except NOTREACHABLE and NOTEXAMINED-*)
    2   a version's bundle could not be read: an unchecked version is not a clean one
    3   the corpus is empty (no version with a bundle): a zero over nothing is not a clean result
    64  usage (an argument error; argparse's own code 2 is mapped to this one)
    70  internal error: the sweep itself failed (an uncaught exception, printed as its TYPE only on
        stderr: never its text, which may carry a value). Never read 70 as clean or as reachable.

`2` wins over `3` and `1`; `3` wins over `1` only when there is nothing to be reachable.

The NOTREACHABLE and NOTEXAMINED lines are information: they never change the exit code.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any, TextIO, get_args

from model_schema import (
    FIT_RESULT_ADAPTER,
    Banding,
    Factor,
    FactorType,
    FitResult,
    GlmFitResult,
    Grouping,
    RatingModelCallStep,
    UnseenCellState,
    UnseenLevelBehaviour,
)
from pricing_core.modelling.glm import _unseen_cell_reports, _unseen_level_gaps
from pricing_core.rating.compile import Bundle, JdmGraph
from pricing_core.rating.runtime import _step_model_refs

_DUMMY = re.compile(r"^(?P<slug>.+)\[(?P<level>.*)\]$")
#: The classes that make a version reachable (exit code 1), in the order they are counted.
_REACHABLE = (
    "PLAIN", "NULLLEVEL", "GROUPING", "INTERACTION", "INTERACTION-LOWERBOUND", "NORELATIVITIES"
)
#: The class of a version whose every undeclared IDENTITY Factor with relativities is one no quote
#: can bring an unseen level to, each with a reason word (`NOTREACHABLE_REASONS`). Not reachable: it
#: does not change the exit code.
NOTREACHABLE = "NOTREACHABLE"
NOTREACHABLE_REASONS = ("closed-input", "not-scored")
_NOT_EXAMINED = (
    "NOTEXAMINED-INTERACTION", "NOTEXAMINED-GROUPING-SOURCE", "NOTEXAMINED-NUMERIC-TERMS"
)
#: A dummy level that starts like a number (`3`, `3.0`, `007`, `3+`, `25-39`): whether a numeric
#: quote input can produce it is `predict.py`'s numeric-level check, which needs the input's type.
_NUMERIC_LOOKING = re.compile(r"^[-+.]?\d")


def _number_like(label: str) -> bool:
    """A label is number-like if Python's `float()` accepts it after `strip()` (`-.5`, `+.5`,
    `nan`, `inf`, `-inf`, ` 1 `), or if it starts like a number (`3+`, `25-39`: band labels that
    `float()` refuses and that a numeric input cannot produce either)."""
    if _NUMERIC_LOOKING.match(label) is not None:
        return True
    try:
        float(label.strip())
    except ValueError:
        return False
    return True

EXIT_CLEAN, EXIT_REACHABLE, EXIT_UNREADABLE, EXIT_EMPTY = 0, 1, 2, 3
EXIT_USAGE, EXIT_INTERNAL = 64, 70


def _model_families() -> frozenset[str]:
    """Every `model_type` the fit-result union names, read from model-schema's discriminated union
    (the `Literal` of each member), never typed here."""
    union = get_args(FitResult)[0]
    return frozenset(
        value
        for member in get_args(union)
        for value in get_args(member.model_fields["model_type"].annotation)
    )


_FAMILIES = _model_families()


class _UnreadableError(Exception):
    """A model payload the sweep cannot classify. `reason` is a fixed word, never a value."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def _model_calls(bundle: Bundle) -> list[tuple[JdmGraph, RatingModelCallStep]]:
    """Every `model_call` node of the Bundle's graphs (the base graph and each purpose graph), with
    the graph it sits in, as the step the runtime reads (`_step_model_refs` takes that type)."""
    calls: list[tuple[JdmGraph, RatingModelCallStep]] = []
    for graph in (bundle.graph, *bundle.purpose_graphs.values()):
        for step_id, node in graph.nodes.items():
            if node.get("type") == "model_call":
                step = RatingModelCallStep.model_validate({**node, "step_id": step_id})
                calls.append((graph, step))
    return calls


def _fed_by_a_closed_input(
    graph: JdmGraph, call: RatingModelCallStep, slug: str, fitted_levels: set[str]
) -> bool:
    """True when `call` is an exact `model_call` and every name it maps to Factor `slug` is an
    input read with `on_missing` = error, produced by that one input node and by no other step,
    declared in the input contract as a non-nullable enum whose domain lies within
    `fitted_levels`. Anything else is not classified here (it stays PLAIN)."""
    if call.mode != "exact":
        return False
    names = [name for name, factor in call.feature_map.items() if factor == slug]
    if not names:
        return False
    contract = {c.get("name"): c for c in graph.input_contract}
    for name in names:
        producers = [n for n in graph.nodes.values() if name in n.get("produces", ())]
        if len(producers) != 1:
            return False
        node = producers[0]
        if node.get("type") != "input" or node.get("on_missing") != "error":
            return False
        entry = contract.get(node.get("input_name"))
        domain = None if entry is None else entry.get("domain")
        if (
            entry is None
            or entry.get("type") != "enum"
            or entry.get("nullable") is not False
            or not isinstance(domain, list)
            or not set(domain) <= fitted_levels
        ):
            return False
    return True


def _findings(bundle: Bundle) -> tuple[int, set[str], set[str], set[str]]:
    """The GLM models in `bundle`, the classes its fits and Factors fall into, the reason words of a
    NOTREACHABLE version, and the other model families it pins. Each `model:` payload is classified
    by its `fit_result.model_type`: `glm` is validated and examined; another family the fit-result
    union names is not examined (FR-131's refusal applies to it whatever a Factor declares);
    anything else raises `_UnreadableError`."""
    payloads = bundle.resolved_payloads
    all_factors = [
        Factor.model_validate(v) for k, v in payloads.items() if k.startswith("factor:")
    ]
    bandings = {
        b.id: b
        for b in (
            Banding.model_validate(v) for k, v in payloads.items() if k.startswith("banding:")
        )
    }
    groupings = {
        g.id: g
        for g in (
            Grouping.model_validate(v) for k, v in payloads.items() if k.startswith("grouping:")
        )
    }
    kinds: set[str] = set()
    other_families: set[str] = set()
    reasons: set[str] = set()
    glm_refs = 0
    calls = _model_calls(bundle)
    open_factor = False
    for key, payload in payloads.items():
        if not key.startswith("model:"):
            continue
        fit_result = payload.get("fit_result") if isinstance(payload, dict) else None
        if not isinstance(fit_result, dict):
            raise _UnreadableError("no-fit-result")
        model_type = fit_result.get("model_type")
        if not isinstance(model_type, str):
            raise _UnreadableError("no-model-type")
        if model_type != "glm":
            if model_type not in _FAMILIES:
                raise _UnreadableError("unknown-model-type")
            other_families.add(model_type)
            continue
        fit = FIT_RESULT_ADAPTER.validate_python(fit_result)
        if not isinstance(fit, GlmFitResult):
            raise _UnreadableError("unknown-model-type")
        glm_refs += 1
        wanted = {str(i) for i in payload.get("spec", {}).get("factors", ())}
        factors = [f for f in all_factors if not wanted or str(f.id) in wanted]
        undeclared = [
            f for f in factors if f.unseen_level_behaviour is not UnseenLevelBehaviour.MAP_TO_BASE
        ]
        fitted = {slug: {e.level for e in levels} for slug, levels in fit.relativities.items()}
        scoring = [
            (graph, call)
            for graph, call in calls
            if key in _step_model_refs(call, payloads)
        ]
        for slug in fitted:
            factor = next((f for f in undeclared if f.slug == slug), None)
            if factor is None or factor.type is not FactorType.IDENTITY:
                continue
            if not scoring:
                reasons.add("not-scored")
            elif all(
                _fed_by_a_closed_input(graph, call, slug, fitted[slug]) for graph, call in scoring
            ):
                reasons.add("closed-input")
            else:
                open_factor = True
        for gap in _unseen_level_gaps(fit.relativities, undeclared, bandings, groupings):
            reached = {r.value for r in gap.reached_by}
            kinds.add("GROUPING" if reached == {"grouping_target"} else "NULLLEVEL")
        if any(f.type is FactorType.GROUPING for f in factors):
            kinds.add("NOTEXAMINED-GROUPING-SOURCE")
        for report in _unseen_cell_reports(fit.relativities, undeclared, bandings, groupings):
            if report.state is UnseenCellState.NOT_EXAMINED:
                kinds.add("NOTEXAMINED-INTERACTION")
            elif (report.unfitted or 0) > 0:
                kinds.add(
                    "INTERACTION-LOWERBOUND"
                    if report.state is UnseenCellState.LOWER_BOUND
                    else "INTERACTION"
                )
        dummy_slugs = {
            m.group("slug") for c in fit.coefficients if (m := _DUMMY.match(c.term)) is not None
        }
        if dummy_slugs - fitted.keys():
            kinds.add("NORELATIVITIES")
        identity = {f.slug for f in factors if f.type is FactorType.IDENTITY}
        for coefficient in fit.coefficients:
            dummy = _DUMMY.match(coefficient.term)
            if (
                dummy is not None
                and dummy.group("slug") in identity
                and _number_like(dummy.group("level"))
            ):
                kinds.add("NOTEXAMINED-NUMERIC-TERMS")
                break
    if open_factor:
        kinds.add("PLAIN")
    elif reasons:
        kinds.add(NOTREACHABLE)
    return glm_refs, kinds, reasons, other_families


def sweep(versions: list[dict[str, Any]], out: TextIO) -> int:
    """Print the report for `versions` to `out` and return the exit code.

    A version dict is `{slug, version, status, bundle_hash, bundle}`; `bundle` is the parsed Bundle
    JSON, or `None` when the row has none to read (`bundle_hash` None: never compiled, not counted;
    `bundle_hash` set: a hash with no readable bundle, UNREADABLE).
    """
    with_bundle = [v for v in versions if v["bundle_hash"] is not None or v["bundle"] is not None]
    unreadable = glm_refs = other_versions = 0
    lines: list[str] = []
    other_families: set[str] = set()
    counts = {name: 0 for name in (*_REACHABLE, NOTREACHABLE, *_NOT_EXAMINED)}
    for each in with_bundle:
        ref = f"{each['slug']}@{each['version']} status={each['status']}"
        try:
            bundle = Bundle.model_validate(each["bundle"])
        except Exception:
            unreadable += 1
            lines.append(f"UNREADABLE {ref} (bundle-unparseable)")
            continue
        try:
            refs, kinds, reasons, others = _findings(bundle)
        except _UnreadableError as exc:
            unreadable += 1
            lines.append(f"UNREADABLE {ref} ({exc.reason})")
            continue
        except Exception as exc:
            # The exception's TYPE only: its text may carry a level or a value.
            unreadable += 1
            lines.append(f"UNREADABLE {ref} ({type(exc).__name__})")
            continue
        glm_refs += refs
        if others:
            other_versions += 1
            other_families |= others
        for kind in sorted(kinds):
            counts[kind] += 1
            if kind == NOTREACHABLE:
                lines.append(f"{kind} {ref} ({','.join(sorted(reasons))})")
            elif kind != "NOTEXAMINED-GROUPING-SOURCE":  # counted, not listed: it is a reason
                lines.append(f"{kind} {ref}")
    print(f"versions: {len(versions)}", file=out)
    print(f"with a bundle: {len(with_bundle)}", file=out)
    print(f"checked: {len(with_bundle) - unreadable}", file=out)
    print(f"unreadable: {unreadable}", file=out)
    print(f"glm refs read: {glm_refs}", file=out)
    for line in lines:
        print(line, file=out)
    print(f"plain: {counts['PLAIN']}", file=out)
    print(f"not-reachable: {counts[NOTREACHABLE]}", file=out)
    print(f"null-level-unfitted: {counts['NULLLEVEL']}", file=out)
    print(f"grouping-unfitted: {counts['GROUPING']}", file=out)
    print(f"interaction-unfitted: {counts['INTERACTION']}", file=out)
    print(
        f"interaction-unfitted-lower-bound: {counts['INTERACTION-LOWERBOUND']} "
        "(a floor: levels never seen at all are not counted)",
        file=out,
    )
    print(f"no-relativities: {counts['NORELATIVITIES']}", file=out)
    print(f"not-examined-interaction: {counts['NOTEXAMINED-INTERACTION']}", file=out)
    print(
        f"not-examined-other-family: {other_versions} (families: "
        f"{', '.join(sorted(other_families)) or 'none'}; a model of another family keeps "
        "FR-131's refusal whatever a Factor declares, so it is not examined here)",
        file=out,
    )
    print(
        f"NOTEXAMINED-CONTRACT {counts['PLAIN']} "
        "(PLAIN versions: an input that is open or not classified here feeds the Factor)",
        file=out,
    )
    print(
        f"NOTEXAMINED-NUMERIC-TERMS {counts['NOTEXAMINED-NUMERIC-TERMS']} "
        "(versions with an IDENTITY Factor whose dummy level starts like a number, any such label: "
        "a FLOOR on what the sweep examined, not a count of faults; whether a numeric quote input "
        "can produce the label depends on its type, which is not classified here)",
        file=out,
    )
    print(
        f"NOTEXAMINED-GROUPING-SOURCE {counts['NOTEXAMINED-GROUPING-SOURCE']} "
        "(versions with a Grouping Factor: an unseen source level maps by the Grouping's own "
        "declared behaviour, not swept here)",
        file=out,
    )
    if unreadable:
        return EXIT_UNREADABLE
    if not with_bundle:
        return EXIT_EMPTY
    return EXIT_REACHABLE if any(counts[name] for name in _REACHABLE) else EXIT_CLEAN


def _read_versions(dsn: str | None, workspace: str | None) -> list[dict[str, Any]]:
    """Every Rating Version, in ONE read-only transaction, by the stored-bundle sweep's reader."""
    path = Path(__file__).with_name("sweep-stored-bundles.py")
    spec = importlib.util.spec_from_file_location("sweep_stored_bundles", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    versions: list[dict[str, Any]] = asyncio.run(module._read_versions(dsn, workspace))
    return versions


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
    parser.add_argument("--dsn", help="a READ-ONLY database URL (default: the app's settings)")
    parser.add_argument("--workspace", help="one workspace id (default: all)")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse exits 2 on a usage error, which this script's contract gives to "unreadable".
        return 0 if exc.code in (0, None) else EXIT_USAGE
    try:
        return sweep(_read_versions(args.dsn, args.workspace), sys.stdout)
    except Exception as exc:
        # An uncaught exception would exit 1, the code for "a version is reachable". Print the
        # type only (never its text, which may carry a value) and exit with its own code.
        print(f"internal error: {type(exc).__name__}", file=sys.stderr)
        return EXIT_INTERNAL


if __name__ == "__main__":
    sys.exit(_main())
