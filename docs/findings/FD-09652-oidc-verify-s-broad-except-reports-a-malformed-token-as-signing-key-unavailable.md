---
id: FD-9652
family: finding
title: oidc verify's broad except reports a malformed token as "signing key unavailable"
status: active
created: 2026-10-05
owner: auditor
tree: 99afcde215c0817c5ac4db55332ab7a69e4752a0
corrected_by: []
relates: [WK-1178]
---

# FD-9652 — `OidcVerifier.verify`'s broad `except` reports a malformed token as "signing key unavailable"

**Working id 9652** (unminted; the lead is the sole allocator). **Severity: LOW; owner WK-1178.**
Ruled by the maintainer (by delegation), decision 2 in the entry headed *"2026-10-05 13:32:27 BST — #1123 check
result accepted; CORRECTION to my 13:28:14 and 13:30:39 pyjwt impact claim; hardening finding YES
(LOW); RL 9663 noted"* (`to-lead.md`, a local channel file, so cited by its header). The `tree:` is
`origin/main` at `99afcde2`; the code below was read there by the auditor.

## Finding

`OidcVerifier.verify` (`backend/src/app/auth/oidc.py`, in the first `try` of `verify`, about
`:100-107` at `99afcde2`) is:

```python
        try:
            signing_key = self._jwk_client().get_signing_key_from_jwt(token)
        except Exception as exc:
            # A JWKS fetch failure and an unknown `kid` both land here. Neither is
            # distinguishable to the caller, and the operator gets the type in the log.
            _log.warning(
                "could not resolve a signing key", extra={"error_type": type(exc).__name__}
            )
            raise TokenRejectedError(f"signing key unavailable: {type(exc).__name__}") from exc
```

`get_signing_key_from_jwt` parses the token itself (pyjwt's `get_unverified_header`, and in 2.14.0
a `decode_complete` call, `jwks_client.py:280` there). A token that fails *parsing* therefore
raises inside this `try`, and `except Exception` maps it to the reason **"signing key
unavailable: <ExceptionType>"**. That reason is for a JWKS fetch failure or an unknown `kid`. For a
malformed token it sends the operator to the identity provider when the fault is in the token.

**The concrete case.** A deeply nested JWT payload raises `RecursionError` inside pyjwt 2.14.0's
`decode_complete`. The response is still a 401, but the 401 is **accidental**: it holds only
because pyjwt parses the payload before `jwt.decode` runs, and the broad `except` catches whatever
it throws. A narrower catch added later, or a pyjwt that stops parsing there, would let the error
escape as a 500.

**Not a 500, not a bypass.** That entry corrects an earlier claim of a possible 500
and of an "REACHABLE" advisory: at `99afcde2` the outcome is a 401 on both pyjwt versions. This
finding is the misleading reason and the accidental dependence, nothing more.

## Evidence

**The reproduction is an earlier auditor's, run at `99afcde2` and reported to the lead; this
record's author did not re-run it** (a gate slot was held by SL-1409's gate, so no test was run
for this record). Method as reported: a scratch copy of `backend/tests/test_auth_oidc.py` (a real
RSA key and a JWKS), a token signed RS256 with the valid `kid` and a payload nested 100,000
levels deep. Results as reported:

| Call | pyjwt 2.14.0 | pyjwt 2.15.0 |
|---|---|---|
| `authenticate_bearer` | `PlatformError` 401 | 401 |
| `verifier.verify` | `TokenRejectedError("signing key unavailable: RecursionError")` | `TokenRejectedError("signing key unavailable: DecodeError")` |
| direct `jwt.decode` | `RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string` | not reported |

**Caveat:** the call was to `authenticate_bearer` with a stub session, not over HTTP, so the 401
is the service seam's, not a measured HTTP response. The 2.15.0 row shows the same wrong reason
with a different type name. Dependabot's #1123 (pyjwt 2.15.0) is unrelated and merges for its
advisory; it does not fix this.

## Disposition

**Ruled** (decision 2 above: "YES, file it, LOW, owner WK-1178"; the lead gives the verdict at the mint): fix before close with owner WK-1178. Remedy (as that decision states it):

In `verify`, catch the decode and recursion class (`jwt.exceptions.DecodeError`, `RecursionError`)
separately from the JWKS-fetch and unknown-`kid` class, with its own reason (for example
"malformed token") and its own log line, leaving the broad catch's reason for the genuine
key-resolution failures. Pin it with a test: a deeply nested token gets a 401 and that reason,
red first. The remedy is not built.

**Re-read at `origin/main` 809a3794, 2026-10-05:** the code above is unchanged, at `oidc.py:99-107` (the `try` at :99, the `except Exception` at :101, the raise at :107); no test in `backend/tests/test_auth_oidc.py` names `RecursionError`, a nested token or "signing key unavailable"; `uv.lock` now resolves pyjwt 2.15.0 (#1123 merged), so the 2.15.0 column of the table is the one that applies on main. The reproduction itself was not re-run (docs only, no test run). The pyjwt 2.14.0 `jwks_client.py:280` cite was not re-read (2.14.0 is no longer installed).
