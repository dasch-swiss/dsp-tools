from collections.abc import Iterator
from pathlib import Path

import pytest

from dsp_tools.xmllib.models.res import Resource
from dsp_tools.xmllib.models.root import XMLRoot


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
            'Text <footnote content="Text &lt;a href=&quot;https://www.google.com/&quot;&gt;Google&lt;/a&gt;"/>',
            # &quot; is always resolved by the XML parser, but then automatically re-escaped
            # because it is part of an attribute
        ),
        (
            'Text <footnote content="Text &lt;a href=&#34;https://www.google.com/&#34;&gt;Google&lt;/a&gt;" />',
            'Text <footnote content="Text &lt;a href=&quot;https://www.google.com/&quot;&gt;Google&lt;/a&gt;"/>',
            # &#34; is always resolved by the XML parser, but then automatically re-escaped to &quot;
            # because it is part of an attribute
        ),
        (
            "Text &quot; &lt;",
            'Text " &lt;',
            # &quot; is always resolved by the XML parser, if it is part of a text
        ),
        (
            'Text <a href="https://www.google.com/">Google</a>',
            'Text <a href="https://www.google.com/">Google</a>',
        ),
        (
            "Text <p><strong><em>Text</em></strong></p>",
            "Text <p><strong><em>Text</em></strong></p>",
        ),
    ],
)
def test_serialisation_of_tags(richtext: str, expected: str, out_file: Path) -> None:
    root = XMLRoot.create_new("1234", "my_onto")
    res = Resource.create_new("res_id", ":Type", "lbl").add_richtext(":prop", richtext)
    root.add_resource(res).write_file(out_file)
    with open(out_file, encoding="utf-8") as f:
        lines = f.readlines()
    start_index = next(i for i, x in enumerate(lines) if '<text encoding="xml">' in x)
    end_index = next(i for i, x in enumerate(lines) if "</text>" in x)
    lines_purged = [x.strip() for x in lines[start_index : end_index + 1]]
    result = "".join(lines_purged).replace('<text encoding="xml">', "").replace("</text>", "")
    assert result == expected
