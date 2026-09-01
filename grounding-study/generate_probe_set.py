"""
Probe question set — four-sector frame.

Reads ONLY the regenerated (validated) graph, not the pre-regeneration source TTLs:
  units  : load/nodes_Unit.json  +  load/edges_{NORTH,EAST,SOUTH,WEST}_OF.json  (unit-unit)
  places : load/nodes_Place.json +  frame8/place_primaries_oneRing_frame4.json  (one-ring layer)
Entities are identified by canonical URI. place_type carries the real categories (needed for the
salience stratum; the old TTL had "Point" for every place).

Population: ordered pairs (A,B) whose four-sector direction of A from B is derivable in <=2 steps.
  depth 1: A is a stored primary of B in sector d              -> {d}, definite by construction
  depth 2: chain B -> M -> A (M is B's primary d1; A is M's primary d2) -> compose(d1,d2).
           Pairs with a stored direct primary are excluded; only pairs whose depth-2 chains ALL
           AGREE are kept, and each item is labelled by its own chain.
Exclusions: same-type name collisions (A, B, M); nationally famous places/landmarks.
Names: English side of a " - " form where present, as stored otherwise, used consistently.
"""
import os, json, re, csv, random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.dirname(HERE)
LOAD = os.path.join(REG, "load")
SEED = 20260620
random.seed(SEED)

ORDER = ["north", "east", "south", "west"]
U4 = frozenset(ORDER)
WORD = {"NORTH_OF": "north", "EAST_OF": "east", "SOUTH_OF": "south", "WEST_OF": "west"}
_T4 = {  # verified four-sector cone table (symmetric)
    "north": {"north": {"north"}, "east": {"north", "east"}, "south": U4, "west": {"north", "west"}},
    "east":  {"north": {"north", "east"}, "east": {"east"}, "south": {"east", "south"}, "west": U4},
    "south": {"north": U4, "east": {"east", "south"}, "south": {"south"}, "west": {"south", "west"}},
    "west":  {"north": {"north", "west"}, "east": U4, "south": {"south", "west"}, "west": {"west"}},
}
def compose(d1, d2): return frozenset(_T4[d1][d2])
def gt_str(r): return "UNDET" if len(r) == 4 else "|".join(d for d in ORDER if d in r)
def klass(r): return "definite" if len(r) == 1 else ("underdetermined" if len(r) == 4 else "disjunctive")
def fix_moji(s):
    """Repair UTF-8-read-as-latin1 mojibake in Welsh names (the source TTL is valid UTF-8 but was
    parsed as latin1 during assembly, mangling 1,238 place names). Targeted and reversible."""
    if not s or not re.search(r"[ÃÂÅÄ]", s):
        return s
    try:
        return s.encode("latin1").decode("utf-8")
    except Exception:
        return s

def eng(n):
    n = fix_moji(n or "")
    return n.split(" - ")[-1].strip() if " - " in n else n.strip()
def norm(s): return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()

FAMOUS_EXACT = {norm(x) for x in [
 "Cardiff","Caerdydd","Swansea","Abertawe","Newport","Casnewydd","Wrexham","Wrecsam","Bangor",
 "Aberystwyth","Llandudno","St Davids","St David's","Tyddewi","Merthyr Tydfil","Barry","Y Barri",
 "Caernarfon","Conwy","Carmarthen","Caerfyrddin","Llanelli","Bridgend","Neath","Castell-nedd",
 "Port Talbot","Pontypridd","Rhyl","Colwyn Bay","Aberdare","Cwmbran","Ebbw Vale","Monmouth",
 "Brecon","Abergavenny","Chepstow","Tenby","Pembroke","Haverfordwest","Milford Haven","Cardigan",
 "Machynlleth","Dolgellau","Betws-y-Coed","Portmeirion","Harlech","Criccieth","Pwllheli","Holyhead",
 "Beaumaris","Llangollen","Hay-on-Wye","Mold","Flint","Denbigh","Ruthin","Welshpool","Newtown",
 "Builth Wells","Llandrindod Wells","Bala","Prestatyn","Porthcawl","Mumbles","Rhossili"]}
FAMOUS_SUBSTR = [norm(x) for x in [
 "snowdon","yr wyddfa","wyddfa","cadair idris","cader idris","pen y fan","brecon beacon","bannau",
 "tryfan","glyder","carnedd","crib goch","pumlumon","plynlimon","aran fawddwy","sugar loaf","skirrid",
 "blorenge","great orme","little orme","worms head","worm s head","three cliffs","preseli","elan valley",
 "vyrnwy","llyn tegid","bala lake","devil s bridge","swallow falls","pistyll rhaeadr","menai",
 "pendine sands","barafundle","whitesands","freshwater west","gower","offa s dyke"]]
def famous(name):
    n = norm(name)
    return n in FAMOUS_EXACT or any(p and p in n for p in FAMOUS_SUBSTR)

# ---------------- units (admin community + community ward), from the regenerated graph ----------
unit_name, unit_ok = {}, set()
for u in json.load(open(os.path.join(LOAD, "nodes_Unit.json"))):
    p = u["props"]
    if "/admin/" in u["uri"] and p.get("unit_type") in ("COMMUNITY", "COMMUNITY WARD") and p.get("unit_name"):
        unit_ok.add(u["uri"]); unit_name[u["uri"]] = eng(p["unit_name"])
uc = defaultdict(int)
for x in unit_ok: uc[norm(unit_name[x])] += 1
unit_collide = {x for x in unit_ok if uc[norm(unit_name[x])] > 1}

unit_prim = defaultdict(list)          # anchor -> [(primary, sector_word)]
for t, w in WORD.items():
    for e in json.load(open(os.path.join(LOAD, f"edges_{t}.json"))):
        if e["from"] in unit_ok and e["to"] in unit_ok:
            unit_prim[e["to"]].append((e["from"], w))

# ---------------- places, from the regenerated graph + one-ring layer ---------------------------
place_name, place_cat = {}, {}
for p in json.load(open(os.path.join(LOAD, "nodes_Place.json"))):
    pr = p["props"]
    if pr.get("place_name", "").strip():
        place_name[p["uri"]] = eng(pr["place_name"]); place_cat[p["uri"]] = pr.get("place_type")
pcc = defaultdict(int)
for x, n in place_name.items(): pcc[norm(n)] += 1
place_collide = {x for x, n in place_name.items() if pcc[norm(n)] > 1}
def salience(uri): return "salient" if place_cat.get(uri) == "populated place" else "non_salient"

place_prim = defaultdict(list)
for e in json.load(open(os.path.join(HERE, "place_primaries_oneRing_frame4.json"))):
    place_prim[e["to"]].append((e["from"], WORD[e["type"]]))

# ---------------- item construction ------------------------------------------------------------
def build(prim, names, collide, etype, ok):
    stored = {(a, b) for b, lst in prim.items() for (a, _d) in lst}
    items = []
    for B, lst in prim.items():                                   # depth 1
        for (A, d) in lst:
            if A == B or A in collide or B in collide: continue
            if not ok(A) or not ok(B): continue
            items.append(dict(cls="definite", depth=1, A=A, B=B, M=None, d1=d, d2=None, res=frozenset({d})))
    chains = defaultdict(list)                                    # depth 2
    for B, lst in prim.items():
        for (M, d1) in lst:
            for (A, d2) in prim.get(M, ()):
                if A == B or A == M or M == B: continue
                if (A, B) in stored: continue
                chains[(A, B)].append((M, d1, d2, compose(d1, d2)))
    for (A, B), cl in chains.items():
        if len({c[3] for c in cl}) != 1: continue                 # chains disagree -> drop
        if A in collide or B in collide or not ok(A) or not ok(B): continue
        pick = next((c for c in sorted(cl, key=lambda c: c[0]) if c[0] not in collide and ok(c[0])), None)
        if not pick: continue
        M, d1, d2, res = pick
        items.append(dict(cls=klass(res), depth=2, A=A, B=B, M=M, d1=d1, d2=d2, res=res))
    for it in items: it["etype"] = etype; it["names"] = names
    return items

unit_items = build(unit_prim, unit_name, unit_collide, "unit", lambda x: True)
place_items = build(place_prim, place_name, place_collide, "place",
                    lambda x: x in place_name and not famous(place_name[x]))

# ---------------- stratified sampling ----------------------------------------------------------
TARGET = [("definite", 1, "unit", 8), ("definite", 1, "place", 7),
          ("definite", 2, "unit", 7), ("definite", 2, "place", 8),
          ("disjunctive", 2, "unit", 15), ("disjunctive", 2, "place", 15),
          ("underdetermined", 2, "unit", 15), ("underdetermined", 2, "place", 15)]
pool = defaultdict(list)
for it in unit_items + place_items: pool[(it["cls"], it["depth"], it["etype"])].append(it)
for k in pool: pool[k].sort(key=lambda it: (it["A"], it["B"], it["M"] or ""))

chosen, achieved, short = [], {}, []
for cls, dep, et, n in TARGET:
    cand = pool.get((cls, dep, et), [])
    if et == "place":                       # >= 1/3 non-salient within each place stratum
        ns = [i for i in cand if salience(i["A"]) == "non_salient" and salience(i["B"]) == "non_salient"]
        k = -(-n // 3)
        pick = random.sample(ns, min(k, len(ns)))
        picked = {(i["A"], i["B"]) for i in pick}
        rest = [i for i in cand if (i["A"], i["B"]) not in picked]
        pick += random.sample(rest, min(n - len(pick), len(rest)))
    else:
        pick = random.sample(cand, min(n, len(cand)))
    achieved[(cls, dep, et)] = (len(pick), n, len(cand))
    if len(pick) < n: short.append((cls, dep, et, len(pick), n, len(cand)))
    chosen += pick

# ---------------- export -----------------------------------------------------------------------
rows = []
for i, it in enumerate(sorted(chosen, key=lambda x: (x["cls"], x["depth"], x["etype"], x["A"])), 1):
    nm = it["names"]; A, B, M = it["A"], it["B"], it["M"]
    An, Bn = nm[A], nm[B]
    if it["depth"] == 1:
        p1, p2, Mn, Mid = f"{An} is the primary {it['d1']} neighbour of {Bn}", "", "", ""
    else:
        Mn, Mid = nm[M], M
        p1 = f"{Mn} is the primary {it['d1']} neighbour of {Bn}"
        p2 = f"{An} is the primary {it['d2']} neighbour of {Mn}"
    sal = "n/a" if it["etype"] == "unit" else (
        "non_salient" if salience(A) == "non_salient" and salience(B) == "non_salient" else "salient")
    rows.append({"item_id": f"P{i:03d}", "class": it["cls"], "depth": it["depth"],
                 "entity_type": it["etype"], "salience_flag": sal,
                 "A_id": A, "A_name": An, "B_id": B, "B_name": Bn, "M_id": Mid, "M_name": Mn,
                 "premise_1": p1, "premise_2": p2, "ground_truth": gt_str(it["res"]), "seed": SEED})
out = os.path.join(HERE, "probe_set_4sector.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["item_id","class","depth","entity_type","salience_flag","A_id","A_name",
                                      "B_id","B_name","M_id","M_name","premise_1","premise_2","ground_truth","seed"])
    w.writeheader(); w.writerows(rows)

print(f"SEED = {SEED}    items = {len(rows)}   -> {out}\n")
print("achieved strata (picked / target / pool available):")
for (cls, dep, et), (got, tgt, cand) in achieved.items():
    print(f"  {cls:15s} depth{dep} {et:5s}: {got:2d}/{tgt:2d}    pool {cand}")
print("\nSHORTFALLS:", short if short else "none")
pl = [r for r in rows if r["entity_type"] == "place"]
ns = [r for r in pl if r["salience_flag"] == "non_salient"]
print(f"\nplace items {len(pl)}; non-salient {len(ns)} (need >= {-(-len(pl)//3)})")
print(f"excluded by name collision: {len(unit_collide)} unit URIs, {len(place_collide)} place URIs")
print(f"class totals: " + str({c: sum(1 for r in rows if r['class']==c) for c in ('definite','disjunctive','underdetermined')}))
