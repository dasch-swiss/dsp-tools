import pytest
import regex
from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.xml_validation import _find_all_text_props_with_multiple_encodings
from dsp_tools.utils.xml_validation import _find_xml_tags_in_simple_text_elements
from dsp_tools.utils.xml_validation import _get_all_ids_and_encodings_from_root
from dsp_tools.utils.xml_validation import _get_encodings_from_one_property
from dsp_tools.utils.xml_validation import _get_encodings_from_one_resource
from dsp_tools.utils.xml_validation import check_if_only_one_encoding_is_used_per_prop_in_root
from dsp_tools.utils.xml_validation_models import TextValueData


class TestFindXMLTagsInUTF8:
    def test_find_xml_tags_in_simple_text_elements_all_good(self, recwarn: pytest.WarningsRecorder) -> None:
        allowed_html_escapes = [
            "(&lt;2cm) (&gt;10cm)",
            "text &lt; text/&gt;",
            "text &lt; text&gt; &amp; text",
            "text &lt;text text &gt; text",
            'text &lt; text text="text"&gt; text',
            'text &lt;text text="text" &gt; text',
        ]
        utf8_texts_with_allowed_html_escapes = [
            f"""
            <knora shortcode="4123" default-ontology="testonto">
                <resource label="label" restype=":restype" id="id">
                    <text-prop name=":name">
                        <text encoding="utf8">{txt}</text>
                    </text-prop>
                </resource>
            </knora>
            """
            for txt in allowed_html_escapes
        ]
        for xml in utf8_texts_with_allowed_html_escapes:
            _find_xml_tags_in_simple_text_elements(etree.fromstring(xml))
        assert len(recwarn) == 0

    def test_find_xml_tags_in_simple_text_elements_forbidden_escapes(self) -> None:
        test_ele = etree.fromstring(
            """
            <knora shortcode="4123" default-ontology="testonto">
                <resource label="label" restype=":restype" id="id">
                    <text-prop name=":name">
                        <text encoding="utf8">&lt;tag s="t"&gt;</text>
                    </text-prop>
                </resource>
            </knora>
            """
        )
        expected_msg = regex.escape(
            "Angular brackets in the format of <text> were found in text properties with encoding=utf8.\n"
            "Please note that these will not be recognised as formatting in the text field, "
            "but will be displayed as-is.\n"
            "The following resources of your XML file contain angular brackets:\n"
            "    - line 5: resource 'id', property ':name'"
        )
        with pytest.warns(DspToolsUserWarning, match=expected_msg):
            _find_xml_tags_in_simple_text_elements(test_ele)

    def test_find_xml_tags_in_simple_text_elements_forbidden_escapes_two(self) -> None:
        test_ele = etree.fromstring(
            """
            <knora shortcode="4123" default-ontology="testonto">
                <resource label="label" restype=":restype" id="id">
                    <text-prop name=":propName">
                        <text encoding="utf8">&lt;em&gt;text&lt;/em&gt;</text>
                    </text-prop>
                </resource>
            </knora>
            """
        )
        expected_msg = regex.escape(
            "Angular brackets in the format of <text> were found in text properties with encoding=utf8.\n"
            "Please note that these will not be recognised as formatting in the text field, "
            "but will be displayed as-is.\n"
            "The following resources of your XML file contain angular brackets:\n"
            "    - line 5: resource 'id', property ':propName'"
        )

        with pytest.warns(DspToolsUserWarning, match=expected_msg):
            _find_xml_tags_in_simple_text_elements(test_ele)


def test_find_all_text_props_with_multiple_encodings_problems() -> None:
    test_props = [TextValueData("problem_id", "problem_prop", {"xml", "utf8"}), TextValueData("", "", {"utf8"})]
    problem = _find_all_text_props_with_multiple_encodings(test_props)[0]
    assert problem.resource_id == "problem_id"
    assert problem.property_name == "problem_prop"
    assert problem.encoding == {"xml", "utf8"}


def test_find_all_text_props_with_multiple_encodings_good() -> None:
    test_props = [TextValueData("", "", {"xml"}), TextValueData("", "", {"utf8"})]
    problem = _find_all_text_props_with_multiple_encodings(test_props)
    assert not problem


def test_get_all_ids_prop_encoding_from_root_no_text() -> None:
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
    res = _get_all_ids_and_encodings_from_root(test_ele)
    assert not res


def test_get_all_ids_prop_encoding_from_root_with_text() -> None:
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
                <resource label="resD" restype=":TestThing2" id="resD" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    res = _get_all_ids_and_encodings_from_root(test_ele)
    assert res[0].resource_id == "test_thing_1"
    assert res[0].property_name == ":hasRichtext"
    assert res[0].encoding == {"xml"}
    assert res[1].resource_id == "resB"
    assert res[1].property_name == ":hasSimpleText"
    assert res[1].encoding == {"utf8"}
    assert res[2].resource_id == "resC"
    assert res[2].property_name == ":hasSimpleText"
    assert res[2].encoding == {"utf8"}


class TestGetEncodingsOneResource:
    def test_no_text(self) -> None:
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
        res = _get_encodings_from_one_resource(test_props)
        assert not res

    def test_one_text_prop(self) -> None:
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
        res = _get_encodings_from_one_resource(test_props)[0]
        assert res.resource_id == "test_thing_1"
        assert res.property_name == ":hasRichtext"
        assert res.encoding == {"utf8"}

    def test_two_text_prop(self) -> None:
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
                    <text encoding="utf8">Text</text>
                </text-prop>
            </resource>
            """
        )
        res = _get_encodings_from_one_resource(test_props)
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
                <text encoding="xml" permissions="open">
                    This text contains links to all resources:
                    <a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>
                </text>
                <text encoding="xml">Text with an external link: <a href="https://www.google.com/">Google</a></text>
            </text-prop>
            """
        )
        res_info = _get_encodings_from_one_property("id", test_prop)
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
        res_info = _get_encodings_from_one_property("id", test_prop)
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
        res_info = _get_encodings_from_one_property("id", test_prop)
        assert res_info.resource_id == "id"
        assert res_info.property_name == ":hasRichtext"
        assert res_info.encoding == {"utf8"}


def test_check_if_only_one_encoding_is_used_in_xml_good() -> None:
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
                        <text encoding="utf8">Text 1</text>
                        <text encoding="utf8">Text 2</text>
                    </text-prop>
                </resource>
                <resource label="resD" restype=":TestThing2" id="resD" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    res = check_if_only_one_encoding_is_used_per_prop_in_root(test_ele)
    assert not res


def test_check_if_only_one_encoding_is_used_in_xml_problem() -> None:
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
                        <text encoding="utf8">Text 1</text>
                        <text encoding="xml">Text 2</text>
                    </text-prop>
                </resource>
                <resource label="resD" restype=":TestThing2" id="resD" permissions="open">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="open">resB</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    res = check_if_only_one_encoding_is_used_per_prop_in_root(test_ele)[0]
    assert res.resource_id == "resC"
    assert res.property_name == ":hasSimpleText"
    assert res.encoding == {"xml", "utf8"}


if __name__ == "__main__":
    pytest.main([__file__])
