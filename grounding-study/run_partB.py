"""
Part B — querying protocol. 90-item probe set, two conditions, one pinned OpenAI model.
Run where the OpenAI API is reachable (not the analysis sandbox).

  pip install openai
  export OPENAI_API_KEY=sk-...
  python run_partB.py --model gpt-4o-2024-08-06 --pilot      # 6 items (2/class), both conditions
  python run_partB.py --model gpt-4o-2024-08-06              # full 180: 90 closed, then 90 open
  python run_partB.py --model gpt-4o-2024-08-06 --stability disjunctive_place   # 15 x 3, separate
  python run_partB.py --model gpt-4o-2024-08-06 --score-only # rescore from raw, no API calls

PROMPTS ARE FROZEN AND UNCHANGED. The pilot revealed a parameter problem, not prompt ambiguity,
so the one permitted prompt fix remains in reserve.

Parameters: temperature 0, max_tokens 200 (uniform for both conditions), no system prompt,
fresh independent request per item.

Answer parsing — conclusion-first cascade:
  (a) exact allowed-answer string in the final line/sentence;
  (b) else the last direction-statement in the response AFTER stripping the verbatim premises;
  (c) else unparseable -> scores wrong, footnoted, never hand-corrected.
Any response with finish_reason == "length" (still truncated at 200) scores as unparseable and is
flagged. No re-queries.
"""
import os, sys, csv, json, re, time, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = os.path.join(HERE, "probe_set_4sector.csv")
RAW = os.path.join(HERE, "partB_raw_responses.jsonl")
RESULTS = os.path.join(HERE, "partB_results.csv")
DIRS = ["north", "east", "south", "west"]
MAX_TOKENS = 800          # raised from 200: the model reasons at length before concluding.
                          # Parameter-only fix; prompts remain frozen. Override with --max-tokens.
TEMPERATURE = 0

# ---------------- verbatim prompts (FROZEN) ----------------
COND1 = ("Consider two locations in Wales: {A_name} and {B_name}. Using a four-sector "
         "compass frame, in which every direction is classified as exactly one of north, "
         "east, south, or west, what is the direction of {A_name} from {B_name}? If the "
         "direction cannot be determined, say so. Answer with exactly one of: north, "
         "east, south, west, cannot be determined.")

COND2 = ("The following facts are drawn from a validated spatial knowledge graph of "
         "Wales. Directions use a four-sector compass frame (north, east, south, west). "
         "'X is the primary north neighbour of Y' means X is the nearest neighbour of Y "
         "within the northern sector; likewise for the other sectors.\n"
         "Facts:\n{facts}\n"
         "Composition rule: a direction composed with itself yields itself; a direction "
         "composed with its opposite yields no conclusion; a direction composed with an "
         "adjacent direction yields the set containing both.\n"
         "Question: using only the facts and the rule, what can be concluded about the "
         "direction of {A_name} from {B_name}? Answer with exactly one of: north, east, "
         "south, west, a set such as 'north or east', or: cannot be determined.")

def build_prompt(cond, it):
    if cond == 1:
        return COND1.format(A_name=it["A_name"], B_name=it["B_name"])
    facts = "\n".join(p for p in (it["premise_1"], it["premise_2"]) if p.strip())
    return COND2.format(facts=facts, A_name=it["A_name"], B_name=it["B_name"])

# ---------------- answer parsing / scoring: SINGLE SOURCE ----------------
# Parsing and scoring live in score_partB.py so the runner and the standalone scorer can never
# diverge. run_partB.py imports them; it defines no copy of its own.
from score_partB import parse_answer, parse_gt, score, score_file, DIRS  # noqa: E402

# ---------------- API ----------------
def call(client, model, prompt, retries=5):
    """-> (text, finish_reason, error)"""
    for a in range(retries):
        try:
            r = client.chat.completions.create(
                model=model, temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}])
            c = r.choices[0]
            return c.message.content, c.finish_reason, None
        except Exception as e:
            if a == retries - 1:
                return None, None, f"{type(e).__name__}: {e}"
            time.sleep(2 ** a)
    return None, None, "unreachable"

def run_loop(client, model, items, cond, path, tag):
    ok = 0
    with open(path, "a", encoding="utf-8") as f:
        for i, it in enumerate(items, 1):
            prompt = build_prompt(cond, it)
            text, fin, err = call(client, model, prompt)
            f.write(json.dumps({
                "block": tag, "item_id": it["item_id"], "condition": cond, "model": model,
                "run_date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "finish_reason": fin, "response": text, "error": err, "prompt": prompt,
                "premise_1": it["premise_1"], "premise_2": it["premise_2"],
                "class": it["class"], "depth": int(it["depth"]), "entity_type": it["entity_type"],
                "salience_flag": it["salience_flag"], "ground_truth": it["ground_truth"],
            }, ensure_ascii=False) + "\n")
            f.flush()
            ok += err is None
            print(f"\r  {tag} cond{cond}: {i}/{len(items)} (ok {ok})", end="", flush=True)
    print()
    return ok

# ---------------- scoring (reads raw; never re-queries) ----------------
def do_score():
    """Delegates to score_partB.score_file — the single source of scoring truth."""
    score_file(RAW, RESULTS)


# ---------------- main ----------------
def main():
    global MAX_TOKENS
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="exact pinned model string, e.g. gpt-4o-2024-08-06")
    ap.add_argument("--pilot", action="store_true", help="6 items (2 per class), both conditions")
    ap.add_argument("--stability", default=None, help="stratum for the 3x rerun, e.g. disjunctive_place")
    ap.add_argument("--score-only", action="store_true", help="rescore existing raw file, no API calls")
    ap.add_argument("--max-tokens", type=int, default=MAX_TOKENS,
                    help=f"completion cap, uniform for both conditions (default {MAX_TOKENS})")
    a = ap.parse_args()
    MAX_TOKENS = a.max_tokens          # applied to every request and recorded in the metadata

    if a.score_only:
        do_score(); return

    from openai import OpenAI
    client = OpenAI()
    items = list(csv.DictReader(open(ITEMS, encoding="utf-8")))
    meta = {"record": "run_metadata", "model": a.model,
            "run_date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS, "system_prompt": None,
            "prompts_frozen": True, "n_items": len(items),
            "seed_of_item_set": items[0]["seed"], "conditions": {"1": "closed book", "2": "open book"}}

    if a.pilot:
        sel = []
        for cls in ("definite", "disjunctive", "underdetermined"):
            c = [i for i in items if i["class"] == cls]
            if cls == "definite":                       # one depth-1 and one depth-2
                sel += [next(i for i in c if i["depth"] == "1"), next(i for i in c if i["depth"] == "2")]
            else:
                sel += c[:2]
        print(json.dumps(meta | {"record": "pilot_metadata", "n_pilot_items": len(sel)}, indent=2))
        clean = True
        for it in sel:
            for cond in (1, 2):
                p = build_prompt(cond, it)
                text, fin, err = call(client, a.model, p)
                pred, stage = parse_answer(text, (it["premise_1"], it["premise_2"]), fin)
                shown = "UNPARSEABLE" if pred is None else ("UNDET" if pred == {"UNDET"}
                        else "|".join(d for d in DIRS if d in pred))
                st, co = score(pred, parse_gt(it["ground_truth"]))
                if stage in ("unparseable", "truncated"): clean = False
                print(f"\n[{it['item_id']} {it['class']} d{it['depth']} cond{cond}] GT={it['ground_truth']}"
                      f"\n  response      : {text!r}"
                      f"\n  finish_reason : {fin}   parse_stage: {stage}"
                      f"\n  parsed        : {shown}   strict={st} consistent={co}   {err or ''}")
        print("\n" + ("RE-PILOT CLEAN — no truncation, all responses parsed. Safe to run the full 180."
                      if clean else
                      "RE-PILOT NOT CLEAN — truncated/unparseable responses present. Do not run yet."))
        print("Pilot writes no files.")
        return

    if a.stability:
        cls, et = a.stability.rsplit("_", 1)
        sub = [i for i in items if i["class"] == cls and i["entity_type"] == et]
        path = os.path.join(HERE, "partB_stability_raw.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(meta | {"record": "stability_metadata", "stratum": a.stability,
                                       "n": len(sub), "repeats": 3}) + "\n")
        for rep in (1, 2, 3):
            run_loop(client, a.model, sub, 2, path, f"stability_rep{rep}")
        print(f"stability block -> {path} (separate from the main 180)")
        return

    # full run: raw saved with item_id, condition, model, run date, finish_reason BEFORE scoring
    with open(RAW, "w", encoding="utf-8") as f:
        f.write(json.dumps(meta) + "\n")
    print(f"model={a.model}  run_date={meta['run_date_utc']}  max_tokens={MAX_TOKENS}\nraw -> {RAW}")
    run_loop(client, a.model, items, 1, RAW, "main")     # loop 1: all 90 closed book
    run_loop(client, a.model, items, 2, RAW, "main")     # loop 2: all 90 open book
    print("\nraw responses complete; scoring now (raw file is already safe on disk)")
    do_score()

if __name__ == "__main__":
    main()
