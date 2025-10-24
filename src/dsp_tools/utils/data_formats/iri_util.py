import regex

_iri_pattern = r"^(http)s?://[\w\.\-~]*(:\d{,6})?(/[\w\-~]+)*(#[\w\-~]*)?"
_resource_iri_pattern = r"https?://rdfh.ch/[a-fA-F0-9]{4}/[\w-]{22}"


def is_iri(s: str) -> bool:
    """Checks whether a string is a valid IRI."""
    return regex.fullmatch(_iri_pattern, s) is not None


def is_resource_iri(s: str) -> bool:
    """Checks whether a string is a valid resource IRI."""
    return regex.fullmatch(_resource_iri_pattern, s) is not None


def from_dsp_iri_to_prefixed_iri(iri: str) -> str:
    dsp_iri_re = r".+\/(.+?)\/v2#(.+)$"
    if not (found := regex.search(dsp_iri_re, iri)):
        return iri
    return f"{found.group(1)}:{found.group(2)}"
