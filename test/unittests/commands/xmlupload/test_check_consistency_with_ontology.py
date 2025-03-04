from collections import defaultdict

import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.models.lookup_models import OntoInfo
from dsp_tools.commands.xmlupload.models.lookup_models import ProjectOntosInformation
from dsp_tools.commands.xmlupload.models.lookup_models import PropertyTextValueTypes
from dsp_tools.commands.xmlupload.models.lookup_models import TextValueData
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _check_all_classes_and_properties_in_onto,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _check_correctness_all_text_value_encodings,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _check_correctness_of_one_prop,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import _find_all_class_types_in_onto
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import _find_all_properties_in_onto
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import _find_one_class_type_in_onto
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import _find_one_property_in_onto
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _get_all_class_types_and_ids_from_data,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _get_all_classes_and_properties_from_data,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _get_all_ids_and_props_and_encodings_from_root,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _get_all_property_names_and_resource_ids_one_resource,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _get_id_and_props_and_encodings_from_one_resource,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _get_prop_and_encoding_from_one_property,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    _get_separate_prefix_and_iri_from_onto_prop_or_cls,
)

DEFAULT_ONTO_PREFIX = "my_onto"


class TestFindClassType:
    def test_no_knora_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _find_one_class_type_in_onto("knoraClassA", onto_lookup)

    def test_knora_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _find_one_class_type_in_onto("knora-api:knoraClassA", onto_lookup)

    def test_no_default_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _find_one_class_type_in_onto(":classA", onto_lookup)

    def test_default_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _find_one_class_type_in_onto("test:classB", onto_lookup)

    def test_unknown_class(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert _find_one_class_type_in_onto("test:classC", onto_lookup) == "Invalid Class Type"

    def test_unknown_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert _find_one_class_type_in_onto("other:classC", onto_lookup) == "Unknown ontology prefix"

    def test_diagnose_all_classes_no_problems(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        test_classes = {"knora-api:knoraClassA": ["idA"], ":classB": ["idB"]}
        assert not _find_all_class_types_in_onto(test_classes, onto_lookup)

    def test_diagnose_all_classes_problems(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        test_classes = {"knoraClassA": ["idA"], ":classD": ["idD"]}
        assert _find_all_class_types_in_onto(test_classes, onto_lookup) == [(":classD", ["idD"], "Invalid Class Type")]


class TestFindProperties:
    def test_no_knora_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _find_one_property_in_onto("knoraPropA", onto_lookup)

    def test_knora_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _find_one_property_in_onto("knora-api:knoraPropA", onto_lookup)

    def test_no_default_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _find_one_property_in_onto(":propA", onto_lookup)

    def test_default_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _find_one_property_in_onto("test:propB", onto_lookup)

    def test_unknown_prefix(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert _find_one_property_in_onto("other:propB", onto_lookup) == "Unknown ontology prefix"

    def test_unknown_property(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert _find_one_property_in_onto("test:propC", onto_lookup) == "Invalid Property"

    def test_diagnose_all_properties_problems(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        test_properties = {"test:propB": ["idB"], "other:propB": ["idB"], "test:propD": ["idD"]}
        expected = [("other:propB", ["idB"], "Unknown ontology prefix"), ("test:propD", ["idD"], "Invalid Property")]
        assert unordered(_find_all_properties_in_onto(test_properties, onto_lookup)) == expected

    def test_diagnose_all_properties_no_problems(self) -> None:
        onto_lookup = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        test_properties = {"test:propB": ["idB"], "knoraPropA": ["idA"]}
        assert not unordered(_find_all_properties_in_onto(test_properties, onto_lookup))


def test_check_all_classes_and_properties_in_onto() -> None:
    onto_lookup = ProjectOntosInformation(
        default_ontology_prefix="test",
        onto_lookup={
            "test": OntoInfo(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": OntoInfo(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    classes = {"knoraClassA": ["idA"]}
    properties = {"knora-api:knoraPropA": ["idA"]}
    res_msg = _check_all_classes_and_properties_in_onto(classes, properties, onto_lookup)
    assert not res_msg


def test_check_all_classes_and_properties_in_onto_problem() -> None:
    onto_lookup = ProjectOntosInformation(
        default_ontology_prefix="test",
        onto_lookup={
            "test": OntoInfo(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": OntoInfo(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    classes = {"knora": ["idA"]}
    properties = {"knora-api:knoraPropA": ["idA"]}
    expected_msg = (
        "\nSome property and/or class type(s) used in the XML are unknown.\n"
        "The ontologies for your project on the server are:\n"
        "    - test\n"
        "    - knora-api"
        "\n\n"
        "The following resource(s) have an invalid resource type:\n\n"
        "    Resource Type: 'knora'\n"
        "    Problem: 'Invalid Class Type'\n"
        "    Resource ID(s):\n"
        "    - idA"
        "\n\n"
    )
    res_msg = _check_all_classes_and_properties_in_onto(classes, properties, onto_lookup)
    assert res_msg == expected_msg


def test_get_prefix_and_prop_cls_identifier() -> None:
    assert _get_separate_prefix_and_iri_from_onto_prop_or_cls(":propA", "test") == ("test", "propA")
    assert _get_separate_prefix_and_iri_from_onto_prop_or_cls("knora-api:knoraPropA", "test") == (
        "knora-api",
        "knoraPropA",
    )
    assert _get_separate_prefix_and_iri_from_onto_prop_or_cls("knoraPropB", "test") == ("knora-api", "knoraPropB")
    assert _get_separate_prefix_and_iri_from_onto_prop_or_cls("test:propA", "test") == ("test", "propA")


def test_get_prefix_and_prop_cls_identifier_error() -> None:
    assert _get_separate_prefix_and_iri_from_onto_prop_or_cls("123654/", "test") == (None, None)


def test_get_all_class_types_and_ids_from_data() -> None:
    test_ele = etree.fromstring(
        """<knora shortcode="4123" default-ontology="test">
                <resource label="resA" restype=":TestThing1" id="resA" permissions="open"/>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="open"/>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="open"/>
        </knora>"""
    )
    expected_classes = {":TestThing1": ["resA"], ":TestThing2": ["resB", "resC"]}
    res_classes = _get_all_class_types_and_ids_from_data(test_ele)
    assert res_classes.keys() == expected_classes.keys()
    for k, v in res_classes.items():
        assert unordered(v) == expected_classes[k]


def test_get_all_property_names_and_resource_ids_one_resource() -> None:
    test_ele = etree.fromstring(
        """<resource label="resC" restype=":TestThing2" id="resC" permissions="open">
                <resptr-prop name=":hasResource2">
                    <resptr permissions="open">resB</resptr>
                </resptr-prop>
                <resptr-prop name=":hasResource3">
                    <resptr permissions="open">resA</resptr>
                </resptr-prop>
            </resource>"""
    )
    expected = {"a": ["a"], ":hasResource2": ["resB", "resC"], ":hasResource3": ["resC"]}
    res_dic = _get_all_property_names_and_resource_ids_one_resource(
        test_ele, defaultdict(list, {"a": ["a"], ":hasResource2": ["resB"]})
    )
    assert res_dic.keys() == expected.keys()
    for k, v in res_dic.items():
        assert unordered(v) == expected[k]


def test_get_all_classes_and_properties_from_data() -> None:
    test_ele = etree.fromstring(
        """<knora shortcode="4123" default-ontology="test">
                <resource label="resA" restype=":TestThing1" id="resA" permissions="open">
                    <resptr-prop name=":hasResource1">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="open">
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                    <resptr-prop name=":hasResource3">
                        <resptr permissions="open">resA</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    expected_classes = {":TestThing1": ["resA"], ":TestThing2": ["resB", "resC"]}
    expected_properties = {
        ":hasResource1": ["resA"],
        ":hasResource2": ["resC"],
        ":hasResource3": ["resC"],
    }
    res_classes, res_properties = _get_all_classes_and_properties_from_data(test_ele)
    assert res_classes.keys() == expected_classes.keys()
    for k, v in res_classes.items():
        assert unordered(v) == expected_classes[k]
    assert res_properties.keys() == expected_properties.keys()
    for k, v in res_properties.items():
        assert unordered(v) == expected_properties[k]


def test_get_id_and_props_and_encodings_from_one_resource_no_text() -> None:
    test_props = etree.fromstring(
        """
        <resource label="First Testthing"
              restype=":TestThing"
              id="test_thing_1"
              permissions="open">
            <uri-prop name=":hasUri">
                <uri permissions="open">https://dasch.swiss</uri>
            </uri-prop>
            <boolean-prop name=":hasBoolean">
                <boolean permissions="open">true</boolean>
            </boolean-prop>
        </resource>
        """
    )
    res = _get_id_and_props_and_encodings_from_one_resource(test_props, DEFAULT_ONTO_PREFIX)
    assert not res


def test_get_id_and_props_and_encodings_from_one_resource_richtext() -> None:
    test_props = etree.fromstring(
        """
        <resource label="First Testthing"
              restype=":TestThing"
              id="test_thing_1"
              permissions="open">
            <uri-prop name=":hasUri">
                <uri permissions="open">https://dasch.swiss</uri>
            </uri-prop>
            <boolean-prop name=":hasBoolean">
                <boolean permissions="open">true</boolean>
            </boolean-prop>
            <text-prop name=":hasRichtext">
                <text encoding="utf8">Text</text>
            </text-prop>
        </resource>
        """
    )
    res = _get_id_and_props_and_encodings_from_one_resource(test_props, DEFAULT_ONTO_PREFIX)[0]
    assert res.resource_id == "test_thing_1"
    assert res.property_name == f"{DEFAULT_ONTO_PREFIX}:hasRichtext"
    assert res.encoding == "utf8"


def test_get_id_and_props_and_encodings_from_one_resource_two_text_props() -> None:
    test_props = etree.fromstring(
        """
        <resource label="First Testthing"
              restype=":TestThing"
              id="test_thing_1"
              permissions="open">
            <uri-prop name=":hasUri">
                <uri permissions="open">https://dasch.swiss</uri>
            </uri-prop>
            <boolean-prop name=":hasBoolean">
                <boolean permissions="open">true</boolean>
            </boolean-prop>
            <text-prop name=":hasRichtext">
                <text encoding="xml">Text</text>
            </text-prop>
            <text-prop name=":hasSimpleText">
                <text encoding="utf8">Text</text>
            </text-prop>
        </resource>
        """
    )
    res = _get_id_and_props_and_encodings_from_one_resource(test_props, DEFAULT_ONTO_PREFIX)
    assert res[0].resource_id == "test_thing_1"
    assert res[0].property_name == f"{DEFAULT_ONTO_PREFIX}:hasRichtext"
    assert res[0].encoding == "xml"
    assert res[1].resource_id == "test_thing_1"
    assert res[1].property_name == f"{DEFAULT_ONTO_PREFIX}:hasSimpleText"
    assert res[1].encoding == "utf8"


class TestGetEncodingOneProperty:
    def test_richtext_several_text_ele(self) -> None:
        test_prop = etree.fromstring(
            """
            <text-prop name=":hasRichtext">
                <text encoding="xml">&lt;</text>
                <text encoding="xml" permissions="open">
                    This text contains links to all resources:
                    <a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>
                </text>
                <text encoding="xml">Text with an external link: <a href="https://www.google.com/">Google</a></text>
            </text-prop>
            """
        )
        res_info = _get_prop_and_encoding_from_one_property("id", ":resType", test_prop, DEFAULT_ONTO_PREFIX)
        assert res_info.resource_id == "id"
        assert res_info.res_type == ":resType"
        assert res_info.property_name == f"{DEFAULT_ONTO_PREFIX}:hasRichtext"
        assert res_info.encoding == "xml"

    def test_simple_several_text_ele(self) -> None:
        test_prop = etree.fromstring(
            """
            <text-prop name=":hasRichtext">
                <text encoding="utf8">Text</text>
                <text encoding="utf8">Text</text>
            </text-prop>
            """
        )
        res_info = _get_prop_and_encoding_from_one_property("id", ":resType", test_prop, DEFAULT_ONTO_PREFIX)
        assert res_info.resource_id == "id"
        assert res_info.res_type == ":resType"
        assert res_info.property_name == f"{DEFAULT_ONTO_PREFIX}:hasRichtext"
        assert res_info.encoding == "utf8"

    def test_simple_one_text_ele(self) -> None:
        test_prop = etree.fromstring(
            """
            <text-prop name=":hasRichtext">
                <text encoding="utf8">Text</text>
            </text-prop>
            """
        )
        res_info = _get_prop_and_encoding_from_one_property("id", ":resType", test_prop, DEFAULT_ONTO_PREFIX)
        assert res_info.resource_id == "id"
        assert res_info.res_type == ":resType"
        assert res_info.property_name == f"{DEFAULT_ONTO_PREFIX}:hasRichtext"
        assert res_info.encoding == "utf8"


def test_get_all_ids_and_props_and_encodings_from_root_no_text() -> None:
    test_ele = etree.fromstring(
        """<knora>
                <resource label="resA" restype=":TestThing1" id="resA" permissions="open">
                    <resptr-prop name=":hasResource1">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="open">
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                    <resptr-prop name=":hasResource3">
                        <resptr permissions="open">resA</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    res = _get_all_ids_and_props_and_encodings_from_root(test_ele, DEFAULT_ONTO_PREFIX)
    assert res == []


def test_get_all_ids_and_props_and_encodings_from_root_with_text() -> None:
    test_ele = etree.fromstring(
        """<knora>
                <resource label="First Testthing"
                      restype=":TestThing"
                      id="test_thing_1"
                      permissions="open">
                    <uri-prop name=":hasUri">
                        <uri permissions="open">https://dasch.swiss</uri>
                    </uri-prop>
                    <text-prop name=":hasRichtext">
                        <text encoding="xml">Text</text>
                    </text-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="open">
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    res = _get_all_ids_and_props_and_encodings_from_root(test_ele, DEFAULT_ONTO_PREFIX)
    assert res[0].resource_id == "test_thing_1"
    assert res[0].property_name == f"{DEFAULT_ONTO_PREFIX}:hasRichtext"
    assert res[0].encoding == "xml"
    assert res[1].resource_id == "resB"
    assert res[1].property_name == f"{DEFAULT_ONTO_PREFIX}:hasSimpleText"
    assert res[1].encoding == "utf8"
    assert res[2].resource_id == "resC"
    assert res[2].property_name == f"{DEFAULT_ONTO_PREFIX}:hasSimpleText"
    assert res[2].encoding == "utf8"


class TestCheckCorrectnessOneProp:
    def test_utf_simple_correct(self) -> None:
        test_val = TextValueData("id", ":restype", "test-onto_2:prop", "utf8")
        test_lookup = PropertyTextValueTypes(set(), {"test-onto_2:prop"})
        assert _check_correctness_of_one_prop(test_val, test_lookup) is True

    def test_utf_simple_wrong(self) -> None:
        test_val = TextValueData("id", ":restype", "test-onto_2:prop", "utf8")
        test_lookup = PropertyTextValueTypes({"test-onto_2:prop"}, set())
        assert _check_correctness_of_one_prop(test_val, test_lookup) is False

    def test_xml_correct(self) -> None:
        test_val = TextValueData("id", ":restype", "test-onto_2:prop", "xml")
        test_lookup = PropertyTextValueTypes({"test-onto_2:prop"}, set())
        assert _check_correctness_of_one_prop(test_val, test_lookup) is True

    def test_xml_wrong(self) -> None:
        test_val = TextValueData("id", ":restype", "test-onto_2:prop", "xml")
        test_lookup = PropertyTextValueTypes(set(), set())
        assert _check_correctness_of_one_prop(test_val, test_lookup) is False


def test_analyse_all_text_value_encodings_are_correct_all_good() -> None:
    test_ele = etree.fromstring(
        """<knora>
                <resource label="First Testthing"
                      restype=":TestThing"
                      id="test_thing_1"
                      permissions="open">
                    <uri-prop name=":hasUri">
                        <uri permissions="open">https://dasch.swiss</uri>
                    </uri-prop>
                    <text-prop name=":hasRichtext">
                        <text encoding="xml">Text</text>
                    </text-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="open">
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    test_lookup = PropertyTextValueTypes(
        formatted_text_props={f"{DEFAULT_ONTO_PREFIX}:hasRichtext"},
        unformatted_text_props={f"{DEFAULT_ONTO_PREFIX}:hasSimpleText", ":hasText"},
    )
    res_msg = _check_correctness_all_text_value_encodings(test_ele, test_lookup, DEFAULT_ONTO_PREFIX)
    assert not res_msg


def test_analyse_all_text_value_encodings_are_correct_problems() -> None:
    test_ele = etree.fromstring(
        """<knora>
                <resource label="First Testthing"
                      restype=":TestThing"
                      id="test_thing_1"
                      permissions="open">
                    <uri-prop name=":hasUri">
                        <uri permissions="open">https://dasch.swiss</uri>
                    </uri-prop>
                    <text-prop name=":hasText">
                        <text encoding="xml">Text</text>
                    </text-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="open">
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                    <text-prop name=":hasRichtext">
                        <text encoding="utf8">Text</text>
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    test_lookup = PropertyTextValueTypes(
        formatted_text_props={f"{DEFAULT_ONTO_PREFIX}:hasRichtext"},
        unformatted_text_props={f"{DEFAULT_ONTO_PREFIX}:hasSimpleText", f"{DEFAULT_ONTO_PREFIX}:hasText"},
    )
    expected_msg = (
        "\nSome text encodings used in the XML data file are not conform with the gui_element "
        "specified in the JSON ontology.\n"
        "Please consult the ontology regarding the assigned gui_elements."
        "\n\n"
        "Resource ID: 'resC' | Resource Type: ':TestThing2'\n"
        f"    - Property Name: '{DEFAULT_ONTO_PREFIX}:hasRichtext' -> Encoding Used: 'utf8'"
        "\n\n"
        "Resource ID: 'test_thing_1' | Resource Type: ':TestThing'\n"
        f"    - Property Name: '{DEFAULT_ONTO_PREFIX}:hasText' -> Encoding Used: 'xml'"
    )
    res_msg = _check_correctness_all_text_value_encodings(test_ele, test_lookup, DEFAULT_ONTO_PREFIX)
    assert res_msg == expected_msg


if __name__ == "__main__":
    pytest.main([__file__])
