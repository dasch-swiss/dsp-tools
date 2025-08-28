from __future__ import annotations

from dsp_tools.xmllib.models.licenses.recommended import License


class LicenseOther:
    """
    Pre-defined licenses that are available in DSP.
    If the user is free to choose a license, we recommend to choose from our [recommended licenses](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/licenses/recommended/).

    - `Public`: [See `Public` for details](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/licenses/other/#xmllib.models.licenses.other.Public).
    - `Various`: [See `Various` for details](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/licenses/other/#xmllib.models.licenses.other.Various).

    Examples:
        ```python
        # adding a BORIS Standard License to a file
        resource = resource.add_file(
            filename="images/cat.jpg",
            license=xmllib.LicenseOther.Various.BORIS_STANDARD,
            copyright_holder="Meow University",
            authorship=["Kitty Meow"],
        )
        ```
    """

    Public: type[Public]
    Various: type[Various]


class Public(License):
    """
    Pre-defined public domain licenses.
    [See the API documentation for details about the licenses.](https://docs.dasch.swiss/latest/DSP-API/01-introduction/legal-info/#license)

    - `CC_0_1_0`: CC0 1.0 Universal
    - `CC_PDM_1_0`: Public Domain Mark 1.0 Universal
    """

    CC_0_1_0 = "http://rdfh.ch/licenses/cc-0-1.0"
    CC_PDM_1_0 = "http://rdfh.ch/licenses/cc-pdm-1.0"


class Various(License):
    """
    A collection of various, pre-defined licenses.
    [See the API documentation for details about the licenses.](https://docs.dasch.swiss/latest/DSP-API/01-introduction/legal-info/#license)

    - `BORIS_STANDARD`: BORIS Standard License
    - `FRANCE_OUVERTE`: LICENCE OUVERTE 2.0
    """

    BORIS_STANDARD = "http://rdfh.ch/licenses/boris"
    FRANCE_OUVERTE = "http://rdfh.ch/licenses/open-licence-2.0"


LicenseOther.Public = Public
LicenseOther.Various = Various
