---
id: RL-9971
family: ruling
title: DP-S1-1 decided — the 200-node limit counts ast.expr nodes, and depth is the longest ast.expr chain, root at 1
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 095dd400918348b32ee6eab1db7915faaa9dfe35
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1268, RL-1184, RL-1289]
---

# RL-9971 — DP-S1-1 decided: the 200-node limit counts `ast.expr` nodes

## How this was ruled

**Ruled at effort `medium`**, under the maintainer's pre-decision by delegation of
2026-09-30 08:48:15 BST (`to-lead.md`, entry headed "PRE-DECISION: the DM may rule
SL-1271's three DPs at MEDIUM effort, under the 08:00 basis, with an executable-evidence
condition"). It applies the 08:00 CHECKPOINT DECISION's basis. Its condition, which this record
meets under *Proof*, is that "each RL must carry an **executable proof** … proven red on
the rejected behaviour and green on the chosen one", including "a boundary case at 200
under the chosen count, and at 201 rejected".

**Working id 9971.** The id is minted at the merge turn, which the lead schedules.

## Verified first, at 095dd400918348b32ee6eab1db7915faaa9dfe35

- **The decision point** is DP-S1-1 of SL-1271's leaf plan (#954, working id 9960), branch
  `p2-wk690-s1-leaf`, read at `4d2e78e8` and re-checked at `6853c1b3`: its decision-point
  table, row at `:275`.
  Its question is: "What does §4.6's 'AST node count ≤ 200; nesting depth ≤ 20' count?"
  - (a) is `ast.expr` nodes only, with depth as the longest chain of nested `ast.expr`
    nodes, the root at 1.
  - (b) is every node `ast.walk` yields, including operator tokens and `Load` contexts.
  - The plan recommends (a).
- **The text being interpreted.**
  - `02` §4.6 (`docs/specs/02-modelling.md:961`): "AST node count ≤ 200 (configurable);
    nesting depth ≤ 20".
  - `02` FR-145 (`:209`): "AST nodes are capped (default 200)".
  - Neither says which nodes. No limit is implemented today (`02` §4.6's 2026-08-22 note),
    so no existing behaviour depends on the answer.
- **The limits bind all four profiles** (`02` §4.6 profile note, `RL-1184` E2). Slice 1
  measures the recipe and check corpus against them before it enforces them.

## Proof — executable, red on (b), green on (a)

**Where it ran.**
- File: `test_dp_s1_1_node_count.py` (sha256 prefix `f7b6fae1e36939d3`), in scratch
  `/home/puzhenhao1989/.claude/jobs/0081b83b/dm-s1-proofs/`. It is not committed; its
  deciding part is reproduced below.
- Environment: this worktree after `uv sync --all-packages`, run at `fb90d381`, so the baseline
  test imports the real parser. `git diff --quiet fb90d381 095dd400 -- packages` → rc 0: the
  code is identical at this record's tree. The parser is `pricing_core.data.expressions.compile_expression`. Polars 1.44.2.

```python
LIMIT = 200
def count_a(src): return sum(isinstance(n, ast.expr) for n in ast.walk(ast.parse(src, mode="eval")))
def count_b(src): return sum(1 for _ in ast.walk(ast.parse(src, mode="eval").body))
AT_LIMIT   = "min(" + ", ".join(["x"] * 198) + ")"   # 1 Call + Name(min) + 198 Name(x)
OVER_LIMIT = "min(" + ", ".join(["x"] * 199) + ")"

def test_counts_recorded():
    assert (count_a("a + b"), count_b("a + b")) == (3, 6)
    assert (count_a(AT_LIMIT), count_b(AT_LIMIT)) == (200, 399)
    assert (count_a(OVER_LIMIT), count_b(OVER_LIMIT)) == (201, 401)

def test_todays_parser_has_no_limit():     # real code: both compile and evaluate today
    ...compile_expression(AT_LIMIT) and compile_expression(OVER_LIMIT) evaluate to [1.0, 2.0]

@pytest.mark.parametrize("pred", ["a_expr_nodes", "b_every_node"])
def test_200_written_nodes_accepted_201_refused(pred):
    assert count(AT_LIMIT) <= LIMIT and count(OVER_LIMIT) > LIMIT

def test_depth_under_a_root_at_1():        # nest(k) = "abs(" * k + "x" + ")" * k
    assert (depth_a(nest(19)), count_a(nest(19))) == (20, 39)
    assert (depth_a(nest(20)), count_a(nest(20))) == (21, 41)
```

**Commands and results** (2026-09-30 08:50:45 BST):

```text
$ uv run --no-sync pytest -q -p no:cacheprovider --rootdir=$S $S/test_dp_s1_1_node_count.py
FAILED …::test_200_written_nodes_accepted_201_refused[b_every_node] - AssertionError:
  b_every_node: 200 written sub-expressions refused (399)
1 failed, 4 passed in 2.07s                                   rc=1
$ uv run --no-sync pytest -q -p no:cacheprovider --rootdir=$S $S/test_dp_s1_1_node_count.py -k "not b_every_node"
4 passed, 1 deselected in 2.67s                               rc=0
```

**How to read it.**
- Under (a), 200 written sub-expressions are accepted and 201 are refused.
- Under (b), the same 200-term expression counts 399 and is refused. `a + b` counts 6
  under (b) against 3 under (a).
- Today's parser accepts both, because it has no limit.
- The counts equal the leaf plan's premise h.

## Ruled

**(a).** Two rules follow.
- **§4.6's node count** is the number of `ast.expr` nodes in the parsed expression. Those
  are names, literals, calls, and unary, binary, boolean and comparison operations,
  counted by `ast.walk` over `ast.parse(src, mode="eval")`.
- **Nesting depth** is the length of the longest chain of nested `ast.expr` nodes, with
  the root expression at depth 1.

Refusal is at count > 200 and at depth > 20, both configurable (FR-145), in all four
profiles.

**Why (a).** An author can count it: a written name, number, call or operation is one node.
Under (b), a limit stated as 200 means about 100 written terms, and the ratio moves with the
operators used. That would be a limit the spec never stated. (b) also counts `Load`
contexts and operator tokens, which an analyst never writes.

**Narrowness: narrow.** The ruling defines a term that `02` §4.6 and FR-145 already use,
for a limit not yet implemented. It changes no FR text, no published contract (no schema,
route or error code), and no existing behaviour.

## What it obliges

- **WK-690 Slice 1 (SL-1271's leaf plan, #954: Task 2, and Task 4 Steps 1, 3 and 4):**
  - implements the count and depth as ruled;
  - cites this record in the `02` §4.6 note that the leaf plan places ("counted over
    `ast.expr` nodes (DP-S1-1 …)");
  - carries the boundary tests below.
- **Nobody else.** This commit edits no spec, plan or roadmap text.

## Acceptance — the violation that must become detectable

In Slice 1's own suite, each case is shown red first:
- *Violation: an expression of exactly 200 `ast.expr` nodes is refused* (`min(x, …)` with
  198 arguments).
- *Violation: one of 201 is accepted.*
- *Violation: depth 20 (19 nested `abs`) is refused, or depth 21 accepted.*
- *Violation: `a + b` is counted as anything but 3.*
