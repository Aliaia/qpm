"""
score_partB.py — standalone scorer: raw responses -> scored per-item table.

Self-contained (no API, no imports from the runner) so it is an independent, auditable artefact.
The parsing/scoring logic is identical to that used in run_partB.py; re-running this on the
shipped raw file reproduces partB_results.csv exactly.

    python score_partB.py                                  # raw -> partB_results.csv
    python score_partB.py --raw X.jsonl --out Y.csv        # explicit paths

Parsing — conclusion-first cascade (never hand-corrected):
  (a) exact allowed-answer string in the final line/sentence
  (b) else the last direction-statement AFTER stripping the verbatim premises
  (c) else unparseable -> scores wrong, footnoted
Any response with finish_reason == "length" is treated as truncated -> unparseable.

Scoring:
  strict_correct     = parsed set == ground-truth set
  consistent_correct = parsed set is a non-empty subset of the ground-truth set
                       (condition 1 cannot express a two-sector set, so a single correct
                        member counts as consistent; report whichever fits the claim)
"""
import os, csv, json, re, argparse
from collections import Counter

DIRS = ["north", "east", "south", "west"]

UNDET_PAT = re.compile(r"can\s*not\s+be\s+determined|cannot\s+be\s+determined|can't\s+be\s+determined"
                       r"|undetermined|indeterminate|unknown|no\s+conclusion|cannot\s+determine",
                       re.I)
ALLOWED_EXACT = {d: {d} for d in DIRS}
ALLOWED_EXACT["cannot be determined"] = {"UNDET"}
for _x in DIRS:
    for _y in DIRS:
        if _x != _y:
            ALLOWED_EXACT[f"{_x} or {_y}"] = {_x, _y}

# An enumeration of THREE OR MORE directions is never a valid answer under the four-sector frame
# (allowed answers: one direction, a two-direction set, or "cannot be determined"). Such runs are
# the model quoting the prompt's own option list back ("...classified as exactly one of north,
# east, south, or west..."), so they are stripped before the stage-(b) scan, exactly as the
# verbatim premises are. Without this, the option list was read as the answer.
OPTION_ENUM = re.compile(r"(?:\b(?:north|east|south|west)\b[\s,]*(?:or\s+)?){3,}", re.I)

def _norm(s):
    return " ".join(s.lower().split()).strip().strip(".!;:,'\"")

def _sentences(text):
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+", (text or "").strip()) if p.strip()]

def parse_answer(text, premises=(), finish_reason=None):
    """-> (answer_set | None, stage); stage in {'a','b','truncated','unparseable'}"""
    if finish_reason == "length":
        return None, "truncated"
    if not text or not text.strip():
        return None, "unparseable"
    sents = _sentences(text)
    if sents and _norm(sents[-1]) in ALLOWED_EXACT:                 # (a)
        return set(ALLOWED_EXACT[_norm(sents[-1])]), "a"
    stripped = OPTION_ENUM.sub(" ", text)                            # (b) drop quoted option list
    for p in premises:
        if p and p.strip():
            stripped = re.sub(re.escape(p.strip()), " ", stripped, flags=re.I)
            stripped = re.sub(re.escape(" ".join(p.split())), " ", stripped, flags=re.I)
    for s in reversed(_sentences(stripped)):
        if UNDET_PAT.search(s):
            return {"UNDET"}, "b"
        found = {d for d in DIRS if re.search(r"\b" + d + r"\b", s, re.I)}
        if found:
            return found, "b"
    return None, "unparseable"                                       # (c)

def parse_gt(g):
    return {"UNDET"} if g.strip() == "UNDET" else set(g.split("|"))

def score(pred, gt):
    if pred is None:
        return (False, False)
    return (pred == gt, len(pred) > 0 and pred.issubset(gt))

def score_file(raw_path, out_path):
    """Raw JSONL -> scored CSV. Single source of truth for scoring (run_partB.py calls this)."""
    meta, rows, unparse, trunc = None, [], 0, 0
    for line in open(raw_path, encoding="utf-8"):
        r = json.loads(line)
        if r.get("record"):
            meta = r
            continue
        pred, stage = parse_answer(r["response"], (r.get("premise_1"), r.get("premise_2")),
                                   r.get("finish_reason"))
        gt = parse_gt(r["ground_truth"])
        st, co = score(pred, gt)
        unparse += stage in ("unparseable", "truncated")
        trunc += stage == "truncated"
        rows.append({"item_id": r["item_id"], "condition": r["condition"], "class": r["class"],
                     "depth": r["depth"], "entity_type": r["entity_type"],
                     "salience_flag": r["salience_flag"], "ground_truth": r["ground_truth"],
                     "response": (r["response"] or "").replace("\n", " ").strip(),
                     "finish_reason": r.get("finish_reason") or "", "parse_stage": stage,
                     "parsed": ("UNPARSEABLE" if pred is None else
                                ("UNDET" if pred == {"UNDET"} else "|".join(d for d in DIRS if d in pred))),
                     "strict_correct": st, "consistent_correct": co, "error": r.get("error") or ""})

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    print(f"model: {meta.get('model')}   run: {meta.get('run_date_utc')}   max_tokens={meta.get('max_tokens')}")
    for c in (1, 2):
        sub = [r for r in rows if r["condition"] == c]
        if not sub: continue
        st = sum(r["strict_correct"] for r in sub); co = sum(r["consistent_correct"] for r in sub)
        print(f"  condition {c} ({'closed' if c == 1 else 'open'} book): "
              f"strict {st}/{len(sub)} ({100*st/len(sub):.1f}%)  consistent {co}/{len(sub)} ({100*co/len(sub):.1f}%)")
        for cls in ("definite", "disjunctive", "underdetermined"):
            s2 = [r for r in sub if r["class"] == cls]
            if s2:
                print(f"      {cls:15s}: strict {sum(r['strict_correct'] for r in s2):2d}/{len(s2):2d}"
                      f"  consistent {sum(r['consistent_correct'] for r in s2):2d}/{len(s2):2d}")
    print("  parse stages:", dict(Counter(r["parse_stage"] for r in rows)))
    print(f"  FOOTNOTE: unparseable (scored wrong) = {unparse}, of which truncated = {trunc}")
    print(f"-> {out_path}")
    return rows

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.path.join(here, "partB_raw_responses.jsonl"))
    ap.add_argument("--out", default=os.path.join(here, "partB_results.csv"))
    a = ap.parse_args()
    score_file(a.raw, a.out)

if __name__ == "__main__":
    main()
