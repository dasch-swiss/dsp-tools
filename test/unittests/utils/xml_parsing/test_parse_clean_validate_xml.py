import pytest
import regex
from lxml import etree

from dsp_tools.error.custom_warnings import DspToolsUserInfo
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _warn_user_about_tags_in_simpletext


def test_warn_user_about_tags_in_simpletext_all_good(recwarn: pytest.WarningsRecorder) -> None:
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
        _warn_user_about_tags_in_simpletext(etree.fromstring(xml))
    assert len(recwarn) == 0


def test_warn_user_about_tags_in_simpletext_forbidden_escapes() -> None:
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
    with pytest.warns(DspToolsUserInfo, match=expected_msg):
        _warn_user_about_tags_in_simpletext(test_ele)


def test_warn_user_about_tags_in_simpletext_forbidden_escapes_two() -> None:
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

    with pytest.warns(DspToolsUserInfo, match=expected_msg):
        _warn_user_about_tags_in_simpletext(test_ele)


if __name__ == "__main__":
    pytest.main([__file__])
