Drop in Oxrdflib into rdflib graph construction in validate-data

https://raw.githubusercontent.com/oxigraph/oxrdflib/refs/heads/main/README.md

---
  Critical Issue: make_data_graph.py pattern is incompatible with naïve swap

  The current pattern in make_data_graph.py creates one new Graph() per resource and per value, then merges them with +=:

  def make_data_graph(data: RdfLikeData) -> Graph:
      g = Graph()
      for r in data.resources:
          g += _make_one_resource(r)  # creates a new Graph() per resource

  def _make_one_resource(...) -> Graph:
      g = _make_property_objects_graph(...)  # creates a new Graph()
      for v in res.values:
          g += _make_one_value(v, res_iri)  # creates a new Graph() per value

  With 250,000 resources and multiple values each, this creates hundreds of thousands of Graph() objects. If we naïvely swap to
  Graph(store="Oxigraph"), each instantiation creates an Oxigraph store backed by a temp file on macOS. That would be worse than
  what you have now, not better.

  The fix is to refactor make_data_graph.py to build one single graph by adding triples directly to it, eliminating all the
  per-resource sub-graphs. The logic stays exactly the same — only the structural pattern changes (functions receive the graph as
  a parameter and add to it, instead of returning small graphs to be merged).

  ---
  Full Implementation Plan

  Task 1 — Add oxrdflib dependency

  uv add oxrdflib. pyoxigraph is already present so no conflict. After adding, verify uv.lock to confirm the resolved pyoxigraph
  version is not silently downgraded (oxrdflib pins a specific pyoxigraph version).

  ---
  Task 2 — Write three compatibility guard tests

  Test A: SPARQL CONSTRUCT .graph return type

  Location: test/unittests/commands/validate_data/sparql/test_oxigraph_compat.py (new file).

  def test_sparql_construct_graph_with_oxigraph_store():
      g = Graph(store="Oxigraph")
      g.add((URIRef("http://a"), RDF.type, URIRef("http://B")))
      result = g.query("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }")
      assert result.graph is not None
      assert (URIRef("http://a"), RDF.type, URIRef("http://B")) in result.graph

  This verifies that .graph on a CONSTRUCT result is an iterable rdflib-compatible Graph when the source uses the Oxigraph store.

  Test B: rdflib.collection.Collection with Oxigraph-backed graph

  def test_collection_with_oxigraph_store():
      g = Graph(store="Oxigraph")
      bn = BNode()
      items = [Literal("a", datatype=XSD.string), Literal("b", datatype=XSD.string)]
      Collection(g, bn, items)
      assert len(list(g)) == 4  # 2× (rdf:first + rdf:rest), last rdf:rest points to rdf:nil constant

  Test C: Graph(store="Oxigraph") += CONSTRUCT result containing blank nodes

  Covers the pattern in cardinality_shacl.py where CONSTRUCT queries produce inline blank nodes
  (e.g. sh:property [ a sh:PropertyShape ; ... ]) and the result is merged with +=.

  def test_construct_with_blank_nodes_merged_into_oxigraph_store():
      g = Graph(store="Oxigraph")
      g.add((URIRef("http://ex/A"), RDF.type, URIRef("http://ex/Class")))
      result = g.query("""
          CONSTRUCT { ?s <http://ex/prop> [ <http://ex/val> ?t ] }
          WHERE { ?s a ?t }
      """)
      assert result.graph is not None
      target = Graph(store="Oxigraph")
      target += result.graph
      assert len(list(target)) == 2  # (A, prop, _:bn) and (_:bn, val, Class)

  ---
  Task 3 — Refactor make_data_graph.py to single-graph pattern

  This is the only file that needs structural (not mechanical) change. The logic is identical — eliminate per-resource Graph
  creation by passing the graph down instead of returning small graphs.

  Rename: _make_property_objects_graph → _add_property_objects (to match the new add-not-return pattern).

  Note: if there are unit tests that directly test internal helper functions (_make_one_resource, _make_one_value,
  _make_property_objects_graph), those tests will need updating to match the new signatures. The public interface
  make_data_graph(data) -> Graph is unchanged, so tests of the public function need no changes.

  Before (make_data_graph.py:23-66):
  def make_data_graph(data: RdfLikeData) -> Graph:
      g = Graph()
      for r in data.resources:
          g += _make_one_resource(r)
      return g

  def _make_one_resource(res: RdfLikeResource) -> Graph:
      res_iri = DATA[res.res_id]
      g = _make_property_objects_graph(res.property_objects, res_iri)
      for v in res.values:
          g += _make_one_value(v, res_iri)
      return g

  def _make_one_value(val: RdfLikeValue, res_iri: URIRef) -> Graph:
      ...
      g = _make_property_objects_graph(val.value_metadata, val_iri)
      g.add(...)
      return g

  def _make_property_objects_graph(...) -> Graph:
      g = Graph()
      for trpl in property_objects:
          g.add(...)
      return g

  After:
  def make_data_graph(data: RdfLikeData) -> Graph:
      g = Graph(store="Oxigraph")
      for r in data.resources:
          _add_one_resource(g, r)
      return g

  def _add_one_resource(g: Graph, res: RdfLikeResource) -> None:
      res_iri = DATA[res.res_id]
      _add_property_objects(g, res.property_objects, res_iri)
      for v in res.values:
          _add_one_value(g, v, res_iri)

  def _add_one_value(g: Graph, val: RdfLikeValue, res_iri: URIRef) -> None:
      ...
      _add_property_objects(g, val.value_metadata, val_iri)
      g.add(...)

  def _add_property_objects(g: Graph, property_objects: list[PropertyObject], subject_iri: URIRef) -> None:
      for trpl in property_objects:
          g.add(...)

  ---
  Task 4 — Mechanical swap: Graph() → Graph(store="Oxigraph") in all remaining files

  All occurrences in the validate-data module except make_data_graph.py (already handled in Task 3). Files and locations:

  ┌──────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────┐
  │                         File                         │                           Graph() occurrences                                    │
  ├──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ validation/get_validation_report.py:47               │ results_graph = Graph()                                                          │
  ├──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ prepare_data/prepare_data.py:147,151,155,199,200,217 │ knora_api, api_shapes, api_card_shapes, og (per-onto), onto_g, resources_in_db   │
  ├──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ sparql/cardinality_shacl.py:25,66,70,112,148,185,218 │ all g = Graph() and return Graph()                                               │
  ├──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ sparql/value_shacl.py:30,72,112,148,221,257,265,285  │ all g = Graph() and return Graph()                                               │
  ├──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ sparql/construct_shacl.py:42,70,74                   │ g = Graph() (lines 42, 74) and return Graph() (line 70)                          │
  ├──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ sparql/legal_info_shacl.py:34                        │ g = Graph()                                                                      │
  ├──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ shacl_cli_validator.py:62                            │ graph = Graph() (full path: commands/validate_data/shacl_cli_validator.py)        │
  └──────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────┘

  Note: validation/validate_ontology.py and models/api_responses.py use Graph only as type annotations — no Graph() constructors
  to swap.

  ---
  Task 5 — Change serialize() calls to format="ox-ttl"

  ox-ttl is registered by oxrdflib as a plugin serializer and works on any rdflib graph backend,
  not only Oxigraph-backed ones. However, the full performance gain (Python bypass, Rust-native
  serialization) only fires when the graph is also backed by the Oxigraph store. Task 5 without
  Task 4 is a partial improvement; Task 4 + Task 5 together is the full optimization.

  Caveat: Oxigraph serializers are not 1:1 compatible with rdflib serializers — minor formatting
  differences exist. The output goes to the Docker SHACL CLI, which is format-agnostic for valid
  Turtle, so this is acceptable. parse(format="ttl") calls are left unchanged (see below).

  This directly addresses the hours-long bottleneck.

  ┌─────────────────────────────────────┬───────────────┬────────────────────────────────────────────────────────────────────────────────────────┐
  │                File                 │     Lines     │                                       Change                                           │
  ├─────────────────────────────────────┼───────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ validation/get_validation_report.py │ 80–85         │ serialize(format="ttl") → serialize(format="ox-ttl") (5 calls — the main bottleneck)   │
  ├─────────────────────────────────────┼───────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ validate_data.py                    │ 354, 356, 358 │ serialize(save_path) → serialize(save_path, format="ox-ttl")                           │
  ├─────────────────────────────────────┼───────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ validation/validate_ontology.py     │ 69            │ serialize(tmp_path / ...) → add format="ox-ttl"                                        │
  └─────────────────────────────────────┴───────────────┴────────────────────────────────────────────────────────────────────────────────────────┘

  Parse calls (parse(format="ttl")) are left unchanged — they parse small ontology files, not 50M-triple data, so there is no
  performance issue and the risk of the ox- parser differences is not worth taking.

  ---
  Task 6 — Run lint and test suite

  just lint
  just mypy
  just unittests
  just integration-tests

  Confirm the three new tests from Task 2 pass, and no regressions in existing tests.

  ---
  What is NOT changing

- All from rdflib import ... type imports — unchanged
- pyoxigraph.Store direct usage in TripleStores, cardinality_shacl.py, prepare_data.py — unchanged, these are already Rust
- parse(format="ttl") calls — unchanged
- from rdflib.xsd_datetime import parse_xsd_date — unaffected, store-independent
- Everything outside the validate_data module

  ---
