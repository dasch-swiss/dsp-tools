import regex


def is_uri(s: str) -> bool:
    """Checks if the given string is a valid URI."""
    # URI = scheme ":" ["//" host [":" port]] path ["?" query] ["#" fragment]
    scheme = r"(?<scheme>[a-z][a-z0-9+.\-]*)"
    host = r"(?<host>[\w_.\-~:\[\]]+)"
    port = r"(?<port>:\d{0,6})"
    path = r"(?<path>/[\w_.\-~:%()]*)"
    query = r"(?<query>\?[\w_.,\-:%=*&]+)"
    fragment = r"(?<fragment>#[\w_.\-~:/]*)"
    m = regex.match(rf"{scheme}:(//{host}{port}?){path}*{query}*{fragment}?", s, flags=regex.UNICODE)
    return m is not None
