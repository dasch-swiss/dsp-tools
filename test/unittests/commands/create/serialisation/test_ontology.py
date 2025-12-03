# mypy: disable-error-code="no-untyped-def"
import pytest
from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import KnoraObjectType
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.serialisation.ontology import _make_one_cardinality_graph
from dsp_tools.commands.create.serialisation.ontology import _make_one_class_graph
from dsp_tools.commands.create.serialisation.ontology import _make_one_property_graph
from dsp_tools.commands.create.serialisation.ontology import _make_ontology_base_graph
from dsp_tools.commands.create.serialisation.ontology import serialise_cardinality_graph_for_request
from dsp_tools.commands.create.serialisation.ontology import serialise_class_graph_for_request
from dsp_tools.commands.create.serialisation.ontology import serialise_ontology_graph_for_request
from dsp_tools.commands.create.serialisation.ontology import serialise_property_graph_for_request
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import SALSAH_GUI
from test.unittests.commands.create.constants import LAST_MODIFICATION_DATE
from test.unittests.commands.create.constants import ONTO
from test.unittests.commands.create.constants import ONTO_IRI
from test.unittests.commands.create.constants import ONTO_IRI_STR
from test.unittests.commands.create.constants import PROJECT_IRI

RESOURCE_IRI = ONTO.Resource
ONTO_HAS_TEXT = ONTO.hasText
ONTO_HAS_TEXT_2 = ONTO.hasText2
KNORA_HAS_VALUE = KNORA_API.hasValue
KNORA_RESOURCE = KNORA_API.Resource
LIST_IRI = Literal("hlist=<http://rdfh.ch/lists/9999/n1>")


@pytest.fixture
def class_with_comment():
    return ParsedClass(
        name=str(RESOURCE_IRI),
        labels={"en": "Label EN", "de": "Label DE"},
        comments={"en": "Comment EN", "de": "Kommentar DE"},
        supers=[KNORA_RESOURCE],
        onto_iri=str(ONTO_IRI),
    )


@pytest.fixture
def class_with_multiple_supers():
    return ParsedClass(
        name=str(RESOURCE_IRI),
        labels={"en": "Label"},
        comments=None,
        supers=[KNORA_RESOURCE, f"{ONTO}OtherRes"],
        onto_iri=str(ONTO_IRI),
    )


def test_creates_graph_with_correct_structure() -> None:
    result = _make_ontology_base_graph(ONTO_IRI, LAST_MODIFICATION_DATE)
    assert len(result) == 2


class TestSerialiseCardinality:
    def test_creates_correct_graph_structure_with_cardinality_1(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(ONTO_HAS_TEXT),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        result_graph = _make_one_cardinality_graph(property_card, RESOURCE_IRI)
        assert len(result_graph) == 5
        blank_nodes = list(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))
        assert len(blank_nodes) == 1
        bn = blank_nodes[0]
        assert (bn, RDF.type, OWL.Restriction) in result_graph
        assert (bn, OWL.cardinality, Literal(1)) in result_graph
        assert (bn, OWL.onProperty, ONTO_HAS_TEXT) in result_graph

    def test_creates_correct_graph_with_max_cardinality(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(ONTO_HAS_TEXT),
            cardinality=Cardinality.C_0_1,
            gui_order=None,
        )
        result_graph = _make_one_cardinality_graph(property_card, RESOURCE_IRI)
        bn = next(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))
        assert (bn, OWL.maxCardinality, Literal(1)) in result_graph

    def test_creates_correct_graph_with_min_cardinality(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(ONTO_HAS_TEXT),
            cardinality=Cardinality.C_0_N,
            gui_order=None,
        )
        result_graph = _make_one_cardinality_graph(property_card, RESOURCE_IRI)
        bn = next(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))
        assert (bn, OWL.minCardinality, Literal(0)) in result_graph

    def test_serialise_card(self):
        property_card = ParsedPropertyCardinality(
            propname=str(ONTO_HAS_TEXT),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        serialised = serialise_cardinality_graph_for_request(
            property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE
        )

        # Check ontology-level properties
        assert serialised["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2"
        assert serialised["@type"] == ["http://www.w3.org/2002/07/owl#Ontology"]
        assert serialised["http://api.knora.org/ontology/knora-api/v2#lastModificationDate"] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#dateTimeStamp", "@value": "2025-10-14T13:00:00.000000Z"}
        ]

        # Check graph contains exactly 2 nodes
        assert len(serialised["@graph"]) == 2

        # Find the resource and restriction nodes
        resource_node = next(
            n for n in serialised["@graph"] if n["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2#Resource"
        )
        restriction_nodes = [n for n in serialised["@graph"] if n["@id"].startswith("_:")]

        # Verify resource node structure
        assert resource_node["@type"] == ["http://www.w3.org/2002/07/owl#Class"]
        assert len(resource_node["http://www.w3.org/2000/01/rdf-schema#subClassOf"]) == 1
        blank_node_id = resource_node["http://www.w3.org/2000/01/rdf-schema#subClassOf"][0]["@id"]
        assert blank_node_id.startswith("_:")

        # Verify restriction node structure
        assert len(restriction_nodes) == 1
        restriction_node = restriction_nodes[0]
        assert restriction_node["@id"] == blank_node_id
        assert restriction_node["@type"] == ["http://www.w3.org/2002/07/owl#Restriction"]
        assert restriction_node["http://www.w3.org/2002/07/owl#cardinality"] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#integer", "@value": 1}
        ]
        assert restriction_node["http://www.w3.org/2002/07/owl#onProperty"] == [
            {"@id": "http://0.0.0.0:3333/ontology/9999/onto/v2#hasText"}
        ]


class TestSerialiseProperty:
    def test_creates_correct_graph_with_minimal_property(self) -> None:
        prop = ParsedProperty(
            name=str(ONTO_HAS_TEXT),
            labels={"en": "has text"},
            comments=None,
            supers=[KNORA_HAS_VALUE],
            object=KnoraObjectType.TEXT,
            subject=None,
            gui_element=GuiElement.SIMPLETEXT,
            node_name=None,
            onto_iri=ONTO_IRI_STR,
        )
        result_graph = _make_one_property_graph(prop, None)
        assert (ONTO_HAS_TEXT, RDFS.subPropertyOf, URIRef(KNORA_HAS_VALUE)) in result_graph
        assert (ONTO_HAS_TEXT, RDF.type, OWL.ObjectProperty) in result_graph
        assert (ONTO_HAS_TEXT, KNORA_API.objectType, URIRef(str(KnoraObjectType.TEXT))) in result_graph
        assert (ONTO_HAS_TEXT, SALSAH_GUI.guiElement, URIRef(str(GuiElement.SIMPLETEXT))) in result_graph
        assert (ONTO_HAS_TEXT, RDFS.label, Literal("has text", lang="en")) in result_graph
        assert len(list(result_graph.objects(ONTO_HAS_TEXT, KNORA_API.subjectType))) == 0
        assert len(list(result_graph.objects(ONTO_HAS_TEXT, RDFS.comment))) == 0

    def test_creates_correct_graph_with_multiple_labels_and_comments(self) -> None:
        prop = ParsedProperty(
            name=str(ONTO_HAS_TEXT),
            labels={"en": "has text", "de": "hat Text", "fr": "a du texte"},
            comments={"en": "A text property", "de": "Eine Texteigenschaft", "fr": "Une propriété de texte"},
            supers=[KNORA_HAS_VALUE],
            object=KnoraObjectType.TEXT,
            subject=None,
            gui_element=GuiElement.SIMPLETEXT,
            node_name=None,
            onto_iri=ONTO_IRI_STR,
        )
        result_graph = _make_one_property_graph(prop, None)
        assert (ONTO_HAS_TEXT, RDFS.subPropertyOf, URIRef(KNORA_HAS_VALUE)) in result_graph
        assert (ONTO_HAS_TEXT, RDFS.label, Literal("has text", lang="en")) in result_graph
        assert (ONTO_HAS_TEXT, RDFS.label, Literal("hat Text", lang="de")) in result_graph
        assert (ONTO_HAS_TEXT, RDFS.label, Literal("a du texte", lang="fr")) in result_graph
        assert (ONTO_HAS_TEXT, RDFS.comment, Literal("A text property", lang="en")) in result_graph
        assert (ONTO_HAS_TEXT, RDFS.comment, Literal("Eine Texteigenschaft", lang="de")) in result_graph
        assert (ONTO_HAS_TEXT, RDFS.comment, Literal("Une propriété de texte", lang="fr")) in result_graph

    def test_creates_correct_graph_with_multiple_super_properties(self) -> None:
        prop = ParsedProperty(
            name=str(ONTO_HAS_TEXT),
            labels={"en": "has text"},
            comments=None,
            supers=[KNORA_HAS_VALUE, ONTO_HAS_TEXT_2],
            object=KnoraObjectType.TEXT,
            subject=None,
            gui_element=GuiElement.SIMPLETEXT,
            node_name=None,
            onto_iri=ONTO_IRI_STR,
        )
        result_graph = _make_one_property_graph(prop, None)
        assert (ONTO_HAS_TEXT, RDFS.subPropertyOf, URIRef(KNORA_HAS_VALUE)) in result_graph
        assert (ONTO_HAS_TEXT, RDFS.subPropertyOf, URIRef(ONTO_HAS_TEXT_2)) in result_graph

    def test_creates_correct_graph_with_subject_type(self) -> None:
        prop = ParsedProperty(
            name=str(ONTO_HAS_TEXT),
            labels={"en": "has text"},
            comments=None,
            supers=[KNORA_HAS_VALUE],
            object=KnoraObjectType.TEXT,
            subject=str(RESOURCE_IRI),
            gui_element=GuiElement.SIMPLETEXT,
            node_name=None,
            onto_iri=ONTO_IRI_STR,
        )
        result_graph = _make_one_property_graph(prop, None)
        assert (ONTO_HAS_TEXT, KNORA_API.subjectType, URIRef(str(RESOURCE_IRI))) in result_graph

    def test_creates_correct_graph_with_list_iri(self) -> None:
        prop = ParsedProperty(
            name=str(ONTO_HAS_TEXT),
            labels={"en": "has list"},
            comments=None,
            supers=[],
            object=KnoraObjectType.LIST,
            subject=None,
            gui_element=GuiElement.LIST,
            node_name="node_name",
            onto_iri=ONTO_IRI_STR,
        )
        result_graph = _make_one_property_graph(prop, LIST_IRI)
        gui_attrs = list(result_graph.objects(ONTO_HAS_TEXT, SALSAH_GUI.guiAttribute))
        assert len(gui_attrs) == 1
        assert gui_attrs[0] == LIST_IRI

    def test_serialise_property(self) -> None:
        prop = ParsedProperty(
            name=str(ONTO_HAS_TEXT),
            labels={"en": "has text", "de": "hat Text"},
            comments={"en": "A text property"},
            supers=[str(ONTO.hasValue)],
            object=KnoraObjectType.TEXT,
            subject=str(RESOURCE_IRI),
            gui_element=GuiElement.TEXTAREA,
            node_name=None,
            onto_iri=ONTO_IRI_STR,
        )
        serialised = serialise_property_graph_for_request(prop, None, ONTO_IRI, LAST_MODIFICATION_DATE)

        # Check ontology-level properties
        assert serialised["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2"
        assert serialised["@type"] == ["http://www.w3.org/2002/07/owl#Ontology"]
        assert serialised["http://api.knora.org/ontology/knora-api/v2#lastModificationDate"] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#dateTimeStamp", "@value": "2025-10-14T13:00:00.000000Z"}
        ]

        # Check graph contains exactly 1 node (the property)
        assert len(serialised["@graph"]) == 1

        # Find the property node
        prop_node = serialised["@graph"][0]

        # Verify property node structure
        assert prop_node["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2#hasText"
        assert prop_node["@type"] == ["http://www.w3.org/2002/07/owl#ObjectProperty"]

        # Check objectType
        assert prop_node["http://api.knora.org/ontology/knora-api/v2#objectType"] == [
            {"@id": "http://api.knora.org/ontology/knora-api/v2#TextValue"}
        ]

        # Check guiElement
        assert prop_node["http://api.knora.org/ontology/salsah-gui/v2#guiElement"] == [
            {"@id": "http://api.knora.org/ontology/salsah-gui/v2#Textarea"}
        ]

        # Check labels
        labels = prop_node["http://www.w3.org/2000/01/rdf-schema#label"]
        assert len(labels) == 2
        label_values = {(lbl["@language"], lbl["@value"]) for lbl in labels}
        assert ("en", "has text") in label_values
        assert ("de", "hat Text") in label_values

        # Check comments
        comments = prop_node["http://www.w3.org/2000/01/rdf-schema#comment"]
        assert len(comments) == 1
        assert comments[0]["@language"] == "en"
        assert comments[0]["@value"] == "A text property"

        # Check subPropertyOf
        super_props = prop_node["http://www.w3.org/2000/01/rdf-schema#subPropertyOf"]
        assert len(super_props) == 1
        assert super_props[0]["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2#hasValue"

        # Check subjectType
        subject_types = prop_node["http://api.knora.org/ontology/knora-api/v2#subjectType"]
        assert len(subject_types) == 1
        assert subject_types[0]["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2#Resource"


class TestSerialiseClass:
    def test_serialise_with_multiple_supers(self, class_with_multiple_supers):
        result = serialise_class_graph_for_request(class_with_multiple_supers, ONTO_IRI, LAST_MODIFICATION_DATE)
        # Check ontology-level properties
        assert result["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2"
        assert result["@type"] == ["http://www.w3.org/2002/07/owl#Ontology"]
        assert result["http://api.knora.org/ontology/knora-api/v2#lastModificationDate"] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#dateTimeStamp", "@value": "2025-10-14T13:00:00.000000Z"}
        ]
        # Check graph contains exactly 1 node (the class)
        assert len(result["@graph"]) == 1
        # Find the class node
        class_node = result["@graph"][0]
        # Verify class node structure
        assert class_node["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2#Resource"
        assert class_node["@type"] == ["http://www.w3.org/2002/07/owl#Class"]
        # Check labels
        labels = class_node["http://www.w3.org/2000/01/rdf-schema#label"]
        assert len(labels) == 1
        assert labels[0]["@language"] == "en"
        assert labels[0]["@value"] == "Label"
        # Check multiple super classes
        super_classes = class_node["http://www.w3.org/2000/01/rdf-schema#subClassOf"]
        assert len(super_classes) == 2
        super_ids = {sc["@id"] for sc in super_classes}
        assert "http://api.knora.org/ontology/knora-api/v2#Resource" in super_ids
        assert "http://0.0.0.0:3333/ontology/9999/onto/v2#OtherRes" in super_ids
        # Check no comments
        assert "http://www.w3.org/2000/01/rdf-schema#comment" not in class_node

    def test_serialise_with_comment(self, class_with_comment):
        result = serialise_class_graph_for_request(class_with_comment, ONTO_IRI, LAST_MODIFICATION_DATE)
        # Check ontology-level properties
        assert result["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2"
        assert result["@type"] == ["http://www.w3.org/2002/07/owl#Ontology"]
        assert result["http://api.knora.org/ontology/knora-api/v2#lastModificationDate"] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#dateTimeStamp", "@value": "2025-10-14T13:00:00.000000Z"}
        ]
        # Check graph contains exactly 1 node (the class)
        assert len(result["@graph"]) == 1
        # Find the class node
        class_node = result["@graph"][0]
        # Verify class node structure
        assert class_node["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2#Resource"
        assert class_node["@type"] == ["http://www.w3.org/2002/07/owl#Class"]
        # Check labels
        labels = class_node["http://www.w3.org/2000/01/rdf-schema#label"]
        assert len(labels) == 2
        de_lbl = [x for x in labels if x["@language"] == "de"]
        assert de_lbl[0]["@value"] == "Label DE"
        de_lbl = [x for x in labels if x["@language"] == "en"]
        assert de_lbl[0]["@value"] == "Label EN"
        # Check comments
        comments = class_node["http://www.w3.org/2000/01/rdf-schema#comment"]
        assert len(comments) == 2
        de_cmnt = [x for x in comments if x["@language"] == "de"]
        assert de_cmnt[0]["@value"] == "Kommentar DE"
        en_cmnt = [x for x in comments if x["@language"] == "en"]
        assert en_cmnt[0]["@value"] == "Comment EN"
        # Check super classes
        super_classes = class_node["http://www.w3.org/2000/01/rdf-schema#subClassOf"]
        assert len(super_classes) == 1
        assert super_classes[0]["@id"] == "http://api.knora.org/ontology/knora-api/v2#Resource"

    def test_make_graph_with_multiple_supers(self, class_with_multiple_supers):
        result = _make_one_class_graph(class_with_multiple_supers)
        assert len(result) == 4
        assert (RESOURCE_IRI, RDF.type, OWL.Class) in result
        assert (RESOURCE_IRI, RDFS.label, Literal("Label", lang="en")) in result
        assert (RESOURCE_IRI, RDFS.subClassOf, URIRef(KNORA_RESOURCE)) in result
        assert (RESOURCE_IRI, RDFS.subClassOf, URIRef(f"{ONTO}OtherRes")) in result
        assert len(list(result.objects(RESOURCE_IRI, RDFS.comment))) == 0

    def test_make_graph_with_comment(self, class_with_comment):
        result = _make_one_class_graph(class_with_comment)
        assert len(result) == 6
        assert (RESOURCE_IRI, RDF.type, OWL.Class) in result
        assert (RESOURCE_IRI, RDFS.label, Literal("Label EN", lang="en")) in result
        assert (RESOURCE_IRI, RDFS.label, Literal("Label DE", lang="de")) in result
        assert (RESOURCE_IRI, RDFS.comment, Literal("Comment EN", lang="en")) in result
        assert (RESOURCE_IRI, RDFS.comment, Literal("Kommentar DE", lang="de")) in result
        assert (RESOURCE_IRI, RDFS.subClassOf, URIRef(KNORA_RESOURCE)) in result


class TestSerialiseOntology:
    def test_serialise_graph_without_comment(self):
        onto = ParsedOntology("onto", "lbl", None, [], [], [])
        serialised = serialise_ontology_graph_for_request(onto, PROJECT_IRI)
        expected = {
            "http://api.knora.org/ontology/knora-api/v2#attachedToProject": {
                "@id": "http://rdfh.ch/projects/projectIRI"
            },
            "http://api.knora.org/ontology/knora-api/v2#ontologyName": "onto",
            "http://www.w3.org/2000/01/rdf-schema#label": "lbl",
        }
        assert serialised == expected

    def test_serialise_graph_with_comment(self):
        onto = ParsedOntology("onto", "lbl", "comment", [], [], [])
        serialised = serialise_ontology_graph_for_request(onto, PROJECT_IRI)
        expected = {
            "http://api.knora.org/ontology/knora-api/v2#attachedToProject": {
                "@id": "http://rdfh.ch/projects/projectIRI"
            },
            "http://api.knora.org/ontology/knora-api/v2#ontologyName": "onto",
            "http://www.w3.org/2000/01/rdf-schema#comment": "comment",
            "http://www.w3.org/2000/01/rdf-schema#label": "lbl",
        }
        assert serialised == expected
