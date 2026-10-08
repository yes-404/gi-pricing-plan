---
id: FD-1506
family: finding
title: The NFR-499 error-sink census identifies an exception by its variable name, so a handler bound to an unlisted name passes it
status: active
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
corrected_by: []
relates: [WK-1178, NFR-499, RL-917]
---

# FD-1506 — the NFR-499 census finds an exception's text by the variable's name

**Filed** by auditor-fdc1 on 2026-10-05, from the maintainer's (by delegation) entry "2026-10-04 17:20:57 BST — Lane B gate
red …" in `to-lead.md`. `tree:` is `origin/main` = `47d770e8fcbd2410fa101019ed8cf3aae69a1baa`, the tree every
figure below was measured on. The id is a working id until the lead mints it.

*Re-anchored 2026-10-05 at main `caa4e411a9c07a389cf47092a923c7761b2b92dc`: the line cites below moved and were
re-read at that tree (name tuple `:187`/`:192` → `:198`/`:203`; `_sinks` `:167` → `:178`; the equality assert
`:218` → `:230`; `test_the_census_sees_an_injected_sink` `:237` → `:248`; the glob `:31` → `:30`;
`objectives.py:1559` → `:1604`). The defect still reproduces there: steps 2 and 3 were re-run (`problem` passes
the census, `exc` fails it). The measurements in the steps below are those of `47d770e8`.*

**Severity: MEDIUM (owner WK-1178).** The maintainer (by delegation) set it MEDIUM "confirmed at filing if (1) reproduces; if
(1) fails, LOW, with the proof attached". (1) reproduces (§Evidence, step 2), so MEDIUM stands. The severity is
the maintainer's (by delegation) and the maintainer's to confirm at the mint.

## Finding

`backend/tests/test_error_sinks.py` is the guard for NFR-499. It finds the places where an exception's text is
stored or logged. It finds two of its seven sink kinds by the **variable name** of the exception, and the name
list is fixed: `("exc", "e", "err")` at `test_error_sinks.py:198` (`str(<name>)`) and `:203` (`{<name>}` in an
f-string). A handler that binds the exception to any other name, and calls `str()` on it or interpolates it,
is not counted. The test compares the census with `_SINKS` for equality (`:230`), so a sink the census does not
see is never compared, and the test passes.

Two failure modes follow, and only one of them has been seen.

1. **False positive (harmless, seen once).** A variable named `e` that is not an exception is counted as a
   sink. The maintainer's (by delegation) entry records this at the WK-673 Slice 2 gate: a Decimal band edge named `e` at
   `analysis.py:372` failed the census, and Delta 4 renamed it to `edge`. **That file is not on `main`
   `47d770e8`** (`git ls-tree -r origin/main --name-only | grep analysis.py` finds no
   `backend/src/app/platform/analysis.py`), so this limb is quoted from the maintainer's (by delegation) record and not re-run
   here.
2. **False negative (silent).** `except X as problem: log(str(problem))` carries the text of an exception
   past the guard. This is the limb this essay proves.

## Requirement

`docs/specs/03-rating-engine.md:1340`, NFR-499 (the first sentence; the amendments follow it in the same cell):

> "Security: the scoring API authenticates per Consumer System with scoped credentials and per-client rate
> limits; quote inputs are never logged in full outside sampled traces, which are access-controlled."

The dated clarification of 2026-08-30 (WK-671) says the clause "governs persistence, not only log output" and
that "a full quote input may be held only in an access-controlled artifact this specification names for that
purpose". The test's own module docstring (`test_error_sinks.py:1-12`) states its job: "fails when one [a sink]
is added, moved or removed without a matching line in `_SINKS` saying what covers it". A sink the census cannot
see is none of these.

## Evidence

All commands were run on 2026-10-05 from the worktree `.claude/worktrees/fd-9726` (clean checkout of
`47d770e8`), with the repository venv. Only the census test was run, not the suite. The scratch file was
created and removed inside the run, and is not committed.

### The name list is the whole identification

```
$ grep -n '("exc", "e", "err")' backend/tests/test_error_sinks.py
187:                and node.args[0].id in ("exc", "e", "err")
192:            and node.value.id in ("exc", "e", "err")
```

`_sinks` (`:178`) reads a `str(...)` call whose first argument is a `Name` in that tuple (`:196-200`), and an
f-string `FormattedValue` whose value is a `Name` in that tuple (`:201-205`). It never reads the `as` binding of
an `ExceptHandler`. The other five sink kinds (`.exception(`, a call with `exc_info=`, `JobError(`, an
assignment to `.last_error`, a dict key `"error_message"`) do not depend on the name.

### 1. Baseline: the census passes on the clean tree

```
$ .venv/bin/python -m pytest -q -p no:cacheprovider --rootdir=$W -c $W/pyproject.toml \
    $W/backend/tests/test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for
1 passed, 2 warnings in 1.31s
```

(`$W` is the worktree root. The two warnings are the per-worktree test-database notice from `conftest_db.py`;
this test touches no database.)

### 2. The false negative: a handler bound to the unlisted name `problem`

Scratch file `backend/src/app/platform/_scratch_fd9726.py`, inside the first glob
(`backend/src/app/**/*.py`, `test_error_sinks.py:30`):

```python
import logging
_log = logging.getLogger(__name__)


def leak(payload):
    try:
        payload.validate()
    except ValueError as problem:
        _log.warning("failed: %s", str(problem))
        return f"failed: {problem}"
```

It logs the exception's text with `str(problem)` and puts it in an f-string, the two forms the census exists
to find. Same command as step 1:

```
1 passed, 2 warnings in 1.19s
```

**The census passes with two unaccounted sinks.**

### 3. Control: the same file with the name `exc`

`sed -i 's/problem/exc/g'` on the scratch file, nothing else changed. Same command:

```
FAILED .claude/worktrees/fd-9726/backend/tests/test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for - AssertionError: a sink that stores or logs an exception's text was added, m...
1 failed, 2 warnings in 1.13s
```

The only difference between the pass in step 2 and the failure in step 3 is the variable's name. The scratch
file was then deleted (`git status --short` empty).

### 4. A second blind spot, found while measuring (not the finding's main limb)

A scratch handler bound to the **listed** name `exc` that logs it by `%`-argument and returns `repr(exc)`:

```python
    except ValueError as exc:
        _log.warning("failed: %s", exc)
        return repr(exc)
```

```
1 passed, 2 warnings in 1.08s
```

So the census also does not see an exception passed bare as a log argument, nor `repr(exc)`. That is a
different gap (the list of **shapes**, not of names), and it is reported here so the remedy's scope is chosen
knowingly. Neither shape is in the module docstring's list of sinks (`:9-12`).

### 5. How many handlers use a name outside the list today

```
$ grep -rnE "except .* as [a-z_]+:" backend/src/app packages/pricing-core/src --include=*.py \
    | grep -vE " as (exc|e|err):" | wc -l
2
```

(The same grep with `as (exc|e|err):` counts 90 handlers.) The two are
`packages/pricing-core/src/pricing_core/modelling/objectives.py:1604` (`as failure`) and
`packages/pricing-core/src/pricing_core/modelling/gbm.py:590` (`as error`). Read at `47d770e8`:

- `objectives.py:1604-1611` interpolates `{failure}` into a `CertificateCheck.detail` string. This is the exact
  false-negative shape, live on `main`. It is on the custom-objective certificate path, an artifact path with
  no Quote Context, so it is **not a quote-input leak**; it is the census missing a sink that a listed name
  would have made it count.
- `gbm.py:590-591` (in `_compile_custom`) raises `GbmFitError(error.code, str(error), …)`: `str(error)` is the same shape. It is a
  model-fit path, again not a quote input.

Neither is a defect against NFR-499 as measured. Both are sinks the census **should** list in `_SINKS` with a
reason (as `("backend/src/app/worker/model_handlers.py", "_fit", "str(exc)")` is listed for its own sites) and does not.

## What this finding does NOT claim

- It does not claim any quote input is logged or stored today. No handler on a quote-input path was found that
  uses an unlisted name (step 5 found two handlers in all, neither on a quote-input path).
- It does not claim the shipped `str(exc)` sinks listed in `_SINKS` are wrong. Their covers were not re-audited.
- It does not re-run the false positive. `analysis.py` is not on `main`; the maintainer's (by delegation) record is the source.
- It does not enumerate every way to log an exception. Step 4 shows two more by measurement. A complete list is
  the remedy's job.
- It does not say the census should be replaced. The AST approach is right; the identification is what is wrong.

## Disposition

Proposed remedy, for WK-1178's plan to decide:

1. **Identify an exception by binding, not by name.** In `_sinks`, track the `as <name>` of each enclosing
   `ast.ExceptHandler` and count `str(<name>)` and `{<name>}` only when `<name>` is bound by an enclosing
   handler. The fixed tuple at `:198` and `:203` goes. This closes the false negative (step 2) and the false
   positive (a variable named `e` that is not an exception is no longer counted, so the `e` → `edge` rename
   becomes unnecessary).
2. **Widen the shapes** the same change can cheaply see: a bare handler-bound name as an argument of a logging
   call, `repr(<name>)`, and `<name>.args`. Whether to count them is a scoping choice for the plan; step 4
   gives the evidence that they pass today.
3. **List the two sites** in step 5 in `_SINKS` with their reasons once the census sees them.
4. **Prove it on broken input both ways** (CLAUDE.md §13): the step 2 handler must fail the census, and a
   non-exception variable named `e` must not. Both belong in `test_the_census_sees_an_injected_sink`
   (`:248`), which today uses only listed names.

## Severity (proposed; the maintainer's)

**MEDIUM.** The guard enforces NFR-499, a security requirement, and a handler written with an ordinary name
such as `error`, `failure` or `problem` passes it silently; two such handlers exist on `main` today. It is not
HIGH: no leak is demonstrated, and a leak also needs a quote-input path to reach the handler. It is not LOW:
the failure is silent, in a security guard, and one `except … as error` away.
