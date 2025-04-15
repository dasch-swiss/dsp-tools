from pathlib import Path
from typing import Iterator

import pytest

from dsp_tools.xmllib.models.res import Resource
from dsp_tools.xmllib.models.root import XMLRoot

SHORTCODE = "1234"
DEFAULT_ONTO = "my_onto"
RES_ID = "res_id"

@pytest.fixture
def out_file() -> Iterator[Path]:
    out_file = Path("testdata/xml-data/tmp-serialise_tags.xml")
    yield out_file
    out_file.unlink()


@pytest.mark.parametrize(
    ("richtext", "expected"),
    [
        (
            'Text <footnote content="Text &lt;a href=&quot;https://www.google.com/&quot;&gt;Google&lt;/a&gt;" />', 
            'Text <footnote content="Text &lt;a href=&quot;https://www.google.com/&quot;&gt;Google&lt;/a&gt;" />',
            # here, the problem is that if an elem.text contains &lt; it will be serialised as &ampt;lt;
        ),
        (
            'Text <footnote content="Text &lt;a href=&#34;https://www.google.com/&#34;&gt;Google&lt;/a&gt;" />', 
            'Text <footnote content="Text &lt;a href=&#34;https://www.google.com/&#34;&gt;Google&lt;/a&gt;" />',
        ),
        (
            'Text <a href="https://www.google.com/">Google</a>',
            'Text <a href="https://www.google.com/">Google</a>',
        ),
        (
            '<p><strong>Bold</strong></p>',
            '<p><strong>Bold</strong></p>',
        )
    ],
)
def test_serialisation_of_tags(richtext: str, expected: str, out_file: Path) -> None:
    root = XMLRoot.create_new(SHORTCODE, DEFAULT_ONTO)
    res = Resource.create_new(RES_ID, ":Type", "lbl")
    res.add_richtext(":prop", richtext)
    root.add_resource(res).write_file(out_file)
    with open(out_file, encoding="utf-8") as f:
        lines = f.readlines()
    line = next(x for x in lines if '<text encoding="xml">' in x).strip()
    assert line == f'<text encoding="xml">{expected}</text>'
