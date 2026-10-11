"""Limbs 1 and 3 of PL-1364 Task 5. Usage: limb13.py <out.jsonl>. Run with the HEAD tree's interpreter."""
import json, sys, time
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import shapes
from model_schema import ScoringResult

out = open(sys.argv[1], "a")


def timed(fn, n=1000, warm=100):
    for _ in range(warm):
        fn()
    xs = []
    for _ in range(n):
        t = time.perf_counter(); fn(); xs.append((time.perf_counter() - t) * 1000)
    xs.sort()
    return {"p50_ms": xs[n // 2], "p99_ms": xs[989], "max_ms": xs[-1]}


for run in (1, 2, 3):
    for name, d in (("U", shapes.shape_u_dict()), ("T", shapes.shape_t_dict())):
        built = ScoringResult.model_validate(d)
        for op, fn in (("V+S", lambda d=d: ScoringResult.model_validate(d).model_dump_json()),
                       ("S", lambda r=built: r.model_dump_json())):
            row = {"limb": 1, "run": run, "shape": name, "op": op, **timed(fn)}
            out.write(json.dumps(row) + "\n"); out.flush(); print(row)

from app.main import create_app
from app.config import Settings
app = create_app(Settings())
spec = app.openapi()
for r in app.routes:
    if getattr(r, "path", "") in ("/api/v1/score", "/api/v1/score/compare") and "POST" in getattr(r, "methods", ()):
        schema = spec["paths"][r.path]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
        row = {"limb": 3, "path": r.path, "response_model": repr(r.response_model), "response_field": repr(r.response_field), "schema200": schema}
        out.write(json.dumps(row) + "\n"); print(row)
