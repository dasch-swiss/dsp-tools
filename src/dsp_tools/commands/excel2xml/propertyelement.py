from dataclasses import dataclass
from typing import Optional
from typing import Union

from dsp_tools.models.exceptions import BaseError

# ruff: noqa: E501 (line-too-long)


@dataclass(frozen=True)
class PropertyElement:
    """
    A PropertyElement object carries more information about a property value than the value itself.
    The "value" is the value that could be passed to a method as plain string/int/float/bool. Use a PropertyElement
    instead to define more precisely what attributes your value tag (e.g. `<text>`, `<uri>`, ...) will have.

    Args:
        value: This is the content that will be written into the value tag (e.g. `<text>`, `<uri>`, ...)
        permissions: This is the permissions that your `<text>` tag (for example) will have
        comment: This is the comment that your `<text>` tag (for example) will have
        encoding: For `<text>` tags only. If provided, it must be "xml" or "utf8".

    Examples:
        See the difference between the first and the second example:

        >>> excel2xml.make_text_prop(":testproperty", "first text")
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="open">
                        first text
                    </text>
                </text-prop>
        >>> excel2xml.make_text_prop(":testproperty", excel2xml.PropertyElement("first text", permissions="restricted", encoding="xml"))
                <text-prop name=":testproperty">
                    <text encoding="xml" permissions="restricted">
                        first text
                    </text>
                </text-prop>
    """

    value: Union[str, int, float, bool]
    permissions: str = "open"
    comment: Optional[str] = None
    encoding: Optional[str] = None

    def __post_init__(self) -> None:
        if self.encoding not in ["utf8", "xml", None]:
            raise BaseError(f"'{self.encoding}' is not a valid encoding for a PropertyElement")
