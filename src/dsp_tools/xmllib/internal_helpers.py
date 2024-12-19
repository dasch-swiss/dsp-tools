from __future__ import annotations

import warnings
from typing import Any

from dsp_tools.models.custom_warnings import DspToolsUserInfo
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.values import Richtext
from dsp_tools.xmllib.value_checkers import is_string_like
from dsp_tools.xmllib.value_converters import replace_newlines_with_tags


def create_richtext_with_checks(
    value: str,
    prop_name: str,
    permissions: Permissions,
    comment: str | None,
    newline_replacement: NewlineReplacement,
    res_id: str,
) -> Richtext:
    """
    Creates a RichtextValue with checks and optional conversions

    Args:
        value: richttext value
        prop_name: name of the property
        permissions: permissions of the value
        comment: comment for the value
        newline_replacement: the replacement for the newlines in the string
        res_id: id of the calling resource

    Returns:
        A richtext value

    Raises:
        Input Error if the input is a dictionary
    """
    # Because of the richtext conversions, the input value is cast as a string.
    # Values such as str(`pd.NA`) result in a non-empy string.
    # Therefore, a check must occur before the conversion takes place.
    check_richtext_before_conversion(value, prop_name, res_id)
    value = replace_newlines_with_tags(str(value), newline_replacement)
    return Richtext(value, prop_name, permissions, comment, res_id)


def check_richtext_before_conversion(value: Any, prop_name: str, res_id: str) -> None:
    """
    Checks if the input which is expected to be richtext is a string.

    Args:
        value: Input value
        prop_name: Property name
        res_id: Resource ID
    """
    if not is_string_like(value):
        msg = f"Resource '{res_id}' has a richtext value that is not a string: Value: {value} | Property: {prop_name}"
        warnings.warn(DspToolsUserWarning(msg))


def check_and_fix_collection_input(value: Any, prop_name: str, res_id: str) -> list[Any]:
    """
    To allow varied input but ensure consistent typing internally, collections are converted.
    As collections are expected to be non-empty a warning is emitted for the user.

    Args:
        value: Input value
        prop_name: Property name
        res_id: Resource ID

    Returns:
        The input as a list

    Raises:
        InputError: if the input is a dictionary
    """
    msg = f"The input value of the resource with the ID '{res_id}' and the property '{prop_name}' "
    match value:
        case set() | list() | tuple():
            if len(value) == 0:
                msg += "is empty. Please note that no values will be added to the resource."
                warnings.warn(DspToolsUserInfo(msg))
            return list(value)
        case dict():
            msg += "is a dictionary. Only collections (list, set, tuple) are permissible."
            raise InputError(msg)
        case _:
            return [value]
