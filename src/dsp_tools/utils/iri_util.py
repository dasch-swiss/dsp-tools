import regex

_iri_pattern = r"https?://rdfh.ch/[a-fA-F0-9]{4}/[\w-]{22}"


def is_iri(s: str) -> bool:
    """Checks whether a string is a valid IRI."""
    return regex.fullmatch(_iri_pattern, s) is not None
