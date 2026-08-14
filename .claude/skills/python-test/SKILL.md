---
name: python-test
description: Testing discipline for this repo — requirement-traceability markers, the negative-test emphasis a governed system needs, pytest configuration, and how to run the suite in an environment without pip. Use when writing or running tests, adding a test marker, or checking which requirements the suite actually covers.
---

# Testing here

```bash
uv run pytest -q
uv run python scripts/req-coverage.py     # which requirements the suite claims
```

## Every test names the requirement it satisfies

```python
@pytest.mark.req("FR-OVR-7")
def test_money_minor_refuses_floats(): ...
```

`scripts/req-coverage.py` turns those marks into a traceability report and **fails when a
test claims a requirement that does not exist** — catching typos and any renumbering that
breaks the append-only rule (`CLAUDE.md` §5).

Coverage is currently *reported, not gated*. At 1.7 % a threshold would fail every build
and teach everyone to ignore it; it earns a floor once a phase's requirements are meant to
be complete.

## Write the negative test first

This is the habit that matters most here. For a governed system the suite has to prove the
wrong thing **cannot** happen, not merely that the right thing can:

- a float is **refused** in the money path, not coerced
- an artifact envelope **cannot** be mutated
- the generated JSON Schema **does not admit** a payload the spec forbids
- a submitter **cannot** approve their own request (`06` NFR-GOV-8)

A suite that only demonstrates the happy path will pass while the invariant it exists to
protect is quietly broken.

## Pin the case where a choice actually bites

Prefer an assertion that fails if the behaviour changes over one that merely documents it:

```python
# 24150 * 1.15 == 27772.5 exactly — a tie, so the rounding mode alone decides.
assert apply_factor(24150, Decimal("1.15"), "half_even") == 27772
assert apply_factor(24150, Decimal("1.15"), "half_up")   == 27773
```

That pair is worth more than either line alone: it shows the mode changes the answer, which
is *why* FR-RATE-12 makes rounding an explicit per-step declaration. (The half-even value
is also the one intuition gets wrong.)

## Configuration

- **`--import-mode=importlib`** — the mode pytest recommends for new projects, and required
  here because each package owns a `test_money.py`; the legacy `prepend` mode collides on
  the basename.
- **`--strict-markers`** — an unregistered marker is an error, so a typo'd `@pytest.mark.req`
  fails rather than silently doing nothing.
- Markers registered in the root `pyproject.toml`. Fixtures in `conftest.py`.

## Running without pip

This environment has no `pip` or `ensurepip`, so `uv run pytest` is unavailable. Fetch
wheels directly and use `PYTHONPATH` — see the `library-spike` skill, which covers the
wheel-fetching recipe, the version-pinning trap, and missing native libraries.

```bash
PYTHONPATH="$SP/libs:packages/model-schema/src:packages/pricing-core/src" \
  python3 -m pytest packages -q -p no:cacheprovider
```

**What cannot be run here:** `uv`, `ruff`, `mypy`, `lint-imports`, `docker compose`. Say so
rather than implying a clean run — CI is the first real check of those.

## Verified

2026-08-14 — W1's 21 tests, run this way. Two defects surfaced by *running* rather than
assuming: the `test_money.py` basename collision (fixed by `importlib` mode), and an
expected value of mine that was simply wrong — 24150 × 1.15 is exactly 27772.5, so
half-even gives 27772 and my intuition had defaulted to half-up.
