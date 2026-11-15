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
    plain: .. null-level-unfitted: .. grouping-unfitted: .. interaction-unfitted: ..
    interaction-unfitted-lower-bound: .. no-relativities: .. not-examined-interaction: ..
    NOTEXAMINED-CONTRACT n / NOTEXAMINED-GROUPING-SOURCE n   (what the sweep did not classify)

Classes (each counts versions; a version can carry several):

    PLAIN                   an IDENTITY categorical Factor with fitted relativities, declaring
                            nothing. An UPPER BOUND: whether the quote's input contract is a closed
                            enum over the fitted levels is not classified (NOTEXAMINED-CONTRACT).
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
    1   at least one version is reachable (any class above except NOTEXAMINED-*)
    2   a version's bundle could not be read: an unchecked version is not a clean one
    3   the corpus is empty (no version with a bundle): a zero over nothing is not a clean result
    64  usage (an argument error; argparse's own code 2 is mapped to this one)
    70  internal error: the sweep itself failed (an uncaught exception, printed as its TYPE only on
        stderr: never its text, which may carry a value). Never read 70 as clean or as reachable.

`2` wins over `3` and `1`; `3` wins over `1` only when there is nothing to be reachable.

The NOTEXAMINED lines are information: they never change the exit code.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any, TextIO

from model_schema import (
    FIT_RESULT_ADAPTER,
    Banding,
    Factor,
    FactorType,
    GlmFitResult,
    Grouping,
    UnseenCellState,
    UnseenLevelBehaviour,
)
from pricing_core.modelling.glm import _unseen_cell_reports, _unseen_level_gaps
from pricing_core.rating.compile import Bundle

_DUMMY = re.compile(r"^(?P<slug>.+)\[(?P<level>.*)\]$")
#: The classes that make a version reachable (exit code 1), in the order they are counted.
_REACHABLE = (
    "PLAIN", "NULLLEVEL", "GROUPING", "INTERACTION", "INTERACTION-LOWERBOUND", "NORELATIVITIES"
)
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


def _findings(bundle: Bundle) -> tuple[int, set[str]]:
    """The GLM models in `bundle` and the classes its fits and Factors fall into."""
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
    glm_refs = 0
    for key, payload in payloads.items():
        if not key.startswith("model:") or "fit_result" not in payload:
            continue
        fit = FIT_RESULT_ADAPTER.validate_python(payload["fit_result"])
        if not isinstance(fit, GlmFitResult):
            continue
        glm_refs += 1
        wanted = {str(i) for i in payload.get("spec", {}).get("factors", ())}
        factors = [f for f in all_factors if not wanted or str(f.id) in wanted]
        undeclared = [
            f for f in factors if f.unseen_level_behaviour is not UnseenLevelBehaviour.MAP_TO_BASE
        ]
        fitted = {slug: {e.level for e in levels} for slug, levels in fit.relativities.items()}
        for slug in fitted:
            factor = next((f for f in undeclared if f.slug == slug), None)
            if factor is not None and factor.type is FactorType.IDENTITY:
                kinds.add("PLAIN")
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
    return glm_refs, kinds


def sweep(versions: list[dict[str, Any]], out: TextIO) -> int:
    """Print the report for `versions` to `out` and return the exit code.

    A version dict is `{slug, version, status, bundle_hash, bundle}`; `bundle` is the parsed Bundle
    JSON, or `None` when the row has none to read (`bundle_hash` None: never compiled, not counted;
    `bundle_hash` set: a hash with no readable bundle, UNREADABLE).
    """
    with_bundle = [v for v in versions if v["bundle_hash"] is not None or v["bundle"] is not None]
    unreadable = glm_refs = 0
    lines: list[str] = []
    counts = {name: 0 for name in (*_REACHABLE, *_NOT_EXAMINED)}
    for each in with_bundle:
        ref = f"{each['slug']}@{each['version']} status={each['status']}"
        try:
            bundle = Bundle.model_validate(each["bundle"])
            refs, kinds = _findings(bundle)
        except Exception:
            unreadable += 1
            lines.append(f"UNREADABLE {ref}")
            continue
        glm_refs += refs
        for kind in sorted(kinds):
            counts[kind] += 1
            if kind != "NOTEXAMINED-GROUPING-SOURCE":  # counted, not listed: it is a reason
                lines.append(f"{kind} {ref}")
    print(f"versions: {len(versions)}", file=out)
    print(f"with a bundle: {len(with_bundle)}", file=out)
    print(f"checked: {len(with_bundle) - unreadable}", file=out)
    print(f"unreadable: {unreadable}", file=out)
    print(f"glm refs read: {glm_refs}", file=out)
    for line in lines:
        print(line, file=out)
    print(f"plain: {counts['PLAIN']}", file=out)
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
        f"NOTEXAMINED-CONTRACT {counts['PLAIN']} "
        "(PLAIN is an upper bound: closed-enum input contracts are not classified here)",
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
