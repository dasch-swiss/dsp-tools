from __future__ import annotations

from enum import StrEnum


class License: ...


class CC(License, StrEnum):
    """
    Pre-defined and recommended [Creative Commons licenses:](https://creativecommons.org/share-your-work/)

    - `BY`: [Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
    - `BY_SA`: [Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
    - `BY_NC`: [Attribution-NonCommercial 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
    - `BY_NC_SA`: [Attribution-NonCommercial-ShareAlike 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
    - `BY_ND`: [Attribution-NoDerivatives 4.0](https://creativecommons.org/licenses/by-nd/4.0/)
    - `BY_NC_ND`: [Attribution-NonCommercial-NoDerivatives 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)

    Examples:
        ```python
        # adding a Creative Commons license to a file
        resource = resource.add_file(
            filename="images/dog.jpg",
            license=xmllib.LicenseRecommended.CC.BY_NC_ND,
            copyright_holder="Bark University",
            authorship=["Bark McDog"],
        )
        ```
    """

    BY = "http://rdfh.ch/licenses/cc-by-4.0"
    BY_SA = "http://rdfh.ch/licenses/cc-by-sa-4.0"
    BY_NC = "http://rdfh.ch/licenses/cc-by-nc-4.0"
    BY_NC_SA = "http://rdfh.ch/licenses/cc-by-nc-sa-4.0"
    BY_ND = "http://rdfh.ch/licenses/cc-by-nd-4.0"
    BY_NC_ND = "http://rdfh.ch/licenses/cc-by-nc-nd-4.0"


class DSP(License, StrEnum):
    """
    Pre-defined and recommended licenses created and curated by DaSCH:

    - `AI_GENERATED`: AI-Generated Content - Not Protected by Copyright
    - `UNKNOWN`: Unknown License - Ask Copyright Holder for Permission
    - `PUBLIC_DOMAIN`: Public Domain - Not Protected by Copyright

    Examples:
        ```python
        # adding a DSP license to a file
        resource = resource.add_file(
            filename="images/cat.jpg",
            license=xmllib.LicenseRecommended.DSP.PUBLIC_DOMAIN,
            copyright_holder="Meow University",
            authorship=["Kitty Meow"],
        )
        ```
    """

    AI_GENERATED = "http://rdfh.ch/licenses/ai-generated"
    UNKNOWN = "http://rdfh.ch/licenses/unknown"
    PUBLIC_DOMAIN = "http://rdfh.ch/licenses/public-domain"


class LicenseRecommended:
    """
    Recommended licenses:

    - `DSP`: Licenses created and curated by DaSCH, [see `DSP` for details.](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/config-options/#xmllib.models.config_options.DSP)
    - `CC`: Creative Commons licenses, [see `CC` for details.](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/config-options/#xmllib.models.config_options.CC)

    Examples:
        ```python
        # adding a Creative Commons license to a file
        resource = resource.add_file(
            filename="images/cat.jpg",
            license=xmllib.LicenseRecommended.CC.BY,
            copyright_holder="Meow University",
            authorship=["Kitty Meow"],
        )
        ```

        ```python
        # adding a DSP license to a file
        resource = resource.add_file(
            filename="images/dog.jpg",
            license=xmllib.LicenseRecommended.DSP.PUBLIC_DOMAIN,
            copyright_holder="Bark University",
            authorship=["Bark McDog"],
        )
        ```
    """

    CC = CC
    DSP = DSP
