# ruff: noqa
"""Measurement (not a test): precision of the bulk transforms, old vs new _format_value.
Run from the worktree root: uv run python scratch/sl8345f/measure_precision.py"""
import sys
from decimal import Decimal, localcontext, getcontext
sys.path.insert(0, "packages/pricing-core/tests")
import test_rate_table_bulk_ops as T
import pricing_core.rate_tables.operations as O

NEW = O._format_value
OLD = lambda v: format(v.normalize(), "f")  # the expression at e6d141ba:operations.py:697
print("ambient prec:", getcontext().prec)

def tbl(vals):
    rows = [{"driver_age_band": b, "relativity": v} for b, v in zip(["17-20", "21-24", "25-29"], vals)]
    return T._version(rows=rows, value=T._value(min=None, max=None))

def ex(f):
    with localcontext() as c:
        c.prec = 400
        return f()

cell = "1234567890123456789012345.6789"  # 29 digits: the engine reads it (cell_parses True to 29 digits)
t = tbl([cell, "1.5", "2"])
f15 = Decimal("1.5")
refs = {
  "uplift_table(0.5)":      ex(lambda: Decimal(cell) * f15),
  "uplift_by_filter(0.5)":  ex(lambda: Decimal(cell) * f15),
  "rebase(base=row 2 =1.5)": ex(lambda: Decimal(cell) / f15),
}
ops = {
  "uplift_table(0.5)":      lambda: O.uplift_table(t, percentage=Decimal("0.5")),
  "uplift_by_filter(0.5)":  lambda: O.uplift_by_filter(t, percentage=Decimal("0.5"), filter={"driver_age_band": ["17-20"]}),
  "rebase(base=row 2 =1.5)": lambda: O.rebase_to_level(t, base_level={"driver_age_band": ["21-24"]}),
}
for mode, fn in (("OLD", OLD), ("NEW", NEW)):
    O._format_value = fn
    print("=====", mode, "_format_value; input cell", cell, "(29 digits)")
    for name, run in ops.items():
        try:
            out = T._cells(run())[0]["relativity"]
            print(f"{name:26} -> {out}   exact={refs[name]}")
        except ValueError as e:
            print(f"{name:26} -> REFUSED {str(e)[:70]}   exact={refs[name]}")
    # floor_and_cap: no arithmetic, the cell is only clamped
    out = T._cells(O.floor_and_cap(t, floor=Decimal("1"), cap=Decimal("2")))[0]["relativity"]
    print(f"{'floor_and_cap(1,2)':26} -> {out}  (clamped to the cap; no arithmetic)")
    out = T._cells(O.floor_and_cap(t, floor=Decimal("1"), cap=Decimal("1" + "0"*29)))
    print(f"{'floor_and_cap(wide cap)':26} -> {out[0]['relativity']}  (cell inside [floor,cap]: unchanged text kept)")


print()
print("--- floor_and_cap with a 35-digit floor above the cell (the only way the OLD _format_value rounds on the ops path at ambient 28)")
wide_floor = Decimal("1234567890123456789012345678901234.5678")
for mode, fn in (("OLD", OLD), ("NEW", NEW)):
    O._format_value = fn
    t2 = tbl(["1", "2", "3"])
    try:
        out = T._cells(O.floor_and_cap(t2, floor=wide_floor, cap=wide_floor))[0]["relativity"]
        print(mode, "->", out, " exact floor =", wide_floor)
    except ValueError as e:
        print(mode, "-> REFUSED", str(e)[:90])

def series(label, start, fmt):
    O._format_value = fmt
    cur = tbl([start, "1", "1"])
    exact = Decimal(start); fac = Decimal("1.0375")
    first_mant = first_diff = refused = None
    for step in range(1, 120):
        try:
            cur = O.uplift_table(cur, percentage=Decimal("0.0375"))   # ambient context stays 28
        except ValueError as e:
            refused = (step, str(e)[:110]); break
        with localcontext() as c:                                    # reference only, high precision
            c.prec = 400; exact = exact * fac
        txt = T._cells(cur)[0]["relativity"]
        d = len(Decimal(txt).as_tuple().digits)
        if first_mant is None and d >= 28: first_mant = (step, d, txt)
        if first_diff is None and Decimal(txt) != exact: first_diff = (step, d, txt, str(exact))
    print(label, "| first mantissa >= 28 digits:", first_mant)
    print(label, "| first stored != exact     :", first_diff)
    print(label, "| first refusal by the op   :", refused)

print()
print("--- (4) repeated x1.0375 through uplift_table (the 1st row of a 3-row table; ambient prec 28)")
for mode, fn in (("OLD", OLD), ("NEW", NEW)):
    series(f"{mode} start 0.1234", "0.1234", fn)
    series(f"{mode} start 0.0123", "0.0123", fn)
    series(f"{mode} start 1.0   ", "1.0", fn)
