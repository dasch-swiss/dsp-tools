from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.models.ontology_lookup_models import (
    _get_all_classes_from_graph,
    _get_all_properties_from_graph,
    _remove_prefixes,
    extract_classes_properties_from_onto,
)


class TestGetAllClassesFromGraph:
    @staticmethod
    def test_single_class() -> None:
        test_graph = [
            {
                "knora-api:isResourceClass": True,
                "rdfs:label": "Sequenz einer Audio-Ressource",
                "knora-api:canBeInstantiated": True,
                "rdfs:subClassOf": [],
                "@type": "owl:Class",
                "@id": "testonto:AudioSequence",
            },
        ]
        res_cls = _get_all_classes_from_graph(test_graph)
        assert res_cls == ["testonto:AudioSequence"]

    @staticmethod
    def test_property() -> None:
        test_graph = [
            {
                "rdfs:label": "URI",
                "rdfs:subPropertyOf": {},
                "knora-api:isEditable": True,
                "knora-api:isResourceProperty": True,
                "@type": "owl:ObjectProperty",
                "salsah-gui:guiAttribute": [],
                "knora-api:objectType": {},
                "salsah-gui:guiElement": {},
                "@id": "testonto:hasUri",
            },
        ]
        res_cls = _get_all_classes_from_graph(test_graph)
        assert not res_cls

    @staticmethod
    def test_from_graph_resources_and_properties() -> None:
        test_graph = [
            {
                "knora-api:isResourceClass": True,
                "rdfs:label": "Sequenz einer Audio-Ressource",
                "knora-api:canBeInstantiated": True,
                "rdfs:subClassOf": [],
                "@type": "owl:Class",
                "@id": "testonto:AudioSequence",
            },
            {
                "rdfs:label": "URI",
                "rdfs:subPropertyOf": {},
                "knora-api:isEditable": True,
                "knora-api:isResourceProperty": True,
                "@type": "owl:ObjectProperty",
                "salsah-gui:guiAttribute": [],
                "knora-api:objectType": {},
                "salsah-gui:guiElement": {},
                "@id": "testonto:hasUri",
            },
        ]
        res_cls = _get_all_classes_from_graph(test_graph)
        assert res_cls == ["testonto:AudioSequence"]


def test_get_all_properties_from_graph_haslinkto() -> None:
    test_graph = [
        {
            "rdfs:label": "hasResource",
            "rdfs:subPropertyOf": {},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "knora-api:isLinkProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {},
            "salsah-gui:guiElement": {},
            "@id": "testonto:hasResource",
        },
        {
            "knora-api:isLinkValueProperty": True,
            "rdfs:label": "hasResource",
            "rdfs:subPropertyOf": {},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {},
            "salsah-gui:guiElement": {},
            "@id": "testonto:hasResourceValue",
        },
    ]
    res_prop = _get_all_properties_from_graph(test_graph)
    assert res_prop == ["testonto:hasResource", "testonto:hasResourceValue"]


def test_get_all_properties_from_graph_resources_and_properties() -> None:
    test_graph = [
        {
            "knora-api:isResourceClass": True,
            "rdfs:label": "Sequenz einer Audio-Ressource",
            "knora-api:canBeInstantiated": True,
            "rdfs:subClassOf": [],
            "@type": "owl:Class",
            "@id": "testonto:AudioSequence",
        },
        {
            "rdfs:label": "URI",
            "rdfs:subPropertyOf": {},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "salsah-gui:guiAttribute": [],
            "knora-api:objectType": {},
            "salsah-gui:guiElement": {},
            "@id": "testonto:hasUri",
        },
    ]
    res_prop = _get_all_properties_from_graph(test_graph)
    assert res_prop == ["testonto:hasUri"]


def test_deserialize_ontology() -> None:
    test_graph = [
        {
            "knora-api:isResourceClass": True,
            "rdfs:label": "Annotation",
            "knora-api:canBeInstantiated": True,
            "rdfs:subClassOf": [],
            "rdfs:comment": "A generic class for representing annotations",
            "@type": "owl:Class",
            "@id": "knora-api:Annotation",
        },
        {
            "rdfs:label": "has Link to",
            "rdfs:subPropertyOf": {},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {},
            "@id": "knora-api:hasLinkTo",
            "knora-api:subjectType": {},
            "knora-api:isLinkProperty": True,
            "rdfs:comment": "Represents a direct connection between two resources",
        },
    ]
    res_onto = extract_classes_properties_from_onto(test_graph)
    assert res_onto.classes == ["Annotation"]
    assert res_onto.properties == ["hasLinkTo"]


def test_remove_prefixes_knora_classes() -> None:
    test_elements = ["knora-api:Annotation", "knora-api:ArchiveFileValue", "knora-api:ArchiveRepresentation"]
    res = _remove_prefixes(test_elements)
    assert unordered(res) == ["Annotation", "ArchiveFileValue", "ArchiveRepresentation"]


def test_remove_prefixes_knora_properties() -> None:
    test_elements = ["knora-api:attachedToUser", "knora-api:deletedBy"]
    res = _remove_prefixes(test_elements)
    assert unordered(res) == ["attachedToUser", "deletedBy"]
