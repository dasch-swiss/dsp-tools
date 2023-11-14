from __future__ import annotations

from dataclasses import dataclass

import regex

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.models.exceptions import BaseError


def is_uri(s: str) -> bool:
    """Checks if the given string is a valid URI."""
    # URI = scheme ":" ["//" host [":" port]] path ["?" query] ["#" fragment]
    scheme = r"(?<scheme>[a-z][a-z0-9+.\-]*)"
    host = r"(?<host>[\w_.\-~:\[\]]+)"
    port = r"(?<port>:\d{0,6})"
    path = r"(?<path>/[\w_.\-~:%()]*)"
    query = r"(?<query>\?[\w_.\-:%=*&]+)"
    fragment = r"(?<fragment>#[\w_.\-~:/]*)"
    m = regex.match(rf"{scheme}:(//{host}{port}?){path}*{query}*{fragment}?", s, flags=regex.UNICODE)
    return m is not None


@dataclass
class FormattedTextValue:
    """Represents a formatted text value with standoard standoff markup"""

    xmlstr: str

    def as_xml(self) -> str:
        """Returns the formatted text value as XML (with XML declaration and wrapped in a <text> element)"""
        return f'<?xml version="1.0" encoding="UTF-8"?>\n<text>{self.xmlstr}</text>'

    def find_internal_ids(self) -> set[str]:
        """Returns a set of all internal ids found in the text value"""
        return set(regex.findall(pattern='href="IRI:(.*?):IRI"', string=self.xmlstr))

    def with_iris(self, iri_resolver: IriResolver) -> FormattedTextValue:
        """
        Returns a copy of this object, where all internal ids are replaced with iris according to the provided mapping.
        """
        s = self.xmlstr
        for internal_id in self.find_internal_ids():
            iri = iri_resolver.get(internal_id)
            if not iri:
                raise BaseError(f"Internal ID {internal_id} could not be resolved to an IRI")
            s = s.replace(f'href="IRI:{internal_id}:IRI"', f'href="{iri}"')
        return FormattedTextValue(s)
