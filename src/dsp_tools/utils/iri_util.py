import regex

_resource_iri_pattern = r"https?://rdfh.ch/[a-fA-F0-9]{4}/[\w-]{22}"


def is_resource_iri(s: str) -> bool:
    """Checks whether a string is a valid resource IRI."""
    return regex.fullmatch(_resource_iri_pattern, s) is not None
