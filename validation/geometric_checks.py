"""
geometric_checks.py — permanent geometric enforcement of the model's spatial conditions,
run alongside validate.py (V1-V8). Two checks, both over the assembled load/ graph:

  G-place-in-leaf : every place's point lies inside its assigned leaf-unit polygon, per
                    hierarchy (the geometric ground of place->unit containment / leaf assignment).
  G-unit-in-parent: every child unit's polygon is contained in its parent's polygon by
                    area-majority (>=50% of interior samples), i.e. the geometric ground of
                    condition H2 (unit CONTAINED_BY). Boundary generalisation is absorbed by
                    the area-majority rule; units without a polygon are FLAGGED, not forced.

Place points: loader/truesource_places.json (WGS84). Unit polygons: load HAS_MAIN_GEOMETRY
(WGS84). Zero failures = pass; missing polygons are reported separately as flags.
"""
import os, re, json, collections
import numpy as np

HERE = os.path.dirname(__file__)
LOAD = os.path.join(os.path.dirname(HERE), "load")
def L(f): return json.load(open(os.path.join(LOAD, f)))

U = {u["uri"]: u["props"] for u in L("nodes_Unit.json")}
belongs = {e["from"]: e["to"] for e in L("edges_BELONGS_TO_HIERARCHY.json")}
Hn = {h["uri"]: h["props"]["hierarchy_name"] for h in L("nodes_Hierarchy.json")}
hof = lambda u: Hn.get(belongs.get(u))
lvl = lambda u: U.get(u, {}).get("unit_level")
hmg = {e["from"]: e["to"] for e in L("edges_HAS_MAIN_GEOMETRY.json")}
cby = {e["from"]: e["to"] for e in L("edges_CONTAINED_BY.json")}

need = set(hmg.values()); wkt = {}
for g in L("nodes_Geometry.json"):
    if g["uri"] in need:
        wkt[g["uri"]] = g["props"].get("wkt", "")

def edges_of(w):
    xi=[];yi=[];xj=[];yj=[]
    for rt in re.findall(r"\(([-0-9.,\s]+)\)", w):
        p=re.findall(r"(-?\d+\.\d+)\s+(-?\d+\.\d+)", rt)
        if len(p)>=4:
            a=np.array([(float(x),float(y)) for x,y in p])
            xi+=list(a[:,0]); yi+=list(a[:,1]); xj+=list(np.roll(a[:,0],1)); yj+=list(np.roll(a[:,1],1))
    if not xi: return None
    return (np.array(xi),np.array(yi),np.array(xj),np.array(yj))

EDG={}; BB={}
for u in U:
    if u in hmg and hmg[u] in wkt:
        e=edges_of(wkt[hmg[u]])
        if e is not None: EDG[u]=e; BB[u]=(e[0].min(),e[1].min(),e[0].max(),e[1].max())

def inside(edg, px, py):
    xi,yi,xj,yj=edg; py2=py[None,:]; px2=px[None,:]
    cond=((yi[:,None]>py2)!=(yj[:,None]>py2)); den=np.where((yj-yi)==0,1e-30,(yj-yi))
    xint=(xj-xi)[:,None]*(py2-yi[:,None])/den[:,None]+xi[:,None]
    return ((cond&(px2<xint)).sum(axis=0)%2==1)

# ---------------- G-place-in-leaf ----------------
ts = json.load(open(os.path.join(HERE, "truesource_places.json")))
BASE = "https://w3id.org/qpm/data"
ppt = {f"{BASE}/os/place_{pid}": (v["lon"], v["lat"]) for pid, v in ts.items()}
by_leaf = collections.defaultdict(list)
for e in L("edges_CONTAINED_BY_UNIT.json"):
    if e["from"] in ppt: by_leaf[e["to"]].append(e["from"])
pass_h = collections.Counter(); fail_h = collections.Counter(); flag_h = collections.Counter()
fails = []
for leaf, pls in by_leaf.items():
    h = hof(leaf)
    if leaf not in EDG:
        flag_h[h] += len(pls); continue
    px = np.array([ppt[p][0] for p in pls]); py = np.array([ppt[p][1] for p in pls])
    ins = inside(EDG[leaf], px, py)
    pass_h[h] += int(ins.sum()); fail_h[h] += int((~ins).sum())
    for p, ok in zip(pls, ins):
        if not ok: fails.append((h, p, leaf))

# ---------------- G-unit-in-parent ----------------
# Boundary-Line polygons cover the admin L2 communities that carry no graph polygon,
# so the community->UA level (H2) is verified rather than flagged.
try:
    import sys; sys.path.insert(0, os.path.join(HERE, "..", "diagnostic"))
    from bl_geom import BLStore
    from osgb import bng_to_wgs84
    _bl = BLStore(os.path.join(HERE, "..", ".."))
except Exception:
    _bl = None
def _w04(u):
    seg=u.split("/")[-1]
    if seg.startswith("community_syn_"): return seg.split("community_syn_")[1]
    m=re.match(r"(W04\d+)", seg); return m.group(1) if m else None
def bl_samples_wgs(u):
    if _bl is None: return None
    rings=_bl.by_code.get(_w04(u) or "")
    if not rings: return None
    xs=[q[0] for r in rings for q in r]; ys=[q[1] for r in rings for q in r]
    gx,gy=np.meshgrid(np.linspace(min(xs),max(xs),11),np.linspace(min(ys),max(ys),11))
    cxi=np.concatenate([np.array(r)[:,0] for r in rings]); cyi=np.concatenate([np.array(r)[:,1] for r in rings])
    cxj=np.concatenate([np.roll(np.array(r)[:,0],1) for r in rings]); cyj=np.concatenate([np.roll(np.array(r)[:,1],1) for r in rings])
    m=inside((cxi,cyi,cxj,cyj), gx.ravel(), gy.ravel()); bx=gx.ravel()[m]; by=gy.ravel()[m]
    if len(bx)<4: bx=np.array([sum(xs)/len(xs)]); by=np.array([sum(ys)/len(ys)])
    lo=[];la=[]
    for X,Y in zip(bx,by): a,b=bng_to_wgs84(X,Y); lo.append(a); la.append(b)
    return np.array(lo), np.array(la)
def samples(u):
    x0,y0,x1,y1=BB[u]
    for N in (12,24):
        gx,gy=np.meshgrid(np.linspace(x0,x1,N+1),np.linspace(y0,y1,N+1)); px=gx.ravel(); py=gy.ravel()
        m=inside(EDG[u],px,py)
        if m.sum()>=8: return px[m],py[m]
    return (px[m],py[m]) if m.sum()>=1 else (np.array([(x0+x1)/2]),np.array([(y0+y1)/2]))
up_pass=up_fail=up_flag=0; up_fails=[]
for c, p in cby.items():
    if p not in EDG: up_flag += 1; continue
    if c in EDG:
        px,py=samples(c)
    else:
        s = bl_samples_wgs(c) if (hof(c)=="Admin" and lvl(c)==2) else None
        if s is None: up_flag += 1; continue
        px,py = s
    frac = inside(EDG[p], px, py).mean()
    if frac >= 0.5: up_pass += 1
    else:
        up_fail += 1
        up_fails.append((hof(c), U[c].get("unit_name"), U.get(p,{}).get("unit_name"), round(float(frac),2)))

print("="*64); print("GEOMETRIC CHECKS (zero failures = pass; flags = missing polygon)"); print("="*64)
print("\nG-place-in-leaf (point inside assigned leaf polygon), per hierarchy:")
for h in ("Admin","Electoral","Postal"):
    tot=pass_h[h]+fail_h[h]
    st="PASS" if fail_h[h]==0 else f"*** {fail_h[h]} FAIL ***"
    print(f"  {h}: {pass_h[h]}/{tot} inside  {st}   (flagged missing-polygon leaves: {flag_h[h]})")
print("\nG-unit-in-parent (child area-majority in parent):")
st="PASS" if up_fail==0 else f"*** {up_fail} FAIL ***"
print(f"  {up_pass} pass, {up_fail} fail, {up_flag} flagged (missing polygon)  {st}")
for r in up_fails[:12]: print("     fail:", r)
json.dump({"place_in_leaf_fail": {h:fail_h[h] for h in ('Admin','Electoral','Postal')},
           "place_in_leaf_flag": {h:flag_h[h] for h in ('Admin','Electoral','Postal')},
           "unit_in_parent_fail": up_fail, "unit_in_parent_flag": up_flag},
          open(os.path.join(HERE, "geometric_checks_counts.json"), "w"))
