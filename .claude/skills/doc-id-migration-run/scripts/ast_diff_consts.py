# Copied from ~/gi-pricing-plan.local/handover/ast_diff_consts.py (W37-6 run 2, 2026-09-17).
# Reformatted only for ruff (imports, line length, type hints); logic and output
# format kept as written.
"""List non-docstring string constants that changed value in one file between two refs.

Usage: ast_diff_consts.py <ref_a> <ref_b> <path>
"""
import ast
import subprocess
import sys

a, b, f = sys.argv[1], sys.argv[2], sys.argv[3]


def consts(src: str) -> list[tuple[str, bool, int]]:
    t = ast.parse(src)
    ds = set()
    for n in ast.walk(t):
        if (
            isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and n.body
            and isinstance(n.body[0], ast.Expr)
            and isinstance(n.body[0].value, ast.Constant)
            and isinstance(n.body[0].value.value, str)
        ):
            ds.add(id(n.body[0].value))
    return [
        (n.value, id(n) in ds, n.lineno)
        for n in ast.walk(t)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    ]


ca = consts(subprocess.run(["git", "show", f"{a}:{f}"], capture_output=True, text=True).stdout)
cb = consts(subprocess.run(["git", "show", f"{b}:{f}"], capture_output=True, text=True).stdout)
print("counts", len(ca), len(cb))
for (va, da, la), (vb, _db, lb) in zip(ca, cb, strict=True):
    if va != vb and not da:
        print(f"L{la}->{lb}:\n  before: {va[:160]!r}\n  after:  {vb[:160]!r}")
