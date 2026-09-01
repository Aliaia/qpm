# The Qualitative Place Model (QPM) — ontology and artefacts, version 1.0

QPM is a qualitative model of the *location of places* for geographic knowledge
graphs. It represents where a place is relationally — through containment paths
within one or more spatial hierarchies and lateral relations (adjacency,
direction, proximity) to peer places — rather than through coordinate geometry
alone. The model stores a **minimal generating set** of relations (one-step
containment, topological adjacency, one primary neighbour per directional
sector) from which the qualitative completion of a scene is derived by
reasoning.

- **Ontology IRI:** https://w3id.org/qpm — **version:** 1.0 — **versionIRI:** https://w3id.org/qpm/1.0
  The GeoSPARQL import is preserved rather than merged, so a reasoner needs network access or a local copy of the GeoSPARQL ontology.
- **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), see `LICENSE`.
- **Creator:** Alia I. Abdelmoty.

## What is in this repository

| Path | What it is |
|---|---|
| `qpm.ttl` | The QPM ontology (OWL, Turtle). Part A is the normative version-1.0 core; Part B is a documented non-normative annex. |
| `qpm.owl` | The same ontology in RDF/XML, generated from `qpm.ttl`. A convenience serialisation; `qpm.ttl` is canonical. |
| `qpm-shapes.ttl` | Companion SHACL shapes enforcing the constraints OWL cannot express (per-hierarchy containment uniqueness, unit parent hierarchy and level adjacency, root integrity, touches well-formedness, composite-place parts, place-origin consistency). |
| `QPM_PropertyGraph_Profile_v1.0.md` | The property-graph profile: the stable contract between the ontology and any Neo4j deployment (node labels, relationship types, properties, derivation patterns, and validation queries). |
| `composition_tables.json` | Machine-readable directional composition (cone) tables at four and eight sectors: each cell gives the derived direction set for one composition step (definite / disjunctive / universal). |
| `validation/` | The validation suite: `validate.py` (property-graph checks V1–V8), `geometric_checks.py` (two geometric checks — place-in-leaf and unit-in-parent), and `validation_V1_V8.cypher` (the same checks as Cypher). |
| `grounding-study/` | Archive of the model-grounding study: the 90-item probe set (`probe_set_4sector.csv`), the run/scoring scripts and prompt templates (`run_partB.py`, `score_partB.py`, `README_partB.md`), the raw model responses (`partB_raw_responses.jsonl`, `partB_stability_raw.jsonl`), and results (`partB_results.csv`, `PARTB_RESULTS.md`). |
| `QPM_Provenance.md` | Provenance of the artefact — sources, element-by-element lineage, divergences the canonical model resolves, and the closing statement of what is not claimed. |
| `MANIFEST.md` | The source and integrity of each file in this release. |
| `LICENSE` | CC BY 4.0. |

## How to use it

1. **Read / reason over the ontology.** Open `qpm.ttl` in an ontology editor
   (e.g. Protégé) or load it into an OWL reasoner to check consistency and
   class satisfiability. The ontology imports GeoSPARQL.
2. **Validate data.** Run the SHACL shapes (`qpm-shapes.ttl`) against your data
   with any SHACL engine (e.g. pySHACL). The property-graph profile gives corresponding checks as Cypher; the two sets overlap but are not identical - V6 and V7 have no SHACL counterpart, and CompositePlaceHasParts has no Cypher counterpart. `validation/validate.py` + `validation/geometric_checks.py` run them over a loaded graph.
3. **Deploy to a graph.** Follow `QPM_PropertyGraph_Profile_v1.0.md`. Consumers
   depend on the profile (the frozen surface), never on the OWL directly; the
   ontology may evolve behind the profile.
4. **Reproduce the grounding study.** See `grounding-study/README_partB.md`.

## Design in one paragraph

Only one-step links are stored; ancestry, general direction, graded proximity,
and cross-hierarchy relations are all **derived**, never materialised. Direction
uses a two-layer architecture: stored functional *primary* neighbours per sector
seed the derived, transitive general direction, whose composition follows the
cone tables in `composition_tables.json`. Places are located in one leaf unit per
hierarchy; distributed places are composites whose parts are nested places, so
each part keeps a unique parent per hierarchy. Full derivation rules and their
provenance are given in `qpm.ttl` (comments) and the profile.

## Citation

Please cite the accompanying paper, *The Qualitative Place Model* (Abdelmoty, in submission),
and this repository at https://w3id.org/qpm (version 1.0).
