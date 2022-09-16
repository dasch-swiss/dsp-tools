import dataclasses
from typing import Union, Optional
import pandas as pd
import regex
from knora.dsplib.models.helpers import BaseError


@dataclasses.dataclass(frozen=True)
class PropertyElement:
    """
    A PropertyElement object carries more information about a property value than the value itself.
    The "value" is the value that could be passed to a method as plain string/int/float/bool. Use a PropertyElement
    instead to define more precisely what attributes your <text> tag (for example) will have.

    Args:
        value: This is the content that will be written between the <text></text> tags (for example)
        permissions: This is the permissions that your <text> tag (for example) will have
        comment: This is the comment that your <text> tag (for example) will have
        encoding: For <text> tags only. Can be "xml" or "utf8".

    Examples:
        See the difference between the first and the second example:

        >>> make_text_prop(":testproperty", "first text")
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="prop-default">
                        first text
                    </text>
                </text-prop>
        >>> make_text_prop(":testproperty", PropertyElement("first text", permissions="prop-restricted", encoding="xml"))
                <text-prop name=":testproperty">
                    <text encoding="xml" permissions="prop-restricted">
                        first text
                    </text>
                </text-prop>
    """
    value: Union[str, int, float, bool]
    permissions: str = "prop-default"
    comment: Optional[str] = None
    encoding: Optional[str] = None

    def __post_init__(self) -> None:
        if not any([
            isinstance(self.value, int),
            isinstance(self.value, float) and pd.notna(self.value),  # necessary because isinstance(np.nan, float)
            isinstance(self.value, bool),
            isinstance(self.value, str) and all([
                regex.search(r"\p{L}|\d|_", self.value, flags=regex.UNICODE),
                not bool(regex.search(r"^(none|<NA>|-|n/a)$", self.value, flags=regex.IGNORECASE))
            ])
        ]):
            raise BaseError(f"'{self.value}' is not a valid value for a PropertyElement")
        if self.encoding not in ["utf8", "xml", None]:
            raise BaseError(f"'{self.encoding}' is not a valid encoding for a PropertyElement")
