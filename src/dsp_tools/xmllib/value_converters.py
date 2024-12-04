from typing import Any

from dsp_tools.xmllib.models.config_options import NewlineReplacement


def convert_to_bool_string(value: Any) -> str:
    """
    Turns a value into a bool string, suitable for an XML.
    It is case-insensitive, meaning that the words can also be capitalised.

    Accepted values:
         - `false`, `0`, `0.0`, `no`, `non`, `nein` -> `false`
         - `true`, `1`, `1.0`, `yes`, `oui`, `ja` -> `true`

    Args:
        value: value to transform

    Returns:
        `"true"` or `"false"` if it is an accepted value,
        else it returns the original value as a string.

    Examples:
        ```python
        result = xmllib.convert_to_bool_string(1)
        # result = "true"
        ```

        ```python
        result = xmllib.convert_to_bool_string("nein")
        # result = "false"
        ```
    """
    str_val = str(value).lower().strip()
    if str_val in ("false", "0", "0.0", "no", "non", "nein"):
        return "false"
    elif str_val in ("true", "1", "1.0", "yes", "oui", "ja"):
        return "true"
    return str(value)


def replace_newlines_with_tags(text: str, converter_option: NewlineReplacement) -> str:
    """
    Converts the newlines in a string to XML tags.

    Args:
        text: string to convert
        converter_option: specifies what tag to use instead of the newline

    Returns:
        String with replaced values

    Raises:
        InputError: If an invalid conversion option is given

        Examples:
            ```python
            result = xmllib.replace_newlines_with_tags("Start\\nEnd", xmllib.NewlineReplacement.NONE)
            # result = "Start\\nEnd"
            ```

            ```python
            result = xmllib.replace_newlines_with_tags("Start\\nEnd", xmllib.NewlineReplacement.LINEBREAK)
            # result = "Start<br/>End"
            ```

            ```python
            result = xmllib.replace_newlines_with_tags("Start\\n\\nEnd", xmllib.NewlineReplacement.PARAGRAPH)
            # result = "<p>Start</p><p>End</p>"
            ```
    """
    match converter_option:
        case NewlineReplacement.NONE:
            return text
        case NewlineReplacement.LINEBREAK:
            return replace_newlines_with_br_tags(text)
        case NewlineReplacement.PARAGRAPH:
            return replace_newlines_with_paragraph_tags(text)


def replace_newlines_with_paragraph_tags(text: str) -> str:
    """
    Replace `Start\\nEnd` with `<p>Start</p><p>End</p>`

    Args:
        text: string to be formatted

    Returns:
        Formatted string with paragraph tags

    Examples:
        ```python
        result = xmllib.replace_newlines_with_paragraph_tags("Start\\n\\nEnd")
        # result = "<p>Start</p><p>End</p>"
        ```

        ```python
        # Multiple consecutive newlines will be treated as one newline
        result = xmllib.replace_newlines_with_paragraph_tags("Start\\n\\nEnd")
        # result = "<p>Start</p><p>End</p>"
        ```
    """
    splt = [x for x in text.split("\n") if x != ""]
    formatted = [f"<p>{x}</p>" for x in splt]
    return "".join(formatted)


def replace_newlines_with_br_tags(text: str) -> str:
    """
    Replaces `\\n` with `<br/>`

    Args:
        text: string to be formatted

    Returns:
        Formatted string with break-line tags

    Examples:
        ```python
        result = xmllib.replace_newlines_with_br_tags("Start\\nEnd")
        # result = "Start<br/>End"
        ```

        ```python
        # Multiple consecutive newlines will be converted into multiple break-lines
        result = xmllib.replace_newlines_with_br_tags("Start\\n\\nEnd")
        # result = "Start<br/><br/>End"
        ```
    """
    return text.replace("\n", "<br/>")
