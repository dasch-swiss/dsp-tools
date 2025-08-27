from __future__ import annotations

from enum import Enum
from enum import auto


class DateFormat(Enum):
    """
    Date format options for the [`reformat_date`](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/general-functions/#xmllib.general_functions.reformat_date) function.

    - `YYYY_MM_DD`
    - `DD_MM_YYYY`
    - `MM_DD_YYYY`
    """  # noqa: E501

    YYYY_MM_DD = auto()
    DD_MM_YYYY = auto()
    MM_DD_YYYY = auto()


class Calendar(Enum):
    """
    Calendar options for the [`reformat_date`](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/general-functions/#xmllib.general_functions.reformat_date) function.

    - `GREGORIAN`
    - `JULIAN`
    - `ISLAMIC`
    """  # noqa: E501

    GREGORIAN = "GREGORIAN"
    JULIAN = "JULIAN"
    ISLAMIC = "ISLAMIC"


class Era(Enum):
    """
    Era options for the [`reformat_date`](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/general-functions/#xmllib.general_functions.reformat_date) function.

    - `CE`
    - `BCE`
    - `AD`
    - `BC`
    """  # noqa: E501

    CE = "CE"
    BCE = "BCE"
    AD = "AD"
    BC = "BC"
