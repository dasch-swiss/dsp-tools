"""
The checking of geolocation values against their CRS.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal

import regex

from dsp_tools.utils.geolocation_constants import ALL_CRS
from dsp_tools.utils.geolocation_constants import CRS_BY_CODE
from dsp_tools.utils.geolocation_constants import Crs

# The same form the XML schema admits: a plain decimal, no exponent, no thousands separator.
_DECIMAL_ORDINATE_PATTERN = regex.compile(r"^[+-]?[0-9]+(\.[0-9]+)?$")


def get_geolocation_problem(crs_code: str, ordinates: Mapping[str, str]) -> str | None:
    """
    Check a CRS code and its named ordinates, and describe the first problem found.

    Returns a message rather than a bool because an author needs to know which of several things is wrong:
    an unsupported CRS, ordinates that do not belong to the CRS, a missing ordinate, or one out of range.

    Args:
        crs_code: the CRS code
        ordinates: the ordinates, keyed by their names, e.g. `{"easting": "2600000", "northing": "1200000"}`

    Returns:
        a message naming the problem, or None if the value is valid
    """
    if not (crs := CRS_BY_CODE.get(crs_code)):
        supported = ", ".join(f"'{x.code}'" for x in ALL_CRS)
        return f"Unsupported coordinate reference system '{crs_code}'. Supported are: {supported}."
    if pair_problem := _get_pair_problem(crs, ordinates):
        return pair_problem
    if x_problem := _get_ordinate_problem(crs, crs.x_name, ordinates[crs.x_name], crs.x_min, crs.x_max):
        return x_problem
    return _get_ordinate_problem(crs, crs.y_name, ordinates[crs.y_name], crs.y_min, crs.y_max)


def _get_pair_problem(crs: Crs, ordinates: Mapping[str, str]) -> str | None:
    expected = (crs.x_name, crs.y_name)
    if foreign := [name for name in ordinates if name not in expected]:
        found = " and ".join(f"'{name}'" for name in foreign)
        msg = f"Given crs=\"{crs.code}\", expected the attributes '{crs.x_name}' and '{crs.y_name}'. Found {found}"
        if foreign_kinds := {x.kind for x in ALL_CRS if set(foreign) <= {x.x_name, x.y_name}} - {crs.kind}:
            belong = "belongs" if len(foreign) == 1 else "belong"
            msg += f", which {belong} to a {foreign_kinds.pop()} CRS"
        return msg + "."
    if missing := [name for name in expected if name not in ordinates]:
        missing_str = "both are missing" if len(missing) == 2 else f"'{missing[0]}' is missing"
        return (
            f"Given crs=\"{crs.code}\", expected both '{crs.x_name}' and '{crs.y_name}'. "
            f"{missing_str[0].upper()}{missing_str[1:]}."
        )
    return None


def _get_ordinate_problem(crs: Crs, name: str, ordinate: str, minimum: Decimal, maximum: Decimal) -> str | None:
    if not _DECIMAL_ORDINATE_PATTERN.match(ordinate.strip()):
        return f"The {name} '{ordinate}' is not a decimal number, e.g. '8.55'."
    value = Decimal(ordinate.strip())
    if not minimum <= value <= maximum:
        return f"The {name} '{ordinate}' is outside the valid range for {crs.label}: {minimum} to {maximum} inclusive."
    return None
