# The accepted XML tags are defined at https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/
_COMMON_BASE = [
    "p",
    "em",
    "strong",
    "u",
    "sub",
    "sup",
    "strike",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
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
KNOWN_XML_TAG_REGEXES = [
    *_COMMON_BASE,
    "a( [^>]+?)?",  # <a> has attributes
    "footnote( [^>]+?)?",  # the footnote text is in the attributes
]
KNOWN_XML_TAGS = [
    *_COMMON_BASE,
    "a",
    "footnote",
]
XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"

# These named entities are defined by the XML specification and are always expanded during parsing,
# regardless of parser options.
# Numeric character references (e.g., `&#34;` or `&#x22;`) are also always resolved
PREDEFINED_XML_ENTITIES = ["&amp;", "&lt;", "&gt;", "&quot;", "&apos;"]
