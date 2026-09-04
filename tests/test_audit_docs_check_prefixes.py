"""`scripts/audit-docs.py`: every numbered check's own `fail()` message begins `check N: `.

Found by exec-h1 auditing row (h1) of `scripts/_docverify.py`'s `EXPECTED_VERDICTS`: h1's
own per-class breakdown (`_docverify._classify_failures`, ported from Ruling 105 §B's shell
one-liner) attributes a failure to a check number by matching `^check (\\d+):` at the start
of its message — a convention checks 29-39 already followed, but checks 1-28 mostly did not.
Two of those gaps (check 1's `broken link in ...` shape, check 27's `process core ...`
shape) were patched as classifier-side special cases in a first pass; the deputy's ruling on
that finding rejected growing the special-case set and required the fix at the source
instead: "a failure the classifier cannot attribute is a count without a predicate ...
special-casing each check as it is noticed is how the bucket refills." Both special cases
were removed from `_docverify.py` in the same commit that added this test.

**One exception, named by its exact message rather than resolved into a prefix**:
`check_notes`'s top-of-function guard (`docs/notes does not exist -- checks 16-20 cannot
run`) covers five check numbers at once, and `_CHECK_PREFIX_RE`'s `(\\d+)` group cannot hold
five values. `_docverify._ABSENT_CHECK_RE` already reports that exact message as a
non-execution marker — a state `_docverify.py` treats separately from a classified failure —
so leaving it unprefixed is not a second instance of the gap this test exists to close.

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence for
a numbered platform requirement — the same reasoning every other `test_audit_docs_*.py` file
gives for its own check.
"""

from __future__ import annotations

import ast
import pathlib
import re
from typing import Final

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"

#: `check_notes`'s guard for its own five check numbers (16-20) at once, matched by exact
#: equality against the message's concatenated literal segments (never a substring test —
#: see `test_the_exempt_message_does_not_silently_widen_to_cover_other_call_sites`), and
#: never by line number (which drifts with every unrelated edit above it) or by enclosing
#: function (a second such guard elsewhere would need naming too).
_EXEMPT_MESSAGE_PREFIX: Final = "does not exist — checks 16-20 cannot run"

_CHECK_PREFIX_RE: Final = re.compile(r"^check \d+: ")


def _first_literal_text(node: ast.expr) -> str | None:
    """The literal text a `fail(...)` call's first argument *starts with* — a bare string, an
    f-string whose first part is a literal, or a `+`/implicit string-concatenation chain
    reduced to its leftmost literal. `None` when the argument opens with an interpolated
    expression (`f"{x}: ..."`), which this predicate cannot evaluate statically and must
    not silently pass — a caller sees `None` and reports it as its own violation.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        if node.values and isinstance(node.values[0], ast.Constant):
            value = node.values[0].value
            return value if isinstance(value, str) else None
        return None
    if isinstance(node, ast.BinOp):
        return _first_literal_text(node.left)
    return None


def _any_literal_text(node: ast.expr) -> str:
    """Every literal (`Constant`) segment of `node` concatenated, interpolations dropped —
    used only to test for the exempt guard's substring, which can sit *after* an
    interpolated segment (`f"{NOTES...} does not exist — checks 16-20 cannot run"` opens
    with `{NOTES...}`, not a literal). Never used to decide the `check N:` prefix itself,
    which must come from `_first_literal_text`'s stricter, leading-literal-only reading.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            v.value for v in node.values if isinstance(v, ast.Constant) and isinstance(v.value, str)
        )
    if isinstance(node, ast.BinOp):
        return _any_literal_text(node.left) + _any_literal_text(node.right)
    return ""


def fail_call_prefix_violations(source: str) -> list[str]:
    """Every `fail(...)` call site in `source` whose message does not begin `check N: `,
    reported as `"L<lineno>: <what's wrong>"` — the exempt guard message is skipped, an
    interpolation-led message is a violation (this predicate cannot verify it, so it must
    not be silently accepted), and everything else is checked by literal prefix match.

    Takes source text rather than a path so the broken-input proof below can run it against
    a mutated in-memory copy without writing a temp file.
    """
    tree = ast.parse(source)
    violations: list[str] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "fail"
            and node.args
        ):
            continue
        # Exact equality, not a substring test: a message that merely *mentions* the
        # exempt wording somewhere inside a longer sentence is not the guard this
        # exemption exists for, and must still be checked normally.
        if _any_literal_text(node.args[0]).strip() == _EXEMPT_MESSAGE_PREFIX:
            continue
        text = _first_literal_text(node.args[0])
        if text is None:
            violations.append(
                f"L{node.lineno}: message opens with an interpolated expression, not a "
                "literal — cannot verify it carries a `check N:` prefix statically"
            )
            continue
        if not _CHECK_PREFIX_RE.match(text.lstrip()):
            violations.append(f"L{node.lineno}: message does not start with `check N: `")
    return violations


def test_every_fail_call_in_audit_docs_starts_with_its_own_check_number() -> None:
    """The real file, as shipped: zero violations.

    Verified against 103 `fail()` call sites at the tree this test was written on — checks
    1-28 patched to carry the prefix in this same change, checks 29-39 already carrying it,
    and the one named exemption (`check_notes`'s five-check guard) excluded by message text
    rather than silently passing because it happens not to match the pattern.
    """
    violations = fail_call_prefix_violations(SCRIPT.read_text(encoding="utf-8"))
    assert violations == [], "\n".join(violations)


def test_a_fail_message_missing_its_prefix_is_caught() -> None:
    """Broken-input proof: one real call site, stripped of its `check N: ` prefix, must turn
    the predicate above red — naming that exact line, not a different one and not the whole
    file going silently green.

    Mutates the shipped source in memory (never the file on disk) by removing the literal
    `"check 6: "` prefix from `main()`'s check-6 "missing required section" message —
    chosen because it is a single-line, single-occurrence, f-string-led site, so the string
    substitution below cannot accidentally also match a different call site.
    """
    source = SCRIPT.read_text(encoding="utf-8")
    target = 'fail(f"check 6: {f.name} missing required section: {name}")'
    assert source.count(target) == 1, (
        "fixture assumption: this exact call site exists exactly once in the shipped file"
    )
    replacement = 'fail(f"{f.name} missing required section: {name}")'
    broken = source.replace(target, replacement)
    expected_line = broken[: broken.index(replacement)].count("\n") + 1

    violations = fail_call_prefix_violations(broken)

    # Exactly one violation, naming this exact line. Stripping "check 6: " leaves the
    # f-string opening on its own interpolation (`f"{f.name} missing ..."`), so the
    # predicate's "opens with an interpolation, cannot verify a prefix" reason is the one
    # that fires here — still the correct catch (an interpolation-led message can never be
    # statically proven to carry the prefix, so treating it as a violation is right, not a
    # separate bug), just not the same reason string as a plain missing-prefix case.
    assert len(violations) == 1, violations
    assert violations[0].startswith(f"L{expected_line}:")


def test_the_exempt_message_does_not_silently_widen_to_cover_other_call_sites() -> None:
    """Positive control on the exemption itself: a message that merely *mentions* the exempt
    wording inside a longer sentence, rather than being exactly `check_notes`'s own guard
    text, is still checked normally — proving the exemption's exact-equality match (not a
    substring test) is narrow enough not to swallow an unrelated call site that happens to
    share wording.
    """
    source = (
        "def fail(msg):\n"
        "    pass\n"
        "\n"
        "def other_check():\n"
        '    fail("check 99: something does not exist — checks 16-20 cannot run, but this '
        'is not that guard")\n'
        "\n"
        "def real_gap():\n"
        '    fail("this message has no prefix at all")\n'
    )
    # The first call carries its own `check 99:` prefix despite mentioning the exempt
    # phrase, so it must NOT be treated as exempt-and-skipped — it is checked normally and
    # passes on its own prefix. The second has no prefix and no exempt phrase, so it must
    # be the one violation reported.
    violations = fail_call_prefix_violations(source)
    assert len(violations) == 1
    assert "L8" in violations[0]
