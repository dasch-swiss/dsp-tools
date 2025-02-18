from __future__ import annotations

from typing import TypeAlias
from typing import Union

from dsp_tools.xmllib import AudioSegmentResource
from dsp_tools.xmllib import LinkResource
from dsp_tools.xmllib import RegionResource
from dsp_tools.xmllib import Resource
from dsp_tools.xmllib import VideoSegmentResource

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

AnyResource: TypeAlias = Union[Resource, RegionResource, LinkResource, VideoSegmentResource, AudioSegmentResource]
