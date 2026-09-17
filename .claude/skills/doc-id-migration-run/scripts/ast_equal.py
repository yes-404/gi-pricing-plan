# Copied from ~/gi-pricing-plan.local/handover/ast_equal.py (W37-6 run 2, 2026-09-17).
# Reformatted only for ruff (imports, line length, statement-per-line); logic and
# output format kept as written.
"""Whole-tree AST equality check: for every `.py` file that differs between two
git refs, is the parsed AST identical (attributes stripped)?

Usage: ast_equal.py <ref_a> <ref_b>
"""
import ast
import subprocess
import sys

a, b = sys.argv[1], sys.argv[2]
files = subprocess.run(
    ["git", "diff", "--name-only", a, b], capture_output=True, text=True, check=True
).stdout.split()
py = [f for f in files if f.endswith(".py")]
same = 0
diff = 0
bad = []
for f in py:
    src_a = subprocess.run(["git", "show", f"{a}:{f}"], capture_output=True, text=True).stdout
    src_b = subprocess.run(["git", "show", f"{b}:{f}"], capture_output=True, text=True).stdout
    da = ast.dump(ast.parse(src_a), include_attributes=False)
    db = ast.dump(ast.parse(src_b), include_attributes=False)
    if da == db:
        same += 1
    else:
        diff += 1
        bad.append(f)
print(f"py files changed: {len(py)}; AST identical: {same}; AST differs: {diff}")
for f in bad:
    print("  DIFFERS:", f)
print("non-py files changed:", [f for f in files if not f.endswith(".py")])
