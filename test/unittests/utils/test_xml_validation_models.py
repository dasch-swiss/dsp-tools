import pandas as pd
import pytest
from lxml import etree
from pandas.testing import assert_frame_equal

from dsp_tools.utils.xml_validation_models import (
    InconsistentTextValueEncodings,
    TextValueData,
    _check_only_one_valid_encoding_used_all_props,
    _get_all_ids_prop_encoding_from_root,
    _get_id_prop_encoding_from_one_resource,
    _get_prop_encoding_from_one_property,
    check_if_only_one_encoding_is_used_in_xml,
)


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
    assert not res


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
    res = _get_id_prop_encoding_from_one_resource(test_props)[0]
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
                <text encoding="utf8">Text</text>
                <text encoding="utf8">Text</text>
            </text-prop>
        </resource>
        """
    )
    res = _get_id_prop_encoding_from_one_resource(test_props)
    assert res[0].resource_id == "test_thing_1"
    assert res[0].property_name == ":hasRichtext"
    assert res[0].encoding == {"xml"}
    assert res[1].resource_id == "test_thing_1"
    assert res[1].property_name == ":hasSimpleText"
    assert res[1].encoding == {"utf8"}


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
                <text encoding="utf8">Text</text>
            </text-prop>
            """
        )
        res_info = _get_prop_encoding_from_one_property("id", test_prop)
        assert res_info.resource_id == "id"
        assert res_info.property_name == ":hasRichtext"
        assert res_info.encoding == {"utf8"}

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
    assert not res


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
    assert res[0].encoding == {"xml"}
    assert res[1].resource_id == "resB"
    assert res[1].property_name == ":hasSimpleText"
    assert res[1].encoding == {"utf8"}
    assert res[2].resource_id == "resC"
    assert res[2].property_name == ":hasSimpleText"
    assert res[2].encoding == {"utf8"}


def test_check_only_one_valid_encoding_used_all_props_problems() -> None:
    test_props = [TextValueData("problem_id", "problem_prop", {"xml", "utf8"}), TextValueData("", "", {"utf8"})]
    problem = _check_only_one_valid_encoding_used_all_props(test_props)[0]
    assert problem.resource_id == "problem_id"
    assert problem.property_name == "problem_prop"
    assert problem.encoding == {"xml", "utf8"}


def test_check_if_only_one_encoding_is_used_in_xml_good() -> None:
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
                        <text encoding="utf8">Text 1</text>
                        <text encoding="utf8">Text 2</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    res = check_if_only_one_encoding_is_used_in_xml(test_ele)
    assert not res


def test_check_if_only_one_encoding_is_used_in_xml_problem() -> None:
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
                        <text encoding="utf8">Text 1</text>
                        <text encoding="xml">Text 2</text>
                    </text-prop>
                </resource>
                <resource label="resC" restype=":TestThing2" id="resD" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    res = check_if_only_one_encoding_is_used_in_xml(test_ele)[0]
    assert res.resource_id == "resC"
    assert res.property_name == ":hasSimpleText"
    assert res.encoding == {"xml", "utf8"}


class TestInvalidTextValueEncodings:
    def test_get_problems_as_df(self) -> None:
        problems = InconsistentTextValueEncodings(
            [
                TextValueData("id1", ":simple", {"utf8", "xml"}),
                TextValueData("id1", ":rich", {"utf8", "xml"}),
                TextValueData("id2", ":rich", {"utf8", "xml"}),
            ]
        )
        expected_df = pd.DataFrame(
            {
                "Resource ID": ["id1", "id1", "id2"],
                "Property Name": [":rich", ":simple", ":rich"],
            }
        )
        res_df = problems._get_problems_as_df()
        assert_frame_equal(res_df, expected_df)

    def test_make_msg_for_one_resource(self) -> None:
        test_df = pd.DataFrame(
            {
                "Resource ID": ["id1", "id1"],
                "Property Name": [":rich", ":simple"],
            }
        )
        res = InconsistentTextValueEncodings._make_msg_for_one_resource("id1", test_df)
        expected = "Resource ID: 'id1'\n" "    - Property Name: ':rich'\n" "    - Property Name: ':simple'"
        assert res == expected

    def test_make_msg_from_df(self) -> None:
        test_df = pd.DataFrame(
            {
                "Resource ID": ["id1", "id1", "id2", "id3"],
                "Property Name": [":rich", ":simple", ":rich", ":mixed"],
            }
        )
        res = InconsistentTextValueEncodings._make_msg_from_df(test_df)
        expected = (
            "Resource ID: 'id1'\n"
            "    - Property Name: ':rich'\n"
            "    - Property Name: ':simple'"
            "\n----------------------------\n"
            "Resource ID: 'id2'\n"
            "    - Property Name: ':rich'"
            "\n----------------------------\n"
            "Resource ID: 'id3'\n"
            "    - Property Name: ':mixed'"
        )
        assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
