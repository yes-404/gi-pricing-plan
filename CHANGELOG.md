# Changelog

All notable changes to this platform that a deployer or a caller of the API needs to know
about. The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- **Scoring now refuses a numeric input the engine cannot hold exactly; it priced silently, or
  failed with a 500, before.** `POST /api/v1/score`, `POST /api/v1/score/compare` and the batch
  path refuse a Rating Input, or any numeric key in a quote's inputs (by key path, nested keys
  included), whose value does not round-trip through a float, or whose float the engine's
  decimal cannot hold. The refusal is `422` `INPUT_CONTRACT_VIOLATION` (an RFC 9457 problem)
  naming the key path; the value is never echoed. Three kinds of value are refused:
  - **More than 15 significant digits.** `0.82469000000000000002` was rounded by the JSON parse
    and priced as the rounded value; it is refused now.
  - **A value that underflows to zero**, such as `1e-400`. It priced as `0.0`; it is refused now.
  - **A value outside the engine's decimal**, which fails in the engine as measured: a scale
    above 28 digits after the point (every non-zero value below about `1e-28` in magnitude,
    such as `1.5e-28`, a subnormal such as `5e-324`, and the smallest normal double
    `2.2250738585072014e-308`) or a magnitude of 2^96 (about `7.9e28`) or more. These were a
    `500` `INTERNAL_ERROR` (`RATING_EVALUATION_FAILED` in `pricing-core`) before; the code
    is now `INPUT_CONTRACT_VIOLATION`, `422`.

  **What a caller must do:** send at most 15 significant digits and at most 28 digits after the
  point, with a magnitude below 2^96 (`7.9e28` is accepted), or zero.
  A value that meets this prices as before; `0` and `-0` are accepted and equal.
