# Part B — results: closed-book vs open-book directional reasoning

**Model:** `gpt-4o-2024-08-06` (pinned) · **Run:** 2026-07-19T23:19:33Z ·
**temperature** 0 · **max_tokens** 800 (uniform) · **no system prompt** · fresh request per item ·
**prompts frozen** (the one permitted change was never spent) · item set **seed 20260620**.

180 requests: 90 closed book (loop 1), then 90 open book (loop 2). Stability block run separately.

## Headline

| condition | strict | consistent |
|---|---:|---:|
| **1 — closed book** (no facts) | **23/90 · 25.6%** | 34/90 · 37.8% |
| **2 — open book** (graph premises + rule) | **73/90 · 81.1%** | 74/90 · 82.2% |

Supplying the stored primaries and the composition rule raises strict accuracy **3.2×**
(25.6% → 81.1%). The graph carries the reasoning; the model alone cannot do this task on these
entities.

## By class

| class | n | closed strict | closed consistent | open strict | open consistent |
|---|---:|---:|---:|---:|---:|
| definite | 30 | 6 · 20.0% | 6 · 20.0% | **30 · 100.0%** | 30 · 100.0% |
| disjunctive | 30 | 0 · 0.0% | 11 · 36.7% | **29 · 96.7%** | 30 · 100.0% |
| underdetermined | 30 | 17 · 56.7% | 17 · 56.7% | **14 · 46.7%** | 14 · 46.7% |

Definite items are answered **perfectly** open book (30/30, and 15/15 at *both* depth 1 and depth
2 — one composition step costs nothing). Disjunctive items are near-perfect (29/30).

**The striking result: underdetermined items get *worse* with the premises** — 46.7% open book
against 56.7% closed book. Given facts and an explicit "opposite yields no conclusion" rule, the
model becomes *more* likely to assert a direction, not less.

## Failure mode — the model will not say "no conclusion"

All 16 open-book errors but one fall in the underdetermined class. Two distinct mechanisms:

**1. Opposite misclassified as adjacent (8 of 16).** The model explicitly applies the wrong branch
of the stated rule. Verbatim (P066):

> "West (Tyddyn-y-Bluen from Pontwgan) composed with East (Cefn Farmhouse from Tyddyn-y-Bluen)
> yields a set containing both west and east, **as they are adjacent directions**."

East and west are opposite. The rule for opposite is *no conclusion*; the model instead returns
the union, answering `east|west`. This is a rule-application error, not a knowledge gap.

**2. Informal path/vector reasoning overriding the rule (the remainder).** Verbatim (P063):

> "if we move north from Nant y Creau to Cefnen Wen and then south to Hafod-y-dre-uchaf, we are
> essentially moving back towards the original position … Therefore … the direction … is south."

The model traces movement along the chain and reports a net direction, bypassing the calculus.

Error distribution on underdetermined items: `east|west` ×8, `north|east` ×2, plus single
definite answers (`south`, `west`, `north`). The single disjunctive error was
`GT=north|east → east` — a *narrowing* of a correct set, the same over-commitment in milder form.

**Reading:** the model's competence is in *propagating* definite and disjunctive relations, and
its failure is concentrated exactly on the indefinite region — the same region the completeness
measure identified as the structural floor. It manufactures a determinate answer where the
calculus says nothing follows.

## Closed-book behaviour — the blanket-response check

Answer distribution (90 items): `UNDET` 48 (53.3%), `north` 15, `east` 13, `south` 7, `west` 6,
`south|west` 1.

The model is **not** answering UNDET indiscriminately, but it does over-produce it (53.3% against
a 33.3% ground-truth base rate), which inflates its underdetermined score. Meanwhile its accuracy
on **definite** items is **20.0% — below the 25% chance level** for a four-way choice. Taken
together: it has essentially **no usable geographic knowledge of these entities**, and its
closed-book "successes" on underdetermined items are largely a by-product of guessing UNDET.
This validates the salience design — the probe set is genuinely outside the model's knowledge.

## Salience, entity type, depth (open book)

| cut | n | strict |
|---|---:|---:|
| unit pairs | 45 | 80.0% |
| place pairs | 45 | 82.2% |
| salient places | 27 | 77.8% |
| **non-salient places** | 18 | **88.9%** |
| definite depth 1 | 15 | 100.0% |
| definite depth 2 | 15 | 100.0% |

Non-salient (topographic-tail) places score **higher** than salient ones — consistent with the
open-book task being pure derivation from supplied facts: where the model has no prior
associations, there is nothing to interfere. Unit and place performance is effectively equal.

## Parse quality (footnotes)

- **0 unparseable, 0 truncated, 0 API errors** across all 180 responses (`finish_reason: stop`
  throughout). The 800-token cap was sufficient.
- Cascade usage: stage (a) exact final-line match **61**, stage (b) last direction-statement after
  stripping verbatim premises **119**. No response required hand-correction.
- Strict and consistent scores nearly coincide open book (81.1% vs 82.2%) because the model does
  emit sets when asked; they diverge closed book (25.6% vs 37.8%) because condition 1 forbids sets,
  so disjunctive items are unreachable under strict scoring by construction.

## Correction note (scoring, post-run — disclosed)

After the run, two closed-book rows were found to be **mis-parsed, not unparseable**: the stage-(b)
scan was reading the prompt's *own option list* — quoted back by the model ("…classified as exactly
one of north, east, south, or west…") — as if it were the answer, yielding a spurious four-way set.

The parser was corrected (not the rows: no result was hand-edited). The rule added is general and
follows from the answer space: under a four-sector frame a valid answer is one direction, a
two-direction set, or "cannot be determined", so **an enumeration of three or more directions can
never be an answer** and is stripped before scanning, exactly as the verbatim premises already are.
All 180 responses were then re-scored from the raw file with `score_partB.py`.

Effect — 2 rows, 3 fields:

| item | field | before | after |
|---|---|---|---|
| P038 c1 | parsed | `north\|east\|south\|west` | `north` (score unchanged — still wrong vs GT `south\|west`) |
| P057 c1 | parsed | `north\|east\|south\|west` | `north` |
| P057 c1 | consistent_correct | False | **True** (GT `north\|east`) |

Consequent figure changes: closed-book **consistent 33→34/90 (36.7→37.8%)** and closed-book
**disjunctive consistent 10→11/30**. No strict score changed; the open-book condition is entirely
unaffected; parse stages and the zero unparseable/zero truncated footnotes are unchanged.

## Stability

Fifteen `disjunctive_place` items rerun three times at temperature 0: **14/15 gave identical
answers across all three repeats**; one item (P037) returned `east` once and `north|east` twice —
a single-item flip between a narrowing and the correct set, consistent with the mild
over-commitment seen elsewhere.

## Caveats

- Underdetermined ground truth is the **derivable ceiling**, not the real world: those places do
  have a true direction, so a closed-book model answering "south" may be geographically right yet
  scored wrong. The comparison is like-for-like across conditions, but the closed-book
  underdetermined number should not be read as spatial competence.
- One composition step only; the probe set does not test deeper chains.
- Single model, single run (plus the stability block); no cross-model claim is made.
