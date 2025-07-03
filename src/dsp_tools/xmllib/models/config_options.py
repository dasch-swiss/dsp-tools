from __future__ import annotations

from enum import Enum
from enum import auto


class Permissions(Enum):
    """
    Options of permissions for resources and values:

    - `PROJECT_SPECIFIC_PERMISSIONS`: the permissions defined on project level will be applied
    - `PUBLIC`: the resource/value is visible for everyone
    - `PRIVATE`: the resource/value is only visible for project members
    - `LIMITED_VIEW`: the resource/value is visible for everyone,
      but images are blurred/watermarked for non-project members

    Deprecated terms:

    - `OPEN`: use `PUBLIC` instead
    - `RESTRICTED`: use `PRIVATE` instead
    - `RESTRICTED_VIEW`: use `LIMITED_VIEW` instead

    Examples:
        ```python
        resource = xmllib.Resource.create_new(
            res_id="ID",
            restype=":ResourceType",
            label="label",
            permissions=xmllib.Permissions.PRIVATE,
        )
        ```
    """

    PROJECT_SPECIFIC_PERMISSIONS = ""
    PUBLIC = "public"
    PRIVATE = "private"
    LIMITED_VIEW = "limited_view"

    # Deprecated terminology
    OPEN = "open"
    RESTRICTED = "restricted"
    RESTRICTED_VIEW = "restricted-view"


class NewlineReplacement(Enum):
    """
    Options how to deal with `\\n` inside rich text values.

    - `NONE`: don't modify the rich text (`\\n` will be lost, because it is meaningless in an XML file)
    - `PARAGRAPH`: replace `Start\\nEnd` with `<p>Start</p><p>End</p>`
    - `LINEBREAK`: replace `Start\\nEnd` with `Start<br/>End`

    Examples:
        ```python
        # setting the replacement options for newlines
        resource = resource.add_richtext(
            prop_name=":propName",
            value="Start\\n\\nEnd",
            newline_replacement=xmllib.NewlineReplacement.PARAGRAPH
        )
        ```
    """

    NONE = auto()
    PARAGRAPH = auto()
    LINEBREAK = auto()


class DateFormat(Enum):
    """
    Date format options for the [`reformat_date`](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/helpers/#xmllib.helpers.reformat_date) function.

    - `YYYY_MM_DD`
    - `DD_MM_YYYY`
    - `MM_DD_YYYY`
    """  # noqa: E501

    YYYY_MM_DD = auto()
    DD_MM_YYYY = auto()
    MM_DD_YYYY = auto()


class Calendar(Enum):
    """
    Calendar options for the [`reformat_date`](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/helpers/#xmllib.helpers.reformat_date) function.

    - `GREGORIAN`
    - `JULIAN`
    - `ISLAMIC`
    """  # noqa: E501

    GREGORIAN = "GREGORIAN"
    JULIAN = "JULIAN"
    ISLAMIC = "ISLAMIC"


class Era(Enum):
    """
    Era options for the [`reformat_date`](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/helpers/#xmllib.helpers.reformat_date) function.

    - `CE`
    - `BCE`
    - `AD`
    - `BC`
    """  # noqa: E501

    CE = "CE"
    BCE = "BCE"
    AD = "AD"
    BC = "BC"
