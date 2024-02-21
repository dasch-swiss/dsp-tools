from lxml import etree

from dsp_tools.utils.xml_validation import _find_xml_tags_in_simple_text_elements


class TestFindXMLTagsInUTF8:
    def test_find_xml_tags_in_simple_text_elements_all_good(self) -> None:
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
            all_good, msg = _find_xml_tags_in_simple_text_elements(etree.fromstring(xml))
            assert all_good is True
            assert msg == ""

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
        expected_msg = (
            "XML-tags are not allowed in text properties with encoding=utf8.\n"
            "The following resources of your XML file violate this rule:\n"
            "    - line 5: resource 'id', property ':name'"
        )
        all_good, res_msg = _find_xml_tags_in_simple_text_elements(test_ele)
        assert all_good is False
        assert res_msg == expected_msg

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
        expected_msg = (
            "XML-tags are not allowed in text properties with encoding=utf8.\n"
            "The following resources of your XML file violate this rule:\n"
            "    - line 5: resource 'id', property ':propName'"
        )
        all_good, res_msg = _find_xml_tags_in_simple_text_elements(test_ele)
        assert all_good is False
        assert res_msg == expected_msg
