KNOWN_XML_TAGS = [  # defined at https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/
    "a( [^>]+)?",  # <a> has attributes
    "footnote( [^>]+)?",  # the footnote text is in the attributes
    "p",
    "em",
    "strong",
    "u",
    "sub",
    "sup",
    "strike",
    "h1",
    "ol",
    "ul",
    "li",
    "tbody",
    "table",
    "tr",
    "td",
    "br",
    "hr",
    "pre",
    "cite",
    "blockquote",
    "code",
]
XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"
