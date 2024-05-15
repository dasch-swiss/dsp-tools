import regex


def is_uri(s: str) -> bool:
    """Checks if the given string is a valid URI."""
    # URI = scheme ":" ["//" host [":" port]] path ["?" query] ["#" fragment]
    scheme = r"(?<scheme>[a-z][a-z0-9+.\-]*)"
    host = r"(?<host>[\w_.\-~:\[\]]+)"
    port = r"(?<port>:\d{0,6})"
    path = r"(?<path>/[\w_.\-~:%()]*)"
    query = r"(?<query>\?[\w_.,;/\-:%=*&]+)"
    fragment = r"(?<fragment>#[\w_.\-~:/]*)"
    m = regex.match(rf"{scheme}:(//{host}{port}?){path}*{query}*{fragment}?", s, flags=regex.UNICODE)
    return m is not None


def is_iiif_uri(uri: str) -> bool:
    """
    Checks if the given URL is a valid IIIF URL.
    It should support all versions of IIIF servers,
    but was constructed with the syntax described in: https://iiif.io/api/image/3.0/#2-uri-syntax
    IIIF is open to modifications which are not described in the official documentation.
    https://iiif.io/api/annex/notes/design_principles/#define-success-not-failure
    This may need to be updated in case of a valid version which is not in the regex.

    Args:
        uri: The URI to be checked.

    Returns:
        True if the URI is a valid IIIF URI, False otherwise.
    """
    split_uri = uri.split("/")
    if len(split_uri) < 5:
        return False
    # {scheme}://{server}{/prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
    region_ex = (
        r"^(full)|(square)|([0-9]+,[0-9]+,[0-9]+,[0-9]+)|"
        r"(pct:[0-9]*\.?[0-9]*,[0-9]*\.?[0-9]*,[0-9]*\.?[0-9]*,[0-9]*\.?[0-9]*)$"
    )
    if not regex.search(region_ex, split_uri[-4]):
        return False
    size_ex = r"^(\^?max)|(\^?pct:[0-9]*\.?[0-9]*)|(\^?[0-9]*,)|(\^?,[0-9]*)|(\^?!?[0-9]*,[0-9]*)$"
    if not regex.search(size_ex, split_uri[-3]):
        return False
    rotation_ex = r"^[-+]?[0-9]*\.?[0-9]+$|^![-+]?[0-9]*\.?[0-9]+$"
    if not regex.search(rotation_ex, split_uri[-2]):
        return False
    quality_format_ex = r"^(color|gray|bitonal|default)\.(jpg|tif|png|jp2|gif|pdf|webp)?$"
    if not regex.search(quality_format_ex, split_uri[-1]):
        return False
    return True
