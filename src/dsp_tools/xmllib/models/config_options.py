from enum import Enum
from enum import auto


class Permissions(Enum):
    """
    Options of permissions for resources and values:

    - `PROJECT_SPECIFIC_PERMISSIONS`: the permissions defined on project level will be applied
    - `OPEN`: the resource/value is visible for everyone
    - `RESTRICTED`: the resource/value is only visible for project members
    - `RESTRICTED_VIEW`: the resource/value is visible for everyone,
      but images are blurred/watermarked for non-project members
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
    """

    NONE = auto()
    PARAGRAPH = auto()
    LINEBREAK = auto()


class PreDefinedLicenses(Enum):
    """
    Options for the pre-defined licenses.

    - `CC_BY` [Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
    - `CC_BY_SA` [Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/)
    - `CC_BY_NC` [Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/)
    - `CC_BY_NC_SA` [Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/)
    - `CC_BY_ND` [Attribution-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nd/4.0/)
    - `CC_BY_NC_ND` [Attribution-NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0/)
    - `CC0` [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
    - `UNKNOWN` [Copyright Not Evaluated](http://rightsstatements.org/vocab/CNE/1.0/)
    """

    CC_BY = "CC-BY"
    CC_BY_SA = "CC-BY-SA"
    CC_BY_NC = "CC-BY-NC"
    CC_BY_NC_SA = "CC-BY-NC-SA"
    CC_BY_ND = "CC-BY-ND"
    CC_BY_NC_ND = "CC-BY-NC-ND"
    CC0 = "CC0"
    UNKNOWN = "unknown"
