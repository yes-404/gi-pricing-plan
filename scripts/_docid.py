"""Shared header parser and id grammar for NT-0019's document-id standard.

`docs/notes/0019-one-id-per-document.md` §1.1, §1.2, §1.5. Owned by W37-2
(`docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`); `scripts/doc-id.py` and
`scripts/doc-index.py` (W37-3) import this module and do not redefine any of it — it is
the one place the id grammar and the header's closed field set are stated.

**Standard library only** (G4 / DP-5): `.github/workflows/docs.yml` runs
`scripts/audit-docs.py` with no dependency-install step, so nothing under `scripts/` that
feeds that workflow may import a third-party package. The header is YAML front matter in
*form* only — NT-0019 §1.5's field set is closed and flat (scalars, `[a, b]` lists, `~` for
null), so a hand-rolled parser over exactly that grammar is a feature, not a shortcut: it
rejects anything PyYAML would silently accept (a nested mapping, an anchor, a tag) that the
standard does not use.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Final

# NT-0019 §1.2a — five words, identical meaning in every family that uses a subset of them.
STATUS_WORDS: Final = ("draft", "active", "closed", "retired", "superseded")

# NT-0019 §1.2's family table, row families first then document families, left to right,
# top to bottom as the table itself lists them.
FAMILY_PREFIXES: Final = (
    "FR", "NFR", "DEP", "OQ", "WK", "SL", "WF",
    "ADR", "RFC", "PL", "LG", "RL", "RS", "CR", "FD",
)

# NT-0019 §1.7: "the resolver is `\b(FR|NFR|DEP|OQ|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0*(\d+)\b`
# with a check that the prefix matches the family the number belongs to." Quoted verbatim
# rather than built from FAMILY_PREFIXES: the note fixes this exact pattern as the citation
# resolver, and a generated version could silently reorder the alternation (regex
# alternation order can change which of two overlapping prefixes wins, though none overlap
# here) without anyone having decided that.
ID_RE: Final = re.compile(r"\b(FR|NFR|DEP|OQ|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0*(\d+)\b")

# NT-0019 §1.1 rule 3: "Filenames pad the integer to the standard's width, currently five."
PAD_WIDTH: Final = 5

# NT-0019 §1.2's "Kind" column, lowercased, keyed by prefix. What never changes on
# extension (§1.12): a new family adds a row here via an RFC-/RL-, this table is not
# reopened for any other reason.
_FAMILY_OF: Final[Mapping[str, str]] = {
    "FR": "requirement",
    "NFR": "requirement",
    "DEP": "requirement",
    "OQ": "open question",
    "WK": "work",
    "SL": "slice",
    "WF": "workflow",
    "ADR": "decision",
    "RFC": "proposal",
    "PL": "plan",
    "LG": "ledger",
    "RL": "ruling",
    "RS": "research",
    "CR": "closure",
    "FD": "finding",
}


class HeaderError(Exception):
    """Malformed front matter, an unknown field, or a field of the wrong shape.

    Carries the path and the 1-based line number in its message.
    """


@dataclass(frozen=True)
class Header:
    """One document's (or row's) parsed front matter — NT-0019 §1.5's closed field set."""

    id: str | None
    family: str
    kind: str | None
    title: str
    status: str
    created: date | None
    owner: str
    phase: str | None
    work: str | None
    slice_: str | None
    tree: str | None
    plans: tuple[str, ...]
    supersedes: tuple[str, ...]
    superseded_by: str | None
    corrected_by: tuple[str, ...]
    corrects: str | None
    relates: tuple[str, ...]
    was: str | None
    vendored: bool
    origin: str | None
    extra: Mapping[str, str]


def canonical(prefix: str, n: int) -> str:
    """The citation form — NT-0019 §1.1 rule 2: unpadded, always. `canonical("PL", 1240)`
    -> `"PL-1240"`.
    """
    return f"{prefix}-{n}"


def padded(prefix: str, n: int, width: int = PAD_WIDTH) -> str:
    """The filename form — NT-0019 §1.1 rule 3: padded to `width` (never truncated below
    the number's own length). `padded("PL", 1240)` -> `"PL-01240"`.
    """
    return f"{prefix}-{n:0{width}d}"


def family_of(prefix: str) -> str:
    """The family word NT-0019 §1.2's "Kind" column gives `prefix`, lowercased.

    Raises `ValueError` naming the prefix for anything not in `FAMILY_PREFIXES` — a
    product identifier (`VR-...`) or a typo, never a silent guess (D5, G5).
    """
    try:
        return _FAMILY_OF[prefix]
    except KeyError:
        raise ValueError(f"{prefix!r} is not a governed-thing family prefix") from None


# Scalar fields that stay strings (default "" when absent — required-ness is a per-family
# policy a caller checks, e.g. audit-docs check 30; this parser only reports what it found).
_STR_FIELDS: Final = ("family", "title", "status", "owner")
# Scalar fields that are `str | None` (default None when absent or `~`).
_OPTIONAL_STR_FIELDS: Final = (
    "id", "kind", "phase", "work", "tree", "superseded_by", "corrects", "was", "origin",
)
# List fields — `[a, b]` or `[]`; default `()` when absent.
_LIST_FIELDS: Final = ("plans", "supersedes", "corrected_by", "relates")
_KNOWN_KEYS: Final = frozenset(
    (*_STR_FIELDS, *_OPTIONAL_STR_FIELDS, *_LIST_FIELDS, "slice", "created", "vendored")
)

_KEY_VALUE_RE: Final = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]?(.*)$")
_LIST_ITEM_RE: Final = re.compile(r"^\[(.*)\]$")


def _strip_inline_comment(value: str) -> str:
    """Drop a trailing `  # comment` — the header examples in NT-0019 §1.5 carry one on
    almost every line. A `#` is only ever a comment marker here because the closed grammar
    has no quoted-string field whose value legitimately contains one; a bare split on the
    first ` #` is exact for that grammar, not an approximation of full YAML.
    """
    idx = value.find(" #")
    return value if idx == -1 else value[:idx]


def _parse_scalar(raw: str) -> str | None:
    value = _strip_inline_comment(raw).strip()
    if value == "~" or value == "":
        return None
    return value


def _parse_list(raw: str, *, path: Path, line_no: int) -> tuple[str, ...]:
    value = _strip_inline_comment(raw).strip()
    match = _LIST_ITEM_RE.match(value)
    if match is None:
        raise HeaderError(f"{path}:{line_no}: not a well-formed `[a, b]` list: {raw!r}")
    inner = match.group(1).strip()
    if not inner:
        return ()
    return tuple(item.strip() for item in inner.split(","))


def _parse_front_matter_body(
    lines: list[str], *, path: Path, first_line_no: int
) -> dict[str, object]:
    """Parse the flat `key: value` lines of one front-matter block into a plain dict,
    keyed by the YAML key exactly as written (`slice`, not `slice_`) — NT-0019 §1.5's
    closed grammar: scalars, `[a, b]` lists, `~` for null, nothing nested.

    Raises `HeaderError` naming `path` and the 1-based line number for a duplicate key, a
    line with no `key: value` shape, an unterminated list, or (via `_parse_created`) a
    malformed date.
    """
    result: dict[str, object] = {}
    for offset, raw_line in enumerate(lines):
        line_no = first_line_no + offset
        if not raw_line.strip():
            continue
        if raw_line[:1] in (" ", "\t"):
            raise HeaderError(
                f"{path}:{line_no}: indented line — nested mappings are not in the "
                f"closed field set (NT-0019 §1.5): {raw_line!r}"
            )
        match = _KEY_VALUE_RE.match(raw_line)
        if match is None:
            raise HeaderError(f"{path}:{line_no}: not a `key: value` line: {raw_line!r}")
        key, raw_value = match.group(1), match.group(2)
        if key in result:
            raise HeaderError(f"{path}:{line_no}: duplicate key {key!r}")
        if key == "created":
            scalar = _parse_scalar(raw_value)
            if scalar is None:
                result[key] = None
                continue
            try:
                year, month, day = (int(part) for part in scalar.split("-"))
                result[key] = date(year, month, day)
            except (ValueError, TypeError) as exc:
                raise HeaderError(
                    f"{path}:{line_no}: `created` is not an ISO date (YYYY-MM-DD): "
                    f"{scalar!r}"
                ) from exc
        elif key == "vendored":
            scalar = _parse_scalar(raw_value)
            result[key] = scalar == "true"
        elif key in _LIST_FIELDS:
            result[key] = _parse_list(raw_value, path=path, line_no=line_no)
        else:
            result[key] = _parse_scalar(raw_value)
    return result


def _str_field(body: Mapping[str, object], key: str) -> str:
    value = body.get(key)
    return value if isinstance(value, str) else ""


def _opt_str_field(body: Mapping[str, object], key: str) -> str | None:
    value = body.get(key)
    return value if isinstance(value, str) else None


def _tuple_field(body: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = body.get(key)
    return value if isinstance(value, tuple) else ()


def _date_field(body: Mapping[str, object], key: str) -> date | None:
    value = body.get(key)
    return value if isinstance(value, date) else None


def _bool_field(body: Mapping[str, object], key: str) -> bool:
    return body.get(key) is True


def parse_header(path: Path) -> Header | None:
    """Parse the YAML-front-matter-shaped header at the top of `path`.

    Returns `None` when the file has no front-matter block at all (its first line is not
    exactly `---`) — most files in this repository today, pre-migration (W37-6), and that
    is a legitimate, common state rather than an error.

    Raises `HeaderError`, naming `path` and a 1-based line number, when a front-matter
    block is present but does not fit NT-0019 §1.5's closed grammar: an unterminated
    block, a duplicate key, an indented (nested) line, a malformed list, or a malformed
    `created` date.

    A key outside the closed field set is not an error here — it lands in `.extra`
    verbatim. Whether a given extra is *permitted* for this file's family (§1.5: "declared
    in that family's template and permitted only there") is a family-aware policy check
    (`audit-docs.py` check 30), not this generic parser's to enforce.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if not lines or lines[0] != "---":
        return None
    try:
        closing = lines.index("---", 1)
    except ValueError:
        raise HeaderError(f"{path}:1: front-matter block has no closing `---`") from None

    body = _parse_front_matter_body(lines[1:closing], path=path, first_line_no=2)

    extra: dict[str, str] = {
        key: "" if value is None else str(value)
        for key, value in body.items()
        if key not in _KNOWN_KEYS
    }

    return Header(
        id=_opt_str_field(body, "id"),
        family=_str_field(body, "family"),
        kind=_opt_str_field(body, "kind"),
        title=_str_field(body, "title"),
        status=_str_field(body, "status"),
        created=_date_field(body, "created"),
        owner=_str_field(body, "owner"),
        phase=_opt_str_field(body, "phase"),
        work=_opt_str_field(body, "work"),
        slice_=_opt_str_field(body, "slice"),
        tree=_opt_str_field(body, "tree"),
        plans=_tuple_field(body, "plans"),
        supersedes=_tuple_field(body, "supersedes"),
        superseded_by=_opt_str_field(body, "superseded_by"),
        corrected_by=_tuple_field(body, "corrected_by"),
        corrects=_opt_str_field(body, "corrects"),
        relates=_tuple_field(body, "relates"),
        was=_opt_str_field(body, "was"),
        vendored=_bool_field(body, "vendored"),
        origin=_opt_str_field(body, "origin"),
        extra=extra,
    )


# Ruling 69 (`docs/plans/2026-09-02-w37-migration-preconditions-rulings.md`, PR #563,
# merged): NT-0019 §1.5's parenthetical, naming `planning-with-files`, `ui-ux-pro-max`,
# `graphify`, `systematic-debugging` and the `vue-*` skills as vendored while giving "a
# directory that provides a `LICENSE` of its own" as the reason, is a gloss identifying
# which skills the note's author had in mind, not a specification of a detector: it is
# wrong about three of its own five named examples (`graphify`, `systematic-debugging`,
# every `vue-*` skill provides no such file) and about 26 of the repository's 28.
# `vendored` is declared and reconciled, never detected. This is the hand-kept enumeration,
# seeded from
# `.claude/skills/README.md`'s provenance sections — the record `CLAUDE.md` §12 makes
# authoritative for what is vendored — and reconciled against `pyproject.toml`'s
# `[tool.ruff] exclude` list by `vendored_skills_ruff_exclude_mismatch` below, which is
# the independent second witness, never the criterion itself: adopting the ruff list
# outright is Ruling 69's other rejected option, because nine of its 28 entries carry a
# deliberate NT-0019 §5.4 edit and two of those (`writing-plans`,
# `subagent-driven-development`) are creating instruments Ruling 66 requires inside the
# migration commit — treating ruff-exclusion itself as "vendored" would exempt them from
# the very migration that must carry them. Extending this set is a deliberate edit,
# recorded in `.claude/skills/README.md` in the same commit (Ruling 69 §2 part 3), never a
# rename this constant discovers on its own.
_VENDORED_SKILLS: Final[frozenset[str]] = frozenset({
    "brainstorming",
    "code-quality",
    "create-adaptable-composable",
    "dispatching-parallel-agents",
    "executing-plans",
    "finishing-a-development-branch",
    "graphify",
    "planning-with-files",
    "receiving-code-review",
    "reproducing-ci-locally",
    "requesting-code-review",
    "secret-hygiene",
    "security-audit",
    "subagent-driven-development",
    "systematic-debugging",
    "test-driven-development",
    "testing-strategy",
    "ui-ux-pro-max",
    "using-git-worktrees",
    "using-superpowers",
    "verification-before-completion",
    "vue-best-practices",
    "vue-debug-guides",
    "vue-pinia-best-practices",
    "vue-router-best-practices",
    "vue-testing-best-practices",
    "writing-plans",
    "writing-skills",
})


def is_vendored(path: Path, repo_root: Path) -> bool:
    """True when `path` sits beneath a directory named in `_VENDORED_SKILLS` directly
    under `.claude/skills/` — NT-0019 §1.5's vendored-skill exemption, as Ruling 69
    resolved it (see the comment above `_VENDORED_SKILLS`): a membership test against a
    declared constant, never a filesystem probe.

    This function's signature is unchanged from the published contract W37-3 and W37-4
    import (Ruling 69 §2 part 4) — only the body changed, from walking the filesystem
    for a `LICENSE` file to testing set membership.

    `path` may be a file or a directory, absolute or relative to `repo_root`; both are
    resolved before comparison, so the two forms behave identically and a symlink is
    followed rather than compared literally. Returns `False` for anything not under
    `repo_root/.claude/skills/<name>` — including `repo_root` itself, a file elsewhere in
    the repository (there is no more special case for the repository's own root
    `LICENSE`: nothing here inspects any `LICENSE` file, so there is nothing for it to be
    mistaken for), and a path outside `repo_root` entirely.
    """
    try:
        rel_parts = path.resolve().relative_to(repo_root.resolve()).parts
    except ValueError:
        return False  # not under repo_root at all
    if len(rel_parts) < 3 or rel_parts[0] != ".claude" or rel_parts[1] != "skills":
        return False
    return rel_parts[2] in _VENDORED_SKILLS


def vendored_skills_ruff_exclude_mismatch(
    repo_root: Path,
) -> tuple[frozenset[str], frozenset[str]]:
    """Ruling 69 §2 part 2's reconciliation: `_VENDORED_SKILLS` against `repo_root`'s
    `pyproject.toml`'s `[tool.ruff] exclude` list, restricted to the `.claude/skills/<name>`
    entries — the independent second witness the ruling requires, never the criterion
    itself (`is_vendored`'s docstring, and the comment above `_VENDORED_SKILLS`, both say
    why the ruff list is not adopted outright: it over-exempts two of Ruling 66's creating
    instruments).

    Returns `(only_in_constant, only_in_ruff)`. Both empty means the two agree — this is
    the passing case, and it is what the real repository must show today. Either side
    non-empty is drift, and the caller must fail loudly naming which side moved (Ruling 69
    acceptance item 1) rather than silently trusting one source over the other.

    Reads `repo_root/pyproject.toml` fresh on every call, with `tomllib` (standard
    library — this module's own docstring, G4/DP-5, is why nothing here may import a
    third-party TOML parser) rather than caching the ruff list at import time, so a test
    can point this at a synthetic `pyproject.toml` under `tmp_path` without needing to
    reload this module. Indexes `config["tool"]["ruff"]["exclude"]` directly rather than
    `.get`-chaining to a default: a moved or renamed key must raise, the same "fail loud"
    the reconciliation itself exists to provide — a silent empty list here would read as
    "ruff excludes nothing", which is drift in exactly the direction this function must
    never hide.
    """
    config = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    exclude = config["tool"]["ruff"]["exclude"]
    prefix = ".claude/skills/"
    ruff_skills = frozenset(
        entry[len(prefix) :] for entry in exclude
        if isinstance(entry, str) and entry.startswith(prefix)
    )
    return _VENDORED_SKILLS - ruff_skills, ruff_skills - _VENDORED_SKILLS


# ---------------------------------------------------------------------------------------
# Template readers — Rulings 79 and 80
# (`docs/plans/2026-09-02-w37-template-parser-conflicts-rulings.md`). Both rulings settle
# the same way: a family's own template under `docs/_templates/` is the licensing
# instrument (Ruling 70 §2 item 1), never a hand-written constant in a reader. Kept here,
# not in `scripts/doc-index.py`, so `scripts/doc-id.py` (the row/phase *writer*,
# `migrate`) and `scripts/doc-index.py` (the *reader*) derive from one definition apiece
# and cannot silently disagree — both already import this module and neither imports the
# other (Ruling 79 §3 item 2: "the reader must not become a third transcription").
# ---------------------------------------------------------------------------------------

#: The two row families (NT-0019 §1.5): a `WK-`/`SL-` row's header is a fenced ```yaml
#: block under the row's own heading, never the file's own front matter. Keyed by family
#: word, the convention `scripts/audit-docs.py`'s `_TEMPLATE_FAMILY` already uses for a
#: template's filename.
ROW_TEMPLATE_FILES: Final[Mapping[str, str]] = {"work": "WK.md", "slice": "SL.md"}

_TEMPLATE_LEADING_COMMENT_RE: Final = re.compile(r"\A<!--.*?-->\n?\n?", re.DOTALL)
_TEMPLATE_FENCED_YAML_RE: Final = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
_TEMPLATE_KEY_RE: Final = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")


def row_template_fields(templates_dir: Path, family: str) -> frozenset[str]:
    """The permitted field set for a `WK-`/`SL-` row, derived from that family's own
    template's fenced ```yaml block (Ruling 79 §3 item 1) — Ruling 70 §2 item 1's "the
    permitted set for a family is the set of keys in that family's template front matter",
    applied to a row's fenced block, which is what a `WK-`/`SL-` row carries in place of a
    document's own top-level front matter (NT-0019 §1.5).

    Raises `ValueError` naming `family` for anything not a row family — a document
    family's field policy is `scripts/audit-docs.py`'s `derive_field_policies` to compute,
    never this function's; and for `templates_dir` when the named template is missing or
    carries no fenced block at all, rather than deriving a silently smaller policy from
    whatever happened to be found (the same "silent empty coverage must be impossible"
    property `derive_field_policies` already enforces for the other twelve templates,
    Ruling 70 §4 item 3).
    """
    try:
        filename = ROW_TEMPLATE_FILES[family]
    except KeyError:
        raise ValueError(
            f"{family!r} is not a row family ({sorted(ROW_TEMPLATE_FILES)})"
        ) from None
    path = templates_dir / filename
    text = path.read_text(encoding="utf-8")
    stripped = _TEMPLATE_LEADING_COMMENT_RE.sub("", text, count=1)
    match = _TEMPLATE_FENCED_YAML_RE.search(stripped)
    if match is None:
        raise ValueError(f"{path}: no fenced ```yaml block found")
    fields: set[str] = set()
    for line in match.group(1).splitlines():
        if not line.strip() or line[:1] in (" ", "\t"):
            continue
        key_match = _TEMPLATE_KEY_RE.match(line)
        if key_match:
            fields.add(key_match.group(1))
    if not fields:
        raise ValueError(f"{path}: fenced ```yaml block carries no 'key:' field")
    return frozenset(fields)


def scan_plain_field_block(lines: Sequence[str], start: int) -> dict[str, str]:
    """The plain `key: value` lines directly beneath a heading at `lines[start - 1]` —
    NT-0019's phase-section grammar (§1.1 rule 4, §1.3; `docs/_templates/PHASE.md`'s own
    words: "not built from the closed header field set of §1.5"), the one block form
    §1.5's closed, fenced grammar does not govern (Ruling 80 §2).

    A bounded scan of `lines[start:]`, stopping at the next heading (any line starting
    with `#`) or a blank line, whichever comes first (Ruling 80 §3 item 1: "stopping at
    the next heading or the first line that is not key: value" — a blank line is such a
    line). A non-blank *indented* line is read as a continuation of the field above it —
    the same signal NT-0019 §1.5's own closed grammar treats as "not a new key" (there, by
    raising; this grammar has no hard-error concept, so it is tolerated instead) — and is
    skipped without stopping the scan; a non-blank, non-indented line with no `:` does
    stop it. Deliberately **not** `_parse_front_matter_body`'s indented-line rule reused
    verbatim: that grammar rejects a continuation outright, because §1.5 requires knowing
    a document is malformed; this one only needs to know where the field block ends, and
    `docs/_templates/PHASE.md`'s own `exit criteria:` placeholder wraps onto an indented
    second line in the committed template (a pre-existing defect independent of both
    rulings, reported alongside them rather than fixed here — see the PR description).

    Used identically by `scripts/doc-index.py`'s `scan_phase_sections` (a real roadmap's
    phase section) and this module's own `phase_template_fields` (`PHASE.md`'s own body)
    so the two cannot silently disagree about where a phase section's field block ends.

    Unbounded by design in the *other* direction that matters: `lines` is whatever the
    caller already sliced to `start` onward — this function itself never looks past a
    heading or a blank line, which is the fix for `scripts/doc-index.py`'s former `rest =
    "\n".join(lines[idx + 1:])` (Ruling 80 §3 item 2: "must not survive the fix in any
    form").
    """
    raw: dict[str, str] = {}
    for line in lines[start:]:
        if not line.strip():
            break
        if line.strip().startswith("#"):
            break
        if line[:1] in (" ", "\t"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            break
        raw[key.strip()] = value.split("#", 1)[0].strip()
    return raw


def phase_template_fields(templates_dir: Path) -> frozenset[str]:
    """The field names NT-0019's phase section declares, read from `docs/_templates/
    PHASE.md`'s own body — never transcribed (Ruling 80 §3 item 3): matches today
    (`("status", "opened", "target", "gates", "exit criteria", "works")`), so this is
    hardening, not repair.

    Raises `ValueError` naming `templates_dir` when `PHASE.md` carries no `##` heading, or
    the heading has no plain field directly beneath it — "silent empty coverage must be
    impossible" (Ruling 70 §4 item 3), applied here to the one template
    `scripts/audit-docs.py`'s `derive_field_policies` deliberately excludes (a phase has
    no family).
    """
    path = templates_dir / "PHASE.md"
    text = path.read_text(encoding="utf-8")
    stripped = _TEMPLATE_LEADING_COMMENT_RE.sub("", text, count=1)
    lines = stripped.splitlines()
    heading_idx = next(
        (i for i, line in enumerate(lines) if line.strip().startswith("##")), None
    )
    if heading_idx is None:
        raise ValueError(f"{path}: no '##' phase heading found")
    fields = scan_plain_field_block(lines, heading_idx + 1)
    if not fields:
        raise ValueError(
            f"{path}: no plain 'key: value' field found directly beneath the phase "
            "heading"
        )
    return frozenset(fields)
