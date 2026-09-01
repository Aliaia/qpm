# QPM Property-Graph Profile, version 1.0

**Status:** 31 August 2026. Derived from the canonical paper (Abdelmoty, *The Qualitative Place Model*) and the QPM Canonical Specification v0.5, and from the canonical ontology (qpm.ttl, version 1.0). This profile is the contract between the QPM ontology and any Neo4j deployment of it, and it is the stable surface for the summer 2026 MSc projects: everything in Section 2 is frozen for the summer; everything the ontology may later revise is invisible behind it. It also serves as the checklist for the pre-handover cleanup and regeneration (Section 6).

**The decoupling principle.** Consumers of the graph (students, the live application, query tooling) depend on this profile, never on the OWL directly. The ontology names and structures may evolve; the profile absorbs the changes. The one standing example: the ontology class is `qpm:BasicPlace`, but the graph label is `Place`, preserving the deployed surface.

---

## 1. Mapping from ontology to graph

### 1.1 Node labels

| Graph label | Ontology class | Notes |
|---|---|---|
| `Place` | `qpm:BasicPlace` | The label name predates the class rename and is retained deliberately. |
| `Unit` | `qpm:Unit` | Includes grid cells when abstract hierarchies are loaded. |
| `Hierarchy` | `qpm:Hierarchy` | |
| `Country` | `qpm:Country` | |
| `Geometry` | `qpm:Geometry` | |
| `PlaceProvenance` | `qpm:PlaceProvenance` | Annex; optional, present only if described places are loaded. |

The `qpm:Place` superclass has no graph label of its own; queries over all places use `(n:Place OR n:Unit)` patterns, as the live application already does. The umbrella label `QPMEntity` and the schema-node labels (`OntologyClass`, `QPMClass`, `OntologyProperty`, `QPMProperty`) are retired: they were loader conveniences, not model content, and the regenerated graph does not carry them. If a TBox graph (the ontology definitions as a graph) is wanted at all, it is deployed as a separate database, never mixed into the data graph.

### 1.2 Relationship types

Stored relationships follow the minimal generating set: one edge per asserted fact, in the canonical direction only. The previous practice of materialising inverse pairs is retired, for two reasons: inverse edges double the graph for no traversal benefit (Neo4j traverses both directions natively), and for the directional relations the auto-inverse was semantically wrong, since the inverse of a primary fact is a general directional fact, not a primary one (that B is A's chosen northern neighbour does not make A B's chosen southern neighbour).

| Graph type | Ontology property | Direction stored | Semantics |
|---|---|---|---|
| `BELONGS_TO_HIERARCHY` | `qpm:belongsToHierarchy` | Unit to Hierarchy | Exactly one per Unit. |
| `CONTAINED_BY` | `qpm:containedBy` | child Unit to parent Unit | One-step; same hierarchy; level minus 1. Ancestry derived by traversal. |
| `CONTAINED_BY_UNIT` | `qpm:containedByUnit` | Place to Unit | One per relevant hierarchy (validation V1). |
| `BASE_PLACE_PARENT` | `qpm:basePlaceParent` | child Place to parent Place | Place nesting; composites and parts; depth derived. |
| `TOUCHES` | `qpm:touches` | one edge per unordered pair | New in 1.0. Full adjacency between same-level, same-hierarchy Units. Stored once per pair; query ignoring direction. |
| `NORTH_OF`, `SOUTH_OF`, `EAST_OF`, `WEST_OF` | `qpm:primaryNorthOf` etc. | neighbour to anchor | **Primary semantics**: the source node is the anchor's one chosen neighbour in that sector. Functional per anchor per sector (validation V5). Not transitive; do not chain these types expecting general direction. |
| `HAS_MAIN_GEOMETRY` | `qpm:hasMainGeometry` | Place or Unit to Geometry | At most one (validation V6). Hard-coded in the live application; name frozen. |
| `HAS_EXTRA_GEOMETRY` | `qpm:hasExtraGeometry` | Place or Unit to Geometry | Unbounded. |
| `HAS_HIERARCHY` | `qpm:hasHierarchy` | Country to Hierarchy | |
| `HAS_PROVENANCE` | `qpm:hasProvenance` | Place to PlaceProvenance | Annex; optional. |
| `INVOLVED_PLACE` | `qpm:involvedPlace` | PlaceProvenance to Place | Annex; optional. |

**Retired types** (present in pre-1.0 data, absent from the regenerated graph): `HAS_CHILD_UNIT`, `CHILD_OF_UNIT`, `BASE_PLACE_CHILD` (inverse duplicates), and any auto-generated directional inverses. Queries traverse `CONTAINED_BY` in reverse instead of matching `HAS_CHILD_UNIT`.

**Derived, never stored** (by design, not omission): ancestral containment, general cardinal direction, all proximity grades (`close`, `near`, `far`, `very far`), cross-hierarchy relations, composite-place unit containment, nesting depth. Section 3 gives the traversal patterns.

### 1.3 Node properties

**Stable properties** (frozen for summer 2026):

| Label | Properties |
|---|---|
| `Place` | `place_name`, `place_type`, `place_function` (optional), `place_origin` (annex: `sourced` or `described`), `source_id`, `source_dataset` (for sourced places), `uri` |
| `Unit` | `unit_name`, `unit_type`, `unit_level` (integer, 0 = root), `source_id`, `source_dataset`, `uri` |
| `Hierarchy` | `hierarchy_name`, `hierarchy_levels`, `units_number`, `uri` |
| `Country` | `name`, `uri` |
| `Geometry` | `wkt` (plain string; the profile's deliberate flattening of `geo:wktLiteral`), `geometry_type` (`Point` or `Polygon`), `geometry_role` (`main` or `extra`; derivable, kept for convenience), `uri` |

Value vocabularies are lowercase throughout (`main`, `extra`, `sourced`, `described`).

`uri` is the entity's canonical IRI. Data IRIs are source-scoped under the data namespace, pattern `https://w3id.org/qpm/data/os/W04000945`; described places without a source identifier are minted under `https://w3id.org/qpm/data/local/` with stable opaque suffixes.

**Deployment-local properties** (permitted, not part of the model; consumers must tolerate their presence and never require them): the legacy integer keys `place_id`, `spatial_unit_id`, `hierarchy_id`; the convenience fields `name`, `longitude`, `latitude` on Geometry; and, if retained after the cleanup decision, the drift fields `subject`, `subject2`, `type2`. The profile permits unknown additional properties in general.

### 1.4 Constraints and indexes

```cypher
CREATE CONSTRAINT qpm_uri_unique IF NOT EXISTS
FOR (n:Place) REQUIRE n.uri IS UNIQUE;
CREATE CONSTRAINT qpm_unit_uri_unique IF NOT EXISTS
FOR (n:Unit) REQUIRE n.uri IS UNIQUE;
CREATE CONSTRAINT qpm_geom_uri_unique IF NOT EXISTS
FOR (n:Geometry) REQUIRE n.uri IS UNIQUE;
CREATE CONSTRAINT qpm_hier_uri_unique IF NOT EXISTS
FOR (n:Hierarchy) REQUIRE n.uri IS UNIQUE;

CREATE INDEX qpm_place_name IF NOT EXISTS FOR (n:Place) ON (n.place_name);
CREATE INDEX qpm_unit_name  IF NOT EXISTS FOR (n:Unit)  ON (n.unit_name);
CREATE INDEX qpm_place_type IF NOT EXISTS FOR (n:Place) ON (n.place_type);
CREATE INDEX qpm_unit_type  IF NOT EXISTS FOR (n:Unit)  ON (n.unit_type);
CREATE INDEX qpm_source_id  IF NOT EXISTS FOR (n:Unit)  ON (n.source_id);
```

---

## 2. The stability contract

Frozen for summer 2026: every name in the tables of Section 1 (labels, relationship types, stable properties), their semantics as stated, the lowercase value vocabularies, and the derivation patterns of Section 3. Free to change without notice: anything marked annex or deployment-local, the OWL axioms behind the profile, the contents of Part B of the ontology, and any property or type not listed here. Additions to the graph (new relationship types, new properties) are permitted at any time and are not breaking changes; consumers must be written to tolerate unknown types and properties, which the live application already is.

Compatibility note: the live application's hard-coded surface (`Place`, `Unit`, `Geometry`, `HAS_MAIN_GEOMETRY`, `place_name`, `unit_name`, `place_type`, `unit_type`, `wkt`) is a strict subset of the frozen surface, so the application runs unmodified against any conforming graph.

---

## 3. Derivation patterns

The graph stores the minimal generating set; these patterns derive the rest. They are the operational form of the ontology's reasoning semantics.

**P1. Ancestral containment of a unit** (transitive closure of one-step containment):

```cypher
MATCH (u:Unit {unit_name: $name})-[:CONTAINED_BY*1..]->(a:Unit)
RETURN a.unit_name, a.unit_level;
```

**P2. The containment path of a place per hierarchy** (the answer to "Where is X?", once per frame of reference):

```cypher
MATCH (p:Place {place_name: $name})-[:CONTAINED_BY_UNIT]->(u:Unit)
      -[:BELONGS_TO_HIERARCHY]->(h:Hierarchy)
OPTIONAL MATCH path = (u)-[:CONTAINED_BY*0..]->(root:Unit)
WHERE NOT (root)-[:CONTAINED_BY]->()
RETURN h.hierarchy_name,
       [n IN nodes(path) | n.unit_name] AS containment_path;
```

**P3. Neighbours (all, then the chosen primaries)**:

```cypher
MATCH (u:Unit {unit_name: $name})-[:TOUCHES]-(n:Unit)
RETURN n.unit_name;                                     // all neighbours

MATCH (n:Unit)-[r:NORTH_OF|SOUTH_OF|EAST_OF|WEST_OF]->(u:Unit {unit_name: $name})
RETURN type(r) AS sector, n.unit_name AS primary_neighbour;
```

**P4. Graded proximity by traversal** (close: distance 1; near: distance at most 2; far: beyond 2 up to k_far):

```cypher
MATCH (u:Unit {unit_name: $name})-[:TOUCHES*1..2]-(v:Unit)
WHERE u <> v
RETURN DISTINCT v.unit_name;                            // near (includes close)

MATCH p = shortestPath((u:Unit {unit_name: $name})-[:TOUCHES*..6]-(v:Unit))
WHERE u <> v AND length(p) > 2 AND length(p) <= $k_far
RETURN DISTINCT v.unit_name;                            // far
```

**P5. Host-derived proximity for places** (places are near if their host units in the chosen hierarchy are near):

```cypher
MATCH (p:Place {place_name: $name})-[:CONTAINED_BY_UNIT]->(u:Unit)
      -[:BELONGS_TO_HIERARCHY]->(:Hierarchy {hierarchy_name: $hier})
MATCH (u)-[:TOUCHES*0..2]-(v:Unit)<-[:CONTAINED_BY_UNIT]-(q:Place)
WHERE q <> p
RETURN DISTINCT q.place_name;
```

**P6. Cross-hierarchy intersection by shared-place inference** (no geometry needed; a place contained in units of two hierarchies witnesses their intersection):

```cypher
MATCH (u:Unit)<-[:CONTAINED_BY_UNIT]-(p:Place)-[:CONTAINED_BY_UNIT]->(v:Unit)
MATCH (u)-[:BELONGS_TO_HIERARCHY]->(h1), (v)-[:BELONGS_TO_HIERARCHY]->(h2)
WHERE h1 <> h2
RETURN u.unit_name, v.unit_name, count(p) AS witnessing_places;
```

**P7. Composite places: derived unit containment and derived depth**:

```cypher
MATCH (part:Place)-[:BASE_PLACE_PARENT]->(comp:Place {place_name: $name})
MATCH (part)-[:CONTAINED_BY_UNIT]->(u:Unit)
RETURN DISTINCT u.unit_name;                            // the composite's units, derived

MATCH p = (x:Place {place_name: $name})-[:BASE_PLACE_PARENT*0..]->(top:Place)
WHERE NOT (top)-[:BASE_PLACE_PARENT]->()
RETURN length(p) AS nesting_depth;                      // depth, derived
```

A caution that belongs in any teaching material: chaining the directional types (`NORTH_OF*2..`) does not compute general direction, because those edges carry primary semantics. General direction between non-neighbours is derived by the composition reasoning described in the specification, not by naive traversal of the primaries.

---

## 4. Validation queries

Run after any load or regeneration; every query must return zero rows. These are the Cypher equivalents of the SHACL shapes (qpm-shapes.ttl).

**V1. Per-hierarchy uniqueness of place containment:**

```cypher
MATCH (p:Place)-[:CONTAINED_BY_UNIT]->(u1:Unit)-[:BELONGS_TO_HIERARCHY]->(h),
      (p)-[:CONTAINED_BY_UNIT]->(u2:Unit)-[:BELONGS_TO_HIERARCHY]->(h)
WHERE u1 <> u2
RETURN p.place_name, h.hierarchy_name;
```

**V2. Unit parent in the same hierarchy:**

```cypher
MATCH (c:Unit)-[:CONTAINED_BY]->(p:Unit)
MATCH (c)-[:BELONGS_TO_HIERARCHY]->(h1), (p)-[:BELONGS_TO_HIERARCHY]->(h2)
WHERE h1 <> h2
RETURN c.unit_name, p.unit_name;
```

**V3. Level adjacency and root integrity:**

```cypher
MATCH (c:Unit)-[:CONTAINED_BY]->(p:Unit)
WHERE p.unit_level <> c.unit_level - 1
RETURN c.unit_name AS child, c.unit_level AS child_level,
       p.unit_name AS parent, p.unit_level AS parent_level
UNION
MATCH (u:Unit)
WHERE (u.unit_level = 0 AND (u)-[:CONTAINED_BY]->())
   OR (u.unit_level > 0 AND NOT (u)-[:CONTAINED_BY]->())
RETURN u.unit_name AS child, u.unit_level AS child_level,
       null AS parent, null AS parent_level;
```

(Note: both arms of the `UNION` must return identically-named columns, hence the aliases; an earlier published form returned unnamed `null, null` columns that Neo4j rejects as duplicate result columns.)

**V4. Touches well-formedness** (same level, same hierarchy, no self-loops, one edge per pair):

```cypher
MATCH (a:Unit)-[:TOUCHES]-(b:Unit)
MATCH (a)-[:BELONGS_TO_HIERARCHY]->(h1), (b)-[:BELONGS_TO_HIERARCHY]->(h2)
WHERE a = b OR h1 <> h2 OR a.unit_level <> b.unit_level
RETURN a.unit_name, b.unit_name
UNION
MATCH (a:Unit)-[:TOUCHES]->(b:Unit)-[:TOUCHES]->(a)
RETURN a.unit_name, b.unit_name;                        // duplicate reverse edges
```

**V5. Primary functionality and the no-intervening-unit rule.** A unit's directional primary is its nearest neighbour in that sector among same-root units, with no intervening unit between them; in a partition it touches (the normal case), but a natural separation (river, estuary) permits a non-touching primary, and a sector with no qualifying unit has no primary. So V5 has two parts.

Part 5a, functionality, is pure-graph (at most one primary per sector per anchor):

```cypher
MATCH (n)-[r:NORTH_OF|SOUTH_OF|EAST_OF|WEST_OF]->(a)
WITH a, type(r) AS sector, count(*) AS c WHERE c > 1
RETURN a.uri, sector, c;
```

Part 5b, the no-intervening-unit check, is geometric and is run in the regeneration/validation pipeline (it needs the unit polygons and a sector/between computation that Cypher cannot express), not as a graph query. It confirms that for each unit primary there is no other same-root unit lying between the primary and the base unit in that sector, applied with a generous tolerance since the relation is qualitative. Note that this replaces the earlier "primary must touch" check: touching is the expected outcome in a partition, not a requirement, so a non-touching primary across an empty separation passes, while a primary with an intervening unit (the upstream nearest-centroid heuristic reaching across other units) fails. The pipeline reports any failing primaries with the intervening unit(s) identified. This part does not apply to BasicPlace primaries, which are nearest-in-sector with no adjacency notion (points do not touch).

A diagnostic-only graph approximation, for spotting candidates before the geometric check, flags unit primaries that are neither touching nor plausibly across an empty gap:

```cypher
MATCH (n:Unit)-[r:NORTH_OF|SOUTH_OF|EAST_OF|WEST_OF]->(a:Unit)
WHERE NOT (n)-[:TOUCHES]-(a)
RETURN a.uri, type(r), n.uri;   // candidates for the geometric between-test, not failures
```

**V6. Geometry cardinality** (at most one main geometry per entity):

```cypher
MATCH (n)-[:HAS_MAIN_GEOMETRY]->(g)
WITH n, count(g) AS c WHERE c > 1
RETURN n.uri, c;
```

**V7. Hierarchy membership** (every unit in exactly one hierarchy):

```cypher
MATCH (u:Unit)
WITH u, size([(u)-[:BELONGS_TO_HIERARCHY]->() | 1]) AS c
WHERE c <> 1
RETURN u.unit_name, c;
```

**V8. Place-origin consistency** (annex; only if described places are loaded):

```cypher
MATCH (p:Place)
WHERE (p.place_origin = 'described' AND NOT (p)-[:HAS_PROVENANCE]->())
   OR (p.place_origin = 'sourced' AND p.source_id IS NULL)
RETURN p.place_name, p.place_origin;
```

---

## 5. What the graph deliberately does not contain

Recorded so absences are read as design, not gaps: no inverse-pair edge types; no materialised proximity, general direction, ancestral containment, nesting depth, or cross-hierarchy relations (all derived, Section 3); no schema or TBox nodes in the data graph; and no `QPMEntity` umbrella label. The H3 and S2 grid-index properties, when present, are deployment-local and not part of the normative model.

---

## 6. Regeneration and cleanup checklist (pre-handover)

Gathered from the specification decisions; this is the work plan for the server sessions.

1. **Loader changes:** emit `TOUCHES` (the adjacency the loader already computes and currently discards), one edge per pair; emit directional primaries as asserted facts only, no auto-inverses; stop emitting `HAS_CHILD_UNIT`, `CHILD_OF_UNIT`, `BASE_PLACE_CHILD`; stop emitting the `QPMEntity` and schema labels; mint source-scoped IRIs into `uri`; write `source_id` and `source_dataset` from the AGI identifiers; map `model_source`/`geometry_source` forward to `place_origin` (basic, given to sourced; salient, computed to described) and drop the old property names; lowercase all value vocabularies.
2. **Name fixes:** Qualitative Place Model everywhere; the QPD expansion corrected in any regenerated BigData artefacts.
3. **Decide and apply the drift-field fate** (`subject`, `subject2`, `type2`): confirm their origin in the BigData import pipeline, then define them as deployment-local or drop them; if dropping, smoke-test the application's search paths (they appear only inside COALESCE-style filters, so degradation should be graceful).
4. **Run validations V1 to V8**; zero rows each before deployment.
5. **Redeploy and smoke-test the live application** against the hard-coded surface (Section 2 compatibility note); check `TOUCHES` appears in the relationship dropdown and behaves.
6. **Credentials closeout in the same session:** confirm the Neo4j password rotation completed; untrack the committed credential files; replace the real password in `.env.example` with a placeholder.
7. **Refresh the package documents** (manifest, README, student guide) against this profile; retire references to removed labels and inverse types; add the Section 3 patterns to the sample queries.
