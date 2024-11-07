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
