# Attribution

## Ordnance Survey OpenData

Parts of this repository name places and administrative units that come from a knowledge graph built
from Ordnance Survey OpenData products — **OS OpenMap Local** (the NamedPlace layer, the source of every
place), **OS Boundary-Line** (the administrative and electoral units) and **OS Code-Point Open** (the postal
geography, which carries Royal Mail and Office for National Statistics data). Those products are released
under the Open Government Licence v3.0
(https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/; Ordnance Survey's terms at
https://www.ordnancesurvey.co.uk/products/os-opendata), which requires the following statement wherever the
data appears:

> Contains OS data © Crown copyright and database right 2026.
> Contains Royal Mail data © Royal Mail copyright and database right 2026.
> Contains National Statistics data © Crown copyright and database right 2026.

### Files that carry Ordnance Survey-derived content

| file | what it carries |
|---|---|
| `grounding-study/probe_set_4sector.csv` | 90 probe items: place and unit names, their keys in the graph, and the directional relations between them |
| `grounding-study/partB_results.csv` | the same items with the model's responses |
| `grounding-study/partB_raw_responses.jsonl` | raw responses, which quote the place and unit names |
| `grounding-study/partB_stability_raw.jsonl` | raw responses of the stability run, likewise |

No other file in this repository carries Ordnance Survey data. The ontology, the shapes, the profile, the
composition tables, the validation suite and the scripts are the authors' own work and are licensed
CC BY 4.0 (`LICENSE`). The two licences attach to different files; no file is under both.

### The populated graph

The populated Wales graph itself (the RDF and the property-graph CSVs) is not published in this repository.
When it is published it will carry the statement above and the Open Government Licence, since it is
derived from the products named. As of 22 September 2026 the deployment contains Ordnance Survey-derived
data only.

## Added 22 September 2026

This file was added on 22 September 2026, after the grounding-study files had been published without the
statement. The omission is corrected here; nothing in the files changed.
