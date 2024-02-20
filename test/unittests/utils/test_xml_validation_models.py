import pytest
from lxml import etree

from dsp_tools.utils.xml_validation_models import (
    TextValueData,
    _check_only_one_valid_encoding_used_all_props,
    _check_only_one_valid_encoding_used_one_prop,
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
                <text encoding="utf8">Text</text>
                <text encoding="utf8">Text</text>
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
    assert res[0].encoding == {"xml"}
    assert res[1].resource_id == "resB"
    assert res[1].property_name == ":hasSimpleText"
    assert res[1].encoding == {"utf8"}
    assert res[2].resource_id == "resC"
    assert res[2].property_name == ":hasSimpleText"
    assert res[2].encoding == {"utf8"}


class TestCheckOnlyOneEncodingUsed:
    def test_utf8(self) -> None:
        assert _check_only_one_valid_encoding_used_one_prop({"utf8"}) is True

    def test_xml(self) -> None:
        assert _check_only_one_valid_encoding_used_one_prop({"utf8"}) is True

    def test_utf8_xml(self) -> None:
        assert _check_only_one_valid_encoding_used_one_prop({"utf8", "xml"}) is False

    def test_other(self) -> None:
        assert _check_only_one_valid_encoding_used_one_prop({"asdfasdf"}) is False


def test_check_only_one_valid_encoding_used_all_props_all_good() -> None:
    test_props = [TextValueData("", "", {"xml"}), TextValueData("", "", {"utf8"})]
    assert _check_only_one_valid_encoding_used_all_props(test_props) is None


def test_check_only_one_valid_encoding_used_all_props_problems() -> None:
    test_props = [TextValueData("problem_id", "problem_prop", {"xml", "utf8"}), TextValueData("", "", {"utf8"})]
    problems: list[TextValueData] = _check_only_one_valid_encoding_used_all_props(test_props)  # type: ignore[assignment]
    assert problems[0].resource_id == "problem_id"
    assert problems[0].property_name == "problem_prop"
    assert problems[0].encoding == {"xml", "utf8"}


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
    all_good, res = check_if_only_one_encoding_is_used_in_xml(test_ele)
    assert all_good is True
    assert res is None


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
    all_good, res = check_if_only_one_encoding_is_used_in_xml(test_ele)
    result: list[TextValueData] = res  # type: ignore[assignment]
    assert all_good is False
    assert result[0].resource_id == "resC"
    assert result[0].property_name == ":hasSimpleText"
    assert result[0].encoding == {"xml", "utf8"}


if __name__ == "__main__":
    pytest.main([__file__])
