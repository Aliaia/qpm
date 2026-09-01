# Part B — querying protocol: how to run

**I could not run this from the analysis sandbox:** it has no OpenAI API key, no `openai` SDK,
and `api.openai.com` is blocked by the proxy (403 on CONNECT — the same allowlist that blocked
pip/npm). The 180 requests must run where the API is reachable. Everything else is ready.

## Run it

```bash
pip install openai
export OPENAI_API_KEY=sk-...

# 1. pilot on 3 held-out items first (protocol allows ONE prompt fix, then freeze)
python run_partB.py --model gpt-4o-2024-08-06 --pilot

# 2. the main run: 90 closed-book, then 90 open-book (two loops, not interleaved)
python run_partB.py --model gpt-4o-2024-08-06

# 3. optional stability: one 15-item stratum, 3 repeats, in a SEPARATE file
python run_partB.py --model gpt-4o-2024-08-06 --stability disjunctive_place
```

Pin an **exact dated model string** (e.g. `gpt-4o-2024-08-06`), not a floating alias, so the run
is reproducible.

## What it does (protocol compliance)

- temperature **0**, `max_tokens` **50**, **no system prompt** (single user message), a **fresh
  independent request** per item — no conversation state.
- **Loop 1 = all 90 closed book, then loop 2 = all 90 open book**, so the raw file is tidy and a
  partial failure is obvious.
- Both prompts are **verbatim** as specified.
- **Model string and run date (UTC) are the first record** of the raw file.
- Responses are appended and flushed **per request**, so an interrupted run is recoverable and
  the failure point is visible. Failed calls retry 5× with backoff and are recorded with `error`.
- The **stability block is written to its own file** (`partB_stability_raw.jsonl`) and cannot
  contaminate the main 180.

## Answer parsing

Case/whitespace normalised. `cannot/can't be determined`, `undetermined`, `unknown`,
`no conclusion`, `indeterminate` → **UNDET**. Set answers matched **order-insensitively**
(`"east or north"` = `"north or east"`). Anything unparseable **scores wrong** and is counted in
a footnote line.

## Outputs

| file | contents |
|---|---|
| `partB_raw_responses.jsonl` | metadata record, then one record per request (prompt, raw response, error, timestamp) |
| `partB_results.csv` | scored: condition, item, class, depth, entity_type, salience, ground_truth, response, parsed, strict_correct, consistent_correct |
| `partB_stability_raw.jsonl` | the separate 15×3 stability block |

## Two judgements I made — flagged, not hidden

**1. Depth-1 items in the open-book condition.** Those items have only `premise_1`, so the
`Facts:` block would otherwise contain a trailing blank line. I emit the single fact with no blank
line. (Verified in the rendered prompt above.)

**2. Closed-book scoring of non-definite items.** Condition 1 restricts the model to a *single*
direction or "cannot be determined", so it **cannot express a two-sector set** — yet 30 items have
disjunctive ground truth. Rather than pick a scoring rule for you, every response is scored twice:

- **`strict_correct`** — exact match with the ground truth (a disjunctive item is only correct if
  the answer names both sectors; unreachable in closed book by construction).
- **`consistent_correct`** — the answer is a non-empty subset of the ground truth (naming one of
  the two permissible sectors counts).

Report whichever fits the claim; both are in the CSV so nothing needs re-running.

**Related design note (not a bug):** for the 30 **underdetermined** items, the graph's answer is
UNDET, but in the real world those places *do* have a definite direction. A closed-book model
answering "south" may be geographically right yet scored wrong against UNDET. That is inherent to
measuring against the derivable ceiling rather than the real scene, as specified — worth a
sentence in the write-up so the closed-book numbers aren't misread.
