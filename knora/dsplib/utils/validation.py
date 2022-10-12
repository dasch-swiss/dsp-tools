import regex

from knora.dsplib.models.helpers import BaseError


def validate_resource_creation_date(creation_date: str, err_msg: str) -> None:
    """
    Checks if creation_date is a valid https://www.w3.org/TR/xmlschema11-2/#dateTimeStamp.

    Args:
        creation_date: the attribute "creation_date" from the <resource> tag in the XML

    Returns:
        None if validation passes. Raises a BaseError if validation fails.
    """
    _regex = r"-?([1-9][0-9]{3,}|0[0-9]{3})" \
             r"-(0[1-9]|1[0-2])" \
             r"-(0[1-9]|[12][0-9]|3[01])" \
             r"T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?|(24:00:00(\.0+)?))" \
             r"(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))"
    if not regex.search(_regex, creation_date):
        raise BaseError(err_msg)
