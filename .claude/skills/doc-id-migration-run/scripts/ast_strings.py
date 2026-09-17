# Copied from ~/gi-pricing-plan.local/handover/ast_strings.py (W37-6 run 2, 2026-09-17).
# Reformatted only for ruff (imports, line length, type hints, statement-per-line);
# logic and output format kept as written.
"""Compare AST string constants and structure between two git refs.

Usage: ast_strings.py <ref_a> <ref_b>

For every changed `.py` file between the two refs: counts docstring-value changes
separately from non-docstring string-value changes, and flags a structural
(non-string) diff — the AST with every string constant masked to `"S"` still
differing. Prints one summary line plus up to six example value changes and up
to five structurally-differing files.
"""
import ast
import subprocess
import sys

a, b = sys.argv[1], sys.argv[2]
files = [
    f
    for f in subprocess.run(
        ["git", "diff", "--name-only", a, b], capture_output=True, text=True
    ).stdout.split()
    if f.endswith(".py")
]


def docstr_ids(tree: ast.AST) -> set[int]:
    ids = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            ids.add(id(node.body[0].value))
    return ids


def consts(src: str) -> tuple[list[tuple[str, bool]], ast.AST]:
    t = ast.parse(src)
    ds = docstr_ids(t)
    out = []
    for n in ast.walk(t):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append((n.value, id(n) in ds))
    return out, t


class Strip(ast.NodeTransformer):
    def visit_Constant(self, n: ast.Constant) -> ast.expr:
        if isinstance(n.value, str):
            return ast.copy_location(ast.Constant(value="S"), n)
        return n


tot_doc = tot_other = 0
other_examples: list[tuple[str, ...]] = []
struct_diff: list[str] = []
for f in files:
    sa = subprocess.run(["git", "show", f"{a}:{f}"], capture_output=True, text=True).stdout
    sb = subprocess.run(["git", "show", f"{b}:{f}"], capture_output=True, text=True).stdout
    ca, ta = consts(sa)
    cb, tb = consts(sb)
    # structural check ignoring string constant values
    dump_a = ast.dump(Strip().visit(ast.parse(sa)), include_attributes=False)
    dump_b = ast.dump(Strip().visit(ast.parse(sb)), include_attributes=False)
    if dump_a != dump_b:
        struct_diff.append(f)
    if len(ca) != len(cb):
        other_examples.append((f, "count", str(len(ca)), str(len(cb))))
        continue
    for (va, da), (vb, _db) in zip(ca, cb, strict=True):
        if va != vb:
            if da:
                tot_doc += 1
            else:
                tot_other += 1
                if len(other_examples) < 6:
                    other_examples.append((f, va[:70], vb[:70]))

print(
    f"files={len(files)} docstring-value changes={tot_doc} "
    f"NON-docstring string-value changes={tot_other} "
    f"structural(non-string) diffs={len(struct_diff)}"
)
for e in other_examples:
    print("  ", e)
for f in struct_diff[:5]:
    print("  STRUCT:", f)
