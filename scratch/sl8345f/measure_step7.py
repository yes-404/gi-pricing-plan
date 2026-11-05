# ruff: noqa
import sys
from decimal import Decimal, localcontext
sys.path.insert(0, "packages/pricing-core/tests")
import test_rate_table_bulk_ops as T
import pricing_core.rate_tables.operations as O
from pricing_core.rating.compile import cell_parses
cur = T._version(rows=[{"driver_age_band": "17-20", "relativity": "0.1234"}], value=T._value(min=None, max=None))
exact = Decimal("0.1234")
for step in range(1, 9):
    try:
        cur = O.uplift_table(cur, percentage=Decimal("0.0375"))
    except ValueError as e:
        print(step, "REFUSED:", e); break
    txt = T._cells(cur)[0]["relativity"]
    with localcontext() as c:
        c.prec = 400; exact = exact * Decimal("1.0375")
    print(step, len(Decimal(txt).as_tuple().digits), "digits", txt, "parses", cell_parses(txt), "| exact", exact)
