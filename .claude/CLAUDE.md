# graphify

**graphify** (`.claude/skills/graphify/SKILL.md`) — turns this repo into a queryable
knowledge graph. Trigger: `/graphify`. When the user types `/graphify`, use the installed
skill before doing anything else.

`graphify-out/` is generated output and is **not** committed (`.gitignore`), so it may not
exist in a fresh clone. Build it with `/graphify .` — code extraction is tree-sitter AST,
local, and costs nothing.

Rules, each conditional on the artifact actually being there:

- **When `graphify-out/graph.json` exists**, prefer it over grepping for codebase
  questions: `graphify query "<question>"`, `graphify path "<A>" "<B>"` for a relationship,
  `graphify explain "<concept>"` for one concept. These return a scoped subgraph, usually
  much smaller than `GRAPH_REPORT.md` or raw grep output.
- **When `graphify-out/wiki/index.md` exists**, use it for broad navigation rather than
  browsing source.
- Read `graphify-out/GRAPH_REPORT.md` only for broad architecture review, or when
  query/path/explain do not surface enough context.
- After modifying code, `graphify update .` keeps the graph current (AST-only, no API cost).

**Do not run the semantic pass over real policy, claims or exposure data.** The code pass is
local, but the docs/PDF/image pass sends content to a configured LLM provider
(`.claude/skills/README.md` records the review). `examples/` carries freMTPL2, which is
public; anything else is not.

The root `CLAUDE.md` is the governed project contract — §12 lists this skill. Nothing about
graphify belongs in it beyond that entry.
