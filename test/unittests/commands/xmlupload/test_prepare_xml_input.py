# mypy: disable-error-code="no-untyped-def"

from lxml import etree

from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import _extract_authorships_from_xml


def test_extract_authorships_from_xml_with_authors():
    root_str = """
    <knora>
        <authorship id="authorship_1">
            <author>
            Lukas 
            Rosenthaler </author>
        </authorship>
        <authorship id="authorship_2">
            <author>\tNora Ammann
            </author>
        </authorship>
        <authorship id="authorship_3">
            <author>Nora    Ammann</author>
            <author>Johannes Nussbaum</author>
        </authorship>
    </knora>
    """
    root = etree.fromstring(root_str)
    expected = {
        "authorship_1": ["Lukas Rosenthaler"],
        "authorship_2": ["Nora Ammann"],
        "authorship_3": ["Nora Ammann", "Johannes Nussbaum"],
    }
    result = _extract_authorships_from_xml(root)
    assert set(result.keys()) == set(expected.keys())
    for k, v in result.items():
        assert set(v) == set(expected[k])


def test_extract_authorships_from_xml_no_authors():
    root = etree.fromstring("<knora></knora>")
    result = _extract_authorships_from_xml(root)
    assert result == {}
