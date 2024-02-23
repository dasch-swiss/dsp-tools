import pytest
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.models.ontology_lookup_models import (
    _check_correct_val_type,
    _extract_classes_and_properties_from_onto,
    _get_all_classes_from_onto,
    _get_all_properties_from_onto,
    _get_all_text_value_properties_and_types_from_onto,
    _make_text_value_property_type_lookup,
    _remove_default_prefix,
    _remove_prefixes,
)


class TestGetAllClassesFromJson:
    @staticmethod
    def test_single_class() -> None:
        test_json = [
            {
                "knora-api:isResourceClass": True,
                "rdfs:label": "Sequenz einer Audio-Ressource",
                "knora-api:canBeInstantiated": True,
                "rdfs:subClassOf": [],
                "@type": "owl:Class",
                "@id": "testonto:AudioSequence",
            },
        ]
        res_cls = _get_all_classes_from_onto(test_json)
        assert res_cls == ["testonto:AudioSequence"]

    @staticmethod
    def test_property() -> None:
        test_json = [
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
        res_cls = _get_all_classes_from_onto(test_json)
        assert not res_cls

    @staticmethod
    def test_from_json_resources_and_properties() -> None:
        test_json = [
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
        res_cls = _get_all_classes_from_onto(test_json)
        assert res_cls == ["testonto:AudioSequence"]


def test_get_all_properties_from_json_haslinkto() -> None:
    test_json = [
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
    res_prop = _get_all_properties_from_onto(test_json)
    assert res_prop == ["testonto:hasResource", "testonto:hasResourceValue"]


def test_get_all_properties_from_json_resources_and_properties() -> None:
    test_json = [
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
    res_prop = _get_all_properties_from_onto(test_json)
    assert res_prop == ["testonto:hasUri"]


def test_deserialize_ontology() -> None:
    test_json = [
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
    res_onto = _extract_classes_and_properties_from_onto(test_json)
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


def test_get_all_text_value_properties_and_types_from_json() -> None:
    test_json = [
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
            "rdfs:label": "Simple Text",
            "rdfs:subPropertyOf": {},
            "knora-api:isResourceProperty": True,
            "knora-api:objectType": {"@id": "knora-api:TextValue"},
            "salsah-gui:guiElement": {"@id": "salsah-gui:SimpleText"},
            "@id": "onto:hasSimpleText",
        },
        {
            "rdfs:label": "Textarea",
            "rdfs:subPropertyOf": {},
            "knora-api:isResourceProperty": True,
            "knora-api:objectType": {"@id": "knora-api:TextValue"},
            "salsah-gui:guiElement": {"@id": "salsah-gui:Textarea"},
            "@id": "onto:hasTextarea",
        },
        {
            "rdfs:label": "Richtext",
            "rdfs:subPropertyOf": {},
            "knora-api:isResourceProperty": True,
            "knora-api:objectType": {"@id": "knora-api:TextValue"},
            "salsah-gui:guiElement": {"@id": "salsah-gui:Richtext"},
            "@id": "onto:hasRichtext",
        },
        {
            "rdfs:label": "Editor",
            "rdfs:subPropertyOf": {},
            "knora-api:isResourceProperty": True,
            "knora-api:isLinkProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {"@id": "onto:Person"},
            "salsah-gui:guiElement": {"@id": "salsah-gui:Searchbox"},
            "@id": "onto:hasEditor",
        },
    ]
    res = _get_all_text_value_properties_and_types_from_onto(test_json)
    assert res == [
        ("onto:hasSimpleText", "salsah-gui:SimpleText"),
        ("onto:hasTextarea", "salsah-gui:Textarea"),
        ("onto:hasRichtext", "salsah-gui:Richtext"),
    ]


def test_check_correct_val_type_cls() -> None:
    test_dict = {
        "knora-api:isResourceClass": True,
        "rdfs:label": "Annotation",
        "knora-api:canBeInstantiated": True,
        "rdfs:subClassOf": [],
        "rdfs:comment": "A generic class for representing annotations",
        "@type": "owl:Class",
        "@id": "knora-api:Annotation",
    }
    res = _check_correct_val_type(test_dict)
    assert not res


def test_check_correct_val_type_link_prop() -> None:
    test_dict = {
        "rdfs:label": "Editor",
        "rdfs:subPropertyOf": {},
        "knora-api:isResourceProperty": True,
        "knora-api:isLinkProperty": True,
        "@type": "owl:ObjectProperty",
        "knora-api:objectType": {"@id": "onto:Person"},
        "salsah-gui:guiElement": {"@id": "salsah-gui:Searchbox"},
        "@id": "onto:hasEditor",
    }
    res = _check_correct_val_type(test_dict)
    assert not res


def test_check_correct_val_type_text_prop() -> None:
    test_dict = {
        "rdfs:label": "Textarea",
        "rdfs:subPropertyOf": {},
        "knora-api:isResourceProperty": True,
        "knora-api:objectType": {"@id": "knora-api:TextValue"},
        "salsah-gui:guiElement": {"@id": "salsah-gui:Textarea"},
        "@id": "onto:hasTextarea",
    }
    res = _check_correct_val_type(test_dict)
    assert res


def test_make_text_value_property_gui() -> None:
    test_li = [
        ("onto:hasSimpleText", "salsah-gui:SimpleText"),
        ("onto_other:hasTextarea", "salsah-gui:Textarea"),
        ("onto:hasRichtext", "salsah-gui:Richtext"),
        ("other_onto:hasRichtext", "salsah-gui:Richtext"),
        ("onto:ontoHasSimpleText", "salsah-gui:SimpleText"),
    ]
    res = _make_text_value_property_type_lookup(test_li, "onto")
    assert res.formatted_text_props == {":hasRichtext", "other_onto:hasRichtext", "hasComment"}
    assert res.unformatted_text_props == {":hasSimpleText", "onto_other:hasTextarea", ":ontoHasSimpleText"}


def test_remove_default_prefix_not_default() -> None:
    res = _remove_default_prefix("onto:property", "default")
    assert res == "onto:property"


def test_remove_default_prefix_default() -> None:
    res = _remove_default_prefix("default:property", "default")
    assert res == ":property"


if __name__ == "__main__":
    pytest.main([__file__])
