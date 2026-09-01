# Provenance of the Qualitative Place Model: A Development Record

Alia I. Abdelmoty
School of Computer Science and Informatics, Cardiff University

Version 1.0, accompanying the QPM ontology release at https://w3id.org/qpm
Licensed CC BY 4.0

---

## 1. Purpose and status

This document is a record, not a research paper. The specification of the
Qualitative Place Model is the canonical ontology paper; this document says
where each element of that model came from, when it was first stated, and how
its formulation changed on the way to the version the ontology now fixes.

It exists for three reasons. The elements of the model were developed over a
long period and in several idioms, so a reader who meets one of the earlier
papers should be able to see how it relates to the model as it now stands. The
canonical paper cites only published work, so the earlier and unpublished part
of the development has no place there and would otherwise go unrecorded. And
the documented lineage in the published record starts later than the actual
development did: the two doctoral theses that build on the model both anchor it
to the Relative Location model of 2016, and neither cites the 1995 work whose
frame of reference, proximity zones, orientation treatment and containment
hierarchy they reuse. That discontinuity is closed here.

Nothing in this document is offered as a claim of priority. Section 7 states
what is and is not being claimed.

## 2. Sources

The record is drawn from the following. Sources are lettered for reference in
the lineage table.

| Ref | Year | Work | Status |
|-----|------|------|--------|
| S0 | 1995 | Abdelmoty, PhD thesis, Heriot-Watt University: qualitative spatial representation and reasoning, and a geographic data model | Unpublished thesis |
| S1 | 2003 | El-Geresy and Abdelmoty, SPARQS: automatic reasoning in qualitative space, AI-2003 | Published |
| S2 | 2005 | El-Geresy and Abdelmoty, Qualitative representation and reasoning with uncertainty in space and time, AI-2005 | Published |
| S3 | 2010 | Abdelmoty, El-Geresy and Smart, Reasoning with geospatial semantics on the linked data web, SeCoGIS 2010 | Published |
| S4 | 2014 | Smart, Abdelmoty and El-Geresy, Spatial reasoning with place information on the semantic web, Int. J. on AI Tools 23(5) | Published |
| S5 | 2016 | Abdelmoty and Al-Muzaini, Reasoning with place information on the linked data web (RelLoc), ALLDATA 2016 | Published |
| S5b | 2016 | Abdelmoty and Al-Muzaini, A computational model of place on the linked data web (SemRelLoc), Int. J. on Advances in Software 9(3&4) | Published |
| S6 | 2024 | Abdelmoty, Muhajab and Satoti, Spatial semantics for the evaluation of administrative geospatial ontologies, ISPRS IJGI | Published |
| S7 | 2024 | Abdelmoty and Satoti, A homogeneous approach to reasoning over global geographic data, AI-2024 | Published |
| S8 | 2025 | Satoti and Abdelmoty, A GIS-native framework for qualitative place models, ISPRS IJGI | Published |
| S9 | 2009 | Smart, PhD thesis, Cardiff University: a semantic web rule language for geospatial domains | Thesis |
| S10 | 2017 | Almuzaini, PhD thesis, Cardiff University: qualitative modelling of place location on the linked data web and GIS | Thesis |
| S11 | 2025 | Muhajab, PhD thesis, Cardiff University: unified management of place information on the web of data | Thesis |
| A1 | c. 2000 | El-Geresy, The ring structure: qualitative representations in large spatial databases, ICCI 2000 | Antecedent |

S1, S2 and A1 supply reasoning machinery rather than place-model structure and
appear here only where an element of the model traces to them.

Several of these works are co-authored with doctoral students, and the theses
S9, S10 and S11 are their own. The model itself is not theirs. Those works
apply it, under the author's direction, to different technologies, data and
questions, and where the record below dates an element to one of them, that
records where the element was first stated in writing and not who originated
it. Where a student contribution is an origination rather than an application,
it is named as such: the discrete local irregular grid pattern and its GeoUnit
abstraction in S7 and S11, and the grid-efficiency method of S8, are of that
kind.

## 3. Origins: the 1995 geographic data model

The structural machinery of the model originates in S0, roughly a decade before
the place idiom was adopted. That work is written in the vocabulary of
geographic features and data models rather than of places, and the
correspondence has to be read through the change of vocabulary, but the
elements are the same ones.

Four features of S0 bear directly on the model as it now stands. It used a
three-level architecture in which a layer of geographic abstract data types
stood between the feature level and the geometric representation, so that a
feature could carry several spatial representations without any of them
constituting its identity; this is the model's treatment of geometry as an
attribute. It treated areal and point phenomena, in its own terms enclosures
and sites, as parallel types onto which features mapped uniformly; this is the
model's homogeneity. It stated the store-one-parent principle directly, that
only the direct parents of objects need be stored and other containment
relationships can be inferred, crediting Worboys and Bofakos; this is the
minimal-storage commitment in its original and narrower form. And it defined a
three-axis qualitative frame of reference, over interaction-proximity,
orientation, and size, whose proximity axis was decomposed into zones rather
than measured metrically and whose orientation axis was explicitly
granularity-parametric, yielding four cardinal values at one resolution and
more at others.

Two further constructs of S0 anticipate parts of the model that the
intervening work did not always carry forward. Composite and multiply connected
objects were handled directly, including the distinction between connected and
disconnected composites and a fused-association construct for spatially fused
parts. And multiple representation, in which one area corresponds to more than
one classification, a city viewed as school districts or alternatively as
administrative districts, is the conceptual seed of the multi-hierarchy
structure; S0 identifies it but notes that its implementation platform did not
support it.

## 4. Element-by-element lineage

For each element of the canonical model: where it first appears, how its
formulation changed, and its status now.

| Element | First appearance | Status in the canonical model |
|---|---|---|
| Geometry as attribute, not identity | S0 (abstract data type layer) | Commitment 1 |
| Homogeneous treatment of areal and point entities | S0 (enclosures and sites) | Commitment 3, Unit and BasicPlace |
| One-step containment, ancestry derived | S0, after Worboys and Bofakos | Commitment 2, generalised to a minimal generating set |
| Containment as an explicit one-step relation with derived transitivity | S5 | Retained, with the subproperty architecture |
| Single-parent axiom in ontology form | S6, S7 | Retained as the partition precondition |
| Containment path as the encoding of location | S8 | Retained |
| Qualitative frame of reference, three axes | S0, reused in S3 | Decomposed into the relation taxonomy |
| Orientation axis, granularity-parametric | S0 | The four against eight sector question, adjudicated in the canonical paper |
| Adjacency-Orientation Matrix | A1, adopted into the place domain in S3 | Not carried forward; superseded by stored primaries |
| Nearest neighbour per directional sector | S5 | The stored directional primary |
| Directional split, multi-valued for units and functional for places | S8 | Retained as the two-layer architecture |
| Graded proximity by zone decomposition | S0 | Retained in spirit, derived rather than stored |
| Graded proximity named close, near, far | S3 | Retained; the close composed with close step survives |
| Proximity as adjacency-graph distance | S6 | Retained as the derivation mechanism |
| Parametric hop-bounded proximity | S8 | Retained |
| Composite objects with disconnected parts | S0 | The composite place |
| Composite place in the place idiom | S3 (split campus example) | Retained; restored after its absence from S5 and S8 |
| Multiple representation of one area | S0 | The multi-hierarchy structure |
| Multi-hierarchy in the place idiom | S3, one line; developed in S6, S7, S11 | Retained |
| Formal location across coexisting hierarchies | S8 | Retained |
| Location profile as a spatial fingerprint | S5 | Retained |
| Salient-place layer | S5b, definitive in S10 | Not carried forward; see section 6 |
| Spatial semantic completeness and competency questions | S6 | Reused as the evaluation instrument |
| GeoUnit and the DLIG pattern | S7, S11 | Terminology maps to Unit; the Cell class is unnecessary |

## 5. Divergences the canonical model resolves

Where the earlier works disagree with one another, the canonical model settles
the question. These are recorded because a reader coming from any one of those
works will find the canonical formulation different from the one they know.

**Graded proximity.** The formal status of the graded scale changed four times:
a zone decomposition with grades as fine as very far in S0; named cognitive
grades of close, near and far in S3; absent altogether in S5, where proximity
is only the nearest neighbour per sector; graph path length grades in S6, with
near as a two-edge path and far as more than two regions between; and a
parameter without labels in S8. The two doctoral applications of the model resolved it
incompatibly, S10 carrying no graded proximity at all and S11 using graph
distance, which is a divergence in how the model was applied rather than a
disagreement about the model. The canonical model derives a graded scale by traversal over the
stored adjacency graph and does not store it.

**Direction, one neighbour per sector or many.** S3 labels every adjacency edge
with an orientation; S5 records one nearest neighbour per sector; S8 splits the
two, multi-valued for units and functional for places. The canonical model
takes the split and gives the reason for keeping the layers distinct.

**The directional frame.** Four sectors are the stated default in S8, which
nonetheless instantiates eight. The canonical paper treats this as an open
question and settles it empirically rather than by preference.

**Naming.** The containment relation appears as a parent reference in S3, as
inside in prose and in in figures within S5, as inside and contains in S6 and
S7, and in two typed forms under one name in S8. The entity vocabulary is Place
and Populated-Place in S3, Region, GeoUnit and Place in S6 and S7, and Unit and
BasicPlace in S8. The canonical model fixes one vocabulary and the ontology
records the mapping.

**Per-hierarchy uniqueness.** The OWL axiom intended to express uniqueness of
containment per hierarchy in S8 does not in fact express it. The constraint is
expressible in SHACL, and the ontology release carries it there.

## 6. Elements not carried into the canonical model

Three elements of the earlier record are deliberately absent, and are noted so
that their absence is not mistaken for oversight.

The salient-place layer of S5b and S10, in which relations are defined only
with reference to an extracted layer of salient places rather than among all
places, is not part of the canonical model. It is a selection policy over the
population rather than a feature of the relational structure, and the canonical
model treats all basic places uniformly. It remains available as a refinement.

The typed uncertainty framework of S2, distinguishing positional, extension,
configuration and orientation uncertainty, was never integrated with the place
model and is not integrated here.

The RCC8 and RCC12 treatment of S4 is not carried forward. The canonical model
returns to the bespoke relations of the rest of the line, for the reasons the
canonical paper gives about what is stored.

The place layer comprises 52,821 records from a single OS-derived source. Of these, 44,285 carry a name and a category from the CLASSIFICA attribute join; the remaining 8,536 are unmatched by that join and are retained with place_type_unknown set, without a name or category. Multi-segment linear and areal features appear as one record per segment, sharing the parent feature's centroid; 3,977 such groups account for 6,311 records beyond the first in each group.

## 7. What is not claimed

The commitments underlying the model have close counterparts in the philosophy
of geography, principally in the work of Smith, Mark, Bittner, Casati and
Varzi. The canonical paper sets out those correspondences and treats them as
warrant.

This document does not claim priority over that literature. The relationship
is one of convergence: the elements recorded here were arrived at
independently, for representational reasons, and the philosophical accounts
were developed independently of them. In the published record the
philosophical work came first, and the earlier development recorded here is
unpublished. The purpose of this document is to record what happened, not to
adjudicate precedence.

Nor does it claim that the earlier formulations were the canonical model in
another notation. Several of them differ from it, and section 5 says how.

## 8. Citation

Abdelmoty, A. I. Provenance of the Qualitative Place Model: A Development
Record. Documentation accompanying the QPM ontology release, version 1.0.
https://w3id.org/qpm
