"""Acceptance 10's stop conditions from the jsonl. Usage: verdict.py <out.jsonl>"""
import json, statistics, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
stop = False
for route in ("/score", "/score/compare"):
    b = [r["p99_ms"] for r in rows if r.get("limb") == 2 and r["route"] == route and r["tree"] == "base"]
    h = [r["p99_ms"] for r in rows if r.get("limb") == 2 and r["route"] == route and r["tree"] == "HEAD"]
    if len(b) != 3 or len(h) != 3:
        print(route, "INCOMPLETE", len(b), len(h)); stop = True; continue
    mb, mh, rng = statistics.median(b), statistics.median(h), max(b) - min(b)
    flag = mh - mb > rng
    stop |= flag
    print(f"{route}: base p99 {b} median {mb:.3f} range {rng:.3f}; HEAD p99 {h} median {mh:.3f}; delta {mh-mb:.3f}; STOP={flag}")
l3 = [r for r in rows if r.get("limb") == 3]
for r in l3:
    ok = r["response_model"] == "None" and r["response_field"] == "None" and "$ref" in r["schema200"]
    print("limb3", r["path"], r["response_model"], r["response_field"], r["schema200"], "OK" if ok else "STOP")
    stop |= not ok
print("STOP_CONDITION_FIRED" if stop else "NO_STOP_CONDITION")
