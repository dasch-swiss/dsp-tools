from __future__ import annotations

import warnings
from typing import Any

from dsp_tools.models.custom_warnings import DspToolsUserInfo
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib import is_string_like


def check_richtext_before_conversion(value: Any, res_id: str, prop_name: str) -> None:
    """
    Checks if the input which is expected to be richtext is a string.

    Args:
        value: Input value
        res_id: Resource ID
        prop_name: Property name
    """
    if not is_string_like(value):
        msg = f"Resource '{res_id}' has a richtext value that is not a string: Value: {value} | Property: {prop_name}"
        warnings.warn(DspToolsUserWarning(msg))


def check_and_fix_collection_input(value: Any, res_id: str, prop_name: str) -> list[Any]:
    """
    To allow varied input but ensure consistent typing internally, collections are converted.
    As collections are expected to be non-empty a warning is emitted for the user.

    Args:
        value: Input value
        res_id: Resource ID
        prop_name: Property name

    Returns:
        The input as a list

    Raises:
        Input Error if the input is a dictionary
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
