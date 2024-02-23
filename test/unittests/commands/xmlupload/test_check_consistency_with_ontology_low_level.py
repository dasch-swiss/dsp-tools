from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import (
    _analyse_all_text_value_encodings_are_correct,
    _check_correct,
    _check_correctness_one_prop,
    _find_all_class_types_in_onto,
    _find_all_classes_and_properties_exist_in_onto,
    _find_all_properties_in_onto,
    _find_one_class_type_in_onto,
    _find_one_property_in_onto,
    _get_all_class_types_and_ids_from_data,
    _get_all_classes_and_properties_from_data,
    _get_all_ids_prop_encoding_from_root,
    _get_all_property_names_and_resource_ids_one_resource,
    _get_id_prop_encoding_from_one_resource,
    _get_prop_encoding_from_one_property,
    _get_separate_prefix_and_iri_from_onto_prop_or_cls,
)
from dsp_tools.commands.xmlupload.models.ontology_lookup_models import (
    OntoInfo,
    ProjectOntosInformation,
    PropertyTextValueEncodingTypes,
    TextValueData,
)


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


def test_find_all_classes_and_properties_exist_in_onto() -> None:
    onto_lookup = ProjectOntosInformation(
        default_ontology_prefix="test",
        onto_lookup={
            "test": OntoInfo(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": OntoInfo(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    classes = {"knoraClassA": ["idA"]}
    properties = {"knora-api:knoraPropA": ["idA"]}
    res_msg = _find_all_classes_and_properties_exist_in_onto(classes, properties, onto_lookup)
    assert not res_msg


def test_find_all_classes_and_properties_exist_in_onto_problem() -> None:
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
        "\n\n---------------------------------------\n\n"
        "The following resource(s) have an invalid resource type:\n\n"
        "    Resource Type: 'knora'\n"
        "    Problem: 'Invalid Class Type'\n"
        "    Resource ID(s):\n"
        "    - idA"
        "\n\n---------------------------------------\n\n"
    )
    res_msg = _find_all_classes_and_properties_exist_in_onto(classes, properties, onto_lookup)
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
                <resource label="resA" restype=":TestThing1" id="resA" permissions="res-default"/>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="res-default"/>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default"/>
        </knora>"""
    )
    expected_classes = {":TestThing1": ["resA"], ":TestThing2": ["resB", "resC"]}
    res_classes = _get_all_class_types_and_ids_from_data(test_ele)
    assert res_classes.keys() == expected_classes.keys()
    for k, v in res_classes.items():
        assert unordered(v) == expected_classes[k]


def test_get_all_property_names_and_resource_ids_one_resource() -> None:
    test_ele = etree.fromstring(
        """<resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                <resptr-prop name=":hasResource2">
                    <resptr permissions="prop-default">resB</resptr>
                </resptr-prop>
                <resptr-prop name=":hasResource3">
                    <resptr permissions="prop-default">resA</resptr>
                </resptr-prop>
            </resource>"""
    )
    expected = {"a": ["a"], ":hasResource2": ["resC"], ":hasResource3": ["resC"]}
    res_dic = _get_all_property_names_and_resource_ids_one_resource(test_ele, {"a": ["a"]})
    assert res_dic.keys() == expected.keys()
    for k, v in res_dic.items():
        assert unordered(v) == expected[k]


def test_get_all_classes_and_properties_from_data() -> None:
    test_ele = etree.fromstring(
        """<knora shortcode="4123" default-ontology="test">
                <resource label="resA" restype=":TestThing1" id="resA" permissions="res-default">
                    <resptr-prop name=":hasResource1">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="res-default">
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                    <resptr-prop name=":hasResource3">
                        <resptr permissions="prop-default">resA</resptr>
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


def test_get_id_prop_encoding_from_one_resource_no_text() -> None:
    test_props = etree.fromstring(
        """
        <resource label="First Testthing"
              restype=":TestThing"
              id="test_thing_1"
              permissions="res-default">
            <uri-prop name=":hasUri">
                <uri permissions="prop-default">https://dasch.swiss</uri>
            </uri-prop>
            <boolean-prop name=":hasBoolean">
                <boolean permissions="prop-default">true</boolean>
            </boolean-prop>
        </resource>
        """
    )
    res = _get_id_prop_encoding_from_one_resource(test_props)
    assert not res


def test_get_id_prop_encoding_from_one_resource_richtext() -> None:
    test_props = etree.fromstring(
        """
        <resource label="First Testthing"
              restype=":TestThing"
              id="test_thing_1"
              permissions="res-default">
            <uri-prop name=":hasUri">
                <uri permissions="prop-default">https://dasch.swiss</uri>
            </uri-prop>
            <boolean-prop name=":hasBoolean">
                <boolean permissions="prop-default">true</boolean>
            </boolean-prop>
            <text-prop name=":hasRichtext">
                <text encoding="utf8">Text</text>
            </text-prop>
        </resource>
        """
    )
    res = _get_id_prop_encoding_from_one_resource(test_props)[0]
    assert res.resource_id == "test_thing_1"
    assert res.property_name == ":hasRichtext"
    assert res.encoding == "utf8"


def test_get_id_prop_encoding_from_one_resource_two_text_props() -> None:
    test_props = etree.fromstring(
        """
        <resource label="First Testthing"
              restype=":TestThing"
              id="test_thing_1"
              permissions="res-default">
            <uri-prop name=":hasUri">
                <uri permissions="prop-default">https://dasch.swiss</uri>
            </uri-prop>
            <boolean-prop name=":hasBoolean">
                <boolean permissions="prop-default">true</boolean>
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
    res: list[TextValueData] = _get_id_prop_encoding_from_one_resource(test_props)
    assert res[0].resource_id == "test_thing_1"
    assert res[0].property_name == ":hasRichtext"
    assert res[0].encoding == "xml"
    assert res[1].resource_id == "test_thing_1"
    assert res[1].property_name == ":hasSimpleText"
    assert res[1].encoding == "utf8"


class TestGetEncodingOneProperty:
    def test_richtext_several_text_ele(self) -> None:
        test_prop = etree.fromstring(
            """
            <text-prop name=":hasRichtext">
                <text encoding="xml">&lt;</text>
                <text encoding="xml" permissions="prop-default">
                    This text contains links to all resources:
                    <a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>
                </text>
                <text encoding="xml">Text with an external link: <a href="https://www.google.com/">Google</a></text>
            </text-prop>
            """
        )
        res_info = _get_prop_encoding_from_one_property("id", test_prop)
        assert res_info.resource_id == "id"
        assert res_info.property_name == ":hasRichtext"
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
        res_info = _get_prop_encoding_from_one_property("id", test_prop)
        assert res_info.resource_id == "id"
        assert res_info.property_name == ":hasRichtext"
        assert res_info.encoding == "utf8"

    def test_simple_one_text_ele(self) -> None:
        test_prop = etree.fromstring(
            """
            <text-prop name=":hasRichtext">
                <text encoding="utf8">Text</text>
            </text-prop>
            """
        )
        res_info = _get_prop_encoding_from_one_property("id", test_prop)
        assert res_info.resource_id == "id"
        assert res_info.property_name == ":hasRichtext"
        assert res_info.encoding == "utf8"


def test_get_all_ids_prop_encoding_from_root_no_text() -> None:
    test_ele = etree.fromstring(
        """<knora>
                <resource label="resA" restype=":TestThing1" id="resA" permissions="res-default">
                    <resptr-prop name=":hasResource1">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="res-default">
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                    <resptr-prop name=":hasResource3">
                        <resptr permissions="prop-default">resA</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    res = _get_all_ids_prop_encoding_from_root(test_ele)
    assert res == []


def test_get_all_ids_prop_encoding_from_root_with_text() -> None:
    test_ele = etree.fromstring(
        """<knora>
                <resource label="First Testthing"
                      restype=":TestThing"
                      id="test_thing_1"
                      permissions="res-default">
                    <uri-prop name=":hasUri">
                        <uri permissions="prop-default">https://dasch.swiss</uri>
                    </uri-prop>
                    <text-prop name=":hasRichtext">
                        <text encoding="xml">Text</text>
                    </text-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="res-default">
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    res = _get_all_ids_prop_encoding_from_root(test_ele)
    assert res[0].resource_id == "test_thing_1"
    assert res[0].property_name == ":hasRichtext"
    assert res[0].encoding == "xml"
    assert res[1].resource_id == "resB"
    assert res[1].property_name == ":hasSimpleText"
    assert res[1].encoding == "utf8"
    assert res[2].resource_id == "resC"
    assert res[2].property_name == ":hasSimpleText"
    assert res[2].encoding == "utf8"


def test_check_correct_true() -> None:
    res = _check_correct(":prop", {":prop", ":other"})
    assert res is True


def test_check_correct_false() -> None:
    res = _check_correct(":nope", {":prop", ":other"})
    assert res is False


class TestCheckCorrectnessOneProp:
    def test_utf_simple_correct(self) -> None:
        test_val = TextValueData("id", ":prop", "utf8")
        test_lookup = PropertyTextValueEncodingTypes(set(), {":prop"})
        assert _check_correctness_one_prop(test_val, test_lookup) is True

    def test_utf_simple_wrong(self) -> None:
        test_val = TextValueData("id", ":prop", "utf8")
        test_lookup = PropertyTextValueEncodingTypes({":prop"}, set())
        assert _check_correctness_one_prop(test_val, test_lookup) is False

    def test_xml_correct(self) -> None:
        test_val = TextValueData("id", ":prop", "xml")
        test_lookup = PropertyTextValueEncodingTypes({":prop"}, set())
        assert _check_correctness_one_prop(test_val, test_lookup) is True

    def test_xml_wrong(self) -> None:
        test_val = TextValueData("id", ":prop", "xml")
        test_lookup = PropertyTextValueEncodingTypes(set(), set())
        assert _check_correctness_one_prop(test_val, test_lookup) is False


def test_analyse_all_text_value_encodings_are_correct_all_good() -> None:
    test_ele = etree.fromstring(
        """<knora>
                <resource label="First Testthing"
                      restype=":TestThing"
                      id="test_thing_1"
                      permissions="res-default">
                    <uri-prop name=":hasUri">
                        <uri permissions="prop-default">https://dasch.swiss</uri>
                    </uri-prop>
                    <text-prop name=":hasRichtext">
                        <text encoding="xml">Text</text>
                    </text-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="res-default">
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    test_lookup = PropertyTextValueEncodingTypes(
        formatted_text={":hasRichtext"}, unformatted_text={":hasSimpleText", ":hasText"}
    )
    _analyse_all_text_value_encodings_are_correct(test_ele, test_lookup)


def test_analyse_all_text_value_encodings_are_correct_problems() -> None:
    test_ele = etree.fromstring(
        """<knora>
                <resource label="First Testthing"
                      restype=":TestThing"
                      id="test_thing_1"
                      permissions="res-default">
                    <uri-prop name=":hasUri">
                        <uri permissions="prop-default">https://dasch.swiss</uri>
                    </uri-prop>
                    <text-prop name=":hasText">
                        <text encoding="xml">Text</text>
                    </text-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="res-default">
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                    <text-prop name=":hasRichtext">
                        <text encoding="utf8">Text</text>
                        <text encoding="utf8">Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    test_lookup = PropertyTextValueEncodingTypes(
        formatted_text={":hasRichtext"}, unformatted_text={":hasSimpleText", ":hasText"}
    )
    expected_msg = (
        "\nSome text encodings used in the data is not conform with the gui-element specified in the ontology.\n"
        "Please consult the ontology regarding the assigned gui-elements."
        "\n\n---------------------------------------\n\n"
        "Resource ID: 'resC'\n"
        "    - Property Name: ':hasRichtext' -> Encoding Used: 'utf8'"
        "\n----------------------------\n"
        "Resource ID: 'test_thing_1'\n"
        "    - Property Name: ':hasText' -> Encoding Used: 'xml'"
    )
    res_msg = _analyse_all_text_value_encodings_are_correct(test_ele, test_lookup)
    assert res_msg == expected_msg
