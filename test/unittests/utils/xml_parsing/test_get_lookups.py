# mypy: disable-error-code="no-untyped-def"

from lxml import etree

from dsp_tools.utils.xml_parsing.get_lookups import get_authorship_lookup


def test_get_authorship_lookup():
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
    result = get_authorship_lookup(root)
    assert set(result.keys()) == set(expected.keys())
    for k, v in result.items():
        assert set(v) == set(expected[k])


def test_extract_authorships_from_xml_no_authors():
    root = etree.fromstring("<knora></knora>")
    result = get_authorship_lookup(root)
    assert result == {}
