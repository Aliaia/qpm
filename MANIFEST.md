# QPM release — manifest

sha256 shown as first 12 hex.

## Files to publish

| File | sha256[:12] | Notes |
|---|---|---|
| `qpm.ttl` | `e5d81d0a00f1` | The QPM ontology, version 1.0 (canonical serialization). camelCase property names; Annex properties revised; CC BY 4.0; paper-aligned. |
| `qpm.owl` | `5e555b07ff0c` | RDF/XML serialization of `qpm.ttl` (Protégé). Convenience copy; the `.ttl` is canonical. Verified: same 77 `qpm:` entities as the `.ttl`, ontology IRI `https://w3id.org/qpm`, GeoSPARQL import preserved (not merged), **asserted axioms only** (no inferred axioms materialized). |
| `qpm-shapes.ttl` | `848fae152c42` | SHACL shapes, camelCase; every property it references is defined in `qpm.ttl` (no dangling). |
| `QPM_PropertyGraph_Profile_v1.0.md` | `e21c2561bd82` | Property-graph deployment contract. Ontology-property refs camelCase; graph surface (`NORTH_OF`, `place_name`, …) deliberately unchanged; Status line refreshed (31 Aug 2026 / paper / spec v0.5). |
| `composition_tables.json` | `27971505dc9a` | 4- and 8-sector cone tables; breakdown verified 4/8/4 and 8/48/8. |
| `QPM_Provenance.md` | `ffb88c69f464` | Provenance document (author-supplied). §7 "What is not claimed" — keep verbatim. Clean of signposts. |
| `validation/validate.py` | `e4ecefc8cd22` | Property-graph checks V1–V8. |
| `validation/geometric_checks.py` | `4e2bab95ad8c` | Geometric checks: place-in-leaf + unit-in-parent. |
| `validation/validation_V1_V8.cypher` | `6a659344d058` | V1–V8 as Cypher. |
| `grounding-study/PARTB_RESULTS.md` | `12d78c48d6b9` | Model-grounding study artefact. |
| `grounding-study/README_partB.md` | `a29319524f46` | Model-grounding study artefact. |
| `grounding-study/generate_probe_set.py` | `8468a4942cbf` | Model-grounding study artefact. |
| `grounding-study/partB_raw_responses.jsonl` | `9f5edec9c955` | Model-grounding study artefact. |
| `grounding-study/partB_results.csv` | `dd1ce67c4765` | Model-grounding study artefact. |
| `grounding-study/partB_stability_raw.jsonl` | `33ead40b7382` | Model-grounding study artefact. |
| `grounding-study/probe_set_4sector.csv` | `0a16f7f77fa1` | Model-grounding study artefact. |
| `grounding-study/run_partB.py` | `29b26def8872` | Model-grounding study artefact. |
| `grounding-study/score_partB.py` | `9cbf6bdb1b4b` | Model-grounding study artefact. |
| `README.md` | `84558a903cb5` | Repository README. |
| `LICENSE` | `93714b5f775e` | CC BY 4.0 full legal code + attribution header (Alia I. Abdelmoty). |

## Verification record

- Reasoning: ROBOT 1.9.7 with HermiT 1.4.3.517. Consistent, no unsatisfiable classes.
- ROBOT report: 0 errors. The 57 missing_definition warnings concern the OBO IAO:0000115 convention, which this ontology does not use; definitions are carried in rdfs:comment.
- qpm.owl: generated from qpm.ttl with robot convert. robot diff reports zero axioms present in qpm.ttl and absent from qpm.owl. GeoSPARQL import preserved, asserted axioms only.
- SHACL: qpm-shapes.ttl validated with pySHACL 0.40.1 against a data sample including known edge cases.
