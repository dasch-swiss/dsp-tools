from typing import Any

from dsp_tools.xmllib.internal.internal_helpers import check_and_warn_if_a_string_contains_a_potentially_empty_value
from dsp_tools.xmllib.internal.internal_helpers import is_nonempty_value_internal


def check_and_get_corrected_comment(comment: Any, res_id: str, prop_name: str | None) -> str | None:
    """The input of comments may also be pd.NA or such. In our models we only want a string or None."""
    if is_nonempty_value_internal(comment):
        check_and_warn_if_a_string_contains_a_potentially_empty_value(
            value=comment,
            res_id=res_id,
            prop_name=prop_name,
            field="comment on value",
        )
        return str(comment)
    return None
