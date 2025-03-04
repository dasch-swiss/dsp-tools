import pytest
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.models.lookup_models import _check_if_text_value_property
from dsp_tools.commands.xmlupload.models.lookup_models import _extract_classes_and_properties_from_onto
from dsp_tools.commands.xmlupload.models.lookup_models import _get_all_classes_from_onto
from dsp_tools.commands.xmlupload.models.lookup_models import _get_all_properties_from_onto
from dsp_tools.commands.xmlupload.models.lookup_models import _get_all_text_value_types_properties_and_from_onto
from dsp_tools.commands.xmlupload.models.lookup_models import _make_text_value_property_type_lookup
from dsp_tools.commands.xmlupload.models.lookup_models import _remove_prefixes


class TestGetAllClassesFromJson:
    @staticmethod
    def test_single_class() -> None:
        test_json = [
            {
                "knora-api:isResourceClass": True,
                "rdfs:label": "Segment einer Audio-Ressource",
                "knora-api:canBeInstantiated": True,
                "rdfs:subClassOf": [],
                "@type": "owl:Class",
                "@id": "testonto:AudioSegment",
            },
        ]
        res_cls = _get_all_classes_from_onto(test_json)
        assert res_cls == ["testonto:AudioSegment"]

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
                "@id": "testonto:AudioSegment",
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
        assert res_cls == ["testonto:AudioSegment"]


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
            "@id": "testonto:AudioSegment",
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
            "rdfs:label": "Region",
            "knora-api:canBeInstantiated": True,
            "rdfs:subClassOf": [],
            "rdfs:comment": "",
            "@type": "owl:Class",
            "@id": "knora-api:Region",
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
    assert res_onto.classes == ["Region"]
    assert res_onto.properties == ["hasLinkTo"]


def test_remove_prefixes_knora_classes() -> None:
    test_elements = ["knora-api:Region", "knora-api:ArchiveFileValue", "knora-api:ArchiveRepresentation"]
    res = _remove_prefixes(test_elements)
    assert unordered(res) == ["Region", "ArchiveFileValue", "ArchiveRepresentation"]


def test_remove_prefixes_knora_properties() -> None:
    test_elements = ["knora-api:attachedToUser", "knora-api:deletedBy"]
    res = _remove_prefixes(test_elements)
    assert unordered(res) == ["attachedToUser", "deletedBy"]


def test_get_all_text_value_types_properties_and_from_onto() -> None:
    test_json = [
        {
            "knora-api:isResourceClass": True,
            "rdfs:label": "Region",
            "knora-api:canBeInstantiated": True,
            "rdfs:subClassOf": [],
            "rdfs:comment": "",
            "@type": "owl:Class",
            "@id": "knora-api:Region",
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
    res = _get_all_text_value_types_properties_and_from_onto(test_json)
    assert res == [
        ("onto:hasSimpleText", "salsah-gui:SimpleText"),
        ("onto:hasTextarea", "salsah-gui:Textarea"),
        ("onto:hasRichtext", "salsah-gui:Richtext"),
    ]


def test_check_if_text_value_property_cls() -> None:
    test_dict = {
        "knora-api:isResourceClass": True,
        "rdfs:label": "Region",
        "knora-api:canBeInstantiated": True,
        "rdfs:subClassOf": [],
        "rdfs:comment": "",
        "@type": "owl:Class",
        "@id": "knora-api:Region",
    }
    res = _check_if_text_value_property(test_dict)
    assert not res


def test_check_if_text_value_property_link_prop() -> None:
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
    res = _check_if_text_value_property(test_dict)
    assert not res


def test_check_if_text_value_property_text_prop() -> None:
    test_dict = {
        "rdfs:label": "Textarea",
        "rdfs:subPropertyOf": {},
        "knora-api:isResourceProperty": True,
        "knora-api:objectType": {"@id": "knora-api:TextValue"},
        "salsah-gui:guiElement": {"@id": "salsah-gui:Textarea"},
        "@id": "onto:hasTextarea",
    }
    res = _check_if_text_value_property(test_dict)
    assert res


def test_make_text_value_property_gui() -> None:
    test_list = [
        ("onto:hasSimpleText", "salsah-gui:SimpleText"),
        ("onto_other:hasTextarea", "salsah-gui:Textarea"),
        ("onto:hasRichtext", "salsah-gui:Richtext"),
        ("other_onto:hasRichtext", "salsah-gui:Richtext"),
        ("onto:ontoHasSimpleText", "salsah-gui:SimpleText"),
    ]
    res = _make_text_value_property_type_lookup(test_list)
    assert res.formatted_text_props == {"onto:hasRichtext", "other_onto:hasRichtext", "hasComment", "hasDescription"}
    assert res.unformatted_text_props == {
        "onto:hasSimpleText",
        "onto_other:hasTextarea",
        "onto:ontoHasSimpleText",
        "hasTitle",
        "hasKeyword",
    }


if __name__ == "__main__":
    pytest.main([__file__])
