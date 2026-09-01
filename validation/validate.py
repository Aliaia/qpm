"""
validate.py  —  run profile V1-V8 over the assembled graph (load files + assembled_meta).
V5 implements the revised V5b: functionality (graph) + no-intervening/adjacency-grounding for
UNIT primaries (geometric; here: every unit primary must be a TOUCHES pair, which the
re-derived primaries satisfy by construction). Place primaries are exempt from grounding.
Reports zero-row passes or itemised failures with samples. Nothing masked.
"""
import os, json
from collections import defaultdict, Counter
HERE = os.path.dirname(__file__)
OUT = os.path.join(os.path.dirname(HERE), "load")

def load(name):
    return json.load(open(os.path.join(OUT, name)))

meta = json.load(open(os.path.join(HERE, "assembled_meta.json")))
unit_hier = meta["unit_hier"]; unit_level = meta["unit_level"]
E = {r: load(f"edges_{r}.json") for r in ["BELONGS_TO_HIERARCHY","CONTAINED_BY","CONTAINED_BY_UNIT",
     "NORTH_OF","SOUTH_OF","EAST_OF","WEST_OF","HAS_MAIN_GEOMETRY","TOUCHES"]}
places = {n["uri"] for n in load("nodes_Place.json")}
report = {}

# V1: per-hierarchy place containment uniqueness
v1 = []
by_place = defaultdict(list)
for e in E["CONTAINED_BY_UNIT"]:
    by_place[e["from"]].append(unit_hier.get(e["to"]))
for p, hs in by_place.items():
    c = Counter(h for h in hs if h)
    for h, n in c.items():
        if n > 1:
            v1.append((p, h, n))
report["V1 place containment uniqueness/hierarchy"] = v1

# V2: unit parent same hierarchy
v2 = [(e["from"], e["to"]) for e in E["CONTAINED_BY"]
      if unit_hier.get(e["from"]) != unit_hier.get(e["to"])]
report["V2 unit parent same hierarchy"] = v2

# V3: level adjacency + root integrity
has_parent = {e["from"] for e in E["CONTAINED_BY"]}
v3 = []
for e in E["CONTAINED_BY"]:
    lc, lp = unit_level.get(e["from"]), unit_level.get(e["to"])
    if lc is None or lp is None or lp != lc - 1:
        v3.append(("level", e["from"], lc, e["to"], lp))
for u, lv in unit_level.items():
    if lv == 0 and u in has_parent:
        v3.append(("root_has_parent", u, lv, None, None))
    if lv and lv > 0 and u not in has_parent:
        v3.append(("nonroot_no_parent", u, lv, None, None))
report["V3 level adjacency + root integrity"] = v3

# V4: touches well-formedness (same hier, same level, no self-loop, one edge per pair)
v4 = []; seen = set()
for e in E["TOUCHES"]:
    a, b = e["from"], e["to"]
    if a == b or unit_hier.get(a) != unit_hier.get(b) or unit_level.get(a) != unit_level.get(b):
        v4.append((a, b, unit_level.get(a), unit_level.get(b)))
    key = frozenset((a, b))
    if key in seen:
        v4.append(("dup", a, b, None))
    seen.add(key)
report["V4 touches well-formedness"] = v4

# V5: functionality (<=1 primary per sector per anchor) + unit grounding (primary is a TOUCHES pair)
touch = {frozenset((e["from"], e["to"])) for e in E["TOUCHES"]}
v5_func = []; v5_ground = []
for rel in ("NORTH_OF","SOUTH_OF","EAST_OF","WEST_OF"):
    per_anchor = Counter(e["to"] for e in E[rel])     # edge (neighbour)->(anchor)
    for anchor, c in per_anchor.items():
        if c > 1:
            v5_func.append((rel, anchor, c))
    for e in E[rel]:
        n, a = e["from"], e["to"]
        if n not in places and a not in places:        # unit primary
            if frozenset((n, a)) not in touch:
                v5_ground.append((rel, n, a))
report["V5a primary functionality (per sector/anchor)"] = v5_func
report["V5b unit primary not adjacency-grounded"] = v5_ground

# V6: <=1 main geometry per entity
v6 = [(u, c) for u, c in Counter(e["from"] for e in E["HAS_MAIN_GEOMETRY"]).items() if c > 1]
report["V6 geometry cardinality"] = v6

# V7: each unit exactly one BELONGS_TO_HIERARCHY
v7 = [(u, c) for u, c in Counter(e["from"] for e in E["BELONGS_TO_HIERARCHY"]).items() if c != 1]
report["V7 hierarchy membership"] = v7

# V8: place-origin consistency
prov = {e["from"] for e in load("edges_HAS_PROVENANCE.json")}  # places with a provenance record
pnodes = {n["uri"]: n["props"] for n in load("nodes_Place.json")}
v8 = []
for uri, pr in pnodes.items():
    o = pr.get("place_origin")
    if o == "described" and uri not in prov:
        v8.append((uri, o))
    if o == "sourced" and not pr.get("source_id"):
        v8.append((uri, o))
report["V8 place-origin consistency"] = v8

print("="*64)
print("V1-V8 VALIDATION (zero rows = pass)")
print("="*64)
for k, v in report.items():
    status = "PASS" if len(v) == 0 else f"*** {len(v)} ROWS ***"
    print(f"{k}: {status}")
    if v:
        for row in v[:4]:
            print("     e.g.", row)
json.dump({k: len(v) for k, v in report.items()}, open(os.path.join(HERE, "validation_counts.json"), "w"))
