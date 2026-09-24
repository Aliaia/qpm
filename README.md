# The Qualitative Place Model (QPM) — ontology and artefacts, version 1.1

QPM is a qualitative model of the *location of places* for geographic knowledge
graphs. It represents where a place is relationally — through containment paths
within one or more spatial hierarchies and lateral relations (adjacency,
direction, proximity) to peer places — rather than through coordinate geometry
alone. The model stores a **minimal generating set** of relations (one-step
containment, topological adjacency, one primary neighbour per directional
sector) from which the qualitative completion of a scene is derived by
reasoning.

- **Ontology IRI:** https://w3id.org/qpm — **version:** 1.1 — **versionIRI:** https://w3id.org/qpm/1.1 — **prior version:** https://w3id.org/qpm/1.0
  The GeoSPARQL import is preserved rather than merged, so a reasoner needs network access or a local copy of the GeoSPARQL ontology.
- **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), see `LICENSE`, for the ontology and the authors' own artefacts. Files that carry Ordnance Survey-derived content are used under the Open Government Licence and carry the attribution in `ATTRIBUTION.md`.
- **Creator:** Alia I. Abdelmoty.

## Versions

| Version | File | versionIRI | Status |
|---|---|---|---|
| 1.1 | `qpm.ttl` (canonical) and `qpm-1.1.ttl` (frozen, identical) | https://w3id.org/qpm/1.1 | current |
| 1.0 | `qpm-1.0.ttl` (frozen; byte-identical to `qpm.ttl` at tag `v1.0`) | https://w3id.org/qpm/1.0 | superseded, kept unchanged |

Both versions use the same namespace, `https://w3id.org/qpm#`, and the same
local names for the same concepts: every class and property of 1.0 is in 1.1
under the same name. Version 1.1 adds one declared property, `qpm:placeKey`
(reserved; populated in no released dataset), carries `owl:priorVersion`, and is
accompanied by corrected SHACL shapes (`qpm-shapes.ttl`: one advisory shape
deactivated rather than evaluated, one shape corrected for a unit that belongs to
two hierarchies, and one shape split so that a reported-not-gated condition is
`sh:Info` rather than a violation). Data that conforms to 1.0 conforms to 1.1.
Earlier, unpublished drafts of the ontology used snake_case local names
(`contained_by`, `place_key`, …); data written against those drafts is **not**
interchangeable with either published version despite sharing the namespace.

## Release notes — 1.1 (13 September 2026)

- `qpm:placeKey` declared (datatype property on `qpm:Place`); reserved, populated in no released dataset.
- `owl:versionIRI` https://w3id.org/qpm/1.1, `owl:priorVersion` https://w3id.org/qpm/1.0, `dct:modified` 2026-09-13.
- Shapes: `PrimaryDirectionalNoInterveningUnit` is `sh:deactivated` (its `FILTER(false)` was evaluated by rdflib and suppressed nothing, so it reported 14,860 spurious violations); `UnitParentSameHierarchy` now requires child and parent to *share* a hierarchy, which the country root, a member of two, satisfies (27 spurious violations); `DescribedPlaceHasProvenance` is split, and the `sourced ⇒ sourceId` half is `SourcedPlaceHasIdentifier` at `sh:Info`.
- Validation of the Wales deployment against these shapes (as RDF: 931,770 triples; 52,821 basic places plus 5 composite places with 131 `partOf` assertions; the deployed property graph holds 122,319 nodes, 52,826 of them places, and 905,317 relationships) reports **0 violations and 375 `sh:Info` results**. The zero follows from the severity change above: under the 1.0 shapes the same 375 nodes were violations. They are 370 source-layer points for which the source supplies no OS identifier (369 unmatched in the current OpenMap Local edition and 1 ambiguous match, kept deliberately and reported as they are) and 5 curated places with a name but no OS identifier; the absence is structural in the source, not an omission of the RDF. pySHACL prints `Conforms: False` whenever any result exists, whatever its severity, so a run over this data reads `Conforms: False` with no violation.
- Composite places in the Wales deployment are **declared** (name, class, verified part and leaf-unit counts), not detected; detection was tried and withdrawn on 14 September 2026 because the source data underdetermine membership.
- **Deployment revised 22 September 2026 (ontology and shapes unchanged).** Five hand-curated Cardiff places, appended to the place layer in 2025 for a demonstration composite, were established to be OpenStreetMap features rather than Ordnance Survey ones and were removed, so that the deployment has one data source (Ordnance Survey OpenData) and one data licence; the curated civic composite went with them, and the four remaining composites are all declared. The figures above therefore read, for the current deployment: **931,692 triples; 52,816 basic places plus 4 composite places with 126 `partOf` assertions; 122,308 nodes, 52,820 of them places, and 905,234 relationships; 0 violations and 370 `sh:Info` results**, all of them `SourcedPlaceHasIdentifier` on the 370 source-layer points described above. The five removed rows were the "5 curated places with a name but no OS identifier" of the 13 September note. The 13 September figures stand as the record of that date.
- Data conforming to 1.0 conforms to 1.1; the local names are unchanged.
- **Tag `v1.1` re-pointed, 24 September 2026 (documentation only; ontology, shapes and `owl:versionIRI` unchanged).** The tag was first cut on 13 September at `7ba647c`. `ATTRIBUTION.md` (the Ordnance Survey attribution statement for the grounding-study files) and the `LICENSE` carve-out of those files from the CC BY 4.0 claim, together with the corrected citation line (1.1, not 1.0), were added after that, so a reader following https://w3id.org/qpm/1.1 reached a tree without them. The tag was moved to the commit carrying these files so that the version IRI resolves to a tree that states the licence position in full. No term of the licence and no file of the ontology changed; anyone who pinned `7ba647c` holds the same ontology, shapes and profile, less the attribution and licence statements added here.

## What is in this repository

| Path | What it is |
|---|---|
| `qpm.ttl` | The QPM ontology, version 1.1 (OWL, Turtle). Part A is the normative core; Part B is a documented non-normative annex. |
| `qpm-1.1.ttl` | Frozen copy of the 1.1 ontology, identical to `qpm.ttl` at this release. |
| `qpm-1.0.ttl` | Frozen copy of the 1.0 ontology as published (tag `v1.0`). Never modified. |
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

## Attribution

The grounding study (`grounding-study/`) names places and units drawn from a knowledge graph built from Ordnance
Survey OpenData products (OS OpenMap Local, OS Boundary-Line, OS Code-Point Open), used under the Open Government
Licence v3.0. Wherever that content appears:

> Contains OS data © Crown copyright and database right 2026.
> Contains Royal Mail data © Royal Mail copyright and database right 2026.
> Contains National Statistics data © Crown copyright and database right 2026.

`ATTRIBUTION.md` says which files, and states the licence position in full.

## Citation

Please cite the accompanying paper, *The Qualitative Place Model* (Abdelmoty, in submission),
and this repository at https://w3id.org/qpm (version 1.1).
