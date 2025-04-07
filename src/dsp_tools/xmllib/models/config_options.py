from enum import Enum
from enum import StrEnum
from enum import auto
from typing import Type


class Permissions(Enum):
    """
    Options of permissions for resources and values:

    - `PROJECT_SPECIFIC_PERMISSIONS`: the permissions defined on project level will be applied
    - `OPEN`: the resource/value is visible for everyone
    - `RESTRICTED`: the resource/value is only visible for project members
    - `RESTRICTED_VIEW`: the resource/value is visible for everyone,
      but images are blurred/watermarked for non-project members

    Examples:
        ```python
        resource = xmllib.Resource.create_new(
            res_id="ID",
            restype=":ResourceType",
            label="label",
            permissions=xmllib.Permissions.RESTRICTED,
        )
        ```
    """

    PROJECT_SPECIFIC_PERMISSIONS = ""
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


class CC(StrEnum):
    """
    Pre-defined and recommended licences:

    - `CC_BY`: [Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
    - `CC_BY_SA`: [Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
    - `CC_BY_NC`: [Attribution-NonCommercial 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
    - `CC_BY_NC_SA`: [Attribution-NonCommercial-ShareAlike 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
    - `CC_BY_ND`: [Attribution-NoDerivatives 4.0](https://creativecommons.org/licenses/by-nd/4.0/)
    - `CC_BY_NC_ND`: [Attribution-NonCommercial-NoDerivatives 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)

    Examples:
        ```python
        # adding a creative commons license to a file
        resource = resource.add_file(
            filename="images/cat.jpg",
            license=xmllib.LicenceRecommended.CC.BY,
            copyright_holder="Meow University",
            authorship=["Kitty Meow"],
        )
        ```
    """

    BY = "http://rdfh.ch/licenses/cc-by-4.0"
    BY_SA = "http://rdfh.ch/licenses/cc-by-sa-4.0"
    BY_NC = "http://rdfh.ch/licenses/cc-by-nc-4.0"
    BY_NC_SA = "http://rdfh.ch/licenses/cc-by-nc-sa-4.0"
    BY_ND = "http://rdfh.ch/licenses/cc-by-nd-4.0"
    BY_NC_ND = "http://rdfh.ch/licenses/cc-by-nc-nd-4.0"


class DSP(StrEnum):
    """
    Pre-defined and recommended licences:

    - `AI_GENERATED`: AI-Generated Content - Not Protected by Copyright
    - `UNKNOWN`: Unknown License - Ask Copyright Holder for Permission
    - `PUBLIC_DOMAIN`: Public Domain - Not Protected by Copyright

    Examples:
        ```python
        # adding a DSP license to a file
        resource = resource.add_file(
            filename="images/dog.jpg",
            license=xmllib.LicenceRecommended.DSP.PUBLIC_DOMAIN,
            copyright_holder="Bark University",
            authorship=["Bark McDog"],
        )
        ```
    """

    AI_GENERATED = "http://rdfh.ch/licenses/ai-generated"
    UNKNOWN = "http://rdfh.ch/licenses/unknown"
    PUBLIC_DOMAIN = "http://rdfh.ch/licenses/public-domain"


class LicenceRecommended:
    """
    Recommended licences:

    - `DSP`: Licences created and curated by DaSCH, [see `DSP` for the options.](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/config-options/#xmllib.models.config_options.DSP)
    - `CC`: Creative Commons licences, [see `CC` for the options.](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/config-options/#xmllib.models.config_options.CC)

    Examples:
        ```python
        # adding a creative commons license to a file
        resource = resource.add_file(
            filename="images/cat.jpg",
            license=xmllib.LicenceRecommended.CC.BY,
            copyright_holder="Meow University",
            authorship=["Kitty Meow"],
        )
        ```

        ```python
        # adding a DSP license to a file
        resource = resource.add_file(
            filename="images/dog.jpg",
            license=xmllib.LicenceRecommended.DSP.PUBLIC_DOMAIN,
            copyright_holder="Bark University",
            authorship=["Bark McDog"],
        )
        ```
    """

    CC: Type[CC] = CC
    DSP: Type[DSP] = DSP
