# vendored-example-skill

An upstream skill, vendored verbatim — a worked example of NT-0019 §1.5's vendored-skill
carve-out: this file itself is stamped (`vendored: true`, `origin:`) like any other
`SKILL.md`, but everything beneath this directory (`LICENSE`, `references/extra.md`) is
exempt from stamping, citation rewrite and shape checks, because it ships its own
`LICENSE`.

Cites `FR-EX-1` here, in the one file that *does* get touched, so a test can tell the
citation-rewrite pass apart from the vendored exemption: this occurrence must rewrite,
the one in `references/extra.md` (beneath the vendored boundary) must not.
