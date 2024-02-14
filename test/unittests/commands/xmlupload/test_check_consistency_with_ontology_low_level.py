import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import (
    _analyse_if_all_text_value_encodings_are_correct,
    _check_correctness_one_prop,
    _check_if_all_class_types_exist,
    _check_if_all_properties_exist,
    _check_if_correct,
    _check_if_one_class_type_exists,
    _check_if_one_property_exists,
    _find_if_all_classes_and_properties_exist_in_onto,
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
    TextValueData,
    TextValuePropertyGUI,
)
from dsp_tools.models.exceptions import InputError


class TestCheckClassType:
    def test_no_knora_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _check_if_one_class_type_exists("knoraClassA", onto_check_info)

    def test_knora_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _check_if_one_class_type_exists("knora-api:knoraClassA", onto_check_info)

    def test_no_default_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _check_if_one_class_type_exists(":classA", onto_check_info)

    def test_default_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _check_if_one_class_type_exists("test:classB", onto_check_info)

    def test_unknown_class(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert _check_if_one_class_type_exists("test:classC", onto_check_info) == "Invalid Class Type"

    def test_unknown_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert _check_if_one_class_type_exists("other:classC", onto_check_info) == "Unknown ontology prefix"

    def test_diagnose_all_classes_no_problems(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        test_classes = {"knora-api:knoraClassA": ["idA"], ":classB": ["idB"]}
        assert not _check_if_all_class_types_exist(test_classes, onto_check_info)

    def test_diagnose_all_classes_problems(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        test_classes = {"knoraClassA": ["idA"], ":classD": ["idD"]}
        assert _check_if_all_class_types_exist(test_classes, onto_check_info) == [
            (":classD", ["idD"], "Invalid Class Type")
        ]


class TestCheckProperties:
    def test_no_knora_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _check_if_one_property_exists("knoraPropA", onto_check_info)

    def test_knora_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _check_if_one_property_exists("knora-api:knoraPropA", onto_check_info)

    def test_no_default_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _check_if_one_property_exists(":propA", onto_check_info)

    def test_default_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _check_if_one_property_exists("test:propB", onto_check_info)

    def test_unknown_prefix(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert _check_if_one_property_exists("other:propB", onto_check_info) == "Unknown ontology prefix"

    def test_unknown_property(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert _check_if_one_property_exists("test:propC", onto_check_info) == "Invalid Property"

    def test_diagnose_all_properties_problems(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        test_properties = {"test:propB": ["idB"], "other:propB": ["idB"], "test:propD": ["idD"]}
        expected = [("other:propB", ["idB"], "Unknown ontology prefix"), ("test:propD", ["idD"], "Invalid Property")]
        assert unordered(_check_if_all_properties_exist(test_properties, onto_check_info)) == expected

    def test_diagnose_all_properties_no_problems(self) -> None:
        onto_check_info = ProjectOntosInformation(
            default_ontology_prefix="test",
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        test_properties = {"test:propB": ["idB"], "knoraPropA": ["idA"]}
        assert not unordered(_check_if_all_properties_exist(test_properties, onto_check_info))


def test_find_if_all_classes_and_properties_exist_in_onto() -> None:
    onto_check_info = ProjectOntosInformation(
        default_ontology_prefix="test",
        onto_lookup={
            "test": OntoInfo(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": OntoInfo(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    classes = {"knoraClassA": ["idA"]}
    properties = {"knora-api:knoraPropA": ["idA"]}
    _find_if_all_classes_and_properties_exist_in_onto(classes, properties, onto_check_info)


def test_find_if_all_classes_and_properties_exist_in_onto_problem() -> None:
    onto_check_info = ProjectOntosInformation(
        default_ontology_prefix="test",
        onto_lookup={
            "test": OntoInfo(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": OntoInfo(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    classes = {"knora": ["idA"]}
    properties = {"knora-api:knoraPropA": ["idA"]}
    with pytest.raises(InputError):
        _find_if_all_classes_and_properties_exist_in_onto(classes, properties, onto_check_info)


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


def test_get_prop_encoding_from_all_properties_no_text() -> None:
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
    assert res is None


def test_get_prop_encoding_from_all_properties_mixed() -> None:
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
    res = _get_id_prop_encoding_from_one_resource(test_props)[0]  # type: ignore[index]
    assert res.resource_id == "test_thing_1"
    assert res.property_name == ":hasRichtext"
    assert res.encoding == {"utf8"}


def test_get_prop_encoding_from_all_properties_two_text_prop() -> None:
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
                <text>Text</text>
            </text-prop>
        </resource>
        """
    )
    res: list[TextValueData] = _get_id_prop_encoding_from_one_resource(test_props)  # type: ignore[assignment]
    assert res[0].resource_id == "test_thing_1"
    assert res[0].property_name == ":hasRichtext"
    assert res[0].encoding == {"xml"}
    assert res[1].resource_id == "test_thing_1"
    assert res[1].property_name == ":hasSimpleText"
    assert res[1].encoding == {None}


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
        assert res_info.encoding == {"xml"}

    def test_simple_several_text_ele(self) -> None:
        test_prop = etree.fromstring(
            """
            <text-prop name=":hasRichtext">
                <text encoding="utf8">Text</text>
                <text>Text</text>
            </text-prop>
            """
        )
        res_info = _get_prop_encoding_from_one_property("id", test_prop)
        assert res_info.resource_id == "id"
        assert res_info.property_name == ":hasRichtext"
        assert res_info.encoding == {"utf8", None}

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
        assert res_info.encoding == {"utf8"}


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
                        <text>Text</text>
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
    assert res[0].encoding == {"xml"}
    assert res[1].resource_id == "resB"
    assert res[1].property_name == ":hasSimpleText"
    assert res[1].encoding == {None}
    assert res[2].resource_id == "resC"
    assert res[2].property_name == ":hasSimpleText"
    assert res[2].encoding == {"utf8"}


def test_check_if_correct_true() -> None:
    res = _check_if_correct(":prop", {":prop", ":other"})
    assert res is True


def test_check_if_correct_false() -> None:
    res = _check_if_correct(":nope", {":prop", ":other"})
    assert res is False


class TestCheckCorrectnessOneProp:
    def test_utf_simple_correct(self) -> None:
        test_val = TextValueData("id", ":prop", {"utf8"})
        test_lookup = TextValuePropertyGUI(set(), {":prop"})
        assert _check_correctness_one_prop(test_val, test_lookup) is True

    def test_none_simple_correct(self) -> None:
        test_val = TextValueData("id", ":prop", {None})
        test_lookup = TextValuePropertyGUI(set(), {":prop"})
        assert _check_correctness_one_prop(test_val, test_lookup) is True

    def test_both_simple_correct(self) -> None:
        test_val = TextValueData("id", ":prop", {None, "utf8"})
        test_lookup = TextValuePropertyGUI(set(), {":prop"})
        assert _check_correctness_one_prop(test_val, test_lookup) is True

    def test_utf_simple_wrong(self) -> None:
        test_val = TextValueData("id", ":prop", {"utf8"})
        test_lookup = TextValuePropertyGUI({":prop"}, set())
        assert _check_correctness_one_prop(test_val, test_lookup) is False

    def test_none_simple_wrong(self) -> None:
        test_val = TextValueData("id", ":prop", {None})
        test_lookup = TextValuePropertyGUI({":prop"}, set())
        assert _check_correctness_one_prop(test_val, test_lookup) is False

    def test_both_simple_wrong(self) -> None:
        test_val = TextValueData("id", ":prop", {None, "utf8"})
        test_lookup = TextValuePropertyGUI({":prop"}, set())
        assert _check_correctness_one_prop(test_val, test_lookup) is False

    def test_xml_correct(self) -> None:
        test_val = TextValueData("id", ":prop", {"xml"})
        test_lookup = TextValuePropertyGUI({":prop"}, set())
        assert _check_correctness_one_prop(test_val, test_lookup) is True

    def test_xml_wrong(self) -> None:
        test_val = TextValueData("id", ":prop", {"xml"})
        test_lookup = TextValuePropertyGUI(set(), set())
        assert _check_correctness_one_prop(test_val, test_lookup) is False

    def test_mixed_wrong(self) -> None:
        test_val = TextValueData("id", ":prop", {"xml", None})
        test_lookup = TextValuePropertyGUI(set(), set())
        assert _check_correctness_one_prop(test_val, test_lookup) is False


def test_check_if_all_text_value_encodings_are_correct_all_good() -> None:
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
                        <text>Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Text</text>
                        <text>Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    test_lookup = TextValuePropertyGUI(formatted_text={":hasRichtext"}, unformatted_text={":hasSimpleText", ":hasText"})
    _analyse_if_all_text_value_encodings_are_correct(test_ele, test_lookup)


def test_check_if_all_text_value_encodings_are_correct_problems() -> None:
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
                        <text>Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                    <text-prop name=":hasRichtext">
                        <text encoding="utf8">Text</text>
                        <text>Text</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    test_lookup = TextValuePropertyGUI(formatted_text={":hasRichtext"}, unformatted_text={":hasSimpleText", ":hasText"})
    expected = r"""
Some text encodings used in the data is not conform with the gui-element specified in the ontology\.
Please consult the ontology regarding the assigned gui-elements.

---------------------------------------

Resource ID\: 'resC'
    - Property Name: '\:hasRichtext' -> Encoding\(s\) Used\: 'None, utf8'
----------------------------
Resource ID\: 'test_thing_1'
    - Property Name\: '\:hasText' -> Encoding\(s\) Used\: 'xml'"""
    with pytest.raises(InputError, match=expected):
        _analyse_if_all_text_value_encodings_are_correct(test_ele, test_lookup)
