from dataclasses import dataclass
from typing import Optional, Union

# pylint: disable=line-too-long


@dataclass(frozen=True)
class PropertyElement:
    """
    A PropertyElement object carries more information about a property value than the value itself.
    The "value" is the value that could be passed to a method as plain string/int/float/bool. Use a PropertyElement
    instead to define more precisely what attributes your value tag (e.g. <text>, <uri>, ...) will have.

    Args:
        value: This is the content that will be written into the value tag (e.g. <text>, <uri>, ...)
        permissions: This is the permissions that your <text> tag (for example) will have
        comment: This is the comment that your <text> tag (for example) will have

    Examples:
        See the difference between the first and the second example:

        >>> make_unformatted_text_prop(":testproperty", "first text")
                <unformatted-text-prop name=":testproperty">
                    <text permissions="prop-default">
                        first text
                    </text>
                </unformatted-text-prop>
        >>> make_unformatted_text_prop(":testproperty", PropertyElement("first text", permissions="prop-restricted"))
                <unformatted-text-prop name=":testproperty">
                    <text permissions="prop-restricted">
                        first text
                    </text>
                </unformatted-text-prop>
    """

    value: Union[str, int, float, bool]
    permissions: str = "prop-default"
    comment: Optional[str] = None
