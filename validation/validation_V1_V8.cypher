// QPM Property-Graph Profile v1.0 — Section 4 validation queries (V1–V8).
// Run each against the LOADED local database (e.g. :use qpm_rebuild first in cypher-shell /
// Browser). Every query must return ZERO rows. These are the real Cypher equivalents of the
// pure-Python/numpy checks already passed; running them here confirms the queries themselves.

// ---- V1. Per-hierarchy uniqueness of place containment ----
MATCH (p:Place)-[:CONTAINED_BY_UNIT]->(u1:Unit)-[:BELONGS_TO_HIERARCHY]->(h),
      (p)-[:CONTAINED_BY_UNIT]->(u2:Unit)-[:BELONGS_TO_HIERARCHY]->(h)
WHERE u1 <> u2
RETURN p.place_name, h.hierarchy_name;

// ---- V2. Unit parent in the same hierarchy ----
MATCH (c:Unit)-[:CONTAINED_BY]->(p:Unit)
MATCH (c)-[:BELONGS_TO_HIERARCHY]->(h1), (p)-[:BELONGS_TO_HIERARCHY]->(h2)
WHERE h1 <> h2
RETURN c.unit_name, p.unit_name;

// ---- V3. Level adjacency and root integrity ----
MATCH (c:Unit)-[:CONTAINED_BY]->(p:Unit)
WHERE p.unit_level <> c.unit_level - 1
RETURN c.unit_name, c.unit_level, p.unit_name, p.unit_level
UNION
MATCH (u:Unit)
WHERE (u.unit_level = 0 AND (u)-[:CONTAINED_BY]->())
   OR (u.unit_level > 0 AND NOT (u)-[:CONTAINED_BY]->())
RETURN u.unit_name, u.unit_level, null, null;

// ---- V4. Touches well-formedness (same level, same hierarchy, no self-loop, one per pair) ----
MATCH (a:Unit)-[:TOUCHES]-(b:Unit)
MATCH (a)-[:BELONGS_TO_HIERARCHY]->(h1), (b)-[:BELONGS_TO_HIERARCHY]->(h2)
WHERE a = b OR h1 <> h2 OR a.unit_level <> b.unit_level
RETURN a.unit_name, b.unit_name
UNION
MATCH (a:Unit)-[:TOUCHES]->(b:Unit)-[:TOUCHES]->(a)
RETURN a.unit_name, b.unit_name;

// ---- V5a. Primary functionality (at most one primary neighbour per sector per anchor) ----
MATCH (n1)-[r:NORTH_OF|SOUTH_OF|EAST_OF|WEST_OF]->(a)
WITH a, type(r) AS sector, count(*) AS c WHERE c > 1
RETURN a.uri, sector, c;

// ---- V5b. Adjacency grounding for UNIT primaries (a unit's primary is a touching neighbour).
//      NOTE: the revised V5 (shape PrimaryDirectionalNoInterveningUnit) makes the geometric
//      "no intervening unit" test a PIPELINE check; the loader derives primaries from TOUCHES,
//      so this graph form holds for units by construction. Run it to confirm zero rows. ----
MATCH (n:Unit)-[r:NORTH_OF|SOUTH_OF|EAST_OF|WEST_OF]->(a:Unit)
WHERE NOT (n)-[:TOUCHES]-(a)
RETURN a.uri, type(r), 1;

// ---- V6. Geometry cardinality (at most one main geometry per entity) ----
MATCH (n)-[:HAS_MAIN_GEOMETRY]->(g)
WITH n, count(g) AS c WHERE c > 1
RETURN n.uri, c;

// ---- V7. Hierarchy membership (every unit in exactly one hierarchy) ----
MATCH (u:Unit)
WITH u, size([(u)-[:BELONGS_TO_HIERARCHY]->() | 1]) AS c
WHERE c <> 1
RETURN u.unit_name, c;

// ---- V8. Place-origin consistency (annex; only if described places loaded) ----
MATCH (p:Place)
WHERE (p.place_origin = 'described' AND NOT (p)-[:HAS_PROVENANCE]->())
   OR (p.place_origin = 'sourced' AND p.source_id IS NULL)
RETURN p.place_name, p.place_origin;

// ---- Count checks (should match the validated figures) ----
// MATCH (n) RETURN labels(n)[0] AS label, count(n) ORDER BY label;
// MATCH ()-[r]->() RETURN type(r) AS rel, count(r) ORDER BY rel;
