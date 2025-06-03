import regex


def is_prod_like_server(server: str) -> bool:
    return server in [
        "https://api.dasch.swiss",
        "https://api.rdu.dasch.swiss",
        "https://api.ls-prod-server.dasch.swiss",
        "https://api.ls-test-server.dasch.swiss",
        "https://api.stage.dasch.swiss",
    ]


def is_uri(s: str) -> bool:
    """Checks if the given string is a valid URI."""
    # URI = scheme ":" ["//" host [":" port]] path ["?" query] ["#" fragment]
    chars_for_path_query_fragment = r"\w_.\-:~%()!@,;/=*&'+"
    scheme = r"(?<scheme>[a-z][a-z0-9+.\-]*)"
    host = r"(?<host>[\w_.\-:~\[\]]+)"
    port = r"(?<port>:\d{0,6})"
    path = rf"(?<path>/[{chars_for_path_query_fragment}]*)"
    query = rf"(?<query>\?[{chars_for_path_query_fragment}]+)"
    fragment = rf"(?<fragment>#[{chars_for_path_query_fragment}]*)"
    m = regex.match(rf"{scheme}:(//{host}{port}?){path}*{query}*{fragment}?", s, flags=regex.UNICODE)
    return m is not None


def is_iiif_uri(uri: str) -> bool:
    """
    Checks if the given URL is a valid IIIF URL.
    It should support all versions of IIIF servers,
    but was constructed with the syntax described in: https://iiif.io/api/image/3.0/#2-uri-syntax.
    IIIF is open to modifications which are not described in the official documentation
    (see https://iiif.io/api/annex/notes/design_principles/#define-success-not-failure).

    Args:
        uri: The URI to be checked.

    Returns:
        True if the URI is a valid IIIF URI, False otherwise.
    """
    # {scheme}://{server}/{prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
    split_uri = uri.lower().split("/")
    try:
        region_seg, size_seg, rotation_seg, quality_format_seg = split_uri[-4:]
    except ValueError:
        return False
    # %5E is the URL encoded version of ^ ->
    # because we do change the uri to lower case we need to change that in the regex
    # (\d+(\.\d+)?) -> number, can be integer or float
    # everything needs to be encapsulated in a group
    # otherwise the ^ and $ only apply respectively to the first and last listed in the alternative options
    region_re = (
        r"^(full|square|"  # full | square
        r"((pct:)?(\d+(\.\d+)?,){3}(\d+(\.\d+)?)))$"  # x,y,w,h | pct:x,y,w,h
    )
    if not regex.search(region_re, region_seg):
        return False
    size_re = (
        r"^((\^|%5e)?max|"  # max | ^max
        r"(\^|%5e)?full|"  # full | ^full
        r"(\^|%5e)?pct:\d+(\.\d+)?|"  # pct:n | ^pct:n
        r"(\^|%5e)?(\d+(\.\d+)?)+(,|%2c)|"  # w, | ^w,
        r"(\^|%5e)?,\d+(\.\d+)?|"  # ,h | ^,h
        r"(\^|%5e)?!?\d+(\.\d+)?,\d+(\.\d+)?)$"  # w,h | ^w,h | !w,h | ^!w,h
    )
    if not regex.search(size_re, size_seg):
        return False
    # rotation -> floating point number 0-360 -> n | !n (positive and negative are allowed)
    rotation_re = r"^!?[+-]?\d+(\.\d+)?$"
    if not regex.search(rotation_re, rotation_seg):
        return False
    # quality -> color | colour | gray | grey | bitonal | default | native
    # format -> jpg | tif | png | gif | jp2 | pdf | webp
    quality_format_re = r"^(colou?r|gr[ae]y|bitonal|default|native)(\.(jpg|tif|png|jp2|gif|pdf|webp))?$"
    return bool(regex.search(quality_format_re, quality_format_seg))
