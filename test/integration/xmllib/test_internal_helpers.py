from pathlib import Path

from dsp_tools.xmllib.models.res import Resource
from dsp_tools.xmllib.models.root import XMLRoot

SHORTCODE = "1234"
DEFAULT_ONTO = "my_onto"
RES_ID = "res_id"
OUT_FILE = Path("testdata/xml-data/serialise_tags.xml")


def test_serialisation_of_tags() -> None:
    url = "https://www.google.com/"
    expected = f'<text encoding="xml">Text<footnote content="Text &lt;a href=&#34;{url}&#34;&gt;Google&lt;/a&gt;" /></text>\n'
    root = XMLRoot.create_new(SHORTCODE, DEFAULT_ONTO)
    res = Resource.create_new(RES_ID, ":Type", "lbl")
    res.add_richtext(":prop", f'Text <footnote content="Text &lt;a href=&quot;{url}&quot;&gt;URL&lt;/a&gt;" />')
    root.add_resource(res).write_file(OUT_FILE)
    with open(OUT_FILE, encoding="utf-8") as f:
        lines = f.readlines()
    line = next(x for x in lines if url in x)
    print(line)
