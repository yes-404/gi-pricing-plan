# Changelog

All notable changes to this platform that a deployer or a caller of the API needs to know
about. The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- **A GLM refuses a level of a categorical Factor that its fit never saw, unless the Factor
  declares `map_to_base`.** A Factor gains `unseen_level_behaviour` (`error` or `map_to_base`;
  unset refuses), on `POST /api/v1/factors` and in the factor form. The refusal is
  `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`: `409` on the prediction route, `MODEL_CALL_FAILED` carrying
  that code on a quote. A Factor's declaration changes only by a new Factor version, which a
  refit pins in a new model and a new Rating Version pins in a new bundle hash (FR-239,
  FR-2143). Run `scripts/sweep-unseen-levels.py` before upgrading: a version it lists will
  refuse the quotes it names until a new model is approved, and a batch carrying many such rows
  can abort above `rating.batch_abort_failure_rate`. A version whose GLM has an indicator term for
  a level its numeric input can never produce refuses every quote on that path, not only the
  affected values; the sweep lists such versions as `NOTEXAMINED-NUMERIC-TERMS` until their models
  are refitted. The sweep examines each GLM in a bundle and counts a model of another family (a
  GBM or an EBM, which keeps the FR-131 refusal) on `not-examined-other-family`; a model with no
  fit result, no model type or an unknown one makes its version unreadable, and each unreadable
  line names the version and a reason word or the exception's type only. Diagnostics, comparisons
  and backtests leave
  rows on such a level out of their figures and report the count and exposure; the model detail
  view lists each banded null level, Grouping target and interaction cell the fit has no
  relativity for.
- **Scoring now refuses a numeric input the engine cannot hold exactly; it priced silently, or
  failed with a 500, before.** `POST /api/v1/score` and `POST /api/v1/score/compare` refuse a
  Rating Input, or any key in a quote's inputs written as a number with a fraction or an
  exponent, or as `NaN`, `Infinity` or `-Infinity` (by key path, nested keys included), whose
  value does not round-trip through a float, or whose float the engine's decimal cannot hold.
  Integers are not checked. On the batch path only a `Decimal`-typed dataset column is checked;
  a float column is unchanged (FD 2123). The refusal is `422` `INPUT_CONTRACT_VIOLATION` (an RFC 9457 problem)
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

### Upgrade notes

- **Do not enable blob garbage collection before backfilling bundle-blob references.** A Rating
  Version compiled before this release stores its compiled bundle blob with `ref_count` 0, so
  enabling garbage collection first can delete a live bundle; backfill the references first
  (FD-2135, OQ-1943).
