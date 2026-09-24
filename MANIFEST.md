# QPM release — manifest

sha256 shown as first 12 hex.

## Files to publish

| File | sha256[:12] | Notes |
|---|---|---|
| `qpm.ttl` | `493ccf3ab55a` | The QPM ontology, version 1.1 (canonical serialization). camelCase property names; 78 `qpm:` entities (1.0 had 77: `qpm:placeKey` added, reserved and unpopulated); owl:versionIRI /1.1, owl:priorVersion /1.0; CC BY 4.0. |
| `qpm-1.1.ttl` | `493ccf3ab55a` | Frozen copy of the 1.1 ontology, byte-identical to `qpm.ttl` at this release. |
| `qpm-1.0.ttl` | `e5d81d0a00f1` | Frozen copy of the 1.0 ontology as published (tag `v1.0`, sha256[:12] e5d81d0a00f1). Never modified. |
| `qpm.owl` | `4661162fd2f0` | RDF/XML serialization of `qpm.ttl` v1.1, regenerated with `robot convert` on 2026-09-13. `robot diff` reports zero axioms present in `qpm.ttl` and absent from `qpm.owl` (the 33 extra axioms in the .owl are ROBOT's annotation-property declarations); same 78 `qpm:` entities; GeoSPARQL import preserved; asserted axioms only. |
| `qpm-shapes.ttl` | `7e809b8edb52` | SHACL shapes, v1.1: `PrimaryDirectionalNoInterveningUnit` sh:deactivated (its FILTER(false) was evaluated and suppressed nothing); `UnitParentSameHierarchy` requires child and parent to SHARE a hierarchy; `DescribedPlaceHasProvenance` split, with `SourcedPlaceHasIdentifier` at sh:Info (see README, release notes 1.1). Every property it references is defined in `qpm.ttl`. |
| `QPM_PropertyGraph_Profile_v1.0.md` | `e21c2561bd82` | Property-graph deployment contract. Ontology-property refs camelCase; graph surface (`NORTH_OF`, `place_name`, …) deliberately unchanged; Status line refreshed (31 Aug 2026 / paper / spec v0.5). |
| `composition_tables.json` | `27971505dc9a` | 4- and 8-sector cone tables; breakdown verified 4/8/4 and 8/48/8. |
| `QPM_Provenance.md` | `ffb88c69f464` | Provenance document (author-supplied). §7 "What is not claimed" — keep verbatim. Clean of signposts. |
| `validation/validate.py` | `e4ecefc8cd22` | Property-graph checks V1–V8. |
| `validation/geometric_checks.py` | `4e2bab95ad8c` | Geometric checks: place-in-leaf + unit-in-parent. |
| `validation/validation_V1_V8.cypher` | `6a659344d058` | V1–V8 as Cypher. |
| `grounding-study/PARTB_RESULTS.md` | `12d78c48d6b9` | Model-grounding study artefact. |
| `grounding-study/README_partB.md` | `0c0ccda2537b` | Model-grounding study artefact; carries the Ordnance Survey attribution for the folder (22 September 2026). |
| `grounding-study/generate_probe_set.py` | `8468a4942cbf` | Model-grounding study artefact. |
| `grounding-study/partB_raw_responses.jsonl` | `9f5edec9c955` | Model-grounding study artefact. |
| `grounding-study/partB_results.csv` | `dd1ce67c4765` | Model-grounding study artefact. |
| `grounding-study/partB_stability_raw.jsonl` | `33ead40b7382` | Model-grounding study artefact. |
| `grounding-study/probe_set_4sector.csv` | `0a16f7f77fa1` | Model-grounding study artefact. |
| `grounding-study/run_partB.py` | `29b26def8872` | Model-grounding study artefact. |
| `grounding-study/score_partB.py` | `9cbf6bdb1b4b` | Model-grounding study artefact. |
| `ATTRIBUTION.md` | `00fbcf37faa0` | Ordnance Survey OpenData attribution and the licence position per file; added 22 September 2026, correcting an omission in the published grounding-study files. |
| `README.md` | `718ec324b251` | Repository README, with the version table, the 1.1 release notes, the two 22 September 2026 deployment revisions (removal; provenance), the record of the v1.1 tag re-pointing (24 September) and the Attribution section. |
| `LICENSE` | `8c25b8a909c0` | CC BY 4.0 full legal code + attribution header (Alia I. Abdelmoty). 24 Sep 2026: the OS-derived grounding-study files carved out of the CC BY 4.0 claim (OGL v3.0, see `ATTRIBUTION.md`); citation line corrected to version 1.1. |

## Verification record — 1.1 (2026-09-13)

- `tools/validate_ontology.py` (parse, meta-SHACL, shapes/ontology agreement, dangling references, naming, header, OWL RL closure): 0 errors, 1 warning (`dct:title` absent; the file carries `dc:title`).
- qpm.owl: regenerated from qpm.ttl with `robot convert` (ROBOT 1.9.7, OpenJDK 24). `robot diff` reports zero axioms present in qpm.ttl and absent from qpm.owl.
- SHACL against the Wales deployment as RDF (`qpm-wales-1.1.nt`, 2026-09-14: 931,770 triples, 52,821 basic places, 5 composite places, 131 `partOf`; property graph 122,319 nodes / 905,317 relationships), pySHACL 0.40.1: **0 `sh:Violation`, 0 `sh:Warning`, 375 `sh:Info`** — every one from `SourcedPlaceHasIdentifier`. Read together with the shape change: under the 1.0 shapes those 375 were violations of `DescribedPlaceHasProvenance`, and it is the split at `sh:Info` in this release that makes the count zero. pySHACL prints `Conforms: False` for results of any severity, so a run against this data will say `Conforms: False` with no violation; the earlier expectation of `Conforms: True` was mistaken.
- The 375: all `qpm:BasicPlace` (of 52,821), `sourceId` absent not empty. 370 are points of the source layer (OS OpenMap Local NamedPlace, SO square) for which the current edition of the product supplies no feature by exact coordinate (369) or two (1); they are kept deliberately and reported as they are. 5 are curated Cardiff civic places with a name but no OS identifier. The source carries no authoritative identifier for them, so the absence is structural in the source; the RDF is complete relative to it. (On 13 September this cohort was 8,541; 8,166 attributes were recovered from the product's April-2026 SO tile before this validation.) The count of places without an identifier is a recorded property of the deployment, not a validation failure.
- Composite places: 5, declared in the deployment's configuration (4 rivers with verified part and leaf-unit counts, 1 curated demonstration); detection withdrawn 2026-09-14.

## Verification record — 1.0

- Reasoning: ROBOT 1.9.7 with HermiT 1.4.3.517. Consistent, no unsatisfiable classes.
- ROBOT report: 0 errors. The 57 missing_definition warnings concern the OBO IAO:0000115 convention, which this ontology does not use; definitions are carried in rdfs:comment.
- qpm.owl: generated from qpm.ttl with robot convert. robot diff reports zero axioms present in qpm.ttl and absent from qpm.owl. GeoSPARQL import preserved, asserted axioms only.
- SHACL: qpm-shapes.ttl validated with pySHACL 0.40.1 against a data sample including known edge cases.
