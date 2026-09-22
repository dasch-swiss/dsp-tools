---
status: accepted
date: 2026-09-22
---

# Represent parsed values as a generic RDF-triple dataclass before building the graph

Between parsing the input XML and building the final `rdflib` graph, `validate-data` holds data in a
generic dataclass structure (`PropertyObject`, `RdfLikeValue`) representing one part of an RDF triple,
independent of both the XML input format and the API's own data structure.

Source: [PR #1360](https://github.com/dasch-swiss/dsp-tools/pull/1360). The PR introduced this structure
under the names `PropertyObject` and `ValueInformation`; `ValueInformation` was later renamed to
`RdfLikeValue` (`src/dsp_tools/commands/validate_data/models/rdf_like_data.py`).

Enforced by: none (docs-only)
