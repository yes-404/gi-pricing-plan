# vendored-example-skill

An upstream skill, vendored verbatim — a worked example of the migration spec's
vendored-skill carve-out: this file itself is stamped (`vendored: true`, `origin:`) like
any other `SKILL.md`, but everything beneath this directory (`LICENSE`,
`references/extra.md`) is exempt from stamping, citation rewrite and shape checks,
because this directory's name is declared as vendored (`tests/test_doc_id_migrate.py`'s
own fixture setup adds it to `_VENDORED_SKILLS` for the duration of each test in that
module — Ruling 69's declared-constant mechanism, not detection by this directory's
`LICENSE` file, which is carried only to prove a vendored skill's own licence text
survives byte-for-byte).

Cites `FR-EX-1` here, in the one file that *does* get touched, so a test can tell the
citation-rewrite pass apart from the vendored exemption: this occurrence must rewrite,
the one in `references/extra.md` (beneath the vendored boundary) must not.
